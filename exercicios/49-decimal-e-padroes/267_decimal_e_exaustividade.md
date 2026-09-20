# 267 — o centavo que fecha, e o caso que aparece antes de rodar

Dois itens que faltavam para a linguagem estar completa, e os dois são de
**correção**: um erra dinheiro em silêncio, o outro devolve `void` em
silêncio.

## 1. O literal decimal: `19.99d`

`Float` é IEEE 754 de 64 bits, e ele **não representa 0,1** — representa o
binário mais próximo. A diferença aparece na soma:

```dataforge
assert 0.1 + 0.2 is not 0.3          // Float
assert 0.1d + 0.2d is 0.3d           // Decimal: exato
```

Antes do sufixo, a exatidão exigia escrever `Dec.de("19.99")` — e quem
escrevia `19.99` **não era avisado de nada**. Um centavo que some numa
linha some de novo num milhão de linhas.

O sufixo constrói o valor a partir do **texto**, sem passar por float
nenhum. É a diferença que decide:

| Como | Resultado |
|---|---|
| `Decimal("0.1")` | exato |
| `Decimal(0.1)` | já carrega o erro do float que veio antes |

### Três detalhes que o exercício cobra

**O `d` só conta quando termina o número.** `19.99dias` é um número
seguido de um nome — engolir o `d` ali criaria um `ias` do nada. E um nome
chamado `d` continua valendo. É a mesma disciplina de adjacência do `~/` e
do hífen num caminho relativo.

**O literal e o módulo são o mesmo valor.** `19.99d is Dec.de("19.99")`, e
`Dec.centavos`, `Dec.arredondar` e `Dec.repartir` trabalham com ele.

**Misturar com `Float` é recusado.** Um `Decimal` existe para ser exato, e
somá-lo a um `Float` devolveria o erro binário de volta dentro — o exato
contaminado pelo aproximado, sem nada denunciar. E é por isso que
`Decimal` **não é um `Number`**: um `Number` que o aceitasse faria a falha
aparecer dentro da ação, longe de quem passou o valor.

O `check` acusa a mistura **antes de rodar** (`decimal-com-float`). Antes
ela só aparecia em execução.

## 2. Exaustividade em padrão aninhado

O `match` já avisava o que ficava de fora num enum solto. Com o enum
**dentro** de uma sequência, ele calava:

```dataforge
point [Cor.A, x]:     // e o Cor.B? Nada avisava.
```

O motivo é arquitetural, e vale entender: a conferência de enum olha o
padrão **inteiro**, e `[Cor.A, x]` não é um membro de enum. A de sequência
**reivindica** o match e se cala, porque `Cor.A` não é irrefutável e o ramo
não conta como cobertura de tamanho. Duas conferências, e o caso passava
entre as duas.

Hoje a cobertura é **por posição**, e o que se cobra é o produto
cartesiano dos eixos de enum — com duas posições de `Cor`, quatro
combinações.

### O que faz a regra calar

| Quando | Por quê |
|---|---|
| ramos de tamanhos diferentes, ou com `...resto` | ali a pergunta é de **tamanho**, e quem responde é a outra conferência |
| uma posição com literal (`[Cor.A, 0]`) | `[Cor.A, 0]` **não** cobre `[Cor.A, *]`, e tratar como se cobrisse inverteria o sentido do aviso |
| mais de 64 combinações | um aviso que lista duzentas é ruído, e ninguém o lê duas vezes |

Uma posição **irrefutável** cobre todos os membros daquele eixo — é o que
faz `point [Cor.A, x]` mais `point [c, x]` ser completo, e o exercício
demonstra os dois.

E um `point` com **guarda** nunca conta como cobertura, aqui como nas
outras quatro formas: `point [Cor.B, x] when x bigger 0` deixa passar o
`x` negativo.

## O que levar

- Um número que uma pessoa vai conferir na mão pede `d`.
- Um caso esquecido num `match` devolve `void`, e `void` atravessa meia
  dúzia de chamadas antes de virar erro **em outro lugar**. É por isso que
  vale ser avisado antes de rodar.
- E as duas regras **calam** onde não conseguem provar. Um falso alarme
  ensina a ignorar mensagens.
