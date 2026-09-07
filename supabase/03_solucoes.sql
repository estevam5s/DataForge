-- ═══════════════════════════════════════════════════════════════
--  DataForge · Esconder a solução de referência
--
--  O 01 comentava que a RLS escondia a coluna 'solucao' — e não
--  escondia. O Postgres não tem RLS por coluna: a política de select
--  libera a linha inteira, solução junto. Qualquer um com a chave anon
--  lia a resposta de todos os problemas.
--
--  A saída em três partes: uma view sem a coluna, a tabela fechada a
--  admin, e uma função que entrega a solução só a quem já resolveu.
-- ═══════════════════════════════════════════════════════════════

-- ── 1. A view que o painel consome ──

-- security_invoker = off (o padrão): a view roda com os direitos de
-- quem a criou, não de quem a consulta. É o que permite ela enxergar a
-- tabela fechada e devolver só as colunas listadas — a forma canônica
-- de fazer "RLS por coluna" no Postgres, que não tem isso nativamente.
--
-- O preço é que a view ignora a política de 'problemas': o filtro é o
-- 'where publicado' aqui, e as colunas são as desta lista. Por isso ela
-- é escrita com as colunas **explícitas**, nunca 'select *' — assim uma
-- coluna nova só aparece se alguém a acrescentar de propósito. Há teste
-- que falha se 'solucao' voltar a aparecer.
-- 'create or replace view' recusa mudar a lista de colunas; num
-- reaplicar depois de editar a lista, ele falha com "cannot drop columns
-- from view". Derrubar antes torna a migração de verdade idempotente.
drop view if exists public.problemas_publicos;

create view public.problemas_publicos as
  select
    id, slug, titulo, dificuldade, categoria, enunciado, assinatura,
    exemplos, dicas, casos, conceitos, ordem, criado_em
  from public.problemas
  where publicado;

comment on view public.problemas_publicos is
  'Os problemas sem a coluna solucao. É o que a prática lê — a tabela '
  'crua fica fechada, porque o Postgres não faz RLS por coluna.';

grant select on public.problemas_publicos to anon, authenticated;

-- ── 2. A tabela crua fecha ──

drop policy if exists "problemas: publicados para todos" on public.problemas;

drop policy if exists "problemas: só admin lê a tabela crua" on public.problemas;
create policy "problemas: só admin lê a tabela crua"
  on public.problemas for select using (public.e_admin());

-- ── 3. A solução, para quem tem direito ──

create or replace function public.solucao_de(p_problema uuid)
returns text
language plpgsql
stable
security definer
set search_path = public
as $$
declare
  ja_resolveu boolean;
begin
  if auth.uid() is null then
    return null;
  end if;

  if public.e_admin() then
    return (select solucao from public.problemas where id = p_problema);
  end if;

  select resolvido into ja_resolveu
    from public.resolucoes
   where dono_id = auth.uid() and problema_id = p_problema;

  -- Quem ainda não resolveu recebe void, não um erro: a interface
  -- mostra "resolva primeiro", que é mais útil que "sem permissão".
  if coalesce(ja_resolveu, false) then
    return (select solucao from public.problemas where id = p_problema);
  end if;

  return null;
end;
$$;

comment on function public.solucao_de is
  'A solução de referência, só para quem já resolveu o problema — ou '
  'para admin. Devolve void em vez de erro para quem ainda não chegou lá.';

revoke all on function public.solucao_de(uuid) from public;
grant execute on function public.solucao_de(uuid) to authenticated;
