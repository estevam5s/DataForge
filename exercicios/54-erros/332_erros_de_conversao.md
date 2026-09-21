# 332 — converter o que veio de fora

Todo dado que entra num programa é texto — do formulário, do CSV, da
variável de ambiente. Converter é onde ele falha, e converter em
silêncio é onde ele **mente**.

## A diferença entre não informado e inválido

Um padrão silencioso junta os dois casos, e o relatório sai com zeros
que ninguém sabe de onde vieram.

## Juntar os erros e devolver todos

Melhor que parar no primeiro: quem preenche corrige tudo numa
passada.

## E a conversão que NÃO é recusada é a mais perigosa

`float` aceita notação científica e infinito — mais do que um
formulário deveria.
