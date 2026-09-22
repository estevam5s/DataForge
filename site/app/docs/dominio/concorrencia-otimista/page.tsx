// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Concorrência otimista",
  description: "Dois comandos decididos sobre a mesma versão: um grava, o outro recebe AggregateVersionError — e tenta de novo.",
};

const blocos: Bloco[] = [
  {"p": "Dois saques de 60 chegam juntos numa conta com saldo 100. Os dois leem saldo 100, os dois decidem que podem, os dois gravam — e a conta fica com −20, embora `decidir` recuse saldo insuficiente. A regra estava certa; o problema é que as duas decisões foram tomadas sobre **o mesmo estado**."},
  {"p": "`anexar(fluxo, eventos, versao_esperada)` fecha isso: grava só se o fluxo ainda está na versão que foi lida. O segundo recebe `AggregateVersionError`, relê, e decide de novo — agora vendo o saldo 40."},
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
armazem.anexar("c", [{"nome": "ContaAberta", "dados": {"titular": "Ana"}},
                     {"nome": "Depositado", "dados": {"valor": 100}}])

// os dois leram a MESMA versão
lido := armazem.versao("c")
estado := D.reconstituir(armazem.ler("c"), aplicar)
saque_a := decidir(estado, {"tipo": "sacar", "valor": 60})
saque_b := decidir(estado, {"tipo": "sacar", "valor": 60})

armazem.anexar("c", saque_a, lido)             // o primeiro grava
recusado := no
monitor:
    armazem.anexar("c", saque_b, lido)         // o segundo, não
handle AggregateVersionError:
    recusado := yes
assert recusado
assert D.reconstituir(armazem.ler("c"), aplicar)["saldo"] is 40`, lang: 'df' },
  {"h2": "Tentar de novo — com teto"},
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
armazem.anexar("c", [{"nome": "ContaAberta", "dados": {"titular": "Ana"}}])

action com_retentativa(conta, comando, tentativas := 3):
    cycle i from 1 to tentativas:
        historia := armazem.ler(conta)
        novos := decidir(D.reconstituir(historia, aplicar), comando)
        monitor:
            yield armazem.anexar(conta, novos, len(historia))
        handle AggregateVersionError:
            skip
    trigger $"'{conta}' mudou {tentativas} vezes seguidas; desisti"

assert com_retentativa("c", {"tipo": "depositar", "valor": 10}) is 2`, lang: 'df' },
  {"list": ["**Releia e decida de novo.** Regravar os mesmos eventos ignoraria o que mudou — é exatamente o erro que o conflito existe para impedir.", "**Tenha teto.** Um fluxo disputado demais é sinal de agregado grande demais; retentar para sempre esconde isso.", "**Otimista, porque conflito é raro.** Travar a conta a cada leitura seria pagar sempre por algo que quase nunca acontece."]},
  {"p": "É o mesmo mecanismo do `If-Match` numa API: ver [Edição concorrente](/docs/api/precondicoes)."},
];

const headings = [{ id: 'tentar-de-novo-com-teto', text: "Tentar de novo — com teto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Concorrência otimista"}
      description={"Dois comandos decididos sobre a mesma versão: um grava, o outro recebe AggregateVersionError — e tenta de novo."}
      href={"/docs/dominio/concorrencia-otimista"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
