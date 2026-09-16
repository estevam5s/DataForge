// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/modulos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A superfície de um módulo",
  description: "Como o analisador lê o que outro arquivo oferece, sem executá-lo — e quando ele prefere calar.",
};

const blocos: Bloco[] = [
  {"p": "`P.naoExiste()` e `P.criar(1, 2, 3)` são acusados **antes de rodar**, mesmo quando `P` vem de outro arquivo. É a checagem que mais importa em sistema grande: num arquivo de 40 linhas o erro aparece na primeira execução; num de 200 arquivos, a maioria das chamadas cruza módulo, e todas elas eram invisíveis."},
  {"h2": "Como ele sabe, sem executar"},
  {"p": "`superficie.py` lê o outro arquivo com o **lexer e o parser**, e não com o interpretador. Do que encontra, guarda o que atravessa a fronteira:"},
  {"table": {"head": ["Guarda", "Para conferir"], "rows": [["os nomes exportados", "`P.naoExiste` — o membro que não existe"], ["a aridade de cada ação", "`P.criar(1, 2, 3)` com dois parâmetros"], ["o tipo de cada parâmetro", "`D.valor_de(texto)` onde se espera `Integer`"], ["o tipo de retorno", "`P.criar(…).clientte` — o campo errado, do outro lado"], ["os campos de cada record", "o mesmo, um nível adiante"]]}},
  {"p": "**O tipo de retorno atravessar é o que mais rende.** Sem ele, uma ação que declara `-> Pedido` virava um valor sem tipo no outro arquivo, e o campo com nome quase certo passava no `check`."},
  {"h2": "A tradução de vocabulário"},
  {"p": "O `-> Pedido` declarado lá é `P.Pedido` aqui. Devolver o nome nu faria o analisador procurar um record que este arquivo não declara — e a primeira versão fazia isso, acusando **o código certo**:"},
  { code: `Parameter 'p' of 'P.com_total' expects Pedido but got P.Pedido
`, lang: 'text' },
  {"p": "Um falso alarme no caminho mais comum de um projeto modular ensina a desligar a verificação inteira. Hoje a tradução acontece nos dois lados, e quando não dá para concluir o analisador **cala**."},
  {"h2": "Quando ele cala"},
  {"table": {"head": ["Cala quando", "Porque"], "rows": [["o outro arquivo não compila", "uma superfície lida de código quebrado é palpite"], ["há ciclo de import", "não há ordem em que a leitura termine"], ["a profundidade (4) acaba", "seguir a cadeia inteira levaria o `check` a minutos"], ["o `relay` nomeia algo que só existe em execução", "o nome pode ser qualquer coisa"], ["o módulo não exporta aquele tipo", "o tipo é interno, e o nome daqui não o alcança"]]}},
  {"p": "Em todos esses casos a superfície devolve **aberta**, e a conferência volta a ficar em silêncio. Um falso alarme é pior que um silêncio."},
  {"h2": "O escopo de quem chama"},
  {"p": "A inferência usa o escopo de **quem chama**, e não o global. Parece detalhe e não é: `D.valor_de(n)` dentro de `action f(n)` virou **\"Undefined name 'n'\"** — 649 falsos alarmes num projeto gerado de 252 arquivos, um por uso de parâmetro numa chamada entre módulos."},
  {"p": "E a suíte passava: os primeiros testes chamavam no nível de topo, onde o escopo global é o certo. O bug só aparecia dentro de uma ação, que é onde quase todo código vive. Quem pegou foi rodar o `check` no projeto grande."},
  {"h2": "O cache"},
  {"p": "A superfície é guardada por `(caminho, mtime)`. Sem isso, 200 arquivos importando três vizinhos cada levariam o `check` de 0,7 s a mais de um minuto — e um analisador que demora um minuto não roda a cada salvar, que é quando ele vale."},
  {"h2": "Por onde seguir"},
  {"cards": [{"href": "/docs/tecnicas/analise-estatica", "title": "Análise estática", "desc": "tudo o que o check prova, e o que o faz calar"}, {"href": "/docs/bibliotecas/contrato", "title": "O contrato de uma biblioteca", "desc": "o que o relay promete, e o que quebra quem depende de você"}]},
];

const headings = [{ id: 'como-ele-sabe-sem-executar', text: "Como ele sabe, sem executar", level: 2 as const }, { id: 'a-traducao-de-vocabulario', text: "A tradução de vocabulário", level: 2 as const }, { id: 'quando-ele-cala', text: "Quando ele cala", level: 2 as const }, { id: 'o-escopo-de-quem-chama', text: "O escopo de quem chama", level: 2 as const }, { id: 'o-cache', text: "O cache", level: 2 as const }, { id: 'por-onde-seguir', text: "Por onde seguir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A superfície de um módulo"}
      description={"Como o analisador lê o que outro arquivo oferece, sem executá-lo — e quando ele prefere calar."}
      href={"/docs/modulos/superficie"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
