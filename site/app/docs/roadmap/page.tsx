import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Roadmap",
  description: "O que já foi implementado, o que falta e em que ordem.",
};

const blocos: Bloco[] = [
  {"p": "Esta página reflete o estado real do repositório. O documento completo, com a auditoria técnica que originou o plano, está em `doc/ANALISE_E_ROADMAP.md`."},
  {"h2": "Implementado no 4.0"},
  {"h3": "Núcleo"},
  {"table": {"head": ["Item", "Estado"], "rows": [["Type checker estático", "**feito** — `dataforge check`"], ["Stack traces", "**feito** — arquivo, linha, coluna e cadeia"], ["Records", "**feito** — imutáveis, igualdade estrutural, `with`"], ["Enums", "**feito** — valores associados, integração com `match`"], ["Desestruturação", "**feito** — listas, records, vaults, `...resto`"], ["Spread", "**feito** — literais, vaults, chamadas"], ["Compreensões", "**feito** — de lista e de vault"], ["Null safety", "**feito** — `??` e `?.`"], ["Pattern matching avançado", "**feito** — tipo, sequência, mapa, record, enum, guardas"], ["Generics", "**pendente**"]]}},
  {"h3": "Ferramentas"},
  {"table": {"head": ["Item", "Estado"], "rows": [["Formatter", "**feito** — `dataforge fmt`"], ["Linter", "**feito** — 13 regras"], ["Test runner", "**feito** — `dataforge test`"], ["Doc generator", "**feito** — `dataforge doc`"], ["REPL avançado", "**feito** — `:type`, `:ast`, `:check`, `:load`, histórico"], ["LSP", "**pendente**"], ["Debugger", "**pendente**"]]}},
  {"h3": "Módulos e biblioteca"},
  {"table": {"head": ["Item", "Estado"], "rows": [["`forge.toml`", "**feito** — `init`, `info`, scripts nomeados"], ["Escopo real entre módulos", "**feito** — `relay` controla o que sai"], ["Imports seletivos", "**feito** — `adopt M.{a, b}`"], ["Detecção de ciclos", "**feito**"], ["Sete módulos novos", "**feito** — Time, OS, Crypto, Collections, Serialization, Process, Logging"], ["Package manager", "**feito** — `dataforge add`, semver, lockfile"]]}},
  {"h2": "4.1 — Confiança"},
  {"list": ["**Verificação de exaustividade** em `match` sobre enum: avisar quando um membro ficou de fora. É o item de melhor relação custo/benefício que sobrou.", "**Contrato de trait**: falhar na declaração quando o blueprint não implementa os métodos, em vez de só na chamada.", "**Generics** — `Cluster<T>`, `Vault<K,V>`, ações genéricas."]},
  {"h2": "4.2 — Ferramental"},
  {"list": ["**LSP**: autocomplete, ir-para-definição, renomear, hover com tipos. O analisador já produz diagnósticos com linha e coluna — falta o servidor.", "**Debugger**: breakpoints, passo a passo, inspeção de variáveis.", "**Cobertura de testes** no `dataforge test`."]},
  {"h2": "4.3 — Ecossistema"},
  {"list": ["**Registro hospedado com autenticação** — hoje publicar é abrir um PR no repositório do registro. Basta para começar, mas não escala para milhares de pacotes nem permite revogar uma versão comprometida.", "**Espelho corporativo** — para quem não pode buscar pacotes na internet aberta.", "**`dataforge audit`** — avisar quando uma dependência instalada tem versão com correção conhecida."]},
  {"h2": "5.0 — Runtime"},
  {"list": ["**IR e VM de bytecode** — hoje é interpretador de árvore, sem otimização.", "**Cache de compilação**.", "**Empacotamento** — gerar um executável com runtime embutido."]},
  {"callout": {"tipo": "nota", "texto": "Nenhum usuário reclamou de desempenho ainda. Medir antes de investir é a regra — se você tem um caso real onde a velocidade impede o uso, isso é a melhor forma de priorizar o item."}},
  {"h2": "Concorrência"},
  {"list": ["`Mutex`, `Semaphore`, `Atomic` — hoje só `channel` é seguro", "`receive` bloqueante", "`TaskGroup` e cancelamento", "`parallel` tratando **blocos** em vez de instruções"]},
  {"h2": "Uma decisão pendente"},
  {"p": "`frame`, `train` e `predict` são marcadores sintáticos: existem no lexer, no parser e no interpretador, mas devolvem um vault com `__type__` e nada acontece."},
  {"p": "Ou se implementa — DataFrame de verdade, ajuste de modelo — ou se remove. Manter sintaxe sem semântica é pior que não ter, porque quem lê a referência assume que funciona."},
  {"h2": "Estado verificado"},
  {"table": {"head": ["Verificação", "Resultado"], "rows": [["Testes unitários", "272 passando"], ["Exercícios", "180/180"], ["Exemplos", "42/42"], ["Análise estática sobre o repositório", "0 erros em 233 arquivos"], ["Formatador", "idempotente em 233 arquivos"], ["Módulos da stdlib", "20/20 carregam"], ["Instalação via pip", "funciona em venv limpo"]]}},
];

const headings = [{ id: 'implementado-no-40', text: "Implementado no 4.0", level: 2 as const }, { id: '41--confianca', text: "4.1 — Confiança", level: 2 as const }, { id: '42--ferramental', text: "4.2 — Ferramental", level: 2 as const }, { id: '43--ecossistema', text: "4.3 — Ecossistema", level: 2 as const }, { id: '50--runtime', text: "5.0 — Runtime", level: 2 as const }, { id: 'concorrencia', text: "Concorrência", level: 2 as const }, { id: 'uma-decisao-pendente', text: "Uma decisão pendente", level: 2 as const }, { id: 'estado-verificado', text: "Estado verificado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Roadmap"}
      description={"O que já foi implementado, o que falta e em que ordem."}
      href={"/docs/roadmap"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
