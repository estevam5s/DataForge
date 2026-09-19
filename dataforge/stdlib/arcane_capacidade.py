# -*- coding: utf-8 -*-
"""Arcane.Capacidade — a fronteira de autoridade, e o que ela NÃO é.

O que faltava
-------------
O `comptime` já recusava `out`, `adopt`, `thread` e `parallel`: é uma
fronteira de capacidade escrita à mão, para um caso só. E o
[`--plugin=`](/docs/metaprogramacao/plugins) roda um `.df` arbitrário do
projeto com **todos** os poderes — uma regra de lint que pode abrir
soquete.

    adopt Arcane.Capacidade as Cap

    // a formula do usuario calcula, e so
    Cap.executar(formula_do_usuario, [])

    // o relatorio le arquivo, e nao fala com a rede
    Cap.executar(gerar_relatorio, ["arquivos"])

O que ele é, com precisão
-------------------------
Uma fronteira de **autoridade ambiente**: o código dentro dela não
consegue **alcançar** um módulo fora da lista. `adopt Arcane.IO` é
recusado pelo nome da capacidade que falta, e não por um erro genérico.

O que ele NÃO é, e isto é mais importante
-----------------------------------------
**Não é uma caixa contra um programa hostil.** Três coisas verdadeiras:

1. **Ele não tira o que foi ENTREGUE.** Se você passa o módulo `IO` como
   argumento, o código tem `IO`. Isso não é um furo: é o modelo. Numa
   linguagem de capacidade, poder é o que se **passa**, não o que está
   no ar — e é por isso que bloquear o `adopt` é a fronteira certa.

2. **A ponte para o Python é uma capacidade à parte**, e bloqueada por
   padrão: `adopt Python.os` alcança tudo o que o Python alcança, e
   deixá-la junto de qualquer outra permissão faria o resto da lista
   virar enfeite.

3. **Um erro na lista é um furo**, e a lista é escrita à mão. Contra
   código que você escreveu e revisou — plugin, fórmula de usuário,
   `comptime` — isto vale. Contra código que alguém quer que rode na sua
   máquina, **não use isto**: use um processo separado, um contêiner, ou
   o sistema operacional.

Escrito assim porque a alternativa é pior: um módulo que se chamasse
`Sandbox` e prometesse contenção seria usado onde não pode ser usado, e
a descoberta viria por incidente.
"""

from ..errors import RuntimeError_

#: As capacidades, com o que cada uma libera. A descrição é a
#: documentação, e há teste cobrando o tamanho dela.
CAPACIDADES = {
    "arquivos": "ler e escrever no disco: Arcane.IO, Arcane.Archive, "
                "Arcane.Excel, Arcane.ArquivoSeguro, Arcane.Lago",
    "rede": "falar com a rede: Arcane.Http, Arcane.Rede, Arcane.Web, "
            "Arcane.Email, Arcane.Malha, Arcane.Kiln, Arcane.Vitrine",
    "processo": "o sistema e outros processos: Arcane.OS, Arcane.Process",
    "ambiente": "variáveis de ambiente e argumentos da linha de comando",
    "banco": "bancos de dados e o que persiste: Arcane.Database, "
             "Arcane.Forge, Arcane.Eventos com fila persistente",
    "threads": "abrir thread, processo e laço de eventos: Arcane.Concurrent, "
               "Arcane.Async, Arcane.Laco, Arcane.Stm",
    "nativo": "biblioteca nativa e ponteiro cru: Arcane.C — memória sem "
              "rede de proteção, e a fronteira mais insegura que existe aqui",
    "python": "a ponte para o Python, que alcança TUDO o que o Python "
              "alcança. É capacidade própria por isso, e nunca vem junto",
}

#: Módulo -> capacidade exigida. Só o que carrega autoridade entra: um
#: `Arcane.Math` bloqueado não protege nada e quebra o caso comum.
_EXIGE = {
    "Arcane.IO": "arquivos", "IO": "arquivos",
    "Arcane.Archive": "arquivos", "Archive": "arquivos", "Zip": "arquivos",
    "Arcane.Excel": "arquivos", "Excel": "arquivos", "Xls": "arquivos",
    "Arcane.ArquivoSeguro": "arquivos", "ArquivoSeguro": "arquivos",
    "Arcane.Lago": "arquivos", "Lago": "arquivos",

    "Arcane.Http": "rede", "Http": "rede",
    "Arcane.Rede": "rede", "Rede": "rede", "Net": "rede",
    "Arcane.Web": "rede", "Web": "rede",
    "Arcane.Email": "rede", "Email": "rede",
    "Arcane.Malha": "rede", "Malha": "rede",
    "Arcane.Kiln": "rede", "Kiln": "rede",
    "Arcane.Vitrine": "rede", "Vitrine": "rede",

    "Arcane.OS": "processo", "OS": "processo",
    "Arcane.Process": "processo", "Process": "processo",

    "Arcane.Database": "banco", "Database": "banco", "Banco": "banco",
    "Arcane.Forge": "banco", "Forge": "banco",

    "Arcane.Concurrent": "threads", "Concurrent": "threads",
    "Arcane.Async": "threads", "Async": "threads",
    "Arcane.Laco": "threads", "Laco": "threads", "Reator": "threads",
    "Arcane.Stm": "threads", "Stm": "threads", "Transacional": "threads",

    "Arcane.C": "nativo", "C": "nativo", "Nativo": "nativo",
}


class _Fronteira:
    """O estado de um cofre aberto: o que foi permitido, e o que foi negado."""

    __slots__ = ("permitidas", "negados")

    def __init__(self, permitidas):
        self.permitidas = permitidas
        self.negados = []


def _exigida(nome_modulo):
    """A capacidade que este módulo pede, ou `None` se ele é inofensivo."""
    if nome_modulo.startswith("Python.") or nome_modulo == "Python":
        return "python"
    if nome_modulo in _EXIGE:
        return _EXIGE[nome_modulo]
    # Um `.df` vizinho não é módulo da biblioteca: ele é código do
    # projeto, e o que ELE adotar passa pela mesma fronteira.
    return None


def _conferir_lista(permissoes):
    pedidas = [str(p) for p in (permissoes or [])]
    desconhecidas = [p for p in pedidas if p not in CAPACIDADES]
    if desconhecidas:
        raise RuntimeError_(
            f"unknown capability: {', '.join(sorted(desconhecidas))}. "
            f"The capabilities are: {', '.join(sorted(CAPACIDADES))}. "
            f"A typo here would silently grant nothing, so it is refused.",
            doc="seguranca/capacidade")
    return set(pedidas)


def _abrir(interp, permitidas):
    """Sombreia a resolução de módulo — o mesmo truque do depurador.

    Sombrear é o que torna a fronteira de custo zero fora dela: sem
    cofre aberto, `_resolver_modulo` é o método da classe, sem nenhuma
    conferência no caminho.
    """
    fronteira = _Fronteira(permitidas)
    original = interp._resolver_modulo

    def guardado(nome_modulo, node, env):
        exigida = _exigida(nome_modulo)
        if exigida is not None and exigida not in fronteira.permitidas:
            fronteira.negados.append({
                "modulo": nome_modulo,
                "capacidade": exigida,
                "linha": getattr(node, "line", 0),
            })
            raise RuntimeError_(
                f"'{nome_modulo}' needs the '{exigida}' capability, and this "
                f"vault did not grant it.",
                getattr(node, "line", 0), getattr(node, "column", 0),
                nota=CAPACIDADES[exigida],
                dica=f"grant it: Cap.executar(acao, [\"{exigida}\"])",
                doc="seguranca/capacidade")
        return original(nome_modulo, node, env)

    interp._resolver_modulo = guardado
    return fronteira, original


def _fechar(interp):
    """Devolve o método da classe — `del`, e não reatribuição.

    Reatribuir criaria de novo um atributo de instância, e o
    interpretador sairia do cofre carregando uma indireção que não
    tinha antes. É a mesma razão do `desligar` do depurador.
    """
    try:
        del interp._resolver_modulo
    except AttributeError:                      # pragma: no cover
        pass


def _interp():
    from ..interpreter import DFAction

    interp = DFAction._interpreter
    if interp is None:                          # pragma: no cover
        raise RuntimeError_("Capacidade needs a running interpreter.",
                            doc="seguranca/capacidade")
    return interp


def executar(acao, permissoes=None, argumentos=None):
    """Roda a ação com estas capacidades, e só estas.

    O que a ação **recebe** continua sendo dela: capacidade é o que o
    código alcança sozinho, não o que lhe foi passado.
    """
    permitidas = _conferir_lista(permissoes)
    interp = _interp()
    _fronteira, _original = _abrir(interp, permitidas)
    try:
        return acao(*list(argumentos or []))
    finally:
        # Um cofre que não se desfaz trava o programa inteiro — e o
        # 'finally' é o que garante isso inclusive quando o corpo falha.
        _fechar(interp)


def observar(acao, permissoes=None, argumentos=None):
    """O mesmo, devolvendo também o que foi negado.

    Serve para descobrir de que uma ação precisa: rode com a lista
    vazia, leia os negados, e conceda o que fizer sentido.
    """
    permitidas = _conferir_lista(permissoes)
    interp = _interp()
    fronteira, _original = _abrir(interp, permitidas)
    erro = None
    resultado = None
    try:
        resultado = acao(*list(argumentos or []))
    except Exception as falha:                  # noqa: BLE001
        erro = falha
    finally:
        _fechar(interp)
    return {
        "resultado": resultado,
        "negados": fronteira.negados,
        "permitidas": sorted(permitidas),
        "falhou": erro is not None,
        "erro": str(erro) if erro is not None else "",
    }


def capacidades():
    """As capacidades, com o que cada uma libera."""
    return dict(CAPACIDADES)


def exige(nome_modulo):
    """Que capacidade este módulo pede? `void` quando é inofensivo."""
    return _exigida(str(nome_modulo))


def modulos_de(capacidade):
    """Que módulos esta capacidade libera."""
    alvo = str(capacidade)
    if alvo not in CAPACIDADES:
        raise RuntimeError_(
            f"unknown capability '{alvo}'. The capabilities are: "
            f"{', '.join(sorted(CAPACIDADES))}.", doc="seguranca/capacidade")
    return sorted({nome for nome, cap in _EXIGE.items() if cap == alvo})


def limites():
    """O que este módulo NÃO faz. Lido em voz alta, de propósito."""
    return [
        "Isto não é uma caixa contra programa hostil, e não deve ser "
        "usado como tal.",
        "Ele não tira o que foi ENTREGUE: passar o módulo é passar o "
        "poder junto. Isso é o modelo de capacidade, não um defeito.",
        "A ponte para o Python é capacidade própria porque alcança tudo "
        "o que o Python alcança — e nunca vem junto de outra.",
        "A lista de módulos é escrita à mão, e um erro nela é um furo. "
        "Contra código malicioso, use processo separado, contêiner ou o "
        "sistema operacional.",
    ]


class ArcaneCapacidade:
    """O dicionário que `adopt Arcane.Capacidade` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Capacidade",
            "executar": executar,
            "observar": observar,
            "capacidades": capacidades,
            "exige": exige,
            "modulos_de": modulos_de,
            "limites": limites,
        }
