# -*- coding: utf-8 -*-
"""Partida — as páginas-raiz de /docs/partida e /docs/hardware (que
respondiam 404) e cinco páginas sobre o começo e o fim de um processo:
encerrar em ordem, código de saída, argumentos, ambiente e contêiner.

`Inicio.ao_encerrar`, `esquecer_encerramento` e `encerrando` entraram
nesta leva. Para funcionar, o interpretador passou a atender, na thread
principal, o que só ela pode fazer: o programa roda numa thread própria
(a da pilha maior), e o Python só instala tratador de sinal na principal.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/partida",
"title": "Partida e fim",
"description": "O que acontece antes da primeira linha e depois da última — e o sinal que chega no meio.",
"blocos": [
 {"p": "Um programa não começa na primeira linha nem termina na última. Antes, há a partida: módulos carregados, a pilha reservada, o ambiente lido. Depois — ou no meio —, há o fim: o `docker stop`, o Ctrl+C, o deploy que troca o processo. Um programa que ignora o fim perde o que estava na memória."},
 {"code": '''adopt Arcane.Inicio as Inicio

Inicio.ao_encerrar(lambda => out "conexões fechadas")
assert not Inicio.encerrando()
out "trabalhando"''', "lang": "df"},
 {"cards": [
   {"href": "/docs/partida/inicio", "title": "Antes da primeira linha", "desc": "as fases da partida, medidas"},
   {"href": "/docs/partida/encerrar", "title": "Encerrar em ordem", "desc": "SIGTERM, Ctrl+C e os finalizadores"},
   {"href": "/docs/partida/codigos-de-saida", "title": "Código de saída", "desc": "0, 1, 2 e 128 + sinal"},
   {"href": "/docs/partida/argumentos", "title": "Argumentos", "desc": "a linha de comando declarada, com ajuda gerada"},
   {"href": "/docs/partida/ambiente", "title": "Ambiente e configuração", "desc": "variáveis, padrões e segredos"},
   {"href": "/docs/partida/conteineres", "title": "Dentro de um contêiner", "desc": "PID 1, o prazo do docker stop e a sonda"},
   {"href": "/docs/partida/por-thread", "title": "Uma variável por thread", "desc": "o valor que cada thread tem o seu"},
   {"href": "/docs/partida/pilha", "title": "A pilha", "desc": "o teto de quadros, e o que vale de verdade"},
   {"href": "/docs/seguranca/capacidade", "title": "Fronteira de capacidade", "desc": "o adopt que é recusado"},
   {"href": "/docs/partida/mapa", "title": "Partida e segurança: o mapa", "desc": "o que existe, e o que não"}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/partida/encerrar",
"title": "Encerrar em ordem",
"description": "SIGTERM, SIGINT e SIGHUP rodam os finalizadores ao contrário, e o processo sai com 128 + sinal.",
"blocos": [
 {"p": "O `docker stop`, o Kubernetes e o `systemctl stop` pedem para o processo terminar mandando **SIGTERM**. Um programa que não trata o sinal morre na hora: a transação no meio não confirma, o arquivo não fecha, a mensagem pega da fila não é devolvida. `Inicio.ao_encerrar` registra o que precisa rodar antes de sair."},
 {"code": '''adopt Arcane.Inicio as Inicio

log := []
Inicio.ao_encerrar(lambda => log.append("banco fechado"))
Inicio.ao_encerrar(lambda => log.append("fila devolvida"))

// o laço de trabalho confere a cada volta
atendidos := 0
persist not Inicio.encerrando() and atendidos smaller 3:
    atendidos += 1
assert atendidos is 3''', "lang": "df"},
 {"h2": "O que acontece no sinal"},
 {"table": {"head": ["Passo", "Por quê"], "rows": [
   ["`encerrando()` passa a `yes`", "um laço que confere para por conta própria, no fim da volta — sem cortar um pedido no meio"],
   ["os finalizadores rodam **ao contrário** do registro", "quem abriu por último fecha primeiro, como uma pilha de `defer`: a fila, que usa o banco, fecha antes dele"],
   ["um finalizador que falha não impede os outros", "fechar o banco não pode depender de o log ter fechado"],
   ["sai com `128 + sinal` — 143 para SIGTERM", "o código que o orquestrador espera de uma saída por sinal"],
   ["um **segundo** sinal sai na hora", "quem aperta Ctrl+C duas vezes não quer esperar"]]}},
 {"p": "O fim normal do programa também roda os finalizadores, uma vez só — registrar para o sinal e esquecer do fim comum era o defeito de metade dos `atexit` escritos à mão."},
 {"callout": {"tipo": "atencao", "titulo": "Registre no topo, antes das threads", "texto": "O Python só entrega sinal à thread principal. O registro é feito lá — o interpretador, que roda o programa numa thread própria, repassa o pedido —, mas um `ao_encerrar` chamado de dentro de uma `thread:` é recusado com a explicação."}},
 {"callout": {"tipo": "dica", "titulo": "O prazo é curto", "texto": "O `docker stop` espera **10 segundos** antes de matar com SIGKILL, que não se trata. O Kubernetes, 30. Finalizador que faz rede precisa de prazo próprio, menor que esse."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/partida/codigos-de-saida",
"title": "Código de saída",
"description": "0 deu certo, 1 deu errado, 2 foi chamado errado, 128 + N morreu por sinal — e quem lê cada um.",
"blocos": [
 {"p": "O código de saída é a única coisa que um processo diz ao programa que o chamou sem que alguém leia a saída. O CI decide por ele, o shell decide por ele (`&&`), o orquestrador decide por ele se reinicia."},
 {"table": {"head": ["Código", "Quer dizer", "Quem produz"], "rows": [
   ["0", "deu certo", "o fim normal do programa"],
   ["1", "rodou e deu errado", "um erro não tratado"],
   ["2", "foi chamado errado", "`Cli.comando` com argumento inválido; `dataforge abi` com quebra"],
   ["128 + N", "morreu pelo sinal N", "143 = SIGTERM, 130 = SIGINT (Ctrl+C)"],
   ["qualquer outro", "o que você decidir", "`OS.exit(n)`"]]}},
 {"code": '''adopt Arcane.OS as OS

action conferir(entrada):
    given len(entrada) is 0:
        out "nada a processar"
        OS.exit(0)                     // não é erro: só não havia o que fazer
    yield len(entrada)

assert conferir([1, 2, 3]) is 3''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Nunca sair com 0 depois de um erro", "texto": "Um script que imprime \"erro!\" e sai com 0 faz o CI passar verde com o trabalho pela metade. É o defeito que o `parallel` tinha — o erro de uma tarefa era impresso, e o programa saía com 0. Erro não tratado sai com 1 sozinho; ao tratar, decida o código de propósito."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/partida/argumentos",
"title": "Argumentos da linha de comando",
"description": "OS.argv para o simples, Cli.comando para o que tem opção, tipo e ajuda — gerada da declaração.",
"blocos": [
 {"p": "Os argumentos chegam depois de `--`: `dataforge run relatorio.df -- --mes 9 saida.csv`. `OS.argv()` os entrega crus; `Cli.comando` os **declara** — nome, tipo, padrão, se é exigido — e confere, converte e gera a ajuda a partir disso."},
 {"code": '''adopt Arcane.Cli as Cli

programa := Cli.comando("relatorio", sobre := "Gera o relatório do mês.", versao := "1.0.0")
_ := programa.opcao("mes", "inteiro", curta := "m", exigida := yes, sobre := "de 1 a 12")
_ := programa.opcao("formato", escolhas := ["csv", "json"], padrao := "csv")
_ := programa.posicional("saida", exigido := no)

lido := programa.ler(["-m", "9", "--formato", "json", "saida.json"])
assert lido["mes"] is 9                     // já convertido para inteiro
assert lido["formato"] is "json"
assert lido["saida"] is "saida.json"

out programa.ajuda()''', "lang": "df"},
 {"h2": "O erro sugere o que existe"},
 {"code": '''adopt Arcane.Cli as Cli

programa := Cli.comando("relatorio")
_ := programa.opcao("mes", "inteiro")

sugeriu := no
monitor:
    programa.ler(["--mess", "9"])
handle Error as e:
    sugeriu := e.message.contains("--mes")
assert sugeriu''', "lang": "df"},
 {"list": [
   "**A ajuda é gerada.** Escrita à mão, ela envelhece na primeira opção nova — e ajuda errada é pior que nenhuma.",
   "**Chamado errado sai com 2**, e não 1: o script que chama distingue \"eu errei a chamada\" de \"o programa falhou\".",
   "**`Cli.perguntar`, `confirmar` e `segredo`** leem do terminal — e `Cli.tem_terminal()` diz se há alguém do outro lado, antes de travar esperando uma resposta num CI."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/partida/ambiente",
"title": "Ambiente e configuração",
"description": "Variáveis de ambiente com padrão, a configuração que falha na partida — e o segredo que nunca vai para o arquivo.",
"blocos": [
 {"p": "A mesma imagem roda em desenvolvimento, homologação e produção; o que muda é o **ambiente**. Ler a configuração de variáveis — e não de um arquivo dentro da imagem — é o que deixa o mesmo artefato ir para os três lugares."},
 {"code": '''adopt Arcane.OS as OS

porta := int(OS.get_env("PORTA", "8080"))
modo := OS.get_env("MODO", "desenvolvimento")
assert porta bigger 0
assert OS.get_env("VARIAVEL_QUE_NAO_EXISTE_AQUI") is void
assert not OS.has_env("VARIAVEL_QUE_NAO_EXISTE_AQUI")''', "lang": "df"},
 {"h2": "Falhe na partida, não no primeiro pedido"},
 {"p": "Uma variável obrigatória que falta deveria impedir o programa de **subir** — com uma mensagem que diz qual —, e não estourar no primeiro pedido que precisa dela, às três da manhã:"},
 {"code": '''adopt Arcane.OS as OS

action exigir(nomes):
    faltam := [n cycle n in nomes given not OS.has_env(n)]
    given len(faltam) bigger 0:
        trigger $"faltam variáveis de ambiente: {faltam.join(", ")}"

OS.set_env("BANCO_URL", "sqlite:///tmp/app.db")
exigir(["BANCO_URL"])                       // passa

recusado := no
monitor:
    exigir(["BANCO_URL", "CHAVE_DA_API"])
handle Error as e:
    recusado := e.message.contains("CHAVE_DA_API")
assert recusado
OS.unset_env("BANCO_URL")''', "lang": "df"},
 {"callout": {"tipo": "perigo", "titulo": "Segredo não é configuração", "texto": "Porta e modo podem estar num `.env` versionado de exemplo. Senha, token e chave **não**: eles vêm do ambiente de verdade, do gerenciador de segredos da plataforma, e nunca de um arquivo no repositório. `dataforge seguranca` procura segredo em arquivo de configuração — que é por onde eles mais vazam."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/partida/conteineres",
"title": "Dentro de um contêiner",
"description": "O programa como PID 1, o prazo do docker stop, o host 0.0.0.0 e a sonda de saúde.",
"blocos": [
 {"p": "Dentro de um contêiner, o seu programa costuma ser o **PID 1** — o primeiro processo. Isso muda três coisas que fora dele não importam."},
 {"table": {"head": ["O quê", "Fora", "Dentro do contêiner"], "rows": [
   ["SIGTERM sem tratador", "o processo morre", "o PID 1 **ignora** — e o `docker stop` espera 10 s e mata com SIGKILL"],
   ["o endereço `127.0.0.1`", "a máquina", "**o próprio contêiner**: nada de fora chega"],
   ["processos filhos que terminam", "o sistema limpa", "viram zumbis, se o PID 1 não os recolhe"]]}},
 {"code": '''adopt Arcane.Inicio as Inicio

// o tratador de SIGTERM é o que faz o 'docker stop' levar 50 ms, e não 10 s
Inicio.ao_encerrar(lambda => out "fila devolvida, banco fechado")
out "servindo"''', "lang": "df"},
 {"list": [
   "**`--host=0.0.0.0` no Kiln e na Vitrine.** Com o padrão `127.0.0.1`, o log diz \"no ar\" e o `curl` de fora não recebe nada — o defeito mais enganoso de um contêiner.",
   "**`dataforge devops init`** gera o Dockerfile com `USER` sem privilégio, `HEALTHCHECK` e a ordem de camadas que não reinstala tudo a cada commit.",
   "**A sonda de saúde responde do próprio processo**: uma rota `/saude` que confere o banco. Um contêiner vivo com o banco caído não deveria receber tráfego."]},
 {"p": "O guia completo, com compose, Kubernetes e o que cada artefato carrega: [DevOps](/docs/devops)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/hardware",
"title": "Hardware",
"description": "SIMD, cache, bare-metal e assembly — e por que, numa linguagem interpretada, a resposta honesta é quase sempre 'não se aplica'.",
"blocos": [
 {"p": "Otimização de hardware — vetorização, localidade de cache, instruções específicas — acontece **abaixo** do interpretador. Numa linguagem interpretada sobre o CPython, o custo de despachar cada nó da árvore domina qualquer efeito de cache em três ordens de grandeza. Fingir o contrário seria documentar o que não acontece."},
 {"table": {"head": ["Quer", "Aqui", "Página"], "rows": [
   ["SIMD, conta vetorizada", "a ponte para o `numpy`, que **é** vetorizado", "[A ponte](/docs/tecnicas/ponte)"],
   ["chamar código nativo", "`Arcane.C`", "[FFI](/docs/ffi)"],
   ["layout de memória exato", "`Arcane.Estrutura`", "[Estruturas](/docs/estruturas)"],
   ["vários núcleos", "`P.map_processos`", "[Concorrência](/docs/concorrencia)"],
   ["bare-metal, kernel, assembly", "não se aplica", "[O mapa](/docs/hardware/mapa)"]]}},
 {"code": '''adopt Arcane.C as C

assert C.endianness() in ["little", "big"]
assert C.tamanho_de("ponteiro") in [4, 8]      // 32 ou 64 bits''', "lang": "df"},
 {"cards": [
   {"href": "/docs/hardware/mapa", "title": "Hardware: o mapa", "desc": "cada item da referência, com a resposta e o que existe no lugar"},
   {"href": "/docs/alvos/portabilidade", "title": "Onde este programa roda", "desc": "os alvos, lidos dos adopt"}]},
]},
]
