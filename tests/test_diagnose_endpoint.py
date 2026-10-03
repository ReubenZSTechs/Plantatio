"""The leaf-diagnosis endpoint, including its behaviour with no trained model."""

import io

import pytest

pytest.importorskip("torch")
pytest.importorskip("torchvision")

from PIL import Image


def _leaf_bytes() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (300, 300), (60, 140, 60)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_returns_503_and_points_at_training_when_untrained(client, monkeypatch, tmp_path):
    """No checkpoint must mean an honest 503, never a fabricated diagnosis."""
    monkeypatch.setenv("PLANTATIO_CNN_CHECKPOINT", str(tmp_path / "absent.pth"))

    from app import config
    config.get_settings.cache_clear()
    monkeypatch.setattr(config, "settings", config.get_settings())

    response = client.post(
        "/api/plants/1/diagnose",
        files={"image": ("leaf.png", _leaf_bytes(), "image/png")},
    )

    assert response.status_code == 503
    detail = response.json()["detail"]
    assert "train_cnn" in detail
    config.get_settings.cache_clear()


def test_unknown_plant_is_404(client):
    response = client.post(
        "/api/plants/9999/diagnose",
        files={"image": ("leaf.png", _leaf_bytes(), "image/png")},
    )

    assert response.status_code == 404


def test_empty_upload_is_rejected(client):
    response = client.post(
        "/api/plants/1/diagnose",
        files={"image": ("leaf.png", b"", "image/png")},
    )

    assert response.status_code == 422


def test_diagnosis_updates_plant_health(client, monkeypatch, tmp_path):
    """A successful scan records the result and moves the health score."""
    import torch

    from backend.pipelines.CNN_classifier import load_model
    from training.configs.models.CNN_model import Model

    model = Model(output_head=2, resnet50_use=False)
    checkpoint = tmp_path / "classifier.pth"
    torch.save(
        {
            "state_dict": model.state_dict(),
            "config": model.config,
            "class_names": ["Tomato___Late_blight", "Tomato___healthy"],
        },
        checkpoint,
    )
    load_model.cache_clear()

    monkeypatch.setenv("PLANTATIO_CNN_CHECKPOINT", str(checkpoint))
    from app import config
    config.get_settings.cache_clear()
    monkeypatch.setattr(config, "settings", config.get_settings())

    response = client.post(
        "/api/plants/1/diagnose",
        files={"image": ("leaf.png", _leaf_bytes(), "image/png")},
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["topClass"] in {"Tomato___Late_blight", "Tomato___healthy"}
    assert body["label"] in {"Late blight", "Healthy"}
    assert 0.0 <= body["confidence"] <= 1.0
    assert isinstance(body["isDefective"], bool)
    assert body["summary"]

    # The scan is reflected on the plant itself.
    plant = client.get("/api/plants/1").json()
    assert plant["health"] == pytest.approx(body["healthScore"], abs=0.1)
    assert any(event["event"] == "Leaf scan" for event in plant["timeline"])

    config.get_settings.cache_clear()
    load_model.cache_clear()
