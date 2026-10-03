"""The classifier architecture, its checkpoint contract, and inference transforms."""

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("torchvision")

from PIL import Image

from backend.pipelines.CNN_classifier import CheckpointMissing, load_model, predict_image
from training.configs.datasets.cnn_DataLoader import eval_transform, train_transform
from training.configs.models.CNN_model import Model


@pytest.fixture
def checkpoint(tmp_path):
    """A small trained-shaped checkpoint written the way the trainer writes it."""
    model = Model(output_head=10, resnet50_use=False)
    path = tmp_path / "classifier.pth"

    torch.save(
        {
            "state_dict": model.state_dict(),
            "config": model.config,
            "class_names": [
                "Tomato___Bacterial_spot", "Tomato___Early_blight",
                "Tomato___Late_blight", "Tomato___Leaf_Mold",
                "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites",
                "Tomato___Target_Spot", "Tomato___Yellow_Leaf_Curl_Virus",
                "Tomato___mosaic_virus", "Tomato___healthy",
            ],
        },
        path,
    )
    load_model.cache_clear()
    return path


def test_forward_returns_logits_per_class():
    model = Model(output_head=10, resnet50_use=False)
    output = model(torch.randn(2, 3, 224, 224))

    assert output.shape == (2, 10)
    # Raw logits: the training loop applies CrossEntropyLoss, which softmaxes.
    assert not torch.allclose(output.sum(dim=1), torch.ones(2))


def test_resnet_backbone_matches_the_same_contract():
    model = Model(output_head=10, resnet50_use=True, pretrained=False)

    assert model(torch.randn(1, 3, 224, 224)).shape == (1, 10)


def test_config_exposes_every_checkpointed_hyperparameter():
    """The trainer reads these attributes off the model when saving."""
    model = Model(output_head=10)

    for key in ("output_head", "out1", "out2", "hidden1", "hidden2", "hidden3",
                "dropout1", "dropout2", "dropout3", "resnet50_use"):
        assert key in model.config
        assert hasattr(model, key)


def test_checkpoint_round_trip_preserves_non_default_shapes(tmp_path):
    """load_model used to pass only output_head, so any other hyperparameter
    produced a state-dict shape mismatch."""
    model = Model(output_head=4, hidden1=128, hidden2=64, hidden3=32, resnet50_use=False)
    path = tmp_path / "custom.pth"
    torch.save({"state_dict": model.state_dict(), "config": model.config,
                "class_names": ["a", "b", "c", "d"]}, path)

    load_model.cache_clear()
    restored, class_names = load_model(path)

    assert restored.hidden1 == 128
    assert restored.output_head == 4
    assert class_names == ["a", "b", "c", "d"]


def test_missing_checkpoint_names_the_training_command(tmp_path):
    load_model.cache_clear()

    with pytest.raises(CheckpointMissing) as excinfo:
        load_model(tmp_path / "absent.pth")

    assert "train_cnn" in str(excinfo.value)


def test_prediction_returns_named_classes(checkpoint, tmp_path):
    """Predictions used to be bare integers no caller could interpret."""
    image_path = tmp_path / "leaf.png"
    Image.new("RGB", (300, 300), (34, 139, 34)).save(image_path)

    predictions = predict_image(image_path, checkpoint, topk=3)

    assert len(predictions) == 3
    assert all(p["class_name"].startswith("Tomato___") for p in predictions)
    # Ranked by confidence, descending.
    assert predictions == sorted(predictions, key=lambda p: -p["confidence"])


def test_eval_transform_is_deterministic():
    """Inference reused the augmentation chain, so the same leaf scored
    differently on every call."""
    image = Image.new("RGB", (300, 300), (120, 200, 80))

    assert torch.equal(eval_transform(image), eval_transform(image))


def test_train_transform_still_augments():
    """Augmentation must remain in place for training."""
    image = Image.new("RGB", (300, 300), (120, 200, 80))

    assert not torch.equal(train_transform(image), train_transform(image))
