"""
Os modelos de projeto do `dataforge new`.

Cada modelo produz um projeto **que roda e passa nos testes** — não um
esqueleto com TODOs. É o que separa um andaime útil de um que a pessoa
apaga na primeira hora.

Todo modelo traz forge.toml, README, .gitignore, código em src/ e teste
em tests/. A estrutura é sempre a mesma, para quem aprendeu um projeto
saber se achar em qualquer outro.
"""

# ── Pedaços comuns ───────────────────────────────────────────

GITIGNORE = """forge_modules/
*.pyc
__pycache__/
.DS_Store
.env
*.db
"""


def _forge_toml(descricao: str, deps: str = "", scripts: str = "") -> str:
    return f'''[project]
name = "{{name}}"
version = "0.1.0"
description = "{descricao}"
entry = "src/main.df"
dataforge = ">=1.0"

[dependencies]{deps}

[scripts]
start = "run src/main.df"
test = "test tests/"{scripts}
'''


def _readme(titulo: str, o_que_faz: str, comandos: str,
            notas: str = "") -> str:
    return f'''# {{name}}

{o_que_faz}

## Rodar

```bash
{comandos}
```

## Estrutura

```
src/      o código
tests/    os testes — rode com `dataforge test tests/`
forge.toml   o manifesto: nome, versão, dependências, scripts
```

{notas}
Feito com [DataForge](https://dataforge-lang.vercel.app) v{{version}}.
'''


MODELOS = {
    # ── 1. Console ───────────────────────────────────────────
    "cli": {
        "name": "Ferramenta de linha de comando",
        "description": "Lê argumentos, imprime tabela colorida, tem --help",
        "icon": "⚡",
        "proximos": [
            ("dataforge run src/main.df -- listar", "roda um comando"),
            ("dataforge run src/main.df -- ajuda", "vê a ajuda"),
            ("dataforge test tests/", "roda os testes"),
        ],
        "files": {
            "forge.toml": _forge_toml(
                "Ferramenta de linha de comando em DataForge"),
            ".gitignore": GITIGNORE,
            "README.md": _readme(
                "{name}",
                "Uma ferramenta de linha de comando: lê argumentos, formata a "
                "saída e tem ajuda de verdade.",
                "dataforge run src/main.df -- ajuda\n"
                "dataforge run src/main.df -- listar\n"
                "dataforge test tests/"),
            "src/main.df": '''// {name} — ferramenta de linha de comando
//
//   dataforge run src/main.df -- ajuda
//   dataforge run src/main.df -- listar
//   dataforge run src/main.df -- somar 2 40

adopt Arcane.OS as OS
adopt Arcane.Text as Text
adopt comandos as C

steady NOME := "{name}"
steady VERSAO := "0.1.0"

action ajuda():
    out ""
    out Text.bold(NOME) + " v" + VERSAO
    out ""
    out "USO"
    out "    dataforge run src/main.df -- <comando> [argumentos]"
    out ""
    out "COMANDOS"
    cycle c in C.catalogo():
        out "    " + Text.pad_end(c["nome"], 12) + c["resumo"]
    out ""

action principal():
    argumentos := OS.argv()

    given len(argumentos) is 0:
        ajuda()
        yield 0

    comando := argumentos[0]
    resto := argumentos[1:]

    given comando is "ajuda" or comando is "--help" or comando is "-h":
        ajuda()
        yield 0

    given comando is "versao" or comando is "--version":
        out VERSAO
        yield 0

    resultado := C.executar(comando, resto)
    given resultado is void:
        out Text.bold("erro: ") + $"comando desconhecido: {comando}"
        out ""
        out "    Rode com 'ajuda' para ver o que existe."
        yield 1

    out resultado
    yield 0

principal()
''',
            "src/comandos.df": '''// Os comandos, separados da leitura de argumentos.
//
// Manter os dois apartados é o que permite testar cada comando sem
// simular a linha de comando.

steady CATALOGO := [
    {"nome": "listar", "resumo": "mostra os itens de exemplo"},
    {"nome": "somar",  "resumo": "soma os números recebidos"},
    {"nome": "ajuda",  "resumo": "mostra esta tela"},
    {"nome": "versao", "resumo": "mostra a versão"}
]

steady ITENS := ["martelo", "bigorna", "tenaz"]

action catalogo():
    yield CATALOGO

action listar():
    linhas := []
    cycle i from 0 to len(ITENS) - 1:
        linhas.append($"  {i + 1}. {ITENS[i]}")
    yield join("\\n", linhas)

action somar(numeros):
    given len(numeros) is 0:
        yield "informe ao menos um número"
    total := 0
    cycle n in numeros:
        total += int(n)
    yield $"soma: {total}"

action executar(comando, argumentos):
    given comando is "listar":
        yield listar()
    given comando is "somar":
        yield somar(argumentos)
    yield void

relay catalogo, listar, somar, executar
''',
            "tests/comandos_test.df": '''adopt Arcane.Test as T
adopt ../src/comandos as C

action test_listar_traz_os_tres_itens():
    saida := C.listar()
    T.assert_contains(saida, "martelo")
    T.assert_contains(saida, "bigorna")
    T.assert_contains(saida, "tenaz")

action test_somar_soma_os_numeros():
    T.assert_eq(C.somar(["2", "40"]), "soma: 42")

action test_somar_sem_argumento_avisa():
    T.assert_contains(C.somar([]), "informe")

action test_comando_desconhecido_devolve_void():
    T.assert_void(C.executar("nao-existe", []))

action test_catalogo_lista_os_comandos():
    T.assert_eq(len(C.catalogo()), 4)
''',
        },
    },

    # ── 2. API REST com Kiln ─────────────────────────────────
    "api": {
        "name": "API REST (Kiln)",
        "description": "Servidor com rotas, JSON, 404/405 e testes sem socket",
        "icon": "🌐",
        "proximos": [
            ("dataforge test tests/", "roda os testes — sem abrir socket"),
            ("dataforge run src/main.df", "sobe em http://127.0.0.1:8080"),
        ],
        "files": {
            "forge.toml": _forge_toml("API REST em DataForge com Kiln"),
            ".gitignore": GITIGNORE,
            "README.md": _readme(
                "{name}",
                "Uma API REST com o **Kiln**, o framework web do DataForge. "
                "Rotas com parâmetro, corpo em JSON, e os status certos.",
                "dataforge test tests/     # 8 testes, sem abrir socket\n"
                "dataforge run src/main.df # http://127.0.0.1:8080",
                notas="""## As rotas

| Rota | Faz |
|------|-----|
| `GET /` | um oi |
| `GET /api/itens` | lista |
| `GET /api/itens/:id` | um item, ou 404 |
| `POST /api/itens` | cria, devolve 201 |
| `DELETE /api/itens/:id` | apaga, devolve 204 |

O 404 e o **405 com `Allow`** vêm de graça: o Kiln distingue "não
existe" de "existe, mas não com esse verbo".

"""),
            "src/app.df": '''// A aplicação: monta e NÃO sobe nada.
//
// Quem acende o forno é o main.df. A separação não é enfeite: um teste
// que importasse o main subiria o servidor e nunca terminaria.

adopt Kiln
adopt repositorio as Repo

server api on 8080:
    middleware Kiln.logger()
    middleware Kiln.cors()

    route GET "/":
        respond html "<h1>{name}</h1><p>API no ar. Veja /api/itens.</p>"

    route GET "/api/itens":
        itens := Repo.listar()
        respond json {"itens": itens, "total": len(itens)}

    route GET "/api/itens/:id":
        item := Repo.achar(params["id"])
        given item is void:
            respond 404 json {"erro": "não achei esse item"}
        respond json item

    route POST "/api/itens":
        // O corpo vem de fora: a chave pode não vir, e indexar um vault
        // sem a chave é erro. '??' é o que separa 400 de 500.
        given body is void or (body["nome"] ?? void) is void:
            respond 400 json {"erro": "informe 'nome'"}
        respond 201 json Repo.criar(body["nome"])

    route DELETE "/api/itens/:id":
        given not Repo.apagar(params["id"]):
            respond 404 json {"erro": "não achei esse item"}
        respond 204

Kiln.on_error(api, 404, lambda req => Kiln.json(
    {"erro": "rota não encontrada"}, 404))

relay api
''',
            "src/repositorio.df": '''// Os dados. Trocar por um banco é mexer só aqui.

itens := [
    {"id": 1, "nome": "Martelo"},
    {"id": 2, "nome": "Bigorna"}
]

proximo := 3

action listar():
    yield itens

action achar(id):
    alvo := int(id)
    cycle item in itens:
        given item["id"] is alvo:
            yield item
    yield void

action criar(nome):
    novo := {"id": proximo, "nome": nome}
    itens.append(novo)
    proximo += 1
    yield novo

action apagar(id):
    alvo := int(id)
    cycle i from 0 to len(itens) - 1:
        given itens[i]["id"] is alvo:
            itens.pop(i)
            yield yes
    yield no

relay listar, achar, criar, apagar
''',
            "src/main.df": '''// {name} — sobe a API.
//
//   dataforge run src/main.df          porta 8080
//   dataforge run src/main.df -- 3000  outra porta

adopt Arcane.OS as OS
adopt app as App

argumentos := OS.argv()
porta := int(argumentos[0]) given len(argumentos) bigger 0 otherwise 8080

ignite App.api on porta
''',
            "tests/api_test.df": '''// Kiln.test executa a rota direto na aplicação, sem abrir socket.
// É o que torna teste de rota tão barato quanto teste de função.

adopt Arcane.Test as T
adopt Kiln
adopt ../src/app as App

steady API := App.api

action test_a_raiz_responde_html():
    r := Kiln.test(API, "GET", "/")
    T.assert_eq(r["status"], 200)
    T.assert_contains(r["body"], "<h1>")

action test_lista_traz_os_itens():
    r := Kiln.test(API, "GET", "/api/itens")
    T.assert_eq(r["status"], 200)
    T.assert_eq(r["body"]["total"], 2)

action test_um_item_pelo_id():
    r := Kiln.test(API, "GET", "/api/itens/1")
    T.assert_eq(r["body"]["nome"], "Martelo")

action test_item_inexistente_da_404():
    T.assert_eq(Kiln.test(API, "GET", "/api/itens/999")["status"], 404)

action test_criar_devolve_201():
    r := Kiln.test(API, "POST", "/api/itens", {"nome": "Tenaz"})
    T.assert_eq(r["status"], 201)
    T.assert_eq(r["body"]["nome"], "Tenaz")
    Kiln.test(API, "DELETE", "/api/itens/" + str(r["body"]["id"]))

action test_corpo_sem_nome_da_400():
    T.assert_eq(Kiln.test(API, "POST", "/api/itens", {})["status"], 400)

action test_apagar_devolve_204():
    novo := Kiln.test(API, "POST", "/api/itens", {"nome": "Lima"})["body"]
    r := Kiln.test(API, "DELETE", "/api/itens/" + str(novo["id"]))
    T.assert_eq(r["status"], 204)

action test_verbo_errado_da_405_e_nao_404():
    T.assert_eq(Kiln.test(API, "PATCH", "/api/itens/1")["status"], 405)
''',
        },
    },

    # ── 3. Site com páginas ──────────────────────────────────
    "web": {
        "name": "Site com páginas (Kiln)",
        "description": "Templates HTML, arquivos estáticos e escape automático",
        "icon": "🖥️",
        "proximos": [
            ("dataforge test tests/", "roda os testes"),
            ("dataforge run src/main.df", "abre em http://127.0.0.1:8080"),
        ],
        "files": {
            "forge.toml": _forge_toml("Site em DataForge com Kiln"),
            ".gitignore": GITIGNORE,
            "README.md": _readme(
                "{name}",
                "Um site com páginas HTML renderizadas pelo **Kiln**: "
                "templates com laço, escape automático e CSS servido do disco.",
                "dataforge test tests/\ndataforge run src/main.df",
                notas="""## Os templates

`{{nome}}` escreve escapando HTML — um produto chamado `Bigorna <de aço>`
sai como texto, não como tag. Para escrever HTML de propósito existe
`{{&campo}}`, e a diferença de um caractere torna a decisão visível na
revisão.

"""),
            "src/app.df": '''// O site: monta e NÃO sobe nada (quem acende é o main.df).

adopt Kiln
adopt Arcane.OS as OS

steady RAIZ := OS.beside("..")

produtos := [
    {"nome": "Martelo de forja", "preco": "R$ 89,90", "estoque": 12},
    {"nome": "Bigorna 50kg",     "preco": "R$ 450,00", "estoque": 3},
    {"nome": "Tenaz reta",       "preco": "R$ 65,50", "estoque": 27}
]

server site on 8080:
    // Ao lado do programa, não de onde o usuário o chamou: sem isso,
    // rodar de duas pastas diferentes carrega templates diferentes.
    views RAIZ + "/views"
    assets "/static" from RAIZ + "/www"

    route GET "/":
        render "catalogo.html" with {
            "titulo": "{name}",
            "produtos": produtos
        }

    route GET "/vazio":
        render "catalogo.html" with {"titulo": "Sem estoque", "produtos": []}

relay site, produtos
''',
            "src/main.df": '''adopt Arcane.OS as OS
adopt app as App

argumentos := OS.argv()
porta := int(argumentos[0]) given len(argumentos) bigger 0 otherwise 8080

ignite App.site on porta
''',
            "views/catalogo.html": '''<!doctype html>
<html lang="pt-BR">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{titulo}}</title>
<link rel="stylesheet" href="/static/estilo.css">

<h1>{{titulo}}</h1>

{{#produtos}}
<article>
  <h2>{{nome}}</h2>
  <p class="preco">{{preco}}</p>
  <p class="estoque">{{estoque}} em estoque</p>
</article>
{{/produtos}}

{{^produtos}}
<p class="vazio">Nada na forja ainda.</p>
{{/produtos}}
''',
            "www/estilo.css": ''':root { --tinta: #1a1a1a; --fundo: #faf8f5; --brasa: #c2410c; }
body { font: 16px/1.6 system-ui, sans-serif; max-width: 46rem;
       margin: 3rem auto; padding: 0 1.5rem;
       color: var(--tinta); background: var(--fundo); }
h1 { font-size: 2rem; }
article { border-bottom: 1px solid #e0dbd3; padding: 1rem 0; }
h2 { font-size: 1.15rem; margin: 0 0 .25rem; }
.preco { font-weight: 600; margin: 0; }
.estoque { color: #6b6b6b; font-size: .9rem; margin: .25rem 0 0; }
.vazio { color: #6b6b6b; font-style: italic; }
''',
            "tests/site_test.df": '''adopt Arcane.Test as T
adopt Kiln
adopt ../src/app as App

steady SITE := App.site

action test_a_home_lista_os_produtos():
    r := Kiln.test(SITE, "GET", "/")
    T.assert_eq(r["status"], 200)
    T.assert_contains(r["body"], "Martelo de forja")

action test_a_pagina_tem_o_html_inteiro():
    corpo := Kiln.test(SITE, "GET", "/")["body"]
    T.assert_contains(corpo, "<!doctype html>")
    T.assert_contains(corpo, "</article>")

action test_lista_vazia_mostra_o_aviso():
    corpo := Kiln.test(SITE, "GET", "/vazio")["body"]
    T.assert_contains(corpo, "Nada na forja")
    T.assert_not_contains(corpo, "<article>")

action test_o_css_e_servido():
    r := Kiln.test(SITE, "GET", "/static/estilo.css")
    T.assert_eq(r["status"], 200)
    T.assert_contains(r["body"], "--brasa")

action test_nao_da_para_sair_da_pasta_publica():
    T.assert_eq(Kiln.test(SITE, "GET", "/static/../../etc/passwd")["status"],
                403)
''',
        },
    },

    # ── 4. Análise de dados ──────────────────────────────────
    "data": {
        "name": "Análise de dados",
        "description": "Banco, estatística e exportação para Excel",
        "icon": "📊",
        "proximos": [
            ("dataforge run src/main.df", "gera o relatório"),
            ("dataforge test tests/", "roda os testes"),
        ],
        "files": {
            "forge.toml": _forge_toml("Análise de dados em DataForge"),
            ".gitignore": GITIGNORE + "*.xlsx\n*.csv\n",
            "README.md": _readme(
                "{name}",
                "O caminho completo de um trabalho de dados: os dados moram "
                "no banco, a análise responde à pergunta, e a planilha é o "
                "que se manda para quem decide.",
                "dataforge run src/main.df\ndataforge test tests/",
                notas="""## O que ele mostra

- `Arcane.Database` — SQLite, sem instalar nada
- `Arcane.Analytics` — média, desvio, correlação, `describe`
- `Arcane.Excel` — `.xlsx` com fórmulas que o Excel resolve ao abrir

O arquivo gerado abre no Excel, no LibreOffice e no Google Sheets.

"""),
            "src/dados.df": '''// Tudo o que toca SQL mora aqui.

adopt Arcane.Database as DB

steady ESQUEMA := """CREATE TABLE IF NOT EXISTS vendas (
    produto TEXT NOT NULL,
    regiao TEXT NOT NULL,
    qtd INTEGER NOT NULL,
    preco REAL NOT NULL
)"""

action abrir(caminho):
    conexao := DB.connect(caminho)
    DB.execute(conexao, ESQUEMA)
    yield conexao

action semear(conexao):
    // Só semeia banco vazio: rodar duas vezes não pode duplicar.
    quantos := DB.query(conexao, "SELECT COUNT(*) AS n FROM vendas")[0]["n"]
    given quantos bigger 0:
        yield quantos

    cycle linha in [
        ["Martelo", "Sul",   12, 89.9],
        ["Bigorna", "Sul",    3, 450.0],
        ["Tenaz",   "Norte", 27, 65.5],
        ["Fole",    "Norte",  8, 320.0],
        ["Marreta", "Sul",   15, 110.0]
    ]:
        DB.execute(conexao,
            "INSERT INTO vendas (produto, regiao, qtd, preco) VALUES (?, ?, ?, ?)",
            linha)
    yield 5

action todas(conexao):
    yield DB.query(conexao, "SELECT * FROM vendas ORDER BY qtd DESC")

action por_regiao(conexao):
    yield DB.query(conexao,
        """SELECT regiao, COUNT(*) AS itens, SUM(qtd * preco) AS valor
             FROM vendas GROUP BY regiao ORDER BY regiao""")

relay abrir, semear, todas, por_regiao
''',
            "src/main.df": '''// {name} — do banco à planilha, passando pela análise.

adopt Arcane.Analytics as An
adopt Arcane.Excel as Xls
adopt Arcane.Database as DB
adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt dados as D

// A pasta temporaria vem do sistema. Cravar "/tmp" faz o modelo
// funcionar no Mac e no Linux e falhar no Windows, que nao tem essa
// pasta — e o primeiro programa que alguem roda nao e lugar de
// aprender isso do jeito dificil.
steady BANCO := IO.join(OS.temp_dir(), "{name}.db")
steady SAIDA := "relatorio.xlsx"

conexao := D.abrir(BANCO)
D.semear(conexao)

registros := D.todas(conexao)
out $"no banco: {len(registros)} vendas"

// ── a pergunta ──
quantidades := [r["qtd"] cycle r in registros]
precos := [r["preco"] cycle r in registros]

out "média de unidades:", An.mean(quantidades)
out "desvio dos preços: ", round(An.stdev(precos), 2)

// Correlação negativa forte diz que o caro vende pouco.
correlacao := An.correlation(quantidades, precos)
out "correlação qtd × preço:", round(correlacao, 3)

// describe() sobre um frame descreve cada coluna de uma vez
tabela := An.from_records(registros)
descricao := An.describe(tabela)
out "coluna qtd:", descricao["qtd"]["count"], "valores, média",
    descricao["qtd"]["mean"]

// ── o entregável ──
livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", registros)

Xls.set(aba, "E1", "receita")
cycle i from 2 to len(registros) + 1:
    Xls.formula(aba, $"E{i}", $"C{i}*D{i}")

Xls.set(aba, "A" + str(len(registros) + 2), "TOTAL")
Xls.formula(aba, "E" + str(len(registros) + 2),
            $"SUM(E2:E{len(registros) + 1})")
Xls.bold_row(aba, len(registros) + 1)

Xls.sheet(livro, "Por região", D.por_regiao(conexao))
Xls.save(livro, SAIDA)

out ""
out $"planilha gravada: {SAIDA}"
out "  as fórmulas são resolvidas pelo Excel ao abrir"

DB.close(conexao)
''',
            "tests/dados_test.df": '''adopt Arcane.Test as T
adopt Arcane.Analytics as An
adopt Arcane.Database as DB
adopt ../src/dados as D

action test_semear_insere_cinco_vendas():
    conexao := D.abrir(":memory:")
    T.assert_eq(D.semear(conexao), 5)
    T.assert_eq(len(D.todas(conexao)), 5)
    DB.close(conexao)

action test_semear_duas_vezes_nao_duplica():
    conexao := D.abrir(":memory:")
    D.semear(conexao)
    D.semear(conexao)
    T.assert_eq(len(D.todas(conexao)), 5)
    DB.close(conexao)

action test_agrupa_por_regiao():
    conexao := D.abrir(":memory:")
    D.semear(conexao)
    T.assert_eq(len(D.por_regiao(conexao)), 2)
    DB.close(conexao)

action test_o_caro_vende_pouco():
    conexao := D.abrir(":memory:")
    D.semear(conexao)
    registros := D.todas(conexao)
    correlacao := An.correlation(
        [r["qtd"] cycle r in registros],
        [r["preco"] cycle r in registros])
    T.assert_less(correlacao, 0)
    DB.close(conexao)
''',
        },
    },

    # ── 5. Biblioteca publicável ─────────────────────────────
    "lib": {
        "name": "Biblioteca",
        "description": "Um pacote com relay, testes e pronto para publicar",
        "icon": "📦",
        "proximos": [
            ("dataforge test tests/", "roda os testes"),
            ("dataforge pack", "empacota para publicar"),
        ],
        "files": {
            "forge.toml": '''[package]
name = "{name}"
version = "0.1.0"
description = "Uma biblioteca DataForge"
license = "MIT"
dataforge = ">=1.0"

[scripts]
test = "test tests/"
''',
            ".gitignore": GITIGNORE,
            "README.md": _readme(
                "{name}",
                "Uma biblioteca DataForge, pronta para publicar no registro.",
                "dataforge test tests/\ndataforge pack",
                notas="""## Usar

```dataforge
adopt {name} as Lib

out Lib.dobrar(21)
```

## Publicar

```bash
dataforge pack
dataforge publish --registry=<url>
```

O `relay` no fim de `src/main.df` decide o que sai da biblioteca —
tudo o mais fica privado.

"""),
            "src/main.df": '''// {name} — a superfície pública da biblioteca.
//
// O 'relay' no fim decide o que sai. O que não estiver lá fica privado,
// e isso é o que permite mudar a implementação sem quebrar quem usa.

steady VERSAO := "0.1.0"

action dobrar(n):
    yield n * 2

action somar_todos(numeros):
    total := 0
    cycle n in numeros:
        total += n
    yield total

action media(numeros):
    given len(numeros) is 0:
        trigger "média de lista vazia"
    yield somar_todos(numeros) / len(numeros)

// Um exemplo de erro com mensagem que diz o que fazer.
action dividir(a, b):
    given b is 0:
        trigger "divisão por zero: confira o divisor antes de chamar"
    yield a / b

relay VERSAO, dobrar, somar_todos, media, dividir
''',
            "tests/main_test.df": '''adopt Arcane.Test as T
adopt ../src/main as Lib

action test_dobrar():
    T.assert_eq(Lib.dobrar(21), 42)
    T.assert_eq(Lib.dobrar(0), 0)
    T.assert_eq(Lib.dobrar(-5), -10)

action test_somar_todos():
    T.assert_eq(Lib.somar_todos([1, 2, 3, 4]), 10)
    T.assert_eq(Lib.somar_todos([]), 0)

action test_media():
    T.assert_eq(Lib.media([2, 4, 6]), 4)

action test_media_de_lista_vazia_falha_com_mensagem():
    monitor:
        Lib.media([])
        T.assert_true(no)
    handle TriggerError as e:
        T.assert_contains(e.message, "vazia")

action test_dividir_por_zero_diz_o_que_fazer():
    monitor:
        Lib.dividir(1, 0)
        T.assert_true(no)
    handle TriggerError as e:
        T.assert_contains(e.message, "confira o divisor")
''',
        },
    },

    # ── 6. Orientação a objetos ──────────────────────────────
    "oop": {
        "name": "Orientação a objetos",
        "description": "Blueprints, traits, propriedades e operadores",
        "icon": "🧩",
        "proximos": [
            ("dataforge run src/main.df", "roda o exemplo"),
            ("dataforge test tests/", "roda os testes"),
        ],
        "files": {
            "forge.toml": _forge_toml("Exemplo de OOP em DataForge"),
            ".gitignore": GITIGNORE,
            "README.md": _readme(
                "{name}",
                "Um domínio modelado com o OOP do DataForge: trait como "
                "contrato, blueprint como implementação, record para o dado "
                "imutável.",
                "dataforge run src/main.df\ndataforge test tests/",
                notas="""## O que ele mostra

| Recurso | Onde |
|---------|------|
| `trait` — o contrato | `Forma` |
| `blueprint … with` | `Retangulo`, `Circulo` |
| `extends` e `root` | `Quadrado` |
| `get` — propriedade | `descricao` |
| `operator +` | soma de retângulos |
| `private` | o campo interno |
| `record` | `Ponto`, imutável |

"""),
            "src/formas.df": '''// Um domínio pequeno, com as ferramentas de OOP do DataForge.

// O trait é o contrato: quem o adota precisa ter estes métodos.
trait Forma:
    action area()
    action perimetro()

blueprint Retangulo(largura, altura) with Forma:
    action area():
        yield self.largura * self.altura

    action perimetro():
        yield 2 * (self.largura + self.altura)

    // Uma propriedade se lê como campo e se calcula como método.
    get descricao():
        yield $"retângulo {self.largura}×{self.altura}"

    // Sobrecarga: '+' passa a funcionar entre retângulos.
    operator +(outro):
        yield spawn Retangulo(self.largura + outro.largura,
                              self.altura + outro.altura)

blueprint Quadrado(lado) extends Retangulo:
    action setup(lado):
        self.largura := lado
        self.altura := lado

    get descricao():
        // 'root' chama a implementação do pai.
        yield "quadrado de lado " + str(self.largura)

blueprint Circulo(raio) with Forma:
    private PI: Float := 3.14159265

    action area():
        yield self.PI * self.raio ** 2

    action perimetro():
        yield 2 * self.PI * self.raio

    get descricao():
        yield $"círculo de raio {self.raio}"

// Record: imutável, com igualdade estrutural.
record Ponto:
    x: Integer
    y: Integer

    action distancia_ate(outro):
        yield sqrt((self.x - outro.x) ** 2 + (self.y - outro.y) ** 2)

relay Forma, Retangulo, Quadrado, Circulo, Ponto
''',
            "src/main.df": '''// {name} — polimorfismo em ação.

adopt formas as F

formas := [
    spawn F.Retangulo(3, 4),
    spawn F.Quadrado(5),
    spawn F.Circulo(2)
]

out "── as formas ──"
cycle f in formas:
    out $"{f.descricao}: área {round(f.area(), 2)}, " +
        $"perímetro {round(f.perimetro(), 2)}"

// Sobrecarga de operador
a := spawn F.Retangulo(2, 3)
b := spawn F.Retangulo(4, 1)
out ""
out "soma de retângulos:", (a + b).descricao

// Records são imutáveis: 'with' devolve uma cópia
p := F.Ponto(0, 0)
q := F.Ponto(3, 4)
out ""
out "distância:", p.distancia_ate(q)
out "cópia com y trocado:", q with {"y": 0}
out "igualdade estrutural:", F.Ponto(1, 2) is F.Ponto(1, 2)
''',
            "tests/formas_test.df": '''adopt Arcane.Test as T
adopt ../src/formas as F

action test_area_do_retangulo():
    T.assert_eq((spawn F.Retangulo(3, 4)).area(), 12)

action test_quadrado_herda_e_ajusta():
    q := spawn F.Quadrado(5)
    T.assert_eq(q.area(), 25)
    T.assert_contains(q.descricao, "quadrado")

action test_propriedade_se_le_como_campo():
    T.assert_eq((spawn F.Retangulo(2, 3)).descricao, "retângulo 2×3")

action test_soma_de_retangulos():
    soma := spawn F.Retangulo(2, 3) + spawn F.Retangulo(4, 1)
    T.assert_eq(soma.area(), 24)

action test_area_do_circulo():
    T.assert_close((spawn F.Circulo(2)).area(), 12.566, 0.01)

action test_record_tem_igualdade_estrutural():
    T.assert_eq(F.Ponto(1, 2), F.Ponto(1, 2))

action test_record_with_devolve_copia():
    p := F.Ponto(3, 4)
    T.assert_eq((p with {"y": 0}).y, 0)
    T.assert_eq(p.y, 4)

action test_distancia_entre_pontos():
    T.assert_eq(F.Ponto(0, 0).distancia_ate(F.Ponto(3, 4)), 5.0)
''',
        },
    },

    # ── 7. Script de automação ───────────────────────────────
    "script": {
        "name": "Script de automação",
        "description": "Arquivos, JSON, datas e processos do sistema",
        "icon": "🔧",
        "proximos": [
            ("dataforge run src/main.df", "roda o script"),
            ("dataforge test tests/", "roda os testes"),
        ],
        "files": {
            "forge.toml": _forge_toml("Script de automação em DataForge"),
            ".gitignore": GITIGNORE + "saida/\n",
            "README.md": _readme(
                "{name}",
                "Um script de automação: varre arquivos, resume o que achou "
                "e grava um relatório em JSON e CSV.",
                "dataforge run src/main.df\ndataforge test tests/"),
            "src/varredura.df": '''// A lógica, separada da entrada e da saída — assim ela se testa.

adopt Arcane.IO as IO
adopt Arcane.OS as OS

action extensao_de(nome):
    ponto := -1
    cycle i from 0 to len(nome) - 1:
        given nome[i] is ".":
            ponto := i
    given ponto is -1 or ponto is 0:
        yield "(sem extensão)"
    yield nome[ponto:]

action resumir(nomes):
    """Quantos arquivos de cada extensão."""
    contagem := {}
    cycle nome in nomes:
        ext := extensao_de(nome)
        contagem[ext] := (contagem[ext] ?? 0) + 1
    yield contagem

action maiores(entradas, quantos):
    """As N maiores, por tamanho."""
    ordenadas := sorted(entradas, lambda e => -e["bytes"])
    yield ordenadas[:quantos]

relay extensao_de, resumir, maiores
''',
            "src/main.df": '''// {name} — varre uma pasta e grava um relatório.
//
//   dataforge run src/main.df           varre a pasta atual
//   dataforge run src/main.df -- /tmp   varre outra

adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Time as Time
adopt varredura as V

argumentos := OS.argv()
pasta := argumentos[0] given len(argumentos) bigger 0 otherwise "."

out $"varrendo {pasta}…"

nomes := IO.list_dir(pasta)
entradas := []
cycle nome in nomes:
    caminho := pasta + "/" + nome
    given IO.is_file(caminho):
        entradas.append({"nome": nome, "bytes": IO.file_size(caminho)})

out $"  {len(entradas)} arquivo(s)"
out ""

out "── por extensão ──"
contagem := V.resumir([e["nome"] cycle e in entradas])
cycle ext in contagem:
    out $"  {ext}: {contagem[ext]}"

out ""
out "── os cinco maiores ──"
cycle e in V.maiores(entradas, 5):
    out $"  {e['nome']}: {e['bytes']} bytes"

// O relatório, ao lado do script — não de onde ele foi chamado.
relatorio := {
    "pasta": pasta,
    "quando": Time.now().iso(),
    "total": len(entradas),
    "por_extensao": contagem,
    "maiores": V.maiores(entradas, 5)
}

destino := OS.beside("..", "relatorio.json")
IO.write_json(destino, relatorio)
out ""
out $"relatório gravado: {destino}"
''',
            "tests/varredura_test.df": '''adopt Arcane.Test as T
adopt ../src/varredura as V

action test_extensao_simples():
    T.assert_eq(V.extensao_de("main.df"), ".df")
    T.assert_eq(V.extensao_de("dados.tar.gz"), ".gz")

action test_arquivo_sem_extensao():
    T.assert_eq(V.extensao_de("LICENSE"), "(sem extensão)")

action test_arquivo_oculto_nao_conta_o_ponto_inicial():
    T.assert_eq(V.extensao_de(".gitignore"), "(sem extensão)")

action test_resumir_conta_por_extensao():
    contagem := V.resumir(["a.df", "b.df", "c.md"])
    T.assert_eq(contagem[".df"], 2)
    T.assert_eq(contagem[".md"], 1)

action test_maiores_ordena_por_tamanho():
    entradas := [
        {"nome": "p", "bytes": 10},
        {"nome": "g", "bytes": 900},
        {"nome": "m", "bytes": 100}
    ]
    T.assert_eq(V.maiores(entradas, 2)[0]["nome"], "g")
''',
        },
    },

    # ── 9. Painel de dados (Vitrine) ─────────────────────────
    "painel": {
        "name": "Painel de dados (Vitrine)",
        "description": "Um dashboard: métricas, gráficos, filtros e testes",
        "icon": "📊",
        "proximos": [
            ("dataforge vitrine dev", "sobe em http://127.0.0.1:8501, "
                                      "recarregando ao salvar"),
            ("dataforge test tests/", "roda os testes — sem navegador"),
        ],
        "files": {
            "forge.toml": _forge_toml("Painel de dados em DataForge"),
            ".gitignore": GITIGNORE,
            "README.md": _readme(
                "{name}",
                "Um painel com a **Vitrine**. O programa roda de cima para "
                "baixo e vira uma página web — sem HTML, sem JavaScript.",
                "dataforge vitrine dev     # http://127.0.0.1:8501\n"
                "dataforge test tests/     # os testes, sem navegador",
                notas="""## Como ele funciona

A cada interação **o programa inteiro roda de novo**, e o estado da
sessão sobrevive. É o que dispensa callback: `V.botao(...)` devolve
`yes` no ciclo do clique, e a linha seguinte já usa o valor.

O custo é que a página precisa ser rápida a cada clique — daí o
`mark @V.cache` sobre `carregar()`.

## Os arquivos

| Arquivo | O quê |
|---|---|
| `src/dados.df` | de onde vêm os números |
| `src/painel.df` | a página |
| `src/main.df` | sobe o servidor |
| `tests/painel_test.df` | clica, digita e confere |

`painel.df` monta e **não** sobe nada. Sem essa separação, um teste que
adotasse o painel subiria o servidor e nunca terminaria.

"""),
            "src/dados.df": '''// De onde vêm os números.
//
// Aqui é sintético. Num painel de verdade, troque por
// 'Banco.consultar(...)' ou 'IO.read_csv(...)' — o resto da aplicação
// não muda.

adopt Arcane.Vitrine as V

steady MESES := ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]

//: O cache faz a leitura acontecer UMA vez, e não a cada clique. Num
//: painel que lê do banco, é a diferença entre uma página que responde
//: e uma que trava.
mark @V.cache
action carregar(regiao):
    base := {"Sul": 120, "Sudeste": 260, "Norte": 80}
    peso := base[regiao] ?? 100
    linhas := []
    cycle i from 0 to 5:
        // Deterministico: o mesmo mês dá sempre o mesmo número, senão
        // o gráfico dançaria a cada clique.
        linhas.append({
            "mes": MESES[i],
            "receita": peso + ((i * 37) % 23) * 4 - 32,
            "meta": peso + 6
        })
    yield linhas

action somar(linhas, campo):
    yield linhas >> morph l: l[campo] >> distill a, v: a + v 0

action regioes():
    yield ["Sudeste", "Sul", "Norte"]

relay carregar, somar, regioes
''',
            "src/painel.df": '''// A página. Monta e NÃO sobe nada — quem sobe é o main.df.

adopt Arcane.Vitrine as V
adopt ./dados as D

action painel():
    lado := V.lateral()
    lado.cabecalho("Filtros", 4)
    regiao := lado.escolha("Região", D.regioes())
    detalhar := lado.interruptor("Mostrar a tabela", yes)

    V.titulo("{name}", icone := "📊")
    V.texto($"Região: {regiao} · primeiro semestre")

    linhas := D.carregar(regiao)
    receita := D.somar(linhas, "receita")
    meta := D.somar(linhas, "meta")

    colunas := V.colunas(3)
    colunas[0].metrica("Receita", $"R$ {receita} mil",
                       variacao := round((receita - meta) / meta * 100, 1))
    colunas[1].metrica("Meta", $"R$ {meta} mil")
    colunas[2].metrica("Meses", len(linhas))

    V.cabecalho("Evolução")
    g := V.grafico("linha", linhas)
    g.eixo_x("mes")
    g.eixo_y(["receita", "meta"])
    g.suavizar(yes)
    V.desenhar(g)

    given detalhar:
        V.cabecalho("Dados")
        V.frame(linhas)
        V.exportar_csv(linhas, nome := $"vendas-{regiao}.csv")

relay painel
''',
            "src/main.df": '''// Sobe o servidor.
//
//   dataforge vitrine dev     recarrega ao salvar
//   dataforge vitrine run     sem recarregar

adopt Arcane.Vitrine as V
adopt ./painel as P

V.app("{name}", icone := "📊")
V.pagina("/", P.painel, titulo := "Painel")
V.subir(porta := 8501)
''',
            "tests/painel_test.df": '''// Testar não precisa de navegador: a árvore de componentes é um dado.

adopt Arcane.Test as T
adopt Arcane.Vitrine as V
adopt ../src/painel as P

action test_o_painel_monta():
    t := V.testar(P.painel)
    T.assert_true(t.existe("titulo"))
    T.assert_eq(t.quantos("metrica"), 3)
    T.assert_false(t.falhou())

action test_o_grafico_desenha_svg():
    t := V.testar(P.painel)
    T.assert_contains(t.html(), "<svg")

action test_trocar_a_regiao_troca_os_numeros():
    t := V.testar(P.painel)
    antes := t.metrica("Receita")
    t.selecionar("Região", "Norte")
    T.assert_neq(t.metrica("Receita"), antes)

action test_o_interruptor_esconde_a_tabela():
    t := V.testar(P.painel)
    T.assert_eq(t.quantos("frame"), 1)
    t.marcar("Mostrar a tabela", no)
    T.assert_eq(t.quantos("frame"), 0)

action test_a_pagina_responde_por_http():
    app := V.app("teste")
    V.pagina("/", P.painel)
    r := V.pedir(app, "GET", "/")
    T.assert_eq(r["status"], 200)
    T.assert_contains(r["body"], "<!DOCTYPE html>")
''',
        },
    },

    # ── 8. Suíte de testes ───────────────────────────────────
    "test": {
        "name": "Suíte de testes",
        "description": "Como testar em DataForge: asserts, erros e cobertura",
        "icon": "🧪",
        "proximos": [
            ("dataforge test tests/ -v", "roda mostrando cada teste"),
            ("dataforge test tests/ --fail-fast", "para no primeiro erro"),
        ],
        "files": {
            "forge.toml": _forge_toml("Exemplo de testes em DataForge"),
            ".gitignore": GITIGNORE,
            "README.md": _readme(
                "{name}",
                "Como se testa em DataForge: uma ação por caso, nome que "
                "descreve o comportamento, e um teste para cada bug.",
                "dataforge test tests/\ndataforge test tests/ -v",
                notas="""## A regra

**Ao corrigir um bug, escreva primeiro o teste que falha.** Um bug sem
teste volta.

O nome do teste diz o comportamento, não o método:

```dataforge
action test_saque_acima_do_saldo_e_recusado():   // bom
action test_sacar_2():                            // ruim
```

"""),
            "src/conta.df": '''// Uma conta bancária — o domínio que os testes exercitam.

blueprint Conta(titular):
    private saldo: Float := 0.0
    historico: Cluster := []

    action depositar(valor):
        given valor smaller_eq 0:
            trigger "depósito precisa ser positivo"
        self.saldo += valor
        self.historico.append({"tipo": "depósito", "valor": valor})
        yield self.saldo

    action sacar(valor):
        given valor smaller_eq 0:
            trigger "saque precisa ser positivo"
        given valor bigger self.saldo:
            trigger $"saldo insuficiente: você tem {self.saldo}"
        self.saldo -= valor
        self.historico.append({"tipo": "saque", "valor": valor})
        yield self.saldo

    get extrato():
        yield self.saldo

    action movimentos():
        yield len(self.historico)

relay Conta
''',
            "tests/conta_test.df": '''// Uma ação por caso. O nome descreve o comportamento esperado —
// quando um teste falha, o nome já diz o que quebrou.

adopt Arcane.Test as T
adopt ../src/conta as C

action test_conta_nova_comeca_zerada():
    conta := spawn C.Conta("Ana")
    T.assert_eq(conta.extrato, 0.0)
    T.assert_eq(conta.movimentos(), 0)

action test_deposito_soma_ao_saldo():
    conta := spawn C.Conta("Ana")
    T.assert_eq(conta.depositar(100), 100)
    T.assert_eq(conta.depositar(50), 150)

action test_saque_subtrai_do_saldo():
    conta := spawn C.Conta("Ana")
    conta.depositar(100)
    T.assert_eq(conta.sacar(30), 70)

action test_saque_acima_do_saldo_e_recusado():
    conta := spawn C.Conta("Ana")
    conta.depositar(10)
    monitor:
        conta.sacar(999)
        T.assert_true(no)
    handle TriggerError as e:
        T.assert_contains(e.message, "insuficiente")

action test_a_mensagem_diz_quanto_ha():
    conta := spawn C.Conta("Ana")
    conta.depositar(42)
    monitor:
        conta.sacar(100)
    handle TriggerError as e:
        T.assert_contains(e.message, "42")

action test_deposito_negativo_e_recusado():
    conta := spawn C.Conta("Ana")
    monitor:
        conta.depositar(-5)
        T.assert_true(no)
    handle TriggerError as e:
        T.assert_contains(e.message, "positivo")

action test_historico_registra_cada_movimento():
    conta := spawn C.Conta("Ana")
    conta.depositar(100)
    conta.sacar(30)
    T.assert_eq(conta.movimentos(), 2)

action test_saque_recusado_nao_entra_no_historico():
    conta := spawn C.Conta("Ana")
    conta.depositar(10)
    monitor:
        conta.sacar(999)
    handle TriggerError as e:
        T.assert_eq(conta.movimentos(), 1)
''',
        },
    },
}
