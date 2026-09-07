-- ═══════════════════════════════════════════════════════════════
--  DataForge · Esquema do painel
--
--  Idempotente: rodar duas vezes não quebra nada.
--  Aplique com  python3 scripts/supabase_aplicar.py
--  ou cole no SQL Editor do Supabase, na ordem 01 → 02 → 03.
--
--  Princípio: a chave anon é pública. Quem protege os dados é a RLS
--  desta migração, não o segredo da chave. Toda tabela abaixo tem RLS
--  ligada, e a política padrão é negar.
-- ═══════════════════════════════════════════════════════════════

create extension if not exists "pgcrypto";

-- ═══════════════════════════════════════════════════════════════
--  1. Identidade
-- ═══════════════════════════════════════════════════════════════

-- Papel do usuário. Enum e não texto: um typo em 'admin' viraria um
-- usuário sem permissão nenhuma, silenciosamente.
do $$ begin
  create type public.papel_usuario as enum ('usuario', 'moderador', 'admin');
exception when duplicate_object then null;
end $$;

create table if not exists public.perfis (
  id             uuid primary key references auth.users(id) on delete cascade,
  nome           text,
  avatar_url     text,
  bio            text,
  papel          public.papel_usuario not null default 'usuario',
  xp             integer not null default 0,
  ofensiva       integer not null default 0,
  ultima_pratica date,
  preferencias   jsonb not null default '{}'::jsonb,
  criado_em      timestamptz not null default now(),
  atualizado_em  timestamptz not null default now()
);

comment on table public.perfis is
  'Dados de cada usuário. O e-mail fica em auth.users e não é copiado aqui.';
comment on column public.perfis.papel is
  'Quem pode o quê. Só o service_role pode promover alguém a admin.';
comment on column public.perfis.ofensiva is
  'Dias seguidos praticando. Zerado pela rotina diária quando há buraco.';

-- Saber se quem chama é admin, sem expor a tabela inteira.
--
-- SECURITY DEFINER porque a política de 'perfis' consulta 'perfis': sem
-- isso, a checagem dispararia a própria política e entraria em recursão
-- infinita — o Postgres aborta com 'infinite recursion detected'.
create or replace function public.e_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.perfis
    where id = auth.uid() and papel in ('admin', 'moderador')
  );
$$;

comment on function public.e_admin is
  'Quem chama é admin ou moderador? SECURITY DEFINER evita recursão de RLS.';

-- ═══════════════════════════════════════════════════════════════
--  2. Trabalho do usuário
-- ═══════════════════════════════════════════════════════════════

create table if not exists public.projetos (
  id            uuid primary key default gen_random_uuid(),
  dono_id       uuid not null references auth.users(id) on delete cascade,
  nome          text not null,
  descricao     text,
  publico       boolean not null default false,
  criado_em     timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists projetos_dono_idx on public.projetos (dono_id);

create table if not exists public.trechos (
  id            uuid primary key default gen_random_uuid(),
  dono_id       uuid not null references auth.users(id) on delete cascade,
  projeto_id    uuid references public.projetos(id) on delete set null,
  titulo        text not null,
  codigo        text not null default '',
  descricao     text,
  publico       boolean not null default false,
  etiquetas     text[] not null default '{}',
  criado_em     timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists trechos_dono_idx on public.trechos (dono_id);
create index if not exists trechos_projeto_idx on public.trechos (projeto_id);

create table if not exists public.anotacoes (
  id            uuid primary key default gen_random_uuid(),
  dono_id       uuid not null references auth.users(id) on delete cascade,
  rota          text not null,
  texto         text not null default '',
  criado_em     timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists anotacoes_dono_idx on public.anotacoes (dono_id);

-- Progresso nos exercícios da documentação (os 200 do repositório).
create table if not exists public.progresso (
  dono_id      uuid not null references auth.users(id) on delete cascade,
  exercicio    text not null,
  concluido    boolean not null default false,
  concluido_em timestamptz,
  primary key (dono_id, exercicio)
);

-- ═══════════════════════════════════════════════════════════════
--  3. Prática: problemas e submissões
-- ═══════════════════════════════════════════════════════════════

do $$ begin
  create type public.dificuldade as enum ('facil', 'medio', 'dificil');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type public.estado_submissao as enum (
    'aceito', 'errado', 'erro_execucao', 'erro_sintaxe', 'tempo_esgotado');
exception when duplicate_object then null;
end $$;

create table if not exists public.problemas (
  id           uuid primary key default gen_random_uuid(),
  slug         text not null unique,
  titulo       text not null,
  dificuldade  public.dificuldade not null default 'facil',
  categoria    text not null default 'geral',
  enunciado    text not null,
  assinatura   text not null,
  exemplos     jsonb not null default '[]'::jsonb,
  dicas        jsonb not null default '[]'::jsonb,
  casos        jsonb not null default '[]'::jsonb,
  solucao      text,
  conceitos    text[] not null default '{}',
  ordem        integer not null default 0,
  publicado    boolean not null default true,
  criado_em    timestamptz not null default now()
);

comment on table public.problemas is
  'Desafios de programação no estilo LeetCode, resolvidos em DataForge.';
comment on column public.problemas.casos is
  'Casos de teste: [{"entrada": [...], "saida": ...}]. Visíveis a quem '
  'está logado — esconder não protege nada, já que a correção roda no '
  'navegador, e ver os casos ajuda a entender o problema.';
comment on column public.problemas.solucao is
  'Solução de referência. O Postgres não faz RLS por coluna, então quem '
  'a esconde é a migração 03: a prática lê a view problemas_publicos '
  '(sem esta coluna) e a solução sai por solucao_de(uuid).';

create index if not exists problemas_categoria_idx
  on public.problemas (categoria, ordem);

create table if not exists public.submissoes (
  id             uuid primary key default gen_random_uuid(),
  dono_id        uuid not null references auth.users(id) on delete cascade,
  problema_id    uuid not null references public.problemas(id) on delete cascade,
  codigo         text not null,
  estado         public.estado_submissao not null,
  testes_ok      integer not null default 0,
  testes_total   integer not null default 0,
  duracao_ms     integer,
  detalhe        text,
  criado_em      timestamptz not null default now()
);

create index if not exists submissoes_dono_idx
  on public.submissoes (dono_id, criado_em desc);
create index if not exists submissoes_problema_idx
  on public.submissoes (problema_id);

-- Um resumo por (usuário, problema): evita varrer todas as submissões
-- para saber se alguém já resolveu algo — a pergunta mais frequente do
-- painel, feita em toda listagem.
create table if not exists public.resolucoes (
  dono_id        uuid not null references auth.users(id) on delete cascade,
  problema_id    uuid not null references public.problemas(id) on delete cascade,
  resolvido      boolean not null default false,
  tentativas     integer not null default 0,
  melhor_ms      integer,
  primeiro_em    timestamptz,
  resolvido_em   timestamptz,
  atualizado_em  timestamptz not null default now(),
  primary key (dono_id, problema_id)
);

-- ═══════════════════════════════════════════════════════════════
--  4. Auditoria e métricas
-- ═══════════════════════════════════════════════════════════════

create table if not exists public.eventos (
  id          bigserial primary key,
  dono_id     uuid references auth.users(id) on delete set null,
  tipo        text not null,
  dados       jsonb not null default '{}'::jsonb,
  criado_em   timestamptz not null default now()
);

create index if not exists eventos_tipo_idx on public.eventos (tipo, criado_em desc);
create index if not exists eventos_dono_idx on public.eventos (dono_id, criado_em desc);

comment on table public.eventos is
  'Trilha de auditoria. Qualquer um insere o seu; só admin lê.';

-- Uma linha por dia, preenchida pela rotina agendada. Contar na hora
-- funcionaria hoje e ficaria lento em um ano.
create table if not exists public.metricas_diarias (
  dia                date primary key,
  usuarios_novos     integer not null default 0,
  usuarios_ativos    integer not null default 0,
  submissoes         integer not null default 0,
  submissoes_aceitas integer not null default 0,
  problemas_resolvidos integer not null default 0,
  trechos_criados    integer not null default 0,
  calculado_em       timestamptz not null default now()
);

-- ═══════════════════════════════════════════════════════════════
--  5. RLS — a partir daqui, tudo é negado por padrão
-- ═══════════════════════════════════════════════════════════════

alter table public.perfis            enable row level security;
alter table public.projetos          enable row level security;
alter table public.trechos           enable row level security;
alter table public.anotacoes         enable row level security;
alter table public.progresso         enable row level security;
alter table public.problemas         enable row level security;
alter table public.submissoes        enable row level security;
alter table public.resolucoes        enable row level security;
alter table public.eventos           enable row level security;
alter table public.metricas_diarias  enable row level security;

-- ── Perfis ──
drop policy if exists "perfis: leitura pública" on public.perfis;
create policy "perfis: leitura pública"
  on public.perfis for select using (true);

drop policy if exists "perfis: dono cria o seu" on public.perfis;
create policy "perfis: dono cria o seu"
  on public.perfis for insert with check (auth.uid() = id);

-- O dono edita o seu, mas NÃO pode se promover: o papel precisa ser o
-- mesmo que já está gravado. Sem esta checagem, qualquer usuário vira
-- admin com um UPDATE.
drop policy if exists "perfis: dono edita, sem trocar de papel" on public.perfis;
create policy "perfis: dono edita, sem trocar de papel"
  on public.perfis for update
  using (auth.uid() = id)
  with check (
    auth.uid() = id
    and papel = (select p.papel from public.perfis p where p.id = auth.uid())
  );

drop policy if exists "perfis: admin edita qualquer um" on public.perfis;
create policy "perfis: admin edita qualquer um"
  on public.perfis for update using (public.e_admin()) with check (public.e_admin());

-- ── Projetos ──
drop policy if exists "projetos: dono, público ou admin" on public.projetos;
create policy "projetos: dono, público ou admin"
  on public.projetos for select
  using (publico or auth.uid() = dono_id or public.e_admin());

drop policy if exists "projetos: dono cria" on public.projetos;
create policy "projetos: dono cria"
  on public.projetos for insert with check (auth.uid() = dono_id);

drop policy if exists "projetos: dono edita" on public.projetos;
create policy "projetos: dono edita"
  on public.projetos for update
  using (auth.uid() = dono_id) with check (auth.uid() = dono_id);

drop policy if exists "projetos: dono ou admin apaga" on public.projetos;
create policy "projetos: dono ou admin apaga"
  on public.projetos for delete
  using (auth.uid() = dono_id or public.e_admin());

-- ── Trechos ──
drop policy if exists "trechos: dono, público ou admin" on public.trechos;
create policy "trechos: dono, público ou admin"
  on public.trechos for select
  using (
    publico
    or auth.uid() = dono_id
    or public.e_admin()
    or exists (
      select 1 from public.projetos p
      where p.id = trechos.projeto_id and p.publico
    )
  );

drop policy if exists "trechos: dono cria" on public.trechos;
create policy "trechos: dono cria"
  on public.trechos for insert with check (auth.uid() = dono_id);

drop policy if exists "trechos: dono edita" on public.trechos;
create policy "trechos: dono edita"
  on public.trechos for update
  using (auth.uid() = dono_id) with check (auth.uid() = dono_id);

drop policy if exists "trechos: dono ou admin apaga" on public.trechos;
create policy "trechos: dono ou admin apaga"
  on public.trechos for delete
  using (auth.uid() = dono_id or public.e_admin());

-- ── Anotações e progresso: privados, sem exceção ──
drop policy if exists "anotações: só o dono" on public.anotacoes;
create policy "anotações: só o dono"
  on public.anotacoes for all
  using (auth.uid() = dono_id) with check (auth.uid() = dono_id);

drop policy if exists "progresso: só o dono" on public.progresso;
create policy "progresso: só o dono"
  on public.progresso for all
  using (auth.uid() = dono_id) with check (auth.uid() = dono_id);

-- ── Problemas: todos leem os publicados; só admin escreve ──
drop policy if exists "problemas: publicados para todos" on public.problemas;
create policy "problemas: publicados para todos"
  on public.problemas for select using (publicado or public.e_admin());

drop policy if exists "problemas: admin escreve" on public.problemas;
create policy "problemas: admin escreve"
  on public.problemas for insert with check (public.e_admin());

drop policy if exists "problemas: admin edita" on public.problemas;
create policy "problemas: admin edita"
  on public.problemas for update using (public.e_admin()) with check (public.e_admin());

drop policy if exists "problemas: admin apaga" on public.problemas;
create policy "problemas: admin apaga"
  on public.problemas for delete using (public.e_admin());

-- ── Submissões: o dono lê e cria as suas; admin lê todas ──
drop policy if exists "submissões: dono ou admin lê" on public.submissoes;
create policy "submissões: dono ou admin lê"
  on public.submissoes for select
  using (auth.uid() = dono_id or public.e_admin());

drop policy if exists "submissões: dono cria" on public.submissoes;
create policy "submissões: dono cria"
  on public.submissoes for insert with check (auth.uid() = dono_id);

-- Submissão não se edita nem se apaga: é histórico. Sem política de
-- update/delete, ambos ficam negados.

-- ── Resoluções ──
drop policy if exists "resoluções: dono ou admin lê" on public.resolucoes;
create policy "resoluções: dono ou admin lê"
  on public.resolucoes for select
  using (auth.uid() = dono_id or public.e_admin());

drop policy if exists "resoluções: dono grava" on public.resolucoes;
create policy "resoluções: dono grava"
  on public.resolucoes for all
  using (auth.uid() = dono_id) with check (auth.uid() = dono_id);

-- ── Eventos: qualquer um registra o seu; só admin lê ──
drop policy if exists "eventos: só admin lê" on public.eventos;
create policy "eventos: só admin lê"
  on public.eventos for select using (public.e_admin());

drop policy if exists "eventos: usuário registra o seu" on public.eventos;
create policy "eventos: usuário registra o seu"
  on public.eventos for insert
  with check (dono_id is null or auth.uid() = dono_id);

-- ── Métricas: painel do admin ──
drop policy if exists "métricas: só admin" on public.metricas_diarias;
create policy "métricas: só admin"
  on public.metricas_diarias for select using (public.e_admin());

-- ═══════════════════════════════════════════════════════════════
--  6. Gatilhos
-- ═══════════════════════════════════════════════════════════════

-- Todo usuário novo ganha um perfil. Sem isto, o painel abriria vazio
-- para quem acabou de se registrar.
create or replace function public.ao_criar_usuario()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.perfis (id, nome, avatar_url)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'nome',
             new.raw_user_meta_data->>'full_name',
             split_part(new.email, '@', 1)),
    new.raw_user_meta_data->>'avatar_url'
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists ao_criar_usuario on auth.users;
create trigger ao_criar_usuario
  after insert on auth.users
  for each row execute function public.ao_criar_usuario();

-- atualizado_em em todas as tabelas que o têm.
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
  foreach t in array array['perfis','projetos','trechos','anotacoes','resolucoes']
  loop
    execute format(
      'drop trigger if exists marcar_%1$s on public.%1$s;
       create trigger marcar_%1$s before update on public.%1$s
       for each row execute function public.marcar_atualizacao();', t);
  end loop;
end $$;

-- Uma submissão aceita atualiza o resumo, o XP e a ofensiva de uma vez.
-- Fazer isso no cliente exigiria três chamadas e deixaria o estado
-- inconsistente se o navegador fechasse no meio.
create or replace function public.ao_submeter()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  ja_resolvido boolean;
  pontos integer;
  ultima date;
begin
  select resolvido into ja_resolvido
  from public.resolucoes
  where dono_id = new.dono_id and problema_id = new.problema_id;

  insert into public.resolucoes as r
    (dono_id, problema_id, resolvido, tentativas, melhor_ms,
     primeiro_em, resolvido_em)
  values (
    new.dono_id, new.problema_id, new.estado = 'aceito', 1,
    case when new.estado = 'aceito' then new.duracao_ms end,
    new.criado_em,
    case when new.estado = 'aceito' then new.criado_em end
  )
  on conflict (dono_id, problema_id) do update set
    resolvido    = r.resolvido or excluded.resolvido,
    tentativas   = r.tentativas + 1,
    melhor_ms    = least(coalesce(r.melhor_ms, excluded.melhor_ms),
                         coalesce(excluded.melhor_ms, r.melhor_ms)),
    resolvido_em = coalesce(r.resolvido_em, excluded.resolvido_em);

  -- XP só na primeira vez que resolve: repetir o mesmo problema não
  -- deve render pontos, senão o placar vira quem clica mais.
  if new.estado = 'aceito' and coalesce(ja_resolvido, false) = false then
    select case dificuldade
             when 'facil' then 10 when 'medio' then 25 else 50 end
      into pontos
      from public.problemas where id = new.problema_id;

    select ultima_pratica into ultima from public.perfis where id = new.dono_id;

    update public.perfis set
      xp = xp + coalesce(pontos, 10),
      ofensiva = case
        when ultima = current_date then ofensiva
        when ultima = current_date - 1 then ofensiva + 1
        else 1
      end,
      ultima_pratica = current_date
    where id = new.dono_id;
  end if;

  return new;
end;
$$;

drop trigger if exists ao_submeter on public.submissoes;
create trigger ao_submeter
  after insert on public.submissoes
  for each row execute function public.ao_submeter();

-- ═══════════════════════════════════════════════════════════════
--  7. Visões
-- ═══════════════════════════════════════════════════════════════

-- O placar não expõe e-mail nem papel: só o que uma tabela de líderes
-- precisa mostrar.
create or replace view public.placar
with (security_invoker = on) as
  select
    p.id,
    p.nome,
    p.avatar_url,
    p.xp,
    p.ofensiva,
    (select count(*) from public.resolucoes r
      where r.dono_id = p.id and r.resolvido) as resolvidos,
    rank() over (order by p.xp desc, p.id) as posicao
  from public.perfis p
  where p.xp > 0;

comment on view public.placar is
  'Tabela de líderes. security_invoker: respeita a RLS de quem consulta.';
