import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "03 · Coleções",
  description: "14 exercícios: clusters, fatiamento, vaults, matrizes, busca e ordenação.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 03`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["025", "**Clusters (listas)**", "crie, acesse e altere elementos de um cluster."], ["026", "**Fatiamento**", "extraia trechos de um cluster com [inicio:fim:passo]."], ["027", "**Metodos de cluster**", "use append, insert, remove, pop, sort e reverse."], ["028", "**Agregacoes numericas**", "calcule soma, minimo, maximo e media de um cluster."], ["029", "**unique, flatten e chunk**", "limpe e reorganize dados aninhados."], ["030", "**Ordenacao**", "ordene numeros e textos, e ordene ao contrario."], ["031", "**Vaults (dicionarios)**", "crie, leia, atualize e remova chaves de um vault."], ["032", "**Percorrendo vaults**", "use keys, values e items para somar um estoque."], ["033", "**Operacoes avancadas de vault**", "use merge, pick, omit, invert e map_values."], ["034", "**Matrizes**", "monte uma matriz identidade 3x3 e calcule o traco."], ["035", "**Pilha e fila**", "implemente LIFO e FIFO usando cluster."], ["036", "**Busca linear e binaria**", "implemente as duas buscas e compare o resultado."], ["037", "**Bubble sort**", "ordene um cluster sem usar sorted()."], ["038", "**Contagem de frequencias**", "conte quantas vezes cada item aparece."]]}},
  {"h2": "025 · Clusters (listas)"},
  {"p": "Crie, acesse e altere elementos de um cluster."},
  { code: `// Exercicio 025 — Clusters (listas)
// Enunciado: crie, acesse e altere elementos de um cluster.

nums := [10, 20, 30, 40, 50]
out "primeiro:", nums[0], "ultimo:", nums[-1], "tamanho:", len(nums)

nums[1] := 99
out nums

assert nums[0] is 10, "indice 0"
assert nums[-1] is 50, "indice negativo"
assert nums[1] is 99, "atribuicao por indice"
assert len(nums) is 5, "tamanho"
`, title: `025_clusters.df` },
  {"h2": "026 · Fatiamento"},
  {"p": "Extraia trechos de um cluster com [inicio:fim:passo]."},
  { code: `// Exercicio 026 — Fatiamento
// Enunciado: extraia trechos de um cluster com [inicio:fim:passo].

letras := ["a", "b", "c", "d", "e", "f"]

out letras[1:4], letras[:3], letras[3:], letras[::2], letras[-2:]

assert letras[1:4] is ["b", "c", "d"], "intervalo"
assert letras[:3] is ["a", "b", "c"], "do inicio"
assert letras[3:] is ["d", "e", "f"], "ate o fim"
assert letras[::2] is ["a", "c", "e"], "passo 2"
assert letras[-2:] is ["e", "f"], "dois ultimos"
assert letras[::-1] is ["f", "e", "d", "c", "b", "a"], "invertido"
`, title: `026_fatiamento.df` },
  {"h2": "Os demais"},
  {"p": "Os outros 12 exercícios deste módulo estão em `exercicios/03-colecoes/`. Rode-os com o comando acima."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '025--clusters-listas', text: "025 · Clusters (listas)", level: 2 as const }, { id: '026--fatiamento', text: "026 · Fatiamento", level: 2 as const }, { id: 'os-demais', text: "Os demais", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"03 · Coleções"}
      description={"14 exercícios: clusters, fatiamento, vaults, matrizes, busca e ordenação."}
      href={"/docs/exercicios/03-colecoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
