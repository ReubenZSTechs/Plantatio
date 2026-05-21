from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

from backend.pipelines.main.state.GraphState import GraphState
from backend.pipelines.agents.agents import subq_llm, answer_llm, reasoning_llm

from RAG.GRAPHRAG.src.pipeline.rag.text_to_cyper import TextToCypherPipeline

# ============================================================
# NODE 1
# SUB QUESTION GENERATOR
# ============================================================

def sub_question_generator_node(state: GraphState):

    query = state["user_query"]

    prompt = f"""
You are a query decomposition system.

Break the following user query into smaller sub-questions.

User Query:
{query}

Return only the sub-questions as bullet points.
"""

    response = subq_llm.invoke(prompt)

    lines = response.split("\n")

    sub_questions = []

    for line in lines:
        line = line.strip()

        if line.startswith("-"):
            sub_questions.append(line.replace("-", "").strip())

    return {
        "sub_questions": sub_questions
    }


# ============================================================
# NODE 2
# RAG RETRIEVAL
# ============================================================
def format_graph_record(record):

    formatted = []

    for key, value in record.items():

        if isinstance(value, dict):

            label = value.get("_labels", ["Unknown"])
            name = value.get("name", "")

            formatted.append(
                f"{key}: ({label}) {name}"
            )

        elif isinstance(value, list):

            for item in value:

                if isinstance(item, dict):

                    label = item.get("_labels", ["Unknown"])
                    name = item.get("name", "")

                    formatted.append(
                        f"{key}: ({label}) {name}"
                    )

    return "\n".join(formatted)

def retrieval_rag_node(state: GraphState):
    graphrag_pipeline = TextToCypherPipeline()

    sub_questions = state["sub_questions"]

    all_records = []

    retrieved_context = []

    for question in sub_questions:

        result = graphrag_pipeline.query(question)

        records = result.get("records", [])

        all_records.extend(records)

        for record in records:

            formatted_record = format_graph_record(record)

            retrieved_context.append(formatted_record)

    return {
        "retrieved_docs": retrieved_context,
        "graph_records": all_records
    }


# ============================================================
# NODE 3
# REASONING
# ============================================================

def reasoning_node(state: GraphState):

    query = state["user_query"]

    context = "\n\n".join(
        state["retrieved_docs"]
    )

    prompt = f"""
You are an expert agricultural reasoning agent.

USER QUESTION:
{query}

GRAPH KNOWLEDGE:
{context}

Perform step-by-step reasoning using the graph knowledge.
"""

    reasoning_output = reasoning_llm.invoke(prompt)

    return {
        "reasoning_output": reasoning_output
    }


# ============================================================
# NODE 4
# FINAL ANSWER GENERATION
# ============================================================

def answer_generation_node(state: GraphState):

    query = state["user_query"]

    reasoning_output = state["reasoning_output"]

    prompt = f"""
You are an expert assistant.

USER QUERY:
{query}

REASONING:
{reasoning_output}

Generate a concise and accurate final answer.
"""

    final_answer = answer_llm.invoke(prompt)

    return {
        "final_answer": final_answer
    }


# ============================================================
# BUILD GRAPH
# ============================================================

graph = StateGraph(GraphState)

graph.add_node(
    "sub_question_generator",
    sub_question_generator_node
)

graph.add_node(
    "retrieval_rag_module",
    retrieval_rag_node
)

graph.add_node(
    "reasoning",
    reasoning_node
)

graph.add_node(
    "answer_generation",
    answer_generation_node
)


# ============================================================
# EDGES
# ============================================================

graph.set_entry_point("sub_question_generator")

graph.add_edge(
    "sub_question_generator",
    "retrieval_rag_module"
)

graph.add_edge(
    "retrieval_rag_module",
    "reasoning"
)

graph.add_edge(
    "reasoning",
    "answer_generation"
)

graph.add_edge(
    "answer_generation",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph_app = graph.compile()


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    result = graph_app.invoke({
        "user_query": "Why are the tomato leaves turning yellow with brown spots?"
    })

    print(result["final_answer"])