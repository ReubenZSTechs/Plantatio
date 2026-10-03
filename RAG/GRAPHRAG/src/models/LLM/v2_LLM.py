"""Shared language-model backend for the Plantatio agent.

One HuggingFace causal model serves every role in the pipeline — query
decomposition, text-to-Cypher translation, reasoning and answer generation —
so the weights are loaded once per process and reused. Loading is deferred
until the first ``generate`` call, which keeps importing the API cheap.

The model is chosen with PLANTATIO_LLM_MODEL_ID. The default is an
NVFP4-quantised checkpoint whose kernels require NVIDIA Blackwell tensor
cores; on other hardware, point that variable at a model the machine can run.
"""

from __future__ import annotations

import contextlib
import logging
import os
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "nvidia/Llama-3.1-8B-Instruct-NVFP4"


class LLMUnavailable(RuntimeError):
    """Raised when the configured model cannot be loaded on this machine."""


def _inference_mode():
    """Disable gradient tracking when torch is present.

    Falls back to a no-op so an injected stub model can drive generation
    without torch installed.
    """
    try:
        import torch

        return torch.no_grad()
    except ImportError:
        return contextlib.nullcontext()


@dataclass(frozen=True)
class GenerationProfile:
    """Decoding settings for one role in the pipeline."""

    max_new_tokens: int
    temperature: float


# Each role gets its own decoding budget while sharing one set of weights.
PROFILES: dict[str, GenerationProfile] = {
    "sub_question": GenerationProfile(max_new_tokens=256, temperature=0.3),
    "text_to_cypher": GenerationProfile(max_new_tokens=512, temperature=0.1),
    "reasoning": GenerationProfile(max_new_tokens=1024, temperature=0.6),
    "answer": GenerationProfile(max_new_tokens=512, temperature=0.5),
}

DEFAULT_PROFILE = GenerationProfile(max_new_tokens=512, temperature=0.4)


class LLMManager:
    """Lazily-loaded, process-wide text generator.

    ``TextToCypherPipeline`` and the LangGraph nodes both construct this; the
    underlying model is shared through a class-level cache so repeated
    instantiation is free.
    """

    _model = None
    _tokenizer = None
    _load_lock = threading.Lock()

    def __init__(self, model_id: str | None = None, role: str = "text_to_cypher"):
        self.model_id = model_id or os.getenv("PLANTATIO_LLM_MODEL_ID", DEFAULT_MODEL_ID)
        self.role = role
        self.profile = PROFILES.get(role, DEFAULT_PROFILE)

    @classmethod
    def reset(cls) -> None:
        """Drop the cached model. Used by tests and on application shutdown."""
        with cls._load_lock:
            cls._model = None
            cls._tokenizer = None

    @classmethod
    def inject(cls, model, tokenizer) -> None:
        """Install a pre-built model and tokenizer.

        Lets tests exercise the full pipeline with a stub instead of
        downloading several gigabytes of weights.
        """
        with cls._load_lock:
            cls._model = model
            cls._tokenizer = tokenizer

    def _ensure_loaded(self) -> None:
        """Load the weights on first use, raising a clear error if impossible."""
        if LLMManager._model is not None:
            return

        with LLMManager._load_lock:
            if LLMManager._model is not None:
                return

            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
            except ImportError as exc:
                raise LLMUnavailable(
                    "transformers and torch are required to run the agent. "
                    "Install them with `pip install -r api/requirements.txt`."
                ) from exc

            dtype_name = os.getenv("PLANTATIO_LLM_DTYPE", "auto")
            dtype = getattr(torch, dtype_name, None) if dtype_name != "auto" else "auto"

            logger.info("Loading %s (this happens once per process).", self.model_id)

            try:
                tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    dtype=dtype,
                    device_map=os.getenv("PLANTATIO_LLM_DEVICE", "auto"),
                    trust_remote_code=os.getenv(
                        "PLANTATIO_LLM_TRUST_REMOTE_CODE", ""
                    ).lower() in {"1", "true", "yes"},
                )
            except Exception as exc:
                raise LLMUnavailable(
                    f"Could not load {self.model_id!r}. NVFP4 checkpoints need "
                    "NVIDIA Blackwell tensor cores (RTX 50-series or B200) and a "
                    "recent transformers build. Set PLANTATIO_LLM_MODEL_ID to a "
                    f"model this machine can run. Original error: {exc}"
                ) from exc

            if tokenizer.pad_token_id is None:
                tokenizer.pad_token = tokenizer.eos_token

            LLMManager._model = model
            LLMManager._tokenizer = tokenizer
            logger.info("Model ready.")

    def generate(self, prompt: str, max_new_tokens: int | None = None,
                 temperature: float | None = None) -> str:
        """Return the model's completion for `prompt`, without echoing it.

        Args:
            prompt: The fully-rendered instruction to send to the model.
            max_new_tokens: Overrides this role's token budget.
            temperature: Overrides this role's sampling temperature.

        Raises:
            LLMUnavailable: If the configured model cannot be loaded.
        """
        self._ensure_loaded()

        tokenizer = LLMManager._tokenizer
        model = LLMManager._model

        messages = [{"role": "user", "content": prompt}]
        if hasattr(tokenizer, "apply_chat_template") and getattr(
            tokenizer, "chat_template", None
        ):
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            text = prompt

        inputs = tokenizer(text, return_tensors="pt")
        if hasattr(model, "device"):
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

        resolved_temperature = (
            self.profile.temperature if temperature is None else temperature
        )

        with _inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens or self.profile.max_new_tokens,
                temperature=resolved_temperature,
                do_sample=resolved_temperature > 0,
                pad_token_id=tokenizer.pad_token_id,
            )

        # Decode only the continuation so callers never have to strip the prompt.
        generated = output[0][inputs["input_ids"].shape[-1]:]
        return tokenizer.decode(generated, skip_special_tokens=True).strip()

    def invoke(self, prompt: str) -> str:
        """Alias for `generate`, matching the LangChain runnable interface."""
        return self.generate(prompt)


def get_llm(role: str = "text_to_cypher") -> LLMManager:
    """Return a manager bound to `role`'s decoding profile."""
    return LLMManager(role=role)
