# -*- coding: utf-8 -*-
"""Vinte e dois tipos de projeto — cada um com um núcleo que RODA.

As três páginas que já existiam (`gestor-tarefas`, `analise-vendas`,
`api-links`) descrevem projetos que moram em `projetos/`. Estas vinte e
duas descrevem **tipos**: o que muda de uma CLI para uma API, de um
ETL para um bot, de um motor de regras para um jogo.

A regra de toda página é a mesma: o bloco marcado como `src/…` roda
sozinho e termina com `assert`. `tests/test_projetos_tipos.py` extrai e
executa cada um — um projeto de exemplo que não roda ensina a
desconfiar de todos os outros.
"""


def _projeto(slug, titulo, descricao, intro, pecas, arvore, toml, nucleo,
             arquivo, teste, decisoes, alem, arquivo_teste=None):
    blocos = [
        {"p": intro},
        {"table": {"head": ["Peça", "O que ela exercita"], "rows": pecas}},
        {"h2": "Estrutura"},
        {"code": arvore, "lang": "text"},
        {"code": toml, "lang": "toml", "title": "forge.toml"},
        {"h2": "O núcleo"},
        {"p": "Este bloco roda sozinho — copie para um arquivo e rode "
              "`dataforge run`. Ele termina com `assert`, e é assim que esta "
              "página é conferida a cada build."},
        {"code": nucleo, "lang": "df", "title": arquivo},
        {"h2": "O teste"},
        {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo "
              "caminho relativo — `dataforge test tests/` descobre o arquivo "
              "sozinho."},
        {"code": teste, "lang": "df",
         "title": arquivo_teste or "tests/nucleo_test.df"},
        {"h2": "As decisões"},
        {"table": {"head": ["Decisão", "Sem ela"], "rows": decisoes}},
        {"h2": "Para ir além"},
        {"list": alem},
        {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
    ]
    return {"href": f"/docs/projetos/{slug}", "title": titulo,
            "description": descricao, "blocos": blocos}


def _toml(nome, descricao, deps=""):
    return f'''[project]
name = "{nome}"
version = "0.1.0"
description = "{descricao}"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]{deps}

[scripts]
start = "run src/main.df"
test = "test tests/"'''


TIPOS = [

# ══════════════════════════════════════════════════════════════
# 1. CLI de anotações
# ══════════════════════════════════════════════════════════════
_projeto(
"cli-notas", "CLI de anotações",
"Uma ferramenta de terminal com subcomandos, persistência em JSON e saída legível.",
"O projeto mais comum que existe, e o que mais cedo mostra se a arquitetura "
"aguenta crescer: cada subcomando é uma ação, o estado mora num arquivo, e a "
"leitura dos argumentos fica **separada** do que eles fazem — senão testar "
"`adicionar` exige simular a linha de comando inteira.",
[["`OS.argv()`", "ler os argumentos sem biblioteca"],
 ["`to_json` / `from_json`", "persistir sem banco"],
 ["`match`", "despachar o subcomando"],
 ["record", "a nota é imutável; editar devolve outra"]],
"""cli-notas/
  forge.toml
  src/
    main.df        le argv e despacha — e nada mais
    notas.df       a regra: adicionar, listar, concluir, buscar
    arquivo.df     onde o estado mora
  tests/
    notas_test.df""",
_toml("cli-notas", "Anotações no terminal"),
"""record Nota:
    id: Integer
    texto: String
    feita: Boolean

action adicionar(notas, texto):
    given texto.trim() is "":
        trigger "uma nota vazia nao e uma nota"
    proximo := 1 given len(notas) is 0 otherwise notas[-1].id + 1
    yield [...notas, Nota(proximo, texto.trim(), no)]

action concluir(notas, id):
    achou := no
    novas := []
    cycle n in notas:
        given n.id is id:
            achou := yes
            novas.append(n with {"feita": yes})
        otherwise:
            novas.append(n)
    given not achou:
        trigger $"nao ha nota {id}"
    yield novas

action buscar(notas, termo):
    yield notas >> sift n: termo.lower() in n.texto.lower()

action linha(n):
    marca := "[x]" given n.feita otherwise "[ ]"
    yield $"{marca} {str(n.id).pad_start(3)}  {n.texto}"

// O despacho: a unica parte que conhece a linha de comando.
action executar(notas, argv):
    given len(argv) is 0:
        yield {"notas": notas, "saida": ["uso: notas <adicionar|listar|feita|buscar>"]}
    comando := argv[0]
    resto := " ".join(argv[1:])
    match comando:
        point "adicionar":
            yield {"notas": adicionar(notas, resto), "saida": ["anotado"]}
        point "listar":
            yield {"notas": notas, "saida": notas >> morph n: linha(n)}
        point "feita":
            yield {"notas": concluir(notas, int(resto)), "saida": ["concluida"]}
        point "buscar":
            yield {"notas": notas, "saida": buscar(notas, resto) >> morph n: linha(n)}
        default:
            yield {"notas": notas, "saida": [$"comando desconhecido: {comando}"]}

// A persistencia e so texto: o record vira vault na ida e volta na volta.
action para_json(notas):
    yield to_json(notas >> morph n: {"id": n.id, "texto": n.texto, "feita": n.feita})

action de_json(texto):
    yield from_json(texto) >> morph v: Nota(v["id"], v["texto"], v["feita"])

estado := []
estado := executar(estado, ["adicionar", "comprar", "cafe"])["notas"]
estado := executar(estado, ["adicionar", "revisar", "o", "PR"])["notas"]
estado := executar(estado, ["feita", "1"])["notas"]
cycle l in executar(estado, ["listar"])["saida"]:
    out l

volta := de_json(para_json(estado))
assert volta is estado
assert len(buscar(estado, "revisar")) is 1
assert estado[0].feita and not estado[1].feita""",
"src/notas.df",
"""adopt ../src/notas as N

crucible "notas":
    trial "o id continua depois do ultimo":
        a := N.adicionar([], "um")
        b := N.adicionar(a, "dois")
        expect b[1].id is 2

    trial "nota vazia e recusada":
        expect(lambda => N.adicionar([], "   ")).to_raise()

    trial "concluir o que nao existe levanta":
        expect(lambda => N.concluir([], 7)).to_raise()""",
[["`executar` recebe `argv` como lista", "testar exige mexer no `sys.argv` do processo"],
 ["o record é imutável (`with`)", "`concluir` muda a lista que outra parte ainda está lendo"],
 ["`trigger` com o motivo", "a CLI imprime *“erro”* e sai com 0"],
 ["o id vem do **último**, não do tamanho", "apagar a nota 2 de 3 faz a próxima nascer com o id 3 — repetido"]],
["Troque o JSON por `Arcane.Database` sem mexer em `notas.df` — é para isso que a regra não sabe onde mora.",
 "Acrescente `--json` para a saída ser lida por outro programa.",
 "Veja [Receitas → CLI](/docs/receitas/cli) para cor, tabela e ajuda gerada."]),

# ══════════════════════════════════════════════════════════════
# 2. API REST com CRUD
# ══════════════════════════════════════════════════════════════
_projeto(
"api-rest", "API REST com CRUD",
"Os cinco verbos sobre um recurso, com os status certos e validação na entrada.",
"Uma API é regra de negócio mais transporte. O erro que mais custa é "
"misturar os dois: a validação vai parar dentro da rota, e testar uma regra "
"passa a exigir montar um pedido HTTP. Aqui a rota só traduz — o que decide "
"mora em ações que se testam sem socket.",
[["`server` / `route`", "as rotas, com parâmetro de caminho"],
 ["`Kiln.test`", "o pedido inteiro, sem abrir porta"],
 ["`Arcane.Database`", "SQLite em memória, com parâmetro `?`"],
 ["os status", "201, 204, 400, 404 — e o 405 que o Kiln dá sozinho"]],
"""api-produtos/
  forge.toml
  src/
    app.df         o 'server': rotas e traducao HTTP
    produtos.df    validar, criar, listar — sem HTTP nenhum
    banco.df       a conexao e o esquema
  main.df          'ignite' — o unico arquivo que abre porta
  tests/
    api_test.df""",
_toml("api-produtos", "API de produtos"),
"""adopt Kiln
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
out "CRUD verde\"""",
"src/app.df",
"""adopt Kiln
adopt ../src/app as App

crucible "api":
    trial "criar devolve 201 e o id":
        r := Kiln.test(App.api, "POST", "/produtos", {"nome": "Mouse", "preco": 50})
        expect r["status"] is 201
        expect "id" in r["body"]

    trial "os dois erros vem juntos":
        r := Kiln.test(App.api, "POST", "/produtos", {})
        expect len(r["body"]["erros"]) is 2""",
[["`problemas` devolve **todos** os erros", "o formulário é corrigido um campo por envio"],
 ["`?` no SQL, nunca interpolação", "`nome := \"x'); DROP TABLE produtos;--\"` apaga a tabela"],
 ["`server` monta, `ignite` sobe (em `main.df`)", "importar o módulo no teste sobe um servidor que nunca termina"],
 ["`404` do recurso separado do `404` da rota", "o cliente não sabe se errou o caminho ou o id"]],
["Paginação com `DB.paginate` — ver [Banco → receitas](/docs/banco-de-dados/receitas).",
 "Contrato OpenAPI gerado das rotas: [OpenAPI](/docs/tecnicas/api).",
 "Autenticação por token no `middleware`: [Kiln → middleware](/docs/kiln/middleware)."]),

# ══════════════════════════════════════════════════════════════
# 3. ETL de CSV
# ══════════════════════════════════════════════════════════════
_projeto(
"etl", "Pipeline ETL",
"Extrair, converter, validar e carregar — e separar a linha ruim em vez de parar tudo.",
"Um ETL de verdade recebe dado sujo. As duas respostas erradas são parar na "
"primeira linha ruim (o lote de ontem nunca carrega) e engolir a linha ruim "
"(o relatório de amanhã soma zero onde havia um valor). A certa é **separar**: "
"a linha ruim vai para uma lista com o motivo, e o resto segue.",
[["`lines` / `split`", "ler CSV sem biblioteca"],
 ["pipeline `>>`", "converter e filtrar em cadeia"],
 ["`Arcane.Decimal`", "somar dinheiro sem erro de float"],
 ["vault de rejeitados", "o motivo por linha, para quem corrige a fonte"]],
"""etl-vendas/
  src/
    extrair.df     texto -> linhas cruas
    transformar.df linha crua -> venda, ou motivo da recusa
    carregar.df    vendas -> banco / relatorio
    main.df        liga os tres
  dados/
    entrada.csv
  tests/""",
_toml("etl-vendas", "ETL de vendas"),
"""adopt Arcane.Decimal as Dec

steady CSV := \"\"\"data,loja,valor
2026-09-01,centro,120.50
2026-09-01,norte,80.00
2026-09-02,centro,abc
2026-09-02,,45.10
2026-09-03,norte,19.99
\"\"\"

action extrair(texto):
    linhas := texto.trim().lines()
    cabecalho := linhas[0].split(",")
    cruas := []
    cycle i from 1 to len(linhas) - 1:
        campos := linhas[i].split(",")
        cruas.append({"linha": i + 1, "campos": zip(cabecalho, campos)})
    yield cruas

action transformar(crua):
    c := {}
    cycle par in crua["campos"]:
        c[par[0]] := par[1].trim()
    given c["loja"] is "":
        yield {"ok": no, "linha": crua["linha"], "motivo": "loja vazia"}
    given not regex_test("^[0-9]+([.][0-9]{1,2})?$", c["valor"]):
        yield {"ok": no, "linha": crua["linha"], "motivo": $"valor '{c["valor"]}' nao e numero"}
    yield {"ok": yes, "venda": {"data": c["data"], "loja": c["loja"], "valor": Dec.de(c["valor"])}}

action rodar(texto):
    resultados := extrair(texto) >> morph r: transformar(r)
    boas := resultados >> sift r: r["ok"] >> morph r: r["venda"]
    ruins := resultados >> sift r: not r["ok"]
    por_loja := {}
    cycle v in boas:
        por_loja[v["loja"]] := Dec.soma([por_loja[v["loja"]] ?? Dec.zero(), v["valor"]])
    yield {"carregadas": len(boas), "rejeitadas": ruins, "por_loja": por_loja}

r := rodar(CSV)
out $"{r['carregadas']} carregadas, {len(r['rejeitadas'])} rejeitadas"
cycle ruim in r["rejeitadas"]:
    out $"  linha {ruim['linha']}: {ruim['motivo']}"

assert r["carregadas"] is 3
assert Dec.texto(r["por_loja"]["norte"]) is "99.99"
assert Dec.texto(r["por_loja"]["centro"]) is "120.50\"""",
"src/main.df",
"""adopt ../src/main as T

crucible "transformar":
    trial "valor com letra vira recusa, e nao zero":
        r := T.transformar({"linha": 4, "campos": [["data", "x"], ["loja", "a"], ["valor", "1,5"]]})
        expect r["ok"] is no
        expect r["linha"] is 4""",
[["a linha ruim é **separada**, não descartada", "o total fecha, e ninguém sabe que faltam três vendas"],
 ["o número da linha vai junto do motivo", "quem corrige a fonte procura a linha num arquivo de 40 mil"],
 ["`Decimal` a partir do **texto**", "`0.1 + 0.2` vira `0.30000000000000004` no relatório financeiro"],
 ["extrair, transformar e carregar em arquivos diferentes", "trocar CSV por API reescreve a validação junto"]],
["Grave os rejeitados num CSV ao lado — é o que o time da fonte vai pedir.",
 "Troque o `for` por `Arcane.Quadro` quando o volume passar de 100 mil linhas: [Quadro](/docs/dados/quadro).",
 "Agende com cron e alerte quando `rejeitadas` passar de 5%."]),

# ══════════════════════════════════════════════════════════════
# 4. Motor de regras de negócio
# ══════════════════════════════════════════════════════════════
_projeto(
"motor-de-regras", "Motor de regras",
"Regras de desconto e elegibilidade como dados, com o motivo de cada decisão.",
"Regra de negócio escrita como `given` aninhado vira um arquivo que ninguém "
"quer tocar: a décima regra é a exceção da terceira, e a ordem importa sem "
"que ninguém saiba por quê. Um motor de regras transforma cada regra num "
"**dado** com nome, condição e efeito — e a decisão passa a vir com a lista do "
"que se aplicou.",
[["lambda como dado", "a condição e o efeito de cada regra"],
 ["prioridade explícita", "a ordem deixa de ser a do arquivo"],
 ["o relatório da decisão", "quem liga no suporte pergunta *por quê*"],
 ["`exclusiva`", "a regra que, quando vale, impede as outras"]],
"""motor-descontos/
  src/
    regras.df      o catalogo — so dados
    motor.df       avaliar, na ordem de prioridade
  tests/
    regras_test.df  um trial por regra""",
_toml("motor-descontos", "Descontos como regras"),
"""action regra(nome, prioridade, quando, desconto, exclusiva := no):
    yield {"nome": nome, "prioridade": prioridade, "quando": quando,
           "desconto": desconto, "exclusiva": exclusiva}

REGRAS := [
    regra("black-friday", 1, lambda p: p["data"] is "2026-11-27", 0.30, yes),
    regra("primeira-compra", 2, lambda p: p["compras_antes"] is 0, 0.10),
    regra("carrinho-grande", 3, lambda p: p["total"] bigger_eq 500, 0.05),
    regra("fidelidade", 4, lambda p: p["compras_antes"] bigger_eq 10, 0.08)
]

action avaliar(pedido, regras):
    aplicadas := []
    cycle r in sorted(regras, lambda a: a["prioridade"]):
        given r["quando"](pedido):
            aplicadas.append(r)
            given r["exclusiva"]:
                halt
    // desconto composto, com teto: dois descontos de 50% nao sao 100%
    fator := 1.0
    cycle r in aplicadas:
        fator := fator * (1 - r["desconto"])
    desconto := min(1 - fator, 0.35)
    yield {"total": round(pedido["total"] * (1 - desconto), 2),
           "desconto": round(desconto, 4),
           "porque": aplicadas >> morph r: r["nome"]}

novo := avaliar({"data": "2026-09-21", "compras_antes": 0, "total": 600}, REGRAS)
out novo
assert novo["porque"] is ["primeira-compra", "carrinho-grande"]
assert novo["total"] is 513.0

bf := avaliar({"data": "2026-11-27", "compras_antes": 12, "total": 600}, REGRAS)
assert bf["porque"] is ["black-friday"]
assert bf["total"] is 420.0""",
"src/motor.df",
"""adopt ../src/motor as M

crucible "descontos":
    trial "o teto segura a soma":
        p := {"data": "2026-09-21", "compras_antes": 12, "total": 1000}
        expect M.avaliar(p, M.REGRAS)["desconto"] smaller_eq 0.35

    trial "a exclusiva impede as outras":
        p := {"data": "2026-11-27", "compras_antes": 0, "total": 1000}
        expect M.avaliar(p, M.REGRAS)["porque"] is ["black-friday"]""",
[["prioridade é um campo", "reordenar o arquivo muda o preço cobrado"],
 ["o resultado traz `porque`", "o suporte não consegue explicar um preço"],
 ["teto no desconto composto", "três regras somadas dão 120% e o pedido sai com preço negativo"],
 ["regra exclusiva **para** a avaliação", "a Black Friday soma com o cupom que ela devia substituir"]],
["Carregue as regras de um arquivo — a condição vira uma expressão avaliada com [Arcane.Dsl](/docs/biblioteca/dsl).",
 "Registre cada decisão com `porque` para auditoria.",
 "Teste por propriedade: nenhum pedido sai com total negativo — [Propriedades](/docs/crucible/propriedades)."]),

# ══════════════════════════════════════════════════════════════
# 5. Jogo de terminal
# ══════════════════════════════════════════════════════════════
_projeto(
"jogo", "Jogo de terminal",
"Jogo da velha com um adversário que não perde — minimax com poda.",
"Jogo é o projeto que mais cedo ensina a separar **estado** de **apresentação**: "
"o tabuleiro é um dado, a jogada é uma função pura sobre ele, e o terminal só "
"desenha. Com isso a IA consegue simular milhares de jogos sem imprimir nada.",
[["cluster de 9 casas", "o estado inteiro do jogo"],
 ["recursão", "o minimax desce até o fim de cada linha de jogo"],
 ["poda alfa-beta", "a mesma resposta visitando uma fração dos nós"],
 ["função pura", "`jogar` devolve um tabuleiro novo"]],
"""jogo-da-velha/
  src/
    tabuleiro.df   jogar, vencedor, casas livres
    ia.df          minimax
    tela.df        desenhar e ler a jogada
    main.df
  tests/""",
_toml("jogo-da-velha", "Jogo da velha com IA"),
"""steady LINHAS := [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]

action vencedor(t):
    cycle l in LINHAS:
        given t[l[0]] is not " " and t[l[0]] is t[l[1]] and t[l[1]] is t[l[2]]:
            yield t[l[0]]
    yield void

action livres(t):
    yield [i cycle i in range(0, 9) given t[i] is " "]

action jogar(t, casa, peca):
    novo := [...t]
    novo[casa] := peca
    yield novo

action outro(p):
    yield "O" given p is "X" otherwise "X"

// Pontua do ponto de vista de 'eu'. A profundidade entra na conta para a
// IA preferir ganhar AGORA a ganhar daqui a tres jogadas.
action minimax(t, vez, eu, alfa, beta, prof):
    v := vencedor(t)
    given v is eu:
        yield 10 - prof
    given v is not void:
        yield prof - 10
    casas := livres(t)
    given len(casas) is 0:
        yield 0
    given vez is eu:
        melhor := -100
        cycle c in casas:
            melhor := max(melhor, minimax(jogar(t, c, vez), outro(vez), eu, alfa, beta, prof + 1))
            alfa := max(alfa, melhor)
            given alfa bigger_eq beta:
                halt
        yield melhor
    pior := 100
    cycle c in casas:
        pior := min(pior, minimax(jogar(t, c, vez), outro(vez), eu, alfa, beta, prof + 1))
        beta := min(beta, pior)
        given alfa bigger_eq beta:
            halt
    yield pior

action melhor_jogada(t, eu):
    melhor := -1000
    escolha := -1
    cycle c in livres(t):
        nota := minimax(jogar(t, c, eu), outro(eu), eu, -1000, 1000, 1)
        given nota bigger melhor:
            melhor := nota
            escolha := c
    yield escolha

action desenhar(t):
    yield [$" {t[0]} | {t[1]} | {t[2]}", $" {t[3]} | {t[4]} | {t[5]}", $" {t[6]} | {t[7]} | {t[8]}"].join("\\n---+---+---\\n")

// X tem duas em linha: a IA (O) precisa bloquear na casa 2.
t := ["X", "X", " ", " ", "O", " ", " ", " ", " "]
assert melhor_jogada(t, "O") is 2

// O tem duas em linha: ganhar vale mais que bloquear.
t2 := ["X", "X", " ", "O", "O", " ", "X", " ", " "]
assert melhor_jogada(t2, "O") is 5

// IA contra IA termina sempre empatada.
jogo := [" " cycle _ in range(0, 9)]
vez := "X"
persist vencedor(jogo) is void and len(livres(jogo)) bigger 0:
    jogo := jogar(jogo, melhor_jogada(jogo, vez), vez)
    vez := outro(vez)
out desenhar(jogo)
assert vencedor(jogo) is void""",
"src/ia.df",
"""adopt ../src/ia as IA

crucible "ia":
    trial "bloqueia a linha do adversario":
        t := ["X", "X", " ", " ", "O", " ", " ", " ", " "]
        expect IA.melhor_jogada(t, "O") is 2""",
[["o tabuleiro não sabe desenhar", "a IA imprime cada jogo simulado"],
 ["`jogar` devolve cópia", "a simulação de uma linha estraga o tabuleiro da seguinte"],
 ["a profundidade na nota", "a IA enrola: vê a vitória em uma e prefere a de três"],
 ["poda alfa-beta", "a primeira jogada visita 549 mil nós em vez de ~20 mil"]],
["Meça a poda com `Arcane.Bench` antes e depois — [Medir](/docs/cli/bench).",
 "Troque para um tabuleiro 4x4 e veja por que o minimax puro deixa de servir.",
 "Um jogo de verdade tem laço de eventos: [Arcane.Laco](/docs/biblioteca/laco)."]),

# ══════════════════════════════════════════════════════════════
# 6. Folha de pagamento
# ══════════════════════════════════════════════════════════════
_projeto(
"folha-de-pagamento", "Cálculo financeiro",
"Folha de pagamento com faixas progressivas — em Decimal, e com o centavo que sobra repartido.",
"Dinheiro tem duas regras que float quebra: somar tem de ser exato, e dividir "
"tem de fechar. Um salário de R$ 1000,00 dividido em três parcelas não são "
"três de 333,33: é 333,34 + 333,33 + 333,33. Este projeto calcula uma folha "
"com desconto progressivo por faixa e reparte sem perder centavo.",
[["`19.99d`", "o literal decimal, construído do texto"],
 ["`Dec.arredondar`", "arredondar com modo declarado"],
 ["`Dec.repartir`", "dividir e o centavo fechar"],
 ["tabela de faixas", "o imposto progressivo como dado"]],
"""folha/
  src/
    faixas.df     a tabela do ano — so dados
    calculo.df    bruto -> descontos -> liquido
    holerite.df   o texto que vai para a pessoa
  tests/
    calculo_test.df  com os exemplos da tabela oficial""",
_toml("folha", "Folha de pagamento"),
"""adopt Arcane.Decimal as Dec

// Faixas de exemplo (NAO sao as oficiais): 'ate' e o teto da faixa.
FAIXAS := [
    {"ate": 2000.00d, "aliquota": 0.075d},
    {"ate": 3500.00d, "aliquota": 0.09d},
    {"ate": 5000.00d, "aliquota": 0.12d},
    {"ate": void,     "aliquota": 0.14d}
]

// Progressivo: cada faixa cobra so o PEDACO do salario que cai nela.
action desconto(bruto, faixas):
    total := Dec.zero()
    piso := Dec.zero()
    cycle f in faixas:
        teto := f["ate"] ?? bruto
        given bruto bigger piso:
            base := min(bruto, teto) - piso
            given base bigger Dec.zero():
                total := total + base * f["aliquota"]
        piso := teto
    yield Dec.arredondar(total, 2)

action holerite(nome, bruto):
    d := desconto(bruto, FAIXAS)
    yield {"nome": nome, "bruto": bruto, "desconto": d, "liquido": bruto - d}

h := holerite("Ana", 4200.00d)
out $"{h['nome']}: bruto {Dec.texto(h['bruto'])}, desconto {Dec.texto(h['desconto'])}, liquido {Dec.texto(h['liquido'])}"

// 2000 * 7,5% + 1500 * 9% + 700 * 12% = 150 + 135 + 84 = 369
assert Dec.texto(h["desconto"]) is "369.00"
assert Dec.texto(h["liquido"]) is "3831.00"

// A parcela que fecha: tres de 333,33 perderiam um centavo.
parcelas := Dec.repartir(1000.00d, 3)
out parcelas >> morph p: Dec.texto(p)
assert Dec.texto(Dec.soma(parcelas)) is "1000.00\"""",
"src/calculo.df",
"""adopt Arcane.Decimal as Dec
adopt ../src/calculo as C

crucible "desconto progressivo":
    trial "abaixo da primeira faixa":
        expect Dec.texto(C.desconto(1000.00d, C.FAIXAS)) is "75.00"

    trial "a soma das parcelas fecha":
        expect Dec.texto(Dec.soma(Dec.repartir(10.00d, 3))) is "10.00\"""",
[["o literal `d`", "`Decimal(0.1)` já nasce com o erro do float"],
 ["a faixa cobra só o **pedaço** dela", "o salário de 2001 paga 9% sobre tudo, e ganhar um real a mais reduz o líquido"],
 ["`repartir` em vez de dividir", "o parcelamento some com um centavo por cliente, e a conciliação nunca fecha"],
 ["as faixas são um arquivo de dados", "a atualização anual vira uma mudança de código"]],
["Compare com [Arcane.Decimal](/docs/biblioteca/decimal) e [Decimal](/docs/tecnicas/decimal).",
 "Gere o holerite em planilha: [Planilhas](/docs/tecnicas/planilhas).",
 "Um teste por linha da tabela oficial — quando a lei muda, o teste muda junto."]),

# ══════════════════════════════════════════════════════════════
# 7. Autenticação completa
# ══════════════════════════════════════════════════════════════
_projeto(
"autenticacao", "Serviço de autenticação",
"Cadastro, login com scrypt, bloqueio progressivo e token assinado com prazo.",
"Autenticação é onde um projeto pequeno mais facilmente fica inseguro: a "
"senha guardada com SHA-256, o login que diz *“usuário não existe”* (e com "
"isso confirma quais e-mails têm conta), e o token que nunca vence. Este "
"projeto faz as três coisas do jeito certo, com o que a biblioteca já tem.",
[["`Crypto.hash_password`", "scrypt, com sal por senha"],
 ["`Crypto.hmac`", "o token assinado"],
 ["tentativas por conta", "o bloqueio progressivo"],
 ["a mesma resposta nos dois erros", "não confirmar quais contas existem"]],
"""auth/
  src/
    senhas.df      forca, hash, conferencia
    contas.df      cadastro e login
    tokens.df      emitir e conferir
  tests/
    login_test.df""",
_toml("auth", "Autenticação"),
"""adopt Arcane.Crypto as Crypto

steady CHAVE := "troque-por-uma-variavel-de-ambiente"
contas := {}
falhas := {}

action cadastrar(email, senha):
    given len(senha) smaller 10:
        trigger "a senha precisa de pelo menos 10 caracteres"
    given email in contas:
        trigger "nao foi possivel cadastrar"
    contas[email] := Crypto.hash_password(senha)

// A MESMA mensagem para "nao existe" e "senha errada": a diferenca e
// exatamente o que quem ataca quer descobrir.
action entrar(email, senha, agora):
    f := falhas[email] ?? {"n": 0, "ate": 0}
    given agora smaller f["ate"]:
        yield {"ok": no, "motivo": "tente mais tarde"}
    guardada := contas[email] ?? void
    given guardada is void or not Crypto.verify_password(senha, guardada):
        n := f["n"] + 1
        // 1, 2, 4, 8... segundos a partir da terceira falha
        espera := 0 given n smaller 3 otherwise 2 ** (n - 3)
        falhas[email] := {"n": n, "ate": agora + espera}
        yield {"ok": no, "motivo": "email ou senha incorretos"}
    falhas[email] := {"n": 0, "ate": 0}
    yield {"ok": yes, "token": emitir(email, agora + 3600)}

action emitir(email, vence):
    carga := $"{email}|{vence}"
    yield $"{carga}|{Crypto.hmac(CHAVE, carga)}"

action conferir(token, agora):
    partes := token.split("|")
    given len(partes) is not 3:
        yield void
    carga := $"{partes[0]}|{partes[1]}"
    given not Crypto.hmac_verify(CHAVE, carga, partes[2]):
        yield void
    given int(partes[1]) smaller_eq agora:
        yield void
    yield partes[0]

cadastrar("ana@exemplo.com", "cavalo-bateria-grampo")
ok := entrar("ana@exemplo.com", "cavalo-bateria-grampo", 1000)
assert ok["ok"]
assert conferir(ok["token"], 1001) is "ana@exemplo.com"
assert conferir(ok["token"], 99999) is void
assert conferir(ok["token"].replace("ana", "eva"), 1001) is void

a := entrar("ana@exemplo.com", "errada", 2000)
b := entrar("ninguem@exemplo.com", "errada", 2000)
assert a["motivo"] is b["motivo"]

cycle i in range(0, 4):
    entrar("ana@exemplo.com", "errada", 3000)
assert entrar("ana@exemplo.com", "cavalo-bateria-grampo", 3000)["motivo"] is "tente mais tarde"
assert entrar("ana@exemplo.com", "cavalo-bateria-grampo", 3100)["ok"]
out "autenticacao verde\"""",
"src/contas.df",
"""adopt ../src/contas as C

crucible "login":
    trial "o token adulterado nao vale":
        C.cadastrar("bia@exemplo.com", "uma-senha-longa")
        t := C.entrar("bia@exemplo.com", "uma-senha-longa", 0)["token"]
        expect C.conferir(t + "x", 1) is void""",
[["scrypt, e não SHA-256", "uma GPU testa bilhões de SHA-256 por segundo"],
 ["mesma resposta nos dois erros", "o formulário vira um oráculo de quais e-mails têm conta"],
 ["espera **progressiva**, não bloqueio fixo", "quem ataca bloqueia a conta da vítima de propósito"],
 ["`hmac_verify`, não `is`", "comparar a assinatura com `is` vaza, pelo tempo, quantos caracteres acertaram"],
 ["o prazo **dentro** da carga assinada", "trocar o prazo não invalida a assinatura"]],
["O token padrão da indústria: `Crypto.jwt_*` — [Autenticação](/docs/seguranca/autenticacao).",
 "2FA com TOTP: [Arcane.Seguranca](/docs/biblioteca/seguranca).",
 "Quem pode o quê depois de entrar: [Arcane.Politica](/docs/biblioteca/politica)."]),

# ══════════════════════════════════════════════════════════════
# 8. Fila de trabalho
# ══════════════════════════════════════════════════════════════
_projeto(
"fila-de-trabalho", "Processador de fila",
"Tarefas com retentativa, recuo exponencial e carta morta — sem perder nenhuma.",
"Todo sistema acaba com trabalho que não cabe no pedido: mandar e-mail, "
"gerar PDF, chamar um serviço lento. A fila resolve, e cria três perguntas "
"novas: o que acontece quando a tarefa falha, quantas vezes se tenta, e onde "
"fica a que nunca vai dar certo. Esta página responde as três com um laço "
"que se entende em cinco minutos.",
[["vault por tarefa", "tentativas, próximo horário e último erro"],
 ["recuo exponencial", "o serviço que caiu não é martelado"],
 ["carta morta", "a tarefa impossível sai do caminho sem sumir"],
 ["`monitor` / `handle`", "a falha de uma não para as outras"]],
"""processador/
  src/
    fila.df        enfileirar, proxima, concluir, falhar
    trabalhos.df   o que cada tipo de tarefa faz
    main.df        o laco
  tests/""",
_toml("processador", "Fila de trabalho"),
"""steady MAXIMO := 4

fila := []
mortas := []
feitas := []

action enfileirar(tipo, dados):
    fila.append({"tipo": tipo, "dados": dados, "tentativas": 0, "quando": 0, "erro": ""})

action recuo(tentativa):
    yield 2 ** tentativa

action proxima(agora):
    cycle i in range(0, len(fila)):
        given fila[i]["quando"] smaller_eq agora:
            yield fila.pop(i)
    yield void

// Um servico que falha nas duas primeiras chamadas, e um que nunca volta.
chamadas := {"email": 0}
action trabalhar(t):
    match t["tipo"]:
        point "email":
            chamadas["email"] += 1
            given chamadas["email"] smaller_eq 2:
                trigger "servidor de e-mail indisponivel"
            yield $"enviado para {t['dados']}"
        point "pdf":
            yield $"gerado {t['dados']}.pdf"
        default:
            trigger $"ninguem sabe fazer '{t['tipo']}'"

action rodar_ate(fim):
    agora := 0
    persist agora smaller_eq fim:
        t := proxima(agora)
        given t is void:
            agora += 1
            skip
        monitor:
            feitas.append(trabalhar(t))
        handle Error as e:
            t["tentativas"] += 1
            t["erro"] := e.message
            given t["tentativas"] bigger_eq MAXIMO:
                mortas.append(t)
            otherwise:
                t["quando"] := agora + recuo(t["tentativas"])
                fila.append(t)

enfileirar("email", "ana@exemplo.com")
enfileirar("pdf", "relatorio-setembro")
enfileirar("fax", "1998")
rodar_ate(60)

out $"feitas: {feitas}"
out $"mortas: {mortas >> morph m: m['tipo'] + ' (' + m['erro'] + ')'}"
assert len(feitas) is 2
assert len(mortas) is 1 and mortas[0]["tipo"] is "fax"
assert mortas[0]["tentativas"] is MAXIMO
assert len(fila) is 0""",
"src/fila.df",
"""adopt ../src/fila as F

crucible "recuo":
    trial "o recuo dobra":
        expect [F.recuo(1), F.recuo(2), F.recuo(3)] is [2, 4, 8]""",
[["o erro fica **na tarefa**", "a carta morta não diz por que morreu"],
 ["recuo exponencial", "mil tarefas repetindo a cada segundo derrubam de novo o serviço que acabou de voltar"],
 ["teto de tentativas", "a tarefa impossível roda para sempre e atrasa todas as outras"],
 ["`handle Error`, não `RuntimeError`", "um `trigger` escapa do `handle` e derruba o laço inteiro"]],
["Fila que sobrevive a reinício, com reserva e prazo: `Eventos.fila_persistente` — [Arcane.Eventos](/docs/biblioteca/eventos).",
 "Acrescente *jitter* ao recuo — [Arcane.Malha](/docs/biblioteca/malha) explica por quê.",
 "Vários operários: [Concorrência](/docs/tecnicas/concorrencia)."]),

# ══════════════════════════════════════════════════════════════
# 9. Interpretador de expressões
# ══════════════════════════════════════════════════════════════
_projeto(
"interpretador", "Interpretador de expressões",
"Lexer, parser recursivo descendente e avaliador — uma calculadora com variáveis.",
"Escrever um interpretador pequeno é a forma mais rápida de entender o que "
"este repositório faz em escala: texto vira token, token vira árvore, árvore "
"vira valor. As três fases ficam separadas pelo mesmo motivo que no "
"DataForge — um erro de sintaxe tem de ser reportado **antes** de qualquer conta.",
[["lexer", "texto → tokens, com a coluna de cada um"],
 ["parser recursivo descendente", "a precedência vem da ordem das funções"],
 ["árvore como vault", "a mesma forma que a `Arcane.Macro` usa"],
 ["ambiente de variáveis", "`x := 2` e depois `x * 3`"]],
"""calc/
  src/
    lexer.df
    parser.df     expr := termo (('+'|'-') termo)*
    avaliar.df
    repl.df
  tests/""",
_toml("calc", "Calculadora com variáveis"),
"""action tokens(texto):
    saida := []
    i := 0
    persist i smaller len(texto):
        c := texto[i]
        given c is " ":
            i += 1
            skip
        given isdigit(c) or c is ".":
            j := i
            persist j smaller len(texto) and (isdigit(texto[j]) or texto[j] is "."):
                j += 1
            saida.append({"tipo": "num", "valor": float(texto[i:j]), "col": i})
            i := j
            skip
        given isalpha(c):
            j := i
            persist j smaller len(texto) and isalnum(texto[j]):
                j += 1
            saida.append({"tipo": "nome", "valor": texto[i:j], "col": i})
            i := j
            skip
        given c in ["+", "-", "*", "/", "(", ")", "="]:
            saida.append({"tipo": c, "valor": c, "col": i})
            i += 1
            skip
        trigger $"caractere inesperado '{c}' na coluna {i + 1}"
    saida.append({"tipo": "fim", "valor": "", "col": len(texto)})
    yield saida

// O parser guarda a posicao num vault: e o estado que as funcoes dividem.
action parse(texto):
    p := {"t": tokens(texto), "i": 0}
    arvore := atribuicao(p)
    given p["t"][p["i"]]["tipo"] is not "fim":
        trigger $"sobrou '{p['t'][p['i']]['valor']}' na coluna {p['t'][p['i']]['col'] + 1}"
    yield arvore

action olhar(p):
    yield p["t"][p["i"]]

action consumir(p):
    t := p["t"][p["i"]]
    p["i"] += 1
    yield t

action atribuicao(p):
    given olhar(p)["tipo"] is "nome" and p["t"][p["i"] + 1]["tipo"] is "=":
        nome := consumir(p)["valor"]
        consumir(p)
        yield {"no": "atr", "nome": nome, "valor": expr(p)}
    yield expr(p)

action expr(p):
    esq := termo(p)
    persist olhar(p)["tipo"] in ["+", "-"]:
        op := consumir(p)["tipo"]
        esq := {"no": "bin", "op": op, "esq": esq, "dir": termo(p)}
    yield esq

action termo(p):
    esq := fator(p)
    persist olhar(p)["tipo"] in ["*", "/"]:
        op := consumir(p)["tipo"]
        esq := {"no": "bin", "op": op, "esq": esq, "dir": fator(p)}
    yield esq

action fator(p):
    t := consumir(p)
    match t["tipo"]:
        point "num":
            yield {"no": "num", "valor": t["valor"]}
        point "nome":
            yield {"no": "var", "nome": t["valor"]}
        point "-":
            yield {"no": "neg", "valor": fator(p)}
        point "(":
            dentro := expr(p)
            given consumir(p)["tipo"] is not ")":
                trigger "faltou fechar o parentese"
            yield dentro
        default:
            trigger $"esperava um numero na coluna {t['col'] + 1}"

action avaliar(nodo, amb):
    match nodo["no"]:
        point "num":
            yield nodo["valor"]
        point "var":
            given nodo["nome"] not in amb:
                trigger $"'{nodo['nome']}' nao foi definida"
            yield amb[nodo["nome"]]
        point "neg":
            yield -avaliar(nodo["valor"], amb)
        point "atr":
            amb[nodo["nome"]] := avaliar(nodo["valor"], amb)
            yield amb[nodo["nome"]]
        point "bin":
            a := avaliar(nodo["esq"], amb)
            b := avaliar(nodo["dir"], amb)
            match nodo["op"]:
                point "+":
                    yield a + b
                point "-":
                    yield a - b
                point "*":
                    yield a * b
                point "/":
                    given b is 0:
                        trigger "divisao por zero"
                    yield a / b

amb := {}
action rodar(linha):
    yield avaliar(parse(linha), amb)

assert rodar("1 + 2 * 3") is 7.0
assert rodar("(1 + 2) * 3") is 9.0
assert rodar("x = 4") is 4.0
assert rodar("-x * 2 + 10") is 2.0

monitor:
    rodar("2 * (3 + ")
    assert no
handle Error as e:
    out e.message
    assert "coluna" in e.message""",
"src/parser.df",
"""adopt ../src/parser as P

crucible "precedencia":
    trial "multiplicacao antes da soma":
        expect P.avaliar(P.parse("2 + 3 * 4"), {}) is 14.0""",
[["uma função por nível de precedência", "`2 + 3 * 4` dá 20"],
 ["a coluna em todo token", "o erro diz *“sintaxe inválida”* sem dizer onde"],
 ["o parser confere que **tudo** foi consumido", "`2 3` avalia para 2 e o 3 some calado"],
 ["parse e avaliação separados", "um erro de sintaxe no fim da linha acontece depois da atribuição do começo"]],
["Compare com o parser de verdade: [Arquitetura](/docs/referencia/arquitetura).",
 "A mesma coisa em combinadores: [Arcane.Dsl](/docs/biblioteca/dsl).",
 "Receita completa: [Receitas → interpretador](/docs/receitas/interpretador)."]),

# ══════════════════════════════════════════════════════════════
# 10. Máquina de estados de pedido
# ══════════════════════════════════════════════════════════════
_projeto(
"maquina-de-estados", "Fluxo de pedido",
"Uma máquina de estados explícita, que recusa a transição impossível e guarda o histórico.",
"Um pedido tem estados, e os bugs caros moram nas transições: o pedido "
"cancelado que é despachado, o pago que volta a aguardar pagamento. Com o "
"estado num texto livre, nada impede isso. Com uma tabela de transições, a "
"transição impossível é **recusada** — e o histórico diz quem mudou o quê.",
[["enum", "os estados possíveis — e só eles"],
 ["tabela de transições", "de onde se pode ir para onde"],
 ["histórico", "cada mudança com quem e quando"],
 ["`match` exaustivo", "o `check` avisa do estado esquecido"]],
"""pedidos/
  src/
    estados.df     o enum e a tabela
    pedido.df      transicionar, historico
  tests/
    fluxo_test.df   um trial por transicao PROIBIDA""",
_toml("pedidos", "Fluxo de pedidos"),
"""enum Estado:
    Criado
    Pago
    Separado
    Enviado
    Entregue
    Cancelado

TRANSICOES := {
    "Criado": ["Pago", "Cancelado"],
    "Pago": ["Separado", "Cancelado"],
    "Separado": ["Enviado"],
    "Enviado": ["Entregue"],
    "Entregue": [],
    "Cancelado": []
}

blueprint Pedido(id):
    estado := Estado.Criado
    historico: Cluster := []

    action mover(para, quem):
        permitidos := TRANSICOES[self.estado.name]
        given para.name not in permitidos:
            trigger $"pedido {self.id}: '{self.estado.name}' nao vai para '{para.name}'. Pode ir para: {permitidos}"
        self.historico.append({"de": self.estado.name, "para": para.name, "quem": quem})
        self.estado := para

    action terminal():
        yield len(TRANSICOES[self.estado.name]) is 0

p := spawn Pedido(42)
p.mover(Estado.Pago, "gateway")
p.mover(Estado.Separado, "ana")
p.mover(Estado.Enviado, "transportadora")

monitor:
    p.mover(Estado.Cancelado, "cliente")
    assert no
handle Error as e:
    out e.message

p.mover(Estado.Entregue, "transportadora")
assert p.terminal()
assert len(p.historico) is 4
assert p.historico[0]["quem"] is "gateway\"""",
"src/pedido.df",
"""adopt ../src/pedido as P

crucible "transicoes proibidas":
    trial "cancelado nao e enviado":
        p := spawn P.Pedido(1)
        p.mover(P.Estado.Cancelado, "x")
        expect(lambda => p.mover(P.Estado.Enviado, "x")).to_raise()""",
[["o estado é um `enum`", "`\"Pagu\"` é aceito e o pedido some de todo relatório"],
 ["a tabela fica num lugar só", "a regra *“cancelado não volta”* está escrita em cinco rotas, e uma esquece"],
 ["a mensagem lista para onde **pode** ir", "quem integra descobre as transições por tentativa e erro"],
 ["o histórico nasce com a transição", "o cliente pergunta quem cancelou, e ninguém sabe"]],
["A máquina genérica da biblioteca: `Padroes.maquina` — [Arcane.Padroes](/docs/biblioteca/padroes).",
 "Transição que dispara evento de domínio: [Arcane.Dominio](/docs/biblioteca/dominio).",
 "Receita: [Máquina de estados](/docs/receitas/maquina-de-estados)."]),

# ══════════════════════════════════════════════════════════════
# 11. Estoque com DDD
# ══════════════════════════════════════════════════════════════
_projeto(
"estoque", "Controle de estoque",
"Entrada, saída, reserva e o estoque mínimo — com a invariante que nunca deixa o saldo negativo.",
"Estoque parece soma e subtração até a primeira venda de um item que não "
"existe. A distinção que resolve é entre **disponível** e **físico**: o que "
"está reservado para um pedido ainda está na prateleira, mas não pode ser "
"vendido de novo. E a invariante *“disponível nunca é negativo”* é cobrada "
"em toda operação, não em algumas.",
[["blueprint com invariante", "o saldo inconsistente é recusado na saída de cada método"],
 ["movimento como registro", "o saldo é a soma dos movimentos, e pode ser reconstruído"],
 ["reserva", "a diferença entre físico e disponível"],
 ["alerta de mínimo", "o ponto de pedido"]],
"""estoque/
  src/
    produto.df     saldo fisico, reservado, minimo
    movimento.df   entrada, saida, ajuste — imutaveis
    relatorio.df   o que repor
  tests/""",
_toml("estoque", "Controle de estoque"),
"""record Movimento:
    tipo: String
    qtd: Integer
    motivo: String

blueprint Item(sku, minimo):
    fisico := 0
    reservado := 0
    movimentos: Cluster := []

    invariant self.fisico bigger_eq 0
    invariant self.reservado bigger_eq 0 and self.reservado smaller_eq self.fisico

    action disponivel():
        yield self.fisico - self.reservado

    action entrar(qtd, motivo):
        given qtd smaller_eq 0:
            trigger "entrada precisa ser positiva"
        self.fisico += qtd
        self.movimentos.append(Movimento("entrada", qtd, motivo))

    action reservar(qtd):
        given qtd bigger self.disponivel():
            trigger $"{self.sku}: pedidos {qtd}, disponiveis {self.disponivel()}"
        self.reservado += qtd

    action baixar(qtd, motivo):
        self.reservado -= qtd
        self.fisico -= qtd
        self.movimentos.append(Movimento("saida", qtd, motivo))

    action repor():
        yield self.disponivel() smaller_eq self.minimo

    action reconstruir():
        yield sum(self.movimentos >> morph m: (m.qtd given m.tipo is "entrada" otherwise -m.qtd))

cafe := spawn Item("CAFE-500", 5)
cafe.entrar(12, "nota 1234")
cafe.reservar(8)
assert cafe.disponivel() is 4
assert cafe.repor()

monitor:
    cafe.reservar(5)
    assert no
handle Error as e:
    out e.message

cafe.baixar(8, "pedido 77")
assert cafe.fisico is 4
assert cafe.reconstruir() is cafe.fisico

// A invariante pega o que a regra esqueceu: baixar sem ter reservado.
monitor:
    cafe.baixar(3, "erro de operacao")
    assert no
handle Error as e:
    out "recusado pela invariante: " + e.type""",
"src/produto.df",
"""adopt ../src/produto as P

crucible "estoque":
    trial "o saldo reconstruido bate":
        i := spawn P.Item("X", 1)
        i.entrar(10, "a")
        i.reservar(4)
        i.baixar(4, "b")
        expect i.reconstruir() is i.fisico""",
[["`invariant` no blueprint", "o método que esqueceu uma conferência deixa o saldo negativo"],
 ["físico e reservado separados", "dois pedidos vendem a mesma última unidade"],
 ["os movimentos são records", "a auditoria mostra um saldo que ninguém sabe de onde veio"],
 ["`reconstruir` a partir dos movimentos", "o saldo corrompido não tem como ser conferido"]],
["As peças de DDD que cobram as distinções: [Arcane.Dominio](/docs/biblioteca/dominio).",
 "Dois operadores ao mesmo tempo: [Concorrência](/docs/tecnicas/concorrencia).",
 "Receita completa: [Inventário](/docs/receitas/inventario)."]),


# ══════════════════════════════════════════════════════════════
# 12. Bot de atendimento
# ══════════════════════════════════════════════════════════════
_projeto(
"bot-atendimento", "Bot de atendimento",
"Um bot de Telegram com menu, conversa em etapas e fallback — testado sem token e sem rede.",
"Um bot que só se testa conversando com ele no celular não tem teste nenhum. "
"`Tg.testar` injeta mensagens e lê o que o bot respondeu, e é isso que "
"permite ter uma suíte para um bot de atendimento com a mesma disciplina "
"de uma API.",
[["`Tg.app` / `mark @app.comando`", "os comandos, como decoradores"],
 ["`mark @app.texto`", "casar por expressão regular"],
 ["`V.estado` por conversa (`ctx.estado`)", "a conversa em etapas"],
 ["`Tg.testar`", "a sonda que finge ser o Telegram"]],
"""bot-suporte/
  src/
    bot.df         montar(token) — sem subir nada
    fluxos.df      a conversa de abrir chamado
  main.df          le o token do ambiente e sobe
  tests/
    bot_test.df""",
_toml("bot-suporte", "Bot de atendimento"),
"""adopt Arcane.Telegram as Tg

chamados := []

action montar(token):
    app := Tg.app(token)

    mark @app.comando("start")
    action comecar(ctx):
        ctx.responder("Oi! Mande /chamado para abrir um chamado, ou /status.")

    mark @app.comando("chamado")
    action abrir(ctx):
        ctx.estado["etapa"] := "assunto"
        ctx.responder("Qual e o assunto?")

    mark @app.comando("status")
    action status(ctx):
        ctx.responder($"{len(chamados)} chamado(s) aberto(s).")

    mark @app.qualquer()
    action conversa(ctx):
        match ctx.estado["etapa"] ?? "":
            point "assunto":
                ctx.estado["assunto"] := ctx.texto
                ctx.estado["etapa"] := "detalhe"
                ctx.responder("Descreva o problema em uma frase.")
            point "detalhe":
                chamados.append({"assunto": ctx.estado["assunto"], "detalhe": ctx.texto})
                ctx.estado["etapa"] := ""
                ctx.responder($"Chamado #{len(chamados)} aberto.")
            default:
                ctx.responder("Nao entendi. Mande /start.")

    yield app

t := Tg.testar(montar("123456:AAHexemplo"))
t.comando("start")
assert "/chamado" in t.ultima()

t.comando("chamado")
t.mandar("Impressora")
t.mandar("nao imprime frente e verso")
assert t.ultima() is "Chamado #1 aberto."
assert chamados[0]["assunto"] is "Impressora"

t.mandar("ola?")
assert "Nao entendi" in t.ultima()
t.comando("status")
assert t.ultima() is "1 chamado(s) aberto(s)."
out "bot verde\"""",
"src/bot.df",
"""adopt Arcane.Telegram as Tg
adopt ../src/bot as B

crucible "bot":
    trial "a conversa volta ao comeco depois de abrir":
        t := Tg.testar(B.montar("123456:AAHexemplo"))
        t.comando("chamado")
        t.mandar("a")
        t.mandar("b")
        t.mandar("c")
        expect "Nao entendi" in t.ultima()""",
[["`montar(token)` devolve o app, não sobe", "o teste sobe um bot que nunca termina"],
 ["o token vem do ambiente em `main.df`", "o token vai parar no repositório"],
 ["a etapa mora no estado **da conversa**", "duas pessoas conversando misturam os chamados"],
 ["`qualquer()` por último", "o fallback engole os comandos"]],
["Teclados e botões: [Telegram → teclados](/docs/telegram/teclados).",
 "Conversas longas: [Telegram → conversas](/docs/telegram/conversas).",
 "Publicar com webhook: [Telegram → publicar](/docs/telegram/publicar)."]),

# ══════════════════════════════════════════════════════════════
# 13. Painel de dados
# ══════════════════════════════════════════════════════════════
_projeto(
"painel", "Painel de dados",
"Um dashboard com filtro, métricas e tabela — testado com a sonda, sem navegador.",
"A Vitrine roda o programa **inteiro** de novo a cada interação, e o estado "
"da sessão sobrevive. É o modelo que dispensa callback — e por isso o painel "
"é um programa de cima para baixo que se testa como qualquer outro: a sonda "
"digita, clica e pergunta o que apareceu.",
[["`V.titulo` / `V.metrica`", "o topo do painel"],
 ["`V.escolha`", "o filtro que reexecuta a página"],
 ["`V.tabela`", "as linhas filtradas"],
 ["`V.testar`", "clicar e digitar sem navegador"]],
"""painel-vendas/
  src/
    dados.df       carregar (com V.cache em producao)
    painel.df      a pagina
  main.df          V.rodar(painel)
  tests/""",
_toml("painel-vendas", "Painel de vendas"),
"""adopt Arcane.Vitrine as V

VENDAS := [
    {"loja": "centro", "mes": "jul", "valor": 1200},
    {"loja": "centro", "mes": "ago", "valor": 1500},
    {"loja": "norte", "mes": "jul", "valor": 800},
    {"loja": "norte", "mes": "ago", "valor": 950}
]

action painel():
    V.titulo("Vendas por loja")
    loja := V.escolha("Loja", ["todas", "centro", "norte"])
    linhas := VENDAS given loja is "todas" otherwise (VENDAS >> sift v: v["loja"] is loja)
    total := sum(linhas >> morph v: v["valor"])
    V.metrica("Total", $"R$ {total}")
    V.metrica("Lançamentos", str(len(linhas)))
    V.tabela(linhas)

t := V.testar(painel)
assert not t.falhou()
assert "R$ 4450" in t.texto()

t.selecionar("Loja", "norte")
assert "R$ 1750" in t.texto()
assert t.existe("tabela")
out "painel verde\"""",
"src/painel.df",
"""adopt Arcane.Vitrine as V
adopt ../src/painel as P

crucible "painel":
    trial "o filtro muda o total":
        t := V.testar(P.painel)
        t.selecionar("Loja", "centro")
        expect "R$ 2700" in t.texto()""",
[["o painel é uma ação sem argumento", "não há como testá-lo sem subir o servidor"],
 ["o filtro é um valor, não um callback", "o estado se espalha por funções que ninguém chama em ordem"],
 ["`V.cache` na leitura dos dados (em produção)", "cada clique relê o banco inteiro"],
 ["a sonda pergunta o **texto**", "o teste quebra a cada mudança de CSS"]],
["Gráficos: [Vitrine → gráficos](/docs/vitrine/graficos).",
 "Layout em malha e painéis: [Vitrine → painel](/docs/vitrine/painel).",
 "Em produção, com sessão fora do processo: [Vitrine → produção](/docs/vitrine/producao)."]),

# ══════════════════════════════════════════════════════════════
# 14. Classificador
# ══════════════════════════════════════════════════════════════
_projeto(
"classificador", "Classificador de clientes",
"Treinar, medir no que o modelo não viu, e explicar o que ele aprendeu.",
"O erro mais caro em aprendizado de máquina não é o modelo ruim: é o modelo "
"medido nos mesmos dados em que treinou, que parece ótimo até a primeira "
"semana em produção. Este projeto separa antes de olhar, mede no conjunto "
"de teste e compara com a linha de base — *“sempre responder a classe mais "
"comum”* — que é o número que o modelo precisa bater.",
[["`ML.dividir`", "separar treino e teste **antes** de tudo"],
 ["`ML.floresta`", "o modelo"],
 ["`ML.avaliar`", "acurácia e F1 no que ele não viu"],
 ["a linha de base", "o número que ele precisa bater"]],
"""churn/
  src/
    dados.df       ler e limpar
    treinar.df     dividir, treinar, avaliar
    prever.df      carregar o modelo salvo e responder
  modelos/         o .json treinado (versionado com a data)
  tests/""",
_toml("churn", "Classificador de cancelamento"),
"""adopt Arcane.Cortex as ML

// Dados sinteticos: quem visita pouco e tem plano barato cancela mais.
clientes := []
cycle i from 1 to 240:
    visitas := i % 12
    plano := [29, 59, 99][i % 3]
    cancela := "sim" given visitas smaller 4 and plano is 29 otherwise "nao"
    clientes.append({"visitas": visitas, "plano": plano, "meses": i % 24, "cancela": cancela})

treino, teste := ML.dividir(clientes, 0.25, 42, "cancela")
modelo := ML.floresta(treino, "cancela", ["visitas", "plano", "meses"], 20)
r := ML.avaliar(modelo, teste)

// A linha de base: responder sempre a classe mais comum.
nao := len(teste >> sift c: c["cancela"] is "nao")
base := nao / len(teste)
out $"acuracia {round(r['acuracia'], 3)} contra linha de base {round(base, 3)}"

assert r["acuracia"] bigger base
assert len(treino) + len(teste) is len(clientes)""",
"src/treinar.df",
"""adopt ../src/treinar as T

crucible "modelo":
    trial "ganha da linha de base":
        expect T.r["acuracia"] bigger T.base

    trial "nenhum cliente fica de fora da divisao":
        expect len(T.treino) + len(T.teste) is len(T.clientes)""",
[["dividir **antes** de olhar", "a acurácia de 99% é memória, não aprendizado"],
 ["semente fixa (`42`)", "cada execução dá um número, e ninguém sabe se melhorou"],
 ["comparar com a linha de base", "90% de acerto num conjunto com 90% de *“não”* não aprendeu nada"],
 ["estratificar pela classe", "o teste sai sem nenhum *“sim”*, e o F1 não tem o que medir"]],
["Importância de cada variável e matriz de confusão: [ML](/docs/tecnicas/ml).",
 "Salvar e versionar o modelo: `ML.salvar` com a data no nome.",
 "Os açúcares `train` e `predict` da linguagem: [Arcane.Cortex](/docs/biblioteca/cortex)."]),

# ══════════════════════════════════════════════════════════════
# 15. Detector de intrusão em log
# ══════════════════════════════════════════════════════════════
_projeto(
"detector-de-intrusao", "Detector em log",
"Ler um log de acesso, correlacionar por IP e alertar força bruta com os eventos que a causaram.",
"Gravar log é quase inútil sozinho: ninguém lê dez milhões de linhas. O que "
"transforma log em segurança é a **regra** — cinco falhas do mesmo IP em um "
"minuto — e o alerta que traz os eventos, para que quem investiga não precise "
"voltar ao log para descobrir o que aconteceu.",
[["`D.motor`", "as regras e a correlação"],
 ["`por := \"ip\"`", "cinco falhas de cinco IPs **não** são força bruta"],
 ["janela deslizante", "4 falhas às 23h59 e 4 às 00h01 contam juntas"],
 ["o alerta com os eventos", "investigável sem voltar ao log"]],
"""vigia-log/
  src/
    ler.df         linha de log -> evento
    regras.df      o catalogo
    main.df        segue o arquivo e alerta
  tests/""",
_toml("vigia-log", "Detector de força bruta"),
"""adopt Arcane.Deteccao as D

LOG := \"\"\"203.0.113.7 POST /login 401
198.51.100.2 POST /login 200
203.0.113.7 POST /login 401
203.0.113.7 POST /login 401
192.0.2.10 POST /login 401
203.0.113.7 POST /login 401
203.0.113.7 POST /login 401\"\"\"

action evento_de(linha):
    ip, metodo, caminho, status := linha.split(" ")
    given caminho is "/login" and status is "401":
        yield {"nome": "login.falhou", "ip": ip}
    yield void

m := D.motor()
m.regra("forca-bruta", quando := "login.falhou", vezes := 5,
    janela := 60.0, gravidade := "alto", attack := "T1110", por := "ip")

alertas := []
cycle linha in LOG.lines():
    e := evento_de(linha)
    given e is not void:
        alertas := [...alertas, ...m.evento(e["nome"], {"ip": e["ip"]})]

cycle a in alertas:
    out $"{a['gravidade']}: {a['regra']} ({a['attack']}) com {len(a['eventos'])} eventos"

assert len(alertas) is 1
assert len(alertas[0]["eventos"]) is 5""",
"src/main.df",
"""adopt ../src/main as L

crucible "leitura":
    trial "login bem-sucedido nao e evento":
        expect L.evento_de("1.2.3.4 POST /login 200") is void""",
[["correlação **por IP**", "cinco usuários errando a senha viram um ataque"],
 ["a regra fala de **evento**, não de linha", "trocar o formato do log reescreve as regras"],
 ["o alerta carrega os eventos", "quem investiga volta ao log de 10 GB"],
 ["o código ATT&CK (`T1110`)", "o alerta não se liga ao catálogo que o time de segurança usa"]],
["Indicadores de comprometimento com prazo: [Detecção](/docs/seguranca/deteccao).",
 "Supressão, para mil alertas por minuto não virarem ruído: [Arcane.Deteccao](/docs/biblioteca/deteccao).",
 "Ler o log enquanto ele cresce: [Streams](/docs/tecnicas/streams)."]),

# ══════════════════════════════════════════════════════════════
# 16. Cofre de segredos
# ══════════════════════════════════════════════════════════════
_projeto(
"cofre-de-segredos", "Cofre de segredos",
"Cifrar por envelope, rotacionar a chave sem reescrever os dados, e recusar o dado adulterado.",
"Uma chave que nunca é trocada é uma chave que um dia vaza e continua "
"valendo. O motivo de ninguém trocar é sempre o mesmo: trocá-la tornaria "
"ilegível tudo que ela cifrou. O envelope resolve — os dados são cifrados "
"por uma chave própria, e só essa chave pequena é cifrada pela mestra.",
[["`Ch.cofre`", "as chaves com propósito e prazo"],
 ["`envelopar` / `desenvelopar`", "DEK por dado, KEK mestra"],
 ["`rotacionar`", "a chave nova, mantendo as antigas"],
 ["`recifrar`", "trocar a mestra sem tocar nos dados"]],
"""cofre/
  src/
    cofre.df       abrir, guardar, ler
    rotacao.df     o job mensal
  tests/""",
_toml("cofre", "Cofre de segredos"),
"""adopt Arcane.Chaves as Ch
adopt Arcane.Bytes as Bytes

cofre := Ch.cofre()
cofre.gerar("mestra", proposito := "cifrar")

segredos := {}
action guardar(nome, valor):
    segredos[nome] := cofre.envelopar(valor, "mestra")

// O envelope guarda BYTES: um segredo pode ser um certificado binario.
// Quem sabe que ali mora texto converte na saida.
action ler(nome):
    yield Bytes.para_texto(cofre.desenvelopar(segredos[nome]))

guardar("banco", "postgres://app:s3nh4@db/loja")
guardar("stripe", "chave-de-teste-ficticia")

// A rotacao: a chave nova passa a cifrar, a antiga continua abrindo.
nova := cofre.rotacionar("mestra", "cifrar")
assert ler("banco") is "postgres://app:s3nh4@db/loja"

// E o job de rotacao recifra so as DEKs — os dados ficam onde estao.
cycle nome in segredos.keys():
    segredos[nome] := cofre.recifrar(segredos[nome], "mestra")
assert segredos["banco"]["kid"] is nova.kid
out "rotacionado; o passado continua legivel\"""",
"src/cofre.df",
"""adopt ../src/cofre as C

crucible "cofre":
    trial "o que se guarda volta igual":
        C.guardar("x", "valor")
        expect C.ler("x") is "valor\"""",
[["envelope (DEK/KEK)", "trocar a mestra é reescrever cada segredo"],
 ["o `kid` dentro do envelope", "com cinco chaves, não se sabe qual abre o quê"],
 ["a chave tem **propósito**", "a chave que assina token também decifra backup"],
 ["a integridade é barulhenta", "o dado adulterado abre como `void` e o programa grava nada onde havia um valor"]],
["O ciclo de vida inteiro: [Criptografia e chaves](/docs/seguranca/criptografia).",
 "Onde a mestra mora em produção: fora do processo — KMS ou variável de ambiente.",
 "A referência: [Arcane.Chaves](/docs/biblioteca/chaves)."]),

# ══════════════════════════════════════════════════════════════
# 17. Planilha reativa
# ══════════════════════════════════════════════════════════════
_projeto(
"planilha-reativa", "Planilha reativa",
"Células que dependem de células — recalculadas sozinhas, só quando alguém lê, e sem o valor que nunca existiu.",
"Uma planilha é o programa reativo que todo mundo já usou: mudar uma célula "
"atualiza as que dependem dela. O que torna isso difícil é o **losango** — "
"quando `C` depende de `A` e de `B`, e `B` também depende de `A`, uma "
"propagação ingênua mostra por um instante um valor que nunca foi verdade.",
[["`R.sinal`", "a célula de entrada"],
 ["`R.derivado`", "a célula com fórmula — preguiçosa e memorizada"],
 ["`R.efeito`", "quem desenha a tela"],
 ["a onda de duas fases", "o losango sem valor intermediário"]],
"""orcamento/
  src/
    celulas.df     as entradas e as formulas
    tela.df        o efeito que imprime
  tests/""",
_toml("orcamento", "Orçamento reativo"),
"""adopt Arcane.Reativo as R

steady receita := R.sinal(10000)
steady custo_fixo := R.sinal(4000)
steady margem := R.sinal(0.2)

contas := {"n": 0}
action calcular_variavel():
    contas["n"] += 1
    yield receita.ler() * 0.3

steady custo_variavel := R.derivado(calcular_variavel)
steady lucro := R.derivado(lambda => receita.ler() - custo_fixo.ler() - custo_variavel.ler())
steady meta := R.derivado(lambda => receita.ler() * margem.ler())

vistos := []
steady tela := R.efeito(lambda => vistos.append(lucro.ler()))

assert lucro.ler() is 3000.0
assert contas["n"] is 1

// 'lucro' le 'receita' direto E via 'custo_variavel': o losango.
receita.escrever(20000)
assert lucro.ler() is 10000.0

// O efeito viu 3000 e depois 10000 — nunca o intermediario de 13000
// (20000 - 4000 - o custo velho de 3000).
assert vistos is [3000.0, 10000.0]
assert meta.ler() is 4000.0
out vistos""",
"src/celulas.df",
"""adopt ../src/celulas as C

crucible "planilha":
    trial "ler duas vezes nao recalcula":
        antes := C.contas["n"]
        C.lucro.ler()
        C.lucro.ler()
        expect C.contas["n"] is antes""",
[["o derivado é **preguiçoso**", "cada leitura recalcula a planilha inteira"],
 ["propagação em duas fases", "a tela pisca um lucro de 13 mil que nunca existiu"],
 ["o efeito roda uma vez por onda", "a tela redesenha duas vezes por mudança"],
 ["dependências descobertas na execução", "a lista de dependências escrita à mão envelhece na primeira fórmula nova"]],
["A explicação do losango, medida: [Arcane.Reativo](/docs/biblioteca/reativo).",
 "Agrupar três escritas numa notificação: `R.lote`.",
 "Fluxos (não valores): `R.observavel`."]),

# ══════════════════════════════════════════════════════════════
# 18. Rotas num grafo
# ══════════════════════════════════════════════════════════════
_projeto(
"rotas", "Planejador de rotas",
"Menor caminho com Dijkstra, o caminho reconstruído e o bairro inalcançável tratado.",
"Grafo é o modelo de tudo que se conecta: ruas, dependências, redes. O "
"planejador de rotas é o exemplo clássico porque tem as três armadilhas de "
"todo algoritmo de grafo — o nó sem saída, o caminho que precisa ser "
"reconstruído e não só medido, e o peso que não pode ser negativo.",
[["vault de listas", "o grafo como lista de adjacência"],
 ["Dijkstra", "menor distância a partir de uma origem"],
 ["`anterior`", "reconstruir o caminho, e não só o custo"],
 ["`void`", "o destino que não se alcança"]],
"""rotas/
  src/
    grafo.df       ligar, vizinhos
    dijkstra.df    menor_caminho
  tests/""",
_toml("rotas", "Planejador de rotas"),
"""MAPA := {
    "centro": [["norte", 4], ["sul", 2]],
    "sul": [["norte", 1], ["leste", 7]],
    "norte": [["leste", 3]],
    "leste": [],
    "ilha": []
}

action menor_caminho(grafo, origem, destino):
    dist := {}
    anterior := {}
    visitados := []
    cycle n in grafo.keys():
        dist[n] := INF
    dist[origem] := 0
    persist yes:
        atual := void
        cycle n in grafo.keys():
            given n not in visitados and dist[n] isnt INF:
                given atual is void or dist[n] smaller dist[atual]:
                    atual := n
        given atual is void or atual is destino:
            halt
        visitados.append(atual)
        cycle aresta in grafo[atual]:
            vizinho, peso := aresta
            given peso smaller 0:
                trigger "Dijkstra nao aceita peso negativo"
            given dist[atual] + peso smaller dist[vizinho]:
                dist[vizinho] := dist[atual] + peso
                anterior[vizinho] := atual
    given dist[destino] is INF:
        yield void
    caminho := [destino]
    persist caminho[0] is not origem:
        caminho := [anterior[caminho[0]], ...caminho]
    yield {"custo": dist[destino], "caminho": caminho}

r := menor_caminho(MAPA, "centro", "leste")
out r
assert r["custo"] is 6
assert r["caminho"] is ["centro", "sul", "norte", "leste"]
assert menor_caminho(MAPA, "centro", "ilha") is void""",
"src/dijkstra.df",
"""adopt ../src/dijkstra as D

crucible "rotas":
    trial "a origem chega nela mesma com custo zero":
        expect D.menor_caminho(D.MAPA, "sul", "sul")["custo"] is 0""",
[["guardar `anterior`", "o programa diz *“6 km”* e não diz por onde"],
 ["`void` para o inalcançável", "o custo sai `INF` e alguém soma isso a um preço"],
 ["recusar peso negativo", "Dijkstra devolve um caminho errado com toda a confiança"],
 ["o grafo é dado", "trocar o mapa exige mexer no algoritmo"]],
["Com milhares de nós, troque a busca linear do menor por uma fila de prioridade.",
 "Peso negativo exige Bellman-Ford.",
 "Meça a classe: `dataforge big-o src/dijkstra.df`."]),

# ══════════════════════════════════════════════════════════════
# 19. Biblioteca publicável
# ══════════════════════════════════════════════════════════════
_projeto(
"biblioteca", "Biblioteca publicável",
"Validador de placas de veículo — com `relay`, erro que diz o motivo e o pacote pronto para o registro.",
"Uma biblioteca é um projeto sem `main`: quem roda é o código de outra "
"pessoa. Isso muda três coisas — o que é público precisa ser declarado, o erro "
"precisa servir a quem não leu o seu código, e a versão passa a ser uma "
"promessa.",
[["`relay`", "a superfície pública, e só ela"],
 ["o vault de resultado", "`{ok, motivo}` em vez de `no`"],
 ["`dataforge pack`", "o tarball reprodutível"],
 ["o teste pelo **nome** do pacote", "`adopt placa`, como o usuário faria"]],
"""placa/
  forge.toml
  src/
    main.df        relay validar, formatar, tipo
  tests/
    placa_test.df  adopt placa  (pelo nome!)
  README.md""",
"""[project]
name = "placa"
version = "1.0.0"
description = "Valida e formata placas brasileiras (antiga e Mercosul)"
entry = "src/main.df"
license = "MIT"
dataforge = ">=1.1"

[dependencies]""",
"""// Antiga: ABC-1234. Mercosul: ABC1D23.
steady ANTIGA := "^[A-Z]{3}-?[0-9]{4}$"
steady MERCOSUL := "^[A-Z]{3}[0-9][A-Z][0-9]{2}$"

action _limpar(texto):
    yield texto.trim().upper().replace(" ", "")

action tipo(texto):
    t := _limpar(texto)
    given regex_test(MERCOSUL, t):
        yield "mercosul"
    given regex_test(ANTIGA, t):
        yield "antiga"
    yield void

action validar(texto):
    given texto is void or _limpar(texto) is "":
        yield {"ok": no, "motivo": "placa vazia"}
    t := _limpar(texto)
    given len(t.replace("-", "")) is not 7:
        yield {"ok": no, "motivo": $"tem {len(t.replace('-', ''))} caracteres, e uma placa tem 7"}
    given tipo(t) is void:
        yield {"ok": no, "motivo": "nao e nem o formato antigo (ABC-1234) nem o Mercosul (ABC1D23)"}
    yield {"ok": yes, "motivo": "", "tipo": tipo(t)}

action formatar(texto):
    t := _limpar(texto).replace("-", "")
    given tipo(t) is "antiga":
        yield t[0:3] + "-" + t[3:]
    yield t

relay validar, formatar, tipo

assert validar("abc1d23")["tipo"] is "mercosul"
assert formatar("abc1234") is "ABC-1234"
assert "7" in validar("AB123")["motivo"]
assert not validar("ABC12D3")["ok"]
out validar("ABC12D3")["motivo"]""",
"src/main.df",
"""adopt placa as P

crucible "placa":
    trial "o motivo diz o que esta errado":
        expect P.validar("")["motivo"] is "placa vazia"

    trial "_limpar nao e publico":
        expect(lambda => P._limpar("x")).to_raise()""",
[["`relay` explícito", "o `_limpar` interno vira contrato e nunca mais pode mudar"],
 ["o motivo em vez de `no`", "o formulário de quem usa diz *“placa inválida”* e mais nada"],
 ["o teste pelo nome do pacote", "a biblioteca funciona no repositório e quebra instalada"],
 ["`license` no manifesto", "a empresa de quem instala não pode usar"]],
["O ciclo inteiro de uma biblioteca: [Escrever uma biblioteca](/docs/bibliotecas).",
 "Publicar no registro: [Publicar](/docs/bibliotecas/publicar).",
 "O desenho da API: [Desenhar a API pública](/docs/bibliotecas/api)."],
"tests/placa_test.df"),

# ══════════════════════════════════════════════════════════════
# 20. Saga de pedido
# ══════════════════════════════════════════════════════════════
_projeto(
"saga", "Pedido distribuído",
"Reservar, cobrar e despachar em três serviços — e desfazer em ordem inversa quando um falha.",
"Não existe transação que atravesse a rede: `BEGIN` no serviço de estoque não "
"alcança o de cobrança. A resposta é a saga — cada passo declara como se "
"desfaz, e uma falha no meio desfaz, **em ordem inversa**, o que já aconteceu.",
[["`Malha.saga`", "os passos e as compensações"],
 ["o estado da saga", "o que cada passo produziu"],
 ["`conferir()`", "o passo que escreve sem compensação, antes de rodar"],
 ["`orfas`", "a compensação que falhou, para um humano"]],
"""pedidos-distribuidos/
  src/
    estoque.df     reservar / liberar
    cobranca.df    cobrar / estornar
    envio.df       despachar
    saga.df        liga os tres
  tests/""",
_toml("pedidos-distribuidos", "Saga de pedido"),
"""adopt Arcane.Malha as Malha

estoque := {"cafe": 3}
cobrado := []
log := []

action reservar(estado, chave):
    given estoque["cafe"] smaller estado["qtd"]:
        trigger "sem estoque"
    estoque["cafe"] -= estado["qtd"]
    log.append("reservou")
    yield {"reserva": "R-1"}

action liberar(estado, chave):
    estoque["cafe"] += estado["qtd"]
    log.append("liberou")

action cobrar(estado, chave):
    given estado["cartao"] is "recusado":
        trigger "cartao recusado"
    cobrado.append(chave)
    log.append("cobrou")
    yield {"cobranca": "C-1"}

action estornar(estado, chave):
    cobrado.remove(chave)
    log.append("estornou")

action despachar(estado, chave):
    given estado["cep"] is "00000-000":
        trigger "cep nao atendido"
    log.append("despachou")

action saga_de_pedido():
    s := Malha.saga("pedido")
    s.passo("reservar", reservar, liberar)
    s.passo("cobrar", cobrar, estornar)
    s.passo("despachar", despachar, void, no)
    yield s

s := saga_de_pedido()
assert s.conferir() is []

r := s.executar({"qtd": 2, "cartao": "ok", "cep": "00000-000"})
out log
assert not r["ok"]
assert r["falhou_em"] is "despachar"
// Ordem INVERSA: estorna antes de liberar.
assert log is ["reservou", "cobrou", "estornou", "liberou"]
assert estoque["cafe"] is 3 and len(cobrado) is 0""",
"src/saga.df",
"""adopt ../src/saga as S

crucible "saga":
    trial "o passo que falhou nao e compensado":
        r := S.saga_de_pedido().executar({"qtd": 1, "cartao": "recusado", "cep": "1"})
        expect r["desfeitos"] is ["reservar"]""",
[["compensar em ordem inversa", "o cliente fica sem dinheiro e sem produto por uma janela"],
 ["o passo que falhou não é desfeito", "o estorno de uma cobrança que não aconteceu"],
 ["a chave de idempotência por passo", "repetir a saga depois de uma queda cobra duas vezes"],
 ["`orfas` não é engolido", "um estorno que falhou deixa o sistema inconsistente, e ninguém sabe"]],
["Chamadas HTTP de verdade com disjuntor e retentativa: [Microsserviços](/docs/tecnicas/microservicos).",
 "A saga **não** dá isolamento — entre reservar e cobrar, outro pedido vê o estoque reservado.",
 "A referência: [Arcane.Malha](/docs/biblioteca/malha)."]),

# ══════════════════════════════════════════════════════════════
# 21. Agendador com expressão cron
# ══════════════════════════════════════════════════════════════
_projeto(
"agendador", "Agendador cron",
"Ler uma expressão cron, dizer quando ela roda — e recusar a que nunca roda.",
"Cron é uma linguagem pequena que quase todo sistema usa e quase ninguém "
"lê direito: `*/15 9-18 * * 1-5` é *“a cada 15 minutos, em horário "
"comercial, nos dias úteis”*. Este projeto escreve o parser, expande cada "
"campo para os valores concretos e responde as próximas execuções.",
[["parser de campo", "`*`, `*/n`, `a-b`, `a,b,c`"],
 ["faixas por campo", "o minuto vai de 0 a 59; o dia da semana, de 0 a 6"],
 ["mensagem com o campo", "*“hora 25 fora de 0-23”*"],
 ["as próximas execuções", "o que o usuário quer ver antes de salvar"]],
"""agendador/
  src/
    cron.df        ler, casa, proximas
    tarefas.df     o catalogo de jobs
  tests/""",
_toml("agendador", "Agendador com cron"),
"""steady CAMPOS := [["minuto", 0, 59], ["hora", 0, 23], ["dia", 1, 31], ["mes", 1, 12], ["semana", 0, 6]]

action expandir(texto, nome, menor, maior):
    valores := []
    cycle parte in texto.split(","):
        passo := 1
        faixa := parte
        given "/" in parte:
            faixa, p := parte.split("/")
            passo := int(p)
            given passo smaller_eq 0:
                trigger $"{nome}: o passo precisa ser positivo"
        given faixa is "*":
            a := menor
            b := maior
        orif "-" in faixa:
            ia, ib := faixa.split("-")
            a := int(ia)
            b := int(ib)
        otherwise:
            a := int(faixa)
            b := a
        given a smaller menor or b bigger maior or a bigger b:
            trigger $"{nome} {faixa} fora de {menor}-{maior}"
        cycle v from a to b step passo:
            valores.append(v)
    yield sorted(unique(valores))

action ler(expressao):
    partes := expressao.trim().split(" ") >> sift p: p is not ""
    given len(partes) is not 5:
        trigger $"uma expressao cron tem 5 campos, esta tem {len(partes)}"
    regra := {}
    cycle i in range(0, 5):
        c := CAMPOS[i]
        regra[c[0]] := expandir(partes[i], c[0], c[1], c[2])
    yield regra

action casa(regra, m, h, dia, mes, semana):
    yield m in regra["minuto"] and h in regra["hora"] and dia in regra["dia"] and mes in regra["mes"] and semana in regra["semana"]

r := ler("*/15 9-18 * * 1-5")
assert r["minuto"] is [0, 15, 30, 45]
assert len(r["hora"]) is 10
assert casa(r, 30, 10, 21, 9, 1)
assert not casa(r, 30, 10, 20, 9, 0)

monitor:
    ler("0 25 * * *")
    assert no
handle Error as e:
    out e.message
    assert "hora 25" in e.message""",
"src/cron.df",
"""adopt ../src/cron as C

crucible "cron":
    trial "lista com virgula":
        expect C.ler("0,30 * * * *")["minuto"] is [0, 30]

    trial "quatro campos e recusado":
        expect(lambda => C.ler("* * * *")).to_raise()""",
[["expandir para os valores concretos", "cada pergunta *“casa?”* reinterpreta o texto"],
 ["a faixa de cada campo", "`0 25 * * *` é aceito e nunca roda"],
 ["a mensagem nomeia o campo", "*“expressão inválida”*, e a pessoa conta os espaços"],
 ["`unique` + `sorted`", "`1,1,2` roda duas vezes no minuto 1"]],
["Rodar no horário, numa thread só: [Arcane.Laco](/docs/biblioteca/laco).",
 "No banco, com `pg_cron`: [Em produção](/docs/banco-de-dados/producao).",
 "O dia do mês **e** da semana juntos é um *ou* no cron clássico — decida e documente."]),

# ══════════════════════════════════════════════════════════════
# 22. Gerador de site estático
# ══════════════════════════════════════════════════════════════
_projeto(
"site-estatico", "Gerador de site estático",
"Markdown para HTML com modelo, índice gerado e o texto sempre escapado.",
"Um gerador de site é um compilador pequeno: a entrada são arquivos de "
"texto, a saída são páginas, e no meio há uma árvore. As duas decisões que "
"importam são escapar **tudo** que vem do texto antes de montar HTML, e "
"gerar o índice dos mesmos dados que geram as páginas — uma segunda lista "
"sempre diverge.",
[["`lines` + `match`", "cabeçalho, lista e parágrafo"],
 ["escape de HTML", "o `<` do texto não vira tag"],
 ["modelo com `$\"…\"`", "a moldura comum de toda página"],
 ["o índice dos mesmos dados", "nenhuma página fica fora do menu"]],
"""blog/
  conteudo/
    *.md
  modelos/
    pagina.html
  src/
    markdown.df    texto -> html
    gerar.df       le a pasta, escreve saida/
  saida/           (gerado — nao versione)""",
_toml("blog", "Gerador de site"),
"""action escapar(t):
    yield t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\\"", "&quot;")

action em_linha(t):
    t := escapar(t)
    yield regex_sub("\\\\*\\\\*(.+?)\\\\*\\\\*", "<strong>\\\\1</strong>", t)

action html_de(markdown):
    saida := []
    em_lista := no
    cycle linha in markdown.lines():
        l := linha.trim()
        given em_lista and not l.startswith("- "):
            saida.append("</ul>")
            em_lista := no
        given l is "":
            skip
        orif l.startswith("## "):
            saida.append($"<h2>{em_linha(l[3:])}</h2>")
        orif l.startswith("# "):
            saida.append($"<h1>{em_linha(l[2:])}</h1>")
        orif l.startswith("- "):
            given not em_lista:
                saida.append("<ul>")
                em_lista := yes
            saida.append($"<li>{em_linha(l[2:])}</li>")
        otherwise:
            saida.append($"<p>{em_linha(l)}</p>")
    given em_lista:
        saida.append("</ul>")
    yield "\\n".join(saida)

action pagina(titulo, corpo, menu):
    yield $"<!doctype html><title>{escapar(titulo)}</title><nav>{menu}</nav><main>{corpo}</main>"

POSTS := [
    {"slug": "ola", "titulo": "Ola", "texto": "# Ola\\n\\nPrimeiro **post**."},
    {"slug": "lista", "titulo": "Uma lista", "texto": "# Lista\\n\\n- um\\n- dois <script>"}
]

menu := "".join(POSTS >> morph p: $"<a href=\\"/{p['slug']}.html\\">{escapar(p['titulo'])}</a>")
site := {}
cycle p in POSTS:
    site[p["slug"] + ".html"] := pagina(p["titulo"], html_de(p["texto"]), menu)

assert "<strong>post</strong>" in site["ola.html"]
assert "<li>dois &lt;script&gt;</li>" in site["lista.html"]
assert "<script>" not in site["lista.html"]
assert site["ola.html"].count("<a href") is len(POSTS)
out site["lista.html"]""",
"src/markdown.df",
"""adopt ../src/markdown as M

crucible "markdown":
    trial "a lista fecha no fim do arquivo":
        expect M.html_de("- a") is "<ul>\\n<li>a</li>\\n</ul>\"""",
[["escapar **antes** de montar", "um post com `<script>` roda no navegador de quem lê"],
 ["o menu sai da lista de posts", "o post novo existe e não aparece no site"],
 ["a lista fecha quando o bloco termina", "o resto da página fica dentro de um `<ul>`"],
 ["`saida/` fora do git", "cada build gera um diff de milhares de linhas"]],
["O escape por destino (atributo, URL, CSS): [Entrada e saída](/docs/seguranca/entrada).",
 "Servir a pasta gerada com o Kiln: [Estáticos](/docs/kiln/estaticos).",
 "Recompilar ao salvar: [`dataforge watch`](/docs/cli/watch)."]),

]


# ── O índice: sai da MESMA lista ────────────────────────────────
#
# A tabela de /docs/projetos era escrita à mão, e uma segunda lista
# divergiria no primeiro tipo novo. Aqui ela é derivada de TIPOS.

GRUPOS = [
    ("Terminal e ferramentas", ["cli-notas", "jogo", "interpretador", "agendador", "site-estatico"]),
    ("Web e serviços", ["api-rest", "autenticacao", "bot-atendimento", "painel", "saga"]),
    ("Dados", ["etl", "classificador", "planilha-reativa", "rotas"]),
    ("Negócio", ["motor-de-regras", "folha-de-pagamento", "maquina-de-estados", "estoque", "fila-de-trabalho"]),
    ("Segurança", ["detector-de-intrusao", "cofre-de-segredos"]),
    ("Ecossistema", ["biblioteca"]),
]

_POR_SLUG = {t["href"].rsplit("/", 1)[-1]: t for t in TIPOS}


def _indice():
    blocos = [
        {"p": "Dois níveis de exemplo. Os **projetos completos** moram em "
              "`projetos/` no repositório, com `forge.toml`, dependências "
              "reais e testes próprios. Os **vinte e dois tipos** abaixo "
              "mostram o que muda de um tipo de programa para outro — e cada "
              "um é conferido a cada build: o manifesto, o núcleo e o teste "
              "são escritos numa pasta, e `dataforge test` precisa passar."},
        {"code": "cd projetos/gestor-tarefas\ndataforge install\n"
                 "dataforge test tests/\ndataforge run src/main.df -- listar",
         "lang": "bash"},
        {"h2": "Projetos completos"},
        {"table": {"head": ["Projeto", "O que faz", "Bibliotecas"], "rows": [
            ["[Gestor de tarefas](/docs/projetos/gestor-tarefas)", "CLI com prazos e persistência", "6"],
            ["[Análise de vendas](/docs/projetos/analise-vendas)", "CSV → relatório estatístico", "6"],
            ["[API de links](/docs/projetos/api-links)", "Encurtador com servidor HTTP", "6"]]}},
        {"h2": "Os vinte e dois tipos"},
        {"p": "Cada página traz a estrutura de pastas, o `forge.toml`, um "
              "núcleo que roda sozinho, o teste, a tabela de decisões — *o "
              "que quebra sem cada uma* — e para onde ir depois."},
    ]
    vistos = set()
    for grupo, slugs in GRUPOS:
        blocos.append({"h3": grupo})
        linhas = []
        for sl in slugs:
            t = _POR_SLUG[sl]
            vistos.add(sl)
            linhas.append([f"[{t['title']}]({t['href']})", t["description"]])
        blocos.append({"table": {"head": ["Tipo", "O que ele mostra"], "rows": linhas}})
    faltando = set(_POR_SLUG) - vistos
    assert not faltando, f"tipo fora de todo grupo: {sorted(faltando)}"
    blocos += [
        {"h2": "Começar um projeto"},
        {"p": "`dataforge new` cria o esqueleto de dez modelos — e todo "
              "projeto criado passa nos próprios testes antes de você mexer "
              "em qualquer coisa."},
        {"code": "dataforge new loja --modelo=api\ncd loja\ndataforge test tests/",
         "lang": "bash"},
        {"table": {"head": ["Modelo", "Parte de"], "rows": [
            ["`cli`", "[CLI de anotações](/docs/projetos/cli-notas)"],
            ["`api`", "[API REST com CRUD](/docs/projetos/api-rest)"],
            ["`data`", "[Pipeline ETL](/docs/projetos/etl)"],
            ["`painel`", "[Painel de dados](/docs/projetos/painel)"],
            ["`bot`", "[Bot de atendimento](/docs/projetos/bot-atendimento)"],
            ["`lib`", "[Biblioteca publicável](/docs/projetos/biblioteca)"]]}},
        {"callout": {"tipo": "dica", "titulo": "A regra de todos",
                     "texto": "A regra de negócio nunca conhece o transporte. "
                              "A rota, o comando e a mensagem do bot só "
                              "traduzem — o que decide mora numa ação que se "
                              "testa em milissegundos, sem socket, sem terminal "
                              "e sem token."}},
    ]
    return {"href": "/docs/projetos", "title": "Projetos",
            "description": "Três projetos completos e vinte e dois tipos de "
                           "projeto, cada um montado e testado a cada build.",
            "blocos": blocos}


PAGINAS = [_indice()] + TIPOS
