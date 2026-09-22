# -*- coding: utf-8 -*-
"""Os seis módulos que fecharam os buracos da biblioteca.

Cada um existe porque alguma coisa comum não tinha como ser feita em
DataForge. As páginas dizem qual era o buraco antes de dizer como se
usa — o "para quê" é o que falta em quase toda documentação de API.
"""


def cod(texto, lang="df"):
    return {"code": texto.strip("\n"), "lang": lang}


PAGINAS = [

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/biblioteca/url",
"title": "Arcane.Url",
"description": "Endereços: ler em partes, montar de volta, resolver relativo e escapar o que precisa ser escapado.",
"blocos": [
 {"p": "Todo programa que fala HTTP mexe com URL, e a linguagem não tinha onde. O Kiln partia a query string por dentro para entregar `req[\"query\"]`, e o `Arcane.Http` montava endereço concatenando texto — nada disso estava ao alcance de quem escreve."},
 cod("""
adopt Arcane.Url as U

p := U.ler("https://loja.com/itens?pagina=2&q=caf%C3%A9#topo")
out p["host"]        // loja.com
out p["query"]       // {pagina: 2, q: café}
out p["porta"]       // void — a URL não disse
"""),
 {"h2": "Por que não dá para fazer com split"},
 {"p": "Dois bugs conhecidos: o `?` que também aparece **dentro** de um valor, e o acento que precisa virar `%C3%A9` — e não virava. Escapar à mão erra na primeira busca com espaço."},
 cod("""
U.escapar("/itens/ação nova")      // /itens/a%C3%A7%C3%A3o%20nova
U.escapar_tudo("/itens/ação")      // %2Fitens%2Fa%C3%A7%C3%A3o
U.desescapar("caf%C3%A9+quente")   // café quente
"""),
 {"h2": "A chave que repete"},
 {"p": "`?tag=a&tag=b` é legítimo e comum em filtro de busca, e um vault não guarda as duas. `query` devolve a **última** (o que quase todo servidor usa) e `query_lista` devolve as duas — a diferença está escrita, em vez de virar surpresa."},
 cod("""
p := U.ler("https://a.com/b?tag=a&tag=b")
out p["query"]["tag"]         // b
out p["query_lista"]["tag"]   // [a, b]
"""),
 {"h2": "Montar, e paginar"},
 {"p": "`montar` é o contrário de `ler`, e recusa campo que não conhece: `caminh` montaria um endereço **sem caminho**, sem nada denunciando. `com_query` troca um parâmetro e preserva os outros — é o que se faz para paginar —, e `void` ali **apaga** o parâmetro, como se tira um filtro."},
 cod("""
U.montar({"esquema": "https", "host": "a.com", "caminho": "/b",
          "query": {"q": "com espaço", "tags": ["p", "q"]}})
// https://a.com/b?q=com+espa%C3%A7o&tags=p&tags=q

U.com_query("https://a.com/l?pagina=1&q=z", {"pagina": 3})
// https://a.com/l?pagina=3&q=z

U.com_query("https://a.com/l?pagina=1&q=z", {"q": void})
// https://a.com/l?pagina=1

U.juntar("https://a.com/doc/x", "../y")     // https://a.com/y
"""),
 {"callout": {"tipo": "atencao", "titulo": "A porta é Integer, e a origem não leva senha", "texto": "A porta vem de texto na URL, e devolvê-la como texto faria `porta + 1` **concatenar** em vez de somar. Sem porta, `void` — e não 80, que seria inventar o que a URL não disse. E `origem` traz só esquema, host e porta: ela vai para log e para cabeçalho de CORS, e a senha de `https://ana:s3nha@a.com` vazaria por ali sem ninguém pedir."}},
],
},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/biblioteca/bytes",
"title": "Arcane.Bytes",
"description": "Dados binários: empacotar com a ordem declarada, um cursor que anda, e a janela que olha sem copiar.",
"blocos": [
 {"p": "A linguagem tem o tipo `Bytes`, e não havia o que fazer com ele. Ler um arquivo binário, falar um protocolo, montar um cabeçalho de quatro bytes — tudo isso pedia sair da linguagem."},

 {"h2": "A ordem dos bytes é obrigatória"},
 {"p": "`empacotar(\"i32\", 1)` **não existe** aqui. O formato sempre diz a ordem:"},
 cod("""
Bytes.empacotar(">i32", 1)     // 00 00 00 01   ordem de rede
Bytes.empacotar("<i32", 1)     // 01 00 00 00   ordem do Intel
"""),
 {"callout": {"tipo": "perigo", "titulo": "Por que ela não pode ser opcional",
              "texto": "Um inteiro escrito na ordem da **máquina** e lido na ordem da rede dá um número diferente, o programa **não falha**, e o dado sai errado do outro lado. É a falha mais cara desta área inteira, e um padrão silencioso a esconderia até o dia em que o servidor mudasse de arquitetura."}},

 {"h2": "Os tipos"},
 {"table": {"head": ["Escrita", "O quê", "Bytes"], "rows": [
   ["`i8` `u8`", "inteiro de 8 bits, com e sem sinal", "1"],
   ["`i16` `u16`", "16 bits", "2"],
   ["`i32` `u32`", "32 bits", "4"],
   ["`i64` `u64`", "64 bits", "8"],
   ["`f32` `f64`", "ponto flutuante", "4 / 8"],
   ["`bool`", "verdadeiro ou falso", "1"],
   ["`bytesN`", "um bloco de tamanho fixo", "N"],
 ]}},
 {"p": "Os nomes dizem o **tamanho em bits**, e não uma letra. `i32` é um inteiro de 32 bits em qualquer máquina; o `int` do C não é — e descobrir isso depois de gravar um arquivo é caro."},

 {"h2": "Um cabeçalho de protocolo"},
 cod("""
adopt Arcane.Bytes as Bytes

// versão (1), tipo (1), tamanho (4) — escrito assim, e não com contas
cabecalho := Bytes.empacotar(">u8 u8 u32", 1, 7, 1024)
out Bytes.hex(cabecalho, " ")          // mostra 01 07 00 00 04 00

partes := Bytes.desempacotar(">u8 u8 u32", cabecalho)
assert partes is [1, 7, 1024]
"""),

 {"h2": "O cursor anda sozinho"},
 {"p": "Ler com fatias exige calcular o deslocamento de cada campo, e **um erro num deles desalinha tudo o que vem depois** — com o programa entregando números plausíveis e errados."},
 cod("""
leitor := Bytes.ler(mensagem)

versao := leitor.ler("u8")
tipo := leitor.ler("u8")
tamanho := leitor.ler("u32")
corpo := leitor.ler_bytes(tamanho)

assert leitor.acabou
"""),
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`leitor.ler(tipo)`", "um campo, e anda"],
   ["`leitor.ler(tipo, n)`", "`n` campos iguais"],
   ["`leitor.ler_bytes(n)`", "um bloco"],
   ["`leitor.ler_texto(n)`", "um bloco, como texto"],
   ["`leitor.ler_ate_zero()`", "texto terminado em zero, como num formato antigo"],
   ["`leitor.espiar(n)`", "olha **sem** andar, para decidir o que vem"],
   ["`leitor.pular(n)` · `leitor.ir_para(p)`", "move o cursor"],
   ["`leitor.resto()`", "tudo o que sobrou"],
   ["`leitor.sobrou` · `leitor.acabou`", "onde estamos"],
 ]}},
 {"p": "Ler além do fim diz **quanto falta**, em vez de estourar calado:"},
 cod("""
erro: faltam bytes para ler 'u32': o cursor está em 1, o campo pede 4
      e só há 1 até o fim.
""", "text"),

 {"h2": "Escrever"},
 cod("""
e := Bytes.escrever()
e.escrever("u8", 2)
e.escrever("u32", 99)
e.escrever_texto("fim", com_zero := yes)
bloco := e.finalizar()
"""),

 {"h2": "A janela não copia"},
 {"p": "Copiar um arquivo de 200 MB para ler 8 bytes é o jeito mais fácil de estourar a memória. A janela aponta para os mesmos bytes:"},
 cod("""
pedaco := Bytes.janela(arquivo_inteiro, 100, 108)   // não copia
guardado := Bytes.copiar(pedaco)                    // agora sim
"""),

 {"h2": "Ver o que está errado"},
 {"p": "O despejo é o que se olha quando o protocolo não bate — posição, hexadecimal e o texto legível, lado a lado:"},
 cod("""out Bytes.despejo(mensagem)"""),
 cod("""00000000  01 07 00 00 04 00 44 61 74 61 46 6f 72 67 65     |......DataForge|""", "text"),

 {"h2": "Segredo se compara em tempo fixo"},
 cod("""
given Bytes.igual_em_tempo_fixo(token_recebido, token_certo):
    out "ok"
"""),
 {"callout": {"tipo": "perigo", "titulo": "Por que não `is`",
              "texto": "Uma comparação comum para no primeiro byte diferente, e o **tempo** conta quantos bateram. Com isso, um atacante descobre um token byte a byte — sem nunca acertar o token inteiro por sorte."}},

 {"h2": "O resto"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`hex(dados[, sep])` · `de_hex(texto)`", "hexadecimal, ida e volta"],
   ["`base64(dados)` · `de_base64(texto)`", "base64"],
   ["`bits(dados)` · `de_bits(texto)`", "a representação em bits"],
   ["`de_texto(t)` · `para_texto(d)`", "texto ⇄ bytes"],
   ["`concatenar(...)` · `fatiar(d, i, f)`", "juntar e cortar"],
   ["`ou_exclusivo(a, b)`", "XOR byte a byte"],
   ["`preencher(d, n, com, a_esquerda)`", "completa até o tamanho"],
   ["`achar(d, agulha)` · `dividir(d, sep)`", "procurar"],
   ["`inverter(d)`", "de trás para frente"],
 ]}},
 {"cards": [{"href": "/docs/exercicios/34-binario-e-rede", "title": "O exercício 235",
             "desc": "Monta e lê um cabeçalho de protocolo, e prova cada afirmação desta página."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/biblioteca/rede",
"title": "Arcane.Rede",
"description": "TCP, UDP, DNS e TLS — o que está abaixo do HTTP.",
"blocos": [
 {"p": "O [Kiln](/docs/kiln) fala HTTP e a [Malha](/docs/tecnicas/microservicos) fala com outro serviço. **Abaixo disso não havia nada**: um protocolo próprio, um agente que manda uma linha por UDP, ou descobrir para onde um nome aponta pediam sair da linguagem."},
 {"p": "E o TLS estava na lista do que **não existe**, na própria documentação. Ele existe agora, dos dois lados."},

 {"h2": "TCP"},
 cod("""
adopt Arcane.Rede as Rede

action atender(conexao):
    pedido := conexao.receber_linha()
    conexao.enviar_linha(pedido.upper())

Rede.servir(atender, host := "0.0.0.0", porta := 9000)
"""),
 cod("""
cliente := Rede.conectar("127.0.0.1", 9000)
cliente.enviar_linha("forja")
out cliente.receber_linha()        // FORJA
cliente.fechar()
"""),

 {"h3": "O TCP não tem fronteira de mensagem"},
 {"p": "Ele entrega um **fluxo de bytes**, e não mensagens. O formato mais comum para resolver isso é tamanho + corpo:"},
 cod("""
adopt Arcane.Bytes as Bytes

action mandar(conexao, texto):
    dados := Bytes.de_texto(texto)
    conexao.enviar(Bytes.empacotar(">u32", len(dados)))
    conexao.enviar(dados)

action receber(conexao):
    quanto := Bytes.desempacotar(">u32", conexao.receber_exato(4))[0]
    yield Bytes.para_texto(conexao.receber_exato(quanto))
"""),
 {"callout": {"tipo": "atencao", "titulo": "`receber_exato`, e não `receber`",
              "texto": "O `recv` devolve **menos** do que se pediu com frequência num pedaço que atravessa pacotes. Tratar o retorno curto como a mensagem inteira corrompe a próxima — e o sintoma é uma conexão que funciona e de repente para."}},

 {"h3": "Ler"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`receber(n, prazo)`", "o que chegou, até `n` bytes"],
   ["`receber_exato(n, prazo)`", "insiste até completar `n`"],
   ["`receber_linha(prazo, limite)`", "até a quebra, **com teto**"],
   ["`receber_tudo(prazo, limite)`", "até o outro lado fechar"],
   ["`enviar(dados)` · `enviar_linha(t)`", "manda tudo, sem devolver pela metade"],
 ]}},
 {"callout": {"tipo": "perigo", "titulo": "O prazo tem padrão, e o limite também",
              "texto": "Uma leitura sem prazo é a forma mais comum de um serviço travar para sempre: o outro lado caiu sem fechar o socket, e o `recv` fica esperando um byte que nunca vem. E uma linha sem teto deixa um cliente que nunca manda `\\n` encher a memória do servidor — um ataque de uma linha."}},

 {"h2": "UDP"},
 {"p": "Manda e esquece: sem conexão, sem ordem, sem garantia. É o **certo** para métrica, descoberta e log — onde perder um pacote custa menos que a espera de confirmar cada um."},
 cod("""
coletor := Rede.udp(porta := 8125, escutar := yes)
chegou := coletor.receber()
out chegou["host"], chegou["dados"]

agente := Rede.udp()
agente.enviar("pedidos=42", "127.0.0.1", 8125)
"""),

 {"h2": "DNS"},
 cod("""
out Rede.resolver("dataforge-lang.vercel.app")
// [{ip: 76.76.21.21, versao: 4}, …]

out Rede.nome_de("8.8.8.8")      // dns.google
out Rede.meu_ip()                // o IP com que esta máquina sai
"""),
 {"callout": {"tipo": "nota", "titulo": "`meu_ip` não é `gethostbyname`",
              "texto": "Numa máquina com `/etc/hosts` comum, resolver o próprio nome devolve `127.0.0.1` e não serve para nada. Abrir um socket UDP para fora (sem mandar nada) faz o sistema escolher a interface de verdade."}},

 {"h2": "Portas"},
 cod("""
porta := Rede.porta_livre()                          // livre agora
given Rede.porta_aberta("db", 5432):
    out "o banco está de pé"

Rede.esperar_porta("api", 8080, prazo := 30.0)       // espera subir
"""),
 {"p": "`esperar_porta` substitui o *\"sobe o serviço e dorme dois segundos torcendo para dar tempo\"* de todo script de integração. Quando ela desiste, diz o que costuma ser:"},
 cod("""
erro: api:8080 não abriu em 30s.
  O serviço não subiu, subiu em outra porta, ou subiu em
  127.0.0.1 quando deveria ser 0.0.0.0.
""", "text"),
 {"callout": {"tipo": "atencao", "titulo": "`porta_aberta` abre uma conexão de verdade",
              "texto": "Não há como perguntar sem bater na porta. Um servidor que conta conexões vai ver esta também — e um que lê uma linha logo de cara vai receber o fim da conexão."}},

 {"h2": "TLS"},
 cod("""
// cliente
seguro := Rede.conectar("api.exemplo.br", 443, tls := yes)

// servidor
Rede.servir(atender, porta := 443,
    tls := {"certificado": "cert.pem", "chave": "chave.pem"})
"""),
 {"h3": "O certificado que vence sem avisar"},
 {"p": "Um certificado vencido derruba o site inteiro, e o aviso chega pelo cliente reclamando. Isto é o que um monitor pergunta:"},
 cod("""
ficha := Rede.certificado_de("dataforge-lang.vercel.app")
out ficha["emissor"], ficha["valido_ate"], ficha["nomes"]

given Rede.dias_ate_vencer("api.exemplo.br") smaller 14:
    alertar("o certificado vence em menos de duas semanas")
"""),
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/biblioteca/eventos",
"title": "Arcane.Eventos",
"description": "Publicar e assinar sem as duas partes se conhecerem, contexto por thread e fila de trabalho.",
"blocos": [
 {"p": "Duas partes de um programa que precisam conversar sem se conhecer. O Kiln tem `Sala` para WebSocket e o [Lavra](/docs/lavra) tem `Fonte` para assinatura — os dois resolvem o mesmo problema para um transporte específico, e faltava a peça geral."},

 {"h2": "Emissor"},
 cod("""
adopt Arcane.Eventos as Eventos

loja := Eventos.emissor("loja")

loja.ao("venda", lambda pedido: gravar_nota(pedido))
loja.ao("venda", lambda pedido: avisar_estoque(pedido))

quantos := loja.emitir("venda", pedido)
"""),
 {"callout": {"tipo": "dica", "titulo": "`emitir` devolve quantos ouviram",
              "texto": "Zero é **informação**: o evento com o nome errado não falha, ele simplesmente não chega — e essa é a falha mais difícil de achar num sistema de eventos."}},

 {"h2": "O ouvinte que quebra sai"},
 {"p": "Um ouvinte quebrado que continua inscrito quebra **a cada evento**, para sempre, e some no meio do log. Ele é removido, e o erro vai para a lista:"},
 cod("""
out loja.erros            // [{evento: venda, erro: …, quando: …}]
out loja.resumo()         // {emitidos: 12, entregues: 20, ouvintes: {…}, erros: 1}
"""),

 {"h2": "Curinga e uma vez"},
 cod("""
loja.ao("*", lambda nome: registrar(nome))        // ouve tudo
loja.uma_vez("pronto", lambda: comecar())         // ouve o próximo, e sai

cancelar := loja.ao("venda", tratar)
cancelar()                                        // desinscreve
"""),
 {"callout": {"tipo": "atencao", "titulo": "Inscrever dentro de um laço é recusado",
              "texto": "Mil ouvintes no mesmo evento quase sempre significa um `ao(...)` dentro de um laço ou de um handler — cada volta inscreve mais um, e nenhum sai. O erro diz isso, em vez de deixar a memória crescer."}},

 {"h2": "O contexto atravessa as camadas"},
 {"p": "O id do pedido, quem pediu, o rastro — sem passar por parâmetro em cada camada:"},
 cod("""
action atender(req):
    yield Eventos.com_contexto({"pedido": req["id"], "quem": req["usuario"]},
        lambda => processar())

// dez camadas abaixo, sem ter recebido nada
action gravar_log(texto):
    Log.info(texto, {"pedido": Eventos.por("pedido")})
"""),
 {"callout": {"tipo": "perigo", "titulo": "É por thread, e tem de ser",
              "texto": "Um vault global serviria até o segundo pedido simultâneo — e aí o id de um apareceria no log do outro. O Kiln atende **um pedido por thread**, então o contexto é por thread."}},

 {"h2": "Fila de trabalho"},
 {"p": "A diferença para o emissor: o emissor entrega **agora**, na thread de quem emitiu. A fila aceita e devolve o controle — quem publicou não espera o trabalho terminar."},
 cod("""
envios := Eventos.fila(lambda mensagem: Email.enviar(mensagem, servidor),
    operarios := 4)

route POST "/cadastro":
    criar(body)
    envios.publicar(boas_vindas(body["email"]))    // não espera
    respond 201 json {"ok": yes}
"""),
 cod("""
envios.esperar(prazo := 5.0)     // num teste: espera esvaziar
out envios.resumo()              // {feitos: 40, falhos: 0, pendentes: 0, operarios: 4}
"""),
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/biblioteca/cli",
"title": "Arcane.Cli",
"description": "A linha de comando de um programa escrito em DataForge: opções tipadas, subcomandos, ajuda gerada e perguntas no terminal.",
"blocos": [
 {"p": "O `dataforge` tem uma CLI completa. Um programa **escrito em** DataForge não tinha nada: `OS.args()` devolve a lista crua, e ler `--porta=8080` dela é escrever o mesmo laço de novo em cada programa."},

 {"h2": "Declarar"},
 cod("""
adopt Arcane.Cli as Cli

app := Cli.comando("relatorio", sobre := "Gera o relatório do mês.",
    versao := "1.0.0")

app.opcao("mes", "inteiro", curta := "m", exigida := yes, sobre := "de 1 a 12")
app.opcao("formato", escolhas := ["csv", "json"], padrao := "csv")
app.opcao("enviar", "sim_nao", sobre := "manda por e-mail")
app.posicional("saida", exigido := no)
app.exemplo("relatorio -m 9 --formato json out.json")

opcoes := app.rodar()
out opcoes["mes"], opcoes["formato"]
"""),
 {"table": {"head": ["Tipo", "Na linha"], "rows": [
   ["`texto`", "`--nome valor`"],
   ["`inteiro` · `numero`", "convertidos, e recusados se não forem"],
   ["`sim_nao`", "`--nome` (sem valor)"],
   ["`lista`", "`--nome a,b,c`"],
 ]}},
 {"p": "As formas aceitas são as de sempre: `--porta 9000`, `--porta=9000`, `-p 9000` e `-p9000`."},

 {"h2": "A ajuda sai da declaração"},
 cod("""
Sobe a forja.

uso: forja [opções] [config]

opções:
  -p, --porta INTEIRO  a porta  (padrão: 8080)
      --modo TEXTO     o ambiente  (dev|prod; padrão: dev)
  -v, --verboso        fala mais
  -h, --ajuda          mostra esta ajuda
      --versao         mostra a versão
""", "text"),
 {"callout": {"tipo": "dica", "titulo": "Por que gerada",
              "texto": "Escrita à mão, ela envelhece no primeiro flag novo — e a **ajuda errada é pior que nenhuma**, porque quem lê confia nela."}},

 {"h2": "O erro sugere"},
 cod("""
$ relatorio --mess 9
relatorio: não conheço '--mess'.
  Você quis dizer '--mes'?

$ relatorio --mes abc
relatorio: '--mes' espera inteiro e recebeu 'abc'.

$ relatorio --formato xml
relatorio: '--formato' aceita csv, json — veio 'xml'.
""", "bash"),
 {"callout": {"tipo": "nota", "titulo": "Sai com código 2",
              "texto": "Código 1 é *\"o programa rodou e deu errado\"*; 2 é *\"você chamou errado\"*. Um script que testa `$?` precisa distinguir os dois."}},

 {"h2": "Subcomandos"},
 cod("""
app := Cli.comando("forja")
subir := app.subcomando("subir", "põe no ar")
subir.opcao("porta", "inteiro", padrao := 8080)
app.subcomando("parar", "tira do ar")

opcoes := app.rodar()
match opcoes["__comando__"]:
    point "subir":
        subir_servidor(opcoes["porta"])
    point "parar":
        parar_servidor()
"""),

 {"h2": "Perguntar"},
 cod("""
nome := Cli.perguntar("Nome do projeto", padrao := "meu-app")
banco := Cli.escolher("Banco?", ["SQLite", "Postgres", "MySQL"])
senha := Cli.segredo("Senha do banco")

given Cli.confirmar("Apagar tudo?", padrao := no):
    apagar()
"""),
 {"callout": {"tipo": "perigo", "titulo": "Elas recusam rodar sem terminal",
              "texto": "Numa pipeline de CI, uma pergunta interativa trava o build **para sempre**, sem dizer por quê. É melhor falhar na hora, dizendo qual opção passar. `Cli.tem_terminal()` responde antes."}},

 {"h2": "Console interativo"},
 cod("""
c := Cli.console("forja> ", sobre := "Console da forja.")
c.registrar("listar", lambda _ => listar_pedidos(), "mostra os pedidos")
c.registrar("ver", lambda id => ver(id), "detalha um pedido")
c.rodar()
"""),
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/biblioteca/email",
"title": "Arcane.Email",
"description": "Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza e caixa de teste.",
"blocos": [
 {"p": "Todo sistema manda e-mail: a confirmação de cadastro, a redefinição de senha, o relatório de madrugada. Não havia como, e a saída era chamar um serviço de fora por HTTP — o que funciona e cobra por mensagem."},

 {"h2": "Montar"},
 cod("""
adopt Arcane.Email as Email

m := Email.mensagem("forja@exemplo.br", "ana@exemplo.br", "Seu pedido")
m.html("<h1>Obrigado</h1><p>Pedido <b>P-1</b> confirmado.</p>")
m.copia_oculta(["auditoria@exemplo.br"])
m.anexar("notas/P-1.pdf")
"""),
 {"callout": {"tipo": "nota", "titulo": "Por que um objeto, e não texto",
              "texto": "Um e-mail com anexo e HTML é MIME multipart, e montá-lo concatenando texto é como montar HTML com `+`: funciona nos casos fáceis e quebra no primeiro acento ou no primeiro anexo binário."}},

 {"h2": "HTML ganha alternativa em texto"},
 {"p": "Sem ela, o cliente de texto puro mostra a marcação crua — e é o que boa parte dos leitores de tela recebe. Quando você não passa uma, ela é derivada do HTML:"},
 cod("""
m.html("<h1>Olá</h1><p>tudo bem</p>")
out m.prever()["texto"]                  // "Olá tudo bem"

m.html(corpo_rico, alternativa := "Seu pedido P-1 foi confirmado.")
"""),

 {"h2": "A cópia oculta não vai no cabeçalho"},
 {"p": "Um Bcc escrito no cabeçalho é **visível para todo mundo** — o oposto do que ele significa. Aqui ele entra só na lista de entrega."},

 {"h2": "Prever antes de mandar"},
 cod("""
out m.prever()
// {de: …, para: [ana@…, auditoria@…], assunto: …,
//  texto: …, html: …, anexos: [{nome: P-1.pdf, bytes: 84213}], tamanho: 85102}
"""),
 {"callout": {"tipo": "perigo", "titulo": "O erro mais caro daqui",
              "texto": "Disparar mil e-mails de teste para endereços reais. `prever` mostra o que **seria** enviado, e não envia nada."}},

 {"h2": "Enviar"},
 cod("""
r := Email.enviar(m, "smtp.exemplo.br", porta := 587,
    usuario := "forja@exemplo.br", senha := OS.env("SMTP_SENHA"))

out r["entregues"], r["recusados"], r["ok"]
"""),
 {"table": {"head": ["Porta", "O quê"], "rows": [
   ["`587`", "STARTTLS — o padrão"],
   ["`465`", "TLS direto"],
   ["`25`", "sem cifra (`seguro := no`)"],
 ]}},
 {"callout": {"tipo": "perigo", "titulo": "TLS é o padrão",
              "texto": "Uma senha de SMTP trafegando em claro numa rede que você não controla é uma credencial perdida. Quem quiser sem TLS escreve `seguro := no` — e aí a escolha está no código, para alguém ver na revisão."}},
 {"p": "Quando o login é recusado, a mensagem lembra o que costuma ser: **muitos provedores exigem uma senha de aplicativo**, e não a senha da conta."},

 {"h2": "Caixa de teste"},
 {"p": "O mesmo contrato, sem mandar nada — então o código que envia não muda entre o teste e a produção:"},
 cod("""
caixa := Email.caixa()
caixa.enviar(m)

assert len(caixa.para("ana@exemplo.br")) is 1
assert caixa.ultimo()["assunto"] is "Seu pedido"
"""),
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/biblioteca/html",
"title": "Arcane.Html",
"description": "Ler HTML de verdade: seletor CSS, tabela como dado, e as duas defesas contra XSS.",
"blocos": [
 {"p": "Ler uma página — um preço, uma tabela, os links — só dava por expressão regular, e **HTML não é regular**. A marcação que funciona no teste quebra no primeiro atributo fora de ordem, na primeira tag sem fechar, no primeiro `<br>` no meio."},

 {"h2": "Seletor CSS"},
 cod("""
adopt Arcane.Html as Html

doc := Html.ler(pagina)

out doc.achar("#p1 h2").texto
out [n.texto cycle n in doc.achar_todos("div.produto > h2")]
out doc.achar("a[href]").atributo("href")
"""),
 {"table": {"head": ["Escrita", "Casa"], "rows": [
   ["`div`", "a tag"],
   ["`.classe`", "quem tem a classe"],
   ["`#id`", "quem tem o id"],
   ["`[attr]` · `[attr=valor]`", "por atributo"],
   ["`a b`", "`b` em qualquer lugar dentro de `a`"],
   ["`a > b`", "`b` filho **direto** de `a`"],
 ]}},
 {"p": "É CSS, e não XPath: `div.preco > span` é o que quem escreve HTML já sabe de cor."},

 {"h2": "O texto junta com espaço"},
 cod("""
<span class="preco"><b>R$</b> <span>450,00</span></span>
""", "text"),
 cod("""
out doc.achar(".preco").texto        // "R$ 450,00"
"""),
 {"p": "Colado, isso viraria `R$450,00`. Com espaço é o que a página **mostra** — e é o que quem extrai quer."},

 {"h2": "Extrair"},
 cod("""
out doc.links("https://forja.br/loja/")
// [{texto: Ver, destino: https://forja.br/produto/1, titulo: }]

out doc.tabela()
// {cabecalho: [Item, Preço], linhas: [[Bigorna, 450], [Marreta, 75]]}

out doc.imagens()
"""),

 {"h2": "As duas defesas"},
 {"h3": "Escapar — antes de mostrar"},
 cod("""
respond html $"<p>{Html.escapar(comentario)}</p>"
"""),
 {"p": "É a defesa contra XSS que mais se esquece: um texto que veio de fora, escrito direto na página, é código."},

 {"h3": "Limpar — tirar toda a marcação"},
 cod("""
assert Html.limpar("<p>ok</p><script>roubar()</script>") is "ok"
"""),
 {"callout": {"tipo": "atencao", "titulo": "Ele tira o conteúdo do script também",
              "texto": "Um `limpar` que só tira as **tags** deixa o corpo do `<script>` como texto — e aí o \"texto limpo\" contém exatamente o código que se queria tirar."}},

 {"h3": "Podar — deixar alguma marcação"},
 {"p": "Para comentário e conteúdo de usuário, onde negrito e link fazem sentido:"},
 cod("""
seguro := Html.podar(comentario)
// <p>, <b>, <a>, <ul>… passam; <script>, <iframe>, <style> somem
"""),
 {"callout": {"tipo": "perigo", "titulo": "A lista é de permitidas",
              "texto": "Uma lista de **proibidas** esquece a próxima tag perigosa que o navegador inventar. E um `href` que começa com `javascript:` é script com outro nome — ele vira um `<a>` sem destino."}},

 {"h2": "HTML real não é bem formado"},
 {"p": "Tag sem fechar, tag fechada que ninguém abriu, `<br>` solto: o leitor engole tudo isso, porque a página que você quer ler está cheia disso e derrubar a leitura não serve a ninguém."},
]},
]
