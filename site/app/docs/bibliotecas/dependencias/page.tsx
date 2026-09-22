// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escolher dependências",
  description: "Cada dependência é uma promessa que você faz em nome de outra pessoa — as perguntas antes de adicionar.",
};

const blocos: Bloco[] = [
  {"p": "Uma dependência entra em uma linha e sai em uma semana de trabalho. Quem instala a sua biblioteca herda **todas** as dependências dela, e as dependências delas. Antes de adicionar, cinco perguntas."},
  {"table": {"head": ["Pergunta", "Porque"], "rows": [["a biblioteca padrão já faz?", "`Arcane.*` vem junto e não tem versão para conflitar"], ["dá para escrever em 50 linhas?", "50 linhas suas não quebram numa atualização de terceiro"], ["quem mantém, e há quanto tempo não há commit?", "uma dependência abandonada é uma vulnerabilidade adiada"], ["qual a faixa de versão?", "`^1.2` aceita 1.x; `*` aceita a 2.0 que quebra tudo"], ["ela depende do Python (`adopt Python.x`)?", "o `forge.toml` não sabe instalar isso — declare no README"]]}},
  { code: `dataforge add validador@^1.0    # faixa: 1.x, a partir da 1.0
dataforge why tabela             # por que isto esta instalado
dataforge tree                   # a arvore inteira, com as transitivas
dataforge outdated               # o que tem versao nova`, lang: 'bash' },
  {"callout": {"tipo": "atencao", "titulo": "Conflito de faixa é erro, e não aviso", "texto": "Se duas dependências pedem faixas incompatíveis do mesmo terceiro, `dataforge add` recusa e diz quem pediu o quê. Instalar as duas versões lado a lado geraria um bug irreproduzível: o mesmo tipo existindo duas vezes."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Escolher dependências"}
      description={"Cada dependência é uma promessa que você faz em nome de outra pessoa — as perguntas antes de adicionar."}
      href={"/docs/bibliotecas/dependencias"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
