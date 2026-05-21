import json
import os
from dotenv import load_dotenv

load_dotenv()

from datetime import datetime


class JSONLLogger:
    def __init__(self, path=os.getenv("DEBUG_FILEPATH_NODE")):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def log(self, node: str, state: dict):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "node": node,

            # core identifiers (safe extraction)
            "chunk_idx": state.get("chunk_idx"),
            "question_idx": state.get("question_idx"),

            "chunk_id": (
                state.get("current_chunk", {}) or {}
            ).get("chunk_id"),

            "question": state.get("current_question"),

            # optional debugging metadata
            "num_questions": len(state.get("questions", [])) if state.get("questions") else None,

            # # 🔥 important for debugging LangGraph behavior
            # "raw_state": state
        }

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")