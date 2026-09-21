// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/pipeline.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Pipeline",
  description: "Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (11)"},
  {"table": {"head": ["Assinatura"], "rows": [["`esquecer_marca(fluxo, chave='')`"], ["`etapa(fluxo, nome, acao, depende_de=None, tentativas=1, espera=0, quando=None, opcional=False, descricao='')`"], ["`fluxo(nome, estado='')`"], ["`grafico(fluxo)`"], ["`historico(fluxo, quantos=10)`"], ["`marca(fluxo, chave, padrao=None)`"], ["`marcar(fluxo, chave, valor)`"], ["`ordem(fluxo)`"], ["`rodar(fluxo, contexto=None, ate=None)`"], ["`rodar_ate(fluxo, etapa, contexto=None)`"], ["`ultima_execucao(fluxo)`"]]}},
];

const headings = [{ id: 'funcoes-11', text: "Funções (11)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Pipeline"}
      description={"Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório."}
      href={"/docs/biblioteca/pipeline"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
