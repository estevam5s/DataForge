# 270 — o agregado é a única porta de escrita

Se qualquer um escreve, a invariante não vale nada — não há onde
cobrá-la. O agregado existe para que exista esse lugar.

## Escrever por fora é recusado

`pedido.mudar(total := 999999)` levanta. Não é burocracia: é a
condição para as duas linhas seguintes significarem algo.

## A invariante é cobrada na SAÍDA

Cobrar na entrada deixa o objeto quebrado quando o comando falha no
meio. Cobrar na saída garante que ninguém observa um estado inválido.

## E o comando recusado é desfeito

Estado, eventos e versão voltam ao que eram. Sem isso, metade da
mudança fica aplicada e a próxima leitura vê um agregado que nunca
deveria existir.

## A versão conta os comandos

Ela não avança num comando desfeito — e é ela que serve a uma trava
otimista: quem grava comparando a versão que leu descobre que outro
passou na frente.

---

A distinção que vale lembrar: a invariante de um `blueprint` **acusa**
e não desfaz; o agregado **acusa e desfaz**.
