import fitz
import pytest

from research_ai.errors import ExtractionError, ValidationError
from research_ai.pdf_processor import extract_pdf_text, validate_and_save_pdf


def test_extracts_actual_pdf_text_with_page_numbers(tmp_path):
    document = fitz.open()
    first = document.new_page()
    first.insert_text((72, 72), "A Research Paper\nAbstract\nThe dataset contains 100 records. " * 4)
    second = document.new_page()
    second.insert_text((72, 72), "Methodology\nWe trained a classifier.")
    content = document.tobytes()
    paper_id, path = validate_and_save_pdf("paper.pdf", content, tmp_path, 2_000_000)
    pages, _, count = extract_pdf_text(paper_id, path)
    assert count == 2
    assert pages[0].page_number == 1
    assert "100 records" in pages[0].text
    assert pages[1].page_number == 2


def test_rejects_non_pdf(tmp_path):
    with pytest.raises(ValidationError):
        validate_and_save_pdf("notes.txt", b"text", tmp_path, 1_000)
