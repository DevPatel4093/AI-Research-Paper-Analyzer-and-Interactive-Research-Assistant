from __future__ import annotations

import re
from collections import Counter

from .models import Chunk, PageText

SECTION_PATTERNS = {
    "Abstract": r"^\s*(?:\d+[.\s]+)?abstract\s*$",
    "Introduction": r"^\s*(?:\d+[.\s]+)?introduction\s*$",
    "Related Work": r"^\s*(?:\d+[.\s]+)?(?:related work|literature review|background)\s*$",
    "Research Problem": r"^\s*(?:\d+[.\s]+)?research problem\s*$",
    "Objectives": r"^\s*(?:\d+[.\s]+)?(?:objectives?|aims?)\s*$",
    "Methodology": r"^\s*(?:\d+[.\s]+)?(?:methodology|methods?|materials and methods?)\s*$",
    "Dataset": r"^\s*(?:\d+[.\s]+)?(?:dataset|data(?:\s+collection)?)\s*$",
    "Experiments": r"^\s*(?:\d+[.\s]+)?(?:experiments?|experimental setup|evaluation)\s*$",
    "Results": r"^\s*(?:\d+[.\s]+)?(?:results?|findings?)\s*$",
    "Discussion": r"^\s*(?:\d+[.\s]+)?discussion\s*$",
    "Conclusion": r"^\s*(?:\d+[.\s]+)?(?:conclusion|conclusions?)\s*$",
    "Limitations": r"^\s*(?:\d+[.\s]+)?limitations?\s*$",
    "Future Work": r"^\s*(?:\d+[.\s]+)?(?:future work|future directions?)\s*$",
    "References": r"^\s*(?:\d+[.\s]+)?references\s*$",
}


def clean_pages(pages: list[PageText]) -> list[PageText]:
    """Normalize whitespace and remove line-level headers/footers repeated on 3+ pages."""
    candidate_lines = [line.strip() for page in pages for line in page.text.splitlines() if line.strip()]
    repeated = {line for line, count in Counter(candidate_lines).items() if count >= 3 and len(line) < 120}
    cleaned: list[PageText] = []
    for page in pages:
        lines = [line.strip() for line in page.text.splitlines() if line.strip() and line.strip() not in repeated]
        text = re.sub(r"[ \t]+", " ", "\n".join(lines))
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        cleaned.append(PageText(page.paper_id, page.page_number, text))
    return cleaned


def identify_sections(page: PageText) -> list[tuple[str, str]]:
    """Split a page at recognised headings; keep an honest 'Unclassified' fallback."""
    current = "Unclassified"
    parts: list[tuple[str, list[str]]] = []
    for line in page.text.splitlines():
        matched = next((name for name, pattern in SECTION_PATTERNS.items() if re.match(pattern, line, re.I)), None)
        if matched:
            if parts and parts[-1][1]:
                pass
            current = matched
            parts.append((current, []))
        else:
            if not parts:
                parts.append((current, []))
            parts[-1][1].append(line)
    return [(section, "\n".join(lines).strip()) for section, lines in parts if "\n".join(lines).strip()]


def chunk_pages(pages: list[PageText], paper_title: str, size: int = 900, overlap: int = 150) -> list[Chunk]:
    if size <= overlap:
        raise ValueError("Chunk size must exceed overlap.")
    chunks: list[Chunk] = []
    index = 0
    for page in pages:
        for section, text in identify_sections(page):
            start = 0
            while start < len(text):
                end = min(len(text), start + size)
                if end < len(text):
                    boundary = max(text.rfind(". ", start, end), text.rfind("\n", start, end))
                    if boundary > start + size // 2:
                        end = boundary + 1
                piece = text[start:end].strip()
                if piece:
                    chunks.append(Chunk(page.paper_id, paper_title, f"{page.paper_id}-c{index:04d}", page.page_number, section, index, piece))
                    index += 1
                if end >= len(text):
                    break
                start = max(end - overlap, start + 1)
    return chunks
