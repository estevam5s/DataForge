// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Canais entre threads",
  description: "P.canal: receber espera, o produtor rápido para quando a fila enche, e fechar termina o consumidor.",
};

const blocos: Bloco[] = [
  {"p": "Um canal é uma fila entre threads com duas garantias: quem **recebe** espera até chegar algo, e — com capacidade — quem **envia** espera quando a fila enche. A segunda é a que protege a memória: um produtor mais rápido que o consumidor para no `enviar`, em vez de acumular um milhão de itens."},
  { code: `adopt Arcane.Concurrent as P

tarefas := P.canal(2)
feitas := []

action produzir():
    cycle i from 1 to 5:
        tarefas.enviar(i)
    tarefas.fechar()

action consumir():
    persist yes:
        t := tarefas.receber()
        given t is void:                  // fechado e vazio
            halt
        feitas.append(t * 10)

parallel:
    produzir()
    consumir()
assert feitas is [10, 20, 30, 40, 50]`, lang: 'df' },
  {"list": ["**`receber(prazo)`** desiste depois do prazo, em vez de esperar para sempre por um produtor que morreu.", "**`tentar_receber()`** não espera: `void` se estiver vazio.", "**Entre fibras de um laço**, o canal é outro — o que suspende a fibra, e não a thread: ver [Canais entre fibras](/docs/runtime/canais)."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Canais entre threads"}
      description={"P.canal: receber espera, o produtor rápido para quando a fila enche, e fechar termina o consumidor."}
      href={"/docs/concorrencia/canais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
