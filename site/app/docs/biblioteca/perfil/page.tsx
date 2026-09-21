// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/perfil.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Perfil",
  description: "Medir com rigor, onde o 'Bench' da a media: percentis (p50, p95, p99, p999) com aquecimento separado, comparacao com SIGNIFICANCIA estatistica (Mann-Whitney, que nao supoe normalidade — tempo de execucao nao e normal), linha de base guardada para acusar regressao no CI, flame graph das ACOES da linguagem em SVG sem nada de fora, pausas do coletor medidas na fonte e contencao de trava.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (16)"},
  {"table": {"head": ["Assinatura"], "rows": [["`chama_svg(perfil, largura=1200, altura_linha=18)`"], ["`chama_texto(perfil)`"], ["`com_trava(alvo, acao)`"], ["`comecar_perfil(interp)`"], ["`comparar(a, b, opcoes=None)`"], ["`conferir(nome, medida, opcoes=None)`"], ["`estatisticas_da_trava(alvo)`"], ["`gc_pausas(acao)`"], ["`guardar(nome, medida, arquivo='perfil-base.json')`"], ["`mann_whitney(a, b)`"], ["`medir(acao, opcoes=None)`"], ["`perfilar(acao, interp=None)`"], ["`relatorio(medida)`"], ["`resumir(valores, casas=4)`"], ["`terminar_perfil(coleta)`"], ["`trava()`"]]}},
];

const headings = [{ id: 'funcoes-16', text: "Funções (16)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Perfil"}
      description={"Medir com rigor, onde o 'Bench' da a media: percentis (p50, p95, p99, p999) com aquecimento separado, comparacao com SIGNIFICANCIA estatistica (Mann-Whitney, que nao supoe normalidade — tempo de execucao nao e normal), linha de base guardada para acusar regressao no CI, flame graph das ACOES da linguagem em SVG sem nada de fora, pausas do coletor medidas na fonte e contencao de trava."}
      href={"/docs/biblioteca/perfil"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
