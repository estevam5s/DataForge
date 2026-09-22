// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Atores",
  description: "P.ator: o estado mora numa thread, as mensagens chegam numa fila, e o erro de uma mensagem não derruba o ator.",
};

const blocos: Bloco[] = [
  {"p": "A trava protege o estado **se** todo mundo lembrar de tomá-la. O ator tira a escolha: o estado mora numa thread própria, e as outras não têm como tocá-lo — só **enviar** uma mensagem. As mensagens entram numa fila e são tratadas uma de cada vez, na ordem de chegada. O ler-modificar-escrever que perde atualização não tem como acontecer."},
  { code: `adopt Arcane.Concurrent as P

action conta(saldo, msg):
    given msg["tipo"] is "sacar" and msg["valor"] bigger saldo:
        trigger "saldo insuficiente"
    yield saldo + msg["valor"] given msg["tipo"] is "depositar" otherwise saldo - msg["valor"]

caixa := P.ator(conta, 100, "caixa")
caixa.enviar({"tipo": "depositar", "valor": 50})
caixa.enviar({"tipo": "sacar", "valor": 500})          // recusado — o ator segue
caixa.enviar({"tipo": "sacar", "valor": 30})

assert caixa.consultar(lambda saldo: saldo) is 120
assert len(caixa.falhas()) is 1
out caixa.falhas()[0]["erro"]`, lang: 'df' },
  {"table": {"head": ["Método", "Faz"], "rows": [["`enviar(msg)`", "põe na fila e volta na hora — não espera o tratamento"], ["`consultar(acao, prazo)`", "roda `acao(estado)` **dentro** do ator, na fila, e devolve o resultado"], ["`parar()`", "trata o que já está na fila, para, e devolve o estado final"], ["`falhas()`", "as mensagens que levantaram, com o erro"], ["`pendentes()` · `processadas()` · `vivo()`", "o estado da fila"]]}},
  {"h2": "A consulta entra na fila"},
  {"p": "`consultar` não lê o estado de fora — isso seria a corrida de volta. Ela entra na **mesma** fila das mensagens, e por isso vê o estado depois de tudo que foi enviado antes dela, e nunca no meio de uma mensagem."},
  {"h2": "O erro não derruba o ator"},
  {"p": "Uma mensagem que levanta é anotada, e o ator **segue com o estado de antes** — a estratégia \"retomar\" dos supervisores do Erlang e do Akka. Um ator que morresse na primeira mensagem ruim derrubaria tudo que depende dele por causa de uma mensagem. Para reagir à falha, `P.ator(comportamento, estado, nome, ao_falhar)`."},
  {"callout": {"tipo": "atencao", "titulo": "Uma thread por ator", "texto": "Cada ator é uma thread do sistema. Dezenas de atores, tudo bem; um por usuário de um sistema com cem mil usuários, não. Para muitas entidades pequenas, um ator por **partição** (por exemplo, por hash do id) com um vault dentro."}},
];

const headings = [{ id: 'a-consulta-entra-na-fila', text: "A consulta entra na fila", level: 2 as const }, { id: 'o-erro-nao-derruba-o-ator', text: "O erro não derruba o ator", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Atores"}
      description={"P.ator: o estado mora numa thread, as mensagens chegam numa fila, e o erro de uma mensagem não derruba o ator."}
      href={"/docs/concorrencia/atores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
