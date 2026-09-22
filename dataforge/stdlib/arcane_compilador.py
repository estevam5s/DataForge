# -*- coding: utf-8 -*-
"""Arcane.Compilador — o caminho de compilação como dado.

O que faltava
-------------
`Arcane.Macro` entrega a **árvore** de uma ação como vault, e com isso
se escreve macro. O que ele não alcança é o que vem depois da árvore: o
HIR, o grafo de fluxo, as análises e o que o compilador de fechamentos
fez. Sem isso, um plugin do `check` só consegue perguntar coisas de
**forma** — "existe um `point` capturando no topo?" — e nunca de
**fluxo** — "este nome está definido em todo caminho que chega aqui?".

    adopt Arcane.Compilador as K

    K.acucares(fonte)               // quanto acucar o arquivo usa
    K.mir(fonte)[0]["blocos"]       // os blocos basicos do topo
    K.talvez_nao_definidas(fonte)   // a analise de fluxo, de dentro
    K.lir(fonte)["proporcao"]       // quanto compilou para fechamento

Quatro decisões
---------------
1. **Entra texto, e não uma ação.** As fases valem para um **arquivo**:
   o grafo do topo e o de cada ação, o inventário do arquivo inteiro. Um
   `Arcane.Macro.arvore(acao)` responde a outra pergunta, e as duas
   convivem — `arvore(fonte)` aqui devolve o programa todo.

2. **Sai vault e cluster, nunca objeto opaco.** Um bloco é
   `{"id": …, "saidas": [{"para": …, "aresta": …}], …}`, que percorre com
   `cycle`, casa com `match` e serializa. É a mesma escolha do `Macro` e
   do `Quadro`: quem consome não precisa conhecer classe nenhuma.

3. **Erro de sintaxe não vira traceback.** A fonte vem de fora — de um
   arquivo, de um editor, de um plugin — e falhar é o caso comum.
   `analisar` levanta erro **da linguagem**, com linha e coluna, e um
   plugin quebrado vira diagnóstico, não pilha do Python.

4. **Não há fase de código de máquina, e o módulo não finge.**
   `fases()` lista o que existe, e `lir` diz na cara que o backend é o
   compilador de fechamentos. Uma função chamada `assembly` que
   devolvesse texto plausível seria a pior coisa que este módulo poderia
   ter.
"""

from .. import hir as _hir
from .. import lir as _lir
from .. import mir as _mir
from .. import otimizar as _ot
from .. import ssa as _ssa
from ..errors import DataForgeError, RuntimeError_
from ..lexer import tokenize
from ..parser import parse

#: As fases do caminho, na ordem. É o que `dataforge ir --fase=` aceita.
FASES = ("lexer", "parser", "hir", "mir", "analises", "ssa", "otimizado",
         "lir")


def _arvore(fonte, nome="<compilador>"):
    """A árvore de um texto, com o erro de sintaxe já traduzido."""
    if not isinstance(fonte, str):
        raise RuntimeError_(
            "Compilador expects the source as text. Read the file first with "
            "IO.read, or pass the program as a string.",
            doc="compilador/pipeline")
    try:
        return parse(tokenize(fonte, nome), nome)
    except DataForgeError:
        raise
    except Exception as erro:               # pragma: no cover
        raise RuntimeError_(f"could not read the source: {erro}",
                            doc="compilador/pipeline")


def fases():
    """Os nomes das fases, na ordem em que o caminho passa por elas."""
    return list(FASES)


def tokens(fonte):
    """A primeira fase: um vault por token."""
    # O valor como o lexer o leu: 7 e numero, "7" seria outro token. O
    # 'str' antigo punha o texto "None" no fim do arquivo — um nome do
    # Python vazando para quem so conhece 'void'.
    return [{"tipo": t.type.name, "valor": t.value,
             "linha": t.line, "coluna": t.column}
            for t in tokenize(fonte, "<compilador>")]


def arvore(fonte):
    """A árvore crua, como vault — a mesma forma do `Arcane.Macro`."""
    from .arcane_macro import _para_dado
    return _para_dado(_arvore(fonte))


def hir(fonte):
    """A árvore depois do açúcar, como vault."""
    from .arcane_macro import _para_dado
    return _para_dado(_hir.normalizar(_arvore(fonte)))


def acucares(fonte):
    """`{nome do açúcar: quantas vezes}` — o que o arquivo usa."""
    return dict(_hir.acucares_usados(_arvore(fonte)))


def acucares_conhecidos():
    """O que a normalização abre, com o que cada um abre."""
    return dict(_hir.ACUCARES)


def nao_e_acucar():
    """O que parece açúcar e não é, com o motivo de cada um."""
    return dict(_hir.NAO_E_ACUCAR)


def resolucao(fonte):
    """De onde vem cada nome: parâmetro, local, livre ou embutido."""
    return [{"nome": c.nome, "linha": c.linha,
             "parametros": list(c.parametros), "locais": list(c.locais),
             "livres": list(c.livres), "embutidos": list(c.embutidos)}
            for c in _hir.resolucao(_arvore(fonte))]


def _corpos(fonte):
    return _mir.construir(_arvore(fonte))


def mir(fonte):
    """Um vault por corpo, com os blocos e as arestas."""
    return [_corpo_como_dado(c) for c in _corpos(fonte)]


def _corpo_como_dado(corpo):
    vivos = _mir.alcancaveis(corpo)
    return {
        "nome": corpo.nome,
        "linha": corpo.linha,
        "parametros": list(corpo.parametros),
        "entrada": corpo.entrada,
        "blocos": [{
            "id": b.id,
            "rotulo": b.rotulo,
            "linha": b.linha,
            "instrucoes": [i.__class__.__name__ for i in b.instrucoes],
            "saidas": [{"para": d, "aresta": r} for d, r in b.saidas],
            "terminador": b.terminador,
            "liga": list(b.escreve),
            "alcancavel": b.id in vivos,
        } for b in corpo.blocos],
    }


def blocos(fonte, nome=None):
    """Só os blocos — de um corpo, se `nome` vier."""
    corpos = _corpos(fonte)
    if nome is not None:
        corpos = [c for c in corpos if c.nome == nome]
        if not corpos:
            raise RuntimeError_(
                f"there is no body named '{nome}' in this source. "
                f"Use Compilador.corpos(fonte) to see the names.",
                doc="compilador/mir")
    return [b for c in corpos for b in _corpo_como_dado(c)["blocos"]]


def corpos(fonte):
    """Os nomes dos corpos: `(programa)`, cada ação, cada rota."""
    return [c.nome for c in _corpos(fonte)]


def alcance(fonte):
    """`{nome do corpo: {"vivos": n, "total": n, "fora": [ids]}}`."""
    saida = {}
    for corpo in _corpos(fonte):
        vivos = _mir.alcancaveis(corpo)
        saida[corpo.nome] = {
            "vivos": len(vivos), "total": len(corpo.blocos),
            "fora": sorted(b.id for b in corpo.blocos if b.id not in vivos)}
    return saida


def constantes(fonte, nome=None):
    """Os nomes cujo valor todo caminho concorda, no fim do corpo."""
    return _por_corpo(fonte, nome, lambda c: dict(_mir.constantes(c)))


def escapam(fonte, nome=None):
    """Os locais que saem do quadro, e por qual motivo."""
    return _por_corpo(fonte, nome, lambda c: dict(_mir.escapam(c)))


def vivas(fonte, nome=None):
    """Os nomes ainda por ler, na entrada de cada bloco."""
    return _por_corpo(
        fonte, nome,
        lambda c: {str(i): sorted(n) for i, n in _mir.vivas(c).items()})


def talvez_nao_definidas(fonte, nome=None):
    """Os nomes lidos num ponto que algum caminho não definiu.

    É a análise que virou o diagnóstico `talvez-nao-definida` do
    `check`. De dentro da linguagem ela serve a duas coisas: escrever
    um plugin que a aplique com outra política, e ver a resposta sem
    passar pela CLI.
    """
    achados = []
    for corpo in _corpos(fonte):
        if nome is not None and corpo.nome != nome:
            continue
        for duvida, _instrucao in _mir.talvez_nao_definidas(corpo):
            achados.append(duvida)
    return achados


def onde_talvez_nao_definidas(fonte):
    """O mesmo, com o corpo e a linha — o que um plugin precisa."""
    return [{"corpo": corpo.nome, "nome": duvida,
             "linha": getattr(instrucao, "line", 0)}
            for corpo in _corpos(fonte)
            for duvida, instrucao in _mir.talvez_nao_definidas(corpo)]


def _por_corpo(fonte, nome, calcular):
    lista = _corpos(fonte)
    if nome is not None:
        escolhidos = [c for c in lista if c.nome == nome]
        if not escolhidos:
            raise RuntimeError_(
                f"there is no body named '{nome}' in this source. "
                f"Use Compilador.corpos(fonte) to see the names.",
                doc="compilador/mir")
        return calcular(escolhidos[0])
    return {c.nome: calcular(c) for c in lista}


def dominancia(fonte, nome=None):
    """Dominadores, dominador imediato e fronteira — de cada corpo.

    `{dominadores: {id: [ids]}, imediato: {id: id}, fronteira: {id: [ids]}}`.
    As tres saem do MESMO ponto fixo que o SSA usa para decidir onde vao
    os phi; expor outra conta aqui faria esta resposta e a do SSA
    poderem discordar.
    """
    def calcular(corpo):
        _vivos, dom, idom, _antes = _ssa._dominancia(corpo)
        fronteira = _ssa.fronteira_de_dominancia(corpo)
        return {
            "dominadores": {str(i): sorted(v) for i, v in sorted(dom.items())},
            "imediato": {str(i): idom[i] for i in sorted(idom)},
            "fronteira": {str(i): sorted(v) for i, v in sorted(fronteira.items())},
        }
    return _por_corpo(fonte, nome, calcular)


def _aspas_dot(texto):
    # So a aspa e escapada: o '\\l' dos rotulos e sintaxe do DOT
    # (alinha a linha a esquerda), e escapar a barra o desligaria.
    return '"' + str(texto).replace('"', '\\"') + '"'


def dot(fonte, nome=None):
    """O grafo de fluxo em DOT, para o Graphviz desenhar.

        IO.write("fluxo.dot", Compilador.dot(fonte))
        // dot -Tsvg fluxo.dot -o fluxo.svg

    Um `subgraph cluster` por corpo. Bloco inalcancavel sai **tracejado
    e cinza** — o grafo tambem responde "que codigo nunca roda?". A
    aresta leva o rotulo (`sim`, `nao`, `volta`, `erro`), que e o que
    diferencia um `given` de um laco no desenho.
    """
    lista = _corpos(fonte)
    if nome is not None:
        lista = [c for c in lista if c.nome == nome]
        if not lista:
            raise RuntimeError_(
                f"there is no body named '{nome}' in this source. "
                f"Use Compilador.corpos(fonte) to see the names.",
                doc="compilador/mir")
    linhas = ["digraph fluxo {",
              '  node [shape=box, fontname="monospace", fontsize=10];',
              '  edge [fontname="monospace", fontsize=9];']
    for n, corpo in enumerate(lista):
        vivos = _mir.alcancaveis(corpo)
        linhas.append(f"  subgraph cluster_{n} {{")
        linhas.append(f"    label={_aspas_dot(corpo.nome)};")
        for b in corpo.blocos:
            instrucoes = [i.__class__.__name__ for i in b.instrucoes]
            corpo_texto = "\\l".join([f"B{b.id} {b.rotulo}"
                                     + (f" (linha {b.linha})" if b.linha else "")]
                                    + instrucoes) + "\\l"
            estilo = "" if b.id in vivos else ', style=dashed, color=gray, fontcolor=gray'
            linhas.append(f"    c{n}_b{b.id} [label={_aspas_dot(corpo_texto)}{estilo}];")
        for b in corpo.blocos:
            for destino, rotulo in b.saidas:
                marca = f" [label={_aspas_dot(rotulo)}]" if rotulo else ""
                linhas.append(f"    c{n}_b{b.id} -> c{n}_b{destino}{marca};")
        linhas.append("  }")
    linhas.append("}")
    return "\n".join(linhas) + "\n"


def ssa(fonte, nome=None):
    """Um vault por corpo, com os φ e as versões de cada leitura.

    SSA responde a pergunta que o MIR não responde: **qual** atribuição
    esta leitura vê. É ela que torna a propagação de constante
    condicional, e por isso `ramos_mortos` sai daqui.
    """
    saida = []
    for corpo in _corpos(fonte):
        if nome is not None and corpo.nome != nome:
            continue
        forma = _ssa.construir(corpo)
        saida.append({
            "nome": forma.nome,
            "parametros": list(forma.parametros),
            "entrada": forma.entrada,
            "blocos": [{
                "id": b.id,
                "rotulo": b.rotulo,
                "terminador": b.terminador,
                "fis": [{"nome": f.nome, "versao": f.versao,
                         "fontes": {str(k): v
                                    for k, v in sorted(f.fontes.items())}}
                        for f in b.fis],
                "instrucoes": [{
                    "no": i.no.__class__.__name__,
                    "linha": i.linha,
                    "le": dict(sorted(i.le.items())),
                    "escreve": ({"nome": i.escreve[0], "versao": i.escreve[1]}
                                if i.escreve else None),
                } for i in b.instrucoes],
                "saidas": [{"para": d, "aresta": r} for d, r in b.saidas],
            } for b in forma.blocos],
        })
    return saida


def provadas(fonte, nome=None):
    """`{"nome#versao": valor}` — o que a propagação condicional conclui."""
    saida = {}
    for corpo in _corpos(fonte):
        if nome is not None and corpo.nome != nome:
            continue
        fixas, _mortos = _ssa.constantes_condicionais(_ssa.construir(corpo))
        for (chave, versao), valor in fixas.items():
            saida[f"{corpo.nome}:{chave}#{versao}"] = valor
    return saida


def ramos_mortos(fonte):
    """Os blocos que a propagação condicional prova que nunca rodam."""
    achados = []
    for corpo in _corpos(fonte):
        forma = _ssa.construir(corpo)
        _fixas, mortos = _ssa.constantes_condicionais(forma)
        for id_ in sorted(mortos):
            bloco = forma.bloco(id_)
            achados.append({"corpo": corpo.nome, "bloco": id_,
                            "rotulo": bloco.rotulo,
                            "linha": bloco.instrucoes[0].linha
                            if bloco.instrucoes else 0})
    return achados


def passes():
    """Os passes de otimização, com o que cada um faz."""
    return dict(_ot.PASSES)


def otimizar(fonte, quais=None):
    """`{passe: quantas vezes}` — o que dá para tirar deste arquivo.

    A conta é o valor; o ganho de tempo, **medido**, é 1,01× em código
    real, e está escrito na doc com esse número. Os passes ficam
    desligados por padrão.
    """
    _arvore_otimizada, contagem = _ot.otimizar(_arvore(fonte), quais)
    for passe in _ot.PASSES:
        contagem.setdefault(passe, 0)
    return contagem


def lir(fonte):
    """O que o compilador de fechamentos compilou, e o que recuou."""
    inventario = _lir.inventario(_arvore(fonte))
    return {
        "compiladas": inventario.compiladas,
        "recuadas": inventario.recuadas,
        "total": inventario.total,
        "proporcao": round(inventario.proporcao(), 1),
        "por_no": {classe: dict(contas)
                   for classe, contas in inventario.por_no.items()},
        "quentes": [{"no": classe, "linha": linha}
                    for classe, linha in inventario.quentes],
    }


def texto(fonte, fase="mir"):
    """A fase escrita, igual ao que `dataforge ir` mostra."""
    if fase not in FASES:
        raise RuntimeError_(
            f"'{fase}' is not a phase. The phases are: {', '.join(FASES)}. "
            f"There is no machine-code phase: the backend is the closure "
            f"compiler.", doc="compilador/pipeline")
    raiz = _arvore(fonte)
    if fase == "lexer":
        return "\n".join(f"  {t}" for t in tokenize(fonte, "<compilador>"))
    if fase == "parser":
        return "\n".join(f"  {i.__class__.__name__}" for i in raiz.body)
    if fase == "hir":
        return _hir.texto(_hir.normalizar(raiz))
    if fase == "ssa":
        return _ssa.texto([_ssa.construir(c) for c in _mir.construir(raiz)],
                          com_constantes=True)
    if fase == "otimizado":
        return _ot.texto(raiz)
    if fase == "lir":
        return _lir.texto(_lir.inventario(raiz))
    return _mir.texto(_mir.construir(raiz), com_analises=(fase == "analises"))


class ArcaneCompilador:
    """O dicionário que `adopt Arcane.Compilador` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Compilador",

            # ── o caminho ──
            "fases": fases,
            "tokens": tokens,
            "arvore": arvore,
            "texto": texto,

            # ── HIR ──
            "hir": hir,
            "acucares": acucares,
            "acucares_conhecidos": acucares_conhecidos,
            "nao_e_acucar": nao_e_acucar,
            "resolucao": resolucao,

            # ── MIR ──
            "mir": mir,
            "blocos": blocos,
            "corpos": corpos,

            # ── as análises ──
            "alcance": alcance,
            "constantes": constantes,
            "escapam": escapam,
            "vivas": vivas,
            "talvez_nao_definidas": talvez_nao_definidas,
            "onde_talvez_nao_definidas": onde_talvez_nao_definidas,

            # ── SSA ──
            "ssa": ssa,
            "dominancia": dominancia,
            "dot": dot,
            "provadas": provadas,
            "ramos_mortos": ramos_mortos,

            # ── otimizacao ──
            "passes": passes,
            "otimizar": otimizar,

            # ── LIR ──
            "lir": lir,
        }
