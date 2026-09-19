# -*- coding: utf-8 -*-
"""Arcane.Percurso — o caminho inteiro de um arquivo, fase por fase, medido.

O que faltava
-------------
`dataforge ir` mostra CADA fase: o HIR, o MIR, as analises, a SSA, o LIR.
O que nao havia era a visao de cima — as fases **em ordem**, o que cada
uma produziu e **quanto tempo levou**. Que e a pergunta que aparece
quando um arquivo demora a abrir no editor: *onde o tempo vai?*

    adopt Arcane.Percurso as Perc

    r := Perc.percorrer("app.df")
    cycle f in r["fases"]:
        out $"{f['fase']:<14} {f['saiu']:<28} {f['ms']} ms"

E na linha de comando:

    dataforge percurso app.df

Ele nao executa o programa
--------------------------
O percurso vai do lexer ao compilador de fechamentos e **para ali**. A
ultima fase e nomeada, medida em zero e marcada como nao percorrida, com
o motivo escrito.

Isso e deliberado. Executar e o que o programa faz — e um arquivo de
verdade abre soquete, escreve em disco e manda e-mail. Um comando cuja
funcao e *mostrar as fases* nao pode ter efeito no mundo, e um que
tivesse seria usado uma vez.

O tempo e uma medida, nao um benchmark
--------------------------------------
Cada fase e cronometrada UMA vez, nesta maquina, com esta carga. Serve
para comparar as fases **entre si** — que e a pergunta — e nao para
comparar maquinas nem para afirmar que uma mudanca melhorou algo. Para
isso ha `Arcane.Bench`, que repete, tira mediana e sabe dizer se a
diferenca e real.
"""

import os
import time

from ..errors import RuntimeError_

#: As fases, na ordem do caminho. `modulo` e onde ela mora, e por isso a
#: tabela tambem e o mapa do compilador.
FASES = (
    {"fase": "lexer", "modulo": "dataforge/lexer.py",
     "o_que_faz": "texto -> tokens, com INDENT/DEDENT e interpolacao"},
    {"fase": "parser", "modulo": "dataforge/parser.py",
     "o_que_faz": "tokens -> arvore, recursivo descendente"},
    {"fase": "hir", "modulo": "dataforge/hir.py",
     "o_que_faz": "abre o acucar sintatico e deixa o nucleo"},
    {"fase": "tipos", "modulo": "dataforge/typechecker.py",
     "o_que_faz": "nomes, aridade, tipos, alcance — e atravessa arquivos"},
    {"fase": "mir", "modulo": "dataforge/mir.py",
     "o_que_faz": "o grafo de fluxo: bloco basico e aresta rotulada"},
    {"fase": "analises", "modulo": "dataforge/mir.py",
     "o_que_faz": "alcance, vivacidade, constantes, escapatoria"},
    {"fase": "ssa", "modulo": "dataforge/ssa.py",
     "o_que_faz": "uma definicao por nome, com os nos phi das juncoes"},
    {"fase": "otimizar", "modulo": "dataforge/otimizar.py",
     "o_que_faz": "dobra de constante, ramo morto, inalcancavel"},
    {"fase": "lir", "modulo": "dataforge/lir.py",
     "o_que_faz": "o que desce para fechamento, e o que recua"},
    {"fase": "execucao", "modulo": "dataforge/interpreter.py",
     "o_que_faz": "chamar os fechamentos — NAO percorrida, de proposito"},
)

#: Onde o caminho real difere do desenho da referencia Deep Tech. Cada
#: item nomeia a fase do desenho, o que ha aqui e por que.
DIVERGENCIAS = (
    {"no_desenho": "Borrow + Dataflow Checker",
     "aqui": "o Dataflow existe (MIR e SSA); o Borrow, nao",
     "porque": "num mundo com coletor a integridade da memoria nunca "
               "esteve em risco. O que se protege e o protocolo, e quem o "
               "protege e 'Arcane.Posse' mais tres codigos do 'check'"},
    {"no_desenho": "LLVM Backend",
     "aqui": "compilador.py — a arvore vira fechamentos Python",
     "porque": "o LLVM tiraria a unica propriedade inegociavel do projeto: "
               "zero dependencia externa no runtime. Medido, esta tecnica "
               "da 1,5x a 1,8x, e o teto dela e ~6,5x"},
    {"no_desenho": "Machine Code / WASM",
     "aqui": "nao ha. O artefato e a arvore compilada, em memoria",
     "porque": "sem backend nativo nao ha o que emitir. RODAR em WASM "
               "funciona pelo Pyodide, com o interpretador junto — e isso "
               "e outra frase"},
    {"no_desenho": "Bare-Metal Runtime",
     "aqui": "nao ha",
     "porque": "o runtime e o CPython. 'Arcane.Alvo' lista o que falta em "
               "cada capacidade do alvo 'embarcado'"},
    {"no_desenho": "(ausente no desenho) Execution Engine",
     "aqui": "interpreter.py — o centro da implementacao",
     "porque": "o desenho supoe compilacao antecipada, e por isso nao tem "
               "onde por o interpretador. Aqui ele e a peca principal"},
)


def fases():
    """As fases, na ordem, sem percorrer arquivo nenhum."""
    return [dict(f) for f in FASES]


def divergencias():
    """Onde o caminho real difere do desenho do documento, e por que."""
    return [dict(d) for d in DIVERGENCIAS]


def _cronometrar(funcao):
    comeco = time.perf_counter()
    valor = funcao()
    return valor, (time.perf_counter() - comeco) * 1000.0


def percorrer(caminho, com_tipos=True):
    """Leva o arquivo por todas as fases e devolve o que cada uma fez.

    `com_tipos := no` pula a analise estatica, que e a fase mais cara num
    projeto com muitos `adopt` — ela le a superficie dos vizinhos.
    """
    alvo = str(caminho)
    if not os.path.isfile(alvo):
        raise RuntimeError_(f"'{alvo}' não existe.", doc="ecossistema/percurso")
    fonte = open(alvo, encoding="utf-8").read()

    from .. import hir as _hir
    from .. import lir as _lir
    from .. import mir as _mir
    from .. import otimizar as _ot
    from .. import ssa as _ssa
    from ..lexer import tokenize
    from ..parser import parse
    from ..typechecker import check_program

    # Os imports LENTOS acontecem antes de qualquer cronometro.
    #
    # `lir` importa `compilador` e abre um interpretador por dentro, e
    # `ssa` importa o seu. A primeira fase que toca um modulo paga o
    # import dele — e medido: num arquivo de 12 tokens o `lir` aparecia
    # com 6,8 ms e 93,8% do total, contra 0,05 ms de trabalho real.
    #
    # Uma ferramenta que responde "onde o tempo vai" e aponta a fase
    # errada e pior que nenhuma: a pessoa vai otimizar o lugar que a
    # ferramenta indicou.
    _lir._tabelas()
    _lir._interprete()

    medidas = {}
    saiu = {}

    try:
        fluxo, ms = _cronometrar(lambda: list(tokenize(fonte, alvo)))
    except Exception as erro:
        raise RuntimeError_(f"'{alvo}' não passa pelo lexer: {erro}",
                            doc="ecossistema/percurso")
    medidas["lexer"] = ms
    saiu["lexer"] = (len(fluxo), f"{len(fluxo)} tokens")

    try:
        arvore, ms = _cronometrar(lambda: parse(list(fluxo), alvo))
    except Exception as erro:
        raise RuntimeError_(f"'{alvo}' não passa pelo parser: {erro}",
                            doc="ecossistema/percurso")
    medidas["parser"] = ms
    nos = sum(1 for _ in _hir._percorrer(arvore))
    saiu["parser"] = (nos, f"{nos} nos, {len(arvore.body)} no topo")

    usados, ms = _cronometrar(lambda: _hir.acucares_usados(arvore))
    medidas["hir"] = ms
    total_acucar = sum(usados.values())
    saiu["hir"] = (total_acucar,
                   f"{total_acucar} acucares em {len(usados)} formas")

    if com_tipos:
        diags, ms = _cronometrar(lambda: check_program(arvore, alvo))
        erros = len([d for d in diags if d.severity == "error"])
        medidas["tipos"] = ms
        saiu["tipos"] = (len(diags),
                         f"{erros} erro(s), {len(diags) - erros} aviso(s)")
    else:
        medidas["tipos"] = 0.0
        saiu["tipos"] = (0, "pulada (com_tipos := no)")

    corpos, ms = _cronometrar(lambda: _mir.construir(arvore))
    medidas["mir"] = ms
    blocos = sum(len(c.blocos) for c in corpos)
    saiu["mir"] = (blocos, f"{len(corpos)} corpo(s), {blocos} bloco(s)")

    def analisar():
        mortos = 0
        indefinidos = 0
        fixos = 0
        for corpo in corpos:
            vivos = _mir.alcancaveis(corpo)
            mortos += len([b for b in corpo.blocos if b.id not in vivos])
            indefinidos += len(_mir.talvez_nao_definidas(corpo))
            fixos += len(_mir.constantes(corpo))
        return mortos, indefinidos, fixos

    (mortos, indefinidos, fixos), ms = _cronometrar(analisar)
    medidas["analises"] = ms
    saiu["analises"] = (mortos + indefinidos + fixos,
                        f"{mortos} bloco(s) morto(s), {indefinidos} nome(s) "
                        f"talvez nao definido(s), {fixos} constante(s)")

    formas, ms = _cronometrar(lambda: [_ssa.construir(c) for c in corpos])
    medidas["ssa"] = ms
    fis = sum(len(b.fis) for f in formas for b in f.blocos)
    saiu["ssa"] = (fis, f"{fis} no(s) phi")

    contagem, ms = _cronometrar(lambda: _ot.relatorio_de(arvore))
    medidas["otimizar"] = ms
    oportunidades = sum(contagem.values())
    saiu["otimizar"] = (oportunidades,
                        f"{oportunidades} oportunidade(s) em "
                        f"{len([k for k, v in contagem.items() if v])} passe(s)")

    inv, ms = _cronometrar(lambda: _lir.inventario(arvore))
    medidas["lir"] = ms
    saiu["lir"] = (inv.compiladas,
                   f"{inv.compiladas} de {inv.total} nos viraram fechamento "
                   f"({inv.proporcao():.0f}%)")

    medidas["execucao"] = 0.0
    saiu["execucao"] = (0, "nao percorrida: executar e o que o programa faz")

    total = sum(medidas.values())
    lista = []
    for fase in FASES:
        nome = fase["fase"]
        quanto, texto_saida = saiu[nome]
        ms = medidas[nome]
        lista.append({**fase, "quanto": quanto, "saiu": texto_saida,
                      "ms": round(ms, 3),
                      "fatia": round(100.0 * ms / total, 1) if total else 0.0,
                      "percorrida": nome != "execucao"})
    mais_caras = sorted([f for f in lista if f["percorrida"]],
                        key=lambda f: -f["ms"])
    return {"arquivo": alvo, "fases": lista, "ms": round(total, 3),
            "mais_cara": mais_caras[0]["fase"] if mais_caras else "",
            "tokens": len(fluxo), "nos": nos,
            "aviso": "cada fase foi medida UMA vez, nesta maquina, com os "
                     "imports ja aquecidos: serve para comparar as fases "
                     "entre si, e nao para comparar maquinas. Para isso, "
                     "Arcane.Bench."}


def desenho():
    """O caminho REAL, desenhado — e a ausencia tem lugar nele."""
    return "\n".join((
        "        arquivo .df",
        "             |",
        "      +----------------+",
        "      | lexer + parser |   tokens -> arvore",
        "      +----------------+",
        "             |",
        "      +----------------+",
        "      | HIR  (acucar)  |   5 formas abertas; 8 NAO sao acucar",
        "      +----------------+",
        "             |",
        "      +----------------+",
        "      | tipos + super- |   atravessa 'adopt': aridade, tipo,",
        "      | ficie          |   retorno — e cala quando nao prova",
        "      +----------------+",
        "             |",
        "      +----------------+",
        "      | MIR + analises |   bloco, aresta, alcance, constantes",
        "      +----------------+",
        "             |",
        "      +----------------+",
        "      | SSA + passes   |   phi, SCCP, dobra, ramo morto",
        "      +----------------+",
        "             |",
        "      +----------------+",
        "      | LIR            |   o que desce, e o que RECUA",
        "      +----------------+",
        "             |",
        "      +----------------+",
        "      | fechamentos    |   <- aqui estaria o LLVM. 1,5x a 1,8x",
        "      | (compilador)   |      medidos; teto ~6,5x",
        "      +----------------+",
        "             |",
        "      +----------------+",
        "      | interpretador  |   o desenho do documento nao tem esta",
        "      +----------------+   peca: ele supoe compilacao antecipada",
        "             |",
        "      +----------------+",
        "      | codigo nativo  |   NAO EXISTE — e a fase fica no mapa",
        "      | / bare-metal   |   para que a ausencia tenha lugar",
        "      +----------------+",
    ))


def relatorio(resultado):
    """A tabela do percurso, da fase mais cara para a mais barata."""
    linhas = [f"  {resultado['arquivo']}  —  {resultado['ms']} ms no total",
              ""]
    linhas.append(f"  {'fase':<10} {'ms':>9} {'%':>6}   o que saiu")
    for f in resultado["fases"]:
        ms = "—" if not f["percorrida"] else f"{f['ms']:.3f}"
        fatia = "" if not f["percorrida"] else f"{f['fatia']:.1f}"
        linhas.append(f"  {f['fase']:<10} {ms:>9} {fatia:>6}   {f['saiu']}")
    linhas.append("")
    if resultado["mais_cara"]:
        linhas.append(f"  a fase mais cara deste arquivo: "
                      f"{resultado['mais_cara']}")
    linhas.append(f"  {resultado['aviso']}")
    return "\n".join(linhas)


class ArcanePercurso:
    """O dicionario que `adopt Arcane.Percurso` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Percurso",
            "fases": fases,
            "percorrer": percorrer,
            "divergencias": divergencias,
            "desenho": desenho,
            "relatorio": relatorio,
        }
