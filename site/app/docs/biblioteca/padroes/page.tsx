// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/padroes.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Padroes",
  description: "Os padrões de projeto que pedem mecanismo: único, pool, construtor, protótipo, flyweight, proxy, adaptador, composto, comandos com desfazer, cadeia, especificação, máquina de estados, memento, visitante, observável, mediador, repositório e barramento.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (20)"},
  {"table": {"head": ["Assinatura"], "rows": [["`adaptar(alvo, mapa)`"], ["`barramento()`"], ["`cadeia(manipuladores)`"], ["`comandos(limite=100)`"], ["`compartilhado(fabrica)`"], ["`composto(valor=None)`"], ["`construtor(molde, obrigatorios=None)`"], ["`especificacao(predicado, nome='especificacao')`"], ["`estrategias(padrao=None)`"], ["`maquina(inicial, transicoes)`"], ["`mediador()`"], ["`memento(obj)`"], ["`observavel()`"], ["`pool(fabrica, tamanho=4, limpar=None)`"], ["`prototipos()`"], ["`proxy(alvo, interceptar)`"], ["`repositorio(campo_id='id')`"], ["`restaurar(obj, memento)`"], ["`unico(fabrica)`"], ["`visitar(obj, visitante)`"]]}},
];

const headings = [{ id: 'funcoes-20', text: "Funções (20)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Padroes"}
      description={"Os padrões de projeto que pedem mecanismo: único, pool, construtor, protótipo, flyweight, proxy, adaptador, composto, comandos com desfazer, cadeia, especificação, máquina de estados, memento, visitante, observável, mediador, repositório e barramento."}
      href={"/docs/biblioteca/padroes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
