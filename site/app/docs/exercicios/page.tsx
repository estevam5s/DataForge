// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Exercícios",
  description: "264 exercícios em 46 módulos, cada um verificando o próprio resultado.",
};

const blocos: Bloco[] = [
  {"h2": "Como funcionam"},
  {"p": "Cada exercício **verifica o próprio resultado com `assert`** — se ele roda sem erro, está correto. Não há gabarito separado: o código é a resposta e o teste ao mesmo tempo."},
  { code: `python3 exercicios/run_all.py          # todos os 264
python3 exercicios/run_all.py 14       # só o módulo 14
python3 exercicios/run_all.py 03 07    # módulos 03 e 07

dataforge run exercicios/01-fundamentos/001_ola_mundo.df`, lang: 'bash' },
  {"p": "Os módulos **11 a 46** trazem um arquivo `.md` ao lado de cada `.df`, com enunciado, conceitos, saída esperada e sugestões para experimentar."},
  {"callout": {"tipo": "nota", "titulo": "Eles rodam a cada mudança", "texto": "Os 264 são executados na suíte do repositório. Um exercício que quebrasse com uma mudança na linguagem apareceria no mesmo instante — é por isso que os exemplos desta documentação podem ser citados sem medo."}},
  {"h2": "Os 46 módulos"},
  {"table": {"head": ["Módulo", "Exercícios", "Assunto"], "rows": [["[**01 · Fundamentos**](/docs/exercicios/01-fundamentos)", "12", "tipos, operadores, precedência, conversão e anotações"], ["[**02 · Controle de fluxo**](/docs/exercicios/02-controle-fluxo)", "12", "given/orif/otherwise, ternário, match e guardas"], ["[**03 · Coleções**](/docs/exercicios/03-colecoes)", "14", "cluster e vault, fatias, spread e compreensões"], ["[**04 · Textos**](/docs/exercicios/04-strings)", "10", "interpolação, métodos de texto, formatação e regex"], ["[**05 · Ações**](/docs/exercicios/05-acoes)", "14", "parâmetros, padrões, retorno, closures e recursão"], ["[**06 · Blueprints**](/docs/exercicios/06-blueprints)", "14", "campos, métodos, herança, traits e records"], ["[**07 · Erros**](/docs/exercicios/07-erros)", "10", "monitor/handle/ensure, trigger, retry e defer"], ["[**08 · Pipelines**](/docs/exercicios/08-pipelines)", "12", "sift, morph, distill e composição"], ["[**09 · Módulos**](/docs/exercicios/09-modulos)", "12", "adopt, relay, seleção e apelidos"], ["[**10 · Avançado**](/docs/exercicios/10-avancado)", "10", "decoradores, generators, threads e canais"], ["[**11 · Tipos e checagem**](/docs/exercicios/11-tipos-e-checagem)", "6", "anotações, o analisador estático e generics"], ["[**12 · Records e enums**](/docs/exercicios/12-records-e-enums)", "6", "imutabilidade, 'with' e enums com valor"], ["[**13 · Desestruturação**](/docs/exercicios/13-desestruturacao)", "6", "cluster, vault, rest e troca de variáveis"], ["[**14 · Pattern matching**](/docs/exercicios/14-pattern-matching)", "6", "point, when, tipos, sequências e vaults"], ["[**15 · Streams**](/docs/exercicios/15-streams-e-generators)", "6", "stream action, emit, take e sequências infinitas"], ["[**16 · Módulos e projetos**](/docs/exercicios/16-modulos-e-projetos)", "7", "forge.toml, pacotes e organização"], ["[**17 · Tempo e sistema**](/docs/exercicios/17-tempo-e-sistema)", "6", "datas, durações, ambiente e processos"], ["[**18 · Persistência**](/docs/exercicios/18-dados-e-persistencia)", "6", "JSON, CSV, SQLite e serialização"], ["[**19 · Concorrência**](/docs/exercicios/19-concorrencia)", "6", "threads, canais, tarefas e paralelismo"], ["[**20 · Projetos finais**](/docs/exercicios/20-projetos-finais)", "6", "programas completos, de ponta a ponta"], ["[**21 · OOP avançado**](/docs/exercicios/21-oop-avancado)", "10", "propriedades, estáticos, operadores, SOLID"], ["[**22 · Web com Kiln**](/docs/exercicios/22-web-kiln)", "8", "rotas, respostas, templates e estáticos"], ["[**23 · Dados e planilhas**](/docs/exercicios/23-dados-e-planilhas)", "3", "frames, agregação e .xlsx"], ["[**24 · Banco de dados**](/docs/exercicios/24-banco-de-dados)", "8", "Forge: conexão, consultas, transações e ORM"], ["[**25 · Testes com Crucible**](/docs/exercicios/25-testes-crucible)", "4", "suítes, matchers, fixtures e dublês"], ["[**26 · Complexidade**](/docs/exercicios/26-complexidade)", "4", "Big-O, memoização e custo de estrutura"], ["[**27 · Ponte para o Python**](/docs/exercicios/27-ponte-python)", "1", "adopt Python.*: numpy, pandas e o que vem junto"], ["[**28 · Vitrine**](/docs/exercicios/28-vitrine)", "1", "painéis e aplicações de dados sem escrever HTML"], ["[**29 · Banco e CRUD**](/docs/exercicios/29-banco-e-crud)", "4", "transações, upsert, busca textual e paginação"], ["[**30 · Tempo real**](/docs/exercicios/30-tempo-real)", "2", "upload, SSE e WebSocket no Kiln"], ["[**31 · Qualidade**](/docs/exercicios/31-qualidade)", "3", "check, lint, cobertura e o que o CI cobra"], ["[**32 · Microserviços**](/docs/exercicios/32-microservicos)", "2", "Arcane.Malha: retry, disjuntor, rastro e saga"], ["[**33 · Lavra**](/docs/exercicios/33-lavra)", "3", "esquema, consulta, lote contra o N+1, servidor e federação"], ["[**34 · Binário e rede**](/docs/exercicios/34-binario-e-rede)", "3", "dados binários, TCP/UDP/DNS, eventos, CLI, e-mail e HTML"], ["[**35 · Paralelismo**](/docs/exercicios/35-paralelismo)", "3", ""], ["[**36 · Quadro e dados**](/docs/exercicios/36-quadro-e-dados)", "1", ""], ["[**37 · OOP como sistema**](/docs/exercicios/37-oop-sistema)", "10", ""], ["[**38 · Sistema de tipos**](/docs/exercicios/38-tipos)", "5", ""], ["[**39 · Concorrência avançada**](/docs/exercicios/39-concorrencia-avancada)", "1", ""], ["[**40 · Metaprogramação**](/docs/exercicios/40-metaprogramacao)", "1", ""], ["[**41 · FFI e nativo**](/docs/exercicios/41-ffi-nativo)", "1", ""], ["[**42 · Dentro do compilador**](/docs/exercicios/42-compilador)", "1", ""], ["[**43 · Backend e otimização**](/docs/exercicios/43-backend)", "1", ""], ["[**44 · Runtime e laço de eventos**](/docs/exercicios/44-runtime)", "1", ""], ["[**45 · Observabilidade e memória**](/docs/exercicios/45-observabilidade)", "1", ""], ["[**46 · Partida, pilha e capacidade**](/docs/exercicios/46-partida)", "1", ""]]}},
];

const headings = [{ id: 'como-funcionam', text: "Como funcionam", level: 2 as const }, { id: 'os-46-modulos', text: "Os 46 módulos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Exercícios"}
      description={"264 exercícios em 46 módulos, cada um verificando o próprio resultado."}
      href={"/docs/exercicios"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
