# Exercicio 229 — Lavra: o esquema e a consulta

## Enunciado

Declare um esquema a partir de records e peça exatamente os campos que quer.

## O problema que o Lavra resolve

Uma rota REST devolve o que o **servidor** decidiu devolver:

```json
GET /usuarios/1
{"id": 1, "nome": "Ana", "email": "…", "criado_em": "…", "endereco": {…},
 "preferencias": {…}, "ultimo_acesso": "…"}
```

Quem só queria o nome carregou tudo. Quem queria o nome **e os pedidos** faz
uma segunda chamada. Numa tela de celular com rede ruim, as duas coisas custam —
e as duas aparecem como "o app está lento".

Com o Lavra, quem pergunta diz o que precisa:

```lavra
busca:
    usuario(id: 1):
        nome
        pedidos:
            numero
```

## O esquema nasce dos seus records

Esta é a decisão que define o módulo:

```dataforge
record Usuario:
    id: Integer
    nome: String
    email: String

Lavra.tipo(esq, Usuario)
```

O `record` já diz nome, campo e tipo. Um arquivo de esquema ao lado seria uma
**segunda fonte de verdade** para divergir da primeira — e esse é exatamente o
defeito que este projeto persegue em todo lugar.

O que o record não diz — o que é obrigatório, o que é lista de quê, qual campo
é calculado e por quem — entra com `Lavra.campo`.

## A notação de tipo

| Escrita | Significa |
|---------|-----------|
| `String` | pode ser `void` |
| `String!` | **nunca** é `void` |
| `[Pedido]` | lista que pode ser void, de itens que podem ser void |
| `[Pedido!]!` | lista que nunca é void, de itens que nunca são void |

O `!` não é decoração. Um campo que admite `void` vira `void` quando o
resolvedor falha, e o resto da resposta segue. Um `!` **sobe** o erro para o
pai, até achar alguém que admita `void`.

É a única forma de a promessa valer alguma coisa: se um `String!` pudesse
voltar vazio, quem consome teria de conferir cada campo mesmo assim.

## Campo calculado

`pedidos` não existe no record `Usuario` — ele é uma relação, e quem responde
por ele é o resolvedor:

```dataforge
action pedidos_de(u):
    yield [p cycle p in pedidos given p.usuario_id is u.id]

Lavra.campo(esq, "Usuario", "pedidos", "[Pedido!]!", resolve := pedidos_de)
```

Repare que `pedidos_de` recebe **um** argumento. A assinatura completa é
`(pai, args, ctx)`, e o Lavra chama com quantos a ação aceitar — exigir os três
faria toda linha carregar um `_, _` que não diz nada.

## `conferir` fecha o esquema

```dataforge
Lavra.conferir(esq)
```

Confere que todo tipo citado existe, que todo contrato é cumprido e que há ao
menos uma busca. Ele falha **aqui** — na montagem —, e não na primeira consulta
que por acaso pedir aquele campo, que pode ser meses depois, em produção.

## Apelidos

```lavra
busca:
    ana: usuario(id: 1):
        nome
    bia: usuario(id: 2):
        nome
```

Sem apelido, os dois `usuario` colidiriam na resposta. É também como se pede o
mesmo campo com argumentos diferentes na mesma consulta.

## Variáveis

```lavra
busca Um($id: Integer!):
    usuario(id: $id):
        nome
```

A consulta é uma só; o valor muda. É o que permite guardá-la como constante no
cliente, em vez de montá-la com concatenação — que é de onde vem injeção.

## Saída esperada

```
{usuario: {nome: Ana, pedidos: [{numero: P-1, total: 99.9}, {numero: P-2, total: 15.0}]}}
{ana: {nome: Ana}, bia: {nome: Bia}}
'Usuario' não tem o campo 'nomee' | você quis dizer 'nome'?
229 ok
```

## Para experimentar

- Peça `email` e veja-o aparecer; tire-o e veja-o sumir. É a diferença inteira.
- Troque `Integer!` por `Integer` no argumento `id` e chame sem passá-lo.
- Declare `Lavra.tipo(esq, Usuario, esconder := ["email"])` e tente pedir
  `email`. O campo deixa de existir para quem consulta — é a garantia mais
  barata que existe.
