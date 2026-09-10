import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

// Gerado por tools/gerar_ref_kiln.py — não edite à mão.

export const metadata: Metadata = {
  title: "Referência do Kiln",
  description: "As 50 funções do módulo e as dez palavras da linguagem.",
};

const blocos: Bloco[] = [
  {
    "p": "Esta página é gerada a partir de `dataforge/stdlib/kiln.py`. São **50 funções** — a sintaxe da linguagem (`server`, `route`, `respond`…) chama estas mesmas."
  },
  {
    "h2": "As palavras da linguagem"
  },
  {
    "table": {
      "head": [
        "Palavra",
        "Equivale a"
      ],
      "rows": [
        [
          "`server nome on porta:`",
          "`Kiln.forge(nome)`"
        ],
        [
          "`route GET \"/x\":`",
          "`Kiln.get(app, \"/x\", handler)`"
        ],
        [
          "`respond json d`",
          "`yield Kiln.json(d)`"
        ],
        [
          "`render \"x\" with d`",
          "`yield Kiln.render(app, \"x\", d)`"
        ],
        [
          "`redirect \"/x\"`",
          "`yield Kiln.redirect(\"/x\")`"
        ],
        [
          "`middleware m`",
          "`Kiln.use(app, m)`"
        ],
        [
          "`mount o at \"/p\"`",
          "`Kiln.mount(app, \"/p\", o)`"
        ],
        [
          "`assets \"/p\" from \"d\"`",
          "`Kiln.static(app, \"/p\", \"d\")`"
        ],
        [
          "`views \"d\"`",
          "`Kiln.templates(app, \"d\")`"
        ],
        [
          "`ignite app on 8080`",
          "`Kiln.listen(app, 8080)`"
        ]
      ]
    }
  },
  {
    "p": "As dez são **contextuais**: só valem dentro de um bloco `server`. Fora dali continuam sendo nomes livres."
  },
  {
    "h2": "Aplicação"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.forge(nome='kiln', …)`",
          "Cria uma aplicação. `Kiln.app` é o mesmo."
        ],
        [
          "`Kiln.app(nome='kiln', …)`",
          "Apelido de `forge`."
        ],
        [
          "`Kiln.config(app, chave, valor)`",
          "Ajusta uma opção: `debug`, `limite_corpo`."
        ],
        [
          "`Kiln.stats(app)`",
          "Pedidos, erros, rotas e tempo no ar."
        ]
      ]
    }
  },
  {
    "h2": "Rotas"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.route(app, metodo, padrao, handler)`",
          "Registra uma rota com o verbo dado."
        ],
        [
          "`Kiln.get(app, padrao, handler)`",
          "Registra uma rota GET."
        ],
        [
          "`Kiln.post(app, padrao, handler)`",
          "Registra uma rota POST."
        ],
        [
          "`Kiln.put(app, padrao, handler)`",
          "Registra uma rota PUT."
        ],
        [
          "`Kiln.patch(app, padrao, handler)`",
          "Registra uma rota PATCH."
        ],
        [
          "`Kiln.delete(app, padrao, handler)`",
          "Registra uma rota DELETE."
        ],
        [
          "`Kiln.options(app, padrao, handler)`",
          "Registra uma rota OPTIONS."
        ],
        [
          "`Kiln.head(app, padrao, handler)`",
          "Registra uma rota HEAD."
        ],
        [
          "`Kiln.any(app, padrao, handler)`",
          "Registra uma rota que casa qualquer verbo."
        ],
        [
          "`Kiln.resource(app, base, controlador)`",
          "Sete rotas RESTful de uma vez, a partir de um vault com `index`, `show`, `create`, `update`, `patch` e `destroy` — só as que existirem."
        ],
        [
          "`Kiln.mount(app, prefixo, outro)`",
          "Junta as rotas de outro server sob um prefixo."
        ],
        [
          "`Kiln.group(app, prefixo, meio=None)`",
          "Sub-app cujas rotas herdam prefixo e middleware."
        ],
        [
          "`Kiln.routes(app)`",
          "Lista as rotas registradas."
        ]
      ]
    }
  },
  {
    "h2": "Middleware"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.use(app, funcao)`",
          "Acrescenta um middleware."
        ],
        [
          "`Kiln.after(app, funcao)`",
          "Roda com a resposta já pronta."
        ],
        [
          "`Kiln.on_error(app, status, handler)`",
          "Troca a resposta de um status (404, 500…)."
        ],
        [
          "`Kiln.cors(origens='*', metodos=None, cabecalhos=None)`",
          "Libera origens e responde o preflight."
        ],
        [
          "`Kiln.logger(formato='dev')`",
          "Uma linha por pedido no terminal."
        ],
        [
          "`Kiln.rate_limit(maximo=60, janela=60)`",
          "429 + `Retry-After` ao estourar o teto por IP."
        ],
        [
          "`Kiln.auth(verificador, esquema='Bearer')`",
          "401 sem credencial; põe o usuário em `req[\"state\"][\"user\"]`."
        ],
        [
          "`Kiln.guard(condicao, status=403, mensagem='sem permissão')`",
          "Middleware a partir de uma condição qualquer."
        ]
      ]
    }
  },
  {
    "h2": "Segurança"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.secure_headers(csp=\"default-src 'self'\", hsts=False, frame='DENY', referrer='strict-origin-when-cross-origin', permissoes='geolocation=(), microphone=(), camera=()')`",
          "Middleware de saída com nosniff, X-Frame-Options, CSP, Referrer-Policy e Permissions-Policy. HSTS opcional — ligue só com o certificado de pé."
        ],
        [
          "`Kiln.cabecalhos_seguros(csp=\"default-src 'self'\", hsts=False, frame='DENY', referrer='strict-origin-when-cross-origin', permissoes='geolocation=(), microphone=(), camera=()')`",
          "O mesmo que `secure_headers`, em português."
        ],
        [
          "`Kiln.csrf(segredo, campo='_csrf', cabecalho='X-CSRF-Token')`",
          "Recusa POST/PUT/PATCH/DELETE sem um token que você assinou. Métodos seguros passam."
        ],
        [
          "`Kiln.csrf_token(req, segredo=None)`",
          "Um token para pôr no formulário ou no fetch."
        ]
      ]
    }
  },
  {
    "h2": "Respostas"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.json(dados, status=200, cabecalhos=None)`",
          "Resposta JSON."
        ],
        [
          "`Kiln.html(texto, status=200, cabecalhos=None)`",
          "Resposta HTML."
        ],
        [
          "`Kiln.text(texto, status=200, cabecalhos=None)`",
          "Resposta em texto puro."
        ],
        [
          "`Kiln.status(codigo, mensagem=None)`",
          "Só um status, com a frase padrão dele."
        ],
        [
          "`Kiln.redirect(destino, status=302)`",
          "302 (ou o status que você passar) com `Location`."
        ],
        [
          "`Kiln.file(caminho, tipo=None, baixar=None)`",
          "Serve um arquivo do disco; `baixar` força o download."
        ],
        [
          "`Kiln.header(resp, chave, valor)`",
          "Acrescenta um cabeçalho a uma resposta."
        ],
        [
          "`Kiln.cookie(resp, nome, valor, dias=None, http_only=True, caminho='/', same_site='Lax', seguro=False)`",
          "Acrescenta um `Set-Cookie`. Já marca `HttpOnly` e `SameSite`."
        ]
      ]
    }
  },
  {
    "h2": "Sessão"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.session_start(app, req, resp, dados=None)`",
          "Cria a sessão e devolve a resposta com o cookie."
        ],
        [
          "`Kiln.session_end(app, req, resp)`",
          "Apaga a sessão e o cookie."
        ],
        [
          "`Kiln.sign(dados, segredo)`",
          "Token assinado com HMAC-SHA256."
        ],
        [
          "`Kiln.unsign(token, segredo)`",
          "Lê um token assinado; `void` se foi adulterado."
        ]
      ]
    }
  },
  {
    "h2": "Views"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.templates(app, pasta)`",
          "Define a pasta dos templates (o mesmo que `views`)."
        ],
        [
          "`Kiln.render(app, nome, dados=None, status=200)`",
          "Renderiza um template e devolve a resposta."
        ],
        [
          "`Kiln.render_string(texto, dados=None)`",
          "Preenche um texto em vez de um arquivo."
        ],
        [
          "`Kiln.static(app, prefixo, pasta)`",
          "Serve uma pasta (o mesmo que `assets`)."
        ],
        [
          "`Kiln.escape(texto)`",
          "Escapa HTML manualmente."
        ]
      ]
    }
  },
  {
    "h2": "Ciclo de vida"
  },
  {
    "table": {
      "head": [
        "Função",
        "Faz"
      ],
      "rows": [
        [
          "`Kiln.listen(app, porta=8080, host='127.0.0.1', silencioso=False)`",
          "Sobe e bloqueia até Ctrl-C (o mesmo que `ignite`)."
        ],
        [
          "`Kiln.serve(app, porta=8080, host='127.0.0.1')`",
          "Sobe em segundo plano e devolve a porta."
        ],
        [
          "`Kiln.stop(app)`",
          "Desliga um servidor que está no ar."
        ],
        [
          "`Kiln.test(app, metodo, caminho, corpo=None, cabecalhos=None)`",
          "Executa um pedido direto na aplicação, sem socket."
        ]
      ]
    }
  },
  {
    "h2": "A requisição"
  },
  {
    "table": {
      "head": [
        "Campo",
        "É"
      ],
      "rows": [
        [
          "`method`",
          "o verbo, em maiúsculas"
        ],
        [
          "`path`",
          "o caminho, já decodificado"
        ],
        [
          "`params`",
          "os parâmetros do caminho"
        ],
        [
          "`query`",
          "a query string"
        ],
        [
          "`body`",
          "o corpo interpretado pelo Content-Type"
        ],
        [
          "`raw_body`",
          "o corpo em bytes"
        ],
        [
          "`headers`",
          "os cabeçalhos, em minúsculas"
        ],
        [
          "`cookies`",
          "os cookies do pedido"
        ],
        [
          "`session`",
          "a sessão do visitante"
        ],
        [
          "`state`",
          "espaço livre para o middleware"
        ],
        [
          "`ip`",
          "o endereço de quem pediu"
        ]
      ]
    }
  },
  {
    "h2": "Os status com frase pronta"
  },
  {
    "p": "`Kiln.status(codigo)` conhece 20 códigos: `200`, `201`, `202`, `204`, `301`, `302`, `304`, `400`, `401`, `403`, `404`, `405`, `409`, `413`, `415`, `422`, `429`, `500`, `502`, `503`."
  }
];

const headings = [{ id: 'as-palavras-da-linguagem', text: "As palavras da linguagem", level: 2 as const }, { id: 'aplicacao', text: "Aplicação", level: 2 as const }, { id: 'rotas', text: "Rotas", level: 2 as const }, { id: 'middleware', text: "Middleware", level: 2 as const }, { id: 'seguranca', text: "Segurança", level: 2 as const }, { id: 'respostas', text: "Respostas", level: 2 as const }, { id: 'sessao', text: "Sessão", level: 2 as const }, { id: 'views', text: "Views", level: 2 as const }, { id: 'ciclo-de-vida', text: "Ciclo de vida", level: 2 as const }, { id: 'a-requisicao', text: "A requisição", level: 2 as const }, { id: 'os-status-com-frase-pronta', text: "Os status com frase pronta", level: 2 as const }];

export default function Page() {
  return (
    <DocPage
      title="Referência do Kiln"
      description="As 50 funções do módulo e as dez palavras da linguagem."
      href="/docs/kiln/referencia"
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
