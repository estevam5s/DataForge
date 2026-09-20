"""Publicar pelo terminal: o token, e o que ele não pode fazer.

O `dataforge publish --registry=<pasta>` escreve num índice estático e
espera um PR. Serve para um registro interno de empresa, e não serve
para a comunidade: ninguém abre um PR para publicar um pacote.

`--remoto` é o caminho que um programador realmente usa, e ele exige
uma credencial que viva fora do navegador. Os testes aqui cobram o lado
do cliente — o do banco está em `supabase/07_tokens_de_publicacao.sql`,
e foi verificado contra o serviço de verdade.
"""

import json
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge import registro_remoto as reg  # noqa: E402


def test_a_variavel_de_ambiente_vence_o_arquivo(tmp_path, monkeypatch):
    """É como a CI passa a credencial sem escrever nada em disco.

    Um runner que precisasse gravar o token num arquivo o deixaria no
    cache da build — e o cache de build costuma ser compartilhado entre
    projetos.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("DATAFORGE_TOKEN", "dfp_doambiente")
    assert reg.ler_token() == "dfp_doambiente"

    reg.gravar_token("dfp_doarquivo")
    assert reg.ler_token() == "dfp_doambiente", (
        "o arquivo venceu a variável — na CI isso usaria a credencial errada")

    monkeypatch.delenv("DATAFORGE_TOKEN")
    assert reg.ler_token() == "dfp_doarquivo"


def test_o_arquivo_de_credencial_nao_e_legivel_por_outros(tmp_path, monkeypatch):
    """Modo 600.

    Um arquivo de credencial legível por outros usuários da máquina é
    uma credencial compartilhada sem que ninguém tenha decidido isso.
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("DATAFORGE_TOKEN", raising=False)
    caminho = reg.gravar_token("dfp_segredo")

    if os.name == "nt":
        # No Windows o modo não é a pergunta: 'chmod' ali só mexe no
        # somente-leitura, e um arquivo 0o666 pode estar perfeitamente
        # restrito por ACL. Quem responde é o 'icacls'.
        import subprocess

        try:
            r = subprocess.run(["icacls", caminho], capture_output=True,
                               text=True, timeout=20,
                               encoding="utf-8", errors="replace")
        except (OSError, subprocess.SubprocessError):      # pragma: no cover
            pytest.skip("o 'icacls' não respondeu nesta máquina")
        assert r.returncode == 0, r.stdout + r.stderr
        # 'BUILTIN\\Us' cobre 'Users' e 'Usuários' de uma vez: a saída do
        # 'icacls' vem na página de código do console, e um acento lido
        # como UTF-8 chega trocado — comparar a palavra inteira falharia
        # em português e passaria calado.
        abertos = [linha for linha in r.stdout.splitlines()
                   if "Everyone" in linha or "Todos" in linha
                   or "BUILTIN\\Us" in linha]
        assert not abertos, (
            "a credencial está ao alcance de outras contas da máquina:\n"
            + "\n".join(abertos))
        return

    modo = os.stat(caminho).st_mode & 0o777
    assert modo == 0o600, f"o arquivo está {oct(modo)}, e devia estar 0o600"


def test_esquecer_apaga_o_arquivo(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("DATAFORGE_TOKEN", raising=False)
    reg.gravar_token("dfp_x")
    assert reg.esquecer_token() is True
    assert reg.ler_token() is None
    assert reg.esquecer_token() is False


def test_o_token_nunca_entra_num_arquivo_do_projeto():
    """Ele vai para o HOME, e não para a pasta do projeto.

    Um arquivo de credencial dentro do repositório acaba commitado — é
    a forma mais comum de vazar credencial de registro de pacote que
    existe.
    """
    caminho = reg.caminho_das_credenciais()
    assert caminho.startswith(os.path.expanduser("~")), caminho
    assert RAIZ not in caminho, (
        "as credenciais estão dentro do repositório, e vão acabar commitadas")


def test_a_chave_publica_embutida_nao_e_a_privilegiada():
    """A `anon` vai no bundle do site; a `service_role` ignora RLS.

    Embutir a primeira no CLI não expõe nada novo — o navegador de
    qualquer visitante já a enxerga. Embutir a segunda daria a quem
    baixasse o pacote acesso total ao banco.
    """
    chave = reg.CHAVE_PADRAO
    assert chave, "sem chave, o CLI não fala com o registro"

    # O papel vem dentro do próprio JWT, em texto.
    import base64
    corpo = chave.split(".")[1]
    corpo += "=" * (-len(corpo) % 4)
    dados = json.loads(base64.urlsafe_b64decode(corpo))
    assert dados.get("role") == "anon", (
        f"a chave embutida tem papel '{dados.get('role')}' — só 'anon' pode "
        f"ser distribuída")


def test_nenhuma_chave_privilegiada_no_codigo_distribuido():
    """Uma trava sobre o CÓDIGO, e não sobre o comportamento.

    Ela procura a CHAVE, e não a palavra: a primeira versão deste teste
    buscava `service_role` como texto e acusou a própria docstring que
    explica por que ela não pode estar aqui. Um teste que reprova o
    comentário sobre a regra ensina a apagar o comentário.

    O que se procura é um JWT de verdade cujo `role` não seja `anon` —
    decodificado, e não adivinhado pelo nome da variável.
    """
    import base64
    import json as _json
    import re

    # Um JWT: três blocos base64url separados por ponto.
    JWT = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}")

    suspeitos = []
    for pasta, _, arquivos in os.walk(os.path.join(RAIZ, "dataforge")):
        for nome in arquivos:
            if not nome.endswith(".py"):
                continue
            caminho = os.path.join(pasta, nome)
            texto = open(caminho, encoding="utf-8", errors="replace").read()
            for achado in JWT.findall(texto):
                corpo = achado.split(".")[1]
                corpo += "=" * (-len(corpo) % 4)
                try:
                    dados = _json.loads(base64.urlsafe_b64decode(corpo))
                except Exception:                       # noqa: BLE001
                    continue
                papel = dados.get("role")
                if papel and papel != "anon":
                    suspeitos.append(
                        f"{os.path.relpath(caminho, RAIZ)}: papel '{papel}'")

    assert not suspeitos, (
        "há chave privilegiada em código distribuído — ela ignora a RLS, e "
        "quem baixar o pacote fica com acesso total ao banco:\n  "
        + "\n  ".join(suspeitos))
