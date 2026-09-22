"""Todo bloco `df` das páginas novas RODA — não só compila.

`tools/verificar_docs.py` confere que os blocos compilam. Compilar não
basta: um `assert` errado compila, uma chave com o nome errado compila,
e `Bench.medir(acao, 5)` compila e estoura na primeira execução. Foram
exatamente esses os defeitos que apareceram escrevendo estas páginas —
e cada um só apareceu executando.

Ficam de fora os blocos que dependem de outro arquivo (`adopt ./…`,
`adopt ../…`) e os que são o `tests/` de um projeto: esses são
montados e testados como projeto em `test_projetos_tipos.py`.
"""
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "site", "scripts"))

MODULOS = ["modulos_avancado", "bibliotecas_avancado", "testes_avancado",
           "devops_avancado", "gramatica_doc", "seguranca_avancado",
           "primeiros_passos_avancado", "fundamentos_avancado",
           "big_o_avancado", "modulos_mais", "bibliotecas_mais",
           "dados_mais"]


def _blocos():
    for nome in MODULOS:
        mod = __import__(f"conteudo.{nome}", fromlist=["PAGINAS"])
        for p in mod.PAGINAS:
            for i, b in enumerate(p["blocos"]):
                if b.get("lang") != "df" or "code" not in b:
                    continue
                codigo = b["code"]
                # So uma linha de 'adopt' relativo de verdade — um comentario
                # que CITA um 'adopt ./' nao impede o bloco de rodar.
                if any(l.strip().startswith(("adopt ./", "adopt ../"))
                       for l in codigo.splitlines()):
                    continue
                if (b.get("title") or "").startswith("tests/"):
                    continue
                yield pytest.param(codigo, id=f"{p['href'].replace('/docs/', '')}#{i}")


@pytest.mark.parametrize("codigo", list(_blocos()))
def test_o_bloco_roda(codigo, tmp_path):
    arq = tmp_path / "bloco.df"
    arq.write_text(codigo + "\n", encoding="utf-8")
    ambiente = dict(os.environ, PYTHONPATH=RAIZ, NO_COLOR="1",
                    PATH=os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", ""))
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", str(arq)],
                       cwd=tmp_path, capture_output=True, text=True, input="",
                       encoding="utf-8", errors="replace", timeout=300, env=ambiente)
    assert r.returncode == 0, (r.stdout + r.stderr)[-2500:]


def test_ha_blocos_suficientes_para_valer():
    assert len(list(_blocos())) >= 80
