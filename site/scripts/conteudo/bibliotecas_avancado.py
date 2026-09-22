# -*- coding: utf-8 -*-
"""Escrever uma biblioteca — as nove páginas que faltavam.

O que já havia cobria o **ciclo** (estrutura, contrato, teste, versão,
publicação, manutenção). O que faltava era o **desenho**: como se
escolhe um nome, como se recebe opção, que erro se levanta, o que se
promete sobre desempenho, e o que só quebra na máquina de outra pessoa.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/api",
"title": "Desenhar a API pública",
"description": "Sete decisões de assinatura — e a que decide se alguém consegue usar a sua biblioteca sem abrir o código.",
"blocos": [
 {"p": "A API é o que a pessoa lê. Tudo o mais — a implementação, os testes, a documentação — existe para sustentá-la, e nenhum deles a conserta depois de publicada."},

 {"h2": "O nome diz o que devolve"},

 {"table": {"head": ["Nome", "O que ele promete", "Devolve"], "rows": [
   ["`buscar`", "procura, pode não achar", "o valor ou `void`"],
   ["`exigir`", "procura, e **falha** se não achar", "o valor, sempre"],
   ["`tem`", "uma pergunta", "`yes`/`no`"],
   ["`de`", "constrói a partir de", "o objeto novo"],
   ["`para`", "converte para", "a outra forma"],
   ["`com`", "uma cópia mudada", "objeto **novo**"],
   ["`definir`", "muda no lugar", "nada útil"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Um par que devolve coisas diferentes tem de ter nomes diferentes", "texto": "`remove` e `pop` fazem quase a mesma coisa nas coleções da linguagem, e os nomes separam o que importa: `remove` apaga **no lugar** e é silencioso quando não acha; `pop` devolve o valor e por isso **levanta**. Devolver `void` calado esconderia a diferença entre *“a chave valia `void`”* e *“a chave não estava lá”* — e `omit` devolve **cópia** sem mexer no original. Três verbos, três promessas."}},

 {"h2": "Posicional até três; depois, opções"},

 {"code": """// Tres posicionais ainda se leem.
//   Tabela.montar(linhas, colunas, titulo)
//
// Cinco nao:
//   Tabela.montar(linhas, colunas, titulo, yes, no, 3, "—")
//                                          ?    ?  ?   ?
//
// A partir dai, o que varia vira um vault de opcoes.

action montar(linhas, colunas, opcoes := {}):
    o := {"titulo": "", "totais": no, "largura": 0, "vazio": "—"}
    cycle chave in opcoes.keys():
        given chave not in o:
            trigger $"'{chave}' nao e uma opcao de montar"
        o[chave] := opcoes[chave]
    yield $"{len(linhas)}x{len(colunas)}, vazio='{o['vazio']}'"

out montar([1, 2], ["a"], {"vazio": "-"})
assert montar([1], ["a"]) is "1x1, vazio='—'\"""", "lang": "df"},

 {"h2": "Aceitar as três formas de “um campo”"},

 {"p": "Uma função que recebe *“o campo pelo qual ordenar”* precisa funcionar com **vault, record e instância**. Este foi um bug real da própria biblioteca: `sort_by_field` devolvia `void` para todos os records, calada."},

 {"code": """adopt Arcane.Reflexo as R

action campo_de(item, nome):
    given typeof(item) is "Vault":
        yield item[nome] ?? void
    yield R.ler(item, nome)

record Pessoa:
    nome: String
    idade: Integer

assert campo_de({"idade": 30}, "idade") is 30
assert campo_de(Pessoa("Ana", 41), "idade") is 41""", "lang": "df"},

 {"h2": "O que nunca entra numa assinatura pública"},

 {"table": {"head": ["Não", "Porque"], "rows": [
   ["um booleano sem nome", "`montar(l, c, yes, no)` é ilegível na chamada; vire opção"],
   ["um índice mágico (`-1` = todos)", "o dia em que `-1` for legítimo não tem saída"],
   ["um tipo do Python vazando", "`list` e `dict` não existem nesta linguagem"],
   ["ordem de argumentos que muda", "é a quebra mais barata de cometer e a mais cara de achar"],
   ["um parâmetro que só faz sentido junto de outro", "dois parâmetros com uma regra entre eles são um objeto"]]}},

 {"p": "Continue em [O vault de opções](/docs/bibliotecas/opcoes) e [Os erros da sua biblioteca](/docs/bibliotecas/erros)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/opcoes",
"title": "O vault de opções",
"description": "Por que recusar a chave desconhecida — e não avisar sobre ela.",
"blocos": [
 {"p": "Um vault de opções aceita qualquer chave. É isso que o torna conveniente, e é exatamente por isso que ele precisa de uma guarda."},

 {"callout": {"tipo": "atencao", "titulo": "O erro de digitação some, e o padrão vence", "texto": "`{\"tentativa\": 9}` — singular — deixava o cliente com as **3 tentativas** do padrão, e o 9 não chegava a lugar nenhum. Pior: `API.openapi(app, {\"title\": \"Loja\"})`, em inglês, como o próprio OpenAPI escreve o campo, saía com o título padrão — e quem escreve isso **publica um contrato com o nome errado** sem nada denunciar."}},

 {"h2": "Recusar, e não avisar"},

 {"p": "Um aviso impresso não para nada: o programa segue com o padrão, que é exatamente o estado que se queria evitar. E num servidor o aviso vai para um log que ninguém lê."},

 {"code": """PADROES := {"tentativas": 3, "prazo": 30, "recuo": 0.5}

action ler_opcoes(recebidas, conhecidas, onde):
    resultado := {}
    cycle k in conhecidas.keys():
        resultado[k] := conhecidas[k]
    cycle k in recebidas.keys():
        given k.startswith("_"):
            skip
        given k not in conhecidas:
            nomes := ", ".join(sorted(conhecidas.keys()))
            trigger $"'{k}' nao e uma opcao de '{onde}'. Aceita: {nomes}"
        resultado[k] := recebidas[k]
    yield resultado

o := ler_opcoes({"prazo": 5}, PADROES, "cliente")
assert o["prazo"] is 5
assert o["tentativas"] is 3

monitor:
    ler_opcoes({"tentativa": 9}, PADROES, "cliente")
    assert no
handle Error as e:
    out e.message""", "lang": "df"},

 {"table": {"head": ["Decisão", "Porque"], "rows": [
   ["a lista de conhecidas num lugar só", "ela **é** a documentação; duas cópias divergem"],
   ["a mensagem lista o que aceita", "quem errou o nome não tem como adivinhar o certo"],
   ["chave começando com `_` passa", "é a porta de escape para extensão e para teste"],
   ["o padrão é aplicado pelo chamador", "a validação e a mesclagem são perguntas diferentes"]]}},

 {"callout": {"tipo": "dica", "titulo": "Sugira o nome parecido", "texto": "O analisador da linguagem usa `difflib` para isso, e vale aqui: *“'tentativa' não é uma opção. Você quis dizer 'tentativas'?”* transforma um erro que custa uma hora num erro que custa cinco segundos. É a diferença entre uma mensagem que **descreve** e uma que **resolve**."}},

 {"p": "Continue em [Desenhar a API](/docs/bibliotecas/api) e [Os erros](/docs/bibliotecas/erros)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/erros",
"title": "Os erros da sua biblioteca",
"description": "A classe do erro é o contrato — e um erro genérico mata a distinção na fronteira do handle.",
"blocos": [
 {"p": "Quem usa a sua biblioteca escreve `handle`. O que ele consegue escrever ali é decidido inteiramente por você."},

 {"callout": {"tipo": "atencao", "titulo": "`trigger \"texto\"` em tudo apaga a distinção", "texto": "Para quem escreve o `handle`, *violar uma regra de negócio* e *dividir por zero* viram a mesma coisa — e a única saída passa a ser comparar o **texto** da mensagem, que quebra na primeira tradução e na primeira correção de vírgula."}},

 {"code": """record FalhaDeLeitura:
    caminho: String
    motivo: String

record FalhaDeFormato:
    linha: Integer
    esperado: String

action carregar(caminho):
    given not caminho.endswith(".csv"):
        trigger FalhaDeFormato(1, "um arquivo .csv")
    given caminho.startswith("/nao-existe"):
        trigger FalhaDeLeitura(caminho, "nao encontrado")
    yield ["ok"]

monitor:
    carregar("dados.txt")
handle FalhaDeFormato as e:
    f := e.value
    out $"linha {f.linha}: esperava {f.esperado}"
handle FalhaDeLeitura as e:
    f := e.value
    out $"nao li {f.caminho}: {f.motivo}"

assert carregar("dados.csv") is ["ok"]""", "lang": "df"},

 {"h2": "Uma base por família"},

 {"p": "Quando a biblioteca tem seis erros, quem a usa quase nunca quer os seis separados — quer *“qualquer coisa que a sua biblioteca levante”*. Uma base comum entrega isso, e ela tem de ser conferida nas **duas** direções."},

 {"table": {"head": ["A conferir", "O que quebra sem isso"], "rows": [
   ["a base pega **todas** as suas", "uma nova nasce fora da família, e o `handle` do usuário passa a deixá-la escapar"],
   ["a base **não** pega as de fora", "`handle SuaBase` vira um `handle` sem tipo — e engole o `1 / 0` do usuário"]]}},

 {"h2": "A mensagem diz o que fazer"},

 {"table": {"head": ["Ruim", "Bom"], "rows": [
   ["`Invalid assignment target`", "`'no' é palavra reservada e não pode receber valor. Escolha outro nome.`"],
   ["`KeyError: cidad`", "`A chave \"cidad\" não está neste vault. Você quis dizer \"cidade\"?`"],
   ["`Connection failed`", "`Não conectei em localhost:5432 — o banco está no ar? 'docker compose up banco' sobe o do projeto.`"]]}},

 {"callout": {"tipo": "dica", "titulo": "Nenhuma mensagem cita tipo do Python", "texto": "`int`, `str`, `list`, `dict` e `NoneType` não existem nesta linguagem, e uma mensagem nesses termos manda a pessoa procurar na documentação errada — ela não tem como saber que `list` é `Cluster`. Há teste sobre o **código** do interpretador proibindo `type(x).__name__` dentro de f-string de mensagem: foi assim que cinco delas chegaram lá, e a trava achou outras três que ninguém tinha visto."}},

 {"p": "Continue em [Erros](/docs/erros) e [O vault de opções](/docs/bibliotecas/opcoes)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/documentar",
"title": "Documentar uma biblioteca",
"description": "dataforge doc, o exemplo que roda — e a única trava que impede a documentação de envelhecer.",
"blocos": [
 {"p": "Documentação apodrece calada: o código muda, o texto fica, e ninguém descobre até alguém seguir a instrução e falhar. A defesa é uma só — **o exemplo tem de rodar**."},

 {"code": """// ~/ Converte reais para centavos, sem passar por float.
// ~/
// ~/   Dinheiro.centavos("19,99")   ->   1999
// ~/
// ~/ Levanta FalhaDeFormato quando o texto nao e um valor.
action centavos(texto):
    limpo := texto.replace(".", "").replace(",", "")
    yield int(limpo)

assert centavos("19,99") is 1999
assert centavos("1.234,50") is 123450""", "lang": "df"},

 {"code": """dataforge doc src/ --out=doc/API.md     # o Markdown, a partir dos comentarios
dataforge doc src/ --formato=json       # para gerar um site""", "lang": "bash"},

 {"h2": "A trava: extrair e executar"},

 {"p": "É o que este repositório faz com a própria documentação — 67 páginas geradas, e **todo bloco marcado como DataForge é extraído e executado** antes de a página existir. Nenhuma promessa da documentação sobrevive a uma mudança que a contradiga."},

 {"code": """# no CI da sua biblioteca
dataforge check .          # o que nem chega a rodar
dataforge test .           # os testes
python3 scripts/rodar_exemplos_da_doc.py   # cada bloco do README""", "lang": "bash"},

 {"callout": {"tipo": "atencao", "titulo": "Um número escrito à mão envelhece sem ninguém ver", "texto": "Uma página desta documentação anunciava *“Funções (28)”* onde havia **44** — e a contagem estava no **título** da seção, que é o que se lê antes da lista. A descrição de um pacote `.deb` dizia *“38 módulos”* quando eram 39. A correção não é conferir de novo: é a contagem sair do próprio módulo, por `inspect`."}},

 {"h2": "O README é a primeira página"},

 {"table": {"head": ["Tem de responder", "Em quantas linhas"], "rows": [
   ["o que esta biblioteca faz", "1"],
   ["como instalar", "1 comando"],
   ["o menor exemplo **completo** que funciona", "até 15 linhas"],
   ["o que ela **não** faz", "3 a 5 linhas"],
   ["onde está o resto", "1 link"]]}},

 {"callout": {"tipo": "dica", "titulo": "Diga o que ela não faz", "texto": "É a seção que mais economiza tempo de quem lê, e a que quase ninguém escreve. Uma biblioteca de datas que diz logo *“não trata fuso horário”* poupa meia hora a cada pessoa que precisa disso — e evita uma issue por mês."}},

 {"p": "Continue em [dataforge doc](/docs/cli/doc) e [Testes de biblioteca](/docs/bibliotecas/testes)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/desempenho",
"title": "Prometer desempenho",
"description": "A média esconde a cauda, o teste t supõe o que não vale, e a primeira medida nunca pode reprovar.",
"blocos": [
 {"p": "Uma biblioteca que promete *“3% mais rápida”* precisa de uma medida que sustente a frase. Quase toda medida ingênua não sustenta."},

 {"h2": "O teste que mais importa"},

 {"callout": {"tipo": "atencao", "titulo": "Compare uma ação com ela mesma, e exija “empate”", "texto": "Uma ferramenta de comparação que responde *“3% mais rápida”* a isso é **pior que nenhuma ferramenta** — é assim que se escolhe a implementação errada com convicção. É o primeiro teste a escrever, antes de medir qualquer coisa real."}},

 {"table": {"head": ["Erro", "Por quê", "O que fazer"], "rows": [
   ["comparar médias", "a média esconde a cauda, que é o que o usuário sente", "percentis — P50, P95, P99"],
   ["teste t", "tempo não é normal: cauda longa, piso duro, picos de escalonamento", "Mann-Whitney, com correção de empates"],
   ["medir A inteiro, depois B", "uma queda de clock no meio vira *“B é mais lenta”*", "**intercalar** as medições"],
   ["o valor de `p` sozinho", "alfa de 0,05 *significa* 1 em 20 falsos positivos", "exigir também o **efeito**, com piso"],
   ["limite absoluto em ms", "mede a **máquina**, não o código", "cobrar um **fator**"]]}},

 {"h2": "A razão não basta, se o trabalho for pequeno"},

 {"p": "Um teste de paralelismo comparou razão — o padrão correto — e falhou com **1,47**: o paralelo levou 0,44 s contra 0,30 s da série. O paralelismo estava certo; o que dominou foi o **custo de criar cinco threads**, que no Windows passa de 60 ms de trabalho."},

 {"code": """// Subir a espera de 0,06 s para 0,25 s resolveu: a serie vira
// ~1,25 s e o tempo de partida deixa de aparecer na conta.
//
// A regra: de o numerador maior, em vez de afrouxar o limite.
// Quatro tarefas em vez de duas; blocos de 300 mil em vez de 150.

adopt Arcane.Bench as B

acao := lambda teto: sum([n * n cycle n in range(1, teto)])
m := B.medir(acao, 20000, 5)
assert m["ms"] bigger_eq 0.0
out $"{m['repeticoes']} repeticoes, {m['ms']} ms\"""", "lang": "df"},

 {"h2": "O ponto de calibração"},

 {"p": "Quando nem o fator basta, meça **um algoritmo conhecidamente linear no mesmo instante**. Se ele não der ~2 ao dobrar o `n`, a máquina não está medindo — e o teste diz isso e **pula**."},

 {"callout": {"tipo": "dica", "titulo": "Medido, com seis threads queimando CPU", "texto": "O linear foi de 1,98 para **3,30–4,90** e o quadrático de 4,17 para **9,66–14,26**. Mais repetições não salvam: o `Bench` já usa o **menor** tempo de N, e a disputa sustentada atinge todas as amostras. E a calibração não deixa de proteger nada — se o código virasse quadrático, a referência continuaria em 2."}},

 {"table": {"head": ["Regra do CI", "Porque"], "rows": [
   ["a **primeira** medida nunca reprova", "um CI que nasce vermelho por desenho é desligado no mesmo dia"],
   ["a tolerância é **obrigatória**", "sem ela, todo CI fica vermelho por ruído de máquina — o que dá no mesmo"]]}},

 {"p": "Continue em [Arcane.Perfil](/docs/biblioteca/perfil) e [Percentis, e a cauda](/docs/observabilidade/perfil)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/seguranca",
"title": "A biblioteca como superfície",
"description": "O que um pacote pode fazer na máquina de quem instala — e as cinco guardas que reduzem isso.",
"blocos": [
 {"p": "Uma biblioteca roda com **toda a autoridade** do programa que a adotou: o disco, a rede, as variáveis de ambiente. Quem a publica assume isso."},

 {"h2": "As cinco guardas"},

 {"table": {"head": ["Guarda", "O ataque que ela corta"], "rows": [
   ["o `sha256` no lock", "o tarball trocado numa versão já publicada"],
   ["a extração que recusa `../` e link simbólico", "*Zip Slip*: escrever fora da pasta do pacote"],
   ["o tarball reprodutível", "um sha256 que muda sozinho e não significa nada"],
   ["`relay` explícito", "o auxiliar interno virar contrato por acidente"],
   ["zero dependência transitiva escondida", "cada dependência nova é uma decisão visível no `forge.toml`"]]}},

 {"h2": "O que a sua biblioteca não deve fazer"},

 {"table": {"head": ["Não", "Porque"], "rows": [
   ["ler variável de ambiente por conta própria", "o segredo do usuário vira seu, e ele não escolheu isso"],
   ["escrever fora da pasta que recebeu", "`~/.config` de quem instalou não é seu"],
   ["abrir rede na importação", "um `adopt` não pode ter efeito; e o CI de outra pessoa quebra sem rede"],
   ["registrar telemetria calada", "é o que faz uma biblioteca ser removida de uma empresa inteira"],
   ["embutir uma chave, mesmo de teste", "ela vira exemplo, e o exemplo vira produção"]]}},

 {"h2": "A varredura de segredo"},

 {"code": """adopt Arcane.Seguranca as S

achados := S.procurar_segredos("token := \\"ghp_\\" + gerar()")
out $"{len(achados)} achado(s)"

// Numa biblioteca, a varredura roda no CI antes do 'pack'.
// Ela e conservadora de proposito: um falso alarme num repositorio
// que fala SOBRE seguranca ensina a ignorar a varredura inteira —
// e foi o que aconteceu aqui, com 19 falsos positivos no proprio
// material didatico antes de a lista de excecoes existir.

assert typeof(achados) is "Cluster\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "A capacidade limita o `adopt`, e não o que foi entregue", "texto": "`Arcane.Capacidade` recusa o `adopt` de um módulo fora da lista, pelo nome da capacidade que falta. Ela **não tira o que já foi passado** — e isso é o modelo, não uma limitação: numa linguagem de capacidade, poder é o que se **passa**, não o que está no ar. Um módulo que prometesse contenção total seria usado onde não pode, e a descoberta viria por incidente."}},

 {"p": "Continue em [Segurança da informação](/docs/seguranca) e [Capacidade](/docs/seguranca/capacidade)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/ci",
"title": "O CI de uma biblioteca",
"description": "O que só quebra fora da sua máquina — e o formato de defeito que isso sempre tem.",
"blocos": [
 {"p": "A suíte local **não é o que o CI roda**, e a diferença não é detalhe. Todo defeito desta classe tem o mesmo formato: uma decisão do ambiente que o repositório não contém."},

 {"code": """name: ci
on: [push, pull_request]
jobs:
  testes:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-15, windows-latest]
        python: ["3.10", "3.13"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python }}" }
      - run: pip install dataforge-lang
      - run: dataforge check . --strict
      - run: dataforge fmt . --check
      - run: dataforge test . --cobertura --minimo=80
      - run: dataforge install && dataforge test .   # numa pasta limpa""", "lang": "yaml"},

 {"h2": "As cinco do Windows"},

 {"table": {"head": ["Sintoma", "Causa"], "rows": [
   ["`[Errno 22]` com o caminho mutilado", "`\"C:\\temp\"` numa string: `\\t` é tabulação. Em macOS e Linux é **pior** — o nome é válido, e o arquivo nasce em outro lugar sem erro nenhum"],
   ["traceback depois de o pacote estar pronto", "`which` é do Unix; use `shutil.which`, que também conhece `PATHEXT`"],
   ["`WSAEINVAL (10022)`", "`getsockname` num socket ainda **não ligado**; no Unix devolve 0"],
   ["a conexão “expira” onde devia ser recusada", "o firewall **descarta** o SYN de uma porta fechada"],
   ["saída ilegível de um subprocesso", "a saída do Windows não é UTF-8 — declare `encoding`"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Um runner que não existe não dá erro: ele nunca começa", "texto": "O primeiro release deste projeto ficou meia hora com um job em `queued` enquanto os outros três terminavam — sem mensagem, sem falha, sem prazo. `macos-13` tinha sido **retirado** pelo GitHub. Não havia histórico dizendo que aquele runner nunca tinha funcionado, porque era o primeiro release. Prenda os rótulos de runner a uma lista conferida."}},

 {"h2": "O relatório também mente"},

 {"table": {"head": ["O quê", "O efeito"], "rows": [
   ["`pytest -rf` lista o que **falhou**, não o que deu **erro**", "11 erros invisíveis no resumo por meses — use `-rfE`"],
   ["o resumo corta no primeiro `\\n`", "a anotação do job mostrou a **primeira linha de um stdout de sucesso** como motivo de reprovação"],
   ["o que é gerado fora do repositório não existe no CI", "todo pacote saiu com o manifesto e **zero** JavaScript, porque a compilação só rodava nesta máquina"]]}},

 {"p": "Continue em [Prometer desempenho](/docs/bibliotecas/desempenho) e [DevOps](/docs/devops)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/ponte",
"title": "Embrulhar uma biblioteca do Python",
"description": "Quando vale, o que a ponte não converte — e a promessa que o seu pacote passa a quebrar.",
"blocos": [
 {"p": "`adopt Python.numpy as np` traz qualquer biblioteca do Python. Numa **aplicação**, é conveniência. Numa **biblioteca publicada**, é uma decisão que passa para quem instala."},

 {"callout": {"tipo": "atencao", "titulo": "A dependência deixa de ser zero — e o `forge.toml` não sabe disso", "texto": "`dataforge/` não tem dependência externa, e é isso que faz `pip install dataforge-lang` bastar numa máquina sem compilador. No momento em que o **seu** pacote adota `Python.lxml`, quem o instalar precisa daquele pacote também — e o gerenciador não vai instalá-lo. Declare no README, e falhe com uma mensagem que diga o comando."}},

 {"h2": "A ponte não converte"},

 {"code": """// Um 'ndarray' continua um 'ndarray'. E o que faz 'a * 2' ser a
// conta vetorizada do numpy, e nao um laco sobre um milhao de
// posicoes.
//
// Isso so funciona porque o interpretador trata objeto estranho por
// PROTOCOLO — membro, metodo, indice, 'len', iteracao, aritmetica,
// texto e verdade ja passavam assim. Trocar protocolo por
// 'isinstance' em qualquer um deles quebraria a ponte inteira.

// E 'typeof' tem uma excecao de proposito: 'np.int64' nao e
// subclasse de 'int', mas faz conta de inteiro — entao ele responde
// 'Integer'. Nao ha nada de numpy no interpretador: 'Fraction' e
// 'Decimal' entram pela mesma porta.

out "a ponte e por protocolo, e nao por tipo\"""", "lang": "df"},

 {"h2": "Quando vale, e quando não"},

 {"table": {"head": ["Vale", "Não vale"], "rows": [
   ["o trabalho é numérico pesado (numpy, scipy)", "a biblioteca já existe em `Arcane.*`"],
   ["um formato binário complexo com implementação madura", "dá para escrever em 200 linhas sem dependência"],
   ["um driver que fala um protocolo proprietário", "só para economizar uma tarde"],
   ["a conta é o gargalo **medido**", "*“pode vir a ser mais rápido”*"]]}},

 {"h2": "A falha tem de nomear o Python exato"},

 {"p": "O instalador cria uma venv em `~/.dataforge`, e um `pip install` no terminal instala em **outro** Python. Uma mensagem que só diz *“módulo não encontrado”* manda a pessoa rodar o comando que já não funcionou."},

 {"table": {"head": ["Ambiente", "O que a mensagem deve dizer"], "rows": [
   ["venv do instalador", "o caminho do Python que está rodando"],
   ["executável único", "`pip install dataforge-lang` — ali não há `pip` nenhum"],
   ["`pip install -e .`", "o `pip` do próprio ambiente"]]}},

 {"p": "Continue em [A ponte](/docs/tecnicas/ponte) e [As formas de adopt](/docs/modulos/adopt)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/bibliotecas/exemplos",
"title": "Quatro bibliotecas de verdade",
"description": "Os pacotes deste repositório, e a decisão de desenho que cada um demonstra.",
"blocos": [
 {"p": "`packages/` tem quatro bibliotecas escritas em DataForge, publicadas no registro do site e somando 46 testes. Elas servem de referência — e de prova de que o gerenciador funciona ponta a ponta."},

 {"table": {"head": ["Pacote", "O quê", "A decisão que ele demonstra"], "rows": [
   ["`validador`", "CPF, CNPJ, e-mail e esquema de formulário", "a validação devolve **o motivo**, e não `no`"],
   ["`tabela`", "saída para terminal", "medir a largura do que é impresso, e não do que é guardado"],
   ["`datas`", "datas em pt-BR, com feriados", "o que a biblioteca **não** faz: fuso horário"],
   ["`cofre`", "configuração em camadas", "a ordem das fontes é o recurso"]]}},

 {"h2": "O validador: o motivo, e não o booleano"},

 {"code": """action validar_cpf(texto):
    digitos := "".join([c cycle c in texto given c.isdigit()])
    given len(digitos) is 0:
        yield {"ok": no, "motivo": "vazio"}
    given len(digitos) is not 11:
        yield {"ok": no, "motivo": $"tem {len(digitos)} digitos, e nao 11"}
    given digitos is digitos[0] * 11:
        yield {"ok": no, "motivo": "todos os digitos iguais"}
    yield {"ok": yes, "motivo": ""}

assert validar_cpf("529.982.247-25")["ok"]
out validar_cpf("111.111.111-11")["motivo"]
out validar_cpf("123")["motivo"]""", "lang": "df"},

 {"callout": {"tipo": "dica", "titulo": "Um validador que devolve `no` obriga o chamador a adivinhar", "texto": "E o que ele adivinha vai para a tela do usuário final: *“CPF inválido”* é a mensagem mais inútil de um formulário. Devolver o motivo custa um vault e resolve o problema onde ele aparece."}},

 {"h2": "O cofre: a ordem é o recurso"},

 {"code": """// A ordem e sempre a mesma, e e ela que faz um segredo de producao
// vencer o padrao do arquivo sem ninguem editar nada:
//
//   padrao  <  arquivo  <  ambiente  <  argumento de linha

action resolver(padrao, arquivo, ambiente, argumento):
    valor := padrao
    cycle fonte in [arquivo, ambiente, argumento]:
        given fonte is not void:
            valor := fonte
    yield valor

assert resolver(5432, 5433, void, void) is 5433
assert resolver(5432, 5433, 6000, void) is 6000
assert resolver(5432, 5433, 6000, 7000) is 7000""", "lang": "df"},

 {"code": """cd packages/validador
dataforge test .
dataforge pack
dataforge publish --registry=../../site/public/registry""", "lang": "bash"},

 {"p": "Continue em [Estrutura](/docs/bibliotecas/estrutura) e [Publicar](/docs/bibliotecas/publicar)."},
]},
]
