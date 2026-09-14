-- ═══════════════════════════════════════════════════════════════
--  Alinhar o banco com o que o painel consulta
-- ═══════════════════════════════════════════════════════════════
--
--  Três páginas do painel estavam quebradas em produção, e a mensagem
--  era sempre a mesma forma:
--
--    /painel/trechos     column trechos.linguagem does not exist
--    /painel/anotacoes   column anotacoes.titulo does not exist
--    /painel/exercicios  column progresso.modulo does not exist
--
--  O site e o esquema divergiram, e nada acusava: a consulta só falha
--  quando alguém abre a página, e o erro aparece na tela de quem usa —
--  não na CI, não nos testes, não no build.
--
--  A correção tem dois lados, e os dois importam:
--
--  1. AQUI, as colunas que carregam conteúdo de verdade — `linguagem`,
--     `titulo`, `modulo`, `tentativas`. Elas faltavam.
--
--  2. NO SITE, o nome do dono. Toda tabela deste banco usa `dono_id`, e
--     só estas três consultas escreviam `usuario_id`. Quem estava
--     errado era o código — e renomear a coluna para agradá-lo
--     quebraria as políticas de RLS de todas as outras.
--
--  `tests/test_painel_banco.py` compara os dois lados a cada execução,
--  para esta classe de erro não voltar a ser descoberta por um usuário.
--
--  Idempotente: pode rodar quantas vezes quiser.

-- ── trechos: em que linguagem está o trecho ───────────────────
--
-- O painel guarda trecho de DataForge, mas também o SQL de uma
-- migração e o shell de um deploy. Sem a coluna, o editor não sabe
-- como colorir, e o filtro por linguagem não existe.

alter table public.trechos
  add column if not exists linguagem text not null default 'dataforge';

comment on column public.trechos.linguagem is
  'dataforge, sql, bash, json… decide a coloração e o filtro.';

-- ── anotacoes: o título ───────────────────────────────────────
--
-- 'texto' já existe e é o corpo. O que faltava era o título: uma lista
-- de anotações sem título obriga a ler o corpo inteiro de cada uma
-- para achar a que se procura.

alter table public.anotacoes
  add column if not exists titulo text;

comment on column public.anotacoes.titulo is
  'Opcional. Sem ele, a lista obriga a ler o corpo de cada uma.';

-- ── progresso: o módulo e as tentativas ───────────────────────
--
-- 'modulo' é o que permite a barra por módulo — sem ela, o painel teria
-- de deduzir o módulo pelo NOME do exercício, e um renomeado quebraria
-- a conta em silêncio.
--
-- 'tentativas' distingue "acertou de primeira" de "acertou na décima".
-- É a diferença entre um exercício fácil e um mal explicado, e é o
-- número que diz qual reescrever.

alter table public.progresso
  add column if not exists modulo text not null default '';

alter table public.progresso
  add column if not exists tentativas integer not null default 1;

comment on column public.progresso.modulo is
  'Deduzir pelo nome do exercício quebraria em silêncio ao renomear um.';
comment on column public.progresso.tentativas is
  'Acertar de primeira e acertar na décima dizem coisas diferentes.';

-- 'progresso' tem chave composta (dono_id, exercicio) e NÃO tem 'id'.
-- O painel pedia 'id' por hábito; a correção é do lado do site, que
-- passou a usar a própria chave. Acrescentar um 'id' sintético aqui
-- criaria uma segunda identidade para a mesma linha.
