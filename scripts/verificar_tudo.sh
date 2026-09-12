#!/bin/sh
# Roda o que a CI roda, na mesma ordem, antes de commitar.
#
# Por que este arquivo existe
# ---------------------------
# A verificacao local era 'pytest + run_all + examples + projetos', e
# isso deixava de fora tres passos que a CI faz — e os tres derrubaram
# a CI de uma vez:
#
#   1. 'fmt --check'         — oito exercicios novos nao formatados
#   2. os geradores          — 'gerar_ref_kiln.py' RECUSOU rodar porque
#                              nove simbolos novos do Kiln nao estavam
#                              descritos; a trava fez o trabalho dela,
#                              e ninguem a acionou localmente
#   3. o diff do gerado      — o que o gerador produz tem de ser
#                              identico ao que esta versionado
#
# Usa o Python do ambiente. Com o .venv ativo, e o do repositorio.
#
#   sh scripts/verificar_tudo.sh          tudo
#   sh scripts/verificar_tudo.sh rapido   sem o site (que leva ~40s)

set -e

# ABSOLUTO: os passos que entram em subpasta (projetos, pacotes, site)
# quebrariam com um caminho relativo, e o sintoma seria "todo projeto
# falhou" — que e o oposto de informativo.
RAIZ=$(cd "$(dirname "$0")/.." && pwd)
PY="${PYTHON:-python3}"
[ -x "$RAIZ/.venv/bin/python3" ] && PY="$RAIZ/.venv/bin/python3"
cd "$RAIZ"
MODO="${1:-tudo}"

vermelho() { printf '\033[1;31m%s\033[0m\n' "$1"; }
verde()    { printf '\033[1;32m%s\033[0m\n' "$1"; }
passo()    { printf '\n\033[1;36m── %s\033[0m\n' "$1"; }

falhou=0
registrar() {
    if [ "$1" -ne 0 ]; then
        vermelho "   ✗ $2"
        falhou=1
    else
        verde "   ✓ $2"
    fi
}

passo "a suite"
$PY -m pytest tests/ -q > /tmp/df_pytest.txt 2>&1 || true
tail -1 /tmp/df_pytest.txt
grep -q "failed\|error" /tmp/df_pytest.txt && registrar 1 "pytest" || registrar 0 "pytest"

passo "os exercicios"
$PY exercicios/run_all.py > /tmp/df_ex.txt 2>&1
registrar $? "exercicios"
tail -2 /tmp/df_ex.txt | head -1

passo "os exemplos"
erros=0
for f in examples/*.df; do
    $PY -m dataforge run "$f" > /dev/null 2>&1 || { vermelho "   $f"; erros=1; }
done
registrar $erros "exemplos"

passo "os projetos"
erros=0
for p in projetos/*/; do
    (cd "$p" && $PY -m dataforge test > /dev/null 2>&1) || { vermelho "   $p"; erros=1; }
done
registrar $erros "projetos"

passo "os pacotes"
erros=0
for p in packages/*/; do
    [ -d "$p/tests" ] || continue
    # Um pacote com dependencia declarada precisa de 'install' antes;
    # a CI nao roda estes, e aqui eles sao informativos.
    (cd "$p" && $PY -m dataforge test > /dev/null 2>&1) || erros=$((erros + 1))
done
[ "$erros" -le 1 ] && registrar 0 "pacotes ($erros precisa(m) de install)" \
                   || registrar 1 "pacotes: $erros falharam"

passo "as proprias ferramentas"
# 'projetos/' ficava de fora, e era o unico lugar com import
# relativo entre arquivos — o caminho que estourava um traceback
# do Python dentro do analisador sem ninguem ver.
$PY -m dataforge check exercicios/ examples/ packages/ projetos/ \
    > /tmp/df_check.txt 2>&1
registrar $? "check"
$PY -m dataforge fmt exercicios/ examples/ packages/ projetos/ --check > /tmp/df_fmt.txt 2>&1
registrar $? "fmt --check"
tail -2 /tmp/df_fmt.txt | head -1
$PY -m dataforge lint exercicios/ > /tmp/df_lint.txt 2>&1
registrar $? "lint"

passo "os trechos da doc compilam"
$PY tools/verificar_docs.py > /tmp/df_docs.txt 2>&1
registrar $? "verificar_docs"
tail -2 /tmp/df_docs.txt | head -1

passo "regerar tudo, e conferir o diff"
# O DIFF, e nao 'git status': comparar o status pegaria tambem o que
# ja estava modificado antes de o script rodar, e o relatorio acusaria
# "um gerador mudou isto" sobre o trabalho de quem esta editando.
antes=$(git diff | shasum 2>/dev/null || git diff | md5sum)
for gerador in \
    tools/gerar_gramatica.py \
    tools/gerar_doc_stdlib.py \
    tools/gerar_ref_kiln.py \
    tools/gerar_ref_vitrine.py \
    tools/gerar_pagina_biblioteca.py \
    tools/gerar_indice_exercicios.py \
    scripts/gerar_api.py \
    site/scripts/gerar_dados.py \
    site/scripts/gerar_conteudo.py \
    site/scripts/gerar_indices.py \
    scripts/gerar_superficie.py
do
    [ -f "$gerador" ] || continue
    # Alguns geradores do site esperam rodar de dentro de site/scripts.
    case "$gerador" in
        site/scripts/*) (cd site/scripts && $PY "$(basename "$gerador")" > /dev/null 2>&1) ;;
        *)              $PY "$gerador" > /dev/null 2>&1 ;;
    esac
    if [ $? -ne 0 ]; then
        vermelho "   ✗ $gerador recusou rodar"
        case "$gerador" in
            site/scripts/*) (cd site/scripts && $PY "$(basename "$gerador")" 2>&1 | tail -4) ;;
            *)              $PY "$gerador" 2>&1 | tail -4 ;;
        esac
        falhou=1
    fi
done
depois=$(git diff | shasum 2>/dev/null || git diff | md5sum)
if [ "$antes" != "$depois" ]; then
    vermelho "   ✗ um gerador mudou arquivo versionado — commite:"
    printf '     (o que mudou AGORA, ao rodar os geradores)\n'
    git --no-pager diff --stat | tail -12
    falhou=1
else
    verde "   ✓ nada gerado esta atrasado"
fi

if [ "$MODO" != "rapido" ]; then
    passo "o site compila"
    if [ -d site/node_modules ]; then
        (cd site && npx tsc --noEmit > /tmp/df_tsc.txt 2>&1)
        registrar $? "tsc --noEmit"
        (cd site && npm run build > /tmp/df_build.txt 2>&1)
        registrar $? "next build"
    else
        printf '   (site/node_modules ausente: rode npm ci)\n'
    fi

    passo "a extensao compila"
    if [ -d editor/vscode/node_modules ]; then
        (cd editor/vscode && npx tsc -p ./ --noEmit > /tmp/df_ext.txt 2>&1)
        registrar $? "tsc da extensao"
    else
        printf '   (editor/vscode/node_modules ausente)\n'
    fi
fi

printf '\n'
if [ "$falhou" -ne 0 ]; then
    vermelho "algo falhou — veja acima"
    exit 1
fi
verde "tudo verde"
