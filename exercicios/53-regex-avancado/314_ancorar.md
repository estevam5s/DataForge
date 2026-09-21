# 314 — `match` ancora só no COMEÇO

Validar com ele aceita lixo no fim, calado. Um validador que aceita
`"88010-000 e mais"` grava um CEP que não existe.

## `fullmatch` casa a string inteira

E `is_exactly` é a pergunta que um validador faz: sim ou não.

## O resultado vazio tem as MESMAS chaves

Senão ler `["start"]` de um não-casamento levantaria — e todo uso
precisaria de um `given` antes.

## E `^...$` faz o mesmo

É o que se vê em padrão copiado da internet. `fullmatch` é o mesmo,
sem depender de lembrar das âncoras.
