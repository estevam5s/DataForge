# -*- coding: utf-8 -*-
"""Arcane.Gramatica — a gramática da linguagem, de dentro de um programa.

Os dados moram em `dataforge/gramatica.py`, e cada produção é conferida
contra o parser por `tests/test_gramatica.py`. Este módulo só os expõe:
um editor, um formatador ou um gerador de documentação escrito em
DataForge pergunta **à linguagem** como ela é, em vez de manter uma
cópia que envelhece.

`validar` e `instrucoes` usam o lexer e o parser de verdade, e **não
executam** nada: é seguro chamá-los sobre o texto que um usuário digitou.
"""

from .. import gramatica as _g


def _producao(nome):
    p = _g.producao(str(nome))
    if p is None:
        from ..errors import RuntimeError_
        import difflib
        perto = difflib.get_close_matches(str(nome), [x["nome"] for x in _g.PRODUCOES], 1)
        raise RuntimeError_(
            f"nao ha producao '{nome}'"
            + (f". Voce quis dizer '{perto[0]}'?" if perto else "."), 0, 0,
            dica="Gramatica.producoes() lista todas.")
    return dict(p)


class ArcaneGramatica:
    """Arcane.Gramatica — produções, precedência, tokens e validação."""

    def __new__(cls):
        return {
            "producoes": lambda grupo="": [dict(p) for p in
                                           (_g.do_grupo(grupo) if grupo else _g.PRODUCOES)],
            "producao": _producao,
            "grupos": lambda: [{"id": i, "nome": n, "resumo": r} for i, n, r in _g.GRUPOS],
            "ebnf": lambda grupo="": _g.ebnf(grupo),
            "precedencia": lambda: [dict(n) for n in _g.PRECEDENCIA],
            # Um cluster, e nao a tupla do Python: `G.raiz(e) is ["BinaryOp", "+"]`
            # tem de ser verdadeiro, e uma tupla nunca e igual a uma lista.
            "raiz": lambda expressao: list(_g.raiz_da_expressao(expressao)),
            "tokens": _g.tokens,
            "instrucoes": _g.instrucoes,
            "validar": _g.validar,
            "palavras": _g.palavras,
        }
