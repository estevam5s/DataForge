// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/stm.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Stm",
  description: "Memoria transacional: escritas que acontecem JUNTAS ou nao acontecem. Variavel transacional, 'atomicamente' com validacao otimista e repeticao no conflito, 'retentar' que espera em vez de girar, 'ou_entao' para compor duas operacoes bloqueantes, e estatisticas de conflito.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (13)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Variavel(valor=None, nome='')`"], ["`atomicamente(acao, tentativas=1000)`"], ["`definir(var, novo)`"], ["`em_transacao()`"], ["`escrever(var, valor)`"], ["`estatisticas()`"], ["`ler(var)`"], ["`modificar(var, acao)`"], ["`ou_entao(primeira, segunda)`"], ["`retentar()`"], ["`valor(var)`"], ["`variavel(valor=None, nome='')`"], ["`zerar_estatisticas()`"]]}},
];

const headings = [{ id: 'funcoes-13', text: "Funções (13)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Stm"}
      description={"Memoria transacional: escritas que acontecem JUNTAS ou nao acontecem. Variavel transacional, 'atomicamente' com validacao otimista e repeticao no conflito, 'retentar' que espera em vez de girar, 'ou_entao' para compor duas operacoes bloqueantes, e estatisticas de conflito."}
      href={"/docs/biblioteca/stm"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
