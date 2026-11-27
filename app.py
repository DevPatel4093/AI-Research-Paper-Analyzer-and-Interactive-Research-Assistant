from __future__ import annotations

import streamlit as st

from research_ai.config import Settings
from research_ai.embeddings import EmbeddingService
from research_ai.errors import ResearchAIError
from research_ai.generation import GenerationService
from research_ai.llm import LLMService
from research_ai.rag import RAGService
from research_ai.reports import generate_report
from research_ai.repository import Repository
from research_ai.services import PaperProcessingService
from research_ai.vector_store import VectorStore

st.set_page_config(page_title="ResearchAI", page_icon="🔬", layout="wide")
st.markdown("""<style>
  .stApp { background: #f7f8fb; color: #17233c; }

  /* ---- Sidebar ---- */
  [data-testid='stSidebar'] { background: #0d1b3d; }
  [data-testid='stSidebar'] [data-testid='stMarkdownContainer'],
  [data-testid='stSidebar'] label,
  [data-testid='stSidebar'] .stCaption { color: #f6f8ff; }
  [data-testid='stSidebar'] [data-testid='stRadio'] label { border-radius: 10px; padding: .35rem .45rem; }
  [data-testid='stSidebar'] [data-testid='stRadio'] label:has(input:checked) { background: #e9e4ff; color: #32236d; }
  [data-testid='stSidebar'] [data-testid='stSelectbox'] span,
  [data-testid='stSidebar'] [data-testid='stSelectbox'] label,
  [data-testid='stSidebar'] [data-testid='stExpander'] summary,
  [data-testid='stSidebar'] [data-testid='stCaptionContainer'] span,
  [data-testid='stSidebar'] p { color: #f6f8ff !important; }

  /* ---- Hero ---- */
  .hero { background: #0d1b3d; color: white; padding: 2.3rem; border-radius: 18px; margin-bottom: 1rem; }
  .hero h1, .hero p { color: white; }

  /* ---- Cards ---- */
  .feature-card {
    background: #ffffff;
    border: 1px solid #e1e7f0;
    border-radius: 18px;
    padding: 1.35rem;
    min-height: 145px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.045);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.comparison-card {
    background: #151821;
    border: 1px solid #2a2f3a;
    border-radius: 14px;
    padding: 22px;
    margin: 20px 0;
}

.comparison-title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    padding-bottom: 18px;
    margin-bottom: 8px;
    border-bottom: 1px solid #303642;
}

.comparison-field {
    padding: 14px 4px;
    border-bottom: 1px solid #252a34;
}

.comparison-field:last-child {
    border-bottom: none;
}

.comparison-label {
    font-size: 14px;
    font-weight: 700;
    color: #9ca8bb;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.comparison-value {
    font-size: 15px;
    line-height: 1.6;
    color: #f1f3f6;
}

.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.09);
}

.feature-card h3 {
    color: #17233c !important;
    margin-bottom: 0.6rem;
}

.feature-card .muted {
    color: #64748b !important;
    line-height: 1.5;
}
  .source-card { border-left: 4px solid #4169e1; margin: .4rem 0; }
  .muted { color: #64748b; }

  /* ---- Form labels ---- */
  [data-testid='stFileUploader'] label,
  [data-testid='stSelectbox'] label,
  [data-testid='stMultiSelect'] label { color: #17233c; }

  /* ---- File uploader — fix dark container ---- */
  [data-testid='stFileUploader'] section { background: #e8edf5 !important; border-color: #c7d0e0 !important; }
  [data-testid='stFileUploader'] section p,
  [data-testid='stFileUploader'] section span,
  [data-testid='stFileUploader'] section small { color: #17233c !important; }
  [data-testid='stFileUploader'] button { background: #4169e1 !important; color: #ffffff !important; border: none !important; }
  [data-testid='stFileUploader'] button:hover { background: #3458c0 !important; }

  .viva-card {
    background: #ffffff;
    border: 1px solid #e1e7f0;
    border-left: 4px solid #4169e1;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
}

.viva-number {
    color: #4169e1;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.07em;
    margin-bottom: 0.35rem;
}

.viva-question {
    color: #17233c;
    font-size: 1rem;
    font-weight: 650;
    line-height: 1.5;
}

.main .block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    color: #17233c !important;
}

p, li, label {
    color: #334155;
}

  /* ---- Chat input — light text on dark container ---- */
  /* =========================================================
   CHAT INPUT
   ========================================================= */

[data-testid='stChatInput'] {
    background: #ffffff !important;
    border: 1px solid #dbe3ef !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
}

[data-testid='stChatInput'] textarea {
    color: #17233c !important;
    background: #ffffff !important;
}

[data-testid='stChatInput'] textarea::placeholder {
    color: #94a3b8 !important;
}

[data-testid='stChatInput'] button {
    background: #4169e1 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
}
  [data-testid='stChatInput'] textarea::placeholder { color: #a0aec0 !important; }

  /* ---- Alert / warning / info / error boxes ---- */
  [data-testid='stAlert'] p,
  [data-testid='stAlert'] span,
  [data-testid='stAlert'] li { color: #17233c !important; }
  [data-testid='stAlert'] svg { color: inherit !important; }

  /* ---- Expanders — dark header bar needs light text ---- */
  [data-testid='stExpander'] summary,
  [data-testid='stExpander'] summary p,
  [data-testid='stExpander'] summary span { color: #17233c !important; }
  [data-testid='stExpander'] summary { background: transparent !important; }

  /* ---- Sidebar radio buttons — fix contrast ---- */
  [data-testid='stSidebar'] [data-testid='stRadio'] label p { color: #f6f8ff !important; }
  [data-testid='stSidebar'] [data-testid='stRadio'] label:has(input:checked) p { color: #32236d !important; }
  [data-testid='stSidebar'] [data-testid='stRadio'] label:has(input:not(:checked)) svg { color: #f6f8ff !important; }
  [data-testid='stSidebar'] [data-testid='stRadio'] label:has(input:checked) svg { color: #32236d !important; }

  .hero-modern {
    background: linear-gradient(
        135deg,
        #102454 0%,
        #1e3a78 55%,
        #314c9b 100%
    );
    color: #ffffff;
    padding: 2.5rem;
    border-radius: 24px;
    margin-bottom: 1.5rem;
    box-shadow: 0 12px 30px rgba(30, 58, 120, 0.18);
}

.hero-modern h1 {
    color: #ffffff !important;
    font-size: 2.6rem;
    line-height: 1.15;
    margin: 0.7rem 0 1rem;
}

.hero-modern p {
    color: #dce7ff !important;
    font-size: 1.05rem;
    max-width: 820px;
    line-height: 1.65;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.2);
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}

.hero-tech {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 1.25rem;
}

.hero-tech span {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    padding: 7px 12px;
    border-radius: 10px;
    font-size: 0.82rem;
}

/* =========================================================
   SIDEBAR VISIBILITY FIX
   ========================================================= */

/* ResearchAI sidebar title */
[data-testid='stSidebar'] h1 {
    color: #ffffff !important;
}

/* Settings expander */
[data-testid='stSidebar'] [data-testid='stExpander'] summary,
[data-testid='stSidebar'] [data-testid='stExpander'] summary p,
[data-testid='stSidebar'] [data-testid='stExpander'] summary span {
    color: #ffffff !important;
}

/* Settings content */
[data-testid='stSidebar'] [data-testid='stExpander'] p,
[data-testid='stSidebar'] [data-testid='stExpander'] span {
    color: #f6f8ff !important;
}

/* =========================================================
   SOURCE CARDS
   ========================================================= */

.source-card {
    background: #f8fafc !important;
    border: 1px solid #dbe3f0 !important;
    border-left: 4px solid #4f7cff !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    margin: 10px 0 !important;
    color: #1f2937 !important;
}

.source-card .source-title {
    color: #2563eb !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    margin-bottom: 5px !important;
}

.source-card .source-paper {
    color: #1f2937 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

.source-card .source-meta {
    color: #64748b !important;
    font-size: 12px !important;
    margin-top: 4px !important;
}

  </style>""",unsafe_allow_html=True)




@st.cache_resource
def services() -> tuple[Settings, Repository, PaperProcessingService, RAGService, GenerationService]:
    settings = Settings.from_environment()
    settings.ensure_directories()
    repository = Repository(settings.database_path)
    embeddings = EmbeddingService(settings.embedding_model)
    vectors = VectorStore(settings.vector_db_path)
    llm = LLMService(settings.gemini_api_key, settings.llm_model)
    return settings, repository, PaperProcessingService(settings, repository, embeddings, vectors), RAGService(settings, embeddings, vectors, llm, repository), GenerationService(repository, llm)


settings, repo, processing, rag, generation = services()
papers = repo.papers()
if "selected_paper" not in st.session_state:
    st.session_state.selected_paper = papers[0].paper_id if papers else None
if "latest_insights" not in st.session_state:
    st.session_state.latest_insights = None

with st.sidebar:
    st.title("🔬 ResearchAI")
    page = st.radio("Navigate", ["🏠 Home", "📊 Paper Analysis", "💬 Ask the Paper", "🎓 Viva Preparation", "📚 Compare Papers", "🔎 Research Insights", "📥 Reports"], label_visibility="collapsed")
    st.divider()
    if papers:
        ids = [paper.paper_id for paper in papers]
        selected = st.selectbox("📄 Current Paper", ids, index=ids.index(st.session_state.selected_paper) if st.session_state.selected_paper in ids else 0, format_func=lambda paper_id: next(paper.title for paper in papers if paper.paper_id == paper_id))
        st.session_state.selected_paper = selected
    else:
        st.caption("No paper selected")
    with st.expander("⚙ Settings"):
        st.caption(f"Embedding: {settings.embedding_model}")
        st.caption(f"LLM: {settings.llm_model}")
        st.caption("AI generation requires GEMINI_API_KEY.")


def current_paper():
    return repo.paper(st.session_state.selected_paper) if st.session_state.selected_paper else None


def require_paper():
    paper = current_paper()
    if not paper:
        st.info("📄 No research paper selected. Upload a PDF from Home to begin.")
    return paper

def show_sources(sources: list[dict]) -> None:
    for source in sources:
        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-title">📚 SOURCE</div>
                <div class="source-paper">
                    {source.get("paper_title", "Paper")}
                </div>
                <div class="source-meta">
                    Page {source.get("page_number", "Unavailable")}
                    • {source.get("section", "Unclassified")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_analysis(analysis: dict[str, str]) -> None:
    labels = {"summary": "📝 Summary", "research_problem": "🎯 Research Problem", "objectives": "🎯 Objectives", "methodology": "⚙ Methodology", "dataset": "🗂 Dataset", "algorithms_models": "🤖 Models / Algorithms", "key_contributions": "⭐ Key Contributions", "results": "📈 Results", "limitations": "⚠ Limitations", "future_work": "🔮 Future Work"}
    for key, label in labels.items():
        with st.expander(label, expanded=key == "summary"):
            st.write(analysis.get(key, "Not explicitly stated in the paper."))


def show_system_status() -> None:
    llm = generation.llm
    rag_status = "Operational" if llm.last_status == "operational" else ("Waiting for LLM verification" if llm.last_status == "not_verified" else f"Waiting for LLM — {llm.status_message}")
    st.subheader("System Status")
    left, middle, right = st.columns(3)
    left.success("PDF Processing\n\nReady")
    middle.info(f"LLM Service\n\n{llm.status_message}")
    right.info(f"RAG Pipeline\n\n{rag_status}")


if page == "🏠 Home":
    st.markdown(
        """
<div class="hero-modern">

<div class="hero-badge">
✨ GENERATIVE AI + RAG RESEARCH ASSISTANT
</div>

<h1>
Turn Research Papers<br>
Into Actionable Knowledge.
</h1>

<p>
Analyze papers, ask questions, prepare for your viva,
compare research and discover potential research directions
with grounded Generative AI.
</p>

<div class="hero-tech">
<span>🧠 Gemini</span>
<span>🔎 RAG</span>
<span>🧩 Semantic Search</span>
<span>📚 ChromaDB</span>
</div>

</div>
""",
        unsafe_allow_html=True,
    )

    upload = st.file_uploader("📄 Upload your research paper", type=["pdf"], help="PDF files only. Text-based research papers are supported.")
    if upload:
        st.success(f"{upload.name} • {upload.size / 1024 / 1024:.2f} MB • Ready to process")
        if st.button("Analyze Paper", type="primary"):
            stages: list[str] = []
            progress = st.progress(0, text="Starting paper processing")
            def note(stage: str) -> None:
                stages.append(stage)
                progress.progress(min(len(stages) * 16, 100), text=stage)
            try:
                with st.spinner("Processing research paper…"):
                    paper = processing.process(upload.name, upload.getvalue(), note)
                progress.progress(100, text="Paper is ready for analysis")
                st.session_state.selected_paper = paper.paper_id
                st.success("✓ PDF uploaded, text extracted, chunks embedded, and knowledge base built.")
                st.rerun()
            except ResearchAIError as error:
                progress.empty()
                st.error(str(error))
    show_system_status()
    columns = st.columns(3)
    features = [("📊", "Analyze Paper", "Structured, source-grounded paper analysis"), ("💬", "Ask Paper", "RAG answers with page and section sources"), ("🎓", "Viva Prep", "Paper-specific viva questions and answers"), ("📚", "Compare Papers", "Side-by-side analysis across uploaded papers"), ("🔎", "Research Insights", "Carefully labelled AI-assisted observations"), ("📥", "Generate Report", "Download a PDF analysis report")]
    for column, (icon, title, text) in zip(columns * 2, features):
        with column:
            st.markdown(f"<div class='feature-card'><h3>{icon} {title}</h3><span class='muted'>{text}</span></div>", unsafe_allow_html=True)

elif page == "📊 Paper Analysis":
    paper = require_paper()
    if paper:
        st.title("📊 Research Paper Analysis")
        st.caption(f"{paper.filename} • {paper.page_count} pages • {paper.section_count} identified sections • {paper.chunk_count} semantic chunks")
        analysis = generation.analysis(paper.paper_id)
        if not analysis:
            st.info("Generate a structured analysis from the uploaded paper. It will not be created without an LLM API key.")
            if st.button("Generate Paper Analysis", type="primary"):
                try:
                    with st.spinner("Generating grounded structured analysis…"):
                        analysis = generation.analyze(paper.paper_id)
                    st.success("Analysis generated.")
                except ResearchAIError as error:
                    st.error(str(error))
        if analysis:
            st.subheader(analysis.get("title", paper.title))
            st.caption(f"Authors: {analysis.get('authors')}  |  Publication: {analysis.get('publication_information')}")
            show_analysis(analysis)

elif page == "💬 Ask the Paper":
    paper = require_paper()
    if paper:
        st.title("💬 Ask the Paper")
        st.caption("Ask anything about the current research paper. Every answer is based on retrieved chunks or says when information is unavailable.")
        history = repo.history(paper.paper_id)
        if not history:
            st.info("💬 Start a conversation — ask your first question about the uploaded research paper.")
        for message in history:
            with st.chat_message("user" if message["role"] == "user" else "assistant"):
                st.write(message["content"])
                if message["role"] == "assistant" and message["sources"]:
                    show_sources(message["sources"])
        question = st.chat_input("Ask a question about this paper…")
        if question:
            try:
                with st.spinner("Retrieving relevant paper sections and generating an answer…"):
                    rag.ask(paper.paper_id, question)
                st.rerun()
            except (ResearchAIError, ValueError) as error:
                st.error(str(error))

elif page == "🎓 Viva Preparation":
    paper = require_paper()
    if paper:
        st.title("🎓 Viva Preparation")
        viva = generation.stored_viva(paper.paper_id)
        if not viva:
            if st.button("Generate Viva Questions", type="primary"):
                try:
                    with st.spinner("Generating grounded viva questions…"):
                        viva = generation.viva(paper.paper_id)

                        if viva is None:
                            viva = generation.stored_viva(paper.paper_id)

                        if viva:
                            st.success("Viva questions generated.")
                        else:
                            st.error("Viva questions were not returned by the generation service.")
                except ResearchAIError as error:
                    st.error(str(error))
        if viva:
            st.markdown(
        """
        <div class="section-intro">
            <h3>🎓 AI-Generated Viva Bank</h3>
            <p>
                20 paper-specific questions covering concepts, technical
                details, methodology, results and critical research thinking.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if viva:
            tabs = st.tabs(list(viva))

            for tab, (category, entries) in zip(tabs, viva.items()):
                with tab:
                    st.subheader(category)

                    if entries:
                        for position, entry in enumerate(entries, start=1):
                            st.markdown(f"### Question {position}")
                            st.markdown(f"**Question:** {entry.get('question', '')}")
                            st.markdown(f"**Answer:** {entry.get('answer', '')}")
                    else:
                        st.info("No questions were generated for this category.")
            else:
                st.warning(
                    "Viva questions could not be generated. "
                    "Please check the Gemini connection and try again."
                )

            for position, entry in enumerate(entries, start=1):

                st.markdown(
                    f"""
                    <div class="viva-card">
                        <div class="viva-number">
                            QUESTION {position}
                        </div>
                        <div class="viva-question">
                            {entry['question']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("💡 View Suggested Answer"):
                    st.write(entry["answer"])

elif page == "📚 Compare Papers":
    st.title("📚 Compare Research Papers")

    if len(papers) < 2:
        st.info(
            "📚 No papers selected. Upload at least two research papers to compare them."
        )

    else:
        selected = st.multiselect(
            "Selected papers",
            [paper.paper_id for paper in papers],
            default=[paper.paper_id for paper in papers[:2]],
            format_func=lambda paper_id: next(
                paper.title
                for paper in papers
                if paper.paper_id == paper_id
            ),
        )

        missing = [
            paper_id
            for paper_id in selected
            if not generation.analysis(paper_id)
        ]

        if missing:
            st.warning(
                "Generate Paper Analysis for every selected paper before comparing them."
            )

        elif len(selected) >= 2:

            if st.button("Compare Papers", type="primary"):

                try:
                    with st.spinner("Comparing research papers..."):
                        comparison = generation.comparison(selected)

                    if comparison:
                        st.success("Paper comparison generated successfully.")

                        for paper_title, details in comparison.items():

                            
                            st.subheader(f"📄 {paper_title}")

                            for field, value in details.items():
                                label = str(field).replace("_", " ").title()

                                with st.container(border=True):
                                    st.markdown(f"**{label}**")
                                    st.write(
                                        value if value not in (None, "")
                                        else "Not explicitly stated in the paper."
                                    )                                

                    else:
                        st.warning(
                            "No comparison result was generated."
                        )

                except (ResearchAIError, ValueError) as error:
                    st.error(str(error))

        else:
            st.info(
                "Select at least two papers to compare them."
            )

elif page == "🔎 Research Insights":
    st.title("🔎 Research Insights")
    if len(papers) < 2:
        st.info("Upload and analyse at least two papers to receive AI-assisted observations.")
    else:
        ids = list(dict.fromkeys(st.multiselect("Papers for insight generation", [paper.paper_id for paper in papers], default=list(dict.fromkeys(paper.paper_id for paper in papers[:2])), format_func=lambda paper_id: next(paper.title for paper in papers if paper.paper_id == paper_id))))
        if len(ids) >= 2 and st.button("Generate Research Insights", type="primary"):
            try:
                with st.spinner("Comparing grounded individual analyses…"):
                    st.session_state.latest_insights = generation.insights(ids)
            except (ResearchAIError, ValueError) as error:
                st.error(str(error))
        insights = st.session_state.latest_insights
        if insights:
            st.subheader("Common Observations")
            for item in insights["common_observations"]:
                st.write(f"• {item}")
            st.subheader("Potential Research Directions")
            for item in insights["possible_research_directions"]:
                st.write(f"💡 {item}")
            st.warning("AI-assisted observations: these suggestions are not guaranteed novel research gaps and should be verified through broader literature review.")

elif page == "📥 Reports":
    paper = require_paper()
    if paper:
        st.title("📄 Research Analysis Report")
        analysis = generation.analysis(paper.paper_id)
        if not analysis:
            st.info("Generate paper analysis before creating a report.")
        else:
            st.success("Included: paper information, structured analysis, saved viva questions, and available research insights.")
            if st.button("Generate Report", type="primary"):
                st.session_state.report = generate_report(paper.title, analysis, generation.stored_viva(paper.paper_id), st.session_state.latest_insights)
            if st.session_state.get("report"):
                st.download_button("Download PDF", st.session_state.report, file_name="Research_Analysis_Report.pdf", mime="application/pdf")
