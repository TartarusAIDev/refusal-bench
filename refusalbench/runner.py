"""Send prompts to any OpenAI-compatible /chat/completions endpoint."""
from __future__ import annotations

import json
import urllib.error
import urllib.request


class ApiError(RuntimeError):
    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"HTTP {status}: {body[:200]}")
        self.status = status


def complete(
    *,
    endpoint: str,
    model: str,
    token: str,
    prompt: str,
    max_tokens: int = 512,
    timeout: float = 90.0,
) -> str:
    """Return the assistant message content for a single user prompt."""
    url = endpoint.rstrip("/") + "/chat/completions"
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.0,
        }
    ).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:  # pragma: no cover - network path
        raise ApiError(e.code, e.read().decode(errors="replace")) from e

    choices = data.get("choices") or [{}]
    return (choices[0].get("message") or {}).get("content") or ""
