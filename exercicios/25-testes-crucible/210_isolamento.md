# Exercício 210 — Isolamento entre trials

## Enunciado

Prove que um teste não contamina o próximo.

## Conceitos

A garantia central do Crucible: cada trial roda no **próprio quadro de escopo**,
com o `setup` refeito. Um teste que passa sozinho e falha na suíte seria bug do
framework, não do teste.

```dataforge
crucible "Isolamento":
    setup:
        contador := 0

    trial "o primeiro soma":
        contador := contador + 1
        expect contador is 1

    trial "o segundo vê o valor original":
        expect contador is 0
```

Os dois passam.

## O que observar

**A ordem não importa.** `--aleatorio` embaralha, e a semente aparece no
relatório para a falha ser reproduzível — uma ordem aleatória que não se repete
é impossível de depurar.

**Um teste que depende de ordem falha ali**, e não seis meses depois, numa
madrugada, depois que alguém acrescentou um teste no meio.

## Armadilhas

- Estado **fora** da suíte não é isolado. Um vault declarado no topo do arquivo
  é compartilhado; se você precisa dele limpo, declare no `setup`.
- Recurso externo — arquivo, banco, servidor — também não. Use `fixture` para
  garantir a limpeza.

## Relacionados

- [212 — Dublês e fixtures](212_dubles_e_fixtures.md)
