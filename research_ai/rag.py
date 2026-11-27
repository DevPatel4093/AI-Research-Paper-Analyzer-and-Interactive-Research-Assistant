from __future__ import annotations

from .models import ChatAnswer, Source
from .prompts.templates import RAG_PROMPT


UNAVAILABLE = "The paper does not explicitly provide this information."


class RAGService:
    def __init__(self, settings, embeddings, vectors, llm, repository):
        self.settings = settings
        self.embeddings = embeddings
        self.vectors = vectors
        self.llm = llm
        self.repository = repository

    def ask(self, paper_id: str, question: str) -> ChatAnswer:
        question = question.strip()

        if not question:
            raise ValueError(
                "Please enter a question about the uploaded paper."
            )

        # =========================================================
        # 1. Convert the user's question into an embedding
        # =========================================================

        question_vector = self.embeddings.encode([question])[0]

        # =========================================================
        # 2. Retrieve the most relevant chunks
        # =========================================================

        retrieved = self.vectors.query(
            question_vector,
            [paper_id],
            max(self.settings.retrieval_top_k, 8),
        )

        # Keep the best retrieved chunks.
        # We intentionally do not apply an aggressive distance
        # threshold here because relevant information may appear
        # in different sections of the paper.
        relevant = retrieved[:8]

        # =========================================================
        # 3. Handle retrieval failure
        # =========================================================

        if not relevant:
            answer = ChatAnswer(
                UNAVAILABLE,
                [],
                True,
            )

            self._save_turn(
                paper_id,
                question,
                answer,
            )

            return answer

        # =========================================================
        # 4. Build source information
        # =========================================================

        sources = [
            Source(
                item.chunk.paper_title,
                item.chunk.page_number,
                item.chunk.section,
                item.chunk.chunk_id,
                item.chunk.text[:500],
            )
            for item in relevant
        ]

        # =========================================================
        # 5. Get previous conversation
        # =========================================================

        history = self.repository.history(paper_id)

        history_text = "\n".join(
            f"{entry['role'].title()}: {entry['content']}"
            for entry in history[-6:]
        )

        if not history_text:
            history_text = "No previous conversation."

        # =========================================================
        # 6. Build retrieved paper context
        # =========================================================

        context_parts = []

        for i, item in enumerate(relevant, start=1):
            context_parts.append(
                f"""
[Source {i}]
Page: {item.chunk.page_number}
Section: {item.chunk.section}

{item.chunk.text}
"""
            )

        context = "\n\n".join(context_parts)

        # =========================================================
        # 7. Build RAG prompt
        # =========================================================

        prompt = RAG_PROMPT.format(
            history=history_text,
            context=context,
            question=question,
        )

        # =========================================================
        # 8. Generate grounded answer
        # =========================================================

        generated = self.llm.generate(
            prompt,
            temperature=0.2,
        ).strip()

        # =========================================================
        # 9. Handle empty LLM response
        # =========================================================

        if not generated:
            generated = UNAVAILABLE

        unavailable = (
            generated.lower().strip()
            == UNAVAILABLE.lower().strip()
        )

        answer = ChatAnswer(
            generated,
            [] if unavailable else sources,
            unavailable,
        )

        # =========================================================
        # 10. Save conversation
        # =========================================================

        self._save_turn(
            paper_id,
            question,
            answer,
        )

        return answer

    def _save_turn(
        self,
        paper_id: str,
        question: str,
        answer: ChatAnswer,
    ) -> None:

        self.repository.add_message(
            paper_id,
            "user",
            question,
            [],
        )

        sources = [
            {
                "paper_title": source.paper_title,
                "page_number": source.page_number,
                "section": source.section,
                "chunk_id": source.chunk_id,
            }
            for source in answer.sources
        ]

        self.repository.add_message(
            paper_id,
            "assistant",
            answer.answer,
            sources,
        )