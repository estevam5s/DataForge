// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O registro de pacotes",
  description: "Uma pasta com um índice e tarballs — servida por qualquer host, e sem servidor a manter.",
};

const blocos: Bloco[] = [
  {"p": "O registro é **estático**: um `index.json` e uma pasta de `.tar.gz`. Não há servidor, não há banco, não há processo a manter no ar — e é por isso que ele vai junto com o site."},
  { code: `site/public/registry/
  index.json              o catalogo: nome, versoes, sha256
  pacotes/
    validador-1.0.0.tar.gz
    tabela-1.1.0.tar.gz
    ...`, lang: 'text' },
  {"table": {"head": ["Decisão", "O que ela evita"], "rows": [["estático", "um serviço a manter, com disponibilidade e custo"], ["índice num arquivo", "uma consulta de rede por dependência"], ["sha256 no índice", "confiar no host do download"], ["qualquer host serve", "ficar preso a um fornecedor"]]}},
  {"h2": "Publicar"},
  { code: `cd packages/validador
dataforge pack
dataforge publish --registry=../../site/public/registry

# E o registro da comunidade, com conta:
dataforge login
dataforge publish
dataforge whoami`, lang: 'bash' },
  {"h2": "Um registro próprio"},
  {"p": "Para uma empresa, o registro interno é uma pasta servida por nginx, por um bucket S3, ou pelo próprio GitHub Pages. O `forge.toml` aponta para ele."},
  { code: `[registro]
url = "https://pacotes.minhaempresa.com"

# Ou por ambiente, que e o que um CI usa:
#   DATAFORGE_REGISTRY=https://pacotes.minhaempresa.com`, lang: 'toml' },
  {"callout": {"tipo": "dica", "titulo": "O registro não é a defesa", "texto": "Um registro privado reduz a superfície, e não a elimina: o que garante que o pacote é o que você aprovou é o **sha256 no lock**, e não de onde ele veio. Um registro comprometido serve um tarball diferente com o mesmo nome e a mesma versão — e o lock recusa."}},
  {"p": "Continue em [Publicar](/docs/bibliotecas/publicar)."},
];

const headings = [{ id: 'publicar', text: "Publicar", level: 2 as const }, { id: 'um-registro-proprio', text: "Um registro próprio", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O registro de pacotes"}
      description={"Uma pasta com um índice e tarballs — servida por qualquer host, e sem servidor a manter."}
      href={"/docs/modulos/registro"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
