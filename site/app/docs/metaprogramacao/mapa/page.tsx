// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/metaprogramacao.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Metaprogramação: o mapa",
  description: "Item por item da parte 5 da referência Deep Tech — comptime, macros, DSLs e compiler plugins — cruzado com o que o DataForge tem.",
};

const blocos: Bloco[] = [
  {"p": "A quinta parte de uma referência Deep Tech cobre computação em tempo de compilação, macros, DSLs e plugins do compilador. Boa parte dela pressupõe um **compilador** com fases separadas. Aqui a \"compilação\" é `parse` + `check` + carga — e é nessas três que as peças abaixo se encaixam."},
  {"h2": "22 · Computação em tempo de compilação"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["`comptime`", "existe: roda na carga, numa caixa sem E/S, e congela o resultado", "[comptime](/docs/metaprogramacao/comptime)"], ["const evaluation", "`comptime steady NOME := …` — constante calculada", "[comptime](/docs/metaprogramacao/comptime)"], ["funções executadas no build", "ações declaradas **dentro** do bloco `comptime`", "[comptime](/docs/metaprogramacao/comptime)"], ["geração de constantes, lookup tables", "o caso central: a tabela é calculada uma vez", "[comptime](/docs/metaprogramacao/comptime)"], ["validações estáticas", "`assert` dentro de `comptime`; o `check` acusa (`comptime-falhou`)", "[comptime](/docs/metaprogramacao/comptime)"], ["cálculos matemáticos em compile-time", "sim — é conta pura, que é o que a caixa permite", "[comptime](/docs/metaprogramacao/comptime)"], ["especialização de código", "**não existe** em build: o caminho é `overload` (decide na chamada) e a macro (reescreve o corpo)", "[Sobrecarga](/docs/oop/sobrecarga)"], ["geração de tipos", "**parcial**: alias genérico (`type Par<T> := …`) e argumento numérico (`Vetor<3>`)", "[Generics](/docs/tipos/genericos)"]]}},
  {"h2": "23 · Macros"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["macros procedurais", "`Arcane.Macro`: a árvore como dado, transformada por código comum", "[Macros](/docs/metaprogramacao/macros)"], ["AST manipulation e transformation", "`arvore`, `percorrer`, `transformar`, `substituir`, `reescrever`", "[Macros](/docs/metaprogramacao/macros)"], ["expansão de macros", "acontece na **carga**, quando o decorador é aplicado", "[Macros](/docs/metaprogramacao/macros)"], ["macros de atributo", "`mark @M.derivar(…)` sobre um blueprint", "[Macros](/docs/metaprogramacao/macros)"], ["macros derivadas", "`texto`, `igualdade`, `ordem`, `vault` a partir dos campos", "[Macros](/docs/metaprogramacao/macros)"], ["higiene de macros", "**explícita**: `nome_fresco` e `renomear` — automática exigiria saber o que é \"de dentro\"", "[Macros](/docs/metaprogramacao/macros)"], ["macros declarativas (padrão → substituição)", "**não existem** como forma própria: o mesmo se escreve com `transformar` e um `given`", "—"], ["token streams", "**não se expõem**: a macro trabalha sobre a árvore, que é o nível em que o significado já está resolvido", "—"]]}},
  {"h2": "24 · DSLs"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["DSLs internas", "blueprint com operadores, pipeline `>>`, ação de alta ordem — e as palavras contextuais do Kiln e do Quadro", "[Kiln](/docs/kiln)"], ["DSLs externas", "`Arcane.Dsl`: combinadores de análise, com falha que diz a posição", "[DSLs](/docs/metaprogramacao/dsl)"], ["parser extensions", "**não existem** como plugin: palavra nova na linguagem é mexer no parser — foi assim com as onze do Kiln e os seis verbos do Quadro", "—"], ["AST híbrida", "a árvore de `M.citar` e a do arquivo são **a mesma**, e é isso que deixa gerar código que roda", "[Macros](/docs/metaprogramacao/macros)"], ["geração de código, templates", "`M.compilar(texto, …)` e `M.acao(…)`; para texto puro, `$\"{}\"` e `Arcane.Text`", "[Macros](/docs/metaprogramacao/macros)"]]}},
  {"h2": "25 · Compiler plugins"},
  {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [["plugins do compilador", "plugins do `check`: um `.df` com `verificar(arvore, arquivo)`", "[Plugins](/docs/metaprogramacao/plugins)"], ["custom lints", "é exatamente o caso de uso, com código próprio e silenciamento", "[Plugins](/docs/metaprogramacao/plugins)"], ["analisadores estáticos", "a árvore inteira é entregue; o que o plugin prova, ele acusa", "[Plugins](/docs/metaprogramacao/plugins)"], ["hooks", "um hook só: `verificar`. Mais hooks sem caso de uso viram superfície para manter", "[Plugins](/docs/metaprogramacao/plugins)"], ["análise de fluxo", "possível dentro do plugin (a ordem das instruções está na árvore); o que **não** existe é um grafo de fluxo pronto", "—"], ["transformações de AST no compilador", "**não existem** por plugin: transformar é trabalho de macro, na carga do arquivo — um plugin do `check` que reescrevesse código faria `check` e `run` discordarem", "—"], ["verificação formal", "**não existe**: o refinamento é verificado, não provado", "[Tipos nomeados](/docs/tipos-nomeados)"]]}},
  {"h2": "O resumo honesto"},
  {"p": "Das quatro seções, **três** têm resposta direta: `comptime`, macros sobre a árvore e plugins do `check`. A quarta — DSLs — tem duas respostas: a interna, que sempre existiu, e a externa, agora com combinadores."},
  {"p": "O que não existe tem um padrão: tudo o que exige **mexer no parser em tempo de execução** (parser extensions, token streams, macros declarativas com sintaxe nova). Isso é decisão de linguagem, e as vezes em que valeu a pena — as onze palavras do Kiln, os seis verbos do Quadro, as treze de OOP — foram feitas no parser, com o custo explicado em cada uma."},
];

const headings = [{ id: '22-computacao-em-tempo-de-compilacao', text: "22 · Computação em tempo de compilação", level: 2 as const }, { id: '23-macros', text: "23 · Macros", level: 2 as const }, { id: '24-dsls', text: "24 · DSLs", level: 2 as const }, { id: '25-compiler-plugins', text: "25 · Compiler plugins", level: 2 as const }, { id: 'o-resumo-honesto', text: "O resumo honesto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Metaprogramação: o mapa"}
      description={"Item por item da parte 5 da referência Deep Tech — comptime, macros, DSLs e compiler plugins — cruzado com o que o DataForge tem."}
      href={"/docs/metaprogramacao/mapa"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
