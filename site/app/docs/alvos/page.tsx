// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/abi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Alvos",
  description: "Onde um programa roda — lido dos adopt, antes de rodar — e o que WebAssembly quer dizer aqui.",
};

const blocos: Bloco[] = [
  {"p": "Um programa que adota `Arcane.C` não roda no navegador; um que adota `Arcane.OS.fork` não roda no Windows. `Arcane.Alvo` lê os `adopt` do arquivo e responde, antes de rodar, em quais alvos ele funciona — e o motivo de cada recusa."},
  { code: `adopt Arcane.Alvo as Alvo

assert len(Alvo.alvos()) bigger 0
out Alvo.alvos()`, lang: 'df' },
  {"cards": [{"href": "/docs/alvos/portabilidade", "title": "Onde este programa roda", "desc": "os perfis de alvo, e o que cada um recusa"}, {"href": "/docs/alvos/wasm", "title": "WebAssembly, com precisão", "desc": "rodar em WASM existe; compilar para WASM, não"}, {"href": "/docs/abi/mapa", "title": "ABI e alvos: o mapa", "desc": "o que existe, e o que não"}]},
  {"callout": {"tipo": "nota", "titulo": "A leitura é de um arquivo", "texto": "Um módulo alcançado **indiretamente** — pelo `adopt` de um `adopt` — não aparece. `roda` quer dizer \"não achei impedimento por esta via\", e `Alvo.limites()` diz isso em execução."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Alvos"}
      description={"Onde um programa roda — lido dos adopt, antes de rodar — e o que WebAssembly quer dizer aqui."}
      href={"/docs/alvos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
