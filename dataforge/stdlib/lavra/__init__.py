# -*- coding: utf-8 -*-
"""Lavra — a consulta tipada do DataForge.

O que é
-------
O cliente diz **exatamente** o que precisa, numa consulta, e recebe
exatamente aquilo — nem um campo a mais, nem uma segunda chamada para
buscar o que faltou.

    busca:
        usuario(id: 7):
            nome
            pedidos(limite: 3):
                numero
                total

Uma rota REST devolve o que o servidor decidiu devolver. Quem precisa
de menos carrega o resto; quem precisa de mais faz outra chamada. Numa
tela de celular com rede ruim, as duas coisas custam.

O nome
------
**Lavra** é a extração de um veio de minério — e `lavrar` também é
redigir um documento. As duas coisas que este módulo faz: um esquema é
lavrado, e a consulta lavra dele exatamente o minério que quer. Segue a
metáfora da forja, como Kiln, Crucible e Vitrine.

A decisão que define o módulo
-----------------------------
**O esquema nasce dos `record` que já existem.**

    record Usuario:
        id: Integer
        nome: String

    Lavra.tipo(esq, Usuario)

O GraphQL precisa de uma linguagem de esquema própria porque o servidor
pode estar escrito em qualquer coisa, e o esquema tem de existir fora
dela. Aqui o servidor é DataForge, e o `record` já diz nome, campo e
tipo. Um arquivo `.graphql` ao lado seria uma segunda fonte de verdade
para divergir da primeira — que é exatamente o defeito que este projeto
persegue em todo lugar.

A consulta é indentada
----------------------
Porque a linguagem é. Uma consulta escrita ao lado do código que a usa
tem de parecer com ele; o `:` no fim marca "isto tem seleção dentro",
como em `given`, `cycle` e `action`.

Sobre o que ele é construído
----------------------------
O servidor HTTP e o WebSocket são o **Kiln** — que já existe, está
testado, e reimplementá-lo aqui criaria duas implementações do mesmo
protocolo para divergirem. O Lavra é o que o Kiln não tem: o esquema, a
consulta, a resolução e os limites.
"""

from .api import *                                   # noqa: F401,F403
from . import api as _api
from . import cliente as _cliente
from . import federacao as _federacao
from . import servidor as _servidor
from .consulta import ErroDeConsulta
from .esquema import ErroDeEsquema
from .execucao import ErroDeExecucao, Recusado
from .lote import ErroDeLote


class ArcaneLavra:
    """O dicionário que `adopt Arcane.Lavra` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Lavra",

            # ── Montar o esquema ──
            "esquema": _api.esquema,
            "tipo": _api.tipo,
            "entrada": _api.entrada,
            "escalar": _api.escalar,
            "contrato": _api.contrato,
            "uniao": _api.uniao,
            "enum": _api.enum,
            "campo": _api.campo,
            "busca": _api.busca,
            "mudanca": _api.mudanca,
            "assinatura": _api.assinatura,
            "diretiva": _api.diretiva,
            "limites": _api.limites,
            "conferir": _api.conferir,
            "introspeccao": _api.introspeccao,

            # ── Consultar ──
            "ler": _api.ler,
            "validar": _api.validar,
            "executar": _api.executar,

            # ── Contexto, lote, erros ──
            "contexto": _api.contexto,
            "lote": _api.lote,
            "pedir": _api.pedir,
            "preencher": _api.preencher,
            "lotes": _api.lotes,
            "recusar": _api.recusar,
            "erro": _api.erro,

            # ── Paginação ──
            "pagina": _api.pagina,
            "tipo_pagina": _api.tipo_pagina,

            # ── Descrever ──
            "descrever": _api.descrever,
            "texto_do_esquema": _api.texto_do_esquema,

            # ── Servir (sobre o Kiln) ──
            "montar": _servidor.montar,
            "montar_assinaturas": _servidor.montar_assinaturas,
            "servir": _servidor.servir,
            "em_segundo_plano": _servidor.em_segundo_plano,
            "parar": _servidor.parar,
            "fonte": _servidor.fonte,

            # ── Consultar outro serviço ──
            "cliente": _cliente.cliente,
            "local": _cliente.local,

            # ── Federação ──
            "portao": _federacao.portao,
            "juntar": _federacao.juntar,
            "estender": _federacao.estender,
            "mapa": _federacao.mapa,
        }


__all__ = ["ArcaneLavra", "ErroDeConsulta", "ErroDeEsquema",
           "ErroDeExecucao", "ErroDeLote", "Recusado"]
