// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O changelog que a superfície escreve",
  description: "Abi.changelog separa quebra de acréscimo, com a dica de migração de cada uma — o esqueleto, e não a nota inteira.",
};

const blocos: Bloco[] = [
  {"p": "Todo release precisa de uma seção no CHANGELOG, e a parte que mais se esquece é justamente a que mais importa: **o que quebrou**. `Abi.changelog` escreve o esqueleto a partir da comparação — cada quebra com a dica do que fazer, cada acréscimo — e deixa para você o porquê."},
  { code: `adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-abi-{randint(100000, 999999)}"
IO.mkdir(pasta)
antes := $"{pasta}/v1.df"
IO.write(antes, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

depois := $"{pasta}/v2.df"
IO.write(depois, "action somar(a, b, c := 0):\\n    yield a + b + c\\naction triplo(x):\\n    yield x * 3\\nrelay somar, triplo\\n")

texto := Abi.changelog(antes, depois, "2.0.0")
out texto
assert texto.starts_with("## 2.0.0")
assert texto.contains("### Quebra compatibilidade")
assert texto.contains("\`dobro\`")                 // o que sumiu
assert texto.contains("### Adicionado")
IO.remove_tree(pasta)`, lang: 'df' },
  {"list": ["**Quebra primeiro.** É o que quem atualiza precisa ler antes de qualquer outra coisa.", "**Com a dica.** \"`dobro` foi removida\" não diz o que fazer; a dica diz (\"mantenha o nome como casca que chama o novo, ou suba a versão maior\").", "**O porquê é seu.** A ferramenta sabe **o que** mudou na superfície; **por que** mudou — e o que isso resolve — só quem escreveu sabe."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O changelog que a superfície escreve"}
      description={"Abi.changelog separa quebra de acréscimo, com a dica de migração de cada uma — o esqueleto, e não a nota inteira."}
      href={"/docs/abi/changelog"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
