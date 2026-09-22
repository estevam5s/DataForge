// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A próxima versão, calculada",
  description: "Abi.proxima_versao compara as duas superfícies e diz 2.0.0, 1.5.0 ou 1.4.3 — com o porquê.",
};

const blocos: Bloco[] = [
  {"p": "O versionamento semântico é uma promessa: a **maior** sobe quando algo quebra, a **menor** quando algo entra sem quebrar, a **correção** quando a superfície não muda. A promessa só vale se o número for **calculado**; escolhido a olho, ele sobe menor numa quebra — e o `^1.4` de todo mundo que depende do pacote puxa a versão que quebra."},
  { code: `adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-abi-{randint(100000, 999999)}"
IO.mkdir(pasta)
antes := $"{pasta}/v1.df"
IO.write(antes, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

quebra := $"{pasta}/quebra.df"
IO.write(quebra, "action somar(a, b):\\n    yield a + b\\nrelay somar\\n")
acrescimo := $"{pasta}/acrescimo.df"
IO.write(acrescimo, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\naction triplo(x):\\n    yield x * 3\\nrelay somar, dobro, triplo\\n")

p := Abi.proxima_versao("1.4.2", antes, quebra)
assert p["proxima"] is "2.0.0"
out p["porque"]

assert Abi.proxima_versao("1.4.2", antes, acrescimo)["proxima"] is "1.5.0"
assert Abi.proxima_versao("1.4.2", antes, antes)["proxima"] is "1.4.3"
IO.remove_tree(pasta)`, lang: 'df' },
  {"table": {"head": ["Veredito", "Quando", "1.4.2 vira"], "rows": [["`maior`", "um nome sumiu, um parâmetro obrigatório entrou, um parâmetro mudou de nome", "2.0.0"], ["`menor`", "um nome novo, um parâmetro opcional novo", "1.5.0"], ["`correcao`", "a superfície é a mesma", "1.4.3"], ["`desconhecido`", "uma das versões não compila", "não calcula — `proxima` é `void`"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Renomear parâmetro é quebra", "texto": "A chamada com nome existe aqui — `somar(a := 1, b := 2)` —, então o **nome** do parâmetro é contrato, e não só a posição. Uma ferramenta feita para C não teria esta regra."}},
  {"p": "A superfície vê o que é **visível**. Uma mudança de comportamento com a mesma assinatura — a ação passa a arredondar diferente — é quebra, e só um teste pega. O cálculo é o piso, não o teto."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"A próxima versão, calculada"}
      description={"Abi.proxima_versao compara as duas superfícies e diz 2.0.0, 1.5.0 ou 1.4.3 — com o porquê."}
      href={"/docs/abi/versao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
