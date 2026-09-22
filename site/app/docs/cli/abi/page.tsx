// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "dataforge abi e alvo",
  description: "A nova versão quebra a anterior? E este programa roda no navegador, no WASI, numa função?",
};

const blocos: Bloco[] = [
  {"p": "Duas perguntas que se fazem antes de publicar, e que costumam ser respondidas a olho."},
  {"h2": "abi — o que muda para quem depende"},
  { code: `dataforge abi v1/lib.df v2/lib.df         # o que mudou, e que bump exige
dataforge abi v1/lib.df v2/lib.df --json  # para o CI
dataforge abi v1/lib.df v2/lib.df --estrito`, lang: 'bash' },
  {"table": {"head": ["Veredito", "Significa", "Código de saída"], "rows": [["`maior`", "alguma coisa quebrou", "1 — reprova o CI"], ["`menor`", "só acréscimos compatíveis", "0"], ["`correcao`", "a superfície não mudou", "0"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Renomear parâmetro é quebra", "texto": "A chamada com nome existe nesta linguagem (`somar(a := 1)`), então o nome do parâmetro é contrato, e não só a posição. Uma ferramenta feita para C não teria essa regra."}},
  {"h2": "alvo — onde o programa roda"},
  { code: `dataforge alvo app.df                  # a tabela de todos
dataforge alvo app.df --alvo=navegador # um so; sai com 1 se nao roda`, lang: 'bash' },
  {"p": "Ela lê os `adopt` e cruza com o que cada ambiente suporta: servidor, CLI, navegador (CPython em WebAssembly), WASI, função serverless e embarcado. A leitura é **estática e de um arquivo** — um `roda` quer dizer *“não achei impedimento por esta via”*."},
  {"p": "Continue em [Compatibilidade](/docs/abi/compatibilidade) e [Portabilidade](/docs/alvos/portabilidade)."},
];

const headings = [{ id: 'abi-o-que-muda-para-quem-depende', text: "abi — o que muda para quem depende", level: 2 as const }, { id: 'alvo-onde-o-programa-roda', text: "alvo — onde o programa roda", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"dataforge abi e alvo"}
      description={"A nova versão quebra a anterior? E este programa roda no navegador, no WASI, numa função?"}
      href={"/docs/cli/abi"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
