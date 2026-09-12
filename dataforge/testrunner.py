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
from .caminhos import curto as _curto

from .errors import DataForgeError
from .interpreter import DFAction, Interpreter
from .lexer import tokenize
from .parser import parse

VERDE, VERMELHO, AMARELO, CINZA, RESET = (
    "\033[1;32m", "\033[1;31m", "\033[1;33m", "\033[0;90m", "\033[0m")
CIANO, BRANCO = "\033[1;36m", "\033[1;37m"


class Resultado:
    __slots__ = ('arquivo', 'nome', 'status', 'mensagem', 'duracao', 'erro', 'saida')

    def __init__(self, arquivo, nome, status, mensagem="", duracao=0.0,
                 erro=None, saida=""):
        self.arquivo = arquivo
        self.nome = nome
        # 'pass' | 'fail' | 'error' | 'skip'
        #
        # 'skip' existe por causa do 'trial … pending': o Crucible o
        # conta separado e nao o chama de falha. Sem este estado ele
        # caia em "tudo que nao passou falhou", e um trial marcado
        # como pendente — que e quem escreveu dizendo "ainda nao" —
        # deixava a suite vermelha.
        self.status = status
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

    # 'forge_modules/' e de terceiro. Rodar os testes das dependencias
    # junto com os seus infla a contagem — um projeto com 13 testes
    # relatava 89 — e faz a sua suite ficar vermelha quando a falha e
    # de uma biblioteca que voce nao escreveu.
    de_fora = os.sep + "forge_modules" + os.sep
    return [f for f in unicos
            if os.path.isfile(f) and de_fora not in os.sep + f]


def _resultados_do_crucible(interp, caminho, inicio, buffer):
    """Roda as suites que o arquivo registrou, e devolve um caso cada.

    `None` quando o arquivo nao registrou suite nenhuma — e ai o fluxo
    normal segue.

    O registro e por PROCESSO, e `reiniciar_por_execucao` o zera a cada
    interpretador: sem isso o segundo arquivo veria os trials do
    primeiro, e a falha de um reapareceria no relatorio do outro.
    """
    try:
        from .stdlib.crucible import REGISTRO
    except ImportError:                                 # pragma: no cover
        return None

    suites = list(getattr(REGISTRO.raiz, "filhas", ()) or ())
    trials = list(getattr(REGISTRO.raiz, "trials", ()) or ())
    if not suites and not trials:
        return None

    modulo = interp.modules.get("Crucible") or interp.modules.get(
        "Arcane.Crucible")
    rodar = (modulo or {}).get("run")
    if not callable(rodar):
        return None

    saida = io.StringIO()
    try:
        with redirect_stdout(saida):
            resumo = rodar({"capturar": True})
    except DataForgeError as erro:
        return [Resultado(caminho, "<crucible>", "fail", erro.message,
                          time.perf_counter() - inicio, erro,
                          buffer.getvalue() + saida.getvalue())]

    return _do_resumo(resumo, caminho, inicio, buffer.getvalue())


def _do_resumo(resumo, caminho, inicio, saida_do_arquivo):
    """O resumo do Crucible virando `Resultado`, um por trial.

    Um por trial, e nao um por arquivo: o relatorio precisa dizer QUAL
    trial caiu, e o total precisa ser o numero de testes de verdade —
    era o que fazia "30 passaram" num projeto com 60 trials.
    """
    from .stdlib.crucible import ArcaneCrucible

    executor = ArcaneCrucible._ultimo
    decorrido = time.perf_counter() - inicio
    saidas = []

    # Os nomes vem de 'crucible.Resultado': 'estado' com os valores
    # 'passou'/'falhou'/'erro'/'pendente'/'ignorado', e 'caminho' com
    # "suite > trial". Adivinhar ('situacao', 'ms') nao daria erro —
    # 'getattr' com padrao devolveria "pass" para TUDO, e um trial
    # quebrado apareceria verde. Foi o primeiro jeito que escrevi.
    from .stdlib.crucible import ERRO, FALHOU, IGNORADO, PENDENTE

    traduz = {FALHOU: "fail", ERRO: "fail",
              PENDENTE: "skip", IGNORADO: "skip"}

    for caso in getattr(executor, "resultados", ()) or ():
        estado = traduz.get(getattr(caso, "estado", ""), "pass")
        mensagem = getattr(caso, "motivo", "") or ""
        erro = getattr(caso, "erro", None)
        if not mensagem and erro is not None:
            mensagem = getattr(erro, "message", None) or str(erro)
        saidas.append(Resultado(
            caminho, getattr(caso, "caminho", "<trial>"), estado,
            mensagem, getattr(caso, "duracao", 0.0),
            erro=erro, saida=getattr(caso, "saida", "") or saida_do_arquivo))

    if saidas:
        return saidas

    # O executor nao expos os casos: nao inventar um verde. Um unico
    # resultado que reflete o resumo, que e o que se sabe.
    total = (resumo or {}).get("total", 0)
    falhas = (resumo or {}).get("falhou", 0)
    return [Resultado(
        caminho, os.path.basename(caminho),
        "fail" if falhas else "pass",
        f"{falhas} de {total} trial(s) falharam" if falhas else "",
        decorrido, saida=saida_do_arquivo)]


def _acoes_de_teste(interp):
    return {nome: valor for nome, valor in interp.global_env.variables.items()
            if nome.startswith("test_") and isinstance(valor, DFAction)}


def _chamar(interp, acao):
    no = type('_N', (), {'line': 0, 'column': 0})()
    return interp._call_action(acao, [], {}, no, interp.global_env)


def executar_arquivo(caminho, verboso=False, filtro="", medidor=None):
    """Executa um arquivo de teste e devolve a lista de resultados.

    Com `medidor`, anota quais linhas rodaram — inclusive as dos módulos
    que este arquivo adota, que é o que interessa medir.
    """
    resultados = []
    fonte = open(caminho, encoding="utf-8").read()

    try:
        arvore = parse(tokenize(fonte, caminho), caminho)
    except DataForgeError as e:
        return [Resultado(caminho, "<parse>", "error", e.message, erro=e)]

    interp = Interpreter()
    desligar = medidor.medir(interp) if medidor is not None else None
    buffer = io.StringIO()
    inicio = time.perf_counter()
    try:
        with redirect_stdout(buffer):
            interp.run(arvore, filename=caminho)
    except DataForgeError as e:
        if desligar:
            desligar()
        return [Resultado(caminho, "<módulo>", "fail", e.message,
                          time.perf_counter() - inicio, e, buffer.getvalue())]

    testes = _acoes_de_teste(interp)

    # Um arquivo com 'crucible'/'trial' registra as suites e NAO as roda:
    # quem as roda e 'Crucible.run()'. Sem isto, um arquivo de 'trial'
    # caia no caso abaixo — "sem acoes test_, o proprio arquivo e o
    # caso" — e era contado como UM TESTE QUE PASSOU.
    #
    # Um teste que falha reportando "Tudo verde" e a pior falha possivel
    # num corredor de testes: a suite fica vermelha e o CI passa. Um
    # arquivo com dez 'trial', um deles quebrado, saia com codigo 0.
    do_crucible = _resultados_do_crucible(interp, caminho, inicio, buffer)
    if do_crucible is not None:
        if desligar:
            desligar()
        return do_crucible

    # Arquivo sem ações test_: o próprio arquivo é o caso.
    if not testes:
        if desligar:
            desligar()
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

    if desligar:
        desligar()
    return resultados


def fontes_de(alvo=".", arquivos_de_teste=()):
    """Os `.df` que os testes deveriam cobrir.

    Tudo sob o alvo menos os próprios arquivos de teste. Incluir os que
    ninguém tocou é o ponto: um módulo sem nenhum teste precisa aparecer
    com **zero por cento**, e não sumir do relatório — sumir é o que faz
    uma cobertura de 95% conviver com metade do sistema sem teste.
    """
    de_teste = {os.path.abspath(f) for f in arquivos_de_teste}
    raiz = alvo if os.path.isdir(alvo) else os.path.dirname(alvo) or "."

    # A raiz do projeto, quando há forge.toml: rodar 'dataforge test
    # tests/' deve medir 'src/', e não só a pasta de testes.
    from . import resolucao
    projeto = resolucao.raiz_do_projeto(os.path.join(raiz, "_"))
    if projeto:
        raiz = projeto

    ignorar = ("forge_modules", "__pycache__", ".git", "node_modules",
               "dist", "build", ".venv", "venv")
    achados = []
    for pasta, subpastas, nomes in os.walk(raiz):
        subpastas[:] = [d for d in subpastas
                        if d not in ignorar and not d.startswith(".")]
        for nome in nomes:
            if not nome.endswith(".df"):
                continue
            caminho = os.path.abspath(os.path.join(pasta, nome))
            if caminho in de_teste:
                continue
            achados.append(caminho)
    return sorted(achados)


def executar(alvo=".", verboso=False, filtro="", cor=True,
             parar_no_primeiro=False, cobertura=False, minimo=0.0,
             detalhar=False):
    """Executa todos os testes sob um alvo. Devolve (resultados, ok)."""
    def tinta(t, c):
        return f"{c}{t}{RESET}" if cor else t

    arquivos = descobrir(alvo)
    if not arquivos:
        print(tinta(f"Nenhum arquivo de teste encontrado em '{alvo}'.", AMARELO))
        print(f"{CINZA if cor else ''}Procuro por *_test.df, test_*.df "
              f"ou .df dentro de tests/.{RESET if cor else ''}")
        return [], True

    medidor = None
    if cobertura:
        from .cobertura import Cobertura
        medidor = Cobertura()
        # O denominador é levantado ANTES de rodar: assim um arquivo que
        # nenhum teste toca aparece com zero, em vez de não aparecer.
        for fonte in fontes_de(alvo, arquivos):
            try:
                texto = open(fonte, encoding="utf-8").read()
                medidor.registrar_arvore(fonte, parse(tokenize(texto, fonte),
                                                      fonte))
            except Exception:
                continue        # não compila: o 'check' é que reclama disso

    todos = []
    inicio = time.perf_counter()

    for arquivo in arquivos:
        resultados = executar_arquivo(arquivo, verboso, filtro, medidor)
        if not resultados:
            continue
        todos.extend(resultados)

        passaram = sum(1 for r in resultados if r.status == "pass")
        pulados = sum(1 for r in resultados if r.status == "skip")
        falharam = len(resultados) - passaram - pulados
        cabecalho = _curto(arquivo)
        estado = tinta("✓", VERDE) if falharam == 0 else tinta("✗", VERMELHO)
        conta = f"{passaram}/{len(resultados) - pulados}"
        if pulados:
            conta += f", {pulados} pendente(s)"
        print(f"{estado} {cabecalho} {CINZA if cor else ''}"
              f"({conta}){RESET if cor else ''}")

        for r in resultados:
            if r.status == "skip":
                if verboso:
                    print(f"    {tinta('pend', AMARELO)} {r.nome}"
                          f"{'  ' + r.mensagem if r.mensagem else ''}")
            elif r.status == "pass":
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
    pulados = sum(1 for r in todos if r.status == "skip")
    falharam = len(todos) - passaram - pulados

    print()
    resumo = f"{passaram} passaram"
    if pulados:
        resumo += f", {pulados} pendente(s)"
    if falharam:
        resumo += f", {tinta(str(falharam) + ' falharam', VERMELHO)}"
    print(f"{resumo} em {len(arquivos)} arquivo(s) — {decorrido:.2f}s")

    abaixo_do_minimo = False
    if medidor is not None:
        abaixo_do_minimo = _relatar_cobertura(medidor, cor, minimo, detalhar)

    if falharam == 0 and todos and not abaixo_do_minimo:
        print(tinta("Tudo verde.", VERDE))
    return todos, falharam == 0 and not abaixo_do_minimo


#: Onde a cor da taxa muda. Não é arbitrário: abaixo de 50% a suíte
#: cobre menos da metade, e um número assim precisa parecer vermelho.
_FAIXAS = ((0.90, VERDE), (0.50, AMARELO), (0.0, VERMELHO))


def _cor_da_taxa(taxa):
    for piso, cor in _FAIXAS:
        if taxa >= piso:
            return cor
    return VERMELHO


def _relatar_cobertura(medidor, cor, minimo, detalhar):
    """Imprime o relatório. Devolve `True` se ficou abaixo do mínimo."""
    def tinta(t, c):
        return f"{c}{t}{RESET}" if cor else t

    relatorio = medidor.por_arquivo()
    total = medidor.total()

    print()
    print(tinta("Cobertura", CIANO))
    print()

    if not relatorio:
        print(f"  {CINZA if cor else ''}nenhum arquivo de código para "
              f"medir{RESET if cor else ''}")
        return False

    largura = min(52, max(len(_curto(r["arquivo"])) for r in relatorio))
    for r in relatorio:
        nome = _curto(r["arquivo"])
        if len(nome) > largura:
            nome = "…" + nome[-(largura - 1):]
        pct = r["taxa"] * 100
        barra = _barra(r["taxa"])
        print(f"  {nome:<{largura}}  {tinta(barra, _cor_da_taxa(r['taxa']))} "
              f"{tinta(f'{pct:5.1f}%', _cor_da_taxa(r['taxa']))}  "
              f"{CINZA if cor else ''}{r['cobertas']}/{r['executaveis']}"
              f"{RESET if cor else ''}")

        if r["acoes_sem_teste"]:
            nomes = ", ".join(r["acoes_sem_teste"][:6])
            resto = len(r["acoes_sem_teste"]) - 6
            if resto > 0:
                nomes += f" e {resto} outra(s)"
            print(f"  {' ' * largura}  {CINZA if cor else ''}"
                  f"sem teste: {nomes}{RESET if cor else ''}")

        if detalhar and r["faltando"]:
            print(f"  {' ' * largura}  {CINZA if cor else ''}"
                  f"linhas: {_faixas(r['faltando'])}{RESET if cor else ''}")

    print()
    taxa = total["taxa"] * 100
    print(f"  {tinta('total', BRANCO)}  "
          f"{tinta(f'{taxa:.1f}%', _cor_da_taxa(total['taxa']))}  "
          f"{CINZA if cor else ''}{total['cobertas']} de "
          f"{total['executaveis']} linhas executáveis{RESET if cor else ''}")

    if minimo > 0 and total["taxa"] < minimo:
        print()
        print(tinta(f"✗ cobertura {taxa:.1f}% abaixo do mínimo exigido "
                    f"({minimo * 100:.0f}%)", VERMELHO))
        return True
    return False


def _barra(taxa, largura=20):
    cheios = round(taxa * largura)
    return "█" * cheios + "░" * (largura - cheios)


def _faixas(linhas):
    """[3, 4, 5, 9, 11, 12] vira '3-5, 9, 11-12'.

    Uma lista de setenta números é ilegível; as faixas dizem onde estão
    os buracos, que é o que se quer saber.
    """
    if not linhas:
        return ""
    grupos = []
    inicio = anterior = linhas[0]
    for atual in linhas[1:]:
        if atual == anterior + 1:
            anterior = atual
            continue
        grupos.append((inicio, anterior))
        inicio = anterior = atual
    grupos.append((inicio, anterior))
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in grupos)
