import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Coleções",
  description: "Clusters e vaults: criação, acesso, fatiamento e os métodos mais usados.",
};

const blocos: Bloco[] = [
  {"h2": "Clusters — listas"},
  { code: `nums := [10, 20, 30, 40, 50]

out nums[0]        # 10
out nums[-1]       # 50   — índice negativo conta do fim
out len(nums)      # 5

nums[1] := 99      # atribuição por índice` },
  {"h3": "Fatiamento"},
  { code: `l := [1, 2, 3, 4, 5]
out l[1:3]      # [2, 3]
out l[:2]       # [1, 2]
out l[3:]       # [4, 5]
out l[::2]      # [1, 3, 5]
out l[::-1]     # [5, 4, 3, 2, 1]

out "DataForge"[0:4]   # Data` },
  {"p": "A forma é `[inicio:fim:passo]`, com `fim` **exclusivo**. Funciona em `Cluster` e em `String`."},
  {"h3": "Métodos"},
  {"table": {"head": ["Grupo", "Métodos"], "rows": [["adicionar", "`append(x)` `insert(i, x)` `extend(outra)`"], ["remover", "`remove(x)` `pop()` `pop(i)` `clear()`"], ["ordenar", "`sort()` `reverse()` `reversed()`"], ["consultar", "`contains(x)` `index(x)` `count(x)` `first()` `last()`"], ["fatiar", "`take(n)` `drop(n)` `slice(a, b)` `chunk(n)` `rotate(n)`"], ["transformar", "`map(f)` `filter(f)` `reduce(f, ini)` `flatten()` `unique()`"], ["testar", "`every(f)` `some(f)` `find(f)`"], ["agregar", "`sum()` `min()` `max()` `mean()` `frequencies()`"], ["converter", "`join(sep)` `copy()`"]]}},
  { code: `pilha := [3, 1, 2]
pilha.append(4)          # [3, 1, 2, 4]
pilha.sort()             # [1, 2, 3, 4]
out pilha.take(2)        # [1, 2]
out pilha.join(" - ")    # 1 - 2 - 3 - 4` },
  {"h3": "Agregações globais"},
  { code: `v := [120, 340, 90, 500, 210]
out sum(v), min(v), max(v)
out mean(v), median(v), round(stdev(v), 2)
out sorted(v), reversed(v), unique(v)` },
  {"h2": "Vaults — dicionários"},
  { code: `pessoa := {"nome": "Ana", "idade": 30}

out pessoa["nome"]     # acesso por chave
out pessoa.nome        # acesso por ponto — equivalente

pessoa["cidade"] := "Floripa"      # adiciona
pessoa["idade"] := 31              # atualiza` },
  {"h3": "Métodos"},
  {"table": {"head": ["Método", "Faz"], "rows": [["`keys()` `values()` `items()`", "as chaves, os valores, os pares"], ["`has(k)` `get(k, padrao)`", "testa e lê com valor padrão"], ["`set(k, v)` `delete(k)`", "escreve e remove"], ["`merge(outro)`", "mescla, o outro vence"], ["`pick(a, b)` `omit(a)`", "seleciona ou descarta chaves"], ["`invert()`", "troca chaves por valores"], ["`map_values(f)`", "transforma os valores"], ["`length()` `copy()` `clear()`", "tamanho, cópia, limpeza"]]}},
  { code: `v := {"a": 1, "b": 2}
out v.get("z", "padrao")            # padrao — sem estourar
out v.merge({"c": 3})               # {a: 1, b: 2, c: 3}
out v.map_values(lambda x: x * 10)  # {a: 10, b: 20}
out v.invert()                      # {1: a, 2: b}` },
  {"h3": "Percorrendo"},
  { code: `estoque := {"parafuso": 120, "porca": 80}

cycle chave in estoque.keys():
    out $"{chave}: {estoque[chave]}"

cycle par in estoque.items():
    out $"{par[0]} -> {par[1]}"` },
  {"h2": "Escolhendo a estrutura"},
  {"table": {"head": ["Precisa de…", "Use"], "rows": [["ordem e índice", "`Cluster`"], ["acesso por chave", "`Vault`"], ["dados nomeados e tipados", "[`record`](/fundamentos/records)"], ["conjunto fechado de valores", "[`enum`](/fundamentos/enums)"], ["pilha, fila, grafo, heap", "[`Arcane.Collections`](/biblioteca/collections)"]]}},
];

const headings = [{ id: 'clusters--listas', text: "Clusters — listas", level: 2 as const }, { id: 'vaults--dicionarios', text: "Vaults — dicionários", level: 2 as const }, { id: 'escolhendo-a-estrutura', text: "Escolhendo a estrutura", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Coleções"}
      description={"Clusters e vaults: criação, acesso, fatiamento e os métodos mais usados."}
      href={"/colecoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
