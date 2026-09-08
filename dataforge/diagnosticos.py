"""
Catalogo de codigos de erro do DataForge.

Todo erro carrega um codigo estavel (DF0601). Este modulo diz o que cada
um significa, e e o que 'dataforge explain DF0601' imprime.

A separacao importa: a mensagem do erro cabe em uma linha e aponta o
lugar; a explicacao aqui tem espaco para o porque e para o exemplo.

O conteudo nao mora aqui — ele vem de 'catalogo_erros.py', que e a mesma
fonte de onde saem as classes de excecao em 'errors.py'. Antes eram duas
listas escritas a mao, e elas divergiam: um erro ganhava classe e ficava
sem explicacao, ou a explicacao vinha sob o codigo de outro.
"""

from .catalogo_erros import ERROS, POR_CODIGO, POR_CLASSE, familia

#: Formato historico: {codigo: {titulo, doc, explicacao, exemplo, solucao}}.
#: Mantido porque a CLI, o site e os testes leem daqui.
CATALOGO = {
    e["codigo"]: {
        "titulo": e["titulo"],
        "doc": e["doc"],
        "explicacao": "\n" + e["explicacao"] + "\n",
        "exemplo": "\n" + e["exemplo"] + "\n" if e["exemplo"] else "",
        "solucao": "\n" + e["solucao"] + "\n" if e["solucao"] else "",
        "classe": e["classe"],
        "pai": e["pai"],
        "familia": familia(e["codigo"]),
    }
    for e in ERROS
}


def buscar(codigo):
    """Aceita 'DF0601', 'df0601' ou '0601'. Devolve (codigo, dados) ou None.

    Tambem aceita o nome da classe ('KeyError', 'KeyError_'), porque e o
    que aparece na mensagem do erro — pedir ao usuario que traduza nome
    em codigo antes de poder consultar seria trabalho a toa.
    """
    if not codigo:
        return None

    bruto = str(codigo).strip()

    # Pelo nome da classe, com ou sem o sublinhado final.
    for nome in (bruto, bruto + "_", bruto.rstrip("_")):
        entrada = POR_CLASSE.get(nome)
        if entrada:
            return (entrada["codigo"], CATALOGO[entrada["codigo"]])

    chave = bruto.upper()
    if not chave.startswith("DF"):
        chave = "DF" + chave.zfill(4)
    dados = CATALOGO.get(chave)
    return (chave, dados) if dados else None


def por_familia():
    """Os codigos agrupados por familia, na ordem em que foram declarados."""
    grupos = {}
    for e in ERROS:
        grupos.setdefault(familia(e["codigo"]), []).append(e)
    return grupos


def procurar(termo):
    """Codigos cujo titulo, classe ou explicacao mencionam o termo."""
    alvo = termo.strip().lower()
    if not alvo:
        return []
    achados = []
    for e in ERROS:
        campos = (e["codigo"], e["classe"], e["titulo"], e["explicacao"])
        if any(alvo in c.lower() for c in campos):
            achados.append(e)
    return achados
