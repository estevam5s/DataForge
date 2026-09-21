// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Observáveis",
  description: "O fluxo no tempo, os operadores, e por que a fonte fria liga preguiçoso.",
};

const blocos: Bloco[] = [
  {"p": "Um observável não tem estado: quem se inscreve recebe o que vier daqui para a frente."},
  { code: `cliques := R.observavel("cliques")

compras := cliques.sift(lambda v => v["botao"] is "comprar")
produtos := compras.morph(lambda v => v["produto"])
inscricao := produtos.distintos().inscrever(lambda p => vistos.append(p))

cliques.emitir({"botao": "ver", "produto": "cafe"})
cliques.emitir({"botao": "comprar", "produto": "cafe"})

inscricao.cancelar()`, lang: 'df' },
  {"h2": "Os operadores"},
  {"table": {"head": ["", "O que faz"], "rows": [["`morph` · `sift` · `distill`", "os mesmos nomes do pipeline `>>` da linguagem"], ["`distintos(chave)`", "só emite quando muda"], ["`primeiros(n)` · `pular(n)`", "recorta o começo do fluxo"], ["`blocos(n)`", "junta em grupos de `n`"], ["`esperar(s)` · `limitar(s)`", "*debounce* e *throttle*"], ["`ao_falhar(f)`", "o erro como valor, e não como interrupção"], ["`para_sinal(inicial)`", "transforma o fluxo em valor"]]}},
  {"h2": "A fonte fria liga preguiçoso"},
  {"p": "`R.de_cluster` e `R.intervalo` são **frias**: só começam quando alguém escuta. O operador só se conecta à sua fonte ao receber o primeiro inscrito — e isso não é uma otimização."},
  { code: `pares := R.de_cluster([1, 2, 3, 4]).sift(lambda n => n % 2 is 0)
pares.morph(lambda n => n * 10).inscrever(lambda n => vistos.append(n))
assert vistos is [20, 40]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Ligando na construção, o resultado era uma lista vazia", "texto": "A fonte despejava os quatro valores no momento em que `sift` se inscrevia nela — antes de `morph` e do assinante final existirem. Sem erro nenhum: só uma lista vazia, que é o pior desfecho possível."}},
  {"h2": "Juntar e combinar"},
  {"p": "`R.juntar(a, b)` intercala os dois fluxos. `R.combinar(a, b)` emite uma tupla com o **último de cada** sempre que qualquer um emite — e só depois que todos já emitiram ao menos uma vez, porque antes disso não há \"último\" para um deles."},
  {"h2": "O exemplo completo"},
  {"p": "`examples/reativo_carrinho.df` percorre sinal, derivado, efeito, lote e observável num carrinho de compras, com `assert` em cada afirmação — inclusive as contagens que **provam** a preguiça."},
];

const headings = [{ id: 'os-operadores', text: "Os operadores", level: 2 as const }, { id: 'a-fonte-fria-liga-preguicoso', text: "A fonte fria liga preguiçoso", level: 2 as const }, { id: 'juntar-e-combinar', text: "Juntar e combinar", level: 2 as const }, { id: 'o-exemplo-completo', text: "O exemplo completo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Observáveis"}
      description={"O fluxo no tempo, os operadores, e por que a fonte fria liga preguiçoso."}
      href={"/docs/reativo/observaveis"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
