-- ═══════════════════════════════════════════════════════════
--  Esquema do painel DataForge
--
--  Aplique no SQL Editor do Supabase, de uma vez. É idempotente:
--  rodar duas vezes não quebra nada.
--
--  Depois, em Authentication → Providers, deixe "Email" ligado.
-- ═══════════════════════════════════════════════════════════

-- ── Perfis ─────────────────────────────────────────────────
-- auth.users é gerenciado pelo Supabase e não deve ser alterado.
-- O perfil vive aqui, ligado por id.

create table if not exists public.perfis (
  id           uuid primary key references auth.users(id) on delete cascade,
  nome         text,
  avatar_url   text,
  bio          text,
  criado_em    timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

comment on table public.perfis is
  'Dados públicos de cada usuário. O e-mail fica em auth.users.';

-- ── Projetos ───────────────────────────────────────────────

create table if not exists public.projetos (
  id           uuid primary key default gen_random_uuid(),
  dono_id      uuid not null references auth.users(id) on delete cascade,
  nome         text not null check (length(trim(nome)) > 0),
  descricao    text,
  publico      boolean not null default false,
  criado_em    timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists projetos_dono_idx on public.projetos(dono_id);
create index if not exists projetos_publico_idx
  on public.projetos(publico) where publico;

-- ── Trechos de código ──────────────────────────────────────

create table if not exists public.trechos (
  id           uuid primary key default gen_random_uuid(),
  projeto_id   uuid not null references public.projetos(id) on delete cascade,
  dono_id      uuid not null references auth.users(id) on delete cascade,
  titulo       text not null,
  codigo       text not null default '',
  linguagem    text not null default 'dataforge',
  criado_em    timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists trechos_projeto_idx on public.trechos(projeto_id);

-- ── Progresso nos exercícios ───────────────────────────────

create table if not exists public.progresso (
  id           uuid primary key default gen_random_uuid(),
  usuario_id   uuid not null references auth.users(id) on delete cascade,
  exercicio    text not null,          -- '001_ola_mundo'
  modulo       text not null,          -- '01-fundamentos'
  concluido    boolean not null default false,
  tentativas   integer not null default 0,
  concluido_em timestamptz,
  -- Um usuário tem no máximo uma linha por exercício. Sem isso, marcar
  -- concluído duas vezes criaria duas linhas e a contagem mentiria.
  unique (usuario_id, exercicio)
);

create index if not exists progresso_usuario_idx on public.progresso(usuario_id);

-- ── Anotações ──────────────────────────────────────────────

create table if not exists public.anotacoes (
  id           uuid primary key default gen_random_uuid(),
  usuario_id   uuid not null references auth.users(id) on delete cascade,
  rota         text not null,          -- '/docs/pipelines'
  titulo       text,
  conteudo     text not null default '',
  criado_em    timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists anotacoes_usuario_idx on public.anotacoes(usuario_id);
create index if not exists anotacoes_rota_idx on public.anotacoes(usuario_id, rota);

-- ═══════════════════════════════════════════════════════════
--  Row Level Security
--
--  A chave anon é pública: vai no bundle e qualquer um a lê. É a RLS
--  que protege os dados. Sem ela, essa chave daria acesso a tudo.
--
--  Toda tabela abaixo é negada por padrão, e cada política abre
--  exatamente um caso.
-- ═══════════════════════════════════════════════════════════

alter table public.perfis     enable row level security;
alter table public.projetos   enable row level security;
alter table public.trechos    enable row level security;
alter table public.progresso  enable row level security;
alter table public.anotacoes  enable row level security;

-- ── Perfis: leitura pública, escrita só do dono ────────────

drop policy if exists "perfis: qualquer um lê" on public.perfis;
create policy "perfis: qualquer um lê"
  on public.perfis for select using (true);

drop policy if exists "perfis: dono edita" on public.perfis;
create policy "perfis: dono edita"
  on public.perfis for update using (auth.uid() = id);

drop policy if exists "perfis: dono cria o seu" on public.perfis;
create policy "perfis: dono cria o seu"
  on public.perfis for insert with check (auth.uid() = id);

-- ── Projetos: o dono vê tudo; os outros só os públicos ─────

drop policy if exists "projetos: dono ou público" on public.projetos;
create policy "projetos: dono ou público"
  on public.projetos for select
  using (auth.uid() = dono_id or publico);

drop policy if exists "projetos: dono cria" on public.projetos;
create policy "projetos: dono cria"
  on public.projetos for insert with check (auth.uid() = dono_id);

drop policy if exists "projetos: dono edita" on public.projetos;
create policy "projetos: dono edita"
  on public.projetos for update using (auth.uid() = dono_id);

drop policy if exists "projetos: dono apaga" on public.projetos;
create policy "projetos: dono apaga"
  on public.projetos for delete using (auth.uid() = dono_id);

-- ── Trechos: seguem a visibilidade do projeto ──────────────

drop policy if exists "trechos: dono ou projeto público" on public.trechos;
create policy "trechos: dono ou projeto público"
  on public.trechos for select
  using (
    auth.uid() = dono_id
    or exists (
      select 1 from public.projetos p
      where p.id = projeto_id and p.publico
    )
  );

drop policy if exists "trechos: dono cria" on public.trechos;
create policy "trechos: dono cria"
  on public.trechos for insert with check (auth.uid() = dono_id);

drop policy if exists "trechos: dono edita" on public.trechos;
create policy "trechos: dono edita"
  on public.trechos for update using (auth.uid() = dono_id);

drop policy if exists "trechos: dono apaga" on public.trechos;
create policy "trechos: dono apaga"
  on public.trechos for delete using (auth.uid() = dono_id);

-- ── Progresso e anotações: privados ────────────────────────

drop policy if exists "progresso: só o dono" on public.progresso;
create policy "progresso: só o dono"
  on public.progresso for all
  using (auth.uid() = usuario_id)
  with check (auth.uid() = usuario_id);

drop policy if exists "anotações: só o dono" on public.anotacoes;
create policy "anotações: só o dono"
  on public.anotacoes for all
  using (auth.uid() = usuario_id)
  with check (auth.uid() = usuario_id);

-- ═══════════════════════════════════════════════════════════
--  Gatilhos
-- ═══════════════════════════════════════════════════════════

-- Perfil criado junto com o usuário. Sem isso, todo lugar que lê o
-- perfil precisaria tratar a ausência dele.
create or replace function public.criar_perfil()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.perfis (id, nome)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'nome', split_part(new.email, '@', 1))
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists ao_criar_usuario on auth.users;
create trigger ao_criar_usuario
  after insert on auth.users
  for each row execute function public.criar_perfil();

-- atualizado_em automático
create or replace function public.marcar_atualizacao()
returns trigger language plpgsql as $$
begin
  new.atualizado_em = now();
  return new;
end;
$$;

do $$
declare t text;
begin
  foreach t in array array['perfis', 'projetos', 'trechos', 'anotacoes'] loop
    execute format(
      'drop trigger if exists marcar_%1$s on public.%1$s;
       create trigger marcar_%1$s before update on public.%1$s
       for each row execute function public.marcar_atualizacao();', t);
  end loop;
end $$;

-- ═══════════════════════════════════════════════════════════
--  Visão de resumo, para o painel não fazer 4 consultas
-- ═══════════════════════════════════════════════════════════

create or replace view public.meu_resumo
with (security_invoker = true) as
select
  u.id as usuario_id,
  (select count(*) from public.projetos p where p.dono_id = u.id)   as projetos,
  (select count(*) from public.trechos  t where t.dono_id = u.id)   as trechos,
  (select count(*) from public.anotacoes a where a.usuario_id = u.id) as anotacoes,
  (select count(*) from public.progresso g
     where g.usuario_id = u.id and g.concluido)                     as exercicios_feitos
from auth.users u;

comment on view public.meu_resumo is
  'security_invoker: a view roda com as permissões de quem consulta, '
  'então a RLS de cada tabela continua valendo.';
