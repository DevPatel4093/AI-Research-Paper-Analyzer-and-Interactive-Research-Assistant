from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Chunk, Paper


class Repository:
    """SQLite metadata store; Chroma owns the embedding vectors."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY, filename TEXT NOT NULL, title TEXT NOT NULL,
                    authors TEXT NOT NULL, publication_info TEXT NOT NULL, page_count INTEGER NOT NULL,
                    section_count INTEGER NOT NULL, chunk_count INTEGER NOT NULL, uploaded_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY, paper_id TEXT NOT NULL, page_number INTEGER NOT NULL,
                    section TEXT NOT NULL, chunk_index INTEGER NOT NULL, text TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS analyses (paper_id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, paper_id TEXT NOT NULL, role TEXT NOT NULL,
                    content TEXT NOT NULL, sources TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS viva (paper_id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS insights (paper_ids TEXT PRIMARY KEY, payload TEXT NOT NULL);
                """
            )

    def save_paper(self, paper: Paper, chunks: list[Chunk]) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (paper.paper_id, paper.filename, paper.title, paper.authors, paper.publication_info,
                 paper.page_count, paper.section_count, paper.chunk_count, paper.uploaded_at),
            )
            db.executemany(
                "INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?, ?, ?)",
                [(c.chunk_id, c.paper_id, c.page_number, c.section, c.chunk_index, c.text) for c in chunks],
            )

    def papers(self) -> list[Paper]:
        with self._connect() as db:
            return [Paper(**dict(row)) for row in db.execute("SELECT * FROM papers ORDER BY uploaded_at DESC")]

    def paper(self, paper_id: str) -> Paper | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM papers WHERE paper_id = ?", (paper_id,)).fetchone()
            return Paper(**dict(row)) if row else None

    def chunks_for(self, paper_id: str, limit: int | None = None) -> list[Chunk]:
        statement = "SELECT * FROM chunks WHERE paper_id = ? ORDER BY chunk_index"
        if limit:
            statement += f" LIMIT {int(limit)}"
        with self._connect() as db:
            paper = self.paper(paper_id)
            if not paper:
                return []
            return [Chunk(paper_id, paper.title, row["chunk_id"], row["page_number"], row["section"], row["chunk_index"], row["text"])
                    for row in db.execute(statement, (paper_id,))]

    def save_json(self, table: str, key: str, payload: object) -> None:
        with self._connect() as db:
            if table == "insights":
                db.execute("INSERT OR REPLACE INTO insights (paper_ids, payload) VALUES (?, ?)", (key, json.dumps(payload)))
            else:
                db.execute(f"INSERT OR REPLACE INTO {table} (paper_id, payload) VALUES (?, ?)", (key, json.dumps(payload)))

    def load_json(self, table: str, key: str) -> object | None:
        column = "paper_ids" if table == "insights" else "paper_id"
        with self._connect() as db:
            row = db.execute(f"SELECT payload FROM {table} WHERE {column} = ?", (key,)).fetchone()
            return json.loads(row["payload"]) if row else None

    def add_message(self, paper_id: str, role: str, content: str, sources: list[dict]) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO conversations (paper_id, role, content, sources) VALUES (?, ?, ?, ?)",
                       (paper_id, role, content, json.dumps(sources)))

    def history(self, paper_id: str, limit: int = 6) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT role, content, sources FROM conversations WHERE paper_id = ? ORDER BY id DESC LIMIT ?", (paper_id, limit)).fetchall()
            return [dict(row) | {"sources": json.loads(row["sources"])} for row in reversed(rows)]
