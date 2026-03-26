import httpx
from ..config import settings


async def generate(prompt: str, system: str | None = None) -> str:
    """Generate text from LLM. Works with both Ollama (local) and OpenRouter (cloud)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    if settings.llm_provider == "openrouter":
        return await _generate_openrouter(messages)
    return await _generate_ollama(messages)


async def _generate_ollama(messages: list[dict]) -> str:
    payload = {
        "model": settings.ollama_model,
        "messages": messages,
        "stream": False,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json=payload,
            timeout=120.0,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]


async def _generate_openrouter(messages: list[dict]) -> str:
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=120.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


async def health_check() -> dict:
    """Check LLM provider connectivity. Returns {status, provider, model}."""
    provider = settings.llm_provider

    if provider == "openrouter":
        if not settings.openrouter_api_key:
            return {"status": "error", "provider": "openrouter", "model": settings.openrouter_model, "detail": "No API key configured"}
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
                    timeout=10.0,
                )
                status = "connected" if resp.status_code == 200 else "error"
        except Exception:
            status = "disconnected"
        return {"status": status, "provider": "openrouter", "model": settings.openrouter_model}

    # Ollama (default)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.ollama_base_url}/api/tags", timeout=5.0
            )
            status = "connected" if resp.status_code == 200 else "error"
    except Exception:
        status = "disconnected"
    return {"status": status, "provider": "ollama", "model": settings.ollama_model}
