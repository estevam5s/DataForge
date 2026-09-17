# 251 — Nascer, viver sob threads, e morrer limpo

## O que se pratica

`exclusive action` reentrante sob `parallel`, `lazy get`, `teardown`,
`Memoria.mapa_fraco` e `Memoria.vivos`.

## O que este exercício ensina que não é óbvio

**1. Sem `exclusive`, o contador perde acessos, calado.** Ler, somar e
escrever são três passos, e duas threads intercaladas somam o mesmo valor
— a armadilha 14 do `CLAUDE.md` mediu 40.425 de 80.000. `exclusive` põe
uma trava **por objeto**: dois contadores diferentes não esperam um pelo
outro.

**2. A trava é reentrante.** `registrar_dois` chama `registrar`, que
também é exclusivo. Com uma trava simples a thread esperaria por si mesma
para sempre.

**3. `teardown` roda na hora, e não "algum dia".** O DataForge herda do
CPython a contagem de referências: o objeto morre quando o último nome o
solta. Enquanto `_outra` segurar a conexão, ela vive — é o que o assert do meio
confere.

**4. O cache com referência forte é o vazamento mais comum que existe.**
`mapa_fraco` guarda o dado *enquanto* a sessão existir, sem ser a razão de
ela existir. Soltar a sessão apaga a entrada.

**5. Recurso importante fecha com `with` ou `defer`.** `teardown` depende
de o último nome soltar o objeto; um objeto preso num ciclo espera o
coletor. Para arquivo e conexão, o ponto de fechamento conhecido é melhor.

## Para ir além

- Tire o `exclusive` de `registrar` e rode algumas vezes: o total muda.
- Rode `dataforge check` sem o `exclusive` e leia o aviso
  `escrita-concorrente`.
