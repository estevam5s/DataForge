# 337 — o sistema de arquivos falha de vários jeitos

Não existe, existe e não é o que se espera, sem permissão, e uma pasta
onde se queria um arquivo. Tratar todos como "erro de IO" é o que faz um
log dizer "falhou" e nada mais.

## Conferir antes NÃO dispensa tratar

Há uma janela entre os dois: o arquivo pode sumir nesse intervalo.

## O `defer` garante a limpeza

Inclusive no caminho de erro — que é o caminho em que o temporário
costuma ficar para trás.

## E o que NÃO se deve fazer

`IO.remove_tree(OS.temp_dir())` destrói o temporário de **todo**
processo da máquina. Sempre uma subpasta própria.
