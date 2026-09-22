// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Jogo de terminal",
  description: "Jogo da velha com um adversário que não perde — minimax com poda.",
};

const blocos: Bloco[] = [
  {"p": "Jogo é o projeto que mais cedo ensina a separar **estado** de **apresentação**: o tabuleiro é um dado, a jogada é uma função pura sobre ele, e o terminal só desenha. Com isso a IA consegue simular milhares de jogos sem imprimir nada."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["cluster de 9 casas", "o estado inteiro do jogo"], ["recursão", "o minimax desce até o fim de cada linha de jogo"], ["poda alfa-beta", "a mesma resposta visitando uma fração dos nós"], ["função pura", "`jogar` devolve um tabuleiro novo"]]}},
  {"h2": "Estrutura"},
  { code: `jogo-da-velha/
  src/
    tabuleiro.df   jogar, vencedor, casas livres
    ia.df          minimax
    tela.df        desenhar e ler a jogada
    main.df
  tests/`, lang: 'text' },
  { code: `[project]
name = "jogo-da-velha"
version = "0.1.0"
description = "Jogo da velha com IA"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `steady LINHAS := [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]

action vencedor(t):
    cycle l in LINHAS:
        given t[l[0]] is not " " and t[l[0]] is t[l[1]] and t[l[1]] is t[l[2]]:
            yield t[l[0]]
    yield void

action livres(t):
    yield [i cycle i in range(0, 9) given t[i] is " "]

action jogar(t, casa, peca):
    novo := [...t]
    novo[casa] := peca
    yield novo

action outro(p):
    yield "O" given p is "X" otherwise "X"

// Pontua do ponto de vista de 'eu'. A profundidade entra na conta para a
// IA preferir ganhar AGORA a ganhar daqui a tres jogadas.
action minimax(t, vez, eu, alfa, beta, prof):
    v := vencedor(t)
    given v is eu:
        yield 10 - prof
    given v is not void:
        yield prof - 10
    casas := livres(t)
    given len(casas) is 0:
        yield 0
    given vez is eu:
        melhor := -100
        cycle c in casas:
            melhor := max(melhor, minimax(jogar(t, c, vez), outro(vez), eu, alfa, beta, prof + 1))
            alfa := max(alfa, melhor)
            given alfa bigger_eq beta:
                halt
        yield melhor
    pior := 100
    cycle c in casas:
        pior := min(pior, minimax(jogar(t, c, vez), outro(vez), eu, alfa, beta, prof + 1))
        beta := min(beta, pior)
        given alfa bigger_eq beta:
            halt
    yield pior

action melhor_jogada(t, eu):
    melhor := -1000
    escolha := -1
    cycle c in livres(t):
        nota := minimax(jogar(t, c, eu), outro(eu), eu, -1000, 1000, 1)
        given nota bigger melhor:
            melhor := nota
            escolha := c
    yield escolha

action desenhar(t):
    yield [$" {t[0]} | {t[1]} | {t[2]}", $" {t[3]} | {t[4]} | {t[5]}", $" {t[6]} | {t[7]} | {t[8]}"].join("\\n---+---+---\\n")

// X tem duas em linha: a IA (O) precisa bloquear na casa 2.
t := ["X", "X", " ", " ", "O", " ", " ", " ", " "]
assert melhor_jogada(t, "O") is 2

// O tem duas em linha: ganhar vale mais que bloquear.
t2 := ["X", "X", " ", "O", "O", " ", "X", " ", " "]
assert melhor_jogada(t2, "O") is 5

// IA contra IA termina sempre empatada.
jogo := [" " cycle _ in range(0, 9)]
vez := "X"
persist vencedor(jogo) is void and len(livres(jogo)) bigger 0:
    jogo := jogar(jogo, melhor_jogada(jogo, vez), vez)
    vez := outro(vez)
out desenhar(jogo)
assert vencedor(jogo) is void`, lang: 'df', title: `src/ia.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/ia as IA

crucible "ia":
    trial "bloqueia a linha do adversario":
        t := ["X", "X", " ", " ", "O", " ", " ", " ", " "]
        expect IA.melhor_jogada(t, "O") is 2`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["o tabuleiro não sabe desenhar", "a IA imprime cada jogo simulado"], ["`jogar` devolve cópia", "a simulação de uma linha estraga o tabuleiro da seguinte"], ["a profundidade na nota", "a IA enrola: vê a vitória em uma e prefere a de três"], ["poda alfa-beta", "a primeira jogada visita 549 mil nós em vez de ~20 mil"]]}},
  {"h2": "Para ir além"},
  {"list": ["Meça a poda com `Arcane.Bench` antes e depois — [Medir](/docs/cli/bench).", "Troque para um tabuleiro 4x4 e veja por que o minimax puro deixa de servir.", "Um jogo de verdade tem laço de eventos: [Arcane.Laco](/docs/biblioteca/laco)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Jogo de terminal"}
      description={"Jogo da velha com um adversário que não perde — minimax com poda."}
      href={"/docs/projetos/jogo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
