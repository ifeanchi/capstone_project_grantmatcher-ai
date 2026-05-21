"""Fetch grant data from APIs or manual sources and upsert into SQLite."""

import argparse
import sqlite3
from pathlib import Path

from ingestion.grants_gov import fetch_grants_gov
from ingestion.nsf import fetch_nsf_awards
from ingestion.nih import fetch_nih_awards

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "grants.db"


def upsert_grants(records: list[dict], source: str) -> None:
    if not records:
        print("No records to upsert.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for record in records:
            cursor.execute(
                """
                INSERT OR REPLACE INTO grants
                (title, organization, field, source, deadline, min_amount, max_amount, eligibility, description, url, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    record.get("title"),
                    record.get("organization"),
                    record.get("field"),
                    source,
                    record.get("deadline"),
                    record.get("min_amount"),
                    record.get("max_amount"),
                    record.get("eligibility"),
                    record.get("description"),
                    record.get("url"),
                ),
            )
        conn.commit()

    print(f"Upserted {len(records)} records from {source} into SQLite")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and upsert grant data into SQLite.")
    parser.add_argument("--source", required=True, choices=["grants_gov", "nsf", "nih"], help="Source to fetch grants from")
    parser.add_argument("--keyword", required=False, help="Search keyword for API fetch")
    args = parser.parse_args()

    if args.source == "grants_gov":
        records = fetch_grants_gov(args.keyword or "nonprofit")
    elif args.source == "nsf":
        records = fetch_nsf_awards(args.keyword or "research")
    else:
        records = fetch_nih_awards(args.keyword or "health")

    upsert_grants(records, source=args.source)


if __name__ == "__main__":
    main()
