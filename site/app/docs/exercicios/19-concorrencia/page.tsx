// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "19 · Concorrência",
  description: "6 exercícios: threads, canais, tarefas e paralelismo.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 19`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[170](#170-acoes-assincronas)", "**Acoes assincronas**", "declare acoes async e aguarde o resultado com await."], ["[171](#171-threads-e-paralelismo)", "**Threads e paralelismo**", "execute trabalho em segundo plano."], ["[172](#172-canais-entre-threads)", "**Canais entre threads**", "passe valores entre threads com seguranca."], ["[173](#173-liberacao-garantida)", "**Liberacao garantida**", "garanta limpeza mesmo quando algo falha."], ["[174](#174-erros-e-retentativas)", "**Erros e retentativas**", "trate falhas temporarias com retry e propagacao controlada."], ["[175](#175-projeto-fila-de-trabalho)", "**Projeto: fila de trabalho**", "monte um sistema de tarefas com fila, trabalhadores e relatorio."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "170 · Acoes assincronas"},
  {"p": "**Enunciado.** declare acoes async e aguarde o resultado com await."},
  { code: `// Uma acao async representa trabalho que pode demorar
async action buscar_usuario(id):
    yield {"id": id, "nome": $"Usuario {id}", "ativo": yes}

async action buscar_pedidos(id_usuario):
    yield [
        {"id": 100, "usuario": id_usuario, "total": 250.0},
        {"id": 101, "usuario": id_usuario, "total": 80.0}
    ]

// await resolve o resultado
usuario := await buscar_usuario(7)
pedidos := await buscar_pedidos(7)

out $"usuario: {usuario["nome"]}"
out $"pedidos: {len(pedidos)}"

assert usuario["id"] is 7, "id do usuario"
assert len(pedidos) is 2, "dois pedidos"

// Compor chamadas assincronas
async action perfil_completo(id):
    u := await buscar_usuario(id)
    p := await buscar_pedidos(id)
    total := p >> morph x: x["total"] >> distill acc, v: acc + v 0
    yield {
        "nome": u["nome"],
        "pedidos": len(p),
        "total_gasto": total
    }

perfil := await perfil_completo(7)
out ""
out perfil
assert perfil["total_gasto"] is 330.0, "250 + 80"

// Erros atravessam o await normalmente
async action pode_falhar(deve):
    given deve:
        trigger "a busca falhou"
    yield "ok"

out ""
monitor:
    await pode_falhar(yes)
handle e:
    out $"erro capturado: {e.message}"

assert await pode_falhar(no) is "ok", "caminho feliz"

// Varias chamadas em sequencia: cada uma espera a anterior
ids := [1, 2, 3]
nomes := []
cycle id in ids:
    u := await buscar_usuario(id)
    nomes.append(u["nome"])

out ""
out nomes
assert len(nomes) is 3, "tres usuarios"

// ── O que 'async' realmente compra ──
//
// Chamar uma acao async COMECA o trabalho e devolve a tarefa. Quem
// chama todas antes de aguardar qualquer uma paga o tempo da mais
// lenta, e nao a soma de todas.

adopt Arcane.Time as T

async action demorada(n):
    T.sleep(0.1)
    yield n * 10

// as quatro comecam aqui
inicio := T.monotonic()
tarefas := [demorada(n) cycle n in [1, 2, 3, 4]]
juntas := await tarefas
tempo_juntas := T.monotonic() - inicio

// e aqui uma de cada vez
inicio := T.monotonic()
uma_a_uma := []
cycle n in [1, 2, 3, 4]:
    uma_a_uma.append(await demorada(n))
tempo_sequencial := T.monotonic() - inicio

out ""
out $"juntas:    {round(tempo_juntas, 2)}s"
out $"uma a uma: {round(tempo_sequencial, 2)}s"

assert juntas is [10, 20, 30, 40], "os mesmos valores"
assert juntas is uma_a_uma, "so muda o tempo, nao o resultado"
assert tempo_juntas smaller tempo_sequencial, "quatro esperas juntas custam menos"

// A tarefa nao e o valor: usar uma sem 'await' e o engano mais comum.
pendente := buscar_usuario(9)
assert typeof(pendente) isnt "Vault", "a chamada devolve a tarefa"
assert await pendente is {"id": 9, "nome": "Usuario 9", "ativo": yes}, "o await entrega o vault"`, lang: 'df', title: `exercicios/19-concorrencia/170_async_await.df` },
  {"h3": "Conceitos"},
  { code: `async action buscar_usuario(id):
    yield {"id": id, "nome": $"Usuario {id}"}

usuario := await buscar_usuario(7)`, lang: 'df' },
  {"p": "Chamar uma ação `async` **começa o trabalho** numa thread e devolve a *tarefa*. `await` espera ela terminar e entrega o valor."},
  {"h3": "Para que serve"},
  {"p": "Representar trabalho que **espera** por algo externo — rede, disco, banco. Enquanto uma operação espera, o programa faz outra."},
  {"p": "Só que escrito assim, uma de cada vez, `async` não compra nada: o `await` na linha seguinte cancela qualquer sobreposição. O ganho está em **chamar todas antes de aguardar qualquer uma**:"},
  { code: `// as quatro comecam aqui
tarefas := [demorada(n) cycle n in [1, 2, 3, 4]]

// e aqui so se espera a mais lenta
valores := await tarefas`, lang: 'df' },
  {"table": {"head": ["Como está escrito", "Quatro esperas de 0,1 s custam"], "rows": [["`tarefas := [...]` e depois `await tarefas`", "**0,1 s**"], ["`cycle` com `await` dentro", "**0,4 s**"]]}},
  {"p": "O exercício mede as duas formas e compara. Rode e veja."},
  {"h3": "O que acelera e o que não"},
  {"p": "As tarefas são threads. Elas se sobrepõem enquanto uma está **esperando algo de fora**. Para contas, não — o GIL do Python deixa uma thread por vez executar código, e vinte tarefas somando números levam o mesmo tempo que uma."},
  {"list": ["entrada e saída (rede, disco, banco, `sleep`) → `async`", "trabalho de CPU → `Arcane.Concurrent`, que usa processos"]},
  {"h3": "A tarefa não é o valor"},
  {"p": "O engano mais comum de quem escreve código assíncrono, em qualquer linguagem:"},
  { code: `u := buscar_usuario(1)
out u["nome"]          // erro: 'u' e a tarefa, nao o vault`, lang: 'df' },
  {"p": "A linguagem aponta a linha e diz a palavra que faltou."},
  {"h3": "Compor"},
  { code: `async action perfil_completo(id):
    u := await buscar_usuario(id)
    p := await buscar_pedidos(id)
    yield {...}`, lang: 'df' },
  {"p": "Uma ação `async` pode aguardar outras. O resultado se lê de cima para baixo, como código síncrono — que é justamente a razão de `async/await` existir em vez de callbacks aninhados."},
  {"h3": "Erros"},
  {"p": "`await` propaga o erro normalmente:"},
  { code: `monitor:
    await pode_falhar(yes)
handle e:
    out $"erro capturado: {e.message}"`, lang: 'df' },
  {"p": "Nada de especial: o `monitor` funciona igual ao redor de código síncrono."},
  {"h3": "O que ainda não existe"},
  {"p": "O roadmap prevê, e vale saber que **ainda não está aqui**:"},
  {"list": ["cancelamento de tarefa em andamento", "`await` com prazo — hoje ele espera o tempo que for", "`Mutex`, `Semaphore`, `Atomic`"]},
  {"p": "Aguardar várias ao mesmo tempo **já existe**: `await` sobre um cluster de tarefas espera todas. Para dividir trabalho de CPU, veja `thread`, `channel` e `Arcane.Concurrent` (próximos exercícios)."},
  {"h3": "Saída esperada"},
  { code: `usuario: Usuario 7
pedidos: 2

{nome: Usuario 7, pedidos: 2, total_gasto: 330.0}

erro capturado: a busca falhou

[Usuario 1, Usuario 2, Usuario 3]

juntas:    0.1s
uma a uma: 0.4s`, lang: 'text' },
  {"p": "Os dois tempos variam com a máquina; o que não varia é a diferença entre eles."},
  {"h3": "Experimente"},
  {"list": ["Escreva uma cadeia de três ações async que dependem uma da outra.", "Combine `await` com `retry` para uma busca que pode falhar temporariamente.", "Troque `T.sleep(0.1)` por uma conta pesada e meça de novo: o ganho some, e"]},
  {"p": "esse é o limite do GIL aparecendo."},
  {"h2": "171 · Threads e paralelismo"},
  {"p": "**Enunciado.** execute trabalho em segundo plano."},
  { code: `adopt Arcane.Time as Time

// Um bloco thread roda em segundo plano
resultados := []

thread:
    cycle i from 1 to 3:
        resultados.append($"A{i}")

thread:
    cycle i from 1 to 3:
        resultados.append($"B{i}")

// Espera as threads terminarem
wait 200

out $"itens produzidos: {len(resultados)}"
assert len(resultados) is 6, "as duas threads produziram"

// parallel roda cada instrucao em uma thread
adopt Arcane.Math as Math

saidas := []
parallel:
    saidas.append($"fatorial: {Math.factorial(12)}")
    saidas.append($"fibonacci: {Math.fibonacci(25)}")
    saidas.append($"primo: {Math.is_prime(9973)}")

wait 300
out ""
cycle s in sorted(saidas):
    out $"  {s}"
assert len(saidas) is 3, "tres tarefas"

// Medindo: trabalho concorrente
action trabalho(n):
    total := 0
    cycle i from 1 to n:
        total += i * i
    yield total

crono := Time.stopwatch()
crono.start()

sequencial := []
cycle n in [50000, 50000, 50000]:
    sequencial.append(trabalho(n))

tempo_seq := crono.stop()
out ""
out $"sequencial: {round(tempo_seq * 1000, 1)} ms"
assert len(sequencial) is 3, "tres resultados"

// Aviso importante: sem sincronizacao, atualizacoes se perdem
//
// O 'check' ACUSA as duas linhas abaixo — e esta certo. Aqui a corrida
// e o assunto do exercicio, e 'df: permitir' diz isso a ele. A regra e
// nomeada: um 'permitir' solto esconderia o erro seguinte.
contador := {"valor": 0}

thread:
    cycle _ in range(0, 1000):
        // df: permitir escrita-concorrente
        contador["valor"] := contador["valor"] + 1

thread:
    cycle _ in range(0, 1000):
        // df: permitir escrita-concorrente
        contador["valor"] := contador["valor"] + 1

wait 400

// O NUMERO nao e impresso — e ele que varia.
//
// Este exercicio existe para mostrar a corrida, e por isso o resultado
// dele e instavel de proposito: 2000 nesta maquina, 1847 no CI, outro
// numero na proxima execucao. O teste que compara a saida com a
// compilacao ligada e desligada roda o arquivo DUAS vezes e exige saida
// identica — e reprovou.
//
// Imprimir a instabilidade era a forma errada de ensina-la. A forma
// certa e AFIRMAR o que se sabe: o valor nunca passa do esperado,
// porque duas threads so podem perder incrementos, nunca inventar.
valor := contador["valor"]

assert valor smaller_eq 2000, "nunca passa: so se perde, nao se inventa"
assert valor bigger 0, "algo foi contado"

out ""
given valor smaller 2000:
    out "o contador veio MENOR que 2000: voce acabou de ver uma"
    out "condicao de corrida acontecer."
otherwise:
    out "o contador fechou em 2000 NESTA execucao — e sorte, nao"
    out "garantia. Na proxima, ou em outra maquina, pode nao fechar."

// ── E a saida, no mesmo arquivo ──────────────────────────────
//
// 'Conc.contador()' e atomico: o incremento acontece dentro de uma
// trava, e o numero fecha SEMPRE. Nao ha o que torcer.
adopt Arcane.Concurrent as Conc

atomico := Conc.contador()

thread:
    cycle _ in range(0, 1000):
        atomico.somar(1)

thread:
    cycle _ in range(0, 1000):
        atomico.somar(1)

wait 400

out ""
out $"com Conc.contador(): {atomico.valor()} — e sempre 2000"
assert atomico.valor() is 2000, "o contador atomico nao perde nada"`, lang: 'df', title: `exercicios/19-concorrencia/171_threads.df` },
  {"h3": "`thread`"},
  { code: `thread:
    cycle i from 1 to 3:
        resultados.append($"A{i}")`, lang: 'df' },
  {"p": "O bloco roda numa thread daemon: o programa **não espera** por ela. Se o programa principal terminar antes, a thread é interrompida no meio."},
  {"p": "Por isso o `wait 200` — sem ele, o programa acabaria antes das threads produzirem qualquer coisa."},
  {"h3": "`parallel`"},
  { code: `parallel:
    saidas.append(tarefa_a())
    saidas.append(tarefa_b())
    saidas.append(tarefa_c())`, lang: 'df' },
  {"p": "**Cada instrução** do bloco vai para uma thread, e há um join de 30 segundos no fim."},
  {"p": "Note a semântica: é uma thread por *instrução*, não uma thread para o bloco inteiro. Isso é uma limitação conhecida — o roadmap prevê mudar para blocos. Enquanto isso, mantenha cada linha do `parallel` autossuficiente."},
  {"h3": "A condição de corrida"},
  {"p": "O último trecho do exercício é o mais importante:"},
  { code: `contador := {"valor": 0}

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1`, lang: 'df' },
  {"p": "O resultado **deveria** ser 2000. Frequentemente é menos."},
  {"p": "O motivo: `contador[\"valor\"] + 1` são três passos — ler, somar, escrever. Se as duas threads leem 5 ao mesmo tempo, ambas escrevem 6. Um incremento se perdeu."},
  {"p": "Rode várias vezes: o número muda. Esse é o tipo de bug que passa em teste e quebra em produção sob carga."},
  {"p": "**O `check` avisa**"},
  { code: `aviso: 'contador' e escrito dentro de 'thread' e vem de fora:
       duas threads podem perder atualizacoes
   sugestao: a linguagem nao sincroniza sozinha — use
             'Arcane.Concurrent': 'contador()' para somar,
             'mutex()' para um bloco, ou 'canal()' para passar
             o valor adiante`, lang: 'text' },
  {"p": "Aqui a corrida é o assunto, então o exercício usa `// df: permitir escrita-concorrente` nas duas linhas. Num código de verdade, o aviso é para ser atendido."},
  {"p": "**E a saída, no mesmo arquivo**"},
  { code: `adopt Arcane.Concurrent as Conc

atomico := Conc.contador()

thread:
    cycle _ in range(0, 1000):
        atomico.somar(1)

thread:
    cycle _ in range(0, 1000):
        atomico.somar(1)

assert atomico.valor() is 2000      // sempre`, lang: 'df' },
  {"p": "O incremento acontece dentro de uma trava. Não há o que torcer."},
  {"p": "**Por que o número não é impresso**"},
  {"p": "A primeira versão deste exercício imprimia `contador[\"valor\"]`, e **isso reprovou a CI**: `test_a_compilacao_nao_muda_o_resultado_de_nenhum_exercicio` roda cada arquivo duas vezes e exige saída idêntica. Deu 2000 numa execução e 1847 na outra — a corrida acontecendo, que é o ponto."},
  {"p": "Imprimir a instabilidade era a forma errada de ensiná-la. A forma certa é afirmar o que se **sabe**:"},
  { code: `assert valor smaller_eq 2000, "nunca passa: so se perde, nao se inventa"
assert valor bigger 0, "algo foi contado"`, lang: 'df' },
  {"p": "Duas threads só podem **perder** incrementos, nunca inventar — então o limite superior é garantido. O texto diz qual dos dois casos aconteceu nesta execução, sem imprimir o número."},
  {"h3": "Como evitar"},
  {"p": "**DataForge 4.0 não tem mutex nem lock.** A ferramenta segura é `channel`:"},
  { code: `channel resultados
thread:
    resultados.send(calcular())`, lang: 'df' },
  {"p": "Cada thread envia o que produziu; a thread principal recebe e agrega. Ninguém escreve na mesma variável."},
  {"p": "O próximo exercício mostra esse padrão."},
  {"h3": "Regra prática"},
  {"table": {"head": ["Situação", "Seguro?"], "rows": [["threads só leem dados compartilhados", "sim"], ["cada thread escreve numa variável própria", "sim"], ["threads enviam por `channel`", "sim"], ["duas threads escrevem na mesma variável", "**não**"], ["`lista.append` de duas threads", "**não**"]]}},
  {"h3": "Saída esperada"},
  { code: `itens produzidos: 6

  fatorial: 479001600
  fibonacci: 75025
  primo: yes

sequencial: 24.3 ms

o contador fechou em 2000 NESTA execucao — e sorte, nao
garantia. Na proxima, ou em outra maquina, pode nao fechar.

com Conc.contador(): 2000 — e sempre 2000`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Rode cinco vezes e veja a mensagem mudar entre \"fechou\" e \"veio menor\""]},
  {"p": "— na sua máquina, num dos dois, mais cedo ou mais tarde."},
  {"list": ["Ponha carga na máquina (`yes > /dev/null &` algumas vezes) e rode de"]},
  {"p": "novo: a corrida aparece mais."},
  {"list": ["Troque o `Conc.contador()` pelo vault e veja o `assert` do fim falhar."]},
  {"h2": "172 · Canais entre threads"},
  {"p": "**Enunciado.** passe valores entre threads com seguranca."},
  { code: `// Um canal e uma fila com trava: seguro entre threads
channel fila

fila.send("primeiro")
fila.send("segundo")
fila.send("terceiro")

out fila.receive()
out fila.receive()
assert fila.receive() is "terceiro", "FIFO"
assert fila.receive() is void, "canal vazio devolve void"

// O padrao correto: cada thread envia, a principal recolhe
channel resultados

action trabalho_pesado(n):
    total := 0
    cycle i from 1 to n:
        total += i
    yield total

thread:
    resultados.send({"tarefa": "A", "valor": trabalho_pesado(10000)})

thread:
    resultados.send({"tarefa": "B", "valor": trabalho_pesado(20000)})

thread:
    resultados.send({"tarefa": "C", "valor": trabalho_pesado(30000)})

wait 400

// Recolhe tudo que chegou
colhidos := []
persist yes:
    item := resultados.receive()
    given item is void:
        halt
    colhidos.append(item)

out ""
out $"colhidos: {len(colhidos)}"
cycle c in sorted(colhidos >> morph c: c["tarefa"]):
    out $"  tarefa {c}"

assert len(colhidos) is 3, "as tres threads reportaram"

// Contador correto: cada thread manda seu total
channel parciais

thread:
    soma := 0
    cycle _ in range(0, 1000):
        soma += 1
    parciais.send(soma)

thread:
    soma := 0
    cycle _ in range(0, 1000):
        soma += 1
    parciais.send(soma)

wait 400

total := 0
persist yes:
    parcial := parciais.receive()
    given parcial is void:
        halt
    total += parcial

out ""
out $"total pelo canal: {total}"
assert total is 2000, "sem condicao de corrida"
out "cada thread trabalhou no proprio escopo e reportou pelo canal"

// Um canal tambem serve de fila de trabalho
channel tarefas
cycle t in ["compilar", "testar", "empacotar", "publicar"]:
    tarefas.send(t)

out ""
out "── processando a fila ──"
persist yes:
    t := tarefas.receive()
    given t is void:
        halt
    out $"  executando: {t}"

// ── Esperar pelo item, em vez de perguntar ──────────────────────
//
// Ate aqui, 'receive()' devolve void na hora quando o canal esta vazio,
// e por isso o laco acima para no primeiro void. Isso so funciona porque
// as threads JA terminaram de enviar ('wait 400'). Com um produtor que
// ainda esta trabalhando, o void chegaria antes do item — e o 'wait' e
// um chute de quanto tempo basta.
//
// 'receive(ms)' espera ate aquele prazo; 'receive(void)' espera o que
// for preciso. A thread dorme ate o item chegar, sem gastar CPU num laco.

channel pedidos

thread:
    sleep(120)
    pedidos.send("pedido 1")
    sleep(120)
    pedidos.send("pedido 2")
    pedidos.send("fim")

out ""
out "── consumidor que espera ──"
recebidos := []
persist yes:
    p := pedidos.receive(5000)
    given p is void or p is "fim":
        halt
    out $"  chegou: {p}"
    recebidos.append(p)

assert recebidos is ["pedido 1", "pedido 2"], "esperou os dois, sem 'wait'"

// O prazo expira e devolve void — o mesmo void de antes
assert pedidos.receive(50) is void, "prazo curto num canal vazio"
out "o consumidor esperou cada item, sem adivinhar quanto tempo bastava"`, lang: 'df', title: `exercicios/19-concorrencia/172_canais.df` },
  {"h3": "O que é um canal"},
  { code: `channel fila
fila.send(valor)
fila.receive()      // o próximo, ou void se estiver vazio`, lang: 'df' },
  {"p": "Uma fila FIFO **com trava interna**. `send` e `receive` são seguros de chamar de qualquer thread — a implementação garante que dois envios simultâneos não se atropelam."},
  {"h3": "O padrão que resolve a corrida"},
  {"p": "O exercício anterior mostrou o problema: duas threads incrementando a mesma variável perdem atualizações. A solução não é sincronizar o acesso — é **não compartilhar**:"},
  { code: `channel parciais

thread:
    soma := 0                  // variável local desta thread
    cycle _ in range(0, 1000):
        soma += 1
    parciais.send(soma)        // reporta uma vez, no fim`, lang: 'df' },
  {"p": "Cada thread trabalha no próprio escopo. Ninguém escreve onde outro lê. No fim, a thread principal soma os parciais — e o resultado é 2000, sempre."},
  {"p": "Essa ideia tem nome: *\"não comunique compartilhando memória; compartilhe memória comunicando\"* — é o lema de Go, e vale igual aqui."},
  {"h3": "Recolher tudo"},
  {"p": "Como `receive` devolve `void` quando a fila esvazia:"},
  { code: `persist yes:
    item := canal.receive()
    given item is void:
        halt
    colhidos.append(item)`, lang: 'df' },
  {"h3": "Fila de trabalho"},
  {"p": "O mesmo canal serve para distribuir tarefas:"},
  { code: `channel tarefas
cycle t in ["compilar", "testar", "empacotar"]:
    tarefas.send(t)

// vários trabalhadores podem consumir daqui
persist yes:
    t := tarefas.receive()
    given t is void:
        halt
    executar(t)`, lang: 'df' },
  {"p": "Cada tarefa vai para exatamente um consumidor — a trava garante isso."},
  {"h3": "Perguntar ou esperar"},
  {"p": "`receive()` **não espera**: devolve `void` na hora se a fila estiver vazia. É por isso que a primeira parte do exercício precisa de um `wait` — ele dá tempo às threads, e é um chute de quanto tempo basta."},
  {"p": "Para esperar pelo item, passe o prazo:"},
  { code: `fila.receive()          // void na hora, se vazio
fila.receive(2000)      // espera até 2 segundos; depois, void
fila.receive(void)      // espera o que for preciso`, lang: 'df' },
  {"p": "A última parte do exercício usa `receive(5000)`: o consumidor dorme até cada pedido chegar, sem gastar CPU num laço e sem adivinhar quanto tempo basta. O prazo é em **milissegundos**, a mesma unidade de `sleep`."},
  {"p": "O padrão sem argumento continua não esperando **de propósito**: mudá-lo não daria erro em programa nenhum, daria **travamento** — o pior tipo de falha, porque não deixa mensagem nem pilha para investigar."},
  {"h3": "Saída esperada"},
  { code: `primeiro
segundo

colhidos: 3
  tarefa A
  tarefa B
  tarefa C

total pelo canal: 2000
cada thread trabalhou no proprio escopo e reportou pelo canal

── processando a fila ──
  executando: compilar
  executando: testar
  executando: empacotar
  executando: publicar`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Monte um pool: N threads consumindo da mesma fila de tarefas.", "Use dois canais — um de entrada, um de saída — para um pipeline concorrente."]},
  {"h2": "173 · Liberacao garantida"},
  {"p": "**Enunciado.** garanta limpeza mesmo quando algo falha."},
  { code: `adopt Arcane.IO as IO

// defer roda ao sair da acao, em qualquer caminho
ordem := []

action com_recurso(deve_falhar):
    ordem.append("abriu")
    defer:
        ordem.append("fechou")
    given deve_falhar:
        trigger "falhou no meio"
    ordem.append("usou")
    yield "concluido"

// Caminho feliz
ordem := []
out com_recurso(no)
out ordem
assert ordem is ["abriu", "usou", "fechou"], "defer roda no fim"

// Caminho com erro: o defer roda mesmo assim
ordem := []
monitor:
    com_recurso(yes)
handle e:
    ordem.append($"tratou: {e.message}")

out ""
out ordem
assert ordem[1] is "fechou", "o defer rodou antes do erro subir"
assert len(ordem) is 3, "abriu, fechou, tratou"

// Varios defer rodam em ordem inversa (LIFO)
pilha := []
action varios():
    defer:
        pilha.append("primeiro declarado")
    defer:
        pilha.append("segundo declarado")
    defer:
        pilha.append("terceiro declarado")
    yield void

varios()
out ""
out pilha
assert pilha[0] is "terceiro declarado", "o ultimo declarado roda primeiro"

// Uso real: arquivo temporario sempre removido
action processar_com_temporario(deve_falhar):
    caminho := "_temp_exercicio_172.txt"
    IO.write(caminho, "dados de trabalho")
    defer:
        given IO.exists(caminho):
            IO.delete(caminho)
    given deve_falhar:
        trigger "erro durante o processamento"
    yield IO.read(caminho).upper()

out ""
out processar_com_temporario(no)
assert IO.exists("_temp_exercicio_172.txt") is no, "removido apos sucesso"

monitor:
    processar_com_temporario(yes)
handle e:
    out $"erro: {e.message}"

assert IO.exists("_temp_exercicio_172.txt") is no, "removido apos falha tambem"
out "o arquivo temporario nao sobreviveu a nenhum dos caminhos"

// defer em cadeia de chamadas: cada acao limpa a sua parte
trilha := []

action interna():
    defer:
        trilha.append("interna limpou")
    trigger "falha na interna"

action externa():
    defer:
        trilha.append("externa limpou")
    interna()

monitor:
    externa()
handle e:
    trilha.append("topo tratou")

out ""
out trilha
assert trilha is ["interna limpou", "externa limpou", "topo tratou"], "de dentro para fora"`, lang: 'df', title: `exercicios/19-concorrencia/173_defer_recursos.df` },
  {"h3": "O problema"},
  { code: `action processar():
    arquivo := abrir("dados.txt")
    // ... se algo aqui disparar, o arquivo nunca fecha
    fechar(arquivo)`, lang: 'df' },
  {"p": "Todo caminho de saída precisaria repetir o `fechar` — e é sempre o caminho de erro que alguém esquece."},
  {"h3": "`defer`"},
  { code: `action com_recurso():
    abrir()
    defer:
        fechar()
    // ... o defer roda aconteça o que acontecer`, lang: 'df' },
  {"p": "O bloco `defer` roda ao sair da ação, em **todos** os caminhos:"},
  {"table": {"head": ["Saída", "`defer` roda?"], "rows": [["chegou ao fim", "sim"], ["`yield` no meio", "sim"], ["`trigger` / erro", "sim"], ["erro vindo de uma ação chamada", "sim"]]}},
  {"p": "> Este comportamento no caminho de erro foi corrigido no 4.0 — antes, o `defer` > só rodava no sucesso, deixando arquivos temporários para trás."},
  {"h3": "Declare junto de quem adquire"},
  { code: `IO.write(caminho, "dados")
defer:
    IO.delete(caminho)`, lang: 'df' },
  {"p": "O `defer` fica **imediatamente após** a aquisição. Assim, ler o código é ver o par completo — não há como esquecer a limpeza porque ela está uma linha abaixo."},
  {"h3": "LIFO: o último declarado roda primeiro"},
  { code: `defer:
    fechar_arquivo()      // roda por último
defer:
    fechar_conexao()      // roda primeiro`, lang: 'df' },
  {"p": "A ordem inversa é a correta para recursos que dependem uns dos outros: você desmonta na ordem oposta à que montou."},
  {"h3": "Em cadeia"},
  { code: `action interna():
    defer:
        trilha.append("interna limpou")
    trigger "falha"

action externa():
    defer:
        trilha.append("externa limpou")
    interna()`, lang: 'df' },
  {"p": "O erro sobe pela pilha, e cada `defer` roda no caminho — **de dentro para fora**. Cada ação limpa o que ela própria adquiriu, sem precisar saber do resto."},
  {"h3": "`defer` ou `ensure`?"},
  {"table": {"head": ["", "`defer`", "`ensure`"], "rows": [["Escopo", "a ação inteira", "um bloco `monitor`"], ["Declaração", "junto da aquisição", "no fim do bloco"], ["Vários", "sim, em LIFO", "um por `monitor`"]]}},
  {"p": "Use `defer` para recursos; `ensure` quando a limpeza pertence a um trecho específico que você já estava envolvendo em `monitor`."},
  {"h3": "Saída esperada"},
  { code: `concluido
[abriu, usou, fechou]

[abriu, fechou, tratou: falhou no meio]

[terceiro declarado, segundo declarado, primeiro declarado]

DADOS DE TRABALHO
erro: erro durante o processamento
o arquivo temporario nao sobreviveu a nenhum dos caminhos

[interna limpou, externa limpou, topo tratou]`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Combine `defer` com `DB.close` numa ação que abre banco.", "Escreva `com_arquivo(caminho, acao)` que abre, chama e fecha com `defer`."]},
  {"h2": "174 · Erros e retentativas"},
  {"p": "**Enunciado.** trate falhas temporarias com retry e propagacao controlada."},
  { code: `adopt Arcane.Logging as Log

registro := Log.logger("rede", "INFO")
registro.colored(no)

// Simula uma operacao instavel
estado := {"tentativas": 0}

action chamada_instavel():
    estado["tentativas"] := estado["tentativas"] + 1
    given estado["tentativas"] smaller 3:
        trigger $"timeout na tentativa {estado["tentativas"]}"
    yield $"sucesso na tentativa {estado["tentativas"]}"

// retry repete ate conseguir
out "── com retry ──"
retry 5:
    resultado := chamada_instavel()
    out $"  {resultado}"
handle e:
    out $"  desistiu: {e}"

assert estado["tentativas"] is 3, "precisou de tres tentativas"

// Quando todas falham, o handler final roda
estado2 := {"n": 0}
action sempre_falha():
    estado2["n"] := estado2["n"] + 1
    trigger "indisponivel"

out ""
out "── falhando sempre ──"
capturou := no
retry 3:
    sempre_falha()
handle e:
    capturou := yes
    out $"  apos {estado2["n"]} tentativas: {e}"

assert estado2["n"] is 3, "tentou tres vezes"
assert capturou is yes, "o handler final rodou"

// Espera crescente entre tentativas
out ""
out "── com espera crescente ──"
espera := {"ms": 10}
tentativa := {"n": 0}

action com_recuo():
    tentativa["n"] := tentativa["n"] + 1
    given tentativa["n"] smaller 3:
        out $"  tentativa {tentativa["n"]} falhou, esperando {espera["ms"]}ms"
        wait espera["ms"]
        espera["ms"] := espera["ms"] * 2
        trigger "ainda indisponivel"
    yield "conectado"

retry 5:
    out $"  {com_recuo()}"
handle e:
    out $"  desistiu: {e}"

assert espera["ms"] is 40, "10 -> 20 -> 40"

// Registrar e repassar
out ""
out "── logando e propagando ──"

action camada_baixa():
    trigger "disco cheio"

action camada_media():
    monitor:
        camada_baixa()
    handle e:
        registro.error("falha na camada baixa", {"motivo": e.message})
        propagate e.message

monitor:
    camada_media()
handle e:
    out $"  o topo recebeu: {e.message}"

// Nem todo erro merece retry
action classificar_erro(mensagem):
    temporarios := ["timeout", "indisponivel", "conexao recusada"]
    cycle t in temporarios:
        given t in mensagem:
            yield "tentar de novo"
    yield "desistir"

out ""
out "── decidindo sobre retry ──"
cycle m in ["timeout ao conectar", "senha invalida", "servico indisponivel", "404 nao encontrado"]:
    out $"  {m.pad_end(26)} -> {classificar_erro(m)}"

assert classificar_erro("timeout ao conectar") is "tentar de novo", "temporario"
assert classificar_erro("senha invalida") is "desistir", "permanente"`, lang: 'df', title: `exercicios/19-concorrencia/174_erros_concorrentes.df` },
  {"h3": "`retry`"},
  { code: `retry 5:
    resultado := chamada_instavel()
    out resultado
handle e:
    out $"desistiu: {e}"`, lang: 'df' },
  {"p": "Tenta o bloco até 5 vezes. Se alguma tentativa der certo, o `retry` termina ali. Se todas falharem, o `handle` roda com o **último** erro."},
  {"h3": "Nem todo erro merece retry"},
  {"p": "Esta é a distinção que separa retry útil de retry inútil:"},
  {"table": {"head": ["Tipo", "Exemplos", "Repetir?"], "rows": [["**Temporário**", "timeout, serviço indisponível, conexão recusada", "sim"], ["**Permanente**", "senha inválida, 404, dado malformado", "não"]]}},
  {"p": "Repetir um erro permanente é desperdício garantido: a senha não vai ficar válida na terceira tentativa. Pior, atrasa a mensagem de erro que o usuário precisa ver."},
  { code: `action classificar_erro(mensagem):
    temporarios := ["timeout", "indisponivel", "conexao recusada"]
    cycle t in temporarios:
        given t in mensagem:
            yield "tentar de novo"
    yield "desistir"`, lang: 'df' },
  {"h3": "Espera crescente"},
  {"p": "Repetir imediatamente contra um serviço sobrecarregado piora a sobrecarga. A prática correta é dobrar a espera:"},
  { code: `espera := {"ms": 10}
// falha → espera 10ms → falha → espera 20ms → falha → espera 40ms
espera["ms"] := espera["ms"] * 2`, lang: 'df' },
  {"p": "Isso tem nome — *exponential backoff* — e é o que evita que N clientes em retry derrubem um serviço que estava só se recuperando."},
  {"h3": "Registrar e repassar"},
  { code: `action camada_media():
    monitor:
        camada_baixa()
    handle e:
        registro.error("falha na camada baixa", {"motivo": e.message})
        propagate e.message`, lang: 'df' },
  {"p": "`propagate` relança depois de registrar. A camada do meio **anota o que sabe** — contexto que o topo não teria — mas não decide o que fazer. Essa decisão pertence a quem tem visão do todo."},
  {"p": "O anti-padrão oposto é engolir:"},
  { code: `handle e:
    registro.error("falhou")     // e agora? o chamador acha que deu certo`, lang: 'df' },
  {"h3": "Regra de ouro"},
  {"p": "**Trate o erro onde você pode fazer algo a respeito.** Nas camadas intermediárias, registre e repasse."},
  {"h3": "Saída esperada"},
  { code: `── com retry ──
  sucesso na tentativa 3

── falhando sempre ──
  apos 3 tentativas: indisponivel

── com espera crescente ──
  tentativa 1 falhou, esperando 10ms
  tentativa 2 falhou, esperando 20ms
  conectado

── logando e propagando ──
23:59:01 ERROR [rede] falha na camada baixa motivo=disco cheio
  o topo recebeu: disco cheio

── decidindo sobre retry ──
  timeout ao conectar        -> tentar de novo
  senha invalida             -> desistir
  servico indisponivel       -> tentar de novo
  404 nao encontrado         -> desistir`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Escreva `retry_inteligente(acao, n)` que só repete erros temporários.", "Acrescente um limite total de tempo além do número de tentativas."]},
  {"h2": "175 · Projeto: fila de trabalho"},
  {"p": "**Enunciado.** monte um sistema de tarefas com fila, trabalhadores e relatorio."},
  { code: `adopt Arcane.Collections as Col
adopt Arcane.Time as Time
adopt Arcane.Logging as Log
adopt Arcane.Text as Text

// ═══ MODELO ═══

enum Estado:
    Pendente
    Executando
    Concluida
    Falhou

record Tarefa:
    id: Integer
    nome: String
    prioridade: Integer
    duracao_ms: Integer

// ═══ FILA COM PRIORIDADE ═══

fila := Col.priority_queue()

tarefas := [
    Tarefa(1, "enviar email", 5, 10),
    Tarefa(2, "processar pagamento", 1, 20),
    Tarefa(3, "gerar relatorio", 8, 15),
    Tarefa(4, "backup", 9, 25),
    Tarefa(5, "alerta de seguranca", 1, 5),
    Tarefa(6, "limpar cache", 7, 10)
]

cycle t in tarefas:
    fila.push(t, t.prioridade)

out Text.box("Fila de Trabalho")
out $"tarefas na fila: {fila.size()}"
assert fila.size() is 6, "seis tarefas"

// ═══ EXECUCAO ═══

registro := Log.logger("worker", "INFO")
registro.colored(no)

historico := []
falhas := {"n": 0}

action executar(t):
    // Simula o trabalho levando o tempo declarado
    wait t.duracao_ms
    given t.nome.contains("pagamento"):
        trigger "gateway indisponivel"
    yield $"{t.nome} concluida"

out ""
out "── processando por prioridade ──"

crono := Time.stopwatch()
crono.start()

persist yes:
    t := fila.pop()
    given t is void:
        halt

    resultado := {"tarefa": t, "estado": Estado.Executando, "detalhe": ""}

    retry 2:
        saida := executar(t)
        resultado["estado"] := Estado.Concluida
        resultado["detalhe"] := saida
    handle e:
        resultado["estado"] := Estado.Falhou
        resultado["detalhe"] := e
        falhas["n"] := falhas["n"] + 1

    historico.append(resultado)
    marca := "ok " given resultado["estado"] is Estado.Concluida otherwise "ERR"
    out $"  [p{t.prioridade}] {marca} {t.nome.pad_end(22)} {resultado["detalhe"]}"

decorrido := crono.stop()

// ═══ RELATORIO ═══

out ""
out Text.box("Relatorio")

concluidas := historico >> sift h: h["estado"] is Estado.Concluida
falhadas := historico >> sift h: h["estado"] is Estado.Falhou

out $"total:      {len(historico)}"
out $"concluidas: {len(concluidas)}"
out $"falhadas:   {len(falhadas)}"
out $"tempo:      {round(decorrido * 1000, 1)} ms"

assert len(historico) is 6, "todas processadas"
assert len(falhadas) is 1, "so o pagamento falhou"
assert falhas["n"] is 1, "uma falha contabilizada"

// A ordem seguiu a prioridade, nao a de insercao
ordem := historico >> morph h: h["tarefa"].prioridade
out ""
out $"ordem de execucao (prioridade): {ordem}"
assert ordem is sorted(ordem), "menor prioridade primeiro"
assert ordem[0] is 1, "as urgentes vieram antes"

// Agrupar por estado
out ""
out "── por estado ──"
cycle nome_estado in Estado.names():
    quantos := len(historico >> sift h: h["estado"].name is nome_estado)
    given quantos bigger 0:
        out $"  {nome_estado.pad_end(12)} {"#".repeat(quantos)} ({quantos})"

// As que falharam voltam para a fila
out ""
given len(falhadas) bigger 0:
    out "── reenfileirando falhas ──"
    cycle h in falhadas:
        t := h["tarefa"]
        fila.push(t, 0)
        out $"  {t.nome} volta com prioridade maxima"
    assert fila.size() is 1, "uma tarefa reenfileirada"`, lang: 'df', title: `exercicios/19-concorrencia/175_projeto_worker.df` },
  {"h3": "A arquitetura"},
  { code: `MODELO       enum Estado, record Tarefa
FILA         Col.priority_queue
EXECUCAO     retry + registro de estado
RELATORIO    agregação por estado e prioridade`, lang: 'text' },
  {"h3": "Fila de prioridade"},
  { code: `fila := Col.priority_queue()
fila.push(tarefa, tarefa.prioridade)
t := fila.pop()      // sempre a de MENOR número`, lang: 'df' },
  {"p": "Menor número = mais urgente. A convenção pode parecer invertida, mas é a tradicional: \"prioridade 1\" é o topo da lista."},
  {"p": "Isso permite inserir em qualquer ordem e sempre tirar a certa. No exercício, `alerta de seguranca` (p1) sai antes de `backup` (p9), mesmo tendo entrado depois."},
  {"h3": "Estado como enum"},
  { code: `enum Estado:
    Pendente
    Executando
    Concluida
    Falhou`, lang: 'df' },
  {"p": "Comparado a guardar `\"concluida\"` como texto: um erro de digitação vira erro na hora, e `Estado.names()` dá a lista completa para o relatório sem repetição."},
  {"h3": "Retentativa por tarefa"},
  { code: `retry 2:
    saida := executar(t)
    resultado["estado"] := Estado.Concluida
handle e:
    resultado["estado"] := Estado.Falhou
    resultado["detalhe"] := e`, lang: 'df' },
  {"p": "O `retry` fica em volta de **uma** tarefa. Uma falha não interrompe a fila — ela é registrada e o laço segue para a próxima. Um `monitor` em volta do laço inteiro abortaria tudo na primeira falha."},
  {"h3": "Registrar o resultado, não só o sucesso"},
  { code: `historico.append({"tarefa": t, "estado": ..., "detalhe": ...})`, lang: 'df' },
  {"p": "Guardar o histórico completo é o que torna o relatório possível. Sem ele, você saberia que \"algo falhou\", mas não o quê nem por quê."},
  {"h3": "Reenfileirar com prioridade máxima"},
  { code: `cycle h in falhadas:
    fila.push(h["tarefa"], 0)`, lang: 'df' },
  {"p": "Tarefas que falharam voltam com prioridade 0 — à frente de tudo. Numa fila real, isso precisaria de um contador de tentativas para não gerar um laço infinito com tarefas que sempre falham."},
  {"h3": "Histograma em texto"},
  { code: `out $"  {nome_estado.pad_end(12)} {"#".repeat(quantos)} ({quantos})"`, lang: 'df' },
  {"h3": "Saída esperada"},
  { code: `┌──────────────────┐
│ Fila de Trabalho │
└──────────────────┘
tarefas na fila: 6

── processando por prioridade ──
  [p1] ERR processar pagamento    gateway indisponivel
  [p1] ok  alerta de seguranca    alerta de seguranca concluida
  [p5] ok  enviar email           enviar email concluida
  [p7] ok  limpar cache           limpar cache concluida
  [p8] ok  gerar relatorio        gerar relatorio concluida
  [p9] ok  backup                 backup concluida

┌───────────┐
│ Relatorio │
└───────────┘
total:      6
concluidas: 5
falhadas:   1

ordem de execucao (prioridade): [1, 1, 5, 7, 8, 9]

── por estado ──
  Concluida    ##### (5)
  Falhou       # (1)

── reenfileirando falhas ──
  processar pagamento volta com prioridade maxima`, lang: 'text' },
  {"h3": "Experimente"},
  {"list": ["Acrescente um contador de tentativas e descarte após 3 falhas.", "Use `thread` + `channel` para processar várias tarefas em paralelo.", "Persista o histórico com `Arcane.Database`."]},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/19-concorrencia/170_async_await.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '170-acoes-assincronas', text: "170 · Acoes assincronas", level: 2 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'para-que-serve', text: "Para que serve", level: 3 as const }, { id: 'o-que-acelera-e-o-que-nao', text: "O que acelera e o que não", level: 3 as const }, { id: 'a-tarefa-nao-e-o-valor', text: "A tarefa não é o valor", level: 3 as const }, { id: 'compor', text: "Compor", level: 3 as const }, { id: 'erros', text: "Erros", level: 3 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '171-threads-e-paralelismo', text: "171 · Threads e paralelismo", level: 2 as const }, { id: 'thread', text: "`thread`", level: 3 as const }, { id: 'parallel', text: "`parallel`", level: 3 as const }, { id: 'a-condicao-de-corrida', text: "A condição de corrida", level: 3 as const }, { id: 'como-evitar', text: "Como evitar", level: 3 as const }, { id: 'regra-pratica', text: "Regra prática", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '172-canais-entre-threads', text: "172 · Canais entre threads", level: 2 as const }, { id: 'o-que-e-um-canal', text: "O que é um canal", level: 3 as const }, { id: 'o-padrao-que-resolve-a-corrida', text: "O padrão que resolve a corrida", level: 3 as const }, { id: 'recolher-tudo', text: "Recolher tudo", level: 3 as const }, { id: 'fila-de-trabalho', text: "Fila de trabalho", level: 3 as const }, { id: 'perguntar-ou-esperar', text: "Perguntar ou esperar", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '173-liberacao-garantida', text: "173 · Liberacao garantida", level: 2 as const }, { id: 'o-problema', text: "O problema", level: 3 as const }, { id: 'defer', text: "`defer`", level: 3 as const }, { id: 'declare-junto-de-quem-adquire', text: "Declare junto de quem adquire", level: 3 as const }, { id: 'lifo-o-ultimo-declarado-roda-primeiro', text: "LIFO: o último declarado roda primeiro", level: 3 as const }, { id: 'em-cadeia', text: "Em cadeia", level: 3 as const }, { id: 'defer-ou-ensure', text: "`defer` ou `ensure`?", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '174-erros-e-retentativas', text: "174 · Erros e retentativas", level: 2 as const }, { id: 'retry', text: "`retry`", level: 3 as const }, { id: 'nem-todo-erro-merece-retry', text: "Nem todo erro merece retry", level: 3 as const }, { id: 'espera-crescente', text: "Espera crescente", level: 3 as const }, { id: 'registrar-e-repassar', text: "Registrar e repassar", level: 3 as const }, { id: 'regra-de-ouro', text: "Regra de ouro", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }, { id: '175-projeto-fila-de-trabalho', text: "175 · Projeto: fila de trabalho", level: 2 as const }, { id: 'a-arquitetura', text: "A arquitetura", level: 3 as const }, { id: 'fila-de-prioridade', text: "Fila de prioridade", level: 3 as const }, { id: 'estado-como-enum', text: "Estado como enum", level: 3 as const }, { id: 'retentativa-por-tarefa', text: "Retentativa por tarefa", level: 3 as const }, { id: 'registrar-o-resultado-nao-so-o-sucesso', text: "Registrar o resultado, não só o sucesso", level: 3 as const }, { id: 'reenfileirar-com-prioridade-maxima', text: "Reenfileirar com prioridade máxima", level: 3 as const }, { id: 'histograma-em-texto', text: "Histograma em texto", level: 3 as const }, { id: 'saida-esperada', text: "Saída esperada", level: 3 as const }, { id: 'experimente', text: "Experimente", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"19 · Concorrência"}
      description={"6 exercícios: threads, canais, tarefas e paralelismo."}
      href={"/docs/exercicios/19-concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
