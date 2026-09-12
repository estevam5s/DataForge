# -*- coding: utf-8 -*-
"""Kiln — upload, tempo real; e Crucible — cobertura e instantâneos."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/kiln/uploads",
"title": "Receber arquivos",
"description": "multipart/form-data, e as três recusas que separam um upload de uma porta aberta.",
"blocos": [
 {"p": "O corpo de um pedido é interpretado pelo `Content-Type`. Com `multipart/form-data`, os campos comuns vão para `req[\"body\"]` e os arquivos para `req[\"files\"]`."},
 {"code": """adopt Kiln

server importador on 8080:
    route POST "/importar":
        arquivo := Kiln.upload(req, "planilha")
        given arquivo is void:
            respond 400 json {"erro": "nenhum arquivo em 'planilha'"}

        linhas := arquivo["texto"].lines() >> sift l: l.trim() is not ""
        gravado := Kiln.salvar_upload(arquivo, "envios",
                                      tipos := [".csv", ".xlsx"],
                                      limite := 5242880)
        respond json {
            "titulo": req["body"]["titulo"] ?? "",
            "linhas": len(linhas),
            "em": gravado["caminho"]
        }""", "lang": "df"},

 {"h2": "O que chega"},
 {"table": {"head": ["Chamada", "Devolve"], "rows": [
   ["`Kiln.upload(req, campo)`", "o vault de um arquivo, ou `void`"],
   ["`Kiln.uploads(req)`", "todos, por nome de campo"],
   ["`req[\"body\"]`", "os campos comuns, como num formulário qualquer"],
   ["`req[\"files\"]`", "o mesmo que `Kiln.uploads(req)`"]]}},
 {"code": """{
    "nome":     "vendas.csv",        // já sem o caminho do cliente
    "tipo":     "text/csv",
    "tamanho":  1284,
    "conteudo": <bytes>,
    "texto":    "id,valor\\n1,10\\n…"
}""", "lang": "text"},
 {"p": "Campos e arquivos ficam **separados** de propósito: quem escreve lê `body[\"titulo\"]` sem saber se o formulário tinha arquivo, e um `cycle` sobre `body` não topa com bytes onde espera texto."},
 {"callout": {"tipo": "nota", "titulo": "Campo repetido vira cluster", "texto": "`tags=a&tags=b` chega como `[\"a\", \"b\"]`, e não como `\"b\"`. É assim que um `<select multiple>` e uma lista de caixas de marcar chegam — o último valor sozinho perderia os outros."}},
 {"p": "O caminho que o cliente manda é descartado: o IE mandava `C:\\Users\\ana\\foto.jpg`, e um navegador hostil manda o que quiser. Fica só `foto.jpg`."},

 {"h2": "Gravar"},
 {"code": """gravado := Kiln.salvar_upload(arquivo, "envios",
                              tipos := [".csv", ".xlsx"],
                              limite := 5242880)
// {"caminho": "envios/a3f91c2e4b08.csv",
//  "nome": "a3f91c2e4b08.csv",
//  "nome_original": "vendas.csv",
//  "tamanho": 1284}""", "lang": "df"},
 {"table": {"head": ["Recusa", "Por quê"], "rows": [
   ["nome com `/`, `\\` ou `..`", "`../../.ssh/authorized_keys` escreve **fora** da pasta de destino"],
   ["acima do `limite`", "um upload de 4 GB enche o disco"],
   ["extensão fora de `tipos`", "`.php` numa pasta servida como estática é execução remota"]]}},
 {"p": "E o nome final **nunca** é o que o cliente mandou: leva um prefixo aleatório. Dois usuários enviando `foto.jpg` não podem sobrescrever um ao outro, e um nome escolhido por quem envia é um nome que ele pode adivinhar depois. `nome_original` volta no resultado, para guardar no banco e mostrar ao usuário."},
 {"callout": {"tipo": "atencao", "titulo": "Recusar, e não sanear", "texto": "`basename(\"../../x\")` devolve `x`, e a travessia fica neutralizada. Mas um cliente que manda `../../.ssh/authorized_keys` está quebrado ou é hostil, e aceitar como `authorized_keys` **esconde isso de quem lê o log**."}},

 {"h2": "Dois limites, e eles são diferentes"},
 {"code": """Kiln.config(app, "limite_corpo", 20971520)     // 20 MB — o do PEDIDO
Kiln.salvar_upload(arquivo, pasta, limite := 5242880)  // 5 MB — o do ARQUIVO""", "lang": "df"},
 {"p": "O limite do pedido é verificado **antes** de o corpo ser lido na memória: um POST maior é recusado com 413 sem chegar à rota. Sem ele, um POST de 2 GB derruba o processo sem exploit nenhum. O padrão é 10 MB."},
 {"p": "O do arquivo é por arquivo, depois de o corpo estar lido. Aumentar um sem o outro não funciona."},

 {"h2": "Vários arquivos"},
 {"code": """route POST "/galeria":
    arquivos := Kiln.uploads(req)
    salvos := []
    cycle nome, arquivo in arquivos:
        salvos.append(Kiln.salvar_upload(arquivo, "fotos",
                                         tipos := [".jpg", ".png", ".webp"]))
    respond json {"salvos": len(salvos)}""", "lang": "df"},

 {"h2": "Testar sem navegador"},
 {"p": "`Kiln.test` aceita o corpo cru — basta montar o `multipart`, que é o que o [exercício 223](/docs/exercicios/30-tempo-real) faz:"},
 {"code": """corpo := "--X\\r\\n" +
         "Content-Disposition: form-data; name=\\"titulo\\"\\r\\n\\r\\n" +
         "Vendas\\r\\n" +
         "--X\\r\\n" +
         "Content-Disposition: form-data; name=\\"planilha\\"; " +
         "filename=\\"v.csv\\"\\r\\nContent-Type: text/csv\\r\\n\\r\\n" +
         "id,valor\\n1,10\\n\\r\\n" +
         "--X--\\r\\n"

r := Kiln.test(app, "POST", "/importar", corpo,
               {"content-type": "multipart/form-data; boundary=X"})
assert r["status"] is 200""", "lang": "df"},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/kiln/tempo-real", "title": "Tempo real", "meta": "SSE e WebSocket", "desc": "O servidor empurrando, e as duas vias."},
   {"href": "/docs/kiln/middleware", "title": "Middleware", "desc": "CORS, limite de taxa, CSRF e cabeçalhos."},
   {"href": "/docs/exercicios/30-tempo-real", "title": "O exercício", "desc": "Upload testado ponta a ponta, sem navegador."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/kiln/tempo-real",
"title": "Tempo real",
"description": "SSE para o servidor empurrar, WebSocket para os dois falarem, e stream para o arquivo grande.",
"blocos": [
 {"p": "Três mecanismos, e a escolha entre eles é quase sempre óbvia."},
 {"table": {"head": ["Precisa", "Use", "Por quê"], "rows": [
   ["o servidor avisa, o cliente só ouve", "**SSE**", "HTTP comum, reconecta sozinho, passa em qualquer proxy"],
   ["os dois falam", "**WebSocket**", "duas vias, quadro binário"],
   ["um arquivo grande sem carregar na memória", "**`Kiln.stream`**", "cada pedaço sai enquanto o próximo é calculado"]]}},
 {"callout": {"tipo": "dica", "titulo": "SSE primeiro, sempre que servir", "texto": "Ele é HTTP comum: um proxy velho no caminho não o quebra, e o navegador reconecta sem uma linha de código. WebSocket entra quando o cliente também precisa falar."}},

 {"h2": "SSE — o servidor empurra"},
 {"code": """adopt Kiln

action progresso(fluxo):
    total := 200
    cycle i from 1 to total:
        given not fluxo.aberto:
            halt
        importar_linha(i)
        given i % 10 is 0:
            fluxo.enviar({"feitos": i, "total": total}, tipo := "progresso")
    fluxo.enviar({"ok": yes}, tipo := "fim")

server importador on 8080:
    route GET "/importacao":
        respond Kiln.sse(progresso)""", "lang": "df"},
 {"p": "No cliente, quatro linhas:"},
 {"code": """const fonte = new EventSource('/importacao');

fonte.addEventListener('progresso', e => {
  const d = JSON.parse(e.data);
  barra.style.width = (d.feitos / d.total * 100) + '%';
});
fonte.addEventListener('fim', () => fonte.close());""", "lang": "javascript"},
 {"table": {"head": ["Método do fluxo", "Faz"], "rows": [
   ["`fluxo.enviar(dados, tipo, identificador)`", "um evento; `no` se o cliente já foi"],
   ["`fluxo.escrever(texto)`", "um pedaço cru, sem formato de evento"],
   ["`fluxo.comentario()`", "o batimento que mantém a conexão viva"],
   ["`fluxo.aberto`", "`no` quando o cliente fechou a aba"],
   ["`fluxo.enviados`", "quantos eventos saíram"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Confira `fluxo.aberto` no laço", "texto": "Sem isso, um painel fechado deixa uma thread empurrando dado para ninguém, para sempre. `enviar` devolve `no` quando o cliente foi embora — e é por isso que ele devolve algo."}},
 {"p": "`fluxo.comentario()` a cada 15 segundos evita que proxy e balanceador fechem a conexão ociosa — eles fecham tipicamente em 30 a 60. O navegador ignora o comentário."},
 {"p": "A resposta já sai com `Cache-Control: no-cache`, `Connection: keep-alive` e `X-Accel-Buffering: no`. O último importa: o nginx guarda resposta em buffer por padrão, e com isso o evento só chegaria quando o buffer enchesse — o que destrói o SSE."},

 {"h3": "O formato, se você quiser montá-lo"},
 {"code": """Kiln.evento({"n": 1}, tipo := "tick", identificador := "7")
// "id: 7\\nevent: tick\\ndata: {\\"n\\": 1}\\n\\n\"""", "lang": "df"},
 {"p": "O `\\n\\n` final não é enfeite: é ele que diz ao navegador que o evento acabou. E um texto com `\\n` dentro leva um `data:` por linha — senão o evento quebraria no meio."},

 {"h2": "`Kiln.stream` — o arquivo grande"},
 {"code": """action exportar(fluxo):
    fluxo.escrever("id,valor,mes\\n")
    cycle linha in Banco.query(db, "SELECT id, valor, mes FROM vendas"):
        fluxo.escrever($"{linha["id"]},{linha["valor"]},{linha["mes"]}\\n")

route GET "/export.csv":
    respond Kiln.stream(exportar, "text/csv")""", "lang": "df"},
 {"p": "Um milhão de linhas sem montar o arquivo na memória. O mesmo mecanismo do SSE, sem o formato de evento."},

 {"h2": "WebSocket"},
 {"code": """sala := Kiln.sala("chat")

action chat(req, ws):
    quem := req["session"]["usuario"] ?? ws.id
    sala.entrar(ws)
    sala.transmitir({"entrou": quem, "agora": sala.quantos()}, exceto := ws)

    persist ws.aberto:
        msg := ws.receber(prazo := 60)
        given msg is void or msg is "sair":
            halt
        sala.transmitir({"de": quem, "texto": msg})

    sala.sair(ws)
    sala.transmitir({"saiu": quem, "agora": sala.quantos()})

server app on 8080:
    route GET "/chat":
        render "chat"

Kiln.ws(app, "/ws", chat)
Kiln.ignite(app, 8080)""", "lang": "df"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`ws.enviar(x)`", "texto, ou qualquer valor — que vira JSON"],
   ["`ws.enviar_json(v)`", "o mesmo, explícito"],
   ["`ws.receber(prazo := n)`", "a próxima mensagem, ou `void` se a conexão acabou"],
   ["`ws.receber_json()`", "já interpretada; `void` se não for JSON"],
   ["`ws.ping()`", "um ping"],
   ["`ws.fechar(codigo, motivo)`", "fecha com aperto de mão"],
   ["`ws.aberto` · `ws.id`", "estado e identidade"],
   ["`ws.recebidos` · `ws.enviados`", "contagem"]]}},

 {"h3": "A sala"},
 {"code": """sala.entrar(ws)                              // devolve quantos
sala.sair(ws)
sala.quantos()
sala.transmitir(mensagem, exceto := ws)      // devolve para quantos chegou
sala.fechar_todos("servidor encerrando")""", "lang": "df"},
 {"p": "Um soquete morto é **removido** em vez de levantar: um cliente que fechou a aba não pode derrubar a mensagem dos outros. E a trava protege a lista — duas threads entrando e saindo ao mesmo tempo é o caso normal, não a exceção."},

 {"h3": "O método `WS`"},
 {"p": "A rota de WebSocket usa o método `WS`, que **não existe em HTTP**. Duas consequências boas: ela não pode ser alcançada por um GET comum, e um `GET /ws` continua livre para servir a página que abre a conexão."},

 {"h3": "Detalhes do protocolo que você não precisa conhecer"},
 {"table": {"head": ["O quê", "Quem trata"], "rows": [
   ["o handshake (`Sec-WebSocket-Accept`)", "o Kiln"],
   ["ping e pong", "dentro do `receber` — obrigar a tratar isso seria obrigar a conhecer o RFC"],
   ["máscara do cliente", "o Kiln (o servidor nunca mascara)"],
   ["mensagem partida em vários quadros", "juntada antes de chegar a você"],
   ["`recv` devolvendo menos bytes do que se pediu", "o leitor insiste até completar"],
   ["um quadro que anuncia 8 exabytes", "recusado com o código 1009"]]}},
 {"callout": {"tipo": "dica", "titulo": "Feche com aperto de mão", "texto": "`ws.fechar(1000, \"fim\")` faz o navegador saber que acabou. Cortar o socket faria o `onerror` disparar do outro lado, e quem escreveu o cliente vai procurar um bug que não existe."}},

 {"h2": "Testar"},
 {"p": "`Kiln.test` **não serve** para SSE nem WebSocket: ele roda tudo numa thread e não abre socket. Para esses dois é preciso um cliente do outro lado."},
 {"code": """porta := Kiln.serve(app, 0)        // segundo plano; devolve a porta

r := Web.get($"http://127.0.0.1:{porta}/importacao")
assert "event: progresso" in r["body"]

Kiln.stop(app)""", "lang": "df"},

 {"h2": "O que o Kiln continua não tendo"},
 {"p": "HTTP/2 e TLS. Ele roda sobre o `http.server` do Python; em produção pública, ponha um nginx ou Caddy na frente — e o WebSocket atravessa proxy reverso sem configuração especial em nenhum dos dois."},
 {"p": "Para um painel que só precisa mostrar dado fresco, a [Vitrine](/docs/vitrine/producao) tem `V.atualizar_a_cada(n)`, que é por pergunta e mais simples que os dois."},
]},
]

PAGINAS += [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/tecnicas/cobertura",
"title": "Cobertura de testes",
"description": "Quais linhas os testes executaram, e por que os dois lados da fração precisam estar certos.",
"blocos": [
 {"p": "Uma suíte verde não diz nada sobre o que ela não exercita. `13 passaram` não distingue \"o sistema está testado\" de \"os treze caminhos fáceis estão testados\" — e num sistema de 200 arquivos, o código que ninguém tocou é exatamente onde o bug mora."},

 {"h2": "Como se pede"},
 {"code": """dataforge test --cobertura
dataforge test --cobertura --linhas     # as linhas descobertas, em faixas
dataforge test --minimo=80              # reprova abaixo disso (saída 1)

dataforge crucible --cobertura          # o mesmo, no Crucible""", "lang": "bash"},
 {"code": """  src/main.df         ░░░░░░░░░░░░░░░░░░░░   0.0%  0/94
                      sem teste: montar_cli, mostrar, principal
  src/repositorio.df  ████████████████████ 100.0%  38/38
  src/tarefa.df       ████████████████████ 100.0%  14/14

  total  35.6%  52 de 146 linhas executáveis""", "lang": "text"},
 {"p": "`--minimo` aceita `80`, `80%` e `0.8`. A fronteira é em 1 **inclusive**: `--minimo=1` é um por cento, porque ninguém exige cobertura total digitando `1`."},

 {"h2": "A informação que resolve"},
 {"p": "`58% coberto` não diz o que fazer. **`sem teste: nunca_chamada`** diz."},
 {"p": "Por isso o relatório lista, para cada arquivo, os nomes das ações cujo corpo nunca rodou — e com `--linhas`, as linhas em faixas (`3-5, 9, 11-12`), porque uma lista de setenta números é ilegível."},

 {"h2": "Os dois lados da fração"},
 {"p": "Cada metade tem um jeito próprio de mentir, e as duas foram tratadas:"},
 {"table": {"head": ["Metade", "De onde vem", "Como mentiria"], "rows": [
   ["denominador", "o parser: quais linhas são **executáveis**", "contar comentário e linha vazia dá um número sempre pessimista, que ninguém olha duas vezes"],
   ["numerador", "a execução, instrumentada", "com a compilação de corpos ligada, o corpo das ações passa por fora e **toda ação daria 0%**"]]}},
 {"p": "E duas escolhas que mudam o que se lê:"},
 {"callout": {"tipo": "nota", "titulo": "A linha do `action` não conta; o corpo conta", "texto": "Assim uma ação nunca chamada aparece com **0%**, e não com 20% por causa da linha da declaração. Zero é a leitura honesta."}},
 {"callout": {"tipo": "nota", "titulo": "Arquivo sem teste nenhum aparece com 0%", "texto": "Em vez de sumir do relatório. Sumir é o que faz uma cobertura de 95% conviver com metade do sistema sem teste — e é o defeito mais comum das ferramentas que medem só o que foi importado."}},

 {"h2": "O que ela não mede"},
 {"p": "É de **linha**, e não de ramo: `given a and b` conta como coberta mesmo que `b` nunca tenha sido avaliado. Medir ramo exigiria instrumentar a avaliação de expressão, o que dobraria o custo — e cobertura de linha já responde a pergunta que importa, que é \"existe código que ninguém testou\"."},

 {"h2": "No CI"},
 {"code": """- name: testes com cobertura mínima
  run: dataforge test --minimo=80""", "lang": "yaml"},
 {"p": "O comando devolve `1` quando fica abaixo, então o job falha. Comece pelo número que você já tem, e suba-o um ponto por vez — um mínimo de 80% num projeto a 35% só ensina a desligar a verificação."},

 {"h2": "Uma advertência"},
 {"p": "Cobertura alta não é qualidade. Um teste que chama tudo e não verifica nada dá 100%:"},
 {"code": """action test_nao_verifica_nada():
    processar_pedido(pedido)      // coberto a 100%, zero garantido""", "lang": "df"},
 {"p": "O número serve para achar o que está a **zero**, e é aí que ele vale quase tudo o que custa. Para o resto, [`Crucible`](/docs/tecnicas/testes) — matchers, dublês, teste por propriedade e instantâneo."},

 {"h2": "`forge_modules/` fica de fora"},
 {"p": "Os testes das suas dependências não são os seus. Um projeto com 13 testes relatava **89**, e a suíte ficava vermelha por falha de uma biblioteca que ninguém escreveu."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/tecnicas/instantaneos",
"title": "Instantâneos e isolamento",
"description": "Três ferramentas do Crucible para resultado grande, estado que sobra entre testes e falha que vai e volta.",
"blocos": [
 {"p": "O que um teste comum não alcança bem."},

 {"h2": "Instantâneo"},
 {"code": """adopt Crucible

crucible "o relatorio":
    trial "nao muda sem aviso":
        Crucible.snapshot("relatorio_mensal", gerar_relatorio())

    trial "e o HTML da pagina tambem":
        Crucible.snapshot("pagina_inicial", V.html_da_pagina())""", "lang": "df"},
 {"p": "Para o que é grande demais para escrever à mão no teste: o HTML de uma página, o relatório de trinta linhas, o JSON de uma rota. Escrever o esperado à mão para isso dá um teste que ninguém mantém — e um teste que ninguém mantém vira um teste que alguém comenta."},

 {"h3": "Na primeira vez ele grava e passa"},
 {"p": "É o único jeito de começar, e por isso o arquivo vai no **controle de versão**: é no diff do commit que alguém confere se o novo esperado está certo."},
 {"code": """__snapshots__/relatorio_test.snap.json""", "lang": "text"},
 {"p": "Um JSON por arquivo de teste, ao lado dele — assim andam junto num `git mv`, e o diff mostra os dois lado a lado. As chaves saem **ordenadas**: um vault que muda de ordem de inserção faria o instantâneo falhar sem nada ter mudado de verdade."},

 {"h3": "Aceitar uma mudança intencional"},
 {"code": """DF_ATUALIZAR_SNAPSHOT=1 dataforge crucible""", "lang": "bash"},
 {"callout": {"tipo": "atencao", "titulo": "Nunca atualize por padrão", "texto": "Seria **pior que não ter instantâneo**: o teste passaria sempre, gravando o errado por cima do certo. A variável de ambiente existe para ser digitada de propósito, e para aparecer no histórico do shell de quem a digitou."}},

 {"h3": "Quando muda"},
 {"code": """o instantaneo 'relatorio_mensal' mudou.
    @@ -3,7 +3,7 @@
       "clientes": 1240,
    -  "receita": 84200.0,
    +  "receita": 91800.0,
       "ticket": 67.9,
    para aceitar: DF_ATUALIZAR_SNAPSHOT=1 dataforge crucible
    o arquivo:    __snapshots__/relatorio_test.snap.json""", "lang": "text"},
 {"p": "A mensagem traz o **diff**, e não os dois textos inteiros: trezentas linhas lado a lado num terminal são ilegíveis, e ter trezentas linhas é justamente o motivo de usar instantâneo."},

 {"h2": "Banco que se desfaz"},
 {"code": """crucible "cadastro de livros":
    Crucible.before(lambda suite: Crucible.banco(db))

    trial "grava um livro":
        Banco.insert(db, "livros", {"titulo": "Duna", "preco": 79.9})
        Crucible.expect(Banco.count(db, "livros")).to_be(1)

    trial "e o seguinte nao ve o que ele gravou":
        Crucible.expect(Banco.count(db, "livros")).to_be(0)""", "lang": "df"},
 {"p": "O problema: um teste que grava deixa a linha lá, e o teste seguinte a encontra. A suíte passa **na ordem em que foi escrita** e falha em qualquer outra — e `--aleatorio` expõe isso de um jeito que parece intermitente."},
 {"p": "`Crucible.banco(db)` abre uma transação e a desfaz no fim do trial, sempre. Apagar tudo entre testes seria a alternativa, e é mais lenta e mais frágil: ela precisa saber a ordem das chaves estrangeiras."},
 {"callout": {"tipo": "dica", "titulo": "Vale para migração também", "texto": "Rode `Banco.migrate` uma vez no `before_all` e envolva cada trial em `Crucible.banco(db)`. O schema é criado uma vez; o dado, nunca sobra."}},

 {"h2": "Teste instável"},
 {"code": """crucible "integracao":
    trial "consulta a API externa":
        r := Crucible.flaky(lambda: Http.get(URL).json(), 3, 0.5)
        Crucible.expect(r["ok"]).to_be(yes)""", "lang": "df"},
 {"p": "Existe para o que depende de rede, de relógio ou de escalonamento — e **não** para esconder um bug. Por isso ele devolve o número de tentativas:"},
 {"code": """{"ok": yes, "tentativas": 3}""", "lang": "text"},
 {"p": "Um teste que precisa de três tentativas toda vez não é instável, **está quebrado**, e o número é o que denuncia isso. Se ele aparece como 3 no seu relatório, o problema não é a rede."},
 {"callout": {"tipo": "nota", "titulo": "`to_raise` não captura a desistência", "texto": "O que `flaky` levanta ao desistir é a própria falha de expectativa do Crucible, que é o **sinal de teste reprovado** — não um erro a capturar. Use `monitor`/`handle` quando quiser conferir a desistência."}},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/tecnicas/testes", "title": "Crucible", "meta": "50 símbolos", "desc": "Suítes, matchers, dublês, fixtures, propriedade e benchmark."},
   {"href": "/docs/tecnicas/cobertura", "title": "Cobertura", "desc": "Quais linhas os testes executaram."},
   {"href": "/docs/exercicios/31-qualidade", "title": "Os exercícios", "desc": "Instantâneo, isolamento e instabilidade, verificados."}]},
]},
]
