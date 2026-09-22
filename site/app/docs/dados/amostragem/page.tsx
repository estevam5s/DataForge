// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Amostrar",
  description: "amostra com semente, e por que a amostra reproduzível é a única que serve.",
};

const blocos: Bloco[] = [
  {"p": "Trabalhar com uma amostra é o que torna possível explorar um arquivo de dez milhões de linhas — e só serve se a mesma análise, rodada amanhã, escolher **as mesmas** linhas. Por isso a amostra aceita uma semente."},
  { code: `adopt Arcane.Quadro as Q

clientes := Q.de_colunas({"id": range(1, 1001)})
a := clientes.amostra(5, 42)
b := clientes.amostra(5, 42)
assert a.coluna("id") is b.coluna("id")           // mesma semente, mesmas linhas
assert a.altura() is 5
out a.coluna("id")`, lang: 'df' },
  {"table": {"head": ["Quero", "Faça"], "rows": [["explorar rápido", "`amostra(1000, semente)`"], ["um relatório que outra pessoa refaz", "a **mesma** semente, escrita no relatório"], ["treinar e testar um modelo", "`Cortex.dividir(dados, 0.2, semente, alvo)` — estratificado pela classe"], ["as primeiras linhas para olhar a forma", "`topo(5)` — e não confundir com amostra"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`topo` não é amostra", "texto": "As primeiras linhas de um arquivo costumam ser as mais antigas, de um único dia, de um único lote. Um padrão que aparece no topo pode não existir no resto. Para olhar a forma, `topo`; para tirar conclusão, `amostra`."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Amostrar"}
      description={"amostra com semente, e por que a amostra reproduzível é a única que serve."}
      href={"/docs/dados/amostragem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
