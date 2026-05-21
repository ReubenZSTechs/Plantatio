import json
import os
from dotenv import load_dotenv
load_dotenv()
import csv

from training.utils.PROMPT_TEMPLATES import generate_question_dataset_prompt, generate_accepted_subquestion_dataset_prompt, generate_rejected_subquestion_dataset_prompt, generate_rejected_answer_dataset_prompt, generate_accepted_answer_dataset_prompt
from training.experiments.dataset_gen.dataset_gen_state import DatasetState
from training.preprocessing.load_documents import load_documents_from_folder
from training.decorators.log_json import JSONLLogger

from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=int(os.getenv('CHUNKING_CHARACTERS')),
    chunk_overlap=int(os.getenv('OVERLAP_CHARACTERS')),
    length_function=len,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)

llm_model = ChatOllama(
    model=os.getenv("DATASET_GEN_MODEL"),
    temperature=0.3
)

def safe_parse_list(text: str):
    try:
        return json.loads(text)
    except:
        return []
    

def sliding_window_function(text):
    chunks = text_splitter.split_text(text)

    # optional filtering
    chunks = [
        chunk for chunk in chunks
        if len(chunk.split()) >= 80
    ]

    return chunks


def prepare_documents_node(state: DatasetState):
    documents = load_documents_from_folder(os.getenv('TXT_PAPERS_FILEPATH'))
    
    return {
        'documents': documents
    }


def chunk_documents_node(state: DatasetState):
    all_chunks = []

    for doc_id, doc in state['documents'].items():
        text = doc['text']
        for i, chunk in enumerate(sliding_window_function(text)):
            data = {
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_{i}",
                "text": chunk
            }
            all_chunks.append(data)

            with open(os.getenv('CHUNKS_FILEPATH'), "a", encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')

    return {
        **state,
        "chunks": all_chunks,
        "chunk_idx": 0,
        "dataset": []
    }

def select_chunk_node(state: DatasetState):

    chunk = state["chunks"][state["chunk_idx"]]

    return {
        **state,
        "current_chunk": chunk,
        "question_idx": 0,
        "questions": []
    }

def generate_questions_node(state: DatasetState):
    chunk = state.get("current_chunk")

    if not chunk:
        raise ValueError("current_chunk is missing in state")

    chunk_text = chunk["text"]

    prompt = generate_question_dataset_prompt(chunk_text)
    raw = llm_model.invoke(prompt).content

    questions = safe_parse_list(raw)

    return {
        "questions": questions
    }


def select_question_node(state):

    idx = state["question_idx"]
    questions = state["questions"]

    if idx >= len(questions):
        return {"current_question": None}

    return {
        "current_question": questions[idx]
    }


def generate_accepted_subquestions_node(state: DatasetState):
    q = state.get("current_question")
    if not q:
        return {"accepted_sub_questions": []}

    prompt = generate_accepted_subquestion_dataset_prompt(q)
    raw = llm_model.invoke(prompt).content

    return {
        "accepted_sub_questions": safe_parse_list(raw)
    }


def generate_rejected_subquestions_node(state: DatasetState):
    q = state.get("current_question")
    if not q:
        return {"rejected_sub_questions": []}

    prompt = generate_rejected_subquestion_dataset_prompt(q)
    raw = llm_model.invoke(prompt).content

    return {
        "rejected_sub_questions": safe_parse_list(raw)
    }


def generate_accepted_answer_node(state: DatasetState):
    chunk_text = state["current_chunk"]["text"]
    question = state["current_question"]

    prompt = generate_accepted_answer_dataset_prompt(
        question,
        documents=[chunk_text]   # IMPORTANT: ONLY THIS CHUNK
    )

    answer = llm_model.invoke(prompt).content

    return {
        "accepted_answer": answer,
        "final_docs": [state["current_chunk"]["chunk_id"]]
    }


def generate_rejected_answer_node(state: DatasetState):
    chunk_text = state["current_chunk"]["text"]
    question = state["current_question"]

    prompt = generate_rejected_answer_dataset_prompt(
        question,
        documents=[chunk_text]   # IMPORTANT: ONLY THIS CHUNK
    )

    answer = llm_model.invoke(prompt).content

    return {
        "rejected_answer": answer
    }


def save_row_node(state: DatasetState):
    if not state.get("accepted_answer") or state["accepted_answer"].strip() == "I do not know the answer":
        return {}
    
    if not state.get("rejected_answer") or state["rejected_answer"].strip() == "I do not know the answer":
        return {}

    accepted_subs = state.get("accepted_sub_questions", [])[:3]
    accepted_subs += [""] * (3 - len(accepted_subs))

    rejected_subs = state.get("rejected_sub_questions", [])[:3]
    rejected_subs += [""] * (3 - len(rejected_subs))

    row = {
        "main_question": state["current_question"],
        "accepted_answer": state["accepted_answer"],
        "rejected_answer": state["rejected_answer"],
        "document_selected": state["current_chunk"]["chunk_id"],
        "accepted_sub_question_1": accepted_subs[0],
        "accepted_sub_question_2": accepted_subs[1],
        "accepted_sub_question_3": accepted_subs[2],
        "rejected_sub_question_1": rejected_subs[0],
        "rejected_sub_question_2": rejected_subs[1],
        "rejected_sub_question_3": rejected_subs[2],
    }

    os.makedirs(os.path.dirname(os.getenv('CSV_FILEPATH')), exist_ok=True)

    file_exists = os.path.isfile(os.getenv('CSV_FILEPATH'))

    with open(os.getenv('CSV_FILEPATH'), "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)

    dataset = state.get("dataset", [])
    dataset.append(row)

    return {"dataset": dataset}


def next_question_node(state: DatasetState):
    return {"question_idx": state["question_idx"] + 1}


def next_chunk_node(state: DatasetState):
    return {"chunk_idx": state["chunk_idx"] + 1}


def route_questions(state: DatasetState):
    if state["question_idx"] < len(state["questions"]):
        return "select_question"
    return "next_chunk"


def route_chunks(state: DatasetState):
    if state["chunk_idx"] < len(state["chunks"]):
        return "select_chunk"
    return "end"


def build_graph():
    builder = StateGraph(state_schema=DatasetState)

    builder.add_node("prepare_documents", prepare_documents_node)
    builder.add_node("chunk_documents", chunk_documents_node)
    builder.add_node("select_chunk", select_chunk_node)

    builder.add_node("generate_questions", generate_questions_node)
    builder.add_node("select_question", select_question_node)

    builder.add_node("generate_accepted_subquestions", generate_accepted_subquestions_node)
    builder.add_node("generate_rejected_subquestions", generate_rejected_subquestions_node)

    builder.add_node("generate_accepted_answer", generate_accepted_answer_node)
    builder.add_node("generate_rejected_answer", generate_rejected_answer_node)

    builder.add_node("save_row", save_row_node)
    builder.add_node("next_question", next_question_node)
    builder.add_node("next_chunk", next_chunk_node)


    builder.set_entry_point("prepare_documents")

    builder.add_edge("prepare_documents", "chunk_documents")
    builder.add_edge("chunk_documents", "select_chunk")
    builder.add_edge("select_chunk", "generate_questions")

    builder.add_edge("generate_questions", "select_question")

    builder.add_conditional_edges(
        "select_question",
        route_questions,
        {
            "select_question": "generate_accepted_subquestions",
            "next_chunk": "next_chunk"
        }
    )

    builder.add_edge("generate_accepted_subquestions", "generate_accepted_answer")
    builder.add_edge("generate_accepted_answer", "generate_rejected_subquestions")
    builder.add_edge("generate_rejected_subquestions", "generate_rejected_answer")
    builder.add_edge("generate_rejected_answer", "save_row")
    builder.add_edge("save_row", "next_question")

    builder.add_conditional_edges(
        "next_question",
        route_questions,
        {
            "select_question": "select_question",
            "next_chunk": "next_chunk"
        }
    )

    builder.add_conditional_edges(
        "next_chunk",
        route_chunks,
        {
            "select_chunk": "select_chunk",
            "end": END
        }
    )

    return builder.compile()