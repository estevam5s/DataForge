#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Espelha `doc/*.md` no repositório da organização.

    python3 scripts/sincronizar_docs_org.py --check    # só compara
    python3 scripts/sincronizar_docs_org.py            # envia

Por que existe
--------------
`github.com/dataforge-df/docs` foi preenchido **copiando arquivo por
arquivo, à mão**. Três dias depois, `referencia.md`, `biblioteca.md` e
`kiln.md` já divergiam do repositório — justamente os três que a
mudança daquele dia tocou.

Documentação que divergiu é pior que documentação ausente: quem lê
confia, e o que ela diz não vale mais. Uma cópia à mão de dez arquivos
não sobrevive a nenhuma semana de trabalho.

O que ele NÃO faz
-----------------
Não mexe nos arquivos que existem **só** na organização
(`arquitetura.md`, `banco-de-dados.md`, `testes.md`): eles foram
escritos para lá e não têm origem aqui. Eles são listados no relatório,
para que a existência deles seja visível em vez de esquecida.

Não apaga nada. Um arquivo que sai de `doc/` continua na organização
até alguém decidir removê-lo — apagar em cascata a partir de um
`git mv` seria a pior forma de descobrir o mapeamento errado.

Credencial
----------
O token sai do `git credential fill`, o mesmo que o `git push` usa.
Nada de token no código nem em variável de ambiente exportada.
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.marca import preparar_saida    # noqa: E402

ORG = "dataforge-df"
REPO = "docs"

#: O mapeamento, num lugar só: `doc/<local>` → `<nome na organização>`.
#:
#: Os nomes diferem de propósito. No repositório o arquivo é
#: `REFERENCIA.md` — grito, como o `README.md` ao lado. Na organização
#: ele é a URL que alguém vai ler e digitar, e `/docs/referencia.md`
#: lê melhor que `/docs/REFERENCIA.md`.
MAPA = {
    "INSTALACAO.md": "instalacao.md",
    "TUTORIAL.md": "tutorial.md",
    "REFERENCIA.md": "referencia.md",
    "BIBLIOTECA_PADRAO.md": "biblioteca.md",
    "KILN.md": "kiln.md",
    "VITRINE.md": "vitrine.md",
    "ANALISE_E_ROADMAP.md": "roadmap.md",
    "ESTABILIDADE.md": "estabilidade.md",
}


def _token():
    """O mesmo token que o `git push` usa."""
    entrada = "protocol=https\nhost=github.com\n\n"
    saida = subprocess.run(["git", "credential", "fill"], input=entrada,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=RAIZ)
    for linha in (saida.stdout or "").splitlines():
        if linha.startswith("password="):
            return linha.split("=", 1)[1]
    return ""


def _api(caminho, token, metodo="GET", corpo=None):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{ORG}/{REPO}/{caminho}",
        data=json.dumps(corpo).encode() if corpo else None,
        method=metodo,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "dataforge-sync"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def _remotos(token):
    """`{nome: (sha, tamanho)}` do que está lá hoje."""
    try:
        itens = _api("contents", token)
    except urllib.error.HTTPError as erro:
        print(f"  nao deu para listar: {erro.code} {erro.reason}",
              file=sys.stderr)
        return None
    return {i["name"]: (i["sha"], i["size"]) for i in itens
            if i["type"] == "file"}


def _sha_do_git(dados):
    """O sha1 que o git daria a este conteúdo.

    É o que o GitHub devolve em `sha`, e comparar com ele evita enviar
    um arquivo idêntico — o que criaria um commit vazio a cada execução
    e tornaria o histórico da organização inútil.
    """
    cabeca = f"blob {len(dados)}\0".encode()
    return hashlib.sha1(cabeca + dados).hexdigest()


def main():
    # O relatorio desenha '≠' e '✓'. No Windows a saida redirecionada
    # vem em cp1252, que nao tem nenhum dos dois — e o script morreria
    # com UnicodeEncodeError antes de dizer o que divergiu.
    preparar_saida()
    conferir = "--check" in sys.argv
    token = _token()
    if not token:
        print("sem credencial do GitHub — rode 'gh auth login' ou "
              "configure o credential helper", file=sys.stderr)
        return 1

    remotos = _remotos(token)
    if remotos is None:
        return 1

    desatualizados = []
    novos = []
    iguais = 0

    for local, remoto in sorted(MAPA.items()):
        caminho = os.path.join(RAIZ, "doc", local)
        if not os.path.isfile(caminho):
            print(f"  \033[1;33mfalta\033[0m   doc/{local} "
                  f"(mapeado para {remoto})")
            continue
        with open(caminho, "rb") as f:
            dados = f.read()
        atual = remotos.get(remoto)
        if atual is None:
            novos.append((local, remoto, dados))
        elif atual[0] != _sha_do_git(dados):
            desatualizados.append((local, remoto, dados, atual[0]))
        else:
            iguais += 1

    so_da_org = sorted(set(remotos) - set(MAPA.values()) - {"README.md"})

    print()
    print(f"  \033[1;37m{ORG}/{REPO}\033[0m")
    print(f"  {iguais} em dia, {len(desatualizados)} desatualizado(s), "
          f"{len(novos)} novo(s)")
    for local, remoto, _, _ in desatualizados:
        print(f"    \033[1;33m≠\033[0m  {remoto}  ←  doc/{local}")
    for local, remoto, _ in novos:
        print(f"    \033[1;32m+\033[0m  {remoto}  ←  doc/{local}")
    if so_da_org:
        print(f"  só na organização (não mexo): {', '.join(so_da_org)}")

    if conferir:
        print()
        return 1 if (desatualizados or novos) else 0

    if not desatualizados and not novos:
        print("\n  nada a enviar\n")
        return 0

    for local, remoto, dados, sha in desatualizados:
        _enviar(token, remoto, dados, sha, f"Atualiza {remoto} de doc/{local}")
        print(f"    \033[1;32m✓\033[0m  {remoto}")
    for local, remoto, dados in novos:
        _enviar(token, remoto, dados, None, f"Acrescenta {remoto} de doc/{local}")
        print(f"    \033[1;32m✓\033[0m  {remoto} (novo)")
    print()
    return 0


def _enviar(token, nome, dados, sha, mensagem):
    corpo = {
        "message": mensagem,
        "content": base64.b64encode(dados).decode(),
        "committer": {"name": "DataForge docs",
                      "email": "contato@estevamsouza.com.br"},
    }
    if sha:
        # Sem o sha, a API recusa a sobrescrita — e é bom que recuse:
        # é o que impede sobrescrever uma edição feita direto na
        # organização sem ninguém ver.
        corpo["sha"] = sha
    _api(f"contents/{nome}", token, "PUT", corpo)


if __name__ == "__main__":
    sys.exit(main())
