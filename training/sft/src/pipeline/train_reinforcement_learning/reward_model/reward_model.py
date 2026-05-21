import re
from collections import Counter
from src.pipeline.train_reinforcement_learning.reward_model.ds_pinalti import penalty_selector
from src.pipeline.train_reinforcement_learning.reward_model.ge_pinalti import penalty_generator
from src.pipeline.train_reinforcement_learning.reward_model.qr_pinalti import penalty_query_rewriter
from src.pipeline.train_reinforcement_learning.reward_model.shared_reward import shared_reward


def reward_query_rewriter(prediction: str, gold: str, sub_questions: list[str]) -> dict:
    """RQR = Rshared + PQR"""
    r_shared = shared_reward(prediction, gold)
    p_qr     = penalty_query_rewriter(sub_questions)
    
    final_reward = {"Rshared": r_shared, "PQR": p_qr, "RQR": round(r_shared + p_qr, 4)}
    return final_reward


def reward_selector(prediction: str, gold: str, selected_ids: list, K: int) -> dict:
    """RS = Rshared + PS"""
    r_shared = shared_reward(prediction, gold)
    p_s      = penalty_selector(selected_ids, K)
    
    # Kunci dictionary diperbaiki menjadi PS dan RS
    final_reward = {"Rshared": r_shared, "PS": p_s, "RS": round(r_shared + p_s, 4)}
    return final_reward


def reward_generator(prediction: str, gold: str, max_length: int = 500) -> dict:
    """RG = Rshared + PG"""
    r_shared = shared_reward(prediction, gold)
    p_g      = penalty_generator(prediction, max_length)
    
    # Kunci dictionary diperbaiki menjadi PG dan RG
    final_reward = {"Rshared": r_shared, "PG": p_g, "RG": round(r_shared + p_g, 4)}
    return final_reward


def collect_rollout(question: str, gold: str, sub_questions: list[str], selected_ids: list[int], K: int, prediction: str, max_answer_length: int = 100) -> dict:
    """
    Satu rollout untuk satu pertanyaan (Algorithm 1, baris Collect Rollout).
    Mengembalikan tuple reward tiap agent.
    """
    r_qr = reward_query_rewriter(prediction, gold, sub_questions)
    r_s  = reward_selector(prediction, gold, selected_ids, K)
    r_g  = reward_generator(prediction, gold, max_answer_length)
    
    final_rollout = {
        "question": question,
        "prediction": prediction,
        "gold": gold,
        "reward_QR": r_qr,
        "reward_S": r_s,
        "reward_G": r_g
    }
    return final_rollout


class ReplayBuffer:
    """Menyimpan rollout tiap epoch/batch, lalu dikosongkan."""

    # Diperbaiki: menggunakan init
    def init(self):
        self.buffer: list[dict] = []

    def add(self, rollout: dict):
        self.buffer.append(rollout)

    def clear(self):
        self.buffer = []

    # Diperbaiki: menggunakan len agar perintah len(buf) berfungsi
    def len(self):
        return len(self.buffer)

    def get_all(self) -> list[dict]:
        return self.buffer


# Diperbaiki: menggunakan name dan "main"
if name == "main":

    question = "When was the Eiffel Tower built and who designed it?"
    gold = "The Eiffel Tower was built in 1889 and designed by Gustave Eiffel."
    sub_questions = ["When was the Eiffel Tower built?", "Who designed the Eiffel Tower?"]
    K = 10                    
    selected_ids = [0, 3, 3]             
    prediction = "The Eiffel Tower was built in 1889 by Gustave Eiffel."

    rollout = collect_rollout(question, gold, sub_questions, selected_ids, K, prediction)

    buf = ReplayBuffer()
    buf.add(rollout)
    print(f"Buffer size: {len(buf)}")  # Ini sekarang akan memanggil buf.len()
    buf.clear()
    print(f"After clear: {len(buf)}")