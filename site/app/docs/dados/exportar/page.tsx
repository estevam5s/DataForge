// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Exportar",
  description: "CSV, JSON, planilha e banco — e o formato que cada destino espera.",
};

const blocos: Bloco[] = [
  {"p": "O fim de todo pipeline de dados é um arquivo que outra ferramenta vai ler. Cada destino tem uma expectativa, e errar a expectativa produz o erro mais irritante que existe: o arquivo abre, e está errado."},
  { code: `adopt Arcane.Quadro as Q
adopt Arcane.IO as IO
adopt Arcane.OS as OS

q := Q.de_vaults([{"produto": "Cafe", "preco": 18.5}, {"produto": "=SOMA(A1)", "preco": 1}])
pasta := $"{OS.temp_dir()}/df-exp-{randint(100000, 999999)}"
IO.mkdir(pasta)

q.para_csv($"{pasta}/produtos.csv")
q.para_csv($"{pasta}/produtos-br.csv", ";")       // o Excel em portugues espera ';'
texto := IO.read($"{pasta}/produtos.csv")
out texto
assert "Cafe" in texto

volta := Q.de_csv($"{pasta}/produtos.csv")
assert volta.altura() is 2
IO.remove_tree(pasta)`, lang: 'df' },
  {"table": {"head": ["Destino", "Use", "O detalhe que quebra"], "rows": [["Excel em português", "`para_csv(caminho, \";\")`", "com `,` ele junta tudo numa coluna"], ["outra API", "`para_json()`", "datas como texto ISO; `void` vira `null`"], ["planilha de verdade", "`Arcane.Excel`", "tipos e várias abas; fórmula é gravada, não calculada"], ["banco", "`Database.upsert_many`", "o CSV que chega de novo duplica — use upsert"]]}},
  {"callout": {"tipo": "perigo", "titulo": "Uma célula que começa com `=` é executada", "texto": "O Excel executa a célula que começa com `=`, `+`, `-` ou `@` — um nome de produto `=HYPERLINK(...)` vira link ativo na planilha de quem abriu. Para CSV que alguém vai abrir no Excel, passe o texto por `Seguranca.escapar_csv` — ver [Entrada e saída](/docs/seguranca/entrada)."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Exportar"}
      description={"CSV, JSON, planilha e banco — e o formato que cada destino espera."}
      href={"/docs/dados/exportar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
