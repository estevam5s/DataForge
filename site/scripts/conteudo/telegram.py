# -*- coding: utf-8 -*-
"""Arcane.Telegram — bots de Telegram, do primeiro /start ao webhook."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram",
"title": "Bots de Telegram",
"description": "Comandos, botões, conversa com estado e webhook — e testes que rodam sem token e sem rede.",
"blocos": [
 {"p": "**`Arcane.Telegram`** é o módulo de bots. A Bot API do Telegram é HTTP com JSON: falar com ela do zero é possível e chato — noventa métodos, um formato de erro próprio, um limite de taxa que responde no **corpo** e não no status, upload multipart, e uma sintaxe de formatação que quebra a mensagem inteira se um caractere escapar."},
 {"code": """adopt Arcane.Telegram as Tg

app := Tg.app(Tg.segredo_do_ambiente())

mark @app.comando("start")
action comecar(ctx):
    ctx.responder($"Ola, {ctx.nome()}!")

app.rodar()""", "lang": "df"},
 {"p": "Isso é o bot inteiro. `ctx` traz quem falou, o que disse e como responder; o `rodar` faz long polling até alguém parar."},

 {"h2": "Do zero ao bot no ar"},
 {"code": """dataforge telegram new meubot     # cria o projeto
cd meubot
export TELEGRAM_TOKEN="123456:AAH..."   # o token vem do @BotFather
dataforge telegram doctor         # confere o que falta
dataforge telegram run            # sobe em long polling""", "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "O token nunca vai no código",
              "texto": "Ele vai para o Git, e do Git para qualquer um — e o @BotFather não avisa quando alguém o usa: o bot só começa a mandar spam. `Tg.segredo_do_ambiente()` lê de `$TELEGRAM_TOKEN` e falha dizendo o que fazer quando a variável está vazia."}},
 {"p": "O módulo também nunca deixa o token aparecer numa mensagem de erro. Ele está na URL de toda chamada, e a URL entra em todo traceback — um token num log de CI é um bot sequestrado."},

 {"h2": "O que chega em `ctx`"},
 {"table": {"head": ["", "O que é"], "rows": [
   ["`ctx.texto`", "o texto da mensagem, ou a legenda da mídia"],
   ["`ctx.args`", "o que veio depois do comando, já separado"],
   ["`ctx.dados`", "o `dados` do botão que foi clicado"],
   ["`ctx.chat`", "o id do chat"],
   ["`ctx.nome()` · `ctx.apelido()`", "quem falou"],
   ["`ctx.e_privado()` · `ctx.e_grupo()` · `ctx.e_admin()`", "onde, e com que poder"],
   ["`ctx.estado`", "o vault **deste chat**, que sobrevive entre mensagens"],
   ["`ctx.update`", "o update cru, para o campo que nenhuma conveniência cobre"]]}},
 {"p": "E para responder: `ctx.responder`, `ctx.citar` (que responde **citando**, o que dá contexto em grupo), `ctx.responder_foto`, `ctx.responder_documento`, `ctx.editar`, `ctx.apagar`, `ctx.digitando` e `ctx.avisar`."},

 {"h2": "O despacho para no primeiro que casa"},
 {"p": "O update é casado **uma vez**, na ordem do registro. A alternativa — entregar a todos — parece mais flexível e produz o bug mais confuso que um bot tem: duas respostas para uma mensagem, e ninguém sabe de onde veio a segunda."},
 {"code": """mark @app.comando("start")
action comecar(ctx):
    ctx.responder("Ola!")

mark @app.texto("\\\\b(oi|ola)\\\\b")
action cumprimento(ctx):
    ctx.responder("Oi!")

mark @app.qualquer()
action resto(ctx):
    ctx.responder("Nao entendi.")""", "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "`qualquer` vai por último — e isso é cobrado",
              "texto": "Ela casa com tudo. Uma rota registrada **depois** dela nunca seria alcançada, e o sintoma é o bot responder \"não entendi\" a um comando que existe. Registrar nessa ordem é **recusado**, na partida: é a mesma classe do `point` inalcançável que o `check` acusa na linguagem."}},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/telegram/comandos", "title": "Comandos e roteamento", "desc": "Comando, texto, botão, mídia, consulta inline e middleware."},
   {"href": "/docs/telegram/teclados", "title": "Teclados e formatação", "desc": "Botões, o teclado do celular, e o escape que salva a mensagem."},
   {"href": "/docs/telegram/conversas", "title": "Conversas e estado", "desc": "A máquina de estados por chat, e onde ela mora."},
   {"href": "/docs/telegram/testes", "title": "Testar sem rede", "desc": "A sonda injeta updates e lê o que o bot mandou."},
   {"href": "/docs/telegram/publicar", "title": "Publicar", "desc": "Webhook, HTTPS, e por que `deploy` não existe."}]},
 {"h2": "Além do básico"},
 {"p": "Mensagens longas, listas com páginas, o ritmo que o Telegram aceita, quem pode usar o quê, erros, arquitetura e receitas — cada bloco testado sem rede."},
 {"cards": [{"href": "/docs/telegram/mensagens-longas", "title": "Mensagens longas", "desc": "O limite de 4096 é em UTF-16, e não em caracteres: Tg.dividir corta onde o Telegram aceita."}, {"href": "/docs/telegram/paginacao", "title": "Listas com páginas", "desc": "Um teclado ◀ 2/5 ▶ que edita a mesma mensagem, e o callback velho que não quebra."}, {"href": "/docs/telegram/ritmo", "title": "Ritmo e limites do Telegram", "desc": "30 mensagens por segundo, 20 por minuto num grupo, e o 429 que bloqueia por minutos."}, {"href": "/docs/telegram/permissoes", "title": "Quem pode usar o quê", "desc": "Lista de permitidos, administradores de grupo e o gancho que barra antes do tratador."}, {"href": "/docs/telegram/erros", "title": "Quando o tratador falha", "desc": "ao_falhar, a mensagem que a pessoa vê, e o erro que vai para o log — nunca o contrário."}, {"href": "/docs/telegram/arquitetura", "title": "Um bot que cresce", "desc": "O bot como casca: a regra num módulo, o estado fora da memória, e o teste que não precisa do Telegram."}, {"href": "/docs/telegram/receitas", "title": "Receitas de bot", "desc": "Lembrete, enquete de um toque, menu de confirmação e resposta a documento — cada uma testada."}, {"href": "/docs/telegram/limites", "title": "Os limites da Bot API", "desc": "Tamanhos, arquivos, teclados e o que o módulo confere antes de o Telegram recusar."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/comandos",
"title": "Comandos e roteamento",
"description": "As sete formas de casar um update, o middleware e o tratador de erro.",
"blocos": [
 {"h2": "Comando"},
 {"code": """mark @app.comando("start", ajuda := "Comeca a conversa")
action comecar(ctx):
    ctx.responder("Ola!")

mark @app.comando(["ajuda", "help"])
action ajudar(ctx):
    ctx.responder("Mande /cadastro.")""", "lang": "df"},
 {"p": "Ele casa com `/nome`, com `/nome argumento` e com **`/nome@meubot`** — a última forma é a que o Telegram usa em grupo, e um bot que não a trata parece mudo lá dentro, funcionando em privado."},
 {"p": "O `ajuda` alimenta `app.publicar_comandos()`, que manda o menu ao Telegram. Sem o menu, a lista que aparece ao digitar `/` vem vazia, e um bot sem menu parece quebrado."},

 {"h2": "Texto, botão e mídia"},
 {"code": """mark @app.texto("^preco de (.+)$")
action preco(ctx):
    ctx.responder("Consultando…")

mark @app.botao("^comprar:(\\\\d+)$")
action comprar(ctx):
    ctx.avisar("Adicionado!")
    ctx.editar("Pedido atualizado.")

mark @app.midia("foto")
action recebeu_foto(ctx):
    ctx.responder("Foto recebida.")""", "lang": "df"},
 {"p": "O `texto` recebe uma expressão regular, ou nada para casar qualquer texto — e ele **nunca** casa uma mensagem que começa com `/`: um tratador de texto que engolisse comandos faria todo comando novo parar de funcionar."},
 {"callout": {"tipo": "atencao", "titulo": "`ctx.avisar()` é obrigatório num botão",
              "texto": "Sem ele, o Telegram deixa o botão com o relógio girando por até um minuto, e quem clicou conclui que o bot travou. Chame sempre, mesmo sem texto."}},
 {"p": "As espécies de mídia: `foto`, `documento`, `voz`, `video`, `audio`, `adesivo`, `local`, `contato`, `animacao` e `enquete`. Uma espécie que não existe é recusada na hora, listando as que existem."},

 {"h2": "Entrou, saiu, consulta inline"},
 {"code": """mark @app.entrou()
action boas_vindas(ctx):
    ctx.responder("Bem-vindo ao grupo!")

mark @app.inline()
action buscar(ctx):
    ctx.bot.responder_inline(ctx.consulta["id"], resultados_de(ctx.texto))""", "lang": "df"},

 {"h2": "Middleware"},
 {"code": """mark @app.antes_de_cada()
action so_assinantes(ctx):
    given not assinante(ctx.id_do_usuario()):
        ctx.responder("Isto e so para assinantes.")
        yield no        // 'no' interrompe: nenhum tratador roda

mark @app.depois_de_cada()
action registrar(ctx):
    Log.info($"{ctx.tipo} de {ctx.chat}")""", "lang": "df"},
 {"p": "Devolver `no` no `antes_de_cada` interrompe o update — é como se faz uma barreira sem espalhar um `given` por todos os tratadores."},

 {"h2": "Quando algo quebra"},
 {"code": """mark @app.ao_falhar()
action deu_errado(ctx, erro):
    out $"[bot] {erro}"
    ctx.responder("Alguma coisa quebrou aqui. Ja anotei.")""", "lang": "df"},
 {"p": "Um erro num tratador **não derruba o bot**: ele é anotado, o tratador de erro roda, e o próximo update é atendido. Um bot que morre porque alguém mandou um emoji inesperado é um bot que fica fora do ar de madrugada."},
 {"p": "Um tratador de erro que também falha não entra em laço: a linha para ali, e o bot segue vivo."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/teclados",
"title": "Teclados e formatação",
"description": "Botões embutidos, o teclado do celular, e o escape de MarkdownV2 que salva a mensagem inteira.",
"blocos": [
 {"h2": "Botões embutidos"},
 {"code": """ctx.responder("Confirma?", teclado := Tg.botoes([
    [Tg.botao("Sim", dados := "ok"), Tg.botao("Nao", dados := "cancelar")],
    [Tg.botao("Ver no site", url := "https://exemplo.dev")]
]))""", "lang": "df"},
 {"p": "O `dados` volta em `ctx.dados` quando alguém clica. `dados` e `url` no mesmo botão é um erro do Telegram — e ele recusa o teclado **inteiro** sem dizer qual botão é o culpado, então é melhor descobrir na chamada."},
 {"callout": {"tipo": "atencao", "titulo": "O `dados` tem 64 BYTES, não 64 caracteres",
              "texto": "O limite é do protocolo e conta bytes: um texto com acento estoura antes do que parece. Guarde o valor no estado do chat e mande só uma chave curta."}},

 {"h2": "O teclado do celular"},
 {"code": """ctx.responder("Escolha:", teclado := Tg.teclado([
    ["Consultar saldo", "Extrato"],
    ["Falar com alguem"]
], dica := "toque numa opcao"))

// e para tirar:
ctx.responder("Pronto.", teclado := Tg.remover_teclado())""", "lang": "df"},

 {"h2": "O escape que salva a mensagem"},
 {"p": "O MarkdownV2 do Telegram exige escapar dezoito caracteres, e a lista inclui o **ponto** e o **hífen** — ou seja, um preço e uma data. Um caractere sem escape faz o Telegram recusar a mensagem **inteira** com 400, e o texto que quebra costuma ser justamente o que veio do usuário: funciona em teste e falha em produção, com o nome de alguém."},
 {"code": """// errado: o '.' e o '-' derrubam a mensagem
ctx.responder("Total: R$ 1.099,90 - hoje", marcacao := "MarkdownV2")

// certo:
ctx.responder(Tg.escapar("Total: R$ 1.099,90 - hoje"),
              marcacao := "MarkdownV2")""", "lang": "df"},
 {"table": {"head": ["Função", "Sai como"], "rows": [
   ["`Tg.escapar(t)`", "o texto com os dezoito reservados escapados"],
   ["`Tg.negrito(t)`", "`*texto*` — já escapado por dentro"],
   ["`Tg.italico(t)` · `Tg.riscado(t)` · `Tg.spoiler(t)`", "as outras ênfases"],
   ["`Tg.codigo(t)`", "código em linha; só a crase é escapada"],
   ["`Tg.bloco(t, lang)`", "bloco de código com linguagem"],
   ["`Tg.link(t, url)` · `Tg.mencao(t, id)`", "link, e menção a uma pessoa"],
   ["`Tg.escapar_html(t)`", "para a marcação HTML, que exige só três trocas"]]}},
 {"p": "O `escapar_html` troca o `&` **primeiro**: na ordem contrária, `<` viraria `&amp;lt;` — o escape do escape."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/conversas",
"title": "Conversas e estado",
"description": "A máquina de estados por chat, a validação passo a passo, e onde o estado mora.",
"blocos": [
 {"p": "Guardar \"em que passo este chat está\" num vault solto é o que todo bot faz errado: funciona até o segundo usuário, os dois se misturam, e um bot reiniciado esquece todo mundo."},

 {"h2": "Uma conversa"},
 {"code": """action e_email(texto):
    yield "@" in texto and "." in texto

cadastro := app.conversa("cadastro", [
    {"pergunta": "Qual e o seu nome?", "guarda": "nome"},
    {"pergunta": "E o seu e-mail?", "guarda": "email",
     "valida": e_email, "erro": "Isso nao parece um e-mail."}
])

mark @cadastro.ao_terminar()
action terminou(ctx, respostas):
    salvar(respostas["nome"], respostas["email"])
    ctx.responder($"Pronto, {respostas['nome']}!")

mark @app.comando("cadastro")
action abrir(ctx):
    cadastro.comecar(ctx)""", "lang": "df"},
 {"p": "Cada passo pergunta, espera, valida e guarda. O estado fica **no chat**, então duas pessoas conversando ao mesmo tempo não se atrapalham."},
 {"callout": {"tipo": "dica", "titulo": "Um comando sempre escapa da conversa",
              "texto": "Qualquer mensagem que comece com `/` encerra a conversa aberta e cai no tratador do comando. Sem isso, quem se perde no meio de um cadastro não consegue nem mandar `/cancelar` — e a única saída vira bloquear o bot."}},

 {"h2": "O estado deste chat"},
 {"code": """mark @app.comando("lembrar")
action lembrar(ctx):
    ctx.guardar("ultima_busca", ctx.args[0] ?? "")
    ctx.responder($"Anotei: {ctx.lembrar('ultima_busca', 'nada')}")""", "lang": "df"},
 {"table": {"head": ["Onde", "Sobrevive a", "Quando usar"], "rows": [
   ["`Tg.estado_em_memoria()`", "nada — some ao reiniciar", "desenvolvimento, e bots sem memória"],
   ["`Tg.estado_em_arquivo(pasta)`", "o reinício do processo", "um bot só, num servidor só"]]}},
 {"p": "O nome do arquivo sai do id do chat, e ele é **conferido**: um id que chegasse com `../` escreveria fora da pasta. O id vem do Telegram e é sempre numérico — mas \"sempre\" é uma suposição sobre um sistema de terceiros, e é barato não depender dela."},
 {"code": """app := Tg.app(Tg.segredo_do_ambiente(),
              estado := Tg.estado_em_arquivo(".telegram/estado"))""", "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/midia",
"title": "Mídia, arquivos e grupos",
"description": "Enviar foto e documento, baixar o que chega, e administrar um grupo.",
"blocos": [
 {"h2": "Enviar"},
 {"code": """ctx.responder_foto("relatorio.png", "O gráfico de setembro")
ctx.responder_documento("fechamento.pdf", "Fechamento do mês")

// ou pelo bot, para outro chat:
app.bot.video(outro_chat, "clipe.mp4")
app.bot.enquete(ctx.chat, "Qual prefere?", ["A", "B"], anonima := no)""", "lang": "df"},
 {"p": "Um **`file_id`** ou uma **URL** vão como texto; só o que está em disco (ou em memória) sobe por multipart. Mandar tudo por multipart funcionaria — e reenviaria um arquivo que o Telegram já tem."},
 {"callout": {"tipo": "dica", "titulo": "Guarde o `file_id`",
              "texto": "Quando um arquivo só vai voltar ao Telegram, guardar o `file_id` que ele devolveu evita as duas chamadas do download e o upload de volta."}},

 {"h2": "\"Digitando…\""},
 {"code": """mark @app.comando("relatorio")
action relatorio(ctx):
    ctx.digitando()          // some em 5s, ou quando a mensagem chega
    dados := consulta_demorada()
    ctx.responder(resumo(dados))""", "lang": "df"},
 {"p": "Chamar antes de um trabalho demorado é a diferença entre um bot que parece travado e um que parece pensando."},

 {"h2": "Baixar"},
 {"code": """mark @app.midia("documento")
action recebeu(ctx):
    arquivo := ctx.mensagem["document"]
    caminho := app.bot.baixar(arquivo["file_id"], $"/tmp/{arquivo['file_name']}")
    ctx.responder($"Salvei em {caminho}")""", "lang": "df"},
 {"p": "São **duas** chamadas por baixo: `getFile` devolve um caminho temporário, e o download é num endereço diferente. Arquivos acima de 20 MB não podem ser baixados pela Bot API, e a mensagem diz isso."},

 {"h2": "Grupos"},
 {"table": {"head": ["", ""], "rows": [
   ["`bot.e_admin(chat, usuario)`", "a pergunta mais comum, já pronta"],
   ["`bot.banir` · `bot.desbanir` · `bot.silenciar`", "moderação"],
   ["`bot.fixar` · `bot.desafixar`", "mensagem fixada"],
   ["`bot.chat(id)` · `bot.membro(chat, id)`", "o que o Telegram sabe"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Em grupo, o bot só vê comandos — por padrão",
              "texto": "A privacidade vem **ligada** no @BotFather: o bot recebe apenas mensagens que começam com `/` ou que o citam. Em privado tudo funciona, e no grupo ele parece mudo. `dataforge telegram doctor` pergunta isso ao Telegram e diz como desligar."}},

 {"h2": "O que o módulo não embrulha"},
 {"code": """Tg.chamar(token, "setChatTitle",
          {"chat_id": -100123, "title": "Novo nome"})

// ou, com o bot aberto:
app.bot.chamar("setChatPhoto", {"chat_id": ctx.chat}, arquivos := {"photo": "logo.png"})""", "lang": "df"},
 {"p": "A Bot API cresce, e um módulo que só oferece o que ele conhece envelhece no dia seguinte. `chamar` é a porta para qualquer método, com o mesmo tratamento de erro e de limite de taxa."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/testes",
"title": "Testar um bot sem rede",
"description": "A sonda injeta updates e devolve o que o bot teria enviado — sem token, sem celular.",
"blocos": [
 {"p": "Um bot que só pode ser testado conversando com ele no celular **não tem teste**: não roda no CI, não repete, e não diz o que quebrou."},
 {"code": """adopt Arcane.Telegram as Tg
adopt Arcane.Test as T

action test_o_start_cumprimenta_pelo_nome():
    t := Tg.testar(meu_bot())
    t.comando("start")
    T.assert_true("Ana" in t.ultima())

action test_o_botao_edita_a_mensagem():
    t := Tg.testar(meu_bot())
    t.clicar("ajuda")
    T.assert_eq(t.quantas("answerCallbackQuery"), 1)""", "lang": "df"},

 {"h2": "O que a sonda faz"},
 {"table": {"head": ["Agir", "Perguntar"], "rows": [
   ["`t.mandar(texto)`", "`t.ultima()` — a última mensagem enviada"],
   ["`t.comando(nome, ...)`", "`t.respostas()` — todas elas"],
   ["`t.clicar(dados)`", "`t.disse(trecho)` — se alguma contém o trecho"],
   ["`t.enviar_foto()` · `t.enviar_documento()`", "`t.ultimo_teclado()`"],
   ["`t.consultar(texto)`", "`t.chamadas(metodo)` · `t.quantas(metodo)`"],
   ["`t.entrar()`", "`t.estado(chave)` · `t.falhou()` · `t.falhas()`"]]}},
 {"p": "O dublê aceita **qualquer** método que ele não conheça, anotando a chamada em vez de estourar um erro: um dublê que precisa acompanhar cada método novo do cliente envelhece no primeiro recurso acrescentado."},

 {"h2": "Testar uma conversa inteira"},
 {"code": """action test_o_cadastro_valida_o_email():
    t := Tg.testar(meu_bot())
    t.comando("cadastro")
    t.mandar("Ana")
    t.mandar("sem arroba")
    T.assert_true("invalido" in t.ultima())
    t.mandar("ana@exemplo.br")
    T.assert_true(t.disse("Pronto"))
    T.assert_eq(t.estado("__conversa__"), void)""", "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/publicar",
"title": "Publicar o bot",
"description": "Long polling contra webhook, o segredo do cabeçalho, e por que `deploy` não existe.",
"blocos": [
 {"h2": "Os dois modos"},
 {"table": {"head": ["", "Long polling", "Webhook"], "rows": [
   ["como", "o bot pergunta ao Telegram", "o Telegram chama o bot"],
   ["exige", "só saída para a internet", "HTTPS com certificado **válido**"],
   ["custo", "uma conexão aberta o tempo todo", "nada enquanto ninguém fala"],
   ["quando", "desenvolvimento, e bots pequenos", "produção"]]}},
 {"p": "Os dois passam pelo **mesmo caminho** por dentro: `atender` recebe um update e não sabe de onde ele veio. Sem isso, um bot testado em polling quebra ao virar webhook — que é justamente quando ele vai para produção."},

 {"h2": "Webhook"},
 {"code": """app.publicar("https://bot.seudominio.dev",
             porta := 8443,
             segredo := Tg.segredo_do_ambiente("WEBHOOK_SEGREDO"))""", "lang": "df"},
 {"p": "Ou em dois passos, quando o servidor já existe: `dataforge telegram webhook https://bot.seudominio.dev` registra, e `app.montar(\"/telegram\", segredo)` devolve um app Kiln para você montar onde quiser."},
 {"callout": {"tipo": "atencao", "titulo": "Use o segredo",
              "texto": "Sem ele, qualquer um que descubra a URL manda updates falsos para o seu bot — e a URL vaza em log de proxy, em print de tela, em qualquer lugar. O módulo confere o cabeçalho `X-Telegram-Bot-Api-Secret-Token` e responde 403 quando não bate."}},
 {"p": "O webhook responde **200 sempre**, mesmo quando o tratador falha: o Telegram reenvia o update quando a resposta demora ou dá erro, e isso faria o mesmo comando rodar três vezes."},

 {"h2": "Quando o bot fica calado"},
 {"code": """dataforge telegram doctor""", "lang": "bash"},
 {"p": "Um bot que não responde não dá erro — ele simplesmente fica calado, e as causas são sempre as mesmas:"},
 {"table": {"head": ["O que o doctor pergunta", "O que costuma ser"], "rows": [
   ["o Telegram aceita o token?", "token revogado, ou com espaço em volta"],
   ["há webhook registrado?", "ele e o polling **não convivem** — o `getUpdates` responde 409 para sempre"],
   ["o bot lê tudo em grupo?", "a privacidade vem ligada: ele só vê `/comandos` e menções"],
   ["o bot entra em grupos?", "`/setjoingroups` no @BotFather"],
   ["quantos updates estão na fila?", "o servidor do webhook não está respondendo 200"]]}},

 {"h2": "Ritmo"},
 {"code": """app := Tg.app(Tg.segredo_do_ambiente(),
              limitador := Tg.limitar(por_segundo := 25,
                                      por_chat_por_minuto := 18))""", "lang": "df"},
 {"p": "O Telegram corta acima de ~30 mensagens por segundo, e num grupo o limite é de cerca de 20 por minuto. Segurar aqui custa milissegundos; ser bloqueado custa minutos — e o `retry_after` que ele devolve é obedecido ao pé da letra, porque repetir antes dele só gasta a cota."},

 {"h2": "`deploy` não existe — de propósito"},
 {"p": "Registrar o webhook é do bot, e isso existe. **Onde** essa URL vai morar — Docker, systemd, uma PaaS, um túnel — é uma opinião sobre infraestrutura que o projeto não tem, pelo mesmo motivo que `dataforge vitrine deploy` não existe."},
 {"code": """dataforge devops docker --porta=8443     # o Dockerfile
dataforge telegram doctor                # o que falta
GET <caminho>/saude                      # métricas e erros""", "lang": "bash"},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/telegram", "title": "Visão geral", "desc": "O bot inteiro em oito linhas."},
   {"href": "/docs/telegram/testes", "title": "Testar sem rede", "desc": "A sonda injeta updates e lê as respostas."},
   {"href": "/docs/devops", "title": "DevOps", "desc": "Dockerfile, compose, CI e manifestos."},
   {"href": "/docs/kiln", "title": "Kiln", "desc": "O servidor HTTP que atende o webhook."}]},
]},
]
