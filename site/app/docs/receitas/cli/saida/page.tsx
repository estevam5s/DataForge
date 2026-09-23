// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cor, tabela e o terminal que não é terminal",
  description: "Colorir sem estragar o `| grep`, e desenhar tabela, árvore e barra sem dependência.",
};

const blocos: Bloco[] = [
  {"p": "A regra que quase todo programa de terminal erra: **cor só quando a saída é um terminal**. Canalizado para um arquivo ou para o `grep`, o código de escape vira lixo no meio do dado — e um `grep \"erro\"` deixa de casar porque há um `\\x1b[31m` grudado na palavra."},
  { code: `adopt Arcane.Color as Cor
adopt Arcane.OS as OS

// 'auto' decide pelo terminal; 'supports' responde o que ele aceita
assert Cor.supports() is yes or Cor.supports() is no

// E 'strip' tira a cor de um texto já colorido — é o que um teste faz.
pintado := Cor.red("falhou")
assert Cor.strip(pintado) is "falhou"
out Cor.strip(Cor.bold(Cor.green("ok")))`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`NO_COLOR` é um padrão, não uma preferência", "texto": "A variável `NO_COLOR` desliga a cor de qualquer ferramenta que a respeite, e existe justamente para quem canaliza, registra em log ou usa leitor de tela. O `dataforge` a respeita em toda a CLI — e isso foi um defeito real aqui: só o depurador a lia."}},
  {"h2": "Tabela"},
  { code: `adopt Arcane.Color as Cor

linhas := [
    ["produto", "qtd", "preço"],
    ["café", "12", "R$ 32,90"],
    ["filtro", "3", "R$ 8,50"],
]
desenho := Cor.table(linhas)
assert "produto" in desenho
out desenho`, lang: 'df' },
  {"h2": "Árvore, régua e barra"},
  { code: `adopt Arcane.Color as Cor

out Cor.rule("Relatório")
out Cor.tree({"projeto": {"src": ["main.df", "util.df"], "tests": ["main_test.df"]}})
out Cor.bar(0.72, 30)
out Cor.box("Concluído em 1,2 s")`, lang: 'df' },
  {"h2": "Progresso que não polui um log"},
  {"p": "Uma barra que se reescreve com `\\r` é ótima num terminal e é uma linha por quadro num arquivo de log. A saída é perguntar antes:"},
  { code: `adopt Arcane.Color as Cor
adopt Arcane.OS as OS

action progresso(feito, total):
    given not OS.is_tty():
        // canalizado: uma linha por marco, e só
        given feito % 50 is 0:
            out $"  {feito}/{total}"
        yield void
    out $"\\r  {Cor.bar(feito / total, 24)} {feito}/{total}"
    yield void

cycle i from 1 to 100:
    given i % 50 is 0:
        progresso(i, 100)
out ""`, lang: 'df' },
  {"h2": "A largura do terminal"},
  { code: `adopt Arcane.Cli as Cli
adopt Arcane.Color as Cor

largura := Cli.largura()
assert largura > 0
// Sem terminal, ela devolve um padrão — e é por isso que ela nunca é
// zero: uma divisão por largura no meio do desenho estouraria.
out $"largura: {largura} colunas"`, lang: 'df' },
];

const headings = [{ id: 'tabela', text: "Tabela", level: 2 as const }, { id: 'arvore-regua-e-barra', text: "Árvore, régua e barra", level: 2 as const }, { id: 'progresso-que-nao-polui-um-log', text: "Progresso que não polui um log", level: 2 as const }, { id: 'a-largura-do-terminal', text: "A largura do terminal", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Cor, tabela e o terminal que não é terminal"}
      description={"Colorir sem estragar o `| grep`, e desenhar tabela, árvore e barra sem dependência."}
      href={"/docs/receitas/cli/saida"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
