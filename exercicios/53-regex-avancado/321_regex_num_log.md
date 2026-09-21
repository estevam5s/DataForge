# 321 — um analisador de log completo

Grupos nomeados, ancoramento, posição e substituição calculada num
caso que existe em todo sistema.

## Só as linhas que casam INTEIRAS

Sem o ancoramento, uma linha malformada casaria pela metade e entraria
no relatório com campos errados.

## Mascarar antes de sair daqui

O e-mail vira `a***@exemplo.com` e o resto do log continua legível.

## E a linha que não casou continua visível

Um parser que descarta em silêncio esconde o dia em que o formato do
banco mudou.
