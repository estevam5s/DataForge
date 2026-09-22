// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Achar na biblioteca padrão",
  description: "Os módulos Arcane, os apelidos, e como descobrir o que existe sem sair do terminal.",
};

const blocos: Bloco[] = [
  {"p": "A biblioteca padrão vem junto com a linguagem, sem instalar nada. Cada módulo tem um nome oficial (`Arcane.Algoritmos`) e apelidos curtos (`Algoritmos`, `Algorithms`) — os três chegam ao **mesmo** módulo."},
  { code: `adopt Arcane.Algoritmos as A
adopt Algoritmos as B
assert A.crivo(10) is B.crivo(10)
out A.__name__           // Arcane.Algoritmos, venha por onde vier`, lang: 'df' },
  { code: `dataforge repl
> :modules                # a lista de modulos
> :doc Arcane.Quadro      # os simbolos de um

dataforge custo src/      # o que cada 'adopt' traz junto`, lang: 'bash' },
  {"table": {"head": ["Preciso de…", "Módulo"], "rows": [["tabela de dados", "`Arcane.Quadro`"], ["banco de dados", "`Arcane.Database`, `Forge`"], ["HTTP (cliente)", "`Arcane.Http`; entre serviços, `Arcane.Malha`"], ["site ou API", "`Kiln`"], ["algoritmo clássico", "`Arcane.Algoritmos`"], ["dinheiro exato", "`Arcane.Decimal`"], ["segurança, LGPD, integridade", "`Arcane.Seguranca`, `Arcane.Privacidade`, `Arcane.Integridade`"], ["GitHub", "`Arcane.GitHub`"]]}},
  {"p": "Todos os módulos, com as assinaturas: [Biblioteca Arcane](/docs/biblioteca)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Achar na biblioteca padrão"}
      description={"Os módulos Arcane, os apelidos, e como descobrir o que existe sem sair do terminal."}
      href={"/docs/modulos/biblioteca-padrao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
