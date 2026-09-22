// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Interpretador de expressões",
  description: "Lexer, parser recursivo descendente e avaliador — uma calculadora com variáveis.",
};

const blocos: Bloco[] = [
  {"p": "Escrever um interpretador pequeno é a forma mais rápida de entender o que este repositório faz em escala: texto vira token, token vira árvore, árvore vira valor. As três fases ficam separadas pelo mesmo motivo que no DataForge — um erro de sintaxe tem de ser reportado **antes** de qualquer conta."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["lexer", "texto → tokens, com a coluna de cada um"], ["parser recursivo descendente", "a precedência vem da ordem das funções"], ["árvore como vault", "a mesma forma que a `Arcane.Macro` usa"], ["ambiente de variáveis", "`x := 2` e depois `x * 3`"]]}},
  {"h2": "Estrutura"},
  { code: `calc/
  src/
    lexer.df
    parser.df     expr := termo (('+'|'-') termo)*
    avaliar.df
    repl.df
  tests/`, lang: 'text' },
  { code: `[project]
name = "calc"
version = "0.1.0"
description = "Calculadora com variáveis"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `action tokens(texto):
    saida := []
    i := 0
    persist i smaller len(texto):
        c := texto[i]
        given c is " ":
            i += 1
            skip
        given isdigit(c) or c is ".":
            j := i
            persist j smaller len(texto) and (isdigit(texto[j]) or texto[j] is "."):
                j += 1
            saida.append({"tipo": "num", "valor": float(texto[i:j]), "col": i})
            i := j
            skip
        given isalpha(c):
            j := i
            persist j smaller len(texto) and isalnum(texto[j]):
                j += 1
            saida.append({"tipo": "nome", "valor": texto[i:j], "col": i})
            i := j
            skip
        given c in ["+", "-", "*", "/", "(", ")", "="]:
            saida.append({"tipo": c, "valor": c, "col": i})
            i += 1
            skip
        trigger $"caractere inesperado '{c}' na coluna {i + 1}"
    saida.append({"tipo": "fim", "valor": "", "col": len(texto)})
    yield saida

// O parser guarda a posicao num vault: e o estado que as funcoes dividem.
action parse(texto):
    p := {"t": tokens(texto), "i": 0}
    arvore := atribuicao(p)
    given p["t"][p["i"]]["tipo"] is not "fim":
        trigger $"sobrou '{p['t'][p['i']]['valor']}' na coluna {p['t'][p['i']]['col'] + 1}"
    yield arvore

action olhar(p):
    yield p["t"][p["i"]]

action consumir(p):
    t := p["t"][p["i"]]
    p["i"] += 1
    yield t

action atribuicao(p):
    given olhar(p)["tipo"] is "nome" and p["t"][p["i"] + 1]["tipo"] is "=":
        nome := consumir(p)["valor"]
        consumir(p)
        yield {"no": "atr", "nome": nome, "valor": expr(p)}
    yield expr(p)

action expr(p):
    esq := termo(p)
    persist olhar(p)["tipo"] in ["+", "-"]:
        op := consumir(p)["tipo"]
        esq := {"no": "bin", "op": op, "esq": esq, "dir": termo(p)}
    yield esq

action termo(p):
    esq := fator(p)
    persist olhar(p)["tipo"] in ["*", "/"]:
        op := consumir(p)["tipo"]
        esq := {"no": "bin", "op": op, "esq": esq, "dir": fator(p)}
    yield esq

action fator(p):
    t := consumir(p)
    match t["tipo"]:
        point "num":
            yield {"no": "num", "valor": t["valor"]}
        point "nome":
            yield {"no": "var", "nome": t["valor"]}
        point "-":
            yield {"no": "neg", "valor": fator(p)}
        point "(":
            dentro := expr(p)
            given consumir(p)["tipo"] is not ")":
                trigger "faltou fechar o parentese"
            yield dentro
        default:
            trigger $"esperava um numero na coluna {t['col'] + 1}"

action avaliar(nodo, amb):
    match nodo["no"]:
        point "num":
            yield nodo["valor"]
        point "var":
            given nodo["nome"] not in amb:
                trigger $"'{nodo['nome']}' nao foi definida"
            yield amb[nodo["nome"]]
        point "neg":
            yield -avaliar(nodo["valor"], amb)
        point "atr":
            amb[nodo["nome"]] := avaliar(nodo["valor"], amb)
            yield amb[nodo["nome"]]
        point "bin":
            a := avaliar(nodo["esq"], amb)
            b := avaliar(nodo["dir"], amb)
            match nodo["op"]:
                point "+":
                    yield a + b
                point "-":
                    yield a - b
                point "*":
                    yield a * b
                point "/":
                    given b is 0:
                        trigger "divisao por zero"
                    yield a / b

amb := {}
action rodar(linha):
    yield avaliar(parse(linha), amb)

assert rodar("1 + 2 * 3") is 7.0
assert rodar("(1 + 2) * 3") is 9.0
assert rodar("x = 4") is 4.0
assert rodar("-x * 2 + 10") is 2.0

monitor:
    rodar("2 * (3 + ")
    assert no
handle Error as e:
    out e.message
    assert "coluna" in e.message`, lang: 'df', title: `src/parser.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/parser as P

crucible "precedencia":
    trial "multiplicacao antes da soma":
        expect P.avaliar(P.parse("2 + 3 * 4"), {}) is 14.0`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["uma função por nível de precedência", "`2 + 3 * 4` dá 20"], ["a coluna em todo token", "o erro diz *“sintaxe inválida”* sem dizer onde"], ["o parser confere que **tudo** foi consumido", "`2 3` avalia para 2 e o 3 some calado"], ["parse e avaliação separados", "um erro de sintaxe no fim da linha acontece depois da atribuição do começo"]]}},
  {"h2": "Para ir além"},
  {"list": ["Compare com o parser de verdade: [Arquitetura](/docs/referencia/arquitetura).", "A mesma coisa em combinadores: [Arcane.Dsl](/docs/biblioteca/dsl).", "Receita completa: [Receitas → interpretador](/docs/receitas/interpretador)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Interpretador de expressões"}
      description={"Lexer, parser recursivo descendente e avaliador — uma calculadora com variáveis."}
      href={"/docs/projetos/interpretador"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
