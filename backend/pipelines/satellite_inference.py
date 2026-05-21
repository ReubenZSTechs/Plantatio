import os
import json
import argparse
from PIL import Image
from huggingface_hub import InferenceClient


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct"
HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN
)


# ============================================================
# PROMPT
# ============================================================

def build_prompt(class_hint=None):

    base_prompt = """
You are an expert satellite image analyst.

Analyze the image and estimate ecological characteristics.

Return ONLY valid JSON in this schema:

{
  "vegetation_density": "low|medium|high",
  "canopy_cover": number,
  "est_biomass": number,
  "carbon_EQ": number,
  "restoration_quality": "poor|moderate|strong",
  "confidence": number
}
"""

    if class_hint:
        base_prompt += f"""

Additional context:
This image is likely related to: {class_hint}
"""

    return base_prompt


# ============================================================
# JSON PARSER
# ============================================================

def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        return json.loads(text[start:end+1])
    except Exception:
        return None


# ============================================================
# VLM INFERENCE
# ============================================================

def run_vlm(image_path, class_hint=None):

    image = Image.open(image_path).convert("RGB")

    prompt = build_prompt(class_hint)

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "image": image
            }
        ],
        max_tokens=512
    )

    return response.choices[0].message["content"]


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(description="HF VLM Satellite Inference")

    parser.add_argument("--image", type=str, required=True, help="Path to image")
    parser.add_argument("--class_hint", type=str, default=None, help="Optional class hint")

    args = parser.parse_args()

    print("\n===================================")
    print("VLM INFERENCE START")
    print("===================================\n")

    print(f"[INFO] Image: {args.image}")

    raw_output = run_vlm(args.image, args.class_hint)

    print("\n[RAW MODEL OUTPUT]")
    print(raw_output)

    parsed = extract_json(raw_output)

    print("\n[PARSED RESULT]")

    if parsed is None:
        print("❌ Failed to parse JSON")
    else:
        print(json.dumps(parsed, indent=4))

    print("\n===================================")
    print("DONE")
    print("===================================\n")


if __name__ == "__main__":
    main()