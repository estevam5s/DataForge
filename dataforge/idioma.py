"""O idioma das mensagens.

O runtime falava inglês e a CLI falava português. Medido nas strings de
mensagem: `interpreter.py` tinha 234 em inglês contra 55 em português, e
`cli.py` o inverso — 200 contra 15. Quem escreve em pt-BR recebia
`dataforge check` em português e o erro de execução em inglês, na mesma
sessão e sobre o mesmo arquivo.

Esta camada resolve isso **sem reescrever as 530 strings**, que é o que
tornaria a mudança irreversível e impediria qualquer falante de inglês de
usar a linguagem. O texto nasce em inglês onde sempre nasceu, e é
traduzido **na hora de desenhar**.

Três decisões que valem lembrar:

1. **A tradução é no DESENHO, não em `error.message`.** `e.message` é o
   que um programa lê num `handle`, e o que 2600 testes comparam. Traduzir
   ali mudaria o comportamento de programas que já existem e quebraria a
   suíte inteira de uma vez — e a informação que interessa a um programa é
   a identidade do erro, não a redação dela. Não há um `Arcane.Idioma`:
   quem embute o DataForge e quer o texto traduzido chama
   `dataforge.idioma.traduzir` do lado do Python.

2. **O que não tem tradução sai em inglês.** Um catálogo incompleto que
   levantasse, ou que devolvesse a chave crua, seria pior que o inglês:
   ninguém consegue traduzir 530 mensagens numa tacada, e um erro é
   sempre mais útil legível em inglês do que ilegível em português.
   `cobertura()` mede o quanto já está traduzido, e é assim que a lista
   cresce sem que ninguém precise adivinhar onde ela está.

3. **`DF_IDIOMA=en` volta ao original.** O inglês continua alcançável, o
   que mantém a linguagem utilizável fora do Brasil e dá a quem reporta
   um bug a forma que aparece em toda busca na internet.
"""

import os
import re

#: O idioma quando ninguem diz nada. A linguagem e escrita em pt-BR, a
#: documentacao e em pt-BR, e a CLI ja era: o runtime era o unico
#: destoando.
PADRAO = "pt"


def atual():
    """O idioma em vigor — qualquer um que tenha catalogo, ou 'en'.

    Um valor que nao corresponde a idioma nenhum cai no PADRAO, e nao
    num erro: `DF_IDIOMA` costuma vir do ambiente da maquina, e um
    programa que se recusa a rodar porque a variavel de locale tem um
    valor estranho seria pior que um programa que fala portugues.

    Quem quer saber se o valor foi entendido chama `dataforge idioma`,
    que diz o que existe e o que nao carregou.
    """
    escolhido = (os.environ.get("DF_IDIOMA") or PADRAO).strip().lower()
    if not escolhido:
        return PADRAO
    if escolhido.startswith("en"):
        return "en"
    # 'pt-BR', 'pt_BR', 'es-419' — o codigo e o que vem antes do
    # separador. Um locale completo e o que o sistema entrega.
    curto = re.split(r"[-_.]", escolhido)[0]
    from .idiomas import registro
    disponiveis = registro()
    if escolhido in disponiveis:
        return escolhido
    if curto in disponiveis:
        return curto
    # 'english' nao comeca com 'en'? comeca. Mas 'espanol' tambem nao e
    # um codigo: o nome por extenso so vale quando ele E o codigo.
    return PADRAO


# ═══════════════════════════════════════════════════════════
#  O registro de idiomas
# ═══════════════════════════════════════════════════════════
#
# Um catalogo por arquivo, em 'dataforge/idiomas/'. A camada nasceu
# binaria — 'pt' ou 'en' —, e binaria ela nao tinha como receber uma
# traducao de fora: quem quisesse espanhol teria de editar o nucleo.
#
# 'DF_IDIOMA_CAMINHO' aponta uma pasta com catalogos de fora, e eles
# entram no registro como os de dentro. Um catalogo quebrado NAO
# derruba nada: ele e ignorado e aparece em 'dataforge idioma' com o
# motivo. Um erro de sintaxe num arquivo de traducao nao pode impedir
# o programa de rodar — a traducao e conforto, e o ingles e o piso.

def _catalogo_pt():
    """As tabelas do portugues, como elas sempre estiveram aqui.

    Elas moram em 'dataforge/idiomas/pt.py' desde que a camada aceitou N
    idiomas. Os nomes continuam exportados porque o teste que confere os
    moldes os le, e porque quem embute o DataForge pode estar lendo-os.
    """
    from .idiomas import registro
    catalogo = registro().get("pt") or {"inteiras": (), "pedacos": ()}
    return catalogo["inteiras"], catalogo["pedacos"]


INTEIRAS, PEDACOS = _catalogo_pt()


def _compilar(tabela, inteira):
    saida = []
    for cru, molde in tabela:
        saida.append((re.compile(cru if not inteira else f"(?s:{cru})"), molde))
    return tuple(saida)


_COMPILADOS = {}


def _tabelas(codigo):
    """As duas tabelas compiladas daquele idioma. `None` para o original.

    A compilacao e por idioma e acontece UMA vez: 115 expressoes
    regulares recompiladas a cada mensagem de erro custariam mais que a
    mensagem.
    """
    if codigo == "en":
        return None
    if codigo not in _COMPILADOS:
        from .idiomas import registro
        catalogo = registro().get(codigo)
        if catalogo is None:
            return None
        _COMPILADOS[codigo] = (_compilar(catalogo["inteiras"], True),
                               _compilar(catalogo["pedacos"], False))
    return _COMPILADOS[codigo]


def esquecer_catalogos():
    """Solta o que esta compilado — para o teste que planta um catalogo."""
    _COMPILADOS.clear()
    from .idiomas import registro
    registro(recarregar=True)


def traduzir(texto, para=None):
    """O texto no idioma em vigor. Sem tradução, devolve o original."""
    if not texto:
        return texto
    tabelas = _tabelas(para or atual())
    if tabelas is None:
        return texto
    inteiras, pedacos = tabelas
    mudou = texto
    for padrao, molde in inteiras:
        achado = padrao.fullmatch(texto)
        if achado:
            # Os pedacos rodam TAMBEM sobre o resultado: um campo do molde
            # pode carregar um trecho que tem traducao propria — "a caught
            # error (TriggerError)" dentro de "Cannot access member …".
            mudou = molde.format(**achado.groupdict())
            break
    for padrao, molde in pedacos:
        mudou = padrao.sub(
            lambda m: molde.format(**m.groupdict()), mudou)
    return mudou


#: As palavras da MOLDURA do relatorio — as que nao vem de uma mensagem.
#:
#: Elas eram literais em portugues dentro do desenhador, e por isso
#: 'DF_IDIOMA=en' produzia 'erro[DF0602]: Key "b" is not in this vault.'
#: — um rotulo em portugues em cima de uma mensagem em ingles, na
#: primeira linha do relatorio. O catalogo traduzia as 530 mensagens e
#: deixava de fora as quatro palavras que mais aparecem.
#:
#: Elas ficam AQUI, e nao no catalogo de cada idioma, porque nao sao
#: mensagens: sao a forma do relatorio. Um idioma que traduz mensagem e
#: esquece a moldura fica pior que o ingles inteiro.
MOLDURA = {
    "en": {"erro": "error", "aviso": "warning", "nota": "note",
           "dica": "hint", "sugestao": "hint", "doc": "doc"},
    "pt": {"erro": "erro", "aviso": "aviso", "nota": "nota",
           "dica": "dica", "sugestao": "sugestão", "doc": "doc"},
    "es": {"erro": "error", "aviso": "aviso", "nota": "nota",
           "dica": "pista", "sugestao": "sugerencia", "doc": "doc"},
}


def palavra(chave, para=None):
    """Uma palavra da moldura no idioma em vigor.

    Um idioma sem moldura declarada cai no INGLES, e nao no portugues:
    quem contribui um catalogo novo sem traduzir a moldura produz um
    relatorio coerente em ingles, e nao um meio-portugues.
    """
    codigo = para or atual()
    tabela = MOLDURA.get(codigo) or MOLDURA["en"]
    return tabela.get(chave, MOLDURA["en"].get(chave, chave))


def tem_traducao(texto, para=None):
    """Se o catálogo conhece este texto. É o que `cobertura` conta."""
    if not texto:
        return True
    return traduzir(texto, para=para or PADRAO) != texto


def cobertura(mensagens, para=None):
    """Quantas das mensagens dadas o catálogo traduz.

    Serve ao teste que mede o avanço: uma camada de idioma sem medida
    fica pela metade sem ninguém perceber, porque o que falta continua
    saindo em inglês legível — que é o fallback certo e também o que
    esconde o buraco.
    """
    total = len(mensagens)
    if not total:
        return 1.0
    return sum(1 for m in mensagens if tem_traducao(m, para)) / total
