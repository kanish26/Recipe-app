"""Vibe-based retrieval + optional LLM narrative."""
from __future__ import annotations
import re

from app.models.recipe import Recipe
from app.services import llm_service
from app.services.embeddings import embed_one
from app.services.supabase_client import get_client

VIBES = [
    "cozy comfort", "fresh summer", "quick weeknight", "hearty winter",
    "light healthy", "spicy bold", "sweet treat", "celebratory",
    "rainy day", "date night", "family dinner", "post-workout",
]

MEAT_WORDS = [
    "chicken", "beef", "pork", "lamb", "fish", "shrimp", "prawn", "bacon",
    "sausage", "ham", "turkey", "salmon", "tuna", "anchovy", "duck", "mutton",
    "crab", "lobster", "oyster", "scallop", "mussel", "venison", "veal",
    "pepperoni", "chorizo", "pancetta", "cod", "trout", "halibut",
]
ANIMAL_PRODUCT_WORDS = [
    "milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "egg", "eggs",
    "honey", "ghee", "paneer", "whey", "casein", "mayonnaise",
]
GLUTEN_WORDS = [
    "wheat", "flour", "bread", "pasta", "noodle", "barley", "rye", "soy sauce",
    "bulgur", "couscous", "breadcrumb", "panko", "semolina", "crouton", "seitan",
    "tortilla", "pita", "bagel", "cracker", "pastry", "pie crust",
]


def _has_any(ingredients: list[str], words: list[str]) -> bool:
    text = " ".join(ingredients).lower()
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def _matches_diet(ingredients: list[str], diet: str) -> bool:
    if diet == "any":
        return True
    has_meat = _has_any(ingredients, MEAT_WORDS)
    if diet == "non-vegetarian":
        return has_meat
    if diet == "vegetarian":
        return not has_meat
    if diet == "vegan":
        return not has_meat and not _has_any(ingredients, ANIMAL_PRODUCT_WORDS)
    if diet == "gluten-free":
        return not _has_any(ingredients, GLUTEN_WORDS)
    return True


def match_vibes(query: str) -> list[str]:
    """Return the subset of canonical vibes that appear in the free-text query."""
    q = query.lower()
    hits = [v for v in VIBES if any(tok in q for tok in v.split())]
    return hits or []


def search(
    vibe: str,
    inventory: list[str] | None = None,
    vibes_filter: list[str] | None = None,
    diet: str = "any",
    limit: int = 10,
) -> list[Recipe]:
    inventory = inventory or []
    query_text = vibe
    if inventory:
        query_text += "\nAvailable ingredients: " + ", ".join(inventory)
    if diet != "any":
        query_text += f"\nDiet: {diet}"

    embedding = embed_one(query_text)
    filter_vibes = vibes_filter or match_vibes(vibe) or None
    # Oversample so diet post-filter still returns `limit` items.
    oversample = limit * 4 if diet != "any" else limit

    client = get_client()
    resp = client.rpc(
        "match_recipes",
        {"query_embedding": embedding, "match_count": oversample, "filter_vibes": filter_vibes},
    ).execute()
    rows = resp.data or []

    # Fallback: if a strict vibe filter returned nothing, drop the filter.
    if not rows and filter_vibes:
        resp = client.rpc(
            "match_recipes",
            {"query_embedding": embedding, "match_count": oversample, "filter_vibes": None},
        ).execute()
        rows = resp.data or []

    filtered = [r for r in rows if _matches_diet(r.get("ingredients") or [], diet)]
    return [Recipe(**row) for row in filtered[:limit]]


def narrate(vibe: str, recipes: list[Recipe]) -> str:
    if not recipes:
        return "No recipes matched that vibe yet."
    top = recipes[:3]
    bullets = "\n".join(f"- {r.title} (vibes: {', '.join(r.vibes)})" for r in top)
    prompt = (
        f"A user is craving '{vibe}'. In 2-3 warm sentences, recommend these recipes "
        f"and hint why they fit the vibe. No preamble, no list format.\n\n{bullets}"
    )
    try:
        return llm_service.generate(prompt).strip()
    except Exception:
        return f"Try {top[0].title} — it fits '{vibe}' perfectly."
