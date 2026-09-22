// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/api_rest_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Erros que um programa lê",
  description: "application/problem+json (RFC 9457): o tipo, o título, o detalhe — e por que texto de erro não é contrato.",
};

const blocos: Bloco[] = [
  {"p": "Todo cliente de uma API acaba precisando decidir o que fazer com um erro: tentar de novo, pedir outro dado, mostrar uma mensagem. Se o erro é só um texto — `{\"erro\": \"saldo insuficiente\"}` —, o cliente decide **comparando texto**, e a primeira revisão de ortografia no servidor quebra todos eles."},
  {"p": "A RFC 9457 resolve isso com cinco campos, e `Kiln.problema` os monta:"},
  {"table": {"head": ["Campo", "O que é", "Quem lê"], "rows": [["`type`", "uma URI que identifica o **tipo** do problema", "o programa: é por ele que se decide"], ["`title`", "o resumo do tipo, igual em toda ocorrência", "a pessoa, num log"], ["`status`", "o mesmo código da resposta HTTP", "quem só tem o corpo em mãos"], ["`detail`", "o que aconteceu **desta vez**", "a pessoa, na tela"], ["`instance`", "qual pedido falhou", "o suporte, cruzando com o log"]]}},
  { code: `adopt Arcane.Kiln as Kiln

saldos := {"ana": 30}
app := Kiln.app()

action comprar(req):
    quem := req["params"]["quem"]
    preco := req["body"]["preco"]
    given (saldos[quem] ?? void) is void:
        yield Kiln.problema(404, "Conta não encontrada", $"não há conta '{quem}'")
    given preco bigger saldos[quem]:
        yield Kiln.problema(422, "Saldo insuficiente",
            $"o saldo é {saldos[quem]} e a compra custa {preco}",
            "https://loja.exemplo/erros/saldo-insuficiente",
            {"saldo": saldos[quem], "preco": preco})
    saldos[quem] -= preco
    yield Kiln.json({"saldo": saldos[quem]})

Kiln.post(app, "/contas/:quem/compras", comprar)

r := Kiln.test(app, "POST", "/contas/ana/compras", {"preco": 50})
assert r["status"] is 422
assert r["body"]["type"] is "https://loja.exemplo/erros/saldo-insuficiente"
assert r["body"]["saldo"] is 30
assert Kiln.test(app, "POST", "/contas/bia/compras", {"preco": 1})["status"] is 404`, lang: 'df' },
  {"h2": "Três decisões que a peça cobra"},
  {"list": ["**Problema é erro.** `Kiln.problema(200, …)` é recusado: um corpo de problema num 200 faz o cliente que olha o status seguir adiante com um erro na mão.", "**Os campos da RFC não vêm em `extras`.** Um `extras` com `status` sobrescreveria o status real no corpo e deixaria corpo e cabeçalho dizendo coisas diferentes.", "**`about:blank` é o tipo padrão**, e ele quer dizer \"o status HTTP já diz tudo\". Assim que um cliente precisar distinguir dois 422, dê a cada um o seu `type`."]},
  {"callout": {"tipo": "perigo", "titulo": "O detalhe vai para fora", "texto": "`detail` chega ao cliente. Nunca ponha ali a mensagem do banco, o caminho de um arquivo ou a pilha: isso conta a estrutura interna para quem perguntar. O erro inteiro vai para o **log**, com o mesmo `instance`, e o `detail` diz o que a pessoa pode fazer."}},
];

const headings = [{ id: 'tres-decisoes-que-a-peca-cobra', text: "Três decisões que a peça cobra", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Erros que um programa lê"}
      description={"application/problem+json (RFC 9457): o tipo, o título, o detalhe — e por que texto de erro não é contrato."}
      href={"/docs/api/problemas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
