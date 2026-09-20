// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "09 · Módulos",
  description: "12 exercícios: adopt, relay, seleção e apelidos.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 09`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[099](#099-adopt-de-um-modulo-local)", "**adopt de um modulo local**", "importe um arquivo .df vizinho e use suas acoes."], ["[100](#100-import-inexistente)", "**Import inexistente**", "comprove que importar um modulo que nao existe dispara erro."], ["[101](#101-arcanemath)", "**Arcane.Math**", "use funcoes matematicas da biblioteca padrao."], ["[102](#102-estatistica-descritiva)", "**Estatistica descritiva**", "calcule medidas de posicao e dispersao."], ["[103](#103-arcaneanalytics)", "**Arcane.Analytics**", "explore correlacao, percentis e outliers."], ["[104](#104-regressao-linear)", "**Regressao linear**", "ajuste uma reta e faca previsoes."], ["[105](#105-dados-tabulares)", "**Dados tabulares**", "agrupe e resuma registros com Arcane.Analytics."], ["[106](#106-arcaneio)", "**Arcane.IO**", "escreva, leia e apague um arquivo temporario."], ["[107](#107-json)", "**JSON**", "serialize e desserialize estruturas."], ["[108](#108-arcanedatabase)", "**Arcane.Database**", "crie uma tabela em memoria, insira e consulte."], ["[109](#109-arcanetext)", "**Arcane.Text**", "formate um relatorio em caixa e tabela."], ["[110](#110-arcanetest)", "**Arcane.Test**", "escreva asserts de biblioteca para uma funcao."]]}},
  {"h2": "099 · adopt de um modulo local"},
  {"p": "**Enunciado.** importe um arquivo .df vizinho e use suas acoes."},
  { code: `adopt geometria as geo

out "PI       =", geo.PI
out "circulo  =", round(geo.area_circulo(2), 4)
out "retangulo=", geo.area_retangulo(3, 4)

assert round(geo.area_circulo(1), 5) is 3.14159, "area do circulo"
assert geo.area_retangulo(3, 4) is 12, "area do retangulo"
assert round(geo.perimetro_circulo(1), 5) is 6.28319, "perimetro"`, lang: 'df', title: `exercicios/09-modulos/099_adopt_local.df` },
  {"h2": "100 · Import inexistente"},
  {"p": "**Enunciado.** comprove que importar um modulo que nao existe dispara erro."},
  { code: `falhou := no
monitor:
    adopt Arcane.NaoExiste as inexistente
    out inexistente
handle e:
    falhou := yes
    out "erro esperado:", e.type

assert falhou is yes, "modulo inexistente dispara ImportError"

adopt Arcane.Math as M
assert M.sqrt(9) is 3.0, "modulo valido funciona"
out "Math.sqrt(9) =", M.sqrt(9)`, lang: 'df', title: `exercicios/09-modulos/100_adopt_erro.df` },
  {"h2": "101 · Arcane.Math"},
  {"p": "**Enunciado.** use funcoes matematicas da biblioteca padrao."},
  { code: `adopt Arcane.Math as Math

out "sqrt(16)  =", Math.sqrt(16)
out "PI        =", round(Math.PI, 5)
out "fatorial5 =", Math.factorial(5)
out "primo(97) =", Math.is_prime(97)
out "fib(12)   =", Math.fibonacci(12)
out "mdc(48,18)=", Math.gcd(48, 18)

assert Math.sqrt(16) is 4.0, "sqrt"
assert Math.factorial(5) is 120, "fatorial"
assert Math.is_prime(97) is yes, "primo"
assert Math.gcd(48, 18) is 6, "mdc"
assert Math.lcm(4, 6) is 12, "mmc"
assert Math.clamp(15, 0, 10) is 10, "clamp"`, lang: 'df', title: `exercicios/09-modulos/101_math.df` },
  {"h2": "102 · Estatistica descritiva"},
  {"p": "**Enunciado.** calcule medidas de posicao e dispersao."},
  { code: `adopt Arcane.Math as Math

amostra := [12, 15, 11, 18, 20, 15, 14, 19, 16, 15]

out "media   ", round(Math.mean(amostra), 2)
out "mediana ", Math.median(amostra)
out "desvio  ", round(Math.stdev(amostra), 4)
out "variancia", round(Math.variance(amostra), 4)

assert Math.mean(amostra) is 15.5, "media"
assert Math.median(amostra) is 15.0, "mediana"
assert Math.min(amostra) is 11, "minimo"
assert Math.max(amostra) is 20, "maximo"
assert round(Math.stdev(amostra), 2) is 2.88, "desvio padrao"`, lang: 'df', title: `exercicios/09-modulos/102_estatistica.df` },
  {"h2": "103 · Arcane.Analytics"},
  {"p": "**Enunciado.** explore correlacao, percentis e outliers."},
  { code: `adopt Arcane.Analytics as An

x := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y := [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

out "correlacao:", round(An.correlation(x, y), 4)
out "percentil 50:", An.percentile(x, 50)
out "quartis:", An.quartiles(x)

com_outlier := [10, 11, 12, 11, 10, 200]
out "outliers:", An.outliers(com_outlier)

assert round(An.correlation(x, y), 4) is 1.0, "correlacao perfeita"
assert An.percentile(x, 50) is 5.5, "mediana via percentil"
assert len(An.outliers(com_outlier)) bigger 0, "detectou outlier"`, lang: 'df', title: `exercicios/09-modulos/103_analytics.df` },
  {"h2": "104 · Regressao linear"},
  {"p": "**Enunciado.** ajuste uma reta e faca previsoes."},
  { code: `adopt Arcane.Analytics as An

x := [1, 2, 3, 4, 5]
y := [3, 5, 7, 9, 11]

modelo := An.linear_regression(x, y)
out "modelo:", modelo

previsto := An.predict_linear(modelo, 6)
out "previsao para x=6:", previsto

assert round(modelo["slope"], 4) is 2.0, "inclinacao"
assert round(modelo["intercept"], 4) is 1.0, "intercepto"
assert round(previsto, 4) is 13.0, "previsao"
assert round(An.r_squared(x, y), 4) is 1.0, "ajuste perfeito"`, lang: 'df', title: `exercicios/09-modulos/104_regressao.df` },
  {"h2": "105 · Dados tabulares"},
  {"p": "**Enunciado.** agrupe e resuma registros com Arcane.Analytics."},
  { code: `adopt Arcane.Analytics as An

registros := [
    {"setor": "TI", "salario": 8000},
    {"setor": "RH", "salario": 5000},
    {"setor": "TI", "salario": 9500},
    {"setor": "RH", "salario": 5500},
    {"setor": "TI", "salario": 7000}
]

grupos := An.group_by(registros, "setor")
out "setores:", grupos.keys()

cycle setor in grupos.keys():
    salarios := grupos[setor] >> morph r: r["salario"]
    out "  " + setor.pad_end(4) + "n=" + str(len(salarios)) + " media=" + str(round(mean(salarios), 2))

assert len(grupos.keys()) is 2, "dois setores"
assert len(grupos["TI"]) is 3, "3 registros de TI"

contagem := An.value_counts(registros >> morph r: r["setor"])
out "contagem:", contagem
assert contagem["TI"] is 3, "TI aparece 3x"`, lang: 'df', title: `exercicios/09-modulos/105_dados_tabulares.df` },
  {"h2": "106 · Arcane.IO"},
  {"p": "**Enunciado.** escreva, leia e apague um arquivo temporario."},
  { code: `adopt Arcane.IO as IO

caminho := "_exercicio_106.txt"
IO.write(caminho, "linha 1\\nlinha 2\\nlinha 3")

assert IO.exists(caminho) is yes, "arquivo criado"

conteudo := IO.read(caminho)
linhas := conteudo.lines()
out "linhas lidas:", len(linhas)
out linhas

assert len(linhas) is 3, "tres linhas"
assert linhas[0] is "linha 1", "primeira linha"

IO.delete(caminho)
assert IO.exists(caminho) is no, "arquivo removido"
out "arquivo temporario removido"`, lang: 'df', title: `exercicios/09-modulos/106_io_arquivos.df` },
  {"h2": "107 · JSON"},
  {"p": "**Enunciado.** serialize e desserialize estruturas."},
  { code: `original := {"nome": "Ana", "tags": ["a", "b"], "ativo": yes, "nota": 9.5}

texto := to_json(original)
out texto

volta := from_json(texto)
out volta

assert typeof(texto) is "String", "to_json devolve String"
assert volta["nome"] is "Ana", "nome preservado"
assert volta["tags"] is ["a", "b"], "lista preservada"
assert volta["nota"] is 9.5, "float preservado"`, lang: 'df', title: `exercicios/09-modulos/107_json.df` },
  {"h2": "108 · Arcane.Database"},
  {"p": "**Enunciado.** crie uma tabela em memoria, insira e consulte."},
  { code: `adopt Arcane.Database as DB

conn := DB.memory()
DB.execute(conn, "CREATE TABLE alunos (id INTEGER PRIMARY KEY, nome TEXT, nota REAL)")
DB.execute(conn, "INSERT INTO alunos (nome, nota) VALUES ('Ana', 9.5)")
DB.execute(conn, "INSERT INTO alunos (nome, nota) VALUES ('Bruno', 7.0)")
DB.execute(conn, "INSERT INTO alunos (nome, nota) VALUES ('Carla', 8.25)")

todos := DB.query(conn, "SELECT nome, nota FROM alunos ORDER BY nota DESC")
cycle linha in todos:
    out "  " + str(linha["nome"]).pad_end(8) + str(linha["nota"])

assert len(todos) is 3, "tres alunos"
assert todos[0]["nome"] is "Ana", "melhor nota primeiro"

aprovados := DB.query(conn, "SELECT COUNT(*) AS total FROM alunos WHERE nota >= 8")
assert aprovados[0]["total"] is 2, "dois aprovados"
out "aprovados:", aprovados[0]["total"]

DB.close(conn)`, lang: 'df', title: `exercicios/09-modulos/108_database.df` },
  {"h2": "109 · Arcane.Text"},
  {"p": "**Enunciado.** formate um relatorio em caixa e tabela."},
  { code: `adopt Arcane.Text as Text

out Text.box("Relatorio Mensal")

cabecalho := ["Produto", "Qtd", "Valor"]
linhas := [
    ["Mouse", "12", "960.00"],
    ["Teclado", "5", "1000.00"]
]
out Text.table(cabecalho, linhas)

assert Text.word_count("um dois tres") is 3, "word_count"
assert Text.kebab_case("MinhaClasseLegal") is "minha-classe-legal", "kebab_case"
assert Text.pascal_case("minha_classe") is "MinhaClasse", "pascal_case"
assert Text.remove_accents("coracao") is "coracao", "remove_accents"
assert Text.number_format(1234567.891, 2) is "1,234,567.89", "number_format"
out Text.number_format(1234567.891, 2)`, lang: 'df', title: `exercicios/09-modulos/109_texto_avancado.df` },
  {"h2": "110 · Arcane.Test"},
  {"p": "**Enunciado.** escreva asserts de biblioteca para uma funcao."},
  { code: `adopt Arcane.Test as Test

action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

Test.assert_eq(fatorial(0), 1, "fatorial de 0")
Test.assert_eq(fatorial(5), 120, "fatorial de 5")
Test.assert_true(fatorial(3) bigger fatorial(2), "cresce")
Test.assert_type(fatorial(4), "Integer", "devolve Integer")
Test.assert_between(fatorial(4), 20, 30, "24 esta no intervalo")

out "todas as verificacoes de Arcane.Test passaram"
assert fatorial(6) is 720, "verificacao final"`, lang: 'df', title: `exercicios/09-modulos/110_testes.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/09-modulos/099_adopt_local.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '099-adopt-de-um-modulo-local', text: "099 · adopt de um modulo local", level: 2 as const }, { id: '100-import-inexistente', text: "100 · Import inexistente", level: 2 as const }, { id: '101-arcanemath', text: "101 · Arcane.Math", level: 2 as const }, { id: '102-estatistica-descritiva', text: "102 · Estatistica descritiva", level: 2 as const }, { id: '103-arcaneanalytics', text: "103 · Arcane.Analytics", level: 2 as const }, { id: '104-regressao-linear', text: "104 · Regressao linear", level: 2 as const }, { id: '105-dados-tabulares', text: "105 · Dados tabulares", level: 2 as const }, { id: '106-arcaneio', text: "106 · Arcane.IO", level: 2 as const }, { id: '107-json', text: "107 · JSON", level: 2 as const }, { id: '108-arcanedatabase', text: "108 · Arcane.Database", level: 2 as const }, { id: '109-arcanetext', text: "109 · Arcane.Text", level: 2 as const }, { id: '110-arcanetest', text: "110 · Arcane.Test", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"09 · Módulos"}
      description={"12 exercícios: adopt, relay, seleção e apelidos."}
      href={"/docs/exercicios/09-modulos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
