"""LLM wrapper. Priority: Groq → Cerebras → Ollama (local).

Set GROQ_API_KEY or CEREBRAS_API_KEY in env to use cloud providers.
If neither is set, falls back to local Ollama.
"""
from __future__ import annotations

from app.utils.config import (
    CEREBRAS_API_KEY, CEREBRAS_MODEL,
    GROQ_API_KEY, GROQ_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
)

_provider: str
_groq_client = None
_cerebras_client = None
_ollama_client = None

if GROQ_API_KEY:
    from groq import Groq
    _groq_client = Groq(api_key=GROQ_API_KEY)
    _provider = "groq"
elif CEREBRAS_API_KEY:
    from openai import OpenAI
    _cerebras_client = OpenAI(
        api_key=CEREBRAS_API_KEY,
        base_url="https://api.cerebras.ai/v1",
    )
    _provider = "cerebras"
else:
    import ollama
    _ollama_client = ollama.Client(host=OLLAMA_BASE_URL)
    _provider = "ollama"


def provider() -> str:
    return _provider


def generate(prompt: str, system: str | None = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    if _provider == "groq":
        resp = _groq_client.chat.completions.create(model=GROQ_MODEL, messages=messages)
        return resp.choices[0].message.content

    if _provider == "cerebras":
        resp = _cerebras_client.chat.completions.create(model=CEREBRAS_MODEL, messages=messages)
        return resp.choices[0].message.content

    resp = _ollama_client.chat(model=OLLAMA_MODEL, messages=messages)
    return resp["message"]["content"]


def ping() -> bool:
    if _provider == "groq":
        _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
        return True

    if _provider == "cerebras":
        _cerebras_client.chat.completions.create(
            model=CEREBRAS_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
        return True

    models = _ollama_client.list().get("models", [])
    names = [m.get("name") or m.get("model") for m in models]
    if not any(OLLAMA_MODEL in (n or "") for n in names):
        raise RuntimeError(f"Ollama model '{OLLAMA_MODEL}' not found. Run: ollama pull {OLLAMA_MODEL}")
    return True
