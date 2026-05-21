from src.utils.CONFIG import CONFIG
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import pandas as pd


def load_vector_db():
    print("Loading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name=CONFIG["EMBEDDING_MODEL"],
        model_kwargs={"device": CONFIG["EMBEDDING_DEVICE"]},
    )

    print("Loading Chroma DB...")

    db = Chroma(
        persist_directory=CONFIG["VECTOR_DB_DIR"],
        embedding_function=embedding_model,
        collection_metadata=CONFIG["CHROMA_COLLECTION_METADATA"]
    )

    return db

def get_chunk_map(db):
    collection = db._collection
    data = collection.get(include=["documents", "metadatas"])

    chunk_map = {}

    for doc, meta in zip(data["documents"], data["metadatas"]):
        chunk_id = meta.get("chunk_id")
        if chunk_id:
            chunk_map[chunk_id] = doc

    return chunk_map

def multi_query_retrieve(db, queries, k):
    retriever = db.as_retriever(search_kwargs={"k": k})

    all_ids = []
    all_docs = []

    for q in queries:
        if pd.isna(q) or not q:
            continue

        docs = retriever.invoke(q)

        ids = [doc.metadata.get("chunk_id") for doc in docs]
        ids = [x for x in ids if x is not None]

        all_ids.extend(ids)
        all_docs.extend(docs)

    return all_ids, all_docs

