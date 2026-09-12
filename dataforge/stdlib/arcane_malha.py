# -*- coding: utf-8 -*-
"""Arcane.Malha — o que muda quando a chamada atravessa a rede.

O problema
----------
Uma chamada de funcao ou funciona, ou levanta. Uma chamada de REDE tem
um terceiro estado: **nao se sabe**. Ela pode ter chegado e a resposta
se perdido; pode estar a caminho; pode ter sido processada duas vezes.

Quase todo bug de microservico vem de tratar o terceiro estado como um
dos dois primeiros:

| O que se faz | O que acontece |
|---|---|
| tentar de novo, sem cuidado | o pedido e processado duas vezes |
| esperar sem prazo | uma thread presa por servico, para sempre |
| insistir num servico caido | ele nao se recupera, porque nunca para de receber |
| propagar so o dado | o rastro se perde na primeira fronteira |

Este modulo trata os quatro. Ele NAO e um framework de microservico —
nao ha service mesh, nao ha sidecar, nao ha registro central. E o que
uma chamada entre servicos precisa para nao mentir.

    adopt Arcane.Malha as Malha

    cliente := Malha.cliente("https://pedidos.interno", {
        "prazo": 3.0,
        "tentativas": 3,
        "disjuntor": {"falhas": 5, "espera": 30}
    })

    r := cliente.get("/pedidos/42")

Sobre o que ele e construido
----------------------------
'urllib' da biblioteca padrao. Sem 'requests', sem 'httpx' — a regra do
projeto e zero dependencia, e o que falta no 'urllib' (retry com recuo,
disjuntor, propagacao de contexto) e exatamente o que este arquivo faz.
"""

import json
import random
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

#: Os codigos que valem tentar de novo.
#:
#: 5xx e o servidor dizendo que o problema e dele; 429 e ele pedindo
#: para esperar; 408 e um prazo do proprio servidor. Um 4xx que nao
#: seja esses dois NAO se repete: o pedido esta errado, e mandar de
#: novo da o mesmo erro com mais latencia.
RETENTAVEIS = frozenset({408, 425, 429, 500, 502, 503, 504})

#: Os metodos seguros de repetir SEM chave de idempotencia.
#:
#: GET, HEAD e OPTIONS nao mudam estado — repeti-los e inofensivo. POST
#: repetido pode cobrar duas vezes, e por isso ele so e repetido quando
#: quem chama fornece uma 'Idempotency-Key'.
IDEMPOTENTES = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})

#: O cabecalho que atravessa toda fronteira.
#:
#: Sem um identificador que viaja com o pedido, investigar um incidente
#: em cinco servicos e cruzar horario de log — que e impossivel quando
#: dois pedidos acontecem no mesmo segundo.
CABECALHO_RASTRO = "X-Request-Id"
CABECALHO_ORIGEM = "X-Origem"


# ═══════════════════════════════════════════════════════════
#  O contexto que viaja
# ═══════════════════════════════════════════════════════════

class Contexto:
    """O rastro do pedido, por thread.

    Ele existe para que a propagacao seja AUTOMATICA. Um cliente que
    obriga quem escreve a passar o id em cada chamada perde o id na
    primeira vez que alguem esquecer — e esquecer e o caso normal.
    """

    _local = threading.local()

    @classmethod
    def atual(cls):
        return getattr(cls._local, "dados", None)

    @classmethod
    def comecar(cls, rastro=None, origem="", extra=None):
        dados = {
            "rastro": rastro or uuid.uuid4().hex,
            "origem": origem,
            "extra": dict(extra or {}),
            "comecou_em": time.time(),
        }
        cls._local.dados = dados
        return dados

    @classmethod
    def terminar(cls):
        dados = cls.atual()
        cls._local.dados = None
        return dados

    @classmethod
    def cabecalhos(cls):
        """O que vai em toda chamada de saida."""
        dados = cls.atual()
        if not dados:
            return {}
        saida = {CABECALHO_RASTRO: dados["rastro"]}
        if dados.get("origem"):
            saida[CABECALHO_ORIGEM] = dados["origem"]
        for chave, valor in dados.get("extra", {}).items():
            saida[f"X-Ctx-{chave}"] = str(valor)
        return saida


# ═══════════════════════════════════════════════════════════
#  Disjuntor
# ═══════════════════════════════════════════════════════════

class Disjuntor:
    """Para de tentar quando o outro lado esta caido.

    Sem ele, um servico que cai leva os que dependem dele: cada pedido
    espera o prazo inteiro antes de falhar, as threads acabam, e o que
    estava de pe cai tambem. E o servico caido nunca se recupera, porque
    nunca para de receber.

    Tres estados:

        fechado   ────falhas demais────▶  aberto
           ▲                               │
           │                          espera passou
        sucesso                            │
           │                               ▼
           └──────────────────────  entreaberto
                                    (deixa UM passar)

    O 'entreaberto' e o que evita a avalanche na volta: com cem threads
    esperando, abrir tudo de uma vez derruba o servico no instante em
    que ele volta.
    """

    def __init__(self, falhas=5, espera=30.0, nome=""):
        self.limite = max(1, int(falhas))
        self.espera = float(espera)
        self.nome = nome or "disjuntor"
        self._falhas = 0
        self._estado = "fechado"
        self._abriu_em = 0.0
        self._trava = threading.RLock()
        self.total_de_recusas = 0

    @property
    def estado(self):
        with self._trava:
            self._talvez_entreabrir()
            return self._estado

    @property
    def falhas(self):
        """Quantas falhas SEGUIDAS ele viu.

        Publico porque a conta que mais engana e esta: o disjuntor conta
        cada TENTATIVA, e um cliente com 'tentativas := 4' produz quatro
        falhas numa chamada so. Quem esta calibrando o limite precisa ver
        esse numero sem abrir o vault de 'resumo'.
        """
        with self._trava:
            return self._falhas

    def _talvez_entreabrir(self):
        if (self._estado == "aberto"
                and time.time() - self._abriu_em >= self.espera):
            self._estado = "entreaberto"

    def permite(self):
        """Devolve `no` quando a chamada nem deve ser tentada."""
        with self._trava:
            self._talvez_entreabrir()
            if self._estado == "aberto":
                self.total_de_recusas += 1
                return False
            return True

    def registrar_sucesso(self):
        with self._trava:
            self._falhas = 0
            self._estado = "fechado"

    def registrar_falha(self):
        with self._trava:
            self._falhas += 1
            if self._estado == "entreaberto":
                # A tentativa de sondagem falhou: volta a abrir, e o
                # relogio reinicia. Sem reiniciar, uma fila de threads
                # sondaria em rajada.
                self._estado = "aberto"
                self._abriu_em = time.time()
            elif self._falhas >= self.limite:
                self._estado = "aberto"
                self._abriu_em = time.time()

    def espera_restante(self):
        with self._trava:
            if self._estado != "aberto":
                return 0.0
            return max(0.0, self.espera - (time.time() - self._abriu_em))

    def resumo(self):
        with self._trava:
            self._talvez_entreabrir()
            return {
                "nome": self.nome,
                "estado": self._estado,
                "falhas": self._falhas,
                "limite": self.limite,
                "recusas": self.total_de_recusas,
                "espera_restante": round(self.espera_restante(), 2),
            }


# ═══════════════════════════════════════════════════════════
#  Recuo
# ═══════════════════════════════════════════════════════════

def recuo(tentativa, base=0.2, teto=10.0, tremor=True):
    """Quanto esperar antes da tentativa seguinte.

    Exponencial COM tremor. O tremor nao e refinamento: sem ele, cem
    clientes que falharam junto tentam de novo junto — e a rajada
    derruba o servico que estava se recuperando. E a diferenca entre
    uma recuperacao e um laco de queda.
    """
    espera = min(teto, base * (2 ** max(0, tentativa - 1)))
    if tremor:
        # Tremor cheio: uniforme entre 0 e a espera. Ele espalha melhor
        # que o parcial quando o numero de clientes e grande.
        espera = random.uniform(0, espera)
    return espera


# ═══════════════════════════════════════════════════════════
#  Cliente
# ═══════════════════════════════════════════════════════════

class Cliente:
    """Um cliente HTTP para chamada entre servicos.

    O que ele acrescenta ao 'urllib', e por que cada um importa:

    | O quê | Sem ele |
    |---|---|
    | prazo em TODA chamada | uma thread presa por servico, para sempre |
    | retry com recuo e tremor | a rajada derruba quem estava voltando |
    | disjuntor | o servico caido nunca se recupera |
    | propagacao de contexto | o rastro se perde na primeira fronteira |
    | so repetir o que e seguro | um POST repetido cobra duas vezes |
    """

    def __init__(self, base, opcoes=None):
        opcoes = opcoes or {}
        self.base = str(base).rstrip("/")
        self.prazo = float(opcoes.get("prazo", 5.0))
        self.tentativas = max(1, int(opcoes.get("tentativas", 3)))
        self.cabecalhos = dict(opcoes.get("cabecalhos", {}))
        self.nome = opcoes.get("nome", "") or _host_de(self.base)

        config = opcoes.get("disjuntor")
        if config is False:
            self.disjuntor = None
        else:
            config = config if isinstance(config, dict) else {}
            self.disjuntor = Disjuntor(
                falhas=config.get("falhas", 5),
                espera=config.get("espera", 30.0),
                nome=self.nome)

        self.recuo_base = float(opcoes.get("recuo", 0.2))
        self.recuo_teto = float(opcoes.get("recuo_teto", 10.0))
        self._trava = threading.RLock()
        self.metricas = {
            "chamadas": 0, "erros": 0, "retentativas": 0,
            "recusadas": 0, "ms_total": 0.0,
        }

    # ── Verbos ───────────────────────────────────────────────

    def get(self, caminho, query=None, cabecalhos=None, prazo=None):
        return self.pedir("GET", caminho, query=query,
                          cabecalhos=cabecalhos, prazo=prazo)

    def post(self, caminho, corpo=None, cabecalhos=None, prazo=None,
             chave=None):
        return self.pedir("POST", caminho, corpo=corpo,
                          cabecalhos=cabecalhos, prazo=prazo, chave=chave)

    def put(self, caminho, corpo=None, cabecalhos=None, prazo=None):
        return self.pedir("PUT", caminho, corpo=corpo,
                          cabecalhos=cabecalhos, prazo=prazo)

    def patch(self, caminho, corpo=None, cabecalhos=None, prazo=None,
              chave=None):
        return self.pedir("PATCH", caminho, corpo=corpo,
                          cabecalhos=cabecalhos, prazo=prazo, chave=chave)

    def delete(self, caminho, cabecalhos=None, prazo=None):
        return self.pedir("DELETE", caminho, cabecalhos=cabecalhos,
                          prazo=prazo)

    # ── O pedido ─────────────────────────────────────────────

    def pedir(self, metodo, caminho, corpo=None, query=None,
              cabecalhos=None, prazo=None, chave=None):
        """A chamada, com tudo o que ela precisa para nao mentir.

        Devolve um vault com 'status', 'body', 'headers', 'ok',
        'tentativas' e 'ms'. Um erro de REDE tambem devolve um vault —
        com 'status: 0' e 'erro' — em vez de levantar: quem chama um
        servico precisa decidir o que fazer, e 'monitor' em volta de
        cada chamada seria ruido.
        """
        metodo = metodo.upper()
        alvo = self._montar(caminho, query)
        prazo = float(prazo if prazo is not None else self.prazo)

        cabs = {
            "Accept": "application/json",
            "User-Agent": "DataForge-Malha/1.0",
        }
        cabs.update(Contexto.cabecalhos())
        cabs.update(self.cabecalhos)
        cabs.update(cabecalhos or {})
        if chave:
            # Com chave de idempotencia, um POST passa a ser seguro de
            # repetir — e e o servidor que garante isso, nao o cliente.
            cabs["Idempotency-Key"] = str(chave)

        dados = None
        if corpo is not None:
            if isinstance(corpo, (dict, list)):
                dados = json.dumps(_serializavel(corpo)).encode()
                cabs.setdefault("Content-Type", "application/json")
            elif isinstance(corpo, bytes):
                dados = corpo
            else:
                dados = str(corpo).encode()

        pode_repetir = metodo in IDEMPOTENTES or bool(chave)
        tentativas = self.tentativas if pode_repetir else 1

        if self.disjuntor is not None and not self.disjuntor.permite():
            with self._trava:
                self.metricas["recusadas"] += 1
            return {
                "ok": False, "status": 0, "body": None, "headers": {},
                "erro": f"disjuntor aberto para '{self.nome}'",
                "disjuntor": self.disjuntor.estado,
                "espera_restante": self.disjuntor.espera_restante(),
                "tentativas": 0, "ms": 0.0,
            }

        comeco = time.perf_counter()
        ultima = None
        for tentativa in range(1, tentativas + 1):
            resposta = self._uma_vez(metodo, alvo, dados, cabs, prazo)
            resposta["tentativas"] = tentativa

            if resposta["ok"] or not _vale_repetir(resposta):
                if resposta["ok"] and self.disjuntor is not None:
                    self.disjuntor.registrar_sucesso()
                elif not resposta["ok"] and self.disjuntor is not None:
                    # 4xx nao e falha do SERVICO: o pedido esta errado.
                    # Contar isso abriria o disjuntor por causa de um bug
                    # de quem chama.
                    if resposta["status"] == 0 or resposta["status"] >= 500:
                        self.disjuntor.registrar_falha()
                break

            ultima = resposta
            if self.disjuntor is not None:
                self.disjuntor.registrar_falha()
            with self._trava:
                self.metricas["retentativas"] += 1
            if tentativa < tentativas:
                # 'Retry-After' do servidor vence o nosso calculo: ele
                # sabe quando vai estar pronto, e ignorar isso e insistir
                # contra quem pediu para esperar.
                #
                # 'is not None', e nao 'or': 'Retry-After: 0' significa
                # "tente agora", e 0.0 e FALSO em Python — com 'or', o
                # zero caia no recuo e o cliente esperava os segundos
                # que o servidor acabara de dizer que nao eram
                # necessarios.
                pedida = _retry_after(resposta)
                espera = pedida if pedida is not None else recuo(
                    tentativa, self.recuo_base, self.recuo_teto)
                time.sleep(espera)
        else:
            resposta = ultima or resposta

        resposta["ms"] = round((time.perf_counter() - comeco) * 1000, 2)
        with self._trava:
            self.metricas["chamadas"] += 1
            self.metricas["ms_total"] += resposta["ms"]
            if not resposta["ok"]:
                self.metricas["erros"] += 1
        return resposta

    def _uma_vez(self, metodo, alvo, dados, cabs, prazo):
        pedido = urllib.request.Request(alvo, data=dados, method=metodo,
                                        headers=cabs)
        try:
            with urllib.request.urlopen(pedido, timeout=prazo) as r:
                bruto = r.read()
                return {
                    "ok": 200 <= r.status < 300,
                    "status": r.status,
                    "headers": {k.lower(): v for k, v in r.headers.items()},
                    "body": _interpretar(bruto, r.headers.get("content-type")),
                    "raw_body": bruto,
                }
        except urllib.error.HTTPError as erro:
            bruto = erro.read()
            return {
                "ok": False,
                "status": erro.code,
                "headers": {k.lower(): v for k, v in erro.headers.items()}
                           if erro.headers else {},
                "body": _interpretar(bruto, (erro.headers or {}).get(
                    "content-type")),
                "raw_body": bruto,
                "erro": f"HTTP {erro.code}",
            }
        except (urllib.error.URLError, TimeoutError, OSError) as erro:
            # 'status: 0' significa "nao chegou". E o terceiro estado —
            # e ele precisa ser distinguivel de um 500, porque um 500
            # foi processado e um 0 talvez nao.
            return {
                "ok": False, "status": 0, "headers": {}, "body": None,
                "erro": f"{type(erro).__name__}: {erro}",
            }

    def _montar(self, caminho, query):
        alvo = self.base + "/" + str(caminho).lstrip("/")
        if query:
            alvo += ("&" if "?" in alvo else "?") + urllib.parse.urlencode(
                {k: v for k, v in query.items() if v is not None}, doseq=True)
        return alvo

    # ── Observar ─────────────────────────────────────────────

    def resumo(self):
        with self._trava:
            m = dict(self.metricas)
        chamadas = m["chamadas"] or 1
        saida = {
            "servico": self.nome,
            "base": self.base,
            "chamadas": m["chamadas"],
            "erros": m["erros"],
            "retentativas": m["retentativas"],
            "recusadas": m["recusadas"],
            "media_ms": round(m["ms_total"] / chamadas, 2),
        }
        if self.disjuntor is not None:
            saida["disjuntor"] = self.disjuntor.resumo()
        return saida


# ═══════════════════════════════════════════════════════════
#  Descoberta
# ═══════════════════════════════════════════════════════════

class Registro:
    """Onde cada servico esta.

    Nao e um registro distribuido — e um vault com um fallback para
    variavel de ambiente. Isso cobre o caso real de quase todo mundo:
    Docker Compose e Kubernetes resolvem nome por DNS, e o que falta e
    nao cravar 'http://localhost:8080' no codigo.

        Malha.registrar("pedidos", "http://pedidos:8080")
        cliente := Malha.de("pedidos")

    O nome vira 'PEDIDOS_URL' como variavel de ambiente, que e a
    convencao que o Compose e o Kubernetes ja produzem.
    """

    def __init__(self):
        self._servicos = {}
        self._clientes = {}
        self._padrao = {}
        self._trava = threading.RLock()

    def registrar(self, nome, base, opcoes=None):
        with self._trava:
            self._servicos[str(nome)] = (str(base), dict(opcoes or {}))
            self._clientes.pop(str(nome), None)
        return nome

    def padrao(self, opcoes):
        """As opcoes de todo cliente criado daqui para frente."""
        with self._trava:
            self._padrao.update(opcoes or {})
        return dict(self._padrao)

    def onde(self, nome):
        """A URL do servico, ou `void`."""
        import os

        nome = str(nome)
        with self._trava:
            if nome in self._servicos:
                return self._servicos[nome][0]
        # A convencao do Compose e do Kubernetes.
        for variavel in (f"{nome.upper().replace('-', '_')}_URL",
                         f"{nome.upper().replace('-', '_')}_HOST"):
            valor = os.environ.get(variavel)
            if valor:
                return valor if "://" in valor else f"http://{valor}"
        return None

    def de(self, nome, opcoes=None):
        """O cliente do servico. Reaproveitado entre chamadas.

        Reaproveitar importa: o disjuntor e as metricas vivem NO
        cliente, e um cliente novo por chamada esqueceria que o servico
        esta caido — o que anula o disjuntor inteiro.
        """
        nome = str(nome)
        with self._trava:
            if nome in self._clientes and not opcoes:
                return self._clientes[nome]

        base = self.onde(nome)
        if base is None:
            from ..errors import RuntimeError_
            variavel = f"{nome.upper().replace('-', '_')}_URL"
            raise RuntimeError_(
                f"nao sei onde esta o servico '{nome}'.", 0, 0,
                nota=f"procurei no registro e na variavel {variavel}",
                dica=f'Malha.registrar("{nome}", "http://{nome}:8080"), '
                     f"ou defina {variavel}",
                doc="tecnicas/microservicos")

        with self._trava:
            _, guardadas = self._servicos.get(nome, (None, {}))
            config = {**self._padrao, **guardadas, **(opcoes or {})}
            config.setdefault("nome", nome)
            cliente = Cliente(base, config)
            if not opcoes:
                self._clientes[nome] = cliente
            return cliente

    def servicos(self):
        with self._trava:
            nomes = sorted(set(self._servicos))
        return [{"nome": n, "base": self.onde(n)} for n in nomes]

    def saude(self):
        """O estado de cada cliente ativo — para uma rota de diagnostico."""
        with self._trava:
            clientes = dict(self._clientes)
        return [c.resumo() for c in clientes.values()]


#: Um registro por processo. Ele guarda os clientes, e portanto os
#: disjuntores: dois registros fariam cada metade do programa ter sua
#: propria opiniao sobre quais servicos estao de pe.
REGISTRO = Registro()


# ═══════════════════════════════════════════════════════════
#  Utilidades
# ═══════════════════════════════════════════════════════════

def _vale_repetir(resposta):
    if resposta["status"] == 0:
        return True        # nao chegou: vale tentar
    return resposta["status"] in RETENTAVEIS


def _retry_after(resposta):
    """O 'Retry-After' do servidor, em segundos.

    Ele sabe quando vai estar pronto, e ignorar isso e insistir contra
    quem pediu para esperar. O teto de 60 s evita que um cabecalho
    absurdo prenda a thread por uma hora.
    """
    bruto = (resposta.get("headers") or {}).get("retry-after")
    if not bruto:
        return None
    try:
        return min(60.0, max(0.0, float(bruto)))
    except (TypeError, ValueError):
        return None


def _interpretar(bruto, tipo):
    if not bruto:
        return None
    texto = bruto.decode("utf-8", errors="replace")
    if tipo and "json" in tipo.lower():
        try:
            return json.loads(texto)
        except ValueError:
            return texto
    return texto


def _host_de(base):
    try:
        return urllib.parse.urlsplit(base).hostname or base
    except ValueError:
        return base


def _serializavel(valor):
    if isinstance(valor, dict):
        return {str(k): _serializavel(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_serializavel(v) for v in valor]
    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor
    if hasattr(valor, "fields"):
        return _serializavel(dict(valor.fields))
    return str(valor)


# ═══════════════════════════════════════════════════════════
#  O modulo
# ═══════════════════════════════════════════════════════════

class Passo:
    """Um passo da saga: o que fazer, e como desfazer.

    `desfazer` e opcional, e a ausencia dele e uma DECLARACAO: este
    passo nao precisa ser compensado (uma leitura, um log). Um passo
    que escreve e nao declara compensacao e o bug que a saga existe
    para prevenir, e `Saga.conferir` acusa.
    """

    __slots__ = ("nome", "fazer", "desfazer", "escreve", "chave")

    def __init__(self, nome, fazer, desfazer=None, escreve=True, chave=None):
        self.nome = str(nome)
        self.fazer = fazer
        self.desfazer = desfazer
        self.escreve = bool(escreve)
        self.chave = chave

    def __repr__(self):
        marca = "" if self.desfazer is not None else " (sem compensacao)"
        return f"<passo {self.nome}{marca}>"


class Saga:
    """Escritas em servicos diferentes que precisam acontecer juntas.

    Nao existe transacao que atravesse a rede: `BEGIN` no servico de
    estoque nao alcanca o de cobranca. A unica resposta correta e
    **compensar** — cada passo declara como se desfaz, e uma falha no
    meio desfaz em ordem inversa o que ja aconteceu.

        reservar ──▶ cobrar ──▶ despachar
                       │
                     falhou
                       │
                       ▼
        liberar  ◀── (nada a estornar: cobrar nao concluiu)

    Tres coisas que a diferenciam de um `monitor` com `ensure`:

    1. **A compensacao roda em ordem inversa.** Estornar a cobranca
       antes de liberar o estoque deixa uma janela em que o cliente
       nao tem dinheiro nem produto.

    2. **Uma compensacao que falha NAO e engolida.** Um estorno que
       nao passa deixa o sistema inconsistente, e isso precisa chegar
       a um humano — `resultado["orfas"]` e a lista, e `ok` continua
       `no` mesmo que o resto tenha desfeito.

    3. **Cada passo tem uma chave de idempotencia estavel**, derivada
       do id da saga e do nome do passo. Repetir a saga inteira depois
       de uma queda nao cobra duas vezes, desde que o servico do outro
       lado honre a chave.

    O que ela **nao** faz: nao ha isolamento. Entre `reservar` e
    `cobrar`, outro pedido ve o estoque ja reservado. Saga troca
    atomicidade por disponibilidade, e essa troca e o ponto — quem
    precisa de isolamento precisa de um banco, nao de microservicos.
    """

    def __init__(self, nome="saga", identificador=None, registro=None):
        self.nome = str(nome)
        self.id = str(identificador or uuid.uuid4())
        self.passos = []
        self.estado = {}
        #: O que aconteceu, em ordem. E o unico jeito de responder
        #: "onde isso parou" depois do fato.
        self.diario = []
        #: Para onde escrever o diario a cada passo. Sem isso, uma
        #: queda do processo no meio da saga perde o que ja foi feito
        #: — e ninguem sabe o que compensar.
        self.registro = registro
        self._concluidos = []

    # ── montar ───────────────────────────────────────────────

    def passo(self, nome, fazer, desfazer=None, escreve=True, chave=None):
        """Acrescenta um passo. Devolve a saga, para encadear."""
        if not callable(fazer):
            raise ValueError(
                f"passo '{nome}': 'fazer' precisa ser uma acao")
        if desfazer is not None and not callable(desfazer):
            raise ValueError(
                f"passo '{nome}': 'desfazer' precisa ser uma acao")
        self.passos.append(Passo(nome, fazer, desfazer, escreve, chave))
        return self

    def conferir(self):
        """Os passos que escrevem e nao declaram compensacao.

        Roda ANTES de executar. Um passo assim nao e erro de sintaxe
        nem falha em teste feliz: ele so aparece no dia em que o passo
        seguinte falha, e ai ja escreveu.
        """
        return [p.nome for p in self.passos
                if p.escreve and p.desfazer is None]

    # ── executar ─────────────────────────────────────────────

    def chave_de(self, nome):
        """A chave de idempotencia deste passo, estavel entre execucoes."""
        for p in self.passos:
            if p.nome == nome and p.chave:
                return str(p.chave)
        return f"{self.id}:{nome}"

    def executar(self, estado=None):
        """Roda os passos; desfaz o que deu se algum falhar.

        Devolve um vault, nunca levanta: uma saga que levanta perde a
        informacao de quanto ela conseguiu desfazer, que e justamente
        o que se precisa saber.
        """
        if estado:
            self.estado.update(estado)
        self._concluidos = []
        comeco = time.perf_counter()

        for passo in self.passos:
            entrada = time.perf_counter()
            try:
                saida = passo.fazer(self.estado, self.chave_de(passo.nome))
            except BaseException as erro:   # noqa: BLE001
                if not isinstance(erro, Exception):
                    raise           # halt, skip, yield atravessam
                self._anotar(passo.nome, "falhou", str(erro),
                             (time.perf_counter() - entrada) * 1000)
                desfeitos, orfas = self._desfazer()
                return {
                    "ok": False,
                    "saga": self.nome,
                    "id": self.id,
                    "falhou_em": passo.nome,
                    "erro": str(erro),
                    "concluidos": [],
                    "desfeitos": desfeitos,
                    "orfas": orfas,
                    "estado": dict(self.estado),
                    "diario": list(self.diario),
                    "ms": (time.perf_counter() - comeco) * 1000,
                }

            if isinstance(saida, dict):
                self.estado.update(saida)
            elif saida is not None:
                self.estado[passo.nome] = saida
            self._concluidos.append(passo)
            self._anotar(passo.nome, "feito", "",
                         (time.perf_counter() - entrada) * 1000)

        return {
            "ok": True,
            "saga": self.nome,
            "id": self.id,
            "falhou_em": "",
            "erro": "",
            "concluidos": [p.nome for p in self._concluidos],
            "desfeitos": [],
            "orfas": [],
            "estado": dict(self.estado),
            "diario": list(self.diario),
            "ms": (time.perf_counter() - comeco) * 1000,
        }

    def _desfazer(self):
        """Compensa o que concluiu, em ordem INVERSA.

        A ordem importa de verdade: estornar a cobranca antes de
        liberar o estoque deixa uma janela em que o cliente nao tem
        dinheiro nem produto. E uma compensacao que falha nao para as
        outras — o estoque preso por um estorno que nao passou seria
        um segundo problema criado pelo primeiro.
        """
        desfeitos = []
        orfas = []
        for passo in reversed(self._concluidos):
            if passo.desfazer is None:
                continue
            entrada = time.perf_counter()
            try:
                passo.desfazer(self.estado, self.chave_de(passo.nome))
            except BaseException as erro:   # noqa: BLE001
                if not isinstance(erro, Exception):
                    raise
                orfas.append({"passo": passo.nome, "erro": str(erro)})
                self._anotar(passo.nome, "orfa", str(erro),
                             (time.perf_counter() - entrada) * 1000)
            else:
                desfeitos.append(passo.nome)
                self._anotar(passo.nome, "desfeito", "",
                             (time.perf_counter() - entrada) * 1000)
        return desfeitos, orfas

    # ── diario ───────────────────────────────────────────────

    def _anotar(self, passo, situacao, detalhe, ms):
        linha = {
            "saga": self.nome, "id": self.id, "passo": passo,
            "situacao": situacao, "detalhe": detalhe,
            "ms": round(ms, 2), "em": time.time(),
            "rastro": ArcaneMalha._rastro(),
        }
        self.diario.append(linha)
        if self.registro is not None:
            try:
                self.registro(linha)
            except Exception:
                # Um diario que nao grava nao pode derrubar a saga: ela
                # esta no meio de escritas reais em servicos reais.
                pass
        return linha

    def __repr__(self):
        return f"<saga {self.nome} {len(self.passos)} passo(s)>"


class ArcaneMalha:
    """Arcane.Malha — chamada entre servicos que nao mente."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Malha",

            # ── cliente ──
            "cliente": cls._cliente,
            "Cliente": Cliente,

            # ── descoberta ──
            "registrar": cls._registrar,
            "de": cls._de,
            "onde": cls._onde,
            "servicos": cls._servicos,
            "padrao": cls._padrao,

            # ── disjuntor ──
            "disjuntor": cls._disjuntor,
            "Disjuntor": Disjuntor,

            # ── contexto ──
            "contexto": cls._contexto,
            "comecar_contexto": cls._comecar_contexto,
            "terminar_contexto": cls._terminar_contexto,
            "rastro": cls._rastro,
            "cabecalhos_de_contexto": cls._cabecalhos,
            "propagar": cls._propagar,

            # ── saga: escritas que precisam acontecer juntas ──
            "saga": cls._saga,
            "Saga": Saga,
            "Passo": Passo,

            # ── observar ──
            "saude": cls._saude,
            "resumo": cls._resumo,

            # ── auxiliares ──
            "recuo": recuo,
            "vale_repetir": _vale_repetir,
            "RETENTAVEIS": sorted(RETENTAVEIS),
        }

    @staticmethod
    def _cliente(base, opcoes=None):
        """Um cliente HTTP resiliente para um servico."""
        return Cliente(base, opcoes)

    @staticmethod
    def _registrar(nome, base, opcoes=None):
        return REGISTRO.registrar(nome, base, opcoes)

    @staticmethod
    def _de(nome, opcoes=None):
        return REGISTRO.de(nome, opcoes)

    @staticmethod
    def _onde(nome):
        return REGISTRO.onde(nome)

    @staticmethod
    def _servicos():
        return REGISTRO.servicos()

    @staticmethod
    def _padrao(opcoes):
        return REGISTRO.padrao(opcoes)

    @staticmethod
    def _disjuntor(falhas=5, espera=30.0, nome=""):
        return Disjuntor(falhas, espera, nome)

    @staticmethod
    def _contexto():
        """O contexto de agora, ou `void`."""
        return Contexto.atual()

    @staticmethod
    def _comecar_contexto(rastro=None, origem="", extra=None):
        return Contexto.comecar(rastro, origem, extra)

    @staticmethod
    def _terminar_contexto():
        return Contexto.terminar()

    @staticmethod
    def _rastro():
        """O id do pedido atual. Serve para pôr no log."""
        dados = Contexto.atual()
        return dados["rastro"] if dados else ""

    @staticmethod
    def _cabecalhos():
        return Contexto.cabecalhos()

    @staticmethod
    def _propagar(req, origem=""):
        """Começa o contexto a partir de um pedido que CHEGOU.

        É a metade que falta da propagação: sem ela, cada serviço
        começa um rastro novo e a corrente se quebra na fronteira.

            middleware action (req):
                Malha.propagar(req, "pedidos")
                yield void
        """
        cabs = req.get("headers") or {}
        rastro = (cabs.get(CABECALHO_RASTRO.lower())
                  or cabs.get(CABECALHO_RASTRO))
        extra = {k[len("x-ctx-"):]: v for k, v in cabs.items()
                 if k.lower().startswith("x-ctx-")}
        dados = Contexto.comecar(rastro, origem, extra)
        # O rastro tambem entra no estado do pedido, para o handler e o
        # log do Kiln o alcancarem sem passar pelo contexto.
        if isinstance(req.get("state"), dict):
            req["state"]["rastro"] = dados["rastro"]
        return dados

    @staticmethod
    def _saga(nome="saga", identificador=None, registro=None):
        """Uma saga: passos com compensacao, para escritas em servicos
        diferentes que precisam acontecer juntas.

            s := Malha.saga("checkout")
            s.passo("reservar", reservar, liberar)
            s.passo("cobrar", cobrar, estornar)
            r := s.executar({"pedido": 42})
            given not r["ok"]:
                out $"parou em {r['falhou_em']}, desfeitos: {r['desfeitos']}"
        """
        return Saga(nome, identificador, registro)

    @staticmethod
    def _saude():
        return REGISTRO.saude()

    @staticmethod
    def _resumo():
        return {
            "servicos": REGISTRO.servicos(),
            "clientes": REGISTRO.saude(),
            "rastro_atual": ArcaneMalha._rastro(),
        }
