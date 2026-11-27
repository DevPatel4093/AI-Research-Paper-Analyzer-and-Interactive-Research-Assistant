from research_ai.models import RetrievedChunk
from research_ai.prompts.templates import RAG_PROMPT
from research_ai.rag import RAGService, UNAVAILABLE


def test_rag_prompt_requires_unknown_information_response():
    prompt = RAG_PROMPT.format(history="No history", context="The paper discusses images.", question="What dataset was used?")
    assert "only from the supplied paper context" in prompt
    assert UNAVAILABLE in prompt


class _Embeddings:
    def encode(self, texts):
        return [[0.0, 1.0]]


class _Vectors:
    def query(self, vector, paper_ids, limit):
        return []


class _LLM:
    def generate(self, prompt):
        raise AssertionError("LLM must not run when retrieval finds no relevant paper content")


class _Repository:
    def __init__(self):
        self.messages = []

    def history(self, paper_id):
        return []

    def add_message(self, *args):
        self.messages.append(args)


def test_rag_returns_unknown_information_without_fabricated_source():
    settings = type("Settings", (), {"retrieval_top_k": 5, "retrieval_max_distance": 0.85})()
    repository = _Repository()
    answer = RAGService(settings, _Embeddings(), _Vectors(), _LLM(), repository).ask("P1", "Which dataset was used?")
    assert answer.unavailable is True
    assert answer.answer == UNAVAILABLE
    assert answer.sources == []
    assert len(repository.messages) == 2
