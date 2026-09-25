// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "52 · Estruturas e ponteiros",
  description: "15 exercícios: layout binário com nome, janela sem cópia e ponteiro.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Sistemas e arquitetura** · layout binário com nome, janela sem cópia e ponteiro · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 52`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[298](#298-o-layout-que-tem-nome)", "**o layout que tem NOME**", "'Arcane.Bytes' empacota por FORMATO, e o resultado e"], ["[299](#299-o-enchimento-que-o-c-insere)", "**o enchimento que o C insere**", "um u32 comeca num multiplo de 4; um u64, num multiplo de"], ["[300](#300-a-janela-nao-copia)", "**a janela nao COPIA**", "copiar um registro de 4 KB para ler um campo de 2 bytes e"], ["[301](#301-andar-por-elemento-e-nao-por-byte)", "**andar por ELEMENTO, e nao por byte**", "'p + 1' num u32* do C anda QUATRO bytes. Andar um byte e"], ["[302](#302-o-ponteiro-que-nao-aponta-para-nada)", "**o ponteiro que nao aponta para nada**", "ha duas formas de um ponteiro nao valer nada, e elas sao"], ["[303](#303-ler-um-formato-binario-de-verdade)", "**ler um formato binario de verdade**", "montar e reler um arquivo com cabecalho, tabela de"], ["[304](#304-os-mesmos-bytes-dois-nomes)", "**os mesmos bytes, dois nomes**", "numa uniao todos os campos moram no deslocamento zero, e"], ["[305](#305-um-campo-com-varias-posicoes)", "**um campo com varias posicoes**", "'rgba' e quatro bytes, e nao quatro campos. Declarar a"], ["[306](#306-as-seis-recusas-do-layout)", "**as seis recusas do layout**", "cada recusa existe porque a alternativa e um numero"], ["[307](#307-um-protocolo-de-linha-montado-e-lido)", "**um protocolo de linha, montado e lido**", "quase todo protocolo binario tem a mesma forma —"], ["[308](#308-o-bloco-e-o-que-ele-promete)", "**o bloco, e o que ele promete**", "'liberar()' nao devolve memoria ao sistema — quem faz"], ["[309](#309-gravar-e-reler-do-disco)", "**gravar e reler do disco**", "um molde so vale se o arquivo que ele produz for lido de"], ["[310](#310-quando-usar-cada-um-dos-tres)", "**quando usar cada um dos tres**", "'Arcane.Bytes' empacota por formato, 'Arcane.Estrutura'"], ["[311](#311-gravar-bytes-num-arquivo)", "**gravar bytes num arquivo**", "a linguagem sabia PRODUZIR bytes — 'Arcane.Bytes',"], ["[312](#312-um-formato-completo-do-zero-ao-disco)", "**um formato completo, do zero ao disco**", "juntar tudo — molde, alinhamento, janela, ponteiro,"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "298 · o layout que tem NOME"},
  {"p": "**Enunciado.** 'Arcane.Bytes' empacota por FORMATO, e o resultado e"},
  { code: `// posicional — 'dados[3]' tres meses depois nao diz nada. Um molde tem
// campos nomeados, e cobra a ordem dos bytes: sem ela, o mesmo arquivo
// lido em duas maquinas da dois valores, e nenhuma das duas falha.

adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as By

steady Cabecalho := Est.definir("Cabecalho", [
        ["magia", "u32"],
        ["versao", "u16"],
        ["registros", "u16"]
    ], ordem := "rede")

out "== 1. o molde sabe o proprio layout =="

assert Cabecalho.tamanho is 8
assert Cabecalho.deslocamento("magia") is 0
assert Cabecalho.deslocamento("versao") is 4
assert Cabecalho.deslocamento("registros") is 6

cycle campo in Cabecalho.mapa():
    out $"   +{campo['deslocamento']}  {campo['campo']} ({campo['tipo']}, {campo['bytes']} bytes)"

out ""
out "== 2. empacotar e ler de volta =="

bloco := Cabecalho.empacotar({"magia": 1145128264, "versao": 2, "registros": 7})
assert len(bloco) is 8
lido := Cabecalho.ler(bloco)
assert lido["versao"] is 2
assert lido["registros"] is 7

out ""
out "== 3. a ordem dos bytes muda o ARQUIVO =="

steady UmNumero := [["n", "u32"]]
rede := Est.definir("A", UmNumero, ordem := "rede").empacotar({"n": 1})
intel := Est.definir("A", UmNumero, ordem := "intel").empacotar({"n": 1})

assert By.hex(rede.bytes()) is "00000001"
assert By.hex(intel.bytes()) is "01000000"
out $"   rede {By.hex(rede.bytes())}  intel {By.hex(intel.bytes())}"

out ""
out "== 4. uma ordem que nao existe e recusada =="

recusou := no
monitor:
    Est.definir("A", UmNumero, ordem := "qualquer")
handle LayoutError as e:
    recusou := yes
    assert "ordem" in e.message
assert recusou

out ""
out "== 5. o que falta vai ZERADO =="

so_versao := Cabecalho.empacotar({"versao": 9})
assert Cabecalho.ler(so_versao)["magia"] is 0
assert Cabecalho.ler(so_versao)["versao"] is 9

out "exercicio 298 ok"`, lang: 'df', title: `exercicios/52-estruturas/298_molde_e_ordem.df` },
  {"p": "`Arcane.Bytes` empacota por **formato**, e o resultado é posicional — `dados[3]` três meses depois não diz nada. Um molde tem campos nomeados, e cobra a ordem dos bytes."},
  {"h3": "A ordem dos bytes é obrigatória"},
  {"p": "Sem ela, o mesmo arquivo lido em duas máquinas dá dois valores, e nenhuma das duas falha. `\"rede\"` é big-endian — o de todo formato de arquivo e todo protocolo."},
  {"h3": "O molde sabe o próprio layout"},
  {"p": "`tamanho`, `deslocamento(campo)` e `mapa()` respondem sem contar à mão — e uma conta à mão envelhece quando alguém acrescenta um campo no meio."},
  {"h3": "E o que falta vai zerado"},
  {"p": "Um registro nasce completo; o que não foi escrito é zero, e não lixo."},
  {"h2": "299 · o enchimento que o C insere"},
  {"p": "**Enunciado.** um u32 comeca num multiplo de 4; um u64, num multiplo de"},
  { code: `// 8. Ignorar isso e o que faz o mesmo '.struct' sair com 12 bytes de
// um lado e 16 do outro — e o arquivo ser lido errado do byte 1 em
// diante, sem nenhum erro.

adopt Arcane.Estrutura as Est

steady CAMPOS := [["a", "u8"], ["b", "u32"]]

steady Alinhado := Est.definir("Pacote", CAMPOS)
steady Junto := Est.definir("Pacote", CAMPOS, empacotado := yes)

out "== 1. alinhado: tres bytes de enchimento =="

assert Alinhado.deslocamento("a") is 0
assert Alinhado.deslocamento("b") is 4
assert Alinhado.tamanho is 8
assert Alinhado.enchimento() is 3

out ""
out "== 2. empacotado: nenhum =="

assert Junto.deslocamento("b") is 1
assert Junto.tamanho is 5
assert Junto.enchimento() is 0

out ""
out "== 3. o REGISTRO INTEIRO tambem e alinhado =="

// Sem isso, um cluster deles sai torto a partir do segundo.
steady Torto := Est.definir("T", [["a", "u32"], ["b", "u8"]])
assert Torto.tamanho is 8
assert Torto.enchimento() is 3
out "   4 + 1 = 5, e o tamanho e 8"

out ""
out "== 4. e e isso que faz um cluster fechar =="

steady Par := Est.definir("Par", [["a", "u16"], ["b", "u16"]])
bloco := Est.bloco(Par.tamanho * 3)
cycle i from 0 to 2:
    Par.escrever(bloco, {"a": i, "b": i * 10}, i * Par.tamanho)

cycle i from 0 to 2:
    lido := Par.ler(bloco, i * Par.tamanho)
    assert lido["a"] is i
    assert lido["b"] is i * 10

out ""
out "== 5. o alinhamento e o do MAIOR campo =="

assert Est.alinhamento_de(Alinhado) is 4
assert Est.alinhamento_de(Est.definir("G", [["x", "f64"], ["y", "u8"]])) is 8
assert Est.tamanho_de("u32") is 4
assert Est.tamanho_de("f64") is 8
assert Est.tamanho_de(Alinhado) is 8

out ""
out "== 6. a lista de tipos e a mesma do Arcane.Bytes =="

// Duas listas divergiriam, e o mesmo 'u32' teria dois tamanhos.
assert "u32" in Est.tipos()
assert "f64" in Est.tipos()
assert "bool" in Est.tipos()
assert len(Est.tipos()) is 11

out "exercicio 299 ok"`, lang: 'df', title: `exercicios/52-estruturas/299_alinhamento.df` },
  {"p": "Um `u32` começa num múltiplo de 4; um `u64`, num múltiplo de 8. Ignorar isso é o que faz o mesmo `.struct` sair com 12 bytes de um lado e 16 do outro — e o arquivo ser lido errado do byte 1 em diante, sem nenhum erro."},
  {"h3": "Alinhado × empacotado"},
  {"p": "`empacotado := yes` recusa o enchimento e cobra os deslocamentos. `enchimento()` diz quantos bytes são só alinhamento."},
  {"h3": "O REGISTRO INTEIRO também é alinhado"},
  {"p": "Ao maior campo. Sem isso, um cluster deles sai torto a partir do segundo — e o segundo registro é lido metade num, metade no outro."},
  {"h3": "E a lista de tipos é a mesma do `Arcane.Bytes`"},
  {"p": "Duas listas divergiriam, e o mesmo `u32` teria dois tamanhos."},
  {"h2": "300 · a janela nao COPIA"},
  {"p": "**Enunciado.** copiar um registro de 4 KB para ler um campo de 2 bytes e"},
  { code: `// o que faz um parser de arquivo grande levar minutos. A janela le e
// escreve NO BLOCO — e a prova disso e reler por outro caminho.

adopt Arcane.Estrutura as Est

steady Registro := Est.definir("Registro", [
        ["id", "u32"],
        ["preco", "f32"],
        ["quantidade", "u16"],
        ["ativo", "bool"]
    ], ordem := "rede")

arquivo := Est.bloco(Registro.tamanho * 3)

steady CATALOGO := [
    {"id": 101, "preco": 32.5, "quantidade": 4, "ativo": yes},
    {"id": 102, "preco": 9.0, "quantidade": 12, "ativo": yes},
    {"id": 103, "preco": 240.0, "quantidade": 0, "ativo": no}
]

cycle i from 0 to 2:
    Registro.escrever(arquivo, CATALOGO[i], i * Registro.tamanho)

out "== 1. percorrer o arquivo inteiro =="

linhas := Est.janelas(arquivo, Registro)
assert len(linhas) is 3
assert [l.ler("id") cycle l in linhas] is [101, 102, 103]

cycle l in linhas:
    out $"   #{l.ler('id')}  R$ {l.ler('preco')}  x{l.ler('quantidade')}"

out ""
out "== 2. escrever na janela muda O BLOCO =="

linhas[2].escrever("quantidade", 7)
linhas[2]["ativo"] := yes

// A prova: reler do bloco, por outro caminho.
conferindo := Registro.ler(arquivo, 2 * Registro.tamanho)
assert conferindo["quantidade"] is 7
assert conferindo["ativo"] is yes

out ""
out "== 3. o vault da janela e uma COPIA =="

foto := linhas[0].vault()
linhas[0].escrever("quantidade", 99)
assert foto["quantidade"] is 4
assert linhas[0].ler("quantidade") is 99
out "   a copia nao acompanha"

out ""
out "== 4. proxima anda UM registro =="

primeira := Est.janela(arquivo, Registro)
assert primeira.deslocamento() is 0
assert primeira.proxima().ler("id") is 102
assert primeira.proxima().deslocamento() is Registro.tamanho

out ""
out "== 5. pedir mais do que cabe e erro, com a conta =="

estourou := no
monitor:
    Est.janelas(arquivo, Registro, quantos := 10)
handle BufferOverflowError as e:
    estourou := yes
    assert "cabem 3" in e.message
    out $"   {e.message}"
assert estourou

out ""
out "== 6. um campo que nao existe SUGERE o parecido =="

sugeriu := no
monitor:
    linhas[0].ler("quantidade_")
handle LayoutError as e:
    sugeriu := yes
    assert "quantidade" in e.message
assert sugeriu

out "exercicio 300 ok"`, lang: 'df', title: `exercicios/52-estruturas/300_janela.df` },
  {"p": "Copiar um registro de 4 KB para ler um campo de 2 bytes é o que faz um parser de arquivo grande levar minutos."},
  {"h3": "Escrever na janela muda O BLOCO"},
  {"p": "E a prova é reler por outro caminho. Se ela copiasse, este teste passaria em silêncio com o valor velho."},
  {"h3": "O vault da janela é uma cópia"},
  {"p": "`vault()` existe para quem quer a foto; a partir dali ela não acompanha mais."},
  {"h3": "Pedir mais do que cabe é erro, com a conta"},
  {"p": "*\"cabem 3 registro(s) aqui, e foram pedidos 10\"* — o número na mensagem é o que dispensa abrir a calculadora."},
  {"h3": "E um campo que não existe SUGERE o parecido"},
  {"p": "O nome certo costuma estar a um caractere de distância, e a lista inteira fica na nota."},
  {"h2": "301 · andar por ELEMENTO, e nao por byte"},
  {"p": "**Enunciado.** 'p + 1' num u32* do C anda QUATRO bytes. Andar um byte e"},
  { code: `// um indice, nao um ponteiro — e e a conta que quem escreve C faz o
// tempo todo.

adopt Arcane.Estrutura as Est

numeros := Est.bloco(16)
steady p := Est.ponteiro(numeros, "u32")

out "== 1. escrever por ponteiro =="

cycle i from 0 to 3:
    p.mais(i).escrever((i + 1) * 100)

assert p.cluster(4) is [100, 200, 300, 400]

out ""
out "== 2. o passo e o TAMANHO DO TIPO =="

assert p.passo() is 4
assert p.mais(1).endereco() is 4
assert p.mais(3).endereco() is 12
assert p.tipo() is "u32"

steady q := Est.ponteiro(numeros, "u8")
assert q.passo() is 1
assert q.mais(1).endereco() is 1

out ""
out "== 3. distancia, tambem em elementos =="

assert p.mais(3).distancia(p) is 3
assert p.distancia(p.mais(2)) is -2

// Entre tipos diferentes nao ha conta possivel.
recusou := no
monitor:
    p.distancia(q)
handle LayoutError as e:
    recusou := yes
    assert "distancia" in e.message
assert recusou

out ""
out "== 4. o cast reinterpreta o MESMO endereco =="

// 100 em big-endian e 00 00 00 64.
assert p.como("u8").cluster(4) is [0, 0, 0, 100]
assert p.como("u16").mais(1).ler() is 100
out "   os mesmos quatro bytes, tres leituras"

out ""
out "== 5. sair do bloco e erro =="

fora := no
monitor:
    p.mais(4).ler()
handle BufferOverflowError as e:
    fora := yes
    assert "byte 16" in e.message
assert fora

out ""
out "== 6. e um valor fora da faixa do tipo tambem =="

// A faixa sai do TIPO DECLARADO, e nao do formato interno do Python.
faixa := no
monitor:
    Est.ponteiro(numeros, "u8").escrever(300)
handle BufferOverflowError as e:
    faixa := yes
    assert "0 a 255" in e.message
    out $"   {e.message}"
assert faixa

out "exercicio 301 ok"`, lang: 'df', title: `exercicios/52-estruturas/301_ponteiro.df` },
  {"p": "`p + 1` num `u32*` do C anda **quatro** bytes. Andar um byte é um índice, não um ponteiro."},
  {"h3": "O passo é o tamanho do tipo"},
  {"p": "E `distancia` responde na mesma unidade. Entre tipos diferentes ela é recusada: a conta é em elementos, e dois tipos têm tamanhos diferentes."},
  {"h3": "O cast reinterpreta o MESMO endereço"},
  {"p": "Os mesmos quatro bytes, três leituras — é o que uma união faz, com outra sintaxe."},
  {"h3": "E a faixa vem do TIPO declarado"},
  {"p": "*\"um u8 vai de 0 a 255\"*, e não `'B' format requires 0 <= number <= 255`: quem escreveu `u8` não tem como ligar uma coisa à outra."},
  {"h2": "302 · o ponteiro que nao aponta para nada"},
  {"p": "**Enunciado.** ha duas formas de um ponteiro nao valer nada, e elas sao"},
  { code: `// diferentes. O NULO tem endereco zero — le-lo seria a falha de
// segmentacao classica. O PENDURADO aponta para um bloco que declarou
// o fim, e o espaco pode ja ser de outra pessoa.

adopt Arcane.Estrutura as Est

out "== 1. o nulo =="

nulo := Est.nulo()
assert nulo.e_nulo()

leu := no
monitor:
    nulo.ler()
handle NullPointerError as e:
    leu := yes
    assert "nulo" in e.message
assert leu

escreveu := no
monitor:
    nulo.escrever(1)
handle NullPointerError:
    escreveu := yes
assert escreveu

out ""
out "== 2. e ele NAO e o 'void' da linguagem =="

// 'NullReferenceError' fala de um void; aqui o endereco existe.
assert nulo is not void
assert typeof(nulo) is not "Void"

out ""
out "== 3. o pendurado =="

morto := Est.bloco(8)
orfao := Est.ponteiro(morto, "u32")
orfao.escrever(7)
assert orfao.ler() is 7
assert not orfao.e_nulo()

assert morto.liberar() is yes
assert orfao.e_nulo()

pendurado := no
monitor:
    orfao.ler()
handle DanglingPointerError as e:
    pendurado := yes
    assert "liberado" in e.message
assert pendurado

out ""
out "== 4. liberar e IDEMPOTENTE =="

// Um 'liberar' no 'defer' e no caminho de erro nao pode virar erro: a
// disciplina atrapalharia em vez de ajudar.
assert morto.liberar() is no
assert len(morto) is 0

out ""
out "== 5. o ponteiro SEGURA o bloco =="

// Com referencia fraca, 'Est.ponteiro(Est.bloco(8), "u32")' nasceria
// pendurado — o bloco temporario morreria assim que a chamada
// voltasse. Um ponteiro cuja validade depende de a expressao ter sido
// guardada numa variavel e uma armadilha.
temporario := Est.ponteiro(Est.bloco(8), "u32")
assert not temporario.e_nulo()
temporario.escrever(42)
assert temporario.ler() is 42
out "   o bloco sem nome continua vivo"

out ""
out "== 6. a familia inteira =="

action classe(acao):
    monitor:
        acao()
    handle Error as e:
        yield e.type
    yield "nenhum"

assert classe(lambda => nulo.ler()) is "NullPointerError"
assert classe(lambda => orfao.ler()) is "DanglingPointerError"
assert classe(lambda => Est.ponteiro(Est.bloco(2), "u32").ler()) is "BufferOverflowError"

// E 'handle LayoutError' pega as tres.
action pela_base(acao):
    monitor:
        acao()
    handle LayoutError:
        yield yes
    yield no

assert pela_base(lambda => nulo.ler())
assert pela_base(lambda => orfao.ler())

out "exercicio 302 ok"`, lang: 'df', title: `exercicios/52-estruturas/302_bloco_e_pendurado.df` },
  {"p": "Há duas formas de um ponteiro não valer nada, e elas são diferentes."},
  {"h3": "O NULO tem endereço zero"},
  {"p": "Lê-lo seria a falha de segmentação clássica. E ele não é o `void` da linguagem: `NullReferenceError` fala de um `void`; aqui o endereço existe."},
  {"h3": "O PENDURADO aponta para um bloco liberado"},
  {"p": "O endereço continua na mão de alguém, e o espaço pode já ser de outra pessoa."},
  {"h3": "`liberar` é idempotente"},
  {"p": "Um `liberar` no `defer` e no caminho de erro não pode virar erro: a disciplina atrapalharia em vez de ajudar."},
  {"h3": "E o ponteiro SEGURA o bloco"},
  {"p": "Com referência fraca, `Est.ponteiro(Est.bloco(8), \"u32\")` nasceria pendurado — o bloco temporário morreria assim que a chamada voltasse. Um ponteiro cuja validade depende de a expressão ter sido guardada numa variável é uma armadilha."},
  {"h2": "303 · ler um formato binario de verdade"},
  {"p": "**Enunciado.** montar e reler um arquivo com cabecalho, tabela de"},
  { code: `// indices e registros — o desenho de quase todo formato que existe.
// O ponto e que nada aqui precisa de FFI.

adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as By

steady MAGIA := 1145128264
steady VERSAO := 1

steady Cabecalho := Est.definir("Cabecalho", [
        ["magia", "u32"],
        ["versao", "u16"],
        ["quantos", "u16"]
    ], ordem := "rede")

steady Indice := Est.definir("Indice", [
        ["id", "u32"],
        ["deslocamento", "u32"]
    ], ordem := "rede")

steady Item := Est.definir("Item", [
        ["id", "u32"],
        ["preco_centavos", "u32"],
        ["estoque", "u16"]
    ], ordem := "rede")

steady ITENS := [
    {"id": 101, "preco_centavos": 3250, "estoque": 4},
    {"id": 102, "preco_centavos": 900, "estoque": 12},
    {"id": 103, "preco_centavos": 24000, "estoque": 0}
]

out "== 1. montar o arquivo =="

steady QUANTOS := len(ITENS)
steady INICIO_INDICE := Cabecalho.tamanho
steady INICIO_ITENS := INICIO_INDICE + Indice.tamanho * QUANTOS

arquivo := Est.bloco(INICIO_ITENS + Item.tamanho * QUANTOS)

Cabecalho.escrever(arquivo, {"magia": MAGIA, "versao": VERSAO,
        "quantos": QUANTOS})

cycle i from 0 to QUANTOS - 1:
    onde := INICIO_ITENS + i * Item.tamanho
    Item.escrever(arquivo, ITENS[i], onde)
    Indice.escrever(arquivo, {"id": ITENS[i]["id"], "deslocamento": onde},
        INICIO_INDICE + i * Indice.tamanho)

out $"   {len(arquivo)} bytes, comecando com {By.hex(arquivo.bytes()[0:4])}"

out ""
out "== 2. reler, como quem recebeu o arquivo =="

cabeca := Cabecalho.ler(arquivo)
assert cabeca["magia"] is MAGIA
assert cabeca["versao"] is VERSAO
assert cabeca["quantos"] is QUANTOS

out ""
out "== 3. procurar pelo indice, sem varrer os itens =="

action achar(dados, id_procurado):
    quantos := Cabecalho.ler(dados)["quantos"]
    candidatas := Est.janelas(dados, Indice, quantos := quantos,
        deslocamento := INICIO_INDICE)
    cycle entrada in candidatas:
        given entrada.ler("id") is id_procurado:
            yield Item.ler(dados, entrada.ler("deslocamento"))
    yield void

achado := achar(arquivo, 102)
assert achado["preco_centavos"] is 900
assert achar(arquivo, 999) is void
out $"   102 -> {achado}"

out ""
out "== 4. mudar o estoque NO LUGAR =="

entradas := Est.janelas(arquivo, Indice, quantos := QUANTOS,
    deslocamento := INICIO_INDICE)
alvo := Est.janela(arquivo, Item, entradas[2].ler("deslocamento"))
alvo["estoque"] := 25

assert achar(arquivo, 103)["estoque"] is 25

out ""
out "== 5. um arquivo curto demais e recusado =="

curto := Est.bloco(4)
recusou := no
monitor:
    Cabecalho.ler(curto)
handle BufferOverflowError as e:
    recusou := yes
    assert "8 byte" in e.message
assert recusou

out ""
out "== 6. e a magia errada e problema de quem le =="

// O modulo nao inventa validacao de formato: quem conhece o formato e
// quem escreve o leitor.
falso := Cabecalho.empacotar({"magia": 0, "versao": 1, "quantos": 0})
assert Cabecalho.ler(falso)["magia"] isnt MAGIA

out "exercicio 303 ok"`, lang: 'df', title: `exercicios/52-estruturas/303_ler_um_formato.df` },
  {"p": "Cabeçalho, tabela de índices e registros — o desenho de quase todo formato que existe. E nada aqui precisa de FFI."},
  {"h3": "Procurar pelo índice, sem varrer os itens"},
  {"p": "É o motivo de o índice existir: a tabela é pequena e ordenada, e os registros podem ser muitos."},
  {"h3": "Mudar o estoque no lugar"},
  {"p": "A janela escreve direto no bloco, e a releitura confirma."},
  {"h3": "E a magia errada é problema de quem lê"},
  {"p": "O módulo não inventa validação de formato: quem conhece o formato é quem escreve o leitor."},
  {"h2": "304 · os mesmos bytes, dois nomes"},
  {"p": "**Enunciado.** numa uniao todos os campos moram no deslocamento zero, e"},
  { code: `// o tamanho e o do maior. Escrever um e ler outro devolve a
// reinterpretacao dos bytes — que e o ponto dela, e tambem o que a
// torna perigosa quando o tipo escrito nao e registrado em lugar
// nenhum.

adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as By

steady Valor := Est.uniao("Valor", [
        ["inteiro", "u32"],
        ["flutuante", "f32"]
    ], ordem := "rede")

out "== 1. todos no mesmo lugar =="

assert Valor.deslocamento("inteiro") is 0
assert Valor.deslocamento("flutuante") is 0
assert Valor.tamanho is 4

out ""
out "== 2. escrever um, ler o outro =="

caixa := Est.bloco(4)
Valor.escrever(caixa, {"flutuante": 1.0})

// 1.0 em IEEE 754 de 32 bits e 0x3F800000.
assert Valor.ler(caixa)["inteiro"] is 1065353216
assert By.hex(caixa.bytes()) is "3f800000"
out $"   1.0 como u32: {Valor.ler(caixa)['inteiro']}"

out ""
out "== 3. e o caminho de volta =="

Valor.escrever(caixa, {"inteiro": 1065353216})
assert Valor.ler(caixa)["flutuante"] is 1.0

out ""
out "== 4. o tamanho e o do MAIOR =="

steady Grande := Est.uniao("Grande", [
        ["curto", "u8"],
        ["longo", "f64"]
    ])
assert Grande.tamanho is 8

out ""
out "== 5. ler bits de um campo =="

// Um campo de flags: oito booleanos num byte.
steady Flags := Est.definir("Flags", [["bits", "u8"]])
f := Flags.empacotar({"bits": 165})

action ligado(valor, posicao):
    yield(valor ~/ (2 ** posicao)) % 2 is 1

b := Flags.ler(f)["bits"]
assert ligado(b, 0)
assert not ligado(b, 1)
assert ligado(b, 2)
assert ligado(b, 5)
assert ligado(b, 7)
out $"   {By.bits(f.bytes())}"

out ""
out "== 6. e o Arcane.Bytes le o mesmo bloco =="

// Os dois modulos falam dos mesmos bytes: um por nome, o outro por
// formato.
assert By.desempacotar(">u32", caixa.bytes())[0] is 1065353216

out "exercicio 304 ok"`, lang: 'df', title: `exercicios/52-estruturas/304_uniao_e_bits.df` },
  {"p": "Numa união todos os campos moram no deslocamento zero, e o tamanho é o do maior."},
  {"h3": "Escrever um, ler o outro"},
  {"p": "`1.0` em IEEE 754 de 32 bits é `0x3F800000` — e ler como `u32` devolve exatamente isso. É o ponto da união, e também o que a torna perigosa quando o tipo escrito não é registrado em lugar nenhum."},
  {"h3": "Ler bits de um campo"},
  {"p": "Oito booleanos num byte: o que um campo de flags é, em todo protocolo binário."},
  {"h3": "E os dois módulos falam dos mesmos bytes"},
  {"p": "`Arcane.Bytes` por formato, `Arcane.Estrutura` por nome."},
  {"h2": "305 · um campo com varias posicoes"},
  {"p": "**Enunciado.** 'rgba' e quatro bytes, e nao quatro campos. Declarar a"},
  { code: `// quantidade no campo e o que faz o molde saber o tamanho do registro
// sem contar a mao — e o que faz a escrita com a quantidade errada ser
// recusada.

adopt Arcane.Estrutura as Est

// O maior valor de um u8, nomeado: onze aparicoes do mesmo 255 sao
// onze lugares para errar quando o tipo mudar.
steady CHEIO := 255

steady Pixel := Est.definir("Pixel", [
        ["rgba", "u8", 4]
    ])

steady Vetor := Est.definir("Vetor", [
        ["nome", "u8", 4],
        ["xyz", "f32", 3]
    ], ordem := "rede")

out "== 1. o tamanho vem da quantidade =="

assert Pixel.tamanho is 4
assert Vetor.tamanho is 16
assert Vetor.deslocamento("xyz") is 4

out ""
out "== 2. ler devolve um cluster =="

p := Pixel.empacotar({"rgba": [CHEIO, 128, 0, CHEIO]})
assert Pixel.ler(p)["rgba"] is [CHEIO, 128, 0, CHEIO]

out ""
out "== 3. e a quantidade errada e recusada =="

recusou := no
monitor:
    Pixel.empacotar({"rgba": [1, 2]})
handle LayoutError as e:
    recusou := yes
    assert "4 posicao" in e.message
assert recusou

out ""
out "== 4. uma imagem de tres pixels =="

imagem := Est.bloco(Pixel.tamanho * 3)
steady CORES := [[CHEIO, 0, 0, CHEIO], [0, CHEIO, 0, CHEIO], [0, 0, CHEIO, CHEIO]]

cycle i from 0 to 2:
    Pixel.escrever(imagem, {"rgba": CORES[i]}, i * Pixel.tamanho)

lidos := [j.ler("rgba") cycle j in Est.janelas(imagem, Pixel)]
assert lidos is CORES

out ""
out "== 5. inverter a imagem, no lugar =="

janelas := Est.janelas(imagem, Pixel)
cycle j in janelas:
    atual := j.ler("rgba")
    j.escrever("rgba", [CHEIO - atual[0], CHEIO - atual[1], CHEIO - atual[2],
            atual[3]])

assert Pixel.ler(imagem)["rgba"] is [0, CHEIO, CHEIO, CHEIO]
out "   a inversao chegou ao bloco"

out ""
out "== 6. campos de tipos diferentes convivem =="

v := Vetor.empacotar({"nome": [80, 79, 78, 84], "xyz": [1.0, 2.0, 3.0]})
lido := Vetor.ler(v)
assert lido["xyz"] is [1.0, 2.0, 3.0]
assert lido["nome"] is [80, 79, 78, 84]

out "exercicio 305 ok"`, lang: 'df', title: `exercicios/52-estruturas/305_campos_multiplos.df` },
  {"p": "`rgba` é quatro bytes, e não quatro campos. Declarar a quantidade é o que faz o molde saber o tamanho do registro sem contar à mão."},
  {"h3": "Ler devolve um cluster"},
  {"p": "E a quantidade errada na escrita é recusada — um `rgba` com dois valores sairia com dois bytes de lixo."},
  {"h3": "Uma imagem de três pixels"},
  {"p": "As janelas percorrem, e a inversão escreve no lugar."},
  {"h3": "E campos de tipos diferentes convivem"},
  {"p": "Bytes e `f32` no mesmo registro, cada um com a sua quantidade."},
  {"h2": "306 · as seis recusas do layout"},
  {"p": "**Enunciado.** cada recusa existe porque a alternativa e um numero"},
  { code: `// plausivel — e um defeito que aparece tres camadas adiante, num campo
// que nao tem nada a ver com a causa.

adopt Arcane.Estrutura as Est

steady Cabecalho := Est.definir("Cabecalho", [
        ["magia", "u32"], ["versao", "u16"], ["registros", "u16"]
    ])

action recusou(acao):
    monitor:
        acao()
    handle LayoutError as e:
        out $"   {e.message}"
        yield yes
    yield no

out "== 1. ler alem do fim =="
assert recusou(lambda => Cabecalho.ler(Est.bloco(4)))

out ""
out "== 2. um deslocamento que nao cabe =="
assert recusou(lambda => Cabecalho.ler(Est.bloco(12), 8))

out ""
out "== 3. um valor fora da faixa do tipo =="
// Sem esta conferencia ele seria truncado em silencio, e o arquivo
// sairia com outro numero.
assert recusou(lambda => Est.definir("P", [["n", "u8"]]).empacotar({"n": 300}))

out ""
out "== 4. um campo que nao existe — com sugestao =="
assert recusou(lambda => Cabecalho.escrever(Est.bloco(8), {"versaoo": 1}))

out ""
out "== 5. um bloco somente leitura =="
// 'bytes' nao muda; 'bytearray' e um Bloco mudam.
assert recusou(lambda => Cabecalho.escrever(Est.bloco(8).bytes(), {"versao": 1}))

out ""
out "== 6. um campo declarado duas vezes =="
// O segundo seria inalcancavel: a leitura devolve um vault.
assert recusou(lambda => Est.definir("P", [["x", "u8"], ["x", "u32"]]))

out ""
out "== 7. um tipo que nao existe — tambem com sugestao =="
assert recusou(lambda => Est.definir("P", [["x", "u33"]]))

out ""
out "== 8. e um molde sem campo nenhum =="
assert recusou(lambda => Est.definir("P", []))

out ""
out "== 9. o deslocamento negativo =="
assert recusou(lambda => Cabecalho.ler(Est.bloco(16), -1))

out ""
out "== 10. um bloco de tamanho negativo =="

negativo := no
monitor:
    Est.bloco(-1)
handle NegativeSizeError:
    negativo := yes
assert negativo

out "exercicio 306 ok"`, lang: 'df', title: `exercicios/52-estruturas/306_estruturas_recusam.df` },
  {"p": "Cada recusa existe porque a alternativa é um número **plausível** — e um defeito que aparece três camadas adiante, num campo que não tem nada a ver com a causa."},
  {"h3": "Ler além do fim"},
  {"p": "Sem a conferência, o resultado são bytes que não são deste registro."},
  {"h3": "Um valor fora da faixa do tipo"},
  {"p": "Ele seria truncado em silêncio, e o arquivo sairia com outro número."},
  {"h3": "Um campo declarado duas vezes"},
  {"p": "O segundo seria inalcançável: a leitura devolve um vault, e a chave repetida some."},
  {"h3": "E os nomes errados sugerem o parecido"},
  {"p": "Tipo e campo, os dois — com a lista inteira na nota."},
  {"h2": "307 · um protocolo de linha, montado e lido"},
  {"p": "**Enunciado.** quase todo protocolo binario tem a mesma forma —"},
  { code: `// cabecalho de tamanho fixo dizendo o tipo e o comprimento, e um corpo
// de tamanho variavel logo depois. Aqui isso vira duas linhas de
// declaracao.

adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as By

steady Quadro := Est.definir("Quadro", [
        ["tipo", "u8"],
        ["comprimento", "u16"]
    ], ordem := "rede", empacotado := yes)

steady PING := 1
steady TEXTO := 2
steady FIM := 3

action montar(tipo, corpo):
    "Um quadro: o cabecalho empacotado, e o corpo logo depois."
    dados := By.de_texto(corpo)
    bloco := Est.bloco(Quadro.tamanho + len(dados))
    Quadro.escrever(bloco, {"tipo": tipo, "comprimento": len(dados)})
    cycle i from 0 to len(dados) - 1:
        bloco[Quadro.tamanho + i] := dados[i]
    yield bloco

action ler_quadros(fluxo):
    "Le quadros em sequencia ate acabar o bloco."
    saida := []
    cursor := 0
    crus := fluxo.bytes()
    persist cursor + Quadro.tamanho smaller_eq len(crus):
        cabeca := Quadro.ler(fluxo, cursor)
        inicio := cursor + Quadro.tamanho
        fim := inicio + cabeca["comprimento"]
        given fim bigger len(crus):
            halt
        saida.append({"tipo": cabeca["tipo"],
                "corpo": By.para_texto(crus[inicio:fim])})
        cursor := fim
    yield saida

out "== 1. o cabecalho e empacotado: 3 bytes =="

assert Quadro.tamanho is 3
assert Quadro.deslocamento("comprimento") is 1
assert Quadro.enchimento() is 0

out ""
out "== 2. montar um quadro =="

um := montar(TEXTO, "ola")
assert len(um) is 6
assert Quadro.ler(um)["tipo"] is TEXTO
assert Quadro.ler(um)["comprimento"] is 3

out ""
out "== 3. juntar tres num fluxo =="

partes := [montar(PING, ""), montar(TEXTO, "bom dia"), montar(FIM, "tchau")]
total := sum([len(p) cycle p in partes])
fluxo := Est.bloco(total)

posicao := 0
cycle parte in partes:
    crus := parte.bytes()
    cycle i from 0 to len(crus) - 1:
        fluxo[posicao + i] := crus[i]
    posicao := posicao + len(crus)

out ""
out "== 4. e ler de volta =="

quadros := ler_quadros(fluxo)
assert len(quadros) is 3
assert quadros[0]["tipo"] is PING
assert quadros[1]["corpo"] is "bom dia"
assert quadros[2]["tipo"] is FIM

cycle q in quadros:
    out $"   tipo {q['tipo']}: {q['corpo']}"

out ""
out "== 5. um quadro cortado no meio nao e entregue =="

// E o defeito classico de quem trata um 'recv' curto como a mensagem
// inteira: o proximo quadro sai corrompido.
cortado := Est.de_bytes(fluxo.bytes()[0:len(fluxo) - 2])
assert len(ler_quadros(cortado)) is 2
out "   dois quadros inteiros, e o terceiro ficou para a proxima leitura"

out "exercicio 307 ok"`, lang: 'df', title: `exercicios/52-estruturas/307_estrutura_e_rede.df` },
  {"p": "Quase todo protocolo binário tem a mesma forma: cabeçalho de tamanho fixo dizendo o tipo e o comprimento, e um corpo de tamanho variável logo depois."},
  {"h3": "O cabeçalho é empacotado"},
  {"p": "Três bytes, sem enchimento: num protocolo de rede o alinhamento não ajuda, e cada byte a mais é banda."},
  {"h3": "Ler quadros em sequência"},
  {"p": "O laço anda pelo bloco lendo cabeçalho e corpo, e para quando não há mais um cabeçalho inteiro."},
  {"h3": "E um quadro cortado no meio não é entregue"},
  {"p": "É o defeito clássico de quem trata um `recv` curto como a mensagem inteira: o próximo quadro sai corrompido, e o sintoma é uma conexão que funciona e de repente para."},
  {"h2": "308 · o bloco, e o que ele promete"},
  {"p": "**Enunciado.** 'liberar()' nao devolve memoria ao sistema — quem faz"},
  { code: `// isso e o CPython. O que ele faz e MARCAR. Num mundo com coletor, a
// memoria nunca esteve em risco; o que se protege e o PROTOCOLO.

adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as By

out "== 1. criar, ler e escrever =="

b := Est.bloco(8)
assert len(b) is 8
assert b.bytes() is By.de_hex("0000000000000000")

b[0] := 255
b[7] := 1
assert b[0] is 255
assert By.hex(b.bytes()) is "ff000000000000" + "01"

out ""
out "== 2. a partir de bytes que ja existem =="

c := Est.de_bytes(By.de_texto("DataForge"))
assert len(c) is 9
assert By.para_texto(c.bytes()) is "DataForge"

out ""
out "== 3. preencher e fatiar =="

d := Est.bloco(4).preencher(170)
assert By.hex(d.bytes()) is "aaaaaaaa"

pedaco := c.fatiar(0, 4)
assert By.para_texto(pedaco.bytes()) is "Data"
// A fatia e um bloco NOVO: mexer nela nao mexe no original.
pedaco[0] := 88
assert By.para_texto(c.bytes()) is "DataForge"

out ""
out "== 4. o bloco liberado responde =="

assert b.vivo()
b.liberar()
assert not b.vivo()
assert len(b) is 0

morreu := no
monitor:
    b[0]
handle DanglingPointerError as e:
    morreu := yes
    assert "liberado" in e.message
assert morreu

out ""
out "== 5. e a janela sobre ele tambem =="

viva := Est.bloco(8)
molde := Est.definir("P", [["n", "u32"]])
j := Est.janela(viva, molde)
j.escrever("n", 7)
assert j.ler("n") is 7

viva.liberar()
janela_morta := no
monitor:
    j.ler("n")
handle DanglingPointerError:
    janela_morta := yes
assert janela_morta

out ""
out "== 6. o bloco e o bytes do Arcane.Bytes conversam =="

// Os dois modulos falam do mesmo dado, e um aceita o outro.
molde2 := Est.definir("Par", [["a", "u16"], ["b", "u16"]], ordem := "rede")
crus := By.empacotar(">u16 u16", [7, 9])
lido := molde2.ler(Est.de_bytes(crus))
assert lido["a"] is 7
assert lido["b"] is 9

out "exercicio 308 ok"`, lang: 'df', title: `exercicios/52-estruturas/308_bloco.df` },
  {"p": "`liberar()` não devolve memória ao sistema — quem faz isso é o CPython. O que ele faz é **marcar**."},
  {"h3": "A fatia é um bloco NOVO"},
  {"p": "Mexer nela não mexe no original: é cópia, e não janela."},
  {"h3": "O bloco liberado responde"},
  {"p": "E a janela sobre ele também. Num mundo com coletor, a memória nunca esteve em risco; o que se protege é o **protocolo**."},
  {"h3": "E os dois módulos conversam"},
  {"p": "`Est.de_bytes(By.empacotar(...))` — o mesmo dado, duas formas de nomeá-lo."},
  {"h2": "309 · gravar e reler do disco"},
  {"p": "**Enunciado.** um molde so vale se o arquivo que ele produz for lido de"},
  { code: `// volta igual. Este exercicio faz a ida e a volta pelo disco, e
// confere byte a byte.

adopt Arcane.Estrutura as Est
adopt Arcane.IO as IO
adopt Arcane.OS as OS

steady Ponto := Est.definir("Ponto", [
        ["x", "f32"],
        ["y", "f32"],
        ["rotulo", "u8", 8]
    ], ordem := "rede")

steady pasta := $"{OS.temp_dir()}/df-309-{randint(100000, 999999)}"
IO.mkdir(pasta)
steady caminho := $"{pasta}/pontos.bin"

action rotulo_para_bytes(texto):
    "Oito bytes, cortados ou preenchidos com zero."
    crus := [ord(c) cycle c in texto]
    cycle i from len(crus) to 7:
        crus.append(0)
    yield crus[0:8]

action bytes_para_rotulo(crus):
    yield join("", [char(b) cycle b in crus given b isnt 0])

steady PONTOS := [
    {"x": 1.5, "y": 2.5, "rotulo": "origem"},
    {"x": -3.0, "y": 0.25, "rotulo": "canto"},
    {"x": 100.0, "y": -100.0, "rotulo": "longe"}
]

out "== 1. gravar =="

bloco := Est.bloco(Ponto.tamanho * len(PONTOS))
cycle i from 0 to len(PONTOS) - 1:
    p := PONTOS[i]
    Ponto.escrever(bloco, {"x": p["x"], "y": p["y"],
            "rotulo": rotulo_para_bytes(p["rotulo"])},
        i * Ponto.tamanho)

IO.write_bytes(caminho, bloco.bytes())
assert IO.exists(caminho)
assert IO.size(caminho) is Ponto.tamanho * len(PONTOS)
out $"   {IO.size(caminho)} bytes em disco"

out ""
out "== 2. reler =="

de_volta := Est.de_bytes(IO.read_bytes(caminho))
assert len(de_volta) is len(bloco)

lidos := []
cycle janela in Est.janelas(de_volta, Ponto):
    lidos.append({"x": janela.ler("x"), "y": janela.ler("y"),
            "rotulo": bytes_para_rotulo(janela.ler("rotulo"))})

assert len(lidos) is 3
assert lidos[0]["rotulo"] is "origem"
assert lidos[1]["x"] is -3.0
assert lidos[2]["y"] is -100.0

cycle l in lidos:
    out $"   {l['rotulo']}: ({l['x']}, {l['y']})"

out ""
out "== 3. os bytes sao IDENTICOS =="

assert IO.read_bytes(caminho) is bloco.bytes()

out ""
out "== 4. e o f32 tem precisao de f32 =="

// 0.1 nao cabe exato em 32 bits: a ida e volta NAO devolve 0.1. Isso
// nao e defeito do modulo — e o tipo que foi escolhido.
teste := Ponto.empacotar({"x": 0.1, "y": 0.0,
        "rotulo": rotulo_para_bytes("")})
assert Ponto.ler(teste)["x"] isnt 0.1
assert abs(Ponto.ler(teste)["x"] - 0.1) smaller 0.0001
out "   f32 aproxima; f64 aproxima menos; Decimal nao aproxima"

steady Exato := Est.definir("Exato", [["x", "f64"]])
assert Exato.ler(Exato.empacotar({"x": 0.1}))["x"] is 0.1

IO.remove_tree(pasta)
out "exercicio 309 ok"`, lang: 'df', title: `exercicios/52-estruturas/309_estrutura_e_arquivo.df` },
  {"p": "Um molde só vale se o arquivo que ele produz for lido de volta igual. A ida e a volta passam pelo disco, e os bytes são comparados."},
  {"h3": "Os bytes são idênticos"},
  {"p": "Não é \"parecido\": é a mesma sequência."},
  {"h3": "E o `f32` tem precisão de `f32`"},
  {"p": "`0.1` não cabe exato em 32 bits, e a ida e volta **não** devolve `0.1`. Isso não é defeito do módulo — é o tipo que foi escolhido, e `f64` aproxima menos."},
  {"h2": "310 · quando usar cada um dos tres"},
  {"p": "**Enunciado.** 'Arcane.Bytes' empacota por formato, 'Arcane.Estrutura'"},
  { code: `// por nome, e 'Arcane.C' fala com biblioteca nativa. Escolher o errado
// nao da erro — da codigo que ninguem consegue ler depois.

adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as By

out "== 1. o mesmo dado, pelos dois caminhos =="

steady FORMATO := ">u32 u16 u16"
steady Molde := Est.definir("Cabecalho", [
        ["magia", "u32"], ["versao", "u16"], ["registros", "u16"]
    ], ordem := "rede")

por_formato := By.empacotar(FORMATO, [1145128264, 2, 7])
por_nome := Molde.empacotar({"magia": 1145128264, "versao": 2,
        "registros": 7})

assert por_formato is por_nome.bytes()
out "   os mesmos oito bytes"

out ""
out "== 2. a diferenca esta na LEITURA =="

lista := By.desempacotar(FORMATO, por_formato)
assert lista[1] is 2  // 'lista[1]' nao diz o que e

vault := Molde.ler(por_nome)
assert vault["versao"] is 2  // este diz

out ""
out "== 3. o formato nao conhece alinhamento =="

// 'u8 u32' empacotado tem 5 bytes nos dois. Mas o C escreve 8, e e o
// molde alinhado que reproduz isso.
assert len(By.empacotar(">u8 u32", [1, 2])) is 5
assert Est.definir("P", [["a", "u8"], ["b", "u32"]],
    empacotado := yes).tamanho is 5
assert Est.definir("P", [["a", "u8"], ["b", "u32"]]).tamanho is 8

out ""
out "== 4. e o formato nao sabe o proprio tamanho por nome =="

assert Molde.deslocamento("registros") is 6
// Pelo formato, isso e uma conta a mao — e uma conta a mao envelhece
// quando alguem acrescenta um campo no meio.

out ""
out "== 5. o cursor do Arcane.Bytes continua util =="

// Ler campos em SEQUENCIA, sem posicao fixa, e o que o cursor faz
// melhor.
cursor := By.ler(por_formato, ">")
assert cursor.ler("u32") is 1145128264
assert cursor.ler("u16") is 2
assert cursor.ler("u16") is 7
assert cursor.acabou

out ""
out "== 6. a regra, em uma frase =="

out "   formato: um punhado de campos, lidos em sequencia"
out "   molde:   um registro com nome, que se repete num arquivo"
out "   FFI:     quando o layout e de OUTRO programa, em C"

out "exercicio 310 ok"`, lang: 'df', title: `exercicios/52-estruturas/310_estrutura_vs_bytes.df` },
  {"p": "`Arcane.Bytes` empacota por formato, `Arcane.Estrutura` por nome, e `Arcane.C` fala com biblioteca nativa. Escolher o errado não dá erro — dá código que ninguém consegue ler depois."},
  {"h3": "A diferença está na LEITURA"},
  {"p": "Os mesmos oito bytes: `lista[1]` não diz o que é; `vault[\"versao\"]` diz."},
  {"h3": "O formato não conhece alinhamento"},
  {"p": "`u8 u32` empacotado tem 5 bytes nos dois. Mas o C escreve 8, e é o molde alinhado que reproduz isso."},
  {"h3": "E a regra, em uma frase"},
  {"p": "Formato: um punhado de campos lidos em sequência. Molde: um registro com nome, que se repete num arquivo. FFI: quando o layout é de **outro programa**, em C."},
  {"h2": "311 · gravar bytes num arquivo"},
  {"p": "**Enunciado.** a linguagem sabia PRODUZIR bytes — 'Arcane.Bytes',"},
  { code: `// 'Arcane.Estrutura', 'Arcane.Crypto' — e nao sabia grava-los.
// 'IO.write' abre em modo texto com UTF-8: passar bytes ali levanta,
// e passar o texto de um 'para_texto' corrompe o que nao for texto
// valido.

adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Bytes as By
adopt Arcane.Estrutura as Est
adopt Arcane.Crypto as Cripto

steady pasta := $"{OS.temp_dir()}/df-311-{randint(100000, 999999)}"
IO.mkdir(pasta)

out "== 1. ida e volta =="

steady caminho := $"{pasta}/dados.bin"
steady CRUS := By.de_hex("deadbeef00ff")

assert IO.write_bytes(caminho, CRUS) is 6
assert IO.read_bytes(caminho) is CRUS
assert IO.size(caminho) is 6
out $"   {By.hex(IO.read_bytes(caminho))}"

out ""
out "== 2. ele aceita um Bloco direto =="

// Obrigar a lembrar de '.bytes()' e a forma mais rapida de gravar a
// representacao em TEXTO de um objeto no lugar do conteudo dele.
bloco := Est.bloco(4).preencher(170)
IO.write_bytes($"{pasta}/bloco.bin", bloco)
assert By.hex(IO.read_bytes($"{pasta}/bloco.bin")) is "aaaaaaaa"

out ""
out "== 3. e um cluster de numeros =="

// E como um 'ponteiro.cluster()' volta.
IO.write_bytes($"{pasta}/lista.bin", [1, 2, 3, 255])
assert By.hex(IO.read_bytes($"{pasta}/lista.bin")) is "010203ff"

out ""
out "== 4. acrescentar no fim =="

IO.append_bytes(caminho, By.de_hex("0102"))
assert len(IO.read_bytes(caminho)) is 8
assert By.hex(IO.read_bytes(caminho)) is "deadbeef00ff0102"

out ""
out "== 5. o que NAO pode virar bytes e recusado =="

recusou := no
monitor:
    IO.write_bytes($"{pasta}/x.bin", {"a": 1})
handle TypeError as e:
    recusou := yes
    assert "bytes" in e.message
assert recusou

out ""
out "== 6. um byte que nao e texto valido sobrevive =="

// E o ponto inteiro: 0xFF sozinho nao e UTF-8, e 'IO.write' o
// destruiria.
steady QUEBRADO := By.de_hex("ff")
IO.write_bytes($"{pasta}/nao-e-texto.bin", QUEBRADO)
assert IO.read_bytes($"{pasta}/nao-e-texto.bin") is QUEBRADO

out ""
out "== 7. um caso de verdade: gravar o digest em binario =="

// 'sha256' devolve o hexadecimal, que ocupa 64 caracteres. Os bytes
// crus sao 32 — metade do arquivo, pelo mesmo dado.
steady EM_HEX := Cripto.sha256("DataForge")
steady CRU := By.de_hex(EM_HEX)

IO.write($"{pasta}/hash.txt", EM_HEX)
IO.write_bytes($"{pasta}/hash.bin", CRU)

assert IO.size($"{pasta}/hash.txt") is 64
assert IO.size($"{pasta}/hash.bin") is 32
assert By.hex(IO.read_bytes($"{pasta}/hash.bin")) is EM_HEX
out $"   {IO.size($'{pasta}/hash.txt')} bytes em texto, {IO.size($'{pasta}/hash.bin')} em binario"

IO.remove_tree(pasta)
out "exercicio 311 ok"`, lang: 'df', title: `exercicios/52-estruturas/311_io_binario.df` },
  {"p": "A linguagem sabia **produzir** bytes — `Bytes`, `Estrutura`, `Crypto` — e não sabia gravá-los. `IO.write` abre em modo texto com UTF-8."},
  {"h3": "O byte que prova o ponto"},
  {"p": "`0xFF` sozinho não é UTF-8. Passá-lo por `IO.write` o destruiria, e o arquivo sairia diferente do que entrou."},
  {"h3": "Ele aceita o que os módulos devolvem"},
  {"p": "Bloco, cluster de números, texto ou bytes. Obrigar a lembrar de `.bytes()` é a forma mais rápida de gravar a **representação em texto** de um objeto no lugar do conteúdo dele."},
  {"h3": "E o que não vira bytes é recusado"},
  {"p": "Inventar uma codificação ali grava outra coisa, em silêncio."},
  {"h2": "312 · um formato completo, do zero ao disco"},
  {"p": "**Enunciado.** juntar tudo — molde, alinhamento, janela, ponteiro,"},
  { code: `// arquivo e conferencia de integridade. E o desenho de um indice de
// banco de dados simples.

adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as By
adopt Arcane.IO as IO
adopt Arcane.OS as OS
adopt Arcane.Crypto as Cripto

steady MAGIA := 1145979218
steady VERSAO := 3

steady Cabecalho := Est.definir("Cabecalho", [
        ["magia", "u32"],
        ["versao", "u16"],
        ["quantos", "u16"],
        ["soma", "u32"]
    ], ordem := "rede")

steady Entrada := Est.definir("Entrada", [
        ["chave", "u32"],
        ["valor", "u32"]
    ], ordem := "rede")

steady PARES := [[10, 100], [20, 400], [30, 900], [40, 1600]]

action soma_simples(crus):
    "Um checksum de brinquedo: a soma dos bytes, em 32 bits."
    total := 0
    cycle b in crus:
        total := (total + b) % 4294967296
    yield total

out "== 1. montar o indice =="

steady INICIO := Cabecalho.tamanho
arquivo := Est.bloco(INICIO + Entrada.tamanho * len(PARES))

cycle i from 0 to len(PARES) - 1:
    Entrada.escrever(arquivo, {"chave": PARES[i][0], "valor": PARES[i][1]},
        INICIO + i * Entrada.tamanho)

corpo := arquivo.bytes()[INICIO:len(arquivo)]
Cabecalho.escrever(arquivo, {"magia": MAGIA, "versao": VERSAO,
        "quantos": len(PARES),
        "soma": soma_simples(corpo)})

assert len(arquivo) is INICIO + Entrada.tamanho * 4
out $"   {len(arquivo)} bytes"

out ""
out "== 2. gravar e reler =="

steady pasta := $"{OS.temp_dir()}/df-312-{randint(100000, 999999)}"
IO.mkdir(pasta)
steady caminho := $"{pasta}/indice.bin"

IO.write_bytes(caminho, arquivo)
lido := Est.de_bytes(IO.read_bytes(caminho))
assert lido.bytes() is arquivo.bytes()

out ""
out "== 3. conferir a integridade ANTES de confiar =="

action abrir(dados):
    "Devolve as entradas, ou levanta dizendo o que esta errado."
    given len(dados) smaller Cabecalho.tamanho:
        trigger "o arquivo e curto demais para ter cabecalho"
    cabeca := Cabecalho.ler(dados)
    given cabeca["magia"] isnt MAGIA:
        trigger "este arquivo nao e um indice"
    given cabeca["versao"] bigger VERSAO:
        trigger $"versao {cabeca['versao']} e mais nova que a que eu leio"
    bytes_do_corpo := dados.bytes()[Cabecalho.tamanho:len(dados)]
    given soma_simples(bytes_do_corpo) isnt cabeca["soma"]:
        trigger "o conteudo nao bate com a soma do cabecalho"
    yield Est.janelas(dados, Entrada, quantos := cabeca["quantos"],
        deslocamento := Cabecalho.tamanho)

entradas := abrir(lido)
assert len(entradas) is 4
assert [e.ler("chave") cycle e in entradas] is [10, 20, 30, 40]

out ""
out "== 4. busca binaria pelo ponteiro =="

// As chaves estao em ordem: da para bisseccionar sem materializar
// nada.
action procurar(dados, quantos, chave):
    baixo := 0
    alto := quantos - 1
    persist baixo smaller_eq alto:
        meio := (baixo + alto) ~/ 2
        janela := Est.janela(dados, Entrada,
            Cabecalho.tamanho + meio * Entrada.tamanho)
        atual := janela.ler("chave")
        given atual is chave:
            yield janela.ler("valor")
        orif atual smaller chave:
            baixo := meio + 1
        otherwise:
            alto := meio - 1
    yield void

assert procurar(lido, 4, 30) is 900
assert procurar(lido, 4, 10) is 100
assert procurar(lido, 4, 25) is void
out "   busca binaria direto no bloco"

out ""
out "== 5. um arquivo corrompido e RECUSADO =="

corrompido := Est.de_bytes(IO.read_bytes(caminho))
corrompido[Cabecalho.tamanho] := 99  // mexe na primeira chave

pegou := no
monitor:
    abrir(corrompido)
handle Error as e:
    pegou := yes
    assert "soma" in e.message
    out $"   {e.message}"
assert pegou

out ""
out "== 6. e um arquivo de outro formato tambem =="

outro := Cabecalho.empacotar({"magia": 0, "versao": 1, "quantos": 0,
        "soma": 0})
nao_e := no
monitor:
    abrir(outro)
handle Error as e:
    nao_e := yes
    assert "nao e um indice" in e.message
assert nao_e

out ""
out "== 7. o hash do arquivo, para guardar ao lado =="

assert len(Cripto.sha256(By.hex(arquivo.bytes()))) is 64

IO.remove_tree(pasta)
out "exercicio 312 ok"`, lang: 'df', title: `exercicios/52-estruturas/312_estrutura_ponta_a_ponta.df` },
  {"p": "Molde, alinhamento, janela, ponteiro, arquivo e conferência de integridade — o desenho de um índice de banco de dados simples."},
  {"h3": "Conferir a integridade ANTES de confiar"},
  {"p": "Tamanho, magia, versão e soma. Um leitor que confia primeiro e confere depois já leu lixo."},
  {"h3": "Busca binária direto no bloco"},
  {"p": "As chaves estão em ordem: dá para bisseccionar sem materializar nada."},
  {"h3": "E o arquivo corrompido é RECUSADO"},
  {"p": "Um byte trocado no corpo muda a soma. Sem ela, a busca devolveria um valor plausível — que é pior que falhar."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/52-estruturas/298_molde_e_ordem.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '298-o-layout-que-tem-nome', text: "298 · o layout que tem NOME", level: 2 as const }, { id: 'a-ordem-dos-bytes-e-obrigatoria', text: "A ordem dos bytes é obrigatória", level: 3 as const }, { id: 'o-molde-sabe-o-proprio-layout', text: "O molde sabe o próprio layout", level: 3 as const }, { id: 'e-o-que-falta-vai-zerado', text: "E o que falta vai zerado", level: 3 as const }, { id: '299-o-enchimento-que-o-c-insere', text: "299 · o enchimento que o C insere", level: 2 as const }, { id: 'alinhado-empacotado', text: "Alinhado × empacotado", level: 3 as const }, { id: 'o-registro-inteiro-tambem-e-alinhado', text: "O REGISTRO INTEIRO também é alinhado", level: 3 as const }, { id: 'e-a-lista-de-tipos-e-a-mesma-do-arcanebytes', text: "E a lista de tipos é a mesma do `Arcane.Bytes`", level: 3 as const }, { id: '300-a-janela-nao-copia', text: "300 · a janela nao COPIA", level: 2 as const }, { id: 'escrever-na-janela-muda-o-bloco', text: "Escrever na janela muda O BLOCO", level: 3 as const }, { id: 'o-vault-da-janela-e-uma-copia', text: "O vault da janela é uma cópia", level: 3 as const }, { id: 'pedir-mais-do-que-cabe-e-erro-com-a-conta', text: "Pedir mais do que cabe é erro, com a conta", level: 3 as const }, { id: 'e-um-campo-que-nao-existe-sugere-o-parecido', text: "E um campo que não existe SUGERE o parecido", level: 3 as const }, { id: '301-andar-por-elemento-e-nao-por-byte', text: "301 · andar por ELEMENTO, e nao por byte", level: 2 as const }, { id: 'o-passo-e-o-tamanho-do-tipo', text: "O passo é o tamanho do tipo", level: 3 as const }, { id: 'o-cast-reinterpreta-o-mesmo-endereco', text: "O cast reinterpreta o MESMO endereço", level: 3 as const }, { id: 'e-a-faixa-vem-do-tipo-declarado', text: "E a faixa vem do TIPO declarado", level: 3 as const }, { id: '302-o-ponteiro-que-nao-aponta-para-nada', text: "302 · o ponteiro que nao aponta para nada", level: 2 as const }, { id: 'o-nulo-tem-endereco-zero', text: "O NULO tem endereço zero", level: 3 as const }, { id: 'o-pendurado-aponta-para-um-bloco-liberado', text: "O PENDURADO aponta para um bloco liberado", level: 3 as const }, { id: 'liberar-e-idempotente', text: "`liberar` é idempotente", level: 3 as const }, { id: 'e-o-ponteiro-segura-o-bloco', text: "E o ponteiro SEGURA o bloco", level: 3 as const }, { id: '303-ler-um-formato-binario-de-verdade', text: "303 · ler um formato binario de verdade", level: 2 as const }, { id: 'procurar-pelo-indice-sem-varrer-os-itens', text: "Procurar pelo índice, sem varrer os itens", level: 3 as const }, { id: 'mudar-o-estoque-no-lugar', text: "Mudar o estoque no lugar", level: 3 as const }, { id: 'e-a-magia-errada-e-problema-de-quem-le', text: "E a magia errada é problema de quem lê", level: 3 as const }, { id: '304-os-mesmos-bytes-dois-nomes', text: "304 · os mesmos bytes, dois nomes", level: 2 as const }, { id: 'escrever-um-ler-o-outro', text: "Escrever um, ler o outro", level: 3 as const }, { id: 'ler-bits-de-um-campo', text: "Ler bits de um campo", level: 3 as const }, { id: 'e-os-dois-modulos-falam-dos-mesmos-bytes', text: "E os dois módulos falam dos mesmos bytes", level: 3 as const }, { id: '305-um-campo-com-varias-posicoes', text: "305 · um campo com varias posicoes", level: 2 as const }, { id: 'ler-devolve-um-cluster', text: "Ler devolve um cluster", level: 3 as const }, { id: 'uma-imagem-de-tres-pixels', text: "Uma imagem de três pixels", level: 3 as const }, { id: 'e-campos-de-tipos-diferentes-convivem', text: "E campos de tipos diferentes convivem", level: 3 as const }, { id: '306-as-seis-recusas-do-layout', text: "306 · as seis recusas do layout", level: 2 as const }, { id: 'ler-alem-do-fim', text: "Ler além do fim", level: 3 as const }, { id: 'um-valor-fora-da-faixa-do-tipo', text: "Um valor fora da faixa do tipo", level: 3 as const }, { id: 'um-campo-declarado-duas-vezes', text: "Um campo declarado duas vezes", level: 3 as const }, { id: 'e-os-nomes-errados-sugerem-o-parecido', text: "E os nomes errados sugerem o parecido", level: 3 as const }, { id: '307-um-protocolo-de-linha-montado-e-lido', text: "307 · um protocolo de linha, montado e lido", level: 2 as const }, { id: 'o-cabecalho-e-empacotado', text: "O cabeçalho é empacotado", level: 3 as const }, { id: 'ler-quadros-em-sequencia', text: "Ler quadros em sequência", level: 3 as const }, { id: 'e-um-quadro-cortado-no-meio-nao-e-entregue', text: "E um quadro cortado no meio não é entregue", level: 3 as const }, { id: '308-o-bloco-e-o-que-ele-promete', text: "308 · o bloco, e o que ele promete", level: 2 as const }, { id: 'a-fatia-e-um-bloco-novo', text: "A fatia é um bloco NOVO", level: 3 as const }, { id: 'o-bloco-liberado-responde', text: "O bloco liberado responde", level: 3 as const }, { id: 'e-os-dois-modulos-conversam', text: "E os dois módulos conversam", level: 3 as const }, { id: '309-gravar-e-reler-do-disco', text: "309 · gravar e reler do disco", level: 2 as const }, { id: 'os-bytes-sao-identicos', text: "Os bytes são idênticos", level: 3 as const }, { id: 'e-o-f32-tem-precisao-de-f32', text: "E o `f32` tem precisão de `f32`", level: 3 as const }, { id: '310-quando-usar-cada-um-dos-tres', text: "310 · quando usar cada um dos tres", level: 2 as const }, { id: 'a-diferenca-esta-na-leitura', text: "A diferença está na LEITURA", level: 3 as const }, { id: 'o-formato-nao-conhece-alinhamento', text: "O formato não conhece alinhamento", level: 3 as const }, { id: 'e-a-regra-em-uma-frase', text: "E a regra, em uma frase", level: 3 as const }, { id: '311-gravar-bytes-num-arquivo', text: "311 · gravar bytes num arquivo", level: 2 as const }, { id: 'o-byte-que-prova-o-ponto', text: "O byte que prova o ponto", level: 3 as const }, { id: 'ele-aceita-o-que-os-modulos-devolvem', text: "Ele aceita o que os módulos devolvem", level: 3 as const }, { id: 'e-o-que-nao-vira-bytes-e-recusado', text: "E o que não vira bytes é recusado", level: 3 as const }, { id: '312-um-formato-completo-do-zero-ao-disco', text: "312 · um formato completo, do zero ao disco", level: 2 as const }, { id: 'conferir-a-integridade-antes-de-confiar', text: "Conferir a integridade ANTES de confiar", level: 3 as const }, { id: 'busca-binaria-direto-no-bloco', text: "Busca binária direto no bloco", level: 3 as const }, { id: 'e-o-arquivo-corrompido-e-recusado', text: "E o arquivo corrompido é RECUSADO", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"52 · Estruturas e ponteiros"}
      description={"15 exercícios: layout binário com nome, janela sem cópia e ponteiro."}
      href={"/docs/exercicios/52-estruturas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
