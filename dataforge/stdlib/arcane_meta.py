"""
Arcane.Meta — ler os decoradores em tempo de execução.

Um decorador que só anota não serve de nada se ninguém puder ler a
anotação. Este módulo é a outra metade: `@Rota("/itens")` grava o
caminho, e `Meta.ler(listar, "Rota")` o devolve.

É o que torna possível escrever, em DataForge, o tipo de framework que
o NestJS escreve em TypeScript: um `@Injetavel` que o contêiner
encontra, um `@Rota` que o roteador registra, um `@Coluna` que o ORM
mapeia — sem que nenhum deles precise de suporte no interpretador.

    @Rota("/itens", metodo: "GET")
    action listar():
        yield itens

    Meta.tem(listar, "Rota")      # yes
    Meta.ler(listar, "Rota")      # {args: ["/itens"], kwargs: {...}}
    Meta.arg(listar, "Rota", 0)   # "/itens"
"""


def _registro(alvo):
    """Os metadados do alvo, ou uma lista vazia."""
    return list(getattr(alvo, "__metadados__", None) or [])


class ArcaneMeta:
    """Leitura e escrita de metadados de decorador."""

    # ── leitura ──

    @staticmethod
    def _todos(alvo):
        """Todos os decoradores do alvo, na ordem em que aparecem."""
        return _registro(alvo)

    @staticmethod
    def _nomes(alvo):
        """Só os nomes: ["Injetavel", "Rota"]."""
        return [m["nome"] for m in _registro(alvo)]

    @staticmethod
    def _tem(alvo, nome):
        """O alvo foi decorado com @nome?"""
        return any(m["nome"] == nome for m in _registro(alvo))

    @staticmethod
    def _ler(alvo, nome):
        """O primeiro @nome do alvo, ou void.

        Devolve `{"nome", "args", "kwargs"}`. Um decorador repetido —
        `@Rota("/a")` e `@Rota("/b")` na mesma ação — é caso de `todos`.
        """
        for m in _registro(alvo):
            if m["nome"] == nome:
                return dict(m)
        return None

    @staticmethod
    def _todos_de(alvo, nome):
        """Todas as ocorrências de @nome. Para decorador repetível."""
        return [dict(m) for m in _registro(alvo) if m["nome"] == nome]

    @staticmethod
    def _arg(alvo, nome, indice=0, padrao=None):
        """Um argumento posicional de @nome, com padrão."""
        marca = ArcaneMeta._ler(alvo, nome)
        if marca is None:
            return padrao
        args = marca.get("args") or []
        return args[int(indice)] if int(indice) < len(args) else padrao

    @staticmethod
    def _opcao(alvo, nome, chave, padrao=None):
        """Um argumento nomeado de @nome, com padrão."""
        marca = ArcaneMeta._ler(alvo, nome)
        if marca is None:
            return padrao
        return (marca.get("kwargs") or {}).get(chave, padrao)

    # ── escrita ──

    @staticmethod
    def _marcar(alvo, nome, *args, **kwargs):
        """Anota o alvo sem usar a sintaxe de decorador.

        Serve para marcar algo que já existe — um valor vindo de outro
        módulo, por exemplo — e para escrever decoradores que anotam
        além do que receberam.
        """
        try:
            registro = getattr(alvo, "__metadados__", None)
            if registro is None:
                registro = []
                alvo.__metadados__ = registro
            registro.append({"nome": nome, "args": list(args),
                             "kwargs": dict(kwargs)})
        except (AttributeError, TypeError):
            return False
        return True

    @staticmethod
    def _limpar(alvo):
        """Remove todos os metadados. Útil em teste."""
        try:
            alvo.__metadados__ = []
            return True
        except (AttributeError, TypeError):
            return False

    # ── varredura ──

    @staticmethod
    def _filtrar(valores, nome):
        """De uma lista (ou vault) de valores, os que têm @nome.

        É como um contêiner de injeção acha o que registrar: varre o
        módulo e fica com o que foi anotado.
        """
        if isinstance(valores, dict):
            return {chave: valor for chave, valor in valores.items()
                    if ArcaneMeta._tem(valor, nome)}
        return [valor for valor in valores if ArcaneMeta._tem(valor, nome)]

    @staticmethod
    def _metodos_com(alvo, nome):
        """Os métodos de um blueprint anotados com @nome.

        Devolve `[{"nome": …, "metodo": …, "meta": …}]`, que é o
        suficiente para um roteador registrar rotas a partir de uma
        classe de controlador.
        """
        metodos = getattr(alvo, "methods", None)
        if not isinstance(metodos, dict):
            return []

        achados = []
        for chave, metodo in metodos.items():
            marca = ArcaneMeta._ler(metodo, nome)
            if marca is not None:
                achados.append({"nome": chave, "metodo": metodo,
                                "meta": marca})
        return achados

    @staticmethod
    def _descrever(alvo):
        """Tudo o que dá para saber do alvo, num vault.

        Para depurar: mostra tipo, nome, decoradores e — quando for um
        blueprint — os métodos e campos.
        """
        info = {
            "tipo": type(alvo).__name__,
            "nome": getattr(alvo, "name", None) or getattr(alvo, "__name__", "?"),
            "decoradores": ArcaneMeta._nomes(alvo),
        }
        metodos = getattr(alvo, "methods", None)
        if isinstance(metodos, dict):
            info["metodos"] = sorted(metodos)
        campos = getattr(alvo, "fields_decl", None)
        if campos:
            info["campos"] = [c[0] for c in campos]
        params = getattr(alvo, "params", None)
        if params:
            info["parametros"] = list(params)
        return info

    def __new__(cls):
        return {
            "__name__": "Arcane.Meta",

            # leitura
            "todos": cls._todos,
            "nomes": cls._nomes,
            "tem": cls._tem,
            "ler": cls._ler,
            "todos_de": cls._todos_de,
            "arg": cls._arg,
            "opcao": cls._opcao,

            # escrita
            "marcar": cls._marcar,
            "limpar": cls._limpar,

            # varredura
            "filtrar": cls._filtrar,
            "metodos_com": cls._metodos_com,
            "descrever": cls._descrever,
        }
