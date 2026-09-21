// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/laco.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Laco",
  description: "O laco de eventos, o escalonador e as fibras: UMA thread dormindo no seletor do sistema (epoll, kqueue ou select) em vez de uma thread por conexao. Fila de prazos com 'apos' e 'a_cada', fila de prontas com teto opcional (contrapressao), executor para o trabalho que bloqueia, cancelamento, e fibras de verdade — um 'stream action' suspenso em cada 'emit'.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (25)"},
  {"table": {"head": ["Assinatura"], "rows": [["`a_cada(laco, ms, acao, rotulo='')`"], ["`agendar(laco, acao, rotulo='')`"], ["`apos(laco, ms, acao, rotulo='')`"], ["`cancelada(alvo)`"], ["`cancelar(alvo)`"], ["`ceder()`"], ["`depois_de(ms, caixa, chave, valor='pronto')`"], ["`dormir(ms)`"], ["`escrever(soquete)`"], ["`esperar(outra)`"], ["`esquecer(laco, soquete)`"], ["`estatisticas(laco)`"], ["`executar(laco, trabalho, depois=None)`"], ["`falhas(laco)`"], ["`fechar(laco)`"], ["`fibra(laco, acao, argumentos=None, nome='')`"], ["`fibras(laco)`"], ["`ler(soquete, caixa, chave, quanto=65536)`"], ["`mecanismo(laco)`"], ["`novo(teto=None)`"], ["`parar(laco)`"], ["`pedidos()`"], ["`quando_escrever(laco, soquete, acao)`"], ["`quando_ler(laco, soquete, acao)`"], ["`rodar(laco, voltas=None)`"]]}},
];

const headings = [{ id: 'funcoes-25', text: "Funções (25)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Laco"}
      description={"O laco de eventos, o escalonador e as fibras: UMA thread dormindo no seletor do sistema (epoll, kqueue ou select) em vez de uma thread por conexao. Fila de prazos com 'apos' e 'a_cada', fila de prontas com teto opcional (contrapressao), executor para o trabalho que bloqueia, cancelamento, e fibras de verdade — um 'stream action' suspenso em cada 'emit'."}
      href={"/docs/biblioteca/laco"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
