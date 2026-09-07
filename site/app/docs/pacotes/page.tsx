import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Gerenciador de pacotes",
  description: "Instalar, remover e travar dependências — o pip e o npm do DataForge.",
};

const blocos: Bloco[] = [
  {"p": "O `dataforge` traz o gerenciador de pacotes embutido. Não há binário separado: os mesmos comandos que rodam e verificam seu código também resolvem dependências."},
  {"h2": "Começar"},
  { code: `dataforge init meu-app        # cria forge.toml e o esqueleto
cd meu-app

dataforge add validador       # instala e grava no forge.toml
dataforge add tabela datas    # vários de uma vez`, lang: 'bash' },
  {"p": "E no seu código:"},
  { code: `adopt validador as V
adopt tabela as Tb

out V.cpf("529.982.247-25")
out Tb.render([["Ana", 30]], ["Nome", "Idade"])`, lang: 'df' },
  {"h2": "Os comandos"},
  {"table": {"head": ["Comando", "O que faz"], "rows": [["`dataforge add <pacote>`", "instala e grava a dependência no `forge.toml`"], ["`dataforge add <pacote>@1.2.0`", "uma versão exata"], ["`dataforge add <pacote>@^2.0`", "uma faixa de versões"], ["`dataforge remove <pacote>`", "desinstala e tira do manifesto"], ["`dataforge install`", "instala tudo o que o `forge.toml` declara"], ["`dataforge install --dry-run`", "mostra o plano sem baixar nada"], ["`dataforge list`", "o que está instalado, e o que veio por transitividade"], ["`dataforge search <termo>`", "procura no registro"], ["`dataforge pack`", "empacota este projeto para publicar"], ["`dataforge publish`", "manda o pacote para um registro"]]}},
  {"h2": "Onde as coisas ficam"},
  { code: `meu-app/
├── forge.toml          o que você pediu
├── forge.lock          o que foi realmente instalado, com sha256
├── forge_modules/      os pacotes (o que o 'adopt' enxerga)
│   ├── validador/
│   └── tabela/
└── src/main.df`, lang: 'bash' },
  {"callout": {"tipo": "dica", "titulo": "forge.lock entra no git", "texto": "O `forge.toml` diz `^1.0.0`; o `forge.lock` diz exatamente `1.4.2`, com o sha256. Versionar o lock é o que faz a instalação de hoje ser idêntica à de daqui a seis meses. Já `forge_modules/` fica de fora — é conteúdo baixado."}},
  {"h2": "Faixas de versão"},
  {"p": "A mesma gramática do npm e do Cargo:"},
  {"table": {"head": ["Escrita", "Aceita", "Não aceita"], "rows": [["`1.2.3`", "só 1.2.3", "qualquer outra"], ["`^1.2.3`", "1.2.3 até 1.9.9", "2.0.0"], ["`^0.2.3`", "0.2.3 até 0.2.9", "0.3.0"], ["`~1.2.3`", "1.2.3 até 1.2.99", "1.3.0"], ["`>=1.0 <2.0`", "1.5.0", "2.0.0"], ["`*`", "qualquer uma", "—"]]}},
  {"p": "`dataforge add` sem faixa grava `^` da versão mais recente: você recebe correções e recursos novos, nunca uma quebra de compatibilidade anunciada."},
  {"p": "Em `^0.x`, o `menor` é que trava — antes do 1.0 a convenção é que qualquer `menor` pode quebrar."},
  {"h2": "Outras origens"},
  {"p": "Nem tudo vem do registro:"},
  { code: `[dependencies]
validador = "^1.0.0"                                    # registro
interno   = { path = "../biblioteca-interna" }          # pasta local
forkado   = { git = "https://github.com/voce/lib.git", ref = "v1.2" }
direto    = { url = "https://exemplo.com/pkg-1.0.tar.gz" }`, lang: 'toml' },
  {"p": "Pela linha de comando:"},
  { code: `dataforge add ../biblioteca-interna
dataforge add git+https://github.com/voce/lib.git`, lang: 'bash' },
  {"h2": "Conflito de versões"},
  {"p": "Quando dois pacotes pedem o mesmo terceiro, o resolvedor intersecta os requisitos e pega a maior versão que serve aos dois. Se não houver nenhuma, ele falha dizendo quem pediu o quê:"},
  { code: `✗ nao ha versao de 'comum' que sirva a todos:
    a@1.0.0 pede ^1.0.0
    b@1.0.0 pede ^2.0.0
    existem: 1.0.0, 2.0.0`, lang: 'bash' },
  {"p": "É deliberado que isso seja um erro, não um aviso: instalar duas cópias da mesma biblioteca em versões diferentes é a origem de bugs que ninguém consegue reproduzir."},
  {"h2": "Integridade"},
  {"p": "Todo pacote do registro traz um `sha256`. Ele é conferido no download e gravado no lock; se o conteúdo mudar sem a versão mudar, a instalação falha em vez de seguir em frente."},
  {"p": "A extração recusa tarballs que tentem escrever fora da pasta de destino (`../`) ou que contenham links simbólicos."},
  {"h2": "Trabalhar offline"},
  { code: `dataforge install --offline`, lang: 'bash' },
  {"p": "Usa o índice em cache e os tarballs já baixados em `~/.dataforge/cache/`. O cache é compartilhado entre projetos — instalar o mesmo pacote num segundo projeto não vai à rede."},
  {"h2": "Como o adopt encontra"},
  {"p": "Na ordem: biblioteca padrão (`Arcane.*`), arquivos ao lado do seu, e então `forge_modules/`, procurando da pasta atual para cima até achar um `forge.toml`."},
  { code: `adopt validador as V           # forge_modules/validador/src/main.df
adopt validador.email as E     # forge_modules/validador/src/email.df`, lang: 'df' },
];

const headings = [{ id: 'comecar', text: "Começar", level: 2 as const }, { id: 'os-comandos', text: "Os comandos", level: 2 as const }, { id: 'onde-as-coisas-ficam', text: "Onde as coisas ficam", level: 2 as const }, { id: 'faixas-de-versao', text: "Faixas de versão", level: 2 as const }, { id: 'outras-origens', text: "Outras origens", level: 2 as const }, { id: 'conflito-de-versoes', text: "Conflito de versões", level: 2 as const }, { id: 'integridade', text: "Integridade", level: 2 as const }, { id: 'trabalhar-offline', text: "Trabalhar offline", level: 2 as const }, { id: 'como-o-adopt-encontra', text: "Como o adopt encontra", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Gerenciador de pacotes"}
      description={"Instalar, remover e travar dependências — o pip e o npm do DataForge."}
      href={"/docs/pacotes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
