from research_ai.models import PageText
from research_ai.text_processing import chunk_pages, clean_pages, identify_sections


def test_cleaning_removes_repeated_header_and_preserves_page_number():
    pages = [PageText("P1", index, f"Conference 2026\nAbstract\nContent on page {index}.") for index in range(1, 4)]
    cleaned = clean_pages(pages)
    assert "Conference 2026" not in cleaned[0].text
    assert cleaned[2].page_number == 3


def test_identifies_section_without_forcing_unknown_text():
    page = PageText("P1", 1, "Abstract\nA concise summary.\nIntroduction\nBackground text.")
    assert identify_sections(page) == [("Abstract", "A concise summary."), ("Introduction", "Background text.")]


def test_chunks_have_traceable_metadata():
    chunks = chunk_pages([PageText("P1", 4, "Methodology\n" + "word " * 500)], "A Paper", size=200, overlap=50)
    assert len(chunks) > 1
    assert all(chunk.paper_id == "P1" and chunk.page_number == 4 and chunk.section == "Methodology" for chunk in chunks)
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)
