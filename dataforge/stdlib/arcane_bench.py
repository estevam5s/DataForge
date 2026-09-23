# -*- coding: utf-8 -*-
"""Arcane.Bench — medir, comparar, e descobrir a classe de custo.

O que faltava
-------------
A linguagem sabia dizer a complexidade que ela LE no codigo
(`dataforge complexidade`, `complexidade.py`), e nao sabia dizer a que
ela MEDE rodando. As duas respondem perguntas diferentes, e as duas
erram sozinhas:

    a analise estatica   ve 'cycle dentro de cycle' e diz O(n^2) —
                         mesmo que o laco interno rode tres vezes

    a medicao            ve o tempo de verdade, com o cache, o GIL e o
                         interpretador dentro — e nao sabe o que vai
                         acontecer com n dez vezes maior

`Bench.classe` fecha a lacuna: mede em tamanhos crescentes e responde
qual curva descreve o que aconteceu.

Como ele decide
---------------
Dobrando `n`, o tempo se multiplica por um fator que e a assinatura da
classe:

    O(1)          1.0      o tempo nao muda
    O(log n)      ~1.1     cresce devagar demais para medir bem
    O(n)          2.0      dobra
    O(n log n)    ~2.1     dobra e um pouco
    O(n^2)        4.0      quadruplica
    O(n^3)        8.0
    O(2^n)        explode

A conta e a MEDIANA dos fatores entre medidas consecutivas, e nao a
media: uma pausa do coletor de lixo no meio de uma amostra vira um
fator absurdo, e a media o carrega para sempre.

`O(n)` e `O(n log n)` ficam a 0.1 de distancia, e nenhuma medicao os
separa com honestidade abaixo de uns cem mil itens. Quando os dois
cabem, a resposta traz os DOIS — dizer um numero que nao se mediu e
pior que dizer "entre estes dois".

Tres decisoes
-------------
1. **Aquece antes de medir.** A primeira chamada paga a compilacao dos
   fechamentos, a alocacao dos escopos e o cache frio. Sem o
   aquecimento, a primeira amostra e sempre a mais lenta, e a curva
   inteira sai torta na direcao de "melhor que linear".

2. **Repete e fica com o MENOR tempo, nao com a media.** O menor e o
   mais proximo do custo real: tudo o que atrapalha (outro processo, o
   coletor, o escalonador) so faz o tempo SUBIR. A media mede a
   maquina; o minimo mede o codigo.

3. **`comparar` roda as implementacoes INTERCALADAS**, e nao uma
   inteira depois da outra. Rodar em bloco faz a segunda pegar o cache
   quente que a primeira deixou — e a ordem passa a decidir quem
   ganha.
"""

import gc
import math
import statistics
import time

from ..errors import RuntimeError_, TypeError_


class ErroDeBench(RuntimeError_):
    CODIGO = "DF1201"


#: As classes, e o fator esperado ao DOBRAR n.
#:
#: A ordem importa: a busca para na primeira que cabe, e ela vai da
#: mais barata para a mais cara. Empatar para cima seria o erro caro —
#: dizer O(n) sobre algo O(n^2) manda a pessoa dormir tranquila.
CLASSES = (
    ("O(1)",        1.00, 0.35),
    ("O(log n)",    1.15, 0.30),
    ("O(n)",        2.00, 0.32),
    ("O(n log n)",  2.15, 0.30),
    ("O(n^2)",      4.00, 0.80),
    ("O(n^3)",      8.00, 1.60),
)

#: O exponencial NAO tem fator fixo, e por isso ficou fora da tabela.
#:
#: Dobrar n num O(2^n) multiplica o tempo por 2^n — que depende de n.
#: A assinatura dele nao e um numero, e sim o fator CRESCENDO entre uma
#: medida e a seguinte. Dar-lhe um centro na tabela criava sobreposicao
#: com O(n^3): com folga larga o bastante para pegar o exponencial, o
#: fator 8,0 de um cubico casava com os dois.
LIMITE_EXPONENCIAL = 1.8


def _mediana(valores):
    return statistics.median(valores) if valores else 0.0


def _chamador(acao, argumento):
    """Como chamar a acao: com o argumento, ou sem nenhum.

    `Bench.medir(minha_acao)` — a forma mais obvia da chamada —
    falhava para TODA acao sem parametro, porque a medida chamava
    `acao(None)` sempre. E o erro culpava quem escreveu:

        a acao 'trabalho' recebe 0 argumento(s), e foram passados 1

    A aridade e PERGUNTADA, e nao adivinhada: uma acao da linguagem
    chega aqui como `DFAction`, cujo `__call__` e `(*args, **kwargs)`
    — `inspect.signature` responde dois para todas elas. E a mesma
    razao de `aridade_de` existir para o `curry`.
    """
    if argumento is not None:
        return lambda: acao(argumento)
    from ..builtins import aridade_de
    return (lambda: acao()) if aridade_de(acao, padrao=1) == 0 else (
        lambda: acao(argumento))


def _medir_uma(acao, argumento, repeticoes, aquecer):
    """O MENOR tempo de N repeticoes, em segundos.

    O menor, e nao a media: tudo o que interfere — outro processo, o
    coletor, o escalonador — so faz o tempo subir. A media mede a
    maquina, o minimo mede o codigo.
    """
    chamar = _chamador(acao, argumento)
    for _ in range(aquecer):
        chamar()

    # O coletor desligado durante a medida. Uma coleta que caia no meio
    # de uma amostra e no meio de outra nao vira ruido: vira inclinacao.
    ligado = gc.isenabled()
    gc.disable()
    try:
        melhor = None
        for _ in range(max(1, repeticoes)):
            inicio = time.perf_counter()
            chamar()
            gasto = time.perf_counter() - inicio
            if melhor is None or gasto < melhor:
                melhor = gasto
        return melhor or 0.0
    finally:
        if ligado:
            gc.enable()


def _fatores(pontos):
    """O fator de crescimento entre medidas consecutivas.

    Normalizado para "quanto o tempo cresce quando n DOBRA", porque so
    assim tamanhos que nao dobram exatamente (100, 250, 500) entram na
    mesma conta.
    """
    saida = []
    for (n1, t1), (n2, t2) in zip(pontos, pontos[1:]):
        if n1 <= 0 or t1 <= 0 or n2 <= n1:
            continue
        razao_n = n2 / n1
        razao_t = t2 / t1
        # O fator medido vale para a razao que HOUVE entre os tamanhos.
        # Elevar ao expoente log(2)/log(razao_n) o converte para "por
        # dobra" — e so assim tamanhos que nao dobram (100, 250, 500)
        # entram na mesma tabela que os que dobram.
        saida.append(razao_t ** (math.log(2) / math.log(razao_n)))
    return saida


def _classificar(fatores):
    """A classe que o fator medido descreve — ou o intervalo onde ele cai.

    Tres respostas possiveis, e cada uma diz uma coisa diferente:

        ["O(n^2)"]              o fator bate com uma classe so
        ["O(n)", "O(n log n)"]  bate com duas, e a medicao nao as separa
        ["entre O(n) e O(n^2)"] nao bate com nenhuma, e cai ENTRE duas

    O terceiro caso e real e comum. 's += "x"' num laco mede fator 2,7:
    nao e linear (2,0) nem quadratico (4,0), porque o CPython otimiza
    parte das concatenacoes e nao todas. Responder "indeterminado" ali
    escondia a informacao mais util que havia — que o custo esta entre
    os dois, e que ele PIORA conforme n cresce.
    """
    if not fatores:
        return ["indeterminado"]
    f = _mediana(fatores)

    # O exponencial primeiro, porque ele nao e um ponto na tabela.
    #
    # Dobrar n num O(2^n) multiplica o tempo por 2^n: o fator cresce a
    # cada medida, e e ISSO que o identifica. Um O(n^3) tem fator 8,0
    # estavel; um O(2^n) vai de 4 para 16 para 256.
    if len(fatores) >= 2 and fatores[0] > 0:
        crescimento = fatores[-1] / fatores[0]
        if crescimento >= LIMITE_EXPONENCIAL and fatores[-1] > 8:
            return ["O(2^n) ou pior"]

    cabem = [nome for nome, esperado, folga in CLASSES
             if abs(f - esperado) <= folga]
    if cabem:
        # Duas vizinhas que cabem: a medicao nao as separa, e dizer uma
        # so seria inventar precisao.
        return cabem[:2]

    if f > CLASSES[-1][1]:
        return ["pior que O(n^3)"]
    if f < CLASSES[0][1]:
        return ["O(1)"]

    # Entre duas classes conhecidas: nomeia as duas.
    for (nome_a, esperado_a, _), (nome_b, esperado_b, _) in zip(CLASSES,
                                                               CLASSES[1:]):
        if esperado_a < f < esperado_b:
            return [f"entre {nome_a} e {nome_b}"]
    return ["indeterminado"]


class ArcaneBench(dict):
    """Medir, comparar, e descobrir a classe de custo."""

    def __new__(cls):
        return {
            # ── medir ──
            "medir": cls._medir,
            "repetir": cls._repetir,

            # ── comparar ──
            "comparar": cls._comparar,

            # ── escalar ──
            "classe": cls._classe,
            "curva": cls._curva,

            # ── apresentar ──
            "tabela": cls._tabela,
            "relatorio": cls._relatorio,
        }

    # ── medir ────────────────────────────────────────────────

    @staticmethod
    def _medir(acao, argumento=None, repeticoes=5, aquecer=1):
        """O tempo de UMA acao, em milissegundos.

        Devolve vault com 'ms', 'repeticoes' e 'por_segundo' — o
        ultimo porque "quantos por segundo" e o numero que se compara
        com o de outra linguagem, e 'ms' sozinho nao e.
        """
        if not callable(acao):
            raise TypeError_(
                "Bench.medir expects an action.",
                dica="pass the action itself, without calling it: "
                     "Bench.medir(minha_acao), not Bench.medir(minha_acao())",
                doc="tecnicas/bench")

        segundos = _medir_uma(acao, argumento, repeticoes, aquecer)
        return {
            "ms": round(segundos * 1000, 4),
            "segundos": round(segundos, 7),
            "repeticoes": repeticoes,
            "por_segundo": round(1 / segundos, 2) if segundos > 0 else 0.0,
        }

    @staticmethod
    def _repetir(acao, vezes, argumento=None):
        """A acao N vezes, e o tempo TOTAL e o MEDIO.

        Para trabalho curto demais para medir uma vez: mil chamadas de
        um microssegundo sao mensuraveis, uma nao e.
        """
        ligado = gc.isenabled()
        gc.disable()
        try:
            inicio = time.perf_counter()
            for _ in range(int(vezes)):
                acao(argumento)
            total = time.perf_counter() - inicio
        finally:
            if ligado:
                gc.enable()
        return {
            "total_ms": round(total * 1000, 4),
            "media_ms": round(total * 1000 / max(1, vezes), 6),
            "vezes": int(vezes),
            "por_segundo": round(vezes / total, 2) if total > 0 else 0.0,
        }

    # ── comparar ─────────────────────────────────────────────

    @staticmethod
    def _comparar(implementacoes, argumento=None, repeticoes=5, aquecer=1):
        """Varias implementacoes do MESMO trabalho, lado a lado.

        Elas rodam INTERCALADAS, e nao uma inteira depois da outra:
        em bloco, a segunda pega o cache quente que a primeira deixou,
        e a ORDEM passa a decidir quem ganha.
        """
        if not isinstance(implementacoes, dict) or not implementacoes:
            raise ErroDeBench(
                "Bench.comparar expects a vault of name -> action.",
                dica='Bench.comparar({"com laco": a, "com pipeline": b})',
                doc="tecnicas/bench")

        nomes = list(implementacoes)
        for nome in nomes:
            if not callable(implementacoes[nome]):
                raise TypeError_(
                    f"'{nome}' is not an action.",
                    dica="the vault maps a name to the action itself",
                    doc="tecnicas/bench")

        for nome in nomes:
            for _ in range(aquecer):
                implementacoes[nome](argumento)

        melhores = {nome: None for nome in nomes}
        ligado = gc.isenabled()
        gc.disable()
        try:
            for _ in range(max(1, repeticoes)):
                for nome in nomes:           # intercalado, de proposito
                    inicio = time.perf_counter()
                    implementacoes[nome](argumento)
                    gasto = time.perf_counter() - inicio
                    if melhores[nome] is None or gasto < melhores[nome]:
                        melhores[nome] = gasto
        finally:
            if ligado:
                gc.enable()

        rapido = min(melhores.values()) or 1e-12
        linhas = []
        for nome in sorted(nomes, key=lambda n: melhores[n]):
            segundos = melhores[nome]
            linhas.append({
                "nome": nome,
                "ms": round(segundos * 1000, 4),
                "vezes": round(segundos / rapido, 2),
                "mais_rapido": segundos <= rapido,
            })
        return {
            "resultados": linhas,
            "vencedor": linhas[0]["nome"],
            "repeticoes": repeticoes,
        }

    # ── escalar ──────────────────────────────────────────────

    @staticmethod
    def _curva(acao, tamanhos, preparar=None, repeticoes=3, aquecer=1):
        """O tempo em cada tamanho, e o fator entre eles.

        'preparar' recebe o tamanho e devolve o que a acao vai receber —
        e ela roda FORA da medida. Sem essa separacao, construir a
        entrada de cem mil itens entra na conta e some a curva do que
        se queria medir.
        """
        pontos = []
        for n in tamanhos:
            entrada = preparar(n) if callable(preparar) else n
            segundos = _medir_uma(acao, entrada, repeticoes, aquecer)
            pontos.append((float(n), segundos))

        fatores = _fatores(pontos)
        return {
            "pontos": [{"n": int(n), "ms": round(t * 1000, 4)}
                       for n, t in pontos],
            "fatores": [round(f, 3) for f in fatores],
            "fator": round(_mediana(fatores), 3) if fatores else 0.0,
        }

    @staticmethod
    def _classe(acao, tamanhos=None, preparar=None, repeticoes=3):
        """Qual curva descreve o que foi MEDIDO.

        Devolve as classes que cabem no fator — uma, ou as duas
        vizinhas quando a medicao nao as separa. Dizer 'O(n)' sobre uma
        amostra que tambem cabe em 'O(n log n)' e inventar precisao.
        """
        tamanhos = list(tamanhos or (1000, 2000, 4000, 8000))
        if len(tamanhos) < 3:
            raise ErroDeBench(
                "at least three sizes are needed to see a curve.",
                nota="with two points every curve is a straight line",
                dica="Bench.classe(f, [1000, 2000, 4000, 8000])",
                doc="tecnicas/bench")

        curva = ArcaneBench._curva(acao, tamanhos, preparar, repeticoes)
        classes = _classificar([f for f in curva["fatores"]])
        return {
            **curva,
            "classes": classes,
            "classe": classes[0],
            "certeza": "exata" if len(classes) == 1 else "entre duas",
        }

    # ── apresentar ───────────────────────────────────────────

    @staticmethod
    def _tabela(resultado):
        """Uma comparacao como texto de largura fixa, para o terminal."""
        linhas = resultado.get("resultados") if isinstance(resultado, dict) else None
        if not linhas:
            return ""
        largura = max(len(l["nome"]) for l in linhas)
        saida = []
        for l in linhas:
            marca = "*" if l["mais_rapido"] else " "
            saida.append(f"{marca} {l['nome']:<{largura}}  "
                         f"{l['ms']:>10.4f} ms  {l['vezes']:>6.2f}x")
        return "\n".join(saida)

    @staticmethod
    def _relatorio(resultado):
        """A curva como texto, com o fator e a classe."""
        if not isinstance(resultado, dict) or "pontos" not in resultado:
            return ""
        saida = ["         n          ms     fator"]
        anterior = None
        for i, p in enumerate(resultado["pontos"]):
            fator = ""
            if anterior is not None and i - 1 < len(resultado["fatores"]):
                fator = f"{resultado['fatores'][i - 1]:>8.2f}"
            saida.append(f"  {p['n']:>8}  {p['ms']:>10.4f}  {fator}")
            anterior = p
        if "classe" in resultado:
            classes = " ou ".join(resultado.get("classes", []))
            saida.append("")
            saida.append(f"  fator medio {resultado['fator']:.2f}  ->  {classes}")
        return "\n".join(saida)
