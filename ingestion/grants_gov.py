"""Client for the Grants.gov API."""

import requests
from typing import List, Dict


def fetch_grants_gov(keyword: str, max_results: int = 25) -> List[Dict]:
    """Fetch grant opportunities from Grants.gov by keyword."""
    url = "https://apply07.grants.gov/grantsws/rest/opportunities/search/"
    payload = {
        "keyword": keyword,
        "rows": max_results,
        "oppStatuses": "posted"
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    results = response.json().get("oppHits", [])

    grants = []
    for item in results:
        grants.append(
            {
                "title": item.get("oppTitle"),
                "organization": item.get("agencyName"),
                "field": item.get("category"),
                "source": "grants.gov",
                "deadline": item.get("closingDate"),
                "min_amount": None,
                "max_amount": None,
                "eligibility": item.get("eligibility"),
                "description": item.get("synopsis"),
                "url": item.get("url"),
            }
        )
    return grants
