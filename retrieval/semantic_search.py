"""ChromaDB semantic search logic for grant retrieval."""

from typing import List, Dict


def semantic_search(query: str, top_k: int = 5) -> List[Dict]:
    """Return top grant matches for a query using ChromaDB."""
    # TODO: implement ChromaDB query logic using embeddings
    print(f"Semantic search for: {query} (top_k={top_k})")
    return []
