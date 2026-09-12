# -*- coding: utf-8 -*-
"""Um vault de opções que não engole erro de digitação.

O problema, com o sintoma exato:

    doc := API.openapi(app, {"title": "Loja", "version": "2.0"})

As chaves são `titulo` e `versao`. As minhas foram **ignoradas em
silêncio**, e o documento saiu com o título padrão — "API DataForge".
Quem escreve isso publica um contrato com o nome errado e não tem como
descobrir: não há erro, não há aviso, e o campo existe no resultado.

O mesmo vale para um simples erro de digitação:

    Malha.cliente(base, {"tentativa": 9})   # 'tentativas'

O cliente fica com **3** tentativas, que é o padrão, e o 9 nunca chega
a lugar nenhum.

─── Por que não aceitar as duas grafias e calar ───────────

Aceitar `title` **e** `titulo` resolveria estes dois casos e nenhum
outro: `tituloo`, `titel`, `tittle` continuam engolidos. O que conserta
a classe inteira é **recusar o que não se conhece**, e é isso que este
módulo faz — com a sugestão do nome parecido, que transforma a recusa
em correção.

─── E por que recusar, e não avisar ───────────────────────

Um aviso impresso não para nada, e o programa segue com o valor padrão
— exatamente o estado que se queria evitar. Uma opção desconhecida é
quase sempre um erro de quem escreveu, e o custo de errar para o lado
da recusa é uma linha a corrigir. O custo do silêncio é um contrato
publicado com o nome errado.
"""

import difflib


class OpcaoDesconhecida(ValueError):
    """Uma chave que a função não conhece.

    `ValueError` porque o interpretador traduz o que a stdlib levanta:
    isto chega ao programa DataForge como um erro com tipo, capturável
    por `handle`.
    """


def ler(opcoes, conhecidas, onde=""):
    """Devolve o vault, recusando chave que `conhecidas` não tem.

    `conhecidas` é um vault `{nome: padrao}` — o mesmo que documenta a
    função. Os padrões não são aplicados aqui: quem chama já tem o seu
    `get(nome, padrao)`, e aplicar duas vezes criaria dois lugares para
    o padrão divergir.

        opcoes = ler(opcoes, {"prazo": 5.0, "tentativas": 3}, "cliente")

    Uma chave que começa com `_` passa: é como se marca "isto é meu, e
    a função não precisa conhecer".
    """
    if not opcoes:
        return {}
    if not isinstance(opcoes, dict):
        raise OpcaoDesconhecida(
            f"{onde or 'esta funcao'} espera um vault de opcoes, "
            f"e recebeu {type(opcoes).__name__}.")

    estranhas = [k for k in opcoes
                 if not str(k).startswith("_") and k not in conhecidas]
    if estranhas:
        raise OpcaoDesconhecida(_mensagem(estranhas, conhecidas, onde))
    return dict(opcoes)


def _mensagem(estranhas, conhecidas, onde):
    nomes = sorted(str(k) for k in conhecidas)
    partes = []
    for chave in estranhas:
        perto = difflib.get_close_matches(str(chave), nomes, n=2, cutoff=0.6)
        if perto:
            alvos = " or ".join(f"'{p}'" for p in perto)
            partes.append(f"'{chave}' (did you mean {alvos}?)")
        else:
            partes.append(f"'{chave}'")

    onde_txt = f"{onde}: " if onde else ""
    plural = "s" if len(estranhas) > 1 else ""
    # A lista completa no fim: sem ela, quem errou um nome que não se
    # parece com nenhum continua sem saber o que existe.
    return (f"{onde_txt}unknown option{plural}: {', '.join(partes)}.\n"
            f"    it accepts: {', '.join(nomes)}")
