# ResearchAI – AI-Powered Research Paper Analyzer and Interactive Research Assistant

<p align="center">
  <strong>Understand. Analyze. Explore. Discover.</strong>
</p>

<p align="center">
  An AI-powered research assistant that transforms academic research papers into interactive, searchable, and structured knowledge using Generative AI and Retrieval-Augmented Generation (RAG).
</p>

---

## 📌 Overview

**ResearchAI** is an AI-powered research paper analysis platform designed to simplify the process of understanding, exploring, and evaluating academic research papers.

Reading and analyzing research papers can be time-consuming, particularly when identifying research objectives, understanding methodologies, interpreting findings, and preparing for academic discussions.

ResearchAI addresses this challenge by combining **Large Language Models (LLMs), semantic embeddings, vector search, and Retrieval-Augmented Generation (RAG)** to provide structured paper analysis and context-aware answers.

Users can upload research papers in PDF format, generate structured summaries, ask questions about the paper, prepare for viva examinations, compare multiple papers, explore research insights, and generate reports through an interactive web application.

## 🎯 Objectives

- Automate the analysis of academic research papers.
- Extract meaningful information from research documents.
- Enable context-aware question answering using RAG.
- Generate paper-specific viva questions and answers.
- Compare multiple research papers.
- Identify useful research insights from academic content.
- Provide a centralized platform for research exploration.

## ✨ Key Features

### 1. 📄 Paper Analysis
Automatically analyzes uploaded research papers and generates structured information, including:

- Research problem and objectives
- Abstract and introduction
- Methodology
- Dataset and techniques
- Experimental results and findings
- Advantages and limitations
- Conclusion and future scope

### 2. 💬 Ask the Paper
Interact with uploaded research papers using natural-language questions.

- Ask questions about paper content.
- Retrieve semantically relevant information.
- Generate context-aware answers using Gemini.
- Display relevant page and section references.
- Handle questions whose answers are not explicitly available in the paper.

### 3. 🎓 Viva Preparation
Generate paper-specific viva questions and answers to help students prepare for academic presentations and examinations.

### 4. 🔄 Compare Papers
Compare multiple research papers to understand their similarities, differences, methodologies, approaches, and findings.

### 5. 💡 Research Insights
Explore meaningful information and AI-generated insights from analyzed research papers.

### 6. 📊 Reports
Generate structured reports containing relevant research-paper analysis and information.

---

## Architecture

```text
PDF → PyMuPDF → cleaning/sections → chunks + metadata → Sentence Transformer
    → ChromaDB → semantic retrieval → grounded prompt → OpenAI LLM → answer + sources
```

The normal chatbot route always retrieves vector-search results first. It never sends an entire paper to the LLM as a shortcut.

--- 

## 🧠 GenAI Concepts and Implementation

ResearchAI combines several concepts from Natural Language Processing and Generative AI.

| Concept | Implementation in ResearchAI |
|---|---|
| Generative AI | Generates paper analysis, answers, viva questions, and research insights. |
| Large Language Model (LLM) | Gemini 2.5 Flash processes contextual information and generates natural-language responses. |
| Transformer Architecture | Used by the Transformer-based models powering the language and embedding components. |
| Sentence Embeddings | Sentence Transformers convert text chunks and user queries into numerical vector representations. |
| Semantic Search | Finds relevant research-paper content based on meaning rather than exact keyword matching. |
| Retrieval-Augmented Generation (RAG) | Supplies retrieved research-paper content to the LLM before response generation. |
| Prompt Engineering | Uses structured prompts to guide the LLM in producing relevant and organized outputs. |
| Vector Database | ChromaDB stores and retrieves semantic embeddings of research-paper chunks. |
| Natural Language Processing | Supports text processing, cleaning, chunking, semantic representation, and question answering. |

**Note:** GANs and Diffusion Models are not directly implemented in the current version of ResearchAI.

---

## ⚙️ System Architecture

ResearchAI follows a Retrieval-Augmented Generation architecture.

```text
             User Uploads Research Paper
                         |
                         v
                 PDF Text Extraction
                     (PyMuPDF)
                         |
                         v
                  Text Preprocessing
                         |
                         v
                 Section Identification
                         |
                         v
                   Semantic Chunking
                         |
                         v
              Sentence Transformer Model
                         |
                         v
                  Text Embeddings
                         |
                         v
                 ChromaDB Vector Store
                         |
                         v
                  User Asks Question
                         |
                         v
                Query Embedding
                         |
                         v
                 Semantic Retrieval
                         |
                         v
             Relevant Research-Paper Chunks
                         |
                         v
                 RAG Context Formation
                         |
                         v
                 Gemini 2.5 Flash
                         |
                         v
                Context-Aware Response
                         |
                         v
             Answer with Source References
```

### How RAG Works

1. **Document Extraction:** PyMuPDF extracts text from uploaded PDF documents.
2. **Preprocessing:** Extracted text is cleaned and organized into meaningful sections.
3. **Chunking:** The document is divided into smaller text segments for efficient retrieval.
4. **Embedding Generation:** Sentence Transformers convert text chunks into numerical vectors.
5. **Vector Storage:** ChromaDB stores the embeddings and associated document information.
6. **Query Processing:** The user's question is converted into an embedding.
7. **Semantic Retrieval:** ChromaDB retrieves relevant chunks based on semantic similarity.
8. **Context Formation:** Retrieved information is combined with the user's question.
9. **Response Generation:** Gemini 2.5 Flash generates a response using the retrieved context.
10. **Source Presentation:** Relevant page and section information is displayed alongside the answer where available.

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Frontend / User Interface | Streamlit |
| PDF Processing | PyMuPDF |
| Natural Language Processing | Sentence Transformers |
| Embedding Generation | Sentence Transformer Models |
| Vector Database | ChromaDB |
| Relational Database | SQLite |
| Generative AI Model | Google Gemini 2.5 Flash |
| Gemini Integration | Google GenAI SDK (`google-genai`) |
| Testing | Pytest |

---

## 📂 Project Modules

| Module | Description |
|---|---|
| Home | Main dashboard and application overview |
| Paper Analysis | Structured research-paper analysis |
| Ask the Paper | RAG-based question answering |
| Viva Preparation | Generation of viva questions and answers |
| Compare Papers | Comparison of multiple research papers |
| Research Insights | AI-generated research insights |
| Reports | Structured report generation |

---

## 🚀 Installation and Setup

Follow these steps to run ResearchAI locally.

### Prerequisites

- Python 3.10 or later
- pip
- Google Gemini API key
- Git

### 1. Clone the Repository

```bash
cd ResearchAI
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Add the following configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.5-flash
```

Replace `your_gemini_api_key` with your actual Google Gemini API key.

**Important:** Never upload your actual `.env` file or API key to GitHub. Use `.env.example` to document the required environment variables.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will generally be available at:

```text
http://localhost:8501
```

---

## 🧪 Testing

ResearchAI includes automated tests using Pytest to verify important application components.

Run the test suite:

```bash
pytest -v
```

**Development verification:** The project test suite previously completed with 10 passed tests and 0 failures.

The application was also tested for:

- PDF text extraction and processing.
- Embedding generation and vector storage.
- RAG-based question answering.
- Handling questions not supported by the paper content.
- Gemini API integration.
- Structured paper analysis.
- Database operations.

---

## 🔒 Security and Data Handling

- API credentials are stored in environment variables.
- `.env` should not be committed to the public repository.
- `.env.example` provides a configuration template.
- SQLite stores application metadata and analysis information.
- ChromaDB maintains the vector representations required for semantic retrieval.

Do not expose API keys, private research documents, or sensitive user information in public repositories.

---

## ⚠️ Limitations

- The current document-processing pipeline primarily targets text-based PDF research papers.
- Scanned PDFs may require OCR before their content can be processed.
- Complex mathematical equations, diagrams, and image-heavy research content may not be fully interpreted.
- Response quality depends on document extraction, retrieval relevance, and LLM performance.
- Gemini API availability and usage limits may affect AI-powered operations.
- AI-generated analysis and insights should be reviewed before being used in academic or professional work.

---

## 🔮 Future Enhancements

Potential improvements include:

- OCR support for scanned research papers.
- Multimodal analysis of research figures, tables, and diagrams.
- Integration with academic research databases.
- Automated literature review generation.
- Research gap identification.
- Citation and reference network analysis.
- Advanced paper recommendation.
- Local LLM integration for offline processing.
- Improved comparison and visualization of research findings.

---

## 🎓 Academic Relevance

ResearchAI demonstrates the practical application of concepts related to:

- Generative Artificial Intelligence
- Large Language Models
- Transformer Architecture
- Natural Language Processing
- Semantic Embeddings
- Vector Databases
- Retrieval-Augmented Generation
- Prompt Engineering

The project demonstrates how Generative AI can be integrated into an academic research workflow to make research papers easier to understand, explore, and analyze.

---

## 👨‍💻 Project Information

**Project Name:** ResearchAI – AI-Powered Research Paper Analyzer

**Project Type:** Generative AI / Natural Language Processing

**Application:** Academic Research Assistance

**Development Framework:** Python and Streamlit

**Generative AI Model:** Google Gemini 2.5 Flash

**Architecture:** Retrieval-Augmented Generation (RAG)

**Database:** SQLite and ChromaDB

---

## 📜 Disclaimer

ResearchAI is an academic project developed for educational and research-assistance purposes. AI-generated responses may contain inaccuracies and should be verified against the original research paper before being used in academic submissions, publications, or professional decisions.

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

**ResearchAI — Making Academic Research More Accessible Through Generative AI.**
