// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Relay — o que sai do módulo",
  description: "Declarar o que é público muda o que o analisador consegue provar sobre quem usa o módulo.",
};

const blocos: Bloco[] = [
  {"p": "Sem `relay`, tudo que o arquivo declara no topo é visível de fora. Com `relay`, só o que está listado — e essa escolha tem uma consequência que quase ninguém espera."},
  { code: `// biblioteca.df
action _normalizar(texto):
    yield texto.strip().lower()

action buscar(termo):
    yield $"procurando '{_normalizar(termo)}'"

record Resultado:
    titulo: String
    peso: Integer

// So estes dois saem. '_normalizar' fica dentro.
relay buscar, Resultado

out buscar("  Café  ")
assert Resultado("x", 1).peso is 1`, lang: 'df' },
  {"h2": "O que o `relay` muda no analisador"},
  {"p": "A superfície de um módulo é lida **sem executá-lo**, e é ela que permite ao `check` acusar `P.naoExiste()` antes de rodar. Quando há `relay`, a superfície é exatamente a lista; quando não há, é tudo o que o topo declara."},
  {"table": {"head": ["Com `relay`", "Sem `relay`"], "rows": [["a superfície é a lista", "a superfície é tudo do topo"], ["mudar um auxiliar não quebra ninguém", "qualquer nome do topo virou contrato"], ["`P.auxiliar()` é **acusado** pelo `check`", "passa"], ["o `abi` compara só o que é público", "compara tudo, e todo *rename* vira quebra"]]}},
  {"callout": {"tipo": "dica", "titulo": "A superfície é conservadora de propósito", "texto": "Ela **cala** — e o `check` volta a não acusar nada — quando o outro arquivo não compila, quando há ciclo de import, quando a profundidade (4) acaba, ou quando o `relay` nomeia algo que só existe em execução. Um falso alarme entre arquivos é pior que um silêncio: ele aparece no caminho mais comum de um projeto modular, e a reação é desligar a verificação inteira."}},
  {"h2": "O que atravessa a fronteira"},
  {"p": "O `check` não confere só o **nome**: ele leva o tipo de retorno e os tipos dos parâmetros. Num sistema de duzentos arquivos a maioria das chamadas atravessa módulo, e era exatamente ali que a conferência calava."},
  { code: `// pedidos.df
//   action criar(id: Integer, cliente: String) -> Pedido: …
//   relay criar, Pedido
//
// main.df
//   adopt ./pedidos as P
//
//   P.criar(1, 2, 3)          // check: aridade
//   P.criar("um", "Ana")      // check: o parametro 'id' e Integer
//   P.criar(1, "Ana").clientte  // check: o campo, com sugestao
//
// O tipo de retorno e TRADUZIDO para o vocabulario de quem chama:
// '-> Pedido' la e 'P.Pedido' aqui. Devolver o nome nu faria o
// analisador procurar um record que este arquivo nao declara — e
// acusar codigo certo, que e o jeito mais rapido de alguem desligar
// a verificacao.

out "o check atravessa arquivos"`, lang: 'df' },
  {"p": "Continue em [A superfície de um módulo](/docs/modulos/superficie) e [Compatibilidade](/docs/abi/compatibilidade)."},
];

const headings = [{ id: 'o-que-o-relay-muda-no-analisador', text: "O que o `relay` muda no analisador", level: 2 as const }, { id: 'o-que-atravessa-a-fronteira', text: "O que atravessa a fronteira", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Relay — o que sai do módulo"}
      description={"Declarar o que é público muda o que o analisador consegue provar sobre quem usa o módulo."}
      href={"/docs/modulos/relay"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
