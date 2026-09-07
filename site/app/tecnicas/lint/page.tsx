import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Lint",
  description: "dataforge lint: as 13 regras de estilo e higiene.",
};

const blocos: Bloco[] = [
  {"h2": "O que ele faz"},
  {"p": "O `lint` encontra o que **compila mas provavelmente não é o que você quis dizer**. Não repete o que o [`check`](/tecnicas/analise-estatica) já reporta: aqui moram questões de higiene e estilo."},
  { code: `dataforge lint src/
dataforge lint . --strict     # avisos derrubam o build`, lang: 'bash' },
  {"h2": "As regras"},
  {"table": {"head": ["Código", "Encontra"], "rows": [["`unused-variable`", "variável atribuída e nunca lida"], ["`unused-import`", "módulo importado com `adopt` e nunca usado"], ["`unused-parameter`", "parâmetro de ação nunca lido no corpo"], ["`shadowed-name`", "nome local que esconde um de fora sem `shadow`"], ["`empty-block`", "bloco cujo corpo não faz nada"], ["`magic-number`", "número solto repetido 5 vezes ou mais"], ["`long-action`", "ação com mais de 60 linhas"], ["`deep-nesting`", "aninhamento de 5 níveis ou mais"], ["`naming-convention`", "blueprint fora de PascalCase, ação fora de snake_case"], ["`redundant-else`", "`otherwise` depois de um ramo que sempre retorna"], ["`double-negation`", "`not not x`"], ["`comparison-to-bool`", "`x is yes` / `x is no`"], ["`todo-comment`", "comentário TODO/FIXME (informativo)"]]}},
  {"h2": "A saída"},
  { code: `app.df:2:1: aviso: Module 'Arcane.Text' is imported but never used
    sugestão: Remove the 'adopt' line
app.df:4:1: aviso: Action 'CalcularTotal' does not follow snake_case
    sugestão: Rename it to 'calcular_total'
app.df:7:5: aviso: Variable 'naoUsada' is assigned but never read
    sugestão: Remove it, or rename it to '_naoUsada' to say it is on purpose`, lang: 'text' },
  {"h2": "Calibragem"},
  {"p": "As regras foram ajustadas contra os 225 arquivos do repositório até restarem apenas avisos legítimos. Duas exceções foram codificadas explicitamente:"},
  {"list": ["**Métodos especiais** (`toString`, `setup`, `add`, `mul`…) não seguem snake_case porque o runtime os chama pelo nome — a grafia é parte do contrato.", "**Assinaturas de trait** (ações sem corpo) não disparam `empty-block` nem `unused-parameter`."]},
  {"h2": "Silenciar de propósito"},
  {"p": "Um `_` no início do nome diz \"não usar isto é intencional\":"},
  { code: `cycle _ in range(0, 3):        # o valor não interessa
    fazer_algo()

action f(dados, _contexto):    # parâmetro exigido pela interface
    yield processar(dados)` },
  {"h2": "Configurar no projeto"},
  { code: `[lint]
strict = false
ignore = ["magic-number", "todo-comment"]`, lang: 'toml', title: `forge.toml` },
];

const headings = [{ id: 'o-que-ele-faz', text: "O que ele faz", level: 2 as const }, { id: 'as-regras', text: "As regras", level: 2 as const }, { id: 'a-saida', text: "A saída", level: 2 as const }, { id: 'calibragem', text: "Calibragem", level: 2 as const }, { id: 'silenciar-de-proposito', text: "Silenciar de propósito", level: 2 as const }, { id: 'configurar-no-projeto', text: "Configurar no projeto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Lint"}
      description={"dataforge lint: as 13 regras de estilo e higiene."}
      href={"/tecnicas/lint"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
