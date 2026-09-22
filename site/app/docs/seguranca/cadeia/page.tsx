// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/seguranca_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Cadeia de suprimentos",
  description: "Do pacote que se instala à imagem que se publica — o que é conferido, e em que ponto.",
};

const blocos: Bloco[] = [
  {"p": "A cadeia de suprimentos é tudo que entra no seu programa sem ter sido escrito por você: pacotes, *actions* do CI, a imagem base, o próprio interpretador. Um ataque a ela alcança todo mundo que confia no elo — por isso cada elo precisa de uma conferência, e não de confiança."},
  {"table": {"head": ["Elo", "A conferência", "Onde"], "rows": [["o pacote instalado", "o sha256 do `forge.lock` é comparado com o que chegou", "`dataforge install`"], ["o pacote publicado", "tarball **reprodutível** (`mtime=0`, uid/gid zerados)", "`dataforge pack`"], ["a extração", "recusa `../` e link simbólico (*Zip Slip*)", "`dataforge add`"], ["as *actions* do CI", "fixar por **SHA do commit**, e não por tag", "o workflow"], ["a imagem base", "atualizada pelo Dependabot; `USER` sem privilégio", "`dataforge devops github`"], ["o inventário", "SBOM em CycloneDX", "`dataforge devops sbom`"], ["o artefato em produção", "manifesto assinado da pasta", "`Arcane.Integridade`"], ["o que o código pode fazer", "o `adopt` fora da lista é recusado", "`Arcane.Capacidade`"]]}},
  { code: `uses: actions/checkout@v4                                       # a tag pode ser MOVIDA
uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # o commit nao`, lang: 'yaml' },
  {"callout": {"tipo": "atencao", "titulo": "A tag de uma action pode mudar de dono", "texto": "Uma tag aponta para o commit que o dono da action quiser, quando ele quiser — e uma conta comprometida move `v4` para um commit malicioso em todos os repositórios que o usam. O SHA não se move. O Dependabot atualiza os SHAs fixados, então fixar não significa ficar para trás."}},
  { code: `dataforge install              # confere o sha256 de cada pacote contra o lock
dataforge outdated             # o que tem versao nova
dataforge devops sbom          # o inventario, para o scanner da empresa
dataforge seguranca . --strict # o segredo que entraria junto no pacote`, lang: 'bash' },
  {"p": "Continue em [Integridade](/docs/seguranca/integridade) e [O lockfile](/docs/modulos/lockfile)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Cadeia de suprimentos"}
      description={"Do pacote que se instala à imagem que se publica — o que é conferido, e em que ponto."}
      href={"/docs/seguranca/cadeia"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
