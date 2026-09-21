# 298 — o layout que tem NOME

`Arcane.Bytes` empacota por **formato**, e o resultado é posicional —
`dados[3]` três meses depois não diz nada. Um molde tem campos
nomeados, e cobra a ordem dos bytes.

## A ordem dos bytes é obrigatória

Sem ela, o mesmo arquivo lido em duas máquinas dá dois valores, e
nenhuma das duas falha. `"rede"` é big-endian — o de todo formato de
arquivo e todo protocolo.

## O molde sabe o próprio layout

`tamanho`, `deslocamento(campo)` e `mapa()` respondem sem contar à
mão — e uma conta à mão envelhece quando alguém acrescenta um campo no
meio.

## E o que falta vai zerado

Um registro nasce completo; o que não foi escrito é zero, e não
lixo.
