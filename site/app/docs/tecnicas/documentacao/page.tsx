import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Documentação",
  description: "dataforge doc: gerar Markdown a partir dos comentários do código.",
};

const blocos: Bloco[] = [
  {"h2": "Usar"},
  { code: `dataforge doc lib.df                    # imprime no terminal
dataforge doc src/ --out=doc/API.md     # escreve num arquivo`, lang: 'bash' },
  {"h2": "A convenção"},
  {"p": "O comentário **imediatamente acima** de uma declaração é a sua documentação:"},
  { code: `// Biblioteca de geometria.
// Funcoes puras para calculos com formas planas.

// Precisao usada em todos os calculos
steady PI := 3.14159265

// Calcula a area de um circulo.
// O raio precisa ser positivo.
action area_circulo(raio: Number) -> Float:
    yield PI * raio ** 2`, title: `geometria.df` },
  {"p": "Os comentários do **topo do arquivo** viram a descrição do módulo. Linhas com `//` ou `#` valem igualmente."},
  {"h2": "O que é extraído"},
  {"table": {"head": ["Declaração", "Vira"], "rows": [["`steady`", "lista de constantes"], ["`record`", "tabela de campos, com tipo e se tem padrão"], ["`enum`", "lista de membros"], ["`trait`", "lista de assinaturas"], ["`blueprint`", "cabeçalho com herança e traits, mais os métodos"], ["`action`", "assinatura completa, com tipos e retorno"]]}},
  {"h2": "A saída"},
  { code: `# \`geometria.df\`

Biblioteca de geometria. Funcoes puras para calculos com formas planas.

## Constantes

- **\`PI\`** — Precisao usada em todos os calculos

## Ações

### \`area_circulo\`

\`\`\`dataforge
action area_circulo(raio: Number) -> Float
\`\`\`

Calcula a area de um circulo.
O raio precisa ser positivo.`, lang: 'text' },
  {"h2": "Por que escrever os comentários"},
  {"p": "Um comentário que descreve **o que a ação faz** e **quais são as pré-condições** vira documentação sem trabalho extra. Compare:"},
  { code: `// soma
action somar(a, b):

// Soma dois valores numericos.
// Textos sao concatenados; tipos incompativeis disparam TypeError.
action somar(a: Number, b: Number) -> Number:` },
  {"h2": "Num projeto"},
  { code: `dataforge doc src/ --out=doc/API.md`, lang: 'bash' },
  {"p": "Gera um Markdown único para todos os `.df` da pasta, na ordem alfabética, com um título por arquivo."},
];

const headings = [{ id: 'usar', text: "Usar", level: 2 as const }, { id: 'a-convencao', text: "A convenção", level: 2 as const }, { id: 'o-que-e-extraido', text: "O que é extraído", level: 2 as const }, { id: 'a-saida', text: "A saída", level: 2 as const }, { id: 'por-que-escrever-os-comentarios', text: "Por que escrever os comentários", level: 2 as const }, { id: 'num-projeto', text: "Num projeto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Documentação"}
      description={"dataforge doc: gerar Markdown a partir dos comentários do código."}
      href={"/docs/tecnicas/documentacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
