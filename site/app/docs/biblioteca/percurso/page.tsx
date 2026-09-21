// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/percurso.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Percurso",
  description: "O caminho inteiro de um arquivo, fase por fase, MEDIDO: lexer, parser, HIR, tipos, MIR, analises, SSA, passes e LIR, com o que cada fase produziu e quanto tempo levou. Responde 'onde o tempo vai' quando um arquivo demora a abrir no editor. Ele NAO executa o programa — executar e o que o programa faz, e um comando que mostra fases nao pode abrir soquete. Traz tambem as divergencias entre o caminho real e o desenho da referencia.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (5)"},
  {"table": {"head": ["Assinatura"], "rows": [["`desenho()`"], ["`divergencias()`"], ["`fases()`"], ["`percorrer(caminho, com_tipos=True)`"], ["`relatorio(resultado)`"]]}},
];

const headings = [{ id: 'funcoes-5', text: "Funções (5)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Percurso"}
      description={"O caminho inteiro de um arquivo, fase por fase, MEDIDO: lexer, parser, HIR, tipos, MIR, analises, SSA, passes e LIR, com o que cada fase produziu e quanto tempo levou. Responde 'onde o tempo vai' quando um arquivo demora a abrir no editor. Ele NAO executa o programa — executar e o que o programa faz, e um comando que mostra fases nao pode abrir soquete. Traz tambem as divergencias entre o caminho real e o desenho da referencia."}
      href={"/docs/biblioteca/percurso"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
