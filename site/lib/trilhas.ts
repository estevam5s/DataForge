/**
 * As trilhas — os caminhos que a linguagem oferece.
 *
 * Cada trilha é uma sequência de passos, e cada passo aponta para uma
 * página que já existe. **Os `href` são conferidos**: `tests/
 * test_roadmap.py` cobra que todo um deles esteja em `site/lib/nav.ts`
 * ou seja uma rota de topo do site. Uma trilha que aponta para uma
 * página removida é pior que nenhuma trilha — ela promete um caminho e
 * entrega um 404 no meio.
 *
 * O que NÃO está aqui, de propósito: a lista de módulos, o número de
 * exercícios e o estado de cada componente da arquitetura. Isso sai de
 * `roadmap-gerado.json`, que vem do próprio código. Aqui mora só o que
 * exige julgamento — a ordem em que vale a pena aprender as coisas.
 */

export type Passo = {
  titulo: string;
  href: string;
  /** O que a pessoa sabe fazer depois deste passo, e não o que ele contém. */
  ganho: string;
  /** A página dos exercícios que exercitam isto. Conferida como os `href`. */
  exercicios?: string;
};

export type Trilha = {
  id: string;
  titulo: string;
  /** Uma frase: para quem é, e o que a pessoa consegue fazer no fim. */
  resumo: string;
  nivel: 'início' | 'intermediário' | 'avançado';
  duracao: string;
  /** Ids das trilhas que convém ter feito antes. */
  antes: string[];
  passos: Passo[];
};

export const TRILHAS: Trilha[] = [
  {
    id: 'fundamentos',
    titulo: 'Os fundamentos',
    resumo:
      'Sair do zero e escrever um programa que lê, decide, repete e falha bem. É o único caminho que todos os outros pressupõem.',
    nivel: 'início',
    duracao: '4 a 6 horas',
    antes: [],
    passos: [
      {
        titulo: 'Instalar e rodar o primeiro arquivo',
        href: '/docs/primeiros-passos',
        ganho: 'um `.df` que roda na sua máquina, e o REPL para experimentar',
      },
      {
        titulo: 'Variáveis, tipos e interpolação',
        href: '/docs/variaveis',
        ganho: '`:=` contra `steady`, o tipo opcional, e `$"{…}"`',
        exercicios: '/docs/exercicios/01-fundamentos',
      },
      {
        titulo: 'Decidir e repetir',
        href: '/docs/condicionais',
        ganho: '`given`/`orif`/`otherwise`, `cycle`, `persist` — e por que `cycle` tem escopo próprio',
        exercicios: '/docs/exercicios/02-controle-fluxo',
      },
      {
        titulo: 'Coleções, fatias e compreensões',
        href: '/docs/colecoes',
        ganho: 'cluster e vault, `[expr cycle x in xs given cond]`, spread e desestruturação',
        exercicios: '/docs/exercicios/03-colecoes',
      },
      {
        titulo: 'Ações',
        href: '/docs/acoes',
        ganho: '`action`/`yield`, parâmetros nomeados, `lambda`, e a diferença para `emit`',
        exercicios: '/docs/exercicios/05-acoes',
      },
      {
        titulo: 'Erros que dizem o que fazer',
        href: '/docs/erros',
        ganho: '`monitor`/`handle`/`ensure`, `trigger`, `defer` — e as 215 classes do catálogo',
        exercicios: '/docs/exercicios/54-erros',
      },
      {
        titulo: 'As ferramentas de linha de comando',
        href: '/docs/cli',
        ganho: '`check`, `fmt`, `lint`, `test` — o analisador acusa antes de rodar',
      },
    ],
  },

  {
    id: 'dados',
    titulo: 'Dados, do CSV ao relatório',
    resumo:
      'Ler, limpar, agrupar e resumir. Termina com um painel no navegador que outra pessoa consegue abrir.',
    nivel: 'intermediário',
    duracao: '6 a 8 horas',
    antes: ['fundamentos'],
    passos: [
      {
        titulo: 'Pipeline: sift, morph, distill',
        href: '/docs/pipelines',
        ganho: 'transformar uma coleção sem laço nem variável temporária',
        exercicios: '/docs/exercicios/08-pipelines',
      },
      {
        titulo: 'O Quadro e os seis verbos',
        href: '/docs/dados/quadro',
        ganho: '`onde`, `pegar`, `sem`, `ordenar`, `agrupar`, `resumir` — e a lógica de três valores',
        exercicios: '/docs/exercicios/36-quadro-e-dados',
      },
      {
        titulo: 'Arquivos e formatos',
        href: '/docs/biblioteca/io',
        ganho: 'CSV, JSON, Excel e arquivos binários, sem dependência externa',
      },
      {
        titulo: 'Banco de dados',
        href: '/docs/biblioteca/database',
        ganho: 'transação que desfaz de verdade, `upsert`, busca textual e paginação',
        exercicios: '/docs/exercicios/24-banco-de-dados',
      },
      {
        titulo: 'Vitrine — o painel',
        href: '/docs/vitrine',
        ganho: 'um app de dados com gráficos, estado de sessão e cache, num arquivo',
        exercicios: '/docs/exercicios/57-vitrine-painel',
      },
    ],
  },

  {
    id: 'web',
    titulo: 'Web com o Kiln',
    resumo:
      'Da primeira rota a um servidor com sessão, upload, WebSocket e as defesas ligadas.',
    nivel: 'intermediário',
    duracao: '6 a 10 horas',
    antes: ['fundamentos'],
    passos: [
      {
        titulo: 'A primeira rota',
        href: '/docs/kiln',
        ganho: '`server`, `route`, `respond`, `render` — e por que `ignite` é separado',
        exercicios: '/docs/exercicios/22-web-kiln',
      },
      {
        titulo: 'Templates e arquivos estáticos',
        href: '/docs/kiln/paginas',
        ganho: 'HTML com dados, escape automático, `assets` e `views`',
      },
      {
        titulo: 'Upload, SSE e WebSocket',
        href: '/docs/kiln/tempo-real',
        ganho: 'multipart, fluxo de eventos e o RFC 6455 falado à mão',
      },
      {
        titulo: 'Segurança da aplicação',
        href: '/docs/biblioteca/seguranca',
        ganho: 'escape por destino, CSRF, SSRF, travessia de caminho, TOTP e token com prazo',
      },
      {
        titulo: 'Levar ao ar',
        href: '/docs/devops',
        ganho: 'Dockerfile, compose, CI e manifestos — gerados, não escondidos',
      },
    ],
  },

  {
    id: 'objetos',
    titulo: 'Objetos e domínio',
    resumo:
      'Modelar um sistema de verdade: os objetos, os contratos que a linguagem cobra, e as distinções do DDD.',
    nivel: 'intermediário',
    duracao: '8 a 12 horas',
    antes: ['fundamentos'],
    passos: [
      {
        titulo: 'Record, blueprint, enum e trait',
        href: '/docs/oop',
        ganho: 'o que é imutável, o que herda, e quando cada um serve',
        exercicios: '/docs/exercicios/06-blueprints',
      },
      {
        titulo: 'Pattern matching',
        href: '/docs/fundamentos/pattern-matching',
        ganho: '`match`/`point`/`when`, padrão aninhado, e os cinco avisos de exaustividade',
        exercicios: '/docs/exercicios/14-pattern-matching',
      },
      {
        titulo: 'Contratos e invariantes',
        href: '/docs/oop/contratos',
        ganho: '`requires`, `promises`, `invariant` — cobrados, e não comentados',
      },
      {
        titulo: 'Métodos mágicos',
        href: '/docs/oop/magicos',
        ganho: 'texto, igualdade, ordem, coleção — e os três que a linguagem não delega',
        exercicios: '/docs/exercicios/55-oop-magicos',
      },
      {
        titulo: 'DDD: valor, entidade, agregado',
        href: '/docs/dominio',
        ganho: 'a invariante cobrada na saída do comando, e o evento publicado só no commit',
        exercicios: '/docs/exercicios/50-dominio',
      },
      {
        titulo: 'Tipos nomeados',
        href: '/docs/tipos',
        ganho: 'alias, união, interseção, refinamento e o tipo opaco',
        exercicios: '/docs/exercicios/38-tipos',
      },
    ],
  },

  {
    id: 'concorrencia',
    titulo: 'Concorrência e mais de um núcleo',
    resumo:
      'O que o GIL permite, o que ele não permite, e as três respostas diferentes que a linguagem tem para isso.',
    nivel: 'avançado',
    duracao: '6 a 10 horas',
    antes: ['fundamentos', 'objetos'],
    passos: [
      {
        titulo: 'thread, parallel e async',
        href: '/docs/tecnicas/concorrencia',
        ganho: 'concorrência de entrada e saída — e o aviso `escrita-concorrente` do `check`',
        exercicios: '/docs/exercicios/19-concorrencia',
      },
      {
        titulo: 'Sincronizar à mão',
        href: '/docs/biblioteca/concurrent',
        ganho: 'mutex, semáforo, barreira, contador atômico e canal — nada é automático',
      },
      {
        titulo: 'Processos: o único caminho para mais de um núcleo',
        href: '/docs/tecnicas/processos',
        ganho: '`map_processos` e o pool, com a medida: 3,45× em 10 núcleos',
        exercicios: '/docs/exercicios/35-paralelismo',
      },
      {
        titulo: 'O laço de eventos e as fibras',
        href: '/docs/biblioteca/laco',
        ganho: '1000 conexões numa thread — e por que a fibra não é green thread',
      },
      {
        titulo: 'Memória transacional',
        href: '/docs/biblioteca/stm',
        ganho: 'escritas que acontecem juntas, e a transação irrevogável que garante progresso',
      },
    ],
  },

  {
    id: 'seguranca',
    titulo: 'Segurança',
    resumo:
      'O que se faz com a entrada que veio de fora — e o que se faz com o segredo que já foi escrito num arquivo.',
    nivel: 'intermediário',
    duracao: '4 a 6 horas',
    antes: ['fundamentos'],
    passos: [
      {
        titulo: 'As primitivas',
        href: '/docs/biblioteca/crypto',
        ganho: 'resumo, HMAC, senha derivada, aleatório de verdade, ChaCha20-Poly1305 e JWT',
      },
      {
        titulo: 'Entrada hostil e escape por destino',
        href: '/docs/biblioteca/seguranca',
        ganho: 'HTML, shell, CSV, cabeçalho, log — e SSRF, travessia, redirecionamento aberto',
      },
      {
        titulo: 'Segundo fator e token com prazo',
        href: '/docs/biblioteca/seguranca',
        ganho: 'TOTP pelos vetores do RFC, e o propósito que impede um token servir ao outro',
      },
      {
        titulo: 'Varrer o projeto',
        href: '/docs/cli',
        ganho: '`dataforge seguranca .` acha segredo por formato, inclusive fora dos `.df`',
      },
      {
        titulo: 'A fronteira de autoridade',
        href: '/docs/biblioteca/capacidade',
        ganho: 'recusar o `adopt` de um módulo fora da lista — e o que isso NÃO é',
      },
    ],
  },

  {
    id: 'interno',
    titulo: 'Por dentro da linguagem',
    resumo:
      'As dez fases de um arquivo, as três representações do meio, e as ferramentas que mostram cada uma. Para quem quer mexer no interpretador.',
    nivel: 'avançado',
    duracao: '10 a 20 horas',
    antes: ['fundamentos', 'objetos'],
    passos: [
      {
        titulo: 'A arquitetura',
        href: '/docs/referencia/arquitetura',
        ganho: 'lexer, parser, AST, analisador, HIR, MIR, SSA, LIR — e onde cada um mora',
      },
      {
        titulo: 'O analisador estático',
        href: '/docs/tecnicas/analise-estatica',
        ganho: 'o que ele prova de um literal, e o que o faz calar — que custou mais',
      },
      {
        titulo: 'As representações do meio',
        href: '/docs/biblioteca/compilador',
        ganho: '`dataforge ir` nas seis fases, e a lista do que NÃO é açúcar',
      },
      {
        titulo: 'Medir antes de otimizar',
        href: '/docs/biblioteca/perfil',
        ganho: 'percentis, Mann-Whitney, e o teste que compara uma ação com ela mesma',
      },
      {
        titulo: 'O inventário conferido',
        href: '/docs/biblioteca/ecossistema',
        ganho: 'os 41 componentes, e a lista do que não existe — cobrada contra o disco',
      },
      {
        titulo: 'Estender a linguagem',
        href: '/docs/referencia/gramatica',
        ganho: 'os cinco lugares por onde passa todo recurso novo, e a gramática EBNF',
      },
    ],
  },
];
