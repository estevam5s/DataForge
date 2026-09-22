// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Muitos dados",
  description: "Quando o arquivo não cabe: ler em pedaços, agregar sem guardar, e quando passar para um banco.",
};

const blocos: Bloco[] = [
  {"p": "Um `Quadro` guarda tudo em memória. Para um arquivo de alguns milhões de linhas, isso ainda funciona; para dezenas de gigabytes, não. Três estratégias, em ordem de esforço."},
  {"table": {"head": ["Estratégia", "Quando", "Com"], "rows": [["**agregar enquanto lê**", "a pergunta é uma soma, uma contagem, uma média", "um `cycle` sobre as linhas, sem guardar"], ["**ler em pedaços**", "cada pedaço é processado sozinho", "`stream action` que emite lotes"], ["**passar para um banco**", "a pergunta muda a cada dia", "SQLite com índice — `Arcane.Database`"]]}},
  { code: `// Agregar enquanto le: memoria constante, qualquer tamanho.
stream action linhas_de(texto):
    cycle linha in texto.lines()[1:]:
        emit linha.split(",")

csv := "loja,valor\\nA,10\\nB,5\\nA,20\\nB,7"
total := {}
cycle campos in linhas_de(csv):
    loja := campos[0]
    total[loja] := (total[loja] ?? 0) + int(campos[1])

assert total is {"A": 30, "B": 12}`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Meça antes de mudar de estratégia", "texto": "`dataforge profile` diz onde o tempo vai. Na maioria dos casos o gargalo não é o tamanho: é um `in` numa lista dentro do laço (O(n²)) — ver [Escolher a estrutura](/docs/big-o/escolher). Trocar a lista por um `set` resolve antes de qualquer banco."}},
  {"p": "Para volume de verdade: [Lago de dados](/docs/tecnicas/lago) e [Parquet](/docs/tecnicas/parquet)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Muitos dados"}
      description={"Quando o arquivo não cabe: ler em pedaços, agregar sem guardar, e quando passar para um banco."}
      href={"/docs/dados/volume"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
