"""Plant-health diagnosis from a leaf photograph.

Wraps the CNN classifier with the interpretation the API needs: which classes
count as healthy, how confident the model is, and a plain-language summary a
grower can act on. When no trained checkpoint is present this reports that
clearly rather than guessing a diagnosis.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# PlantVillage class names contain "healthy" for the unaffected class.
_HEALTHY_MARKERS = ("healthy", "no_disease")


class DiagnosisUnavailable(RuntimeError):
    """Raised when no classifier is available to answer with."""


@dataclass
class Diagnosis:
    """A ranked classification plus the verdict derived from it."""

    predictions: list[dict] = field(default_factory=list)
    top_class: str = ""
    confidence: float = 0.0
    is_defective: bool = False
    health_score: float = 0.0
    summary: str = ""

    def as_dict(self) -> dict:
        return {
            "predictions": self.predictions,
            "top_class": self.top_class,
            "confidence": self.confidence,
            "is_defective": self.is_defective,
            "health_score": self.health_score,
            "summary": self.summary,
        }


def humanize_class(class_name: str) -> str:
    """Turn a dataset label into something readable.

    "Tomato___Late_blight" becomes "Late blight".
    """
    label = class_name.split("___")[-1] if "___" in class_name else class_name
    return label.replace("_", " ").strip().capitalize()


def is_healthy(class_name: str) -> bool:
    """True when a class name denotes an unaffected plant."""
    lowered = class_name.lower()
    return any(marker in lowered for marker in _HEALTHY_MARKERS)


def _summarize(top_class: str, confidence: float, defective: bool) -> str:
    """Write the grower-facing sentence for a diagnosis."""
    label = humanize_class(top_class)
    percent = round(confidence * 100)

    if not defective:
        return f"No disease detected ({percent}% confidence). Keep to the current care plan."

    if confidence < 0.5:
        return (
            f"Possible {label.lower()}, but confidence is low ({percent}%). "
            "Take a closer, well-lit photo of the affected leaf to confirm."
        )

    return (
        f"{label} detected with {percent}% confidence. "
        "Remove affected foliage and review the treatment guidance below."
    )


def diagnose_image(image, checkpoint: str | Path | None = None, topk: int = 3) -> Diagnosis:
    """Classify a leaf image and interpret the result.

    Args:
        image: A PIL image or a path to one.
        checkpoint: Override the configured checkpoint path.
        topk: How many ranked predictions to include.

    Returns:
        A populated `Diagnosis`.

    Raises:
        DiagnosisUnavailable: If no checkpoint exists, or torch is missing.
    """
    try:
        from backend.pipelines.CNN_classifier import CheckpointMissing, predict_image
    except ImportError as exc:
        raise DiagnosisUnavailable(
            "torch and torchvision are required for leaf diagnosis. "
            "Install them with `pip install -r api/requirements.txt`."
        ) from exc

    from app.config import settings

    path = Path(checkpoint) if checkpoint else settings.vision.cnn_checkpoint

    try:
        predictions = predict_image(image, path, topk=topk)
    except CheckpointMissing as exc:
        raise DiagnosisUnavailable(str(exc)) from exc

    if not predictions:
        raise DiagnosisUnavailable("The classifier returned no predictions.")

    best = predictions[0]
    defective = not is_healthy(best["class_name"])

    # Health reads as the probability the plant is unaffected.
    healthy_probability = sum(
        item["confidence"] for item in predictions if is_healthy(item["class_name"])
    )
    health_score = round(
        (healthy_probability if defective else best["confidence"]) * 100, 1
    )

    return Diagnosis(
        predictions=[
            {**item, "label": humanize_class(item["class_name"])} for item in predictions
        ],
        top_class=best["class_name"],
        confidence=round(best["confidence"], 4),
        is_defective=defective,
        health_score=health_score,
        summary=_summarize(best["class_name"], best["confidence"], defective),
    )
