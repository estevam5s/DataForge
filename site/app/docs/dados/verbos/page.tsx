// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dados_quadro.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Os verbos do pipeline",
  description: "Seis palavras contextuais que fazem um quadro fluir pelo operador >> — com as colunas escritas nuas.",
};

const blocos: Bloco[] = [
  {"p": "O operador `>>` já existia, com `sift`, `morph` e `distill`. Para dado tabular faltava o vocabulário: **seis verbos** que operam sobre o quadro inteiro, e não sobre um item por vez."},
  { code: `resumo := vendas
    >> onde valor bigger 50
    >> agrupar produto
    >> resumir {"valor": "soma"}
    >> ordenar valor desc

out resumo.texto()
`, lang: 'df' },
  { code: `produto  valor
-------  -----
cafe     210
cha      60
`, lang: 'text', title: `saída` },
  {"h2": "Os seis"},
  {"table": {"head": ["Verbo", "Faz", "Devolve"], "rows": [["`onde <expressão>`", "filtra, com as colunas escritas nuas", "quadro"], ["`pegar a, b`", "escolhe colunas, nessa ordem", "quadro"], ["`sem a`", "descarta colunas", "quadro"], ["`ordenar col [desc]`", "ordena", "quadro"], ["`agrupar col[, col2]`", "agrupa", "**agrupamento**"], ["`resumir {…}`", "agrega", "quadro"]]}},
  {"p": "`agrupar` é o único que não devolve quadro: um agrupamento não tem forma retangular até alguém dizer \"média de quê\". Depois dele vem `resumir` — e qualquer outro verbo ali diz isso."},
  {"h2": "A coluna se escreve nua"},
  {"p": "É o que faz o verbo valer a pena. `onde valor bigger 50` lê como se lê, sem `lambda l: l[\"valor\"]`:"},
  { code: `out (vendas >> onde qtd bigger 3).altura()
`, lang: 'df' },
  {"p": "Nem todo cabeçalho de CSV é um identificador válido — `Valor Total` e `preco/kg` são nomes comuns de coluna. Por isso as duas formas convivem:"},
  { code: `q := Q.de_vaults([{"Valor Total": 10}, {"Valor Total": 30}])
out (q >> pegar "Valor Total").colunas()
`, lang: 'df' },
  {"h2": "Duas regras de escopo, e elas são previsíveis"},
  {"table": {"head": ["Dentro de um `onde`", "Vale"], "rows": [["um nome que é coluna", "**a coluna vence**, sempre"], ["um nome que não é coluna", "o escopo de fora, como em qualquer expressão"]]}},
  { code: `limite := 100.0
out (vendas >> onde valor bigger limite).altura()    // 1 — 'limite' vem de fora
`, lang: 'df' },
  {"p": "A primeira regra é o contrato do verbo: dentro de um `onde`, um nome nu é uma coluna. Sem ela, o mesmo código leria de dois jeitos conforme o que houvesse no escopo."},
  {"h2": "A ausência não passa no filtro"},
  {"p": "Comparar com o **desconhecido** não dá nem sim nem não, e a linha não passa. É a lógica de três valores do SQL, e a de toda ferramenta de dados que existe:"},
  { code: `out (vendas >> onde valor bigger 0).altura()     // 4 — a linha sem valor fica fora
out (vendas >> onde valor is void).altura()      // 1 — e quem quer a ausência pergunta
`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "A outra escolha era defensável, e inútil", "texto": "Levantar erro na comparação com `void` é o que a linguagem faz em toda expressão comum, e está certo lá. Aqui tornaria o verbo inutilizável: todo conjunto real tem ausência, e o primeiro `onde` de todo programa morreria na primeira linha vazia. **Só essa falha é engolida** — uma coluna que não existe, uma ação que quebra ou uma divisão por zero continuam subindo."}},
  {"h2": "Os verbos convivem com `sift` e `morph`"},
  {"p": "A conversão é preguiçosa: cada estágio pede a forma de que precisa, na hora em que precisa."},
  { code: `out vendas >> onde regiao is "sul" >> morph l: l["produto"]
`, lang: 'df' },
  {"p": "E a fonte pode ser um **cluster de vaults**, que é o que sai de `IO.read_csv(caminho, yes)` e de `Database.query` — obrigar a converter na mão faria o verbo valer menos justamente onde o dado entra."},
  { code: `linhas := [{"a": 1}, {"a": 5}]
out (linhas >> onde a bigger 2).altura()
`, lang: 'df' },
  {"h2": "Por que contextuais, e não reservadas"},
  {"p": "As seis palavras **não** entram em `KEYWORDS`. Elas valem só logo depois de um `>>`, e continuam livres como nome em todo o resto:"},
  { code: `onde := 1
pegar := 2
agrupar := 3
out onde + pegar + agrupar
`, lang: 'df' },
  {"p": "É o mesmo tratamento das onze palavras do [Kiln](/docs/kiln). `agrupar`, `ordenar` e `pegar` são nomes bons demais para tirar de quem escreve — e este repositório já removeu sete palavras reservadas por serem caras sem entregar nada."},
  {"h2": "O que o analisador confere, e o que ele não pode"},
  {"p": "A expressão de um `onde` **não** é inferida no escopo de fora: os nomes dela são colunas, e o analisador não sabe quais colunas um quadro tem em tempo de análise. Inferir ali acusaria `onde valor bigger 50` com *\"'valor' is not defined\"* — um falso alarme no caminho mais comum do verbo, que é exatamente o que ensina a desligar a verificação inteira."},
  {"p": "O que ele confere é o que consegue provar: que o verbo existe, que `agrupar` é seguido de `resumir`, e o tipo que o pipeline produz."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/dados/quadro", "title": "O Quadro", "desc": "a estrutura por baixo dos verbos"}, {"href": "/docs/pipelines", "title": "Pipelines", "desc": "sift, morph e distill — o operador de origem"}, {"href": "/docs/dados/mapa", "title": "O mapa do ecossistema", "desc": "onde cada peça de dado mora"}]},
];

const headings = [{ id: 'os-seis', text: "Os seis", level: 2 as const }, { id: 'a-coluna-se-escreve-nua', text: "A coluna se escreve nua", level: 2 as const }, { id: 'duas-regras-de-escopo-e-elas-sao-previsiveis', text: "Duas regras de escopo, e elas são previsíveis", level: 2 as const }, { id: 'a-ausencia-nao-passa-no-filtro', text: "A ausência não passa no filtro", level: 2 as const }, { id: 'os-verbos-convivem-com-sift-e-morph', text: "Os verbos convivem com `sift` e `morph`", level: 2 as const }, { id: 'por-que-contextuais-e-nao-reservadas', text: "Por que contextuais, e não reservadas", level: 2 as const }, { id: 'o-que-o-analisador-confere-e-o-que-ele-nao-pode', text: "O que o analisador confere, e o que ele não pode", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Os verbos do pipeline"}
      description={"Seis palavras contextuais que fazem um quadro fluir pelo operador >> — com as colunas escritas nuas."}
      href={"/docs/dados/verbos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
