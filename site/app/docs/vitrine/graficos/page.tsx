// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/vitrine.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gráficos",
  description: "Sete tipos de gráfico, desenhados em SVG no servidor — sem biblioteca e sem CDN.",
};

const blocos: Bloco[] = [
  {"h2": "A forma curta"},
  { code: `V.grafico_linha(dados, x := "mes", y := "receita")
V.grafico_barras(dados, x := "mes", y := ["receita", "meta"])
V.grafico_area(dados, x := "dia", y := "acumulado")
V.grafico_dispersao(dados, x := "peso", y := "altura")
V.grafico_pizza(dados, x := "categoria", y := "valor")
V.grafico_rosca(dados, x := "categoria", y := "valor")
V.grafico_barras_h(dados, x := "produto", y := "vendas")
V.histograma(dados, campo := "idade", faixas := 12)`, lang: 'df' },
  {"p": "Sem `x` e `y`, a Vitrine adivinha: a primeira coluna não numérica vira o eixo, e as numéricas viram as séries. É o suficiente para um `V.grafico_linha(vendas)` funcionar na primeira tentativa."},
  {"h2": "A forma construída"},
  {"p": "Quando há mais a dizer:"},
  { code: `g := V.grafico("barras", vendas)
g.eixo_x("mes")
g.eixo_y(["receita", "meta"])
g.titulo("Vendas por período")
g.cores(["#FED403", "#0F62FE"])
g.altura(340)
g.empilhar(yes)
g.rotular(yes)
g.limite_y(0, 1000)
V.desenhar(g)`, lang: 'df' },
  {"p": "Cada método devolve o próprio gráfico, então também dá para encadear. Nada aparece na página até `V.desenhar`."},
  {"table": {"head": ["Método", "Faz"], "rows": [["`eixo_x(campo)`", "a coluna das categorias"], ["`eixo_y(campo)`", "uma coluna, ou um cluster delas"], ["`serie(campo)`", "acrescenta mais uma ao mesmo gráfico"], ["`titulo(texto)`", "o título acima"], ["`cores(cluster)`", "a paleta"], ["`altura(px)`", "a altura do desenho"], ["`empilhar(yes)`", "barras somadas em vez de lado a lado"], ["`suavizar(yes)`", "curva em vez de linha reta"], ["`rotular(yes)`", "o valor escrito sobre cada barra"], ["`legenda(no)` · `grade(no)`", "desliga a legenda ou a grade"], ["`limite_y(min, max)`", "fixa a escala"]]}},
  {"h2": "O que os dados precisam parecer"},
  {"p": "As mesmas três formas de `V.tabela`, mais uma quarta que um `group_by` costuma devolver:"},
  { code: `[{"mes": "Jan", "receita": 120}]       // cluster de vaults
{"mes": ["Jan"], "receita": [120]}     // vault de colunas
[["Jan", 120]]                         // matriz
{"Sul": 120, "Norte": 90}              // rótulo → número`, lang: 'df' },
  {"h2": "Por que SVG no servidor"},
  {"p": "Uma dependência de JavaScript obrigaria a página a buscar centenas de kilobytes de uma CDN, o que quebra qualquer aplicação que rode numa rede fechada — e é exatamente onde painel de dados costuma rodar."},
  {"p": "SVG também imprime, escala, é legível por leitor de tela, e o arquivo que sai daqui é o mesmo em qualquer navegador. A escala do eixo é arredondada para um número redondo: um eixo que vai até 1 237 não ajuda ninguém a ler o gráfico; até 1 500, com marcas de 500 em 500, ajuda."},
  {"callout": {"tipo": "nota", "titulo": "A paleta padrão", "texto": "A primeira cor é o amarelo da marca; as demais foram escolhidas para continuarem distinguíveis em escala de cinza e para quem não separa vermelho de verde — 8% dos homens. `V.paleta` traz as dez."}},
];

const headings = [{ id: 'a-forma-curta', text: "A forma curta", level: 2 as const }, { id: 'a-forma-construida', text: "A forma construída", level: 2 as const }, { id: 'o-que-os-dados-precisam-parecer', text: "O que os dados precisam parecer", level: 2 as const }, { id: 'por-que-svg-no-servidor', text: "Por que SVG no servidor", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gráficos"}
      description={"Sete tipos de gráfico, desenhados em SVG no servidor — sem biblioteca e sem CDN."}
      href={"/docs/vitrine/graficos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
