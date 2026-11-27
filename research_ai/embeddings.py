from __future__ import annotations

from sentence_transformers import SentenceTransformer

from .errors import EmbeddingError


class EmbeddingService:
    """Loads one real Sentence Transformer for both chunks and questions."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as error:  # external model download/cache failures
                raise EmbeddingError("Unable to load the embedding model. Check your internet connection or local model cache.") from error
        return self._model

    def encode(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return vectors.tolist()
        except EmbeddingError:
            raise
        except Exception as error:
            raise EmbeddingError("Unable to generate document embeddings.") from error
