import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

import streamlit as st
import time

from src.models.graph.v2_graph import Agent, build_graph
from src.utils.CONFIG import CONFIG

import chromadb
from chromadb.utils import embedding_functions


if "messages" not in st.session_state:
    st.session_state.messages = []

if "debug_state" not in st.session_state:
    st.session_state.debug_state = {}

if "current_node" not in st.session_state:
    st.session_state.current_node = "Idle"

if "current_node_desc" not in st.session_state:
    st.session_state.current_node_desc = "Idle"


NODE_DESCRIPTIONS = {
    "refine_prompt": "Refining your query...",
    "analyze_prompt": "Understanding intent...",
    "generate_cot_steps": "Planning reasoning steps...",
    "generate_sub_questions": "Breaking down the problem...",
    "analyze_entity": "Extracting key entities...",
    "fuse_entity": "Aligning reasoning units...",
    "evaluate_fuse_entity": "Scoring reasoning units...",
    "filter_reasoning_units": "Filtering high-confidence reasoning...",
    "retrieve_data": "Retrieving relevant documents...",
    "build_context": "Building structured context...",
    "data_formatter": "Extracting factual points...",
    "increment_times_debate": "Preparing debate iteration...",
    "debate_1": "Building argument...",
    "debate_2": "Critically analyzing...",
    "debate_3": "Structuring insights...",
    "store_answers": "Collecting debate outputs...",
    "check_correlation": "Checking agreement across agents...",
    "generate_answer": "Generating final answer...",
    "evaluation": "Evaluating answer quality...",
    "print_state": "Finalizing state..."
}


@st.cache_resource
def get_collection(embedding_model_name, collection_name):
    client = chromadb.PersistentClient(path='data/chroma_db')

    embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_model_name
    )

    collection = client.get_collection(
        name=collection_name,
        embedding_function=embedding_model
    )

    return collection


collection = get_collection(
    embedding_model_name=CONFIG['EMBEDDING_MODEL_NAME_SENTENCEBERT'],
    collection_name=CONFIG['COLLECTION_NAME_SENTENCEBERT']
)

agent_graph = build_graph(agent=Agent(collection))


st.title("Multi-Agent Khobat Q&A App")

with st.sidebar:
    st.title("Controls")

    show_state = st.checkbox("Show State")

    st.markdown("---")
    st.page_link("pages/dashboard.py", label="Dashboard")
    st.page_link("pages/logs.py", label="Logs")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        progress_bar = st.progress(0)
        status = st.empty()

        def update_progress():
            node = st.session_state.get("current_node", "Processing...")
            desc = NODE_DESCRIPTIONS.get(node, node)
            status.markdown(f"🔄 {desc}")
            # progress_bar.progress(min(step_idx / total_steps, 1.0))

        state = {
            "initial_query": prompt,
            "refined_query": "",
            "user_context": {},

            "cot_steps": [],
            "sub_questions": [],

            "entity_metadata": [],
            "reasoning_units": [],

            "retrieved_docs": [],
            "metadatas": [],
            "context": "",
            "point_of_facts": [],

            "debator_1_argument": {},
            "debator_2_argument": {},
            "debator_3_argument": {},

            "argument_debate": {},
            "correlation_result": {},
            "debate_context": [],

            "answer": "",
            "metrics": {},

            "times_debate": 0
        }

        current_state = state.copy()
        final_state = None
        step_counter = 0

        for step in agent_graph.stream(state):
            for node_name, update in step.items():
                current_state.update(update)

            st.session_state.debug_state = current_state.copy()

            final_state = current_state
            step_counter += 1
            update_progress()
            time.sleep(0.02)

        if final_state is None:
            answer = "Something went wrong."
        else:
            answer = final_state.get("answer", "No answer generated.")

        streamed_text = ""
        for char in answer:
            streamed_text += char
            placeholder.markdown(streamed_text)
            time.sleep(0.005)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })


if show_state:
    st.sidebar.subheader("🧪 State Debug")

    state = st.session_state.get("debug_state", {})

    if state:
        key = st.sidebar.selectbox("Select State Key", list(state.keys()))
        value = state.get(key)

        if isinstance(value, dict):
            st.sidebar.json(value)

        elif isinstance(value, list):
            st.sidebar.write(value)

        elif isinstance(value, str):
            st.sidebar.text_area("Value", value, height=200)

        else:
            st.sidebar.write(value)