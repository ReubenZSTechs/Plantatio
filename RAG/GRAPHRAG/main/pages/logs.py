import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.utils.CONFIG import CONFIG

import streamlit as st
import pandas as pd

@st.cache_data
def load_logs():
    llm_df = pd.read_json(CONFIG['LOGFILE'], lines=True)
    llm_df["type"] = "llm"

    node_df = pd.read_json(CONFIG['NODE_LOGS'], lines=True)
    node_df["type"] = "node"

    return pd.concat([llm_df, node_df], ignore_index=True)

df = load_logs()

st.title("📜 Logs Viewer")

log_type = st.selectbox("Type", ["All", "node", "llm"])

copy_df = df.copy()

if log_type != "All":
    copy_df = copy_df[copy_df["type"] == log_type]

st.dataframe(copy_df.tail(50))

st.subheader("Inspect Log")

selected = st.selectbox("Select Entry", copy_df.index)

row = copy_df.loc[selected]

st.json(row.to_dict())

if row.get("type") == "llm":
    st.write("### Prompt")
    st.code(row.get("prompt", ""))

    st.write("### Raw Output")
    st.code(row.get("raw_output", ""))

    st.write("### Cleaned Output")
    st.code(row.get("cleaned_output", ""))

    st.write("### Parsed Output")
    st.code(row.get("parsed_output", ""))

    st.write("### JSON Valid")
    st.write(row.get("valid_json", False))

    if row.get("clean_error"):
        st.write("### Clean Error")
        st.code(row.get("clean_error"))