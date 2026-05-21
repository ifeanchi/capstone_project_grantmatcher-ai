"""Seed the SQLite grant catalog from JSON data."""

import json
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "data" / "grants.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS grants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    organization TEXT,
    field TEXT,
    source TEXT,
    deadline DATE,
    min_amount INTEGER,
    max_amount INTEGER,
    eligibility TEXT,
    description TEXT,
    url TEXT,
    chroma_synced_at TIMESTAMP,
    embedding TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(title, organization)
);
"""


def initialize_database(db_path: str = str(DB_PATH)) -> None:
    db_path_obj = Path(db_path)
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()

    print(f"Initialized SQLite database at: {db_path}")


def seed_from_json(json_path: str = str(DATA_DIR / "foundation_grants.json")) -> None:
    initialize_database()

    with open(json_path, "r", encoding="utf-8") as json_file:
        records = json.load(json_file)

    if not isinstance(records, list):
        raise ValueError("Expected a JSON array of grant records.")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for record in records:
            cursor.execute(
                """
                INSERT OR IGNORE INTO grants
                (title, organization, field, source, deadline, min_amount, max_amount, eligibility, description, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.get("title"),
                    record.get("organization"),
                    record.get("field"),
                    record.get("source", "manual"),
                    record.get("deadline"),
                    record.get("min_amount"),
                    record.get("max_amount"),
                    record.get("eligibility"),
                    record.get("description"),
                    record.get("url"),
                ),
            )
        conn.commit()

    print(f"Seeded grants from {json_path} into {DB_PATH}")


if __name__ == "__main__":
    seed_from_json()
