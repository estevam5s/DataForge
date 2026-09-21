# 269 — a regra cobrada na criação

Um `record` já dá imutabilidade e igualdade estrutural, e essas duas
metades são a maior parte. O que ele **não** dá é a regra:
`Dinheiro(-5, "BRL")` é um record perfeitamente válido, e o negócio
descobre isso três camadas adiante, num extrato negativo.

## A criação é o único ponto que impede

Depois de existir, o valor circula. A regra vale ali, ou não vale em
lugar nenhum.

## E ela vale em toda fronteira

Inclusive no `com`. Um refinamento que só valesse na criação seria uma
sugestão, e não um tipo.

## Um valor não muda

Dois valores iguais são o **mesmo** valor; mudar um deles mudaria o
outro para quem os comparou. A saída é criar outro.

## E ele nasce completo

Um campo vazio faria dois valores "iguais" diferirem no que ninguém
preencheu.

## A regra que estoura é um bug DELA

Dizer "valor inválido" quando a condição quebrou esconderia o defeito
real — e mandaria a pessoa procurar no lugar errado. As duas coisas
exigem correções em arquivos diferentes.

---

Tudo isso levanta `ValueObjectError`, que desce de `DomainError`:
`handle DomainError` pega a família, e quem precisa distinguir nomeia o
específico.
