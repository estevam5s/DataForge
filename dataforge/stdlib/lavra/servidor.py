# -*- coding: utf-8 -*-
"""Servir o esquema: HTTP para busca e mudança, WebSocket para assinatura.

Sobre o Kiln, e não ao lado dele
--------------------------------
HTTP, rotas, CORS, sessão, cabeçalhos de segurança e WebSocket já
existem no Kiln, testados. Reimplementá-los aqui criaria duas
implementações do mesmo protocolo para divergirem — que é o defeito que
este projeto persegue.

    server api on 8080:
        route GET "/saude":
            respond json {"ok": yes}

    Lavra.montar(api, esq, "/lavra")

Três decisões
-------------
1. **Uma rota, um método.** `POST /lavra` executa; `GET /lavra` devolve
   o esquema em texto. Não há uma rota por busca: a consulta já diz o
   que quer, e uma rota por campo desfaria a razão de o Lavra existir.

2. **Erro de consulta responde 200.** Parece errado e não é: o HTTP
   falou, e a resposta tem `dados` e `erros`. Um 400 obrigaria o
   cliente a ter dois caminhos de leitura para o mesmo corpo, e
   esconderia o caso normal — dados parciais com um erro num campo.
   O 400 fica para o que nem chegou a ser consulta (corpo ilegível), e
   o 500 para o que quebrou fora dela.

3. **A assinatura precisa de socket de verdade.** `Kiln.test` não abre
   WebSocket, então uma assinatura só é exercitada subindo o servidor —
   e é assim que ela é testada aqui.
"""

import json
import threading
import time

from .api import executar, texto_do_esquema
from .execucao import Contexto


def _kiln():
    from ..kiln import ArcaneKiln
    return ArcaneKiln


def _corpo(req):
    corpo = req.get("body")
    if isinstance(corpo, (bytes, bytearray)):
        corpo = corpo.decode("utf-8", "replace")
    if isinstance(corpo, str):
        try:
            corpo = json.loads(corpo)
        except (ValueError, TypeError):
            return None
    return corpo if isinstance(corpo, dict) else None


def montar(app, esquema, caminho="/lavra", contexto_de=None,
           permitir_get=True, introspeccao_publica=True):
    """Põe o esquema no ar dentro de um app Kiln já existente."""
    K = _kiln()

    def atender(req):
        corpo = _corpo(req)
        if corpo is None:
            return K._json({
                "dados": None,
                "erros": [{"mensagem": "o corpo não é um vault com 'consulta'",
                           "caminho": [], "codigo": "pedido",
                           "extra": {"forma": {"consulta": "…",
                                               "variaveis": {},
                                               "operacao": "…"}}}],
            }, 400)

        texto = corpo.get("consulta") or corpo.get("query")
        if not isinstance(texto, str) or not texto.strip():
            return K._json({
                "dados": None,
                "erros": [{"mensagem": "faltou 'consulta'", "caminho": [],
                           "codigo": "pedido"}],
            }, 400)

        ctx = _contexto(contexto_de, req, esquema)
        resposta = executar(esquema, texto,
                            variaveis=corpo.get("variaveis")
                            or corpo.get("variables"),
                            contexto=ctx,
                            operacao=corpo.get("operacao")
                            or corpo.get("operationName"))
        return K._json(resposta)

    K._post(app, caminho, atender)

    if permitir_get:
        def esquema_em_texto(req):
            if not introspeccao_publica:
                return K._text("o esquema não é público", 404)
            return K._header(K._text(texto_do_esquema(esquema)),
                             "Content-Type", "text/plain; charset=utf-8")
        K._get(app, caminho, esquema_em_texto)

    return app


def _contexto(contexto_de, req, esquema=None):
    """O contexto de UM pedido.

    Quando `contexto_de` devolve um Contexto pronto, ele é usado
    INTEIRO. A primeira versão pegava só o `.dados` e montava outro por
    cima — e os LOTES ficavam para trás:

        erro: não há lote chamado 'itens' nesta consulta

    Quem escreve um `contexto_de` que registra os lotes está fazendo a
    coisa certa; descartá-los silenciosamente transformava a montagem
    correta no erro mais confuso do módulo.
    """
    if contexto_de is None:
        return Contexto({"pedido": req}, esquema)
    from .execucao import _chamar
    pronto = _chamar(contexto_de, req)
    if isinstance(pronto, Contexto):
        pronto.dados.setdefault("pedido", req)
        if esquema is not None:
            pronto.esquema = esquema
        return pronto
    dados = dict(pronto or {})
    dados.setdefault("pedido", req)
    return Contexto(dados, esquema)


# ══════════════════════════════════════════════════════════════
#  Assinaturas
# ══════════════════════════════════════════════════════════════

class Fonte:
    """De onde saem os eventos de uma assinatura.

    É uma fila com assinantes, e não um gerador: um gerador serve UM
    consumidor, e uma assinatura tem muitos. Publicar num gerador
    obrigaria a manter um por conexão, o que multiplica o trabalho pelo
    número de pessoas com a aba aberta.
    """

    def __init__(self, nome):
        self.nome = nome
        self._assinantes = []
        self._trava = threading.RLock()

    def assinar(self, entregar):
        with self._trava:
            self._assinantes.append(entregar)
        return lambda: self.cancelar(entregar)

    def cancelar(self, entregar):
        with self._trava:
            if entregar in self._assinantes:
                self._assinantes.remove(entregar)

    def publicar(self, valor):
        with self._trava:
            assinantes = list(self._assinantes)
        mortos = []
        for entregar in assinantes:
            try:
                entregar(valor)
            except Exception:                        # noqa: BLE001
                # Um assinante que morreu não pode derrubar a entrega
                # dos outros — é a mesma regra da Sala do Kiln.
                mortos.append(entregar)
        for entregar in mortos:
            self.cancelar(entregar)
        return len(assinantes) - len(mortos)

    @property
    def quantos(self):
        with self._trava:
            return len(self._assinantes)


def fonte(nome="fonte"):
    return Fonte(nome)


def montar_assinaturas(app, esquema, caminho="/lavra/assinar",
                       contexto_de=None):
    """A assinatura por WebSocket.

    O protocolo é mínimo e de propósito: uma mensagem `{"consulta": …}`
    começa a assinatura, e o servidor manda uma mensagem por evento, no
    mesmo formato de `Lavra.executar`. Sem `connection_init`, sem `ack`,
    sem `complete` — o handshake do WebSocket já disse que a conexão
    está de pé, e repetir isso numa camada acima só dá mais um lugar
    para travar.
    """
    K = _kiln()

    def atender(soquete, req=None):
        cancelar = []
        try:
            while True:
                mensagem = soquete.receber()
                if mensagem is None:
                    break
                try:
                    pedido = json.loads(mensagem)
                except (ValueError, TypeError):
                    soquete.enviar(json.dumps({
                        "erros": [{"mensagem": "mensagem não é JSON",
                                   "codigo": "pedido", "caminho": []}]}))
                    continue
                if pedido.get("parar"):
                    break
                texto = pedido.get("consulta") or pedido.get("query")
                if not texto:
                    soquete.enviar(json.dumps({
                        "erros": [{"mensagem": "faltou 'consulta'",
                                   "codigo": "pedido", "caminho": []}]}))
                    continue
                cancelar.append(_assinar(esquema, texto, pedido, soquete,
                                         contexto_de, req))
        finally:
            for parar in cancelar:
                try:
                    parar()
                except Exception:                    # noqa: BLE001
                    pass

    K._ws(app, caminho, atender)
    return app


def _assinar(esquema, texto, pedido, soquete, contexto_de, req):
    """Roda a assinatura uma vez para descobrir a Fonte, e liga o cano."""
    ctx = _contexto(contexto_de, req or {}, esquema)
    primeira = executar(esquema, texto,
                        variaveis=pedido.get("variaveis"),
                        contexto=ctx,
                        operacao=pedido.get("operacao"))
    if primeira.get("erros"):
        soquete.enviar(json.dumps(primeira, default=str))
        return lambda: None

    achada = _achar_fonte(primeira.get("dados"))
    if achada is None:
        soquete.enviar(json.dumps(primeira, default=str))
        return lambda: None

    def entregar(valor):
        resposta = executar(esquema, texto,
                            variaveis=pedido.get("variaveis"),
                            contexto=Contexto(ctx.dados, esquema),
                            raiz={"__evento": valor},
                            operacao=pedido.get("operacao"))
        soquete.enviar(json.dumps(resposta, default=str))

    return achada.assinar(entregar)


def _achar_fonte(valor):
    if isinstance(valor, Fonte):
        return valor
    if isinstance(valor, dict):
        for item in valor.values():
            achada = _achar_fonte(item)
            if achada is not None:
                return achada
    if isinstance(valor, list):
        for item in valor:
            achada = _achar_fonte(item)
            if achada is not None:
                return achada
    return None


def servir(esquema, porta=8080, host="127.0.0.1", caminho="/lavra",
           contexto_de=None, silencioso=False):
    """Sobe um servidor só para o esquema. Devolve o app."""
    K = _kiln()
    app = K._forge("lavra")
    montar(app, esquema, caminho, contexto_de)
    montar_assinaturas(app, esquema, caminho + "/assinar", contexto_de)
    if not silencioso:
        print(f"  Lavra no ar em http://{host}:{porta}{caminho}")
    K._listen(app, porta, host, silencioso=True)
    return app


def em_segundo_plano(esquema, porta=0, host="127.0.0.1", caminho="/lavra",
                     contexto_de=None):
    """Sobe em outra thread e devolve `(app, porta)`. Para teste."""
    K = _kiln()
    app = K._forge("lavra")
    montar(app, esquema, caminho, contexto_de)
    montar_assinaturas(app, esquema, caminho + "/assinar", contexto_de)
    porta_real = K._serve(app, porta, host)
    return app, porta_real


def parar(app):
    _kiln()._stop(app)
