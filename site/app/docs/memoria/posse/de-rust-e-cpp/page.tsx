// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/posse_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "De Rust e de C++ para cá",
  description: "O que traduz, o que não traduz, e o que aqui é desnecessário.",
};

const blocos: Bloco[] = [
  {"p": "Quem vem de Rust ou de C++ reconhece os nomes, e a tradução é útil — desde que venha com a diferença que mais importa: **aqui há um coletor**, e por isso a posse é uma disciplina de **recurso**, não uma garantia de memória."},
  {"table": {"head": ["Rust / C++", "DataForge", "Diferença"], "rows": [["`Box<T>` / `unique_ptr`", "`Posse.dono(valor)`", "checado em execução, e no `check` do arquivo"], ["`Rc<T>` / `shared_ptr`", "`Posse.compartilhado(valor)`", "igual, e a contagem também é determinística"], ["`Weak<T>` / `weak_ptr`", "`Posse.fraco(compartilhado)`", "igual"], ["`&T`", "`Posse.com(d, acao)`", "o escopo é a ação, e não um tempo de vida no tipo"], ["`&mut T`", "`Posse.celula`", "exclusividade conferida em execução"], ["`Drop`", "o `ao_soltar` do dono", "igual, e também roda no escopo"], ["RAII", "`defer` e `Posse.escopo`", "o `defer` é da **ação**, não do bloco"], ["*borrow checker*", "`dataforge check`", "prova o que dá num arquivo; o resto é execução"], ["*lifetime* no tipo", "**não existe**", "e é a ausência que mais se nota"]]}},
  {"h2": "O que aqui é desnecessário"},
  {"list": ["**Anotar tempo de vida.** Nada aqui devolve uma referência que pode sobreviver ao dono: `usar` e `com` recebem uma ação, e o valor não escapa por construção.", "**`clone()` por toda parte.** O coletor resolve o compartilhamento de leitura; `clonar` é sobre **quem fecha**, e não sobre quem lê.", "**`unsafe`.** Não há o que desligar: a integridade da memória não depende desta camada.", "**Mover por padrão.** Aqui o padrão é passar a referência; mover é um pedido explícito, porque quase nunca é o que se quer."]},
  {"h2": "E o que é mais fraco, dito sem rodeio"},
  {"table": {"head": ["Em Rust", "Aqui"], "rows": [["o compilador **prova**, e o programa não compila", "o `check` prova o que dá num arquivo; o resto falha em execução"], ["a regra vale para todo valor", "vale para o que nasceu de `Arcane.Posse`"], ["custo zero em execução", "custo pequeno, mas real: um objeto por recurso"], ["`Send`/`Sync` no tipo", "não há — a travessia de processo confere na hora de atravessar"]]}},
  { code: `adopt Arcane.Posse as Posse

// O que Rust escreveria com tempo de vida, aqui é escopo de ação:
// o valor emprestado NÃO escapa, porque não há como devolvê-lo.
d := Posse.dono([1, 2, 3])

// Isto lê e devolve um DADO, não a referência:
tamanho := Posse.com(d, lambda v => len(v))
assert tamanho is 3

// Mesmo devolvendo o próprio valor, o dono continua sendo o dono, e
// soltar continua fechando na hora certa.
d.soltar()
assert d.solto() is yes`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Quando NÃO usar posse", "texto": "Para um arquivo aberto e fechado na mesma ação, `defer` basta e é mais curto. A posse ganha quando o recurso **atravessa**: vai para dentro de uma estrutura, é devolvido por uma ação, ou tem mais de um candidato a dono. Usá-la em tudo é o mesmo erro de anotar tipo em tudo."}},
];

const headings = [{ id: 'o-que-aqui-e-desnecessario', text: "O que aqui é desnecessário", level: 2 as const }, { id: 'e-o-que-e-mais-fraco-dito-sem-rodeio', text: "E o que é mais fraco, dito sem rodeio", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"De Rust e de C++ para cá"}
      description={"O que traduz, o que não traduz, e o que aqui é desnecessário."}
      href={"/docs/memoria/posse/de-rust-e-cpp"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
