-- ═══════════════════════════════════════════════════════════════
--  Publicar pelo terminal: tokens
-- ═══════════════════════════════════════════════════════════════
--
--  O painel já publica uma biblioteca pelo navegador. Faltava o
--  caminho que um programador realmente usa:
--
--      dataforge login
--      dataforge publish --remoto
--
--  Isso exige uma credencial que viva fora do navegador, e uma
--  credencial dessas tem regras próprias.
--
--  Cinco decisões:
--
--  1. O TOKEN NÃO É GUARDADO. Só o `sha256` dele. Um vazamento do
--     banco não entrega a capacidade de publicar em nome de ninguém —
--     é a mesma razão de nenhum sistema sério guardar senha em texto.
--
--  2. ELE APARECE UMA VEZ SÓ, na criação. Poder relê-lo depois faria
--     do banco um cofre de credenciais ativas, que é exatamente o que
--     a decisão 1 evita.
--
--  3. O PREFIXO FICA VISÍVEL (`dfp_a1b2…`). Sem ele, a lista de
--     tokens é um monte de linhas idênticas, e revogar "o do meu
--     notebook antigo" vira adivinhação.
--
--  4. REVOGAR NÃO APAGA. A linha fica, com `revogado_em`. Apagar
--     perderia a trilha de que aquele token existiu e publicou — e é
--     justamente o que se quer consultar depois de um vazamento.
--
--  5. O TOKEN NÃO EXPIRA SOZINHO. Um que morre no meio de um deploy
--     ensina a guardar o de vida mais longa que existir. O que existe
--     é `ultimo_uso`, para revogar com informação.
--
--  Idempotente: pode rodar quantas vezes quiser.

-- O pgcrypto vive no schema 'extensions' no Supabase, e as funções
-- abaixo fixam 'search_path = public' — o que é a prática certa, e faz
-- 'digest()' e 'gen_random_bytes()' ficarem invisíveis para elas.
--
-- Por isso as chamadas são QUALIFICADAS ('extensions.digest'). Pôr
-- 'extensions' no search_path resolveria também, e abriria a porta que
-- o search_path fixo existe para fechar: uma função 'security definer'
-- que resolve nomes por um caminho que outra pessoa pode alterar.
create extension if not exists pgcrypto with schema extensions;

create table if not exists public.tokens_de_publicacao (
  id           bigserial primary key,
  dono_id      uuid not null references auth.users(id) on delete cascade,

  -- Como a pessoa reconhece este token. 'notebook', 'CI do projeto X'.
  nome         text not null check (length(nome) between 1 and 60),

  -- Os primeiros caracteres, para a lista não ser um monte de linhas
  -- iguais. Não identificam o token: são 8 de 48.
  prefixo      text not null,

  -- sha256 do token inteiro. É o ÚNICO vestígio dele aqui.
  hash         text not null unique check (hash ~ '^[0-9a-f]{64}$'),

  criado_em    timestamptz not null default now(),
  ultimo_uso   timestamptz,
  usos         integer not null default 0,
  revogado_em  timestamptz
);

create index if not exists tokens_dono_idx
  on public.tokens_de_publicacao (dono_id, criado_em desc);
create index if not exists tokens_hash_idx
  on public.tokens_de_publicacao (hash) where revogado_em is null;

comment on table public.tokens_de_publicacao is
  'Só o sha256 do token. Um vazamento do banco não publica em nome de ninguém.';

alter table public.tokens_de_publicacao enable row level security;

drop policy if exists "tokens: o dono ve os seus" on public.tokens_de_publicacao;
create policy "tokens: o dono ve os seus"
  on public.tokens_de_publicacao for select
  using (dono_id = auth.uid() or public.e_admin());

-- Sem INSERT nem UPDATE por política: a criação passa por função, que é
-- quem sabe gerar o token e devolver o texto uma única vez.

-- ── Criar ──────────────────────────────────────────────────────

create or replace function public.criar_token_de_publicacao(p_nome text)
returns text
language plpgsql
security definer
set search_path = public
as $$
declare
  v_token  text;
  v_ativos integer;
begin
  if auth.uid() is null then
    raise exception 'é preciso entrar para criar um token';
  end if;

  if coalesce(btrim(p_nome), '') = '' then
    raise exception 'dê um nome ao token'
      using hint = 'é por ele que você vai saber qual revogar depois';
  end if;

  select count(*) into v_ativos
    from public.tokens_de_publicacao
   where dono_id = auth.uid() and revogado_em is null;

  if v_ativos >= 10 then
    raise exception 'você já tem 10 tokens ativos'
      using hint = 'revogue os que não usa antes de criar outro';
  end if;

  -- 'dfp_' + 44 hexadecimais. O prefixo legível serve para a pessoa
  -- reconhecer o token na lista, e 'gen_random_bytes' é o gerador
  -- criptográfico — 'random()' seria previsível a partir da semente.
  v_token := 'dfp_' || encode(extensions.gen_random_bytes(22), 'hex');

  insert into public.tokens_de_publicacao (dono_id, nome, prefixo, hash)
  values (auth.uid(), btrim(p_nome), left(v_token, 12),
          encode(extensions.digest(v_token, 'sha256'), 'hex'));

  -- A ÚNICA vez que o texto existe fora da máquina de quem pediu.
  return v_token;
end;
$$;

grant execute on function public.criar_token_de_publicacao(text)
  to authenticated;

create or replace function public.revogar_token(p_id bigint)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  update public.tokens_de_publicacao
     set revogado_em = now()
   where id = p_id
     and (dono_id = auth.uid() or public.e_admin())
     and revogado_em is null;
end;
$$;

grant execute on function public.revogar_token(bigint) to authenticated;

-- ── Publicar com o token ───────────────────────────────────────
--
-- Esta função é o que o `dataforge publish --remoto` chama. Ela é
-- `security definer` e roda SEM sessão: quem prova identidade é o
-- token, e não um cookie.

create or replace function public.publicar_com_token(
  p_token        text,
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
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_dono   uuid;
  v_id     bigint;
  v_tok_id bigint;
  v_atual  uuid;
  v_recente integer;
begin
  select id, dono_id into v_tok_id, v_dono
    from public.tokens_de_publicacao
   where hash = encode(extensions.digest(coalesce(p_token, ''), 'sha256'), 'hex')
     and revogado_em is null;

  if v_dono is null then
    -- A mesma mensagem para "não existe" e "revogado", de propósito:
    -- distinguir os dois diria a quem tenta adivinhar que chegou perto.
    raise exception 'token inválido ou revogado'
      using hint = 'crie outro em /painel/tokens e rode dataforge login';
  end if;

  update public.tokens_de_publicacao
     set ultimo_uso = now(), usos = usos + 1
   where id = v_tok_id;

  -- As mesmas validações da porta do navegador. Elas estão aqui
  -- também porque esta função não passa por aquela: duplicar a regra é
  -- o preço de ter duas portas, e deixar uma delas sem guarda seria
  -- ter uma porta sem guarda.
  if coalesce(lower(btrim(p_nome)), '') !~ '^[a-z][a-z0-9_-]{1,38}[a-z0-9]$' then
    raise exception 'nome de pacote inválido: %', coalesce(p_nome, 'nenhum')
      using hint = 'minúsculas, dígitos, hífen e _; de 3 a 40 caracteres';
  end if;

  if coalesce(p_versao, '') !~ '^[0-9]+\.[0-9]+\.[0-9]+([-+][0-9A-Za-z.-]+)?$' then
    raise exception 'versão inválida: %', coalesce(p_versao, 'nenhuma')
      using hint = 'use semver: 1.0.0';
  end if;

  if length(btrim(coalesce(p_descricao, ''))) < 10 then
    raise exception 'a descrição está curta demais'
      using hint = 'de 10 a 300 caracteres — ela aparece no dataforge search';
  end if;

  if coalesce(p_tarball, '') !~ '^https://' then
    raise exception 'o endereço do tarball precisa começar com https://';
  end if;

  if coalesce(lower(p_sha256), '') !~ '^[0-9a-f]{64}$' then
    raise exception 'sha256 inválido'
      using hint = 'são 64 hexadecimais — o que o dataforge pack imprime';
  end if;

  select count(*) into v_recente
    from public.bibliotecas_enviadas
   where autor_id = v_dono and criado_em > now() - interval '1 day';
  if v_recente >= 10 then
    raise exception 'muitos envios hoje — dez por dia pelo terminal';
  end if;

  select autor_id into v_atual
    from public.bibliotecas_enviadas where nome = lower(btrim(p_nome));

  if found then
    if v_atual is distinct from v_dono then
      raise exception 'o nome "%" já é de outra pessoa', lower(btrim(p_nome))
        using hint = 'escolha outro nome para o pacote';
    end if;
    update public.bibliotecas_enviadas
       set versao = p_versao, descricao = btrim(p_descricao),
           tarball = p_tarball, sha256 = lower(p_sha256),
           licenca = coalesce(nullif(btrim(p_licenca), ''), 'MIT'),
           repositorio = nullif(btrim(p_repositorio), ''),
           documentacao = nullif(btrim(p_documentacao), ''),
           palavras = coalesce(p_palavras, '{}'),
           estado = 'pendente', motivo = null,
           revisado_por = null, revisado_em = null,
           atualizado_em = now()
     where nome = lower(btrim(p_nome))
    returning id into v_id;
  else
    insert into public.bibliotecas_enviadas
      (autor_id, nome, versao, descricao, tarball, sha256, licenca,
       repositorio, documentacao, palavras)
    values
      (v_dono, lower(btrim(p_nome)), p_versao, btrim(p_descricao),
       p_tarball, lower(p_sha256),
       coalesce(nullif(btrim(p_licenca), ''), 'MIT'),
       nullif(btrim(p_repositorio), ''), nullif(btrim(p_documentacao), ''),
       coalesce(p_palavras, '{}'))
    returning id into v_id;
  end if;

  return jsonb_build_object(
    'id', v_id,
    'nome', lower(btrim(p_nome)),
    'versao', p_versao,
    'estado', 'pendente');
end;
$$;

comment on function public.publicar_com_token is
  'A porta do terminal. Quem prova identidade é o token, não um cookie.';

grant execute on function public.publicar_com_token(
  text, text, text, text, text, text, text, text, text, text[])
  to anon, authenticated;

-- ── Quem sou eu, com este token ────────────────────────────────
--
-- O `dataforge login` precisa confirmar que o token vale ANTES de
-- guardá-lo em disco. Sem isso, o erro só apareceria no primeiro
-- publish — longe do comando que o causou.

create or replace function public.conferir_token(p_token text)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_nome  text;
  v_dono  uuid;
begin
  select t.nome, t.dono_id into v_nome, v_dono
    from public.tokens_de_publicacao t
   where t.hash = encode(extensions.digest(coalesce(p_token, ''), 'sha256'), 'hex')
     and t.revogado_em is null;

  if v_dono is null then
    return jsonb_build_object('valido', false);
  end if;

  return jsonb_build_object(
    'valido', true,
    'token', v_nome,
    'pacotes', (select count(*) from public.bibliotecas_enviadas
                 where autor_id = v_dono));
end;
$$;

grant execute on function public.conferir_token(text) to anon, authenticated;
