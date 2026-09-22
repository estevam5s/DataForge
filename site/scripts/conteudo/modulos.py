# -*- coding: utf-8 -*-
"""O sistema de módulos, em nível de especificação."""

PAGINAS = [
{
"href": "/docs/modulos",
"title": "O sistema de módulos",
"description": "adopt e relay — o que é público, onde mora cada módulo, e como isso se compara a CommonJS e a ECMAScript.",
"blocos": [
 {"p": "Toda linguagem grande acaba precisando responder quatro perguntas sobre módulos: **o que um arquivo oferece**, **onde mora o que ele pede**, **quantas vezes ele carrega** e **o que acontece quando dois se pedem em círculo**. Esta seção responde as quatro, com o comportamento medido — não com a intenção."},
 {"p": "As duas palavras:"},
 {"code": """adopt Arcane.Math as Math          // o módulo inteiro, com apelido
adopt Arcane.Math.{sqrt, floor}    // só o que interessa
adopt {sqrt as raiz} from Arcane.Math
adopt ./util as U                  // um arquivo vizinho

relay somar, Ponto                 // o que ESTE arquivo oferece
""", "lang": "df"},

 {"h2": "Ao lado de CommonJS e ECMAScript"},
 {"p": "A tabela existe para quem chega de uma das duas. Onde a DataForge difere, ela difere de propósito, e a coluna da direita diz por quê."},
 {"table": {"head": ["Pergunta", "CommonJS", "ECMAScript (ESM)", "DataForge"], "rows": [
   ["importar", "`require('x')`", "`import x from 'x'`", "`adopt x as X`"],
   ["exportar", "`module.exports =`", "`export`", "`relay`"],
   ["export padrão", "sim (`module.exports`)", "sim (`export default`)", "**não existe**"],
   ["quando resolve", "em execução", "antes de executar", "em execução, e o `check` confere antes"],
   ["carrega quantas vezes", "uma", "uma", "**uma**"],
   ["o que é público sem declarar", "nada", "nada", "**tudo**"],
   ["ciclo", "devolve o parcial", "vive com TDZ", "**erro**"],
   ["import dinâmico", "`require()` em qualquer lugar", "`import()`", "não existe"],
   ["ordem de `export`", "irrelevante", "içado", "**depois** da declaração"]]}},
 {"callout": {"tipo": "nota", "titulo": "Sem export padrão, de propósito", "texto": "O `export default` obriga quem importa a inventar um nome, e dois arquivos que importam o mesmo módulo o chamam de coisas diferentes. Aqui o nome vem de quem escreveu (`relay somar`) ou do apelido explícito (`as U`) — e procurar por `somar` no projeto acha todos os usos."}},

 {"h2": "Tudo é público até você dizer o contrário"},
 {"p": "Um arquivo **sem** `relay` oferece tudo o que declara no topo. É o oposto do padrão de CommonJS e ESM, e a razão é o arquivo pequeno: obrigar um `relay` num módulo de três ações é cerimônia sem ganho."},
 {"code": """interno := 42

action publica():
    yield "oi"
""", "lang": "df", "title": "aberto.df"},
 {"code": """adopt ./aberto as A
out A.publica(), A.interno       // oi 42 — os dois visíveis
""", "lang": "df"},
 {"p": "**O primeiro `relay` fecha a porta.** A partir dele, o arquivo declara o que exporta, e o resto vira interno:"},
 {"code": """interno := 42

action publica():
    yield "oi"

relay publica          // agora 'interno' não atravessa mais
""", "lang": "df"},
 {"p": "Essa é também a fronteira que o analisador usa: um módulo com `relay` diz o que é contrato, e `A.interno` passa a ser acusado **antes de rodar**."},

 {"h2": "`relay` vem depois, e isso não é detalhe"},
 {"p": "Em JavaScript, `export function f(){}` funciona em qualquer posição, porque a declaração é içada. Aqui o `relay` **lê** os nomes que já existem:"},
 {"code": """relay usar              // erro: 'usar' ainda não existe

action usar():
    yield 1
""", "lang": "df"},
 {"code": """erro: 'usar' is not defined
  dica: define it before the 'relay', or remove it from the list
""", "lang": "text"},
 {"p": "A forma certa é o `relay` no fim do arquivo, que é também onde ele se lê melhor — a última linha responde \"o que este arquivo oferece?\" sem obrigar a percorrer tudo."},

 {"h2": "Um módulo carrega uma vez, e o estado é compartilhado"},
 {"p": "Como em CommonJS e em ESM. Dois arquivos que adotam o mesmo módulo recebem **o mesmo** módulo — e o estado dele é único no programa:"},
 {"code": """out "carregando contador.df"
total := 0

action somar():
    total += 1
    yield total

relay somar
""", "lang": "df", "title": "contador.df"},
 {"code": """adopt ./contador as C

action usar():
    yield C.somar()

relay usar
""", "lang": "df", "title": "a.df"},
 {"code": """adopt ./contador as C
adopt ./a as A

out C.somar()      // 1
out A.usar()       // 2  — o MESMO contador
out C.somar()      // 3
""", "lang": "df", "title": "main.df"},
 {"code": """carregando contador.df
1
2
3
""", "lang": "text", "title": "saída"},
 {"p": "A mensagem de carga aparece **uma vez**. É o que torna um módulo um bom lugar para configuração e um lugar perigoso para estado mutável: `total` acima é global ao programa, e duas rotas de um servidor escrevendo nele perdem atualizações — ver [concorrência](/docs/tecnicas/concorrencia)."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/modulos/resolucao", "title": "Resolução", "desc": "o algoritmo exato: onde a linguagem procura, e em que ordem"},
   {"href": "/docs/modulos/carga", "title": "Carga e ciclos", "desc": "quando o arquivo executa, e o que acontece num círculo"},
   {"href": "/docs/modulos/superficie", "title": "A superfície", "desc": "como o analisador atravessa a fronteira e confere a chamada"},
   {"href": "/docs/modulos/templates", "title": "Templates", "desc": "a camada de visão, e por que ela não é a linguagem"},
   {"href": "/docs/bibliotecas", "title": "Escrever uma biblioteca", "desc": "do primeiro arquivo ao pacote publicado"}]},

 {"h2": "Mais sobre módulos"},
 {"p": "Renomear sem quebrar quem importa, esconder o interno, quebrar um ciclo, e dividir um arquivo que cresceu demais."},
 {"cards": [{"href": "/docs/modulos/renomear", "title": "Renomear sem quebrar", "desc": "relay novo as antigo — o nome novo e o velho, o mesmo objeto, e o abi dizendo que é compatível."}, {"href": "/docs/modulos/fachada", "title": "A fachada: um index.df", "desc": "relay from ./x — reunir vários módulos internos numa API só, e esconder o resto."}, {"href": "/docs/modulos/ciclos", "title": "Ciclos de import", "desc": "Por que A → B → A não sobe, como o check mostra a cadeia, e as três formas de quebrá-la."}, {"href": "/docs/modulos/visibilidade", "title": "O que é público", "desc": "Sem relay, tudo do topo sai — inclusive o que começa com _. Só o relay esconde."}, {"href": "/docs/modulos/biblioteca-padrao", "title": "Achar na biblioteca padrão", "desc": "Os módulos Arcane, os apelidos, e como descobrir o que existe sem sair do terminal."}, {"href": "/docs/modulos/estado", "title": "O estado de um módulo", "desc": "Um módulo carrega uma vez, e o que ele guarda é compartilhado por todos que o adotam."}, {"href": "/docs/modulos/entrada", "title": "O ponto de entrada", "desc": "app.df monta, main.df sobe — e por que importar um módulo não pode ter efeito."}, {"href": "/docs/modulos/python", "title": "Adotar do Python", "desc": "adopt Python.x — o que atravessa, o que não converte, e o custo para quem instala."}, {"href": "/docs/modulos/dividir", "title": "Dividir um arquivo grande", "desc": "Quando partir, por onde partir, e como fazer isso sem quebrar quem já adota o arquivo."}]},
]},

{
"href": "/docs/modulos/resolucao",
"title": "Resolução de módulos",
"description": "O algoritmo exato: as cinco formas de pedir um módulo, e a ordem em que a linguagem procura cada uma.",
"blocos": [
 {"p": "\"Module not found\" é uma das mensagens mais frustrantes que existem, e quase sempre porque o algoritmo de busca é folclore. Aqui ele é curto o bastante para caber numa página — e é **uma implementação só**, em `resolucao.py`, usada pelo interpretador e pelo analisador."},
 {"callout": {"tipo": "atencao", "titulo": "Por que uma só", "texto": "A regra já esteve escrita em dois lugares, e eles divergiram: o analisador transformava `./mod` em `//mod`, e **todo** `adopt` relativo de **todo** projeto gerava um aviso falso — 795 de 795 num projeto de 21 mil linhas. Um aviso que está sempre errado é pior que nenhum aviso."}},

 {"h2": "As cinco formas"},
 {"table": {"head": ["O que você escreve", "Resolve contra"], "rows": [
   ["`Arcane.Math`", "a biblioteca padrão"],
   ["`Python.numpy`", "a ponte para o Python (não passa pela busca em disco)"],
   ["`./util`, `../lib/util`", "a pasta do **arquivo que escreve o import**"],
   ["`sub.modulo`", "a pasta do arquivo, depois o diretório atual"],
   ["`validador`", "`forge_modules/`, subindo até achar um `forge.toml`"]]}},
 {"p": "**Relativo resolve a partir do arquivo, nunca do diretório de onde se rodou.** É o que permite mover a pasta inteira sem quebrar nada, e o que torna a leitura do arquivo suficiente para saber o que ele importa."},

 {"h2": "A ordem, para um caminho relativo"},
 {"p": "`adopt ./util` procura, nesta ordem:"},
 {"code": """./util               (o caminho exato, se for um arquivo)
./util.df
./util/main.df
./util/src/main.df
""", "lang": "text"},
 {"p": "A ordem importa porque um arquivo e uma pasta com o mesmo nome podem coexistir. Sem ela declarada, a escolha dependeria da ordem em que o sistema de arquivos devolve os nomes."},

 {"h2": "A ordem, para um nome pontilhado"},
 {"p": "`adopt sub.modulo` troca o ponto por separador de pasta — **e só aqui**, depois de o caso relativo ter sido descartado:"},
 {"code": """<pasta do arquivo>/sub/modulo.df
<pasta do arquivo>/sub/modulo/main.df
<pasta do arquivo>/sub/modulo/src/main.df
<diretório atual>/sub/modulo.df
<diretório atual>/sub/modulo/main.df
<diretório atual>/sub/modulo/src/main.df
""", "lang": "text"},

 {"h2": "Hífen num caminho relativo"},
 {"p": "`adopt ./minha-lib as L` funciona, e não é óbvio que devesse: o lexer entrega o hífen como operador de subtração. O segmento de caminho cola `-`, `.` e dígitos ao nome exigindo **adjacência de coluna** — sem essa guarda, `a - b` viraria um arquivo chamado `a-b`."},

 {"h2": "Um pacote se importa pelo próprio nome"},
 {"p": "O teste de uma biblioteca escreve `adopt validador`, e não `adopt ../src/main`, porque precisa exercitá-la pelo caminho que um usuário usaria. A busca sobe até o `forge.toml` mais próximo e olha o `forge_modules/` dali."},
 {"code": """meu-projeto/
  forge.toml              o que você pediu      (versionado)
  forge.lock              o que foi instalado   (versionado)
  forge_modules/          os pacotes            (NÃO versionado)
  src/main.df
""", "lang": "text"},

 {"h2": "Quando não acha"},
 {"p": "A mensagem nomeia o que foi procurado, e não só o que faltou — um \"não encontrado\" sem a lista de tentativas obriga a adivinhar qual das cinco formas a linguagem achou que você estava usando."},
 {"p": "O `dataforge deps` mostra o grafo de imports do projeto e acusa ciclo, usando o mesmo `resolucao.py`. Ele já teve uma **terceira** cópia da regra — uma expressão regular que começava em `[A-Za-z_]`, de modo que `./vizinho` nunca casava — e dizia \"0 arquivos com imports próprios\" em todo projeto do repositório."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/modulos/carga", "title": "Carga e ciclos", "desc": "quando o arquivo executa, e o que acontece num círculo"},
   {"href": "/docs/pacotes", "title": "Gerenciador de pacotes", "desc": "add, install, lock e o registro estático"}]},
]},

{
"href": "/docs/modulos/carga",
"title": "Carga, ordem e ciclos",
"description": "Quando o corpo de um módulo executa, o que ele deixa para trás, e por que um ciclo é erro aqui.",
"blocos": [
 {"p": "Um `adopt` **executa** o arquivo, de cima a baixo, uma vez. Tudo o que estiver no topo dele roda — inclusive o que imprime, o que abre arquivo e o que conecta em banco."},

 {"h2": "O que roda, e quando"},
 {"code": """// config.df — tudo isto roda no primeiro 'adopt'
out "lendo a configuração"
steady PORTA := 8000
conexao := abrir_banco()          // acontece AQUI, não no primeiro uso

action porta():
    yield PORTA

relay porta
""", "lang": "df"},
 {"p": "Efeito colateral no topo de um módulo é a causa mais comum de \"por que meu teste abre conexão?\". A regra prática é a mesma de qualquer linguagem com carga única: **no topo, só declaração e constante**; o que custa fica dentro de uma ação."},

 {"h2": "Ciclo é erro, e não meia resposta"},
 {"p": "As outras linguagens escolheram conviver com o ciclo: CommonJS devolve o módulo **pela metade**, e ESM deixa o nome numa zona morta onde lê-lo é erro de execução. As duas transformam um problema de arquitetura num bug intermitente."},
 {"code": """adopt ./y as Y
action daqui():
    yield "x"
relay daqui
""", "lang": "df", "title": "x.df"},
 {"code": """adopt ./x as X
action dali():
    yield "y"
relay dali
""", "lang": "df", "title": "y.df"},
 {"code": """erro[DF0501]: Circular import: x.df → y.df → x.df.
Break the cycle by moving the shared part into a third module.
""", "lang": "text"},
 {"p": "**A cadeia inteira aparece.** Um ciclo de quatro arquivos é impossível de quebrar sem saber por onde ele passa, e a busca é em **largura** para achar o ciclo mais curto — que é o mais fácil de romper."},

 {"h2": "O `check` acha o ciclo antes de rodar"},
 {"p": "O ciclo estourava só em execução, no primeiro `adopt`, e o `check` passava limpo num projeto que não sobe:"},
 {"code": """$ dataforge check x.df
x.df:1:1: erro: circular import: x.df → y.df → x.df
    sugestão: move the shared part into a third module
""", "lang": "bash"},
 {"callout": {"tipo": "dica", "titulo": "Rode o check na PASTA", "texto": "Conferir só o arquivo de entrada não acha o ciclo: ele não está no ciclo, apenas importa quem está. `dataforge check .` percorre todos, e é a forma que o CI deve usar."}},

 {"h2": "Como quebrar um ciclo"},
 {"list": [
   "**Mova o compartilhado para um terceiro módulo.** Se `x` e `y` se pedem, quase sempre é porque ambos precisam de um tipo ou de uma constante que não é de nenhum dos dois.",
   "**Inverta a dependência.** Quem sabe *como* fazer não deveria conhecer quem *manda* fazer: passe a ação como argumento em vez de importar o chamador.",
   "**Junte os dois.** Dois arquivos que se pedem em círculo frequentemente são um só arquivo que alguém dividiu cedo demais."], "ordered": True},

 {"h2": "Ordem de execução, num programa com módulos"},
 {"code": """1. o interpretador lê o arquivo de entrada
2. cada 'adopt' do topo executa o módulo pedido, na ordem em que aparece
3. o módulo, por sua vez, executa os 'adopt' dele — em profundidade
4. um módulo já carregado NÃO executa de novo: devolve o mesmo objeto
5. o corpo do arquivo de entrada roda
6. os 'defer' escritos no topo rodam no fim, inclusive se houve erro
""", "lang": "text"},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/modulos/superficie", "title": "A superfície", "desc": "o que o analisador consegue provar sobre outro arquivo"},
   {"href": "/docs/tecnicas/concorrencia", "title": "Concorrência", "desc": "por que estado no topo de um módulo é perigoso num servidor"}]},
]},

{
"href": "/docs/modulos/superficie",
"title": "A superfície de um módulo",
"description": "Como o analisador lê o que outro arquivo oferece, sem executá-lo — e quando ele prefere calar.",
"blocos": [
 {"p": "`P.naoExiste()` e `P.criar(1, 2, 3)` são acusados **antes de rodar**, mesmo quando `P` vem de outro arquivo. É a checagem que mais importa em sistema grande: num arquivo de 40 linhas o erro aparece na primeira execução; num de 200 arquivos, a maioria das chamadas cruza módulo, e todas elas eram invisíveis."},

 {"h2": "Como ele sabe, sem executar"},
 {"p": "`superficie.py` lê o outro arquivo com o **lexer e o parser**, e não com o interpretador. Do que encontra, guarda o que atravessa a fronteira:"},
 {"table": {"head": ["Guarda", "Para conferir"], "rows": [
   ["os nomes exportados", "`P.naoExiste` — o membro que não existe"],
   ["a aridade de cada ação", "`P.criar(1, 2, 3)` com dois parâmetros"],
   ["o tipo de cada parâmetro", "`D.valor_de(texto)` onde se espera `Integer`"],
   ["o tipo de retorno", "`P.criar(…).clientte` — o campo errado, do outro lado"],
   ["os campos de cada record", "o mesmo, um nível adiante"]]}},
 {"p": "**O tipo de retorno atravessar é o que mais rende.** Sem ele, uma ação que declara `-> Pedido` virava um valor sem tipo no outro arquivo, e o campo com nome quase certo passava no `check`."},

 {"h2": "A tradução de vocabulário"},
 {"p": "O `-> Pedido` declarado lá é `P.Pedido` aqui. Devolver o nome nu faria o analisador procurar um record que este arquivo não declara — e a primeira versão fazia isso, acusando **o código certo**:"},
 {"code": """Parameter 'p' of 'P.com_total' expects Pedido but got P.Pedido
""", "lang": "text"},
 {"p": "Um falso alarme no caminho mais comum de um projeto modular ensina a desligar a verificação inteira. Hoje a tradução acontece nos dois lados, e quando não dá para concluir o analisador **cala**."},

 {"h2": "Quando ele cala"},
 {"table": {"head": ["Cala quando", "Porque"], "rows": [
   ["o outro arquivo não compila", "uma superfície lida de código quebrado é palpite"],
   ["há ciclo de import", "não há ordem em que a leitura termine"],
   ["a profundidade (4) acaba", "seguir a cadeia inteira levaria o `check` a minutos"],
   ["o `relay` nomeia algo que só existe em execução", "o nome pode ser qualquer coisa"],
   ["o módulo não exporta aquele tipo", "o tipo é interno, e o nome daqui não o alcança"]]}},
 {"p": "Em todos esses casos a superfície devolve **aberta**, e a conferência volta a ficar em silêncio. Um falso alarme é pior que um silêncio."},

 {"h2": "O escopo de quem chama"},
 {"p": "A inferência usa o escopo de **quem chama**, e não o global. Parece detalhe e não é: `D.valor_de(n)` dentro de `action f(n)` virou **\"Undefined name 'n'\"** — 649 falsos alarmes num projeto gerado de 252 arquivos, um por uso de parâmetro numa chamada entre módulos."},
 {"p": "E a suíte passava: os primeiros testes chamavam no nível de topo, onde o escopo global é o certo. O bug só aparecia dentro de uma ação, que é onde quase todo código vive. Quem pegou foi rodar o `check` no projeto grande."},

 {"h2": "O cache"},
 {"p": "A superfície é guardada por `(caminho, mtime)`. Sem isso, 200 arquivos importando três vizinhos cada levariam o `check` de 0,7 s a mais de um minuto — e um analisador que demora um minuto não roda a cada salvar, que é quando ele vale."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/tecnicas/analise-estatica", "title": "Análise estática", "desc": "tudo o que o check prova, e o que o faz calar"},
   {"href": "/docs/bibliotecas/contrato", "title": "O contrato de uma biblioteca", "desc": "o que o relay promete, e o que quebra quem depende de você"}]},
]},

{
"href": "/docs/modulos/templates",
"title": "Templates e a camada de visão",
"description": "A sintaxe de template do Kiln, ao lado de EJS e Handlebars — e por que ela é deliberadamente pequena.",
"blocos": [
 {"p": "EJS, Handlebars e Jinja resolvem o mesmo problema: montar HTML a partir de dado, sem concatenar texto à mão. A diferença entre eles é **quanta linguagem cabe dentro do template** — e essa escolha decide a manutenção do projeto inteiro."},

 {"h2": "As quatro construções"},
 {"code": """<h1>{{titulo}}</h1>
{{#produtos}}<article>{{nome}} — {{preco}}</article>{{/produtos}}
{{^produtos}}<p>Nada na forja.</p>{{/produtos}}
<footer>{{&html_bruto}}</footer>
""", "lang": "text", "title": "views/loja.html"},
 {"table": {"head": ["Forma", "O que faz"], "rows": [
   ["`{{x}}`", "escreve, **escapando HTML**"],
   ["`{{&x}}`", "escreve **sem** escapar"],
   ["`{{#lista}}…{{/lista}}`", "repete para cada item"],
   ["`{{^lista}}…{{/lista}}`", "mostra quando a lista está vazia"]]}},
 {"code": """server loja at "0.0.0.0" on 8000:
    views "views"

    route GET "/":
        render "loja" with {"titulo": "Forja", "produtos": catalogo()}
""", "lang": "df"},

 {"h2": "Ao lado de EJS e Handlebars"},
 {"table": {"head": ["", "EJS", "Handlebars", "Kiln"], "rows": [
   ["código no template", "**JavaScript inteiro**", "helpers registrados", "**nenhum**"],
   ["escapar por padrão", "não (`<%= %>` escapa, `<%- %>` não)", "sim", "**sim**"],
   ["condicional", "`if` do JS", "`{{#if}}`", "só \"vazio ou não\""],
   ["laço", "`for` do JS", "`{{#each}}`", "`{{#lista}}`"],
   ["chamar função", "sim", "helpers", "**não**"],
   ["parcial / include", "`include()`", "`{{> parcial}}`", "compor no `.df`"]]}},
 {"callout": {"tipo": "nota", "titulo": "A coluna que mais importa é a primeira linha", "texto": "Quando o template aceita a linguagem inteira, a lógica migra para lá — e vai junto o que não dá para testar sem renderizar HTML. Um template que só sabe escrever, repetir e checar vazio obriga a decisão a ficar no `.df`, onde há tipo, `check` e teste."}},

 {"h2": "O que fazer quando o template \"precisa\" de lógica"},
 {"p": "A resposta é sempre a mesma: decida antes, e passe o resultado pronto."},
 {"code": """// em vez de tentar formatar no template:
action para_a_tela(produtos):
    yield [{"nome": p.nome,
            "preco": $"R$ {round(p.preco, 2)}",
            "esgotado": p.estoque is 0}
           cycle p in produtos]

route GET "/":
    render "loja" with {"titulo": "Forja", "produtos": para_a_tela(catalogo())}
""", "lang": "df"},
 {"p": "O ganho não é estético: `para_a_tela` é uma ação comum, e testá-la não exige servidor, socket nem HTML."},

 {"h2": "Escapar é o padrão, e isso é segurança"},
 {"p": "`{{x}}` escapa. É a diferença entre um nome de produto com `<script>` virar texto na tela ou virar código no navegador de quem visita. O `{{&x}}` existe para o caso legítimo — um trecho que você mesmo gerou — e a forma mais longa é de propósito: o inseguro tem de ser escrito de caso pensado."},

 {"h2": "A outra camada de visão"},
 {"p": "Quando a página **é** o programa — um painel, uma ferramenta interna, um relatório interativo — a resposta não é template: é a [Vitrine](/docs/vitrine), onde o `.df` de cima a baixo vira a página, sem HTML nenhum."},

 {"h2": "Por onde seguir"},
 {"cards": [
   {"href": "/docs/kiln/paginas", "title": "Páginas HTML no Kiln", "desc": "views, layout e o que o render faz"},
   {"href": "/docs/vitrine", "title": "Vitrine", "desc": "a página como programa, sem template"},
   {"href": "/docs/seguranca", "title": "Segurança", "desc": "escape, CSRF, sessão e o que o framework garante"}]},
]},
]
