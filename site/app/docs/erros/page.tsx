import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Tratamento de erros",
  description: "monitor, handle tipado, ensure, guard, validate, retry, propagate, defer e stack traces.",
};

const blocos: Bloco[] = [
  {"h2": "monitor / handle / ensure"},
  { code: `monitor:
    x := 10 / 0
handle e:
    out $"capturado: {e.type} — {e.message}"
ensure:
    out "sempre roda"` },
  { code: `capturado: RuntimeError — Division by zero
sempre roda`, lang: 'text', title: `saída` },
  {"callout": {"tipo": "nota", "titulo": "Um monitor sem handle não engole o erro", "texto": "Ele só garante o `ensure` e deixa o erro subir. Isso é deliberado: silenciar um erro deve ser sempre explícito."}},
  {"h2": "O objeto de erro"},
  {"p": "O nome ligado pelo `handle` expõe:"},
  {"table": {"head": ["Campo", "Contém"], "rows": [["`.type`", "o nome do tipo, ex. `\"RuntimeError\"`"], ["`.message`", "a mensagem"], ["`.line` `.column`", "a posição de origem"]]}},
  {"p": "Ele também se comporta como texto ao ser concatenado ou comparado com uma `String`."},
  {"h3": "handle tipado"},
  { code: `monitor:
    x := 1 / 0
handle RuntimeError as e:
    out $"só pego erro de execução: {e.message}"` },
  {"p": "Se o erro não casar com o tipo, ele **continua subindo** — não é capturado ali. Os tipos disponíveis estão em [Hierarquia de erros](/docs/referencia/erros)."},
  {"h3": "Vários handle"},
  {"p": "Um `monitor` aceita uma cláusula por tipo de erro. Vence a **primeira que casar** — a ordem importa, como nos `point` de um `match`:"},
  { code: `action ler(vault, chave, divisor):
    monitor:
        yield vault[chave] / divisor
    handle KeyError:
        yield 0
    handle DivisionByZeroError as e:
        out e.message
        yield 0
    handle Error as e:
        propagate` },
  {"p": "Sem isso, tratar dois erros de formas diferentes obrigava a capturar `Error` e despachar na mão com um `match e.type` — que é exatamente o que o `handle` tipado existe para evitar."},
  {"callout": {"tipo": "atencao", "titulo": "Do específico para o geral", "texto": "Um `handle` sem tipo (ou com `Error`) captura tudo e torna **inalcançável** todo `handle` abaixo dele. O `dataforge check` avisa, mas o programa roda mesmo assim — com um bloco que nunca executa."}},
  {"h2": "Lançar"},
  {"table": {"head": ["Forma", "Efeito"], "rows": [["`trigger <expr>`", "lança `TriggerError` com a mensagem"], ["`guard <cond>, <msg>`", "lança se a condição for falsa"], ["`guard <cond> otherwise: bloco`", "roda o bloco e **sai da ação**"], ["`validate <expr>, <msg>`", "lança se o valor for falso"], ["`propagate <expr>`", "relança, depois de registrar"], ["`assert <cond>, <msg>`", "lança `RuntimeError_` se falso"]]}},
  { code: `action sacar(conta, valor):
    guard valor bigger 0, "valor precisa ser positivo"
    guard valor smaller_eq conta.saldo, "saldo insuficiente"
    yield conta with {"saldo": conta.saldo - valor}` },
  {"p": "`guard` na entrada da ação documenta as pré-condições em duas linhas, sem aninhar o corpo inteiro num `given`."},
  {"h2": "retry"},
  {"p": "Repete um bloco até conseguir. Se todas as tentativas falharem, o `handle` roda com o último erro:"},
  { code: `tentativas := {"n": 0}

retry 5:
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] smaller 3:
        trigger "instabilidade temporaria"
    out $"sucesso na tentativa {tentativas["n"]}"
handle e:
    out $"desistiu: {e}"` },
  {"callout": {"tipo": "atencao", "titulo": "Nem todo erro merece retry", "texto": "Repetir um erro **permanente** (senha inválida, 404, dado malformado) é desperdício garantido, e atrasa a mensagem que o usuário precisa ver. Repita apenas o que é **temporário**: timeout, serviço indisponível, conexão recusada."}},
  {"h2": "propagate — registrar e repassar"},
  { code: `action camada_media():
    monitor:
        camada_baixa()
    handle e:
        registro.error("falha na camada baixa", {"motivo": e.message})
        propagate e.message` },
  {"p": "A camada do meio **anota o que sabe** — contexto que o topo não teria — mas não decide o que fazer. Essa decisão pertence a quem tem visão do todo."},
  {"p": "O anti-padrão oposto é engolir: `handle e: registro.error(\"falhou\")` faz o chamador achar que deu certo."},
  {"h2": "defer — limpeza garantida"},
  { code: `action processar():
    IO.write(temp, "dados")
    defer:
        IO.delete(temp)      # roda em QUALQUER caminho de saída

    given deve_falhar:
        trigger "erro no meio"
    yield IO.read(temp)` },
  {"table": {"head": ["Saída", "`defer` roda?"], "rows": [["chegou ao fim", "sim"], ["`yield` no meio", "sim"], ["`trigger` / erro", "sim"], ["erro vindo de uma ação chamada", "sim"]]}},
  {"p": "Vários `defer` rodam em ordem **inversa** (LIFO) — a ordem correta para desmontar recursos dependentes."},
  {"h3": "defer ou ensure?"},
  {"table": {"head": ["", "`defer`", "`ensure`"], "rows": [["Escopo", "a ação inteira", "um bloco `monitor`"], ["Declaração", "junto da aquisição", "no fim do bloco"], ["Vários", "sim, em LIFO", "um por `monitor`"]]}},
  {"h2": "Stack traces"},
  {"p": "Um erro não tratado traz o arquivo, a linha, o trecho do código e a cadeia de chamadas:"},
  { code: `RuntimeError: Division by zero
  em calculadora.df:12:15

    12 |     yield total / divisor
       |           ^

  Pilha de chamadas (mais recente primeiro):
    em media                  calculadora.df:12
    em relatorio              calculadora.df:28
    em main                   calculadora.df:45`, lang: 'text' },
  {"h2": "Onde tratar"},
  {"p": "**Trate o erro onde você pode fazer algo a respeito.** Nas camadas intermediárias, registre e repasse. No topo, decida: mostrar ao usuário, tentar de novo, ou abortar."},
];

const headings = [{ id: 'monitor--handle--ensure', text: "monitor / handle / ensure", level: 2 as const }, { id: 'o-objeto-de-erro', text: "O objeto de erro", level: 2 as const }, { id: 'lancar', text: "Lançar", level: 2 as const }, { id: 'retry', text: "retry", level: 2 as const }, { id: 'propagate--registrar-e-repassar', text: "propagate — registrar e repassar", level: 2 as const }, { id: 'defer--limpeza-garantida', text: "defer — limpeza garantida", level: 2 as const }, { id: 'stack-traces', text: "Stack traces", level: 2 as const }, { id: 'onde-tratar', text: "Onde tratar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Tratamento de erros"}
      description={"monitor, handle tipado, ensure, guard, validate, retry, propagate, defer e stack traces."}
      href={"/docs/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
