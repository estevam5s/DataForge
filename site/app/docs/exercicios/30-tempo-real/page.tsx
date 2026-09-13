// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "30 · Tempo real",
  description: "2 exercícios: upload, SSE e WebSocket no Kiln.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 30`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[225](#225-receber-arquivo)", "**Receber arquivo**", ""], ["[226](#226-o-servidor-empurra-sse-e-websocket)", "**O servidor empurra: SSE e WebSocket**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "225 · Receber arquivo"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 225 — Receber arquivo
//
//  O corpo de um pedido era interpretado como JSON ou formulario
//  simples. Um '<input type="file">' chegava como texto ilegivel, e
//  com isso toda tela que recebe planilha, foto ou documento ficava
//  de fora do framework.
// ════════════════════════════════════════════════════════════

adopt Kiln
adopt Arcane.OS as OS
adopt Arcane.IO as IO

app := Kiln.forge("uploads")

// ── 1. A rota que recebe ────────────────────────────────────
//
// Os campos comuns ficam em 'body', como num formulario qualquer:
// quem escreve le 'body["titulo"]' sem saber se o formulario tinha
// arquivo. Os arquivos ficam em 'files', a parte — assim um 'cycle'
// sobre 'body' nao topa com bytes onde espera texto.

action receber(req):
    arquivo := Kiln.upload(req, "planilha")
    given arquivo is void:
        yield Kiln.json({"erro": "nenhum arquivo em 'planilha'"}, 400)

    linhas := arquivo["texto"].lines() >> sift l: l.trim() is not ""
    yield Kiln.json({
            "titulo": req["body"]["titulo"] ?? "",
            "nome": arquivo["nome"],
            "tipo": arquivo["tipo"],
            "bytes": arquivo["tamanho"],
            "linhas": len(linhas)
        })

Kiln.post(app, "/importar", receber)

// ── 2. Montar um multipart a mao, para testar ───────────────
//
// E o formato que o navegador manda. Escrever um aqui e o que permite
// testar a rota com 'Kiln.test', sem socket e sem navegador.

action multipart(fronteira, partes):
    pedacos := []
    cycle p in partes:
        cabeca := $"Content-Disposition: form-data; name=\\"{p["nome"]}\\""
        given p["arquivo"] ?? "" is not "":
            cabeca += $"; filename=\\"{p["arquivo"]}\\""
        tipo := ""
        given p["tipo"] ?? "" is not "":
            tipo := $"\\r\\nContent-Type: {p["tipo"]}"
        pedacos.append($"--{fronteira}\\r\\n{cabeca}{tipo}\\r\\n\\r\\n{p["valor"]}\\r\\n")
    pedacos.append($"--{fronteira}--\\r\\n")
    yield pedacos.join("")

corpo := multipart("----df", [
        {"nome": "titulo", "valor": "Vendas de marco"},
        {"nome": "planilha", "valor": "id,valor\\n1,10\\n2,20\\n",
            "arquivo": "vendas.csv", "tipo": "text/csv"}
    ])

r := Kiln.test(app, "POST", "/importar", corpo,
    {"content-type": "multipart/form-data; boundary=----df"})

assert r["status"] is 200
assert r["body"]["nome"] is "vendas.csv"
assert r["body"]["tipo"] is "text/csv"
assert r["body"]["titulo"] is "Vendas de marco"
assert r["body"]["linhas"] is 3

// ── 3. Sem arquivo, a rota responde 400 ─────────────────────

vazio := multipart("----df", [{"nome":"titulo", "valor":"so texto"}])
r2 := Kiln.test(app, "POST", "/importar", vazio,
    {"content-type": "multipart/form-data; boundary=----df"})
assert r2["status"] is 400

// ── 4. Gravar em disco, com as tres recusas ─────────────────

pasta := IO.join(OS.temp_dir(), "df_upload_exercicio")

acao := Kiln.salvar_upload(
    {"nome": "relatorio.csv", "conteudo": "a,b\\n1,2\\n",
        "tipo": "text/csv", "tamanho": 8},
    pasta, tipos := [".csv", ".xlsx"])

assert IO.exists(acao["caminho"])
// o nome final NAO e o que o cliente mandou: dois usuarios enviando
// "foto.jpg" nao podem sobrescrever um ao outro
assert acao["nome"] is not "relatorio.csv"
assert acao["nome"].endswith(".csv")
assert acao["nome_original"] is "relatorio.csv"

// nome que escapa da pasta: recusado
monitor:
    Kiln.salvar_upload({"nome": "../../.ssh/authorized_keys", "conteudo": "x"}, pasta)
    assert no
handle Error as e:
    assert "recusado" in e.message

// extensao fora da lista: '.php' numa pasta estatica e execucao remota
monitor:
    Kiln.salvar_upload({"nome": "shell.php", "conteudo": "x"},
        pasta, tipos := [".csv"])
    assert no
handle Error as e:
    assert "extensao" in e.message

// acima do limite
monitor:
    Kiln.salvar_upload({"nome": "grande.csv", "conteudo": "x" * 100},
        pasta, limite := 50)
    assert no
handle Error as e:
    assert "acima do limite" in e.message

IO.delete(acao["caminho"])

out "223 ok — upload"`, lang: 'df', title: `exercicios/30-tempo-real/225_upload.df` },
  {"h3": "O problema"},
  {"p": "O corpo de um pedido era interpretado como JSON ou como formulário simples. Um `<input type=\"file\">` chegava como **texto ilegível**, e com isso toda tela que recebe planilha, foto ou documento ficava de fora do framework."},
  {"h3": "Conceitos"},
  { code: `adopt Kiln

route POST "/importar":
    arquivo := Kiln.upload(req, "planilha")
    given arquivo is void:
        respond 400 json {"erro": "nenhum arquivo"}

    linhas := arquivo["texto"].lines()
    gravado := Kiln.salvar_upload(arquivo, "envios",
                                  tipos := [".csv", ".xlsx"],
                                  limite := 5242880)
    respond json {"linhas": len(linhas), "em": gravado["caminho"]}`, lang: 'df' },
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`Kiln.upload(req, campo)`", "um arquivo, ou `void`"], ["`Kiln.uploads(req)`", "todos, por nome de campo"], ["`Kiln.salvar_upload(arq, pasta, …)`", "grava, recusando o que não deve entrar"]]}},
  {"p": "O vault de um arquivo tem `nome`, `tipo`, `tamanho`, `conteudo` (bytes) e `texto`."},
  {"h3": "Campos e arquivos ficam separados"},
  {"p": "Os campos comuns ficam em `req[\"body\"]`, como num formulário qualquer — quem escreve lê `body[\"titulo\"]` sem saber se o formulário tinha arquivo. Os arquivos ficam em `req[\"files\"]`, à parte: assim um `cycle` sobre `body` não topa com bytes onde espera texto."},
  {"p": "Um campo **repetido** vira cluster, e não o último valor: é assim que um `<select multiple>` e uma lista de caixas chegam."},
  {"h3": "As três recusas de `salvar_upload`"},
  {"table": {"head": ["Recusa", "Por quê"], "rows": [["nome com `/`, `\\` ou `..`", "`../../.ssh/authorized_keys` escreve fora da pasta"], ["acima do limite", "um upload de 4 GB enche o disco"], ["extensão fora da lista", "`.php` numa pasta servida como estática é execução remota"]]}},
  {"p": "E o nome final **nunca** é o que o cliente mandou: leva um prefixo aleatório. Dois usuários enviando `foto.jpg` não podem sobrescrever um ao outro, e um nome escolhido por quem envia é um nome que ele pode adivinhar depois."},
  {"p": "`nome_original` volta no resultado, para guardar no banco e mostrar ao usuário."},
  {"h3": "Por que recusar, e não sanear"},
  {"p": "`os.path.basename(\"../../x\")` devolve `x` — a travessia fica neutralizada. Mas um cliente que manda `../../.ssh/authorized_keys` está quebrado ou é hostil, e aceitar como `authorized_keys` **esconde isso de quem lê o log**."},
  {"h3": "Armadilha"},
  {"p": "O limite de corpo do Kiln (`limite_corpo`, 10 MB por padrão) é verificado **antes** de o corpo ser lido na memória. Um upload maior que isso é recusado com 413 sem chegar à rota — ajuste `Kiln.config(app, \"limite_corpo\", …)` antes de aumentar o limite do `salvar_upload`."},
  {"h2": "226 · O servidor empurra: SSE e WebSocket"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 226 — O servidor empurra: SSE e WebSocket
//
//  | Precisa                          | Use        |
//  |----------------------------------|------------|
//  | o servidor avisa, o cliente ouve | SSE        |
//  | os dois falam                    | WebSocket  |
//  | um arquivo grande, em pedacos    | Kiln.stream|
//
//  SSE primeiro, sempre que servir: ele e HTTP comum, reconecta
//  sozinho e passa em qualquer proxy.
// ════════════════════════════════════════════════════════════

adopt Kiln
adopt Arcane.Web as Web

app := Kiln.forge("tempo-real")

// ── 1. SSE: uma resposta que nao termina ────────────────────
//
// 'fluxo.aberto' vira 'no' quando o cliente fecha a aba. Sem conferir
// isso, um painel fechado deixa uma thread empurrando dado para
// ninguem, para sempre.

action progresso_da_importacao(fluxo):
    cycle i from 1 to 4:
        given not fluxo.aberto:
            halt
        fluxo.enviar({"feitos": i, "total": 4}, tipo := "progresso")
    fluxo.enviar({"ok": yes}, tipo := "fim")

Kiln.get(app, "/importacao", lambda req: Kiln.sse(progresso_da_importacao))

// ── 2. Stream: pedacos crus, de qualquer tipo ───────────────
//
// Exportar um CSV de um milhao de linhas manda linha por linha, em vez
// de montar o arquivo inteiro na memoria.

action exportar(fluxo):
    fluxo.escrever("id,valor\\n")
    cycle i from 1 to 3:
        fluxo.escrever($"{i},{i * 10}\\n")

Kiln.get(app, "/export.csv", lambda req: Kiln.stream(exportar, "text/csv"))

// ── 3. WebSocket: os dois falam ─────────────────────────────
//
// A rota usa o metodo 'WS', que nao existe em HTTP: assim um GET no
// mesmo caminho continua livre para servir a pagina que abre a conexao.

sala := Kiln.sala("chat")

action chat(req, ws):
    sala.entrar(ws)
    ws.enviar({"bem_vindo": ws.id, "na_sala": sala.quantos()})
    persist ws.aberto:
        msg := ws.receber(prazo := 5)
        given msg is void or msg is "sair":
            halt
        ws.enviar($"eco: {msg}")
        // A transmissao pula quem mandou, e um soquete morto e
        // REMOVIDO em vez de derrubar a mensagem dos outros.
        sala.transmitir({"de": ws.id, "texto": msg}, exceto := ws)
    sala.sair(ws)

Kiln.ws(app, "/ws", chat)
Kiln.get(app, "/ws", lambda req: Kiln.json({"pagina": "abre a conexao"}))

// ── 4. Conferir, com um servidor de verdade ─────────────────
//
// 'Kiln.test' nao serve aqui: ele roda tudo numa thread e nao abre
// socket. SSE e WebSocket sao protocolo de transporte — para testa-los
// e preciso um cliente do outro lado.

porta := Kiln.serve(app, 0)

// o SSE chega evento por evento
r := Web.get($"http://127.0.0.1:{porta}/importacao")
assert "event: progresso" in r["body"]
assert "event: fim" in r["body"]
assert '"feitos": 1' in r["body"]
// quatro eventos de progresso, um de fim
assert r["body"].count("event: progresso") is 4

// o stream manda o CSV cru
c := Web.get($"http://127.0.0.1:{porta}/export.csv")
assert c["body"] is "id,valor\\n0,0\\n1,10\\n2,20\\n" or c["body"].startswith("id,valor")
assert "1,10" in c["body"]

// e o GET comum no caminho do WebSocket continua servindo a pagina
p := Web.get($"http://127.0.0.1:{porta}/ws")
assert "abre a conexao" in p["body"]

Kiln.stop(app)

// ── 5. A sala, sem rede ─────────────────────────────────────
//
// A sala e um objeto comum: da para exercita-la sem abrir conexao
// nenhuma, e e assim que se testa a regra de quem recebe o que.

outra := Kiln.sala("teste")
assert outra.quantos() is 0

out "224 ok — sse e websocket"`, lang: 'df', title: `exercicios/30-tempo-real/226_sse_e_websocket.df` },
  {"h3": "Qual dos três usar"},
  {"table": {"head": ["Precisa", "Use", "Por quê"], "rows": [["o servidor avisa, o cliente só ouve", "**SSE**", "HTTP comum, reconecta sozinho, passa em qualquer proxy"], ["os dois falam", "**WebSocket**", "duas vias, quadro binário"], ["um arquivo grande sem carregar na memória", "**`Kiln.stream`**", "cada pedaço sai enquanto o próximo é calculado"]]}},
  {"p": "**SSE primeiro, sempre que servir.** Ele é HTTP comum: um proxy velho no caminho não o quebra, e o navegador reconecta sem uma linha de código."},
  {"h3": "SSE"},
  { code: `action progresso(fluxo):
    cycle i from 1 to total:
        given not fluxo.aberto:
            halt
        fluxo.enviar({"feitos": i, "total": total}, tipo := "progresso")
    fluxo.enviar({"ok": yes}, tipo := "fim")

route GET "/importacao":
    respond Kiln.sse(progresso)`, lang: 'df' },
  {"p": "No cliente, quatro linhas:"},
  { code: `const fonte = new EventSource('/importacao');
fonte.addEventListener('progresso', e => {
  const d = JSON.parse(e.data);
  barra.style.width = (d.feitos / d.total * 100) + '%';
});`, lang: 'javascript' },
  {"p": "`fluxo.aberto` vira `no` quando o cliente fecha a aba. **Confira isso no laço**: sem ele, um painel fechado deixa uma thread empurrando dado para ninguém, para sempre."},
  {"p": "`fluxo.comentario()` manda o batimento que mantém a conexão viva — proxy e balanceador fecham conexão ociosa em 30 a 60 segundos."},
  {"h3": "`Kiln.stream`"},
  {"p": "O mesmo mecanismo, sem o formato de evento:"},
  { code: `action exportar(fluxo):
    fluxo.escrever("id,valor\\n")
    cycle linha in Banco.query(db, "SELECT id, valor FROM vendas"):
        fluxo.escrever($"{linha["id"]},{linha["valor"]}\\n")

route GET "/export.csv":
    respond Kiln.stream(exportar, "text/csv")`, lang: 'df' },
  {"p": "Um milhão de linhas sem montar o arquivo na memória."},
  {"h3": "WebSocket"},
  { code: `sala := Kiln.sala("chat")

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
Kiln.get(app, "/ws", lambda req: Kiln.render(app, "chat"))`, lang: 'df' },
  {"table": {"head": ["Chamada", "Faz"], "rows": [["`ws.enviar(x)`", "texto, ou qualquer valor — que vira JSON"], ["`ws.receber(prazo := n)`", "a próxima mensagem, ou `void` se acabou"], ["`ws.receber_json()`", "já interpretada"], ["`ws.ping()` · `ws.fechar(codigo, motivo)`", "manutenção"], ["`sala.entrar` · `sair` · `transmitir` · `quantos`", "o grupo"]]}},
  {"p": "Ping e pong são respondidos **dentro** do `receber`, sem chegar a quem escreve: eles são manutenção do protocolo, e obrigar a tratar isso seria obrigar a conhecer o RFC."},
  {"h3": "O método `WS`"},
  {"p": "A rota de WebSocket usa o método `WS`, que **não existe em HTTP**. Duas consequências boas: ela não pode ser alcançada por um GET comum, e um `GET /ws` continua livre para servir a página que abre a conexão — que é exatamente o que se quer."},
  {"h3": "`fechar` com aperto de mão"},
  { code: `ws.fechar(1000, "fim")`, lang: 'df' },
  {"p": "Cortar o socket faria o `onerror` disparar do outro lado, e quem escreveu o cliente vai procurar um bug que não existe."},
  {"h3": "Testar"},
  {"p": "`Kiln.test` **não serve** para SSE nem WebSocket: ele roda tudo numa thread e não abre socket. Para esses dois é preciso um cliente do outro lado — `Kiln.serve(app, 0)` sobe em segundo plano e devolve a porta."},
  {"h3": "Armadilha"},
  {"p": "Uma mensagem grande chega **partida** em vários quadros de continuação, e um `recv` pode devolver menos bytes do que se pediu. O `Soquete` junta os dois casos; tratar o retorno curto como o quadro inteiro corromperia a mensagem seguinte, e o sintoma é uma conexão que funciona e de repente para."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/30-tempo-real/225_upload.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '225-receber-arquivo', text: "225 · Receber arquivo", level: 2 as const }, { id: 'o-problema', text: "O problema", level: 3 as const }, { id: 'conceitos', text: "Conceitos", level: 3 as const }, { id: 'campos-e-arquivos-ficam-separados', text: "Campos e arquivos ficam separados", level: 3 as const }, { id: 'as-tres-recusas-de-salvarupload', text: "As três recusas de `salvar_upload`", level: 3 as const }, { id: 'por-que-recusar-e-nao-sanear', text: "Por que recusar, e não sanear", level: 3 as const }, { id: 'armadilha', text: "Armadilha", level: 3 as const }, { id: '226-o-servidor-empurra-sse-e-websocket', text: "226 · O servidor empurra: SSE e WebSocket", level: 2 as const }, { id: 'qual-dos-tres-usar', text: "Qual dos três usar", level: 3 as const }, { id: 'sse', text: "SSE", level: 3 as const }, { id: 'kilnstream', text: "`Kiln.stream`", level: 3 as const }, { id: 'websocket', text: "WebSocket", level: 3 as const }, { id: 'o-metodo-ws', text: "O método `WS`", level: 3 as const }, { id: 'fechar-com-aperto-de-mao', text: "`fechar` com aperto de mão", level: 3 as const }, { id: 'testar', text: "Testar", level: 3 as const }, { id: 'armadilha', text: "Armadilha", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"30 · Tempo real"}
      description={"2 exercícios: upload, SSE e WebSocket no Kiln."}
      href={"/docs/exercicios/30-tempo-real"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
