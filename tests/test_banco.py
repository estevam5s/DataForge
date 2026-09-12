"""Arcane.Database — o que um CRUD de verdade exige.

O módulo tinha o básico: conectar, consultar, inserir, um construtor de
consulta e migrações. Faltava o que separa um exemplo de um sistema:

| Sem isso | O que acontece |
|---|---|
| transação com desfazer | a venda é gravada e o estoque não baixa |
| `upsert` | o catálogo que chega por CSV toda noite duplica |
| `increment` no banco | duas vendas ao mesmo tempo perdem uma baixa |
| paginação com total | a tela não sabe desenhar a paginação |
| busca textual | `LIKE %termo%` varre a tabela inteira |
| `explain` | ninguém descobre o índice que falta |

Três bugs nasceram e morreram escrevendo estes testes, todos do tipo que
não dá erro:

1. `"livr*"` — o `*` dentro das aspas é literal; a sintaxe de prefixo do
   FTS5 é `"livr"*`. A busca devolvia lista vazia, calada.
2. `apelido MATCH ?` é recusado pelo SQLite, e o nome da tabela junto de
   um apelido devolvia vazio — também sem erro.
3. `stats` contava as quatro tabelas-sombra de cada índice FTS: um banco
   de duas tabelas parecia ter dez.
"""

import os
import sys

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module


@pytest.fixture
def B():
    return get_module("Arcane.Database")


@pytest.fixture
def db(B):
    banco = B["memory"]()
    B["create_table"](banco, "produtos", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "sku": "TEXT NOT NULL UNIQUE",
        "nome": "TEXT NOT NULL",
        "preco": "REAL NOT NULL DEFAULT 0",
        "estoque": "INTEGER NOT NULL DEFAULT 0",
    })
    B["create_table"](banco, "vendas", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "produto_id": "INTEGER NOT NULL REFERENCES produtos(id)",
        "quantidade": "INTEGER NOT NULL",
        "valor": "REAL NOT NULL",
        "vendedor": "TEXT NOT NULL",
    })
    return banco


def _produto(B, db, sku, nome, preco=10.0, estoque=5):
    return B["upsert"](db, "produtos", {
        "sku": sku, "nome": nome, "preco": preco, "estoque": estoque}, "sku")


# ═══════════════════════════════════════════════════════════
#  Transação
# ═══════════════════════════════════════════════════════════

def test_a_transacao_desfaz_tudo_no_erro(B, db):
    """É a peça que falta num PDV: gravar a venda, baixar o estoque e
    lançar o pagamento precisam valer juntos."""
    _produto(B, db, "L-1", "Duna", 79.9, 3)

    def vender_demais():
        B["insert"](db, "vendas", {"produto_id": 1, "quantidade": 99,
                                   "valor": 999.0, "vendedor": "ana"})
        B["increment"](db, "produtos", "estoque", -99, {"id": 1})
        raise ValueError("estoque insuficiente")

    with pytest.raises(ValueError):
        B["transacao"](db, vender_demais)

    assert B["count"](db, "vendas") == 0
    assert B["query_one"](db, "SELECT estoque FROM produtos")["estoque"] == 3


def test_a_transacao_devolve_o_que_a_acao_devolveu(B, db):
    assert B["transacao"](db, lambda: 42) == 42


def test_a_transacao_desfaz_tambem_no_sinal_de_controle(B, db):
    """`halt` e `yield` derivam de `BaseException`: deixar commitado o
    que já foi escrito seria a pior das duas opções."""
    _produto(B, db, "L-1", "Duna")

    class Sinal(BaseException):
        pass

    def com_sinal():
        B["insert"](db, "vendas", {"produto_id": 1, "quantidade": 1,
                                   "valor": 1.0, "vendedor": "x"})
        raise Sinal()

    with pytest.raises(Sinal):
        B["transacao"](db, com_sinal)
    assert B["count"](db, "vendas") == 0


def test_o_savepoint_desfaz_so_a_parte_de_dentro(B, db):
    """Um item sem estoque não deve desfazer a venda inteira."""
    _produto(B, db, "L-1", "Duna")

    def venda():
        B["insert"](db, "vendas", {"produto_id": 1, "quantidade": 1,
                                   "valor": 10.0, "vendedor": "ana"})

        def item_ruim():
            B["insert"](db, "vendas", {"produto_id": 1, "quantidade": 2,
                                       "valor": 20.0, "vendedor": "ana"})
            raise ValueError("sem estoque")

        try:
            B["savepoint"](db, "item", item_ruim)
        except ValueError:
            pass
        return "ok"

    assert B["transacao"](db, venda) == "ok"
    assert B["count"](db, "vendas") == 1


# ═══════════════════════════════════════════════════════════
#  Escrita idempotente
# ═══════════════════════════════════════════════════════════

def test_o_upsert_nao_duplica_e_diz_o_que_fez(B, db):
    assert _produto(B, db, "L-1", "O Hobbit", 49.9) == "inserido"
    assert _produto(B, db, "L-1", "O Hobbit (2ª ed)", 54.9) == "atualizado"
    assert B["count"](db, "produtos") == 1
    assert B["query_one"](db, "SELECT nome FROM produtos")["nome"] == \
        "O Hobbit (2ª ed)"


def test_o_upsert_many_conta_os_dois_casos(B, db):
    _produto(B, db, "L-1", "Duna")
    resultado = B["upsert_many"](db, "produtos", [
        {"sku": "L-1", "nome": "Duna", "preco": 1.0, "estoque": 1},
        {"sku": "L-2", "nome": "Neuromancer", "preco": 2.0, "estoque": 2},
        {"sku": "L-3", "nome": "Solaris", "preco": 3.0, "estoque": 3},
    ], "sku")
    assert resultado == {"inseridos": 2, "atualizados": 1}


def test_o_upsert_many_e_uma_transacao_so(B, db):
    """Mil produtos, um por um, são mil sincronizações de disco."""
    resultado = B["upsert_many"](db, "produtos", [
        {"sku": f"P-{i}", "nome": f"Item {i}", "preco": 1.0, "estoque": 1}
        for i in range(200)], "sku")
    assert resultado["inseridos"] == 200


def test_insert_or_ignore_devolve_zero_quando_ja_existe(B, db):
    primeiro = B["insert_or_ignore"](db, "produtos",
                                     {"sku": "L-1", "nome": "Duna"})
    assert primeiro > 0
    assert B["insert_or_ignore"](db, "produtos",
                                 {"sku": "L-1", "nome": "Outro"}) == 0


def test_o_increment_soma_no_banco_e_nao_na_memoria(B, db):
    """Ler, somar e escrever de volta perde atualizações quando duas
    vendas acontecem ao mesmo tempo — e o estoque fica errado sem
    nenhum erro aparecer."""
    _produto(B, db, "L-1", "Duna", estoque=10)
    assert B["increment"](db, "produtos", "estoque", -3, {"sku": "L-1"}) == 1
    assert B["query_one"](db, "SELECT estoque FROM produtos")["estoque"] == 7


def test_o_increment_em_paralelo_nao_perde_baixa(B, db):
    import threading

    _produto(B, db, "L-1", "Duna", estoque=0)

    def bater():
        for _ in range(200):
            B["increment"](db, "produtos", "estoque", 1, {"sku": "L-1"})

    linhas = [threading.Thread(target=bater) for _ in range(4)]
    for t in linhas:
        t.start()
    for t in linhas:
        t.join()
    assert B["query_one"](db, "SELECT estoque FROM produtos")["estoque"] == 800


# ═══════════════════════════════════════════════════════════
#  Paginação e relatório
# ═══════════════════════════════════════════════════════════

def test_a_paginacao_traz_o_que_a_tela_precisa(B, db):
    B["upsert_many"](db, "produtos", [
        {"sku": f"P-{i:03d}", "nome": f"Item {i}", "preco": 1.0, "estoque": 1}
        for i in range(25)], "sku")

    pagina = B["paginate"](db, "produtos", 2, 10, order_by="sku")
    assert pagina["pagina"] == 2
    assert pagina["paginas"] == 3
    assert pagina["total"] == 25
    assert len(pagina["itens"]) == 10
    assert pagina["tem_anterior"] and pagina["tem_proxima"]
    # E a segunda página não repete a primeira.
    assert pagina["itens"][0]["sku"] == "P-010"


def test_a_ultima_pagina_sabe_que_e_a_ultima(B, db):
    B["upsert_many"](db, "produtos", [
        {"sku": f"P-{i}", "nome": f"I{i}", "preco": 1.0, "estoque": 1}
        for i in range(12)], "sku")
    pagina = B["paginate"](db, "produtos", 2, 10, order_by="sku")
    assert len(pagina["itens"]) == 2
    assert pagina["tem_proxima"] is False


def test_por_pagina_tem_teto(B, db):
    """O número vem de fora numa rota, e `?por_pagina=1000000` é como se
    derruba um servidor sem exploit."""
    pagina = B["paginate"](db, "produtos", 1, 999999)
    assert pagina["por_pagina"] == 500


def test_o_relatorio_agrupa_e_ordena(B, db):
    _produto(B, db, "L-1", "Duna")
    for vendedor, valor in (("ana", 100.0), ("ana", 50.0), ("bruno", 30.0)):
        B["insert"](db, "vendas", {"produto_id": 1, "quantidade": 1,
                                   "valor": valor, "vendedor": vendedor})

    linhas = B["aggregate"](db, "vendas",
                            {"receita": ["sum", "valor"],
                             "quantas": ["count", "*"]},
                            group_by="vendedor", order_by="receita DESC")
    assert linhas[0]["vendedor"] == "ana"
    assert linhas[0]["receita"] == 150.0
    assert linhas[0]["quantas"] == 2


def test_group_count_e_o_relatorio_que_mais_se_pede(B, db):
    _produto(B, db, "L-1", "Duna")
    for quem in ("ana", "ana", "bruno"):
        B["insert"](db, "vendas", {"produto_id": 1, "quantidade": 1,
                                   "valor": 1.0, "vendedor": quem})
    linhas = B["group_count"](db, "vendas", "vendedor")
    assert linhas[0] == {"vendedor": "ana", "quantidade": 2}


# ═══════════════════════════════════════════════════════════
#  Busca textual
# ═══════════════════════════════════════════════════════════

def test_a_busca_acha_por_prefixo(B, db):
    """`"livr*"` — o `*` dentro das aspas é um caractere literal, e a
    busca devolvia lista vazia sem um erro sequer. A sintaxe de prefixo
    do FTS5 é `"livr"*`."""
    _produto(B, db, "L-1", "O Hobbit")
    _produto(B, db, "L-2", "Duna")
    B["create_search"](db, "produtos", ["nome", "sku"])

    achados = B["search"](db, "produtos", "hobb")
    assert len(achados) == 1
    assert achados[0]["nome"] == "O Hobbit"


def test_a_busca_devolve_a_linha_da_tabela_original(B, db):
    """Quem busca quer o produto, não o índice."""
    _produto(B, db, "L-1", "O Hobbit", 49.9, 7)
    B["create_search"](db, "produtos", ["nome"])
    achado = B["search"](db, "produtos", "hobbit")[0]
    assert achado["preco"] == 49.9
    assert achado["estoque"] == 7


def test_o_indice_se_mantem_em_dia(B, db):
    """Sem os gatilhos, o índice envelhece em silêncio e a busca deixa
    de achar o que foi cadastrado depois."""
    _produto(B, db, "L-1", "O Hobbit")
    B["create_search"](db, "produtos", ["nome"])

    _produto(B, db, "L-2", "Hobbit Anotado")
    assert len(B["search"](db, "produtos", "hobbit")) == 2

    B["upsert"](db, "produtos", {"sku": "L-2", "nome": "Coisa Outra",
                                 "preco": 1.0, "estoque": 1}, "sku")
    assert len(B["search"](db, "produtos", "hobbit")) == 1

    B["delete"](db, "produtos", {"sku": "L-1"})
    assert B["search"](db, "produtos", "hobbit") == []


def test_a_busca_com_varias_palavras(B, db):
    _produto(B, db, "L-1", "O Senhor dos Aneis")
    _produto(B, db, "L-2", "O Hobbit")
    B["create_search"](db, "produtos", ["nome"])
    assert len(B["search"](db, "produtos", "senhor anei")) == 1


def test_um_termo_vazio_nao_devolve_tudo(B, db):
    _produto(B, db, "L-1", "Duna")
    B["create_search"](db, "produtos", ["nome"])
    assert B["search"](db, "produtos", "   ") == []


def test_buscar_sem_indice_diz_como_criar(B, db):
    with pytest.raises(Exception) as erro:
        B["search"](db, "produtos", "x")
    assert "create_search" in erro.value.dica


# ═══════════════════════════════════════════════════════════
#  Diagnóstico
# ═══════════════════════════════════════════════════════════

def test_o_explain_denuncia_a_varredura_e_o_indice_resolve(B, db):
    """A linha que importa é a que diz SCAN: num cadastro de 200 mil
    produtos é a diferença entre 2 ms e 2 s."""
    _produto(B, db, "L-1", "Duna")

    antes = B["explain"](db, "SELECT * FROM produtos WHERE nome = ?", ["Duna"])
    assert antes["varre_tabela"] is True
    assert "le a tabela inteira" in antes["aviso"]

    B["create_index"](db, "produtos", ["nome"])
    depois = B["explain"](db, "SELECT * FROM produtos WHERE nome = ?", ["Duna"])
    assert depois["varre_tabela"] is False
    assert depois["aviso"] == ""


def test_os_indices_saem_com_as_colunas(B, db):
    B["create_index"](db, "produtos", ["nome", "preco"], name="idx_np")
    achados = {i["nome"]: i for i in B["indexes"](db, "produtos")}
    assert achados["idx_np"]["colunas"] == ["nome", "preco"]
    # O índice que o SQLite cria para o UNIQUE é marcado como automático.
    assert any(i["automatico"] for i in achados.values())


def test_o_stats_nao_conta_as_tabelas_sombra_do_fts(B, db):
    """Um banco de duas tabelas parecia ter dez."""
    _produto(B, db, "L-1", "Duna")
    antes = len(B["stats"](db)["tabelas"])
    B["create_search"](db, "produtos", ["nome"])
    assert len(B["stats"](db)["tabelas"]) == antes


def test_a_integridade_e_conferivel(B, db):
    assert B["integrity"](db)["ok"] is True


def test_as_chaves_estrangeiras_sao_legiveis(B, db):
    chaves = B["foreign_keys"](db, "vendas")
    assert chaves[0]["coluna"] == "produto_id"
    assert chaves[0]["aponta_para"] == "produtos"


def test_o_schema_sai_como_sql(B, db):
    sql = B["schema_sql"](db, "produtos")
    assert "CREATE TABLE" in sql and "sku" in sql
    inteiro = B["schema_sql"](db)
    assert "produtos" in inteiro and "vendas" in inteiro


# ═══════════════════════════════════════════════════════════
#  Migrações
# ═══════════════════════════════════════════════════════════

def _migracoes():
    return [
        {"version": 1, "description": "clientes",
         "up": "CREATE TABLE clientes (id INTEGER PRIMARY KEY, nome TEXT);",
         "down": "DROP TABLE clientes;"},
        {"version": 2, "description": "email",
         "up": "ALTER TABLE clientes ADD COLUMN email TEXT;",
         "down": "ALTER TABLE clientes DROP COLUMN email;"},
    ]


def test_migrar_e_desfazer(B, db):
    assert B["migrate"](db, _migracoes()) == 2
    assert "email" in [c["name"] for c in B["columns"](db, "clientes")]

    assert B["rollback_migration"](db, _migracoes()) == 1
    assert "email" not in [c["name"] for c in B["columns"](db, "clientes")]
    assert B["table_exists"](db, "clientes")


def test_o_rollback_desfaz_uma_por_padrao(B, db):
    """Desfazer em cascata por acidente é perda de dado."""
    B["migrate"](db, _migracoes())
    B["rollback_migration"](db, _migracoes())
    assert [m["version"] for m in B["migrations_applied"](db)] == [1]


def test_o_rollback_ate_uma_versao(B, db):
    B["migrate"](db, _migracoes())
    assert B["rollback_migration"](db, _migracoes(), ate=0) == 2
    assert B["migrations_applied"](db) == []


def test_uma_migracao_sem_down_nao_e_pulada_em_silencio(B, db):
    """Pular deixaria o banco num estado que nenhuma versão descreve."""
    migracoes = [{"version": 1, "description": "sem volta",
                  "up": "CREATE TABLE x (id INTEGER);"}]
    B["migrate"](db, migracoes)
    with pytest.raises(Exception) as erro:
        B["rollback_migration"](db, migracoes)
    assert "nao tem 'down'" in str(erro.value)


def test_migrar_e_idempotente(B, db):
    assert B["migrate"](db, _migracoes()) == 2
    assert B["migrate"](db, _migracoes()) == 0


# ═══════════════════════════════════════════════════════════
#  Nome vai cru para o SQL — e por isso é conferido
# ═══════════════════════════════════════════════════════════

@pytest.mark.parametrize("veneno", [
    "nome; DROP TABLE produtos",
    'nome" OR 1=1 --',
    "produtos.nome",
    "",
    "1nome",
])
def test_nome_de_coluna_invalido_e_recusado(B, db, veneno):
    """Valor vai por `?`. Nome de coluna não pode ir por parâmetro — o
    SQLite não aceita — e portanto vai concatenado. É a porta de
    injeção, e a única defesa é recusar o que não parece um nome."""
    with pytest.raises(Exception):
        B["increment"](db, "produtos", veneno, 1)
    assert B["table_exists"](db, "produtos")


def test_order_by_vindo_de_fora_e_conferido(B, db):
    """`?ordenar=nome; DROP TABLE x` é SQL injetado."""
    with pytest.raises(Exception):
        B["aggregate"](db, "produtos", {"n": ["count", "*"]},
                       order_by="nome; DROP TABLE produtos")
    assert B["table_exists"](db, "produtos")


def test_uma_direcao_de_ordenacao_invalida_e_recusada(B, db):
    with pytest.raises(Exception) as erro:
        B["aggregate"](db, "produtos", {"n": ["count", "*"]},
                       order_by="nome ASCENDENTE")
    assert "direcao de ordenacao" in str(erro.value)


def test_uma_agregacao_desconhecida_e_recusada(B, db):
    """O nome vai cru para o SQL."""
    with pytest.raises(Exception) as erro:
        B["aggregate"](db, "produtos", {"x": ["median", "preco"]})
    assert "agregacao conhecida" in str(erro.value)


def test_ordem_valida_passa(B, db):
    _produto(B, db, "L-1", "Duna")
    linhas = B["aggregate"](db, "produtos", {"n": ["count", "*"]},
                            group_by="sku", order_by="sku DESC, n")
    assert linhas


# ═══════════════════════════════════════════════════════════
#  A cláusula de condição
# ═══════════════════════════════════════════════════════════

def test_void_vira_is_null_e_nao_igual_a_null(B, db):
    """`coluna = NULL` nunca é verdadeiro em SQL; quem escreve `void`
    quer dizer "está vazio"."""
    B["insert"](db, "produtos", {"sku": "L-1", "nome": "Duna",
                                 "preco": 1.0, "estoque": 1})
    B["execute"](db, "ALTER TABLE produtos ADD COLUMN nota TEXT")
    assert B["increment"](db, "produtos", "estoque", 1, {"nota": None}) == 1


def test_uma_lista_vazia_nao_casa_com_nada(B, db):
    """`IN ()` é erro de sintaxe no SQLite, e a resposta certa para
    "nenhum dos valores" é não casar com nada."""
    _produto(B, db, "L-1", "Duna")
    assert B["increment"](db, "produtos", "estoque", 1, {"sku": []}) == 0


def test_os_operadores_de_comparacao(B, db):
    _produto(B, db, "L-1", "Duna", preco=50.0)
    _produto(B, db, "L-2", "Solaris", preco=150.0)
    assert B["increment"](db, "produtos", "estoque", 1,
                          {"preco": {"gte": 100}}) == 1


def test_um_operador_desconhecido_e_recusado(B, db):
    with pytest.raises(Exception) as erro:
        B["increment"](db, "produtos", "estoque", 1,
                       {"preco": {"aproximadamente": 10}})
    assert "operador de condicao" in str(erro.value)
