# 325 — ler um formato de linha

Regex não serve para linguagem aninhada — não há como casar parênteses
equilibrados, porque isso exige **contar**. Para um formato de LINHA ela
é a ferramenta certa.

## O ancoramento é o que faz isso funcionar

Sem `^...$`, a linha `# [falso]` casaria com a de seção.

## E a conversão de tipo, com o padrão decidindo

Inteiro, decimal, booleano ou texto — cada um reconhecido pela forma,
e não por uma tabela de nomes de campo.
