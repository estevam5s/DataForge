import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "08 · Pipelines",
  description: "12 exercícios: `sift`/`morph`/`distill`, composição, currying e streams.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 08`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["087", "**sift (filtro)**", "filtre numeros e registros com o operador >>."], ["088", "**morph (transformacao)**", "transforme cada elemento de um cluster."], ["089", "**distill (reducao)**", "reduza um cluster a um unico valor."], ["090", "**Pipeline encadeado**", "combine sift, morph e distill em uma unica expressao."], ["091", "**Pipeline com acao nomeada**", "reutilize acoes declaradas dentro do pipeline."], ["092", "**map, filter e reduce como metodos**", "a mesma logica do pipeline, com metodos de cluster."], ["093", "**Composicao de funcoes**", "combine acoes pequenas em uma maior."], ["094", "**Aplicacao parcial e curry**", "fixe argumentos e gere novas acoes."], ["095", "**Arcane.Functional**", "use utilitarios funcionais da biblioteca padrao."], ["096", "**Streams reativos**", "observe os itens de um stream conforme chegam."], ["097", "**Relatorio com pipelines**", "gere um resumo de vendas por vendedor."], ["098", "**Pipeline de limpeza de dados**", "normalize uma lista suja de emails."]]}},
  {"h2": "087 · sift (filtro)"},
  {"p": "Filtre numeros e registros com o operador >>."},
  { code: `// Exercicio 087 — sift (filtro)
// Enunciado: filtre numeros e registros com o operador >>.

nums := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
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
out adultos >> morph p: p["nome"]
`, title: `087_sift.df` },
  {"h2": "088 · morph (transformacao)"},
  {"p": "Transforme cada elemento de um cluster."},
  { code: `// Exercicio 088 — morph (transformacao)
// Enunciado: transforme cada elemento de um cluster.

nums := [1, 2, 3, 4]
quadrados := nums >> morph n: n ** 2
textos := nums >> morph n: "item-" + str(n)

out quadrados
out textos

assert quadrados is [1, 4, 9, 16], "quadrados"
assert textos is ["item-1", "item-2", "item-3", "item-4"], "textos"

precos := [100, 200, 300]
com_imposto := precos >> morph p: round(p * 1.15, 2)
assert com_imposto is [115.0, 230.0, 345.0], "com imposto"
`, title: `088_morph.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 10 exercícios deste módulo estão em `exercicios/08-pipelines/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '087--sift-filtro', text: "087 · sift (filtro)", level: 2 as const }, { id: '088--morph-transformacao', text: "088 · morph (transformacao)", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"08 · Pipelines"}
      description={"12 exercícios: `sift`/`morph`/`distill`, composição, currying e streams."}
      href={"/docs/exercicios/08-pipelines"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
