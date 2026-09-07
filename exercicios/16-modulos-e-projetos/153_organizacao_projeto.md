# Exercicio 153 — Organizando um projeto

## Enunciado

Estruture o código em camadas com responsabilidades separadas.

## As quatro camadas

| Camada | Contém | Depende de |
|--------|--------|------------|
| **Modelo** | records, enums, invariantes | nada |
| **Regras** | decisões de negócio | modelo |
| **Apresentação** | como virar texto | modelo, regras |
| **Aplicação** | orquestra o fluxo | todas |

As setas apontam sempre para baixo. O modelo não sabe que existe apresentação; as
regras não sabem se o resultado vira terminal, HTTP ou CSV.

## Num projeto real

Cada camada é um módulo:

```
src/
  modelo.df          record Produto, enum Situacao
  regras.df          situacao_de, precisa_repor
  apresentacao.df    formatar_produto, cabecalho
  main.df            junta tudo
tests/
  regras_test.df
forge.toml
```

E cada módulo declara sua interface:

```dataforge
// regras.df
relay LIMITE_CRITICO, situacao_de, precisa_repor
```

## Por que separar

O critério prático é **o que muda junto**.

- Trocar o limite de estoque crítico → mexe só em `regras.df`
- Trocar o terminal por uma página web → mexe só em `apresentacao.df`
- Acrescentar um campo ao produto → mexe em `modelo.df` e em quem usa o campo

Quando tudo está num arquivo, qualquer mudança arrisca qualquer coisa.

## Regras puras são testáveis

```dataforge
action situacao_de(p: Produto) -> Situacao:
    given p.estoque is 0:
        yield Situacao.EmFalta
    ...
```

Essa ação não imprime, não lê arquivo, não consulta banco. O teste é uma linha:

```dataforge
assert situacao_de(Produto("X", "Y", 1, 0)) is Situacao.EmFalta
```

Se ela também formatasse a saída, testá-la exigiria comparar strings — e mudar o
formato quebraria o teste da regra.

## O detalhe do ternário

```dataforge
marca := "!" given precisa_repor(p) otherwise " "
```

Uma linha em vez de um `given`/`otherwise` de quatro. Vale para valores simples
como este; para lógica maior, o bloco continua mais legível.

## Saída esperada

```
Inventario
----------
  P01   Mouse           15  R$ 1200.0
! P02   Teclado          3  R$ 600.0
! P03   Monitor          0  R$ 0.0
  P04   Cabo            60  R$ 1500.0

Repor
-----
  Teclado: Critico
  Monitor: EmFalta

patrimonio: R$ 3300.0
```

## Experimente

- Separe de verdade em quatro arquivos com `relay` e `adopt`.
- Acrescente uma camada de persistência com `Arcane.Database`.
- Escreva `tests/regras_test.df` cobrindo as três situações.
