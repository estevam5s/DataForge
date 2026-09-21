// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "51 · Programação reativa",
  description: "15 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 51`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[283](#283-um-valor-que-outros-valores-acompanham)", "**um valor que outros valores acompanham**", "a diferenca entre \"me avise quando algo acontecer\" e"], ["[284](#284-a-dependencia-e-descoberta-nao-declarada)", "**a dependencia e DESCOBERTA, nao declarada**", "nao ha lista para escrever. O derivado roda, e todo sinal"], ["[285](#285-o-efeito-roda-ao-nascer-e-o-lote-agrupa)", "**o efeito roda ao nascer, e o lote agrupa**", "um efeito que nao rodasse na criacao deixaria a tela sem"], ["[286](#286-o-valor-que-nunca-existiu)", "**o valor que nunca existiu**", "num losango — 'c' le 'a' e 'b', e 'b' le 'a' — marcar e"], ["[287](#287-sinal-e-valor-observavel-e-fluxo)", "**sinal e valor; observavel e fluxo**", "um clique e fluxo — perguntar \"qual o valor do clique"], ["[288](#288-a-fonte-fria-liga-preguicoso)", "**a fonte fria liga preguicoso**", "'de_cluster' so comeca quando alguem escuta. Se o"], ["[289](#289-o-tempo-dentro-do-fluxo)", "**o tempo dentro do fluxo**", "'esperar' e o debounce — so emite quando o fluxo fica"], ["[290](#290-dois-fluxos-num-so-de-duas-formas)", "**dois fluxos num so, de duas formas**", "'juntar' intercala — o que vier, de qualquer um."], ["[291](#291-a-falha-encerra-o-fluxo)", "**a falha ENCERRA o fluxo**", "num fluxo, um erro nao pode derrubar o programa — quem"], ["[292](#292-o-que-o-grafo-reativo-recusa)", "**o que o grafo reativo recusa**", "tres recusas, e cada uma evita um defeito que nao"], ["[293](#293-um-carrinho-que-se-recalcula-sozinho)", "**um carrinho que se recalcula sozinho**", "juntar sinal, derivado, efeito e lote num caso de uso —"], ["[294](#294-quando-mudou-nao-e-obvio)", "**quando \"mudou\" nao e obvio**", "escrever o mesmo valor nao notifica. Mas o que e \"o"], ["[295](#295-o-reativo-em-cima-de-uma-tabela)", "**o reativo em cima de uma tabela**", "um painel que filtra e resume. O filtro e um sinal, a"], ["[296](#296-o-fluxo-que-bate-sozinho)", "**o fluxo que bate sozinho**", "'intervalo' e uma fonte fria com relogio. Ela e a forma"], ["[297](#297-quatro-formas-de-lidar-com-mudanca)", "**quatro formas de lidar com mudanca**", "a linguagem tem 'Arcane.Eventos' (um emissor),"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "283 · um valor que outros valores acompanham"},
  {"p": "**Enunciado.** a diferenca entre \"me avise quando algo acontecer\" e"},
  { code: `// "este total e sempre a soma daqueles tres". O derivado e preguicoso
// e memorizado — e contar as vezes que a formula roda e o unico jeito
// de PROVAR as duas coisas.

adopt Arcane.Reativo as R

steady preco := R.sinal(10.0)
steady quantidade := R.sinal(3)

contas := {"n": 0}

action calcular():
    contas["n"] := contas["n"] + 1
    yield preco.ler() * quantidade.ler()

steady total := R.derivado(calcular)

out "== 1. ele so calcula quando alguem LE =="

assert contas["n"] is 0
assert total.ler() is 30.0
assert contas["n"] is 1

out ""
out "== 2. e o valor fica memorizado =="

total.ler()
total.ler()
assert contas["n"] is 1
out "   tres leituras, uma conta so"

out ""
out "== 3. mudar uma fonte invalida =="

quantidade.escrever(5)
assert total.ler() is 50.0
assert contas["n"] is 2

out ""
out "== 4. escrever o MESMO valor nao invalida =="

// Senao a cadeia recalcularia por nada, e um efeito de rede dispararia
// duas vezes pelo mesmo estado.
quantidade.escrever(5)
assert total.ler() is 50.0
assert contas["n"] is 2

out ""
out "== 5. atualizar le e escreve numa chamada =="

quantidade.atualizar(lambda q => q + 1)
assert quantidade.ler() is 6
assert total.ler() is 60.0

out ""
out "== 6. ler SEM depender =="

// '.valor()' nao registra a dependencia: e a saida para um contador de
// depuracao que nao deve fazer o derivado recalcular.
assert preco.valor() is 10.0
assert quantidade.valor() is 6

out "exercicio 283 ok"`, lang: 'df', title: `exercicios/51-reativo/283_sinal_e_derivado.df` },
  {"p": "A diferença entre *\"me avise quando algo acontecer\"* e *\"este total é sempre a soma daqueles três\"*. Contar as vezes que a fórmula roda é o único jeito de **provar** a preguiça e a memória."},
  {"h3": "Ele só calcula quando alguém lê"},
  {"p": "Recalcular na escrita faria uma cadeia de dez derivados rodar dez vezes por mudança, e a maioria deles nunca é lida."},
  {"h3": "E o valor fica memorizado"},
  {"p": "Três leituras, uma conta. O contador é a prova; sem ele isso seria uma afirmação."},
  {"h3": "Escrever o mesmo valor não invalida"},
  {"p": "Senão a cadeia recalcularia por nada, e um efeito de rede dispararia duas vezes pelo mesmo estado."},
  {"h3": "E `.valor()` lê sem depender"},
  {"p": "É o `untracked` dos outros frameworks: sem ele, um derivado que lê um contador de depuração passaria a recalcular a cada incremento dele."},
  {"h2": "284 · a dependencia e DESCOBERTA, nao declarada"},
  {"p": "**Enunciado.** nao ha lista para escrever. O derivado roda, e todo sinal"},
  { code: `// lido durante a execucao entra. Uma lista a mao envelhece na primeira
// condicao nova dentro da formula — e o sintoma e um valor que para de
// atualizar.

adopt Arcane.Reativo as R

steady subtotal := R.sinal(50.0)
steady cupom := R.sinal(0.0)

contas := {"n": 0}

action calcular_frete():
    contas["n"] := contas["n"] + 1
    given subtotal.ler() bigger 100.0:
        yield 0.0
    yield 20.0 - cupom.ler()

steady frete := R.derivado(calcular_frete)

out "== 1. abaixo de 100, o frete LE o cupom =="

assert frete.ler() is 20.0
antes := contas["n"]

cupom.escrever(5.0)
assert frete.ler() is 15.0
assert contas["n"] is antes + 1
out "   mexer no cupom recalculou o frete"

out ""
out "== 2. acima de 100 a formula toma o outro ramo =="

subtotal.escrever(300.0)
assert frete.ler() is 0.0

out ""
out "== 3. e a partir dai o cupom nao mexe em nada =="

// As fontes que sumiram param de notificar. Sem isso, a formula
// acumularia dependencias dos DOIS ramos e recalcularia por mudancas
// que ela nem le mais.
antes := contas["n"]
cupom.escrever(7.0)
frete.ler()
assert contas["n"] is antes
out "   o cupom saiu das dependencias"

out ""
out "== 4. voltando abaixo de 100, ele volta =="

subtotal.escrever(50.0)
assert frete.ler() is 13.0
antes := contas["n"]
cupom.escrever(1.0)
assert frete.ler() is 19.0
assert contas["n"] is antes + 1

out ""
out "== 5. um derivado sobre derivados =="

steady total := R.derivado(lambda => subtotal.ler() + frete.ler())
assert total.ler() is 69.0
subtotal.escrever(60.0)
assert total.ler() is 79.0

out "exercicio 284 ok"`, lang: 'df', title: `exercicios/51-reativo/284_dependencia_descoberta.df` },
  {"p": "Não há lista para escrever: o derivado roda, e todo sinal lido durante a execução entra. Uma lista à mão envelhece na primeira condição nova dentro da fórmula — e o sintoma é um valor que **para de atualizar**."},
  {"h3": "O ramo tomado decide a dependência"},
  {"p": "Abaixo de 100 o frete lê o cupom, e mexer no cupom o invalida. Acima de 100 a fórmula toma o outro ramo e não lê mais."},
  {"h3": "As fontes que sumiram param de notificar"},
  {"p": "Sem isso, a fórmula acumularia as dependências dos **dois** ramos e recalcularia por mudanças que ela nem lê mais."},
  {"h3": "E voltando, a dependência volta"},
  {"p": "Ela é refeita a cada execução: não há estado antigo a limpar."},
  {"h2": "285 · o efeito roda ao nascer, e o lote agrupa"},
  {"p": "**Enunciado.** um efeito que nao rodasse na criacao deixaria a tela sem"},
  { code: `// o estado inicial — e quem escreve teria de chama-lo a mao, o que se
// esquece exatamente uma vez. E tres escritas em sequencia mostram dois
// estados intermediarios que nunca deveriam aparecer.

adopt Arcane.Reativo as R

steady a := R.sinal(1)
steady b := R.sinal(10)
steady soma := R.derivado(lambda => a.ler() + b.ler())

vistos := []

action anotar():
    vistos.append(soma.ler())

steady vigia := R.efeito(anotar)

out "== 1. ele ja rodou =="

assert vistos is [11]

out ""
out "== 2. e roda de novo a cada mudanca =="

a.escrever(2)
assert vistos is [11, 12]
b.escrever(20)
assert vistos is [11, 12, 22]

out ""
out "== 3. o lote agrupa varias escritas numa notificacao =="

action tres_escritas():
    a.escrever(3)
    b.escrever(30)
    a.escrever(4)

R.lote(tres_escritas)
assert vistos is [11, 12, 22, 34]
out "   tres escritas, uma notificacao"

out ""
out "== 4. o lote devolve o que a acao devolveu =="

assert R.lote(lambda => 42) is 42

out ""
out "== 5. parar e definitivo =="

vigia.parar()
a.escrever(100)
assert vistos is [11, 12, 22, 34]
assert soma.ler() is 130
out "   o derivado continua certo; o efeito e que parou"

out ""
out "== 6. um efeito que nao le sinal nenhum roda uma vez so =="

// Sem dependencia descoberta, nada tem como acorda-lo de novo.
quantas := {"n": 0}

action so_conta():
    quantas["n"] := quantas["n"] + 1

steady solto := R.efeito(so_conta)
assert quantas["n"] is 1

a.escrever(200)
b.escrever(300)
assert quantas["n"] is 1
out "   sem dependencia, nada o acorda"

out "exercicio 285 ok"`, lang: 'df', title: `exercicios/51-reativo/285_efeito_e_lote.df` },
  {"p": "Um efeito que não rodasse na criação deixaria a tela sem o estado inicial — e quem escreve teria de chamá-lo à mão, o que se esquece exatamente uma vez."},
  {"h3": "Ele já rodou"},
  {"p": "E roda de novo a cada mudança de qualquer dependência."},
  {"h3": "O lote agrupa várias escritas numa notificação"},
  {"p": "Sem ele, três escritas mostram dois estados intermediários que nunca deveriam aparecer na tela. E ele **já existiu sem agrupar nada**: montava uma lista de adiados que ninguém lia."},
  {"h3": "Parar é definitivo"},
  {"p": "O derivado continua certo; o que parou foi o efeito. São coisas diferentes, e confundi-las faz alguém \"desligar\" o cálculo achando que desligou o desenho."},
  {"h3": "E um efeito sem dependência roda uma vez só"},
  {"p": "Sem sinal lido, nada tem como acordá-lo."},
  {"h2": "286 · o valor que nunca existiu"},
  {"p": "**Enunciado.** num losango — 'c' le 'a' e 'b', e 'b' le 'a' — marcar e"},
  { code: `// avisar numa fase so entrega um numero errado na tela, que aparece e
// some sozinho. A propagacao tem DUAS fases: marcar o grafo inteiro e,
// so entao, avisar.

adopt Arcane.Reativo as R

steady a := R.sinal(1)
steady b := R.derivado(lambda => a.ler() * 2)
steady c := R.derivado(lambda => a.ler() + b.ler())

vistos := []
steady vigia := R.efeito(lambda => vistos.append(c.ler()))

out "== 1. o estado inicial =="

assert vistos is [3]  // ou seja, um mais dois

out ""
out "== 2. uma escrita, UM aviso, e ele consistente =="

a.escrever(5)
// O certo e 15 (5 + 10). Antes da correcao o efeito via 7 primeiro —
// o 'a' novo somado ao 'b' velho —, e esse 7 nunca foi verdade.
assert vistos is [3, 15]
out $"   {vistos}"

out ""
out "== 3. o efeito alcancado por dois caminhos roda UMA vez =="

a.escrever(10)
assert len(vistos) is 3
assert vistos[-1] is 30

out ""
out "== 4. uma cadeia longa tambem avisa uma vez =="

steady d1 := R.derivado(lambda => a.ler() + 1)
steady d2 := R.derivado(lambda => d1.ler() + 1)
steady d3 := R.derivado(lambda => d2.ler() + 1)
steady d4 := R.derivado(lambda => d3.ler() + 1)

quantas := []
steady fim := R.efeito(lambda => quantas.append(d4.ler()))
assert quantas is [14]

a.escrever(100)
assert quantas is [14, 104]

out ""
out "== 5. o ouvinte de um derivado espera a marcacao =="

lidos := []
c.observar(lambda v => lidos.append(v))
a.escrever(7)
assert lidos is [21]

out "exercicio 286 ok"`, lang: 'df', title: `exercicios/51-reativo/286_losango.df` },
  {"p": "Num losango — `c` lê `a` e `b`, e `b` lê `a` — marcar e avisar numa fase só entrega um número **errado**, que aparece e some sozinho."},
  {"h3": "O 7 nunca foi verdade"},
  {"p": "Com `a = 5`, o certo é 15. O 7 era `5 + o b antigo`: `b` ainda estava limpo quando `c` recalculou. E a lista de dependentes é um **conjunto**, então qual caminho vem primeiro não é escolhido por ninguém — o defeito ia e vinha conforme a ordem de hash."},
  {"h3": "A marcação percorre o grafo inteiro primeiro"},
  {"p": "Só depois os efeitos e ouvintes rodam. Quando eles rodam, todo derivado alcançado já sabe que está sujo."},
  {"h3": "E o efeito alcançado por dois caminhos roda uma vez"},
  {"p": "Deduplicado pelo próprio objeto — e não por `id()`, que só é único entre objetos **vivos**."},
  {"p": "---"},
  {"p": "Não é uma notificação a mais: é um valor errado na tela. Um defeito que produz o número certo *depois* é mais difícil de achar que um que estoura."},
  {"h2": "287 · sinal e valor; observavel e fluxo"},
  {"p": "**Enunciado.** um clique e fluxo — perguntar \"qual o valor do clique"},
  { code: `// agora?" nao tem resposta. Um saldo e valor. Frameworks que chamam os
// dois de "stream" fazem a pergunta "qual e o valor atual?" deixar de
// ter resposta.

adopt Arcane.Reativo as R

steady cliques := R.observavel("cliques")
recebidos := []

out "== 1. quem se inscreve recebe o que vier DAQUI PARA A FRENTE =="

cliques.emitir({"botao": "ver", "produto": "cafe"})  // ninguem ouvia

inscricao := cliques.inscrever(lambda c => recebidos.append(c["produto"]))
cliques.emitir({"botao": "comprar", "produto": "moedor"})
assert recebidos is ["moedor"]

out ""
out "== 2. os operadores sao os mesmos nomes do pipeline =="

compras := []
so_compras := cliques.sift(lambda c => c["botao"] is "comprar")
nomes := so_compras.morph(lambda c => c["produto"])
outra := nomes.distintos().inscrever(lambda p => compras.append(p))

cliques.emitir({"botao": "ver", "produto": "prensa"})
cliques.emitir({"botao": "comprar", "produto": "cafe"})
cliques.emitir({"botao": "comprar", "produto": "cafe"})
cliques.emitir({"botao": "comprar", "produto": "filtro"})

assert compras is ["cafe", "filtro"]
out $"   {compras}"

out ""
out "== 3. cancelar para de chegar =="

outra.cancelar()
cliques.emitir({"botao": "comprar", "produto": "coador"})
assert compras is ["cafe", "filtro"]
assert len(recebidos) bigger 1

out ""
out "== 4. o fluxo vira valor quando a pergunta muda =="

ultimo := cliques.para_sinal({"produto": "nenhum"})
assert ultimo.ler()["produto"] is "nenhum"
cliques.emitir({"botao": "comprar", "produto": "bule"})
assert ultimo.ler()["produto"] is "bule"

out ""
out "== 5. encerrar e definitivo =="

inscricao.cancelar()
cliques.encerrar()

fechado := no
monitor:
    cliques.emitir({"botao": "comprar", "produto": "tarde"})
handle StreamClosedError as e:
    fechado := yes
    assert "encerrado" in e.message
assert fechado

out "exercicio 287 ok"`, lang: 'df', title: `exercicios/51-reativo/287_observavel.df` },
  {"p": "Um clique é fluxo — perguntar *\"qual o valor do clique agora?\"* não tem resposta. Um saldo é valor. Frameworks que chamam os dois de \"stream\" fazem a pergunta *\"qual é o valor atual?\"* deixar de ter resposta."},
  {"h3": "Quem se inscreve recebe o que vier daqui para a frente"},
  {"p": "O que foi emitido antes não volta. É a definição de fluxo."},
  {"h3": "Os operadores têm os nomes do pipeline"},
  {"p": "`morph`, `sift`, `distill` — os mesmos do `>>` da linguagem, e não um segundo vocabulário."},
  {"h3": "O fluxo vira valor quando a pergunta muda"},
  {"p": "`para_sinal` é a ponte: a partir dali, \"qual é o último?\" tem resposta."},
  {"h3": "E encerrar é definitivo"},
  {"p": "Emitir depois disso levanta. Devolver `no` calado fazia o valor sumir sem nada no log."},
  {"h2": "288 · a fonte fria liga preguicoso"},
  {"p": "**Enunciado.** 'de_cluster' so comeca quando alguem escuta. Se o"},
  { code: `// operador se ligasse a fonte na CONSTRUCAO, os valores sairiam antes
// de o assinante final existir — e o resultado seria uma lista vazia,
// sem erro nenhum.

adopt Arcane.Reativo as R

// Nomeado porque o lint tem razao: um 4 solto em cinco lugares e
// cinco decisoes que se perdem de vista.
steady ATE_SEIS := [1, 2, 3, 4, 5, 6]
steady ATE_CINCO := [1, 2, 3, 4, 5]
steady ATE_QUATRO := [1, 2, 3, 4]

out "== 1. a cadeia inteira chega =="

dobrados := []
pares := R.de_cluster(ATE_SEIS).sift(lambda n => n % 2 is 0)
pares.morph(lambda n => n * 10).inscrever(lambda n => dobrados.append(n))
assert dobrados is [20, 40, 60]

out ""
out "== 2. sem ninguem escutando, nada corre =="

correu := []
frio := R.de_cluster([1, 2, 3]).morph(lambda n => rastrear(n, correu))

action rastrear(n, caixa):
    caixa.append(n)
    yield n

assert correu is []
out "   a fonte fria esperou"

frio.inscrever(lambda _n => void)
assert correu is [1, 2, 3]

out ""
out "== 3. primeiros e pular recortam =="

tres := []
R.de_cluster(ATE_CINCO).primeiros(3).inscrever(lambda n => tres.append(n))
assert tres is [1, 2, 3]

resto := []
R.de_cluster(ATE_CINCO).pular(3).inscrever(lambda n => resto.append(n))
assert resto is [4, 5]

out ""
out "== 4. blocos junta em grupos =="

grupos := []
R.de_cluster(ATE_CINCO).blocos(2).inscrever(lambda g => grupos.append(g))
assert grupos is [[1, 2], [3, 4]]
out "   o resto incompleto nao e emitido"

out ""
out "== 5. distill acumula ao longo do fluxo =="

somas := []
R.de_cluster(ATE_QUATRO).distill(lambda a, v => a + v, 0)
    .inscrever(lambda s => somas.append(s))
assert somas is [1, 3, 6, 10]

out "exercicio 288 ok"`, lang: 'df', title: `exercicios/51-reativo/288_fonte_fria.df` },
  {"p": "`de_cluster` só começa quando alguém escuta. Se o operador se ligasse à fonte na **construção**, os valores sairiam antes de o assinante final existir — e o resultado seria uma lista vazia, sem erro nenhum."},
  {"h3": "A cadeia inteira chega"},
  {"p": "Porque cada operador só se conecta à sua fonte ao receber o primeiro inscrito."},
  {"h3": "Sem ninguém escutando, nada corre"},
  {"p": "A prova é um efeito colateral dentro do `morph`: ele não aconteceu."},
  {"h3": "E os recortes"},
  {"p": "`primeiros`, `pular`, `blocos` e `distill` — o `blocos` não emite o resto incompleto, porque um bloco pela metade não é um bloco."},
  {"h2": "289 · o tempo dentro do fluxo"},
  {"p": "**Enunciado.** 'esperar' e o debounce — so emite quando o fluxo fica"},
  { code: `// quieto; 'limitar' e o throttle — deixa passar no maximo um por
// intervalo. Os dois existem porque um campo de busca que consulta a
// cada tecla manda vinte consultas para escrever "cafeteira".

adopt Arcane.Reativo as R
adopt Arcane.Time as Tempo

steady QUIETO := 0.12
steady PRAZO := 5.0

action esperar_ate(condicao):
    """Espera a condicao, e nao o relogio: um 'sleep' fixo mede a
    maquina, e o mesmo exercicio reprova numa esteira carregada."""
    limite := Tempo.timestamp() + PRAZO
    persist Tempo.timestamp() smaller limite:
        given condicao():
            yield yes
        Tempo.sleep(0.01)
    yield no

out "== 1. esperar so emite depois do silencio =="

teclas := R.observavel("teclas")
buscas := []
teclas.esperar(QUIETO).inscrever(lambda t => buscas.append(t))

cycle letra in ["c", "ca", "caf", "cafe"]:
    teclas.emitir(letra)

// Nada saiu ainda: o fluxo nao ficou quieto.
assert buscas is []
assert esperar_ate(lambda => len(buscas) is 1)
assert buscas is ["cafe"]
out $"   quatro teclas, uma busca: {buscas}"

out ""
out "== 2. um segundo silencio emite de novo =="

teclas.emitir("cha")
assert esperar_ate(lambda => len(buscas) is 2)
assert buscas is ["cafe", "cha"]

out ""
out "== 3. limitar deixa passar o PRIMEIRO de cada intervalo =="

rolagem := R.observavel("rolagem")
marcos := []
rolagem.limitar(QUIETO).inscrever(lambda n => marcos.append(n))

cycle i from 1 to 5:
    rolagem.emitir(i)

assert marcos is [1]
out "   cinco eventos de rolagem, um marco"

Tempo.sleep(QUIETO * 2)
rolagem.emitir(99)
assert esperar_ate(lambda => len(marcos) is 2)
assert marcos is [1, 99]

out ""
out "== 4. a diferenca, em uma frase =="

// 'esperar' responde no FIM da rajada; 'limitar' responde no COMECO.
assert buscas[0] is "cafe"  // a ultima tecla
assert marcos[0] is 1  // o primeiro evento

out "exercicio 289 ok"`, lang: 'df', title: `exercicios/51-reativo/289_esperar_e_limitar.df` },
  {"p": "`esperar` é o *debounce* — só emite quando o fluxo fica quieto; `limitar` é o *throttle* — deixa passar no máximo um por intervalo."},
  {"h3": "A diferença, em uma frase"},
  {"p": "`esperar` responde no **fim** da rajada; `limitar` responde no **começo**."},
  {"h3": "E os dois existem pelo mesmo motivo"},
  {"p": "Um campo de busca que consulta a cada tecla manda vinte consultas para escrever \"cafeteira\"."},
  {"h3": "O teste espera por CONDIÇÃO"},
  {"p": "Um `sleep` fixo mede a máquina, e o mesmo exercício reprova numa esteira carregada sem que nada tenha mudado no código."},
  {"h2": "290 · dois fluxos num so, de duas formas"},
  {"p": "**Enunciado.** 'juntar' intercala — o que vier, de qualquer um."},
  { code: `// 'combinar' emite o ULTIMO de cada, e so depois que todos ja
// emitiram pelo menos uma vez: antes disso nao ha "ultimo" para um
// deles, e inventar um seria mentir sobre um valor que nunca existiu.

adopt Arcane.Reativo as R

out "== 1. juntar intercala =="

a := R.observavel("a")
b := R.observavel("b")
tudo := []
R.juntar(a, b).inscrever(lambda v => tudo.append(v))

a.emitir(1)
b.emitir("x")
a.emitir(2)
b.emitir("y")

assert tudo is [1, "x", 2, "y"]

out ""
out "== 2. combinar espera todos falarem uma vez =="

c := R.observavel("c")
d := R.observavel("d")
pares := []
R.combinar(c, d).inscrever(lambda p => pares.append(p))

c.emitir(1)
assert pares is []  // 'd' ainda nao falou
c.emitir(2)
assert pares is []

d.emitir("x")
assert pares is [[2, "x"]]
out $"   {pares}"

out ""
out "== 3. e dai em diante, qualquer um dispara =="

c.emitir(3)
assert pares is [[2, "x"], [3, "x"]]
d.emitir("y")
assert pares is [[2, "x"], [3, "x"], [3, "y"]]

out ""
out "== 4. um formulario com dois campos =="

nome := R.observavel("nome")
email := R.observavel("email")
validos := []

action conferir(par):
    ok := len(par[0]) bigger 0 and "@" in par[1]
    validos.append(ok)

R.combinar(nome, email).inscrever(conferir)

nome.emitir("Ana")
email.emitir("ana")
assert validos is [no]
email.emitir("ana@exemplo.com")
assert validos is [no, yes]

out "exercicio 290 ok"`, lang: 'df', title: `exercicios/51-reativo/290_juntar_e_combinar.df` },
  {"p": "`juntar` intercala — o que vier, de qualquer um. `combinar` emite o **último de cada** sempre que qualquer um emite."},
  {"h3": "Combinar espera todos falarem uma vez"},
  {"p": "Antes disso não há \"último\" para um deles, e inventar um seria mentir sobre um valor que nunca existiu."},
  {"h3": "E daí em diante, qualquer um dispara"},
  {"p": "O par carrega o valor novo de quem emitiu e o último de quem não emitiu."},
  {"h3": "Um formulário com dois campos"},
  {"p": "É o caso canônico: a validação precisa dos dois, e nenhum dos dois sozinho responde."},
  {"h2": "291 · a falha ENCERRA o fluxo"},
  {"p": "**Enunciado.** num fluxo, um erro nao pode derrubar o programa — quem"},
  { code: `// escuta esta num retorno de chamada, longe de qualquer 'monitor'.
// 'falhar' avisa quem se inscreveu E encerra: um fluxo que continuasse
// depois de falhar deixaria quem escuta sem saber se o proximo valor
// veio de uma fonte que ainda funciona.

adopt Arcane.Reativo as R

out "== 1. quem se inscreve pode receber o erro =="

leituras := R.observavel("leituras")
valores := []
falhas := []
fins := []

leituras.inscrever(lambda v => valores.append(v),
    lambda e => falhas.append(str(e)),
    lambda => fins.append(yes))

leituras.emitir(10)
leituras.falhar("o sensor nao respondeu")

assert valores is [10]
assert len(falhas) is 1
assert "sensor" in falhas[0]

out ""
out "== 2. e a falha ENCERRA o fluxo =="

// O aviso de fim sai junto: quem escuta sabe que nao vem mais nada.
assert fins is [yes]

acabou := no
monitor:
    leituras.emitir(20)
handle StreamClosedError:
    acabou := yes
assert acabou
out "   depois da falha, nao ha proximo valor"

out ""
out "== 3. ao_falhar transforma o erro em VALOR =="

sensor := R.observavel("sensor")
lidos := []
sensor.ao_falhar(lambda _e => -1).inscrever(lambda v => lidos.append(v))

sensor.emitir(21)
sensor.falhar("cabo solto")
assert lidos is [21, -1]
out $"   {lidos}"

// O fluxo continua encerrado: 'ao_falhar' traduz a falha, e nao a
// desfaz.
ainda := no
monitor:
    sensor.emitir(22)
handle StreamClosedError:
    ainda := yes
assert ainda

out ""
out "== 4. o fim sem erro tambem e avisado =="

fila := R.observavel("fila")
fim := []
fila.inscrever(lambda _v => void, void, lambda => fim.append(yes))

assert fim is []
assert fila.encerrar() is yes
assert fim is [yes]
assert fila.encerrar() is no  // encerrar de novo nao avisa de novo

out ""
out "== 5. um SINAL nao tem erro =="

// Ele tem um valor agora; "o saldo falhou" nao e um estado de saldo.
// Quem precisa disso guarda um Arcane.Resultado dentro do sinal.
saldo := R.sinal(100)
assert saldo.ler() is 100

out "exercicio 291 ok"`, lang: 'df', title: `exercicios/51-reativo/291_erro_no_fluxo.df` },
  {"p": "Num fluxo, um erro não pode derrubar o programa — quem escuta está num retorno de chamada, longe de qualquer `monitor`."},
  {"h3": "Falhar avisa E encerra"},
  {"p": "Um fluxo que continuasse depois de falhar deixaria quem escuta sem saber se o próximo valor veio de uma fonte que ainda funciona. O aviso de fim sai junto."},
  {"h3": "`ao_falhar` transforma o erro em VALOR"},
  {"p": "E não desfaz o encerramento: ele traduz a falha, e o fluxo continua fechado."},
  {"h3": "E um SINAL não tem erro"},
  {"p": "Ele tem um valor agora; *\"o saldo falhou\"* não é um estado de saldo. Quem precisa disso guarda um `Arcane.Resultado` dentro do sinal."},
  {"h2": "292 · o que o grafo reativo recusa"},
  {"p": "**Enunciado.** tres recusas, e cada uma evita um defeito que nao"},
  { code: `// levantaria erro nenhum — ele so entregaria o valor errado.

adopt Arcane.Reativo as R

out "== 1. um derivado que depende de si mesmo =="

caixa := {}
steady a := R.derivado(lambda => caixa["b"].ler() + 1)
steady b := R.derivado(lambda => a.ler() + 1)
caixa["b"] := b

ciclo := no
monitor:
    a.ler()
handle ReactiveCycleError as e:
    ciclo := yes
    // A cadeia INTEIRA: dizer so "ha um ciclo" manda procurar em toda
    // a formula.
    assert "→" in e.nota
    out $"   {e.nota}"
assert ciclo

out ""
out "== 2. um derivado nao pode ESCREVER =="

// A formula e lida para descobrir de que ela depende. Escrever de
// dentro dela faz a propagacao correr no meio da propria descoberta.
contador := R.sinal(0)
steady mau := R.derivado(lambda => contador.escrever(1))

escreveu := no
monitor:
    mau.ler()
handle ReactiveWriteError as e:
    escreveu := yes
    assert "efeito" in e.dica
assert escreveu
assert contador.ler() is 0

out ""
out "== 3. mas um EFEITO pode =="

// Ele nao tem valor a produzir, e a escrita dele abre a proxima onda.
origem := R.sinal(1)
eco := R.sinal(0)
steady espelho := R.efeito(lambda => eco.escrever(origem.ler() * 10))

assert eco.ler() is 10
origem.escrever(3)
assert eco.ler() is 30
espelho.parar()

out ""
out "== 4. emitir num fluxo encerrado =="

fluxo := R.observavel("f")
fluxo.encerrar()

tarde := no
monitor:
    fluxo.emitir(1)
handle StreamClosedError:
    tarde := yes
assert tarde

out ""
out "== 5. a base pega as tres =="

action pela_base(acao):
    monitor:
        acao()
    handle ReactiveError:
        yield yes
    yield no

assert pela_base(lambda => a.ler())
assert pela_base(lambda => mau.ler())
assert pela_base(lambda => fluxo.emitir(1))

out "exercicio 292 ok"`, lang: 'df', title: `exercicios/51-reativo/292_reativo_recusa.df` },
  {"p": "Três recusas, e cada uma evita um defeito que não levantaria erro nenhum — ele só entregaria o valor errado."},
  {"h3": "Um derivado que depende de si mesmo"},
  {"p": "A mensagem traz a **cadeia inteira**: dizer só \"há um ciclo\" manda procurar em toda a fórmula, e o ciclo mais curto é o mais fácil de quebrar."},
  {"h3": "Um derivado não pode escrever"},
  {"p": "A fórmula é lida para descobrir de **que** ela depende. Escrever de dentro dela faz a propagação correr no meio da própria descoberta: o grafo muda enquanto está sendo percorrido."},
  {"h3": "Mas um EFEITO pode"},
  {"p": "Ele não tem valor a produzir, e a escrita dele abre a **próxima** onda — e não reentra na que está correndo."},
  {"h2": "293 · um carrinho que se recalcula sozinho"},
  {"p": "**Enunciado.** juntar sinal, derivado, efeito e lote num caso de uso —"},
  { code: `// e medir quantas vezes cada formula rodou, que e o unico jeito de
// provar que a preguica e real.

adopt Arcane.Reativo as R

steady itens := R.sinal([])
steady cupom := R.sinal(0)
steady FRETE_BASE := 2000
steady ISENCAO := 15000

contas := {"subtotal": 0, "frete": 0, "total": 0}

action calcular_subtotal():
    contas["subtotal"] := contas["subtotal"] + 1
    yield sum([i["centavos"] * i["qtd"] cycle i in itens.ler()])

steady subtotal := R.derivado(calcular_subtotal)

action calcular_frete():
    contas["frete"] := contas["frete"] + 1
    given subtotal.ler() bigger_eq ISENCAO:
        yield 0
    yield FRETE_BASE - cupom.ler()

steady frete := R.derivado(calcular_frete)

action calcular_total():
    contas["total"] := contas["total"] + 1
    yield subtotal.ler() + frete.ler()

steady total := R.derivado(calcular_total)

recibos := []
steady recibo := R.efeito(lambda => recibos.append(total.ler()))

out "== 1. o carrinho vazio =="

assert subtotal.ler() is 0
assert frete.ler() is FRETE_BASE
assert recibos is [2000]

out ""
out "== 2. dois produtos =="

itens.escrever([
        {"nome": "cafe", "centavos": 3250, "qtd": 2},
        {"nome": "filtro", "centavos": 900, "qtd": 1}
    ])
assert subtotal.ler() is 7400
assert total.ler() is 9400
assert recibos[-1] is 9400

out ""
out "== 3. o cupom so vale abaixo da isencao =="

cupom.escrever(500)
assert frete.ler() is 1500
assert total.ler() is 8900

out ""
out "== 4. passando da isencao, o frete zera e para de ler o cupom =="

itens.escrever([{"nome":"moedor", "centavos":24000, "qtd":1}])
assert frete.ler() is 0
assert total.ler() is 24000

antes := contas["frete"]
cupom.escrever(900)
frete.ler()
assert contas["frete"] is antes
out "   o cupom saiu das dependencias do frete"

out ""
out "== 5. o lote agrupa a montagem inteira =="

quantos_recibos := len(recibos)

action montar_de_novo():
    itens.escrever([{"nome":"prensa", "centavos":8000, "qtd":1}])
    cupom.escrever(0)
    itens.escrever([{"nome":"prensa", "centavos":8000, "qtd":2}])

R.lote(montar_de_novo)
assert len(recibos) is quantos_recibos + 1
assert total.ler() is 16000  // passou da isencao: frete zero
out $"   tres escritas, um recibo: {recibos[-1]}"

out ""
out "== 6. e as contas provam a preguica =="

// Cada formula rodou muito menos vezes do que houve escritas.
out $"   subtotal {contas['subtotal']}, frete {contas['frete']}, total {contas['total']}"
assert contas["subtotal"] smaller 10
assert contas["total"] smaller 12

out "exercicio 293 ok"`, lang: 'df', title: `exercicios/51-reativo/293_reativo_carrinho.df` },
  {"p": "Sinal, derivado, efeito e lote num caso de uso — e as contagens que **provam** que a preguiça é real."},
  {"h3": "A isenção muda a dependência"},
  {"p": "Acima do valor de isenção o frete deixa de ler o cupom, e mexer nele para de recalcular qualquer coisa."},
  {"h3": "O lote agrupa a montagem inteira"},
  {"p": "Três escritas, um recibo."},
  {"h3": "E as contas fecham"},
  {"p": "Cada fórmula rodou muito menos vezes do que houve escritas — e o número é medido, não afirmado."},
  {"h2": "294 · quando \"mudou\" nao e obvio"},
  {"p": "**Enunciado.** escrever o mesmo valor nao notifica. Mas o que e \"o"},
  { code: `// mesmo" depende do valor: dois clusters com o mesmo conteudo sao
// iguais, e dois objetos sem igualdade declarada nao. O sinal aceita a
// comparacao de quem escreveu.

adopt Arcane.Reativo as R

out "== 1. o padrao compara por igualdade =="

n := R.sinal(10)
vezes := []
n.observar(lambda v => vezes.append(v))

n.escrever(10)
assert vezes is []
n.escrever(11)
assert vezes is [11]

out ""
out "== 2. dois clusters de mesmo conteudo sao o mesmo valor =="

xs := R.sinal([1, 2, 3])
mudou := []
xs.observar(lambda v => mudou.append(len(v)))

xs.escrever([1, 2, 3])
assert mudou is []
xs.escrever([1, 2, 3, 4])
assert mudou is [4]

out ""
out "== 3. mudar a lista NO LUGAR nao avisa ninguem =="

// O sinal guarda uma referencia, e a referencia nao mudou. E a mesma
// razao por que a vigia do depurador compara uma FOTO estrutural.
atual := xs.ler()
atual.append(5)
assert len(xs.ler()) is 5
assert mudou is [4]
out "   append nao e escrita: o sinal nao soube"

// A forma que avisa e escrever uma lista nova.
xs.escrever([...atual, 6])
assert mudou is [4, 6]

out ""
out "== 4. uma comparacao propria =="

// Duas leituras de sensor que diferem por menos de 0,5 grau sao "a
// mesma temperatura" — e sem isso a tela pisca a cada ruido.
action quase_igual(a, b):
    yield abs(a - b) smaller 0.5

temperatura := R.sinal(20.0, iguais := quase_igual)
avisos := []
temperatura.observar(lambda t => avisos.append(t))

temperatura.escrever(20.2)
temperatura.escrever(20.4)
assert avisos is []
temperatura.escrever(21.0)
assert avisos is [21.0]
out $"   tres leituras, um aviso: {avisos}"

out ""
out "== 5. cancelar o observador =="

parar := temperatura.observar(lambda t => avisos.append(t))
temperatura.escrever(30.0)
assert len(avisos) is 3
parar()
temperatura.escrever(40.0)
assert len(avisos) is 4

out "exercicio 294 ok"`, lang: 'df', title: `exercicios/51-reativo/294_sinal_igualdade.df` },
  {"p": "Escrever o mesmo valor não notifica. Mas o que é \"o mesmo\" depende do valor."},
  {"h3": "Dois clusters de mesmo conteúdo são o mesmo valor"},
  {"p": "A comparação padrão é a igualdade da linguagem, e ela é estrutural."},
  {"h3": "Mudar a lista NO LUGAR não avisa ninguém"},
  {"p": "O sinal guarda uma referência, e a referência não mudou. É a mesma razão por que a vigia do depurador compara uma **foto** estrutural — e a forma que avisa é escrever uma lista nova."},
  {"h3": "E uma comparação própria"},
  {"p": "Duas leituras de sensor que diferem por menos de meio grau são \"a mesma temperatura\" — e sem isso a tela pisca a cada ruído."},
  {"h2": "295 · o reativo em cima de uma tabela"},
  {"p": "**Enunciado.** um painel que filtra e resume. O filtro e um sinal, a"},
  { code: `// tabela filtrada e um derivado, e o resumo e outro — mexer no filtro
// recalcula os dois, e so eles.

adopt Arcane.Reativo as R
adopt Arcane.Quadro as Q

steady VENDAS := [
    {"vendedor": "Ana", "regiao": "sul", "valor": 1200.0},
    {"vendedor": "Bia", "regiao": "sul", "valor": 800.0},
    {"vendedor": "Caio", "regiao": "norte", "valor": 2400.0},
    {"vendedor": "Dora", "regiao": "norte", "valor": 600.0},
    {"vendedor": "Eva", "regiao": "sul", "valor": 3000.0}
]

steady regiao := R.sinal("sul")
steady minimo := R.sinal(0.0)

contas := {"filtrar": 0, "resumir": 0}

action filtrar():
    contas["filtrar"] := contas["filtrar"] + 1
    r := regiao.ler()
    m := minimo.ler()
    yield [v cycle v in VENDAS given v["regiao"] is r and v["valor"] bigger_eq m]

steady filtradas := R.derivado(filtrar)

action resumir():
    contas["resumir"] := contas["resumir"] + 1
    linhas := filtradas.ler()
    given len(linhas) is 0:
        yield {"quantas": 0, "total": 0.0, "media": 0.0}
    total := sum([l["valor"] cycle l in linhas])
    yield {"quantas": len(linhas), "total": total,
        "media": round(total / len(linhas), 2)}

steady resumo := R.derivado(resumir)

out "== 1. o sul =="

assert resumo.ler()["quantas"] is 3
assert resumo.ler()["total"] is 5000.0
out $"   {resumo.ler()}"

out ""
out "== 2. trocar a regiao recalcula os dois =="

regiao.escrever("norte")
assert resumo.ler()["quantas"] is 2
assert resumo.ler()["total"] is 3000.0

out ""
out "== 3. o minimo tambem e uma dependencia =="

minimo.escrever(1000.0)
assert resumo.ler()["quantas"] is 1
assert filtradas.ler()[0]["vendedor"] is "Caio"

out ""
out "== 4. e o quadro le a mesma lista =="

quadro := Q.de_vaults(filtradas.ler())
assert len(quadro) is 1
assert quadro.colunas() is ["vendedor", "regiao", "valor"]

out ""
out "== 5. nada recalcula sem leitura =="

antes := contas["filtrar"]
regiao.escrever("sul")
minimo.escrever(0.0)
assert contas["filtrar"] is antes
assert resumo.ler()["quantas"] is 3
assert contas["filtrar"] is antes + 1
out "   duas escritas, uma conta"

out "exercicio 295 ok"`, lang: 'df', title: `exercicios/51-reativo/295_reativo_e_quadro.df` },
  {"p": "Um painel que filtra e resume: o filtro é um sinal, a tabela filtrada é um derivado, e o resumo é outro."},
  {"h3": "Mexer no filtro recalcula os dois"},
  {"p": "E só eles: a fonte não é tocada."},
  {"h3": "Nada recalcula sem leitura"},
  {"p": "Duas escritas seguidas, uma conta. É a preguiça valendo numa cadeia de dois níveis."},
  {"h3": "E o quadro lê a mesma lista"},
  {"p": "`Q.de_vaults` recebe o que o derivado devolveu — sem conversão, sem cópia."},
  {"h2": "296 · o fluxo que bate sozinho"},
  {"p": "**Enunciado.** 'intervalo' e uma fonte fria com relogio. Ela e a forma"},
  { code: `// de um painel se atualizar, e por isso precisa de duas coisas: um
// teto opcional de batidas, e um cancelamento que PARA de verdade.
//
// Os testes esperam por CONDICAO, e nao por relogio: um 'sleep' fixo
// mede a maquina, e o mesmo exercicio reprova numa esteira carregada
// sem que nada tenha mudado no codigo.

adopt Arcane.Reativo as R
adopt Arcane.Time as Tempo

steady PASSO := 0.05
steady PRAZO := 5.0

action esperar_ate(condicao):
    "Espera a condicao virar verdadeira, ou desiste no prazo."
    limite := Tempo.timestamp() + PRAZO
    persist Tempo.timestamp() smaller limite:
        given condicao():
            yield yes
        Tempo.sleep(PASSO / 5)
    yield no

out "== 1. ele nao comeca sem ninguem escutando =="

silencioso := R.intervalo(PASSO, quantos := 3)
Tempo.sleep(PASSO * 4)
assert silencioso.inscritos() is 0
out "   passou o tempo de tres batidas, e nada correu"

out ""
out "== 2. com teto, ele termina sozinho =="

batidas := []
fim := []
contado := R.intervalo(PASSO, quantos := 3)
contado.inscrever(lambda n => batidas.append(n), void,
    lambda => fim.append(yes))

assert esperar_ate(lambda => len(fim) is 1)

// A contagem comeca em ZERO, como o 'interval' de todo framework
// reativo: o numero e "quantas ja passaram", e nao "a quantidade".
assert batidas is [0, 1, 2]
out $"   {batidas}"

out ""
out "== 3. sem teto, quem para e o cancelamento =="

livres := []
sempre := R.intervalo(PASSO)
inscricao := sempre.inscrever(lambda n => livres.append(n))

assert esperar_ate(lambda => len(livres) bigger_eq 2)
inscricao.cancelar()
quantas := len(livres)

// Depois de cancelar, o numero nao anda mais — e para PROVAR isso a
// espera precisa ser maior que varias batidas.
Tempo.sleep(PASSO * 5)
assert len(livres) is quantas
out "   cancelada, ela parou de bater"

out ""
out "== 4. o operador vale aqui tambem =="

pares := []
so_pares := R.intervalo(PASSO, quantos := 6).sift(lambda n => n % 2 is 0)
so_pares.inscrever(lambda n => pares.append(n))

assert esperar_ate(lambda => len(pares) is 3)
assert pares is [0, 2, 4]

out "exercicio 296 ok"`, lang: 'df', title: `exercicios/51-reativo/296_intervalo.df` },
  {"p": "`intervalo` é uma fonte fria com relógio: a forma de um painel se atualizar."},
  {"h3": "Ele não começa sem ninguém escutando"},
  {"p": "Um temporizador que roda sem assinante é trabalho jogado fora — e numa thread que ninguém observa."},
  {"h3": "Com teto, ele termina sozinho"},
  {"p": "E avisa o fim. A contagem começa em **zero**, como o `interval` de todo framework reativo: o número é \"quantas já passaram\", e não \"a quantidade\"."},
  {"h3": "Sem teto, quem para é o cancelamento"},
  {"p": "E ele para de verdade: a prova é o número não andar mais depois de uma espera maior que várias batidas."},
  {"h2": "297 · quatro formas de lidar com mudanca"},
  {"p": "**Enunciado.** a linguagem tem 'Arcane.Eventos' (um emissor),"},
  { code: `// 'Arcane.Stream' (topicos com offset), 'stream action' (um gerador
// preguicoso) e agora o reativo. Elas nao resolvem o mesmo problema, e
// escolher a errada e de onde vem metade da complicacao.

adopt Arcane.Reativo as R
adopt Arcane.Eventos as Ev

out "== 1. o emissor: quem escuta recebe o que foi emitido =="

emissor := Ev.emissor()
avisados := []
emissor.ao("pedido.pago", lambda dados => avisados.append(dados["id"]))
emissor.emitir("pedido.pago", {"id": "P-1"})
assert avisados is ["P-1"]

// Pergunta que ele NAO responde: "qual foi o ultimo pedido pago?"
// Ele nao guarda estado.

out ""
out "== 2. o sinal: ele TEM um valor agora =="

ultimo := R.sinal("nenhum")
ultimo.escrever("P-1")
assert ultimo.ler() is "P-1"
out "   a pergunta 'qual e o valor agora?' tem resposta"

out ""
out "== 3. o gerador preguicoso produz sob demanda =="

stream action naturais():
    n := 1
    persist yes:
        emit n
        n += 1

assert naturais().take(4) is [1, 2, 3, 4]
// Quem manda e quem CONSOME. Ninguem e avisado de nada.

out ""
out "== 4. o observavel: um fluxo no tempo, empurrado =="

cliques := R.observavel("cliques")
contados := []
cliques.inscrever(lambda c => contados.append(c))
cliques.emitir("a")
cliques.emitir("b")
assert contados is ["a", "b"]
// Quem manda e quem PRODUZ — e nao ha "valor atual".

out ""
out "== 5. e o derivado e o que nenhum dos outros da =="

// "Este total e sempre a soma daqueles tres" — sem callback, sem
// assinatura, sem recalcular a mao.
a := R.sinal(1)
b := R.sinal(2)
c := R.sinal(3)
steady soma := R.derivado(lambda => a.ler() + b.ler() + c.ler())

assert soma.ler() is 6
b.escrever(20)
assert soma.ler() is 24
out "   ninguem recalculou nada"

out ""
out "== 6. e a ponte entre os dois mundos =="

// Um fluxo vira valor com 'para_sinal'; um valor vira fluxo com
// 'observar'.
fluxo_para_valor := cliques.para_sinal("nenhum")
cliques.emitir("c")
assert fluxo_para_valor.ler() is "c"

do_valor := []
a.observar(lambda v => do_valor.append(v))
a.escrever(9)
assert do_valor is [9]

out "exercicio 297 ok"`, lang: 'df', title: `exercicios/51-reativo/297_reativo_vs_eventos.df` },
  {"p": "A linguagem tem `Arcane.Eventos` (um emissor), `Arcane.Stream` (tópicos com offset), `stream action` (um gerador preguiçoso) e o reativo. Elas não resolvem o mesmo problema, e escolher a errada é de onde vem metade da complicação."},
  {"h3": "O emissor não guarda estado"},
  {"p": "A pergunta *\"qual foi o último pedido pago?\"* não tem resposta nele."},
  {"h3": "O gerador é puxado; o observável é empurrado"},
  {"p": "No primeiro, quem manda é quem consome. No segundo, quem produz."},
  {"h3": "E o derivado é o que nenhum dos outros dá"},
  {"p": "*\"Este total é sempre a soma daqueles três\"* — sem callback, sem assinatura, sem recalcular à mão."},
  {"h3": "As duas pontes"},
  {"p": "`para_sinal` leva o fluxo para o mundo dos valores; `observar` leva o valor para o mundo dos fluxos."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/51-reativo/283_sinal_e_derivado.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '283-um-valor-que-outros-valores-acompanham', text: "283 · um valor que outros valores acompanham", level: 2 as const }, { id: 'ele-so-calcula-quando-alguem-le', text: "Ele só calcula quando alguém lê", level: 3 as const }, { id: 'e-o-valor-fica-memorizado', text: "E o valor fica memorizado", level: 3 as const }, { id: 'escrever-o-mesmo-valor-nao-invalida', text: "Escrever o mesmo valor não invalida", level: 3 as const }, { id: 'e-valor-le-sem-depender', text: "E `.valor()` lê sem depender", level: 3 as const }, { id: '284-a-dependencia-e-descoberta-nao-declarada', text: "284 · a dependencia e DESCOBERTA, nao declarada", level: 2 as const }, { id: 'o-ramo-tomado-decide-a-dependencia', text: "O ramo tomado decide a dependência", level: 3 as const }, { id: 'as-fontes-que-sumiram-param-de-notificar', text: "As fontes que sumiram param de notificar", level: 3 as const }, { id: 'e-voltando-a-dependencia-volta', text: "E voltando, a dependência volta", level: 3 as const }, { id: '285-o-efeito-roda-ao-nascer-e-o-lote-agrupa', text: "285 · o efeito roda ao nascer, e o lote agrupa", level: 2 as const }, { id: 'ele-ja-rodou', text: "Ele já rodou", level: 3 as const }, { id: 'o-lote-agrupa-varias-escritas-numa-notificacao', text: "O lote agrupa várias escritas numa notificação", level: 3 as const }, { id: 'parar-e-definitivo', text: "Parar é definitivo", level: 3 as const }, { id: 'e-um-efeito-sem-dependencia-roda-uma-vez-so', text: "E um efeito sem dependência roda uma vez só", level: 3 as const }, { id: '286-o-valor-que-nunca-existiu', text: "286 · o valor que nunca existiu", level: 2 as const }, { id: 'o-7-nunca-foi-verdade', text: "O 7 nunca foi verdade", level: 3 as const }, { id: 'a-marcacao-percorre-o-grafo-inteiro-primeiro', text: "A marcação percorre o grafo inteiro primeiro", level: 3 as const }, { id: 'e-o-efeito-alcancado-por-dois-caminhos-roda-uma-vez', text: "E o efeito alcançado por dois caminhos roda uma vez", level: 3 as const }, { id: '287-sinal-e-valor-observavel-e-fluxo', text: "287 · sinal e valor; observavel e fluxo", level: 2 as const }, { id: 'quem-se-inscreve-recebe-o-que-vier-daqui-para-a-frente', text: "Quem se inscreve recebe o que vier daqui para a frente", level: 3 as const }, { id: 'os-operadores-tem-os-nomes-do-pipeline', text: "Os operadores têm os nomes do pipeline", level: 3 as const }, { id: 'o-fluxo-vira-valor-quando-a-pergunta-muda', text: "O fluxo vira valor quando a pergunta muda", level: 3 as const }, { id: 'e-encerrar-e-definitivo', text: "E encerrar é definitivo", level: 3 as const }, { id: '288-a-fonte-fria-liga-preguicoso', text: "288 · a fonte fria liga preguicoso", level: 2 as const }, { id: 'a-cadeia-inteira-chega', text: "A cadeia inteira chega", level: 3 as const }, { id: 'sem-ninguem-escutando-nada-corre', text: "Sem ninguém escutando, nada corre", level: 3 as const }, { id: 'e-os-recortes', text: "E os recortes", level: 3 as const }, { id: '289-o-tempo-dentro-do-fluxo', text: "289 · o tempo dentro do fluxo", level: 2 as const }, { id: 'a-diferenca-em-uma-frase', text: "A diferença, em uma frase", level: 3 as const }, { id: 'e-os-dois-existem-pelo-mesmo-motivo', text: "E os dois existem pelo mesmo motivo", level: 3 as const }, { id: 'o-teste-espera-por-condicao', text: "O teste espera por CONDIÇÃO", level: 3 as const }, { id: '290-dois-fluxos-num-so-de-duas-formas', text: "290 · dois fluxos num so, de duas formas", level: 2 as const }, { id: 'combinar-espera-todos-falarem-uma-vez', text: "Combinar espera todos falarem uma vez", level: 3 as const }, { id: 'e-dai-em-diante-qualquer-um-dispara', text: "E daí em diante, qualquer um dispara", level: 3 as const }, { id: 'um-formulario-com-dois-campos', text: "Um formulário com dois campos", level: 3 as const }, { id: '291-a-falha-encerra-o-fluxo', text: "291 · a falha ENCERRA o fluxo", level: 2 as const }, { id: 'falhar-avisa-e-encerra', text: "Falhar avisa E encerra", level: 3 as const }, { id: 'aofalhar-transforma-o-erro-em-valor', text: "`ao_falhar` transforma o erro em VALOR", level: 3 as const }, { id: 'e-um-sinal-nao-tem-erro', text: "E um SINAL não tem erro", level: 3 as const }, { id: '292-o-que-o-grafo-reativo-recusa', text: "292 · o que o grafo reativo recusa", level: 2 as const }, { id: 'um-derivado-que-depende-de-si-mesmo', text: "Um derivado que depende de si mesmo", level: 3 as const }, { id: 'um-derivado-nao-pode-escrever', text: "Um derivado não pode escrever", level: 3 as const }, { id: 'mas-um-efeito-pode', text: "Mas um EFEITO pode", level: 3 as const }, { id: '293-um-carrinho-que-se-recalcula-sozinho', text: "293 · um carrinho que se recalcula sozinho", level: 2 as const }, { id: 'a-isencao-muda-a-dependencia', text: "A isenção muda a dependência", level: 3 as const }, { id: 'o-lote-agrupa-a-montagem-inteira', text: "O lote agrupa a montagem inteira", level: 3 as const }, { id: 'e-as-contas-fecham', text: "E as contas fecham", level: 3 as const }, { id: '294-quando-mudou-nao-e-obvio', text: "294 · quando \"mudou\" nao e obvio", level: 2 as const }, { id: 'dois-clusters-de-mesmo-conteudo-sao-o-mesmo-valor', text: "Dois clusters de mesmo conteúdo são o mesmo valor", level: 3 as const }, { id: 'mudar-a-lista-no-lugar-nao-avisa-ninguem', text: "Mudar a lista NO LUGAR não avisa ninguém", level: 3 as const }, { id: 'e-uma-comparacao-propria', text: "E uma comparação própria", level: 3 as const }, { id: '295-o-reativo-em-cima-de-uma-tabela', text: "295 · o reativo em cima de uma tabela", level: 2 as const }, { id: 'mexer-no-filtro-recalcula-os-dois', text: "Mexer no filtro recalcula os dois", level: 3 as const }, { id: 'nada-recalcula-sem-leitura', text: "Nada recalcula sem leitura", level: 3 as const }, { id: 'e-o-quadro-le-a-mesma-lista', text: "E o quadro lê a mesma lista", level: 3 as const }, { id: '296-o-fluxo-que-bate-sozinho', text: "296 · o fluxo que bate sozinho", level: 2 as const }, { id: 'ele-nao-comeca-sem-ninguem-escutando', text: "Ele não começa sem ninguém escutando", level: 3 as const }, { id: 'com-teto-ele-termina-sozinho', text: "Com teto, ele termina sozinho", level: 3 as const }, { id: 'sem-teto-quem-para-e-o-cancelamento', text: "Sem teto, quem para é o cancelamento", level: 3 as const }, { id: '297-quatro-formas-de-lidar-com-mudanca', text: "297 · quatro formas de lidar com mudanca", level: 2 as const }, { id: 'o-emissor-nao-guarda-estado', text: "O emissor não guarda estado", level: 3 as const }, { id: 'o-gerador-e-puxado-o-observavel-e-empurrado', text: "O gerador é puxado; o observável é empurrado", level: 3 as const }, { id: 'e-o-derivado-e-o-que-nenhum-dos-outros-da', text: "E o derivado é o que nenhum dos outros dá", level: 3 as const }, { id: 'as-duas-pontes', text: "As duas pontes", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"51 · Programação reativa"}
      description={"15 exercícios: ."}
      href={"/docs/exercicios/51-reativo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
