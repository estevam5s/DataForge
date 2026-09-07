# Exercicio 189 — Quando usar record e quando usar blueprint

## Enunciado

Compare os dois, e escolha pelo que o dado precisa ser.

## Conceitos

A pergunta que decide: **dois desses, com os mesmos valores, são a mesma coisa?**

| | `record` | `blueprint` |
|---|---|---|
| Igualdade | estrutural — mesmos valores, mesmo record | por identidade |
| Mutação | imutável; `with` cria cópia | estado evolui |
| Uso típico | valor: ponto, dinheiro, data | entidade: conta, usuário, sessão |

Dois pontos `(1, 2)` **são** o mesmo ponto — record. Duas contas com o mesmo
saldo **não** são a mesma conta — blueprint.

| Linguagem | record | blueprint |
|---|---|---|
| Python | `@dataclass(frozen=True)` | `class` |
| Java | `record` | `class` |
| Kotlin | `data class` | `class` |
| Rust | `struct` + `derive(PartialEq)` | `struct` + `impl` |

## O que observar

**Record também tem comportamento.** `distancia_ate` é um método normal — a
diferença não é ter ou não métodos, é a identidade e a mutabilidade.

**`with` devolve uma cópia**, e o original não muda. É o que torna record seguro
de compartilhar: ninguém altera o seu pelas costas.

**Tentar atribuir a um campo de record é recusado**, com a alternativa na
mensagem.

## Armadilhas

- Usar blueprint para valor força você a implementar `operator ==` à mão, e a
  lembrar de copiar antes de passar adiante.
- Usar record para entidade obriga a recriar o objeto inteiro a cada mudança, e
  perde a identidade — duas contas iguais viram uma.

## Relacionados

- [181 — Campos declarados](181_campos_declarados.md)
- [185 — Sobrecarga de operadores](185_sobrecarga_operadores.md)
