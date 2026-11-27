# Requirements Traceability

| Major requirement | Specification source | Implementation | Status | Test status |
|---|---|---|---|---|
| PDF validation and text extraction | PRD §§7–8; TRD §§6–7 | `research_ai/pdf_processor.py` | Implemented | `tests/test_pdf_processor.py` |
| Cleaning, sectioning, chunks, metadata | PRD §9; TRD §§8–10 | `research_ai/text_processing.py` | Implemented | `tests/test_text_processing.py` |
| Embeddings and vector retrieval | PRD §§10–12; TRD §§11–13 | `research_ai/embeddings.py`, `vector_store.py` | Implemented but not verified | Dependencies currently absent; live-model check pending |
| RAG and grounded chat | PRD §§12–18; TRD §§13–20 | `research_ai/rag.py`, prompts | Implemented but not verified | Vector and LLM integration pending |
| Paper analysis and viva | PRD §§16,19; TRD §§18,21 | `research_ai/generation.py` | Implemented | LLM integration pending |
| Multi-paper comparison and insights | PRD §§20–21; TRD §§22–23 | `research_ai/generation.py` | Implemented | LLM integration pending |
| Downloadable PDF report | PRD §25; TRD §24 | `research_ai/reports.py` | Implemented | Pending runtime test |
| Streamlit user experience | PRD §24; App Flow; UI/UX Brief | `app.py` | Implemented | Startup pending |
| Evaluation | PRD §28; TRD §32 | `research_ai/evaluation.py` | Partially implemented | `tests/test_evaluation.py`; no result data |
