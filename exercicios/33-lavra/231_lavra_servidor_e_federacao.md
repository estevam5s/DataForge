# Exercicio 231 — Lavra: contratos, mudanças, servidor e federação

## Enunciado

Sirva o esquema por HTTP e componha dois serviços num só.

## Contratos

Um **contrato** são campos que vários tipos prometem ter:

```dataforge
Lavra.tipo(esq, Artigo, cumpre := ["Conteudo"])
Lavra.tipo(esq, Video, cumpre := ["Conteudo"])

Lavra.contrato(esq, "Conteudo", {"id": "Integer", "titulo": "String"},
    resolve_tipo := que_tipo)
```

Quem consulta pede os campos do contrato, e usa `... em Tipo:` para pedir o que
só existe num deles:

```lavra
busca:
    acervo:
        titulo
        ... em Video:
            minutos
```

O `resolve_tipo` responde **qual tipo concreto é aquele valor**. Sem ele, o
Lavra tenta descobrir pelo nome do record — e quando não consegue, diz isso com
a lista dos candidatos, em vez de devolver um objeto pela metade.

O contrato é conferido na montagem: um tipo que declara cumpri-lo e não tem um
dos campos **para o `Lavra.conferir`**.

## Mudanças

A escrita aparece no **nome da operação**:

```lavra
mudanca:
    criarArtigo(dados: {titulo: "Recem-forjado"}):
        id
        titulo
```

Quem lê a consulta sabe, sem abrir o resolvedor, se aquilo muda alguma coisa —
e é o que permite a um intermediário guardar uma `busca` em cache e nunca uma
`mudanca`.

### Entrada e saída são tipos diferentes

```dataforge
Lavra.entrada(esq, {"titulo": "String"}, nome := "NovoArtigo")
```

O `Artigo` que sai tem `id`; o `NovoArtigo` que entra não tem. Usar o mesmo tipo
nos dois lados obrigaria a marcar metade dos campos como opcionais — e aí nenhum
deles seria conferido.

## Servir por HTTP

```dataforge
par := Lavra.em_segundo_plano(esq)
app := par[0]
porta := par[1]
```

Uma rota, um método:

| Rota | O que faz |
|------|-----------|
| `POST /lavra` | executa a consulta |
| `GET /lavra` | devolve o esquema em texto |
| `WS /lavra/assinar` | as assinaturas |

Não há uma rota por busca: a consulta já diz o que quer, e uma rota por campo
desfaria a razão de o Lavra existir.

### Erro de consulta responde 200

Parece errado e não é: o **HTTP falou**, e a resposta tem `dados` e `erros`. Um
400 obrigaria o cliente a ter dois caminhos de leitura para o mesmo corpo, e
esconderia o caso normal — dados parciais com um erro num campo.

O 400 fica para o que nem chegou a ser consulta (corpo ilegível, sem
`consulta`), e o 500 para o que quebrou fora dela.

## Federação

Cada time tem o seu serviço. Quem consulta não quer saber disso:

```dataforge
portao := Lavra.portao()
Lavra.juntar(portao, "contas", contas)
Lavra.juntar(portao, "vendas", vendas)

Lavra.estender(portao, "Conta", "vendas", "[Venda!]!", resolve := vendas_da_conta)
```

O campo que atravessa a fronteira é declarado como **extensão** — ele não
pertence a nenhum dos dois serviços sozinho.

### Conflito de nome é erro

Dois serviços que declaram `Usuario` param a composição. Fundir os dois em
silêncio faria a resposta depender da **ordem do `juntar`** — que funciona na
máquina de quem escreveu e muda quando alguém reordena duas linhas.

### O mapa

```dataforge
out Lavra.mapa(portao)
```

É a resposta para "quem declara isto?" — a pergunta que mais se faz num esquema
federado, e a que mais custa responder lendo código de três repositórios.

## Saída esperada

```
{acervo: [{titulo: Sobre a forja}, {titulo: Como fundir, minutos: 12}]}
200 3
{conta: {nome: Ana, vendas: [{total: 9.9}]}}
contas vendas
231 ok
```

## Para experimentar

- Peça `minutos` sem o `... em Video:` e veja a validação recusar — `Conteudo`
  não promete `minutos`.
- Junte dois esquemas com um tipo de mesmo nome e leia a mensagem.
- Chame `GET /lavra` no navegador: o esquema em texto é o que se versiona.
