"""
dataforge oop — metricas de orientacao a objeto e os cheiros que elas revelam.

Le a arvore, sem executar nada, e mede cada blueprint pelas metricas de
Chidamber e Kemerer — as que a literatura de engenharia de software usa
desde 1994 para prever onde os defeitos vao aparecer:

    WMC   soma da complexidade ciclomatica dos metodos
    DIT   profundidade na arvore de heranca
    NOC   filhas diretas
    CBO   acoplamento: com quantos outros tipos ele conversa
    RFC   resposta: metodos proprios + metodos que ele chama
    LCOM  falta de coesao (0 = coeso, 1 = cada metodo mexe no seu campo)

e mais fan-in/fan-out, a instabilidade de Martin (Ce / (Ca + Ce)) e o
indice de manutenibilidade.

─── Numero sozinho nao diz nada ────────────────────────────────

"CBO 12" nao ensina a melhorar. Por isso cada limite ultrapassado vira
um CHEIRO com nome, o principio que ele fere, o porque e o que fazer —
e os limites estao numa tabela so ('LIMITES'), porque sao opiniao, e
opiniao escrita em um lugar e discutivel; espalhada, nao.

Os cheiros sao SUGESTOES. Um blueprint que agrega e roteia pode ter CBO
alto de proposito. O comando sai com 0 mesmo com cheiros, a menos que
se peca '--strict' — e ai quem pediu decidiu que o limite e regra.
"""

import math
import os

from . import ast_nodes as ast


#: Os limites dos cheiros. Opiniao, num lugar so.
LIMITES = {
    "metodos": 20,          # God blueprint
    "loc": 400,
    "wmc": 50,
    "dit": 4,               # heranca funda
    "cbo": 10,              # acoplamento excessivo
    "lcom": 0.8,            # falta de coesao (com metodos e campos suficientes)
    "parametros": 5,        # parametros demais
    "linhas_do_metodo": 50,  # metodo longo
    "assinaturas": 7,       # contrato gordo (ISP)
    "ramos_de_tipo": 3,     # 'given typeof(x) is …' em cadeia (OCP)
}

_CONSTRUTORES = ("setup", "initiate", "__init__")


# ═════════════════════════════════════════════════════════════
#  Coleta
# ═════════════════════════════════════════════════════════════

class Tipo:
    """Um blueprint, contrato ou trait, com o que se mediu dele."""

    def __init__(self, no, arquivo, especie, dono=None):
        self.no = no
        self.nome = no.name
        self.arquivo = arquivo
        self.especie = especie              # blueprint | contract | trait | meta
        self.dono = dono                    # blueprint de fora, se aninhado
        self.maes = [p.rsplit(".", 1)[-1] for p in getattr(no, "parents", []) or []]
        self.contratos = [t.rsplit(".", 1)[-1] for t in getattr(no, "traits", []) or []]
        self.metodos = []
        self.campos = set()
        self.filhas = []
        self.referencias = set()            # tipos citados (CBO de saida)
        self.chamadas = set()               # metodos chamados em outros objetos
        self.cheiros = []
        self.metricas = {}


def _andar(no):
    """Todos os nos abaixo deste, em profundidade."""
    pilha = [no]
    while pilha:
        atual = pilha.pop()
        if isinstance(atual, ast.ASTNode):
            yield atual
            for chave, valor in vars(atual).items():
                if not chave.startswith("_"):
                    pilha.append(valor)
        elif isinstance(atual, (list, tuple)):
            pilha.extend(atual)
        elif isinstance(atual, dict):
            pilha.extend(atual.values())


def _ultima_linha(no):
    return max((getattr(n, "line", 0) or 0 for n in _andar(no)), default=no.line)


def complexidade_ciclomatica(corpo):
    """1 + cada ponto de decisao: given/orif, lacos, match, handle, and/or, ternario."""
    total = 1
    for n in _andar(corpo):
        nome = type(n).__name__
        if nome == "GivenBlock":
            total += 1 + len(getattr(n, "orif_blocks", []) or [])
        elif nome in ("CycleFromTo", "CycleIn", "PersistBlock", "PerformBlock",
                      "TernaryExpression", "CoalesceOp", "RetryBlock"):
            total += 1
        elif nome == "MatchBlock":
            total += max(1, len(getattr(n, "points", []) or []))
        elif nome == "MonitorBlock":
            total += len(getattr(n, "handles", None) or [1])
        elif nome == "LogicalOp":
            total += 1
    return total


def _nomes_de_tipo(texto):
    """'Cluster' → nada; 'Pedido' → {'Pedido'}; 'M.Pedido' → {'Pedido'}."""
    if not texto:
        return set()
    base = str(texto).rsplit(".", 1)[-1]
    if base in _EMBUTIDOS:
        return set()
    return {base} if base[:1].isupper() else set()


#: Tipos da linguagem: acoplar-se a 'String' nao e acoplamento.
_EMBUTIDOS = frozenset({
    "Integer", "Float", "String", "Boolean", "Cluster", "Vault", "Record",
    "Any", "Void", "Action", "Stream", "Frame", "Server", "Number", "Set",
    "Bytes", "Complex", "Decimal", "Error", "Task", "Channel", "Blueprint",
    "Enum", "Tuple", "Date", "DateTime",
})


def coletar(arquivos):
    """{nome: Tipo} de todos os arquivos, e os problemas de leitura."""
    from .lexer import tokenize
    from .parser import parse
    from .errors import DataForgeError

    tipos, problemas, fontes = {}, [], {}
    for caminho in arquivos:
        try:
            with open(caminho, encoding="utf-8") as f:
                fonte = f.read()
            arvore = parse(tokenize(fonte, caminho), caminho)
        except (OSError, UnicodeDecodeError) as erro:
            problemas.append((caminho, str(erro)))
            continue
        except DataForgeError as erro:
            problemas.append((caminho, erro.message))
            continue
        fontes[caminho] = fonte
        for no in _andar(arvore):
            if isinstance(no, ast.BlueprintDeclaration):
                especie = "meta" if getattr(no, "is_meta", False) else "blueprint"
                tipos.setdefault(no.name, Tipo(no, caminho, especie))
            elif isinstance(no, ast.ContractDeclaration):
                tipos.setdefault(no.name, Tipo(no, caminho, "contract"))
            elif isinstance(no, ast.TraitDeclaration):
                tipos.setdefault(no.name, Tipo(no, caminho, "trait"))
    for tipo in tipos.values():
        _medir_membros(tipo, tipos)
    for tipo in tipos.values():
        for mae in tipo.maes + tipo.contratos:
            if mae in tipos:
                tipos[mae].filhas.append(tipo.nome)
    return tipos, problemas, fontes


def _medir_membros(tipo, tipos):
    no = tipo.no
    if tipo.especie == "contract":
        tipo.metodos = [m for m in no.members if isinstance(m, ast.ActionDeclaration)]
        return
    corpo = no.body if isinstance(no, ast.BlueprintDeclaration) else no.methods
    for membro in corpo:
        if isinstance(membro, ast.ActionDeclaration):
            tipo.metodos.append(membro)
        elif isinstance(membro, ast.Assignment) and isinstance(membro.target, ast.Identifier):
            tipo.campos.add(membro.target.name)
    if isinstance(no, ast.BlueprintDeclaration):
        tipo.campos |= set(no.constructor_params or [])
        tipo.campos |= {c[0] for c in no.fields_decl or []}
        for campo in no.fields_decl or []:
            tipo.referencias |= _nomes_de_tipo(campo[1])
        for t in (getattr(no, "constructor_types", None) or {}).values():
            tipo.referencias |= _nomes_de_tipo(t)
    tipo.referencias |= set(tipo.maes) | set(tipo.contratos)
    for metodo in tipo.metodos:
        for t in (metodo.param_types or {}).values():
            tipo.referencias |= _nomes_de_tipo(t)
        tipo.referencias |= _nomes_de_tipo(metodo.return_type)
        for n in _andar(metodo.body):
            if isinstance(n, ast.Assignment) and isinstance(n.target, ast.MemberAccess) \
                    and isinstance(n.target.object, ast.Identifier) \
                    and n.target.object.name in ("self", "this"):
                tipo.campos.add(n.target.member)
            if isinstance(n, ast.SpawnExpression) and isinstance(n.class_name, ast.Identifier):
                tipo.referencias.add(n.class_name.name)
            if isinstance(n, ast.Identifier) and n.name in tipos and n.name != tipo.nome:
                tipo.referencias.add(n.name)
            if isinstance(n, ast.MethodCall) and not (
                    isinstance(n.object, ast.Identifier)
                    and n.object.name in ("self", "this")):
                tipo.chamadas.add(n.method)
    tipo.referencias.discard(tipo.nome)


# ═════════════════════════════════════════════════════════════
#  Metricas
# ═════════════════════════════════════════════════════════════

def _campos_usados(metodo, campos):
    usados = set()
    for n in _andar(metodo.body):
        if isinstance(n, ast.MemberAccess) and isinstance(n.object, ast.Identifier) \
                and n.object.name in ("self", "this") and n.member in campos:
            usados.add(n.member)
    return usados


def lcom(tipo):
    """LCOM* de Henderson-Sellers: 0 coeso, 1 sem coesao nenhuma."""
    metodos = [m for m in tipo.metodos if m.name not in _CONSTRUTORES
               and not m.name.startswith("__")]
    campos = tipo.campos
    if len(metodos) < 2 or not campos:
        return 0.0
    uso = {c: 0 for c in campos}
    for m in metodos:
        for c in _campos_usados(m, campos):
            uso[c] += 1
    media = sum(uso.values()) / len(campos)
    k = len(metodos)
    return round(max(0.0, min(1.0, (media - k) / (1 - k))), 2)


def _dit(nome, tipos, vistos=None):
    vistos = vistos or set()
    if nome in vistos:
        return 0
    vistos.add(nome)
    tipo = tipos.get(nome)
    if tipo is None:
        return 1                       # mae de outro lugar: pelo menos um nivel
    if not tipo.maes:
        return 0
    return 1 + max(_dit(m, tipos, vistos) for m in tipo.maes)


def _halstead_volume(fonte, inicio, fim):
    from .lexer import tokenize
    trecho = "\n".join(fonte.split("\n")[inicio - 1:fim])
    try:
        tokens = [t for t in tokenize(trecho, "<oop>")
                  if t.type.name not in ("NEWLINE", "INDENT", "DEDENT", "EOF")]
    except Exception:                      # noqa: BLE001 — trecho solto pode nao tokenizar
        palavras = trecho.split()
        return len(palavras) * math.log2(max(2, len(set(palavras))))
    distintos = {(t.type, str(t.value)) for t in tokens}
    return len(tokens) * math.log2(max(2, len(distintos)))


def medir(tipos, fontes):
    entrada = {nome: 0 for nome in tipos}
    for tipo in tipos.values():
        for ref in tipo.referencias:
            if ref in entrada:
                entrada[ref] += 1
    for tipo in tipos.values():
        no = tipo.no
        fim = _ultima_linha(no)
        loc = fim - no.line + 1
        wmc = sum(complexidade_ciclomatica(m.body) for m in tipo.metodos)
        conhecidos = {r for r in tipo.referencias if r in tipos}
        ce = len(tipo.referencias)
        ca = entrada[tipo.nome]
        hv = _halstead_volume(fontes.get(tipo.arquivo, ""), no.line, fim)
        mi = 171 - 5.2 * math.log(max(hv, 1)) - 0.23 * wmc - 16.2 * math.log(max(loc, 1))
        tipo.metricas = {
            "loc": loc,
            "metodos": len(tipo.metodos),
            "campos": len(tipo.campos),
            "wmc": wmc,
            "dit": _dit(tipo.nome, tipos),
            "noc": len(tipo.filhas),
            "cbo": ce,
            "rfc": len(tipo.metodos) + len(tipo.chamadas),
            "lcom": lcom(tipo),
            "fan_in": ca,
            "fan_out": ce,
            "instabilidade": round(ce / (ca + ce), 2) if (ca + ce) else 0.0,
            "manutenibilidade": round(max(0.0, mi * 100 / 171), 1),
            "acoplados": sorted(conhecidos),
        }


# ═════════════════════════════════════════════════════════════
#  Cheiros
# ═════════════════════════════════════════════════════════════

def _cheiro(tipo, codigo, principio, mensagem, dica, linha=None):
    tipo.cheiros.append({
        "codigo": codigo, "principio": principio, "mensagem": mensagem,
        "dica": dica, "linha": linha or tipo.no.line,
    })


def cheirar(tipos, limites=None):
    L = {**LIMITES, **(limites or {})}
    for tipo in tipos.values():
        m = tipo.metricas
        if tipo.especie in ("contract", "trait"):
            if len(tipo.metodos) > L["assinaturas"]:
                _cheiro(tipo, "contrato-gordo", "ISP",
                        f"'{tipo.nome}' exige {len(tipo.metodos)} metodos",
                        "quebre em contratos pequenos, um por cliente — quem "
                        "so le nao deveria implementar 'salvar'")
            continue

        if m["metodos"] > L["metodos"] or m["loc"] > L["loc"] or m["wmc"] > L["wmc"]:
            _cheiro(tipo, "god-blueprint", "SRP",
                    f"'{tipo.nome}' tem {m['metodos']} metodos, {m['loc']} linhas "
                    f"e WMC {m['wmc']}",
                    "separe as responsabilidades: o que muda por motivos "
                    "diferentes mora em blueprints diferentes")
        if m["dit"] > L["dit"]:
            _cheiro(tipo, "heranca-funda", "composicao sobre heranca",
                    f"'{tipo.nome}' esta {m['dit']} niveis abaixo da raiz",
                    "cada nivel e uma mae que pode quebrar a filha; troque "
                    "niveis por campos que guardam o comportamento")
        if m["cbo"] > L["cbo"]:
            _cheiro(tipo, "acoplamento-excessivo", "baixo acoplamento",
                    f"'{tipo.nome}' conversa com {m['cbo']} tipos",
                    "dependa de contratos, e receba as dependencias pelo "
                    "construtor em vez de construi-las")
        if m["lcom"] > L["lcom"] and m["metodos"] >= 4 and m["campos"] >= 3:
            _cheiro(tipo, "baixa-coesao", "SRP",
                    f"'{tipo.nome}' tem LCOM {m['lcom']}: os metodos quase nao "
                    f"dividem campos",
                    "grupos de metodos que usam grupos de campos diferentes "
                    "sao blueprints diferentes dentro de um so")

        getters = [x for x in tipo.metodos if x.name.startswith(("get", "set", "obter", "definir"))
                   and len(x.body) <= 2]
        if tipo.campos and len(tipo.metodos) >= 2 and len(getters) == len(tipo.metodos):
            _cheiro(tipo, "modelo-anemico", "tell, don't ask",
                    f"'{tipo.nome}' so tem leitores e escritores de campo",
                    "a regra que usa esses campos esta em outro lugar; traga-a "
                    "para dentro, perto dos dados")

        for metodo in tipo.metodos:
            linhas = _ultima_linha(metodo) - metodo.line + 1
            if linhas > L["linhas_do_metodo"]:
                _cheiro(tipo, "metodo-longo", "SRP",
                        f"'{tipo.nome}.{metodo.name}' tem {linhas} linhas",
                        "extraia os passos em metodos com nome", metodo.line)
            if len(metodo.params) > L["parametros"]:
                _cheiro(tipo, "parametros-demais", "KISS",
                        f"'{tipo.nome}.{metodo.name}' recebe {len(metodo.params)} "
                        f"parametros",
                        "agrupe os que andam juntos num record", metodo.line)
            if getattr(metodo, "is_override", False) or _sobrescreve(tipo, metodo, tipos):
                if _so_recusa(metodo):
                    _cheiro(tipo, "sobrescrita-que-recusa", "LSP",
                            f"'{tipo.nome}.{metodo.name}' sobrescreve para so "
                            f"levantar erro",
                            "quem usa a mae espera que o metodo funcione; se a "
                            "filha nao pode cumprir, ela nao e um subtipo — use "
                            "um contrato menor", metodo.line)
            inveja = _inveja(metodo)
            if inveja:
                _cheiro(tipo, "inveja-de-recurso", "tell, don't ask",
                        f"'{tipo.nome}.{metodo.name}' le {inveja[1]} membros de "
                        f"'{inveja[0]}' e quase nenhum de si mesmo",
                        f"o metodo talvez pertenca a quem '{inveja[0]}' e",
                        metodo.line)
            ramos = _ramos_por_tipo(metodo)
            if ramos >= L["ramos_de_tipo"]:
                _cheiro(tipo, "switch-de-tipo", "OCP",
                        f"'{tipo.nome}.{metodo.name}' decide por tipo em {ramos} "
                        f"ramos",
                        "cada tipo novo exige editar este metodo; um metodo no "
                        "contrato, sobrescrito por cada tipo, fecha isso",
                        metodo.line)
            concretos = _constroi_concreto(metodo, tipos)
            if concretos and metodo.name not in _CONSTRUTORES:
                _cheiro(tipo, "dependencia-concreta", "DIP",
                        f"'{tipo.nome}.{metodo.name}' constroi "
                        f"{', '.join(sorted(concretos))} por dentro",
                        "receba pelo construtor, tipado pelo contrato — e o "
                        "teste passa a poder trocar a implementacao", metodo.line)

    for a, b in _ciclos(tipos):
        _cheiro(tipos[a], "dependencia-circular", "acoplamento",
                f"'{a}' e '{b}' dependem um do outro",
                "extraia um contrato que um dos dois implementa, e aponte a "
                "dependencia para ele")


def _sobrescreve(tipo, metodo, tipos, vistos=None):
    vistos = vistos or set()
    for mae in tipo.maes:
        if mae in vistos or mae not in tipos:
            continue
        vistos.add(mae)
        if any(m.name == metodo.name for m in tipos[mae].metodos):
            return True
        if _sobrescreve(tipos[mae], metodo, tipos, vistos):
            return True
    return False


def _so_recusa(metodo):
    corpo = [s for s in metodo.body if not isinstance(s, ast.StringLiteral)]
    return len(corpo) == 1 and type(corpo[0]).__name__ == "TriggerStatement"


def _inveja(metodo):
    de_si, de_outros = 0, {}
    parametros = set(metodo.params)
    for n in _andar(metodo.body):
        if isinstance(n, (ast.MemberAccess, ast.MethodCall)) and isinstance(n.object, ast.Identifier):
            nome = n.object.name
            if nome in ("self", "this"):
                de_si += 1
            elif nome in parametros:
                de_outros[nome] = de_outros.get(nome, 0) + 1
    if not de_outros:
        return None
    alvo, quantos = max(de_outros.items(), key=lambda kv: kv[1])
    if quantos >= 4 and quantos > 3 * max(de_si, 1):
        return alvo, quantos
    return None


def _ramos_por_tipo(metodo):
    maior = 0
    for n in _andar(metodo.body):
        if type(n).__name__ != "GivenBlock":
            continue
        condicoes = [n.condition] + [c for c, _ in (n.orif_blocks or [])]
        por_tipo = sum(1 for c in condicoes if any(
            type(x).__name__ in ("TypeofExpression",) or
            (isinstance(x, ast.FunctionCall) and isinstance(x.callee, ast.Identifier)
             and x.callee.name in ("instanceof", "e_um", "typeof", "class_name"))
            for x in _andar(c)))
        maior = max(maior, por_tipo)
    return maior


def _constroi_concreto(metodo, tipos):
    achados = set()
    for n in _andar(metodo.body):
        if isinstance(n, ast.SpawnExpression) and isinstance(n.class_name, ast.Identifier):
            alvo = tipos.get(n.class_name.name)
            if alvo is not None and alvo.especie == "blueprint" and alvo.contratos:
                achados.add(alvo.nome)
    return achados


def _ciclos(tipos):
    vistos = set()
    for a in sorted(tipos):
        for b in sorted(tipos[a].referencias):
            if b in tipos and a in tipos[b].referencias and a < b and (a, b) not in vistos:
                vistos.add((a, b))
                yield a, b


# ═════════════════════════════════════════════════════════════
#  Saidas
# ═════════════════════════════════════════════════════════════

def diagrama(tipos):
    """O diagrama de classes em Mermaid, a partir da arvore."""
    linhas = ["classDiagram"]
    visib = {"public": "+", "private": "-", "protected": "#", "internal": "~"}
    for nome in sorted(tipos):
        tipo = tipos[nome]
        linhas.append(f"    class {nome} {{")
        if tipo.especie == "contract":
            linhas.append("        <<interface>>")
        elif tipo.especie == "trait":
            linhas.append("        <<trait>>")
        elif tipo.especie == "meta":
            linhas.append("        <<metaclass>>")
        elif getattr(tipo.no, "is_abstract", False):
            linhas.append("        <<abstract>>")
        if isinstance(tipo.no, ast.BlueprintDeclaration):
            for campo, t, _p, v in tipo.no.fields_decl or []:
                linhas.append(f"        {visib.get(v, '+')}{t} {campo}")
            for campo in tipo.no.constructor_params or []:
                t = (tipo.no.constructor_types or {}).get(campo, "")
                linhas.append(f"        +{(t + ' ') if t else ''}{campo}")
        for metodo in tipo.metodos:
            sufixo = "*" if getattr(metodo, "is_abstract", False) else \
                "$" if getattr(metodo, "is_static", False) else ""
            retorno = f" {metodo.return_type}" if metodo.return_type else ""
            linhas.append(f"        {visib.get(getattr(metodo, 'visibility', 'public'), '+')}"
                          f"{metodo.name}({', '.join(metodo.params)}){sufixo}{retorno}")
        linhas.append("    }")
    for nome in sorted(tipos):
        tipo = tipos[nome]
        for mae in tipo.maes:
            if mae in tipos:
                linhas.append(f"    {mae} <|-- {nome}")
        for contrato in tipo.contratos:
            if contrato in tipos:
                linhas.append(f"    {contrato} <|.. {nome}")
        for ref in sorted(tipo.referencias - set(tipo.maes) - set(tipo.contratos)):
            if ref in tipos:
                linhas.append(f"    {nome} ..> {ref}")
    return "\n".join(linhas) + "\n"


def hierarquia(tipos):
    raizes = sorted(n for n, t in tipos.items()
                    if not any(m in tipos for m in t.maes))
    linhas = []

    def andar(nome, nivel, vistos):
        if nome in vistos:
            return
        vistos.add(nome)
        tipo = tipos[nome]
        marcas = [x for x, sim in (("abstract", getattr(tipo.no, "is_abstract", False)),
                                   ("final", getattr(tipo.no, "is_final", False)),
                                   ("sealed", getattr(tipo.no, "is_sealed", False)))
                  if sim]
        extra = (f"  with {', '.join(tipo.contratos)}" if tipo.contratos else "") + \
            (f"  [{', '.join(marcas)}]" if marcas else "")
        linhas.append("  " * nivel + nome + extra)
        for filha in sorted(f for f in tipo.filhas if tipos[f].especie != "contract"
                            and nome in tipos[f].maes):
            andar(filha, nivel + 1, vistos)

    for raiz in raizes:
        if tipos[raiz].especie in ("blueprint", "meta"):
            andar(raiz, 0, set())
    return "\n".join(linhas)


def analisar(arquivos, limites=None):
    tipos, problemas, fontes = coletar(arquivos)
    medir(tipos, fontes)
    cheirar(tipos, limites)
    return tipos, problemas


def como_json(tipos, problemas):
    return {
        "tipos": [{
            "nome": t.nome, "especie": t.especie, "arquivo": t.arquivo,
            "linha": t.no.line, "maes": t.maes, "contratos": t.contratos,
            "metricas": t.metricas, "cheiros": t.cheiros,
        } for t in sorted(tipos.values(), key=lambda t: (t.arquivo, t.no.line))],
        "problemas": [{"arquivo": a, "motivo": m} for a, m in problemas],
        "limites": dict(LIMITES),
    }


def relatorio(tipos, problemas, cor=lambda texto, _c: texto, curto=os.path.relpath):
    saida = []
    blueprints = [t for t in tipos.values() if t.especie in ("blueprint", "meta")]
    contratos = [t for t in tipos.values() if t.especie in ("contract", "trait")]
    saida.append(cor(f"{len(blueprints)} blueprint(s), {len(contratos)} contrato(s)/trait(s)",
                     "1;37"))
    if blueprints:
        cabecalho = (f"  {'blueprint':<24}{'LOC':>5}{'met':>5}{'WMC':>5}{'DIT':>5}"
                     f"{'NOC':>5}{'CBO':>5}{'RFC':>5}{'LCOM':>6}{'in':>4}{'out':>4}{'MI':>7}")
        saida.append(cor(cabecalho, "1;90"))
        for t in sorted(blueprints, key=lambda t: -t.metricas["wmc"]):
            m = t.metricas
            saida.append(
                f"  {t.nome[:23]:<24}{m['loc']:>5}{m['metodos']:>5}{m['wmc']:>5}"
                f"{m['dit']:>5}{m['noc']:>5}{m['cbo']:>5}{m['rfc']:>5}{m['lcom']:>6}"
                f"{m['fan_in']:>4}{m['fan_out']:>4}{m['manutenibilidade']:>7}")
    cheiros = [(t, c) for t in tipos.values() for c in t.cheiros]
    if cheiros:
        saida.append("")
        saida.append(cor(f"{len(cheiros)} cheiro(s):", "1;33"))
        for t, c in sorted(cheiros, key=lambda tc: (tc[0].arquivo, tc[1]["linha"])):
            saida.append(f"  {curto(t.arquivo)}:{c['linha']}  "
                         + cor(c["codigo"], "1;33") + cor(f"  [{c['principio']}]", "0;36"))
            saida.append(f"      {c['mensagem']}")
            saida.append(cor(f"      → {c['dica']}", "0;90"))
    elif tipos:
        saida.append("")
        saida.append(cor("nenhum cheiro acima dos limites.", "1;32"))
    for arquivo, motivo in problemas:
        saida.append(cor(f"  nao li {curto(arquivo)}: {motivo}", "1;31"))
    return "\n".join(saida)
