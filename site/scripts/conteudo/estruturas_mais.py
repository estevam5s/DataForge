# -*- coding: utf-8 -*-
"""Estruturas — catorze páginas, do tipo de um campo ao formato de
arquivo inteiro.

Entraram na linguagem nesta leva: os campos `char[N]` e `bytes[N]`,
`campos_de_bits`, `varint`/`ler_varint`, `zigzag`, `crc32`,
`trocar_ordem` e `mapear` (arquivo mapeado em memória). Os números que
as páginas afirmam foram conferidos contra referências externas: o
`struct` do Python, o `zlib`, o `ctypes` e os exemplos das próprias
especificações (Protocol Buffers, PNG, RFC 791).
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/tipos",
"title": "Os tipos de um campo",
"description": "Inteiros com e sem sinal, ponto flutuante, booleano, texto e bytes de tamanho fixo — e a faixa que cada um aceita.",
"blocos": [
 {"p": "Um campo binário não tem \"um número\": tem um número de **N bits**, com ou sem sinal. Escolher o tipo é escolher a faixa — e um valor fora dela, num formato binário, não dá erro sozinho: ele é **truncado**, e o arquivo sai com outro número. `Arcane.Estrutura` confere a faixa na escrita."},
 {"table": {"head": ["Tipo", "Bytes", "Faixa", "Uso típico"], "rows": [
   ["`u8` / `i8`", "1", "0 a 255 / −128 a 127", "byte cru, flag, contador pequeno"],
   ["`u16` / `i16`", "2", "0 a 65.535 / ±32.767", "porta de rede, amostra de áudio"],
   ["`u32` / `i32`", "4", "0 a 4,29 bi / ±2,1 bi", "tamanho de arquivo, id, cor RGBA"],
   ["`u64` / `i64`", "8", "0 a 1,8×10¹⁹", "timestamp em ns, deslocamento em arquivo grande"],
   ["`f32` / `f64`", "4 / 8", "~7 / ~15 dígitos", "medida física, coordenada"],
   ["`bool`", "1", "`yes` / `no`", "flag isolada"],
   ["`char` N", "N", "texto de até N bytes em UTF-8", "nome fixo, código de 4 letras"],
   ["`bytes` N", "N", "N bytes crus", "assinatura mágica, hash, chave"]]}},
 {"code": '''adopt Arcane.Estrutura as Est

Leitura := Est.definir("Leitura", [
    ["sensor", "u16"], ["temperatura", "f32"], ["ok", "bool"], ["rotulo", "char", 6]])

b := Leitura({"sensor": 7, "temperatura": 21.5, "ok": yes, "rotulo": "sala"})
assert Leitura.ler(b) is {"sensor": 7, "temperatura": 21.5, "ok": yes, "rotulo": "sala"}
assert Est.tamanho_de("u16") is 2 and Est.tamanho_de("f64") is 8

estourou := no
monitor:
    Leitura({"sensor": 70000})             // u16 vai até 65535
handle BufferOverflowError as e:
    estourou := yes
    out e.message
assert estourou''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`f32` perde precisão", "texto": "`21.5` volta 21.5 porque é exato em binário; `0.1` gravado em `f32` volta `0.10000000149011612`. Para dinheiro, nunca ponto flutuante: `i64` em centavos."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/alinhamento",
"title": "Alinhamento e enchimento",
"description": "Por que u8 + u32 + u16 ocupa 12 bytes e não 7, como reduzir, e quando empacotar.",
"blocos": [
 {"p": "O processador lê um `u32` mais depressa — e em algumas arquiteturas, **só** consegue lê-lo — quando ele começa num endereço múltiplo de 4. O compilador de C insere bytes vazios entre os campos para garantir isso, e também no fim do registro, para um vetor deles continuar alinhado. Esses bytes são o **enchimento**."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.C as C

campos := [["a", "u8"], ["b", "u32"], ["c", "u16"]]
alinhado := Est.definir("S", campos, "intel")
out alinhado.mapa()

assert alinhado.tamanho is 12                  // u8, três vazios, u32, u16, dois vazios
assert alinhado.enchimento() is 5
assert alinhado.tamanho is C.estrutura(campos).tamanho()   // o mesmo que o C faria

empacotado := Est.definir("S", campos, "intel", yes)
assert empacotado.tamanho is 7                 // o '#pragma pack(1)' do C''', "lang": "df"},
 {"h2": "Reordenar custa zero e economiza"},
 {"p": "Os mesmos campos, do maior para o menor, deixam de precisar de enchimento no meio. Num vetor de um milhão de registros, isso é um terço da memória:"},
 {"code": '''adopt Arcane.Estrutura as Est

bagunçado := Est.definir("A", [["a", "u8"], ["b", "u32"], ["c", "u16"]], "intel")
ordenado := Est.definir("B", [["b", "u32"], ["c", "u16"], ["a", "u8"]], "intel")
assert bagunçado.tamanho is 12 and ordenado.tamanho is 8''', "lang": "df"},
 {"table": {"head": ["Modo", "Use quando"], "rows": [
   ["alinhado (padrão)", "o registro vai para uma `struct` do C, ou vive na memória em vetor"],
   ["empacotado (`yes`)", "o formato de arquivo ou protocolo foi definido **sem** enchimento — quase todos"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Formato de arquivo quase nunca é alinhado", "texto": "PNG, WAV, ZIP e o cabeçalho IP foram desenhados byte a byte. Ler um deles com o molde alinhado desloca todo campo depois do primeiro enchimento — e os números lidos são plausíveis, que é o pior jeito de estar errado."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/ordem-dos-bytes",
"title": "A ordem dos bytes",
"description": "Big-endian, little-endian, a ordem da rede, e o bswap — com o mesmo número lido dos dois jeitos.",
"blocos": [
 {"p": "O número `0x12345678` ocupa quatro bytes, e há duas ordens para escrevê-los: o byte mais significativo primeiro (**big-endian**, `12 34 56 78`) ou o menos significativo primeiro (**little-endian**, `78 56 34 12`). Os processadores x86 e ARM usam little; os protocolos de rede e a maioria dos formatos de arquivo, big — por isso \"rede\" é o padrão aqui."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

N := Est.definir("N", [["v", "u32"]])                 // "rede" = big-endian
I := Est.definir("I", [["v", "u32"]], "intel")        // little-endian

assert Bytes.hex(N({"v": 0x12345678}).bytes()) is "12345678"
assert Bytes.hex(I({"v": 0x12345678}).bytes()) is "78563412"

// os MESMOS bytes, lidos na ordem errada, são outro número — sem erro nenhum
crus := N({"v": 1}).bytes()
assert I.ler(crus)["v"] is 16777216
assert Est.trocar_ordem(16777216, "u32") is 1''', "lang": "df"},
 {"table": {"head": ["Formato", "Ordem"], "rows": [
   ["TCP/IP, DNS, PNG, JPEG, Java class", "big-endian (rede)"],
   ["WAV, BMP, ZIP, executável do Windows", "little-endian"],
   ["TIFF", "está no próprio arquivo (`II` ou `MM`)"],
   ["Protocol Buffers", "varint — não tem ordem de palavra: ver [Varint](/docs/estruturas/varint)"]]}},
 {"callout": {"tipo": "dica", "titulo": "Qual é a desta máquina?", "texto": "`C.endianness()` responde — e a resposta quase nunca importa: o molde declara a ordem do **formato**, e ela vale em qualquer máquina. É exatamente por isso que a ordem é obrigatória."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/textos",
"title": "Texto de tamanho fixo",
"description": "O char[N] do C: completado com zeros, lido até o primeiro zero — e o acento que não cabe.",
"blocos": [
 {"p": "Muitos formatos guardam texto num espaço de **tamanho fixo**: o código `IHDR` de um chunk PNG, o nome de 16 caracteres de um registro antigo. O campo `char` com N bytes é esse espaço: escreve completando com zeros, e lê até o primeiro zero."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

Registro := Est.definir("Registro", [["codigo", "char", 4], ["nome", "char", 8]], "rede", yes)
b := Registro({"codigo": "AB", "nome": "Joana"})

assert Bytes.hex(b.bytes()) is "414200004a6f616e61000000"   // os zeros completam
assert Registro.ler(b) is {"codigo": "AB", "nome": "Joana"} // e somem na leitura''', "lang": "df"},
 {"h2": "O limite é em bytes, não em letras"},
 {"p": "O campo mede **bytes em UTF-8**, e um acento ocupa dois. \"João\" tem 4 letras e 5 bytes: não cabe num `char` de 4. Cortar em silêncio gravaria \"Jo\\xc3\" — metade de um caractere, e um texto inválido. O molde recusa:"},
 {"code": '''adopt Arcane.Estrutura as Est

Nome := Est.definir("Nome", [["n", "char", 4]])
recusado := no
monitor:
    Nome({"n": "João"})
handle BufferOverflowError as e:
    recusado := yes
assert recusado
assert Nome.ler(Nome({"n": "Joã"}))["n"] is "Joã"          // quatro bytes: cabe''', "lang": "df"},
 {"h2": "Bytes crus"},
 {"p": "`bytes` com N é o mesmo espaço, sem interpretação: a assinatura mágica de um arquivo, um hash, uma chave. Lê e escreve `Bytes`, e nunca corta no primeiro zero — porque ali o zero é dado."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

Cab := Est.definir("Cab", [["magica", "bytes", 4], ["versao", "u8"]], "rede", yes)
b := Cab({"magica": Bytes.de_hex("7f454c46"), "versao": 2})   // a assinatura do ELF
assert Bytes.hex(Cab.ler(b)["magica"]) is "7f454c46"''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/bits",
"title": "Campos de bits",
"description": "Versão e tamanho do IPv4 no mesmo byte, as flags do TCP em 16 bits — com máscara, e nunca com o bitfield do C.",
"blocos": [
 {"p": "Protocolos economizam: o primeiro byte do cabeçalho IPv4 guarda **dois** campos — a versão nos 4 bits de cima e o tamanho do cabeçalho nos 4 de baixo. `Est.campos_de_bits` descreve isso com nome, e o primeiro campo é o de **cima**, como toda RFC desenha."},
 {"code": '''adopt Arcane.Estrutura as Est

Ver_ihl := Est.campos_de_bits("Ver_ihl", [["versao", 4], ["ihl", 4]])
assert Ver_ihl.ler(0x45) is {"versao": 4, "ihl": 5}          // IPv4, 5 palavras de 32 bits
assert Ver_ihl.juntar({"versao": 4, "ihl": 5}) is 0x45
out Ver_ihl.mapa()''', "lang": "df"},
 {"h2": "As flags do TCP"},
 {"code": '''adopt Arcane.Estrutura as Est

Tcp := Est.campos_de_bits("Tcp", [
    ["deslocamento", 4], ["reservado", 3], ["ns", 1], ["cwr", 1], ["ece", 1],
    ["urg", 1], ["ack", 1], ["psh", 1], ["rst", 1], ["syn", 1], ["fin", 1]], 16)

syn_ack := Tcp.juntar({"deslocamento": 5, "syn": 1, "ack": 1})
assert syn_ack is 0x5012
flags := Tcp.ler(syn_ack)
assert flags["syn"] is 1 and flags["ack"] is 1 and flags["fin"] is 0''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O valor que invadiria o vizinho", "texto": "Um 16 num campo de 4 bits, somado sem conferir, liga o bit do campo **ao lado**. O defeito aparece no outro campo, e a busca começa no lugar errado. `juntar` recusa (`BufferOverflowError`), com a faixa do campo na mensagem."}},
 {"callout": {"tipo": "nota", "titulo": "Por que não o bitfield do C", "texto": "`unsigned versao:4;` deixa a ordem dos bits para o compilador — e dois compiladores escolhem diferente. Todo código de rede sério usa máscara e deslocamento, que é o que `campos_de_bits` faz, com a ordem declarada."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/operacoes-de-bits",
"title": "Operações de bits",
"description": "E, OU, OU exclusivo, NÃO com largura, deslocamento e contagem — como funções, e por que não operadores.",
"blocos": [
 {"p": "Máscara, flag, permissão em octal, cor num inteiro, soma de conferência: tudo isso é conta **bit a bit**. As funções moram em `Arcane.Estrutura`, com nomes que dizem o que fazem:"},
 {"table": {"head": ["Função", "Faz", "No C"], "rows": [
   ["`bits_e(a, b)`", "1 só onde os dois têm 1 — a máscara", "`a & b`"],
   ["`bits_ou(a, b)`", "liga o que estiver ligado em qualquer um", "`a | b`"],
   ["`bits_xou(a, b)`", "1 onde diferem; aplicado duas vezes, desfaz", "`a ^ b`"],
   ["`bits_nao(a, largura)`", "inverte dentro da largura", "`~a` (com o tipo dando a largura)"],
   ["`deslocar(a, n)`", "esquerda com n positivo, direita com negativo", "`a << n` / `a >> -n`"],
   ["`contar_uns(a)`", "quantos bits ligados", "`__builtin_popcount`"],
   ["`bit_ligado(a, i)` · `ligar_bit` · `desligar_bit`", "um bit só, contando de 0 embaixo", "máscara na mão"]]}},
 {"code": '''adopt Arcane.Estrutura as Est

// permissões do Unix: rwx para o dono, r-x para o grupo, r-- para os outros
steady LER := 4
steady ESCREVER := 2
steady EXECUTAR := 1
dono := Est.bits_ou(Est.bits_ou(LER, ESCREVER), EXECUTAR)
modo := Est.bits_ou(Est.bits_ou(Est.deslocar(dono, 6), Est.deslocar(5, 3)), 4)
assert modo is 0o754

grupo := Est.bits_e(Est.deslocar(modo, -3), 7)
assert grupo is 5
assert not Est.bit_ligado(grupo, 1)                // o grupo não escreve

assert Est.bits_nao(0b10110000, 8) is 0b01001111    // dentro de um byte
assert Est.contar_uns(0xFF) is 8
assert Est.bits_xou(Est.bits_xou(1234, 0xABCD), 0xABCD) is 1234''', "lang": "df"},
 {"h2": "Por que não operadores"},
 {"p": "Os três símbolos que toda linguagem usa já têm dono aqui: `>>` é o **pipeline**, `|` é a união de tipos e `&` a interseção. Um `a >> 2` que deslocasse bits mudaria o sentido de todo pipeline já escrito, e `a & b` numa anotação seria lido como tipo. Funções com nome não disputam nada — e `deslocar(x, -4)` diz o sentido, que é a dúvida de sempre com `>>`."},
 {"callout": {"tipo": "atencao", "titulo": "O NÃO precisa de largura", "texto": "O inteiro da linguagem não tem tamanho, e o NÃO de um número sem tamanho é negativo: `~5` no Python dá −6. `bits_nao(5, 8)` dá 250, que é o que quem inverte um byte quer — e recusa um número que não cabe na largura."}},
 {"p": "Para campos com nome dentro de um inteiro — versão e tamanho no mesmo byte —, [Campos de bits](/docs/estruturas/bits) é mais legível que máscara na mão."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/varint",
"title": "Varint e zigzag",
"description": "O inteiro de tamanho variável do Protocol Buffers e do WebAssembly: 7 bits por byte, e o truque para os negativos.",
"blocos": [
 {"p": "A maioria dos números de uma mensagem é pequena — ids, contagens, tamanhos. Gastar 8 bytes num `u64` para guardar um 3 é desperdício, e o **varint** (LEB128) resolve: 7 bits de dado por byte, e o bit alto diz \"ainda tem mais\". Um número menor que 128 ocupa **um** byte."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

assert Bytes.hex(Est.varint(1)) is "01"
assert Bytes.hex(Est.varint(150)) is "9601"         // o exemplo da doc do protobuf
assert Bytes.hex(Est.varint(300)) is "ac02"

lido := Est.ler_varint(Bytes.de_hex("ff9601ff"), 1)  // começando no byte 1
assert lido is {"valor": 150, "tamanho": 2}''', "lang": "df"},
 {"h2": "Negativos: zigzag"},
 {"p": "Em varint sem sinal, −1 é o maior número de 64 bits: **dez** bytes. O zigzag intercala os sinais — 0, −1, 1, −2, 2 viram 0, 1, 2, 3, 4 — e um −1 volta a caber em um byte. É o que o protobuf faz com `sint64`."},
 {"code": '''adopt Arcane.Estrutura as Est

assert [Est.zigzag(n) cycle n in [0, -1, 1, -2, 2]] is [0, 1, 2, 3, 4]
assert len(Est.varint(Est.zigzag(-1))) is 1
cycle n in [-1000, -1, 0, 7, 123456]:
    assert Est.desfazer_zigzag(Est.zigzag(n)) is n

recusou := no
monitor:
    Est.varint(-1)                    // sem zigzag, recusado — com a dica
handle LayoutError:
    recusou := yes
assert recusou''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O varint que não termina", "texto": "Dados cortados no meio de um varint têm o bit alto ligado no último byte. `ler_varint` levanta dizendo em que byte o número começou e quantos leu — em vez de ler o que vem depois como parte do número."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/png",
"title": "Ler um PNG de verdade",
"description": "Assinatura, chunks, tamanho em big-endian e o CRC de cada um — o formato inteiro, sem biblioteca de imagem.",
"blocos": [
 {"p": "Um PNG é uma assinatura de 8 bytes seguida de **chunks**: tamanho (`u32`, big-endian), tipo (4 letras), dados, e um CRC-32 do tipo mais os dados. O primeiro chunk é sempre `IHDR`, com largura, altura e profundidade de cor. Montamos um cabeçalho de verdade e o lemos de volta, conferindo o CRC:"},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

steady ASSINATURA := Bytes.de_hex("89504e470d0a1a0a")
Ihdr := Est.definir("Ihdr", [["largura", "u32"], ["altura", "u32"], ["profundidade", "u8"],
    ["cor", "u8"], ["compressao", "u8"], ["filtro", "u8"], ["entrelace", "u8"]], "rede", yes)

action chunk(tipo, dados):
    corpo := Bytes.concatenar(Bytes.de_texto(tipo), dados)
    yield Bytes.escrever(">").escrever("u32", len(dados)).escrever_bytes(corpo).escrever("u32", Est.crc32(corpo)).finalizar()

dados := Ihdr({"largura": 640, "altura": 480, "profundidade": 8, "cor": 6}).bytes()
png := Bytes.concatenar(ASSINATURA, chunk("IHDR", dados))

// ── ler ──
assert Bytes.fatiar(png, 0, 8) is ASSINATURA
l := Bytes.ler(Bytes.fatiar(png, 8), ">")
tamanho := l.ler("u32")
tipo := l.ler_texto(4)
corpo := l.ler_bytes(tamanho)
crc := l.ler("u32")
assert tipo is "IHDR" and tamanho is 13
assert crc is Est.crc32(corpo, Est.crc32(Bytes.de_texto(tipo)))   // CRC em duas partes
assert Ihdr.ler(corpo)["largura"] is 640''', "lang": "df"},
 {"list": [
   "**A assinatura primeiro.** Ela tem um `\\r\\n` e um `\\n` de propósito: um arquivo que passou por conversão de fim de linha tem a assinatura estragada, e o erro aparece aqui — e não como uma imagem corrompida.",
   "**O CRC antes de confiar.** Um chunk com CRC errado é recusado antes de os dados serem interpretados.",
   "**`crc32(dados, inicial)` continua uma conta.** O CRC do PNG é do tipo **mais** os dados; calcular em duas partes evita concatenar os dois só para conferir."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/wav",
"title": "Escrever um WAV",
"description": "O cabeçalho RIFF de 44 bytes, em little-endian, e um segundo de onda senoidal escrito amostra por amostra.",
"blocos": [
 {"p": "O WAV é o formato de áudio mais simples que existe: 44 bytes de cabeçalho **little-endian** e depois as amostras. É um bom exercício justamente por ser little-endian — ler com o molde padrão (big-endian) dá números absurdos e nenhum erro."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes
adopt Arcane.Math as M

Wav := Est.definir("Wav", [
    ["riff", "char", 4], ["tamanho", "u32"], ["wave", "char", 4],
    ["fmt", "char", 4], ["fmt_tamanho", "u32"], ["formato", "u16"], ["canais", "u16"],
    ["taxa", "u32"], ["bytes_por_segundo", "u32"], ["alinhamento", "u16"], ["bits", "u16"],
    ["data", "char", 4], ["data_tamanho", "u32"]], "intel", yes)
assert Wav.tamanho is 44

taxa := 8000
amostras := [int(M.sin(2 * M.PI * 440 * i / taxa) * 8000) cycle i in range(taxa)]
corpo := Bytes.escrever("<")
cycle a in amostras:
    corpo.escrever("i16", a)
audio := corpo.finalizar()

cab := Wav({"riff": "RIFF", "tamanho": 36 + len(audio), "wave": "WAVE", "fmt": "fmt ",
    "fmt_tamanho": 16, "formato": 1, "canais": 1, "taxa": taxa,
    "bytes_por_segundo": taxa * 2, "alinhamento": 2, "bits": 16,
    "data": "data", "data_tamanho": len(audio)})
arquivo := Bytes.concatenar(cab.bytes(), audio)

lido := Wav.ler(arquivo)
assert lido["riff"] is "RIFF" and lido["taxa"] is 8000
assert lido["data_tamanho"] is 16000                  // um segundo de 16 bits mono
assert len(arquivo) is 16044''', "lang": "df"},
 {"p": "Grave com `IO.write_bytes(\"la.wav\", arquivo)` e qualquer tocador reproduz um lá de 440 Hz. `IO.write` não serve: ele abre em modo texto, e bytes de áudio não são texto."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/protocolo",
"title": "Um protocolo binário",
"description": "Mensagens TLV — tipo, tamanho, valor — com varint: escrever, ler, e o campo desconhecido que não quebra ninguém.",
"blocos": [
 {"p": "TLV (tipo-tamanho-valor) é o desenho que sobrevive a versões: cada campo diz o próprio tamanho, então quem lê pode **pular** um campo que não conhece. É a mesma ideia do Protocol Buffers, e o motivo pelo qual um cliente antigo lê a mensagem de um servidor novo."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

steady NOME := 1
steady IDADE := 2
steady FOTO := 9                     // um campo que a versão antiga não conhece

action campo(tipo, valor):
    yield Bytes.concatenar(Est.varint(tipo), Est.varint(len(valor)), valor)

action mensagem(campos):
    yield campos >> distill acc, c: Bytes.concatenar(acc, c) Bytes.de_texto("")

action ler(dados, conhecidos):
    saida := {}
    pos := 0
    persist pos smaller len(dados):
        t := Est.ler_varint(dados, pos)
        n := Est.ler_varint(dados, pos + t["tamanho"])
        inicio := pos + t["tamanho"] + n["tamanho"]
        given inicio + n["valor"] bigger len(dados):
            trigger $"o campo {t["valor"]} diz ter {n["valor"]} bytes e a mensagem acaba antes"
        given t["valor"] in conhecidos:
            saida[conhecidos[t["valor"]]] := Bytes.fatiar(dados, inicio, inicio + n["valor"])
        pos := inicio + n["valor"]            // o desconhecido é PULADO
    yield saida

m := mensagem([campo(NOME, Bytes.de_texto("Ana")), campo(FOTO, Bytes.de_hex("ffd8ffe0")),
               campo(IDADE, Est.varint(30))])
lido := ler(m, {NOME: "nome", IDADE: "idade"})
assert Bytes.para_texto(lido["nome"]) is "Ana"
assert Est.ler_varint(lido["idade"])["valor"] is 30''', "lang": "df"},
 {"callout": {"tipo": "perigo", "titulo": "O tamanho vem de fora", "texto": "O tamanho de cada campo é **dado da mensagem**, e uma mensagem maliciosa diz ter 4 GB. Conferir `inicio + tamanho` contra o que chegou — antes de fatiar — é o que separa um erro legível de ler memória que não é desta mensagem. Ver [Entrada hostil](/docs/estruturas/entrada-hostil)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/arquivo-mapeado",
"title": "Arquivo mapeado em memória",
"description": "Um arquivo de gigabytes como um bloco, sem lê-lo inteiro: o sistema traz só as páginas tocadas.",
"blocos": [
 {"p": "`IO.read_bytes` lê o arquivo **inteiro** para a memória. Para um arquivo de 4 GB cujo cabeçalho de 64 bytes você quer ler, isso são 4 GB de leitura. `Est.mapear` entrega o arquivo como um `Bloco`, e o sistema operacional traz para a memória só as páginas que forem tocadas."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-mapa-{randint(100000, 999999)}"
IO.mkdir(pasta)
caminho := $"{pasta}/contadores.bin"

Contador := Est.definir("Contador", [["id", "u32"], ["visitas", "u64"]], "rede", yes)
IO.write_bytes(caminho, Est.bloco(Contador.tamanho * 3).bytes())   // três registros zerados

mapa := Est.mapear(caminho, yes)                   // yes: para escrever
registros := Est.janelas(mapa, Contador)
registros[1]["id"] := 7
registros[1]["visitas"] := registros[1]["visitas"] + 1
mapa.sincronizar()                                 // garante que chegou ao disco
mapa.liberar()

de_novo := Est.janelas(IO.read_bytes(caminho), Contador)
assert de_novo[1]["id"] is 7 and de_novo[1]["visitas"] is 1
IO.remove_tree(pasta)''', "lang": "df"},
 {"table": {"head": ["Use", "Quando"], "rows": [
   ["`IO.read_bytes`", "arquivo pequeno, lido inteiro de qualquer jeito"],
   ["`Est.mapear(c)`", "arquivo grande, e você lê pedaços — um índice, um cabeçalho"],
   ["`Est.mapear(c, yes)`", "atualizar registros no lugar, sem reescrever o arquivo"]]}},
 {"list": [
   "**Só leitura por padrão.** Escrever num mapa aberto sem `yes` é recusado com a dica — e não um `TypeError` do sistema.",
   "**O arquivo não pode estar vazio**: o mapa de zero bytes não existe. Crie-o no tamanho que o formato exige antes.",
   "**`sincronizar()` antes de confiar.** Sem ele, o que foi escrito pode ainda estar só na memória quando outro processo lê o arquivo.",
   "**`liberar()` fecha o mapa.** Toda janela sobre ele passa a recusar leitura — em vez de ler memória que já não é do arquivo."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/conferencia",
"title": "CRC e soma de conferência",
"description": "CRC-32 do PNG e do ZIP, e a soma de complemento de um do cabeçalho IP — com o vetor da RFC.",
"blocos": [
 {"p": "Um dado que atravessou disco ou rede pode chegar com um bit trocado, e um número com um bit trocado é **outro número válido**. A conferência é um resumo pequeno, gravado junto, que muda quando qualquer bit muda."},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

dados := Bytes.de_texto("DataForge")
crc := Est.crc32(dados)
alterado := Bytes.de_texto("DataForgf")       // um caractere de diferença
assert Est.crc32(alterado) is not crc
assert crc is Est.crc32(Bytes.de_texto("Forge"), Est.crc32(Bytes.de_texto("Data")))''', "lang": "df"},
 {"h2": "A soma do cabeçalho IPv4"},
 {"p": "O IP usa algo mais simples que o CRC: a soma, em complemento de um, das palavras de 16 bits do cabeçalho. Com o exemplo clássico (192.168.0.1 → 192.168.0.199), a soma tem de dar `b861` — e somar o cabeçalho **com** a soma tem de dar zero:"},
 {"code": '''adopt Arcane.Bytes as Bytes

adopt Arcane.Estrutura as Est

action soma_ip(cabecalho):
    total := 0
    cycle i in range(0, len(cabecalho), 2):
        total += Est.deslocar(cabecalho[i], 8) + cabecalho[i + 1]
    persist total bigger 0xFFFF:                 // dobra o "vai um" de volta
        total := Est.bits_e(total, 0xFFFF) + Est.deslocar(total, -16)
    yield Est.bits_nao(total, 16)                // o complemento de um

sem_soma := Bytes.de_hex("450000730000400040110000c0a80001c0a800c7")
assert soma_ip(sem_soma) is 0xb861

com_soma := Bytes.de_hex("45000073000040004011b861c0a80001c0a800c7")
assert soma_ip(com_soma) is 0              // o receptor confere assim''', "lang": "df"},
 {"table": {"head": ["", "Pega", "Não pega", "Onde"], "rows": [
   ["soma de complemento de um", "um bit trocado", "duas palavras trocadas de lugar", "IP, TCP, UDP"],
   ["CRC-32", "rajadas de erro de até 32 bits", "adulteração intencional", "PNG, ZIP, gzip, Ethernet"],
   ["SHA-256 / HMAC", "qualquer mudança, inclusive proposital", "—", "`Arcane.Crypto`, `Arcane.Integridade`"]]}},
 {"callout": {"tipo": "perigo", "titulo": "CRC não é segurança", "texto": "Quem altera o arquivo de propósito recalcula o CRC em microssegundos. Para saber se alguém **mexeu**, é hash criptográfico com chave: [`Arcane.Integridade`](/docs/seguranca/integridade)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/entrada-hostil",
"title": "Ler entrada hostil",
"description": "Todo tamanho que vem do arquivo é suspeito: as cinco conferências antes de interpretar um byte.",
"blocos": [
 {"p": "Um leitor de formato binário é a porta mais atacada de um sistema: o arquivo vem de fora, e cada número dentro dele — tamanho, contagem, deslocamento — decide **quanto** o programa vai ler e **onde**. Em C, confiar num desses números é o estouro de buffer clássico. Aqui a memória não corre risco, mas o programa ainda pode travar, alocar gigabytes ou ler o lugar errado."},
 {"table": {"head": ["Confira", "Contra", "Senão"], "rows": [
   ["a assinatura", "a constante do formato", "interpreta um arquivo de outro formato"],
   ["o tamanho declarado", "o que realmente chegou", "fatia além do fim"],
   ["a contagem", "um teto razoável", "aloca um cluster de um bilhão de itens"],
   ["o deslocamento", "o intervalo do próprio arquivo", "lê fora dele"],
   ["a conferência (CRC)", "os dados", "interpreta lixo como dado válido"]]}},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

steady MAX_ITENS := 10000
Cab := Est.definir("Cab", [["magica", "char", 4], ["quantos", "u32"]], "rede", yes)
Item := Est.definir("Item", [["id", "u32"]], "rede", yes)

action ler_lista(dados):
    given len(dados) smaller Cab.tamanho:
        trigger "arquivo menor que o cabeçalho"
    cab := Cab.ler(dados)
    given cab["magica"] is not "LIST":
        trigger $"assinatura '{cab["magica"]}' não é de uma lista"
    given cab["quantos"] bigger MAX_ITENS:
        trigger $"{cab["quantos"]} itens passa do teto de {MAX_ITENS}"
    precisa := Cab.tamanho + cab["quantos"] * Item.tamanho
    given precisa bigger len(dados):
        trigger $"declara {cab["quantos"]} itens ({precisa} bytes) e o arquivo tem {len(dados)}"
    yield [j["id"] cycle j in Est.janelas(dados, Item, cab["quantos"], Cab.tamanho)]

bom := Bytes.concatenar(Cab({"magica": "LIST", "quantos": 2}).bytes(),
    Item({"id": 7}).bytes(), Item({"id": 9}).bytes())
assert ler_lista(bom) is [7, 9]

mentiroso := Cab({"magica": "LIST", "quantos": 4000000000}).bytes()
recusado := void
monitor:
    ler_lista(mentiroso)
handle Error as e:
    recusado := e.message
assert recusado.contains("teto")''', "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Teste com lixo", "texto": "O teste que mais acha defeito num leitor binário é o de propriedade: milhares de entradas aleatórias, e a única exigência é que o leitor **recuse com erro da linguagem** — nunca trave, nunca estoure memória. Ver [Teste por propriedade](/docs/crucible/propriedades)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/de-c-para-dataforge",
"title": "De uma struct do C para um molde",
"description": "Traduzir uma struct, conferir o layout contra o próprio C, e o #pragma pack.",
"blocos": [
 {"p": "Quando o formato vem descrito como uma `struct` do C — num cabeçalho `.h`, numa especificação antiga —, a tradução é campo a campo. O que muda de uma plataforma para outra é o **tamanho** de alguns tipos do C, e o alinhamento. A tabela resolve o primeiro; o `Arcane.C` confere o segundo contra o compilador de verdade."},
 {"table": {"head": ["No C", "No molde", "Cuidado"], "rows": [
   ["`uint8_t`, `unsigned char`", "`u8`", "—"],
   ["`int16_t`, `short`", "`i16`", "`short` é 16 bits em toda plataforma comum"],
   ["`int32_t`, `int`", "`i32`", "`int` é 32 bits em toda plataforma comum"],
   ["`long`", "`i64` no Linux/macOS, `i32` no Windows", "o motivo de usar `int32_t` no C"],
   ["`float` / `double`", "`f32` / `f64`", "—"],
   ["`char nome[16]`", "`[\"nome\", \"char\", 16]`", "lido até o primeiro zero"],
   ["`uint8_t hash[32]`", "`[\"hash\", \"bytes\", 32]`", "nunca cortado"],
   ["`__attribute__((packed))`, `#pragma pack(1)`", "`Est.definir(…, ordem, yes)`", "—"]]}},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.C as C

// struct Ponto3D { uint8_t marca; float x, y, z; uint16_t cor; };
campos := [["marca", "u8"], ["x", "f32"], ["y", "f32"], ["z", "f32"], ["cor", "u16"]]

molde := Est.definir("Ponto3D", campos, "intel")
assert molde.tamanho is C.estrutura(campos).tamanho()     // vinte, como o compilador
assert molde.deslocamento("x") is 4                       // três bytes de enchimento
assert Est.alinhamento_de(molde) is 4''', "lang": "df"},
 {"p": "Se o dado vai **para** uma função C, o caminho é o [`Arcane.C`](/docs/ffi/ponteiros), que monta a struct na memória que o C lê. `Arcane.Estrutura` é para quando o dado é um arquivo ou um pacote de rede — e não precisa de biblioteca nativa nenhuma."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/estruturas/receitas",
"title": "Receitas binárias",
"description": "Hexdump, cor RGBA num u32, deslocamento de bits sem molde, e um vetor de registros ordenado no lugar.",
"blocos": [
 {"h2": "Olhar os bytes"},
 {"code": '''adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

P := Est.definir("P", [["id", "u16"], ["nome", "char", 6]], "rede", yes)
out Bytes.despejo(P({"id": 258, "nome": "ana"}).bytes())
assert Bytes.hex(P({"id": 258, "nome": "ana"}).bytes()).starts_with("0102616e61")''', "lang": "df"},
 {"h2": "Uma cor RGBA num u32"},
 {"code": '''adopt Arcane.Estrutura as Est

Rgba := Est.campos_de_bits("Rgba", [["r", 8], ["g", 8], ["b", 8], ["a", 8]], 32)
laranja := Rgba.juntar({"r": 255, "g": 165, "b": 0, "a": 255})
assert laranja is 0xFFA500FF
assert Rgba.ler(laranja)["g"] is 165''', "lang": "df"},
 {"h2": "Ordenar registros no lugar"},
 {"code": '''adopt Arcane.Estrutura as Est

Nota := Est.definir("Nota", [["aluno", "u16"], ["nota", "u8"]], "rede", yes)
bloco := Est.bloco(Nota.tamanho * 3)
dados := [[1, 7], [2, 10], [3, 4]]
cycle i in range(3):
    Nota.escrever(bloco, {"aluno": dados[i][0], "nota": dados[i][1]}, i * Nota.tamanho)

// lê, ordena os VALORES, e regrava — o bloco continua o mesmo
lidos := [Nota.ler(bloco, i * Nota.tamanho) cycle i in range(3)]
ordenados := sorted(lidos, lambda n: -n["nota"])
cycle i in range(3):
    Nota.escrever(bloco, ordenados[i], i * Nota.tamanho)
assert [j["aluno"] cycle j in Est.janelas(bloco, Nota)] is [2, 1, 3]''', "lang": "df"},
]},
]
