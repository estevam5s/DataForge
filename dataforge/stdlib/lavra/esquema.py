# -*- coding: utf-8 -*-
"""O esquema: tipos, campos, argumentos, contratos, uniões e escalares.

A decisão que define o módulo
-----------------------------
Um tipo do Lavra **nasce de um `record` que já existe**. Não há uma
segunda linguagem de declaração de esquema ao lado da linguagem:

    record Usuario:
        id: Integer
        nome: String
        email: String

    Lavra.tipo(esq, Usuario)

O GraphQL precisa de um SDL próprio porque o servidor pode ser escrito
em qualquer linguagem, e o esquema tem de existir fora dela. Aqui o
servidor é DataForge, e o `record` já diz nome, campo e tipo — repetir
isso num arquivo `.graphql` seria inventar uma segunda fonte de verdade
para divergir da primeira.

O que o record não diz — o que é obrigatório, o que é lista de quê,
qual campo é calculado e por quem — entra com `Lavra.campo`.

A notação de tipo
-----------------
É a do GraphQL, porque ela é boa e universalmente lida:

    String        pode ser void
    String!       nunca é void
    [String]      lista que pode ser void, de itens que podem ser void
    [String!]!    lista que nunca é void, de itens que nunca são void

`!` e `[]` são a **única** coisa que o Lavra pega emprestado da sintaxe
do GraphQL, e de propósito: quem já conhece lê sem aprender nada, e
quem não conhece aprende dois símbolos.
"""

import re

# ── Escalares embutidos ────────────────────────────────────────
#
# O nome é o da linguagem, e não o do GraphQL: aqui o tipo se chama
# 'Integer', não 'Int'. Quem escreve o esquema é quem escreve o
# record, e ele não devia ter de traduzir.
ESCALARES = {
    "Integer": {"aceita": (int,), "descricao": "número inteiro"},
    "Float": {"aceita": (int, float), "descricao": "número com casas"},
    "String": {"aceita": (str,), "descricao": "texto"},
    "Boolean": {"aceita": (bool,), "descricao": "yes ou no"},
    "ID": {"aceita": (int, str), "descricao": "identificador opaco"},
}

_NOME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ErroDeEsquema(Exception):
    """O esquema está errado. Sempre em tempo de montagem, nunca de consulta."""


class Tipo:
    """A forma de um tipo do esquema, em qualquer das cinco espécies."""

    __slots__ = ("nome", "especie", "campos", "descricao", "contratos",
                 "membros", "valores", "resolver_tipo", "serializar",
                 "desserializar", "origem")

    def __init__(self, nome, especie, descricao=""):
        self.nome = nome
        self.especie = especie      # objeto | entrada | escalar | contrato | uniao | enum
        self.campos = {}            # nome -> Campo
        self.descricao = descricao
        self.contratos = []         # nomes de contratos que este objeto cumpre
        self.membros = []           # união: nomes dos tipos que a compõem
        self.valores = {}           # enum: nome -> valor
        self.resolver_tipo = None   # contrato/união: valor -> nome do tipo
        self.serializar = None      # escalar próprio
        self.desserializar = None
        self.origem = None          # o record/blueprint de onde ele veio

    def __repr__(self):
        return f"<tipo {self.especie} '{self.nome}'>"


class Campo:
    """Um campo: o tipo dele, os argumentos que aceita e quem o resolve."""

    __slots__ = ("nome", "tipo", "argumentos", "resolver", "descricao",
                 "obsoleto", "complexidade")

    def __init__(self, nome, tipo, argumentos=None, resolver=None,
                 descricao="", obsoleto="", complexidade=1):
        self.nome = nome
        self.tipo = tipo            # texto: 'String!', '[Pedido!]!'
        self.argumentos = argumentos or {}
        self.resolver = resolver
        self.descricao = descricao
        self.obsoleto = obsoleto
        self.complexidade = complexidade

    def __repr__(self):
        return f"<campo {self.nome}: {self.tipo}>"


class Referencia:
    """Um tipo lido da notação: o nome, se é lista, se admite void.

    Guardado como ÁRVORE, e não como texto, porque a validação e a
    coerção percorrem `[[Pedido!]!]!` de fora para dentro — e fazer
    isso por expressão regular a cada campo de cada item de cada
    consulta é onde um servidor de consulta fica lento.
    """

    __slots__ = ("nome", "lista", "de", "obrigatorio")

    def __init__(self, nome=None, lista=False, de=None, obrigatorio=False):
        self.nome = nome
        self.lista = lista
        self.de = de
        self.obrigatorio = obrigatorio

    @property
    def nome_base(self):
        ref = self
        while ref.lista:
            ref = ref.de
        return ref.nome

    def __str__(self):
        if self.lista:
            texto = f"[{self.de}]"
        else:
            texto = self.nome
        return texto + ("!" if self.obrigatorio else "")

    def __repr__(self):
        return f"<ref {self}>"


def ler_tipo(texto):
    """'[Pedido!]!' -> Referencia(lista, de=Pedido!, obrigatorio)."""
    if isinstance(texto, Referencia):
        return texto
    texto = str(texto).strip()
    if not texto:
        raise ErroDeEsquema("um campo precisa de tipo")

    obrigatorio = texto.endswith("!")
    if obrigatorio:
        texto = texto[:-1].strip()

    if texto.startswith("["):
        if not texto.endswith("]"):
            raise ErroDeEsquema(
                f"tipo de lista sem fechar: '{texto}'. "
                f"Escreva '[Pedido]' ou '[Pedido!]!'")
        return Referencia(lista=True, de=ler_tipo(texto[1:-1]),
                          obrigatorio=obrigatorio)

    if not _NOME.match(texto):
        raise ErroDeEsquema(
            f"'{texto}' não é um nome de tipo. Use letras, dígitos e '_', "
            f"começando por letra — com '!' para obrigatório e '[]' para lista")
    return Referencia(nome=texto, obrigatorio=obrigatorio)


class Esquema:
    """Tudo o que a consulta pode pedir, e quem responde por cada parte."""

    def __init__(self, nome="lavra"):
        self.nome = nome
        self.tipos = {}
        self.busca = Tipo("Busca", "objeto", "O que se pode ler.")
        self.mudanca = Tipo("Mudanca", "objeto", "O que se pode alterar.")
        self.assinatura = Tipo("Assinatura", "objeto", "O que se pode acompanhar.")
        self.diretivas = {}
        self.limites = {"profundidade": 12, "complexidade": 1000, "itens": 1000}
        self._por_valor = []        # (teste, nome do tipo) para contrato/união

        for nome_e, dados in ESCALARES.items():
            t = Tipo(nome_e, "escalar", dados["descricao"])
            self.tipos[nome_e] = t

    # ── Declarar ───────────────────────────────────────────────

    def registrar(self, tipo):
        if tipo.nome in self.tipos and self.tipos[tipo.nome] is not tipo:
            raise ErroDeEsquema(
                f"o tipo '{tipo.nome}' já existe neste esquema. "
                f"Um nome, um tipo — senão a consulta fica ambígua.")
        self.tipos[tipo.nome] = tipo
        return tipo

    def obter(self, nome):
        if nome == "Busca":
            return self.busca
        if nome == "Mudanca":
            return self.mudanca
        if nome == "Assinatura":
            return self.assinatura
        return self.tipos.get(nome)

    # ── Conferir ───────────────────────────────────────────────

    def conferir(self):
        """Todo tipo citado existe, e todo campo tem por onde ser resolvido.

        Roda na MONTAGEM. Um esquema que cita um tipo inexistente falha
        aqui, e não na primeira consulta que por acaso pedir aquele
        campo — que pode ser meses depois, em produção.
        """
        problemas = []
        raizes = [("Busca", self.busca), ("Mudanca", self.mudanca),
                  ("Assinatura", self.assinatura)]

        for nome, tipo in list(self.tipos.items()) + raizes:
            for campo in tipo.campos.values():
                ref = ler_tipo(campo.tipo)
                alvo = ref.nome_base
                if self.obter(alvo) is None:
                    problemas.append(
                        f"{nome}.{campo.nome} é '{campo.tipo}', e o tipo "
                        f"'{alvo}' não existe no esquema")
                for arg, decl in campo.argumentos.items():
                    base = ler_tipo(_tipo_do_argumento(decl)).nome_base
                    if self.obter(base) is None:
                        problemas.append(
                            f"o argumento '{arg}' de {nome}.{campo.nome} é "
                            f"'{base}', que não existe no esquema")
            for contrato in tipo.contratos:
                alvo = self.obter(contrato)
                if alvo is None or alvo.especie != "contrato":
                    problemas.append(
                        f"'{tipo.nome}' cumpre '{contrato}', que não é um "
                        f"contrato deste esquema")
                    continue
                for exigido in alvo.campos:
                    if exigido not in tipo.campos:
                        problemas.append(
                            f"'{tipo.nome}' cumpre '{contrato}' mas não tem "
                            f"o campo '{exigido}'")
            for membro in tipo.membros:
                if self.obter(membro) is None:
                    problemas.append(
                        f"a união '{tipo.nome}' cita '{membro}', que não "
                        f"existe no esquema")

        if not self.busca.campos:
            problemas.append(
                "o esquema não tem nenhuma busca. Declare ao menos uma com "
                "Lavra.busca(esq, nome, tipo, resolve := …)")
        if problemas:
            raise ErroDeEsquema(
                "o esquema não fecha:\n  - " + "\n  - ".join(problemas))
        return self


def _tipo_do_argumento(decl):
    """Um argumento é 'String!' ou {"tipo": "String!", "padrao": …}."""
    if isinstance(decl, dict):
        return decl.get("tipo") or decl.get("type") or "String"
    return decl


def padrao_do_argumento(decl):
    if isinstance(decl, dict):
        for chave in ("padrao", "default", "valor"):
            if chave in decl:
                return decl[chave]
    return _SEM_PADRAO


class _SemPadrao:
    __slots__ = ()

    def __repr__(self):
        return "<sem padrão>"


#: Um argumento sem padrão é diferente de um com padrão `void`: o
#: primeiro é exigido quando o tipo é `!`, o segundo já tem resposta.
_SEM_PADRAO = _SemPadrao()
SEM_PADRAO = _SEM_PADRAO
