/**
 * Prática: problemas, submissões e placar.
 *
 * A correção acontece **no navegador**, com o interpretador de verdade
 * (veja `lib/runtime.ts`). O que vem para cá é só o resultado — o banco
 * guarda o histórico, não julga o código.
 *
 * Isso tem uma consequência que vale dizer em voz alta: um usuário
 * determinado pode forjar uma submissão aceita chamando a API direto.
 * Para uma plataforma de estudo isso não importa — quem trapaceia só
 * engana a si mesmo. Se um dia houver competição valendo algo, a
 * correção precisa migrar para o servidor.
 */

import { obterCliente } from './cliente';

export type Dificuldade = 'facil' | 'medio' | 'dificil';

export type EstadoSubmissao =
  | 'aceito' | 'errado' | 'erro_execucao' | 'erro_sintaxe' | 'tempo_esgotado';

export type Problema = {
  id: string;
  slug: string;
  titulo: string;
  dificuldade: Dificuldade;
  categoria: string;
  enunciado: string;
  assinatura: string;
  exemplos: { entrada: string; saida: string }[];
  dicas: string[];
  casos: { entrada: unknown[]; saida: unknown }[];
  conceitos: string[];
  solucao?: string | null;
};

export type Resolucao = {
  problema_id: string;
  resolvido: boolean;
  tentativas: number;
  melhor_ms: number | null;
  resolvido_em: string | null;
};

export type Submissao = {
  id: string;
  problema_id: string;
  estado: EstadoSubmissao;
  testes_ok: number;
  testes_total: number;
  duracao_ms: number | null;
  criado_em: string;
};

type Resposta<T> = { dados: T; erro: string | null };

// ── Demonstração ────────────────────────────────────────────
// Sem banco, a prática ainda funciona: o corretor roda no navegador e
// só o histórico deixa de ser gravado.

const PROBLEMAS_DEMO: Problema[] = [
  {
    id: 'demo-1',
    slug: 'soma-dois',
    titulo: 'Soma de dois números',
    dificuldade: 'facil',
    categoria: 'fundamentos',
    enunciado:
      'Escreva a ação `resolver(a, b)` que devolve a soma de dois inteiros.\n\n'
      + 'É o primeiro problema: serve para você conhecer o editor, o botão '
      + 'de rodar e o formato da resposta.',
    assinatura: 'action resolver(a, b):',
    exemplos: [
      { entrada: 'a = 2, b = 3', saida: '5' },
      { entrada: 'a = -1, b = 1', saida: '0' },
    ],
    dicas: ['`yield` devolve o valor e encerra a ação.'],
    casos: [
      { entrada: [2, 3], saida: 5 },
      { entrada: [-1, 1], saida: 0 },
      { entrada: [0, 0], saida: 0 },
    ],
    conceitos: ['acoes', 'aritmetica'],
  },
  {
    id: 'demo-2',
    slug: 'fizzbuzz',
    titulo: 'FizzBuzz',
    dificuldade: 'facil',
    categoria: 'fundamentos',
    enunciado:
      'Devolva um cluster de 1 a n onde múltiplos de 3 viram "Fizz", de 5 '
      + 'viram "Buzz", e de ambos viram "FizzBuzz".\n\nO clássico. A ordem '
      + 'dos testes é o que separa quem acerta de quem quase acerta.',
    assinatura: 'action resolver(n):',
    exemplos: [{ entrada: 'n = 5', saida: '[1, 2, "Fizz", 4, "Buzz"]' }],
    dicas: ['Teste 15 primeiro — ou 3 e 5 juntos.'],
    casos: [
      { entrada: [5], saida: [1, 2, 'Fizz', 4, 'Buzz'] },
      { entrada: [3], saida: [1, 2, 'Fizz'] },
    ],
    conceitos: ['condicionais', 'cycle'],
  },
];

// ── Consultas ───────────────────────────────────────────────

export async function listarProblemas(): Promise<Resposta<Problema[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: PROBLEMAS_DEMO, erro: null };

  // A view não tem a coluna 'solucao'. A tabela crua é fechada a admin:
  // o Postgres não faz RLS por coluna, e uma política que liberasse a
  // linha entregaria a resposta junto com o enunciado.
  const { data, error } = await cliente
    .from('problemas_publicos')
    .select('id, slug, titulo, dificuldade, categoria, enunciado, '
          + 'assinatura, exemplos, dicas, casos, conceitos')
    .order('ordem');

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as Problema[], erro: null };
}

/**
 * A solução de referência de um problema.
 *
 * Vem de uma função do banco, não de uma consulta: ela entrega a
 * solução só a quem **já resolveu** o problema — ou a um admin. Quem
 * ainda não chegou lá recebe void, e a interface diz o porquê.
 *
 * Fosse uma coluna da listagem, a resposta viajaria junto com o
 * enunciado e apareceria na aba de rede de qualquer navegador.
 */
export async function buscarSolucao(
  problemaId: string
): Promise<Resposta<string | null>> {
  const cliente = obterCliente();
  if (!cliente) {
    return { dados: 'action resolver(a, b):\n    yield a + b', erro: null };
  }

  const { data, error } = await cliente.rpc('solucao_de', {
    p_problema: problemaId,
  });

  if (error) return { dados: null, erro: error.message };
  return { dados: (data as string) ?? null, erro: null };
}

export async function listarResolucoes(): Promise<Resposta<Resolucao[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    return {
      dados: [{
        problema_id: 'demo-1', resolvido: true, tentativas: 2,
        melhor_ms: 34, resolvido_em: new Date().toISOString(),
      }],
      erro: null,
    };
  }

  const { data, error } = await cliente
    .from('resolucoes')
    .select('problema_id, resolvido, tentativas, melhor_ms, resolvido_em');

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as Resolucao[], erro: null };
}

export async function listarSubmissoes(
  limite = 20
): Promise<Resposta<Submissao[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  const { data, error } = await cliente
    .from('submissoes')
    .select('id, problema_id, estado, testes_ok, testes_total, '
          + 'duracao_ms, criado_em')
    .order('criado_em', { ascending: false })
    .limit(limite);

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as Submissao[], erro: null };
}

/**
 * Grava uma submissão.
 *
 * O gatilho `ao_submeter` do banco cuida do resto: atualiza o resumo,
 * soma o XP na primeira vez que o problema é resolvido e ajusta a
 * ofensiva. Fazer isso em três chamadas do cliente deixaria o estado
 * inconsistente se o navegador fechasse no meio.
 */
export async function registrarSubmissao(entrada: {
  problemaId: string;
  codigo: string;
  estado: EstadoSubmissao;
  testesOk: number;
  testesTotal: number;
  duracaoMs: number;
  detalhe?: string;
}): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return null;

  const { data: sessao } = await cliente.auth.getUser();
  if (!sessao.user) return 'entre para gravar seu progresso';

  const { error } = await cliente.from('submissoes').insert({
    dono_id: sessao.user.id,
    problema_id: entrada.problemaId,
    codigo: entrada.codigo,
    estado: entrada.estado,
    testes_ok: entrada.testesOk,
    testes_total: entrada.testesTotal,
    duracao_ms: entrada.duracaoMs,
    detalhe: entrada.detalhe?.slice(0, 2000) ?? null,
  });

  return error ? error.message : null;
}

export type LinhaPlacar = {
  id: string;
  nome: string | null;
  avatar_url: string | null;
  xp: number;
  ofensiva: number;
  resolvidos: number;
  posicao: number;
};

export async function listarPlacar(limite = 20): Promise<Resposta<LinhaPlacar[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    return {
      dados: [
        { id: '1', nome: 'Você', avatar_url: null, xp: 180, ofensiva: 3,
          resolvidos: 7, posicao: 1 },
      ],
      erro: null,
    };
  }

  const { data, error } = await cliente
    .from('placar')
    .select('*')
    .order('posicao')
    .limit(limite);

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as LinhaPlacar[], erro: null };
}
