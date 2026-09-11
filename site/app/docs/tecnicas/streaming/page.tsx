// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/fluxo.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Streaming",
  description: "Tópicos, partições e offsets — um log em disco, com a semântica do Kafka.",
};

const blocos: Bloco[] = [
  { code: `adopt Arcane.Stream as S

corrente := S.corrente("eventos/")
S.topico(corrente, "pedidos", 4)

S.publicar(corrente, "pedidos", {"id": 1, "valor": 90}, "cliente-7")

cycle e in S.consumir(corrente, "pedidos", "faturamento"):
    processar(e["valor"])
    S.confirmar(corrente, "pedidos", "faturamento", e)`, lang: 'df' },
  {"p": "Kafka é um cluster: réplicas, eleição de líder, coordenação entre máquinas. `Arcane.Stream` é um **log em arquivo** com a mesma semântica de tópico, partição e offset — o que cabe num processo, e que é onde a maioria dos fluxos de verdade começa."},
  {"h2": "Um log, não uma fila"},
  {"p": "É a diferença que define o módulo. A fila **entrega e esquece**; o log **guarda**, e cada consumidor lembra onde parou."},
  { code: `faturamento := S.consumir(corrente, "pedidos", "faturamento")   // 12
auditoria   := S.consumir(corrente, "pedidos", "auditoria")     // 12

S.confirmar_ate(corrente, "pedidos", "faturamento", faturamento)

S.consumir(corrente, "pedidos", "faturamento")   // 0  — já processou
S.consumir(corrente, "pedidos", "auditoria")     // 12 — não mexeu`, lang: 'df' },
  {"p": "Dois grupos leem o **mesmo** evento sem disputar. Numa fila, o primeiro a ler tira o evento do outro."},
  {"callout": {"tipo": "atencao", "titulo": "`consumir` não avança sozinho", "texto": "Quem avança é `confirmar`, **depois** de processar. Avançar na leitura daria *no máximo uma vez*: um processo que cai no meio perderia o evento em silêncio — o pior resultado possível num fluxo de dados. A garantia aqui é *ao menos uma vez*, e é a honesta."}},
  {"h2": "A partição é a unidade de ordem"},
  { code: `S.publicar(corrente, "pedidos", evento, "cliente-7")`, lang: 'df' },
  {"p": "Eventos com a **mesma chave** caem sempre na mesma partição, e ali a ordem é garantida — os três eventos do cliente 7 chegam na ordem em que aconteceram."},
  {"p": "Entre partições não há ordem, e é justamente isso que permite processar quatro em paralelo. Quem quer ordem total usa uma partição só, e paga com a serialização."},
  {"callout": {"tipo": "nota", "titulo": "A partição é estável entre execuções", "texto": "O `hash()` do Python é aleatorizado por processo desde a 3.3. Usá-lo mandaria a mesma chave para partições diferentes a cada execução, e a única garantia que a partição dá — a ordem por chave — deixaria de existir. Aqui é SHA-256."}},
  {"h2": "Voltar e reprocessar"},
  { code: `S.voltar(corrente, "pedidos", "faturamento", 0)`, lang: 'df' },
  {"p": "É o que uma fila **não permite**, e o motivo de o log guardar o evento depois de entregue: quando a regra de processamento estava errada — e vai estar — dá para rodar tudo de novo."},
  {"h2": "O atraso é a métrica que se vigia"},
  { code: `S.atraso(corrente, "pedidos", "faturamento")
// {"total": 40213, "por_particao": {"p0": 12000, "p1": 9800, …}}`, lang: 'df' },
  {"p": "Um atraso que só cresce significa que a produção passou o consumo — e o momento de agir é **antes** de o disco encher, não depois."},
  {"h2": "Retenção"},
  { code: `S.reter(corrente, "pedidos", 10)     // guarda os 10 últimos segmentos`, lang: 'df' },
  {"p": "Um log que só cresce enche o disco. A retenção apaga por **segmento**, não por evento: apagar o meio de um arquivo exigiria reescrevê-lo inteiro, e o offset dos que sobram mudaria — quebrando a posição de todo grupo."},
  {"h2": "Janelas"},
  { code: `cycle j in S.janela(eventos, 60):
    out $"{j["inicio"]}: {j["quantos"]} eventos"`, lang: 'df' },
  {"p": "É a operação que dá sentido a um fluxo: *quantos por minuto* é a pergunta que se faz, e ela não existe sem janela."},
  {"h2": "O que ele não faz"},
  {"list": ["**Sem réplica.** O log vive num disco só.", "**Sem transação entre tópicos.** Publicar em dois é duas operações.", "**Sem coordenação automática** entre consumidores de um mesmo grupo — cada processo lê as partições que você mandar.", "**A garantia é *ao menos uma vez*.** Um processo que cai entre processar e confirmar reprocessa o evento; *exatamente uma vez* exige transação de ponta a ponta, e ninguém a tem de graça."]},
];

const headings = [{ id: 'um-log-nao-uma-fila', text: "Um log, não uma fila", level: 2 as const }, { id: 'a-particao-e-a-unidade-de-ordem', text: "A partição é a unidade de ordem", level: 2 as const }, { id: 'voltar-e-reprocessar', text: "Voltar e reprocessar", level: 2 as const }, { id: 'o-atraso-e-a-metrica-que-se-vigia', text: "O atraso é a métrica que se vigia", level: 2 as const }, { id: 'retencao', text: "Retenção", level: 2 as const }, { id: 'janelas', text: "Janelas", level: 2 as const }, { id: 'o-que-ele-nao-faz', text: "O que ele não faz", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Streaming"}
      description={"Tópicos, partições e offsets — um log em disco, com a semântica do Kafka."}
      href={"/docs/tecnicas/streaming"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
