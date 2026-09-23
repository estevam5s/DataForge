// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/faq.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Glossário: por que esta palavra",
  description: "O vocabulário inteiro, com a palavra que cada uma substitui — e o motivo de sete terem sido removidas.",
};

const blocos: Bloco[] = [
  {"p": "A objeção mais comum à linguagem é o vocabulário: *por que `given` e não `if`?* A resposta honesta é que a escolha foi deliberada e tem custo — e que o projeto já **removeu sete palavras reservadas** por serem caras sem entregar nada."},
  {"h2": "O mapa"},
  {"table": {"head": ["Onde você diria", "Aqui", "Nota"], "rows": [["`=`", "`:=`", "`=` sozinho não existe — `given x = 5` é erro de sintaxe, não um bug calado"], ["`const`", "`steady`", ""], ["`print`", "`out`", "aceita vários, separados por vírgula"], ["`if`/`elif`/`else`", "`given`/`orif`/`otherwise`", "o nome atribuído num ramo **existe depois** do bloco"], ["ternário", "`a given cond otherwise b`", "a mesma ordem do `if`"], ["`switch`", "`match` / `point` / `when` / `default`", "`when` é a guarda"], ["`for x in xs`", "`cycle x in xs`", "o corpo tem escopo próprio, de propósito"], ["`for i in range(1,6)`", "`cycle i from 1 to 5`", "**inclusivo nos dois extremos**"], ["`while`", "`persist`", ""], ["`do..while`", "`perform … persist`", ""], ["`break` / `continue`", "`halt` / `skip`", "atravessam `monitor`"], ["`def` / `return`", "`action` / `yield`", "`yield` **encerra** a ação"], ["gerador", "`stream action` / `emit`", "separados de propósito"], ["`class` / `new`", "`blueprint` / `spawn`", ""], ["`self` / `super`", "`self` / `root`", ""], ["`interface`", "`trait`", ""], ["`@dataclass(frozen=True)`", "`record`", "imutável, igualdade estrutural"], ["`import` / `export`", "`adopt` / `relay`", "`relay` é real, não convenção"], ["`try`/`catch`/`finally`", "`monitor`/`handle`/`ensure`", ""], ["`throw`", "`trigger`", "levanta `TriggerError`, **não** `RuntimeError`"], ["`true`/`false`/`null`", "`yes`/`no`/`void`", ""], ["`//` (divisão inteira)", "`~/`", "aqui `//` é comentário"], ["`filter`/`map`/`reduce`", "`>> sift`/`morph`/`distill`", "sintaxe, não função"]]}},
  {"h2": "As que mais pegam quem escreve em português"},
  {"p": "Estas são palavras reservadas, e por isso não podem ser nomes de variável: `no`, `in`, `is`, `to`, `from`, `as`, `step`, `point`, `default`, `frame`, `stream`, `emit`, `forge`, `record`, `enum`, `when`. Já `range`, `cluster` e `vault` **são funções**, e continuam livres."},
  {"callout": {"tipo": "nota", "titulo": "Trinta e duas palavras são contextuais, e nenhuma é reservada", "texto": "As onze do Kiln (`server`, `route`, `render`…), as seis do Quadro (`onde`, `agrupar`, `ordenar`…) e as treze de OOP (`readonly`, `final`…) só valem onde o que vem depois confirma. `route := \"/pedidos\"` continua sendo uma variável chamada `route`, e há um bloco na documentação que **demonstra** isso rodando."}},
  {"h2": "Por que sete foram removidas"},
  {"p": "Toda palavra em `KEYWORDS` deixa de poder ser identificador. Antes de acrescentar uma, o projeto confere se o parser realmente a consome:"},
  { code: `$ grep -c "TokenType.NOVA\\b" dataforge/parser.py   # precisa ser > 0`, lang: 'bash' },
  {"p": "Se for zero, ela só quebra código de usuário sem entregar nada. Foi o caso de sete — e o mesmo raciocínio recusou `covariant` e `contravariant`, que seriam palavras que não decidem nada: a conferência de variância já está certa sem declaração, e há teste registrando essa decisão."},
  {"cards": [{"href": "/docs/referencia/arquitetura", "title": "Referência", "desc": "a gramática e as palavras"}, {"href": "/docs/referencia/palavras-reservadas", "title": "As palavras", "desc": "um exemplo que roda para cada"}, {"href": "/docs/faq/python", "title": "Vindo do Python", "desc": "a tabela lado a lado"}]},
];

const headings = [{ id: 'o-mapa', text: "O mapa", level: 2 as const }, { id: 'as-que-mais-pegam-quem-escreve-em-portugues', text: "As que mais pegam quem escreve em português", level: 2 as const }, { id: 'por-que-sete-foram-removidas', text: "Por que sete foram removidas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Glossário: por que esta palavra"}
      description={"O vocabulário inteiro, com a palavra que cada uma substitui — e o motivo de sete terem sido removidas."}
      href={"/docs/faq/glossario"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
