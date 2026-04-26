from __future__ import annotations
from fastapi import APIRouter, HTTPException

from app.models.recipe import Recipe
from app.models.search import VibeSearchRequest, VibeSearchResponse
from app.services import rag_pipeline
from app.services.supabase_client import get_client

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/by-vibe", response_model=VibeSearchResponse)
def by_vibe(req: VibeSearchRequest) -> VibeSearchResponse:
    recipes = rag_pipeline.search(req.vibe, req.inventory, req.vibes_filter, req.diet, req.limit)
    narrative = rag_pipeline.narrate(req.vibe, recipes) if recipes else None
    return VibeSearchResponse(
        query=req.vibe,
        matched_vibes=rag_pipeline.match_vibes(req.vibe),
        recipes=recipes,
        narrative=narrative,
    )


@router.get("/vibes")
def list_vibes() -> dict:
    return {"vibes": rag_pipeline.VIBES}


@router.get("/{recipe_id}", response_model=Recipe)
def get_recipe(recipe_id: int) -> Recipe:
    resp = get_client().table("recipes").select(
        "id,title,ingredients,instructions,cuisine,vibes"
    ).eq("id", recipe_id).limit(1).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Recipe(**resp.data[0])
