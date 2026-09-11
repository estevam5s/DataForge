# -*- coding: utf-8 -*-
"""Parquet e Data Lake.

O que se testa aqui é INTEROPERABILIDADE. Um Parquet que só o DataForge
lê não é Parquet: é um formato próprio com nome emprestado. Quando o
pyarrow existe na máquina, os testes leem de volta com ele — e escrevem
com ele para lermos.
"""

import os
import shutil
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.errors import ValueError_                          # noqa: E402
from dataforge.stdlib import get_module, parquet                  # noqa: E402

L = get_module("Arcane.Lago")


def _python_com_pyarrow():
    """Um Python que tenha pyarrow, ou None.

    Ele quase nunca está no venv do DataForge — que não tem dependência
    nenhuma —, mas costuma existir noutro Python da máquina. Procurar
    ali é o que torna o teste de interoperabilidade possível sem
    acrescentar uma dependência ao projeto.
    """
    for caminho in ("/opt/anaconda3/bin/python3", "/opt/homebrew/bin/python3",
                    "/usr/local/bin/python3", sys.executable):
        if not os.path.isfile(caminho):
            continue
        try:
            r = subprocess.run([caminho, "-c", "import pyarrow"],
                               capture_output=True, timeout=30)
            if r.returncode == 0:
                return caminho
        except (OSError, subprocess.SubprocessError):
            continue
    return None


PYARROW = _python_com_pyarrow()
so_com_pyarrow = pytest.mark.skipif(
    PYARROW is None, reason="nenhum Python com pyarrow nesta máquina")


LINHAS = [
    {"id": 1, "nome": "Ana", "valor": 10.5, "ativo": True},
    {"id": 2, "nome": "Bo", "valor": 20.0, "ativo": False},
    {"id": 3, "nome": None, "valor": None, "ativo": True},
]


# ═══════════════════════════════════════════════════════════
#  Parquet: ida e volta
# ═══════════════════════════════════════════════════════════

class TestParquet:
    def test_ida_e_volta(self, tmp_path):
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS)
        assert parquet.ler(f) == LINHAS

    def test_o_nulo_sobrevive(self, tmp_path):
        """Nulo vira nível de definição; perdê-lo desloca a coluna."""
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS)
        lidas = parquet.ler(f)
        assert lidas[2]["nome"] is None and lidas[2]["valor"] is None

    def test_marca_no_comeco_e_no_fim(self, tmp_path):
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS)
        bruto = open(f, "rb").read()
        assert bruto[:4] == b"PAR1" and bruto[-4:] == b"PAR1"

    def test_le_so_a_coluna_pedida(self, tmp_path):
        """É o ponto do formato colunar."""
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS)
        assert parquet.ler(f, ["id"]) == [{"id": 1}, {"id": 2}, {"id": 3}]

    def test_coluna_que_nao_existe_e_recusada_com_a_lista(self, tmp_path):
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS)
        with pytest.raises(ValueError_) as e:
            parquet.ler(f, ["fantasma"])
        assert "fantasma" in e.value.message
        # a nota lista o que EXISTE — é o que resolve o erro de digitação
        assert "nome" in e.value.nota

    def test_esquema_sem_ler_os_dados(self, tmp_path):
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS)
        e = parquet.esquema(f)
        assert e["linhas"] == 3
        tipos = {c["nome"]: c["tipo"] for c in e["colunas"]}
        assert tipos == {"id": "inteiro", "nome": "texto",
                         "valor": "numero", "ativo": "booleano"}

    def test_a_coluna_com_nulo_e_declarada_opcional(self, tmp_path):
        """Declarar OPTIONAL sem nulo custaria os níveis à toa."""
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS)
        por_nome = {c["nome"]: c for c in parquet.esquema(f)["colunas"]}
        assert por_nome["id"]["aceita_vazio"] is False
        assert por_nome["nome"]["aceita_vazio"] is True

    def test_varios_grupos(self, tmp_path):
        f = str(tmp_path / "t.parquet")
        linhas = [{"n": i} for i in range(250)]
        parquet.escrever(f, linhas, por_grupo=100)
        assert parquet.esquema(f)["grupos"] == 3
        assert [l["n"] for l in parquet.ler(f)] == list(range(250))

    def test_sem_compressao_tambem_le(self, tmp_path):
        f = str(tmp_path / "t.parquet")
        parquet.escrever(f, LINHAS, compressao="")
        assert parquet.ler(f) == LINHAS

    def test_gzip_e_deterministico(self, tmp_path):
        """Sem mtime=0, o mesmo dado geraria bytes diferentes."""
        a, b = str(tmp_path / "a.parquet"), str(tmp_path / "b.parquet")
        parquet.escrever(a, LINHAS)
        parquet.escrever(b, LINHAS)
        assert open(a, "rb").read() == open(b, "rb").read()

    def test_lista_vazia_e_recusada_com_o_motivo(self, tmp_path):
        with pytest.raises(ValueError_) as e:
            parquet.escrever(str(tmp_path / "t.parquet"), [])
        assert "esquema" in e.value.dica

    def test_arquivo_que_nao_e_parquet(self, tmp_path):
        f = tmp_path / "x.parquet"
        f.write_bytes(b"isto nao e parquet")
        with pytest.raises(ValueError_) as e:
            parquet.ler(str(f))
        assert "PAR1" in e.value.nota


# ═══════════════════════════════════════════════════════════
#  Interoperabilidade — o que faz ser Parquet de verdade
# ═══════════════════════════════════════════════════════════

@so_com_pyarrow
class TestInteroperabilidade:
    def _pyarrow(self, codigo):
        r = subprocess.run([PYARROW, "-c", codigo],
                           capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()

    def test_o_pyarrow_le_o_que_escrevemos(self, tmp_path):
        f = str(tmp_path / "df.parquet")
        parquet.escrever(f, LINHAS)
        saida = self._pyarrow(f"""
import pyarrow.parquet as pp, json
t = pp.read_table({f!r})
print(json.dumps({{"linhas": t.num_rows,
                   "colunas": t.schema.names,
                   "tipos": [str(x) for x in t.schema.types],
                   "dados": t.to_pydict()}}))""")
        import json
        r = json.loads(saida)
        assert r["linhas"] == 3
        assert r["tipos"] == ["int64", "string", "double", "bool"]
        assert r["dados"]["nome"] == ["Ana", "Bo", None]

    def test_lemos_o_que_o_pyarrow_escreve(self, tmp_path):
        """Ele usa DICIONÁRIO por padrão — é assim que a maioria dos
        Parquet do mundo é escrita, e ler só PLAIN leria quase nada."""
        f = str(tmp_path / "arrow.parquet")
        self._pyarrow(f"""
import pyarrow as pa, pyarrow.parquet as pp
pp.write_table(pa.table({{"id":[10,20,30],"nome":["a","b",None],
                          "v":[1.5,2.5,3.5],"ok":[True,False,True]}}),
               {f!r}, compression="gzip")""")
        linhas = parquet.ler(f)
        assert [l["id"] for l in linhas] == [10, 20, 30]
        assert [l["nome"] for l in linhas] == ["a", "b", None]
        assert linhas[0]["ok"] is True

    def test_volume_com_varios_grupos_e_dicionario_grande(self, tmp_path):
        """Um índice largo cruza três bytes no bit-packing.

        O erro aparecia num valor em mil, com o resto certo — o pior
        jeito de um bug de formato se manifestar.
        """
        f = str(tmp_path / "grande.parquet")
        self._pyarrow(f"""
import pyarrow as pa, pyarrow.parquet as pp
n = 20000
pp.write_table(pa.table({{"id": list(range(n)),
                          "cat": ["a","b","c","d"]*(n//4)}}),
               {f!r}, compression="gzip", row_group_size=5000)""")
        linhas = parquet.ler(f, ["id"])
        assert [l["id"] for l in linhas] == list(range(20000))

    def test_o_pyarrow_le_o_lago_particionado(self, tmp_path):
        """Partição Hive: o layout que Spark e DuckDB já entendem."""
        lago = L["lago"](str(tmp_path / "lago"))
        linhas = [{"id": i, "ano": 2025 + (i % 2), "v": i * 1.5}
                  for i in range(1, 41)]
        L["gravar"](lago, "vendas", linhas, ["ano"])
        saida = self._pyarrow(f"""
import pyarrow.dataset as ds, json
d = ds.dataset({str(tmp_path / 'lago' / 'vendas')!r},
               format="parquet", partitioning="hive")
t = d.to_table()
print(json.dumps({{"linhas": t.num_rows, "colunas": sorted(t.schema.names),
                   "so2026": d.to_table(filter=ds.field("ano")==2026).num_rows}}))""")
        import json
        r = json.loads(saida)
        assert r["linhas"] == 40
        assert "ano" in r["colunas"], "a partição não virou coluna"
        assert r["so2026"] == 20


# ═══════════════════════════════════════════════════════════
#  O lago
# ═══════════════════════════════════════════════════════════

VENDAS = [
    {"id": 1, "ano": 2025, "mes": 12, "produto": "Martelo", "valor": 89.9},
    {"id": 2, "ano": 2026, "mes": 1, "produto": "Bigorna", "valor": 450.0},
    {"id": 3, "ano": 2026, "mes": 1, "produto": "Tenaz", "valor": 35.5},
    {"id": 4, "ano": 2026, "mes": 2, "produto": "Torno", "valor": 900.0},
]


class TestLago:
    def _lago(self, tmp_path):
        lago = L["lago"](str(tmp_path / "lago"))
        L["gravar"](lago, "vendas", VENDAS, ["ano", "mes"])
        return lago

    def test_particiona_no_caminho(self, tmp_path):
        lago = self._lago(tmp_path)
        caminhos = [a["arquivo"] for a in L["arquivos"](lago, "vendas")]
        assert any("ano=2026/mes=1" in c.replace(os.sep, "/") for c in caminhos)

    def test_o_filtro_descarta_pelo_NOME_da_pasta(self, tmp_path):
        lago = self._lago(tmp_path)
        assert len(L["ler"](lago, "vendas", {"ano": 2026})) == 3
        assert len(L["ler"](lago, "vendas", {"ano": 2026, "mes": 1})) == 2

    def test_o_campo_de_particao_volta_na_linha(self, tmp_path):
        """Ele não está DENTRO do arquivo — vem do caminho."""
        lago = self._lago(tmp_path)
        linha = L["ler"](lago, "vendas", {"ano": 2026, "mes": 2})[0]
        assert linha["ano"] == "2026" and linha["produto"] == "Torno"

    def test_gravar_acrescenta_e_nao_sobrescreve(self, tmp_path):
        lago = self._lago(tmp_path)
        L["gravar"](lago, "vendas",
                    [{"id": 9, "ano": 2026, "mes": 1, "produto": "Lima",
                      "valor": 1.0}], ["ano", "mes"])
        assert len(L["ler"](lago, "vendas", {"ano": 2026, "mes": 1})) == 3

    def test_compactar_junta_sem_perder_linha(self, tmp_path):
        lago = self._lago(tmp_path)
        for i in range(3):
            L["gravar"](lago, "vendas",
                        [{"id": 100 + i, "ano": 2026, "mes": 1,
                          "produto": f"x{i}", "valor": 1.0}], ["ano", "mes"])
        antes = len(L["ler"](lago, "vendas"))
        L["compactar"](lago, "vendas")
        assert len(L["arquivos"](lago, "vendas", {"ano": 2026, "mes": 1})) == 1
        assert len(L["ler"](lago, "vendas")) == antes

    def test_particoes_lista_o_que_existe(self, tmp_path):
        p = L["particoes"](self._lago(tmp_path), "vendas")
        assert {"ano": "2025", "mes": "12"} in p
        assert len(p) == 3

    def test_remover_particao_sem_filtro_e_recusado(self, tmp_path):
        """Sem filtro, apagaria a tabela inteira."""
        with pytest.raises(ValueError_):
            L["remover_particao"](self._lago(tmp_path), "vendas", {})

    def test_remover_particao_leva_so_ela(self, tmp_path):
        lago = self._lago(tmp_path)
        L["remover_particao"](lago, "vendas", {"ano": 2025})
        assert len(L["ler"](lago, "vendas")) == 3

    def test_tabela_que_nao_existe_diz_quais_existem(self, tmp_path):
        with pytest.raises(Exception) as e:
            L["ler"](self._lago(tmp_path), "fantasma")
        assert "vendas" in e.value.nota

    def test_valor_de_particao_nao_escapa_da_pasta(self, tmp_path):
        """O valor vem do DADO, e dado vem de fora — é Zip Slip por outra porta."""
        lago = L["lago"](str(tmp_path / "lago"))
        L["gravar"](lago, "t", [{"g": "../../fora", "v": 1}], ["g"])
        for pasta, _, nomes in os.walk(str(tmp_path / "lago")):
            for nome in nomes:
                caminho = os.path.realpath(os.path.join(pasta, nome))
                assert caminho.startswith(os.path.realpath(str(tmp_path / "lago")))

    def test_vacuo_tira_o_arquivo_pela_metade(self, tmp_path):
        lago = self._lago(tmp_path)
        sujo = os.path.join(lago.raiz, "vendas", "lixo.parquet.parcial")
        open(sujo, "wb").write(b"gravacao interrompida")
        L["vacuo"](lago)
        assert not os.path.exists(sujo)


class TestCamadas:
    def test_promover_nao_altera_o_bronze(self, tmp_path):
        """É o bruto que permite reprocessar quando a regra estava errada."""
        lago = L["lago"](str(tmp_path / "lago"))
        bronze = L["camada"](lago, "bronze")
        L["gravar"](bronze, "v", [{"id": i, "ano": 2026} for i in range(5)],
                    ["ano"])
        L["promover"](lago, "v", "bronze", "prata",
                      lambda linhas: linhas[:2], ["ano"])
        assert len(L["ler"](bronze, "v")) == 5
        assert len(L["ler"](L["camada"](lago, "prata"), "v")) == 2

    def test_camada_desconhecida_e_recusada(self, tmp_path):
        lago = L["lago"](str(tmp_path / "lago"))
        with pytest.raises(ValueError_) as e:
            L["camada"](lago, "platina")
        assert "bronze" in e.value.nota
