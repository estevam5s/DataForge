// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fonte de eventos",
  description: "O estado não é guardado: é derivado dos fatos. O armazém, as duas funções puras e o que isso compra.",
};

const blocos: Bloco[] = [
  {"p": "Num modelo comum, a tabela guarda o **estado de agora**: o saldo é 70. Numa fonte de eventos, guarda-se **o que aconteceu** — aberta, depositou 100, sacou 30 — e o saldo é uma conta feita sobre isso. A pergunta \"qual era o saldo em março?\" passa a ter resposta, e \"por que o saldo é 70?\" também."},
  {"p": "O modelo inteiro cabe em duas funções **puras**:"},
  {"table": {"head": ["Função", "Recebe", "Devolve", "Pode recusar?"], "rows": [["`decidir`", "o estado e um comando", "os eventos que ele produz", "**sim** — é aqui que mora a regra"], ["`aplicar`", "o estado e um evento", "o estado seguinte", "**nunca** — o fato já aconteceu"]]}},
  { code: `adopt Arcane.Dominio as D

// evoluir: o estado depois de um fato. Pura, e nunca recusa nada.
aplicar := {
    "ContaAberta": lambda s, d: {"titular": d["titular"], "saldo": 0, "aberta": yes},
    "Depositado": lambda s, d: {...s, "saldo": s["saldo"] + d["valor"]},
    "Sacado": lambda s, d: {...s, "saldo": s["saldo"] - d["valor"]},
    "ContaEncerrada": lambda s, d: {...s, "aberta": no}
}

// decidir: os fatos que um comando produz — ou o motivo da recusa.
action decidir(estado, comando):
    tipo := comando["tipo"]
    given tipo is "abrir":
        yield [{"nome": "ContaAberta", "dados": {"titular": comando["titular"]}}]
    given not (estado["aberta"] ?? no):
        trigger "a conta não está aberta"
    given tipo is "depositar":
        yield [{"nome": "Depositado", "dados": {"valor": comando["valor"]}}]
    given tipo is "sacar":
        given comando["valor"] bigger estado["saldo"]:
            trigger $"saldo {estado["saldo"]} não cobre {comando["valor"]}"
        yield [{"nome": "Sacado", "dados": {"valor": comando["valor"]}}]
    trigger $"comando desconhecido: {tipo}"

armazem := D.armazem()

action executar(conta, comando):
    historia := armazem.ler(conta)
    estado := D.reconstituir(historia, aplicar)
    novos := decidir(estado, comando)
    armazem.anexar(conta, novos, len(historia))
    yield D.reconstituir(historia + novos, aplicar)

executar("conta-1", {"tipo": "abrir", "titular": "Ana"})
executar("conta-1", {"tipo": "depositar", "valor": 100})
final := executar("conta-1", {"tipo": "sacar", "valor": 30})
assert final["saldo"] is 70

// a história inteira continua ali
assert [e["nome"] cycle e in armazem.ler("conta-1")] is ["ContaAberta", "Depositado", "Sacado"]

// e o passado tem resposta: o saldo depois do segundo fato
assert D.reconstituir(armazem.ler("conta-1")[0:2], aplicar)["saldo"] is 100`, lang: 'df' },
  {"h2": "Por que `aplicar` nunca recusa"},
  {"p": "Um evento é um fato no passado. Se `aplicar` pudesse recusar `Sacado`, reconstituir uma conta antiga falharia no dia em que a regra de saque mudasse — e o histórico, que é a fonte da verdade, deixaria de ser legível. A regra vive em `decidir`, que só olha o **presente**."},
  {"callout": {"tipo": "atencao", "titulo": "`reconstituir` é estrito", "texto": "Um evento sem aplicador é **erro** (`EventError`). Ignorá-lo chegaria a um estado que a conta nunca teve. A [projeção](/docs/dominio/projecoes), ao contrário, ignora de propósito o que não lhe interessa."}},
  {"table": {"head": ["Compra", "Custa"], "rows": [["auditoria completa, de graça", "reconstituir a cada comando (ou um instantâneo)"], ["responder sobre o passado", "evento nunca muda: um erro vira um evento de correção"], ["novos modelos de leitura a partir do histórico", "projeções a manter"], ["depurar reproduzindo a sequência exata", "um armazém que nunca apaga"]]}},
];

const headings = [{ id: 'por-que-aplicar-nunca-recusa', text: "Por que `aplicar` nunca recusa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fonte de eventos"}
      description={"O estado não é guardado: é derivado dos fatos. O armazém, as duas funções puras e o que isso compra."}
      href={"/docs/dominio/fonte-de-eventos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
