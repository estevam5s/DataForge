// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "05 · Ações",
  description: "14 exercícios: parâmetros, padrões, retorno, closures e recursão.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 05`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[049](#049-acao-basica)", "**Acao basica**", "escreva uma acao que soma e outra sem retorno."], ["[050](#050-parametros-com-valor-padrao)", "**Parametros com valor padrao**", "permita chamar a acao com menos argumentos."], ["[051](#051-argumentos-nomeados)", "**Argumentos nomeados**", "passe argumentos fora de ordem usando o nome."], ["[052](#052-verificacao-de-aridade)", "**Verificacao de aridade**", "comprove que argumentos faltando ou sobrando disparam erro."], ["[053](#053-acoes-tipadas)", "**Acoes tipadas**", "anote parametros e retorno e comprove a checagem."], ["[054](#054-recursao)", "**Recursao**", "fatorial, fibonacci e soma de digitos."], ["[055](#055-limite-de-recursao)", "**Limite de recursao**", "comprove que recursao infinita vira erro controlado."], ["[056](#056-acoes-de-alta-ordem)", "**Acoes de alta ordem**", "passe acoes como argumento e devolva acoes."], ["[057](#057-closures)", "**Closures**", "crie um contador que preserva estado entre chamadas."], ["[058](#058-lambdas)", "**Lambdas**", "use acoes anonimas em variaveis e como argumento."], ["[059](#059-decoradores-com-mark)", "**Decoradores com mark**", "envolva uma acao com log sem alterar seu corpo."], ["[060](#060-defer)", "**defer**", "agende limpeza que roda ao sair da acao."], ["[061](#061-escopo-e-shadow)", "**Escopo e shadow**", "entenda quando uma acao le e quando cria uma variavel."], ["[062](#062-memoizacao-manual)", "**Memoizacao manual**", "acelere fibonacci guardando resultados ja calculados."]]}},
  {"h2": "049 · Acao basica"},
  {"p": "**Enunciado.** escreva uma acao que soma e outra sem retorno."},
  { code: `action somar(a, b):
    yield a + b

action saudar(nome):
    out "Ola,", nome

out somar(2, 3)
saudar("Ana")

assert somar(2, 3) is 5, "soma"
assert saudar("Ana") is void, "acao sem yield devolve void"`, lang: 'df', title: `exercicios/05-acoes/049_acao_basica.df` },
  {"h2": "050 · Parametros com valor padrao"},
  {"p": "**Enunciado.** permita chamar a acao com menos argumentos."},
  { code: `action criar_usuario(nome, papel := "leitor", ativo := yes):
    yield {"nome": nome, "papel": papel, "ativo": ativo}

out criar_usuario("Ana")
out criar_usuario("Bruno", "admin")

assert criar_usuario("Ana")["papel"] is "leitor", "padrao aplicado"
assert criar_usuario("Bruno", "admin")["papel"] is "admin", "padrao sobrescrito"
assert criar_usuario("Carla", "editor", no)["ativo"] is no, "terceiro argumento"`, lang: 'df', title: `exercicios/05-acoes/050_parametros_padrao.df` },
  {"h2": "051 · Argumentos nomeados"},
  {"p": "**Enunciado.** passe argumentos fora de ordem usando o nome."},
  { code: `action retangulo(largura := 1, altura := 1):
    yield largura * altura

out retangulo(altura := 5, largura := 3)
assert retangulo(altura := 5, largura := 3) is 15, "nomeados fora de ordem"
assert retangulo(largura := 4) is 4, "so um nomeado"
assert retangulo() is 1, "todos padrao"`, lang: 'df', title: `exercicios/05-acoes/051_argumentos_nomeados.df` },
  {"h2": "052 · Verificacao de aridade"},
  {"p": "**Enunciado.** comprove que argumentos faltando ou sobrando disparam erro."},
  { code: `action dividir(a, b):
    yield a / b

faltando := no
monitor:
    dividir(10)
handle e:
    faltando := yes
    out "faltando:", e

sobrando := no
monitor:
    dividir(1, 2, 3)
handle e:
    sobrando := yes
    out "sobrando:", e

assert faltando is yes, "argumento faltando dispara"
assert sobrando is yes, "argumento sobrando dispara"
assert dividir(10, 4) is 2.5, "chamada correta"`, lang: 'df', title: `exercicios/05-acoes/052_aridade.df` },
  {"h2": "053 · Acoes tipadas"},
  {"p": "**Enunciado.** anote parametros e retorno e comprove a checagem."},
  { code: `action area_circulo(raio: Number) -> Float:
    yield 3.14159 * raio ** 2

out round(area_circulo(2), 4)
assert round(area_circulo(2), 5) is 12.56636, "area"

erro := no
monitor:
    area_circulo("dois")
handle e:
    erro := yes
    out "erro esperado:", e
assert erro is yes, "parametro tipado rejeita String"`, lang: 'df', title: `exercicios/05-acoes/053_tipos_em_acoes.df` },
  {"h2": "054 · Recursao"},
  {"p": "**Enunciado.** fatorial, fibonacci e soma de digitos."},
  { code: `action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)

action soma_digitos(n):
    given n smaller 10:
        yield n
    yield n % 10 + soma_digitos(n ~/ 10)

out fatorial(6), fib(10), soma_digitos(9875)

assert fatorial(6) is 720, "fatorial"
assert fib(10) is 55, "fibonacci"
assert soma_digitos(9875) is 29, "soma de digitos"`, lang: 'df', title: `exercicios/05-acoes/054_recursao.df` },
  {"h2": "055 · Limite de recursao"},
  {"p": "**Enunciado.** comprove que recursao infinita vira erro controlado."},
  { code: `action infinita(n):
    yield infinita(n + 1)

estourou := no
monitor:
    infinita(1)
handle e:
    estourou := yes
    out "erro controlado:", e

assert estourou is yes, "recursao infinita e detectada"

action contar(n):
    given n smaller_eq 0:
        yield 0
    yield 1 + contar(n - 1)
assert contar(500) is 500, "recursao profunda legitima funciona"
out "recursao de 500 niveis ok"`, lang: 'df', title: `exercicios/05-acoes/055_recursao_profunda.df` },
  {"h2": "056 · Acoes de alta ordem"},
  {"p": "**Enunciado.** passe acoes como argumento e devolva acoes."},
  { code: `action aplicar_duas_vezes(fn, valor):
    yield fn(fn(valor))

action dobro(x):
    yield x * 2

action fabrica_somador(n):
    action somador(x):
        yield x + n
    yield somador

out aplicar_duas_vezes(dobro, 5)
soma10 := fabrica_somador(10)
out soma10(5)

assert aplicar_duas_vezes(dobro, 5) is 20, "aplicada duas vezes"
assert soma10(5) is 15, "acao devolvida"
assert fabrica_somador(3)(4) is 7, "chamada encadeada"`, lang: 'df', title: `exercicios/05-acoes/056_acoes_de_alta_ordem.df` },
  {"h2": "057 · Closures"},
  {"p": "**Enunciado.** crie um contador que preserva estado entre chamadas."},
  { code: `action criar_contador(inicio := 0):
    estado := {"valor": inicio}
    action proximo():
        estado["valor"] := estado["valor"] + 1
        yield estado["valor"]
    yield proximo

c1 := criar_contador()
c2 := criar_contador(100)

out c1(), c1(), c1()
out c2(), c2()

assert c1() is 4, "c1 continuou de 3"
assert c2() is 103, "c2 tem estado proprio"`, lang: 'df', title: `exercicios/05-acoes/057_closures.df` },
  {"h2": "058 · Lambdas"},
  {"p": "**Enunciado.** use acoes anonimas em variaveis e como argumento."},
  { code: `quadrado := lambda x: x * x
soma := lambda a, b => a + b
constante := lambda: 42

out quadrado(7), soma(3, 4), constante()

assert quadrado(7) is 49, "lambda de um parametro"
assert soma(3, 4) is 7, "lambda com =>"
assert constante() is 42, "lambda sem parametro"

nums := [1, 2, 3, 4, 5]
assert nums.map(lambda n: n * 10) is [10, 20, 30, 40, 50], "map com lambda"
assert nums.filter(lambda n: n % 2 is 1) is [1, 3, 5], "filter com lambda"
assert nums.reduce(lambda a, b: a + b, 0) is 15, "reduce com lambda"
out nums.map(lambda n: n * 10)`, lang: 'df', title: `exercicios/05-acoes/058_lambdas.df` },
  {"h2": "059 · Decoradores com mark"},
  {"p": "**Enunciado.** envolva uma acao com log sem alterar seu corpo."},
  { code: `registro := []

action com_log(fn):
    action envolvida(x):
        registro.append("chamada com " + str(x))
        yield fn(x)
    yield envolvida

mark @com_log
action triplo(x):
    yield x * 3

out triplo(5)
out triplo(2)
out registro

assert triplo(4) is 12, "a acao decorada continua correta"
assert len(registro) is 3, "o decorador registrou 3 chamadas"
assert registro[0] is "chamada com 5", "primeiro registro"`, lang: 'df', title: `exercicios/05-acoes/059_decoradores.df` },
  {"h2": "060 · defer"},
  {"p": "**Enunciado.** agende limpeza que roda ao sair da acao."},
  { code: `ordem := []

action com_recurso():
    defer:
        ordem.append("fechou recurso")
    ordem.append("abriu recurso")
    ordem.append("usou recurso")
    yield "pronto"

resultado := com_recurso()
out resultado
out ordem

assert resultado is "pronto", "retorno normal"
assert ordem is ["abriu recurso", "usou recurso", "fechou recurso"], "defer roda por ultimo"`, lang: 'df', title: `exercicios/05-acoes/060_defer.df` },
  {"h2": "061 · Escopo e shadow"},
  {"p": "**Enunciado.** entenda quando uma acao le e quando cria uma variavel."},
  { code: `global_x := 10

action le_global():
    yield global_x

action sombreia():
    shadow global_x := 99
    yield global_x

out le_global(), sombreia(), global_x

assert le_global() is 10, "le do escopo externo"
assert sombreia() is 99, "shadow cria uma copia local"
assert global_x is 10, "o valor externo nao mudou"`, lang: 'df', title: `exercicios/05-acoes/061_escopo.df` },
  {"h2": "062 · Memoizacao manual"},
  {"p": "**Enunciado.** acelere fibonacci guardando resultados ja calculados."},
  { code: `cache := {}
chamadas := {"n": 0}

action fib_memo(n):
    chamadas["n"] := chamadas["n"] + 1
    given n smaller 2:
        yield n
    given cache.has(str(n)):
        yield cache[str(n)]
    valor := fib_memo(n - 1) + fib_memo(n - 2)
    cache[str(n)] := valor
    yield valor

out "fib(30) =", fib_memo(30)
out "chamadas:", chamadas["n"]

assert fib_memo(30) is 832040, "fib(30)"
assert chamadas["n"] smaller 100, "memoizacao evita explosao de chamadas"`, lang: 'df', title: `exercicios/05-acoes/062_memoizacao.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/05-acoes/049_acao_basica.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '049-acao-basica', text: "049 · Acao basica", level: 2 as const }, { id: '050-parametros-com-valor-padrao', text: "050 · Parametros com valor padrao", level: 2 as const }, { id: '051-argumentos-nomeados', text: "051 · Argumentos nomeados", level: 2 as const }, { id: '052-verificacao-de-aridade', text: "052 · Verificacao de aridade", level: 2 as const }, { id: '053-acoes-tipadas', text: "053 · Acoes tipadas", level: 2 as const }, { id: '054-recursao', text: "054 · Recursao", level: 2 as const }, { id: '055-limite-de-recursao', text: "055 · Limite de recursao", level: 2 as const }, { id: '056-acoes-de-alta-ordem', text: "056 · Acoes de alta ordem", level: 2 as const }, { id: '057-closures', text: "057 · Closures", level: 2 as const }, { id: '058-lambdas', text: "058 · Lambdas", level: 2 as const }, { id: '059-decoradores-com-mark', text: "059 · Decoradores com mark", level: 2 as const }, { id: '060-defer', text: "060 · defer", level: 2 as const }, { id: '061-escopo-e-shadow', text: "061 · Escopo e shadow", level: 2 as const }, { id: '062-memoizacao-manual', text: "062 · Memoizacao manual", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"05 · Ações"}
      description={"14 exercícios: parâmetros, padrões, retorno, closures e recursão."}
      href={"/docs/exercicios/05-acoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
