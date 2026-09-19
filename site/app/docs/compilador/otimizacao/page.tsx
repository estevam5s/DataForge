// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_backend.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O pipeline de otimização, medido",
  description: "Os três passes que existem, o que cada um tira — e o número honesto: 1,33× numa carga feita para eles, 1,01× em código real.",
};

const blocos: Bloco[] = [
  {"p": "Uma referência de linguagem compilada descreve o pipeline do LLVM: inlining, vetorização, análise de alias, otimização de programa inteiro. **Nada disso existe aqui**, e escrever uma função chamada `vetorizar` que não vetoriza seria pior que não ter nenhuma."},
  {"p": "O pipeline desta linguagem é o [compilador de fechamentos](/docs/compilador/analises): a árvore vira funções Python, uma vez. Acima dele há três passes que tiram trabalho **antes** de o fechamento ser construído."},
  {"table": {"head": ["Passe", "O que faz"], "rows": [["`dobra-de-constante`", "`2 + 3 * 4` vira `14`, na carga e não por volta"], ["`ramo-morto`", "o ramo cuja condição a [propagação condicional](/docs/compilador/ssa) prova falsa sai da árvore, com o corpo"], ["`inalcancavel`", "o que vem depois de um `yield`, `halt` ou `trigger` sai do corpo"]]}},
  { code: `adopt Arcane.Compilador as K

// duas dobras: '3 * 4' vira 12, e depois '2 + 12' vira 14
assert K.otimizar("x := 2 + 3 * 4\\n")["dobra-de-constante"] is 2

// o ramo provado falso sai inteiro
fonte := "x := 1\\ngiven x bigger 5:\\n    out 1\\notherwise:\\n    out 2\\n"
assert K.otimizar(fonte)["ramo-morto"] bigger 0

// e os passes estao nomeados, com o que cada um faz
assert len(keys(K.passes())) is 3
assert "na carga" in K.passes()["dobra-de-constante"]`, lang: 'df' },
  {"h2": "O número"},
  {"p": "Esta é a parte que interessa, e ela é **desconfortável**. A escolha do que compilar não foi intuição: saiu do [inventário do LIR](/docs/compilador/analises), que conta, por classe de nó, o que recua para o interpretador de árvore — e separa os recuos **dentro de laço**."},
  { code: `no                           recuos   em laco
Assignment                      229        92     ← v["k"] := x
MorphOperation                   59        59
SkipStatement                    48        46
MembershipOp                    277        23     ← x in xs
TernaryExpression                85        23
CoalesceOp                       90        19     ← a ?? b
UnaryOp                         116        18
TypeofExpression                123        12
SliceAccess                      44         7`, lang: 'text', title: `O inventário, sobre 388 arquivos do repositório` },
  {"p": "Dez desses nós ganharam construtor no compilador de fechamentos. E o resultado medido:"},
  {"table": {"head": ["Carga", "Antes", "Depois", "Ganho"], "rows": [["feita **dos nós que o inventário aponta**", "507 ms", "382 ms", "**1,33×**"], ["59 exercícios **reais** do repositório", "1150 ms", "1143 ms", "**1,01× — nada**"]]}},
  {"callout": {"tipo": "atencao", "titulo": "E o motivo é instrutivo", "texto": "O que recua é dominado por nós que rodam **uma vez** (declaração, `adopt`, `assert` de topo). Os que rodam dentro de laço são poucos por volta, e o trabalho da volta **já estava compilado**: leitura de nome, conta binária, chamada, leitura por índice. Otimizar o que sobra é otimizar 3% de 3%."}},
  {"p": "Por isso os três passes ficam **desligados por padrão**. Eles existem para serem medidos, para `dataforge ir --fase=otimizado` mostrar o que dá para tirar, e porque a conta honesta é a informação — não a promessa de velocidade."},
  {"h2": "Duas regras ao mexer nos passes"},
  {"p": "**A prova é a saída.** Um passe errado não levanta erro: ele muda o resultado. Os testes rodam exercícios do repositório nas duas formas e comparam caractere por caractere — a mesma trava do [HIR](/docs/compilador/hir), pelo mesmo motivo."},
  {"p": "**Nada que possa falhar é dobrado.** É a regra que mais recusa:"},
  { code: `// '1 / 0' dobrado moveria o erro para a CARGA, longe da linha
// que o causa. Sem dobrar, ele estoura onde esta escrito:
monitor:
    x := 1 / 0
handle Error as e:
    assert e.type is "DivisionByZeroError"
    assert e.line is 4`, lang: 'df' },
  {"table": {"head": ["Não dobra", "Porque"], "rows": [["`1 / 0`, `5 % 0`", "moveria o erro para a carga"], ["`\"a\" + 1`", "mudaria a mensagem de erro"], ["`2 ** 1000000`", "meio milhão de dígitos montados no carregamento"], ["`a + b` com nome", "o valor pode não ser o que parece; quem prova isso é o SSA, não a dobra"], ["`yes + 1`", "booleano somando é um acidente, não uma conta"]]}},
];

const headings = [{ id: 'o-numero', text: "O número", level: 2 as const }, { id: 'duas-regras-ao-mexer-nos-passes', text: "Duas regras ao mexer nos passes", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O pipeline de otimização, medido"}
      description={"Os três passes que existem, o que cada um tira — e o número honesto: 1,33× numa carga feita para eles, 1,01× em código real."}
      href={"/docs/compilador/otimizacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
