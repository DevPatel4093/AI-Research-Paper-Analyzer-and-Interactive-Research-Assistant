from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class PageText:
    paper_id: str
    page_number: int
    text: str


@dataclass(frozen=True)
class Chunk:
    paper_id: str
    paper_title: str
    chunk_id: str
    page_number: int
    section: str
    chunk_index: int
    text: str


@dataclass(frozen=True)
class Paper:
    paper_id: str
    filename: str
    title: str
    authors: str = "Not explicitly stated in the paper."
    publication_info: str = "Not explicitly stated in the paper."
    page_count: int = 0
    section_count: int = 0
    chunk_count: int = 0
    uploaded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    distance: float


@dataclass(frozen=True)
class Source:
    paper_title: str
    page_number: int
    section: str
    chunk_id: str
    excerpt: str


@dataclass(frozen=True)
class ChatAnswer:
    answer: str
    sources: list[Source]
    unavailable: bool = False
