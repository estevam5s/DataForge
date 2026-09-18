# -*- coding: utf-8 -*-
"""Arcane.Resultado — a falha como VALOR, e a ausência com nome.

O que faltava
-------------
A linguagem tem `monitor`/`handle` para o erro que interrompe, e `void`
com `??` para a ausência. Faltava a terceira forma, que é a que uma
fronteira pede: **devolver** a falha em vez de levantá-la.

    action buscar(id):
        given id smaller 0:
            yield R.falha("id negativo")
        yield R.ok({"id": id})

    r := buscar(-1)
    given r.falhou():
        out r.erro()

Quem chama decide o que fazer, e o compilador de quem lê o código vê no
tipo de retorno que existe um caminho de falha. Levantar é para o que
**não era esperado**; devolver é para o que era.

Três decisões
-------------
1. **`Resultado` não levanta ao ser lido.** `r.valor()` de uma falha
   levanta — porque ali quem escreveu afirmou que deu certo —, mas
   `r.ou(padrao)`, `r.mapear(…)` e `r.entao(…)` atravessam a falha sem
   erro. Uma peça que levanta em toda leitura seria `trigger` com mais
   passos.

2. **`Talvez` existe apesar de `void`.** `void` é a ausência, e `??`
   resolve 90% dos casos — mas não distingue "a chave não está lá" de
   "a chave vale void", que é exatamente a dúvida num vault de
   configuração. `Talvez.nada()` e `Talvez.algo(void)` são diferentes.

3. **`tentar` captura só o erro da LINGUAGEM.** Um `KeyboardInterrupt`
   ou um sinal de controle (`halt`, `yield`) atravessa: transformar
   sinal de controle em valor de falha faria um `halt` dentro de um
   `tentar` virar uma falha silenciosa em vez de sair do laço.
"""

from ..errors import DataForgeError, RuntimeError_

#: O que `tentar` NÃO captura: sinal de controle da linguagem.
#: Eles derivam de BaseException de propósito — ver errors.py.


def _texto_do_erro(erro):
    return getattr(erro, "message", None) or str(erro) or type(erro).__name__


class Resultado:
    """`ok(valor)` ou `falha(erro)` — e nada mais.

    Ele é um valor: passa por parâmetro, entra num cluster, atravessa
    processo e serializa. O que ele não faz é decidir por quem chama.
    """

    __slots__ = ("_ok", "_valor", "_erro", "_detalhe")

    def __init__(self, ok, valor=None, erro=None, detalhe=None):
        self._ok = bool(ok)
        self._valor = valor
        self._erro = erro
        self._detalhe = detalhe

    # ── perguntar ──
    def deu_certo(self):
        return self._ok

    def falhou(self):
        return not self._ok

    def valor(self):
        """O valor — e levanta se falhou, porque ler assim é afirmar."""
        if not self._ok:
            raise RuntimeError_(
                f"reading the value of a failed Resultado: {self._erro}",
                0, 0, nota="use 'ou(padrao)', 'mapear' or ask 'falhou()' first",
                dica="r.ou(padrao) never raises",
                doc="tipos/resultado")
        return self._valor

    def erro(self):
        """O motivo da falha, ou `void` quando deu certo."""
        return self._erro

    def detalhe(self):
        return self._detalhe

    def ou(self, padrao=None):
        """O valor, ou o padrão. Nunca levanta."""
        return self._valor if self._ok else padrao

    def exigir(self, mensagem=None):
        """O valor, ou levanta com a mensagem de quem chamou."""
        if self._ok:
            return self._valor
        raise RuntimeError_(
            str(mensagem) if mensagem else f"Resultado failed: {self._erro}",
            0, 0, nota=str(self._erro), doc="tipos/resultado")

    # ── transformar ──
    def mapear(self, acao):
        """Muda o valor quando deu certo; a falha passa intacta."""
        if not self._ok:
            return self
        return Resultado(True, acao(self._valor))

    def entao(self, acao):
        """Encadeia outra operação que também devolve `Resultado`."""
        if not self._ok:
            return self
        seguinte = acao(self._valor)
        if not isinstance(seguinte, Resultado):
            return Resultado(True, seguinte)
        return seguinte

    def recuperar(self, acao):
        """Dá outra chance à falha: `acao(erro)` vira o novo resultado."""
        if self._ok:
            return self
        saida = acao(self._erro)
        return saida if isinstance(saida, Resultado) else Resultado(True, saida)

    def para_vault(self):
        return {"ok": self._ok, "valor": self._valor, "erro": self._erro,
                "detalhe": self._detalhe}

    # ── protocolo ──
    def __bool__(self):
        return self._ok

    def __eq__(self, outro):
        if not isinstance(outro, Resultado):
            return NotImplemented
        return (self._ok, self._valor, self._erro) == \
               (outro._ok, outro._valor, outro._erro)

    def __hash__(self):
        return hash((self._ok, str(self._valor), str(self._erro)))

    def __repr__(self):
        if self._ok:
            return f"ok({self._valor!r})"
        return f"falha({self._erro!r})"

    def __str__(self):
        return repr(self)


class Talvez:
    """`algo(valor)` ou `nada()` — a ausência com nome.

    Serve onde `void` é ambíguo: um vault que guarda `void` num valor
    legítimo, um cache que precisa distinguir "não tenho" de "tenho e é
    void", e uma busca que pode não achar.
    """

    __slots__ = ("_tem", "_valor")

    def __init__(self, tem, valor=None):
        self._tem = bool(tem)
        self._valor = valor

    def tem(self):
        return self._tem

    def vazio(self):
        return not self._tem

    def valor(self):
        if not self._tem:
            raise RuntimeError_(
                "reading the value of an empty Talvez", 0, 0,
                dica="use 'ou(padrao)' or ask 'tem()' first",
                doc="tipos/resultado")
        return self._valor

    def ou(self, padrao=None):
        return self._valor if self._tem else padrao

    def mapear(self, acao):
        return Talvez(True, acao(self._valor)) if self._tem else self

    def filtrar(self, acao):
        """Mantém o valor só se a condição passar."""
        if not self._tem:
            return self
        return self if acao(self._valor) else Talvez(False)

    def para_resultado(self, motivo="nada"):
        return Resultado(True, self._valor) if self._tem \
            else Resultado(False, erro=motivo)

    def __bool__(self):
        return self._tem

    def __eq__(self, outro):
        if not isinstance(outro, Talvez):
            return NotImplemented
        return (self._tem, self._valor) == (outro._tem, outro._valor)

    def __hash__(self):
        return hash((self._tem, str(self._valor)))

    def __repr__(self):
        return f"algo({self._valor!r})" if self._tem else "nada()"

    def __str__(self):
        return repr(self)


# ═════════════════════════════════════════════════════════════
#  As portas de entrada
# ═════════════════════════════════════════════════════════════

def ok(valor=None):
    return Resultado(True, valor)


def falha(erro="falhou", detalhe=None):
    return Resultado(False, erro=erro, detalhe=detalhe)


def tentar(acao, *args):
    """Roda a ação e devolve `ok` ou `falha` com a mensagem do erro.

    Captura só `DataForgeError`: um sinal de controle da linguagem
    (`halt`, `skip`, `yield`) atravessa, senão um `halt` dentro de um
    `tentar` viraria falha em vez de sair do laço.
    """
    try:
        return Resultado(True, acao(*args))
    except DataForgeError as erro:
        return Resultado(False, erro=_texto_do_erro(erro),
                         detalhe=getattr(erro, "error_type", "") or
                         type(erro).__name__)


def de(valor, motivo="void"):
    """`void` vira falha; qualquer outro valor vira `ok`."""
    return Resultado(False, erro=motivo) if valor is None \
        else Resultado(True, valor)


def todos(resultados):
    """Um `Resultado` com TODOS os valores, ou a primeira falha.

    É o que se quer ao validar um formulário inteiro: ou sai a lista
    pronta, ou sai o primeiro motivo — e não uma lista com buracos.
    """
    valores = []
    for item in resultados:
        if not isinstance(item, Resultado):
            valores.append(item)
            continue
        if item.falhou():
            return item
        valores.append(item.valor())
    return Resultado(True, valores)


def erros(resultados):
    """Só os motivos das falhas — para relatar tudo de uma vez."""
    return [r.erro() for r in resultados
            if isinstance(r, Resultado) and r.falhou()]


def algo(valor=None):
    return Talvez(True, valor)


def nada():
    return Talvez(False)


def talvez_de(valor):
    """`void` vira `nada()`; o resto vira `algo(valor)`."""
    return Talvez(False) if valor is None else Talvez(True, valor)


def primeiro(colecao, condicao=None):
    """O primeiro item que serve, como `Talvez` — sem levantar no vazio."""
    for item in colecao:
        if condicao is None or condicao(item):
            return Talvez(True, item)
    return Talvez(False)


def chave(vault, nome):
    """`Talvez` da chave: distingue "não tem" de "tem e vale void"."""
    if hasattr(vault, "__contains__") and nome in vault:
        return Talvez(True, vault[nome])
    return Talvez(False)


class ArcaneResultado:
    """O dicionário que `adopt Arcane.Resultado` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Resultado",

            # ── Resultado ──
            "ok": ok,
            "falha": falha,
            "tentar": tentar,
            "de": de,
            "todos": todos,
            "erros": erros,
            "Resultado": Resultado,

            # ── Talvez ──
            "algo": algo,
            "nada": nada,
            "talvez": talvez_de,
            "primeiro": primeiro,
            "chave": chave,
            "Talvez": Talvez,
        }
