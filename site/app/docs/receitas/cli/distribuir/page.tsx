// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/receitas_cli.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Distribuir a ferramenta",
  description: "Do `.df` no seu computador ao comando que outra pessoa instala.",
};

const blocos: Bloco[] = [
  {"p": "Uma ferramenta que só roda na sua máquina é um script. Três formas de entregá-la, em ordem de esforço:"},
  {"table": {"head": ["Forma", "Quem instala precisa de", "Quando"], "rows": [["um `.df` e o `forge.toml`", "DataForge instalado", "equipe que já usa a linguagem"], ["um pacote no registro", "`dataforge add sua-lib`", "biblioteca, ou ferramenta reusável"], ["contêiner", "Docker", "CI, e máquina que não vai instalar nada"]]}},
  {"h2": "O projeto"},
  { code: `$ dataforge new cli minha-ferramenta
$ cd minha-ferramenta
$ dataforge test
$ dataforge run src/main.df -- --ajuda`, lang: 'bash' },
  {"p": "O `--` separa o que é do `dataforge` do que é **seu**: sem ele, `--ajuda` seria lido pela CLI da linguagem, e a sua nunca veria a flag."},
  {"h2": "Empacotar e publicar"},
  { code: `$ dataforge pack
$ dataforge publish --registry=../registro`, lang: 'bash' },
  {"p": "O tarball é **reprodutível** (`mtime=0`, uid e gid zerados): sem isso o sha256 mudaria a cada empacotamento, e a verificação de integridade do `forge.lock` não significaria nada."},
  {"h2": "Um contêiner que não precisa do DataForge instalado"},
  { code: `$ dataforge devops dockerfile
$ docker build -t minha-ferramenta .
$ docker run --rm minha-ferramenta --ajuda`, lang: 'bash' },
  {"p": "O `Dockerfile` gerado copia o manifesto **antes** do código (um commit numa linha deixa de reinstalar tudo), roda como `USER forge` — um escape de container vira um usuário sem privilégio, e não root no host — e põe o `.env` no `.dockerignore`, porque o segredo ficaria na camada e `docker history` o mostraria."},
  {"h2": "O que conferir antes de publicar"},
  { code: `adopt Arcane.Abi as Abi

// 'Abi' responde qual bump de semver a mudança exige, comparando a
// SUPERFÍCIE de duas versões — e não o texto do código.
assert "maior" in Abi.regras() or len(Abi.regras()) > 0
out "as regras de compatibilidade estão em Arcane.Abi"`, lang: 'df' },
  {"list": ["`dataforge test` e `dataforge check` verdes.", "`dataforge abi` entre a versão publicada e esta — **renomear um parâmetro é quebra**, porque a chamada com nome existe nesta linguagem.", "A ajuda cita cada opção, e os exemplos rodam.", "O `forge.lock` versionado: quem clonar em outro dia recebe a mesma árvore."]},
];

const headings = [{ id: 'o-projeto', text: "O projeto", level: 2 as const }, { id: 'empacotar-e-publicar', text: "Empacotar e publicar", level: 2 as const }, { id: 'um-conteiner-que-nao-precisa-do-dataforge-instalado', text: "Um contêiner que não precisa do DataForge instalado", level: 2 as const }, { id: 'o-que-conferir-antes-de-publicar', text: "O que conferir antes de publicar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Distribuir a ferramenta"}
      description={"Do `.df` no seu computador ao comando que outra pessoa instala."}
      href={"/docs/receitas/cli/distribuir"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
