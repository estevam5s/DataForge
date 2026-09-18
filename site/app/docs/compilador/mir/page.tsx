// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/compilador_interno.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "MIR — o grafo de fluxo",
  description: "Bloco básico, aresta rotulada, laço com aresta de volta e tratador de erro: a representação que responde por onde o programa passa.",
};

const blocos: Bloco[] = [
  {"p": "A árvore diz o que o programa **é**; o grafo diz por onde ele **passa**. São perguntas diferentes, e as que mais interessam a um analisador só a segunda responde: este código é alcançável? este nome está definido em todo caminho que chega aqui? este local escapa do quadro?"},
  {"p": "`construir` devolve um **corpo** por ação — mais um chamado `(programa)` para o nível de topo, e um por rota do Kiln. Cada corpo é uma lista de **blocos básicos**: uma sequência de instruções sem desvio no meio, com arestas rotuladas para os seguintes."},
  { code: `  classificar(n)   7 bloco(s), 2 inalcancavel(is)
     bloco 0 [entrada] → 1 (sim), 2 (nao)
        linha 5: ComparisonOp bigger
     bloco 1 [sim] ⏹ yield
        linha 6: YieldStatement
     bloco 2 [nao] → 3 (sim), 4 (nao)
        linha 7: ComparisonOp smaller
     bloco 3 [sim] ⏹ yield
        linha 8: YieldStatement
     bloco 4 [nao] ⏹ yield
        linha 10: YieldStatement
   × bloco 5 [juncao] → 6
   × bloco 6 [juncao] ⏹ fim`, lang: 'text', title: `dataforge ir --fase=mir` },
  {"p": "O `×` marca o bloco **inalcançável**: todos os três ramos encerram com `yield`, então a junção não tem como ser atingida. E os dois blocos de junção, em vez de um, são o `orif` já aberto pelo HIR — o que mostra a normalização pagando o preço dela."},
  {"h2": "Os rótulos de aresta"},
  {"table": {"head": ["Aresta", "Quando"], "rows": [["*(sem rótulo)*", "cai no seguinte"], ["`sim` · `nao`", "os dois lados de um `given`, de um laço ou de um `guard`"], ["`volta`", "a aresta de trás de um laço — sem ela não é laço"], ["`halt` · `skip`", "sai do laço, ou volta para a condição"], ["`erro`", "do corpo de um `monitor` para o `handle`"], ["`point` · `default`", "os ramos de um `match`"], ["`defer`", "o corpo que roda na saída da ação"]]}},
  { code: `adopt Arcane.Compilador as K

fonte := "n := 3\\npersist n bigger 0:\\n    n -= 1\\nout n\\n"

blocos := K.blocos(fonte, "(programa)")
voltas := [b cycle b in blocos
           given len([s cycle s in b["saidas"] given s["aresta"] is "volta"]) bigger 0]
assert len(voltas) is 1          // um laco tem uma aresta de volta`, lang: 'df' },
  {"h2": "Três decisões que valem lembrar"},
  {"callout": {"tipo": "nota", "titulo": "O MIR é construído a partir do HIR", "texto": "É o que paga a normalização. Sem ela, `orif` e `perform` seriam dois casos a mais no construtor de grafo — e um caso esquecido num construtor de grafo **não dá erro**: produz análise errada com cara de verdade."}},
  {"p": "**A aresta de erro sai da ENTRADA do `monitor`**, e não de cada instrução do corpo. Precisa ser assim para a análise ficar conservadora: o `handle` vê o estado de **antes** do corpo, que é o pior caso honesto. Uma aresta por instrução daria o mesmo resultado com um grafo três vezes maior."},
  {"p": "**O que roda fora da ordem é opaco.** `thread`, `parallel`, `server`, `crucible` e as suas famílias entram como **uma** instrução. Abrir o corpo deles num grafo sequencial afirmaria uma ordem que não existe — e é exatamente sobre concorrência que uma afirmação errada custa."},
  { code: `adopt Arcane.Compilador as K

fonte := "monitor:\\n    x := 1\\nhandle Error as e:\\n    out e.message\\nensure:\\n    out 2\\n"

rotulos := [b["rotulo"] cycle b in K.blocos(fonte, "(programa)")]
assert "tratador" in rotulos
assert "ensure" in rotulos`, lang: 'df' },
];

const headings = [{ id: 'os-rotulos-de-aresta', text: "Os rótulos de aresta", level: 2 as const }, { id: 'tres-decisoes-que-valem-lembrar', text: "Três decisões que valem lembrar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"MIR — o grafo de fluxo"}
      description={"Bloco básico, aresta rotulada, laço com aresta de volta e tratador de erro: a representação que responde por onde o programa passa."}
      href={"/docs/compilador/mir"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
