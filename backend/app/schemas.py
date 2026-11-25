from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

RoleType = Literal["system", "developer", "user", "assistant", "tool"]
DecisionAction = Literal["KEEP", "COMPRESS", "DROP"]


class ContextItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=128)
    role: RoleType
    content: str = Field(..., min_length=1, max_length=12000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=12000)
    items: list[ContextItem] = Field(default_factory=list, max_length=80)
    provider: Literal["ollama", "gemini"] | None = None
    model: str | None = Field(default=None, max_length=128)
    api_key: str | None = Field(default=None, max_length=512, exclude=True)
    comparison_enabled: bool | None = None


class PruningDecision(BaseModel):
    item_id: str
    role: RoleType
    action: DecisionAction
    reason: str
    tokens_before: int = Field(ge=0)
    tokens_after: int = Field(ge=0)


class TokenMetrics(BaseModel):
    baseline_tokens: int = Field(ge=0)
    optimized_tokens: int = Field(ge=0)
    saved_tokens: int
    saved_pct: float


class ChatResponse(BaseModel):
    session_id: str
    answer: str | None = None
    provider: str
    model: str
    provider_status: str
    metrics: TokenMetrics
    decisions: list[PruningDecision] = Field(default_factory=list)


class SessionCreateResponse(BaseModel):
    session_id: str
    session_token: str
    label: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    env: str
    main_provider: str
    main_model: str
    persistence: Literal["available", "unavailable"]