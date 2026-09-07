import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "13 · Desestruturação",
  description: "6 exercícios: `...resto`, spread, compreensões e interpolação.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 13`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["133", "**Desestruturacao de listas**", "extraia varios valores de uma lista numa unica linha."], ["134", "**Resto e spread**", "colete o que sobra com ...resto e expanda colecoes com ..."], ["135", "**Desestruturar records e vaults**", "extraia campos nomeados de um record ou de um dicionario."], ["136", "**Compreensao de listas**", "construa listas transformando e filtrando numa unica expressao."], ["137", "**Compreensao de vaults**", "construa dicionarios com a mesma sintaxe, produzindo chave e valor."], ["138", "**Interpolacao de strings**", "monte textos com valores embutidos, sem concatenacao manual."]]}},
  {"h2": "133 · Desestruturacao de listas"},
  {"p": "Extraia varios valores de uma lista numa unica linha."},
  { code: `// Exercicio 133 — Desestruturacao de listas
// Enunciado: extraia varios valores de uma lista numa unica linha.

// Forma basica: um nome para cada posicao
a, b := [1, 2]
out a, b
assert a is 1 and b is 2, "dois valores"

x, y, z := [10, 20, 30]
assert x + y + z is 60, "tres valores"

// Troca sem variavel temporaria
p := "primeiro"
q := "segundo"
p, q := q, p
out p, q
assert p is "segundo", "troca"

// Quantidade errada e erro, nao silencio
erro := no
monitor:
    m, n := [1, 2, 3]
handle e:
    erro := yes
    out e.message
assert erro is yes, "3 valores nao cabem em 2 nomes"

// Desestruturar dentro de um laco
pares := [[1, "um"], [2, "dois"], [3, "tres"]]
cycle par in pares:
    numero, palavra := par
    out $"{numero} = {palavra}"

// Retornar varios valores de uma acao
action divide_com_resto(a, b):
    yield [a ~/ b, a % b]

quociente, resto := divide_com_resto(17, 5)
out $"17 / 5 = {quociente} resto {resto}"
assert quociente is 3 and resto is 2, "divisao com resto"
`, title: `133_desestruturar_listas.df` },
  {"h2": "134 · Resto e spread"},
  {"p": "Colete o que sobra com ...resto e expanda colecoes com ..."},
  { code: `// Exercicio 134 — Resto e spread
// Enunciado: colete o que sobra com ...resto e expanda colecoes com ...

// ...resto captura o que sobrou
primeiro, ...outros := [1, 2, 3, 4, 5]
out primeiro, outros
assert primeiro is 1, "cabeca"
assert outros is [2, 3, 4, 5], "cauda"

// O resto pode estar no meio
inicio, ...meio, fim := [1, 2, 3, 4, 5]
out inicio, meio, fim
assert meio is [2, 3, 4], "o meio"
assert fim is 5, "o ultimo"

// Resto vazio e valido
so_um, ...nada := [9]
assert nada is [], "resto pode ser vazio"

// Spread expande na construcao
a := [1, 2]
b := [3, 4]
juntos := [...a, ...b, 5]
out juntos
assert juntos is [1, 2, 3, 4, 5], "concatenacao com spread"

// Spread em vaults: o ultimo vence
padrao := {"tema": "claro", "fonte": 14}
usuario := {"tema": "escuro"}
final := {...padrao, ...usuario}
out final
assert final is {"tema": "escuro", "fonte": 14}, "usuario sobrescreve padrao"

// Spread em chamadas
action somar_tres(a, b, c):
    yield a + b + c

args := [10, 20, 30]
out somar_tres(...args)
assert somar_tres(...args) is 60, "argumentos expandidos"

// Copia rasa: o novo nao e o mesmo objeto
original := [1, 2, 3]
copia := [...original]
copia.append(4)
out original, copia
assert original is [1, 2, 3], "o original nao mudou"
assert copia is [1, 2, 3, 4], "a copia mudou"
`, title: `134_resto_e_spread.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 4 exercícios deste módulo estão em `exercicios/13-desestruturacao/`. Cada um tem um `.md` ao lado com a explicação completa."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '133--desestruturacao-de-listas', text: "133 · Desestruturacao de listas", level: 2 as const }, { id: '134--resto-e-spread', text: "134 · Resto e spread", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"13 · Desestruturação"}
      description={"6 exercícios: `...resto`, spread, compreensões e interpolação."}
      href={"/exercicios/13-desestruturacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
