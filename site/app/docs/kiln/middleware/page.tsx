import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Middleware",
  description: "CORS, log, autenticação e limite de taxa — e por que a ordem importa.",
};

const blocos: Bloco[] = [
  {"h2": "A regra"},
  {"p": "Middleware roda antes de toda rota. **Se devolve uma resposta, a cadeia para ali.** Se devolve `void`, o pedido segue — e o que ele guardou em `req[\"state\"]` chega na rota."},
  { code: `server api on 8080:
    middleware Kiln.rate_limit(60, 60)
    middleware Kiln.logger()
    middleware Kiln.auth(conferir_token)

    route GET "/eu":
        respond json {"usuario": req["state"]["user"]}` },
  {"h2": "Os prontos"},
  {"table": {"head": ["Middleware", "Faz"], "rows": [
    ["`Kiln.cors(origens)`", "responde o preflight `OPTIONS` e libera origens"],
    ["`Kiln.logger()`", "uma linha por pedido no terminal"],
    ["`Kiln.rate_limit(max, janela)`", "429 + `Retry-After` ao estourar"],
    ["`Kiln.auth(verificador)`", "401 sem credencial; põe o usuário em `state`"],
    ["`Kiln.guard(condicao, status, msg)`", "middleware a partir de qualquer condição"]
  ]}},
  {"h2": "A ordem importa"},
  { code: `// certo
middleware Kiln.rate_limit(60, 60)
middleware Kiln.auth(conferir)

// errado
middleware Kiln.auth(conferir)
middleware Kiln.rate_limit(60, 60)` },
  {"p": "Na ordem errada, um pedido barrado pelo `auth` nunca chega a ser **contado** — e quem está martelando a porta com credenciais inválidas é justamente quem você quer limitar. O limite vem primeiro, sempre."},
  {"h2": "Autenticação é sua"},
  { code: `action conferir(token):
    linhas := DB.query(banco,
        "SELECT usuario FROM sessoes WHERE token = ?", [token])
    yield linhas[0]["usuario"] given len(linhas) bigger 0 otherwise void

middleware Kiln.auth(conferir)` },
  {"p": "`Kiln.auth` cuida do protocolo: lê o `Authorization`, devolve 401 com `WWW-Authenticate`, e põe o resultado em `req[\"state\"][\"user\"]`. Quem decide se o token vale é a sua ação — o Kiln não escolhe seu banco nem seu formato de token."},
  {"h2": "Middleware próprio"},
  { code: `action so_de_dia(req):
    hora := Time.now().hour
    given hora smaller 8 or hora bigger_eq 18:
        yield Kiln.json({"erro": "fora do horário"}, 503)
    yield void        // void deixa passar

middleware so_de_dia` },
  {"p": "Devolva algo **só quando for para cortar** o pedido. Um middleware que devolve um valor sem querer interrompe a cadeia e a rota nunca roda — e nada no terminal explica por quê."},
  {"h2": "Depois da resposta"},
  { code: `Kiln.after(app, lambda req, resp => Kiln.header(
    resp, "X-Powered-By", "DataForge"))` },
  {"p": "Roda com a resposta pronta, para carimbar cabeçalhos ou medir. Um erro aqui é engolido: nada pode derrubar uma resposta que já está montada."},
  {"h2": "CORS"},
  { code: `middleware Kiln.cors()                       // libera tudo
middleware Kiln.cors("https://meusite.com")  // uma origem` },
  {"p": "O `OPTIONS` é respondido no middleware e **nunca chega na rota** — por isso você não precisa registrar uma rota `OPTIONS` para cada caminho."},
  {"p": "E o `Access-Control-Allow-Origin` vai na **resposta real**, não só no preflight — inclusive nas de erro. Um 404 sem o cabeçalho faz o navegador esconder o corpo, e quem escreveu o cliente vê \"erro de CORS\" em vez do erro de verdade."},
  {"callout": {"tipo": "nota", "titulo": "Um cabeçalho só no preflight não serve para nada", "texto": "Foi um bug real: o middleware respondia o `OPTIONS` com os quatro cabeçalhos e guardava a origem num campo que **ninguém lia**. O navegador aprovava o preflight e então bloqueava o `fetch`. O `curl` funcionava, o servidor respondia 200 com o corpo certo, e só o navegador recusava — com uma mensagem que manda mexer no middleware que já estava lá."}},
  {"p": "Com uma origem específica, a resposta leva `Vary: Origin`: sem ele um cache intermediário serve a resposta de um site para outro, com o cabeçalho apontando para a origem errada. Com `*` não há `Vary` — é a mesma resposta para todos, e ali ele só estragaria o cache."},
  {"p": "Uma rota que declara a própria origem vence o middleware:"},
  { code: `route GET "/parceiro":
    r := Kiln.json(dados)
    Kiln.header(r, "Access-Control-Allow-Origin", "https://parceiro.com")
    respond r` },
  {"h2": "Limite de taxa: a letra miúda"},
  {"p": "A contagem é **por processo e em memória**: com vários processos, cada um tem a sua, e o limite efetivo é o número de processos vezes o teto. Serve muito bem para uma aplicação de um processo e para conter abuso acidental; para um limite rígido, use um contador compartilhado."},
];

const headings = [{ id: 'a-regra', text: "A regra", level: 2 as const }, { id: 'os-prontos', text: "Os prontos", level: 2 as const }, { id: 'a-ordem-importa', text: "A ordem importa", level: 2 as const }, { id: 'autenticacao-e-sua', text: "Autenticação é sua", level: 2 as const }, { id: 'middleware-proprio', text: "Middleware próprio", level: 2 as const }, { id: 'depois-da-resposta', text: "Depois da resposta", level: 2 as const }, { id: 'cors', text: "CORS", level: 2 as const }, { id: 'limite-de-taxa-a-letra-miuda', text: "Limite de taxa: a letra miúda", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Middleware"}
      description={"CORS, log, autenticação e limite de taxa — e por que a ordem importa."}
      href={"/docs/kiln/middleware"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
