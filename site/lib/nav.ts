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
    items: [{ title: 'Introdução', href: '/' }],
  },
  {
    title: 'Visão geral',
    defaultOpen: true,
    items: [
      { title: 'Primeiros passos', href: '/primeiros-passos' },
      { title: 'Instalação', href: '/instalacao' },
      { title: 'Variáveis', href: '/variaveis' },
      { title: 'Tipos', href: '/tipos' },
      { title: 'Operadores', href: '/operadores' },
      { title: 'Condicionais', href: '/condicionais' },
      { title: 'Laços', href: '/lacos' },
      { title: 'Coleções', href: '/colecoes' },
      { title: 'Textos', href: '/textos' },
      { title: 'Ações', href: '/acoes' },
      { title: 'Blueprints', href: '/blueprints' },
      { title: 'Tratamento de erros', href: '/erros' },
      { title: 'Pipelines', href: '/pipelines' },
    ],
  },
  {
    title: 'Fundamentos',
    items: [
      { title: 'Anotações de tipo', href: '/fundamentos/anotacoes-de-tipo' },
      { title: 'Records', href: '/fundamentos/records' },
      { title: 'Enums', href: '/fundamentos/enums' },
      { title: 'Pattern matching', href: '/fundamentos/pattern-matching' },
      { title: 'Desestruturação', href: '/fundamentos/desestruturacao' },
      { title: 'Spread e rest', href: '/fundamentos/spread' },
      { title: 'Compreensões', href: '/fundamentos/compreensoes' },
      { title: 'Interpolação', href: '/fundamentos/interpolacao' },
      { title: 'Generators', href: '/fundamentos/generators' },
      { title: 'Closures e lambdas', href: '/fundamentos/closures' },
      { title: 'Decoradores', href: '/fundamentos/decoradores' },
      { title: 'Traits', href: '/fundamentos/traits' },
      { title: 'Escopo', href: '/fundamentos/escopo' },
      { title: 'Módulos', href: '/fundamentos/modulos' },
    ],
  },
  {
    title: 'Técnicas',
    items: [
      { title: 'Análise estática', href: '/tecnicas/analise-estatica' },
      { title: 'Testes', href: '/tecnicas/testes' },
      { title: 'Formatação', href: '/tecnicas/formatacao' },
      { title: 'Lint', href: '/tecnicas/lint' },
      { title: 'Documentação', href: '/tecnicas/documentacao' },
      { title: 'Estrutura de projeto', href: '/tecnicas/projeto' },
      { title: 'Concorrência', href: '/tecnicas/concorrencia' },
      { title: 'Streams', href: '/tecnicas/streams' },
      { title: 'Serialização', href: '/tecnicas/serializacao' },
      { title: 'Arquivos', href: '/tecnicas/arquivos' },
      { title: 'Banco de dados', href: '/tecnicas/banco-de-dados' },
      { title: 'Servidor HTTP', href: '/tecnicas/http' },
      { title: 'Logging', href: '/tecnicas/logging' },
      { title: 'Datas e horas', href: '/tecnicas/datas' },
      { title: 'Processos', href: '/tecnicas/processos' },
      { title: 'Criptografia', href: '/tecnicas/criptografia' },
    ],
  },
  {
    title: 'Biblioteca Arcane',
    items: [
      { title: 'Visão geral', href: '/biblioteca' },
      { title: 'Arcane.Math', href: '/biblioteca/math' },
      { title: 'Arcane.Text', href: '/biblioteca/text' },
      { title: 'Arcane.Analytics', href: '/biblioteca/analytics' },
      { title: 'Arcane.Functional', href: '/biblioteca/functional' },
      { title: 'Arcane.Time', href: '/biblioteca/time' },
      { title: 'Arcane.Async', href: '/biblioteca/async' },
      { title: 'Arcane.Database', href: '/biblioteca/database' },
      { title: 'Arcane.Crypto', href: '/biblioteca/crypto' },
      { title: 'Arcane.OS', href: '/biblioteca/os' },
      { title: 'Arcane.Collections', href: '/biblioteca/collections' },
      { title: 'Arcane.Test', href: '/biblioteca/test' },
      { title: 'Arcane.Regex', href: '/biblioteca/regex' },
      { title: 'Arcane.IO', href: '/biblioteca/io' },
      { title: 'Arcane.Serialization', href: '/biblioteca/serialization' },
      { title: 'Arcane.Http', href: '/biblioteca/http' },
      { title: 'Arcane.Process', href: '/biblioteca/process' },
      { title: 'Arcane.Logging', href: '/biblioteca/logging' },
      { title: 'Arcane.Data', href: '/biblioteca/data' },
      { title: 'Arcane.Web', href: '/biblioteca/web' },
      { title: 'Arcane.Cortex', href: '/biblioteca/cortex' },
    ],
  },
  {
    title: 'CLI',
    items: [
      { title: 'Visão geral', href: '/cli' },
      { title: 'dataforge run', href: '/cli/run' },
      { title: 'dataforge check', href: '/cli/check' },
      { title: 'dataforge test', href: '/cli/test' },
      { title: 'dataforge fmt', href: '/cli/fmt' },
      { title: 'dataforge lint', href: '/cli/lint' },
      { title: 'dataforge doc', href: '/cli/doc' },
      { title: 'dataforge init', href: '/cli/init' },
      { title: 'dataforge repl', href: '/cli/repl' },
      { title: 'forge.toml', href: '/cli/forge-toml' },
    ],
  },
  {
    title: 'Exercícios',
    badge: '180',
    items: [
      { title: 'Visão geral', href: '/exercicios' },
      { title: '01 · Fundamentos', href: '/exercicios/01-fundamentos' },
      { title: '02 · Controle de fluxo', href: '/exercicios/02-controle-fluxo' },
      { title: '03 · Coleções', href: '/exercicios/03-colecoes' },
      { title: '04 · Textos', href: '/exercicios/04-strings' },
      { title: '05 · Ações', href: '/exercicios/05-acoes' },
      { title: '06 · Blueprints', href: '/exercicios/06-blueprints' },
      { title: '07 · Erros', href: '/exercicios/07-erros' },
      { title: '08 · Pipelines', href: '/exercicios/08-pipelines' },
      { title: '09 · Módulos', href: '/exercicios/09-modulos' },
      { title: '10 · Avançado', href: '/exercicios/10-avancado' },
      { title: '11 · Tipos e checagem', href: '/exercicios/11-tipos-e-checagem' },
      { title: '12 · Records e enums', href: '/exercicios/12-records-e-enums' },
      { title: '13 · Desestruturação', href: '/exercicios/13-desestruturacao' },
      { title: '14 · Pattern matching', href: '/exercicios/14-pattern-matching' },
      { title: '15 · Streams', href: '/exercicios/15-streams-e-generators' },
      { title: '16 · Módulos e projetos', href: '/exercicios/16-modulos-e-projetos' },
      { title: '17 · Tempo e sistema', href: '/exercicios/17-tempo-e-sistema' },
      { title: '18 · Persistência', href: '/exercicios/18-dados-e-persistencia' },
      { title: '19 · Concorrência', href: '/exercicios/19-concorrencia' },
      { title: '20 · Projetos finais', href: '/exercicios/20-projetos-finais' },
    ],
  },
  {
    title: 'Referência',
    items: [
      { title: 'Gramática (EBNF)', href: '/referencia/gramatica' },
      { title: 'Palavras reservadas', href: '/referencia/palavras-reservadas' },
      { title: 'Operadores', href: '/referencia/operadores' },
      { title: 'Precedência', href: '/referencia/precedencia' },
      { title: 'Sistema de tipos', href: '/referencia/tipos' },
      { title: 'Hierarquia de erros', href: '/referencia/erros' },
      { title: 'Funções embutidas', href: '/referencia/embutidas' },
      { title: 'Arquitetura do runtime', href: '/referencia/arquitetura' },
    ],
  },
  {
    title: 'Receitas',
    items: [
      { title: 'Ferramenta de linha de comando', href: '/receitas/cli' },
      { title: 'API REST', href: '/receitas/api-rest' },
      { title: 'Pipeline ETL', href: '/receitas/etl' },
      { title: 'Análise de dados', href: '/receitas/analise-de-dados' },
      { title: 'Interpretador de expressões', href: '/receitas/interpretador' },
      { title: 'Validadores brasileiros', href: '/receitas/validadores' },
      { title: 'Fila de trabalho', href: '/receitas/fila-de-trabalho' },
      { title: 'Máquina de estados', href: '/receitas/maquina-de-estados' },
      { title: 'Processamento de CSV', href: '/receitas/csv' },
      { title: 'Sistema de inventário', href: '/receitas/inventario' },
    ],
  },
  {
    title: 'FAQ',
    items: [
      { title: 'Perguntas frequentes', href: '/faq' },
      { title: 'Erros comuns', href: '/faq/erros-comuns' },
      { title: 'Desempenho', href: '/faq/desempenho' },
      { title: 'Comparação com Python', href: '/faq/python' },
      { title: 'Comparação com JavaScript', href: '/faq/javascript' },
      { title: 'Migração 3.x → 4.0', href: '/faq/migracao' },
    ],
  },
  {
    title: 'Roadmap',
    standalone: true,
    items: [{ title: 'Roadmap', href: '/roadmap' }],
  },
  {
    title: 'Contribuir',
    standalone: true,
    items: [{ title: 'Contribuir', href: '/contribuir' }],
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
