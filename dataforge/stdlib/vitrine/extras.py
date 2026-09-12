"""Validação de campo, tradução e componentes próprios.

Três coisas que um app de verdade precisa e que não cabiam em nenhum
dos outros arquivos.
"""

import threading

from . import componentes as C
from .nucleo import Contexto, No


# ═══════════════════════════════════════════════════════════
#  Validação
# ═══════════════════════════════════════════════════════════
#
# O erro aparece **sob o campo**, e não num alerta no topo. Um
# formulário de doze campos com um alerta dizendo "há erros" obriga a
# pessoa a caçar qual deles — e é a diferença entre corrigir na hora e
# desistir.

def validar(valor, regra, mensagem=""):
    """Confere um valor e desenha o erro sob o último campo.

    A regra é uma ação que recebe o valor e devolve:

    - `yes`/`no` — e a mensagem é a que você passou;
    - um **texto** — e ele é a mensagem (vazio significa que passou);
    - `void` — passou.

    Devolve `yes` quando o valor está bom.

        email := V.entrada("E-mail")
        given no V.validar(email, Regex.e_email, "E-mail inválido"):
            V.parar()
    """
    problema = _problema(valor, regra, mensagem)
    if problema is None:
        return True
    _marcar_ultimo(problema)
    return False


def campo_validado(rotulo, regra, mensagem="", valor="", tipo="texto",
                   dica="", chave=None):
    """Um campo com a regra junto. Devolve `(valor, esta_bom)`.

        email, bom := V.campo_validado("E-mail", Regex.e_email,
                                       "Digite um e-mail válido.")
        given bom:
            V.sucesso("ok")

    Um campo **vazio e nunca tocado** não é acusado: reclamar antes de
    a pessoa digitar qualquer coisa é ruído, não ajuda.
    """
    atual = C.entrada(rotulo, valor, dica, tipo, chave)
    if not str(atual).strip():
        return [atual, False]
    return [atual, validar(atual, regra, mensagem)]


def _problema(valor, regra, mensagem):
    """A mensagem de erro, ou `None` quando o valor passou."""
    try:
        resposta = regra(valor) if callable(regra) else regra
    except Exception as erro:                      # noqa: BLE001
        # Uma regra que dispara é uma regra quebrada, e não um valor
        # ruim. Dizer "E-mail inválido" aqui esconderia o bug real.
        return f"a regra de validação falhou: {erro}"
    if resposta is None or resposta is True:
        return None
    if resposta is False:
        return C._str(mensagem) or "Valor inválido."
    texto = C._str(resposta)
    return texto or None


def _marcar_ultimo(problema):
    """Prende a mensagem ao último campo posto na árvore."""
    ctx = C._ctx()
    for no in reversed(ctx.topo.filhos):
        if "chave" in no.props and "rotulo" in no.props:
            no.props["problema"] = problema
            return
    # Nenhum campo antes — a mensagem vira um alerta, que é melhor do
    # que sumir.
    C.erro(problema)


# ═══════════════════════════════════════════════════════════
#  Tradução
# ═══════════════════════════════════════════════════════════

class Traducao:
    """Chave para texto, por idioma.

    O idioma é **por sessão**, e não por processo: dois visitantes podem
    estar lendo a mesma página em línguas diferentes, e guardar isso num
    lugar só faria um trocar o idioma do outro.

        V.i18n.carregar("pt-BR", {"painel.titulo": "Painel"})
        V.i18n.carregar("en-US", {"painel.titulo": "Dashboard"})
        V.i18n.idioma("en-US")
        V.titulo(V.t("painel.titulo"))
    """

    #: Os cinco do enunciado, mais o que alguém carregar.
    PADRAO = "pt-BR"

    def __init__(self):
        self.dicionarios = {}
        self.reserva = self.PADRAO
        self._trava = threading.RLock()

    def carregar(self, idioma, pares):
        with self._trava:
            self.dicionarios.setdefault(str(idioma), {}).update(
                {str(k): C._str(v) for k, v in (pares or {}).items()})
        return self

    def idiomas(self):
        with self._trava:
            return sorted(self.dicionarios)

    def idioma(self, qual=None):
        """Lê ou troca o idioma **desta sessão**."""
        ctx = Contexto.atual()
        if qual is None:
            if ctx is None:
                return self.reserva
            return ctx.sessao.obter("__idioma__", self.reserva)
        if ctx is not None:
            ctx.sessao.definir("__idioma__", str(qual))
            ctx.config_local["idioma"] = str(qual)
        else:
            self.reserva = str(qual)
        return str(qual)

    def traduzir(self, chave, **valores):
        """O texto da chave. Sem tradução, devolve a **chave**.

        Devolver a chave, e não vazio, é deliberado: um rótulo faltando
        aparece como `painel.titulo` na tela — feio o bastante para
        alguém corrigir, e informativo o bastante para dizer qual é.
        """
        chave = str(chave)
        atual = self.idioma()
        with self._trava:
            texto = (self.dicionarios.get(atual, {}).get(chave)
                     or self.dicionarios.get(self.reserva, {}).get(chave)
                     or chave)
        for nome, valor in (valores or {}).items():
            texto = texto.replace("{" + nome + "}", C._str(valor))
        return texto

    def seletor(self, rotulo="Idioma", nomes=None):
        """Desenha a troca de idioma e devolve o escolhido."""
        disponiveis = self.idiomas() or [self.reserva]
        rotulos = dict(nomes or {})
        visiveis = [rotulos.get(i, i) for i in disponiveis]
        atual = self.idioma()
        indice = disponiveis.index(atual) if atual in disponiveis else 0
        escolhido = C.escolha(rotulo, visiveis, indice, chave="__idioma__")
        for codigo, visivel in zip(disponiveis, visiveis):
            if visivel == escolhido and codigo != atual:
                self.idioma(codigo)
                from .runtime import _Reexecutar
                # Trocar o idioma no meio da página deixaria a metade de
                # cima na língua anterior.
                raise _Reexecutar()
        return atual


# ═══════════════════════════════════════════════════════════
#  Componentes próprios
# ═══════════════════════════════════════════════════════════

def componente(nome, acao=None):
    """Registra um componente reaproveitável, pelo nome.

    Uma ação **já é** um componente na Vitrine — chamá-la desenha o que
    ela desenha, e nada além disso é necessário:

        action cartao_de_usuario(nome, email):
            caixa := V.cartao(nome)
            caixa.texto(email)

        cartao_de_usuario("Ana", "ana@exemplo.br")

    O registro existe para o caso em que o nome precisa atravessar
    módulos — um plugin que acrescenta componentes, ou um tema que
    substitui um deles sem que quem chama saiba.

        V.componente("cartao_de_usuario", cartao_de_usuario)
        V.usar("cartao_de_usuario", "Ana", "ana@exemplo.br")

    Também serve de decorador:

        mark @V.componente("cartao_de_usuario")
        action cartao_de_usuario(nome, email):
            …
    """
    def registrar(alvo):
        _registro()[str(nome)] = alvo
        return alvo

    if acao is None:
        return registrar
    return registrar(acao)


def usar(nome, *args, **kwargs):
    """Chama um componente registrado."""
    registrados = _registro()
    alvo = registrados.get(str(nome))
    if alvo is None:
        from ...errors import RuntimeError_
        import difflib
        perto = difflib.get_close_matches(str(nome), sorted(registrados), n=1)
        raise RuntimeError_(
            f"nenhum componente chamado '{nome}' foi registrado.", 0, 0,
            nota=(f"voce quis dizer '{perto[0]}'?" if perto else
                  ("os registrados: " + ", ".join(sorted(registrados))
                   if registrados else "nenhum foi registrado ainda")),
            dica="V.componente(\"nome\", acao) registra",
            doc="vitrine/componentes")
    return alvo(*args, **kwargs)


def componentes_registrados():
    return sorted(_registro())


def _registro():
    from .api import _app
    return _app().componentes
