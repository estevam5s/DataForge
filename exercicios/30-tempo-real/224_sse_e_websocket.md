# Exercicio 224 — O servidor empurra: SSE e WebSocket

## Enunciado

Faça o servidor avisar o cliente sem ele perguntar. Duas vezes: uma só
de ida, outra nas duas direções.

## Qual dos três usar

| Precisa | Use | Por quê |
|---|---|---|
| o servidor avisa, o cliente só ouve | **SSE** | HTTP comum, reconecta sozinho, passa em qualquer proxy |
| os dois falam | **WebSocket** | duas vias, quadro binário |
| um arquivo grande sem carregar na memória | **`Kiln.stream`** | cada pedaço sai enquanto o próximo é calculado |

**SSE primeiro, sempre que servir.** Ele é HTTP comum: um proxy velho no
caminho não o quebra, e o navegador reconecta sem uma linha de código.

## SSE

```dataforge
action progresso(fluxo):
    cycle i from 1 to total:
        given not fluxo.aberto:
            halt
        fluxo.enviar({"feitos": i, "total": total}, tipo := "progresso")
    fluxo.enviar({"ok": yes}, tipo := "fim")

route GET "/importacao":
    respond Kiln.sse(progresso)
```

No cliente, quatro linhas:

```javascript
const fonte = new EventSource('/importacao');
fonte.addEventListener('progresso', e => {
  const d = JSON.parse(e.data);
  barra.style.width = (d.feitos / d.total * 100) + '%';
});
```

`fluxo.aberto` vira `no` quando o cliente fecha a aba. **Confira isso
no laço**: sem ele, um painel fechado deixa uma thread empurrando dado
para ninguém, para sempre.

`fluxo.comentario()` manda o batimento que mantém a conexão viva —
proxy e balanceador fecham conexão ociosa em 30 a 60 segundos.

## `Kiln.stream`

O mesmo mecanismo, sem o formato de evento:

```dataforge
action exportar(fluxo):
    fluxo.escrever("id,valor\n")
    cycle linha in Banco.query(db, "SELECT id, valor FROM vendas"):
        fluxo.escrever($"{linha["id"]},{linha["valor"]}\n")

route GET "/export.csv":
    respond Kiln.stream(exportar, "text/csv")
```

Um milhão de linhas sem montar o arquivo na memória.

## WebSocket

```dataforge
sala := Kiln.sala("chat")

action chat(req, ws):
    sala.entrar(ws)
    ws.enviar({"bem_vindo": ws.id, "na_sala": sala.quantos()})
    persist ws.aberto:
        msg := ws.receber(prazo := 30)
        given msg is void or msg is "sair":
            halt
        sala.transmitir({"de": ws.id, "texto": msg}, exceto := ws)
    sala.sair(ws)

Kiln.ws(app, "/ws", chat)
Kiln.get(app, "/ws", lambda req: Kiln.render(app, "chat"))
```

| Chamada | Faz |
|---|---|
| `ws.enviar(x)` | texto, ou qualquer valor — que vira JSON |
| `ws.receber(prazo := n)` | a próxima mensagem, ou `void` se acabou |
| `ws.receber_json()` | já interpretada |
| `ws.ping()` · `ws.fechar(codigo, motivo)` | manutenção |
| `sala.entrar` · `sair` · `transmitir` · `quantos` | o grupo |

Ping e pong são respondidos **dentro** do `receber`, sem chegar a quem
escreve: eles são manutenção do protocolo, e obrigar a tratar isso seria
obrigar a conhecer o RFC.

## O método `WS`

A rota de WebSocket usa o método `WS`, que **não existe em HTTP**. Duas
consequências boas: ela não pode ser alcançada por um GET comum, e um
`GET /ws` continua livre para servir a página que abre a conexão — que é
exatamente o que se quer.

## `fechar` com aperto de mão

```dataforge
ws.fechar(1000, "fim")
```

Cortar o socket faria o `onerror` disparar do outro lado, e quem
escreveu o cliente vai procurar um bug que não existe.

## Testar

`Kiln.test` **não serve** para SSE nem WebSocket: ele roda tudo numa
thread e não abre socket. Para esses dois é preciso um cliente do outro
lado — `Kiln.serve(app, 0)` sobe em segundo plano e devolve a porta.

## Armadilha

Uma mensagem grande chega **partida** em vários quadros de continuação,
e um `recv` pode devolver menos bytes do que se pediu. O `Soquete` junta
os dois casos; tratar o retorno curto como o quadro inteiro corromperia
a mensagem seguinte, e o sintoma é uma conexão que funciona e de repente
para.
