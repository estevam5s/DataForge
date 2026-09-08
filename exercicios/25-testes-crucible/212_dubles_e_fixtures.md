# Exercício 212 — Dublês e fixtures

## Enunciado

Teste uma regra de negócio sem tocar no banco.

## Conceitos

Um serviço que constrói a própria conexão exige subir PostgreSQL para testar uma
validação de nome. Um que **recebe** o repositório por parâmetro se testa com um
dublê, em microssegundos.

```dataforge
repo := Crucible.mock("repositorio")
repo.quando("salvar").devolve("Ana")

s := spawn ServicoDeCadastro(repo)
expect s.cadastrar("Ana") is "Ana"
expect repo.chamado_com("salvar", "Ana") is yes
```

É [inversão de dependência](https://dataforge-lang.vercel.app/docs/oop/solid) na
prática.

## O que observar

**Cobrar o que NÃO aconteceu.** O segundo trial verifica que o repositório não
foi chamado. Sem o dublê, isso exigiria olhar o banco — e um teste que precisa
de banco para verificar uma regra de nome está testando a coisa errada.

**`provide` divide a fixture.** O que vem antes prepara; o que vem depois limpa.
Escrever as duas juntas é o que impede a limpeza de ser esquecida — o modo mais
comum de uma suíte passar a depender de ordem.

**A limpeza roda mesmo com falha**, e só para as fixtures que o trial realmente
usou.

## Armadilhas

- Um mock que devolve sempre a mesma coisa esconde bug de paginação.
  `devolve_em_sequencia` cobre isso.
- Testar o mock em vez do código: se todas as expectativas são sobre chamadas e
  nenhuma sobre resultado, o teste não prova nada.

## Relacionados

- [210 — Isolamento](210_isolamento.md)
- [206 — Relações](../24-banco-de-dados/206_relacoes_sem_n_mais_um.md)
