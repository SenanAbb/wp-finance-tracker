
create extension if not exists pgcrypto;
create extension if not exists citext;
create extension if not exists vector;

drop table if exists public.knowledge_embeddings cascade;
drop table if exists public.sessions cascade;
drop table if exists public.auth_rate_limits cascade;
drop table if exists public.category_limits cascade;
drop table if exists public.investments cascade;
drop table if exists public.transactions cascade;
drop table if exists public.categories cascade;
drop table if exists public.accounts cascade;
drop table if exists public.auth_challenges cascade;
drop table if exists public.users cascade;

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  phone_number citext not null unique,
  display_name text,
  default_currency text not null default 'EUR',
  created_at timestamptz not null default now(),
  constraint users_phone_number_e164_check check (
    regexp_replace(phone_number::text, '[^0-9+]', '', 'g') ~ '^\\+[1-9]\\d{1,14}$'
  )
);

create table if not exists public.auth_challenges (
  id uuid primary key default gen_random_uuid(),
  phone_number citext not null,
  code_hash text not null,
  purpose text not null default 'login',
  expires_at timestamptz not null,
  consumed_at timestamptz,
  failed_attempts int not null default 0,
  last_attempt_at timestamptz,
  ip text,
  user_agent text,
  created_at timestamptz not null default now(),
  constraint auth_challenges_phone_number_e164_check check (
    regexp_replace(phone_number::text, '[^0-9+]', '', 'g') ~ '^\\+[1-9]\\d{1,14}$'
  )
);

create index if not exists auth_challenges_phone_number_idx on public.auth_challenges (phone_number);
create index if not exists auth_challenges_expires_at_idx on public.auth_challenges (expires_at);
create index if not exists auth_challenges_active_idx on public.auth_challenges (phone_number) where consumed_at is null;

create table if not exists public.auth_rate_limits (
  id uuid primary key default gen_random_uuid(),
  ip_address inet not null,
  phone_number citext,
  request_type text not null,
  attempted_at timestamptz not null default now(),
  success boolean default false
);

create index if not exists auth_rate_limits_ip_idx on public.auth_rate_limits (ip_address);
create index if not exists auth_rate_limits_phone_idx on public.auth_rate_limits (phone_number);
create index if not exists auth_rate_limits_ip_type_date_idx on public.auth_rate_limits (ip_address, request_type, attempted_at);

create table if not exists public.sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  session_token_hash text not null unique,
  created_at timestamptz not null default now(),
  last_seen_at timestamptz not null default now(),
  channel text not null default 'whatsapp',
  created_via text not null default 'whatsapp_login',
  origin text not null default 'web' check (origin in ('web', 'whatsapp')),
  expires_at timestamptz not null,
  revoked_at timestamptz,
  refresh_token_hash text,
  refresh_token_expires_at timestamptz,
  ip text,
  user_agent text
);

create index if not exists sessions_user_id_idx on public.sessions (user_id);
create index if not exists sessions_expires_at_idx on public.sessions (expires_at);
create unique index if not exists sessions_one_active_per_user_idx on public.sessions (user_id) where revoked_at is null;

create table if not exists public.accounts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  name text not null,
  type text not null,
  currency text not null default 'EUR',
  balance numeric(14,2) not null default 0,
  created_at timestamptz not null default now(),
  archived_at timestamptz,
  constraint accounts_type_check check (type in ('banco','inversion','cash'))
);

create index if not exists accounts_user_id_idx on public.accounts (user_id);

create table if not exists public.categories (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  type text not null,
  created_at timestamptz not null default now(),
  constraint categories_type_check check (type in ('expense','income','investment')),
  constraint categories_name_type_unique unique (name, type)
);


create table if not exists public.transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  account_id uuid references public.accounts(id) on delete set null,
  type text not null,
  amount numeric(14,2) not null,
  currency text not null default 'EUR',
  category_id uuid references public.categories(id) on delete set null,
  description text,
  reference text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  constraint transactions_type_check check (type in ('expense','income','investment','transfer','adjustment')),
  constraint transactions_amount_check check (amount >= 0)
);

create index if not exists transactions_user_created_at_idx on public.transactions (user_id, created_at desc);
create index if not exists transactions_user_type_created_at_idx on public.transactions (user_id, type, created_at desc);
create index if not exists transactions_category_id_idx on public.transactions (category_id);

create table if not exists public.category_limits (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  category_id uuid not null references public.categories(id) on delete cascade,
  monthly_limit numeric(14,2) not null,
  currency text not null default 'EUR',
  active boolean not null default true,
  created_at timestamptz not null default now(),
  constraint category_limits_monthly_limit_check check (monthly_limit >= 0),
  constraint category_limits_unique_active unique (user_id, category_id)
);

create index if not exists category_limits_user_id_idx on public.category_limits (user_id);

create table if not exists public.investments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  asset_name text not null,
  asset_type text not null,
  amount_invested numeric(14,2) not null,
  purchase_price numeric(14,6),
  quantity numeric(20,8),
  currency text not null default 'EUR',
  created_at timestamptz not null default now(),
  constraint investments_asset_type_check check (asset_type in ('crypto','stock','etf','real_estate','other')),
  constraint investments_amount_invested_check check (amount_invested >= 0)
);

create index if not exists investments_user_created_at_idx on public.investments (user_id, created_at desc);

-- Seed básico: categorías y datos de ejemplo
-- Se puede ejecutar con psql o desde el SQL editor de Supabase

-- Insertar categorías globales (sin user_id)
insert into public.categories (name, type)
values
  -- Categorías de gastos
  ('comida', 'expense'),
  ('transporte', 'expense'),
  ('hogar', 'expense'),
  ('ocio', 'expense'),
  ('salud', 'expense'),
  ('educación', 'expense'),
  ('trabajo', 'expense'),
  ('ropa', 'expense'),
  ('tecnología', 'expense'),
  ('otros', 'expense'),
  -- Categorías de ingresos
  ('salario', 'income'),
  ('freelance', 'income'),
  ('inversiones', 'income'),
  ('otros ingresos', 'income'),
  -- Categorías de inversión
  ('criptomonedas', 'investment'),
  ('acciones', 'investment'),
  ('fondos', 'investment')
on conflict do nothing;

alter table public.users
  drop constraint if exists users_phone_number_e164_check;

alter table public.users
  add constraint users_phone_number_e164_check
  check (regexp_replace(phone_number::text, '[^0-9+]', '', 'g') ~ '^\+[1-9]\d{1,14}$');

alter table public.auth_challenges
  drop constraint if exists auth_challenges_phone_number_e164_check;

alter table public.auth_challenges
  add constraint auth_challenges_phone_number_e164_check
  check (regexp_replace(phone_number::text, '[^0-9+]', '', 'g') ~ '^\+[1-9]\d{1,14}$');

-- ============================================================================
-- Knowledge Embeddings: Búsqueda vectorial para intents, categorías y FAQ
-- ============================================================================
-- Tipos:
--   'category'  → sinónimos/ejemplos de categorías de gastos/ingresos
--   'intent'    → frases de ejemplo para cada intención del usuario
--   'faq'       → preguntas frecuentes con respuestas predefinidas
-- ============================================================================

create table if not exists public.knowledge_embeddings (
  id uuid primary key default gen_random_uuid(),
  type text not null check (type in ('category', 'intent', 'faq', 'account')),
  content text not null,
  metadata jsonb not null default '{}',
  embedding vector(1536) not null,
  created_at timestamptz not null default now(),
  constraint knowledge_embeddings_content_type_unique unique (content, type)
);

-- Índice HNSW para búsqueda vectorial rápida (mejor que IVFFlat para < 100k filas)
create index if not exists knowledge_embeddings_hnsw_idx
  on public.knowledge_embeddings
  using hnsw (embedding vector_cosine_ops)
  with (m = 16, ef_construction = 64);

-- Índice para filtrar por tipo antes de la búsqueda vectorial
create index if not exists knowledge_embeddings_type_idx
  on public.knowledge_embeddings (type);

-- ============================================================================
-- Función: match_embeddings
-- ============================================================================
-- Busca los embeddings más similares a un vector de consulta.
-- Parámetros:
--   query_embedding   → vector del mensaje del usuario (1536 dims)
--   match_type        → filtro opcional: 'category', 'intent', 'faq' o NULL para todos
--   match_threshold   → similitud mínima (0.0 - 1.0), default 0.5
--   match_count       → número máximo de resultados, default 5
-- ============================================================================

create or replace function public.match_embeddings(
  query_embedding vector(1536),
  match_type text default null,
  match_threshold float default 0.5,
  match_count int default 5
)
returns table (
  id uuid,
  type text,
  content text,
  metadata jsonb,
  similarity float
)
language sql stable
as $$
  select
    ke.id,
    ke.type,
    ke.content,
    ke.metadata,
    1 - (ke.embedding <=> query_embedding) as similarity
  from public.knowledge_embeddings ke
  where
    (match_type is null or ke.type = match_type)
    and 1 - (ke.embedding <=> query_embedding) > match_threshold
  order by ke.embedding <=> query_embedding
  limit match_count;
$$;