// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_interno.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O caminho de compilação",
  description: "As seis fases que um arquivo .df atravessa, o comando que mostra cada uma — e a fase que não existe, dita com esse nome.",
};

const blocos: Bloco[] = [
  {"p": "Um `.df` não vai direto do texto ao resultado. Ele atravessa seis fases, e cada uma responde a uma pergunta diferente sobre o mesmo programa. `dataforge tokens` e `dataforge ast` mostravam a primeira e a terceira; as do meio não apareciam em lugar nenhum."},
  { code: `texto
  ↓  lexer.py            tokens, com linha e coluna
  ↓  parser.py           AST — 140 formas de no
  ↓  hir.py              HIR — a arvore depois do acucar
  ↓  typechecker.py      nomes, aridade, tipos, posse
  ↓  mir.py              MIR — bloco basico, aresta, laco, tratador
  ↓  compilador.py       LIR — a arvore vira fechamentos
  ↓  interpreter.py      executa`, lang: 'text', title: `As seis fases` },
  {"callout": {"tipo": "atencao", "titulo": "Não há fase de código de máquina, e este é o lugar de dizer isso", "texto": "Uma referência de linguagem compilada continua com LLVM IR, passes, registradores e linker. O DataForge é **interpretado**: o backend dele é o compilador de fechamentos (`compilador.py`), e a última fase é chamar fechamento Python. `dataforge ir --fase=lir` é onde isso fica visível — e uma fase chamada `assembly` que devolvesse texto plausível seria a pior coisa que esta documentação poderia ter."}},
  {"h2": "O comando"},
  { code: `dataforge ir app.df                # o caminho inteiro
dataforge ir app.df --fase=hir     # quanto acucar o arquivo usa
dataforge ir app.df --fase=mir     # o grafo de fluxo
dataforge ir app.df --fase=analises
dataforge ir app.df --fase=lir     # o que compilou, e o que recuou
dataforge ir app.df --fase=mir --acao=classificar
dataforge ir app.df --json         # as mesmas fases como dado`, lang: 'bash', title: `dataforge ir` },
  {"p": "Uma fase inventada é recusada **com a lista** — inclusive a que muita gente vai tentar primeiro:"},
  { code: `$ dataforge ir app.df --fase=llvm
Erro: fase 'llvm' nao existe.
  Fases: tokens, ast, hir, mir, analises, lir, tudo
  Nao ha fase de LLVM nem de codigo de maquina: o backend e o
  compilador de fechamentos.`, lang: 'bash', title: `A fase que não existe` },
  {"h2": "De dentro da linguagem"},
  {"p": "`Arcane.Compilador` entrega as mesmas fases como **dado**. É o que permite a um [plugin do `check`](/docs/metaprogramacao/plugins) perguntar coisas de **fluxo**, e não só de forma — e `Arcane.Macro` sozinho não alcança isso: ele para na árvore."},
  { code: `adopt Arcane.Compilador as K

fonte := "action f(n):\\n    given n:\\n        yield 1\\n    orif n is 0:\\n        yield 2\\n"

assert K.fases() is ["lexer", "parser", "hir", "mir", "analises",
                    "ssa", "otimizado", "lir"]
assert K.acucares(fonte) is {"orif-aninhado": 1}
assert K.corpos(fonte) is ["(programa)", "f"]
assert K.lir(fonte)["proporcao"] bigger 0`, lang: 'df' },
  {"table": {"head": ["Símbolo", "A fase"], "rows": [["`K.fases()`", "os nomes, na ordem"], ["`K.tokens(fonte)`", "lexer — um vault por token"], ["`K.arvore(fonte)`", "parser — a árvore como vault, igual ao `Arcane.Macro`"], ["`K.hir` · `K.acucares` · `K.resolucao`", "[HIR](/docs/compilador/hir)"], ["`K.mir` · `K.blocos` · `K.corpos`", "[MIR](/docs/compilador/mir)"], ["`K.alcance` · `K.constantes` · `K.escapam` · `K.vivas` · `K.talvez_nao_definidas`", "[as análises](/docs/compilador/analises)"], ["`K.lir(fonte)`", "o que virou fechamento, e o que recuou"], ["`K.texto(fonte, fase)`", "a fase escrita, igual ao `dataforge ir`"]]}},
  {"h2": "Onde o lexer e o parser já estavam documentados"},
  {"p": "As duas primeiras fases têm página própria desde antes: a [gramática formal](/docs/referencia/gramatica) em EBNF, as [palavras reservadas](/docs/referencia/palavras-reservadas) e a [arquitetura](/docs/referencia/arquitetura) do interpretador. O que estas páginas acrescentam é o meio do caminho."},
];

const headings = [{ id: 'o-comando', text: "O comando", level: 2 as const }, { id: 'de-dentro-da-linguagem', text: "De dentro da linguagem", level: 2 as const }, { id: 'onde-o-lexer-e-o-parser-ja-estavam-documentados', text: "Onde o lexer e o parser já estavam documentados", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O caminho de compilação"}
      description={"As seis fases que um arquivo .df atravessa, o comando que mostra cada uma — e a fase que não existe, dita com esse nome."}
      href={"/docs/compilador/pipeline"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
