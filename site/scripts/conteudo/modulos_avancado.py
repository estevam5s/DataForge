# -*- coding: utf-8 -*-
"""Módulos e empacotamento — as nove páginas que faltavam.

O que já havia cobria o mecanismo (resolução, carga, ciclos,
superfície). O que faltava era o **uso**: as formas de `adopt`, o que
`relay` muda, o gerenciador de pacotes ponta a ponta, e como se
organiza um projeto que passou de duzentos arquivos.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/adopt",
"title": "As formas de adopt",
"description": "Seis formas, e o que cada uma muda — inclusive a que traz qualquer biblioteca do Python.",
"blocos": [
 {"p": "`adopt` é uma palavra e seis formas. A escolha entre elas não é estilo: ela decide o que o leitor do arquivo consegue saber sem sair dele."},

 {"code": """// 1. O modulo inteiro, com o nome dele.
adopt Arcane.Math

// 2. Com apelido — o mais comum, e o que encurta sem esconder.
adopt Arcane.Math as M

// 3. So o que se usa.
adopt Arcane.Math.{sqrt, floor}

// 4. So o que se usa, renomeando.
adopt {sqrt as raiz} from Arcane.Math

out M.PI
out sqrt(16.0)
out raiz(25.0)
assert floor(3.7) is 3""", "lang": "df"},

 {"table": {"head": ["Forma", "Quando", "O que ela custa"], "rows": [
   ["`adopt X`", "uso raro, nome curto", "o nome inteiro em cada chamada"],
   ["`adopt X as M`", "**o padrão**", "nada; o apelido diz de onde veio"],
   ["`adopt X.{a, b}`", "duas ou três funções muito usadas", "quem lê `sqrt(x)` não sabe de onde ele vem"],
   ["`adopt {a as b} from X`", "quando o nome colide", "idem, mais o nome trocado"],
   ["`adopt ./vizinho`", "arquivo do próprio projeto", "o caminho é relativo a **este** arquivo"],
   ["`adopt Python.numpy`", "biblioteca do Python", "a dependência deixa de ser zero"]]}},

 {"callout": {"tipo": "atencao", "titulo": "O import seletivo apaga a origem", "texto": "`adopt Arcane.Math.{sqrt}` faz `sqrt(x)` ficar igual a uma função do próprio arquivo — e num arquivo de trezentas linhas, quem lê no meio não tem como saber de onde ela veio sem subir até o topo. Vale para duas ou três funções de uso muito frequente; a partir daí, o apelido custa três caracteres e devolve a informação."}},

 {"h2": "Caminhos relativos"},

 {"code": """// 'adopt ./x' procura ao lado DESTE arquivo — e nao da pasta em
// que o programa foi executado. A diferenca aparece quando o mesmo
// modulo e importado de duas profundidades.
//
//   projeto/
//     src/
//       main.df          adopt ./modelos
//       modelos.df
//       admin/
//         painel.df      adopt ../modelos
//
// E o hifen funciona: 'adopt ./minha-lib as L'. O lexer entrega o
// hifen como MINUS, e o caminho so o cola ao nome quando as colunas
// sao ADJACENTES — sem essa guarda, 'a - b' viraria um arquivo
// chamado 'a-b'.

out "o caminho e relativo ao arquivo, e nao ao diretorio de trabalho\"""", "lang": "df"},

 {"h2": "A ponte para o Python"},

 {"p": "`Python` é espaço de nomes **reservado**, resolvido antes da biblioteca e dos arquivos vizinhos — um `Python.df` no disco não sequestra o import."},

 {"code": """// adopt Python.numpy as np
//
// A ponte NAO CONVERTE: um 'ndarray' continua um 'ndarray', e
// 'a * 2' e a conta vetorizada do numpy, e nao um laco sobre um
// milhao de posicoes. Isso so funciona porque o interpretador trata
// objeto estranho por PROTOCOLO — membro, metodo, indice, 'len',
// iteracao, aritmetica, texto e verdade.

out "a ponte existe, e a dependencia passa a ser sua\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Um `adopt Python.x` muda a promessa do seu projeto", "texto": "`dataforge/` não tem dependência externa, e é isso que faz `pip install dataforge-lang` bastar numa máquina sem compilador. No momento em que o **seu** código adota um módulo do Python, quem instalar o seu projeto precisa daquele pacote também — e o `forge.toml` não sabe disso. Declare no README, e prefira o que a biblioteca já resolve."}},

 {"p": "Continue em [Resolução](/docs/modulos/resolucao) e [A ponte](/docs/tecnicas/ponte)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/relay",
"title": "Relay — o que sai do módulo",
"description": "Declarar o que é público muda o que o analisador consegue provar sobre quem usa o módulo.",
"blocos": [
 {"p": "Sem `relay`, tudo que o arquivo declara no topo é visível de fora. Com `relay`, só o que está listado — e essa escolha tem uma consequência que quase ninguém espera."},

 {"code": """// biblioteca.df
action _normalizar(texto):
    yield texto.strip().lower()

action buscar(termo):
    yield $"procurando '{_normalizar(termo)}'"

record Resultado:
    titulo: String
    peso: Integer

// So estes dois saem. '_normalizar' fica dentro.
relay buscar, Resultado

out buscar("  Café  ")
assert Resultado("x", 1).peso is 1""", "lang": "df"},

 {"h2": "O que o `relay` muda no analisador"},

 {"p": "A superfície de um módulo é lida **sem executá-lo**, e é ela que permite ao `check` acusar `P.naoExiste()` antes de rodar. Quando há `relay`, a superfície é exatamente a lista; quando não há, é tudo o que o topo declara."},

 {"table": {"head": ["Com `relay`", "Sem `relay`"], "rows": [
   ["a superfície é a lista", "a superfície é tudo do topo"],
   ["mudar um auxiliar não quebra ninguém", "qualquer nome do topo virou contrato"],
   ["`P.auxiliar()` é **acusado** pelo `check`", "passa"],
   ["o `abi` compara só o que é público", "compara tudo, e todo *rename* vira quebra"]]}},

 {"callout": {"tipo": "dica", "titulo": "A superfície é conservadora de propósito", "texto": "Ela **cala** — e o `check` volta a não acusar nada — quando o outro arquivo não compila, quando há ciclo de import, quando a profundidade (4) acaba, ou quando o `relay` nomeia algo que só existe em execução. Um falso alarme entre arquivos é pior que um silêncio: ele aparece no caminho mais comum de um projeto modular, e a reação é desligar a verificação inteira."}},

 {"h2": "O que atravessa a fronteira"},

 {"p": "O `check` não confere só o **nome**: ele leva o tipo de retorno e os tipos dos parâmetros. Num sistema de duzentos arquivos a maioria das chamadas atravessa módulo, e era exatamente ali que a conferência calava."},

 {"code": """// pedidos.df
//   action criar(id: Integer, cliente: String) -> Pedido: …
//   relay criar, Pedido
//
// main.df
//   adopt ./pedidos as P
//
//   P.criar(1, 2, 3)          // check: aridade
//   P.criar("um", "Ana")      // check: o parametro 'id' e Integer
//   P.criar(1, "Ana").clientte  // check: o campo, com sugestao
//
// O tipo de retorno e TRADUZIDO para o vocabulario de quem chama:
// '-> Pedido' la e 'P.Pedido' aqui. Devolver o nome nu faria o
// analisador procurar um record que este arquivo nao declara — e
// acusar codigo certo, que e o jeito mais rapido de alguem desligar
// a verificacao.

out "o check atravessa arquivos\"""", "lang": "df"},

 {"p": "Continue em [A superfície de um módulo](/docs/modulos/superficie) e [Compatibilidade](/docs/abi/compatibilidade)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/pacotes",
"title": "Usar um pacote",
"description": "add, install, remove — e onde o código de terceiro vai parar.",
"blocos": [
 {"p": "`dataforge add` resolve, baixa e instala; o `adopt` encontra o resultado. Quatro arquivos e uma pasta, e cada um tem um dono."},

 {"table": {"head": ["Onde", "O quê", "Versionado?"], "rows": [
   ["`forge.toml`", "o que você **pediu** — as faixas", "**sim**"],
   ["`forge.lock`", "o que foi **instalado** — versão e sha256", "**sim**"],
   ["`forge_modules/`", "os pacotes", "**não**"],
   ["`~/.dataforge/cache/`", "os tarballs, entre projetos", "não"]]}},

 {"code": """dataforge add validador          # a ultima, e grava a faixa
dataforge add tabela@^1.2        # uma faixa explicita
dataforge install                # tudo do forge.toml (e do lock)
dataforge list                   # o que esta instalado
dataforge remove tabela          # tira do toml e da pasta
dataforge outdated               # o que sobe, e o que exige mudar a faixa""", "lang": "bash"},

 {"code": """// Depois do 'add', o 'adopt' acha sozinho: ele olha
// 'forge_modules/', subindo ate achar um 'forge.toml'.
//
//   adopt validador as V
//   out V.cpf("529.982.247-25")
//
// O nome e o do PACOTE, e nao um caminho: e o mesmo 'adopt' que o
// teste da propria biblioteca usa, e e por isso que ele precisa
// funcionar pelo nome — o teste exercita a biblioteca pelo caminho
// que um usuario usaria.

out "o adopt encontra o que o add instalou\"""", "lang": "df"},

 {"callout": {"tipo": "atencao", "titulo": "Conflito de versão é erro, e não aviso", "texto": "Se dois pacotes pedem faixas **incompatíveis** do mesmo terceiro, `resolver()` falha dizendo quem pediu o quê. A alternativa — instalar duas cópias em versões diferentes — gera bug irreproduzível: o mesmo tipo passa a existir duas vezes, e `x is y` responde não sobre dois objetos que deveriam ser o mesmo."}},

 {"h2": "O que a extração recusa"},

 {"table": {"head": ["Recusa", "O ataque"], "rows": [
   ["entrada com `../`", "*Zip Slip*: escrever fora da pasta do pacote"],
   ["link simbólico", "apontar para fora e ser seguido depois"],
   ["descompactação desproporcional", "*zip bomb*: 1 KB que vira 10 GB"]]}},

 {"p": "Continue em [O lockfile](/docs/modulos/lockfile) e [O registro](/docs/modulos/registro)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/lockfile",
"title": "O lockfile",
"description": "O que ele trava, por que ele precisa ser LIDO, e as duas regras que decidem os empates.",
"blocos": [
 {"p": "O `forge.lock` guarda a versão exata e o **sha256** de cada pacote. Ele é versionado, e a razão é uma só: duas pessoas clonando o mesmo projeto em dias diferentes têm de receber a mesma árvore."},

 {"callout": {"tipo": "atencao", "titulo": "Um lockfile que ninguém lê não trava nada", "texto": "Este arquivo existia, era versionado, carregava o sha256 — e **nenhum caminho de instalação o consultava**. `_sincronizar` sempre resolvia as faixas do zero e reescrevia o arquivo. Duas pessoas recebiam árvores diferentes, e a “verificação de integridade” conferia um download **contra ele mesmo**. Vale conferir isso em qualquer gerenciador que você use: se `install` e `update` fazem a mesma coisa, o lock é decoração."}},

 {"table": {"head": ["Comando", "O que ele faz"], "rows": [
   ["`install`", "instala **o que o lock fixa**, enquanto couber na faixa do `forge.toml`"],
   ["`update`", "resolve de novo dentro das faixas e **reescreve** o lock; com nomes, move só eles"],
   ["`add`", "move só o que está sendo adicionado — o resto continua travado"],
   ["`outdated`", "separa o que sobe com `update` do que exige mudar o `forge.toml`"]]}},

 {"h2": "As duas regras dos empates"},

 {"table": {"head": ["Regra", "Porque"], "rows": [
   ["a **faixa do `forge.toml` vence o lock**", "o manifesto é a intenção; o lock é a memória da última resolução. Quem sobe o requisito está pedindo outra versão"],
   ["o **sha256 do lock é comparado com o que chegou**", "um tarball trocado numa versão já publicada **para a instalação**, com a mensagem dizendo o que fazer. É o ataque que um lockfile existe para impedir"]]}},

 {"h2": "O tarball é reprodutível"},

 {"p": "`mtime=0`, uid e gid zerados. Sem isso o sha256 mudaria a cada empacotamento, a verificação de integridade não significaria nada — e, pior, pareceria significar."},

 {"code": """cd packages/validador
dataforge pack                      # o tarball, com sha256 estavel
dataforge pack && dataforge pack    # o MESMO sha256 nas duas vezes""", "lang": "bash"},

 {"p": "Continue em [O registro](/docs/modulos/registro) e [Versão e compatibilidade](/docs/bibliotecas/versao)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/registro",
"title": "O registro de pacotes",
"description": "Uma pasta com um índice e tarballs — servida por qualquer host, e sem servidor a manter.",
"blocos": [
 {"p": "O registro é **estático**: um `index.json` e uma pasta de `.tar.gz`. Não há servidor, não há banco, não há processo a manter no ar — e é por isso que ele vai junto com o site."},

 {"code": """site/public/registry/
  index.json              o catalogo: nome, versoes, sha256
  pacotes/
    validador-1.0.0.tar.gz
    tabela-1.1.0.tar.gz
    ...""", "lang": "text"},

 {"table": {"head": ["Decisão", "O que ela evita"], "rows": [
   ["estático", "um serviço a manter, com disponibilidade e custo"],
   ["índice num arquivo", "uma consulta de rede por dependência"],
   ["sha256 no índice", "confiar no host do download"],
   ["qualquer host serve", "ficar preso a um fornecedor"]]}},

 {"h2": "Publicar"},

 {"code": """cd packages/validador
dataforge pack
dataforge publish --registry=../../site/public/registry

# E o registro da comunidade, com conta:
dataforge login
dataforge publish
dataforge whoami""", "lang": "bash"},

 {"h2": "Um registro próprio"},

 {"p": "Para uma empresa, o registro interno é uma pasta servida por nginx, por um bucket S3, ou pelo próprio GitHub Pages. O `forge.toml` aponta para ele."},

 {"code": """[registro]
url = "https://pacotes.minhaempresa.com"

# Ou por ambiente, que e o que um CI usa:
#   DATAFORGE_REGISTRY=https://pacotes.minhaempresa.com""", "lang": "toml"},

 {"callout": {"tipo": "dica", "titulo": "O registro não é a defesa", "texto": "Um registro privado reduz a superfície, e não a elimina: o que garante que o pacote é o que você aprovou é o **sha256 no lock**, e não de onde ele veio. Um registro comprometido serve um tarball diferente com o mesmo nome e a mesma versão — e o lock recusa."}},

 {"p": "Continue em [Publicar](/docs/bibliotecas/publicar)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/monorepo",
"title": "Workspace e monorepo",
"description": "Vários pacotes numa árvore só — e a checagem de faixas que acusa antes de instalar.",
"blocos": [
 {"p": "Um projeto com uma aplicação e quatro bibliotecas internas não deveria publicar as quatro para poder usá-las. O workspace é a árvore inteira vista de uma vez."},

 {"code": """minha-empresa/
  forge.toml            [workspace] members = ["apps/*", "libs/*"]
  apps/
    loja/forge.toml
    admin/forge.toml
  libs/
    validacao/forge.toml
    relatorios/forge.toml""", "lang": "text"},

 {"code": """dataforge workspace          # o grafo, e os conflitos de faixa
dataforge workspace --json   # para o CI ler""", "lang": "bash"},

 {"h2": "O que ele acusa, e o que ele cala"},

 {"p": "A interseção de faixas sai da **mesma classe `Requisito`** que o `resolver` usa. Uma segunda noção de *“estas faixas se cruzam?”* divergiria da instalação — e o relatório aprovaria o que o `add` recusa."},

 {"table": {"head": ["Acusa", "Cala"], "rows": [
   ["um pino exato recusado pelo outro lado", "faixas que se cruzam, mesmo sem serem iguais"],
   ["duas faixas sem interseção", "o que ele não consegue provar"],
   ["ciclo entre membros", "—"]]}},

 {"callout": {"tipo": "atencao", "titulo": "Ele lê, e NÃO instala", "texto": "`workspace` é um relatório. Ele não mexe em `forge_modules/`, não reescreve o lock e não baixa nada — o que o torna seguro de rodar no CI de todo *pull request*. E ele só acusa o que **prova**: um falso conflito faria o comando ser ignorado, e aí o conflito de verdade passa junto."}},

 {"h2": "O pino por projeto"},

 {"p": "`project.dataforge` no `forge.toml` diz de que versão da linguagem aquele projeto precisa — e ele é **cobrado**, não apenas mostrado."},

 {"code": """[project]
nome = "loja"
dataforge = ">=1.1"

# 'dataforge run' troca para a versao pinada quando ela esta
# instalada, e RECUSA quando nao esta. Um pino que nao e cobrado e
# um comentario com sintaxe — e era exatamente o que ele era: o
# unico lugar que o lia era o 'dataforge info', para mostrar na
# tela.""", "lang": "toml"},

 {"p": "Continue em [Versões lado a lado](/docs/cli/versoes) e [Workspace](/docs/cli/workspace)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/organizar",
"title": "Organizar um projeto grande",
"description": "O que muda quando o projeto passa de duzentos arquivos — e as quatro decisões que decidem se ele continua navegável.",
"blocos": [
 {"p": "Num arquivo de quarenta linhas, qualquer organização funciona. O que segue é o que passa a importar quando a maioria das chamadas atravessa módulo."},

 {"h2": "Por assunto, e não por tipo"},

 {"table": {"head": ["Por tipo (não)", "Por assunto (sim)"], "rows": [
   ["`modelos/`, `servicos/`, `rotas/`", "`pedidos/`, `clientes/`, `estoque/`"],
   ["mudar uma regra toca três pastas", "mudar uma regra toca uma pasta"],
   ["a fronteira do domínio não aparece", "a pasta **é** a fronteira"],
   ["`modelos/` com quarenta arquivos", "cada pasta cabe na tela"]]}},

 {"code": """src/
  pedidos/
    modelo.df        record Pedido, e as regras dele
    repositorio.df   como ele e guardado
    rotas.df         como ele e exposto
    pedidos_test.df
  clientes/
    ...
  compartilhado/
    tipos.df         o que MESMO e de todos""", "lang": "text"},

 {"callout": {"tipo": "atencao", "titulo": "`compartilhado/` é onde o acoplamento se esconde", "texto": "Toda pasta assim começa com três tipos e termina com quarenta — e a partir daí tudo depende de tudo, sem que nenhuma dependência pareça errada individualmente. A regra que segura: um tipo só entra ali quando **três** assuntos diferentes já o usam. Com dois, ele mora no que o criou, e o outro adota de lá."}},

 {"h2": "O ciclo de import é erro, e não estilo"},

 {"p": "Ele estourava só em execução, no primeiro `adopt`, e o `check` passava limpo num projeto que não sobe. Hoje o `check` acusa — e a mensagem mostra a **cadeia inteira**, porque um ciclo de quatro arquivos é impossível de quebrar sem saber por onde ele passa."},

 {"code": """dataforge check src/          # acusa o ciclo, com a cadeia
dataforge deps                # o grafo de imports
dataforge deps --ciclos       # so os ciclos""", "lang": "bash"},

 {"h2": "O que medir num projeto grande"},

 {"table": {"head": ["Comando", "O que ele responde"], "rows": [
   ["`dataforge stats`", "as ações e blueprints, o arquivo e a ação mais longos"],
   ["`dataforge oop`", "acoplamento e coesão; os cheiros com o princípio SOLID"],
   ["`dataforge deps`", "quem depende de quem, e os ciclos"],
   ["`dataforge big-o`", "a classe de complexidade de cada ação"],
   ["`dataforge test --cobertura`", "o que nenhum teste toca — e um arquivo sem teste aparece com **0%**, em vez de sumir"]]}},

 {"callout": {"tipo": "dica", "titulo": "O cache de árvores é o que torna isso rápido", "texto": "Duzentos arquivos importando três vizinhos cada levariam o `check` de 0,7 s a mais de um minuto sem cache. Medido: a fase de parse de 269 arquivos caiu de **258,7 ms para 17,9 ms**, e o `check` de `exercicios/` de 0,918 s para 0,524 s. A chave carrega caminho, `mtime_ns`, tamanho e um resumo do lexer, do parser e da AST — um cache que devolve a árvore errada é pior que nenhum."}},

 {"p": "Continue em [O cache de árvores](/docs/cli/cache) e [Diagnóstico](/docs/modulos/diagnostico)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/diagnostico",
"title": "Quando o import não resolve",
"description": "Os seis motivos de um adopt falhar, em ordem de frequência — e o comando que responde cada um.",
"blocos": [
 {"p": "Um `adopt` que não resolve tem sempre uma de seis causas. Elas estão em ordem de frequência."},

 {"table": {"head": ["#", "Sintoma", "Causa", "O que fazer"], "rows": [
   ["1", "`Module not found`", "caminho relativo errado — ele é relativo ao **arquivo**, e não ao diretório de trabalho", "`dataforge deps` mostra o que cada arquivo pede"],
   ["2", "acha em desenvolvimento e não no CI", "o pacote não está no `forge.toml`; funcionava pelo cache local", "`dataforge install` numa pasta limpa"],
   ["3", "`import cycle`", "A importa B, que importa A", "`dataforge check` mostra a cadeia"],
   ["4", "o nome existe e o símbolo não", "`relay` não o exporta", "confira o `relay` do outro arquivo"],
   ["5", "instalação velha no PATH", "há até três lugares: `.venv/`, `~/.dataforge/`, o Python do sistema", "`which dataforge` e `dataforge --version`"],
   ["6", "funciona no Mac e falha no Linux", "maiúscula no nome do arquivo — o macOS não diferencia", "renomeie tudo em minúsculas"]]}},

 {"callout": {"tipo": "atencao", "titulo": "A instalação velha é a mais enganosa", "texto": "Uma cópia antiga no PATH produz erros que **não existem no repositório** — foi assim que um `LexError: Unexpected character: '$'` apareceu num arquivo que usava interpolação normalmente. O `.venv` deve estar em modo editável (`pip install -e .`), que aponta para a árvore e nunca envelhece."}},

 {"h2": "Onde a resolução mora"},

 {"p": "Num lugar só: `resolucao.py`. Isso não é organização — é uma correção. A regra já esteve escrita em **três** lugares, e os três divergiram."},

 {"table": {"head": ["Onde estava", "O que dava errado"], "rows": [
   ["no analisador", "`nome.replace('.', os.sep)` transformava `'./mod'` em `'//mod'` — **795 de 795** avisos falsos num projeto de 21 mil linhas"],
   ["no `dataforge deps`", "uma expressão regular que começava em `[A-Za-z_]`, então `./vizinho` nunca casava: o comando dizia *“0 arquivos com imports próprios”* em todo projeto"],
   ["no interpretador", "a cópia que funcionava"]]}},

 {"callout": {"tipo": "dica", "titulo": "Um aviso que mente é pior que nenhum aviso", "texto": "Cada aviso de *“Module not found”* que o `check` emitia num `adopt` relativo era mentira — e um analisador que erra no caminho mais comum é um analisador que se desliga. `tests/test_resolucao.py` cobre os quatro casos e **proíbe a cópia voltar**."}},

 {"p": "Continue em [Resolução](/docs/modulos/resolucao) e [Organizar](/docs/modulos/organizar)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/modulos/testar",
"title": "Testar código modular",
"description": "Testar um módulo pelo caminho que um usuário usaria — e as duas armadilhas que fazem a suíte mentir.",
"blocos": [
 {"p": "Um teste que importa o módulo por um caminho que ninguém mais usa não prova que o módulo é utilizável."},

 {"code": """// packages/validador/tests/cpf_test.df
//
// CERTO: pelo NOME do pacote, como um usuario faria.
//   adopt validador as V
//
// ERRADO: por caminho relativo ate a fonte.
//   adopt ../src/main as V
//
// A segunda forma passa e nao prova nada sobre a instalacao. Foi
// ela que escondeu que um pacote nao sabia se importar pelo proprio
// nome: as suites dos VINTE pacotes deste repositorio falhavam, e o
// CI nao apanhava — ele nao rodava 'dataforge test' dentro de
// 'packages/'.

out "teste pelo caminho que o usuario usa\"""", "lang": "df"},

 {"h2": "As duas armadilhas"},

 {"callout": {"tipo": "atencao", "titulo": "1. “Tudo verde” com um teste reprovado", "texto": "Um arquivo com `crucible`/`trial` **registra** as suítes e não as roda — quem roda é `Crucible.run()`. O corredor caía no caso *“sem ações `test_`, o próprio arquivo é o caso”* e contava o arquivo como **um teste que passou**. Um arquivo com dez `trial`, um deles quebrado, saía com **código 0** — e `dataforge crucible`, sobre a mesma suíte, saía com 1. Os dois discordavam, e o nome mais óbvio era o que mentia."}},

 {"callout": {"tipo": "atencao", "titulo": "2. A cobertura otimista", "texto": "O denominador vem do parser (quais linhas são **executáveis**), e a definição de “instrução” é a existência de `exec_<Nó>` no interpretador — e não uma lista. A primeira versão era uma lista e apodreceu antes de ser commitada: ela tinha `CycleLoop`, e o nó se chama `CycleFromTo`. O laço inteiro ficava fora do denominador, e a cobertura saía **otimista** — o pior defeito possível numa métrica."}},

 {"h2": "O teste de um módulo"},

 {"code": """adopt Arcane.Crucible

crucible "normalizacao":
    trial "tira espaco e caixa":
        expect(normalizar("  Café  ")) to_be("café")

    trial "texto vazio nao quebra":
        expect(normalizar("")) to_be("")

    trial "ainda nao decidido" pending:
        expect(normalizar(void)) to_be("")

action normalizar(t):
    yield (t ?? "").strip().lower()

r := Crucible.run()
out $"{r['passou']} passaram, {r['pendente']} pendente(s)\"""", "lang": "df"},

 {"table": {"head": ["Comando", "Cobre"], "rows": [
   ["`dataforge test .`", "descobre `*_test.df` e `tests/`"],
   ["`dataforge test --cobertura --minimo=80`", "reprova o CI abaixo do piso"],
   ["`dataforge test --fail-fast`", "para na primeira falha"],
   ["`dataforge check . --strict`", "o que nem chega a rodar"]]}},

 {"p": "Continue em [Testes de biblioteca](/docs/bibliotecas/testes) e [Crucible](/docs/testes)."},
]},
]
