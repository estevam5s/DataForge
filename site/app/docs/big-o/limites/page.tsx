// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ω, Θ e limites inferiores",
  description: "O que O, Ω e Θ dizem de diferente — e por que nenhuma ordenação por comparação pode ser melhor que n log n.",
};

const blocos: Bloco[] = [
  {"p": "`O` é um limite **de cima**: \"não custa mais que isto\". Ele sozinho não diz que um algoritmo é bom — dizer que a busca linear é `O(n²)` é verdade, e inútil."},
  {"p": "A família inteira tem cinco membros, e três deles aparecem em conversa de projeto:"},
  {"table": {"head": ["Notação", "Lê-se", "Significa"], "rows": [["`O(f)`", "\"ó grande\"", "cresce **no máximo** como f — limite superior"], ["`Ω(f)`", "\"ômega\"", "cresce **no mínimo** como f — limite inferior"], ["`Θ(f)`", "\"teta\"", "cresce **exatamente** como f — os dois ao mesmo tempo"], ["`o(f)`", "\"ó pequeno\"", "cresce **estritamente menos** que f"], ["`ω(f)`", "\"ômega pequeno\"", "cresce **estritamente mais** que f"]]}},
  {"callout": {"tipo": "nota", "titulo": "O que se diz na prática", "texto": "Quando alguém diz \"o merge sort é O(n log n)\", quase sempre quer dizer `Θ(n log n)` — o limite justo. `O` sozinho é o costume, e não erro: todo `Θ(f)` também é `O(f)`."}},
  {"h2": "Do algoritmo para o problema"},
  {"p": "A mudança de perspectiva que importa: `O` e `Θ` descrevem um **algoritmo**; `Ω` pode descrever o **problema**. Provar que um problema é `Ω(g)` é provar que **nenhum** algoritmo pode fazer melhor — inclusive os que ainda não foram inventados."},
  {"p": "Quando o limite inferior do problema encontra o limite superior de um algoritmo, o assunto está encerrado: ele é **ótimo**, e procurar um melhor é perda de tempo."},
  {"h2": "Nenhuma ordenação por comparação vence `n log n`"},
  {"p": "É o limite inferior mais conhecido, e a prova cabe em três linhas."},
  {"list": ["Ordenar `n` itens é escolher uma entre **n!** permutações possíveis.", "Cada comparação tem **dois** desfechos, então `k` comparações distinguem no máximo `2^k` casos.", "Para `2^k ≥ n!` é preciso `k ≥ log₂(n!)`, e `log₂(n!) ≈ n log n`.", "Logo, **toda** ordenação baseada em comparar é `Ω(n log n)`."], "ordered": true},
  {"p": "O merge sort é `O(n log n)`. Limite inferior e superior coincidem: ele é ótimo na sua classe, e nenhum truque de implementação vai derrubá-lo para `O(n)`."},
  {"h2": "Escapar do limite: não comparar"},
  {"p": "O limite vale para quem **compara**. Um algoritmo que usa o valor como **endereço** não está nessa classe, e por isso pode ser linear:"},
  { code: `// ordenação por contagem: O(n + k), sem comparar nada.
// O preço: só serve para inteiros numa faixa conhecida.
action ordenar_contando(xs, maior):
    contagem := [0] * (maior + 1)
    cycle x in xs:
        contagem[x] += 1
    saida := []
    cycle valor, vezes in enumerate(contagem):
        cycle k from 1 to vezes:
            saida.append(valor)
    yield saida

out ordenar_contando([3, 1, 2, 3, 1], 3)     // [1, 1, 2, 3, 3]`, lang: 'df' },
  {"p": "Não há contradição: a contagem não é uma ordenação por comparação. Ela paga com a **faixa** — `k` entra no custo, e ordenar mil números entre 0 e um bilhão aloca um bilhão de posições."},
  {"callout": {"tipo": "atencao", "titulo": "E ela perde na prática, aqui", "texto": "Medido com 200 mil inteiros de 0 a 999: `sorted` levou **13,5 ms** e a contagem escrita em DataForge, **381 ms** — 28x mais lenta, sendo assintoticamente melhor. O `sorted` roda em C; a contagem roda no interpretador. É o assunto da página [A constante que decide](/docs/big-o/constantes)."}},
  {"h2": "Outros limites inferiores que decidem projeto"},
  {"table": {"head": ["Problema", "Limite", "Consequência"], "rows": [["achar o máximo de uma lista sem ordem", "`Ω(n)`", "não existe atalho: é preciso ver todos"], ["buscar num conjunto **ordenado**, por comparação", "`Ω(log n)`", "a busca binária é ótima"], ["buscar por **igualdade** com tabela de espalhamento", "`Θ(1)` médio", "por isso um vault vence um cluster"], ["ler `n` itens de disco", "`Ω(n/B)` blocos", "o custo é o **bloco**, não o item — ver [complexidade de dados](/docs/big-o/dados)"]]}},
  {"h2": "Quando não se conhece nenhum algoritmo bom"},
  {"p": "Há problemas para os quais ninguém achou solução polinomial **e** ninguém provou que ela não existe. Reconhecê-los é prático: significa parar de procurar o algoritmo esperto e começar a procurar uma aproximação."},
  { code: `// subconjunto que soma exatamente ao alvo: O(2^n) por força bruta
action soma_exata(valores, alvo, i, atual):
    given atual is alvo:
        yield yes
    given i bigger_eq len(valores) or atual bigger alvo:
        yield no
    given soma_exata(valores, alvo, i + 1, atual + valores[i]):
        yield yes
    yield soma_exata(valores, alvo, i + 1, atual)

out soma_exata([3, 34, 4, 12, 5, 2], 9, 0, 0)     // yes`, lang: 'df' },
  {"p": "Três saídas honestas, quando o problema é desses:"},
  {"list": ["**Aproximar** — aceitar 95% da resposta em tempo polinomial.", "**Restringir** — resolver só o caso que o seu sistema realmente tem (valores pequenos, grafo esparso, n abaixo de 30).", "**Podar** — força bruta com corte, como o `atual bigger alvo` acima. Não muda a classe, muda o dia."]},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/big-o/recorrencias", "title": "Recorrências", "desc": "como se resolve o custo de uma função que chama a si mesma"}, {"href": "/docs/big-o/constantes", "title": "A constante que decide", "desc": "por que o melhor no papel perde na máquina"}, {"href": "/docs/big-o/estruturas-avancadas", "title": "Estruturas avançadas", "desc": "heap, união-busca e o custo de cada escolha"}]},
];

const headings = [{ id: 'do-algoritmo-para-o-problema', text: "Do algoritmo para o problema", level: 2 as const }, { id: 'nenhuma-ordenacao-por-comparacao-vence-n-log-n', text: "Nenhuma ordenação por comparação vence `n log n`", level: 2 as const }, { id: 'escapar-do-limite-nao-comparar', text: "Escapar do limite: não comparar", level: 2 as const }, { id: 'outros-limites-inferiores-que-decidem-projeto', text: "Outros limites inferiores que decidem projeto", level: 2 as const }, { id: 'quando-nao-se-conhece-nenhum-algoritmo-bom', text: "Quando não se conhece nenhum algoritmo bom", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ω, Θ e limites inferiores"}
      description={"O que O, Ω e Θ dizem de diferente — e por que nenhuma ordenação por comparação pode ser melhor que n log n."}
      href={"/docs/big-o/limites"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
