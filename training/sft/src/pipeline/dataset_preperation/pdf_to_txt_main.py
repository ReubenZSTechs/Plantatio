import requests
import json
import os
from typing import TypedDict, List, Optional, Dict, Any
import fitz

from time import time, sleep
from tqdm import tqdm

from src.models.state.pdf_to_txt_state import GraphState
from src.utils.CONFIG import CONFIG
from src.models.graph.pdf_to_txt_graph import build_graph


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        text = []

        for page in doc:
            text.append(page.get_text())

        return "\n".join(text)
    except:
        return ""
    

def save_text_file(arxiv_id: str, text: str) -> str:
    txt_path = os.path.join(f"{CONFIG['DATA_FILEPATH']}/txt", f"{arxiv_id}.txt")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    return txt_path                                                                                                                                       

def append_result_to_jsonl(file_path: str, data: dict):
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")


def jsonl_to_json(jsonl_path, json_path):
    data = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)



def process_arxiv_dataset(json_path: str, graph, output_path: str, limit: int = None):
    results = []
    scanned = 0

    with open(json_path, "r") as f:
        iterator = tqdm(f, desc="Processing arXiv")

        for line in iterator:
            if limit and len(results) >= limit:
                break

            scanned += 1

            iterator.set_postfix({
                "processed": scanned,
                "accepted": len(results),
                "rejected": scanned - len(results),
                "rate": f"{len(results)/scanned:.2f}" if scanned > 0 else "0"
            })


            try:
                paper = json.loads(line)
            except:
                continue

            arxiv_id = paper.get("id", "")
            title = paper.get("title", "").strip()
            abstract = paper.get("abstract", "").strip()
            categories_str = paper.get("categories", "")

            if not abstract:
                continue

            # YEAR FILTER
            year = extract_year_from_versions(paper)

            if year < CONFIG['YEAR_FILTER']:
                tqdm.write(f"⏩ Skipped (year={year}) | {arxiv_id}")
                continue

            # PREFILTER
            if not cheap_prefilter(title, abstract):
                tqdm.write(f"⏩ Skipped (prefilter) | {arxiv_id} | year={year}")
                continue

            # KEYWORDS
            category_keywords = [
                c.lower().replace(".", " ")
                for c in categories_str.split()
            ]

            title_keywords = [
                w.lower()
                for w in title.split()
                if len(w) > 4
            ]

            keywords = category_keywords + title_keywords

            tqdm.write(f"\nChecking {arxiv_id} | year={year} | Title: {title}")
            tqdm.write(f"Keywords: {keywords}")

            state = {
                "keywords": keywords,
                "abstract": abstract
            }

            # GRAPH INVOCATION
            result = graph.invoke(state)

            source = result.get("decision_source", "unknown")

            # MULTI-LABEL DECISION
            is_relevant = (
                result.get("is_rag") or
                result.get("is_rl") or
                result.get("is_langgraph")
            )

            confidence_dict = result.get("confidence", {})

            max_conf = max(
                confidence_dict.get("rag", 0.0),
                confidence_dict.get("rl", 0.0),
                confidence_dict.get("langgraph", 0.0)
            )

            # LABEL STRING
            labels = []
            if result.get("is_rag"):
                labels.append("RAG")
            if result.get("is_rl"):
                labels.append("RL")
            if result.get("is_langgraph"):
                labels.append("LangGraph")

            label_str = ",".join(labels) if labels else "None"

            # REJECT
            if not is_relevant or max_conf < CONFIG["CONFIDENCE_THRESHOLD"]:
                tqdm.write(
                    f"✘ Rejected [{label_str}] | source={source} | max_conf={max_conf:.2f} | "
                    f"(rag={confidence_dict.get('rag',0):.2f}, "
                    f"rl={confidence_dict.get('rl',0):.2f}, "
                    f"langgraph={confidence_dict.get('langgraph',0):.2f}) "
                    f"| year={year}"
                )
                continue

            # ACCEPT
            tqdm.write(
                f"✔ Accepted [{label_str}] | source={source} | max_conf={max_conf:.2f} | "
                f"(rag={confidence_dict.get('rag',0):.2f}, "
                f"rl={confidence_dict.get('rl',0):.2f}, "
                f"langgraph={confidence_dict.get('langgraph',0):.2f}) "
                f"| year={year} → downloading..."
            )

            # DOWNLOAD
            pdf_path = download_arxiv_pdf(arxiv_id)

            if not pdf_path:
                tqdm.write("⚠ Failed to download PDF")
                continue

            text = extract_text_from_pdf(pdf_path)

            if not text.strip():
                tqdm.write("⚠ Empty text extracted")
                continue

            txt_path = save_text_file(arxiv_id, text)

            # STORE
            result_entry = {
                "id": arxiv_id,
                "title": title,
                "categories": categories_str,
                "year": year,
                "labels": labels,
                "confidence": confidence_dict,
                "explanation": result.get("explanation", "")[:500],  # truncate optional
                "decision_source": source,
                "txt_path": txt_path
            }

            # Append to file immediately
            append_result_to_jsonl(output_path, result_entry)

            # Keep in memory (optional)
            results.append(result_entry)

            tqdm.write(f"✔ Saved to {txt_path}")
            sleep(0.3)

    tqdm.write("\nFinished processing dataset.")
    return results





if __name__ == "__main__":
    # Build langgraph
    graph = build_graph(GraphState)

    # Run pipeline
    results = process_arxiv_dataset(
        json_path=CONFIG['RAW_DATA'],
        graph=graph,
        output_path=CONFIG['TEMP_JSON_LOGS_FILEPATH'],
        limit=CONFIG['NUM_DOCUMENTS']
    )

    jsonl_to_json(jsonl_path=CONFIG['TEMP_JSON_LOGS_FILEPATH'], json_path=CONFIG['JSON_SELECTION_FILEPATH'])

    print(f"Saved {len(results)} papers.")