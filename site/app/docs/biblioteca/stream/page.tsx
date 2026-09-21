// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/stream.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Stream",
  description: "Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (17)"},
  {"table": {"head": ["Assinatura"], "rows": [["`atraso(corrente, topico, grupo)`"], ["`confirmar(corrente, topico, grupo, evento)`"], ["`confirmar_ate(corrente, topico, grupo, eventos)`"], ["`consumir(corrente, topico, grupo, quantos=0, particao=None)`"], ["`corrente(raiz)`"], ["`grupos(corrente, topico)`"], ["`informacao(corrente, topico)`"], ["`janela(eventos, segundos=60, campo='quando')`"], ["`ler_de(corrente, topico, desde=0, quantos=0, particao=None)`"], ["`offset(corrente, topico, grupo)`"], ["`publicar(corrente, topico, valor, chave=None)`"], ["`publicar_lote(corrente, topico, eventos)`"], ["`remover_topico(corrente, nome)`"], ["`reter(corrente, topico, segmentos=10)`"], ["`topico(corrente, nome, particoes=1)`"], ["`topicos(corrente)`"], ["`voltar(corrente, topico, grupo, para=0)`"]]}},
];

const headings = [{ id: 'funcoes-17', text: "Funções (17)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Stream"}
      description={"Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo."}
      href={"/docs/biblioteca/stream"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
