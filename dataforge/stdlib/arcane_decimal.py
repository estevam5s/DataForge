"""Arcane.Decimal — número exato, para quando 0,1 + 0,2 precisa dar 0,3.

O problema
----------
`Float` é IEEE 754 de 64 bits, e ele não representa 0,1. Representa o
binário mais próximo, e a diferença aparece na soma:

    out 0.1 + 0.2        # 0.30000000000000004

Isso não é defeito do DataForge: é assim em toda linguagem com ponto
flutuante binário, e é o certo para física, estatística e gráficos, onde
a precisão relativa importa mais que o dígito decimal exato.

É errado para dinheiro, para imposto e para qualquer número que uma
pessoa vai conferir na mão. Um centavo que some numa linha some de novo
num milhão de linhas.

A resposta
----------
`Decimal` guarda o número em base **dez**, do jeito que foi escrito:

    adopt Arcane.Decimal as Dec

    a := Dec.de("0.1")
    b := Dec.de("0.2")
    out a + b            # 0.3

A aritmética é a da própria linguagem — `+`, `-`, `*`, `/`, `<`, `is`
funcionam — porque o interpretador trata valor por protocolo, e não por
tipo.

Duas escolhas que valem explicar
--------------------------------
**`Dec.de(0.1)` devolve `0.1`, e não `0.1000000000000000055…`.** A
conversão passa pelo texto do número, que é o que a pessoa escreveu e o
que ela quer dizer. Converter o binário cru seria tecnicamente mais
"fiel" e praticamente inútil: ninguém digita 0.1 querendo o binário mais
próximo dele.

**Arredondar é meio-para-cima por padrão.** O `round` do Python — e o
embutido desta linguagem — fazem arredondamento bancário: 0,5 vira 0 e
2,5 vira 2. É o certo para estatística, porque não enviesa uma série
longa. Para dinheiro é errado: 2,5 centavos precisam virar 3, sempre, ou
o cliente reclama do extrato. É a mesma decisão que o pacote `moeda` já
tinha tomado.

Misturar com `Float` é recusado
-------------------------------
`Dec.de("1.5") + 0.5` levanta erro, e de propósito: somar um número
exato com um aproximado devolve um aproximado, e a garantia que se veio
buscar desapareceria em silêncio. Converta o lado que falta.
"""

import decimal

#: Os modos de arredondamento, com os nomes da linguagem.
#:
#: 'MEIO_PARA_CIMA' vem primeiro porque é o padrão daqui, e o motivo
#: está no cabeçalho: contabilidade não usa arredondamento bancário.
_MODOS = {
    "MEIO_PARA_CIMA": decimal.ROUND_HALF_UP,
    "MEIO_PARA_BAIXO": decimal.ROUND_HALF_DOWN,
    "MEIO_PAR": decimal.ROUND_HALF_EVEN,
    "CIMA": decimal.ROUND_CEILING,
    "BAIXO": decimal.ROUND_FLOOR,
    "TRUNCA": decimal.ROUND_DOWN,
    "LONGE_DO_ZERO": decimal.ROUND_UP,
}


def _erro(mensagem, dica=""):
    from ..errors import TypeError_
    return TypeError_(mensagem, 0, 0, dica=dica, doc="tecnicas/decimal")


class ArcaneDecimal:
    """Número decimal exato."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Decimal",

            # ── Criar ──
            "de": cls._de,
            "zero": lambda: decimal.Decimal(0),
            "de_centavos": cls._de_centavos,

            # ── Converter de volta ──
            "texto": cls._texto,
            "float": cls._para_float,
            "inteiro": cls._para_inteiro,
            "centavos": cls._centavos,

            # ── Operar ──
            "arredondar": cls._arredondar,
            "soma": cls._soma,
            "media": cls._media,
            "abs": lambda d: abs(cls._exigir(d, "abs")),
            "sinal": lambda d: (0 if cls._exigir(d, "sinal") == 0
                                else (1 if cls._exigir(d, "sinal") > 0 else -1)),
            "repartir": cls._repartir,

            # ── Perguntar ──
            "e_decimal": lambda x: isinstance(x, decimal.Decimal),
            "casas": cls._casas,
            "modos": lambda: sorted(_MODOS),
        }

    # ── Criar ────────────────────────────────────────────────

    @staticmethod
    def _de(valor):
        """Texto, inteiro ou float viram um decimal exato.

        O float passa pelo texto dele: `Dec.de(0.1)` é `0.1`, e não o
        binário mais próximo de 0,1. Ver o cabeçalho do módulo.
        """
        if isinstance(valor, decimal.Decimal):
            return valor
        if isinstance(valor, bool):
            raise _erro("'Decimal.de' nao aceita yes/no.",
                        dica="use 1 e 0, ou \"1\" e \"0\"")
        if isinstance(valor, int):
            return decimal.Decimal(valor)
        if isinstance(valor, float):
            return decimal.Decimal(repr(valor))
        if isinstance(valor, str):
            try:
                return decimal.Decimal(valor.strip().replace(",", "."))
            except decimal.InvalidOperation:
                raise _erro(
                    f"'{valor}' nao e um numero decimal.",
                    dica='Decimal.de("19.99")  — ponto ou virgula, '
                         'sem separador de milhar') from None
        raise _erro(
            f"'Decimal.de' precisa de texto, inteiro ou float.",
            dica='Decimal.de("19.99")')

    @staticmethod
    def _de_centavos(centavos):
        """`1999` vira `19.99` — a ponte com quem guarda dinheiro em inteiro."""
        return decimal.Decimal(int(centavos)) / decimal.Decimal(100)

    # ── Converter de volta ───────────────────────────────────

    @staticmethod
    def _exigir(valor, onde):
        if isinstance(valor, decimal.Decimal):
            return valor
        raise _erro(
            f"'Decimal.{onde}' precisa de um Decimal, e veio "
            f"{type(valor).__name__}.",
            dica='converta antes:  Decimal.de(x)')

    @classmethod
    def _texto(cls, valor, casas=None):
        """O número como texto, opcionalmente com casas fixas.

        Com `casas`, arredonda meio-para-cima antes — é o que a pessoa
        quer ao formatar um preço, e deixar o arredondamento implícito
        em outro modo seria a armadilha de sempre.
        """
        d = cls._exigir(valor, "texto")
        if casas is None:
            return str(d)
        return str(cls._arredondar(d, int(casas)))

    @classmethod
    def _para_float(cls, valor):
        """De volta para `Float` — e a exatidão acaba aqui.

        Existe porque a maior parte da biblioteca fala float. Chamar
        isto é a linha onde a garantia termina, e é bom que ela seja
        visível.
        """
        return float(cls._exigir(valor, "float"))

    @classmethod
    def _para_inteiro(cls, valor):
        return int(cls._exigir(valor, "inteiro"))

    @classmethod
    def _centavos(cls, valor):
        """`19.99` vira `1999`, arredondando meio-para-cima."""
        d = cls._arredondar(cls._exigir(valor, "centavos"), 2)
        return int(d.scaleb(2).to_integral_value(decimal.ROUND_HALF_UP))

    # ── Operar ───────────────────────────────────────────────

    @classmethod
    def _arredondar(cls, valor, casas=0, modo="MEIO_PARA_CIMA"):
        d = cls._exigir(valor, "arredondar")
        regra = _MODOS.get(modo)
        if regra is None:
            raise _erro(
                f"'{modo}' nao e um modo de arredondamento.",
                dica=f"os modos: {', '.join(sorted(_MODOS))}")
        casas = int(casas)
        alvo = decimal.Decimal(1).scaleb(-casas) if casas else decimal.Decimal(1)
        return d.quantize(alvo, rounding=regra)

    @classmethod
    def _soma(cls, valores):
        """A soma exata de um cluster. Aceita texto e número junto."""
        total = decimal.Decimal(0)
        for item in valores:
            total += cls._de(item)
        return total

    @classmethod
    def _media(cls, valores):
        itens = list(valores)
        if not itens:
            raise _erro("'Decimal.media' de um cluster vazio.",
                        dica="confira com  given len(xs) bigger 0:  antes")
        return cls._soma(itens) / decimal.Decimal(len(itens))

    @classmethod
    def _repartir(cls, valor, partes, casas=2):
        """Divide sem perder centavo — a soma das partes é o total.

        `Decimal.repartir(Decimal.de("10.00"), 3)` devolve
        `[3.34, 3.33, 3.33]`, e não três vezes 3,33 com um centavo
        sumindo. Dividir dinheiro em partes iguais quase nunca dá partes
        iguais, e quem paga percebe.
        """
        total = cls._exigir(valor, "repartir")
        n = int(partes)
        if n <= 0:
            raise _erro("'Decimal.repartir' precisa de pelo menos uma parte.")

        casas = int(casas)
        unidade = decimal.Decimal(1).scaleb(-casas)
        base = (total / n).quantize(unidade, rounding=decimal.ROUND_DOWN)
        resultado = [base] * n

        # O que sobrou da divisão, distribuído um centavo por parte,
        # do começo para o fim — é como uma conta é rateada de verdade.
        sobra = total - base * n
        passos = int((sobra / unidade).to_integral_value(decimal.ROUND_HALF_UP))
        for i in range(abs(passos)):
            ajuste = unidade if passos > 0 else -unidade
            resultado[i % n] += ajuste
        return resultado

    @classmethod
    def _casas(cls, valor):
        """Quantas casas decimais o número tem, como foi escrito."""
        d = cls._exigir(valor, "casas")
        expoente = d.as_tuple().exponent
        return -expoente if isinstance(expoente, int) and expoente < 0 else 0
