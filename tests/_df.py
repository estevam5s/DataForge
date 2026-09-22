"""Rodar um programa DataForge de dentro de um teste, como um usuário roda."""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rodar(tmp_path, fonte, nome="p.df", **env):
    arquivo = tmp_path / nome
    arquivo.write_text(fonte, encoding="utf-8")
    return subprocess.run([sys.executable, "-m", "dataforge", "run", str(arquivo)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=RAIZ,
                          env=dict(os.environ, NO_COLOR="1", **env))
