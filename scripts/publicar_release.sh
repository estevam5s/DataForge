#!/usr/bin/env bash
# Publica um release da linguagem — e confere o que foi publicado.
#
#   bash scripts/publicar_release.sh              # so confere e mostra os comandos
#   bash scripts/publicar_release.sh --executar   # marca, empurra, espera o CI e confere
#
# Por que existe
# --------------
# O .deb da primeira versao foi publicado com 1.194 bytes. O gerador ja estava
# corrigido no 'main'; a tag 'v1.0.0' e que apontava para um commit
# ANTERIOR a correcao, e o CI empacotou o codigo daquela tag. Nada no
# caminho entre "marcar" e "publicar" olhava o que ia sair.
#
# Este script e esse caminho, escrito:
#   1. 'gh' autenticado
#   2. arvore limpa, e o HEAD igual ao 'origin/main' — a tag marca o que
#      esta publicado no repositorio, e nao o que esta so nesta maquina
#   3. a tag e a versao do codigo, e ela ainda nao existe
#   4. o .deb gerado AQUI passa pelo piso de tamanho antes de marcar
#   5. so entao a tag; o workflow 'release.yml' constroi e publica
#   6. o release publicado e conferido: o .deb acima do piso, e cada
#      arquivo da pagina /download baixando de verdade
#
# A versao NAO e escolhida aqui. Subir a versao e decisao de quem mantem:
# mude 'dataforge/__init__.py' e 'pyproject.toml' (o release.yml recusa os
# dois divergindo) e os demais lugares que 'tests/test_api_e_marca.py'
# confere, e rode este script.

set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-python3}"
EXECUTAR=0
[ "${1:-}" = "--executar" ] && EXECUTAR=1

versao=$("$PY" -c 'import dataforge; print(dataforge.__version__)')
projeto=$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml | head -1)
tag="v$versao"
piso=2097152

erro() { printf '  \033[1;31m✗\033[0m %s\n' "$*"; exit 1; }
ok()   { printf '  \033[1;32m✓\033[0m %s\n' "$*"; }

echo
echo "  DataForge $versao — release $tag"
echo

# ── 1. gh ──
command -v gh >/dev/null 2>&1 || erro "o GitHub CLI nao esta instalado: https://cli.github.com"
if ! gh auth status >/dev/null 2>&1; then
    erro "o gh nao esta autenticado. Rode:
       gh auth login --hostname github.com --git-protocol https --web
     (ou exporte GH_TOKEN com um token de escopo 'repo' e 'workflow')"
fi
ok "gh autenticado"

# ── 2. a arvore ──
[ -z "$(git status --porcelain --untracked-files=no)" ] \
    || erro "ha mudancas nao commitadas — a tag marcaria outra coisa"
git fetch --quiet origin main --tags
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] \
    || erro "o HEAD nao e o origin/main — faca push antes de marcar"
ok "HEAD = origin/main ($(git rev-parse --short HEAD))"

# ── 3. a versao ──
[ "$versao" = "$projeto" ] \
    || erro "dataforge/__init__.py diz $versao e pyproject.toml diz $projeto"
if git ls-remote --exit-code --tags origin "refs/tags/$tag" >/dev/null 2>&1; then
    erro "a tag $tag ja existe no GitHub. Uma versao publicada nao se republica:
       quem baixou tem o SHA256SUMS dela. Suba a versao e rode de novo."
fi
ok "a tag $tag ainda nao existe"

# ── 4. o .deb, antes de marcar ──
saida=$(mktemp -d)
trap 'rm -rf "$saida"' EXIT
DF_PACOTES_SAIDA="$saida" "$PY" packaging/gerar_pacotes.py >/dev/null
deb="$saida/dataforge_${versao}_all.deb"
bytes=$(wc -c < "$deb" | tr -d ' ')
[ "$bytes" -ge "$piso" ] || erro "o .deb local tem $bytes bytes (piso $piso)"
ok "o .deb local tem $((bytes / 1024 / 1024)) MB"
"$PY" -m pytest tests/test_release_deb.py -q -p no:cacheprovider >/dev/null \
    || erro "as travas do release reprovaram: pytest tests/test_release_deb.py"
ok "as travas do release passam"

echo
echo "  Os comandos:"
echo
echo "    git tag -a $tag -m \"DataForge $versao\""
echo "    git push origin $tag"
echo "    gh run watch \"\$(gh run list --workflow=release.yml --limit 1 --json databaseId -q '.[0].databaseId')\" --exit-status"
echo "    gh release view $tag --json assets -q '.assets[] | \"\\(.name) \\(.size)\"'"
echo "    python3 scripts/verificar_downloads.py"
echo
echo "  O release e criado pelo workflow (softprops/action-gh-release), com"
echo "  todos os binarios e o SHA256SUMS. Para um release SO com o .deb e o"
echo "  PKGBUILD, sem esperar o CI:"
echo
echo "    gh release create $tag \"$deb\" packaging/arch/PKGBUILD \\"
echo "        --verify-tag --title \"DataForge $versao\" --generate-notes"
echo

if [ "$EXECUTAR" -eq 0 ]; then
    echo "  (nada foi feito — rode com --executar)"
    echo
    exit 0
fi

# ── 5. marcar ──
git tag -a "$tag" -m "DataForge $versao"
git push origin "$tag"
ok "tag $tag empurrada — o release.yml comecou"

sleep 10
execucao=$(gh run list --workflow=release.yml --limit 1 --json databaseId -q '.[0].databaseId')
gh run watch "$execucao" --exit-status || erro "o workflow falhou: gh run view $execucao --log-failed"

# ── 6. conferir o que saiu ──
publicado=$(gh release view "$tag" --json assets \
    -q ".assets[] | select(.name == \"dataforge_${versao}_all.deb\") | .size")
[ -n "$publicado" ] || erro "o release $tag nao tem o .deb"
[ "$publicado" -ge "$piso" ] || erro "o .deb PUBLICADO tem $publicado bytes"
ok "o .deb publicado tem $((publicado / 1024 / 1024)) MB"

"$PY" scripts/verificar_downloads.py || erro "algum download da pagina nao baixa"
ok "release $tag publicado e conferido"
