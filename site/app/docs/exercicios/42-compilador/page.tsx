// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "42 · Dentro do compilador",
  description: "1 exercício: HIR, MIR e o que a análise de fluxo prova.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Por dentro da linguagem** · HIR, MIR e o que a análise de fluxo prova · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 42`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[260](#260-dentro-do-compilador-hir-mir-e-o-que-o-fluxo-prova)", "**dentro do compilador: HIR, MIR e o que o fluxo prova**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "260 · dentro do compilador: HIR, MIR e o que o fluxo prova"},
  { code: `// A linguagem ja tinha lexer, parser, AST, analisador e um compilador de
// fechamentos — e nenhuma forma de VER as representacoes do meio. Este
// exercicio abre as seis fases de dentro da propria linguagem.

adopt Arcane.Compilador as K

// ── as fases ──
assert K.fases() is ["lexer", "parser", "hir", "mir", "analises",
    "ssa", "otimizado", "lir"]

fonte := """
action classificar(n):
    given n bigger 10:
        yield "alto"
    orif n smaller 0:
        yield "negativo"
    otherwise:
        yield "baixo"

total := 0
cycle i in [1, 2, 3]:
    total += i
out classificar(total)
"""

// ── lexer: o token sabe onde nasceu ──
tokens := K.tokens(fonte)
assert len(tokens) bigger 30
assert tokens[0]["linha"] is 1
assert "tipo" in tokens[0] and "coluna" in tokens[0]

// ── parser: a arvore, como dado ──
arvore := K.arvore(fonte)
assert arvore["tipo"] is "Program"
assert arvore["corpo"][0]["tipo"] is "ActionDeclaration"

// ── HIR: o acucar que o arquivo usa ──
// 'orif' e uma corrente de given deitada; '+=' le o alvo e escreve nele
assert K.acucares(fonte) is {"orif-aninhado": 1, "composta-simples": 1}

// e no HIR o orif deixou de existir
de_fora := K.hir(fonte)["corpo"][0]["corpo"][0]
assert de_fora["tipo"] is "GivenBlock"
assert len(de_fora["orif_blocks"]) is 0
assert de_fora["otherwise_body"][0]["tipo"] is "GivenBlock"

// o que so PARECE acucar tem o motivo escrito ao lado
motivos := K.nao_e_acucar()
assert "CycleFromTo" in motivos  // 'range' materializa a lista
assert "MarkDecorator" in motivos  // decorador que devolve void nao troca
assert len(motivos["TernaryExpression"]) bigger 20

// ── resolucao: de onde vem cada nome ──
ligacoes := K.resolucao("fora := 1\\naction f(a):\\n    b := a + 1\\n    yield b + fora + sqrt(4)\\n")
f := [c cycle c in ligacoes given c["nome"] is "f"][0]
assert f["parametros"] is ["a"]
assert f["locais"] is ["b"]
assert f["livres"] is ["fora"]  // le e nao cria: vem de fora
assert f["embutidos"] is ["sqrt"]

// ── MIR: bloco basico e aresta ──
assert K.corpos(fonte) is ["(programa)", "classificar"]

topo := K.blocos(fonte, "(programa)")
// o laco tem uma aresta de volta — sem ela nao e laco
voltas := [b["id"] cycle b in topo
    given len([s cycle s in b["saidas"] given s["aresta"] is "volta"]) bigger 0]
assert len(voltas) is 1

// o 'given' abre dois ramos, e os dois tem rotulo
ramos := K.blocos(fonte, "classificar")
etiquetas := unique([s["aresta"] cycle b in ramos cycle s in b["saidas"]])
assert "sim" in etiquetas and "nao" in etiquetas

// o monitor liga o corpo ao tratador
com_erro := "monitor:\\n    x := 1\\nhandle Error as e:\\n    out e.message\\nensure:\\n    out 2\\n"
rotulos := [b["rotulo"] cycle b in K.blocos(com_erro, "(programa)")]
assert "tratador" in rotulos and "ensure" in rotulos

// ── alcance: o codigo que nao pode ser atingido ──
// os tres ramos encerram com yield, logo a juncao nao e alcancavel
vida := K.alcance(fonte)["classificar"]
assert vida["vivos"] smaller vida["total"]
assert len(vida["fora"]) bigger 0

// ── definida em todo caminho: o aviso que o check nao tinha ──
assert K.talvez_nao_definidas("given c:\\n    x := 1\\nout x\\n") is ["x"]

// com o 'otherwise' cobrindo, silencio
assert K.talvez_nao_definidas(
    "given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n") is []

// o laco conta como ramo: ele pode nao rodar nenhuma vez
assert K.talvez_nao_definidas("cycle x in xs:\\n    ultimo := x\\nout ultimo\\n") is ["ultimo"]

// e a analise CALA quando nao pode provar — cada silencio e um falso
// alarme que nao acontece
assert K.talvez_nao_definidas(
    "monitor:\\n    given c:\\n        x := 1\\n    out x\\nhandle Error:\\n    out 0\\n") is []

// ── propagacao de constante: a intersecao e o recurso ──
assert K.constantes("x := 2\\ny := x + 1\\nout y\\n", "(programa)") is {"x": 2, "y": 3}

// dois ramos que discordam nao deixam constante nenhuma
assert K.constantes("given c:\\n    x := 1\\notherwise:\\n    x := 2\\nout x\\n",
    "(programa)") is {}

// ── escapatoria: quem mais pode estar lendo ──
com_closure := "action f():\\n" +
"    preso := 1\\n" +
"    solto := 2\\n" +
"    ler := lambda => preso + 1\\n" +
"    yield ler()\\n"
fugas := K.escapam(com_closure, "f")
assert fugas["preso"] is "fechamento"
assert fugas["ler"] is "devolvido"
assert "solto" not in fugas  // vive e morre no quadro

// ── LIR: o que o compilador de fechamentos fez ──
// nao ha codigo de maquina: o backend e compilador.py, e o LIR diz
// quanto da arvore virou fechamento e o que recuou para a arvore
inventario := K.lir(fonte)
assert inventario["total"] is inventario["compiladas"] + inventario["recuadas"]
assert inventario["proporcao"] bigger 0 and inventario["proporcao"] smaller_eq 100
assert "por_no" in inventario

// o recuo DENTRO de um laco e o unico que aparece num perfil
quente := K.lir("cycle i in [1, 2]:\\n    out [x cycle x in [1]]\\n")
assert len(quente["quentes"]) bigger_eq 0

// ── a fase que nao existe ──
monitor:
    K.texto(fonte, "llvm")
    assert no
handle RuntimeError as e:
    assert "llvm" in e.message
    assert "backend" in e.message  // e diz qual e

out "260 ok"`, lang: 'df', title: `exercicios/42-compilador/260_pipeline_hir_mir.df` },
  {"p": "A linguagem já tinha lexer, parser, AST, analisador estático e um compilador de fechamentos. O que faltava era **ver** as representações do meio: `dataforge tokens` mostrava a primeira fase, `dataforge ast` a terceira, e as outras quatro não apareciam em lugar nenhum."},
  { code: `texto → lexer → AST → HIR → typechecker → MIR → LIR → executa`, lang: 'text' },
  {"p": "`dataforge ir <arquivo> --fase=…` mostra cada uma, e `Arcane.Compilador` as entrega como **dado** — o que permite a um plugin do `check` perguntar coisas de **fluxo**, e não só de forma."},
  {"h3": "HIR: o açúcar, e o que só parece"},
  {"p": "Cinco formas de escrita são abertas: a corrente de `orif` vira `given` aninhado, `x += 1` vira `x := x + 1` **quando o alvo é um nome**, `x not in xs` vira `not (x in xs)`, `perform` vira o laço com a primeira volta garantida, e `-5` vira o literal `-5` em vez de uma operação sobre `5`."},
  {"p": "**A prova não é a forma da árvore: é a saída.** Um desaçucaramento errado não levanta erro — ele muda o resultado. Por isso a garantia é medida rodando exercícios do repositório nas duas formas e comparando caractere por caractere."},
  {"p": "A outra lista vale mais: oito formas que **parecem** açúcar e não são, com o motivo ao lado. `cycle i from 0 to 3` não vira `cycle i in range(0, 4)` porque `range` **materializa** a lista, e um laço de um milhão de voltas criaria uma lista de um milhão de itens. `a ?? b` não vira ternário porque avaliaria `a` duas vezes. `mark @f` não vira `g := f(g)` porque um decorador que devolve `void` **não** substitui o alvo — e é isso que deixa `@Rota(\"/x\")` só anotar."},
  {"h3": "MIR: o grafo, e por que cada decisão"},
  {"p": "A árvore diz o que o programa **é**; o grafo diz por onde ele **passa**. Um corpo por ação, mais `(programa)` no topo, cada um com blocos básicos e arestas rotuladas: `sim`, `nao`, `volta`, `halt`, `skip`, `erro`, `point`, `default`, `defer`."},
  {"p": "Três decisões:"},
  {"p": "1. **O MIR sai do HIR**, e é isso que paga a normalização: sem ela, `orif` e `perform` seriam dois casos a mais no construtor de grafo — e um caso esquecido ali não dá erro, produz análise errada com cara de verdade. 2. **A aresta de erro sai da ENTRADA do `monitor`**, não de cada instrução. O `handle` vê o estado de **antes** do corpo, que é o pior caso honesto; uma aresta por instrução daria o mesmo resultado com um grafo três vezes maior. 3. **O que roda fora da ordem é opaco.** `thread`, `parallel`, `server` entram como **uma** instrução: abrir o corpo deles num grafo sequencial afirmaria uma ordem que não existe."},
  {"h3": "O aviso que o check não sabia dar"},
  { code: `given n bigger 10:
    rotulo := "alto"
yield rotulo          // e quando a condicao e falsa?`, lang: 'df' },
  {"p": "O analisador **registra** o nome do ramo, e isso está certo: um `given` compartilha o escopo, e é assim que se decide um valor em dois caminhos. O que faltava era contar por **quantos** caminhos ele passa — e essa pergunta só o grafo responde (`talvez-nao-definida`)."},
  {"p": "O laço conta como ramo pelo mesmo motivo: ele pode não rodar nenhuma vez."},
  {"p": "**Cada silêncio é um falso alarme que não acontece.** Ela cala quando o corpo tem `monitor` (o `handle` lê o que o corpo talvez não tenha atribuído, e isso é o uso normal), quando tem `defer`, quando há fechamento ou bloco opaco, e — o que só apareceu **medindo** — quando o nome existe **fora**: `:=` dentro de uma ação escreve o nome externo quando ele existe. Sem essa última regra, os nove contadores por fechamento do repositório seriam todos acusados."},
  {"h3": "Constante, e escapatória"},
  {"p": "A propagação de constante usa **interseção**: um nome que dois ramos escrevem com valores diferentes sai da tabela. É isso que a separa de uma varredura de texto."},
  {"p": "A escapatória responde \"o que mais alguém pode estar lendo?\" com quatro motivos: `devolvido`, `fechamento`, `concorrente`, `guardado`. Numa linguagem compilada ela decide o que vive na pilha; aqui o coletor do Python continua respondendo pela memória, mas a pergunta segue prática — um nome que escapa para uma `thread` é a metade de todo bug de concorrência."},
  {"h3": "LIR: o backend que existe"},
  {"p": "Não há código de máquina, e o módulo não finge. O backend do DataForge é `compilador.py`: a árvore vira fechamentos Python, uma vez. E essa descida é **parcial** — o que não está nas tabelas recua para o interpretador de árvore, e continua correto, só não fica mais rápido."},
  {"p": "O que não existia em lugar nenhum era saber **o que** recuou. O inventário diz, por classe de nó, e separa os recuos que acontecem **dentro de um laço** — os únicos em que a diferença aparece num perfil."},
  {"p": "A conta sai das tabelas do próprio `compilador.py`, e não de uma lista à parte: uma segunda lista divergiria no primeiro nó novo, e o relatório passaria a mentir com confiança."},
  {"h3": "O que NÃO existe"},
  {"list": ["**LLVM, registradores, linker**: não é lacuna, é o que a escolha de ser"]},
  {"p": "interpretado significa. O teto da técnica já está medido em ~6,5×."},
  {"list": ["**Otimização sobre o MIR**: ele é para **analisar**, não para"]},
  {"p": "reescrever."},
  {"list": ["**Tempo de vida nomeado** (`'a`): o coletor responde pela memória, e um"]},
  {"p": "`'a` sem nada para provar seria cerimônia."},
  {"list": ["**Pratt parser**: a precedência é a cascata de funções. Pratt paga"]},
  {"p": "quando a tabela de operadores é dinâmica, e aqui ela é fixa."},
  {"list": ["**Recuperação de erro dentro de um arquivo**: o primeiro erro de"]},
  {"p": "sintaxe encerra a leitura daquele arquivo (entre arquivos o `check` continua)."},
  {"list": ["**Prova formal** (SMT, refinamento provado): há contrato cobrado em"]},
  {"p": "execução e `--plugin=` para acoplar regra própria, e é onde isso para."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/42-compilador/260_pipeline_hir_mir.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '260-dentro-do-compilador-hir-mir-e-o-que-o-fluxo-prova', text: "260 · dentro do compilador: HIR, MIR e o que o fluxo prova", level: 2 as const }, { id: 'hir-o-acucar-e-o-que-so-parece', text: "HIR: o açúcar, e o que só parece", level: 3 as const }, { id: 'mir-o-grafo-e-por-que-cada-decisao', text: "MIR: o grafo, e por que cada decisão", level: 3 as const }, { id: 'o-aviso-que-o-check-nao-sabia-dar', text: "O aviso que o check não sabia dar", level: 3 as const }, { id: 'constante-e-escapatoria', text: "Constante, e escapatória", level: 3 as const }, { id: 'lir-o-backend-que-existe', text: "LIR: o backend que existe", level: 3 as const }, { id: 'o-que-nao-existe', text: "O que NÃO existe", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"42 · Dentro do compilador"}
      description={"1 exercício: HIR, MIR e o que a análise de fluxo prova."}
      href={"/docs/exercicios/42-compilador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
