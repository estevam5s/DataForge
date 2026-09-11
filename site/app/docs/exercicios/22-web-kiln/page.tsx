// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "22 · Web kiln",
  description: "7 exercícios: rotas, respostas, templates e estáticos.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 22`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["191", "**O primeiro servidor**", "declare um servidor com duas rotas e responda texto e HTML."], ["192", "**Parametros de caminho e query string**", "leia :id do caminho e ?campo= da query."], ["193", "**Uma API RESTful completa**", "os cinco verbos sobre um mesmo recurso, com os status certos."], ["194", "**Paginas HTML com template**", "renderize uma pagina a partir de um template com laco."], ["195", "**Middleware, autenticacao e limite de taxa**", "proteja rotas e limite pedidos por IP."], ["196", "**Paginas de erro, redirecionamento e arquivos estaticos**", "personalize o 404, redirecione uma rota antiga e sirva CSS."], ["197", "**Subir o servidor de verdade**", "acenda o forno, faca um pedido pela rede e apague."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/22-web-kiln/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/22-web-kiln/191_primeiro_servidor.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"22 · Web kiln"}
      description={"7 exercícios: rotas, respostas, templates e estáticos."}
      href={"/docs/exercicios/22-web-kiln"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
