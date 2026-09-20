// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Referência rápida: as dezesseis áreas",
  description: "A tabela final da referência Deep Tech, com o que existe em cada área, onde ele mora no código e a rota que o documenta.",
};

const blocos: Bloco[] = [
  {"p": "A referência fecha com uma tabela de dezesseis áreas. Esta página é essa tabela **resolvida**: para cada área, o que existe, onde mora e onde está documentado."},
  {"p": "Ela também é o índice de saída das 22 partes — se você chegou aqui procurando por um assunto, comece por esta tabela."},
  {"h2": "Linguagem e tipos"},
  {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [["Linguagem", "81 palavras reservadas, 52 contextuais, 225 funções globais", "[referência](/docs/referencia/arquitetura)"], ["Tipos", "alias, união, interseção, refinamento (`where`), opaco, genérico com limite", "[tipos nomeados](/docs/tipos-nomeados)"], ["Coleções tipadas", "`Cluster<T>`, `Vault<K,V>`, `Set<T>`, `Tuple<A,B>` — fronteira e inserção", "[genéricos](/docs/tipos/genericos)"], ["OOP", "`record`, `blueprint`, `enum`, `trait`, contrato, invariante, metaclasse", "[OOP avançada](/docs/oop/contratos)"], ["Falha como valor", "`ok`/`falha`, `Talvez` para onde `void` é ambíguo", "[resultado](/docs/tipos/resultado)"]]}},
  {"h2": "Memória, posse e concorrência"},
  {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [["Posse", "dono exclusivo, empréstimo com escopo, contagem determinística, referência fraca", "[posse](/docs/memoria/posse)"], ["Memória", "arena, mapa fraco, controle e **medição** do coletor", "[coletor](/docs/memoria/coletor)"], ["Concorrência", "mutex, semáforo, barreira, contador atômico, canal bloqueante, STM", "[STM](/docs/concorrencia/stm)"], ["Mais de um núcleo", "`P.map_processos`, pool que sobrevive entre chamadas — **3,45×** em 10 núcleos", "[paralelismo](/docs/tecnicas/processos)"], ["Runtime async", "laço de eventos, escalonador, fibras, `async`/`await`", "[laço de eventos](/docs/runtime/laco)"]]}},
  {"callout": {"tipo": "atencao", "titulo": "A linguagem não sincroniza sozinha", "texto": "Duas threads escrevendo na mesma variável perdem atualizações — medido: 40.425 de 80.000, em silêncio. As peças existem; **usá-las é escolha de quem escreve**, e o `check` avisa sem recusar."}},
  {"h2": "Metaprogramação e FFI"},
  {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [["Metaprogramação", "citar, transformar, gerar, derivar; a árvore como dado", "[macros](/docs/metaprogramacao/macros)"], ["`comptime`", "calcular na leitura, e falhar ali", "[comptime](/docs/metaprogramacao/comptime)"], ["DSL", "combinadores para uma linguagem externa própria", "[DSL](/docs/metaprogramacao/dsl)"], ["FFI", "biblioteca nativa, ponteiro cru, struct conferida contra a ABI, callback", "[FFI para C](/docs/ffi/c)"], ["Ponte Python", "`adopt Python.numpy` — **sem converter nada**", "[ponte](/docs/tecnicas/ponte)"], ["ABI", "a superfície como contrato, 11 regras, o bump que a mudança exige", "[superfície](/docs/abi/superficie)"]]}},
  {"h2": "Compilador, backend e hardware"},
  {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [["Compilador", "lexer, parser, AST, HIR, MIR, LIR, dataflow", "[percurso](/docs/ecossistema/percurso)"], ["Backend", "SSA com φ, SCCP, dobra de constante, ramo morto, fechamentos", "[backend](/docs/compilador/backend)"], ["Hardware", "o que se pode observar de dentro do CPython, e o que **não**", "[hardware](/docs/hardware/mapa)"], ["Build", "`forge.toml`, Dockerfile, CI, k8s, Helm, SBOM, `doctor`", "[DevOps](/docs/devops)"]]}},
  {"callout": {"tipo": "nota", "titulo": "PGO, LTO e cross-compilation", "texto": "As três pressupõem um compilador que emite objeto. Não havendo backend nativo, elas **não se aplicam** — e a página de hardware diz isso com todas as letras, em vez de deixar a linha em branco."}},
  {"h2": "Observabilidade e ecossistema"},
  {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [["Performance", "percentis, cauda, flame graph em SVG, pausas do coletor, Mann-Whitney", "[perfil](/docs/observabilidade/perfil)"], ["Complexidade", "`big-o` **lê** a árvore; `bench` **mede** a curva", "[complexidade](/docs/big-o/analisar)"], ["Tooling", "LSP, depurador, DAP, formatador, linter, testes com cobertura, doc", "[ferramentas](/docs/cli)"], ["Web", "rodar em WASM pelo Pyodide; compilar para WASM **não existe**", "[WASM](/docs/alvos/wasm)"], ["Alvos", "6 ambientes descritos, com o motivo de cada ausência", "[portabilidade](/docs/alvos/portabilidade)"], ["Partida", "7 fases de inicialização, TLS, pilha, capacidade", "[partida](/docs/partida/inicio)"], ["Ecossistema", "41 componentes, conferidos contra o disco", "[componentes](/docs/ecossistema/componentes)"], ["Design", "10 princípios medidos, 9 tensões", "[princípios](/docs/ecossistema/principios)"]]}},
  {"h2": "Onde começar, por objetivo"},
  {"cards": [{"href": "/docs/ecossistema/ausencias", "title": "O que não existe", "meta": "5 componentes", "desc": "A página mais útil para decidir se a linguagem serve ao seu caso."}, {"href": "/docs/ecossistema/tensoes", "title": "As tensões", "meta": "9 decisões", "desc": "Onde dois princípios se contradizem, e qual venceu — com o custo."}, {"href": "/docs/ecossistema/percurso", "title": "Onde o tempo vai", "meta": "10 fases", "desc": "O percurso de um arquivo, medido fase por fase."}, {"href": "/docs/ecossistema/mapa", "title": "Partes 20, 21 e 22", "meta": "o mapa", "desc": "Item por item: o que virou código, o que virou página, o que não existe."}]},
];

const headings = [{ id: 'linguagem-e-tipos', text: "Linguagem e tipos", level: 2 as const }, { id: 'memoria-posse-e-concorrencia', text: "Memória, posse e concorrência", level: 2 as const }, { id: 'metaprogramacao-e-ffi', text: "Metaprogramação e FFI", level: 2 as const }, { id: 'compilador-backend-e-hardware', text: "Compilador, backend e hardware", level: 2 as const }, { id: 'observabilidade-e-ecossistema', text: "Observabilidade e ecossistema", level: 2 as const }, { id: 'onde-comecar-por-objetivo', text: "Onde começar, por objetivo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Referência rápida: as dezesseis áreas"}
      description={"A tabela final da referência Deep Tech, com o que existe em cada área, onde ele mora no código e a rota que o documenta."}
      href={"/docs/ecossistema/referencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
