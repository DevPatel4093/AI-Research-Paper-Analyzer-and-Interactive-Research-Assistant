from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from .config import Settings
from .embeddings import EmbeddingService
from .errors import ExtractionError
from .models import Paper
from .pdf_processor import extract_pdf_text, validate_and_save_pdf
from .repository import Repository
from .text_processing import chunk_pages, clean_pages
from .vector_store import VectorStore


def paper_title(pages_text: list[str], filename: str, metadata: dict[str, str]) -> str:
    if metadata.get("title"):
        return metadata["title"].strip()
    for text in pages_text:
        for line in text.splitlines():
            candidate = line.strip()
            if len(candidate) >= 8 and len(candidate) <= 220 and not re.match(r"^(abstract|introduction)$", candidate, re.I):
                return candidate
    return Path(filename).stem


class PaperProcessingService:
    def __init__(self, settings: Settings, repository: Repository, embeddings: EmbeddingService, vectors: VectorStore) -> None:
        self.settings = settings
        self.repository = repository
        self.embeddings = embeddings
        self.vectors = vectors

    def process(self, filename: str, content: bytes, progress: Callable[[str], None] | None = None) -> Paper:
        notify = progress or (lambda _: None)
        self.settings.ensure_directories()
        notify("Validating PDF")
        paper_id, path = validate_and_save_pdf(filename, content, self.settings.upload_dir, self.settings.max_upload_bytes)
        try:
            notify("Extracting text")
            pages, metadata, page_count = extract_pdf_text(paper_id, path)
            notify("Cleaning content and identifying sections")
            cleaned = clean_pages(pages)
            title = paper_title([page.text for page in cleaned], filename, metadata)
            chunks = chunk_pages(cleaned, title)
            if not chunks:
                raise ExtractionError("No meaningful text chunks could be created from this PDF.")
            notify("Generating Transformer embeddings")
            vectors = self.embeddings.encode([chunk.text for chunk in chunks])
            notify("Building vector knowledge base")
            self.vectors.upsert(chunks, vectors)
            section_count = len({chunk.section for chunk in chunks if chunk.section != "Unclassified"})
            paper = Paper(
                paper_id=paper_id, filename=filename, title=title,
                authors=metadata.get("author", "Not explicitly stated in the paper."),
                publication_info=metadata.get("subject", "Not explicitly stated in the paper."),
                page_count=page_count, section_count=section_count, chunk_count=len(chunks),
            )
            self.repository.save_paper(paper, chunks)
            notify("Paper is ready")
            return paper
        except Exception:
            # Leave the original upload only when processing succeeds; a failed file never appears as an indexed paper.
            path.unlink(missing_ok=True)
            raise
