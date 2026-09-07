/**
 * Estrutura de navegação da documentação do DataForge.
 *
 * Espelha a arquitetura de informação de uma documentação de linguagem madura:
 * uma introdução, uma visão geral progressiva, fundamentos, técnicas aplicadas,
 * a biblioteca padrão, as ferramentas, os exercícios e a referência formal.
 */

export type NavItem = {
  title: string;
  href: string;
  badge?: string;
};

export type NavSection = {
  title: string;
  items: NavItem[];
  /** Seções de item único aparecem como link direto, sem acordeão. */
  standalone?: boolean;
  badge?: string;
  /** Começa aberta na primeira visita. */
  defaultOpen?: boolean;
};

export const nav: NavSection[] = [
  {
    title: 'Introdução',
    standalone: true,
    items: [{ title: 'Introdução', href: '/docs' }],
  },
  {
    title: 'Visão geral',
    defaultOpen: true,
    items: [
      { title: 'Primeiros passos', href: '/docs/primeiros-passos' },
      { title: 'Instalação', href: '/docs/instalacao' },
      { title: 'Variáveis', href: '/docs/variaveis' },
      { title: 'Tipos', href: '/docs/tipos' },
      { title: 'Operadores', href: '/docs/operadores' },
      { title: 'Condicionais', href: '/docs/condicionais' },
      { title: 'Laços', href: '/docs/lacos' },
      { title: 'Coleções', href: '/docs/colecoes' },
      { title: 'Textos', href: '/docs/textos' },
      { title: 'Ações', href: '/docs/acoes' },
      { title: 'Blueprints', href: '/docs/blueprints' },
      { title: 'Tratamento de erros', href: '/docs/erros' },
      { title: 'Pipelines', href: '/docs/pipelines' },
    ],
  },
  {
    title: 'Fundamentos',
    items: [
      { title: 'Anotações de tipo', href: '/docs/fundamentos/anotacoes-de-tipo' },
      { title: 'Records', href: '/docs/fundamentos/records' },
      { title: 'Enums', href: '/docs/fundamentos/enums' },
      { title: 'Pattern matching', href: '/docs/fundamentos/pattern-matching' },
      { title: 'Desestruturação', href: '/docs/fundamentos/desestruturacao' },
      { title: 'Spread e rest', href: '/docs/fundamentos/spread' },
      { title: 'Compreensões', href: '/docs/fundamentos/compreensoes' },
      { title: 'Interpolação', href: '/docs/fundamentos/interpolacao' },
      { title: 'Generators', href: '/docs/fundamentos/generators' },
      { title: 'Closures e lambdas', href: '/docs/fundamentos/closures' },
      { title: 'Decoradores', href: '/docs/fundamentos/decoradores' },
      { title: 'Traits', href: '/docs/fundamentos/traits' },
      { title: 'Escopo', href: '/docs/fundamentos/escopo' },
      { title: 'Módulos', href: '/docs/fundamentos/modulos' },
    ],
  },
  {
    title: 'Técnicas',
    items: [
      { title: 'Análise estática', href: '/docs/tecnicas/analise-estatica' },
      { title: 'Testes', href: '/docs/tecnicas/testes' },
      { title: 'Formatação', href: '/docs/tecnicas/formatacao' },
      { title: 'Lint', href: '/docs/tecnicas/lint' },
      { title: 'Documentação', href: '/docs/tecnicas/documentacao' },
      { title: 'Estrutura de projeto', href: '/docs/tecnicas/projeto' },
      { title: 'Concorrência', href: '/docs/tecnicas/concorrencia' },
      { title: 'Streams', href: '/docs/tecnicas/streams' },
      { title: 'Serialização', href: '/docs/tecnicas/serializacao' },
      { title: 'Arquivos', href: '/docs/tecnicas/arquivos' },
      { title: 'Banco de dados', href: '/docs/tecnicas/banco-de-dados' },
      { title: 'Servidor HTTP', href: '/docs/tecnicas/http' },
      { title: 'Logging', href: '/docs/tecnicas/logging' },
      { title: 'Datas e horas', href: '/docs/tecnicas/datas' },
      { title: 'Processos', href: '/docs/tecnicas/processos' },
      { title: 'Criptografia', href: '/docs/tecnicas/criptografia' },
    ],
  },
  {
    title: 'Biblioteca Arcane',
    items: [
      { title: 'Visão geral', href: '/docs/biblioteca' },
      { title: 'Arcane.Math', href: '/docs/biblioteca/math' },
      { title: 'Arcane.Text', href: '/docs/biblioteca/text' },
      { title: 'Arcane.Analytics', href: '/docs/biblioteca/analytics' },
      { title: 'Arcane.Functional', href: '/docs/biblioteca/functional' },
      { title: 'Arcane.Time', href: '/docs/biblioteca/time' },
      { title: 'Arcane.Async', href: '/docs/biblioteca/async' },
      { title: 'Arcane.Database', href: '/docs/biblioteca/database' },
      { title: 'Arcane.Crypto', href: '/docs/biblioteca/crypto' },
      { title: 'Arcane.OS', href: '/docs/biblioteca/os' },
      { title: 'Arcane.Collections', href: '/docs/biblioteca/collections' },
      { title: 'Arcane.Test', href: '/docs/biblioteca/test' },
      { title: 'Arcane.Regex', href: '/docs/biblioteca/regex' },
      { title: 'Arcane.IO', href: '/docs/biblioteca/io' },
      { title: 'Arcane.Serialization', href: '/docs/biblioteca/serialization' },
      { title: 'Arcane.Http', href: '/docs/biblioteca/http' },
      { title: 'Arcane.Process', href: '/docs/biblioteca/process' },
      { title: 'Arcane.Logging', href: '/docs/biblioteca/logging' },
      { title: 'Arcane.Data', href: '/docs/biblioteca/data' },
      { title: 'Arcane.Web', href: '/docs/biblioteca/web' },
      { title: 'Arcane.Cortex', href: '/docs/biblioteca/cortex' },
    ],
  },
  {
    title: 'CLI',
    items: [
      { title: 'Visão geral', href: '/docs/cli' },
      { title: 'dataforge run', href: '/docs/cli/run' },
      { title: 'dataforge check', href: '/docs/cli/check' },
      { title: 'dataforge test', href: '/docs/cli/test' },
      { title: 'dataforge fmt', href: '/docs/cli/fmt' },
      { title: 'dataforge lint', href: '/docs/cli/lint' },
      { title: 'dataforge doc', href: '/docs/cli/doc' },
      { title: 'dataforge init', href: '/docs/cli/init' },
      { title: 'dataforge repl', href: '/docs/cli/repl' },
      { title: 'forge.toml', href: '/docs/cli/forge-toml' },
    ],
  },
  {
    title: 'Exercícios',
    badge: '180',
    items: [
      { title: 'Visão geral', href: '/docs/exercicios' },
      { title: '01 · Fundamentos', href: '/docs/exercicios/01-fundamentos' },
      { title: '02 · Controle de fluxo', href: '/docs/exercicios/02-controle-fluxo' },
      { title: '03 · Coleções', href: '/docs/exercicios/03-colecoes' },
      { title: '04 · Textos', href: '/docs/exercicios/04-strings' },
      { title: '05 · Ações', href: '/docs/exercicios/05-acoes' },
      { title: '06 · Blueprints', href: '/docs/exercicios/06-blueprints' },
      { title: '07 · Erros', href: '/docs/exercicios/07-erros' },
      { title: '08 · Pipelines', href: '/docs/exercicios/08-pipelines' },
      { title: '09 · Módulos', href: '/docs/exercicios/09-modulos' },
      { title: '10 · Avançado', href: '/docs/exercicios/10-avancado' },
      { title: '11 · Tipos e checagem', href: '/docs/exercicios/11-tipos-e-checagem' },
      { title: '12 · Records e enums', href: '/docs/exercicios/12-records-e-enums' },
      { title: '13 · Desestruturação', href: '/docs/exercicios/13-desestruturacao' },
      { title: '14 · Pattern matching', href: '/docs/exercicios/14-pattern-matching' },
      { title: '15 · Streams', href: '/docs/exercicios/15-streams-e-generators' },
      { title: '16 · Módulos e projetos', href: '/docs/exercicios/16-modulos-e-projetos' },
      { title: '17 · Tempo e sistema', href: '/docs/exercicios/17-tempo-e-sistema' },
      { title: '18 · Persistência', href: '/docs/exercicios/18-dados-e-persistencia' },
      { title: '19 · Concorrência', href: '/docs/exercicios/19-concorrencia' },
      { title: '20 · Projetos finais', href: '/docs/exercicios/20-projetos-finais' },
    ],
  },
  {
    title: 'Referência',
    items: [
      { title: 'Gramática (EBNF)', href: '/docs/referencia/gramatica' },
      { title: 'Palavras reservadas', href: '/docs/referencia/palavras-reservadas' },
      { title: 'Operadores', href: '/docs/referencia/operadores' },
      { title: 'Precedência', href: '/docs/referencia/precedencia' },
      { title: 'Sistema de tipos', href: '/docs/referencia/tipos' },
      { title: 'Hierarquia de erros', href: '/docs/referencia/erros' },
      { title: 'Funções embutidas', href: '/docs/referencia/embutidas' },
      { title: 'Arquitetura do runtime', href: '/docs/referencia/arquitetura' },
    ],
  },
  {
    title: 'Receitas',
    items: [
      { title: 'Ferramenta de linha de comando', href: '/docs/receitas/cli' },
      { title: 'API REST', href: '/docs/receitas/api-rest' },
      { title: 'Pipeline ETL', href: '/docs/receitas/etl' },
      { title: 'Análise de dados', href: '/docs/receitas/analise-de-dados' },
      { title: 'Interpretador de expressões', href: '/docs/receitas/interpretador' },
      { title: 'Validadores brasileiros', href: '/docs/receitas/validadores' },
      { title: 'Fila de trabalho', href: '/docs/receitas/fila-de-trabalho' },
      { title: 'Máquina de estados', href: '/docs/receitas/maquina-de-estados' },
      { title: 'Processamento de CSV', href: '/docs/receitas/csv' },
      { title: 'Sistema de inventário', href: '/docs/receitas/inventario' },
    ],
  },
  {
    title: 'FAQ',
    items: [
      { title: 'Perguntas frequentes', href: '/docs/faq' },
      { title: 'Erros comuns', href: '/docs/faq/erros-comuns' },
      { title: 'Desempenho', href: '/docs/faq/desempenho' },
      { title: 'Comparação com Python', href: '/docs/faq/python' },
      { title: 'Comparação com JavaScript', href: '/docs/faq/javascript' },
      { title: 'Migração 3.x → 4.0', href: '/docs/faq/migracao' },
    ],
  },
  {
    title: 'Roadmap',
    standalone: true,
    items: [{ title: 'Roadmap', href: '/docs/roadmap' }],
  },
  {
    title: 'Contribuir',
    standalone: true,
    items: [{ title: 'Contribuir', href: '/docs/contribuir' }],
  },
];

/** Todas as rotas, achatadas — usado pelo "anterior/próximo" e pela busca. */
export const allRoutes: NavItem[] = nav.flatMap((s) => s.items);

/** Descobre a seção a que uma rota pertence. */
export function sectionOf(href: string): NavSection | undefined {
  return nav.find((s) => s.items.some((i) => i.href === href));
}

/** Vizinhos na ordem de leitura, para a navegação de rodapé. */
export function neighbours(href: string) {
  const i = allRoutes.findIndex((r) => r.href === href);
  return {
    prev: i > 0 ? allRoutes[i - 1] : undefined,
    next: i >= 0 && i < allRoutes.length - 1 ? allRoutes[i + 1] : undefined,
  };
}
