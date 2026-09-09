-- ═══════════════════════════════════════════════════════════════
--  Downloads da linguagem
-- ═══════════════════════════════════════════════════════════════
--
--  Quantas pessoas baixaram, de onde, por qual caminho e em qual
--  sistema. O painel do admin lê daqui.
--
--  Duas decisões que valem registrar:
--
--  1. NÃO guardamos o IP. Ele identifica pessoa, e para contar
--     downloads não é preciso saber QUEM baixou — basta saber que
--     foram N. O que se guarda é um HASH do IP com um sal que gira
--     todo dia: dá para contar "únicos do dia" sem poder voltar ao
--     endereço, e no dia seguinte nem isso.
--
--  2. A contagem por dia é MATERIALIZADA por rotina agendada. Contar
--     na hora funciona hoje, com mil linhas, e fica lento com um
--     milhão — e o painel é a última coisa que deveria ficar lenta.
--
--  Idempotente: pode rodar quantas vezes quiser.

-- ── A tabela bruta ─────────────────────────────────────────────

create table if not exists public.downloads (
  id           bigserial primary key,

  -- Por onde veio: 'script' (curl | sh), 'powershell', 'pip',
  -- 'tarball' (baixou o .tar.gz direto), 'docker', 'vsix'.
  origem       text not null,

  -- Qual versão. Guardar isto é o que permite ver a adoção de uma
  -- versão nova sem perguntar a ninguém.
  versao       text not null default '1.0.0',

  -- Sistema e arquitetura, quando o instalador os informa.
  sistema      text,
  arquitetura  text,

  -- País pelo cabeçalho do CDN. É granularidade suficiente para saber
  -- onde a linguagem pega, e grosseira demais para identificar alguém.
  pais         text,

  -- O hash do IP com o sal do dia. Serve só para 'únicos do dia'.
  visitante    text,

  -- De onde a pessoa veio, quando o navegador conta.
  referencia   text,

  criado_em    timestamptz not null default now(),

  -- O dia em UTC, como coluna GERADA.
  --
  -- 'date(criado_em)' num índice é recusado pelo Postgres, e com
  -- razão: converter timestamptz para date depende do fuso da SESSÃO,
  -- e um índice cujo conteúdo muda com quem consulta não é índice. A
  -- coluna fixa o fuso em UTC e passa a ser imutável.
  dia          date generated always as
                 ((criado_em at time zone 'UTC')::date) stored
);

create index if not exists downloads_dia_idx
  on public.downloads (dia, origem);
create index if not exists downloads_criado_idx
  on public.downloads (criado_em desc);
create index if not exists downloads_versao_idx
  on public.downloads (versao, criado_em desc);
create index if not exists downloads_visitante_idx
  on public.downloads (visitante, criado_em desc)
  where visitante is not null;

comment on table public.downloads is
  'Um registro por download. Sem IP: só um hash com sal que gira por dia.';

-- ── O resumo por dia ───────────────────────────────────────────

create table if not exists public.downloads_por_dia (
  dia          date not null,
  origem       text not null,
  versao       text not null default '1.0.0',
  total        integer not null default 0,
  unicos       integer not null default 0,
  calculado_em timestamptz not null default now(),
  primary key (dia, origem, versao)
);

comment on table public.downloads_por_dia is
  'Materializado pela rotina agendada. Contar na hora fica lento em um ano.';

-- ── Registrar um download ──────────────────────────────────────
--
-- SECURITY DEFINER porque quem chama é anônimo: o instalador não
-- tem sessão. A função é o ÚNICO caminho de escrita, e ela valida o
-- que entra — sem isso, uma tabela aberta a anônimo vira lixeira.

create or replace function public.registrar_download(
  p_origem      text,
  p_versao      text default '1.0.0',
  p_sistema     text default null,
  p_arquitetura text default null,
  p_pais        text default null,
  p_visitante   text default null,
  p_referencia  text default null
)
returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
  v_id bigint;
begin
  -- A lista de origens é fechada. Aberta, ela viraria texto livre
  -- vindo de fora, e o painel somaria categorias inventadas.
  if p_origem is null or p_origem not in
     ('script', 'powershell', 'pip', 'tarball', 'docker', 'vsix', 'site') then
    raise exception 'origem inválida: %', coalesce(p_origem, 'nula')
      using hint = 'use script, powershell, pip, tarball, docker, vsix ou site';
  end if;

  insert into public.downloads
    (origem, versao, sistema, arquitetura, pais, visitante, referencia)
  values
    (p_origem,
     coalesce(nullif(left(p_versao, 20), ''), '1.0.0'),
     nullif(left(p_sistema, 40), ''),
     nullif(left(p_arquitetura, 20), ''),
     nullif(left(p_pais, 4), ''),
     nullif(left(p_visitante, 64), ''),
     nullif(left(p_referencia, 200), ''))
  returning id into v_id;

  return v_id;
end;
$$;

comment on function public.registrar_download is
  'O único caminho de escrita. Valida a origem: aberta, ela viraria lixeira.';

grant execute on function public.registrar_download(
  text, text, text, text, text, text, text) to anon, authenticated;

-- ── O total público ────────────────────────────────────────────
--
-- Um número só, para o site mostrar. Não expõe nada por linha, então
-- pode ser público — e é o tipo de número que dá vontade de mostrar.

create or replace function public.total_de_downloads()
returns bigint
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(sum(total), 0)::bigint from public.downloads_por_dia;
$$;

grant execute on function public.total_de_downloads() to anon, authenticated;

-- ── O painel do admin ──────────────────────────────────────────

create or replace function public.painel_de_downloads(p_dias integer default 30)
returns jsonb
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  v_desde date := current_date - greatest(coalesce(p_dias, 30), 1);
  v_resultado jsonb;
begin
  if not public.e_admin() then
    raise exception 'só admin' using errcode = '42501';
  end if;

  select jsonb_build_object(
    'total', (select coalesce(sum(total), 0) from public.downloads_por_dia),
    'total_periodo', (
      select coalesce(sum(total), 0) from public.downloads_por_dia
      where dia >= v_desde),
    'unicos_periodo', (
      select count(distinct visitante) from public.downloads
      where criado_em >= v_desde and visitante is not null),
    'hoje', (
      select coalesce(sum(total), 0) from public.downloads_por_dia
      where dia = current_date),

    -- A série por dia, para o gráfico. Com os dias vazios preenchidos:
    -- um gráfico que pula o dia sem download mente sobre a tendência.
    'por_dia', (
      select coalesce(jsonb_agg(linha order by linha->>'dia'), '[]'::jsonb)
      from (
        select jsonb_build_object(
                 'dia', d::date,
                 'total', coalesce((
                   select sum(total) from public.downloads_por_dia p
                   where p.dia = d::date), 0)
               ) as linha
        from generate_series(v_desde, current_date, '1 day') as d
      ) s),

    'por_origem', (
      select coalesce(jsonb_object_agg(origem, soma), '{}'::jsonb)
      from (select origem, sum(total) as soma
            from public.downloads_por_dia
            where dia >= v_desde group by origem) s),

    'por_sistema', (
      select coalesce(jsonb_object_agg(coalesce(sistema, 'desconhecido'), n),
                      '{}'::jsonb)
      from (select sistema, count(*) as n from public.downloads
            where criado_em >= v_desde group by sistema) s),

    'por_versao', (
      select coalesce(jsonb_object_agg(versao, soma), '{}'::jsonb)
      from (select versao, sum(total) as soma
            from public.downloads_por_dia
            where dia >= v_desde group by versao) s),

    'por_pais', (
      select coalesce(jsonb_agg(jsonb_build_object('pais', pais, 'total', n)
                                order by n desc), '[]'::jsonb)
      from (select coalesce(pais, '—') as pais, count(*) as n
            from public.downloads
            where criado_em >= v_desde
            group by pais order by n desc limit 12) s),

    'ultimos', (
      select coalesce(jsonb_agg(jsonb_build_object(
               'origem', origem, 'sistema', sistema,
               'versao', versao, 'pais', pais, 'quando', criado_em)
             order by criado_em desc), '[]'::jsonb)
      from (select * from public.downloads
            order by criado_em desc limit 20) s)
  ) into v_resultado;

  return v_resultado;
end;
$$;

comment on function public.painel_de_downloads is
  'Tudo o que o painel do admin mostra, numa chamada só.';

grant execute on function public.painel_de_downloads(integer) to authenticated;

-- ── A rotina que materializa ───────────────────────────────────

create or replace function public.consolidar_downloads(p_dia date default null)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  v_dia date := coalesce(p_dia, current_date);
  v_linhas integer;
begin
  insert into public.downloads_por_dia (dia, origem, versao, total, unicos,
                                        calculado_em)
  select dia, origem, versao,
         count(*), count(distinct visitante), now()
  from public.downloads
  where dia = v_dia
  group by dia, origem, versao
  on conflict (dia, origem, versao) do update
    set total = excluded.total,
        unicos = excluded.unicos,
        calculado_em = now();

  get diagnostics v_linhas = row_count;
  return v_linhas;
end;
$$;

comment on function public.consolidar_downloads is
  'Recalcula o resumo de um dia. Idempotente: rodar de novo corrige.';

-- ── RLS ────────────────────────────────────────────────────────

alter table public.downloads         enable row level security;
alter table public.downloads_por_dia enable row level security;

-- Ninguém lê a tabela bruta a não ser admin. Escrever só pela função,
-- que é SECURITY DEFINER e passa por cima do RLS.
drop policy if exists "downloads: só admin lê" on public.downloads;
create policy "downloads: só admin lê"
  on public.downloads for select using (public.e_admin());

drop policy if exists "downloads_por_dia: só admin lê" on public.downloads_por_dia;
create policy "downloads_por_dia: só admin lê"
  on public.downloads_por_dia for select using (public.e_admin());

-- ── O agendamento ──────────────────────────────────────────────

do $$
begin
  if exists (select 1 from pg_extension where extname = 'pg_cron') then
    perform cron.unschedule('consolidar-downloads')
      where exists (select 1 from cron.job
                    where jobname = 'consolidar-downloads');

    -- De hora em hora: o painel não precisa ser ao vivo, e recalcular
    -- o dia inteiro a cada download seria desperdício.
    perform cron.schedule(
      'consolidar-downloads', '7 * * * *',
      $cron$
        select public.consolidar_downloads(current_date);
        select public.consolidar_downloads(current_date - 1);
      $cron$);
  end if;
end
$$;
