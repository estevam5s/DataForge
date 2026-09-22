# -*- coding: utf-8 -*-
"""Arcane.Integridade — provar que o que está aqui é o que foi posto aqui.

Integridade é o "I" da tríade, e o menos implementado: quase todo
sistema cifra, poucos conferem. Três peças:

**SRI** (*Subresource Integrity*) — o `integrity="sha384-…"` de um
`<script>` servido por CDN. Sem ele, quem controla a CDN troca o
JavaScript de todas as páginas que o usam.

**Manifesto de pasta** — o SHA-256 de cada arquivo, e depois a
conferência: o que foi **acrescentado**, **removido** e **alterado**.
É o que um verificador de integridade de arquivos (à moda do Tripwire)
faz: a pasta de uma aplicação em produção não muda entre deploys, e
qualquer diferença é um incidente até prova em contrário.

**Manifesto assinado** — um manifesto guardado ao lado dos arquivos
não prova nada: quem troca o arquivo troca o manifesto junto. Assinado
com uma chave que mora fora dali, ele passa a provar.

Uma decisão que vale lembrar: o caminho no manifesto é **relativo** e
com `/`, em qualquer sistema. Um manifesto gerado no Windows precisa
conferir no Linux, e `C:\\app\\x.df` nunca casaria com `/srv/app/x.df`.
"""

import base64
import hashlib
import hmac as _hmac
import json
import os


def _erro(mensagem, nota="", dica="", doc="biblioteca/integridade"):
    from ..errors import RuntimeError_
    return RuntimeError_(str(mensagem), 0, 0, nota=nota, dica=dica, doc=doc)


def _bytes(conteudo):
    if isinstance(conteudo, (bytes, bytearray)):
        return bytes(conteudo)
    return str(conteudo).encode("utf-8")


_ALGORITMOS_SRI = ("sha256", "sha384", "sha512")


def sri(conteudo, algoritmo="sha384"):
    """O valor do atributo `integrity` — `sha384-<base64>`."""
    if algoritmo not in _ALGORITMOS_SRI:
        raise _erro(f"'{algoritmo}' nao e aceito em SRI. Use sha256, sha384 ou sha512.")
    digest = hashlib.new(algoritmo, _bytes(conteudo)).digest()
    return f"{algoritmo}-{base64.b64encode(digest).decode('ascii')}"


def conferir_sri(conteudo, integridade):
    """`yes` se algum dos valores (separados por espaço) bate — como o navegador."""
    for parte in str(integridade or "").split():
        alg = parte.split("-", 1)[0]
        if alg in _ALGORITMOS_SRI and _hmac.compare_digest(sri(conteudo, alg), parte):
            return True
    return False


def _hash_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 16), b""):
            h.update(bloco)
    return h.hexdigest()


_IGNORAR_PADRAO = (".git", "__pycache__", "forge_modules", ".DS_Store")


def manifesto(pasta, ignorar=None):
    """`{caminho_relativo: sha256}` de cada arquivo da pasta.

    Links simbólicos **não são seguidos**: um link para fora da pasta
    faria o manifesto descrever arquivos que não são dela.
    """
    raiz = os.path.abspath(str(pasta))
    if not os.path.isdir(raiz):
        raise _erro(f"'{pasta}' nao e uma pasta.")
    fora = set(_IGNORAR_PADRAO) | set(ignorar or ())
    saida = {}
    for atual, subpastas, arquivos in os.walk(raiz, followlinks=False):
        subpastas[:] = sorted(d for d in subpastas if d not in fora)
        for nome in sorted(arquivos):
            if nome in fora:
                continue
            completo = os.path.join(atual, nome)
            if os.path.islink(completo):
                continue
            relativo = os.path.relpath(completo, raiz).replace(os.sep, "/")
            saida[relativo] = _hash_arquivo(completo)
    return saida


def conferir_manifesto(pasta, esperado, ignorar=None):
    """O que mudou desde o manifesto — `{ok, acrescentados, removidos, alterados}`."""
    atual = manifesto(pasta, ignorar)
    esperado = dict(esperado or {})
    acrescentados = sorted(set(atual) - set(esperado))
    removidos = sorted(set(esperado) - set(atual))
    alterados = sorted(c for c in set(atual) & set(esperado) if atual[c] != esperado[c])
    return {"ok": not (acrescentados or removidos or alterados),
            "acrescentados": acrescentados, "removidos": removidos,
            "alterados": alterados, "arquivos": len(atual)}


def _canonico(m):
    return json.dumps(m, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def assinar_manifesto(m, chave):
    """O manifesto com uma assinatura HMAC-SHA256 sobre a forma canônica."""
    if not chave or len(str(chave)) < 16:
        raise _erro("a chave de assinatura precisa de pelo menos 16 caracteres.",
                    nota="um manifesto guardado ao lado dos arquivos, sem assinatura "
                         "de uma chave que mora FORA dali, nao prova nada: quem troca "
                         "o arquivo troca o manifesto junto.")
    arquivos = dict(m.get("arquivos", m) if isinstance(m, dict) else {})
    assinatura = _hmac.new(str(chave).encode("utf-8"), _canonico(arquivos),
                           hashlib.sha256).hexdigest()
    return {"arquivos": arquivos, "assinatura": assinatura, "algoritmo": "HMAC-SHA256"}


def verificar_manifesto(assinado, chave):
    """`yes` se o manifesto não foi alterado depois de assinado."""
    if not isinstance(assinado, dict) or "assinatura" not in assinado:
        return False
    esperado = assinar_manifesto(assinado.get("arquivos", {}), chave)["assinatura"]
    return _hmac.compare_digest(esperado, str(assinado["assinatura"]))


class ArcaneIntegridade:
    """Arcane.Integridade — SRI, manifesto de pasta e manifesto assinado."""

    def __new__(cls):
        return {
            "sri": sri,
            "conferir_sri": conferir_sri,
            "manifesto": manifesto,
            "conferir_manifesto": conferir_manifesto,
            "assinar_manifesto": assinar_manifesto,
            "verificar_manifesto": verificar_manifesto,
        }
