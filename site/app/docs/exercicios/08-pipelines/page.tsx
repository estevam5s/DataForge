// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "08 · Pipelines",
  description: "12 exercícios: sift, morph, distill e composição.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Primeiros passos** · sift, morph, distill e composição · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 08`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[087](#087-sift-filtro)", "**sift (filtro)**", "filtre numeros e registros com o operador >>."], ["[088](#088-morph-transformacao)", "**morph (transformacao)**", "transforme cada elemento de um cluster."], ["[089](#089-distill-reducao)", "**distill (reducao)**", "reduza um cluster a um unico valor."], ["[090](#090-pipeline-encadeado)", "**Pipeline encadeado**", "combine sift, morph e distill em uma unica expressao."], ["[091](#091-pipeline-com-acao-nomeada)", "**Pipeline com acao nomeada**", "reutilize acoes declaradas dentro do pipeline."], ["[092](#092-map-filter-e-reduce-como-metodos)", "**map, filter e reduce como metodos**", "a mesma logica do pipeline, com metodos de cluster."], ["[093](#093-composicao-de-funcoes)", "**Composicao de funcoes**", "combine acoes pequenas em uma maior."], ["[094](#094-aplicacao-parcial-e-curry)", "**Aplicacao parcial e curry**", "fixe argumentos e gere novas acoes."], ["[095](#095-arcanefunctional)", "**Arcane.Functional**", "use utilitarios funcionais da biblioteca padrao."], ["[096](#096-streams-reativos)", "**Streams reativos**", "observe os itens de um stream conforme chegam."], ["[097](#097-relatorio-com-pipelines)", "**Relatorio com pipelines**", "gere um resumo de vendas por vendedor."], ["[098](#098-pipeline-de-limpeza-de-dados)", "**Pipeline de limpeza de dados**", "normalize uma lista suja de emails."]]}},
  {"h2": "087 · sift (filtro)"},
  {"p": "**Enunciado.** filtre numeros e registros com o operador >>."},
  { code: `nums := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
pares := nums >> sift n: n % 2 is 0
grandes := nums >> sift n: n bigger 7

out pares, grandes
assert pares is [2, 4, 6, 8, 10], "pares"
assert grandes is [8, 9, 10], "maiores que 7"

pessoas := [
    {"nome": "Ana", "idade": 30},
    {"nome": "Bruno", "idade": 17},
    {"nome": "Carla", "idade": 45}
]
adultos := pessoas >> sift p: p["idade"] bigger_eq 18
assert len(adultos) is 2, "dois adultos"
out adultos >> morph p: p["nome"]`, lang: 'df', title: `exercicios/08-pipelines/087_sift.df` },
  {"h2": "088 · morph (transformacao)"},
  {"p": "**Enunciado.** transforme cada elemento de um cluster."},
  { code: `nums := [1, 2, 3, 4]
quadrados := nums >> morph n: n ** 2
textos := nums >> morph n: "item-" + str(n)

out quadrados
out textos

assert quadrados is [1, 4, 9, 16], "quadrados"
assert textos is ["item-1", "item-2", "item-3", "item-4"], "textos"

precos := [100, 200, 300]
com_imposto := precos >> morph p: round(p * 1.15, 2)
assert com_imposto is [115.0, 230.0, 345.0], "com imposto"`, lang: 'df', title: `exercicios/08-pipelines/088_morph.df` },
  {"h2": "089 · distill (reducao)"},
  {"p": "**Enunciado.** reduza um cluster a um unico valor."},
  { code: `nums := [1, 2, 3, 4, 5]

soma := nums >> distill acc, v: acc + v 0
produto := nums >> distill acc, v: acc * v 1
maximo := nums >> distill acc, v: acc bigger v and acc or v 0

out soma, produto, maximo
assert soma is 15, "soma"
assert produto is 120, "produto"
assert maximo is 5, "maximo"

palavras := ["Data", "Forge", "Lang"]
concatenado := palavras >> distill acc, v: acc + v ""
assert concatenado is "DataForgeLang", "concatenacao"
out concatenado`, lang: 'df', title: `exercicios/08-pipelines/089_distill.df` },
  {"h2": "090 · Pipeline encadeado"},
  {"p": "**Enunciado.** combine sift, morph e distill em uma unica expressao."},
  { code: `vendas := [120, 45, 300, 80, 500, 15, 250]

total_grandes := vendas
    >> sift v: v bigger_eq 100
    >> morph v: v * 1.1
    >> distill acc, v: acc + v 0

out "total das vendas grandes com 10%:", round(total_grandes, 2)
assert round(total_grandes, 2) is 1287.0, "pipeline completo"

nomes := ["ana", "BRUNO", "carla", "di"]
formatados := nomes
    >> sift n: n.length() bigger 2
    >> morph n: n.capitalize()
out formatados
assert formatados is ["Ana", "Bruno", "Carla"], "pipeline de texto"`, lang: 'df', title: `exercicios/08-pipelines/090_pipeline_encadeado.df` },
  {"h2": "091 · Pipeline com acao nomeada"},
  {"p": "**Enunciado.** reutilize acoes declaradas dentro do pipeline."},
  { code: `action eh_primo(n):
    given n smaller 2:
        yield no
    i := 2
    persist i * i smaller_eq n:
        given n % i is 0:
            yield no
        i += 1
    yield yes

action ao_quadrado(n):
    yield n * n

nums := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
primos := nums >> sift eh_primo
quadrados_primos := nums >> sift eh_primo >> morph ao_quadrado

out primos
out quadrados_primos
assert primos is [2, 3, 5, 7, 11], "primos"
assert quadrados_primos is [4, 9, 25, 49, 121], "quadrados dos primos"`, lang: 'df', title: `exercicios/08-pipelines/091_pipeline_com_acao.df` },
  {"h2": "092 · map, filter e reduce como metodos"},
  {"p": "**Enunciado.** a mesma logica do pipeline, com metodos de cluster."},
  { code: `nums := [1, 2, 3, 4, 5, 6]

dobros := nums.map(lambda n: n * 2)
impares := nums.filter(lambda n: n % 2 is 1)
soma := nums.reduce(lambda a, b: a + b, 0)

out dobros, impares, soma
assert dobros is [2, 4, 6, 8, 10, 12], "map"
assert impares is [1, 3, 5], "filter"
assert soma is 21, "reduce"

assert nums.every(lambda n: n bigger 0) is yes, "every"
assert nums.some(lambda n: n bigger 5) is yes, "some"
assert nums.find(lambda n: n % 4 is 0) is 4, "find"`, lang: 'df', title: `exercicios/08-pipelines/092_map_filter_reduce.df` },
  {"h2": "093 · Composicao de funcoes"},
  {"p": "**Enunciado.** combine acoes pequenas em uma maior."},
  { code: `action mais_um(x):
    yield x + 1

action dobrar(x):
    yield x * 2

composta := compose(dobrar, mais_um)
encadeada := pipe_fn(mais_um, dobrar)

out composta(5)
out encadeada(5)

assert composta(5) is 12, "compose aplica da direita para a esquerda"
assert encadeada(5) is 12, "pipe aplica da esquerda para a direita"`, lang: 'df', title: `exercicios/08-pipelines/093_composicao_funcoes.df` },
  {"h2": "094 · Aplicacao parcial e curry"},
  {"p": "**Enunciado.** fixe argumentos e gere novas acoes."},
  { code: `action somar3(a, b, c):
    yield a + b + c

soma_com_10 := partial(somar3, 10)
out soma_com_10(5, 2)
assert soma_com_10(5, 2) is 17, "aplicacao parcial"

action multiplicar(a, b):
    yield a * b

triplicar := partial(multiplicar, 3)
assert triplicar(7) is 21, "triplicar"
out [1, 2, 3].map(triplicar)
assert [1, 2, 3].map(triplicar) is [3, 6, 9], "usada em map"`, lang: 'df', title: `exercicios/08-pipelines/094_currying.df` },
  {"h2": "095 · Arcane.Functional"},
  {"p": "**Enunciado.** use utilitarios funcionais da biblioteca padrao."},
  { code: `adopt Arcane.Functional as F

nums := [5, 1, 4, 2, 8, 3]

out F.take_while(lambda n: n bigger 0, nums)
out F.sort_by(lambda n: -n, nums)
out F.group_by(lambda n: n % 2 is 0 and "par" or "impar", nums)
out F.chunk(2, nums)

assert F.sort_by(lambda n: n, nums) is [1, 2, 3, 4, 5, 8], "sort_by"
assert F.chunk(2, nums) is [[5, 1], [4, 2], [8, 3]], "chunk"
assert F.unique_by(lambda n: n % 3, nums) is [5, 1, 3], "unique_by"`, lang: 'df', title: `exercicios/08-pipelines/095_stdlib_functional.df` },
  {"h2": "096 · Streams reativos"},
  {"p": "**Enunciado.** observe os itens de um stream conforme chegam."},
  { code: `recebidos := []
s := stream([10, 20, 30, 40])

observe valor in s:
    given valor bigger 35:
        halt
    recebidos.append(valor)

out recebidos
assert recebidos is [10, 20, 30], "parou em 40"

soma := 0
observe v in [1, 2, 3, 4, 5]:
    given v % 2 is 0:
        skip
    soma += v
assert soma is 9, "somou apenas os impares"
out "soma dos impares:", soma`, lang: 'df', title: `exercicios/08-pipelines/096_observe_stream.df` },
  {"h2": "097 · Relatorio com pipelines"},
  {"p": "**Enunciado.** gere um resumo de vendas por vendedor."},
  { code: `vendas := [
    {"vendedor": "Ana", "valor": 1200},
    {"vendedor": "Bruno", "valor": 800},
    {"vendedor": "Ana", "valor": 300},
    {"vendedor": "Carla", "valor": 2000},
    {"vendedor": "Bruno", "valor": 450}
]

por_vendedor := {}
cycle v in vendas:
    nome := v["vendedor"]
    atual := por_vendedor.get(nome, 0)
    por_vendedor[nome] := atual + v["valor"]

out "=== total por vendedor ==="
cycle par in por_vendedor.items():
    out "  " + par[0].pad_end(8) + "R$ " + str(par[1])

valores := vendas >> morph v: v["valor"]
out "faturamento:", sum(valores)
out "ticket medio:", round(mean(valores), 2)

assert por_vendedor["Ana"] is 1500, "Ana"
assert por_vendedor["Bruno"] is 1250, "Bruno"
assert sum(valores) is 4750, "faturamento"
assert round(mean(valores), 1) is 950.0, "ticket medio"`, lang: 'df', title: `exercicios/08-pipelines/097_pipeline_relatorio.df` },
  {"h2": "098 · Pipeline de limpeza de dados"},
  {"p": "**Enunciado.** normalize uma lista suja de emails."},
  { code: `bruto := ["  ANA@Exemplo.com ", "invalido", "bruno@teste.org", "", "  CARLA@X.COM"]

adopt Arcane.Regex as Regex

limpos := bruto
    >> morph e: e.trim().lower()
    >> sift e: Regex.is_email(e)

out limpos
assert limpos is ["ana@exemplo.com", "bruno@teste.org", "carla@x.com"], "emails limpos"

dominios := limpos >> morph e: e.split("@")[1]
out unique(dominios)
assert unique(dominios) is ["exemplo.com", "teste.org", "x.com"], "dominios"`, lang: 'df', title: `exercicios/08-pipelines/098_pipeline_texto.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/08-pipelines/087_sift.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '087-sift-filtro', text: "087 · sift (filtro)", level: 2 as const }, { id: '088-morph-transformacao', text: "088 · morph (transformacao)", level: 2 as const }, { id: '089-distill-reducao', text: "089 · distill (reducao)", level: 2 as const }, { id: '090-pipeline-encadeado', text: "090 · Pipeline encadeado", level: 2 as const }, { id: '091-pipeline-com-acao-nomeada', text: "091 · Pipeline com acao nomeada", level: 2 as const }, { id: '092-map-filter-e-reduce-como-metodos', text: "092 · map, filter e reduce como metodos", level: 2 as const }, { id: '093-composicao-de-funcoes', text: "093 · Composicao de funcoes", level: 2 as const }, { id: '094-aplicacao-parcial-e-curry', text: "094 · Aplicacao parcial e curry", level: 2 as const }, { id: '095-arcanefunctional', text: "095 · Arcane.Functional", level: 2 as const }, { id: '096-streams-reativos', text: "096 · Streams reativos", level: 2 as const }, { id: '097-relatorio-com-pipelines', text: "097 · Relatorio com pipelines", level: 2 as const }, { id: '098-pipeline-de-limpeza-de-dados', text: "098 · Pipeline de limpeza de dados", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"08 · Pipelines"}
      description={"12 exercícios: sift, morph, distill e composição."}
      href={"/docs/exercicios/08-pipelines"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
