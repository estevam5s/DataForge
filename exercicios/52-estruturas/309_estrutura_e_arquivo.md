# 309 — gravar e reler do disco

Um molde só vale se o arquivo que ele produz for lido de volta igual.
A ida e a volta passam pelo disco, e os bytes são comparados.

## Os bytes são idênticos

Não é "parecido": é a mesma sequência.

## E o `f32` tem precisão de `f32`

`0.1` não cabe exato em 32 bits, e a ida e volta **não** devolve
`0.1`. Isso não é defeito do módulo — é o tipo que foi escolhido, e
`f64` aproxima menos.
