# -*- coding: utf-8 -*-
"""Posse — seis páginas novas: o arquivo e o soquete, contagem
determinística, referência fraca, o que o `check` prova, pool de
recursos, e a leitura para quem vem de Rust ou de C++.

Todo bloco roda.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/memoria/posse/recursos",
"title": "O arquivo, o soquete e a conexão",
"description": "O que a posse protege num mundo com coletor — e o que ela não protege.",
"blocos": [
 {"p": "A primeira coisa a dizer, porque ela evita a leitura errada de tudo o mais: **num mundo com coletor, a memória nunca esteve em risco**. O que `Arcane.Posse` protege é o **protocolo** de um recurso — soltar uma vez, não usar depois de soltar, não escrever no meio de uma leitura."},
 {"table": {
   "head": ["O problema", "Sem posse", "Com posse"],
   "rows": [
     ["usar depois de fechar", "erro do sistema operacional, três camadas longe", "`PosseMovidaError`, na linha que usou"],
     ["fechar duas vezes", "erro, ou pior: fecha o descritor de outro", "`soltar` é idempotente"],
     ["esquecer de fechar", "o arquivo fica aberto até o processo morrer", "o escopo solta, e o `check` avisa"],
     ["dois donos do mesmo arquivo", "quem fecha primeiro estraga o outro", "há **um** dono, e mover é explícito"]]}},
 {"code": '''adopt Arcane.Posse as Posse

// O dono carrega o valor E o que fazer ao soltar.
fechados := []
arquivo := Posse.dono({"nome": "dados.csv"},
                      lambda v => fechados.append(v["nome"]),
                      "arquivo")

// Usar é sempre por dentro de uma ação: não há como guardar a
// referência crua e usá-la depois de soltar.
assert arquivo.usar(lambda v => v["nome"]) is "dados.csv"
assert arquivo.vivo() is yes

arquivo.soltar()
assert fechados is ["dados.csv"]
assert arquivo.solto() is yes

// E soltar de novo NÃO é erro.
assert arquivo.soltar() is no''', "lang": "df"},
 {"h2": "Por que `soltar` é idempotente"},
 {"p": "Um `close()` escrito no `defer` **e** no caminho de erro é a forma mais comum de fechar recurso — e se o segundo `soltar` levantasse, a disciplina atrapalharia em vez de ajudar. A regra: soltar é pedir um **estado final**, e nesse ponto já não importa se ele já estava lá."},
 {"h2": "Usar depois de soltar é erro, e o erro diz onde"},
 {"code": '''adopt Arcane.Posse as Posse

conexao := Posse.dono({"banco": "loja"})
conexao.soltar()

monitor:
    conexao.usar(lambda v => v["banco"])
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"h2": "O de fora solta o que possuía"},
 {"p": "Um dono que guarda outro dono precisa soltá-lo — é a *drop glue*. Sem isso, soltar o de fora deixaria o de dentro aberto, que é exatamente o vazamento que a peça existe para evitar:"},
 {"code": '''adopt Arcane.Posse as Posse

soltos := []

action abrir(nome):
    yield Posse.dono({"nome": nome}, lambda v => soltos.append(v["nome"]), nome)

// Um 'Escopo' guarda vários, e solta todos na ordem inversa da
// abertura — como a pilha de um bloco.
escopo := Posse.escopo()
escopo.guardar(abrir("conexao"))
escopo.guardar(abrir("transacao"))
escopo.guardar(abrir("arquivo"))
assert escopo.quantos() is 3

escopo.soltar()
assert soltos is ["arquivo", "transacao", "conexao"]
out soltos''', "lang": "df"},
 {"p": "A ordem inversa não é estética: a transação foi aberta **sobre** a conexão, e fechar a conexão primeiro deixaria a transação sem onde confirmar."},
 {"h2": "E o `defer`, que já existia"},
 {"table": {
   "head": ["", "`defer`", "`Posse`"],
   "rows": [
     ["quando roda", "na saída da **ação**", "quando o dono é solto, ou o escopo fecha"],
     ["quem garante", "o interpretador", "quem escreveu"],
     ["protege de usar depois", "não", "**sim** — e é a diferença que importa"],
     ["atravessa fronteira", "não", "sim: o dono pode ser movido"],
     ["custo para quem não usa", "zero", "zero"]]}},
 {"p": "Os dois convivem, e o mais comum é usar `defer` para o caso simples e `Posse` quando o recurso **atravessa** — vai para dentro de uma estrutura, é devolvido por uma ação, ou tem mais de um candidato a dono."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/memoria/posse/mover",
"title": "Mover, emprestar e copiar",
"description": "As três formas de passar um recurso adiante — e o que cada uma promete.",
"blocos": [
 {"p": "Passar um recurso para outra parte do programa tem três significados diferentes, e confundi-los é de onde vem quase todo bug de recurso."},
 {"table": {
   "head": ["", "O que acontece", "Quem fecha"],
   "rows": [
     ["**mover**", "o dono antigo perde o valor", "o novo dono"],
     ["**emprestar**", "o outro usa, e devolve", "o dono, como antes"],
     ["**copiar**", "há dois valores independentes", "cada um o seu"]]}},
 {"code": '''adopt Arcane.Posse as Posse

original := Posse.dono({"id": 1}, void, "sessao")
novo := original.mover()

// O antigo perdeu: usá-lo é erro, e o erro diz que foi movido.
assert original.movido() is yes
assert novo.usar(lambda v => v["id"]) is 1

monitor:
    original.usar(lambda v => v["id"])
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"h2": "Emprestar, e o `com` que SOLTA"},
 {"p": "Duas peças parecidas com propósitos diferentes, e trocá-las é o erro mais comum desta área:"},
 {"table": {
   "head": ["", "`d.usar(acao)`", "`Posse.com(d, acao)`"],
   "rows": [
     ["o que faz", "empresta para **ler**, e devolve", "usa e **solta** no fim"],
     ["o dono depois", "continua vivo", "**solto**"],
     ["equivale a", "um empréstimo", "o `defer` aplicado a um dono"],
     ["quando", "no meio do trabalho", "na última vez que se usa aquele recurso"]]}},
 {"code": '''adopt Arcane.Posse as Posse

// 'usar' empresta e devolve: o dono continua vivo.
d := Posse.dono([1, 2, 3])
assert d.usar(lambda v => len(v)) is 3
assert d.vivo() is yes
assert Posse.estado(d)["emprestimos"] is 0
d.soltar()

// 'com' é RAII: ele usa e SOLTA — inclusive quando o corpo falha,
// que é justamente o caminho por onde metade dos recursos vaza.
soltos := []
d2 := Posse.dono([1, 2], lambda v => soltos.append("fechou"))
assert Posse.com(d2, lambda v => len(v)) is 2
assert d2.solto() is yes
assert soltos is ["fechou"]

// E com erro no meio, ele solta do mesmo jeito.
d3 := Posse.dono([1], lambda v => soltos.append("fechou 3"))
monitor:
    Posse.com(d3, lambda v => 1 / 0)
handle Error:
    out "a ação falhou…"
assert d3.solto() is yes
assert soltos is ["fechou", "fechou 3"]''', "lang": "df"},
 {"h2": "Não se escreve no meio de uma leitura"},
 {"p": "É a regra que dá nome à disciplina: enquanto há um empréstimo de leitura vivo, um empréstimo **exclusivo** é recusado. Sem isso, a coleção muda debaixo de quem a percorre — e o sintoma é um item pulado, não um erro."},
 {"code": '''adopt Arcane.Posse as Posse

cel := Posse.celula([1, 2, 3])

// Ler e escrever recebem uma AÇÃO, e é isso que dá o escopo: o valor
// não escapa, e a exclusividade vale só enquanto a ação roda.
assert cel.ler(lambda v => len(v)) is 3

// O que a ação devolve passa a ser o valor — inclusive num número ou
// num texto, onde não há como mexer no lugar.
cel.escrever(lambda v => [...v, 4])
assert cel.ler(lambda v => len(v)) is 4

contador := Posse.celula(10)
contador.escrever(lambda v => v + 1)
assert contador.ler(lambda v => v) is 11

// 'trocar' devolve o anterior e põe o novo, sem janela entre os dois.
antigo := cel.trocar([9])
assert len(antigo) is 4
assert cel.ler(lambda v => v[0]) is 9''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Uma escrita que não escrevia", "texto": "`escrever` entregava o valor para a ação mexer **no lugar** e descartava o retorno. Num cluster isso funciona por acidente; num número, `escrever(lambda v => v + 1)` não escrevia nada — e o programa seguia com o valor velho, calado. Hoje o retorno é guardado, e devolver `void` continua sendo mexer no lugar."}},
 {"h2": "Copiar é RASA, e isso importa"},
 {"p": "`copiar()` devolve **outro dono do mesmo valor** — é a cópia rasa. Os dois podem soltar sem erro (soltar é idempotente), mas o valor lá dentro continua sendo um só:"},
 {"code": '''adopt Arcane.Posse as Posse

d := Posse.dono({"itens": [1, 2]})
c := d.copiar()

// Dois DONOS, um valor: mexer por um aparece no outro.
c.mudar(lambda v => {"itens": [...v["itens"], 3]})
assert c.usar(lambda v => len(v["itens"])) is 3
assert d.usar(lambda v => len(v["itens"])) is 2   // o 'd' guarda o antigo

// Para dois valores de verdade, copie o VALOR, e não o dono:
adopt Arcane.Objetos as Obj
outro := Posse.dono(Obj.clonar_fundo(d.usar(lambda v => v)))
outro.mudar(lambda v => {"itens": [...v["itens"], 9]})
assert d.usar(lambda v => len(v["itens"])) is 2''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Copiar um recurso quase nunca é o que se quer", "texto": "Copiar um **valor** é barato e seguro. Copiar um dono de arquivo aberto dá dois objetos que apontam para o mesmo descritor, e aí os dois vão fechá-lo. Por isso a cópia é explícita, e não o padrão: o padrão é mover."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/memoria/posse/compartilhado",
"title": "Compartilhado, contagem e referência fraca",
"description": "Quando há mais de um dono legítimo — e o ciclo que a contagem não resolve.",
"blocos": [
 {"p": "Um dono só nem sempre é possível: um cache, um pool e um barramento de eventos têm **vários** interessados no mesmo objeto, e nenhum deles sabe quem é o último a sair. A contagem responde isso — e ela é **determinística**, diferente do coletor."},
 {"code": '''adopt Arcane.Posse as Posse

soltos := []
c := Posse.compartilhado({"conexao": 1}, lambda v => soltos.append("fechou"))
assert c.contar() is 1

// Cada 'clonar' é mais um dono.
b := c.clonar()
d := c.clonar()
assert c.contar() is 3

// E o recurso só fecha quando o ÚLTIMO sai.
c.soltar()
b.soltar()
assert soltos is []
d.soltar()
assert soltos is ["fechou"]''', "lang": "df"},
 {"p": "\"Determinística\" é a palavra que importa: o fechamento acontece **na linha do último `soltar`**, e não quando o coletor decidir passar. Para um arquivo, isso é a diferença entre um descritor liberado agora e um liberado daqui a um minuto."},
 {"h2": "A referência fraca não conta"},
 {"code": '''adopt Arcane.Posse as Posse

c := Posse.compartilhado({"x": 1})
f := Posse.fraco(c)

// A fraca NÃO segura o recurso vivo.
assert c.contar() is 1
assert f.vivo() is yes

// 'promover' devolve um dono de verdade — ou void, se já foi.
forte := f.promover()
assert forte is not void
assert c.contar() is 2
forte.soltar()

c.soltar()
assert f.vivo() is no
assert f.promover() is void''', "lang": "df"},
 {"h2": "Para que serve a fraca"},
 {"table": {
   "head": ["Caso", "Por que fraca"],
   "rows": [
     ["um **cache** de objetos", "o cache não pode ser a razão de nada continuar vivo"],
     ["o **filho que aponta para o pai**", "forte nos dois sentidos é um ciclo, e o ciclo nunca zera"],
     ["um **observador**", "quem observa não deveria impedir o observado de sumir"],
     ["um **índice** por id", "ele é uma conveniência, não um dono"]]}},
 {"h2": "O ciclo, que é o que a contagem não resolve"},
 {"code": '''adopt Arcane.Posse as Posse

// Pai e filho apontando um para o outro com FORTE: a contagem de
// nenhum dos dois chega a zero, e o recurso nunca fecha.
pai := Posse.compartilhado({"nome": "pai"})
filho := Posse.compartilhado({"nome": "filho"})

// A saída: um dos lados é fraco. Aqui, o filho→pai.
fraca_para_o_pai := Posse.fraco(pai)
assert pai.contar() is 1              // a fraca não somou

pai.soltar()
assert fraca_para_o_pai.vivo() is no  // e o pai pôde sair
filho.soltar()
out "sem ciclo: o lado de volta é fraco"''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "O coletor do Python continua lá", "texto": "Ele é quem resolve o ciclo que escapa — e `Arcane.Memoria` deixa medi-lo e controlá-lo. A contagem daqui não substitui o coletor: ela dá **momento** ao fechamento de um recurso, que é outra promessa. Confundir as duas é o erro mais comum ao ler esta parte."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/memoria/posse/analise",
"title": "O que o `check` prova",
"description": "Três diagnósticos, e — mais importante — os quatro silêncios.",
"blocos": [
 {"p": "O analisador acusa uso depois de mover, recurso que não é solto e empréstimo que escapa. Como em todo o resto da linguagem, **o que o faz calar é tão importante quanto o que o faz falar**."},
 {"table": {
   "head": ["Código", "Severidade", "O quê"],
   "rows": [
     ["`posse-movida`", "**erro**", "usar um dono depois de `mover()` — é provável em um arquivo só"],
     ["`recurso-vazado`", "aviso", "um dono criado e nunca solto naquele caminho"],
     ["`emprestimo-escapa`", "aviso", "o valor emprestado é guardado fora do escopo do empréstimo"]]}},
 {"p": "Os dois últimos são **aviso**, e por um motivo: a análise vê **um arquivo**, e o recurso pode ser solto por um caminho que ela não enxerga — passado para uma ação de outro módulo, guardado num escopo que fecha depois. Um erro ali reprovaria código correto."},
 {"h2": "Os quatro silêncios"},
 {"table": {
   "head": ["Ele cala quando", "Porque"],
   "rows": [
     ["o nome **não nasceu** de `Arcane.Posse`", "o exercício 118 tem um `mover()` de máquina de estados, e a primeira versão o acusou"],
     ["você **pergunta o estado** (`movido`, `vivo`, `contar`)", "`assert a.movido()` depois do `mover` é justamente o que se escreve"],
     ["o dono é **devolvido** pela ação", "quem recebe passa a ser o dono, e o arquivo não vê isso"],
     ["o dono entra num **escopo**", "o escopo solta, e ele pode fechar em outro lugar"]]}},
 {"code": '''adopt Arcane.Posse as Posse

// Perguntar o estado é sempre legítimo — inclusive depois de mover.
d := Posse.dono({"x": 1})
novo := d.mover()
assert d.movido() is yes
assert novo.vivo() is yes

// E devolver o dono é o padrão de uma fábrica de recurso: quem
// chamou vira o dono, e o 'check' não acusa vazamento aqui.
action abrir_conexao(nome):
    yield Posse.dono({"nome": nome}, lambda v => void, nome)

c := abrir_conexao("loja")
assert c.usar(lambda v => v["nome"]) is "loja"
c.soltar()''', "lang": "df"},
 {"h2": "Silenciar de propósito"},
 {"p": "Quando o analisador está certo e o código também — um recurso solto por um caminho que ele não vê —, a saída é **nomear** a regra:"},
 {"code": '''adopt Arcane.Posse as Posse

action guardar_em_algum_lugar(d):
    yield d

d := Posse.dono({"x": 1})       // df: permitir recurso-vazado
guardar_em_algum_lugar(d)
out "o dono foi adiante, e quem recebe solta"''', "lang": "df"},
 {"p": "A regra tem de ser **nomeada**: um `permitir` solto esconderia o erro seguinte, que ninguém pediu para esconder. Um analisador sem escape obriga a escolher entre conviver com um alarme e desligar a verificação inteira — e a segunda é o que acontece."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/memoria/posse/pool",
"title": "Um pool de recursos",
"description": "O caso que junta tudo: emprestar, devolver, e o que acontece quando ninguém devolve.",
"blocos": [
 {"p": "Um pool é o exemplo canônico de posse: o recurso **pertence** ao pool, quem usa **empresta**, e devolver não é opcional — um empréstimo que não volta é uma conexão a menos, para sempre."},
 {"code": '''adopt Arcane.Posse as Posse

blueprint Pool:
    action setup(quantas):
        self.livres := []
        self.emprestadas := 0
        self.criadas := 0
        cycle i from 1 to quantas:
            self.criadas := self.criadas + 1
            self.livres.append({"id": self.criadas})

    action com(acao):
        given len(self.livres) is 0:
            trigger "o pool acabou — todas as conexões estão emprestadas"
        conexao := self.livres.pop(len(self.livres) - 1)
        self.emprestadas := self.emprestadas + 1
        // O 'defer' é o que torna a devolução impossível de esquecer:
        // ele roda mesmo quando a ação falha no meio.
        defer:
            self.livres.append(conexao)
            self.emprestadas := self.emprestadas - 1
        yield acao(conexao)

p := spawn Pool(2)
assert p.com(lambda c => c["id"]) is 2
assert len(p.livres) is 2          // devolvida

// E mesmo quando o corpo falha:
monitor:
    p.com(lambda c => 1 / 0)
handle Error:
    out "a ação falhou"
assert len(p.livres) is 2
assert p.emprestadas is 0
out "devolvida mesmo com erro"''', "lang": "df"},
 {"h2": "O que acontece quando o pool acaba"},
 {"code": '''adopt Arcane.Posse as Posse

blueprint Pool:
    action setup(quantas):
        self.livres := [{"id": i} cycle i in range(1, quantas + 1)]

    action pegar():
        given len(self.livres) is 0:
            // Falhar RÁPIDO é melhor que esperar para sempre: uma
            // espera sem prazo vira um travamento sem mensagem, e
            // ninguém consegue distinguir isso de rede lenta.
            trigger "pool esgotado: aumente o tamanho ou reduza o tempo de uso"
        yield self.livres.pop(0)

p := spawn Pool(1)
primeira := p.pegar()

monitor:
    p.pegar()
    assert no
handle Error as e:
    out e.message''', "lang": "df"},
 {"h2": "As quatro decisões de um pool"},
 {"table": {
   "head": ["Decisão", "Sem ela"],
   "rows": [
     ["devolver no `defer`", "uma falha no meio come uma conexão por vez, até o pool acabar"],
     ["falhar quando esgota, com prazo", "espera infinita — e um travamento sem mensagem"],
     ["um **teto**, e não crescer sem limite", "o pool vira um jeito elaborado de abrir conexão demais no banco"],
     ["conferir a conexão ao devolver", "uma conexão morta volta para o pool e quebra o próximo"]]}},
 {"h2": "E o pool de processos, que já existe"},
 {"p": "Para trabalho de CPU, a linguagem já traz um: `P.pool_processos()` paga a partida **uma vez** — medido, 180 ms na primeira chamada e 82 ms na segunda. O `fechar()` é explícito porque o contrário deixa processos ociosos vivos."},
 {"code": '''adopt Arcane.Concurrent as C

pool := C.pool_processos()
defer:
    pool.fechar()

assert pool is not void
out "o pool sobrevive entre chamadas — e o fechar é explícito"''', "lang": "df"},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/memoria/posse/de-rust-e-cpp",
"title": "De Rust e de C++ para cá",
"description": "O que traduz, o que não traduz, e o que aqui é desnecessário.",
"blocos": [
 {"p": "Quem vem de Rust ou de C++ reconhece os nomes, e a tradução é útil — desde que venha com a diferença que mais importa: **aqui há um coletor**, e por isso a posse é uma disciplina de **recurso**, não uma garantia de memória."},
 {"table": {
   "head": ["Rust / C++", "DataForge", "Diferença"],
   "rows": [
     ["`Box<T>` / `unique_ptr`", "`Posse.dono(valor)`", "checado em execução, e no `check` do arquivo"],
     ["`Rc<T>` / `shared_ptr`", "`Posse.compartilhado(valor)`", "igual, e a contagem também é determinística"],
     ["`Weak<T>` / `weak_ptr`", "`Posse.fraco(compartilhado)`", "igual"],
     ["`&T`", "`Posse.com(d, acao)`", "o escopo é a ação, e não um tempo de vida no tipo"],
     ["`&mut T`", "`Posse.celula`", "exclusividade conferida em execução"],
     ["`Drop`", "o `ao_soltar` do dono", "igual, e também roda no escopo"],
     ["RAII", "`defer` e `Posse.escopo`", "o `defer` é da **ação**, não do bloco"],
     ["*borrow checker*", "`dataforge check`", "prova o que dá num arquivo; o resto é execução"],
     ["*lifetime* no tipo", "**não existe**", "e é a ausência que mais se nota"]]}},
 {"h2": "O que aqui é desnecessário"},
 {"list": [
   "**Anotar tempo de vida.** Nada aqui devolve uma referência que pode sobreviver ao dono: `usar` e `com` recebem uma ação, e o valor não escapa por construção.",
   "**`clone()` por toda parte.** O coletor resolve o compartilhamento de leitura; `clonar` é sobre **quem fecha**, e não sobre quem lê.",
   "**`unsafe`.** Não há o que desligar: a integridade da memória não depende desta camada.",
   "**Mover por padrão.** Aqui o padrão é passar a referência; mover é um pedido explícito, porque quase nunca é o que se quer."]},
 {"h2": "E o que é mais fraco, dito sem rodeio"},
 {"table": {
   "head": ["Em Rust", "Aqui"],
   "rows": [
     ["o compilador **prova**, e o programa não compila", "o `check` prova o que dá num arquivo; o resto falha em execução"],
     ["a regra vale para todo valor", "vale para o que nasceu de `Arcane.Posse`"],
     ["custo zero em execução", "custo pequeno, mas real: um objeto por recurso"],
     ["`Send`/`Sync` no tipo", "não há — a travessia de processo confere na hora de atravessar"]]}},
 {"code": '''adopt Arcane.Posse as Posse

// O que Rust escreveria com tempo de vida, aqui é escopo de ação:
// o valor emprestado NÃO escapa, porque não há como devolvê-lo.
d := Posse.dono([1, 2, 3])

// Isto lê e devolve um DADO, não a referência:
tamanho := Posse.com(d, lambda v => len(v))
assert tamanho is 3

// Mesmo devolvendo o próprio valor, o dono continua sendo o dono, e
// soltar continua fechando na hora certa.
d.soltar()
assert d.solto() is yes''', "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "Quando NÃO usar posse", "texto": "Para um arquivo aberto e fechado na mesma ação, `defer` basta e é mais curto. A posse ganha quando o recurso **atravessa**: vai para dentro de uma estrutura, é devolvido por uma ação, ou tem mais de um candidato a dono. Usá-la em tudo é o mesmo erro de anotar tipo em tudo."}},
]},
]
