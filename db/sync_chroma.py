"""Sync data into Chroma vector store."""

import sqlite3
from pathlib import Path
from typing import List, Dict
import time

from sentence_transformers import SentenceTransformer

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
    BASE_DIR = Path(__file__).resolve().parent.parent
    persist_dir = str(BASE_DIR / ".chromadb")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Computing embeddings (this may take a few seconds)...")
    embeddings = model.encode(docs := [record.get("description") or record.get("title") or "" for record in records], show_progress_bar=True)

    # save embeddings to SQLite first, so local fallback always works
    import json
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for record, emb in zip(records, embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings):
            cursor.execute(
                "UPDATE grants SET chroma_synced_at = ?, embedding = ? WHERE id = ?",
                (now, json.dumps(emb), int(record["id"]))
            )
        conn.commit()

    # Optional Chroma sync
    try:
        import chromadb
        from chromadb.config import Settings

        collection = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir)).get_or_create_collection(name=index_name)
        ids = [str(record["id"]) for record in records]
        metadatas = [
            {
                "sqlite_id": record["id"],
                "title": record.get("title"),
                "organization": record.get("organization"),
                "field": record.get("field"),
            }
            for record in records
        ]
        collection.add(
            ids=ids,
            documents=docs,
            metadatas=metadatas,
            embeddings=embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings,
        )
        try:
            collection.client.persist()
        except Exception:
            pass
        print(f"Synced {len(records)} records to ChromaDB (collection: {index_name}).")
    except ImportError:
        print("Chromadb not installed. Embedded vectors were stored in SQLite for fallback search.")
    except Exception as exc:
        print("Chroma sync failed, but embeddings are stored in SQLite. Error:", exc)
        print(f"Stored {len(records)} embeddings locally for fallback search.")


if __name__ == "__main__":
    sync_chroma()
