# 268 — o que separa um valor de uma entidade

A distinção que decide metade da modelagem, e que não é sobre
mutabilidade. Duas pessoas com o mesmo nome são **duas pessoas**; a
mesma pessoa com outro nome continua sendo ela. O que separa as duas é
a **continuidade**.

## O valor é igual por conteúdo

`Dinheiro(10, "BRL")` e outro `Dinheiro(10, "BRL")` são o **mesmo
valor** — não dois valores parecidos. E é por isso que ele serve de
chave num vault: a igualdade e o hash andam juntos.

Trocar um campo não muda o valor: cria **outro**. `dez.com(quantia := 20)`
devolve um novo, e o original continua valendo 10.

## A entidade é igual por identidade

`D.entidade("Pessoa", "1", nome := "Ana")` e a mesma id com outro nome
são a mesma pessoa. Dois nomes iguais com ids diferentes são duas.

E o **tipo** faz parte da identidade: um `Pedido` de id `"1"` não é uma
`Pessoa` de id `"1"`. Sem isso, dois repositórios distintos colidiriam
na mesma chave.

## E ela muda sem deixar de ser ela

`ana.mudar(nome := "Ana Souza")` continua igual a `ana_maria`. É o
ponto: a entidade é o que sobrevive à mudança de estado.

---

Se a sua peça precisa distinguir duas instâncias iguais, ela é uma
**entidade**. Se duas iguais são a mesma coisa, é um **valor** — e aí
ela não tem lugar num repositório.
