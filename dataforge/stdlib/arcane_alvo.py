# -*- coding: utf-8 -*-
"""Arcane.Alvo — "isso roda no navegador?", respondido dos `adopt`.

O que faltava
-------------
A pergunta é real e aparece cedo: *este programa roda no navegador? numa
função serverless? num WASI?* A resposta dependia de alguém conhecer de
cor o que cada ambiente suporta — e de lembrar, para cada `adopt`, se
aquele módulo abre soquete, processo ou arquivo.

    adopt Arcane.Alvo as Alvo

    r := Alvo.conferir("app.df", "navegador")
    given not r["roda"]:
        cycle p in r["problemas"]:
            out $"linha {p['linha']}: {p['modulo']} precisa de {p['capacidade']}"

E na linha de comando:

    dataforge alvo app.df --alvo=navegador

O vocabulário é o mesmo
-----------------------
As capacidades são as de [`Arcane.Capacidade`](/docs/seguranca/capacidade):
`arquivos`, `rede`, `processo`, `banco`, `threads`, `nativo`, `python`.
Lá elas são **cobradas em execução**; aqui são **lidas antes de rodar**,
e o alvo é quem diz quais existem.

É a mesma pergunta feita de dois lados, e usar dois vocabulários faria
as duas respostas divergirem no primeiro módulo novo.

O limite, e ele é grande
------------------------
**Esta leitura é estática, e sai dos `adopt`.** Ela não é uma prova:

* um módulo alcançado **indiretamente** (uma biblioteca do projeto que
  adota `Arcane.Process`) não aparece aqui — a leitura é de um arquivo;
* `adopt Python.x` conta como capacidade `python` e para aí: o que
  aquele pacote faz, ninguém lê;
* um programa que **não** adota nada perigoso ainda pode falhar por
  outra razão — memória, tempo, uma dependência nativa do Python.

O que ela dá é o que vale: a lista dos pontos que **certamente** não
rodam, com a linha. Um "roda" aqui quer dizer "não achei impedimento por
esta via", e o módulo diz isso em `limites()`.
"""

import os

from .. import ast_nodes as ast
from ..errors import RuntimeError_
from ..lexer import tokenize
from ..parser import parse

#: O que cada alvo suporta. A lista é a documentação — há teste cobrando
#: o tamanho de `o_que_e`, porque um nome de alvo sem explicação obriga
#: quem lê a adivinhar de que ambiente se está falando.
ALVOS = {
    "servidor": {
        "o_que_e": "uma máquina com sistema operacional completo: o alvo "
                   "padrão, e onde o DataForge foi feito para rodar",
        "suporta": ["arquivos", "rede", "processo", "banco", "threads",
                    "nativo", "python", "ambiente"],
        "porque": {},
    },
    "cli": {
        "o_que_e": "um programa de linha de comando na máquina do usuário "
                   "— o mesmo que o servidor, e a distinção é de uso",
        "suporta": ["arquivos", "rede", "processo", "banco", "threads",
                    "nativo", "python", "ambiente"],
        "porque": {},
    },
    "navegador": {
        "o_que_e": "o CPython compilado para WebAssembly (Pyodide) dentro "
                   "de uma aba: memória linear, sem sistema operacional "
                   "por baixo e tudo dentro da caixa de areia da página",
        "suporta": ["python"],
        "porque": {
            "arquivos": "não há sistema de arquivos real: o que existe é "
                        "um sistema em memória que some quando a aba fecha",
            "rede": "soquete cru não existe na aba; o que há é 'fetch', "
                    "sujeito à política de mesma origem (CORS)",
            "processo": "não há como criar processo dentro de uma aba",
            "banco": "não há cliente TCP para Postgres ou MySQL; o SQLite "
                     "existiria só em memória",
            "threads": "as threads do Python não atravessam para o "
                       "WebAssembly sem SharedArrayBuffer e isolamento "
                       "de origem, e o Pyodide as desliga por padrão",
            "nativo": "não há '.so' a carregar: o 'ctypes' não tem para "
                      "onde apontar",
            "ambiente": "não há variável de ambiente numa aba",
        },
    },
    "wasi": {
        "o_que_e": "WebAssembly fora do navegador, com a interface de "
                   "sistema do WASI: há arquivos (nos diretórios abertos "
                   "pelo host) e não há processo nem thread",
        "suporta": ["arquivos", "ambiente", "python"],
        "porque": {
            "rede": "a rede do WASI ainda é proposta, e o que existe hoje "
                    "depende do host expor soquete — não conte com ela",
            "processo": "não há 'fork' nem 'exec' no WASI",
            "banco": "sem rede, só faria sentido um banco em arquivo",
            "threads": "as threads do WASI dependem de uma extensão que "
                       "nem todo host implementa",
            "nativo": "carregar biblioteca nativa exigiria um linker "
                      "dinâmico que o WASI não tem por padrão",
        },
    },
    "funcao": {
        "o_que_e": "uma função serverless: processo efêmero, sistema de "
                   "arquivos somente leitura fora de /tmp, e morte anunciada "
                   "ao fim do pedido",
        "suporta": ["rede", "banco", "python", "ambiente", "arquivos"],
        "porque": {
            "processo": "criar processo é quase sempre bloqueado, e quando "
                        "não é, ele morre junto com a invocação",
            "threads": "uma thread que sobrevive ao pedido é interrompida "
                       "no meio quando o ambiente congela o processo",
            "nativo": "a biblioteca nativa teria de ser empacotada junto, "
                      "e a maioria dos ambientes não deixa",
        },
    },
    "embarcado": {
        "o_que_e": "um microcontrolador com MicroPython ou parecido: "
                   "memória em kilobytes, e uma fração da biblioteca padrão",
        "suporta": [],
        "porque": {
            "arquivos": "há um sistema de arquivos minúsculo, e a "
                        "biblioteca padrão que o DataForge usa não está lá",
            "rede": "existe em alguns, e por uma API que não é a do CPython",
            "processo": "não há processo: há um programa só",
            "banco": "não há cliente de banco nessa faixa de memória",
            "threads": "não há threading do CPython",
            "nativo": "não há 'ctypes'",
            "python": "não é o CPython: é outro interpretador, com outra "
                      "biblioteca padrão",
            "ambiente": "não há ambiente",
        },
    },
}

#: Módulo -> capacidade. É a MESMA tabela conceitual de
#: `Arcane.Capacidade`: dois vocabulários divergiriam no primeiro módulo
#: novo, e as duas respostas passariam a discordar.
def _tabela():
    from .arcane_capacidade import _EXIGE
    return _EXIGE


def alvos():
    """Os alvos conhecidos, com o que cada um suporta e o que não."""
    saida = {}
    todas = set()
    for perfil in ALVOS.values():
        todas |= set(perfil["suporta"]) | set(perfil["porque"])
    for nome, perfil in ALVOS.items():
        saida[nome] = {
            "o_que_e": perfil["o_que_e"],
            "suporta": sorted(perfil["suporta"]),
            "nao_suporta": sorted(todas - set(perfil["suporta"])),
        }
    return saida


def _arvore_de(caminho):
    alvo = str(caminho)
    if not os.path.isfile(alvo):
        raise RuntimeError_(f"'{alvo}' não existe.", doc="alvos/portabilidade")
    fonte = open(alvo, encoding="utf-8").read()
    try:
        return parse(tokenize(fonte, alvo), alvo)
    except Exception as erro:
        raise RuntimeError_(f"'{alvo}' não compila: {erro}",
                            doc="alvos/portabilidade")


def exigencias(caminho):
    """Que capacidades este arquivo pede, e em que linha.

    Sai dos `adopt`, e só deles. Um módulo alcançado indiretamente não
    aparece — ver `limites()`.
    """
    from .. import hir as _hir

    exige = _tabela()
    achados = []
    vistos = set()
    for no in _hir._percorrer(_arvore_de(caminho)):
        if not isinstance(no, ast.AdoptStatement):
            continue
        nome = no.module
        if nome.startswith("Python.") or nome == "Python":
            capacidade = "python"
        else:
            capacidade = exige.get(nome)
        if capacidade is None:
            continue
        chave = (nome, capacidade)
        if chave in vistos:
            continue
        vistos.add(chave)
        achados.append({"capacidade": capacidade, "modulo": nome,
                        "linha": getattr(no, "line", 0)})
    return sorted(achados, key=lambda e: (e["linha"], e["modulo"]))


def conferir(caminho, alvo="servidor"):
    """Este arquivo roda neste alvo? E o que impede, se não roda."""
    nome = str(alvo)
    if nome not in ALVOS:
        raise RuntimeError_(
            f"'{nome}' is not a known target. The targets are: "
            f"{', '.join(sorted(ALVOS))}.", doc="alvos/portabilidade")

    perfil = ALVOS[nome]
    suporta = set(perfil["suporta"])
    problemas = []
    for exigencia in exigencias(caminho):
        if exigencia["capacidade"] in suporta:
            continue
        problemas.append({
            **exigencia,
            "porque": perfil["porque"].get(
                exigencia["capacidade"],
                f"o alvo '{nome}' não oferece '{exigencia['capacidade']}'"),
        })
    return {
        "alvo": nome,
        "roda": not problemas,
        "problemas": problemas,
        "arquivo": str(caminho),
        "suporta": sorted(suporta),
    }


def conferir_todos(caminho):
    """O mesmo, em todos os alvos — a tabela que responde de uma vez."""
    return {nome: conferir(caminho, nome) for nome in sorted(ALVOS)}


def porque(alvo, capacidade):
    """Por que este alvo não tem esta capacidade."""
    nome, cap = str(alvo), str(capacidade)
    if nome not in ALVOS:
        raise RuntimeError_(
            f"'{nome}' is not a known target. The targets are: "
            f"{', '.join(sorted(ALVOS))}.", doc="alvos/portabilidade")
    if cap in ALVOS[nome]["suporta"]:
        return ""
    return ALVOS[nome]["porque"].get(cap, "")


def limites():
    """O que esta leitura NÃO prova. Lido em voz alta, de propósito."""
    return [
        "A leitura é ESTÁTICA e sai dos 'adopt' deste arquivo: ela não "
        "executa nada.",
        "Um módulo alcançado INDIRETAMENTE — uma biblioteca do projeto "
        "que adota 'Arcane.Process' — não aparece aqui.",
        "'adopt Python.x' conta como capacidade 'python' e para aí: o "
        "que aquele pacote faz por dentro, ninguém lê.",
        "Um 'roda' quer dizer 'não achei impedimento por esta via', e "
        "não 'vai funcionar': memória, tempo e dependência nativa do "
        "Python continuam sendo problema de quem publica.",
    ]


def relatorio(resultado):
    """O veredito escrito, com a linha de cada impedimento."""
    if resultado["roda"]:
        return (f"  {resultado['arquivo']} roda em '{resultado['alvo']}'\n"
                f"  (leitura estatica dos 'adopt' — ver Alvo.limites())")
    linhas = [f"  {resultado['arquivo']} NAO roda em "
              f"'{resultado['alvo']}':", ""]
    for p in resultado["problemas"]:
        linhas.append(f"   linha {p['linha']}: {p['modulo']} "
                      f"precisa de '{p['capacidade']}'")
        linhas.append(f"      {p['porque']}")
    return "\n".join(linhas)


class ArcaneAlvo:
    """O dicionário que `adopt Arcane.Alvo` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Alvo",
            "alvos": alvos,
            "exigencias": exigencias,
            "conferir": conferir,
            "conferir_todos": conferir_todos,
            "porque": porque,
            "limites": limites,
            "relatorio": relatorio,
        }
