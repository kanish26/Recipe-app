from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

from app.models.recipe import Recipe

Diet = Literal["any", "vegetarian", "vegan", "non-vegetarian", "gluten-free"]


class VibeSearchRequest(BaseModel):
    vibe: str = Field(..., description="Free-text vibe, e.g. 'cozy comfort food'")
    inventory: list[str] = Field(default_factory=list, description="Ingredients the user already has")
    vibes_filter: list[str] | None = Field(default=None, description="Optional strict vibe tag filter")
    diet: Diet = Field(default="any", description="Dietary preference")
    limit: int = Field(default=10, ge=1, le=50)


class VibeSearchResponse(BaseModel):
    query: str
    matched_vibes: list[str]
    recipes: list[Recipe]
    narrative: str | None = None
