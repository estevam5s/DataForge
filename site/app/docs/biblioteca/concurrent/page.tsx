// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/concurrent.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Concurrent",
  description: "Threads, processos, canal bloqueante, grupo de tarefas e prazo.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (33)"},
  {"table": {"head": ["Assinatura"], "rows": [["`anel(capacidade=16)`"], ["`atomico(inicial=None)`"], ["`barreira(quantas)`"], ["`canal(capacidade=0)`"], ["`com_prazo(acao, segundos)`"], ["`com_trava(trava, acao)`"], ["`condicao()`"], ["`contador(inicial=0)`"], ["`dormir(segundos)`"], ["`esperar(tarefa, prazo=None)`"], ["`esperar_primeira(tarefas, prazo=None)`"], ["`esperar_todas(tarefas, prazo=None)`"], ["`evento()`"], ["`executor(trabalhadores=4)`"], ["`fila_sem_trava(itens=None)`"], ["`grupo(trabalhadores=None, nome='')`"], ["`lotes(acao, itens, tamanho=10, trabalhadores=None)`"], ["`map(acao, itens, trabalhadores=None, prazo=None)`"], ["`map_processos(acao, itens, trabalhadores=None)`"], ["`mutex()`"], ["`nucleos()`"], ["`para_cada(acao, itens, trabalhadores=None)`"], ["`pilha_sem_trava(itens=None)`"], ["`pool_processos(trabalhadores=None)`"], ["`processo(acao, *args)`"], ["`promessa()`"], ["`repetir_a_cada(acao, segundos, vezes=0)`"], ["`rodar(acao, *args)`"], ["`semaforo(quantos=1)`"], ["`sou_principal()`"], ["`thread_atual()`"], ["`threads_vivas()`"], ["`trava_leitura_escrita()`"]]}},
];

const headings = [{ id: 'funcoes-33', text: "Funções (33)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Concurrent"}
      description={"Threads, processos, canal bloqueante, grupo de tarefas e prazo."}
      href={"/docs/biblioteca/concurrent"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
