# Exercicio 217 — A ponte para o Python

## Enunciado

Use uma biblioteca Python de dentro do DataForge, e faça o programa
continuar funcionando quando ela não estiver instalada.

## Conceitos

```dataforge
adopt Python.numpy as np              // o módulo inteiro
adopt Python.numpy.linalg as la       // um submódulo
adopt Python.json.{loads, dumps}      // só os nomes que interessam
adopt {sqrt} from Python.math         // a ordem invertida também vale
```

Não há palavra reservada nova. `Python` é um **espaço de nomes
reservado**, resolvido antes da biblioteca padrão e antes dos arquivos
vizinhos — um `Python.df` no disco não sequestra o import.

## Para que serve

Uma linguagem que não alcança biblioteca nenhuma é uma ilha: toda
capacidade nova precisa ser reescrita do zero. O DataForge **roda sobre
Python** e não alcançava nada dele. Esta é a porta.

## A ponte não converte

Um `ndarray` continua um `ndarray`:

```dataforge
adopt Python.numpy as np

a := np.array([1, 2, 3, 4])
out a * 2 + 1        // [3 5 7 9] — conta vetorizada do numpy
```

Se a ponte copiasse, `a * 2` viraria um laço sobre um cluster de um
milhão de posições, e a razão de usar numpy desapareceria.

Isso funciona porque o interpretador trata objeto estranho pelo que ele
**faz**, não pelo que ele é — membro, método, índice, `len`, iteração,
aritmética, texto e verdade já passavam por protocolo.

O preço é que o vocabulário vaza em dois lugares, e os dois são
deliberados:

| | `typeof` responde | Por quê |
|---|---|---|
| tupla do Python | `tuple` | ela indexa e percorre, mas não tem `append` |
| `ndarray` | `ndarray` | é o que ele é |
| `np.int64` | **`Integer`** | ele *faz* conta de inteiro |

O último é a exceção que prova a regra: `given typeof(x) is "Integer"`
seria falso para um valor que soma, divide e compara como um. A regra
vem do protocolo `numbers` do Python — não há nada de numpy dentro do
interpretador, e `Fraction` e `Decimal` entram pela mesma porta.

## Perguntar antes de depender

```dataforge
adopt Arcane.Ponte as Ponte

dados := [4.0, 8.0, 15.0, 16.0]
media := 0.0

given Ponte.tem("statistics"):
    adopt Python.statistics as st
    media := st.mean(dados)
otherwise:
    media := (dados >> distill a, v: a + v 0) / len(dados)
```

O `media := 0.0` antes do `given` não é enfeite: cada ramo tem o
próprio escopo, e o que nasce dentro não vaza para fora.

## Explorar de dentro da linguagem

| | Faz |
|---|---|
| `Ponte.atributos(x)` | os nomes públicos de um módulo ou objeto |
| `Ponte.doc(x)` | a documentação que o Python carrega no objeto |
| `Ponte.assinatura(x)` | como se chama, ou `void` se o Python não declara |
| `Ponte.tipo(x)` | o nome do tipo **do lado de lá** |
| `Ponte.cluster(x)` / `Ponte.vault(x)` | converte, explicitamente |
| `Ponte.tem(nome)` / `Ponte.versao(nome)` | sem levantar erro |
| `Ponte.onde()` / `Ponte.empacotado()` | qual Python está por trás |

`Ponte.assinatura` devolve `void` para função escrita em C que não
declara os argumentos. Inventar `(…)` faria você achar que a função não
tem nenhum.

## Quando o pacote não está lá

A mensagem responde as três perguntas que você vai ter, nesta ordem: o
que faltou, **em qual Python** faltou, e o comando exato para aquele
Python.

O caminho importa: o instalador cria uma venv em `~/.dataforge`. Quem
roda `pip install pandas` no terminal instala no Python do **sistema**,
que é outro, e o `adopt` continua falhando sem que nada explique.

E o `dataforge check` avisa antes de rodar, porque ele consegue
**provar** que o pacote não está aqui.

> **O executável único não tem `pip`.** Ele traz um Python próprio e
> nunca vai instalar pacote nenhum. A mensagem diz isso com todas as
> letras, em vez de sugerir um comando que não funcionaria.

## O que a ponte não protege

`adopt Python.os` roda o código de inicialização do pacote, exatamente
como um `import` faria. **Não há sandbox**, e fingir que há seria pior
que não ter.

Isso não acrescenta uma categoria de risco — a linguagem já tem
`Arcane.Process.run` e escrita em disco. O que a ponte faz é tornar a
fronteira **visível na linha do `adopt`**.

## A promessa de zero dependências continua inteira

Nada em `dataforge/` importa nada de fora. O que muda é que o **programa
de quem escreve** passa a poder escolher as suas — a mesma distinção
entre "o Python não depende do numpy" e "o seu script pode depender".

## Saída esperada

```
o Python por tras: python3
math instalado?   yes
xyz123 instalado? no

pm.gcd(12, 18) = 6

{"nome": "Ana", "notas": [9, 8, 10]}

reduce com uma acao daqui: 15

media: 10.75

json tem 'dumps'? yes
assinatura: gcd(*integers)
doc: Return the integer part of the square root of the input.

typeof da tupla:  tuple
typeof convertido: Cluster

erro do Python, capturado aqui: ValueError

ok
```

## Experimente

- `Ponte.atributos` num pacote que você use, e chame algo de lá.
- Instale o `requests` e escreva um `adopt Python.requests` que busque
  uma página — compare com o `Arcane.Http` da linguagem.
- Rode `dataforge check` num arquivo que importe um pacote ausente.
- Escreva uma ação que só usa numpy quando ele existe, e caia num laço
  quando não existe. Rode os dois caminhos.
