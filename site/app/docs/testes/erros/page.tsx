// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/testes_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar erros e exceções",
  description: "Que ele falha, com que tipo, com que mensagem — e que não falhou pela metade.",
};

const blocos: Bloco[] = [
  {"p": "O caminho de erro é o menos testado e o que mais aparece em produção. Três perguntas por falha: **ela acontece?**, **com o tipo certo?**, **deixou tudo como estava?** A terceira é a que quase ninguém escreve."},
  { code: `adopt Arcane.Crucible

record SaldoInsuficiente:
    pedido: Float
    disponivel: Float

contas := {"ana": 100.0, "bia": 0.0}

action transferir(de, para, valor):
    given valor smaller_eq 0:
        trigger "valor precisa ser positivo"
    given contas[de] smaller valor:
        trigger SaldoInsuficiente(valor, contas[de])
    contas[de] -= valor
    contas[para] += valor

crucible "transferir":
    trial "falha com o tipo do dominio":
        monitor:
            transferir("bia", "ana", 10.0)
            Crucible.fail("devia ter levantado")
        handle SaldoInsuficiente as e:
            expect e.value.disponivel is 0.0

    trial "a mensagem diz o que fazer":
        expect(lambda => transferir("ana", "bia", -5)).to_raise()

    trial "a falha nao deixa nada pela metade":
        antes := {"ana": contas["ana"], "bia": contas["bia"]}
        monitor:
            transferir("ana", "bia", 1000.0)
        handle Error:
            antes := antes
        expect contas["ana"] is antes["ana"]
        expect contas["bia"] is antes["bia"]

r := Crucible.run()
assert r["falhou"] is 0 and r["passou"] is 3`, lang: 'df' },
  {"h2": "O que conferir numa falha"},
  {"table": {"head": ["Pergunta", "Como", "Porque"], "rows": [["ela acontece?", "`expect(lambda => …).to_raise()`", "o `lambda` adia a chamada — sem ele o erro estoura antes do `expect`"], ["com o tipo certo?", "`handle SeuTipo as e`", "`handle Error` pega também o `1 / 0` do seu próprio bug"], ["com o valor certo?", "`e.value` num record levantado", "o chamador decide pelo campo, não pelo texto"], ["nada ficou pela metade?", "comparar o estado antes e depois", "o débito aconteceu e o crédito não"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Não compare o texto da mensagem", "texto": "Um teste que confere `e.message is \"saldo insuficiente\"` quebra na primeira correção de vírgula e na primeira tradução. Compare o **tipo** e os **campos** — o texto é para humanos."}},
  {"p": "Continue em [Regressão](/docs/testes/regressao) e [Erros](/docs/erros)."},
];

const headings = [{ id: 'o-que-conferir-numa-falha', text: "O que conferir numa falha", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar erros e exceções"}
      description={"Que ele falha, com que tipo, com que mensagem — e que não falhou pela metade."}
      href={"/docs/testes/erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
