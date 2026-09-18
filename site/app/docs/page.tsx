import Link from 'next/link';
import type { Metadata } from 'next';
import { CodeBlock } from '@/components/CodeBlock';
import { Callout, Card, CardGrid, DocPage, H2, H3, Table } from '@/components/Doc';

const DESCRICAO =
  'A documentação do DataForge: mais de 190 páginas, 255 exercícios que ' +
  'verificam o próprio resultado com assert, e cada trecho de código ' +
  'compilado a cada mudança. Linguagem, biblioteca, frameworks e ferramentas.';

export const metadata: Metadata = {
  title: 'Introdução',
  description: DESCRICAO,
  // A '/docs' é a segunda página mais compartilhada, e merece o card
  // próprio: quem manda o link da documentação está mandando outra
  // coisa que não a página inicial.
  openGraph: {
    type: 'article',
    locale: 'pt_BR',
    url: 'https://dataforge-lang.vercel.app/docs',
    siteName: 'DataForge',
    title: 'Documentação do DataForge',
    description: DESCRICAO,
    images: [
      {
        url: '/og-docs.png',
        width: 1200,
        height: 630,
        type: 'image/png',
        alt: 'Documentação do DataForge',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Documentação do DataForge',
    description: DESCRICAO,
    images: ['/og-docs.png'],
  },
  alternates: { canonical: 'https://dataforge-lang.vercel.app/docs' },
};

const headings = [
  { id: 'o-que-e', text: 'O que é', level: 2 as const },
  { id: 'um-exemplo-completo', text: 'Um exemplo completo', level: 2 as const },
  { id: 'filosofia', text: 'Filosofia', level: 2 as const },
  { id: 'de-onde-voce-vem', text: 'De onde você vem', level: 2 as const },
  { id: 'instalacao', text: 'Instalação', level: 2 as const },
  { id: 'o-que-tem-hoje', text: 'O que tem hoje', level: 2 as const },
  { id: 'o-que-ainda-nao-tem', text: 'O que ainda não tem', level: 2 as const },
  { id: 'por-onde-comecar', text: 'Por onde começar', level: 2 as const },
  { id: 'levar-ao-ar', text: 'Levar ao ar', level: 2 as const },
];

const exemplo = `adopt Arcane.Collections as Col

record Produto:
    nome: String
    preco: Number
    estoque: Integer

enum Situacao:
    EmFalta
    Critico
    Normal

action situacao_de(p: Produto) -> Situacao:
    match p:
        point Produto(estoque := 0):
            yield Situacao.EmFalta
        point Produto(estoque := e) when e smaller 5:
            yield Situacao.Critico
        default:
            yield Situacao.Normal

estoque := [
    Produto("Mouse", 80.0, 15),
    Produto("Teclado", 200.0, 3),
    Produto("Monitor", 1200.0, 0)
]

patrimonio := estoque
    >> morph p: p.preco * p.estoque
    >> distill acc, v: acc + v 0

cycle p in Col.sort_by_field(estoque, "preco", yes):
    out $"{p.nome.pad_end(10)} {situacao_de(p).name.pad_end(10)} R$ {p.preco * p.estoque}"

out $"\\npatrimônio: R$ {patrimonio}"
out $"repor: {[p.nome cycle p in estoque given situacao_de(p) isnt Situacao.Normal]}"`;

const saida = `Monitor    EmFalta    R$ 0.0
Teclado    Critico    R$ 600.0
Mouse      Normal     R$ 1200.0

patrimônio: R$ 1800.0
repor: [Teclado, Monitor]`;

export default function Home() {
  return (
    <DocPage
      title="Introdução"
      description="DataForge é uma linguagem de programação interpretada, de propósito geral, implementada em Python 3.10+ sem dependências externas no runtime."
      href="/docs"
      headings={headings}
    >
      <H2>O que é</H2>

      <p>
        DataForge não é um DSL nem um transpilador. Tem lexer, parser recursivo
        descendente, AST tipada, analisador estático e interpretador de árvore
        próprios — cerca de 19 mil linhas de Python, sem uma única dependência
        externa em tempo de execução.
      </p>

      <p>
        O que a distingue não é a lista de recursos, e sim o <strong>vocabulário</strong>.
        Onde outras linguagens dizem <code>if</code>, <code>for</code>,{' '}
        <code>class</code> e <code>try</code>, o DataForge diz{' '}
        <code>given</code>, <code>cycle</code>, <code>blueprint</code> e{' '}
        <code>monitor</code>. As palavras foram escolhidas para descrever a{' '}
        <em>intenção</em> de quem escreve, não a mecânica da máquina.
      </p>

      <Table
        head={['', 'Valor']}
        rows={[
          [<>Versão</>, <><code>1.0.0</code></>],
          [<>Extensão</>, <><code>.df</code></>],
          [<>Runtime</>, <>Python 3.10+, zero dependências</>],
          [<>Biblioteca padrão</>, <>56 módulos, 1650 símbolos</>],
          [<>Funções globais</>, <>228, sem <code>adopt</code></>],
          [<>Licença</>, <>MIT</>],
        ]}
      />

      <H2>Um exemplo completo</H2>

      <p>
        Este programa usa <code>record</code>, <code>enum</code>, pattern
        matching com guarda, pipeline, compreensão de lista e interpolação de
        strings — tudo o que a linguagem tem de mais característico, em trinta
        linhas:
      </p>

      <CodeBlock code={exemplo} title="estoque.df" />

      <p>A saída:</p>

      <CodeBlock code={saida} lang="text" title="saída" />

      <H2>Filosofia</H2>

      <H3>Vocabulário que descreve intenção</H3>
      <p>
        <code>monitor</code> / <code>handle</code> / <code>ensure</code> diz
        exatamente o que o bloco faz: monitorar, tratar, garantir. Comparado a{' '}
        <code>try</code> / <code>catch</code> / <code>finally</code>, que
        descreve a mecânica do runtime, o primeiro comunica a intenção do
        programador.
      </p>

      <H3>Erros que ensinam</H3>
      <p>
        Uma mensagem de erro deve dizer <strong>o que fazer</strong>, não apenas
        o que houve. Compare:
      </p>
      <CodeBlock
        lang="text"
        title="antes / depois"
        code={`RuntimeError: Invalid assignment target

'no' is a reserved keyword and cannot be assigned to.
    sugestão: Pick another name.`}
      />

      <H3>Análise otimista</H3>
      <p>
        O analisador estático fica calado quando não consegue{' '}
        <strong>provar</strong> que algo está errado. Um falso alarme é pior que
        um alerta perdido, porque ensina a ignorar as mensagens. Hoje ele reporta{' '}
        <strong>zero erros</strong> em 368 arquivos conhecidamente bons.
      </p>

      <H3>Verificável</H3>
      <p>
        Cada afirmação desta documentação corresponde a código que roda. São{' '}
        <strong>3404 testes</strong>, 255 exercícios que verificam o próprio
        resultado com <code>assert</code>, e 44 programas de exemplo. Os
        trechos desta documentação são compilados a cada mudança — 1449 deles.
      </p>

      <H2>De onde você vem</H2>

      <p>
        Se você já programa, esta tabela é a ponte mais rápida:
      </p>

      <Table
        head={['Conceito', 'Outras linguagens', 'DataForge']}
        rows={[
          [<>atribuição</>, <><code>x = 1</code></>, <><code>x := 1</code></>],
          [<>constante</>, <><code>const</code></>, <><code>steady</code></>],
          [<>imprimir</>, <><code>print</code></>, <><code>out</code></>],
          [<>interpolação</>, <><code>f&quot;&#123;x&#125;&quot;</code></>, <><code>$&quot;&#123;x&#125;&quot;</code></>],
          [<>condicional</>, <><code>if</code>/<code>elif</code>/<code>else</code></>, <><code>given</code>/<code>orif</code>/<code>otherwise</code></>],
          [<>seleção</>, <><code>switch</code>/<code>match</code></>, <><code>match</code>/<code>point</code>/<code>when</code></>],
          [<>laço</>, <><code>for</code>/<code>while</code></>, <><code>cycle</code>/<code>persist</code></>],
          [<>função</>, <><code>def</code>/<code>return</code></>, <><code>action</code>/<code>yield</code></>],
          [<>gerador</>, <><code>yield</code></>, <><code>stream action</code>/<code>emit</code></>],
          [<>classe</>, <><code>class</code>/<code>new</code></>, <><code>blueprint</code>/<code>spawn</code></>],
          [<>dados imutáveis</>, <><code>@dataclass(frozen)</code></>, <><code>record</code></>],
          [<>interface</>, <><code>interface</code></>, <><code>trait</code></>],
          [<>módulos</>, <><code>import</code>/<code>export</code></>, <><code>adopt</code>/<code>relay</code></>],
          [<>erros</>, <><code>try</code>/<code>catch</code>/<code>finally</code></>, <><code>monitor</code>/<code>handle</code>/<code>ensure</code></>],
          [<>booleanos</>, <><code>true</code>/<code>false</code>/<code>null</code></>, <><code>yes</code>/<code>no</code>/<code>void</code></>],
          [<>coleções</>, <><code>filter</code>/<code>map</code>/<code>reduce</code></>, <><code>&gt;&gt; sift</code>/<code>morph</code>/<code>distill</code></>],
          [<>divisão inteira</>, <><code>//</code></>, <><code>~/</code></>],
        ]}
      />

      <Callout tipo="atencao" titulo="A pegadinha do //">
        <p>
          Em DataForge, <code>//</code> é <strong>comentário</strong> por padrão —
          como em toda linguagem da família C. Ele só vira divisão inteira quando
          seguido de dígito, <code>(</code> ou uma chamada. Para divisão inteira
          sem ambiguidade existe <code>~/</code>, e é o que a documentação usa.
        </p>
      </Callout>

      <H2>Instalação</H2>

      <CodeBlock
        lang="bash"
        code={`git clone https://github.com/estevam5s/DataForge.git
cd DataForge

python3 -m venv .venv && source .venv/bin/activate
pip install .

dataforge version`}
      />

      <p>
        Depois disso, <Link href="/docs/primeiros-passos">seu primeiro programa</Link>{' '}
        leva mais um minuto. O guia completo, com Windows e solução de
        problemas, está em <Link href="/docs/instalacao">Instalação</Link>.
      </p>

      <H2>O que tem hoje</H2>

      <Table
        head={['Área', 'Recursos']}
        rows={[
          [<><strong>Tipos</strong></>, <>anotações opcionais verificadas, <code>typeof</code>, <code>cast</code>, análise estática</>],
          [<><strong><Link href="/docs/tipos/visao-geral">Sistema de tipos</Link></strong></>, <><Link href="/docs/tipos-nomeados">alias, união, interseção, refinamento e tipo opaco</Link>; <Link href="/docs/tipos/genericos">generics com limite, em ação, blueprint, record, enum e trait</Link>; tipos indexados (<code>Vetor&lt;3&gt;</code>); <Link href="/docs/tipos/tuplas">tuplas</Link>; <Link href="/docs/tipos/reflexao">reflexão</Link></>],
          [<><strong><Link href="/docs/tipos/resultado">Resultado</Link></strong></>, <>a falha como valor: <code>ok</code>/<code>falha</code> com <code>mapear</code>, <code>entao</code> e <code>todos</code>; <code>Talvez</code> para onde <code>void</code> é ambíguo</>],
          [<><strong>Dados</strong></>, <>records imutáveis, enums, clusters, vaults, compreensões</>],
          [<><strong>Fluxo</strong></>, <><code>given</code>/<code>orif</code>/<code>otherwise</code>, <code>match</code> estrutural, quatro laços</>],
          [<><strong>Ações</strong></>, <>padrões, tipos, closures, lambdas, decoradores, <code>defer</code></>],
          [<><strong>Erros</strong></>, <><code>handle</code> tipado, <code>guard</code>, <code>retry</code>, <code>propagate</code>, stack traces</>],
          [<><strong>Fluxos</strong></>, <>pipelines, <code>stream action</code> com avaliação preguiçosa</>],
          [<><strong>Módulos</strong></>, <><code>adopt</code> seletivo, <code>relay</code>, detecção de ciclos, <code>forge.toml</code></>],
          [<><strong>Ferramentas</strong></>, <>40 comandos: <code>check</code>, <code>test</code>, <code>fmt</code>, <code>lint</code>, <code>big-o</code>, <code>debug</code>, <code>lsp</code>, <code>repl</code></>],
          [<><strong>Editor</strong></>, <><Link href="/docs/tecnicas/lsp">servidor de linguagem</Link>: autocompletar, hover, ir-para-definição, renomear</>],
          [<><strong>Web</strong></>, <><Link href="/docs/kiln">Kiln</Link> — rotas, middleware, CSRF, cache, gzip, idempotência</>],
          [<><strong>Testes</strong></>, <><Link href="/docs/crucible">Crucible</Link> — 59 matchers, fixtures, dublês, benchmark</>],
          [<><strong>Banco</strong></>, <><Link href="/docs/banco-de-dados">Forge</Link> — SQLite, Postgres, MySQL, Redis e Mongo por protocolo próprio</>],
          [<><strong>Dados</strong></>, <><Link href="/docs/tecnicas/parquet">Parquet</Link>, <Link href="/docs/tecnicas/lago">Data Lake</Link>, <Link href="/docs/tecnicas/pipeline">pipelines</Link>, <Link href="/docs/tecnicas/streaming">streaming</Link>, <Link href="/docs/tecnicas/ml">ML</Link></>],
          [<><strong>Pacotes</strong></>, <>semver, lockfile, verificação de integridade, registro estático</>],
        ]}
      />

      <H2>O que ainda não tem</H2>

      <p>
        Ser honesto sobre isto é parte de conhecer a ferramenta:
      </p>

      <ul>
        <li>
          <strong>Desempenho</strong> — é interpretador de árvore escrito em
          Python, e paga duas camadas de interpretação. Medido:{' '}
          <code>fib(28)</code> em 4,8 s contra 0,02 s do CPython. Não é
          bloqueio para script, ETL, CLI ou servidor, onde a rede domina; é
          bloqueio para laço quente. Uma VM de bytecode é o próximo salto.
        </li>
        <li>
          <strong>Variância declarada</strong> —{' '}
          <code>&lt;T extends Number&gt;</code> é cobrado nas duas metades, e{' '}
          <code>Cluster&lt;T&gt;</code> é conferido item a item, mas não há{' '}
          <code>in</code>/<code>out</code> para declarar covariância: uma{' '}
          <code>Cluster&lt;Filha&gt;</code> não é aceita onde se pede{' '}
          <code>Cluster&lt;Mae&gt;</code>.
        </li>
        <li>
          <strong>Exaustividade em padrão aninhado</strong> — o{' '}
          <code>match</code> avisa o que falta em enum, booleano, sequência e
          na família de um <code>abstract blueprint</code>; ele não desce em{' '}
          <code>[Cor.A, x]</code>, e um ramo com guarda nunca conta como
          cobertura.
        </li>
        <li>
          <strong>Prova formal de refinamento</strong> — um{' '}
          <code>where</code> é <em>verificado</em>: o <code>check</code>{' '}
          decide sobre literais, e o resto é conferido na fronteira, em
          execução. Não há prova de que a regra nunca falha, e isso pediria um
          provador, não um analisador.
        </li>
        <li>
          <strong>Memória manual e FFI de ponteiro</strong> — não há{' '}
          <em>ownership</em>, <em>borrow checker</em>, alocador próprio nem{' '}
          ponteiro cru: a coleta é automática. Para mais de um núcleo existe{' '}
          a travessia de processo; para biblioteca nativa, a{' '}
          <Link href="/docs/tecnicas/ponte">ponte para o Python</Link>.
        </li>
        <li>
          <strong>Ecossistema</strong> — o registro tem 20 pacotes, todos deste
          projeto. Uma linguagem fica completa quando outra pessoa publica nela,
          e isso não se resolve com código.
        </li>
      </ul>

      <p>
        O que <em>deixou</em> de faltar desde a última revisão: LSP,{' '}
        <Link href="/docs/editor">depurador no editor (DAP) com watchpoint</Link>,{' '}
        <Link href="/docs/tipos/genericos">generics com limite</Link>,{' '}
        conteúdo de coleção verificado,{' '}
        <Link href="/docs/tipos-nomeados">tipos nomeados</Link>,{' '}
        <Link href="/docs/tipos/tuplas">tuplas</Link>, contrato de trait e o
        gerenciador de pacotes — todos existem hoje. O mapa item por item,
        com o que existe e o que não, está em{' '}
        <Link href="/docs/tipos/mapa">Fundamentos e tipos: o mapa</Link>.
      </p>

      <p>
        O plano completo está no <Link href="/docs/roadmap">Roadmap</Link>.
      </p>

      <H2>Por onde começar</H2>

      <CardGrid>
        <Card href="/docs/primeiros-passos" title="Primeiros passos" meta="5 min">
          Instale, escreva o primeiro programa e conheça a CLI.
        </Card>
        <Card href="/docs/variaveis" title="Visão geral" meta="13 páginas">
          A linguagem do zero, na ordem em que é usada.
        </Card>
        <Card href="/docs/exercicios" title="255 exercícios" meta="38 áreas">
          Cada um se verifica com <code>assert</code>. Vinte e dois módulos têm
          um <code>.md</code> explicativo ao lado de cada exercício.
        </Card>
        <Card href="/docs/biblioteca" title="Biblioteca Arcane" meta="1650 símbolos">
          Estatística, bancos, HTTP, criptografia, Parquet, ML, streaming.
        </Card>
        <Card href="/docs/tipos/visao-geral" title="Sistema de tipos" meta="novo">
          Alias, união, interseção, refinamento e tipo opaco; generics em
          record, enum e trait; tuplas, tipos indexados e reflexão.
        </Card>
        <Card href="/docs/referencia/gramatica" title="Referência formal">
          Gramática EBNF, palavras reservadas, precedência e semântica.
        </Card>
        <Card href="/docs/receitas/cli" title="Receitas">
          Projetos completos: CLI, API REST, ETL, interpretador.
        </Card>
      </CardGrid>

      <H2>Levar ao ar</H2>

      <p>
        A parte que a maioria das documentações de linguagem deixa de
        fora, e que é onde um projeto trava: o que falta para ele subir.
      </p>

      <CardGrid>
        <Card href="/docs/devops" title="DevOps" meta="11 subcomandos">
          <code>Dockerfile</code>, compose, CI, Kubernetes, Helm, Terraform,
          nginx, Prometheus e SBOM — gerados do que o projeto usa. E o{' '}
          <code>doctor</code>, que diz o que falta e o comando que resolve.
        </Card>
        <Card href="/docs/instalacao/docker" title="A imagem oficial">
          Rodar DataForge em container sem instalar nada — e usá-la como
          base da sua.
        </Card>
        <Card href="/docs/seguranca" title="Segurança">
          Cabeçalhos, CSRF, limite de taxa, e o que nunca vai ao
          repositório.
        </Card>
        <Card href="/docs/tecnicas/observar" title="Observabilidade">
          Métrica, traço e linhagem — e o rastro que atravessa a
          fronteira entre serviços.
        </Card>
      </CardGrid>
    </DocPage>
  );
}
