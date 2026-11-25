-- Phase 2 Initial Schema for Memora (apply in Supabase SQL Editor or via migration)

create table if not exists public.sessions (
  id text primary key,
  label text,
  token_hash text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.session_events (
  id uuid primary key default gen_random_uuid(),
  session_id text not null references public.sessions(id) on delete cascade,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.session_metrics (
  id uuid primary key default gen_random_uuid(),
  session_id text not null references public.sessions(id) on delete cascade,
  baseline_tokens integer not null default 0,
  optimized_tokens integer not null default 0,
  saved_tokens integer not null default 0,
  saved_pct double precision not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.session_progress_memory (
  session_id text primary key references public.sessions(id) on delete cascade,
  state_json jsonb not null default '{}'::jsonb,
  version integer not null default 1,
  updated_at timestamptz not null default now()
);

create index if not exists idx_session_events_session_id
  on public.session_events(session_id, created_at desc);

create index if not exists idx_session_metrics_session_id
  on public.session_metrics(session_id, created_at desc);

-- Enable Row-Level Security (service-role / backend manages access)
alter table public.sessions enable row level security;
alter table public.session_events enable row level security;
alter table public.session_metrics enable row level security;
alter table public.session_progress_memory enable row level security;