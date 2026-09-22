// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/observar.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Observar",
  description: "Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (22)"},
  {"table": {"head": ["Assinatura"], "rows": [["`abrir(painel, nome, dentro_de=None)`"], ["`alerta_slo(objetivo, longa, curta, limiar=14.4)`"], ["`alertar(painel, regras)`"], ["`arvore(painel)`"], ["`contar(painel, nome, quanto=1)`"], ["`cronometrar(painel, nome, acao)`"], ["`derivar(painel, saida, entradas, como='')`"], ["`fechar(painel, ident, estado='ok', detalhe=None)`"], ["`grafo(painel)`"], ["`impacto(painel, nome)`"], ["`marcar(painel, nome, valor)`"], ["`medir(painel, nome, valor)`"], ["`orcamento(objetivo, total, falhas)`"], ["`origem(painel, nome, profundidade=20)`"], ["`painel(nome, versao='', arquivo='')`"], ["`prometheus(painel)`"], ["`queima(objetivo, total, falhas)`"], ["`relatorio(painel)`"], ["`resumo(painel)`"], ["`salvar(painel, caminho='')`"], ["`trechos(painel)`"], ["`valor(painel, nome)`"]]}},
];

const headings = [{ id: 'funcoes-22', text: "Funções (22)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Observar"}
      description={"Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados."}
      href={"/docs/biblioteca/observar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
