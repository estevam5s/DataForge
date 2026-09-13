# Exercicio 237 — Eventos, linha de comando, e-mail e HTML

## Enunciado

Junte as peças que faltavam para um programa completo.

## Eventos: duas partes que não se conhecem

```dataforge
loja.ao("venda", lambda pedido: gravar_nota(pedido))
loja.ao("venda", lambda pedido: avisar_estoque(pedido))

quantos := loja.emitir("venda", pedido)
```

**`emitir` devolve quantos ouviram**, e zero é informação: o evento com o nome
errado não falha, ele simplesmente não chega — e essa é a falha mais difícil de
achar num sistema de eventos.

### O ouvinte que quebra sai

Um ouvinte quebrado que continua inscrito quebra **a cada evento**, para
sempre, e some no meio do log. Ele é removido e o erro vai para `emissor.erros`.

### Inscrever num laço é recusado

Mil ouvintes no mesmo evento quase sempre significa um `ao(...)` dentro de um
laço ou de um handler — cada volta inscreve mais um, e nenhum sai.

## O contexto atravessa as camadas

```dataforge
Eventos.com_contexto({"pedido": "P-9"}, lambda => processar())

// dez camadas abaixo, sem ter recebido nada
Eventos.por("pedido")      // "P-9"
```

É **por thread**. Um vault global serviria até o segundo pedido simultâneo — e
aí o id de um apareceria no log do outro. O Kiln atende um pedido por thread.

## A linha de comando

A ajuda é **gerada da declaração**. Escrita à mão, ela envelhece no primeiro
flag novo — e a ajuda errada é pior que nenhuma, porque quem lê confia nela.

O erro sugere o que existe e sai com **código 2**: 1 é "o programa rodou e deu
errado", 2 é "você chamou errado". Um script que testa `$?` precisa distinguir
os dois.

```
relatorio: não conheço '--mess'.
  Você quis dizer '--mes'?
```

## E-mail

Três coisas que o exercício prova:

1. **O HTML ganha alternativa em texto.** Sem ela, o cliente de texto puro
   mostra a marcação crua — e é o que boa parte dos leitores de tela recebe.
2. **A cópia oculta não vira cabeçalho.** Um Bcc escrito no cabeçalho é
   visível para todo mundo, o oposto do que ele significa.
3. **`prever` mostra sem mandar.** O erro mais caro daqui é disparar mil
   e-mails de teste para endereços reais.

A caixa de teste tem o **mesmo contrato** do envio real, então o código que
envia não muda entre o teste e a produção.

## HTML

O seletor é **CSS**, e não XPath: `div.preco > span` é o que quem escreve HTML
já sabe de cor.

O texto junta com **espaço**:

```html
<span class="preco"><b>R$</b> <span>450,00</span></span>
```

Colado, isso viraria `R$450,00`. Com espaço é o que a página mostra — e é o que
quem extrai quer.

### As duas defesas

| Chamada | Para quê |
|---------|----------|
| `escapar` | antes de mostrar um texto que veio de fora |
| `limpar` | tirar **toda** a marcação, e o conteúdo de `<script>` junto |
| `podar` | deixar alguma marcação, pela lista de **permitidas** |

Um `limpar` que só tira as tags deixa o corpo do `<script>` como texto — e aí o
"texto limpo" contém exatamente o código que se queria tirar.

E a lista de `podar` é de **permitidas** porque uma lista de proibidas esquece
a próxima tag perigosa que o navegador inventar.

## Saída esperada

```
9 json yes out.json
Relatorio de setembro -> [chefe@exemplo.br, auditoria@exemplo.br]
237 ok
```

## Para experimentar

- Emita um evento com o nome errado e repare no zero.
- Inscreva num laço de mil voltas e leia a mensagem.
- Poda um comentário com `<img src=x onerror=alert(1)>`.
