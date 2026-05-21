from typing import TypedDict, List, Dict, Any


class GraphState(TypedDict):

    user_query: str

    sub_questions: List[str]

    retrieved_docs: List[str]

    graph_records: List[Dict[str, Any]]

    reasoning_output: str

    final_answer: str