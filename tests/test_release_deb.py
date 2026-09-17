"""O .deb publicado tinha 1.194 bytes — e o que impede isso de voltar.

O gerador ja estava certo quando o problema foi visto: o pacote local
saia com 6,5 MB. O que estava errado era o RELEASE — a tag 'v1.0.0'
apontava para um commit anterior a correcao, e o CI empacotou com o
gerador velho. Tres travas, cada uma para um jeito de repetir o erro:

1. o workflow recusa uma tag que nao e a versao da linguagem — sem isso,
   'v1.0.1' num codigo que diz '1.0.0' publicaria 'dataforge_1.0.0_all.deb'
   debaixo da tag nova;
2. o gerador recusa terminar com um pacote pequeno demais para conter a
   linguagem;
3. o verificador de downloads tem piso POR ARQUIVO: 100 KB servem para
   separar um binario de uma pagina de erro, e nao separam um .deb inteiro
   de um .deb sem a biblioteca.
"""

import os
import re
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)


def _passo(nome_do_passo):
    """O corpo 'run:' de um passo do release.yml, pelo nome."""
    texto = open(os.path.join(RAIZ, ".github", "workflows", "release.yml"),
                 encoding="utf-8").read()
    achado = re.search(
        r"- name: " + re.escape(nome_do_passo) + r"\n\s+run: \|\n((?:\s{10,}.*\n|\s*\n)+)",
        texto)
    assert achado, f"o release.yml nao tem o passo '{nome_do_passo}'"
    linhas = achado.group(1).splitlines()
    recuo = min(len(l) - len(l.lstrip()) for l in linhas if l.strip())
    return "\n".join(l[recuo:] for l in linhas)


@pytest.mark.skipif(sys.platform.startswith("win"), reason="passo em bash")
@pytest.mark.parametrize("tag,deve_passar", [
    ("v{versao}", True),
    ("v9.9.9", False),
    ("{versao}", False),          # sem o 'v': o gatilho e 'v*', e o nome tem de bater
])
def test_o_release_recusa_tag_que_nao_e_a_versao_da_linguagem(tag, deve_passar):
    """Roda o passo de verdade, com a tag no ambiente, como o Actions faz."""
    from dataforge import __version__
    corpo = _passo("a tag e a versao da linguagem")
    r = subprocess.run(
        ["bash", "-c", corpo], cwd=RAIZ, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        env={**os.environ, "GITHUB_REF_NAME": tag.format(versao=__version__),
             "PYTHONPATH": RAIZ})
    assert (r.returncode == 0) is deve_passar, r.stdout + r.stderr


def test_o_passo_da_versao_roda_antes_de_construir():
    """Uma trava que roda depois da construcao gasta os quatro runners antes."""
    texto = open(os.path.join(RAIZ, ".github", "workflows", "release.yml"),
                 encoding="utf-8").read()
    assert re.search(r"needs:\s*\[?\s*versao", texto), (
        "os jobs de construcao precisam depender do job que confere a versao")


def test_o_gerador_recusa_um_deb_pequeno_demais(tmp_path):
    sys.path.insert(0, os.path.join(RAIZ, "packaging"))
    import gerar_pacotes

    pequeno = tmp_path / "dataforge_1.0.0_all.deb"
    pequeno.write_bytes(b"!<arch>\n" + b"0" * 1186)          # os 1.194 bytes
    with pytest.raises(SystemExit) as erro:
        gerar_pacotes.conferir_tamanho(str(pequeno))
    assert "1194" in str(erro.value) or "1.194" in str(erro.value)

    grande = tmp_path / "ok.deb"
    grande.write_bytes(b"!<arch>\n" + b"0" * gerar_pacotes.TAMANHO_MINIMO_DO_DEB)
    gerar_pacotes.conferir_tamanho(str(grande))


def test_o_verificador_de_downloads_tem_piso_por_arquivo():
    sys.path.insert(0, os.path.join(RAIZ, "scripts"))
    import verificar_downloads as v

    deb = "dataforge_1.0.0_all.deb"
    ok, motivo = v.avaliar(deb, 1194, "application/octet-stream")
    assert ok is False and "KB" in motivo
    # 300 KB passava pelo piso geral de 100 KB, e nao e uma linguagem
    assert v.avaliar(deb, 300 * 1024, "application/octet-stream")[0] is False
    assert v.avaliar(deb, 6_535_938, "application/octet-stream")[0] is True
    # uma pagina de erro continua recusada em qualquer arquivo
    assert v.avaliar("PKGBUILD", 10_000, "text/html")[0] is False
    # e o PKGBUILD, que e texto pequeno por natureza, nao tem piso de binario
    assert v.avaliar("PKGBUILD", 1740, "text/plain")[0] is True


@pytest.mark.skipif(sys.platform.startswith("win"), reason="script em bash")
def test_o_script_de_publicacao_e_bash_valido_e_nao_fixa_versao():
    caminho = os.path.join(RAIZ, "scripts", "publicar_release.sh")
    assert subprocess.run(["bash", "-n", caminho]).returncode == 0
    texto = open(caminho, encoding="utf-8").read()
    assert not re.search(r"\b\d+\.\d+\.\d+\b", texto.replace("1.194", "")), (
        "a versao sai do codigo; escrita no script, ela envelhece")


@pytest.mark.skipif(sys.platform.startswith("win"), reason="script em bash")
def test_o_script_de_publicacao_para_sem_gh_autenticado(tmp_path):
    """Sem autenticacao, ele diz o comando — e nao marca tag nenhuma."""
    falso = tmp_path / "gh"
    falso.write_text("#!/bin/sh\nexit 1\n")
    falso.chmod(0o755)
    r = subprocess.run(
        ["bash", os.path.join(RAIZ, "scripts", "publicar_release.sh"), "--executar"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
        env={**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}",
             "PY": sys.executable})
    assert r.returncode != 0
    assert "gh auth login" in r.stdout
