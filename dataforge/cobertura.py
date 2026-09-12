# -*- coding: utf-8 -*-
"""Quais linhas os testes realmente executaram.

Por que isto importa
--------------------
'dataforge test' dizia passou ou falhou, e nunca "este ramo nunca
rodou". Num sistema de 200 arquivos, nao saber o que NAO esta testado e
a diferenca entre uma suite que protege e uma que da falsa seguranca: o
codigo que ninguem exercitou e exatamente onde o bug mora.

Como funciona
-------------
Duas metades, e as duas precisam estar certas para o numero significar
algo.

**O denominador** sai do parser: quais linhas sao EXECUTAVEIS. Contar
todas as linhas do arquivo mediria comentario e linha vazia, e daria um
numero sempre pessimista que ninguem olharia duas vezes. Contar so as
linhas que rodaram sobre elas mesmas daria sempre 100%.

**O numerador** sai da execucao: 'execute' e sombreado, como o
depurador faz, e anota 'no.line'. O corpo compilado das acoes passa POR
FORA de 'execute' — daí 'compilar_corpos = False' enquanto se mede,
pelo mesmo motivo que o depurador desliga.

O que ele NAO mede
------------------
Ramo, e nao linha: 'given a and b' conta como uma linha coberta mesmo
que 'b' nunca tenha sido avaliado. Medir ramo exigiria instrumentar a
avaliacao de expressao, o que dobraria o custo — e cobertura de linha ja
responde a pergunta que importa, que e "existe codigo que ninguem
testou".
"""

import os

from . import ast_nodes as ast

#: Nos que NAO consomem uma linha executavel por si.
#:
#: A declaracao de uma acao nao "roda": o que roda e o corpo dela. Contar
#: a linha do 'action' faria uma acao nunca chamada parecer parcialmente
#: coberta, que e a pior leitura possivel — ela esta 0% coberta.
_SO_ESTRUTURA = (
    ast.Program,
)


class Cobertura:
    """As linhas executaveis de cada arquivo, e quais foram executadas."""

    def __init__(self):
        #: caminho -> set(linhas executaveis)
        self.executaveis = {}
        #: caminho -> set(linhas executadas)
        self.executadas = {}
        #: caminho -> o nome da acao que comeca em cada linha
        self.acoes = {}

    # ── Medir ────────────────────────────────────────────────

    def registrar_arvore(self, caminho, arvore):
        """O denominador: as linhas que dariam para executar."""
        caminho = os.path.abspath(caminho)
        if caminho in self.executaveis:
            return
        linhas, acoes = _linhas_executaveis(arvore)
        self.executaveis[caminho] = linhas
        self.acoes[caminho] = acoes
        self.executadas.setdefault(caminho, set())

    def anotar(self, caminho, linha):
        """O numerador: esta linha rodou."""
        if not caminho or not linha:
            return
        self.executadas.setdefault(os.path.abspath(caminho), set()).add(linha)

    # ── Ler ──────────────────────────────────────────────────

    def por_arquivo(self):
        """Uma linha de relatorio por arquivo, do menos coberto."""
        relatorio = []
        for caminho, possiveis in self.executaveis.items():
            if not possiveis:
                continue
            feitas = self.executadas.get(caminho, set()) & possiveis
            faltando = sorted(possiveis - feitas)
            relatorio.append({
                "arquivo": caminho,
                "executaveis": len(possiveis),
                "cobertas": len(feitas),
                "taxa": len(feitas) / len(possiveis),
                "faltando": faltando,
                "acoes_sem_teste": sorted(
                    nome for linha, nome in self.acoes.get(caminho, {}).items()
                    if linha in faltando),
            })
        return sorted(relatorio, key=lambda r: (r["taxa"], r["arquivo"]))

    def total(self):
        possiveis = sum(len(v) for v in self.executaveis.values())
        if not possiveis:
            return {"executaveis": 0, "cobertas": 0, "taxa": 1.0}
        cobertas = sum(len(self.executadas.get(c, set()) & v)
                       for c, v in self.executaveis.items())
        return {"executaveis": possiveis, "cobertas": cobertas,
                "taxa": cobertas / possiveis}

    # ── Instrumentar ─────────────────────────────────────────

    def medir(self, interp):
        """Sombreia `execute` no interpretador. Devolve o que desliga.

        Mesma tecnica do depurador, e pelo mesmo motivo o corpo
        compilado e desligado: ele passa por fora de `execute`, e medir
        com ele ligado mostraria zero por cento em toda acao.
        """
        anterior = interp.compilar_corpos
        interp.compilar_corpos = False
        original = interp.execute
        anotar = self.anotar

        def executar(no, env):
            # O arquivo vem do interpretador, e nao do no: um no nao
            # carrega de que arquivo veio, e um 'adopt' troca o
            # 'filename' enquanto o modulo importado roda — que e
            # exatamente o comportamento desejado aqui.
            anotar(interp.filename, getattr(no, "line", 0))
            return original(no, env)

        interp.execute = executar

        def desligar():
            # 'del', e nao reatribuicao: reatribuir deixaria um atributo
            # de instancia com o metodo ligado, e o interpretador sairia
            # da medicao carregando uma indirecao que nao tinha.
            interp.__dict__.pop("execute", None)
            interp.compilar_corpos = anterior

        return desligar


def linhas_executaveis(arvore):
    """Só o conjunto de linhas — para quem nao precisa das acoes.

    Existe para o depurador: uma parada precisa cair numa linha que o
    interpretador executa, e a pergunta e a MESMA que a cobertura faz.
    Duas definicoes de "linha executavel" divergiriam, e a parada
    cairia onde a cobertura nao conta.
    """
    return _linhas_executaveis(arvore)[0]


def _linhas_executaveis(arvore):
    """As linhas que o interpretador pode executar, e as acoes por linha.

    Desce a arvore inteira — corpo de acao, de blueprint, de laco, de
    'monitor'. O que conta e a linha de cada INSTRUCAO; expressao dentro
    dela nao acrescenta linha propria, porque a instrucao inteira roda
    ou nao roda junta.
    """
    linhas = set()
    acoes = {}

    def descer(no, dentro_de=None):
        if no is None:
            return
        if isinstance(no, (list, tuple)):
            for item in no:
                descer(item, dentro_de)
            return
        if not isinstance(no, ast.ASTNode):
            return

        nome_do_no = type(no).__name__
        linha = getattr(no, "line", 0)

        if nome_do_no == "ActionDeclaration":
            # A linha da declaracao nao e executavel; o corpo e. Assim
            # uma acao nunca chamada aparece 0% e nao 20%.
            if linha:
                acoes[_primeira_linha_do_corpo(no) or linha] = no.name
            descer(getattr(no, "body", None), no.name)
            for decorador in (getattr(no, "decorators", None) or []):
                descer(decorador, dentro_de)
            return

        if nome_do_no in ("BlueprintDeclaration", "RecordDeclaration",
                          "EnumDeclaration", "TraitDeclaration"):
            for campo in ("body", "methods"):
                valor = getattr(no, campo, None)
                if isinstance(valor, dict):
                    descer(list(valor.values()), dentro_de)
                else:
                    descer(valor, dentro_de)
            return

        if not isinstance(no, _SO_ESTRUTURA) and linha and _e_instrucao(no):
            linhas.add(linha)

        for campo in getattr(no, "__dataclass_fields__", {}):
            if campo in ("line", "column"):
                continue
            descer(getattr(no, campo, None), dentro_de)

    descer(arvore)
    return linhas, acoes


def _primeira_linha_do_corpo(acao):
    corpo = getattr(acao, "body", None) or []
    for stmt in corpo:
        linha = getattr(stmt, "line", 0)
        if linha:
            return linha
    return 0


#: Os nos que sao INSTRUCAO — cache de '_e_instrucao'.
_INSTRUCOES = {}


def _e_instrucao(no):
    """True quando o interpretador executa este no como INSTRUCAO.

    A definicao nao e uma lista escrita aqui: e a existencia de um
    'exec_<Nome>' no interpretador. Isso e o que 'execute' faz, e usar a
    mesma fonte significa que um no novo na linguagem entra no
    denominador sozinho.

    A primeira versao ERA uma lista, e ela apodreceu antes de ser
    commitada: tinha 'CycleLoop', e o no se chama 'CycleFromTo'. O laco
    inteiro ficava fora da contagem, e a cobertura saia otimista sem
    nada denunciando — que e o pior defeito possivel numa metrica de
    cobertura.
    """
    nome = type(no).__name__
    conhecido = _INSTRUCOES.get(nome)
    if conhecido is None:
        from .interpreter import Interpreter
        conhecido = hasattr(Interpreter, f"exec_{nome}")
        _INSTRUCOES[nome] = conhecido
    return conhecido
