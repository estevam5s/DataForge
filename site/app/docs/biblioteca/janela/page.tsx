// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/janela.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Janela",
  description: "Aplicação de mesa nativa com zero dependência: o Tk vem na biblioteca padrão. A árvore é separada do desenho, como na Vitrine — e por isso uma tela se testa sem display nenhum.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (10)"},
  {"table": {"head": ["Assinatura"], "rows": [["`App(titulo='DataForge', largura=720, altura=520, tema='claro')`"], ["`No(especie, rotulo='', valor=None, opcoes=None, chave='')`"], ["`Sonda(tela_acao, estado=None, titulo='')`"], ["`Tela(estado, eventos=None, titulo='')`"], ["`abrir(aplicacao, tela_acao, quando_fechar=None, fechar_em=0)`"], ["`app(titulo='DataForge', largura=720, altura=520, tema='claro')`"], ["`componentes()`"], ["`montar(tela_acao, estado=None, eventos=None, titulo='')`"], ["`tem_display()`"], ["`testar(tela_acao, estado=None, titulo='')`"]]}},
];

const headings = [{ id: 'funcoes-10', text: "Funções (10)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Janela"}
      description={"Aplicação de mesa nativa com zero dependência: o Tk vem na biblioteca padrão. A árvore é separada do desenho, como na Vitrine — e por isso uma tela se testa sem display nenhum."}
      href={"/docs/biblioteca/janela"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
