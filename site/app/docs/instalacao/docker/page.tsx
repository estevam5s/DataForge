// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fluxo.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Docker",
  description: "A imagem oficial: multi-estágio, sem root, sem dependências.",
};

const blocos: Bloco[] = [
  { code: `docker run --rm -it estevan5s/dataforge repl`, lang: 'bash' },
  {"p": "A imagem oficial está em [hub.docker.com/r/estevan5s/dataforge](https://hub.docker.com/r/estevan5s/dataforge). Ela é **multi-estágio**: as ferramentas de build ficam no primeiro estágio e não chegam à imagem final — o que se baixa é o interpretador, a biblioteca padrão e nada mais."},
  {"h2": "Rodar o seu arquivo"},
  { code: `docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df`, lang: 'bash' },
  {"p": "O `-v \"$PWD:/app\"` monta a pasta atual em `/app`, que é o diretório de trabalho da imagem. **Sem ele, o container não enxerga arquivo nenhum seu** — é o esquecimento mais comum."},
  { code: `alias df-docker='docker run --rm -it -v "$PWD:/app" estevan5s/dataforge'

df-docker run main.df
df-docker check src/
df-docker repl`, lang: 'bash' },
  {"h2": "O que há dentro"},
  {"table": {"head": ["", ""], "rows": [["Base", "`python:3.12-slim`"], ["Usuário", "`forge` — **não é root**"], ["Diretório", "`/app`"], ["Entrypoint", "`dataforge`"], ["Comando padrão", "`repl`"], ["Dependências", "**nenhuma** além da stdlib do Python"]]}},
  {"p": "O entrypoint é o `dataforge`, então **qualquer subcomando funciona** — `run`, `check`, `fmt`, `lint`, `test`, `big-o`, `init`, `new`, `repl`."},
  {"h2": "Servidor web"},
  {"p": "O Kiln escuta em `0.0.0.0` dentro do container. Em `127.0.0.1` ele ficaria inalcançável de fora — é o erro mais comum ao conteinerizar um servidor."},
  { code: `docker run --rm -p 8080:8080 -v "$PWD:/app" estevan5s/dataforge run app.df
curl localhost:8080`, lang: 'bash' },
  {"h2": "Como imagem base"},
  { code: `FROM estevan5s/dataforge:1.0.0

WORKDIR /app
COPY forge.toml .
RUN dataforge install          # resolve as dependências primeiro

COPY src/ ./src/
RUN dataforge check src/ --strict    # o build falha se o código não passar

EXPOSE 8080
CMD ["run", "src/main.df"]`, lang: 'text' },
  {"callout": {"tipo": "dica", "titulo": "Copie o `forge.toml` antes do código", "texto": "As dependências mudam menos que o código. Nessa ordem, o Docker reaproveita a camada do `install` em toda build que só mexeu em `src/` — a diferença entre um build de 2 segundos e um de 2 minutos."}},
  {"h2": "No CI"},
  { code: `jobs:
  verificar:
    runs-on: ubuntu-latest
    container: estevan5s/dataforge:1.0.0
    steps:
      - uses: actions/checkout@v4
      - run: dataforge check src/ --strict
      - run: dataforge fmt . --check
      - run: dataforge test tests/`, lang: 'text' },
  {"p": "Como o container **já é** o ambiente, não há passo de instalação — e a versão do interpretador fica presa na tag, então o CI de hoje roda igual daqui a um ano."},
  {"h2": "Etiquetas"},
  {"table": {"head": ["Tag", "O que é"], "rows": [["`latest`", "a última versão estável"], ["`1.0.0`", "uma versão fixa — **use esta em produção**"], ["`1.0`", "a última correção da 1.0"]]}},
  {"callout": {"tipo": "atencao", "titulo": "`latest` muda sem avisar", "texto": "Num Dockerfile ou num CI, fixe a versão. É a diferença entre um build reproduzível e um que quebra numa terça-feira sem ninguém ter mexido em nada."}},
  {"h2": "Permissões"},
  {"p": "O container não roda como root. Se os arquivos que ele cria aparecerem com dono errado na sua máquina, force o seu próprio usuário:"},
  { code: `docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/app" \\
  estevan5s/dataforge run main.df`, lang: 'bash' },
  {"h2": "Construir a sua"},
  { code: `git clone https://github.com/estevam5s/DataForge
cd DataForge
docker build -t dataforge .
docker run --rm -it dataforge repl`, lang: 'bash' },
];

const headings = [{ id: 'rodar-o-seu-arquivo', text: "Rodar o seu arquivo", level: 2 as const }, { id: 'o-que-ha-dentro', text: "O que há dentro", level: 2 as const }, { id: 'servidor-web', text: "Servidor web", level: 2 as const }, { id: 'como-imagem-base', text: "Como imagem base", level: 2 as const }, { id: 'no-ci', text: "No CI", level: 2 as const }, { id: 'etiquetas', text: "Etiquetas", level: 2 as const }, { id: 'permissoes', text: "Permissões", level: 2 as const }, { id: 'construir-a-sua', text: "Construir a sua", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Docker"}
      description={"A imagem oficial: multi-estágio, sem root, sem dependências."}
      href={"/docs/instalacao/docker"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
