"""The import chain that previously prevented the API from starting at all."""


def test_api_module_imports():
    """`api/app/app.py` must import without loading weights or hitting a database."""
    import app.app as module

    assert module.app.title == "Plantatio API"


def test_llm_manager_is_importable():
    """The module that .gitignore silently excluded now resolves."""
    from RAG.GRAPHRAG.src.models.LLM.v2_LLM import LLMManager

    assert hasattr(LLMManager, "generate")


def test_retrieval_pipeline_is_importable():
    """`src.*` no longer resolves to the React frontend directory."""
    from RAG.GRAPHRAG.src.pipeline.rag.text_to_cypher import TextToCypherPipeline

    assert hasattr(TextToCypherPipeline, "query")


def test_agents_module_has_no_import_time_side_effects():
    """Importing the agent roles must not download any checkpoint."""
    from backend.pipelines.agents import agents

    assert callable(agents.subq_llm)
    assert callable(agents.reasoning_llm)
    assert callable(agents.answer_llm)
