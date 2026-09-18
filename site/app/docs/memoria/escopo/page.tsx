// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/memoria_posse.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escopo de recursos",
  description: "Vários recursos, uma saída: o escopo solta tudo na ordem inversa da entrada — inclusive quando o corpo falha.",
};

const blocos: Bloco[] = [
  {"p": "Um recurso é fácil de fechar. Cinco são fáceis de esquecer — e o esquecimento acontece sempre no mesmo lugar: o caminho de erro. O escopo resolve os dois: tudo o que entra sai junto, e sai na **ordem inversa** da entrada."},
  { code: `adopt Arcane.Posse as P

saida := []
e := P.escopo()

e.dono("conexao", lambda x => saida.append(x))
e.dono("transacao", lambda x => saida.append(x))
arquivo := e.guardar(P.dono("arquivo", lambda x => saida.append(x)))

assert e.quantos() is 3
assert arquivo.usar(lambda x => len(x)) is 7

assert e.soltar() is 3
assert saida is ["arquivo", "transacao", "conexao"]      // do último ao primeiro
assert not e.vivo() and e.soltar() is 0                  // idempotente`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Por que a ordem é inversa", "texto": "O que foi aberto por último costuma depender do que veio antes: a transação depende da conexão. Fechar na ordem da entrada quebraria a transação antes de a conexão dela sair — é a mesma ordem dos destrutores de uma linguagem com RAII, e do `defer` empilhado."}},
  {"h2": "com_escopo: e o caminho de erro também"},
  { code: `adopt Arcane.Posse as P

saida := []

monitor:
    P.com_escopo(lambda e => e.dono("a", lambda x => saida.append(x))
                              .usar(lambda x => trigger "no meio"))
handle Error as e:
    assert e.message is "no meio"

assert saida is ["a"]          // soltou mesmo com o corpo falhando`, lang: 'df' },
  {"p": "E um recurso que falha ao fechar **não** deixa os outros abertos: o escopo solta todos e relata depois — o mesmo raciocínio do `defer`, que também não engole o erro."},
  {"h2": "Quando usar cada um"},
  {"table": {"head": ["Situação", "A peça"], "rows": [["um recurso, um uso", "`P.com(dono, acao)`"], ["vários recursos que saem juntos", "`P.com_escopo(lambda e => …)`"], ["o recurso vive além da ação", "`P.dono(…)` devolvido, e quem recebe solta"], ["muitos donos, saída no último", "`P.compartilhado(…)`"], ["fechar no fim da ação, sem objeto novo", "`defer`, que a linguagem já tem"]]}},
];

const headings = [{ id: 'comescopo-e-o-caminho-de-erro-tambem', text: "com_escopo: e o caminho de erro também", level: 2 as const }, { id: 'quando-usar-cada-um', text: "Quando usar cada um", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Escopo de recursos"}
      description={"Vários recursos, uma saída: o escopo solta tudo na ordem inversa da entrada — inclusive quando o corpo falha."}
      href={"/docs/memoria/escopo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
