/**
 * Consultas do painel administrativo.
 *
 * Nada aqui usa chave privilegiada: é o mesmo cliente `anon` do resto do
 * site. Quem decide o que este usuário pode ver é a RLS, com a função
 * `e_admin()` do banco — se alguém sem papel chamar estas funções, o
 * Postgres devolve zero linhas, não um erro de permissão.
 *
 * Isso é de propósito: uma tela de admin que só se esconde no cliente
 * não protege nada, porque o cliente é do usuário.
 */

import { obterCliente } from './cliente';

type Resposta<T> = { dados: T; erro: string | null };

export type MetricaDia = {
  dia: string;
  usuarios_novos: number;
  usuarios_ativos: number;
  submissoes: number;
  submissoes_aceitas: number;
  problemas_resolvidos: number;
  trechos_criados: number;
};

export type UsuarioAdmin = {
  id: string;
  nome: string | null;
  papel: 'usuario' | 'moderador' | 'admin';
  xp: number;
  ofensiva: number;
  ultima_pratica: string | null;
  criado_em: string;
};

export type Agendamento = {
  id: string;
  nome: string;
  descricao: string | null;
  cadencia: string;
  expressao_cron: string;
  funcao: string;
  ativo: boolean;
  ultima_execucao: string | null;
  ultimo_estado: string | null;
};

export type Execucao = {
  id: number;
  agendamento_id: string;
  comecou_em: string;
  terminou_em: string | null;
  sucesso: boolean | null;
  detalhe: string | null;
  linhas_afetadas: number | null;
};

export type Evento = {
  id: number;
  dono_id: string | null;
  tipo: string;
  dados: Record<string, unknown>;
  criado_em: string;
};

export type Resumo = {
  usuarios: number;
  problemas: number;
  submissoes: number;
  aceitas: number;
  resolvidos: number;
  agendamentos: number;
};

/** Números do topo do painel. Seis contagens numa ida só. */
export async function carregarResumo(): Promise<Resposta<Resumo>> {
  const cliente = obterCliente();
  const vazio: Resumo = {
    usuarios: 0, problemas: 0, submissoes: 0,
    aceitas: 0, resolvidos: 0, agendamentos: 0,
  };
  if (!cliente) {
    return {
      dados: { usuarios: 128, problemas: 16, submissoes: 943,
               aceitas: 612, resolvidos: 428, agendamentos: 6 },
      erro: null,
    };
  }

  // head:true traz só a contagem, sem as linhas — o que importa aqui.
  const contar = (tabela: string, filtro?: [string, string]) => {
    let consulta = cliente.from(tabela).select('*', { count: 'exact', head: true });
    if (filtro) consulta = consulta.eq(filtro[0], filtro[1]);
    return consulta;
  };

  const [u, p, s, a, r, g] = await Promise.all([
    contar('perfis'),
    contar('problemas'),
    contar('submissoes'),
    contar('submissoes', ['estado', 'aceito']),
    contar('resolucoes', ['resolvido', 'true']),
    contar('agendamentos'),
  ]);

  const erro = [u, p, s, a, r, g].find((x) => x.error)?.error?.message ?? null;

  return {
    dados: {
      usuarios: u.count ?? 0,
      problemas: p.count ?? 0,
      submissoes: s.count ?? 0,
      aceitas: a.count ?? 0,
      resolvidos: r.count ?? 0,
      agendamentos: g.count ?? 0,
    },
    erro: erro && !u.count ? erro : null,
  };
}

export async function listarMetricas(dias = 30): Promise<Resposta<MetricaDia[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    const hoje = new Date();
    const dados = Array.from({ length: 14 }, (_, i) => {
      const d = new Date(hoje);
      d.setDate(d.getDate() - (13 - i));
      return {
        dia: d.toISOString().slice(0, 10),
        usuarios_novos: Math.floor(Math.random() * 8),
        usuarios_ativos: 12 + Math.floor(Math.random() * 20),
        submissoes: 30 + Math.floor(Math.random() * 60),
        submissoes_aceitas: 18 + Math.floor(Math.random() * 30),
        problemas_resolvidos: 10 + Math.floor(Math.random() * 20),
        trechos_criados: Math.floor(Math.random() * 6),
      };
    });
    return { dados, erro: null };
  }

  const { data, error } = await cliente
    .from('metricas_diarias')
    .select('*')
    .order('dia', { ascending: false })
    .limit(dias);

  if (error) return { dados: [], erro: error.message };
  return {
    dados: ((data ?? []) as unknown as MetricaDia[]).reverse(),
    erro: null,
  };
}

export async function listarUsuarios(
  limite = 100
): Promise<Resposta<UsuarioAdmin[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    return {
      dados: [
        { id: '1', nome: 'Visitante', papel: 'admin', xp: 180, ofensiva: 3,
          ultima_pratica: new Date().toISOString().slice(0, 10),
          criado_em: new Date().toISOString() },
      ],
      erro: null,
    };
  }

  const { data, error } = await cliente
    .from('perfis')
    .select('id, nome, papel, xp, ofensiva, ultima_pratica, criado_em')
    .order('criado_em', { ascending: false })
    .limit(limite);

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as UsuarioAdmin[], erro: null };
}

/**
 * Troca o papel de alguém.
 *
 * A política "perfis: admin edita qualquer um" permite isto; a política
 * do dono impede que ele mude o próprio papel. Um usuário comum que
 * tentar chamar esta função não recebe erro — a linha simplesmente não
 * é encontrada pela RLS.
 */
export async function mudarPapel(
  id: string,
  papel: UsuarioAdmin['papel']
): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return null;
  const { error } = await cliente.from('perfis').update({ papel }).eq('id', id);
  return error ? error.message : null;
}

export async function listarAgendamentos(): Promise<Resposta<Agendamento[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    return {
      dados: [
        { id: '1', nome: 'processar_envios',
          descricao: 'Prepara os envios pendentes da fila.',
          cadencia: 'a_cada_30_min', expressao_cron: '*/30 * * * *',
          funcao: 'tarefa_processar_envios', ativo: true,
          ultima_execucao: new Date().toISOString(), ultimo_estado: 'ok' },
        { id: '2', nome: 'metricas_diarias',
          descricao: 'Consolida o dia anterior.',
          cadencia: 'fim_do_dia', expressao_cron: '10 3 * * *',
          funcao: 'tarefa_metricas_diarias', ativo: true,
          ultima_execucao: new Date().toISOString(), ultimo_estado: 'ok' },
      ],
      erro: null,
    };
  }

  const { data, error } = await cliente
    .from('agendamentos')
    .select('*')
    .order('nome');

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as Agendamento[], erro: null };
}

/**
 * Liga ou desliga uma tarefa.
 *
 * O gatilho `ao_mudar_agendamento` sincroniza o pg_cron sozinho: sem
 * ele, mudar a linha na tabela não mudaria nada de verdade.
 */
export async function alternarAgendamento(
  id: string,
  ativo: boolean
): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return null;
  const { error } = await cliente.from('agendamentos').update({ ativo }).eq('id', id);
  return error ? error.message : null;
}

export async function mudarCron(
  id: string,
  expressao: string
): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return null;

  // Cinco campos: minuto, hora, dia, mês, dia-da-semana. Validar aqui
  // evita gravar algo que o pg_cron recusa silenciosamente.
  if (expressao.trim().split(/\s+/).length !== 5) {
    return 'a expressão cron precisa de cinco campos: min hora dia mês semana';
  }

  const { error } = await cliente
    .from('agendamentos')
    .update({ expressao_cron: expressao.trim() })
    .eq('id', id);
  return error ? error.message : null;
}

export async function listarExecucoes(
  limite = 40
): Promise<Resposta<Execucao[]>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: [], erro: null };

  const { data, error } = await cliente
    .from('execucoes_agendamento')
    .select('*')
    .order('comecou_em', { ascending: false })
    .limit(limite);

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as Execucao[], erro: null };
}

export async function listarEventos(limite = 80): Promise<Resposta<Evento[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    return {
      dados: [
        { id: 1, dono_id: null, tipo: 'pulso',
          dados: { usuarios: 128, ativos_1h: 9 },
          criado_em: new Date().toISOString() },
      ],
      erro: null,
    };
  }

  const { data, error } = await cliente
    .from('eventos')
    .select('*')
    .order('criado_em', { ascending: false })
    .limit(limite);

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as Evento[], erro: null };
}

export type ProblemaAdmin = {
  id: string;
  slug: string;
  titulo: string;
  dificuldade: string;
  categoria: string;
  publicado: boolean;
  ordem: number;
};

export async function listarProblemasAdmin(): Promise<Resposta<ProblemaAdmin[]>> {
  const cliente = obterCliente();
  if (!cliente) {
    return {
      dados: [
        { id: '1', slug: 'soma-dois', titulo: 'Soma de dois números',
          dificuldade: 'facil', categoria: 'fundamentos',
          publicado: true, ordem: 0 },
      ],
      erro: null,
    };
  }

  const { data, error } = await cliente
    .from('problemas')
    .select('id, slug, titulo, dificuldade, categoria, publicado, ordem')
    .order('ordem');

  if (error) return { dados: [], erro: error.message };
  return { dados: (data ?? []) as unknown as ProblemaAdmin[], erro: null };
}

export async function publicarProblema(
  id: string,
  publicado: boolean
): Promise<string | null> {
  const cliente = obterCliente();
  if (!cliente) return null;
  const { error } = await cliente
    .from('problemas')
    .update({ publicado })
    .eq('id', id);
  return error ? error.message : null;
}

// ── Downloads ────────────────────────────────────────────────

export type PainelDownloads = {
  total: number;
  total_periodo: number;
  unicos_periodo: number;
  hoje: number;
  por_dia: { dia: string; total: number }[];
  por_origem: Record<string, number>;
  por_sistema: Record<string, number>;
  por_versao: Record<string, number>;
  por_pais: { pais: string; total: number }[];
  ultimos: {
    origem: string;
    sistema: string | null;
    versao: string;
    pais: string | null;
    quando: string;
  }[];
};

const DOWNLOADS_VAZIO: PainelDownloads = {
  total: 0, total_periodo: 0, unicos_periodo: 0, hoje: 0,
  por_dia: [], por_origem: {}, por_sistema: {}, por_versao: {},
  por_pais: [], ultimos: [],
};

/**
 * Tudo o que o painel de downloads mostra, numa chamada só.
 *
 * O agrupamento acontece no Postgres, e não aqui: trazer cem mil
 * linhas para o navegador contar seria transferir megabytes para
 * produzir oito números.
 */
export async function carregarDownloads(
  dias = 30,
): Promise<Resposta<PainelDownloads>> {
  const cliente = obterCliente();
  if (!cliente) return { dados: DOWNLOADS_VAZIO, erro: null };

  const { data, error } = await cliente.rpc('painel_de_downloads', {
    p_dias: dias,
  });
  if (error) return { dados: DOWNLOADS_VAZIO, erro: error.message };
  return { dados: { ...DOWNLOADS_VAZIO, ...(data as PainelDownloads) }, erro: null };
}

/** O total público — o mesmo número que o site mostra. */
export async function totalDeDownloads(): Promise<number> {
  const cliente = obterCliente();
  if (!cliente) return 0;
  const { data, error } = await cliente.rpc('total_de_downloads');
  return error ? 0 : Number(data ?? 0);
}
