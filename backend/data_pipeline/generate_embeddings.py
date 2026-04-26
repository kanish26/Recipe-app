"""Generate embeddings in resumable chunks and write embedded.parquet.

Saves progress every CHUNK rows to embedded_partial.parquet so a crash doesn't restart.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.embeddings import embed, recipe_text

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
CHUNK = 5000


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-size", type=int, default=256, help="model batch size")
    args = ap.parse_args()

    df = pd.read_parquet(PROCESSED / "vibed.parquet").reset_index(drop=True)
    n = len(df)
    print(f"Embedding {n} recipes in chunks of {CHUNK}...")

    partial_path = PROCESSED / "embedded_partial.parquet"
    if partial_path.exists():
        done = pd.read_parquet(partial_path)
        start = len(done)
        print(f"[resume] found {start} already-embedded rows in {partial_path.name}")
        vectors: list[list[float]] = done["embedding"].tolist()
    else:
        start = 0
        vectors = []

    for i in tqdm(range(start, n, CHUNK), desc="chunks"):
        slab = df.iloc[i : i + CHUNK]
        texts = [
            recipe_text(r["title"], list(r["ingredients"]), r["instructions"], list(r["vibes"]))
            for _, r in slab.iterrows()
        ]
        vectors.extend(embed(texts, batch_size=args.batch_size, show_progress=False))

        # checkpoint
        snap = df.iloc[: len(vectors)].copy()
        snap["embedding"] = vectors
        snap.to_parquet(partial_path, index=False)

    df["embedding"] = vectors
    final = PROCESSED / "embedded.parquet"
    df.to_parquet(final, index=False)
    partial_path.unlink(missing_ok=True)
    print(f"Wrote {len(df)} recipes with embeddings -> {final}")


if __name__ == "__main__":
    main()
