// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dados: e o pandas?",
  description: "Arcane.Quadro, os seis verbos, e quando chamar o pandas de dentro — com a fronteira dita sem rodeio.",
};

const blocos: Bloco[] = [
  {"p": "Há duas respostas, e escolher entre elas é uma decisão de tamanho, não de gosto."},
  {"h2": "A tabela de dados da linguagem"},
  { code: `adopt Arcane.Quadro as Q

vendas := Q.de_vaults([
    {"loja": "centro", "mes": "jan", "valor": 1200},
    {"loja": "centro", "mes": "fev", "valor": 1500},
    {"loja": "praia",  "mes": "jan", "valor": 900},
    {"loja": "praia",  "mes": "fev", "valor": 1100}])

// A forma e {coluna: agregacao}. Com mais de uma, a coluna de saida
// vira 'coluna_agregacao' — e a lista de agregacoes e FECHADA: um nome
// desconhecido e recusado com a lista do que existe, porque ele pode
// vir de um '?agregar=' de uma tela.
resumo := vendas
    >> onde valor bigger 1000
    >> agrupar "loja"
    >> resumir {"valor": ["soma", "contagem"]}

assert len(resumo) is 2
cycle linha in resumo:
    out $"{linha["loja"]}: {linha["valor_soma"]} em {linha["valor_contagem"]} mes(es)"
`, lang: 'df' },
  {"p": "`onde`, `pegar`, `sem`, `ordenar`, `agrupar` e `resumir` são operações do `>>` — e **não** são palavras reservadas: `agrupar` e `ordenar` são nomes bons demais para tirar de quem escreve. O parser as reconhece só logo depois de um `>>`."},
  {"h2": "Cinco decisões que explicam o resto"},
  {"table": {"head": ["Decisão", "Porque"], "rows": [["a linha é um **vault**", "é o que `IO.read_csv(c, yes)` e `Database.query` já devolvem"], ["por dentro é **colunar**", "`descrever` e `correlacao` viram uma passada por coluna"], ["todo verbo devolve um quadro **novo**", "o pipeline fica reexecutável, como `record`/`with`"], ["a ausência tem **um nome só**", "`void`, texto vazio e NaN são a mesma coisa — separá-los é metade do bug de limpeza"], ["coluna que não existe é **erro, com sugestão**", "devolver coluna vazia calada é o jeito mais rápido de um relatório sair errado"]]}},
  {"callout": {"tipo": "nota", "titulo": "`onde` usa a lógica de três valores do SQL", "texto": "Comparar com `void` não faz a linha passar, em vez de levantar. A outra escolha é a que a linguagem faz em toda expressão comum e está certa lá; aqui tornaria o verbo inutilizável, porque todo conjunto real tem ausência. E só essa falha é engolida — reconhecida por uma **marca no objeto de erro**, nunca comparando o texto da mensagem, que quebraria na primeira tradução."}},
  {"h2": "Quando chamar o pandas"},
  {"p": "`adopt Python.pandas as pd` traz a biblioteca inteira, e a ponte **não converte**: um `DataFrame` continua um `DataFrame`, e `df[\"b\"].sum()` é o código do pandas rodando — não um laço daqui. Isso funciona porque o interpretador trata objeto estranho por **protocolo**: membro, método, índice, `len`, iteração, aritmética e verdade já passavam assim."},
  {"p": "O exemplo abaixo usa um módulo da biblioteca do próprio Python, que existe em toda instalação — com o pandas seria idêntico, e este bloco **roda** na verificação da documentação:"},
  { code: `adopt Python.statistics as st

notas := [7.0, 8.5, 6.0, 9.5]
assert st.mean(notas) is 7.75
out $"media {st.mean(notas)}, mediana {st.median(notas)}"
`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O pacote tem de estar no Python que roda a linguagem", "texto": "O instalador cria uma venv em `~/.dataforge`, e um `pip install pandas` no terminal costuma instalar em outro lugar. A mensagem de ausência nomeia o Python exato por causa disso."}},
  {"table": {"head": ["Use o `Quadro` quando", "Use o pandas quando"], "rows": [["o dado cabe na memória com folga", "são milhões de linhas e você precisa de vetorização"], ["você quer zero dependência", "o ambiente já tem a pilha científica"], ["o resultado vai para a Vitrine ou para um relatório", "você vai encadear com scikit-learn, statsmodels…"], ["o programa roda em rede fechada", "há espaço para instalar"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Havia duas tabelas de dados, e elas divergiam", "texto": "`Arcane.Analytics.DataFrame` e `Arcane.Data.Frame` eram classes independentes com `group_by`, `describe`, `normalize`, `merge` e `pivot` implementados **duas vezes** — e `describe` devolvia chaves diferentes conforme o módulo adotado. As duas continuam funcionando (quebrar código que existe seria pior), e `Arcane.Quadro` é a resposta única."}},
  {"cards": [{"href": "/docs/biblioteca/quadro", "title": "Arcane.Quadro", "desc": "a referência"}, {"href": "/docs/vitrine", "title": "Vitrine", "desc": "o painel, com gráfico em SVG"}, {"href": "/docs/bibliotecas/ponte", "title": "A ponte para o Python", "desc": "como ela não converte"}]},
];

const headings = [{ id: 'a-tabela-de-dados-da-linguagem', text: "A tabela de dados da linguagem", level: 2 as const }, { id: 'cinco-decisoes-que-explicam-o-resto', text: "Cinco decisões que explicam o resto", level: 2 as const }, { id: 'quando-chamar-o-pandas', text: "Quando chamar o pandas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Dados: e o pandas?"}
      description={"Arcane.Quadro, os seis verbos, e quando chamar o pandas de dentro — com a fronteira dita sem rodeio."}
      href={"/docs/faq/dados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
