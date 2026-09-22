// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testes unitários",
  description: "O que é uma unidade, a forma preparar-agir-conferir, e um teste por razão de falhar.",
};

const blocos: Bloco[] = [
  {"p": "Uma unidade é o menor pedaço de comportamento que faz sentido sozinho — quase sempre uma ação ou um método. O teste unitário a exercita **sem** o que é lento, caro ou de fora: sem rede, sem disco, sem relógio de verdade."},
  {"h2": "Preparar, agir, conferir"},
  { code: `adopt Arcane.Crucible

action desconto(total, cliente):
    given cliente["vip"]:
        yield total * 0.1
    given total bigger_eq 200:
        yield total * 0.05
    yield 0

crucible "desconto":
    trial "vip ganha 10% em qualquer valor":
        // preparar
        cliente := {"vip": yes}
        // agir
        d := desconto(50, cliente)
        // conferir
        expect d is 5.0

    trial "comum ganha 5% a partir de 200":
        expect desconto(200, {"vip": no}) is 10.0

    trial "comum abaixo de 200 nao ganha nada":
        expect desconto(199.99, {"vip": no}) is 0

r := Crucible.run()
assert r["falhou"] is 0 and r["passou"] is 3`, lang: 'df' },
  {"h2": "As cinco regras"},
  {"table": {"head": ["Regra", "Sem ela"], "rows": [["**uma razão para falhar** por teste", "o teste cai e não se sabe qual das quatro coisas quebrou"], ["o **nome** diz o comportamento", "`teste_desconto_3` falha, e é preciso ler o corpo para saber o quê"], ["**sem lógica** no teste (sem `given`, sem laço)", "o teste passa a precisar de teste"], ["**independente** da ordem", "o teste 7 só passa depois do 6, e rodar sozinho falha"], ["**rápido** (milissegundos)", "ninguém roda a suíte antes do commit, e ela para de proteger"]]}},
  {"h2": "Os limites valem mais que o meio"},
  {"p": "O bug mora na fronteira: `199.99` e `200` dizem mais sobre `desconto` que `150` e `500`. Para cada `bigger_eq`, teste o valor exato e o imediatamente abaixo."},
  {"callout": {"tipo": "atencao", "titulo": "Não teste a implementação", "texto": "Um teste que confere que `desconto` chamou `round` duas vezes quebra na primeira refatoração que não mudou nada. Confira o **que** sai, não **como** saiu — dublês de interação são para fronteiras (rede, banco), não para o miolo."}},
  {"p": "Continue em [Parametrizados](/docs/testes/parametrizados) e [Dublês](/docs/crucible/dubles)."},
];

const headings = [{ id: 'preparar-agir-conferir', text: "Preparar, agir, conferir", level: 2 as const }, { id: 'as-cinco-regras', text: "As cinco regras", level: 2 as const }, { id: 'os-limites-valem-mais-que-o-meio', text: "Os limites valem mais que o meio", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testes unitários"}
      description={"O que é uma unidade, a forma preparar-agir-conferir, e um teste por razão de falhar."}
      href={"/docs/testes/unitarios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
