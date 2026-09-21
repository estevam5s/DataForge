// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/malha.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Malha",
  description: "Chamada entre serviços que não mente: cliente HTTP com prazo, retry com recuo e tremor, disjuntor de três estados, descoberta por nome e propagação automática do rastro do pedido.",
};

const blocos: Bloco[] = [
  {"h2": "Constantes"},
  {"table": {"head": ["Nome", "Valor"], "rows": [["`RETENTAVEIS`", "`[408, 425, 429, 500, 502, 503, 504]`"]]}},
  {"h2": "Funções (22)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Cliente(base, opcoes=None)`"], ["`Disjuntor(falhas=5, espera=30.0, nome='')`"], ["`Passo(nome, fazer, desfazer=None, escreve=True, chave=None)`"], ["`Saga(nome='saga', identificador=None, registro=None)`"], ["`cabecalhos_de_contexto()`"], ["`cliente(base, opcoes=None)`"], ["`comecar_contexto(rastro=None, origem='', extra=None)`"], ["`contexto()`"], ["`de(nome, opcoes=None)`"], ["`disjuntor(falhas=5, espera=30.0, nome='')`"], ["`onde(nome)`"], ["`padrao(opcoes)`"], ["`propagar(req, origem='')`"], ["`rastro()`"], ["`recuo(tentativa, base=0.2, teto=10.0, tremor=True)`"], ["`registrar(nome, base, opcoes=None)`"], ["`resumo()`"], ["`saga(nome='saga', identificador=None, registro=None)`"], ["`saude()`"], ["`servicos()`"], ["`terminar_contexto()`"], ["`vale_repetir(resposta)`"]]}},
];

const headings = [{ id: 'constantes', text: "Constantes", level: 2 as const }, { id: 'funcoes-22', text: "Funções (22)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Malha"}
      description={"Chamada entre serviços que não mente: cliente HTTP com prazo, retry com recuo e tremor, disjuntor de três estados, descoberta por nome e propagação automática do rastro do pedido."}
      href={"/docs/biblioteca/malha"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
