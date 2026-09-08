# Exercício 206 — Relações e o problema do N+1

## Enunciado

Carregue os pedidos de cem usuários em duas consultas.

## Conceitos

Buscar cem usuários e ler `usuario.pedidos` de cada um faz **cento e uma**
consultas: uma para os usuários, e uma por usuário.

Isso não aparece em desenvolvimento, com três linhas na tabela. Aparece em
produção, com dez mil — e é o bug de ORM mais comum que existe.

```dataforge
// duas consultas, para qualquer quantidade
com_pedidos := Usuario.com(Usuario.todos(), "pedidos")
```

## O que observar

**A relação NÃO carrega sozinha.** Ou você pede com `com(...)`, ou ela não vem.
Um ORM que carrega ao ser lida funciona — devagar, e só quando é tarde demais
para perceber.

**Duas consultas, e há teste contando.** A suíte do Forge instrumenta a conexão
e conta as chamadas. Se alguém trocar a implementação por uma que faz N+1, o
teste falha.

**Uma relação que não existe avisa**, e lista as que existem.

## Armadilhas

- `tem_muitos` procura a chave `<modelo>_id` na outra tabela. Se o nome for
  outro, passe-o: `tem_muitos("pedidos", "Pedido", "dono_id")`.
- Sem índice na chave estrangeira, a segunda consulta varre a tabela. Declare
  `"indice": yes` no campo.

## Relacionados

- [205 — Modelos e validação](205_modelos_e_validacao.md)
- [213 — Medir o crescimento](../26-complexidade/213_medir_o_crescimento.md)
