// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/posse_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um pool de recursos",
  description: "O caso que junta tudo: emprestar, devolver, e o que acontece quando ninguém devolve.",
};

const blocos: Bloco[] = [
  {"p": "Um pool é o exemplo canônico de posse: o recurso **pertence** ao pool, quem usa **empresta**, e devolver não é opcional — um empréstimo que não volta é uma conexão a menos, para sempre."},
  { code: `adopt Arcane.Posse as Posse

blueprint Pool:
    action setup(quantas):
        self.livres := []
        self.emprestadas := 0
        self.criadas := 0
        cycle i from 1 to quantas:
            self.criadas := self.criadas + 1
            self.livres.append({"id": self.criadas})

    action com(acao):
        given len(self.livres) is 0:
            trigger "o pool acabou — todas as conexões estão emprestadas"
        conexao := self.livres.pop(len(self.livres) - 1)
        self.emprestadas := self.emprestadas + 1
        // O 'defer' é o que torna a devolução impossível de esquecer:
        // ele roda mesmo quando a ação falha no meio.
        defer:
            self.livres.append(conexao)
            self.emprestadas := self.emprestadas - 1
        yield acao(conexao)

p := spawn Pool(2)
assert p.com(lambda c => c["id"]) is 2
assert len(p.livres) is 2          // devolvida

// E mesmo quando o corpo falha:
monitor:
    p.com(lambda c => 1 / 0)
handle Error:
    out "a ação falhou"
assert len(p.livres) is 2
assert p.emprestadas is 0
out "devolvida mesmo com erro"`, lang: 'df' },
  {"h2": "O que acontece quando o pool acaba"},
  { code: `adopt Arcane.Posse as Posse

blueprint Pool:
    action setup(quantas):
        self.livres := [{"id": i} cycle i in range(1, quantas + 1)]

    action pegar():
        given len(self.livres) is 0:
            // Falhar RÁPIDO é melhor que esperar para sempre: uma
            // espera sem prazo vira um travamento sem mensagem, e
            // ninguém consegue distinguir isso de rede lenta.
            trigger "pool esgotado: aumente o tamanho ou reduza o tempo de uso"
        yield self.livres.pop(0)

p := spawn Pool(1)
primeira := p.pegar()

monitor:
    p.pegar()
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"h2": "As quatro decisões de um pool"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["devolver no `defer`", "uma falha no meio come uma conexão por vez, até o pool acabar"], ["falhar quando esgota, com prazo", "espera infinita — e um travamento sem mensagem"], ["um **teto**, e não crescer sem limite", "o pool vira um jeito elaborado de abrir conexão demais no banco"], ["conferir a conexão ao devolver", "uma conexão morta volta para o pool e quebra o próximo"]]}},
  {"h2": "E o pool de processos, que já existe"},
  {"p": "Para trabalho de CPU, a linguagem já traz um: `P.pool_processos()` paga a partida **uma vez** — medido, 180 ms na primeira chamada e 82 ms na segunda. O `fechar()` é explícito porque o contrário deixa processos ociosos vivos."},
  { code: `adopt Arcane.Concurrent as C

pool := C.pool_processos()
defer:
    pool.fechar()

assert pool is not void
out "o pool sobrevive entre chamadas — e o fechar é explícito"`, lang: 'df' },
];

const headings = [{ id: 'o-que-acontece-quando-o-pool-acaba', text: "O que acontece quando o pool acaba", level: 2 as const }, { id: 'as-quatro-decisoes-de-um-pool', text: "As quatro decisões de um pool", level: 2 as const }, { id: 'e-o-pool-de-processos-que-ja-existe', text: "E o pool de processos, que já existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Um pool de recursos"}
      description={"O caso que junta tudo: emprestar, devolver, e o que acontece quando ninguém devolve."}
      href={"/docs/memoria/posse/pool"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
