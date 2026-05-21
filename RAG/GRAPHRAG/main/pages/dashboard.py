import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import streamlit as st
import pandas as pd
from src.utils.CONFIG import CONFIG

@st.cache_data
def load_logs():
    llm_df = pd.read_json(CONFIG['LOGFILE'], lines=True)
    llm_df["type"] = "llm"

    node_df = pd.read_json(CONFIG['NODE_LOGS'], lines=True)
    node_df["type"] = "node"

    return pd.concat([llm_df, node_df], ignore_index=True)

df = load_logs()

st.title("📊 LLM System Dashboard")

if df.empty:
    st.warning("No logs found")
    st.stop()

# Split logs
node_df = df[df["type"] == "node"]
llm_df = df[df["type"] == "llm"]

# ===== Metrics =====
st.subheader("System Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Calls", len(df))
col2.metric("Node Calls", len(node_df))
col3.metric("LLM Calls", len(llm_df))

# ===== Latency =====
st.subheader("Latency")

if not node_df.empty:
    st.line_chart(node_df["latency"])

# ===== Recent Calls =====
st.subheader("🧠 Recent Node Calls")
st.dataframe(node_df.tail(5)[["timestamp", "node_name", "latency", "success"]])

st.subheader("🤖 Recent LLM Calls")
st.dataframe(llm_df.tail(5)[["timestamp", "function", "total_latency", "tokens_generated"]])