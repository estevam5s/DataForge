// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ordenação",
  description: "Por comparação é O(n log n) no melhor caso; por contagem, O(n + k) — e o que é estabilidade.",
};

const blocos: Bloco[] = [
  {"p": "Todo algoritmo que ordena **comparando** pares precisa de Ω(n log n) comparações no pior caso — é um limite matemático, não uma falta de esperteza. A única forma de ir abaixo é **não comparar**: contar."},
  { code: `adopt Arcane.Algoritmos as Alg

// Merge sort: O(n log n), estavel.
pedidos := [
    {"cliente": "bia", "valor": 50},
    {"cliente": "ana", "valor": 30},
    {"cliente": "bia", "valor": 10},
    {"cliente": "ana", "valor": 20}]
por_cliente := Alg.ordenar_mesclando(pedidos, lambda p: p["cliente"])
// Estavel: dentro de 'ana', a ordem original (30 antes de 20) ficou.
assert (por_cliente >> morph p: p["valor"]) is [30, 20, 50, 10]

// Counting sort: O(n + k), so inteiros, e so quando a faixa k e pequena.
notas := [7, 3, 9, 3, 10, 0, 7]
assert Alg.ordenar_contando(notas) is [0, 3, 3, 7, 7, 9, 10]`, lang: 'df' },
  {"table": {"head": ["Algoritmo", "Tempo", "Espaço", "Estável", "Quando"], "rows": [["`sorted` (Timsort)", "O(n log n)", "O(n)", "sim", "o padrão — e rápido em dados quase ordenados"], ["`ordenar_mesclando`", "O(n log n)", "O(n)", "sim", "quando se quer ver o algoritmo"], ["`ordenar_contando`", "O(n + k)", "O(k)", "sim", "inteiros numa faixa pequena (notas, idades)"]]}},
  {"callout": {"tipo": "dica", "titulo": "Estabilidade é o que permite ordenar por dois critérios", "texto": "Ordene primeiro pelo critério **secundário** e depois pelo principal, com um algoritmo estável: os empates do principal mantêm a ordem do secundário. Sem estabilidade, a segunda ordenação embaralha a primeira."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Ordenação"}
      description={"Por comparação é O(n log n) no melhor caso; por contagem, O(n + k) — e o que é estabilidade."}
      href={"/docs/big-o/ordenacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
