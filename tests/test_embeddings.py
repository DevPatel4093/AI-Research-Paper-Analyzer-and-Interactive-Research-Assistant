from research_ai.embeddings import EmbeddingService


class _Vectors:
    def tolist(self):
        return [[0.25, 0.75]]


class _Model:
    def __init__(self):
        self.calls = []

    def encode(self, texts, normalize_embeddings, show_progress_bar):
        self.calls.append((texts, normalize_embeddings, show_progress_bar))
        return _Vectors()


def test_embedding_service_uses_same_model_encoding_contract():
    service = EmbeddingService("test-model")
    model = _Model()
    service._model = model
    assert service.encode(["paper text"]) == [[0.25, 0.75]]
    assert model.calls == [(["paper text"], True, False)]
