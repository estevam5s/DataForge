// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Processos e sagas",
  description: "Quando um fato de um agregado precisa virar comando em outro: o gerente de processo, e a compensação.",
};

const blocos: Bloco[] = [
  {"p": "Um agregado protege a **própria** consistência, e só ela. \"Quando o pagamento for confirmado, reservar o estoque\" atravessa dois agregados — e não cabe dentro de nenhum. Quem liga os dois é um **processo**: ele escuta fatos e emite comandos."},
  { code: `adopt Arcane.Dominio as D

armazem := D.armazem()
estoque := {"cafe": 1}
log := []

action processo_de_pedido(r):
    given r["nome"] is "PagamentoConfirmado":
        item := r["dados"]["item"]
        given estoque[item] bigger 0:
            estoque[item] -= 1
            armazem.anexar(r["fluxo"], [{"nome": "EstoqueReservado", "dados": {"item": item}}])
        otherwise:
            // não há como reservar: compensar o que já aconteceu
            armazem.anexar(r["fluxo"], [{"nome": "PagamentoEstornado", "dados": {"motivo": "sem estoque"}}])
    given r["nome"] in ["EstoqueReservado", "PagamentoEstornado"]:
        log.append(r["nome"])

armazem.assinar(processo_de_pedido)
armazem.anexar("pedido-1", [{"nome": "PagamentoConfirmado", "dados": {"item": "cafe"}}])
armazem.anexar("pedido-2", [{"nome": "PagamentoConfirmado", "dados": {"item": "cafe"}}])

assert log is ["EstoqueReservado", "PagamentoEstornado"]`, lang: 'df' },
  {"h2": "Compensar não é desfazer"},
  {"p": "O pagamento do pedido 2 **aconteceu**: o dinheiro saiu da conta de alguém. Não existe apagar esse fato; existe um fato novo — `PagamentoEstornado` — que o compensa. É o que dá à fonte de eventos o histórico honesto: quem lê vê que houve pagamento e estorno, e por quê."},
  {"p": "Quando os passos atravessam **serviços** por rede, e não agregados no mesmo processo, a peça é a `Saga` do [`Arcane.Malha`](/docs/tecnicas/microservicos): ela compensa em ordem inversa e anota a compensação que falhou."},
];

const headings = [{ id: 'compensar-nao-e-desfazer', text: "Compensar não é desfazer", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Processos e sagas"}
      description={"Quando um fato de um agregado precisa virar comando em outro: o gerente de processo, e a compensação."}
      href={"/docs/dominio/processos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
