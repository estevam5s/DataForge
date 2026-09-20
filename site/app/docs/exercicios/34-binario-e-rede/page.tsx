// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "34 · Binário e rede",
  description: "3 exercícios: dados binários, TCP/UDP/DNS, eventos, CLI, e-mail e HTML.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 34`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[235](#235-dados-binarios-com-arcanebytes)", "**Dados binarios com Arcane.Bytes**", "monte e leia um cabecalho de protocolo, byte a byte."], ["[236](#236-tcp-udp-e-dns-com-arcanerede)", "**TCP, UDP e DNS com Arcane.Rede**", "fale um protocolo proprio, abaixo do HTTP."], ["[237](#237-eventos-linha-de-comando-e-mail-e-html)", "**Eventos, linha de comando, e-mail e HTML**", "junte as pecas que faltavam para um programa completo."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "235 · Dados binarios com Arcane.Bytes"},
  {"p": "**Enunciado.** monte e leia um cabecalho de protocolo, byte a byte."},
  { code: `adopt Arcane.Bytes as B

// ── 1. A ordem dos bytes e OBRIGATORIA ──
//
// 'i32' sozinho nao existe aqui. Um inteiro escrito na ordem da
// maquina e lido na ordem da rede da um numero diferente, o programa
// nao falha, e o dado sai errado do outro lado.
monitor:
    _ := B.empacotar("i32", 1)
    assert no, "devia ter recusado"
handle Error as e:
    assert "ORDEM DOS BYTES" in e.message

assert B.hex(B.empacotar(">i32", 1)) is "00000001", "rede: byte mais alto primeiro"
assert B.hex(B.empacotar("<i32", 1)) is "01000000", "Intel: ao contrario"

// ── 2. Um cabecalho de protocolo ──
//
// "versao (1 byte), tipo (1), tamanho (4)" — escrito assim, e nao com
// contas de deslocamento.
cabecalho := B.empacotar(">u8 u8 u32", 1, 7, 1024)
out B.hex(cabecalho, " ")
assert B.tamanho(">u8 u8 u32") is 6
assert B.desempacotar(">u8 u8 u32", cabecalho) is [1, 7, 1024]

// ── 3. O cursor anda sozinho ──
//
// Ler com fatias exige acertar o indice de cada campo, e um erro num
// deles desalinha TUDO o que vem depois — entregando numeros
// plausiveis e errados.
mensagem := B.concatenar(cabecalho, B.de_texto("DataForge"))
leitor := B.ler(mensagem)

versao := leitor.ler("u8")
tipo := leitor.ler("u8")
tamanho := leitor.ler("u32")
corpo := leitor.resto()

out $"v{versao} tipo={tipo} tamanho={tamanho} corpo={B.para_texto(corpo)}"
assert versao is 1
assert B.para_texto(corpo) is "DataForge"
assert leitor.acabou

// Ler alem do fim diz quanto falta, em vez de estourar calado.
curto := B.ler(B.de_hex("01"))
monitor:
    _ := curto.ler("u32")
    assert no
handle Error as e:
    assert "pede 4" in e.message

// ── 4. Escrever ──
escritor := B.escrever()
_ := escritor.escrever("u8", 2)
_ := escritor.escrever("u32", 99)
_ := escritor.escrever_texto("fim", com_zero := yes)
montado := escritor.finalizar()
assert B.ler(montado).ler("u8") is 2

de_volta := B.ler(montado)
_ := de_volta.ler("u8")
assert de_volta.ler("u32") is 99
assert de_volta.ler_ate_zero() is "fim"

// ── 5. Ver o que esta errado ──
//
// O despejo e o que se olha quando o protocolo nao bate: posicao,
// hexadecimal e o texto legivel, lado a lado.
out B.despejo(mensagem)
assert "DataForge" in B.despejo(mensagem)

// ── 6. Segredo se compara em tempo fixo ──
//
// Uma comparacao comum para no primeiro byte diferente, e o TEMPO
// conta quantos bateram. Com isso, um atacante descobre um token byte
// a byte.
token := B.de_hex("deadbeef")
assert B.igual_em_tempo_fixo(token, B.de_hex("deadbeef"))
assert not B.igual_em_tempo_fixo(token, B.de_hex("deadbeff"))

// ── 7. A janela nao copia ──
//
// Copiar um arquivo de 200 MB para ler 8 bytes e o jeito mais facil de
// estourar a memoria.
grande := B.de_texto("x" * 10000)
pedaco := B.janela(grande, 100, 108)
assert len(B.copiar(pedaco)) is 8

out "235 ok"`, lang: 'df', title: `exercicios/34-binario-e-rede/235_bytes.df` },
  {"h3": "O que faltava"},
  {"p": "A linguagem tem o tipo `Bytes`, e não havia o que fazer com ele. Ler um arquivo binário, falar um protocolo, montar um cabeçalho de quatro bytes — tudo isso pedia sair da linguagem."},
  {"h3": "A ordem dos bytes é obrigatória"},
  { code: `Bytes.empacotar("i32", 1)      // recusado
Bytes.empacotar(">i32", 1)     // 00 00 00 01   ordem de rede
Bytes.empacotar("<i32", 1)     // 01 00 00 00   ordem do Intel`, lang: 'df' },
  {"p": "Um padrão silencioso aqui seria a pior decisão possível: um inteiro escrito na ordem da **máquina** e lido na ordem da rede dá um número diferente, o programa **não falha**, e o dado sai errado do outro lado."},
  {"p": "Isso não aparece em teste — a máquina que escreve e a que lê são a mesma. Ele aparece no dia em que o servidor muda de arquitetura, ou no dia em que alguém lê o arquivo em outro lugar."},
  {"h3": "Os nomes dizem o tamanho"},
  {"p": "`i32` é um inteiro de 32 bits em qualquer máquina. O `int` do C não é, e descobrir isso depois de gravar um arquivo é caro."},
  {"table": {"head": ["Escrita", "O quê", "Bytes"], "rows": [["`i8` `u8`", "inteiro de 8 bits, com e sem sinal", "1"], ["`i16` `u16`", "16 bits", "2"], ["`i32` `u32`", "32 bits", "4"], ["`i64` `u64`", "64 bits", "8"], ["`f32` `f64`", "ponto flutuante", "4 / 8"], ["`bool`", "verdadeiro ou falso", "1"], ["`bytesN`", "um bloco de tamanho fixo", "N"]]}},
  {"h3": "O cursor anda sozinho"},
  {"p": "Ler com fatias exige calcular o deslocamento de cada campo:"},
  { code: `versao := dados[0]
tipo := dados[1]
tamanho := dados[2:6]      // e aqui já é preciso lembrar que u32 são 4 bytes`, lang: 'df' },
  {"p": "Um erro num deles **desalinha tudo o que vem depois** — e o pior é que o programa não quebra: ele entrega números plausíveis e errados."},
  { code: `leitor := Bytes.ler(mensagem)
versao := leitor.ler("u8")
tipo := leitor.ler("u8")
tamanho := leitor.ler("u32")
corpo := leitor.resto()`, lang: 'df' },
  {"p": "E ler além do fim diz **quanto falta**:"},
  { code: `faltam bytes para ler 'u32': o cursor está em 1, o campo pede 4
e só há 1 até o fim.`, lang: 'text' },
  {"h3": "O despejo"},
  {"p": "É o que se olha quando o protocolo não bate — posição, hexadecimal e o texto legível, lado a lado:"},
  { code: `00000000  01 07 00 00 04 00 44 61 74 61 46 6f 72 67 65     |......DataForge|`, lang: 'text' },
  {"p": "É assim que se vê o byte a mais que desalinhou tudo."},
  {"h3": "Segredo se compara em tempo fixo"},
  { code: `Bytes.igual_em_tempo_fixo(token_recebido, token_certo)`, lang: 'df' },
  {"p": "Uma comparação comum para no **primeiro byte diferente**, e o tempo conta quantos bateram. Com isso, um atacante descobre um token byte a byte, sem nunca precisar acertá-lo inteiro por sorte."},
  {"h3": "A janela não copia"},
  {"p": "Copiar um arquivo de 200 MB para ler 8 bytes é o jeito mais fácil de estourar a memória. `Bytes.janela` aponta para os mesmos bytes; `Bytes.copiar` só é chamado quando o pedaço precisa mesmo ser guardado."},
  {"h3": "Saída esperada"},
  { code: `01 07 00 00 04 00
v1 tipo=7 tamanho=1024 corpo=DataForge
00000000  01 07 00 00 04 00 44 61 74 61 46 6f 72 67 65     |......DataForge|
235 ok`, lang: 'text' },
  {"h3": "Para experimentar"},
  {"list": ["Troque `>u32` por `<u32` e veja o `1024` virar `262144`.", "Leia um campo a mais que o bloco tem, e leia a mensagem de erro.", "Monte um cabeçalho, mande por TCP (exercício 236) e leia do outro lado."]},
  {"h2": "236 · TCP, UDP e DNS com Arcane.Rede"},
  {"p": "**Enunciado.** fale um protocolo proprio, abaixo do HTTP."},
  { code: `adopt Arcane.Rede as Rede
adopt Arcane.Bytes as B

// ── 1. Um servidor TCP que fala um protocolo proprio ──
//
// O quadro e: tamanho (4 bytes, ordem de rede) + corpo. E o formato
// mais comum que existe, e o que resolve o problema do TCP nao ter
// fronteira de mensagem — ele entrega um FLUXO de bytes, e nao
// mensagens.
action atender(conexao):
    persist yes:
        cabecalho := conexao.receber(4)
        given len(cabecalho) is 0:
            halt
        tamanho := B.desempacotar(">u32", cabecalho)[0]
        corpo := conexao.receber_exato(tamanho)
        resposta := B.de_texto(B.para_texto(corpo).upper())
        _ := conexao.enviar(B.empacotar(">u32", len(resposta)))
        _ := conexao.enviar(resposta)

servidor := Rede.servir_em_segundo_plano(atender, porta := 0)
defer:
    _ := servidor.parar()

// ── 2. O cliente ──
cliente := Rede.conectar("127.0.0.1", servidor.porta)
defer:
    _ := cliente.fechar()

action pedir(texto):
    dados := B.de_texto(texto)
    _ := cliente.enviar(B.empacotar(">u32", len(dados)))
    _ := cliente.enviar(dados)
    quanto := B.desempacotar(">u32", cliente.receber_exato(4))[0]
    yield B.para_texto(cliente.receber_exato(quanto))

out pedir("forja")
assert pedir("forja") is "FORJA"
assert pedir("bigorna e marreta") is "BIGORNA E MARRETA"

// 'receber_exato' insiste ate completar. O 'recv' devolve MENOS do que
// se pediu com frequencia num pedaco que atravessa pacotes, e tratar o
// retorno curto como a mensagem inteira corrompe a proxima — o sintoma
// e uma conexao que funciona e de repente para.
longo := "a" * 5000
assert len(pedir(longo)) is 5000, "atravessa varios pacotes"

// ── 3. UDP: manda e esquece ──
//
// Sem conexao, sem ordem, sem garantia. E o certo para metrica,
// descoberta e log — onde perder um pacote custa menos que a espera de
// confirmar cada um.
coletor := Rede.udp(porta := 0, escutar := yes)
defer:
    _ := coletor.fechar()

agente := Rede.udp()
defer:
    _ := agente.fechar()

_ := agente.enviar("pedidos=42", "127.0.0.1", coletor.porta)
chegou := coletor.receber(prazo := 3.0)
out $"de {chegou['host']}: {B.para_texto(chegou['dados'])}"
assert B.para_texto(chegou["dados"]) is "pedidos=42"

// ── 4. DNS ──
locais := Rede.resolver("localhost")
assert len(locais) bigger 0
achou := [e cycle e in locais given e["ip"] in ["127.0.0.1", "::1"]]
assert len(achou) bigger 0

// ── 5. Portas ──
livre := Rede.porta_livre()
assert not Rede.porta_aberta("127.0.0.1", livre, 0.2), "ninguem escuta ali"
assert Rede.porta_aberta("127.0.0.1", servidor.porta), "o nosso, sim"

// ARMADILHA: 'porta_aberta' ABRE uma conexao de verdade — nao ha como
// perguntar sem bater na porta. Um servidor que conta conexoes vai ver
// esta tambem.

// 'esperar_porta' substitui o "dorme dois segundos e torce" de todo
// script de integracao.
gasto := Rede.esperar_porta("127.0.0.1", servidor.porta, prazo := 5.0)
assert gasto smaller 1.0

// ── 6. Erro de conexao diz o que significa ──
//
// E sao DUAS coisas diferentes, conforme quem esta do outro lado:
//
//   RECUSADA     alguem respondeu "nao ha ninguem nesta porta". E uma
//                RESPOSTA, e das uteis: o host esta de pe.
//   prazo acabou nao veio resposta nenhuma. Pode ser firewall, rede
//                caida, ou uma maquina que nao existe.
//
// No Unix uma porta fechada responde RST, e o erro e a recusa. No
// Windows o firewall DESCARTA o pacote em vez de recusa-lo, e o que se
// tem e a espera — a segunda mensagem e a verdade ali, e exigir a
// primeira seria exigir que a linguagem mentisse sobre o que aconteceu.
monitor:
    _ := Rede.conectar("127.0.0.1", livre, prazo := 2.0)
    assert no
handle Error as e:
    // A PORTA nao entra na saida: ela e sorteada, e um exercicio cuja
    // saida muda a cada execucao nao pode ser comparado — e a suite
    // compara, para provar que a compilacao nao muda o resultado.
    respondeu := "RECUSADA" in e.message
    calou := "prazo" in e.message
    assert respondeu or calou, "a mensagem tem de separar recusa de espera"
    out "conexao em porta vazia: RECUSADA, ou espera onde o firewall cala"

out "236 ok"`, lang: 'df', title: `exercicios/34-binario-e-rede/236_rede.df` },
  {"h3": "O que faltava"},
  {"p": "O Kiln fala HTTP e a Malha fala com outro serviço. **Abaixo disso não havia nada**: um protocolo próprio, um agente que manda uma linha por UDP, ou descobrir para onde um nome aponta pediam sair da linguagem."},
  {"h3": "O TCP não tem fronteira de mensagem"},
  {"p": "Esta é a ideia central do exercício. O TCP entrega um **fluxo de bytes**, e não mensagens: o que você mandou em três `enviar` pode chegar num `receber` só, ou ao contrário."},
  {"p": "O formato mais comum para resolver isso é **tamanho + corpo**:"},
  { code: `action mandar(conexao, texto):
    dados := Bytes.de_texto(texto)
    conexao.enviar(Bytes.empacotar(">u32", len(dados)))
    conexao.enviar(dados)

action receber(conexao):
    quanto := Bytes.desempacotar(">u32", conexao.receber_exato(4))[0]
    yield Bytes.para_texto(conexao.receber_exato(quanto))`, lang: 'df' },
  {"h3": "`receber_exato`, e não `receber`"},
  {"p": "O `recv` devolve **menos** do que se pediu com frequência num pedaço que atravessa pacotes. Tratar o retorno curto como a mensagem inteira corrompe a próxima — e o sintoma é uma conexão que funciona e de repente para."},
  {"p": "No exercício, o teste com 5 000 caracteres existe justamente para atravessar mais de um pacote."},
  {"h3": "O prazo e o limite têm padrão"},
  {"table": {"head": ["Sem", "O que acontece"], "rows": [["prazo", "o outro lado caiu sem fechar o socket, e o `recv` espera um byte que nunca vem"], ["limite na linha", "um cliente que nunca manda `\\n` enche a memória do servidor — um ataque de uma linha"]]}},
  {"h3": "UDP: manda e esquece"},
  {"p": "Sem conexão, sem ordem, sem garantia. Parece pior, e é o **certo** para métrica, descoberta e log: perder um pacote custa menos que a espera de confirmar cada um."},
  { code: `coletor := Rede.udp(porta := 8125, escutar := yes)
chegou := coletor.receber()
out chegou["host"], chegou["dados"]`, lang: 'df' },
  {"p": "Repare que `receber` diz **de quem veio** — sem conexão, essa é a única forma de saber."},
  {"h3": "Portas"},
  {"p": "`esperar_porta` substitui o *\"sobe o serviço e dorme dois segundos torcendo para dar tempo\"* de todo script de integração. Quando ela desiste, diz o que costuma ser:"},
  { code: `api:8080 não abriu em 30s.
  O serviço não subiu, subiu em outra porta, ou subiu em
  127.0.0.1 quando deveria ser 0.0.0.0.`, lang: 'text' },
  {"p": "**Armadilha:** `porta_aberta` abre uma conexão de verdade — não há como perguntar sem bater na porta. Um servidor que conta conexões vai ver esta também."},
  {"h3": "O erro diz o que significa"},
  { code: `conectar (127.0.0.1:63859): a conexao foi RECUSADA.
  Ha alguem escutando nessa porta? Recusa e resposta: o
  host esta de pe e nada atende ali.`, lang: 'text' },
  {"p": "Recusa e prazo esgotado são coisas **diferentes**: a primeira significa que o host respondeu; a segunda, que ninguém respondeu. Confundi-las manda a pessoa procurar no lugar errado."},
  {"p": "**E qual das duas aparece depende do sistema.** No Unix, uma porta fechada responde `RST` e o erro é a recusa. No **Windows**, o firewall *descarta* o pacote em vez de recusá-lo, e o que se tem é a espera — ali a segunda mensagem é a verdade, e exigir a primeira seria exigir que a linguagem mentisse sobre o que aconteceu. Por isso o exercício aceita as duas: o que ele cobra é que a mensagem **separe** os dois casos."},
  {"h3": "Saída esperada"},
  { code: `FORJA
de 127.0.0.1: pedidos=42
conexao em porta vazia: RECUSADA, ou espera onde o firewall cala
236 ok`, lang: 'text' },
  {"h3": "Para experimentar"},
  {"list": ["Troque `receber_exato` por `receber` e mande os 5 000 caracteres. Veja a"]},
  {"p": "mensagem chegar pela metade."},
  {"list": ["Suba o servidor em `127.0.0.1` e tente conectar do IP da máquina.", "Mande um datagrama para uma porta onde ninguém escuta. UDP não reclama."]},
  {"h2": "237 · Eventos, linha de comando, e-mail e HTML"},
  {"p": "**Enunciado.** junte as pecas que faltavam para um programa completo."},
  { code: `adopt Arcane.Eventos as Ev
adopt Arcane.Cli as Cli
adopt Arcane.Email as Mail
adopt Arcane.Html as Html

// ── 1. Eventos: duas partes que nao se conhecem ──
loja := Ev.emissor("loja")
notas := []
avisos := []

_ := loja.ao("venda", lambda pedido: notas.append(pedido))
_ := loja.ao("venda", lambda pedido: avisos.append($"aviso de {pedido}"))

// 'emitir' devolve QUANTOS ouviram. Zero e informacao: o evento com o
// nome errado nao falha, ele simplesmente nao chega — e essa e a falha
// mais dificil de achar num sistema de eventos.
assert loja.emitir("venda", "P-1") is 2
assert loja.emitir("vendaa", "P-2") is 0, "nome errado: ninguem ouviu"
assert notas is ["P-1"]

// Um ouvinte que quebra SAI da lista. Um quebrado que continua inscrito
// quebra a cada evento, para sempre, e some no meio do log.
frageis := Ev.emissor()
bons := []
_ := frageis.ao("x", lambda v: 1 ~/ 0)
_ := frageis.ao("x", lambda v: bons.append(v))
assert frageis.emitir("x", 1) is 1, "o bom recebeu mesmo assim"
assert frageis.ouvintes("x") is 1, "o quebrado saiu"
assert len(frageis.erros) is 1

// O curinga ouve tudo — para log e auditoria.
tudo := []
_ := loja.ao("*", lambda nome: tudo.append(nome))
_ := loja.emitir("estorno", "P-1")
assert tudo is ["estorno"]

// ── 2. O contexto atravessa as camadas ──
//
// Sem passar por parametro em cada uma. E por THREAD: um vault global
// serviria ate o segundo pedido simultaneo.
action camada_funda():
    yield Ev.por("pedido", "(sem)")

assert Ev.com_contexto({"pedido": "P-9"}, camada_funda) is "P-9"
assert camada_funda() is "(sem)", "fora do contexto, nao ha nada"

// ── 3. A linha de comando ──
programa := Cli.comando("relatorio", sobre := "Gera o relatorio do mes.",
    versao := "1.0.0")
_ := programa.opcao("mes", "inteiro", curta := "m", exigida := yes,
    sobre := "o mes, de 1 a 12")
_ := programa.opcao("formato", escolhas := ["csv", "json"], padrao := "csv")
_ := programa.opcao("enviar", "sim_nao", sobre := "manda por e-mail")
_ := programa.posicional("saida", exigido := no)

lido := programa.ler(["-m", "9", "--formato", "json", "--enviar", "out.json"])
out lido["mes"], lido["formato"], lido["enviar"], lido["saida"]
assert lido["mes"] is 9
assert lido["formato"] is "json"
assert lido["enviar"]
assert lido["saida"] is "out.json"

// A ajuda e GERADA da declaracao. Escrita a mao, ela envelhece no
// primeiro flag novo — e a ajuda errada e pior que nenhuma.
ajuda := programa.ajuda()
assert "-m, --mes" in ajuda
assert "csv|json" in ajuda
assert "exigida" in ajuda

// O erro sugere o que existe, e sai com codigo 2: 1 e "rodou e deu
// errado", 2 e "voce chamou errado".
monitor:
    _ := programa.ler(["--mess", "9"])
    assert no
handle Error as e:
    assert "--mes" in e.message

// ── 4. E-mail ──
relatorio := Mail.mensagem("forja@exemplo.br", "chefe@exemplo.br",
    "Relatorio de setembro")
_ := relatorio.html("<h1>Setembro</h1><p>Total: <b>R$ 12.400</b></p>")
_ := relatorio.copia_oculta(["auditoria@exemplo.br"])
_ := relatorio.anexar_dados("relatorio.csv", "mes,total\\n9,12400", "text/csv")

previa := relatorio.prever()
out previa["assunto"], "->", previa["para"]
assert len(previa["para"]) is 2, "o oculto recebe"
assert previa["texto"] is "Setembro Total: R$ 12.400", "alternativa em texto"

// O Bcc NAO vira cabecalho — ele iria visivel para todo mundo, que e o
// oposto do que significa.
cabecalho := relatorio.como_texto().split("\\n\\n")[0]
assert "auditoria" not in cabecalho

// A caixa de teste tem o MESMO contrato do envio real.
caixa := Mail.caixa()
_ := caixa.enviar(relatorio)
assert len(caixa.para("chefe@exemplo.br")) is 1

// ── 5. HTML ──
pagina := """
<div class="produto" id="p1">
  <h2>Bigorna</h2>
  <span class="preco"><b>R$</b> <span>450,00</span></span>
  <a href="/produto/1">Ver</a>
</div>
<table><tr><th>Item</th><th>Total</th></tr>
       <tr><td>Bigorna</td><td>450</td></tr></table>
"""
doc := Html.ler(pagina)

assert doc.achar("#p1 h2").texto is "Bigorna"
// O texto junta com ESPACO: '<b>R$</b><span>10</span>' colado viraria
// 'R$10'; com espaco, 'R$ 10' — que e o que a pagina mostra.
assert doc.achar(".preco").texto is "R$ 450,00"

links := doc.links("https://forja.br/loja/")
assert links[0]["destino"] is "https://forja.br/produto/1"

tabela := doc.tabela()
assert tabela["cabecalho"] is ["Item", "Total"]
assert tabela["linhas"] is [["Bigorna", "450"]]

// 'limpar' tira o conteudo do script tambem. Um 'limpar' que so tira
// as tags deixa o corpo do <script> como TEXTO — e ai o "texto limpo"
// contem o codigo que se queria tirar.
assert Html.limpar("<p>ok</p><script>roubar()</script>") is "ok"

// 'podar' usa lista de PERMITIDAS. Uma lista de proibidas esquece a
// proxima tag perigosa que o navegador inventar.
podado := Html.podar("<p>oi</p><iframe src='x'></iframe><b>b</b>")
assert "iframe" not in podado
assert "<b>b</b>" in podado

out "237 ok"`, lang: 'df', title: `exercicios/34-binario-e-rede/237_eventos_cli_html.df` },
  {"h3": "Eventos: duas partes que não se conhecem"},
  { code: `loja.ao("venda", lambda pedido: gravar_nota(pedido))
loja.ao("venda", lambda pedido: avisar_estoque(pedido))

quantos := loja.emitir("venda", pedido)`, lang: 'df' },
  {"p": "**`emitir` devolve quantos ouviram**, e zero é informação: o evento com o nome errado não falha, ele simplesmente não chega — e essa é a falha mais difícil de achar num sistema de eventos."},
  {"p": "**O ouvinte que quebra sai**"},
  {"p": "Um ouvinte quebrado que continua inscrito quebra **a cada evento**, para sempre, e some no meio do log. Ele é removido e o erro vai para `emissor.erros`."},
  {"p": "**Inscrever num laço é recusado**"},
  {"p": "Mil ouvintes no mesmo evento quase sempre significa um `ao(...)` dentro de um laço ou de um handler — cada volta inscreve mais um, e nenhum sai."},
  {"h3": "O contexto atravessa as camadas"},
  { code: `Eventos.com_contexto({"pedido": "P-9"}, lambda => processar())

// dez camadas abaixo, sem ter recebido nada
Eventos.por("pedido")      // "P-9"`, lang: 'df' },
  {"p": "É **por thread**. Um vault global serviria até o segundo pedido simultâneo — e aí o id de um apareceria no log do outro. O Kiln atende um pedido por thread."},
  {"h3": "A linha de comando"},
  {"p": "A ajuda é **gerada da declaração**. Escrita à mão, ela envelhece no primeiro flag novo — e a ajuda errada é pior que nenhuma, porque quem lê confia nela."},
  {"p": "O erro sugere o que existe e sai com **código 2**: 1 é \"o programa rodou e deu errado\", 2 é \"você chamou errado\". Um script que testa `$?` precisa distinguir os dois."},
  { code: `relatorio: não conheço '--mess'.
  Você quis dizer '--mes'?`, lang: 'text' },
  {"h3": "E-mail"},
  {"p": "Três coisas que o exercício prova:"},
  {"p": "1. **O HTML ganha alternativa em texto.** Sem ela, o cliente de texto puro mostra a marcação crua — e é o que boa parte dos leitores de tela recebe. 2. **A cópia oculta não vira cabeçalho.** Um Bcc escrito no cabeçalho é visível para todo mundo, o oposto do que ele significa. 3. **`prever` mostra sem mandar.** O erro mais caro daqui é disparar mil e-mails de teste para endereços reais."},
  {"p": "A caixa de teste tem o **mesmo contrato** do envio real, então o código que envia não muda entre o teste e a produção."},
  {"h3": "HTML"},
  {"p": "O seletor é **CSS**, e não XPath: `div.preco > span` é o que quem escreve HTML já sabe de cor."},
  {"p": "O texto junta com **espaço**:"},
  { code: `<span class="preco"><b>R$</b> <span>450,00</span></span>`, lang: 'text' },
  {"p": "Colado, isso viraria `R$450,00`. Com espaço é o que a página mostra — e é o que quem extrai quer."},
  {"p": "**As duas defesas**"},
  {"table": {"head": ["Chamada", "Para quê"], "rows": [["`escapar`", "antes de mostrar um texto que veio de fora"], ["`limpar`", "tirar **toda** a marcação, e o conteúdo de `<script>` junto"], ["`podar`", "deixar alguma marcação, pela lista de **permitidas**"]]}},
  {"p": "Um `limpar` que só tira as tags deixa o corpo do `<script>` como texto — e aí o \"texto limpo\" contém exatamente o código que se queria tirar."},
  {"p": "E a lista de `podar` é de **permitidas** porque uma lista de proibidas esquece a próxima tag perigosa que o navegador inventar."},
  {"h3": "Saída esperada"},
  { code: `9 json yes out.json
Relatorio de setembro -> [chefe@exemplo.br, auditoria@exemplo.br]
237 ok`, lang: 'text' },
  {"h3": "Para experimentar"},
  {"list": ["Emita um evento com o nome errado e repare no zero.", "Inscreva num laço de mil voltas e leia a mensagem.", "Poda um comentário com `<img src=x onerror=alert(1)>`."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/34-binario-e-rede/235_bytes.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '235-dados-binarios-com-arcanebytes', text: "235 · Dados binarios com Arcane.Bytes", level: 2 as const }, { id: 'o-que-faltava', text: "O que faltava", level: 3 as const }, { id: 'a-ordem-dos-bytes-e-obrigatoria', text: "A ordem dos bytes é obrigatória", level: 3 as const }, { id: 'os-nomes-dizem-o-tamanho', text: "Os nomes dizem o tamanho", level: 3 as const }, { id: 'o-cursor-anda-sozinho', text: "O cursor anda sozinho", level: 3 as const }, { id: 'o-despejo', text: "O despejo", level: 3 as const }, { id: 'segredo-se-compara-em-tempo-fixo', text: "Segredo se compara em tempo fixo", level: 3 as const }, { id: 'a-janela-nao-copia', text: "A janela não copia", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'para-experimentar', text: "Para experimentar", level: 3 as const }, { id: '236-tcp-udp-e-dns-com-arcanerede', text: "236 · TCP, UDP e DNS com Arcane.Rede", level: 2 as const }, { id: 'o-que-faltava', text: "O que faltava", level: 3 as const }, { id: 'o-tcp-nao-tem-fronteira-de-mensagem', text: "O TCP não tem fronteira de mensagem", level: 3 as const }, { id: 'receberexato-e-nao-receber', text: "`receber_exato`, e não `receber`", level: 3 as const }, { id: 'o-prazo-e-o-limite-tem-padrao', text: "O prazo e o limite têm padrão", level: 3 as const }, { id: 'udp-manda-e-esquece', text: "UDP: manda e esquece", level: 3 as const }, { id: 'portas', text: "Portas", level: 3 as const }, { id: 'o-erro-diz-o-que-significa', text: "O erro diz o que significa", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'para-experimentar', text: "Para experimentar", level: 3 as const }, { id: '237-eventos-linha-de-comando-e-mail-e-html', text: "237 · Eventos, linha de comando, e-mail e HTML", level: 2 as const }, { id: 'eventos-duas-partes-que-nao-se-conhecem', text: "Eventos: duas partes que não se conhecem", level: 3 as const }, { id: 'o-contexto-atravessa-as-camadas', text: "O contexto atravessa as camadas", level: 3 as const }, { id: 'a-linha-de-comando', text: "A linha de comando", level: 3 as const }, { id: 'e-mail', text: "E-mail", level: 3 as const }, { id: 'html', text: "HTML", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'para-experimentar', text: "Para experimentar", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"34 · Binário e rede"}
      description={"3 exercícios: dados binários, TCP/UDP/DNS, eventos, CLI, e-mail e HTML."}
      href={"/docs/exercicios/34-binario-e-rede"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
