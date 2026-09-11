// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "01 · Fundamentos",
  description: "12 exercícios: tipos, operadores, precedência, conversão e anotações.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 01`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["001", "**Ola, mundo**", "imprima uma saudacao e o nome da linguagem em duas linhas."], ["002", "**Variaveis**", "declare uma variavel de cada tipo primitivo e imprima cada uma."], ["003", "**Constantes com steady**", "declare constantes e comprove que reatribuir dispara erro."], ["004", "**Operadores aritmeticos**", "use +, -, *, /, %, ** e a divisao inteira ~/."], ["005", "**Precedencia de operadores**", "comprove a ordem de avaliacao e a associatividade de **."], ["006", "**Comparacoes**", "use as palavras-chave e os simbolos equivalentes."], ["007", "**Operadores logicos**", "monte uma tabela verdade com and, or e not."], ["008", "**Comparacao encadeada**", "verifique se um valor esta dentro de um intervalo em uma unica expressao."], ["009", "**Atribuicao composta**", "use +=, -=, *=, /= e %= para transformar um saldo."], ["010", "**typeof e cast**", "descubra o tipo de cada valor e converta entre tipos."], ["011", "**Anotacoes de tipo**", "declare variaveis tipadas e comprove que o tipo errado dispara erro."], ["012", "**Interpolacao e formatacao de saida**", "monte uma linha de relatorio combinando texto e numeros."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/01-fundamentos/001_ola_mundo.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"01 · Fundamentos"}
      description={"12 exercícios: tipos, operadores, precedência, conversão e anotações."}
      href={"/docs/exercicios/01-fundamentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
