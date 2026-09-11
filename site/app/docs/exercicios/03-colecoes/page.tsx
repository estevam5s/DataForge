// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "03 · Colecoes",
  description: "14 exercícios: cluster e vault, fatias, spread e compreensões.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 03`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["025", "**Clusters (listas)**", "crie, acesse e altere elementos de um cluster."], ["026", "**Fatiamento**", "extraia trechos de um cluster com [inicio:fim:passo]."], ["027", "**Metodos de cluster**", "use append, insert, remove, pop, sort e reverse."], ["028", "**Agregacoes numericas**", "calcule soma, minimo, maximo e media de um cluster."], ["029", "**unique, flatten e chunk**", "limpe e reorganize dados aninhados."], ["030", "**Ordenacao**", "ordene numeros e textos, e ordene ao contrario."], ["031", "**Vaults (dicionarios)**", "crie, leia, atualize e remova chaves de um vault."], ["032", "**Percorrendo vaults**", "use keys, values e items para somar um estoque."], ["033", "**Operacoes avancadas de vault**", "use merge, pick, omit, invert e map_values."], ["034", "**Matrizes**", "monte uma matriz identidade 3x3 e calcule o traco."], ["035", "**Pilha e fila**", "implemente LIFO e FIFO usando cluster."], ["036", "**Busca linear e binaria**", "implemente as duas buscas e compare o resultado."], ["037", "**Bubble sort**", "ordene um cluster sem usar sorted()."], ["038", "**Contagem de frequencias**", "conte quantas vezes cada item aparece."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/03-colecoes/025_clusters.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"03 · Colecoes"}
      description={"14 exercícios: cluster e vault, fatias, spread e compreensões."}
      href={"/docs/exercicios/03-colecoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
