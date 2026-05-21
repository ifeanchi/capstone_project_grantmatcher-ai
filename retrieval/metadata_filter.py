"""SQLite metadata filtering utilities for grant search."""

from typing import List, Dict


def filter_active_grants(grants: List[Dict]) -> List[Dict]:
    """Filter out expired grants from the grant list."""
    from datetime import date

    active = []
    for grant in grants:
        deadline = grant.get("deadline")
        if not deadline:
            active.append(grant)
            continue

        try:
            deadline_date = date.fromisoformat(deadline)
        except ValueError:
            active.append(grant)
            continue

        if deadline_date >= date.today():
            active.append(grant)

    return active


def filter_by_field(grants: List[Dict], field: str) -> List[Dict]:
    """Filter grant results by field/topic."""
    return [grant for grant in grants if grant.get("field") and grant.get("field").lower() == field.lower()]
