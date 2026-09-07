import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Perguntas frequentes",
  description: "As dúvidas mais comuns sobre a linguagem, seu escopo e suas escolhas.",
};

const blocos: Bloco[] = [
  {"h2": "É uma linguagem de verdade?"},
  {"p": "Sim. DataForge tem lexer, parser recursivo descendente, AST tipada, analisador estático e interpretador de árvore próprios — cerca de 19 mil linhas de Python. Não é um wrapper sobre `eval`: cada construção tem seu nó de AST e sua regra de avaliação."},
  {"p": "A prova prática: um dos exercícios é um [interpretador de expressões escrito em DataForge](/docs/receitas/interpretador), com lexer, parser e avaliador. A linguagem é expressiva o bastante para implementar outra."},
  {"h2": "Por que não usar Python direto?"},
  {"p": "Se o objetivo é produtividade imediata em produção, use Python. DataForge existe por outras razões:"},
  {"list": ["**Vocabulário que descreve intenção** — `given`/`monitor`/`blueprint` em vez de `if`/`try`/`class`", "**Pipelines como sintaxe**, não biblioteca", "**Erros que ensinam** — cada mensagem sugere a correção", "**Análise estática opcional** que não exige anotar tudo", "Ser um **objeto de estudo** completo de como se constrói uma linguagem"]},
  {"h2": "Por que `:=` em vez de `=`?"},
  {"p": "Elimina a confusão clássica entre atribuição e comparação. Em DataForge, `=` sozinho não existe — então `given x = 5` é erro de sintaxe, não um bug silencioso."},
  {"h2": "Por que `yes`/`no` em vez de `true`/`false`?"},
  {"p": "Consistência com o vocabulário. A linguagem inteira usa palavras curtas e diretas; `yes`/`no` cabe nessa família melhor que `true`/`false`."},
  {"h2": "Por que `//` é comentário e não divisão?"},
  {"p": "`//` abre comentário em praticamente toda linguagem da família C. Fazer dele divisão inteira, como Python, quebraria a expectativa de quem vem de C, Java, JavaScript, Go ou Rust."},
  {"p": "A regra é conservadora: **comentário por padrão**, divisão só quando o que vem depois não pode ser prosa. Para não pensar nisso, existe `~/`."},
  {"h2": "Preciso anotar os tipos?"},
  {"p": "Não. Anotar é opcional e você escolhe onde. A recomendação prática: anote a **fronteira** — parâmetros e retorno de ações públicas, campos de record — e deixe o interior livre."},
  {"h2": "Dá para usar em produção?"},
  {"p": "Depende do que \"produção\" significa no seu caso. O que existe e é testado: 272 testes, 190 exercícios, 42 exemplos, análise estática, servidor HTTP e SQLite funcionando."},
  {"p": "O que **não** existe: gerenciador de pacotes, LSP, debugger, VM otimizada e generics. Para um utilitário interno ou um script de dados, é viável. Para um sistema crítico com equipe grande, ainda não."},
  {"h2": "Como o desempenho se compara?"},
  {"p": "É um interpretador de árvore sem otimização, então mais lento que Python — que já é lento comparado a linguagens compiladas. Uma VM de bytecode está no [roadmap](/docs/roadmap), mas ninguém reclamou de desempenho ainda."},
  {"p": "Veja [Desempenho](/docs/faq/desempenho) para números e o que fazer a respeito."},
  {"h2": "Posso contribuir?"},
  {"p": "Sim — veja [Contribuir](/docs/contribuir). Os itens mais acessíveis do roadmap: verificação de exaustividade em `match`, contrato de trait no analisador, funções novas nos módulos `Arcane.*` e mais exercícios."},
  {"h2": "Qual a licença?"},
  {"p": "MIT."},
];

const headings = [{ id: 'e-uma-linguagem-de-verdade', text: "É uma linguagem de verdade?", level: 2 as const }, { id: 'por-que-nao-usar-python-direto', text: "Por que não usar Python direto?", level: 2 as const }, { id: 'por-que--em-vez-de', text: "Por que `:=` em vez de `=`?", level: 2 as const }, { id: 'por-que-yesno-em-vez-de-truefalse', text: "Por que `yes`/`no` em vez de `true`/`false`?", level: 2 as const }, { id: 'por-que--e-comentario-e-nao-divisao', text: "Por que `//` é comentário e não divisão?", level: 2 as const }, { id: 'preciso-anotar-os-tipos', text: "Preciso anotar os tipos?", level: 2 as const }, { id: 'da-para-usar-em-producao', text: "Dá para usar em produção?", level: 2 as const }, { id: 'como-o-desempenho-se-compara', text: "Como o desempenho se compara?", level: 2 as const }, { id: 'posso-contribuir', text: "Posso contribuir?", level: 2 as const }, { id: 'qual-a-licenca', text: "Qual a licença?", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Perguntas frequentes"}
      description={"As dúvidas mais comuns sobre a linguagem, seu escopo e suas escolhas."}
      href={"/docs/faq"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
