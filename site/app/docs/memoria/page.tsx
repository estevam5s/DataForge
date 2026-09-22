// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Memória",
  description: "O coletor sob controle, o layout de um objeto, o escopo e a posse — num runtime que gerencia a memória por você.",
};

const blocos: Bloco[] = [
  {"p": "DataForge roda sobre o CPython, e a memória é gerenciada: ninguém chama `free`. O que se controla é o **coletor** — quando ele roda, e o que ele deixa para trás — e o **protocolo** de um recurso: quem é dono, quem empresta, quem solta."},
  { code: `adopt Arcane.Memoria as Mem

assert Mem.gc_ligado()
Mem.sem_gc(lambda => [i * 2 cycle i in range(1000)])   // um trecho sem pausas do coletor
assert Mem.gc_ligado()                                  // religado, mesmo se a ação falhasse`, lang: 'df' },
  {"cards": [{"href": "/docs/memoria/coletor", "title": "O coletor sob controle", "desc": "ligar, desligar, congelar — e a pausa medida"}, {"href": "/docs/memoria/layout", "title": "O layout de um objeto", "desc": "quanto ocupa, e onde"}, {"href": "/docs/memoria/escopo", "title": "Escopo e tempo de vida", "desc": "quando um valor deixa de existir"}, {"href": "/docs/memoria/posse", "title": "Posse", "desc": "dono exclusivo, empréstimo, contagem"}, {"href": "/docs/memoria/mapa", "title": "Memória: o mapa", "desc": "o que existe, e o que não"}, {"href": "/docs/estruturas", "title": "Estruturas binárias", "desc": "bloco, janela e ponteiro sem FFI"}]},
  {"callout": {"tipo": "nota", "titulo": "Controlar o coletor não é controlar a memória", "texto": "No CPython quem libera é a **contagem de referências**, e ela roda na hora. O coletor existe só para os ciclos. Desligá-lo num trecho curto não vaza memória em geral — só deixa o ciclo para trás, que é o que torna a técnica segura."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Memória"}
      description={"O coletor sob controle, o layout de um objeto, o escopo e a posse — num runtime que gerencia a memória por você."}
      href={"/docs/memoria"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
