// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A API do GitHub",
  description: "Issue, comentário no PR, status do commit, release e workflow_dispatch — com paginação e o limite de taxa.",
};

const blocos: Bloco[] = [
  {"p": "`GH.cliente(token)` fala a API REST v3: manda os cabeçalhos que ela pede (`Accept`, `X-GitHub-Api-Version`), pagina seguindo `Link: rel=\"next\"`, guarda o limite de taxa que sobrou e nunca imprime o token. Sem `token`, ele usa o `GITHUB_TOKEN` do ambiente — que é o que existe dentro de um job."},
  { code: `adopt Arcane.GitHub as GH

gh := GH.cliente()          // GITHUB_TOKEN do ambiente
out gh                      // o token nunca aparece
assert "sem token" in str(gh) or "com token" in str(gh)

// O que e recusado ANTES de ir a rede:
monitor:
    gh.status("dono/repo", "abc123", "ok")
    assert no
handle Error as e:
    out e.message

monitor:
    gh.repositorio("sem-barra")
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"h2": "No CI: comentar o resultado no PR"},
  { code: `adopt Arcane.GitHub as GH

// ci/comentar.df — roda num job de pull_request
action comentar_cobertura(percentual):
    c := GH.contexto()
    ev := GH.evento()
    numero := ev["pull_request"]["number"] ?? void
    given numero is void:
        yield no
    gh := GH.cliente()
    gh.comentar(c["repositorio"], numero,
        $"Cobertura: **{percentual}%** — [execucao]({c['url_da_execucao']})")
    yield yes

// Fora de um PR nao comenta nada — e nao quebra.
assert comentar_cobertura(87) is no`, lang: 'df' },
  {"h2": "O que ele oferece"},
  {"table": {"head": ["Método", "Endpoint"], "rows": [["`repositorio(repo)`", "`GET /repos/{repo}`"], ["`issues(repo, estado)`", "todas as páginas — e **sem** os PRs, que a API mistura"], ["`criar_issue(repo, titulo, corpo, rotulos)`", "`POST /repos/{repo}/issues`"], ["`comentar(repo, numero, texto)`", "issue **ou** PR — para a API, os dois são issues"], ["`status(repo, sha, estado, contexto)`", "o ✓/✗ ao lado do commit"], ["`criar_release(repo, tag, …)`", "`POST /repos/{repo}/releases`"], ["`disparar_workflow(repo, arquivo, ref, entradas)`", "`workflow_dispatch`"], ["`todas(caminho)` / `pedir(metodo, caminho, corpo)`", "qualquer outro endpoint"]]}},
  {"callout": {"tipo": "atencao", "titulo": "404 num repositório privado", "texto": "Um token sem acesso a um repositório privado recebe **404**, e não 403 — a API não confirma que o repositório existe. A mensagem do erro diz isso, porque a reação natural a um 404 é procurar um erro de digitação que não existe."}},
  {"p": "Continue em [Release por tag](/docs/devops/release)."},
];

const headings = [{ id: 'no-ci-comentar-o-resultado-no-pr', text: "No CI: comentar o resultado no PR", level: 2 as const }, { id: 'o-que-ele-oferece', text: "O que ele oferece", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A API do GitHub"}
      description={"Issue, comentário no PR, status do commit, release e workflow_dispatch — com paginação e o limite de taxa."}
      href={"/docs/devops/api-github"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
