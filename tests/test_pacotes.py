"""Testes do gerenciador de pacotes (dataforge add/install/remove/pack)."""

import json
import os
import sys
import tarfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.packages import (  # noqa: E402
    Dependencia, ErroPacote, Lock, Registro, Requisito, Versao,
    empacotar, resolver,
)


# ─── Versoes ───────────────────────────────────────────────

def test_versao_ordena():
    assert Versao("1.0.0") < Versao("1.0.1") < Versao("1.1.0") < Versao("2.0.0")
    assert Versao("1.10.0") > Versao("1.9.0")        # numerico, nao alfabetico
    assert Versao("v1.2.3") == Versao("1.2.3")       # o 'v' e ignorado


def test_versao_pre_release_vem_antes():
    assert Versao("1.0.0-beta") < Versao("1.0.0")


def test_versao_invalida():
    with pytest.raises(ErroPacote):
        Versao("nao-e-versao")


@pytest.mark.parametrize("requisito,versao,aceita", [
    ("*", "9.9.9", True),
    ("1.2.3", "1.2.3", True),
    ("1.2.3", "1.2.4", False),
    ("^1.2.3", "1.2.3", True),
    ("^1.2.3", "1.9.9", True),
    ("^1.2.3", "2.0.0", False),
    ("^1.2.3", "1.2.2", False),
    ("^0.2.3", "0.2.9", True),       # ^0.x trava o 'menor'
    ("^0.2.3", "0.3.0", False),
    ("~1.2.3", "1.2.99", True),
    ("~1.2.3", "1.3.0", False),
    (">=1.0 <2.0", "1.5.0", True),
    (">=1.0 <2.0", "2.0.0", False),
])
def test_requisito(requisito, versao, aceita):
    assert Requisito(requisito).aceita(Versao(versao)) is aceita


def test_requisito_escolhe_a_maior():
    assert str(Requisito("^1.0.0").melhor(["1.0.0", "1.5.2", "1.9.9", "2.0.0"])) == "1.9.9"
    assert Requisito("^3.0.0").melhor(["1.0.0", "2.0.0"]) is None


# ─── Dependencias ──────────────────────────────────────────

def test_dependencia_reconhece_a_fonte():
    assert Dependencia("a", "^1.0").fonte == "registro"
    assert Dependencia("a", "./local").fonte == "path"
    assert Dependencia("a", {"path": "../x"}).fonte == "path"
    assert Dependencia("a", "git+https://x/y.git").fonte == "git"
    assert Dependencia("a", {"git": "https://x/y.git", "ref": "v1"}).ref == "v1"
    assert Dependencia("a", "https://x/y.tar.gz").fonte == "url"


def test_dependencia_volta_para_toml():
    assert Dependencia("a", "^1.0").para_toml() == "^1.0"
    assert Dependencia("a", {"path": "../x"}).para_toml() == {"path": "../x"}


# ─── Resolucao ─────────────────────────────────────────────

class RegistroFalso(Registro):
    """Registro em memoria, para testar a resolucao sem rede."""

    def __init__(self, pacotes):
        self.url = "memoria"
        self.offline = False
        self._indice = {"pacotes": pacotes}


def _pkg(versoes):
    return {"versoes": {v: {"arquivo": f"x-{v}.tar.gz", "sha256": "",
                            "dependencias": d} for v, d in versoes.items()}}


def test_resolve_transitivas():
    reg = RegistroFalso({
        "app": _pkg({"1.0.0": {"nucleo": "^1.0.0"}}),
        "nucleo": _pkg({"1.0.0": {}, "1.4.0": {}}),
    })
    plano = resolver([Dependencia("app", "^1.0.0")], reg)
    assert set(plano) == {"app", "nucleo"}
    assert str(plano["nucleo"]["versao"]) == "1.4.0"      # a maior compativel


def test_resolve_intersecta_requisitos():
    reg = RegistroFalso({
        "a": _pkg({"1.0.0": {"comum": "^1.0.0"}}),
        "b": _pkg({"1.0.0": {"comum": "<1.5.0"}}),
        "comum": _pkg({"1.0.0": {}, "1.2.0": {}, "1.9.0": {}}),
    })
    plano = resolver([Dependencia("a", "*"), Dependencia("b", "*")], reg)
    # 1.9.0 serve ao 'a' mas nao ao 'b'; 1.2.0 serve aos dois
    assert str(plano["comum"]["versao"]) == "1.2.0"


def test_conflito_diz_quem_pediu_o_que():
    reg = RegistroFalso({
        "a": _pkg({"1.0.0": {"comum": "^1.0.0"}}),
        "b": _pkg({"1.0.0": {"comum": "^2.0.0"}}),
        "comum": _pkg({"1.0.0": {}, "2.0.0": {}}),
    })
    with pytest.raises(ErroPacote) as exc:
        resolver([Dependencia("a", "*"), Dependencia("b", "*")], reg)
    mensagem = str(exc.value)
    assert "comum" in mensagem
    assert "a@1.0.0" in mensagem and "b@1.0.0" in mensagem


def test_pacote_desconhecido_sugere_parecido():
    reg = RegistroFalso({"validador": _pkg({"1.0.0": {}})})
    with pytest.raises(ErroPacote) as exc:
        resolver([Dependencia("validadr", "*")], reg)
    assert "validador" in str(exc.value)


# ─── Lockfile ──────────────────────────────────────────────

def test_lock_grava_e_le(tmp_path):
    lock = Lock(str(tmp_path))
    lock.registrar("x", "1.0.0", "registro", "abc123", {"y": "^1.0"})
    lock.gravar("http://reg")

    relido = Lock(str(tmp_path))
    assert relido.pacotes["x"]["versao"] == "1.0.0"
    assert relido.pacotes["x"]["sha256"] == "abc123"
    assert relido.registro == "http://reg"


def test_lock_corrompido_nao_derruba(tmp_path):
    (tmp_path / "forge.lock").write_text("{ isto nao e json", encoding="utf-8")
    assert Lock(str(tmp_path)).pacotes == {}


# ─── Empacotar ─────────────────────────────────────────────

def _projeto(tmp_path, nome="meu-pacote", versao="1.0.0"):
    (tmp_path / "forge.toml").write_text(
        f'[package]\nname = "{nome}"\nversion = "{versao}"\n'
        'entry = "src/main.df"\n\n[dependencies]\n', encoding="utf-8")
    (tmp_path / "src").mkdir(exist_ok=True)
    (tmp_path / "src" / "main.df").write_text("out 1\n", encoding="utf-8")
    return tmp_path


def test_empacota_com_sha(tmp_path):
    _projeto(tmp_path)
    caminho, sha, nome, versao = empacotar(str(tmp_path))
    assert os.path.exists(caminho)
    assert nome == "meu-pacote" and versao == "1.0.0"
    assert len(sha) == 64


def test_empacotar_deixa_de_fora_o_que_nao_e_fonte(tmp_path):
    _projeto(tmp_path)
    (tmp_path / "forge_modules").mkdir()
    (tmp_path / "forge_modules" / "outro.df").write_text("x", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x", encoding="utf-8")

    caminho, _, _, _ = empacotar(str(tmp_path))
    with tarfile.open(caminho) as tar:
        nomes = tar.getnames()
    assert not any("forge_modules" in n for n in nomes)
    assert not any(".git" in n for n in nomes)
    assert any(n.endswith("src/main.df") for n in nomes)


def test_empacotar_recusa_nome_invalido(tmp_path):
    _projeto(tmp_path, nome="Nome Invalido!")
    with pytest.raises(ErroPacote) as exc:
        empacotar(str(tmp_path))
    assert "invalido" in str(exc.value).lower()


def test_empacotar_e_reproduzivel(tmp_path):
    """Dois pacotes do mesmo fonte tem o mesmo sha — senao o lock quebra."""
    _projeto(tmp_path)
    _, sha1, _, _ = empacotar(str(tmp_path))
    _, sha2, _, _ = empacotar(str(tmp_path))
    assert sha1 == sha2


# ─── Seguranca ─────────────────────────────────────────────

def test_extrair_recusa_caminho_que_escapa(tmp_path):
    """Um tarball com '../' nao pode escrever fora do destino."""
    from dataforge.packages import _extrair_seguro

    malicioso = tmp_path / "mal.tar.gz"
    vitima = tmp_path / "fora.txt"
    vitima.write_text("original", encoding="utf-8")

    with tarfile.open(malicioso, "w:gz") as tar:
        tar.add(str(vitima), arcname="../fora.txt")

    destino = tmp_path / "destino"
    destino.mkdir()
    with tarfile.open(malicioso) as tar:
        with pytest.raises(ErroPacote) as exc:
            _extrair_seguro(tar, str(destino))
    assert "fora do destino" in str(exc.value)


# ─── Resolucao de modulos pelo interpretador ───────────────

def _rodar(caminho):
    """Executa um .df e devolve a saida."""
    import io
    from contextlib import redirect_stdout
    from dataforge.interpreter import Interpreter
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    fonte = open(caminho, encoding="utf-8").read()
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, caminho), caminho), caminho)
    return saida.getvalue()


def test_adopt_encontra_pacote_instalado(tmp_path):
    (tmp_path / "forge.toml").write_text('[project]\nname = "app"\n', encoding="utf-8")
    pacote = tmp_path / "forge_modules" / "saudacao" / "src"
    pacote.mkdir(parents=True)
    (pacote / "main.df").write_text(
        'action ola(nome):\n    yield $"ola, {nome}"\n\nrelay ola\n', encoding="utf-8")
    (tmp_path / "forge_modules" / "saudacao" / "forge.toml").write_text(
        '[package]\nname = "saudacao"\nversion = "1.0.0"\nentry = "src/main.df"\n',
        encoding="utf-8")

    app = tmp_path / "src"
    app.mkdir()
    (app / "main.df").write_text(
        'adopt saudacao as S\nout S.ola("mundo")\n', encoding="utf-8")

    assert "ola, mundo" in _rodar(str(app / "main.df"))


def test_erro_de_import_menciona_forge_modules(tmp_path):
    from dataforge.errors import ImportError_

    (tmp_path / "main.df").write_text("adopt inexistente as X\n", encoding="utf-8")
    with pytest.raises(ImportError_) as exc:
        _rodar(str(tmp_path / "main.df"))
    assert "forge_modules" in str(exc.value)


# ─── Dependencias de pacote local ──────────────────────────
# 'resolver' so buscava transitivas de pacotes do registro. Um pacote
# instalado por caminho local ('dataforge add ../minha-lib') entrava
# sozinho, e quebrava no primeiro 'adopt' do que ele mesmo usa.

def test_dependencia_local_traz_as_suas(tmp_path):
    from dataforge.packages import Dependencia, resolver

    # a lib local declara que depende de 'ajudante'
    lib = tmp_path / "minha-lib"
    (lib / "src").mkdir(parents=True)
    (lib / "forge.toml").write_text(
        '[package]\nname = "minha-lib"\nversion = "1.0.0"\n'
        'entry = "src/main.df"\n\n[dependencies]\najudante = "^1.0.0"\n',
        encoding="utf-8")

    reg = RegistroFalso({"ajudante": _pkg({"1.0.0": {}, "1.2.0": {}})})
    plano = resolver([Dependencia("minha-lib", {"path": str(lib)})],
                     reg, raiz=str(tmp_path))

    assert "minha-lib" in plano
    assert "ajudante" in plano, "a dependencia da lib local ficou de fora"
    assert str(plano["ajudante"]["versao"]) == "1.2.0"


def test_pacote_local_sem_manifesto_nao_estoura(tmp_path):
    from dataforge.packages import Dependencia, resolver

    lib = tmp_path / "sem-toml"
    lib.mkdir()
    plano = resolver([Dependencia("sem-toml", {"path": str(lib)})],
                     RegistroFalso({}), raiz=str(tmp_path))
    assert list(plano) == ["sem-toml"]
