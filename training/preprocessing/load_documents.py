import os
from dotenv import load_dotenv

load_dotenv()

import re


def clean_text(text: str):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_title(text: str, fallback: str):
    lines = text.split("\n")
    if len(lines) > 0:
        title = lines[0].strip()
        if len(title) > 5:
            return title
    return fallback


def load_documents_from_folder(txt_folder: str):
    if not os.path.exists(txt_folder):
        raise FileNotFoundError(f"TXT folder not found: {txt_folder}")

    documents = {}

    txt_files = [
        f for f in os.listdir(txt_folder)
        if f.endswith(".txt")
    ]

    for i, filename in enumerate(txt_files):
        txt_path = os.path.join(txt_folder, filename)

        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Failed to read {txt_path}: {e}")
            continue

        text = clean_text(text)

        doc_id = f"doc_{i}"
        file_id = filename.replace(".txt", "")

        title = extract_title(text, file_id)

        documents[doc_id] = {
            "id": file_id,
            "title": title.strip(),
            "text": text,
            "source": filename
        }

    return documents


if __name__ == "__main__":
    docs = load_documents_from_folder(os.getenv('TXT_PAPERS_FILEPATH'))

    # safe print (avoid crash if fewer files)
    keys = list(docs.keys())

    for i in range(min(3, len(keys))):
        print(docs[keys[i]]["title"])