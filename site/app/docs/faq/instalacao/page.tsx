// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Instalação: o que dá errado",
  description: "Os três lugares onde a linguagem pode estar instalada, a cópia velha no PATH, e o erro que não existe no repositório.",
};

const blocos: Bloco[] = [
  {"p": "A instalação funciona de primeira quase sempre. O que custa tempo é o caso em que ela funcionou **duas vezes**, em lugares diferentes, e o `PATH` escolhe a errada."},
  {"h2": "As formas"},
  {"table": {"head": ["Como", "Onde põe", "Para quem"], "rows": [["`pip install dataforge-lang`", "no Python que rodou o `pip`", "quem já tem Python"], ["`scripts/instalar.sh`", "uma venv em `~/.dataforge`", "macOS e Linux, sem sudo"], ["`scripts/instalar.ps1`", "idem", "Windows"], ["binário do release", "onde você puser", "sem Python nenhum"], ["`pip install -e .`", "aponta para o repositório", "quem desenvolve a linguagem"]]}},
  {"h2": "O erro que não existe no seu arquivo"},
  {"callout": {"tipo": "perigo", "titulo": "Cuidado com instalação velha no PATH", "texto": "Há **três** lugares onde a linguagem pode estar: uma venv do projeto, `~/.dataforge` e o Python do sistema. Uma cópia antiga produz erros que não existem no seu código — foi assim que um `LexError: Unexpected character: '$'` apareceu num arquivo que usa interpolação normalmente. A interpolação existe há versões; o que estava velho era o binário."}},
  { code: `$ which -a dataforge df
$ dataforge --version
$ python3 -c "import dataforge; print(dataforge.__file__)"`, lang: 'bash' },
  {"p": "Se as três respostas não concordarem, é isso. Num checkout de desenvolvimento, a venv deve estar em modo editável (`pip install -e .`), que aponta para o repositório e nunca envelhece."},
  {"h2": "O pino do projeto pode trocar a versão por baixo"},
  {"p": "O `forge.toml` declara `dataforge = \">=1.1\"`, e o pino **é cobrado**: `dataforge run` troca por `os.execve` quando a versão pedida está instalada, e **recusa** quando não está. Um pino que não é cobrado é um comentário com sintaxe."},
  {"table": {"head": ["Variável", "O que faz"], "rows": [["`DATAFORGE_SEM_TROCA=1`", "ignora o pino"], ["`DATAFORGE_RAIZ`", "troca a raiz das instalações"], ["`DF_IDIOMA=en`", "as mensagens voltam ao inglês"], ["`NO_COLOR=1`", "sem cor, em toda a CLI"]]}},
  {"h2": "A ponte para o Python instala noutro lugar"},
  {"p": "`adopt Python.numpy as np` procura o numpy **no Python que está rodando a linguagem**. O instalador cria uma venv em `~/.dataforge`, e um `pip install numpy` no terminal costuma instalar em outro. A mensagem de ausência nomeia o Python exato — e no executável único, onde não há `pip` nenhum, ela aponta `pip install dataforge-lang` em vez de um comando que nunca funcionaria."},
  {"cards": [{"href": "/docs/instalacao", "title": "Instalação", "desc": "o guia inteiro"}, {"href": "/docs/faq/editor", "title": "Editor", "desc": "VS Code, LSP e depurador"}, {"href": "/download", "title": "Download", "desc": "os binários por plataforma"}]},
];

const headings = [{ id: 'as-formas', text: "As formas", level: 2 as const }, { id: 'o-erro-que-nao-existe-no-seu-arquivo', text: "O erro que não existe no seu arquivo", level: 2 as const }, { id: 'o-pino-do-projeto-pode-trocar-a-versao-por-baixo', text: "O pino do projeto pode trocar a versão por baixo", level: 2 as const }, { id: 'a-ponte-para-o-python-instala-noutro-lugar', text: "A ponte para o Python instala noutro lugar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Instalação: o que dá errado"}
      description={"Os três lugares onde a linguagem pode estar instalada, a cópia velha no PATH, e o erro que não existe no repositório."}
      href={"/docs/faq/instalacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
