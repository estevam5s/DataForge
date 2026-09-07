#!/usr/bin/env sh
# Instalador do DataForge para Linux e macOS.
#
#   curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
#
# Variáveis:
#   DATAFORGE_VERSION=4.0.0     versão a instalar (padrão: a mais recente)
#   DATAFORGE_PREFIX=~/.local   onde instalar (padrão: ~/.dataforge)
#   DATAFORGE_REPO=...          repositório de origem
#
# POSIX sh de propósito: roda em dash, ash e busybox, não só em bash.

set -eu

VERSAO="${DATAFORGE_VERSION:-4.0.0}"
PREFIXO="${DATAFORGE_PREFIX:-$HOME/.dataforge}"
SITE="${DATAFORGE_SITE:-https://dataforge-lang.vercel.app}"
REPO="${DATAFORGE_REPO:-https://github.com/estevam5s/DataForge}"
PYTHON_MINIMO="3.10"

esc="$(printf '\033')"
vermelho="${esc}[1;31m"; verde="${esc}[1;32m"; amarelo="${esc}[1;33m"
ciano="${esc}[1;36m"; apagado="${esc}[0;90m"; fim="${esc}[0m"

info()  { printf "${ciano}==>${fim} %s\n" "$1"; }
ok()    { printf "${verde}  ✓${fim} %s\n" "$1"; }
aviso() { printf "${amarelo}  !${fim} %s\n" "$1"; }
erro()  { printf "${vermelho}erro:${fim} %s\n" "$1" >&2; exit 1; }

# ── Onde estamos ─────────────────────────────────────────────

detectar_sistema() {
    case "$(uname -s)" in
        Linux*)   SISTEMA=linux ;;
        Darwin*)  SISTEMA=macos ;;
        MINGW*|MSYS*|CYGWIN*)
            erro "no Windows, use o PowerShell:
  irm https://dataforge-lang.vercel.app/instalar.ps1 | iex" ;;
        *) erro "sistema não reconhecido: $(uname -s)" ;;
    esac
}

# ── Python ───────────────────────────────────────────────────

versao_ok() {
    "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null
}

achar_python() {
    for candidato in python3.13 python3.12 python3.11 python3.10 python3 python; do
        if command -v "$candidato" >/dev/null 2>&1 && versao_ok "$candidato"; then
            PYTHON="$candidato"
            return 0
        fi
    done
    return 1
}

instrucao_python() {
    case "$SISTEMA" in
        macos) echo "  brew install python@3.12" ;;
        linux)
            if command -v apt-get >/dev/null 2>&1; then
                echo "  sudo apt install python3 python3-venv"
            elif command -v dnf >/dev/null 2>&1; then
                echo "  sudo dnf install python3"
            elif command -v pacman >/dev/null 2>&1; then
                echo "  sudo pacman -S python"
            else
                echo "  instale o Python $PYTHON_MINIMO ou mais novo pelo gerenciador da sua distro"
            fi ;;
    esac
}

# ── Download ─────────────────────────────────────────────────

baixar() {
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$1" -o "$2"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$2" "$1"
    else
        erro "preciso de curl ou wget para baixar"
    fi
}

# ── Instalação ───────────────────────────────────────────────

principal() {
    # A arte vai por heredoc sem aspas no delimitador: assim o shell nao
    # tenta interpretar as barras invertidas do desenho.
    printf "%b" "$ciano"
    cat <<'ARTE'

  ____        _        _____
 |  _ \  __ _| |_ __ _|  ___|__  _ __ __ _  ___
 | | | |/ _` | __/ _` | |_ / _ \| '__/ _` |/ _ \
 | |_| | (_| | || (_| |  _| (_) | | | (_| |  __/
 |____/ \__,_|\__\__,_|_|  \___/|_|  \__, |\___|
                                     |___/
ARTE
    printf "%b linguagem de programação · v%s%b\n\n" "$apagado" "$VERSAO" "$fim"

    detectar_sistema
    ok "sistema: $SISTEMA ($(uname -m))"

    if ! achar_python; then
        printf "\n"
        erro "não achei Python $PYTHON_MINIMO ou mais novo.
Instale com:
$(instrucao_python)

Depois rode este instalador de novo."
    fi
    ok "python: $("$PYTHON" --version 2>&1) em $(command -v "$PYTHON")"

    # venv própria: não mexe no Python do sistema, não precisa de sudo,
    # e desinstalar é apagar uma pasta
    info "instalando em $PREFIXO"
    if [ -d "$PREFIXO" ]; then
        aviso "já existe — substituindo"
        rm -rf "$PREFIXO"
    fi
    mkdir -p "$PREFIXO"

    if ! "$PYTHON" -m venv "$PREFIXO/venv" 2>/dev/null; then
        erro "não consegui criar o ambiente virtual.
No Debian/Ubuntu falta o pacote:
  sudo apt install python3-venv"
    fi
    ok "ambiente virtual criado"

    PIP="$PREFIXO/venv/bin/pip"
    "$PIP" install --quiet --upgrade pip >/dev/null 2>&1 || true

    info "baixando o DataForge $VERSAO"
    ARQUIVO="$(mktemp -d)/dataforge.tar.gz"

    # O site e a origem: um tarball estatico, sem depender do GitHub.
    # As duas alternativas abaixo so entram se o site estiver fora do ar.
    if baixar "$SITE/dist/dataforge-$VERSAO.tar.gz" "$ARQUIVO" 2>/dev/null; then
        ok "baixado de $SITE"
    elif baixar "$REPO/archive/refs/tags/v$VERSAO.tar.gz" "$ARQUIVO" 2>/dev/null; then
        ok "baixado do GitHub (tag v$VERSAO)"
    elif baixar "$REPO/archive/refs/heads/main.tar.gz" "$ARQUIVO" 2>/dev/null; then
        aviso "usando o ramo principal do GitHub"
    else
        erro "não consegui baixar o DataForge $VERSAO.
Tentei:
  $SITE/dist/dataforge-$VERSAO.tar.gz
  $REPO/archive/refs/tags/v$VERSAO.tar.gz

Confira sua conexão, ou instale pelo PyPI:
  pip install dataforge-lang"
    fi

    FONTE="$(dirname "$ARQUIVO")/fonte"
    mkdir -p "$FONTE"
    tar -xzf "$ARQUIVO" -C "$FONTE" --strip-components=1
    ok "código baixado"

    info "instalando"
    "$PIP" install --quiet "$FONTE" || erro "a instalação falhou"
    ok "pacote instalado"

    mkdir -p "$PREFIXO/bin"
    for nome in dataforge df; do
        cat > "$PREFIXO/bin/$nome" <<ATALHO
#!/usr/bin/env sh
exec "$PREFIXO/venv/bin/dataforge" "\$@"
ATALHO
        chmod +x "$PREFIXO/bin/$nome"
    done
    ok "comandos: dataforge, df"

    VERIFICADA="$("$PREFIXO/bin/dataforge" version 2>&1 | head -1)"
    printf "\n${verde}  %s instalado${fim}\n\n" "$VERIFICADA"

    if command -v dataforge >/dev/null 2>&1 && \
       [ "$(command -v dataforge)" = "$PREFIXO/bin/dataforge" ]; then
        printf "  Pronto. Comece por:\n\n"
        printf "    ${ciano}dataforge repl${fim}\n"
        printf "    ${ciano}dataforge init meu-projeto${fim}\n\n"
    else
        printf "  ${amarelo}Falta um passo:${fim} ponha o DataForge no seu PATH.\n\n"
        printf "    ${ciano}export PATH=\"%s/bin:\$PATH\"${fim}\n\n" "$PREFIXO"
        printf "  Para valer sempre, acrescente essa linha ao seu\n"
        printf "  ~/.bashrc, ~/.zshrc ou ~/.profile.\n\n"
    fi

    printf "  ${apagado}documentação: https://dataforge-lang.vercel.app/docs${fim}\n"
    printf "  ${apagado}desinstalar:  rm -rf %s${fim}\n\n" "$PREFIXO"
}

principal "$@"
