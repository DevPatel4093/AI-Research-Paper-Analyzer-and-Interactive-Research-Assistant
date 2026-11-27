from research_ai.evaluation import precision_at_k, recall_at_k


def test_retrieval_metrics():
    assert precision_at_k(["c1", "c2", "c3"], {"c2", "c4"}) == 1 / 3
    assert recall_at_k(["c1", "c2", "c3"], {"c2", "c4"}) == 1 / 2
