// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fundamentos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Igualdade e comparação",
  description: "is compara pelo valor, por estrutura — e as três formas de comparar coleções e objetos.",
};

const blocos: Bloco[] = [
  {"p": "`is` pergunta *“são iguais?”* **pelo valor**, e não *“são o mesmo objeto?”*. Duas listas com os mesmos itens são iguais; dois records com os mesmos campos também."},
  { code: `assert [1, 2] is [1, 2]
assert {"a": 1, "b": 2} is {"b": 2, "a": 1}     // a ordem das chaves nao importa
assert {1, 2} is {2, 1}
assert [1, 2] isnt [2, 1]                        // a ordem da lista importa

record Ponto:
    x: Integer
    y: Integer
assert Ponto(1, 2) is Ponto(1, 2)               // record: por estrutura
assert Ponto(1, 2) isnt Ponto(2, 1)`, lang: 'df' },
  {"h2": "Tipos diferentes nunca são iguais"},
  { code: `assert 1 isnt "1"
assert 1 is 1.0                    // numeros comparam pelo valor
// 1 is "1" e acusado pelo check: 'igualdade-impossivel'`, lang: 'df' },
  {"h2": "Ordenar"},
  { code: `assert "banana" bigger "abacate"          // texto: ordem de dicionario
assert "Z" smaller "a"                       // maiuscula vem antes!
assert sorted(["b", "A", "c"]) is ["A", "b", "c"]
assert sorted(["b", "A", "c"], lambda s: s.lower()) is ["A", "b", "c"]
assert 1 smaller 2 smaller 3                  // a comparacao encadeia`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Blueprint compara por identidade — a menos que você diga", "texto": "Duas instâncias de um `blueprint` são iguais só se forem o **mesmo** objeto, porque um objeto mutável com os mesmos campos hoje pode ter campos diferentes amanhã. Para comparar por valor, declare `__eq__` — ver [métodos mágicos](/docs/oop/magicos)."}},
];

const headings = [{ id: 'tipos-diferentes-nunca-sao-iguais', text: "Tipos diferentes nunca são iguais", level: 2 as const }, { id: 'ordenar', text: "Ordenar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Igualdade e comparação"}
      description={"is compara pelo valor, por estrutura — e as três formas de comparar coleções e objetos."}
      href={"/docs/fundamentos/igualdade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
