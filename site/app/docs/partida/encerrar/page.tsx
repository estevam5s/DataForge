// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Encerrar em ordem",
  description: "SIGTERM, SIGINT e SIGHUP rodam os finalizadores ao contrário, e o processo sai com 128 + sinal.",
};

const blocos: Bloco[] = [
  {"p": "O `docker stop`, o Kubernetes e o `systemctl stop` pedem para o processo terminar mandando **SIGTERM**. Um programa que não trata o sinal morre na hora: a transação no meio não confirma, o arquivo não fecha, a mensagem pega da fila não é devolvida. `Inicio.ao_encerrar` registra o que precisa rodar antes de sair."},
  { code: `adopt Arcane.Inicio as Inicio

log := []
Inicio.ao_encerrar(lambda => log.append("banco fechado"))
Inicio.ao_encerrar(lambda => log.append("fila devolvida"))

// o laço de trabalho confere a cada volta
atendidos := 0
persist not Inicio.encerrando() and atendidos smaller 3:
    atendidos += 1
assert atendidos is 3`, lang: 'df' },
  {"h2": "O que acontece no sinal"},
  {"table": {"head": ["Passo", "Por quê"], "rows": [["`encerrando()` passa a `yes`", "um laço que confere para por conta própria, no fim da volta — sem cortar um pedido no meio"], ["os finalizadores rodam **ao contrário** do registro", "quem abriu por último fecha primeiro, como uma pilha de `defer`: a fila, que usa o banco, fecha antes dele"], ["um finalizador que falha não impede os outros", "fechar o banco não pode depender de o log ter fechado"], ["sai com `128 + sinal` — 143 para SIGTERM", "o código que o orquestrador espera de uma saída por sinal"], ["um **segundo** sinal sai na hora", "quem aperta Ctrl+C duas vezes não quer esperar"]]}},
  {"p": "O fim normal do programa também roda os finalizadores, uma vez só — registrar para o sinal e esquecer do fim comum era o defeito de metade dos `atexit` escritos à mão."},
  {"callout": {"tipo": "atencao", "titulo": "Registre no topo, antes das threads", "texto": "O Python só entrega sinal à thread principal. O registro é feito lá — o interpretador, que roda o programa numa thread própria, repassa o pedido —, mas um `ao_encerrar` chamado de dentro de uma `thread:` é recusado com a explicação."}},
  {"callout": {"tipo": "dica", "titulo": "O prazo é curto", "texto": "O `docker stop` espera **10 segundos** antes de matar com SIGKILL, que não se trata. O Kubernetes, 30. Finalizador que faz rede precisa de prazo próprio, menor que esse."}},
];

const headings = [{ id: 'o-que-acontece-no-sinal', text: "O que acontece no sinal", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Encerrar em ordem"}
      description={"SIGTERM, SIGINT e SIGHUP rodam os finalizadores ao contrário, e o processo sai com 128 + sinal."}
      href={"/docs/partida/encerrar"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
