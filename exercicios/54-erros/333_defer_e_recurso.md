# 333 — fechar o que foi aberto

`defer` roda na saída da **ação**, onde quer que esteja escrito.

## Num laço, ele acumula e roda tudo no fim

Na ordem inversa do registro. A consequência prática: num laço de dez
mil voltas, dez mil arquivos ficam abertos até a ação terminar. Quem
precisa fechar por **volta** extrai o corpo para uma ação própria.

## Ele NÃO engole o erro dele

Um erro dentro do `defer` viaja. Até a correção era descartado, e um
arquivo não fechado terminava o programa com código **0**.

## E quando os dois falham, viaja o original

Com o do fechamento em `e.outros` — é o modelo do
try-with-resources.
