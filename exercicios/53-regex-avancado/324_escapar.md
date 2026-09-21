# 324 — o texto que vem de fora não é um padrão

Montar um padrão concatenando texto de usuário é como um ponto vira
"qualquer caractere".

## O parênteses é PIOR que quebrar

`(48) 99999-1234` compila: o parênteses vira um **grupo**, e os
parênteses somem do que se procura. O padrão passa a casar um telefone
sem parênteses — e não há erro nenhum.

## `escape` é o parâmetro de uma consulta SQL

O equivalente exato: o texto entra como **dado**, e não como
sintaxe.

## E um padrão que vem de fora passa por `risk`

Antes de rodar, e não depois.
