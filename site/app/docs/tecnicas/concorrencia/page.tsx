import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Concorrência",
  description: "async/await, threads, canais, travas — e os processos, que são o único caminho para mais de um núcleo.",
};

const blocos: Bloco[] = [
  {"h2": "async / await"},
  {"p": "Uma ação marcada com `async` **começa a rodar assim que é chamada**, numa thread própria. A chamada não devolve o resultado — devolve a *tarefa*. `await` espera ela terminar e entrega o valor."},
  { code: `async action buscar_usuario(id):
    yield {"id": id, "nome": $"Usuario {id}"}

usuario := await buscar_usuario(7)
out usuario` },
  {"h3": "Onde está o ganho"},
  {"p": "Escrito assim, uma de cada vez, `async` não adianta nada. O ganho aparece quando você chama **todas antes de aguardar qualquer uma**:"},
  { code: `adopt Arcane.Time as T

async action baixar(endereco):
    T.sleep(0.2)          // uma requisicao de rede, na vida real
    yield endereco.upper()

// as seis comecam aqui, juntas
tarefas := [baixar(e) cycle e in ["a", "b", "c", "d", "e", "f"]]

// e aqui so se espera a mais lenta
paginas := await tarefas` },
  {"table": {"head": ["Como está escrito", "Seis esperas de 200 ms custam"], "rows": [
    ["`tarefas := [baixar(e) …]` e depois `await tarefas`", "**0,2 s** — todas se sobrepõem"],
    ["`cycle e in …:` com `await baixar(e)` dentro", "**1,2 s** — cada uma espera a anterior"]]}},
  {"h3": "O que async acelera, e o que não acelera"},
  {"p": "As tarefas são threads do Python. Elas se sobrepõem enquanto uma está **esperando algo de fora** — rede, disco, banco de dados, `sleep`. Para contas, não: o GIL deixa uma thread por vez executar código, e vinte tarefas somando números levam o mesmo tempo que uma."},
  {"callout": {"tipo": "dica", "texto": "Trabalho de **entrada e saída** → `async`. Trabalho de **CPU** → [`Arcane.Concurrent`](/docs/biblioteca), que usa processos e escapa do GIL."}},
  {"h3": "Erros atravessam o await"},
  {"p": "O `trigger` que aconteceu na outra thread é relevantado na linha do `await` — que é onde quem escreveu pode fazer algo a respeito."},
  { code: `async action pode_falhar(deve):
    given deve:
        trigger "a busca falhou"
    yield "ok"

monitor:
    await pode_falhar(yes)
handle e:
    out e.message          // a busca falhou` },
  {"callout": {"tipo": "atencao", "titulo": "Usar o resultado sem await", "texto": "É o engano mais comum de quem escreve código assíncrono, em qualquer linguagem. `buscar_usuario(1)[\"nome\"]` não funciona: `buscar_usuario(1)` é a tarefa, não o vault. A linguagem diz exatamente isso quando acontece, com a linha e a correção."}},
  {"h2": "thread"},
  { code: `resultados := []

thread:
    cycle i from 1 to 3:
        resultados.append($"A{i}")

wait 200        # espera as threads
out len(resultados)` },
  {"p": "O bloco roda numa thread daemon: o programa **não espera** por ela. Se terminar antes, a thread é interrompida no meio."},
  {"h2": "A condição de corrida"},
  {"p": "Este é o ponto mais importante desta página:"},
  { code: `contador := {"valor": 0}

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

thread:
    cycle _ in range(0, 1000):
        contador["valor"] := contador["valor"] + 1

wait 400
out contador["valor"]     # deveria ser 2000. Frequentemente é menos.` },
  {"p": "`contador[\"valor\"] + 1` são três passos — ler, somar, escrever. Se as duas threads leem 5 ao mesmo tempo, ambas escrevem 6. Um incremento se perdeu."},
  {"p": "Rode várias vezes: o número muda. É o tipo de bug que passa em teste e quebra em produção sob carga."},
  {"h2": "channel — a via segura"},
  {"p": "Há duas saídas, e a ordem importa: a primeira é **não compartilhar**. `Arcane.Concurrent` tem `mutex`, `semaforo`, `barreira`, `contador` e canal bloqueante — mas uma trava protege o acesso e não o desenho, e um programa em que cada thread trabalha no próprio escopo não precisa de nenhuma delas."},
  { code: `channel parciais

thread:
    soma := 0                  # variável local desta thread
    cycle _ in range(0, 1000):
        soma += 1
    parciais.send(soma)        # reporta uma vez, no fim

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

out total     # 2000, sempre` },
  {"p": "Cada thread trabalha no próprio escopo. Ninguém escreve onde outro lê. Essa ideia tem nome — *\"não comunique compartilhando memória; compartilhe memória comunicando\"* — e é o lema de Go."},
  {"h2": "Quando compartilhar é inevitável"},
  {"p": "Nem todo acumulador cabe num canal. Para esses, `Arcane.Concurrent` tem as travas — e `com_trava` solta a trava **mesmo quando o corpo estoura**, que é a diferença entre um erro e um programa parado para sempre."},
  { code: `adopt Arcane.Concurrent as P

trava := P.mutex()
total := {"valor": 0}

action somar(n):
    yield P.com_trava(trava, lambda => total.set("valor", total["valor"] + n))

P.map(somar, range(1, 1001))
out total["valor"]          // 500500, sempre` },
  {"p": "Para o caso mais comum — somar — há `contador`, que não precisa de trava nenhuma escrita à mão:"},
  { code: `adopt Arcane.Concurrent as P

visitas := P.contador()

action registrar(_):
    yield visitas.somar(1)

P.map(registrar, range(0, 10000))
out visitas.valor()         // 10000` },
  {"callout": {"tipo": "atencao", "titulo": "Nada disso é aplicado sozinho", "texto": "A linguagem não sincroniza por você. O `check` **avisa** (`escrita-concorrente`) quando um `thread`, um `parallel` ou uma `route` escreve num nome que vem de fora — e a rota é o caso que mais engana, porque ali a thread é invisível: o Kiln atende um pedido por thread. Medido: seis pedidos simultâneos numa rota que lê, espera e escreve entregaram **1 de 6**."}},
  {"h2": "Regra prática"},
  {"table": {"head": ["Situação", "Seguro?"], "rows": [["threads só leem dados compartilhados", "sim"], ["cada thread escreve numa variável própria", "sim"], ["threads enviam por `channel`", "sim"], ["duas threads escrevem na mesma variável", "**não**"], ["`lista.append` de duas threads", "**não**"]]}},
  {"h2": "parallel"},
  { code: `parallel:
    saidas.append(tarefa_a())
    saidas.append(tarefa_b())` },
  {"p": "**Cada instrução** do bloco vai para uma thread — não uma thread para o bloco inteiro. É uma limitação conhecida; enquanto isso, mantenha cada linha autossuficiente."},
  {"h2": "Vários núcleos, de verdade"},
  {"p": "Tudo acima acontece em **um núcleo**. `async`, `thread` e `parallel` usam threads do Python, e duas threads do Python nunca executam bytecode ao mesmo tempo — é o GIL. Para trabalho que **espera**, isso não importa: a thread solta o GIL enquanto espera, e dez downloads acontecem juntos. Para trabalho que **calcula**, oito threads levam o mesmo tempo que uma."},
  {"p": "O caminho para os outros núcleos é um só, e ele usa **processos**:"},
  { code: `adopt Arcane.Concurrent as P

action cpu(n):
    s := 0
    cycle i from 1 to n:
        s += i * i
    yield s

blocos := [200000, 200000, 200000, 200000, 200000, 200000, 200000, 200000]

out P.nucleos()                       // 10
out sum(P.map_processos(cpu, blocos)) // usa os 8` },
  {"p": "Medido nesta máquina de 10 núcleos, com os mesmos oito blocos:"},
  {"table": {"head": ["Como", "Tempo", "Ganho"], "rows": [
    ["em série", "1607 ms", "—"],
    ["`P.map` — threads", "1654 ms", "**0,97x**"],
    ["`P.map_processos` — processos", "466 ms", "**3,45x**"]]}},
  {"p": "As threads não só deixaram de ganhar: ficaram um pouco **mais lentas** que a série, pelo custo de trocar de contexto sem nada a ganhar em troca. Esse é o resultado esperado, e ele é a razão de `map_processos` existir."},
  {"h3": "O que atravessa para o outro processo"},
  {"p": "Um processo recebe o trabalho por **cópia**. O que viaja não é a ação — é a **declaração** dela, mais os nomes que ela lê e não cria, mais tudo o que esses nomes alcançam: outras ações, `record`, `enum`, `blueprint`, e os módulos, que o outro lado carrega de novo pelo nome."},
  { code: `adopt Arcane.Concurrent as P
adopt Arcane.Math as M

steady TAXA := 0.08

record Pedido:
    cliente: String
    valor: Float

action imposto(v):
    yield v * TAXA

action com_imposto(p):
    yield Pedido(p.cliente, M.round(p.valor + imposto(p.valor), 2))

pedidos := [Pedido("ana", 100.0), Pedido("bia", 250.0)]
out P.map_processos(com_imposto, pedidos)` },
  {"p": "A `steady`, o `record`, o módulo e a segunda ação atravessam junto, sem que nada disso precise ser dito. O `record` que volta é o **mesmo tipo** declarado aqui — `with` funciona sobre ele."},
  {"h3": "O que não atravessa"},
  {"p": "Uma conexão de banco, um arquivo aberto, um socket, um mutex, um canal e uma tarefa existem no processo que os abriu. Copiá-los não faria sentido: o outro lado ganharia um número de descritor que lá não aponta para nada."},
  { code: `adopt Arcane.Concurrent as P
adopt Arcane.Database as DB

// a conexao e aberta DENTRO da acao: cada processo abre a sua
action contar(arquivo):
    banco := DB.connect(arquivo)
    yield DB.count(banco, "pedidos")

out P.map_processos(contar, ["a.db", "b.db", "c.db"])` },
  {"p": "Quando um nome desses é mesmo usado lá dentro, a mensagem o chama pelo nome e diz o que ele guarda — não `cannot pickle`, e não o nome de um objeto interno da biblioteca:"},
  { lang: 'text', code: `erro[DF1001]: 'db' cannot cross into another process
  = nota: it holds a connection to a database, which exists only in
          the process that opened it
  = dica: open it INSIDE the action — each process opens its own — or
          use 'map', which uses threads and shares memory` },
  {"callout": {"tipo": "dica", "titulo": "Quando vale pagar a travessia", "texto": "Copiar os dados de ida e de volta custa. A conta vira a favor dos processos a partir de **alguns milissegundos de trabalho por item** — abaixo disso, `map` com threads é mais rápido mesmo em trabalho de CPU, porque não há fronteira a cruzar."}},
  {"h3": "Um pool que sobrevive entre chamadas"},
  {"p": "`map_processos` abre um pool, usa e fecha. Iniciar um processo custa **mais de cem milissegundos** — aceitável uma vez num script, inaceitável por pedido num servidor web. `P.pool_processos()` paga esse custo uma vez:"},
  { code: `adopt Arcane.Concurrent as P

pool := P.pool_processos()

// a primeira chamada paga a partida; a segunda nao
out pool.map(pesado, blocos)
out pool.map(pesado, outros)

// uma chamada so, disparada e esperada depois
tarefa := pool.enviar(pesado, bloco)
out tarefa.esperar()

pool.fechar()` },
  {"table": {"head": ["Chamada", "Tempo"], "rows": [
    ["a primeira — abre os processos", "180 ms"],
    ["a segunda — reaproveita", "**82 ms**"]]}},
  {"p": "`fechar()` é explícito de propósito. Os processos ficam vivos até ele — e um pool aberto por engano dentro de um laço deixaria a máquina cheia de processos ociosos. Depois de fechado, o pool recusa e diz por quê."},
  {"p": "Para uma chamada avulsa, sem pool, há `P.processo(acao, …)`: é o `thread` da linguagem, num núcleo de verdade. Ele abre e fecha um processo por chamada, então para várias seguidas o pool é o caminho."},
  {"h3": "O erro que acontece do outro lado"},
  {"p": "Ele volta como erro daqui, dizendo onde aconteceu. A pilha e a linha ficam no outro processo — nada disso sobrevive à cópia —, mas a mensagem e a dica chegam inteiras, inclusive o *did you mean*."},
  {"h2": "O que ainda não existe"},
  {"list": ["cancelamento de tarefa e `await` com prazo", "`parallel` tratando blocos em vez de instruções", "depurar uma thread sem parar as outras"]},
  {"p": "Tudo isso está no [roadmap](/docs/roadmap)."},
];

const headings = [{ id: 'async-await', text: "async / await", level: 2 as const }, { id: 'onde-esta-o-ganho', text: "Onde está o ganho", level: 3 as const }, { id: 'o-que-async-acelera-e-o-que-nao-acelera', text: "O que async acelera, e o que não acelera", level: 3 as const }, { id: 'erros-atravessam-o-await', text: "Erros atravessam o await", level: 3 as const }, { id: 'thread', text: "thread", level: 2 as const }, { id: 'a-condicao-de-corrida', text: "A condição de corrida", level: 2 as const }, { id: 'channel-a-via-segura', text: "channel — a via segura", level: 2 as const }, { id: 'quando-compartilhar-e-inevitavel', text: "Quando compartilhar é inevitável", level: 2 as const }, { id: 'regra-pratica', text: "Regra prática", level: 2 as const }, { id: 'parallel', text: "parallel", level: 2 as const }, { id: 'varios-nucleos-de-verdade', text: "Vários núcleos, de verdade", level: 2 as const }, { id: 'o-que-atravessa-para-o-outro-processo', text: "O que atravessa para o outro processo", level: 3 as const }, { id: 'o-que-nao-atravessa', text: "O que não atravessa", level: 3 as const }, { id: 'um-pool-que-sobrevive-entre-chamadas', text: "Um pool que sobrevive entre chamadas", level: 3 as const }, { id: 'o-erro-que-acontece-do-outro-lado', text: "O erro que acontece do outro lado", level: 3 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Concorrência"}
      description={"async/await, threads, canais, travas — e os processos, que são o único caminho para mais de um núcleo."}
      href={"/docs/tecnicas/concorrencia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
