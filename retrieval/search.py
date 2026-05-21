"""Simple local search over `data/mock_grants.json` for development/testing."""

import json
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
MOCK_PATH = BASE_DIR / "data" / "mock_grants.json"


def load_mock_grants() -> List[Dict]:
    with open(MOCK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _score_record(record: Dict, query_terms: List[str]) -> int:
    text = " ".join([str(record.get("title", "")), str(record.get("description", ""))]).lower()
    score = 0
    for term in query_terms:
        if term in text:
            score += text.count(term)
    return score


def search_grants(query: str, top_k: int = 5) -> List[Dict]:
    """Return top_k grants from the mock dataset matching the query (simple term overlap).

    This is a stand-in for semantic search so the app can be tested without Chroma.
    """
    records = load_mock_grants()
    if not query or not query.strip():
        return records[:top_k]

    terms = [t.strip().lower() for t in query.split() if t.strip()]
    scored = []
    for r in records:
        score = _score_record(r, terms)
        if score > 0:
            r_copy = dict(r)
            r_copy["_score"] = score
            scored.append(r_copy)

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return scored[:top_k]
