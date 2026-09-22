# -*- coding: utf-8 -*-
"""Arcane.Evolucao — como uma API muda sem pegar ninguém de surpresa.

Uma biblioteca que remove uma ação de uma versão para a outra quebra
quem a usa no dia da atualização. O caminho é avisar ANTES: a ação
continua funcionando, e quem a chama recebe um aviso dizendo desde
quando ela está obsoleta, por quê, e o que usar no lugar.

Três decisões, e o que cada uma evita:

1. **O aviso sai uma vez por ação**, e não por chamada. Uma ação obsoleta
   num laço de um milhão de voltas imprimiria um milhão de linhas — e o
   aviso que sai um milhão de vezes é o aviso que se aprende a filtrar.
2. **`DF_OBSOLETOS=erro` transforma o aviso em erro.** É o que se liga no
   CI: o aviso impresso não para nada, e o programa segue usando a API
   que vai sumir. `DF_OBSOLETOS=silencio` cala — para quando não se pode
   mudar o código agora e o aviso só polui.
3. **O aviso vai para a saída de ERRO**, e não para a saída normal: um
   programa cuja saída é lida por outro (um CSV, um JSON) não pode ter
   um aviso no meio dela.

`experimental` é o outro lado: uma API que pode mudar sem aviso de
versão. Marcá-la diz a quem usa que não há promessa ainda.
"""

import os
import sys
import threading

_VISTOS = set()
_AVISOS = []
_TRAVA = threading.Lock()


def _erro(mensagem, nota="", dica="", doc="biblioteca/evolucao"):
    from ..errors import RuntimeError_
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=doc)


def _nome_de(acao):
    return getattr(acao, "name", None) or getattr(acao, "__name__", None) or "acao"


def _modo():
    modo = os.environ.get("DF_OBSOLETOS", "aviso").strip().lower()
    return modo if modo in ("aviso", "erro", "silencio") else "aviso"


def _emitir(tipo, nome, texto):
    modo = _modo()
    registro = {"tipo": tipo, "acao": nome, "mensagem": texto}
    with _TRAVA:
        primeira = (tipo, nome) not in _VISTOS
        _VISTOS.add((tipo, nome))
        if primeira:
            _AVISOS.append(registro)
    if modo == "erro" and tipo == "obsoleta":
        raise _erro(texto, dica="DF_OBSOLETOS=erro transforma o aviso em erro; "
                                "troque a chamada pelo que a mensagem sugere")
    if primeira and modo != "silencio":
        sys.stderr.write(f"aviso: {texto}\n")
        sys.stderr.flush()


def obsoleta(motivo="", desde="", use=""):
    """Decorador: `mark @Ev.obsoleta("motivo", desde := "1.4", use := "nova")`.

    A ação continua funcionando; a primeira chamada avisa.
    """
    def decorar(acao):
        if not callable(acao):
            raise _erro("'obsoleta' decora uma acao")
        nome = _nome_de(acao)
        partes = [f"'{nome}' esta obsoleta"]
        if desde:
            partes.append(f"desde a {desde}")
        texto = " ".join(partes)
        if motivo:
            texto += f": {motivo}"
        if use:
            texto += f". Use '{use}'"
        texto += "."

        def envolvida(*args, **kwargs):
            _emitir("obsoleta", nome, texto)
            return acao(*args, **kwargs)

        envolvida.__name__ = nome
        envolvida.__doc__ = f"(obsoleta) {texto}"
        envolvida.obsoleta = {"motivo": motivo, "desde": desde, "use": use}
        return envolvida
    return decorar


def experimental(motivo=""):
    """Decorador: a API existe, e ainda pode mudar sem aviso de versão."""
    def decorar(acao):
        if not callable(acao):
            raise _erro("'experimental' decora uma acao")
        nome = _nome_de(acao)
        texto = f"'{nome}' e experimental e pode mudar sem aviso de versao"
        if motivo:
            texto += f": {motivo}"
        texto += "."

        def envolvida(*args, **kwargs):
            _emitir("experimental", nome, texto)
            return acao(*args, **kwargs)

        envolvida.__name__ = nome
        envolvida.experimental = {"motivo": motivo}
        return envolvida
    return decorar


def renomeada(acao, nome_antigo, desde=""):
    """A mesma ação com o nome antigo, avisando que ele mudou.

    Para quando `relay nova as antiga` não basta: quando se quer que o
    nome velho continue funcionando **e** avise.
    """
    nova = _nome_de(acao)
    texto = f"'{nome_antigo}' foi renomeada para '{nova}'"
    if desde:
        texto += f" na {desde}"
    texto += f". Use '{nova}'."

    def envolvida(*args, **kwargs):
        _emitir("obsoleta", nome_antigo, texto)
        return acao(*args, **kwargs)

    envolvida.__name__ = nome_antigo
    return envolvida


def avisos():
    """Os avisos já emitidos nesta execução — para um teste conferir."""
    with _TRAVA:
        return [dict(a) for a in _AVISOS]


def esquecer():
    """Zera o registro: o próximo uso avisa de novo. Para testes."""
    with _TRAVA:
        _VISTOS.clear()
        _AVISOS.clear()


class ArcaneEvolucao:
    """Arcane.Evolucao — obsoleta, experimental e renomeada."""

    def __new__(cls):
        return {
            "obsoleta": obsoleta,
            "experimental": experimental,
            "renomeada": renomeada,
            "avisos": avisos,
            "esquecer": esquecer,
        }
