// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/dsl.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Dsl",
  description: "Combinadores para escrever uma linguagem pequena, propria: texto, numero, nome, aspas, espaco, sequencia, alternativa, repeticao, opcional e separado_por, com 'analisar' devolvendo Resultado e a falha dizendo a posicao e o que era esperado.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (18)"},
  {"table": {"head": ["Assinatura"], "rows": [["`adiado(pegar)`"], ["`analisar(analisador, entrada, tudo=True)`"], ["`ate(parada)`"], ["`entre_aspas(aspa='\"')`"], ["`espaco(obrigatorio=False)`"], ["`exigir(analisador, mensagem)`"], ["`gramatica(regras, inicial)`"], ["`mapear(analisador, acao)`"], ["`muitos(analisador, minimo=0)`"], ["`nome()`"], ["`numero()`"], ["`opcional(analisador, padrao=None)`"], ["`ou(analisadores)`"], ["`qualquer_de(caracteres)`"], ["`separado_por(item, separador, minimo=0)`"], ["`seq(analisadores)`"], ["`simbolo(qual)`"], ["`texto(esperado)`"]]}},
];

const headings = [{ id: 'funcoes-18', text: "Funções (18)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Dsl"}
      description={"Combinadores para escrever uma linguagem pequena, propria: texto, numero, nome, aspas, espaco, sequencia, alternativa, repeticao, opcional e separado_por, com 'analisar' devolvendo Resultado e a falha dizendo a posicao e o que era esperado."}
      href={"/docs/biblioteca/dsl"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
