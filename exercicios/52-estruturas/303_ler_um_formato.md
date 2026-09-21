# 303 — ler um formato binário de verdade

Cabeçalho, tabela de índices e registros — o desenho de quase todo
formato que existe. E nada aqui precisa de FFI.

## Procurar pelo índice, sem varrer os itens

É o motivo de o índice existir: a tabela é pequena e ordenada, e os
registros podem ser muitos.

## Mudar o estoque no lugar

A janela escreve direto no bloco, e a releitura confirma.

## E a magia errada é problema de quem lê

O módulo não inventa validação de formato: quem conhece o formato é
quem escreve o leitor.
