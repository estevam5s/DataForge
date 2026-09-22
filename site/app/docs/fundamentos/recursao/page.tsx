// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Recursão",
  description: "Uma ação que chama a si mesma, o caso base, o teto de mil quadros — e as duas saídas.",
};

const blocos: Bloco[] = [
  {"p": "Recursão é resolver um problema resolvendo uma versão menor dele. Toda recursão tem duas partes: o **caso base**, que responde sem chamar ninguém, e o **passo**, que chama a si mesma com algo menor."},
  { code: `action fatorial(n):
    given n smaller_eq 1:
        yield 1                      // caso base
    yield n * fatorial(n - 1)        // passo

assert fatorial(5) is 120

// Percorrer uma arvore e o uso natural.
arvore := {"valor": 1, "filhos": [
    {"valor": 2, "filhos": []},
    {"valor": 3, "filhos": [{"valor": 4, "filhos": []}]}]}

action somar(nodo):          // 'no' e palavra reservada (e o falso)
    total := nodo["valor"]
    cycle f in nodo["filhos"]:
        total += somar(f)
    yield total

assert somar(arvore) is 10`, lang: 'df' },
  {"h2": "O teto, e as duas saídas"},
  {"p": "Cada chamada ocupa um quadro, e o teto é mil. Uma recursão legítima de cinco mil níveis não tem nada de infinita — e mesmo assim bate no teto. Há duas saídas:"},
  { code: `arvore := {"valor": 1, "filhos": [{"valor": 2, "filhos": []}, {"valor": 3, "filhos": [{"valor": 4, "filhos": []}]}]}

// 1. Chamada de cauda: 'yield f(...)' como retorno INTEIRO vira salto,
//    e nao empilha. Testado com 200 mil.
action somar_ate(n, acc := 0):
    given n is 0:
        yield acc
    yield somar_ate(n - 1, acc + n)

assert somar_ate(10000) is 50005000

// 2. Um laco com pilha explicita.
action contar_nos(raiz):
    pilha := [raiz]
    n := 0
    persist len(pilha) bigger 0:
        nodo := pilha.pop()
        n += 1
        cycle f in nodo["filhos"]:
            pilha.append(f)
    yield n

assert contar_nos(arvore) is 4`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`n * fatorial(n - 1)` não é cauda", "texto": "Depois da chamada ainda há uma multiplicação, então o quadro precisa ficar. Só `yield f(...)` **sozinho** é cauda — por isso `somar_ate` leva o acumulador como parâmetro."}},
  {"p": "O custo de uma recursão: [Recorrências](/docs/big-o/recorrencias)."},
];

const headings = [{ id: 'o-teto-e-as-duas-saidas', text: "O teto, e as duas saídas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Recursão"}
      description={"Uma ação que chama a si mesma, o caso base, o teto de mil quadros — e as duas saídas."}
      href={"/docs/fundamentos/recursao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
