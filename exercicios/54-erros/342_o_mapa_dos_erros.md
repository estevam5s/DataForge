# 342 — as famílias, e como escolher

O código de um erro diz a família, e a família diz **de quem é a
culpa** — que é a única pergunta que importa quando um log chega às três
da manhã.

## Dezoito famílias

Das três primeiras (sintaxe, execução, tipos) às três últimas
(domínio, reativo, memória estruturada).

## A escada de tratamento

Do mais específico ao mais geral, e cada degrau com uma **ação**
diferente: pedir de novo, criar e tentar, registrar e seguir, registrar
e parar.

## E a que mais custa caro

`handle RuntimeError` **não** pega um `trigger`.

---

As três decisões que o módulo ensina: capture pela família e nomeie o
específico quando precisar; falha esperada é **valor**, falha
excepcional é `trigger`; e o que fecha recurso vai em `defer` — que não
engole nada.
