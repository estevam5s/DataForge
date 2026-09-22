# -*- coding: utf-8 -*-
"""Reativo — oito páginas: desfazer, recurso assíncrono, operadores,
lote, formulário, vazamento, testes e o estado de uma aplicação.

`R.historico` e `R.recurso` entraram nesta leva. Todo bloco roda.
`sleep` recebe milissegundos.
"""

PAGINAS = [
# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/historico",
"title": "Desfazer e refazer",
"description": "Um histórico que acompanha o sinal sem que quem escreve saiba — e o lote que vira um passo só.",
"blocos": [
 {"p": "Desfazer costuma ser escrito como uma pilha de comandos inversos, e cada comando novo precisa lembrar de empilhar o seu. `R.historico` inverte isso: ele **observa** o sinal e anota cada valor anterior. Quem escreve no sinal não sabe que existe desfazer — e por isso não tem como esquecer dele."},
 {"code": '''adopt Arcane.Reativo as R

texto := R.sinal("")
h := R.historico(texto)

texto.escrever("O")
texto.escrever("Ol")
texto.escrever("Olá")

h.desfazer()
assert texto.ler() is "Ol"
h.desfazer()
assert texto.ler() is "O"
h.refazer()
assert texto.ler() is "Ol"
assert h.passos() is {"desfazer": 2, "refazer": 1}

texto.escrever("Oi")                 // escrever algo novo...
assert not h.pode_refazer()          // ...apaga o que dava para refazer''', "lang": "df"},
 {"h2": "Um lote é um passo"},
 {"p": "Colar um parágrafo escreve várias vezes; desfazer a colagem deveria voltar **tudo**. Dentro de `R.lote`, as escritas viram uma notificação só — e o histórico anota um passo só:"},
 {"code": '''adopt Arcane.Reativo as R

doc := R.sinal("")
h := R.historico(doc)

action colar():
    doc.escrever("Primeira linha")
    doc.escrever("Primeira linha\\nSegunda linha")

R.lote(colar)
assert h.passos()["desfazer"] is 1
h.desfazer()
assert doc.ler() is ""''', "lang": "df"},
 {"list": [
   "**Limite**: `R.historico(sinal, 100)` guarda até 100 passos e descarta o mais velho — sem teto, editar por horas vira memória.",
   "**Só de sinal**: um derivado não se escreve, e \"desfazer\" nele seria desfazer nas fontes — recusado na criação.",
   "**`h.parar()`** desliga o histórico quando a tela fecha."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/recursos",
"title": "Dados que chegam depois",
"description": "R.recurso: carregando, pronto ou erro — e a resposta velha que chega por último e não pode vencer.",
"blocos": [
 {"p": "Toda tela que busca dados fora tem três estados: **carregando** (o spinner), **pronto** (o dado) e **erro** (a mensagem). `R.recurso` guarda os três num sinal, e busca de novo quando a fonte muda."},
 {"code": '''adopt Arcane.Reativo as R

busca := R.sinal("café")

action buscar(termo):
    sleep(20)                                   // a rede
    yield [$"{termo} torrado", $"{termo} moído"]

resultados := R.recurso(buscar, busca)
assert resultados.aguardar(2)["valor"] is ["café torrado", "café moído"]

busca.escrever("chá")
final := resultados.aguardar(2)
assert final["estado"] is "pronto" and final["valor"][0] is "chá torrado"''', "lang": "df"},
 {"h2": "A resposta velha"},
 {"p": "A pessoa digita \"ca\" e depois \"café\". A busca de \"ca\" é mais lenta e chega **por último** — e sem cuidado a tela mostra o resultado da pergunta velha, com \"café\" escrito na caixa. Cada busca do recurso leva um número de geração, e a resposta de uma geração passada é **descartada**:"},
 {"code": '''adopt Arcane.Reativo as R

termo := R.sinal("ca")

action buscar(t):
    sleep(300 given t is "ca" otherwise 30)     // a primeira é a lenta
    yield $"resultados de {t}"

r := R.recurso(buscar, termo)
termo.escrever("café")
assert r.aguardar(2)["valor"] is "resultados de café"
sleep(400)                                      // a lenta chega agora…
assert r.ler()["valor"] is "resultados de café" // …e não vence
assert r.descartadas() is 1''', "lang": "df"},
 {"h2": "O erro é um estado, não uma exceção"},
 {"code": '''adopt Arcane.Reativo as R

r := R.recurso(lambda => 1 / 0)
estado := r.aguardar(2)
assert estado["estado"] is "erro"
out estado["erro"]''', "lang": "df"},
 {"p": "A tela decide lendo `r.estado()`, que é um **sinal**: um derivado ou efeito que o lê redesenha quando a busca termina. `aguardar` existe para teste e para script — numa interface, ninguém espera; quem reage é o efeito."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/operadores",
"title": "Operadores de fluxo",
"description": "morph, sift, distill, distintos, primeiros, pular, blocos, esperar e limitar — e quando cada um cabe.",
"blocos": [
 {"p": "Um observável é um fluxo de valores no tempo, e os operadores montam fluxos a partir de outros — cada um devolve um **observável novo**, e o original continua como estava."},
 {"code": '''adopt Arcane.Reativo as R

cliques := R.observavel("cliques")
vistos := []
pares_vezes_dez := cliques.sift(lambda v: v % 2 is 0).morph(lambda v: v * 10)
inscricao := pares_vezes_dez.inscrever(lambda v: vistos.append(v))

cycle i in range(1, 7):
    cliques.emitir(i)
assert vistos is [20, 40, 60]

inscricao.cancelar()
cliques.emitir(8)
assert vistos is [20, 40, 60]           // cancelado, não recebe mais''', "lang": "df"},
 {"table": {"head": ["Operador", "Emite", "Para"], "rows": [
   ["`morph(f)`", "`f(v)` de cada valor", "transformar"],
   ["`sift(cond)`", "só o que passa", "filtrar"],
   ["`distill(f, inicial)`", "o acumulado até aqui", "somatório corrente, estado de um jogo"],
   ["`distintos()`", "só quando muda em relação ao anterior", "não redesenhar à toa"],
   ["`primeiros(n)` · `pular(n)`", "os n primeiros · depois dos n primeiros", "o primeiro clique, ignorar o aquecimento"],
   ["`blocos(n)`", "grupos de n", "gravar em lote"],
   ["`esperar(s)`", "só quando para de chegar por s segundos", "a caixa de busca (*debounce*)"],
   ["`limitar(s)`", "no máximo um por janela", "o botão que não pode ser clicado duas vezes (*throttle*)"],
   ["`para_sinal(inicial)`", "vira um sinal com o último valor", "ligar o fluxo a um derivado"]]}},
 {"code": '''adopt Arcane.Reativo as R

vendas := R.observavel()
total := vendas.distill(lambda acc, v: acc + v, 0).para_sinal(0)
vendas.emitir(30)
vendas.emitir(12)
assert total.ler() is 42

leituras := R.observavel()
mudou := []
leituras.distintos().inscrever(lambda v: mudou.append(v))
cycle v in [20, 20, 21, 21, 20]:
    leituras.emitir(v)
assert mudou is [20, 21, 20]

lotes := []
fonte := R.observavel()
fonte.blocos(2).inscrever(lambda b: lotes.append(b))
cycle v in [1, 2, 3, 4]:
    fonte.emitir(v)
assert lotes is [[1, 2], [3, 4]]''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "`esperar` e `limitar` são o contrário um do outro", "texto": "`esperar` emite o **último** depois do silêncio — a busca roda uma vez, quando a pessoa para de digitar. `limitar` emite o **primeiro** e ignora o resto da janela — o segundo clique no \"pagar\" não passa. Trocar os dois é o bug mais comum de interface reativa."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/lote",
"title": "Escrever em lote",
"description": "Três escritas, uma notificação: o estado intermediário que ninguém deveria ver.",
"blocos": [
 {"p": "Trocar nome e sobrenome são duas escritas. Entre elas, o nome completo vale \"Bia Souza\" com o sobrenome velho — um valor que nunca foi verdade. Um efeito que roda entre as duas escritas mostra esse valor na tela, ou pior, grava."},
 {"code": '''adopt Arcane.Reativo as R

nome := R.sinal("Ana")
sobrenome := R.sinal("Souza")
completo := R.derivado(lambda => $"{nome.ler()} {sobrenome.ler()}")
vistos := []
R.efeito(lambda => vistos.append(completo.ler()))

action trocar():
    nome.escrever("Bia")
    sobrenome.escrever("Lima")

R.lote(trocar)
assert vistos is ["Ana Souza", "Bia Lima"]     // "Bia Souza" nunca apareceu''', "lang": "df"},
 {"p": "Sem o lote, `vistos` teria três valores, e o do meio seria \"Bia Souza\". Dentro dele, os avisos são adiados até o fim, e cada efeito roda **uma vez**, vendo o estado final."},
 {"list": [
   "**Todo comando que muda mais de um sinal é um lote.** Carregar um formulário do servidor, aplicar um filtro com três campos, desfazer uma colagem.",
   "**O [histórico](/docs/reativo/historico) anota um lote como um passo** — é o mesmo mecanismo.",
   "**Uma escrita dentro de um efeito abre a próxima onda**, e não entra na atual: a fila não cresce enquanto é percorrida."]},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/formularios",
"title": "Um formulário reativo",
"description": "Cada campo um sinal, cada erro um derivado, e o botão que só habilita quando tudo está certo.",
"blocos": [
 {"p": "Um formulário é o caso de uso que o modelo reativo resolve melhor: a regra de cada campo é uma **fórmula** sobre o valor dele, e \"pode enviar?\" é uma fórmula sobre os erros. Nada é recalculado à mão, e nenhum campo esquece de revalidar."},
 {"code": '''adopt Arcane.Reativo as R

email := R.sinal("")
senha := R.sinal("")
confirma := R.sinal("")

erro_email := R.derivado(lambda => (void given email.ler().contains("@") otherwise "e-mail inválido"))
erro_senha := R.derivado(lambda => (void given len(senha.ler()) bigger_eq 8 otherwise "mínimo 8 caracteres"))
erro_confirma := R.derivado(lambda => (void given confirma.ler() is senha.ler() otherwise "as senhas diferem"))
pode_enviar := R.derivado(lambda => [erro_email.ler(), erro_senha.ler(), erro_confirma.ler()] is [void, void, void])

assert not pode_enviar.ler()
email.escrever("ana@exemplo.br")
senha.escrever("segredo-longo")
assert erro_confirma.ler() is "as senhas diferem"
confirma.escrever("segredo-longo")
assert pode_enviar.ler()

senha.escrever("curta")                   // mudar a senha revalida a confirmação
assert erro_confirma.ler() is "as senhas diferem" and not pode_enviar.ler()''', "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "O ternário num lambda vai entre parênteses", "texto": "O corpo de um `lambda` liga mais forte que `given … otherwise`: sem os parênteses, `lambda => void given c otherwise \"erro\"` vira um ternário **sobre o lambda**, e o derivado recebe um texto no lugar da ação. O mesmo vale para `>>`. A mensagem de erro mostra a forma certa."}},
 {"callout": {"tipo": "dica", "titulo": "A confirmação depende das duas", "texto": "`erro_confirma` lê `senha` e `confirma`, e as dependências são **descobertas** na execução. Trocar a senha depois de confirmar revalida a confirmação sozinho — é o caso que um formulário imperativo esquece, e o botão fica habilitado com senhas diferentes."}},
 {"p": "Na Vitrine, o mesmo raciocínio vale campo a campo: ver [Estado e cache](/docs/vitrine/estado)."},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/vazamentos",
"title": "Parar o que não se usa",
"description": "Efeito, inscrição, histórico e recurso seguram referências: sem parar, a tela fechada continua reagindo.",
"blocos": [
 {"p": "Um efeito registrado num sinal fica vivo enquanto o sinal viver. Se a tela que o criou fecha e ninguém o para, ele continua rodando a cada mudança — redesenhando o que não existe, e segurando na memória tudo o que o fechamento dele alcança."},
 {"code": '''adopt Arcane.Reativo as R

contador := R.sinal(0)
execucoes := [0]

action mostrar():
    execucoes[0] += 1
    out $"contador: {contador.ler()}"

vigia := R.efeito(mostrar)

contador.escrever(1)
assert execucoes[0] is 2              // uma ao nascer, uma pela mudança

vigia.parar()
contador.escrever(2)
assert execucoes[0] is 2              // parado: não roda mais
assert contador.ouvintes() is 0       // e o sinal não o segura''', "lang": "df"},
 {"table": {"head": ["Peça", "Como parar"], "rows": [
   ["efeito", "`e.parar()`"],
   ["inscrição num observável", "`inscricao.cancelar()`"],
   ["`sinal.observar(acao)`", "chamar o cancelador que ele devolveu"],
   ["histórico", "`h.parar()`"],
   ["recurso", "`r.parar()`"],
   ["observável que acabou", "`o.encerrar()` — avisa `ao_fim` de cada inscrito"]]}},
 {"callout": {"tipo": "dica", "titulo": "`ouvintes()` para o teste", "texto": "Todo sinal responde quantos o escutam. Um teste que abre e fecha a tela cem vezes e confere `ouvintes()` no fim é a forma barata de pegar um vazamento antes de ele virar lentidão."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/testes",
"title": "Testar código reativo",
"description": "Escrever, ler, contar execuções — e aguardar o recurso sem sleep arbitrário.",
"blocos": [
 {"p": "O modelo reativo é **síncrono** por padrão: escrever num sinal recalcula os derivados e roda os efeitos antes de a escrita voltar. Isso torna o teste direto — sem esperar, sem relógio."},
 {"code": '''adopt Arcane.Reativo as R

preco := R.sinal(10)
qtd := R.sinal(2)
contas := [0]

action calcular():
    contas[0] += 1
    yield preco.ler() * qtd.ler()

total := R.derivado(calcular)

assert total.ler() is 20
assert total.ler() is 20
assert contas[0] is 1              // memorizado: duas leituras, uma conta
qtd.escrever(2)                     // o mesmo valor
assert total.ler() is 20 and contas[0] is 1
qtd.escrever(3)
assert total.ler() is 30 and contas[0] is 2''', "lang": "df"},
 {"h2": "O que conferir"},
 {"table": {"head": ["Pergunta", "Como"], "rows": [
   ["o valor está certo?", "`derivado.ler()` depois de escrever"],
   ["recalcula à toa?", "contar as execuções da fórmula"],
   ["o efeito viu um estado intermediário?", "guardar o que ele viu numa lista, e comparar"],
   ["vazou?", "`sinal.ouvintes()` depois de parar"],
   ["o recurso terminou?", "`r.aguardar(prazo)` — espera o estado, e não um tempo fixo"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Nunca `sleep` para esperar um recurso", "texto": "Um `sleep(100)` passa na sua máquina e falha num CI carregado, que é onde a busca demora 150 ms. `aguardar` espera o **estado** sair de \"carregando\", com um prazo que só é atingido quando algo está de fato errado."}},
]},

# ══════════════════════════════════════════════════════════════
{
"href": "/docs/reativo/estado-da-aplicacao",
"title": "O estado de uma aplicação",
"description": "Sinais para o que se escreve, derivados para o que se calcula, comandos para o que muda — e nada mais.",
"blocos": [
 {"p": "Uma aplicação reativa fica fácil de manter quando o estado segue três regras: **o que é informação de fato** é sinal; **o que se calcula a partir dela** é derivado; **o que muda** passa por uma ação nomeada, dentro de um lote. Um derivado guardado como sinal fica desatualizado; um sinal que qualquer um escreve vira depuração de \"quem mudou isto?\"."},
 {"code": '''adopt Arcane.Reativo as R

// ── o estado: só o que não se calcula ──
itens := R.sinal([])
cupom := R.sinal(void)

// ── o que se calcula ──
subtotal := R.derivado(lambda => (itens.ler() >> distill acc, i: acc + i["preco"] * i["qtd"] 0))
desconto := R.derivado(lambda => (subtotal.ler() * 0.1 given cupom.ler() is "DEZ" otherwise 0))
total := R.derivado(lambda => subtotal.ler() - desconto.ler())

// ── o que muda: comandos com nome ──
action adicionar(nome, preco, qtd):
    itens.escrever(itens.ler() + [{"nome": nome, "preco": preco, "qtd": qtd}])

action aplicar_cupom(codigo):
    cupom.escrever(codigo)

historico := R.historico(itens)
adicionar("café", 30, 2)
adicionar("filtro", 10, 1)
aplicar_cupom("DEZ")
assert total.ler() is 63.0
historico.desfazer()                  // tira o filtro
assert total.ler() is 54.0''', "lang": "df"},
 {"list": [
   "**Nunca guarde um calculado.** `total` como sinal precisaria ser atualizado em cada comando — e o primeiro comando novo esquece.",
   "**A lista é trocada, não mudada.** `itens.escrever(itens.ler() + [novo])` notifica; `itens.ler().append(novo)` muda a lista por dentro e **ninguém é avisado**.",
   "**O desfazer vem de graça** quando o estado é pequeno e os comandos só escrevem nele."]},
]},
]
