// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "40 · Metaprogramação",
  description: "1 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 40`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[258](#258-comptime-macros-dsl-e-plugin-do-check)", "**comptime, macros, DSL e plugin do check**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "258 · comptime, macros, DSL e plugin do check"},
  { code: `// A linguagem ja tinha decorador, metaclasse e augment — tudo em
// EXECUCAO. Esta e a outra metade: o que acontece antes de o programa
// rodar, e o que permite gerar codigo a partir de dado.

adopt Arcane.Macro as M
adopt Arcane.Dsl as D

// ── comptime: a conta feita uma vez, na carga ──
comptime QUADRADOS := [i * i cycle i in range(0, 6)]
comptime steady MAXIMO := 2 ** 10

assert QUADRADOS is [0, 1, 4, 9, 16, 25]
assert MAXIMO is 1024

comptime:
    action fatorial(n):
        yield 1 given n smaller_eq 1 otherwise n * fatorial(n - 1)

    TABELA := [fatorial(i) cycle i in range(0, 6)]

assert TABELA is [1, 1, 2, 6, 24, 120]

// a validacao estatica: se a tabela mudar, o check acusa antes de rodar
comptime:
    assert len(TABELA) is 6

// 'comptime' continua sendo nome comum fora da declaracao
comptime_qualquer := 3
assert comptime_qualquer is 3

// ── macro: a arvore como dado ──
action somar(a, b):
    yield a + b

arvore := M.arvore(somar)
assert arvore["tipo"] is "ActionDeclaration"
assert arvore["parametros"] is ["a", "b"]
assert arvore["corpo"][0]["tipo"] is "YieldStatement"

// citar: texto vira arvore; texto: arvore vira texto
citada := M.citar("x * 2 + 1")
assert citada["tipo"] is "BinaryOp"
assert M.texto(citada) is "x * 2 + 1"

// percorrer: cada no, uma vez
tipos := []

action anotar(nodo):
    tipos.append(nodo["tipo"])

M.percorrer(arvore, anotar)
assert len(tipos) bigger 3
assert "BinaryOp" in tipos

// reescrever: o corpo, trocado
action dobro(x):
    yield x * 2

action virar_soma(nodo):
    given nodo["tipo"] is "BinaryOp" and nodo["op"] is "*":
        yield M.citar("x + x")
    yield nodo

trocada := M.reescrever(dobro, virar_soma)
assert dobro(5) is 10
assert trocada(5) is 10  // corpo diferente, resultado igual

// gerar: uma acao a partir de texto
gerada := M.compilar("a * 10", "dez_vezes", ["a"])
assert gerada(4) is 40

// higiene: o nome gerado nao captura o de quem chamou
temporario := "do usuario"
corpo := M.citar("temporario + 1")
limpo := M.renomear(corpo, "temporario", M.nome_fresco("temporario"))
assert M.texto(limpo) isnt M.texto(corpo)

// macro de atributo: os campos geram os metodos
mark @M.derivar("texto", "igualdade", "vault")
blueprint Ponto:
    x := 1
    y := 2

a := spawn Ponto()
b := spawn Ponto()
assert $"{a}" is "Ponto(x=1, y=2)"
assert a is b
assert a.para_vault() is {"x": 1, "y": 2}

// ── DSL: uma linguagem pequena, propria ──
numero := D.mapear(D.numero(), lambda t => cast t as Float)
operador := D.ou([D.texto("+"), D.texto("-"), D.texto("*")])

action aplicar(partes):
    esquerda := partes[0]
    cycle par in partes[1]:
        given par[0] is "+":
            esquerda := esquerda + par[1]
        orif par[0] is "-":
            esquerda := esquerda - par[1]
        otherwise:
            esquerda := esquerda * par[1]
    yield esquerda

expressao := D.mapear(D.seq([numero, D.muitos(D.seq([operador, numero]))]), aplicar)

assert D.analisar(expressao, "2+3*4").valor() is 20.0
assert D.analisar(expressao, "10-4").valor() is 6.0

// a falha diz ONDE, e o que era esperado
ruim := D.analisar(D.numero(), "abc")
assert ruim.falhou()
assert ruim.erro()["posicao"] is 0
assert "numero" in ruim.erro()["esperado"]

// combinadores: alternativa, repeticao, opcional, separado
palavra := D.ou([D.texto("sim"), D.texto("nao")])
lista := D.muitos(D.seq([palavra, D.opcional(D.texto(","))]))
assert len(D.analisar(lista, "sim,nao,sim").valor()) is 3

nomes := D.separado_por(D.nome(), D.texto(","))
assert D.analisar(nomes, "ana,bia,caio").valor() is ["ana", "bia", "caio"]

out "258 ok"`, lang: 'df', title: `exercicios/40-metaprogramacao/258_comptime_e_macros.df` },
  {"p": "A linguagem já tinha decorador, metaclasse e `augment` — tudo em **execução**. Esta é a outra metade: o que acontece **antes** de o programa rodar, e o que permite gerar código a partir de dado."},
  {"h3": "comptime: a conta feita uma vez"},
  {"p": "`comptime` roda na **carga**, antes da primeira linha do programa, numa caixa sem E/S. O resultado vira constante."},
  {"p": "Se ele pudesse fazer E/S, \"tempo de compilação\" seria só \"mais cedo\" — por isso `out`, `adopt`, `thread` e `parallel` são recusados ali, com o motivo na mensagem."},
  {"p": "Três usos que pagam o recurso:"},
  {"list": ["**tabela de consulta** calculada uma vez;", "**constante derivada** (`2 ** 16`) escrita como conta, e não como"]},
  {"p": "número mágico;"},
  {"list": ["**validação estática**: um `assert` dentro de `comptime` é uma trava de"]},
  {"p": "build, e o `dataforge check` a executa (`comptime-falhou`)."},
  {"h3": "Macro: a árvore como dado"},
  {"p": "O decorador troca o **valor**; a macro troca o **corpo**."},
  {"p": "`M.arvore(acao)` devolve um vault comum — que percorre com `cycle`, casa com `match` e serializa em JSON, sem que nada disso conheça a classe do nó. `M.citar(texto)` faz o caminho inverso, e é a mesma árvore do arquivo: é isso que permite gerar código que **roda**."},
  {"p": "`M.transformar` devolve uma árvore **nova**. Uma macro que mutasse o que recebeu mudaria a ação de quem chamou."},
  {"p": "**Higiene é explícita**"},
  {"p": "Uma macro que gera um temporário chamado `temp` quebra quem já tinha um `temp`. `M.nome_fresco` e `M.renomear` existem para isso — e são explícitos, porque fazer higiene sozinho exigiria saber o que é \"de dentro\", e essa decisão é de quem escreve a macro."},
  {"p": "**Derivar**"},
  {"p": "`mark @M.derivar(\"texto\", \"igualdade\", \"vault\")` gera `__str__`, `__eq__` e `para_vault()` **a partir dos campos que já existem**. É a macro derivada, e roda na carga — não a cada chamada."},
  {"h3": "DSL externa"},
  {"p": "`Arcane.Dsl` são combinadores: `texto`, `numero`, `nome`, `seq`, `ou`, `muitos`, `opcional`, `separado_por`, `mapear`. `D.analisar` devolve um `Resultado` — texto de fora falha o tempo todo, e obrigar `monitor` em volta faria o caminho normal ser o do erro."},
  {"p": "A falha diz **posição**, o que era esperado e o trecho em volta: \"não deu certo\" não ajuda a consertar a linha 3 de um arquivo de configuração."},
  {"h3": "Plugin do check"},
  {"p": "Um `.df` que exporta `verificar(arvore, arquivo)` e devolve achados com `linha`, `coluna`, `codigo`, `mensagem`, `sugestao` e `severidade`. Rode com `--plugin=regras.df`, ou declare em `forge.toml`:"},
  { code: `[check]
plugins = ["regras.df"]`, lang: 'toml' },
  {"p": "O código aparece na mensagem, e `// df: permitir <codigo>` silencia a regra na linha — sem isso, quem discordasse de uma regra teria de desligar o plugin inteiro."},
  {"p": "Um plugin quebrado vira **diagnóstico**, e não traceback: quem roda o `check` quer o relatório do código dele."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/40-metaprogramacao/258_comptime_e_macros.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '258-comptime-macros-dsl-e-plugin-do-check', text: "258 · comptime, macros, DSL e plugin do check", level: 2 as const }, { id: 'comptime-a-conta-feita-uma-vez', text: "comptime: a conta feita uma vez", level: 3 as const }, { id: 'macro-a-arvore-como-dado', text: "Macro: a árvore como dado", level: 3 as const }, { id: 'dsl-externa', text: "DSL externa", level: 3 as const }, { id: 'plugin-do-check', text: "Plugin do check", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"40 · Metaprogramação"}
      description={"1 exercícios: ."}
      href={"/docs/exercicios/40-metaprogramacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
