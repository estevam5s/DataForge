// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/big_o_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Programação dinâmica",
  description: "Trocar exponencial por polinomial guardando subproblemas — LCS, Levenshtein e a mochila.",
};

const blocos: Bloco[] = [
  {"p": "Programação dinâmica é o que se faz quando uma recursão ingênua recalcula os mesmos subproblemas milhares de vezes. Guarda-se cada resposta numa tabela, e o custo cai de exponencial para o tamanho da tabela."},
  { code: `adopt Arcane.Algoritmos as Alg

// A maior subsequencia comum: O(n·m). Pode haver mais de uma do mesmo
// tamanho (BCBA, BDAB, BCAB) — o que e garantido e o TAMANHO.
s := Alg.lcs("ABCBDAB", "BDCABA")
assert len(s) is 4

// Quantas edicoes separam duas palavras: O(n·m), e sugere o que foi quase digitado.
assert Alg.levenshtein("gato", "rato") is 1
palavras := ["arvore", "arroz", "ervilha"]
digitado := "arvroe"
mais_perto := sorted(palavras, lambda p: Alg.levenshtein(p, digitado))[0]
assert mais_perto is "arvore"

// A mochila 0/1: o que levar para o maior valor sem passar do peso. O(n·W).
itens := [
    {"nome": "notebook", "peso": 3, "valor": 2000},
    {"nome": "camera", "peso": 2, "valor": 1500},
    {"nome": "livro", "peso": 1, "valor": 300},
    {"nome": "tripe", "peso": 2, "valor": 400}]
r := Alg.mochila(itens, 5)
assert r["valor"] is 3500
assert (r["escolhidos"] >> morph i: i["nome"]) is ["notebook", "camera"]`, lang: 'df' },
  {"h2": "O mesmo problema, sem a tabela"},
  { code: `// Levenshtein recursivo: cada chamada abre tres — O(3^n).
action lev(a, b):
    given len(a) is 0:
        yield len(b)
    given len(b) is 0:
        yield len(a)
    custo := 0 given a[0] is b[0] otherwise 1
    yield min(lev(a[1:], b) + 1, lev(a, b[1:]) + 1, lev(a[1:], b[1:]) + custo)

assert lev("gato", "rato") is 1     // ok com 4 letras; com 12, nao termina hoje`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O(n·W) não é polinomial de verdade", "texto": "O custo da mochila depende de **W**, a capacidade — e não do tamanho da entrada, que é o número de dígitos de W. Com W de um milhão, a tabela tem um milhão de colunas. Por isso se diz *pseudo-polinomial*, e por isso o peso precisa ser inteiro."}},
];

const headings = [{ id: 'o-mesmo-problema-sem-a-tabela', text: "O mesmo problema, sem a tabela", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Programação dinâmica"}
      description={"Trocar exponencial por polinomial guardando subproblemas — LCS, Levenshtein e a mochila."}
      href={"/docs/big-o/programacao-dinamica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
