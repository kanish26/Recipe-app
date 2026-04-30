from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services import supabase_client, llm_service
from app.routes import recipes as recipes_routes

app = FastAPI(title="Recipe Vibe API")
app.include_router(recipes_routes.router)

import os
_extra_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", *_extra_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    checks = {"api": "ok"}
    try:
        supabase_client.ping(); checks["supabase"] = "ok"
    except Exception:
        checks["supabase"] = "error"
    try:
        llm_service.ping(); checks["llm"] = "ok"
    except Exception:
        checks["llm"] = "error"
    checks["status"] = "ok" if all(v == "ok" for k, v in checks.items() if k != "status") else "degraded"
    return checks
