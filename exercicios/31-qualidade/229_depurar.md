# 229 — Depurar sem `out`

## Por que não `out`

`out` no meio do código é o depurador mais usado do mundo, e tem três
defeitos:

| Defeito | Consequência |
|---|---|
| muda o que você está medindo | o `out` num laço apertado altera o tempo que você queria medir |
| tem de ser removido depois | e o que sobrar vira ruído na saída de produção |
| só mostra o que você pensou em imprimir | o valor que explica o bug é justamente o que você não suspeitou |

O terceiro é o pior. Um depurador mostra **tudo que está vivo** naquele
ponto, incluindo o que você não sabia que precisava ver.

## O que este exercício exercita

O depurador interativo precisa de um terminal (`dataforge debug`) ou de
um editor (F5). Nenhum dos dois cabe num `assert`. O que cabe — e é o
que este exercício cobra — são as informações em que ele se apoia, e
que a linguagem entrega ao programa:

```dataforge
monitor:
    media([])
handle Error as e:
    out e.type       // "DivisionByZeroError"
    out e.line       // 22 — a linha do yield, onde nasceu
    out e.pilha      // quem chamou quem
```

## `e.pilha` — quem chamou quem

Numa ação chamada de cinco lugares, *"deu erro em `media()`"* não ajuda:
o que importa é **qual** das cinco chamadas.

```dataforge
handle Error as e:
    nomes := [q["name"] cycle q in e.pilha]
    assert nomes is ["nivel1", "nivel2", "nivel3"]
```

Do **mais externo para o mais interno** — a ordem em que se lê "quem
chamou quem", e a mesma em que o stack trace desenha. Inverter aqui
faria o programa e a tela discordarem sobre a mesma pilha.

Cada quadro é um vault com `name`, `line`, `column` e `file`. O `file`
é o que faz a pilha servir num projeto de 200 arquivos.

`e.stack` é o mesmo — o nome em inglês, para quem já conhece a palavra.

## As duas linhas, e as duas estão certas

É a confusão mais comum ao ler uma pilha:

| Campo | O que é |
|---|---|
| `e.line` | onde o erro **nasceu** |
| `quadro["line"]` | onde a **chamada** foi feita |

```dataforge
monitor:
    media([])            // ← quadro["line"] aponta para cá
handle Error as e:
    assert e.line is 22  // ← dentro de 'media', no 'yield'
    assert e.pilha[0]["line"] bigger e.line
```

Números diferentes, de propósito. Para **consertar** você quer o
primeiro; para entender **por que** aquela ação foi chamada com aquele
argumento, o segundo.

Um erro numa ação declarada num arquivo e chamada de outro já reportou
a linha certa com o **nome do arquivo errado** — e o trecho desenhado
embaixo da seta vinha do arquivo de quem chamou. Isso manda a pessoa
depurar o arquivo errado, e é o pior tipo de mensagem de erro: confiante
e errada.

## `handle RuntimeError` não pega um `trigger`

A armadilha 18, e ela aparece neste exercício de propósito:

```dataforge
action nivel1():
    monitor:
        yield nivel2()
    handle RuntimeError:
        yield "nao passa por aqui"      // nunca roda
```

`trigger` levanta `TriggerError`. Para pegar qualquer coisa, `handle
Error`. Um `handle` do tipo errado é invisível: o código parece tratar
o erro, e o erro passa por cima dele.

## `defer` mostra sem sujar o caminho de saída

Um `out` antes de cada `yield` precisa ser repetido em **cada** saída da
ação — e a que você esquecer é justamente a que dá errado.

```dataforge
action classificar(n):
    defer:
        saidas.append($"classificar({n}) saiu")
    given n smaller 0:
        yield "negativo"
    given n is 0:
        yield "zero"
    yield "positivo"
```

Três saídas diferentes, três registros, nenhum esquecido. `defer` abre
**bloco** — não aceita expressão na mesma linha.

## O depurador de verdade

Quando você tem terminal ou editor:

```bash
dataforge debug conta.df              # para na primeira instrução
dataforge debug conta.df --parar=42   # só na linha 42
```

Dentro dele: `p` passo, `n` próximo, `f` sai da ação, `c` continua,
`vars` lista o escopo, `pilha` mostra quem chamou quem — e **qualquer
expressão** é avaliada no quadro onde você parou.

No VS Code, clique na margem e aperte **F5**. Os breakpoints, a pilha,
as variáveis em árvore e o console de avaliação ficam no painel. O
adaptador é `dataforge dap`, que fala Debug Adapter Protocol — o mesmo
protocolo do Neovim, do Helix e do Emacs.

Duas coisas que o depurador faz e que não são óbvias:

- **uma parada em comentário é movida** para a próxima linha executável,
  e o painel mostra onde ficou. Uma parada que nunca dispara, mostrada
  acesa, é o pior dos dois mundos;
- **as 228 embutidas não aparecem** no painel de variáveis. Elas vivem
  no escopo global, e despejá-las enterra as três variáveis que você
  parou para ver.
