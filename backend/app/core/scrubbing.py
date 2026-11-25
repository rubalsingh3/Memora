from __future__ import annotations

import re
from typing import Any

SECRET_KEYS = frozenset({
    "api_key",
    "apikey",
    "secret",
    "secret_key",
    "token",
    "session_token",
    "token_hash",
    "password",
    "authorization",
    "x-session-token",
})

REDACTED_FIELDS = frozenset({
    "content",
    "prompt",
    "answer",
    "response",
    "raw",
    "text",
})

_KEY_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"sk-[0-9A-Za-z\-_]{16,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
]


def redact_text(value: str) -> str:
    cleaned = value
    for pattern in _KEY_PATTERNS:
        cleaned = pattern.sub("[REDACTED_KEY]", cleaned)
    return cleaned


def scrub_payload(data: Any) -> Any:
    if isinstance(data, dict):
        out: dict[str, Any] = {}
        for k, v in data.items():
            key_lower = str(k).lower()
            if key_lower in SECRET_KEYS:
                continue
            if key_lower in REDACTED_FIELDS and isinstance(v, str):
                out[k] = "[REDACTED]"
            else:
                out[k] = scrub_payload(v)
        return out
    if isinstance(data, list):
        return [scrub_payload(item) for item in data]
    if isinstance(data, str):
        return redact_text(data)
    return data