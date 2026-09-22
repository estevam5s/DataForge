# -*- coding: utf-8 -*-
"""Telegram — oito páginas além do básico.

Todo bloco roda com `Tg.testar`, sem token e sem rede. Escrevendo-as
apareceu um defeito da linguagem: `mark @app.texto()` com parênteses
vazios chamava `app.texto(acao)`, e o bot ficava calado. Hoje `@f()` é
fábrica, como em toda linguagem com decorador.
"""

_BOT = '''adopt Arcane.Telegram as Tg

app := Tg.app("123456:TESTE-exemplo")
'''

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/mensagens-longas",
"title": "Mensagens longas",
"description": "O limite de 4096 é em UTF-16, e não em caracteres: Tg.dividir corta onde o Telegram aceita.",
"blocos": [
 {"p": "Uma mensagem do Telegram tem no máximo **4096** unidades; uma legenda de foto, **1024**. Passar disso não corta a mensagem: o Telegram a **recusa inteira** com `message is too long`, e o relatório que o bot ia mandar simplesmente não chega."},
 {"p": "E a conta é em unidades **UTF-16**, não em caracteres. Um emoji — quase todos estão fora do plano básico — vale **dois**. Uma mensagem de 4000 caracteres com 200 emojis passa de 4096 e é recusada, embora `len` diga 4000."},
 {"code": _BOT + '''
relatorio := ("linha do relatório com 📦\\n" * 300)

mark @app.comando("relatorio")
action enviar_relatorio(ctx):
    cycle parte in Tg.dividir(relatorio):
        ctx.responder(parte)

t := Tg.testar(app)
t.comando("relatorio")
assert t.quantas("sendMessage") bigger 1
assert "".join(t.respostas()).replace("\\n", "") is relatorio.replace("\\n", "")''', "lang": "df"},
 {"h2": "Onde ele corta"},
 {"table": {"head": ["Preferência", "Por quê"], "rows": [
   ["1. parágrafo (`\\n\\n`)", "o leitor não percebe a quebra"],
   ["2. linha", "uma linha de tabela não fica pela metade"],
   ["3. espaço", "uma palavra não se parte"],
   ["4. no meio", "só quando uma \"palavra\" passa do limite sozinha"]]}},
 {"p": "E um escape do MarkdownV2 nunca é separado da barra: um pedaço terminando em `\\\\` e o seguinte começando em `.` são **duas** mensagens recusadas por marcação inválida."},
 {"code": '''adopt Arcane.Telegram as Tg

legenda := Tg.dividir("Legenda muito longa " * 80, 1024)
assert len(legenda) bigger 1
cycle p in legenda:
    assert len(p) smaller_eq 1024''', "lang": "df"},
 {"callout": {"tipo": "dica", "titulo": "Mais de 20 mensagens?", "texto": "Um relatório que vira vinte mensagens já não é uma mensagem. Mande um **arquivo**: `ctx.responder_documento(\"relatorio.csv\")` — ele chega inteiro, e a pessoa abre na planilha."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/paginacao",
"title": "Listas com páginas",
"description": "Um teclado ◀ 2/5 ▶ que edita a mesma mensagem, e o callback velho que não quebra.",
"blocos": [
 {"p": "Uma lista de cem produtos não cabe numa mensagem, e mandar vinte mensagens enterra a conversa. O padrão é **uma** mensagem com um teclado de navegação que a **edita** a cada clique."},
 {"code": _BOT + '''
produtos := [$"Produto {i}" cycle i in range(1, 13)]

action mostrar(numero):
    yield Tg.paginado(produtos, numero, 5, "prod")

mark @app.comando("catalogo")
action catalogo(ctx):
    p := mostrar(1)
    ctx.responder(p["itens"].join("\\n"), teclado := p["teclado"])

mark @app.botao("^prod:")
action virar(ctx):
    p := mostrar(Tg.ler_pagina(ctx.dados, "prod"))
    ctx.editar(p["itens"].join("\\n"), teclado := p["teclado"])

t := Tg.testar(app)
t.comando("catalogo")
assert t.ultima().starts_with("Produto 1")
assert t.ultimo_teclado()["inline_keyboard"][0][-1]["callback_data"] is "prod:2"

t.clicar("prod:3")
editada := t.chamadas("editMessageText")[-1]
assert editada["texto"].starts_with("Produto 11")''', "lang": "df"},
 {"h2": "Três detalhes"},
 {"list": [
   "**Editar, e não mandar de novo.** `ctx.editar` troca a mensagem que tinha o teclado; mandar outra deixaria cinco teclados vivos na conversa, cada um mostrando outra página.",
   "**O callback velho não quebra.** A lista pode encolher entre o envio do teclado e o clique: `paginado` limita a página ao que existe, e o clique em `prod:9` mostra a última.",
   "**O prefixo separa os teclados.** O mesmo bot tem vários; `Tg.ler_pagina(\"menu:2\", \"prod\")` é `void`, e não a página 2 de outra lista."]},
 {"callout": {"tipo": "atencao", "titulo": "64 bytes por botão", "texto": "O `dados` de um botão tem no máximo 64 **bytes**. Por isso ele leva só a página (`prod:3`), e nunca o filtro, a busca ou o item inteiro: guarde isso em `ctx.estado` e mande só a chave."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/ritmo",
"title": "Ritmo e limites do Telegram",
"description": "30 mensagens por segundo, 20 por minuto num grupo, e o 429 que bloqueia por minutos.",
"blocos": [
 {"p": "O Telegram corta o bot que envia rápido demais, e o corte não é uma mensagem perdida: é um **429** com `retry_after` que pode passar de um minuto, e nesse intervalo o bot não responde **ninguém**."},
 {"table": {"head": ["Limite", "Aproximado", "O que estoura"], "rows": [
   ["mensagens no total", "~30 por segundo", "um aviso para todos os assinantes num laço"],
   ["num mesmo grupo", "~20 por minuto", "um bot que responde toda mensagem de um grupo ativo"],
   ["num mesmo chat privado", "~1 por segundo", "uma resposta dividida em vinte partes"]]}},
 {"p": "`Tg.limitar` segura o ritmo **antes** de enviar — esperar alguns milissegundos custa menos que ser bloqueado por minutos:"},
 {"code": '''adopt Arcane.Telegram as Tg

lim := Tg.limitar(50, 18)             // até 50 por segundo, e 18 por minuto por chat
inicio := time()
cycle i in range(10):
    lim.esperar(1001)
decorrido := time() - inicio
assert decorrido bigger_eq 0.15       // dez envios a 50/s: ao menos 180 ms''', "lang": "df"},
 {"h2": "Aviso para todos os assinantes"},
 {"p": "O caso que mais estoura é o *broadcast*: mil assinantes num laço sem pausa. Com o limitador, o laço leva o tempo que o Telegram aceita — e numa [fila](/docs/biblioteca/eventos), ele não segura o tratador que disparou o aviso."},
 {"code": _BOT + '''
assinantes := [1001, 1002, 1003]
lim := Tg.limitar(25, 18)

action avisar_todos(texto):
    cycle chat in assinantes:
        lim.esperar(chat)
        app.bot.enviar(chat, texto)

t := Tg.testar(app)
avisar_todos("Manutenção às 22h.")
assert t.quantas("sendMessage") is 3''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O bloqueio pelo usuário", "texto": "Quem bloqueia o bot faz todo envio a ele falhar com **403**. No broadcast, isso não é erro do bot: anote e tire o chat da lista, senão cada aviso futuro gasta uma chamada — e o ritmo — num chat que nunca vai receber."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/permissoes",
"title": "Quem pode usar o quê",
"description": "Lista de permitidos, administradores de grupo e o gancho que barra antes do tratador.",
"blocos": [
 {"p": "Um bot é público: **qualquer pessoa** que achar o nome dele pode mandar `/apagar_tudo`. A pergunta \"quem pode?\" precisa de resposta em todo comando que muda algo — e a forma de não esquecê-la em nenhum é respondê-la **num lugar só**."},
 {"code": _BOT + '''
steady ADMINS := [42]

mark @app.antes_de_cada()
action barrar(ctx):
    publicos := ["/start", "/ajuda"]
    given (ctx.texto ?? "") in publicos or ctx.id_do_usuario() in ADMINS:
        yield yes
    ctx.responder("Este bot é de uso interno.")
    yield no                               // 'no' interrompe o update

mark @app.comando("apagar_tudo")
action apagar_tudo(ctx):
    ctx.responder("Apagado.")

admin := Tg.testar(app)
admin.comando("apagar_tudo")
assert admin.ultima() is "Apagado."

estranho := Tg.testar(app, 2002, {"id": 7, "first_name": "Zé"})
estranho.comando("apagar_tudo")
assert estranho.ultima() is "Este bot é de uso interno."''', "lang": "df"},
 {"h2": "Em grupo: quem administra"},
 {"p": "Num grupo, a pergunta costuma ser \"quem fala é administrador deste grupo?\". `ctx.e_admin()` pergunta ao Telegram — e em conversa privada é sempre `yes`, porque ali a pessoa administra a própria conversa:"},
 {"code": _BOT + '''
mark @app.comando("fixar")
action fixar(ctx):
    given not ctx.e_admin():
        ctx.responder("Só administradores fixam mensagens.")
        yield void
    ctx.responder("Fixada.")

t := Tg.testar(app, -100123)            // id negativo: um grupo
t.comando("fixar")
assert t.ultima() is "Só administradores fixam mensagens."''', "lang": "df"},
 {"callout": {"tipo": "perigo", "titulo": "Nunca confie no nome", "texto": "`username` e `first_name` são escolhidos pela pessoa e mudam quando ela quiser. A lista de permitidos é de **ids** numéricos — `ctx.id_do_usuario()` —, que o Telegram garante."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/erros",
"title": "Quando o tratador falha",
"description": "ao_falhar, a mensagem que a pessoa vê, e o erro que vai para o log — nunca o contrário.",
"blocos": [
 {"p": "Um tratador que levanta, sem nada por cima, deixa a pessoa esperando uma resposta que não vem. `app.ao_falhar` é o tratador do erro: ele recebe o contexto **e** o erro, responde algo útil a quem estava falando, e anota o resto."},
 {"code": _BOT + '''
anotados := []

mark @app.comando("dividir")
action dividir(ctx):
    partes := ctx.texto.split(" ")
    ctx.responder($"{int(partes[1]) / int(partes[2])}")

mark @app.ao_falhar()
action falhou(ctx, erro):
    anotados.append(erro)
    ctx.responder("Não consegui fazer essa conta. Tente: /dividir 10 2")

t := Tg.testar(app)
t.comando("dividir", "10", "0")
assert t.ultima().starts_with("Não consegui")
assert len(anotados) is 1 and t.falhou()

t.comando("dividir", "10", "2")
assert t.ultima() is "5.0"''', "lang": "df"},
 {"table": {"head": ["Vai para a pessoa", "Vai para o log"], "rows": [
   ["o que ela pode fazer (\"tente /dividir 10 2\")", "o erro inteiro, com a linha"],
   ["que algo falhou, sem culpá-la", "o id do chat e o texto que chegou"],
   ["nunca: mensagem do banco, caminho de arquivo, token", "o token **mascarado**, se aparecer"]]}},
 {"callout": {"tipo": "dica", "titulo": "Nos testes, `t.falhou()`", "texto": "O `ao_falhar` faz o bot parecer bem-comportado — e esconde a falha do teste. Confira `t.falhou()` e `t.falhas()`: um teste que só olha a resposta gentil passa com o tratador quebrado."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/arquitetura",
"title": "Um bot que cresce",
"description": "O bot como casca: a regra num módulo, o estado fora da memória, e o teste que não precisa do Telegram.",
"blocos": [
 {"p": "O primeiro bot é um arquivo só, e está certo assim. O segundo mês traz um banco, três tipos de usuário e um relatório — e aí o arquivo único mistura **o que o bot faz** com **como o Telegram recebe**, e nenhum dos dois se testa sozinho."},
 {"table": {"head": ["Camada", "Sabe de", "Não sabe de"], "rows": [
   ["o **núcleo** (`pedidos.df`)", "a regra: o que é um pedido válido, o total, o estado", "Telegram, `ctx`, teclado"],
   ["o **bot** (`bot.df`)", "comandos, teclados, a conversa", "como se calcula o total"],
   ["o **estado**", "onde a conversa mora entre mensagens", "o que ela significa"]]}},
 {"code": _BOT + '''
// o núcleo: nada aqui sabe que existe um Telegram
action total(itens):
    yield itens >> distill acc, i: acc + i["preco"] * i["qtd"] 0

// a casca: traduz mensagem em chamada, e resultado em texto
mark @app.comando("total")
action comando_total(ctx):
    carrinho := ctx.lembrar("carrinho", [])
    ctx.responder($"Total: R$ {total(carrinho)}")

mark @app.comando("pegar")
action pegar(ctx):
    carrinho := ctx.lembrar("carrinho", [])
    carrinho.append({"preco": 10, "qtd": 2})
    ctx.guardar("carrinho", carrinho)
    ctx.responder("Adicionado.")

assert total([{"preco": 10, "qtd": 3}]) is 30   // o núcleo, sem bot

t := Tg.testar(app)
t.comando("pegar")
t.comando("total")
assert t.ultima() is "Total: R$ 20"''', "lang": "df"},
 {"h2": "O estado fora da memória"},
 {"p": "`Tg.estado_em_memoria()` some quando o processo reinicia — e o bot reinicia a cada deploy. Para produção, `Tg.estado_em_arquivo(caminho)`, e o carrinho de quem estava no meio de uma compra sobrevive à atualização."},
 {"p": "O projeto completo nesse formato está em [Bot de atendimento](/docs/projetos/bot-atendimento)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/receitas",
"title": "Receitas de bot",
"description": "Lembrete, enquete de um toque, menu de confirmação e resposta a documento — cada uma testada.",
"blocos": [
 {"h2": "Confirmar antes de agir"},
 {"code": _BOT + '''
mark @app.comando("cancelar_pedido")
action pedir_confirmacao(ctx):
    ctx.responder("Cancelar o pedido 77?", teclado := Tg.botoes([[
        Tg.botao("Sim, cancelar", dados := "cancelar:77:sim"),
        Tg.botao("Não", dados := "cancelar:77:nao")]]))

mark @app.botao("^cancelar:")
action decidir(ctx):
    partes := ctx.dados.split(":")
    ctx.editar("Pedido cancelado." given partes[2] is "sim" otherwise "Nada foi feito.")

t := Tg.testar(app)
t.comando("cancelar_pedido")
t.clicar("cancelar:77:nao")
assert t.chamadas("editMessageText")[-1]["texto"] is "Nada foi feito."''', "lang": "df"},
 {"h2": "Enquete de um toque"},
 {"code": _BOT + '''
votos := {"sim": 0, "nao": 0}

mark @app.comando("enquete")
action enquete(ctx):
    ctx.responder("Almoço às 12h?", teclado := Tg.botoes([[
        Tg.botao("👍", dados := "voto:sim"), Tg.botao("👎", dados := "voto:nao")]]))

mark @app.botao("^voto:")
action votar(ctx):
    escolha := ctx.dados.split(":")[1]
    votos[escolha] += 1
    ctx.editar($"Almoço às 12h?  👍 {votos["sim"]}  👎 {votos["nao"]}")

t := Tg.testar(app)
t.comando("enquete")
t.clicar("voto:sim")
t.clicar("voto:sim")
assert votos["sim"] is 2''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um voto por pessoa", "texto": "A enquete acima conta dois cliques da mesma pessoa. Para um voto por pessoa, guarde `ctx.id_do_usuario()` num conjunto — `{…}` — e confira antes de somar. E duas pessoas clicando ao mesmo tempo escrevem no mesmo vault: com o bot atendendo em threads, use um [ator](/docs/concorrencia/atores)."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/telegram/limites",
"title": "Os limites da Bot API",
"description": "Tamanhos, arquivos, teclados e o que o módulo confere antes de o Telegram recusar.",
"blocos": [
 {"p": "Quase toda recusa do Telegram é um limite que se sabe de antemão. Conferir antes troca um `400 Bad Request` genérico, que não diz qual campo estourou, por uma mensagem com o nome do campo."},
 {"table": {"head": ["O quê", "Limite", "Quem confere"], "rows": [
   ["texto de mensagem", "4096 unidades UTF-16", "`Tg.dividir`"],
   ["legenda de mídia", "1024 unidades UTF-16", "`Tg.dividir(texto, 1024)`"],
   ["`dados` de um botão", "64 **bytes**", "`Tg.botao` — recusa na hora"],
   ["`dados` e `url` no mesmo botão", "não pode", "`Tg.botao` — recusa na hora"],
   ["arquivo enviado pelo bot", "50 MB", "o Telegram"],
   ["arquivo baixado pelo bot", "20 MB", "o Telegram"],
   ["comandos no menu", "100, de até 32 caracteres", "`app.publicar_comandos`"]]}},
 {"code": '''adopt Arcane.Telegram as Tg

monitor:
    Tg.botao("Ver", dados := "detalhe:" + "ç" * 40)
handle Error as e:
    assert e.message.contains("64 bytes")        // quarenta 'ç' são 80 bytes''', "lang": "df"},
]},
]
