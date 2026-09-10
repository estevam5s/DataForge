# -*- coding: utf-8 -*-
"""
Arcane.Pipeline — orquestração de ETL/ELT.

    adopt Arcane.Pipeline as P

    fluxo := P.fluxo("vendas")

    P.etapa(fluxo, "extrair", extrair)
    P.etapa(fluxo, "limpar", limpar, ["extrair"])
    P.etapa(fluxo, "agregar", agregar, ["limpar"])
    P.etapa(fluxo, "carregar", carregar, ["agregar"])

    relatorio := P.rodar(fluxo)

Airflow, Prefect e Dagster resolvem isto com um servidor, um banco e um
agendador. Aqui é uma estrutura de dados e um laço — o que cabe num
processo só, que é onde a maioria dos pipelines de verdade vive.

─── O que um DAG precisa garantir ──────────────────────────

1. **Ordem.** Uma etapa só roda depois das que ela declara depender.
   A ordenação é topológica, e um ciclo é ERRO — não aviso: um ciclo
   não tem ordem possível, e escolher uma arbitrariamente produziria um
   resultado que ninguém consegue explicar.

2. **Não repetir trabalho.** Cada etapa roda uma vez por execução, e o
   resultado dela fica disponível para as seguintes.

3. **Falha não é silêncio.** Quando uma etapa falha, as que dependem
   dela são PULADAS, não executadas com entrada faltando. Rodar mesmo
   assim produz dado corrompido, que é pior que dado ausente — o
   ausente alguém percebe.

─── Incremental ────────────────────────────────────────────

Reprocessar tudo a cada execução é o que faz um pipeline de 10 minutos
virar um de 6 horas em dois anos. 'marca_de_agua' guarda até onde já se
leu, e devolve isso na próxima execução:

    ultima := P.marca(fluxo, "vendas")        // void na primeira vez
    novos := ler(desde: ultima)
    P.marcar(fluxo, "vendas", maior_data)

O checkpoint só avança quando a execução INTEIRA termina bem. Avançar
por etapa deixaria a marca à frente do que foi carregado, e o que ficou
no meio some para sempre — silenciosamente.
"""

import json
import os
import time
import traceback

from ..errors import ValueError_

#: Como uma etapa pode terminar.
OK, FALHOU, PULADA, SALTADA = "ok", "falhou", "pulada", "saltada"


class Etapa:
    """Uma etapa e o que se sabe dela."""

    __slots__ = ("nome", "acao", "depende_de", "tentativas", "espera",
                 "quando", "opcional", "descricao")

    def __init__(self, nome, acao, depende_de=None, tentativas=1,
                 espera=0.0, quando=None, opcional=False, descricao=""):
        self.nome = nome
        self.acao = acao
        self.depende_de = list(depende_de or [])
        self.tentativas = max(1, int(tentativas))
        self.espera = float(espera)
        self.quando = quando
        self.opcional = bool(opcional)
        self.descricao = descricao


class Fluxo:
    """O DAG e o estado que atravessa execuções."""

    def __init__(self, nome, estado=None):
        self.nome = nome
        self.etapas = {}
        self.ordem_declarada = []
        self.arquivo_estado = estado
        self.marcas = {}
        self.historico = []
        if estado and os.path.isfile(estado):
            try:
                with open(estado, encoding="utf-8") as f:
                    guardado = json.load(f)
                self.marcas = guardado.get("marcas", {})
                self.historico = guardado.get("historico", [])
            except (OSError, json.JSONDecodeError):
                # Estado corrompido não pode impedir o pipeline de
                # rodar: ele reprocessa mais do que precisava, que é
                # ruim — mas parar de rodar é pior.
                self.marcas, self.historico = {}, []

    def gravar(self):
        if not self.arquivo_estado:
            return
        pasta = os.path.dirname(self.arquivo_estado)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        temporario = self.arquivo_estado + ".parcial"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump({"fluxo": self.nome, "marcas": self.marcas,
                       "historico": self.historico[-50:]}, f,
                      ensure_ascii=False, indent=2, default=str)
        # Renomeia: gravar direto deixa o checkpoint pela metade se a
        # máquina cair, e um checkpoint pela metade é pior que nenhum.
        os.replace(temporario, self.arquivo_estado)


def _ordenar(fluxo):
    """A ordem topológica, ou erro se houver ciclo.

    Kahn: quem não depende de ninguém sai primeiro, e cada saída
    libera quem dependia dela. Sobrar alguém no fim significa
    dependência circular — e não há ordem possível.

    A ordem de DECLARAÇÃO desempata. Sem isso, dois pipelines com as
    mesmas etapas rodariam em ordens diferentes entre execuções, e um
    bug que só aparece numa das ordens seria irreproduzível.
    """
    restantes = {n: set(e.depende_de) for n, e in fluxo.etapas.items()}
    for nome, faltando in restantes.items():
        desconhecidas = faltando - set(fluxo.etapas)
        if desconhecidas:
            raise ValueError_(
                f"a etapa '{nome}' depende de "
                f"{', '.join(sorted(desconhecidas))}, que não existe.",
                dica="confira o nome, ou declare a etapa antes de rodar",
                doc="tecnicas/pipeline")

    posicao = {n: i for i, n in enumerate(fluxo.ordem_declarada)}
    saida = []
    while restantes:
        prontas = sorted((n for n, d in restantes.items() if not d),
                         key=lambda n: posicao.get(n, 0))
        if not prontas:
            ciclo = ", ".join(sorted(restantes))
            raise ValueError_(
                f"as etapas {ciclo} dependem umas das outras.",
                nota="um ciclo não tem ordem possível",
                dica="quebre o ciclo, ou junte as etapas numa só",
                doc="tecnicas/pipeline")
        for nome in prontas:
            saida.append(nome)
            restantes.pop(nome)
            for d in restantes.values():
                d.discard(nome)
    return saida


class ArcanePipeline(dict):
    """Orquestração de ETL/ELT: DAG, retry, incremental e métricas."""

    def __new__(cls):
        return {
            # montar
            "fluxo": cls._fluxo,
            "etapa": cls._etapa,
            "ordem": cls._ordem,
            "grafico": cls._grafico,

            # rodar
            "rodar": cls._rodar,
            "rodar_ate": cls._rodar_ate,

            # incremental
            "marca": cls._marca,
            "marcar": cls._marcar,
            "esquecer_marca": cls._esquecer_marca,

            # observar
            "historico": cls._historico,
            "ultima_execucao": cls._ultima_execucao,
        }

    # ── montar ──────────────────────────────────────────────

    @staticmethod
    def _fluxo(nome, estado=""):
        """Um fluxo novo. Com 'estado', ele lembra entre execuções."""
        return Fluxo(nome, estado or None)

    @staticmethod
    def _etapa(fluxo, nome, acao, depende_de=None, tentativas=1,
               espera=0, quando=None, opcional=False, descricao=""):
        """Acrescenta uma etapa.

        'tentativas' e 'espera' cobrem a falha passageira — rede, banco
        ocupado — que é a mais comum num pipeline e a que menos merece
        acordar alguém.

        'quando' é uma condição: a etapa é SALTADA quando ela dá falso.
        É como se roda o mesmo fluxo em modos diferentes sem duplicá-lo.
        """
        if nome in fluxo.etapas:
            raise ValueError_(
                f"a etapa '{nome}' já existe neste fluxo.",
                dica="cada etapa tem um nome só; renomeie uma delas",
                doc="tecnicas/pipeline")
        fluxo.etapas[nome] = Etapa(nome, acao, depende_de, tentativas,
                                   espera, quando, opcional, descricao)
        fluxo.ordem_declarada.append(nome)
        return fluxo

    @staticmethod
    def _ordem(fluxo):
        """A ordem em que as etapas vão rodar."""
        return _ordenar(fluxo)

    @staticmethod
    def _grafico(fluxo):
        """O DAG em texto, para conferir antes de rodar."""
        linhas = [f"{fluxo.nome}"]
        for nome in _ordenar(fluxo):
            etapa = fluxo.etapas[nome]
            de = f"  ← {', '.join(etapa.depende_de)}" if etapa.depende_de else ""
            marca = " (opcional)" if etapa.opcional else ""
            linhas.append(f"  {nome}{marca}{de}")
        return "\n".join(linhas)

    # ── rodar ───────────────────────────────────────────────

    @staticmethod
    def _rodar(fluxo, contexto=None, ate=None):
        """Roda o fluxo inteiro e devolve o relatório.

        O relatório é o produto: sem ele, saber o que aconteceu exige
        ler log, e log de pipeline é o que ninguém lê até quebrar.
        """
        ordem = _ordenar(fluxo)
        if ate:
            if ate not in fluxo.etapas:
                raise ValueError_(f"não há etapa '{ate}' neste fluxo.",
                                  doc="tecnicas/pipeline")
            precisa = _ate_incluindo(fluxo, ate)
            ordem = [n for n in ordem if n in precisa]

        estado = dict(contexto or {})
        resultados = {}
        etapas = []
        falhou_alguma = False
        inicio = time.time()

        for nome in ordem:
            etapa = fluxo.etapas[nome]
            quebradas = [d for d in etapa.depende_de
                         if resultados.get(d, {}).get("estado") in
                         (FALHOU, PULADA)]
            if quebradas:
                # Rodar com entrada faltando produz dado corrompido, que
                # é pior que dado ausente: o ausente alguém percebe.
                etapas.append(_registro(nome, PULADA, 0, 0,
                                        f"depende de {', '.join(quebradas)}"))
                resultados[nome] = etapas[-1]
                continue

            if etapa.quando is not None and not _verdadeiro(etapa.quando, estado):
                etapas.append(_registro(nome, SALTADA, 0, 0,
                                        "a condição deu falso"))
                resultados[nome] = etapas[-1]
                continue

            registro = _rodar_etapa(etapa, estado)
            etapas.append(registro)
            resultados[nome] = registro
            if registro["estado"] == OK:
                estado[nome] = registro.get("valor")
            elif not etapa.opcional:
                falhou_alguma = True

        duracao = time.time() - inicio
        relatorio = {
            "fluxo": fluxo.nome,
            "quando": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "ok": not falhou_alguma,
            "duracao": round(duracao, 4),
            "etapas": etapas,
            "resultados": {k: v.get("valor") for k, v in resultados.items()
                           if v["estado"] == OK},
            "resumo": {
                "total": len(etapas),
                OK: sum(1 for e in etapas if e["estado"] == OK),
                FALHOU: sum(1 for e in etapas if e["estado"] == FALHOU),
                PULADA: sum(1 for e in etapas if e["estado"] == PULADA),
                SALTADA: sum(1 for e in etapas if e["estado"] == SALTADA),
            },
        }

        fluxo.historico.append({k: relatorio[k] for k in
                                ("quando", "ok", "duracao", "resumo")})
        # O checkpoint só avança quando a execução INTEIRA deu certo.
        # Gravar depois de uma falha deixaria a marca à frente do que
        # foi carregado, e o que ficou no meio some — em silêncio.
        if not falhou_alguma:
            fluxo.gravar()
        return relatorio

    @staticmethod
    def _rodar_ate(fluxo, etapa, contexto=None):
        """Roda só o que a etapa precisa, e para nela."""
        return ArcanePipeline._rodar(fluxo, contexto, ate=etapa)

    # ── incremental ─────────────────────────────────────────

    @staticmethod
    def _marca(fluxo, chave, padrao=None):
        """Até onde já se leu. 'void' na primeira execução."""
        return fluxo.marcas.get(chave, padrao)

    @staticmethod
    def _marcar(fluxo, chave, valor):
        """Guarda até onde se leu. Só vai ao disco no fim da execução."""
        fluxo.marcas[chave] = valor
        return valor

    @staticmethod
    def _esquecer_marca(fluxo, chave=""):
        """Apaga a marca — a próxima execução reprocessa tudo."""
        if chave:
            fluxo.marcas.pop(chave, None)
        else:
            fluxo.marcas.clear()
        fluxo.gravar()
        return True

    # ── observar ────────────────────────────────────────────

    @staticmethod
    def _historico(fluxo, quantos=10):
        return fluxo.historico[-int(quantos):]

    @staticmethod
    def _ultima_execucao(fluxo):
        return fluxo.historico[-1] if fluxo.historico else None


def _ate_incluindo(fluxo, alvo):
    """O alvo e tudo de que ele depende, direta ou indiretamente."""
    precisa, pilha = set(), [alvo]
    while pilha:
        nome = pilha.pop()
        if nome in precisa:
            continue
        precisa.add(nome)
        pilha.extend(fluxo.etapas[nome].depende_de)
    return precisa


def _verdadeiro(condicao, estado):
    """A condição de 'quando' — ação ou valor."""
    if callable(condicao):
        try:
            return bool(condicao(estado))
        except TypeError:
            return bool(condicao())
    return bool(condicao)


def _registro(nome, estado, duracao, tentativas, motivo="", valor=None):
    saida = {"etapa": nome, "estado": estado,
             "duracao": round(duracao, 4), "tentativas": tentativas}
    if motivo:
        saida["motivo"] = motivo
    if valor is not None:
        saida["valor"] = valor
    return saida


def _rodar_etapa(etapa, estado):
    """Roda uma etapa, com as tentativas que ela pediu."""
    inicio = time.time()
    ultimo_erro = None

    for tentativa in range(1, etapa.tentativas + 1):
        try:
            valor = _chamar(etapa.acao, estado)
            return _registro(etapa.nome, OK, time.time() - inicio,
                             tentativa, "", valor)
        except Exception as erro:                       # noqa: BLE001
            ultimo_erro = erro
            if tentativa < etapa.tentativas:
                # Espera crescente: se o banco está ocupado, insistir no
                # mesmo ritmo mantém ele ocupado.
                time.sleep(etapa.espera * tentativa)

    mensagem = getattr(ultimo_erro, "message", None) or str(ultimo_erro)
    registro = _registro(etapa.nome, FALHOU, time.time() - inicio,
                         etapa.tentativas, mensagem)
    registro["tipo_do_erro"] = type(ultimo_erro).__name__.rstrip("_")
    registro["rastro"] = "".join(traceback.format_exception_only(
        type(ultimo_erro), ultimo_erro)).strip()
    return registro


def _chamar(acao, estado):
    """Chama a ação com o contexto, ou sem — o que ela aceitar.

    Uma etapa que não usa nada do que veio antes não deveria ser
    obrigada a declarar um parâmetro que ignora.
    """
    try:
        return acao(estado)
    except TypeError as erro:
        if "argument" not in str(erro) and "positional" not in str(erro):
            raise
        return acao()
