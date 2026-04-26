"""Download the three source datasets from Kaggle into backend/data/raw/."""
from __future__ import annotations
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATASETS = [
    ("shuyangli94/food-com-recipes-and-user-interactions", "foodcom"),
    ("paultimothymooney/recipenlg", "recipenlg"),
    ("nehaprabhavalkar/indian-food-101", "indian"),
    ("sooryaprakash12/cleaned-indian-recipes-dataset", "indian_6k"),
]

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def main() -> None:
    if not os.getenv("KAGGLE_API_TOKEN") and not (Path.home() / ".kaggle" / "kaggle.json").exists():
        print("Error: KAGGLE_API_TOKEN not set and no ~/.kaggle/kaggle.json found.", file=sys.stderr)
        sys.exit(1)

    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for slug, name in DATASETS:
        target = DATA_DIR / name
        if target.exists() and any(target.iterdir()):
            print(f"[skip] {name} already downloaded at {target}")
            continue
        target.mkdir(parents=True, exist_ok=True)
        print(f"[download] {slug} -> {target}")
        api.dataset_download_files(slug, path=str(target), unzip=True, quiet=False)
    print("Done.")


if __name__ == "__main__":
    main()
