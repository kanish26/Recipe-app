"""Load embedded.parquet into the Supabase `recipes` table in batches.

Supports resume via --start-from (row offset in the parquet) so a mid-run crash
can be resumed without duplicating.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.supabase_client import get_client

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"


def _row_to_record(row) -> dict:
    return {
        "title": row["title"],
        "ingredients": list(row["ingredients"]),
        "instructions": row["instructions"],
        "cuisine": row["cuisine"] or None,
        "prep_time": int(row["prep_time"]) if pd.notna(row["prep_time"]) else None,
        "cook_time": int(row["cook_time"]) if pd.notna(row["cook_time"]) else None,
        "servings": int(row["servings"]) if pd.notna(row["servings"]) else None,
        "vibes": list(row["vibes"]),
        "source": row["source"],
        "embedding": list(row["embedding"]),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--truncate", action="store_true", help="Delete existing rows first")
    ap.add_argument("--start-from", type=int, default=0, help="Resume from this row offset")
    args = ap.parse_args()

    df = pd.read_parquet(PROCESSED / "embedded.parquet")
    client = get_client()

    if args.truncate:
        print("Truncating recipes table...")
        client.table("recipes").delete().neq("id", 0).execute()

    if args.start_from:
        df = df.iloc[args.start_from :].reset_index(drop=True)
        print(f"Resuming from offset {args.start_from}, {len(df)} rows remaining")

    print(f"Inserting {len(df)} recipes in batches of {args.batch}...")
    for i in tqdm(range(0, len(df), args.batch)):
        chunk = [_row_to_record(r) for _, r in df.iloc[i : i + args.batch].iterrows()]
        client.table("recipes").insert(chunk).execute()
    print("Done.")


if __name__ == "__main__":
    main()
