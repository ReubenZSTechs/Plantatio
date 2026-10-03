"""The LangGraph agent and the record formatting it depends on."""

import pytest

from backend.pipelines.main.nodes.nodes import (
    answer_generation_node,
    format_graph_record,
    reasoning_node,
    sub_question_generator_node,
)


def test_scalar_columns_are_kept():
    """Aggregate queries used to produce an empty context: only dicts and
    lists were rendered, so counts and names were silently dropped."""
    assert format_graph_record({"count(n)": 42}) == "count(n): 42"
    assert format_graph_record({"name": "Early blight"}) == "name: Early blight"


def test_node_labels_render_without_python_list_syntax():
    """`_labels` is a list; it used to be interpolated as "(['DISEASE'])"."""
    rendered = format_graph_record({"d": {"_labels": ["DISEASE"], "name": "Early blight"}})

    assert rendered == "d: (DISEASE) Early blight"
    assert "[" not in rendered


def test_multiple_labels_are_joined():
    rendered = format_graph_record({"n": {"_labels": ["PLANT", "CROP"], "name": "Tomato"}})

    assert rendered == "n: (PLANT|CROP) Tomato"


def test_none_values_are_skipped():
    assert format_graph_record({"missing": None, "kept": "value"}) == "kept: value"


def test_sub_questions_fall_back_to_the_original_query(monkeypatch):
    """A model that ignores the output format must not yield zero retrieval."""
    from backend.pipelines.main.nodes import nodes

    class Unformatted:
        def generate(self, prompt, **_):
            return "I will not use bullet points."

    monkeypatch.setattr(nodes, "subq_llm", lambda: Unformatted())

    result = nodes.sub_question_generator_node({"user_query": "Why are leaves yellow?"})

    assert result["sub_questions"] == ["Why are leaves yellow?"]


def test_reasoning_states_when_the_graph_was_empty(monkeypatch):
    """An empty retrieval should be acknowledged, not silently reasoned over."""
    from backend.pipelines.main.nodes import nodes

    captured = {}

    class Capturing:
        def generate(self, prompt, **_):
            captured["prompt"] = prompt
            return "reasoned"

    monkeypatch.setattr(nodes, "reasoning_llm", lambda: Capturing())

    nodes.reasoning_node({"user_query": "q", "retrieved_docs": []})

    assert "No matching facts" in captured["prompt"]


def test_graph_runs_end_to_end_with_stubs(client):
    """The whole agent executes against injected fakes, in node order."""
    response = client.post(
        "/api/b2c/chat",
        json={"messages": [{"role": "user", "content": "Brown spots on leaves?"}]},
    )

    assert response.status_code == 200
    assert response.json()["provenance"]["recordCount"] >= 1
