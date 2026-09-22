// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O runtime",
  description: "O laço de eventos, as fibras e o executor: muita espera numa thread só.",
};

const blocos: Bloco[] = [
  {"p": "`Arcane.Laco` é um **reator**: uma thread dormindo no `selectors` do sistema até haver algo a fazer — um soquete pronto, um prazo vencido, uma tarefa na fila. É a forma de atender mil conexões com **uma** thread, em vez de mil."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
ordem := []
L.apos(laco, 20, lambda => ordem.append("depois"))
L.agendar(laco, lambda => ordem.append("agora"))
L.apos(laco, 40, lambda => L.parar(laco))
L.rodar(laco)
assert ordem is ["agora", "depois"]`, lang: 'df' },
  {"table": {"head": ["Peça", "Faz"], "rows": [["o laço", "a fila de prontas, a fila de prazos e o seletor de E/S"], ["as fibras", "`stream action` que cede o controle em cada `emit`"], ["o canal", "fibras que conversam sem trava"], ["o executor", "o trabalho que bloqueia vai para um pool, e o resultado volta pela fila"]]}},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/runtime/laco", "title": "O laço de eventos", "desc": "o reator, e por que ele dorme em vez de girar"}, {"href": "/docs/runtime/escalonador", "title": "O escalonador", "desc": "a ordem de execução e a justiça"}, {"href": "/docs/runtime/fibras", "title": "Fibras", "desc": "stream action como corrotina — e o limite do stackless"}, {"href": "/docs/runtime/canais", "title": "Canais entre fibras", "desc": "o chan do Go, com contrapressão de graça"}, {"href": "/docs/runtime/prazos", "title": "Prazos e relógios", "desc": "apos, a_cada e cancelar"}, {"href": "/docs/runtime/executor", "title": "O executor", "desc": "o trabalho que bloqueia, fora do laço"}, {"href": "/docs/runtime/contrapressao", "title": "Contrapressão", "desc": "o teto da fila, e a falha visível"}, {"href": "/docs/runtime/falhas", "title": "Quando algo falha", "desc": "uma conexão ruim não derruba o servidor"}, {"href": "/docs/runtime/escolher", "title": "Laço, thread, async ou processo", "desc": "qual modelo para qual trabalho"}, {"href": "/docs/runtime/mapa", "title": "O runtime: o mapa", "desc": "o que existe, e o que não"}]},
];

const headings = [{ id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O runtime"}
      description={"O laço de eventos, as fibras e o executor: muita espera numa thread só."}
      href={"/docs/runtime"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
