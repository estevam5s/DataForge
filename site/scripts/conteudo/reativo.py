# -*- coding: utf-8 -*-
"""Arcane.Reativo — valores que avisam quando mudam."""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo",
"title": "Programação reativa",
"description": "Sinal, derivado e efeito: um valor que outros valores acompanham — com as dependências descobertas na execução.",
"blocos": [
 {"p": "A linguagem já tinha três formas de lidar com mudança, e nenhuma resolvia o mesmo problema: `Arcane.Eventos` é um emissor, `Arcane.Stream` são tópicos com offset (Kafka, e não RxJS), e `stream action` é um gerador preguiçoso. O que faltava é a quarta — um **valor** que outros valores acompanham."},
 {"p": "É a diferença entre *\"me avise quando algo acontecer\"* e *\"este total é sempre a soma daqueles três\"*."},
 {"code": """adopt Arcane.Reativo as R

preco := R.sinal(10.0)
quantidade := R.sinal(3)
total := R.derivado(lambda => preco.ler() * quantidade.ler())

out total.ler()          // 30.0
quantidade.escrever(5)
out total.ler()          // 50.0 — ninguem recalculou a mao""", "lang": "df"},

 {"h2": "Sinal é valor; observável é fluxo"},
 {"p": "**Sinal** tem um estado agora, e quem pergunta recebe o valor de agora. **Observável** não tem estado: quem se inscreve recebe o que vier daqui para a frente. Um clique é um fluxo; um saldo é um valor."},
 {"callout": {"tipo": "nota", "titulo": "Por que a distinção é mantida",
              "texto": "Frameworks reativos costumam ter os dois e chamar os dois de \"stream\" — e aí a pergunta \"qual é o valor atual?\" passa a não ter resposta."}},

 {"h2": "As peças"},
 {"table": {"head": ["", "O que é"], "rows": [
   ["`R.sinal(v)`", "um valor com estado: `ler`, `escrever`, `atualizar`, `observar`"],
   ["`R.derivado(f)`", "calculado de outros — preguiçoso e memorizado"],
   ["`R.efeito(f)`", "o que acontece quando muda; roda uma vez ao nascer"],
   ["`R.lote(f)`", "várias escritas, uma notificação"],
   ["`R.observavel()`", "um fluxo no tempo, com `morph`, `sift`, `distill`…"],
   ["`R.de_cluster` · `R.intervalo`", "fontes frias: só começam quando alguém escuta"],
   ["`R.juntar` · `R.combinar`", "dois fluxos num só"]]}},

 {"h2": "Onde continuar"},
 {"cards": [
   {"href": "/docs/reativo/sinais", "title": "Sinais e derivados", "desc": "A preguiça, a memória e as dependências descobertas."},
   {"href": "/docs/reativo/efeitos", "title": "Efeitos e propagação", "desc": "O losango, e por que a marcação vem antes do aviso."},
   {"href": "/docs/reativo/observaveis", "title": "Observáveis", "desc": "Fluxos, operadores e a fonte fria."}]},
 {"h2": "Mais sobre reatividade"},
 {"p": "Desfazer e refazer, dados que chegam depois, operadores de fluxo, lote, formulários, vazamentos e testes."},
 {"cards": [{"href": "/docs/reativo/historico", "title": "Desfazer e refazer", "desc": "Um histórico que acompanha o sinal sem que quem escreve saiba — e o lote que vira um passo só."}, {"href": "/docs/reativo/recursos", "title": "Dados que chegam depois", "desc": "R.recurso: carregando, pronto ou erro — e a resposta velha que chega por último e não pode vencer."}, {"href": "/docs/reativo/operadores", "title": "Operadores de fluxo", "desc": "morph, sift, distill, distintos, primeiros, pular, blocos, esperar e limitar — e quando cada um cabe."}, {"href": "/docs/reativo/lote", "title": "Escrever em lote", "desc": "Três escritas, uma notificação: o estado intermediário que ninguém deveria ver."}, {"href": "/docs/reativo/formularios", "title": "Um formulário reativo", "desc": "Cada campo um sinal, cada erro um derivado, e o botão que só habilita quando tudo está certo."}, {"href": "/docs/reativo/vazamentos", "title": "Parar o que não se usa", "desc": "Efeito, inscrição, histórico e recurso seguram referências: sem parar, a tela fechada continua reagindo."}, {"href": "/docs/reativo/testes", "title": "Testar código reativo", "desc": "Escrever, ler, contar execuções — e aguardar o recurso sem sleep arbitrário."}, {"href": "/docs/reativo/estado-da-aplicacao", "title": "O estado de uma aplicação", "desc": "Sinais para o que se escreve, derivados para o que se calcula, comandos para o que muda — e nada mais."}]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/sinais",
"title": "Sinais e derivados",
"description": "Preguiçoso, memorizado, e com as dependências descobertas executando a fórmula.",
"blocos": [
 {"h2": "O derivado é preguiçoso e memorizado"},
 {"p": "Ele só recalcula quando **alguém lê** e alguma dependência mudou. Recalcular na escrita faria uma cadeia de dez derivados rodar dez vezes por mudança — e a maioria deles nunca é lida."},
 {"code": """contas := {"n": 0}

action calcular():
    contas["n"] := contas["n"] + 1
    yield itens.ler()

steady quantos := R.derivado(calcular)

quantos.ler()
quantos.ler()
quantos.ler()
assert contas["n"] is 1      // tres leituras, uma conta so""", "lang": "df"},

 {"h2": "As dependências são descobertas, não declaradas"},
 {"p": "Não há lista para escrever: o derivado roda, e **todo sinal lido durante a execução** entra. Uma lista escrita à mão envelhece na primeira condição nova dentro da fórmula, e o sintoma é um valor que para de atualizar."},
 {"code": """action calcular_frete():
    given subtotal.ler() bigger 100.0:
        yield 0.0
    yield 20.0 - cupom.ler()

steady frete := R.derivado(calcular_frete)""", "lang": "df"},
 {"p": "Abaixo de 100 o frete **leu** o cupom, e mexer no cupom o invalida. Acima de 100 a fórmula toma o outro ramo e não lê mais: a partir daí, mexer no cupom não mexe em nada. As fontes que sumiram param de notificar — sem isso, uma fórmula com `given` acumularia as dependências dos dois ramos e recalcularia por mudanças que ela nem lê mais."},

 {"h2": "Escrever o mesmo valor não notifica"},
 {"p": "Um sinal que avisa sobre `x := x` faz uma cadeia recalcular por nada e um efeito de rede disparar duas vezes. A comparação pode ser trocada: `R.sinal(v, iguais := minha_comparacao)`."},

 {"h2": "Ler sem depender"},
 {"p": "`.valor()` devolve o valor **sem** registrar a dependência — o `untracked` dos outros frameworks. Sem ele, um derivado que lê um contador de depuração passaria a recalcular a cada incremento dele."},

 {"h2": "Um ciclo é recusado, com o caminho"},
 {"code": """// erro: o derivado 'a' depende de si mesmo.
//   nota: a cadeia: a → b → a
//   dica: quebre o ciclo: um dos dois precisa ser um sinal""", "lang": "text"},
 {"p": "Dizer apenas \"há um ciclo\" manda procurar em toda a fórmula; a cadeia é o que o torna quebrável."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/efeitos",
"title": "Efeitos e propagação",
"description": "O efeito que roda ao nascer, o lote, e o losango que entregava um valor que nunca existiu.",
"blocos": [
 {"h2": "O efeito roda uma vez ao ser criado"},
 {"code": """action mostrar():
    linhas.append($"total R$ {total.ler()}")

steady vigia := R.efeito(mostrar)   // ja rodou uma vez

itens.escrever([...])               // roda de novo
vigia.parar()                       // e para de rodar""", "lang": "df"},
 {"p": "Sem isso, quem escreve `R.efeito(…)` vê a tela vazia até a primeira mudança — e conclui que o efeito não funciona. A alternativa seria chamá-lo à mão depois de criar, o que se esquece exatamente uma vez."},

 {"h2": "A propagação tem duas fases"},
 {"p": "Esta é a decisão que mais importa do módulo, e ela veio de um defeito medido. Num **losango** — `c` lê `a` e `b`, e `b` lê `a` — marcar e avisar numa fase só entrega um valor que nunca existiu."},
 {"code": """a := R.sinal(1)
b := R.derivado(lambda => a.ler() * 2)
c := R.derivado(lambda => a.ler() + b.ler())

R.efeito(lambda => vistos.append(c.ler()))
a.escrever(5)

// antes:  [3, 7, 15]     <- o 7 nunca foi verdade
// agora:  [3, 15]""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Não é uma notificação a mais — é um número errado",
              "texto": "Com `a = 5`, o valor certo é 15. O 7 era `5 + o b antigo`: `b` ainda estava limpo quando `c` recalculou. E como a lista de dependentes é um conjunto, qual caminho vem primeiro não é escolhido por ninguém — o defeito ia e vinha conforme a ordem de hash, aparecendo e sumindo sozinho na tela."}},
 {"p": "Hoje a marcação percorre o grafo **inteiro** primeiro, e só depois os efeitos e ouvintes rodam. Daí saem três regras:"},
 {"table": {"head": ["Regra", "Sem ela"], "rows": [
   ["o aviso pertence à propagação, e não ao recálculo", "uma simples **leitura** disparava efeito de terceiros"],
   ["o efeito alcançado por dois caminhos roda **uma** vez", "a tela redesenhava duas vezes por mudança"],
   ["a dedup é pelo objeto, e não por `id()`", "`id()` só é único entre objetos **vivos**"],
   ["uma escrita dentro de um efeito abre a **próxima** onda", "a fila cresceria enquanto é percorrida"]]}},

 {"h2": "Lote"},
 {"code": """action tres_escritas():
    itens.escrever([...])
    cupom.escrever(0.0)
    itens.escrever([...])

R.lote(tres_escritas)      // UMA notificacao""", "lang": "df"},
 {"p": "Sem ele, mudar três sinais que alimentam o mesmo derivado faz o efeito rodar três vezes — e as duas primeiras mostram um estado intermediário que nunca deveria aparecer na tela."},
 {"callout": {"tipo": "nota", "titulo": "Ele já existiu sem agrupar nada",
              "texto": "A primeira versão montava uma lista de adiados que **ninguém lia**: o gancho era escrito e nenhum caminho de escrita o consultava. `lote` tinha documentação e tinha teste de que não estourava — e três escritas davam três notificações, exatamente como sem ele. É a mesma forma do `forge.lock` que era escrito e nunca lido."}},
 {"p": "Se a ação falhar no meio, os avisos **saem mesmo assim**: a escrita já aconteceu, e engolir a notificação deixaria a tela mostrando um estado que não é mais o do programa."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/observaveis",
"title": "Observáveis",
"description": "O fluxo no tempo, os operadores, e por que a fonte fria liga preguiçoso.",
"blocos": [
 {"p": "Um observável não tem estado: quem se inscreve recebe o que vier daqui para a frente."},
 {"code": """cliques := R.observavel("cliques")

compras := cliques.sift(lambda v => v["botao"] is "comprar")
produtos := compras.morph(lambda v => v["produto"])
inscricao := produtos.distintos().inscrever(lambda p => vistos.append(p))

cliques.emitir({"botao": "ver", "produto": "cafe"})
cliques.emitir({"botao": "comprar", "produto": "cafe"})

inscricao.cancelar()""", "lang": "df"},

 {"h2": "Os operadores"},
 {"table": {"head": ["", "O que faz"], "rows": [
   ["`morph` · `sift` · `distill`", "os mesmos nomes do pipeline `>>` da linguagem"],
   ["`distintos(chave)`", "só emite quando muda"],
   ["`primeiros(n)` · `pular(n)`", "recorta o começo do fluxo"],
   ["`blocos(n)`", "junta em grupos de `n`"],
   ["`esperar(s)` · `limitar(s)`", "*debounce* e *throttle*"],
   ["`ao_falhar(f)`", "o erro como valor, e não como interrupção"],
   ["`para_sinal(inicial)`", "transforma o fluxo em valor"]]}},

 {"h2": "A fonte fria liga preguiçoso"},
 {"p": "`R.de_cluster` e `R.intervalo` são **frias**: só começam quando alguém escuta. O operador só se conecta à sua fonte ao receber o primeiro inscrito — e isso não é uma otimização."},
 {"code": """pares := R.de_cluster([1, 2, 3, 4]).sift(lambda n => n % 2 is 0)
pares.morph(lambda n => n * 10).inscrever(lambda n => vistos.append(n))
assert vistos is [20, 40]""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Ligando na construção, o resultado era uma lista vazia",
              "texto": "A fonte despejava os quatro valores no momento em que `sift` se inscrevia nela — antes de `morph` e do assinante final existirem. Sem erro nenhum: só uma lista vazia, que é o pior desfecho possível."}},

 {"h2": "Juntar e combinar"},
 {"p": "`R.juntar(a, b)` intercala os dois fluxos. `R.combinar(a, b)` emite uma tupla com o **último de cada** sempre que qualquer um emite — e só depois que todos já emitiram ao menos uma vez, porque antes disso não há \"último\" para um deles."},

 {"h2": "O exemplo completo"},
 {"p": "`examples/reativo_carrinho.df` percorre sinal, derivado, efeito, lote e observável num carrinho de compras, com `assert` em cada afirmação — inclusive as contagens que **provam** a preguiça."},
]},
]
