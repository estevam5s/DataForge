import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Comparação com JavaScript",
  description: "O que muda para quem vem de JavaScript ou TypeScript.",
};

const blocos: Bloco[] = [
  {"h2": "A tabela"},
  {"table": {"head": ["JavaScript / TypeScript", "DataForge", "Nota"], "rows": [["`let x = 1`", "`x := 1`", ""], ["`const X = 1`", "`steady X := 1`", ""], ["`console.log(x)`", "`out x`", ""], ["`` `${x}` ``", "`$\"{x}\"`", ""], ["`if`/`else if`/`else`", "`given`/`orif`/`otherwise`", ""], ["`c ? a : b`", "`a given c otherwise b`", "ordem diferente"], ["`switch`/`case`", "`match`/`point`", "sem fall-through"], ["`for (const x of xs)`", "`cycle x in xs:`", ""], ["`for (let i=1; i<=5; i++)`", "`cycle i from 1 to 5:`", ""], ["`while`", "`persist`", ""], ["`do…while`", "`perform … persist`", ""], ["`break`/`continue`", "`halt`/`skip`", ""], ["`function`/`return`", "`action`/`yield`", ""], ["`function*` + `yield`", "`stream action` + `emit`", ""], ["`(x) => e`", "`lambda x: e`", ""], ["`class`/`new`", "`blueprint`/`spawn`", ""], ["`this`", "`self`", ""], ["`super`", "`root`", ""], ["`interface`", "`record` ou `trait`", "record é valor; trait é contrato"], ["`enum` (TS)", "`enum`", ""], ["`import`/`export`", "`adopt`/`relay`", ""], ["`try`/`catch`/`finally`", "`monitor`/`handle`/`ensure`", ""], ["`throw`", "`trigger`", ""], ["`true`/`false`/`null`", "`yes`/`no`/`void`", ""], ["`?.`", "`?.`", "igual"], ["`??`", "`??`", "igual"], ["`...`", "`...`", "igual"], ["`.filter().map().reduce()`", "`>> sift >> morph >> distill`", ""], ["`Math.floor(a/b)`", "`a ~/ b`", ""], ["`@decorator`", "`mark @decorator`", ""], ["`await`", "`await`", "síncrono por enquanto"]]}},
  {"h2": "Semelhanças que ajudam"},
  {"p": "Se você vem de TypeScript, três coisas funcionam quase igual:"},
  { code: `// TypeScript
const {nome, idade} = usuario;
const todos = [...a, ...b];
const config = {...padrao, ...usuario};
const porta = cfg?.servidor?.porta ?? 8080;`, lang: 'text', title: `TypeScript` },
  { code: `{nome, idade} := usuario
todos := [...a, ...b]
config := {...padrao, ...usuario}
porta := cfg?.servidor?.porta ?? 8080`, title: `DataForge` },
  {"h2": "A diferença que mais confunde"},
  {"p": "Em JavaScript, `??` só dispara em `null` e `undefined`. Em DataForge, só em `void` — a mesma ideia. Mas `||` do JavaScript dispara também em `0` e `\"\"`, e **DataForge não tem esse comportamento em `??`**:"},
  { code: `0 ?? 99        # 0   — zero é um valor
"" ?? "x"      # ""  — texto vazio é um valor
no ?? yes      # no  — falso é um valor` },
  {"h2": "Tipagem"},
  {"p": "DataForge é dinamicamente tipado com anotações opcionais — mais próximo de JSDoc que de TypeScript. A diferença: as anotações são verificadas **em tempo de execução também**, não só estaticamente."},
  { code: `action media(nums: Cluster) -> Float:
    yield sum(nums) / len(nums)

media("texto")     # erro na chamada, não só no editor` },
  {"h2": "Traduzindo"},
  { code: `const aprovados = alunos.filter(a => a.nota >= 7);
const media = alunos.reduce((s, a) => s + a.nota, 0) / alunos.length;
console.log(\`\${aprovados.length} aprovados, media \${media.toFixed(2)}\`);`, lang: 'text', title: `JavaScript` },
  { code: `aprovados := alunos >> sift a: a.nota bigger_eq 7
media := alunos >> morph a: a.nota >> distill s, n: s + n 0
out $"{len(aprovados)} aprovados, media {round(media / len(alunos), 2)}"`, title: `DataForge` },
];

const headings = [{ id: 'a-tabela', text: "A tabela", level: 2 as const }, { id: 'semelhancas-que-ajudam', text: "Semelhanças que ajudam", level: 2 as const }, { id: 'a-diferenca-que-mais-confunde', text: "A diferença que mais confunde", level: 2 as const }, { id: 'tipagem', text: "Tipagem", level: 2 as const }, { id: 'traduzindo', text: "Traduzindo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Comparação com JavaScript"}
      description={"O que muda para quem vem de JavaScript ou TypeScript."}
      href={"/docs/faq/javascript"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
