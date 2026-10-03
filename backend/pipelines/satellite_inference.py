"""Satellite land-cover and restoration analysis via a vision-language model.

One image in, six ecological metrics out. Used by the B2B satellite endpoint to
compare a baseline against a current image of the same site.
"""

from __future__ import annotations

import argparse
import base64
import json
import logging
import mimetypes
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

RESPONSE_SCHEMA = """{
  "vegetation_density": "low|medium|high",
  "canopy_cover": number between 0 and 1,
  "est_biomass": number between 0 and 1,
  "carbon_EQ": number between 0 and 1,
  "restoration_quality": "poor|moderate|strong",
  "confidence": number between 0 and 1
}"""


class VLMUnavailable(RuntimeError):
    """Raised when the vision model cannot be reached."""


@lru_cache(maxsize=1)
def _client():
    """Return a cached Inference API client.

    Built on first use rather than at import, so a missing token cannot stop
    the API from starting.
    """
    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise VLMUnavailable(
            "huggingface_hub is required for satellite analysis. "
            "Install it with `pip install -r api/requirements.txt`."
        ) from exc

    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        raise VLMUnavailable("HF_TOKEN is not set (see .env.example).")

    return InferenceClient(
        provider=os.getenv("PLANTATIO_VLM_PROVIDER", "auto"),
        api_key=token,
    )


def build_prompt(class_hint: Optional[str] = None) -> str:
    """Compose the analysis instruction, optionally hinting at the land cover."""
    prompt = f"""You are an expert satellite image analyst.

Analyse the image and estimate its ecological characteristics. Normalise every
numeric value to the 0-1 range so results are comparable across images.

Return ONLY valid JSON in this schema:

{RESPONSE_SCHEMA}
"""

    if class_hint:
        prompt += f"\nContext: this image is described as '{class_hint}'.\n"

    return prompt


def _as_data_url(image_path: str | Path) -> str:
    """Encode an image as a data URL for the chat-completions image part."""
    path = Path(image_path)
    media_type = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def extract_json(text: str) -> Optional[dict]:
    """Pull the first JSON object out of a model response.

    Returns None when nothing parseable is present.
    """
    if not text:
        return None

    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        logger.warning("No JSON object found in model output.")
        return None

    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        logger.warning("Model output was not valid JSON: %.200s", text)
        return None


def run_vlm(image_path: str | Path, class_hint: Optional[str] = None) -> str:
    """Send one image to the vision model and return its raw reply.

    The image travels as a base64 `image_url` part inside `content`. The
    previous implementation passed a PIL object under a sibling `"image"` key,
    which is neither JSON-serialisable nor part of the chat schema, so the
    request never left the process.
    """
    model_id = os.getenv("PLANTATIO_VLM_MODEL_ID", DEFAULT_MODEL_ID)

    response = _client().chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_prompt(class_hint)},
                    {"type": "image_url", "image_url": {"url": _as_data_url(image_path)}},
                ],
            }
        ],
        max_tokens=512,
    )

    # `message` is a dataclass, so attribute access rather than subscripting.
    return response.choices[0].message.content or ""


def analyze(image_path: str | Path, class_hint: Optional[str] = None) -> Optional[dict]:
    """Analyse one image and return the parsed metrics."""
    return extract_json(run_vlm(image_path, class_hint))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

    parser = argparse.ArgumentParser(description="Satellite VLM inference")
    parser.add_argument("--image", required=True, help="Path to the image")
    parser.add_argument("--class-hint", dest="class_hint", default=None)
    args = parser.parse_args()

    parsed = analyze(args.image, args.class_hint)

    if parsed is None:
        logger.error("Could not parse a result for %s.", args.image)
        raise SystemExit(1)

    print(json.dumps(parsed, indent=2))


if __name__ == "__main__":
    main()
