"""O ecossistema conferido, os princípios medidos, as tensões e o percurso.

Partes 20, 21 e 22 da referência Deep Tech — as três que fecham o
documento, e as três que um projeto costuma escrever como prosa.

Todo bloco `df` destas páginas RODA (`tests/test_ecossistema.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/componentes",
"title": "O ecossistema, conferido",
"description": "O inventário da implementação com uma marca por componente — e uma conferência nas duas direções, para que o mapa não possa mentir.",
"blocos": [
 {"p": "A referência fecha com um desenho do ecossistema: `dfc` com onze fases, `dfup`, `dfpm`, um runtime de seis peças, sete ferramentas e oito alvos."},
 {"p": "Um desenho desses é o texto mais fácil de escrever num projeto — e o mais fácil de deixar envelhecer. Ele não roda, ninguém o executa, e no dia em que uma peça muda de nome o mapa passa a mentir **sem nada denunciar**."},
 {"callout": {"tipo": "nota", "titulo": "Este repositório já pagou por isso", "texto": "A tabela da biblioteca padrão esteve escrita em **três lugares**, e os três divergiram. Uma contagem de símbolos voltou a ficar errada depois de corrigida, porque alguém editou o `.tsx` gerado em vez da fonte. Um mapa do ecossistema escrito à mão seria a quarta cópia."}},

 {"h2": "As três marcas"},
 {"p": "Cada componente do desenho carrega **um de três estados**, e o terceiro é o que dá valor ao mapa:"},
 {"table": {"head": ["Marca", "Estado", "Quer dizer"], "rows": [
   ["`[+]`", "`existe`", "a peça está aqui, com esse papel"],
   ["`[~]`", "`equivale`", "não há essa peça; há **outra** que responde a mesma pergunta por outro mecanismo — nomeada, com o porquê"],
   ["`[-]`", "`nao-existe`", "não há, e o motivo está escrito"]]}},
 {"p": "A lista é fechada de propósito. Um quarto estado seria o lugar onde \"mais ou menos\" se esconderia — e é exatamente o que se quer não ter num inventário."},
 {"code": """dataforge ecossistema              # o inventario inteiro
dataforge ecossistema --ausencias  # so o que nao existe, e o motivo
dataforge ecossistema --json       # para o CI ler""", "lang": "bash"},

 {"h2": "A conferência nas duas direções"},
 {"p": "O que impede o mapa de envelhecer não é cuidado de quem escreve: é `conferir()`, e ele cobra **duas** coisas."},
 {"table": {"head": ["Direção", "O que cobra", "O que impede"], "rows": [
   ["`faltando`", "todo caminho citado no mapa existe no disco", "a peça foi renomeada e o mapa continua apontando para o nome antigo"],
   ["`orfaos`", "todo módulo de `dataforge/` aparece em algum componente", "um módulo novo nasce **fora** do mapa, e o inventário fica incompleto em silêncio"]]}},
 {"callout": {"tipo": "atencao", "titulo": "A segunda é a que importa, e foi ela que pegou o primeiro erro", "texto": "A primeira versão deste mapa citava `dataforge/stdlib/arcane_concurrent.py` em dois componentes. O arquivo se chama `arcane_paralelo.py` — a classe é que se chama `ArcaneConcurrent`. `conferir()` acusou os dois antes de qualquer teste existir. Sem ele, o mapa teria nascido mentindo em dois pontos."}},
 {"code": """adopt Arcane.Ecossistema as Eco

n := Eco.numeros()
assert n["componentes"] bigger 30
assert n["nao_existem"] bigger 0

c := Eco.conferir()
assert c["ok"] is yes
assert len(c["faltando"]) is 0
assert len(c["orfaos"]) is 0
out $"{n['componentes']} componentes, {c['citados']} caminhos conferidos\"""", "lang": "df"},
 {"p": "O comando **sai com 1** quando o mapa e o disco discordam. É o que faz um CI reprovar um inventário que passou a mentir — a mesma escolha do `dataforge abi`, que sai com 2 quando o contrato quebra."},

 {"h2": "Os grupos, e o que há em cada um"},
 {"p": "O `dfc` do desenho não é um binário separado aqui: o driver é o próprio `dataforge`, e **cada fase tem um comando que a mostra** — `tokens`, `ast`, `ir`, `percurso`."},
 {"table": {"head": ["Grupo", "O que existe", "O que não"], "rows": [
   ["`dfc`", "lexer, parser, AST, HIR, verificador de tipos, MIR, dataflow, SSA, LIR", "backend LLVM e gerador de código de máquina"],
   ["`dfup`", "os instaladores, e `dataforge version`", "**gerenciador de versões**: não há como manter duas lado a lado nem fixar por projeto"],
   ["`dfpm`", "resolver com semver, `forge.lock`, integridade, empacotar, publicar", "workspace com várias peças resolvidas de uma vez"],
   ["Runtime", "escalonador, laço de eventos, async, threads, processos, erros", "alocador próprio e runtime bare-metal"],
   ["Tooling", "LSP, **depurador**, formatador, linter, testes, bench, profiler, doc", "— (o depurador é a peça que o desenho do documento não lista)"],
   ["Interop", "FFI para C, ponte para o Python, `Arcane.Abi`", "— (o layout binário não existe, e o **problema** dele existe)"],
   ["Alvos", "Linux, macOS, Windows, ARM, ARM64", "bare-metal; e WASM só na direção \"rodar em\""]]}},
 {"p": "As peças que **faltam no desenho** também estão no mapa, e a mais importante é o `Execution Engine`: o desenho supõe compilação antecipada, e por isso não tem onde pôr o interpretador. Aqui ele é o centro."},

 {"h2": "Os números saem do mesmo lugar que os publica"},
 {"p": "`numeros()` não tem um único valor escrito à mão. A contagem de símbolos usa o **mesmo levantamento** que gera a página da biblioteca."},
 {"callout": {"tipo": "perigo", "titulo": "Uma soma própria já divergiu em 112 símbolos", "texto": "Uma contagem ingênua sobre `DESCRICOES` discordou de `gerar_pagina_biblioteca.py`, que é o gerador canônico — e o número errado foi publicado no site. Duas fontes para o mesmo número é uma fonte a mais do que se pode manter."}},
 {"code": """adopt Arcane.Ecossistema as Eco

n := Eco.numeros()
// tudo derivado: nada aqui e escrito a mao
assert n["modulos"] bigger 60
assert n["simbolos"] bigger 1800
assert n["comandos"] bigger 40
assert n["existem"] + n["equivalem"] + n["nao_existem"] is n["componentes"]
out $"{n['modulos']} modulos, {n['simbolos']} simbolos, {n['comandos']} comandos\"""", "lang": "df"},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/ausencias",
"title": "O que não existe, e o que está no lugar",
"description": "Sete componentes do desenho não existem. Cada um com o que faz a diferença: o motivo, o que responde pela mesma pergunta, e o número medido do substituto.",
"blocos": [
 {"p": "Esta é a página que uma referência técnica quase nunca tem, e é a mais útil de todas: **o que a linguagem não faz.**"},
 {"p": "Um mapa que marca tudo como pronto não é um mapa, é publicidade. Quem o lê descobre a ausência ao tentar — no pior momento, e depois de ter escolhido a linguagem por causa dele."},
 {"callout": {"tipo": "nota", "titulo": "A regra que este repositório segue", "texto": "Nomear a ausência **com o motivo** e, quando houver, com o número medido do que está no lugar. Publicar o número mesmo quando ele é decepcionante: a otimização que rendeu 1,01×, o laço de eventos que ficou em ~1,1× a versão com threads. Um número ruim publicado vale mais que um bom prometido."}},

 {"h2": "Backend LLVM, e gerador de código"},
 {"p": "As duas maiores ausências, e são a mesma: **não há compilação para código de máquina.**"},
 {"table": {"head": ["No desenho", "Aqui", "Medido"], "rows": [
   ["`LLVM Backend`", "`compilador.py` — a árvore é percorrida uma vez e vira fechamentos Python, o que tira o despacho do caminho quente", "**1,5× a 1,8×** conforme a carga"],
   ["`Code Generator`", "não há. O que sai do compilador é um fechamento, e quem o executa é `interpreter.py`", "—"],
   ["`Machine Code / WASM`", "não há. O artefato é a árvore compilada, em memória", "—"]]}},
 {"p": "O motivo não é falta de tempo. Amarrar o LLVM tiraria **a única propriedade inegociável do projeto**: zero dependência externa no runtime. E o teto desta técnica é conhecido."},
 {"callout": {"tipo": "atencao", "titulo": "O teto é ~6,5×, e ele não é do compilador de fechamentos", "texto": "É o teto de **qualquer** técnica que fique dentro do Python — inclusive uma VM de bytecode escrita em Python. O resto exigiria sair do CPython, que é outra linguagem de implementação, não outra fase do compilador. Dizer \"ainda não temos backend\" sugeriria que ele vem depois; a verdade é que ele é uma decisão de arquitetura, e ela está tomada."}},
 {"p": "A fase continua **no mapa**, marcada como ausente. Uma fase apagada do desenho não deixa a ausência aparecer — e é em `dataforge ir --fase=lir` que ela fica visível, porque o LIR mostra o que desceu para fechamento e o que **recuou** para a árvore."},

 {"h2": "Gerenciador de versões"},
 {"p": "O desenho tem `dfup`. Aqui não há nada equivalente, e **esta é uma ausência de verdade** — não um mecanismo diferente com o mesmo efeito."},
 {"table": {"head": ["O que o rustup faz", "Aqui"], "rows": [
   ["instalar várias versões lado a lado", "não há"],
   ["alternar a versão ativa", "não há: trocar de versão é reinstalar"],
   ["fixar a versão por projeto", "não há no `forge.toml`"],
   ["dizer qual está ativa", "`dataforge version`"]]}},
 {"p": "Quem precisa disso hoje usa um `venv` por projeto e `pip install dataforge-lang==<versao>`. Os instaladores criam uma venv em `~/.dataforge`, que não toca no Python do sistema e não pede sudo."},
 {"callout": {"tipo": "dica", "titulo": "E há uma armadilha real nisso", "texto": "Há **três** lugares onde o DataForge pode estar instalado — o `.venv` do repositório, `~/.dataforge` e o Python do sistema. Uma cópia antiga no PATH produz erros que não existem no código: foi assim que um `LexError: Unexpected character: '$'` apareceu num arquivo que usava interpolação normalmente. Sem gerenciador de versões, essa confusão é por conta de quem instala."}},

 {"h2": "Workspace"},
 {"p": "Um comando que resolva a árvore de vários pacotes de uma vez não existe. Cada pacote tem o seu `forge.toml`, e os quatro pacotes deste repositório são mantidos assim."},
 {"p": "`dataforge new` cria projeto a partir de 9 modelos, e **todo projeto criado passa nos próprios testes** — o que resolve a partida, não a manutenção de um monorepo."},

 {"h2": "Alocador"},
 {"p": "O alocador é o do CPython, e trocá-lo exigiria estar do lado de fora dele. O que se pode fazer daqui — e se faz — é **mandar no coletor** e medir a pausa dele."},
 {"table": {"head": ["O que existe", "Onde"], "rows": [
   ["arena: alocar em bloco e soltar de uma vez", "`Arcane.Memoria.Arena`"],
   ["ligar, desligar e rodar sem coletor num trecho", "`gc_ligar`, `gc_desligar`, `sem_gc`"],
   ["mudar os limiares das três gerações", "`gc_limiares`, `gc_geracoes`"],
   ["congelar o que já existe, para não ser varrido de novo", "`gc_congelar`"],
   ["**medir a pausa** de cada coleta", "`Arcane.Perfil.gc_pausas`"],
   ["referência fraca e mapa fraco", "`Arcane.Memoria`"]]}},
 {"p": "A diferença entre \"controlar memória\" e \"controlar o coletor\" é real, e o projeto prefere nomeá-la a fingir que são a mesma coisa."},

 {"h2": "Bare-metal, kernel, microcontrolador"},
 {"p": "Não há, e **não há caminho a partir daqui**: o runtime é o CPython."},
 {"p": "Isso não fica como um silêncio. [`Arcane.Alvo`](/docs/alvos/portabilidade) descreve o alvo `embarcado` e diz, capacidade por capacidade, o que falta — não há `threading` do CPython, não há `ctypes`, e não é o CPython: é outro interpretador, com outra biblioteca padrão."},
 {"callout": {"tipo": "nota", "titulo": "Por que a ausência é descrita em detalhe", "texto": "Para que ela apareça **antes** de alguém tentar. Uma ausência silenciosa custa a tarde de quem descobre; uma ausência descrita custa trinta segundos de leitura."}},
 {"code": """adopt Arcane.Ecossistema as Eco

// As tres marcas, e o que cada uma quer dizer
assert "existe" in Eco.ESTADOS
assert "equivale" in Eco.ESTADOS
assert "nao-existe" in Eco.ESTADOS

faltam := Eco.o_que_nao_existe()
cycle f in faltam:
    assert f["porque"] is not ""       // toda ausencia tem motivo escrito

// e o que esta no lugar, quando ha algo no lugar
outra := Eco.equivalencias()
assert len(outra) bigger 0
out $"{len(faltam)} ausencias, {len(outra)} equivalencias\"""", "lang": "df"},

 {"h2": "O `equivale` não é um consolo"},
 {"p": "Seis componentes estão marcados como `equivale`, e a distinção com `existe` é estrita: há **outra peça**, nomeada, que responde a mesma pergunta por outro mecanismo."},
 {"table": {"head": ["No desenho", "O que está no lugar", "Por que não é a mesma coisa"], "rows": [
   ["`Borrow Checker`", "`Arcane.Posse` + três códigos do `check`", "não há tempo de vida declarado; o que se protege é o **protocolo** (soltar uma vez, não usar depois), e não a integridade da memória — essa nunca esteve em risco"],
   ["`Build System`", "`forge.toml` + `dataforge devops`", "não havendo compilação para binário, não há etapa de build a orquestrar: o artefato é o código mais o `forge.lock`"],
   ["`ABI` e símbolos", "`Arcane.Abi`", "não há layout binário a quebrar — e há **exatamente o mesmo problema**, com o mesmo sintoma cruel: não é erro de quem publicou, é de quem consome, depois"],
   ["`RISC-V`", "nada de arquitetura no projeto", "onde há CPython 3.10+, roda. **Não é testado**, e dizer \"suportado\" seria prometer o que ninguém verificou"],
   ["`WASM`", "Pyodide", "**compilar para** WASM não existe; **rodar em** WASM funciona, com o interpretador inteiro junto"],
   ["`Driver` (`dfc`)", "o próprio `dataforge`", "um segundo executável duplicaria a resolução de caminho e a leitura do `forge.toml`"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/principios",
"title": "Os dez princípios, medidos",
"description": "Cada princípio com a frase do documento, o que ela significa aqui, o veredito e uma prova que roda — duas delas chamam o analisador e uma abre um interpretador.",
"blocos": [
 {"p": "A referência fecha com dez princípios de design. Uma lista de princípios é o texto mais fácil de escrever num projeto e o mais fácil de não cumprir: **ninguém a executa, e por isso ela nunca reprova.**"},
 {"p": "Aqui cada princípio carrega cinco coisas, e a terceira é a que muda o gênero do texto:"},
 {"table": {"head": ["Campo", "O que é"], "rows": [
   ["`no_documento`", "a frase como a referência a escreve"],
   ["`aqui`", "o que ela significa **nesta** implementação"],
   ["`veredito`", "`cumprido`, `parcial` ou `nao-se-aplica` — e a lista é fechada"],
   ["`prova`", "uma medida que **roda**, e o número que ela deu"],
   ["`custo`", "o que foi entregue em troca"]]}},
 {"code": """dataforge principios             # os dez, medidos
dataforge principios --tensoes   # so onde dois se contradizem
dataforge principios --json      # como dado""", "lang": "bash"},

 {"h2": "O veredito não é dez de dez, de propósito"},
 {"p": "Cinco cumpridos, quatro parciais, um que não se aplica. Um relatório que aprovasse os dez seria a prova de que ninguém o leu."},
 {"code": """adopt Arcane.Principios as Prin

v := Prin.veredito()
assert v["total"] is 10
assert v["cumprido"] bigger 0
assert v["parcial"] bigger 0

// A prova RODA: ela nao repete o texto, ela mede
p := Prin.conferir("compile-time-first")[0]
assert p["veredito"] is "parcial"
assert "4 de 4" in p["medido"]
out p["medido"]""", "lang": "df"},

 {"h2": "As provas que rodam de verdade"},
 {"p": "Três das dez não consultam tabela nenhuma: elas executam o analisador ou o interpretador, porque \"verificação antes de rodar\" e \"custo zero quando desligado\" não são frases — são coisas que se demonstram ou não se demonstram."},
 {"table": {"head": ["Princípio", "O que a prova faz", "O que ela mediu"], "rows": [
   ["`compile-time-first`", "roda o `check` sobre quatro trechos com defeito conhecido — índice fora do alcance, chave ausente, laço que nunca roda, igualdade impossível", "**4 de 4** acusados antes de rodar"],
   ["`custo-zero`", "cria um blueprint sem contrato, invariante nem modificador e olha o que ele carrega", "**3 de 3** sentinelas em `None`, **2 de 2** atalhos de acesso ligados"],
   ["`seguranca-por-padrao`", "roda o `check` sobre um `thread` que escreve num nome de fora e olha a **severidade**", "sai como `warning` — e não como `error`"],
   ["`interoperabilidade`", "adota um módulo do Python de verdade", "a ponte resolve"],
   ["`runtime-modular`", "abre um interpretador sem nenhum `adopt`", "**0** módulos carregados, **0** dependências externas"]]}},

 {"h2": "O que \"custo zero\" quer dizer aqui — e por que o veredito é `nao-se-aplica`"},
 {"p": "O documento diz: *abstrações de alto nível devem compilar para código equivalente a implementações manuais.* Não havendo compilação para código nativo, **a frase não tem como valer**, e forçá-la a valer seria redefini-la em silêncio."},
 {"p": "Então o veredito é `nao-se-aplica` — e há outra leitura que vale, é cobrada e foi medida: **uma abstração custa zero para quem não a usa.**"},
 {"table": {"head": ["Leitura", "Como é cobrada"], "rows": [
   ["contrato, sobrecarga, `exclusive`", "`DFAction.extras` é `None`"],
   ["invariante na linhagem, metaclasse com gancho", "`DFBlueprint.vigias` é `None`"],
   ["congelado, travado, `lazy`, `readonly` em construção", "`DFInstance._estado` é `None`"],
   ["propriedade, descritor, `__getattribute__`", "`leitura_simples` e `escrita_simples` continuam ligados"]]}},
 {"callout": {"tipo": "dica", "titulo": "O acesso a campo ficou mais rápido DEPOIS de os recursos existirem", "texto": "4,47 s → cerca de 3,8 s na carga de método/campo/`spawn`. Não é coincidência: os dois atalhos por blueprint só existiram porque os recursos precisavam de um jeito de sair do caminho — e, no caminho, encontraram o que já estava custando."}},
 {"callout": {"tipo": "atencao", "titulo": "E aqui está o preço, escrito", "texto": "Quem acrescenta um jeito novo de interceptar acesso precisa **derrubar o atalho** do blueprint. A falta disso não dá erro: só faz o recurso novo não rodar para os objetos simples — silenciosamente, que é a pior forma de falhar."}},

 {"h2": "Os dez, em resumo"},
 {"table": {"head": ["#", "Princípio", "Veredito", "O limite"], "rows": [
   ["1", "segurança por padrão", "`parcial`", "o analisador é otimista: a escrita concorrente é **aviso**, não erro"],
   ["2", "custo zero", "`nao-se-aplica`", "não há compilação nativa; vale a leitura \"custa zero quando desligado\""],
   ["3", "controle explícito de recursos", "`cumprido`", "controla-se o protocolo e o coletor, não a alocação"],
   ["4", "compile-time first", "`parcial`", "quando não consegue provar, **cala** — e os silêncios estão listados"],
   ["5", "interoperabilidade", "`cumprido`", "depende de tratar objeto estranho por protocolo, em todo o caminho"],
   ["6", "portabilidade", "`parcial`", "é **herdada** do CPython: é o que dá ARM de graça e o que põe o teto"],
   ["7", "performance observável", "`cumprido`", "medir e ler erram de formas opostas, e por isso existem as duas"],
   ["8", "extensibilidade", "`cumprido`", "palavra nova entra como **contextual**, ao custo de complexidade no parser"],
   ["9", "runtime modular", "`cumprido`", "zero dependência: criptografia e formato de arquivo escritos aqui"],
   ["10", "escalabilidade técnica", "`parcial`", "kernel, bare-metal e microcontrolador estão **fora**, e são nomeados"]]}},
 {"p": "Cada linha da tabela aponta um arquivo. É o que a próxima página usa: [onde dois princípios se contradizem](/docs/ecossistema/tensoes), e qual venceu."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/tensoes",
"title": "Onde dois princípios se contradizem",
"description": "Nove tensões reais: a escolha, o motivo, o custo aceito e o arquivo onde a decisão mora. Uma lista de princípios diz o que se quer; a tensão diz o que se escolheu.",
"blocos": [
 {"p": "Um princípio isolado não informa nada. Todo mundo é a favor de segurança, e todo mundo é a favor de velocidade."},
 {"p": "O que informa é **onde dois princípios se contradizem e qual deles venceu** — e essa decisão, nesta linguagem, está sempre num arquivo."},
 {"code": """adopt Arcane.Principios as Prin

// A tensao e o conteudo: a lista diz o que se quer, a tensao diz o que
// se escolheu quando nao era possivel querer as duas coisas.
ts := Prin.tensoes()
assert len(ts) bigger_eq 9
cycle t in ts:
    assert len(t["entre"]) is 2
    assert t["escolha"] is not ""
    assert t["custo"] is not ""        // toda escolha tem preco declarado

out $"{len(ts)} tensoes, e cada uma aponta um arquivo\"""", "lang": "df"},

 {"h2": "Segurança × verificação: o aviso que não virou erro"},
 {"p": "Duas threads escrevendo na mesma variável perdem atualizações **em silêncio** — medido: 40.425 de 80.000. Numa rota do Kiln é pior, porque a concorrência é invisível: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**."},
 {"p": "O `check` avisa. Ele não **recusa**."},
 {"callout": {"tipo": "atencao", "titulo": "Por que não é erro", "texto": "Um acumulador protegido por mutex passa pelo mesmo caminho de um sem proteção. Recusá-lo proibiria o uso correto — e a pessoa desligaria a verificação inteira, perdendo também os avisos que valiam. **Custo aceito:** um programa com bug de concorrência passa pelo `check`."}},
 {"p": "E a lista de métodos que disparam o aviso foi **medida, não presumida**: `append` de quatro threads, 5 mil vezes cada, entregou 20.000 de 20.000 — o GIL protege a operação inteira, e avisar sobre ele seria falso alarme em código que funciona."},

 {"h2": "Verificação × falso alarme: o analisador cala"},
 {"p": "A calibragem é **0 erros em 222 arquivos conhecidamente bons**. Quando o analisador não consegue provar, ele fica calado — e a lista de silêncios é explícita."},
 {"table": {"head": ["Cala quando", "Porque"], "rows": [
   ["o outro arquivo não compila", "um falso alarme no caminho mais comum de um projeto modular ensina a desligar a verificação"],
   ["há ciclo de import", "a leitura não termina, e chutar seria pior"],
   ["a profundidade (4) acaba", "o custo cresce e a certeza não"],
   ["o `relay` nomeia algo que só existe em execução", "não há como ler o que ainda não rodou"],
   ["`v[\"k\"] ?? padrao`", "`??` é exatamente o que a dica daquele erro recomenda — acusar o próprio conserto desligaria a ferramenta"],
   ["um parâmetro de tipo (`T`) chega com cara de tipo", "sem isso, a trilha ganhava dois alarmes no capítulo que **ensina** generics"]]}},
 {"callout": {"tipo": "perigo", "titulo": "O custo de errar essa escolha foi medido", "texto": "Quando a inferência usou o escopo global em vez do de quem chama, o `check` deu **649 falsos alarmes** num projeto de 252 arquivos — um por uso de parâmetro numa chamada entre módulos. E a suíte passava: os primeiros testes chamavam no nível de topo, onde o escopo global é o certo. Quem pegou foi rodar no projeto grande."}},

 {"h2": "Velocidade × depurabilidade: o depurador desliga o compilador"},
 {"p": "`interp.compilar_corpos = False`. O depurador para em cada linha sombreando `execute`, e o corpo compilado passa por fora."},
 {"p": "Um depurador que enxerga metade das instruções é **pior** que um interpretador mais lento: ele mente sobre onde o programa está."},
 {"callout": {"tipo": "nota", "titulo": "E as duas execuções não são o mesmo caminho", "texto": "Por isso `tests/test_desempenho.py` roda uma amostra dos exercícios com a compilação ligada e desligada e compara a saída **caractere por caractere**. É esse teste que pega um fechamento que divergiu do método que ele espelha."}},

 {"h2": "Velocidade × correção: o escopo do laço"},
 {"p": "Reaproveitar o escopo entre voltas de um laço é a otimização mais rentável do interpretador. E é **a mais perigosa**: errá-la não dá erro, dá resposta errada."},
 {"code": """acoes := []
cycle i from 1 to 3:
    acoes.append(lambda => i)          // cada volta tem o SEU 'i'

assert acoes[0]() is 1
assert acoes[1]() is 2
assert acoes[2]() is 3                 // e nao 3, 3, 3
out "cada closure lembra a volta em que nasceu\"""", "lang": "df"},
 {"p": "`_corpo_captura_escopo` varre a árvore **inteira**, e não só as instruções — um `lambda` vive dentro de uma expressão. Sem isso, as três closures veriam todas o último valor: o clássico que o Python tem e que aqui não acontece."},

 {"h2": "Extensibilidade × nomes bons"},
 {"p": "`route`, `render`, `server`, `agrupar` e `ordenar` são nomes bons demais para tirar de quem escreve. Por isso palavra nova entra como **contextual**, e não em `KEYWORDS`."},
 {"code": """// 'route' e contextual: aqui e um nome comum
route := "/pedidos"
agrupar := yes
assert route is "/pedidos"
assert agrupar is yes
out "as palavras do framework continuam livres\"""", "lang": "df"},
 {"table": {"head": ["Família", "Quantas", "Onde valem"], "rows": [
   ["Kiln", "11", "dentro de `server` e de uma rota"],
   ["OOP / blueprint", "21", "onde um modificador faz sentido"],
   ["`type`, `opaque`, `where`", "4", "quando a linha confirma a declaração"],
   ["Crucible", "10", "numa suíte de teste"],
   ["verbos de quadro", "6", "logo depois de um `>>`"]]}},
 {"callout": {"tipo": "dica", "titulo": "Sete palavras reservadas já foram REMOVIDAS", "texto": "Toda palavra em `KEYWORDS` deixa de poder ser identificador. Antes de acrescentar uma, o repositório cobra `grep -c \"TokenType.NOVA\" dataforge/parser.py` — se der 0, ela só quebra código de usuário sem entregar nada. **Custo aceito:** o parser fica mais complicado, e a gramática do editor precisa de duas travas para não envelhecer."}},

 {"h2": "Runtime modular × zero dependência"},
 {"p": "A biblioteca padrão usa **apenas** a biblioteca padrão do Python. Isso significa código escrito à mão onde havia biblioteca madura:"},
 {"list": ["ChaCha20-Poly1305, pelo RFC 8439", "o `.xlsx`, sem dependência externa", "o WebSocket, pelo RFC 6455 — máscara, ping, pong, continuação e quadro de 64 bits", "os gráficos da Vitrine, em SVG escrito no servidor, com ~4 KB de cliente"]},
 {"p": "O preço está escrito: criptografia e formato de arquivo implementados aqui, com o risco que isso tem. E o ganho também: **um app em rede fechada funciona** — que é onde painel de dados costuma rodar."},
 {"callout": {"tipo": "nota", "titulo": "E há teste cobrando isso", "texto": "Um teste proíbe `http://`, `https://` e `cdn` no CSS e no JS da Vitrine. Uma biblioteca de CDN quebra qualquer app em rede fechada, e a falha aparece no cliente, não no build."}},

 {"h2": "Portabilidade × performance"},
 {"p": "A portabilidade é **herdada** do CPython. É o que dá Linux, macOS, Windows, ARM e ARM64 sem uma linha de código de arquitetura, e o que faz `adopt Python.numpy` existir."},
 {"p": "É também o que põe o teto em ~6,5×. As duas coisas são a mesma decisão vista de dois lados, e não há como ficar só com uma."},

 {"h2": "Controle × segurança: onde a proteção para"},
 {"p": "FFI sem ponteiro não é FFI. `Arcane.C` recusa o nulo e confere o layout da struct contra a ABI — e aritmética de ponteiro é aritmética de ponteiro."},
 {"callout": {"tipo": "perigo", "titulo": "Um segmentation fault não é um erro da linguagem", "texto": "É o processo morrendo. A fronteira está **documentada** em vez de fingida: passado esse ponto, quem escreve é responsável pelo que acontece."}},

 {"h2": "Mensagem útil × identidade do erro"},
 {"p": "O runtime fala português. A tradução acontece **no desenho**, nunca em `error.message`."},
 {"table": {"head": ["Decisão", "Sem ela"], "rows": [
   ["traduzir ao desenhar", "`e.message` é o que um `handle` compara e o que milhares de testes comparam — traduzir ali mudaria o comportamento de programa já escrito"],
   ["o que não tem tradução sai em inglês", "ninguém traduz 530 mensagens numa tacada, e um erro é mais útil legível em inglês que ilegível em português"],
   ["a suíte roda em inglês", "um teste que afirma \"Division by zero\" checa a **estrutura** do relatório; deixar o idioma solto o faria reprovar a cada tradução nova"],
   ["há um piso de cobertura", "o fallback certo é também o que esconde o buraco: o que falta sai em inglês legível, e ninguém vê"]]}},
 {"p": "O que interessa a um programa é a **identidade** do erro, não o idioma dele. O que interessa a uma pessoa é o contrário — e as duas coisas caibem, desde que em camadas diferentes."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/percurso",
"title": "O percurso, e onde o tempo vai",
"description": "As nove fases de compilação em ordem, com o que cada uma produziu e quanto levou — e por que o comando não executa o programa.",
"blocos": [
 {"p": "[`dataforge ir`](/docs/compilador/pipeline) mostra **cada** fase: o HIR, o MIR, as análises, a SSA, o LIR. O que não havia era a visão de cima — as fases **em ordem**, o que cada uma produziu e quanto tempo levou."},
 {"p": "Que é a pergunta que aparece quando um arquivo demora a abrir no editor: *onde o tempo vai?*"},
 {"code": """dataforge percurso app.df              # a tabela de fases
dataforge percurso app.df --sem-tipos  # pula a analise estatica
dataforge percurso --desenho           # o caminho, com as ausencias
dataforge percurso app.df --json       # como dado""", "lang": "bash"},
 {"code": """  app.df  —  0.526 ms no total

  fase              ms      %   o que saiu
  lexer          0.064   12.2   12 tokens
  parser         0.034    6.4   5 nos, 2 no topo
  hir            0.007    1.2   0 acucares em 0 formas
  tipos          0.143   27.2   0 erro(s), 0 aviso(s)
  mir            0.050    9.5   1 corpo(s), 1 bloco(s)
  analises       0.040    7.6   0 morto(s), 0 talvez nao definido(s)
  ssa            0.033    6.3   0 no(s) phi
  otimizar       0.092   17.4   0 oportunidade(s) em 0 passe(s)
  lir            0.064   12.2   4 de 4 nos viraram fechamento (100%)
  execucao           —          nao percorrida: executar e o que o programa faz

  a fase mais cara deste arquivo: tipos""", "lang": "text", "title": "dataforge percurso — a saída"},

 {"h2": "Ele não executa o programa, e isso é deliberado"},
 {"p": "O percurso vai do lexer ao compilador de fechamentos e **para ali**. A última fase é nomeada, medida em zero e marcada como não percorrida, com o motivo escrito."},
 {"callout": {"tipo": "atencao", "titulo": "Um comando que mostra fases não pode ter efeito no mundo", "texto": "Executar é o que o programa faz — e um arquivo de verdade abre soquete, escreve em disco e manda e-mail. Um `dataforge percurso` que executasse seria usado **uma vez**. A fase continua no mapa para que a ausência tenha lugar, do mesmo modo que `Machine Code` continua no desenho do ecossistema."}},
 {"code": """adopt Arcane.Percurso as Perc

fs := Perc.fases()
assert len(fs) is 10
assert fs[0]["fase"] is "lexer"
assert fs[9]["fase"] is "execucao"     // nomeada, e NAO percorrida

d := Perc.divergencias()
assert len(d) bigger_eq 5
out $"{len(fs)} fases, {len(d)} divergencias do desenho\"""", "lang": "df"},

 {"h2": "A armadilha que inverteu a resposta"},
 {"p": "A primeira versão deste comando apontava a fase errada — e apontava com confiança, que é o pior jeito de errar."},
 {"table": {"head": ["Arquivo de 12 tokens", "Antes", "Depois"], "rows": [
   ["fase apontada como mais cara", "`lir`, com **93,8%**", "`tipos`, com 27,2%"],
   ["total", "7,266 ms", "**0,526 ms**"],
   ["trabalho real do `lir`", "0,05 ms", "0,064 ms"]]}},
 {"p": "A causa: `lir` importa `compilador` e abre um interpretador **por dentro**. A primeira fase que toca um módulo paga o `import` dele, e o cronômetro atribui esse custo a ela."},
 {"callout": {"tipo": "perigo", "titulo": "Uma ferramenta que aponta a fase errada é pior que nenhuma", "texto": "A pessoa vai otimizar o lugar que a ferramenta indicou. Hoje os imports lentos acontecem **antes** de qualquer cronômetro, e o módulo diz isso num comentário ao lado da linha que os aquece — para que ninguém os remova por parecerem inúteis."}},

 {"h2": "O tempo é uma medida, não um benchmark"},
 {"p": "Cada fase é cronometrada **uma** vez, nesta máquina, com esta carga. Serve para comparar as fases **entre si** — que é a pergunta — e não para comparar máquinas nem para afirmar que uma mudança melhorou algo."},
 {"p": "Para isso há [`Arcane.Bench`](/docs/observabilidade/comparar), que repete, tira **mediana** (e não média: uma pausa do coletor no meio da amostra a carrega para sempre) e sabe dizer, por Mann-Whitney, se a diferença é real."},
 {"code": """adopt Arcane.Percurso as Perc
adopt Arcane.IO as IO
adopt Arcane.OS as OS

pasta := $"{OS.temp_dir()}/df-percurso-{randint(100000, 999999)}"
IO.mkdir(pasta)
alvo := $"{pasta}/exemplo.df"
IO.write(alvo, "action dobrar(n):\\n    yield n * 2\\nout dobrar(21)\\n")

r := Perc.percorrer(alvo)
assert len(r["fases"]) is 10
assert r["ms"] bigger 0

// a ultima fase existe no mapa e NAO foi percorrida
ultima := r["fases"][9]
assert ultima["fase"] is "execucao"
assert ultima["percorrida"] is no

out $"a fase mais cara: {r['mais_cara']}"
IO.remove_tree(pasta)""", "lang": "df"},

 {"h2": "O que cada fase entrega"},
 {"table": {"head": ["Fase", "Arquivo", "O que sai"], "rows": [
   ["`lexer`", "`lexer.py`", "tokens, com INDENT/DEDENT e interpolação"],
   ["`parser`", "`parser.py`", "a árvore — e quantos nós ela tem"],
   ["`hir`", "`hir.py`", "quantos açúcares o arquivo usa, de 5 formas; e **8 construções que não são açúcar**, cada uma com o motivo"],
   ["`tipos`", "`typechecker.py`", "erros e avisos — e esta fase **atravessa** os `adopt`"],
   ["`mir`", "`mir.py`", "corpos e blocos básicos, com arestas rotuladas"],
   ["`analises`", "`mir.py`", "bloco morto, nome talvez não definido, constante provada"],
   ["`ssa`", "`ssa.py`", "nós φ das junções"],
   ["`otimizar`", "`otimizar.py`", "oportunidades de dobra, ramo morto e inalcançável"],
   ["`lir`", "`lir.py`", "quantos nós desceram para fechamento, e **quantos recuaram**"],
   ["`execucao`", "`interpreter.py`", "— não percorrida"]]}},
 {"callout": {"tipo": "dica", "titulo": "A fase `tipos` é a mais cara num projeto de verdade", "texto": "Ela lê a **superfície** dos arquivos vizinhos para conferir aridade, tipo de parâmetro e tipo de retorno através do `adopt`. O cache é por `(caminho, mtime)`: sem ele, 200 arquivos importando três vizinhos cada levariam o `check` de 0,7 s a mais de um minuto. `--sem-tipos` a pula, quando a pergunta é sobre as outras."}},

 {"h2": "O que a medida mostrou, e não era o esperado"},
 {"p": "No maior exemplo do repositório — 2.233 tokens, 1.161 nós — a fase mais cara **não** é o verificador de tipos nem a construção do grafo:"},
 {"table": {"head": ["Fase", "Fatia", "O que ela achou"], "rows": [
   ["`otimizar`", "**35,3%**", "8 oportunidades, em 2 dos 3 passes"],
   ["`mir`", "15,4%", "21 corpos, 66 blocos"],
   ["`tipos`", "11,7%", "0 erros, 1 aviso"],
   ["`ssa`", "10,9%", "10 nós φ"],
   ["`lir`", "3,9%", "1.113 de 1.153 nós compilados (97%)"]]}},
 {"p": "**O passe que acha menos é o que custa mais.** `relatorio_de` reescreve a árvore inteira para contar, e num arquivo que já está bem escrito ele encontra oito dobras de constante e nada mais."},
 {"callout": {"tipo": "nota", "titulo": "E isso é coerente com o que já estava medido", "texto": "Os passes de otimização deste repositório rendem **1,01×** na execução. Um ganho de 1% que custa um terço do tempo de análise é exatamente o tipo de número que costuma não ser publicado — e é o que decide se vale ligá-los por padrão. Eles não são ligados: `dataforge ir --fase=otimizado` mostra o que eles conseguiriam, e fica a cargo de quem lê."}},

 {"h2": "O caminho real, e onde ele difere do desenho"},
 {"p": "`dataforge percurso --desenho` imprime o caminho com as ausências no lugar delas. As cinco divergências em relação ao desenho da referência:"},
 {"table": {"head": ["No desenho", "Aqui", "Por quê"], "rows": [
   ["`Borrow + Dataflow Checker`", "o Dataflow existe; o Borrow, não", "num mundo com coletor, o que se protege é o protocolo — e quem o protege é `Arcane.Posse` mais três códigos do `check`"],
   ["`LLVM Backend`", "`compilador.py` — fechamentos", "o LLVM tiraria a zero dependência. Medido: 1,5× a 1,8×, com teto ~6,5×"],
   ["`Machine Code / WASM`", "não há; o artefato é a árvore compilada", "rodar **em** WASM funciona pelo Pyodide, e isso é outra frase"],
   ["`Bare-Metal Runtime`", "não há", "o runtime é o CPython"],
   ["*(ausente no desenho)* `Execution Engine`", "`interpreter.py` — o centro", "o desenho supõe compilação antecipada, e por isso não tem onde pôr o interpretador"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/referencia",
"title": "Referência rápida: as dezesseis áreas",
"description": "A tabela final da referência Deep Tech, com o que existe em cada área, onde ele mora no código e a rota que o documenta.",
"blocos": [
 {"p": "A referência fecha com uma tabela de dezesseis áreas. Esta página é essa tabela **resolvida**: para cada área, o que existe, onde mora e onde está documentado."},
 {"p": "Ela também é o índice de saída das 22 partes — se você chegou aqui procurando por um assunto, comece por esta tabela."},

 {"h2": "Linguagem e tipos"},
 {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [
   ["Linguagem", "81 palavras reservadas, 52 contextuais, 225 funções globais", "[referência](/docs/referencia/arquitetura)"],
   ["Tipos", "alias, união, interseção, refinamento (`where`), opaco, genérico com limite", "[tipos nomeados](/docs/tipos-nomeados)"],
   ["Coleções tipadas", "`Cluster<T>`, `Vault<K,V>`, `Set<T>`, `Tuple<A,B>` — fronteira e inserção", "[genéricos](/docs/tipos/genericos)"],
   ["OOP", "`record`, `blueprint`, `enum`, `trait`, contrato, invariante, metaclasse", "[OOP avançada](/docs/oop/contratos)"],
   ["Falha como valor", "`ok`/`falha`, `Talvez` para onde `void` é ambíguo", "[resultado](/docs/tipos/resultado)"]]}},

 {"h2": "Memória, posse e concorrência"},
 {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [
   ["Posse", "dono exclusivo, empréstimo com escopo, contagem determinística, referência fraca", "[posse](/docs/memoria/posse)"],
   ["Memória", "arena, mapa fraco, controle e **medição** do coletor", "[coletor](/docs/memoria/coletor)"],
   ["Concorrência", "mutex, semáforo, barreira, contador atômico, canal bloqueante, STM", "[STM](/docs/concorrencia/stm)"],
   ["Mais de um núcleo", "`P.map_processos`, pool que sobrevive entre chamadas — **3,45×** em 10 núcleos", "[paralelismo](/docs/tecnicas/processos)"],
   ["Runtime async", "laço de eventos, escalonador, fibras, `async`/`await`", "[laço de eventos](/docs/runtime/laco)"]]}},
 {"callout": {"tipo": "atencao", "titulo": "A linguagem não sincroniza sozinha", "texto": "Duas threads escrevendo na mesma variável perdem atualizações — medido: 40.425 de 80.000, em silêncio. As peças existem; **usá-las é escolha de quem escreve**, e o `check` avisa sem recusar."}},

 {"h2": "Metaprogramação e FFI"},
 {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [
   ["Metaprogramação", "citar, transformar, gerar, derivar; a árvore como dado", "[macros](/docs/metaprogramacao/macros)"],
   ["`comptime`", "calcular na leitura, e falhar ali", "[comptime](/docs/metaprogramacao/comptime)"],
   ["DSL", "combinadores para uma linguagem externa própria", "[DSL](/docs/metaprogramacao/dsl)"],
   ["FFI", "biblioteca nativa, ponteiro cru, struct conferida contra a ABI, callback", "[FFI para C](/docs/ffi/c)"],
   ["Ponte Python", "`adopt Python.numpy` — **sem converter nada**", "[ponte](/docs/tecnicas/ponte)"],
   ["ABI", "a superfície como contrato, 11 regras, o bump que a mudança exige", "[superfície](/docs/abi/superficie)"]]}},

 {"h2": "Compilador, backend e hardware"},
 {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [
   ["Compilador", "lexer, parser, AST, HIR, MIR, LIR, dataflow", "[percurso](/docs/ecossistema/percurso)"],
   ["Backend", "SSA com φ, SCCP, dobra de constante, ramo morto, fechamentos", "[backend](/docs/compilador/backend)"],
   ["Hardware", "o que se pode observar de dentro do CPython, e o que **não**", "[hardware](/docs/hardware/mapa)"],
   ["Build", "`forge.toml`, Dockerfile, CI, k8s, Helm, SBOM, `doctor`", "[DevOps](/docs/devops)"]]}},
 {"callout": {"tipo": "nota", "titulo": "PGO, LTO e cross-compilation", "texto": "As três pressupõem um compilador que emite objeto. Não havendo backend nativo, elas **não se aplicam** — e a página de hardware diz isso com todas as letras, em vez de deixar a linha em branco."}},

 {"h2": "Observabilidade e ecossistema"},
 {"table": {"head": ["Área", "O que existe", "Rota"], "rows": [
   ["Performance", "percentis, cauda, flame graph em SVG, pausas do coletor, Mann-Whitney", "[perfil](/docs/observabilidade/perfil)"],
   ["Complexidade", "`big-o` **lê** a árvore; `bench` **mede** a curva", "[complexidade](/docs/big-o/analisar)"],
   ["Tooling", "LSP, depurador, DAP, formatador, linter, testes com cobertura, doc", "[ferramentas](/docs/cli)"],
   ["Web", "rodar em WASM pelo Pyodide; compilar para WASM **não existe**", "[WASM](/docs/alvos/wasm)"],
   ["Alvos", "6 ambientes descritos, com o motivo de cada ausência", "[portabilidade](/docs/alvos/portabilidade)"],
   ["Partida", "7 fases de inicialização, TLS, pilha, capacidade", "[partida](/docs/partida/inicio)"],
   ["Ecossistema", "41 componentes, conferidos contra o disco", "[componentes](/docs/ecossistema/componentes)"],
   ["Design", "10 princípios medidos, 9 tensões", "[princípios](/docs/ecossistema/principios)"]]}},

 {"h2": "Onde começar, por objetivo"},
 {"cards": [
   {"href": "/docs/ecossistema/ausencias", "title": "O que não existe", "meta": "7 componentes", "desc": "A página mais útil para decidir se a linguagem serve ao seu caso."},
   {"href": "/docs/ecossistema/tensoes", "title": "As tensões", "meta": "9 decisões", "desc": "Onde dois princípios se contradizem, e qual venceu — com o custo."},
   {"href": "/docs/ecossistema/percurso", "title": "Onde o tempo vai", "meta": "10 fases", "desc": "O percurso de um arquivo, medido fase por fase."},
   {"href": "/docs/ecossistema/mapa", "title": "Partes 20, 21 e 22", "meta": "o mapa", "desc": "Item por item: o que virou código, o que virou página, o que não existe."}]},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/ecossistema/mapa",
"title": "Ecossistema e design: o mapa",
"description": "As partes 20, 21 e 22 da referência Deep Tech, item por item: o que virou código, o que virou página, e o que não existe — com o motivo.",
"blocos": [
 {"p": "As três partes que fecham a referência são as de **síntese**, e é exatamente aí que um documento começa a mentir: um desenho não roda, e uma lista de princípios nunca reprova."},
 {"p": "A resposta aqui foi fazer as três **derivadas do código e conferidas contra ele**. Este mapa é o índice do resultado, item por item."},

 {"h2": "Parte 20 — arquitetura do ecossistema"},
 {"table": {"head": ["Item do desenho", "Estado", "Onde"], "rows": [
   ["`dfc` — Lexer, Parser, AST, HIR", "`existe`", "`lexer.py`, `parser.py`, `ast_nodes.py`, `hir.py`"],
   ["`dfc` — Type Checker", "`existe`", "`typechecker.py` + `superficie.py` + `resolucao.py`"],
   ["`dfc` — Borrow Checker", "`equivale`", "`Arcane.Posse` + 3 códigos do `check`"],
   ["`dfc` — MIR, Dataflow, LIR", "`existe`", "`mir.py`, `ssa.py`, `lir.py`"],
   ["`dfc` — LLVM Backend", "**`nao-existe`**", "`compilador.py` — fechamentos, 1,5× a 1,8×"],
   ["`dfc` — Code Generator", "**`nao-existe`**", "não há código de máquina"],
   ["`dfup` — Version Manager", "**`nao-existe`**", "os instaladores; trocar versão é reinstalar"],
   ["`dfpm` — Package Manager, Resolver", "`existe`", "`packages.py`, registro estático"],
   ["`dfpm` — Build System", "`equivale`", "`forge.toml` + `dataforge devops`"],
   ["`dfpm` — Workspace Manager", "**`nao-existe`**", "um `forge.toml` por pacote"],
   ["Runtime — Allocator", "**`nao-existe`**", "`Arcane.Memoria`: arena e controle do coletor"],
   ["Runtime — Scheduler, Event Loop, Async", "`existe`", "`arcane_laco.py`"],
   ["Runtime — Thread Runtime", "`existe`", "`travessia.py` — 3,45× em 10 núcleos"],
   ["Runtime — Error Runtime", "`existe`", "`errors.py`, 177 códigos, `idioma.py`"],
   ["Runtime — Bare-Metal", "**`nao-existe`**", "o runtime é o CPython"],
   ["Tooling — os sete", "`existe`", "LSP, fmt, lint, test, bench, profile, doc"],
   ["*(ausente)* Debugger", "`existe`", "`depurador.py` + `dap.py`"],
   ["*(ausente)* Execution Engine", "`existe`", "`interpreter.py` — o centro"],
   ["Targets — Linux, macOS, Windows, ARM", "`existe`", "4 plataformas construídas a cada tag"],
   ["Targets — RISC-V", "`equivale`", "onde há CPython roda; **não testado**"],
   ["Targets — WASM", "`equivale`", "rodar em, pelo Pyodide; compilar para, não"],
   ["Targets — Bare-Metal", "**`nao-existe`**", "`Arcane.Alvo` descreve o que falta"]]}},
 {"p": "O módulo: [`Arcane.Ecossistema`](/docs/ecossistema/componentes) · o comando: `dataforge ecossistema` · a conferência: `conferir()`, nas duas direções."},

 {"h2": "Parte 21 — princípios de design"},
 {"table": {"head": ["Princípio", "Veredito", "O que a prova mediu"], "rows": [
   ["segurança por padrão", "`parcial`", "8 capacidades; a escrita concorrente sai como **aviso**"],
   ["custo zero", "`nao-se-aplica`", "3 de 3 sentinelas em `None`, 2 de 2 atalhos ligados"],
   ["controle explícito de recursos", "`cumprido`", "`Posse` com 16 símbolos, `Memoria` com 24, `defer` na linguagem"],
   ["compile-time first", "`parcial`", "**4 de 4** erros de execução acusados antes de rodar"],
   ["interoperabilidade", "`cumprido`", "`Arcane.C` com 23 símbolos; a ponte resolve"],
   ["portabilidade", "`parcial`", "6 alvos; 1 sem capacidade nenhuma"],
   ["performance observável", "`cumprido`", "8 de 8 comandos de medição presentes"],
   ["extensibilidade", "`cumprido`", "81 reservadas contra **52 contextuais**"],
   ["runtime modular", "`cumprido`", "**0** módulos carregados, **0** dependências externas"],
   ["escalabilidade técnica", "`parcial`", "7 componentes ausentes, nomeados"]]}},
 {"p": "E as **nove tensões**, que são o conteúdo que uma lista de princípios nunca tem: [onde dois se contradizem](/docs/ecossistema/tensoes), qual venceu, o custo aceito e o arquivo onde a decisão mora."},
 {"p": "O módulo: [`Arcane.Principios`](/docs/ecossistema/principios) · o comando: `dataforge principios` · `--tensoes` para só as nove."},

 {"h2": "Parte 22 — visão de implementação"},
 {"table": {"head": ["Item", "O que virou", "Onde"], "rows": [
   ["o desenho do pipeline", "as 10 fases como dado, na ordem", "`Arcane.Percurso.fases()`"],
   ["o caminho de um arquivo", "as fases **medidas**, com o que cada uma produziu", "`percorrer()` · `dataforge percurso`"],
   ["o desenho em si", "impresso, com as ausências no lugar delas", "`desenho()` · `--desenho`"],
   ["onde o real difere do desenho", "5 divergências, com o motivo de cada", "`divergencias()`"],
   ["`Application / Server`", "o interpretador, e os dois frameworks web", "[Kiln](/docs/kiln) · [Vitrine](/docs/vitrine)"],
   ["`Bare-Metal / Kernel / MCU`", "**não existe**", "[as ausências](/docs/ecossistema/ausencias)"]]}},

 {"h2": "O que estas três partes ensinaram"},
 {"table": {"head": ["Lição", "Como apareceu"], "rows": [
   ["um mapa escrito à mão mente sem avisar", "`conferir()` pegou dois caminhos errados meus **antes** do primeiro teste existir: o arquivo se chama `arcane_paralelo.py`, e só a classe se chama `ArcaneConcurrent`"],
   ["uma ferramenta que aponta a fase errada é pior que nenhuma", "o `lir` marcava 93,8% num arquivo de 12 tokens: era o custo do `import`, não da fase. O total caiu de 7,3 ms para **0,5 ms** e a resposta mudou de fase"],
   ["um princípio que não se aplica é informação", "\"zero-cost abstractions\" não tem como valer sem compilação nativa. Redefini-lo em silêncio seria pior que marcá-lo `nao-se-aplica` e escrever a leitura que vale"],
   ["a ausência precisa de lugar no mapa", "`Machine Code` e `execucao` continuam nos desenhos, marcados. Apagá-los faria o desenho parecer completo"]]}},
 {"p": "As 22 partes da referência estão cobertas. O que existe está medido; o que não existe está nomeado, com o motivo — que é a única forma de um documento técnico continuar verdadeiro depois de publicado."},
]},
]
