import sys
import os
import re
import csv
from time import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.CONFIG import CONFIG
from src.models.graph.v1_graph import Agent, build_graph
from src.models.LLM.v1_LLM import AgentManager

import streamlit as st

import chromadb
from chromadb.utils import embedding_functions


@st.cache_resource
def get_collection(embedding_model_name, collection_name):
    client = chromadb.PersistentClient(path='data/chroma_db')

    embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)

    collection = client.get_collection(name=collection_name, embedding_function=embedding_model)

    return collection

def build_chat_history(messages):
    history = ""
    for msg in messages[-6:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"
    return history


def parse_metrics(metrics_text): 
    def extract(metric_name):
        match = re.search(
            rf"{metric_name}\s*:\s*(\d+)\s*/\s*10",
            metrics_text,
            re.IGNORECASE
        )
        return int(match.group(1)) if match else None

    return {
        "faithfulness": extract("Faithfulness"),
        "relevance": extract("Relevance"),
        "completeness": extract("Completeness")
    }


def save_to_csv(file_path, row_dict):
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["model_name", "faithfulness", "relevance", "completeness", "latency"]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(row_dict)



st.set_page_config(page_title="SRA+ MINI PROJECT #1", layout='wide')
st.title("Khotbah GRII Q&A")

# Debug Toggle
debug_mode = st.sidebar.checkbox("🧠 Enable Debug Mode", value=False)
st.session_state["debug_mode"] = debug_mode

# Init
collection = get_collection(
    embedding_model_name=CONFIG['EMBEDDING_MODEL_NAME_BGE'],
    collection_name=CONFIG['COLLECTION_NAME_BGE']
)

manager = AgentManager()
agent = Agent(collection=collection, rewrite_llm=manager.get_rewrite_model(), reasoning_llm=manager.get_reasoning_model(), evaluator_llm=manager.get_evaluator_model())
graph = build_graph(agent=agent)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# Input
if prompt := st.chat_input("Ask something about the preaching in GRII..."):
    st.session_state.messages.append({
        'role': 'user',
        'content': prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        with st.spinner("Thinking..."):
            start_time = time()

            result = graph.invoke({
                'query': prompt,
                'chat_history': build_chat_history(st.session_state.messages)
            })

            end_time = time()
            latency = end_time - start_time

            # Stream answer
            for chunk in manager.get_reasoning_model().stream(result['answer']):
                token = chunk.content
                full_response += token
                placeholder.markdown(full_response)

            # Append evaluation
            # Parse evaluation metrics
            parsed = parse_metrics(result['metrics'])

            # Save to CSV
            save_to_csv(
                file_path=CONFIG['CSV_RESULTS_FILEPATH'],
                row_dict={
                    "model_name": CONFIG['LLM_MODEL_NAME'],
                    "faithfulness": parsed["faithfulness"],
                    "relevance": parsed["relevance"],
                    "completeness": parsed["completeness"],
                    "latency": round(latency, 4)
                }
            )

            # Append evaluation to UI
            full_response += (
                "\n\n---\n"
                "### 📊 Evaluation\n" + result['metrics'] +
                "\n\n### ⏱️ Latency\n"
                f"{latency:.2f} seconds"
            )
            placeholder.markdown(full_response)

    st.session_state.messages.append({
        'role': 'assistant',
        'content': full_response
    })

# Debug Panel
if st.session_state.get("debug_mode", False) and "debug_state" in st.session_state:
    with st.expander("🧠 Debug State (Click to expand)", expanded=False):
        state = st.session_state["debug_state"]

        st.markdown("### 🔍 Query")
        st.code(state.get('query', ''), language="text")

        st.markdown("### ✏️ Rewritten Query")
        st.code(state.get('rewritten_query', ''), language="text")

        st.markdown("### 📚 Retrieved Docs")
        for i, doc in enumerate(state.get('retrieved_docs', [])):
            st.markdown(f"**Doc {i+1}:**")
            st.code(doc[:500] + "..." if len(doc) > 500 else doc)

        st.markdown("### 🧾 Metadatas")
        st.json(state.get('metadatas', []))

        st.markdown("### 🧠 Context")
        ctx = state.get('context', '')
        st.code(ctx[:1000] + "..." if len(ctx) > 1000 else ctx)

        st.markdown("### 🧩 Analysis")
        st.code(state.get('analysis', ''), language="text")

        st.markdown("### 💬 Answer")
        st.code(state.get('answer', ''), language="text")

        st.markdown("### 📊 Metrics")
        st.code(state.get('metrics', ''), language="text")