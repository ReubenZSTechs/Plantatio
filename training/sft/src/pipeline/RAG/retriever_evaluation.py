import pandas as pd
from dotenv import load_dotenv

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from src.utils.CONFIG import CONFIG


load_dotenv()


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


def parse_ground_truth(selected_documents):
    if pd.isna(selected_documents):
        return []

    if isinstance(selected_documents, str):
        selected_documents = selected_documents.strip("[]")
        return [
            x.strip().strip("'\"")
            for x in selected_documents.split(",")
            if x.strip()
        ]

    return []


def multi_query_retrieve(db, queries, k):
    """
    queries: list of query strings
    return: merged retrieved chunk_ids
    """
    all_ids = []

    for q in queries:
        if pd.isna(q) or not q:
            continue

        retriever = db.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(q)

        ids = [doc.metadata.get("chunk_id") for doc in docs]
        ids = [x for x in ids if x is not None]

        all_ids.extend(ids)

    return list(set(all_ids))


def evaluate_sample(db, row, k):
    main_q = row["main_question"]
    sub_qs = [
        row.get("sub_question_1"),
        row.get("sub_question_2"),
        row.get("sub_question_3"),
    ]

    queries = [main_q] + sub_qs

    ground_truth = parse_ground_truth(row["selected_documents"])

    retrieved_ids = multi_query_retrieve(db, queries, k)

    ground_truth_set = set(ground_truth)
    retrieved_set = set(retrieved_ids)

    intersection = ground_truth_set & retrieved_set

    hit = int(len(intersection) > 0)

    recall = len(intersection) / len(ground_truth_set) if ground_truth_set else 0
    precision = len(intersection) / len(retrieved_set) if retrieved_set else 0

    return hit, recall, precision, retrieved_ids


def evaluate():
    print("=== MULTI-QUERY RETRIEVER EVALUATION ===")

    csv_path = CONFIG["GOOD_DATA_CSV"]
    k = CONFIG.get("EVAL_K", 5)

    print(f"Loading dataset from: {csv_path}")

    df = pd.read_csv(csv_path)

    db = load_vector_db()

    total_hit = 0
    total_recall = 0
    total_precision = 0

    n = len(df)

    for i, row in df.iterrows():
        hit, recall, precision, retrieved_ids = evaluate_sample(db, row, k)

        ground_truth = parse_ground_truth(row["selected_documents"])

        total_hit += hit
        total_recall += recall
        total_precision += precision

        print(f"\n[{i+1}/{n}]")
        print(f"Main Query: {row['main_question'][:80]}...")
        print(f"Ground Truth: {ground_truth}")
        print(f"Retrieved (merged): {retrieved_ids}")
        print(f"Hit@{k}: {hit} | Recall@{k}: {recall:.2f} | Precision@{k}: {precision:.2f}")

    print("\n=== FINAL RESULT ===")
    print(f"Hit@{k}       : {total_hit / n:.4f}")
    print(f"Recall@{k}    : {total_recall / n:.4f}")
    print(f"Precision@{k} : {total_precision / n:.4f}")


if __name__ == "__main__":
    evaluate()