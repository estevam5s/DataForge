# Site de documentação do DataForge

Documentação da linguagem DataForge em Next.js 15 (App Router), exportada
como HTML estático. 122 rotas, todo o conteúdo em português.

## Rodar

```bash
npm install
npm run dev        # http://localhost:3000
```

## Build

```bash
npm run build      # gera out/ com 125 páginas estáticas
```

`next.config.mjs` usa `output: 'export'`, então **não há servidor Node**. Para
conferir o build localmente, sirva a pasta com qualquer servidor estático:

```bash
cd out && python3 -m http.server 4321
```

> `next start` não funciona com `output: 'export'` — é esperado.

Deploy: aponte a Vercel/Netlify/Pages para `out/`. O `404.html` gerado é
servido automaticamente por esses hosts.

## Estrutura

| Caminho | O que é |
|---|---|
| `lib/nav.ts` | As 122 rotas em 12 seções. **Fonte da verdade da navegação** — sidebar, busca e os links anterior/próximo saem daqui. |
| `lib/dados-gerados.json` | Extraído do repositório DataForge: assinaturas reais dos 20 módulos (674 símbolos), os 180 exercícios com código, 81 palavras-chave, 225 builtins. |
| `lib/highlight.ts` | Tokenizador do DataForge. Replica a regra `//` do lexer real e trata interpolação `$"{x}"`. |
| `lib/content.ts` | O tipo `Bloco` — as páginas são dados, não JSX solto. |
| `components/Doc.tsx` | `DocPage`, `H2`, `Callout`, `Table`, `CardGrid`. |
| `components/Search.tsx` | Paleta ⌘K com ranking ponderado. |
| `app/<rota>/page.tsx` | Uma página por rota, cada uma um array de `Bloco`. |

## Conteúdo derivado do código

Assinaturas de módulo, código de exercício e listas de palavras-chave vêm de
`lib/dados-gerados.json`, extraído programaticamente do repositório. Quando a
linguagem mudar, regenere esse arquivo em vez de editar as páginas à mão — é o
que impede a documentação de divergir do código.

## Verificações

```bash
npm run build                       # 125/125 páginas
npx tsc --noEmit                    # tipos
```

Um crawler simples sobre `out/**/*.html` confirma que nenhum link interno
aponta para rota inexistente.
