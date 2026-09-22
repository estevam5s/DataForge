// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/github.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.GitHub",
  description: "O que um programa precisa para viver no GitHub: no Actions, saídas, variáveis e resumo com delimitador seguro, anotações escapadas que aparecem na linha do PR, máscara linha a linha e grupos; webhooks com assinatura HMAC conferida em tempo constante sobre os bytes originais; e a API REST com paginação por Link e o limite de taxa que sobrou.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (19)"},
  {"table": {"head": ["Assinatura"], "rows": [["`ClienteGitHub(token='', base='https://api.github.com', prazo=30.0)`"], ["`anotacao(nivel, mensagem, arquivo='', linha=0, coluna=0, titulo='', fim_linha=0)`"], ["`anotar(nivel, mensagem, arquivo='', linha=0, coluna=0, titulo='')`"], ["`assinatura(segredo, corpo)`"], ["`cliente(token='', base='https://api.github.com', prazo=30.0)`"], ["`conferir_webhook(segredo, corpo, cabecalho)`"], ["`contexto()`"], ["`em_actions()`"], ["`escapar_dado(texto)`"], ["`escapar_propriedade(texto)`"], ["`evento()`"], ["`evento_de_webhook(cabecalhos, corpo, segredo)`"], ["`exportar(nome, valor)`"], ["`grupo(nome, acao)`"], ["`mascarar_no_log(valor)`"], ["`no_path(pasta)`"], ["`resumo(markdown)`"], ["`saida(nome, valor)`"], ["`tabela_markdown(linhas, colunas=None)`"]]}},
];

const headings = [{ id: 'funcoes-19', text: "Funções (19)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.GitHub"}
      description={"O que um programa precisa para viver no GitHub: no Actions, saídas, variáveis e resumo com delimitador seguro, anotações escapadas que aparecem na linha do PR, máscara linha a linha e grupos; webhooks com assinatura HMAC conferida em tempo constante sobre os bytes originais; e a API REST com paginação por Link e o limite de taxa que sobrou."}
      href={"/docs/biblioteca/github"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
