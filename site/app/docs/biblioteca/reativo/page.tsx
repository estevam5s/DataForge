// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/reativo.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Reativo",
  description: "Valores que avisam quando mudam: sinal (um valor com estado), derivado (calculado de outros, preguicoso e memorizado, com as dependencias DESCOBERTAS na execucao), efeito (o que acontece quando muda, com limpeza entre ciclos) e observavel (um fluxo no tempo, com morph, sift, distill, distintos, esperar, limitar, combinar e juntar). A diferenca entre valor e fluxo e mantida de proposito: um clique e fluxo, um saldo e valor.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (18)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Derivado(formula, nome='derivado')`"], ["`Efeito(acao, nome='efeito', agora=True)`"], ["`Historico(alvo, limite=100)`"], ["`Inscricao(cancelar)`"], ["`Observavel(nome='observavel')`"], ["`Recurso(buscar, fonte=None)`"], ["`Sinal(inicial=None, nome='sinal', iguais=None)`"], ["`combinar(*fontes)`"], ["`de_cluster(itens, nome='de_cluster')`"], ["`derivado(formula, nome='derivado')`"], ["`efeito(acao, nome='efeito', agora=True)`"], ["`historico(alvo, limite=100)`"], ["`intervalo(segundos, quantos=0, nome='intervalo')`"], ["`juntar(*fontes)`"], ["`lote(acao)`"], ["`observavel(nome='observavel')`"], ["`recurso(buscar, fonte=None)`"], ["`sinal(inicial=None, nome='sinal', iguais=None)`"]]}},
];

const headings = [{ id: 'funcoes-18', text: "Funções (18)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Reativo"}
      description={"Valores que avisam quando mudam: sinal (um valor com estado), derivado (calculado de outros, preguicoso e memorizado, com as dependencias DESCOBERTAS na execucao), efeito (o que acontece quando muda, com limpeza entre ciclos) e observavel (um fluxo no tempo, com morph, sift, distill, distintos, esperar, limitar, combinar e juntar). A diferenca entre valor e fluxo e mantida de proposito: um clique e fluxo, um saldo e valor."}
      href={"/docs/biblioteca/reativo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
