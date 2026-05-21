from src.utils.CONFIG import CONFIG
import os
import json
import re

def clean_text(text: str):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def load_documents_from_processed(base_path: str):
    json_path = os.path.join(base_path, "filtered_results.json")
    txt_folder = os.path.join(base_path, "txt")

    with open(json_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    documents = {}

    for i, item in enumerate(metadata):
        doc_id = f"doc_{i}"

        # Extract filename from ID (safe way)
        txt_filename = f"{item['id']}.txt"
        txt_path = os.path.join(txt_folder, txt_filename)

        if not os.path.exists(txt_path):
            print(f"WARNING: Missing {txt_path}")
            continue

        with open(txt_path, "r", encoding="utf-8") as f:
            text = f.read()

        text = clean_text(text)

        documents[doc_id] = {
            "id": item["id"],
            "title": item["title"].strip(),
            "text": text,
            "labels": item.get("labels", []),
            "source": txt_filename
        }

    return documents

if __name__ == "__main__":
    docs = load_documents_from_processed(CONFIG['DATA_FILEPATH'])

    print(docs['doc_0']['title'])
    print(docs['doc_1']['title'])
    print(docs['doc_2']['title'])