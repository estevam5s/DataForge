# 375 — o gráfico é SVG escrito no servidor

Zero dependência também no navegador. Uma biblioteca de CDN quebra
qualquer app em rede fechada — que é onde painel de dados costuma
rodar.

## A barra é ancorada no zero; a linha, não

Não é estética. Numa barra o que significa é o **comprimento**, e
cortar o eixo faz uma barra 3% maior parecer o dobro. Numa linha o que
significa é a **posição**: forçar o zero num patrimônio que vai de 1,02
a 1,13 milhão desenha uma reta, e a variação some.

## `void` numa série é um VÃO, e não um zero

O caminho antigo convertia ausência para `0.0`, e a linha de um
acumulado despencava ao chegar no mês que ainda não aconteceu — um
gráfico que mostra uma queda de um milhão onde só falta o dado.

## E há teste proibindo `http://` no CSS e no JS

É o que garante a rede fechada.
