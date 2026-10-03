"""Train the tomato leaf-disease classifier.

Reads the CSV index built by `training/preprocessing/build_dataset_CNN.py`,
trains with class-weighted cross-entropy and early stopping, writes evaluation
plots, and saves a checkpoint carrying both the architecture hyperparameters
and the class names needed at inference.

Usage:
    python -m training.scripts.train_cnn
"""

import logging
import os
from pathlib import Path

import matplotlib
import numpy as np
import seaborn as sns
import torch
from torch.utils.data import DataLoader, random_split
from tqdm import tqdm

matplotlib.use("Agg")  # Plots are written to disk; never block on a window.
import matplotlib.pyplot as plt

from training.configs.datasets.cnn_DataLoader import (
    TomatoDataset, eval_transform, train_transform,
)
from training.configs.models.CNN_model import Model

from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, roc_auc_score, precision_recall_curve, average_precision_score
from sklearn.preprocessing import label_binarize
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
logger = logging.getLogger(__name__)

CONFIG = {
    'BATCH_SIZE': 32,
    'DEVICE': 'cuda' if torch.cuda.is_available() else 'cpu',
    'EPOCH': 30,
    'DATASET_PATH': os.getenv(
        "CNN_DATASET_CSV", 'training/datasets/formatted/directory_dataset.csv'
    ),
    'PATIENCE': 3,
    'SEED': 42,
    'MODEL_OUT': Path(os.getenv(
        "PLANTATIO_CNN_CHECKPOINT", "models/plant_CNN_classifier_model.pth"
    )),
    'PLOT_DIR': Path("training/datasets/evaluation"),
}

# A fixed seed keeps the train/val/test split reproducible across runs.
torch.manual_seed(CONFIG['SEED'])
np.random.seed(CONFIG['SEED'])

CONFIG['MODEL_OUT'].parent.mkdir(parents=True, exist_ok=True)
CONFIG['PLOT_DIR'].mkdir(parents=True, exist_ok=True)

logger.info("Training on %s", CONFIG['DEVICE'].upper())

dataset = TomatoDataset(csv_file=CONFIG['DATASET_PATH'], transform=train_transform)

# Class order comes from the dataset itself, so the labels written into the
# checkpoint always match the indices the model was trained on. Reading
# os.listdir(DATA_FILEPATH) instead gave an unrelated order, and silently
# listed the working directory when the variable was unset.
class_names = list(dataset.classes)
logger.info("Found %d classes: %s", len(class_names), ", ".join(class_names))

train_data, val_data, test_data = random_split(
    dataset=dataset,
    lengths=[0.7, 0.2, 0.1],
    generator=torch.Generator().manual_seed(CONFIG['SEED']),
)

# Validation and test must not be augmented; they shared the training
# transform, which made their metrics noisy and optimistic.
val_data.dataset = TomatoDataset(CONFIG['DATASET_PATH'], transform=eval_transform)
test_data.dataset = TomatoDataset(CONFIG['DATASET_PATH'], transform=eval_transform)

train_loader = DataLoader(dataset=train_data, batch_size=CONFIG['BATCH_SIZE'], shuffle=True)
val_loader = DataLoader(dataset=val_data, batch_size=CONFIG['BATCH_SIZE'], shuffle=False)
test_loader = DataLoader(dataset=test_data, batch_size=CONFIG['BATCH_SIZE'], shuffle=False)

logger.info(
    "Batches - train: %d, validation: %d, test: %d",
    len(train_loader), len(val_loader), len(test_loader),
)


def compute_class_weights(loader, num_classes, device):
    """Return inverse-frequency class weights, caching them to disk."""
    filepath = os.getenv(
        "CLASS_WEIGHT_SAVE", str(CONFIG['PLOT_DIR'] / "class_weights.pt")
    )

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:

        logger.info("Loading cached class weights from %s", filepath)

        weights = torch.load(filepath, map_location=device)

        logger.info("Loaded Class Weights:\n")

        for i, cls in enumerate(class_names):
            logger.info(f"{cls}: {weights[i].item():.4f}")

        return weights
    

    logger.info("Computing class weights...")

    counts = Counter()

    for _, labels in tqdm(loader, desc="Loading labels"):
        counts.update(labels.tolist())

    total = sum(counts.values())

    weights = torch.tensor(
        [total / counts[i] for i in range(num_classes)],
        dtype=torch.float32,
        device=device
    )

    logger.info("Computed class weights:")

    for i, cls in enumerate(class_names):
        logger.info("  %-40s %.4f (count=%d)", cls, weights[i].item(), counts[i])

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    torch.save(weights, filepath)

    logger.info("Saved class weights to %s", filepath)

    return weights


# Training and validation loop
plant_clas_model = Model(output_head=len(class_names)).to(CONFIG['DEVICE'])

train_loss_arr = []
val_loss_arr = []
val_acc_arr = []
train_acc_arr = []

best_val_loss = np.inf
epochs_no_improve = 0
best_model_state = None

num_classes = len(class_names)
class_weights = compute_class_weights(train_loader, num_classes, CONFIG['DEVICE'])

loss_func = torch.nn.CrossEntropyLoss(weight=class_weights)
optimizer = torch.optim.AdamW(plant_clas_model.parameters(), lr=1e-4, weight_decay=1e-2)

for epoch in range(CONFIG['EPOCH']):
    logger.info("Epoch %d/%d", epoch + 1, CONFIG['EPOCH'])
    plant_clas_model.train()
    loss_sum = 0
    total = 0
    correct = 0

    train_pbar = tqdm(train_loader, desc=f"Train {epoch+1}")
    for img, label in train_pbar:
        X = img.to(CONFIG['DEVICE'])
        y = label.to(CONFIG['DEVICE'])

        optimizer.zero_grad()
        outputs = plant_clas_model(X)
        loss = loss_func(outputs, y)
        loss.backward()
        optimizer.step()

        loss_sum += loss.item()

        preds = outputs.argmax(dim=1)
        correct += (preds == y).sum().item()
        total += y.size(0)

    epoch_train_loss = loss_sum / len(train_loader)
    epoch_train_acc = correct / total
    train_loss_arr.append(epoch_train_loss)
    train_acc_arr.append(epoch_train_acc)

    val_loss_sum = 0
    total = 0
    correct = 0
    plant_clas_model.eval()

    with torch.no_grad():
        val_pbar = tqdm(val_loader, desc=f"Validate {epoch+1}")
        for img, label in val_pbar:
            X = img.to(CONFIG['DEVICE'])
            y = label.to(CONFIG['DEVICE'])

            outputs = plant_clas_model(X)

            loss = loss_func(outputs, y)
            val_loss_sum += loss.item()

            preds = outputs.argmax(dim=1)
            correct += (preds == y).sum().item()
            total += y.size(0)

    epoch_val_loss = val_loss_sum / len(val_loader)
    epoch_val_acc = correct / total

    val_loss_arr.append(epoch_val_loss)
    val_acc_arr.append(epoch_val_acc)

    tqdm.write(
        f"Epoch {epoch+1:03d} | "
        f"Train Loss: {epoch_train_loss:.4f}, Acc: {epoch_train_acc*100:.2f}% | "
        f"Val Loss: {epoch_val_loss:.4f}, Acc: {epoch_val_acc*100:.2f}%"
    )

    
    # early stopping mechanism
    if epoch_val_loss < best_val_loss:
        best_val_loss = epoch_val_loss
        epochs_no_improve = 0
        best_model_state = plant_clas_model.state_dict()
    else:
        epochs_no_improve += 1
        logger.info(f"Validation loss did not improve ({epochs_no_improve}/{CONFIG['PATIENCE']})")

        if epochs_no_improve >= CONFIG['PATIENCE']:
            logger.info("\nEarly stopping triggered.")
            break

# restore the best model weights
if best_model_state:
    plant_clas_model.load_state_dict(best_model_state)
    logger.info("Best model weights restored.")


test_loss_sum = 0
total = 0
correct = 0
all_preds = []
all_labels = []
all_probs = []

plant_clas_model.eval()

with torch.no_grad():
    test_pbar = tqdm(test_loader, desc=f"Validating...")
    for img, label in test_pbar:
        X = img.to(CONFIG['DEVICE'])
        y = label.to(CONFIG['DEVICE'])

        outputs = plant_clas_model(X)

        loss = loss_func(outputs, y)
        test_loss_sum += loss.item()

        probs = torch.softmax(outputs, dim=1)
        preds = probs.argmax(dim=1)

        correct += (preds == y).sum().item()
        total += y.size(0)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(y.cpu().numpy())
        all_probs.extend(probs.cpu().numpy())

epoch_test_loss = test_loss_sum / len(test_loader)
epoch_test_acc = correct / total

logger.info(f"Loss: {epoch_test_loss}")
logger.info(f"Accuracy: {epoch_test_acc}")


logger.info("\nClassification Report:\n")
print(classification_report(all_labels, all_preds, target_names=class_names, digits=4))


cm = confusion_matrix(all_labels, all_preds)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
            xticklabels=range(len(set(all_labels))),
            yticklabels=range(len(set(all_labels))))
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix Heatmap')
plt.savefig(CONFIG['PLOT_DIR'] / 'confusion_matrix.png')



plt.figure(figsize=(8, 5))
plt.title(f"Training & Validation model loss")
plt.plot(train_loss_arr, label="Train loss")
plt.plot(val_loss_arr, label="Validation loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.savefig(CONFIG['PLOT_DIR'] / 'training_validation_loss.png')


plt.figure(figsize=(8, 5))
plt.title("Training & Validation Accuracy")
plt.plot(train_acc_arr, label='Training accuracy')
plt.plot(val_acc_arr, label="Validation accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.savefig(CONFIG['PLOT_DIR'] / 'training_validation_accuracy.png')

y_true = np.array(all_labels)
y_prob = np.array(all_probs)

n_classes = len(class_names)
y_true_bin = label_binarize(y_true, classes=range(n_classes))


fpr = {}
tpr = {}
roc_auc = {}

for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

roc_auc["macro"] = roc_auc_score(y_true_bin, y_prob, average="macro", multi_class="ovr")
roc_auc["micro"] = roc_auc_score(y_true_bin, y_prob, average="micro", multi_class="ovr")

logger.info("\nROC-AUC Scores:")
for i, name in enumerate(class_names):
    logger.info(f"{name}: {roc_auc[i]:.4f}")
logger.info(f"Macro ROC-AUC: {roc_auc['macro']:.4f}")
logger.info(f"Micro ROC-AUC: {roc_auc['micro']:.4f}")

plt.figure(figsize=(8,6))
for i, name in enumerate(class_names):
    plt.plot(fpr[i], tpr[i], label=f"{name} (AUC={roc_auc[i]:.3f})")

plt.plot([0,1],[0,1],'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Multiclass ROC Curve (OvR)")
plt.legend()
plt.tight_layout()
plt.savefig(CONFIG['PLOT_DIR'] / 'multiclass_ROC_Curve.png')

precision = {}
recall = {}
avg_precision = {}

for i in range(n_classes):
    precision[i], recall[i], _ = precision_recall_curve(y_true_bin[:, i], y_prob[:, i])
    avg_precision[i] = average_precision_score(y_true_bin[:, i], y_prob[:, i])

avg_precision["macro"] = average_precision_score(y_true_bin, y_prob, average="macro")
avg_precision["micro"] = average_precision_score(y_true_bin, y_prob, average="micro")

logger.info("\nPR-AUC Scores:")
for i, name in enumerate(class_names):
    logger.info(f"{name}: {avg_precision[i]:.4f}")
logger.info(f"Macro PR-AUC: {avg_precision['macro']:.4f}")
logger.info(f"Micro PR-AUC: {avg_precision['micro']:.4f}")

plt.figure(figsize=(8,6))
for i, name in enumerate(class_names):
    plt.plot(recall[i], precision[i], label=f"{name} (AP={avg_precision[i]:.3f})")

plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Multiclass Precision-Recall Curve (OvR)")
plt.legend()
plt.tight_layout()
plt.savefig(CONFIG['PLOT_DIR'] / 'multiclass_PR_Curve.png')


# Saving the model.
# class_names is persisted alongside the weights: without it, inference could
# only report integer indices that nothing could map back to a disease.
checkpoint = {
    'state_dict': plant_clas_model.state_dict(),
    'config': plant_clas_model.config,
    'class_names': class_names,
}

torch.save(checkpoint, CONFIG['MODEL_OUT'])

logger.info("Saved checkpoint to %s", CONFIG['MODEL_OUT'])
