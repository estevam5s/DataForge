// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_literais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Tipos literais",
  description: "Um valor vira um tipo: type Estado := \"ativo\" | \"inativo\". A conferência acontece onde o dado entra, e não espalhada por cinquenta comparações.",
};

const blocos: Bloco[] = [
  {"p": "Um tipo literal é um tipo cujo conjunto de valores tem **um** elemento. Sozinho ele é curioso; em união ele é o recurso: `type Estado := \"ativo\" | \"inativo\"` diz, num lugar só, o que antes vivia espalhado em `given e is \"ativo\" or e is \"inativo\"` — e esquecido numa das fronteiras."},
  {"h2": "A forma"},
  { code: `type Estado := "ativo" | "inativo" | "suspenso"
type Nivel  := 1 | 2 | 3
type Ligado := yes

action mudar(e: Estado) -> String:
    yield e

assert mudar("ativo") is "ativo"
assert mudar("suspenso") is "suspenso"
out "a fronteira confere, e o resto do programa nao precisa"
`, lang: 'df' },
  {"p": "Texto, inteiro, decimal e booleano podem ser literais. `void` fica de fora de propósito: `Void` já é o tipo dele, e `type T := void` seria uma segunda forma de dizer a mesma coisa."},
  {"h2": "Onde ele é cobrado"},
  {"table": {"head": ["Momento", "O que acontece"], "rows": [["`dataforge check`, com o **literal** na mão", "acusa, e lista os valores que valem (`tipo-literal`)"], ["`dataforge check`, com uma variável", "**cala** — não há o que provar"], ["execução, em toda fronteira", "recusa, nomeando o tipo e o que chegou"]]}},
  { code: `type Estado := "ativo" | "inativo"

// Provado antes de rodar: o literal esta na mao.
// e: Estado := "zzz"
//   erro: a variável 'e' declared as Estado ("ativo" | "inativo")
//         but the value is 'zzz'

// E cobrado na fronteira, quando o valor vem de fora.
action mudar(e: Estado) -> String:
    yield e

recusou := no
monitor:
    mudar("zzz")
handle Error as erro:
    recusou := yes

assert recusou
out "o que o analisador nao prova, a fronteira cobra"
`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O silêncio é o recurso", "texto": "Um `String` que veio de `input()` ou de uma coluna não prova nada, e acusá-lo recusaria justamente o código para o qual o tipo existe: **ler a entrada e passá-la adiante**, deixando a fronteira decidir. O analisador só fala com o literal na mão."}},
  {"h2": "`yes` e `1` não se confundem"},
  {"p": "A comparação é por igualdade **e** por tipo. Em Python `True == 1` é verdadeiro, e sem a conferência de tipo um `type Ligado := yes` aceitaria o número 1 calado — um valor que nunca foi escrito passando por um tipo que existe para não deixar."},
  {"h2": "A base de uma união de literais é conhecida"},
  { code: `type Estado := "ativo" | "inativo"

action rotulo(e: Estado) -> String:
    // 'e' e um String para o analisador, e por isso isto e aceito:
    // sem essa leitura, devolver 'e' num '-> String' seria acusado.
    yield e + "!"

assert rotulo("ativo") is "ativo!"
out "uniao so de literais do mesmo tipo abre para a base"
`, lang: 'df' },
  {"p": "Uma união **mista** — `\"auto\" | Integer` — não tem base única, e ali o analisador volta a calar em vez de escolher uma: escolher faria ele aprovar o que a execução recusa."},
  {"h2": "Quando usar, e quando não"},
  {"table": {"head": ["Use um tipo literal quando", "Use um `enum` quando"], "rows": [["o valor **é** o dado — vem de um JSON, de uma coluna, de um `?estado=`", "o valor é um conceito do domínio, com nome próprio"], ["você quer conferir na fronteira sem converter nada", "você quer método, `.name`, `.value` e exaustividade no `match`"], ["a lista é pequena e fechada", "a lista cresce, ou carrega comportamento"]]}},
  {"cards": [{"href": "/docs/tipos", "title": "O sistema de tipos", "desc": "o guia"}, {"href": "/docs/faq/tipos", "title": "FAQ: tipos", "desc": "o que é conferido, e quando"}, {"href": "/docs/tipos/genericos", "title": "Genéricos", "desc": "`<T extends X>`"}]},
];

const headings = [{ id: 'a-forma', text: "A forma", level: 2 as const }, { id: 'onde-ele-e-cobrado', text: "Onde ele é cobrado", level: 2 as const }, { id: 'yes-e-1-nao-se-confundem', text: "`yes` e `1` não se confundem", level: 2 as const }, { id: 'a-base-de-uma-uniao-de-literais-e-conhecida', text: "A base de uma união de literais é conhecida", level: 2 as const }, { id: 'quando-usar-e-quando-nao', text: "Quando usar, e quando não", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Tipos literais"}
      description={"Um valor vira um tipo: type Estado := \"ativo\" | \"inativo\". A conferência acontece onde o dado entra, e não espalhada por cinquenta comparações."}
      href={"/docs/tipos/literais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
