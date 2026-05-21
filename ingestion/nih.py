"""Client for the NIH RePORTER API."""

import requests
from typing import List, Dict


def fetch_nih_awards(query: str, max_results: int = 25) -> List[Dict]:
    """Fetch NIH awards from the RePORTER API."""
    url = "https://api.reporter.nih.gov/v2/projects/search"
    payload = {
        "criteria": {
            "queryText": query
        },
        "includeFields": ["project_title", "org_name", "project_start_date", "project_end_date", "abstract_text", "fy_cost"],
        "offset": 0,
        "limit": max_results,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json().get("results", [])

    grants = []
    for item in data:
        grants.append(
            {
                "title": item.get("project_title"),
                "organization": item.get("org_name"),
                "field": None,
                "source": "nih",
                "deadline": item.get("project_end_date"),
                "min_amount": None,
                "max_amount": item.get("fy_cost"),
                "eligibility": None,
                "description": item.get("abstract_text"),
                "url": None,
            }
        )
    return grants
