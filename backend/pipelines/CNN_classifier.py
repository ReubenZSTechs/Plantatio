import argparse
import os
import torch
from PIL import Image

from training.configs.models.CNN_model import Model
from training.configs.datasets.cnn_DataLoader import transform


# =========================
# DEVICE
# =========================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# =========================
# LOAD MODEL
# =========================
def load_model(model_path):
    checkpoint = torch.load(model_path, map_location=DEVICE)

    model = Model(output_head=checkpoint["config"]["output_head"])
    model.load_state_dict(checkpoint["state_dict"])

    model.to(DEVICE)
    model.eval()

    return model


# =========================
# PREDICT SINGLE IMAGE
# =========================
def predict_image(model, image_path, topk=3):
    image = Image.open(image_path).convert("RGB")
    x = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(x)
        probs = torch.softmax(outputs, dim=1)[0]

        top_probs, top_idxs = torch.topk(probs, topk)

    results = []
    for i in range(topk):
        results.append({
            "class_id": top_idxs[i].item(),
            "confidence": top_probs[i].item()
        })

    return results


# =========================
# PREDICT FOLDER
# =========================
def predict_folder(model, folder_path, topk=3):
    results = {}

    for file in os.listdir(folder_path):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(folder_path, file)
            results[file] = predict_image(model, path, topk)

    return results


# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser(description="CNN Inference Script")

    parser.add_argument("--model", type=str, default="models/plant_CNN_classifier_model.pth")
    parser.add_argument("--image", type=str, help="Path to image")
    parser.add_argument("--folder", type=str, help="Path to folder of images")
    parser.add_argument("--topk", type=int, default=3, help="Top-K predictions")

    args = parser.parse_args()

    model = load_model(args.model)

    # =========================
    # SINGLE IMAGE MODE
    # =========================
    if args.image:
        results = predict_image(model, args.image, args.topk)

        print("\n=== PREDICTION ===")
        for r in results:
            print(f"Class ID: {r['class_id']} | Confidence: {r['confidence']:.4f}")

    # =========================
    # FOLDER MODE
    # =========================
    elif args.folder:
        results = predict_folder(model, args.folder, args.topk)

        print("\n=== BATCH PREDICTION ===")
        for img_name, preds in results.items():
            print(f"\n{img_name}")
            for p in preds:
                print(f"  Class ID: {p['class_id']} | Confidence: {p['confidence']:.4f}")

    else:
        print("Please provide --image or --folder")


if __name__ == "__main__":
    main()