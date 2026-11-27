# AI Research Paper Analyzer and Interactive Research Assistant

A Streamlit application that converts an uploaded text-based PDF research paper into a source-traceable semantic knowledge base. It uses PyMuPDF for extraction, Sentence Transformers for real embeddings, ChromaDB for vector retrieval, and a configurable OpenAI LLM for grounded analysis, chat, viva preparation, and multi-paper insights.

## Features

- PDF-only upload validation with clear corrupt/scanned-PDF errors.
- Page-preserving extraction, cleaning, section detection, chunk metadata, real embeddings, and persistent ChromaDB retrieval.
- Structured paper analysis with explicit missing-information handling.
- Conversational **Ask the Paper** RAG chat with source cards (paper, page, section, chunk).
- Paper-specific viva questions, multi-paper comparison, labelled AI-assisted research observations, and PDF reports.
- SQLite stores paper metadata, chunks, generated records, and chat history; ChromaDB stores vectors and retrievable source text.

## Architecture

```text
PDF → PyMuPDF → cleaning/sections → chunks + metadata → Sentence Transformer
    → ChromaDB → semantic retrieval → grounded prompt → OpenAI LLM → answer + sources
```

The normal chatbot route always retrieves vector-search results first. It never sends an entire paper to the LLM as a shortcut.

## Setup and run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `OPENAI_API_KEY` in `.env` for analysis, chat, viva, and insights. Then start the app:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

Open the local URL shown by Streamlit. Upload a text-based PDF, process it on **Home**, then use the sidebar to access analysis, chat, viva, comparison, insights, and reports.

## Configuration

`OPENAI_API_KEY` is required for LLM-backed features. Other optional settings are in `.env.example`: `LLM_MODEL`, `EMBEDDING_MODEL`, `VECTOR_DB_PATH`, `UPLOAD_DIR`, `REPORT_DIR`, `DATABASE_URL`, `MAX_UPLOAD_MB`, `RETRIEVAL_TOP_K`, and `RETRIEVAL_MAX_DISTANCE`.

## Testing and evaluation

Run automated tests with:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The test suite covers cleaning/sectioning/chunk metadata, grounding prompt rules, and Precision@K/Recall@K calculations. Retrieval and answer evaluation must use paper-specific annotated questions; no performance figures are fabricated by the app.

## Known limitations

- Text-based PDFs are supported; OCR, table/figure, equation, and multimodal analysis are out of scope.
- LLM-backed features require a valid OpenAI API key and service availability.
- Research observations are assistance, not validated novel research gaps.
- Automatic headings are best-effort and retain `Unclassified` rather than assign a doubtful section.
