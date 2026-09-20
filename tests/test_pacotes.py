"""Testes do gerenciador de pacotes (dataforge add/install/remove/pack)."""

import json
import os
import subprocess
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


# ═══════════════════════════════════════════════════════════
#  O lockfile passa a ser LIDO
# ═══════════════════════════════════════════════════════════

def _registro_com_duas_versoes(tmp_path):
    """Um registro de mentira com 'tabela' em 1.0.0 e 1.1.0.

    O conteúdo das duas é o mesmo tarball de propósito: o que está
    sendo exercitado é a RESOLUÇÃO, e um conteúdo diferente só
    acrescentaria ruído.
    """
    import hashlib
    import json
    import shutil

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    origem = os.path.join(raiz, "site", "public", "registry")
    if not os.path.isfile(os.path.join(origem, "index.json")):
        pytest.skip("o registro do site não está neste checkout")

    destino = str(tmp_path / "reg")
    shutil.copytree(origem, destino)

    indice = os.path.join(destino, "index.json")
    dados = json.load(open(indice, encoding="utf-8"))
    pacote = dados["pacotes"]["tabela"]
    antiga = pacote["versoes"]["1.0.0"]
    tarball = os.path.join(destino, "pacotes", antiga["arquivo"])
    novo = "tabela-1.1.0.tar.gz"
    shutil.copy(tarball, os.path.join(destino, "pacotes", novo))
    pacote["versoes"]["1.1.0"] = {
        "arquivo": novo,
        "sha256": hashlib.sha256(open(tarball, "rb").read()).hexdigest(),
        "dependencias": {}, "dataforge": ">=4.0",
    }
    json.dump(dados, open(indice, "w", encoding="utf-8"), ensure_ascii=False)
    return destino, antiga["sha256"]


def _projeto_travado(tmp_path, faixa="^1.0.0"):
    pasta = tmp_path / "proj"
    pasta.mkdir()
    (pasta / "forge.toml").write_text(
        '[project]\nname = "teste-lock"\nversion = "0.1.0"\n\n'
        f'[dependencies]\ntabela = "{faixa}"\n', encoding="utf-8")
    return pasta


def _rodar_no_projeto(pasta, registro, *argumentos):
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ambiente = {**os.environ,
                "PYTHONPATH": raiz,
                "DATAFORGE_REGISTRY": f"file://{registro}",
                "NO_COLOR": "1"}
    return subprocess.run([sys.executable, "-m", "dataforge", *argumentos],
                          cwd=str(pasta), env=ambiente, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=180)


def _travado(pasta):
    import json
    return json.load(open(pasta / "forge.lock", encoding="utf-8")
                     )["pacotes"]["tabela"]["versao"]


def test_o_install_HONRA_o_forge_lock(tmp_path):
    """O lockfile era escrito e nunca lido.

    Ele é versionado, carrega o sha256 de cada pacote — e nenhum
    caminho de instalação o consultava: `_sincronizar` sempre resolvia
    a faixa do zero e **reescrevia** o arquivo. Duas pessoas clonando o
    mesmo projeto em dias diferentes recebiam versões diferentes, e a
    "verificação de integridade" conferia um download contra ele
    mesmo.

    Um lockfile que ninguém lê não trava nada.
    """
    registro, sha_antigo = _registro_com_duas_versoes(tmp_path)
    pasta = _projeto_travado(tmp_path)

    # Sem lock, a faixa manda: a mais nova.
    primeira = _rodar_no_projeto(pasta, registro, "install")
    assert primeira.returncode == 0, primeira.stdout + primeira.stderr
    assert _travado(pasta) == "1.1.0"

    # Agora o lock fixa a 1.0.0, como se um colega tivesse instalado
    # antes de a 1.1.0 existir.
    import json
    lock = json.load(open(pasta / "forge.lock", encoding="utf-8"))
    lock["pacotes"]["tabela"] = {"versao": "1.0.0", "fonte": "registro",
                                 "sha256": sha_antigo, "dependencias": {}}
    json.dump(lock, open(pasta / "forge.lock", "w", encoding="utf-8"))

    segunda = _rodar_no_projeto(pasta, registro, "install")
    assert segunda.returncode == 0, segunda.stdout + segunda.stderr
    assert _travado(pasta) == "1.0.0", (
        "o install voltou a ignorar o lock — quem clona o projeto amanhã "
        "recebe outra árvore")
    assert "1.0.0" in segunda.stdout


def test_o_update_MOVE_o_que_o_install_respeita(tmp_path):
    """A outra metade: sem ela, a única forma de subir uma dependência
    seria apagar o lockfile — e aí sobe tudo de uma vez, que é o
    oposto de uma atualização controlada."""
    registro, sha_antigo = _registro_com_duas_versoes(tmp_path)
    pasta = _projeto_travado(tmp_path)
    _rodar_no_projeto(pasta, registro, "install")

    import json
    lock = json.load(open(pasta / "forge.lock", encoding="utf-8"))
    lock["pacotes"]["tabela"] = {"versao": "1.0.0", "fonte": "registro",
                                 "sha256": sha_antigo, "dependencias": {}}
    json.dump(lock, open(pasta / "forge.lock", "w", encoding="utf-8"))

    r = _rodar_no_projeto(pasta, registro, "update")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _travado(pasta) == "1.1.0", r.stdout
    # O relatório diz de onde para onde: um update mudo não dá para
    # revisar antes de commitar o lock.
    assert "1.0.0" in r.stdout and "1.1.0" in r.stdout


def test_o_install_PARA_quando_o_conteudo_de_uma_versao_muda(tmp_path):
    """Um tarball trocado no registro é o ataque que o lock existe para
    impedir — e até aqui ele passava batido, porque o sha era gravado e
    nunca comparado."""
    registro, _sha = _registro_com_duas_versoes(tmp_path)
    pasta = _projeto_travado(tmp_path)
    _rodar_no_projeto(pasta, registro, "install")

    import json
    lock = json.load(open(pasta / "forge.lock", encoding="utf-8"))
    lock["pacotes"]["tabela"]["sha256"] = "0" * 64
    json.dump(lock, open(pasta / "forge.lock", "w", encoding="utf-8"))

    r = _rodar_no_projeto(pasta, registro, "install")
    assert r.returncode == 1, r.stdout
    assert "NAO e o mesmo pacote" in r.stdout or "não é o mesmo" in r.stdout
    # A mensagem diz o que fazer, e não só que deu errado.
    assert "dataforge update" in r.stdout


def test_a_faixa_do_forge_toml_VENCE_o_lock(tmp_path):
    """O manifesto é a intenção; o lock é a memória da última resolução.

    Quem sobe o requisito no `forge.toml` está pedindo outra versão —
    e o lock não pode segurar o projeto numa que a faixa nova já não
    admite.
    """
    registro, sha_antigo = _registro_com_duas_versoes(tmp_path)
    pasta = _projeto_travado(tmp_path, faixa="^1.0.0")
    _rodar_no_projeto(pasta, registro, "install")

    import json
    lock = json.load(open(pasta / "forge.lock", encoding="utf-8"))
    lock["pacotes"]["tabela"] = {"versao": "1.0.0", "fonte": "registro",
                                 "sha256": sha_antigo, "dependencias": {}}
    json.dump(lock, open(pasta / "forge.lock", "w", encoding="utf-8"))

    (pasta / "forge.toml").write_text(
        '[project]\nname = "teste-lock"\nversion = "0.1.0"\n\n'
        '[dependencies]\ntabela = ">=1.1.0"\n', encoding="utf-8")

    r = _rodar_no_projeto(pasta, registro, "install")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _travado(pasta) == "1.1.0", (
        "o lock segurou uma versão que a faixa declarada já não admite")


def test_um_auxiliar_novo_nao_pode_SOMBREAR_um_que_ja_existe():
    """Duas funções com o mesmo nome no mesmo módulo: a última vence.

    Aconteceu escrevendo os testes acima: `_projeto` e `_rodar` já
    existiam neste arquivo, com outra assinatura, e as definições novas
    passaram a valer **para os testes antigos também** — seis
    reprovaram de uma vez, com erros que falavam de argumento
    inesperado em testes que ninguém tinha tocado.

    O Python não avisa. Esta trava avisa.
    """
    import ast

    caminho = os.path.abspath(__file__)
    arvore = ast.parse(open(caminho, encoding="utf-8").read())
    nomes = [no.name for no in arvore.body
             if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))]

    repetidos = sorted({n for n in nomes if nomes.count(n) > 1})
    assert not repetidos, (
        "função definida duas vezes no módulo — a segunda apaga a "
        f"primeira, e os testes que chamavam a primeira mudam de "
        f"comportamento em silêncio: {repetidos}")
