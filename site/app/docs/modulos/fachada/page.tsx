// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A fachada: um index.df",
  description: "relay from ./x — reunir vários módulos internos numa API só, e esconder o resto.",
};

const blocos: Bloco[] = [
  {"p": "Quando uma biblioteca cresce, ela vira vários arquivos. Quem a usa não deveria precisar saber em qual arquivo mora cada ação. Uma **fachada** reúne o que é público num ponto só."},
  { code: `lib/
  index.df        a fachada: o unico arquivo que quem usa adota
  precos.df       total, desconto
  frete.df        calcular_frete
  _cache.df       interno — nao aparece na fachada`, lang: 'text' },
  { code: `// index.df
relay from ./precos      // tudo o que precos.df exporta
relay from ./frete
// _cache.df nao e citado: continua interno`, lang: 'text', title: `lib/index.df` },
  { code: `adopt ./lib/index as Loja
out Loja.total(100), Loja.calcular_frete("SC")`, lang: 'text', title: `main.df` },
  {"table": {"head": ["Decisão", "Porque"], "rows": [["o nome local **vence** o re-exportado", "um `relay from` não sobrescreve o que a fachada definiu"], ["o `check` abre a superfície de um `relay from`", "seguir até o outro arquivo é possível, mas por ora ele cala em vez de adivinhar"], ["mover uma ação entre arquivos internos não muda nada para fora", "é o ponto: a fachada é o contrato, os arquivos são detalhe"]]}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"A fachada: um index.df"}
      description={"relay from ./x — reunir vários módulos internos numa API só, e esconder o resto."}
      href={"/docs/modulos/fachada"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
