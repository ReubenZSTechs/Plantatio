# Training

Two models are trained here: the tomato leaf-disease CNN used by
`POST /api/plants/{id}/diagnose`, and the LoRA fine-tunes under `sft/`.

## Leaf-disease classifier

### 1. Get the dataset

The tooling expects an ImageFolder tree — one directory per class. The
10-class tomato subset of [PlantVillage][pv] is what the defaults assume:

```
training/datasets/raw/PlantVillage_Tomato/
├── Tomato___Bacterial_spot/
├── Tomato___Early_blight/
├── Tomato___Late_blight/
├── Tomato___Leaf_Mold/
├── Tomato___Septoria_leaf_spot/
├── Tomato___Spider_mites_Two_spotted_spider_mite/
├── Tomato___Target_Spot/
├── Tomato___Tomato_Yellow_Leaf_Curl_Virus/
├── Tomato___Tomato_mosaic_virus/
└── Tomato___healthy/
```

Any number of classes works; `output_head` follows the directory count.

[pv]: https://www.kaggle.com/datasets/emmarex/plantdisease

### 2. Point the environment at it

In `.env` (copy `.env.example` first):

```
DATA_FILEPATH=./training/datasets/raw/PlantVillage_Tomato
CNN_DIR_FILEPATH=./training/datasets/formatted
```

### 3. Build the index and train

```bash
pip install -r training/requirements.txt

python -m training.preprocessing.build_dataset_CNN   # writes directory_dataset.csv
python -m training.scripts.train_cnn                 # writes the checkpoint
```

Training uses class-weighted cross-entropy (the PlantVillage classes are
imbalanced) with early stopping on validation loss. Evaluation plots —
confusion matrix, loss and accuracy curves, per-class ROC and
precision-recall — land in `training/datasets/evaluation/`.

The checkpoint is written to `models/plant_CNN_classifier_model.pth` and
carries three things: the weights, the architecture hyperparameters needed to
rebuild the network, and the class names in label-index order. Inference needs
all three, so do not hand-assemble a checkpoint without them.

### 4. Use it

The API picks the checkpoint up from `PLANTATIO_CNN_CHECKPOINT`. Until one
exists, `POST /api/plants/{id}/diagnose` returns 503 with a pointer back to
this file rather than guessing a diagnosis.

```bash
curl -F image=@leaf.jpg http://localhost:8000/api/plants/1/diagnose
```

Or straight from the CLI:

```bash
python -m backend.pipelines.CNN_classifier --image leaf.jpg --topk 3
```

### Notes

- Inference uses `eval_transform` (deterministic), not `train_transform`
  (randomised). Scoring the same leaf twice must give the same answer.
- `resnet50_use=True` fine-tunes an ImageNet ResNet-50 backbone and is the
  default. `resnet50_use=False` trains a much smaller scratch CNN, which is
  useful for a quick end-to-end check on CPU.

## Language-model fine-tuning

See `sft/` for the LoRA pipeline, and `utils/ollama/` for GGUF conversion and
Ollama export.
