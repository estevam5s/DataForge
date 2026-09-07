# Exercicio 181 — Campos declarados

## Enunciado

Declare campos com tipo e valor padrão no corpo do blueprint, em vez de criá-los
dentro do `setup`.

## Conceitos

Até o 4.0, todo campo nascia por atribuição no `setup`. Isso funciona, mas
esconde a forma do objeto: para saber o que ele tem, era preciso ler o corpo do
construtor inteiro.

```dataforge
blueprint Contador:
    valor: Integer := 0
    passo: Integer := 1
```

Declarar o campo separa **o que o objeto tem** de **como ele nasce** — e o valor
padrão elimina o `setup` repetitivo.

| Linguagem | Equivalente |
|-----------|-------------|
| Python | atributo de classe, ou `@dataclass` |
| TypeScript | `campo: Tipo = valor` na classe |
| Java | `private int valor = 0;` |
| Kotlin | `var valor: Int = 0` |

## O que observar

**Campo sem padrão começa `void`.** Não é erro: é o valor que diz "ainda não
tem". Um campo obrigatório deve ser preenchido no `setup`.

**Campos são herdados.** O filho enxerga os do pai sem redeclarar, e pode
acrescentar os seus.

**O tipo é documentação verificada.** O analisador estático usa a anotação para
apontar atribuição incompatível antes de rodar.

## Armadilhas

- Um campo declarado **não** é criado pelo `setup` automaticamente — se o
  construtor recebe `nome`, ainda é preciso `self.nome := nome`.
- O padrão é avaliado uma vez, na declaração do blueprint. Para um valor que
  precisa ser novo a cada objeto (uma lista, por exemplo), atribua no `setup`.

## Relacionados

- [182 — Métodos estáticos](182_metodos_estaticos.md)
- [184 — Visibilidade](184_visibilidade.md)
- [189 — Records vs blueprints](189_records_vs_blueprints.md)
