// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Partida e fim",
  description: "O que acontece antes da primeira linha e depois da última — e o sinal que chega no meio.",
};

const blocos: Bloco[] = [
  {"p": "Um programa não começa na primeira linha nem termina na última. Antes, há a partida: módulos carregados, a pilha reservada, o ambiente lido. Depois — ou no meio —, há o fim: o `docker stop`, o Ctrl+C, o deploy que troca o processo. Um programa que ignora o fim perde o que estava na memória."},
  { code: `adopt Arcane.Inicio as Inicio

Inicio.ao_encerrar(lambda => out "conexões fechadas")
assert not Inicio.encerrando()
out "trabalhando"`, lang: 'df' },
  {"cards": [{"href": "/docs/partida/inicio", "title": "Antes da primeira linha", "desc": "as fases da partida, medidas"}, {"href": "/docs/partida/encerrar", "title": "Encerrar em ordem", "desc": "SIGTERM, Ctrl+C e os finalizadores"}, {"href": "/docs/partida/codigos-de-saida", "title": "Código de saída", "desc": "0, 1, 2 e 128 + sinal"}, {"href": "/docs/partida/argumentos", "title": "Argumentos", "desc": "a linha de comando declarada, com ajuda gerada"}, {"href": "/docs/partida/ambiente", "title": "Ambiente e configuração", "desc": "variáveis, padrões e segredos"}, {"href": "/docs/partida/conteineres", "title": "Dentro de um contêiner", "desc": "PID 1, o prazo do docker stop e a sonda"}, {"href": "/docs/partida/por-thread", "title": "Uma variável por thread", "desc": "o valor que cada thread tem o seu"}, {"href": "/docs/partida/pilha", "title": "A pilha", "desc": "o teto de quadros, e o que vale de verdade"}, {"href": "/docs/seguranca/capacidade", "title": "Fronteira de capacidade", "desc": "o adopt que é recusado"}, {"href": "/docs/partida/mapa", "title": "Partida e segurança: o mapa", "desc": "o que existe, e o que não"}]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Partida e fim"}
      description={"O que acontece antes da primeira linha e depois da última — e o sinal que chega no meio."}
      href={"/docs/partida"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
