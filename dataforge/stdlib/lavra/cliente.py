# -*- coding: utf-8 -*-
"""Falar com um servidor Lavra — o daqui, ou o de outro serviço.

Sobre a Malha, e não sobre um HTTP cru
--------------------------------------
Uma chamada de rede tem três desfechos, e o terceiro é "não se sabe".
`Arcane.Malha` já resolve retentativa com recuo, disjuntor, propagação
de rastro e idempotência — e reimplementar isso aqui daria uma versão
pior das mesmas coisas.

O cliente do Lavra é fino de propósito: ele monta o corpo, chama a
Malha e lê a resposta.
"""

import json


def _malha():
    from ..arcane_malha import ArcaneMalha
    return ArcaneMalha


class Cliente:
    """Um servidor Lavra, do ponto de vista de quem consulta."""

    def __init__(self, url, cabecalhos=None, cliente_malha=None,
                 tempo_limite=10.0):
        self.url = url.rstrip("/")
        self.cabecalhos = dict(cabecalhos or {})
        self.cabecalhos.setdefault("Content-Type", "application/json")
        self.tempo_limite = tempo_limite
        self.malha = cliente_malha
        self.chamadas = 0

    def consultar(self, texto, variaveis=None, operacao=None,
                  cabecalhos=None):
        corpo = {"consulta": texto}
        if variaveis:
            corpo["variaveis"] = variaveis
        if operacao:
            corpo["operacao"] = operacao
        self.chamadas += 1

        cabs = dict(self.cabecalhos)
        cabs.update(cabecalhos or {})

        resposta = self._enviar(corpo, cabs)
        if resposta.get("status", 0) == 0:
            # O caso honesto: NÃO SE SABE se chegou. Colapsá-lo em
            # "falhou" faria quem chama repetir uma mudança.
            return {"dados": None,
                    "erros": [{"mensagem": resposta.get("erro")
                               or "não deu para saber se a consulta chegou",
                               "caminho": [], "codigo": "rede"}],
                    "extensoes": {"status": 0}}
        conteudo = resposta.get("corpo")
        if isinstance(conteudo, (str, bytes)):
            try:
                conteudo = json.loads(conteudo)
            except (ValueError, TypeError):
                conteudo = None
        if not isinstance(conteudo, dict):
            return {"dados": None,
                    "erros": [{"mensagem": f"o servidor respondeu "
                                           f"{resposta.get('status')} e o "
                                           f"corpo não é uma resposta Lavra",
                               "caminho": [], "codigo": "rede"}],
                    "extensoes": {"status": resposta.get("status")}}
        return conteudo

    def _enviar(self, corpo, cabecalhos):
        M = _malha()
        if self.malha is None:
            self.malha = M._cliente("lavra", base=self.url)
        return M._post(self.malha, "", corpo=corpo, cabecalhos=cabecalhos,
                       tempo_limite=self.tempo_limite)

    # ── Açúcar ─────────────────────────────────────────────

    def dados(self, texto, variaveis=None, operacao=None):
        """Só os dados. Levanta se houve erro — para quem quer o caminho feliz."""
        resposta = self.consultar(texto, variaveis, operacao)
        if resposta.get("erros"):
            from .execucao import ErroDeExecucao
            primeiro = resposta["erros"][0]
            raise ErroDeExecucao(primeiro.get("mensagem", "erro"),
                                 primeiro.get("caminho"),
                                 primeiro.get("codigo", "erro"),
                                 {"todos": resposta["erros"]})
        return resposta.get("dados")


def cliente(url, cabecalhos=None, tempo_limite=10.0):
    return Cliente(url, cabecalhos, tempo_limite=tempo_limite)


# ══════════════════════════════════════════════════════════════
#  Local: consultar sem rede
# ══════════════════════════════════════════════════════════════

class Local:
    """O mesmo contrato do Cliente, sem socket. É o que torna teste barato."""

    def __init__(self, esquema, contexto=None):
        self.esquema = esquema
        self.contexto = contexto
        self.chamadas = 0

    def consultar(self, texto, variaveis=None, operacao=None,
                  cabecalhos=None):
        from .api import executar
        self.chamadas += 1
        return executar(self.esquema, texto, variaveis, self.contexto,
                        operacao=operacao)

    def dados(self, texto, variaveis=None, operacao=None):
        resposta = self.consultar(texto, variaveis, operacao)
        if resposta.get("erros"):
            from .execucao import ErroDeExecucao
            primeiro = resposta["erros"][0]
            raise ErroDeExecucao(primeiro.get("mensagem", "erro"),
                                 primeiro.get("caminho"),
                                 primeiro.get("codigo", "erro"),
                                 {"todos": resposta["erros"]})
        return resposta.get("dados")


def local(esquema, contexto=None):
    return Local(esquema, contexto)
