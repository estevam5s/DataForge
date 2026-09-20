"""Versões lado a lado, o workspace e o cache de árvores.

Os três últimos itens da lista de "o que falta" — e os três existiam
pela metade: o campo `project.dataforge` já sabia declarar a versão
exigida e **ninguém o cobrava**, cada pacote tinha o seu `forge.toml` e
nada olhava a árvore, e o lexer refazia a cada execução a mesma árvore a
partir de um arquivo que não mudou.

Todo bloco `df` destas páginas RODA (`tests/test_seis_pendencias.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/cli/versoes",
"title": "Versões lado a lado",
"description": "versions, use, switch e upgrade: uma venv por versão, o pino no forge.toml — e o pino é cobrado, não apenas mostrado.",
"blocos": [
 {"p": "Havia um jeito de **instalar** e nenhum de **escolher**: trocar de versão era reinstalar por cima, e não havia como dizer *\"este projeto roda na 1.0.0\"*."},
 {"callout": {"tipo": "perigo", "titulo": "E metade do mecanismo já existia, sem ninguém cobrar", "texto": "O campo `project.dataforge` do `forge.toml` existia, e `Manifest.requires()` já sabia ler `>=`, `^` e `~`. **O único lugar que os usava era `dataforge info`, para mostrar na tela.** Um pino que não é cobrado não é um pino: é um comentário com sintaxe."}},

 {"h2": "Onde as versões moram"},
 {"code": """~/.dataforge/
├── versoes/
│   ├── 1.0.0/          uma venv por versao
│   └── 2.0.0/
└── atual               a escolha GLOBAL""", "lang": "text", "title": "a raiz — ou DATAFORGE_RAIZ"},
 {"p": "`DATAFORGE_RAIZ` troca a raiz. Não é um detalhe de conveniência: é o que torna tudo isto **testável** sem mexer na instalação de quem está rodando os testes."},
 {"code": """dataforge versions            # o que existe, o que roda, o que o projeto exige
dataforge upgrade             # instala a mais nova AO LADO
dataforge upgrade 1.0.0 --check   # so diz o que faria
dataforge use 1.0.0           # fixa no projeto (forge.toml)
dataforge use 1.0.0 --global  # fixa para a maquina
dataforge switch 1.0.0        # o mesmo comando, outro nome""", "lang": "bash"},

 {"h2": "O pino é cobrado — senão `use` seria um gesto"},
 {"p": "`dataforge run` num projeto que exige outra versão **entrega a execução a ela**. São três saídas, e a terceira é a que importa:"},
 {"table": {"head": ["Situação", "O que acontece"], "rows": [
   ["não há pino, ou ele é satisfeito", "segue nesta versão, e o custo é uma leitura de `forge.toml`"],
   ["há pino e a versão está instalada", "**troca** (`os.execve`), e a outra versão recebe os mesmos argumentos"],
   ["há pino e ela **não** está instalada", "**recusa**, com o comando que a instala"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Por que recusar, e não avisar", "texto": "Rodar na versão errada é exatamente o que o pino existe para impedir. Um aviso seria ignorado na segunda vez, e a diferença entre as versões aparece como um defeito no código de quem escreveu — não como um problema de versão. `DATAFORGE_SEM_TROCA=1` ignora o pino quando você quer, uma vez."}},
 {"code": """$ dataforge run main.df
Erro: o projeto exige DataForge 9.9.9, e esta e a 1.0.0, e a 9.9.9 nao esta instalada.
      dataforge upgrade 9.9.9
      dataforge versions          (o que existe aqui)
      DATAFORGE_SEM_TROCA=1 dataforge run …   (ignorar o pino, uma vez)""", "lang": "bash", "title": "a recusa, com as três saídas"},
 {"p": "E uma marca no ambiente impede a troca de acontecer **duas vezes**: um executável mal configurado que apontasse para si mesmo entraria em laço, e um laço na partida é o defeito mais difícil de interromper."},

 {"h2": "O manifesto é de uma pessoa, e não é reformatado"},
 {"p": "`use` reescreve o `forge.toml` **linha a linha**. Serializar o TOML de novo a partir da estrutura apagaria comentários e reordenaria campos — e um comando que mexe num arquivo de configuração não pode reformatá-lo por baixo."},
 {"code": """# o meu projeto            <- o comentario fica
[project]
name = "loja"
version = "0.1.0"
entry = "main.df"
dataforge = "1.0.0"        <- entra DENTRO da secao, na ultima linha dela

[dependencies]             <- e a outra secao continua onde estava""", "lang": "text", "title": "forge.toml depois de 'dataforge use 1.0.0'"},
 {"p": "O campo entra depois da **última linha com conteúdo** da seção, e não no fim dela: uma linha em branco separa as seções, e inserir depois dela punha o campo do `[project]` visualmente na seção seguinte. Fixar de novo **troca** em vez de duplicar."},

 {"h2": "O que não existe, e é o limite"},
 {"table": {"head": ["Não há", "Consequência"], "rows": [
   ["um *shim* no PATH", "o `dataforge` que você chama é o que está instalado, e é ele que redireciona — quem instala a 2.0.0 e quer que ela atenda direto ainda precisa reinstalar"],
   ["troca no `check`, no `fmt` e nos outros", "a troca vale no `run`. Conferir sintaxe numa versão vizinha quase nunca muda a resposta, e re-executar todo comando dobraria a partida"],
   ["instalação sem rede", "`upgrade` usa `pip`. Sem rede, `--check` mostra os passos que ele daria"]]}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/cli/workspace",
"title": "A árvore inteira, e os conflitos dela",
"description": "Vários pacotes num repositório: quem depende de quê, e duas faixas incompatíveis do mesmo terceiro — achadas antes de instalar.",
"blocos": [
 {"p": "Cada pacote tem o seu `forge.toml`. A única forma de saber se dois deles pedem faixas **incompatíveis** do mesmo terceiro era instalar os dois e esperar o erro — que aparece no dia da instalação, na máquina de quem consome."},
 {"code": """dataforge workspace              # a arvore daqui para baixo
dataforge workspace packages     # so uma pasta
dataforge workspace --json       # para o CI ler
dataforge ws                     # o mesmo comando""", "lang": "bash"},
 {"code": """── 25 pacote(s) em packages ──
  aleatorio            0.1.0      0 dep(s)  aleatorio/forge.toml
  validador            0.1.0      1 dep(s)  validador/forge.toml
  …

  nenhum conflito de faixa entre os pacotes""", "lang": "text", "title": "dataforge workspace — a saída"},

 {"h2": "Conflito é erro, e não aviso"},
 {"p": "O comando **sai com 2** quando duas faixas não se cruzam. É a mesma decisão que o resolvedor de dependências já tomava: instalar duas cópias do mesmo pacote em versões diferentes gera bug irreproduzível."},
 {"code": """  CONFLITOS:
   terceiro
      um pede 1.0.0
      dois pede 2.0.0""", "lang": "text"},
 {"callout": {"tipo": "nota", "titulo": "A interseção sai da MESMA classe que o `add` usa", "texto": "`Requisito`, de `packages.py`. Uma segunda noção de *\"estas faixas se cruzam?\"* divergiria da instalação — e aí o relatório aprovaria o que o `add` recusa, que é o pior resultado possível para duas respostas da mesma pergunta."}},

 {"h2": "Ele não inventa conflito"},
 {"p": "Sem uma lista das versões publicadas não há como decidir por enumeração. Então a pergunta é feita sobre os **pinos exatos**: se um lado exige `==X` e o outro recusa o `X`, o conflito está **provado**. Fora disso, cala."},
 {"table": {"head": ["Um pede", "O outro pede", "Veredito"], "rows": [
   ["`1.0.0`", "`2.0.0`", "**conflito** — o pino de um é recusado pelo outro"],
   ["`^1.0.0`", "`>=1.0.0`", "cala — as faixas podem se cruzar"],
   ["`^1.0.0`", "`1.5.0`", "cala — `1.5.0` satisfaz `^1.0.0`"]]}},
 {"p": "É a mesma prudência do [analisador estático](/docs/tecnicas/analise-estatica): um falso conflito faria o comando ser ignorado, e aí ele não serviria para o caso verdadeiro."},

 {"h2": "E ele não instala"},
 {"p": "Ler e relatar. Instalar a árvore inteira a partir de um comando que a pessoa rodou para *\"ver o que tem\"* seria mexer em disco sem ser pedido — quem quer instalar chama `dataforge install`, em cada pacote."},
 {"p": "As pastas que não são pacote do projeto ficam fora da varredura: `forge_modules`, `node_modules`, `dist`, `out`, `.venv` e as que começam com ponto."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/cli/cache",
"title": "O cache de árvores",
"description": "O lexer e o parser refaziam a mesma árvore a cada execução. Medido: 93% menos na fase de parse — e 4,4% num arquivo só, que também é o número.",
"blocos": [
 {"p": "A cada execução, o lexer e o parser refazem **exatamente a mesma coisa** a partir de um arquivo que não mudou. O cache guarda a árvore."},
 {"callout": {"tipo": "atencao", "titulo": "Ele NÃO é um cache de fechamentos", "texto": "`compilador.py` transforma a árvore em funções Python, e função não atravessa processo — não há o que guardar. Chamar isto de \"cache de compilação\" seria prometer o que ele não faz: o que se guarda é a **árvore**."}},

 {"h2": "O número, e os dois números"},
 {"table": {"head": ["Medida", "Sem cache", "Com cache"], "rows": [
   ["a fase de parse, 269 arquivos", "258,7 ms", "**17,9 ms** — 93% menos"],
   ["`dataforge check exercicios` (real, 269 arquivos)", "0,918 s", "**0,524 s** — 43% menos"],
   ["`dataforge run` num arquivo de 383 linhas", "131,8 ms", "~126 ms — **4,4%**"]]}},
 {"p": "A terceira linha é a desconfortável, e por isso está aqui: **76 ms dos 132 ms** daquele comando são o `import` do próprio Python. O cache vale onde há **muitos** arquivos — o `check` de um projeto, a CI — e quase não aparece num script pequeno. Publicar só a primeira medida seria escolher a medida."},
 {"p": "O cache dos 269 arquivos ocupa **1553 KB**."},

 {"h2": "A chave é o que impede o desastre"},
 {"p": "Um cache que devolve a árvore errada é **pior que nenhum cache**: o programa roda, e roda outra coisa. A chave carrega cinco coisas:"},
 {"list": ["o caminho absoluto do arquivo;", "o `mtime_ns` e o tamanho dele;", "a versão da linguagem;", "o formato do que é guardado;", "e um **resumo da própria implementação** — `lexer.py`, `parser.py`, `ast_nodes.py`, `tokens.py` e `tipos_nomeados.py`."]},
 {"callout": {"tipo": "perigo", "titulo": "O último é o que importa durante o desenvolvimento", "texto": "Mexer no parser sem subir a versão não invalidaria nada, e a execução seguinte leria uma árvore que o parser de hoje **não produz mais**. É o erro mais difícil de diagnosticar que um cache pode causar, porque nada acusa: o programa roda. Há teste tocando o `mtime` do `parser.py` e exigindo que o cache se invalide."}},

 {"h2": "Falhar não pode custar nada"},
 {"table": {"head": ["Se", "Então"], "rows": [
   ["o arquivo do cache está corrompido", "refaz o parse, sem levantar"],
   ["a versão de `pickle` é outra", "refaz o parse"],
   ["não há permissão de escrita", "roda sem guardar"],
   ["o processo morreu no meio da gravação", "não há arquivo pela metade: escreve ao lado e renomeia, e `os.replace` é atômico no POSIX e no Windows"]]}},
 {"p": "**Uma otimização nunca pode ser um motivo de erro.** Toda leitura do cache está num `try`, e toda falha cai no caminho normal."},

 {"h2": "Ligar, desligar, limpar"},
 {"code": """DATAFORGE_SEM_CACHE=1 dataforge check src/   # desliga, para medir
DATAFORGE_CACHE=/tmp/meu dataforge check src/ # outra pasta
dataforge clean                               # apaga o cache de arvores""", "lang": "bash"},
 {"p": "`dataforge clean` **sempre** apaga o cache de árvores, e diz quantos arquivos tirou. Deixá-lo para trás faria o `clean` mentir sobre o que limpou — e é justamente o lugar onde um artefato velho engana."},
 {"p": "A prova de que ele é seguro não é o desenho: é o teste que roda exercícios do repositório com a árvore do cache e sem ela, e compara a saída **caractere por caractere** — a mesma rede de segurança do [compilador de fechamentos](/docs/compilador/backend)."},
]},
]
