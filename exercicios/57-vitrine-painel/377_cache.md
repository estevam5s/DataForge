# 377 — o cache não é opcional

O programa **inteiro** roda de novo a cada interação. Sem cache, a
consulta que carrega os dados roda a cada tecla digitada — e o painel
fica inutilizável com qualquer fonte que não seja instantânea.

## Dois argumentos, duas consultas — e nada mais

Voltar ao argumento anterior volta ao cache.

## O depósito é indexado por IDENTIDADE da ação

Duas ações `carregar` em arquivos diferentes dividiriam o mesmo cache,
e o teto da primeira venceria calado sobre o da segunda. Mas `id()` não
é identidade ao longo do **tempo**: o CPython reaproveita o endereço de
um objeto coletado, e uma ação nova caía na chave de uma ação morta —
herdando o **valor** dela.

## E o recurso, para o que NÃO é dado

`V.cache` guarda **valor**; `V.recurso` guarda um objeto que se abre
uma vez — uma conexão, um modelo carregado.
