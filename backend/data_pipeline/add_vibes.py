"""Tag each recipe with 1-3 vibes using a fast keyword heuristic, refined by Mistral for ambiguous cases.

For the 1000-recipe seed run we default to keyword-only (seconds). Pass --llm to
enable Mistral refinement (slower: ~30-60 min for 1000 recipes, but higher quality).
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"

VIBES = [
    "cozy comfort", "fresh summer", "quick weeknight", "hearty winter",
    "light healthy", "spicy bold", "sweet treat", "celebratory",
    "rainy day", "date night", "family dinner", "post-workout",
]

KEYWORDS: dict[str, list[str]] = {
    "cozy comfort": ["stew", "casserole", "mac and cheese", "mashed", "pot pie", "soup", "chili", "meatloaf", "gravy"],
    "fresh summer": ["salad", "gazpacho", "ceviche", "watermelon", "cucumber", "cold", "grill", "mint", "lemon"],
    "quick weeknight": ["15 minute", "20 minute", "quick", "easy", "weeknight", "sheet pan", "one pot", "stir fry"],
    "hearty winter": ["roast", "braised", "stew", "pot roast", "slow cook", "dumpling", "shepherd", "beef"],
    "light healthy": ["salad", "grilled chicken", "steamed", "low calorie", "low fat", "quinoa", "tofu", "veggie"],
    "spicy bold": ["spicy", "chili", "sriracha", "jalapeno", "curry", "cajun", "szechuan", "hot sauce", "masala"],
    "sweet treat": ["cake", "cookie", "brownie", "pie", "ice cream", "chocolate", "pudding", "tart", "dessert"],
    "celebratory": ["roast", "wellington", "lobster", "prime rib", "holiday", "christmas", "thanksgiving", "cake"],
    "rainy day": ["soup", "stew", "ramen", "hot chocolate", "grilled cheese", "tomato soup"],
    "date night": ["steak", "pasta", "risotto", "wine", "scallop", "truffle", "filet", "lamb"],
    "family dinner": ["lasagna", "casserole", "pasta", "meatball", "pizza", "chicken", "pot roast"],
    "post-workout": ["chicken", "quinoa", "protein", "salmon", "egg", "yogurt", "oat", "banana"],
}


def score(text: str) -> list[tuple[str, int]]:
    scored = []
    for vibe, kws in KEYWORDS.items():
        count = sum(1 for kw in kws if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE))
        if count:
            scored.append((vibe, count))
    return sorted(scored, key=lambda x: -x[1])


def keyword_vibes(row) -> list[str]:
    text = f"{row['title']} {' '.join(row['ingredients'])} {row['instructions'][:500]}"
    ranked = score(text)
    picks = [v for v, _ in ranked[:3]]
    return picks or ["family dinner"]


def llm_vibes(row, client, model: str) -> list[str]:
    prompt = (
        f"Given this recipe, return 1-3 vibes from: {', '.join(VIBES)}.\n"
        f"Respond with ONLY a JSON array of strings, nothing else.\n\n"
        f"Title: {row['title']}\nIngredients: {', '.join(row['ingredients'][:12])}\n"
    )
    try:
        resp = client.chat(model=model, messages=[{"role": "user", "content": prompt}])
        content = resp["message"]["content"].strip()
        match = re.search(r"\[.*?\]", content, re.DOTALL)
        if match:
            picks = json.loads(match.group(0))
            valid = [v for v in picks if v in VIBES]
            if valid:
                return valid[:3]
    except Exception as e:
        print(f"[llm fallback] {e}", file=sys.stderr)
    return keyword_vibes(row)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="Refine with Mistral (slower)")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    df = pd.read_parquet(PROCESSED / "processed.parquet")
    if args.limit:
        df = df.head(args.limit).copy()

    if args.llm:
        from app.services import llm_service
        tqdm.pandas(desc="LLM vibe-tag")
        df["vibes"] = df.progress_apply(lambda r: llm_vibes(r, llm_service._client, "mistral"), axis=1)
    else:
        tqdm.pandas(desc="keyword vibe-tag")
        df["vibes"] = df.progress_apply(keyword_vibes, axis=1)

    path = PROCESSED / "vibed.parquet"
    df.to_parquet(path, index=False)
    print(f"Wrote {len(df)} recipes with vibes -> {path}")
    print("Vibe distribution:")
    print(df["vibes"].explode().value_counts().to_string())


if __name__ == "__main__":
    main()
