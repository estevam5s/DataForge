# -*- coding: utf-8 -*-
"""Arcane.Privacidade — o que a LGPD pede, como operações sobre dado.

`Arcane.Seguranca` protege o sistema de quem ataca. Este módulo protege
**o titular** do próprio sistema: o que se guarda, por quanto tempo, com
que autorização, e o que sai num relatório. As distinções que ele cobra
são as que a lei faz e que o código costuma apagar:

**Pseudonimizar não é anonimizar.** Um hash de CPF sem chave se desfaz
com uma tabela: são só 10⁹ CPFs possíveis, e um laptop os calcula numa
tarde. `pseudonimizar` usa HMAC com uma chave que mora fora da base — o
dado continua pessoal (a LGPD diz isso), mas deixa de ser legível por
quem só tem a base.

**Tirar o nome não anonimiza.** CEP, data de nascimento e sexo
identificam a maioria das pessoas de um país. `k_anonimato` mede o menor
grupo de linhas indistinguíveis pelos quase-identificadores, e
`generalizar` é o que se faz quando esse número é 1.

**Consentimento é por finalidade.** Concordar com "receber a nota
fiscal por e-mail" não autoriza "marketing". `consentimentos()` guarda
cada finalidade separada, com a data e a versão do termo, e a revogação
vale dali em diante — o histórico continua, porque provar que havia
consentimento no dia é a pergunta da fiscalização.

O que ele **não** é: não é parecer jurídico, e não decide a base legal
de um tratamento. Ele torna as decisões registráveis e conferíveis.
"""

import hashlib
import hmac as _hmac
import math
import random as _random
import time


def _erro(mensagem, nota="", dica="", doc="biblioteca/privacidade"):
    from ..errors import RuntimeError_
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=doc)


def _campo(linha, nome):
    if isinstance(linha, dict):
        return linha.get(nome)
    return getattr(linha, nome, None)


# ═══════════════════════════════════════════════════════════
#  Pseudonimizar e generalizar
# ═══════════════════════════════════════════════════════════

def pseudonimizar(valor, chave, finalidade="", tamanho=16):
    """Um apelido estável para o valor — HMAC-SHA256 com uma chave.

    Estável: o mesmo CPF dá o mesmo apelido, e as junções entre tabelas
    continuam funcionando. Sem a chave, não se volta ao CPF — e com ela
    também não: não há "decifrar", só recalcular.

    `finalidade` separa os contextos: o apelido do CPF no relatório de
    vendas não casa com o do relatório de RH, e cruzar os dois exige a
    chave, e não só as duas planilhas.
    """
    if not chave or len(str(chave)) < 16:
        raise _erro(
            "a chave de pseudonimizacao precisa de pelo menos 16 caracteres.",
            nota="um hash sem chave (ou com chave curta) de um CPF se desfaz "
                 "calculando os 10^9 CPFs possiveis — uma tarde num laptop.",
            dica="gere com Crypto.random_token() e guarde FORA da base.")
    if valor is None:
        return None
    msg = f"{finalidade}\x1f{str(valor).strip()}".encode("utf-8")
    digest = _hmac.new(str(chave).encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return digest[:max(8, min(int(tamanho), 64))]


def generalizar(valor, tipo, nivel=1):
    """Tira precisão de um quase-identificador.

    | tipo | nivel 1 | nivel 2 |
    |---|---|---|
    | `idade` | faixa de 10 (`30-39`) | faixa de 20 |
    | `cep` | 5 dígitos (`01310-***`) | 3 dígitos |
    | `data` | mês (`2026-09`) | ano |
    | `numero` | dezena | centena |

    Generalizar é a resposta quando `k_anonimato` dá 1: menos precisão,
    grupos maiores, e ninguém fica sozinho numa linha.
    """
    if valor is None:
        return None
    nivel = max(1, int(nivel))
    if tipo == "idade":
        largura = 10 * nivel
        base = (int(valor) // largura) * largura
        return f"{base}-{base + largura - 1}"
    if tipo == "cep":
        digitos = "".join(c for c in str(valor) if c.isdigit())
        if len(digitos) != 8:
            raise _erro(f"'{valor}' nao e um CEP de 8 digitos.")
        manter = 5 if nivel == 1 else 3
        mascarado = digitos[:manter] + "*" * (8 - manter)
        return f"{mascarado[:5]}-{mascarado[5:]}"
    if tipo == "data":
        texto = str(valor)
        return texto[:7] if nivel == 1 else texto[:4]
    if tipo == "numero":
        passo = 10 ** nivel
        return int(float(valor) // passo * passo)
    raise _erro(f"nao sei generalizar o tipo '{tipo}'. Use idade, cep, data ou numero.")


def k_anonimato(linhas, quase_identificadores):
    """O menor grupo de linhas indistinguíveis pelos quase-identificadores.

    `k = 1` quer dizer que alguém está **sozinho** numa combinação — e
    quem conhece essa combinação (o CEP e a idade de um vizinho) acha a
    linha dele, com todo o resto que ela carrega. Devolve `{k, grupos,
    menores}` — os menores são as combinações a generalizar primeiro.
    """
    linhas = list(linhas or [])
    campos = list(quase_identificadores or [])
    if not campos:
        raise _erro("k_anonimato precisa dos quase-identificadores (ex.: cep, idade, sexo).")
    contagem = {}
    for l in linhas:
        chave = tuple(str(_campo(l, c)) for c in campos)
        contagem[chave] = contagem.get(chave, 0) + 1
    if not contagem:
        return {"k": 0, "grupos": 0, "menores": []}
    k = min(contagem.values())
    menores = [dict(zip(campos, chave)) for chave, n in sorted(contagem.items())
               if n == k][:10]
    return {"k": k, "grupos": len(contagem), "menores": menores}


def minimizar(linha, permitidos):
    """Só os campos que a finalidade precisa — o resto não sai.

    É uma lista de **permitidos**, e não de proibidos: um campo novo na
    tabela (o CPF que alguém acrescentou ontem) fica fora do relatório
    até alguém decidir que ele entra.
    """
    permitidos = list(permitidos or [])
    if isinstance(linha, list):
        return [minimizar(l, permitidos) for l in linha]
    return {c: _campo(linha, c) for c in permitidos}


# ═══════════════════════════════════════════════════════════
#  Retenção
# ═══════════════════════════════════════════════════════════

def vencidos(linhas, campo_data, dias, agora=None):
    """As linhas cujo prazo de retenção passou.

    `campo_data` é um instante em segundos (ou texto ISO `AAAA-MM-DD`).
    Uma linha **sem** data volta como vencida: um registro que não diz
    quando nasceu não tem como provar que ainda pode ser guardado.
    """
    agora = time.time() if agora is None else float(agora)
    limite = agora - float(dias) * 86400
    saida = []
    for l in linhas or []:
        v = _campo(l, campo_data)
        if v is None or v == "":
            saida.append(l)
            continue
        if isinstance(v, str):
            try:
                v = time.mktime(time.strptime(v[:10], "%Y-%m-%d"))
            except ValueError:
                saida.append(l)
                continue
        if float(v) < limite:
            saida.append(l)
    return saida


# ═══════════════════════════════════════════════════════════
#  Consentimento
# ═══════════════════════════════════════════════════════════

class Consentimentos:
    """O registro de consentimentos — por titular E por finalidade.

    Três regras:

    1. **Uma finalidade por vez.** `conceder(titular, "marketing")` não
       autoriza "pesquisa".
    2. **A revogação não apaga o passado.** Ela acrescenta um evento; a
       pergunta "havia consentimento no dia 3?" continua respondível.
    3. **O termo tem versão.** Consentir com a versão 1 não é consentir
       com a 2, que acrescentou compartilhamento com terceiros.
    """

    def __init__(self):
        self._eventos = []

    def __repr__(self):
        return f"<Consentimentos: {len(self._eventos)} evento(s)>"

    def conceder(self, titular, finalidade, versao="1", quando=None):
        self._eventos.append({"titular": str(titular), "finalidade": str(finalidade),
                              "versao": str(versao), "concedido": True,
                              "quando": time.time() if quando is None else float(quando)})
        return self

    def revogar(self, titular, finalidade, quando=None):
        self._eventos.append({"titular": str(titular), "finalidade": str(finalidade),
                              "versao": "", "concedido": False,
                              "quando": time.time() if quando is None else float(quando)})
        return self

    def _estado(self, titular, finalidade, ate):
        ultimo = None
        for e in self._eventos:
            if e["titular"] == str(titular) and e["finalidade"] == str(finalidade) \
                    and e["quando"] <= ate:
                if ultimo is None or e["quando"] >= ultimo["quando"]:
                    ultimo = e
        return ultimo

    def pode(self, titular, finalidade, versao="", quando=None):
        """`yes` se havia consentimento vigente (na versão pedida, se houver)."""
        ate = time.time() if quando is None else float(quando)
        e = self._estado(titular, finalidade, ate)
        if e is None or not e["concedido"]:
            return False
        return not versao or e["versao"] == str(versao)

    def historico(self, titular):
        return [dict(e) for e in self._eventos if e["titular"] == str(titular)]

    def finalidades(self, titular):
        """As finalidades vigentes agora."""
        nomes = {e["finalidade"] for e in self._eventos if e["titular"] == str(titular)}
        return sorted(f for f in nomes if self.pode(titular, f))


def consentimentos():
    return Consentimentos()


# ═══════════════════════════════════════════════════════════
#  Direitos do titular
# ═══════════════════════════════════════════════════════════

class Titulares:
    """Onde moram os dados de um titular — para exportar e para esquecer.

    O direito de acesso e o de eliminação falham do mesmo jeito: o dado
    está em onze lugares, e o pedido é atendido em nove. Aqui cada lugar
    **se registra** com uma ação que exporta e outra que apaga, e o
    atendimento percorre todos — e diz quais falharam, em vez de
    responder "feito".
    """

    def __init__(self):
        self._lugares = []

    def __repr__(self):
        return f"<Titulares: {len(self._lugares)} lugar(es) registrado(s)>"

    def registrar(self, nome, exportar, apagar):
        if not callable(exportar) or not callable(apagar):
            raise _erro(f"'{nome}': exportar e apagar precisam ser acoes.")
        self._lugares.append((str(nome), exportar, apagar))
        return self

    def exportar(self, titular):
        dados, falhas = {}, {}
        for nome, exp, _ap in self._lugares:
            try:
                dados[nome] = exp(titular)
            except Exception as e:      # noqa: BLE001 — a falha vai no relatorio
                falhas[nome] = getattr(e, "message", None) or str(e)
        return {"titular": titular, "dados": dados, "falhas": falhas,
                "completo": not falhas}

    def esquecer(self, titular):
        apagados, falhas = [], {}
        for nome, _exp, ap in self._lugares:
            try:
                ap(titular)
                apagados.append(nome)
            except Exception as e:      # noqa: BLE001
                falhas[nome] = getattr(e, "message", None) or str(e)
        return {"titular": titular, "apagados": apagados, "falhas": falhas,
                "completo": not falhas}


def titulares():
    return Titulares()


# ═══════════════════════════════════════════════════════════
#  Contagem com privacidade diferencial
# ═══════════════════════════════════════════════════════════

def contagem_privada(n, epsilon=1.0, semente=None):
    """Uma contagem com ruído de Laplace — privacidade diferencial.

    Publicar *"3 pessoas com a doença X no bairro Y"* identifica as três.
    Com ruído de escala `1/ε`, a presença ou ausência de **uma** pessoa
    muda pouco a distribuição do número publicado. `ε` menor protege
    mais e erra mais; e cada publicação gasta orçamento — publicar a
    mesma contagem cem vezes com ruído novo deixa a média revelar o valor.

    O resultado é arredondado e nunca negativo: pós-processar não gasta
    privacidade, e uma contagem negativa só confundiria quem lê.
    """
    epsilon = float(epsilon)
    if epsilon <= 0:
        raise _erro("epsilon precisa ser positivo — menor protege mais e erra mais.")
    gerador = _random.Random(semente) if semente is not None else _random.SystemRandom()
    u = gerador.random() - 0.5
    ruido = -(1.0 / epsilon) * math.copysign(1.0, u) * math.log(1 - 2 * abs(u))
    return max(0, int(round(float(n) + ruido)))


class ArcanePrivacidade:
    """Arcane.Privacidade — pseudonimização, k-anonimato, retenção,
    consentimento, direitos do titular e contagem privada."""

    def __new__(cls):
        return {
            "pseudonimizar": pseudonimizar,
            "generalizar": generalizar,
            "k_anonimato": k_anonimato,
            "minimizar": minimizar,
            "vencidos": vencidos,
            "consentimentos": consentimentos,
            "titulares": titulares,
            "contagem_privada": contagem_privada,
            "Consentimentos": Consentimentos,
            "Titulares": Titulares,
        }
