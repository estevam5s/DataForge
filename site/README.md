# Site do DataForge

Landing institucional em `/` e a documentação completa em `/docs`, num único
app Next.js 15 (App Router) exportado como HTML estático. 123 rotas, todo o
conteúdo em português.

## Rodar

```bash
npm install
npm run dev        # http://localhost:3000
```

## Build

```bash
npm run build      # gera out/ com 126 páginas estáticas
```

`next.config.mjs` usa `output: 'export'`, então **não há servidor Node**.
Para conferir o build, sirva a pasta com qualquer servidor estático:

```bash
cd out && python3 -m http.server 4321
```

> `next start` não funciona com `output: 'export'` — é esperado.

Deploy: aponte a Vercel/Netlify/Pages para `out/`. O `404.html` gerado é
servido automaticamente por esses hosts.

## As duas metades

| Rota | O que é | Chrome |
|---|---|---|
| `/` | Landing institucional | Nav flutuante próprio, rodapé próprio, **sempre escura** |
| `/docs/**` | 122 páginas de documentação | Cabeçalho com busca ⌘K, sidebar, tema claro/escuro |

O layout raiz (`app/layout.tsx`) carrega só as fontes e o script de tema.
O chrome da documentação vive em `app/docs/layout.tsx`, então a landing não
o herda. A landing usa tokens próprios no escopo `.lp` (em `globals.css`),
fora das variáveis de tema — é por isso que ela continua escura mesmo com a
documentação no claro.

## Estrutura

| Caminho | O que é |
|---|---|
| `lib/nav.ts` | As 122 rotas de `/docs` em 12 seções. **Fonte da verdade da navegação** — sidebar, busca e os links anterior/próximo saem daqui. |
| `lib/dados-gerados.json` | Gerado do repositório: 20 módulos com 674 símbolos reais, 180 exercícios com código, 81 palavras reservadas, 225 embutidas. |
| `lib/trechos-landing.json` | Os quatro trechos da seção Sintaxe, com o código e **a saída capturada da execução**. |
| `lib/highlight.ts` | Tokenizador do DataForge. Replica a regra `//` do lexer real e trata interpolação `$"{x}"`. |
| `scripts/gerar_dados.py` | Regenera `dados-gerados.json` a partir do código. |
| `components/landing/` | Seções da landing: `Heroi`, `Pilares`, `Manifesto`, `Ferramentas`, `Sintaxe`, `Arcane`, `Aprender`, `RodapeSite`. |
| `components/Doc.tsx` | `DocPage`, `H2`, `Callout`, `Table`, `CardGrid` da documentação. |
| `app/docs/<rota>/page.tsx` | Uma página por rota, cada uma um array de `Bloco`. |

## Conteúdo derivado do código

Assinaturas de módulo, código de exercício, palavras reservadas e embutidas
vêm de `lib/dados-gerados.json`. Quando a linguagem mudar:

```bash
python3 scripts/gerar_dados.py
```

Isso importa `dataforge.stdlib` e `dataforge.builtins` do repositório-pai e
reescreve o JSON. **Nunca edite totais à mão nas páginas** — foi assim que a
grade da landing chegou a dizer 661 símbolos enquanto a documentação dizia 674.

As saídas de terminal da seção Ferramentas foram copiadas de execuções reais
(`dataforge check`, `fmt`, `lint`, `test`, `repl`). Se a saída de um comando
mudar, atualize `components/landing/Ferramentas.tsx`.

## Verificações

```bash
npm run build                       # 126/126 páginas
npx tsc --noEmit                    # tipos
```

E um crawler sobre `out/**/*.html` confirmando que nenhum link interno aponta
para rota inexistente:

```bash
cd out && python3 - <<'PY'
import re, pathlib, collections
raiz = pathlib.Path('.')
existentes = {('/' + str(p.parent.relative_to(raiz)).replace('.','')).rstrip('/') or '/'
              for p in raiz.rglob('index.html')}
q = collections.defaultdict(list)
for f in raiz.rglob('*.html'):
    o = ('/' + str(f.parent.relative_to(raiz)).replace('.','')).rstrip('/') or '/'
    for h in re.findall(r'href="(/[^"#?]*)"', f.read_text()):
        a = h.rstrip('/') or '/'
        if a.startswith('/_next') or '.' in a.rsplit('/',1)[-1]: continue
        if a not in existentes: q[a].append(o)
print(len(existentes), 'rotas |', 'OK' if not q else f'{len(q)} QUEBRADOS')
for a, o in sorted(q.items()): print('  QUEBRADO', a, '←', o[0])
PY
```
