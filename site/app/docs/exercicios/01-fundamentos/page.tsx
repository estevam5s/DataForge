// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "01 · Fundamentos",
  description: "12 exercícios: tipos, operadores, precedência, conversão e anotações.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 01`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[001](#001-ola-mundo)", "**Ola, mundo**", "imprima uma saudacao e o nome da linguagem em duas linhas."], ["[002](#002-variaveis)", "**Variaveis**", "declare uma variavel de cada tipo primitivo e imprima cada uma."], ["[003](#003-constantes-com-steady)", "**Constantes com steady**", "declare constantes e comprove que reatribuir dispara erro."], ["[004](#004-operadores-aritmeticos)", "**Operadores aritmeticos**", "use +, -, *, /, %, ** e a divisao inteira ~/."], ["[005](#005-precedencia-de-operadores)", "**Precedencia de operadores**", "comprove a ordem de avaliacao e a associatividade de **."], ["[006](#006-comparacoes)", "**Comparacoes**", "use as palavras-chave e os simbolos equivalentes."], ["[007](#007-operadores-logicos)", "**Operadores logicos**", "monte uma tabela verdade com and, or e not."], ["[008](#008-comparacao-encadeada)", "**Comparacao encadeada**", "verifique se um valor esta dentro de um intervalo em uma unica expressao."], ["[009](#009-atribuicao-composta)", "**Atribuicao composta**", "use +=, -=, *=, /= e %= para transformar um saldo."], ["[010](#010-typeof-e-cast)", "**typeof e cast**", "descubra o tipo de cada valor e converta entre tipos."], ["[011](#011-anotacoes-de-tipo)", "**Anotacoes de tipo**", "declare variaveis tipadas e comprove que o tipo errado dispara erro."], ["[012](#012-interpolacao-e-formatacao-de-saida)", "**Interpolacao e formatacao de saida**", "monte uma linha de relatorio combinando texto e numeros."]]}},
  {"h2": "001 · Ola, mundo"},
  {"p": "**Enunciado.** imprima uma saudacao e o nome da linguagem em duas linhas."},
  { code: `out "Ola, mundo!"
out "Bem-vindo ao DataForge."

assert 1 is 1, "o programa deve rodar ate o fim"`, lang: 'df', title: `exercicios/01-fundamentos/001_ola_mundo.df` },
  {"h2": "002 · Variaveis"},
  {"p": "**Enunciado.** declare uma variavel de cada tipo primitivo e imprima cada uma."},
  { code: `inteiro := 42
decimal := 3.14
texto := "DataForge"
verdadeiro := yes
falso := no
nada := void

out inteiro, decimal, texto, verdadeiro, falso, nada

assert inteiro is 42, "inteiro"
assert decimal is 3.14, "decimal"
assert texto is "DataForge", "texto"
assert verdadeiro is yes, "booleano verdadeiro"
assert falso is no, "booleano falso"
assert nada is void, "void"`, lang: 'df', title: `exercicios/01-fundamentos/002_variaveis.df` },
  {"h2": "003 · Constantes com steady"},
  {"p": "**Enunciado.** declare constantes e comprove que reatribuir dispara erro."},
  { code: `steady PI := 3.14159
steady APP := "DataForge"

out PI, APP

reatribuiu := no
monitor:
    PI := 0
    reatribuiu := yes
handle e:
    out "Erro esperado:", e

assert reatribuiu is no, "steady nao pode ser reatribuida"`, lang: 'df', title: `exercicios/01-fundamentos/003_constantes.df` },
  {"h2": "004 · Operadores aritmeticos"},
  {"p": "**Enunciado.** use +, -, *, /, %, ** e a divisao inteira ~/."},
  { code: `a := 17
b := 5

out "soma       ", a + b
out "subtracao  ", a - b
out "produto    ", a * b
out "divisao    ", a / b
out "resto      ", a % b
out "potencia   ", a ** 2
out "div inteira", a ~/ b

assert a + b is 22, "soma"
assert a - b is 12, "subtracao"
assert a * b is 85, "produto"
assert a / b is 3.4, "divisao"
assert a % b is 2, "resto"
assert a ** 2 is 289, "potencia"
assert a ~/ b is 3, "divisao inteira"`, lang: 'df', title: `exercicios/01-fundamentos/004_aritmetica.df` },
  {"h2": "005 · Precedencia de operadores"},
  {"p": "**Enunciado.** comprove a ordem de avaliacao e a associatividade de **."},
  { code: `out 2 + 3 * 4
out(2 + 3) * 4
out 2 ** 3 ** 2
out -2 ** 2

assert 2 + 3 * 4 is 14, "multiplicacao antes da soma"
assert(2 + 3) * 4 is 20, "parenteses primeiro"
assert 2 ** 3 ** 2 is 512, "potencia associa a direita"
assert -2 ** 2 is -4, "o sinal aplica depois da potencia"`, lang: 'df', title: `exercicios/01-fundamentos/005_precedencia.df` },
  {"h2": "006 · Comparacoes"},
  {"p": "**Enunciado.** use as palavras-chave e os simbolos equivalentes."},
  { code: `a := 10
b := 3

out a is 10, a isnt b, a bigger b, a smaller b
out a bigger_eq 10, a smaller_eq 9
out a > b, a < b, a >= 10, a <= 9

assert(a is 10) is yes, "is"
assert(a isnt b) is yes, "isnt"
assert(a bigger b) is(a > b), "bigger equivale a >"
assert(a smaller b) is(a < b), "smaller equivale a <"
assert(a bigger_eq 10) is(a >= 10), "bigger_eq equivale a >="
assert(a smaller_eq 9) is(a <= 9), "smaller_eq equivale a <="`, lang: 'df', title: `exercicios/01-fundamentos/006_comparacoes.df` },
  {"h2": "007 · Operadores logicos"},
  {"p": "**Enunciado.** monte uma tabela verdade com and, or e not."},
  { code: `out "p     q     and   or    not p"
cycle p in [yes, no]:
    cycle q in [yes, no]:
        out str(p).pad_end(6) + str(q).pad_end(6) + str(p and q).pad_end(6) + str(p or q).pad_end(6) + str(not p)

assert(yes and no) is no, "and"
assert(yes or no) is yes, "or"
assert(not yes) is no, "not"`, lang: 'df', title: `exercicios/01-fundamentos/007_logica.df` },
  {"h2": "008 · Comparacao encadeada"},
  {"p": "**Enunciado.** verifique se um valor esta dentro de um intervalo em uma unica expressao."},
  { code: `nota := 7.5

dentro := 0 <= nota <= 10
out "nota", nota, "esta no intervalo [0, 10]?", dentro

assert dentro is yes, "7.5 esta no intervalo"
assert(0 <= 11 <= 10) is no, "11 esta fora"
assert(1 smaller 5 smaller 10) is yes, "encadeamento com palavras-chave"`, lang: 'df', title: `exercicios/01-fundamentos/008_comparacao_encadeada.df` },
  {"h2": "009 · Atribuicao composta"},
  {"p": "**Enunciado.** use +=, -=, *=, /= e %= para transformar um saldo."},
  { code: `saldo := 100
saldo += 50
assert saldo is 150, "apos +="
saldo -= 30
assert saldo is 120, "apos -="
saldo *= 2
assert saldo is 240, "apos *="
saldo /= 4
assert saldo is 60.0, "apos /="
resto := 17
resto %= 5
assert resto is 2, "apos %="

out "saldo final:", saldo
out "resto:", resto`, lang: 'df', title: `exercicios/01-fundamentos/009_atribuicao_composta.df` },
  {"h2": "010 · typeof e cast"},
  {"p": "**Enunciado.** descubra o tipo de cada valor e converta entre tipos."},
  { code: `out typeof(1), typeof(1.0), typeof("a"), typeof(yes), typeof([1]), typeof({"k": 1}), typeof(void)

assert typeof(1) is "Integer", "Integer"
assert typeof(1.0) is "Float", "Float"
assert typeof("a") is "String", "String"
assert typeof(yes) is "Boolean", "Boolean"
assert typeof([1]) is "Cluster", "Cluster"
assert typeof({"k": 1}) is "Vault", "Vault"
assert typeof(void) is "Void", "Void"

assert cast "42" as Integer is 42, "String para Integer"
assert cast 42 as String is "42", "Integer para String"
assert cast 3.9 as Integer is 3, "Float para Integer trunca"
assert cast "3.5" as Float is 3.5, "String para Float"

out "conversoes ok"`, lang: 'df', title: `exercicios/01-fundamentos/010_tipos_e_conversao.df` },
  {"h2": "011 · Anotacoes de tipo"},
  {"p": "**Enunciado.** declare variaveis tipadas e comprove que o tipo errado dispara erro."},
  { code: `idade: Integer := 30
nome: String := "Ana"
altura: Float := 1.72
ativo: Boolean := yes
tags: Cluster := ["a", "b"]

out idade, nome, altura, ativo, tags

falhou := no
monitor:
    peso: Integer := "setenta"
handle e:
    falhou := yes
    out "Erro esperado:", e

assert falhou is yes, "atribuir String a Integer deve falhar"`, lang: 'df', title: `exercicios/01-fundamentos/011_anotacoes_de_tipo.df` },
  {"h2": "012 · Interpolacao e formatacao de saida"},
  {"p": "**Enunciado.** monte uma linha de relatorio combinando texto e numeros."},
  { code: `produto := "Teclado"
preco := 199.9
quantidade := 3
total := preco * quantidade

linha := produto + " x" + str(quantidade) + " = R$ " + str(round(total, 2))
out linha

assert linha is "Teclado x3 = R$ 599.7", "linha formatada"
assert round(total, 2) is 599.7, "total"`, lang: 'df', title: `exercicios/01-fundamentos/012_entrada_de_dados.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/01-fundamentos/001_ola_mundo.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '001-ola-mundo', text: "001 · Ola, mundo", level: 2 as const }, { id: '002-variaveis', text: "002 · Variaveis", level: 2 as const }, { id: '003-constantes-com-steady', text: "003 · Constantes com steady", level: 2 as const }, { id: '004-operadores-aritmeticos', text: "004 · Operadores aritmeticos", level: 2 as const }, { id: '005-precedencia-de-operadores', text: "005 · Precedencia de operadores", level: 2 as const }, { id: '006-comparacoes', text: "006 · Comparacoes", level: 2 as const }, { id: '007-operadores-logicos', text: "007 · Operadores logicos", level: 2 as const }, { id: '008-comparacao-encadeada', text: "008 · Comparacao encadeada", level: 2 as const }, { id: '009-atribuicao-composta', text: "009 · Atribuicao composta", level: 2 as const }, { id: '010-typeof-e-cast', text: "010 · typeof e cast", level: 2 as const }, { id: '011-anotacoes-de-tipo', text: "011 · Anotacoes de tipo", level: 2 as const }, { id: '012-interpolacao-e-formatacao-de-saida', text: "012 · Interpolacao e formatacao de saida", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"01 · Fundamentos"}
      description={"12 exercícios: tipos, operadores, precedência, conversão e anotações."}
      href={"/docs/exercicios/01-fundamentos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
