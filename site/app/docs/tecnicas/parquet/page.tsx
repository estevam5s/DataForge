// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lago.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Parquet",
  description: "O formato colunar, escrito e lido em DataForge — sem pyarrow, e interoperável com ele.",
};

const blocos: Bloco[] = [
  {"p": "**Parquet** é o formato em que os dados de verdade vivem. `Arcane.Lago` o escreve e o lê em Python puro: um arquivo gerado aqui é lido pelo pandas, pelo DuckDB e pelo Spark, e um arquivo gerado por eles é lido aqui."},
  { code: `adopt Arcane.Lago as L

L.gravar_parquet("vendas.parquet", linhas)
L.ler_parquet("vendas.parquet")
L.ler_parquet("vendas.parquet", ["id", "valor"])   // só duas colunas
L.esquema_parquet("vendas.parquet")                // sem ler os dados`, lang: 'df' },
  {"h2": "Por que colunar"},
  {"p": "Um CSV guarda linha a linha. Para somar uma coluna de 40 milhões de linhas, o disco entrega as outras trinta junto — e elas são jogadas fora. O Parquet guarda **coluna a coluna**: ler uma coluna lê só ela."},
  { code: `// 50.000 linhas, 4 colunas
L.ler_parquet("grande.parquet")            // 0,05 s
L.ler_parquet("grande.parquet", ["id"])    // 0,02 s — 2,9× mais rápido`, lang: 'df' },
  {"p": "E valores do mesmo tipo, lado a lado, comprimem muito melhor. Uma coluna de datas repetidas ou de categorias encolhe uma ordem de grandeza; a mesma informação espalhada por linhas, não."},
  {"h2": "O formato, por dentro"},
  { code: `PAR1                       ← marca de abertura
[dados da coluna 1]        ← páginas, uma por bloco de valores
[dados da coluna 2]
…
[metadados em Thrift]      ← esquema, onde cada coluna começa
<4 bytes: tamanho deles>
PAR1                       ← marca de fechamento`, lang: 'text' },
  {"p": "Os metadados ficam no **fim**, e não no começo. É o que permite escrever um arquivo sem saber de antemão quantas linhas ele terá — e é por isso que o leitor busca o fim primeiro."},
  {"callout": {"tipo": "nota", "titulo": "Thrift compact, escrito à mão", "texto": "Os metadados usam o protocolo Thrift compact: inteiros em zigzag varint, campos por delta de id, estruturas aninhadas. Não há biblioteca — é a parte que mais parece arbitrária e a que menos pode errar por um byte. Um deslocamento de um único byte no rodapé faz o pyarrow recusar o arquivo inteiro sem dizer onde."}},
  {"h2": "Tipos"},
  {"table": {"head": ["DataForge", "Parquet", "Lido como"], "rows": [["`Integer`", "INT64", "`int64`"], ["`Number`", "DOUBLE", "`double`"], ["`String`", "BYTE_ARRAY (UTF8)", "`string`"], ["`Boolean`", "BOOLEAN", "`bool`"], ["`void`", "nível de definição", "`null`"]]}},
  {"p": "O tipo sai dos **valores**, e um inteiro grande demais para 64 bits sobe para `DOUBLE`. Misturar tipos numa coluna é o que mais quebra na leitura — o Parquet é tipado, e o CSV que o originou não era."},
  {"h2": "Nulos custam quando existem"},
  {"p": "Uma coluna sem nulo nenhum é declarada **REQUIRED**, e não carrega níveis de definição. A que tem nulo é **OPTIONAL**, e paga por isso. Declarar tudo como opcional custaria os níveis à toa em toda coluna."},
  {"h2": "Dicionário"},
  {"p": "A maioria dos Parquet do mundo é escrita com codificação por **dicionário**: a página guarda índices, e os valores distintos ficam numa página à parte. Uma coluna de cinco categorias vira 3 bits por linha."},
  {"p": "Nós escrevemos PLAIN e lemos os dois — ler só PLAIN leria quase nada do que existe por aí."},
  {"h2": "O que ainda não lemos"},
  {"table": {"head": ["Compressão", "Estado"], "rows": [["sem compressão", "**lê e escreve**"], ["gzip", "**lê e escreve** (o padrão)"], ["snappy, zstd, brotli, lz4", "recusado, com o nome da compressão na mensagem"]]}},
  {"p": "Gzip está na biblioteca padrão do Python; as outras exigiriam dependência, e a linguagem não tem nenhuma. Quando o arquivo vem comprimido de outro jeito, a mensagem diz qual e como regravar."},
];

const headings = [{ id: 'por-que-colunar', text: "Por que colunar", level: 2 as const }, { id: 'o-formato-por-dentro', text: "O formato, por dentro", level: 2 as const }, { id: 'tipos', text: "Tipos", level: 2 as const }, { id: 'nulos-custam-quando-existem', text: "Nulos custam quando existem", level: 2 as const }, { id: 'dicionario', text: "Dicionário", level: 2 as const }, { id: 'o-que-ainda-nao-lemos', text: "O que ainda não lemos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Parquet"}
      description={"O formato colunar, escrito e lido em DataForge — sem pyarrow, e interoperável com ele."}
      href={"/docs/tecnicas/parquet"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
