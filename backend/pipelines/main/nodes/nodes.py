"""LangGraph nodes implementing the Plantatio GraphRAG agent.

The graph runs: decompose the query into sub-questions, retrieve matching
knowledge from Neo4j via text-to-Cypher, reason over what came back, then
write the final answer. The compiled graph is built lazily so importing this
module never loads model weights or opens a database connection.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from langgraph.graph import END, StateGraph

from backend.pipelines.agents.agents import answer_llm, reasoning_llm, subq_llm
from backend.pipelines.main.state.GraphState import GraphState
from RAG.GRAPHRAG.src.pipeline.rag.text_to_cypher import TextToCypherPipeline

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_retrieval_pipeline() -> TextToCypherPipeline:
    """Return the process-wide text-to-Cypher pipeline.

    Cached because each instance opens its own Neo4j driver; building one per
    request leaked a connection every time a user sent a message.
    """
    return TextToCypherPipeline()


def close_retrieval_pipeline() -> None:
    """Close the shared pipeline's driver. Called on application shutdown."""
    cache_info = getattr(get_retrieval_pipeline, "cache_info", None)
    if cache_info is not None and not cache_info().currsize:
        return

    try:
        handler = getattr(get_retrieval_pipeline(), "handler", None)
        if handler is not None:
            handler.close()
    except Exception:
        logger.warning("Could not close the graph connection cleanly.", exc_info=True)
    finally:
        clear = getattr(get_retrieval_pipeline, "cache_clear", None)
        if clear is not None:
            clear()


def _format_value(key: str, value: Any) -> str | None:
    """Render one Cypher result value as a single readable line."""
    if isinstance(value, dict):
        labels = value.get("_labels") or ["Unknown"]
        # _labels arrives as a list; join it rather than str()-ing the list,
        # which used to render as "(['Entity'])".
        label = "|".join(labels) if isinstance(labels, (list, tuple, set)) else str(labels)
        name = value.get("name", "")
        return f"{key}: ({label}) {name}".rstrip()

    if isinstance(value, (list, tuple)):
        parts = [_format_value(key, item) for item in value]
        return "\n".join(part for part in parts if part)

    if value is None:
        return None

    # Scalar columns were previously dropped entirely, so any aggregate query
    # (counts, names, averages) produced an empty context.
    return f"{key}: {value}"


def format_graph_record(record: dict) -> str:
    """Render a Cypher result row as text the model can read."""
    lines = [_format_value(key, value) for key, value in record.items()]
    return "\n".join(line for line in lines if line)


def sub_question_generator_node(state: GraphState) -> dict:
    """Break the user's question into retrievable sub-questions."""
    query = state["user_query"]

    prompt = f"""You are a query decomposition system for a plant-science assistant.

Break the following user query into smaller, self-contained sub-questions that
can each be answered from an agronomy knowledge graph.

User Query:
{query}

Return only the sub-questions, one per line, each starting with "- ".
"""

    response = subq_llm().generate(prompt)

    sub_questions = [
        line.lstrip("-").strip()
        for line in response.splitlines()
        if line.strip().startswith("-")
    ]

    # Always retrieve something, even if the model ignored the output format.
    if not sub_questions:
        sub_questions = [query]

    logger.info("Decomposed query into %d sub-question(s).", len(sub_questions))
    return {"sub_questions": sub_questions}


def retrieval_rag_node(state: GraphState) -> dict:
    """Query the knowledge graph for each sub-question."""
    pipeline = get_retrieval_pipeline()

    all_records: list[dict] = []
    retrieved_context: list[str] = []

    for question in state["sub_questions"]:
        try:
            result = pipeline.query(question)
        except Exception:
            logger.exception("Graph retrieval failed for sub-question %r.", question)
            continue

        records = result.get("records", [])
        all_records.extend(records)

        for record in records:
            formatted = format_graph_record(record)
            if formatted:
                retrieved_context.append(formatted)

    logger.info("Retrieved %d graph record(s).", len(all_records))
    return {"retrieved_docs": retrieved_context, "graph_records": all_records}


def reasoning_node(state: GraphState) -> dict:
    """Reason step by step over the retrieved graph knowledge."""
    context = "\n\n".join(state["retrieved_docs"])

    if not context:
        context = "(No matching facts were found in the knowledge graph.)"

    prompt = f"""You are an expert agricultural reasoning agent.

USER QUESTION:
{state["user_query"]}

GRAPH KNOWLEDGE:
{context}

Reason step by step using only the graph knowledge above. If the knowledge is
insufficient, say so explicitly rather than guessing.
"""

    return {"reasoning_output": reasoning_llm().generate(prompt)}


def answer_generation_node(state: GraphState) -> dict:
    """Write the grower-facing answer from the reasoning trace."""
    prompt = f"""You are Plantatio's growing assistant.

USER QUERY:
{state["user_query"]}

REASONING:
{state["reasoning_output"]}

Write a concise, practical answer for the grower. Be specific about what to do
next. If the reasoning found no supporting evidence, say that plainly.
"""

    return {"final_answer": answer_generation_cleanup(answer_llm().generate(prompt))}


def answer_generation_cleanup(answer: str) -> str:
    """Strip stray formatting a chat model sometimes wraps answers in."""
    return answer.strip().strip("`").strip()


def build_graph() -> StateGraph:
    """Wire the agent's nodes into a compiled LangGraph application."""
    graph = StateGraph(GraphState)

    graph.add_node("sub_question_generator", sub_question_generator_node)
    graph.add_node("retrieval_rag_module", retrieval_rag_node)
    graph.add_node("reasoning", reasoning_node)
    graph.add_node("answer_generation", answer_generation_node)

    graph.set_entry_point("sub_question_generator")
    graph.add_edge("sub_question_generator", "retrieval_rag_module")
    graph.add_edge("retrieval_rag_module", "reasoning")
    graph.add_edge("reasoning", "answer_generation")
    graph.add_edge("answer_generation", END)

    return graph.compile()


@lru_cache(maxsize=1)
def get_graph_app():
    """Return the compiled agent, building it on first use."""
    return build_graph()
