import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Hierarquia de erros",
  description: "Os tipos de erro, quando ocorrem e como capturá-los.",
};

const blocos: Bloco[] = [
  {"h2": "Os tipos"},
  {"table": {"head": ["Tipo", "Quando ocorre"], "rows": [["`SyncError`", "indentação inconsistente ou tab"], ["`LexError`", "caractere inválido, texto não terminado"], ["`ParseError`", "sintaxe inválida"], ["`RuntimeError_`", "divisão por zero, `assert` falso, operação inválida"], ["`TypeError_`", "tipo incompatível, aridade errada"], ["`NameError_`", "nome não definido"], ["`IndexError_`", "índice ou chave fora de alcance"], ["`ImportError_`", "módulo não encontrado ou ciclo de importação"], ["`TriggerError`", "lançado por `trigger`, `guard` ou `validate`"], ["`StackOverflowError_`", "recursão além de 1000 quadros"]]}},
  {"p": "Os três primeiros acontecem **antes** de executar — são erros de leitura do arquivo. O `dataforge check` os encontra sem rodar nada."},
  {"h2": "Capturar por tipo"},
  { code: `monitor:
    x := 1 / 0
handle RuntimeError as e:
    out $"{e.type}: {e.message}"` },
  {"p": "No `handle`, use o nome **sem** o sublinhado final: `RuntimeError`, `TypeError`, `NameError`, `IndexError`, `ImportError`, `TriggerError`, `StackOverflowError`."},
  {"p": "Se o erro não casar com o tipo, ele **continua subindo**. Os nomes `Error`, `Exception` e `Any` capturam qualquer erro."},
  {"h2": "O objeto de erro"},
  {"table": {"head": ["Campo", "Contém"], "rows": [["`.type`", "o nome do tipo, sem sublinhado"], ["`.message`", "a mensagem"], ["`.line` `.column`", "a posição de origem"]]}},
  {"p": "Ele também se comporta como texto ao ser concatenado ou comparado com uma `String`."},
  {"h2": "Sinais de controle"},
  {"p": "`halt`, `skip` e `yield` **não são erros**. Eles derivam de uma classe separada e por isso **atravessam** blocos `monitor` sem serem capturados:"},
  { code: `action f():
    monitor:
        yield 42          # retorna 42 — NÃO cai no handle
    handle e:
        out "nao chega aqui"` },
  {"p": "Isso foi um bug corrigido no 3.1: antes, um `yield` dentro de `monitor` era engolido e a ação devolvia `void`."},
  {"h2": "Um monitor sem handle"},
  {"p": "Não engole o erro — só garante o `ensure` e deixa o erro subir. Silenciar deve ser sempre explícito."},
  {"h2": "Stack traces"},
  { code: `RuntimeError: Division by zero
  em calculadora.df:12:15

    12 |     yield total / divisor
       |           ^

  Pilha de chamadas (mais recente primeiro):
    em media                  calculadora.df:12
    em relatorio              calculadora.df:28`, lang: 'text' },
];

const headings = [{ id: 'os-tipos', text: "Os tipos", level: 2 as const }, { id: 'capturar-por-tipo', text: "Capturar por tipo", level: 2 as const }, { id: 'o-objeto-de-erro', text: "O objeto de erro", level: 2 as const }, { id: 'sinais-de-controle', text: "Sinais de controle", level: 2 as const }, { id: 'um-monitor-sem-handle', text: "Um monitor sem handle", level: 2 as const }, { id: 'stack-traces', text: "Stack traces", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Hierarquia de erros"}
      description={"Os tipos de erro, quando ocorrem e como capturá-los."}
      href={"/referencia/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
