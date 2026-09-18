"""
`type` — dar nome a um tipo, e cobrar o que o nome promete.

A linguagem sabia declarar `record`, `enum`, `blueprint` e `trait`, e não
sabia dar nome a um TIPO. Cinco formas passaram a existir, e as cinco são
a MESMA declaração — muda só o que vem depois do `:=`:

    type Id := Integer                                   alias
    type Par<T> := Cluster<T>                            alias genérico
    type Json := String | Integer | Boolean | Void       união
    type Auditavel := Serial & Ordenavel                 interseção
    type Positivo := Integer where valor bigger 0        refinamento
    opaque type Cpf := String where len(valor) is 11     opaco

─── Transparente confere; opaco embrulha ───────────────────────

Um tipo transparente é uma CONFERÊNCIA: `x: Positivo := 5` guarda o
número 5, e `typeof(x)` responde `Integer`. Nada muda de forma, e por
isso nada quebra — `x` continua sendo aceito por tudo que aceita um
`Integer`.

Um tipo opaco é um VALOR: `Cpf("12345678901")` devolve um objeto que
sabe o próprio nome. É o que torna o tipo **nominal** — um texto com
onze dígitos não é um `Cpf`, e essa é a única forma de o tipo proteger
de alguma coisa. Um `Cpf` que fosse só uma conferência aceitaria
`cadastrar(senha)` sem reclamar, e aí o tipo não serve para nada.

O embrulho (`Opaco`) delega por PROTOCOLO — texto, igualdade, ordem,
hash, conta, tamanho, iteração, índice. É a mesma escolha da ponte para
o Python: quem pergunta `len(x)` não precisa saber o que `x` é.

─── A regra roda na fronteira ──────────────────────────────────

`where valor bigger 0` é uma expressão da linguagem, com `valor` ligado
ao que está entrando. Ela roda na declaração, no parâmetro, no retorno e
no campo — em toda fronteira onde o nome aparece. Um refinamento que só
valesse na criação seria uma sugestão, não um tipo.

A base é conferida ANTES da regra, sempre. `len(valor)` sobre um número
levantaria um erro do interpretador — e a mensagem falaria de `len`, e
não do tipo que a pessoa escreveu.

─── Custo ──────────────────────────────────────────────────────

Quem não declara `type` não paga nada: o registro nasce vazio, e
`_check_type` só olha para cá quando o nome não é um tipo embutido — uma
busca de dicionário que já acontecia. A regra de um refinamento é
compilada uma vez, na declaração, e não a cada conferência.
"""

from .errors import TypeError_

#: As formas que uma declaração pode ter. É o campo `especie` do nó.
ALIAS = "alias"
UNIAO = "uniao"
INTERSECAO = "intersecao"


class TipoNomeado:
    """Uma declaração de `type`, já pronta para conferir.

    `partes` são os nomes do lado direito: um só no alias e no
    refinamento, vários na união e na interseção.
    """

    __slots__ = ("nome", "especie", "partes", "parametros", "regra",
                 "regra_texto", "opaco", "escopo", "arquivo")

    def __init__(self, nome, especie, partes, parametros=(), regra=None,
                 regra_texto="", opaco=False, escopo=None, arquivo=""):
        self.nome = nome
        self.especie = especie
        self.partes = tuple(partes)
        self.parametros = tuple(parametros)
        self.regra = regra                  # o nó da expressão de 'where'
        self.regra_texto = regra_texto      # como ela foi escrita
        self.opaco = opaco
        self.escopo = escopo                # onde a regra é avaliada
        self.arquivo = arquivo

    @property
    def base(self):
        """O tipo de baixo — o que o valor é, de verdade."""
        return self.partes[0] if self.partes else "Any"

    def texto(self):
        junta = " | " if self.especie == UNIAO else " & "
        direita = junta.join(self.partes) if len(self.partes) > 1 else self.base
        if self.regra_texto:
            direita += f" where {self.regra_texto}"
        return direita

    def __repr__(self):                                    # pragma: no cover
        return f"<type {self.nome} := {self.texto()}>"


class Opaco:
    """O valor de um tipo opaco: o dado de dentro, e o nome por fora.

    Delegar por protocolo é o que faz `$"{cpf}"`, `a is b`, `len(nome)`,
    `preco * 2` e `ordenar(...)` continuarem funcionando sem que nenhum
    deles saiba o que é um tipo opaco. Trocar isso por `isinstance` em
    qualquer lugar quebraria o tipo inteiro.
    """

    __slots__ = ("valor", "tipo")

    def __init__(self, valor, tipo):
        self.valor = valor
        self.tipo = tipo

    # ── identidade ──
    def __repr__(self):
        return repr(self.valor)

    def __str__(self):
        return str(self.valor)

    def __eq__(self, outro):
        return self.valor == (outro.valor if isinstance(outro, Opaco) else outro)

    def __ne__(self, outro):
        return not self.__eq__(outro)

    def __hash__(self):
        return hash(self.valor)

    def __bool__(self):
        return bool(self.valor)

    # ── ordem ──
    def __lt__(self, outro):
        return self.valor < _cru(outro)

    def __le__(self, outro):
        return self.valor <= _cru(outro)

    def __gt__(self, outro):
        return self.valor > _cru(outro)

    def __ge__(self, outro):
        return self.valor >= _cru(outro)

    # ── conta ──
    def __add__(self, outro):
        return self.valor + _cru(outro)

    def __radd__(self, outro):
        return _cru(outro) + self.valor

    def __sub__(self, outro):
        return self.valor - _cru(outro)

    def __rsub__(self, outro):
        return _cru(outro) - self.valor

    def __mul__(self, outro):
        return self.valor * _cru(outro)

    def __rmul__(self, outro):
        return _cru(outro) * self.valor

    def __truediv__(self, outro):
        return self.valor / _cru(outro)

    def __rtruediv__(self, outro):
        return _cru(outro) / self.valor

    def __floordiv__(self, outro):
        return self.valor // _cru(outro)

    def __mod__(self, outro):
        return self.valor % _cru(outro)

    def __neg__(self):
        return -self.valor

    def __int__(self):
        return int(self.valor)

    def __float__(self):
        return float(self.valor)

    # ── coleção ──
    def __len__(self):
        return len(self.valor)

    def __iter__(self):
        return iter(self.valor)

    def __contains__(self, item):
        return _cru(item) in self.valor

    def __getitem__(self, chave):
        return self.valor[chave]


def _cru(valor):
    """O dado de dentro, se for opaco; o próprio valor, se não."""
    return valor.valor if isinstance(valor, Opaco) else valor


def desembrulhar(valor):
    """Público: o que serializar, gravar num banco ou mandar pela rede."""
    return _cru(valor)


# ═════════════════════════════════════════════════════════════
#  O registro
# ═════════════════════════════════════════════════════════════

class Registro:
    """Os tipos declarados num programa. Um por interpretador."""

    __slots__ = ("por_nome",)

    def __init__(self):
        self.por_nome = {}

    def declarar(self, tipo):
        self.por_nome[tipo.nome] = tipo
        return tipo

    def obter(self, nome):
        """O tipo com esse nome — inclusive 'M.Positivo', que veio por adopt."""
        achado = self.por_nome.get(nome)
        if achado is None and "." in nome:
            achado = self.por_nome.get(nome.rsplit(".", 1)[1])
        return achado

    def __contains__(self, nome):
        return self.obter(nome) is not None

    def __bool__(self):
        return bool(self.por_nome)


def especializar(molde, argumentos):
    """'type Par<T> := Cluster<T>' + ('Integer',) -> Cluster<Integer>.

    É a função de tipo mais simples que existe, e é o que torna um alias
    genérico útil: sem a troca, 'Par<Integer>' conferiria 'Cluster<T>' e
    'T' aceita tudo — o nome prometeria uma coisa e cobraria outra.
    """
    if not molde.parametros:
        return molde
    troca = dict(zip(molde.parametros, argumentos))
    partes = tuple(_trocar(parte, troca) for parte in molde.partes)
    return TipoNomeado(
        nome=f"{molde.nome}<{', '.join(argumentos)}>", especie=molde.especie,
        partes=partes, parametros=(), regra=molde.regra,
        regra_texto=molde.regra_texto, opaco=molde.opaco,
        escopo=molde.escopo, arquivo=molde.arquivo)


def _trocar(tipo, troca):
    """Troca os parâmetros de tipo pelo que foi passado, sem tocar no resto."""
    saida, palavra = [], []
    for ch in tipo + " ":
        if ch.isalnum() or ch in "._":
            palavra.append(ch)
            continue
        nome = "".join(palavra)
        saida.append(troca.get(nome, nome))
        palavra = []
        saida.append(ch)
    return "".join(saida)[:-1]


def separar_uniao(tipo):
    """'A | B' -> ['A', 'B']; '&' idem. Respeita os '<>' aninhados.

    'Vault<String, Integer> | Void' tem uma vírgula e um '|', e só o
    segundo separa: dentro dos sinais de menor e maior está o conteúdo
    da coleção, que não é alternativa de nada.
    """
    for simbolo, especie in (("|", UNIAO), ("&", INTERSECAO)):
        partes = _quebrar(tipo, simbolo)
        if len(partes) > 1:
            return especie, partes
    return ALIAS, [tipo.strip()]


def _quebrar(tipo, simbolo):
    partes, profundidade, atual = [], 0, []
    for ch in tipo:
        if ch == "<":
            profundidade += 1
        elif ch == ">":
            profundidade -= 1
        if ch == simbolo and profundidade == 0:
            partes.append("".join(atual).strip())
            atual = []
        else:
            atual.append(ch)
    partes.append("".join(atual).strip())
    return [p for p in partes if p]


def e_composto(tipo):
    """'A | B' ou 'A & B' escrito direto na anotação, sem nome."""
    return isinstance(tipo, str) and separar_uniao(tipo)[0] != ALIAS


# ═════════════════════════════════════════════════════════════
#  As mensagens
# ═════════════════════════════════════════════════════════════

def erro_de_uniao(nome, partes, obtido, o_que, node):
    alternativas = " | ".join(partes)
    rotulo = f"{nome} ({alternativas})" if nome != alternativas else alternativas
    return TypeError_(
        f"{o_que} declared as {rotulo} but got {obtido}",
        getattr(node, "line", 0), getattr(node, "column", 0),
        nota="a union accepts a value of any one of its members",
        dica=f"pass one of: {alternativas}",
        doc="tipos-nomeados")


def erro_de_intersecao(nome, falta, obtido, o_que, node):
    return TypeError_(
        f"{o_que} declared as {nome} but got {obtido}, which is not a {falta}",
        getattr(node, "line", 0), getattr(node, "column", 0),
        nota=f"{nome} requires every part at the same time",
        dica=f"make {obtido} implement {falta}",
        doc="tipos-nomeados")


def erro_de_regra(tipo, valor_texto, o_que, node):
    return TypeError_(
        f"{o_que} declared as {tipo.nome} but {valor_texto} breaks its rule: "
        f"{tipo.regra_texto}",
        getattr(node, "line", 0), getattr(node, "column", 0),
        nota=f"{tipo.nome} is a {tipo.base} where {tipo.regra_texto}",
        dica=f"check the value before it reaches {o_que}",
        doc="tipos-nomeados")


def erro_de_opaco(tipo, obtido, o_que, node):
    return TypeError_(
        f"{o_que} declared as {tipo.nome} but got {obtido}",
        getattr(node, "line", 0), getattr(node, "column", 0),
        nota=f"{tipo.nome} is opaque: only {tipo.nome}(…) makes one, and it "
             f"validates what goes in",
        dica=f"build it with {tipo.nome}(…)",
        doc="tipos-nomeados")
