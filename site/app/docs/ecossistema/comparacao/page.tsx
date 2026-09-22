// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Comparada com outras linguagens",
  description: "Python, JavaScript, Go e Rust lado a lado: sintaxe, tipos, concorrência, erros — e onde DataForge escolheu diferente.",
};

const blocos: Bloco[] = [
  {"p": "DataForge roda sobre o CPython, e em execução se parece mais com Python do que com qualquer outra. Na **escrita**, as escolhas vieram de lugares diferentes — e esta tabela diz de onde, e o que ficou de fora."},
  {"table": {"head": ["", "DataForge", "Python", "JavaScript", "Go", "Rust"], "rows": [["atribuição", "`x := 1`", "`x = 1`", "`let x = 1`", "`x := 1`", "`let x = 1`"], ["tipos", "opcionais, conferidos pelo `check` e em execução", "opcionais, só por ferramenta", "TypeScript à parte", "estáticos", "estáticos, com dono"], ["nulo", "`void`, com `??` e `?.`", "`None`", "`null`/`undefined`", "`nil`", "`Option`"], ["erro", "`monitor`/`handle`, e `Resultado` como valor", "`try`/`except`", "`try`/`catch`", "valor de retorno", "`Result`"], ["concorrência", "threads, laço, fibras, atores, STM, processos", "threads + GIL, asyncio", "laço único", "goroutines + canais", "threads + async"], ["divisão inteira", "`~/`", "`//`", "`Math.floor(a/b)`", "`/` em inteiros", "`/` em inteiros"], ["pipeline", "`>> sift`, `>> morph`", "—", "—", "—", "iteradores"], ["pacotes", "`dataforge add`, com lock e sha256", "pip", "npm", "go mod", "cargo"]]}},
  { code: `// o canal do Go, o ator do Erlang e o Resultado do Rust — na mesma linguagem
adopt Arcane.Laco as L
adopt Arcane.Concurrent as P
adopt Arcane.Resultado as Res

c := L.canal(1)
a := P.ator(lambda soma, v: soma + v, 0)
a.enviar(5)
assert a.parar() is 5
assert Res.ok(3).deu_certo()`, lang: 'df' },
  {"h2": "O que ficou de fora, de propósito"},
  {"list": ["**Compilação para código nativo.** O interpretador compila a árvore para fechamentos do Python (1,5× a 1,8×); o teto dessa técnica é ~6,5×. Ir além exigiria sair do Python — e da dependência zero.", "**Operadores de bits.** `>>`, `|` e `&` já têm dono (pipeline, união e interseção de tipos); as [operações de bits](/docs/estruturas/operacoes-de-bits) são funções.", "**Macro que reescreve sintaxe.** Há [macro sobre a árvore](/docs/metaprogramacao/macros), mas não uma que invente palavra nova."]},
];

const headings = [{ id: 'o-que-ficou-de-fora-de-proposito', text: "O que ficou de fora, de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Comparada com outras linguagens"}
      description={"Python, JavaScript, Go e Rust lado a lado: sintaxe, tipos, concorrência, erros — e onde DataForge escolheu diferente."}
      href={"/docs/ecossistema/comparacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
