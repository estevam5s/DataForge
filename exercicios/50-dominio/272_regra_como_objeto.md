# 272 — a regra que se combina e se explica

Um `given` dentro do serviço não pode ser combinado, nem reaproveitado
na consulta que lista "quem pode", nem explicado ao usuário. Os três
usos são a **mesma** regra, e escrevê-la três vezes é como as três
divergem.

## A decisão

`pode.vale(cliente)` responde sim ou não. É o uso óbvio, e o único que
um `given` cobre.

## A explicação aponta a PARTE que falhou

*"maior de idade E mora no Brasil"* não diz qual das duas a pessoa
precisa resolver — e essa frase é o que vai para a tela.

## E a mesma regra filtra uma lista

`pode.filtrar(todos)` é a consulta. Sem o objeto, ela seria um segundo
`given` numa compreensão — e os dois divergiriam na primeira mudança.

## Uma regra quebrada LEVANTA

Devolver "não vale" recusaria o usuário por um bug, calado.
