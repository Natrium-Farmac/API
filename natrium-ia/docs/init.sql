-- Extensões necessárias
create extension if not exists pgcrypto;
create extension if not exists vector;

-- ============== CLIENTES ==============
create table if not exists clientes (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  telefone text unique not null,
  email text,
  endereco text,
  criado_em timestamp default now()
);

-- ============== PEDIDOS ==============
create table if not exists pedidos (
  id uuid primary key default gen_random_uuid(),
  cliente_id uuid references clientes(id) on delete cascade,
  receita_url text,
  valor numeric(10,2),
  status text check (status in ('NEW','QUOTED','PAYMENT_PENDING','PAID','FULFILLED','CANCELLED')) default 'NEW',
  criado_em timestamp default now(),
  atualizado_em timestamp default now()
);
create index if not exists idx_pedidos_cliente on pedidos(cliente_id);

-- ============== MENSAGENS ==============
create table if not exists mensagens (
  id bigserial primary key,
  cliente_id uuid references clientes(id) on delete set null,
  pedido_id uuid references pedidos(id) on delete set null,
  agente text check (agente in ('customer','reception','closure','system')) not null,
  conteudo text not null,
  criado_em timestamp default now()
);
create index if not exists idx_mensagens_pedido on mensagens(pedido_id);
create index if not exists idx_mensagens_cliente on mensagens(cliente_id);

-- ============== ANEXOS ==============
create table if not exists anexos (
  id bigserial primary key,
  cliente_id uuid references clientes(id) on delete set null,
  pedido_id uuid references pedidos(id) on delete cascade,
  tipo text check (tipo in ('RECEITA','COMPROVANTE','OUTRO')) default 'OUTRO',
  url text not null,
  mime text,
  criado_em timestamp default now()
);
create index if not exists idx_anexos_pedido on anexos(pedido_id);

-- ============== COMPROVANTES ==============
create table if not exists comprovantes (
  id bigserial primary key,
  pedido_id uuid references pedidos(id) on delete cascade,
  url text not null,
  valor numeric(10,2),
  status text check (status in ('PENDING','APPROVED','REJECTED')) default 'PENDING',
  reconhecido_em timestamp,
  criado_em timestamp default now()
);
create index if not exists idx_comprovantes_pedido on comprovantes(pedido_id);

-- ============== KB_CHUNKS (RAG) ==============
create table if not exists kb_chunks (
  id bigserial primary key,
  titulo text,
  conteudo text not null,
  embedding vector(1536),
  criado_em timestamp default now()
);
-- Index vetorial (necessita ANALYZE após popular)
do $$ begin
  create index idx_kb_embedding on kb_chunks using ivfflat (embedding vector_cosine_ops);
exception when others then null;
end $$;

-- ============== RPC: match_documents ==============
-- Envia um vetor de consulta e retorna os top-N mais similares
create or replace function match_documents(query_embedding vector(1536), match_count int default 5)
returns table(id bigint, titulo text, conteudo text, similarity float)
language plpgsql
as $$
begin
  return query
  select k.id, k.titulo, k.conteudo, 1 - (k.embedding <=> query_embedding) as similarity
  from kb_chunks k
  where k.embedding is not null
  order by k.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Trigger de updated_at em pedidos
create or replace function update_updated_at_column()
returns trigger as $$
begin
   new.atualizado_em = now();
   return new;
end;
$$ language 'plpgsql';

drop trigger if exists set_timestamp on pedidos;
create trigger set_timestamp
before update on pedidos
for each row
execute procedure update_updated_at_column();