"""Inference for the tomato leaf-disease classifier.

Loads a checkpoint written by ``training/scripts/train_cnn.py`` and classifies
single images or whole folders. The model is cached per checkpoint path so a
server can call ``predict_image`` repeatedly without reloading weights.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from functools import lru_cache
from pathlib import Path

import torch
from PIL import Image

from training.configs.datasets.cnn_DataLoader import eval_transform
from training.configs.models.CNN_model import Model

logger = logging.getLogger(__name__)

DEFAULT_CHECKPOINT = Path("models/plant_CNN_classifier_model.pth")

# Hyperparameters the checkpoint stores for rebuilding the network.
_CONFIG_KEYS = (
    "output_head", "out1", "out2", "hidden1", "hidden2", "hidden3",
    "dropout1", "dropout2", "dropout3", "resnet50_use",
)


class CheckpointMissing(FileNotFoundError):
    """Raised when no trained classifier is available."""


def _device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@lru_cache(maxsize=2)
def load_model(model_path: str | Path = DEFAULT_CHECKPOINT) -> tuple[Model, list[str]]:
    """Load a checkpoint and return (model, class_names).

    Args:
        model_path: Path to a checkpoint produced by the training script.

    Returns:
        The model in eval mode, and the class names in label-index order.

    Raises:
        CheckpointMissing: If no checkpoint exists at `model_path`.
    """
    path = Path(model_path)
    if not path.is_file():
        raise CheckpointMissing(
            f"No classifier checkpoint at {path}. Train one with "
            "`python -m training.scripts.train_cnn`, or set "
            "PLANTATIO_CNN_CHECKPOINT to an existing file."
        )

    device = _device()
    # weights_only defaults to True from PyTorch 2.6 and would reject the
    # config dict this checkpoint stores alongside the tensors.
    checkpoint = torch.load(path, map_location=device, weights_only=False)

    config = checkpoint.get("config", {})
    # Every stored hyperparameter is passed through; using only output_head
    # produced a shape mismatch for any non-default checkpoint.
    kwargs = {key: config[key] for key in _CONFIG_KEYS if key in config}

    model = Model(**kwargs, pretrained=False)
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device).eval()

    class_names = checkpoint.get("class_names") or [
        str(index) for index in range(model.output_head)
    ]

    logger.info("Loaded classifier from %s with %d classes.", path, len(class_names))
    return model, class_names


def predict_image(image: Image.Image | str | Path, model_path: str | Path = DEFAULT_CHECKPOINT,
                  topk: int = 3) -> list[dict]:
    """Classify one image.

    Args:
        image: A PIL image, or a path to one.
        model_path: Checkpoint to use.
        topk: How many ranked predictions to return.

    Returns:
        Ranked predictions, each ``{"class_id", "class_name", "confidence"}``.
    """
    model, class_names = load_model(model_path)

    pil_image = image if isinstance(image, Image.Image) else Image.open(image)
    tensor = eval_transform(pil_image.convert("RGB")).unsqueeze(0).to(_device())

    with torch.no_grad():
        probabilities = torch.softmax(model(tensor), dim=1)[0]

    count = min(topk, probabilities.numel())
    scores, indices = torch.topk(probabilities, count)

    return [
        {
            "class_id": int(index),
            "class_name": class_names[int(index)] if int(index) < len(class_names) else str(int(index)),
            "confidence": float(score),
        }
        for score, index in zip(scores, indices)
    ]


def predict_folder(folder_path: str | Path, model_path: str | Path = DEFAULT_CHECKPOINT,
                   topk: int = 3) -> dict[str, list[dict]]:
    """Classify every image in a folder, keyed by filename."""
    folder = Path(folder_path)
    suffixes = {".jpg", ".jpeg", ".png"}

    return {
        entry.name: predict_image(entry, model_path, topk)
        for entry in sorted(folder.iterdir())
        if entry.suffix.lower() in suffixes
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

    parser = argparse.ArgumentParser(description="Classify tomato leaf images")
    parser.add_argument(
        "--model",
        default=os.getenv("PLANTATIO_CNN_CHECKPOINT", str(DEFAULT_CHECKPOINT)),
    )
    parser.add_argument("--image", help="Path to a single image")
    parser.add_argument("--folder", help="Path to a folder of images")
    parser.add_argument("--topk", type=int, default=3)
    args = parser.parse_args()

    if not args.image and not args.folder:
        parser.error("provide --image or --folder")

    if args.image:
        result = predict_image(args.image, args.model, args.topk)
    else:
        result = predict_folder(args.folder, args.model, args.topk)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
