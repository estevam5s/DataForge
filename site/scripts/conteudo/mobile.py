# -*- coding: utf-8 -*-
"""Aplicativos móveis — a Brasa, e a página multiplataforma.

A regra da seção é a do repositório inteiro: **não se inventa que
existe**. A Brasa entrega um PWA que o Android e o iPhone instalam; ela
não gera APK, e a página diz isso onde alguém procuraria.

Todo bloco `.df` roda — sem navegador, que é como o CI roda.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile",
"title": "Aplicativos móveis",
"description": "Brasa: o framework de aplicativos para o celular — abas, lista tocável, compartilhar, localização e o PWA que o Android e o iPhone instalam, testável sem navegador.",
"blocos": [
 {"p": "A **Brasa** transforma um programa DataForge num aplicativo que o **Android e o iPhone instalam na tela inicial**, abrem em tela cheia, sem barra de endereço, e usam sem conexão. Por baixo é a [Vitrine](/docs/vitrine): o programa roda no servidor, de cima para baixo, e o estado sobrevive por sessão. A Brasa acrescenta o que faz uma página virar aplicativo."},
 {"code": '''adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

produtos := [{"id": 1, "nome": "café", "qtd": 12},
             {"id": 2, "nome": "açúcar", "qtd": 3}]

app := Br.app("Estoque", cor := "#E8453C")

action inicio():
    Br.topo("Produtos")
    Br.lista(produtos, titulo := "nome", detalhe := "qtd",
             destino := "/produto?id={id}")

action produto():
    id := int(V.parametro("id", "0"))
    p := [x cycle x in produtos given x["id"] is id][0]
    Br.topo(p["nome"], voltar := yes)
    V.metrica("Em estoque", p["qtd"])
    Br.compartilhar($"{p["nome"]}: {p["qtd"]} em estoque")

Br.tela("/", inicio, titulo := "Estoque", icone := "carrinho", aba := yes)
Br.tela("/produto", produto)

// Br.rodar(app) sobe na rede local. Aqui, a Sonda toca sem navegador.
s := Br.testar(app)
s.tocar("açúcar")
assert s.titulo() is "açúcar"
s.voltar()
assert s.titulo() is "Produtos"
out s.itens()''', "lang": "df"},
 {"h2": "O que ela é"},
 {"table": {"head": ["Peça", "Como se escreve", "Página"], "rows": [
   ["barra de abas embaixo", "`Br.tela(\"/\", inicio, aba := yes, icone := \"casa\")`", "[Telas e navegação](/docs/mobile/telas-e-navegacao)"],
   ["topo com voltar", "`Br.topo(\"Produto\", voltar := yes)`", "[Telas e navegação](/docs/mobile/telas-e-navegacao)"],
   ["lista tocável", "`Br.lista(itens, destino := \"/p?id={id}\")`", "[Componentes](/docs/mobile/componentes)"],
   ["botão flutuante, estado vazio", "`Br.botao_flutuante(\"Novo\", \"/novo\")` · `Br.vazio(...)`", "[Componentes](/docs/mobile/componentes)"],
   ["recursos do aparelho", "`Br.compartilhar` · `Br.ligar` · `Br.mapa` · `Br.localizacao`", "[O aparelho](/docs/mobile/aparelho)"],
   ["o aplicativo instalável", "manifesto, service worker e ícones — gerados", "[PWA e publicação](/docs/mobile/pwa)"],
   ["testar", "`Br.testar(app)` · `Br.conferir_pwa(app)`", "[Testar](/docs/mobile/testar)"]]}},
 {"p": "E todo componente da Vitrine continua valendo dentro de uma tela: `V.entrada`, `V.botao`, `V.metrica`, `V.grafico`, `V.camera`… O CSS da Brasa os ajusta ao dedo — botão com 44 px de altura, campo com fonte de 16 px (abaixo disso o iPhone dá zoom ao tocar)."},
 {"h2": "Começar"},
 {"code": '''$ dataforge mobile novo tarefas
$ cd tarefas
$ dataforge test                     # as telas sem navegador, e o PWA conferido
$ dataforge mobile rodar src/main.df
  Tarefas no ar
  neste computador:  http://localhost:8600
  no celular:        http://192.168.0.12:8600   (mesma rede Wi-Fi)''', "lang": "bash"},
 {"p": "Abra o endereço do celular no navegador dele: o aplicativo funciona na hora. Para **instalar** na tela inicial, o endereço precisa ser HTTPS — ver [PWA e publicação](/docs/mobile/pwa)."},
 {"callout": {"tipo": "atencao", "titulo": "Não há APK", "texto": "O que a Brasa entrega é um PWA: uma página que o sistema instala como aplicativo. Empacotar o interpretador num APK exigiria python-for-android ou Chaquopy, e as duas trazem a cadeia de dependências que a linguagem não tem. O que existe e o que não existe está em [Limites](/docs/mobile/limites)."}},
 {"cards": [
   {"title": "Telas e navegação", "desc": "abas, topo, voltar e parâmetros.", "href": "/docs/mobile/telas-e-navegacao"},
   {"title": "Componentes", "desc": "lista, vazio, seção e botão flutuante.", "href": "/docs/mobile/componentes"},
   {"title": "O aparelho", "desc": "compartilhar, ligar, mapa e localização.", "href": "/docs/mobile/aparelho"},
   {"title": "Testar", "desc": "a Sonda, e o PWA conferido servindo.", "href": "/docs/mobile/testar"},
   {"title": "PWA e publicação", "desc": "instalar exige HTTPS — as formas que funcionam.", "href": "/docs/mobile/pwa"},
   {"title": "Limites", "desc": "o que não existe, e a decisão.", "href": "/docs/mobile/limites"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile/telas-e-navegacao",
"title": "Telas e navegação",
"description": "Registrar telas, a barra de abas, o topo com voltar, e passar parâmetros de uma tela a outra.",
"blocos": [
 {"p": "`Br.tela(caminho, acao, titulo, icone, aba)` registra uma tela. As que têm `aba := yes` aparecem na barra de baixo — até **cinco**: acima disso o rótulo não cabe numa tela de celular, e o Material e a Apple param em cinco. As outras são telas de detalhe, abertas por uma lista ou um botão."},
 {"code": '''adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

app := Br.app("Clube", cor := "#2F6FED")

action inicio():
    Br.topo("Início")
    V.texto("bem-vindo")

action agenda():
    Br.topo("Agenda")
    Br.lista([{"id": 7, "nome": "Treino"}], destino := "/evento?id={id}")

action evento():
    Br.topo($"Evento {V.parametro("id")}", voltar := yes)

Br.tela("/", inicio, titulo := "Início", icone := "casa", aba := yes)
Br.tela("/agenda", agenda, titulo := "Agenda", icone := "calendario", aba := yes)
Br.tela("/evento", evento)

s := Br.testar(app)
assert s.abas() is [{"titulo": "Início", "ativa": yes}, {"titulo": "Agenda", "ativa": no}]
s.tocar("Agenda")
s.tocar("Treino")
assert s.titulo() is "Evento 7"
assert [a["ativa"] cycle a in s.abas()] is [no, no]   // no detalhe, nenhuma acesa
s.voltar()
assert s.titulo() is "Agenda"''', "lang": "df"},
 {"h2": "O topo e o voltar"},
 {"p": "`Br.topo(titulo, voltar := yes)` desenha a seta. Ela usa o **histórico do navegador** — é o que o gesto de voltar do Android faz — e cai em `destino_voltar` (padrão `/`) quando não há para onde voltar: o aplicativo foi aberto direto naquela tela, por um link compartilhado."},
 {"h2": "Parâmetros"},
 {"p": "O destino de uma lista leva os campos do item — `\"/produto?id={id}\"` —, e a tela de destino os lê com `V.parametro(\"id\")`. Cada valor é **codificado** na URL: um id com `&` dentro não vira um segundo parâmetro."},
 {"h2": "Os ícones"},
 {"code": '''adopt Arcane.Vitrine as V

out len(V.icones()), "ícones"
out V.icones()[0:8]''', "lang": "df"},
 {"p": "O ícone da aba é o **nome** de um dos ícones da Vitrine (SVG escrito na página, sem CDN) ou um **emoji**. Um nome que não existe é recusado na linha que registra a tela, com sugestão — `nao ha icone 'caixa'`, *você quis dizer: baixar, casa, faisca* —, em vez de desenhar a palavra na barra."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile/componentes",
"title": "Componentes",
"description": "Lista tocável, estado vazio, seção e botão flutuante — e os da Vitrine, que continuam valendo.",
"blocos": [
 {"h2": "Lista"},
 {"code": '''adopt Arcane.Brasa as Br

contatos := [
    {"id": 1, "nome": "Ana Souza", "cidade": "Recife"},
    {"id": 2, "nome": "Bruno Lima", "cidade": "Curitiba"},
]
app := Br.app("Contatos")

action tela():
    Br.topo("Contatos")
    Br.secao("Favoritos")
    Br.lista(contatos, titulo := "nome", detalhe := "cidade",
             destino := "/contato?id={id}", icone := "usuario")

Br.tela("/", tela)
s := Br.testar(app)
assert s.itens() is [{"titulo": "Ana Souza", "detalhe": "Recife"},
                     {"titulo": "Bruno Lima", "detalhe": "Curitiba"}]''', "lang": "df"},
 {"p": "A **linha inteira** é o alvo, com 56 px de altura — o dedo não acerta um link de 14 px no meio de um texto. `titulo` e `detalhe` são nomes de campo, e o item pode ser vault, record ou instância. O texto é **escapado**: um nome com `<script>` aparece como texto, e não roda."},
 {"h2": "Estado vazio"},
 {"code": '''adopt Arcane.Brasa as Br

app := Br.app("Pedidos")

action tela():
    Br.topo("Pedidos")
    Br.vazio("Nenhum pedido ainda", "os pedidos novos aparecem aqui")

Br.tela("/", tela)
assert Br.testar(app).tem("Nenhum pedido ainda")''', "lang": "df"},
 {"p": "Uma lista vazia sem explicação parece **travada**. O vazio diz o que é e, na dica, o que fazer."},
 {"h2": "Botão flutuante"},
 {"code": '''adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

notas := []
app := Br.app("Notas")

action lista():
    Br.topo("Notas")
    Br.lista(notas, titulo := "texto")
    Br.botao_flutuante("Nova nota", "/nova")

action nova():
    Br.topo("Nova nota", voltar := yes)
    texto := V.entrada("Texto")
    given V.botao("Salvar"):
        notas.append({"texto": texto})
        V.navegar("/")

Br.tela("/", lista, titulo := "Notas", icone := "lapis", aba := yes)
Br.tela("/nova", nova)

s := Br.testar(app)
s.tocar("Nova nota")
s.digitar("Texto", "comprar pão")
s.clicar("Salvar")
s.ir("/")
assert s.tem("comprar pão")''', "lang": "df"},
 {"p": "Ele fica no canto, **acima** da barra de abas, e respeita a área segura do aparelho (o entalhe e a barra de gestos do iPhone)."},
 {"h2": "Os links são conferidos"},
 {"table": {"head": ["Destino", "Resultado"], "rows": [
   ["`/produto?id=3`", "aceito — um caminho do aplicativo"],
   ["`tel:`, `sms:`, `mailto:`, `geo:`, `https:`", "aceito — abre o aplicativo do aparelho"],
   ["`javascript:…`, `//outro.site`, `data:…`", "**recusado** — um dado nunca vira código"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile/aparelho",
"title": "O aparelho",
"description": "Compartilhar, ligar, abrir no mapa e a localização — pelo navegador, com a permissão do usuário.",
"blocos": [
 {"p": "O aplicativo alcança o aparelho **pelo navegador**, com as APIs da web e a permissão do usuário. Nada disso é nativo, e cada recurso diz o que acontece onde ele não existe."},
 {"table": {"head": ["Chamada", "No celular", "Onde não há"], "rows": [
   ["`Br.compartilhar(texto)`", "a folha do sistema (WhatsApp, e-mail…)", "copia para a área de transferência e diz \"Copiado\""],
   ["`Br.ligar(numero)`", "abre o discador", "o computador pergunta que aplicativo usar"],
   ["`Br.mapa(lat, lon)`", "abre o aplicativo de mapas", "abre o mapa no navegador"],
   ["`Br.localizacao()`", "pede a posição ao usuário", "exige **HTTPS** — sem ele, o botão diz isso"]]}},
 {"code": '''adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

app := Br.app("Entregas")

action tela():
    Br.topo("Entrega 42")
    Br.ligar("+55 11 99999-0000", "Ligar para o cliente")
    Br.mapa(-23.5505, -46.6333, "Ver o endereço")
    Br.compartilhar("Entrega 42 a caminho")
    onde := Br.localizacao("Registrar minha posição")
    given onde isnt void:
        V.texto($"posição: {onde["lat"]}, {onde["lon"]} (±{onde["precisao"]} m)")

Br.tela("/", tela)

s := Br.testar(app)
assert not s.tem("posição:")
s.localizacao(-23.5505, -46.6333, 12)      // o que o navegador responderia
assert s.tem("posição: -23.5505, -46.6333 (±12.0 m)")''', "lang": "df"},
 {"h2": "Como a localização chega"},
 {"p": "O botão pede a posição ao navegador, que pergunta ao usuário. A resposta volta como parâmetro, a tela roda de novo com ela, e ela **fica na sessão** — a próxima tela não pede outra vez. `Br.localizacao()` devolve `{lat, lon, precisao}` ou `void`, e na Sonda `s.localizacao(lat, lon)` faz o papel do navegador."},
 {"callout": {"tipo": "atencao", "titulo": "HTTPS, de novo", "texto": "O navegador só oferece `navigator.geolocation` num contexto seguro: HTTPS ou `localhost`. Pela rede local em `http://192.168…` o botão diz \"Precisa de HTTPS para localizar\" em vez de ficar mudo."}},
 {"h2": "A câmera"},
 {"p": "É o `V.camera` da Vitrine: o navegador do celular abre a câmera traseira, e a foto chega à tela como arquivo. Ver [Vitrine](/docs/vitrine)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile/testar",
"title": "Testar",
"description": "A Sonda toca, volta e confere sem navegador — e o PWA é conferido servindo, como o Android o veria.",
"blocos": [
 {"code": '''adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V
adopt Arcane.Crucible as Crucible

tarefas := [{"id": 1, "titulo": "Estudar", "feita": no}]
app := Br.app("Tarefas")

action inicio():
    Br.topo("Tarefas")
    Br.lista([t cycle t in tarefas given not t["feita"]],
             titulo := "titulo", destino := "/tarefa?id={id}")

action tarefa():
    t := tarefas[int(V.parametro("id")) - 1]
    Br.topo(t["titulo"], voltar := yes)
    given V.botao("Concluir"):
        t["feita"] := yes
        V.navegar("/")

Br.tela("/", inicio, titulo := "Tarefas", icone := "conferir", aba := yes)
Br.tela("/tarefa", tarefa)

crucible "o aplicativo":
    trial "concluir tira da lista":
        s := Br.testar(app)
        s.tocar("Estudar")
        s.clicar("Concluir")
        s.ir("/")
        expect len(s.itens()) is 0

    trial "o PWA tem tudo que o Android exige":
        falhas := [c cycle c in Br.conferir_pwa(app) given not c["ok"]]
        expect falhas is []

Crucible.run()''', "lang": "df"},
 {"h2": "A Sonda"},
 {"table": {"head": ["Chamada", "Faz"], "rows": [
   ["`s.tocar(rotulo)`", "toca numa linha da lista, numa aba ou no botão flutuante"],
   ["`s.voltar()` · `s.ir(caminho)`", "o gesto de voltar, e abrir uma tela"],
   ["`s.localizacao(lat, lon)`", "o que o navegador responderia"],
   ["`s.clicar` · `s.digitar`", "os da Vitrine, nos componentes dela"],
   ["`s.titulo()` · `s.itens()` · `s.abas()` · `s.caminho()`", "o que a tela desenhou, como dado"],
   ["`s.texto()` · `s.tem(texto)` · `s.html()`", "o conteúdo"]]}},
 {"p": "A Sonda não analisa o HTML: cada componente da Brasa **anota** o que desenhou (título, itens, abas, destinos), e é essa anotação que ela lê. Por isso `s.tocar(\"café\")` acha a linha pelo que o programa passou, e não por uma expressão regular."},
 {"h2": "`Br.conferir_pwa`: o que o Android exige"},
 {"p": "Ele **não** confere a configuração: sobe o aplicativo, pede cada arquivo por HTTP e olha o que chegou. Um manifesto certo servido com o tipo errado não instala — e só pedindo se descobre isso."},
 {"table": {"head": ["Conferido", "Por quê"], "rows": [
   ["a página liga o manifesto, declara `theme-color` e registra o service worker", "sem os três, o \"instalar\" não aparece"],
   ["o manifesto vem como `application/manifest+json` e tem nome, `start_url`, `display` e ícones", "o que o Chrome lê para oferecer a instalação"],
   ["`display: standalone`", "abrir sem barra de endereço"],
   ["ícones PNG de 192 e 512 px, e um **maskable** de 512", "o Android recorta o ícone; o maskable deixa a margem"],
   ["o service worker na raiz, como JavaScript, tratando `fetch`", "fora da raiz ele não cobre o aplicativo inteiro"],
   ["`viewport-fit=cover`", "o conteúdo respeitar o entalhe"]]}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile/pwa",
"title": "PWA e publicação",
"description": "Do programa ao ícone na tela inicial: o que a Brasa gera, por que instalar exige HTTPS, e as formas de publicar.",
"blocos": [
 {"h2": "O que a Brasa gera sozinha"},
 {"table": {"head": ["Arquivo", "O que é"], "rows": [
   ["`/manifest.webmanifest`", "nome, cor, ícones e `display: standalone`"],
   ["`/sw.js`", "o service worker, na raiz — **rede primeiro, cache de reserva**"],
   ["`/__brasa__/icone-192.png` e `-512.png`", "o ícone: a cor da marca e as iniciais do nome, em PNG"],
   ["`/__brasa__/icone-maskable-512.png`", "o mesmo, de borda a borda, para o recorte do Android"]]}},
 {"code": '''adopt Arcane.Brasa as Br

app := Br.app("Estoque da Loja", cor := "#E8453C", versao := "3")
m := Br.manifesto(app)
assert m["display"] is "standalone"
assert m["short_name"] is "Estoque da L"
out [i["sizes"] cycle i in m["icons"]]''', "lang": "df"},
 {"p": "Os ícones são PNG escritos em Python puro — cabeçalho, pixels comprimidos com `zlib`, CRC —, porque a biblioteca padrão não desenha imagem e trazer o Pillow quebraria a promessa de zero dependência por um quadrado com duas letras."},
 {"h2": "Rede primeiro, cache de reserva"},
 {"p": "O service worker busca da rede e **só** cai no cache quando ela falha. Cache primeiro seria mais rápido — e faria o aplicativo mostrar dado velho sem avisar. Só `GET` entra no cache: uma ação repetida do cache seria um pedido duplicado. Uma tela nunca aberta com internet mostra \"Sem conexão\" em vez de uma página em branco."},
 {"callout": {"tipo": "nota", "titulo": "Suba a `versao` a cada publicação", "texto": "Ela entra no nome do cache (`brasa-3`). Sem mudar a versão, o aparelho continua servindo o cache antigo — e o sintoma é \"publiquei e não mudou nada\", que faz perder uma tarde."}},
 {"h2": "Instalar exige HTTPS"},
 {"p": "Pela rede local, em `http://192.168…`, o aplicativo **abre e funciona**, mas o celular não oferece \"instalar\" e o service worker não roda — e não há aviso: o botão simplesmente não aparece. É regra do navegador, não da linguagem. `localhost` é a exceção, para desenvolver no computador."},
 {"table": {"head": ["Forma", "Quando"], "rows": [
   ["um proxy com certificado (Caddy, nginx) na frente do `Br.rodar`", "o aplicativo roda num servidor seu"],
   ["um túnel (Cloudflare Tunnel, ngrok)", "para mostrar a alguém hoje, do seu computador"],
   ["um contêiner numa plataforma com HTTPS", "`dataforge devops` gera o Dockerfile; lembre de `--host=0.0.0.0`"]]}},
 {"p": "O Kiln, que serve a Vitrine e a Brasa, **não tem TLS** — ele roda sobre o `http.server` do Python. Em produção, o proxy vai na frente."},
 {"h2": "Conferir no aparelho"},
 {"list": [
   "No Chrome do Android: o menu mostra **Instalar aplicativo** (sem manifesto, ele oferece só um atalho comum).",
   "No iPhone: Safari → Compartilhar → **Adicionar à Tela de Início**.",
   "Abra pelo ícone: **não há barra de endereço** — é o `standalone`.",
   "Desligue a rede e reabra uma tela já visitada: ela abre, do cache."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile/limites",
"title": "Limites",
"description": "O que a Brasa não faz, por que, e quando esta linguagem não é a ferramenta.",
"blocos": [
 {"h2": "O que NÃO existe"},
 {"list": [
   "**APK** e publicação na Play Store ou na App Store.",
   "**Widget nativo** (Material, Compose, SwiftUI) — os componentes são HTML com o CSS ajustado ao dedo.",
   "**Notificação push** — exigiria um servidor de push e chaves VAPID, e no iPhone só funciona com o aplicativo instalado.",
   "**Bluetooth, NFC e sensores** — as APIs da web para eles são parciais, e só no Chrome.",
   "**Funcionar sem servidor**: o programa roda no servidor. Sem rede, o aplicativo mostra as telas já visitadas, do cache — não executa nada novo."]},
 {"h2": "O iPhone tem limites próprios"},
 {"p": "O Safari instala o PWA na tela inicial, mas descarta o service worker com mais frequência, e a notificação só existe com o aplicativo instalado. O que a Brasa gera funciona nos dois — o que muda é quanto do cache sobrevive."},
 {"h2": "A decisão, escrita"},
 {"p": "Um APK que empacota o CPython é possível, e custa a promessa central do projeto: **zero dependência**. O PWA entrega o caso de uso real — uma ferramenta no celular de quem trabalha: o estoque, a entrega, o chamado, o painel — sem quebrar nada. Quando o caso for um aplicativo de loja, com widget nativo e notificação, a resposta honesta é que esta linguagem não é a ferramenta."},
 {"code": '''$ dataforge mobile doctor''', "lang": "bash"},
 {"p": "O `doctor` repete, no terminal, o que existe e o que não existe — para ninguém precisar abrir esta página para descobrir."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/multiplataforma",
"title": "Uma regra, três plataformas",
"description": "A mesma regra de negócio na web (Vitrine), na mesa (Bigorna) e no celular (Brasa) — escrita uma vez, testada uma vez.",
"blocos": [
 {"p": "Os três frameworks de interface do DataForge têm a **mesma forma** — o programa da tela roda de cima para baixo, de novo a cada interação — e isso não é coincidência: é o que deixa a regra de negócio morar num módulo **sem interface nenhuma**, usado igual pelos três."},
 {"table": {"head": ["", "Vitrine", "Bigorna", "Brasa"], "rows": [
   ["onde roda", "navegador", "janela nativa (Tk)", "celular (PWA)"],
   ["para", "painel e aplicação de dados", "ferramenta de mesa", "aplicativo no bolso"],
   ["navegação", "páginas", "telas, menus e atalhos", "abas e voltar"],
   ["testar", "`V.testar`", "`B.testar`", "`Br.testar`"],
   ["distribuir", "servidor", "`.app`, `.exe`, binário", "PWA por HTTPS"]]}},
 {"h2": "A regra, uma vez"},
 {"code": '''// estoque.df — nenhum adopt de interface aqui dentro.
record Produto:
    nome: String
    qtd: Integer

action baixar(p: Produto, quanto: Integer) -> Produto:
    given quanto bigger p.qtd:
        trigger $"só há {p.qtd} de {p.nome}"
    yield p with {"qtd": p.qtd - quanto}

action resumo(itens) -> String:
    yield $"{len(itens)} produto(s), {sum([i.qtd cycle i in itens])} unidades"

p := baixar(Produto("café", 12), 2)
assert p.qtd is 10
assert resumo([p]) is "1 produto(s), 10 unidades"
out "a regra não sabe onde vai aparecer"''', "lang": "df"},
 {"h2": "As três telas"},
 {"code": '''adopt Arcane.Bigorna as B
adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V
adopt Arcane.OS as OS

record Produto:
    nome: String
    qtd: Integer

action resumo(itens) -> String:
    yield $"{len(itens)} produto(s), {sum([i.qtd cycle i in itens])} unidades"

estoque := [Produto("café", 12), Produto("açúcar", 3)]

// ── na mesa ──
mesa := B.app("Estoque", pasta_de_config := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")
action tela_mesa(t):
    t.titulo("Estoque")
    t.tabela(["nome", "qtd"], [{"nome": p.nome, "qtd": p.qtd} cycle p in estoque])
    t.status(resumo(estoque))
mesa.tela("inicio", tela_mesa)

// ── no celular ──
celular := Br.app("Estoque")
action tela_celular():
    Br.topo("Estoque")
    Br.lista(estoque, titulo := "nome", detalhe := "qtd")
    V.texto(resumo(estoque))
Br.tela("/", tela_celular)

// ── as duas, testadas contra a MESMA regra ──
assert B.testar(mesa).status() is "2 produto(s), 15 unidades"
assert Br.testar(celular).tem("2 produto(s), 15 unidades")
out "uma regra, duas telas, o mesmo resultado"''', "lang": "df"},
 {"p": "Num projeto de verdade, a regra fica em `src/estoque.df` e cada interface a adota com `adopt ./estoque as E`. Um teste da regra não abre janela nem sobe servidor — e é ele que pega o erro de negócio, antes de qualquer tela."},
 {"cards": [
   {"title": "Vitrine", "desc": "painéis e aplicações de dados no navegador.", "href": "/docs/vitrine"},
   {"title": "Bigorna", "desc": "aplicações de mesa nativas.", "href": "/docs/desktop"},
   {"title": "Brasa", "desc": "aplicativos para o celular.", "href": "/docs/mobile"}]},
]},
]
