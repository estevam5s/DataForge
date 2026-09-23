"""Todo bloco `df` das páginas novas RODA — não só compila.

`tools/verificar_docs.py` confere que os blocos compilam. Compilar não
basta: um `assert` errado compila, uma chave com o nome errado compila,
e `Bench.medir(acao, 5)` compila e estoura na primeira execução. Foram
exatamente esses os defeitos que apareceram escrevendo estas páginas —
e cada um só apareceu executando.

Ficam de fora os blocos que dependem de outro arquivo (`adopt ./…`,
`adopt ../…`) e os que são o `tests/` de um projeto: esses são
montados e testados como projeto em `test_projetos_tipos.py`.

E os que pedem hardware ou um serviço de fora — uma placa Arduino, um
broker MQTT. Eles levam `title` começando por "precisa de", e são
**conferidos** por `tools/verificar_docs.py`, que os compila. A
alternativa seria escondê-los da documentação, e aí a página sobre
falar com uma placa não mostraria como se fala com uma placa.
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
           "dados_mais",
           "api_rest_mais",
           "telegram_mais",
           "dominio_mais",
           "estruturas_mais",
           "reativo_mais",
           "ffi_mais",
           "compilador_mais",
           "runtime_mais",
           "observabilidade_mais",
           "partida_mais",
           "abi_mais",
           "ecossistema_mais",
           "concorrencia_mais",
           "iot",
           "receitas_cli",
           "lavra_mais",
           "posse_mais",
           "concorrencia_extra"]


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
                titulo = b.get("title") or ""
                if titulo.startswith("tests/") or titulo.startswith("precisa de"):
                    continue
                # Um bloco que ENCERRA de proposito — 'Cli.erro' escreve
                # no stderr e sai com 1, e e assim que se mostra o que
                # ele faz. O titulo diz o codigo, e o teste COBRA esse
                # codigo: pular seria deixar de conferir justamente o
                # bloco que fala sobre codigo de saida.
                esperado = 0
                if titulo.startswith("encerra com "):
                    esperado = int(titulo.split()[-1])
                yield pytest.param(codigo, esperado,
                                   id=f"{p['href'].replace('/docs/', '')}#{i}")


@pytest.mark.parametrize("codigo,esperado", list(_blocos()))
def test_o_bloco_roda(codigo, esperado, tmp_path):
    arq = tmp_path / "bloco.df"
    arq.write_text(codigo + "\n", encoding="utf-8")
    ambiente = dict(os.environ, PYTHONPATH=RAIZ, NO_COLOR="1",
                    PATH=os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", ""))
    r = subprocess.run([sys.executable, "-m", "dataforge", "run", str(arq)],
                       cwd=tmp_path, capture_output=True, text=True, input="",
                       encoding="utf-8", errors="replace", timeout=300, env=ambiente)
    assert r.returncode == esperado, (r.stdout + r.stderr)[-2500:]


def test_ha_blocos_suficientes_para_valer():
    assert len(list(_blocos())) >= 80
