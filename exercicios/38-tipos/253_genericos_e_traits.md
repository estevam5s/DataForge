# 253 — Generics, tipos indexados e traits

Três perguntas, e as respostas que este exercício demonstra.

## 1. O que um `<T>` promete?

Nada sobre o valor — e isso é de propósito. Ele descreve a **relação**:
`action primeiro<T>(xs: Cluster<T>) -> T` diz que o que sai é do mesmo
tipo do que estava dentro. É por isso que `primeiro([1,2,3])` e
`primeiro(["a","b"])` são os dois válidos.

Com `extends`, o parâmetro passa a ser **verificável**, e então é
verificado nas duas metades: o `check` acusa a chamada antes de rodar, e
a execução confere o valor.

| Forma | Documenta | Cobra |
|---|---|---|
| `<T>` | sim | não |
| `<T extends Number>` | sim | sim, nos dois lados |

Dentro da declaração, um `T extends Number` **é** um `Number`: é o que
permite escrever `self.quanto * 2` sem o analisador reclamar.

## 2. Onde o argumento chega?

No **campo**. `Caixa<Integer>` recusa `Caixa("texto")`, e a mensagem
nomeia o campo culpado:

```
field 'valor' of Caixa<Integer> in variable 'errada' declared as Integer but got String
```

Sem isso, o parâmetro viraria comentário — o tipo prometeria uma coisa e
aceitaria outra.

Uma coleção anotada com o parâmetro (`itens: Cluster<T> := []`) **não**
guarda o conteúdo: `T` aceita qualquer coisa, e um `Pilha<T>` que
recusasse `append(1)` não serviria para nada. Uma coleção com tipo
concreto (`Cluster<Integer>`) continua guardando.

## 3. O tamanho pode fazer parte do tipo?

Pode, e é o que `Vetor<3>` faz. O argumento de um genérico pode ser um
**número**, e ele entra na regra do tipo:

```dataforge
type Vetor<N> := Cluster<Float> where len(valor) is N

action somar(a: Vetor<2>, b: Vetor<2>) -> Vetor<2>:
    yield [a[0] + b[0], a[1] + b[1]]
```

É a forma prática dos tipos dependentes: a ação passa a recusar uma
coordenada de três casas na fronteira, e o `check` prova o erro de um
literal antes de rodar.

## Traits: exigência, padrão e herança

Um método **sem corpo** é exigência; **com corpo** é implementação
padrão, que quem adota recebe. `trait Editavel extends Legivel` soma as
duas coisas da mãe.

A mensagem de quem implementa metade nomeia **quem declarou** a
exigência (`Legivel`), e não quem a repassou (`Editavel`). Numa cadeia de
traits, o nome errado manda procurar no arquivo errado.

Um trait também declara:

- **tipo associado** — `type Item := Any`, preenchido por quem
  implementa (`type Item := Integer`) e conferido como qualquer anotação;
- **constante associada** — `steady LIMITE := 3`, que vira membro
  (`Fila.LIMITE`).

E para exigir dois traits ao mesmo tempo, a interseção:
`type Auditavel := Serial & Forma`. Um objeto que tem só metade é
recusado na fronteira, dizendo qual metade falta.
