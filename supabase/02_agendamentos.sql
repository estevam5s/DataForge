-- ═══════════════════════════════════════════════════════════════
--  DataForge · Tarefas agendadas
--
--  Uma tabela descreve o que rodar e quando; o pg_cron dispara.
--  Separar as duas coisas permite ligar, desligar e reagendar pelo
--  painel do admin, sem migração e sem deploy.
-- ═══════════════════════════════════════════════════════════════

create extension if not exists pg_cron with schema extensions;
create extension if not exists pg_net  with schema extensions;

-- ═══════════════════════════════════════════════════════════════
--  1. O catálogo de tarefas
-- ═══════════════════════════════════════════════════════════════

do $$ begin
  create type public.cadencia as enum (
    'a_cada_30_min', 'por_hora', 'a_cada_6_horas',
    'diario', 'fim_do_dia', 'semanal', 'mensal', 'personalizado');
exception when duplicate_object then null;
end $$;

create table if not exists public.agendamentos (
  id             uuid primary key default gen_random_uuid(),
  nome           text not null unique,
  descricao      text,
  cadencia       public.cadencia not null,
  expressao_cron text not null,
  funcao         text not null,
  config         jsonb not null default '{}'::jsonb,
  ativo          boolean not null default true,
  ultima_execucao timestamptz,
  ultimo_estado  text,
  criado_em      timestamptz not null default now(),
  atualizado_em  timestamptz not null default now()
);

comment on table public.agendamentos is
  'O que roda sozinho e com que frequência. O pg_cron lê daqui.';
comment on column public.agendamentos.expressao_cron is
  'Cron de cinco campos, em UTC. O Supabase roda em UTC, e converter '
  'para o fuso do usuário aqui só criaria confusão no horário de verão.';
comment on column public.agendamentos.funcao is
  'Nome da função SQL a executar. Só funções de public. são aceitas — '
  'veja public.rodar_agendamento, que valida antes de executar.';

create table if not exists public.execucoes_agendamento (
  id             bigserial primary key,
  agendamento_id uuid not null references public.agendamentos(id) on delete cascade,
  comecou_em     timestamptz not null default now(),
  terminou_em    timestamptz,
  sucesso        boolean,
  detalhe        text,
  linhas_afetadas integer
);

create index if not exists execucoes_agendamento_idx
  on public.execucoes_agendamento (agendamento_id, comecou_em desc);

-- Fila de envios: e-mails, webhooks, relatórios. A tarefa agendada
-- enfileira; um worker (ou o próprio pg_net) entrega. Enfileirar em vez
-- de enviar direto é o que torna a rotina reexecutável sem duplicar
-- mensagem se ela falhar no meio.
create table if not exists public.envios (
  id           bigserial primary key,
  destino_id   uuid references auth.users(id) on delete cascade,
  canal        text not null default 'email',
  assunto      text not null,
  corpo        text not null,
  dados        jsonb not null default '{}'::jsonb,
  estado       text not null default 'pendente',
  tentativas   integer not null default 0,
  agendado_para timestamptz not null default now(),
  enviado_em   timestamptz,
  erro         text,
  criado_em    timestamptz not null default now()
);

create index if not exists envios_pendentes_idx
  on public.envios (estado, agendado_para) where estado = 'pendente';

alter table public.agendamentos          enable row level security;
alter table public.execucoes_agendamento enable row level security;
alter table public.envios                enable row level security;

drop policy if exists "agendamentos: só admin" on public.agendamentos;
create policy "agendamentos: só admin"
  on public.agendamentos for all
  using (public.e_admin()) with check (public.e_admin());

drop policy if exists "execuções: só admin" on public.execucoes_agendamento;
create policy "execuções: só admin"
  on public.execucoes_agendamento for select using (public.e_admin());

-- O usuário vê o que foi enviado para ele; o admin vê tudo.
drop policy if exists "envios: destinatário ou admin" on public.envios;
create policy "envios: destinatário ou admin"
  on public.envios for select
  using (auth.uid() = destino_id or public.e_admin());

drop policy if exists "envios: admin gerencia" on public.envios;
create policy "envios: admin gerencia"
  on public.envios for all
  using (public.e_admin()) with check (public.e_admin());

-- ═══════════════════════════════════════════════════════════════
--  2. As tarefas
-- ═══════════════════════════════════════════════════════════════

-- Consolida o dia anterior numa linha. Contar na hora funcionaria hoje
-- e ficaria lento em um ano.
create or replace function public.tarefa_metricas_diarias()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  alvo date := current_date - 1;
begin
  insert into public.metricas_diarias as m (
    dia, usuarios_novos, usuarios_ativos, submissoes,
    submissoes_aceitas, problemas_resolvidos, trechos_criados)
  select
    alvo,
    (select count(*) from public.perfis
      where criado_em::date = alvo),
    (select count(distinct dono_id) from public.submissoes
      where criado_em::date = alvo),
    (select count(*) from public.submissoes
      where criado_em::date = alvo),
    (select count(*) from public.submissoes
      where criado_em::date = alvo and estado = 'aceito'),
    (select count(*) from public.resolucoes
      where resolvido_em::date = alvo),
    (select count(*) from public.trechos
      where criado_em::date = alvo)
  on conflict (dia) do update set
    usuarios_novos       = excluded.usuarios_novos,
    usuarios_ativos      = excluded.usuarios_ativos,
    submissoes           = excluded.submissoes,
    submissoes_aceitas   = excluded.submissoes_aceitas,
    problemas_resolvidos = excluded.problemas_resolvidos,
    trechos_criados      = excluded.trechos_criados,
    calculado_em         = now();
  return 1;
end;
$$;

-- Quem passou um dia sem praticar perde a ofensiva. Zerar no cliente
-- não funciona: o usuário que some é justamente quem não abre o site.
create or replace function public.tarefa_zerar_ofensivas()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare afetados integer;
begin
  update public.perfis
     set ofensiva = 0
   where ofensiva > 0
     and (ultima_pratica is null or ultima_pratica < current_date - 1);
  get diagnostics afetados = row_count;
  return afetados;
end;
$$;

-- Resumo semanal na fila de envios, para quem praticou na semana.
create or replace function public.tarefa_resumo_semanal()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare enfileirados integer;
begin
  insert into public.envios (destino_id, assunto, corpo, dados)
  select
    p.id,
    'Sua semana no DataForge',
    format('Você resolveu %s problema(s) esta semana e está com %s XP.',
           coalesce(r.total, 0), p.xp),
    jsonb_build_object('xp', p.xp, 'ofensiva', p.ofensiva,
                       'resolvidos_semana', coalesce(r.total, 0))
  from public.perfis p
  left join (
    select dono_id, count(*) as total
      from public.resolucoes
     where resolvido and resolvido_em > now() - interval '7 days'
     group by dono_id
  ) r on r.dono_id = p.id
  where coalesce(r.total, 0) > 0;
  get diagnostics enfileirados = row_count;
  return enfileirados;
end;
$$;

-- Higiene: eventos velhos e execuções antigas não servem a ninguém e
-- crescem para sempre.
create or replace function public.tarefa_limpar_historico()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare removidos integer := 0;
        parcial integer;
begin
  delete from public.eventos where criado_em < now() - interval '90 days';
  get diagnostics parcial = row_count;  removidos := removidos + parcial;

  delete from public.execucoes_agendamento
   where comecou_em < now() - interval '30 days';
  get diagnostics parcial = row_count;  removidos := removidos + parcial;

  delete from public.envios
   where estado = 'enviado' and enviado_em < now() - interval '30 days';
  get diagnostics parcial = row_count;  removidos := removidos + parcial;

  return removidos;
end;
$$;

-- Marca envios pendentes como prontos para o worker. Roda de meia em
-- meia hora; um envio que falhou volta a ser tentado até 5 vezes.
create or replace function public.tarefa_processar_envios()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare prontos integer;
begin
  update public.envios
     set tentativas = tentativas + 1,
         estado = case when tentativas >= 4 then 'falhou' else 'pronto' end
   where estado = 'pendente' and agendado_para <= now();
  get diagnostics prontos = row_count;
  return prontos;
end;
$$;

-- Fotografia de hora em hora: quantos estão online, quanto se submeteu.
create or replace function public.tarefa_pulso_horario()
returns integer
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.eventos (tipo, dados)
  values ('pulso', jsonb_build_object(
    'usuarios', (select count(*) from public.perfis),
    'ativos_1h', (select count(distinct dono_id) from public.submissoes
                   where criado_em > now() - interval '1 hour'),
    'submissoes_1h', (select count(*) from public.submissoes
                       where criado_em > now() - interval '1 hour'),
    'em', now()));
  return 1;
end;
$$;

-- ═══════════════════════════════════════════════════════════════
--  3. O executor
-- ═══════════════════════════════════════════════════════════════

-- Roda uma tarefa pelo nome, registra o resultado e não deixa uma falha
-- derrubar o job do cron — senão um erro pontual pararia o agendamento
-- inteiro até alguém perceber.
create or replace function public.rodar_agendamento(p_nome text)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  agenda public.agendamentos;
  execucao_id bigint;
  resultado integer;
begin
  select * into agenda from public.agendamentos where nome = p_nome;
  if not found or not agenda.ativo then
    return;
  end if;

  -- Só funções desta migração podem ser chamadas. Sem esta lista, o
  -- campo 'funcao' seria injeção de SQL com passo de admin.
  if agenda.funcao not in (
      'tarefa_metricas_diarias', 'tarefa_zerar_ofensivas',
      'tarefa_resumo_semanal', 'tarefa_limpar_historico',
      'tarefa_processar_envios', 'tarefa_pulso_horario') then
    raise exception 'função não permitida: %', agenda.funcao;
  end if;

  insert into public.execucoes_agendamento (agendamento_id)
  values (agenda.id) returning id into execucao_id;

  begin
    execute format('select public.%I()', agenda.funcao) into resultado;

    update public.execucoes_agendamento
       set terminou_em = now(), sucesso = true, linhas_afetadas = resultado
     where id = execucao_id;
    update public.agendamentos
       set ultima_execucao = now(), ultimo_estado = 'ok'
     where id = agenda.id;
  exception when others then
    update public.execucoes_agendamento
       set terminou_em = now(), sucesso = false, detalhe = sqlerrm
     where id = execucao_id;
    update public.agendamentos
       set ultima_execucao = now(), ultimo_estado = 'erro: ' || sqlerrm
     where id = agenda.id;
  end;
end;
$$;

-- ═══════════════════════════════════════════════════════════════
--  4. O catálogo, e o cron que o dispara
-- ═══════════════════════════════════════════════════════════════

insert into public.agendamentos (nome, descricao, cadencia, expressao_cron, funcao)
values
  ('processar_envios',
   'Prepara os envios pendentes da fila. Repete até 5 vezes antes de desistir.',
   'a_cada_30_min', '*/30 * * * *', 'tarefa_processar_envios'),

  ('pulso_horario',
   'Fotografia de uso da última hora, para o gráfico do painel do admin.',
   'por_hora', '0 * * * *', 'tarefa_pulso_horario'),

  ('metricas_diarias',
   'Consolida o dia anterior numa linha de metricas_diarias.',
   'fim_do_dia', '10 3 * * *', 'tarefa_metricas_diarias'),

  ('zerar_ofensivas',
   'Zera a ofensiva de quem passou um dia sem praticar.',
   'diario', '5 3 * * *', 'tarefa_zerar_ofensivas'),

  ('limpar_historico',
   'Apaga eventos com mais de 90 dias e execuções com mais de 30.',
   'diario', '30 4 * * *', 'tarefa_limpar_historico'),

  ('resumo_semanal',
   'Enfileira o resumo da semana para quem praticou.',
   'semanal', '0 12 * * 1', 'tarefa_resumo_semanal')
on conflict (nome) do update set
  descricao      = excluded.descricao,
  cadencia       = excluded.cadencia,
  expressao_cron = excluded.expressao_cron,
  funcao         = excluded.funcao;

-- Sincroniza o pg_cron com a tabela. Idempotente: desagenda antes de
-- agendar, então rodar a migração de novo não duplica job.
create or replace function public.sincronizar_cron()
returns integer
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  agenda public.agendamentos;
  quantos integer := 0;
begin
  for agenda in select * from public.agendamentos loop
    begin
      perform cron.unschedule('df_' || agenda.nome);
    exception when others then null;   -- ainda não existia
    end;

    if agenda.ativo then
      perform cron.schedule(
        'df_' || agenda.nome,
        agenda.expressao_cron,
        format('select public.rodar_agendamento(%L)', agenda.nome));
      quantos := quantos + 1;
    end if;
  end loop;
  return quantos;
end;
$$;

select public.sincronizar_cron();

-- Mexeu no agendamento pelo painel, o cron acompanha. Sem isto, mudar a
-- expressão na tabela não mudaria nada de verdade.
create or replace function public.ao_mudar_agendamento()
returns trigger language plpgsql security definer
set search_path = public, extensions as $$
begin
  perform public.sincronizar_cron();
  return new;
end;
$$;

drop trigger if exists ao_mudar_agendamento on public.agendamentos;
create trigger ao_mudar_agendamento
  after insert or update of expressao_cron, ativo on public.agendamentos
  for each statement execute function public.ao_mudar_agendamento();
