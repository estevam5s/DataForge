#!/usr/bin/env sh
# Instalador do DataForge para Linux e macOS.
#
#   curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
#
# Variáveis:
#   DATAFORGE_VERSION=1.0.0     versão a instalar (padrão: a mais recente)
#   DATAFORGE_PREFIX=~/.local   onde instalar (padrão: ~/.dataforge)
#   DATAFORGE_REPO=...          repositório de origem
#
# Opções (só quando o script roda de um arquivo — `| sh` não repassa
# argumentos, então baixe primeiro com -o):
#
#   --com-editor      instala a extensão do editor       (padrão: sim)
#   --sem-editor      não instala
#   --com-exemplos    baixa os 42 exemplos e 200 exercícios
#   --abrir-docs      abre a documentação ao terminar
#   --silencioso      só erros
#
# POSIX sh de propósito: roda em dash, ash e busybox, não só em bash.

set -eu

VERSAO="${DATAFORGE_VERSION:-1.0.0}"
PREFIXO="${DATAFORGE_PREFIX:-$HOME/.dataforge}"
SITE="${DATAFORGE_SITE:-https://dataforge-lang.vercel.app}"

#: A marca que identifica a linha que ESTE script escreveu no rc do
#: shell. Sem ela, reinstalar empilha um 'export PATH' a cada vez.
MARCA_PATH="# DataForge — adicionado pelo instalador"
REPO="${DATAFORGE_REPO:-https://github.com/estevam5s/DataForge}"
PYTHON_MINIMO="3.10"

# Para onde a contagem de instalacoes vai. Vazio desliga.
CONTAGEM_URL="${DATAFORGE_CONTAGEM_URL:-https://teimsogvbhllhzkvioam.supabase.co}"
CONTAGEM_CHAVE="${DATAFORGE_CONTAGEM_CHAVE:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlaW1zb2d2YmhsbGh6a3Zpb2FtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg4MTM5OTIsImV4cCI6MjEwNDM4OTk5Mn0.0_ZtGzWaYXkRrijJubIodeAJpVSiIC5Mz48mHCjfsmM}"

# As opções também chegam por variável de ambiente: `curl … | sh` não
# repassa argumentos, e o assistente do site monta o comando assim.
COM_EDITOR=1
COM_EXEMPLOS=0
ABRIR_DOCS=0
SILENCIOSO=0

for opcao in ${DATAFORGE_EXTRAS:-} "$@"; do
    case "$opcao" in
        --com-editor)   COM_EDITOR=1 ;;
        --sem-editor)   COM_EDITOR=0 ;;
        --com-exemplos) COM_EXEMPLOS=1 ;;
        --abrir-docs)   ABRIR_DOCS=1 ;;
        --silencioso|-q) SILENCIOSO=1 ;;
        "") ;;
        *) printf "aviso: opção desconhecida: %s\n" "$opcao" >&2 ;;
    esac
done

# 'DATAFORGE_SEM_EDITOR' continua valendo: quem já usava não deve
# descobrir que parou de funcionar.
[ -n "${DATAFORGE_SEM_EDITOR:-}" ] && COM_EDITOR=0

esc="$(printf '\033')"
vermelho="${esc}[1;31m"; verde="${esc}[1;32m"; amarelo="${esc}[1;33m"
ciano="${esc}[1;36m"; apagado="${esc}[0;90m"; fim="${esc}[0m"

info()  { printf "${ciano}==>${fim} %s\n" "$1"; }
ok()    { printf "${verde}  ✓${fim} %s\n" "$1"; }
#: '/Users/ana/.zshrc' -> '~/.zshrc'. Caminho absoluto numa mensagem
#: rouba a atencao do que importa.
curto() { printf '%s' "$1" | sed "s|^$HOME|~|"; }
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

    # Coloracao no editor. Se nao houver editor instalado, o comando diz
    # isso e sai sem erro — nao e motivo para a instalacao falhar.
    if [ "$COM_EDITOR" = "1" ]; then
        "$PREFIXO/bin/dataforge" editor >/dev/null 2>&1 && \
            ok "extensão instalada no editor"
    fi

    if [ "$COM_EXEMPLOS" = "1" ]; then
        instalar_exemplos
    fi

    if command -v dataforge >/dev/null 2>&1 && \
       [ "$(command -v dataforge)" = "$PREFIXO/bin/dataforge" ]; then
        printf "  Pronto. Comece por:\n\n"
        printf "    ${ciano}dataforge repl${fim}\n"
        printf "    ${ciano}dataforge init meu-projeto${fim}\n\n"
    else
        configurar_path
    fi

    printf "  ${apagado}documentação: https://dataforge-lang.vercel.app/docs${fim}\n"
    printf "  ${apagado}desinstalar:  rm -rf %s${fim}\n\n" "$PREFIXO"

    if [ "$ABRIR_DOCS" = "1" ]; then
        abrir_navegador "$SITE/docs/primeiros-passos"
    fi

    contar_instalacao
}

# Avisa que houve mais uma instalacao.
#
# O que vai: a origem, a versao, o sistema e a arquitetura. O que NAO
# vai: nada que identifique quem instalou — nem nome de maquina, nem
# usuario, nem caminho.
#
# Silencioso e opcional: sai sem barulho se nao houver rede, e
# DATAFORGE_SEM_TELEMETRIA=1 desliga. Uma instalacao nunca falha por
# causa disto.
contar_instalacao() {
    [ -n "${DATAFORGE_SEM_TELEMETRIA:-}" ] && return 0

    [ -z "$CONTAGEM_URL" ] && return 0
    command -v curl >/dev/null 2>&1 || return 0

    arq="$(uname -m 2>/dev/null || echo '')"
    corpo="{\"p_origem\":\"script\",\"p_versao\":\"$VERSAO\",\"p_sistema\":\"$SISTEMA\",\"p_arquitetura\":\"$arq\"}"

    # A chave abaixo e a ANONIMA do Supabase, que ja e publica: ela
    # esta no bundle de toda pagina do site. O que protege a tabela nao
    # e a chave — e o RLS, que so deixa gravar pela funcao e so deixa
    # ler quem e admin.
    curl -fsS -m 4 -X POST "$CONTAGEM_URL/rest/v1/rpc/registrar_download" \
        -H "apikey: $CONTAGEM_CHAVE" \
        -H "Content-Type: application/json" \
        -d "$corpo" >/dev/null 2>&1 || true
    return 0
}

# ── Extras ───────────────────────────────────────────────────

#: Os arquivos de inicializacao de cada shell, do mais especifico ao
#: mais geral. O zsh nao le ~/.bashrc e o bash nao le ~/.zshrc: escrever
#: no arquivo errado e o mesmo que nao escrever.
arquivo_de_rc() {
    nome_do_shell="$(basename "${SHELL:-/bin/sh}")"
    case "$nome_do_shell" in
        zsh)  printf '%s/.zshrc'   "$HOME" ;;
        bash)
            # No macOS o bash de login le .bash_profile e ignora o
            # .bashrc; no Linux e o contrario. Preferimos o que ja
            # existe, e caimos no .profile quando nenhum existe.
            if [ -f "$HOME/.bashrc" ]; then printf '%s/.bashrc' "$HOME"
            elif [ -f "$HOME/.bash_profile" ]; then printf '%s/.bash_profile' "$HOME"
            else printf '%s/.profile' "$HOME"; fi ;;
        fish) printf '%s/.config/fish/config.fish' "$HOME" ;;
        *)    printf '%s/.profile' "$HOME" ;;
    esac
}

#: Acrescenta o PATH ao rc do shell, uma vez so.
#:
#: A marca existe para o script poder rodar de novo — atualizacao,
#: reinstalacao — sem empilhar uma linha a cada vez. Um ~/.zshrc com
#: quinze 'export PATH' iguais e o que acontece quando ninguem confere.
configurar_path() {
    RC="$(arquivo_de_rc)"
    LINHA="export PATH=\"$PREFIXO/bin:\$PATH\""
    case "$RC" in
        *config.fish) LINHA="fish_add_path $PREFIXO/bin" ;;
    esac

    if [ -f "$RC" ] && grep -qF "$MARCA_PATH" "$RC" 2>/dev/null; then
        ok "PATH já estava configurado em $(curto "$RC")"
    else
        mkdir -p "$(dirname "$RC")" 2>/dev/null || true
        if {
            printf '\n%s\n' "$MARCA_PATH"
            printf '%s\n' "$LINHA"
        } >> "$RC" 2>/dev/null; then
            ok "PATH configurado em $(curto "$RC")"
        else
            printf "  ${amarelo}Nao consegui escrever em %s.${fim}\n\n" "$RC"
            printf "    ${ciano}%s${fim}\n\n" "$LINHA"
            return 0
        fi
    fi

    printf "\n  Pronto. Nesta janela, ative agora:\n\n"
    printf "    ${ciano}export PATH=\"%s/bin:\$PATH\"${fim}\n\n" "$PREFIXO"
    printf "  ${apagado}Nas proximas, ja vem sozinho.${fim}\n\n"
    printf "  Comece por:\n\n"
    printf "    ${ciano}dataforge repl${fim}\n"
    printf "    ${ciano}dataforge init meu-projeto${fim}\n\n"
}

instalar_exemplos() {
    # Os exemplos vêm do tarball já baixado, se ele os trouxer. Baixar
    # um segundo arquivo só para isso dobraria o tempo de instalação
    # de quem só quer olhar dois programas.
    destino="$PREFIXO/exemplos"
    if [ -d "$FONTE/examples" ]; then
        mkdir -p "$destino"
        cp -R "$FONTE/examples/." "$destino/" 2>/dev/null || true
        [ -d "$FONTE/exercicios" ] && \
            cp -R "$FONTE/exercicios" "$PREFIXO/" 2>/dev/null || true
        ok "exemplos em $destino"
    else
        aviso "os exemplos não vieram no pacote; veja em $SITE/docs/exercicios"
    fi
}

abrir_navegador() {
    # Sem 'erro' se não houver navegador: uma instalação bem-sucedida
    # não pode falhar por causa de um extra opcional.
    if command -v open >/dev/null 2>&1; then
        open "$1" >/dev/null 2>&1 || true
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$1" >/dev/null 2>&1 || true
    fi
}

principal "$@"
