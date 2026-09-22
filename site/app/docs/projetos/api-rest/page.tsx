// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "API REST com CRUD",
  description: "Os cinco verbos sobre um recurso, com os status certos e validação na entrada.",
};

const blocos: Bloco[] = [
  {"p": "Uma API é regra de negócio mais transporte. O erro que mais custa é misturar os dois: a validação vai parar dentro da rota, e testar uma regra passa a exigir montar um pedido HTTP. Aqui a rota só traduz — o que decide mora em ações que se testam sem socket."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`server` / `route`", "as rotas, com parâmetro de caminho"], ["`Kiln.test`", "o pedido inteiro, sem abrir porta"], ["`Arcane.Database`", "SQLite em memória, com parâmetro `?`"], ["os status", "201, 204, 400, 404 — e o 405 que o Kiln dá sozinho"]]}},
  {"h2": "Estrutura"},
  { code: `api-produtos/
  forge.toml
  src/
    app.df         o 'server': rotas e traducao HTTP
    produtos.df    validar, criar, listar — sem HTTP nenhum
    banco.df       a conexao e o esquema
  main.df          'ignite' — o unico arquivo que abre porta
  tests/
    api_test.df`, lang: 'text' },
  { code: `[project]
name = "api-produtos"
version = "0.1.0"
description = "API de produtos"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Kiln
adopt Arcane.Database as DB

db := DB.memory()
DB.execute(db, "CREATE TABLE produtos (id INTEGER PRIMARY KEY, nome TEXT NOT NULL, preco REAL NOT NULL)")

// ── a regra, sem HTTP ────────────────────────────────────────
action problemas(dados):
    erros := []
    given (dados["nome"] ?? "").trim() is "":
        erros.append("nome e obrigatorio")
    preco := dados["preco"] ?? void
    given preco is void or not is_number(preco):
        erros.append("preco precisa ser numero")
    orif preco smaller_eq 0:
        erros.append("preco precisa ser positivo")
    yield erros

action criar(dados):
    DB.execute(db, "INSERT INTO produtos (nome, preco) VALUES (?, ?)",
        [dados["nome"].trim(), dados["preco"]])
    yield DB.query(db, "SELECT * FROM produtos ORDER BY id DESC LIMIT 1")[0]

action buscar(id):
    linhas := DB.query(db, "SELECT * FROM produtos WHERE id = ?", [int(id)])
    yield linhas[0] given len(linhas) bigger 0 otherwise void

// ── o transporte ────────────────────────────────────────────
server api on 0:
    route GET "/produtos":
        respond json {"itens": DB.query(db, "SELECT * FROM produtos ORDER BY id")}

    route GET "/produtos/:id":
        p := buscar(params["id"])
        given p is void:
            respond 404 json {"erro": "produto nao existe"}
        respond json p

    route POST "/produtos":
        erros := problemas(body)
        given len(erros) bigger 0:
            respond 400 json {"erros": erros}
        respond 201 json criar(body)

    route DELETE "/produtos/:id":
        given buscar(params["id"]) is void:
            respond 404 json {"erro": "produto nao existe"}
        DB.execute(db, "DELETE FROM produtos WHERE id = ?", [int(params["id"])])
        respond 204

r := Kiln.test(api, "POST", "/produtos", {"nome": "Teclado", "preco": 199.9})
assert r["status"] is 201
id := r["body"]["id"]

ruim := Kiln.test(api, "POST", "/produtos", {"nome": "", "preco": -1})
assert ruim["status"] is 400
assert len(ruim["body"]["erros"]) is 2

assert Kiln.test(api, "GET", $"/produtos/{id}")["body"]["nome"] is "Teclado"
assert Kiln.test(api, "DELETE", $"/produtos/{id}")["status"] is 204
assert Kiln.test(api, "GET", $"/produtos/{id}")["status"] is 404
assert Kiln.test(api, "PATCH", "/produtos/1")["status"] is 405
out "CRUD verde"`, lang: 'df', title: `src/app.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt Kiln
adopt ../src/app as App

crucible "api":
    trial "criar devolve 201 e o id":
        r := Kiln.test(App.api, "POST", "/produtos", {"nome": "Mouse", "preco": 50})
        expect r["status"] is 201
        expect "id" in r["body"]

    trial "os dois erros vem juntos":
        r := Kiln.test(App.api, "POST", "/produtos", {})
        expect len(r["body"]["erros"]) is 2`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["`problemas` devolve **todos** os erros", "o formulário é corrigido um campo por envio"], ["`?` no SQL, nunca interpolação", "`nome := \"x'); DROP TABLE produtos;--\"` apaga a tabela"], ["`server` monta, `ignite` sobe (em `main.df`)", "importar o módulo no teste sobe um servidor que nunca termina"], ["`404` do recurso separado do `404` da rota", "o cliente não sabe se errou o caminho ou o id"]]}},
  {"h2": "Para ir além"},
  {"list": ["Paginação com `DB.paginate` — ver [Banco → receitas](/docs/banco-de-dados/receitas).", "Contrato OpenAPI gerado das rotas: [OpenAPI](/docs/tecnicas/api).", "Autenticação por token no `middleware`: [Kiln → middleware](/docs/kiln/middleware)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"API REST com CRUD"}
      description={"Os cinco verbos sobre um recurso, com os status certos e validação na entrada."}
      href={"/docs/projetos/api-rest"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
