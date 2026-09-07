"""
DataForge Test Runner — `dataforge test`

Descobre e executa arquivos de teste, agrupando por suíte e reportando o que
falhou com a mensagem, a linha e a pilha de chamadas.

Convenções de descoberta
------------------------
* arquivos `*_test.df`, `test_*.df` ou qualquer `.df` dentro de `tests/`
* toda ação cujo nome começa com `test_` vira um caso de teste
* um arquivo sem ações `test_` é executado inteiro como um único caso
  (os `assert` de dentro dele valem como verificações)

Ganchos opcionais, chamados quando existem:
`setup_all`, `teardown_all`, `setup`, `teardown`.
"""

import glob
import io
import os
import time
from contextlib import redirect_stdout

from .errors import DataForgeError
from .interpreter import DFAction, Interpreter
from .lexer import tokenize
from .parser import parse

VERDE, VERMELHO, AMARELO, CINZA, RESET = (
    "\033[1;32m", "\033[1;31m", "\033[1;33m", "\033[0;90m", "\033[0m")


class Resultado:
    __slots__ = ('arquivo', 'nome', 'status', 'mensagem', 'duracao', 'erro', 'saida')

    def __init__(self, arquivo, nome, status, mensagem="", duracao=0.0,
                 erro=None, saida=""):
        self.arquivo = arquivo
        self.nome = nome
        self.status = status        # 'pass' | 'fail' | 'error'
        self.mensagem = mensagem
        self.duracao = duracao
        self.erro = erro
        self.saida = saida


def descobrir(alvo="."):
    """Lista os arquivos de teste sob um caminho."""
    if os.path.isfile(alvo):
        return [alvo]

    encontrados = []
    for padrao in ("**/*_test.df", "**/test_*.df", "**/tests/**/*.df",
                   "**/testes/**/*.df"):
        encontrados.extend(glob.glob(os.path.join(alvo, padrao), recursive=True))
    unicos = sorted(set(os.path.normpath(f) for f in encontrados))
    return [f for f in unicos if os.path.isfile(f)]


def _acoes_de_teste(interp):
    return {nome: valor for nome, valor in interp.global_env.variables.items()
            if nome.startswith("test_") and isinstance(valor, DFAction)}


def _chamar(interp, acao):
    no = type('_N', (), {'line': 0, 'column': 0})()
    return interp._call_action(acao, [], {}, no, interp.global_env)


def executar_arquivo(caminho, verboso=False, filtro=""):
    """Executa um arquivo de teste e devolve a lista de resultados."""
    resultados = []
    fonte = open(caminho, encoding="utf-8").read()

    try:
        arvore = parse(tokenize(fonte, caminho), caminho)
    except DataForgeError as e:
        return [Resultado(caminho, "<parse>", "error", e.message, erro=e)]

    interp = Interpreter()
    buffer = io.StringIO()
    inicio = time.perf_counter()
    try:
        with redirect_stdout(buffer):
            interp.run(arvore, filename=caminho)
    except DataForgeError as e:
        return [Resultado(caminho, "<módulo>", "fail", e.message,
                          time.perf_counter() - inicio, e, buffer.getvalue())]

    testes = _acoes_de_teste(interp)

    # Arquivo sem ações test_: o próprio arquivo é o caso.
    if not testes:
        return [Resultado(caminho, os.path.basename(caminho), "pass", "",
                          time.perf_counter() - inicio, saida=buffer.getvalue())]

    ganchos = interp.global_env.variables
    for gancho in ("setup_all",):
        if isinstance(ganchos.get(gancho), DFAction):
            with redirect_stdout(io.StringIO()):
                _chamar(interp, ganchos[gancho])

    for nome, acao in sorted(testes.items()):
        if filtro and filtro not in nome:
            continue
        marca = time.perf_counter()
        saida = io.StringIO()
        try:
            with redirect_stdout(saida):
                if isinstance(ganchos.get("setup"), DFAction):
                    _chamar(interp, ganchos["setup"])
                _chamar(interp, acao)
                if isinstance(ganchos.get("teardown"), DFAction):
                    _chamar(interp, ganchos["teardown"])
            resultados.append(Resultado(caminho, nome, "pass", "",
                                        time.perf_counter() - marca,
                                        saida=saida.getvalue()))
        except DataForgeError as e:
            resultados.append(Resultado(caminho, nome, "fail", e.message,
                                        time.perf_counter() - marca, e,
                                        saida.getvalue()))
        except Exception as e:  # falha inesperada no runtime
            resultados.append(Resultado(caminho, nome, "error", str(e),
                                        time.perf_counter() - marca, None,
                                        saida.getvalue()))

    for gancho in ("teardown_all",):
        if isinstance(ganchos.get(gancho), DFAction):
            with redirect_stdout(io.StringIO()):
                _chamar(interp, ganchos[gancho])

    return resultados


def executar(alvo=".", verboso=False, filtro="", cor=True, parar_no_primeiro=False):
    """Executa todos os testes sob um alvo. Devolve (resultados, ok)."""
    def tinta(t, c):
        return f"{c}{t}{RESET}" if cor else t

    arquivos = descobrir(alvo)
    if not arquivos:
        print(tinta(f"Nenhum arquivo de teste encontrado em '{alvo}'.", AMARELO))
        print(f"{CINZA if cor else ''}Procuro por *_test.df, test_*.df "
              f"ou .df dentro de tests/.{RESET if cor else ''}")
        return [], True

    todos = []
    inicio = time.perf_counter()

    for arquivo in arquivos:
        resultados = executar_arquivo(arquivo, verboso, filtro)
        if not resultados:
            continue
        todos.extend(resultados)

        passaram = sum(1 for r in resultados if r.status == "pass")
        falharam = len(resultados) - passaram
        cabecalho = os.path.relpath(arquivo)
        estado = tinta("✓", VERDE) if falharam == 0 else tinta("✗", VERMELHO)
        print(f"{estado} {cabecalho} {CINZA if cor else ''}"
              f"({passaram}/{len(resultados)}){RESET if cor else ''}")

        for r in resultados:
            if r.status == "pass":
                if verboso:
                    print(f"    {tinta('ok', VERDE)}   {r.nome} "
                          f"{CINZA if cor else ''}{r.duracao * 1000:.1f}ms{RESET if cor else ''}")
            else:
                print(f"    {tinta('FALHOU', VERMELHO)} {r.nome}")
                print(f"      {r.mensagem}")
                if r.erro is not None and getattr(r.erro, 'line', 0):
                    print(f"      em {cabecalho}:{r.erro.line}")
                    for quadro in reversed(getattr(r.erro, 'stack', []) or []):
                        print(f"        via {quadro.name} (linha {quadro.line})")
                if verboso and r.saida.strip():
                    for linha in r.saida.strip().splitlines():
                        print(f"      {CINZA if cor else ''}| {linha}{RESET if cor else ''}")
                if parar_no_primeiro:
                    break
        if parar_no_primeiro and falharam:
            break

    decorrido = time.perf_counter() - inicio
    passaram = sum(1 for r in todos if r.status == "pass")
    falharam = len(todos) - passaram

    print()
    resumo = f"{passaram} passaram"
    if falharam:
        resumo += f", {tinta(str(falharam) + ' falharam', VERMELHO)}"
    print(f"{resumo} em {len(arquivos)} arquivo(s) — {decorrido:.2f}s")
    if falharam == 0 and todos:
        print(tinta("Tudo verde.", VERDE))
    return todos, falharam == 0
