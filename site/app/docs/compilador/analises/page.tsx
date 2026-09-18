// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_interno.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O que o fluxo prova",
  description: "Alcance, vivacidade, definição em todo caminho, propagação de constante e escapatória — e o aviso novo que sai da terceira.",
};

const blocos: Bloco[] = [
  {"p": "Cinco análises sobre o grafo. Uma delas virou diagnóstico do `check`, porque era a única pergunta que ele ainda não sabia responder."},
  {"table": {"head": ["Análise", "Responde", "Direção"], "rows": [["`alcance`", "este bloco pode ser atingido?", "para frente, união"], ["`vivas`", "este valor ainda vai ser lido?", "para trás, união"], ["`talvez_nao_definidas`", "todo caminho até aqui definiu este nome?", "para frente, **interseção**"], ["`constantes`", "todo caminho concorda com este valor?", "para frente, interseção"], ["`escapam`", "quem mais pode estar lendo este local?", "estrutural"]]}},
  {"h2": "O aviso novo: `talvez-nao-definida`"},
  { code: `action classificar(n):
    given n bigger 10:
        rotulo := "alto"
    yield rotulo          // e quando a condicao e falsa?`, lang: 'df', title: `O que o check passava` },
  {"p": "O analisador **registra** o nome do ramo, e isso está certo: um `given` [compartilha o escopo](/docs/fundamentos/escopo), e é assim que se decide um valor em dois caminhos. O que faltava era contar por **quantos** caminhos ele passa — e essa pergunta só o grafo responde."},
  { code: `$ dataforge check app.df
aviso[talvez-nao-definida]: 'rotulo' may not be defined here: some path
                            to this line does not assign it
  --> app.df:4:11
  dica: Give 'rotulo' a value before the branch, or add the 'otherwise'
        that covers the other path`, lang: 'bash' },
  {"p": "O laço conta como ramo pelo mesmo motivo — ele pode não rodar nenhuma vez:"},
  { code: `adopt Arcane.Compilador as K

// o 'otherwise' cobre: silencio
assert K.talvez_nao_definidas(
    "given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n") is []

// so um ramo: acusa
assert K.talvez_nao_definidas("given c:\\n    x := 1\\nout x\\n") is ["x"]

// o laco pode nao rodar
assert K.talvez_nao_definidas(
    "cycle x in xs:\\n    ultimo := x\\nout ultimo\\n") is ["ultimo"]`, lang: 'df' },
  {"h3": "O que a faz calar"},
  {"p": "Cada silêncio é um falso alarme que não acontece — e um deles só apareceu **medindo** o repositório."},
  {"table": {"head": ["Cala quando", "Porque"], "rows": [["o corpo tem `monitor`", "o `handle` lê o que o corpo talvez não tenha atribuído, e isso é o uso normal"], ["o corpo tem `defer`", "ele roda na saída da ação, fora da ordem do grafo"], ["há fechamento no corpo", "um `lambda` pode ligar o nome depois, e o grafo não vê quando ele roda"], ["há bloco opaco (`thread`, `parallel`)", "a ordem é outra"], ["o nome existe **fora**", "`:=` dentro de uma ação escreve o nome externo quando ele existe — **medido**, e sem esta regra os nove contadores por fechamento do repositório seriam acusados"], ["o nome não é escrito neste corpo", "então é global, embutido ou erro — e isso o `check` já responde"]]}},
  {"callout": {"tipo": "atencao", "titulo": "É aviso, e não erro", "texto": "O caminho que não define pode ser o que nunca acontece, e só quem escreveu sabe. Como toda regra, dá para silenciar de propósito: `// df: permitir talvez-nao-definida`."}},
  {"h2": "Propagação de constante"},
  {"p": "Uma atribuição que o grafo prova única. É a interseção que separa esta análise de uma varredura de texto: um nome que dois ramos escrevem com valores diferentes **sai** da tabela."},
  { code: `adopt Arcane.Compilador as K

assert K.constantes("x := 2\\ny := x + 1\\nout y\\n", "(programa)") is {"x": 2, "y": 3}

// dois ramos discordam: nao ha constante
assert K.constantes("given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n",
                    "(programa)") is {}`, lang: 'df' },
  {"h2": "Escapatória"},
  {"p": "Quais locais saem do quadro, e por qual motivo. Numa linguagem compilada é o primeiro passo da alocação em pilha; aqui ela não move nada de lugar — o coletor do Python continua respondendo por isso — mas responde uma pergunta prática: **o que mais alguém pode estar lendo?** Um nome que escapa para uma `thread` é a metade de todo bug de concorrência."},
  { code: `adopt Arcane.Compilador as K

fonte := "action f():\\n    preso := 1\\n    solto := 2\\n" +
         "    ler := lambda => preso + 1\\n    yield ler()\\n"

fugas := K.escapam(fonte, "f")
assert fugas["preso"] is "fechamento"      // a closure o le
assert fugas["ler"] is "devolvido"         // sai da acao
assert "solto" not in fugas                // vive e morre no quadro`, lang: 'df' },
  {"table": {"head": ["Motivo", "O que aconteceu"], "rows": [["`devolvido`", "sai da ação por `yield`"], ["`fechamento`", "um `lambda` ou uma ação aninhada o lê"], ["`concorrente`", "um `thread` ou `parallel` o lê"], ["`guardado`", "vai para dentro de um objeto ou coleção"]]}},
  {"h2": "Vivacidade, e o LIR"},
  {"p": "`vivas` diz, na entrada de cada bloco, quais nomes ainda serão lidos. Numa linguagem compilada é a base da alocação de registradores; aqui a pergunta continua útil na hora de olhar um corpo grande."},
  {"p": "E o [LIR](/docs/compilador/pipeline) fecha o caminho com a informação que não existia em lugar nenhum: **o que o compilador de fechamentos compilou, e o que recuou** para o interpretador de árvore."},
  { code: `$ dataforge ir app.df --fase=lir
  42 de 48 nos viraram fechamento (88%)
  6 recuaram para o interpretador de arvore

  no                          compila   recua
   AssertStatement                  0       3
   ListComprehension                0       2

  1 recuo(s) DENTRO de laco — e onde a diferenca aparece num perfil:
   ListComprehension — linha(s) 31`, lang: 'bash' },
  {"p": "O recuo **dentro de um laço** é o único em que a diferença aparece num perfil, e por isso ele é listado em separado. A conta sai das tabelas do próprio `compilador.py`, e não de uma lista à parte: uma segunda lista divergiria no primeiro nó novo, e o relatório passaria a mentir com confiança."},
];

const headings = [{ id: 'o-aviso-novo-talvez-nao-definida', text: "O aviso novo: `talvez-nao-definida`", level: 2 as const }, { id: 'o-que-a-faz-calar', text: "O que a faz calar", level: 3 as const }, { id: 'propagacao-de-constante', text: "Propagação de constante", level: 2 as const }, { id: 'escapatoria', text: "Escapatória", level: 2 as const }, { id: 'vivacidade-e-o-lir', text: "Vivacidade, e o LIR", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O que o fluxo prova"}
      description={"Alcance, vivacidade, definição em todo caminho, propagação de constante e escapatória — e o aviso novo que sai da terceira."}
      href={"/docs/compilador/analises"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
