// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/async.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Async",
  description: "Promessas, filas, agendamento e execução concorrente.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Async as Async

// Promessas e agendamento
tarefa := Async.promise(lambda: 42)
out Async.resolve(tarefa)`, title: `exemplo` },
  {"h2": "Funções (52)"},
  {"table": {"head": ["Assinatura"], "rows": [["`all(promises)`"], ["`any(promises)`"], ["`ao_criar(funcao)`"], ["`ao_falhar(funcao)`"], ["`ao_terminar(funcao)`"], ["`batch(fn)`"], ["`buffer_op(size)`"], ["`catch(promise, callback)`"], ["`channel(buffer_size=0)`"], ["`combine_latest(*observables)`"], ["`computed(signals, fn)`"], ["`debounce_op(ms)`"], ["`delay(ms, fn=None)`"], ["`distinct_op()`"], ["`effect(signals, fn)`"], ["`emit(emitter, event, *data)`"], ["`emit_event(emitter, event, *data)`"], ["`emitter()`"], ["`esperar_todas(prazo=None)`"], ["`event_emitter()`"], ["`filter_op(fn)`"], ["`from_list(lst)`"], ["`interval(ms, count=10)`"], ["`map_op(fn)`"], ["`merge(*observables)`"], ["`observable(producer=None)`"], ["`of(*values)`"], ["`off(emitter, event, callback=None)`"], ["`on(emitter, event, callback)`"], ["`once_event(emitter, event, callback)`"], ["`parallel(*fns)`"], ["`pipe_stream(observable, *operators)`"], ["`promise(executor)`"], ["`race(promises)`"], ["`receive(ch)`"], ["`reject(error)`"], ["`resolve(value)`"], ["`retry_task(fn, max_retries=3, delay_ms=100)`"], ["`scan_op(fn, initial)`"], ["`sem_ganchos()`"], ["`send(ch, value)`"], ["`sequential(*fns)`"], ["`settled(promises)`"], ["`signal(initial_value)`"], ["`skip_op(n)`"], ["`subject()`"], ["`subscribe(observable, callback)`"], ["`take_op(n)`"], ["`task(fn)`"], ["`then(promise, callback)`"], ["`timeout(ms, fn)`"], ["`vivas()`"]]}},
];

const headings = [{ id: 'funcoes-52', text: "Funções (52)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Async"}
      description={"Promessas, filas, agendamento e execução concorrente."}
      href={"/docs/biblioteca/async"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
