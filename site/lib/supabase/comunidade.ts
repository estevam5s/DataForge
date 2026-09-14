/**
 * Feedback e bibliotecas da comunidade.
 *
 * Nada aqui escreve numa tabela direto. As duas escritas passam por
 * função do Postgres (`enviar_feedback`, `enviar_biblioteca`), e o
 * motivo é o mesmo dos downloads: uma tabela aberta a `authenticated`
 * vira lixeira no dia em que alguém descobre o endpoint. A função
 * valida tamanho, forma e **frequência** — e a frequência precisa
 * viver no banco, porque quem manda o POST escolhe se executa o
 * JavaScript da página.
 *
 * Quem decide o que cada um lê é a RLS: o autor vê o que escreveu, o
 * admin vê tudo, e uma biblioteca aprovada é pública.
 */

import { obterCliente } from './cliente';

type Resposta<T> = { dados: T; erro: string | null };

export type TipoDeFeedback =
  | 'elogio' | 'problema' | 'ideia' | 'duvida' | 'outro';

export const TIPOS: { valor: TipoDeFeedback; rotulo: string; dica: string }[] = [
  { valor: 'problema', rotulo: 'Problema', dica: 'algo não funciona como deveria' },
  { valor: 'ideia', rotulo: 'Ideia', dica: 'algo que falta, ou que daria para melhorar' },
  { valor: 'duvida', rotulo: 'Dúvida', dica: 'a documentação não respondeu' },
  { valor: 'elogio', rotulo: 'Elogio', dica: 'algo que funcionou bem' },
  { valor: 'outro', rotulo: 'Outro', dica: 'o que não cabe acima' },
];

export type Feedback = {
  id: number;
  autor_id: string | null;
  tipo: TipoDeFeedback;
  assunto: string;
  mensagem: string;
  pagina: string | null;
  versao: string | null;
  estado: 'novo' | 'lido' | 'respondido' | 'arquivado';
  resposta: string | null;
  respondido_em: string | null;
  criado_em: string;
};

export type Biblioteca = {
  id: number;
  autor_id: string | null;
  nome: string;
  versao: string;
  descricao: string;
  repositorio: string | null;
  documentacao: string | null;
  licenca: string;
  tarball: string;
  sha256: string;
  palavras: string[];
  estado: 'pendente' | 'aprovada' | 'recusada';
  motivo: string | null;
  revisado_em: string | null;
  downloads: number;
  criado_em: string;
  atualizado_em: string;
};

/**
 * A mensagem do Postgres, e não "algo deu errado".
 *
 * As exceções das funções trazem `hint` junto — "espere um pouco; o
 * que já foi enviado não se perdeu" —, e é justamente a parte que diz
 * o que fazer. Descartá-la deixa só a metade que reclama.
 */
function explicar(erro: { message: string; hint?: string | null }): string {
  const dica = erro.hint ? ` ${erro.hint}` : '';
  return `${erro.message}.${dica}`.replace(/\.\./g, '.');
}

const SEM_BANCO = 'O painel está em modo demonstração: não há banco configurado.';

// ═══ Feedback ══════════════════════════════════════════════════

export async function enviarFeedback(campos: {
  tipo: TipoDeFeedback;
  assunto: string;
  mensagem: string;
  pagina?: string;
  versao?: string;
}): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return SEM_BANCO;

  const { error } = await cliente.rpc('enviar_feedback', {
    p_tipo: campos.tipo,
    p_assunto: campos.assunto,
    p_mensagem: campos.mensagem,
    p_pagina: campos.pagina ?? null,
    p_versao: campos.versao ?? null,
  });
  return error ? explicar(error) : null;
}

/** O que EU escrevi. A RLS já limita; o filtro aqui é só clareza. */
export async function meusFeedbacks(): Promise<Resposta<Feedback[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  const { data, error } = await cliente
    .from('feedback')
    .select('*')
    .order('criado_em', { ascending: false })
    .limit(50);
  return { dados: (data ?? []) as Feedback[], erro: error?.message ?? null };
}

export async function listarFeedbackAdmin(
  estado?: Feedback['estado'],
): Promise<Resposta<Feedback[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  let consulta = cliente
    .from('feedback')
    .select('*')
    .order('criado_em', { ascending: false })
    .limit(300);
  if (estado) consulta = consulta.eq('estado', estado);

  const { data, error } = await consulta;
  return { dados: (data ?? []) as Feedback[], erro: error?.message ?? null };
}

export async function responderFeedback(
  id: number,
  estado: Feedback['estado'],
  resposta?: string,
): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return SEM_BANCO;

  const { error } = await cliente.rpc('responder_feedback', {
    p_id: id, p_estado: estado, p_resposta: resposta ?? null,
  });
  return error ? explicar(error) : null;
}

// ═══ Bibliotecas ═══════════════════════════════════════════════

export async function enviarBiblioteca(campos: {
  nome: string;
  versao: string;
  descricao: string;
  tarball: string;
  sha256: string;
  licenca?: string;
  repositorio?: string;
  documentacao?: string;
  palavras?: string[];
}): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return SEM_BANCO;

  const { error } = await cliente.rpc('enviar_biblioteca', {
    p_nome: campos.nome,
    p_versao: campos.versao,
    p_descricao: campos.descricao,
    p_tarball: campos.tarball,
    p_sha256: campos.sha256,
    p_licenca: campos.licenca ?? 'MIT',
    p_repositorio: campos.repositorio || null,
    p_documentacao: campos.documentacao || null,
    p_palavras: campos.palavras ?? [],
  });
  return error ? explicar(error) : null;
}

/** As aprovadas — o registro que o `dataforge add` enxerga. */
export async function bibliotecasPublicas(): Promise<Resposta<Biblioteca[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  const { data, error } = await cliente
    .from('bibliotecas_enviadas')
    .select('*')
    .eq('estado', 'aprovada')
    .order('downloads', { ascending: false });
  return { dados: (data ?? []) as Biblioteca[], erro: error?.message ?? null };
}

/**
 * As minhas, em qualquer estado.
 *
 * Vem numa consulta separada da pública porque a RLS devolve as duas
 * coisas juntas — as aprovadas de todo mundo e as minhas pendentes —,
 * e misturá-las faria a tela dizer que a biblioteca de outra pessoa é
 * minha.
 */
export async function minhasBibliotecas(
  autorId: string,
): Promise<Resposta<Biblioteca[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  const { data, error } = await cliente
    .from('bibliotecas_enviadas')
    .select('*')
    .eq('autor_id', autorId)
    .order('atualizado_em', { ascending: false });
  return { dados: (data ?? []) as Biblioteca[], erro: error?.message ?? null };
}

export async function listarBibliotecasAdmin(
  estado?: Biblioteca['estado'],
): Promise<Resposta<Biblioteca[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  let consulta = cliente
    .from('bibliotecas_enviadas')
    .select('*')
    .order('criado_em', { ascending: false })
    .limit(300);
  if (estado) consulta = consulta.eq('estado', estado);

  const { data, error } = await consulta;
  return { dados: (data ?? []) as Biblioteca[], erro: error?.message ?? null };
}

export async function revisarBiblioteca(
  id: number,
  estado: Biblioteca['estado'],
  motivo?: string,
): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return SEM_BANCO;

  const { error } = await cliente.rpc('revisar_biblioteca', {
    p_id: id, p_estado: estado, p_motivo: motivo ?? null,
  });
  return error ? explicar(error) : null;
}

// ═══ Tokens de publicação ══════════════════════════════════════
//
// O token existe em texto uma vez só, na criação. O banco guarda o
// `sha256` dele — um vazamento não entrega a capacidade de publicar em
// nome de ninguém. Por isso `criarToken` devolve a string e nada mais
// a recupera depois.

export type TokenDePublicacao = {
  id: number;
  nome: string;
  prefixo: string;
  criado_em: string;
  ultimo_uso: string | null;
  usos: number;
  revogado_em: string | null;
};

export async function listarTokens(): Promise<Resposta<TokenDePublicacao[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  const { data, error } = await cliente
    .from('tokens_de_publicacao')
    .select('id, nome, prefixo, criado_em, ultimo_uso, usos, revogado_em')
    .order('criado_em', { ascending: false });
  return {
    dados: (data ?? []) as TokenDePublicacao[],
    erro: error?.message ?? null,
  };
}

/** O token em texto — a única vez que ele existe fora do banco. */
export async function criarToken(
  nome: string,
): Promise<{ token: string | null; erro: string | null }> {
  const cliente = obterCliente();
  if (!cliente) return { token: null, erro: SEM_BANCO };

  const { data, error } = await cliente.rpc('criar_token_de_publicacao', {
    p_nome: nome,
  });
  if (error) return { token: null, erro: explicar(error) };
  return { token: data as string, erro: null };
}

export async function revogarToken(id: number): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return SEM_BANCO;
  const { error } = await cliente.rpc('revogar_token', { p_id: id });
  return error ? explicar(error) : null;
}
