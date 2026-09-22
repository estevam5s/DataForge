# -*- coding: utf-8 -*-
"""`dataforge completar <bash|zsh|fish>` — o autocompletar do terminal.

O script sai do **catálogo** (`cli.GRUPOS`), e não de uma lista escrita
aqui: um comando novo aparece no Tab no dia em que entra no catálogo, e
uma opção removida some. Uma segunda lista divergiria na primeira
semana — foi o que aconteceu com a tabela da biblioteca, escrita em três
lugares.

Três decisões:

1. **As opções são por comando.** `dataforge check --<Tab>` oferece
   `--strict`, e não as sessenta opções de todos os comandos juntas.
2. **Depois de `run`, `check`, `fmt`… o Tab completa arquivo.** É o que
   se digita ali, e um completar que oferece subcomando no lugar de
   `src/main.df` é pior que nenhum.
3. **O script é texto puro, sem chamar o `dataforge` a cada Tab.**
   Chamar o interpretador em cada tecla custaria ~100 ms por Tab — o
   bastante para a pessoa perceber e desligar.
"""

import re

#: Os comandos cujo argumento é um arquivo ou uma pasta.
COM_ARQUIVO = {"run", "check", "fmt", "lint", "test", "watch", "doc", "bench",
               "debug", "profile", "fix", "stats", "oop", "big-o", "deps",
               "tokens", "ast", "ir", "percurso", "alvo", "custo", "api",
               "converter", "crucible", "seguranca", "vitrine"}


def _catalogo():
    from .cli import GRUPOS
    comandos = []
    for _grupo, cmds in GRUPOS:
        for c in cmds:
            flags = []
            for flag, _desc in (c.opcoes or ()):
                base = re.split(r"[=\s<\[]", str(flag), maxsplit=1)[0]
                if base.startswith("-") and base not in flags:
                    flags.append(base)
            nomes = [c.nome] + [a for a in (c.apelidos or ())
                                if not a.startswith("-")]
            comandos.append({"nomes": nomes, "resumo": c.resumo,
                             "flags": flags})
    return comandos


def _todos_os_nomes(catalogo):
    return [n for c in catalogo for n in c["nomes"]]


def bash():
    cat = _catalogo()
    casos = []
    for c in cat:
        if c["flags"]:
            padrao = "|".join(c["nomes"])
            casos.append(f"        {padrao}) opcoes=\"{' '.join(c['flags'])}\" ;;")
    arquivos = "|".join(sorted(COM_ARQUIVO))
    return "\n".join([
        "# Autocompletar do DataForge para bash — gerado por",
        "# 'dataforge completar bash'. Instale com:",
        "#   dataforge completar bash > ~/.local/share/bash-completion/completions/dataforge",
        "",
        "_dataforge() {",
        "    local atual comando opcoes",
        '    atual="${COMP_WORDS[COMP_CWORD]}"',
        "    if [ \"$COMP_CWORD\" -eq 1 ]; then",
        f"        COMPREPLY=( $(compgen -W \"{' '.join(_todos_os_nomes(cat))}\" -- \"$atual\") )",
        "        return",
        "    fi",
        '    comando="${COMP_WORDS[1]}"',
        '    opcoes=""',
        '    case "$comando" in',
        *casos,
        "    esac",
        '    if [[ "$atual" == -* ]]; then',
        '        COMPREPLY=( $(compgen -W "$opcoes --help" -- "$atual") )',
        "        return",
        "    fi",
        '    case "$comando" in',
        f"        {arquivos}) COMPREPLY=( $(compgen -f -- \"$atual\") ) ;;",
        "    esac",
        "}",
        "complete -o filenames -F _dataforge dataforge df",
    ]) + "\n"


def _zsh_escapar(texto):
    return str(texto).replace("\\", "\\\\").replace("'", "'\\''").replace(":", "\\:")


def zsh():
    cat = _catalogo()
    itens = []
    for c in cat:
        for n in c["nomes"]:
            itens.append(f"    '{n}:{_zsh_escapar(c['resumo'])}'")
    casos = []
    for c in cat:
        partes = []
        if c["flags"]:
            partes.append(" ".join(f"'{f}'" for f in c["flags"]))
        if any(n in COM_ARQUIVO for n in c["nomes"]):
            partes.append("'*:arquivo:_files'")
        if partes:
            casos.append(f"        {'|'.join(c['nomes'])}) _arguments {' '.join(partes)} ;;")
    return "\n".join([
        "#compdef dataforge df",
        "# Autocompletar do DataForge para zsh — gerado por",
        "# 'dataforge completar zsh'. Instale com:",
        "#   dataforge completar zsh > \"${fpath[1]}/_dataforge\"",
        "",
        "_dataforge() {",
        "  local -a comandos",
        "  comandos=(",
        *itens,
        "  )",
        "  if (( CURRENT == 2 )); then",
        "    _describe 'comando' comandos",
        "    return",
        "  fi",
        "  case \"$words[2]\" in",
        *casos,
        "  esac",
        "}",
        "",
        '_dataforge "$@"',
    ]) + "\n"


def _fish_escapar(texto):
    return str(texto).replace("\\", "\\\\").replace("'", "\\'")


def fish():
    cat = _catalogo()
    linhas = [
        "# Autocompletar do DataForge para fish — gerado por",
        "# 'dataforge completar fish'. Instale com:",
        "#   dataforge completar fish > ~/.config/fish/completions/dataforge.fish",
        "",
        "complete -c dataforge -f",
    ]
    for c in cat:
        for n in c["nomes"]:
            linhas.append(
                f"complete -c dataforge -n '__fish_use_subcommand' -a '{n}' "
                f"-d '{_fish_escapar(c['resumo'])}'")
    for c in cat:
        cond = " ".join(c["nomes"])
        for f in c["flags"]:
            if f.startswith("--"):
                linhas.append(
                    f"complete -c dataforge -n '__fish_seen_subcommand_from {cond}' "
                    f"-l '{f[2:]}'")
        if any(n in COM_ARQUIVO for n in c["nomes"]):
            linhas.append(
                f"complete -c dataforge -n '__fish_seen_subcommand_from {cond}' -F")
    return "\n".join(linhas) + "\n"


SHELLS = {"bash": bash, "zsh": zsh, "fish": fish}


def executar(args):
    """Imprime o script. Devolve o código de saída."""
    from .cli import color
    qual = (args[0] if args else "").lower()
    if qual not in SHELLS:
        print(color("  uso: dataforge completar <bash|zsh|fish>", "1;33"))
        print()
        print("    bash   dataforge completar bash > ~/.local/share/bash-completion/completions/dataforge")
        print("    zsh    dataforge completar zsh > \"${fpath[1]}/_dataforge\"")
        print("    fish   dataforge completar fish > ~/.config/fish/completions/dataforge.fish")
        return 0 if not qual else 1
    print(SHELLS[qual](), end="")
    return 0
