// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/devops_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Release por tag",
  description: "Uma tag v* testa de novo, confere a versão do manifesto, empacota e publica.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge devops github` escreve `.github/workflows/release.yml`. Ele dispara numa tag `v*` e faz quatro coisas, nesta ordem — e a ordem é o que impede o release errado."},
  {"list": ["**Confere a tag contra o `forge.toml`.** `v1.4.0` com `version = \"1.3.9\"` no manifesto é recusado: o pacote sairia com um número e a tag diria outro.", "**Testa de novo.** A tag pode apontar para um commit que nunca passou pelo CI.", "**Empacota.** Uma biblioteca vira o tarball reprodutível de `dataforge pack`; uma aplicação, um `.tar.gz` sem `.git` nem `forge_modules`.", "**Publica** com `gh release create --generate-notes`."], "ordered": true},
  { code: `# subir a versao
sed -i 's/^version = .*/version = "1.4.0"/' forge.toml
git commit -am "1.4.0"
git tag v1.4.0
git push --follow-tags`, lang: 'bash' },
  {"table": {"head": ["No workflow", "Sem ele"], "rows": [["`permissions: contents: write`", "o token padrão é somente-leitura, e o passo de publicar falha com 403 no primeiro release"], ["a conferência tag × manifesto", "o pacote `1.3.9` publicado na release `v1.4.0`"], ["os testes antes do pacote", "a tag num commit quebrado vira uma versão publicada"], ["`--generate-notes`", "as notas escritas à mão esquecem metade dos PRs"]]}},
  {"callout": {"tipo": "dica", "titulo": "Que número subir", "texto": "`dataforge abi` compara a superfície da versão anterior com a atual e diz se a mudança é patch, minor ou major — renomear um parâmetro é quebra, porque a chamada com nome existe nesta linguagem. Ver [Compatibilidade](/docs/abi/compatibilidade)."}},
  {"p": "Continue em [O repositório](/docs/devops/repositorio)."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Release por tag"}
      description={"Uma tag v* testa de novo, confere a versão do manifesto, empacota e publica."}
      href={"/docs/devops/release"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
