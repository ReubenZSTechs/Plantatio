import json
import pandas as pd

from pathlib import Path

from src.utils.PROMPT_TEMPLATES import (
    get_query_rewriter_train_prompt,
    get_answer_generation_train_prompt,
    get_document_selector_train_prompt,
)


def safe_str(val) -> str:
    if pd.isna(val):
        return ""
    return str(val).strip()


def split_chunks(raw: str,chunk_sep: str,) -> list[str]:
    return [c.strip() for c in raw.split(chunk_sep) if c.strip()]


def chosen_ids_to_doc_ids(chosen_raw: str,) -> list[str]:

    return [cid.strip() for cid in chosen_raw.split(",") if cid.strip()
    ]


def build_qr(row) -> dict:

    question = safe_str(row["main_question"])

    subs = [
        safe_str(row.get("sub_question_1", "")),
        safe_str(row.get("sub_question_2", "")),
        safe_str(row.get("sub_question_3", "")),
    ]

    subs = [s for s in subs if s]

    output = json.dumps(
        subs if subs else [question],
        ensure_ascii=False,
    )

    return {
        "instruction": get_query_rewriter_train_prompt(
            question
        ),
        "input": "",
        "output": output,
        "history": [],
    }


def build_sel(
    row,
    chunk_sep: str,
) -> dict | None:

    question = safe_str(
        row["main_question"]
    )

    chosen_raw = safe_str(
        row["chosen_id"]
    )

    retriever_raw = safe_str(
        row["retriever_chunks"]
    )

    retriever_ids = safe_str(
        row["retriever_id"]
    )

    ret_chunks = split_chunks(
        retriever_raw,
        chunk_sep,
    )

    if not ret_chunks:
        return None

    ret_ids = [
        rid.strip()
        for rid in retriever_ids.split(",")
        if rid.strip()
    ]

    
    # BUILD DOC LIST
    

    if len(ret_ids) == len(ret_chunks):

        doc_list = [
            {
                "id": ret_ids[i],
                "content": ret_chunks[i],
            }
            for i in range(len(ret_chunks))
        ]

    else:

        doc_list = [
            {
                "id": f"doc_{i}",
                "content": ret_chunks[i],
            }
            for i in range(len(ret_chunks))
        ]

    chosen_ids = chosen_ids_to_doc_ids(
        chosen_raw
    )

    ret_id_set = {
        d["id"]
        for d in doc_list
    }

    relevant_output = [
        cid
        for cid in chosen_ids
        if cid in ret_id_set
    ]

    # fallback edge case
    if not relevant_output:
        relevant_output = chosen_ids

    return {
        "instruction": get_document_selector_train_prompt(
            question,
            doc_list,
        ),
        "input": "",
        "output": json.dumps(
            relevant_output,
            ensure_ascii=False,
        ),
        "history": [],
    }


def build_gen(
    row,
    chunk_sep: str,
) -> dict | None:

    question = safe_str(
        row["main_question"]
    )

    answer = safe_str(
        row["accepted_answer"]
    )



    return {
        "instruction": get_answer_generation_train_prompt(
            question,
        ),
        "input": "",
        "output": answer,
        "history": [],
    }


def build_sft_data(
    input_csv: str,
    qr_output: str,
    sel_output: str,
    gen_output: str,
    chunk_sep: str,
):

    print(f"Reading: {input_csv}")

    
    # LOAD CSV
    

    df = pd.read_csv(input_csv)

    print(f"Total rows: {len(df)}")

        

    qr_data = []

    sel_data = []

    gen_data = []

    skipped_sel = 0

    skipped_gen = 0

    

    for _, row in df.iterrows():

        
        # QUERY REWRITER

        qr_data.append(
            build_qr(row)
        )

        
        # DOCUMENT SELECTOR

        sel_entry = build_sel(
            row=row,
            chunk_sep=chunk_sep,
        )

        if sel_entry:
            sel_data.append(sel_entry)
        else:
            skipped_sel += 1

        
        # ANSWER GENERATOR

        gen_entry = build_gen(
            row=row,
            chunk_sep=chunk_sep,
        )

        if gen_entry:
            gen_data.append(gen_entry)
        else:
            skipped_gen += 1



    for path, data in [

        (qr_output, qr_data),

        (sel_output, sel_data),

        (gen_output, gen_data),

    ]:

        output_path = Path(path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )


    print("\n=== DONE ===")

    print(
        f"qr_sft_data.json  : "
        f"{len(qr_data)} entries "
        f"-> {qr_output}"
    )

    print(
        f"sel_sft_data.json : "
        f"{len(sel_data)} entries "
        f"(skipped: {skipped_sel}) "
        f"-> {sel_output}"
    )

    print(
        f"gen_sft_data.json : "
        f"{len(gen_data)} entries "
        f"(skipped: {skipped_gen}) "
        f"-> {gen_output}"
    )