// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Tipos: o que é conferido, e quando",
  description: "Anotar é opcional, e o que muda quando você anota. União, refinamento, opaco, genéricos — e onde o analisador cala de propósito.",
};

const blocos: Bloco[] = [
  {"p": "A dúvida mais comum sobre tipos aqui não é *como escrever* — é **quem confere, e quando**. Há duas metades, e elas respondem em momentos diferentes: o `dataforge check` responde antes de rodar, o interpretador responde na fronteira. Saber qual está falando economiza muito tempo."},
  {"h2": "Anotar é opcional; conferir não é"},
  { code: `// sem anotacao: roda, e o check cala sobre o tipo
x := 10

// com anotacao: o check prova o que der para provar, e a execucao
// confere na fronteira
idade: Integer := 30

action dobro(n: Integer) -> Integer:
    yield n * 2

assert dobro(idade) is 60
out "o tipo declarado vale na entrada e na saida"
`, lang: 'df' },
  {"h2": "`type`: uma declaração, seis formas"},
  {"p": "O que muda é o que vem depois do `:=`."},
  { code: `type Id := Integer                              // alias
type Numero := Integer | Float                  // uniao
type Positivo := Integer where valor bigger 0   // refinamento

action guardar(p: Positivo) -> Integer:
    yield p

assert guardar(7) is 7
out "o refinamento vale em TODA fronteira, nao so na criacao"
`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Transparente confere; opaco embrulha", "texto": "Um alias que mudasse o valor quebraria tudo que já aceita um `Integer`. Um opaco que **não** mudasse não protegeria de nada — `cadastrar(senha)` passaria. Por isso `opaque type Cpf := String where …` devolve um valor que **não é** um texto, e delega por protocolo: comparação, ordem, `len` e índice continuam funcionando sem que ninguém saiba o que é um tipo opaco."}},
  {"h2": "`<T>` solto não é conferido; `<T extends X>` é"},
  { code: `// sem limite: documenta a relacao, e aceita qualquer valor
action eco<T>(x: T) -> T:
    yield x

// com limite: cobrado nas duas metades — o check na chamada, a
// execucao no valor. E dentro do corpo, um 'T extends Number' E um
// Number para o analisador: e o que deixa escrever 'a bigger b'.
action maior<T extends Number>(a: T, b: T) -> T:
    yield a given a bigger b otherwise b

assert eco("oi") is "oi"
assert maior(3, 9) is 9
out "o limite atravessa o adopt tambem"
`, lang: 'df' },
  {"h2": "O que o `check` prova a partir de um literal"},
  {"table": {"head": ["Acusa", "Código"], "rows": [["`xs[10]` num cluster de três", "`indice-fora-do-alcance`"], ["`v[\"cidad\"]` num vault sem a chave, com sugestão", "`chave-ausente`"], ["`cycle i from 5 to 1` — nunca roda; `step 0` — nunca termina", "`cycle-vazio`"], ["`1 is \"1\"` — sempre `no`", "`igualdade-impossivel`"], ["`p.clientte` num record, com sugestão", "membro inexistente"], ["`P.criar(1, 2, 3)` vindo de **outro arquivo**", "aridade entre módulos"]]}},
  {"h2": "E o que ele cala, de propósito"},
  {"p": "O silêncio é tão projetado quanto o alarme. Um falso alarme ensina a ignorar mensagens — e depois a desligar a verificação inteira."},
  {"list": ["**`v[\"k\"] ?? padrao` não é acusado.** O `??` é exatamente o que a dica daquele erro recomenda: um analisador que acusa o conserto que ele próprio sugere é um analisador que se desliga.", "**Um parâmetro de tipo não é um tipo.** Sem isso, a trilha ganhava dois alarmes no capítulo que *ensina* genéricos.", "**O tipo declarado de uma ação decorada não vale.** Não há como saber qual decorador substitui, e diante de duas respostas ele cala.", "**`xs[-1]` continua livre** — tratar todo negativo como fora do alcance acusaria a forma normal de pegar o último item."]},
  {"h2": "Silenciar uma regra, de propósito"},
  { code: `cores := ["azul", "verde"]

// A regra tem de ser NOMEADA: um 'permitir' solto esconderia o erro
// seguinte, que ninguem pediu para esconder.
match cores:
    point c:                        // df: permitir point-inalcancavel
        out $"casou com {len(c)} cores"

out "a regra vale na linha, ou na de cima"
`, lang: 'df' },
  {"cards": [{"href": "/docs/tipos", "title": "O sistema de tipos", "desc": "o guia inteiro"}, {"href": "/docs/faq/typescript", "title": "Comparação com TypeScript", "desc": "o que cada um confere"}, {"href": "/docs/erros", "title": "Códigos de erro", "desc": "o catálogo"}]},
];

const headings = [{ id: 'anotar-e-opcional-conferir-nao-e', text: "Anotar é opcional; conferir não é", level: 2 as const }, { id: 'type-uma-declaracao-seis-formas', text: "`type`: uma declaração, seis formas", level: 2 as const }, { id: 't-solto-nao-e-conferido-t-extends-x-e', text: "`<T>` solto não é conferido; `<T extends X>` é", level: 2 as const }, { id: 'o-que-o-check-prova-a-partir-de-um-literal', text: "O que o `check` prova a partir de um literal", level: 2 as const }, { id: 'e-o-que-ele-cala-de-proposito', text: "E o que ele cala, de propósito", level: 2 as const }, { id: 'silenciar-uma-regra-de-proposito', text: "Silenciar uma regra, de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Tipos: o que é conferido, e quando"}
      description={"Anotar é opcional, e o que muda quando você anota. União, refinamento, opaco, genéricos — e onde o analisador cala de propósito."}
      href={"/docs/faq/tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
