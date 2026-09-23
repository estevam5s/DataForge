// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Comparação com TypeScript",
  description: "Dois sistemas de tipos com filosofias diferentes: um apaga na compilação, o outro confere também em execução.",
};

const blocos: Bloco[] = [
  {"p": "A comparação certa não é de sintaxe — é de **onde o tipo vive**. O TypeScript apaga tudo antes de rodar: o tipo é um contrato entre quem escreve e quem lê, e no `JSON.parse` ele acaba. Em DataForge o tipo declarado é conferido **também na fronteira em execução**, e é por isso que ele pega o que um `any` mal colocado deixa passar."},
  {"h2": "A tabela"},
  {"table": {"head": ["TypeScript", "DataForge", "Nota"], "rows": [["`type Id = number`", "`type Id := Integer`", "alias nos dois"], ["`type N = number \\| string`", "`type N := Integer \\| String`", "união nos dois"], ["`A & B`", "`A & B`", "interseção nos dois"], ["*branded type* por convenção", "`opaque type Cpf := String`", "aqui é **mecanismo**, não convenção"], ["— (não existe)", "`Integer where valor bigger 0`", "refinamento **conferido**"], ["`function f<T>(x: T): T`", "`action f<T>(x: T) -> T`", "sem limite, nenhum dos dois cobra"], ["`<T extends number>`", "`<T extends Number>`", "cobrado nas duas metades"], ["`interface`", "`trait`", ""], ["`readonly` / `as const`", "`record`", "imutável por construção"], ["`enum`", "`enum`", "com método, aqui"], ["`x?.y` / `x ?? y`", "`x?.y` / `x ?? y`", "iguais"], ["`tsc --noEmit`", "`dataforge check`", "embutido, sem instalar nada"], ["`as any`", "não anotar", "o analisador cala, e isso é dito"]]}},
  {"h2": "A diferença que mais aparece"},
  { code: `type Positivo := Integer where valor bigger 0

action cobrar(v: Positivo) -> Integer:
    yield v * 100

// Isto passa: 7 satisfaz a regra.
assert cobrar(7) is 700

// E isto e RECUSADO em execucao, nao so no editor — que e o que um
// 'as any' do TypeScript nao impede.
recusou := no
monitor:
    cobrar(0 - 5)
handle Error as e:
    recusou := yes
assert recusou
out "o refinamento vale onde o dado chega de fora"
`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "A prova roda num avaliador puro", "texto": "A regra de um `where` é código de quem escreveu, e o analisador **não pode executar código arbitrário** para decidir se acusa. Por isso ela é avaliada numa lista fechada de funções: o que sai dessa lista faz o `check` calar, e a conferência acontece em execução."}},
  {"h2": "O que o TypeScript tem e DataForge não"},
  {"list": ["**Tipos condicionais e mapeados** — `T extends U ? A : B`, `Partial<T>`, `Record<K,V>`.", "**Inferência de fluxo tão fina quanto** — o *narrowing* do TS por `typeof` e `in` é mais completo.", "**Tipos literais de template** — `` `on${Capitalize<E>}` ``.", "**Ecossistema de tipos** — o DefinitelyTyped não tem equivalente aqui."]},
  {"h2": "O que DataForge tem e o TypeScript não"},
  {"list": ["**Refinamento conferido** (`where`) — no TS é convenção e uma função guarda.", "**Tipo opaco de verdade** — o *branded type* do TS some na compilação.", "**O tipo atravessa `adopt`** — a aridade **e** os tipos dos parâmetros são conferidos entre arquivos, antes de rodar.", "**A conferência em execução** — o tipo não desaparece quando o dado vem de um JSON."]},
  {"cards": [{"href": "/docs/faq/tipos", "title": "Tipos", "desc": "o que é conferido, e quando"}, {"href": "/docs/tipos", "title": "O sistema de tipos", "desc": "o guia"}, {"href": "/docs/faq/javascript", "title": "Comparação com JavaScript", "desc": "a sintaxe, lado a lado"}]},
];

const headings = [{ id: 'a-tabela', text: "A tabela", level: 2 as const }, { id: 'a-diferenca-que-mais-aparece', text: "A diferença que mais aparece", level: 2 as const }, { id: 'o-que-o-typescript-tem-e-dataforge-nao', text: "O que o TypeScript tem e DataForge não", level: 2 as const }, { id: 'o-que-dataforge-tem-e-o-typescript-nao', text: "O que DataForge tem e o TypeScript não", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Comparação com TypeScript"}
      description={"Dois sistemas de tipos com filosofias diferentes: um apaga na compilação, o outro confere também em execução."}
      href={"/docs/faq/typescript"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
