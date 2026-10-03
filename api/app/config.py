"""Central runtime configuration for the Plantatio API.

Every credential and tunable the backend needs is read from the environment
here, so no secret is written into source. Values are resolved once at import
and exposed through the module-level ``settings`` singleton.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    """Populate os.environ from a repo-root .env file, if one exists.

    Uses python-dotenv when available and falls back to a minimal parser so the
    API still boots in environments where the package is absent.
    """
    env_path = REPO_ROOT / ".env"
    if not env_path.is_file():
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
        return
    except ImportError:
        pass

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_bool(name: str, default: bool = False) -> bool:
    raw = _env(name)
    if not raw:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str) -> list[str]:
    return [item.strip() for item in _env(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Neo4jSettings:
    """Connection details for the knowledge graph."""

    uri: str
    user: str
    password: str
    database: str

    @property
    def configured(self) -> bool:
        """True when enough detail is present to attempt a connection."""
        return bool(self.uri and self.user and self.password)


@dataclass(frozen=True)
class LLMSettings:
    """Which language model backs the agent, and how it is loaded."""

    model_id: str
    device_map: str
    dtype: str
    max_new_tokens: int
    trust_remote_code: bool


@dataclass(frozen=True)
class VisionSettings:
    """Checkpoint and model ids for the CNN and the satellite VLM."""

    cnn_checkpoint: Path
    vlm_model_id: str
    vlm_provider: str
    hf_token: str


@dataclass(frozen=True)
class Settings:
    """Everything the API reads from the environment."""

    database_url: str
    cors_origins: list[str]
    neo4j: Neo4jSettings
    llm: LLMSettings
    vision: VisionSettings
    demo_mode: bool = field(default=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build the settings singleton from the current environment."""
    _load_dotenv()

    return Settings(
        database_url=_env("DATABASE_URL", f"sqlite:///{REPO_ROOT / 'plantatio.db'}"),
        cors_origins=_env_list(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://localhost:8080,"
            "http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8080",
        ),
        neo4j=Neo4jSettings(
            uri=_env("NEO4J_URI"),
            user=_env("NEO4J_USER"),
            password=_env("NEO4J_PASSWORD"),
            database=_env("NEO4J_DATABASE", "neo4j"),
        ),
        llm=LLMSettings(
            model_id=_env("PLANTATIO_LLM_MODEL_ID", "nvidia/Llama-3.1-8B-Instruct-NVFP4"),
            device_map=_env("PLANTATIO_LLM_DEVICE", "auto"),
            dtype=_env("PLANTATIO_LLM_DTYPE", "auto"),
            max_new_tokens=int(_env("PLANTATIO_LLM_MAX_NEW_TOKENS", "512")),
            trust_remote_code=_env_bool("PLANTATIO_LLM_TRUST_REMOTE_CODE", False),
        ),
        vision=VisionSettings(
            cnn_checkpoint=Path(
                _env("PLANTATIO_CNN_CHECKPOINT", str(REPO_ROOT / "models" / "plant_CNN_classifier_model.pth"))
            ),
            vlm_model_id=_env("PLANTATIO_VLM_MODEL_ID", "Qwen/Qwen2.5-VL-7B-Instruct"),
            vlm_provider=_env("PLANTATIO_VLM_PROVIDER", "auto"),
            hf_token=_env("HF_TOKEN"),
        ),
        demo_mode=_env_bool("PLANTATIO_DEMO_MODE", False),
    )


settings = get_settings()
