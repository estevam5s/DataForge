// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "54 · Erros e famílias",
  description: "15 exercícios: .",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 54`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[328](#328-capturar-por-familia-e-nao-por-nome)", "**capturar por FAMILIA, e nao por nome**", "sao 208 codigos de erro. Comparar nomes exatos obrigaria"], ["[329](#329-o-que-se-le-de-um-erro-capturado)", "**o que se lê de um erro capturado**", "um erro nao e so uma mensagem. Ele carrega o tipo, a"], ["[330](#330-o-erro-que-o-programa-inventa)", "**o erro que o programa inventa**", "nao ha hierarquia de excecao do usuario, e o que"], ["[331](#331-a-familia-das-colecoes)", "**a familia das colecoes**", "indice, chave e fatia falham de jeitos diferentes, e"], ["[332](#332-converter-o-que-veio-de-fora)", "**converter o que veio de fora**", "todo dado que entra num programa e texto — do formulario,"], ["[333](#333-fechar-o-que-foi-aberto)", "**fechar o que foi aberto**", "'defer' roda na saida da ACAO, onde quer que esteja"], ["[334](#334-insistir-e-saber-quando-parar)", "**insistir, e saber quando parar**", "uma falha de rede e diferente de uma falha de logica. A"], ["[335](#335-a-falha-como-valor)", "**a falha como VALOR**", "um erro interrompe; um resultado nao. Quando a falha e"], ["[336](#336-o-valor-que-nao-serve-para-a-operacao)", "**o valor que nao serve para a operacao**", "a familia dos tipos. O que importa aqui e que nenhuma"], ["[337](#337-o-sistema-de-arquivos-falha-de-seis-jeitos)", "**o sistema de arquivos falha de seis jeitos**", "nao existe, existe e nao e o que se espera, sem"], ["[338](#338-o-erro-que-aparece-na-fronteira)", "**o erro que aparece na FRONTEIRA**", "'requires', 'promises' e 'invariant' movem a falha para"], ["[339](#339-o-erro-que-acontece-em-outra-thread)", "**o erro que acontece em OUTRA thread**", "'parallel' espera todas as tarefas e levanta na linha do"], ["[340](#340-o-que-monitor-nao-pega)", "**o que 'monitor' NAO pega**", "'halt', 'skip' e 'yield' atravessam um 'monitor'. Eles"], ["[341](#341-afirmar-que-algo-falha)", "**afirmar que algo FALHA**", "um teste que so confere o caminho feliz nao prova nada"], ["[342](#342-as-dezoito-familias-e-como-escolher)", "**as dezoito familias, e como escolher**", "fechar o modulo com o mapa. O codigo de um erro diz a"]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "328 · capturar por FAMILIA, e nao por nome"},
  {"p": "**Enunciado.** sao 208 codigos de erro. Comparar nomes exatos obrigaria"},
  { code: `// a listar cada um; a heranca deixa 'handle RuntimeError' pegar os
// vinte da familia, e quem precisa distinguir ainda nomeia o
// especifico.

adopt Arcane.IO as IO

action classe_de(acao):
    monitor:
        acao()
    handle Error as e:
        yield e.type
    yield "nenhum"

out "== 1. cada erro tem a sua classe =="

assert classe_de(lambda => 1 / 0) is "DivisionByZeroError"  // df: permitir division-by-zero
assert classe_de(lambda => [1, 2][9]) is "IndexError"  // df: permitir indice-fora-do-alcance
assert classe_de(lambda => {"a": 1} ["b"]) is "KeyError"  // df: permitir chave-ausente
assert classe_de(lambda => int("nao e numero")) is "ConversionError"
assert classe_de(lambda => IO.read("/nao/existe/mesmo")) is "FileNotFoundError"

out ""
out "== 2. a familia pega todos os filhos =="

action pela_familia(acao, _rotulo):
    monitor:
        acao()
    handle RuntimeError:
        yield "runtime"
    handle Error:
        yield "outro"
    yield "nenhum"

assert pela_familia(lambda => 1 / 0, "divisao") is "runtime"  // df: permitir division-by-zero

out ""
out "== 3. a ORDEM dos handle importa =="

// O primeiro que casa vence. Com 'Error' no topo, nada abaixo dele
// seria alcancado.
qual := ""
monitor:
    _x := 1 / 0  // df: permitir division-by-zero
handle DivisionByZeroError:
    qual := "especifico"
handle RuntimeError:
    qual := "familia"
assert qual is "especifico"

invertido := ""
monitor:
    _x := 1 / 0  // df: permitir division-by-zero
handle RuntimeError:
    invertido := "familia"
handle DivisionByZeroError:
    invertido := "especifico"
assert invertido is "familia"
out "   do especifico ao geral, sempre"

out ""
out "== 4. 'trigger' levanta TriggerError, e nao RuntimeError =="

// E a armadilha mais cara: 'handle RuntimeError' nao pega um
// 'trigger'.
nao_pegou := yes
monitor:
    monitor:
        trigger "minha falha"
    handle RuntimeError:
        nao_pegou := no
handle TriggerError as e:
    assert e.message is "minha falha"
assert nao_pegou

// Para pegar qualquer coisa: 'handle Error'.
pegou := no
monitor:
    trigger "outra"
handle Error:
    pegou := yes
assert pegou

out ""
out "== 5. e 'handle' sem tipo pega tudo =="

sem_tipo := no
monitor:
    trigger "qualquer"
handle:
    sem_tipo := yes
assert sem_tipo

out "exercicio 328 ok"`, lang: 'df', title: `exercicios/54-erros/328_familias.df` },
  {"p": "São mais de duzentos códigos. Comparar nomes exatos obrigaria a listar cada um; a herança deixa `handle RuntimeError` pegar os vinte da família, e quem precisa distinguir ainda nomeia o específico."},
  {"h3": "A ORDEM dos `handle` importa"},
  {"p": "O primeiro que casa vence. Com `Error` no topo, nada abaixo dele seria alcançado — do específico ao geral, sempre."},
  {"h3": "`trigger` levanta `TriggerError`, e não `RuntimeError`"},
  {"p": "É a armadilha mais cara do capítulo: `handle RuntimeError` **não** pega um `trigger`, e o sintoma é \"o tratamento não funcionou\" sem nenhuma pista."},
  {"h3": "E `handle` sem tipo pega tudo"},
  {"p": "Inclusive o que você não queria. Ele serve para o topo do programa, e não para o meio."},
  {"h2": "329 · o que se lê de um erro capturado"},
  {"p": "**Enunciado.** um erro nao e so uma mensagem. Ele carrega o tipo, a"},
  { code: `// linha, a nota, a dica e a doc — e e isso que faz a diferenca entre
// um log que ajuda e um que so diz que algo deu errado.

adopt Arcane.IO as IO

out "== 1. os campos =="

monitor:
    _x := 1 / 0  // df: permitir division-by-zero
handle Error as e:
    assert e.type is "DivisionByZeroError"
    assert "zero" in lower(e.message)
    assert e.line bigger 0
    out $"   {e.type} na linha {e.line}: {e.message}"

out ""
out "== 2. a nota e a dica, quando existem =="

monitor:
    IO.read("/nao/existe/mesmo/nem/um/pouco")
handle FileNotFoundError as e:
    assert len(e.message) bigger 0
    out $"   {e.message}"

out ""
out "== 3. relancar preservando o original =="

action camada_de_baixo():
    trigger "o banco nao respondeu"

action camada_de_cima():
    monitor:
        camada_de_baixo()
    handle Error as e:
        // Embrulhar e a norma; sem a causa, a mensagem de fora diz o
        // QUE falhou e perde o PORQUE.
        trigger $"nao consegui salvar o pedido: {e.message}"

monitor:
    camada_de_cima()
handle Error as e:
    assert "salvar o pedido" in e.message
    assert "banco nao respondeu" in e.message
    out $"   {e.message}"

out ""
out "== 4. 'ensure' roda sempre =="

passos := []

action com_limpeza(vai_falhar):
    monitor:
        passos.append("comecou")
        given vai_falhar:
            trigger "falhou"
        passos.append("terminou")
    handle Error:
        passos.append("tratou")
    ensure:
        passos.append("limpou")

com_limpeza(no)
assert passos is ["comecou", "terminou", "limpou"]

passos := []
com_limpeza(yes)
assert passos is ["comecou", "tratou", "limpou"]

out ""
out "== 5. e 'monitor' SEM 'handle' nao engole =="

escapou := no
monitor:
    monitor:
        trigger "passa direto"
    ensure:
        passos.append("mas o ensure rodou")
handle Error as e:
    escapou := yes
    assert e.message is "passa direto"
assert escapou
assert passos[-1] is "mas o ensure rodou"

out "exercicio 329 ok"`, lang: 'df', title: `exercicios/54-erros/329_o_erro_como_valor.df` },
  {"p": "Um erro não é só uma mensagem: ele carrega o tipo, a linha, a nota, a dica e o código. É isso que faz a diferença entre um log que ajuda e um que só diz que algo deu errado."},
  {"h3": "Relançar preservando o original"},
  {"p": "Embrulhar é a norma; sem a causa, a mensagem de fora diz **o quê** falhou e perde o **porquê**."},
  {"h3": "`ensure` roda sempre"},
  {"p": "Nos dois caminhos, e depois do `handle`."},
  {"h3": "E `monitor` SEM `handle` não engole"},
  {"p": "Ele só garante o `ensure`. O erro continua viajando."},
  {"h2": "330 · o erro que o programa inventa"},
  {"p": "**Enunciado.** nao ha hierarquia de excecao do usuario, e o que"},
  { code: `// substitui e melhor para quem trata — um RECORD com os campos do
// problema. Uma classe vazia so carrega o nome; o record leva o saldo,
// o valor pedido e a diferenca. E 'handle <Nome>' o captura pelo nome.

record SaldoInsuficiente:
    saldo: Float
    pedido: Float

    action falta() -> Float:
        yield self.pedido - self.saldo

record ContaBloqueada:
    conta: String
    motivo: String

record ValorInvalido:
    valor: Float

out "== 1. levantar um record =="

action sacar(saldo, quanto):
    given quanto bigger saldo:
        trigger SaldoInsuficiente(saldo, quanto)
    yield saldo - quanto

assert sacar(100.0, 30.0) is 70.0

out ""
out "== 2. e captura-lo PELO NOME =="

pegou := no
monitor:
    sacar(100.0, 250.0)
handle SaldoInsuficiente as e:
    pegou := yes
    // O valor original viaja em 'e.value': os campos, e nao o texto.
    assert e.value.falta() is 150.0
    out $"   faltam {e.value.falta()}"
assert pegou

out ""
out "== 3. cada nome captura so o seu =="

action transferir(de, quanto, bloqueadas):
    given de in bloqueadas:
        trigger ContaBloqueada(de, "em analise")
    given quanto smaller_eq 0.0:
        trigger ValorInvalido(quanto)
    given quanto bigger 1000.0:
        trigger SaldoInsuficiente(1000.0, quanto)
    yield quanto

action tentar(de, quanto):
    monitor:
        transferir(de, quanto, ["X"])
        yield "ok"
    handle ContaBloqueada as e:
        yield $"bloqueio: {e.value.conta} ({e.value.motivo})"
    handle ValorInvalido as e:
        yield $"valor invalido: {e.value.valor}"
    handle SaldoInsuficiente as e:
        yield $"faltam {e.value.falta()}"

assert tentar("A", 100.0) is "ok"
assert startswith(tentar("X", 100.0), "bloqueio:")
assert startswith(tentar("A", -5.0), "valor invalido:")
assert startswith(tentar("A", 5000.0), "faltam")

cycle caso in [["A", 100.0], ["X", 100.0], ["A", -5.0], ["A", 5000.0]]:
    out $"   {caso[0]} {caso[1]}  ->  {tentar(caso[0], caso[1])}"

out ""
out "== 4. e 'handle Error' continua pegando todos =="

qualquer := ""
monitor:
    sacar(10.0, 20.0)
handle Error as e:
    // O tipo do ERRO continua sendo TriggerError; o nome do record e
    // o que 'handle' casa.
    qualquer := e.type
assert qualquer is "TriggerError"

out ""
out "== 5. 'match' sobre o valor, quando se quer decidir por forma =="

action classificar(falha):
    match falha:
        point SaldoInsuficiente(saldo, pedido):
            yield $"faltam {pedido - saldo}"
        point ContaBloqueada(conta, motivo):
            yield $"{conta}: {motivo}"
        point String as texto:
            yield $"texto: {texto}"
        default:
            yield "desconhecido"

assert classificar(SaldoInsuficiente(10.0, 30.0)) is "faltam 20.0"
assert classificar(ContaBloqueada("X", "em analise")) is "X: em analise"
assert classificar("algo") is "texto: algo"

out ""
out "== 6. um texto levantado NAO ganha nome =="

// Senao 'handle String' capturaria todo 'trigger "..."' do programa.
so_texto := no
monitor:
    monitor:
        trigger "so uma mensagem"
    handle String:
        assert no
handle Error as e:
    so_texto := e.type is "TriggerError"
assert so_texto

out "exercicio 330 ok"`, lang: 'df', title: `exercicios/54-erros/330_erro_do_usuario.df` },
  {"p": "Não há hierarquia de exceção do usuário, e o que substitui é melhor para quem trata: um **record** com os campos do problema. Uma classe vazia só carrega o nome; o record leva o saldo, o valor pedido e a diferença."},
  {"h3": "E `handle <Nome>` o captura pelo nome"},
  {"p": "Isso não funcionava: `_error_matches` consultava `tipo_usuario` e **nada** o escrevia. O ramo existia, tinha docstring, e era inalcançável — quem levantava um record só podia capturá-lo com `handle Error` e um `match`."},
  {"h3": "O valor original viaja em `e.value`"},
  {"p": "Os campos, e não o texto. Extrair por regex o que o programa já tinha como dado é o que isso evita."},
  {"h3": "E um texto levantado NÃO ganha nome"},
  {"p": "Senão `handle String` capturaria todo `trigger \"…\"` do programa."},
  {"h2": "331 · a familia das colecoes"},
  {"p": "**Enunciado.** indice, chave e fatia falham de jeitos diferentes, e"},
  { code: `// cada um tem uma saida diferente. Tratar os tres com o mesmo
// 'handle Error' e o que faz um bug de chave virar "algo deu errado".

out "== 1. indice fora do alcance =="

xs := [10, 20, 30]

monitor:
    _x := xs[9]
handle IndexError as e:
    assert "9" in e.message or "range" in lower(e.message)
    out $"   {e.message}"

// A saida: conferir o tamanho, ou usar o indice negativo.
assert xs[-1] is 30
assert(xs[9] given len(xs) bigger 9 otherwise void) is void

out ""
out "== 2. chave ausente =="

v := {"nome": "Ana", "cidade": "Florianopolis"}

monitor:
    _x := v["idade"]  // df: permitir chave-ausente
handle KeyError as e:
    out $"   {e.message}"

// A saida: '??' — e e ela que o proprio erro sugere.
assert(v["idade"] ?? 0) is 0
assert v["nome"] ?? "sem nome" is "Ana"

out ""
out "== 3. e a diferenca entre 'pop' e 'remove' =="

// 'remove' apaga no lugar e e silencioso quando nao acha.
copia := {"a": 1, "b": 2}
remove(copia, "z")
assert keys(copia) is ["a", "b"]

// 'pop' devolve o valor e por isso LEVANTA: devolver void calado
// esconderia a diferenca entre "a chave valia void" e "a chave nao
// estava la".
levantou := no
monitor:
    pop(copia, "z")
handle Error:
    levantou := yes
assert levantou
assert pop(copia, "a") is 1

out ""
out "== 4. num cluster, o segundo argumento e o VALOR =="

lista := [1, 2, 3]
remove(lista, 2)
assert lista is [1, 3]

vault := {"x": 1, "y": 2}
remove(vault, "x")
assert keys(vault) is ["y"]

out ""
out "== 5. 'omit' devolve copia, e nao mexe no original =="

steady ORIGINAL := {"a": 1, "b": 2, "c": 3}
sem_b := omit(ORIGINAL, "b")
assert keys(sem_b) is ["a", "c"]
assert keys(ORIGINAL) is ["a", "b", "c"]

out ""
out "== 6. e uma colecao congelada recusa a escrita =="

congelada := freeze([1, 2, 3])
recusou := no
monitor:
    congelada.append(4)
handle Error as e:
    recusou := yes
assert recusou
assert len(congelada) is 3

out "exercicio 331 ok"`, lang: 'df', title: `exercicios/54-erros/331_erros_de_colecao.df` },
  {"p": "Índice, chave e fatia falham de jeitos diferentes, e cada um tem uma saída diferente. Tratar os três com o mesmo `handle Error` é o que faz um bug de chave virar \"algo deu errado\"."},
  {"h3": "`remove` e `pop` mudam de sentido"},
  {"p": "Num cluster o segundo argumento é o **valor**; num vault, a **chave**. `remove` é silencioso; `pop` **levanta** — devolver `void` calado esconderia a diferença entre \"a chave valia `void`\" e \"a chave não estava lá\"."},
  {"h3": "`omit` devolve cópia"},
  {"p": "E não mexe no original."},
  {"h3": "E o `??` é a saída que o próprio erro sugere"},
  {"p": "Um analisador que acusasse o conserto que ele mesmo recomenda é um analisador que se desliga."},
  {"h2": "332 · converter o que veio de fora"},
  {"p": "**Enunciado.** todo dado que entra num programa e texto — do formulario,"},
  { code: `// do CSV, da variavel de ambiente. Converter e onde ele falha, e
// converter em silencio e onde ele mente.

adopt Arcane.Serialization as Serde

out "== 1. a conversao que falha =="

monitor:
    int("quarenta e dois")
handle ConversionError as e:
    out $"   {e.message}"

assert int("42") is 42
assert float("3.5") is 3.5

out ""
out "== 2. converter com um padrao, sem esconder o erro =="

action para_inteiro(texto, padrao):
    monitor:
        yield int(texto)
    handle ConversionError:
        yield padrao

assert para_inteiro("42", 0) is 42
assert para_inteiro("x", 0) is 0

out ""
out "== 3. a diferenca entre nao informado e invalido =="

// Um padrao silencioso junta os dois casos, e o relatorio sai com
// zeros que ninguem sabe de onde vieram.
action ler_idade(texto):
    given texto is void or trim(texto) is "":
        yield {"ok": yes, "valor": void, "motivo": "nao informado"}
    monitor:
        yield {"ok": yes, "valor": int(texto), "motivo": ""}
    handle ConversionError:
        yield {"ok": no, "valor": void, "motivo": $"'{texto}' nao e um numero"}

assert ler_idade("30")["valor"] is 30
assert ler_idade("")["ok"] and ler_idade("")["valor"] is void
assert not ler_idade("trinta")["ok"]
out $"   {ler_idade('trinta')['motivo']}"

out ""
out "== 4. um formulario inteiro, com os erros juntos =="

steady CAMPOS := [["idade", "30"], ["altura", "1,75"], ["peso", "70.5"]]

erros := []
valores := {}
cycle campo in CAMPOS:
    monitor:
        valores[campo[0]] := float(campo[1])
    handle ConversionError:
        erros.append($"{campo[0]}: '{campo[1]}' nao e um numero")

assert len(erros) is 1
assert "altura" in erros[0]
assert valores["peso"] is 70.5
out $"   {erros[0]}"

// Juntar os erros e devolver todos de uma vez e melhor que parar no
// primeiro: quem preenche corrige tudo numa passada.

out ""
out "== 5. JSON invalido =="

assert Serde.from_json('{"a": 1}')["a"] is 1

quebrou := no
monitor:
    Serde.from_json("{isto nao e json}")
handle Error as e:
    quebrou := yes
    out $"   {e.type}"
assert quebrou

out ""
out "== 6. e a conversao que NAO e recusada e a mais perigosa =="

// Float aceita notacao cientifica e infinito.
assert float("1e400") bigger 1000000.0
assert int("0") is 0
out "   'int' e 'float' aceitam mais do que um formulario deveria"

out "exercicio 332 ok"`, lang: 'df', title: `exercicios/54-erros/332_erros_de_conversao.df` },
  {"p": "Todo dado que entra num programa é texto — do formulário, do CSV, da variável de ambiente. Converter é onde ele falha, e converter em silêncio é onde ele **mente**."},
  {"h3": "A diferença entre não informado e inválido"},
  {"p": "Um padrão silencioso junta os dois casos, e o relatório sai com zeros que ninguém sabe de onde vieram."},
  {"h3": "Juntar os erros e devolver todos"},
  {"p": "Melhor que parar no primeiro: quem preenche corrige tudo numa passada."},
  {"h3": "E a conversão que NÃO é recusada é a mais perigosa"},
  {"p": "`float` aceita notação científica e infinito — mais do que um formulário deveria."},
  {"h2": "333 · fechar o que foi aberto"},
  {"p": "**Enunciado.** 'defer' roda na saida da ACAO, onde quer que esteja"},
  { code: `// escrito — dentro de um cycle, de um persist, ou no topo. E ele NAO
// engole: um erro dentro dele viaja, e se a acao ja estava falhando,
// viaja o ORIGINAL com o do defer em 'e.outros'.

adopt Arcane.IO as IO
adopt Arcane.OS as OS

steady pasta := $"{OS.temp_dir()}/df-333-{randint(100000, 999999)}"
IO.mkdir(pasta)

ordem := []

out "== 1. ele roda na saida da acao =="

action com_defer():
    defer:
        ordem.append("fechou")
    ordem.append("trabalhou")
    yield "pronto"

assert com_defer() is "pronto"
assert ordem is ["trabalhou", "fechou"]

out ""
out "== 2. e roda tambem quando a acao FALHA =="

ordem := []

action falha_com_defer():
    defer:
        ordem.append("fechou mesmo assim")
    trigger "quebrou no meio"

monitor:
    falha_com_defer()
handle Error:
    ordem.append("tratado")
assert ordem is ["fechou mesmo assim", "tratado"]

out ""
out "== 3. num laco, ele acumula e roda TUDO no fim =="

// Ele se registrava no escopo em que aparece, e so o da acao era
// consultado: um 'defer' num laco NUNCA rodava, calado — e fechar
// arquivo por volta e o uso mais obvio que existe. Hoje ele roda, e
// roda na SAIDA DA ACAO, na ordem inversa do registro.
ordem := []

action num_laco():
    cycle i from 1 to 3:
        defer:
            ordem.append($"fecha {i}")
        ordem.append($"abre {i}")

num_laco()
assert ordem is ["abre 1", "abre 2", "abre 3", "fecha 3", "fecha 2", "fecha 1"]
out $"   {ordem}"

// A consequencia pratica: num laco de dez mil voltas, dez mil
// arquivos ficam abertos ate a acao terminar. Quem precisa fechar por
// VOLTA extrai o corpo para uma acao propria — e ai a saida dela e o
// fim do 'defer'.
por_volta := []

action uma_volta(i):
    defer:
        por_volta.append($"fecha {i}")
    por_volta.append($"abre {i}")

cycle i from 1 to 3:
    uma_volta(i)

assert por_volta is ["abre 1", "fecha 1", "abre 2", "fecha 2",
    "abre 3", "fecha 3"]
out $"   por acao: {por_volta}"

out ""
out "== 4. um arquivo por volta, fechado por volta =="

action gravar_tres():
    cycle i from 1 to 3:
        caminho := $"{pasta}/parte-{i}.txt"
        defer:
            ordem.append($"salvou {i}")
        IO.write(caminho, $"conteudo {i}")

ordem := []
gravar_tres()
assert len(ordem) is 3
cycle i from 1 to 3:
    assert IO.exists($"{pasta}/parte-{i}.txt")

out ""
out "== 5. o defer NAO engole o erro dele =="

action defer_que_quebra():
    defer:
        quebrar()
    yield "voltei"

action quebrar():
    trigger "o fechamento falhou"

viajou := no
monitor:
    defer_que_quebra()
handle Error as e:
    viajou := yes
    assert "fechamento falhou" in e.message
assert viajou
out "   um arquivo nao fechado nao termina o programa com codigo 0"

out ""
out "== 6. e quando os DOIS falham, viaja o original =="

action os_dois():
    defer:
        quebrar()
    trigger "o erro de verdade"

monitor:
    os_dois()
handle Error as e:
    // E o modelo do try-with-resources: o original manda, e o do
    // fechamento vai junto.
    assert "o erro de verdade" in e.message
    assert len(e.outros) bigger_eq 1
    out $"   original: {e.message} · junto: {len(e.outros)}"

IO.remove_tree(pasta)
out "exercicio 333 ok"`, lang: 'df', title: `exercicios/54-erros/333_defer_e_recurso.df` },
  {"p": "`defer` roda na saída da **ação**, onde quer que esteja escrito."},
  {"h3": "Num laço, ele acumula e roda tudo no fim"},
  {"p": "Na ordem inversa do registro. A consequência prática: num laço de dez mil voltas, dez mil arquivos ficam abertos até a ação terminar. Quem precisa fechar por **volta** extrai o corpo para uma ação própria."},
  {"h3": "Ele NÃO engole o erro dele"},
  {"p": "Um erro dentro do `defer` viaja. Até a correção era descartado, e um arquivo não fechado terminava o programa com código **0**."},
  {"h3": "E quando os dois falham, viaja o original"},
  {"p": "Com o do fechamento em `e.outros` — é o modelo do try-with-resources."},
  {"h2": "334 · insistir, e saber quando parar"},
  {"p": "**Enunciado.** uma falha de rede e diferente de uma falha de logica. A"},
  { code: `// primeira costuma passar na segunda tentativa; a segunda passa a
// vida inteira falhando. Insistir na errada esconde o bug.

adopt Arcane.Time as Tempo

out "== 1. um retry a mao =="

tentativas := {"n": 0}

action instavel(falhar_ate):
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] smaller_eq falhar_ate:
        trigger $"falha transitoria {tentativas['n']}"
    yield $"ok na tentativa {tentativas['n']}"

action insistir(acao, vezes):
    ultimo := ""
    cycle i from 1 to vezes:
        monitor:
            yield acao()
        handle Error as e:
            ultimo := e.message
    trigger $"desisti depois de {vezes}: {ultimo}"

assert insistir(lambda => instavel(2), 5) is "ok na tentativa 3"
assert tentativas["n"] is 3

out ""
out "== 2. e ele desiste, dizendo o ultimo motivo =="

tentativas["n"] := 0
desistiu := no
monitor:
    insistir(lambda => instavel(99), 3)
handle Error as e:
    desistiu := yes
    assert "desisti depois de 3" in e.message
    assert "falha transitoria 3" in e.message
    out $"   {e.message}"
assert desistiu

out ""
out "== 3. o recuo com TREMOR =="

// Sem jitter, todos os clientes que falharam juntos voltam juntos — e
// o servico cai de novo no mesmo instante.
action recuo(tentativa, base):
    espera := base * (2 ** (tentativa - 1))
    yield espera + random() * base

esperas := [recuo(i, 0.01) cycle i in range(1, 5)]
assert esperas[0] smaller esperas[3]
assert len(unique([round(recuo(1, 0.01), 6) cycle i in range(5)])) bigger 1
out "   quatro tentativas, esperas crescentes e diferentes entre si"

out ""
out "== 4. o que NAO se repete =="

// Um erro de logica repete identico. Repetir aqui e gastar tempo e
// esconder o bug.
action nao_vale_repetir():
    x := [1, 2]
    yield x[9]  // df: permitir indice-fora-do-alcance

sempre := 0
cycle i from 1 to 3:
    monitor:
        nao_vale_repetir()
    handle IndexError:
        sempre += 1
assert sempre is 3
out "   tres tentativas, tres vezes o MESMO erro"

out ""
out "== 5. distinguir as duas familias =="

steady REPETIVEIS := ["ConnectionError", "TimeoutError", "NetworkError"]

action vale_repetir(tipo):
    yield tipo in REPETIVEIS

assert vale_repetir("TimeoutError")
assert not vale_repetir("IndexError")
assert not vale_repetir("ConversionError")

out ""
out "== 6. e um prazo total, alem do numero de tentativas =="

action insistir_ate(acao, prazo):
    limite := Tempo.timestamp() + prazo
    ultimo := ""
    persist Tempo.timestamp() smaller limite:
        monitor:
            yield acao()
        handle Error as e:
            ultimo := e.message
    trigger $"prazo esgotado: {ultimo}"

tentativas["n"] := 0
assert insistir_ate(lambda => instavel(1), 2.0) is "ok na tentativa 2"

out "exercicio 334 ok"`, lang: 'df', title: `exercicios/54-erros/334_retry_e_prazo.df` },
  {"p": "Uma falha de rede é diferente de uma falha de lógica. A primeira costuma passar na segunda tentativa; a segunda passa a vida inteira falhando — e insistir nela esconde o bug."},
  {"h3": "O recuo com TREMOR"},
  {"p": "Sem *jitter*, todos os clientes que falharam juntos voltam juntos — e o serviço cai de novo no mesmo instante."},
  {"h3": "O que NÃO se repete"},
  {"p": "Um erro de lógica repete idêntico. Três tentativas, três vezes o mesmo erro."},
  {"h3": "E um prazo total, além do número de tentativas"},
  {"p": "Cinco tentativas de dez segundos são cinquenta segundos de espera para quem está do outro lado."},
  {"h2": "335 · a falha como VALOR"},
  {"p": "**Enunciado.** um erro interrompe; um resultado nao. Quando a falha e"},
  { code: `// ESPERADA — um CEP que nao existe, um arquivo que pode faltar —
// levantar obriga quem chama a montar um 'monitor' em volta de cada
// chamada, e o codigo some dentro do tratamento.

adopt Arcane.Resultado as Res

out "== 1. ok e falha =="

action dividir(a, b):
    given b is 0:
        yield Res.falha("divisao por zero")
    yield Res.ok(a / b)

bom := dividir(10, 2)
assert bom.deu_certo()
assert bom.valor() is 5.0

ruim := dividir(10, 0)
assert ruim.falhou()
assert ruim.erro() is "divisao por zero"
out $"   {ruim.erro()}"

out ""
out "== 2. encadear sem 'monitor' em cada passo =="

action metade(x):
    yield dividir(x, 2)

action mais_um(x):
    yield Res.ok(x + 1)

passo := dividir(20, 2).entao(metade).entao(mais_um)
assert passo.valor() is 6.0

// E a falha ATRAVESSA sem que ninguem confira no meio.
quebrado := dividir(20, 0).entao(metade).entao(mais_um)
assert quebrado.falhou()
assert quebrado.erro() is "divisao por zero"
out "   a falha atravessou tres passos sem um 'given' sequer"

out ""
out "== 3. mapear muda o VALOR, e nao o desfecho =="

assert dividir(10, 2).mapear(lambda v => v * 10).valor() is 50.0
assert dividir(10, 0).mapear(lambda v => v * 10).falhou()

out ""
out "== 4. o padrao de saida =="

assert dividir(10, 0).ou(-1.0) is -1.0
assert dividir(10, 2).ou(-1.0) is 5.0

// E a recuperacao, que transforma a falha em outro resultado.
recuperado := dividir(10, 0).recuperar(lambda _e => Res.ok(0.0))
assert recuperado.valor() is 0.0

out ""
out "== 5. a hora de voltar para o mundo dos erros =="

// Na fronteira do programa, um resultado vira erro — porque ai nao ha
// mais quem trate.
levantou := no
monitor:
    dividir(1, 0).exigir()
handle Error as e:
    levantou := yes
    assert "divisao por zero" in e.message
assert levantou

out ""
out "== 6. 'tentar' embrulha uma acao que LEVANTA =="

// E a ponte no outro sentido: transformar um erro em resultado.
assert Res.tentar(lambda => 1 / 0).falhou()  // df: permitir division-by-zero
assert Res.tentar(lambda => 10 / 2).valor() is 5.0

out ""
out "== 7. 'Talvez', para onde 'void' e ambiguo =="

// 'void' nao distingue "nao achei" de "achei, e o valor e void".
steady CACHE := {"a": 1, "b": void}

action buscar(chave):
    given chave not in CACHE:
        yield Res.nada()
    yield Res.algo(CACHE[chave])

assert buscar("a").tem()
assert buscar("b").tem()  // achei, e o valor e void
assert buscar("z").vazio()  // nao achei
out "   'b' existe e vale void; 'z' nao existe"

out ""
out "== 8. e todos/primeiro, para uma lista de resultados =="

steady VARIOS := [dividir(10, 2), dividir(10, 0), dividir(20, 4)]
assert len(Res.erros(VARIOS)) is 1
assert Res.todos(VARIOS).falhou()

steady SO_BONS := [dividir(10, 2), dividir(20, 4)]
assert Res.todos(SO_BONS).valor() is [5.0, 5.0]

out ""
out "== 9. quando usar cada um =="

out "   falha ESPERADA (CEP invalido, arquivo opcional): Resultado"
out "   falha EXCEPCIONAL (disco cheio, bug):            trigger"

out "exercicio 335 ok"`, lang: 'df', title: `exercicios/54-erros/335_resultado_como_valor.df` },
  {"p": "Um erro interrompe; um resultado não. Quando a falha é **esperada** — um CEP que não existe, um arquivo que pode faltar — levantar obriga quem chama a montar um `monitor` em volta de cada chamada, e o código some dentro do tratamento."},
  {"h3": "A falha atravessa a cadeia sem um `given` sequer"},
  {"p": "`entao` só chama o próximo quando o anterior deu certo."},
  {"h3": "E a hora de voltar para o mundo dos erros"},
  {"p": "Na fronteira do programa, `exigir()` transforma o resultado em erro — porque ali não há mais quem trate. E `tentar` é a ponte no outro sentido."},
  {"h3": "`Talvez`, para onde `void` é ambíguo"},
  {"p": "`void` não distingue \"não achei\" de \"achei, e o valor é `void`\"."},
  {"h3": "Quando usar cada um"},
  {"p": "Falha **esperada**: `Resultado`. Falha **excepcional** (disco cheio, bug): `trigger`."},
  {"h2": "336 · o valor que nao serve para a operacao"},
  {"p": "**Enunciado.** a familia dos tipos. O que importa aqui e que nenhuma"},
  { code: `// mensagem cita tipo do Python: 'int', 'str', 'list' e 'dict' nao
// existem nesta linguagem, e uma mensagem nesses termos manda a pessoa
// procurar na documentacao errada.

out "== 1. somar o que nao soma =="

monitor:
    x := 1 + "dois"
handle TypeError as e:
    assert "int" not in e.message
    assert "str" not in e.message
    out $"   {e.message}"

out ""
out "== 2. os nomes sao os DESTA linguagem =="

assert typeof(1) is "Integer"
assert typeof(1.5) is "Float"
assert typeof("x") is "String"
assert typeof([1]) is "Cluster"
assert typeof({"a": 1}) is "Vault"
assert typeof(yes) is "Boolean"
assert typeof(void) is "Void"
assert typeof((1, "a")) is "Tuple"

out ""
out "== 3. chamar o que nao e acao =="

monitor:
    x := 42
    x()
handle Error as e:
    out $"   {e.type}"

out ""
out "== 4. indexar o que nao e indexavel =="

monitor:
    y := 42
    _z := y[0]  // df: permitir index-type
handle Error as e:
    assert "Integer" in e.message or "index" in lower(e.message)
    out $"   {e.message}"

out ""
out "== 5. o void que atravessa =="

// 'void' nao levanta na hora: ele viaja, e a queixa sai longe da
// causa. E por isso que '?.' e '??' existem.
action pode_nao_achar(chave):
    given chave is "a":
        yield {"nome": "Ana"}
    yield void

achado := pode_nao_achar("z")
assert achado is void

monitor:
    _nome := achado["nome"]
handle Error as e:
    out $"   {e.message}"

// As duas saidas:
assert(achado?.nome) is void
assert(pode_nao_achar("z") ?? {"nome": "desconhecido"})["nome"] is "desconhecido"

out ""
out "== 6. e a aridade errada e recusada na chamada =="

action somar(a, b):
    yield a + b

// 'somar(1)' e acusado pelo 'check' ANTES de rodar — e por isso nao
// da para escreve-lo aqui sem o arquivo inteiro ser recusado. A forma
// que so falha em execucao e a chamada indireta.
chamar := somar
monitor:
    chamar(1)
handle TypeError as e:
    assert "b" in e.message
    out $"   {e.message}"

monitor:
    chamar(1, 2, 3)
handle TypeError as e:
    out $"   {e.message}"

out "exercicio 336 ok"`, lang: 'df', title: `exercicios/54-erros/336_erros_de_tipo.df` },
  {"p": "O que importa aqui é que **nenhuma mensagem cita tipo do Python**: `int`, `str`, `list` e `dict` não existem nesta linguagem, e uma mensagem nesses termos manda a pessoa procurar na documentação errada."},
  {"h3": "Os nomes são os DESTA linguagem"},
  {"p": "`Integer`, `Cluster`, `Vault`, `Boolean`, `Void`, `Tuple`."},
  {"h3": "O `void` que atravessa"},
  {"p": "Ele não levanta na hora: viaja, e a queixa sai longe da causa. É por isso que `?.` e `??` existem."},
  {"h3": "E a aridade errada é recusada na chamada"},
  {"p": "E antes dela, quando o `check` consegue provar."},
  {"h2": "337 · o sistema de arquivos falha de seis jeitos"},
  {"p": "**Enunciado.** nao existe, existe e nao e o que se espera, sem"},
  { code: `// permissao, e uma pasta onde se queria um arquivo. Tratar os quatro
// como "erro de IO" e o que faz um log dizer "falhou" e nada mais.

adopt Arcane.IO as IO
adopt Arcane.OS as OS

steady pasta := $"{OS.temp_dir()}/df-337-{randint(100000, 999999)}"
IO.mkdir(pasta)
steady arquivo := $"{pasta}/dados.txt"
IO.write(arquivo, "conteudo")

out "== 1. nao existe =="

monitor:
    IO.read($"{pasta}/nao-existe.txt")
handle FileNotFoundError as e:
    out $"   {e.type}"

out ""
out "== 2. e uma pasta onde se queria arquivo =="

monitor:
    IO.read(pasta)
handle Error as e:
    out $"   {e.type}"

out ""
out "== 3. conferir ANTES e melhor do que tratar depois =="

action ler_se_der(caminho):
    given not IO.exists(caminho):
        yield {"ok": no, "motivo": "o arquivo nao existe"}
    given caminho in [pasta]:
        yield {"ok": no, "motivo": "isto e uma pasta"}
    monitor:
        yield {"ok": yes, "texto": IO.read(caminho)}
    handle Error as e:
        yield {"ok": no, "motivo": e.message}

assert ler_se_der(arquivo)["texto"] is "conteudo"
assert ler_se_der($"{pasta}/x")["motivo"] is "o arquivo nao existe"
assert ler_se_der(pasta)["motivo"] is "isto e uma pasta"

// Mas conferir e depois usar tem uma janela entre os dois: o arquivo
// pode sumir nesse intervalo. Por isso o 'monitor' continua ali.
out "   conferir nao dispensa tratar: ha uma janela entre os dois"

out ""
out "== 4. escrever numa pasta que nao existe =="

monitor:
    IO.write($"{pasta}/sem/pasta/x.txt", "x")
handle Error as e:
    out $"   {e.type}"

// A saida: criar a arvore antes.
IO.mkdir($"{pasta}/sub")
IO.write($"{pasta}/sub/x.txt", "x")
assert IO.exists($"{pasta}/sub/x.txt")

out ""
out "== 5. o defer garante a limpeza =="

action trabalhar_com_temporario():
    temporario := $"{pasta}/temp-{randint(1000, 9999)}.txt"
    defer:
        given IO.exists(temporario):
            IO.delete(temporario)
    IO.write(temporario, "rascunho")
    assert IO.exists(temporario)
    trigger "falhou depois de criar"

monitor:
    trabalhar_com_temporario()
handle Error:
    out "   falhou, e o temporario foi apagado"

sobraram := [f cycle f in IO.list_dir(pasta) given startswith(f, "temp-")]
assert len(sobraram) is 0

out ""
out "== 6. e o que NAO se deve fazer =="

// 'IO.remove_tree(OS.temp_dir())' destroi o temporario de TODO
// processo da maquina. Sempre uma subpasta propria.
assert startswith(pasta, OS.temp_dir())
assert pasta isnt OS.temp_dir()

IO.remove_tree(pasta)
assert not IO.exists(pasta)
out "exercicio 337 ok"`, lang: 'df', title: `exercicios/54-erros/337_erros_de_arquivo.df` },
  {"p": "Não existe, existe e não é o que se espera, sem permissão, e uma pasta onde se queria um arquivo. Tratar todos como \"erro de IO\" é o que faz um log dizer \"falhou\" e nada mais."},
  {"h3": "Conferir antes NÃO dispensa tratar"},
  {"p": "Há uma janela entre os dois: o arquivo pode sumir nesse intervalo."},
  {"h3": "O `defer` garante a limpeza"},
  {"p": "Inclusive no caminho de erro — que é o caminho em que o temporário costuma ficar para trás."},
  {"h3": "E o que NÃO se deve fazer"},
  {"p": "`IO.remove_tree(OS.temp_dir())` destrói o temporário de **todo** processo da máquina. Sempre uma subpasta própria."},
  {"h2": "338 · o erro que aparece na FRONTEIRA"},
  {"p": "**Enunciado.** 'requires', 'promises' e 'invariant' movem a falha para"},
  { code: `// onde ela e compreensivel. Sem eles, um argumento errado vira uma
// conta errada tres chamadas adiante, e a queixa fala de outra coisa.

blueprint Conta:
    saldo := 0.0

    invariant self.saldo bigger_eq 0.0

    action setup(inicial):
        self.saldo := inicial

    action sacar(quanto):
        expects quanto bigger 0.0
        promises outcome smaller_eq before(self.saldo)
        self.saldo := self.saldo - quanto
        yield self.saldo

    action depositar(quanto):
        expects quanto bigger 0.0
        self.saldo := self.saldo + quanto
        yield self.saldo

out "== 1. o caminho feliz =="

c := spawn Conta(100.0)
assert c.sacar(30.0) is 70.0
assert c.depositar(10.0) is 80.0

out ""
out "== 2. a pre-condicao acusa QUEM CHAMOU =="

// Sem ela, 'sacar(-50)' AUMENTA o saldo, e o erro aparece no extrato.
pre := no
monitor:
    c.sacar(-50.0)
handle PreconditionError as e:
    pre := yes
    out $"   {e.message}"
assert pre
assert c.saldo is 80.0

out ""
out "== 3. a invariante acusa o OBJETO =="

inv := no
monitor:
    c.sacar(999.0)
handle InvariantError as e:
    inv := yes
    out $"   {e.message}"
assert inv

out ""
out "== 4. as duas dizem coisas diferentes =="

// 'PreconditionError' = o argumento esta errado.
// 'InvariantError'    = o objeto chegou a um estado que nao pode existir.
out "   precondicao: o erro e de quem chamou"
out "   invariante:  o erro e do objeto"

out ""
out "== 5. e a pos-condicao confere o RESULTADO =="

blueprint Quebrada:
    valor := 0

    action dobrar(x):
        promises outcome bigger x
        yield x - 1  // mente sobre o que promete

q := spawn Quebrada()
pos := no
monitor:
    q.dobrar(10)
handle PostconditionError as e:
    pos := yes
    out $"   {e.message}"
assert pos

out ""
out "== 6. a familia dos contratos =="

action classe_de(acao):
    monitor:
        acao()
    handle Error as e:
        yield e.type
    yield "nenhum"

assert classe_de(lambda => c.sacar(-1.0)) is "PreconditionError"
assert classe_de(lambda => q.dobrar(1)) is "PostconditionError"

// E 'handle ContractError' pega os tres.
pela_base := no
monitor:
    c.sacar(-1.0)
handle ContractError:
    pela_base := yes
assert pela_base

out "exercicio 338 ok"`, lang: 'df', title: `exercicios/54-erros/338_contrato_e_invariante.df` },
  {"p": "`expects`, `promises` e `invariant` movem a falha para onde ela é compreensível. Sem eles, um argumento errado vira uma conta errada três chamadas adiante, e a queixa fala de outra coisa."},
  {"h3": "As três dizem coisas diferentes"},
  {"p": "`PreconditionError` = o argumento está errado, e a culpa é de quem chamou. `PostconditionError` = a ação mentiu sobre o que promete. `InvariantError` = o objeto chegou a um estado que não pode existir."},
  {"h3": "Sem a pré-condição, `sacar(-50)` AUMENTA o saldo"},
  {"p": "E o erro aparece no extrato, semanas depois."},
  {"h3": "E `handle ContractError` pega as três"},
  {"p": "Quando a distinção não importa para quem trata."},
  {"h2": "339 · o erro que acontece em OUTRA thread"},
  {"p": "**Enunciado.** 'parallel' espera todas as tarefas e levanta na linha do"},
  { code: `// bloco, com as demais falhas em '.outros' — entao um 'monitor' o
// pega. 'thread' nao espera: o erro e desenhado na hora, e o programa
// termina com codigo diferente de zero.

adopt Arcane.Concurrent as Conc

out "== 1. 'parallel' espera todas =="

resultados := []

action trabalhar(n):
    resultados.append(n)

parallel:
    trabalhar(1)
    trabalhar(2)
    trabalhar(3)

assert len(resultados) is 3
out $"   tres tarefas, {len(resultados)} resultados"

out ""
out "== 2. e o erro de uma delas CHEGA ao monitor =="

// Ate a correcao, os dois faziam 'except Exception' e imprimiam uma
// linha: o programa seguia, saia com 0, e nenhum 'handle' via o erro.
action quebrar(qual):
    trigger $"tarefa {qual} falhou"

pegou := no
monitor:
    parallel:
        trabalhar(9)
        quebrar("A")
handle Error as e:
    pegou := yes
    assert "falhou" in e.message
    out $"   {e.message}"
assert pegou

out ""
out "== 3. varias falhas: a primeira manda, as outras vao junto =="

monitor:
    parallel:
        quebrar("A")
        quebrar("B")
        quebrar("C")
handle Error as e:
    out $"   uma na mensagem, {len(e.outros)} em '.outros'"
    assert len(e.outros) bigger_eq 1

out ""
out "== 4. a linguagem NAO sincroniza sozinha =="

// Duas threads escrevendo no mesmo nome perdem atualizacoes, em
// silencio. E o 'check' avisa sobre o padrao — mas avisar nao e
// sincronizar.
solto := {"n": 0}

action somar_sem_trava(voltas):
    cycle i from 1 to voltas:
        atual := solto["n"]
        solto["n"] := atual + 1

steady THREADS := 4
steady VOLTAS := 3000

parallel:
    somar_sem_trava(VOLTAS)
    somar_sem_trava(VOLTAS)
    somar_sem_trava(VOLTAS)
    somar_sem_trava(VOLTAS)

esperado := THREADS * VOLTAS
out $"   sem mutex: {solto['n']} de {esperado}"
assert solto["n"] smaller_eq esperado

out ""
out "== 5. com mutex, fecha =="

protegido := {"n": 0}
steady trava := Conc.mutex()

action somar_com_trava(voltas):
    cycle i from 1 to voltas:
        trava.acquire()
        protegido["n"] := protegido["n"] + 1
        trava.release()

parallel:
    somar_com_trava(VOLTAS)
    somar_com_trava(VOLTAS)
    somar_com_trava(VOLTAS)
    somar_com_trava(VOLTAS)

assert protegido["n"] is esperado
out $"   com mutex: {protegido['n']} de {esperado}"

out ""
out "== 6. e o que o GIL protege sozinho =="

// 'append' de varias threads entrega tudo: o GIL protege a operacao
// inteira, e avisar sobre ele seria falso alarme em codigo que
// funciona. O que perde e ler-modificar-escrever.
juntos := []

action acrescentar(voltas):
    cycle i from 1 to voltas:
        juntos.append(i)

parallel:
    acrescentar(1000)
    acrescentar(1000)

assert len(juntos) is 2000
out "   'append' de duas threads: 2000 de 2000"

out "exercicio 339 ok"`, lang: 'df', title: `exercicios/54-erros/339_erros_de_concorrencia.df` },
  {"p": "`parallel` espera todas as tarefas e levanta na linha do bloco, com as demais falhas em `.outros` — então um `monitor` o pega."},
  {"h3": "Até a correção, os dois engoliam"},
  {"p": "`thread` e `parallel` faziam `except Exception` e imprimiam uma linha: o programa seguia, saía com **0**, e nenhum `handle` via o erro. Um CI passava verde com metade do trabalho perdida."},
  {"h3": "A linguagem NÃO sincroniza sozinha"},
  {"p": "Duas threads escrevendo no mesmo nome perdem atualizações, em silêncio. O `check` **avisa** sobre o padrão — mas avisar não é sincronizar."},
  {"h3": "E o que o GIL protege sozinho"},
  {"p": "`append` de várias threads entrega tudo: o GIL protege a operação inteira, e avisar sobre ele seria falso alarme em código que funciona. O que perde é ler-modificar-escrever."},
  {"h2": "340 · o que 'monitor' NAO pega"},
  {"p": "**Enunciado.** 'halt', 'skip' e 'yield' atravessam um 'monitor'. Eles"},
  { code: `// derivam de um sinal de controle, e nao de erro — capturar um 'yield'
// com 'handle' faria uma acao devolver o tratamento em vez do valor.

out "== 1. 'yield' atravessa =="

action com_monitor():
    monitor:
        yield "voltei de dentro do monitor"
    handle Error:
        yield "NAO DEVIA"

assert com_monitor() is "voltei de dentro do monitor"

out ""
out "== 2. e o 'ensure' AINDA roda =="

passos := []

action sai_de_dentro():
    monitor:
        passos.append("entrou")
        yield "saiu"
    ensure:
        passos.append("limpou")

assert sai_de_dentro() is "saiu"
assert passos is ["entrou", "limpou"]

out ""
out "== 3. 'halt' atravessa =="

encontrados := []

action procurar(xs, alvo):
    cycle x in xs:
        monitor:
            given x is alvo:
                halt
            encontrados.append(x)
        handle Error:
            encontrados.append("erro")
    yield encontrados

assert procurar([1, 2, 3, 4], 3) is [1, 2]

out ""
out "== 4. 'skip' tambem =="

pares := []
cycle i from 1 to 6:
    monitor:
        given i % 2 is 1:
            skip
        pares.append(i)
    handle Error:
        pares.append(-1)
assert pares is [2, 4, 6]

out ""
out "== 5. e por isso um 'handle' generico nao os engole =="

// Num interpretador que capturasse tudo, o 'halt' viraria uma
// mensagem de erro e o laco continuaria — o defeito mais confuso que
// existe, porque o codigo LE certo.
contou := 0
cycle i from 1 to 10:
    monitor:
        given i bigger 3:
            halt
        contou += 1
    handle:
        contou := -100
assert contou is 3

out ""
out "== 6. o que 'monitor' PEGA =="

// Tudo que deriva de Error. E um 'monitor' sem 'handle' nao engole
// nada: ele so garante o 'ensure'.
escapou := no
monitor:
    monitor:
        trigger "passa direto"
    ensure:
        passos.append("mesmo assim")
handle Error:
    escapou := yes
assert escapou
assert passos[-1] is "mesmo assim"

out "exercicio 340 ok"`, lang: 'df', title: `exercicios/54-erros/340_erro_que_atravessa.df` },
  {"p": "`halt`, `skip` e `yield` atravessam um `monitor`. Eles derivam de um sinal de controle, e não de erro."},
  {"h3": "Capturar um `yield` faria a ação devolver o tratamento"},
  {"p": "Em vez do valor. E o `ensure` **ainda** roda — a saída é garantida sem que o sinal seja engolido."},
  {"h3": "Num interpretador que capturasse tudo"},
  {"p": "O `halt` viraria uma mensagem de erro e o laço continuaria — o defeito mais confuso que existe, porque o código **lê** certo."},
  {"h3": "E `monitor` sem `handle` não engole nada"},
  {"p": "Ele só garante o `ensure`."},
  {"h2": "341 · afirmar que algo FALHA"},
  {"p": "**Enunciado.** um teste que so confere o caminho feliz nao prova nada"},
  { code: `// sobre o tratamento. Afirmar a falha e tao importante quanto afirmar
// o sucesso — e afirmar a falha ERRADA e pior que nao afirmar.

adopt Arcane.Crucible as Crucible

steady expect := Crucible.expect

action sacar(saldo, quanto):
    given quanto smaller_eq 0.0:
        trigger ValorInvalido(quanto)
    given quanto bigger saldo:
        trigger SaldoInsuficiente(saldo, quanto)
    yield saldo - quanto

record ValorInvalido:
    valor: Float

record SaldoInsuficiente:
    saldo: Float
    pedido: Float

out "== 1. afirmar que levanta =="

expect(lambda => sacar(100.0, 250.0)).to_raise()
expect(lambda => sacar(100.0, 30.0)).to_not_raise()

out ""
out "== 2. e afirmar QUAL levanta =="

// Sem isto, um teste passa quando a acao falha pelo motivo errado —
// e o motivo errado costuma ser um erro de digitacao no proprio
// teste.
qual := ""
monitor:
    sacar(100.0, -5.0)
handle ValorInvalido:
    qual := "valor"
handle SaldoInsuficiente:
    qual := "saldo"
assert qual is "valor"

out ""
out "== 3. o teste que passa pelo motivo errado =="

// O nome errado vem de um vault, e nao de uma variavel solta: assim
// ele e o mesmo defeito — um erro de digitacao que so aparece em
// execucao — sem o 'check' recusar o arquivo inteiro, que e o que ele
// faz quando o nome nao existe em lugar nenhum.
steady LIMITES := {"saldo": 100.0}

action com_erro_de_digitacao(saldo, quanto):
    given quanto bigger LIMITES["sald"]:  // 'sald' nao existe
        trigger SaldoInsuficiente(saldo, quanto)
    yield saldo - quanto

// 'to_raise' sozinho passaria: a acao levanta mesmo — de NameError.
expect(lambda => com_erro_de_digitacao(100.0, 250.0)).to_raise()

// Conferindo o tipo, o teste reprova como deveria.
tipo := ""
monitor:
    com_erro_de_digitacao(100.0, 250.0)
handle Error as e:
    tipo := e.type
assert tipo is "KeyError"
assert tipo isnt "TriggerError"
out "   'to_raise' sozinho aprova um teste que deveria falhar"

out ""
out "== 4. conferir a mensagem =="

monitor:
    sacar(10.0, 999.0)
handle SaldoInsuficiente as e:
    assert e.value.pedido is 999.0
    assert e.value.saldo is 10.0

out ""
out "== 5. um caso de borda por vez =="

steady CASOS := [
    [100.0, 100.0, "ok"],
    [100.0, 100.01, "falta"],
    [100.0, 0.0, "invalido"],
    [0.0, 1.0, "falta"]
]

action classificar(saldo, quanto):
    monitor:
        sacar(saldo, quanto)
        yield "ok"
    handle ValorInvalido:
        yield "invalido"
    handle SaldoInsuficiente:
        yield "falta"

cycle caso in CASOS:
    obtido := classificar(caso[0], caso[1])
    assert obtido is caso[2], $"{caso[0]}/{caso[1]}: esperava {caso[2]}, veio {obtido}"
    out $"   {caso[0]} - {caso[1]}  ->  {obtido}"

out "exercicio 341 ok"`, lang: 'df', title: `exercicios/54-erros/341_erros_no_teste.df` },
  {"p": "Um teste que só confere o caminho feliz não prova nada sobre o tratamento. E afirmar a falha **errada** é pior que não afirmar."},
  {"h3": "`to_raise` sozinho aprova um teste que deveria falhar"},
  {"p": "Uma ação com erro de digitação levanta mesmo — de `NameError`. O teste passa, e a regra que ele deveria cobrir nunca foi exercitada."},
  {"h3": "Conferir o tipo é o que separa os dois"},
  {"p": "E o motivo errado costuma ser um erro de digitação no próprio teste."},
  {"h3": "E um caso de borda por vez"},
  {"p": "A tabela de casos diz o esperado ao lado do entrado, e a mensagem do `assert` diz qual linha falhou."},
  {"h2": "342 · as dezoito familias, e como escolher"},
  {"p": "**Enunciado.** fechar o modulo com o mapa. O codigo de um erro diz a"},
  { code: `// familia, e a familia diz de quem e a culpa — que e a unica pergunta
// que importa quando um log chega as tres da manha.

out "== 1. o codigo carrega a familia =="

action codigo_de(acao):
    monitor:
        acao()
    handle Error as e:
        yield e.codigo
    yield ""

// DF02xx = execucao, DF06xx = colecoes, DF15xx = validacao.
assert startswith(codigo_de(lambda => 1 / 0), "DF02")  // df: permitir division-by-zero
assert startswith(codigo_de(lambda => [1][9]), "DF06")  // df: permitir indice-fora-do-alcance
out $"   1/0 -> {codigo_de(lambda => 1 / 0)}"  // df: permitir division-by-zero

out ""
out "== 2. as dezoito familias =="

steady FAMILIAS := {
    "01": "sintaxe — o texto nao vira programa",
    "02": "execucao — o programa roda e falha",
    "03": "tipos — o valor nao serve para a operacao",
    "04": "nomes — o nome nao existe, ou nao ali",
    "05": "modulos — adopt e relay",
    "06": "colecoes — indice, chave, fatia",
    "07": "do usuario — trigger e assert",
    "08": "limites — recursao, memoria, tempo",
    "09": "objetos — blueprint, record, trait, enum",
    "10": "concorrencia — thread, canal, async",
    "11": "sistema — arquivo, processo, ambiente",
    "12": "dados — banco, ORM, serializacao",
    "13": "rede — HTTP, Kiln, socket",
    "14": "testes — Crucible",
    "15": "validacao — conversao, formato, contrato",
    "16": "dominio — DDD: valor, agregado, evento, regra",
    "17": "reativo — sinal, derivado, efeito, observavel",
    "18": "memoria estruturada — layout, ponteiro, janela"
}

assert len(keys(FAMILIAS)) is 18
cycle chave in ["02", "16", "17", "18"]:
    out $"   DF{chave}xx  {FAMILIAS[chave]}"

out ""
out "== 3. de quem e a culpa =="

steady CULPA := {
    "PreconditionError": "quem chamou",
    "PostconditionError": "a acao",
    "InvariantError": "o objeto",
    "ConversionError": "o dado que entrou",
    "FileNotFoundError": "o ambiente",
    "TimeoutError": "o outro lado",
    "AggregateError": "a regra de negocio"
}

assert CULPA["PreconditionError"] is "quem chamou"
assert CULPA["InvariantError"] is "o objeto"
out "   um log que nao responde isso nao serve a ninguem"

out ""
out "== 4. a escada de tratamento =="

// Do mais especifico ao mais geral, e cada degrau com uma acao
// diferente.
action tratar(acao):
    monitor:
        acao()
        yield "ok"
    handle ConversionError:
        yield "pedir de novo ao usuario"
    handle FileNotFoundError:
        yield "criar o arquivo e tentar"
    handle RuntimeError:
        yield "registrar e seguir"
    handle Error:
        yield "registrar e PARAR"

assert tratar(lambda => int("x")) is "pedir de novo ao usuario"
assert tratar(lambda => 1 / 0) is "registrar e seguir"  // df: permitir division-by-zero
assert tratar(lambda => trigger "x") is "registrar e PARAR"
assert tratar(lambda => 1 + 1) is "ok"

out ""
out "== 5. as tres decisoes que este modulo ensinou =="

out "   1. capture pela FAMILIA, e nomeie o especifico quando precisar"
out "   2. falha esperada e VALOR (Resultado); falha excepcional e 'trigger'"
out "   3. o que fecha recurso vai em 'defer' — e ele nao engole nada"

out ""
out "== 6. e a que mais custa caro =="

// 'trigger' levanta TriggerError, e nao RuntimeError. 'handle
// RuntimeError' nao pega um 'trigger' — e esse e o erro que aparece
// como "o tratamento nao funcionou" sem nenhuma pista.
nao_pegou := yes
monitor:
    monitor:
        trigger "minha falha"
    handle RuntimeError:
        nao_pegou := no
handle TriggerError:
    void
assert nao_pegou
out "   'handle RuntimeError' NAO pega um 'trigger'"

out "exercicio 342 ok"`, lang: 'df', title: `exercicios/54-erros/342_o_mapa_dos_erros.df` },
  {"p": "O código de um erro diz a família, e a família diz **de quem é a culpa** — que é a única pergunta que importa quando um log chega às três da manhã."},
  {"h3": "Dezoito famílias"},
  {"p": "Das três primeiras (sintaxe, execução, tipos) às três últimas (domínio, reativo, memória estruturada)."},
  {"h3": "A escada de tratamento"},
  {"p": "Do mais específico ao mais geral, e cada degrau com uma **ação** diferente: pedir de novo, criar e tentar, registrar e seguir, registrar e parar."},
  {"h3": "E a que mais custa caro"},
  {"p": "`handle RuntimeError` **não** pega um `trigger`."},
  {"p": "---"},
  {"p": "As três decisões que o módulo ensina: capture pela família e nomeie o específico quando precisar; falha esperada é **valor**, falha excepcional é `trigger`; e o que fecha recurso vai em `defer` — que não engole nada."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/54-erros/328_familias.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '328-capturar-por-familia-e-nao-por-nome', text: "328 · capturar por FAMILIA, e nao por nome", level: 2 as const }, { id: 'a-ordem-dos-handle-importa', text: "A ORDEM dos `handle` importa", level: 3 as const }, { id: 'trigger-levanta-triggererror-e-nao-runtimeerror', text: "`trigger` levanta `TriggerError`, e não `RuntimeError`", level: 3 as const }, { id: 'e-handle-sem-tipo-pega-tudo', text: "E `handle` sem tipo pega tudo", level: 3 as const }, { id: '329-o-que-se-le-de-um-erro-capturado', text: "329 · o que se lê de um erro capturado", level: 2 as const }, { id: 'relancar-preservando-o-original', text: "Relançar preservando o original", level: 3 as const }, { id: 'ensure-roda-sempre', text: "`ensure` roda sempre", level: 3 as const }, { id: 'e-monitor-sem-handle-nao-engole', text: "E `monitor` SEM `handle` não engole", level: 3 as const }, { id: '330-o-erro-que-o-programa-inventa', text: "330 · o erro que o programa inventa", level: 2 as const }, { id: 'e-handle-nome-o-captura-pelo-nome', text: "E `handle <Nome>` o captura pelo nome", level: 3 as const }, { id: 'o-valor-original-viaja-em-evalue', text: "O valor original viaja em `e.value`", level: 3 as const }, { id: 'e-um-texto-levantado-nao-ganha-nome', text: "E um texto levantado NÃO ganha nome", level: 3 as const }, { id: '331-a-familia-das-colecoes', text: "331 · a familia das colecoes", level: 2 as const }, { id: 'remove-e-pop-mudam-de-sentido', text: "`remove` e `pop` mudam de sentido", level: 3 as const }, { id: 'omit-devolve-copia', text: "`omit` devolve cópia", level: 3 as const }, { id: 'e-o-e-a-saida-que-o-proprio-erro-sugere', text: "E o `??` é a saída que o próprio erro sugere", level: 3 as const }, { id: '332-converter-o-que-veio-de-fora', text: "332 · converter o que veio de fora", level: 2 as const }, { id: 'a-diferenca-entre-nao-informado-e-invalido', text: "A diferença entre não informado e inválido", level: 3 as const }, { id: 'juntar-os-erros-e-devolver-todos', text: "Juntar os erros e devolver todos", level: 3 as const }, { id: 'e-a-conversao-que-nao-e-recusada-e-a-mais-perigosa', text: "E a conversão que NÃO é recusada é a mais perigosa", level: 3 as const }, { id: '333-fechar-o-que-foi-aberto', text: "333 · fechar o que foi aberto", level: 2 as const }, { id: 'num-laco-ele-acumula-e-roda-tudo-no-fim', text: "Num laço, ele acumula e roda tudo no fim", level: 3 as const }, { id: 'ele-nao-engole-o-erro-dele', text: "Ele NÃO engole o erro dele", level: 3 as const }, { id: 'e-quando-os-dois-falham-viaja-o-original', text: "E quando os dois falham, viaja o original", level: 3 as const }, { id: '334-insistir-e-saber-quando-parar', text: "334 · insistir, e saber quando parar", level: 2 as const }, { id: 'o-recuo-com-tremor', text: "O recuo com TREMOR", level: 3 as const }, { id: 'o-que-nao-se-repete', text: "O que NÃO se repete", level: 3 as const }, { id: 'e-um-prazo-total-alem-do-numero-de-tentativas', text: "E um prazo total, além do número de tentativas", level: 3 as const }, { id: '335-a-falha-como-valor', text: "335 · a falha como VALOR", level: 2 as const }, { id: 'a-falha-atravessa-a-cadeia-sem-um-given-sequer', text: "A falha atravessa a cadeia sem um `given` sequer", level: 3 as const }, { id: 'e-a-hora-de-voltar-para-o-mundo-dos-erros', text: "E a hora de voltar para o mundo dos erros", level: 3 as const }, { id: 'talvez-para-onde-void-e-ambiguo', text: "`Talvez`, para onde `void` é ambíguo", level: 3 as const }, { id: 'quando-usar-cada-um', text: "Quando usar cada um", level: 3 as const }, { id: '336-o-valor-que-nao-serve-para-a-operacao', text: "336 · o valor que nao serve para a operacao", level: 2 as const }, { id: 'os-nomes-sao-os-desta-linguagem', text: "Os nomes são os DESTA linguagem", level: 3 as const }, { id: 'o-void-que-atravessa', text: "O `void` que atravessa", level: 3 as const }, { id: 'e-a-aridade-errada-e-recusada-na-chamada', text: "E a aridade errada é recusada na chamada", level: 3 as const }, { id: '337-o-sistema-de-arquivos-falha-de-seis-jeitos', text: "337 · o sistema de arquivos falha de seis jeitos", level: 2 as const }, { id: 'conferir-antes-nao-dispensa-tratar', text: "Conferir antes NÃO dispensa tratar", level: 3 as const }, { id: 'o-defer-garante-a-limpeza', text: "O `defer` garante a limpeza", level: 3 as const }, { id: 'e-o-que-nao-se-deve-fazer', text: "E o que NÃO se deve fazer", level: 3 as const }, { id: '338-o-erro-que-aparece-na-fronteira', text: "338 · o erro que aparece na FRONTEIRA", level: 2 as const }, { id: 'as-tres-dizem-coisas-diferentes', text: "As três dizem coisas diferentes", level: 3 as const }, { id: 'sem-a-pre-condicao-sacar-50-aumenta-o-saldo', text: "Sem a pré-condição, `sacar(-50)` AUMENTA o saldo", level: 3 as const }, { id: 'e-handle-contracterror-pega-as-tres', text: "E `handle ContractError` pega as três", level: 3 as const }, { id: '339-o-erro-que-acontece-em-outra-thread', text: "339 · o erro que acontece em OUTRA thread", level: 2 as const }, { id: 'ate-a-correcao-os-dois-engoliam', text: "Até a correção, os dois engoliam", level: 3 as const }, { id: 'a-linguagem-nao-sincroniza-sozinha', text: "A linguagem NÃO sincroniza sozinha", level: 3 as const }, { id: 'e-o-que-o-gil-protege-sozinho', text: "E o que o GIL protege sozinho", level: 3 as const }, { id: '340-o-que-monitor-nao-pega', text: "340 · o que 'monitor' NAO pega", level: 2 as const }, { id: 'capturar-um-yield-faria-a-acao-devolver-o-tratamento', text: "Capturar um `yield` faria a ação devolver o tratamento", level: 3 as const }, { id: 'num-interpretador-que-capturasse-tudo', text: "Num interpretador que capturasse tudo", level: 3 as const }, { id: 'e-monitor-sem-handle-nao-engole-nada', text: "E `monitor` sem `handle` não engole nada", level: 3 as const }, { id: '341-afirmar-que-algo-falha', text: "341 · afirmar que algo FALHA", level: 2 as const }, { id: 'toraise-sozinho-aprova-um-teste-que-deveria-falhar', text: "`to_raise` sozinho aprova um teste que deveria falhar", level: 3 as const }, { id: 'conferir-o-tipo-e-o-que-separa-os-dois', text: "Conferir o tipo é o que separa os dois", level: 3 as const }, { id: 'e-um-caso-de-borda-por-vez', text: "E um caso de borda por vez", level: 3 as const }, { id: '342-as-dezoito-familias-e-como-escolher', text: "342 · as dezoito familias, e como escolher", level: 2 as const }, { id: 'dezoito-familias', text: "Dezoito famílias", level: 3 as const }, { id: 'a-escada-de-tratamento', text: "A escada de tratamento", level: 3 as const }, { id: 'e-a-que-mais-custa-caro', text: "E a que mais custa caro", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"54 · Erros e famílias"}
      description={"15 exercícios: ."}
      href={"/docs/exercicios/54-erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
