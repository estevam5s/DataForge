// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Números",
  description: "Integer, Float e Decimal — a divisão, o arredondamento, e o 0,1 + 0,2.",
};

const blocos: Bloco[] = [
  {"p": "Três tipos de número, e cada um existe por um motivo. **Integer** é exato e sem limite de tamanho. **Float** é rápido e aproximado. **Decimal** é exato com casas — o que dinheiro precisa."},
  { code: `assert typeof(7) is "Integer"
assert typeof(7.0) is "Float"
assert typeof(7.0d) is "Decimal"

assert 2 ** 100 is 1267650600228229401496703205376    // inteiro nao estoura
assert 7 / 2 is 3.5          // '/' sempre da Float
assert 7 ~/ 2 is 3           // divisao inteira
assert -7 ~/ 2 is -4         // arredonda para BAIXO, e nao para o zero
assert 7 % 3 is 1
assert 1_000_000 is 1000000  // o '_' e so para ler`, lang: 'df' },
  {"h2": "O 0,1 + 0,2"},
  { code: `adopt Arcane.Decimal as Dec

assert 0.1 + 0.2 isnt 0.3                    // Float: aproximado
assert 0.1d + 0.2d is 0.3d                   // Decimal: exato
assert Dec.texto(Dec.soma([19.99d, 0.01d])) is "20.00"
out 0.1 + 0.2`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Dinheiro é Decimal", "texto": "Float guarda 0,1 como uma fração binária que não fecha — é por isso que `0.1 + 0.2` dá `0.30000000000000004`. Num total de pedido, esse erro aparece como um centavo a mais. Use o literal `19.99d`, e misturar Decimal com Float numa conta é **recusado** de propósito."}},
  {"h2": "Arredondar"},
  { code: `adopt Arcane.Decimal as Dec

assert round(2.675, 2) is 2.67          // Float: 2.675 e na verdade 2.67499…
assert Dec.texto(Dec.arredondar(2.675d, 2)) is "2.68"   // Decimal: o que se espera
assert floor(-2.5) is -3 and ceil(-2.5) is -2`, lang: 'df' },
  {"table": {"head": ["Quero", "Use"], "rows": [["contar, indexar, somar inteiros", "Integer"], ["medir, calcular estatística, ciência", "Float"], ["dinheiro, imposto, qualquer coisa que se concilie", "Decimal (`19.99d`)"]]}},
];

const headings = [{ id: 'o-01-02', text: "O 0,1 + 0,2", level: 2 as const }, { id: 'arredondar', text: "Arredondar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Números"}
      description={"Integer, Float e Decimal — a divisão, o arredondamento, e o 0,1 + 0,2."}
      href={"/docs/fundamentos/numeros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
