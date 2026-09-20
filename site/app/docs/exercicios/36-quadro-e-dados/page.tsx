// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "36 · Quadro e dados",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 36`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[241](#241-o-quadro-e-os-seis-verbos-do-pipeline)", "**O quadro, e os seis verbos do pipeline**", "carregue um conjunto com ausencia, limpe-o, agrupe e"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "241 · O quadro, e os seis verbos do pipeline"},
  {"p": "**Enunciado.** carregue um conjunto com ausencia, limpe-o, agrupe e"},
  { code: `// responda tres perguntas. Sem sair da linguagem.

adopt Arcane.Quadro as Q

// Um quadro nasce do que o resto da linguagem ja produz: um cluster de
// vaults. E o que 'IO.read_csv(caminho, yes)' devolve, e o que
// 'Database.query' devolve.
vendas := Q.de_vaults([
        {"produto": "cafe", "regiao": "sul", "valor": 120.0, "qtd": 4},
        {"produto": "cafe", "regiao": "norte", "valor": 90.0, "qtd": 3},
        {"produto": "cha", "regiao": "sul", "valor": 60.0, "qtd": 2},
        {"produto": "cha", "regiao": "norte", "valor": void, "qtd": 1},
        {"produto": "acucar", "regiao": "sul", "valor": 30.0, "qtd": 5}
    ])

assert typeof(vendas) is "Quadro", "o tipo tem o nome da linguagem"
assert vendas.forma() is [5, 4], "cinco linhas, quatro colunas"

// ── 1. Olhar antes de calcular ──────────────────────────────
//
// 'perfil' e o primeiro comando a rodar num conjunto que voce nao
// conhece. Uma media sobre dados com buraco nao avisa que tinha buraco.

perfil := vendas.perfil()
so_valor := perfil.onde(lambda l: l["coluna"] is "valor")
assert so_valor.coluna("ausentes") is [1], "uma venda sem valor"
assert so_valor.coluna("tipo") is ["Float"], "a coluna e decimal"

// ── 2. A logica de tres valores ─────────────────────────────
//
// Comparar com o desconhecido nao da nem sim nem nao, e a linha nao
// passa. E o que o SQL faz, e o que toda ferramenta de dados faz.

acima := vendas >> onde valor bigger 50
assert acima.altura() is 3, "a linha sem valor fica de fora"

// E quem QUER a ausencia pergunta por ela.
sem_valor := vendas >> onde valor is void
assert sem_valor.altura() is 1, "e ela continua alcancavel"

// ── 3. A coluna se escreve nua, e o escopo de fora continua ──

limite := 100.0
caras := vendas >> onde valor bigger limite
assert caras.altura() is 1, "'limite' vem de fora; 'valor' e coluna"

// ── 4. Agrupar e resumir ────────────────────────────────────

resumo := vendas
    >> onde valor bigger 0
    >> agrupar produto
    >> resumir {"valor": "soma"}
    >> ordenar valor desc

assert resumo.coluna("produto") is ["cafe", "cha", "acucar"], "do maior ao menor"
assert resumo.coluna("valor") is [210.0, 60.0, 30.0], "as somas"

// 'contagem' e 'contagem_valida' respondem perguntas DIFERENTES:
// quantas linhas ha, e quantas tem valor.
contas := vendas.agrupar("produto")
    .resumir({"valor": ["contagem", "contagem_valida"]})
cha := contas.onde(lambda l: l["produto"] is "cha")
assert cha.coluna("valor_contagem") is [2], "duas linhas de cha"
assert cha.coluna("valor_contagem_valida") is [1], "uma delas sem valor"

// ── 5. Limpar ───────────────────────────────────────────────

limpo := vendas.preencher({"valor": "media"})
assert limpo.nulos()["valor"] is 0, "nao sobrou ausencia"
assert limpo.coluna("valor")[3] is 75.0, "a media das quatro que havia"

// ── 6. Juntar ───────────────────────────────────────────────

gerentes := Q.de_vaults([{"regiao":"sul", "gerente":"Ana"}])

dentro := vendas.juntar(gerentes, "regiao")
esquerda := vendas.juntar(gerentes, "regiao", "esquerda")
assert dentro.altura() is 3, "so o que casa"
assert esquerda.altura() is 5, "e as cinco, com void onde nao casou"
assert esquerda.nulos()["gerente"] is 2, "as duas do norte"

// ── 7. O quadro fala o protocolo da linguagem ───────────────
//
// Nada no 'cycle', no 'len' ou no '>>' sabe o que e um quadro. Eles
// funcionam porque iterar um quadro da LINHAS como vault.

total := 0
cycle linha in vendas:
    total += linha["qtd"]
assert total is 15, "o cycle percorre linhas"
assert len(vendas) is 5, "len conta linhas"
assert vendas["qtd"] is [4, 3, 2, 1, 5], "indexar por texto da a coluna"
assert vendas[0]["produto"] is "cafe", "indexar por numero da a linha"

// E os verbos convivem com sift e morph no mesmo pipeline.
nomes := vendas >> onde regiao is "sul" >> morph l: l["produto"]
assert nomes is ["cafe", "cha", "acucar"], "os tres do sul"

// ── 8. Todo verbo devolve um quadro NOVO ────────────────────

assert vendas.altura() is 5, "o original nunca muda"

out "241 ok — quadro, verbos, ausencia, agrupamento e juncao"`, lang: 'df', title: `exercicios/36-quadro-e-dados/241_quadro_e_verbos.df` },
  {"h3": "O que se pratica"},
  {"p": "Carregar um conjunto com ausência, olhar antes de calcular, filtrar, agrupar, resumir, limpar e juntar — sem sair da linguagem."},
  {"h3": "O que este exercício ensina que não é óbvio"},
  {"p": "**1. `perfil()` vem antes de qualquer conta.** Uma média sobre dados com buraco não avisa que tinha buraco: ela só sai menor. Conferir a contagem de ausentes primeiro é o passo que separa um relatório de um chute."},
  {"p": "**2. A ausência não passa no filtro, e isso é de propósito.** `>> onde valor bigger 50` deixa de fora a linha cujo `valor` é `void` — comparar com o desconhecido não dá nem sim nem não. É a lógica de três valores do SQL, e a de toda ferramenta de dados que existe."},
  {"p": "A outra escolha — levantar erro — é o que a linguagem faz em toda expressão comum, e está certa lá. Aqui tornaria o verbo inutilizável: todo conjunto real tem ausência, e o primeiro `onde` de todo programa morreria na primeira linha vazia. Quem **quer** a ausência pergunta por ela: `onde valor is void`."},
  {"p": "**3. Dentro de um `onde`, um nome nu é uma COLUNA.** E o escopo de fora continua alcançável para tudo o que não for coluna — um limite guardado numa variável funciona em `onde valor bigger limite`. Sem essa regra, o mesmo código leria de dois jeitos conforme o que houvesse no escopo."},
  {"p": "**4. `contagem` e `contagem_valida` respondem perguntas diferentes.** Quantas linhas há, e quantas têm valor. Num conjunto com ausência, confundir as duas troca a média — e o erro não aparece em lugar nenhum."},
  {"p": "**5. Nada no `cycle`, no `len` ou no `>>` sabe o que é um quadro.** Eles funcionam porque iterar um quadro dá **linhas como vault** — o mesmo protocolo que faz a ponte para o Python funcionar sem conversão. Se alguém um dia trocar protocolo por tipo, isso quebra inteiro."},
  {"p": "**6. Todo verbo devolve um quadro novo.** Como `record` e `with`: o original nunca muda. É o que permite comparar o antes e o depois, e o que torna um pipeline reexecutável."},
  {"h3": "Para ler depois"},
  {"list": ["[O Quadro](https://dataforge-lang.vercel.app/docs/dados/quadro)", "[Os verbos do pipeline](https://dataforge-lang.vercel.app/docs/dados/verbos)", "[O mapa do ecossistema de dados](https://dataforge-lang.vercel.app/docs/dados/mapa)"]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/36-quadro-e-dados/241_quadro_e_verbos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '241-o-quadro-e-os-seis-verbos-do-pipeline', text: "241 · O quadro, e os seis verbos do pipeline", level: 2 as const }, { id: 'o-que-se-pratica', text: "O que se pratica", level: 3 as const }, { id: 'o-que-este-exercicio-ensina-que-nao-e-obvio', text: "O que este exercício ensina que não é óbvio", level: 3 as const }, { id: 'para-ler-depois', text: "Para ler depois", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"36 · Quadro e dados"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/36-quadro-e-dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
