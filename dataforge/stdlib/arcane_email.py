# -*- coding: utf-8 -*-
"""Arcane.Email — montar e enviar e-mail.

O que faltava
-------------
Todo sistema manda e-mail: a confirmação de cadastro, a redefinição de
senha, o relatório de madrugada. Não havia como, e a saída era chamar
um serviço de fora por HTTP — o que funciona e cobra por mensagem.

Três decisões
-------------
1. **A mensagem é montada por um objeto, e não por texto.** Um e-mail
   com anexo e HTML é MIME multipart, e montá-lo concatenando texto é
   como montar HTML com `+`: funciona nos casos fáceis e quebra no
   primeiro acento ou no primeiro anexo binário.

2. **`enviar` exige TLS por padrão.** Uma senha de SMTP trafegando em
   claro numa rede que você não controla é uma credencial perdida. Quem
   quiser sem TLS escreve `seguro := no` — e aí a escolha está no
   código, para alguém ver na revisão.

3. **`prever` mostra a mensagem sem mandar.** O erro mais caro daqui é
   disparar mil e-mails de teste para endereços reais. `prever` devolve
   o que SERIA enviado.
"""

import mimetypes
import os
import re
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr, parseaddr


class ErroDeEmail(Exception):
    pass


_ENDERECO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valido(endereco):
    """Parece um endereço? Não garante que ele exista — nada garante.

    A única conferência que vale é mandar uma mensagem e ver se volta.
    Isto pega o erro de digitação, que é o caso comum.
    """
    _, puro = parseaddr(str(endereco))
    return bool(_ENDERECO.match(puro))


def _exigir(enderecos, campo):
    lista = [enderecos] if isinstance(enderecos, str) else list(enderecos or ())
    for e in lista:
        if not valido(e):
            raise ErroDeEmail(
                f"'{e}' não é um endereço válido (campo {campo}).\n"
                f"  Um endereço tem a forma nome@dominio.br")
    return lista


class Mensagem:
    """Um e-mail sendo montado."""

    def __init__(self, de="", para=None, assunto=""):
        # Os campos ficam GUARDADOS, e a mensagem MIME é construída a
        # cada `montar()`. A primeira versão montava sobre o mesmo
        # objeto, e a segunda chamada estourava com
        #
        #     TypeError: set_content not valid on multipart
        #
        # — o que fazia `prever()` antes de `enviar()` quebrar o envio.
        # Um `prever` que impede o `enviar` é pior que não ter `prever`.
        self._campos = {}
        self._ocultos = []
        self.anexos = []
        self._texto = ""
        self._html = ""
        if de:
            self.de(de)
        if para:
            self.para(para)
        if assunto:
            self.assunto(assunto)

    def de(self, endereco, nome=""):
        _exigir(endereco, "de")
        self._campos["From"] = formataddr((nome, endereco)) if nome \
            else endereco
        return self

    def para(self, enderecos):
        self._campos["To"] = ", ".join(_exigir(enderecos, "para"))
        return self

    def copia(self, enderecos):
        self._campos["Cc"] = ", ".join(_exigir(enderecos, "copia"))
        return self

    def copia_oculta(self, enderecos):
        """Bcc. Ele NÃO vira cabeçalho — vai só na lista de entrega.

        Um Bcc escrito no cabeçalho é visível para todo mundo, e é
        exatamente o oposto do que ele significa.
        """
        self._ocultos = _exigir(enderecos, "copia_oculta")
        return self

    def responder_para(self, endereco):
        _exigir(endereco, "responder_para")
        self._campos["Reply-To"] = endereco
        return self

    def assunto(self, texto):
        self._campos["Subject"] = str(texto)
        return self

    def texto(self, corpo):
        self._texto = str(corpo)
        return self

    def html(self, corpo, alternativa=""):
        """O corpo em HTML. `alternativa` é o que vê quem não lê HTML.

        Sem ela, o cliente de texto puro mostra a marcação crua — e é o
        que boa parte dos leitores de tela recebe.
        """
        self._html = str(corpo)
        if alternativa:
            self._texto = str(alternativa)
        elif not self._texto:
            self._texto = re.sub(r"<[^>]+>", " ", self._html)
            self._texto = re.sub(r"\s+", " ", self._texto).strip()
        return self

    def anexar(self, caminho, nome=""):
        if not os.path.isfile(caminho):
            raise ErroDeEmail(f"não achei o arquivo '{caminho}' para anexar")
        tipo, _ = mimetypes.guess_type(caminho)
        principal, _, sub = (tipo or "application/octet-stream").partition("/")
        with open(caminho, "rb") as f:
            self.anexos.append({
                "nome": nome or os.path.basename(caminho),
                "dados": f.read(), "principal": principal, "sub": sub})
        return self

    def anexar_dados(self, nome, dados, tipo="application/octet-stream"):
        principal, _, sub = tipo.partition("/")
        bruto = dados if isinstance(dados, (bytes, bytearray)) \
            else str(dados).encode("utf-8")
        self.anexos.append({"nome": nome, "dados": bytes(bruto),
                            "principal": principal, "sub": sub or "octet-stream"})
        return self

    def cabecalho(self, chave, valor):
        self._campos[str(chave)] = str(valor)
        return self

    # ── finalizar ──

    def montar(self):
        """A mensagem MIME. PURA: pode ser chamada quantas vezes for."""
        if not self._campos.get("From"):
            raise ErroDeEmail("falta o remetente: use 'de(endereco)'")
        if not self._campos.get("To") and not self._ocultos:
            raise ErroDeEmail("falta o destinatário: use 'para(endereco)'")

        m = EmailMessage()
        for chave, valor in self._campos.items():
            m[chave] = valor
        m.set_content(self._texto or "")
        if self._html:
            m.add_alternative(self._html, subtype="html")
        for anexo in self.anexos:
            m.add_attachment(
                anexo["dados"], maintype=anexo["principal"],
                subtype=anexo["sub"], filename=anexo["nome"])
        return m

    def destinatarios(self):
        alvos = []
        for campo in ("To", "Cc"):
            if self._campos.get(campo):
                alvos += [e.strip() for e in self._campos[campo].split(",")]
        alvos += list(self._ocultos)
        return alvos

    def prever(self):
        """O que SERIA enviado. O erro mais caro daqui é disparar de verdade."""
        montada = self.montar()
        return {
            "de": montada.get("From", ""),
            "para": self.destinatarios(),
            "assunto": montada.get("Subject", ""),
            "texto": self._texto,
            "html": self._html,
            "anexos": [{"nome": a["nome"], "bytes": len(a["dados"])}
                       for a in self.anexos],
            "tamanho": len(bytes(montada)),
        }

    def como_texto(self):
        return self.montar().as_string()

    def __repr__(self):
        return f"<email para {len(self.destinatarios())} destinatário(s)>"


def mensagem(de="", para=None, assunto=""):
    return Mensagem(de, para, assunto)


# ══════════════════════════════════════════════════════════════
#  Enviar
# ══════════════════════════════════════════════════════════════

def enviar(mensagem_, servidor, porta=587, usuario="", senha="",
           seguro=True, prazo=30.0):
    """Manda de verdade. Devolve o que foi entregue.

    `seguro := yes` (o padrão) faz STARTTLS na porta 587 e TLS direto na
    465. Uma senha de SMTP em claro numa rede que você não controla é
    uma credencial perdida.
    """
    montada = mensagem_.montar() if isinstance(mensagem_, Mensagem) \
        else mensagem_
    alvos = mensagem_.destinatarios() if isinstance(mensagem_, Mensagem) \
        else None
    porta = int(porta)

    try:
        if seguro and porta == 465:
            contexto = ssl.create_default_context()
            cliente = smtplib.SMTP_SSL(servidor, porta, timeout=prazo,
                                       context=contexto)
        else:
            cliente = smtplib.SMTP(servidor, porta, timeout=prazo)
            if seguro:
                cliente.starttls(context=ssl.create_default_context())
    except OSError as erro:
        raise ErroDeEmail(
            f"não consegui falar com {servidor}:{porta}: {erro}\n"
            f"  587 é STARTTLS, 465 é TLS direto, 25 é sem cifra.") from None

    try:
        if usuario:
            try:
                cliente.login(usuario, senha)
            except smtplib.SMTPAuthenticationError as erro:
                raise ErroDeEmail(
                    f"o servidor recusou o login de '{usuario}'.\n"
                    f"  {erro.smtp_error.decode('utf-8', 'replace') if isinstance(erro.smtp_error, bytes) else erro.smtp_error}\n"
                    f"  Muitos provedores exigem uma senha de APLICATIVO, "
                    f"e não a senha da conta.") from None
        recusados = cliente.send_message(montada, to_addrs=alvos)
    finally:
        try:
            cliente.quit()
        except Exception:                            # noqa: BLE001
            pass

    return {
        "entregues": [a for a in (alvos or []) if a not in recusados],
        "recusados": {k: str(v) for k, v in (recusados or {}).items()},
        "ok": not recusados,
    }


class Caixa:
    """Um servidor de teste: guarda em vez de mandar.

    É o que torna barato testar um fluxo que manda e-mail. O contrato é
    o mesmo de `enviar`, então o código que envia não muda entre o
    teste e a produção.
    """

    def __init__(self):
        self.enviados = []

    def enviar(self, mensagem_, *_args, **_kwargs):
        ficha = mensagem_.prever() if isinstance(mensagem_, Mensagem) \
            else {"assunto": "", "para": []}
        self.enviados.append(ficha)
        return {"entregues": ficha["para"], "recusados": {}, "ok": True}

    def ultimo(self):
        return self.enviados[-1] if self.enviados else None

    def para(self, endereco):
        return [m for m in self.enviados if endereco in m["para"]]

    def limpar(self):
        self.enviados = []
        return self

    def __repr__(self):
        return f"<caixa {len(self.enviados)} enviado(s)>"


def caixa():
    return Caixa()


class ArcaneEmail:
    """O dicionário que `adopt Arcane.Email` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Email",
            "mensagem": mensagem,
            "Mensagem": Mensagem,
            "enviar": enviar,
            "valido": valido,
            "caixa": caixa,
            "Caixa": Caixa,
        }
