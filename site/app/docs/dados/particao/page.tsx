// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_engenharia.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Janelas por grupo",
  description: "Média móvel por loja, ranking por categoria, variação em relação ao dia anterior do mesmo produto.",
};

const blocos: Bloco[] = [
  {"p": "Toda função de janela sem partição responde à pergunta errada no caso mais comum que existe. \"Média móvel de sete dias **por loja**\" atravessava a fronteira das lojas: a primeira venda da loja B entrava com as três últimas da loja A."},
  { code: `adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "sul",   "dia": 1, "valor": 10},
    {"loja": "norte", "dia": 1, "valor": 100},
    {"loja": "sul",   "dia": 2, "valor": 20},
    {"loja": "norte", "dia": 2, "valor": 200},
    {"loja": "sul",   "dia": 3, "valor": 30},
])

// SEM partição: o acumulado soma as duas lojas juntas.
sem := v.acumulado("valor")
assert sem.coluna("valor_soma_acumulado") is [10, 110, 130, 330, 360]

// COM partição: cada loja tem o seu.
com := v.acumulado("valor", "soma", void, "loja")
assert com.coluna("valor_soma_acumulado") is [10, 100, 30, 300, 60]
out com.texto()`, lang: 'df' },
  {"p": "O primeiro resultado não é um erro visível: é um número plausível. Num painel de vendas ele apareceria como \"acumulado da loja sul: 360\", e ninguém tem como desconfiar olhando."},
  {"h2": "As cinco que aceitam `por`"},
  {"table": {"head": ["Função", "Responde", "Com `por`"], "rows": [["`janela`", "a média dos últimos N", "dos últimos N **daquele grupo**"], ["`acumulado`", "o total corrido", "o total corrido **do grupo**"], ["`defasar`", "o valor de N linhas atrás", "da linha anterior **do mesmo grupo**"], ["`variacao`", "quanto mudou", "em relação ao anterior **do grupo**"], ["`ranquear`", "a posição geral", "a posição **dentro do grupo**"]]}},
  { code: `adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"cat": "bebida", "produto": "cafe",   "vendas": 300},
    {"cat": "bebida", "produto": "cha",    "vendas": 120},
    {"cat": "acessorio", "produto": "filtro", "vendas": 90},
    {"cat": "acessorio", "produto": "caneca", "vendas": 150},
])

// Um ranking GLOBAL responde "quem vendeu mais no total".
global_ := v.ranquear("vendas", "posicao_geral")
assert global_.coluna("posicao_geral") is [1, 3, 4, 2]

// O que quase sempre se quer é "quem é o primeiro DA SUA categoria".
na_cat := global_.ranquear("vendas", "posicao_na_cat", yes, "minimo", "cat")
assert na_cat.coluna("posicao_na_cat") is [1, 2, 2, 1]
out na_cat.texto()`, lang: 'df' },
  {"h2": "A ordem das linhas é preservada"},
  {"p": "A coluna nova volta na posição **original**, e não agrupada. Um quadro reordenado pela janela quebraria o `com`, que casa por posição — e faria a linha 3 do resultado não corresponder à linha 3 da entrada, que é o tipo de defeito que só aparece três junções depois."},
  { code: `adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"g": "a", "i": 1, "x": 10},
    {"g": "b", "i": 2, "x": 100},
    {"g": "a", "i": 3, "x": 20},
])
r := v.acumulado("x", "soma", void, "g")
assert r.coluna("i") is [1, 2, 3]           // a ordem é a de entrada
assert r.coluna("x_soma_acumulado") is [10, 100, 30]`, lang: 'df' },
  {"h2": "Partição por várias colunas"},
  { code: `adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "sul", "produto": "cafe", "v": 1},
    {"loja": "sul", "produto": "cafe", "v": 2},
    {"loja": "sul", "produto": "cha",  "v": 10},
    {"loja": "norte", "produto": "cafe", "v": 100},
])
r := v.acumulado("v", "soma", void, ["loja", "produto"])
assert r.coluna("v_soma_acumulado") is [1, 3, 10, 100]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Ordene antes", "texto": "Uma janela lê as linhas **na ordem em que elas estão**. Para \"os últimos sete dias\", ordene por data antes — senão a janela junta o que estiver perto no arquivo, e não no tempo. Ordenar depois da janela não conserta: o valor já foi calculado."}},
  { code: `adopt Arcane.Quadro as Q

v := Q.de_vaults([
    {"loja": "sul", "dia": 3, "x": 30},
    {"loja": "sul", "dia": 1, "x": 10},
    {"loja": "sul", "dia": 2, "x": 20},
])

// Fora de ordem, a "variação em relação a ontem" é ficção.
errado := v.variacao("x", "delta", no)
assert errado.coluna("delta") is [void, 0 - 20, 10]

// Ordenar primeiro é o que a torna verdade.
certo := v.ordenar("dia").variacao("x", "delta", no)
assert certo.coluna("delta") is [void, 10, 10]`, lang: 'df' },
];

const headings = [{ id: 'as-cinco-que-aceitam-por', text: "As cinco que aceitam `por`", level: 2 as const }, { id: 'a-ordem-das-linhas-e-preservada', text: "A ordem das linhas é preservada", level: 2 as const }, { id: 'particao-por-varias-colunas', text: "Partição por várias colunas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Janelas por grupo"}
      description={"Média móvel por loja, ranking por categoria, variação em relação ao dia anterior do mesmo produto."}
      href={"/docs/dados/particao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
