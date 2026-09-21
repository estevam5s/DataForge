// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/compilador.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Compilador",
  description: "O caminho de compilacao como dado: os tokens, a arvore, o HIR (a arvore depois do acucar, com a lista do que e acucar e do que so parece), o MIR (bloco basico, aresta, laco e tratador) e as analises que so o grafo responde — alcance, vivacidade, constante em todo caminho, escapatoria e o nome que so um ramo define. O LIR diz o que o compilador de fechamentos compilou e o que recuou para a arvore.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (24)"},
  {"table": {"head": ["Assinatura"], "rows": [["`acucares(fonte)`"], ["`acucares_conhecidos()`"], ["`alcance(fonte)`"], ["`arvore(fonte)`"], ["`blocos(fonte, nome=None)`"], ["`constantes(fonte, nome=None)`"], ["`corpos(fonte)`"], ["`escapam(fonte, nome=None)`"], ["`fases()`"], ["`hir(fonte)`"], ["`lir(fonte)`"], ["`mir(fonte)`"], ["`nao_e_acucar()`"], ["`onde_talvez_nao_definidas(fonte)`"], ["`otimizar(fonte, quais=None)`"], ["`passes()`"], ["`provadas(fonte, nome=None)`"], ["`ramos_mortos(fonte)`"], ["`resolucao(fonte)`"], ["`ssa(fonte, nome=None)`"], ["`talvez_nao_definidas(fonte, nome=None)`"], ["`texto(fonte, fase='mir')`"], ["`tokens(fonte)`"], ["`vivas(fonte, nome=None)`"]]}},
];

const headings = [{ id: 'funcoes-24', text: "Funções (24)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Compilador"}
      description={"O caminho de compilacao como dado: os tokens, a arvore, o HIR (a arvore depois do acucar, com a lista do que e acucar e do que so parece), o MIR (bloco basico, aresta, laco e tratador) e as analises que so o grafo responde — alcance, vivacidade, constante em todo caminho, escapatoria e o nome que so um ramo define. O LIR diz o que o compilador de fechamentos compilou e o que recuou para a arvore."}
      href={"/docs/biblioteca/compilador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
