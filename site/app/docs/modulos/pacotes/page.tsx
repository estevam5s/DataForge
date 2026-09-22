// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Usar um pacote",
  description: "add, install, remove — e onde o código de terceiro vai parar.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge add` resolve, baixa e instala; o `adopt` encontra o resultado. Quatro arquivos e uma pasta, e cada um tem um dono."},
  {"table": {"head": ["Onde", "O quê", "Versionado?"], "rows": [["`forge.toml`", "o que você **pediu** — as faixas", "**sim**"], ["`forge.lock`", "o que foi **instalado** — versão e sha256", "**sim**"], ["`forge_modules/`", "os pacotes", "**não**"], ["`~/.dataforge/cache/`", "os tarballs, entre projetos", "não"]]}},
  { code: `dataforge add validador          # a ultima, e grava a faixa
dataforge add tabela@^1.2        # uma faixa explicita
dataforge install                # tudo do forge.toml (e do lock)
dataforge list                   # o que esta instalado
dataforge remove tabela          # tira do toml e da pasta
dataforge outdated               # o que sobe, e o que exige mudar a faixa`, lang: 'bash' },
  { code: `// Depois do 'add', o 'adopt' acha sozinho: ele olha
// 'forge_modules/', subindo ate achar um 'forge.toml'.
//
//   adopt validador as V
//   out V.cpf("529.982.247-25")
//
// O nome e o do PACOTE, e nao um caminho: e o mesmo 'adopt' que o
// teste da propria biblioteca usa, e e por isso que ele precisa
// funcionar pelo nome — o teste exercita a biblioteca pelo caminho
// que um usuario usaria.

out "o adopt encontra o que o add instalou"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Conflito de versão é erro, e não aviso", "texto": "Se dois pacotes pedem faixas **incompatíveis** do mesmo terceiro, `resolver()` falha dizendo quem pediu o quê. A alternativa — instalar duas cópias em versões diferentes — gera bug irreproduzível: o mesmo tipo passa a existir duas vezes, e `x is y` responde não sobre dois objetos que deveriam ser o mesmo."}},
  {"h2": "O que a extração recusa"},
  {"table": {"head": ["Recusa", "O ataque"], "rows": [["entrada com `../`", "*Zip Slip*: escrever fora da pasta do pacote"], ["link simbólico", "apontar para fora e ser seguido depois"], ["descompactação desproporcional", "*zip bomb*: 1 KB que vira 10 GB"]]}},
  {"p": "Continue em [O lockfile](/docs/modulos/lockfile) e [O registro](/docs/modulos/registro)."},
];

const headings = [{ id: 'o-que-a-extracao-recusa', text: "O que a extração recusa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Usar um pacote"}
      description={"add, install, remove — e onde o código de terceiro vai parar."}
      href={"/docs/modulos/pacotes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
