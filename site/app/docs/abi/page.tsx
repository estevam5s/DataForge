// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Superfície e contrato",
  description: "O que um módulo oferece é um contrato com quem o usa — e a ferramenta que diz, antes do release, se ele foi quebrado.",
};

const blocos: Bloco[] = [
  {"p": "A **superfície** de um módulo é o que ele exporta com `relay`: nomes, parâmetros, campos. Quem adota o módulo depende exatamente disso. Mudar a superfície é mudar o contrato — e `Arcane.Abi` compara duas versões e diz se a mudança **quebra** quem usava a anterior."},
  { code: `adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-abi-{randint(100000, 999999)}"
IO.mkdir(pasta)
antes := $"{pasta}/v1.df"
IO.write(antes, "action somar(a, b):\\n    yield a + b\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

depois := $"{pasta}/v2.df"
IO.write(depois, "action somar(a, b, c := 0):\\n    yield a + b + c\\naction dobro(x):\\n    yield x * 2\\nrelay somar, dobro\\n")

assert Abi.veredito(antes, depois) is "menor"          // acrescentou, não quebrou
assert Abi.compativel(antes, depois)
IO.remove_tree(pasta)`, lang: 'df' },
  {"cards": [{"href": "/docs/abi/superficie", "title": "A superfície é o contrato", "desc": "o que entra, e o que o relay esconde"}, {"href": "/docs/abi/compatibilidade", "title": "O que quebra", "desc": "as onze regras, uma a uma"}, {"href": "/docs/abi/versao", "title": "A próxima versão", "desc": "calculada da superfície, e não escolhida a olho"}, {"href": "/docs/abi/changelog", "title": "O changelog", "desc": "o esqueleto que a superfície consegue escrever"}, {"href": "/docs/abi/aposentar", "title": "Aposentar sem quebrar", "desc": "renomear com relay … as, e avisar antes de remover"}, {"href": "/docs/abi/ci", "title": "O contrato no CI", "desc": "o release que quebra sem subir a versão maior é reprovado"}, {"href": "/docs/abi/zero-x", "title": "Antes do 1.0", "desc": "o que o 0.x promete, e o que não"}, {"href": "/docs/abi/simbolos", "title": "O mapa de símbolos", "desc": "quem exporta o quê"}, {"href": "/docs/alvos", "title": "Alvos", "desc": "onde um programa roda"}, {"href": "/docs/abi/mapa", "title": "ABI e alvos: o mapa", "desc": "o que existe, e o que não"}]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Superfície e contrato"}
      description={"O que um módulo oferece é um contrato com quem o usa — e a ferramenta que diz, antes do release, se ele foi quebrado."}
      href={"/docs/abi"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
