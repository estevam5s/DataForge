// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Exercícios",
  description: "217 exercícios em 27 módulos, cada um verificando o próprio resultado.",
};

const blocos: Bloco[] = [
  {"h2": "Como funcionam"},
  {"p": "Cada exercício **verifica o próprio resultado com `assert`** — se ele roda sem erro, está correto. Não há gabarito separado: o código é a resposta e o teste ao mesmo tempo."},
  { code: `python3 exercicios/run_all.py          # todos os 217
python3 exercicios/run_all.py 14       # só o módulo 14
python3 exercicios/run_all.py 03 07    # módulos 03 e 07

dataforge run exercicios/01-fundamentos/001_ola_mundo.df`, lang: 'bash' },
  {"p": "Os módulos **11 a 27** trazem um arquivo `.md` ao lado de cada `.df`, com enunciado, conceitos, saída esperada e sugestões para experimentar."},
  {"callout": {"tipo": "nota", "titulo": "Eles rodam a cada mudança", "texto": "Os 217 são executados na suíte do repositório. Um exercício que quebrasse com uma mudança na linguagem apareceria no mesmo instante — é por isso que os exemplos desta documentação podem ser citados sem medo."}},
  {"h2": "Os 27 módulos"},
  {"table": {"head": ["Módulo", "Exercícios", "Assunto"], "rows": [["[**01 · Fundamentos**](/docs/exercicios/01-fundamentos)", "12", "tipos, operadores, precedência, conversão e anotações"], ["[**02 · Controle fluxo**](/docs/exercicios/02-controle-fluxo)", "12", "given/orif/otherwise, ternário, match e guardas"], ["[**03 · Colecoes**](/docs/exercicios/03-colecoes)", "14", "cluster e vault, fatias, spread e compreensões"], ["[**04 · Strings**](/docs/exercicios/04-strings)", "10", "interpolação, métodos de texto, formatação e regex"], ["[**05 · Acoes**](/docs/exercicios/05-acoes)", "14", "parâmetros, padrões, retorno, closures e recursão"], ["[**06 · Blueprints**](/docs/exercicios/06-blueprints)", "14", "campos, métodos, herança, traits e records"], ["[**07 · Erros**](/docs/exercicios/07-erros)", "10", "monitor/handle/ensure, trigger, retry e defer"], ["[**08 · Pipelines**](/docs/exercicios/08-pipelines)", "12", "sift, morph, distill e composição"], ["[**09 · Modulos**](/docs/exercicios/09-modulos)", "12", "adopt, relay, seleção e apelidos"], ["[**10 · Avancado**](/docs/exercicios/10-avancado)", "10", "decoradores, generators, threads e canais"], ["[**11 · Tipos e checagem**](/docs/exercicios/11-tipos-e-checagem)", "6", "anotações, o analisador estático e generics"], ["[**12 · Records e enums**](/docs/exercicios/12-records-e-enums)", "6", "imutabilidade, 'with' e enums com valor"], ["[**13 · Desestruturacao**](/docs/exercicios/13-desestruturacao)", "6", "cluster, vault, rest e troca de variáveis"], ["[**14 · Pattern matching**](/docs/exercicios/14-pattern-matching)", "6", "point, when, tipos, sequências e vaults"], ["[**15 · Streams e generators**](/docs/exercicios/15-streams-e-generators)", "6", "stream action, emit, take e sequências infinitas"], ["[**16 · Modulos e projetos**](/docs/exercicios/16-modulos-e-projetos)", "6", "forge.toml, pacotes e organização"], ["[**17 · Tempo e sistema**](/docs/exercicios/17-tempo-e-sistema)", "6", "datas, durações, ambiente e processos"], ["[**18 · Dados e persistencia**](/docs/exercicios/18-dados-e-persistencia)", "6", "JSON, CSV, SQLite e serialização"], ["[**19 · Concorrencia**](/docs/exercicios/19-concorrencia)", "6", "threads, canais, tarefas e paralelismo"], ["[**20 · Projetos finais**](/docs/exercicios/20-projetos-finais)", "6", "programas completos, de ponta a ponta"], ["[**21 · Oop avancado**](/docs/exercicios/21-oop-avancado)", "10", "propriedades, estáticos, operadores, SOLID"], ["[**22 · Web kiln**](/docs/exercicios/22-web-kiln)", "7", "rotas, respostas, templates e estáticos"], ["[**23 · Dados e planilhas**](/docs/exercicios/23-dados-e-planilhas)", "3", "frames, agregação e .xlsx"], ["[**24 · Banco de dados**](/docs/exercicios/24-banco-de-dados)", "8", "Forge: conexão, consultas, transações e ORM"], ["[**25 · Testes crucible**](/docs/exercicios/25-testes-crucible)", "4", "suítes, matchers, fixtures e dublês"], ["[**26 · Complexidade**](/docs/exercicios/26-complexidade)", "4", "Big-O, memoização e custo de estrutura"], ["[**27 · Ponte python**](/docs/exercicios/27-ponte-python)", "1", ""]]}},
];

const headings = [{ id: 'como-funcionam', text: "Como funcionam", level: 2 as const }, { id: 'os-27-modulos', text: "Os 27 módulos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Exercícios"}
      description={"217 exercícios em 27 módulos, cada um verificando o próprio resultado."}
      href={"/docs/exercicios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
