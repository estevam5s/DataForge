// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Código de saída",
  description: "0 deu certo, 1 deu errado, 2 foi chamado errado, 128 + N morreu por sinal — e quem lê cada um.",
};

const blocos: Bloco[] = [
  {"p": "O código de saída é a única coisa que um processo diz ao programa que o chamou sem que alguém leia a saída. O CI decide por ele, o shell decide por ele (`&&`), o orquestrador decide por ele se reinicia."},
  {"table": {"head": ["Código", "Quer dizer", "Quem produz"], "rows": [["0", "deu certo", "o fim normal do programa"], ["1", "rodou e deu errado", "um erro não tratado"], ["2", "foi chamado errado", "`Cli.comando` com argumento inválido; `dataforge abi` com quebra"], ["128 + N", "morreu pelo sinal N", "143 = SIGTERM, 130 = SIGINT (Ctrl+C)"], ["qualquer outro", "o que você decidir", "`OS.exit(n)`"]]}},
  { code: `adopt Arcane.OS as OS

action conferir(entrada):
    given len(entrada) is 0:
        out "nada a processar"
        OS.exit(0)                     // não é erro: só não havia o que fazer
    yield len(entrada)

assert conferir([1, 2, 3]) is 3`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Nunca sair com 0 depois de um erro", "texto": "Um script que imprime \"erro!\" e sai com 0 faz o CI passar verde com o trabalho pela metade. É o defeito que o `parallel` tinha — o erro de uma tarefa era impresso, e o programa saía com 0. Erro não tratado sai com 1 sozinho; ao tratar, decida o código de propósito."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Código de saída"}
      description={"0 deu certo, 1 deu errado, 2 foi chamado errado, 128 + N morreu por sinal — e quem lê cada um."}
      href={"/docs/partida/codigos-de-saida"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
