// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/kiln_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Tempo real",
  description: "SSE para o servidor empurrar, WebSocket para os dois falarem, e stream para o arquivo grande.",
};

const blocos: Bloco[] = [
  {"p": "Três mecanismos, e a escolha entre eles é quase sempre óbvia."},
  {"table": {"head": ["Precisa", "Use", "Por quê"], "rows": [["o servidor avisa, o cliente só ouve", "**SSE**", "HTTP comum, reconecta sozinho, passa em qualquer proxy"], ["os dois falam", "**WebSocket**", "duas vias, quadro binário"], ["um arquivo grande sem carregar na memória", "**`Kiln.stream`**", "cada pedaço sai enquanto o próximo é calculado"]]}},
  {"callout": {"tipo": "dica", "titulo": "SSE primeiro, sempre que servir", "texto": "Ele é HTTP comum: um proxy velho no caminho não o quebra, e o navegador reconecta sem uma linha de código. WebSocket entra quando o cliente também precisa falar."}},
  {"h2": "SSE — o servidor empurra"},
  { code: `adopt Kiln

action progresso(fluxo):
    total := 200
    cycle i from 1 to total:
        given not fluxo.aberto:
            halt
        importar_linha(i)
        given i % 10 is 0:
            fluxo.enviar({"feitos": i, "total": total}, tipo := "progresso")
    fluxo.enviar({"ok": yes}, tipo := "fim")

server importador on 8080:
    route GET "/importacao":
        respond Kiln.sse(progresso)`, lang: 'df' },
  {"p": "No cliente, quatro linhas:"},
  { code: `const fonte = new EventSource('/importacao');

fonte.addEventListener('progresso', e => {
  const d = JSON.parse(e.data);
  barra.style.width = (d.feitos / d.total * 100) + '%';
});
fonte.addEventListener('fim', () => fonte.close());`, lang: 'javascript' },
  {"table": {"head": ["Método do fluxo", "Faz"], "rows": [["`fluxo.enviar(dados, tipo, identificador)`", "um evento; `no` se o cliente já foi"], ["`fluxo.escrever(texto)`", "um pedaço cru, sem formato de evento"], ["`fluxo.comentario()`", "o batimento que mantém a conexão viva"], ["`fluxo.aberto`", "`no` quando o cliente fechou a aba"], ["`fluxo.enviados`", "quantos eventos saíram"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Confira `fluxo.aberto` no laço", "texto": "Sem isso, um painel fechado deixa uma thread empurrando dado para ninguém, para sempre. `enviar` devolve `no` quando o cliente foi embora — e é por isso que ele devolve algo."}},
  {"p": "`fluxo.comentario()` a cada 15 segundos evita que proxy e balanceador fechem a conexão ociosa — eles fecham tipicamente em 30 a 60. O navegador ignora o comentário."},
  {"p": "A resposta já sai com `Cache-Control: no-cache`, `Connection: keep-alive` e `X-Accel-Buffering: no`. O último importa: o nginx guarda resposta em buffer por padrão, e com isso o evento só chegaria quando o buffer enchesse — o que destrói o SSE."},
  {"h3": "O formato, se você quiser montá-lo"},
  { code: `Kiln.evento({"n": 1}, tipo := "tick", identificador := "7")
// "id: 7\\nevent: tick\\ndata: {\\"n\\": 1}\\n\\n"`, lang: 'df' },
  {"p": "O `\\n\\n` final não é enfeite: é ele que diz ao navegador que o evento acabou. E um texto com `\\n` dentro leva um `data:` por linha — senão o evento quebraria no meio."},
  {"h2": "`Kiln.stream` — o arquivo grande"},
  { code: `action exportar(fluxo):
    fluxo.escrever("id,valor,mes\\n")
    cycle linha in Banco.query(db, "SELECT id, valor, mes FROM vendas"):
        fluxo.escrever($"{linha["id"]},{linha["valor"]},{linha["mes"]}\\n")

route GET "/export.csv":
    respond Kiln.stream(exportar, "text/csv")`, lang: 'df' },
  {"p": "Um milhão de linhas sem montar o arquivo na memória. O mesmo mecanismo do SSE, sem o formato de evento."},
  {"h2": "WebSocket"},
  { code: `sala := Kiln.sala("chat")

action chat(req, ws):
    quem := req["session"]["usuario"] ?? ws.id
    sala.entrar(ws)
    sala.transmitir({"entrou": quem, "agora": sala.quantos()}, exceto := ws)

    persist ws.aberto:
        msg := ws.receber(prazo := 60)
        given msg is void or msg is "sair":
            halt
        sala.transmitir({"de": quem, "texto": msg})

    sala.sair(ws)
    sala.transmitir({"saiu": quem, "agora": sala.quantos()})

server app on 8080:
    route GET "/chat":
        render "chat"

Kiln.ws(app, "/ws", chat)
Kiln.ignite(app, 8080)`, lang: 'df' },
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`ws.enviar(x)`", "texto, ou qualquer valor — que vira JSON"], ["`ws.enviar_json(v)`", "o mesmo, explícito"], ["`ws.receber(prazo := n)`", "a próxima mensagem, ou `void` se a conexão acabou"], ["`ws.receber_json()`", "já interpretada; `void` se não for JSON"], ["`ws.ping()`", "um ping"], ["`ws.fechar(codigo, motivo)`", "fecha com aperto de mão"], ["`ws.aberto` · `ws.id`", "estado e identidade"], ["`ws.recebidos` · `ws.enviados`", "contagem"]]}},
  {"h3": "A sala"},
  { code: `sala.entrar(ws)                              // devolve quantos
sala.sair(ws)
sala.quantos()
sala.transmitir(mensagem, exceto := ws)      // devolve para quantos chegou
sala.fechar_todos("servidor encerrando")`, lang: 'df' },
  {"p": "Um soquete morto é **removido** em vez de levantar: um cliente que fechou a aba não pode derrubar a mensagem dos outros. E a trava protege a lista — duas threads entrando e saindo ao mesmo tempo é o caso normal, não a exceção."},
  {"h3": "O método `WS`"},
  {"p": "A rota de WebSocket usa o método `WS`, que **não existe em HTTP**. Duas consequências boas: ela não pode ser alcançada por um GET comum, e um `GET /ws` continua livre para servir a página que abre a conexão."},
  {"h3": "Detalhes do protocolo que você não precisa conhecer"},
  {"table": {"head": ["O quê", "Quem trata"], "rows": [["o handshake (`Sec-WebSocket-Accept`)", "o Kiln"], ["ping e pong", "dentro do `receber` — obrigar a tratar isso seria obrigar a conhecer o RFC"], ["máscara do cliente", "o Kiln (o servidor nunca mascara)"], ["mensagem partida em vários quadros", "juntada antes de chegar a você"], ["`recv` devolvendo menos bytes do que se pediu", "o leitor insiste até completar"], ["um quadro que anuncia 8 exabytes", "recusado com o código 1009"]]}},
  {"callout": {"tipo": "dica", "titulo": "Feche com aperto de mão", "texto": "`ws.fechar(1000, \"fim\")` faz o navegador saber que acabou. Cortar o socket faria o `onerror` disparar do outro lado, e quem escreveu o cliente vai procurar um bug que não existe."}},
  {"h2": "Testar"},
  {"p": "`Kiln.test` **não serve** para SSE nem WebSocket: ele roda tudo numa thread e não abre socket. Para esses dois é preciso um cliente do outro lado."},
  { code: `porta := Kiln.serve(app, 0)        // segundo plano; devolve a porta

r := Web.get($"http://127.0.0.1:{porta}/importacao")
assert "event: progresso" in r["body"]

Kiln.stop(app)`, lang: 'df' },
  {"h2": "O que o Kiln continua não tendo"},
  {"p": "HTTP/2 e TLS. Ele roda sobre o `http.server` do Python; em produção pública, ponha um nginx ou Caddy na frente — e o WebSocket atravessa proxy reverso sem configuração especial em nenhum dos dois."},
  {"p": "Para um painel que só precisa mostrar dado fresco, a [Vitrine](/docs/vitrine/producao) tem `V.atualizar_a_cada(n)`, que é por pergunta e mais simples que os dois."},
];

const headings = [{ id: 'sse-o-servidor-empurra', text: "SSE — o servidor empurra", level: 2 as const }, { id: 'o-formato-se-voce-quiser-monta-lo', text: "O formato, se você quiser montá-lo", level: 3 as const }, { id: 'kilnstream-o-arquivo-grande', text: "`Kiln.stream` — o arquivo grande", level: 2 as const }, { id: 'websocket', text: "WebSocket", level: 2 as const }, { id: 'a-sala', text: "A sala", level: 3 as const }, { id: 'o-metodo-ws', text: "O método `WS`", level: 3 as const }, { id: 'detalhes-do-protocolo-que-voce-nao-precisa-conhecer', text: "Detalhes do protocolo que você não precisa conhecer", level: 3 as const }, { id: 'testar', text: "Testar", level: 2 as const }, { id: 'o-que-o-kiln-continua-nao-tendo', text: "O que o Kiln continua não tendo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Tempo real"}
      description={"SSE para o servidor empurrar, WebSocket para os dois falarem, e stream para o arquivo grande."}
      href={"/docs/kiln/tempo-real"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
