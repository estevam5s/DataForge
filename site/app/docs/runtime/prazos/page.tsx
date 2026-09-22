// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Prazos e relógios",
  description: "apos, a_cada e cancelar — sem uma thread por relógio.",
};

const blocos: Bloco[] = [
  {"p": "Um relógio por thread é o jeito ingênuo: mil temporizadores, mil threads dormindo. O laço guarda todos os prazos num **heap** e dorme até o mais próximo — mil temporizadores custam uma thread."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
batidas := []
relogio := L.a_cada(laco, 10, lambda => batidas.append("tique"))
L.apos(laco, 35, lambda => L.cancelar(relogio))     // para o relógio
L.apos(laco, 60, lambda => L.parar(laco))
L.rodar(laco)

// cancelado aos 35 ms: no máximo 3 batidas de 10 ms — e ao menos uma.
// Num computador carregado podem ser menos; nunca mais.
assert len(batidas) bigger_eq 1 and len(batidas) smaller_eq 3
assert L.cancelada(relogio)`, lang: 'df' },
  {"table": {"head": ["Função", "Faz"], "rows": [["`L.agendar(laco, acao)`", "na próxima volta"], ["`L.apos(laco, ms, acao)`", "uma vez, depois de `ms`"], ["`L.a_cada(laco, ms, acao)`", "a cada `ms`, até ser cancelado"], ["`L.cancelar(tarefa)`", "desmarca — vale para tarefa e para fibra"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O prazo é um mínimo, não uma promessa", "texto": "`apos(laco, 10, f)` roda `f` **não antes** de 10 ms. Se o laço estiver ocupado com uma tarefa lenta, roda depois dela. `L.estatisticas(laco)[\"maior_atraso_ms\"]` mostra quanto o pior prazo atrasou — e um número alto ali quer dizer que alguma tarefa está bloqueando o laço."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Prazos e relógios"}
      description={"apos, a_cada e cancelar — sem uma thread por relógio."}
      href={"/docs/runtime/prazos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
