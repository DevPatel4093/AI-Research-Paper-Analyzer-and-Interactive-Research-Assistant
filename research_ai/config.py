from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_dir: Path
    upload_dir: Path
    report_dir: Path
    vector_db_path: Path
    database_path: Path
    embedding_model: str
    llm_model: str
    gemini_api_key: str | None
    max_upload_bytes: int
    retrieval_top_k: int
    retrieval_max_distance: float

    @classmethod
    def from_environment(cls, base_dir: Path | None = None) -> "Settings":
        root = base_dir or Path.cwd()
        database_url = os.getenv("DATABASE_URL", "sqlite:///data/research_ai.db")
        database_path = Path(database_url.removeprefix("sqlite:///"))
        if not database_path.is_absolute():
            database_path = root / database_path
        return cls(
            base_dir=root,
            upload_dir=root / os.getenv("UPLOAD_DIR", "data/uploads"),
            report_dir=root / os.getenv("REPORT_DIR", "data/reports"),
            vector_db_path=root / os.getenv("VECTOR_DB_PATH", "data/chroma"),
            database_path=database_path,
            embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            llm_model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            max_upload_bytes=int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024,
            retrieval_top_k=int(os.getenv("RETRIEVAL_TOP_K", "5")),
            retrieval_max_distance=float(os.getenv("RETRIEVAL_MAX_DISTANCE", "0.85")),
        )

    def ensure_directories(self) -> None:
        for path in (self.upload_dir, self.report_dir, self.vector_db_path, self.database_path.parent):
            path.mkdir(parents=True, exist_ok=True)
