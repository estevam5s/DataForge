// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "20 · Projetos finais",
  description: "6 exercícios: programas completos, de ponta a ponta.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **A linguagem a fundo** · programas completos, de ponta a ponta · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 20`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[176](#176-projeto-ferramenta-de-linha-de-comando)", "**Projeto: ferramenta de linha de comando**", "escreva um utilitario que analisa arquivos e imprime um relatorio."], ["[177](#177-projeto-analise-de-dados)", "**Projeto: analise de dados**", "carregue, limpe, agregue e visualize um conjunto de dados."], ["[178](#178-projeto-mini-linguagem)", "**Projeto: mini linguagem**", "escreva um interpretador de expressoes dentro do DataForge."], ["[179](#179-projeto-sistema-de-biblioteca)", "**Projeto: sistema de biblioteca**", "integre records, enums, banco, validacao e relatorios."], ["[180](#180-revisao-todos-os-conceitos)", "**Revisao: todos os conceitos**", "um programa que exercita cada recurso da linguagem."], ["[181](#181-encerramento-e-proximos-passos)", "**Encerramento e proximos passos**", "o que voce aprendeu, o que a linguagem ainda nao faz e para onde ir."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "176 · Projeto: ferramenta de linha de comando"},
  {"p": "**Enunciado.** escreva um utilitario que analisa arquivos e imprime um relatorio."},
  { code: `adopt Arcane.IO as IO
adopt Arcane.Text as Text
adopt Arcane.Collections as Col
adopt Arcane.Time as Time

// ═══ MODELO ═══

record Arquivo:
    nome: String
    extensao: String
    bytes: Integer
    linhas: Integer

// ═══ ANALISE ═══

action analisar(caminho: String) -> Arquivo:
    conteudo := IO.read(caminho)
    yield Arquivo(
        IO.basename(caminho),
        IO.ext(caminho) ?? "(sem)",
        IO.size(caminho),
        len(conteudo.lines())
    )

action formatar_bytes(n: Number) -> String:
    given n smaller 1024:
        yield $"{n} B"
    orif n smaller 1048576:
        yield $"{round(n / 1024, 1)} KB"
    yield $"{round(n / 1048576, 2)} MB"

// ═══ PREPARO: uma pasta de exemplo ═══

pasta := "_projeto_175"
IO.mkdir(pasta)

exemplos := {
    "notas.txt": "linha 1\\nlinha 2\\nlinha 3",
    "config.json": '{"tema": "escuro", "fonte": 14}',
    "dados.csv": "nome,valor\\nA,1\\nB,2\\nC,3\\nD,4",
    "leiame.md": "# Titulo\\n\\nUm paragrafo.",
    "script.df": "action f():\\n    yield 1\\nout f()"
}
cycle nome in exemplos.keys():
    IO.write(IO.join(pasta, nome), exemplos[nome])

// ═══ RELATORIO ═══

arquivos := IO.list_dir(pasta) >> morph nome: analisar(IO.join(pasta, nome))

out Text.box("Analise de Arquivos")
out ""
out $"  {"ARQUIVO".pad_end(14)}{"EXT".pad_end(8)}{"TAMANHO".pad_start(10)}{"LINHAS".pad_start(8)}"
out $"  {"-".repeat(40)}"

cycle a in Col.sort_by_field(arquivos, "bytes", yes):
    out $"  {a.nome.pad_end(14)}{a.extensao.pad_end(8)}{formatar_bytes(a.bytes).pad_start(10)}{str(a.linhas).pad_start(8)}"

assert len(arquivos) is 5, "cinco arquivos"

// ── totais ──
total_bytes := arquivos >> morph a: a.bytes >> distill acc, b: acc + b 0
total_linhas := arquivos >> morph a: a.linhas >> distill acc, l: acc + l 0

out ""
out $"  total: {len(arquivos)} arquivos, {formatar_bytes(total_bytes)}, {total_linhas} linhas"
assert total_linhas is 15, "soma das linhas"

// ── por extensao ──
out ""
out "  ── por extensao ──"
por_ext := Col.group_by(arquivos, "extensao")
cycle ext in sorted(por_ext.keys()):
    grupo := por_ext[ext]
    soma := grupo >> morph a: a.bytes >> distill acc, b: acc + b 0
    barra := "#".repeat(max(1, soma * 20 ~/ max(total_bytes, 1)))
    out $"  {ext.pad_end(8)}{str(len(grupo)).pad_start(3)}  {barra} {formatar_bytes(soma)}"

assert len(por_ext.keys()) is 5, "cinco extensoes distintas"

// ── o maior e o menor ──
maior := Col.sort_by_field(arquivos, "bytes", yes)[0]
menor := Col.sort_by_field(arquivos, "bytes")[0]
out ""
out $"  maior: {maior.nome} ({formatar_bytes(maior.bytes)})"
out $"  menor: {menor.nome} ({formatar_bytes(menor.bytes)})"

// ── busca por conteudo ──
out ""
out "  ── procurando por 'linha' ──"
achados := []
cycle nome in IO.list_dir(pasta):
    caminho := IO.join(pasta, nome)
    conteudo := IO.read(caminho)
    numero := 0
    cycle l in conteudo.lines():
        numero += 1
        given "linha" in l.lower():
            achados.append($"{nome}:{numero}: {l.trim()}")

cycle a in achados:
    out $"    {a}"
assert len(achados) is 3, "tres ocorrencias"

// ═══ LIMPEZA ═══
cycle nome in IO.list_dir(pasta):
    IO.delete(IO.join(pasta, nome))
IO.delete(pasta)
out ""
out "  (pasta temporaria removida)"`, lang: 'df', title: `exercicios/20-projetos-finais/176_cli_arquivos.df` },
  {"h3": "O que ele faz"},
  {"p": "1. Lê cada arquivo da pasta 2. Extrai nome, extensão, tamanho e contagem de linhas 3. Agrupa por extensão com um histograma 4. Encontra o maior e o menor 5. Busca um termo em todos os arquivos"},
  {"h3": "Modelo primeiro"},
  { code: `record Arquivo:
    nome: String
    extensao: String
    bytes: Integer
    linhas: Integer`, lang: 'df' },
  {"p": "Converter os dados brutos num record logo na entrada faz o resto do programa trabalhar com `a.bytes` em vez de chamar `IO.size` repetidamente. Uma leitura, um tipo, muitos usos."},
  {"h3": "Formatação legível"},
  { code: `action formatar_bytes(n: Number) -> String:
    given n smaller 1024:
        yield $"{n} B"
    orif n smaller 1048576:
        yield $"{round(n / 1024, 1)} KB"
    yield $"{round(n / 1048576, 2)} MB"`, lang: 'df' },
  {"p": "\"1.4 KB\" comunica; \"1433\" não. Numa ferramenta de terminal, esse detalhe é a diferença entre útil e irritante."},
  {"h3": "Colunas alinhadas"},
  { code: `out $"  {a.nome.pad_end(14)}{a.extensao.pad_end(8)}{formatar_bytes(a.bytes).pad_start(10)}"`, lang: 'df' },
  {"p": "`pad_end` para texto (alinha à esquerda), `pad_start` para número (alinha à direita). É como toda tabela de terminal se lê melhor."},
  {"h3": "Histograma proporcional"},
  { code: `barra := "#".repeat(max(1, soma * 20 ~/ max(total_bytes, 1)))`, lang: 'df' },
  {"p": "Dois `max` protegem contra os casos de borda: barra de comprimento zero, e divisão por zero se a pasta estiver vazia. Vale escrever mesmo quando \"não vai acontecer\" — é uma linha, e evita um crash na única vez em que acontece."},
  {"h3": "Busca com número de linha"},
  { code: `numero := 0
cycle l in conteudo.lines():
    numero += 1
    given "linha" in l.lower():
        achados.append($"{nome}:{numero}: {l.trim()}")`, lang: 'df' },
  {"p": "O formato `arquivo:linha: texto` é o do `grep` — e o que editores reconhecem para saltar direto ao ponto."},
  {"h3": "Limpeza"},
  {"p": "A ferramenta apaga o que criou. Num programa real, isso iria num `defer` logo após o `mkdir`."},
  {"h3": "Saída esperada"},
  { code: `┌─────────────────────┐
│ Analise de Arquivos │
└─────────────────────┘

  ARQUIVO       EXT        TAMANHO  LINHAS
  ----------------------------------------
  dados.csv     .csv         26 B       5
  script.df     .df          34 B       3
  ...

  total: 5 arquivos, 145 B, 15 linhas

  ── por extensao ──
  .csv       1  ### 26 B
  ...

  ── procurando por 'linha' ──
    notas.txt:1: linha 1
    notas.txt:2: linha 2
    notas.txt:3: linha 3`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Aceite o caminho e o termo de busca como argumentos.", "Percorra subpastas recursivamente.", "Acrescente `--json` para saída legível por máquina."]},
  {"h2": "177 · Projeto: analise de dados"},
  {"p": "**Enunciado.** carregue, limpe, agregue e visualize um conjunto de dados."},
  { code: `adopt Arcane.Analytics as An
adopt Arcane.Math as Math
adopt Arcane.Text as Text
adopt Arcane.Collections as Col

// ═══ DADOS ═══

record Venda:
    mes: Integer
    vendedor: String
    regiao: String
    valor: Number

bruto := [
    [1, "Ana", "sul", 12000], [1, "Bruno", "norte", 8500],
    [1, "Carla", "sul", 15000], [2, "Ana", "sul", 13500],
    [2, "Bruno", "norte", 9200], [2, "Carla", "sul", 11000],
    [3, "Ana", "sul", 16000], [3, "Bruno", "norte", 7800],
    [3, "Carla", "sul", 18500], [4, "Ana", "sul", 14200],
    [4, "Bruno", "norte", 11000], [4, "Carla", "sul", 19000]
]

vendas := bruto >> morph l: Venda(l[0], l[1], l[2], l[3])
valores := vendas >> morph v: v.valor

out Text.box("Analise de Vendas")

// ═══ ESTATISTICA DESCRITIVA ═══

out ""
out "── resumo ──"
out $"  registros:     {len(vendas)}"
out $"  total:         R$ {sum(valores)}"
out $"  media:         R$ {round(Math.mean(valores), 2)}"
out $"  mediana:       R$ {Math.median(valores)}"
out $"  desvio padrao: R$ {round(Math.stdev(valores), 2)}"
out $"  minimo:        R$ {min(valores)}"
out $"  maximo:        R$ {max(valores)}"

assert len(vendas) is 12, "doze registros"
assert sum(valores) is 155700, "total"

// ═══ QUARTIS E OUTLIERS ═══

q := An.quartiles(valores)
out ""
out "── distribuicao ──"
out $"  Q1: R$ {q["Q1"]}   Q2: R$ {q["Q2"]}   Q3: R$ {q["Q3"]}"
out $"  amplitude interquartil: R$ {An.iqr(valores)}"

outliers := An.outliers(valores)
out $"  outliers: {outliers}"

// ═══ AGREGACAO ═══

out ""
out "── por vendedor ──"
por_vendedor := Col.group_by(vendas, "vendedor")
resumos := []
cycle nome in sorted(por_vendedor.keys()):
    v := por_vendedor[nome] >> morph x: x.valor
    resumos.append({"nome": nome, "total": sum(v), "media": round(Math.mean(v), 2)})

cycle r in Col.sort_by_field(resumos, "total", yes):
    barra := "#".repeat(r["total"] * 30 ~/ max(sum(valores), 1))
    out $"  {r["nome"].pad_end(8)}R$ {str(r["total"]).pad_start(7)}  {barra}"

assert len(resumos) is 3, "tres vendedores"

out ""
out "── por regiao ──"
por_regiao := Col.group_by(vendas, "regiao")
cycle regiao in sorted(por_regiao.keys()):
    v := por_regiao[regiao] >> morph x: x.valor
    fatia := round(sum(v) * 100 / sum(valores), 1)
    out $"  {regiao.pad_end(8)}R$ {str(sum(v)).pad_start(7)}  ({fatia}%)"

// ═══ SERIE TEMPORAL ═══

out ""
out "── evolucao mensal ──"
por_mes := {}
cycle v in vendas:
    por_mes[v.mes] := por_mes.get(v.mes, 0) + v.valor

meses := sorted(por_mes.keys())
serie := meses >> morph m: por_mes[m]
maximo := max(serie)

cycle m in meses:
    total := por_mes[m]
    barra := "█".repeat(max(1, total * 30 ~/ maximo))
    out $"  mes {m}: {barra} R$ {total}"

assert len(meses) is 4, "quatro meses"

// ═══ TENDENCIA ═══

correlacao := An.correlation(meses, serie)
modelo := An.linear_regression(meses, serie)
previsao := An.predict_linear(modelo, 5)

out ""
out "── tendencia ──"
out $"  correlacao mes x total: {round(correlacao, 4)}"
out $"  reta: y = {round(modelo["slope"], 2)}x + {round(modelo["intercept"], 2)}"
out $"  ajuste (R2): {round(An.r_squared(meses, serie), 4)}"
out $"  previsao para o mes 5: R$ {round(previsao, 2)}"

assert correlacao bigger 0, "vendas crescendo"
assert previsao bigger serie[len(serie) - 1], "previsao acima do ultimo mes"

// ═══ MEDIA MOVEL ═══

out ""
out "── media movel (2 meses) ──"
movel := An.moving_average(serie, 2)
cycle i from 0 to len(movel) - 1:
    out $"  janela {i + 1}: R$ {round(movel[i], 2)}"

// ═══ CONCLUSAO ═══

melhor := Col.sort_by_field(resumos, "total", yes)[0]
crescimento := round((serie[len(serie) - 1] - serie[0]) * 100 / serie[0], 1)

out ""
out Text.box("Conclusao")
out $"  melhor vendedor: {melhor["nome"]} (R$ {melhor["total"]})"
out $"  crescimento no periodo: {crescimento}%"
out $"  ticket medio: R$ {round(Math.mean(valores), 2)}"

assert melhor["nome"] is "Carla", "Carla vendeu mais"
assert crescimento bigger 0, "houve crescimento"`, lang: 'df', title: `exercicios/20-projetos-finais/177_analise_dados.df` },
  {"h3": "As cinco etapas"},
  { code: `1. MODELAR      record Venda
2. DESCREVER    média, mediana, desvio, quartis
3. AGREGAR      por vendedor, por região, por mês
4. VISUALIZAR   histogramas em texto
5. PROJETAR     correlação, regressão, previsão`, lang: 'text' },
  {"h3": "Modelar antes de analisar"},
  { code: `vendas := bruto >> morph l: Venda(l[0], l[1], l[2], l[3])`, lang: 'df' },
  {"p": "Uma linha converte listas anônimas em records tipados. Depois disso, `v.valor` em vez de `l[3]` — e um erro de índice vira um erro de campo, que o `dataforge check` encontra."},
  {"h3": "Média e mediana contam histórias diferentes"},
  { code: `Math.mean(valores)      // sensível a extremos
Math.median(valores)    // resistente`, lang: 'df' },
  {"p": "Quando as duas divergem muito, a distribuição é assimétrica — geralmente por causa de poucos valores muito altos ou baixos. Olhar as duas é mais informativo que olhar só a média."},
  {"h3": "Quartis e outliers"},
  { code: `q := An.quartiles(valores)      // q1, q2, q3
An.iqr(valores)                 // Q3 - Q1
An.outliers(valores)            // fora de 1.5 × IQR`, lang: 'df' },
  {"p": "O critério de 1,5 × IQR é o mesmo do boxplot. Um outlier não é necessariamente um erro — pode ser a venda excepcional que você quer entender."},
  {"h3": "Histograma proporcional"},
  { code: `barra := "#".repeat(r["total"] * 30 ~/ max(sum(valores), 1))`, lang: 'df' },
  {"p": "O `~/` (divisão inteira) dá o número de blocos; `max(..., 1)` evita divisão por zero. Trinta caracteres cabem em qualquer terminal."},
  {"h3": "Correlação e regressão"},
  { code: `An.correlation(meses, serie)          // -1 a 1
An.linear_regression(meses, serie)    // slope e intercept
An.r_squared(meses, serie)            // qualidade do ajuste
An.predict_linear(modelo, 5)          // extrapola`, lang: 'df' },
  {"table": {"head": ["R²", "Significa"], "rows": [["perto de 1", "a reta explica bem os dados"], ["perto de 0", "a reta não explica nada"]]}},
  {"p": "**Cuidado com extrapolação.** Prever o mês 5 a partir de 4 meses é razoável; prever o mês 50 não é. A reta descreve o passado observado, não garante o futuro."},
  {"h3": "Média móvel"},
  { code: `An.moving_average(serie, 2)`, lang: 'df' },
  {"p": "Suaviza a variação de curto prazo. Numa série ruidosa, é o que deixa a tendência visível."},
  {"h3": "Saída esperada"},
  { code: `┌───────────────────┐
│ Analise de Vendas │
└───────────────────┘

── resumo ──
  registros:     12
  total:         R$ 155700
  media:         R$ 12975.0
  mediana:       R$ 12750.0
  ...

── por vendedor ──
  Carla   R$   63500  ############
  Ana     R$   55700  ##########
  Bruno   R$   36500  #######

── evolucao mensal ──
  mes 1: ████████████████████████ R$ 35500
  ...

── tendencia ──
  correlacao mes x total: 0.8834
  previsao para o mes 5: R$ 47660.0`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente uma coluna de custo e calcule a margem.", "Compare o crescimento de cada vendedor separadamente.", "Exporte o relatório como CSV com `Serde.records_to_csv`."]},
  {"h2": "178 · Projeto: mini linguagem"},
  {"p": "**Enunciado.** escreva um interpretador de expressoes dentro do DataForge."},
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
            persist i smaller len(fonte) and(fonte[i].isdigit() or fonte[i] is "."):
                numero += fonte[i]
                i += 1
            tokens.append(Token("numero", numero))
            skip
        given c.isalpha() or c is "_":
            nome := ""
            persist i smaller len(fonte) and(fonte[i].isalnum() or fonte[i] is "_"):
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

    raiz := expressao()
    guard atual() is void, $"sobrou entrada apos a expressao"
    yield raiz

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
out "  a multiplicacao ficou mais funda na arvore — precedencia respeitada"`, lang: 'df', title: `exercicios/20-projetos-finais/178_interpretador.df` },
  {"h3": "Por que este exercício"},
  {"p": "Uma linguagem capaz de implementar outra linguagem é uma linguagem completa. Este é o mesmo desenho do interpretador do próprio DataForge, em escala reduzida."},
  {"h3": "As três fases"},
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
  {"h3": "Fase 1 — Lexer"},
  {"p": "Percorre o texto agrupando caracteres em tokens:"},
  { code: `given c.isdigit():
    numero := ""
    persist i smaller len(fonte) and (fonte[i].isdigit() or fonte[i] is "."):
        numero += fonte[i]
        i += 1
    tokens.append(Token("numero", numero))`, lang: 'df' },
  {"p": "Cada tipo de token tem seu laço interno que consome enquanto o caractere pertencer àquele token. Um caractere desconhecido dispara erro com a posição — a informação que o usuário precisa."},
  {"h3": "Fase 2 — Parser de descida recursiva"},
  {"p": "A gramática vira funções, uma por nível de precedência:"},
  { code: `expressao := termo (('+' | '-') termo)*
termo     := fator (('*' | '/') fator)*
fator     := numero | nome | '(' expressao ')' | '-' fator`, lang: 'text' },
  { code: `action expressao():
    no_ := termo()
    persist e_simbolo("+") or e_simbolo("-"):
        op := consumir().valor
        no_ := {"tipo": "bin", "op": op, "esq": no_, "dir": termo()}
    yield no_`, lang: 'df' },
  {"p": "**A precedência está na estrutura, não em tabelas.** `expressao` chama `termo`, que chama `fator`. Como `termo` é chamado mais fundo, a multiplicação fica mais fundo na árvore — e o avaliador, que desce recursivamente, a calcula primeiro."},
  {"p": "O teste no fim do exercício confirma exatamente isso."},
  {"p": "Repare também que `fator` chama `expressao` de volta ao encontrar `(`. Essa recursão mútua é o que faz parênteses funcionarem em qualquer profundidade, sem código especial."},
  {"h3": "Fase 3 — Avaliador"},
  { code: `action avaliar(no_, ambiente):
    match no_["tipo"]:
        point "num":
            yield no_["valor"]
        point "bin":
            e := avaliar(no_["esq"], ambiente)
            d := avaliar(no_["dir"], ambiente)
            ...`, lang: 'df' },
  {"p": "Um `match` sobre o tipo do nó, com recursão nos filhos. É todo o interpretador."},
  {"h3": "Erros em cada fase"},
  {"table": {"head": ["Entrada", "Fase", "Mensagem"], "rows": [["`2 @ 3`", "lexer", "caractere inesperado"], ["`2 +`", "parser", "expressão incompleta"], ["`(1 + 2`", "parser", "esperava `)`"], ["`1 2`", "parser", "sobrou entrada"], ["`z + 1`", "avaliador", "variável indefinida"], ["`1 / 0`", "avaliador", "divisão por zero"]]}},
  {"p": "Cada fase valida o que é da sua competência. Isso é o que produz mensagens específicas em vez de \"erro de sintaxe\"."},
  {"h3": "Ambiente de variáveis"},
  { code: `ambiente := {"x": 10.0, "y": 4.0}
calcular("x + y", ambiente)     // 14.0`, lang: 'df' },
  {"p": "O ambiente é passado ao avaliador, não guardado globalmente. Essa é a base de escopo em qualquer interpretador."},
  {"h3": "Saída esperada"},
  { code: `┌────────────────────┐
│ Mini Interpretador │
└────────────────────┘

── expressoes ──
  2 + 3                = 5.0
  2 + 3 * 4            = 14.0
  (2 + 3) * 4          = 20.0
  ...

── erros tratados ──
  2 +          -> expressao incompleta
  (1 + 2       -> esperava ')'
  1 / 0        -> divisao por zero
  z + 1        -> variavel indefinida: z
  2 @ 3        -> caractere inesperado: '@' na posicao 2

  a multiplicacao ficou mais funda na arvore — precedencia respeitada`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente `^` para potência (associando à **direita**).", "Adicione chamadas de função: `sqrt(16)`, `max(1, 2)`.", "Implemente atribuição: `x = 5` e depois `x + 1`.", "Escreva um \"compilador\" que gera notação polonesa reversa a partir da árvore."]},
  {"h2": "179 · Projeto: sistema de biblioteca"},
  {"p": "**Enunciado.** integre records, enums, banco, validacao e relatorios."},
  { code: `adopt Arcane.Database as DB
adopt Arcane.Time as Time
adopt Arcane.Text as Text
adopt Arcane.Collections as Col

// ═══════════════════════════════════════════════════════════
//  SISTEMA DE BIBLIOTECA
// ═══════════════════════════════════════════════════════════

// ── MODELO ──

enum Situacao:
    Disponivel
    Emprestado
    Atrasado

record Livro:
    id: Integer
    titulo: String
    autor: String
    ano: Integer

record Emprestimo:
    id: Integer
    livro_id: Integer
    leitor: String
    dias: Integer

steady PRAZO_DIAS := 14
steady MULTA_POR_DIA := 2.5

// ── REGRAS (puras, testaveis) ──

action situacao_do(emprestimo) -> Situacao:
    given emprestimo is void:
        yield Situacao.Disponivel
    given emprestimo.dias bigger PRAZO_DIAS:
        yield Situacao.Atrasado
    yield Situacao.Emprestado

action multa_de(emprestimo) -> Number:
    given emprestimo is void:
        yield 0
    atraso := emprestimo.dias - PRAZO_DIAS
    yield 0 given atraso smaller_eq 0 otherwise round(atraso * MULTA_POR_DIA, 2)

action validar_livro(titulo, autor, ano) -> Cluster:
    problemas := []
    given len(titulo.trim()) smaller 2:
        problemas.append("titulo muito curto")
    given len(autor.trim()) smaller 2:
        problemas.append("autor muito curto")
    given ano smaller 1450 or ano bigger 2100:
        problemas.append($"ano improvavel: {ano}")
    yield problemas

// ── PERSISTENCIA ──

conn := DB.memory()
DB.execute(conn, """CREATE TABLE livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    ano INTEGER NOT NULL
)""")
DB.execute(conn, """CREATE TABLE emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    livro_id INTEGER NOT NULL,
    leitor TEXT NOT NULL,
    dias INTEGER NOT NULL
)""")

action cadastrar(titulo, autor, ano):
    problemas := validar_livro(titulo, autor, ano)
    given len(problemas) bigger 0:
        yield {"ok": no, "erros": problemas}
    DB.execute(conn, "INSERT INTO livros (titulo, autor, ano) VALUES (?, ?, ?)",
        [titulo.trim(), autor.trim(), ano])
    yield {"ok": yes}

action emprestar(livro_id, leitor, dias):
    ja := DB.query_one(conn, "SELECT id FROM emprestimos WHERE livro_id = ?", [livro_id])
    given ja isnt void:
        yield {"ok": no, "erros": ["livro ja emprestado"]}
    DB.execute(conn, "INSERT INTO emprestimos (livro_id, leitor, dias) VALUES (?, ?, ?)",
        [livro_id, leitor, dias])
    yield {"ok": yes}

action livros():
    yield DB.query(conn, "SELECT id, titulo, autor, ano FROM livros ORDER BY titulo")
        >> morph l: Livro(l["id"], l["titulo"], l["autor"], l["ano"])

action emprestimo_de(livro_id):
    linha := DB.query_one(conn,
        "SELECT id, livro_id, leitor, dias FROM emprestimos WHERE livro_id = ?", [livro_id])
    given linha is void:
        yield void
    yield Emprestimo(linha["id"], linha["livro_id"], linha["leitor"], linha["dias"])

// ── APLICACAO ──

out Text.box("Biblioteca")

acervo := [
    ["Dom Casmurro", "Machado de Assis", 1899],
    ["Grande Sertao Veredas", "Guimaraes Rosa", 1956],
    ["Vidas Secas", "Graciliano Ramos", 1938],
    ["A Hora da Estrela", "Clarice Lispector", 1977],
    ["X", "Autor", 2020],
    ["Livro do Futuro", "Alguem", 3000]
]

out ""
out "── cadastro ──"
cycle item in acervo:
    titulo, autor, ano := item
    r := cadastrar(titulo, autor, ano)
    given r.ok:
        out $"  ok   {titulo}"
    otherwise:
        out $"  nao  {titulo}: {r["erros"].join("; ")}"

assert DB.count(conn, "livros") is 4, "quatro livros validos"

// ── emprestimos ──
out ""
out "── emprestimos ──"
cycle e in [[1, "Ana", 5], [2, "Bruno", 20], [1, "Carla", 3]]:
    livro_id, leitor, dias := e
    r := emprestar(livro_id, leitor, dias)
    given r.ok:
        out $"  ok   livro {livro_id} para {leitor} ha {dias} dias"
    otherwise:
        out $"  nao  livro {livro_id} para {leitor}: {r["erros"].join("; ")}"

assert DB.count(conn, "emprestimos") is 2, "dois emprestimos"

// ── acervo com situacao ──
out ""
out Text.box("Acervo")
out ""
out $"  {"TITULO".pad_end(24)}{"ANO".pad_start(6)}  {"SITUACAO".pad_end(12)}MULTA"
out $"  {"-".repeat(56)}"

total_multas := 0
cycle l in livros():
    emp := emprestimo_de(l.id)
    sit := situacao_do(emp)
    multa := multa_de(emp)
    total_multas += multa
    texto_multa := "-" given multa is 0 otherwise $"R$ {multa}"
    out $"  {l.titulo.pad_end(24)}{str(l.ano).pad_start(6)}  {sit.name.pad_end(12)}{texto_multa}"

out ""
out $"  multas acumuladas: R$ {total_multas}"
assert total_multas is 15.0, "6 dias de atraso x 2.5"

// ── estatisticas ──
todos := livros()
por_seculo := Col.group_by(todos, lambda l: $"seculo {l.ano ~/ 100 + 1}")

out ""
out "── por seculo ──"
cycle s in sorted(por_seculo.keys()):
    out $"  {s}: {len(por_seculo[s])} livro(s)"

mais_antigo := Col.sort_by_field(todos, "ano")[0]
out ""
out $"  mais antigo: {mais_antigo.titulo} ({mais_antigo.ano})"
assert mais_antigo.ano is 1899, "Dom Casmurro"

emprestados := len(todos >> sift l: emprestimo_de(l.id) isnt void)
out $"  emprestados: {emprestados} de {len(todos)} ({round(emprestados * 100 / len(todos), 1)}%)"
assert emprestados is 2, "dois emprestados"

DB.close(conn)
out ""
out "  (conexao fechada)"`, lang: 'df', title: `exercicios/20-projetos-finais/179_sistema_completo.df` },
  {"h3": "A arquitetura"},
  { code: `MODELO         record Livro, record Emprestimo, enum Situacao
REGRAS         situacao_do, multa_de, validar_livro   ← puras
PERSISTENCIA   cadastrar, emprestar, livros           ← tocam o banco
APLICACAO      cadastro, relatório, estatísticas`, lang: 'text' },
  {"p": "O que distingue as camadas: **as regras não sabem que existe banco**."},
  {"h3": "Regras puras"},
  { code: `action situacao_do(emprestimo) -> Situacao:
    given emprestimo is void:
        yield Situacao.Disponivel
    given emprestimo.dias bigger PRAZO_DIAS:
        yield Situacao.Atrasado
    yield Situacao.Emprestado`, lang: 'df' },
  {"p": "Sem banco, sem `out`, sem data do sistema. Consequência prática: o teste é uma linha, e roda em microssegundos."},
  { code: `assert situacao_do(Emprestimo(1, 1, "Ana", 20)) is Situacao.Atrasado`, lang: 'df' },
  {"p": "Se ela consultasse o banco, cada teste precisaria montar um esquema."},
  {"h3": "Constantes com nome"},
  { code: `steady PRAZO_DIAS := 14
steady MULTA_POR_DIA := 2.5`, lang: 'df' },
  {"p": "Compare com `given emprestimo.dias bigger 14` espalhado por três lugares. Quando a biblioteca mudar o prazo, há uma linha para mudar — e o nome documenta o que o número significa."},
  {"h3": "Validar e converter na fronteira"},
  { code: `action livros():
    yield DB.query(conn, "SELECT ...")
        >> morph l: Livro(l["id"], l["titulo"], l["autor"], l["ano"])`, lang: 'df' },
  {"p": "Linhas do banco entram; records tipados saem. A partir dali, `l.titulo` com verificação, não `l[\"titulo\"]` com risco de digitar errado."},
  {"h3": "Regra de negócio no banco"},
  { code: `action emprestar(livro_id, leitor, dias):
    ja := DB.query_one(conn, "SELECT id FROM emprestimos WHERE livro_id = ?", [livro_id])
    given ja isnt void:
        yield {"ok": no, "erros": ["livro ja emprestado"]}`, lang: 'df' },
  {"p": "\"Um livro só pode estar emprestado uma vez\" depende do estado atual — não dá para validar sem consultar. Por isso essa checagem fica na camada de persistência, não em `validar_livro`."},
  {"h3": "Agrupar por expressão"},
  { code: `Col.group_by(todos, lambda l: $"seculo {l.ano ~/ 100 + 1}")`, lang: 'df' },
  {"p": "`group_by` aceita o nome de um campo **ou** uma função. Aqui a chave é calculada: 1899 → século 19, 1956 → século 20."},
  {"h3": "Saída esperada"},
  { code: `┌────────────┐
│ Biblioteca │
└────────────┘

── cadastro ──
  ok   Dom Casmurro
  ok   Grande Sertao Veredas
  ...
  nao  X: titulo muito curto
  nao  Livro do Futuro: ano improvavel: 3000

── emprestimos ──
  ok   livro 1 para Ana ha 5 dias
  ok   livro 2 para Bruno ha 20 dias
  nao  livro 1 para Carla: livro ja emprestado

┌────────┐
│ Acervo │
└────────┘

  TITULO                     ANO  SITUACAO    MULTA
  --------------------------------------------------------
  A Hora da Estrela         1977  Disponivel  -
  Dom Casmurro              1899  Emprestado  -
  Grande Sertao Veredas     1956  Atrasado    R$ 15.0
  Vidas Secas               1938  Disponivel  -

  multas acumuladas: R$ 15.0`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente devolução, com registro da data.", "Use `Arcane.Time` para calcular os dias a partir de datas reais.", "Exponha como API HTTP reaproveitando as regras.", "Escreva `tests/regras_test.df` cobrindo prazo, atraso e multa."]},
  {"h2": "180 · Revisao: todos os conceitos"},
  {"p": "**Enunciado.** um programa que exercita cada recurso da linguagem."},
  { code: `adopt Arcane.Text as Text
adopt Arcane.Collections as Col

out Text.box("Revisao DataForge 4.0")

// ── 1. Tipos e variaveis ──
out ""
out "1. tipos e variaveis"
nome: String := "DataForge"
versao: Number := 4.0
steady ANO := 2026
out $"   {nome} {versao} ({ANO}) — typeof: {typeof(versao)}"

// ── 2. Operadores ──
out ""
out "2. operadores"
out $"   7 // 2 = {7 ~/ 2}   2 ** 10 = {2 ** 10}   0 <= 5 <= 10: {0 <= 5 <= 10}"
out $"   pertinencia: {"a" in "casa"}   coalescencia: {void ?? "padrao"}"

// ── 3. Controle de fluxo ──
out ""
out "3. controle de fluxo"
classificacao := "alto" given versao bigger_eq 4 otherwise "antigo"
out $"   ternario: {classificacao}"
soma := 0
cycle i from 1 to 10:
    given i % 3 is 0:
        skip
    soma += i
out $"   soma sem multiplos de 3: {soma}"

// ── 4. Colecoes e compreensoes ──
out ""
out "4. colecoes"
nums := [1, 2, 3, 4, 5, 6, 7, 8]
out $"   quadrados pares: {[n * n cycle n in nums given n % 2 is 0]}"
out $"   fatia invertida: {nums[::-1][0:3]}"
out $"   vault: {{n: n * 2 cycle n in [1, 2, 3]}}"

// ── 5. Desestruturacao e spread ──
out ""
out "5. desestruturacao"
primeiro, ...resto := nums
out $"   cabeca {primeiro}, cauda com {len(resto)}"
combinado := [...resto[0:2], 99]
out $"   spread: {combinado}"

// ── 6. Acoes ──
out ""
out "6. acoes"
action aplicar(f, v):
    yield f(v)
dobro := lambda x: x * 2
out $"   alta ordem + lambda: {aplicar(dobro, 21)}"

action com_padrao(base, fator := 2):
    yield base * fator
out $"   parametro padrao: {com_padrao(10)} e {com_padrao(10, 5)}"

// ── 7. Records e enums ──
out ""
out "7. records e enums"
record Ponto:
    x: Integer
    y: Integer
    action distancia():
        yield round(sqrt(self.x ** 2 + self.y ** 2), 4)

enum Quadrante:
    Primeiro
    Outro

p := Ponto(3, 4)
q := Quadrante.Primeiro given p.x bigger 0 and p.y bigger 0 otherwise Quadrante.Outro
out $"   {p} dista {p.distancia()} — quadrante {q.name}"
out $"   copia com with: {p with {"y": 0}}"

// ── 8. Blueprints ──
out ""
out "8. blueprints"
blueprint Forma:
    action area():
        yield 0
    action descrever():
        yield $"{typeof(self)} de area {self.area()}"

blueprint Quadrado(lado) extends Forma:
    action area():
        yield self.lado ** 2

out $"   {(spawn Quadrado(4)).descrever()}"

// ── 9. Pattern matching ──
out ""
out "9. pattern matching"
action descrever(v):
    match v:
        point Integer as n when n bigger 100:
            yield "inteiro grande"
        point Integer:
            yield "inteiro"
        point [a, b]:
            yield $"par ({a},{b})"
        point Ponto(x, y):
            yield $"ponto {x},{y}"
        point {"tipo": t}:
            yield $"vault {t}"
        default:
            yield "outro"

cycle v in [5, 500, [1, 2], Ponto(1, 2), {"tipo":"x"}, "texto"]:
    out $"   {descrever(v)}"

// ── 10. Erros ──
out ""
out "10. erros"
action arriscado(n):
    guard n isnt 0, "divisor nao pode ser zero"
    defer:
        out "   (defer limpou)"
    yield 100 / n

monitor:
    out $"   ok: {arriscado(4)}"
    arriscado(0)
handle e:
    out $"   capturado: {e.message}"
ensure:
    out "   (ensure sempre roda)"

// ── 11. Pipelines ──
out ""
out "11. pipelines"
total := nums
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0
out $"   pares x10 somados: {total}"

// ── 12. Generators ──
out ""
out "12. generators"
stream action fib():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b
out $"   fibonacci: {fib().take(8)}"

// ── 13. Modulos e stdlib ──
out ""
out "13. stdlib"
g := Col.graph()
g.add_edge("a", "b", 1)
g.add_edge("b", "c", 2)
out $"   menor caminho a->c: {g.shortest_path("a", "c")["path"]}"

// ── 14. Concorrencia ──
out ""
out "14. concorrencia"
channel canal
thread:
    canal.send("mensagem da thread")
wait 150
out $"   recebido: {canal.receive()}"

// ── VERIFICACAO ──
assert soma is 37, "1+2+4+5+7+8+10"
assert p.distancia() is 5.0, "distancia"
assert total is 200, "20+40+60+80"
assert fib().take(8) is [0, 1, 1, 2, 3, 5, 8, 13], "fibonacci"
assert descrever(500) is "inteiro grande", "pattern com guarda"
assert(spawn Quadrado(4)).area() is 16, "heranca"

out ""
out Text.box("Tudo verificado")`, lang: 'df', title: `exercicios/20-projetos-finais/180_revisao_geral.df` },
  {"h3": "O roteiro"},
  {"table": {"head": ["#", "Tema", "Recursos"], "rows": [["1", "Tipos", "anotações, `steady`, `typeof`"], ["2", "Operadores", "`~/`, `**`, encadeamento, `in`, `??`"], ["3", "Fluxo", "ternário, `cycle`, `skip`"], ["4", "Coleções", "compreensões, fatiamento"], ["5", "Desestruturação", "`...resto`, spread"], ["6", "Ações", "alta ordem, lambda, padrões"], ["7", "Records/enums", "métodos, `with`"], ["8", "Blueprints", "herança, polimorfismo"], ["9", "Pattern matching", "tipo, sequência, record, vault, guarda"], ["10", "Erros", "`guard`, `defer`, `monitor`, `ensure`"], ["11", "Pipelines", "`sift`, `morph`, `distill`"], ["12", "Generators", "`stream action`, `emit`, infinito"], ["13", "Stdlib", "`Arcane.Collections`"], ["14", "Concorrência", "`thread`, `channel`"]]}},
  {"h3": "Combinações que valem notar"},
  {"p": "**Ternário com enum**"},
  { code: `q := Quadrante.Primeiro given p.x bigger 0 and p.y bigger 0 otherwise Quadrante.Outro`, lang: 'df' },
  {"p": "**Fatiamento encadeado**"},
  { code: `nums[::-1][0:3]        // inverte, depois pega os três primeiros`, lang: 'df' },
  {"p": "**`guard` + `defer` juntos**"},
  { code: `action arriscado(n):
    guard n isnt 0, "divisor nao pode ser zero"
    defer:
        out "(defer limpou)"
    yield 100 / n`, lang: 'df' },
  {"p": "O `guard` vem **antes** do `defer` de propósito: se a pré-condição falhar, não há recurso adquirido para limpar."},
  {"p": "**Pipeline multilinha**"},
  { code: `total := nums
    >> sift n: n % 2 is 0
    >> morph n: n * 10
    >> distill acc, v: acc + v 0`, lang: 'df' },
  {"p": "Uma linha que começa com `>>` continua a expressão anterior."},
  {"p": "**Generator infinito consumido parcialmente**"},
  { code: `stream action fib():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

fib().take(8)`, lang: 'df' },
  {"p": "O `persist yes` não trava porque `take(8)` para de pedir. E o `a, b := b, a + b` faz a troca simultânea sem temporária."},
  {"h3": "Autoavaliação"},
  {"p": "Se você consegue **explicar cada bloco** deste arquivo, cobriu a linguagem. Os pontos onde titubear indicam qual módulo revisar:"},
  {"table": {"head": ["Titubeou em", "Volte para"], "rows": [["tipos, `typeof`", "módulo 11"], ["records, enums", "módulo 12"], ["desestruturação, spread", "módulo 13"], ["`match` com padrões", "módulo 14"], ["`stream action`", "módulo 15"], ["`adopt`, `relay`", "módulo 16"]]}},
  {"h3": "Experimente"},
  {"list": ["Comente um bloco e preveja o que quebra nos `assert`.", "Reescreva o pipeline como compreensão, e vice-versa.", "Acrescente um bloco 15 usando um recurso que faltou."]},
  {"h2": "181 · Encerramento e proximos passos"},
  {"p": "**Enunciado.** o que voce aprendeu, o que a linguagem ainda nao faz e para onde ir."},
  { code: `adopt Arcane.Text as Text
adopt Arcane.Collections as Col

out Text.box("DataForge 4.0 — Encerramento")

// ── O QUE A LINGUAGEM TEM ──

recursos := [
    ["Tipos", "anotacoes opcionais verificadas, typeof, cast"],
    ["Analise estatica", "dataforge check: nomes, aridade, tipos"],
    ["Controle", "given/orif/otherwise, match com padroes, 4 lacos"],
    ["Colecoes", "clusters, vaults, fatiamento, compreensoes"],
    ["Destructuring", "listas, records, vaults, spread"],
    ["Acoes", "padroes, tipos, closures, lambdas, decoradores, defer"],
    ["Records", "imutaveis, igualdade estrutural, with"],
    ["Enums", "valores associados, integracao com match"],
    ["Blueprints", "heranca, traits, operadores, introspeccao"],
    ["Erros", "monitor/handle tipado, guard, retry, propagate"],
    ["Pipelines", "sift, morph, distill, multilinha"],
    ["Generators", "stream action, emit, sequencias infinitas"],
    ["Modulos", "adopt seletivo, relay, deteccao de ciclos"],
    ["Concorrencia", "async/await, thread, channel, parallel"],
    ["Stdlib", "20 modulos Arcane"],
    ["Ferramentas", "check, test, fmt, lint, doc, repl, init"]
]

out ""
out "── o que voce aprendeu ──"
cycle r in recursos:
    area, detalhe := r
    out $"  {area.pad_end(18)}{detalhe}"

assert len(recursos) is 16, "dezesseis areas"

// ── O QUE AINDA NAO EXISTE ──

pendentes := [
    ["Generics", "Cluster<T> e acoes genericas"],
    ["Exaustividade", "avisar quando um membro de enum ficou fora do match"],
    ["Contrato de trait", "verificar que o blueprint implementou tudo"],
    ["LSP", "autocomplete e ir-para-definicao no editor"],
    ["Debugger", "breakpoints e inspecao passo a passo"],
    ["Pacotes", "dataforge add, registry, lockfile"],
    ["Bytecode", "VM propria em vez de interpretador de arvore"],
    ["Sincronizacao", "mutex e semaforo entre threads"]
]

out ""
out "── o que ainda falta ──"
cycle p in pendentes:
    area, detalhe := p
    out $"  {area.pad_end(18)}{detalhe}"

// ── ONDE ESTUDAR ──

out ""
out "── documentacao ──"
docs := {
    "doc/TUTORIAL.md": "a linguagem do zero, com exemplos que rodam",
    "doc/REFERENCIA.md": "gramatica EBNF, palavras-chave, precedencia",
    "doc/BIBLIOTECA_PADRAO.md": "assinaturas dos 20 modulos Arcane",
    "doc/INSTALACAO.md": "instalar e preparar o ambiente",
    "doc/ANALISE_E_ROADMAP.md": "estado tecnico e o que vem depois",
    "CLAUDE.md": "contexto para trabalhar no interpretador"
}
cycle caminho in docs.keys():
    out $"  {caminho.pad_end(28)}{docs[caminho]}"

// ── COMANDOS ──

out ""
out "── comandos do dia a dia ──"
comandos := [
    "dataforge init            comeca um projeto",
    "dataforge run arquivo.df  executa",
    "dataforge check src/      analise estatica",
    "dataforge test tests/ -v  roda os testes",
    "dataforge fmt . --check   verifica a formatacao",
    "dataforge lint src/       estilo e higiene",
    "dataforge doc src/        gera documentacao",
    "dataforge repl            console interativo"
]
cycle c in comandos:
    out $"  {c}"

// ── DESAFIOS ──

out ""
out Text.box("Desafios")

desafios := [
    ["Facil", "um jogo da velha em terminal"],
    ["Facil", "conversor de unidades com enum e records"],
    ["Medio", "gerenciador de tarefas com banco e CLI"],
    ["Medio", "cliente de API com retry e cache"],
    ["Medio", "gerador de sites estaticos a partir de markdown"],
    ["Dificil", "linguagem de consulta sobre CSV"],
    ["Dificil", "servidor HTTP com rotas, auth e persistencia"],
    ["Dificil", "type checker para o mini interpretador do exercicio 177"]
]

por_nivel := Col.group_by(desafios, lambda d: d[0])
out ""
cycle nivel in ["Facil", "Medio", "Dificil"]:
    out $"  {nivel}:"
    cycle d in por_nivel[nivel]:
        out $"    - {d[1]}"

assert len(desafios) is 8, "oito desafios"
assert len(por_nivel.keys()) is 3, "tres niveis"

// ── FECHAMENTO ──

out ""
out Text.box("180 exercicios concluidos")
out ""
out "  Modulos 01-10: fundamentos, colecoes, acoes, blueprints, erros"
out "  Modulos 11-20: tipos, records, padroes, streams, projetos"
out ""
out "  Rode a suite inteira com:"
out "    python3 exercicios/run_all.py"
out ""
out "  Contribua: o roadmap esta em doc/ANALISE_E_ROADMAP.md"`, lang: 'df', title: `exercicios/20-projetos-finais/181_proximos_passos.df` },
  {"h3": "O que você percorreu"},
  {"p": "180 exercícios em 20 módulos, do `out \"Ola\"` a um interpretador de expressões com lexer, parser e avaliador próprios."},
  {"p": "**Módulos 1–10: a base**"},
  {"p": "Fundamentos, controle de fluxo, coleções, textos, ações, blueprints, tratamento de erros, pipelines, módulos e concorrência."},
  {"p": "**Módulos 11–20: DataForge 4.0**"},
  {"p": "Tipos verificados, análise estática, records, enums, desestruturação, pattern matching, generators, sistema de módulos, tempo e sistema, persistência, concorrência e seis projetos integradores."},
  {"h3": "O que a linguagem tem hoje"},
  {"table": {"head": ["Área", "Recursos"], "rows": [["**Tipos**", "anotações opcionais verificadas, `typeof`, `cast`, análise estática"], ["**Dados**", "records imutáveis, enums, clusters, vaults, compreensões"], ["**Fluxo**", "`given`/`orif`/`otherwise`, `match` estrutural, quatro laços"], ["**Ações**", "padrões, tipos, closures, lambdas, decoradores, `defer`"], ["**Erros**", "`handle` tipado, `guard`, `retry`, `propagate`, stack traces"], ["**Fluxos**", "pipelines, `stream action` com avaliação preguiçosa"], ["**Módulos**", "`adopt` seletivo, `relay`, detecção de ciclos, `forge.toml`"], ["**Stdlib**", "20 módulos `Arcane.*`"], ["**Ferramentas**", "`check`, `test`, `fmt`, `lint`, `doc`, `repl`, `init`"]]}},
  {"h3": "O que ainda não existe"},
  {"p": "Ser honesto sobre isso é parte de conhecer a ferramenta:"},
  {"list": ["**Generics** — `Cluster<T>` e ações genéricas", "**Exaustividade** — avisar quando um membro de enum ficou fora do `match`", "**Contrato de trait** — verificar que o blueprint implementou tudo", "**LSP** — autocomplete e ir-para-definição no editor", "**Debugger** — breakpoints e inspeção passo a passo", "**Gerenciador de pacotes** — `dataforge add`, registry, lockfile", "**Bytecode** — VM própria no lugar do interpretador de árvore", "**Sincronização** — mutex e semáforo entre threads"]},
  {"p": "O plano completo está em `doc/ANALISE_E_ROADMAP.md`."},
  {"h3": "O ciclo de trabalho"},
  { code: `dataforge init                # começar um projeto
dataforge check src/          # nomes, tipos, aridade
dataforge lint src/           # estilo e higiene
dataforge fmt src/            # formatar
dataforge test tests/ -v      # testes
dataforge doc src/ --out=doc/API.md
dataforge run                 # executar`, lang: 'bash' },
  {"p": "Em integração contínua:"},
  { code: `dataforge fmt . --check && dataforge check . && dataforge test`, lang: 'bash' },
  {"h3": "Desafios para continuar"},
  {"p": "**Fácil**"},
  {"list": ["Jogo da velha em terminal", "Conversor de unidades com enum e records"]},
  {"p": "**Médio**"},
  {"list": ["Gerenciador de tarefas com banco e CLI", "Cliente de API com retry e cache", "Gerador de sites estáticos a partir de markdown"]},
  {"p": "**Difícil**"},
  {"list": ["Linguagem de consulta sobre CSV (`SELECT nome WHERE idade > 30`)", "Servidor HTTP com rotas, autenticação e persistência", "Type checker para o mini interpretador do exercício 177"]},
  {"p": "Esse último é especialmente interessante: você já escreveu o interpretador; acrescentar verificação de tipos a ele é o mesmo caminho que o DataForge percorreu do 3.0 para o 4.0."},
  {"h3": "Documentação"},
  {"table": {"head": ["Documento", "Para"], "rows": [["[`doc/TUTORIAL.md`](../../doc/TUTORIAL.md)", "a linguagem do zero"], ["[`doc/REFERENCIA.md`](../../doc/REFERENCIA.md)", "gramática e semântica"], ["[`doc/BIBLIOTECA_PADRAO.md`](../../doc/BIBLIOTECA_PADRAO.md)", "os módulos `Arcane.*`"], ["[`doc/ANALISE_E_ROADMAP.md`](../../doc/ANALISE_E_ROADMAP.md)", "estado técnico e roadmap"], ["[`CLAUDE.md`](../../CLAUDE.md)", "trabalhar no interpretador"]]}},
  {"h3": "Rodando tudo"},
  { code: `python3 exercicios/run_all.py         # os 180
python3 exercicios/run_all.py 14      # um módulo
python3 -m pytest tests/ -q           # a suíte do interpretador`, lang: 'bash' },
  {"h3": "Contribuir"},
  {"p": "O roadmap tem itens de todos os tamanhos. Os mais acessíveis para começar:"},
  {"list": ["Verificação de exaustividade em `match` sobre enum", "Contrato de trait no analisador estático", "Novas funções nos módulos `Arcane.*`", "Mais exercícios"]},
  {"p": "Cada recurso novo pede: sintaxe documentada, teste de regressão, exercício didático e a suíte existente continuando verde."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/20-projetos-finais/176_cli_arquivos.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '176-projeto-ferramenta-de-linha-de-comando', text: "176 · Projeto: ferramenta de linha de comando", level: 2 as const }, { id: 'o-que-ele-faz', text: "O que ele faz", level: 3 as const }, { id: 'modelo-primeiro', text: "Modelo primeiro", level: 3 as const }, { id: 'formatacao-legivel', text: "Formatação legível", level: 3 as const }, { id: 'colunas-alinhadas', text: "Colunas alinhadas", level: 3 as const }, { id: 'histograma-proporcional', text: "Histograma proporcional", level: 3 as const }, { id: 'busca-com-numero-de-linha', text: "Busca com número de linha", level: 3 as const }, { id: 'limpeza', text: "Limpeza", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '177-projeto-analise-de-dados', text: "177 · Projeto: analise de dados", level: 2 as const }, { id: 'as-cinco-etapas', text: "As cinco etapas", level: 3 as const }, { id: 'modelar-antes-de-analisar', text: "Modelar antes de analisar", level: 3 as const }, { id: 'media-e-mediana-contam-historias-diferentes', text: "Média e mediana contam histórias diferentes", level: 3 as const }, { id: 'quartis-e-outliers', text: "Quartis e outliers", level: 3 as const }, { id: 'histograma-proporcional', text: "Histograma proporcional", level: 3 as const }, { id: 'correlacao-e-regressao', text: "Correlação e regressão", level: 3 as const }, { id: 'media-movel', text: "Média móvel", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '178-projeto-mini-linguagem', text: "178 · Projeto: mini linguagem", level: 2 as const }, { id: 'por-que-este-exercicio', text: "Por que este exercício", level: 3 as const }, { id: 'as-tres-fases', text: "As três fases", level: 3 as const }, { id: 'fase-1-lexer', text: "Fase 1 — Lexer", level: 3 as const }, { id: 'fase-2-parser-de-descida-recursiva', text: "Fase 2 — Parser de descida recursiva", level: 3 as const }, { id: 'fase-3-avaliador', text: "Fase 3 — Avaliador", level: 3 as const }, { id: 'erros-em-cada-fase', text: "Erros em cada fase", level: 3 as const }, { id: 'ambiente-de-variaveis', text: "Ambiente de variáveis", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '179-projeto-sistema-de-biblioteca', text: "179 · Projeto: sistema de biblioteca", level: 2 as const }, { id: 'a-arquitetura', text: "A arquitetura", level: 3 as const }, { id: 'regras-puras', text: "Regras puras", level: 3 as const }, { id: 'constantes-com-nome', text: "Constantes com nome", level: 3 as const }, { id: 'validar-e-converter-na-fronteira', text: "Validar e converter na fronteira", level: 3 as const }, { id: 'regra-de-negocio-no-banco', text: "Regra de negócio no banco", level: 3 as const }, { id: 'agrupar-por-expressao', text: "Agrupar por expressão", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '180-revisao-todos-os-conceitos', text: "180 · Revisao: todos os conceitos", level: 2 as const }, { id: 'o-roteiro', text: "O roteiro", level: 3 as const }, { id: 'combinacoes-que-valem-notar', text: "Combinações que valem notar", level: 3 as const }, { id: 'autoavaliacao', text: "Autoavaliação", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '181-encerramento-e-proximos-passos', text: "181 · Encerramento e proximos passos", level: 2 as const }, { id: 'o-que-voce-percorreu', text: "O que você percorreu", level: 3 as const }, { id: 'o-que-a-linguagem-tem-hoje', text: "O que a linguagem tem hoje", level: 3 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 3 as const }, { id: 'o-ciclo-de-trabalho', text: "O ciclo de trabalho", level: 3 as const }, { id: 'desafios-para-continuar', text: "Desafios para continuar", level: 3 as const }, { id: 'documentacao', text: "Documentação", level: 3 as const }, { id: 'rodando-tudo', text: "Rodando tudo", level: 3 as const }, { id: 'contribuir', text: "Contribuir", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"20 · Projetos finais"}
      description={"6 exercícios: programas completos, de ponta a ponta."}
      href={"/docs/exercicios/20-projetos-finais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
