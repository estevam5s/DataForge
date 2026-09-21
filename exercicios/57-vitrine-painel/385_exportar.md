# 385 — tirar o dado de dentro do painel

Todo painel acaba com alguém pedindo "manda isso em Excel". Exportar é
a diferença entre um painel usado e um painel que vira captura de tela
colada num e-mail.

## O arquivo é montado NO SERVIDOR

Não há biblioteca de planilha no navegador, e o `.xlsx` sai do
`Arcane.Excel`, que grava sem dependência externa.

## O conteúdo fica no estado, e não no nó

O HTML leva o botão; os bytes ficam para quem clicar. Mandar um
`.xlsx` inteiro dentro do HTML de toda página seria absurdo.

## E `build` e `deploy` não existem

Não há o que construir (não há bundle), e um `deploy` que falasse com
o servidor por dentro esconderia o que a máquina é.
