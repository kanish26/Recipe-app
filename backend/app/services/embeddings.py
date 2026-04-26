from __future__ import annotations
from functools import lru_cache
from typing import Sequence

import torch
from sentence_transformers import SentenceTransformer

from app.utils.config import EMBEDDING_MODEL


def _pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    device = _pick_device()
    model = SentenceTransformer(EMBEDDING_MODEL, device=device)
    print(f"[embeddings] model={EMBEDDING_MODEL} device={device}")
    return model


def embed(texts: Sequence[str], batch_size: int = 128, show_progress: bool = False) -> list[list[float]]:
    vectors = get_model().encode(
        list(texts),
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return vectors.tolist()


def embed_one(text: str) -> list[float]:
    return embed([text])[0]


def recipe_text(title: str, ingredients: list[str], instructions: str, vibes: list[str] | None = None) -> str:
    parts = [title, "Ingredients: " + ", ".join(ingredients)]
    if vibes:
        parts.append("Vibes: " + ", ".join(vibes))
    parts.append(instructions[:800])
    return "\n".join(parts)
