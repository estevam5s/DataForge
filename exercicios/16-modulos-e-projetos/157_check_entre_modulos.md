# 157 — O que o `check` pega através do `adopt`

## Por que isto é o que mais importa em escala

Num arquivo de 40 linhas, um erro aparece na primeira execução. Num
sistema de 200 arquivos, **a maioria das chamadas atravessa módulo** — e
é ali que um erro sobrevive até produção.

O `check` lê o outro `.df` com o lexer e o parser, e **nunca o executa**:
analisar não pode ter efeito colateral.

## As quatro coisas que ele prova

```dataforge
adopt ./loja as L

p := L.criar("CAF", "Cafe")

out p.nomee              // has no field 'nomee' — Did you mean 'nome'?
L.criar("CAF")           // takes 2 argument(s), got 1
L.apagar("CAF")          // module 'L' has no 'apagar'
L.criar("CAF", 42)       // 'nome' expects String but got Integer
```

O primeiro e o quarto **dependem das declarações de tipo**:

| No módulo importado | Dá ao analisador |
|---|---|
| `action criar(…) -> Produto` | o tipo do valor que volta, e com ele os campos |
| `action criar(sku: String, …)` | o que cada argumento deve ser |

Sem elas, o analisador cala — ele só acusa o que consegue **provar**.

É isso que torna a anotação de tipo valer a pena. Num arquivo só, ela
documenta. Atravessando módulo, ela é a diferença entre um erro achado
em 0,4 s e um erro achado em produção.

## Dentro de uma ação — onde o código vive

A inferência de tipo usa o escopo de **quem chama**. Usar o escopo
global fazia `L.criar(sku, nome)` dentro de `action f(sku, nome)` virar
**"Undefined name 'sku'"** — 649 falsos alarmes num projeto gerado de
252 arquivos, um por cada uso de parâmetro numa chamada entre módulos.

E os testes passavam: eles chamavam no **nível de topo**, onde o escopo
global é o certo. O bug só aparecia dentro de uma ação.

Quem pegou foi rodar o `check` no projeto grande. É a mesma lição de
sempre: comparar contra uma fonte de verdade, não reler o código.

## O que o faz calar, e por que isso importa igual

```dataforge
x := L.sem_tipo("qualquer coisa")   // 'action sem_tipo(x)' — sem tipo
out x.campo_que_nao_existe          // passa, e está certo passar
```

Um falso alarme ensina a ignorar mensagens — e aí os verdadeiros também
são ignorados. A calibragem atual é **zero erros** em 333 arquivos
conhecidamente bons do repositório.

Ele também cala **inteiro** quando a superfície do outro arquivo não é
confiável:

| Cala quando | Porque |
|---|---|
| o outro arquivo **não compila** | é problema dele, e o `check` sobre ele vai dizer isso |
| há **ciclo de import** | seguir entraria em laço |
| a profundidade (4 níveis) acaba | o custo cresce e o ganho não |
| o `relay` nomeia algo calculado | o conteúdo só existe em execução |

O item 7 do exercício prova o primeiro: um `adopt` de um arquivo
quebrado, seguido de uma chamada inventada, **não é acusado**. Acusar
ali seria culpar o inocente.

## A armadilha de `OS.temp_dir()`

Este exercício escreve arquivos para conferir o `check`, e a primeira
versão fazia isto:

```dataforge
pasta := OS.temp_dir()      // a pasta do SISTEMA
…
IO.remove_tree(pasta)       // apaga o temporário de TODOS os processos
```

`OS.temp_dir()` devolve `/var/folders/…/T` — compartilhada com toda a
máquina. Escrever direto nela deixa lixo; apagá-la no fim destrói o
temporário dos outros programas. O certo é uma subpasta com nome único:

```dataforge
pasta := $"{OS.temp_dir()}/df-157-{randint(100000, 999999)}"
IO.mkdir(pasta)
```

## Rodar o `check` de dentro de um `.df`

```dataforge
adopt Arcane.Process as Proc

r := Proc.run(["dataforge", "check", caminho])
saida := r["stdout"] + r["stderr"]
```

`Proc.run` devolve um vault com `stdout`, `stderr` e `code`. Note que
`"sem erros"` **contém** a palavra `erro` — conferir a ausência dela
contradiz a conferência do sucesso, e foi o que a primeira versão deste
exercício fez.
