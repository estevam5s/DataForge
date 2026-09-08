import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Rotas e parâmetros",
  description: "Padrões de caminho, query string, corpo e os seis atalhos de toda rota.",
};

const blocos: Bloco[] = [
  {"h2": "Os verbos"},
  { code: `server api on 8080:
    route GET "/itens":
        respond json itens

    route POST "/itens":
        respond 201 json body

    route PUT "/itens/:id":
        respond json trocado

    route DELETE "/itens/:id":
        respond 204

    route HEAD "/saude":
        respond 200

    route ANY "/webhook":
        respond 200` },
  {"p": "O corpo da rota é um bloco indentado, como o de uma ação — não cabe na mesma linha do `route`."},
  {"p": "`ANY` casa qualquer verbo — útil para webhooks de serviços que mudam de método sem avisar."},
  {"h2": "Padrões de caminho"},
  {"table": {"head": ["Padrão", "Casa", "Não casa", "Resultado"], "rows": [
    ["`/itens`", "`/itens`, `/itens/`", "`/itensX`", "`{}`"],
    ["`/itens/:id`", "`/itens/42`", "`/itens`", "`{\"id\": \"42\"}`"],
    ["`/u/:id/posts/:post`", "`/u/7/posts/3`", "`/u/7`", "dois parâmetros"],
    ["`/files/*caminho`", "`/files/a/b.txt`", "—", "`{\"caminho\": \"a/b.txt\"}`"]
  ]}},
  {"p": "`:nome` casa **um trecho**; `*nome` casa **tudo o que sobrar**, barras inclusive. Um parâmetro chega já decodificado: `/b/ma%C3%A7%C3%A3` dá `\"maçã\"`."},
  {"h2": "Os seis atalhos"},
  {"p": "Dentro de uma rota, seis nomes já existem:"},
  { code: `route POST "/itens/:id":
    out params["id"]        // do caminho
    out query["formato"]    // da query string
    out body["nome"]        // o corpo, já interpretado
    out headers["authorization"]
    out session["usuario"]
    out req["method"], req["ip"]    // e a requisição inteira` },
  {"table": {"head": ["Nome", "É", "Quando falta a chave"], "rows": [
    ["`params`", "parâmetros do caminho", "não falta — o padrão garante"],
    ["`query`", "a query string", "**erro** — use `??`"],
    ["`body`", "o corpo interpretado", "**erro** — use `??`"],
    ["`headers`", "cabeçalhos, em minúsculas", "**erro** — use `??`"],
    ["`session`", "a sessão do visitante", "**erro** — use `??`"],
    ["`req`", "tudo, mais `method`, `path`, `ip`, `state`", "—"]
  ]}},
  {"h2": "A armadilha do `??`"},
  {"p": "`query`, `body` e `headers` vêm de fora: a chave pode simplesmente não vir. Indexar um vault sem a chave é **erro**, e dentro de uma rota isso vira 500."},
  { code: `// 500 na primeira visita sem filtro
route GET "/":
    respond json listar(query["categoria"])

// certo
route GET "/":
    respond json listar(query["categoria"] ?? void)` },
  {"p": "Esta é a causa número um de 500 inesperado em código Kiln novo. `params` é a exceção: se a rota casou, o parâmetro existe."},
  {"h2": "Query com um valor e com vários"},
  {"p": "`?nome=x` dá `\"x\"`; `?tag=a&tag=b` dá `[\"a\", \"b\"]`. Obrigar a indexar `[0]` sempre seria ruído em 95% dos casos — mas vale lembrar disso ao ler um campo que pode repetir."},
  {"h2": "O corpo, por Content-Type"},
  {"table": {"head": ["Content-Type", "`body` é"], "rows": [
    ["`application/json`", "vault ou cluster — ou o **texto cru**, se o JSON estiver quebrado"],
    ["`application/x-www-form-urlencoded`", "vault (formulário HTML)"],
    ["qualquer outro", "o texto"],
    ["sem corpo", "`void`"]
  ]}},
  {"p": "JSON inválido **não** vira 500. Chega como texto, e a rota decide — porque JSON quebrado é problema do cliente, e a resposta certa é 400, não \"o servidor caiu\"."},
  {"h2": "404 e 405"},
  { code: `// só GET e POST registrados em /itens
Kiln.test(api, "GET",    "/itens")   // 200
Kiln.test(api, "DELETE", "/itens")   // 405, Allow: GET, POST
Kiln.test(api, "GET",    "/nada")    // 404` },
  {"p": "O 405 traz `Allow` com os verbos aceitos. Devolver 404 ali mandaria o cliente procurar um caminho que existe."},
  {"h2": "Agrupar rotas"},
  { code: `server admin on 0:
    route GET "/usuarios":
        respond json usuarios

server api on 8080:
    route GET "/saude":
        respond 200

// as rotas do admin passam a viver sob /admin
Kiln.mount(api, "/admin", admin)` },
  {"p": "`mount` copia as rotas do outro server com o prefixo. Dentro de um bloco `server` a mesma coisa se escreve `mount admin at \"/admin\"`."},
  {"h2": "Ver as rotas registradas"},
  { code: `cycle r in Kiln.routes(api):
    out r["method"], r["path"], r["params"]` },
];

const headings = [{ id: 'os-verbos', text: "Os verbos", level: 2 as const }, { id: 'padroes-de-caminho', text: "Padrões de caminho", level: 2 as const }, { id: 'os-seis-atalhos', text: "Os seis atalhos", level: 2 as const }, { id: 'a-armadilha-do', text: "A armadilha do `??`", level: 2 as const }, { id: 'query-com-um-valor-e-com-varios', text: "Query com um valor e com vários", level: 2 as const }, { id: 'o-corpo-por-content-type', text: "O corpo, por Content-Type", level: 2 as const }, { id: '404-e-405', text: "404 e 405", level: 2 as const }, { id: 'agrupar-rotas', text: "Agrupar rotas", level: 2 as const }, { id: 'ver-as-rotas-registradas', text: "Ver as rotas registradas", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Rotas e parâmetros"}
      description={"Padrões de caminho, query string, corpo e os seis atalhos que toda rota recebe."}
      href={"/docs/kiln/rotas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
