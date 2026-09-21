# -*- coding: utf-8 -*-
"""'dataforge telegram' — criar, rodar, diagnosticar e publicar um bot.

    dataforge telegram new meubot     cria o projeto
    dataforge telegram run            sobe em long polling
    dataforge telegram doctor         diz por que o bot nao responde
    dataforge telegram webhook <url>  registra o webhook e sobe o servidor
    dataforge telegram off            desliga o webhook

Por que 'doctor' existe, e por que ele e o comando mais util aqui
-----------------------------------------------------------------
Um bot que nao responde nao da erro: ele simplesmente fica calado. As
causas sao poucas e sempre as mesmas — token errado, webhook ativo
brigando com o polling, outro processo com o mesmo token, privacidade
de grupo ligada — e nenhuma delas aparece no terminal. O `doctor`
pergunta cada uma ao proprio Telegram e diz qual e.

Por que 'webhook' existe e 'deploy' nao
----------------------------------------
Registrar o webhook e uma chamada a Bot API com uma URL: isso e do
bot, e cabe aqui. **Onde** essa URL vai morar — Docker, systemd, uma
PaaS, um tunel — e uma opiniao sobre infraestrutura que o projeto nao
tem, pelo mesmo motivo que `dataforge vitrine deploy` nao existe.
"""

import os
import sys


def color(texto, codigo):
    from .cli import color as _color
    return _color(texto, codigo)


#: Os nomes que um arquivo de bot costuma ter, em ordem.
CANDIDATOS = ("bot.df", "main.df", "app.df", "src/bot.df", "src/main.df")

#: A variavel de ambiente em que o token mora. Um token no codigo vai
#: para o Git, e do Git para qualquer um.
VARIAVEL = "TELEGRAM_TOKEN"


def executar(args, flags):
    sub = args[0] if args else "run"
    resto = args[1:]

    if sub in ("run", "dev", "polling"):
        return _rodar(resto, flags)
    if sub == "doctor":
        return _diagnosticar(resto, flags)
    if sub == "webhook":
        return _webhook(resto, flags)
    if sub in ("off", "sem-webhook"):
        return _desligar(resto, flags)
    if sub == "new":
        return _criar(resto, flags)
    if sub in ("-h", "--help", "help"):
        return _uso()
    if sub == "deploy":
        return _explicar_deploy()
    print(color(f"  subcomando desconhecido: {sub}", "1;31"))
    return _uso()


def _uso():
    print()
    print(color("  dataforge telegram <comando>", "1"))
    print()
    print("    new <nome>        cria um projeto de bot")
    print("    run               sobe em long polling (o modo de desenvolver)")
    print("    doctor            diz por que o bot não responde")
    print("    webhook <url>     registra o webhook e sobe o servidor")
    print("    off               desliga o webhook")
    print()
    print(color(f"  O token vem de ${VARIAVEL}.", "2"))
    print(color('    export TELEGRAM_TOKEN="123456:AAH..."', "2"))
    print()
    return 0


# ═══════════════════════════════════════════════════════════
#  Rodar
# ═══════════════════════════════════════════════════════════

def _rodar(args, flags):
    alvo = _achar_alvo(args)
    if alvo is None:
        return 1
    if not _token(obrigatorio=True):
        return 1
    os.environ["TELEGRAM_MODO"] = "polling"
    from .cli import run_file
    try:
        run_file(alvo)
    except KeyboardInterrupt:
        print(color("\n  bot parado.", "2"))
    return 0


def _achar_alvo(args):
    if args and not args[0].startswith("-"):
        if os.path.isfile(args[0]):
            return args[0]
        print(color(f"  não achei '{args[0]}'.", "1;31"))
        return None
    for nome in CANDIDATOS:
        if os.path.isfile(nome):
            return nome
    print(color("  não achei o arquivo do bot.", "1;31"))
    print()
    print("  Procurei por: " + ", ".join(CANDIDATOS))
    print("  Passe o caminho:  dataforge telegram run meubot.df")
    print("  Ou crie um:       dataforge telegram new meubot")
    print()
    return None


def _token(obrigatorio=False):
    valor = os.environ.get(VARIAVEL, "").strip()
    if valor or not obrigatorio:
        return valor
    print(color(f"  ${VARIAVEL} está vazia.", "1;31"))
    print()
    print("  O token vem do @BotFather, no próprio Telegram:")
    print("    1. converse com @BotFather")
    print("    2. mande /newbot e siga as perguntas")
    print("    3. ele devolve algo como 123456789:AAH...")
    print()
    print(color(f'    export {VARIAVEL}="123456789:AAH..."', "1"))
    print()
    print(color("  Nunca ponha o token no código: ele vai para o Git, e de", "2"))
    print(color("  lá para qualquer um. O @BotFather não avisa quando isso", "2"))
    print(color("  acontece — o bot só começa a mandar spam.", "2"))
    print()
    return ""


# ═══════════════════════════════════════════════════════════
#  Diagnosticar
# ═══════════════════════════════════════════════════════════

def _diagnosticar(args, flags):
    """As cinco causas de um bot calado, perguntadas ao Telegram."""
    print()
    print(color("  dataforge telegram doctor", "1"))
    print()
    problemas = []

    def linha(rotulo, ok, detalhe="", conserto=""):
        marca = color("  ✓", "1;32") if ok else color("  ✗", "1;31")
        print(f"{marca} {rotulo}" + (color(f"  {detalhe}", "2") if detalhe else ""))
        if not ok and conserto:
            problemas.append(conserto)

    token = _token()
    linha("a variável de ambiente existe", bool(token),
          f"${VARIAVEL}" if token else "vazia",
          f'export {VARIAVEL}="123456:AAH..."')
    if not token:
        _fechar(problemas)
        return 1

    linha("o token tem a forma certa", ":" in token,
          "<id>:<segredo>",
          "confira se não veio espaço ou aspas junto do token")

    sys.path.insert(0, os.getcwd())
    from .stdlib import get_module
    Tg = get_module("Arcane.Telegram")

    try:
        bot = Tg["bot"](token)
        eu = bot.eu()
    except Exception as erro:                                # noqa: BLE001
        linha("o Telegram aceita o token", False,
              getattr(erro, "message", str(erro))[:70],
              "peça um token novo ao @BotFather com /token")
        _fechar(problemas)
        return 1

    linha("o Telegram aceita o token", True, f"@{eu.get('username')}")
    linha("o bot entra em grupos", bool(eu.get("can_join_groups")),
          "can_join_groups", "@BotFather → /setjoingroups")
    # Esta e a causa que mais engana: com a privacidade LIGADA (o
    # padrao), o bot so recebe mensagens que comecam com '/' ou que o
    # citam. Em privado tudo funciona, e em grupo ele fica mudo.
    le_tudo = bool(eu.get("can_read_all_group_messages"))
    linha("lê todas as mensagens de grupo", le_tudo,
          "privacidade ligada — só vê /comandos e menções" if not le_tudo
          else "privacidade desligada",
          "se o bot precisa ler tudo em grupo: @BotFather → "
          "/setprivacy → Disable")

    try:
        info = bot.info_do_webhook()
    except Exception:                                        # noqa: BLE001
        info = {}
    url = info.get("url") or ""
    linha("o webhook não briga com o polling", not url,
          url or "nenhum registrado",
          "rode 'dataforge telegram off' antes de usar polling")

    pendentes = int(info.get("pending_update_count") or 0)
    if url:
        linha("o webhook está entregando", pendentes < 20,
              f"{pendentes} update(s) na fila",
              "o servidor do webhook não está respondendo 200")
        ultimo = info.get("last_error_message")
        if ultimo:
            linha("o Telegram não reclamou do webhook", False, str(ultimo)[:60],
                  "confira o certificado e se a URL responde 200 rápido")

    alvo = None
    for nome in CANDIDATOS:
        if os.path.isfile(nome):
            alvo = nome
            break
    linha("há um arquivo de bot aqui", alvo is not None, alvo or "",
          "dataforge telegram new meubot")
    if alvo:
        fonte = open(alvo, encoding="utf-8").read()
        linha("ele sobe o bot", any(m in fonte for m in
                                    (".rodar(", ".publicar(", ".montar(")),
              "", "acrescente 'app.rodar()' ao final")
        linha("o token não está escrito no arquivo",
              ":AAH" not in fonte and "segredo_do_ambiente" in fonte
              or ":AAH" not in fonte,
              "", "leia o token com Tg.segredo_do_ambiente()")

    _fechar(problemas)
    return 1 if problemas else 0


def _fechar(problemas):
    print()
    if not problemas:
        print(color("  tudo pronto.", "1;32"))
    else:
        print(color(f"  {len(problemas)} coisa(s) a resolver:", "1;33"))
        for conserto in problemas:
            print(f"    · {conserto}")
    print()


# ═══════════════════════════════════════════════════════════
#  Webhook
# ═══════════════════════════════════════════════════════════

def _webhook(args, flags):
    if not args:
        print(color("  uso: dataforge telegram webhook https://seu.dominio", "1;31"))
        print()
        print("  O Telegram só aceita HTTPS com certificado válido — ele")
        print("  recusa HTTP, e recusa certificado que não consiga validar.")
        print("  Durante o desenvolvimento, um túnel resolve:")
        print(color("    cloudflared tunnel --url http://localhost:8443", "2"))
        print()
        return 1
    url = args[0]
    token = _token(obrigatorio=True)
    if not token:
        return 1

    sys.path.insert(0, os.getcwd())
    from .stdlib import get_module
    Tg = get_module("Arcane.Telegram")

    caminho = _flag_texto(flags, "--caminho", "/telegram")
    segredo = _flag_texto(flags, "--segredo", "")
    alvo = str(url).rstrip("/") + caminho
    try:
        Tg["bot"](token).webhook(alvo, segredo=segredo)
    except Exception as erro:                                # noqa: BLE001
        print(color(f"  o Telegram recusou: "
                    f"{getattr(erro, 'message', erro)}", "1;31"))
        return 1
    print(color(f"  webhook registrado em {alvo}", "1;32"))
    if not segredo:
        print(color("  aviso: sem --segredo, qualquer um que descubra a URL", "1;33"))
        print(color("         manda updates falsos para o seu bot.", "1;33"))
    print()
    print("  Agora suba o servidor que atende esse caminho:")
    print(color(f"    app.publicar(\"{url}\", caminho := \"{caminho}\")", "2"))
    print()
    return 0


def _desligar(args, flags):
    token = _token(obrigatorio=True)
    if not token:
        return 1
    sys.path.insert(0, os.getcwd())
    from .stdlib import get_module
    Tg = get_module("Arcane.Telegram")
    Tg["bot"](token).sem_webhook()
    print(color("  webhook desligado — o polling volta a funcionar.", "1;32"))
    return 0


def _explicar_deploy():
    print()
    print(color("  'deploy' não existe — de propósito.", "1;33"))
    print()
    print("  Registrar o webhook é do bot, e isso existe:")
    print(color("    dataforge telegram webhook https://seu.dominio", "2"))
    print()
    print("  Onde essa URL vai morar — Docker, systemd, uma PaaS, um túnel")
    print("  — é uma opinião sobre infraestrutura que o projeto não tem.")
    print()
    print("  O que o bot oferece para quem opera:")
    print("    GET <caminho>/saude     métricas e contagem de erros")
    print("    dataforge telegram doctor")
    print("    dataforge devops docker --porta=8443")
    print()
    return 0


def _criar(args, flags):
    if not args:
        print(color("  uso: dataforge telegram new <nome>", "1;31"))
        return 1
    from .cli import new_project
    # O modelo e o PRIMEIRO posicional de "new", e nao uma flag:
    # "dataforge new bot <nome>". Passa-lo como "--modelo="
    # fazia o comando reclamar que faltava dizer o modelo.
    return new_project(["bot", args[0]], flags)


def _flag_texto(flags, nome, padrao):
    for flag in flags or []:
        if flag.startswith(nome + "="):
            return flag.split("=", 1)[1]
    return padrao
