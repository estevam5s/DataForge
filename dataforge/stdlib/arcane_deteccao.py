# -*- coding: utf-8 -*-
"""Arcane.Deteccao — a regra que vê o que passou, e o alerta que sai.

    adopt Arcane.Deteccao as D

    motor := D.motor()
    motor.regra("forca-bruta", quando := "login.falhou",
        vezes := 5, janela := 60.0, gravidade := "alto",
        attack := "T1110")

    cycle i from 1 to 5:
        motor.evento("login.falhou", {"ip": "203.0.113.7"}, por := "203.0.113.7")

    out len(motor.alertas())      // 1

─── Detecção não é registro ────────────────────────────────

Gravar log é fácil e quase inútil sozinho: ninguém lê dez milhões de
linhas. O que transforma log em defesa é a **regra** — a afirmação de
que uma sequência de eventos significa alguma coisa — e o **alerta**,
que é a regra disparando com o contexto junto.

Este módulo é a peça que faltava entre `Seguranca.auditoria` (que
grava) e a pessoa (que precisa saber). Ele é pequeno de propósito: um
SIEM de verdade é infraestrutura, e reimplementá-lo em Python daria
um subconjunto pior amarrado à linguagem.

─── As cinco decisões ──────────────────────────────────────

| Decisão | Sem ela |
|---|---|
| a correlação é por **chave**, e não global | cinco falhas de cinco pessoas diferentes viram um alerta de força bruta |
| a janela é **deslizante** | 5 falhas às 23h59 e 5 às 00h01 passam por baixo de duas janelas fixas |
| o alerta traz os **eventos que o causaram** | "força bruta detectada" sem o que aconteceu não é investigável |
| há **supressão** | a mesma regra disparando mil vezes por minuto é ruído, e ruído é o que faz desligar o alerta |
| a regra que **falha** é contada, e não engolida | um motor que morre no primeiro erro de regra deixa de detectar tudo o resto |

─── Indicadores: o que eles são, e o que não são ───────────

Um IOC — hash, IP, domínio, URL — responde *"isto já foi visto num
incidente?"*. Ele é **datado e perecível**: um IP malicioso hoje é um
IP de nuvem reciclado em três semanas, e um indicador sem prazo vira
falso positivo permanente. Por isso `indicadores()` tem prazo e a
consulta descarta o que venceu.

E ele **não prova** nada sozinho: um domínio na lista pode ser um
colega abrindo um artigo sobre o incidente. IOC é sinal, e o valor
dele está em somar com outros.

─── O que ele NÃO faz ──────────────────────────────────────

**Não envia alerta.** `aoAlertar` recebe um retorno de chamada, e
quem manda para o Slack, para o e-mail ou para o Telegram é quem
chama. Um módulo que escolhesse o canal escolheria errado.

**Não lê arquivo de log sozinho.** Ele recebe eventos. Um leitor de
arquivo embutido teria de adivinhar o formato, e formato de log é a
coisa que menos se parece entre dois sistemas.

**Não é YARA.** `varrer()` casa expressão regular sobre texto e bytes,
o que cobre a parte de YARA que se usa no dia a dia (strings e
condição), e não tem o módulo PE, nem os operadores de offset, nem a
compilação. Chamá-lo de YARA seria prometer o que não está aqui.
"""

import re
import threading
import time

from ..builtins import _df_type as _nome_do_tipo
from .opcoes import ler as _ler_opcoes

_DOC = "seguranca/deteccao"

#: As gravidades, em ordem. A lista é FECHADA — um sexto valor seria
#: onde "mais ou menos urgente" se esconderia, e a triagem depende de
#: os níveis significarem a mesma coisa para todo mundo.
GRAVIDADES = ("informativo", "baixo", "medio", "alto", "critico")

#: Os tipos de indicador que o módulo reconhece.
TIPOS_DE_INDICADOR = ("ip", "dominio", "url", "hash", "email", "usuario")


def _erro(mensagem, nota="", dica="", classe="SecurityError"):
    from .. import errors

    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _texto(valor, onde):
    if isinstance(valor, str):
        return valor
    raise _erro(f"'{onde}' espera um texto, e recebeu um "
                f"{_nome_do_tipo(valor)}.")


def _peso(gravidade):
    try:
        return GRAVIDADES.index(gravidade)
    except ValueError:
        return 0


# ═══════════════════════════════════════════════════════════
#  Indicadores de comprometimento
# ═══════════════════════════════════════════════════════════

class _Indicadores:
    """A lista do que já foi visto num incidente — com prazo.

    O prazo não é detalhe: um IP malicioso hoje é um IP de nuvem
    reciclado em três semanas. Um indicador sem validade vira falso
    positivo permanente, e falso positivo permanente é o que faz
    alguém desligar a consulta inteira.
    """

    __slots__ = ("_itens", "_trava")

    def __init__(self):
        self._itens = {}
        self._trava = threading.Lock()

    def acrescentar(self, tipo, valor, fonte="", gravidade="medio",
                    prazo=2592000.0, nota="", quando=None):
        if tipo not in TIPOS_DE_INDICADOR:
            raise _erro(
                f"'{tipo}' nao e um tipo de indicador.",
                nota="Ha: " + ", ".join(TIPOS_DE_INDICADOR))
        if gravidade not in GRAVIDADES:
            raise _erro(f"'{gravidade}' nao e uma gravidade.",
                        nota="Ha: " + ", ".join(GRAVIDADES))
        agora = time.time() if quando is None else float(quando)
        chave = (tipo, _normalizar(tipo, valor))
        with self._trava:
            self._itens[chave] = {
                "tipo": tipo, "valor": _normalizar(tipo, valor),
                "fonte": fonte, "gravidade": gravidade, "nota": nota,
                "visto": agora,
                "vence": agora + float(prazo) if prazo else 0.0,
            }
        return self

    def carregar(self, lista, fonte="", prazo=2592000.0):
        """Um feed inteiro de uma vez."""
        for item in lista or []:
            if isinstance(item, dict):
                self.acrescentar(
                    item.get("tipo", "ip"), item.get("valor", ""),
                    item.get("fonte", fonte),
                    item.get("gravidade", "medio"),
                    item.get("prazo", prazo), item.get("nota", ""))
        return self

    def ver(self, tipo, valor, quando=None):
        """Está na lista? Devolve o indicador, ou `void`."""
        agora = time.time() if quando is None else float(quando)
        with self._trava:
            achado = self._itens.get((tipo, _normalizar(tipo, valor)))
        if achado is None:
            return None
        if achado["vence"] and agora >= achado["vence"]:
            return None
        return dict(achado)

    def remover(self, tipo, valor):
        with self._trava:
            return self._itens.pop((tipo, _normalizar(tipo, valor)), None) is not None

    def limpar_vencidos(self, quando=None):
        agora = time.time() if quando is None else float(quando)
        with self._trava:
            antes = len(self._itens)
            self._itens = {
                k: v for k, v in self._itens.items()
                if not (v["vence"] and agora >= v["vence"])}
            return antes - len(self._itens)

    def tudo(self):
        with self._trava:
            return [dict(v) for v in self._itens.values()]

    def __len__(self):
        return len(self._itens)


def _normalizar(tipo, valor):
    """O mesmo indicador escrito de dois jeitos é o mesmo indicador.

    `MAU.EXEMPLO.` e `mau.exemplo` são o mesmo domínio, e um hash em
    maiúsculas é o mesmo hash. Sem isto, a lista teria duas entradas
    e a consulta acharia uma delas — a errada, metade das vezes.
    """
    v = str(valor).strip()
    if tipo in ("dominio", "email"):
        return v.lower().rstrip(".")
    if tipo == "hash":
        return v.lower()
    if tipo == "url":
        return v.rstrip("/")
    return v


# ═══════════════════════════════════════════════════════════
#  O motor de regras
# ═══════════════════════════════════════════════════════════

_REGRA = {
    "quando": "", "vezes": 1, "janela": 60.0, "gravidade": "medio",
    "attack": "", "por": "", "onde": None, "suprimir": 300.0,
    "descricao": "",
}


class _Motor:
    """Recebe eventos, aplica regras, e produz alertas.

    O estado é por **chave de correlação** (`por`): sem ela, cinco
    falhas de cinco pessoas diferentes viram um alerta de força bruta
    — e o alerta que mais custa é o que está errado.
    """

    __slots__ = ("_regras", "_janelas", "_alertas", "_suprimidos",
                 "_indicadores", "_ao_alertar", "_erros", "_trava",
                 "_vistos")

    def __init__(self):
        self._regras = []
        self._janelas = {}
        self._alertas = []
        self._suprimidos = {}
        self._indicadores = _Indicadores()
        self._ao_alertar = None
        self._erros = []
        self._vistos = 0
        self._trava = threading.Lock()

    # ── Montagem ────────────────────────────────────────────

    def regra(self, nome, opcoes=None, **kw):
        """Uma regra: qual evento, quantas vezes, em que janela."""
        cru = dict(opcoes or {})
        cru.update(kw)
        o = dict(_REGRA)
        o.update(_ler_opcoes(cru, _REGRA, "Deteccao.regra"))
        if o["gravidade"] not in GRAVIDADES:
            raise _erro(f"'{o['gravidade']}' nao e uma gravidade.",
                        nota="Ha: " + ", ".join(GRAVIDADES))
        if not o["quando"] and o["onde"] is None:
            raise _erro(
                f"a regra '{nome}' nao diz o que observar.",
                dica="Use 'quando := \"nome.do.evento\"' ou "
                     "'onde := lambda e => …'.")
        with self._trava:
            self._regras.append({"nome": _texto(nome, "regra"), **o})
        return self

    def ao_alertar(self, acao):
        """Quem manda para o Slack, o e-mail ou o Telegram é quem chama.

        Um módulo que escolhesse o canal escolheria errado — e ficaria
        com uma dependência de rede no caminho de uma detecção.
        """
        self._ao_alertar = acao
        return self

    def indicadores(self):
        return self._indicadores

    # ── A entrada ───────────────────────────────────────────

    def evento(self, nome, dados=None, por="", quando=None):
        """Um evento entrou. Devolve os alertas que ELE causou.

        Devolver só os novos — e não a lista inteira — é o que permite
        reagir na hora sem varrer tudo de novo a cada chamada.
        """
        agora = time.time() if quando is None else float(quando)
        e = {"nome": _texto(nome, "evento"), "dados": dict(dados or {}),
             "por": str(por), "quando": agora}
        with self._trava:
            self._vistos += 1
            regras = list(self._regras)

        novos = []
        for r in regras:
            try:
                if not self._casa(r, e):
                    continue
            except Exception as erro:                      # noqa: BLE001
                # Uma regra que falha NÃO derruba o motor: ela é
                # contada e as outras seguem. Um motor que morre no
                # primeiro erro deixa de detectar tudo o resto — e o
                # silêncio parece calmaria.
                with self._trava:
                    self._erros.append({"regra": r["nome"],
                                        "erro": str(erro), "quando": agora})
                continue
            alerta = self._registrar(r, e, agora)
            if alerta is not None:
                novos.append(alerta)
        return novos

    def _casa(self, regra, evento):
        if regra["quando"] and regra["quando"] != evento["nome"]:
            # `login.*` cobre `login.falhou`; o curinga é explícito.
            if not (regra["quando"].endswith("*")
                    and evento["nome"].startswith(regra["quando"][:-1])):
                return False
        if regra["onde"] is not None:
            return bool(regra["onde"](evento))
        return True

    def _registrar(self, regra, evento, agora):
        # A chave de correlação: o campo nomeado em `por`, ou o `por`
        # do próprio evento. Sem ela, tudo cai no mesmo balde.
        chave = (regra["nome"],
                 str(evento["dados"].get(regra["por"], evento["por"]))
                 if regra["por"] else evento["por"])

        janela = float(regra["janela"])
        with self._trava:
            fila = self._janelas.setdefault(chave, [])
            # Janela DESLIZANTE: 5 falhas às 23h59 e 5 às 00h01 passam
            # por baixo de duas janelas fixas, e é exatamente assim que
            # se contorna um contador por minuto.
            corte = agora - janela
            while fila and fila[0]["quando"] < corte:
                fila.pop(0)
            fila.append(evento)

            if len(fila) < int(regra["vezes"]):
                return None

            ultimo = self._suprimidos.get(chave, 0.0)
            if agora - ultimo < float(regra["suprimir"]):
                return None
            self._suprimidos[chave] = agora

            alerta = {
                "regra": regra["nome"],
                "gravidade": regra["gravidade"],
                "descricao": regra["descricao"] or regra["nome"],
                "attack": regra["attack"],
                "chave": chave[1],
                "quando": agora,
                "vezes": len(fila),
                # Os eventos que o causaram vão junto: "força bruta
                # detectada" sem o que aconteceu não é investigável.
                "eventos": [dict(x) for x in fila[-int(regra["vezes"]):]],
            }
            self._alertas.append(alerta)
            # A janela é zerada: sem isso, o sexto evento dispararia de
            # novo, e o sétimo também.
            fila.clear()

        if self._ao_alertar is not None:
            try:
                self._ao_alertar(alerta)
            except Exception as erro:                      # noqa: BLE001
                with self._trava:
                    self._erros.append({"regra": regra["nome"],
                                        "erro": f"ao_alertar: {erro}",
                                        "quando": agora})
        return alerta

    def observar(self, tipo, valor, contexto=None, quando=None):
        """Um valor de fora bateu num indicador? Vira evento se bater."""
        achado = self._indicadores.ver(tipo, valor, quando)
        if achado is None:
            return None
        dados = dict(contexto or {})
        dados.update({"tipo": tipo, "valor": achado["valor"],
                      "fonte": achado["fonte"], "nota": achado["nota"]})
        self.evento("indicador.visto", dados, por=str(valor), quando=quando)
        return achado

    # ── A saída ─────────────────────────────────────────────

    def alertas(self, desde=None, gravidade_minima=None):
        with self._trava:
            saida = [dict(a) for a in self._alertas]
        if desde is not None:
            saida = [a for a in saida if a["quando"] >= float(desde)]
        if gravidade_minima:
            piso = _peso(gravidade_minima)
            saida = [a for a in saida if _peso(a["gravidade"]) >= piso]
        return saida

    def resumo(self):
        """O que aconteceu, em números. É o que vai para o painel."""
        with self._trava:
            alertas = list(self._alertas)
            return {
                "eventos": self._vistos,
                "regras": len(self._regras),
                "alertas": len(alertas),
                "por_gravidade": {
                    g: sum(1 for a in alertas if a["gravidade"] == g)
                    for g in GRAVIDADES},
                "por_regra": {
                    r["nome"]: sum(1 for a in alertas if a["regra"] == r["nome"])
                    for r in self._regras},
                "indicadores": len(self._indicadores),
                # Regras que falharam. Zero é o estado esperado, e um
                # número que cresce em silêncio é uma detecção que não
                # está acontecendo.
                "erros_de_regra": len(self._erros),
            }

    def erros(self):
        with self._trava:
            return [dict(e) for e in self._erros]

    def limpar(self):
        with self._trava:
            self._alertas.clear()
            self._janelas.clear()
            self._suprimidos.clear()
        return True


# ═══════════════════════════════════════════════════════════
#  Padrões sobre conteúdo
# ═══════════════════════════════════════════════════════════

def _padrao(nome, textos, gravidade="medio", descricao=""):
    """Um conjunto de expressões, com nome — o que YARA chama de regra.

    NÃO é YARA: cobre a parte que se usa no dia a dia (as strings e a
    condição "alguma delas"), e não tem o módulo PE, os operadores de
    offset nem a compilação. Chamá-lo de YARA seria prometer o que não
    está aqui.
    """
    if gravidade not in GRAVIDADES:
        raise _erro(f"'{gravidade}' nao e uma gravidade.")
    compilados = []
    for t in textos or []:
        try:
            compilados.append((t, re.compile(t, re.I | re.S)))
        except re.error as erro:
            raise _erro(
                f"o padrao {t!r} da regra '{nome}' nao compila: {erro}",
                dica="Escape o que for literal com 'Seg.escapar_regex'.")
    return {"nome": _texto(nome, "padrao"), "gravidade": gravidade,
            "descricao": descricao, "_compilados": compilados,
            "padroes": [t for t, _ in compilados]}


def _varrer(conteudo, padroes, minimo=1):
    """Quais padrões batem, e onde. Aceita texto ou bytes."""
    alvo = conteudo
    if isinstance(alvo, (bytes, bytearray)):
        alvo = bytes(alvo).decode("latin-1")
    alvo = _texto(alvo, "analisar")

    saida = []
    for p in padroes or []:
        achados = []
        for texto, compilado in p.get("_compilados", []):
            for m in compilado.finditer(alvo):
                achados.append({
                    "padrao": texto,
                    "posicao": m.start(),
                    "linha": alvo.count("\n", 0, m.start()) + 1,
                    # O trecho vem CURTO: um relatório que despeja o
                    # arquivo inteiro não é lido, e se o conteúdo for
                    # malicioso ele passa a estar em mais um lugar.
                    "trecho": alvo[m.start():m.start() + 60].replace("\n", " "),
                })
        if len(achados) >= int(minimo):
            saida.append({"regra": p["nome"], "gravidade": p["gravidade"],
                          "descricao": p["descricao"],
                          "achados": achados[:20], "total": len(achados)})
    saida.sort(key=lambda r: -_peso(r["gravidade"]))
    return saida


# ═══════════════════════════════════════════════════════════
#  Log
# ═══════════════════════════════════════════════════════════

_COMBINADO = re.compile(
    r'^(?P<ip>\S+) \S+ (?P<usuario>\S+) \[(?P<quando>[^\]]+)\] '
    r'"(?P<metodo>\S+) (?P<caminho>\S+)[^"]*" '
    r'(?P<status>\d{3}) (?P<bytes>\S+)')


def _ler_linha(linha, formato="combinado"):
    """Uma linha de log de acesso vira vault.

    Só o formato combinado (Apache/nginx), e o motivo é honesto: é o
    único que tem forma fixa o bastante para um analisador embutido
    acertar. Para o resto, `Arcane.Regex` com o padrão do seu sistema
    — e é melhor assim que um analisador que adivinha errado.
    """
    if formato != "combinado":
        raise _erro(
            f"nao conheco o formato '{formato}'.",
            nota="Ha: 'combinado' (Apache/nginx).",
            dica="Para outro formato, use 'Arcane.Regex' com o padrao "
                 "do seu sistema — adivinhar seria pior.")
    m = _COMBINADO.match(_texto(linha, "ler_linha"))
    if m is None:
        return None
    d = m.groupdict()
    try:
        d["status"] = int(d["status"])
    except (TypeError, ValueError):
        pass
    return d


class ArcaneDeteccao(dict):
    """O vault que o 'adopt' entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Deteccao",

            "motor": lambda: _Motor(),
            "indicadores": lambda: _Indicadores(),

            "padrao": _padrao,
            #: Chama-se 'varrer', e nao 'analisar':
            #: 'Arcane.Seguranca.analisar' ja existe e responde outra
            #: pergunta — as dez regras sintaticas sobre um '.df'.
            #: Aqui o alvo e CONTEUDO qualquer, contra padroes que
            #: quem chama escreveu. Dois nomes iguais para perguntas
            #: diferentes fazem presumir a resposta errada, e ha teste
            #: proibindo a colisao entre os modulos de seguranca.
            "varrer": _varrer,
            "ler_linha": _ler_linha,

            "GRAVIDADES": list(GRAVIDADES),
            "TIPOS_DE_INDICADOR": list(TIPOS_DE_INDICADOR),
        }
