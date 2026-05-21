"""Sync data into Chroma vector store."""

import sqlite3
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "grants.db"


def get_pending_records() -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, title, organization, field, source, deadline, min_amount, max_amount,
                   eligibility, description, url
            FROM grants
            WHERE chroma_synced_at IS NULL OR chroma_synced_at < last_updated
            """
        )
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


def sync_chroma(index_name: str = "grantmatcher") -> None:
    records = get_pending_records()
    if not records:
        print("No records to sync to ChromaDB.")
        return

    print(f"Found {len(records)} records to sync to ChromaDB index '{index_name}'.")
    # TODO: implement ChromaDB embedding generation and upsert logic
    for record in records:
        print(f"Would sync record ID {record['id']}: {record['title']}")


if __name__ == "__main__":
    sync_chroma()
