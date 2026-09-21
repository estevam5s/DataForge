# -*- coding: utf-8 -*-
"""Arcane.Dominio — as pecas de um modelo de dominio que se sustenta.

O que este modulo NAO e
-----------------------
Ele nao e um framework que obriga a modelar de um jeito, e nao e uma
camada sobre banco. DDD e um conjunto de distincoes, e o valor delas
esta em serem **cobradas** — nao em serem nomeadas. Um `blueprint`
chamado `Pedido` com um comentario "// agregado" nao impede ninguem de
mexer nos itens por fora.

O que ha aqui sao as cobrancas:

    valor        igualdade por CONTEUDO, e imutavel — a troca e outro valor
    entidade     igualdade por IDENTIDADE, e o estado muda
    agregado     a unica porta de escrita; guarda invariantes e eventos
    evento       um fato que aconteceu, no passado, e imutavel
    repositorio  guarda e recupera AGREGADOS inteiros
    regra        uma condicao de negocio que se combina com E, OU e NAO
    unidade      uma transacao: confirma tudo, ou nada, e ai publica

Quatro decisoes que valem lembrar
---------------------------------
1. **A invariante e cobrada na saida de cada comando, e nao na
   entrada.** Cobrar antes deixa o objeto quebrado quando o comando
   falha no meio; cobrar depois garante que ninguem observa um estado
   invalido — e e por isso que o agregado e a unica porta.

2. **O evento so e publicado quando a unidade confirma.** Publicar na
   hora faz o mundo reagir a um fato que a transacao ainda pode
   desfazer — e-mail enviado sobre um pedido que nao existe.

3. **Um valor nao tem identidade, e isso e uma cobranca.** Dois
   `Dinheiro(10, "BRL")` sao o MESMO valor. Se a sua peca precisa
   distinguir duas instancias iguais, ela e uma entidade, e o modulo
   diz isso em vez de deixar passar.

4. **A regra e um objeto, e nao um `given`.** Um `given` dentro do
   servico nao pode ser combinado, nem reaproveitado na consulta, nem
   explicado ao usuario. `regra.por_que_nao(x)` devolve o motivo.
"""

import threading
import time
import uuid

_DOC = "tecnicas/dominio"


def _erro(mensagem, nota="", dica="", classe="DomainError"):
    """O erro do dominio, com a CLASSE certa.

    Levantar `RuntimeError_` em tudo faria a distincao morrer na
    fronteira: para quem escreve o `handle`, violar uma invariante e
    dividir por zero viram a mesma coisa. Cada peca levanta o seu, e
    `handle DomainError` continua pegando os nove.
    """
    from .. import errors
    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _campos_de(alvo):
    """Os campos de um vault, record ou instancia — a mesma pergunta."""
    if isinstance(alvo, dict):
        return dict(alvo)
    for atributo in ("fields", "campos"):
        valor = getattr(alvo, atributo, None)
        if isinstance(valor, dict):
            return dict(valor)
    interno = getattr(alvo, "__dict__", None)
    if isinstance(interno, dict):
        return {k: v for k, v in interno.items() if not k.startswith("_")}
    return {}


def _ler(alvo, campo, padrao=None):
    if isinstance(alvo, dict):
        return alvo.get(campo, padrao)
    return getattr(alvo, campo, _campos_de(alvo).get(campo, padrao))


# ═══════════════════════════════════════════════════════════
#  Valor
# ═══════════════════════════════════════════════════════════

class Valor:
    """Um objeto de valor: igualdade por CONTEUDO, e imutavel.

        Dinheiro := D.valor("Dinheiro", ["quantia", "moeda"],
                            regra := lambda v => v["quantia"] bigger_eq 0)

        dez := Dinheiro(10, "BRL")
        outro := Dinheiro(10, "BRL")
        assert dez is_equal outro          // o MESMO valor

    Por que nao um `record` e pronto
    ---------------------------------
    O `record` da a imutabilidade e a igualdade estrutural, e essas
    duas metades ja sao a maior parte. O que ele nao da e a **regra**:
    um `Dinheiro(-5, "BRL")` e um record perfeitamente valido, e o
    negocio descobre isso tres camadas adiante, num extrato negativo.
    Aqui a regra e cobrada na CRIACAO, que e o unico ponto em que ela
    pode impedir o valor errado de existir.
    """

    __slots__ = ("_nome", "_campos", "_valores", "_regra", "_motivo")

    def __init__(self, nome, campos, valores, regra=None, motivo=""):
        self._nome = str(nome)
        self._campos = tuple(campos)
        self._valores = dict(valores)
        self._regra = regra
        self._motivo = str(motivo)
        if callable(regra):
            try:
                passou = regra(dict(self._valores))
            except Exception as erro:                        # noqa: BLE001
                raise _erro(
                    f"a regra de '{self._nome}' estourou: {erro}",
                    nota="uma regra quebrada e um bug da regra, e nao um "
                         "valor invalido — dizer 'valor invalido' aqui "
                         "esconderia o defeito real",
                    classe="ValueObjectError")
            if passou is False:
                raise _erro(
                    motivo or f"'{self._nome}' recusou {self._valores}.",
                    nota="um objeto de valor e cobrado na CRIACAO: e o "
                         "unico ponto em que a regra pode impedir o valor "
                         "errado de existir",
                    classe="ValueObjectError")

    # ── ler ──────────────────────────────────────────────────

    def __getattr__(self, nome):
        valores = object.__getattribute__(self, "_valores")
        if nome in valores:
            return valores[nome]
        raise AttributeError(
            f"'{object.__getattribute__(self, '_nome')}' nao tem '{nome}'. "
            f"Tem: {', '.join(valores)}")

    def __getitem__(self, chave):
        return self._valores[str(chave)]

    def campos(self):
        return dict(self._valores)

    def nome(self):
        return self._nome

    # ── trocar e o mesmo que criar outro ─────────────────────

    def com(self, **mudancas):
        """Um valor NOVO com os campos trocados. O original nao muda.

        E o `with` do record, e pelo mesmo motivo: trocar um campo de
        um objeto de valor e criar outro valor. Um `Dinheiro` que muda
        de quantia nao e o mesmo dinheiro — e uma quantia diferente.
        """
        desconhecidos = set(mudancas) - set(self._campos)
        if desconhecidos:
            raise _erro(
                f"'{self._nome}' nao tem {sorted(desconhecidos)}.",
                nota=f"os campos sao: {', '.join(self._campos)}",
                dica="um campo a mais aqui seria um erro de digitacao "
                     "passando calado",
                classe="ValueObjectError")
        return Valor(self._nome, self._campos,
                     {**self._valores, **mudancas}, self._regra, self._motivo)

    # ── igualdade por conteudo ───────────────────────────────

    def __eq__(self, outro):
        if not isinstance(outro, Valor):
            return NotImplemented
        return (self._nome == outro._nome
                and self._valores == outro._valores)

    def __ne__(self, outro):
        igual = self.__eq__(outro)
        return NotImplemented if igual is NotImplemented else not igual

    def __hash__(self):
        return hash((self._nome, tuple(sorted(
            (k, str(v)) for k, v in self._valores.items()))))

    def __setattr__(self, nome, valor):
        if nome in self.__slots__:
            object.__setattr__(self, nome, valor)
            return
        raise _erro(
            f"'{self._nome}' e um objeto de valor: ele nao muda.",
            nota="dois valores iguais sao o MESMO valor; mudar um deles "
                 "mudaria o outro para quem os comparou",
            dica=f"crie outro: {self._nome.lower()}.com({nome} := …)",
            classe="ValueObjectError")

    def __repr__(self):
        partes = ", ".join(f"{k}={v!r}" for k, v in self._valores.items())
        return f"{self._nome}({partes})"


def valor(nome, campos, regra=None, motivo=""):
    """Define um tipo de objeto de valor. Devolve o construtor dele."""
    lista = [str(c) for c in (campos or [])]
    if not lista:
        raise _erro(f"'{nome}' precisa de ao menos um campo.",
                    dica='D.valor("Dinheiro", ["quantia", "moeda"])',
                    classe="ValueObjectError")

    def construir(*args, **kwargs):
        if len(args) > len(lista):
            raise _erro(
                f"'{nome}' aceita {len(lista)} campo(s), e vieram "
                f"{len(args)}.",
                nota=f"os campos, em ordem: {', '.join(lista)}",
                classe="ValueObjectError")
        valores = dict(zip(lista, args))
        desconhecidos = set(kwargs) - set(lista)
        if desconhecidos:
            raise _erro(f"'{nome}' nao tem {sorted(desconhecidos)}.",
                        nota=f"os campos sao: {', '.join(lista)}",
                        classe="ValueObjectError")
        valores.update(kwargs)
        faltando = [c for c in lista if c not in valores]
        if faltando:
            raise _erro(f"falta {faltando} para montar '{nome}'.",
                        nota="um objeto de valor nasce completo — um campo "
                             "vazio faria dois valores 'iguais' diferirem "
                             "no que ninguem preencheu",
                        classe="ValueObjectError")
        return Valor(nome, lista, valores, regra, motivo)

    construir.nome = str(nome)
    construir.campos = lista
    return construir


# ═══════════════════════════════════════════════════════════
#  Entidade e agregado
# ═══════════════════════════════════════════════════════════

class Entidade:
    """Igualdade por IDENTIDADE, e o estado muda.

    Duas pessoas com o mesmo nome sao duas pessoas. E a mesma pessoa
    com outro nome continua sendo ela — o que separa uma entidade de um
    objeto de valor nao e a mutabilidade, e sim a **continuidade**.
    """

    __slots__ = ("_id", "_tipo", "_estado", "_trava")

    def __init__(self, tipo, identidade=None, **estado):
        self._tipo = str(tipo)
        self._id = str(identidade) if identidade is not None else novo_id()
        self._estado = dict(estado)
        self._trava = threading.RLock()

    def id(self):
        return self._id

    def tipo(self):
        return self._tipo

    def estado(self):
        with self._trava:
            return dict(self._estado)

    def ler(self, campo, padrao=None):
        with self._trava:
            return self._estado.get(str(campo), padrao)

    def mudar(self, **campos):
        with self._trava:
            self._estado.update(campos)
        return self

    def __eq__(self, outro):
        if not isinstance(outro, Entidade):
            return NotImplemented
        return self._tipo == outro._tipo and self._id == outro._id

    def __ne__(self, outro):
        igual = self.__eq__(outro)
        return NotImplemented if igual is NotImplemented else not igual

    def __hash__(self):
        return hash((self._tipo, self._id))

    def __repr__(self):
        return f"<{self._tipo} {self._id}>"


def entidade(tipo, identidade=None, **estado):
    return Entidade(tipo, identidade, **estado)


def novo_id():
    """Um identificador novo. UUID4, em texto.

    Texto, e nao numero: um id que o banco gera obriga a salvar antes
    de ter identidade, e ai o agregado existe sem ser ele mesmo no
    intervalo entre criar e confirmar.
    """
    return str(uuid.uuid4())


class Agregado:
    """A unica porta de escrita de um grupo de objetos.

        pedido := D.agregado("Pedido")
        pedido.invariante("o total nunca e negativo",
                          lambda p => p.ler("total", 0) bigger_eq 0)

        mark @pedido.comando("acrescentar_item")
        action acrescentar(p, item, preco):
            p.mudar(total := p.ler("total", 0) + preco)
            p.aconteceu("ItemAcrescentado", {"item": item, "preco": preco})

    Tres cobrancas, e o que cada uma evita
    ---------------------------------------
    - **As invariantes sao conferidas na SAIDA de cada comando.**
      Cobrar na entrada deixa o objeto quebrado quando o comando falha
      no meio; cobrar na saida garante que ninguem observa um estado
      invalido.
    - **O estado so muda por comando.** `pedido.mudar(...)` fora de um
      comando e recusado: se qualquer um escreve, a invariante nao vale
      nada, porque nao ha onde cobra-la.
    - **Os eventos ficam guardados** ate a unidade de trabalho
      confirmar. Publicar na hora faz o mundo reagir a um fato que a
      transacao ainda pode desfazer.
    """

    def __init__(self, tipo, identidade=None, **estado):
        self._entidade = Entidade(tipo, identidade, **estado)
        self._invariantes = []
        self._eventos = []
        self._versao = 0
        self._em_comando = 0
        self._trava = threading.RLock()

    # ── identidade e estado ──────────────────────────────────

    def id(self):
        return self._entidade.id()

    def tipo(self):
        return self._entidade.tipo()

    def versao(self):
        """Quantos comandos ja rodaram. Serve a travas otimistas."""
        return self._versao

    def estado(self):
        return self._entidade.estado()

    def ler(self, campo, padrao=None):
        return self._entidade.ler(campo, padrao)

    def mudar(self, **campos):
        if self._em_comando <= 0:
            raise _erro(
                f"'{self.tipo()}' so muda dentro de um comando.",
                nota="se qualquer um escreve, a invariante nao vale nada — "
                     "nao ha onde cobra-la",
                dica='declare o comando: mark @agregado.comando("nome")',
                classe="AggregateError")
        self._entidade.mudar(**campos)
        return self

    # ── invariantes ──────────────────────────────────────────

    def invariante(self, descricao, condicao):
        """Uma verdade que vale ANTES e DEPOIS de todo comando."""
        if not callable(condicao):
            raise _erro("uma invariante precisa de uma condicao.",
                        classe="AggregateError")
        self._invariantes.append({"descricao": str(descricao),
                                  "condicao": condicao})
        return self

    def conferir(self):
        """Cobra as invariantes agora. Levanta na primeira que falhar."""
        for regra in self._invariantes:
            try:
                vale = regra["condicao"](self)
            except Exception as erro:                        # noqa: BLE001
                raise _erro(
                    f"a invariante '{regra['descricao']}' estourou: {erro}",
                    nota="uma invariante quebrada e um bug dela, e nao um "
                         "estado invalido",
                    classe="AggregateError")
            if vale is False:
                raise _erro(
                    f"'{self.tipo()}' violou: {regra['descricao']}",
                    nota=f"o estado era {self.estado()}",
                    dica="o comando foi desfeito; o agregado continua no "
                         "estado anterior",
                    classe="AggregateError")
        return True

    # ── comandos ─────────────────────────────────────────────

    def comando(self, nome, acao=None):
        """Registra um comando. Tambem serve de decorador.

        O que ele acrescenta: a conferencia das invariantes na saida, o
        avanco da versao, e o desfazer quando algo falha no meio.
        """
        def registrar(alvo):
            def executar(*args, **kwargs):
                return self.executar(nome, alvo, *args, **kwargs)

            executar.__name__ = str(nome)
            setattr(self, str(nome), executar)
            return executar

        return registrar if acao is None else registrar(acao)

    def executar(self, nome, acao, *args, **kwargs):
        with self._trava:
            # A foto do estado e dos eventos: sem ela, um comando que
            # falha no meio deixa metade da mudanca aplicada, e a
            # proxima leitura ve um agregado que nunca deveria existir.
            antes = self._entidade.estado()
            eventos_antes = list(self._eventos)
            self._em_comando += 1
            try:
                resultado = acao(self, *args, **kwargs)
                self.conferir()
            except Exception:
                self._entidade._estado = antes
                self._eventos = eventos_antes
                raise
            finally:
                self._em_comando -= 1
            self._versao += 1
            return resultado

    # ── eventos ──────────────────────────────────────────────

    def aconteceu(self, nome, dados=None):
        """Anota um fato. Ele so sai daqui quando a unidade confirmar."""
        registro = evento(nome, dados, origem=self.id(), tipo=self.tipo())
        self._eventos.append(registro)
        return registro

    def eventos(self):
        return list(self._eventos)

    def limpar_eventos(self):
        saindo = list(self._eventos)
        self._eventos.clear()
        return saindo

    def __eq__(self, outro):
        if not isinstance(outro, Agregado):
            return NotImplemented
        return self._entidade == outro._entidade

    def __hash__(self):
        return hash(self._entidade)

    def __repr__(self):
        return (f"<agregado {self.tipo()} {self.id()} v{self._versao}, "
                f"{len(self._eventos)} evento(s)>")


def agregado(tipo, identidade=None, **estado):
    return Agregado(tipo, identidade, **estado)


# ═══════════════════════════════════════════════════════════
#  Evento
# ═══════════════════════════════════════════════════════════

class Evento:
    """Um fato que aconteceu. No passado, e imutavel.

    O nome no passado nao e estilo: um evento chamado `CriarPedido` e
    um comando disfarcado, e quem o recebe acha que pode recusa-lo. Um
    `PedidoCriado` ja aconteceu — quem escuta reage, e nao decide.
    """

    __slots__ = ("nome", "dados", "em", "origem", "tipo", "id")

    def __init__(self, nome, dados=None, origem="", tipo=""):
        object.__setattr__(self, "nome", str(nome))
        object.__setattr__(self, "dados", dict(dados or {}))
        object.__setattr__(self, "em", time.time())
        object.__setattr__(self, "origem", str(origem))
        object.__setattr__(self, "tipo", str(tipo))
        object.__setattr__(self, "id", novo_id())

    def __setattr__(self, nome, valor):
        raise _erro(
            f"o evento '{self.nome}' ja aconteceu: ele nao muda.",
            nota="mudar um fato passado e reescrever a historia — quem ja "
                 "reagiu a ele reagiu ao que estava escrito antes",
            classe="EventError")

    def para_vault(self):
        return {"id": self.id, "nome": self.nome, "dados": dict(self.dados),
                "em": self.em, "origem": self.origem, "tipo": self.tipo}

    def __repr__(self):
        return f"<{self.nome} de {self.tipo} {self.origem}>"


def evento(nome, dados=None, origem="", tipo=""):
    if not str(nome):
        raise _erro("um evento precisa de nome.", classe="EventError")
    return Evento(nome, dados, origem, tipo)


# ═══════════════════════════════════════════════════════════
#  Regra (specification)
# ═══════════════════════════════════════════════════════════

class Regra:
    """Uma condicao de negocio que se combina, e que explica o "nao".

        maior := D.regra("maior de idade", lambda p => p.idade bigger_eq 18)
        brasil := D.regra("mora no Brasil", lambda p => p.pais is "BR")
        pode := maior.e(brasil)

        given not pode.vale(pessoa):
            out pode.por_que_nao(pessoa)

    Por que um objeto, e nao um `given`
    ------------------------------------
    Um `given` dentro do servico nao pode ser combinado, nem
    reaproveitado na consulta que lista "quem pode", nem explicado ao
    usuario. Os tres usos sao a mesma regra, e escreve-la tres vezes e
    como as tres divergem.
    """

    __slots__ = ("descricao", "_condicao")

    def __init__(self, descricao, condicao):
        if not callable(condicao):
            raise _erro("uma regra precisa de uma condicao.",
                        dica='D.regra("maior", lambda p => p.idade bigger_eq 18)',
                        classe="SpecificationError")
        self.descricao = str(descricao)
        self._condicao = condicao

    def vale(self, alvo):
        try:
            return bool(self._condicao(alvo))
        except Exception as erro:                            # noqa: BLE001
            raise _erro(
                f"a regra '{self.descricao}' estourou: {erro}",
                nota="uma regra quebrada e um bug dela, e nao um alvo que "
                     "nao a satisfaz — devolver 'nao vale' esconderia o "
                     "defeito",
                classe="SpecificationError")

    def por_que_nao(self, alvo):
        """O motivo, ou vazio quando vale. Combinada, diz QUAL parte falhou."""
        return "" if self.vale(alvo) else self.descricao

    # ── combinar ─────────────────────────────────────────────

    def e(self, outra):
        return _E(self, outra)

    def ou(self, outra):
        return _OU(self, outra)

    def nao(self):
        return _NAO(self)

    def filtrar(self, itens):
        """Os itens que satisfazem — a regra usada como consulta."""
        return [i for i in (itens or []) if self.vale(i)]

    def __repr__(self):
        return f"<regra {self.descricao}>"


class _E(Regra):
    __slots__ = ("_a", "_b")

    def __init__(self, a, b):
        self._a, self._b = a, b
        Regra.__init__(self, f"{a.descricao} E {b.descricao}",
                       lambda alvo: a.vale(alvo) and b.vale(alvo))

    def por_que_nao(self, alvo):
        # A parte que falhou, e nao a frase inteira: "maior de idade E
        # mora no Brasil" nao diz qual das duas o usuario precisa
        # resolver.
        for parte in (self._a, self._b):
            motivo = parte.por_que_nao(alvo)
            if motivo:
                return motivo
        return ""


class _OU(Regra):
    __slots__ = ("_a", "_b")

    def __init__(self, a, b):
        self._a, self._b = a, b
        Regra.__init__(self, f"{a.descricao} OU {b.descricao}",
                       lambda alvo: a.vale(alvo) or b.vale(alvo))

    def por_que_nao(self, alvo):
        if self.vale(alvo):
            return ""
        return (f"nem '{self._a.descricao}' nem '{self._b.descricao}'")


class _NAO(Regra):
    __slots__ = ("_dentro",)

    def __init__(self, dentro):
        self._dentro = dentro
        Regra.__init__(self, f"NAO ({dentro.descricao})",
                       lambda alvo: not dentro.vale(alvo))


def regra(descricao, condicao):
    return Regra(descricao, condicao)


# ═══════════════════════════════════════════════════════════
#  Repositorio
# ═══════════════════════════════════════════════════════════

class Repositorio:
    """Guarda e recupera AGREGADOS inteiros, por identidade.

    Ele nao tem `atualizar_campo`, nem consulta por coluna, e isso e
    deliberado: um repositorio que devolve meio agregado devolve um
    objeto cujas invariantes ninguem pode garantir.

    Esta implementacao e em memoria. Para um banco, `D.repositorio_de`
    recebe as acoes de ler e gravar — o contrato e o mesmo, e e o
    contrato que importa.
    """

    def __init__(self, tipo, ler=None, gravar=None, apagar=None, listar=None):
        self.tipo = str(tipo)
        self._memoria = {}
        self._ler = ler
        self._gravar = gravar
        self._apagar = apagar
        self._listar = listar
        self._trava = threading.RLock()

    def guardar(self, alvo):
        identidade = _identidade_de(alvo)
        if callable(self._gravar):
            self._gravar(identidade, alvo)
        else:
            with self._trava:
                self._memoria[identidade] = alvo
        return alvo

    def por_id(self, identidade):
        chave = str(identidade)
        if callable(self._ler):
            return self._ler(chave)
        with self._trava:
            return self._memoria.get(chave)

    def exigir(self, identidade):
        """Como `por_id`, mas levanta quando nao acha.

        As duas existem porque as duas perguntas existem: "existe?" e
        "me de, porque tem de existir". Uma so obrigaria metade das
        chamadas a tratar um `void` que nunca acontece.
        """
        achado = self.por_id(identidade)
        if achado is None:
            raise _erro(
                f"nao ha {self.tipo} com id '{identidade}'.",
                nota="quem chama 'exigir' afirma que ele existe; para a "
                     "duvida, 'por_id' devolve void",
                classe="RepositoryError")
        return achado

    def apagar(self, identidade):
        chave = str(identidade)
        if callable(self._apagar):
            return self._apagar(chave)
        with self._trava:
            return self._memoria.pop(chave, None) is not None

    def todos(self):
        if callable(self._listar):
            return list(self._listar())
        with self._trava:
            return list(self._memoria.values())

    def que(self, uma_regra):
        """Os agregados que satisfazem a regra — a mesma da decisao."""
        return uma_regra.filtrar(self.todos())

    def quantos(self):
        return len(self.todos())

    def __repr__(self):
        return f"<repositorio de {self.tipo}, {self.quantos()} item(ns)>"


def repositorio(tipo):
    return Repositorio(tipo)


def repositorio_de(tipo, ler, gravar, apagar=None, listar=None):
    """Um repositorio sobre o seu armazem — banco, arquivo, o que for."""
    return Repositorio(tipo, ler, gravar, apagar, listar)


def _identidade_de(alvo):
    for atributo in ("id",):
        valor_do = getattr(alvo, atributo, None)
        if callable(valor_do):
            return str(valor_do())
        if valor_do is not None:
            return str(valor_do)
    achado = _ler(alvo, "id")
    if achado is None:
        raise _erro(
            "o que vai para um repositorio precisa de identidade.",
            nota="um repositorio guarda agregados e entidades, que tem id; "
                 "um objeto de VALOR nao tem — e nao tem porque dois iguais "
                 "sao o mesmo",
            dica="se a sua peca precisa distinguir duas instancias iguais, "
                 "ela e uma entidade",
            classe="IdentityError")
    return str(achado)


# ═══════════════════════════════════════════════════════════
#  Unidade de trabalho
# ═══════════════════════════════════════════════════════════

class Unidade:
    """Uma transacao de dominio: confirma tudo, ou nada — e ai publica.

        u := D.unidade()
        u.registrar(pedido)
        u.registrar(estoque)
        u.confirmar()          // grava os dois, e SO ENTAO publica

    O evento so sai na confirmacao. Publicar na hora faz o mundo reagir
    a um fato que a transacao ainda pode desfazer: o e-mail sai, e o
    pedido nao existe.
    """

    def __init__(self, publicar=None):
        self._registrados = []
        self._publicar = publicar
        self._confirmada = False
        self._desfeita = False
        self.publicados = []

    def registrar(self, alvo, repo=None):
        if self._confirmada or self._desfeita:
            raise _erro("esta unidade ja terminou.",
                        dica="abra outra com D.unidade()",
                        classe="UnitOfWorkError")
        self._registrados.append({"alvo": alvo, "repo": repo})
        return self

    def confirmar(self):
        if self._confirmada:
            raise _erro("esta unidade ja foi confirmada.",
                        classe="UnitOfWorkError")
        if self._desfeita:
            raise _erro("esta unidade foi desfeita.",
                        classe="UnitOfWorkError")

        # Primeiro TODAS as invariantes, depois TODAS as gravacoes: se
        # a segunda gravacao falhasse por invariante, a primeira ja
        # estaria no banco, e a transacao de dominio teria vazado pela
        # metade.
        for registro in self._registrados:
            alvo = registro["alvo"]
            if hasattr(alvo, "conferir"):
                alvo.conferir()

        for registro in self._registrados:
            if registro["repo"] is not None:
                registro["repo"].guardar(registro["alvo"])

        saindo = []
        for registro in self._registrados:
            alvo = registro["alvo"]
            if hasattr(alvo, "limpar_eventos"):
                saindo.extend(alvo.limpar_eventos())

        self._confirmada = True
        self.publicados = saindo
        if callable(self._publicar):
            for fato in saindo:
                self._publicar(fato)
        return saindo

    def desfazer(self):
        """Descarta tudo — inclusive os eventos, que nunca aconteceram."""
        if self._confirmada:
            raise _erro("nao da para desfazer o que ja foi confirmado.",
                        nota="os eventos ja foram publicados, e quem reagiu "
                             "a eles nao tem como voltar atras",
                        dica="publique um evento de compensacao",
                        classe="UnitOfWorkError")
        for registro in self._registrados:
            alvo = registro["alvo"]
            if hasattr(alvo, "limpar_eventos"):
                alvo.limpar_eventos()
        self._desfeita = True
        return True

    def eventos_pendentes(self):
        pendentes = []
        for registro in self._registrados:
            alvo = registro["alvo"]
            if hasattr(alvo, "eventos"):
                pendentes.extend(alvo.eventos())
        return pendentes

    def __repr__(self):
        estado = ("confirmada" if self._confirmada else
                  "desfeita" if self._desfeita else "aberta")
        return f"<unidade {estado}, {len(self._registrados)} registrado(s)>"


def unidade(publicar=None):
    return Unidade(publicar)


# ═══════════════════════════════════════════════════════════
#  Contexto delimitado
# ═══════════════════════════════════════════════════════════

class Contexto:
    """Um modelo, com fronteira — e a traducao para atravessa-la.

        vendas := D.contexto("Vendas")
        vendas.repositorio("Pedido")
        vendas.ao_acontecer("PedidoPago", faturar)

    A traducao existe porque o mesmo nome significa coisas diferentes
    dos dois lados: o "Cliente" de Vendas tem limite de credito, e o de
    Suporte tem plano e chamados abertos. Passar um objeto inteiro de
    um lado ao outro e o que faz dois modelos virarem um so — e o unico
    e o que nao serve a ninguem.
    """

    def __init__(self, nome):
        self.nome = str(nome)
        self._repositorios = {}
        self._ouvintes = {}
        self._traducoes = {}
        self.recebidos = []

    def repositorio(self, tipo):
        if str(tipo) not in self._repositorios:
            self._repositorios[str(tipo)] = Repositorio(tipo)
        return self._repositorios[str(tipo)]

    def repositorios(self):
        return sorted(self._repositorios)

    def ao_acontecer(self, nome_do_evento, acao=None):
        """Registra quem reage a um fato. Tambem serve de decorador."""
        def registrar(alvo):
            self._ouvintes.setdefault(str(nome_do_evento), []).append(alvo)
            return alvo

        return registrar if acao is None else registrar(acao)

    def publicar(self, fato):
        """Entrega o fato a quem registrou interesse.

        Um ouvinte que estoura **nao** impede os outros: eles reagem a
        um fato que ja aconteceu, e derrubar os demais por causa de um
        faria o mundo ficar parcialmente atualizado sem ninguem saber.
        """
        self.recebidos.append(fato)
        falhas = []
        for ouvinte in self._ouvintes.get(fato.nome, []):
            try:
                ouvinte(fato)
            except Exception as erro:                        # noqa: BLE001
                falhas.append({"evento": fato.nome, "erro": str(erro)})
        return falhas

    def traduzir_de(self, outro_contexto, tipo, acao):
        """Como um objeto do outro lado vira um objeto daqui.

        E a *camada anticorrupcao*: sem ela, o modelo de fora entra
        inteiro e o de dentro passa a ter campos que so existem porque
        o outro time os tem.
        """
        self._traducoes[(str(outro_contexto), str(tipo))] = acao
        return self

    def receber(self, outro_contexto, tipo, objeto):
        chave = (str(outro_contexto), str(tipo))
        traducao = self._traducoes.get(chave)
        if traducao is None:
            raise _erro(
                f"'{self.nome}' nao sabe traduzir '{tipo}' de "
                f"'{outro_contexto}'.",
                nota="sem traducao, o modelo de fora entraria inteiro — e o "
                     "de dentro passaria a ter campos que so existem porque "
                     "o outro time os tem",
                dica=f'{self.nome}.traduzir_de("{outro_contexto}", '
                     f'"{tipo}", acao)',
                classe="BoundedContextError")
        return traducao(objeto)

    def __repr__(self):
        return (f"<contexto {self.nome}, {len(self._repositorios)} "
                f"repositorio(s), {len(self._ouvintes)} evento(s) ouvido(s)>")


def contexto(nome):
    return Contexto(nome)


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

class ArcaneDominio:
    """Arcane.Dominio — as pecas de um modelo que se sustenta."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Dominio",

            # ── as pecas ──
            "valor": valor,
            "Valor": Valor,
            "entidade": entidade,
            "Entidade": Entidade,
            "agregado": agregado,
            "Agregado": Agregado,
            "evento": evento,
            "Evento": Evento,
            "regra": regra,
            "Regra": Regra,
            "repositorio": repositorio,
            "repositorio_de": repositorio_de,
            "Repositorio": Repositorio,
            "unidade": unidade,
            "Unidade": Unidade,
            "contexto": contexto,
            "Contexto": Contexto,

            # ── utilidades ──
            "novo_id": novo_id,
        }
