-- ═══════════════════════════════════════════════════════════════
--  Feedback, e as bibliotecas que a comunidade envia
-- ═══════════════════════════════════════════════════════════════
--
--  Duas coisas que o painel não tinha, e que puxam na mesma direção:
--  um caminho de volta de quem usa a linguagem para quem a escreve.
--
--    feedback              o que a pessoa achou
--    bibliotecas_enviadas  o que a pessoa escreveu, para os outros
--                          baixarem com 'dataforge add'
--
--  Quatro decisões que valem registrar:
--
--  1. AS DUAS TABELAS SÃO ESCRITAS POR FUNÇÃO, e não por INSERT
--     direto. Uma tabela aberta a 'authenticated' vira lixeira no dia
--     em que alguém descobre o endpoint: a função valida o tamanho, a
--     forma e a frequência antes de gravar.
--
--  2. LIMITE POR PESSOA E POR JANELA, dentro do banco. No cliente ele
--     é decoração — quem manda o POST escolhe se executa o JavaScript.
--     São 5 feedbacks por hora e 3 bibliotecas por dia.
--
--  3. A BIBLIOTECA NASCE 'pendente'. Aprovar é ato humano: um registro
--     que aceita pacote sem revisão é um vetor de distribuição de
--     código, e o `dataforge add` baixa e executa o que está lá.
--
--  4. O AUTOR NUNCA É APAGADO JUNTO. 'on delete set null' em vez de
--     'cascade': se alguém encerra a conta, o feedback e a biblioteca
--     continuam — eles são sobre a LINGUAGEM, não sobre a pessoa, e
--     apagar um pacote que outros já instalaram quebraria os projetos
--     deles.
--
--  Idempotente: pode rodar quantas vezes quiser.

-- ═══ Feedback ══════════════════════════════════════════════════

create table if not exists public.feedback (
  id           bigserial primary key,

  -- Nulo quando a conta foi encerrada depois. Ver decisão 4.
  autor_id     uuid references auth.users(id) on delete set null,

  -- Lista fechada. Aberta, o painel agruparia categorias inventadas.
  tipo         text not null
               check (tipo in ('elogio', 'problema', 'ideia', 'duvida', 'outro')),

  assunto      text not null check (length(assunto) between 3 and 120),
  mensagem     text not null check (length(mensagem) between 10 and 4000),

  -- De onde a pessoa escreveu. É o que transforma "está confuso" em
  -- "a página X está confusa" — sem isso, metade do feedback é
  -- impossível de agir.
  pagina       text,
  versao       text,

  estado       text not null default 'novo'
               check (estado in ('novo', 'lido', 'respondido', 'arquivado')),

  -- A resposta fica junto do pedido: procurar em outro lugar o que se
  -- respondeu a quem é como não ter respondido.
  resposta     text,
  respondido_por uuid references auth.users(id) on delete set null,
  respondido_em  timestamptz,

  criado_em    timestamptz not null default now()
);

create index if not exists feedback_estado_idx
  on public.feedback (estado, criado_em desc);
create index if not exists feedback_autor_idx
  on public.feedback (autor_id, criado_em desc);
create index if not exists feedback_tipo_idx
  on public.feedback (tipo, criado_em desc);

comment on table public.feedback is
  'O que quem usa achou. Escrito só por enviar_feedback(), que valida e limita.';

-- ═══ Bibliotecas enviadas pela comunidade ══════════════════════

create table if not exists public.bibliotecas_enviadas (
  id            bigserial primary key,
  autor_id      uuid references auth.users(id) on delete set null,

  -- O nome com que se instala: 'dataforge add <nome>'. Ele é a chave
  -- pública do pacote, então é único e tem forma fechada — um nome com
  -- '/' ou '..' viraria caminho ao ser extraído.
  nome          text not null unique
                check (nome ~ '^[a-z][a-z0-9_-]{1,38}[a-z0-9]$'),

  -- Semver. O registro resolve faixas ('^1.2') comparando estes
  -- números, e um texto livre aqui quebraria a resolução inteira.
  versao        text not null default '1.0.0'
                check (versao ~ '^[0-9]+\.[0-9]+\.[0-9]+([-+][0-9A-Za-z.-]+)?$'),

  descricao     text not null check (length(descricao) between 10 and 300),
  repositorio   text check (repositorio ~ '^https://'),
  documentacao  text check (documentacao ~ '^https://'),
  licenca       text not null default 'MIT' check (length(licenca) <= 40),

  -- Onde está o tarball. Só https: um link 'http' num instalador é um
  -- ataque de rede esperando acontecer.
  tarball       text not null check (tarball ~ '^https://'),

  -- O sha256 do tarball. Sem ele a verificação de integridade do
  -- 'dataforge add' não significa nada.
  sha256        text not null check (sha256 ~ '^[0-9a-f]{64}$'),

  -- Para a busca. 'text[]' e não texto separado por vírgula: o segundo
  -- não tem como ser indexado nem consultado sem varrer tudo.
  palavras      text[] not null default '{}',

  estado        text not null default 'pendente'
                check (estado in ('pendente', 'aprovada', 'recusada')),

  -- Por que foi recusada. Recusar sem dizer o motivo faz a pessoa
  -- reenviar a mesma coisa.
  motivo        text,
  revisado_por  uuid references auth.users(id) on delete set null,
  revisado_em   timestamptz,

  downloads     integer not null default 0,
  criado_em     timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists bibliotecas_estado_idx
  on public.bibliotecas_enviadas (estado, criado_em desc);
create index if not exists bibliotecas_autor_idx
  on public.bibliotecas_enviadas (autor_id, criado_em desc);
create index if not exists bibliotecas_palavras_idx
  on public.bibliotecas_enviadas using gin (palavras);

comment on table public.bibliotecas_enviadas is
  'Pacotes da comunidade. Nasce pendente: aprovar é ato humano, e o add executa o que baixa.';

-- ═══ RLS ═══════════════════════════════════════════════════════

alter table public.feedback             enable row level security;
alter table public.bibliotecas_enviadas enable row level security;

-- ── feedback ──
--
-- Quem escreveu lê o que escreveu, e mais nada: feedback costuma
-- conter frustração, e uma caixa pública muda o que as pessoas
-- escrevem nela.

drop policy if exists "feedback: autor lê o seu" on public.feedback;
create policy "feedback: autor lê o seu"
  on public.feedback for select
  using (autor_id = auth.uid() or public.e_admin());

drop policy if exists "feedback: só admin altera" on public.feedback;
create policy "feedback: só admin altera"
  on public.feedback for update
  using (public.e_admin()) with check (public.e_admin());

drop policy if exists "feedback: só admin apaga" on public.feedback;
create policy "feedback: só admin apaga"
  on public.feedback for delete using (public.e_admin());

-- Sem política de INSERT: a escrita passa só por 'enviar_feedback()'.

-- ── bibliotecas ──
--
-- O que foi APROVADO é público: é um registro de pacotes, e um
-- registro que só o dono enxerga não serve para nada. O que está
-- pendente ou recusado, só o autor e o admin.

drop policy if exists "bibliotecas: aprovada é pública" on public.bibliotecas_enviadas;
create policy "bibliotecas: aprovada é pública"
  on public.bibliotecas_enviadas for select
  using (estado = 'aprovada' or autor_id = auth.uid() or public.e_admin());

drop policy if exists "bibliotecas: admin modera" on public.bibliotecas_enviadas;
create policy "bibliotecas: admin modera"
  on public.bibliotecas_enviadas for update
  using (public.e_admin()) with check (public.e_admin());

drop policy if exists "bibliotecas: admin apaga" on public.bibliotecas_enviadas;
create policy "bibliotecas: admin apaga"
  on public.bibliotecas_enviadas for delete using (public.e_admin());

-- ═══ Escrever: as duas portas ══════════════════════════════════

create or replace function public.enviar_feedback(
  p_tipo     text,
  p_assunto  text,
  p_mensagem text,
  p_pagina   text default null,
  p_versao   text default null
)
returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
  v_id      bigint;
  v_recente integer;
begin
  if auth.uid() is null then
    raise exception 'é preciso entrar para enviar feedback'
      using hint = 'entre na conta e tente de novo';
  end if;

  -- O limite vive AQUI, e não no cliente: quem manda o POST escolhe
  -- se executa o JavaScript da página.
  select count(*) into v_recente
    from public.feedback
   where autor_id = auth.uid()
     and criado_em > now() - interval '1 hour';

  if v_recente >= 5 then
    raise exception 'muitos envios seguidos — cinco por hora'
      using hint = 'espere um pouco; o que já foi enviado não se perdeu';
  end if;

  -- Conferido AQUI, e não só pelo CHECK da tabela.
  --
  -- O CHECK protege o dado, e a mensagem dele é
  -- 'new row for relation "feedback" violates check constraint
  -- "feedback_assunto_check"' — que chega inteira na tela de quem
  -- escreveu. Ela fala da restrição, e não do que fazer.
  if p_tipo is null or p_tipo not in
     ('elogio', 'problema', 'ideia', 'duvida', 'outro') then
    raise exception 'tipo inválido: %', coalesce(p_tipo, 'nenhum')
      using hint = 'use elogio, problema, ideia, duvida ou outro';
  end if;

  if length(btrim(coalesce(p_assunto, ''))) < 3 then
    raise exception 'o assunto está curto demais'
      using hint = 'escreva de 3 a 120 caracteres — uma linha que resuma';
  end if;

  if length(btrim(p_assunto)) > 120 then
    raise exception 'o assunto passa de 120 caracteres'
      using hint = 'o resto cabe na mensagem';
  end if;

  if length(btrim(coalesce(p_mensagem, ''))) < 10 then
    raise exception 'a mensagem está curta demais'
      using hint = 'pelo menos dez caracteres — um "não funciona" sozinho não dá para agir';
  end if;

  if length(btrim(p_mensagem)) > 4000 then
    raise exception 'a mensagem passa de 4000 caracteres'
      using hint = 'se for um log longo, cole só o trecho que importa';
  end if;

  insert into public.feedback (autor_id, tipo, assunto, mensagem, pagina, versao)
  values (auth.uid(),
          coalesce(nullif(p_tipo, ''), 'outro'),
          btrim(p_assunto),
          btrim(p_mensagem),
          nullif(left(p_pagina, 200), ''),
          nullif(left(p_versao, 20), ''))
  returning id into v_id;

  return v_id;
end;
$$;

comment on function public.enviar_feedback is
  'A única porta de escrita do feedback. Valida, e limita a cinco por hora.';

grant execute on function public.enviar_feedback(text, text, text, text, text)
  to authenticated;

create or replace function public.enviar_biblioteca(
  p_nome         text,
  p_versao       text,
  p_descricao    text,
  p_tarball      text,
  p_sha256       text,
  p_licenca      text default 'MIT',
  p_repositorio  text default null,
  p_documentacao text default null,
  p_palavras     text[] default '{}'
)
returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
  v_id      bigint;
  v_recente integer;
  v_dono    uuid;
  v_estado  text;
begin
  if auth.uid() is null then
    raise exception 'é preciso entrar para enviar uma biblioteca'
      using hint = 'entre na conta e tente de novo';
  end if;

  select count(*) into v_recente
    from public.bibliotecas_enviadas
   where autor_id = auth.uid()
     and criado_em > now() - interval '1 day';

  if v_recente >= 3 then
    raise exception 'muitos envios seguidos — três por dia'
      using hint = 'revise o que já enviou antes de mandar outro';
  end if;

  -- Conferido aqui pelo mesmo motivo: a mensagem do CHECK fala da
  -- restrição, e quem lê precisa saber o que corrigir.
  if coalesce(lower(btrim(p_nome)), '') !~ '^[a-z][a-z0-9_-]{1,38}[a-z0-9]$' then
    raise exception 'nome de pacote inválido: %', coalesce(p_nome, 'nenhum')
      using hint = 'minúsculas, dígitos, hífen e _; começa por letra, '
                   'termina por letra ou dígito, de 3 a 40 caracteres';
  end if;

  if coalesce(p_versao, '') !~ '^[0-9]+\.[0-9]+\.[0-9]+([-+][0-9A-Za-z.-]+)?$' then
    raise exception 'versão inválida: %', coalesce(p_versao, 'nenhuma')
      using hint = 'use semver: 1.0.0, 2.1.3, 1.0.0-beta.1';
  end if;

  if length(btrim(coalesce(p_descricao, ''))) < 10 then
    raise exception 'a descrição está curta demais'
      using hint = 'de 10 a 300 caracteres — ela aparece no dataforge search';
  end if;

  if length(btrim(p_descricao)) > 300 then
    raise exception 'a descrição passa de 300 caracteres'
      using hint = 'o texto longo vai na documentação do pacote';
  end if;

  if coalesce(p_tarball, '') !~ '^https://' then
    raise exception 'o endereço do tarball precisa começar com https://'
      using hint = 'um link http num instalador é um ataque de rede esperando acontecer';
  end if;

  if coalesce(lower(p_sha256), '') !~ '^[0-9a-f]{64}$' then
    raise exception 'sha256 inválido'
      using hint = 'são 64 caracteres de 0-9 e a-f — o que o dataforge pack imprime';
  end if;

  if p_repositorio is not null and btrim(p_repositorio) <> ''
     and btrim(p_repositorio) !~ '^https://' then
    raise exception 'o repositório precisa começar com https://';
  end if;

  if p_documentacao is not null and btrim(p_documentacao) <> ''
     and btrim(p_documentacao) !~ '^https://' then
    raise exception 'a documentação precisa começar com https://';
  end if;

  -- O nome já existe? Só o DONO publica versão nova dele.
  --
  -- Sem esta conferência, quem chegasse depois sequestraria o nome de
  -- um pacote que outros já instalaram — e 'dataforge add' passaria a
  -- baixar outra coisa com o mesmo nome. É o ataque que mais aparece
  -- em registro de pacotes.
  select autor_id, estado into v_dono, v_estado
    from public.bibliotecas_enviadas where nome = lower(btrim(p_nome));

  if found then
    if v_dono is distinct from auth.uid() then
      raise exception 'o nome "%" já é de outra pessoa', lower(btrim(p_nome))
        using hint = 'escolha outro nome para o pacote';
    end if;

    update public.bibliotecas_enviadas
       set versao        = p_versao,
           descricao     = btrim(p_descricao),
           tarball       = p_tarball,
           sha256        = lower(p_sha256),
           licenca       = coalesce(nullif(btrim(p_licenca), ''), 'MIT'),
           repositorio   = nullif(btrim(p_repositorio), ''),
           documentacao  = nullif(btrim(p_documentacao), ''),
           palavras      = coalesce(p_palavras, '{}'),
           -- Versão nova volta para a fila: o que se revisou foi o
           -- conteúdo anterior, e aprovar o nome de uma vez tornaria a
           -- revisão inútil a partir do segundo envio.
           estado        = 'pendente',
           motivo        = null,
           revisado_por  = null,
           revisado_em   = null,
           atualizado_em = now()
     where nome = lower(btrim(p_nome))
    returning id into v_id;

    return v_id;
  end if;

  insert into public.bibliotecas_enviadas
    (autor_id, nome, versao, descricao, tarball, sha256, licenca,
     repositorio, documentacao, palavras)
  values
    (auth.uid(), lower(btrim(p_nome)), p_versao, btrim(p_descricao),
     p_tarball, lower(p_sha256),
     coalesce(nullif(btrim(p_licenca), ''), 'MIT'),
     nullif(btrim(p_repositorio), ''), nullif(btrim(p_documentacao), ''),
     coalesce(p_palavras, '{}'))
  returning id into v_id;

  return v_id;
end;
$$;

comment on function public.enviar_biblioteca is
  'A única porta de escrita. O nome é do primeiro dono: sem isso, ele seria sequestrável.';

grant execute on function public.enviar_biblioteca(
  text, text, text, text, text, text, text, text, text[]) to authenticated;

-- ═══ Moderar ═══════════════════════════════════════════════════

create or replace function public.revisar_biblioteca(
  p_id     bigint,
  p_estado text,
  p_motivo text default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.e_admin() then
    raise exception 'só quem modera pode revisar';
  end if;

  if p_estado not in ('pendente', 'aprovada', 'recusada') then
    raise exception 'estado inválido: %', p_estado;
  end if;

  -- Recusar sem motivo faz a pessoa reenviar a mesma coisa.
  if p_estado = 'recusada' and coalesce(btrim(p_motivo), '') = '' then
    raise exception 'diga por que foi recusada'
      using hint = 'o motivo é o que evita o reenvio idêntico';
  end if;

  update public.bibliotecas_enviadas
     set estado        = p_estado,
         motivo        = nullif(btrim(p_motivo), ''),
         revisado_por  = auth.uid(),
         revisado_em   = now(),
         atualizado_em = now()
   where id = p_id;
end;
$$;

grant execute on function public.revisar_biblioteca(bigint, text, text)
  to authenticated;

create or replace function public.responder_feedback(
  p_id       bigint,
  p_estado   text,
  p_resposta text default null
)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not public.e_admin() then
    raise exception 'só quem modera pode responder';
  end if;

  if p_estado not in ('novo', 'lido', 'respondido', 'arquivado') then
    raise exception 'estado inválido: %', p_estado;
  end if;

  update public.feedback
     set estado         = p_estado,
         resposta       = coalesce(nullif(btrim(p_resposta), ''), resposta),
         respondido_por = case when p_estado = 'respondido'
                               then auth.uid() else respondido_por end,
         respondido_em  = case when p_estado = 'respondido'
                               then now() else respondido_em end
   where id = p_id;
end;
$$;

grant execute on function public.responder_feedback(bigint, text, text)
  to authenticated;

-- ═══ O registro público ════════════════════════════════════════
--
-- É daqui que sai o 'index.json' que o 'dataforge add' consulta. Só o
-- que foi aprovado, e só os campos que o instalador precisa.

create or replace function public.registro_publico()
returns table (
  nome         text,
  versao       text,
  descricao    text,
  tarball      text,
  sha256       text,
  licenca      text,
  repositorio  text,
  palavras     text[],
  downloads    integer,
  atualizado_em timestamptz
)
language sql
stable
security definer
set search_path = public
as $$
  select nome, versao, descricao, tarball, sha256, licenca,
         repositorio, palavras, downloads, atualizado_em
    from public.bibliotecas_enviadas
   where estado = 'aprovada'
   order by downloads desc, nome;
$$;

grant execute on function public.registro_publico() to anon, authenticated;

create or replace function public.contar_download_biblioteca(p_nome text)
returns void
language sql
security definer
set search_path = public
as $$
  update public.bibliotecas_enviadas
     set downloads = downloads + 1
   where nome = lower(btrim(p_nome)) and estado = 'aprovada';
$$;

grant execute on function public.contar_download_biblioteca(text)
  to anon, authenticated;
