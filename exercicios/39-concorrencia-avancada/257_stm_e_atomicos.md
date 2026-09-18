# 257 — Memória transacional, CAS e estruturas sem trava

## O problema, medido

Duas threads somando na mesma variável entregaram **40.425 de 80.000**
neste repositório — em silêncio. O `mutex` resolve **uma** seção crítica.
O que ele não resolve é **compor**: transferir de uma conta para outra
são duas escritas que precisam acontecer juntas, e com mutex isso vira
ordem de aquisição — uma regra que ninguém consegue verificar, e cuja
violação é impasse.

## A transação

`T.atomicamente(acao)` roda a ação num **rascunho**: tudo o que ela lê
guarda a versão, e tudo o que ela escreve fica de lado. No fim, sob uma
trava curta, ela confere se alguma variável lida mudou. Se mudou,
descarta e tenta de novo; se não, publica tudo de uma vez.

Quatro consequências:

1. **atomicidade** — um erro no meio não deixa metade escrita, e o erro
   sobe (engoli-lo seria o oposto de atomicidade);
2. **isolamento** — a transação lê a própria escrita, não a dos outros;
3. **composição** — aninhar é achatar: duas ações transacionais dentro
   de uma terceira são **uma** transação;
4. **conflito custa repetição**, e não dado errado. As estatísticas
   dizem quanto.

## Esperar sem girar

`T.retentar()` diz "não dá para seguir com o que existe agora". A
transação é abandonada e **dorme** até alguma variável que ela leu mudar.
`T.ou_entao(a, b)` tenta a segunda quando a primeira pede para esperar —
é a composição de duas operações bloqueantes, que um mutex não tem.

## Nunca faça E/S dentro de uma transação

Ela pode ser **repetida**, e o que já saiu não volta: um `out`, um
`IO.write` ou um `Http.post` lá dentro aconteceria duas vezes. Junte o
resultado dentro e faça a E/S depois.

## CAS: a peça de baixo

`comparar_e_trocar(esperado, novo)` troca **só se** o valor ainda for o
que você leu. O laço clássico — leia, calcule, troque se ninguém mexeu —
é como se escreve qualquer atualização sem trava.

## O que "sem trava" quer dizer aqui

`append` e `popleft` de um `deque` acontecem inteiros em C: não há janela
entre ler e escrever. Isso está medido — quatro threads com 5 mil
`append` cada entregaram 20.000 de 20.000.

O que **não** é indivisível é qualquer sequência escrita em DataForge:
`v["n"] := v["n"] + 1` perde atualização. Ali a resposta é `atomico`,
`mutex` ou transação.

E `lock-free` não é `wait-free`: o laço de CAS repete quando há disputa,
e uma thread azarada pode repetir muitas vezes.
