# 339 — o erro que acontece em OUTRA thread

`parallel` espera todas as tarefas e levanta na linha do bloco, com as
demais falhas em `.outros` — então um `monitor` o pega.

## Até a correção, os dois engoliam

`thread` e `parallel` faziam `except Exception` e imprimiam uma linha:
o programa seguia, saía com **0**, e nenhum `handle` via o erro. Um CI
passava verde com metade do trabalho perdida.

## A linguagem NÃO sincroniza sozinha

Duas threads escrevendo no mesmo nome perdem atualizações, em
silêncio. O `check` **avisa** sobre o padrão — mas avisar não é
sincronizar.

## E o que o GIL protege sozinho

`append` de várias threads entrega tudo: o GIL protege a operação
inteira, e avisar sobre ele seria falso alarme em código que funciona. O
que perde é ler-modificar-escrever.
