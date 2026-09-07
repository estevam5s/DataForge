#!/usr/bin/env bash
# Testa cada pacote de packages/ instalando-o num projeto limpo.
# É o único jeito de provar que o pacote funciona como pacote — rodar
# os testes de dentro da pasta não exercita a instalação nem o 'adopt'.
set -u
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"

# O registro do proprio repositorio: um pacote com dependencia precisa
# achar a versao que esta aqui, nao a que ja foi publicada.
export DATAFORGE_REGISTRY="file://$RAIZ/site/public/registry"
BANCADA="${TMPDIR:-/tmp}/df_bancada"
falhas=0; total=0

for pkg in "$RAIZ"/packages/*/; do
  nome=$(basename "$pkg")
  [ -d "$pkg/tests" ] || continue
  total=$((total + 1))

  rm -rf "$BANCADA"; mkdir -p "$BANCADA/src"
  printf '[project]\nname = "bancada"\nversion = "0.1.0"\nentry = "src/main.df"\n\n[dependencies]\n' \
    > "$BANCADA/forge.toml"

  saida=$(cd "$BANCADA" && dataforge add "$pkg" 2>&1)
  if [ $? -ne 0 ]; then
    printf "  \033[1;31m✗\033[0m %-16s instalação falhou\n" "$nome"
    echo "$saida" | tail -3 | sed 's/^/      /'
    falhas=$((falhas + 1)); continue
  fi

  # o linter pega o que o analisador não vê: variável escrita e nunca
  # lida, nome fora do padrão, ramo redundante
  sujeira=$(dataforge lint "$pkg/src" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -c "aviso:")
  if [ "$sujeira" -gt 0 ]; then
    printf "  \033[1;33m!\033[0m %-16s %s aviso(s) de lint\n" "$nome" "$sujeira"
    dataforge lint "$pkg/src" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep "aviso:" | head -3 | sed 's/^/      /'
    falhas=$((falhas + 1)); continue
  fi

  cp -r "$pkg/tests" "$BANCADA/"
  resultado=$(cd "$BANCADA" && dataforge test tests/ 2>&1)
  if echo "$resultado" | grep -q "FALHOU\|✗"; then
    printf "  \033[1;31m✗\033[0m %-16s %s\n" "$nome" \
      "$(echo "$resultado" | sed 's/\x1b\[[0-9;]*m//g' | grep -E 'passaram|falharam' | tail -1)"
    echo "$resultado" | sed 's/\x1b\[[0-9;]*m//g' | grep -A2 FALHOU | head -6 | sed 's/^/      /'
    falhas=$((falhas + 1))
  else
    n=$(echo "$resultado" | sed 's/\x1b\[[0-9;]*m//g' | grep -oE '[0-9]+ passaram' | head -1)
    printf "  \033[1;32m✓\033[0m %-16s %s\n" "$nome" "$n"
  fi
done

rm -rf "$BANCADA"
echo
if [ $falhas -eq 0 ]; then
  printf "\033[1;32m%d/%d pacotes verdes\033[0m\n" "$total" "$total"
else
  printf "\033[1;31m%d de %d pacotes com falha\033[0m\n" "$falhas" "$total"
  exit 1
fi
