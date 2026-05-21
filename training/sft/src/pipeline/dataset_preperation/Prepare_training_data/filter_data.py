import os
import pandas as pd

from src.pipeline.RAG.retriver import (
    load_vector_db,
    multi_query_retrieve,
    get_chunk_map,
)


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


def evaluate_row(
    db,
    chunk_map,
    row,
    k,
):

    queries = [
        row.get("main_question"),
        row.get("sub_question_1"),
        row.get("sub_question_2"),
        row.get("sub_question_3"),
    ]

    ground_truth = parse_ground_truth(
        row.get("selected_documents")
    )

    if not ground_truth:
        return False, [], [], [], [], [], []

    retrieved_ids, retrieved_docs = multi_query_retrieve(
        db,
        queries,
        k,
    )

    gt_set = set(ground_truth)

    hit = any(cid in gt_set for cid in retrieved_ids)

    # chosen = semua ground truth
    chosen_ids = list(gt_set)

    chosen_chunks = [
        chunk_map.get(cid)
        for cid in chosen_ids
        if cid in chunk_map
    ]

    # retriever dengan duplikat
    retriever_ids_with_dup = retrieved_ids

    retriever_chunks_with_dup = [
        chunk_map.get(cid)
        for cid in retriever_ids_with_dup
        if cid in chunk_map
    ]

    # retriever tanpa duplikat
    retriever_ids_no_dup = list(
        dict.fromkeys(retrieved_ids)
    )

    retriever_chunks_no_dup = [
        chunk_map.get(cid)
        for cid in retriever_ids_no_dup
        if cid in chunk_map
    ]

    return (
        hit,
        chosen_ids,
        chosen_chunks,
        retriever_ids_with_dup,
        retriever_chunks_with_dup,
        retriever_ids_no_dup,
        retriever_chunks_no_dup,
    )


def filter_good_data(
    csv_filepath: str,
    eval_k: int,
    good_data_csv_with_dup: str,
    good_data_csv_no_dup: str,
    bad_data_csv: str,
    chunk_sep: str,
):

    print("=== FILTERING GOOD & BAD DATA ===")

    # LOAD DATA

    df = pd.read_csv(csv_filepath)

    db = load_vector_db()

    chunk_map = get_chunk_map(db)

    # STORAGE

    good_rows_with_dup = []

    good_rows_no_dup = []

    bad_rows = []

    # ITERATE ROWS

    for _, row in df.iterrows():

        (
            hit,
            chosen_ids,
            chosen_chunks,
            retriever_ids_with_dup,
            retriever_chunks_with_dup,
            retriever_ids_no_dup,
            retriever_chunks_no_dup,
        ) = evaluate_row(
            db=db,
            chunk_map=chunk_map,
            row=row,
            k=eval_k,
        )

        base_row = dict(row)

        base_row["chosen_id"] = ",".join(chosen_ids)

        base_row["chosen_chunks"] = (
            chunk_sep.join(chosen_chunks)
            if chosen_chunks
            else ""
        )

            # GOOD DATA
    
        if hit:

            row_with_dup = dict(base_row)

            row_with_dup["retriever_id"] = ",".join(
                retriever_ids_with_dup
            )

            row_with_dup["retriever_chunks"] = (
                chunk_sep.join(retriever_chunks_with_dup)
                if retriever_chunks_with_dup
                else ""
            )

            good_rows_with_dup.append(row_with_dup)

            row_no_dup = dict(base_row)

            row_no_dup["retriever_id"] = ",".join(
                retriever_ids_no_dup
            )

            row_no_dup["retriever_chunks"] = (
                chunk_sep.join(retriever_chunks_no_dup)
                if retriever_chunks_no_dup
                else ""
            )

            good_rows_no_dup.append(row_no_dup)

    
        else:
            row_with_dup = dict(base_row)

            row_with_dup["retriever_id"] = ",".join(
                retriever_ids_with_dup
            )

            row_with_dup["retriever_chunks"] = (
                chunk_sep.join(retriever_chunks_with_dup)
                if retriever_chunks_with_dup
                else ""
            )

            good_rows_with_dup.append(row_with_dup)

            row_no_dup = dict(base_row)

            row_no_dup["retriever_id"] = ",".join(
                retriever_ids_no_dup
            )

            row_no_dup["retriever_chunks"] = (
                chunk_sep.join(retriever_chunks_no_dup)
                if retriever_chunks_no_dup
                else ""
            )

            good_rows_no_dup.append(row_no_dup)




    # DATAFRAME
    good_df_with_dup = pd.DataFrame(
        good_rows_with_dup
    )

    good_df_no_dup = pd.DataFrame(
        good_rows_no_dup
    )

    bad_df = pd.DataFrame(
        bad_rows
    )


    os.makedirs(
        os.path.dirname(good_data_csv_with_dup),
        exist_ok=True,
    )

    good_df_with_dup.to_csv(
        good_data_csv_with_dup,
        index=False,
    )

    good_df_no_dup.to_csv(
        good_data_csv_no_dup,
        index=False,
    )

    bad_df.to_csv(
        bad_data_csv,
        index=False,
    )

    print("Filtering completed.")