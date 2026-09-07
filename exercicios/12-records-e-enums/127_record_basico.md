# Exercicio 127 — Records

## Enunciado

Declare um `record`, construa instâncias das duas formas e comprove que a
igualdade é estrutural.

## Conceitos

Um **record** é um agregado de dados nomeados e tipados. Comparando com o que
você já conhece:

| Linguagem | Equivalente |
|-----------|-------------|
| Python | `@dataclass(frozen=True)` |
| TypeScript | `interface` / `type` |
| Java | `record` |
| Go | `struct` |
| Rust | `struct` |

### Declaração

```dataforge
record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"
```

Cada campo **exige** um tipo. Um `:=` depois do tipo dá um valor padrão, o que
torna o campo opcional na construção.

### Construção

Duas formas, ambas verificadas:

```dataforge
Usuario("Ana", 30)                              // posicional
Usuario(nome := "Ana", idade := 30)             // nomeada
```

A forma nomeada é preferível quando há mais de três campos: `Usuario("Ana", 30,
"a@x.com", yes, 2)` é ilegível.

## Igualdade estrutural

Esta é a diferença central em relação a um `blueprint`:

```dataforge
Usuario("Ana", 30) is Usuario("Ana", 30)    // yes
```

Duas instâncias com os mesmos valores **são iguais**, mesmo sendo objetos
distintos. Blueprints comparam por identidade; records, por conteúdo.

Isso é o que torna records úteis como chaves, como valores em conjuntos e em
comparações de teste.

## Quando usar record e quando usar blueprint

| Use `record` | Use `blueprint` |
|--------------|-----------------|
| dados sem comportamento próprio | objetos com estado que muda |
| igualdade por valor | identidade importa |
| imutável | precisa mutar campos |
| sem herança | herança, traits, polimorfismo |

## Saída esperada

```
Usuario(nome: Ana, idade: 30, email: sem@email)
Usuario(nome: Bruno, idade: 25, email: b@x.com)
Ana 30 sem@email
yes
no
erro: Record 'Usuario' is missing field 'idade'
erro: field 'nome' of record 'Usuario' declared as String but got Integer
```

## Experimente

- Adicione `ativo: Boolean := yes` e veja que o código existente continua válido.
- Rode `dataforge check`: ele aponta `Usuario("Carla")` **antes** de executar.
