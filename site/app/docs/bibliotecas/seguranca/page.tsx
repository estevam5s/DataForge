// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A biblioteca como superfície",
  description: "O que um pacote pode fazer na máquina de quem instala — e as cinco guardas que reduzem isso.",
};

const blocos: Bloco[] = [
  {"p": "Uma biblioteca roda com **toda a autoridade** do programa que a adotou: o disco, a rede, as variáveis de ambiente. Quem a publica assume isso."},
  {"h2": "As cinco guardas"},
  {"table": {"head": ["Guarda", "O ataque que ela corta"], "rows": [["o `sha256` no lock", "o tarball trocado numa versão já publicada"], ["a extração que recusa `../` e link simbólico", "*Zip Slip*: escrever fora da pasta do pacote"], ["o tarball reprodutível", "um sha256 que muda sozinho e não significa nada"], ["`relay` explícito", "o auxiliar interno virar contrato por acidente"], ["zero dependência transitiva escondida", "cada dependência nova é uma decisão visível no `forge.toml`"]]}},
  {"h2": "O que a sua biblioteca não deve fazer"},
  {"table": {"head": ["Não", "Porque"], "rows": [["ler variável de ambiente por conta própria", "o segredo do usuário vira seu, e ele não escolheu isso"], ["escrever fora da pasta que recebeu", "`~/.config` de quem instalou não é seu"], ["abrir rede na importação", "um `adopt` não pode ter efeito; e o CI de outra pessoa quebra sem rede"], ["registrar telemetria calada", "é o que faz uma biblioteca ser removida de uma empresa inteira"], ["embutir uma chave, mesmo de teste", "ela vira exemplo, e o exemplo vira produção"]]}},
  {"h2": "A varredura de segredo"},
  { code: `adopt Arcane.Seguranca as S

achados := S.procurar_segredos("token := \\"ghp_\\" + gerar()")
out $"{len(achados)} achado(s)"

// Numa biblioteca, a varredura roda no CI antes do 'pack'.
// Ela e conservadora de proposito: um falso alarme num repositorio
// que fala SOBRE seguranca ensina a ignorar a varredura inteira —
// e foi o que aconteceu aqui, com 19 falsos positivos no proprio
// material didatico antes de a lista de excecoes existir.

assert typeof(achados) is "Cluster"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "A capacidade limita o `adopt`, e não o que foi entregue", "texto": "`Arcane.Capacidade` recusa o `adopt` de um módulo fora da lista, pelo nome da capacidade que falta. Ela **não tira o que já foi passado** — e isso é o modelo, não uma limitação: numa linguagem de capacidade, poder é o que se **passa**, não o que está no ar. Um módulo que prometesse contenção total seria usado onde não pode, e a descoberta viria por incidente."}},
  {"p": "Continue em [Segurança da informação](/docs/seguranca) e [Capacidade](/docs/seguranca/capacidade)."},
];

const headings = [{ id: 'as-cinco-guardas', text: "As cinco guardas", level: 2 as const }, { id: 'o-que-a-sua-biblioteca-nao-deve-fazer', text: "O que a sua biblioteca não deve fazer", level: 2 as const }, { id: 'a-varredura-de-segredo', text: "A varredura de segredo", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A biblioteca como superfície"}
      description={"O que um pacote pode fazer na máquina de quem instala — e as cinco guardas que reduzem isso."}
      href={"/docs/bibliotecas/seguranca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
