# -*- coding: utf-8 -*-
"""
O servidor de linguagem (LSP) do DataForge.

    dataforge lsp            # fala por stdin/stdout, como o protocolo manda

Ele nao reimplementa nada: o analisador estatico, o formatador e o
linter ja existem, e o que falta e o PROTOCOLO por cima deles. O
'typechecker' ja resolve nomes, conhece aridade, infere tipos e sugere
o nome parecido com difflib — tudo o que um editor precisa para
autocompletar, para o hover e para o erro sublinhado enquanto se digita.

─── Por que sem dependencia ────────────────────────────────

Ha bibliotecas prontas (pygls, lsprotocol). Nenhuma entra: o runtime do
DataForge nao tem dependencia externa, e o LSP roda dentro dele. O
protocolo em si e simples — JSON-RPC 2.0 sobre stdio, com um cabecalho
'Content-Length' — e o que se ganha em conforto nao paga quebrar a
promessa que a linguagem inteira faz.

─── O que ele responde ─────────────────────────────────────

    publishDiagnostics   erro e aviso enquanto se digita
    completion           palavras, embutidas, modulos, simbolos locais
    hover                assinatura e o que a coisa faz
    definition           ir para onde o nome foi declarado
    references           onde mais ele aparece
    documentSymbol       o esquema do arquivo, para a barra lateral
    signatureHelp        os parametros, enquanto se escreve a chamada
    rename               renomear com seguranca em todo o arquivo
    formatting           o mesmo 'dataforge fmt'
    codeAction           aplicar a sugestao do analisador

─── Duas decisoes ──────────────────────────────────────────

1. **Uma analise por versao de documento, guardada.** O editor pede
   diagnostico, depois hover, depois completion — tudo sobre o MESMO
   texto. Reanalisar a cada pedido multiplicaria o trabalho por cinco
   sem mudar uma virgula do resultado.

2. **Erro de sintaxe nao apaga o que ja se sabia.** Enquanto se digita,
   o arquivo passa a maior parte do tempo invalido — falta um ':',
   falta fechar um parentese. Se cada estado invalido zerasse o
   esquema, o autocompletar sumiria justo enquanto se escreve. A ultima
   analise BOA fica guardada e continua servindo.
"""

import difflib
import json
import os
import sys
import threading
import traceback

from . import ast_nodes as ast
from .builtins import get_builtins
from .errors import DataForgeError
from .exemplos_palavras import PALAVRAS
from .formatter import format_source
from .lexer import tokenize
from .parser import parse
from .stdlib import get_module, list_modules
from .stdlib.catalogo import DESCRICOES
from .tokens import CONTEXTUAIS_BLUEPRINT, CONTEXTUAIS_KILN, KEYWORDS
from .typechecker import check_program

#: Como o LSP numera severidade.
ERRO, AVISO, INFO, DICA = 1, 2, 3, 4

#: Como ele numera o tipo de um item de completar.
K_TEXTO, K_METODO, K_ACAO, K_CONSTRUTOR, K_CAMPO, K_VARIAVEL = 1, 2, 3, 4, 5, 6
K_CLASSE, K_INTERFACE, K_MODULO, K_PROPRIEDADE = 7, 8, 9, 10
K_VALOR, K_ENUM, K_PALAVRA, K_TRECHO = 12, 13, 14, 15
K_CONSTANTE, K_MEMBRO_ENUM, K_OPERADOR = 21, 20, 24

#: Como ele numera um simbolo do esquema do arquivo.
S_MODULO, S_ACAO, S_CLASSE, S_ENUM = 2, 12, 5, 10
S_VARIAVEL, S_CONSTANTE, S_CAMPO, S_MEMBRO_ENUM = 13, 14, 8, 22
S_METODO, S_INTERFACE, S_ESTRUTURA = 6, 11, 23


# ═════════════════════════════════════════════════════════════
#  O que sabemos de um arquivo
# ═════════════════════════════════════════════════════════════

class Simbolo:
    """Um nome declarado no arquivo, e tudo que o editor pede dele."""

    __slots__ = ("nome", "especie", "linha", "coluna", "detalhe", "doc",
                 "params", "filhos", "fim_linha")

    def __init__(self, nome, especie, linha, coluna, detalhe="", doc="",
                 params=None, fim_linha=None):
        self.nome = nome
        self.especie = especie          # 'acao' | 'blueprint' | 'record' | …
        self.linha = linha              # 1-based, como o DataForge conta
        self.coluna = coluna
        self.detalhe = detalhe          # a assinatura, para o hover
        self.doc = doc
        self.params = params or []
        self.filhos = []
        self.fim_linha = fim_linha if fim_linha is not None else linha


class Analise:
    """O resultado de olhar um arquivo uma vez.

    'boa' diz se o texto chegou a virar arvore. Um arquivo com erro de
    sintaxe ainda produz diagnostico — mas nao produz esquema, e por
    isso o servidor guarda a ultima analise boa em separado.
    """

    def __init__(self, texto, uri):
        self.texto = texto
        self.uri = uri
        self.linhas = texto.split("\n")
        self.diagnosticos = []
        self.simbolos = []
        self.programa = None
        self.boa = False
        self.modulos = {}          # apelido -> nome oficial do modulo

    def simbolo_em(self, nome):
        """O simbolo com este nome, procurando tambem nos filhos."""
        for s in self.simbolos:
            if s.nome == nome:
                return s
            for f in s.filhos:
                if f.nome == nome:
                    return f
        return None

    def linha_de(self, n):
        """A linha n (1-based), ou '' se estiver fora."""
        return self.linhas[n - 1] if 1 <= n <= len(self.linhas) else ""


# ═════════════════════════════════════════════════════════════
#  Ler o arquivo
# ═════════════════════════════════════════════════════════════

def _assinatura_de_acao(no):
    """'somar(a: Integer, b: Integer) -> Integer'."""
    tipos = getattr(no, "param_types", {}) or {}
    padroes = getattr(no, "defaults", {}) or {}
    partes = []
    for p in getattr(no, "params", []):
        texto = p
        if p in tipos:
            texto += f": {tipos[p]}"
        if p in padroes:
            texto += " := …"
        partes.append(texto)
    generico = ""
    if getattr(no, "type_params", None):
        generico = "<" + ", ".join(no.type_params) + ">"
    retorno = f" -> {no.return_type}" if getattr(no, "return_type", "") else ""
    prefixo = "stream action " if getattr(no, "is_stream", False) else \
              "async action " if getattr(no, "is_async", False) else "action "
    return f"{prefixo}{no.name}{generico}({', '.join(partes)}){retorno}"


def _doc_de(no, linhas):
    """O comentario logo ACIMA da declaracao.

    DataForge nao tem docstring: o costume, visivel nos 216 exercicios e
    na stdlib, e comentar em cima. Ler dali e o que faz o hover mostrar
    algo util sem inventar sintaxe nova.
    """
    fim = getattr(no, "line", 0) - 1        # a linha acima, 1-based -> indice
    juntas = []
    while fim >= 1:
        texto = linhas[fim - 1].strip() if fim <= len(linhas) else ""
        if texto.startswith("//"):
            juntas.append(texto.lstrip("/").strip())
            fim -= 1
            continue
        if not texto and juntas:            # linha em branco encerra
            break
        break
    return "\n".join(reversed(juntas))


def _fim_do_bloco(no):
    """A ultima linha que o no cobre, para o esquema do arquivo."""
    maior = getattr(no, "line", 0)
    pilha = [no]
    visto = 0
    while pilha and visto < 4000:            # teto: arquivo gerado pode ser enorme
        atual = pilha.pop()
        visto += 1
        linha = getattr(atual, "line", 0)
        if isinstance(linha, int) and linha > maior:
            maior = linha
        for campo in getattr(atual, "__dataclass_fields__", {}):
            valor = getattr(atual, campo, None)
            if isinstance(valor, list):
                pilha.extend(v for v in valor
                             if hasattr(v, "__dataclass_fields__"))
            elif hasattr(valor, "__dataclass_fields__"):
                pilha.append(valor)
    return maior


def _colher(programa, linhas):
    """Os simbolos de topo do arquivo, com os filhos de cada um."""
    saida = []
    for no in getattr(programa, "body", []) or []:
        s = None

        if isinstance(no, ast.ActionDeclaration):
            s = Simbolo(no.name, "acao", no.line, no.column,
                        _assinatura_de_acao(no), _doc_de(no, linhas),
                        list(no.params), _fim_do_bloco(no))

        elif isinstance(no, ast.BlueprintDeclaration):
            pais = f" extends {', '.join(no.parents)}" if no.parents else ""
            traits = f" with {', '.join(no.traits)}" if no.traits else ""
            s = Simbolo(no.name, "blueprint", no.line, no.column,
                        f"blueprint {no.name}{pais}{traits}",
                        _doc_de(no, linhas), [], _fim_do_bloco(no))
            for filho in no.body or []:
                if isinstance(filho, ast.ActionDeclaration):
                    s.filhos.append(Simbolo(
                        filho.name, "metodo", filho.line, filho.column,
                        _assinatura_de_acao(filho), _doc_de(filho, linhas),
                        list(filho.params), _fim_do_bloco(filho)))
            for campo in getattr(no, "fields_decl", []) or []:
                nome = campo[0] if isinstance(campo, (tuple, list)) else campo
                s.filhos.append(Simbolo(str(nome), "campo", no.line, no.column))

        elif isinstance(no, ast.RecordDeclaration):
            campos = ", ".join(f"{c[0]}: {c[1]}" for c in no.fields)
            s = Simbolo(no.name, "record", no.line, no.column,
                        f"record {no.name}({campos})", _doc_de(no, linhas),
                        [c[0] for c in no.fields], _fim_do_bloco(no))
            for c in no.fields:
                s.filhos.append(Simbolo(c[0], "campo", no.line, no.column,
                                        f"{c[0]}: {c[1]}"))
            for nome, metodo in (no.methods or {}).items():
                s.filhos.append(Simbolo(nome, "metodo", metodo.line,
                                        metodo.column,
                                        _assinatura_de_acao(metodo)))

        elif isinstance(no, ast.EnumDeclaration):
            s = Simbolo(no.name, "enum", no.line, no.column,
                        f"enum {no.name}", _doc_de(no, linhas), [],
                        _fim_do_bloco(no))
            for membro in no.members:
                nome = membro[0] if isinstance(membro, (tuple, list)) else membro
                s.filhos.append(Simbolo(str(nome), "membro_enum",
                                        no.line, no.column,
                                        f"{no.name}.{nome}"))

        elif isinstance(no, ast.TraitDeclaration):
            s = Simbolo(no.name, "trait", no.line, no.column,
                        f"trait {no.name}", _doc_de(no, linhas), [],
                        _fim_do_bloco(no))

        elif isinstance(no, ast.SteadyDeclaration):
            s = Simbolo(no.name, "constante", no.line, no.column,
                        f"steady {no.name}", _doc_de(no, linhas))

        elif isinstance(no, ast.Assignment) and \
                isinstance(no.target, ast.Identifier):
            tipo = getattr(no, "declared_type", "") or ""
            s = Simbolo(no.target.name, "variavel", no.line, no.column,
                        f"{no.target.name}{': ' + tipo if tipo else ''}",
                        _doc_de(no, linhas))

        if s is not None:
            saida.append(s)
    return saida


def _modulos_adotados(programa):
    """apelido -> nome oficial, para o completar depois do ponto."""
    mapa = {}
    for no in getattr(programa, "body", []) or []:
        if isinstance(no, ast.AdoptStatement) and not no.selection:
            mapa[no.alias or no.module.split(".")[-1]] = no.module
    return mapa


def analisar(texto, uri):
    """Olha o arquivo uma vez: diagnosticos, esquema, modulos."""
    a = Analise(texto, uri)
    caminho = _caminho_de(uri)

    try:
        arvore = parse(tokenize(texto, caminho), caminho)
    except DataForgeError as erro:
        a.diagnosticos.append(_do_erro(erro))
        return a
    except Exception as erro:                       # noqa: BLE001
        a.diagnosticos.append({
            "range": _faixa(1, 1, 1, 1),
            "severity": ERRO, "source": "dataforge",
            "message": str(erro)})
        return a

    a.programa = arvore
    a.boa = True
    a.simbolos = _colher(arvore, a.linhas)
    a.modulos = _modulos_adotados(arvore)

    try:
        # O texto do EDITOR, e nao o do disco: e nele que estao os
        # '// df: permitir <regra>' que a pessoa acabou de escrever, e
        # ler do disco silenciaria a regra errada — ou nenhuma — num
        # arquivo nao salvo.
        for d in check_program(arvore, caminho, source=texto):
            a.diagnosticos.append(_do_diagnostico(d, a))
    except Exception:                               # noqa: BLE001
        # O analisador falhar nao pode derrubar o servidor: sem
        # diagnostico o editor ainda colore, completa e navega.
        pass
    return a


def _do_erro(erro):
    linha = max(1, getattr(erro, "line", 1) or 1)
    coluna = max(1, getattr(erro, "column", 1) or 1)
    largura = max(1, getattr(erro, "span", 1) or 1)
    mensagem = getattr(erro, "message", str(erro))
    if getattr(erro, "dica", ""):
        mensagem += f"\n\ndica: {erro.dica}"
    return {
        "range": _faixa(linha, coluna, linha, coluna + largura),
        "severity": ERRO,
        "source": "dataforge",
        "code": getattr(erro, "codigo", "") or type(erro).__name__,
        "message": mensagem,
    }


def _do_diagnostico(d, analise):
    """Um Diagnostic do typechecker no formato do protocolo.

    A faixa cobre a PALAVRA sob o cursor, nao um caractere: sublinhado
    de um caractere so e quase invisivel, e o editor usa a faixa para
    decidir onde a lampada de correcao aparece.
    """
    linha = max(1, d.line or 1)
    coluna = max(1, d.column or 1)
    texto = analise.linha_de(linha)
    fim = coluna
    while fim - 1 < len(texto) and (texto[fim - 1].isalnum() or
                                    texto[fim - 1] in "_."):
        fim += 1
    saida = {
        "range": _faixa(linha, coluna, linha, max(fim, coluna + 1)),
        "severity": ERRO if d.severity == "error" else AVISO,
        "source": "dataforge",
        "message": d.message + (f"\n\ndica: {d.hint}" if d.hint else ""),
    }
    if d.code:
        saida["code"] = d.code
    return saida


def _faixa(l1, c1, l2, c2):
    """O protocolo conta de zero; o DataForge, de um."""
    return {"start": {"line": max(0, l1 - 1), "character": max(0, c1 - 1)},
            "end": {"line": max(0, l2 - 1), "character": max(0, c2 - 1)}}


def _caminho_de(uri):
    if uri.startswith("file://"):
        from urllib.parse import unquote, urlparse
        return unquote(urlparse(uri).path)
    return uri


# ═════════════════════════════════════════════════════════════
#  O catalogo do que se pode completar
# ═════════════════════════════════════════════════════════════

#: Palavra -> o que ela abre. So o que ajuda; repetir o nome nao ajuda.
#:
#: O EXEMPLO de cada uma vive em 'dataforge/exemplos_palavras.py', com um
#: teste que roda cada um. Dizer o que a palavra faz e metade: quem esta
#: aprendendo precisa ver como se escreve, e uma frase de dez palavras
#: nao substitui tres linhas de codigo.
_O_QUE_A_PALAVRA_FAZ = {
    "given": "condicional — given cond: … orif … otherwise:",
    "orif": "senão-se, dentro de um 'given'",
    "otherwise": "o ramo final de um 'given', ou o 'else' do ternário",
    "cycle": "laço — cycle i from 1 to 10  ou  cycle x in colecao",
    "persist": "laço enquanto a condição valer (while)",
    "perform": "roda uma vez antes de testar (do..while)",
    "halt": "sai do laço",
    "skip": "pula para a próxima volta",
    "action": "declara uma ação",
    "yield": "devolve e ENCERRA a ação",
    "emit": "produz um item, sem encerrar (só em 'stream action')",
    "stream": "generator preguiçoso — stream action",
    "blueprint": "declara uma classe",
    "spawn": "cria uma instância",
    "record": "estrutura imutável, com igualdade estrutural",
    "enum": "conjunto fechado de valores",
    "trait": "contrato de métodos",
    "extends": "herança",
    "with": "adota traits, ou copia um record mudando campos",
    "self": "a instância atual",
    "root": "o próximo na MRO — o 'super'",
    "match": "casamento de padrão estrutural",
    "point": "um caso do match",
    "when": "guarda de um 'point'",
    "default": "o caso final do match",
    "monitor": "bloco protegido (try)",
    "handle": "captura um erro; pode haver um por tipo",
    "ensure": "roda em qualquer saída (finally)",
    "trigger": "levanta um erro",
    "steady": "constante",
    "adopt": "importa um módulo",
    "relay": "exporta nomes do módulo",
    "out": "imprime",
    "assert": "cobra que a expressão seja verdadeira",
    "defer": "roda quando o escopo terminar",
    "thread": "dispara numa linha de execução",
    "lambda": "ação anônima — lambda x: expr",
    "mark": "aplica um decorador",
    "yes": "verdadeiro", "no": "falso", "void": "ausência de valor",
}

#: As palavras que abrem bloco — o editor as trata com peso próprio.
_ABREM_BLOCO = {"given", "orif", "otherwise", "cycle", "persist", "perform",
                "action", "blueprint", "record", "enum", "trait", "match",
                "point", "monitor", "handle", "ensure", "server", "route"}


def _itens_de_palavra():
    saida = []
    for palavra in sorted(set(KEYWORDS) | set(CONTEXTUAIS_BLUEPRINT) |
                          set(CONTEXTUAIS_KILN)):
        item = {"label": palavra, "kind": K_PALAVRA,
                "detail": (PALAVRAS[palavra][0] if palavra in PALAVRAS
                           else _O_QUE_A_PALAVRA_FAZ.get(
                               palavra, "palavra reservada")),
                # O exemplo aparece no painel ao lado do item selecionado,
                # antes de a pessoa aceitar a sugestao.
                "documentation": (
                    {"kind": "markdown",
                     "value": f"```dataforge\n{PALAVRAS[palavra][1]}\n```"}
                    if palavra in PALAVRAS else None)}
        if palavra in _ABREM_BLOCO:
            # O ':' e a quebra vem junto: quem escolhe 'given' vai
            # escrever ':' em seguida, sempre.
            item["insertText"] = f"{palavra} ${{1:condicao}}:\n\t$0" \
                if palavra in ("given", "orif") else palavra
            item["insertTextFormat"] = 2 if palavra in ("given", "orif") else 1
        saida.append(item)
    return saida


def _itens_embutidos():
    saida = []
    for nome, valor in get_builtins().items():
        if nome.startswith("_"):
            continue
        saida.append({
            "label": nome, "kind": K_ACAO,
            "detail": _assinatura_de_python(valor, nome),
            "documentation": (valor.__doc__ or "").strip().split("\n")[0]
            if callable(valor) else "",
        })
    return saida


def _itens_de_modulo():
    saida = []
    for nome in sorted({get_module(n)["__name__"] for n in set(list_modules())}):
        descricao, curto = DESCRICOES.get(nome, ("", ""))
        saida.append({"label": nome, "kind": K_MODULO,
                      "detail": curto, "documentation": descricao})
    return saida


def _assinatura_de_python(valor, nome):
    """A assinatura de uma embutida ou de um simbolo da stdlib."""
    if not callable(valor):
        return type(valor).__name__
    try:
        import inspect
        return nome + str(inspect.signature(valor))
    except (TypeError, ValueError):
        return nome + "(…)"


#: Montados uma vez: eles nao mudam entre pedidos, e sao ~1200 itens.
_PALAVRAS = None
_EMBUTIDAS = None
_MODULOS = None


def _catalogo():
    global _PALAVRAS, _EMBUTIDAS, _MODULOS
    if _PALAVRAS is None:
        _PALAVRAS = _itens_de_palavra()
        _EMBUTIDAS = _itens_embutidos()
        _MODULOS = _itens_de_modulo()
    return _PALAVRAS, _EMBUTIDAS, _MODULOS


def _simbolos_do_modulo(nome_oficial):
    """Os itens de completar de um modulo da stdlib."""
    modulo = get_module(nome_oficial)
    if not isinstance(modulo, dict):
        return []
    saida = []
    for chave in sorted(k for k in modulo if not k.startswith("__")):
        valor = modulo[chave]
        saida.append({
            "label": chave,
            "kind": K_ACAO if callable(valor) else
                    K_MODULO if isinstance(valor, dict) else K_CONSTANTE,
            "detail": _assinatura_de_python(valor, chave),
            "documentation": (getattr(valor, "__doc__", "") or
                              "").strip().split("\n")[0],
        })
    return saida


# ═════════════════════════════════════════════════════════════
#  Ler o que esta sob o cursor
# ═════════════════════════════════════════════════════════════

def _palavra_em(linha, coluna):
    """A palavra sob o cursor, e onde ela comeca e acaba (0-based)."""
    if not linha:
        return "", coluna, coluna
    fim = min(coluna, len(linha))
    inicio = fim
    while inicio > 0 and (linha[inicio - 1].isalnum() or linha[inicio - 1] == "_"):
        inicio -= 1
    while fim < len(linha) and (linha[fim].isalnum() or linha[fim] == "_"):
        fim += 1
    return linha[inicio:fim], inicio, fim


def _prefixo_com_ponto(linha, coluna):
    """'Math.sq' -> ('Math', 'sq'). Vazio quando nao ha ponto."""
    ate = linha[:coluna]
    if "." not in ate:
        return "", ""
    antes, _, depois = ate.rpartition(".")
    if not depois or depois.isidentifier() or depois == "":
        _, inicio, _ = _palavra_em(antes, len(antes))
        return antes[inicio:], depois
    return "", ""


def _locais_ate(analise, linha):
    """Os nomes visiveis ate esta linha, para o completar.

    Inclui os parametros da acao que CONTEM o cursor: dentro do corpo
    eles sao os nomes mais usados, e nao aparecer ali e o que mais faz
    alguem achar que o autocompletar 'nao funciona'.
    """
    saida = {}
    for s in analise.simbolos:
        saida[s.nome] = s
        if s.especie in ("acao", "blueprint", "record") and \
                s.linha <= linha <= s.fim_linha:
            for p in s.params:
                saida.setdefault(p, Simbolo(p, "parametro", s.linha, s.coluna,
                                            f"{p} — parâmetro de {s.nome}"))
            for f in s.filhos:
                saida.setdefault(f.nome, f)
    return saida


_ICONE = {
    "acao": K_ACAO, "metodo": K_METODO, "blueprint": K_CLASSE,
    "record": K_ESTRUTURA if False else K_CLASSE, "enum": K_ENUM,
    "membro_enum": K_MEMBRO_ENUM, "campo": K_CAMPO, "trait": K_INTERFACE,
    "variavel": K_VARIAVEL, "constante": K_CONSTANTE, "parametro": K_VARIAVEL,
}

_ESQUEMA = {
    "acao": S_ACAO, "metodo": S_METODO, "blueprint": S_CLASSE,
    "record": S_ESTRUTURA, "enum": S_ENUM, "membro_enum": S_MEMBRO_ENUM,
    "campo": S_CAMPO, "trait": S_INTERFACE, "variavel": S_VARIAVEL,
    "constante": S_CONSTANTE, "parametro": S_VARIAVEL,
}


def completar(analise, linha, coluna):
    """Os itens para o cursor nesta posicao."""
    texto = analise.linha_de(linha)
    dono, _ = _prefixo_com_ponto(texto, coluna)

    # Depois de um ponto: so o que existe DENTRO daquilo. Devolver o
    # catalogo inteiro ali e o que faz o autocompletar virar ruido.
    if dono:
        oficial = analise.modulos.get(dono)
        if oficial:
            return _simbolos_do_modulo(oficial)
        if get_module(dono) is not None:
            return _simbolos_do_modulo(get_module(dono)["__name__"])
        alvo = analise.simbolo_em(dono)
        if alvo and alvo.filhos:
            return [{"label": f.nome, "kind": _ICONE.get(f.especie, K_CAMPO),
                     "detail": f.detalhe, "documentation": f.doc}
                    for f in alvo.filhos]
        return []

    palavras, embutidas, modulos = _catalogo()
    locais = [{"label": s.nome, "kind": _ICONE.get(s.especie, K_VARIAVEL),
               "detail": s.detalhe or s.especie,
               "documentation": s.doc,
               # Os nomes do proprio arquivo vem primeiro: e o que se
               # procura em 9 de 10 vezes.
               "sortText": f"0{s.nome}"}
              for s in _locais_ate(analise, linha).values()]
    apelidos = [{"label": a, "kind": K_MODULO, "detail": oficial,
                 "sortText": f"1{a}"}
                for a, oficial in analise.modulos.items()]
    return locais + apelidos + palavras + embutidas + modulos


def hover(analise, linha, coluna):
    """O cartao que aparece ao parar o mouse."""
    texto = analise.linha_de(linha)
    dono, _ = _prefixo_com_ponto(texto, coluna + 1)
    palavra, _, _ = _palavra_em(texto, coluna)
    if not palavra:
        return None

    # Simbolo do proprio arquivo
    alvo = analise.simbolo_em(palavra)
    if alvo:
        corpo = f"```dataforge\n{alvo.detalhe or alvo.nome}\n```"
        if alvo.doc:
            corpo += f"\n\n{alvo.doc}"
        return corpo

    # Membro de modulo — 'Math.sqrt'
    if dono:
        oficial = analise.modulos.get(dono) or (
            get_module(dono)["__name__"] if get_module(dono) else None)
        if oficial:
            modulo = get_module(oficial)
            if palavra in modulo:
                valor = modulo[palavra]
                doc = (getattr(valor, "__doc__", "") or "").strip()
                return (f"```dataforge\n{oficial}.{_assinatura_de_python(valor, palavra)}\n```"
                        + (f"\n\n{doc}" if doc else ""))

    # Modulo
    if palavra in analise.modulos or get_module(palavra) is not None:
        oficial = analise.modulos.get(palavra) or get_module(palavra)["__name__"]
        descricao, curto = DESCRICOES.get(oficial, ("", ""))
        quantos = len([k for k in get_module(oficial) if not k.startswith("__")])
        return (f"```dataforge\nadopt {oficial}\n```\n\n{descricao}\n\n"
                f"*{quantos} símbolos · nome curto: `{curto}`*")

    # Embutida
    embutidas = get_builtins()
    if palavra in embutidas:
        valor = embutidas[palavra]
        doc = (getattr(valor, "__doc__", "") or "").strip()
        return (f"```dataforge\n{_assinatura_de_python(valor, palavra)}\n```"
                + (f"\n\n{doc}" if doc else "")
                + "\n\n*função embutida — não precisa de `adopt`*")

    # Palavra reservada
    ficha = PALAVRAS.get(palavra)
    if ficha is not None:
        explicacao, exemplo = ficha
        contexto = " (só dentro de um bloco `server`)" \
            if palavra in CONTEXTUAIS_KILN else ""
        return (f"**{palavra}** — {explicacao}\n\n"
                f"```dataforge\n{exemplo}\n```\n\n"
                f"*palavra reservada{contexto}*")

    if palavra in _O_QUE_A_PALAVRA_FAZ:
        return (f"```dataforge\n{palavra}\n```\n\n"
                f"{_O_QUE_A_PALAVRA_FAZ[palavra]}\n\n*palavra reservada*")
    if palavra in KEYWORDS or palavra in CONTEXTUAIS_KILN:
        contexto = " (só dentro de um bloco `server`)" \
            if palavra in CONTEXTUAIS_KILN else ""
        return f"```dataforge\n{palavra}\n```\n\n*palavra reservada{contexto}*"
    return None


def definicao(analise, linha, coluna):
    """Onde o nome sob o cursor foi declarado."""
    palavra, _, _ = _palavra_em(analise.linha_de(linha), coluna)
    alvo = analise.simbolo_em(palavra) if palavra else None
    if alvo is None:
        return None
    return {"uri": analise.uri,
            "range": _faixa(alvo.linha, alvo.coluna,
                            alvo.linha, alvo.coluna + len(alvo.nome))}


def referencias(analise, linha, coluna):
    """Onde mais este nome aparece no arquivo.

    E busca por texto, com fronteira de palavra — nao resolucao de
    escopo. Duas variaveis locais com o mesmo nome em acoes diferentes
    aparecem juntas. Para renomear dentro de um arquivo isso e o
    esperado; para um projeto, seria pouco — e o servidor nao promete
    mais do que faz.
    """
    palavra, _, _ = _palavra_em(analise.linha_de(linha), coluna)
    if not palavra:
        return []
    achados = []
    for n, texto in enumerate(analise.linhas, start=1):
        inicio = 0
        while True:
            i = texto.find(palavra, inicio)
            if i < 0:
                break
            antes = texto[i - 1] if i > 0 else " "
            depois = texto[i + len(palavra)] if i + len(palavra) < len(texto) else " "
            if not (antes.isalnum() or antes == "_") and \
               not (depois.isalnum() or depois == "_"):
                achados.append({"uri": analise.uri,
                                "range": _faixa(n, i + 1, n, i + 1 + len(palavra))})
            inicio = i + len(palavra)
    return achados


def esquema(analise):
    """O esquema do arquivo, para a barra lateral do editor."""
    def um(s):
        faixa = _faixa(s.linha, 1, s.fim_linha, 200)
        return {
            "name": s.nome,
            "detail": s.detalhe,
            "kind": _ESQUEMA.get(s.especie, S_VARIAVEL),
            "range": faixa,
            "selectionRange": _faixa(s.linha, s.coluna,
                                     s.linha, s.coluna + len(s.nome)),
            "children": [um(f) for f in s.filhos],
        }
    return [um(s) for s in analise.simbolos]


def ajuda_de_assinatura(analise, linha, coluna):
    """Os parametros da chamada que esta sendo escrita."""
    texto = analise.linha_de(linha)[:coluna]
    profundidade = 0
    for i in range(len(texto) - 1, -1, -1):
        if texto[i] == ")":
            profundidade += 1
        elif texto[i] == "(":
            if profundidade == 0:
                nome, _, _ = _palavra_em(texto, i)
                if not nome:
                    return None
                virgulas = texto[i:].count(",")
                alvo = analise.simbolo_em(nome)
                if alvo and alvo.params:
                    return {
                        "signatures": [{
                            "label": alvo.detalhe or nome,
                            "documentation": alvo.doc,
                            "parameters": [{"label": p} for p in alvo.params],
                        }],
                        "activeSignature": 0,
                        "activeParameter": min(virgulas, len(alvo.params) - 1),
                    }
                embutidas = get_builtins()
                if nome in embutidas:
                    return {"signatures": [{
                        "label": _assinatura_de_python(embutidas[nome], nome),
                        "documentation": (getattr(embutidas[nome], "__doc__", "")
                                          or "").strip().split("\n")[0]}],
                        "activeSignature": 0, "activeParameter": virgulas}
                return None
            profundidade -= 1
    return None


def renomear(analise, linha, coluna, novo):
    """Troca o nome em todo o arquivo — recusando o que quebraria."""
    palavra, _, _ = _palavra_em(analise.linha_de(linha), coluna)
    if not palavra:
        return None, "não há nome sob o cursor"
    if not novo.isidentifier():
        return None, f"'{novo}' não é um nome válido"
    # Uma palavra reservada como nome nao e erro do editor: e erro que
    # so apareceria depois, na proxima vez que o arquivo rodasse.
    if novo in KEYWORDS:
        return None, f"'{novo}' é palavra reservada do DataForge"
    edicoes = [{"range": r["range"], "newText": novo}
               for r in referencias(analise, linha, coluna)]
    if not edicoes:
        return None, f"'{palavra}' não foi encontrado"
    return {"changes": {analise.uri: edicoes}}, None


def acoes_de_codigo(analise, faixa):
    """As correcoes rapidas para os diagnosticos nesta faixa.

    So o que o analisador ja sabe consertar: quando a dica traz um nome
    entre aspas ('did you mean X?'), aplica-lo e mecanico. Inventar
    correcao a partir da mensagem seria adivinhacao.
    """
    import re
    saida = []
    inicio = faixa["start"]["line"]
    fim = faixa["end"]["line"]
    for d in analise.diagnosticos:
        if not (inicio <= d["range"]["start"]["line"] <= fim):
            continue
        # Sem IGNORECASE, 'Did you mean' — como o typechecker escreve —
        # nao casava, e a lampada de correcao nunca aparecia.
        m = re.search(r"did you mean '([^']+)'|quis dizer '([^']+)'",
                      d["message"], re.IGNORECASE)
        if not m:
            continue
        sugestao = m.group(1) or m.group(2)
        saida.append({
            "title": f"Trocar por '{sugestao}'",
            "kind": "quickfix",
            "diagnostics": [d],
            "isPreferred": True,
            "edit": {"changes": {analise.uri: [
                {"range": d["range"], "newText": sugestao}]}},
        })
    return saida


def formatar(analise):
    """O arquivo inteiro formatado — o mesmo 'dataforge fmt'."""
    try:
        novo = format_source(analise.texto)
    except Exception:                               # noqa: BLE001
        return None            # arquivo invalido: formatar quebraria mais
    if novo == analise.texto:
        return []
    return [{"range": _faixa(1, 1, len(analise.linhas) + 1, 1),
             "newText": novo}]


# ═════════════════════════════════════════════════════════════
#  O protocolo: JSON-RPC 2.0 sobre stdio
# ═════════════════════════════════════════════════════════════

class Servidor:
    """Le pedidos de stdin, responde em stdout.

    O transporte e o do LSP: cada mensagem vem precedida de
    'Content-Length: N', linha em branco, e N bytes de JSON. Ler byte a
    byte em vez de linha a linha importa — o corpo pode conter '\\n', e
    contar linhas ali corta a mensagem no meio.
    """

    def __init__(self, entrada=None, saida=None, registro=None):
        self.entrada = entrada or sys.stdin.buffer
        self.saida = saida or sys.stdout.buffer
        self.registro = registro
        self.documentos = {}        # uri -> texto
        self.analises = {}          # uri -> Analise (a mais recente)
        self.ultima_boa = {}        # uri -> Analise (a ultima que virou arvore)
        self.rodando = True
        self.trava = threading.Lock()

    # ── transporte ──────────────────────────────────────────

    def _ler(self):
        cabecalhos = {}
        while True:
            linha = self.entrada.readline()
            if not linha:
                return None                 # o editor fechou
            linha = linha.decode("utf-8", "replace").strip()
            if not linha:
                break
            if ":" in linha:
                chave, _, valor = linha.partition(":")
                cabecalhos[chave.strip().lower()] = valor.strip()
        tamanho = int(cabecalhos.get("content-length", 0))
        if tamanho <= 0:
            return None
        corpo = b""
        while len(corpo) < tamanho:          # read() pode devolver menos
            pedaco = self.entrada.read(tamanho - len(corpo))
            if not pedaco:
                return None
            corpo += pedaco
        try:
            return json.loads(corpo.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _escrever(self, mensagem):
        dados = json.dumps(mensagem, ensure_ascii=False).encode("utf-8")
        with self.trava:
            self.saida.write(b"Content-Length: %d\r\n\r\n" % len(dados))
            self.saida.write(dados)
            self.saida.flush()

    def _responder(self, ident, resultado):
        self._escrever({"jsonrpc": "2.0", "id": ident, "result": resultado})

    def _erro(self, ident, codigo, mensagem):
        self._escrever({"jsonrpc": "2.0", "id": ident,
                        "error": {"code": codigo, "message": mensagem}})

    def _notificar(self, metodo, parametros):
        self._escrever({"jsonrpc": "2.0", "method": metodo,
                        "params": parametros})

    def _log(self, texto):
        if self.registro:
            self.registro.write(texto + "\n")
            self.registro.flush()

    # ── documentos ──────────────────────────────────────────

    def _analisar(self, uri):
        a = analisar(self.documentos.get(uri, ""), uri)
        self.analises[uri] = a
        if a.boa:
            self.ultima_boa[uri] = a
        return a

    def _para_consultar(self, uri):
        """A analise que responde hover/completar/esquema.

        Enquanto se digita, o arquivo passa a maior parte do tempo
        invalido. Devolver a analise quebrada faria o autocompletar
        sumir justo no meio da escrita — que e quando ele mais serve.
        """
        atual = self.analises.get(uri)
        if atual is not None and atual.boa:
            return atual
        antiga = self.ultima_boa.get(uri)
        if antiga is None:
            return atual or Analise(self.documentos.get(uri, ""), uri)
        # O TEXTO precisa ser o de agora: as posicoes vem do editor, e
        # ler a linha do texto velho apontaria para outro lugar.
        antiga.texto = self.documentos.get(uri, antiga.texto)
        antiga.linhas = antiga.texto.split("\n")
        return antiga

    def _publicar(self, uri):
        analise = self.analises.get(uri)
        if analise is None:
            return
        self._notificar("textDocument/publishDiagnostics",
                        {"uri": uri, "diagnostics": analise.diagnosticos})

    # ── laco ────────────────────────────────────────────────

    def rodar(self):
        while self.rodando:
            try:
                mensagem = self._ler()
            except Exception as erro:               # noqa: BLE001
                self._log(f"falha ao ler: {erro}")
                break
            if mensagem is None:
                break
            try:
                self._despachar(mensagem)
            except Exception:                       # noqa: BLE001
                # Um pedido que estoura nao pode derrubar o servidor: o
                # editor ficaria sem diagnostico e sem aviso nenhum, e a
                # pessoa culparia a linguagem.
                self._log(traceback.format_exc())
                if mensagem.get("id") is not None:
                    self._erro(mensagem["id"], -32603, "erro interno")
        return 0

    def _despachar(self, mensagem):
        metodo = mensagem.get("method")
        ident = mensagem.get("id")
        p = mensagem.get("params") or {}
        tratador = getattr(self, "m_" + (metodo or "").replace("/", "_")
                           .replace("$", "cifrao"), None)
        if tratador is None:
            if ident is not None:
                self._erro(ident, -32601, f"método desconhecido: {metodo}")
            return
        resultado = tratador(p, ident)
        if ident is not None and resultado is not _SEM_RESPOSTA:
            self._responder(ident, resultado)

    # ── ciclo de vida ───────────────────────────────────────

    def m_initialize(self, p, ident):
        from . import __version__
        return {
            "capabilities": {
                # 1 = o editor manda o documento INTEIRO a cada tecla.
                # Diferencial (2) economiza banda num processo que fala
                # por um cano local — e cada aplicacao errada de um
                # diff e um estado que ninguem consegue reproduzir.
                "textDocumentSync": {"openClose": True, "change": 1,
                                     "save": {"includeText": False}},
                "completionProvider": {
                    "triggerCharacters": [".", ":", "@"],
                    "resolveProvider": False,
                },
                "hoverProvider": True,
                "definitionProvider": True,
                "referencesProvider": True,
                "documentSymbolProvider": True,
                "documentFormattingProvider": True,
                "renameProvider": {"prepareProvider": True},
                "signatureHelpProvider": {"triggerCharacters": ["(", ","]},
                "codeActionProvider": {"codeActionKinds": ["quickfix"]},
                "documentHighlightProvider": True,
            },
            "serverInfo": {"name": "dataforge-lsp", "version": __version__},
        }

    def m_initialized(self, p, ident):
        return _SEM_RESPOSTA

    def m_shutdown(self, p, ident):
        self.rodando = False
        return None

    def m_exit(self, p, ident):
        self.rodando = False
        return _SEM_RESPOSTA

    def m_cifraocancelRequest(self, p, ident):
        return _SEM_RESPOSTA

    # ── sincronizacao ───────────────────────────────────────

    def m_textDocument_didOpen(self, p, ident):
        doc = p["textDocument"]
        self.documentos[doc["uri"]] = doc.get("text", "")
        self._analisar(doc["uri"])
        self._publicar(doc["uri"])
        return _SEM_RESPOSTA

    def m_textDocument_didChange(self, p, ident):
        uri = p["textDocument"]["uri"]
        mudancas = p.get("contentChanges") or []
        if mudancas:
            self.documentos[uri] = mudancas[-1].get("text", "")
        self._analisar(uri)
        self._publicar(uri)
        return _SEM_RESPOSTA

    def m_textDocument_didSave(self, p, ident):
        uri = p["textDocument"]["uri"]
        if "text" in p:
            self.documentos[uri] = p["text"]
        self._analisar(uri)
        self._publicar(uri)
        return _SEM_RESPOSTA

    def m_textDocument_didClose(self, p, ident):
        uri = p["textDocument"]["uri"]
        for onde in (self.documentos, self.analises, self.ultima_boa):
            onde.pop(uri, None)
        # Limpar os diagnosticos: senao eles ficam no painel de
        # problemas apontando para um arquivo que nao esta mais aberto.
        self._notificar("textDocument/publishDiagnostics",
                        {"uri": uri, "diagnostics": []})
        return _SEM_RESPOSTA

    # ── as respostas ────────────────────────────────────────

    def _onde(self, p):
        uri = p["textDocument"]["uri"]
        pos = p.get("position") or {"line": 0, "character": 0}
        return self._para_consultar(uri), pos["line"] + 1, pos["character"]

    def m_textDocument_completion(self, p, ident):
        analise, linha, coluna = self._onde(p)
        return {"isIncomplete": False, "items": completar(analise, linha, coluna)}

    def m_textDocument_hover(self, p, ident):
        analise, linha, coluna = self._onde(p)
        texto = hover(analise, linha, coluna)
        if not texto:
            return None
        return {"contents": {"kind": "markdown", "value": texto}}

    def m_textDocument_definition(self, p, ident):
        analise, linha, coluna = self._onde(p)
        return definicao(analise, linha, coluna)

    def m_textDocument_references(self, p, ident):
        analise, linha, coluna = self._onde(p)
        return referencias(analise, linha, coluna)

    def m_textDocument_documentHighlight(self, p, ident):
        analise, linha, coluna = self._onde(p)
        return [{"range": r["range"]}
                for r in referencias(analise, linha, coluna)]

    def m_textDocument_documentSymbol(self, p, ident):
        return esquema(self._para_consultar(p["textDocument"]["uri"]))

    def m_textDocument_signatureHelp(self, p, ident):
        analise, linha, coluna = self._onde(p)
        return ajuda_de_assinatura(analise, linha, coluna)

    def m_textDocument_formatting(self, p, ident):
        uri = p["textDocument"]["uri"]
        analise = self.analises.get(uri) or self._para_consultar(uri)
        return formatar(analise)

    def m_textDocument_prepareRename(self, p, ident):
        analise, linha, coluna = self._onde(p)
        palavra, inicio, fim = _palavra_em(analise.linha_de(linha), coluna)
        if not palavra:
            return None
        return _faixa(linha, inicio + 1, linha, fim + 1)

    def m_textDocument_rename(self, p, ident):
        analise, linha, coluna = self._onde(p)
        edicao, motivo = renomear(analise, linha, coluna, p.get("newName", ""))
        if edicao is None:
            self._erro(ident, -32602, motivo or "não dá para renomear")
            return _SEM_RESPOSTA
        return edicao

    def m_textDocument_codeAction(self, p, ident):
        uri = p["textDocument"]["uri"]
        analise = self.analises.get(uri) or self._para_consultar(uri)
        return acoes_de_codigo(analise, p.get("range") or
                               {"start": {"line": 0}, "end": {"line": 10 ** 6}})


class _SemResposta:
    """Marca uma notificacao: ela nao devolve nada, nem 'null'."""


_SEM_RESPOSTA = _SemResposta()


def main(argv=None):
    """'dataforge lsp' — fala o protocolo por stdin/stdout."""
    argv = list(argv or [])
    registro = None
    for arg in argv:
        if arg.startswith("--log="):
            registro = open(arg.split("=", 1)[1], "a", encoding="utf-8")
    # stdout e o CANAL: qualquer print perdido corrompe a proxima
    # mensagem, e o editor desiste sem dizer por que.
    return Servidor(registro=registro).rodar()
