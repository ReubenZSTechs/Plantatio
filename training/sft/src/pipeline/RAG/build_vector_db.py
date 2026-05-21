import os
import json
import shutil
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.utils.CONFIG import CONFIG



load_dotenv()


def load_documents():
    chunks_path = CONFIG["CHUNKS_FILEPATH"]

    print(f"Loading chunks from {chunks_path}")

    if not os.path.exists(chunks_path):
        raise FileNotFoundError(f"{chunks_path} does not exist")

    documents = []

    with open(chunks_path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)

            doc = Document(
                page_content=data["text"],
                metadata={
                    "chunk_id": data["chunk_id"],
                    "source_doc_id": data["source_doc_id"],
                    "length": len(data["text"])
                }
            )

            documents.append(doc)

    print(f"Loaded {len(documents)} chunks")

    # preview
    preview_limit = min(2, len(documents))
    for i in range(preview_limit):
        doc = documents[i]
        print(f"\nDocument {i+1}")
        print(f"Chunk ID: {doc.metadata['chunk_id']}")
        print(f"Source Doc: {doc.metadata['source_doc_id']}")
        print(f"Length: {doc.metadata['length']}")
        print(f"Preview: {doc.page_content[:100]}...")

    return documents


def create_vector_store(documents):
    persist_directory = CONFIG["VECTOR_DB_DIR"]

    if CONFIG["CLEAR_VECTOR_DB"] and os.path.exists(persist_directory):
        print("Removing existing vector store...")
        shutil.rmtree(persist_directory)

    print("Loading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name=CONFIG["EMBEDDING_MODEL"],
        model_kwargs={"device": CONFIG["EMBEDDING_DEVICE"]},
    )

    print("Creating vector store...")

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata=CONFIG["CHROMA_COLLECTION_METADATA"]
    )

    print("Finished creating vector store")
    print(f"Saved to: {persist_directory}")

    return vector_store


def Build_vector_DB():
    print("Build_Vector_DB")

    documents = load_documents()

    if len(documents) == 0:
        raise ValueError("No chunks loaded. Check your CHUNKS_FILEPATH.")

    vector_store = create_vector_store(documents)

    print("=== DONE ===")
