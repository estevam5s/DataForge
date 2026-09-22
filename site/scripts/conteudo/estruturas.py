# -*- coding: utf-8 -*-
"""Arcane.Estrutura — layout binário com nome, janela e ponteiro."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas",
"title": "Estruturas e ponteiros",
"description": "Layout binário com campos nomeados, alinhamento conferido, janela que não copia e ponteiro com aritmética por elemento.",
"blocos": [
 {"p": "A linguagem já tinha duas respostas para bytes, e faltava a do meio."},
 {"table": {"head": ["", "O que resolve", "O que falta"], "rows": [
   ["`Arcane.Bytes`", "empacota e desempacota por **formato**: `'>i32 u16'`", "não tem **nome** — o resultado é posicional, e `dados[3]` três meses depois não diz nada"],
   ["`Arcane.C`", "`estrutura` e `ponteiro` de verdade", "é **FFI**: exige uma biblioteca nativa carregada"],
   ["`Arcane.Estrutura`", "campos nomeados, alinhamento, janela, ponteiro", "não fala com o C — para isso é o `Arcane.C`"]]}},
 {"p": "Ler o cabeçalho de um PNG não deveria exigir `ctypes`."},
 {"code": """adopt Arcane.Estrutura as Est

steady Cabecalho := Est.definir("Cabecalho", [
    ["magia", "u32"],
    ["versao", "u16"],
    ["registros", "u16"]
], ordem := "rede")

c := Cabecalho.ler(dados)
out c["versao"]""", "lang": "df"},

 {"h2": "A ordem dos bytes é obrigatória"},
 {"callout": {"tipo": "atencao", "titulo": "Sem ela, o mesmo arquivo dá dois valores",
              "texto": "E nenhuma das duas máquinas falha. É a mesma cobrança do `Arcane.Bytes`, e pelo mesmo motivo. `\"rede\"` é big-endian — o de todo formato de arquivo e todo protocolo; `\"intel\"` é little-endian."}},

 {"h2": "O alinhamento é declarado, e conferido"},
 {"code": """Alinhado := Est.definir("Pacote", [["a", "u8"], ["b", "u32"]])
Junto := Est.definir("Pacote", [["a", "u8"], ["b", "u32"]],
    empacotado := yes)

out Alinhado.deslocamento("b")     // 4 — o C insere 3 bytes de enchimento
out Alinhado.tamanho               // 8
out Junto.deslocamento("b")        // 1
out Junto.tamanho                  // 5""", "lang": "df"},
 {"p": "Um `u32` começa num múltiplo de 4; um `u64`, num múltiplo de 8. Adivinhar aqui é o que faz o mesmo `.struct` sair com 12 bytes de um lado e 16 do outro. E o **registro inteiro** também é alinhado ao maior campo — sem isso, um cluster deles sai torto a partir do segundo."},
 {"p": "`molde.mapa()` devolve a tabela do layout (campo, tipo, deslocamento, bytes) e `molde.enchimento()` diz quantos bytes são só alinhamento."},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/estruturas/janelas", "title": "Blocos e janelas", "desc": "Ler e escrever no lugar, sem copiar."},
   {"href": "/docs/estruturas/ponteiros", "title": "Ponteiros", "desc": "Aritmética por elemento, cast, distância e o nulo."}]},
 {"h2": "Do campo ao formato de arquivo"},
 {"p": "Tipos e faixas, alinhamento, ordem dos bytes, texto de tamanho fixo, bits, varint, CRC — e PNG, WAV e um protocolo binário inteiros, lidos e escritos."},
 {"cards": [{"href": "/docs/estruturas/tipos", "title": "Os tipos de um campo", "desc": "Inteiros com e sem sinal, ponto flutuante, booleano, texto e bytes de tamanho fixo — e a faixa que cada um aceita."}, {"href": "/docs/estruturas/alinhamento", "title": "Alinhamento e enchimento", "desc": "Por que u8 + u32 + u16 ocupa 12 bytes e não 7, como reduzir, e quando empacotar."}, {"href": "/docs/estruturas/ordem-dos-bytes", "title": "A ordem dos bytes", "desc": "Big-endian, little-endian, a ordem da rede, e o bswap — com o mesmo número lido dos dois jeitos."}, {"href": "/docs/estruturas/textos", "title": "Texto de tamanho fixo", "desc": "O char[N] do C: completado com zeros, lido até o primeiro zero — e o acento que não cabe."}, {"href": "/docs/estruturas/bits", "title": "Campos de bits", "desc": "Versão e tamanho do IPv4 no mesmo byte, as flags do TCP em 16 bits — com máscara, e nunca com o bitfield do C."}, {"href": "/docs/estruturas/operacoes-de-bits", "title": "Operações de bits", "desc": "E, OU, OU exclusivo, NÃO com largura, deslocamento e contagem — como funções, e por que não operadores."}, {"href": "/docs/estruturas/varint", "title": "Varint e zigzag", "desc": "O inteiro de tamanho variável do Protocol Buffers e do WebAssembly: 7 bits por byte, e o truque para os negativos."}, {"href": "/docs/estruturas/png", "title": "Ler um PNG de verdade", "desc": "Assinatura, chunks, tamanho em big-endian e o CRC de cada um — o formato inteiro, sem biblioteca de imagem."}, {"href": "/docs/estruturas/wav", "title": "Escrever um WAV", "desc": "O cabeçalho RIFF de 44 bytes, em little-endian, e um segundo de onda senoidal escrito amostra por amostra."}, {"href": "/docs/estruturas/protocolo", "title": "Um protocolo binário", "desc": "Mensagens TLV — tipo, tamanho, valor — com varint: escrever, ler, e o campo desconhecido que não quebra ninguém."}, {"href": "/docs/estruturas/arquivo-mapeado", "title": "Arquivo mapeado em memória", "desc": "Um arquivo de gigabytes como um bloco, sem lê-lo inteiro: o sistema traz só as páginas tocadas."}, {"href": "/docs/estruturas/conferencia", "title": "CRC e soma de conferência", "desc": "CRC-32 do PNG e do ZIP, e a soma de complemento de um do cabeçalho IP — com o vetor da RFC."}, {"href": "/docs/estruturas/entrada-hostil", "title": "Ler entrada hostil", "desc": "Todo tamanho que vem do arquivo é suspeito: as cinco conferências antes de interpretar um byte."}, {"href": "/docs/estruturas/de-c-para-dataforge", "title": "De uma struct do C para um molde", "desc": "Traduzir uma struct, conferir o layout contra o próprio C, e o #pragma pack."}, {"href": "/docs/estruturas/receitas", "title": "Receitas binárias", "desc": "Hexdump, cor RGBA num u32, deslocamento de bits sem molde, e um vetor de registros ordenado no lugar."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/janelas",
"title": "Blocos e janelas",
"description": "O bloco que sabe dizer quando acabou, e a janela que lê e escreve sem copiar.",
"blocos": [
 {"h2": "O bloco"},
 {"code": """b := Est.bloco(64)          // 64 bytes zerados
c := Est.de_bytes(dados)    // a partir do que já existe

out len(b)
b.liberar()                 // marca o fim""", "lang": "df"},
 {"p": "`liberar()` não devolve memória ao sistema — quem faz isso é o CPython. O que ele faz é **marcar**: a partir dali, toda janela e todo ponteiro sobre este bloco levantam em vez de ler. É idempotente, como o `soltar` do `Arcane.Posse`: um `liberar` no `defer` e no caminho de erro não pode virar erro."},

 {"h2": "A janela não copia"},
 {"code": """j := Est.janela(arquivo, Registro, deslocamento := 8)

out j.ler("preco")
j.escrever("quantidade", 7)     // muda O BLOCO
j["ativo"] := yes               // o mesmo, por índice""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Por que não devolver um vault",
              "texto": "Copiar um registro de 4 KB para ler um campo de 2 bytes é o que faz um parser de arquivo grande levar minutos. `j.vault()` existe para quando a cópia é o que se quer — e ela deixa de acompanhar o bloco a partir dali."}},

 {"h2": "Percorrer um arquivo de registros"},
 {"code": """linhas := Est.janelas(arquivo, Registro,
    deslocamento := Cabecalho.tamanho)

cycle linha in linhas:
    out linha.ler("id"), linha.ler("preco")""", "lang": "df"},
 {"p": "Sem `quantos`, ele devolve quantos couberem. Pedir mais do que cabe é **erro**, com a conta na mensagem: `cabem 2 registro(s) de 'Par' aqui, e foram pedidos 5`. E `j.proxima()` anda um registro, para quem prefere o laço explícito."},

 {"h2": "O que é recusado"},
 {"table": {"head": ["", "Sem a recusa"], "rows": [
   ["ler além do fim do bloco", "o resultado é um número plausível, e o defeito aparece três camadas adiante"],
   ["um valor fora da faixa do tipo", "ele é truncado em silêncio, e o arquivo sai com outro número"],
   ["um campo que não existe", "a escrita iria para lugar nenhum — a mensagem sugere o nome parecido"],
   ["escrever num bloco somente leitura", "`bytes` não muda; a queixa sairia do Python, sobre outra coisa"],
   ["usar um bloco liberado", "lê-se o que ocupou o espaço depois"]]}},
 {"p": "A faixa vem do **tipo declarado**, e não do `struct` do Python: `um u8 vai de 0 a 255`, e não `'B' format requires 0 <= number <= 255` — quem escreveu `u8` não tem como ligar uma coisa à outra."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/ponteiros",
"title": "Ponteiros",
"description": "Aritmética por elemento, cast, distância — e as duas formas de um ponteiro não valer nada.",
"blocos": [
 {"h2": "Andar por elemento, e não por byte"},
 {"code": """p := Est.ponteiro(numeros, "u32")

out p.ler()
out p.mais(1).ler()          // o PRÓXIMO u32
out p.mais(1).endereco()     // 4 — e não 1
out p.cluster(4)             // os quatro a partir daqui""", "lang": "df"},
 {"p": "`p + 1` num `u32*` do C anda quatro bytes. Andar um byte é um índice, não um ponteiro — e é a conta que quem escreve C faz o tempo todo. `p.distancia(q)` responde na mesma unidade, e é recusada entre tipos diferentes: a conta é em elementos, e dois tipos têm tamanhos diferentes."},

 {"h2": "O cast"},
 {"code": """p.como("u8").mais(3).ler()   // os mesmos bytes, outro tipo""", "lang": "df"},

 {"h2": "As duas formas de não valer nada"},
 {"table": {"head": ["", "O que é"], "rows": [
   ["`Est.nulo()`", "o endereço existe e vale **zero**; lê-lo seria a falha de segmentação clássica"],
   ["bloco liberado", "o endereço continua na mão de alguém, e o bloco declarou o fim"]]}},
 {"code": """p := Est.nulo()
out p.e_nulo()      // yes
p.ler()             // NullPointerError

morto := Est.bloco(8)
q := Est.ponteiro(morto, "u32")
morto.liberar()
q.ler()             // DanglingPointerError""", "lang": "df"},
 {"p": "`NullPointerError` é diferente de `NullReferenceError`, que fala de um `void` da linguagem. Aqui o endereço existe."},

 {"h2": "O ponteiro segura o bloco — e isso é uma decisão"},
 {"callout": {"tipo": "nota", "titulo": "A referência fraca era uma armadilha",
              "texto": "A primeira versão guardava uma referência fraca, para imitar o C. O efeito: `Est.ponteiro(Est.bloco(8), \"u32\")` nascia pendurado, porque o bloco temporário morria assim que a chamada voltava. Um ponteiro cuja validade depende de a expressão ter sido guardada numa variável aparece e some conforme a contagem de referências — que é a pior classe de defeito. Num mundo com coletor a memória nunca esteve em risco; o que se protege é o **protocolo**, e ele tem um ponto só: `liberar()`."}},

 {"h2": "União"},
 {"code": """Valor := Est.uniao("Valor", [
    ["inteiro", "u32"],
    ["flutuante", "f32"]
], ordem := "rede")

Valor.escrever(caixa, {"flutuante": 1.0})
out Valor.ler(caixa)["inteiro"]     // 1065353216 — o IEEE 754 de 1.0""", "lang": "df"},
 {"p": "Todos os campos no mesmo deslocamento zero, e o tamanho é o do maior. Escrever um e ler outro devolve a reinterpretação dos bytes — que é o ponto de uma união, e também o que a torna perigosa quando o tipo escrito não é registrado em algum lugar."},

 {"h2": "O exemplo completo"},
 {"p": "`examples/estrutura_binaria.df` monta um arquivo com cabeçalho e três registros, percorre com janelas, escreve por ponteiro e demonstra as cinco recusas — com `assert` em cada afirmação."},
]},
]
