// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Serviços de domínio",
  description: "A regra que não pertence a nenhuma entidade — e por que ela não é um 'Manager' com tudo dentro.",
};

const blocos: Bloco[] = [
  {"p": "Transferir dinheiro entre duas contas: a regra é de qual das duas? Nenhuma — e forçá-la dentro de `Conta` faz uma conta mexer na outra, que é exatamente o que o agregado existe para impedir. Uma operação do domínio que **envolve várias** entidades, e não é de nenhuma, é um **serviço de domínio**."},
  { code: `adopt Arcane.Dominio as D

action conta(id, saldo):
    c := D.agregado("Conta", id, saldo := saldo)
    c.invariante("saldo não negativo", lambda x => x.ler("saldo") bigger_eq 0)
    mark @c.comando("debitar")
    action debitar(x, v):
        x.mudar(saldo := x.ler("saldo") - v)
    mark @c.comando("creditar")
    action creditar(x, v):
        x.mudar(saldo := x.ler("saldo") + v)
    yield c

// o serviço: coordena, e deixa cada conta cuidar das próprias regras
action transferir(origem, destino, valor, limite_diario := 1000):
    given valor bigger limite_diario:
        trigger $"transferência acima do limite diário de {limite_diario}"
    origem.debitar(valor)         // se falhar aqui, nada mudou
    destino.creditar(valor)

a := conta("A", 100)
b := conta("B", 0)
transferir(a, b, 70)
assert a.ler("saldo") is 30 and b.ler("saldo") is 70

falhou := no
monitor:
    transferir(a, b, 50)          // a invariante de A recusa
handle Error:
    falhou := yes
assert falhou and a.ler("saldo") is 30 and b.ler("saldo") is 70`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "E se o crédito falhar depois do débito?", "texto": "No exemplo, o débito vem primeiro porque é ele que pode ser recusado. Se o crédito também pudesse falhar, o débito já estaria feito — e os dois precisam de uma [unidade de trabalho](/docs/dominio/eventos) que confirme os dois juntos, ou de um [processo com compensação](/docs/dominio/processos)."}},
  {"p": "O cheiro do serviço mal usado é o **`GerenciadorDeContas`** com trinta métodos: a regra saiu das entidades e elas viraram sacos de dados. Serviço é a exceção, para o que não tem dono — não o lugar padrão de toda regra."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Serviços de domínio"}
      description={"A regra que não pertence a nenhuma entidade — e por que ela não é um 'Manager' com tudo dentro."}
      href={"/docs/dominio/servicos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
