// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O executor",
  description: "O trabalho que bloqueia vai para um pool de threads, e o resultado volta pela fila do laço.",
};

const blocos: Bloco[] = [
  {"p": "Um laço tem **uma** thread. Uma tarefa que bloqueia — ler um arquivo grande, consultar um banco sem driver assíncrono, uma conta pesada — trava **tudo**: nenhum prazo vence, nenhuma conexão é atendida. `L.executar` manda o trabalho para um pool, e entrega o resultado de volta ao laço quando fica pronto."},
  { code: `adopt Arcane.Laco as L

laco := L.novo()
log := []

action consulta_lenta():
    sleep(30)                         // um banco sem driver assíncrono
    yield 42

action pronto(r):                     // roda NO LAÇO, quando o pool termina
    log.append($"resultado {r}")
    L.parar(laco)

L.executar(laco, consulta_lenta, pronto)
L.a_cada(laco, 5, lambda => log.append("laço vivo"))
L.rodar(laco)

assert log.contains("resultado 42")
assert log.contains("laço vivo")      // o laço seguiu girando durante a consulta`, lang: 'df' },
  {"list": ["**O `depois` roda no laço**, e não no pool: ali ele pode mexer no estado do laço sem trava.", "**A conta de trabalhos no pool segura o laço vivo.** Sem ela, `rodar` terminaria antes de o resultado voltar, e `executar` seria uma forma elaborada de jogar trabalho fora.", "**Trabalho de CPU não fica mais rápido** num pool de threads: o GIL continua no caminho. Para isso, processos — ver [Laço, thread, async ou processo](/docs/runtime/escolher)."]},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"O executor"}
      description={"O trabalho que bloqueia vai para um pool de threads, e o resultado volta pela fila do laço."}
      href={"/docs/runtime/executor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
