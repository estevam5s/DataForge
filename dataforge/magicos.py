"""
Os metodos magicos do DataForge.

Um metodo magico e um gancho: a linguagem o procura no blueprint quando
uma operacao acontece sobre uma instancia. Declarar '__add__' faz o '+'
funcionar; declarar '__getitem__' faz o '[]' funcionar.

    blueprint Vetor(x, y):
        action __add__(outro):
            yield spawn Vetor(self.x + outro.x, self.y + outro.y)

        action __str__():
            yield $"({self.x}, {self.y})"

        action __eq__(outro):
            yield self.x is outro.x and self.y is outro.y

    out spawn Vetor(1, 2) + spawn Vetor(3, 4)      // (4, 6)

─── Por que o nome com dois sublinhados ────────────────────

Porque e o que quem chega do Python ja conhece, e porque o sublinhado
duplo sinaliza "isto nao e para voce chamar" — ele e chamado PELA
linguagem, no momento da operacao. 'v.__add__(outro)' funciona, mas
escrever isso e o mesmo que escrever 'v + outro' de um jeito pior.

DataForge ja tinha 'operator +', que continua valendo e tem
prioridade: ele e mais direto de ler para quem nunca viu Python. Os
dois convivem porque cobrem publicos diferentes.

─── O que cada grupo cobre ─────────────────────────────────

    construcao    nascer, morrer, copiar
    texto         'out', interpolacao, formatacao
    comparacao    ==, !=, <, <=, >, >=, e ordenacao
    aritmetica    + - * / // % **, e as versoes refletida e no-lugar
    bits          & | ^ ~ << >>
    conversao     int(), float(), bool(), len(), hash()
    colecao       [], del, 'in', percurso, tamanho
    chamada       obj()
    atributo      leitura, escrita e remocao de campo
    contexto      'with'
    assincrono    'await' e percurso assincrono
"""

# ═════════════════════════════════════════════════════════════
#  A tabela
# ═════════════════════════════════════════════════════════════
#
# Cada entrada: nome -> (grupo, aridade, descricao).
# A aridade nao conta 'self'.

MAGICOS = {
    # ── construcao e ciclo de vida ──
    "__init__":      ("construcao", 0, "roda no spawn; sinonimo de 'setup'"),
    "__new__":       ("construcao", 0, "cria a instancia antes de '__init__'"),
    "__del__":       ("construcao", 0, "roda quando o objeto e descartado"),
    "__copy__":      ("construcao", 0, "copia rasa"),
    "__deepcopy__":  ("construcao", 0, "copia profunda"),
    "__clone__":     ("construcao", 0, "copia, no vocabulario do DataForge"),

    # ── texto ──
    "__str__":       ("texto", 0, "o texto que 'out' imprime"),
    "__repr__":      ("texto", 0, "o texto para quem depura"),
    "__format__":    ("texto", 1, "formatacao com especificador"),
    "__bytes__":     ("texto", 0, "a representacao em bytes"),
    "__doc__":       ("texto", 0, "a documentacao do objeto"),

    # ── comparacao ──
    "__eq__":        ("comparacao", 1, "a == b  (e 'a is b')"),
    "__ne__":        ("comparacao", 1, "a != b  (e 'a isnt b')"),
    "__lt__":        ("comparacao", 1, "a < b   (e 'a smaller b')"),
    "__le__":        ("comparacao", 1, "a <= b"),
    "__gt__":        ("comparacao", 1, "a > b   (e 'a bigger b')"),
    "__ge__":        ("comparacao", 1, "a >= b"),
    "__cmp__":       ("comparacao", 1, "-1, 0 ou 1; cobre os seis de uma vez"),

    # ── aritmetica ──
    "__add__":       ("aritmetica", 1, "a + b"),
    "__sub__":       ("aritmetica", 1, "a - b"),
    "__mul__":       ("aritmetica", 1, "a * b"),
    "__truediv__":   ("aritmetica", 1, "a / b"),
    "__floordiv__":  ("aritmetica", 1, "a ~/ b"),
    "__mod__":       ("aritmetica", 1, "a % b"),
    "__pow__":       ("aritmetica", 1, "a ** b"),
    "__divmod__":    ("aritmetica", 1, "quociente e resto de uma vez"),
    "__matmul__":    ("aritmetica", 1, "a @ b — multiplicacao de matriz"),

    # ── aritmetica refletida ──
    # Chamada quando o operando da ESQUERDA nao sabe fazer a conta.
    # '2 * vetor' procura '__rmul__' no vetor.
    "__radd__":      ("refletida", 1, "b + a, quando 'b' nao sabe somar"),
    "__rsub__":      ("refletida", 1, "b - a"),
    "__rmul__":      ("refletida", 1, "b * a"),
    "__rtruediv__":  ("refletida", 1, "b / a"),
    "__rfloordiv__": ("refletida", 1, "b ~/ a"),
    "__rmod__":      ("refletida", 1, "b % a"),
    "__rpow__":      ("refletida", 1, "b ** a"),
    "__rmatmul__":   ("refletida", 1, "b @ a"),

    # ── aritmetica no lugar ──
    # 'x += 1' procura '__iadd__' antes de cair em '__add__'. A
    # diferenca importa para objeto mutavel: somar no lugar evita
    # alocar um objeto novo por volta de laco.
    "__iadd__":      ("no-lugar", 1, "a += b, alterando 'a'"),
    "__isub__":      ("no-lugar", 1, "a -= b"),
    "__imul__":      ("no-lugar", 1, "a *= b"),
    "__itruediv__":  ("no-lugar", 1, "a /= b"),
    "__ifloordiv__": ("no-lugar", 1, "a ~/= b"),
    "__imod__":      ("no-lugar", 1, "a %= b"),
    "__ipow__":      ("no-lugar", 1, "a **= b"),

    # ── unarios ──
    "__neg__":       ("unario", 0, "-a"),
    "__pos__":       ("unario", 0, "+a"),
    "__abs__":       ("unario", 0, "abs(a)"),
    "__invert__":    ("unario", 0, "~a"),
    "__round__":     ("unario", 1, "round(a, casas)"),
    "__floor__":     ("unario", 0, "floor(a)"),
    "__ceil__":      ("unario", 0, "ceil(a)"),
    "__trunc__":     ("unario", 0, "trunc(a)"),

    # ── bits ──
    "__and__":       ("bits", 1, "a & b"),
    "__or__":        ("bits", 1, "a | b"),
    "__xor__":       ("bits", 1, "a ^ b"),
    "__lshift__":    ("bits", 1, "a << b"),
    "__rshift__":    ("bits", 1, "a >> b"),
    "__rand__":      ("bits", 1, "b & a"),
    "__ror__":       ("bits", 1, "b | a"),
    "__rxor__":      ("bits", 1, "b ^ a"),

    # ── conversao ──
    "__bool__":      ("conversao", 0, "o que 'given obj:' decide"),
    "__int__":       ("conversao", 0, "int(obj)"),
    "__float__":     ("conversao", 0, "float(obj)"),
    "__complex__":   ("conversao", 0, "complex(obj)"),
    "__index__":     ("conversao", 0, "o objeto como indice de colecao"),
    "__hash__":      ("conversao", 0, "a chave de vault que este objeto vira"),

    # ── colecao ──
    "__len__":       ("colecao", 0, "len(obj)"),
    "__getitem__":   ("colecao", 1, "obj[chave]"),
    "__setitem__":   ("colecao", 2, "obj[chave] := valor"),
    "__delitem__":   ("colecao", 1, "delete obj[chave]"),
    "__contains__":  ("colecao", 1, "item in obj"),
    "__iter__":      ("colecao", 0, "'cycle x in obj'"),
    "__next__":      ("colecao", 0, "o proximo item do percurso"),
    "__reversed__":  ("colecao", 0, "percurso de tras para frente"),
    "__missing__":   ("colecao", 1, "chave ausente, antes de dar erro"),
    "__length_hint__": ("colecao", 0, "tamanho aproximado, para alocar antes"),

    # ── chamada ──
    "__call__":      ("chamada", -1, "obj(argumentos)"),

    # ── atributo ──
    "__getattr__":     ("atributo", 1, "obj.campo, quando o campo nao existe"),
    "__getattribute__": ("atributo", 1, "obj.campo, SEMPRE"),
    "__setattr__":     ("atributo", 2, "obj.campo := valor"),
    "__delattr__":     ("atributo", 1, "delete obj.campo"),
    "__dir__":         ("atributo", 0, "a lista de nomes do objeto"),

    # ── descritor ──
    # Um descritor e um objeto que controla o acesso a um campo de
    # OUTRO objeto. E o mecanismo por tras de 'get'/'set', exposto
    # para quem quer reaproveitar a mesma regra em varios campos.
    "__get__":       ("descritor", 2, "leitura do campo que este objeto guarda"),
    "__set__":       ("descritor", 2, "escrita nele"),
    "__delete__":    ("descritor", 1, "remocao"),
    "__set_name__":  ("descritor", 2, "o nome que ele recebeu na classe"),

    # ── contexto ──
    "__enter__":     ("contexto", 0, "'with obj as x:' — o que 'x' recebe"),
    "__exit__":      ("contexto", 0, "o fim do bloco, mesmo com erro"),

    # ── assincrono ──
    "__await__":     ("assincrono", 0, "'await obj'"),
    "__aiter__":     ("assincrono", 0, "percurso assincrono"),
    "__anext__":     ("assincrono", 0, "o proximo item dele"),
    "__aenter__":    ("assincrono", 0, "'with' assincrono"),
    "__aexit__":     ("assincrono", 0, "o fim dele"),

    # ── tipo e classe ──
    "__instancecheck__": ("tipo", 1, "'e_um(x, Isto)'"),
    "__subclasscheck__": ("tipo", 1, "se um blueprint descende deste"),
    "__class_getitem__": ("tipo", 1, "Blueprint[Tipo] — generics"),
    "__init_subclass__": ("tipo", 1, "roda quando alguem herda deste"),
}

#: Operador -> metodo magico, para a busca ser um dicionario e nao um if.
POR_OPERADOR = {
    "+": "__add__", "-": "__sub__", "*": "__mul__", "/": "__truediv__",
    "~/": "__floordiv__", "//": "__floordiv__", "%": "__mod__",
    "**": "__pow__", "@": "__matmul__",
    "&": "__and__", "|": "__or__", "^": "__xor__",
    "<<": "__lshift__", ">>": "__rshift__",
}

#: O refletido de cada um: '2 * vetor' pergunta ao vetor.
REFLETIDO = {
    "__add__": "__radd__", "__sub__": "__rsub__", "__mul__": "__rmul__",
    "__truediv__": "__rtruediv__", "__floordiv__": "__rfloordiv__",
    "__mod__": "__rmod__", "__pow__": "__rpow__", "__matmul__": "__rmatmul__",
    "__and__": "__rand__", "__or__": "__ror__", "__xor__": "__rxor__",
}

#: A versao no-lugar, para 'x += 1'.
NO_LUGAR = {
    "__add__": "__iadd__", "__sub__": "__isub__", "__mul__": "__imul__",
    "__truediv__": "__itruediv__", "__floordiv__": "__ifloordiv__",
    "__mod__": "__imod__", "__pow__": "__ipow__",
}

#: Comparacao -> metodo. Os nomes do DataForge e os simbolos.
POR_COMPARACAO = {
    "is": "__eq__", "==": "__eq__",
    "isnt": "__ne__", "!=": "__ne__",
    "smaller": "__lt__", "<": "__lt__",
    "smaller_eq": "__le__", "<=": "__le__",
    "bigger": "__gt__", ">": "__gt__",
    "bigger_eq": "__ge__", ">=": "__ge__",
}

#: Quando so '__cmp__' existe, ele responde os seis.
DE_CMP = {
    "__eq__": lambda c: c == 0,
    "__ne__": lambda c: c != 0,
    "__lt__": lambda c: c < 0,
    "__le__": lambda c: c <= 0,
    "__gt__": lambda c: c > 0,
    "__ge__": lambda c: c >= 0,
}

#: Unario -> metodo.
POR_UNARIO = {"-": "__neg__", "+": "__pos__", "~": "__invert__"}


def grupos():
    """Os metodos magicos agrupados, na ordem em que a doc os apresenta."""
    saida = {}
    for nome, (grupo, aridade, descricao) in MAGICOS.items():
        saida.setdefault(grupo, []).append(
            {"nome": nome, "aridade": aridade, "descricao": descricao})
    return saida


def e_magico(nome):
    """O nome segue a convencao de metodo magico?

    Aceita qualquer '__x__', e nao so os da tabela: quem define um
    proprio nao deveria ver o nome tratado como campo comum.
    """
    return (isinstance(nome, str) and len(nome) > 4
            and nome.startswith("__") and nome.endswith("__"))


def conhecido(nome):
    return nome in MAGICOS


def total():
    return len(MAGICOS)
