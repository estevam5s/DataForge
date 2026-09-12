import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "API REST e Insomnia",
  description: "Arcane.API — OpenAPI, coleção do Insomnia, Postman e curl, derivados das rotas do Kiln.",
};

const blocos: Bloco[] = [
  {"p": "O [Kiln](/docs/kiln) já é um framework REST completo: `route`, `resource`, `cors`, `auth`, `rate_limit`, paginação, validação. O que faltava era o **outro lado** — quem vai consumir a API precisava ler o código-fonte do servidor para saber o que ela oferece."},
  {"callout": {"tipo": "nota", "titulo": "Por que não escrever à mão", "texto": "Documentação de API escrita à mão resolve por uma semana. Depois ela diverge — e uma documentação de API **errada** é pior que nenhuma, porque quem a lê não tem como saber. Aqui ela é derivada das rotas registradas: o servidor é a fonte da verdade."}},

  {"h2": "Um comando"},
  { code: `dataforge api src/app.df                          # a tabela de rotas
dataforge api src/app.df --openapi  -o=openapi.json
dataforge api src/app.df --insomnia -o=insomnia.json
dataforge api src/app.df --postman  -o=postman.json
dataforge api src/app.df --curl`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Aponte para o app.df, não para o main.df", "texto": "O arquivo é **executado** para que as rotas se registrem — é assim que um servidor Kiln se declara. O `main.df` chama `ignite` e nunca voltaria. É a mesma separação que `projetos/loja-web` usa, e agora ela tem uma segunda razão de existir."}},

  {"h2": "Insomnia"},
  {"p": "Importar em **Import → From File** dá uma requisição por rota, já com método, URL e corpo de exemplo onde faz sentido."},
  { code: `dataforge api src/app.df --insomnia -o=insomnia.json`, lang: 'bash' },
  {"table": {"head": ["No Kiln", "No Insomnia", "Por quê"], "rows": [
    ["`/produtos/:id`", "`{{ base }}/produtos/{{ id }}`", "`{{ }}` é o que o Insomnia reconhece como variável"],
    ["a porta do `server`", "ambiente `base`", "trocar de máquina é editar um campo"],
    ["`POST` / `PUT` / `PATCH`", "corpo JSON vazio", "pronto para preencher"]]}},
  {"p": "Deixar `:id` cru daria uma requisição que bate literalmente em `/produtos/:id` — e ninguém entende por que dá 404."},

  {"h2": "OpenAPI 3.1"},
  {"p": "É o formato que o Swagger UI lê, que gera cliente em vinte linguagens, e que um validador de contrato consome. Se for para exportar um só, é este."},
  { code: `adopt Kiln
adopt Arcane.API as API

server Loja on 8080:
    route GET "/produtos":
        respond json {"produtos": []}
    route POST "/produtos":
        respond json {"criado": yes}
    route GET "/produtos/:id":
        respond json {"id": params["id"]}

out API.openapi(Loja, {
    "titulo": "API da Loja",
    "versao": "2.0.0",
    "base": "https://api.loja.com"
})` },
  {"p": "`/produtos/:id` vira `/produtos/{id}`, e o parâmetro de caminho é declarado. Sem essa tradução, o Swagger trata `:id` como parte literal do caminho e o cliente gerado bate numa URL que não existe."},

  {"h2": "curl, para o README"},
  { code: `# Lista produtos
curl https://api.loja.com/produtos

# Cria produtos
curl -X POST https://api.loja.com/produtos \\
  -H 'Content-Type: application/json' \\
  -d '{}'

# Um produto
curl https://api.loja.com/produtos/<id>`, lang: 'bash' },
  {"p": "É o formato menos cerimonioso, e o que mais se usa na prática: cabe num README, num chamado de suporte, ou numa mensagem para quem está testando a API pela primeira vez."},

  {"h2": "A tabela inteira"},
  {"table": {"head": ["", "Devolve"], "rows": [
    ["`API.openapi(app, config)`", "OpenAPI 3.1, como texto JSON"],
    ["`API.insomnia(app, config)`", "coleção do Insomnia v4"],
    ["`API.postman(app, config)`", "coleção do Postman v2.1"],
    ["`API.curl(app, config)`", "um comando por rota"],
    ["`API.markdown(app, config)`", "a tabela de rotas"],
    ["`API.rotas(app)`", "as rotas cruas, como cluster de vaults"],
    ["`API.resumo(app)`", "quantas rotas, por método"]]}},
  {"p": "O `config` aceita `titulo`, `versao`, `descricao` e `base`. Todas as funções aceitam tanto o servidor quanto a lista que `Kiln.routes` devolve — quem chama não deveria precisar saber qual das duas tem em mãos."},

  {"h2": "O que ele não infere, e por quê"},
  {"p": "O Kiln não declara tipos de corpo nem de resposta: `respond json {…}` monta o vault na hora. Então o **esquema** de entrada e saída não aparece no OpenAPI — só a rota, o método e os parâmetros de caminho."},
  {"callout": {"tipo": "atencao", "texto": "Inventar um esquema a partir de um exemplo daria uma documentação com **aparência** de completa e conteúdo adivinhado. Uma documentação menor e verdadeira é mais útil que uma grande e inventada — principalmente quando alguém vai gerar um cliente a partir dela."}},
  {"p": "Onde você declarar validação com `Kiln.validar`, essa parte é real e entra."},
];

const headings = [{ id: 'um-comando', text: "Um comando", level: 2 as const }, { id: 'insomnia', text: "Insomnia", level: 2 as const }, { id: 'openapi-31', text: "OpenAPI 3.1", level: 2 as const }, { id: 'curl-para-o-readme', text: "curl, para o README", level: 2 as const }, { id: 'a-tabela-inteira', text: "A tabela inteira", level: 2 as const }, { id: 'o-que-ele-nao-infere-e-por-que', text: "O que ele não infere, e por quê", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"API REST e Insomnia"}
      description={"Arcane.API — OpenAPI, coleção do Insomnia, Postman e curl, derivados das rotas do Kiln."}
      href={"/docs/tecnicas/api"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
