import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Máquina de estados",
  description: "Um enum, uma tabela de transições e nenhum estado inválido representável.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `118_maquina_estados.df`, que roda e verifica a si mesmo."},
  { code: `steady TRANSICOES := {
    "novo": ["pago", "cancelado"],
    "pago": ["enviado", "reembolsado"],
    "enviado": ["entregue"],
    "entregue": [],
    "cancelado": [],
    "reembolsado": []
}

blueprint Pedido:
    action setup():
        self.estado := "novo"
        self.historico := ["novo"]

    action mover(destino):
        permitidos := TRANSICOES[self.estado]
        given not permitidos.contains(destino):
            trigger "transicao invalida: " + self.estado + " -> " + destino
        self.estado := destino
        self.historico.append(destino)
        yield destino

p := spawn Pedido()
p.mover("pago")
p.mover("enviado")
p.mover("entregue")
out p.historico

assert p.estado is "entregue", "estado final"
assert p.historico is ["novo", "pago", "enviado", "entregue"], "historico"

invalida := no
monitor:
    p.mover("pago")
handle e:
    invalida := yes
    out "bloqueado:", e
assert invalida is yes, "transicao invalida bloqueada"`, title: `118_maquina_estados.df` },
  {"h2": "As três partes"},
  {"list": ["O **enum** enumera os estados possíveis", "A **tabela** declara quais saltos são legítimos", "As **ações** só consultam a tabela"]},
  {"p": "Nenhum estado inválido é representável, e nenhuma transição inválida é possível. Um estado com lista vazia é terminal — o laço para sozinho."},
  {"h2": "Por que não usar texto"},
  {"p": "Com `\"publicado\"` como texto solto, um erro de digitação vira um `no` silencioso. Com [enum](/fundamentos/enums), é erro na hora — e o `check` acha antes de rodar."},
];

const headings = [{ id: 'as-tres-partes', text: "As três partes", level: 2 as const }, { id: 'por-que-nao-usar-texto', text: "Por que não usar texto", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Máquina de estados"}
      description={"Um enum, uma tabela de transições e nenhum estado inválido representável."}
      href={"/receitas/maquina-de-estados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
