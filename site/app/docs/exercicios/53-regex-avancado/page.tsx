// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "53 · Regex avançado",
  description: "15 exercícios: grupos nomeados, âncoras, troca que calcula e risco.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Sistemas e arquitetura** · grupos nomeados, âncoras, troca que calcula e risco · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 53`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[313](#313-o-grupo-nomeado-que-nao-chegava-ao-resultado)", "**o grupo nomeado que nao chegava ao resultado**", "'(?P<ano>\\d{4})' sempre compilou, e o nome NAO vinha no"], ["[314](#314-match-ancora-so-no-comeco)", "**'match' ancora so no COMECO**", "validar com 'match' aceita lixo no fim, calado. E um"], ["[315](#315-a-troca-que-calcula)", "**a troca que CALCULA**", "'sub' so troca por texto. Mascarar um CPF, dobrar um"], ["[316](#316-partir-sem-perder-o-separador)", "**partir sem perder o separador**", "'split' descarta os separadores. Reconstruir o texto"], ["[317](#317-depurar-um-padrao)", "**depurar um padrao**", "um padrao que devolve a lista errada quase sempre casa"], ["[318](#318-ler-uma-expressao-regular)", "**ler uma expressao regular**", "ler uma expressao regular e o custo dela. O padrao que"], ["[319](#319-o-padrao-que-trava-o-processo)", "**o padrao que trava o processo**", "'(a+)+$' contra trinta caracteres que nao casam leva"], ["[320](#320-os-validadores-brasileiros-e-o-que-eles-nao-fazem)", "**os validadores brasileiros, e o que eles NAO fazem**", "'is_cpf' confere o FORMATO, e nao o digito verificador."], ["[321](#321-um-analisador-de-log-completo)", "**um analisador de log completo**", "juntar grupos nomeados, ancoramento, posicao e"], ["[322](#322-as-tres-flags-e-o-que-cada-uma-muda)", "**as tres flags, e o que cada uma muda**", "IGNORECASE, MULTILINE e DOTALL mudam o significado do"], ["[323](#323-compilar-uma-vez-usar-muitas)", "**compilar uma vez, usar muitas**", "um padrao usado num laco e recompilado a cada volta."], ["[324](#324-o-texto-que-vem-de-fora-nao-e-um-padrao)", "**o texto que vem de fora nao e um padrao**", "montar um padrao concatenando texto de usuario e como um"], ["[325](#325-ler-um-formato-de-texto-sem-escrever-um-parser)", "**ler um formato de texto sem escrever um parser**", "um arquivo de configuracao em secoes. Regex nao serve"], ["[326](#326-extrair-uma-tabela-de-um-texto)", "**extrair uma tabela de um texto**", "o caso mais comum de regex num trabalho de dados —"], ["[327](#327-o-mapa-do-modulo-e-o-que-ele-nao-faz)", "**o mapa do modulo, e o que ele nao faz**", "fechar o modulo dizendo onde cada peca serve, e sendo"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "313 · o grupo nomeado que nao chegava ao resultado"},
  {"p": "**Enunciado.** '(?P<ano>\\d{4})' sempre compilou, e o nome NAO vinha no"},
  { code: `// resultado — ele chegava por posicao. E ninguem escreve
// '(?P<ano>…)' para depois ler 'groups[2]'.

adopt Arcane.Regex as Regex

steady DATA := "(?P<ano>\\\\d{4})-(?P<mes>\\\\d{2})-(?P<dia>\\\\d{2})"

out "== 1. o nome chega junto =="

achado := Regex.search(DATA, "vence em 2026-09-20, avise antes")
assert achado["matched"]
assert achado["named"]["ano"] is "2026"
assert achado["named"]["mes"] is "09"
assert achado["named"]["dia"] is "20"
out $"   {achado['named']}"

out ""
out "== 2. a posicao continua existindo =="

// Havia codigo lendo dali; tira-la seria quebrar o que funciona.
assert achado["groups"] is ["2026", "09", "20"]
assert achado["value"] is "2026-09-20"

out ""
out "== 3. 'named' devolve so o vault =="

assert Regex.named(DATA, "2026-09-20")["mes"] is "09"
assert Regex.named(DATA, "sem data") is {}

out ""
out "== 4. e 'findnamed' le um log linha a linha =="

// Uma string simples nao cruza linhas: para texto multilinha, tres
// aspas.
steady LOG := """2026-09-20 ERRO falha ao gravar
2026-09-20 AVISO disco quase cheio
2026-09-21 ERRO conexao perdida"""

steady LINHA := "(?P<data>[\\\\d-]+) (?P<nivel>\\\\w+) (?P<texto>.+)"
linhas := Regex.findnamed(LINHA, LOG)

assert len(linhas) is 3
assert linhas[0]["nivel"] is "ERRO"
assert linhas[1]["texto"] is "disco quase cheio"

erros := [l cycle l in linhas given l["nivel"] is "ERRO"]
assert len(erros) is 2
cycle e in erros:
    out $"   {e['data']}: {e['texto']}"

out ""
out "== 5. os nomes declarados, na ordem =="

assert Regex.group_names(DATA) is ["ano", "mes", "dia"]
assert Regex.group_names("(\\\\d)(\\\\w)") is []

out ""
out "== 6. sem grupo nomeado, 'named' vem vazio =="

// Ler ["named"] nao pode depender de o padrao ter nomes.
assert Regex.search("\\\\d+", "abc 12")["named"] is {}
assert Regex.search("\\\\d+", "sem numero")["named"] is {}

out "exercicio 313 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/313_grupos_nomeados.df` },
  {"p": "`(?P<ano>\\d{4})` sempre compilou, e o nome **não** vinha no resultado — ele chegava por posição. E ninguém escreve `(?P<ano>…)` para depois ler `groups[2]`."},
  {"h3": "O nome chega junto"},
  {"p": "`achado[\"named\"]` é um vault. A posição continua em `groups`: havia código lendo dali, e tirá-la seria quebrar o que funciona."},
  {"h3": "`findnamed` lê um log linha a linha"},
  {"p": "Um vault por casamento — e daí em diante é filtrar e agrupar como qualquer lista."},
  {"h3": "E `named` vem vazio quando não há nomes"},
  {"p": "Ler `[\"named\"]` não pode depender de o padrão ter nomes, senão toda leitura viraria um `??`."},
  {"h2": "314 · 'match' ancora so no COMECO"},
  {"p": "**Enunciado.** validar com 'match' aceita lixo no fim, calado. E um"},
  { code: `// validador que aceita "88010-000 e mais" grava um CEP que nao existe.

adopt Arcane.Regex as Regex

steady CEP := "\\\\d{5}-?\\\\d{3}"

out "== 1. a diferenca =="

assert Regex.match(CEP, "88010-000 e mais lixo")["matched"]
assert not Regex.fullmatch(CEP, "88010-000 e mais lixo")["matched"]
assert Regex.fullmatch(CEP, "88010-000")["matched"]

out ""
out "== 2. 'is_exactly' e a pergunta de um validador =="

assert Regex.is_exactly(CEP, "88010000")
assert Regex.is_exactly(CEP, "88010-000")
assert not Regex.is_exactly(CEP, "8801-000")
assert not Regex.is_exactly(CEP, " 88010-000")

out ""
out "== 3. um formulario inteiro =="

steady CAMPOS := {
    "cep": CEP,
    "telefone": "\\\\(\\\\d{2}\\\\) \\\\d{4,5}-\\\\d{4}",
    "usuario": "[a-z0-9_]{3,20}"
}

action validar(dados):
    erros := {}
    cycle campo in keys(CAMPOS):
        valor := dados[campo] ?? ""
        given not Regex.is_exactly(CAMPOS[campo], valor):
            erros[campo] := $"'{valor}' nao e um {campo} valido"
    yield erros

bons := validar({"cep": "88010-000", "telefone": "(48) 99999-1234",
        "usuario": "ana_souza"})
assert bons is {}

ruins := validar({"cep": "88010-000 ", "telefone": "48999991234",
        "usuario": "Ana"})
assert len(keys(ruins)) is 3
cycle campo in keys(ruins):
    out $"   {ruins[campo]}"

out ""
out "== 4. o resultado vazio tem as MESMAS chaves =="

// Senao ler ["start"] de um nao-casamento levantaria.
vazio := Regex.fullmatch("\\\\d+", "abc")
cheio := Regex.fullmatch("\\\\d+", "12")
assert keys(vazio) is keys(cheio)
assert vazio["start"] is -1
assert vazio["named"] is {}

out ""
out "== 5. o ancoramento tambem da para escrever a mao =="

// '^...$' faz o mesmo, e e o que se ve em padrao copiado da internet.
assert Regex.test("^" + CEP + "$", "88010-000")
assert not Regex.test("^" + CEP + "$", "88010-000 x")
out "   'fullmatch' e o mesmo, sem depender de lembrar das ancoras"

out "exercicio 314 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/314_ancorar.df` },
  {"p": "Validar com ele aceita lixo no fim, calado. Um validador que aceita `\"88010-000 e mais\"` grava um CEP que não existe."},
  {"h3": "`fullmatch` casa a string inteira"},
  {"p": "E `is_exactly` é a pergunta que um validador faz: sim ou não."},
  {"h3": "O resultado vazio tem as MESMAS chaves"},
  {"p": "Senão ler `[\"start\"]` de um não-casamento levantaria — e todo uso precisaria de um `given` antes."},
  {"h3": "E `^...$` faz o mesmo"},
  {"p": "É o que se vê em padrão copiado da internet. `fullmatch` é o mesmo, sem depender de lembrar das âncoras."},
  {"h2": "315 · a troca que CALCULA"},
  {"p": "**Enunciado.** 'sub' so troca por texto. Mascarar um CPF, dobrar um"},
  { code: `// numero ou virar a caixa de uma palavra exigia sair do modulo — e
// quem sai escreve um laco que se esquece de um caso.

adopt Arcane.Regex as Regex

out "== 1. dobrar os numeros =="

assert Regex.sub_with("\\\\d+", lambda m => str(int(m["value"]) * 2),
    "a1 b20 c300") is "a2 b40 c600"

out ""
out "== 2. a acao recebe os grupos NOMEADOS =="

action inverter_data(m):
    n := m["named"]
    yield $"{n['dia']}/{n['mes']}/{n['ano']}"

steady ISO := "(?P<ano>\\\\d{4})-(?P<mes>\\\\d{2})-(?P<dia>\\\\d{2})"
assert Regex.sub_with(ISO, inverter_data,
    "de 2026-09-20 a 2026-10-01") is "de 20/09/2026 a 01/10/2026"

out ""
out "== 3. devolver void NAO troca =="

// E o que deixa a acao escolher o que nao mexer, sem reconstruir.
action so_os_grandes(m):
    given int(m["value"]) bigger 10:
        yield "N"
    yield void

assert Regex.sub_with("\\\\d+", so_os_grandes, "1 20 3 400") is "1 N 3 N"

out ""
out "== 4. mascarar um documento, deixando o fim =="

action mascarar_cpf(m):
    inteiro := m["value"]
    yield "***.***." + inteiro[8:len(inteiro)]

steady CPF := "\\\\d{3}\\\\.\\\\d{3}\\\\.\\\\d{3}-\\\\d{2}"
mascarado := Regex.sub_with(CPF, mascarar_cpf,
    "cliente 529.982.247-25 confirmado")
assert mascarado is "cliente ***.***.247-25 confirmado"
out $"   {mascarado}"

out ""
out "== 5. o limite de trocas =="

assert Regex.sub_with("\\\\d", lambda m => "x", "12345", count := 2) is "xx345"

out ""
out "== 6. 'replace_map' deixa o que nao esta na tabela =="

// Uma tabela sem padrao transformaria o desconhecido em vazio — e o
// texto sairia com buracos.
steady TABELA := {"sim": "yes", "nao": "no"}
assert Regex.replace_map("\\\\w+", TABELA, "sim talvez nao") is "yes talvez no"

out ""
out "== 7. e uma acao que nao e acao e recusada =="

recusou := no
monitor:
    Regex.sub_with("\\\\d", "x", "1")
handle RegexError as e:
    recusou := yes
    assert "acao" in e.message
assert recusou

out "exercicio 315 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/315_substituir_calculando.df` },
  {"p": "`sub` só troca por texto. Mascarar um CPF, dobrar um número ou virar a caixa de uma palavra exigia sair do módulo — e quem sai escreve um laço que se esquece de um caso."},
  {"h3": "A ação recebe o mesmo vault de `search`"},
  {"p": "Com `value`, `groups`, `named` e `span`. Passar o objeto de casamento do Python obrigaria a escrever `m.group(1)`, que é vocabulário de outra linguagem."},
  {"h3": "Devolver `void` NÃO troca"},
  {"p": "É o que deixa a ação escolher o que **não** mexer, sem reconstruir o texto."},
  {"h3": "E `replace_map` deixa o que não está na tabela"},
  {"p": "Uma tabela sem padrão transformaria o desconhecido em vazio, e o texto sairia com buracos."},
  {"h2": "316 · partir sem perder o separador"},
  {"p": "**Enunciado.** 'split' descarta os separadores. Reconstruir o texto"},
  { code: `// depois de transformar os pedacos exige saber o que havia entre eles
// — e adivinhar ali e como um join(" ") transforma tabulacao em
// espaco sem ninguem ver.

adopt Arcane.Regex as Regex

out "== 1. a diferenca =="

assert Regex.split("\\\\s+", "a  b\\tc") is ["a", "b", "c"]
assert Regex.split_keep("\\\\s+", "a  b\\tc") is ["a", "  ", "b", "\\t", "c"]

out ""
out "== 2. e e por isso que ele reconstroi =="

steady TEXTO := "campo1 = valor;  campo2 =outro"
pedacos := Regex.split_keep("[=;]", TEXTO)
assert join("", pedacos) is TEXTO
out $"   {len(pedacos)} pedacos, e o texto volta inteiro"

out ""
out "== 3. transformar so o que nao e separador =="

action maiusculo_fora_do_separador(partes):
    saida := []
    cycle p in partes:
        given Regex.is_exactly("[=;]", p):
            saida.append(p)
        otherwise:
            saida.append(upper(p))
    yield join("", saida)

assert maiusculo_fora_do_separador(pedacos) is "CAMPO1 = VALOR;  CAMPO2 =OUTRO"

out ""
out "== 4. separador nas pontas =="

assert Regex.split_keep(",", ",a,") is [",", "a", ","]
assert Regex.split_keep(",", "sem virgula") is ["sem virgula"]

out ""
out "== 5. recortar ENTRE marcas =="

steady HTML := "<b>um</b> e <b>dois</b>, e <i>tres</i>"
assert Regex.between("<b>", "</b>", HTML) is ["um", "dois"]
assert Regex.between("<i>", "</i>", HTML) is ["tres"]

// Uma abertura sem fecho nao entrega meio pedaco.
assert Regex.between("\\\\[", "\\\\]", "[a] e [sem fim") is ["a"]

out ""
out "== 6. um caso de verdade: os campos de uma consulta =="

steady URL := "?nome=Ana&cidade=Florianopolis&pagina=2"
pares := {}
cycle pedaco in Regex.split("&", URL[1:len(URL)]):
    partes := Regex.split("=", pedaco)
    pares[partes[0]] := partes[1]

assert pares["nome"] is "Ana"
assert pares["pagina"] is "2"

out "exercicio 316 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/316_partir_e_recortar.df` },
  {"p": "`split` descarta os separadores. Reconstruir o texto depois de transformar os pedaços exige saber o que havia entre eles — e adivinhar ali é como um `join(\" \")` transforma tabulação em espaço sem ninguém ver."},
  {"h3": "E é por isso que ele reconstrói"},
  {"p": "`join(\"\", pedacos)` devolve o texto inteiro, byte a byte."},
  {"h3": "`between` recorta entre marcas"},
  {"p": "E uma abertura sem fecho não entrega meio pedaço."},
  {"h2": "317 · depurar um padrao"},
  {"p": "**Enunciado.** um padrao que devolve a lista errada quase sempre casa"},
  { code: `// num lugar que nao se esperava — e uma lista de resultados nao diz
// ONDE. 'highlight' marca, 'positions' aponta linha e coluna.

adopt Arcane.Regex as Regex

out "== 1. marcar os casamentos =="

assert Regex.highlight("\\\\d+", "a1 b22 c333") is "a[1] b[22] c[333]"
assert Regex.highlight("\\\\d+", "a1", before := "<<", after := ">>") is "a<<1>>"

out ""
out "== 2. e e assim que se ve o padrao ganancioso =="

steady HTML := "<b>um</b> e <b>dois</b>"

// '.*' come tudo ate o ULTIMO fecho.
guloso := Regex.highlight("<b>.*</b>", HTML)
assert guloso is "[<b>um</b> e <b>dois</b>]"

// '.*?' para no primeiro.
preguicoso := Regex.highlight("<b>.*?</b>", HTML)
assert preguicoso is "[<b>um</b>] e [<b>dois</b>]"

out $"   guloso:     {guloso}"
out $"   preguicoso: {preguicoso}"

out ""
out "== 3. linha e coluna, e nao deslocamento em bytes =="

// Quem le um erro procura linha e coluna; um 'span' nao serve para
// apontar num arquivo.
steady FONTE := """action somar(a, b):
    yield a + b

action dobrar(x):
    yield x * 2"""

acoes := Regex.positions("action (\\\\w+)", FONTE)
assert len(acoes) is 2
assert acoes[0]["linha"] is 1
assert acoes[0]["coluna"] is 1
assert acoes[1]["linha"] is 4
assert acoes[1]["value"] is "action dobrar"

cycle a in acoes:
    out $"   {a['linha']}:{a['coluna']}  {a['value']}"

out ""
out "== 4. a coluna comeca em UM =="

achado := Regex.positions("x", "  x")
assert achado[0]["coluna"] is 3
assert achado[0]["start"] is 2

out ""
out "== 5. um lint de brinquedo =="

steady CODIGO := """x := 1
// TODO: arrumar isto
y := 2
// TODO: e isto tambem"""

pendencias := Regex.positions("TODO:.*", CODIGO)
assert len(pendencias) is 2
cycle p in pendencias:
    out $"   linha {p['linha']}: {p['value']}"

out "exercicio 317 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/317_ver_o_que_casou.df` },
  {"p": "Um padrão que devolve a lista errada quase sempre casa num lugar que não se esperava — e uma lista de resultados não diz **onde**."},
  {"h3": "`highlight` marca"},
  {"p": "E é assim que se vê o padrão ganancioso: `.*` come tudo até o último fecho; `.*?` para no primeiro."},
  {"h3": "`positions` responde em linha e coluna"},
  {"p": "A posição em bytes de um `span` não serve para apontar num arquivo: quem lê um erro procura linha e coluna. E a coluna começa em **um**."},
  {"h2": "318 · ler uma expressao regular"},
  {"p": "**Enunciado.** ler uma expressao regular e o custo dela. O padrao que"},
  { code: `// valida um e-mail cabe numa linha e leva dez minutos para ser
// entendido por quem nao a escreveu.

adopt Arcane.Regex as Regex

out "== 1. pedaco a pedaco =="

partes := Regex.explain("^\\\\d{3}-\\\\w+$")
assert [p["trecho"] cycle p in partes] is ["^", "\\\\d", "{3}", "-", "\\\\w", "+", "$"]

cycle p in partes:
    out $"   {p['trecho']}  ->  {p['quer_dizer']}"

out ""
out "== 2. ele nomeia o grupo =="

assert "'ano'" in Regex.explain("(?P<ano>\\\\d{4})")[0]["quer_dizer"]
assert "NAO captura" in Regex.explain("(?:ab)")[0]["quer_dizer"]

out ""
out "== 3. e distingue o preguicoso do guloso =="

assert "MENOS" in Regex.explain("a+?")[1]["quer_dizer"]
assert "MENOS" not in Regex.explain("a+")[1]["quer_dizer"]

out ""
out "== 4. a classe negada =="

assert "FORA" in Regex.explain("[^abc]")[0]["quer_dizer"]
assert "FORA" not in Regex.explain("[abc]")[0]["quer_dizer"]

out ""
out "== 5. literais seguidos viram um pedaco so =="

literal := Regex.explain("abc")
assert len(literal) is 1
assert literal[0]["trecho"] is "abc"

out ""
out "== 6. um padrao quebrado NAO e explicado =="

// E a mensagem mostra ONDE: a do Python diz 'at position 7' e nao
// desenha o padrao.
quebrou := no
monitor:
    Regex.explain("(sem fecho")
handle RegexError as e:
    quebrou := yes
    assert "^" in e.message
    out $"   recusou o padrao quebrado"
assert quebrou

out ""
out "== 7. um padrao de verdade, lido em voz alta =="

steady TELEFONE := "\\\\(\\\\d{2}\\\\) \\\\d{4,5}-\\\\d{4}"
frases := [p["quer_dizer"] cycle p in Regex.explain(TELEFONE)]
assert "de 4 a 5 vezes" in frases
assert Regex.is_exactly(TELEFONE, "(48) 99999-1234")

out "exercicio 318 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/318_explicar_um_padrao.df` },
  {"p": "Ler uma expressão regular é o custo dela: o padrão que valida um e-mail cabe numa linha e leva dez minutos para ser entendido por quem não a escreveu."},
  {"h3": "Pedaço a pedaço"},
  {"p": "Cada trecho com o que ele quer dizer, em português. A tabela é fechada de propósito: explicar o que não se reconhece com uma frase genérica é pior que não explicar, porque parece resposta."},
  {"h3": "Ele distingue o preguiçoso e a classe negada"},
  {"p": "`+?` e `[^abc]` — os dois que mais confundem quem lê."},
  {"h3": "E um padrão quebrado NÃO é explicado"},
  {"p": "A mensagem mostra **onde**: a do Python diz `at position 7` e não desenha o padrão, e num padrão de sessenta caracteres contar até sete é o que a pessoa faz em seguida."},
  {"h2": "319 · o padrao que trava o processo"},
  {"p": "**Enunciado.** '(a+)+$' contra trinta caracteres que nao casam leva"},
  { code: `// ANOS: o motor tenta todas as formas de dividir a entrada entre os
// dois quantificadores, e sao 2^n. Nada no modulo dizia isso.

adopt Arcane.Regex as Regex

out "== 1. os quatro desenhos classicos =="

steady PERIGOSOS := ["(a+)+$", "([a-z]+)+$", "(a{2,})+$", "(x|x)+$"]

cycle padrao in PERIGOSOS:
    analise := Regex.risk(padrao)
    assert analise["perigoso"]
    out $"   {padrao}  ->  {analise['motivo']}"

out ""
out "== 2. e o padrao comum NAO e acusado =="

// Um falso alarme aqui ensinaria a desligar a conferencia inteira.
steady COMUNS := [
    "\\\\d{3}-\\\\d{4}",
    "^[a-z]+@[a-z]+\\\\.[a-z]{2,}$",
    "(?P<ano>\\\\d{4})-(?P<mes>\\\\d{2})",
    "\\\\w+"
]

cycle padrao in COMUNS:
    assert not Regex.risk(padrao)["perigoso"]

out ""
out "== 3. a analise DIZ que e forma, e nao prova =="

// Prometer mais do que ela entrega e o defeito de uma ferramenta
// assim: ela reconhece quatro desenhos e cala no resto.
nota := Regex.risk("\\\\d+")["nota"]
assert "forma" in nota
assert "e nao uma prova" in nota

out ""
out "== 4. 'safe_search' recusa ANTES de rodar =="

// Nao ha como interromper uma busca ja comecada: o motor do Python
// nao solta o GIL, entao um prazo numa thread nao para nada.
recusou := no
monitor:
    Regex.safe_search("(a+)+$", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaab")
handle RegexError as e:
    recusou := yes
    assert "travar" in e.message
    out $"   {e.message}"
assert recusou

out ""
out "== 5. e deixa passar o que e seguro =="

achado := Regex.safe_search("(?P<n>\\\\d+)", "abc 42")
assert achado["named"]["n"] is "42"
assert not achado["demorou"]
assert achado["ms"] bigger_eq 0

out ""
out "== 6. o prazo e MEDIDO, e nao interrompe =="

// A honestidade aqui e o recurso: 'demorou' diz que passou do prazo,
// e nao que a busca foi cancelada.
com_prazo_zero := Regex.safe_search("\\\\d+", "xxxxxxxxxx", ms := 0)
assert com_prazo_zero["demorou"]
assert not com_prazo_zero["matched"]

out ""
out "== 7. o que fazer com um padrao que vem de fora =="

action buscar_com_cuidado(padrao, texto):
    """Um padrao vindo de um campo ou de um arquivo de configuracao
    nunca deveria ser compilado sem passar por aqui."""
    analise := Regex.risk(padrao)
    given analise["perigoso"]:
        yield {"ok": no, "motivo": analise["motivo"]}
    yield {"ok": yes, "achado": Regex.search(padrao, texto)["value"]}

assert buscar_com_cuidado("\\\\d+", "a 42")["achado"] is "42"
assert not buscar_com_cuidado("(a+)+$", "aaa")["ok"]

out "exercicio 319 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/319_o_padrao_que_trava.df` },
  {"p": "`(a+)+$` contra trinta caracteres que não casam leva **anos**: o motor tenta todas as formas de dividir a entrada entre os dois quantificadores, e são 2ⁿ."},
  {"h3": "Os quatro desenhos clássicos"},
  {"p": "Quantificador dentro de outro, repetição aberta dentro de outra, alternância que casa a mesma coisa, classe repetida dentro de grupo repetido."},
  {"h3": "E o padrão comum NÃO é acusado"},
  {"p": "Um falso alarme aqui ensinaria a desligar a conferência inteira."},
  {"h3": "A análise DIZ que é forma, e não prova"},
  {"p": "Prometer mais do que ela entrega é o defeito de uma ferramenta assim: ela reconhece quatro desenhos e **cala no resto**."},
  {"h3": "E `safe_search` recusa ANTES de rodar"},
  {"p": "Não há como interromper uma busca já começada: o motor do Python não solta o GIL, então um prazo numa thread não para nada — ela só deixaria de esperar enquanto o processo inteiro continua travado."},
  {"h2": "320 · os validadores brasileiros, e o que eles NAO fazem"},
  {"p": "**Enunciado.** 'is_cpf' confere o FORMATO, e nao o digito verificador."},
  { code: `// Um validador que confere so a forma aceita 111.111.111-11, que nao
// e um CPF — e o cadastro descobre isso na primeira nota fiscal.

adopt Arcane.Regex as Regex

out "== 1. o que eles conferem =="

assert Regex.is_cpf("529.982.247-25")
assert Regex.is_cnpj("11.222.333/0001-81")
assert Regex.is_email("ana@exemplo.com")
assert Regex.is_ipv4("192.168.0.1")
assert Regex.is_date("2026-09-20")

out ""
out "== 2. e o que eles NAO conferem =="

// O formato esta certo, e o documento nao existe.
assert Regex.is_cpf("111.111.111-11")
out "   '111.111.111-11' passa no formato, e nao e um CPF"

action digito_verificador(numeros, peso_inicial):
    soma := 0
    peso := peso_inicial
    cycle n in numeros:
        soma += n * peso
        peso -= 1
    resto := (soma * 10) % 11
    yield 0 given resto bigger_eq 10 otherwise resto

action cpf_valido(texto):
    digitos := [int(c) cycle c in texto given c in "0123456789"]
    given len(digitos) isnt 11:
        yield no
    // Todos iguais e o caso que o formato deixa passar.
    given len(unique(digitos)) is 1:
        yield no
    primeiro := digito_verificador(digitos[0:9], 10)
    given primeiro isnt digitos[9]:
        yield no
    segundo := digito_verificador(digitos[0:10], 11)
    yield segundo is digitos[10]

assert cpf_valido("529.982.247-25")
assert not cpf_valido("111.111.111-11")
assert not cpf_valido("529.982.247-24")

out ""
out "== 3. os dois juntos =="

action conferir_cpf(texto):
    given not Regex.is_cpf(texto):
        yield "o formato nao e de CPF"
    given not cpf_valido(texto):
        yield "o digito verificador nao fecha"
    yield ""

assert conferir_cpf("529.982.247-25") is ""
assert conferir_cpf("123") is "o formato nao e de CPF"
assert conferir_cpf("111.111.111-11") is "o digito verificador nao fecha"
out $"   {conferir_cpf('111.111.111-11')}"

out ""
out "== 4. os padroes prontos, direto =="

assert Regex.test(Regex.patterns["email"], "ana@exemplo.com")
assert Regex.test(Regex.patterns["hex_color"], "#B28600")
assert Regex.test(Regex.patterns["slug"], "meu-artigo-novo")
assert not Regex.test(Regex.patterns["slug"], "Meu Artigo")

out ""
out "== 5. extrair de um texto corrido =="

steady TEXTO := "fale com ana@x.com ou bia@y.org, ou ligue (48) 99999-1234"
assert len(Regex.extract_emails(TEXTO)) is 2
assert "bia@y.org" in Regex.extract_emails(TEXTO)

out "exercicio 320 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/320_validadores.df` },
  {"p": "`is_cpf` confere o **formato**, e não o dígito verificador. Um validador de forma aceita `111.111.111-11`, que não é um CPF — e o cadastro descobre isso na primeira nota fiscal."},
  {"h3": "Os dois juntos"},
  {"p": "Formato e dígito verificador respondem coisas diferentes, e a mensagem de erro precisa dizer qual das duas falhou."},
  {"h3": "E os padrões prontos"},
  {"p": "E-mail, cor hexadecimal, slug, CEP — o catálogo existe para não haver cinco versões do mesmo padrão espalhadas pelo projeto."},
  {"h2": "321 · um analisador de log completo"},
  {"p": "**Enunciado.** juntar grupos nomeados, ancoramento, posicao e"},
  { code: `// substituicao calculada num caso que existe em todo sistema: ler o
// log, resumir e mascarar o que nao pode sair dali.

adopt Arcane.Regex as Regex

steady LOG := """2026-09-20T08:12:03 INFO  usuario=ana@exemplo.com acao=login ms=42
2026-09-20T08:12:44 ERRO  usuario=bia@exemplo.com acao=pagar ms=1203
2026-09-20T08:13:01 INFO  usuario=ana@exemplo.com acao=listar ms=17
2026-09-20T08:14:20 ERRO  usuario=caio@exemplo.com acao=pagar ms=2401
linha que nao e do formato
2026-09-20T08:15:00 AVISO usuario=ana@exemplo.com acao=sair ms=8"""

steady LINHA := "^(?P<quando>[\\\\dT:-]+) +(?P<nivel>\\\\w+) +usuario=(?P<quem>\\\\S+) +acao=(?P<acao>\\\\w+) +ms=(?P<ms>\\\\d+)$"

out "== 1. so as linhas que casam INTEIRAS =="

// Sem o ancoramento, uma linha malformada casaria pela metade e
// entraria no relatorio com campos errados.
linhas := []
cycle bruta in split(LOG, "\\n"):
    campos := Regex.named(LINHA, bruta)
    given len(keys(campos)) bigger 0:
        linhas.append(campos)

assert len(linhas) is 5
out $"   {len(linhas)} linhas lidas, uma descartada"

out ""
out "== 2. resumir por nivel =="

por_nivel := {}
cycle l in linhas:
    n := l["nivel"]
    por_nivel[n] := (por_nivel[n] ?? 0) + 1

assert por_nivel["INFO"] is 2
assert por_nivel["ERRO"] is 2
assert por_nivel["AVISO"] is 1

out ""
out "== 3. o pior tempo =="

tempos := [int(l["ms"]) cycle l in linhas]
assert max(tempos) is 2401
assert min(tempos) is 8

lentas := [l cycle l in linhas given int(l["ms"]) bigger 1000]
assert len(lentas) is 2
assert [l["acao"] cycle l in lentas] is ["pagar", "pagar"]
out "   as duas lentas sao a mesma acao"

out ""
out "== 4. quem mais aparece =="

por_pessoa := {}
cycle l in linhas:
    q := l["quem"]
    por_pessoa[q] := (por_pessoa[q] ?? 0) + 1

assert por_pessoa["ana@exemplo.com"] is 3

out ""
out "== 5. mascarar o e-mail antes de sair daqui =="

action mascarar(m):
    inteiro := m["value"]
    partes := split(inteiro, "@")
    yield partes[0][0] + "***@" + partes[1]

publico := Regex.sub_with(Regex.patterns["email"], mascarar, LOG)
assert "ana@exemplo.com" not in publico
assert "a***@exemplo.com" in publico
assert "acao=login" in publico
out "   o resto do log continua legivel"

out ""
out "== 6. e onde estavam os erros =="

posicoes := Regex.positions("^\\\\S+ +ERRO", LOG, flags := Regex.MULTILINE)
assert len(posicoes) is 2
assert posicoes[0]["linha"] is 2
assert posicoes[1]["linha"] is 4

out "exercicio 321 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/321_regex_num_log.df` },
  {"p": "Grupos nomeados, ancoramento, posição e substituição calculada num caso que existe em todo sistema."},
  {"h3": "Só as linhas que casam INTEIRAS"},
  {"p": "Sem o ancoramento, uma linha malformada casaria pela metade e entraria no relatório com campos errados."},
  {"h3": "Mascarar antes de sair daqui"},
  {"p": "O e-mail vira `a***@exemplo.com` e o resto do log continua legível."},
  {"h3": "E a linha que não casou continua visível"},
  {"p": "Um parser que descarta em silêncio esconde o dia em que o formato do banco mudou."},
  {"h2": "322 · as tres flags, e o que cada uma muda"},
  {"p": "**Enunciado.** IGNORECASE, MULTILINE e DOTALL mudam o significado do"},
  { code: `// MESMO padrao. Escolher a errada nao da erro — da uma lista com
// resultados a mais ou a menos, e ninguem confere.

adopt Arcane.Regex as Regex

steady TEXTO := """Primeira linha
segunda LINHA
terceira linha"""

out "== 1. IGNORECASE =="

assert len(Regex.findall("linha", TEXTO)) is 2
assert len(Regex.findall("linha", TEXTO, Regex.IGNORECASE)) is 3

out ""
out "== 2. MULTILINE muda o que '^' e '$' querem dizer =="

// Sem ela, '^' e o comeco do TEXTO; com ela, de cada LINHA.
assert len(Regex.findall("^\\\\w+", TEXTO)) is 1
assert len(Regex.findall("^\\\\w+", TEXTO, Regex.MULTILINE)) is 3

primeiras := Regex.findall("^\\\\w+", TEXTO, Regex.MULTILINE)
assert primeiras is ["Primeira", "segunda", "terceira"]

out ""
out "== 3. DOTALL faz o '.' atravessar a quebra =="

assert Regex.search("Primeira.*terceira", TEXTO)["matched"] is no
assert Regex.search("Primeira.*terceira", TEXTO, Regex.DOTALL)["matched"]

out ""
out "== 4. combinar duas =="

steady AS_DUAS := Regex.MULTILINE + Regex.IGNORECASE

// So com MULTILINE, a linha do meio fica de fora: ela diz "LINHA".
assert len(Regex.findall("^\\\\w+ linha$", TEXTO, Regex.MULTILINE)) is 2
// Com as duas, as tres entram.
assert len(Regex.findall("^\\\\w+ linha$", TEXTO, AS_DUAS)) is 3
out $"   so MULTILINE: 2 · com IGNORECASE: 3"

out ""
out "== 5. e o erro classico: '.*' com DOTALL num HTML =="

steady HTML := """<div>
  <p>um</p>
  <p>dois</p>
</div>"""

// Guloso e com DOTALL: engole tudo.
guloso := Regex.findall("<p>.*</p>", HTML, Regex.DOTALL)
assert len(guloso) is 1

// Preguicoso: dois.
preguicoso := Regex.findall("<p>.*?</p>", HTML, Regex.DOTALL)
assert len(preguicoso) is 2
assert preguicoso[0] is "<p>um</p>"
out "   o mesmo padrao, com e sem '?', da 1 ou 2"

out ""
out "== 6. a flag vale nas funcoes novas tambem =="

assert Regex.is_exactly("[a-z]+", "ABC", Regex.IGNORECASE)
assert Regex.named("(?P<p>^\\\\w+)", TEXTO, Regex.MULTILINE)["p"] is "Primeira"
assert len(Regex.findnamed("(?P<p>^\\\\w+)", TEXTO, Regex.MULTILINE)) is 3

out "exercicio 322 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/322_flags.df` },
  {"p": "`IGNORECASE`, `MULTILINE` e `DOTALL` mudam o significado do **mesmo** padrão. Escolher a errada não dá erro — dá uma lista com resultados a mais ou a menos, e ninguém confere."},
  {"h3": "`MULTILINE` muda o que `^` e `$` querem dizer"},
  {"p": "Sem ela, do **texto**; com ela, de cada **linha**."},
  {"h3": "`DOTALL` faz o `.` atravessar a quebra"},
  {"p": "E aí o erro clássico: `.*` com `DOTALL` num HTML engole tudo até o último fecho. O `?` é o que separa 1 de 2."},
  {"h3": "E a flag vale nas funções novas também"},
  {"p": "`is_exactly`, `named` e `findnamed` a recebem como as antigas."},
  {"h2": "323 · compilar uma vez, usar muitas"},
  {"p": "**Enunciado.** um padrao usado num laco e recompilado a cada volta."},
  { code: `// 'compile' devolve um objeto com as operacoes ja presas ao padrao —
// e a medida mostra que a diferenca e real, sem inventar numero.

adopt Arcane.Regex as Regex
adopt Arcane.Bench as Bench

steady PADRAO := "(?P<chave>\\\\w+)=(?P<valor>[^;]+)"
steady LINHA := "nome=Ana;cidade=Florianopolis;plano=pro;ativo=sim"
steady VOLTAS := 2000

out "== 1. o compilado tem TODAS as operacoes =="

// Ele tinha cinco, e quem compilava perdia 'finditer', os grupos
// nomeados e 'fullmatch' — e voltava a chamar a versao por texto,
// que e o contrario do motivo de compilar.
compilado := Regex.compile(PADRAO)
assert compilado.test(LINHA)
assert len(compilado.findall(LINHA)) is 4
assert compilado.group_names() is ["chave", "valor"]
assert compilado.named(LINHA)["chave"] is "nome"
assert compilado.pattern is PADRAO

out ""
out "== 2. os dois caminhos dao o MESMO resultado =="

action pelo_texto(n):
    total := 0
    cycle i from 1 to n:
        total += len(Regex.findall(PADRAO, LINHA))
    yield total

action pelo_compilado(n):
    total := 0
    cycle i from 1 to n:
        total += len(compilado.findall(LINHA))
    yield total

assert pelo_texto(10) is pelo_compilado(10)

out ""
out "== 3. e a medida compara um FATOR, e nao dois tempos crus =="

// 'assert a bigger b' entre dois numeros de microssegundos e um
// sorteio. O que se cobra e a razao, com folga.
com_texto := Bench.medir(pelo_texto, VOLTAS)
com_objeto := Bench.medir(pelo_compilado, VOLTAS)

razao := com_texto["ms"] / max(com_objeto["ms"], 0.0001)
out $"   texto {round(com_texto['ms'], 1)} ms, compilado {round(com_objeto['ms'], 1)} ms"

// O Python guarda um cache interno de padroes, entao a diferenca e
// pequena — e afirmar "e muito mais rapido" seria inventar. O que se
// afirma e o que se mede: o compilado nao e MAIS LENTO.
assert razao bigger 0.5

out ""
out "== 4. o que muda de verdade e a LEITURA =="

// O padrao fica com um nome, num lugar so.
steady CAMPOS := Regex.compile("(?P<chave>\\\\w+)=(?P<valor>[^;]+)")

action ler_config(linha):
    saida := {}
    cycle achado in CAMPOS.findnamed(linha):
        saida[achado["chave"]] := achado["valor"]
    yield saida

config := ler_config(LINHA)
assert config["cidade"] is "Florianopolis"
assert config["ativo"] is "sim"
assert len(keys(config)) is 4

out ""
out "== 5. e a substituicao tambem vem presa ao padrao =="

assert compilado.sub("X", LINHA) is "X;X;X;X"

out "exercicio 323 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/323_regex_e_desempenho.df` },
  {"p": "Um padrão usado num laço é recompilado a cada volta — e o Python tem um cache interno, então a diferença é pequena."},
  {"h3": "O compilado tem TODAS as operações"},
  {"p": "Ele tinha cinco, na forma que a doc recomenda para um laço: quem compilava perdia `finditer`, os grupos nomeados e `fullmatch` — e voltava a chamar a versão por texto, que é o contrário do motivo de compilar."},
  {"h3": "A medida compara um FATOR"},
  {"p": "`assert a bigger b` entre dois números de microssegundos é um sorteio. E o que se **afirma** é o que se mede: o compilado não é mais lento — e não \"é muito mais rápido\", que seria inventar."},
  {"h3": "O que muda de verdade é a LEITURA"},
  {"p": "O padrão ganha um nome, num lugar só."},
  {"h2": "324 · o texto que vem de fora nao e um padrao"},
  {"p": "**Enunciado.** montar um padrao concatenando texto de usuario e como um"},
  { code: `// ponto vira "qualquer caractere" e um parenteses vira erro de
// sintaxe. 'escape' e o equivalente do parametro de uma consulta SQL.

adopt Arcane.Regex as Regex

out "== 1. um ponto nao e um ponto =="

// 'ana.souza' como padrao casa 'anaXsouza'.
assert Regex.test("ana.souza", "anaXsouza")
assert not Regex.test(Regex.escape("ana.souza"), "anaXsouza")
assert Regex.test(Regex.escape("ana.souza"), "ana.souza")

out ""
out "== 2. e o parenteses e PIOR que quebrar =="

// '(48) 99999-1234' compila: o parenteses vira um GRUPO, e os
// parenteses somem do que se procura. O padrao passa a casar um
// telefone SEM parenteses — e nao ha erro nenhum.
assert Regex.test("(48) 99999-1234", "ligue 48 99999-1234")
assert not Regex.test(Regex.escape("(48) 99999-1234"), "ligue 48 99999-1234")
assert Regex.test(Regex.escape("(48) 99999-1234"), "ligue (48) 99999-1234")
out "   sem escapar, ele casou o telefone errado — calado"

// Um que de fato quebra: o fecho sem abertura.
quebrou := no
monitor:
    Regex.explain("sem abertura)")
handle RegexError:
    quebrou := yes
assert quebrou

out ""
out "== 3. uma busca literal dentro de um texto =="

action contem(texto, procurado):
    yield Regex.test(Regex.escape(procurado), texto)

steady CATALOGO := "cafe 3.50; leite 4.20; pao 1.00"
assert contem(CATALOGO, "3.50")
assert not contem(CATALOGO, "3x50")

out ""
out "== 4. e uma troca literal =="

// Sem escapar, '$' seria o fim da linha.
assert Regex.sub(Regex.escape("R$"), "BRL", "R$ 10 e R$ 20") is "BRL 10 e BRL 20"

out ""
out "== 5. montar um padrao COM a parte escapada =="

action comeca_com(prefixo):
    yield "^" + Regex.escape(prefixo) + "\\\\d+$"

assert Regex.test(comeca_com("NF-"), "NF-12345")
assert not Regex.test(comeca_com("NF-"), "NFX12345")
assert Regex.test(comeca_com("a.b"), "a.b99")
assert not Regex.test(comeca_com("a.b"), "aXb99")

out ""
out "== 6. e a conferencia de risco, antes de usar o que veio de fora =="

action padrao_do_usuario(texto, procurar_em):
    analise := Regex.risk(texto)
    given analise["perigoso"]:
        yield {"ok": no, "motivo": analise["motivo"]}
    yield {"ok": yes, "quantos": Regex.count(texto, procurar_em)}

assert padrao_do_usuario("\\\\d+", "a1 b2")["quantos"] is 2
assert not padrao_do_usuario("(a+)+$", "aaa")["ok"]
out "   um padrao de fora passa por 'risk' antes de rodar"

out "exercicio 324 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/324_escapar.df` },
  {"p": "Montar um padrão concatenando texto de usuário é como um ponto vira \"qualquer caractere\"."},
  {"h3": "O parênteses é PIOR que quebrar"},
  {"p": "`(48) 99999-1234` compila: o parênteses vira um **grupo**, e os parênteses somem do que se procura. O padrão passa a casar um telefone sem parênteses — e não há erro nenhum."},
  {"h3": "`escape` é o parâmetro de uma consulta SQL"},
  {"p": "O equivalente exato: o texto entra como **dado**, e não como sintaxe."},
  {"h3": "E um padrão que vem de fora passa por `risk`"},
  {"p": "Antes de rodar, e não depois."},
  {"h2": "325 · ler um formato de texto sem escrever um parser"},
  {"p": "**Enunciado.** um arquivo de configuracao em secoes. Regex nao serve"},
  { code: `// para linguagem aninhada — nao ha como casar parenteses equilibrados
// —, mas para um formato de LINHA ela e a ferramenta certa.

adopt Arcane.Regex as Regex

steady CONFIG := """# comentario no topo
[servidor]
host = 0.0.0.0
porta = 8080

[banco]
url = sqlite:///dados.db
# outro comentario
timeout = 30
pool = 5"""

steady SECAO := "^\\\\[(?P<nome>[^\\\\]]+)\\\\]$"
steady CHAVE := "^(?P<chave>\\\\w+)\\\\s*=\\\\s*(?P<valor>.+)$"

action ler_ini(texto):
    saida := {}
    atual := "geral"
    cycle linha in split(texto, "\\n"):
        limpa := trim(linha)
        given limpa is "" or startswith(limpa, "#"):
            skip
        cabecalho := Regex.named(SECAO, limpa)
        given len(keys(cabecalho)) bigger 0:
            atual := cabecalho["nome"]
            saida[atual] := {}
            skip
        par := Regex.named(CHAVE, limpa)
        given len(keys(par)) bigger 0:
            given atual not in saida:
                saida[atual] := {}
            saida[atual][par["chave"]] := trim(par["valor"])
    yield saida

out "== 1. ler =="

config := ler_ini(CONFIG)
assert keys(config) is ["servidor", "banco"]
assert config["servidor"]["porta"] is "8080"
assert config["banco"]["url"] is "sqlite:///dados.db"
assert config["banco"]["timeout"] is "30"

cycle secao in keys(config):
    out $"   [{secao}] {len(keys(config[secao]))} chave(s)"

out ""
out "== 2. o comentario nao entra =="

assert "#" not in join(",", keys(config["banco"]))

out ""
out "== 3. e o ancoramento e o que faz isso funcionar =="

// Sem '^...$', a linha '# [falso]' casaria com a de secao.
assert Regex.named(SECAO, "# [falso]") is {}
assert Regex.named(SECAO, "[servidor]")["nome"] is "servidor"

out ""
out "== 4. converter os tipos, com o padrao decidindo =="

action converter(texto):
    given Regex.is_exactly("-?\\\\d+", texto):
        yield int(texto)
    given Regex.is_exactly("-?\\\\d+\\\\.\\\\d+", texto):
        yield float(texto)
    given lower(texto) in ["sim", "nao", "yes", "no", "true", "false"]:
        yield lower(texto) in ["sim", "yes", "true"]
    yield texto

assert converter("8080") is 8080
assert converter("1.5") is 1.5
assert converter("sim") is yes
assert converter("sqlite:///dados.db") is "sqlite:///dados.db"

tipado := {}
cycle secao in keys(config):
    tipado[secao] := {}
    cycle chave in keys(config[secao]):
        tipado[secao][chave] := converter(config[secao][chave])

assert tipado["servidor"]["porta"] is 8080
assert tipado["banco"]["pool"] is 5
assert typeof(tipado["banco"]["url"]) is "String"

out ""
out "== 5. o que regex NAO faz =="

// Nao ha como casar parenteses equilibrados com expressao regular:
// isso exige contar, e uma expressao regular nao conta.
out "   formato de LINHA: regex; linguagem ANINHADA: parser"

out "exercicio 325 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/325_regex_texto_estruturado.df` },
  {"p": "Regex não serve para linguagem aninhada — não há como casar parênteses equilibrados, porque isso exige **contar**. Para um formato de LINHA ela é a ferramenta certa."},
  {"h3": "O ancoramento é o que faz isso funcionar"},
  {"p": "Sem `^...$`, a linha `# [falso]` casaria com a de seção."},
  {"h3": "E a conversão de tipo, com o padrão decidindo"},
  {"p": "Inteiro, decimal, booleano ou texto — cada um reconhecido pela forma, e não por uma tabela de nomes de campo."},
  {"h2": "326 · extrair uma tabela de um texto"},
  {"p": "**Enunciado.** o caso mais comum de regex num trabalho de dados —"},
  { code: `// transformar texto semiestruturado em linhas com colunas, e daí em
// diante deixar o quadro trabalhar.

adopt Arcane.Regex as Regex
adopt Arcane.Quadro as Q

steady EXTRATO := """20/09/2026  PIX RECEBIDO ANA SOUZA        +1.250,00
20/09/2026  COMPRA CARTAO MERCADO           -87,45
21/09/2026  PIX ENVIADO BIA LIMA            -300,00
22/09/2026  SALARIO EMPRESA LTDA          +5.400,00
22/09/2026  COMPRA CARTAO FARMACIA          -52,30
rodape que nao e lancamento"""

steady LANCAMENTO := "^(?P<data>\\\\d{2}/\\\\d{2}/\\\\d{4})\\\\s+(?P<descricao>.+?)\\\\s+(?P<sinal>[+-])(?P<valor>[\\\\d.,]+)$"

action para_numero(texto):
    "'1.250,00' vira 1250.0 — o ponto e milhar, a virgula e decimal."
    limpo := replace(replace(texto, ".", ""), ",", ".")
    yield float(limpo)

out "== 1. so as linhas que casam inteiras =="

linhas := []
cycle bruta in split(EXTRATO, "\\n"):
    campos := Regex.named(LANCAMENTO, bruta)
    given len(keys(campos)) is 0:
        skip
    valor := para_numero(campos["valor"])
    linhas.append({
            "data": campos["data"],
            "descricao": trim(campos["descricao"]),
            "valor": valor given campos["sinal"] is "+" otherwise -valor
        })

assert len(linhas) is 5
out $"   {len(linhas)} lancamentos, o rodape ficou de fora"

out ""
out "== 2. os numeros em pt-BR viraram numeros =="

assert linhas[0]["valor"] is 1250.0
assert linhas[1]["valor"] is -87.45
assert linhas[3]["valor"] is 5400.0

out ""
out "== 3. e dai em diante e um quadro =="

extrato := Q.de_vaults(linhas)
assert len(extrato) is 5
assert extrato.colunas() is ["data", "descricao", "valor"]

entradas := extrato >> onde valor bigger 0
saidas := extrato >> onde valor smaller 0
assert len(entradas) is 2
assert len(saidas) is 3

out ""
out "== 4. o saldo =="

saldo := sum([l["valor"] cycle l in linhas])
assert round(saldo, 2) is 6210.25
out $"   saldo: {round(saldo, 2)}"

out ""
out "== 5. classificar pela descricao =="

steady REGRAS := [
    ["PIX (RECEBIDO|ENVIADO)", "pix"],
    ["COMPRA CARTAO", "cartao"],
    ["SALARIO", "salario"]
]

action classificar(descricao):
    cycle regra in REGRAS:
        given Regex.test(regra[0], descricao):
            yield regra[1]
    yield "outros"

categorias := [classificar(l["descricao"]) cycle l in linhas]
assert categorias is ["pix", "cartao", "pix", "salario", "cartao"]

por_categoria := {}
cycle i from 0 to len(linhas) - 1:
    c := categorias[i]
    por_categoria[c] := round((por_categoria[c] ?? 0.0) + linhas[i]["valor"], 2)

assert por_categoria["pix"] is 950.0
assert por_categoria["cartao"] is -139.75
cycle c in keys(por_categoria):
    out $"   {c}: {por_categoria[c]}"

out ""
out "== 6. e a linha que nao casou continua visivel =="

// Um parser que descarta em silencio esconde o dia em que o formato
// do banco mudou.
ignoradas := []
cycle bruta in split(EXTRATO, "\\n"):
    given len(keys(Regex.named(LANCAMENTO, bruta))) is 0 and trim(bruta) isnt "":
        ignoradas.append(bruta)

assert len(ignoradas) is 1
out $"   ignorada: {ignoradas[0]}"

out "exercicio 326 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/326_regex_e_quadro.df` },
  {"p": "O caso mais comum de regex num trabalho de dados: transformar texto semiestruturado em linhas com colunas, e daí em diante deixar o quadro trabalhar."},
  {"h3": "Os números em pt-BR viram números"},
  {"p": "`1.250,00` — o ponto é milhar e a vírgula é decimal. Passar isso por um `float()` direto dá `1.25`, e o extrato fecha errado por mil."},
  {"h3": "E daí em diante é um quadro"},
  {"p": "`Q.de_vaults` e os verbos: `onde`, `agrupar`, `resumir`."},
  {"h3": "A linha que não casou continua visível"},
  {"p": "Um parser que descarta em silêncio esconde o dia em que o formato mudou."},
  {"h2": "327 · o mapa do modulo, e o que ele nao faz"},
  {"p": "**Enunciado.** fechar o modulo dizendo onde cada peca serve, e sendo"},
  { code: `// explicito sobre os limites. Uma ferramenta que nao nomeia o que nao
// faz e usada onde nao deve.

adopt Arcane.Regex as Regex

out "== 1. as quatro perguntas, e a funcao de cada uma =="

steady TEXTO := "pedido 101 de ana@x.com em 2026-09-20"

// "casa?"
assert Regex.test("\\\\d+", TEXTO)
// "casa INTEIRO?"
assert not Regex.is_exactly("\\\\d+", TEXTO)
// "o que casou?"
assert Regex.search("\\\\d+", TEXTO)["value"] is "101"
// "todos os que casaram?"
assert Regex.findall("\\\\d+", TEXTO) is ["101", "2026", "09", "20"]

out ""
out "== 2. e as tres formas de trocar =="

assert Regex.sub("\\\\d+", "N", TEXTO) is "pedido N de ana@x.com em N-N-N"
assert Regex.sub_with("\\\\d+", lambda m => str(len(m["value"])), TEXTO) is "pedido 3 de ana@x.com em 4-2-2"
assert Regex.replace_map("\\\\d+", {"101": "CEM E UM"}, TEXTO) is "pedido CEM E UM de ana@x.com em 2026-09-20"

out ""
out "== 3. os tres jeitos de VER =="

assert "[101]" in Regex.highlight("\\\\d+", TEXTO)
assert Regex.positions("\\\\d+", TEXTO)[0]["coluna"] is 8
assert len(Regex.explain("\\\\d{3}")) is 2

out ""
out "== 4. o que o modulo NAO faz =="

// (a) Nao valida documento: 'is_cpf' e formato.
assert Regex.is_cpf("111.111.111-11")

// (b) Nao interrompe uma busca em andamento. O motor do Python nao
// solta o GIL: um prazo numa thread nao para nada. A defesa e a
// recusa ANTES.
recusou := no
monitor:
    Regex.safe_search("(a+)+$", "aaaa")
handle RegexError:
    recusou := yes
assert recusou

// (c) 'risk' e forma, e nao prova.
assert "e nao uma prova" in Regex.risk("\\\\d+")["nota"]

// (d) Nao casa estrutura aninhada: isso exige contar, e uma
// expressao regular nao conta.
out "   parenteses equilibrados: use um parser"

out ""
out "== 5. o compilado, para o laco =="

steady CAMPO := Regex.compile("(?P<k>\\\\w+)=(?P<v>[^;]+)")
assert CAMPO.group_names() is ["k", "v"]
assert len(CAMPO.findnamed("a=1;b=2;c=3")) is 3

out ""
out "== 6. e a regra de quando NAO usar regex =="

// Procurar um texto literal nao precisa de expressao regular — e com
// ela o ponto do 'ana.souza' vira 'qualquer caractere'.
assert "ana" in TEXTO
assert Regex.test(Regex.escape("ana@x.com"), TEXTO)
out "   'in' para literal; regex para FORMA"

out "exercicio 327 ok"`, lang: 'df', title: `exercicios/53-regex-avancado/327_regex_o_mapa.df` },
  {"p": "Fechar o módulo dizendo onde cada peça serve, e sendo explícito sobre os limites. Uma ferramenta que não nomeia o que **não** faz é usada onde não deve."},
  {"h3": "As quatro perguntas"},
  {"p": "\"casa?\", \"casa inteiro?\", \"o que casou?\" e \"todos os que casaram?\" — e uma função para cada."},
  {"h3": "O que o módulo NÃO faz"},
  {"p": "Não valida documento (`is_cpf` é formato), não interrompe uma busca em andamento, `risk` é forma e não prova, e não casa estrutura aninhada."},
  {"h3": "E quando NÃO usar regex"},
  {"p": "Procurar um texto literal não precisa dela — e com ela o ponto do `ana.souza` vira \"qualquer caractere\". `in` para literal; regex para **forma**."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/53-regex-avancado/313_grupos_nomeados.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '313-o-grupo-nomeado-que-nao-chegava-ao-resultado', text: "313 · o grupo nomeado que nao chegava ao resultado", level: 2 as const }, { id: 'o-nome-chega-junto', text: "O nome chega junto", level: 3 as const }, { id: 'findnamed-le-um-log-linha-a-linha', text: "`findnamed` lê um log linha a linha", level: 3 as const }, { id: 'e-named-vem-vazio-quando-nao-ha-nomes', text: "E `named` vem vazio quando não há nomes", level: 3 as const }, { id: '314-match-ancora-so-no-comeco', text: "314 · 'match' ancora so no COMECO", level: 2 as const }, { id: 'fullmatch-casa-a-string-inteira', text: "`fullmatch` casa a string inteira", level: 3 as const }, { id: 'o-resultado-vazio-tem-as-mesmas-chaves', text: "O resultado vazio tem as MESMAS chaves", level: 3 as const }, { id: 'e-faz-o-mesmo', text: "E `^...$` faz o mesmo", level: 3 as const }, { id: '315-a-troca-que-calcula', text: "315 · a troca que CALCULA", level: 2 as const }, { id: 'a-acao-recebe-o-mesmo-vault-de-search', text: "A ação recebe o mesmo vault de `search`", level: 3 as const }, { id: 'devolver-void-nao-troca', text: "Devolver `void` NÃO troca", level: 3 as const }, { id: 'e-replacemap-deixa-o-que-nao-esta-na-tabela', text: "E `replace_map` deixa o que não está na tabela", level: 3 as const }, { id: '316-partir-sem-perder-o-separador', text: "316 · partir sem perder o separador", level: 2 as const }, { id: 'e-e-por-isso-que-ele-reconstroi', text: "E é por isso que ele reconstrói", level: 3 as const }, { id: 'between-recorta-entre-marcas', text: "`between` recorta entre marcas", level: 3 as const }, { id: '317-depurar-um-padrao', text: "317 · depurar um padrao", level: 2 as const }, { id: 'highlight-marca', text: "`highlight` marca", level: 3 as const }, { id: 'positions-responde-em-linha-e-coluna', text: "`positions` responde em linha e coluna", level: 3 as const }, { id: '318-ler-uma-expressao-regular', text: "318 · ler uma expressao regular", level: 2 as const }, { id: 'pedaco-a-pedaco', text: "Pedaço a pedaço", level: 3 as const }, { id: 'ele-distingue-o-preguicoso-e-a-classe-negada', text: "Ele distingue o preguiçoso e a classe negada", level: 3 as const }, { id: 'e-um-padrao-quebrado-nao-e-explicado', text: "E um padrão quebrado NÃO é explicado", level: 3 as const }, { id: '319-o-padrao-que-trava-o-processo', text: "319 · o padrao que trava o processo", level: 2 as const }, { id: 'os-quatro-desenhos-classicos', text: "Os quatro desenhos clássicos", level: 3 as const }, { id: 'e-o-padrao-comum-nao-e-acusado', text: "E o padrão comum NÃO é acusado", level: 3 as const }, { id: 'a-analise-diz-que-e-forma-e-nao-prova', text: "A análise DIZ que é forma, e não prova", level: 3 as const }, { id: 'e-safesearch-recusa-antes-de-rodar', text: "E `safe_search` recusa ANTES de rodar", level: 3 as const }, { id: '320-os-validadores-brasileiros-e-o-que-eles-nao-fazem', text: "320 · os validadores brasileiros, e o que eles NAO fazem", level: 2 as const }, { id: 'os-dois-juntos', text: "Os dois juntos", level: 3 as const }, { id: 'e-os-padroes-prontos', text: "E os padrões prontos", level: 3 as const }, { id: '321-um-analisador-de-log-completo', text: "321 · um analisador de log completo", level: 2 as const }, { id: 'so-as-linhas-que-casam-inteiras', text: "Só as linhas que casam INTEIRAS", level: 3 as const }, { id: 'mascarar-antes-de-sair-daqui', text: "Mascarar antes de sair daqui", level: 3 as const }, { id: 'e-a-linha-que-nao-casou-continua-visivel', text: "E a linha que não casou continua visível", level: 3 as const }, { id: '322-as-tres-flags-e-o-que-cada-uma-muda', text: "322 · as tres flags, e o que cada uma muda", level: 2 as const }, { id: 'multiline-muda-o-que-e-querem-dizer', text: "`MULTILINE` muda o que `^` e `$` querem dizer", level: 3 as const }, { id: 'dotall-faz-o-atravessar-a-quebra', text: "`DOTALL` faz o `.` atravessar a quebra", level: 3 as const }, { id: 'e-a-flag-vale-nas-funcoes-novas-tambem', text: "E a flag vale nas funções novas também", level: 3 as const }, { id: '323-compilar-uma-vez-usar-muitas', text: "323 · compilar uma vez, usar muitas", level: 2 as const }, { id: 'o-compilado-tem-todas-as-operacoes', text: "O compilado tem TODAS as operações", level: 3 as const }, { id: 'a-medida-compara-um-fator', text: "A medida compara um FATOR", level: 3 as const }, { id: 'o-que-muda-de-verdade-e-a-leitura', text: "O que muda de verdade é a LEITURA", level: 3 as const }, { id: '324-o-texto-que-vem-de-fora-nao-e-um-padrao', text: "324 · o texto que vem de fora nao e um padrao", level: 2 as const }, { id: 'o-parenteses-e-pior-que-quebrar', text: "O parênteses é PIOR que quebrar", level: 3 as const }, { id: 'escape-e-o-parametro-de-uma-consulta-sql', text: "`escape` é o parâmetro de uma consulta SQL", level: 3 as const }, { id: 'e-um-padrao-que-vem-de-fora-passa-por-risk', text: "E um padrão que vem de fora passa por `risk`", level: 3 as const }, { id: '325-ler-um-formato-de-texto-sem-escrever-um-parser', text: "325 · ler um formato de texto sem escrever um parser", level: 2 as const }, { id: 'o-ancoramento-e-o-que-faz-isso-funcionar', text: "O ancoramento é o que faz isso funcionar", level: 3 as const }, { id: 'e-a-conversao-de-tipo-com-o-padrao-decidindo', text: "E a conversão de tipo, com o padrão decidindo", level: 3 as const }, { id: '326-extrair-uma-tabela-de-um-texto', text: "326 · extrair uma tabela de um texto", level: 2 as const }, { id: 'os-numeros-em-pt-br-viram-numeros', text: "Os números em pt-BR viram números", level: 3 as const }, { id: 'e-dai-em-diante-e-um-quadro', text: "E daí em diante é um quadro", level: 3 as const }, { id: 'a-linha-que-nao-casou-continua-visivel', text: "A linha que não casou continua visível", level: 3 as const }, { id: '327-o-mapa-do-modulo-e-o-que-ele-nao-faz', text: "327 · o mapa do modulo, e o que ele nao faz", level: 2 as const }, { id: 'as-quatro-perguntas', text: "As quatro perguntas", level: 3 as const }, { id: 'o-que-o-modulo-nao-faz', text: "O que o módulo NÃO faz", level: 3 as const }, { id: 'e-quando-nao-usar-regex', text: "E quando NÃO usar regex", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"53 · Regex avançado"}
      description={"15 exercícios: grupos nomeados, âncoras, troca que calcula e risco."}
      href={"/docs/exercicios/53-regex-avancado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
