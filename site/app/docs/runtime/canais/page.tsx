// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Canais entre fibras",
  description: "L.canal: o chan do Go dentro de um laço — encontro com capacidade 0, fila com N, e fechar que termina o consumidor.",
};

const blocos: Bloco[] = [
  {"p": "Duas fibras que dividem uma lista precisam combinar quem mexe quando. O **canal** é a combinação pronta: uma fibra envia, a outra recebe, e o laço suspende quem precisa esperar. Nada é compartilhado além do próprio canal."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
pedidos := L.canal(2)
log := []

stream action produtor():
    cycle i from 1 to 5:
        log.append($"envia {i}")
        emit L.enviar(pedidos, i)          // espera se já há 2 na fila
    pedidos.fechar()

stream action consumidor():
    caixa := {}
    persist yes:
        emit L.receber(pedidos, caixa, "v")
        given caixa["v"] is void:          // fechado e vazio: acabou
            halt
        log.append($"trata {caixa["v"]}")
        emit L.dormir(1)                   // o consumidor é mais lento

L.fibra(laco, produtor)
L.fibra(laco, consumidor)
L.rodar(laco)

tratados := [x cycle x in log given x.starts_with("trata")]
assert tratados is ["trata 1", "trata 2", "trata 3", "trata 4", "trata 5"]`, lang: 'df' },
  {"h2": "Capacidade decide o ritmo"},
  {"table": {"head": ["Capacidade", "Quem envia", "Uso"], "rows": [["0 (padrão)", "espera até alguém receber — um **encontro**", "entregar em mão: sincronizar duas fibras"], ["N", "segue até haver N esperando", "absorver rajadas, sem deixar a fila crescer sem fim"]]}},
  {"p": "É a **contrapressão** de graça: um produtor mais rápido que o consumidor para no `enviar`, em vez de encher a memória. Com o canal de capacidade 2 acima, o produtor nunca fica mais de três itens à frente."},
  {"h2": "Fechar"},
  {"list": ["**Quem produz fecha.** `pedidos.fechar()` diz \"não vem mais nada\"; o consumidor recebe `void` depois de esvaziar a fila, e sai do laço.", "**Enviar num canal fechado é erro** — anotado em `L.falhas(laco)`, e a fibra que enviou termina. Ninguém ia ler.", "**Receber pela caixa.** `emit` é instrução, e não expressão: o valor volta escrito no vault que a fibra passou. Explícito, e melhor que fingir que `emit` devolve algo."]},
];

const headings = [{ id: 'capacidade-decide-o-ritmo', text: "Capacidade decide o ritmo", level: 2 as const }, { id: 'fechar', text: "Fechar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Canais entre fibras"}
      description={"L.canal: o chan do Go dentro de um laço — encontro com capacidade 0, fila com N, e fechar que termina o consumidor."}
      href={"/docs/runtime/canais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
