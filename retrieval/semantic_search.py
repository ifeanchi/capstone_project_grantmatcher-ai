"""ChromaDB semantic search logic for grant retrieval."""

from typing import List, Dict
from pathlib import Path
import sqlite3

from sentence_transformers import SentenceTransformer


def semantic_search(query: str, top_k: int = 5) -> List[Dict]:
    """Return top grant matches for a query using ChromaDB."""
    BASE_DIR = Path(__file__).resolve().parent.parent

    # init model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    persist_dir = str(BASE_DIR / ".chromadb")
    collection = None
    try:
        import chromadb
        from chromadb.config import Settings

        client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=persist_dir))
        collection = client.get_or_create_collection(name="grantmatcher")
    except ImportError:
        print("Chromadb not installed, falling back to SQLite search.")
    except Exception as exc:
        print("Chroma client/create_collection failed, falling back to SQLite search:", exc)

    q_emb = model.encode([query])[0]
    if collection is not None:
        try:
            results = collection.query(query_embeddings=[q_emb], n_results=top_k, include=["metadatas", "documents", "distances", "ids"])
            ids = [int(i) for i in results.get("ids", [[]])[0]]
            distances = results.get("distances", [[]])[0]

            DB_PATH = BASE_DIR / "data" / "grants.db"
            matches: List[Dict] = []
            if ids:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    for sid, dist in zip(ids, distances):
                        cursor.execute("SELECT id, title, organization, field, source, deadline, min_amount, max_amount, eligibility, description, url FROM grants WHERE id = ?", (sid,))
                        row = cursor.fetchone()
                        if not row:
                            continue
                        columns = ["id", "title", "organization", "field", "source", "deadline", "min_amount", "max_amount", "eligibility", "description", "url"]
                        record = dict(zip(columns, row))
                        record["_distance"] = dist
                        matches.append(record)
            return matches
        except Exception as exc:
            print("Chroma query failed, falling back to SQLite search:", exc)

    # fallback: use embeddings stored in SQLite and do cosine similarity locally
    import json
    import numpy as np

    DB_PATH = BASE_DIR / "data" / "grants.db"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, embedding FROM grants WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()

    if not rows:
        return []

    embeddings = []
    ids = []
    for rid, emb_text in rows:
        try:
            vec = np.array(json.loads(emb_text), dtype=float)
            embeddings.append(vec)
            ids.append(rid)
        except Exception:
            continue

    if not embeddings:
        return []

    query_vec = np.array(q_emb, dtype=float)
    emb_matrix = np.vstack(embeddings)
    norms = np.linalg.norm(emb_matrix, axis=1) * np.linalg.norm(query_vec)
    sims = (emb_matrix @ query_vec) / (norms + 1e-12)
    top_idx = sims.argsort()[::-1][:top_k]

    matches = []
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for i in top_idx:
            sid = ids[int(i)]
            sim = float(sims[int(i)])
            cursor.execute("SELECT id, title, organization, field, source, deadline, min_amount, max_amount, eligibility, description, url FROM grants WHERE id = ?", (sid,))
            row = cursor.fetchone()
            if not row:
                continue
            columns = ["id", "title", "organization", "field", "source", "deadline", "min_amount", "max_amount", "eligibility", "description", "url"]
            record = dict(zip(columns, row))
            record["_similarity"] = sim
            matches.append(record)

    return matches
