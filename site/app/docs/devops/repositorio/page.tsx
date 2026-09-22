// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O repositório",
  description: "Dependabot, CODEOWNERS, modelos de PR e de issue, e a proteção do ramo principal.",
};

const blocos: Bloco[] = [
  {"p": "O mesmo `dataforge devops github` escreve os arquivos que fazem um repositório se manter sozinho. Nenhum deles é código, e todos evitam um tipo de incidente."},
  { code: `dataforge devops github --dono=@minha-org/plataforma

  ✓ .github/workflows/release.yml
  ✓ .github/dependabot.yml
  ✓ .github/CODEOWNERS
  ✓ .github/pull_request_template.md
  ✓ .github/ISSUE_TEMPLATE/bug.yml`, lang: 'text' },
  {"table": {"head": ["Arquivo", "Evita"], "rows": [["`dependabot.yml`", "a *action* e a imagem base que envelhecem sem ninguém ver"], ["`CODEOWNERS`", "a mudança no workflow — que muda o que chega à produção — sem revisão de quem responde por ele"], ["`pull_request_template.md`", "o PR que não diz o que muda nem como foi conferido"], ["`ISSUE_TEMPLATE/bug.yml`", "o bug sem versão e sem o programa que reproduz"]]}},
  {"callout": {"tipo": "atencao", "titulo": "O Dependabot não lê o `forge.toml`", "texto": "Ele não conhece o ecossistema do DataForge, e o arquivo gerado diz isso num comentário — melhor que esperar um PR de atualização que nunca vai chegar. Para as dependências DataForge, rode `dataforge outdated` num job agendado."}},
  {"h2": "Proteger o ramo principal"},
  {"p": "A proteção é configuração do GitHub, não arquivo — por isso o gerador não a escreve. O que ligar em *Settings → Branches*:"},
  {"table": {"head": ["Regra", "Porque"], "rows": [["exigir o job `verificar` verde", "o CI que ninguém é obrigado a esperar é decoração"], ["exigir revisão dos `CODEOWNERS`", "é o que dá dentes ao arquivo"], ["proibir `push --force`", "o histórico que alguém reescreveu não tem como ser auditado"], ["exigir o ramo atualizado", "dois PRs verdes separados podem ser vermelhos juntos"]]}},
  {"p": "Continue em [GitLab CI](/docs/devops/gitlab)."},
];

const headings = [{ id: 'proteger-o-ramo-principal', text: "Proteger o ramo principal", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O repositório"}
      description={"Dependabot, CODEOWNERS, modelos de PR e de issue, e a proteção do ramo principal."}
      href={"/docs/devops/repositorio"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
