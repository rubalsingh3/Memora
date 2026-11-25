export type RoleType = "system" | "developer" | "user" | "assistant" | "tool";
export type DecisionAction = "KEEP" | "COMPRESS" | "DROP";

export interface ContextItem {
  id: string;
  role: RoleType;
  content: string;
}

export interface ChatRequestPayload {
  session_id: string;
  message: string;
  items?: ContextItem[];
  provider?: "ollama" | "gemini" | null;
  model?: string | null;
  api_key?: string | null;
  comparison_enabled?: boolean | null;
}

export interface PruningDecision {
  item_id: string;
  role: RoleType;
  action: DecisionAction;
  reason: string;
  tokens_before: number;
  tokens_after: number;
}

export interface TokenMetrics {
  baseline_tokens: number;
  optimized_tokens: number;
  saved_tokens: number;
  saved_pct: number;
}

export interface ChatResponsePayload {
  session_id: string;
  answer: string | null;
  provider: string;
  model: string;
  provider_status: string;
  metrics: TokenMetrics;
  decisions: PruningDecision[];
}

export interface SessionCreateResponse {
  session_id: string;
  session_token: string;
  label?: string | null;
}

export interface HealthResponse {
  status: "ok" | "degraded";
  env: string;
  main_provider: string;
  main_model: string;
  persistence: "available" | "unavailable";
}