# 379 — mais de uma página

O que não casa com página nenhuma cai no tratador de 404 do Kiln, e
**não** numa rota curinga.

## Uma curinga engoliria o que vier depois

Ela é casada na **ordem** do registro, então engoliria toda rota
acrescentada depois do `V.montar()` — que é exatamente o que se faz para
servir uma API ao lado do painel.

## O menu sai da lista, e não de uma cópia

Duas listas divergiriam, e o item apontaria para uma página que não
existe mais.

## E o 404 responde 404

E não 200 com "404" no corpo: um monitor que só olha o status veria o
site saudável.
