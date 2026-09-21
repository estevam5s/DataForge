# 338 — o erro que aparece na FRONTEIRA

`expects`, `promises` e `invariant` movem a falha para onde ela é
compreensível. Sem eles, um argumento errado vira uma conta errada três
chamadas adiante, e a queixa fala de outra coisa.

## As três dizem coisas diferentes

`PreconditionError` = o argumento está errado, e a culpa é de quem
chamou. `PostconditionError` = a ação mentiu sobre o que promete.
`InvariantError` = o objeto chegou a um estado que não pode existir.

## Sem a pré-condição, `sacar(-50)` AUMENTA o saldo

E o erro aparece no extrato, semanas depois.

## E `handle ContractError` pega as três

Quando a distinção não importa para quem trata.
