// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Do quadro ao gráfico",
  description: "Levar um Quadro para um painel da Vitrine — a janela vira linha, o pivô vira barra.",
};

const blocos: Bloco[] = [
  {"p": "Um número numa tabela diz o valor; um gráfico diz a **forma** — a tendência, a sazonalidade, o ponto fora. A Vitrine desenha a partir de uma lista de vaults, que é exatamente o que um `Quadro` devolve com `para_vaults()`."},
  { code: `adopt Arcane.Quadro as Q
adopt Arcane.Vitrine as V

vendas := Q.de_vaults([
    {"dia": "01", "valor": 120}, {"dia": "02", "valor": 150},
    {"dia": "03", "valor": 90}, {"dia": "04", "valor": 200}])
    .janela("valor", 2, "media", "media_movel", 1)

action painel():
    V.titulo("Vendas")
    V.grafico_linha(vendas.para_vaults(), x := "dia", y := ["valor", "media_movel"])

t := V.testar(painel)
assert not t.falhou()
assert t.existe("grafico")`, lang: 'df' },
  {"table": {"head": ["Pergunta", "Verbo do Quadro", "Gráfico"], "rows": [["como evolui?", "`janela` / `acumulado`", "linha"], ["qual é maior?", "`agrupar(...).resumir(...)`", "barra"], ["quanto de cada um?", "`pivotar`", "barra empilhada"], ["como se distribui?", "`discretizar`", "histograma (barra)"], ["anda junto?", "`correlacao`", "dispersão"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Barra começa no zero; linha não precisa", "texto": "Numa barra, o que significa é o comprimento, e cortar o eixo faz 3% parecer o dobro. Numa linha, o que significa é a posição — forçar o zero achata a variação que o gráfico existe para mostrar. A Vitrine já decide assim; ver [Gráficos](/docs/vitrine/graficos)."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Do quadro ao gráfico"}
      description={"Levar um Quadro para um painel da Vitrine — a janela vira linha, o pivô vira barra."}
      href={"/docs/dados/visualizar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
