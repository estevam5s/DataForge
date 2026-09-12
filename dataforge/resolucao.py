# -*- coding: utf-8 -*-
"""Onde mora o modulo que um 'adopt' pede.

Por que este arquivo existe
---------------------------
A regra estava escrita em DOIS lugares — o interpretador, que precisa
carregar o arquivo, e o analisador, que precisa saber se ele existe — e
os dois divergiram do pior jeito possivel: o analisador fazia

    nome.replace('.', os.sep)

o que transforma './mod0' em '//mod0'. Resultado: TODO 'adopt' relativo
de TODO projeto gerava um aviso "Module not found" falso. Eram 62 no
repositorio e 795 num projeto de 21 mil linhas — 795 de 795, ou seja,
cada aviso que o analisador emitia ali era mentira.

Isso e pior que nao avisar nada. O projeto tem um principio explicito
sobre o assunto: "um falso alarme ensina o usuario a ignorar mensagens".

As tres formas de pedir um modulo
---------------------------------
| Forma            | Resolve contra              |
|------------------|-----------------------------|
| 'Arcane.Math'    | a biblioteca padrao         |
| 'Python.numpy'   | a ponte (nao passa por aqui)|
| './util'         | o ARQUIVO que escreve       |
| 'sub.modulo'     | o arquivo, depois o cwd     |
| 'pacote'         | forge_modules/              |

Relativo resolve sempre a partir do arquivo que escreve o import, nunca
do diretorio de onde se rodou o programa: assim mover a pasta inteira
nao quebra nada, e ler o codigo basta para saber o que ele importa.
"""

import os

#: Os prefixos que marcam um caminho relativo explicito.
RELATIVOS = ("./", "../", ".\\", "..\\")


def e_relativo(nome):
    """'./util' e './a/b' sao relativos; 'Arcane.Math' nao e."""
    return str(nome).startswith(RELATIVOS) or str(nome).endswith(".df")


def pasta_de(arquivo):
    """A pasta do arquivo que escreve o import.

    '<stdin>', '<repl>' e afins nao sao arquivos: ali o relativo so pode
    contar com o diretorio atual.
    """
    if arquivo and not str(arquivo).startswith("<"):
        return os.path.dirname(os.path.abspath(arquivo))
    return os.getcwd()


def candidatos(nome, arquivo=None):
    """Os caminhos onde o modulo pode estar, na ordem de procura.

    A ordem importa: 'util.df' antes de 'util/main.df' antes de
    'util/src/main.df'. Um arquivo e uma pasta com o mesmo nome fariam a
    escolha depender da ordem, e esta e a que o interpretador usa.
    """
    origem = pasta_de(arquivo)

    if e_relativo(nome):
        alvo = os.path.normpath(os.path.join(origem, nome))
        return [alvo, alvo + ".df",
                os.path.join(alvo, "main.df"),
                os.path.join(alvo, "src", "main.df")]

    # 'sub.modulo' vira 'sub/modulo'. So aqui o replace e correto —
    # depois de ter descartado o caso relativo, que era o que ele
    # estragava.
    partes = str(nome).replace(".", os.sep)
    achados = []
    for base in _bases(origem):
        alvo = os.path.join(base, partes)
        achados += [alvo + ".df", os.path.join(alvo, "main.df"),
                    os.path.join(alvo, "src", "main.df")]
    return achados


def _bases(origem):
    """A pasta do arquivo primeiro, o diretorio atual depois."""
    atual = os.getcwd()
    return [origem] if origem == atual else [origem, atual]


def achar(nome, arquivo=None):
    """O caminho do modulo, ou None.

    Nao levanta: quem chama decide se a ausencia e erro (interpretador)
    ou aviso (analisador).
    """
    for candidato in candidatos(nome, arquivo):
        if os.path.isfile(candidato):
            return candidato
    return None


def raiz_do_projeto(arquivo=None):
    """A pasta com o 'forge.toml' mais proximo, subindo.

    Um arquivo em 'tests/' ou em 'src/sub/' precisa encontrar a raiz de
    qualquer profundidade.
    """
    atual = pasta_de(arquivo)
    while True:
        if os.path.isfile(os.path.join(atual, "forge.toml")):
            return atual
        acima = os.path.dirname(atual)
        if acima == atual:
            return None
        atual = acima


def achar_no_proprio_pacote(nome, arquivo=None):
    """O modulo pedido pelo NOME DO PROPRIO pacote.

    O teste de um pacote escreve 'adopt validador', e nao
    'adopt ../src/main', porque o teste precisa exercitar a biblioteca
    pelo mesmo caminho que um usuario dela usaria. Sem isto, a suite de
    um pacote so roda depois de publicado e instalado.

    E nao e teoria: as suites dos VINTE pacotes deste repositorio
    falhavam por isso, com "Module not found", e nada na CI apanhava —
    ela nao rodava 'dataforge test' dentro de 'packages/'.
    """
    raiz = raiz_do_projeto(arquivo)
    if raiz is None:
        return None

    declarado, entrada = _manifesto(raiz)
    if not declarado:
        return None

    primeiro = str(nome).split(".")[0]
    if primeiro != declarado:
        return None

    resto = str(nome).split(".")[1:]
    if resto:
        alvo = os.path.join(raiz, "src", *resto)
        for candidato in (alvo + ".df", os.path.join(alvo, "main.df")):
            if os.path.isfile(candidato):
                return candidato
        return None

    procura = []
    if entrada:
        procura.append(os.path.join(raiz, entrada))
    procura += [os.path.join(raiz, "src", "main.df"),
                os.path.join(raiz, "main.df"),
                os.path.join(raiz, "src", f"{declarado}.df")]
    for candidato in procura:
        if os.path.isfile(candidato):
            return candidato
    return None


def _manifesto(raiz):
    """(nome, entrada) do forge.toml, lidos sem parser de TOML.

    So duas chaves interessam, e as duas sao 'chave = "valor"' numa
    linha. Um parser de TOML aqui seria peso morto — e a stdlib do
    Python 3.10 nao tem escritor nem leitor tolerante.
    """
    caminho = os.path.join(raiz, "forge.toml")
    nome = entrada = ""
    try:
        with open(caminho, encoding="utf-8") as f:
            for linha in f:
                limpa = linha.strip()
                if limpa.startswith("#") or "=" not in limpa:
                    continue
                chave, _, valor = limpa.partition("=")
                chave = chave.strip()
                valor = valor.strip().strip('"').strip("'")
                if chave == "name" and not nome:
                    nome = valor
                elif chave == "entry" and not entrada:
                    entrada = valor
    except OSError:
        return "", ""
    return nome, entrada


def dependencias_declaradas(arquivo=None):
    """Os nomes do bloco '[dependencies]' do forge.toml.

    Serve para distinguir dois casos que a mesma mensagem confundia:
    um nome que ninguem declarou (erro de digitacao, provavelmente) e um
    que esta no manifesto e so nao foi instalado ainda. O segundo se
    resolve com um comando, e dizer qual e a diferenca entre um aviso
    util e um aviso que so incomoda.
    """
    raiz = raiz_do_projeto(arquivo)
    if raiz is None:
        return set()
    nomes = set()
    dentro = False
    try:
        with open(os.path.join(raiz, "forge.toml"), encoding="utf-8") as f:
            for linha in f:
                limpa = linha.strip()
                if limpa.startswith("["):
                    dentro = limpa.lower().startswith("[dependencies")
                    continue
                if dentro and "=" in limpa and not limpa.startswith("#"):
                    nomes.add(limpa.partition("=")[0].strip())
    except OSError:
        return set()
    return nomes


def achar_em_pacotes(nome, arquivo=None):
    """O modulo dentro de 'forge_modules/', subindo ate achar forge.toml.

    Um projeto com dependencias tem a pasta na raiz, e um arquivo em
    'src/sub/' precisa encontra-la de qualquer profundidade.
    """
    pasta = pasta_de(arquivo)
    raiz = pasta
    while True:
        if os.path.isfile(os.path.join(raiz, "forge.toml")):
            break
        acima = os.path.dirname(raiz)
        if acima == raiz:
            raiz = pasta
            break
        raiz = acima

    modulos = os.path.join(raiz, "forge_modules")
    if not os.path.isdir(modulos):
        return None

    primeiro = str(nome).split(".")[0]
    resto = str(nome).split(".")[1:]
    pacote = os.path.join(modulos, primeiro)
    if not os.path.isdir(pacote):
        return None

    if resto:
        alvo = os.path.join(pacote, "src", *resto)
        for candidato in (alvo + ".df", os.path.join(alvo, "main.df")):
            if os.path.isfile(candidato):
                return candidato
        return None

    for candidato in (os.path.join(pacote, "src", "main.df"),
                      os.path.join(pacote, "main.df"),
                      os.path.join(pacote, f"{primeiro}.df")):
        if os.path.isfile(candidato):
            return candidato
    return None
