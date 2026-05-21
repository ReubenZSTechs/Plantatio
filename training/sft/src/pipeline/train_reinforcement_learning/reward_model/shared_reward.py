from collections import Counter



def compute_f1(prediction: str, gold: str) -> float:
    """
    Hitung F1 token-level antara prediksi dan golden answer.
    """
    pred_tokens = prediction.lower().split()
    gold_tokens = gold.lower().split()

    pred_count = Counter(pred_tokens)
    gold_count = Counter(gold_tokens)

    common = sum((pred_count & gold_count).values())

    if common == 0:
        return 0.0

    precision = common / len(pred_tokens)
    recall    = common / len(gold_tokens)
    f1        = 2 * precision * recall / (precision + recall)
    return round(f1, 4)

def shared_reward(prediction: str, gold: str) -> float:
    return compute_f1(prediction, gold)