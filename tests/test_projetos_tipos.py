"""Os vinte e dois tipos de projeto da documentação, montados e testados.

Cada página de `/docs/projetos/<tipo>` mostra um `forge.toml`, um núcleo
em `src/` e um teste em `tests/`. Conferir que o núcleo **compila** não
diz nada sobre o projeto: o teste importa o núcleo por caminho relativo,
e um nome errado ali só aparece montando a pasta de verdade.

Por isso este arquivo faz o que quem copia a página faria: escreve os
três arquivos numa pasta, roda o núcleo com `dataforge run` e a suíte
com `dataforge test`. Um projeto de exemplo que não roda ensina a
desconfiar de todos os outros.
"""
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))

from conteudo import projetos_tipos  # noqa: E402


def _partes(pagina):
    toml = nucleo = teste = None
    for b in pagina["blocos"]:
        if "code" not in b:
            continue
        titulo = b.get("title") or ""
        if b.get("lang") == "toml" and titulo == "forge.toml":
            toml = b["code"]
        elif b.get("lang") == "df" and titulo.startswith("src/"):
            nucleo = (titulo, b["code"])
        elif b.get("lang") == "df" and titulo.startswith("tests/"):
            teste = (titulo, b["code"])
    return toml, nucleo, teste


def _rodar(argumentos, pasta):
    ambiente = dict(os.environ, PYTHONPATH=RAIZ, DATAFORGE_SEM_TROCA="1",
                    NO_COLOR="1")
    return subprocess.run(
        [sys.executable, "-m", "dataforge", *argumentos], cwd=pasta,
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=300, env=ambiente)


PAGINAS = projetos_tipos.TIPOS


def test_sao_vinte_e_dois_tipos():
    assert len(PAGINAS) == 22
    slugs = [p["href"] for p in PAGINAS]
    assert len(set(slugs)) == len(slugs), "dois tipos com o mesmo endereço"


def test_toda_pagina_tem_manifesto_nucleo_e_teste():
    for p in PAGINAS:
        toml, nucleo, teste = _partes(p)
        assert toml, f"{p['href']} sem forge.toml"
        assert nucleo, f"{p['href']} sem núcleo em src/"
        assert teste, f"{p['href']} sem teste em tests/"
        assert "assert" in nucleo[1], f"{p['href']}: o núcleo não confere nada"


@pytest.mark.parametrize("pagina", PAGINAS, ids=[p["href"].rsplit("/", 1)[-1] for p in PAGINAS])
def test_o_projeto_montado_roda_e_passa_nos_testes(pagina, tmp_path):
    toml, (arq_nucleo, nucleo), (arq_teste, teste) = _partes(pagina)
    (tmp_path / "forge.toml").write_text(toml + "\n", encoding="utf-8")
    for nome, texto in ((arq_nucleo, nucleo), (arq_teste, teste)):
        destino = tmp_path / nome
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto + "\n", encoding="utf-8")

    r = _rodar(["run", arq_nucleo], tmp_path)
    assert r.returncode == 0, f"o núcleo falhou:\n{(r.stdout + r.stderr)[-1500:]}"

    r = _rodar(["test", "tests/"], tmp_path)
    saida = r.stdout + r.stderr
    assert r.returncode == 0, f"a suíte do projeto falhou:\n{saida[-2000:]}"
    assert "passaram" in saida, f"nenhum teste rodou:\n{saida[-800:]}"


def test_o_indice_lista_todos_os_tipos_e_sai_da_mesma_lista():
    indice = projetos_tipos.PAGINAS[0]
    assert indice["href"] == "/docs/projetos"
    texto = str(indice["blocos"])
    for t in PAGINAS:
        assert t["href"] in texto, f"{t['href']} fora do índice"
