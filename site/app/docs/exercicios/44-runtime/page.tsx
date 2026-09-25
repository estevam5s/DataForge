// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "44 · Runtime e laço de eventos",
  description: "1 exercício: laço de eventos, escalonador e fibras.",
};

const blocos: Bloco[] = [
  {"p": "Nível: **Por dentro da linguagem** · laço de eventos, escalonador e fibras · [todos os módulos](/docs/exercicios)"},
  { code: `python3 exercicios/run_all.py 44`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[262](#262-o-laco-de-eventos-o-escalonador-e-as-fibras)", "**o laco de eventos, o escalonador e as fibras**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "262 · o laco de eventos, o escalonador e as fibras"},
  { code: `// 'async/await' nesta linguagem e UMA THREAD POR TAREFA. Serve para
// sobrepor entrada e saida, e nao escala: mil conexoes sao mil threads
// do sistema. O outro modelo e o reator — uma thread dormindo no
// seletor do sistema — e e o que este exercicio exercita.
//
// Medido: 2000 conexoes atendidas por UMA thread, com +0 MB de memoria,
// contra 2000 threads e +36 MB.

adopt Arcane.Laco as L
adopt Arcane.Time as T

// ── o laco: fila de prontas e fila de prazos ──
laco := L.novo()
ordem := []

L.agendar(laco, lambda => ordem.append("agora"))
L.apos(laco, 40, lambda => ordem.append("tarde"))
L.apos(laco, 10, lambda => ordem.append("cedo"))
L.apos(laco, 25, lambda => ordem.append("meio"))
L.rodar(laco)

// quem foi agendado DEPOIS mas vence ANTES roda antes: a fila de
// prazos e um heap, nao uma lista percorrida
assert ordem is ["agora", "cedo", "meio", "tarde"]

// o poller e o do sistema: epoll no Linux, kqueue no macOS
assert L.mecanismo(laco) in ["epoll", "kqueue", "select", "poll"]

// ── ele NAO gira em vao ──
// E a diferenca entre um reator e uma espera ocupada. Com um unico
// temporizador, o numero de voltas tem de ser pequeno.
parado := L.novo()
L.apos(parado, 80, lambda => void)
L.rodar(parado)
assert L.estatisticas(parado)["voltas"] smaller 50

// ── cancelar uma tarefa ──
cancelavel := L.novo()
visto := []
t := L.apos(cancelavel, 10, lambda => visto.append("nao devia"))
L.cancelar(t)
L.apos(cancelavel, 30, lambda => visto.append("esta sim"))
L.rodar(cancelavel)
assert visto is ["esta sim"]
assert L.cancelada(t)

// ── contrapressao: a fila recusa em vez de crescer sem limite ──
// Sem teto, uma fonte mais rapida que o consumo troca "falha visivel"
// por "morte por memoria", que e muito pior de diagnosticar.
apertado := L.novo(2)
assert L.agendar(apertado, lambda => void)
assert L.agendar(apertado, lambda => void)
assert not L.agendar(apertado, lambda => void)
assert L.estatisticas(apertado)["recusadas"] is 1

// ── um erro num retorno de chamada nao derruba o laco ──
// Um reator que morre no primeiro erro derruba o servidor inteiro — e o
// erro costuma ser de UMA conexao.
resistente := L.novo()
seguiu := []
L.agendar(resistente, lambda => 1 / 0)  // df: permitir division-by-zero
L.agendar(resistente, lambda => seguiu.append("segui"))
L.rodar(resistente)

assert seguiu is ["segui"]
assert L.estatisticas(resistente)["erros"] is 1
assert L.falhas(resistente)[0]["tipo"] is "DivisionByZeroError"

// ── o que bloqueia vai para o pool, e o laco continua girando ──
comPool := L.novo()
marcas := []

action pesado():
    T.sleep(0.05)
    yield "pronto"

L.executar(comPool, pesado, lambda r => marcas.append(r))
L.apos(comPool, 10, lambda => marcas.append("tique"))
L.rodar(comPool)

// o tique rodou ENQUANTO o trabalho pesado corria
assert marcas is ["tique", "pronto"]

// ── FIBRAS: um 'stream action' suspenso em cada 'emit' ──
// Nao e aproximacao: o corpo de um stream ja e um gerador que o
// interpretador suspende, e a troca de contexto e o quadro dele.

stream action trabalhador(nome, diario):
    cycle i from 1 to 3:
        diario.append($"{nome}{i}")
        emit L.ceder()

comFibras := L.novo()
diario := []
L.fibra(comFibras, trabalhador, ["A", diario])
L.fibra(comFibras, trabalhador, ["B", diario])

assert L.fibras(comFibras) is 2
L.rodar(comFibras)

// INTERCALADAS. Se fossem sequenciais seria A1 A2 A3 B1 B2 B3 — e e
// isto que prova que o escalonamento e cooperativo.
assert diario is ["A1", "B1", "A2", "B2", "A3", "B3"]
assert L.fibras(comFibras) is 0

// ── uma fibra que dorme deixa a outra andar ──
misto := L.novo()
registro := []

stream action lenta(r):
    r.append("lenta comecou")
    emit L.dormir(60)
    r.append("lenta terminou")

stream action rapida(r):
    cycle i from 1 to 3:
        r.append($"rapida {i}")
        emit L.dormir(5)

L.fibra(misto, lenta, [registro])
L.fibra(misto, rapida, [registro])
L.rodar(misto)

assert registro[0] is "lenta comecou"
assert registro[len(registro) - 1] is "lenta terminou"
assert "rapida 3" in registro

// ── a caixa: como uma fibra RECEBE algo ──
// 'emit' e INSTRUCAO, nao expressao: ele nao devolve valor. O laco
// entrega por um vault que a fibra passou. Explicito e melhor que
// fingir que 'emit' e uma expressao.
stream action espera(caixa):
    emit L.depois_de(20, caixa, "resposta", "chegou")
    caixa["visto"] := caixa["resposta"]

comCaixa := L.novo()
caixa := {"resposta": void, "visto": void}
L.fibra(comCaixa, espera, [caixa])
L.rodar(comCaixa)
assert caixa["visto"] is "chegou"

// ── cancelar uma fibra ──
// Uma thread do sistema nao se cancela assim: e a vantagem concreta de
// a fibra ser um objeto, e nao um recurso do SO.
comCancelamento := L.novo()
curto := []

stream action longa(r):
    r.append("comecei")
    emit L.dormir(50)
    r.append("nao chega aqui")

f := L.fibra(comCancelamento, longa, [curto])
L.apos(comCancelamento, 5, lambda => L.cancelar(f))
L.rodar(comCancelamento)

assert curto is ["comecei"]
assert L.cancelada(f)

// ── um erro dentro de uma fibra nao leva as outras ──
comErro := L.novo()
outras := []

stream action quebra():
    emit L.ceder()
    _x := 1 / 0  // df: permitir division-by-zero

stream action segue(r):
    emit L.ceder()
    r.append("a outra seguiu")

L.fibra(comErro, quebra, [])
L.fibra(comErro, segue, [outras])
L.rodar(comErro)

assert outras is ["a outra seguiu"]
assert len(L.falhas(comErro)) is 1

// ── o que uma fibra pode esperar e uma lista FECHADA ──
// Um vault qualquer emitido por engano viraria uma fibra parada para
// sempre, esperando algo que ninguem registrou.
assert "ceder" in L.pedidos()
assert "dormir" in L.pedidos()
assert "ler" in L.pedidos()

// ── uma fibra so nasce de 'stream action' ──
// Uma acao comum roda ate o fim e nunca para: nao ha onde suspender.
action comum():
    yield 1

monitor:
    L.fibra(L.novo(), comum, [])
    assert no
handle RuntimeError as e:
    assert "stream action" in e.message

out "262 ok"`, lang: 'df', title: `exercicios/44-runtime/262_laco_e_fibras.df` },
  {"p": "`async/await` nesta linguagem é **uma thread por tarefa**. Serve para o que foi feito — sobrepor entrada e saída — e não escala: mil conexões simultâneas são mil threads do sistema, e a conta aparece na memória e no escalonador do SO antes de aparecer no programa. O Kiln atende **um pedido por thread** pelo mesmo motivo."},
  {"p": "O outro modelo é o **reator**: uma thread que dorme num seletor do sistema — `epoll` no Linux, `kqueue` no macOS e no BSD, `select` no Windows — e acorda quando algum descritor tem trabalho."},
  {"h3": "O número"},
  {"p": "Um servidor de linha, uma requisição por conexão, medido contra o mesmo servidor com uma thread por conexão:"},
  {"table": {"head": ["Conexões", "Laço de eventos", "Thread por conexão"], "rows": [["400", "33 ms · **1 thread** · +0 MB", "43 ms · 400 threads · +14 MB"], ["1000", "73 ms · **1 thread** · +1 MB", "83 ms · 1000 threads · +36 MB"], ["2000", "151 ms · **1 thread** · +0 MB", "161 ms · 2000 threads · +36 MB"]]}},
  {"p": "**O tempo quase empata, e a memória é que conta a história.** Nesta máquina duas mil threads ainda funcionam, e a diferença de tempo fica em ~1,1×. O que muda é a **forma da conta**: o custo do laço é plano, o do modelo de threads é linear (~36 KB por thread). Num contêiner com limite de threads, ou com trabalho de verdade por conexão, um falha onde o outro nem percebe."},
  {"p": "Publicar o 1,1× é mais honesto que publicar só o caso em que o outro modelo já quebrou."},
  {"h3": "Ele não gira em vão"},
  {"p": "É a diferença entre um reator e uma espera ocupada, e é **testada**: com um único temporizador, o número de voltas tem de ser pequeno. Um laço de espera ocupada daria milhões e queimaria um núcleo sem fazer nada."},
  {"h3": "As três filas"},
  {"table": {"head": ["Fila", "O que resolve"], "rows": [["**poller** (`selectors`)", "dormir até haver E/S, em vez de girar"], ["**prazos** (heap)", "`apos` e `a_cada` sem uma thread por relógio"], ["**prontas**", "a ordem de execução, e onde a contrapressão mora"]]}},
  {"p": "E uma quarta que quase sempre falta num reator escrito à mão: o **executor**. Um trabalho que bloqueia dentro do laço trava tudo — não só aquela tarefa, mas toda conexão aberta. `L.executar` manda para um pool e devolve o resultado pela fila, que é a única forma de o laço continuar girando."},
  {"p": "Para isso funcionar, `agendar` chamado de outra thread precisa **acordar o laço**. É o truque clássico do autocano (*socketpair*): um seletor acorda por **descritor**, e uma fila em memória não é um descritor."},
  {"h3": "Contrapressão, e o erro que não derruba"},
  {"p": "Uma fila sem teto troca **falha visível** por **morte por memória** — que é muito pior de diagnosticar, porque acontece longe da causa. Com teto, `agendar` devolve `no` e quem chama decide."},
  {"p": "E um reator que morre no primeiro erro derruba o servidor inteiro, sendo que o erro costuma ser de **uma** conexão. Aqui ele é contado, guardado com o tipo e o texto, e o laço segue."},
  {"h3": "Fibras — e elas são reais"},
  {"p": "Um `stream action` da linguagem **já é** um gerador do Python, e o interpretador suspende o corpo dele em cada `emit`. O escalonador dirige esse gerador: o valor emitido diz **o que a fibra está esperando**, e a troca de contexto é o quadro do gerador."},
  {"p": "Duas fibras cedendo o controle produzem `A1 B1 A2 B2 A3 B3`. Se fossem sequenciais seria `A1 A2 A3 B1 B2 B3` — é isso que prova o escalonamento cooperativo."},
  {"p": "`emit` é **instrução**, não expressão: não devolve valor para a fibra. O laço entrega por um vault que ela passou — a **caixa**. Ser explícito aqui é melhor que fingir o contrário."},
  {"p": "E cancelar uma fibra fecha o gerador, o que roda os `defer` do corpo. Uma thread do sistema não se cancela assim: é a vantagem concreta de a fibra ser um objeto, e não um recurso do SO."},
  {"h3": "Sem pilha — e isso tem nome"},
  {"p": "**Um `emit` dentro de uma ação chamada NÃO suspende a fibra.** Só o `emit` do corpo da própria fibra suspende."},
  {"p": "É a limitação de toda corrotina **sem pilha** (*stackless*) — a mesma dos iteradores do C# e do `yield` do Python. Suspender dentro de uma chamada exige pilha própria, e isso quer dizer troca de contexto em assembly ou uma extensão em C: as duas fora de uma linguagem sem dependência externa."},
  {"p": "É por isso que a documentação diz **fibra** e não *green thread*."},
  {"h3": "O que NÃO existe"},
  {"list": ["**work stealing** entre laços: cada laço é uma thread, e com o GIL o"]},
  {"p": "ganho some antes de aparecer."},
  {"list": ["**`io_uring`**: só Linux, e pelo CPython exigiria extensão em C.", "**IOCP no Windows**: ali o `selectors` usa `select`, com teto de 512"]},
  {"p": "descritores. É o limite desta forma, e está dito em vez de escondido."},
  {"list": ["**prioridade por tarefa**: a fila é FIFO. Prioridade sem inversão de"]},
  {"p": "prioridade é mais difícil do que parece."},
  {"list": ["**mais de um núcleo**: o laço é uma thread só, e o GIL continua no"]},
  {"p": "caminho. Para CPU, `P.map_processos`."},
  {"h3": "Quando usar qual"},
  {"table": {"head": ["Precisa de", "Use"], "rows": [["sobrepor duas ou três chamadas de rede", "`async`/`await` — mais simples, e o custo não aparece"], ["milhares de conexões abertas ao mesmo tempo", "**este módulo**"], ["usar mais de um núcleo", "`P.map_processos`"], ["servir HTTP com rota e template", "Kiln — thread por pedido, e para a maioria isso basta"]]}},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/44-runtime/262_laco_e_fibras.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '262-o-laco-de-eventos-o-escalonador-e-as-fibras', text: "262 · o laco de eventos, o escalonador e as fibras", level: 2 as const }, { id: 'o-numero', text: "O número", level: 3 as const }, { id: 'ele-nao-gira-em-vao', text: "Ele não gira em vão", level: 3 as const }, { id: 'as-tres-filas', text: "As três filas", level: 3 as const }, { id: 'contrapressao-e-o-erro-que-nao-derruba', text: "Contrapressão, e o erro que não derruba", level: 3 as const }, { id: 'fibras-e-elas-sao-reais', text: "Fibras — e elas são reais", level: 3 as const }, { id: 'sem-pilha-e-isso-tem-nome', text: "Sem pilha — e isso tem nome", level: 3 as const }, { id: 'o-que-nao-existe', text: "O que NÃO existe", level: 3 as const }, { id: 'quando-usar-qual', text: "Quando usar qual", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"44 · Runtime e laço de eventos"}
      description={"1 exercício: laço de eventos, escalonador e fibras."}
      href={"/docs/exercicios/44-runtime"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
