import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Benchmark",
  description: "Medir, comparar implementações, e descobrir a classe de custo que acontece de verdade.",
};

const blocos: Bloco[] = [
  {"p": "A linguagem sabe dizer a complexidade que **lê** no código — é o [`dataforge big-o`](/docs/big-o/analisar). `Arcane.Bench` diz a que **acontece** quando o programa roda. As duas respondem perguntas diferentes, e erram de formas opostas:"},
  {"table": {"head": ["", "Enxerga", "Não enxerga"], "rows": [
    ["análise estática", "a estrutura: laços aninhados, recursão, o custo das embutidas", "quantas voltas cada laço dá de verdade"],
    ["medição", "o tempo com cache, GIL e interpretador dentro", "o que acontece com `n` dez vezes maior"],
  ]}},
  {"p": "Quando as duas concordam, a classe está estabelecida. Quando divergem, **a divergência é o resultado**."},

  {"h2": "Medir uma ação"},
  { code: `adopt Arcane.Bench as B

action pesado(n):
    yield sum([i * i cycle i in range(0, n)])

r := B.medir(pesado, 100000)
out r["ms"], "ms"
out r["por_segundo"], "por segundo"` },
  {"p": "`medir` roda várias vezes e fica com o **menor** tempo, não com a média. Tudo o que interfere — outro processo, o coletor de lixo, o escalonador — só faz o tempo **subir**: a média mede a máquina, o mínimo mede o código."},

  {"h2": "Comparar implementações"},
  {"p": "O caso que mais se usa: duas formas de fazer a mesma coisa, e a pergunta de qual vale a pena."},
  { code: `adopt Arcane.Bench as B
adopt Arcane.Text as T

action com_mais(n):
    s := ""
    cycle i from 1 to n:
        s += "x"
    yield len(s)

action com_construtor(n):
    b := T.construtor()
    cycle i from 1 to n:
        b.add("x")
    yield b.tamanho()

out B.tabela(B.comparar({
    "s += x": com_mais,
    "construtor": com_construtor,
}, argumento := 160000))` },
  { lang: 'text', code: `* construtor    121.5580 ms    1.00x
  s += x        402.2138 ms    3.31x` },
  {"callout": {"tipo": "nota", "titulo": "Elas rodam intercaladas, e não em bloco", "texto": "Rodar uma implementação inteira e depois a outra faz a segunda pegar o cache quente que a primeira deixou — e a **ordem** passa a decidir quem ganha. `comparar` alterna a cada repetição."}},

  {"h2": "Descobrir a classe"},
  {"p": "`classe` mede em tamanhos crescentes e responde qual curva descreve o que aconteceu. A conta é o fator de crescimento **quando `n` dobra**:"},
  {"table": {"head": ["Classe", "Fator ao dobrar n"], "rows": [
    ["`O(1)`", "1,0 — o tempo não muda"],
    ["`O(log n)`", "≈1,1"],
    ["`O(n)`", "2,0 — dobra"],
    ["`O(n log n)`", "≈2,1"],
    ["`O(n²)`", "4,0 — quadruplica"],
    ["`O(n³)`", "8,0"],
    ["`O(2ⁿ)`", "o fator **cresce** a cada medida"],
  ]}},
  { code: `adopt Arcane.Bench as B

action quadratica(xs):
    total := 0
    cycle a in xs:
        cycle b in xs:
            total += 1
    yield total

action preparar(n):
    yield [i cycle i in range(0, n)]

out B.relatorio(B.classe(quadratica, [200, 400, 800, 1600],
    preparar := preparar))` },
  { lang: 'text', code: `         n          ms     fator
       200     23.6437  
       400     94.4445      3.99
       800    378.1281      4.00
      1600   1521.9530      4.03

  fator medio 4.00  ->  O(n^2)` },

  {"h3": "Três respostas, e o que cada uma diz"},
  {"list": [
    "**Uma classe** (`O(n²)`) — o fator bate com uma só, e a resposta é essa.",
    "**Duas classes** (`O(n)` ou `O(n log n)`) — as duas cabem, e a medição não as separa. Ficam a 0,15 de distância, e nenhuma amostra abaixo de uns cem mil itens decide entre elas. Escolher uma seria inventar precisão.",
    "**Um intervalo** (`entre O(n log n) e O(n²)`) — o fator não bate com nenhuma, e cai entre duas. É o caso real de `s += \"x\"` num laço: o custo por volta do interpretador é grande e **linear**, e mascara parte da cópia até `n` crescer o bastante.",
  ]},
  {"callout": {"tipo": "dica", "titulo": "Por que a mediana, e não a média", "texto": "Uma pausa do coletor de lixo no meio de uma amostra vira um fator absurdo, e a média o carrega para sempre — um `O(n)` seria reportado como exponencial por causa de uma coleta bem colocada. A mediana o descarta."}},

  {"h3": "Onde o `+=` é caro, e onde não é"},
  {"p": "Vale saber por que a mesma linha mede coisas diferentes conforme o lugar. O CPython tem uma otimização para `s += t` que só funciona quando a string tem **uma referência só** — e dentro do interpretador ela nunca tem, porque a variável vive no dicionário do escopo."},
  {"table": {"head": ["Onde", "Fator", "Classe"], "rows": [
    ["variável local de Python", "2,11", "`O(n)` — a otimização se aplica"],
    ["string dentro de um dicionário", "4,06", "**`O(n²)`** — ela não se aplica"],
    ["dentro do interpretador DataForge", "2,48", "entre as duas"],
  ]}},
  {"p": "O interpretador fica no meio porque o custo por volta dele é grande e **linear**, e ainda mascara parte da cópia nesses tamanhos. Com `n` maior a curva sobe: 3,07 em 160 mil. É por isso que [`Arcane.Text.construtor`](/docs/biblioteca) existe — ele é `O(n)` em qualquer tamanho."},

  {"h2": "As duas respostas lado a lado"},
  {"p": "`dataforge big-o --medir` roda o arquivo e põe a classe lida ao lado da medida:"},
  { lang: 'bash', code: `dataforge big-o --medir algoritmos.df` },
  { lang: 'text', code: `medindo algoritmos.df — 4 acao(oes)

  acao                     analisado      medido
  ──────────────────────── ────────────── ──────────────────────────
  pares                    O(n^2)         O(n^2)                fator 4.04
  primeiro                 O(1)           O(1) ou O(log n)      fator 0.90
  so_tres                  O(n)           O(n) ou O(n log n)    fator 2.00
  soma                     O(n)           O(n) ou O(n log n)    fator 1.98` },
  {"p": "Só ações de **um parâmetro** entram. Com dois, não há como saber qual deles é o `n` — e adivinhar produziria uma curva sobre o argumento errado, que é pior que não medir."},

  {"h2": "O que a medição não faz"},
  {"list": [
    "**Não prova um limite.** Ela descreve a amostra que houve. Um algoritmo com pior caso raro pode medir `O(n)` mil vezes e ser `O(n²)`.",
    "**Não substitui o `check`.** A análise estática vê o código todo, inclusive o ramo que a sua entrada não percorreu.",
    "**Não mede memória.** `Bench` mede tempo. Para espaço, [`dataforge big-o`](/docs/big-o/espaco) analisa a estrutura.",
  ]},
];

const headings = [{ id: 'medir-uma-acao', text: "Medir uma ação", level: 2 as const }, { id: 'comparar-implementacoes', text: "Comparar implementações", level: 2 as const }, { id: 'descobrir-a-classe', text: "Descobrir a classe", level: 2 as const }, { id: 'tres-respostas-e-o-que-cada-uma-diz', text: "Três respostas, e o que cada uma diz", level: 3 as const }, { id: 'onde-o-e-caro-e-onde-nao-e', text: "Onde o `+=` é caro, e onde não é", level: 3 as const }, { id: 'as-duas-respostas-lado-a-lado', text: "As duas respostas lado a lado", level: 2 as const }, { id: 'o-que-a-medicao-nao-faz', text: "O que a medição não faz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Benchmark"}
      description={"Medir, comparar implementações, e descobrir a classe de custo que acontece de verdade."}
      href={"/docs/tecnicas/bench"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
