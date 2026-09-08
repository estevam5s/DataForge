# Exercício 207 — Migrações

## Enunciado

Evolua o esquema sem perder o que já está gravado.

## Conceitos

Duas formas.

**A diferença** compara o modelo com a tabela real e cria o que falta:

```dataforge
d := Usuario.diferenca()          // o que falta
Usuario.aplicar_diferenca()       // cria
```

**Os passos numerados** cobrem o que a diferença não cobre — renomear uma
coluna, migrar dados, criar um índice composto:

```dataforge
m := Forge.migracoes(db)
m.passo("001_cria_pedidos", subir, descer)
m.subir()
```

## O que observar

**`aplicar_diferenca` nunca apaga.** Ele cria o que falta e **relata** o que
sobra. Perda de dado não se automatiza: uma coluna que sumiu do modelo pode ter
sido erro de digitação, e a diferença entre um `DROP` e uma restauração de
backup é grande.

**O histórico mora no banco**, numa tabela `_forge_migracoes`. É o que faz duas
máquinas concordarem sobre o estado: um arquivo versionado diz o que *deveria*
ter rodado; a tabela diz o que rodou.

**Uma migração que falha para tudo.** Continuar depois de uma falha deixa o
banco num estado que nenhuma migração previu.

## Armadilhas

- Escreva o `descer` mesmo que não vá usar. O momento em que você precisa dele é
  o pior momento possível para escrevê-lo.
- Comparar o modelo com a tabela **real** é melhor que confiar num histórico de
  arquivos, que diverge assim que alguém mexe no banco à mão.

## Relacionados

- [205 — Modelos e validação](205_modelos_e_validacao.md)
