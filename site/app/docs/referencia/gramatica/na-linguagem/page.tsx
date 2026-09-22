// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/gramatica_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A gramática, de dentro de um programa",
  description: "Arcane.Gramatica e dataforge gramatica — perguntar à linguagem como ela é.",
};

const blocos: Bloco[] = [
  {"p": "Um editor, um formatador ou um gerador de documentação escrito em DataForge não precisa manter uma cópia da gramática: ele pergunta **à linguagem**. `Arcane.Gramatica` expõe as produções, a precedência, os tokens e a validação — com o lexer e o parser de verdade, e sem executar nada."},
  { code: `adopt Arcane.Gramatica as G

out len(G.producoes()), "producoes em", len(G.grupos()), "grupos"
out G.producao("guard")["ebnf"]

// Quem liga mais forte? A resposta sai da arvore.
assert G.raiz("1 + 2 * 3") is ["BinaryOp", "+"]

// O que o parser entendeu, instrucao por instrucao.
assert G.instrucoes("x := 1\\nout x") is ["Assignment", "OutStatement"]

// Validar o texto que um usuario digitou — sem executa-lo.
r := G.validar("x := (1 +")
assert not r["ok"]
out $"linha {r['erros'][0]['linha']}: {r['erros'][0]['mensagem']}"

assert "cycle" in G.palavras()["reservadas"]
assert "route" in G.palavras()["contextuais"]`, lang: 'df' },
  {"table": {"head": ["Função", "Devolve"], "rows": [["`producoes(grupo)`", "as produções — nome, EBNF, exemplo, nós, nota"], ["`producao(nome)`", "uma; o nome errado é recusado com sugestão"], ["`grupos()` / `ebnf(grupo)`", "os grupos; o texto EBNF"], ["`precedencia()`", "a escada, da mais fraca para a mais forte"], ["`raiz(expressao)`", "a classe e o operador na raiz da árvore"], ["`tokens(texto)`", "o que o lexer viu, com linha e coluna"], ["`instrucoes(texto)`", "a classe de cada instrução de topo"], ["`validar(texto)`", "`{ok, instrucoes, erros}` — sem executar"], ["`palavras()`", "as reservadas e as contextuais"]]}},
  {"h2": "No terminal"},
  { code: `dataforge gramatica                      # os grupos
dataforge gramatica pipeline             # uma producao: EBNF, exemplo, nota
dataforge gramatica expressoes --ebnf    # o EBNF de um grupo
dataforge gramatica --ebnf               # a gramatica inteira
dataforge gramatica --precedencia        # quem liga mais forte
dataforge gramatica --json               # como dado`, lang: 'bash' },
  {"callout": {"tipo": "dica", "titulo": "A garantia", "texto": "São 56 produções, e cobrem as 81 palavras reservadas — há teste exigindo que toda palavra reservada apareça em alguma. Uma palavra fora da gramática seria uma parte da linguagem que a documentação não descreve."}},
];

const headings = [{ id: 'no-terminal', text: "No terminal", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A gramática, de dentro de um programa"}
      description={"Arcane.Gramatica e dataforge gramatica — perguntar à linguagem como ela é."}
      href={"/docs/referencia/gramatica/na-linguagem"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
