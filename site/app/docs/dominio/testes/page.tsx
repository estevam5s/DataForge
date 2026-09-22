// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar o domínio",
  description: "Dado estes fatos, quando este comando, então estes fatos — ou esta recusa.",
};

const blocos: Bloco[] = [
  {"p": "Com `decidir` puro, o teste do domínio não precisa de banco, de agregado montado nem de dublê: **dado** o histórico, **quando** o comando chega, **então** saem estes eventos — ou esta recusa. O teste lê como a regra, e a regra é o que ele confere."},
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

action dado_quando_entao(historia, comando):
    yield decidir(D.reconstituir(historia, aplicar), comando)

aberta := [{"nome": "ContaAberta", "dados": {"titular": "Ana"}},
           {"nome": "Depositado", "dados": {"valor": 50}}]

// então: o fato certo
assert dado_quando_entao(aberta, {"tipo": "sacar", "valor": 20}) is
    [{"nome": "Sacado", "dados": {"valor": 20}}]

// então: a recusa certa, com o motivo
motivo := void
monitor:
    dado_quando_entao(aberta, {"tipo": "sacar", "valor": 80})
handle Error as e:
    motivo := e.message
assert motivo.contains("não cobre")

// então: nada acontece numa conta encerrada
encerrada := aberta + [{"nome": "ContaEncerrada", "dados": {}}]
monitor:
    dado_quando_entao(encerrada, {"tipo": "depositar", "valor": 1})
    assert no
handle Error as e:
    assert e.message.contains("não está aberta")`, lang: 'df' },
  {"p": "E as invariantes de um agregado se testam pelo lado de fora: tentar o comando que as violaria, e conferir que o estado e a `versao()` não mudaram. Para o formato dado/quando/então com relatório por passo, [`Crucible.cenario`](/docs/testes/bdd)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar o domínio"}
      description={"Dado estes fatos, quando este comando, então estes fatos — ou esta recusa."}
      href={"/docs/dominio/testes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
