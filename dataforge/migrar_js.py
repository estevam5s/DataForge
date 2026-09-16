"""JavaScript e TypeScript → DataForge. `dataforge converter app.ts`

O que ele é
-----------
O irmão de `migrar.py`, com a mesma promessa e a mesma honestidade: ele
**lê** a linguagem de origem — tokenizador e parser próprios, não
expressão regular — e emite DataForge com a indentação e o vocabulário
certos. O que não tem equivalente honesto vira um comentário
`// TODO(converter):` com o código original ao lado.

Por que um parser próprio
-------------------------
O Python traz o `ast` na biblioteca padrão, e por isso `migrar.py` não
precisou de parser. Para JavaScript não há nada equivalente, e a regra
deste repositório é **zero dependência externa**. Escrever um parser de
JS inteiro seria um projeto à parte; escrever o de um **subconjunto
declarado** é o trabalho de um arquivo — e é o que está aqui.

A fronteira é explícita: o que o parser não reconhece vira pendência
apontando a linha, nunca um palpite. Um conversor que erra em silêncio é
pior que um que aponta onde parou.

O TypeScript entra pela mesma porta
-----------------------------------
As anotações de tipo do TS são **lidas** e aproveitadas: `n: number`
vira `n: Float`, `-> string` vira `-> String`, e `interface` vira
`trait`. O que é só do sistema de tipos e não existe em execução
(`type X = …`, genéricos condicionais, `as const`) é descartado com nota,
porque a DataForge não tem onde guardar.

Três decisões que valem lembrar
-------------------------------
1. **Uma função de seta com corpo em bloco não vira `lambda`.** O
   `lambda` da DataForge é uma expressão só. `xs.map(x => { … })` vira
   uma ação nomeada acima, e a chamada passa a referenciá-la — traduzir
   para um `lambda` com ponto e vírgula produziria algo que não compila.
2. **`for (let i = 0; i < n; i++)` vira `cycle i from 0 to n - 1`** só
   quando as três partes têm a forma exata. Qualquer variação vira
   `persist`, que é sempre correto.
3. **`null` e `undefined` viram os dois `void`.** A DataForge tem um
   vazio só, e fingir dois seria inventar semântica que ela não tem.

A divergência que ele não mascara
---------------------------------
Em JavaScript, `v.naoExiste` devolve `undefined`; na DataForge, ler uma
chave ausente é **erro**. O `?.` não muda isso nas duas linguagens — ele
protege contra o lado esquerdo vazio, e não contra o campo que falta.

Traduzir esse acesso para algo que devolve `void` calado transformaria um
erro de digitação num vazio que atravessa o programa inteiro. A tradução
mantém o acesso, e o programa falha na linha certa. Quem quer o
comportamento do JS escreve `v["b"] ?? padrao`, que é o que a DataForge
oferece para isso.
"""

import io
import os
import re

# ═════════════════════════════════════════════════════════════
#  Tabelas
# ═════════════════════════════════════════════════════════════

PALAVRAS = frozenset("""
break case catch class const continue debugger default delete do else
export extends finally for function if import in instanceof let new
return static super switch this throw try typeof var void while with
yield async await of get set
interface type enum implements private protected public readonly
abstract declare namespace as satisfies
""".split())

#: Operadores, do mais longo para o mais curto — a ordem é o que faz
#: '===' não ser lido como '==' seguido de '='.
OPERADORES = sorted([
    ">>>=", "...", "===", "!==", "**=", "<<=", ">>=", ">>>", "&&=", "||=",
    "??=", "=>", "==", "!=", "<=", ">=", "&&", "||", "??", "?.", "++", "--",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "**", "<<", ">>",
    "{", "}", "(", ")", "[", "]", ";", ",", "<", ">", "+", "-", "*", "/",
    "%", "&", "|", "^", "!", "~", "?", ":", "=", ".", "@", "#",
], key=len, reverse=True)

#: Comparação e lógica: o que muda de nome ao virar DataForge.
_COMPARACAO = {
    "===": "is", "==": "is", "!==": "isnt", "!=": "isnt",
    "&&": "and", "||": "or",
}

#: Os tipos do TypeScript que têm equivalente honesto.
TIPOS = {
    "number": "Float", "string": "String", "boolean": "Boolean",
    "any": "Any", "unknown": "Any", "object": "Vault", "void": "Void",
    "null": "Void", "undefined": "Void", "bigint": "Integer",
    "Array": "Cluster", "Object": "Vault", "Map": "Vault", "Set": "Cluster",
    "Function": "Action", "Promise": "Any", "Date": "Any", "symbol": "Any",
    "never": "Void", "int": "Integer", "float": "Float",
}

#: Globais do JS que têm um embutido da DataForge com outro nome.
_GLOBAIS = {
    "console.log": "out", "console.info": "out", "console.debug": "out",
    "parseInt": "int", "parseFloat": "float", "String": "str",
    "Number": "float", "Boolean": "bool", "Array.from": "cluster",
    "Object.keys": "keys", "Object.values": "values",
    "Object.entries": "items", "Math.floor": "floor", "Math.ceil": "ceil",
    "Math.abs": "abs", "Math.max": "max", "Math.min": "min",
    "Math.round": "round", "Math.sqrt": "sqrt", "Math.pow": "pow",
    "Math.random": "random", "isNaN": "is_nan", "JSON.stringify": "to_json",
    "JSON.parse": "from_json", "Number.isInteger": "is_integer",
}

#: Métodos de coleção e texto que mudam de nome.
_METODOS = {
    "push": "append", "forEach": "each", "indexOf": "index_of",
    "includes": "contains", "toUpperCase": "upper", "toLowerCase": "lower",
    "trim": "strip", "trimStart": "lstrip", "trimEnd": "rstrip",
    "startsWith": "starts_with", "endsWith": "ends_with",
    "toString": "str", "charAt": "char_at", "padStart": "pad_start",
    "padEnd": "pad_end", "concat": "concat", "shift": "pop_left",
    "unshift": "push_left", "splice": "splice", "findIndex": "find_index",
}

#: As palavras que a DataForge reserva, e que um nome vindo do JS não
#: pode usar. Lida de 'tokens.py' para nunca envelhecer.
def _reservadas():
    from .tokens import KEYWORDS
    return set(KEYWORDS)


# ═════════════════════════════════════════════════════════════
#  Tokenizador
# ═════════════════════════════════════════════════════════════

class Token:
    __slots__ = ("tipo", "valor", "linha", "antes_de_quebra")

    def __init__(self, tipo, valor, linha, antes_de_quebra=False):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.antes_de_quebra = antes_de_quebra

    def __repr__(self):
        return f"<{self.tipo} {self.valor!r} L{self.linha}>"


class ErroDeLeitura(Exception):
    """A fonte não é JavaScript/TypeScript que este parser saiba ler."""

    def __init__(self, mensagem, linha):
        super().__init__(f"linha {linha}: {mensagem}")
        self.linha = linha


_NUMERO = re.compile(
    r"0[xX][0-9a-fA-F_]+n?|0[bB][01_]+n?|0[oO][0-7_]+n?"
    r"|(?:\d[\d_]*)?\.?\d[\d_]*(?:[eE][+-]?\d+)?n?")
_NOME = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")

#: Depois destes, uma '/' começa uma expressão regular — e não uma
#: divisão. Sem essa distinção, '/\d+/.test(s)' é lido como divisão e o
#: resto da linha vira lixo.
_ANTES_DE_REGEX = frozenset({
    "(", ",", "=", ":", "[", "!", "&", "|", "?", "{", "}", ";", "+", "-",
    "*", "%", "<", ">", "==", "===", "!=", "!==", "=>", "&&", "||", "??",
    "return", "typeof", "instanceof", "in", "of", "new", "delete", "case",
    "do", "else", "yield", "await",
})


def tokenizar(fonte):
    """O texto vira tokens. Comentários somem; a quebra de linha fica
    marcada no token seguinte, porque o JS usa isso (inserção automática
    de ponto e vírgula) e ignorá-la junta duas instruções numa."""
    saida = []
    i, n, linha = 0, len(fonte), 1
    quebrou = False

    while i < n:
        c = fonte[i]

        if c == "\n":
            linha += 1
            quebrou = True
            i += 1
            continue
        if c in " \t\r\f\v":
            i += 1
            continue

        # ── comentários ──
        if fonte.startswith("//", i):
            fim = fonte.find("\n", i)
            i = n if fim < 0 else fim
            continue
        if fonte.startswith("/*", i):
            fim = fonte.find("*/", i + 2)
            if fim < 0:
                raise ErroDeLeitura("comentário /* sem fechar", linha)
            linha += fonte.count("\n", i, fim)
            i = fim + 2
            continue

        # ── texto ──
        if c in "'\"":
            valor, i, linha = _ler_texto(fonte, i, linha, c)
            saida.append(Token("TEXTO", valor, linha, quebrou))
            quebrou = False
            continue
        if c == "`":
            partes, i, linha = _ler_template(fonte, i, linha)
            saida.append(Token("TEMPLATE", partes, linha, quebrou))
            quebrou = False
            continue

        # ── número ──
        if c.isdigit() or (c == "." and i + 1 < n and fonte[i + 1].isdigit()):
            m = _NUMERO.match(fonte, i)
            saida.append(Token("NUMERO", m.group(0), linha, quebrou))
            quebrou = False
            i = m.end()
            continue

        # ── nome ou palavra ──
        if c.isalpha() or c in "_$":
            m = _NOME.match(fonte, i)
            texto = m.group(0)
            tipo = "PALAVRA" if texto in PALAVRAS else "NOME"
            saida.append(Token(tipo, texto, linha, quebrou))
            quebrou = False
            i = m.end()
            continue

        # ── expressão regular, quando a posição permite ──
        if c == "/" and _cabe_regex(saida):
            valor, i, linha = _ler_regex(fonte, i, linha)
            saida.append(Token("REGEX", valor, linha, quebrou))
            quebrou = False
            continue

        # ── operador ──
        for op in OPERADORES:
            if fonte.startswith(op, i):
                saida.append(Token("OP", op, linha, quebrou))
                quebrou = False
                i += len(op)
                break
        else:
            raise ErroDeLeitura(f"caractere inesperado: {c!r}", linha)

    saida.append(Token("FIM", "", linha, True))
    return saida


def _cabe_regex(saida):
    if not saida:
        return True
    ultimo = saida[-1]
    if ultimo.tipo in ("NUMERO", "TEXTO", "TEMPLATE", "NOME", "REGEX"):
        return False
    if ultimo.tipo == "PALAVRA":
        return ultimo.valor in _ANTES_DE_REGEX
    return ultimo.valor in _ANTES_DE_REGEX


def _ler_texto(fonte, i, linha, aspas):
    i += 1
    fora = []
    while i < len(fonte) and fonte[i] != aspas:
        if fonte[i] == "\\":
            fora.append(fonte[i:i + 2])
            i += 2
            continue
        if fonte[i] == "\n":
            raise ErroDeLeitura("texto sem fechar", linha)
        fora.append(fonte[i])
        i += 1
    if i >= len(fonte):
        raise ErroDeLeitura("texto sem fechar", linha)
    return "".join(fora), i + 1, linha


def _ler_template(fonte, i, linha):
    """Um template literal vira uma lista de pedaços: ('texto', s) e
    ('expr', codigo). O `${}` pode aninhar chaves, e contar é o que
    impede `${ {a: 1} }` de fechar cedo."""
    i += 1
    partes, atual = [], []
    while i < len(fonte) and fonte[i] != "`":
        if fonte[i] == "\\":
            atual.append(fonte[i:i + 2])
            i += 2
            continue
        if fonte.startswith("${", i):
            if atual:
                partes.append(("texto", "".join(atual)))
                atual = []
            profundidade, j = 1, i + 2
            while j < len(fonte) and profundidade:
                if fonte[j] == "{":
                    profundidade += 1
                elif fonte[j] == "}":
                    profundidade -= 1
                    if not profundidade:
                        break
                elif fonte[j] in "'\"`":
                    _, j, linha = _ler_texto(fonte, j, linha, fonte[j])
                    continue
                j += 1
            if j >= len(fonte):
                raise ErroDeLeitura("${ sem fechar num template", linha)
            partes.append(("expr", fonte[i + 2:j]))
            i = j + 1
            continue
        if fonte[i] == "\n":
            linha += 1
        atual.append(fonte[i])
        i += 1
    if i >= len(fonte):
        raise ErroDeLeitura("template sem fechar", linha)
    if atual:
        partes.append(("texto", "".join(atual)))
    return partes, i + 1, linha


def _ler_regex(fonte, i, linha):
    inicio = i
    i += 1
    dentro_de_classe = False
    while i < len(fonte):
        c = fonte[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            dentro_de_classe = True
        elif c == "]":
            dentro_de_classe = False
        elif c == "/" and not dentro_de_classe:
            break
        elif c == "\n":
            raise ErroDeLeitura("expressão regular sem fechar", linha)
        i += 1
    i += 1
    while i < len(fonte) and fonte[i].isalpha():
        i += 1
    return fonte[inicio:i], i, linha


# ═════════════════════════════════════════════════════════════
#  Parser
# ═════════════════════════════════════════════════════════════
#
# A árvore é feita de dicionários com a chave 't' dizendo o tipo. Um
# dataclass por nó daria trinta classes para um arquivo que as usa uma
# vez cada; o dicionário mantém o parser legível e o emissor é quem sabe
# o que fazer com cada 't'.

class Parser:
    """Um subconjunto declarado de JavaScript e TypeScript.

    O que ele reconhece está nos métodos abaixo. O que ele não reconhece
    vira um nó `{"t": "cru"}` com o texto original e a linha — e o
    emissor o transforma em pendência, nunca em palpite.
    """

    def __init__(self, tokens, fonte=""):
        self.tokens = tokens
        self.pos = 0
        self.linhas = fonte.splitlines()

    # ── navegação ───────────────────────────────────────────

    def atual(self):
        return self.tokens[self.pos]

    def olhar(self, adiante=1):
        i = min(self.pos + adiante, len(self.tokens) - 1)
        return self.tokens[i]

    def avancar(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def e(self, valor, tipo=None):
        tok = self.atual()
        if tipo and tok.tipo != tipo:
            return False
        return tok.valor == valor

    def aceitar(self, valor, tipo=None):
        if self.e(valor, tipo):
            return self.avancar()
        return None

    def exigir(self, valor):
        if not self.e(valor):
            raise ErroDeLeitura(
                f"era esperado {valor!r}, veio {self.atual().valor!r}",
                self.atual().linha)
        return self.avancar()

    def ponto_e_virgula(self):
        """O ';' é opcional em JS. Aceita-o, e segue sem ele."""
        self.aceitar(";")

    # ── programa ────────────────────────────────────────────

    def programa(self):
        corpo = []
        while self.atual().tipo != "FIM":
            corpo.append(self.instrucao())
        return corpo

    def instrucao(self):
        tok = self.atual()
        linha = tok.linha

        if tok.valor == "{" and tok.tipo == "OP":
            return {"t": "bloco", "corpo": self.bloco(), "linha": linha}
        if tok.valor == ";":
            self.avancar()
            return {"t": "vazio", "linha": linha}

        if tok.tipo == "PALAVRA":
            metodo = {
                "const": self.declaracao, "let": self.declaracao,
                "var": self.declaracao,
                "function": self.funcao, "async": self.talvez_async,
                "class": self.classe, "if": self.se, "for": self.para,
                "while": self.enquanto, "do": self.faca,
                "switch": self.escolha, "try": self.tentar,
                "throw": self.lancar, "return": self.retornar,
                "break": self.parar, "continue": self.pular,
                "import": self.importar, "export": self.exportar,
                "interface": self.interface, "type": self.tipo_alias,
                "enum": self.enumeracao,
            }.get(tok.valor)
            if metodo:
                return metodo()

        expr = self.expressao()
        self.ponto_e_virgula()
        return {"t": "expr", "valor": expr, "linha": linha}

    def bloco(self):
        self.exigir("{")
        corpo = []
        while not self.e("}") and self.atual().tipo != "FIM":
            corpo.append(self.instrucao())
        self.exigir("}")
        return corpo

    def corpo_ou_instrucao(self):
        """`if (c) x();` sem chaves é um corpo de uma instrução só."""
        if self.e("{"):
            return self.bloco()
        return [self.instrucao()]

    # ── declarações ─────────────────────────────────────────

    def declaracao(self):
        linha = self.atual().linha
        palavra = self.avancar().valor
        itens = []
        while True:
            alvo = self.alvo_de_declaracao()
            anotacao = self.anotacao_de_tipo()
            valor = self.expressao() if self.aceitar("=") else None
            itens.append({"alvo": alvo, "tipo": anotacao, "valor": valor})
            if not self.aceitar(","):
                break
        self.ponto_e_virgula()
        return {"t": "declara", "fixo": palavra == "const",
                "itens": itens, "linha": linha}

    def alvo_de_declaracao(self):
        if self.e("[") or self.e("{"):
            return self.padrao_de_desestruturacao()
        tok = self.atual()
        if tok.tipo not in ("NOME", "PALAVRA"):
            raise ErroDeLeitura(
                f"era esperado um nome, veio {tok.valor!r}", tok.linha)
        return {"t": "nome", "valor": self.avancar().valor}

    def padrao_de_desestruturacao(self):
        if self.aceitar("["):
            nomes = []
            while not self.e("]"):
                if self.aceitar("..."):
                    nomes.append({"resto": True,
                                  "nome": self.avancar().valor})
                elif self.e(","):
                    nomes.append(None)
                else:
                    nomes.append({"resto": False,
                                  "nome": self.avancar().valor})
                if not self.aceitar(","):
                    break
            self.exigir("]")
            return {"t": "padrao_lista", "nomes": nomes}

        self.exigir("{")
        campos = []
        while not self.e("}"):
            if self.aceitar("..."):
                campos.append({"chave": None, "nome": self.avancar().valor,
                               "resto": True})
            else:
                chave = self.avancar().valor
                nome = self.avancar().valor if self.aceitar(":") else chave
                campos.append({"chave": chave, "nome": nome, "resto": False})
            if not self.aceitar(","):
                break
        self.exigir("}")
        return {"t": "padrao_vault", "campos": campos}

    def anotacao_de_tipo(self):
        """`: number` do TypeScript. Devolve o texto do tipo, ou None."""
        if not self.e(":"):
            return None
        self.avancar()
        return self.texto_de_tipo()

    def texto_de_tipo(self):
        """Consome um tipo do TS e devolve o texto dele, sem interpretar.

        A tradução para o vocabulário da DataForge é do emissor: aqui só
        interessa saber ONDE o tipo acaba, para o parser não se perder.
        """
        pedacos = []
        profundidade = 0
        while self.atual().tipo != "FIM":
            tok = self.atual()
            if profundidade == 0 and tok.valor in (
                    ",", ";", ")", "}", "=", "=>") and not (
                    tok.valor == "=>" and pedacos and pedacos[-1] == ")"):
                break
            if profundidade == 0 and tok.valor == "]":
                break
            # Um '{' no meio de um tipo, fora de qualquer aninhamento, e o
            # CORPO comecando: 'function f(): Promise<string> {'. So no
            # inicio ele e um tipo de objeto ('{ a: number }').
            if profundidade == 0 and tok.valor == "{" and pedacos:
                break
            if tok.valor in ("<", "(", "[", "{"):
                profundidade += 1
            elif tok.valor in (">", ")", "]", "}"):
                if profundidade == 0:
                    break
                profundidade -= 1
            valor = self.avancar().valor
            pedacos.append(valor if isinstance(valor, str) else "…")
        return " ".join(pedacos).replace(" [ ]", "[]").replace(" < ", "<")

    def referencia_de_tipo(self):
        """Só o NOME de um tipo: 'A', 'M.A', 'A<T>'.

        É o que vem depois de `extends` e de `implements`, e ali um '{'
        é o corpo da classe começando — ler um tipo inteiro engoliria a
        classe inteira.
        """
        if self.atual().tipo not in ("NOME", "PALAVRA"):
            return ""
        nome = self.avancar().valor
        while self.e("."):
            self.avancar()
            nome += "." + self.avancar().valor
        if self.e("<"):
            self.parametros_de_tipo()
        return nome

    # ── funções ─────────────────────────────────────────────

    def talvez_async(self):
        if self.olhar().valor in ("function",):
            self.avancar()
            no = self.funcao()
            no["assincrona"] = True
            return no
        linha = self.atual().linha
        expr = self.expressao()
        self.ponto_e_virgula()
        return {"t": "expr", "valor": expr, "linha": linha}

    def funcao(self):
        linha = self.atual().linha
        self.exigir("function")
        gerador = bool(self.aceitar("*"))
        nome = self.avancar().valor if self.atual().tipo in ("NOME", "PALAVRA") \
            and not self.e("(") else ""
        self.parametros_de_tipo()
        parametros = self.parametros()
        retorno = self.anotacao_de_tipo()
        corpo = self.bloco()
        return {"t": "acao", "nome": nome, "parametros": parametros,
                "retorno": retorno, "corpo": corpo, "gerador": gerador,
                "assincrona": False, "linha": linha}

    def parametros_de_tipo(self):
        """`<T, U extends X>` — lido e descartado, exceto os nomes."""
        if not self.e("<"):
            return []
        profundidade = 0
        nomes = []
        while self.atual().tipo != "FIM":
            tok = self.avancar()
            if tok.valor == "<":
                profundidade += 1
            elif tok.valor == ">":
                profundidade -= 1
                if not profundidade:
                    break
            elif tok.tipo == "NOME" and profundidade == 1 and \
                    (not nomes or nomes[-1] != tok.valor):
                if len(nomes) == 0 or self.tokens[self.pos - 2].valor in ("<", ","):
                    nomes.append(tok.valor)
        return nomes

    def parametros(self):
        self.exigir("(")
        saida = []
        while not self.e(")"):
            campo = False
            for modificador in ("public", "private", "protected", "readonly"):
                if self.aceitar(modificador):
                    # 'constructor(private nome: string)' do TypeScript
                    # DECLARA o campo e o atribui. Sem guardar isso, o
                    # campo nunca era criado e 'this.nome' estourava.
                    campo = True
            if self.aceitar("..."):
                nome = self.avancar().valor
                self.anotacao_de_tipo()
                saida.append({"nome": nome, "resto": True, "tipo": None,
                              "padrao": None})
            else:
                alvo = self.alvo_de_declaracao()
                opcional = bool(self.aceitar("?"))
                tipo = self.anotacao_de_tipo()
                padrao = self.expressao_sem_virgula() if self.aceitar("=") else None
                saida.append({"nome": alvo, "resto": False, "tipo": tipo,
                              "padrao": padrao, "opcional": opcional,
                              "campo": campo})
            if not self.aceitar(","):
                break
        self.exigir(")")
        return saida

    # ── classe ──────────────────────────────────────────────

    def classe(self):
        linha = self.atual().linha
        self.exigir("class")
        nome = self.avancar().valor
        self.parametros_de_tipo()
        mae = None
        traits = []
        if self.aceitar("extends"):
            mae = self.referencia_de_tipo()
        if self.aceitar("implements"):
            while True:
                traits.append(self.referencia_de_tipo())
                if not self.aceitar(","):
                    break
        membros = self.corpo_da_classe()
        return {"t": "classe", "nome": nome, "mae": mae, "traits": traits,
                "membros": membros, "linha": linha}

    def corpo_da_classe(self):
        self.exigir("{")
        membros = []
        while not self.e("}") and self.atual().tipo != "FIM":
            if self.aceitar(";"):
                continue
            linha = self.atual().linha
            modificadores = set()
            while self.atual().valor in ("public", "private", "protected",
                                         "static", "readonly", "abstract",
                                         "declare", "async", "get", "set"):
                # 'get'/'set'/'async' só são modificadores se vier nome depois.
                if self.atual().valor in ("get", "set", "async") and \
                        self.olhar().valor in ("(", "=", ";", ":"):
                    break
                modificadores.add(self.avancar().valor)
            gerador = bool(self.aceitar("*"))
            if self.e("#"):
                self.avancar()
                modificadores.add("private")
            nome = self.avancar().valor
            if self.e("<"):
                self.parametros_de_tipo()
            if self.e("("):
                parametros = self.parametros()
                retorno = self.anotacao_de_tipo()
                corpo = self.bloco() if self.e("{") else []
                membros.append({"t": "metodo", "nome": nome,
                                "parametros": parametros, "retorno": retorno,
                                "corpo": corpo, "mods": modificadores,
                                "gerador": gerador, "linha": linha})
            else:
                self.aceitar("?")
                self.aceitar("!")
                tipo = self.anotacao_de_tipo()
                valor = self.expressao() if self.aceitar("=") else None
                self.ponto_e_virgula()
                membros.append({"t": "campo", "nome": nome, "tipo": tipo,
                                "valor": valor, "mods": modificadores,
                                "linha": linha})
        self.exigir("}")
        return membros

    # ── controle ────────────────────────────────────────────

    def se(self):
        linha = self.atual().linha
        self.exigir("if")
        self.exigir("(")
        condicao = self.expressao()
        self.exigir(")")
        corpo = self.corpo_ou_instrucao()
        senao = []
        if self.aceitar("else"):
            senao = [self.se()] if self.e("if") else self.corpo_ou_instrucao()
        return {"t": "se", "condicao": condicao, "corpo": corpo,
                "senao": senao, "linha": linha}

    def para(self):
        linha = self.atual().linha
        self.exigir("for")
        self.aceitar("await")
        self.exigir("(")

        inicio = self.pos
        declara = self.atual().valor in ("let", "const", "var")
        if declara:
            self.avancar()
        if not self.e(";"):
            alvo = self.alvo_de_declaracao() if (
                declara or self.atual().tipo == "NOME") else None
            if alvo is not None and self.atual().valor in ("of", "in"):
                tipo = self.avancar().valor
                fonte = self.expressao()
                self.exigir(")")
                corpo = self.corpo_ou_instrucao()
                return {"t": "para_em", "alvo": alvo, "sobre": tipo,
                        "fonte": fonte, "corpo": corpo, "linha": linha}
        self.pos = inicio

        partida = None
        if not self.e(";"):
            partida = self.instrucao_de_cabecalho()
        self.aceitar(";")
        condicao = None if self.e(";") else self.expressao()
        self.exigir(";")
        passo = None if self.e(")") else self.expressao()
        self.exigir(")")
        corpo = self.corpo_ou_instrucao()
        return {"t": "para", "partida": partida, "condicao": condicao,
                "passo": passo, "corpo": corpo, "linha": linha}

    def instrucao_de_cabecalho(self):
        if self.atual().valor in ("let", "const", "var"):
            return self.declaracao()
        expr = self.expressao()
        return {"t": "expr", "valor": expr, "linha": self.atual().linha}

    def enquanto(self):
        linha = self.atual().linha
        self.exigir("while")
        self.exigir("(")
        condicao = self.expressao()
        self.exigir(")")
        return {"t": "enquanto", "condicao": condicao,
                "corpo": self.corpo_ou_instrucao(), "linha": linha}

    def faca(self):
        linha = self.atual().linha
        self.exigir("do")
        corpo = self.corpo_ou_instrucao()
        self.exigir("while")
        self.exigir("(")
        condicao = self.expressao()
        self.exigir(")")
        self.ponto_e_virgula()
        return {"t": "faca", "condicao": condicao, "corpo": corpo,
                "linha": linha}

    def escolha(self):
        linha = self.atual().linha
        self.exigir("switch")
        self.exigir("(")
        alvo = self.expressao()
        self.exigir(")")
        self.exigir("{")
        casos = []
        while not self.e("}") and self.atual().tipo != "FIM":
            if self.aceitar("case"):
                valor = self.expressao()
                self.exigir(":")
            else:
                self.exigir("default")
                self.exigir(":")
                valor = None
            corpo = []
            while not self.e("case") and not self.e("default") and \
                    not self.e("}") and self.atual().tipo != "FIM":
                corpo.append(self.instrucao())
            casos.append({"valor": valor, "corpo": corpo})
        self.exigir("}")
        return {"t": "escolha", "alvo": alvo, "casos": casos, "linha": linha}

    def tentar(self):
        linha = self.atual().linha
        self.exigir("try")
        corpo = self.bloco()
        nome_do_erro, pegar = None, None
        if self.aceitar("catch"):
            if self.aceitar("("):
                nome_do_erro = self.avancar().valor
                self.anotacao_de_tipo()
                self.exigir(")")
            pegar = self.bloco()
        garantir = self.bloco() if self.aceitar("finally") else None
        return {"t": "tentar", "corpo": corpo, "erro": nome_do_erro,
                "pegar": pegar, "garantir": garantir, "linha": linha}

    def lancar(self):
        linha = self.atual().linha
        self.exigir("throw")
        valor = self.expressao()
        self.ponto_e_virgula()
        return {"t": "lancar", "valor": valor, "linha": linha}

    def retornar(self):
        linha = self.atual().linha
        self.exigir("return")
        valor = None
        if not self.e(";") and not self.e("}") and \
                not self.atual().antes_de_quebra:
            valor = self.expressao()
        self.ponto_e_virgula()
        return {"t": "retorna", "valor": valor, "linha": linha}

    def parar(self):
        linha = self.avancar().linha
        self.ponto_e_virgula()
        return {"t": "parar", "linha": linha}

    def pular(self):
        linha = self.avancar().linha
        self.ponto_e_virgula()
        return {"t": "pular", "linha": linha}

    # ── módulos ─────────────────────────────────────────────

    def importar(self):
        linha = self.atual().linha
        self.exigir("import")
        if self.atual().tipo == "TEXTO":
            caminho = self.avancar().valor
            self.ponto_e_virgula()
            return {"t": "importa", "nomes": [], "padrao": None,
                    "tudo": None, "de": caminho, "linha": linha}
        padrao, nomes, tudo = None, [], None
        if self.atual().tipo in ("NOME", "PALAVRA") and not self.e("{") \
                and not self.e("*"):
            padrao = self.avancar().valor
            self.aceitar(",")
        if self.aceitar("*"):
            self.exigir("as")
            tudo = self.avancar().valor
        elif self.aceitar("{"):
            while not self.e("}"):
                original = self.avancar().valor
                apelido = self.avancar().valor if self.aceitar("as") else original
                nomes.append((original, apelido))
                if not self.aceitar(","):
                    break
            self.exigir("}")
        self.exigir("from")
        caminho = self.avancar().valor
        self.ponto_e_virgula()
        return {"t": "importa", "nomes": nomes, "padrao": padrao,
                "tudo": tudo, "de": caminho, "linha": linha}

    def exportar(self):
        linha = self.atual().linha
        self.exigir("export")
        if self.aceitar("default"):
            alvo = self.instrucao()
            return {"t": "exporta", "alvo": alvo, "nomes": None,
                    "padrao": True, "linha": linha}
        if self.e("{"):
            self.avancar()
            nomes = []
            while not self.e("}"):
                original = self.avancar().valor
                apelido = self.avancar().valor if self.aceitar("as") else original
                nomes.append((original, apelido))
                if not self.aceitar(","):
                    break
            self.exigir("}")
            if self.aceitar("from"):
                self.avancar()
            self.ponto_e_virgula()
            return {"t": "exporta", "alvo": None, "nomes": nomes,
                    "padrao": False, "linha": linha}
        return {"t": "exporta", "alvo": self.instrucao(), "nomes": None,
                "padrao": False, "linha": linha}

    # ── só do TypeScript ────────────────────────────────────

    def interface(self):
        linha = self.atual().linha
        self.exigir("interface")
        nome = self.avancar().valor
        self.parametros_de_tipo()
        maes = []
        if self.aceitar("extends"):
            while True:
                maes.append(self.texto_de_tipo())
                if not self.aceitar(","):
                    break
        self.exigir("{")
        membros = []
        while not self.e("}") and self.atual().tipo != "FIM":
            if self.aceitar(";") or self.aceitar(","):
                continue
            for m in ("readonly", "public"):
                self.aceitar(m)
            nome_do_membro = self.avancar().valor
            self.aceitar("?")
            if self.e("("):
                parametros = self.parametros()
                retorno = self.anotacao_de_tipo()
                membros.append({"t": "metodo", "nome": nome_do_membro,
                                "parametros": parametros, "retorno": retorno})
            else:
                membros.append({"t": "campo", "nome": nome_do_membro,
                                "tipo": self.anotacao_de_tipo()})
        self.exigir("}")
        return {"t": "interface", "nome": nome, "maes": maes,
                "membros": membros, "linha": linha}

    def tipo_alias(self):
        linha = self.atual().linha
        self.exigir("type")
        nome = self.avancar().valor
        self.parametros_de_tipo()
        self.exigir("=")
        texto = self.texto_de_tipo()
        self.ponto_e_virgula()
        return {"t": "tipo_alias", "nome": nome, "texto": texto,
                "linha": linha}

    def enumeracao(self):
        linha = self.atual().linha
        self.exigir("enum")
        nome = self.avancar().valor
        self.exigir("{")
        membros = []
        while not self.e("}") and self.atual().tipo != "FIM":
            chave = self.avancar().valor
            valor = self.expressao_sem_virgula() if self.aceitar("=") else None
            membros.append((chave, valor))
            if not self.aceitar(","):
                break
        self.exigir("}")
        return {"t": "enum", "nome": nome, "membros": membros, "linha": linha}

    # ── expressões ──────────────────────────────────────────
    #
    # Descida recursiva pela precedência do JavaScript, do mais fraco
    # para o mais forte. Cada nível chama o de baixo e só monta um nó se
    # o operador daquele nível aparecer.

    def expressao(self):
        """Inclui o operador vírgula: `a = 1, b = 2`."""
        primeiro = self.expressao_sem_virgula()
        if not self.e(","):
            return primeiro
        itens = [primeiro]
        while self.aceitar(","):
            itens.append(self.expressao_sem_virgula())
        return {"t": "sequencia", "itens": itens}

    def expressao_sem_virgula(self):
        return self.atribuicao()

    def atribuicao(self):
        seta = self.talvez_seta()
        if seta is not None:
            return seta

        esquerda = self.ternaria()
        tok = self.atual()
        if tok.tipo == "OP" and tok.valor in (
                "=", "+=", "-=", "*=", "/=", "%=", "**=", "&&=", "||=",
                "??=", "&=", "|=", "^=", "<<=", ">>=", ">>>="):
            op = self.avancar().valor
            return {"t": "atribui", "alvo": esquerda, "op": op,
                    "valor": self.atribuicao()}
        return esquerda

    def talvez_seta(self):
        """`x => …`, `(a, b) => …`, `async (a) => …`.

        Exige espiar adiante: `(a)` sozinho é um parêntese comum, e só a
        `=>` depois do fecha-parênteses o torna uma função.
        """
        inicio = self.pos
        assincrona = False
        if self.e("async") and not self.olhar().antes_de_quebra and \
                (self.olhar().valor == "(" or self.olhar().tipo == "NOME"):
            assincrona = True
            self.avancar()

        if self.atual().tipo == "NOME" and self.olhar().valor == "=>":
            parametros = [{"nome": {"t": "nome", "valor": self.avancar().valor},
                           "resto": False, "tipo": None, "padrao": None}]
        elif self.e("(") and self._fecha_com_seta():
            parametros = self.parametros()
            self.anotacao_de_tipo()
        else:
            self.pos = inicio
            return None

        if not self.aceitar("=>"):
            self.pos = inicio
            return None

        if self.e("{"):
            corpo, expr = self.bloco(), None
        else:
            corpo, expr = None, self.expressao_sem_virgula()
        return {"t": "seta", "parametros": parametros, "corpo": corpo,
                "expr": expr, "assincrona": assincrona}

    def _fecha_com_seta(self):
        """O ')' que fecha este '(' é seguido de '=>'?"""
        profundidade, i = 0, self.pos
        while i < len(self.tokens):
            valor = self.tokens[i].valor
            if valor in ("(", "[", "{"):
                profundidade += 1
            elif valor in (")", "]", "}"):
                profundidade -= 1
                if profundidade == 0:
                    j = i + 1
                    # pula uma anotação de retorno: '(a): number => …'
                    if self.tokens[j].valor == ":":
                        while j < len(self.tokens) and \
                                self.tokens[j].valor != "=>":
                            if self.tokens[j].valor in (";", "{"):
                                return False
                            j += 1
                    return self.tokens[j].valor == "=>"
            elif self.tokens[i].tipo == "FIM":
                return False
            i += 1
        return False

    def ternaria(self):
        condicao = self.binaria(0)
        if not self.aceitar("?"):
            return condicao
        entao = self.expressao_sem_virgula()
        self.exigir(":")
        senao = self.expressao_sem_virgula()
        return {"t": "ternaria", "condicao": condicao, "entao": entao,
                "senao": senao}

    #: Um nível por linha, do mais fraco para o mais forte.
    NIVEIS = [
        ("??",), ("||",), ("&&",), ("|",), ("^",), ("&",),
        ("===", "!==", "==", "!="),
        ("<", ">", "<=", ">=", "instanceof", "in"),
        ("<<", ">>", ">>>"),
        ("+", "-"), ("*", "/", "%"),
    ]

    def binaria(self, nivel):
        if nivel >= len(self.NIVEIS):
            return self.potencia()
        esquerda = self.binaria(nivel + 1)
        while self.atual().valor in self.NIVEIS[nivel] and \
                self.atual().tipo in ("OP", "PALAVRA"):
            op = self.avancar().valor
            direita = self.binaria(nivel + 1)
            esquerda = {"t": "binaria", "op": op, "esquerda": esquerda,
                        "direita": direita}
        return esquerda

    def potencia(self):
        base = self.unaria()
        if self.e("**"):
            self.avancar()
            return {"t": "binaria", "op": "**", "esquerda": base,
                    "direita": self.potencia()}
        return base

    def unaria(self):
        tok = self.atual()
        if tok.valor in ("!", "-", "+", "~", "typeof", "void", "delete",
                         "await") and tok.tipo in ("OP", "PALAVRA"):
            op = self.avancar().valor
            return {"t": "unaria", "op": op, "valor": self.unaria()}
        if tok.valor in ("++", "--"):
            op = self.avancar().valor
            return {"t": "passo", "op": op, "alvo": self.unaria(),
                    "prefixo": True}
        return self.posfixo()

    def posfixo(self):
        alvo = self.chamada()
        while self.atual().valor in ("++", "--") and \
                not self.atual().antes_de_quebra:
            op = self.avancar().valor
            alvo = {"t": "passo", "op": op, "alvo": alvo, "prefixo": False}
        return alvo

    def chamada(self):
        if self.e("new"):
            self.avancar()
            alvo = self.primaria()
            while self.e("."):
                self.avancar()
                alvo = {"t": "membro", "objeto": alvo,
                        "nome": self.avancar().valor, "seguro": False}
            argumentos = self.argumentos() if self.e("(") else []
            valor = {"t": "novo", "alvo": alvo, "args": argumentos}
        else:
            valor = self.primaria()

        while True:
            if self.e("."):
                self.avancar()
                valor = {"t": "membro", "objeto": valor,
                         "nome": self.avancar().valor, "seguro": False}
            elif self.e("?."):
                self.avancar()
                if self.e("("):
                    valor = {"t": "chama", "alvo": valor,
                             "args": self.argumentos(), "seguro": True}
                else:
                    valor = {"t": "membro", "objeto": valor,
                             "nome": self.avancar().valor, "seguro": True}
            elif self.e("["):
                self.avancar()
                indice = self.expressao()
                self.exigir("]")
                valor = {"t": "indice", "objeto": valor, "indice": indice}
            elif self.e("("):
                valor = {"t": "chama", "alvo": valor,
                         "args": self.argumentos(), "seguro": False}
            elif self.atual().tipo == "TEMPLATE" and \
                    valor.get("t") in ("nome", "membro"):
                # Template marcado (`sql\`…\``): não há equivalente.
                self.avancar()
                valor = {"t": "cru", "texto": "template marcado",
                         "linha": self.atual().linha}
            elif self.e("!") and not self.atual().antes_de_quebra:
                self.avancar()          # o '!' do TS: 'x!.y' — só some
            elif self.e("as"):
                self.avancar()
                self.texto_de_tipo()    # 'x as T' — o tipo some
            else:
                return valor

    def argumentos(self):
        self.exigir("(")
        saida = []
        while not self.e(")"):
            if self.aceitar("..."):
                saida.append({"t": "espalha",
                              "valor": self.expressao_sem_virgula()})
            else:
                saida.append(self.expressao_sem_virgula())
            if not self.aceitar(","):
                break
        self.exigir(")")
        return saida

    def primaria(self):
        tok = self.atual()

        if tok.tipo == "NUMERO":
            return {"t": "numero", "valor": self.avancar().valor}
        if tok.tipo == "TEXTO":
            return {"t": "texto", "valor": self.avancar().valor}
        if tok.tipo == "TEMPLATE":
            return {"t": "template", "partes": self.avancar().valor}
        if tok.tipo == "REGEX":
            return {"t": "regex", "valor": self.avancar().valor}

        if tok.valor == "(":
            self.avancar()
            dentro = self.expressao()
            self.exigir(")")
            return {"t": "grupo", "valor": dentro}

        if tok.valor == "[":
            self.avancar()
            itens = []
            while not self.e("]"):
                if self.aceitar("..."):
                    itens.append({"t": "espalha",
                                  "valor": self.expressao_sem_virgula()})
                else:
                    itens.append(self.expressao_sem_virgula())
                if not self.aceitar(","):
                    break
            self.exigir("]")
            return {"t": "lista", "itens": itens}

        if tok.valor == "{":
            return self.objeto()

        if tok.valor == "function":
            return self.funcao()
        if tok.valor == "class":
            return self.classe()
        if tok.valor in ("this", "super"):
            return {"t": "nome", "valor": self.avancar().valor}
        if tok.valor in ("true", "false", "null", "undefined"):
            return {"t": "constante", "valor": self.avancar().valor}

        if tok.tipo in ("NOME", "PALAVRA"):
            valor = self.avancar().valor
            if valor in ("true", "false", "null", "undefined"):
                return {"t": "constante", "valor": valor}
            return {"t": "nome", "valor": valor}

        raise ErroDeLeitura(f"expressão inesperada: {tok.valor!r}", tok.linha)

    def objeto(self):
        linha = self.atual().linha
        self.exigir("{")
        campos = []
        while not self.e("}") and self.atual().tipo != "FIM":
            if self.aceitar("..."):
                campos.append({"espalha": True,
                               "valor": self.expressao_sem_virgula()})
            elif self.e("[") :
                self.avancar()
                chave = self.expressao()
                self.exigir("]")
                self.exigir(":")
                campos.append({"espalha": False, "chave": chave,
                               "calculada": True,
                               "valor": self.expressao_sem_virgula()})
            else:
                tok = self.avancar()
                chave = tok.valor
                if self.e("("):
                    parametros = self.parametros()
                    self.anotacao_de_tipo()
                    corpo = self.bloco()
                    campos.append({"espalha": False, "chave": chave,
                                   "calculada": False,
                                   "valor": {"t": "seta",
                                             "parametros": parametros,
                                             "corpo": corpo, "expr": None,
                                             "assincrona": False}})
                elif self.aceitar(":"):
                    campos.append({"espalha": False, "chave": chave,
                                   "calculada": False,
                                   "valor": self.expressao_sem_virgula()})
                else:
                    campos.append({"espalha": False, "chave": chave,
                                   "calculada": False,
                                   "valor": {"t": "nome", "valor": chave}})
            if not self.aceitar(","):
                break
        self.exigir("}")
        return {"t": "objeto", "campos": campos, "linha": linha}


def analisar(fonte, arquivo="<js>"):
    """O texto vira a lista de instruções. Levanta `ErroDeLeitura`."""
    return Parser(tokenizar(fonte), fonte).programa()


# ═════════════════════════════════════════════════════════════
#  Emissor
# ═════════════════════════════════════════════════════════════

class Emissor:
    """A árvore vira DataForge.

    Duas regras governam tudo aqui:

    1. **Nada é traduzido por aproximação.** Quando não há equivalente,
       sai um `TODO(converter)` com o código original ao lado — e a
       linha entra em `pendencias`, que o relatório conta.
    2. **A saída tem de compilar.** Uma pendência é um comentário, e um
       comentário sempre compila. É por isso que o modo de falhar deste
       arquivo é "faltou traduzir", e nunca "gerou algo quebrado".
    """

    def __init__(self, fonte="", arquivo="<js>"):
        self.saida = []
        self.pendencias = []
        self.nivel = 0
        self.linhas = fonte.splitlines()
        self.arquivo = arquivo
        self.reservadas = _reservadas()
        self.auxiliares = []        # ações extraídas de setas com bloco
        self.contador = 0
        self.em_metodo = False

    # ── utilidades ──────────────────────────────────────────

    def escrever(self, texto=""):
        self.saida.append(("    " * self.nivel + texto).rstrip())

    def pendente(self, no, motivo):
        linha = no.get("linha", 0) if isinstance(no, dict) else 0
        original = ""
        if 0 < linha <= len(self.linhas):
            original = self.linhas[linha - 1].strip()
        self.pendencias.append((linha, motivo))
        self.escrever(f"// TODO(converter): {motivo}")
        if original:
            self.escrever(f"//   {original}")

    def nome(self, texto):
        """Um nome do JS que colide com palavra reservada ganha sufixo."""
        if texto == "this":
            return "self"
        if texto == "super":
            return "root"
        if texto in self.reservadas:
            return texto + "_"
        # '$' e nomes com '$' não são válidos aqui.
        return texto.replace("$", "_")

    def tipo(self, texto):
        """`number` vira `Float`; o que não estiver na tabela, some."""
        if not texto:
            return None
        limpo = texto.strip().rstrip("[]").split("<")[0].split("|")[0].strip()
        if texto.strip().endswith("[]") or texto.strip().startswith("Array"):
            return "Cluster"
        return TIPOS.get(limpo)

    def nova_auxiliar(self, base="corpo"):
        self.contador += 1
        return f"_{base}_{self.contador}"

    # ── programa ────────────────────────────────────────────

    def programa(self, corpo):
        for no in corpo:
            self.instrucao(no)
        if self.auxiliares:
            self.saida = self.auxiliares + [""] + self.saida

    def bloco(self, corpo, vazio="pass"):
        """Um bloco indentado. Um corpo vazio recebe um marcador, porque
        a DataForge exige ao menos uma instrução depois do ':'."""
        self.nivel += 1
        if not corpo:
            self.escrever("// (vazio)")
            self.escrever("void")
        else:
            for no in corpo:
                self.instrucao(no)
        self.nivel -= 1

    # ── instruções ──────────────────────────────────────────

    def instrucao(self, no):
        metodo = getattr(self, "st_" + no["t"], None)
        if metodo is None:
            self.pendente(no, f"instrução '{no['t']}' não traduzida")
            return
        metodo(no)

    def st_vazio(self, no):
        pass

    def st_bloco(self, no):
        for dentro in no["corpo"]:
            self.instrucao(dentro)

    def st_expr(self, no):
        valor = no["valor"]
        if valor["t"] == "passo":
            alvo = self.expr(valor["alvo"])
            self.escrever(f"{alvo} {'+=' if valor['op'] == '++' else '-='} 1")
            return
        if valor["t"] == "chama" and self._e_saida(valor["alvo"]):
            args = ", ".join(self.expr(a) for a in valor["args"])
            self.escrever(f"out {args}" if args else 'out ""')
            return
        self.escrever(self.expr(valor))

    def _e_saida(self, alvo):
        return (alvo["t"] == "membro" and alvo["objeto"].get("valor") == "console"
                and alvo["nome"] in ("log", "info", "debug"))

    def st_declara(self, no):
        for item in no["itens"]:
            alvo, valor = item["alvo"], item["valor"]
            if alvo["t"] == "padrao_lista":
                nomes = []
                for parte in alvo["nomes"]:
                    if parte is None:
                        nomes.append("_")
                    elif parte["resto"]:
                        nomes.append("..." + self.nome(parte["nome"]))
                    else:
                        nomes.append(self.nome(parte["nome"]))
                texto = ", ".join(nomes)
                self.escrever(f"{texto} := {self.expr(valor)}")
                continue
            if alvo["t"] == "padrao_vault":
                origem = self.expr(valor)
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", origem):
                    temporario = self.nova_auxiliar("dados")
                    self.escrever(f"{temporario} := {origem}")
                    origem = temporario
                for campo in alvo["campos"]:
                    if campo["resto"]:
                        self.pendente(
                            no, "resto de um vault desestruturado não tem "
                                "equivalente direto")
                        continue
                    self.escrever(
                        f'{self.nome(campo["nome"])} := {origem}["{campo["chave"]}"]')
                continue

            nome = self.nome(alvo["valor"])
            anotacao = self.tipo(item["tipo"])
            marca = "steady " if no["fixo"] else ""
            if valor is None:
                self.escrever(f"{marca}{nome}: {anotacao} := void"
                              if anotacao else f"{marca}{nome} := void")
                continue
            texto = self.expr(valor)
            if anotacao:
                self.escrever(f"{marca}{nome}: {anotacao} := {texto}")
            else:
                self.escrever(f"{marca}{nome} := {texto}")

    def st_acao(self, no, dentro_de_classe=False):
        nome = self.nome(no["nome"]) if no["nome"] else self.nova_auxiliar("acao")
        cabecalho = "stream action " if no.get("gerador") else "action "
        if no.get("assincrona"):
            cabecalho = "async " + cabecalho
        retorno = self.tipo(no.get("retorno"))
        assinatura = f"{cabecalho}{nome}({self.parametros(no['parametros'])})"
        if retorno and retorno != "Void":
            assinatura += f" -> {retorno}"
        self.escrever(assinatura + ":")
        self.bloco(no["corpo"])
        self.escrever()

    def parametros(self, parametros):
        saida = []
        for p in parametros:
            alvo = p["nome"]
            if isinstance(alvo, dict) and alvo.get("t") != "nome":
                saida.append(self.nova_auxiliar("arg"))
                continue
            nome = self.nome(alvo["valor"] if isinstance(alvo, dict) else alvo)
            if p.get("resto"):
                nome = "..." + nome
            anotacao = self.tipo(p.get("tipo"))
            if anotacao:
                nome += f": {anotacao}"
            if p.get("padrao") is not None:
                nome += f" := {self.expr(p['padrao'])}"
            elif p.get("opcional"):
                nome += " := void"
            saida.append(nome)
        return ", ".join(saida)

    def st_classe(self, no):
        cabecalho = f"blueprint {self.nome(no['nome'])}"
        construtor = next((m for m in no["membros"]
                           if m["t"] == "metodo" and m["nome"] == "constructor"),
                          None)
        if no["mae"]:
            cabecalho += f" extends {self.nome(no['mae'].split('<')[0].strip())}"
        if no["traits"]:
            nomes = ", ".join(self.nome(t.split("<")[0].strip())
                              for t in no["traits"])
            cabecalho += f" with {nomes}"
        self.escrever(cabecalho + ":")
        self.nivel += 1

        campos = [m for m in no["membros"] if m["t"] == "campo"]
        for campo in campos:
            anotacao = self.tipo(campo["tipo"])
            nome = self.nome(campo["nome"])
            if campo["valor"] is not None:
                texto = f"{nome}: {anotacao} := {self.expr(campo['valor'])}" \
                    if anotacao else f"{nome} := {self.expr(campo['valor'])}"
                self.escrever(texto)
            elif anotacao:
                self.escrever(f"{nome}: {anotacao} := void")

        metodos = [m for m in no["membros"] if m["t"] == "metodo"]
        if not metodos and not campos:
            self.escrever("// (sem membros)")
            self.escrever("void")
        anterior = self.em_metodo
        self.em_metodo = True
        for metodo in metodos:
            self.metodo(metodo, construtor)
        self.em_metodo = anterior
        self.nivel -= 1
        self.escrever()

    def metodo(self, metodo, construtor):
        nome = "setup" if metodo["nome"] == "constructor" else self.nome(metodo["nome"])
        # 'static' e um PREFIXO da declaracao, nao uma linha propria.
        estatico = "static " if "static" in metodo["mods"] else ""
        if "get" in metodo["mods"]:
            self.escrever(f"get {nome}():")
            self.bloco(metodo["corpo"])
            self.escrever()
            return
        if "set" in metodo["mods"]:
            valor = self.parametros(metodo["parametros"]) or "valor"
            self.escrever(f"set {nome}({valor}):")
            self.bloco(metodo["corpo"])
            self.escrever()
            return
        cabecalho = "stream action " if metodo.get("gerador") else "action "
        if "async" in metodo["mods"]:
            cabecalho = "async " + cabecalho
        cabecalho = estatico + cabecalho
        retorno = self.tipo(metodo.get("retorno"))
        assinatura = f"{cabecalho}{nome}({self.parametros(metodo['parametros'])})"
        if retorno and retorno != "Void":
            assinatura += f" -> {retorno}"
        self.escrever(assinatura + ":")
        propriedades = [p for p in metodo["parametros"] if p.get("campo")]
        if propriedades:
            self.nivel += 1
            for p in propriedades:
                alvo = p["nome"]
                bruto = alvo["valor"] if isinstance(alvo, dict) else alvo
                self.escrever(f"self.{self.nome(bruto)} := {self.nome(bruto)}")
            self.nivel -= 1
        self.bloco(metodo["corpo"])
        self.escrever()

    def st_se(self, no):
        self.escrever(f"given {self.expr(no['condicao'])}:")
        self.bloco(no["corpo"])
        senao = no["senao"]
        while senao:
            if len(senao) == 1 and senao[0]["t"] == "se":
                dentro = senao[0]
                self.escrever(f"orif {self.expr(dentro['condicao'])}:")
                self.bloco(dentro["corpo"])
                senao = dentro["senao"]
                continue
            self.escrever("otherwise:")
            self.bloco(senao)
            break

    def st_para_em(self, no):
        alvo = no["alvo"]
        if alvo["t"] == "nome":
            nome = self.nome(alvo["valor"])
        elif alvo["t"] == "padrao_lista":
            nome = ", ".join(self.nome(p["nome"]) for p in alvo["nomes"] if p)
        else:
            nome = self.nova_auxiliar("item")
        fonte = self.expr(no["fonte"])
        if no["sobre"] == "in":
            fonte = f"keys({fonte})"
        self.escrever(f"cycle {nome} in {fonte}:")
        self.bloco(no["corpo"])

    def st_para(self, no):
        contado = self._contado(no)
        if contado:
            self.escrever(contado)
            self.bloco(no["corpo"])
            return
        if no["partida"] is not None:
            self.instrucao(no["partida"])
        condicao = self.expr(no["condicao"]) if no["condicao"] else "yes"
        self.escrever(f"persist {condicao}:")
        self.nivel += 1
        if not no["corpo"] and no["passo"] is None:
            self.escrever("void")
        for dentro in no["corpo"]:
            self.instrucao(dentro)
        if no["passo"] is not None:
            self.instrucao({"t": "expr", "valor": no["passo"],
                            "linha": no["linha"]})
        self.nivel -= 1

    def _contado(self, no):
        """`for (let i = 0; i < n; i++)` vira `cycle i from 0 to n - 1`.

        Só quando as três partes casam exatamente. Qualquer variação cai
        no `persist`, que é sempre correto — inventar um `cycle` a partir
        de um cabeçalho parecido trocaria o número de voltas em silêncio.
        """
        partida, condicao, passo = no["partida"], no["condicao"], no["passo"]
        if not (partida and condicao and passo):
            return None
        if partida["t"] != "declara" or len(partida["itens"]) != 1:
            return None
        item = partida["itens"][0]
        if item["alvo"]["t"] != "nome" or item["valor"] is None:
            return None
        nome = self.nome(item["alvo"]["valor"])
        if passo.get("t") != "passo" or passo["op"] != "++":
            return None
        if passo["alvo"].get("valor") != item["alvo"]["valor"]:
            return None
        if condicao.get("t") != "binaria" or \
                condicao["esquerda"].get("valor") != item["alvo"]["valor"]:
            return None
        inicio = self.expr(item["valor"])
        limite = self.expr(condicao["direita"])
        if condicao["op"] == "<":
            # 'to 3 - 1' esta certo e se le mal. Quando o limite e um
            # numero, a conta e feita aqui.
            if re.fullmatch(r"\d+", limite):
                return f"cycle {nome} from {inicio} to {int(limite) - 1}:"
            return f"cycle {nome} from {inicio} to {limite} - 1:"
        if condicao["op"] == "<=":
            return f"cycle {nome} from {inicio} to {limite}:"
        return None

    def st_enquanto(self, no):
        self.escrever(f"persist {self.expr(no['condicao'])}:")
        self.bloco(no["corpo"])

    def st_faca(self, no):
        self.escrever("perform:")
        self.bloco(no["corpo"])
        self.escrever(f"persist {self.expr(no['condicao'])}")

    def st_escolha(self, no):
        self.escrever(f"match {self.expr(no['alvo'])}:")
        self.nivel += 1
        for caso in no["casos"]:
            corpo = [i for i in caso["corpo"] if i["t"] != "parar"]
            if caso["valor"] is None:
                self.escrever("default:")
            else:
                self.escrever(f"point {self.expr(caso['valor'])}:")
            self.bloco(corpo)
        self.nivel -= 1

    def st_tentar(self, no):
        self.escrever("monitor:")
        self.bloco(no["corpo"])
        if no["pegar"] is not None:
            nome = self.nome(no["erro"]) if no["erro"] else "erro"
            self.escrever(f"handle Error as {nome}:")
            self.bloco(no["pegar"])
        if no["garantir"] is not None:
            self.escrever("ensure:")
            self.bloco(no["garantir"])

    def st_lancar(self, no):
        valor = no["valor"]
        if valor["t"] == "novo":
            args = ", ".join(self.expr(a) for a in valor["args"])
            self.escrever(f"trigger {args}" if args else 'trigger "erro"')
            return
        self.escrever(f"trigger {self.expr(valor)}")

    def st_retorna(self, no):
        if no["valor"] is None:
            self.escrever("yield void")
        else:
            self.escrever(f"yield {self.expr(no['valor'])}")

    def st_parar(self, no):
        self.escrever("halt")

    def st_pular(self, no):
        self.escrever("skip")

    def st_importa(self, no):
        caminho = no["de"]
        if caminho.startswith("."):
            caminho = re.sub(r"\.(js|ts|mjs|cjs|jsx|tsx)$", "", caminho)
        else:
            caminho = "Python." + caminho if "/" not in caminho else caminho
        if no["tudo"]:
            self.escrever(f"adopt {caminho} as {self.nome(no['tudo'])}")
        elif no["nomes"]:
            partes = ", ".join(
                self.nome(o) if o == a else f"{self.nome(o)} as {self.nome(a)}"
                for o, a in no["nomes"])
            self.escrever(f"adopt {{{partes}}} from {caminho}")
        elif no["padrao"]:
            self.escrever(f"adopt {caminho} as {self.nome(no['padrao'])}")
        else:
            self.escrever(f"adopt {caminho}")

    def st_exporta(self, no):
        if no["nomes"] is not None:
            nomes = ", ".join(self.nome(o) for o, _ in no["nomes"])
            self.escrever(f"relay {nomes}")
            return
        alvo = no["alvo"]
        self.instrucao(alvo)
        nome = ""
        if alvo["t"] in ("acao", "classe"):
            nome = alvo.get("nome", "")
        elif alvo["t"] == "declara" and alvo["itens"]:
            primeiro = alvo["itens"][0]["alvo"]
            nome = primeiro.get("valor", "") if primeiro["t"] == "nome" else ""
        if nome:
            self.escrever(f"relay {self.nome(nome)}")

    def st_interface(self, no):
        """`interface` vira `trait`: é o contrato sem implementação."""
        self.escrever(f"trait {self.nome(no['nome'])}:")
        self.nivel += 1
        metodos = [m for m in no["membros"] if m["t"] == "metodo"]
        campos = [m for m in no["membros"] if m["t"] == "campo"]
        for campo in campos:
            self.escrever(f"// campo '{campo['nome']}'"
                          + (f": {self.tipo(campo['tipo']) or campo['tipo']}"
                             if campo["tipo"] else ""))
        for metodo in metodos:
            self.escrever(f"action {self.nome(metodo['nome'])}"
                          f"({self.parametros(metodo['parametros'])})")
        if not metodos:
            self.escrever("// um trait sem método não exige nada")
            self.escrever("void")
        self.nivel -= 1
        self.escrever()

    def st_tipo_alias(self, no):
        self.escrever(f"// type {no['nome']} = {no['texto']}")
        self.escrever(f"//   (a DataForge não tem apelido de tipo; "
                      f"use o tipo direto, ou um record)")

    def st_enum(self, no):
        self.escrever(f"enum {self.nome(no['nome'])}:")
        self.nivel += 1
        if not no["membros"]:
            self.escrever("void")
        for chave, valor in no["membros"]:
            if valor is None:
                self.escrever(self.nome(chave))
            else:
                self.escrever(f"{self.nome(chave)} := {self.expr(valor)}")
        self.nivel -= 1
        self.escrever()

    # ── expressões ──────────────────────────────────────────

    def expr(self, no):
        if no is None:
            return "void"
        metodo = getattr(self, "ex_" + no["t"], None)
        if metodo is None:
            self.pendencias.append((no.get("linha", 0),
                                    f"expressão '{no['t']}' não traduzida"))
            return f'void  // TODO(converter): {no["t"]}'
        return metodo(no)

    def ex_numero(self, no):
        texto = no["valor"].replace("_", "").rstrip("n")
        return texto

    def ex_texto(self, no):
        corpo = no["valor"].replace('\\"', '"').replace("\\'", "'")
        return '"' + corpo.replace('"', '\\"') + '"'

    def ex_constante(self, no):
        return {"true": "yes", "false": "no",
                "null": "void", "undefined": "void"}[no["valor"]]

    def ex_nome(self, no):
        return self.nome(no["valor"])

    def ex_grupo(self, no):
        return f"({self.expr(no['valor'])})"

    def ex_sequencia(self, no):
        return self.expr(no["itens"][-1])

    def ex_template(self, no):
        """`` `oi ${nome}` `` vira `$"oi {nome}"`."""
        fora = []
        for tipo, valor in no["partes"]:
            if tipo == "texto":
                fora.append(valor.replace("\\`", "`").replace('"', '\\"'))
            else:
                try:
                    dentro = Parser(tokenizar(valor), valor).expressao()
                    fora.append("{" + self.expr(dentro) + "}")
                except ErroDeLeitura:
                    fora.append("{" + valor.strip() + "}")
        return '$"' + "".join(fora) + '"'

    def ex_regex(self, no):
        corpo = no["valor"].rsplit("/", 1)[0][1:]
        return 'r"' + corpo.replace('"', '\\"') + '"'

    def ex_lista(self, no):
        return "[" + ", ".join(self.expr(i) for i in no["itens"]) + "]"

    def ex_espalha(self, no):
        return "..." + self.expr(no["valor"])

    def ex_objeto(self, no):
        partes = []
        for campo in no["campos"]:
            if campo.get("espalha"):
                partes.append("..." + self.expr(campo["valor"]))
            elif campo.get("calculada"):
                partes.append(f"{self.expr(campo['chave'])}: "
                              f"{self.expr(campo['valor'])}")
            else:
                chave = campo["chave"]
                if not (chave.startswith('"') or chave.startswith("'")):
                    chave = f'"{chave}"'
                else:
                    chave = f'"{chave.strip(chr(34) + chr(39))}"'
                partes.append(f"{chave}: {self.expr(campo['valor'])}")
        return "{" + ", ".join(partes) + "}"

    def ex_binaria(self, no):
        op = no["op"]
        esquerda = self.expr(no["esquerda"])
        direita = self.expr(no["direita"])
        if op in _COMPARACAO:
            return f"{esquerda} {_COMPARACAO[op]} {direita}"
        if op == "instanceof":
            return f'e_um({esquerda}, "{direita}")'
        if op == "in":
            return f"{esquerda} in keys({direita})"
        if op in (">>>", "<<", ">>", "&", "|", "^"):
            return f"{esquerda} {op} {direita}"
        return f"{esquerda} {op} {direita}"

    def ex_unaria(self, no):
        op, valor = no["op"], self.expr(no["valor"])
        if op == "!":
            return f"not {valor}"
        if op == "typeof":
            return f"typeof {valor}"
        if op == "await":
            return f"await {valor}"
        if op in ("void", "delete"):
            self.pendencias.append((no.get("linha", 0),
                                    f"'{op}' não tem equivalente"))
            return f"void  // TODO(converter): {op} {valor}"
        return f"{op}{valor}"

    def ex_passo(self, no):
        alvo = self.expr(no["alvo"])
        return f"({alvo} + 1)" if no["op"] == "++" else f"({alvo} - 1)"

    def ex_ternaria(self, no):
        return (f"{self.expr(no['entao'])} given {self.expr(no['condicao'])} "
                f"otherwise {self.expr(no['senao'])}")

    def ex_atribui(self, no):
        alvo = self.expr(no["alvo"])
        valor = self.expr(no["valor"])
        op = no["op"]
        if op == "=":
            return f"{alvo} := {valor}"
        if op in ("&&=", "||=", "??="):
            ligacao = {"&&=": "and", "||=": "or", "??=": "??"}[op]
            if op == "??=":
                return f"{alvo} := {alvo} ?? {valor}"
            return f"{alvo} := {alvo} {ligacao} {valor}"
        return f"{alvo} {op} {valor}"

    def ex_membro(self, no):
        objeto = no["objeto"]
        caminho = self._caminho(no)
        if caminho in _GLOBAIS:
            return _GLOBAIS[caminho]
        alvo = self.expr(objeto)
        nome = no["nome"]
        if nome == "length":
            return f"len({alvo})"
        ponto = "?." if no.get("seguro") else "."
        return f"{alvo}{ponto}{_METODOS.get(nome, self.nome(nome))}"

    def _caminho(self, no):
        """'Math.floor' como texto, para procurar na tabela de globais."""
        if no["t"] == "nome":
            return no["valor"]
        if no["t"] == "membro":
            base = self._caminho(no["objeto"])
            return f"{base}.{no['nome']}" if base else ""
        return ""

    def ex_indice(self, no):
        return f"{self.expr(no['objeto'])}[{self.expr(no['indice'])}]"

    def ex_chama(self, no):
        alvo = no["alvo"]
        caminho = self._caminho(alvo)
        args = [self.expr(a) for a in no["args"]]

        if caminho in _GLOBAIS:
            return f"{_GLOBAIS[caminho]}({', '.join(args)})"
        if caminho == "Array.isArray":
            return f'typeof({args[0]}) is "Cluster"'
        if caminho.endswith(".join") and args:
            return f"join({args[0]}, {self.expr(alvo['objeto'])})"

        texto = self.expr(alvo)
        return f"{texto}({', '.join(args)})"

    def ex_novo(self, no):
        alvo = self._caminho(no["alvo"])
        args = ", ".join(self.expr(a) for a in no["args"])
        if alvo in ("Error", "TypeError", "RangeError", "SyntaxError"):
            return args or '"erro"'
        if alvo == "Map":
            return "{}"
        if alvo in ("Set", "Array"):
            return f"[{args}]" if args else "[]"
        if alvo == "Date":
            return "Time.now()"
        return f"spawn {self.nome(alvo)}({args})"

    def ex_seta(self, no):
        """A seta com **expressão** vira `lambda`; com **bloco**, uma ação
        nomeada acima — o `lambda` da DataForge é uma expressão só."""
        parametros = self.parametros(no["parametros"])
        if no["expr"] is not None:
            corpo = self.expr(no["expr"])
            return f"lambda {parametros}: {corpo}" if parametros \
                else f"lambda: {corpo}"

        nome = self.nova_auxiliar("acao")
        guardado, nivel = self.saida, self.nivel
        self.saida, self.nivel = [], 0
        cabecalho = "async action " if no.get("assincrona") else "action "
        self.escrever(f"{cabecalho}{nome}({parametros}):")
        self.bloco(no["corpo"])
        self.auxiliares.extend(self.saida)
        self.auxiliares.append("")
        self.saida, self.nivel = guardado, nivel
        return nome

    def ex_acao(self, no):
        """Uma `function` usada como valor: mesma saída da seta com bloco."""
        return self.ex_seta({"parametros": no["parametros"],
                             "corpo": no["corpo"], "expr": None,
                             "assincrona": no.get("assincrona", False)})

    def ex_cru(self, no):
        self.pendencias.append((no.get("linha", 0), no.get("texto", "?")))
        return f'void  // TODO(converter): {no.get("texto", "?")}'


# ═════════════════════════════════════════════════════════════
#  Entrada
# ═════════════════════════════════════════════════════════════

def converter_fonte(fonte, arquivo="<js>"):
    """O texto JS/TS vira (texto DataForge, pendências).

    Levanta `ErroDeLeitura` quando o parser não reconhece a fonte —
    traduzir o que não se leu produziria lixo com cara de tradução.
    """
    arvore = analisar(fonte, arquivo)
    emissor = Emissor(fonte, arquivo)
    emissor.programa(arvore)

    origem = "TypeScript" if arquivo.endswith((".ts", ".tsx")) else "JavaScript"
    cabecalho = [
        f"// Convertido de {os.path.basename(arquivo)} ({origem}) "
        f"por 'dataforge converter'.",
        "//",
    ]
    if emissor.pendencias:
        cabecalho += [
            f"// {len(emissor.pendencias)} ponto(s) precisam de revisao —",
            "// procure por 'TODO(converter)' abaixo.",
            "//",
        ]
    else:
        cabecalho += ["// Nada ficou pendente. Rode 'dataforge check' "
                      "para conferir.", "//"]
    cabecalho.append("")

    corpo = "\n".join(cabecalho + emissor.saida)
    while "\n\n\n" in corpo:
        corpo = corpo.replace("\n\n\n", "\n\n")
    return corpo.rstrip() + "\n", emissor.pendencias


def converter_arquivo(caminho, destino=None):
    """Converte um `.js`/`.ts` e grava o `.df` ao lado."""
    with io.open(caminho, encoding="utf-8") as f:
        fonte = f.read()
    texto, pendencias = converter_fonte(fonte, caminho)
    destino = destino or os.path.splitext(caminho)[0] + ".df"
    with io.open(destino, "w", encoding="utf-8") as f:
        f.write(texto)
    return destino, pendencias
