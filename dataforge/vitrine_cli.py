# -*- coding: utf-8 -*-
"""'dataforge vitrine' — subir, desenvolver e diagnosticar um painel.

Quatro subcomandos, e todos fazem a mesma coisa por baixo: achar o
arquivo que sobe a aplicacao e roda-lo. A diferenca esta em COMO.

    dataforge vitrine run     sobe, sem recarregar
    dataforge vitrine dev     sobe recarregando ao salvar
    dataforge vitrine doctor  diz por que nao subiu
    dataforge vitrine new     cria o projeto (o mesmo que 'new --modelo=painel')

Nao ha 'build' nem 'deploy' aqui de proposito. Uma aplicacao Vitrine nao
tem etapa de build — nao ha bundler, nao ha transpilacao, nao ha
'node_modules': o que roda e o .df. E 'deploy' seria inventar uma opiniao
sobre Docker, systemd ou nuvem que o projeto nao tem; 'dataforge vitrine
doctor' diz o que falta, e o resto e do time que opera.
"""

import os
import sys


def color(texto, codigo):
    """O 'color' do cli.py, importado sob demanda.

    No topo ele faria ciclo: 'cli.py' importa este modulo para
    despachar o comando.
    """
    from .cli import color as _color
    return _color(texto, codigo)

#: Os nomes que um arquivo que SOBE a aplicacao costuma ter, em ordem.
CANDIDATOS = ("main.df", "app.df", "painel.df", "dashboard.df",
              "src/main.df", "src/app.df", "src/painel.df")

#: Uma porta acima de 1024 (sem sudo) e longe do 8080 do Kiln, para os
#: dois poderem estar no ar ao mesmo tempo durante o desenvolvimento.
PORTA_PADRAO = 8501


def executar(args, flags):
    """Ponto de entrada. Devolve o codigo de saida."""
    sub = args[0] if args else "run"
    resto = args[1:]

    if sub in ("run", "dev", "start"):
        return _subir(resto, flags, recarregar=(sub == "dev"))
    if sub == "doctor":
        return _diagnosticar(resto, flags)
    if sub in ("new", "create"):
        return _criar(resto, flags)
    if sub in ("build", "deploy"):
        return _explicar_ausencia(sub)

    print(color(f"  subcomando desconhecido: '{sub}'", "1;31"))
    print()
    print(_uso())
    return 1


def _uso():
    return (
        "  uso: dataforge vitrine <subcomando>\n\n"
        "    run [arquivo]     sobe a aplicação\n"
        "    dev [arquivo]     sobe recarregando ao salvar\n"
        "    doctor            diz por que ela não sobe\n"
        "    new <nome>        cria um projeto de painel\n\n"
        "    --porta=8501      a porta\n"
        "    --host=0.0.0.0    o endereço (o padrão só aceita local)\n")


# ═══════════════════════════════════════════════════════════
#  Subir
# ═══════════════════════════════════════════════════════════

def _subir(args, flags, recarregar):
    alvo = _achar_alvo(args)
    if alvo is None:
        return 1

    porta = _flag_numero(flags, "--porta", PORTA_PADRAO)
    host = _flag_texto(flags, "--host", "127.0.0.1")

    # Estas chegam ao programa pelo ambiente, e nao por argumento: o .df
    # ja escreveu 'V.subir(porta := 8501)', e reescrever o arquivo do
    # usuario para mudar a porta seria pior que ignorar a flag.
    os.environ["VITRINE_PORTA"] = str(porta)
    os.environ["VITRINE_HOST"] = host
    if recarregar:
        os.environ["VITRINE_RECARREGAR"] = "1"

    if host == "0.0.0.0":
        print(color(
            "  aviso: --host=0.0.0.0 aceita conexão de qualquer máquina da\n"
            "         rede. Em produção pública, ponha um nginx ou Caddy na\n"
            "         frente — não há TLS aqui.", "1;33"))
        print()

    from .cli import run_file
    try:
        run_file(alvo)
    except KeyboardInterrupt:
        print(color("\n  vitrine fechada.", "2"))
    return 0


def _achar_alvo(args):
    """O arquivo que sobe a aplicacao."""
    if args:
        alvo = args[0]
        if os.path.isfile(alvo):
            return alvo
        print(color(f"  o arquivo '{alvo}' não existe.", "1;31"))
        return None

    for nome in CANDIDATOS:
        if os.path.isfile(nome):
            return nome

    from . import project
    manifesto = project.carregar(".")
    if manifesto is not None and os.path.isfile(manifesto.entry_path()):
        return manifesto.entry_path()

    print(color("  não achei o arquivo que sobe a aplicação.", "1;31"))
    print()
    print(color("  procurei por: " + ", ".join(CANDIDATOS[:4]), "2"))
    print()
    print("  diga qual é:   dataforge vitrine run caminho/do/arquivo.df")
    print("  ou crie um:    dataforge vitrine new meupainel")
    return None


# ═══════════════════════════════════════════════════════════
#  Diagnostico
# ═══════════════════════════════════════════════════════════

def _diagnosticar(args, flags):
    """Confere o que costuma impedir um painel de subir.

    Cada linha responde uma pergunta que alguem faria ao ver a tela em
    branco — e a ordem e a da causa mais provavel para a menos.
    """
    print()
    print(color("  ◆ Vitrine — diagnóstico", "1;33"))
    print()

    problemas = []

    def linha(rotulo, ok, detalhe="", conserto=""):
        marca = color("✓", "1;32") if ok else color("✗", "1;31")
        print(f"  {marca} {rotulo}" + (color(f"  {detalhe}", "2")
                                       if detalhe else ""))
        if not ok and conserto:
            problemas.append(conserto)

    # 1. O modulo carrega?
    try:
        from .stdlib import get_module
        modulo = get_module("Arcane.Vitrine")
        linha("o módulo Arcane.Vitrine carrega",
              modulo is not None,
              f"{len(modulo) - 1} símbolos" if modulo else "")
    except Exception as erro:                      # noqa: BLE001
        linha("o módulo Arcane.Vitrine carrega", False, str(erro),
              "a instalação está incompleta; reinstale com "
              "'pip install --force-reinstall dataforge-lang'")

    # 2. O Kiln, de quem ela depende?
    try:
        from .stdlib import get_module as _g
        linha("o Kiln está disponível", _g("Kiln") is not None,
              "a Vitrine roda sobre ele")
    except Exception as erro:                      # noqa: BLE001
        linha("o Kiln está disponível", False, str(erro))

    # 3. Ha um arquivo que sobe?
    alvo = None
    for nome in CANDIDATOS:
        if os.path.isfile(nome):
            alvo = nome
            break
    linha("há um arquivo que sobe a aplicação", alvo is not None,
          alvo or "nenhum de " + ", ".join(CANDIDATOS[:3]),
          "crie um projeto com 'dataforge vitrine new meupainel'")

    # 4. Ele compila?
    if alvo:
        try:
            from .lexer import tokenize
            from .parser import parse
            fonte = open(alvo, encoding="utf-8").read()
            parse(tokenize(fonte, alvo), alvo)
            linha(f"{alvo} compila", True)
        except Exception as erro:                  # noqa: BLE001
            linha(f"{alvo} compila", False, str(erro).split("\n")[0],
                  f"rode 'dataforge check {alvo}' para o detalhe")

        # 5. Ele adota a Vitrine?
        fonte = open(alvo, encoding="utf-8").read()
        adota = "Arcane.Vitrine" in fonte or "Vitrine" in fonte
        if not adota:
            for outro in _vizinhos(alvo):
                if "Vitrine" in open(outro, encoding="utf-8").read():
                    adota = True
                    break
        linha("o projeto usa a Vitrine", adota,
              "" if adota else "nenhum 'adopt Arcane.Vitrine' encontrado",
              "acrescente 'adopt Arcane.Vitrine as V'")

        # 6. Ele SOBE, ou so monta?
        sobe = any(m in fonte for m in
                   ("V.subir", "V.rodar", ".subir(", ".rodar("))
        linha("o arquivo sobe o servidor", sobe,
              "" if sobe else "não achei V.subir nem V.rodar",
              "acrescente 'V.subir(porta := 8501)' ao final")

    # 7. A porta esta livre?
    porta = _flag_numero(flags, "--porta", PORTA_PADRAO)
    livre = _porta_livre(porta)
    linha(f"a porta {porta} está livre", livre,
          "" if livre else "algo já está ouvindo nela",
          f"use outra: 'dataforge vitrine dev --porta={porta + 1}'")

    print()
    if problemas:
        print(color(f"  {len(problemas)} coisa(s) a resolver:", "1;33"))
        for i, conserto in enumerate(problemas, 1):
            print(f"    {i}. {conserto}")
        print()
        return 1
    print(color("  tudo pronto — 'dataforge vitrine dev' sobe.", "1;32"))
    print()
    return 0


def _vizinhos(alvo):
    """Os .df da mesma pasta e da 'src/', para procurar o 'adopt'."""
    pasta = os.path.dirname(os.path.abspath(alvo)) or "."
    achados = []
    for raiz in (pasta, os.path.join(pasta, "src"),
                 os.path.join(os.path.dirname(pasta), "src")):
        if os.path.isdir(raiz):
            for nome in sorted(os.listdir(raiz)):
                if nome.endswith(".df"):
                    achados.append(os.path.join(raiz, nome))
    return achados[:20]


def _porta_livre(porta):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", int(porta)))
            return True
        except OSError:
            return False


# ═══════════════════════════════════════════════════════════
#  Criar
# ═══════════════════════════════════════════════════════════

def _criar(args, flags):
    if not args:
        print(color("  uso: dataforge vitrine new <nome>", "1;31"))
        return 1
    from .cli import new_command
    return new_command([args[0], "--modelo=painel"] + list(flags))


def _explicar_ausencia(sub):
    """'build' e 'deploy' nao existem, e a mensagem diz por quê.

    Um comando que nao existe e melhor explicado do que sugerido: quem
    veio de outro framework procura os dois, e "comando desconhecido"
    nao responde a pergunta que a pessoa tem.
    """
    if sub == "build":
        print(color("  não há etapa de build numa aplicação Vitrine.", "1;33"))
        print()
        print("  Não há bundler, transpilação nem 'node_modules': o que roda")
        print("  é o próprio .df, e o HTML é montado no servidor a cada")
        print("  pedido. Para distribuir o projeto, 'dataforge pack'.")
    else:
        print(color("  'deploy' não existe — de propósito.", "1;33"))
        print()
        print("  Publicar envolve escolher entre Docker, systemd, uma PaaS e")
        print("  um proxy na frente, e o DataForge não tem opinião sobre isso.")
        print()
        print("  O que a Vitrine oferece:")
        print("    dataforge vitrine doctor        o que falta para subir")
        print("    GET /__vitrine__/saude          para o balanceador")
        print("    GET /__vitrine__/metricas       para o monitoramento")
        print()
        print("  E o essencial: um processo por aplicação, com nginx ou")
        print("  Caddy na frente — não há TLS nem HTTP/2 aqui.")
    print()
    return 1


# ═══════════════════════════════════════════════════════════
#  Flags
# ═══════════════════════════════════════════════════════════

def _flag_texto(flags, nome, padrao):
    for f in flags:
        if f.startswith(nome + "="):
            return f.split("=", 1)[1]
    return padrao


def _flag_numero(flags, nome, padrao):
    bruto = _flag_texto(flags, nome, None)
    if bruto is None:
        return padrao
    try:
        return int(bruto)
    except ValueError:
        print(color(f"  '{nome}={bruto}' não é um número; usando {padrao}.",
                    "1;33"))
        return padrao
