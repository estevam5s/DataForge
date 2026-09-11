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
  {"callout": {"tipo": "nota", "titulo": "Sobre a numeração", "texto": "A linguagem passou por quatro ciclos internos de desenvolvimento antes de ser publicada. A **1.0.0** é o primeiro lançamento público, e a numeração recomeça aqui — o que veio antes está no histórico do repositório, não no versionamento."}},
  {"h2": "O que a 1.0 entrega"},
  {"h3": "Núcleo"},
  {"table": {"head": ["Item", "Estado"], "rows": [["Analisador estático", "**feito** — `dataforge check`"], ["Stack traces", "**feito** — arquivo, linha, coluna e cadeia"], ["Records", "**feito** — imutáveis, igualdade estrutural, `with`"], ["Enums", "**feito** — valores associados, integração com `match`"], ["Desestruturação", "**feito** — listas, records, vaults, `...resto`"], ["Spread", "**feito** — literais, vaults, chamadas"], ["Compreensões", "**feito** — de lista e de vault"], ["Null safety", "**feito** — `??` e `?.`"], ["Pattern matching", "**feito** — tipo, sequência, mapa, record, enum, guardas"], ["OOP completa", "**feito** — propriedades, estáticos, visibilidade, operadores, abstratos"], ["Generics", "**feito** — `blueprint Pilha<T>`, `action primeiro<T>()`"]]}},
  {"h3": "Ferramentas"},
  {"table": {"head": ["Item", "Estado"], "rows": [["Formatador", "**feito** — `dataforge fmt`"], ["Linter", "**feito** — 13 regras"], ["Executor de testes", "**feito** — `dataforge test`"], ["Gerador de documentação", "**feito** — `dataforge doc`"], ["REPL", "**feito** — `:type`, `:ast`, `:check`, `:load`, histórico"], ["Coloração no editor", "**feito** — `dataforge editor`, instalada pelo instalador"], ["LSP", "**feito** — `dataforge lsp`, 10 recursos"], ["Depurador", "**pendente**"]]}},
  {"h3": "Módulos e biblioteca"},
  {"table": {"head": ["Item", "Estado"], "rows": [["`forge.toml`", "**feito** — `init`, `info`, scripts nomeados"], ["Escopo real entre módulos", "**feito** — `relay` controla o que sai"], ["Imports seletivos", "**feito** — `adopt M.{a, b}`"], ["Detecção de ciclos", "**feito**"], ["22 módulos, 753 símbolos", "**feito**"], ["Gerenciador de pacotes", "**feito** — `dataforge add`, semver, lockfile"], ["Kiln — framework web", "**feito** — sintaxe própria, 46 funções"], ["Planilhas `.xlsx`", "**feito** — `Arcane.Excel`, sem dependência"]]}},
  {"h2": "1.1 — Confiança"},
  {"list": ["**Verificação de exaustividade** em `match` sobre enum: avisar quando um membro ficou de fora. É o item de melhor relação custo/benefício que sobrou.", "**Contrato de trait**: falhar na declaração quando o blueprint não implementa os métodos, em vez de só na chamada.", "**Generics com restrição** — hoje `<T>` documenta e o analisador o aceita; falta `<T extends Comparable>` para o checker provar mais.", "**Menos unário no formatador**: hoje `yield -1` vira `yield - 1`, e por isso ninguém roda `dataforge fmt`."]},
  {"h2": "1.2 — Ferramental"},
  {"list": ["**Depurador**: breakpoints, passo a passo, inspeção de variáveis.", "**Cobertura de testes** no `dataforge test`."]},
  {"h2": "1.3 — Ecossistema"},
  {"list": ["**Registro hospedado com autenticação** — hoje publicar é abrir um PR no repositório do registro. Basta para começar, mas não escala para milhares de pacotes nem permite revogar uma versão comprometida.", "**Espelho corporativo** — para quem não pode buscar pacotes na internet aberta.", "**`dataforge audit`** — avisar quando uma dependência instalada tem versão com correção conhecida."]},
  {"h2": "2.0 — Runtime"},
  {"list": ["**IR e máquina virtual de bytecode** — hoje é interpretador de árvore com **compilação para fechamentos**, que já rende de 1,23× a 1,80×.", "**Cache de compilação**."]},
  {"callout": {"tipo": "nota", "titulo": "O que a medição já disse", "texto": "Um protótipo de VM de bytecode em Python deu 7,9×, e o de fechamentos preservando a semântica inteira deu 6,5×. Mesma ordem de grandeza — a VM não é o salto que o nome sugere, porque ela também rodaria em Python. Medir antes de investir é a regra; se você tem um caso real onde a velocidade impede o uso, é a melhor forma de priorizar o item."}},
  {"h2": "Concorrência"},
  {"list": ["`Mutex`, `Semaphore`, `Atomic` — hoje só `channel` é seguro", "`receive` bloqueante", "`TaskGroup` e cancelamento", "`parallel` tratando **blocos** em vez de instruções", "Isolamento de transação por thread no `Arcane.Database` — hoje a conexão serializa os acessos, mas duas threads em `begin`/`commit` compartilham a mesma transação"]},
  {"h2": "Uma decisão pendente"},
  {"p": "`frame`, `train` e `predict` são marcadores sintáticos: existem no lexer, no parser e no interpretador, mas devolvem um vault com `__type__` e nada acontece."},
  {"p": "Ou se implementa — DataFrame de verdade, ajuste de modelo — ou se remove. Manter sintaxe sem semântica é pior que não ter, porque quem lê a referência assume que funciona."},
  {"h2": "Estado verificado"},
  {"table": {"head": ["Verificação", "Resultado"], "rows": [["Testes automatizados", "502 passando"], ["Exercícios", "200/200"], ["Exemplos", "42/42"], ["Projetos completos", "4, com 61 testes"], ["Análise estática sobre o repositório", "0 erros em 302 arquivos"], ["Módulos da biblioteca", "22/22 carregam"], ["Instalação via `curl \| sh`", "verificada em produção"], ["Imagem Docker", "amd64 e arm64, verificada após `docker pull`"]]}},
];

const headings = [{ id: 'o-que-a-10-entrega', text: "O que a 1.0 entrega", level: 2 as const }, { id: 'nucleo', text: "Núcleo", level: 3 as const }, { id: 'ferramentas', text: "Ferramentas", level: 3 as const }, { id: 'modulos-e-biblioteca', text: "Módulos e biblioteca", level: 3 as const }, { id: '11-confianca', text: "1.1 — Confiança", level: 2 as const }, { id: '12-ferramental', text: "1.2 — Ferramental", level: 2 as const }, { id: '13-ecossistema', text: "1.3 — Ecossistema", level: 2 as const }, { id: '20-runtime', text: "2.0 — Runtime", level: 2 as const }, { id: 'concorrencia', text: "Concorrência", level: 2 as const }, { id: 'uma-decisao-pendente', text: "Uma decisão pendente", level: 2 as const }, { id: 'estado-verificado', text: "Estado verificado", level: 2 as const }];

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
