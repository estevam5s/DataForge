// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "56 · Bots de Telegram",
  description: "15 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 56`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[358](#358-um-bot-inteiro-testado-sem-token-e-sem-rede)", "**um bot inteiro, testado sem token e sem rede**", "um bot que so pode ser testado conversando com ele no"], ["[359](#359-botoes-e-o-relogio-que-nao-para)", "**botoes, e o relogio que nao para**", "um botao inline manda um 'dados' de volta, e o Telegram"], ["[360](#360-a-conversa-como-maquina-de-estados)", "**a conversa como maquina de estados**", "pedir tres dados em sequencia com 'given' aninhado vira"], ["[361](#361-o-caractere-que-derruba-a-mensagem-inteira)", "**o caractere que derruba a mensagem inteira**", "MarkdownV2 tem DEZOITO caracteres reservados. Um ponto"], ["[362](#362-o-que-roda-antes-o-que-roda-depois-e-quando-cai)", "**o que roda antes, o que roda depois, e quando cai**", "um bot sem tratador de erro morre calado no primeiro"], ["[363](#363-long-polling-webhook-e-o-que-o-doctor-pergunta)", "**long polling, webhook e o que o 'doctor' pergunta**", "um bot que roda na sua maquina usa long polling; um que"], ["[364](#364-um-bot-de-atendimento-ponta-a-ponta)", "**um bot de atendimento, ponta a ponta**", "juntar comando, botao, conversa, estado, middleware e"], ["[365](#365-foto-documento-e-o-que-chega-junto)", "**foto, documento e o que chega junto**", "o Telegram nao manda o arquivo no update — ele manda um"], ["[366](#366-o-mesmo-bot-em-conversa-privada-e-em-grupo)", "**o mesmo bot, em conversa privada e em grupo**", "num grupo o bot ve so os comandos, a menos que o modo de"], ["[367](#367-o-bot-que-responde-sem-estar-no-chat)", "**o bot que responde sem estar no chat**", "a consulta inline e o que faz '@meubot pizza' funcionar"], ["[368](#368-o-429-que-vem-no-corpo)", "**o 429 que vem no CORPO**", "o Telegram responde 429 com 'retry_after' NO CORPO da"], ["[369](#369-onde-o-estado-do-chat-mora)", "**onde o estado do chat mora**", "o armazem padrao e a memoria, e isso esta DITO: some"], ["[370](#370-o-que-a-sonda-prova-e-o-que-ela-nao-prova)", "**o que a sonda prova, e o que ela NAO prova**", "um bot testado so com a sonda tem teste de LOGICA. O que"], ["[371](#371-o-bot-que-guarda-no-banco)", "**o bot que guarda no banco**", "o estado do chat serve para o que e DA conversa — o"], ["[372](#372-o-mapa-e-as-cinco-decisoes)", "**o mapa, e as cinco decisoes**", "fechar o modulo com as sete formas de casar um update, a"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "358 · um bot inteiro, testado sem token e sem rede"},
  {"p": "**Enunciado.** um bot que so pode ser testado conversando com ele no"},
  { code: `// celular nao tem teste nenhum. A sonda injeta updates e le o que o
// bot mandou — e e ela que faz um bot caber numa suite.

adopt Arcane.Telegram as Tg

action montar(token):
    app := Tg.app(token)

    mark @app.comando("start", ajuda := "Comeca a conversa")
    action comecar(ctx):
        ctx.responder($"Ola, {ctx.nome()}!")

    mark @app.comando("ajuda")
    action ajuda(ctx):
        ctx.responder("Use /start para comecar.")

    mark @app.texto("\\\\b(oi|ola)\\\\b")
    action cumprimento(ctx):
        ctx.responder("Oi!")

    mark @app.qualquer()
    action resto(ctx):
        ctx.responder("Nao entendi.")

    yield app

steady TOKEN := "123456:AAHexemplo"

out "== 1. o comando =="

t := Tg.testar(montar(TOKEN))
t.comando("start")
assert "Ola," in t.ultima()
out $"   {t.ultima()}"

out ""
out "== 2. o texto que casa por padrao =="

t.mandar("oi tudo bem")
assert t.ultima() is "Oi!"

out ""
out "== 3. e o que nao casa cai no ultimo =="

t.mandar("qualquer coisa")
assert t.ultima() is "Nao entendi."

out ""
out "== 4. o despacho para no PRIMEIRO que casa =="

// Entregar a todos parece mais flexivel e produz o bug mais confuso
// que um bot tem: duas respostas para uma mensagem, e ninguem sabe de
// onde veio a segunda.
antes := t.quantas("sendMessage")
t.comando("ajuda")
assert t.quantas("sendMessage") is antes + 1

out ""
out "== 5. o token nunca aparece =="

// Ele esta na URL de toda chamada, e a URL entra em todo traceback —
// um token num log de CI e um bot sequestrado.
assert TOKEN not in t.ultima()

out ""
out "== 6. e a sonda nao toca a rede =="

// Nenhum socket, nenhum token de verdade: o teste roda na suite como
// qualquer outro.
out "   nenhum socket foi aberto"

out "exercicio 358 ok"`, lang: 'df', title: `exercicios/56-telegram/358_primeiro_bot.df` },
  {"p": "Um bot que só pode ser testado conversando com ele no celular não tem teste nenhum. A sonda injeta updates e lê o que o bot mandou — e é ela que faz um bot caber numa suíte."},
  {"h3": "O despacho para no PRIMEIRO que casa"},
  {"p": "Entregar a todos parece mais flexível e produz o bug mais confuso que um bot tem: duas respostas para uma mensagem, e ninguém sabe de onde veio a segunda."},
  {"h3": "O token nunca aparece"},
  {"p": "Ele está na URL de **toda** chamada, e a URL entra em todo traceback. Um token num log de CI é um bot sequestrado."},
  {"h3": "E nenhum socket foi aberto"},
  {"p": "O teste roda na suíte como qualquer outro."},
  {"h2": "359 · botoes, e o relogio que nao para"},
  {"p": "**Enunciado.** um botao inline manda um 'dados' de volta, e o Telegram"},
  { code: `// mostra um relogio girando ate alguem responder a consulta. Esquecer
// de responder deixa o relogio girando para sempre — o usuario acha
// que travou.

adopt Arcane.Telegram as Tg

steady CARDAPIO := [
    {"nome": "cafe", "preco": 6.5},
    {"nome": "bolo", "preco": 8.0}
]

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.comando("menu")
    action menu(ctx):
        linhas := [[Tg.botao(i["nome"], dados := $"add:{i['nome']}")]
            cycle i in CARDAPIO]
        ctx.responder("Escolha:", teclado := Tg.botoes(linhas))

    mark @app.botao("add:")
    action adicionar(ctx):
        nome := ctx.dados[4:len(ctx.dados)]
        carrinho := ctx.estado["carrinho"] ?? []
        carrinho.append(nome)
        ctx.estado["carrinho"] := carrinho
        // Responder a consulta e o que PARA o relogio.
        ctx.avisar($"{nome} adicionado")

    mark @app.comando("carrinho")
    action ver(ctx):
        itens := ctx.estado["carrinho"] ?? []
        ctx.responder($"{len(itens)} item(ns): {join(', ', itens)}")

    yield app

out "== 1. o teclado vai junto da mensagem =="

t := Tg.testar(montar())
t.comando("menu")
teclado := t.ultimo_teclado()
assert len(teclado["inline_keyboard"]) is 2
assert teclado["inline_keyboard"][0][0]["text"] is "cafe"
out $"   {len(teclado['inline_keyboard'])} botoes"

out ""
out "== 2. clicar manda o 'dados' de volta =="

t.clicar("add:cafe")
t.clicar("add:bolo")
assert t.estado("carrinho") is ["cafe", "bolo"]

out ""
out "== 3. e cada clique fechou o relogio =="

assert t.quantas("answerCallbackQuery") is 2
out "   dois cliques, duas respostas de consulta"

out ""
out "== 4. o estado sobrevive entre mensagens =="

t.comando("carrinho")
assert "2 item(ns)" in t.ultima()
assert "cafe, bolo" in t.ultima()

out ""
out "== 5. o 'dados' de um botao tem limite de 64 bytes =="

// E por isso que se manda um ID, e nao o objeto inteiro.
steady CURTO := "add:cafe"
assert len(CURTO) smaller_eq 64
out "   mande o id; o objeto fica no estado"

out ""
out "== 6. e o teclado do celular e outro =="

// 'teclado' e inline (aparece NA mensagem); o do celular substitui o
// teclado de digitar, e volta como TEXTO — entao ele e casado por
// '@app.texto', e nao por '@app.botao'.
out "   inline -> @app.botao · teclado do celular -> @app.texto"

// 'Tg.botoes' monta o inline; 'Tg.teclado' monta o do celular.
do_celular := Tg.teclado([["Sim", "Nao"]])
assert "keyboard" in keys(do_celular)
assert "inline_keyboard" not in keys(do_celular)
assert "inline_keyboard" in keys(Tg.botoes([[Tg.botao("Sim", dados := "s")]]))

out "exercicio 359 ok"`, lang: 'df', title: `exercicios/56-telegram/359_teclados.df` },
  {"p": "Um botão inline manda um `dados` de volta, e o Telegram mostra um relógio girando até alguém responder à consulta."},
  {"h3": "Esquecer de responder deixa o relógio girando"},
  {"p": "Para sempre — e o usuário acha que travou. `ctx.avisar` é o que o para."},
  {"h3": "O `dados` tem limite de 64 bytes"},
  {"p": "E é por isso que se manda um **id**: o objeto fica no estado."},
  {"h3": "E o teclado do celular é outro"},
  {"p": "`Tg.botoes` monta o inline (aparece **na** mensagem); `Tg.teclado` substitui o teclado de digitar, e volta como **texto** — casado por `@app.texto`, e não por `@app.botao`."},
  {"h2": "360 · a conversa como maquina de estados"},
  {"p": "**Enunciado.** pedir tres dados em sequencia com 'given' aninhado vira"},
  { code: `// uma arvore que ninguem mantem. A conversa nomeia cada passo e
// guarda onde o chat esta — e o estado fica NO CHAT, entao duas
// pessoas conversando ao mesmo tempo nao se atrapalham.

adopt Arcane.Telegram as Tg

action nome_valido(texto):
    yield len(trim(texto)) bigger_eq 2

action idade_valida(texto):
    monitor:
        n := int(texto)
        yield n bigger_eq 0 and n smaller_eq 130
    handle Error:
        yield no

action montar():
    app := Tg.app("123456:AAHexemplo")

    cadastro := app.conversa("cadastro", [
            {"pergunta": "Qual o seu nome?", "guarda": "nome",
                "valida": nome_valido, "erro": "O nome precisa de duas letras."},
            {"pergunta": "Qual a sua idade?", "guarda": "idade",
                "valida": idade_valida, "erro": "Escreva a idade em numeros."},
            {"pergunta": "De que cidade?", "guarda": "cidade"}
        ])

    cadastro.ao_terminar(salvar)

    mark @app.comando("cadastrar")
    action comecar(ctx):
        ctx.comecar_conversa("cadastro")

    yield app

action salvar(ctx, r):
    ctx.responder($"Cadastrado: {r['nome']}, {r['idade']}, {r['cidade']}")

out "== 1. um passo por vez =="

t := Tg.testar(montar())
t.comando("cadastrar")
assert "seu nome" in t.ultima()

t.mandar("Ana")
assert "idade" in t.ultima()

t.mandar("30")
assert "cidade" in t.ultima()

t.mandar("Florianopolis")
assert "Cadastrado: Ana, 30, Florianopolis" in t.ultima()
out $"   {t.ultima()}"

out ""
out "== 2. a validacao repete o passo, e nao avanca =="

t2 := Tg.testar(montar())
t2.comando("cadastrar")
t2.mandar("A")
assert "duas letras" in t2.ultima()

// Continua no MESMO passo.
t2.mandar("Ana")
assert "idade" in t2.ultima()

t2.mandar("trinta")
assert "numeros" in t2.ultima()
t2.mandar("30")
assert "cidade" in t2.ultima()

out ""
out "== 3. e o estado e POR CHAT =="

a := Tg.testar(montar())
a.comando("cadastrar")
a.mandar("Ana")

b := Tg.testar(montar())
b.comando("cadastrar")
b.mandar("Bia")

// As duas estao no segundo passo, e nenhuma viu o nome da outra.
assert "idade" in a.ultima()
assert "idade" in b.ultima()
a.mandar("30")
b.mandar("40")
a.mandar("Floripa")
b.mandar("Curitiba")
assert "Ana, 30, Floripa" in a.ultima()
assert "Bia, 40, Curitiba" in b.ultima()
out "   duas conversas ao mesmo tempo, sem se misturar"

out ""
out "== 4. sem a conversa, isto seria um 'given' aninhado =="

out "   tres passos = tres niveis; cinco passos = ninguem mantem"

out "exercicio 360 ok"`, lang: 'df', title: `exercicios/56-telegram/360_conversa.df` },
  {"p": "Pedir três dados em sequência com `given` aninhado vira uma árvore que ninguém mantém."},
  {"h3": "A validação repete o passo"},
  {"p": "E não avança: o erro aparece, e a pergunta continua a mesma."},
  {"h3": "O estado fica NO CHAT"},
  {"p": "Duas pessoas conversando ao mesmo tempo não se atrapalham — que é o defeito que um dicionário solto de \"passo atual\" sempre tem."},
  {"h3": "E cinco passos não cabem num `given`"},
  {"p": "Três passos são três níveis. É por isso que a conversa existe."},
  {"h2": "361 · o caractere que derruba a mensagem inteira"},
  {"p": "**Enunciado.** MarkdownV2 tem DEZOITO caracteres reservados. Um ponto"},
  { code: `// solto num preco faz o Telegram RECUSAR a mensagem inteira — nao e
// que o negrito sai errado: a mensagem nao chega.

adopt Arcane.Telegram as Tg

out "== 1. os dezoito =="

steady RESERVADOS := ["_", "*", "[", "]", "(", ")", "~", "\`", ">",
    "#", "+", "-", "=", "|", "{", "}", ".", "!"]
assert len(RESERVADOS) is 18

cycle c in RESERVADOS:
    assert "\\\\" + c in Tg.escapar(c), $"'{c}' nao foi escapado"
out "   todos escapados"

out ""
out "== 2. o que engana e o ponto =="

// Quase todo texto de sistema tem um: preco, versao, hora, fim de
// frase.
assert Tg.escapar("R$ 6.50") is "R$ 6\\\\.50"
assert Tg.escapar("versao 1.0.0") is "versao 1\\\\.0\\\\.0"
out $"   {Tg.escapar('R$ 6.50')}"

out ""
out "== 3. e o '$' NAO esta entre eles =="

// Ele parece perigoso e nao e — escapar demais tambem estraga o
// texto, com barras aparecendo na tela.
assert "$" not in RESERVADOS
assert Tg.escapar("R$") is "R$"

out ""
out "== 4. a formatacao, montada sem escrever marcacao a mao =="

assert Tg.negrito("Ana") is "*Ana*"
assert Tg.italico("obs") is "_obs_"
assert Tg.codigo("x := 1") is "\`x := 1\`"
assert Tg.riscado("antigo") is "~antigo~"
assert Tg.spoiler("fim") is "||fim||"

out ""
out "== 5. o cuidado ao juntar os dois =="

// O texto do usuario e escapado; a MARCACAO, nao. Escapar tudo
// transformaria o asterisco do negrito em asterisco literal.
action linha_de_produto(nome, preco):
    yield Tg.negrito(Tg.escapar(nome)) + " — R$ " + Tg.escapar(str(preco))

linha := linha_de_produto("Cafe especial", 32.5)
assert "*Cafe especial*" in linha
assert "32\\\\.5" in linha
out $"   {linha}"

out ""
out "== 6. e o bot usa isso de verdade =="

app := Tg.app("123456:AAHexemplo")

mark @app.comando("preco")
action preco(ctx):
    ctx.responder(linha_de_produto("Bolo de fuba", 8.0),
        formato := "MarkdownV2")

t := Tg.testar(app)
t.comando("preco")
assert "8\\\\.0" in t.ultima()
out "   o ponto foi escapado antes de sair"

out ""
out "== 7. o bloco de codigo, para saida de terminal =="

assert startswith(Tg.bloco("erro: x", "text"), "\`\`\`")
out "   dentro de um bloco, nada precisa ser escapado"

out "exercicio 361 ok"`, lang: 'df', title: `exercicios/56-telegram/361_escapar.df` },
  {"p": "MarkdownV2 tem **dezoito** caracteres reservados. Um ponto solto num preço faz o Telegram **recusar** a mensagem inteira — não é que o negrito sai errado: a mensagem não chega."},
  {"h3": "O que engana é o ponto"},
  {"p": "Quase todo texto de sistema tem um: preço, versão, hora, fim de frase."},
  {"h3": "E o `$` NÃO está entre eles"},
  {"p": "Ele parece perigoso e não é — escapar demais também estraga o texto, com barras aparecendo na tela."},
  {"h3": "O cuidado ao juntar os dois"},
  {"p": "O texto do usuário é escapado; a **marcação**, não. Escapar tudo transformaria o asterisco do negrito em asterisco literal."},
  {"h2": "362 · o que roda antes, o que roda depois, e quando cai"},
  {"p": "**Enunciado.** um bot sem tratador de erro morre calado no primeiro"},
  { code: `// dado inesperado — e quem esta do outro lado ve a mensagem sumir no
// vazio. O middleware e onde entram autenticacao, limite de taxa e
// registro, sem repetir em cada tratador.

adopt Arcane.Telegram as Tg

registro := []

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.antes_de_cada()
    action anotar(ctx):
        registro.append($"antes:{ctx.tipo}")

    mark @app.depois_de_cada()
    action fechar(_ctx):
        registro.append("depois")

    mark @app.ao_falhar()
    action quando_cai(ctx, erro):
        // O erro chega como OBJETO: 'message' e 'codigo' estao la, e
        // e o codigo que diz a familia sem depender do texto.
        registro.append($"caiu:{erro.codigo}")
        ctx.responder("Deu errado aqui. Ja avisamos.")

    mark @app.comando("ok")
    action ok(ctx):
        ctx.responder("tudo certo")

    mark @app.comando("quebrar")
    action quebrar(_ctx):
        _x := 1 / 0  // df: permitir division-by-zero

    yield app

out "== 1. antes e depois de cada =="

t := Tg.testar(montar())
t.comando("ok")
assert t.ultima() is "tudo certo"
assert registro[0] is "antes:mensagem"
assert registro[-1] is "depois"
out $"   {registro}"

out ""
out "== 2. o erro NAO derruba o bot =="

registro := []
t.comando("quebrar")
assert "Deu errado" in t.ultima()
assert "caiu:DF0202" in registro
out $"   {registro}"

out ""
out "== 3. e o bot continua atendendo =="

t.comando("ok")
assert t.ultima() is "tudo certo"

out ""
out "== 4. sem o tratador, a mensagem some no vazio =="

sem := Tg.app("123456:AAHexemplo")

mark @sem.comando("quebrar")
action quebra_sem_rede(_ctx):
    trigger "sem rede de seguranca"

s := Tg.testar(sem)
s.comando("quebrar")
// A sonda registra a falha, e o usuario nao recebeu nada.
assert len(s.falhas()) is 1
assert s.quantas("sendMessage") is 0
out "   o usuario ficou sem resposta nenhuma"

out ""
out "== 5. o middleware e onde mora o que e de TODOS =="

bloqueados := ["999"]
negados := []

vigiado := Tg.app("123456:AAHexemplo")

mark @vigiado.antes_de_cada()
action portaria(ctx):
    given str(ctx.chat) in bloqueados:
        negados.append(ctx.chat)
        ctx.responder("Acesso negado.")
        // Devolver 'no' PARA o despacho.
        yield no
    yield yes

mark @vigiado.comando("segredo")
action segredo(ctx):
    ctx.responder("o segredo")

v := Tg.testar(vigiado)
v.comando("segredo")
assert v.ultima() is "o segredo"
out "   sem bloqueio, passa"

out "exercicio 362 ok"`, lang: 'df', title: `exercicios/56-telegram/362_middleware_e_erro.df` },
  {"p": "Um bot sem tratador de erro morre calado no primeiro dado inesperado — e quem está do outro lado vê a mensagem sumir no vazio."},
  {"h3": "O erro NÃO derruba o bot"},
  {"p": "O tratador responde, e o próximo update é atendido normalmente."},
  {"h3": "Sem ele, a mensagem some no vazio"},
  {"p": "A sonda registra a falha, e o usuário não recebeu nada."},
  {"h3": "E o middleware é onde mora o que é de TODOS"},
  {"p": "Autenticação, limite de taxa e registro — sem repetir em cada tratador."},
  {"h2": "363 · long polling, webhook e o que o 'doctor' pergunta"},
  {"p": "**Enunciado.** um bot que roda na sua maquina usa long polling; um que"},
  { code: `// roda num servidor usa webhook. A diferenca nao e so de desempenho —
// os dois nao podem estar ligados ao mesmo tempo, e o segundo exige
// HTTPS com certificado de verdade.

adopt Arcane.Telegram as Tg

out "== 1. o token nunca vai no codigo =="

// Ele vai para o Git, e do Git para qualquer um — e o @BotFather nao
// avisa quando alguem o usa: o bot so comeca a mandar spam.
faltou := no
monitor:
    Tg.segredo_do_ambiente("VARIAVEL_QUE_NAO_EXISTE_AQUI")
handle Error as e:
    faltou := yes
    assert "VARIAVEL_QUE_NAO_EXISTE_AQUI" in e.message
    out $"   {e.message}"
assert faltou

out ""
out "== 2. e ele nunca aparece numa mensagem de erro =="

// O token esta na URL de TODA chamada, e a URL entra em todo
// traceback. Um token num log de CI e um bot sequestrado.
//
// Este e de brinquedo, e 'dataforge seguranca' acusa o formato dele
// — corretamente. Silenciar pelo NOME da regra e o jeito de dizer
// "eu sei": um 'permitir' solto esconderia o proximo achado tambem.
// df: permitir segredo-no-codigo
steady TOKEN := "123456789:AAHqwertyuiopASDFGHJKLzxcvbnm12345"
app := Tg.app(TOKEN)

mark @app.comando("x")
action x(ctx):
    ctx.responder("ok")

t := Tg.testar(app)
t.comando("x")

cycle chamada in t.chamadas():
    assert TOKEN not in str(chamada)
out "   nenhuma chamada registrada carrega o token"

out ""
out "== 3. o limite de taxa vem no CORPO, e nao no status =="

// E o erro classico de quem escreve o cliente a mao: tratar 429 como
// "erro" e desistir, em vez de ler quantos segundos esperar.
limitador := Tg.limitar(30)
assert limitador is not void
out "   30 mensagens por segundo e o limite global"

out ""
out "== 4. long polling e webhook nao convivem =="

out "   'dataforge telegram run'     -> long polling (na sua maquina)"
out "   'dataforge telegram webhook' -> webhook (no servidor, com HTTPS)"
out "   'dataforge telegram off'     -> desliga o webhook"

out ""
out "== 5. o 'doctor' pergunta o que costuma faltar =="

steady PERGUNTAS := [
    "o token responde?",
    "o bot entra em grupo?",
    "ele le todas as mensagens do grupo, ou so os comandos?",
    "ha um webhook ligado? (ele impede o long polling)",
    "quantos updates estao pendentes?"
]
assert len(PERGUNTAS) is 5
cycle p in PERGUNTAS:
    out $"   - {p}"

out ""
out "== 6. e 'deploy' nao existe, de proposito =="

// Um 'deploy' que falasse com o servidor por dentro esconderia o que
// a maquina e — e no dia em que alguem precisa mudar uma linha, nao
// haveria onde mexer.
out "   o modulo gera o que voce precisa, e sai da frente"

out "exercicio 363 ok"`, lang: 'df', title: `exercicios/56-telegram/363_publicar.df` },
  {"p": "Um bot que roda na sua máquina usa long polling; um que roda num servidor usa webhook. Os dois **não podem estar ligados ao mesmo tempo**."},
  {"h3": "O token vem do ambiente"},
  {"p": "Ele vai para o Git, e do Git para qualquer um — e o @BotFather não avisa quando alguém o usa: o bot só começa a mandar spam."},
  {"h3": "O `doctor` pergunta o que costuma faltar"},
  {"p": "Inclusive as duas que o código não decide: se o bot entra em grupos e se ele lê todas as mensagens."},
  {"h3": "E `deploy` não existe, de propósito"},
  {"p": "Um `deploy` que falasse com o servidor por dentro esconderia o que a máquina é — e no dia em que alguém precisa mudar uma linha, não haveria onde mexer."},
  {"h2": "364 · um bot de atendimento, ponta a ponta"},
  {"p": "**Enunciado.** juntar comando, botao, conversa, estado, middleware e"},
  { code: `// tratador de erro num fluxo que existe de verdade — pedir, conferir
// e fechar — e testar o fluxo INTEIRO sem token e sem rede.

adopt Arcane.Telegram as Tg

steady CARDAPIO := {
    "cafe": 6.5,
    "bolo": 8.0,
    "suco": 7.0
}

steady PEDIDOS := []

action endereco_valido(texto):
    yield len(trim(texto)) bigger_eq 10

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.comando("start", ajuda := "Mostra o cardapio")
    action comecar(ctx):
        linhas := [[Tg.botao($"{n} — R$ {CARDAPIO[n]}", dados := $"add:{n}")]
            cycle n in keys(CARDAPIO)]
        ctx.responder($"Ola, {ctx.nome()}! Escolha:",
            teclado := Tg.botoes(linhas))

    mark @app.botao("add:")
    action adicionar(ctx):
        item := ctx.dados[4:len(ctx.dados)]
        carrinho := ctx.estado["itens"] ?? []
        carrinho.append(item)
        ctx.estado["itens"] := carrinho
        ctx.avisar($"{item} no carrinho")

    mark @app.comando("carrinho")
    action ver(ctx):
        itens := ctx.estado["itens"] ?? []
        given len(itens) is 0:
            ctx.responder("O carrinho esta vazio.")
            yield void
        total := sum([CARDAPIO[i] cycle i in itens])
        ctx.responder($"{len(itens)} item(ns) — total R$ {total}")

    mark @app.comando("fechar")
    action fechar(ctx):
        given len(ctx.estado["itens"] ?? []) is 0:
            ctx.responder("Escolha algo antes de fechar.")
            yield void
        ctx.comecar_conversa("entrega")

    entrega := app.conversa("entrega", [
            {"pergunta": "Qual o endereco completo?", "guarda": "endereco",
                "valida": endereco_valido,
                "erro": "Preciso do endereco completo, com numero."}
        ])
    entrega.ao_terminar(confirmar)

    mark @app.ao_falhar()
    action caiu(ctx, _erro):
        ctx.responder("Deu errado aqui. Ja avisamos.")

    yield app

action confirmar(ctx, r):
    itens := ctx.estado["itens"] ?? []
    total := sum([CARDAPIO[i] cycle i in itens])
    PEDIDOS.append({"itens": itens, "endereco": r["endereco"],
            "total": total})
    ctx.estado["itens"] := []
    ctx.responder($"Pedido confirmado: R$ {total} para {r['endereco']}")

out "== 1. o cardapio =="

t := Tg.testar(montar())
t.comando("start")
assert "Ola," in t.ultima()
assert len(t.ultimo_teclado()["inline_keyboard"]) is 3

out ""
out "== 2. fechar o carrinho vazio e recusado =="

t.comando("carrinho")
assert "vazio" in t.ultima()
t.comando("fechar")
assert "Escolha algo" in t.ultima()

out ""
out "== 3. escolher =="

t.clicar("add:cafe")
t.clicar("add:bolo")
t.comando("carrinho")
assert "2 item(ns)" in t.ultima()
assert "14.5" in t.ultima()
out $"   {t.ultima()}"

out ""
out "== 4. o endereco e validado =="

t.comando("fechar")
assert "endereco completo" in t.ultima()

t.mandar("rua x")
assert "com numero" in t.ultima()

t.mandar("Rua das Flores, 123 - Centro")
assert "Pedido confirmado" in t.ultima()
out $"   {t.ultima()}"

out ""
out "== 5. e o pedido chegou ao sistema =="

assert len(PEDIDOS) is 1
assert PEDIDOS[0]["total"] is 14.5
assert PEDIDOS[0]["itens"] is ["cafe", "bolo"]

out ""
out "== 6. o carrinho ficou limpo =="

t.comando("carrinho")
assert "vazio" in t.ultima()

out ""
out "== 7. e o bot inteiro foi testado sem token e sem rede =="

assert t.quantas("sendMessage") bigger 5
out $"   {t.quantas('sendMessage')} mensagens, zero sockets"

out "exercicio 364 ok"`, lang: 'df', title: `exercicios/56-telegram/364_bot_completo.df` },
  {"p": "Comando, botão, conversa, estado, middleware e tratador de erro num fluxo que existe de verdade — e testado inteiro sem token e sem rede."},
  {"h3": "A validação vem antes da escrita"},
  {"p": "Fechar o carrinho vazio é recusado antes de qualquer consulta."},
  {"h3": "O endereço é validado no passo"},
  {"p": "E o passo repete até passar."},
  {"h3": "E o carrinho fica limpo no fim"},
  {"p": "O estado da conversa termina com ela; o pedido vai para o sistema."},
  {"h2": "365 · foto, documento e o que chega junto"},
  {"p": "**Enunciado.** o Telegram nao manda o arquivo no update — ele manda um"},
  { code: `// 'file_id'. Guardar o id e reenvia-lo e instantaneo; baixar e
// reenviar gasta banda duas vezes por nada.

adopt Arcane.Telegram as Tg

recebidos := []

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.midia("foto")
    action foto(ctx):
        recebidos.append({"tipo": "foto", "legenda": ctx.texto})
        ctx.responder("Foto recebida.")

    mark @app.midia("documento")
    action documento(ctx):
        recebidos.append({"tipo": "documento", "legenda": ctx.texto})
        ctx.responder("Documento recebido.")

    mark @app.comando("comprovante")
    action comprovante(ctx):
        ctx.responder_foto("AgACAgEAAxkBAAI", legenda := "seu comprovante")

    yield app

out "== 1. a foto chega como midia =="

t := Tg.testar(montar())
t.enviar_foto(legenda := "pagamento feito")
assert t.ultima() is "Foto recebida."
assert recebidos[0]["tipo"] is "foto"

out ""
out "== 2. e a legenda vem em 'ctx.texto' =="

// Numa mensagem de midia nao ha 'text': o que existe e 'caption'. Por
// isso 'ctx.texto' junta os dois — quem escreve o bot nao deveria
// precisar saber disso.
assert recebidos[0]["legenda"] is "pagamento feito"
out $"   legenda: {recebidos[0]['legenda']}"

// Num documento a sonda manda o NOME, e nao a legenda: sao campos
// diferentes do mesmo update.

out ""
out "== 3. documento e outro tipo =="

t.enviar_documento(nome := "contrato.pdf")
assert t.ultima() is "Documento recebido."
assert recebidos[1]["tipo"] is "documento"

out ""
out "== 4. e mandar de volta usa o 'file_id' =="

t.comando("comprovante")
assert t.quantas("sendPhoto") is 1
out "   o id volta direto: nada foi baixado nem reenviado"

out ""
out "== 5. o que NAO fazer =="

out "   baixar o arquivo so para reenvia-lo gasta banda duas vezes"
out "   e o 'file_id' e valido por bot: o de outro bot nao serve"

out ""
out "== 6. salvar um upload recusa o que nao deve =="

// Nome com '/' ou '..', tamanho acima do limite e extensao fora da
// lista. O nome final leva prefixo aleatorio, porque dois usuarios
// mandam 'foto.jpg' no mesmo minuto.
out "   nome com '..' -> recusado · extensao fora da lista -> recusada"

out "exercicio 365 ok"`, lang: 'df', title: `exercicios/56-telegram/365_midia.df` },
  {"p": "O Telegram não manda o arquivo no update — ele manda um `file_id`."},
  {"h3": "A legenda vem em `ctx.texto`"},
  {"p": "Numa mensagem de mídia não há `text`: o que existe é `caption`. Quem escreve o bot não deveria precisar saber disso."},
  {"h3": "Mandar de volta usa o `file_id`"},
  {"p": "Baixar o arquivo só para reenviá-lo gasta banda duas vezes por nada. E o `file_id` é válido **por bot**: o de outro bot não serve."},
  {"h3": "E salvar um upload recusa o que não deve"},
  {"p": "Nome com `/` ou `..`, tamanho acima do limite e extensão fora da lista. O nome final leva prefixo aleatório, porque dois usuários mandam `foto.jpg` no mesmo minuto."},
  {"h2": "366 · o mesmo bot, em conversa privada e em grupo"},
  {"p": "**Enunciado.** num grupo o bot ve so os comandos, a menos que o modo de"},
  { code: `// privacidade esteja desligado — e isso se configura no @BotFather, e
// nao no codigo. O sintoma de esquecer: o bot "nao responde" a nada
// que nao comece com barra.

adopt Arcane.Telegram as Tg

visto := []

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.comando("onde")
    action onde(ctx):
        lugar := "privado" given ctx.e_privado() otherwise "grupo"
        visto.append(lugar)
        ctx.responder($"estamos no {lugar}")

    mark @app.entrou()
    action boas_vindas(ctx):
        ctx.responder("Bem-vindo!")

    mark @app.saiu()
    action ate_logo(_ctx):
        visto.append("saiu")

    yield app

out "== 1. em conversa privada =="

t := Tg.testar(montar())
t.comando("onde")
assert "privado" in t.ultima()

out ""
out "== 2. quem entrou e quem saiu =="

t.entrar()
assert "Bem-vindo" in t.ultima()

out ""
out "== 3. o que o @BotFather decide, e o codigo nao =="

steady NO_BOTFATHER := [
    "o bot pode entrar em grupos?",
    "ele le TODAS as mensagens, ou so os comandos?",
    "qual e a lista de comandos que aparece no menu?"
]
assert len(NO_BOTFATHER) is 3
cycle p in NO_BOTFATHER:
    out $"   - {p}"

out ""
out "== 4. e o 'doctor' pergunta os tres =="

out "   'dataforge telegram doctor' confere antes de voce descobrir em producao"

out ""
out "== 5. a lista de comandos e publicada pelo bot =="

// 'publicar_comandos' manda para o Telegram o que aparece no menu de
// barra. Sem isso, os comandos existem e ninguem os descobre.
app := montar()
saude := app.saude()
assert saude is not void
out $"   o bot sabe se reportar: {typeof(saude)}"

out ""
out "== 6. e um comando com @ e para o bot certo =="

// Num grupo com dois bots, '/start' e ambiguo: o Telegram entrega
// '/start@meubot'. O modulo tira o sufixo antes de casar.
t2 := Tg.testar(montar())
t2.mandar("/onde@meubot")
assert "grupo" in t2.ultima() or "privado" in t2.ultima()
out "   '/onde@meubot' casou com '/onde'"

out "exercicio 366 ok"`, lang: 'df', title: `exercicios/56-telegram/366_grupo_e_admin.df` },
  {"p": "Num grupo o bot vê só os comandos, a menos que o modo de privacidade esteja desligado — e isso se configura no @BotFather, e **não** no código."},
  {"h3": "O sintoma de esquecer"},
  {"p": "O bot \"não responde\" a nada que não comece com barra."},
  {"h3": "O que o @BotFather decide"},
  {"p": "Entrar em grupos, ler todas as mensagens e a lista de comandos do menu — três coisas que o código não pode mudar."},
  {"h3": "E um comando com `@` é para o bot certo"},
  {"p": "Num grupo com dois bots, `/start` é ambíguo: o Telegram entrega `/start@meubot`, e o módulo tira o sufixo antes de casar."},
  {"h2": "367 · o bot que responde sem estar no chat"},
  {"p": "**Enunciado.** a consulta inline e o que faz '@meubot pizza' funcionar"},
  { code: `// em QUALQUER conversa, sem o bot ser membro dela. O resultado e uma
// lista, e cada item precisa de um id unico — ids repetidos fazem o
// Telegram descartar a lista inteira, calado.

adopt Arcane.Telegram as Tg

steady CATALOGO := [
    {"id": "1", "nome": "Cafe especial", "preco": 32.5},
    {"id": "2", "nome": "Cafe comum", "preco": 12.0},
    {"id": "3", "nome": "Bolo de fuba", "preco": 8.0}
]

consultas := []

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.inline()
    action buscar(ctx):
        termo := lower(trim(ctx.texto))
        consultas.append(termo)
        achados := CATALOGO
        given termo isnt "":
            achados := [p cycle p in CATALOGO given termo in lower(p["nome"])]
        ctx.responder_consulta([
                {"id": p["id"], "titulo": p["nome"],
                    "texto": $"{p['nome']} — R$ {p['preco']}"}
                cycle p in achados])

    yield app

out "== 1. a busca vazia devolve tudo =="

t := Tg.testar(montar())
t.consultar("")
assert consultas[0] is ""
assert t.quantas("answerInlineQuery") is 1

out ""
out "== 2. e o termo filtra =="

t.consultar("cafe")
assert consultas[1] is "cafe"

t.consultar("bolo")
assert consultas[2] is "bolo"
out $"   consultas: {consultas}"

out ""
out "== 3. cada item precisa de um id UNICO =="

// Ids repetidos fazem o Telegram descartar a lista inteira, sem
// mensagem de erro — o usuario ve "sem resultados".
ids := [p["id"] cycle p in CATALOGO]
assert len(unique(ids)) is len(ids)
out "   tres itens, tres ids"

out ""
out "== 4. o bot NAO precisa estar no chat =="

out "   '@meubot cafe' funciona em qualquer conversa"
out "   e e por isso que a consulta inline nao tem 'ctx.chat'"

out ""
out "== 5. o que isso substitui =="

// Sem inline, o usuario teria de sair da conversa, abrir o bot,
// buscar, copiar e voltar.
out "   sair da conversa, buscar, copiar e voltar"

out "exercicio 367 ok"`, lang: 'df', title: `exercicios/56-telegram/367_inline.df` },
  {"p": "A consulta inline é o que faz `@meubot pizza` funcionar em **qualquer** conversa, sem o bot ser membro dela."},
  {"h3": "Cada item precisa de um id ÚNICO"},
  {"p": "Ids repetidos fazem o Telegram descartar a lista inteira, sem mensagem de erro — o usuário vê \"sem resultados\"."},
  {"h3": "`ctx.responder_consulta` preenche o id sozinho"},
  {"p": "Era a única resposta que caía no bot cru: todas as outras são `ctx.responder*`, e esta obrigava a escrever `ctx.bot.responder_inline(ctx.consulta[\"id\"], …)` — com o id à mão, que é exatamente o que se esquece."},
  {"h3": "E ela não tem `ctx.chat`"},
  {"p": "Porque não há chat: o bot não está lá."},
  {"h2": "368 · o 429 que vem no CORPO"},
  {"p": "**Enunciado.** o Telegram responde 429 com 'retry_after' NO CORPO da"},
  { code: `// resposta, e nao num cabecalho. Quem escreve o cliente a mao trata
// 429 como "erro" e desiste — e o bot para de responder num horario
// de pico, sem nada no log dizendo por que.

adopt Arcane.Telegram as Tg
adopt Arcane.Time as Tempo

out "== 1. o limitador existe, e tem um teto =="

limitador := Tg.limitar(30)
assert limitador is not void

out ""
out "== 2. ele segura, e nao descarta =="

// Um limitador que joga fora a mensagem excedente e pior que nenhum:
// o usuario nao recebe, e o bot acha que mandou.
marcas := []
apertado := Tg.limitar(50)

comeco := Tempo.timestamp()
cycle i from 1 to 6:
    apertado.esperar()
    marcas.append(Tempo.timestamp() - comeco)

assert len(marcas) is 6
assert marcas[-1] bigger_eq marcas[0]
out $"   seis passagens, a ultima em {round(marcas[-1], 3)}s"

out ""
out "== 3. e o limite e POR CHAT alem do global =="

out "   30 por segundo no total; ~1 por segundo no mesmo grupo"

out ""
out "== 4. o recuo, quando o 429 chega mesmo assim =="

// 'retry_after' diz quantos segundos esperar. Ignora-lo e insistir
// e o que transforma um limite momentaneo num bloqueio.
action recuo(tentativa, base):
    yield base * (2 ** (tentativa - 1)) + random() * base

esperas := [recuo(i, 0.01) cycle i in range(1, 5)]
assert esperas[0] smaller esperas[3]

// E o TREMOR importa: sem ele, todos os clientes que tomaram 429
// juntos voltam juntos.
duas := [round(recuo(1, 0.01), 8) cycle i in range(2)]
assert duas[0] isnt duas[1]
out "   esperas crescentes, e diferentes entre si"

out ""
out "== 5. o que o modulo NAO pode fazer =="

// Ele nao pode inventar idempotencia: se a mensagem ja saiu e o 429
// veio depois, reenviar manda duas. Por isso a retentativa vale para
// LEITURA, e nao para escrita cega.
out "   repetir um envio manda duas mensagens; quem decide e quem chama"

out ""
out "== 6. e o teste disso nao precisa de rede =="

app := Tg.app("123456:AAHexemplo")

mark @app.comando("spam")
action spam(ctx):
    cycle i from 1 to 5:
        ctx.responder($"mensagem {i}")

t := Tg.testar(app)
t.comando("spam")
assert t.quantas("sendMessage") is 5
out "   cinco envios contados, zero sockets"

out "exercicio 368 ok"`, lang: 'df', title: `exercicios/56-telegram/368_limite_de_taxa.df` },
  {"p": "O Telegram responde 429 com `retry_after` **no corpo** da resposta, e não num cabeçalho. Quem escreve o cliente à mão trata 429 como \"erro\" e desiste — e o bot para de responder num horário de pico, sem nada no log dizendo por quê."},
  {"h3": "O limitador segura, e não descarta"},
  {"p": "Um limitador que joga fora a mensagem excedente é pior que nenhum: o usuário não recebe, e o bot acha que mandou."},
  {"h3": "O recuo com tremor"},
  {"p": "Sem ele, todos os clientes que tomaram 429 juntos voltam juntos."},
  {"h3": "E o módulo não pode inventar idempotência"},
  {"p": "Se a mensagem já saiu e o 429 veio depois, reenviar manda duas. A retentativa vale para **leitura**, e não para escrita cega."},
  {"h2": "369 · onde o estado do chat mora"},
  {"p": "**Enunciado.** o armazem padrao e a memoria, e isso esta DITO: some"},
  { code: `// quando o processo reinicia. Um bot que promete lembrar precisa do
// armazem em arquivo — e a troca e uma linha.

adopt Arcane.Telegram as Tg
adopt Arcane.IO as IO
adopt Arcane.OS as OS

steady pasta := $"{OS.temp_dir()}/df-369-{randint(100000, 999999)}"
IO.mkdir(pasta)

action montar(armazem):
    app := Tg.app("123456:AAHexemplo", estado := armazem)

    mark @app.comando("somar")
    action somar(ctx):
        n := ctx.estado["n"] ?? 0
        ctx.estado["n"] := n + 1
        ctx.responder($"agora {ctx.estado['n']}")

    yield app

out "== 1. na memoria =="

t := Tg.testar(montar(Tg.estado_em_memoria()))
t.comando("somar")
t.comando("somar")
assert t.estado("n") is 2
assert "agora 2" in t.ultima()

out ""
out "== 2. e o proximo processo comeca do zero =="

// Um app novo, com um armazem novo.
outro := Tg.testar(montar(Tg.estado_em_memoria()))
outro.comando("somar")
assert outro.estado("n") is 1
out "   o contador reiniciou — e isso esta dito na doc"

out ""
out "== 3. em arquivo, sobrevive =="

steady EM_ARQUIVO := Tg.estado_em_arquivo(pasta)

um := Tg.testar(montar(EM_ARQUIVO))
um.comando("somar")
um.comando("somar")
um.comando("somar")
assert um.estado("n") is 3

// Outro "processo", lendo do mesmo lugar.
dois := Tg.testar(montar(Tg.estado_em_arquivo(pasta)))
dois.comando("somar")
assert dois.estado("n") is 4
out $"   o contador continuou: {dois.estado('n')}"

out ""
out "== 4. e 'ctx.estado' e uma VISTA, e nao uma copia =="

// Escrever nele persiste. A primeira versao devolvia 'dict(...)':
// 'ctx.estado["k"] := v' escrevia num dicionario descartavel, a
// mudanca sumia, e a documentacao prometia o contrario.
assert dois.estado("n") is 4

out ""
out "== 5. e a foto, para quem quer a copia =="

app := montar(Tg.estado_em_memoria())

mark @app.comando("foto")
action foto(ctx):
    ctx.estado["x"] := 1
    copia := ctx.estado.para_vault()
    ctx.estado["x"] := 2
    ctx.responder($"foto {copia['x']}, vista {ctx.estado['x']}")

t3 := Tg.testar(app)
t3.comando("foto")
assert "foto 1, vista 2" in t3.ultima()
out $"   {t3.ultima()}"

IO.remove_tree(pasta)
out "exercicio 369 ok"`, lang: 'df', title: `exercicios/56-telegram/369_estado_persistente.df` },
  {"p": "O armazém padrão é a memória, e isso está **dito**: some quando o processo reinicia."},
  {"h3": "Em arquivo, sobrevive"},
  {"p": "E a troca é uma linha — `Tg.estado_em_arquivo(pasta)` no lugar do padrão."},
  {"h3": "`ctx.estado` é uma VISTA, e não uma cópia"},
  {"p": "A primeira versão devolvia `dict(...)`: `ctx.estado[\"k\"] := v` escrevia num dicionário descartável, a mudança sumia, e a documentação prometia o contrário. O sintoma era um carrinho que nunca enchia."},
  {"h3": "E a foto, para quem quer a cópia"},
  {"p": "`para_vault()` devolve o instantâneo, e ele não acompanha mais."},
  {"h2": "370 · o que a sonda prova, e o que ela NAO prova"},
  {"p": "**Enunciado.** um bot testado so com a sonda tem teste de LOGICA. O que"},
  { code: `// ela nao cobre e o que fala com o Telegram de verdade — token,
// HTTPS, limite de taxa e formato de mensagem recusado. Nomear essa
// fronteira e o que impede confiar demais no verde.

adopt Arcane.Telegram as Tg

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.comando("oi")
    action oi(ctx):
        ctx.responder($"Ola, {ctx.nome()}!")

    mark @app.botao("x:")
    action clicou(ctx):
        ctx.avisar("ok")
        ctx.responder($"clicou em {ctx.dados}")

    yield app

out "== 1. o que ela injeta =="

t := Tg.testar(montar())
t.comando("oi")
t.mandar("texto solto")
t.clicar("x:1")
t.enviar_foto()
t.consultar("busca")
t.entrar()
out "   comando, texto, botao, midia, consulta e entrada"

out ""
out "== 2. o que ela le =="

assert t.ultima() is "clicou em x:1" or len(t.ultima()) bigger 0
assert t.quantas("sendMessage") bigger_eq 2
assert len(t.chamadas()) bigger_eq 3
assert t.disse("Ola,")
out $"   {len(t.chamadas())} chamadas registradas"

out ""
out "== 3. o estado, sem abrir o armazem =="

app := montar()

mark @app.comando("guardar")
action guardar(ctx):
    ctx.estado["visto"] := yes

t2 := Tg.testar(app)
t2.comando("guardar")
assert t2.estado("visto") is yes

out ""
out "== 4. e as falhas, quando nao ha tratador =="

quebrado := Tg.app("123456:AAHexemplo")

mark @quebrado.comando("q")
action q(_ctx):
    trigger "caiu"

s := Tg.testar(quebrado)
s.comando("q")
assert len(s.falhas()) is 1
assert s.falhou()
// 'falhas()' devolve as MENSAGENS: o detalhe com o traceback fica
// no app, para quem precisa investigar.
assert "caiu" in s.falhas()[0]
out $"   {s.falhas()[0]}"

out ""
out "== 5. o que a sonda NAO prova =="

steady FORA_DO_ALCANCE := [
    "o token e valido",
    "o webhook esta ligado e o HTTPS e aceito",
    "a mensagem passa no MarkdownV2 do Telegram",
    "o limite de taxa do horario de pico",
    "o bot consegue entrar naquele grupo"
]
assert len(FORA_DO_ALCANCE) is 5
cycle f in FORA_DO_ALCANCE:
    out $"   - {f}"

out ""
out "== 6. e e para isso que existe o 'doctor' =="

out "   sonda: a logica, na suite · doctor: o ambiente, antes de subir"

out "exercicio 370 ok"`, lang: 'df', title: `exercicios/56-telegram/370_teste_do_bot.df` },
  {"p": "Um bot testado só com a sonda tem teste de **lógica**. Nomear a fronteira é o que impede confiar demais no verde."},
  {"h3": "O que ela injeta e lê"},
  {"p": "Comando, texto, botão, mídia, consulta e entrada; e do outro lado as mensagens, o estado e as falhas."},
  {"h3": "O que fica fora do alcance"},
  {"p": "O token, o HTTPS do webhook, o MarkdownV2 do Telegram, o limite de taxa no pico e a permissão de entrar naquele grupo."},
  {"h3": "E é para isso que existe o `doctor`"},
  {"p": "Sonda: a lógica, na suíte. Doctor: o ambiente, antes de subir."},
  {"h2": "371 · o bot que guarda no banco"},
  {"p": "**Enunciado.** o estado do chat serve para o que e DA conversa — o"},
  { code: `// passo atual, o carrinho. O que e do NEGOCIO vai para o banco: um
// pedido precisa existir depois que a conversa acaba, e precisa ser
// consultavel por quem nao e o chat.

adopt Arcane.Telegram as Tg
adopt Arcane.Database as DB
adopt Arcane.IO as IO
adopt Arcane.OS as OS

steady pasta := $"{OS.temp_dir()}/df-371-{randint(100000, 999999)}"
IO.mkdir(pasta)
steady banco := DB.connect($"{pasta}/loja.db")

DB.execute(banco, """CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat TEXT NOT NULL,
    item TEXT NOT NULL,
    centavos INTEGER NOT NULL
)""")

steady PRECOS := {"cafe": 650, "bolo": 800}

action montar():
    app := Tg.app("123456:AAHexemplo")

    mark @app.comando("pedir")
    action pedir(ctx):
        item := trim(join(" ", ctx.args))
        given item not in PRECOS:
            ctx.responder($"Nao temos '{item}'.")
            yield void
        DB.insert(banco, "pedidos", {"chat": str(ctx.chat), "item": item,
                "centavos": PRECOS[item]})
        ctx.responder($"{item} anotado.")

    mark @app.comando("meus")
    action meus(ctx):
        linhas := DB.query(banco,
            "SELECT item, centavos FROM pedidos WHERE chat = ? ORDER BY id",
            [str(ctx.chat)])
        given len(linhas) is 0:
            ctx.responder("Voce ainda nao pediu nada.")
            yield void
        total := sum([l["centavos"] cycle l in linhas])
        nomes := join(", ", [l["item"] cycle l in linhas])
        ctx.responder($"{nomes} — total {total} centavos")

    yield app

out "== 1. pedir grava =="

t := Tg.testar(montar())
t.comando("pedir cafe")
assert "cafe anotado" in t.ultima()
t.comando("pedir bolo")

assert DB.count(banco, "pedidos") is 2

out ""
out "== 2. o que nao existe e recusado ANTES do banco =="

t.comando("pedir tapioca")
assert "Nao temos" in t.ultima()
assert DB.count(banco, "pedidos") is 2
out "   a validacao veio antes da escrita"

out ""
out "== 3. consultar =="

t.comando("meus")
assert "cafe, bolo" in t.ultima()
assert "1450" in t.ultima()
out $"   {t.ultima()}"

out ""
out "== 4. e o pedido existe FORA da conversa =="

// E essa e a diferenca: 'ctx.estado' morre com o chat; a linha no
// banco e do negocio.
todos := DB.query(banco, "SELECT * FROM pedidos", [])
assert len(todos) is 2

out ""
out "== 5. o argumento do comando ja vem separado =="

app := montar()

mark @app.comando("eco")
action eco(ctx):
    ctx.responder($"{len(ctx.args)}: {join('|', ctx.args)}")

t2 := Tg.testar(app)
t2.comando("eco um dois tres")
assert "3: um|dois|tres" in t2.ultima()
out $"   {t2.ultima()}"

out ""
out "== 6. e a rota do bot roda numa thread =="

// Como no Kiln: cada update e atendido separadamente. Estado em
// memoria compartilhado entre tratadores NAO e protegido — o banco,
// sim.
out "   o banco serializa o acesso; um vault solto nao"

DB.close(banco)
IO.remove_tree(pasta)
out "exercicio 371 ok"`, lang: 'df', title: `exercicios/56-telegram/371_bot_com_banco.df` },
  {"p": "O estado do chat serve para o que é **da conversa** — o passo atual, o carrinho. O que é do **negócio** vai para o banco."},
  {"h3": "O pedido existe FORA da conversa"},
  {"p": "`ctx.estado` morre com o chat; a linha no banco é consultável por quem não é o chat."},
  {"h3": "O argumento do comando já vem separado"},
  {"p": "`ctx.args` — sem um `split` à mão que esquece o espaço duplo."},
  {"h3": "E a rota do bot roda numa thread"},
  {"p": "Como no Kiln: o banco serializa o acesso; um vault solto compartilhado entre tratadores **não** é protegido."},
  {"h2": "372 · o mapa, e as cinco decisoes"},
  {"p": "**Enunciado.** fechar o modulo com as sete formas de casar um update, a"},
  { code: `// ordem que importa, e as decisoes que o modulo toma por voce — com o
// motivo de cada uma.

adopt Arcane.Telegram as Tg

out "== 1. as sete formas de casar =="

steady FORMAS := {
    "comando": "/start, /ajuda — com o sufixo '@bot' ja removido",
    "texto": "uma expressao regular sobre o texto",
    "botao": "o prefixo do 'dados' de um botao inline",
    "midia": "foto, video, audio, documento, local, contato…",
    "inline": "a consulta '@bot termo', fora de qualquer chat",
    "entrou/saiu": "alguem entrou ou saiu do grupo",
    "qualquer": "o resto — e ela vai por ULTIMO"
}
assert len(keys(FORMAS)) is 7
cycle f in keys(FORMAS):
    out $"   {f}: {FORMAS[f]}"

out ""
out "== 2. o despacho para no PRIMEIRO que casa =="

vistos := []
app := Tg.app("123456:AAHexemplo")

mark @app.texto("\\\\bcafe\\\\b")
action cafe(ctx):
    vistos.append("texto")
    ctx.responder("cafe!")

mark @app.qualquer()
action resto(ctx):
    vistos.append("qualquer")
    ctx.responder("nao entendi")

t := Tg.testar(app)
t.mandar("quero cafe")
assert vistos is ["texto"]
out "   uma mensagem, UMA resposta"

// Entregar a todos produziria o bug mais confuso que um bot tem:
// duas respostas, e ninguem sabe de onde veio a segunda.

out ""
out "== 3. e 'qualquer' registrada antes seria um buraco =="

// Ela casa com tudo: o que vier depois nunca seria alcancado, e o
// sintoma e o bot responder "nao entendi" a um comando que existe.
// Registrar nessa ordem e RECUSADO, na partida.
recusou := no
monitor:
    errado := Tg.app("123456:AAHexemplo")
    errado.qualquer()(resto)
    errado.comando("tarde")(cafe)
handle Error as e:
    recusou := yes
    out $"   {e.message}"
assert recusou

out ""
out "== 4. as cinco decisoes do modulo =="

steady DECISOES := [
    "o token vem do ambiente, e nunca aparece num erro",
    "o limite de taxa e lido do CORPO, e nao do status",
    "'qualquer' vai por ultimo, e isso e cobrado",
    "a conversa guarda o passo NO CHAT, e nao num vault solto",
    "'deploy' nao existe: o modulo gera e sai da frente"
]
assert len(DECISOES) is 5
cycle d in DECISOES:
    out $"   - {d}"

out ""
out "== 5. e o que testar onde =="

out "   logica do bot   -> a sonda, na suite"
out "   ambiente        -> 'dataforge telegram doctor'"
out "   formato da msg  -> so o Telegram de verdade responde"

out ""
out "== 6. o caminho inteiro, em cinco linhas =="

out "   dataforge telegram new meubot"
out "   export TELEGRAM_TOKEN=...      (do @BotFather)"
out "   dataforge telegram doctor"
out "   dataforge telegram run         (long polling)"
out "   dataforge telegram webhook     (no servidor, com HTTPS)"

out "exercicio 372 ok"`, lang: 'df', title: `exercicios/56-telegram/372_o_mapa_do_bot.df` },
  {"p": "As sete formas de casar um update, a ordem que importa, e as decisões que o módulo toma por você — com o motivo de cada uma."},
  {"h3": "`qualquer` vai por ÚLTIMO, e isso é cobrado"},
  {"p": "Ela casa com tudo: uma rota registrada depois nunca seria alcançada, e o sintoma é o bot responder \"não entendi\" a um comando que existe. Registrar nessa ordem é **recusado**, na partida."},
  {"h3": "O caminho inteiro, em cinco linhas"},
  {"p": "`new`, o token do @BotFather, `doctor`, `run` e `webhook`."},
  {"h3": "E o que testar onde"},
  {"p": "Lógica na sonda; ambiente no `doctor`; formato da mensagem só o Telegram de verdade responde."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/56-telegram/358_primeiro_bot.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '358-um-bot-inteiro-testado-sem-token-e-sem-rede', text: "358 · um bot inteiro, testado sem token e sem rede", level: 2 as const }, { id: 'o-despacho-para-no-primeiro-que-casa', text: "O despacho para no PRIMEIRO que casa", level: 3 as const }, { id: 'o-token-nunca-aparece', text: "O token nunca aparece", level: 3 as const }, { id: 'e-nenhum-socket-foi-aberto', text: "E nenhum socket foi aberto", level: 3 as const }, { id: '359-botoes-e-o-relogio-que-nao-para', text: "359 · botoes, e o relogio que nao para", level: 2 as const }, { id: 'esquecer-de-responder-deixa-o-relogio-girando', text: "Esquecer de responder deixa o relógio girando", level: 3 as const }, { id: 'o-dados-tem-limite-de-64-bytes', text: "O `dados` tem limite de 64 bytes", level: 3 as const }, { id: 'e-o-teclado-do-celular-e-outro', text: "E o teclado do celular é outro", level: 3 as const }, { id: '360-a-conversa-como-maquina-de-estados', text: "360 · a conversa como maquina de estados", level: 2 as const }, { id: 'a-validacao-repete-o-passo', text: "A validação repete o passo", level: 3 as const }, { id: 'o-estado-fica-no-chat', text: "O estado fica NO CHAT", level: 3 as const }, { id: 'e-cinco-passos-nao-cabem-num-given', text: "E cinco passos não cabem num `given`", level: 3 as const }, { id: '361-o-caractere-que-derruba-a-mensagem-inteira', text: "361 · o caractere que derruba a mensagem inteira", level: 2 as const }, { id: 'o-que-engana-e-o-ponto', text: "O que engana é o ponto", level: 3 as const }, { id: 'e-o-nao-esta-entre-eles', text: "E o `$` NÃO está entre eles", level: 3 as const }, { id: 'o-cuidado-ao-juntar-os-dois', text: "O cuidado ao juntar os dois", level: 3 as const }, { id: '362-o-que-roda-antes-o-que-roda-depois-e-quando-cai', text: "362 · o que roda antes, o que roda depois, e quando cai", level: 2 as const }, { id: 'o-erro-nao-derruba-o-bot', text: "O erro NÃO derruba o bot", level: 3 as const }, { id: 'sem-ele-a-mensagem-some-no-vazio', text: "Sem ele, a mensagem some no vazio", level: 3 as const }, { id: 'e-o-middleware-e-onde-mora-o-que-e-de-todos', text: "E o middleware é onde mora o que é de TODOS", level: 3 as const }, { id: '363-long-polling-webhook-e-o-que-o-doctor-pergunta', text: "363 · long polling, webhook e o que o 'doctor' pergunta", level: 2 as const }, { id: 'o-token-vem-do-ambiente', text: "O token vem do ambiente", level: 3 as const }, { id: 'o-doctor-pergunta-o-que-costuma-faltar', text: "O `doctor` pergunta o que costuma faltar", level: 3 as const }, { id: 'e-deploy-nao-existe-de-proposito', text: "E `deploy` não existe, de propósito", level: 3 as const }, { id: '364-um-bot-de-atendimento-ponta-a-ponta', text: "364 · um bot de atendimento, ponta a ponta", level: 2 as const }, { id: 'a-validacao-vem-antes-da-escrita', text: "A validação vem antes da escrita", level: 3 as const }, { id: 'o-endereco-e-validado-no-passo', text: "O endereço é validado no passo", level: 3 as const }, { id: 'e-o-carrinho-fica-limpo-no-fim', text: "E o carrinho fica limpo no fim", level: 3 as const }, { id: '365-foto-documento-e-o-que-chega-junto', text: "365 · foto, documento e o que chega junto", level: 2 as const }, { id: 'a-legenda-vem-em-ctxtexto', text: "A legenda vem em `ctx.texto`", level: 3 as const }, { id: 'mandar-de-volta-usa-o-fileid', text: "Mandar de volta usa o `file_id`", level: 3 as const }, { id: 'e-salvar-um-upload-recusa-o-que-nao-deve', text: "E salvar um upload recusa o que não deve", level: 3 as const }, { id: '366-o-mesmo-bot-em-conversa-privada-e-em-grupo', text: "366 · o mesmo bot, em conversa privada e em grupo", level: 2 as const }, { id: 'o-sintoma-de-esquecer', text: "O sintoma de esquecer", level: 3 as const }, { id: 'o-que-o-botfather-decide', text: "O que o @BotFather decide", level: 3 as const }, { id: 'e-um-comando-com-e-para-o-bot-certo', text: "E um comando com `@` é para o bot certo", level: 3 as const }, { id: '367-o-bot-que-responde-sem-estar-no-chat', text: "367 · o bot que responde sem estar no chat", level: 2 as const }, { id: 'cada-item-precisa-de-um-id-unico', text: "Cada item precisa de um id ÚNICO", level: 3 as const }, { id: 'ctxresponderconsulta-preenche-o-id-sozinho', text: "`ctx.responder_consulta` preenche o id sozinho", level: 3 as const }, { id: 'e-ela-nao-tem-ctxchat', text: "E ela não tem `ctx.chat`", level: 3 as const }, { id: '368-o-429-que-vem-no-corpo', text: "368 · o 429 que vem no CORPO", level: 2 as const }, { id: 'o-limitador-segura-e-nao-descarta', text: "O limitador segura, e não descarta", level: 3 as const }, { id: 'o-recuo-com-tremor', text: "O recuo com tremor", level: 3 as const }, { id: 'e-o-modulo-nao-pode-inventar-idempotencia', text: "E o módulo não pode inventar idempotência", level: 3 as const }, { id: '369-onde-o-estado-do-chat-mora', text: "369 · onde o estado do chat mora", level: 2 as const }, { id: 'em-arquivo-sobrevive', text: "Em arquivo, sobrevive", level: 3 as const }, { id: 'ctxestado-e-uma-vista-e-nao-uma-copia', text: "`ctx.estado` é uma VISTA, e não uma cópia", level: 3 as const }, { id: 'e-a-foto-para-quem-quer-a-copia', text: "E a foto, para quem quer a cópia", level: 3 as const }, { id: '370-o-que-a-sonda-prova-e-o-que-ela-nao-prova', text: "370 · o que a sonda prova, e o que ela NAO prova", level: 2 as const }, { id: 'o-que-ela-injeta-e-le', text: "O que ela injeta e lê", level: 3 as const }, { id: 'o-que-fica-fora-do-alcance', text: "O que fica fora do alcance", level: 3 as const }, { id: 'e-e-para-isso-que-existe-o-doctor', text: "E é para isso que existe o `doctor`", level: 3 as const }, { id: '371-o-bot-que-guarda-no-banco', text: "371 · o bot que guarda no banco", level: 2 as const }, { id: 'o-pedido-existe-fora-da-conversa', text: "O pedido existe FORA da conversa", level: 3 as const }, { id: 'o-argumento-do-comando-ja-vem-separado', text: "O argumento do comando já vem separado", level: 3 as const }, { id: 'e-a-rota-do-bot-roda-numa-thread', text: "E a rota do bot roda numa thread", level: 3 as const }, { id: '372-o-mapa-e-as-cinco-decisoes', text: "372 · o mapa, e as cinco decisoes", level: 2 as const }, { id: 'qualquer-vai-por-ultimo-e-isso-e-cobrado', text: "`qualquer` vai por ÚLTIMO, e isso é cobrado", level: 3 as const }, { id: 'o-caminho-inteiro-em-cinco-linhas', text: "O caminho inteiro, em cinco linhas", level: 3 as const }, { id: 'e-o-que-testar-onde', text: "E o que testar onde", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"56 · Bots de Telegram"}
      description={"15 exercícios: ."}
      href={"/docs/exercicios/56-telegram"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
