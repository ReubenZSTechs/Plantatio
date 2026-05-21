from training.configs.models.CNN_model import Model
from training.configs.datasets.cnn_DataLoader import TomatoDataset, transform

import torch
from torch.utils.data import random_split, DataLoader
from PIL import Image

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
import os

from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, roc_auc_score, precision_recall_curve, average_precision_score
from sklearn.preprocessing import label_binarize
from collections import Counter

import warnings
warnings.filterwarnings(action='ignore')

CONFIG = {
    'BATCH_SIZE': 32,
    'DEVICE': 'cuda' if torch.cuda.is_available() else 'cpu',
    'EPOCH': 30,
    'DATASET_PATH': 'training/datasets/formatted/directory_dataset.csv',
    'NUM_CLASSES': 10,
    'PATIENCE': 3,
}

if torch.cuda.is_available():
    print(f"Using GPU")
else:
    print(f"Using CPU")


dataset = TomatoDataset(csv_file=CONFIG['DATASET_PATH'], transform=transform)

train_data, val_data, test_data = random_split(dataset=dataset, lengths=[0.7, 0.2, 0.1])

train_loader = DataLoader(dataset=train_data, batch_size=CONFIG['BATCH_SIZE'], shuffle=True)
val_loader = DataLoader(dataset=val_data, batch_size=CONFIG['BATCH_SIZE'], shuffle=True)
test_loader = DataLoader(dataset=test_data, batch_size=CONFIG['BATCH_SIZE'], shuffle=False)

for img, label in train_loader:
    img_single = img[0]

    img_np = img_single.cpu().numpy()

    # Rearrange dimensions from [C, H, W] → [H, W, C]
    img_np = img_np.transpose((1, 2, 0))

    img_np = (img_np * 0.5) + 0.5  # example for [-1,1] range

    plt.imshow(img_np)
    plt.title(f"Label: {label[0].item()}")
    plt.axis("off")
    plt.show()

    break

print()

print(f"There are {len(train_loader)} training data batches")
print(f"There are {len(val_loader)} validation data batches")
print(f"There are {len(test_loader)} testing data batches\n") 


# Compute Class Weights
class_names = []

for class_name in os.listdir(os.getenv("DATA_FILEPATH")):
    class_names.append(class_name)

print(class_names)


def compute_class_weights(loader, num_classes, device):
    filepath = os.getenv("CLASS_WEIGHT_SAVE")

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:

        print(f"Loading existing class weights from:\n{filepath}\n")

        weights = torch.load(filepath, map_location=device)

        print("Loaded Class Weights:\n")

        for i, cls in enumerate(class_names):
            print(f"{cls}: {weights[i].item():.4f}")

        return weights
    

    print("Computing class weights...\n")

    counts = Counter()

    for _, labels in tqdm(loader, desc="Loading labels"):
        counts.update(labels.tolist())

    total = sum(counts.values())

    weights = torch.tensor(
        [total / counts[i] for i in range(num_classes)],
        dtype=torch.float32,
        device=device
    )

    print("\nComputed Class Weights:\n")

    for i, cls in enumerate(class_names):
        print(
            f"{cls}: {weights[i].item():.4f} "
            f"(count = {counts[i]})"
        )

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    torch.save(weights, filepath)

    print(f"\nSaved class weights to:\n{filepath}")

    return weights


# Training and validation loop
plant_clas_model = Model(output_head=10).to(CONFIG['DEVICE'])

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
    print(f"\nEpoch {epoch+1}/{CONFIG['EPOCH']}")
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
        print(f"Validation loss did not improve ({epochs_no_improve}/{CONFIG['PATIENCE']})")

        if epochs_no_improve >= CONFIG['PATIENCE']:
            print("\nEarly stopping triggered.")
            break

# restore the best model weights
if best_model_state:
    plant_clas_model.load_state_dict(best_model_state)
    print("Best model weights restored.")


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

print(f"Loss: {epoch_test_loss}")
print(f"Accuracy: {epoch_test_acc}")


print("\nClassification Report:\n")
print(classification_report(all_labels, all_preds, target_names=class_names, digits=4))


cm = confusion_matrix(all_labels, all_preds)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
            xticklabels=range(len(set(all_labels))),
            yticklabels=range(len(set(all_labels))))
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix Heatmap')
plt.savefig('training/datasets/evaluation/confusion_matrix.png')



plt.figure(figsize=(8, 5))
plt.title(f"Training & Validation model loss")
plt.plot(train_loss_arr, label="Train loss")
plt.plot(val_loss_arr, label="Validation loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.savefig('training/datasets/evaluation/training_validation_loss.png')


plt.figure(figsize=(8, 5))
plt.title("Training & Validation Accuracy")
plt.plot(train_acc_arr, label='Training accuracy')
plt.plot(val_acc_arr, label="Validation accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.savefig("training/datasets/evaluation/training_validation_accuracy.png")

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

print("\nROC-AUC Scores:")
for i, name in enumerate(class_names):
    print(f"{name}: {roc_auc[i]:.4f}")
print(f"Macro ROC-AUC: {roc_auc['macro']:.4f}")
print(f"Micro ROC-AUC: {roc_auc['micro']:.4f}")

plt.figure(figsize=(8,6))
for i, name in enumerate(class_names):
    plt.plot(fpr[i], tpr[i], label=f"{name} (AUC={roc_auc[i]:.3f})")

plt.plot([0,1],[0,1],'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Multiclass ROC Curve (OvR)")
plt.legend()
plt.tight_layout()
plt.savefig("training/datasets/evaluation/multiclass_ROC_Curve.png")

precision = {}
recall = {}
avg_precision = {}

for i in range(n_classes):
    precision[i], recall[i], _ = precision_recall_curve(y_true_bin[:, i], y_prob[:, i])
    avg_precision[i] = average_precision_score(y_true_bin[:, i], y_prob[:, i])

avg_precision["macro"] = average_precision_score(y_true_bin, y_prob, average="macro")
avg_precision["micro"] = average_precision_score(y_true_bin, y_prob, average="micro")

print("\nPR-AUC Scores:")
for i, name in enumerate(class_names):
    print(f"{name}: {avg_precision[i]:.4f}")
print(f"Macro PR-AUC: {avg_precision['macro']:.4f}")
print(f"Micro PR-AUC: {avg_precision['micro']:.4f}")

plt.figure(figsize=(8,6))
for i, name in enumerate(class_names):
    plt.plot(recall[i], precision[i], label=f"{name} (AP={avg_precision[i]:.3f})")

plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Multiclass Precision-Recall Curve (OvR)")
plt.legend()
plt.tight_layout()
plt.savefig('training/datasets/evaluation/multiclass_PR_Curve.png')


# Saving the model
model_architecture = {
    'state_dict': plant_clas_model.state_dict(),

    'config': {
        'output_head': plant_clas_model.output_head,
        'dropout1': plant_clas_model.dropout1,
        'dropout2': plant_clas_model.dropout2,
        'dropout3': plant_clas_model.dropout3,
        'hidden1': plant_clas_model.hidden1,
        'hidden2': plant_clas_model.hidden2,
        'hidden3': plant_clas_model.hidden3,
        'out1': plant_clas_model.out1,
        'out2': plant_clas_model.out2,
        'resnet50_use': plant_clas_model.resnet50_use
    }
}

torch.save(model_architecture, "models/plant_CNN_classifier_model.pth")