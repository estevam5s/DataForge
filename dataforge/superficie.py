# -*- coding: utf-8 -*-
"""O que um modulo local OFERECE — lido do arquivo, sem executa-lo.

O problema que isto resolve
---------------------------
O analisador declarava o apelido de um 'adopt' como "Module" e parava
ali. Consequencia, num projeto de 200 arquivos:

    adopt ./pedidos as P

    P.naoExisteMesmo()         # nao acusado
    P.criar(1, 2, 3)           # aridade errada, nao acusada
    P.Pedido("texto", "texto") # tipo errado, nao acusado
    p.zzz                      # campo inexistente, nao acusado

Ou seja: TODA chamada entre modulos era invisivel para a conferencia. E
num sistema grande a maioria das chamadas e entre modulos — num arquivo
de 40 linhas o erro aparece na primeira execucao; num de 200 arquivos,
aparece em producao.

O que e lido
------------
So o que 'relay' exporta, quando ha 'relay'. Um modulo que declara o que
exporta esta dizendo que o resto e interno, e acusar o uso de um nome
interno seria acusar o que o programa faz de certo — mas conferir
ARIDADE de quem foi exportado e sempre justo.

O que NAO e feito
-----------------
O arquivo nao e executado. Nada de 'adopt' recursivo com efeito
colateral, nada de ler banco, nada de subir servidor. So lexer e parser,
e so os nos de definicao do nivel de cima.

Por isso a superficie e conservadora: quando o arquivo nao compila, ou
quando o modulo exporta algo que sai de uma expressao (um 'relay' de
variavel calculada), ela devolve 'aberta = yes' e o analisador volta a
ficar calado. Um falso alarme e pior que um silencio.
"""

import os
import threading

from . import resolucao

#: caminho absoluto -> (mtime, Superficie). Um projeto de 200 arquivos
#: importa os mesmos vizinhos dezenas de vezes, e parsear de novo a cada
#: vez levaria o 'check' de meio segundo a mais de um minuto.
_CACHE = {}
_TRAVA = threading.RLock()

#: Ate onde a leitura desce. Um ciclo 'a -> b -> a' e legitimo em
#: DataForge (o interpretador o detecta em execucao); aqui ele so nao
#: pode virar recursao infinita.
PROFUNDIDADE = 4


class Membro:
    """Uma coisa que o modulo oferece."""

    __slots__ = ("nome", "especie", "minimo", "maximo", "campos", "linha")

    def __init__(self, nome, especie, minimo=0, maximo=None, campos=None,
                 linha=0):
        self.nome = nome
        #: 'acao', 'record', 'blueprint', 'enum', 'trait', 'valor'
        self.especie = especie
        #: Quantos argumentos aceita. 'maximo = None' significa variadico.
        self.minimo = minimo
        self.maximo = maximo
        #: Para record e blueprint: os membros de instancia.
        self.campos = set(campos or ())
        self.linha = linha

    def aceita(self, quantos):
        if quantos < self.minimo:
            return False
        return self.maximo is None or quantos <= self.maximo

    def esperado(self):
        if self.maximo is None:
            return f"{self.minimo} ou mais"
        if self.minimo == self.maximo:
            return str(self.minimo)
        return f"{self.minimo} a {self.maximo}"

    def __repr__(self):
        return f"<{self.especie} {self.nome}>"


class Superficie:
    """O que um modulo oferece, e se podemos confiar na lista.

    `aberta` e a valvula: quando `yes`, o analisador nao acusa nada
    sobre este modulo. Ela liga sozinha no caso de o arquivo nao
    compilar, de a profundidade acabar, ou de o modulo reexportar algo
    que so existe em execucao.
    """

    __slots__ = ("membros", "aberta", "motivo", "caminho", "importa")

    def __init__(self, membros=None, aberta=False, motivo="", caminho="",
                 importa=None):
        self.membros = dict(membros or {})
        self.aberta = aberta
        self.motivo = motivo
        self.caminho = caminho
        #: Os caminhos absolutos que este arquivo adota. E com isto que
        #: o analisador acha ciclo sem executar nada.
        self.importa = list(importa or ())

    def tem(self, nome):
        return self.aberta or nome in self.membros

    def obter(self, nome):
        return self.membros.get(nome)

    def nomes(self):
        return sorted(self.membros)

    def __repr__(self):
        estado = "aberta" if self.aberta else f"{len(self.membros)} membro(s)"
        return f"<superficie {os.path.basename(self.caminho)} {estado}>"


ABERTA = Superficie(aberta=True, motivo="modulo nao lido")


def de_modulo(nome, arquivo, profundidade=PROFUNDIDADE, vistos=None):
    """A superficie do modulo que `nome` pede, visto de `arquivo`."""
    caminho = (resolucao.achar(nome, arquivo)
               or resolucao.achar_em_pacotes(nome, arquivo)
               or resolucao.achar_no_proprio_pacote(nome, arquivo))
    if caminho is None:
        return None            # nao e um modulo local — quem chama decide
    return de_arquivo(caminho, profundidade, vistos)


def de_arquivo(caminho, profundidade=PROFUNDIDADE, vistos=None):
    """A superficie de um .df, do cache quando possivel."""
    caminho = os.path.abspath(caminho)
    vistos = vistos or set()

    if caminho in vistos:
        # Ciclo. Devolver aberta em vez de vazia: o modulo existe, so
        # nao sabemos o que ele tem sem entrar em loop.
        return Superficie(aberta=True, motivo="ciclo de import",
                          caminho=caminho)
    if profundidade <= 0:
        return Superficie(aberta=True, motivo="profundidade esgotada",
                          caminho=caminho)

    try:
        marca = os.path.getmtime(caminho)
    except OSError:
        return Superficie(aberta=True, motivo="arquivo ilegivel",
                          caminho=caminho)

    with _TRAVA:
        guardado = _CACHE.get(caminho)
        if guardado is not None and guardado[0] == marca:
            return guardado[1]

    superficie = _ler(caminho, profundidade, vistos | {caminho})
    with _TRAVA:
        _CACHE[caminho] = (marca, superficie)
    return superficie


def limpar_cache():
    """Para o LSP, que reanalisa o arquivo a cada tecla."""
    with _TRAVA:
        _CACHE.clear()


def _ler(caminho, profundidade, vistos):
    from .lexer import tokenize
    from .parser import parse

    try:
        with open(caminho, encoding="utf-8") as f:
            fonte = f.read()
        programa = parse(tokenize(fonte, caminho), caminho)
    except Exception:                             # noqa: BLE001
        # Um arquivo que nao compila e problema DELE, e o 'check' sobre
        # ele vai dizer isso. Aqui, calar: acusar o uso de um simbolo
        # porque o outro arquivo esta quebrado seria culpar o inocente.
        return Superficie(aberta=True, motivo="nao compila",
                          caminho=caminho)

    definidos = {}
    exportados = []
    importados = []
    reexporta_calculado = False

    for stmt in getattr(programa, "body", []) or []:
        tipo = type(stmt).__name__

        if tipo == "ActionDeclaration":
            definidos[stmt.name] = _de_acao(stmt)
        elif tipo == "RecordDeclaration":
            definidos[stmt.name] = _de_record(stmt)
        elif tipo == "BlueprintDeclaration":
            definidos[stmt.name] = _de_blueprint(stmt)
        elif tipo == "EnumDeclaration":
            definidos[stmt.name] = Membro(
                stmt.name, "enum", 1, 1,
                campos=(list(getattr(stmt, "members", {}) or {})
                        + list(getattr(stmt, "methods", {}) or {})),
                linha=getattr(stmt, "line", 0))
        elif tipo == "TraitDeclaration":
            definidos[stmt.name] = Membro(
                stmt.name, "trait", 0, None,
                linha=getattr(stmt, "line", 0))
        elif tipo == "Assignment":
            nome = _nome_do_alvo(stmt)
            if nome:
                # Uma variavel do nivel de cima e um valor, e chamar um
                # valor pode ser legitimo (um lambda). Variadico.
                definidos.setdefault(nome, Membro(
                    nome, "valor", 0, None,
                    linha=getattr(stmt, "line", 0)))
        elif tipo == "RelayStatement":
            if getattr(stmt, "origem", None):
                # 'relay a, b from ./outro' — reexporta de terceiro.
                # Seguir ate la seria possivel; por ora, abrir.
                reexporta_calculado = True
            for nome in getattr(stmt, "names", []) or []:
                exportados.append(nome)
        elif tipo == "AdoptStatement":
            alvo = _modulo_local(getattr(stmt, "module", ""), caminho)
            if alvo:
                importados.append(alvo)
            # 'adopt ./x as X' + 'relay X' reexporta um modulo inteiro.
            alias = getattr(stmt, "alias", None)
            if not alias:
                bruto = str(getattr(stmt, "module", ""))
                alias = bruto.replace("\\", "/").rstrip("/").split("/")[-1]
                alias = alias.split(".")[-1] if "." in alias else alias
            if alias:
                definidos.setdefault(alias, Membro(alias, "valor", 0, None))
            for par in (getattr(stmt, "selection", None) or []):
                apelido = par[1] if isinstance(par, (list, tuple)) else par
                definidos.setdefault(apelido, Membro(apelido, "valor",
                                                     0, None))

    if exportados:
        membros = {}
        for nome in exportados:
            achado = definidos.get(nome)
            if achado is None:
                # 'relay' de algo que este leitor nao viu — um nome que
                # nasce dentro de um 'given', de um laco, de um
                # 'monitor'. Existe em execucao e nao aqui.
                reexporta_calculado = True
                continue
            membros[nome] = achado
        if reexporta_calculado:
            return Superficie(membros, aberta=True,
                              motivo="relay de nome calculado",
                              caminho=caminho, importa=importados)
        return Superficie(membros, caminho=caminho, importa=importados)

    # Sem 'relay', tudo o que e do nivel de cima esta visivel — e como o
    # interpretador se comporta.
    return Superficie(definidos, caminho=caminho, importa=importados)


def _modulo_local(nome, de_onde):
    """O caminho absoluto de um 'adopt', quando ele e um arquivo local."""
    if not nome or str(nome).startswith("Python."):
        return None
    from .stdlib import get_module
    if get_module(str(nome)) is not None:
        return None
    alvo = (resolucao.achar(nome, de_onde)
            or resolucao.achar_em_pacotes(nome, de_onde)
            or resolucao.achar_no_proprio_pacote(nome, de_onde))
    return os.path.abspath(alvo) if alvo else None


def ciclo_a_partir_de(caminho, limite=40):
    """O ciclo de import que comeca e volta neste arquivo, ou None.

    Devolve a CADEIA — ['a.df', 'b.df', 'a.df'] — e nao so um sim ou
    nao: um ciclo de quatro arquivos e impossivel de quebrar sem saber
    por onde ele passa.

    Um ciclo estoura em EXECUCAO, no primeiro 'adopt'. Achar isso antes
    de rodar e exatamente o trabalho do analisador, e ele nao fazia:
    'dataforge check' passava limpo num projeto que nao sobe.

    O limite existe para o caso de um grafo enorme; ele e generoso o
    bastante para nunca esconder um ciclo real de projeto.
    """
    inicio = os.path.abspath(caminho)
    # Busca em largura: o ciclo mais CURTO primeiro, que e o mais facil
    # de quebrar — e o que a mensagem deve mostrar.
    fila = [[inicio]]
    vistos = set()
    passos = 0
    while fila and passos < limite:
        passos += 1
        cadeia = fila.pop(0)
        atual = cadeia[-1]
        superficie = de_arquivo(atual)
        for vizinho in superficie.importa:
            if vizinho == inicio:
                return cadeia + [vizinho]
            if vizinho in vistos:
                continue
            vistos.add(vizinho)
            fila.append(cadeia + [vizinho])
    return None


def _de_acao(stmt):
    """`params` e uma lista de nomes; `defaults`, um vault por nome.

    O rest chega como um nome com prefixo '...' — e o que o parser
    produz para `action f(a, ...resto)`.
    """
    parametros = [str(p) for p in (getattr(stmt, "params", []) or [])]
    padroes = getattr(stmt, "defaults", {}) or {}
    variadico = any(p.startswith("...") for p in parametros)
    fixos = [p for p in parametros if not p.startswith("...")]
    obrigatorios = sum(1 for p in fixos if p not in padroes)
    return Membro(stmt.name, "acao", obrigatorios,
                  None if variadico else len(fixos),
                  linha=getattr(stmt, "line", 0))


def _de_record(stmt):
    """`fields` e uma lista de tuplas `(nome, tipo, padrao)`."""
    campos = [f[0] if isinstance(f, (list, tuple)) else getattr(f, "name", f)
              for f in (getattr(stmt, "fields", []) or [])]
    metodos = list(getattr(stmt, "methods", {}) or {})
    # Um record aceita os campos posicionalmente ou por nome, e todos
    # podem ter padrao: o minimo e zero.
    return Membro(stmt.name, "record", 0, len(campos),
                  campos=list(campos) + metodos,
                  linha=getattr(stmt, "line", 0))


def _de_blueprint(stmt):
    """Os metodos de um blueprint moram no `body`, nao num vault."""
    parametros = [str(p) for p in
                  (getattr(stmt, "constructor_params", []) or [])]
    metodos = {}
    membros = set(parametros)
    for filho in (getattr(stmt, "body", []) or []):
        nome = getattr(filho, "name", None)
        if nome:
            membros.add(nome)
            if type(filho).__name__ == "ActionDeclaration":
                metodos[nome] = filho
    for campo in (getattr(stmt, "fields_decl", []) or []):
        membros.add(campo[0] if isinstance(campo, (list, tuple))
                    else getattr(campo, "name", campo))

    # Se ele herda de algo, a lista de membros nao esta fechada: a mae
    # pode estar em outro arquivo, e a regra de "calar quando a mae nao
    # foi vista" ja existe no analisador de instancia.
    herda = bool(getattr(stmt, "parents", None) or
                 getattr(stmt, "traits", None))

    setup = metodos.get("setup") or metodos.get("initiate")
    if parametros:
        minimo, maximo = 0, len(parametros)
    elif setup is not None:
        acao = _de_acao(setup)
        minimo, maximo = acao.minimo, acao.maximo
    else:
        minimo, maximo = 0, 0

    return Membro(stmt.name, "blueprint", minimo, maximo,
                  # Conjunto vazio quando herda: significa "nao sei", e
                  # quem consulta trata assim.
                  campos=set() if herda else membros,
                  linha=getattr(stmt, "line", 0))


def _nome_do_alvo(stmt):
    alvo = getattr(stmt, "target", None)
    if alvo is None:
        return None
    if isinstance(alvo, str):
        return alvo
    return getattr(alvo, "name", None)
