import ollama
from app.utils.config import OLLAMA_BASE_URL, OLLAMA_MODEL

_client = ollama.Client(host=OLLAMA_BASE_URL)


def generate(prompt: str, system: str | None = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = _client.chat(model=OLLAMA_MODEL, messages=messages)
    return response["message"]["content"]


def ping() -> bool:
    models = _client.list().get("models", [])
    names = [m.get("name") or m.get("model") for m in models]
    if not any(OLLAMA_MODEL in (n or "") for n in names):
        raise RuntimeError(f"Ollama model '{OLLAMA_MODEL}' not found. Run: ollama pull {OLLAMA_MODEL}")
    return True
