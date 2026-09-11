// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Padrões e como melhorar",
  description: "Os cinco jeitos mais comuns de escrever um O(n²) sem querer — e a versão linear de cada um.",
};

const blocos: Bloco[] = [
  {"p": "Quase todo O(n²) acidental cai num destes cinco padrões. Os cinco têm versão linear, e as cinco usam a mesma ideia: **trocar busca por indexação**."},
  {"h2": "1. `in` sobre cluster dentro de laço"},
  {"p": "O mais comum de todos. O laço está à vista; o custo do `in` não."},
  { code: `// O(n²) — 'in' percorre 'ys' a cada item de 'xs'
action comuns_lento(xs, ys):
    saida := []
    cycle x in xs:
        given x in ys:
            saida.append(x)
    yield saida`, lang: 'df' },
  { code: `// O(n) — o vault responde em O(1)
action comuns(xs, ys):
    indice := {}
    cycle y in ys:
        indice[str(y)] := yes

    saida := []
    cycle x in xs:
        given indice.has(str(x)):
            saida.append(x)
    yield saida

assert comuns([1, 2, 3], [2, 3, 4]) is [2, 3]`, lang: 'df' },
  {"h2": "2. Procurar dentro do laço"},
  { code: `// O(n²) — 'index_of' percorre a cada volta
action posicoes_lento(xs, alvos):
    yield [xs.index_of(a) cycle a in alvos]`, lang: 'df' },
  { code: `// O(n) — um índice, construído uma vez
action posicoes(xs, alvos):
    onde := {}
    cycle i, x in enumerate(xs):
        given not onde.has(str(x)):
            onde[str(x)] := i
    yield [onde[str(a)] ?? -1 cycle a in alvos]

assert posicoes(["a", "b", "c"], ["c", "a"]) is [2, 0]`, lang: 'df' },
  {"h2": "3. Ordenar dentro do laço"},
  { code: `// O(n² log n) — ordena a cada volta
action maiores_lento(grupos):
    yield [sorted(g)[-1] cycle g in grupos]`, lang: 'df' },
  { code: `// O(n) — 'max' não precisa ordenar
action maiores(grupos):
    yield [max(g) cycle g in grupos]

assert maiores([[3, 1], [5, 9]]) is [3, 9]`, lang: 'df' },
  {"p": "Ordenar para pegar o maior é pagar O(n log n) por uma resposta que custa O(n). Vale só quando se quer os *k* maiores, com k grande."},
  {"h2": "4. Concatenar dentro do laço"},
  { code: `// O(n²) — cada '+' copia a string inteira
action juntar_lento(partes):
    saida := ""
    cycle p in partes:
        saida := saida + p
    yield saida`, lang: 'df' },
  { code: `// O(n) — 'join' aloca uma vez
action juntar(partes):
    yield "".join(partes)

assert juntar(["a", "b", "c"]) is "abc"`, lang: 'df' },
  {"p": "Vale para clusters também: `saida := [...saida, x]` dentro de um laço copia tudo a cada volta. Use `saida.append(x)`, que é O(1) amortizado."},
  {"h2": "5. Agrupar comparando todos com todos"},
  { code: `// O(n²) — compara cada um com cada um
action agrupar_lento(itens):
    grupos := []
    cycle item in itens:
        achou := no
        cycle g in grupos:
            given g[0]["tipo"] is item["tipo"]:
                g.append(item)
                achou := yes
        given not achou:
            grupos.append([item])
    yield grupos`, lang: 'df' },
  { code: `// O(n) — o vault agrupa direto
action agrupar(itens):
    yield itens.group_by(lambda i: i["tipo"])

dados := [{"tipo": "a", "n": 1}, {"tipo": "a", "n": 2}, {"tipo": "b", "n": 3}]
assert len(agrupar(dados)["a"]) is 2`, lang: 'df' },
  {"h2": "A ideia por trás dos cinco"},
  {"callout": {"tipo": "dica", "titulo": "Troque busca por indexação", "texto": "Um vault responde \"você tem isto?\" em O(1). Construir o índice custa O(n) uma vez; consultá-lo n vezes custa O(n). Buscar linearmente n vezes custa O(n²). A troca é sempre a mesma, e quase sempre vale."}},
  {"p": "O custo é memória: o índice ocupa O(n). Ver [complexidade de espaço](/docs/big-o/espaco) para quando essa troca **não** vale."},
  {"h2": "Encontrando os seus"},
  { code: `dataforge big-o src/ -v | grep -A3 'O(n^2)'`, lang: 'bash' },
  {"p": "Ou deixe o editor mostrar: a extensão marca com `⟵ acima do limite` tudo o que passa de O(n log n)."},
];

const headings = [{ id: '1-in-sobre-cluster-dentro-de-laco', text: "1. `in` sobre cluster dentro de laço", level: 2 as const }, { id: '2-procurar-dentro-do-laco', text: "2. Procurar dentro do laço", level: 2 as const }, { id: '3-ordenar-dentro-do-laco', text: "3. Ordenar dentro do laço", level: 2 as const }, { id: '4-concatenar-dentro-do-laco', text: "4. Concatenar dentro do laço", level: 2 as const }, { id: '5-agrupar-comparando-todos-com-todos', text: "5. Agrupar comparando todos com todos", level: 2 as const }, { id: 'a-ideia-por-tras-dos-cinco', text: "A ideia por trás dos cinco", level: 2 as const }, { id: 'encontrando-os-seus', text: "Encontrando os seus", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Padrões e como melhorar"}
      description={"Os cinco jeitos mais comuns de escrever um O(n²) sem querer — e a versão linear de cada um."}
      href={"/docs/big-o/padroes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
