# 331 — a família das coleções

Índice, chave e fatia falham de jeitos diferentes, e cada um tem uma
saída diferente. Tratar os três com o mesmo `handle Error` é o que faz
um bug de chave virar "algo deu errado".

## `remove` e `pop` mudam de sentido

Num cluster o segundo argumento é o **valor**; num vault, a **chave**.
`remove` é silencioso; `pop` **levanta** — devolver `void` calado
esconderia a diferença entre "a chave valia `void`" e "a chave não
estava lá".

## `omit` devolve cópia

E não mexe no original.

## E o `??` é a saída que o próprio erro sugere

Um analisador que acusasse o conserto que ele mesmo recomenda é um
analisador que se desliga.
