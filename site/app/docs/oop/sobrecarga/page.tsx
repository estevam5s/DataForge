// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sobrecarga",
  description: "overload: variantes da mesma ação escolhidas pela aridade e pelos tipos, com empate recusado.",
};

const blocos: Bloco[] = [
  {"p": "Uma linguagem dinâmica não precisa de sobrecarga para aceitar tipos diferentes — um `given typeof(x)` resolve. O que ela ganha com sobrecarga é **declarar** as formas aceitas, e deixar a linguagem recusar a que não serve com a lista das que servem."},
  { code: `overload action formatar(valor: Integer):
    yield $"{valor}"
overload action formatar(valor: Float):
    yield $"{round(valor, 2)}"
overload action formatar(valor: String, largura: Integer):
    yield valor.ljust(largura)

assert formatar(3) is "3"
assert formatar(2.5) is "2.5"
assert formatar("ab", 4) is "ab  "

monitor:
    formatar(yes)
    assert no
handle OverloadResolutionError as e:
    out e.message`, lang: 'df' },
  {"h2": "Como a variante é escolhida"},
  {"list": ["descarta as que não aceitam a **quantidade** e os **nomes** dos argumentos;", "confere os **tipos declarados**, com a mesma regra de qualquer anotação (um `Integer` serve onde se pede `Float`);", "entre as que sobram, vence a que declara **mais tipos** — a mais específica;", "um empate é `AmbiguousOverloadError`. Escolher pela ordem de escrita faria mover uma variante de lugar mudar um programa que não a chama."], "ordered": true},
  {"h2": "Construtores sobrecarregados"},
  { code: `blueprint Cor:
    r := 0
    g := 0
    b := 0
    overload action setup(cinza: Integer):
        self.r := cinza
        self.g := cinza
        self.b := cinza
    overload action setup(r: Integer, g: Integer, b: Integer):
        self.r := r
        self.g := g
        self.b := b

assert (spawn Cor(128)).g is 128
assert (spawn Cor(1, 2, 3)).b is 3`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Todas marcadas", "texto": "Toda variante leva `overload`, inclusive a primeira. Misturar uma ação comum com variantes do mesmo nome é recusado: não há leitura em que as duas convivam."}},
];

const headings = [{ id: 'como-a-variante-e-escolhida', text: "Como a variante é escolhida", level: 2 as const }, { id: 'construtores-sobrecarregados', text: "Construtores sobrecarregados", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sobrecarga"}
      description={"overload: variantes da mesma ação escolhidas pela aridade e pelos tipos, com empate recusado."}
      href={"/docs/oop/sobrecarga"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
