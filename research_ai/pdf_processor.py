from __future__ import annotations

import re
import uuid
from pathlib import Path

import fitz

from .errors import ExtractionError, ValidationError
from .models import PageText


def validate_and_save_pdf(filename: str, content: bytes, upload_dir: Path, max_size: int) -> tuple[str, Path]:
    if not filename.lower().endswith(".pdf"):
        raise ValidationError("Please upload a valid research paper in PDF format.")
    if not content:
        raise ValidationError("The uploaded PDF is empty.")
    if len(content) > max_size:
        raise ValidationError(f"The uploaded PDF exceeds the {max_size // (1024 * 1024)} MB limit.")
    if not content.startswith(b"%PDF"):
        raise ValidationError("Invalid or corrupted PDF file.")
    paper_id = f"P-{uuid.uuid4().hex[:10]}"
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
    path = upload_dir / f"{paper_id}_{safe_name}"
    try:
        with fitz.open(stream=content, filetype="pdf") as document:
            if document.page_count == 0:
                raise ValidationError("The uploaded PDF has no pages.")
    except fitz.FileDataError as error:
        raise ValidationError("Invalid or corrupted PDF file.") from error
    path.write_bytes(content)
    return paper_id, path


def extract_pdf_text(paper_id: str, path: Path) -> tuple[list[PageText], dict[str, str], int]:
    try:
        with fitz.open(path) as document:
            metadata = document.metadata or {}
            pages = [PageText(paper_id, number, page.get_text("text")) for number, page in enumerate(document, start=1)]
            count = document.page_count
    except (fitz.FileDataError, RuntimeError) as error:
        raise ExtractionError("Unable to read the uploaded PDF.") from error
    if sum(len(page.text.strip()) for page in pages) < 100:
        raise ExtractionError("No extractable text was found. This PDF may be scanned or image-based; OCR processing may be required.")
    return pages, {key: value for key, value in metadata.items() if value}, count
