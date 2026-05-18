from typing import TypedDict, List, Dict, Any, Optional


class DatasetState(TypedDict):
    documents: Dict[str, Dict[str, Any]]
    chunks: List[Dict[str, Any]]

    chunk_idx: int
    question_idx: int

    current_chunk: Dict[str, Any]
    current_question: str
    questions: List[str]
    accepted_sub_questions: List[str]
    rejected_sub_questions: List[str]

    accepted_answer: str
    rejected_answer: str
    final_docs: List[str]

    dataset: List[Dict[str, Any]]
