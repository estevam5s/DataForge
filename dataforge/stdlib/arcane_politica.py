# -*- coding: utf-8 -*-
"""Arcane.Politica — quem pode o quê, e por quê.

    adopt Arcane.Politica as P

    pol := P.motor("loja")
    pol.papel("editor", ["pedido:ler", "pedido:escrever"])
    pol.papel("admin", ["pedido:apagar"], herda := ["editor"])

    d := pol.pode({"papel": "editor"}, "pedido:apagar", pedido)
    out d["permitido"]      // no
    out d["motivo"]         // "nenhuma regra permitiu (padrao: negar)"

─── Por que um modulo, e nao um 'given' ────────────────────

Autorizacao escrita como `given usuario["papel"] is "admin":` espalha
a decisao por cinquenta arquivos. Quando a regra muda — e ela sempre
muda — nao ha onde olhar, e o que fica para tras nao da erro: fica
permitindo.

O que este modulo acrescenta nao e conveniencia, sao quatro garantias
que um `given` nao tem: o padrao e **negar**, a **negacao explicita
vence**, toda decisao **diz quem a tomou**, e a delegacao **vence**.

─── A decisao explica quem decidiu ─────────────────────────

`pode()` devolve um vault, e nao um booleano:

    {"permitido": no, "motivo": "negacao explicita de 'somente-dono'",
     "regra": "somente-dono", "sujeito": "…", "acao": "…"}

Um motor de politica que responde so `yes`/`no` e impossivel de
auditar e quase impossivel de depurar: o incidente pergunta *por que
ele conseguiu*, e a resposta e um encolher de ombros. O `motivo` e o
que vai para a trilha de auditoria.

─── As quatro regras, e o que cada uma evita ───────────────

| Regra | Sem ela |
|---|---|
| **padrao e negar** | uma acao nova nasce permitida para todo mundo |
| **negar vence permitir** | a excecao "este usuario nao" e apagada por um papel |
| **ninguem delega o que nao tem** | a cadeia de delegacoes cria autoridade do nada |
| **a delegacao tem prazo** | delegar vira conceder, com passos a mais |

─── O que ele NAO faz ──────────────────────────────────────

**Nao busca o sujeito nem o recurso.** Ele recebe os dois ja
carregados. Um motor que consulta o banco decidiria com dados que
quem chama nao viu, e o teste dele passaria a precisar de banco.

**Nao substitui a autorizacao por RECURSO na consulta.** Conferir
`pode(usuario, "pedido:ler", pedido)` depois de carregar o pedido
ainda carrega o pedido de outra pessoa. A defesa que funciona e a
consulta que ja filtra pelo dono — isto aqui e a segunda camada, nao
a primeira.

**Nao e distribuido.** As politicas vivem no processo. Num sistema com
varias instancias, quem decide continua sendo cada uma delas; o que
precisa ser comum e a FONTE (o banco de papeis), e nao o motor.
"""

import fnmatch
import threading
import time

from ..builtins import _df_type as _nome_do_tipo
from .opcoes import ler as _ler_opcoes

_DOC = "seguranca/autorizacao"


def _erro(mensagem, nota="", dica="", classe="AuthorizationError"):
    from .. import errors

    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _texto(valor, onde):
    if isinstance(valor, str):
        return valor
    raise _erro(
        f"'{onde}' espera um texto, e recebeu um {_nome_do_tipo(valor)}.",
        classe="AuthorizationError")


def _campo(alvo, nome, padrao=None):
    """Le um campo de vault, record ou instancia.

    A mesma indulgencia de `arcane_collections._campo_de`: o sujeito
    de uma politica e um vault num teste e um record em producao, e
    recusar um dos dois obrigaria a converter na fronteira.
    """
    if alvo is None:
        return padrao
    if isinstance(alvo, dict):
        return alvo.get(nome, padrao)
    valor = getattr(alvo, nome, None)
    if valor is not None:
        return valor
    ler = getattr(alvo, "get", None)
    if callable(ler):
        try:
            return ler(nome, padrao)
        except Exception:                                  # noqa: BLE001
            return padrao
    return padrao


def _casa(padrao, concreto):
    """`pedido:*` cobre `pedido:ler`; `pedido:ler` cobre so ele mesmo.

    O curinga e EXPLICITO: quem escreve `pedido:*` esta dizendo "todas
    as acoes deste recurso, inclusive as que ainda nao existem". Uma
    permissao que crescesse sozinha sem alguem ter escrito o `*` e
    como uma acao nova nasce permitida.
    """
    return padrao == concreto or fnmatch.fnmatchcase(concreto, padrao)


# ═══════════════════════════════════════════════════════════
#  A decisao
# ═══════════════════════════════════════════════════════════

def _decisao(permitido, motivo, regra="", extra=None):
    d = {"permitido": bool(permitido), "motivo": motivo, "regra": regra}
    if extra:
        d.update(extra)
    return d


# ═══════════════════════════════════════════════════════════
#  Papeis, grupos e a heranca
# ═══════════════════════════════════════════════════════════

class _Papel:
    __slots__ = ("nome", "permissoes", "herda")

    def __init__(self, nome, permissoes, herda):
        self.nome = nome
        self.permissoes = list(permissoes or [])
        self.herda = list(herda or [])


class _Politica:
    """O motor. Uma instancia por dominio de decisao.

    Ele guarda papeis, grupos, regras (ABAC), listas por objeto (ACL)
    e delegacoes — e `pode()` percorre tudo numa ordem que e o
    contrato do modulo, e nao um detalhe:

        1. a delegacao vencida e descartada;
        2. a NEGACAO explicita vence tudo;
        3. a ACL do objeto;
        4. a regra de atributo (ABAC);
        5. a permissao do papel (RBAC), com heranca;
        6. a delegacao;
        7. negar.

    A ordem importa porque as camadas discordam de proposito: a ACL
    existe para dizer "neste objeto, nao", e se o papel viesse antes
    ela nunca seria alcancada.
    """

    __slots__ = ("nome", "_papeis", "_grupos", "_regras", "_acl",
                 "_negacoes", "_delegacoes", "_trava", "_tenant")

    def __init__(self, nome, tenant=""):
        self.nome = str(nome)
        self._tenant = str(tenant or "")
        self._papeis = {}
        self._grupos = {}
        self._regras = []
        self._acl = {}
        self._negacoes = []
        self._delegacoes = []
        self._trava = threading.Lock()

    # ── Montagem ────────────────────────────────────────────

    def papel(self, nome, permissoes=None, herda=None):
        """Declara um papel. `herda` e uma lista de outros papeis."""
        n = _texto(nome, "papel")
        with self._trava:
            self._papeis[n] = _Papel(n, permissoes, herda)
        return self

    def grupo(self, nome, papeis=None, membros=None):
        """Um conjunto de papeis, e quem esta nele."""
        n = _texto(nome, "grupo")
        with self._trava:
            self._grupos[n] = {"papeis": list(papeis or []),
                               "membros": list(membros or [])}
        return self

    def regra(self, nome, condicao, acoes=None):
        """Uma regra de ATRIBUTO (ABAC), que decide olhando os valores.

        A condicao recebe `(sujeito, acao, recurso, contexto)` e
        devolve `yes`, `no` ou `void`. **`void` e "nao opino"** — e
        essa e a diferenca entre uma regra e um motor: uma regra que
        so soubesse dizer nao bloquearia tudo que ela nao entende.
        """
        with self._trava:
            self._regras.append({"nome": _texto(nome, "regra"),
                                 "condicao": condicao,
                                 "acoes": list(acoes or ["*"])})
        return self

    def negar(self, sujeito, acao, recurso=None, motivo=""):
        """Uma negacao EXPLICITA. Ela vence qualquer permissao.

        E o que torna possivel a excecao — "este usuario nao, apesar
        do papel dele". Sem prioridade sobre o permitir, a excecao
        seria apagada pelo papel e ninguem notaria.
        """
        with self._trava:
            self._negacoes.append({
                "sujeito": _identidade(sujeito), "acao": _texto(acao, "negar"),
                "recurso": _identidade(recurso) if recurso is not None else "*",
                "motivo": motivo or "negacao explicita"})
        return self

    def acl(self, recurso, sujeito, permissoes):
        """Lista de acesso POR OBJETO: quem pode o que naquele item."""
        chave = _identidade(recurso)
        with self._trava:
            self._acl.setdefault(chave, {})[_identidade(sujeito)] = list(permissoes)
        return self

    def delegar(self, de, para, permissoes, prazo=3600.0, quando=None):
        """`de` empresta permissoes a `para`, por um prazo.

        **Ninguem delega o que nao tem.** Sem essa conferencia, uma
        cadeia de delegacoes cria autoridade do nada: A delega a B algo
        que A nao pode, B delega a C, e C passa a poder.

        E o prazo e obrigatorio por desenho: delegacao sem prazo e
        concessao de permissao com passos a mais — e ninguem lembra de
        revogar.
        """
        agora = time.time() if quando is None else float(quando)
        faltando = [p for p in permissoes
                    if not self.pode(de, p, None)["permitido"]]
        if faltando:
            raise _erro(
                f"'{_identidade(de)}' nao pode delegar o que nao tem.",
                nota="sem estas permissoes: " + ", ".join(faltando),
                dica="Uma cadeia de delegacoes nao pode criar autoridade.",
                classe="DelegationError")
        with self._trava:
            self._delegacoes.append({
                "de": _identidade(de), "para": _identidade(para),
                "permissoes": list(permissoes), "vence": agora + float(prazo)})
        return self

    def revogar(self, para, acao=None):
        """Tira a delegacao antes do prazo."""
        alvo = _identidade(para)
        with self._trava:
            antes = len(self._delegacoes)
            self._delegacoes = [
                d for d in self._delegacoes
                if not (d["para"] == alvo
                        and (acao is None or acao in d["permissoes"]))]
            return antes - len(self._delegacoes)

    # ── A decisao ───────────────────────────────────────────

    def _permissoes_do_papel(self, nome, vistos=None):
        """As permissoes de um papel, mais as dos que ele herda.

        Devolve pares `(permissao, papel_de_origem)`: o motivo da
        decisao tem de nomear o papel que REALMENTE tem a permissao, e
        nao o que foi consultado. Com a heranca `admin → editor →
        leitor`, dizer "o papel 'admin' permite 'pedido:ler'" manda
        quem audita procurar a permissao num papel onde ela nao esta.

        `vistos` corta o ciclo: `admin herda editor herda admin` e um
        erro de configuracao que, sem isto, seria uma recursao infinita
        na primeira decisao — em producao, e nao no teste.
        """
        vistos = vistos or set()
        if nome in vistos:
            return []
        vistos.add(nome)
        papel = self._papeis.get(nome)
        if papel is None:
            return []
        saida = [(p, nome) for p in papel.permissoes]
        for mae in papel.herda:
            saida.extend(self._permissoes_do_papel(mae, vistos))
        return saida

    def _papeis_do_sujeito(self, sujeito):
        papeis = []
        um = _campo(sujeito, "papel")
        if um:
            papeis.append(str(um))
        muitos = _campo(sujeito, "papeis") or []
        papeis.extend(str(p) for p in muitos)

        eu = _identidade(sujeito)
        for nome, g in self._grupos.items():
            if eu in [str(m) for m in g["membros"]]:
                papeis.extend(str(p) for p in g["papeis"])
        return papeis

    def pode(self, sujeito, acao, recurso=None, contexto=None, quando=None):
        """A decisao, com o motivo. Nunca levanta."""
        a = _texto(acao, "pode")
        eu = _identidade(sujeito)
        agora = time.time() if quando is None else float(quando)
        base = {"sujeito": eu, "acao": a,
                "recurso": _identidade(recurso) if recurso is not None else ""}

        # Isolamento por inquilino, ANTES de tudo: um sujeito de outro
        # tenant nao existe para esta politica. Conferir isso depois
        # das permissoes faria um papel 'admin' atravessar a fronteira.
        if self._tenant:
            dele = str(_campo(sujeito, "tenant", "") or "")
            if dele and dele != self._tenant:
                return _decisao(False, f"sujeito e do inquilino '{dele}'",
                                "tenant", base)

        with self._trava:
            negacoes = list(self._negacoes)
            regras = list(self._regras)
            acl = dict(self._acl)
            delegacoes = list(self._delegacoes)

        # 1. NEGACAO EXPLICITA — vence tudo.
        alvo = _identidade(recurso) if recurso is not None else "*"
        for n in negacoes:
            if n["sujeito"] not in (eu, "*"):
                continue
            if not _casa(n["acao"], a):
                continue
            if n["recurso"] not in (alvo, "*"):
                continue
            return _decisao(False, n["motivo"], "negacao", base)

        # 2. ACL do objeto.
        if recurso is not None and alvo in acl:
            do_objeto = acl[alvo].get(eu)
            if do_objeto is not None:
                for p in do_objeto:
                    if _casa(p, a):
                        return _decisao(True, f"a lista do objeto '{alvo}' permite",
                                        "acl", base)
                return _decisao(False, f"a lista do objeto '{alvo}' nao inclui '{a}'",
                                "acl", base)

        # 3. Regra de atributo (ABAC). 'void' e "nao opino".
        for r in regras:
            if not any(_casa(p, a) for p in r["acoes"]):
                continue
            try:
                resposta = _chamar(r["condicao"], sujeito, a, recurso, contexto)
            except Exception as erro:                      # noqa: BLE001
                # Uma regra que falha NAO permite. Tratar a excecao
                # como "nao opino" faria um bug virar autorizacao.
                return _decisao(False, f"a regra '{r['nome']}' falhou: {erro}",
                                r["nome"], base)
            if resposta is None:
                continue
            return _decisao(bool(resposta),
                            f"a regra '{r['nome']}' "
                            + ("permitiu" if resposta else "negou"),
                            r["nome"], base)

        # 4. Papel (RBAC), com heranca.
        for nome in self._papeis_do_sujeito(sujeito):
            for p, dono in self._permissoes_do_papel(nome):
                if _casa(p, a):
                    via = "" if dono == nome else f" (por '{nome}')"
                    return _decisao(True,
                                    f"o papel '{dono}' permite '{p}'{via}",
                                    f"papel:{dono}", base)

        # 5. Delegacao ainda no prazo.
        for d in delegacoes:
            if d["para"] != eu or d["vence"] <= agora:
                continue
            for p in d["permissoes"]:
                if _casa(p, a):
                    return _decisao(
                        True,
                        f"delegado por '{d['de']}' ate "
                        f"{int(d['vence'] - agora)}s a partir de agora",
                        "delegacao", base)

        # 6. O padrao.
        return _decisao(False, "nenhuma regra permitiu (padrao: negar)",
                        "padrao", base)

    def exigir(self, sujeito, acao, recurso=None, contexto=None):
        """O mesmo, levantando — para quem escreve o caminho feliz."""
        d = self.pode(sujeito, acao, recurso, contexto)
        if not d["permitido"]:
            raise _erro(
                f"'{d['sujeito']}' nao pode '{d['acao']}'.",
                nota=d["motivo"],
                dica="Responda 404 quando a existencia do recurso ja e "
                     "informacao; 403 so quando ela ja e publica.",
                classe="AuthorizationError")
        return True

    def explicar(self, sujeito, acao, recurso=None, contexto=None):
        """Todas as camadas, e o que cada uma responderia.

        E a ferramenta de depuracao do motor: `pode()` para na
        primeira que decide, e quando a resposta surpreende o que se
        quer saber e o que as OUTRAS teriam dito.
        """
        d = self.pode(sujeito, acao, recurso, contexto)
        eu = _identidade(sujeito)
        return {
            "decisao": d,
            "papeis": self._papeis_do_sujeito(sujeito),
            "permissoes": sorted({p for nome in self._papeis_do_sujeito(sujeito)
                                  for p, _ in self._permissoes_do_papel(nome)}),
            "negacoes": [n for n in self._negacoes
                         if n["sujeito"] in (eu, "*")],
            "delegacoes": [dd for dd in self._delegacoes if dd["para"] == eu],
            "regras": [r["nome"] for r in self._regras],
        }

    def permissoes_de(self, sujeito):
        """Tudo que o sujeito alcanca hoje, por papel ou delegacao."""
        agora = time.time()
        saida = set()
        for nome in self._papeis_do_sujeito(sujeito):
            saida.update(p for p, _ in self._permissoes_do_papel(nome))
        eu = _identidade(sujeito)
        for d in self._delegacoes:
            if d["para"] == eu and d["vence"] > agora:
                saida.update(d["permissoes"])
        return sorted(saida)

    def papeis(self):
        return sorted(self._papeis)

    def auditar(self):
        """O que a politica tem hoje — para revisao, e para o relatorio.

        Uma politica que ninguem consegue LER envelhece com permissoes
        que ninguem lembra por que existem.
        """
        return {
            "politica": self.nome,
            "inquilino": self._tenant,
            "papeis": {n: {"permissoes": p.permissoes, "herda": p.herda}
                       for n, p in self._papeis.items()},
            "grupos": dict(self._grupos),
            "regras": [r["nome"] for r in self._regras],
            "negacoes": len(self._negacoes),
            "objetos_com_lista": len(self._acl),
            "delegacoes_vivas": sum(1 for d in self._delegacoes
                                    if d["vence"] > time.time()),
        }


def _identidade(alvo):
    """Quem e este sujeito, ou qual e este recurso.

    Ordem: 'id', depois 'email', depois 'nome' — e por fim o texto.
    Sem uma identidade estavel, a ACL e a delegacao apontariam para
    objetos diferentes a cada pedido.
    """
    if alvo is None:
        return ""
    if isinstance(alvo, (str, int)):
        return str(alvo)
    for campo in ("id", "email", "nome", "identidade"):
        valor = _campo(alvo, campo)
        if valor is not None:
            return str(valor)
    return str(alvo)


#: A condicao recebe, nesta ordem, o que ela declarar.
#:
#: Uma regra costuma olhar so o sujeito e o recurso; obrigar as quatro
#: faria toda regra ter dois parametros ignorados, e um parametro
#: ignorado e onde um erro de ordem se esconde.
_ARGUMENTOS_DA_REGRA = ("sujeito", "acao", "recurso", "contexto")


def _aridade(condicao):
    """Quantos parametros a acao declara — perguntando, nao tentando.

    A primeira versao chamava com quatro argumentos e, no
    `TypeError`, tentava com tres. Isso NAO funciona aqui: uma
    `DFAction` levanta `TypeError_` da linguagem, que nao e o
    `TypeError` do Python — e o erro caia no `except Exception` de
    quem chama, virando "a regra falhou" e, com ele, uma NEGACAO.

    Uma regra correta era recusada porque o motor errou a chamada, e
    o sintoma era uma permissao que nunca vinha. Perguntar a aridade
    e o unico jeito que nao depende de adivinhar a forma do erro.
    """
    declarados = getattr(condicao, "params", None)
    if declarados is not None:
        try:
            return max(1, min(4, len(declarados)))
        except TypeError:
            pass
    try:
        import inspect

        positivos = [
            p for p in inspect.signature(condicao).parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
        ]
        return max(1, min(4, len(positivos)))
    except (TypeError, ValueError):
        # Um chamavel que nao se deixa inspecionar recebe os quatro:
        # e o contrato completo, e quem escreveu assim sabe disso.
        return 4


def _chamar(condicao, sujeito, acao, recurso, contexto):
    """Chama a condicao com exatamente os argumentos que ela declara."""
    todos = (sujeito, acao, recurso, contexto)
    return condicao(*todos[:_aridade(condicao)])


# ═══════════════════════════════════════════════════════════
#  Atalhos de alto nivel
# ═══════════════════════════════════════════════════════════

_DE_VAULT = {"papeis": {}, "grupos": {}, "negacoes": [], "inquilino": ""}


def _de_vault(nome, definicao):
    """Monta a politica de um vault — o que sai de um arquivo ou banco.

    E o caminho que importa em producao: a politica nao e escrita em
    codigo, ela e CARREGADA. Mudar quem pode o que nao pode exigir
    deploy.
    """
    d = dict(_DE_VAULT)
    d.update(_ler_opcoes(definicao, _DE_VAULT, "Politica.de_vault"))
    pol = _Politica(nome, d.get("inquilino", ""))
    for papel, corpo in (d.get("papeis") or {}).items():
        if isinstance(corpo, dict):
            pol.papel(papel, corpo.get("permissoes"), corpo.get("herda"))
        else:
            pol.papel(papel, corpo)
    for grupo, corpo in (d.get("grupos") or {}).items():
        pol.grupo(grupo, (corpo or {}).get("papeis"), (corpo or {}).get("membros"))
    for n in d.get("negacoes") or []:
        pol.negar(n.get("sujeito", "*"), n.get("acao", "*"),
                  n.get("recurso"), n.get("motivo", ""))
    return pol


def _separacao_de_funcoes(politica, acao, solicitante, aprovador):
    """Quem solicita nao aprova — e a conferencia e uma so.

    Escrita a mao em cada fluxo, ela e esquecida em um deles; e o um
    e o que vira a fraude.
    """
    if _identidade(solicitante) == _identidade(aprovador):
        raise _erro(
            "quem solicita nao aprova.",
            nota=f"'{_identidade(solicitante)}' pediu e tentou aprovar '{acao}'.",
            dica="Separacao de funcoes: dois pares de olhos na mesma acao.",
            classe="AuthorizationError")
    politica.exigir(aprovador, acao)
    return True


class ArcanePolitica(dict):
    """O vault que o 'adopt' entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Politica",

            #: Chama-se 'motor', e nao 'politica', de proposito:
            #: 'Arcane.Seguranca.politica' ja existe e responde outra
            #: pergunta — se uma SENHA atende a politica. Dois nomes
            #: iguais para conceitos diferentes fazem quem le o codigo
            #: seis meses depois presumir a resposta errada, e ha teste
            #: proibindo a colisao entre os dois modulos.
            #:
            #: E 'motor' e mais preciso sobre o que volta: um motor de
            #: decisao, e nao um documento de politica.
            "motor": lambda nome, inquilino="": _Politica(nome, inquilino),
            "de_vault": _de_vault,

            "identidade": _identidade,
            "casa": _casa,
            "separacao_de_funcoes": _separacao_de_funcoes,

            #: As camadas, na ordem em que 'pode()' as percorre. A
            #: ordem e contrato: a ACL existe para dizer "neste objeto,
            #: nao", e se o papel viesse antes ela nunca seria
            #: alcancada.
            "camadas": lambda: ["tenant", "negacao", "acl", "regra",
                                "papel", "delegacao", "padrao"],
        }
