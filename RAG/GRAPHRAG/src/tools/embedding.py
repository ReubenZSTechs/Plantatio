import os
import json
import uuid # For unique ID in ChromaDB later
from src.utils.CONFIG import CONFIG

import chromadb
from chromadb.utils import embedding_functions

from tqdm import tqdm

def get_collection(embedding_model_name, collection_name):
    client = chromadb.PersistentClient(path='data/chroma_db')

    embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)

    collection = client.get_or_create_collection(name=collection_name, embedding_function=embedding_model)

    return collection, client

def load_json_transcripts(limit=20):
    all_segments = []
    count = 0

    for file_name in os.listdir(CONFIG['DATA_FILEPATH_TRANSCRIPT']):
        # if count >= limit:
        #     break

        if file_name.endswith(CONFIG['DATA_FILETYPE_TRANSCRIPT']):
            file_path = os.path.join(CONFIG['DATA_FILEPATH_TRANSCRIPT'], file_name)

            with open(file_path, "r", encoding='utf-8') as f:
                data = json.load(f)

                window_size = 5
                stride = 2

                segments_list = data.get("segments", [])

                for i in range(0, len(segments_list), stride):
                    chunk = segments_list[i:i+window_size]

                    if not chunk:
                        continue

                    text = " ".join([c["text"] for c in chunk])

                    file_data = {
                        "text": text.lower(),
                        "start": chunk[0].get("start", 0),
                        "end": chunk[-1].get("end", 0),
                        "source": file_name
                    }

                    all_segments.append(file_data)

            count += 1

    print(f"Loaded {count} files")
    return all_segments

def embed(collection, segments: list[dict], batch_size=128):
    print(f"Embedding and inserting {len(segments)} segments")

    for i in tqdm(range(0, len(segments), batch_size)):
        batch = segments[i:i+batch_size]

        docs, ids, metas = [], [], []

        for seg in batch:
            docs.append(seg['text'])
            ids.append(str(uuid.uuid4()))

            metas.append({
                'source': seg['source'],
                'start': seg['start'],
                'end': seg['end']
            })

        collection.add(documents=docs, ids=ids, metadatas=metas)


        
if __name__ == "__main__":
    collection, client = get_collection(embedding_model_name=CONFIG['EMBEDDING_MODEL_NAME_SENTENCEBERT'], collection_name=CONFIG['COLLECTION_NAME_SENTENCEBERT'])

    if collection.count() > 0:
        print(f"Collection already has data")
    else:
        segments = load_json_transcripts()
        embed(collection=collection, segments=segments)
        print(f"Embedding completed and saved to data/chroma_db")

    print(client.list_collections())