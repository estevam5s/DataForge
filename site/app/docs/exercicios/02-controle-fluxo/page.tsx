// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "02 · Controle de fluxo",
  description: "12 exercícios: given/orif/otherwise, ternário, match e guardas.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 02`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[013](#013-condicional-given)", "**Condicional given**", "classifique um numero como positivo, negativo ou zero."], ["[014](#014-condicionais-aninhadas)", "**Condicionais aninhadas**", "converta uma nota de 0 a 10 em conceito A/B/C/D."], ["[015](#015-match-point-default)", "**match / point / default**", "traduza o codigo de um dia da semana para o nome."], ["[016](#016-laco-cycle-fromto)", "**Laco cycle from/to**", "some os numeros de 1 a 100."], ["[017](#017-laco-com-step)", "**Laco com step**", "liste os pares de 0 a 10 e faca uma contagem regressiva."], ["[018](#018-laco-cycle-in)", "**Laco cycle in**", "percorra uma lista e um vault."], ["[019](#019-laco-persist-while)", "**Laco persist (while)**", "calcule quantas vezes um numero pode ser dividido por 2."], ["[020](#020-laco-perform-do-while)", "**Laco perform (do-while)**", "garanta que o corpo execute ao menos uma vez."], ["[021](#021-halt-e-skip)", "**halt e skip**", "pule os multiplos de 3 e pare ao encontrar o primeiro maior que 10."], ["[022](#022-lacos-aninhados)", "**Lacos aninhados**", "imprima a tabuada de 1 a 3 e monte a matriz de produtos."], ["[023](#023-fizzbuzz)", "**FizzBuzz**", "para 1..15, diga Fizz, Buzz, FizzBuzz ou o proprio numero."], ["[024](#024-guard-como-pre-condicao)", "**guard como pre-condicao**", "use guard para sair cedo de uma acao com entrada invalida."]]}},
  {"h2": "013 · Condicional given"},
  {"p": "**Enunciado.** classifique um numero como positivo, negativo ou zero."},
  { code: `action classificar(n):
    given n bigger 0:
        yield "positivo"
    orif n smaller 0:
        yield "negativo"
    otherwise:
        yield "zero"

cycle n in [5, -3, 0]:
    out n, "->", classificar(n)

assert classificar(5) is "positivo", "positivo"
assert classificar(-3) is "negativo", "negativo"
assert classificar(0) is "zero", "zero"`, lang: 'df', title: `exercicios/02-controle-fluxo/013_given_simples.df` },
  {"h2": "014 · Condicionais aninhadas"},
  {"p": "**Enunciado.** converta uma nota de 0 a 10 em conceito A/B/C/D."},
  { code: `action conceito(nota):
    given nota bigger_eq 9:
        yield "A"
    orif nota bigger_eq 7:
        yield "B"
    orif nota bigger_eq 5:
        yield "C"
    otherwise:
        yield "D"

cycle n in [10, 8, 6, 2]:
    out n, "->", conceito(n)

assert conceito(10) is "A", "A"
assert conceito(8) is "B", "B"
assert conceito(6) is "C", "C"
assert conceito(2) is "D", "D"`, lang: 'df', title: `exercicios/02-controle-fluxo/014_given_aninhado.df` },
  {"h2": "015 · match / point / default"},
  {"p": "**Enunciado.** traduza o codigo de um dia da semana para o nome."},
  { code: `action dia(n):
    match n:
        point 1:
            yield "segunda"
        point 2:
            yield "terca"
        point 3:
            yield "quarta"
        default:
            yield "desconhecido"

cycle n in [1, 2, 3, 9]:
    out n, "->", dia(n)

assert dia(1) is "segunda", "1"
assert dia(3) is "quarta", "3"
assert dia(9) is "desconhecido", "default"`, lang: 'df', title: `exercicios/02-controle-fluxo/015_match.df` },
  {"h2": "016 · Laco cycle from/to"},
  {"p": "**Enunciado.** some os numeros de 1 a 100."},
  { code: `total := 0
cycle i from 1 to 100:
    total += i

out "soma de 1 a 100 =", total
assert total is 5050, "soma de Gauss"`, lang: 'df', title: `exercicios/02-controle-fluxo/016_cycle_from_to.df` },
  {"h2": "017 · Laco com step"},
  {"p": "**Enunciado.** liste os pares de 0 a 10 e faca uma contagem regressiva."},
  { code: `pares := []
cycle i from 0 to 10 step 2:
    pares.append(i)

regressiva := []
cycle i from 5 to 1 step -1:
    regressiva.append(i)

out "pares:      ", pares
out "regressiva: ", regressiva

assert pares is [0, 2, 4, 6, 8, 10], "pares"
assert regressiva is [5, 4, 3, 2, 1], "regressiva"`, lang: 'df', title: `exercicios/02-controle-fluxo/017_cycle_step.df` },
  {"h2": "018 · Laco cycle in"},
  {"p": "**Enunciado.** percorra uma lista e um vault."},
  { code: `frutas := ["maca", "uva", "pera"]
cycle f in frutas:
    out "fruta:", f

precos := {"maca": 3.5, "uva": 8.0}
cycle chave in precos.keys():
    out chave, "custa", precos[chave]

contagem := 0
cycle f in frutas:
    contagem += 1
assert contagem is 3, "percorreu 3 frutas"
assert len(precos.keys()) is 2, "duas chaves"`, lang: 'df', title: `exercicios/02-controle-fluxo/018_cycle_in.df` },
  {"h2": "019 · Laco persist (while)"},
  {"p": "**Enunciado.** calcule quantas vezes um numero pode ser dividido por 2."},
  { code: `n := 1024
divisoes := 0
persist n bigger 1:
    n := n ~/ 2
    divisoes += 1

out "1024 vira 1 apos", divisoes, "divisoes"
assert divisoes is 10, "log2(1024) = 10"`, lang: 'df', title: `exercicios/02-controle-fluxo/019_persist.df` },
  {"h2": "020 · Laco perform (do-while)"},
  {"p": "**Enunciado.** garanta que o corpo execute ao menos uma vez."},
  { code: `execucoes := 0
perform:
    execucoes += 1
persist no

out "executou", execucoes, "vez(es) mesmo com condicao falsa"
assert execucoes is 1, "do-while roda ao menos uma vez"

contagem := 0
i := 0
perform:
    i += 1
    contagem += i
persist i smaller 4
assert contagem is 10, "1+2+3+4"`, lang: 'df', title: `exercicios/02-controle-fluxo/020_perform.df` },
  {"h2": "021 · halt e skip"},
  {"p": "**Enunciado.** pule os multiplos de 3 e pare ao encontrar o primeiro maior que 10."},
  { code: `selecionados := []
cycle i from 1 to 100:
    given i % 3 is 0:
        skip
    given i bigger 10:
        halt
    selecionados.append(i)

out selecionados
assert selecionados is [1, 2, 4, 5, 7, 8, 10], "pulou multiplos de 3 e parou em 11"`, lang: 'df', title: `exercicios/02-controle-fluxo/021_halt_skip.df` },
  {"h2": "022 · Lacos aninhados"},
  {"p": "**Enunciado.** imprima a tabuada de 1 a 3 e monte a matriz de produtos."},
  { code: `matriz := []
cycle i from 1 to 3:
    linha := []
    cycle j from 1 to 3:
        linha.append(i * j)
    matriz.append(linha)
    out "tabuada do", i, ":", linha

assert matriz is [[1, 2, 3], [2, 4, 6], [3, 6, 9]], "matriz de produtos"
assert matriz[2][2] is 9, "3 x 3"`, lang: 'df', title: `exercicios/02-controle-fluxo/022_lacos_aninhados.df` },
  {"h2": "023 · FizzBuzz"},
  {"p": "**Enunciado.** para 1..15, diga Fizz, Buzz, FizzBuzz ou o proprio numero."},
  { code: `action fizzbuzz(n):
    given n % 15 is 0:
        yield "FizzBuzz"
    orif n % 3 is 0:
        yield "Fizz"
    orif n % 5 is 0:
        yield "Buzz"
    otherwise:
        yield str(n)

resultado := []
cycle i from 1 to 15:
    resultado.append(fizzbuzz(i))

out resultado.join(" ")
assert fizzbuzz(3) is "Fizz", "3"
assert fizzbuzz(5) is "Buzz", "5"
assert fizzbuzz(15) is "FizzBuzz", "15"
assert fizzbuzz(7) is "7", "7"
assert len(resultado) is 15, "15 itens"`, lang: 'df', title: `exercicios/02-controle-fluxo/023_fizzbuzz.df` },
  {"h2": "024 · guard como pre-condicao"},
  {"p": "**Enunciado.** use guard para sair cedo de uma acao com entrada invalida."},
  { code: `action raiz_segura(n):
    guard n bigger_eq 0 otherwise:
        out "  entrada negativa, devolvendo void"
    yield sqrt(n)

out raiz_segura(16)
out raiz_segura(-4)

assert raiz_segura(16) is 4.0, "raiz de 16"
assert raiz_segura(-4) is void, "guard interrompe a acao"

// guard com mensagem dispara erro
disparou := no
action exige_positivo(n):
    guard n bigger 0, "n precisa ser positivo"
    yield n
monitor:
    exige_positivo(-1)
handle e:
    disparou := yes
    out "  erro:", e
assert disparou is yes, "guard com mensagem dispara"`, lang: 'df', title: `exercicios/02-controle-fluxo/024_guard.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/02-controle-fluxo/013_given_simples.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '013-condicional-given', text: "013 · Condicional given", level: 2 as const }, { id: '014-condicionais-aninhadas', text: "014 · Condicionais aninhadas", level: 2 as const }, { id: '015-match-point-default', text: "015 · match / point / default", level: 2 as const }, { id: '016-laco-cycle-fromto', text: "016 · Laco cycle from/to", level: 2 as const }, { id: '017-laco-com-step', text: "017 · Laco com step", level: 2 as const }, { id: '018-laco-cycle-in', text: "018 · Laco cycle in", level: 2 as const }, { id: '019-laco-persist-while', text: "019 · Laco persist (while)", level: 2 as const }, { id: '020-laco-perform-do-while', text: "020 · Laco perform (do-while)", level: 2 as const }, { id: '021-halt-e-skip', text: "021 · halt e skip", level: 2 as const }, { id: '022-lacos-aninhados', text: "022 · Lacos aninhados", level: 2 as const }, { id: '023-fizzbuzz', text: "023 · FizzBuzz", level: 2 as const }, { id: '024-guard-como-pre-condicao', text: "024 · guard como pre-condicao", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"02 · Controle de fluxo"}
      description={"12 exercícios: given/orif/otherwise, ternário, match e guardas."}
      href={"/docs/exercicios/02-controle-fluxo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
