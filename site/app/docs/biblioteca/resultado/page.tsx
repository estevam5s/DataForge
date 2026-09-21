// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/resultado.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Resultado",
  description: "A falha como VALOR, e a ausencia com nome: 'ok'/'falha' para quem devolve o erro em vez de levanta-lo, com 'mapear', 'entao', 'recuperar', 'ou' e 'todos' (a primeira falha vence); e 'Talvez' ('algo'/'nada') para onde 'void' e ambiguo — distinguir 'a chave nao esta la' de 'a chave vale void'.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (13)"},
  {"table": {"head": ["Assinatura"], "rows": [["`Resultado(ok, valor=None, erro=None, detalhe=None)`"], ["`Talvez(tem, valor=None)`"], ["`algo(valor=None)`"], ["`chave(vault, nome)`"], ["`de(valor, motivo='void')`"], ["`erros(resultados)`"], ["`falha(erro='falhou', detalhe=None)`"], ["`nada()`"], ["`ok(valor=None)`"], ["`primeiro(colecao, condicao=None)`"], ["`talvez(valor)`"], ["`tentar(acao, *args)`"], ["`todos(resultados)`"]]}},
];

const headings = [{ id: 'funcoes-13', text: "Funções (13)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Resultado"}
      description={"A falha como VALOR, e a ausencia com nome: 'ok'/'falha' para quem devolve o erro em vez de levanta-lo, com 'mapear', 'entao', 'recuperar', 'ou' e 'todos' (a primeira falha vence); e 'Talvez' ('algo'/'nada') para onde 'void' e ambiguo — distinguir 'a chave nao esta la' de 'a chave vale void'."}
      href={"/docs/biblioteca/resultado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
