# Exercicio 186 — Blueprints abstratos e contratos de trait

## Enunciado

Declare o que um tipo precisa ter, e deixe a linguagem cobrar de quem herdar.

## Conceitos

```dataforge
abstract blueprint Forma:
    abstract action area()       // exigência: o herdeiro implementa

    action descrever():          // concreto: o herdeiro ganha de graça
        yield $"area {self.area()}"
```

Um blueprint abstrato **não pode ser spawnado** — ele existe para ser herdado.
Um método abstrato é uma exigência, e o erro sai **na declaração do herdeiro**,
não na primeira chamada.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `ABC` + `@abstractmethod` |
| TypeScript | `abstract class` / `interface` |
| Java | `abstract class` / `interface` |
| Rust | `trait` com método sem corpo |

## O que observar

**O contrato é conferido na declaração.** Um blueprint que adota um trait e não
implementa o que ele exige falha ao ser declarado:

```
erro[DF0301]: Blueprint 'Ruim' does not implement 1 abstract method:
    comparar()  — declarado em 'Comparavel'
    Implement it, or mark 'Ruim' as 'abstract blueprint' if it is not meant
    to be spawned directly.
```

Isso é diferente de descobrir o problema quando alguém chama o método ausente,
em produção.

**Trait pode ter implementação padrão.** Método com corpo no trait é herdado;
método sem corpo é exigência.

**Um abstrato pode ter métodos concretos** que chamam os abstratos — é o padrão
"método molde": o pai define o roteiro, o filho preenche os passos.

## Armadilhas

- Um blueprint que herda de abstrato e **não implementa tudo** também precisa ser
  `abstract`. Deixar pela metade não compila.
- Trait não guarda estado. Para compartilhar campos, use herança ou composição.

## Relacionados

- [188 — Composição](188_composicao.md)
- [190 — Polimorfismo](190_polimorfismo.md)
