// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_e_seguranca.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A pilha",
  description: "Profundidade, teto e quadros — a pilha tinha limite e não tinha como ser perguntada.",
};

const blocos: Bloco[] = [
  {"p": "O teto de quadros é **mil**, e recursão legítima o atinge: uma travessia de árvore de cinco mil nós não tem nada de infinita. Quem a escreve precisa saber de quanto é o teto **antes** de bater nele."},
  { code: `adopt Arcane.Inicio as I

action folha():
    yield I.pilha()

action tronco():
    yield folha()

p := tronco()
assert p["profundidade"] bigger_eq 2
assert p["restante"] is p["limite"] - p["profundidade"]`, lang: 'df' },
  { code: `adopt Arcane.Inicio as I

action quem():
    yield [q["acao"] cycle q in I.quadros()]

assert "quem" in quem()`, lang: 'df' },
  {"h2": "Ajustar o teto"},
  { code: `adopt Arcane.Inicio as I

antes := I.limite_da_pilha()
I.limite_da_pilha(300)
assert I.pilha()["limite"] is 300
I.limite_da_pilha(antes)`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Subir demais é recusado, e o motivo é concreto", "texto": "Cada chamada desta linguagem gasta **vários** quadros do CPython. Um teto alto demais troca uma mensagem clara (\"a recursão passou de mil quadros, e aqui estão as duas saídas\") por um `RecursionError` cru do Python — que não fala desta linguagem e não diz o que fazer."}},
  {"p": "As duas saídas que a mensagem do erro traz continuam sendo as certas: `yield f(…)` como retorno **inteiro** vira salto e **não tem teto** (testado com 200 mil), ou um `cycle` com pilha explícita."},
  {"table": {"head": ["Item da literatura", "Aqui"], "rows": [["stack frames", "`I.quadros()` — ação, linha e arquivo de cada um"], ["stack overflow detection", "o teto de quadros, com mensagem que diz as duas saídas"], ["coroutine / fiber stacks", "as [fibras](/docs/runtime/fibras) são **sem pilha**: o contexto é o quadro do gerador"], ["stack probes, stack guards, stack growth", "**não se aplica**: quem gerencia a pilha é o CPython"]]}},
];

const headings = [{ id: 'ajustar-o-teto', text: "Ajustar o teto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A pilha"}
      description={"Profundidade, teto e quadros — a pilha tinha limite e não tinha como ser perguntada."}
      href={"/docs/partida/pilha"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
