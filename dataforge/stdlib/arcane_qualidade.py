# -*- coding: utf-8 -*-
"""
Arcane.Qualidade — validação de dados como parte do pipeline.

    adopt Arcane.Qualidade as Q

    regras := {
        "id":         {"obrigatorio": yes, "unico": yes, "tipo": "inteiro"},
        "valor":      {"tipo": "numero", "minimo": 0},
        "email":      {"formato": "email"},
        "situacao":   {"em": ["ativo", "inativo"]},
    }

    r := Q.conferir(linhas, regras)
    given not r["ok"]:
        out Q.relatorio(r)

─── Por que isto não é um 'assert' ─────────────────────────

    assert todas(linhas, lambda l: l["id"] is not void)

Isso responde "passou?" e nada mais. Quando falha — e vai falhar, com
dado de verdade — não diz QUAL linha, QUANTAS, nem se é um caso isolado
ou metade do arquivo. E é essa diferença que decide se o pipeline para
ou segue.

Aqui cada violação traz a linha, o campo, o valor e o que se esperava.
Um relatório que diz "3 de 40.000 linhas com e-mail inválido" leva a
uma decisão; "falhou" leva a abrir o arquivo no editor.

─── As seis dimensões ──────────────────────────────────────

    completude    o campo veio?
    validade      está no formato/faixa certa?
    unicidade     a chave se repete?
    consistência  os campos combinam entre si?
    precisão      o tipo é o declarado?
    atualidade    o dado é recente o bastante?

'perfil' mede as seis de uma vez, sem regra nenhuma — é por onde se
começa quando o arquivo é desconhecido.
"""

import re
import statistics
from datetime import datetime

from ..errors import ValueError_

#: Quantas violações guardar por regra.
#:
#: Um arquivo com 40 mil linhas ruins produziria 40 mil registros e um
#: relatório que ninguém lê. As primeiras mostram o PADRÃO — que é o
#: que se procura — e a contagem total continua exata.
AMOSTRA = 10

_FORMATOS = {
    "email": r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$",
    "url": r"^https?://[^\s]+$",
    "uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
           r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
    "data": r"^\d{4}-\d{2}-\d{2}$",
    "data_hora": r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}",
    "cpf": r"^\d{3}\.?\d{3}\.?\d{3}-?\d{2}$",
    "cnpj": r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$",
    "cep": r"^\d{5}-?\d{3}$",
    "telefone": r"^\+?\d{2}?\s?\(?\d{2}\)?\s?9?\d{4}-?\d{4}$",
}

_TIPOS = {
    "inteiro": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "numero": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "texto": lambda v: isinstance(v, str),
    "booleano": lambda v: isinstance(v, bool),
    "lista": lambda v: isinstance(v, list),
    "vault": lambda v: isinstance(v, dict),
}


def _campo(linha, nome):
    if isinstance(linha, dict):
        return linha.get(nome)
    return getattr(linha, nome, None)


def _vazio(valor):
    """Ausente é 'void', texto vazio ou só espaço.

    Um campo com '   ' passou por 'não é void' e mesmo assim não tem
    dado. Tratar os dois como o mesmo caso é o que evita descobrir isso
    três etapas adiante.
    """
    return valor is None or (isinstance(valor, str) and not valor.strip())


class ArcaneQualidade(dict):
    """As seis dimensões, medidas e cobradas."""

    def __new__(cls):
        return {
            "conferir": cls._conferir,
            "relatorio": cls._relatorio,
            "perfil": cls._perfil,
            "esperar": cls._esperar,

            # dimensões isoladas
            "completude": cls._completude,
            "unicidade": cls._unicidade,
            "duplicadas": cls._duplicadas,
            "fora_da_faixa": cls._fora_da_faixa,
            "atualidade": cls._atualidade,

            # limpeza
            "sem_duplicadas": cls._sem_duplicadas,
            "so_validas": cls._so_validas,
            "preencher": cls._preencher,

            # esquema
            "esquema_de": cls._esquema_de,
            "deriva": cls._deriva,
            "exigir_esquema": cls._exigir_esquema,

            "formatos": lambda: sorted(_FORMATOS),
        }

    # ── deriva de esquema ───────────────────────────────────

    @staticmethod
    def _esquema_de(linhas, amostra=0):
        """O esquema OBSERVADO: o tipo de cada campo, e se ele falta.

        Ele é lido do dado, e não declarado — é o que permite
        comparar o que chegou hoje com o que chegava ontem sem que
        alguém tenha escrito o contrato antes.

        `nulavel` é o que mais importa na comparação: um campo que
        sempre veio preenchido e hoje vem vazio em metade das linhas
        não mudou de tipo, e mesmo assim quebra quem o consome.
        """
        linhas = list(linhas)
        if amostra and amostra > 0:
            linhas = linhas[:int(amostra)]
        campos = {}
        for linha in linhas:
            for nome in (linha.keys() if isinstance(linha, dict)
                         else getattr(linha, "_campos", lambda: [])()):
                valor = _campo(linha, nome)
                ficha = campos.setdefault(
                    nome, {"tipos": set(), "vazios": 0, "vistas": 0})
                ficha["vistas"] += 1
                if _vazio(valor):
                    ficha["vazios"] += 1
                else:
                    ficha["tipos"].add(_nome_do_tipo(valor))
        return {
            nome: {
                # Um campo com dois tipos e um campo com PROBLEMA, e
                # esconder isso num "misto" faria a deriva calar
                # justamente onde ela mais serve.
                "tipo": ("vazio" if not f["tipos"] else
                         sorted(f["tipos"])[0] if len(f["tipos"]) == 1 else
                         "|".join(sorted(f["tipos"]))),
                "nulavel": f["vazios"] > 0,
                # Duas contas diferentes, e confundi-las foi o primeiro
                # defeito desta peca: 'presenca' e quantas linhas TEM a
                # chave, 'vazios' e quantas a tem VAZIA. Um campo que
                # vem sempre, com metade em branco, tem presenca 1.0 e
                # vazios 0.5 — e e o segundo numero que quebra quem le.
                "presenca": round(f["vistas"] / max(1, len(linhas)), 4),
                "vazios": round(f["vazios"] / max(1, f["vistas"]), 4),
            }
            for nome, f in campos.items()
        }

    @staticmethod
    def _deriva(esperado, recebido):
        """O que mudou entre dois esquemas — e se isso QUEBRA.

        É a falha que mais derruba pipeline em produção, e ela não
        chega como erro: alguém a montante acrescenta uma coluna,
        renomeia outra, ou passa a mandar o id como texto. O programa
        continua rodando e o número sai errado.

        Os três baldes são os do `Arcane.Abi`, pela mesma razão:

        | balde | o que é |
        |---|---|
        | `quebra` | campo que sumiu, tipo que mudou, campo que passou a vir vazio |
        | `compativel` | campo novo — quem não o lê não vê diferença |
        | `desconhecido` | o campo existe dos dois lados e um dos lados nunca viu valor |

        O terceiro balde existe pelo mesmo motivo do `campo-novo-em-record`
        do ABI: sem valor nenhum de um dos lados, **não dá para saber**,
        e tanto acusar quanto calar estaria inventando uma resposta.
        """
        esperado = dict(esperado or {})
        recebido = dict(recebido or {})
        quebra, compativel, desconhecido = [], [], []

        for nome, antes in esperado.items():
            agora = recebido.get(nome)
            if agora is None:
                quebra.append({"campo": nome, "o_que": "sumiu",
                               "antes": antes.get("tipo"), "agora": None})
                continue
            if "vazio" in (antes.get("tipo"), agora.get("tipo")):
                desconhecido.append({
                    "campo": nome, "o_que": "um dos lados nunca viu valor",
                    "antes": antes.get("tipo"), "agora": agora.get("tipo")})
                continue
            if antes.get("tipo") != agora.get("tipo"):
                quebra.append({"campo": nome, "o_que": "mudou de tipo",
                               "antes": antes.get("tipo"),
                               "agora": agora.get("tipo")})
            elif agora.get("nulavel") and not antes.get("nulavel"):
                quebra.append({"campo": nome, "o_que": "passou a vir vazio",
                               "antes": "sempre preenchido",
                               "agora": f"{round(agora.get('vazios', 0) * 100)}% vazio"})

        for nome, agora in recebido.items():
            if nome not in esperado:
                compativel.append({"campo": nome, "o_que": "campo novo",
                                   "antes": None, "agora": agora.get("tipo")})

        return {"quebra": quebra, "compativel": compativel,
                "desconhecido": desconhecido,
                "ok": not quebra,
                "resumo": (f"{len(quebra)} quebra(s), "
                           f"{len(compativel)} acrescimo(s), "
                           f"{len(desconhecido)} sem resposta")}

    @staticmethod
    def _exigir_esquema(linhas, esperado, amostra=0):
        """Confere o lote contra o esquema e LEVANTA se ele quebrar.

        É a versão que se põe na entrada de um pipeline: falhar aqui
        custa uma execução; deixar passar custa um relatório errado que
        ninguém desconfia.
        """
        visto = ArcaneQualidade._esquema_de(linhas, amostra)
        relato = ArcaneQualidade._deriva(esperado, visto)
        if relato["quebra"]:
            partes = [f"{q['campo']}: {q['o_que']}"
                      + (f" ({q['antes']} → {q['agora']})"
                         if q["agora"] is not None else "")
                      for q in relato["quebra"]]
            raise ValueError_(
                "o esquema do lote nao bate com o esperado: "
                + "; ".join(partes),
                nota=relato["resumo"],
                dica="Qualidade.deriva(esperado, Qualidade.esquema_de(linhas)) "
                     "mostra tudo, inclusive os acrescimos",
                doc="dados/engenharia")
        return relato

    # ── conferir ────────────────────────────────────────────

    @staticmethod
    def _conferir(linhas, regras, parar_em=0):
        """Confere as linhas contra as regras. Não levanta: relata.

        Levantar na primeira violação seria pior: um pipeline precisa
        saber se o problema é uma linha ou metade do arquivo, e essa
        decisão depende de ver o quadro inteiro.
        """
        linhas = list(linhas or [])
        violacoes = []
        por_campo = {}
        vistos = {}

        for campo, regra in (regras or {}).items():
            regra = regra if isinstance(regra, dict) else {"tipo": str(regra)}
            if regra.get("unico"):
                vistos[campo] = {}

        for indice, linha in enumerate(linhas):
            for campo, regra in (regras or {}).items():
                regra = regra if isinstance(regra, dict) else {"tipo": str(regra)}
                valor = _campo(linha, campo)
                problema = _conferir_campo(valor, regra, campo, vistos, indice)
                if problema is None:
                    continue
                por_campo.setdefault(campo, {"total": 0, "exemplos": []})
                por_campo[campo]["total"] += 1
                if len(por_campo[campo]["exemplos"]) < AMOSTRA:
                    registro = {"linha": indice, "campo": campo,
                                "valor": valor, "problema": problema}
                    por_campo[campo]["exemplos"].append(registro)
                    violacoes.append(registro)
            if parar_em and len(violacoes) >= parar_em:
                break

        total_violacoes = sum(v["total"] for v in por_campo.values())
        ruins = len({v["linha"] for v in violacoes})
        return {
            "ok": total_violacoes == 0,
            "linhas": len(linhas),
            "violacoes": total_violacoes,
            "linhas_com_problema": ruins,
            "taxa_boa": round(1 - (ruins / len(linhas)), 4) if linhas else 1.0,
            "por_campo": por_campo,
            "exemplos": violacoes[:AMOSTRA * 2],
        }

    @staticmethod
    def _esperar(linhas, regras, minimo=1.0):
        """Confere e LEVANTA se a taxa boa ficar abaixo do mínimo.

        É a forma para dentro de um pipeline, onde continuar com dado
        ruim é a falha cara. 'minimo' existe porque nem todo dado
        precisa ser perfeito — um arquivo com 0,1% de e-mails inválidos
        costuma poder seguir, e parar por isso seria pior.
        """
        r = ArcaneQualidade._conferir(linhas, regras)
        if r["taxa_boa"] < float(minimo):
            campos = ", ".join(
                f"{c} ({d['total']})" for c, d in sorted(
                    r["por_campo"].items(), key=lambda x: -x[1]["total"])[:5])
            raise ValueError_(
                f"qualidade abaixo do mínimo: {r['taxa_boa']:.1%} "
                f"(esperado {float(minimo):.1%}).",
                nota=f"{r['linhas_com_problema']} de {r['linhas']} linhas "
                     f"com problema — {campos}",
                dica="use 'Qualidade.relatorio()' para ver os exemplos, ou "
                     "'so_validas()' para seguir só com o que passou",
                doc="tecnicas/qualidade")
        return r

    @staticmethod
    def _relatorio(resultado, largura=72):
        """O resultado em texto, para o log ou para o terminal."""
        linhas = []
        marca = "✓" if resultado["ok"] else "✗"
        linhas.append(f"{marca} {resultado['linhas']} linha(s), "
                      f"{resultado['violacoes']} violação(ões), "
                      f"{resultado['taxa_boa']:.1%} boas")
        if resultado["ok"]:
            return "\n".join(linhas)

        linhas.append("")
        for campo, dados in sorted(resultado["por_campo"].items(),
                                   key=lambda x: -x[1]["total"]):
            proporcao = dados["total"] / max(1, resultado["linhas"])
            linhas.append(f"  {campo}  —  {dados['total']} "
                          f"({proporcao:.1%})")
            for exemplo in dados["exemplos"][:3]:
                valor = repr(exemplo["valor"])
                if len(valor) > 30:
                    valor = valor[:27] + "…"
                linhas.append(f"      linha {exemplo['linha']}: "
                              f"{valor} — {exemplo['problema']}")
        return "\n".join(linhas)

    # ── perfil ──────────────────────────────────────────────

    @staticmethod
    def _perfil(linhas, amostra=0):
        """Mede o que há, sem regra nenhuma.

        É por onde se começa quando o arquivo é desconhecido: quantos
        nulos, quantos distintos, que tipos convivem no mesmo campo — e
        é a partir daí que se escreve a regra.
        """
        linhas = list(linhas or [])
        if amostra and len(linhas) > amostra:
            passo = max(1, len(linhas) // amostra)
            linhas = linhas[::passo][:amostra]
        if not linhas:
            return {"linhas": 0, "campos": {}}

        campos = {}
        for linha in linhas:
            chaves = linha.keys() if isinstance(linha, dict) else \
                [c for c in dir(linha) if not c.startswith("_")]
            for chave in chaves:
                campos.setdefault(chave, [])
        for linha in linhas:
            for chave in campos:
                campos[chave].append(_campo(linha, chave))

        saida = {}
        for chave, valores in campos.items():
            presentes = [v for v in valores if not _vazio(v)]
            tipos = sorted({_nome_do_tipo(v) for v in presentes})
            perfil = {
                "preenchidos": len(presentes),
                "vazios": len(valores) - len(presentes),
                "completude": round(len(presentes) / len(valores), 4),
                "distintos": len({_chave_hashavel(v) for v in presentes}),
                "tipos": tipos,
                # Dois tipos no mesmo campo quase sempre é defeito de
                # origem — CSV lido sem esquema, JSON de fonte instável.
                "tipo_misto": len(tipos) > 1,
            }
            numeros = [v for v in presentes
                       if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if numeros:
                perfil.update({
                    "minimo": min(numeros), "maximo": max(numeros),
                    "media": round(statistics.fmean(numeros), 6),
                    "mediana": statistics.median(numeros),
                })
            textos = [v for v in presentes if isinstance(v, str)]
            if textos:
                perfil["menor_texto"] = min(len(t) for t in textos)
                perfil["maior_texto"] = max(len(t) for t in textos)
            if perfil["distintos"] and perfil["distintos"] == len(presentes) \
                    and len(presentes) > 1:
                perfil["parece_chave"] = True
            saida[chave] = perfil
        return {"linhas": len(linhas), "campos": saida}

    # ── dimensões isoladas ──────────────────────────────────

    @staticmethod
    def _completude(linhas, campos=None):
        """Quanto de cada campo veio preenchido."""
        linhas = list(linhas or [])
        if not linhas:
            return {}
        alvos = list(campos) if campos else list(
            linhas[0].keys() if isinstance(linhas[0], dict) else [])
        return {c: round(sum(1 for l in linhas if not _vazio(_campo(l, c)))
                         / len(linhas), 4) for c in alvos}

    @staticmethod
    def _unicidade(linhas, campo):
        """A proporção de valores distintos — 1.0 é chave."""
        linhas = list(linhas or [])
        if not linhas:
            return 1.0
        valores = [_chave_hashavel(_campo(l, campo)) for l in linhas]
        return round(len(set(valores)) / len(valores), 4)

    @staticmethod
    def _duplicadas(linhas, campos):
        """As linhas cuja chave se repete, agrupadas."""
        campos = [campos] if isinstance(campos, str) else list(campos)
        grupos = {}
        for i, linha in enumerate(linhas or []):
            chave = tuple(_chave_hashavel(_campo(linha, c)) for c in campos)
            grupos.setdefault(chave, []).append(i)
        return [{"chave": list(k), "linhas": v, "quantas": len(v)}
                for k, v in grupos.items() if len(v) > 1]

    @staticmethod
    def _fora_da_faixa(linhas, campo, minimo=None, maximo=None):
        saida = []
        for i, linha in enumerate(linhas or []):
            valor = _campo(linha, campo)
            if not isinstance(valor, (int, float)) or isinstance(valor, bool):
                continue
            if (minimo is not None and valor < minimo) or \
               (maximo is not None and valor > maximo):
                saida.append({"linha": i, "valor": valor})
        return saida

    @staticmethod
    def _atualidade(linhas, campo, dias=1):
        """Quantas linhas são mais velhas que o limite.

        Dado antigo não é dado errado — é dado que passou a mentir sem
        avisar, e é a dimensão que mais escapa da validação.
        """
        limite = time.time() - (float(dias) * 86400)
        velhas = 0
        for linha in linhas or []:
            quando = _para_tempo(_campo(linha, campo))
            if quando is not None and quando < limite:
                velhas += 1
        total = len(list(linhas or []))
        return {"velhas": velhas, "total": total,
                "proporcao": round(velhas / total, 4) if total else 0.0,
                "limite_dias": float(dias)}

    # ── limpeza ─────────────────────────────────────────────

    @staticmethod
    def _sem_duplicadas(linhas, campos=None):
        """Mantém a PRIMEIRA de cada chave repetida.

        A primeira, e não a última: em dado de origem a ordem costuma
        ser a de chegada, e a primeira é a original.
        """
        linhas = list(linhas or [])
        if not linhas:
            return []
        if campos is None:
            vistos, saida = set(), []
            for linha in linhas:
                chave = _chave_hashavel(linha)
                if chave not in vistos:
                    vistos.add(chave)
                    saida.append(linha)
            return saida
        campos = [campos] if isinstance(campos, str) else list(campos)
        vistos, saida = set(), []
        for linha in linhas:
            chave = tuple(_chave_hashavel(_campo(linha, c)) for c in campos)
            if chave not in vistos:
                vistos.add(chave)
                saida.append(linha)
        return saida

    @staticmethod
    def _so_validas(linhas, regras):
        """Só as linhas que passam em todas as regras."""
        vistos = {c: {} for c, r in (regras or {}).items()
                  if isinstance(r, dict) and r.get("unico")}
        saida = []
        for i, linha in enumerate(linhas or []):
            if all(_conferir_campo(_campo(linha, c),
                                   r if isinstance(r, dict) else {"tipo": str(r)},
                                   c, vistos, i) is None
                   for c, r in (regras or {}).items()):
                saida.append(linha)
        return saida

    @staticmethod
    def _preencher(linhas, padroes):
        """Preenche o que está vazio, sem tocar no que veio."""
        saida = []
        for linha in linhas or []:
            if not isinstance(linha, dict):
                saida.append(linha)
                continue
            nova = dict(linha)
            for campo, padrao in (padroes or {}).items():
                if _vazio(nova.get(campo)):
                    nova[campo] = padrao
            saida.append(nova)
        return saida


import time  # noqa: E402  (usado por _atualidade)


def _nome_do_tipo(valor):
    if isinstance(valor, bool):
        return "booleano"
    if isinstance(valor, int):
        return "inteiro"
    if isinstance(valor, float):
        return "numero"
    if isinstance(valor, str):
        return "texto"
    if isinstance(valor, list):
        return "lista"
    if isinstance(valor, dict):
        return "vault"
    return type(valor).__name__


def _chave_hashavel(valor):
    """Um valor comparável, mesmo quando ele é lista ou vault."""
    if isinstance(valor, (list, tuple)):
        return tuple(_chave_hashavel(v) for v in valor)
    if isinstance(valor, dict):
        return tuple(sorted((k, _chave_hashavel(v)) for k, v in valor.items()))
    try:
        hash(valor)
        return valor
    except TypeError:
        return repr(valor)


def _para_tempo(valor):
    """Segundos desde a época, a partir de número ou texto ISO."""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        return float(valor)
    if isinstance(valor, str):
        texto = valor.strip().replace("Z", "+00:00")
        for tentativa in (texto, texto[:19], texto[:10]):
            try:
                return datetime.fromisoformat(tentativa).timestamp()
            except ValueError:
                continue
    return None


def _conferir_campo(valor, regra, campo, vistos, indice):
    """O problema deste valor, ou None. Uma regra por vez, na ordem."""
    if _vazio(valor):
        return "obrigatório, e veio vazio" if regra.get("obrigatorio") else None

    tipo = regra.get("tipo")
    if tipo and tipo in _TIPOS and not _TIPOS[tipo](valor):
        return f"esperava {tipo}, veio {_nome_do_tipo(valor)}"

    formato = regra.get("formato")
    if formato:
        padrao = _FORMATOS.get(formato, formato)
        if not isinstance(valor, str) or re.match(padrao, valor) is None:
            return f"fora do formato {formato}"

    if "em" in regra and valor not in regra["em"]:
        return "valor fora da lista permitida"

    numero = valor if isinstance(valor, (int, float)) and \
        not isinstance(valor, bool) else None
    tamanho = len(valor) if isinstance(valor, (str, list, dict)) else None

    if "minimo" in regra:
        alvo = numero if numero is not None else tamanho
        if alvo is not None and alvo < regra["minimo"]:
            return f"abaixo do mínimo {regra['minimo']}"
    if "maximo" in regra:
        alvo = numero if numero is not None else tamanho
        if alvo is not None and alvo > regra["maximo"]:
            return f"acima do máximo {regra['maximo']}"

    if regra.get("unico"):
        chave = _chave_hashavel(valor)
        onde = vistos.setdefault(campo, {})
        if chave in onde:
            return f"repetido — já apareceu na linha {onde[chave]}"
        onde[chave] = indice

    confere = regra.get("confere")
    if callable(confere):
        try:
            if not confere(valor):
                return "reprovado pela regra própria"
        except Exception:                               # noqa: BLE001
            return "a regra própria estourou neste valor"
    return None
