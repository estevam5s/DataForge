# Exercício 203 — Injeção de SQL

## Enunciado

Tente derrubar uma tabela por um campo de busca.

## Conceitos

Injeção de SQL é o bug mais explorado da história do software. Ele acontece
quando um valor vindo do usuário entra no **texto** da consulta:

```
-- o que o programa monta, concatenando:
select * from usuarios where nome = ''; drop table usuarios; --'
```

O Forge o torna impossível **por construção**: o construtor não tem como pôr um
valor no texto. Valores viram parâmetros, sempre — e o banco os trata como
dado, nunca como comando.

## O que observar

**Não é disciplina de quem escreve.** Numa linguagem onde a concatenação é
possível, todo programador precisa lembrar de não fazê-la, sempre, em todo
lugar. Aqui não há o que lembrar.

**A lista de operadores é fechada.** `.onde("x", operador, v)` só aceita os
operadores conhecidos. Um operador vindo de variável seria outro caminho de
injeção, e ele está fechado pelo mesmo motivo.

**O SQL à mão também é seguro**, desde que use `?` e passe os valores separados.

## Armadilhas

- `onde_cru(sql, valores)` existe para o que o construtor não cobre. O SQL vai
  **como escrito**; os valores continuam parâmetros. Nunca concatene entrada do
  usuário no texto que você passa a ela.
- Nome de **tabela** e de **coluna** não podem ser parâmetros — nenhum banco
  permite. Se eles vierem do usuário, valide contra uma lista fechada.

## Relacionados

- [202 — Construtor de consultas](202_construtor_de_consultas.md)
- [Segurança](https://dataforge-lang.vercel.app/docs/seguranca)
