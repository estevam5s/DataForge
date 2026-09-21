# -*- coding: utf-8 -*-
"""Arcane.Chaves — a chave tem dono, prazo e propósito.

    adopt Arcane.Chaves as Ch

    cofre := Ch.cofre()
    k := cofre.gerar("sessao", proposito := "assinar", prazo := 86400)

    assinatura := Ch.usar(k, "assinar")     // devolve o material
    Ch.usar(k, "cifrar")                    // erro: propósito errado

─── O problema que este módulo resolve ─────────────────────

`Crypto` gera bytes aleatórios e cifra com eles. O que ele não tem é o
**ciclo de vida**: de onde a chave veio, até quando vale, para que
serve, e o que fazer com o dado cifrado pela versão anterior.

Sem isso, o que acontece na prática é sempre o mesmo: uma chave nasce
numa variável de ambiente, é usada para tudo, e nunca é trocada —
porque trocá-la tornaria ilegível tudo que já foi cifrado.

─── As quatro decisões ─────────────────────────────────────

| Decisão | Sem ela |
|---|---|
| **a chave tem propósito** | a que assina token também decifra arquivo, e um comprometimento vira todos |
| **a rotação mantém as antigas** | trocar a chave torna ilegível o que já foi cifrado — então ninguém troca |
| **o dado carrega o `kid`** | na hora de decifrar não se sabe qual das cinco chaves usar |
| **o material não aparece em texto** | o `Segredo` do `Arcane.Seguranca` é a mesma decisão, e pelo mesmo motivo |

─── Envelope: a chave de dados é cifrada pela chave mestra ──

Cifrar um terabyte com a chave mestra significa que rotacioná-la é
reescrever o terabyte. Com envelope, cada objeto tem a **sua** chave
de dados (DEK), e o que a chave mestra (KEK) cifra é só a DEK — 32
bytes. Rotacionar a mestra passa a ser recifrar as DEKs, e não os
dados.

É o que KMS, Vault e as três nuvens fazem, e o motivo é este.

─── O que ele NÃO é ────────────────────────────────────────

**Não é um HSM nem um KMS.** O material vive na memória deste
processo, e quem lê a memória lê a chave. Um HSM existe justamente
para que a chave nunca saia dele — e isso é hardware, não biblioteca.

**Não persiste sozinho.** `exportar()` devolve o cofre cifrado pela
senha mestra, e gravar é decisão de quem chama. Um cofre que escolhe
onde gravar escolheria errado em metade dos casos.

**Não há chave assimétrica.** RSA e curva elíptica em Python puro são
lentas e são exatamente onde um erro de implementação vira falha
silenciosa. Para assinatura com prova perante terceiro, um serviço.
"""

import base64
import hashlib
import hmac
import json
import os
import threading
import time

from ..builtins import _df_type as _nome_do_tipo
from .opcoes import ler as _ler_opcoes

_DOC = "seguranca/chaves"

#: Os propósitos que uma chave pode ter. A lista é FECHADA.
#:
#: Aceitar qualquer texto faria `"asinar"` criar um propósito novo em
#: silêncio, e a chave passaria a não servir para nada — sem erro, e
#: com a descoberta na primeira verificação que falha.
PROPOSITOS = ("assinar", "cifrar", "derivar", "autenticar")

#: Os estados. Um estado a mais é onde "mais ou menos" se esconderia.
ESTADOS = ("ativa", "aposentada", "revogada")


def _erro(mensagem, nota="", dica="", classe="CryptoKeyError"):
    from .. import errors

    alvo = errors.erro_por_nome(classe) or errors.RuntimeError_
    return alvo(str(mensagem), 0, 0, nota=nota, dica=dica, doc=_DOC)


def _b64(dados):
    return base64.urlsafe_b64encode(dados).decode("ascii").rstrip("=")


def _de_b64(texto):
    t = str(texto)
    return base64.urlsafe_b64decode(t + "=" * (-len(t) % 4))


class Chave:
    """Uma chave: material, propósito, prazo e estado.

    O material **não aparece em texto**. `__str__`, `__repr__` e
    `__format__` dão o `kid` e o propósito — nunca os bytes. É a mesma
    decisão do `Seguranca.segredo`, e pelo mesmo motivo: o vazamento
    mais comum é alguém imprimir o objeto para depurar.
    """

    __slots__ = ("kid", "proposito", "criada", "vence", "estado",
                 "rotulo", "_material")

    def __init__(self, kid, material, proposito, criada, vence, rotulo=""):
        self.kid = kid
        self.proposito = proposito
        self.criada = criada
        self.vence = vence
        self.estado = "ativa"
        self.rotulo = rotulo
        object.__setattr__(self, "_material", material)

    # ── O material só sai por aqui ──────────────────────────

    def material(self, proposito=None):
        """Os bytes — conferindo o propósito e o prazo.

        O propósito é argumento e não campo lido: quem pede tem de
        DIZER para que quer, e é essa declaração que a conferência
        compara. Ler `chave.proposito` e confiar nele não conferiria
        nada.
        """
        if self.estado == "revogada":
            raise _erro(
                f"a chave '{self.kid}' foi revogada.",
                nota=f"rotulo: {self.rotulo or '(sem rotulo)'}",
                dica="Uma chave revogada nao volta: gere outra.")
        if proposito is not None and proposito != self.proposito:
            raise _erro(
                f"a chave '{self.kid}' e de '{self.proposito}', "
                f"e foi pedida para '{proposito}'.",
                nota="Uma chave por proposito impede que um "
                     "comprometimento vire todos.",
                dica=f"Gere uma chave de '{proposito}' no cofre.")
        if self.vencida():
            raise _erro(
                f"a chave '{self.kid}' venceu.",
                nota=f"prazo: {time.strftime('%Y-%m-%d %H:%M', time.gmtime(self.vence))}",
                dica="Rotacione o cofre; as antigas continuam decifrando "
                     "o que ja foi cifrado com elas.")
        return self._material

    def vencida(self, quando=None):
        agora = time.time() if quando is None else float(quando)
        return self.vence > 0 and agora >= self.vence

    def revogar(self):
        """Sem volta, de propósito.

        Uma chave revogada que pudesse ser reativada não seria uma
        revogação — seria uma pausa, e quem a revogou não pediu isso.
        """
        self.estado = "revogada"
        object.__setattr__(self, "_material", b"")
        return True

    def resumo(self):
        """O que dá para mostrar num log ou numa tela."""
        return {
            "kid": self.kid, "proposito": self.proposito,
            "estado": self.estado, "rotulo": self.rotulo,
            "criada": int(self.criada), "vence": int(self.vence),
            "vencida": self.vencida(),
            # A impressão digital identifica a chave sem revelá-la — é
            # o que se compara quando duas máquinas precisam concordar
            # sobre qual chave estão usando.
            "impressao": hashlib.sha256(self._material).hexdigest()[:16]
            if self._material else "",
        }

    def __str__(self):
        return f"<chave {self.kid} ({self.proposito})>"

    def __repr__(self):
        return self.__str__()

    def __format__(self, _spec):
        return self.__str__()

    def __hash__(self):
        raise _erro(
            "uma chave nao pode virar chave de vault.",
            dica="Use 'chave.kid', que identifica sem revelar.")


_COFRE = {"tamanho": 32, "prazo": 0.0, "manter": 3}


class _Cofre:
    """As chaves de um sistema: as ativas, e as aposentadas que ainda
    precisam decifrar o passado."""

    __slots__ = ("_chaves", "_ativa", "_opcoes", "_trava")

    def __init__(self, opcoes=None):
        o = dict(_COFRE)
        o.update(_ler_opcoes(opcoes, _COFRE, "Chaves.cofre"))
        self._opcoes = o
        self._chaves = {}
        self._ativa = {}
        self._trava = threading.Lock()

    def gerar(self, rotulo, proposito="cifrar", prazo=None, tamanho=None):
        """Uma chave nova, e ela passa a ser a ativa daquele rótulo."""
        if proposito not in PROPOSITOS:
            raise _erro(
                f"'{proposito}' nao e um proposito de chave.",
                nota="Ha: " + ", ".join(PROPOSITOS),
                dica="A lista e fechada: um proposito com erro de "
                     "digitacao criaria uma chave que nao serve para nada.")
        n = int(tamanho if tamanho is not None else self._opcoes["tamanho"])
        p = float(prazo if prazo is not None else self._opcoes["prazo"])
        agora = time.time()
        material = os.urandom(n)
        kid = _b64(hashlib.sha256(material + str(agora).encode()).digest()[:9])

        chave = Chave(kid, material, proposito, agora,
                      agora + p if p > 0 else 0.0, str(rotulo))
        with self._trava:
            self._chaves[kid] = chave
            anterior = self._ativa.get((str(rotulo), proposito))
            if anterior is not None:
                self._chaves[anterior].estado = "aposentada"
            self._ativa[(str(rotulo), proposito)] = kid
            self._podar(str(rotulo), proposito)
        return chave

    def _podar(self, rotulo, proposito):
        """Guarda as N últimas aposentadas, e descarta o resto.

        Guardar todas para sempre faz o cofre crescer sem fim; guardar
        zero torna ilegível o que foi cifrado ontem. O padrão é três —
        e quem precisa de mais diz quanto.
        """
        manter = int(self._opcoes["manter"])
        do_rotulo = sorted(
            (c for c in self._chaves.values()
             if c.rotulo == rotulo and c.proposito == proposito
             and c.estado == "aposentada"),
            key=lambda c: c.criada, reverse=True)
        for velha in do_rotulo[manter:]:
            self._chaves.pop(velha.kid, None)

    def ativa(self, rotulo, proposito="cifrar"):
        """A chave que se usa AGORA para aquele rótulo e propósito."""
        with self._trava:
            kid = self._ativa.get((str(rotulo), proposito))
        if kid is None:
            raise _erro(
                f"nao ha chave ativa de '{proposito}' para '{rotulo}'.",
                dica=f"Crie com: cofre.gerar(\"{rotulo}\", "
                     f"proposito := \"{proposito}\")")
        return self._chaves[kid]

    def por_kid(self, kid):
        """A chave que cifrou aquele dado — inclusive uma aposentada.

        É o que torna a rotação possível: o dado carrega o `kid`, e
        decifrar não depende de adivinhar qual das cinco chaves era.
        """
        chave = self._chaves.get(str(kid))
        if chave is None:
            raise _erro(
                f"nao conheco a chave '{kid}'.",
                nota="Ela pode ter sido podada: o cofre guarda as "
                     f"{self._opcoes['manter']} ultimas aposentadas.",
                dica="Recifre o dado antigo antes que a chave saia.")
        return chave

    def rotacionar(self, rotulo, proposito="cifrar"):
        """Gera a próxima e aposenta a atual. A antiga continua lendo."""
        return self.gerar(rotulo, proposito)

    def revogar(self, kid):
        """Diferente de aposentar: a revogada não decifra mais nada."""
        return self.por_kid(kid).revogar()

    def listar(self, rotulo=None):
        with self._trava:
            chaves = list(self._chaves.values())
        if rotulo is not None:
            chaves = [c for c in chaves if c.rotulo == str(rotulo)]
        return [c.resumo() for c in sorted(chaves, key=lambda c: -c.criada)]

    def precisa_rotacionar(self, aviso=604800.0):
        """As que vencem dentro do prazo de aviso — uma semana, por padrão.

        Uma chave que vence sem ninguém saber derruba o sistema numa
        madrugada. O aviso é o que transforma isso em tarefa.
        """
        agora = time.time()
        return [c.resumo() for c in self._chaves.values()
                if c.estado == "ativa" and c.vence > 0
                and c.vence - agora <= float(aviso)]

    # ── Envelope ────────────────────────────────────────────

    def envelopar(self, dados, rotulo="mestra"):
        """Cifra `dados` com uma DEK nova, e a DEK com a chave mestra.

        Rotacionar a mestra passa a ser recifrar 32 bytes por objeto,
        e não reescrever os dados. É o que KMS, Vault e as três nuvens
        fazem.
        """
        from . import cifra as _cifra

        kek = self.ativa(rotulo, "cifrar")
        dek = os.urandom(32)
        return {
            "kid": kek.kid,
            "dek": _b64(_selar(kek.material("cifrar"), dek)),
            "dados": _b64(_selar(dek, _para_bytes(dados))),
        }

    def desenvelopar(self, envelope):
        """Abre o envelope — achando a chave pelo `kid` que ele carrega."""
        from . import cifra as _cifra

        if not isinstance(envelope, dict) or "kid" not in envelope:
            raise _erro(
                "isto nao tem a forma de um envelope.",
                nota="Um envelope tem 'kid', 'dek' e 'dados'.")
        kek = self.por_kid(envelope["kid"])
        dek = _abrir(kek.material("cifrar"), _de_b64(envelope["dek"]))
        return _abrir(dek, _de_b64(envelope["dados"]))

    def recifrar(self, envelope, rotulo="mestra"):
        """Reabre com a chave antiga e fecha com a ativa.

        É a operação que a rotação existe para tornar possível — e ela
        toca a DEK, não os dados.
        """
        return self.envelopar(self.desenvelopar(envelope), rotulo)

    # ── Persistência ────────────────────────────────────────

    def exportar(self, senha):
        """O cofre inteiro, cifrado pela senha mestra.

        Gravar é de quem chama: um cofre que escolhesse onde gravar
        escolheria errado em metade dos casos.
        """
        from . import cifra as _cifra

        corpo = json.dumps({
            "chaves": [{
                "kid": c.kid, "proposito": c.proposito, "estado": c.estado,
                "criada": c.criada, "vence": c.vence, "rotulo": c.rotulo,
                "material": _b64(c._material),
            } for c in self._chaves.values()],
            "ativa": {f"{r}\x1f{p}": k for (r, p), k in self._ativa.items()},
        }, separators=(",", ":")).encode("utf-8")

        sal = os.urandom(16)
        return _b64(sal + _selar(_cifra.derivar(senha, sal, 200000), corpo))

    def importar(self, pacote, senha):
        from . import cifra as _cifra

        bruto = _de_b64(pacote)
        try:
            corpo = _abrir(_cifra.derivar(senha, bruto[:16], 200000), bruto[16:])
        except Exception:                                  # noqa: BLE001
            # A mensagem aqui e mais especifica que a de '_abrir': neste
            # caminho a causa provavel e a senha, e dizer isso poupa
            # quem esta com o cofre na mao.
            raise _erro(
                "o cofre nao abriu com esta senha.",
                nota="A etiqueta do AEAD nao fecha: ou a senha e outra, "
                     "ou o pacote foi alterado.")
        d = json.loads(corpo.decode("utf-8"))
        with self._trava:
            for c in d["chaves"]:
                chave_obj = Chave(c["kid"], _de_b64(c["material"]),
                                  c["proposito"], c["criada"], c["vence"],
                                  c["rotulo"])
                chave_obj.estado = c["estado"]
                self._chaves[c["kid"]] = chave_obj
            for k, kid in d["ativa"].items():
                rotulo, proposito = k.split("\x1f")
                self._ativa[(rotulo, proposito)] = kid
        return len(d["chaves"])

    def auditar(self):
        agora = time.time()
        return {
            "total": len(self._chaves),
            "ativas": sum(1 for c in self._chaves.values() if c.estado == "ativa"),
            "aposentadas": sum(1 for c in self._chaves.values()
                               if c.estado == "aposentada"),
            "revogadas": sum(1 for c in self._chaves.values()
                             if c.estado == "revogada"),
            "vencidas": sum(1 for c in self._chaves.values() if c.vencida(agora)),
            "rotulos": sorted({c.rotulo for c in self._chaves.values()}),
        }


#: O formato de um pacote cifrado: nonce (12) + etiqueta (16) + corpo.
#:
#: 'cifra.selar' devolve o corpo e a etiqueta SEPARADOS, e 'abrir'
#: pede os dois. Guardar cada um num campo proprio espalharia o
#: formato por cinco lugares; colados em ordem fixa, o formato mora
#: nestas duas funcoes e em nenhum outro lugar.
#:
#: A etiqueta vem ANTES do corpo de proposito: os dois primeiros
#: campos tem tamanho fixo, e assim o corte nao depende do tamanho
#: total — que e o que quebra quando o corpo e vazio.
_NONCE = 12
_ETIQUETA = 16


def _selar(chave, dados):
    from . import cifra as _cifra

    nonce = _cifra.nonce_novo()
    corpo, etiqueta = _cifra.selar(chave, nonce, dados, b"")
    return nonce + etiqueta + corpo


def _abrir(chave, pacote):
    """Abre, e LEVANTA quando a etiqueta nao fecha.

    `cifra.abrir` devolve `None` nesse caso, e nao levanta. E uma
    escolha defensavel la — ela e a primitiva, e quem chama decide —
    mas deixa-la passar aqui seria o pior defeito possivel: um
    `desenvelopar` que devolve `void` em vez de recusar faz o programa
    acima gravar nada onde havia um dado, ou tratar a ausencia como
    conteudo vazio. A falha de integridade e o assunto todo do AEAD, e
    ela tem de ser barulhenta.
    """
    from . import cifra as _cifra

    if len(pacote) < _NONCE + _ETIQUETA:
        raise _erro("o pacote cifrado esta truncado.",
                    nota=f"ele tem {len(pacote)} bytes, e o cabecalho "
                         f"sozinho ocupa {_NONCE + _ETIQUETA}.")
    nonce = pacote[:_NONCE]
    etiqueta = pacote[_NONCE:_NONCE + _ETIQUETA]
    aberto = _cifra.abrir(chave, nonce, pacote[_NONCE + _ETIQUETA:],
                          etiqueta, b"")
    if aberto is None:
        raise _erro(
            "o conteudo cifrado nao abriu.",
            nota="A etiqueta do AEAD nao fecha: ou a chave e outra, ou "
                 "o dado foi alterado depois de cifrado.",
            dica="Confira o 'kid' do envelope: ele diz qual chave o cifrou.")
    return aberto


def _para_bytes(valor):
    if isinstance(valor, (bytes, bytearray)):
        return bytes(valor)
    if isinstance(valor, str):
        return valor.encode("utf-8")
    raise _erro(
        f"espera texto ou bytes, e recebeu um {_nome_do_tipo(valor)}.")


def _derivar_de(chave, contexto, tamanho=32):
    """Uma subchave por contexto, a partir de uma chave mestra (HKDF).

    É como se tem uma chave por finalidade sem guardar dez chaves: a
    mestra fica no cofre, e `derivar_de(mestra, "cookies")` sempre dá
    a mesma subchave — sem que a subchave revele a mestra.
    """
    material = chave.material("derivar") if isinstance(chave, Chave) \
        else _para_bytes(chave)
    ctx = _para_bytes(contexto)
    extraida = hmac.new(b"DataForge-HKDF", material, hashlib.sha256).digest()
    saida, bloco, i = b"", b"", 1
    while len(saida) < int(tamanho):
        bloco = hmac.new(extraida, bloco + ctx + bytes([i]),
                         hashlib.sha256).digest()
        saida += bloco
        i += 1
    return saida[:int(tamanho)]


def _usar(chave, proposito):
    """O material, conferindo propósito, prazo e revogação."""
    if not isinstance(chave, Chave):
        raise _erro(f"esperava uma chave, e recebeu um {_nome_do_tipo(chave)}.")
    return chave.material(proposito)


class ArcaneChaves(dict):
    """O vault que o 'adopt' entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Chaves",

            "cofre": lambda opcoes=None: _Cofre(opcoes),
            "usar": _usar,
            "derivar_de": _derivar_de,
            "e_chave": lambda v: isinstance(v, Chave),

            "PROPOSITOS": list(PROPOSITOS),
            "ESTADOS": list(ESTADOS),
        }
