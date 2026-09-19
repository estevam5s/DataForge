"""A superfície como contrato, o mapa de símbolos, os alvos e o WebAssembly.

Partes 18 e 19 da referência Deep Tech.
Todo bloco `df` destas páginas RODA (`tests/test_abi_e_alvos.py`).
"""

PAGINAS = [
# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/abi/superficie",
"title": "A superfície é o contrato",
"description": "O que um módulo exporta, com que aridade e com que tipos — e por que mudá-la é o mesmo problema que quebrar uma ABI.",
"blocos": [
 {"p": "Numa linguagem compilada, quebrar a **ABI** é trocar o layout de uma struct ou a convenção de chamada. O sintoma é cruel: o programa **carrega** e corrompe memória, longe da causa e sem nada denunciar."},
 {"p": "Aqui não há layout binário a quebrar. E existe **exatamente o mesmo problema**, com outro nome."},
 {"table": {"head": ["Na linguagem compilada", "Aqui"], "rows": [
   ["símbolo removido do `.so`", "símbolo tirado do `relay`"],
   ["assinatura trocada", "aridade, nome ou tipo de parâmetro trocado"],
   ["layout de struct mudado", "campo acrescentado a um `record`"],
   ["tipo de retorno trocado", "o mesmo — e ele **atravessa** o `adopt`"],
   ["`soname` bump", "versão **maior** no `forge.toml`"]]}},
 {"callout": {"tipo": "atencao", "titulo": "O sintoma também é o mesmo", "texto": "**Não é um erro de compilação de quem publicou.** O módulo novo compila perfeitamente, os testes dele passam, o pacote sobe. O erro acontece na máquina de **quem consome**, depois, no dia da atualização — e a pessoa que vai depurar não é a que causou."}},

 {"h2": "O que é contrato, e o que não é"},
 {"p": "A superfície respeita o `relay`. Um módulo que **declara** o que exporta está dizendo que o resto é interno — e o que é interno não é contrato, então mexer nele não quebra ninguém."},
 {"code": """action somar(a: Integer, b: Integer) -> Integer:
    yield a + b

action interna():          // nao esta no relay: nao e contrato
    yield 1

record Ponto:
    x: Integer
    y: Integer

relay somar, Ponto""", "lang": "df", "title": "lib.df — o relay decide"},
 {"p": "Sem `relay`, tudo o que é de topo é contrato — o que é a escolha certa para um arquivo que não declarou nada, e um bom motivo para declarar."},

 {"h2": "A superfície, como dado"},
 {"code": """adopt Arcane.Abi as Abi

// Abi.superficie("lib.df") devolve, por simbolo:
//   especie      acao, record, blueprint, enum, trait, valor
//   minimo       quantos argumentos ele EXIGE
//   maximo       quantos ele ACEITA (void = variadico)
//   parametros   os nomes, na ordem — e eles sao contrato
//   tipos        o tipo declarado de cada um
//   retorno      o tipo de retorno, que atravessa o adopt
//   campos       de um record ou blueprint
//   linha        onde ele foi declarado

assert len(keys(Abi.regras())) bigger_eq 7""", "lang": "df"},
 {"callout": {"tipo": "nota", "titulo": "A conta sai de `superficie.py`", "texto": "O mesmo módulo que o `check` usa para [atravessar arquivos](/docs/tecnicas/analise-estatica). Uma segunda leitura da superfície divergiria da primeira — e aí o `check` e o `abi` passariam a discordar sobre o que um módulo oferece, que é o pior resultado possível para duas ferramentas que respondem a mesma pergunta."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/abi/compatibilidade",
"title": "O que quebra, e qual versão subir",
"description": "Onze regras nomeadas, o veredito de semver que a mudança exige, e o terceiro balde para o que a superfície não decide sozinha.",
"blocos": [
 {"p": "O [gerenciador de pacotes](/docs/cli/pacotes) já tinha semver, `forge.lock` e verificação de integridade. O que faltava era **o que decide o número**: nada conferia se a versão nova quebra a anterior, e o bump era escolhido a olho."},
 {"code": """dataforge abi v1/lib.df v2/lib.df        # sai com 2 se quebrou
dataforge abi a.df b.df --json           # para o CI ler
dataforge abi a.df b.df --estrito        # o indecidivel conta como quebra""", "lang": "bash"},

 {"h2": "As regras que quebram"},
 {"table": {"head": ["Regra", "Por que quebra"], "rows": [
   ["`simbolo-removido`", "um nome que o módulo exportava deixou de existir; quem o adotava para de compilar no dia da atualização"],
   ["`especie-trocada`", "o nome continua e virou outra coisa (uma ação virou `record`): toda forma de uso muda junto"],
   ["`aridade-incompativel`", "uma chamada que era válida deixou de ser — mais argumento exigido, ou menos aceito"],
   ["`parametro-renomeado`", "**a chamada com nome existe aqui** (`somar(a := 1, b := 2)`), então o nome do parâmetro é contrato e não só a posição"],
   ["`tipo-de-parametro`", "quem passava o tipo antigo passa a ser recusado pelo `check`"],
   ["`retorno-trocado`", "o tipo de retorno **atravessa** a fronteira do `adopt`: quem usava o valor perde a conferência, ou é acusado"],
   ["`campo-removido`", "todo acesso ao campo passa a ser erro"]]}},
 {"callout": {"tipo": "nota", "titulo": "`parametro-renomeado` é a regra que uma ferramenta feita para C não precisaria ter", "texto": "Em C o argumento é posicional e o nome do parâmetro não sai do cabeçalho. Nesta linguagem a chamada com nome existe, então trocar `a` por `x` quebra `somar(a := 1, b := 2)` — e quebra **em silêncio**, porque o `check` de quem consome vai acusar um nome que a pessoa nunca escreveu errado."}},

 {"h2": "As que não quebram"},
 {"table": {"head": ["Regra", "Por que é compatível"], "rows": [
   ["`simbolo-novo`", "ninguém depende dele ainda"],
   ["`parametro-opcional-novo`", "quem chamava com os antigos continua chamando igual"],
   ["`campo-novo-opcional`", "num blueprint, a construção antiga continua valendo"]]}},

 {"h2": "E o terceiro balde"},
 {"p": "Há um caso que a superfície **não consegue decidir**, e fingir que decide seria pior que não ter a ferramenta."},
 {"callout": {"tipo": "atencao", "titulo": "`campo-novo-em-record` — a superfície não carrega valor padrão", "texto": "Acrescentar um campo a um `record` quebra `Ponto(3, 4)` **se o campo não tiver padrão**. Se tiver, é compatível. A superfície lê a declaração sem executá-la e não sabe qual dos dois é. Acusar quebra reprovaria um release correto; calar deixaria passar um que quebra. O honesto é um **terceiro balde**, em destaque no relatório — e `--estrito` o transforma em quebra para quem prefere o alarme."}},
 {"code": """  1 ponto(s) que a superficie NAO decide sozinha:
   ? Ponto  [campo-novo-em-record]
      um campo foi acrescentado a um record. Quebra SE ele nao tiver
      valor padrao — e a superficie nao carrega padroes, entao esta e
      uma decisao que so quem escreveu pode tomar
      → se o campo tem valor padrão, é compatível; se não tem, dê um
        — ou suba a versão maior""", "lang": "text"},

 {"h2": "O veredito"},
 {"table": {"head": ["Veredito", "Quando", "Saída do comando"], "rows": [
   ["`maior`", "alguma coisa quebrou", "**2** — reprova no CI"],
   ["`menor`", "só acréscimos compatíveis", "0"],
   ["`correcao`", "a superfície não mudou", "0"],
   ["`desconhecido`", "um dos lados não compila", "1, com o motivo"]]}},
 {"callout": {"tipo": "nota", "titulo": "Uma superfície que não compila não julga", "texto": "`veredito` devolve `desconhecido` com o motivo, em vez de acusar quebra. Um falso alarme aqui reprova um release que está certo — e a segunda vez que isso acontece, a conferência inteira é desligada. Um analisador sem escape ensina a ignorá-lo; um que erra ensina a removê-lo."}},

 {"h2": "No CI"},
 {"code": """# no seu pipeline, antes de publicar
git show HEAD~1:src/main.df > /tmp/antes.df
dataforge abi /tmp/antes.df src/main.df || exit 1""", "lang": "bash", "title": "Conferir contra o commit anterior"},
 {"p": "Cada quebra vem com **o que fazer** ao lado — e quase sempre há um caminho que evita o bump: dar valor padrão ao parâmetro novo, manter o nome antigo como casca que chama o novo, aceitar os dois tipos por um ciclo."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/abi/simbolos",
"title": "O mapa de símbolos",
"description": "De onde vem cada nome de um arquivo — o análogo do mapa que um ligador escreve, e a resposta para a pergunta que mais custa num projeto grande.",
"blocos": [
 {"p": "Num projeto de duzentos arquivos, *\"de onde vem este nome?\"* é a pergunta que mais custa a responder à mão. Um ligador escreve isso num **arquivo de mapa**; aqui ele sai do mesmo caminho que o `check` usa para atravessar arquivos."},
 {"code": """adopt Arcane.Abi as Abi
adopt Arcane.IO as IO
adopt Arcane.OS as OS

caminho := $"{OS.temp_dir()}/exemplo-{randint(100000, 999999)}.df"
IO.write(caminho, "adopt Arcane.Math as M\\n\\n" +
                  "action calcular(n):\\n" +
                  "    yield M.sqrt(n) + len(\\\"abc\\\") + fantasma\\n")

origem := {e["nome"]: e["origem"] cycle e in Abi.mapa(caminho)}

assert origem["M"] is "modulo"              // veio de um adopt
assert origem["len"] is "embutido"          // uma das 228 globais
assert origem["calcular"] is "local"        // declarado neste arquivo
assert origem["fantasma"] is "desconhecido" // NINGUEM prove este nome

IO.delete(caminho)""", "lang": "df"},
 {"table": {"head": ["Origem", "O que quer dizer"], "rows": [
   ["`modulo`", "veio de um `adopt`; `de` traz o módulo e `linha`, a linha do import"],
   ["`local`", "declarado neste arquivo — ação, record, blueprint, enum ou variável de topo"],
   ["`embutido`", "uma das 228 funções globais, sem import"],
   ["`desconhecido`", "**ninguém provê este nome** — é isto que interessa"]]}},
 {"h2": "O nome sem dono"},
 {"p": "A linha `desconhecido` é a que paga o mapa. Um nome que nenhum `adopt`, nenhuma declaração local e nenhum embutido provê é, quase sempre, uma das três coisas: um erro de digitação, um `adopt` que alguém apagou, ou um nome que vem de um arquivo vizinho que este não importa."},
 {"p": "O [`check` já acusa](/docs/tecnicas/analise-estatica) o nome indefinido quando consegue provar. O mapa é a outra metade: ele **lista tudo**, com a origem de cada um, e serve para revisar um arquivo inteiro de uma vez em vez de esperar o analisador tropeçar."},
 {"callout": {"tipo": "nota", "titulo": "Por que isto é o análogo de um mapa de ligador", "texto": "Um ligador resolve símbolos entre objetos e escreve onde cada um foi parar. Aqui não há relocação nem seção — mas a **resolução de símbolo** existe igual: `resolucao.py` decide onde mora o módulo de um `adopt`, e é a única cópia dessa regra no repositório. O mapa é o relatório dela."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/alvos/portabilidade",
"title": "Onde este programa roda",
"description": "Seis alvos descritos, com o que cada um suporta e por que não suporta o resto — lido dos adopt, e honesto sobre o que isso não prova.",
"blocos": [
 {"p": "*Este programa roda no navegador? numa função serverless? num WASI?* É uma pergunta real e ela aparece cedo — e a resposta dependia de alguém conhecer de cor o que cada ambiente suporta, e de lembrar, para cada `adopt`, se aquele módulo abre soquete, processo ou arquivo."},
 {"code": """dataforge alvo app.df                      # a tabela de todos
dataforge alvo app.df --alvo=navegador     # um so, e sai com 3 se nao roda
dataforge alvo app.df --json               # como dado""", "lang": "bash"},
 {"code": """adopt Arcane.Alvo as Alvo

assert sorted(keys(Alvo.alvos())) is
       ["cli", "embarcado", "funcao", "navegador", "servidor", "wasi"]

// o servidor suporta tudo
assert Alvo.alvos()["servidor"]["nao_suporta"] is []""", "lang": "df"},

 {"h2": "Os seis alvos"},
 {"table": {"head": ["Alvo", "O que é", "Não tem"], "rows": [
   ["`servidor`", "máquina com sistema operacional completo — onde o DataForge foi feito para rodar", "—"],
   ["`cli`", "programa de linha de comando na máquina do usuário", "—"],
   ["`navegador`", "o CPython compilado para WebAssembly (Pyodide) dentro de uma aba", "arquivos, rede, processo, banco, threads, nativo, ambiente"],
   ["`wasi`", "WebAssembly **fora** do navegador, com a interface de sistema do WASI", "rede, processo, banco, threads, nativo"],
   ["`funcao`", "serverless: processo efêmero, disco só de leitura fora de `/tmp`", "processo, threads, nativo"],
   ["`embarcado`", "microcontrolador com MicroPython — memória em kilobytes", "quase tudo"]]}},
 {"p": "E cada ausência vem com **o motivo**, não só com um `não`:"},
 {"code": """adopt Arcane.Alvo as Alvo

porque := Alvo.porque("navegador", "threads")
assert "SharedArrayBuffer" in porque

assert "soquete cru" in Alvo.porque("navegador", "rede")
assert Alvo.porque("servidor", "rede") is ""     // ele tem""", "lang": "df"},

 {"h2": "O mesmo vocabulário da capacidade"},
 {"p": "As capacidades são as de [`Arcane.Capacidade`](/docs/seguranca/capacidade): `arquivos`, `rede`, `processo`, `banco`, `threads`, `nativo`, `python`, `ambiente`."},
 {"p": "Lá elas são **cobradas em execução**; aqui são **lidas antes de rodar**, e o alvo é quem diz quais existem. É a mesma pergunta feita de dois lados — e usar dois vocabulários faria as duas respostas divergirem no primeiro módulo novo."},
 {"code": """adopt Arcane.Alvo as Alvo
adopt Arcane.Capacidade as Cap

// os dois falam a mesma lingua
assert Cap.exige("Arcane.Process") is "processo"
assert "processo" in Alvo.alvos()["navegador"]["nao_suporta"]""", "lang": "df"},

 {"h2": "O que esta leitura NÃO prova"},
 {"callout": {"tipo": "atencao", "titulo": "É estática, e sai dos `adopt` de um arquivo", "texto": "Um `roda` aqui quer dizer **\"não achei impedimento por esta via\"**, e não \"vai funcionar\". O módulo devolve esta lista em execução, com `Alvo.limites()`, para quem for ler pelo código e não pela documentação."}},
 {"table": {"head": ["Limite", "Consequência"], "rows": [
   ["a leitura é de **um arquivo**", "um módulo alcançado indiretamente — uma biblioteca do projeto que adota `Arcane.Process` — não aparece"],
   ["`adopt Python.x` conta como `python` e para aí", "o que aquele pacote faz por dentro, ninguém lê"],
   ["não executa nada", "memória, tempo e dependência nativa do Python continuam sendo problema de quem publica"]]}},
 {"p": "Dito isso, o que ela dá é o que vale: **a lista dos pontos que certamente não rodam, com a linha**. Isso responde a pergunta em dois segundos, e o resto continua sendo trabalho de quem publica."},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/alvos/wasm",
"title": "WebAssembly, com precisão",
"description": "O DataForge não compila para WASM — e o que existe no lugar funciona. A diferença entre as duas frases importa.",
"blocos": [
 {"p": "A resposta curta: **o DataForge não compila para WebAssembly**, e não há um alvo `wasm32` para o qual gerar módulo."},
 {"p": "A resposta útil é mais longa, e ela começa por separar duas coisas que costumam ser confundidas."},

 {"h2": "Compilar PARA WebAssembly · rodar EM WebAssembly"},
 {"table": {"head": ["", "Compilar para WASM", "Rodar em WASM"], "rows": [
   ["o que é", "produzir um `.wasm` com as funções da sua linguagem", "rodar o **interpretador** dentro de um runtime WASM"],
   ["quem faz", "Rust, C, Zig, Go, AssemblyScript", "CPython pelo Pyodide, e portanto o DataForge junto"],
   ["no DataForge", "**não existe**", "**funciona**, e não é uma porta desta linguagem"],
   ["custo", "—", "o interpretador inteiro vai junto: alguns megabytes antes da primeira linha"]]}},
 {"callout": {"tipo": "nota", "titulo": "Rodar em WASM é rodar o CPython em WASM", "texto": "O Pyodide compila o CPython para WebAssembly e o DataForge roda em cima, como rodaria em qualquer outro CPython. É um resultado real e é a via prática — mas quem chama isso de \"DataForge compila para WASM\" está descrevendo outra coisa, e a diferença aparece no tamanho do artefato e no que o ambiente permite."}},

 {"h2": "O que o item do documento pede, item por item"},
 {"table": {"head": ["Item", "Resposta"], "rows": [
   ["**WASM target**", "**não existe**. Emitir WASM exigiria um backend de geração de código — e a [parte 8](/docs/compilador/backend) explica por que ele não existe nem para código de máquina nativo"],
   ["**WASI**", "**não como alvo de compilação**. O `wasi` em `Arcane.Alvo` é o perfil de **restrições** de rodar ali dentro, não um formato de saída"],
   ["**linear memory**", "**não se aplica** diretamente: a memória linear é do runtime WASM que hospeda o CPython, e nenhum objeto do DataForge a alcança"],
   ["**imports / exports**", "**não se aplica** no sentido do módulo WASM. O análogo da linguagem é `adopt` e `relay`, e o contrato deles tem [ferramenta própria](/docs/abi/compatibilidade)"],
   ["**host bindings**", "o análogo existe e é real: a [ponte para o Python](/docs/tecnicas/ponte) e o [FFI com C](/docs/ffi/c) — dois jeitos de chamar o que está fora"],
   ["**SIMD**", "**não se aplica** — ver [o mapa de hardware](/docs/hardware/mapa)"],
   ["**threads**", "**não no navegador**: dependem de `SharedArrayBuffer` e de isolamento de origem, e o Pyodide as desliga por padrão. É por isso que `threads` está fora do perfil `navegador`"],
   ["**component model**", "**não se aplica**: sem módulo WASM, não há componente a compor"]]}},

 {"h2": "Se você quer isso hoje"},
 {"p": "O caminho que funciona é o de qualquer projeto Python no navegador: carregar o Pyodide, instalar o pacote e rodar. O que o `Arcane.Alvo` acrescenta é dizer **antes** quais linhas do seu programa não vão sobreviver ali."},
 {"code": """adopt Arcane.Alvo as Alvo

// antes de tentar: o que nao roda numa aba?
// r := Alvo.conferir("app.df", "navegador")
// cycle p in r["problemas"]:
//     out $"linha {p['linha']}: {p['modulo']} precisa de {p['capacidade']}"

assert "navegador" in keys(Alvo.alvos())
assert len(Alvo.limites()) bigger_eq 3""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Por que não emitir WASM \"só para dizer que emite\"", "texto": "Seria possível gerar um `.wasm` que implementasse um subconjunto minúsculo da linguagem — literais, contas, talvez um laço. Ele não rodaria nenhum programa do repositório, e passaria a existir como uma caixa que se marca. A [parte 8](/docs/compilador/otimizacao) já mostrou o que acontece quando se mede em vez de supor: a otimização que \"devia\" render, rendeu **1,01×**. Um backend WASM parcial renderia menos que isso, e custaria uma promessa."}},
]},

# ════════════════════════════════════════════════════════════════════
{
"href": "/docs/abi/mapa",
"title": "ABI, ligador e alvos: o mapa",
"description": "Item por item das partes 18 e 19 da referência Deep Tech — ABI, linker, executáveis, WebAssembly e targets especializados.",
"blocos": [
 {"p": "Duas partes que parecem inteiramente \"não se aplica\" — e não são. O que transfere delas não é o binário: é o **contrato** e a **restrição de ambiente**, que existem em qualquer linguagem que se distribua."},

 {"h2": "72 · ABI"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["**binary compatibility**", "a **superfície** é o contrato, e `dataforge abi` diz o que quebrou", "[Compatibilidade](/docs/abi/compatibilidade)"],
   ["**versioning**", "o veredito de semver que a mudança **exige** — antes era escolhido a olho", "[Compatibilidade](/docs/abi/compatibilidade)"],
   ["**symbol naming**", "o `relay` decide o que é público; o mapa diz de onde vem cada nome", "[Símbolos](/docs/abi/simbolos)"],
   ["calling conventions", "reais, mas **só na fronteira com o C**: `ctypes` aplica a ABI da plataforma", "[FFI](/docs/ffi/c)"],
   ["struct layout", "`C.estrutura` dá tamanho, alinhamento e deslocamento de verdade — inclusive o padding", "[Chamar C](/docs/ffi/c)"],
   ["enum representation", "`C.enumeracao`: inteiro com nome, que é o que atravessa", "[Chamar C](/docs/ffi/c)"],
   ["platform-specific ABI", "vem do `ctypes`, que segue a do sistema", "[FFI](/docs/ffi/mapa)"],
   ["register / stack conventions", "**não se aplica**: não há registrador alcançável", "—"]]}},

 {"h2": "73 · Linker"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["**symbol resolution**", "`resolucao.py` — onde mora o módulo de um `adopt`, e **a única cópia** dessa regra; o mapa é o relatório dela", "[Símbolos](/docs/abi/simbolos)"],
   ["dynamic linking", "`C.carregar` abre `.so`, `.dylib` e `.dll` em tempo de execução — é `dlopen` de verdade", "[FFI](/docs/ffi/c)"],
   ["\"linkar\" dependências", "`forge_modules/`, `forge.lock` e a resolução com semver do gerenciador", "[Pacotes](/docs/cli/pacotes)"],
   ["detecção de ciclo", "erro do `check`, com a **cadeia inteira** na mensagem — busca em largura, para achar o ciclo mais curto", "[Carga](/docs/modulos/carga)"],
   ["static linking, relocations, sections", "**não se aplica**: não há passo de ligação, e nada é relocado"],
   ["ELF, PE/COFF, Mach-O", "os binários do release **são** esses formatos — produzidos pelo PyInstaller, não pelo DataForge", "[Download](/download)"],
   ["linker scripts", "**não se aplica**"]]}},

 {"h2": "74 · Executáveis"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["executables", "o release constrói para **quatro** plataformas e roda os exercícios *pelo binário* em cada uma", "[Download](/download)"],
   ["static libraries", "o análogo é o **pacote**: `dataforge pack` produz um tarball reprodutível (`mtime=0`, uid/gid zerados), senão o sha256 mudaria a cada empacotamento", "[Pacotes](/docs/cli/pacotes)"],
   ["dynamic libraries", "do lado de consumo: `Arcane.C`", "[FFI](/docs/ffi/c)"],
   ["entry points", "`forge.toml` declara a entrada; `dataforge run` sem arquivo a usa", "[forge.toml](/docs/cli/forge-toml)"],
   ["**debug symbols**", "o análogo é a informação de posição: linha, coluna e `span` em **todo** nó e **todo** erro — é ela que desenha a seta", "[Erros](/docs/erros)"],
   ["stripping", "**não se aplica**, e a razão é boa: tirar a informação de posição não economizaria nada que importe, e a mensagem de erro é metade do valor da linguagem"],
   ["object files, relocations, sections", "**não se aplica**"]]}},

 {"h2": "75 · WebAssembly"},
 {"table": {"head": ["Item", "No DataForge", "Onde"], "rows": [
   ["WASM target, WASI como saída", "**não existe** — e a diferença entre *compilar para* e *rodar em* está escrita", "[WebAssembly](/docs/alvos/wasm)"],
   ["**rodar em WASM**", "**funciona**, pelo Pyodide: é rodar o CPython em WebAssembly", "[WebAssembly](/docs/alvos/wasm)"],
   ["host bindings", "o análogo existe: a ponte para o Python e o FFI com C", "[Ponte](/docs/tecnicas/ponte)"],
   ["threads no navegador", "**não**, e o perfil `navegador` diz por quê (SharedArrayBuffer e isolamento de origem)", "[Portabilidade](/docs/alvos/portabilidade)"],
   ["linear memory, imports/exports, SIMD, component model", "**não se aplica** sem módulo WASM", "[WebAssembly](/docs/alvos/wasm)"]]}},

 {"h2": "76 · Targets especializados"},
 {"table": {"head": ["Alvo", "Resposta"], "rows": [
   ["**server**", "é o alvo padrão, e onde tudo foi medido"],
   ["**desktop / CLI**", "sim: quatro plataformas no release, com instalador gráfico no Windows"],
   ["**WebAssembly**", "rodando o CPython, não compilando — ver acima"],
   ["**serverless**", "o perfil `funcao` existe e diz o que não sobrevive: processo, thread longa, biblioteca nativa"],
   ["**mobile**", "**não há porta**. Existe CPython em Android e iOS, e nada disso foi testado aqui — dizer \"sim\" sem ter rodado seria inventar"],
   ["**embedded / bare-metal / kernel**", "**não se aplica** — ver [o mapa de hardware](/docs/hardware/mapa)"],
   ["**game engines**", "**não se aplica**: o laço de renderização precisa de milissegundos previsíveis, e um interpretador de árvore com GC não os dá"],
   ["**HPC / scientific computing**", "**pela ponte**: `adopt Python.numpy` traz a conta vetorizada de verdade, e `P.map_processos` usa mais de um núcleo. O que o DataForge não faz é ser o laço numérico"]]}},

 {"h2": "O resumo honesto"},
 {"p": "Das duas partes, **a 18 rendeu mais do que parecia**: ABI não é sobre bytes, é sobre **contrato** — e o contrato existe aqui, quebra do mesmo jeito e agora tem ferramenta que o confere. A **19 rendeu o perfil de restrições**, que responde a pergunta real (\"roda no navegador?\") sem prometer um backend que não existe."},
 {"callout": {"tipo": "nota", "titulo": "O que estas duas partes entregaram", "texto": "Dois módulos (`Arcane.Abi`, `Arcane.Alvo`), dois comandos (`dataforge abi`, `dataforge alvo`), onze regras de compatibilidade nomeadas com o que fazer em cada uma, seis perfis de alvo com o **porquê** de cada ausência — e um terceiro balde para o caso que a superfície não decide, em vez de uma resposta inventada."}},
]},
]
