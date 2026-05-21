"""Client for the NSF Awards API."""

import requests
from typing import List, Dict


def fetch_nsf_awards(query: str, max_results: int = 25) -> List[Dict]:
    """Fetch awards from the NSF Awards API."""
    url = "https://api.nsf.gov/services/v1/awards.json"
    params = {
        "keyword": query,
        "printFields": "id,title,abstractText,awardAmount,awardeeName,startDate,endDate",
        "rows": max_results,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json().get("response", {}).get("award", [])

    grants = []
    for item in data:
        grants.append(
            {
                "title": item.get("title"),
                "organization": item.get("awardeeName"),
                "field": None,
                "source": "nsf",
                "deadline": item.get("endDate"),
                "min_amount": None,
                "max_amount": item.get("awardAmount"),
                "eligibility": None,
                "description": item.get("abstractText"),
                "url": None,
            }
        )
    return grants
