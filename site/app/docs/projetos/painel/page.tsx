// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Painel de dados",
  description: "Um dashboard com filtro, métricas e tabela — testado com a sonda, sem navegador.",
};

const blocos: Bloco[] = [
  {"p": "A Vitrine roda o programa **inteiro** de novo a cada interação, e o estado da sessão sobrevive. É o modelo que dispensa callback — e por isso o painel é um programa de cima para baixo que se testa como qualquer outro: a sonda digita, clica e pergunta o que apareceu."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`V.titulo` / `V.metrica`", "o topo do painel"], ["`V.escolha`", "o filtro que reexecuta a página"], ["`V.tabela`", "as linhas filtradas"], ["`V.testar`", "clicar e digitar sem navegador"]]}},
  {"h2": "Estrutura"},
  { code: `painel-vendas/
  src/
    dados.df       carregar (com V.cache em producao)
    painel.df      a pagina
  main.df          V.rodar(painel)
  tests/`, lang: 'text' },
  { code: `[project]
name = "painel-vendas"
version = "0.1.0"
description = "Painel de vendas"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Vitrine as V

VENDAS := [
    {"loja": "centro", "mes": "jul", "valor": 1200},
    {"loja": "centro", "mes": "ago", "valor": 1500},
    {"loja": "norte", "mes": "jul", "valor": 800},
    {"loja": "norte", "mes": "ago", "valor": 950}
]

action painel():
    V.titulo("Vendas por loja")
    loja := V.escolha("Loja", ["todas", "centro", "norte"])
    linhas := VENDAS given loja is "todas" otherwise (VENDAS >> sift v: v["loja"] is loja)
    total := sum(linhas >> morph v: v["valor"])
    V.metrica("Total", $"R$ {total}")
    V.metrica("Lançamentos", str(len(linhas)))
    V.tabela(linhas)

t := V.testar(painel)
assert not t.falhou()
assert "R$ 4450" in t.texto()

t.selecionar("Loja", "norte")
assert "R$ 1750" in t.texto()
assert t.existe("tabela")
out "painel verde"`, lang: 'df', title: `src/painel.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt Arcane.Vitrine as V
adopt ../src/painel as P

crucible "painel":
    trial "o filtro muda o total":
        t := V.testar(P.painel)
        t.selecionar("Loja", "centro")
        expect "R$ 2700" in t.texto()`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["o painel é uma ação sem argumento", "não há como testá-lo sem subir o servidor"], ["o filtro é um valor, não um callback", "o estado se espalha por funções que ninguém chama em ordem"], ["`V.cache` na leitura dos dados (em produção)", "cada clique relê o banco inteiro"], ["a sonda pergunta o **texto**", "o teste quebra a cada mudança de CSS"]]}},
  {"h2": "Para ir além"},
  {"list": ["Gráficos: [Vitrine → gráficos](/docs/vitrine/graficos).", "Layout em malha e painéis: [Vitrine → painel](/docs/vitrine/painel).", "Em produção, com sessão fora do processo: [Vitrine → produção](/docs/vitrine/producao)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Painel de dados"}
      description={"Um dashboard com filtro, métricas e tabela — testado com a sonda, sem navegador."}
      href={"/docs/projetos/painel"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
