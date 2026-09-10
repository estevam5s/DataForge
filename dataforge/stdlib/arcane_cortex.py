# -*- coding: utf-8 -*-
"""
Arcane.Cortex — aprendizado de máquina que roda.

    adopt Arcane.Cortex as ML

    treino, teste := ML.dividir(dados, 0.2)

    modelo := ML.floresta(treino, "comprou", ["idade", "renda", "visitas"])
    r := ML.avaliar(modelo, teste)

    out $"acerto: {r["acuracia"]}, F1: {r["f1"]}"

─── O que este módulo é, e o que não é ─────────────────────

Não é TensorFlow. Não há GPU, não há retropropagação, não há rede
profunda — e fingir que há seria pior que não ter: alguém escreveria
`Dense(128)` esperando uma camada e receberia um vault com o nome
`Dense` dentro.

**A versão anterior deste módulo era exatamente isso.** `sentiment`
devolvia `neutral 0.5` para qualquer texto, `Dense(4)` devolvia
`{"type": "Dense", "units": 4}`, e `classify` pedia um modelo que não
existia em lugar nenhum. Cinco símbolos, nenhum funcionando.

O que existe aqui são os algoritmos clássicos, implementados de
verdade, na escala em que um interpretador de árvore trabalha: milhares
de linhas, não milhões. Regressão, árvore, floresta, k-NN, Naive Bayes,
k-médias e PCA — que cobrem a maioria esmagadora dos problemas de dado
tabular, e que rodam.

─── A parte que quase todo tutorial pula ───────────────────

Treinar é a parte fácil. O que separa um modelo útil de um número
bonito é a **avaliação**: dividir antes de olhar, medir no que não foi
visto, e olhar a matriz de confusão em vez da acurácia.

Num problema com 99% de uma classe, um modelo que responde sempre a
mesma coisa acerta 99%. `avaliar` devolve precisão, revocação e F1
justamente porque a acurácia sozinha esconde isso — e `matriz` mostra
onde ele erra.
"""

import json
import math
import os
import random

from ..errors import ValueError_

#: A semente padrão.
#:
#: Fixa de propósito: sem ela, treinar duas vezes dá modelos diferentes,
#: e comparar duas ideias vira comparar dois sorteios. Quem quer variar
#: passa a semente.
SEMENTE = 42


def _campo(linha, nome):
    if isinstance(linha, dict):
        return linha.get(nome)
    return getattr(linha, nome, None)


def _matriz_de(linhas, colunas):
    """As linhas como matriz de números, recusando o que não é número."""
    saida = []
    for i, linha in enumerate(linhas):
        vetor = []
        for coluna in colunas:
            valor = _campo(linha, coluna)
            if isinstance(valor, bool):
                valor = int(valor)
            if not isinstance(valor, (int, float)):
                raise ValueError_(
                    f"a coluna '{coluna}' da linha {i} não é número: "
                    f"{valor!r}.",
                    dica="use 'ML.categorico()' para transformar texto em "
                         "número antes de treinar",
                    doc="tecnicas/ml")
            vetor.append(float(valor))
        saida.append(vetor)
    return saida


def _alvos(linhas, alvo):
    return [_campo(l, alvo) for l in linhas]


# ═════════════════════════════════════════════════════════════
#  Métricas — a parte que decide se o modelo serve
# ═════════════════════════════════════════════════════════════

def _matriz_confusao(reais, previstos):
    classes = sorted({*reais, *previstos}, key=lambda x: (x is None, str(x)))
    indice = {c: i for i, c in enumerate(classes)}
    tabela = [[0] * len(classes) for _ in classes]
    for real, previsto in zip(reais, previstos):
        tabela[indice[real]][indice[previsto]] += 1
    return classes, tabela


def _metricas_de_classe(reais, previstos):
    """Precisão, revocação e F1 por classe, e a média ponderada.

    A média é PONDERADA pelo tamanho da classe. A simples trataria uma
    classe de 3 exemplos como igual a uma de 3000, e num problema
    desbalanceado isso inverte a conclusão.
    """
    classes, tabela = _matriz_confusao(reais, previstos)
    por_classe, pesos = {}, []
    for i, classe in enumerate(classes):
        verdadeiros = tabela[i][i]
        previstos_como = sum(tabela[j][i] for j in range(len(classes)))
        reais_da_classe = sum(tabela[i])
        precisao = verdadeiros / previstos_como if previstos_como else 0.0
        revocacao = verdadeiros / reais_da_classe if reais_da_classe else 0.0
        f1 = (2 * precisao * revocacao / (precisao + revocacao)
              if precisao + revocacao else 0.0)
        por_classe[str(classe)] = {
            "precisao": round(precisao, 4),
            "revocacao": round(revocacao, 4),
            "f1": round(f1, 4),
            "quantos": reais_da_classe,
        }
        pesos.append(reais_da_classe)

    total = sum(pesos) or 1
    def media(chave):
        return round(sum(por_classe[str(c)][chave] * p
                         for c, p in zip(classes, pesos)) / total, 4)

    return {
        "precisao": media("precisao"),
        "revocacao": media("revocacao"),
        "f1": media("f1"),
        "por_classe": por_classe,
        "classes": [str(c) for c in classes],
        "matriz": tabela,
    }


# ═════════════════════════════════════════════════════════════
#  Os modelos
# ═════════════════════════════════════════════════════════════

class Modelo:
    """Um modelo treinado, e tudo que ele precisa para prever."""

    __slots__ = ("especie", "alvo", "colunas", "parametros", "classes",
                 "escala", "treinado_com")

    def __init__(self, especie, alvo, colunas, parametros,
                 classes=None, escala=None, treinado_com=0):
        self.especie = especie
        self.alvo = alvo
        self.colunas = list(colunas)
        self.parametros = parametros
        self.classes = classes
        self.escala = escala
        self.treinado_com = treinado_com

    def para_vault(self):
        return {"especie": self.especie, "alvo": self.alvo,
                "colunas": self.colunas, "parametros": self.parametros,
                "classes": self.classes, "escala": self.escala,
                "treinado_com": self.treinado_com}


def _prever_um(modelo, vetor):
    especie = modelo.especie
    if especie == "linear":
        return _linear_prever(modelo.parametros, vetor)
    if especie == "logistica":
        p = _sigmoide(_linear_prever(modelo.parametros, vetor))
        return modelo.classes[1] if p >= 0.5 else modelo.classes[0]
    if especie == "arvore":
        return _arvore_prever(modelo.parametros, vetor)
    if especie == "floresta":
        votos = {}
        for arvore in modelo.parametros:
            voto = _arvore_prever(arvore, vetor)
            votos[voto] = votos.get(voto, 0) + 1
        return max(votos.items(), key=lambda x: x[1])[0]
    if especie == "vizinhos":
        return _knn_prever(modelo, vetor)
    raise ValueError_(f"não sei prever com um modelo '{especie}'.",
                      doc="tecnicas/ml")


# ── regressão linear ────────────────────────────────────────

def _linear_prever(pesos, vetor):
    return pesos[0] + sum(p * v for p, v in zip(pesos[1:], vetor))


def _minimos_quadrados(X, y):
    """Resolve (XᵀX)β = Xᵀy por eliminação de Gauss.

    A solução fechada, e não descida de gradiente: para as dezenas de
    colunas que um problema tabular tem, ela é exata e mais rápida — e
    não tem taxa de aprendizado para alguém errar.
    """
    n = len(X[0]) + 1
    A = [[0.0] * (n + 1) for _ in range(n)]
    for linha, alvo in zip(X, y):
        estendida = [1.0] + list(linha)
        for i in range(n):
            for j in range(n):
                A[i][j] += estendida[i] * estendida[j]
            A[i][n] += estendida[i] * alvo

    # Pivoteamento parcial: sem ele, uma coluna quase constante gera
    # divisão por um número minúsculo e o resultado explode.
    for i in range(n):
        maior = max(range(i, n), key=lambda r: abs(A[r][i]))
        if abs(A[maior][i]) < 1e-12:
            continue
        A[i], A[maior] = A[maior], A[i]
        pivo = A[i][i]
        for j in range(i, n + 1):
            A[i][j] /= pivo
        for r in range(n):
            if r != i and A[r][i]:
                fator = A[r][i]
                for j in range(i, n + 1):
                    A[r][j] -= fator * A[i][j]
    return [A[i][n] for i in range(n)]


def _sigmoide(z):
    # Cortar em ±60 evita overflow: e^709 é o limite do float, e um
    # z grande já saturou muito antes disso.
    if z < -60:
        return 0.0
    if z > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


def _descida_logistica(X, y, voltas=300, taxa=0.1):
    """Descida de gradiente para a logística.

    Não há solução fechada aqui — a função de custo não é quadrática.
    """
    n = len(X[0]) + 1
    pesos = [0.0] * n
    quantos = len(X) or 1
    for _ in range(voltas):
        gradiente = [0.0] * n
        for linha, alvo in zip(X, y):
            estendida = [1.0] + list(linha)
            erro = _sigmoide(sum(p * v for p, v in zip(pesos, estendida))) - alvo
            for i in range(n):
                gradiente[i] += erro * estendida[i]
        for i in range(n):
            pesos[i] -= taxa * gradiente[i] / quantos
    return pesos


# ── árvore de decisão ───────────────────────────────────────

def _gini(rotulos):
    """A impureza: 0 quando todos são iguais.

    Gini e não entropia: dá árvores praticamente idênticas e não
    calcula logaritmo, que aqui é o custo dominante.
    """
    if not rotulos:
        return 0.0
    total = len(rotulos)
    contagem = {}
    for r in rotulos:
        contagem[r] = contagem.get(r, 0) + 1
    return 1.0 - sum((c / total) ** 2 for c in contagem.values())


def _melhor_corte(X, y, colunas_sorteadas=None):
    """A coluna e o limiar que mais reduzem a impureza."""
    melhor = (None, None, _gini(y))
    quantas = len(X[0])
    alvos = colunas_sorteadas if colunas_sorteadas is not None else range(quantas)

    for coluna in alvos:
        valores = sorted({linha[coluna] for linha in X})
        if len(valores) < 2:
            continue
        # O corte fica no MEIO entre dois valores vistos, e não num
        # deles: cortar em '<= 5' quando 5 existe põe todos os iguais de
        # um lado só, e o modelo passa a depender de o valor exato ter
        # aparecido no treino.
        for a, b in zip(valores, valores[1:]):
            limiar = (a + b) / 2
            esquerda = [r for linha, r in zip(X, y) if linha[coluna] <= limiar]
            direita = [r for linha, r in zip(X, y) if linha[coluna] > limiar]
            if not esquerda or not direita:
                continue
            peso = (len(esquerda) * _gini(esquerda) +
                    len(direita) * _gini(direita)) / len(y)
            if peso < melhor[2] - 1e-12:
                melhor = (coluna, limiar, peso)
    return melhor[0], melhor[1]


def _mais_comum(rotulos):
    contagem = {}
    for r in rotulos:
        contagem[r] = contagem.get(r, 0) + 1
    return max(contagem.items(), key=lambda x: (x[1], str(x[0])))[0]


def _crescer(X, y, profundidade, minimo, por_corte=None, aleatorio=None):
    if profundidade <= 0 or len(y) < minimo or len(set(y)) == 1:
        return {"folha": _mais_comum(y)}

    sorteadas = None
    if por_corte:
        # Cada corte olha um subconjunto das colunas. É o que torna as
        # árvores de uma floresta DIFERENTES entre si — sem isso, elas
        # seriam quase idênticas e a votação não acrescentaria nada.
        quantas = len(X[0])
        k = max(1, min(quantas, int(por_corte)))
        sorteadas = (aleatorio or random).sample(range(quantas), k)

    coluna, limiar = _melhor_corte(X, y, sorteadas)
    if coluna is None:
        return {"folha": _mais_comum(y)}

    esq_X, esq_y, dir_X, dir_y = [], [], [], []
    for linha, rotulo in zip(X, y):
        if linha[coluna] <= limiar:
            esq_X.append(linha)
            esq_y.append(rotulo)
        else:
            dir_X.append(linha)
            dir_y.append(rotulo)

    return {
        "coluna": coluna, "limiar": limiar,
        "esquerda": _crescer(esq_X, esq_y, profundidade - 1, minimo,
                             por_corte, aleatorio),
        "direita": _crescer(dir_X, dir_y, profundidade - 1, minimo,
                            por_corte, aleatorio),
    }


def _arvore_prever(no, vetor):
    while "folha" not in no:
        no = no["esquerda"] if vetor[no["coluna"]] <= no["limiar"] \
            else no["direita"]
    return no["folha"]


def _importancia(no, quantas, saida=None):
    """Quantas vezes cada coluna foi usada para cortar."""
    saida = saida if saida is not None else [0] * quantas
    if "folha" in no:
        return saida
    saida[no["coluna"]] += 1
    _importancia(no["esquerda"], quantas, saida)
    _importancia(no["direita"], quantas, saida)
    return saida


# ── k vizinhos ──────────────────────────────────────────────

def _knn_prever(modelo, vetor):
    k, X, y = modelo.parametros["k"], modelo.parametros["X"], \
        modelo.parametros["y"]
    distancias = sorted(
        ((sum((a - b) ** 2 for a, b in zip(vetor, linha)), rotulo)
         for linha, rotulo in zip(X, y)), key=lambda p: p[0])
    return _mais_comum([r for _, r in distancias[:k]])


# ── Naive Bayes para texto ──────────────────────────────────

def _palavras(texto):
    import re
    return re.findall(r"\w+", str(texto).lower(), flags=re.UNICODE)


# ═════════════════════════════════════════════════════════════
#  A interface
# ═════════════════════════════════════════════════════════════

class ArcaneCortex(dict):
    """Aprendizado de máquina clássico, que roda de verdade."""

    def __new__(cls):
        return {
            # preparar
            "dividir": cls._dividir,
            "embaralhar": cls._embaralhar,
            "categorico": cls._categorico,
            "escalonar": cls._escalonar,
            "aplicar_escala": cls._aplicar_escala,

            # treinar
            "linear": cls._linear,
            "logistica": cls._logistica,
            "arvore": cls._arvore,
            "floresta": cls._floresta,
            "vizinhos": cls._vizinhos,
            "bayes_texto": cls._bayes_texto,
            "kmedias": cls._kmedias,
            "pca": cls._pca,

            # usar
            "prever": cls._prever,
            "prever_um": cls._prever_uma_linha,
            "probabilidade": cls._probabilidade,

            # avaliar
            "avaliar": cls._avaliar,
            "matriz": cls._matriz,
            "validacao_cruzada": cls._validacao_cruzada,
            "importancia": cls._importancia,
            "acuracia": cls._acuracia,
            "erro": cls._erro,

            # guardar
            "salvar": cls._salvar,
            "carregar": cls._carregar,
            "resumo": cls._resumo,
        }

    # ── preparar ────────────────────────────────────────────

    @staticmethod
    def _embaralhar(linhas, semente=SEMENTE):
        copia = list(linhas or [])
        random.Random(semente).shuffle(copia)
        return copia

    @staticmethod
    def _dividir(linhas, proporcao=0.2, semente=SEMENTE, estratificar=""):
        """(treino, teste). Embaralha antes — sempre.

        Dado quase nunca chega em ordem aleatória: vem ordenado por
        data, por id, por categoria. Cortar sem embaralhar põe todo um
        tipo de exemplo de um lado só, e a avaliação mede outra coisa.

        'estratificar' mantém a proporção das classes nos dois lados —
        num problema com 2% de fraude, um corte cego pode deixar o teste
        sem fraude nenhuma.
        """
        linhas = list(linhas or [])
        if len(linhas) < 2:
            raise ValueError_(
                "não dá para dividir menos de duas linhas.",
                doc="tecnicas/ml")
        sorteio = random.Random(semente)

        if estratificar:
            grupos = {}
            for linha in linhas:
                grupos.setdefault(_campo(linha, estratificar), []).append(linha)
            treino, teste = [], []
            for chave in sorted(grupos, key=str):
                grupo = grupos[chave]
                sorteio.shuffle(grupo)
                corte = max(1, int(len(grupo) * float(proporcao)))
                teste.extend(grupo[:corte])
                treino.extend(grupo[corte:])
            sorteio.shuffle(treino)
            sorteio.shuffle(teste)
            return [treino, teste]

        copia = list(linhas)
        sorteio.shuffle(copia)
        corte = max(1, int(len(copia) * float(proporcao)))
        return [copia[corte:], copia[:corte]]

    @staticmethod
    def _categorico(linhas, coluna, prefixo=""):
        """Texto vira número: uma coluna 0/1 por valor distinto.

        É 'one-hot', e não um número por categoria: numerar
        'azul=0, verde=1, vermelho=2' faria o modelo achar que vermelho
        é maior que azul, e que verde está no meio dos dois.
        """
        valores = sorted({str(_campo(l, coluna)) for l in linhas or []})
        base = prefixo or coluna
        saida = []
        for linha in linhas or []:
            nova = dict(linha) if isinstance(linha, dict) else {}
            atual = str(_campo(linha, coluna))
            nova.pop(coluna, None)
            for valor in valores:
                nova[f"{base}_{valor}"] = 1 if atual == valor else 0
            saida.append(nova)
        return {"linhas": saida, "colunas": [f"{base}_{v}" for v in valores]}

    @staticmethod
    def _escalonar(linhas, colunas):
        """A média e o desvio de cada coluna, para normalizar depois.

        Sem escala, uma coluna em milhares domina uma em unidades no
        k-NN e na logística — a distância vira a da coluna grande, e as
        outras deixam de existir. Árvore e floresta não precisam: elas
        cortam por coluna, e a grandeza não muda a ordem.
        """
        X = _matriz_de(linhas, colunas)
        escala = {}
        for i, coluna in enumerate(colunas):
            valores = [linha[i] for linha in X]
            media = sum(valores) / len(valores)
            variancia = sum((v - media) ** 2 for v in valores) / len(valores)
            desvio = math.sqrt(variancia)
            # Desvio zero é coluna constante: dividir por ele daria
            # infinito, e a coluna não informa nada mesmo.
            escala[coluna] = {"media": media, "desvio": desvio or 1.0}
        return escala

    @staticmethod
    def _aplicar_escala(linhas, escala):
        saida = []
        for linha in linhas or []:
            nova = dict(linha) if isinstance(linha, dict) else {}
            for coluna, e in escala.items():
                valor = _campo(linha, coluna)
                if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                    nova[coluna] = (float(valor) - e["media"]) / e["desvio"]
            saida.append(nova)
        return saida

    # ── treinar ─────────────────────────────────────────────

    @staticmethod
    def _linear(linhas, alvo, colunas):
        """Regressão linear múltipla, por mínimos quadrados."""
        X = _matriz_de(linhas, colunas)
        y = [float(v) for v in _alvos(linhas, alvo)]
        if len(X) <= len(colunas):
            raise ValueError_(
                f"são {len(colunas)} colunas para {len(X)} linhas.",
                nota="com menos linhas que colunas há infinitas soluções",
                dica="traga mais dados, ou treine com menos colunas",
                doc="tecnicas/ml")
        return Modelo("linear", alvo, colunas, _minimos_quadrados(X, y),
                      treinado_com=len(X))

    @staticmethod
    def _logistica(linhas, alvo, colunas, voltas=300, taxa=0.1):
        """Classificação binária."""
        X = _matriz_de(linhas, colunas)
        brutos = _alvos(linhas, alvo)
        classes = sorted({*brutos}, key=str)
        if len(classes) != 2:
            raise ValueError_(
                f"a logística separa DUAS classes; '{alvo}' tem "
                f"{len(classes)}.",
                nota=f"são: {', '.join(str(c) for c in classes[:6])}",
                dica="use 'floresta' ou 'arvore' para mais de duas",
                doc="tecnicas/ml")
        y = [1.0 if v == classes[1] else 0.0 for v in brutos]
        pesos = _descida_logistica(X, y, int(voltas), float(taxa))
        return Modelo("logistica", alvo, colunas, pesos,
                      classes=[classes[0], classes[1]], treinado_com=len(X))

    @staticmethod
    def _arvore(linhas, alvo, colunas, profundidade=6, minimo=2):
        X = _matriz_de(linhas, colunas)
        y = _alvos(linhas, alvo)
        raiz = _crescer(X, y, int(profundidade), int(minimo))
        return Modelo("arvore", alvo, colunas, raiz,
                      classes=sorted({str(v) for v in y}), treinado_com=len(X))

    @staticmethod
    def _floresta(linhas, alvo, colunas, arvores=20, profundidade=8,
                  minimo=2, semente=SEMENTE):
        """Várias árvores, cada uma vendo uma amostra e um subconjunto.

        Uma árvore sozinha decora o treino. A floresta corrige isso por
        duas fontes de variação: cada árvore vê uma AMOSTRA COM
        REPOSIÇÃO das linhas, e cada corte olha só parte das colunas.
        Sem as duas, as árvores sairiam iguais e a votação não somaria.
        """
        X = _matriz_de(linhas, colunas)
        y = _alvos(linhas, alvo)
        sorteio = random.Random(semente)
        por_corte = max(1, int(math.sqrt(len(colunas))))

        mata = []
        for _ in range(int(arvores)):
            indices = [sorteio.randrange(len(X)) for _ in range(len(X))]
            amostra_X = [X[i] for i in indices]
            amostra_y = [y[i] for i in indices]
            mata.append(_crescer(amostra_X, amostra_y, int(profundidade),
                                 int(minimo), por_corte, sorteio))
        return Modelo("floresta", alvo, colunas, mata,
                      classes=sorted({str(v) for v in y}), treinado_com=len(X))

    @staticmethod
    def _vizinhos(linhas, alvo, colunas, k=5):
        """k-NN. Não treina: guarda, e decide na hora de prever.

        Por isso ele é instantâneo para treinar e lento para prever — o
        contrário de todos os outros.
        """
        X = _matriz_de(linhas, colunas)
        y = _alvos(linhas, alvo)
        if int(k) > len(X):
            raise ValueError_(
                f"k={k} é maior que as {len(X)} linhas de treino.",
                doc="tecnicas/ml")
        return Modelo("vizinhos", alvo, colunas,
                      {"k": int(k), "X": X, "y": y},
                      classes=sorted({str(v) for v in y}), treinado_com=len(X))

    @staticmethod
    def _bayes_texto(linhas, alvo, coluna):
        """Naive Bayes multinomial — classificar texto.

        É o algoritmo por trás de filtro de spam desde os anos 90, e
        continua difícil de bater em texto curto. 'Naive' porque supõe
        que as palavras são independentes, o que é falso e funciona
        assim mesmo.

        A suavização de Laplace (+1) existe para uma palavra nunca vista
        numa classe não zerar a probabilidade inteira — sem ela, uma
        palavra nova torna a classe impossível, e não improvável.
        """
        contagem, totais, documentos = {}, {}, {}
        vocabulario = set()
        for linha in linhas or []:
            classe = _campo(linha, alvo)
            palavras = _palavras(_campo(linha, coluna))
            documentos[classe] = documentos.get(classe, 0) + 1
            por_classe = contagem.setdefault(classe, {})
            for palavra in palavras:
                por_classe[palavra] = por_classe.get(palavra, 0) + 1
                totais[classe] = totais.get(classe, 0) + 1
                vocabulario.add(palavra)

        if not documentos:
            raise ValueError_("não há linhas para treinar.", doc="tecnicas/ml")

        return Modelo("bayes", alvo, [coluna],
                      {"contagem": contagem, "totais": totais,
                       "documentos": documentos,
                       "vocabulario": len(vocabulario)},
                      classes=sorted(documentos, key=str),
                      treinado_com=sum(documentos.values()))

    @staticmethod
    def _kmedias(linhas, colunas, grupos=3, voltas=50, semente=SEMENTE):
        """k-médias, com centros iniciais espalhados (k-means++)."""
        X = _matriz_de(linhas, colunas)
        k = min(int(grupos), len(X))
        sorteio = random.Random(semente)

        # k-means++: o primeiro centro é sorteado, e cada seguinte cai
        # onde está mais longe dos já escolhidos. Sortear todos leva a
        # dois centros no mesmo aglomerado, e um grupo vazio.
        centros = [list(X[sorteio.randrange(len(X))])]
        while len(centros) < k:
            distancias = [min(sum((a - b) ** 2 for a, b in zip(p, c))
                              for c in centros) for p in X]
            total = sum(distancias) or 1.0
            alvo = sorteio.random() * total
            acumulado = 0.0
            for ponto, d in zip(X, distancias):
                acumulado += d
                if acumulado >= alvo:
                    centros.append(list(ponto))
                    break

        rotulos = [0] * len(X)
        for _ in range(int(voltas)):
            mudou = False
            for i, ponto in enumerate(X):
                melhor = min(range(k), key=lambda c: sum(
                    (a - b) ** 2 for a, b in zip(ponto, centros[c])))
                if melhor != rotulos[i]:
                    rotulos[i] = melhor
                    mudou = True
            for c in range(k):
                membros = [p for p, r in zip(X, rotulos) if r == c]
                if membros:
                    centros[c] = [sum(v) / len(membros) for v in zip(*membros)]
            if not mudou:
                break

        inercia = sum(sum((a - b) ** 2 for a, b in
                          zip(ponto, centros[rotulos[i]]))
                      for i, ponto in enumerate(X))
        return {"grupos": rotulos, "centros": centros,
                "inercia": round(inercia, 6), "k": k,
                "tamanhos": [rotulos.count(c) for c in range(k)]}

    @staticmethod
    def _pca(linhas, colunas, componentes=2):
        """Reduz dimensões preservando a variância, por potência iterada.

        Sem álgebra linear pronta, os autovetores saem por iteração de
        potência com deflação: acha o maior, remove-o da matriz, repete.
        É exato o bastante para visualização, que é o uso comum.
        """
        X = _matriz_de(linhas, colunas)
        n = len(colunas)
        medias = [sum(linha[i] for linha in X) / len(X) for i in range(n)]
        centrado = [[v - m for v, m in zip(linha, medias)] for linha in X]

        cov = [[sum(a[i] * a[j] for a in centrado) / max(1, len(X) - 1)
                for j in range(n)] for i in range(n)]

        vetores, valores = [], []
        sorteio = random.Random(SEMENTE)
        for _ in range(min(int(componentes), n)):
            v = [sorteio.random() for _ in range(n)]
            valor = 0.0
            for _ in range(200):
                novo = [sum(cov[i][j] * v[j] for j in range(n)) for i in range(n)]
                norma = math.sqrt(sum(x * x for x in novo))
                if norma < 1e-12:
                    break
                novo = [x / norma for x in novo]
                if sum(abs(a - b) for a, b in zip(novo, v)) < 1e-10:
                    v = novo
                    valor = norma
                    break
                v, valor = novo, norma
            vetores.append(v)
            valores.append(valor)
            # Deflação: tira a direção já achada para a próxima volta
            # não convergir para a mesma.
            for i in range(n):
                for j in range(n):
                    cov[i][j] -= valor * v[i] * v[j]

        total = sum(valores) or 1.0
        projetado = [[sum(p[i] * v[i] for i in range(n)) for v in vetores]
                     for p in centrado]
        return {"pontos": projetado, "componentes": vetores,
                "variancia": [round(x / total, 4) for x in valores],
                "medias": medias}

    # ── usar ────────────────────────────────────────────────

    @staticmethod
    def _prever(modelo, linhas):
        if modelo.especie == "bayes":
            return [ArcaneCortex._bayes_prever(modelo, _campo(l, modelo.colunas[0]))
                    for l in linhas or []]
        X = _matriz_de(linhas, modelo.colunas)
        return [_prever_um(modelo, vetor) for vetor in X]

    @staticmethod
    def _prever_uma_linha(modelo, linha):
        return ArcaneCortex._prever(modelo, [linha])[0]

    @staticmethod
    def _bayes_prever(modelo, texto):
        p = modelo.parametros
        melhor, melhor_valor = None, float("-inf")
        total_docs = sum(p["documentos"].values())
        for classe in p["documentos"]:
            # Em log: multiplicar centenas de probabilidades pequenas
            # chega a zero por falta de precisão do float.
            score = math.log(p["documentos"][classe] / total_docs)
            for palavra in _palavras(texto):
                vistas = p["contagem"].get(classe, {}).get(palavra, 0)
                score += math.log((vistas + 1) /
                                  (p["totais"].get(classe, 0) + p["vocabulario"]))
            if score > melhor_valor:
                melhor, melhor_valor = classe, score
        return melhor

    @staticmethod
    def _probabilidade(modelo, linha):
        """A confiança da previsão, quando o modelo sabe dizer."""
        if modelo.especie == "logistica":
            vetor = _matriz_de([linha], modelo.colunas)[0]
            p = _sigmoide(_linear_prever(modelo.parametros, vetor))
            return {str(modelo.classes[0]): round(1 - p, 4),
                    str(modelo.classes[1]): round(p, 4)}
        if modelo.especie == "floresta":
            vetor = _matriz_de([linha], modelo.colunas)[0]
            votos = {}
            for arvore in modelo.parametros:
                voto = str(_arvore_prever(arvore, vetor))
                votos[voto] = votos.get(voto, 0) + 1
            total = sum(votos.values())
            return {k: round(v / total, 4) for k, v in sorted(votos.items())}
        raise ValueError_(
            f"um modelo '{modelo.especie}' não dá probabilidade.",
            nota="'logistica' e 'floresta' dão",
            doc="tecnicas/ml")

    # ── avaliar ─────────────────────────────────────────────

    @staticmethod
    def _avaliar(modelo, linhas):
        """Mede no que o modelo NÃO viu. Devolve o que importa.

        Para classificação vêm precisão, revocação e F1 além da
        acurácia — num problema com 99% de uma classe, responder sempre
        a mesma coisa acerta 99%, e só o F1 denuncia.
        """
        reais = _alvos(linhas, modelo.alvo)
        previstos = ArcaneCortex._prever(modelo, linhas)

        if modelo.especie == "linear":
            erros = [float(r) - float(p) for r, p in zip(reais, previstos)]
            n = len(erros) or 1
            media_real = sum(float(r) for r in reais) / n
            ss_total = sum((float(r) - media_real) ** 2 for r in reais)
            ss_erro = sum(e * e for e in erros)
            return {
                "linhas": len(linhas),
                "mae": round(sum(abs(e) for e in erros) / n, 6),
                "rmse": round(math.sqrt(ss_erro / n), 6),
                "r2": round(1 - ss_erro / ss_total, 6) if ss_total else 0.0,
            }

        acertos = sum(1 for r, p in zip(reais, previstos) if r == p)
        saida = {"linhas": len(linhas),
                 "acuracia": round(acertos / (len(linhas) or 1), 4),
                 "acertos": acertos, "erros": len(linhas) - acertos}
        saida.update(_metricas_de_classe([str(r) for r in reais],
                                         [str(p) for p in previstos]))
        return saida

    @staticmethod
    def _matriz(modelo, linhas):
        """A matriz de confusão, em texto — onde ele erra, e com o quê."""
        reais = [str(v) for v in _alvos(linhas, modelo.alvo)]
        previstos = [str(v) for v in ArcaneCortex._prever(modelo, linhas)]
        classes, tabela = _matriz_confusao(reais, previstos)
        largura = max(8, max(len(c) for c in classes) + 2)

        cabecalho = "real \\ previsto".ljust(largura + 4)
        cabecalho += "".join(c.rjust(largura) for c in classes)
        saida = [cabecalho, "-" * len(cabecalho)]
        for i, classe in enumerate(classes):
            linha = classe.ljust(largura + 4)
            linha += "".join(str(tabela[i][j]).rjust(largura)
                             for j in range(len(classes)))
            saida.append(linha)
        return "\n".join(saida)

    @staticmethod
    def _validacao_cruzada(linhas, alvo, colunas, especie="floresta",
                           dobras=5, semente=SEMENTE, **extras):
        """Treina k vezes, cada uma testando numa fatia diferente.

        Uma divisão só mede um sorteio. Com 200 linhas, a diferença
        entre duas sementes chega a dez pontos de acurácia — e escolher
        um modelo por causa disso é escolher pelo sorteio.

        O DESVIO entre as dobras diz mais que a média: um modelo que
        varia muito entre elas não é confiável, por melhor que seja a
        média.
        """
        treinar = {"linear": ArcaneCortex._linear,
                   "logistica": ArcaneCortex._logistica,
                   "arvore": ArcaneCortex._arvore,
                   "floresta": ArcaneCortex._floresta,
                   "vizinhos": ArcaneCortex._vizinhos}.get(especie)
        if treinar is None:
            raise ValueError_(
                f"não sei treinar um modelo '{especie}'.",
                nota="há: linear, logistica, arvore, floresta, vizinhos",
                doc="tecnicas/ml")

        copia = ArcaneCortex._embaralhar(linhas, semente)
        k = max(2, min(int(dobras), len(copia)))
        tamanho = len(copia) // k
        resultados = []

        for dobra in range(k):
            inicio = dobra * tamanho
            fim = inicio + tamanho if dobra < k - 1 else len(copia)
            teste = copia[inicio:fim]
            treino = copia[:inicio] + copia[fim:]
            if not treino or not teste:
                continue
            modelo = treinar(treino, alvo, colunas, **extras)
            r = ArcaneCortex._avaliar(modelo, teste)
            resultados.append(r.get("acuracia", r.get("r2", 0.0)))

        media = sum(resultados) / len(resultados) if resultados else 0.0
        variancia = (sum((x - media) ** 2 for x in resultados) /
                     len(resultados)) if resultados else 0.0
        return {"dobras": len(resultados),
                "por_dobra": [round(x, 4) for x in resultados],
                "media": round(media, 4),
                "desvio": round(math.sqrt(variancia), 4)}

    @staticmethod
    def _importancia(modelo):
        """Quais colunas o modelo mais usa para decidir."""
        if modelo.especie == "linear":
            pesos = modelo.parametros[1:]
            total = sum(abs(p) for p in pesos) or 1.0
            return {c: round(abs(p) / total, 4)
                    for c, p in zip(modelo.colunas, pesos)}
        if modelo.especie == "arvore":
            contagens = _importancia(modelo.parametros, len(modelo.colunas))
        elif modelo.especie == "floresta":
            contagens = [0] * len(modelo.colunas)
            for arvore in modelo.parametros:
                _importancia(arvore, len(modelo.colunas), contagens)
        else:
            raise ValueError_(
                f"um modelo '{modelo.especie}' não diz a importância.",
                nota="'linear', 'arvore' e 'floresta' dizem",
                doc="tecnicas/ml")
        total = sum(contagens) or 1
        return {c: round(n / total, 4)
                for c, n in sorted(zip(modelo.colunas, contagens),
                                   key=lambda x: -x[1])}

    @staticmethod
    def _acuracia(reais, previstos):
        pares = list(zip(reais, previstos))
        return round(sum(1 for r, p in pares if r == p) / (len(pares) or 1), 4)

    @staticmethod
    def _erro(reais, previstos):
        """MAE, RMSE e R² de duas listas de números."""
        erros = [float(r) - float(p) for r, p in zip(reais, previstos)]
        n = len(erros) or 1
        media = sum(float(r) for r in reais) / n
        ss_total = sum((float(r) - media) ** 2 for r in reais)
        ss_erro = sum(e * e for e in erros)
        return {"mae": round(sum(abs(e) for e in erros) / n, 6),
                "rmse": round(math.sqrt(ss_erro / n), 6),
                "r2": round(1 - ss_erro / ss_total, 6) if ss_total else 0.0}

    # ── guardar ─────────────────────────────────────────────

    @staticmethod
    def _salvar(modelo, caminho):
        """O modelo em JSON — legível, versionável, sem pickle.

        Pickle executaria código ao carregar: um modelo baixado de
        qualquer lugar viraria execução arbitrária. JSON não tem esse
        problema, e ainda dá para ler o arquivo e entender o que ele é.
        """
        pasta = os.path.dirname(caminho)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        temporario = caminho + ".parcial"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(modelo.para_vault(), f, ensure_ascii=False,
                      indent=2, default=str)
        os.replace(temporario, caminho)
        return {"arquivo": caminho, "especie": modelo.especie,
                "bytes": os.path.getsize(caminho)}

    @staticmethod
    def _carregar(caminho):
        with open(caminho, encoding="utf-8") as f:
            d = json.load(f)
        modelo = Modelo(d["especie"], d["alvo"], d["colunas"],
                        d["parametros"], d.get("classes"), d.get("escala"),
                        d.get("treinado_com", 0))
        if modelo.especie == "bayes":
            # O JSON transforma toda chave em texto; a contagem por
            # classe precisa voltar como veio, senão a previsão erra a
            # classe por comparar 'True' com True.
            p = modelo.parametros
            p["documentos"] = dict(p.get("documentos", {}))
            p["totais"] = dict(p.get("totais", {}))
        return modelo

    @staticmethod
    def _resumo(modelo):
        """O que este modelo é, em uma linha por informação."""
        return {"especie": modelo.especie, "alvo": modelo.alvo,
                "colunas": modelo.colunas,
                "classes": modelo.classes,
                "treinado_com": modelo.treinado_com}
