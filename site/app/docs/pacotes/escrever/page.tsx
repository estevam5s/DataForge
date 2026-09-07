import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escrever uma biblioteca",
  description: "Do esqueleto ao registro, com o que separa uma boa de uma qualquer.",
};

const blocos: Bloco[] = [
  {"h2": "O esqueleto"},
  { code: `meu-pacote/
├── forge.toml
├── README.md
├── src/
│   └── main.df        o ponto de entrada
└── tests/
    └── meu_pacote_test.df`, lang: 'bash' },
  {"h2": "O manifesto"},
  { code: `[package]
name = "texto"
version = "1.0.0"
description = "Texto: slug, truncar, mascarar, distância de edição, similaridade e templates."
authors = ["DataForge"]
license = "MIT"
entry = "src/main.df"
dataforge = ">=4.1"
keywords = ["texto", "string", "slug"]

[dependencies]

[scripts]
test = "test tests/"`, lang: 'toml' },
  {"h2": "A API é o que o relay exporta"},
  { code: `action publica(x):
    yield _interna(x) * 2

action _interna(x):        // detalhe: não sai
    yield x + 1

relay publica`, lang: 'df' },
  {"p": "Tudo o que atravessa o `relay` é promessa. Mudar a assinatura de algo exportado quebra quem depende — e é por isso que a lista deve ser curta e deliberada."},
  {"h2": "Testar como pacote, não como arquivo"},
  {"p": "Rodar os testes de dentro da pasta não exercita a instalação nem o `adopt`. O jeito de provar que funciona é instalar num projeto limpo:"},
  { code: `cd /tmp && mkdir bancada && cd bancada
printf '[project]\\nname="bancada"\\nversion="0.1.0"\\n\\n[dependencies]\\n' > forge.toml
dataforge add ~/meu-pacote
cp -r ~/meu-pacote/tests .
dataforge test tests/`, lang: 'bash' },
  {"p": "O repositório do DataForge automatiza isso em `scripts/testar_libs.sh`, e roda para os 20 pacotes a cada mudança."},
  {"h2": "O linter guia a estrutura"},
  {"p": "`dataforge lint src/` aponta ação longa demais, aninhamento profundo, número mágico repetido e parâmetro nunca usado. Vale seguir: as bibliotecas do registro foram divididas exatamente onde ele apontou."},
  {"p": "Quando a regra não serve ao seu caso, desligue no manifesto — e diga por quê:"},
  { code: `[lint]
# A tabela de pesos do CPF/CNPJ é a especificação do documento: são
# números que não se pode nomear, porque não significam nada sozinhos.
ignore = ["magic-number"]`, lang: 'toml' },
  {"h2": "Publicar"},
  { code: `dataforge pack
dataforge publish --registry=/caminho/do/registro`, lang: 'bash' },
  {"p": "O tarball é reprodutível: mesma fonte, mesmo sha256. Republicar a mesma versão é recusado — suba a `version` primeiro, porque um lockfile apontando para conteúdo que mudou é pior que um erro."},
  {"h2": "Versionar"},
  {"table": {"head": ["Mudança", "Sobe", "Exemplo"], "rows": [["Corrigiu um bug", "correção", "1.0.0 → 1.0.1"], ["Acrescentou algo", "menor", "1.0.1 → 1.1.0"], ["Quebrou compatibilidade", "maior", "1.1.0 → 2.0.0"]]}},
  {"p": "Quem depende de você escreveu `^1.0.0`. Enquanto o `maior` não sobe, essa pessoa recebe suas versões automaticamente — e conta com que nada quebre."},
  {"h2": "Uma biblioteca boa"},
  {"list": ["**Resolve um problema**, não cinco. `moeda` não formata data.", "**Explica por que existe** no cabeçalho — o que o código não diz sozinho.", "**Falha com mensagem útil.** `trigger \"nao da para operar BRL com USD sem converter\"` vale mais que um `void` silencioso.", "**Tem teste do caso difícil**, não só do fácil: repartir 10 reais em 3 sem perder centavo, arredondar 2,5 para cima."]},
];

const headings = [{ id: 'o-esqueleto', text: "O esqueleto", level: 2 as const }, { id: 'o-manifesto', text: "O manifesto", level: 2 as const }, { id: 'a-api-e-o-que-o-relay-exporta', text: "A API é o que o relay exporta", level: 2 as const }, { id: 'testar-como-pacote-nao-como-arquivo', text: "Testar como pacote, não como arquivo", level: 2 as const }, { id: 'o-linter-guia-a-estrutura', text: "O linter guia a estrutura", level: 2 as const }, { id: 'publicar', text: "Publicar", level: 2 as const }, { id: 'versionar', text: "Versionar", level: 2 as const }, { id: 'uma-biblioteca-boa', text: "Uma biblioteca boa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Escrever uma biblioteca"}
      description={"Do esqueleto ao registro, com o que separa uma boa de uma qualquer."}
      href={"/docs/pacotes/escrever"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
