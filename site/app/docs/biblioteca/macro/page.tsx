// GERADO por 'tools/gerar_paginas_biblioteca.py'. Nao edite aqui.
// O que e escrito a mao mora em
// 'site/scripts/conteudo_biblioteca/macro.py'; as tabelas saem do
// proprio modulo, a cada geracao.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Arcane.Macro",
  description: "A arvore como dado: ler o corpo de uma acao, percorrer, transformar e gerar codigo. 'citar' transforma texto em arvore, 'reescrever' devolve uma acao com o corpo trocado, 'nome_fresco' e 'renomear' dao higiene, e 'derivar' e a macro de atributo que gera __str__, __eq__, __lt__ e para_vault a partir dos campos.",
};

const blocos: Bloco[] = [
  {"h2": "Funções (13)"},
  {"table": {"head": ["Assinatura"], "rows": [["`acao(nome, parametros, corpo, fechamento=None)`"], ["`arvore(alvo)`"], ["`citar(texto)`"], ["`compilar(texto_fonte, nome='gerada', parametros=None)`"], ["`derivar(*quais)`"], ["`derivaveis()`"], ["`nome_fresco(base='temp')`"], ["`percorrer(dado, visitante)`"], ["`reescrever(alvo, transformador)`"], ["`renomear(dado, de, para)`"], ["`substituir(dado, de, para)`"], ["`texto(dado)`"], ["`transformar(dado, acao)`"]]}},
];

const headings = [{ id: 'funcoes-13', text: "Funções (13)", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Arcane.Macro"}
      description={"A arvore como dado: ler o corpo de uma acao, percorrer, transformar e gerar codigo. 'citar' transforma texto em arvore, 'reescrever' devolve uma acao com o corpo trocado, 'nome_fresco' e 'renomear' dao higiene, e 'derivar' e a macro de atributo que gera __str__, __eq__, __lt__ e para_vault a partir dos campos."}
      href={"/docs/biblioteca/macro"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
