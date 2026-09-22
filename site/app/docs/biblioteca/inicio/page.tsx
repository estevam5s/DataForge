// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/inicio.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Inicio",
  description: "O que roda ANTES da primeira linha: as fases da partida nomeadas e em ordem, e quanto cada 'adopt' custou — que e a unica forma de responder 'por que o programa demora a comecar?' sem cronometrar a mao. Mais armazenamento por THREAD com inicializacao e finalizador (o 'threading.local' da o armazem e nao da o resto), e a pilha que se pergunta: profundidade, teto, quanto falta e os quadros abertos.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (15)"},
  {"table": {"head": ["Assinatura"], "rows": [["`adocoes()`"], ["`ao_encerrar(acao)`"], ["`definir(a, v)`"], ["`encerrando()`"], ["`esquecer_encerramento(chave)`"], ["`fases()`"], ["`limite_da_pilha(novo=None)`"], ["`limpar(a)`"], ["`local(inicial, ao_terminar=None, nome='')`"], ["`meu(a)`"], ["`pilha()`"], ["`quadros()`"], ["`relatorio()`"], ["`texto_do_relatorio()`"], ["`threads_com_valor(a)`"]]}},
];

const headings = [{ id: 'funcoes-15', text: "Funções (15)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Inicio"}
      description={"O que roda ANTES da primeira linha: as fases da partida nomeadas e em ordem, e quanto cada 'adopt' custou — que e a unica forma de responder 'por que o programa demora a comecar?' sem cronometrar a mao. Mais armazenamento por THREAD com inicializacao e finalizador (o 'threading.local' da o armazem e nao da o resto), e a pilha que se pergunta: profundidade, teto, quanto falta e os quadros abertos."}
      href={"/docs/biblioteca/inicio"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
