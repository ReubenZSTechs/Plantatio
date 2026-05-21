def penalty_generator(answer: str, max_length: int = 500) -> float:
    """
    Penalti PG untuk Generator.
    -0.5 jika panjang jawaban (word count) melebihi max_length, else 0.
    Eq. (9): RG = Rshared + PG
    """
    word_count = len(answer.split())
    return -0.5 if word_count > max_length else 0.0
