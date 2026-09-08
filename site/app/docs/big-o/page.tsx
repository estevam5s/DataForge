import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Complexidade e Big-O",
  description: "Quanto o seu código cresce — e como o DataForge mede isso sem rodar nada.",
};

const blocos: Bloco[] = [
  {"p": "Um algoritmo que funciona com dez itens pode não terminar com um milhão. **Big-O é a linguagem para falar disso antes de descobrir na produção.**"},
  {"p": "O DataForge analisa complexidade de dentro: `dataforge big-o` lê a árvore do seu programa e diz a classe de cada ação — e o motivo. Não é uma calculadora à parte; é o mesmo compilador que roda o código."},
  { code: `action comuns(xs, ys):
    saida := []
    cycle x in xs:
        given x in ys:
            saida.append(x)
    yield saida`, lang: 'df' },
  { code: `$ dataforge big-o exemplo.df -v

  ▲ comuns                     O(n^2)      tempo   O(n) espaco
      · 'cycle … in 'xs'' na linha 3 anda uma vez por item
      · 'in' na linha 4 percorre a colecao (use um vault para O(1))
      ⚠ O(n^2): dobrar a entrada quadruplica o tempo.
        se um dos lacos so procura um item, um vault faz isso em O(1)`, lang: 'bash' },
  {"callout": {"tipo": "dica", "titulo": "O porquê vem junto", "texto": "`O(n²)` sozinho não ajuda a melhorar nada. O relatório sempre diz **onde** e **o que fazer** — é a diferença entre um número e uma ferramenta."}},
  {"h2": "As curvas"},
  {"p": "A tabela diz que O(n²) é pior que O(n log n). O gráfico mostra *quanto* — e é isso que decide projeto. Clique nas classes para comparar; arraste para mudar o tamanho da entrada."},
  {"componente": "curvas-big-o"},
  {"h2": "O que cada classe custa"},
  {"p": "Os números não são decorativos. É a diferença entre \"isso é lento\" e \"isso não termina antes do almoço\":"},
  {"componente": "escala-big-o"},
  {"p": "Um O(n²) com um milhão de itens são 10¹² operações — cerca de **onze dias** a um milhão de operações por segundo. O mesmo problema em O(n log n) são 20 milhões: **vinte segundos**."},
  {"h2": "Linear contra logarítmica, vendo"},
  {"p": "A busca linear olha caixa por caixa. A binária descarta metade a cada passo. Com 32 itens a diferença já aparece; com um milhão, é 1.000.000 contra 20."},
  {"componente": "corrida-busca"},
  {"h2": "O que Big-O não diz"},
  {"p": "Três coisas que a notação deliberadamente ignora, e que às vezes decidem a escolha:"},
  {"list": ["**A constante.** O(n) com constante 1000 perde de O(n²) com constante 1 até n=1000. Big-O é sobre crescimento, não sobre velocidade.", "**A memória.** Um algoritmo O(n log n) que aloca uma cópia pode perder para um O(n²) que trabalha no lugar, quando a memória é o gargalo.", "**O caso médio.** O(n²) é o pior caso do quicksort; o médio é O(n log n), e é ele que se observa. Ver [melhor, médio e pior caso](/docs/big-o/casos)."]},
  {"callout": {"tipo": "nota", "titulo": "Meça também", "texto": "A análise diz como o custo cresce. `dataforge profile` diz quanto ele é hoje, no seu computador, com os seus dados. As duas coisas respondem perguntas diferentes, e você precisa das duas."}},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/big-o/classes", "title": "As classes", "desc": "de O(1) a O(n!), com exemplo em DataForge de cada uma"}, {"href": "/docs/big-o/analisar", "title": "Analisar o seu código", "desc": "o comando, as opções, e o que ele consegue e não consegue provar"}, {"href": "/docs/big-o/padroes", "title": "Padrões e como melhorar", "desc": "os cinco jeitos mais comuns de escrever um O(n²) sem querer"}, {"href": "/docs/big-o/estruturas", "title": "Custo das estruturas", "desc": "cluster, vault, string — o que cada operação custa"}, {"href": "/docs/big-o/casos", "title": "Melhor, médio e pior", "desc": "e a análise amortizada, que explica por que 'append' é O(1)"}, {"href": "/docs/big-o/espaco", "title": "Complexidade de espaço", "desc": "trocar tempo por memória, e quando vale"}]},
];

const headings = [{ id: 'as-curvas', text: "As curvas", level: 2 as const }, { id: 'o-que-cada-classe-custa', text: "O que cada classe custa", level: 2 as const }, { id: 'linear-contra-logaritmica-vendo', text: "Linear contra logarítmica, vendo", level: 2 as const }, { id: 'o-que-big-o-nao-diz', text: "O que Big-O não diz", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Complexidade e Big-O"}
      description={"Quanto o seu código cresce — e como o DataForge mede isso sem rodar nada."}
      href={"/docs/big-o"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
