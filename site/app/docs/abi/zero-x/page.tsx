// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Antes do 1.0",
  description: "O 0.x anuncia que a API ainda não assentou: quebra sobe o menor, acréscimo sobe a correção.",
};

const blocos: Bloco[] = [
  {"p": "Pelo versionamento semântico, qualquer coisa pode mudar antes do 1.0. Na prática, os gerenciadores de pacote (Cargo, npm) tratam o 0.x com uma regra própria: o **menor** faz o papel do maior. `^0.4.2` aceita 0.4.9, mas não 0.5.0. `Abi.proxima_versao` segue a mesma convenção:"},
  { code: `adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-abi-{randint(100000, 999999)}"
IO.mkdir(pasta)
antes := $"{pasta}/v1.df"
IO.write(antes, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

quebra := $"{pasta}/quebra.df"
IO.write(quebra, "action somar(a, b):\\n    yield a + b\\nrelay somar\\n")
assert Abi.proxima_versao("0.4.2", antes, quebra)["proxima"] is "0.5.0"    // não 1.0.0
assert Abi.proxima_versao("0.4.2", antes, antes)["proxima"] is "0.4.3"
IO.remove_tree(pasta)`, lang: 'df' },
  {"table": {"head": ["Mudança", "0.x", "1.x em diante"], "rows": [["quebra", "0.4 → **0.5**", "1.4 → **2.0**"], ["acréscimo", "0.4.2 → 0.4.3", "1.4 → 1.5"], ["correção", "0.4.2 → 0.4.3", "1.4.2 → 1.4.3"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Por que não pular para o 1.0", "texto": "Uma quebra no 0.x não deveria ir para 1.0 sozinha: o 1.0 é uma **promessa** de estabilidade, e fazê-la por causa de uma quebra — e não porque a API assentou — é prometer sem querer. Subir para 1.0 é decisão de quem mantém, e nenhuma ferramenta a toma."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Antes do 1.0"}
      description={"O 0.x anuncia que a API ainda não assentou: quebra sobe o menor, acréscimo sobe a correção."}
      href={"/docs/abi/zero-x"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
