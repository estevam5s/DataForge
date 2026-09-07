'use client';

import { obterCliente } from './cliente';

/**
 * Acesso aos dados do painel.
 *
 * Toda função devolve `{ dados, erro }` — nunca estoura. Sem Supabase
 * configurado, devolve o conjunto de demonstração, para que a interface
 * possa ser vista e revisada antes de existirem credenciais.
 */

export type Projeto = {
  id: string;
  nome: string;
  descricao: string | null;
  publico: boolean;
  criado_em: string;
};

export type Trecho = {
  id: string;
  projeto_id: string;
  titulo: string;
  codigo: string;
  linguagem: string;
  criado_em: string;
};

export type Anotacao = {
  id: string;
  rota: string;
  titulo: string | null;
  conteudo: string;
  atualizado_em: string;
};

export type Progresso = {
  id: string;
  exercicio: string;
  modulo: string;
  concluido: boolean;
  tentativas: number;
};

type Resposta<T> = { dados: T; erro: string | null };

// ── Demonstração ───────────────────────────────────────────
// Dados plausíveis, para a interface poder ser avaliada sem banco.

const AGORA = new Date().toISOString();

const PROJETOS_DEMO: Projeto[] = [
  { id: 'p1', nome: 'Relatório de vendas', publico: false, criado_em: AGORA,
    descricao: 'Lê CSV, agrupa por região e imprime a tabela.' },
  { id: 'p2', nome: 'Validador de cadastro', publico: true, criado_em: AGORA,
    descricao: 'Usa validador + cofre para conferir formulário.' },
  { id: 'p3', nome: 'Interpretador de expressões', publico: true, criado_em: AGORA,
    descricao: 'Lexer, parser e avaliador em 200 linhas.' },
];

const TRECHOS_DEMO: Trecho[] = [
  { id: 't1', projeto_id: 'p1', titulo: 'Agrupar por região',
    linguagem: 'dataforge', criado_em: AGORA,
    codigo: 'adopt colecao as C\n\nvendas := ler_csv("vendas.csv")\n'
          + 'por_regiao := C.agrupar(vendas, lambda v => v["regiao"])\n\n'
          + 'cycle regiao in por_regiao.keys():\n'
          + '    total := C.somar_por(por_regiao[regiao], lambda v => v["valor"])\n'
          + '    out $"{regiao}: {total}"' },
  { id: 't2', projeto_id: 'p2', titulo: 'Esquema de validação',
    linguagem: 'dataforge', criado_em: AGORA,
    codigo: 'adopt validador as V\n\nregras := V.esquema({\n'
          + '    "email": [V.regra_obrigatorio(), V.regra_email()],\n'
          + '    "cpf": [V.regra_cpf()]\n})\n\n'
          + 'r := V.validar(regras, dados)\nout r["valido"], r["erros"]' },
];

const ANOTACOES_DEMO: Anotacao[] = [
  { id: 'a1', rota: '/docs/pipelines', titulo: 'Ordem do distill',
    conteudo: 'O acumulador vem primeiro: `distill acc, v: acc + v 0`. '
            + 'O 0 no fim é o valor inicial.',
    atualizado_em: AGORA },
  { id: 'a2', rota: '/docs/fundamentos/pattern-matching', titulo: 'point maiúsculo',
    conteudo: 'point n (minúsculo) captura; point Integer (maiúsculo) casa por tipo.',
    atualizado_em: AGORA },
];

const PROGRESSO_DEMO: Progresso[] = [
  { id: 'g1', exercicio: '001_ola_mundo', modulo: '01-fundamentos',
    concluido: true, tentativas: 1 },
  { id: 'g2', exercicio: '002_variaveis', modulo: '01-fundamentos',
    concluido: true, tentativas: 2 },
  { id: 'g3', exercicio: '013_condicionais', modulo: '02-controle-fluxo',
    concluido: true, tentativas: 1 },
  { id: 'g4', exercicio: '087_sift', modulo: '08-pipelines',
    concluido: false, tentativas: 3 },
];

// ── Consultas ──────────────────────────────────────────────

export async function listarProjetos(): Promise<Resposta<Projeto[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: PROJETOS_DEMO, erro: null };

  const { data, error } = await cliente
    .from('projetos')
    .select('id, nome, descricao, publico, criado_em')
    .order('atualizado_em', { ascending: false });
  return { dados: (data as Projeto[]) ?? [], erro: error?.message ?? null };
}

export async function criarProjeto(
  nome: string, descricao: string, publico: boolean,
): Promise<Resposta<Projeto | null>> {
  const cliente = obterCliente();
  if (!cliente) {
    const novo: Projeto = {
      id: `p${Date.now()}`, nome, descricao, publico,
      criado_em: new Date().toISOString(),
    };
    PROJETOS_DEMO.unshift(novo);
    return { dados: novo, erro: null };
  }

  const { data: sessao } = await cliente.auth.getUser();
  if (!sessao.user) return { dados: null, erro: 'Sessão expirada.' };

  const { data, error } = await cliente
    .from('projetos')
    .insert({ nome, descricao, publico, dono_id: sessao.user.id })
    .select()
    .single();
  return { dados: (data as Projeto) ?? null, erro: error?.message ?? null };
}

export async function apagarProjeto(id: string): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) {
    const i = PROJETOS_DEMO.findIndex((p) => p.id === id);
    if (i >= 0) PROJETOS_DEMO.splice(i, 1);
    return null;
  }
  const { error } = await cliente.from('projetos').delete().eq('id', id);
  return error?.message ?? null;
}

export async function listarTrechos(
  projetoId?: string,
): Promise<Resposta<Trecho[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    const filtrados = projetoId
      ? TRECHOS_DEMO.filter((t) => t.projeto_id === projetoId)
      : TRECHOS_DEMO;
    return { dados: filtrados, erro: null };
  }

  let consulta = cliente
    .from('trechos')
    .select('id, projeto_id, titulo, codigo, linguagem, criado_em')
    .order('atualizado_em', { ascending: false });
  if (projetoId) consulta = consulta.eq('projeto_id', projetoId);

  const { data, error } = await consulta;
  return { dados: (data as Trecho[]) ?? [], erro: error?.message ?? null };
}

export async function salvarTrecho(
  projetoId: string, titulo: string, codigo: string,
): Promise<Resposta<Trecho | null>> {
  const cliente = obterCliente();
  if (!cliente) {
    const novo: Trecho = {
      id: `t${Date.now()}`, projeto_id: projetoId, titulo, codigo,
      linguagem: 'dataforge', criado_em: new Date().toISOString(),
    };
    TRECHOS_DEMO.unshift(novo);
    return { dados: novo, erro: null };
  }

  const { data: sessao } = await cliente.auth.getUser();
  if (!sessao.user) return { dados: null, erro: 'Sessão expirada.' };

  const { data, error } = await cliente
    .from('trechos')
    .insert({
      projeto_id: projetoId, titulo, codigo,
      linguagem: 'dataforge', dono_id: sessao.user.id,
    })
    .select()
    .single();
  return { dados: (data as Trecho) ?? null, erro: error?.message ?? null };
}

export async function apagarTrecho(id: string): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) {
    const i = TRECHOS_DEMO.findIndex((t) => t.id === id);
    if (i >= 0) TRECHOS_DEMO.splice(i, 1);
    return null;
  }
  const { error } = await cliente.from('trechos').delete().eq('id', id);
  return error?.message ?? null;
}

export async function listarAnotacoes(): Promise<Resposta<Anotacao[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: ANOTACOES_DEMO, erro: null };

  const { data, error } = await cliente
    .from('anotacoes')
    .select('id, rota, titulo, conteudo, atualizado_em')
    .order('atualizado_em', { ascending: false });
  return { dados: (data as Anotacao[]) ?? [], erro: error?.message ?? null };
}

export async function salvarAnotacao(
  rota: string, titulo: string, conteudo: string,
): Promise<Resposta<Anotacao | null>> {
  const cliente = obterCliente();
  if (!cliente) {
    const nova: Anotacao = {
      id: `a${Date.now()}`, rota, titulo, conteudo,
      atualizado_em: new Date().toISOString(),
    };
    ANOTACOES_DEMO.unshift(nova);
    return { dados: nova, erro: null };
  }

  const { data: sessao } = await cliente.auth.getUser();
  if (!sessao.user) return { dados: null, erro: 'Sessão expirada.' };

  const { data, error } = await cliente
    .from('anotacoes')
    .insert({ rota, titulo, conteudo, usuario_id: sessao.user.id })
    .select()
    .single();
  return { dados: (data as Anotacao) ?? null, erro: error?.message ?? null };
}

export async function apagarAnotacao(id: string): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) {
    const i = ANOTACOES_DEMO.findIndex((a) => a.id === id);
    if (i >= 0) ANOTACOES_DEMO.splice(i, 1);
    return null;
  }
  const { error } = await cliente.from('anotacoes').delete().eq('id', id);
  return error?.message ?? null;
}

export async function listarProgresso(): Promise<Resposta<Progresso[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: PROGRESSO_DEMO, erro: null };

  const { data, error } = await cliente
    .from('progresso')
    .select('id, exercicio, modulo, concluido, tentativas');
  return { dados: (data as Progresso[]) ?? [], erro: error?.message ?? null };
}

export async function marcarExercicio(
  exercicio: string, modulo: string, concluido: boolean,
): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) {
    const existente = PROGRESSO_DEMO.find((p) => p.exercicio === exercicio);
    if (existente) existente.concluido = concluido;
    else PROGRESSO_DEMO.push({
      id: `g${Date.now()}`, exercicio, modulo, concluido, tentativas: 1,
    });
    return null;
  }

  const { data: sessao } = await cliente.auth.getUser();
  if (!sessao.user) return 'Sessão expirada.';

  // onConflict: a chave única (usuario_id, exercicio) faz o upsert
  // atualizar em vez de duplicar
  const { error } = await cliente.from('progresso').upsert(
    {
      usuario_id: sessao.user.id, exercicio, modulo, concluido,
      concluido_em: concluido ? new Date().toISOString() : null,
    },
    { onConflict: 'usuario_id,exercicio' },
  );
  return error?.message ?? null;
}
