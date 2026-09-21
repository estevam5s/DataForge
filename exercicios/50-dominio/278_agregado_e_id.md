# 278 — a identidade nasce com o objeto

Um id que o banco gera obriga a salvar antes de ter identidade, e no
intervalo entre criar e confirmar o objeto existe sem ser ele mesmo.

## O id é texto, e nasce com o agregado

`D.novo_id()` é um UUID4. Quem quiser o seu passa na criação.

## A versão conta os comandos

E é ela que serve a uma trava otimista: quem grava comparando a versão
que leu descobre que outro passou na frente.

## E `estado()` é uma cópia

A foto não acompanha o agregado. Devolver o dicionário vivo abriria
uma porta de escrita ao lado do comando — que é exatamente o que o
agregado existe para fechar.
