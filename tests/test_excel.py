"""
Testes do Arcane.Excel — planilhas .xlsx sem dependencia externa.

O que mais importa aqui: o arquivo gerado precisa ser um .xlsx de
verdade (ZIP com as pecas que o Excel exige), e nao apenas algo que o
nosso proprio leitor consiga reabrir.
"""

import datetime
import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.stdlib import get_module  # noqa: E402
from dataforge.stdlib.arcane_excel import (  # noqa: E402
    ArcaneExcel, Livro, coluna_para_letra, endereco, ler_endereco,
    letra_para_coluna,
)


@pytest.fixture
def xls():
    return get_module("Arcane.Excel")


# ── Enderecos ────────────────────────────────────────────────

@pytest.mark.parametrize("indice,letra", [
    (0, "A"), (1, "B"), (25, "Z"), (26, "AA"), (27, "AB"),
    (51, "AZ"), (52, "BA"), (701, "ZZ"), (702, "AAA"),
])
def test_letra_de_coluna_nos_dois_sentidos(indice, letra):
    assert coluna_para_letra(indice) == letra
    assert letra_para_coluna(letra) == indice


def test_endereco_nos_dois_sentidos():
    assert endereco(0, 0) == "A1"
    assert endereco(6, 1) == "B7"
    assert ler_endereco("B7") == (6, 1)
    assert ler_endereco("aa10") == (9, 26)


def test_endereco_invalido_reclama():
    with pytest.raises(ValueError, match="inválido"):
        ler_endereco("nao é célula")


# ── Escrita ──────────────────────────────────────────────────

def test_arquivo_gerado_e_um_xlsx_de_verdade(xls, tmp_path):
    """As pecas que o Excel exige precisam estar todas no ZIP."""
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["a", "b"], [1, 2]])

    assert zipfile.is_zipfile(destino)
    with zipfile.ZipFile(destino) as z:
        nomes = z.namelist()
        for exigido in ("[Content_Types].xml", "_rels/.rels",
                        "xl/workbook.xml", "xl/_rels/workbook.xml.rels",
                        "xl/styles.xml", "xl/worksheets/sheet1.xml"):
            assert exigido in nomes, f"falta {exigido}"
        assert z.testzip() is None            # nenhum membro corrompido


def test_xml_gerado_e_bem_formado(xls, tmp_path):
    import xml.etree.ElementTree as ET
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["nome & cia", "<tag>"], ['aspas "x"', 1]])
    with zipfile.ZipFile(destino) as z:
        for nome in z.namelist():
            if nome.endswith(".xml") or nome.endswith(".rels"):
                ET.fromstring(z.read(nome))   # estoura se estiver torto


def test_caracter_de_controle_nao_corrompe_o_arquivo(xls, tmp_path):
    """Um \\x00 vindo de CSV sujo geraria um arquivo que o Excel recusa."""
    import xml.etree.ElementTree as ET
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["ok"], ["a\x00b\x07c"]])
    with zipfile.ZipFile(destino) as z:
        ET.fromstring(z.read("xl/worksheets/sheet1.xml"))


# ── Ida e volta ──────────────────────────────────────────────

def test_tipos_sobrevivem_a_ida_e_volta(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    livro = xls["new"]()
    xls["sheet"](livro, "T", [
        ["texto", "inteiro", "real", "booleano", "vazio"],
        ["oi", 42, 3.5, True, None],
        ["tchau", -7, 0.001, False, None],
    ])
    xls["save"](livro, destino)

    lido = xls["read"](destino)
    linhas = xls["rows"](lido, "T")
    assert linhas[1][:4] == ["oi", 42, 3.5, True]
    assert linhas[2][:4] == ["tchau", -7, 0.001, False]


def test_data_volta_como_data(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    livro = xls["new"]()
    aba = xls["sheet"](livro, "T")
    xls["set"](aba, "A1", datetime.date(2026, 3, 15))
    xls["save"](livro, destino)

    valor = xls["get"](xls["sheet"](xls["read"](destino), "T"), "A1")
    assert isinstance(valor, (datetime.date, datetime.datetime))
    assert (valor.year, valor.month, valor.day) == (2026, 3, 15)


def test_acentos_e_emoji_sobrevivem(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["coração", "ação 🔨", "ÀÉÎÕÜ"]])
    assert xls["rows"](xls["read"](destino))[0] == \
        ["coração", "ação 🔨", "ÀÉÎÕÜ"]


def test_varias_abas_mantem_nome_e_ordem(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    livro = xls["new"]()
    for nome in ("Vendas", "Custos", "Resumo 2026"):
        xls["sheet"](livro, nome, [["x"], [1]])
    xls["save"](livro, destino)
    assert xls["sheets"](xls["read"](destino)) == \
        ["Vendas", "Custos", "Resumo 2026"]


def test_planilha_esparsa_nao_inventa_celulas(xls, tmp_path):
    """Escrever em Z100 nao pode materializar 100 linhas vazias."""
    destino = str(tmp_path / "t.xlsx")
    livro = xls["new"]()
    aba = xls["sheet"](livro, "T")
    xls["set"](aba, "A1", "canto")
    xls["set"](aba, "Z100", "outro canto")
    assert len(aba.celulas) == 2
    xls["save"](livro, destino)

    lido = xls["read"](destino)
    assert xls["dims"](lido, "T") == {"linhas": 100, "colunas": 26,
                                      "celulas": 2}
    assert xls["get"](xls["sheet"](lido, "T"), "Z100") == "outro canto"


# ── Vaults e cabecalho ───────────────────────────────────────

def test_lista_de_vaults_vira_tabela_com_cabecalho(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [
        {"produto": "Martelo", "qtd": 3},
        {"produto": "Bigorna", "qtd": 1},
    ])
    linhas = xls["rows"](xls["read"](destino))
    assert linhas[0] == ["produto", "qtd"]
    assert linhas[1] == ["Martelo", 3]


def test_vaults_com_chaves_diferentes_ganham_todas_as_colunas(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [{"a": 1}, {"a": 2, "b": 9}])
    linhas = xls["rows"](xls["read"](destino))
    assert linhas[0] == ["a", "b"]
    assert linhas[2] == [2, 9]


def test_records_devolve_vaults_pelo_cabecalho(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["nome", "idade"], ["Ana", 30], ["Bia", 25]])
    assert xls["records"](xls["read"](destino)) == [
        {"nome": "Ana", "idade": 30},
        {"nome": "Bia", "idade": 25},
    ]


# ── Colunas ──────────────────────────────────────────────────

def test_coluna_pelo_titulo_e_pela_letra(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["nome", "qtd"], ["Ana", 3], ["Bia", 7]])
    lido = xls["read"](destino)
    assert xls["column"](lido, None, "qtd") == [3, 7]
    assert xls["column"](lido, None, "B") == ["qtd", 3, 7]


def test_titulo_vence_a_letra_de_coluna(xls, tmp_path):
    """Uma coluna chamada 'B' deve ser achada pelo nome, nao pela posicao."""
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["B", "outra"], [1, 2], [3, 4]])
    assert xls["column"](xls["read"](destino), None, "B") == [1, 3]


def test_coluna_inexistente_reclama(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["a"], [1]])
    with pytest.raises(ValueError, match="não encontrada"):
        xls["column"](xls["read"](destino), None, "não existe")


# ── Formulas ─────────────────────────────────────────────────

def test_formula_e_gravada_e_relida(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    livro = xls["new"]()
    aba = xls["sheet"](livro, "T", [["v"], [10], [20]])
    xls["formula"](aba, "A4", "=SUM(A2:A3)")
    xls["save"](livro, destino)

    relido = xls["sheet"](xls["read"](destino), "T")
    assert relido.formulas[(3, 0)] == "SUM(A2:A3)"


# ── Conversao ────────────────────────────────────────────────

def test_csv_vira_xlsx_com_numeros_de_verdade(xls, tmp_path):
    origem = tmp_path / "d.csv"
    origem.write_text("nome,qtd\nAna,3\nBia,7\n", encoding="utf-8")
    livro = xls["from_csv"](str(origem))
    linhas = xls["rows"](livro)
    assert linhas[0] == ["nome", "qtd"]
    assert linhas[1] == ["Ana", 3]      # 3, nao "3"


def test_xlsx_vira_csv(xls, tmp_path):
    fonte = str(tmp_path / "t.xlsx")
    xls["quick"](fonte, [["a", "b"], [1, 2]])
    destino = str(tmp_path / "saida.csv")
    xls["to_csv"](xls["read"](fonte), destino)
    assert open(destino, encoding="utf-8").read().replace("\r\n", "\n") \
        == "a,b\n1,2\n"


def test_planilha_vira_frame_de_analise(xls, tmp_path):
    destino = str(tmp_path / "t.xlsx")
    xls["quick"](destino, [["produto", "qtd"], ["Martelo", 12], ["Tenaz", 8]])
    frame = xls["to_frame"](xls["read"](destino))
    assert frame.shape() == [2, 2]
    assert frame.column("qtd") == [12, 8]


def test_arquivo_ausente_diz_o_nome(xls):
    with pytest.raises(FileNotFoundError, match="não encontrada"):
        xls["read"](os.path.join("nao", "existe", "isso.xlsx"))


# ── describe(frame): o bug que motivou a correcao ────────────

def test_describe_de_um_frame_descreve_cada_coluna():
    """Antes devolvia {'count': 0, 'type': 'non-numeric'} calado."""
    An = get_module("Analytics")
    frame = An["from_records"]([{"a": 1, "b": "x"},
                                {"a": 5, "b": "y"},
                                {"a": 9, "b": "z"}])
    saida = An["describe"](frame)
    assert saida["a"]["count"] == 3
    assert saida["a"]["mean"] == 5.0
    assert saida["b"]["type"] == "non-numeric"


def test_describe_de_lista_continua_igual():
    An = get_module("Analytics")
    assert An["describe"]([1, 2, 3, 4])["mean"] == 2.5


def test_describe_ignora_booleano_como_numero():
    """True vale 1 em Python; numa coluna de dados isso e ruido."""
    An = get_module("Analytics")
    assert An["describe"]([True, False, True])["count"] == 0
