import os
import json
from PIL import Image
import ollama

# ============================================================
# CONFIG
# ============================================================

DATASET_PATH = "training/datasets/raw/EuroSAT_RGB"
OUTPUT_FILE = "training/datasets/processed/satellite_images/eurosat_vlm_labels.jsonl"

MODEL_NAME = "qwen3-vl:4b-instruct-bf16"

VALID_EXTENSIONS = [".jpg", ".jpeg", ".png", ".tif"]

# ============================================================
# PROMPT
# ============================================================

PROMPT = """
You are an expert environmental satellite imagery analyst.

Analyze the satellite image visually.

Estimate environmental properties based ONLY on visual vegetation density.

IMPORTANT:
- NEVER return all zeros.
- Dense forest should have:
  - high canopy_cover
  - high biomass
  - high carbon_EQ
- Agricultural land should have:
  - medium vegetation
  - medium biomass
- Residential or industrial land should have:
  - low vegetation values

Use realistic approximate ranges.

Return ONLY valid JSON.

Schema:
{
  "vegetation_density": "low|medium|high",
  "canopy_cover": number,
  "est_biomass": number,
  "carbon_EQ": number,
  "restoration_quality": "poor|moderate|strong",
  "confidence": number
}
"""

# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json(text):

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    json_text = text[start:end+1]

    try:
        return json.loads(json_text)
    except Exception:
        return None

# ============================================================
# OLLAMA INFERENCE
# ============================================================

def run_vlm(image_path, class_name):

    dynamic_prompt = f"""
    This satellite image belongs to the class: {class_name}

    Analyze the ecological characteristics visually.

    Forest:
    - very high vegetation
    - high biomass
    - high canopy cover

    AnnualCrop:
    - medium vegetation
    - moderate biomass

    Residential:
    - low vegetation
    - low biomass

    Return ONLY valid JSON.

    Schema:
    {{
      "vegetation_density": "low|medium|high",
      "canopy_cover": number,
      "est_biomass": number,
      "carbon_EQ": number,
      "restoration_quality": "poor|moderate|strong",
      "confidence": number
    }}
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": dynamic_prompt,
                "images": [image_path]
            }
        ]
    )

    return response["message"]["content"]

# ============================================================
# MAIN LOOP
# ============================================================

all_results = []

for class_name in os.listdir(DATASET_PATH):

    class_folder = os.path.join(DATASET_PATH, class_name)

    if not os.path.isdir(class_folder):
        continue

    print(f"\n[INFO] Processing class: {class_name}")

    for filename in os.listdir(class_folder):

        ext = os.path.splitext(filename)[1].lower()

        if ext not in VALID_EXTENSIONS:
            continue

        image_path = os.path.join(class_folder, filename)

        print(f"[INFO] Labeling: {image_path}")

        try:

            raw_output = run_vlm(image_path, class_name)

            parsed = extract_json(raw_output)

            if parsed is None:
                print("[WARNING] Invalid JSON response")
                print(raw_output)
                continue

            result = {
                "image_path": image_path,
                "class_name": class_name,
                "labels": parsed
            }

            all_results.append(result)

            # Incremental save
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(result) + "\n")

            print("[SUCCESS] Saved label")

        except Exception as e:
            print(f"[ERROR] {e}")

# ============================================================
# FINISHED
# ============================================================

print("\n===================================")
print(f"[INFO] Finished")
print(f"[INFO] Total labeled: {len(all_results)}")
print(f"[INFO] Output file: {OUTPUT_FILE}")
print("===================================")