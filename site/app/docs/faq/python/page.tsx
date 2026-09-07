import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Comparação com Python",
  description: "O que muda para quem vem de Python, lado a lado.",
};

const blocos: Bloco[] = [
  {"h2": "A tabela"},
  {"table": {"head": ["Python", "DataForge", "Nota"], "rows": [["`x = 1`", "`x := 1`", "`=` sozinho não existe"], ["`print(x)`", "`out x`", ""], ["`f\"{x}\"`", "`$\"{x}\"`", ""], ["`if`/`elif`/`else`", "`given`/`orif`/`otherwise`", ""], ["`a if c else b`", "`a given c otherwise b`", "mesma ordem"], ["`match`/`case`", "`match`/`point`", "`when` no lugar de `if`"], ["`for x in xs:`", "`cycle x in xs:`", ""], ["`for i in range(1,6)`", "`cycle i from 1 to 5:`", "**inclusivo**"], ["`while`", "`persist`", ""], ["`break`/`continue`", "`halt`/`skip`", ""], ["`def`/`return`", "`action`/`yield`", ""], ["`yield` (gerador)", "`stream action` + `emit`", "separados de propósito"], ["`lambda x: e`", "`lambda x: e`", "igual"], ["`class`", "`blueprint`", ""], ["`Clas()`", "`spawn Clas()`", ""], ["`self`", "`self`", "igual"], ["`super()`", "`root`", ""], ["`@dataclass(frozen=True)`", "`record`", "imutável por padrão"], ["`Enum`", "`enum`", ""], ["`Protocol` / ABC", "`trait`", ""], ["`import x`", "`adopt x`", ""], ["`from x import y`", "`adopt x.{y}`", ""], ["`__all__`", "`relay`", "de verdade, não convenção"], ["`try`/`except`/`finally`", "`monitor`/`handle`/`ensure`", ""], ["`raise`", "`trigger`", ""], ["`True`/`False`/`None`", "`yes`/`no`/`void`", ""], ["`[e for x in xs if c]`", "`[e cycle x in xs given c]`", ""], ["`{k: v for …}`", "`{k: v cycle …}`", ""], ["`a, *r = xs`", "`a, ...r := xs`", ""], ["`[*a, *b]`", "`[...a, ...b]`", ""], ["`{**a, **b}`", "`{...a, ...b}`", ""], ["`f(*args)`", "`f(...args)`", ""], ["`x if x else y`", "`x ?? y`", "`??` só dispara em `void`"], ["`x and x.y`", "`x?.y`", ""], ["`//`", "`~/`", "em DataForge, `//` é comentário"], ["`@decorator`", "`mark @decorator`", ""], ["`with open(…) as f:`", "`defer` no lugar", "sem gerenciador de contexto"], ["`filter`/`map`/`reduce`", "`>> sift`/`morph`/`distill`", ""]]}},
  {"h2": "O que DataForge tem e Python não"},
  {"list": ["**Pipelines como sintaxe** — `>>` faz parte da gramática", "**`?.` e `??`** — acesso seguro e coalescência nativos", "**Análise estática embutida** — sem instalar mypy", "**`guard`** — pré-condição que sai da ação", "**`retry`** — repetição com handler, sem biblioteca", "**Padrões de record por nome** — `point P(campo := valor)`"]},
  {"h2": "O que Python tem e DataForge não"},
  {"list": ["**Generics** — `list[int]`, `TypeVar`", "**Gerenciador de contexto** — `with`", "**Ecossistema** — numpy, pandas, requests, e os outros 500 mil pacotes", "**LSP e debugger** maduros", "**Desempenho** — mesmo o CPython é mais rápido", "**`async` real** — em DataForge o `await` é síncrono por enquanto"]},
  {"h2": "Traduzindo um script"},
  { code: `# Python
def media(notas):
    if not notas:
        return 0
    return sum(notas) / len(notas)

aprovados = [a for a in alunos if a["nota"] >= 7]
print(f"{len(aprovados)} aprovados, media {media([a['nota'] for a in alunos]):.2f}")`, lang: 'text', title: `Python` },
  { code: `action media(notas: Cluster) -> Float:
    given len(notas) is 0:
        yield 0.0
    yield sum(notas) / len(notas)

aprovados := alunos >> sift a: a["nota"] bigger_eq 7
todas := alunos >> morph a: a["nota"]
out $"{len(aprovados)} aprovados, media {round(media(todas), 2)}"`, title: `DataForge` },
];

const headings = [{ id: 'a-tabela', text: "A tabela", level: 2 as const }, { id: 'o-que-dataforge-tem-e-python-nao', text: "O que DataForge tem e Python não", level: 2 as const }, { id: 'o-que-python-tem-e-dataforge-nao', text: "O que Python tem e DataForge não", level: 2 as const }, { id: 'traduzindo-um-script', text: "Traduzindo um script", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Comparação com Python"}
      description={"O que muda para quem vem de Python, lado a lado."}
      href={"/docs/faq/python"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
