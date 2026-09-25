// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/bigorna.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Bigorna",
  description: "O framework de aplicações de mesa: várias telas com navegação, barra de menus com atalhos (Ctrl vira Cmd no macOS), diálogos nativos, barra de status, notificação, tabela com seleção, preferências na pasta certa de cada sistema e tema claro/escuro — sobre o Tk, sem dependência, e testável sem display.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (11)"},
  {"table": {"head": ["Assinatura"], "rows": [["`App(nome='DataForge', largura=900, altura=600, tema='sistema', pasta_de_config=None)`"], ["`Sonda(aplicacao)`"], ["`Tela(aplicacao, nome, eventos, dialogos)`"], ["`app(nome='DataForge', largura=900, altura=600, tema='sistema', pasta_de_config=None)`"], ["`item(rotulo, comando, atalho='')`"], ["`pasta_de_config(nome)`"], ["`rodar(aplicacao, fechar_em=0)`"], ["`separador()`"], ["`tem_display()`"], ["`temas()`"], ["`testar(aplicacao)`"]]}},
];

const headings = [{ id: 'funcoes-11', text: "Funções (11)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Bigorna"}
      description={"O framework de aplicações de mesa: várias telas com navegação, barra de menus com atalhos (Ctrl vira Cmd no macOS), diálogos nativos, barra de status, notificação, tabela com seleção, preferências na pasta certa de cada sistema e tema claro/escuro — sobre o Tk, sem dependência, e testável sem display."}
      href={"/docs/biblioteca/bigorna"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
