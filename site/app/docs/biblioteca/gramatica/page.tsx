// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/gramatica.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Gramatica",
  description: "A gramática da linguagem como dado: as produções em EBNF, cada uma com um exemplo conferido contra o parser, a tabela de precedência provada pela árvore, os tokens de um texto, as instruções que o parser entendeu e a validação de sintaxe sem executar nada.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (10)"},
  {"table": {"head": ["Assinatura"], "rows": [["`ebnf(grupo='')`"], ["`grupos()`"], ["`instrucoes(texto)`"], ["`palavras()`"], ["`precedencia()`"], ["`producao(nome)`"], ["`producoes(grupo='')`"], ["`raiz(expressao)`"], ["`tokens(texto)`"], ["`validar(texto)`"]]}},
];

const headings = [{ id: 'funcoes-10', text: "Funções (10)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Gramatica"}
      description={"A gramática da linguagem como dado: as produções em EBNF, cada uma com um exemplo conferido contra o parser, a tabela de precedência provada pela árvore, os tokens de um texto, as instruções que o parser entendeu e a validação de sintaxe sem executar nada."}
      href={"/docs/biblioteca/gramatica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
