from __future__ import annotations

from pathlib import Path

import chromadb

from .errors import VectorStoreError
from .models import Chunk, RetrievedChunk


class VectorStore:
    COLLECTION_NAME = "research_paper_chunks"

    def __init__(self, directory: Path) -> None:
        try:
            self.client = chromadb.PersistentClient(path=str(directory))
            self.collection = self.client.get_or_create_collection(
                self.COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
            )
        except Exception as error:
            raise VectorStoreError("Unable to initialise the vector database.") from error

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise VectorStoreError("Chunk and embedding counts do not match.")
        if not chunks:
            raise VectorStoreError("No document chunks were available for indexing.")
        try:
            self.collection.upsert(
                ids=[chunk.chunk_id for chunk in chunks],
                documents=[chunk.text for chunk in chunks],
                embeddings=vectors,
                metadatas=[
                    {
                        "paper_id": chunk.paper_id,
                        "paper_title": chunk.paper_title,
                        "page_number": chunk.page_number,
                        "section": chunk.section,
                        "chunk_index": chunk.chunk_index,
                    }
                    for chunk in chunks
                ],
            )
        except Exception as error:
            raise VectorStoreError("Unable to store document embeddings.") from error

    def query(self, vector: list[float], paper_ids: list[str] | None, limit: int) -> list[RetrievedChunk]:
        where = {"paper_id": {"$in": paper_ids}} if paper_ids else None
        try:
            result = self.collection.query(
                query_embeddings=[vector], n_results=limit, where=where,
                include=["documents", "metadatas", "distances"],
            )
            ids = result.get("ids", [[]])[0]
            docs = result.get("documents", [[]])[0]
            metadata = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            return [
                RetrievedChunk(
                    Chunk(
                        paper_id=item["paper_id"], paper_title=item["paper_title"], chunk_id=chunk_id,
                        page_number=int(item["page_number"]), section=item["section"],
                        chunk_index=int(item["chunk_index"]), text=text,
                    ),
                    float(distance),
                )
                for chunk_id, text, item, distance in zip(ids, docs, metadata, distances)
            ]
        except Exception as error:
            raise VectorStoreError("Unable to retrieve relevant paper content.") from error
