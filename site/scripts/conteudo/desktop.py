# -*- coding: utf-8 -*-
"""Desktop e mobile — sete páginas.

A regra da seção é a do repositório inteiro: **não se inventa que
existe**. O desktop é nativo e funciona nos três sistemas; o Android
tem um caminho que funciona (PWA) e um que não existe (APK), e a página
diz qual é qual.

Todo bloco roda — sem display, que é como o CI roda.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/desktop",
"title": "Aplicações de mesa",
"description": "Uma janela nativa em macOS, Windows e Linux — com zero dependência, e testável sem display.",
"blocos": [
 {"p": "O Tk vem **na biblioteca padrão do Python**, e é a única forma de desenhar uma janela nativa nos três sistemas sem trazer nada de fora. Qt, GTK e wx dariam mais controle e quebrariam a única promessa inegociável do projeto."},
 {"code": '''adopt Arcane.Janela as J

action tela(t):
    t.titulo("Cadastro")
    nome := t.entrada("Nome", "")
    given t.botao("Salvar"):
        t.aviso($"salvo: {nome}")

// Com display, abre a janela. Sem, a Sonda exercita a MESMA tela.
given J.tem_display():
    out "aqui eu abriria: J.abrir(J.app(\\"Cadastro\\"), tela)"
otherwise:
    out "sem display — e a tela continua testável"

s := J.testar(tela)
s.digitar("Nome", "café")
s.clicar("Salvar")
assert s.tem("salvo: café")
out s.texto()''', "lang": "df"},
 {"h2": "A forma é a da Vitrine"},
 {"p": "E isso não é coincidência: **o programa inteiro roda de novo a cada interação**, e o estado sobrevive. É o que dispensa callback, diffing e a pergunta \"onde fica o estado\" — e é o que torna uma tela testável."},
 {"table": {
   "head": ["", "Callback (Tk cru, Qt)", "Reexecução (aqui, e na Vitrine)"],
   "rows": [
     ["onde mora o estado", "espalhado em widgets", "no vault da aplicação"],
     ["ler um campo", "`entry.get()`", "`nome := t.entrada(\"Nome\")` — a própria chamada"],
     ["redesenhar", "você lembra de fazer", "acontece"],
     ["testar", "precisa de display e de robô", "`J.testar(tela)`"],
     ["o custo", "—", "a tela roda inteira a cada clique"]]}},
 {"h2": "Começar"},
 {"code": '''$ dataforge desktop novo caixa
$ cd caixa
$ dataforge test                     # a tela, sem abrir janela
$ dataforge desktop rodar src/main.df''', "lang": "bash"},
 {"p": "O esqueleto separa `src/tela.df` de `src/main.df`, e a razão é a mesma do Kiln (`server` monta, `ignite` sobe): um teste que importasse o módulo da tela **abriria a janela e nunca terminaria**."},
 {"h2": "O que ela NÃO é"},
 {"list": [
   "Não há animação, tema por componente, arrastar-e-soltar nem gráfico interativo.",
   "Para painel de dados existe a **Vitrine**, que roda no navegador e desenha 27 tipos de gráfico.",
   "Esta peça é para a ferramenta interna de mesa — a que lê um arquivo, mostra uma tabela, tem quatro botões, e precisa rodar numa máquina sem navegador."]},
 {"cards": [
   {"title": "Os componentes", "desc": "o que dá para pôr na tela, e o que cada um devolve.", "href": "/docs/desktop/componentes"},
   {"title": "Testar sem display", "desc": "a Sonda, e por que ela não simula nada.", "href": "/docs/desktop/testar"},
   {"title": "Empacotar", "desc": ".app, .exe e binário — e o que o PyInstaller cobra.", "href": "/docs/desktop/empacotar"},
   {"title": "Android", "desc": "o que funciona, e o APK que não existe.", "href": "/docs/mobile"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/desktop/componentes",
"title": "Os componentes",
"description": "Vinte e dois, e o que cada um devolve para o programa.",
"blocos": [
 {"p": "Cada chamada **põe** um componente e **devolve** o valor dele. É o que faz a tela ser um programa comum, de cima para baixo."},
 {"h2": "Entradas"},
 {"code": '''adopt Arcane.Janela as J

action tela(t):
    nome := t.entrada("Nome", "")
    senha := t.senha("Senha")
    idade := t.numero("Idade", 18, 0, 120)
    obs := t.area("Observações", "", 4)
    cor := t.escolha("Cor", ["azul", "verde"], "verde")
    ativo := t.caixa("Ativo", yes)
    nivel := t.deslizante("Nível", 0, 10, 5)
    quando := t.data("Quando", "2026-09-22")
    onde := t.arquivo("Arquivo", "", ["csv"])

    t.texto($"{nome}|{idade}|{cor}|{ativo}|{nivel}")

s := J.testar(tela)
assert s.campos() is ["Arquivo", "Ativo", "Cor", "Idade", "Nome", "Nível", "Observações", "Quando", "Senha"]
s.digitar("Nome", "Ana")
s.digitar("Idade", 30)
assert s.tem("Ana|30|verde|yes|5")
out s.texto()''', "lang": "df"},
 {"table": {
   "head": ["Componente", "Devolve", "Nota"],
   "rows": [
     ["`entrada`", "texto", "uma linha"],
     ["`senha`", "texto", "esconde o que se digita"],
     ["`numero`", "**Integer ou Float**", "digitado ele chega como texto, e `n + 1` daria concatenação"],
     ["`area`", "texto", "várias linhas"],
     ["`escolha`", "a opção", "uma de uma lista"],
     ["`caixa`", "`yes`/`no`", ""],
     ["`deslizante`", "número", "com mínimo e máximo"],
     ["`data`", "texto", "sem seletor nativo — é um campo com formato"],
     ["`arquivo`", "o caminho", "sem display, é um campo de texto"]]}},
 {"h2": "Mostrar"},
 {"code": '''adopt Arcane.Janela as J

action tela(t):
    t.titulo("Relatório")
    t.texto("uma linha de texto comum")
    t.aviso("deu certo")
    t.erro("não deu")
    t.separador()
    t.tabela(["produto", "preço"], [
        {"produto": "café", "preço": "32,90"},
        {"produto": "filtro", "preço": "8,50"},
    ])
    t.lista(["primeiro", "segundo"])
    t.progresso(0.72, "carregando")

s := J.testar(tela)
assert s.tem("Relatório") and s.tem("deu certo")
assert s.tabelas()[0]["linhas"] is [["café", "32,90"], ["filtro", "8,50"]]
out s.texto()''', "lang": "df"},
 {"p": "A tabela aceita **vault ou lista**: com vault, as colunas casam pelo nome; com lista, pela posição. Os dois são comuns — `Database.query` devolve vaults, e um CSV lido devolve listas."},
 {"h2": "O botão vale para UMA execução"},
 {"code": '''adopt Arcane.Janela as J

salvos := []

action tela(t):
    t.entrada("Nome", "")
    given t.botao("Salvar", yes):
        salvos.append(1)

s := J.testar(tela)
s.clicar("Salvar")
assert len(salvos) is 1

// Reexecutar NÃO salva de novo: o clique é um evento, e não estado.
s.digitar("Nome", "x")
assert len(salvos) is 1
out "um clique, um salvamento"''', "lang": "df"},
 {"p": "Se o clique ficasse guardado, a próxima reexecução salvaria o formulário de novo — e esse é o defeito clássico de quem monta isto à mão."},
 {"h2": "Agrupar"},
 {"code": '''adopt Arcane.Janela as J

action tela(t):
    t.grupo("Identificação")
    t.entrada("Nome")
    t.entrada("E-mail")
    t.fim()

    t.grupo("Endereço")
    t.entrada("Rua")
    t.fim()

s := J.testar(tela)
assert s.tem("Identificação") and s.tem("Endereço")
assert len(s.campos()) is 3
out s.texto()''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Dois campos com o mesmo rótulo", "texto": "Eles existem — e sem um contador na chave dividiriam o estado, o que faz digitar num mudar o outro. A chave é `especie:rotulo`, com `#2` a partir do segundo."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/desktop/testar",
"title": "Testar sem display",
"description": "A Sonda monta a mesma árvore que o Tk desenharia — e por isso ela não simula nada.",
"blocos": [
 {"p": "Uma biblioteca de interface que só funciona com display é uma biblioteca **sem teste**: o runner do CI não tem display. A separação entre a **árvore** e o **desenho** é o que resolve isso — e ela é a mesma decisão da Vitrine."},
 {"code": '''adopt Arcane.Janela as J
adopt Arcane.Crucible as Crucible

itens := []

action tela(t):
    t.titulo("Lista")
    nome := t.entrada("Nome", "")
    given t.botao("Adicionar"):
        given nome is "":
            t.erro("o nome é obrigatório")
        otherwise:
            itens.append(nome)
    t.texto($"{len(itens)} item(ns)")

crucible "a tela":

    trial "o nome vazio e recusado":
        itens.clear()
        s := J.testar(tela)
        s.clicar("Adicionar")
        expect s.tem("o nome é obrigatório") is yes

    trial "adicionar conta":
        itens.clear()
        s := J.testar(tela)
        s.digitar("Nome", "café")
        s.clicar("Adicionar")
        expect s.tem("1 item(ns)") is yes

Crucible.run()''', "lang": "df"},
 {"h2": "O que a Sonda faz"},
 {"table": {
   "head": ["Chamada", "O quê"],
   "rows": [
     ["`s.digitar(rotulo, valor)`", "preenche e **reexecuta** a tela"],
     ["`s.clicar(rotulo)`", "clica e reexecuta — o clique vale para uma execução"],
     ["`s.escolher(rotulo, valor)`", "recusa o que não está na lista"],
     ["`s.marcar(rotulo, yes)`", "a caixa"],
     ["`s.texto()`", "tudo o que a tela mostra"],
     ["`s.valor(rotulo)`", "o valor de um campo"],
     ["`s.campos()`, `s.botoes()`", "o que existe na tela"],
     ["`s.tabelas()`", "as tabelas, com colunas e linhas"],
     ["`s.arvore()`", "a árvore inteira como vault — para instantâneo"]]}},
 {"h2": "Um rótulo que não existe lista os que existem"},
 {"code": '''adopt Arcane.Janela as J

action tela(t):
    t.entrada("Nome")
    t.botao("Salvar")

s := J.testar(tela)

monitor:
    s.digitar("Nomee", "x")
    assert no
handle Error as e:
    out e.message
    out $"  {e.nota}"''', "lang": "df"},
 {"h2": "A árvore é dado"},
 {"p": "Guardá-la num instantâneo faz **qualquer** mudança de tela aparecer no diff do commit — inclusive a que ninguém pretendia:"},
 {"code": '''adopt Arcane.Janela as J

action tela(t):
    t.titulo("Cadastro")
    t.entrada("Nome")
    t.botao("Salvar")

s := J.testar(tela)
arvore := s.arvore()
assert arvore["especie"] is "raiz"
assert [f["especie"] cycle f in arvore["filhos"]] is ["titulo", "entrada", "botao"]
out arvore["filhos"][1]''', "lang": "df"},
 {"h2": "O que a Sonda NÃO prova"},
 {"list": [
   "**O desenho.** Se um componente não tiver ramo no desenho, a Sonda passa e a janela não mostra nada.",
   "**A aparência** — fonte, espaçamento, cor. Nenhum teste aqui finge isso.",
   "**O comportamento do Tk** — o que acontece ao redimensionar, ao colar texto grande, ao usar leitor de tela.",
   "Por isso existe `test_a_janela_abre_de_verdade`, que **abre** uma janela e a fecha sozinha — e que pula onde não há display."]},
 {"callout": {"tipo": "nota", "titulo": "`fechar_em` existe por causa do teste", "texto": "Uma janela que só fecha no clique não tem como ser exercitada num CI, e o que não se exercita quebra calado. `J.abrir(app, tela, void, 400)` fecha sozinha em 400 ms."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/desktop/empacotar",
"title": "Empacotar",
"description": ".app, .exe e binário — e as três coisas que o PyInstaller cobra sem avisar.",
"blocos": [
 {"p": "`dataforge desktop empacotar` gera o lançador e chama o **PyInstaller**. É a mesma escolha do `iot carregar`, que chama o `arduino-cli`: empacotar um interpretador Python é um problema resolvido, e resolvê-lo de novo daria um subconjunto pior amarrado a esta linguagem."},
 {"code": '''$ dataforge desktop doctor
  ✓ Tk                   versão 8.6
  ✓ display              há para onde desenhar
  ✓ PyInstaller          /usr/local/bin/pyinstaller
  ✓ alvo desta máquina   .app (macOS)

$ dataforge desktop empacotar src/main.df --nome=Caixa
empacotando 'Caixa'…
pronto: dist/''', "lang": "bash"},
 {"h2": "As três coisas que ele cobra sem avisar"},
 {"table": {
   "head": ["O quê", "O sintoma", "O que o comando faz"],
   "rows": [
     ["import lazy", "\"No module named 'dataforge'\" — parece falta de instalação", "o lançador importa no **topo**, onde a análise estática enxerga"],
     ["instalação editável", "idem, e só na máquina de quem desenvolve", "passa `--paths` com a raiz do pacote"],
     ["só o arquivo de entrada", "morre no primeiro `adopt ./vizinho`", "empacota a **pasta inteira** do programa"]]}},
 {"p": "As três produzem o mesmo tipo de falha: o executável **monta, abre e morre** — e a mensagem fala de uma biblioteca que quem escreveu nunca viu. Foram os três defeitos desta implementação, nesta ordem."},
 {"h2": "E a guarda do `__main__`"},
 {"code": '''// O lançador gerado tem isto, e não é decoração:
//
//     if __name__ == "__main__":
//         multiprocessing.freeze_support()
//         main()
//
// Sem ela, o 'spawn' de map_processos reexecuta o APLICATIVO INTEIRO
// em cada trabalhador — e a mensagem fala de "bootstrapping phase",
// vocabulário do multiprocessing, três camadas longe de quem chamou.
adopt Arcane.Concurrent as C
assert C.nucleos() >= 1
out "num executável congelado, freeze_support() vem ANTES de main()"''', "lang": "df"},
 {"h2": "O que sai, por sistema"},
 {"table": {
   "head": ["Sistema", "Sai", "O que o usuário vê"],
   "rows": [
     ["macOS", "`dist/Nome.app` e `dist/Nome`", "o aviso do Gatekeeper até você assinar e notarizar"],
     ["Windows", "`dist/Nome.exe`", "o SmartScreen, até o executável ter reputação ou assinatura"],
     ["Linux", "`dist/Nome`", "depende da libc de quem construiu — construa na distro mais antiga que você suporta"]]}},
 {"h2": "O que NÃO existe"},
 {"list": [
   "**Assinatura e notarização** — é conta de desenvolvedor da Apple, e o comando não a pede nem a esconde.",
   "**Instalador** (`.dmg`, `.msi`, `.deb` do seu app) — o que sai é o executável.",
   "**Atualização automática.**",
   "**Compilação cruzada**: um `.exe` se faz no Windows, e um `.app` no macOS. O PyInstaller não cruza, e nenhuma opção aqui finge que cruza."]},
 {"callout": {"tipo": "atencao", "titulo": "O binário é grande, e isso é o interpretador", "texto": "Um app de tela simples sai com ~9 MB porque ele **carrega o Python inteiro** junto. É o preço de distribuir para quem não tem nada instalado — e é o mesmo preço do binário da própria CLI."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/desktop/completo",
"title": "Uma aplicação inteira",
"description": "Um controle de estoque com arquivo, tabela, validação e teste — em 70 linhas.",
"blocos": [
 {"p": "Juntando tudo: lê e grava um arquivo, valida a entrada, mostra uma tabela e tem teste que roda sem display."},
 {"code": '''adopt Arcane.Janela as J
adopt Arcane.Serialization as Ser
adopt Arcane.IO as IO
adopt Arcane.OS as OS

// ── onde o dado mora ───────────────────────────────────────
pasta := $"{OS.temp_dir()}/df-estoque-{randint(100000, 999999)}"
IO.mkdir(pasta)
defer:
    IO.remove_tree(pasta)
ARQUIVO := $"{pasta}/estoque.json"

action carregar():
    given not IO.exists(ARQUIVO):
        yield []
    yield Ser.from_json(IO.read(ARQUIVO))

action gravar(itens):
    IO.write(ARQUIVO, Ser.to_json(itens))
    yield len(itens)

itens := carregar()

// ── a tela ─────────────────────────────────────────────────
action tela(t):
    t.titulo("Estoque")

    t.grupo("Entrada")
    nome := t.entrada("Produto", "")
    qtd := t.numero("Quantidade", 1, 1, 9999)
    given t.botao("Adicionar", yes):
        given nome is "":
            t.erro("o produto é obrigatório")
        orif nome in [i["nome"] cycle i in itens]:
            t.erro($"'{nome}' já está no estoque")
        otherwise:
            itens.append({"nome": nome, "qtd": qtd})
            gravar(itens)
            t.aviso($"{nome}: {qtd} em estoque")
    t.fim()

    t.separador()
    t.texto($"{len(itens)} produto(s)")
    t.tabela(["nome", "qtd"], itens)

    given len(itens) > 0 and t.botao("Esvaziar"):
        itens.clear()
        gravar(itens)

// ── rodar ou testar ────────────────────────────────────────
s := J.testar(tela)
s.digitar("Produto", "café")
s.digitar("Quantidade", 12)
s.clicar("Adicionar")
assert s.tem("café: 12 em estoque")

// o duplicado é recusado
s.clicar("Adicionar")
assert s.tem("já está no estoque")
assert len(itens) is 1

// e o arquivo foi gravado
assert IO.exists(ARQUIVO)
assert len(Ser.from_json(IO.read(ARQUIVO))) is 1
out s.texto()''', "lang": "df"},
 {"h2": "As decisões que ela carrega"},
 {"table": {
   "head": ["Decisão", "O que ela evita"],
   "rows": [
     ["o estado mora **fora** da ação de tela", "ele seria recriado a cada reexecução, e a lista ficaria sempre vazia"],
     ["gravar a cada mudança", "fechar a janela perder o trabalho — não há `Ctrl-S` aqui"],
     ["o duplicado é recusado **antes** de gravar", "um arquivo com dois \"café\" e nenhuma forma de saber qual vale"],
     ["a validação devolve `t.erro`, e não levanta", "um erro que fecha a janela no meio do cadastro"],
     ["`defer` na pasta temporária", "lixo em disco a cada execução do exemplo"]]}},
 {"h2": "O que falta para virar produção"},
 {"list": [
   "**Editar e remover** — a tabela é só leitura, e `t.tabela` não tem seleção.",
   "**Desfazer**, que aqui seria uma pilha do estado anterior.",
   "**Gravação atômica**: escrever ao lado e renomear, senão um fechamento no meio da gravação deixa o arquivo pela metade.",
   "**Um banco** em vez de JSON, quando passar de alguns milhares de linhas — `Arcane.Database` está a um `adopt` de distância."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile",
"title": "Android",
"description": "O que funciona hoje, o que não existe, e por que a distinção importa.",
"blocos": [
 {"callout": {"tipo": "atencao", "titulo": "Não há APK", "texto": "Empacotar o interpretador num aplicativo Android exigiria python-for-android ou Chaquopy, e as duas trazem uma cadeia de dependências que a linguagem não tem. Dizer \"dá para fazer app Android\" sem essa distinção seria a documentação mentindo sobre a linguagem."}},
 {"h2": "O que funciona hoje"},
 {"table": {
   "head": ["Caminho", "O que é", "O que custa"],
   "rows": [
     ["**PWA**", "uma aplicação Vitrine ou Kiln que o Android instala na tela inicial", "precisa de HTTPS, e não é app nativo"],
     ["**servidor na rede**", "o programa roda no computador, e o celular abre no navegador", "os dois na mesma rede"],
     ["**Termux**", "o interpretador roda **dentro** do Android", "quem usa precisa instalar o Termux"]]}},
 {"code": '''$ dataforge mobile doctor
$ dataforge mobile pwa --nome="Meu Painel" --em=publico
gerado em publico/
  manifest.json   o que o Android lê para oferecer 'instalar'
  sw.js           o service worker — rede primeiro, cache de reserva
  icone.svg       o ícone''', "lang": "bash"},
 {"h2": "O que o Android exige, sem exceção"},
 {"list": [
   "**HTTPS** — em `http://` ele não oferece instalar (`localhost` é a exceção, para desenvolver).",
   "**O manifesto** com `name`, `icons` e `display: standalone`.",
   "**Um service worker** registrado — é ele que faz o botão \"instalar\" aparecer.",
   "Um ícone de **512×512** com `purpose: maskable`, senão o Android recorta o seu de qualquer jeito."]},
 {"h2": "Rede primeiro, cache de reserva"},
 {"p": "O service worker gerado busca da rede e **só** cai no cache quando ela falha. A estratégia inversa (cache primeiro) é mais rápida e faz um painel mostrar dado velho sem avisar — o que é pior que dizer \"sem conexão\"."},
 {"code": '''adopt Arcane.Vitrine as V

// Um painel da Vitrine é o que vira PWA: ele já é uma página, já
// responde no celular, e o manifesto só acrescenta o "instalar".
action pagina():
    V.titulo("Estoque")
    V.metrica("Produtos", 42)
    V.frame([{"nome": "café", "qtd": 12}])

s := V.testar(pagina)
s.rodar()
assert "Estoque" in s.texto()
out "o mesmo painel vira app instalável"''', "lang": "df"},
 {"h2": "O que NÃO existe"},
 {"list": [
   "**APK**, e publicação na Play Store.",
   "**Widget nativo** (Material, Compose).",
   "**Câmera, GPS e notificação nativas** pelo DataForge — o PWA alcança parte disso pelo navegador, com a permissão do usuário.",
   "**iOS**: o Safari instala PWA na tela inicial, com limites maiores (sem notificação push confiável, e o service worker é descartado com mais frequência)."]},
 {"h2": "A decisão, escrita"},
 {"p": "Um APK que empacota o CPython é possível e custa a promessa central do projeto: **zero dependência**. O PWA entrega o caso de uso real — uma ferramenta interna no celular de quem trabalha — sem quebrar nada. Quando o caso for um app de loja, com widget nativo e notificação, a resposta honesta é que esta linguagem não é a ferramenta."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/mobile/pwa",
"title": "Um PWA passo a passo",
"description": "Do painel da Vitrine ao ícone na tela inicial do Android.",
"blocos": [
 {"p": "O caminho inteiro tem quatro passos, e três deles são do Android — não da linguagem."},
 {"h2": "1. O painel"},
 {"code": '''adopt Arcane.Vitrine as V

action pagina():
    V.titulo("Chão de fábrica")
    colunas := V.colunas(2)
    colunas[0].metrica("Em produção", 12)
    colunas[1].metrica("Parados", 3)
    V.frame([
        {"maquina": "prensa 1", "estado": "ok"},
        {"maquina": "prensa 2", "estado": "parada"},
    ])
    V.atualizar_a_cada(5)

s := V.testar(pagina)
s.rodar()
assert "Chão de fábrica" in s.texto()
out "o painel responde — e é o mesmo no celular"''', "lang": "df"},
 {"h2": "2. Os arquivos do PWA"},
 {"code": '''$ dataforge mobile pwa --nome="Chão de fábrica" --em=publico''', "lang": "bash"},
 {"h2": "3. O HTML"},
 {"code": '''<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0d1017">
<script>navigator.serviceWorker?.register('/sw.js')</script>''', "lang": "text"},
 {"h2": "4. O HTTPS"},
 {"p": "Sem ele o Android **não oferece instalar**, e não há aviso: o botão simplesmente não aparece. As três formas que funcionam:"},
 {"table": {
   "head": ["Forma", "Quando"],
   "rows": [
     ["um proxy com certificado (nginx, Caddy)", "o painel roda na sua rede, e você controla o servidor"],
     ["um túnel (Cloudflare, ngrok)", "para mostrar a alguém hoje"],
     ["hospedagem estática + API", "quando a página é estática e o dado vem por HTTP"]]}},
 {"p": "O Kiln **não tem TLS** — ele roda sobre o `http.server` do Python. Em produção pública, o nginx ou o Caddy vai na frente, e isso está escrito na página dele também."},
 {"h2": "Conferir que ficou instalável"},
 {"list": [
   "Abra no Chrome do Android e veja se aparece \"Adicionar à tela inicial\" **com ícone próprio** (sem manifesto, ele oferece um atalho comum).",
   "Nas Ferramentas do Desenvolvedor: **Application → Manifest** e **Service Workers**.",
   "Desligue a rede e recarregue: com o service worker, a página abre; sem ele, dá erro de conexão.",
   "Instale, abra pelo ícone, e confira que **não há barra de endereço** — é o `display: standalone` funcionando."]},
 {"callout": {"tipo": "nota", "titulo": "Atualizar um PWA instalado", "texto": "O service worker gerado troca o cache pelo nome (`nome-vN`) e chama `skipWaiting`. Sem mudar a versão, o Android continua servindo o cache antigo — e o sintoma é \"publiquei e não mudou nada\", que faz perder uma tarde."}},
]},
]
