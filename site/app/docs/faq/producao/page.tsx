// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Dá para pôr em produção?",
  description: "A resposta é \"depende de quê\", e as condições são concretas: o que falta no Kiln, o que o DevOps gera, e o que precisa vir de fora.",
};

const blocos: Bloco[] = [
  {"p": "A resposta curta: **para ferramenta interna, painel e serviço atrás de um proxy, sim**. Para um serviço público exposto direto na internet, **não sem um servidor na frente**. As condições abaixo são todas concretas."},
  {"h2": "O que o Kiln não tem, e por quê"},
  {"table": {"head": ["Falta", "Motivo", "O que fazer"], "rows": [["**TLS**", "refazer TLS em Python puro seria a pior escolha de segurança possível", "nginx, Caddy ou o proxy da nuvem"], ["**HTTP/2**", "ele roda sobre o `http.server` do Python", "o mesmo proxy resolve"], ["**sincronização automática**", "a linguagem não aplica trava por você", "`Arcane.Concurrent`, e leia o aviso do `check`"]]}},
  {"p": "O que **tem**, e costuma surpreender: WebSocket com o RFC 6455 falado à mão, Server-Sent Events, streaming de resposta, upload multipart com nome e extensão conferidos, CSRF, cabeçalhos de segurança e limite de corpo como middleware."},
  {"h2": "O que o `devops` gera"},
  { code: `$ dataforge devops dockerfile
$ dataforge devops compose
$ dataforge devops ci github
$ dataforge devops k8s
$ dataforge devops doctor`, lang: 'bash' },
  {"p": "Ele **gera texto e sai da frente**. Um `deploy` que falasse com Docker e Kubernetes por dentro esconderia o que a imagem é, e no dia em que alguém precisa mudar uma camada não haveria onde mexer."},
  {"table": {"head": ["No artefato", "Sem ele"], "rows": [["`USER forge`", "um escape de contêiner vira root no host"], ["o manifesto copiado antes do código", "um commit numa linha reinstala tudo (8 s → 2 min)"], ["`.env` no `.dockerignore`", "o segredo fica na camada, e `docker history` o mostra"], ["`resources` + as duas sondas no Deployment", "um pod come o nó; o Service manda tráfego antes da hora"], ["`depends_on: service_healthy`", "a app falha na primeira consulta, de forma intermitente"]]}},
  {"callout": {"tipo": "perigo", "titulo": "`--host=0.0.0.0` dentro de um contêiner", "texto": "O padrão é `127.0.0.1`, que de dentro significa o próprio contêiner. O sintoma engana: o log diz \"no ar\" e o `curl` de fora não recebe nada. Vale para a Vitrine e para o `ignite` do Kiln (`at \"0.0.0.0\"`)."}},
  {"h2": "O banco sobe depois da aplicação"},
  {"p": "`Forge.esperar(url)` espera o banco **aceitar** conexão e devolve a conexão aberta. O recurso dela é o que ela **não** repete: só erro passageiro entra na retentativa; **credencial errada levanta na hora**. Repetir uma senha errada por quarenta segundos troca um erro claro por um travamento, e o programa não fica mais certo por esperar."},
  {"p": "Medido: 0,51 s contra um contêiner recém-subido, **4 ms** para recusar uma senha errada."},
  {"h2": "Antes de dizer que está no ar"},
  {"list": ["`dataforge check .` limpo, e `dataforge test --cobertura --minimo=…` no CI.", "`dataforge seguranca` — ele varre o **projeto**, e não só os `.df`: um segredo vaza do arquivo de configuração muito mais do que do código.", "`dataforge abi` entre a versão publicada e a nova — é o que decide o número, em vez de escolhê-lo a olho.", "Um smoke-test de verdade: site 200, rota protegida 401, admin 403, webhook 400."]},
  {"cards": [{"href": "/docs/devops", "title": "DevOps", "desc": "os geradores, um a um"}, {"href": "/docs/kiln", "title": "Kiln", "desc": "o framework web"}, {"href": "/docs/faq/quando-nao-usar", "title": "Quando não usar", "desc": "os limites, com medida"}]},
];

const headings = [{ id: 'o-que-o-kiln-nao-tem-e-por-que', text: "O que o Kiln não tem, e por quê", level: 2 as const }, { id: 'o-que-o-devops-gera', text: "O que o `devops` gera", level: 2 as const }, { id: 'o-banco-sobe-depois-da-aplicacao', text: "O banco sobe depois da aplicação", level: 2 as const }, { id: 'antes-de-dizer-que-esta-no-ar', text: "Antes de dizer que está no ar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Dá para pôr em produção?"}
      description={"A resposta é \"depende de quê\", e as condições são concretas: o que falta no Kiln, o que o DevOps gera, e o que precisa vir de fora."}
      href={"/docs/faq/producao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
