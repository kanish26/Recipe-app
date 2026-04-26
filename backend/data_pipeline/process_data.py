"""Normalize all three raw datasets into a single processed.parquet file.

Output schema (one row per recipe):
    title, ingredients(list[str]), instructions(str), cuisine(str),
    prep_time(int|None), cook_time(int|None), servings(int|None), source(str)
"""
from __future__ import annotations
import argparse
import ast
import json
import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW = DATA_DIR / "raw"
PROCESSED = DATA_DIR / "processed"


def _find_csv(root: Path, needle: str) -> Path | None:
    for p in root.rglob("*.csv"):
        if needle.lower() in p.name.lower():
            return p
    return None


def _to_list(val) -> list[str]:
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return []
    s = str(val).strip()
    if not s:
        return []
    for parser in (json.loads, ast.literal_eval):
        try:
            parsed = parser(s)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except Exception:
            pass
    return [part.strip() for part in re.split(r"[\n;,]", s) if part.strip()]


def _join_steps(val) -> str:
    items = _to_list(val)
    if not items:
        return str(val or "").strip()
    return "\n".join(f"{i+1}. {step}" for i, step in enumerate(items))


def load_foodcom(limit: int) -> pd.DataFrame:
    csv = _find_csv(RAW / "foodcom", "RAW_recipes") or _find_csv(RAW / "foodcom", "recipes")
    if not csv:
        print("[foodcom] no CSV found, skipping")
        return pd.DataFrame()
    df = pd.read_csv(csv, nrows=limit * 3)  # oversample, then filter
    df = df.dropna(subset=["name", "ingredients", "steps"]).head(limit)
    return pd.DataFrame({
        "title": df["name"].astype(str),
        "ingredients": df["ingredients"].apply(_to_list),
        "instructions": df["steps"].apply(_join_steps),
        "cuisine": "",
        "prep_time": pd.NA,
        "cook_time": df.get("minutes", pd.Series([pd.NA] * len(df))).astype("Int64"),
        "servings": pd.NA,
        "source": "food.com",
    })


def load_recipenlg(limit: int) -> pd.DataFrame:
    csv = _find_csv(RAW / "recipenlg", "full_dataset") or _find_csv(RAW / "recipenlg", "recipenlg")
    if not csv:
        print("[recipenlg] no CSV found, skipping")
        return pd.DataFrame()
    df = pd.read_csv(csv, nrows=limit * 3)
    df = df.dropna(subset=["title", "ingredients", "directions"]).head(limit)
    return pd.DataFrame({
        "title": df["title"].astype(str),
        "ingredients": df["ingredients"].apply(_to_list),
        "instructions": df["directions"].apply(_join_steps),
        "cuisine": "",
        "prep_time": pd.NA,
        "cook_time": pd.NA,
        "servings": pd.NA,
        "source": "recipenlg",
    })


def load_indian(limit: int) -> pd.DataFrame:
    csv = _find_csv(RAW / "indian", "indian_food") or next(iter((RAW / "indian").rglob("*.csv")), None)
    if not csv:
        print("[indian] no CSV found, skipping")
        return pd.DataFrame()
    df = pd.read_csv(csv).head(limit)
    ingredients = df["ingredients"].apply(_to_list) if "ingredients" in df.columns else [[] for _ in range(len(df))]
    instructions = df["instructions"] if "instructions" in df.columns else df.get("description", pd.Series([""] * len(df)))
    return pd.DataFrame({
        "title": df["name"].astype(str) if "name" in df.columns else df.iloc[:, 0].astype(str),
        "ingredients": ingredients,
        "instructions": instructions.fillna("").astype(str),
        "cuisine": df.get("region", pd.Series(["Indian"] * len(df))).fillna("Indian").astype(str),
        "prep_time": df.get("prep_time", pd.Series([pd.NA] * len(df))).astype("Int64") if "prep_time" in df.columns else pd.NA,
        "cook_time": df.get("cook_time", pd.Series([pd.NA] * len(df))).astype("Int64") if "cook_time" in df.columns else pd.NA,
        "servings": pd.NA,
        "source": "indian-food-101",
    })


def load_indian_6k(limit: int) -> pd.DataFrame:
    csv = next(iter((RAW / "indian_6k").rglob("*.csv")), None)
    if not csv:
        print("[indian_6k] no CSV found, skipping")
        return pd.DataFrame()
    df = pd.read_csv(csv).head(limit)
    cols = {c.lower(): c for c in df.columns}
    name_col = cols.get("translatedrecipename") or cols.get("recipename") or cols.get("name") or list(df.columns)[0]
    ing_col = cols.get("translatedingredients") or cols.get("ingredients") or cols.get("cleanedingredients")
    inst_col = cols.get("translatedinstructions") or cols.get("instructions")
    cuisine_col = cols.get("cuisine")
    prep_col = cols.get("preptimeinmins") or cols.get("prep_time")
    cook_col = cols.get("cooktimeinmins") or cols.get("cook_time")
    serv_col = cols.get("servings")
    ingredients = df[ing_col].apply(_to_list) if ing_col else [[] for _ in range(len(df))]
    instructions = df[inst_col].fillna("").astype(str) if inst_col else pd.Series([""] * len(df))
    return pd.DataFrame({
        "title": df[name_col].astype(str),
        "ingredients": ingredients,
        "instructions": instructions,
        "cuisine": df[cuisine_col].fillna("Indian").astype(str) if cuisine_col else pd.Series(["Indian"] * len(df)),
        "prep_time": pd.to_numeric(df[prep_col], errors="coerce").astype("Int64") if prep_col else pd.NA,
        "cook_time": pd.to_numeric(df[cook_col], errors="coerce").astype("Int64") if cook_col else pd.NA,
        "servings": pd.to_numeric(df[serv_col], errors="coerce").astype("Int64") if serv_col else pd.NA,
        "source": "indian-6k",
    })


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--foodcom", type=int, default=400)
    ap.add_argument("--recipenlg", type=int, default=400)
    ap.add_argument("--indian", type=int, default=200)
    ap.add_argument("--indian-6k", dest="indian_6k", type=int, default=6000)
    args = ap.parse_args()

    frames = [
        load_foodcom(args.foodcom),
        load_recipenlg(args.recipenlg),
        load_indian(args.indian),
        load_indian_6k(args.indian_6k),
    ]
    frames = [f for f in frames if not f.empty]
    if not frames:
        raise SystemExit("No data loaded. Did you run download_datasets.py?")

    out = pd.concat(frames, ignore_index=True)
    out = out[out["ingredients"].apply(lambda x: len(x) >= 2)].reset_index(drop=True)
    out = out[out["title"].str.len().between(3, 200)].reset_index(drop=True)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    path = PROCESSED / "processed.parquet"
    out.to_parquet(path, index=False)
    print(f"Wrote {len(out)} recipes -> {path}")
    print(out["source"].value_counts().to_string())


if __name__ == "__main__":
    main()
