import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Kiln — o framework web",
  description: "Servidor HTTP, rotas, páginas e API REST com sintaxe própria na linguagem.",
};

const blocos: Bloco[] = [
  {"p": "**Kiln** é o framework web do DataForge. O nome vem do forno onde a peça ganha a forma final: a requisição entra crua e sai como resposta."},
  {"p": "Ele não é um módulo como os outros. O Kiln tem **sintaxe própria na linguagem** — `server`, `route`, `respond`, `render`, `redirect`, `middleware`, `mount`, `assets`, `views` e `ignite` — para que uma rota se leia como uma rota, e não como uma chamada de função com um `lambda` dentro."},
  {"h2": "Um servidor inteiro"},
  { code: `adopt Kiln

produtos := [
    {"id": 1, "nome": "Martelo", "preco": 89.9},
    {"id": 2, "nome": "Bigorna", "preco": 450.0}
]

server loja on 8080:
    middleware Kiln.logger()
    middleware Kiln.cors()

    route GET "/":
        respond html "<h1>Forja</h1><p>2 itens no catálogo</p>"

    route GET "/produtos":
        respond json {"itens": produtos, "total": len(produtos)}

    route GET "/produtos/:id":
        p := achar(int(params["id"]))
        given p is void:
            respond 404 json {"erro": "não achei"}
        respond json p

    route POST "/produtos":
        produtos.append(body)
        respond 201 json body

ignite loja` },
  {"p": "Isso é um servidor completo: HTML, JSON, parâmetro de caminho, corpo interpretado, status certo. Não há arquivo de configuração, nem decorador, nem registro manual de rota."},
  {"h2": "As onze palavras"},
  {"table": {"head": ["Palavra", "Faz"], "rows": [
    ["`server nome on porta:`", "declara a aplicação e liga ao nome"],
    ["`route VERBO \"caminho\":`", "registra uma rota"],
    ["`respond [status] [tipo] valor`", "envia a resposta e **encerra a rota**"],
    ["`render \"arquivo\" with dados`", "renderiza um template e encerra a rota"],
    ["`redirect \"/destino\"`", "302 com `Location` (ou `status 301`)"],
    ["`middleware expressao`", "roda antes de toda rota"],
    ["`after expressao`", "roda **depois**, com a resposta na mão"],
    ["`mount outro at \"/prefixo\"`", "junta outro server sob um prefixo"],
    ["`assets \"/prefixo\" from \"pasta\"`", "serve arquivos do disco"],
    ["`views \"pasta\"`", "onde ficam os templates"],
    ["`ignite nome [on porta]`", "acende o forno: sobe e bloqueia"]
  ]}},
  {"p": "`middleware` corta o pedido antes da rota — autenticação, limite de taxa. `after` recebe a resposta pronta e pode trocá-la — cabeçalhos, compressão, cache. Todas são **contextuais**: só valem dentro de um bloco `server`. Fora dali, `route`, `render` e `server` continuam sendo nomes livres — `render := 42` é uma variável perfeitamente válida, e nenhum programa escrito antes do Kiln parou de compilar por causa dele."},
  {"h2": "Declarar não é subir"},
  {"p": "`server` monta a aplicação e liga ao nome. Quem acende o forno é `ignite`. A separação parece pedante até você escrever o primeiro teste:"},
  { code: `// executa a rota direto na aplicação, sem abrir socket
r := Kiln.test(loja, "GET", "/produtos/2")
out r["status"], r["body"]["nome"]    // 200 Bigorna` },
  {"p": "Testar uma rota fica tão barato quanto testar uma ação — que é o que faz alguém realmente escrever esses testes. O projeto [loja-web](/docs/projetos) tem 29 deles, e todos juntos rodam em 0,06 s."},
  {"h2": "O que vem de graça"},
  {"table": {"head": ["Situação", "O Kiln faz"], "rows": [
    ["caminho não registrado", "404"],
    ["caminho existe, verbo não", "**405** com o cabeçalho `Allow`"],
    ["`OPTIONS` com `Kiln.cors()`", "responde o preflight, sem chegar na rota"],
    ["erro dentro da rota", "500, detalhe no terminal, servidor de pé"],
    ["JSON quebrado no corpo", "chega como texto — a rota decide se é 400"],
    ["corpo grande demais", "413 antes de ler tudo na memória"],
    ["`../` num caminho estático", "403, antes de abrir o arquivo"]
  ]}},
  {"p": "A distinção entre 404 e 405 não é preciosismo: dizer \"esse caminho existe, mas não com esse verbo\" poupa quem consome a API de procurar um bug que não existe."},
  {"h2": "O que já vem pronto"},
  {"p": "Estas não são bibliotecas para instalar: fazem parte do Kiln, e não têm dependência nenhuma."},
  { code: `server api on 8080:
    middleware Kiln.request_id()             // um id por pedido
    middleware Kiln.limite_de_corpo(1048576) // 413 acima de 1 MB
    middleware Kiln.rate_limit(60, 60)       // 60 por minuto, por IP
    middleware Kiln.csrf(SEGREDO)            // recusa POST de fora
    middleware Kiln.validar(ESQUEMA)         // 422 com todos os campos
    middleware Kiln.idempotente()            // não cobra duas vezes

    after Kiln.cache(120)                    // ETag + 304
    after Kiln.cabecalhos_seguros()          // CSP, nosniff, frame
    after Kiln.comprimir()                   // gzip quando compensa
    after Kiln.auditoria()                   // quem mudou o quê

    route GET "/produtos":
        achados := Kiln.buscar(produtos, req, ["nome"])
        respond Kiln.paginar(Kiln.ordenar(achados, req, ["preco"]), req)`, lang: 'df' },
  {"h3": "Listar bem é mais que devolver a lista"},
  {"p": "`GET /produtos?q=martelo&ordenar=-preco&pagina=2&por_pagina=10` — as três coisas que toda API precisa, e que quase sempre são reescritas à mão em cada rota:"},
  { code: `{
  "itens": [ … ],
  "pagina": 2, "por_pagina": 10,
  "total": 45, "paginas": 5,
  "tem_proxima": yes, "tem_anterior": yes
}`, lang: 'json' },
  {"callout": {"tipo": "atencao", "titulo": "Dois detalhes que não são conforto", "texto": "`por_pagina` tem **teto**: sem ele, `?por_pagina=1000000` derruba o servidor sem ferramenta nenhuma. E `ordenar` só aceita os campos que você listar — ordenar por um campo que a API nunca expôs revela a ordem dele."}},
  {"h3": "Validação que relata tudo de uma vez"},
  { code: `ESQUEMA := {
    "nome":  {"tipo": "texto", "obrigatorio": yes, "min": 3, "max": 40},
    "preco": {"tipo": "numero", "min": 0},
    "email": {"tipo": "email"},
    "papel": {"tipo": "texto", "em": ["admin", "leitor"]},
}`, lang: 'df' },
  { code: `{
  "erro": "dados inválidos",
  "campos": {
    "nome": "mínimo 3",
    "preco": "mínimo 0",
    "papel": "valor fora da lista permitida"
  }
}`, lang: 'json', title: '422' },
  {"p": "Um erro por envio faz quem preenche descobrir os cinco problemas em cinco tentativas — e a maioria desiste no terceiro. É **422** e não 400: o corpo foi entendido; o que falhou foi o conteúdo, e um cliente consegue distinguir os dois casos."},
  {"h3": "Idempotência — o problema do checkout"},
  {"p": "A resposta se perde na rede, o cliente reenvia, e a cobrança acontece **de novo**. O cliente sozinho não tem como saber; quem precisa reconhecer o reenvio é o servidor:"},
  { code: `POST /cobrar
Idempotency-Key: pedido-8f2c

→ {"cobranca": 1}

POST /cobrar                    // mesma chave, cliente reenviou
Idempotency-Key: pedido-8f2c

→ {"cobranca": 1}               // Idempotent-Replay: true`, lang: 'text' },
  {"callout": {"tipo": "nota", "titulo": "Fica em memória", "texto": "Some se o processo reiniciar, e não atravessa vários processos. Para valer de verdade, guarde num banco — o `Forge` serve."}},
  {"h3": "Cache e compressão"},
  {"p": "`Kiln.cache(120)` põe `Cache-Control` e `ETag`, e devolve **304** quando o cliente já tem a versão. `Kiln.comprimir()` faz gzip quando o cliente aceita e o corpo compensa — numa resposta JSON de 5,4 KB, 69 bytes na rede."},
  {"p": "Ele não toca em imagem, vídeo nem zip: já estão comprimidos, e passar gzip por cima costuma **aumentar** o tamanho. Abaixo de 1 KB também não vale — o cabeçalho do gzip sozinho tem 18 bytes."},
  {"h2": "Comparado ao que você conhece"},
  {"table": {"head": ["", "Kiln", "Flask", "Express", "Fastify"], "rows": [
    ["declarar", "`server api on 8080:`", "`Flask(__name__)`", "`express()`", "`fastify()`"],
    ["rota", "`route GET \"/x\":`", "`@app.route(\"/x\")`", "`app.get(\"/x\", fn)`", "`f.get(\"/x\", fn)`"],
    ["responder", "`respond json d`", "`return jsonify(d)`", "`res.json(d)`", "`return d`"],
    ["parâmetro", "`params[\"id\"]`", "`<int:id>`", "`req.params.id`", "`req.params.id`"],
    ["subir", "`ignite api`", "`app.run()`", "`app.listen()`", "`f.listen()`"],
    ["dependências", "**nenhuma**", "Werkzeug, Jinja2…", "npm", "npm"]
  ]}},
  {"h2": "Por onde seguir"},
  {"table": {"head": ["Página", "Cobre"], "rows": [
    ["[Rotas e parâmetros](/docs/kiln/rotas)", "`:id`, `*resto`, os seis atalhos, 405"],
    ["[Respostas](/docs/kiln/respostas)", "`respond`, status, cookies, arquivos"],
    ["[Páginas HTML](/docs/kiln/paginas)", "templates, laços, escape automático"],
    ["[Middleware](/docs/kiln/middleware)", "CORS, autenticação, limite de taxa"],
    ["[Sessão e cookies](/docs/kiln/sessao)", "login, cookie assinado"],
    ["[Estáticos e uploads](/docs/kiln/estaticos)", "CSS, imagens, downloads"],
    ["[Levar para produção](/docs/kiln/producao)", "o que muda fora da sua máquina"],
    ["[Referência](/docs/kiln/referencia)", "as 46 funções do módulo"]
  ]}},
];

const headings = [{ id: 'um-servidor-inteiro', text: "Um servidor inteiro", level: 2 as const }, { id: 'as-onze-palavras', text: "As onze palavras", level: 2 as const }, { id: 'declarar-nao-e-subir', text: "Declarar não é subir", level: 2 as const }, { id: 'o-que-vem-de-graca', text: "O que vem de graça", level: 2 as const }, { id: 'o-que-ja-vem-pronto', text: "O que já vem pronto", level: 2 as const }, { id: 'comparado-ao-que-voce-conhece', text: "Comparado ao que você conhece", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title={"Kiln — o framework web"}
      description={"Servidor HTTP, rotas, páginas e API REST, com sintaxe própria na linguagem e zero dependências."}
      href={"/docs/kiln"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
