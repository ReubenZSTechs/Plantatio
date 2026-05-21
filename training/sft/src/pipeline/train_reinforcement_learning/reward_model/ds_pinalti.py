def penalty_selector(selected_ids: list, K: int) -> float:
    """
    Penalti PS untuk Selector.
    -1 jika ada duplikat ID atau ID di luar format [0, K-1], else 0.
    Eq. (6): RS = Rshared + PS

    Args:
        selected_ids: list ID yang dipilih (misal [0, 3, 9])
        K: jumlah total dokumen kandidat
    """
    has_duplicate = len(selected_ids) != len(set(selected_ids))
    has_invalid   = any(not (0 <= i < K) for i in selected_ids)

    return -1.0 if (has_duplicate or has_invalid) else 0.0