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
  {"h2": "As dez palavras"},
  {"table": {"head": ["Palavra", "Faz"], "rows": [
    ["`server nome on porta:`", "declara a aplicação e liga ao nome"],
    ["`route VERBO \"caminho\":`", "registra uma rota"],
    ["`respond [status] [tipo] valor`", "envia a resposta e **encerra a rota**"],
    ["`render \"arquivo\" with dados`", "renderiza um template e encerra a rota"],
    ["`redirect \"/destino\"`", "302 com `Location` (ou `status 301`)"],
    ["`middleware expressao`", "roda antes de toda rota"],
    ["`mount outro at \"/prefixo\"`", "junta outro server sob um prefixo"],
    ["`assets \"/prefixo\" from \"pasta\"`", "serve arquivos do disco"],
    ["`views \"pasta\"`", "onde ficam os templates"],
    ["`ignite nome [on porta]`", "acende o forno: sobe e bloqueia"]
  ]}},
  {"p": "Todas são **contextuais**: só valem dentro de um bloco `server`. Fora dali, `route`, `render` e `server` continuam sendo nomes livres — `render := 42` é uma variável perfeitamente válida, e nenhum programa escrito antes do Kiln parou de compilar por causa dele."},
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

const headings = [{ id: 'um-servidor-inteiro', text: "Um servidor inteiro", level: 2 as const }, { id: 'as-dez-palavras', text: "As dez palavras", level: 2 as const }, { id: 'declarar-nao-e-subir', text: "Declarar não é subir", level: 2 as const }, { id: 'o-que-vem-de-graca', text: "O que vem de graça", level: 2 as const }, { id: 'comparado-ao-que-voce-conhece', text: "Comparado ao que você conhece", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

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
