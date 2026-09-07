import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Exercícios",
  description: "180 exercícios em 20 módulos, do \"Olá, mundo\" a um interpretador com lexer, parser e avaliador.",
};

const blocos: Bloco[] = [
  {"h2": "Como funcionam"},
  {"p": "Cada exercício **verifica o próprio resultado com `assert`** — se ele roda sem erro, está correto. Não há gabarito separado: o código é a resposta e o teste ao mesmo tempo."},
  { code: `python3 exercicios/run_all.py          # todos os 180
python3 exercicios/run_all.py 14       # só o módulo 14
python3 exercicios/run_all.py 03 07    # módulos 03 e 07

dataforge run exercicios/01-fundamentos/001_ola_mundo.df`, lang: 'bash' },
  {"p": "Os módulos **11 a 20** trazem um arquivo `.md` ao lado de cada `.df`, com enunciado, conceitos, saída esperada e sugestões para experimentar."},
  {"h2": "Os vinte módulos"},
  {"table": {"head": ["Módulo", "N", "Tema"], "rows": [["[01 · Fundamentos](/exercicios/01-fundamentos)", "12", "tipos, operadores, precedência, conversão e anotações"], ["[02 · Controle de fluxo](/exercicios/02-controle-fluxo)", "12", "condicionais, os quatro laços, `halt`/`skip` e `guard`"], ["[03 · Coleções](/exercicios/03-colecoes)", "14", "clusters, fatiamento, vaults, matrizes, busca e ordenação"], ["[04 · Textos](/exercicios/04-strings)", "10", "métodos, regex, templates, palíndromo e cifra de César"], ["[05 · Ações](/exercicios/05-acoes)", "14", "aridade, recursão, closures, lambdas, decoradores e `defer`"], ["[06 · Blueprints](/exercicios/06-blueprints)", "14", "herança, `root`, traits, polimorfismo e padrões de projeto"], ["[07 · Tratamento de erros](/exercicios/07-erros)", "10", "`monitor`, `handle` tipado, `guard`, `retry` e `propagate`"], ["[08 · Pipelines](/exercicios/08-pipelines)", "12", "`sift`/`morph`/`distill`, composição, currying e streams"], ["[09 · Módulos](/exercicios/09-modulos)", "12", "`adopt` local e da stdlib, Math, Analytics, IO e SQLite"], ["[10 · Avançado](/exercicios/10-avancado)", "10", "async, threads, canais, árvore binária e interpretador RPN"], ["[11 · Tipos e checagem](/exercicios/11-tipos-e-checagem)", "6", "anotações, ações tipadas, `typeof`, `cast` e `dataforge check` · com `.md`"], ["[12 · Records e enums](/exercicios/12-records-e-enums)", "6", "imutabilidade, `with`, métodos e enums com valores · com `.md`"], ["[13 · Desestruturação](/exercicios/13-desestruturacao)", "6", "`...resto`, spread, compreensões e interpolação · com `.md`"], ["[14 · Pattern matching](/exercicios/14-pattern-matching)", "6", "literais, tipos, sequências, records, vaults e guardas · com `.md`"], ["[15 · Streams e generators](/exercicios/15-streams-e-generators)", "6", "`stream action`, `emit`, infinitos e ETL · com `.md`"], ["[16 · Módulos e projetos](/exercicios/16-modulos-e-projetos)", "6", "`adopt`/`relay`, camadas, `forge.toml` e testes · com `.md`"], ["[17 · Tempo e sistema](/exercicios/17-tempo-e-sistema)", "6", "datas, cronômetro, SO, processos e logging · com `.md`"], ["[18 · Dados e persistência](/exercicios/18-dados-e-persistencia)", "6", "serialização, arquivos, SQLite e HTTP · com `.md`"], ["[19 · Concorrência](/exercicios/19-concorrencia)", "6", "`async`/`await`, threads, canais, `defer` e `retry` · com `.md`"], ["[20 · Projetos finais](/exercicios/20-projetos-finais)", "6", "CLI, análise de dados, interpretador e revisão · com `.md`"]]}},
  {"h2": "Trilhas"},
  {"table": {"head": ["Se você quer…", "Comece por"], "rows": [["aprender a linguagem do zero", "01 → 10, na ordem"], ["conhecer os recursos do 4.0", "11 → 16"], ["escrever programas de verdade", "16 → 20"], ["dominar pattern matching", "12, 14"], ["trabalhar com dados", "03, 08, 15, 18, 20"], ["construir uma aplicação", "16, 17, 18, 19, 20"]]}},
  {"h2": "Como estudar"},
  {"p": "Cada arquivo começa com o número, o título e o enunciado:"},
  { code: `// Exercicio 134 — Resto e spread
// Enunciado: colete o que sobra com ...resto e expanda colecoes com ...` },
  {"p": "Leia o enunciado, tente resolver por conta, depois compare. Os `assert` no fim documentam exatamente o comportamento esperado — inclusive os casos de borda."},
];

const headings = [{ id: 'como-funcionam', text: "Como funcionam", level: 2 as const }, { id: 'os-vinte-modulos', text: "Os vinte módulos", level: 2 as const }, { id: 'trilhas', text: "Trilhas", level: 2 as const }, { id: 'como-estudar', text: "Como estudar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Exercícios"}
      description={"180 exercícios em 20 módulos, do \"Olá, mundo\" a um interpretador com lexer, parser e avaliador."}
      href={"/exercicios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
