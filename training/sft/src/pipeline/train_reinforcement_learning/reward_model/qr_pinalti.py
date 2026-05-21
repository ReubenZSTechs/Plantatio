def penalty_query_rewriter(sub_questions: list[str]) -> float:
    """
    Penalti PQR untuk Query Rewriter.
    -0.5 jika jumlah sub-questions > 4, else 0.
    Eq. (3): RQR = Rshared + PQR
    """
    return -0.5 if len(sub_questions) > 4 else 0.0