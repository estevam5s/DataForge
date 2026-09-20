// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fechamento.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O cache de árvores",
  description: "O lexer e o parser refaziam a mesma árvore a cada execução. Medido: 93% menos na fase de parse — e 4,4% num arquivo só, que também é o número.",
};

const blocos: Bloco[] = [
  {"p": "A cada execução, o lexer e o parser refazem **exatamente a mesma coisa** a partir de um arquivo que não mudou. O cache guarda a árvore."},
  {"callout": {"tipo": "atencao", "titulo": "Ele NÃO é um cache de fechamentos", "texto": "`compilador.py` transforma a árvore em funções Python, e função não atravessa processo — não há o que guardar. Chamar isto de \"cache de compilação\" seria prometer o que ele não faz: o que se guarda é a **árvore**."}},
  {"h2": "O número, e os dois números"},
  {"table": {"head": ["Medida", "Sem cache", "Com cache"], "rows": [["a fase de parse, 269 arquivos", "258,7 ms", "**17,9 ms** — 93% menos"], ["`dataforge check exercicios` (real, 269 arquivos)", "0,918 s", "**0,524 s** — 43% menos"], ["`dataforge run` num arquivo de 383 linhas", "131,8 ms", "~126 ms — **4,4%**"]]}},
  {"p": "A terceira linha é a desconfortável, e por isso está aqui: **76 ms dos 132 ms** daquele comando são o `import` do próprio Python. O cache vale onde há **muitos** arquivos — o `check` de um projeto, a CI — e quase não aparece num script pequeno. Publicar só a primeira medida seria escolher a medida."},
  {"p": "O cache dos 269 arquivos ocupa **1553 KB**."},
  {"h2": "A chave é o que impede o desastre"},
  {"p": "Um cache que devolve a árvore errada é **pior que nenhum cache**: o programa roda, e roda outra coisa. A chave carrega cinco coisas:"},
  {"list": ["o caminho absoluto do arquivo;", "o `mtime_ns` e o tamanho dele;", "a versão da linguagem;", "o formato do que é guardado;", "e um **resumo da própria implementação** — `lexer.py`, `parser.py`, `ast_nodes.py`, `tokens.py` e `tipos_nomeados.py`."]},
  {"callout": {"tipo": "perigo", "titulo": "O último é o que importa durante o desenvolvimento", "texto": "Mexer no parser sem subir a versão não invalidaria nada, e a execução seguinte leria uma árvore que o parser de hoje **não produz mais**. É o erro mais difícil de diagnosticar que um cache pode causar, porque nada acusa: o programa roda. Há teste tocando o `mtime` do `parser.py` e exigindo que o cache se invalide."}},
  {"h2": "Falhar não pode custar nada"},
  {"table": {"head": ["Se", "Então"], "rows": [["o arquivo do cache está corrompido", "refaz o parse, sem levantar"], ["a versão de `pickle` é outra", "refaz o parse"], ["não há permissão de escrita", "roda sem guardar"], ["o processo morreu no meio da gravação", "não há arquivo pela metade: escreve ao lado e renomeia, e `os.replace` é atômico no POSIX e no Windows"]]}},
  {"p": "**Uma otimização nunca pode ser um motivo de erro.** Toda leitura do cache está num `try`, e toda falha cai no caminho normal."},
  {"h2": "Ligar, desligar, limpar"},
  { code: `DATAFORGE_SEM_CACHE=1 dataforge check src/   # desliga, para medir
DATAFORGE_CACHE=/tmp/meu dataforge check src/ # outra pasta
dataforge clean                               # apaga o cache de arvores`, lang: 'bash' },
  {"p": "`dataforge clean` **sempre** apaga o cache de árvores, e diz quantos arquivos tirou. Deixá-lo para trás faria o `clean` mentir sobre o que limpou — e é justamente o lugar onde um artefato velho engana."},
  {"p": "A prova de que ele é seguro não é o desenho: é o teste que roda exercícios do repositório com a árvore do cache e sem ela, e compara a saída **caractere por caractere** — a mesma rede de segurança do [compilador de fechamentos](/docs/compilador/backend)."},
];

const headings = [{ id: 'o-numero-e-os-dois-numeros', text: "O número, e os dois números", level: 2 as const }, { id: 'a-chave-e-o-que-impede-o-desastre', text: "A chave é o que impede o desastre", level: 2 as const }, { id: 'falhar-nao-pode-custar-nada', text: "Falhar não pode custar nada", level: 2 as const }, { id: 'ligar-desligar-limpar', text: "Ligar, desligar, limpar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O cache de árvores"}
      description={"O lexer e o parser refaziam a mesma árvore a cada execução. Medido: 93% menos na fase de parse — e 4,4% num arquivo só, que também é o número."}
      href={"/docs/cli/cache"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
