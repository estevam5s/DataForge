// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/color.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Color",
  description: "Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (66)"},
  {"table": {"head": ["Assinatura"], "rows": [["`auto()`"], ["`badge(texto, cor='blue')`"], ["`bar(valor, total, largura=30, cor='green', mostrar_numero=True)`"], ["`bg_rgb(texto, r, g, b)`"], ["`black(texto)`"], ["`blink(texto)`"], ["`blue(texto)`"], ["`bold(texto)`"], ["`box(texto, titulo='', cor='cyan', largura=0)`"], ["`bright_blue(texto)`"], ["`bright_cyan(texto)`"], ["`bright_green(texto)`"], ["`bright_magenta(texto)`"], ["`bright_red(texto)`"], ["`bright_white(texto)`"], ["`bright_yellow(texto)`"], ["`cyan(texto)`"], ["`dim(texto)`"], ["`error(texto)`"], ["`force(ligado=True)`"], ["`gradient(texto, de, para)`"], ["`gray(texto)`"], ["`green(texto)`"], ["`grey(texto)`"], ["`hex(texto, cor)`"], ["`hidden(texto)`"], ["`info()`"], ["`info_msg(texto)`"], ["`italic(texto)`"], ["`magenta(texto)`"], ["`muted(texto)`"], ["`on_black(texto)`"], ["`on_blue(texto)`"], ["`on_bright_blue(texto)`"], ["`on_bright_cyan(texto)`"], ["`on_bright_green(texto)`"], ["`on_bright_magenta(texto)`"], ["`on_bright_red(texto)`"], ["`on_bright_white(texto)`"], ["`on_bright_yellow(texto)`"], ["`on_cyan(texto)`"], ["`on_gray(texto)`"], ["`on_green(texto)`"], ["`on_grey(texto)`"], ["`on_magenta(texto)`"], ["`on_red(texto)`"], ["`on_white(texto)`"], ["`on_yellow(texto)`"], ["`paint(texto, *nomes)`"], ["`rainbow(texto)`"], ["`red(texto)`"], ["`reverse(texto)`"], ["`rgb(texto, r, g, b)`"], ["`rule(titulo='', cor='gray', largura=0)`"], ["`spinner_frames(estilo='pontos')`"], ["`strike(texto)`"], ["`strip(texto)`"], ["`success(texto)`"], ["`supports()`"], ["`table(linhas, cabecalho=True, cor='cyan')`"], ["`tree(no, prefixo='', ultimo=True)`"], ["`underline(texto)`"], ["`warning(texto)`"], ["`white(texto)`"], ["`width(padrao=80)`"], ["`yellow(texto)`"]]}},
];

const headings = [{ id: 'funcoes-66', text: "Funções (66)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Color"}
      description={"Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore."}
      href={"/docs/biblioteca/color"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
