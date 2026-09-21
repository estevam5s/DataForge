# 276 — o comando que falha no meio não deixa metade

Um comando que muda três campos e falha no terceiro deixaria os dois
primeiros aplicados. A próxima leitura veria um agregado que nunca
deveria existir — e nada denunciaria.

## Estado, versão e eventos voltam

Os três juntos. Deixar a versão avançar faria uma trava otimista
recusar uma gravação legítima.

## O evento do comando desfeito também some

Um fato de um comando que não aconteceu é a pior classe de evento:
alguém reage a ele, e não há nada para reagir.

## E a invariante violada tem o mesmo efeito

Não há dois caminhos de desfazer — há um.
