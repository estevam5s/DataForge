// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O cache de árvores",
  description: "A árvore guardada entre execuções: 93% do parse — e a chave que impede de rodar a árvore de outro arquivo.",
};

const blocos: Bloco[] = [
  {"p": "Ler e analisar sintaticamente um arquivo custa tempo toda vez que ele roda. O cache guarda a **árvore** — e não código compilado, que não atravessa processo — e a devolve enquanto o arquivo não muda."},
  {"table": {"head": ["Medida", "Sem cache", "Com"], "rows": [["o parse de 269 arquivos", "258,7 ms", "**17,9 ms**"], ["`dataforge check exercicios`", "0,918 s", "**0,524 s**"], ["`dataforge run` de um arquivo de 383 linhas", "131,8 ms", "4,4% menos"]]}},
  {"p": "A terceira linha é a honesta: num arquivo só, a maior parte do tempo é o `import` do próprio Python. O cache vale onde há muitos arquivos — o `check` de um projeto, a suíte de testes."},
  {"h2": "A chave"},
  {"p": "Um cache que devolve a árvore errada é pior que nenhum: o programa roda, e roda **outra coisa**. A chave carrega o caminho, o instante de modificação em nanossegundos, o tamanho, a versão da linguagem, e um resumo do próprio lexer e parser — mexer no parser sem subir a versão não pode deixar árvores velhas valendo."},
  { code: `DATAFORGE_SEM_CACHE=1 dataforge run programa.df     # desliga, para medir`, lang: 'bash' },
  {"p": "Toda falha do cache cai no caminho normal, e a gravação é feita ao lado e trocada de uma vez: um processo interrompido não deixa arquivo pela metade."},
];

const headings = [{ id: 'a-chave', text: "A chave", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O cache de árvores"}
      description={"A árvore guardada entre execuções: 93% do parse — e a chave que impede de rodar a árvore de outro arquivo."}
      href={"/docs/compilador/cache"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
