import os
import fitz
from tqdm import tqdm

def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        text = []

        for page in doc:
            page_text = page.get_text()
            if page_text:
                text.append(page_text)

        return "\n".join(text).strip()

    except Exception as e:
        print(f"Failed to read {pdf_path}: {e}")
        return ""


def save_text_file(filename: str, text: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    txt_path = os.path.join(
        output_dir,
        filename.replace(".pdf", ".txt")
    )

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return txt_path


def process_local_pdfs(input_dir: str, output_dir: str):
    pdf_files = [
        f for f in os.listdir(input_dir)
        if f.lower().endswith(".pdf")
    ]

    results = []

    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        pdf_path = os.path.join(input_dir, pdf_file)

        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            tqdm.write(f"⚠ Empty PDF skipped: {pdf_file}")
            continue

        txt_path = save_text_file(pdf_file, text, output_dir)

        results.append({
            "pdf": pdf_file,
            "txt": txt_path,
            "length": len(text)
        })

        tqdm.write(f"✔ Saved: {txt_path}")

    return results


if __name__ == "__main__":
    input_dir = "training/datasets/raw/papers"
    output_dir = "training/datasets/processed/papers/txt"

    results = process_local_pdfs(input_dir, output_dir)

    print(f"\nDone. Converted {len(results)} PDFs → TXT")