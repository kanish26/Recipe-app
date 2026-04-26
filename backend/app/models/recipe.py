from __future__ import annotations
from pydantic import BaseModel


class Recipe(BaseModel):
    id: int
    title: str
    ingredients: list[str] = []
    instructions: str = ""
    cuisine: str | None = None
    vibes: list[str] = []
    similarity: float | None = None
