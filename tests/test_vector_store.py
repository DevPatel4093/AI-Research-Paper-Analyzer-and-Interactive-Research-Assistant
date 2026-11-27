import pytest

chromadb = pytest.importorskip("chromadb")

from research_ai.models import Chunk
from research_ai.vector_store import VectorStore


def test_vector_retrieval_returns_original_chunk_metadata(tmp_path):
    store = VectorStore(tmp_path / "vectors")
    chunk = Chunk("P1", "Paper One", "P1-c0", 5, "Dataset", 0, "The study uses the ABC dataset.")
    store.upsert([chunk], [[1.0, 0.0, 0.0]])
    result = store.query([1.0, 0.0, 0.0], ["P1"], 1)
    assert result[0].chunk.text == chunk.text
    assert result[0].chunk.page_number == 5
    assert result[0].chunk.section == "Dataset"
