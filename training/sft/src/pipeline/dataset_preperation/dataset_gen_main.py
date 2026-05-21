import json
from tqdm import tqdm

from src.models.graph.dataset_gen_graph import build_graph
from src.utils.CONFIG import CONFIG
from src.tools.log_json import JSONLLogger

from src.tools.load_documents import load_documents_from_processed
from src.models.graph.dataset_gen_graph import sliding_window_function


def write_jsonl(path, obj):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    documents = load_documents_from_processed(CONFIG['DATA_FILEPATH'])

    chunks = []
    for doc_id, doc in documents.items():
        for chunk in sliding_window_function(doc["text"]):
            chunks.append(chunk)

    total_chunks = len(chunks)
    print(f"There are {total_chunks} chunks to be processed")
    total = total_chunks * 2

    graph = build_graph()

    state = {}

    logger = JSONLLogger(CONFIG["DEBUG_FILEPATH"])

    jsonl_path = CONFIG["DEBUG_FILEPATH"]

    pbar = tqdm(desc="Generating dataset", total=total)

    for event in graph.stream(state):

        for node_name, output in event.items():
            # tqdm.write(f"Node: {node_name}")

            logger.log(node=node_name, state=output)

            if node_name == "save_row":
                pbar.update(1)

            if node_name == "save_row" and output.get("dataset"):
                write_jsonl(jsonl_path, output["dataset"][-1])

            # dynamic label
            if node_name == "select_chunk":
                pbar.set_description(f"Chunk {output.get('chunk_idx', '?')}")

            if node_name == "select_question":
                pbar.set_description(f"Q {output.get('question_idx', '?')}")


    pbar.close()

    print("\nDataset generation done.")