"""Arcane.Privacidade e Arcane.Integridade — as distinções, cobradas.

O SRI é conferido contra o exemplo publicado pela MDN; comparar a
implementação com ela mesma não prova nada.
"""
import os
import statistics
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.stdlib import get_module  # noqa: E402

P = get_module("Arcane.Privacidade")
I = get_module("Arcane.Integridade")
CHAVE = "uma-chave-que-mora-fora-da-base"


# ── pseudonimizar ───────────────────────────────────────────────

def test_pseudonimo_e_estavel_e_separado_por_finalidade():
    a = P["pseudonimizar"]("529.982.247-25", CHAVE, "vendas")
    assert a == P["pseudonimizar"]("529.982.247-25 ", CHAVE, "vendas")
    assert a != P["pseudonimizar"]("529.982.247-25", CHAVE, "rh")
    assert a != P["pseudonimizar"]("529.982.247-25", CHAVE + "x", "vendas")
    assert len(a) == 16 and "529" not in a


def test_chave_curta_e_recusada_e_void_passa():
    with pytest.raises(Exception) as e:
        P["pseudonimizar"]("x", "curta")
    assert "16 caracteres" in str(e.value)
    assert P["pseudonimizar"](None, CHAVE) is None


# ── generalizar, k-anonimato, minimizar ─────────────────────────

def test_generalizar_cada_tipo():
    assert P["generalizar"](34, "idade") == "30-39"
    assert P["generalizar"](34, "idade", 2) == "20-39"
    assert P["generalizar"]("01310-100", "cep") == "01310-***"
    assert P["generalizar"]("01310100", "cep", 2) == "013**-***"
    assert P["generalizar"]("2026-09-21", "data") == "2026-09"
    assert P["generalizar"]("2026-09-21", "data", 2) == "2026"
    assert P["generalizar"](1234, "numero", 2) == 1200
    with pytest.raises(Exception):
        P["generalizar"]("123", "cep")
    with pytest.raises(Exception):
        P["generalizar"](1, "altura")


LINHAS = [
    {"cep": "01310-100", "idade": 34, "doenca": "A"},
    {"cep": "01310-200", "idade": 36, "doenca": "B"},
    {"cep": "01310-300", "idade": 31, "doenca": "A"},
    {"cep": "04567-000", "idade": 52, "doenca": "C"},
    {"cep": "04567-111", "idade": 58, "doenca": "B"},
]


def test_k_anonimato_acha_quem_esta_sozinho_e_generalizar_resolve():
    cru = P["k_anonimato"](LINHAS, ["cep", "idade"])
    assert cru["k"] == 1 and cru["grupos"] == 5
    gen = [{"cep": P["generalizar"](l["cep"], "cep", 2), "idade": P["generalizar"](l["idade"], "idade", 2)}
           for l in LINHAS]
    depois = P["k_anonimato"](gen, ["cep", "idade"])
    assert depois["k"] == 2 and depois["grupos"] == 2


def test_k_anonimato_sem_campos_e_recusado():
    with pytest.raises(Exception):
        P["k_anonimato"](LINHAS, [])


def test_minimizar_e_por_lista_de_permitidos():
    assert P["minimizar"](LINHAS[0], ["idade"]) == {"idade": 34}
    assert P["minimizar"](LINHAS[:2], ["cep"]) == [{"cep": "01310-100"}, {"cep": "01310-200"}]


# ── retenção ────────────────────────────────────────────────────

def test_vencidos_inclui_o_que_nao_tem_data():
    agora = 100 * 86400
    linhas = [{"id": 1, "criado": 99 * 86400}, {"id": 2, "criado": 1 * 86400},
              {"id": 3}, {"id": 4, "criado": "texto"}]
    assert [l["id"] for l in P["vencidos"](linhas, "criado", 30, agora)] == [2, 3, 4]


# ── consentimento ───────────────────────────────────────────────

def test_consentimento_e_por_finalidade_e_por_versao():
    c = P["consentimentos"]()
    c.conceder("ana", "nota-fiscal", "1", quando=10)
    assert c.pode("ana", "nota-fiscal", quando=20)
    assert not c.pode("ana", "marketing", quando=20)
    assert not c.pode("ana", "nota-fiscal", versao="2", quando=20)


def test_revogar_vale_dali_em_diante_e_nao_apaga_o_passado():
    c = P["consentimentos"]()
    c.conceder("ana", "marketing", quando=10).revogar("ana", "marketing", quando=50)
    assert c.pode("ana", "marketing", quando=30)
    assert not c.pode("ana", "marketing", quando=60)
    assert len(c.historico("ana")) == 2
    assert c.finalidades("ana") == []


# ── direitos do titular ─────────────────────────────────────────

def test_exportar_e_esquecer_percorrem_todo_lugar_e_relatam_falhas():
    banco = {"ana": {"email": "a@x"}}
    t = P["titulares"]()
    t.registrar("banco", lambda tit: banco.get(tit), lambda tit: banco.pop(tit, None))
    t.registrar("backup", lambda tit: 1 / 0, lambda tit: 1 / 0)
    e = t.exportar("ana")
    assert e["dados"]["banco"] == {"email": "a@x"} and not e["completo"]
    assert "backup" in e["falhas"]
    x = t.esquecer("ana")
    assert x["apagados"] == ["banco"] and not x["completo"] and "ana" not in banco


def test_registrar_sem_acao_e_recusado():
    with pytest.raises(Exception):
        P["titulares"]().registrar("x", None, lambda t: t)


# ── privacidade diferencial ─────────────────────────────────────

def test_contagem_privada_nunca_e_negativa_e_centra_no_valor():
    amostras = [P["contagem_privada"](100, 1.0, semente=s) for s in range(2000)]
    assert min(amostras) >= 0
    assert abs(statistics.mean(amostras) - 100) < 0.5
    assert len(set(amostras)) > 5      # ha ruido de verdade
    assert all(P["contagem_privada"](0, 1.0, semente=s) >= 0 for s in range(200))


def test_epsilon_menor_espalha_mais():
    largo = statistics.pstdev([P["contagem_privada"](1000, 0.1, semente=s) for s in range(1000)])
    estreito = statistics.pstdev([P["contagem_privada"](1000, 2.0, semente=s) for s in range(1000)])
    assert largo > 5 * estreito
    with pytest.raises(Exception):
        P["contagem_privada"](1, 0)


# ── integridade: SRI ────────────────────────────────────────────

# O exemplo da página "Subresource Integrity" da MDN.
MDN_JS = "alert('Hello, world.');"
MDN_SRI = "sha384-H8BRh8j48O9oYatfu5AZzq6A9RINhZO5H16dQZngK7T62em8MUt1FLm52t+eX6xO"


def test_sri_bate_com_o_exemplo_da_mdn():
    assert I["sri"](MDN_JS) == MDN_SRI
    assert I["conferir_sri"](MDN_JS, f"sha256-xxx {MDN_SRI}")
    assert not I["conferir_sri"](MDN_JS + " ", MDN_SRI)
    with pytest.raises(Exception):
        I["sri"]("x", "md5")


# ── integridade: manifesto ──────────────────────────────────────

def _pasta(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.df").write_text("out 1\n")
    (tmp_path / "b.txt").write_text("b\n")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text("ref\n")
    return tmp_path


def test_manifesto_e_relativo_com_barra_e_ignora_o_git(tmp_path):
    m = I["manifesto"](str(_pasta(tmp_path)))
    assert set(m) == {"src/a.df", "b.txt"}
    assert all(len(h) == 64 for h in m.values())


def test_link_simbolico_nao_e_seguido(tmp_path):
    p = _pasta(tmp_path)
    fora = tmp_path.parent / f"fora-{os.getpid()}.txt"
    fora.write_text("segredo\n")
    try:
        os.symlink(fora, p / "link.txt")
    except (OSError, NotImplementedError):
        pytest.skip("sem permissao para criar link simbolico")
    try:
        assert "link.txt" not in I["manifesto"](str(p))
    finally:
        fora.unlink()


def test_conferir_acha_acrescentado_removido_e_alterado(tmp_path):
    p = _pasta(tmp_path)
    m = I["manifesto"](str(p))
    assert I["conferir_manifesto"](str(p), m)["ok"]
    (p / "src" / "a.df").write_text("out 2\n")
    (p / "b.txt").unlink()
    (p / "novo.df").write_text("x\n")
    r = I["conferir_manifesto"](str(p), m)
    assert not r["ok"]
    assert (r["alterados"], r["removidos"], r["acrescentados"]) == (["src/a.df"], ["b.txt"], ["novo.df"])


def test_manifesto_assinado_denuncia_a_troca_conjunta(tmp_path):
    p = _pasta(tmp_path)
    assinado = I["assinar_manifesto"](I["manifesto"](str(p)), CHAVE)
    assert I["verificar_manifesto"](assinado, CHAVE)
    # quem troca o arquivo troca o manifesto junto — e a assinatura denuncia
    adulterado = {**assinado, "arquivos": {**assinado["arquivos"], "b.txt": "0" * 64}}
    assert not I["verificar_manifesto"](adulterado, CHAVE)
    assert not I["verificar_manifesto"](assinado, CHAVE + "outra")
    assert not I["verificar_manifesto"]({"arquivos": {}}, CHAVE)
    with pytest.raises(Exception):
        I["assinar_manifesto"]({}, "curta")


def test_do_dataforge(tmp_path):
    f = tmp_path / "p.df"
    f.write_text(
        'adopt Arcane.Privacidade as P\nadopt Arcane.Integridade as I\n'
        'a := P.pseudonimizar("529.982.247-25", "uma-chave-que-mora-fora", "vendas")\n'
        'assert len(a) is 16\n'
        'assert P.k_anonimato([{"c": 1}, {"c": 1}], ["c"])["k"] is 2\n'
        'c := P.consentimentos()\n'
        'c.conceder("ana", "marketing")\n'
        'assert c.pode("ana", "marketing") and not c.pode("ana", "pesquisa")\n'
        f'assert I.sri("{MDN_JS}") is "{MDN_SRI}"\n', encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", str(f)], cwd=RAIZ,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stdout + r.stderr
