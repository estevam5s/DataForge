import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Palavras reservadas",
  description: "As 81 palavras que a linguagem reserva, agrupadas por tema.",
};

const blocos: Bloco[] = [
  {"p": "DataForge reserva **81 palavras**. Usar uma delas como nome produz um `ParseError` explicando qual é a palavra e sugerindo outro nome."},
  {"h2": "Por tema"},
  {"table": {"head": ["Tema", "Palavras"], "rows": [["Fundação", "`steady` `shadow` `static` `out` `emit` `in` `typeof` `cast` `void` `yes` `no`"], ["Condicionais", "`given` `orif` `otherwise` `match` `point` `default` `when`"], ["Laços", "`cycle` `persist` `perform` `halt` `skip` `from` `to` `step`"], ["Ações", "`action` `yield` `lambda` `mark` `defer` `async` `await` `stream`"], ["Tipos", "`blueprint` `record` `enum` `trait` `spawn` `forge` `self` `root` `extends` `with`"], ["Módulos", "`adopt` `relay` `as` `using`"], ["Erros", "`monitor` `handle` `ensure` `trigger` `retry` `recover` `guard` `propagate` `validate` `assert`"], ["Concorrência", "`thread` `channel` `parallel` `observe` `pulse` `wait`"], ["Pipelines", "`sift` `morph` `distill`"], ["Comparação e lógica", "`is` `isnt` `bigger` `smaller` `bigger_eq` `smaller_eq` `and` `or` `not`"], ["Dados", "`frame` `train` `predict`"], ["Outras", "`delete` `inspect`"]]}},
  {"h2": "Em ordem alfabética"},
  { code: `action      adopt       and         as          assert      async       await
bigger      bigger_eq   blueprint   cast        channel     cycle       default
defer       delete      distill     emit        ensure      enum        extends
forge       frame       from        given       guard       halt        handle
in          inspect     is          isnt        lambda      mark        match
monitor     morph       no          not         observe     or          orif
otherwise   out         parallel    perform     persist     point       predict
propagate   pulse       record      recover     relay       retry       root
self        shadow      sift        skip        smaller     smaller_eq  spawn
static      steady      step        stream      thread      to          train
trait       trigger     typeof      using       validate    void        wait
when        with        yes         yield`, lang: 'text' },
  {"h2": "O que NÃO é reservado"},
  {"p": "`cluster`, `vault` e `range` **são funções embutidas**, não palavras reservadas — podem ser usadas como nome e chamadas normalmente:"},
  { code: `out cluster(["a", "b"])      # converte para lista
out vault({"k": 1})
out range(1, 5)` },
  {"callout": {"tipo": "atencao", "titulo": "As que mais pegam em português", "texto": "`no` (o literal falso), `in`, `is`, `to`, `from`, `as`, `step`, `point`, `default`, `frame`, `stream`, `emit`, `forge`. Um `no := 1` é erro — use `nao` ou outro nome."}},
  {"h2": "A mensagem de erro"},
  { code: `ParseError [line 1, col 1]: 'no' is a reserved keyword and cannot be assigned to. Pick another name.`, lang: 'text' },
];

const headings = [{ id: 'por-tema', text: "Por tema", level: 2 as const }, { id: 'em-ordem-alfabetica', text: "Em ordem alfabética", level: 2 as const }, { id: 'o-que-nao-e-reservado', text: "O que NÃO é reservado", level: 2 as const }, { id: 'a-mensagem-de-erro', text: "A mensagem de erro", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Palavras reservadas"}
      description={"As 81 palavras que a linguagem reserva, agrupadas por tema."}
      href={"/docs/referencia/palavras-reservadas"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
