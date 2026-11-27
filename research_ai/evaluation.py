from __future__ import annotations


def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    if not retrieved_ids:
        return 0.0
    return sum(item in relevant_ids for item in retrieved_ids) / len(retrieved_ids)


def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str]) -> float:
    if not relevant_ids:
        return 0.0
    return sum(item in relevant_ids for item in retrieved_ids) / len(relevant_ids)
