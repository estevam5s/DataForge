// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/plataforma_runtime.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A máquina: como um .df executa",
  description: "Do texto ao resultado — lexer, parser, análise, compilação para fechamentos e o interpretador de árvore.",
};

const blocos: Bloco[] = [
  {"p": "Esta página responde o que acontece entre você apertar Enter e o programa dar resposta. Ela é honesta sobre a parte que mais gera pergunta: **não há VM de bytecode**, e a razão está medida mais abaixo."},
  { code: `arquivo.df → tokenize() → parse() → [check_program()] → run(ast)
             lexer.py    parser.py  typechecker.py      interpreter.py
`, lang: 'text' },
  {"h2": "As cinco etapas"},
  {"table": {"head": ["Etapa", "Arquivo", "O que entra e o que sai"], "rows": [["**léxico**", "`lexer.py`", "texto → tokens, com INDENT/DEDENT e interpolação"], ["**sintaxe**", "`parser.py`", "tokens → árvore, por descida recursiva"], ["**análise**", "`typechecker.py`", "árvore → diagnósticos, sem executar nada"], ["**compilação**", "`compilador.py`", "árvore → fechamentos Python, uma vez"], ["**execução**", "`interpreter.py`", "fechamentos → o programa rodando"]]}},
  {"p": "A análise é **opcional** para rodar e obrigatória no `check`: é a mesma função nos dois casos, e é por isso que o editor, o CI e a linha de comando nunca discordam."},
  {"h2": "A indentação vira token"},
  {"p": "Blocos por indentação exigem que o lexer conte colunas e emita marcas — não há chave para o parser casar:"},
  { code: `given x > 5:
    out "grande"
out "fim"
`, lang: 'df' },
  { code: `GIVEN  IDENT(x)  GT  INT(5)  COLON  NEWLINE
INDENT  OUT  STRING  NEWLINE
DEDENT  OUT  STRING  NEWLINE  EOF
`, lang: 'text' },
  {"p": "Tab é erro, e não equivalente a espaços: a mistura dos dois produz um arquivo que se lê de um jeito e executa de outro, conforme a largura do tab no editor de cada um."},
  {"h2": "Despacho: de string para tabela, e daí para fechamento"},
  {"p": "O interpretador começou despachando por **nome de classe** — um nó `GivenBlock` procurava `exec_GivenBlock`. Funciona e é lento: é uma busca de atributo por instrução executada, e um programa médio executa mais de um milhão."},
  {"p": "Hoje há duas camadas:"},
  {"list": ["**Tabela por classe** — o nome vira uma entrada de dicionário resolvida uma vez.", "**Compilação para fechamentos** — a árvore é percorrida **uma vez** e cada nó vira uma função Python que faz o que aquele nó faz. Executar passa a ser chamar funções: sem busca, sem `isinstance`, sem ler campo de nó."], "ordered": true},
  { code: `// o que a compilação faz, em espírito
// antes:  a cada volta, olhar o nó e decidir o que ele é
// depois: uma função por nó, decidida uma vez

soma := 0
cycle i from 1 to 1000000:
    soma += i
`, lang: 'df' },
  {"p": "Medido: **1,5× a 1,8×**, conforme a carga. Três regras governam esse arquivo, e a terceira é a que mais surpreende:"},
  {"table": {"head": ["Regra", "Porque"], "rows": [["cada construtor espelha um `exec_`/`eval_` e **delega aos mesmos auxiliares**", "a semântica não é reimplementada; divergir faria a linguagem responder duas coisas"], ["o que não está na tabela **recua** para o interpretador", "um recurso novo continua funcionando sem tocar aqui — só não fica mais rápido"], ["o **depurador desliga tudo**", "ele para em cada linha sombreando `execute`, e o corpo compilado passaria por fora: um depurador que enxerga metade das instruções é pior que um interpretador lento"]]}},
  {"h2": "Por que não há bytecode"},
  {"p": "A pergunta é justa: quase toda linguagem interpretada compila para bytecode e roda uma VM. A resposta é um número."},
  {"table": {"head": ["Técnica", "Ganho medido", "Custo"], "rows": [["interpretador de árvore (o ponto de partida)", "1×", "—"], ["tabela de despacho", "incluída abaixo", "pequeno"], ["**compilação para fechamentos** (hoje)", "**1,5× a 1,8×**", "um arquivo de 330 linhas"], ["VM de bytecode **em Python**", "~6,5× (o teto)", "reescrever o interpretador inteiro"], ["sair do Python", "muito mais", "a promessa de zero dependência acaba"]]}},
  {"p": "O teto de **6,5×** é o ponto: uma VM escrita em Python continua sendo Python executando o laço de despacho. O ganho existe e não é transformador, e o custo é reescrever a parte do sistema que mais tem teste e mais tem semântica sutil."},
  {"callout": {"tipo": "nota", "titulo": "Onde o esforço foi, em vez disso", "texto": "Sete gargalos medidos com `cProfile` — não com intuição. O maior: as tabelas de método de texto, vault e cluster eram literais reconstruídos a **cada** acesso, e 146 lambdas nasciam num `xs.append(i)`. 200 mil `append`: **0,77 s → 0,27 s**. Nenhum deles estava onde se esperava."}},
  {"h2": "O escopo, e a otimização mais perigosa"},
  {"p": "Um laço reaproveita o escopo entre voltas — alocar um por volta é caro. Mas se o corpo **captura** o escopo (uma ação, um `lambda`, um `blueprint`, um `thread`, um `defer`), cada volta precisa do seu:"},
  { code: `acoes := []
cycle i from 1 to 3:
    acoes.append(lambda: i)

out [f() cycle f in acoes]      // [1, 2, 3] — e não [3, 3, 3]
`, lang: 'df' },
  {"p": "Sem essa distinção, as três closures veriam o último valor — o clássico que existe em várias linguagens e que aqui não acontece. A varredura olha a árvore **inteira**, e não só as instruções: um `lambda` vive dentro de uma expressão."},
  {"h2": "A pilha, e o salto de cauda"},
  {"p": "O teto de quadros é mil, e recursão legítima o atinge: uma travessia de árvore de cinco mil nós não tem nada de infinita. Há duas saídas, e a primeira é automática:"},
  { code: `action somar_ate(n, total := 0):
    given n is 0:
        yield total
    yield somar_ate(n - 1, total + n)     // retorno INTEIRO: vira salto

out somar_ate(50000)
`, lang: 'df' },
  {"p": "`yield f(…)` como retorno inteiro não empilha: o quadro é reusado. Testado com 200 mil. Quatro casos são **recusados** pela análise, antes de rodar — há `defer` na ação, o `yield` está dentro de `monitor`, a recursão é indireta, ou **todo** `yield` da ação é cauda (aí ela nunca devolve, e virar laço mudo seria pior que o erro)."},
  {"h2": "Threads, processos e o GIL"},
  {"table": {"head": ["Ferramenta", "Paralelismo real", "Para quê"], "rows": [["`thread:` / `parallel:`", "**não** em CPU", "rede, disco, banco, espera"], ["`async` / `await`", "**não** em CPU", "entrada e saída sobreposta"], ["`P.map_processos`", "**sim**", "trabalho de CPU — medido 4,71× em 10 núcleos"]]}},
  {"p": "O GIL do Python deixa uma thread por vez executar bytecode. A travessia de processo copia a **declaração** da ação, e não o fechamento — ver [complexidade em paralelo](/docs/big-o/paralelo)."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/referencia/arquitetura", "title": "Arquitetura do runtime", "desc": "o mapa dos arquivos, um por um"}, {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que otimizar sem medir é chute"}, {"href": "/docs/tecnicas/ponte", "title": "A ponte para o Python", "desc": "como um objeto estranho atravessa sem cópia"}]},
];

const headings = [{ id: 'as-cinco-etapas', text: "As cinco etapas", level: 2 as const }, { id: 'a-indentacao-vira-token', text: "A indentação vira token", level: 2 as const }, { id: 'despacho-de-string-para-tabela-e-dai-para-fechamento', text: "Despacho: de string para tabela, e daí para fechamento", level: 2 as const }, { id: 'por-que-nao-ha-bytecode', text: "Por que não há bytecode", level: 2 as const }, { id: 'o-escopo-e-a-otimizacao-mais-perigosa', text: "O escopo, e a otimização mais perigosa", level: 2 as const }, { id: 'a-pilha-e-o-salto-de-cauda', text: "A pilha, e o salto de cauda", level: 2 as const }, { id: 'threads-processos-e-o-gil', text: "Threads, processos e o GIL", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A máquina: como um .df executa"}
      description={"Do texto ao resultado — lexer, parser, análise, compilação para fechamentos e o interpretador de árvore."}
      href={"/docs/vm"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
