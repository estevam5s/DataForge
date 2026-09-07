import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Interpretador de expressões",
  description: "Lexer, parser e avaliador completos — escritos em DataForge.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `177_interpretador.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Text as Text

// Um interpretador completo: lexer, parser e avaliador.
// Suporta numeros, + - * /, parenteses e variaveis.

// ═══ TOKENS ═══

record Token:
    tipo: String
    valor: String

action tokenizar(fonte: String) -> Cluster:
    tokens := []
    i := 0
    persist i smaller len(fonte):
        c := fonte[i]
        given c is " ":
            i += 1
            skip
        given c.isdigit():
            numero := ""
            persist i smaller len(fonte) and (fonte[i].isdigit() or fonte[i] is "."):
                numero += fonte[i]
                i += 1
            tokens.append(Token("numero", numero))
            skip
        given c.isalpha() or c is "_":
            nome := ""
            persist i smaller len(fonte) and (fonte[i].isalnum() or fonte[i] is "_"):
                nome += fonte[i]
                i += 1
            tokens.append(Token("nome", nome))
            skip
        given c in "+-*/()":
            tokens.append(Token("simbolo", c))
            i += 1
            skip
        trigger $"caractere inesperado: '{c}' na posicao {i}"
    yield tokens

// ═══ PARSER: descida recursiva ═══
// expressao := termo (('+' | '-') termo)*
// termo     := fator (('*' | '/') fator)*
// fator     := numero | nome | '(' expressao ')' | '-' fator

action parsear(tokens: Cluster) -> Vault:
    pos := {"i": 0}

    action atual():
        given pos["i"] bigger_eq len(tokens):
            yield void
        yield tokens[pos["i"]]

    action consumir():
        t := atual()
        pos["i"] := pos["i"] + 1
        yield t

    action e_simbolo(s):
        t := atual()
        yield t isnt void and t.tipo is "simbolo" and t.valor is s

    action fator():
        given e_simbolo("-"):
            consumir()
            yield {"tipo": "neg", "de": fator()}
        given e_simbolo("("):
            consumir()
            interno := expressao()
            guard e_simbolo(")"), "esperava ')'"
            consumir()
            yield interno
        t := consumir()
        guard t isnt void, "expressao incompleta"
        match t.tipo:
            point "numero":
                yield {"tipo": "num", "valor": cast t.valor as Float}
            point "nome":
                yield {"tipo": "var", "nome": t.valor}
            default:
                trigger $"token inesperado: {t.valor}"

    action termo():
        no_ := fator()
        persist e_simbolo("*") or e_simbolo("/"):
            op := consumir().valor
            no_ := {"tipo": "bin", "op": op, "esq": no_, "dir": fator()}
        yield no_

    action expressao():
        no_ := termo()
        persist e_simbolo("+") or e_simbolo("-"):
            op := consumir().valor
            no_ := {"tipo": "bin", "op": op, "esq": no_, "dir": termo()}
        yield no_

    arvore := expressao()
    guard atual() is void, $"sobrou entrada apos a expressao"
    yield arvore

// ═══ AVALIADOR ═══

action avaliar(no_: Vault, ambiente: Vault) -> Number:
    match no_["tipo"]:
        point "num":
            yield no_["valor"]
        point "var":
            nome := no_["nome"]
            guard nome in ambiente, $"variavel indefinida: {nome}"
            yield ambiente[nome]
        point "neg":
            yield 0 - avaliar(no_["de"], ambiente)
        point "bin":
            e := avaliar(no_["esq"], ambiente)
            d := avaliar(no_["dir"], ambiente)
            match no_["op"]:
                point "+":
                    yield e + d
                point "-":
                    yield e - d
                point "*":
                    yield e * d
                point "/":
                    guard d isnt 0, "divisao por zero"
                    yield e / d
                default:
                    trigger $"operador desconhecido: {no_["op"]}"
        default:
            trigger "no desconhecido"

action calcular(fonte: String, ambiente: Vault := {}) -> Number:
    yield avaliar(parsear(tokenizar(fonte)), ambiente)

// ═══ DEMONSTRACAO ═══

out Text.box("Mini Interpretador")

out ""
out "── expressoes ──"
casos := [
    ["2 + 3", 5.0],
    ["2 + 3 * 4", 14.0],
    ["(2 + 3) * 4", 20.0],
    ["10 / 4", 2.5],
    ["-5 + 3", -2.0],
    ["2 * (3 + 4) - 1", 13.0],
    ["1 + 2 + 3 + 4", 10.0]
]

cycle caso in casos:
    fonte, esperado := caso
    obtido := calcular(fonte)
    out $"  {fonte.pad_end(20)} = {obtido}"
    assert obtido is esperado, $"resultado de {fonte}"

// ── com variaveis ──
out ""
out "── com variaveis ──"
ambiente := {"x": 10.0, "y": 4.0, "taxa": 1.15}

cycle e in ["x + y", "x * y", "(x + y) * taxa", "x / y - 1"]:
    out $"  {e.pad_end(20)} = {round(calcular(e, ambiente), 4)}"

assert calcular("x + y", ambiente) is 14.0, "soma de variaveis"
assert round(calcular("(x + y) * taxa", ambiente), 2) is 16.1, "com taxa"

// ── erros ──
out ""
out "── erros tratados ──"
cycle ruim in ["2 +", "(1 + 2", "1 / 0", "z + 1", "2 @ 3", "1 2"]:
    monitor:
        calcular(ruim, ambiente)
        out $"  {ruim.pad_end(12)} -> nao deveria passar"
    handle erro:
        out $"  {ruim.pad_end(12)} -> {erro.message}"

// ── a arvore ──
out ""
out "── arvore de '2 + 3 * 4' ──"
arvore := parsear(tokenizar("2 + 3 * 4"))
out $"  raiz: {arvore["op"]}"
out $"  esquerda: {arvore["esq"]["valor"]}"
out $"  direita: {arvore["dir"]["op"]} de {arvore["dir"]["esq"]["valor"]} e {arvore["dir"]["dir"]["valor"]}"
assert arvore["op"] is "+", "soma na raiz"
assert arvore["dir"]["op"] is "*", "multiplicacao mais funda: precedencia correta"

out ""
out "  a multiplicacao ficou mais funda na arvore — precedencia respeitada"`, title: `177_interpretador.df` },
  {"h2": "Por que este projeto"},
  {"p": "Uma linguagem capaz de implementar outra linguagem é uma linguagem completa. Este é o mesmo desenho do interpretador do próprio DataForge, em escala reduzida."},
  {"h2": "As três fases"},
  { code: `"2 + 3 * 4"
     ↓  tokenizar
[num:2] [sim:+] [num:3] [sim:*] [num:4]
     ↓  parsear
        (+)
       /   \\
      2    (*)
          /   \\
         3     4
     ↓  avaliar
        14.0`, lang: 'text' },
  {"h2": "A precedência está na estrutura"},
  {"p": "A gramática vira funções, uma por nível: `expressao` chama `termo`, que chama `fator`. Como `termo` é chamado mais fundo, a multiplicação fica mais fundo na árvore — e o avaliador, que desce recursivamente, a calcula primeiro."},
  {"p": "Não há tabela de precedência: ela emerge da forma como as funções se chamam."},
  {"h2": "Erros em cada fase"},
  {"table": {"head": ["Entrada", "Fase", "Mensagem"], "rows": [["`2 @ 3`", "lexer", "caractere inesperado"], ["`2 +`", "parser", "expressão incompleta"], ["`(1 + 2`", "parser", "esperava `)`"], ["`z + 1`", "avaliador", "variável indefinida"], ["`1 / 0`", "avaliador", "divisão por zero"]]}},
  {"p": "Cada fase valida o que é da sua competência. Isso é o que produz mensagens específicas em vez de \"erro de sintaxe\"."},
];

const headings = [{ id: 'por-que-este-projeto', text: "Por que este projeto", level: 2 as const }, { id: 'as-tres-fases', text: "As três fases", level: 2 as const }, { id: 'a-precedencia-esta-na-estrutura', text: "A precedência está na estrutura", level: 2 as const }, { id: 'erros-em-cada-fase', text: "Erros em cada fase", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Interpretador de expressões"}
      description={"Lexer, parser e avaliador completos — escritos em DataForge."}
      href={"/docs/receitas/interpretador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
