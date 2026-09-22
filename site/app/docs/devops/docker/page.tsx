// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Docker e Compose",
  description: "A imagem multiestágio, o compose com banco — e as cinco decisões que cada artefato carrega.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge devops docker` escreve três arquivos: `Dockerfile`, `.dockerignore` e `docker-compose.yml`. Eles saem do que o projeto **usa** — o gerador lê os `adopt` e o `forge.toml` —, e cada linha tem um motivo que um artefato copiado da internet não tem."},
  { code: `dataforge devops docker              # os tres arquivos
dataforge devops docker --seco       # mostra, sem escrever
dataforge devops docker build        # docker build com a tag do projeto
dataforge devops doctor              # o que falta para subir`, lang: 'bash' },
  {"h2": "O que a imagem carrega, e por quê"},
  {"table": {"head": ["No artefato", "Sem ele"], "rows": [["`USER forge`", "um escape de contêiner vira root no host"], ["o manifesto copiado **antes** do código", "um commit numa linha reinstala tudo — de 8 s para 2 min"], ["`.env` no `.dockerignore`", "o segredo fica na camada, e `docker history` o mostra"], ["`HEALTHCHECK` com prazo", "o orquestrador manda tráfego para um contêiner que ainda está subindo"], ["`depends_on: service_healthy` no compose", "a aplicação falha na primeira consulta, de forma intermitente"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`0.0.0.0` dentro do contêiner", "texto": "O padrão do Kiln e da Vitrine é `127.0.0.1`, que de dentro do contêiner significa **o próprio contêiner**. O sintoma engana: o log diz *“no ar”* e o `curl` de fora não recebe nada. `ignite api at \"0.0.0.0\"` — e o gerador já escreve isso no comando."}},
  {"h2": "O banco no compose"},
  {"p": "Quando o projeto adota `Forge`, o compose ganha o serviço do banco com sonda de saúde, e a aplicação lê a URL de `DATABASE_URL`. `Forge.esperar` espera o banco **aceitar** conexão antes da primeira consulta — ver [O banco em contêiner](/docs/banco-de-dados/docker)."},
  { code: `services:
  app:
    build: .
    environment:
      DATABASE_URL: postgres://app:app@banco:5432/app
    depends_on:
      banco:
        condition: service_healthy
  banco:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 2s
      retries: 30`, lang: 'yaml' },
  {"p": "Continue em [Kubernetes](/docs/devops/kubernetes) e [Instalação com Docker](/docs/instalacao/docker)."},
];

const headings = [{ id: 'o-que-a-imagem-carrega-e-por-que', text: "O que a imagem carrega, e por quê", level: 2 as const }, { id: 'o-banco-no-compose', text: "O banco no compose", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Docker e Compose"}
      description={"A imagem multiestágio, o compose com banco — e as cinco decisões que cada artefato carrega."}
      href={"/docs/devops/docker"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
