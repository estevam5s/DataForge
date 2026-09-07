# Exercicio 132 — Enums com `match`

## Enunciado

Trate cada membro de um enum com pattern matching e modele uma máquina de
estados onde só as transições declaradas são possíveis.

## Conceitos

Enum e `match` foram feitos um para o outro:

```dataforge
match luz:
    point Semaforo.Vermelho:
        yield "frear"
    point Semaforo.Amarelo:
        yield "reduzir"
    point Semaforo.Verde:
        yield "acelerar"
    default:
        yield "estado desconhecido"
```

`point Semaforo.Vermelho` é um **padrão de valor**: casa por igualdade com aquele
membro específico.

## Por que manter o `default`

DataForge 4.0 ainda não verifica exaustividade (avisar quando um membro ficou de
fora está no roadmap). Enquanto isso, o `default` é sua rede: se amanhã alguém
adicionar `Semaforo.Piscante`, o programa não silencia — cai num ramo que você
controla.

Um truque útil: faça o `default` **falhar ruidosamente** durante o
desenvolvimento.

```dataforge
default:
    trigger $"estado nao tratado: {luz}"
```

Assim o membro novo aparece na primeira execução, não na primeira reclamação.

## Máquina de estados

O padrão completo tem três partes:

```dataforge
enum Pedido:
    Novo
    Pago
    Enviado
    Entregue

steady TRANSICOES := {
    "Novo": ["Pago"],
    "Pago": ["Enviado"],
    "Enviado": ["Entregue"],
    "Entregue": []
}
```

1. O **enum** enumera os estados possíveis.
2. A **tabela** declara quais saltos são legítimos.
3. As **ações** só consultam a tabela.

Nenhum estado inválido é representável, e nenhuma transição inválida é possível.
`Entregue` com lista vazia é um estado terminal — o laço para sozinho.

## `from_name` fecha o ciclo

A tabela guarda texto (`"Pago"`), mas o programa trabalha com membros.
`Pedido.from_name(texto)` converte de volta, devolvendo `void` se o nome não
existir.

## Saída esperada

```
Vermelho (pare) -> frear
Amarelo (atencao) -> reduzir
Verde (siga) -> acelerar
[Novo, Pago, Enviado, Entregue]
```

## Experimente

- Acrescente `Cancelado` e permita `Novo -> Cancelado`.
- Faça `avancar` devolver todos os próximos possíveis em vez do primeiro.
- Troque o `default` por `trigger` e adicione um membro sem tratá-lo.
