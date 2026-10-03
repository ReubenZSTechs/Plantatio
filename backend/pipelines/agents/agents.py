"""Role-scoped accessors for the agent's language model.

Every node in the graph shares one set of weights, loaded on first use by
``LLMManager``. These helpers exist so nodes can ask for a model tuned to
their role without knowing how it is loaded, and so importing this module
costs nothing — previously it loaded roughly 40 GB of checkpoints at import
time, which prevented the API from starting at all.
"""

from __future__ import annotations

from RAG.GRAPHRAG.src.models.LLM.v2_LLM import LLMManager, LLMUnavailable

__all__ = [
    "LLMUnavailable",
    "answer_llm",
    "reasoning_llm",
    "subq_llm",
    "text_to_cypher_llm",
]


def subq_llm() -> LLMManager:
    """Model used to decompose a user query into sub-questions."""
    return LLMManager(role="sub_question")


def reasoning_llm() -> LLMManager:
    """Model used to reason step by step over retrieved graph knowledge."""
    return LLMManager(role="reasoning")


def answer_llm() -> LLMManager:
    """Model used to write the grower-facing final answer."""
    return LLMManager(role="answer")


def text_to_cypher_llm() -> LLMManager:
    """Model used to translate natural language into Cypher."""
    return LLMManager(role="text_to_cypher")
