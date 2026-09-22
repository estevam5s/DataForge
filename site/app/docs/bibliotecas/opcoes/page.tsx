// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "O vault de opções",
  description: "Por que recusar a chave desconhecida — e não avisar sobre ela.",
};

const blocos: Bloco[] = [
  {"p": "Um vault de opções aceita qualquer chave. É isso que o torna conveniente, e é exatamente por isso que ele precisa de uma guarda."},
  {"callout": {"tipo": "atencao", "titulo": "O erro de digitação some, e o padrão vence", "texto": "`{\"tentativa\": 9}` — singular — deixava o cliente com as **3 tentativas** do padrão, e o 9 não chegava a lugar nenhum. Pior: `API.openapi(app, {\"title\": \"Loja\"})`, em inglês, como o próprio OpenAPI escreve o campo, saía com o título padrão — e quem escreve isso **publica um contrato com o nome errado** sem nada denunciar."}},
  {"h2": "Recusar, e não avisar"},
  {"p": "Um aviso impresso não para nada: o programa segue com o padrão, que é exatamente o estado que se queria evitar. E num servidor o aviso vai para um log que ninguém lê."},
  { code: `PADROES := {"tentativas": 3, "prazo": 30, "recuo": 0.5}

action ler_opcoes(recebidas, conhecidas, onde):
    resultado := {}
    cycle k in conhecidas.keys():
        resultado[k] := conhecidas[k]
    cycle k in recebidas.keys():
        given k.startswith("_"):
            skip
        given k not in conhecidas:
            nomes := ", ".join(sorted(conhecidas.keys()))
            trigger $"'{k}' nao e uma opcao de '{onde}'. Aceita: {nomes}"
        resultado[k] := recebidas[k]
    yield resultado

o := ler_opcoes({"prazo": 5}, PADROES, "cliente")
assert o["prazo"] is 5
assert o["tentativas"] is 3

monitor:
    ler_opcoes({"tentativa": 9}, PADROES, "cliente")
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"table": {"head": ["Decisão", "Porque"], "rows": [["a lista de conhecidas num lugar só", "ela **é** a documentação; duas cópias divergem"], ["a mensagem lista o que aceita", "quem errou o nome não tem como adivinhar o certo"], ["chave começando com `_` passa", "é a porta de escape para extensão e para teste"], ["o padrão é aplicado pelo chamador", "a validação e a mesclagem são perguntas diferentes"]]}},
  {"callout": {"tipo": "dica", "titulo": "Sugira o nome parecido", "texto": "O analisador da linguagem usa `difflib` para isso, e vale aqui: *“'tentativa' não é uma opção. Você quis dizer 'tentativas'?”* transforma um erro que custa uma hora num erro que custa cinco segundos. É a diferença entre uma mensagem que **descreve** e uma que **resolve**."}},
  {"p": "Continue em [Desenhar a API](/docs/bibliotecas/api) e [Os erros](/docs/bibliotecas/erros)."},
];

const headings = [{ id: 'recusar-e-nao-avisar', text: "Recusar, e não avisar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"O vault de opções"}
      description={"Por que recusar a chave desconhecida — e não avisar sobre ela."}
      href={"/docs/bibliotecas/opcoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
