// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Receber webhooks do GitHub",
  description: "A assinatura HMAC sobre os bytes originais, a entrega que chega duas vezes, e o 401 que não processa nada.",
};

const blocos: Bloco[] = [
  {"p": "Um webhook é um POST que chega de fora dizendo *“houve um push”*. Qualquer um que descubra a URL pode mandar o mesmo POST — por isso o GitHub **assina** o corpo com HMAC-SHA256, e o cabeçalho `X-Hub-Signature-256` traz a assinatura. Conferi-la é a única coisa que separa um evento do GitHub de um pedido forjado."},
  {"h2": "No Kiln"},
  { code: `adopt Kiln
adopt Arcane.GitHub as GH

steady SEGREDO := "troque-por-OS.env"
vistos := []
processados := []

server hooks on 0:
    route POST "/github":
        monitor:
            // raw_body: os BYTES que chegaram. Decodificar e re-serializar o
            // JSON muda espacos e ordem das chaves, e a assinatura nao bate.
            e := GH.evento_de_webhook(headers, req["raw_body"], SEGREDO)
        handle Error:
            respond 401 json {"erro": "assinatura invalida"}
        // O GitHub reentrega. Processar duas vezes e o proximo defeito.
        given e["entrega"] in vistos:
            respond 200 json {"repetida": yes}
        vistos.append(e["entrega"])
        given e["tipo"] is "pull_request" and e["acao"] is "opened":
            processados.append(e["carga"]["number"])
        respond 202 json {"ok": yes}

corpo := to_json({"action": "opened", "number": 7})
cab := {"X-GitHub-Event": "pull_request", "X-GitHub-Delivery": "d-1",
        "X-Hub-Signature-256": GH.assinatura(SEGREDO, corpo)}

assert Kiln.test(hooks, "POST", "/github", corpo, cab)["status"] is 202
assert Kiln.test(hooks, "POST", "/github", corpo, cab)["body"]["repetida"]
assert processados is [7]

forjado := cab with {}
forjado["X-Hub-Signature-256"] := GH.assinatura("outro", corpo)
assert Kiln.test(hooks, "POST", "/github", corpo, forjado)["status"] is 401
out "webhook: assinado, idempotente, e o forjado recusado"`, lang: 'df' },
  {"h2": "As quatro decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["conferir sobre `raw_body`", "a assinatura nunca bate, e alguém desliga a conferência para *“funcionar”*"], ["comparar em **tempo constante**", "`==` vaza, pelo tempo, quantos caracteres da assinatura acertaram"], ["guardar o `X-GitHub-Delivery`", "a reentrega cria o mesmo deploy, o mesmo e-mail, a mesma cobrança duas vezes"], ["responder rápido (202) e processar depois", "o GitHub desiste em 10 s e marca a entrega como falha"]]}},
  {"callout": {"tipo": "dica", "titulo": "O vetor da documentação", "texto": "O teste de `Arcane.GitHub` confere a assinatura contra o exemplo publicado pelo GitHub (segredo *“It's a Secret to Everybody”*, corpo *“Hello, World!”*). Comparar a implementação com ela mesma não prova nada; com o vetor oficial, prova."}},
  {"p": "Continue em [A API do GitHub](/docs/devops/api-github)."},
];

const headings = [{ id: 'no-kiln', text: "No Kiln", level: 2 as const }, { id: 'as-quatro-decisoes', text: "As quatro decisões", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Receber webhooks do GitHub"}
      description={"A assinatura HMAC sobre os bytes originais, a entrega que chega duas vezes, e o 401 que não processa nada."}
      href={"/docs/devops/webhooks"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
