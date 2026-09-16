// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Publicar um pacote",
  description: "Empacotar, o que entra no tarball, o registro estático — e por que o pacote é reprodutível.",
};

const blocos: Bloco[] = [
  {"p": "Publicar é dois passos: **empacotar** (gerar o tarball) e **enviar** (copiar para um registro). Os dois são comandos, e o registro não é um servidor."},
  {"h2": "Empacotar"},
  { code: `dataforge check .
dataforge test tests/
dataforge pack
`, lang: 'bash' },
  { code: `  dist/minha-lib-1.0.0.tar.gz   14.2 KB
  sha256: 9eb3d7de7b8581abf905ad93c978514af39b65253ede72ee82d262c8fe7761d0
`, lang: 'text' },
  {"p": "**O tarball é reprodutível**: `mtime` zerado, uid e gid zerados. Sem isso o sha256 mudaria a cada empacotamento, e a verificação de integridade não significaria nada — dois downloads da mesma versão não teriam como ser comparados."},
  {"h2": "O que entra, e o que não"},
  {"table": {"head": ["Entra", "Fica de fora"], "rows": [["`forge.toml`", "`forge_modules/`"], ["o `entry` e tudo o que ele alcança", "`dist/`"], ["`src/`", "`.git/`"], ["`tests/`", "arquivos fora do projeto"], ["`README.md`, `LICENSE`", "o que o `.gitignore` já exclui"]]}},
  {"callout": {"tipo": "dica", "titulo": "Confira antes de publicar", "texto": "`tar tzf dist/minha-lib-1.0.0.tar.gz` lista o que vai dentro. É o momento de descobrir um `.env` ou um dump de banco — depois de publicado, o conteúdo saiu da sua máquina."}},
  {"h2": "O registro é uma pasta"},
  {"p": "Não há servidor a manter: um registro é uma pasta com `index.json` e `pacotes/*.tar.gz`, servida por qualquer host estático."},
  { code: `registro/
  index.json
  pacotes/
    validador-1.0.0.tar.gz
    tabela-1.1.0.tar.gz
`, lang: 'text' },
  { code: `dataforge publish --registry=../registro
`, lang: 'bash' },
  {"p": "O do projeto vive em `site/public/registry/` e vai ao ar junto com o site. Publicar numa pasta e versioná-la é um registro privado completo — o que uma empresa precisa para compartilhar bibliotecas internas sem infraestrutura."},
  {"h2": "A extração recusa o que sai da pasta"},
  {"p": "Um pacote não pode escrever fora do lugar dele. A extração recusa caminho com `../` e recusa link simbólico — as duas formas clássicas de um tarball malicioso sobrescrever um arquivo do sistema."},
  {"h2": "Do outro lado: instalar"},
  { code: `dataforge add validador             # a última versão
dataforge add validador@1.2.0       # uma exata
dataforge install                   # resolve o forge.toml inteiro
dataforge list                      # o que está instalado
dataforge remove validador
`, lang: 'bash' },
  {"p": "O cache fica em `~/.dataforge/cache/`, entre projetos: instalar a mesma versão num segundo projeto não baixa de novo."},
  {"h2": "A lista antes de publicar"},
  {"list": ["`dataforge check .` limpo", "`dataforge test tests/` verde, importando **pelo nome do pacote**", "`version` subida, segundo o [semver](/docs/bibliotecas/versao)", "README com um exemplo que roda", "`tar tzf` conferido — nada de segredo, nada de `dist/`", "o CHANGELOG diz o que mudou, e o que quebrou"], "ordered": true},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/bibliotecas/manutencao", "title": "Manter", "desc": "depreciar sem quebrar"}, {"href": "/docs/pacotes/publicar", "title": "Referência do publish", "desc": "as opções do comando"}]},
];

const headings = [{ id: 'empacotar', text: "Empacotar", level: 2 as const }, { id: 'o-que-entra-e-o-que-nao', text: "O que entra, e o que não", level: 2 as const }, { id: 'o-registro-e-uma-pasta', text: "O registro é uma pasta", level: 2 as const }, { id: 'a-extracao-recusa-o-que-sai-da-pasta', text: "A extração recusa o que sai da pasta", level: 2 as const }, { id: 'do-outro-lado-instalar', text: "Do outro lado: instalar", level: 2 as const }, { id: 'a-lista-antes-de-publicar', text: "A lista antes de publicar", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Publicar um pacote"}
      description={"Empacotar, o que entra no tarball, o registro estático — e por que o pacote é reprodutível."}
      href={"/docs/bibliotecas/publicar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
