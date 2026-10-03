"""Shared fixtures: an API client backed by stub models and a stub graph.

The real agent needs multi-gigabyte weights and a live Neo4j instance, so the
tests inject fakes at the two seams the pipeline exposes — LLMManager.inject
and TextToCypherPipeline(llm=..., handler=...).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "api"))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_plantatio.db")
os.environ.setdefault("PLANTATIO_LLM_MODEL_ID", "stub/model")


class StubLLM:
    """Returns canned completions keyed off what the prompt asks for."""

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str, **_kwargs) -> str:
        self.prompts.append(prompt)

        if "query decomposition" in prompt:
            return "- What causes yellowing leaves?\n- What causes brown spots?"
        if "Cypher" in prompt or "cypher" in prompt:
            return '{"cypher": "MATCH (d:DISEASE) RETURN d LIMIT 5", "return_type": "graph", "params": {}}'
        if "reasoning agent" in prompt:
            return "Yellowing with brown spots is consistent with early blight."
        return "Remove affected leaves and apply a copper-based fungicide."

    def invoke(self, prompt: str) -> str:
        return self.generate(prompt)


class StubRecord:
    """Mimics the parts of neo4j.Record the serializer relies on."""

    def __init__(self, row: dict) -> None:
        self._row = row

    def keys(self):
        return self._row.keys()

    def __getitem__(self, key):
        return self._row[key]

    def data(self):
        return self._row


class StubNeo4jHandler:
    """Stands in for a live graph, returning one fixed record."""

    def __init__(self) -> None:
        self.database = "stub"
        self.driver = None
        self.closed = False

    def connect(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    def get_neo4j_schema(self):
        return [StubRecord({
            "nodes": [{"name": "DISEASE"}, {"name": "PLANT"}],
            "relationships": [({"name": "PLANT"}, "AFFECTED_BY", {"name": "DISEASE"})],
        })], None, None

    def execute_query(self, query, parameters=None):
        return [StubRecord({"d": {"_labels": ["DISEASE"], "name": "Early blight"}})], None, None


@pytest.fixture
def stub_llm() -> StubLLM:
    return StubLLM()


@pytest.fixture
def client(stub_llm, monkeypatch):
    """A TestClient whose agent runs against the stub model and stub graph."""
    from fastapi.testclient import TestClient

    from backend.pipelines.main.nodes import nodes
    from RAG.GRAPHRAG.src.pipeline.rag.text_to_cypher import TextToCypherPipeline

    pipeline = TextToCypherPipeline(llm=stub_llm, handler=StubNeo4jHandler())
    pipeline.connected = True

    nodes.get_retrieval_pipeline.cache_clear()
    monkeypatch.setattr(nodes, "get_retrieval_pipeline", lambda: pipeline)
    monkeypatch.setattr(nodes, "subq_llm", lambda: stub_llm)
    monkeypatch.setattr(nodes, "reasoning_llm", lambda: stub_llm)
    monkeypatch.setattr(nodes, "answer_llm", lambda: stub_llm)
    nodes.get_graph_app.cache_clear()

    import app.app as app_module

    with TestClient(app_module.app) as test_client:
        yield test_client
