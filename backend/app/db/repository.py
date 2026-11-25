from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import hmac
import secrets
from typing import Any

from backend.app.core.scrubbing import scrub_payload
from backend.app.db.client import get_supabase_client


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(raw_token: str, expected_hash: str) -> bool:
    if not raw_token or not expected_hash:
        return False
    actual_hash = hash_token(raw_token)
    return hmac.compare_digest(actual_hash, expected_hash)


@dataclass
class SessionRecord:
    session_id: str
    token_hash: str
    label: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)


class SessionRepository:
    def __init__(self, max_sessions: int = 500) -> None:
        self.max_sessions = max_sessions
        self._sessions: dict[str, SessionRecord] = {}
        self._client = get_supabase_client()
        self.persistence_available = self._probe_schema()

    def _probe_schema(self) -> bool:
        if self._client is None:
            return False
        try:
            self._client.table("sessions").select("id").limit(1).execute()
            return True
        except Exception:
            return False

    def create_session(self, label: str | None = None) -> tuple[SessionRecord, str]:
        if len(self._sessions) >= self.max_sessions:
            oldest_key = next(iter(self._sessions))
            del self._sessions[oldest_key]

        session_id = f"sess_{secrets.token_hex(8)}"
        raw_token = secrets.token_urlsafe(32)
        record = SessionRecord(
            session_id=session_id,
            token_hash=hash_token(raw_token),
            label=label,
        )
        self._sessions[session_id] = record

        if self.persistence_available and self._client is not None:
            try:
                self._client.table("sessions").insert({
                    "id": record.session_id,
                    "label": record.label,
                    "token_hash": record.token_hash,
                    "created_at": record.created_at,
                }).execute()
            except Exception:
                self.persistence_available = False

        return record, raw_token

    def get_session(self, session_id: str, raw_token: str | None) -> SessionRecord | None:
        record = self._sessions.get(session_id)
        if record is None and self.persistence_available and self._client is not None:
            try:
                res = (
                    self._client.table("sessions")
                    .select("id,label,token_hash,created_at")
                    .eq("id", session_id)
                    .limit(1)
                    .execute()
                )
                rows = getattr(res, "data", None) or []
                if rows:
                    row = rows[0]
                    record = SessionRecord(
                        session_id=row["id"],
                        token_hash=row["token_hash"],
                        label=row.get("label"),
                        created_at=row.get("created_at", ""),
                    )
                    self._sessions[session_id] = record
            except Exception:
                self.persistence_available = False

        if record is None or not raw_token:
            return None
        if not verify_token(raw_token, record.token_hash):
            return None
        return record

    def record_event(self, session_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        clean_payload = scrub_payload(payload)
        entry = {
            "session_id": session_id,
            "event_type": event_type,
            "payload": clean_payload,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if session_id in self._sessions:
            self._sessions[session_id].events.append(entry)

        if self.persistence_available and self._client is not None:
            try:
                self._client.table("session_events").insert(entry).execute()
            except Exception:
                self.persistence_available = False
        return entry

    def record_metrics(self, session_id: str, metrics: dict[str, Any]) -> dict[str, Any]:
        row = {
            "session_id": session_id,
            "baseline_tokens": int(metrics.get("baseline_tokens", 0)),
            "optimized_tokens": int(metrics.get("optimized_tokens", 0)),
            "saved_tokens": int(metrics.get("saved_tokens", 0)),
            "saved_pct": float(metrics.get("saved_pct", 0.0)),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if session_id in self._sessions:
            self._sessions[session_id].metrics.append(row)

        if self.persistence_available and self._client is not None:
            try:
                self._client.table("session_metrics").insert(row).execute()
            except Exception:
                self.persistence_available = False
        return row