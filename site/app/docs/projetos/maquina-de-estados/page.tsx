// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fluxo de pedido",
  description: "Uma máquina de estados explícita, que recusa a transição impossível e guarda o histórico.",
};

const blocos: Bloco[] = [
  {"p": "Um pedido tem estados, e os bugs caros moram nas transições: o pedido cancelado que é despachado, o pago que volta a aguardar pagamento. Com o estado num texto livre, nada impede isso. Com uma tabela de transições, a transição impossível é **recusada** — e o histórico diz quem mudou o quê."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["enum", "os estados possíveis — e só eles"], ["tabela de transições", "de onde se pode ir para onde"], ["histórico", "cada mudança com quem e quando"], ["`match` exaustivo", "o `check` avisa do estado esquecido"]]}},
  {"h2": "Estrutura"},
  { code: `pedidos/
  src/
    estados.df     o enum e a tabela
    pedido.df      transicionar, historico
  tests/
    fluxo_test.df   um trial por transicao PROIBIDA`, lang: 'text' },
  { code: `[project]
name = "pedidos"
version = "0.1.0"
description = "Fluxo de pedidos"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `enum Estado:
    Criado
    Pago
    Separado
    Enviado
    Entregue
    Cancelado

TRANSICOES := {
    "Criado": ["Pago", "Cancelado"],
    "Pago": ["Separado", "Cancelado"],
    "Separado": ["Enviado"],
    "Enviado": ["Entregue"],
    "Entregue": [],
    "Cancelado": []
}

blueprint Pedido(id):
    estado := Estado.Criado
    historico: Cluster := []

    action mover(para, quem):
        permitidos := TRANSICOES[self.estado.name]
        given para.name not in permitidos:
            trigger $"pedido {self.id}: '{self.estado.name}' nao vai para '{para.name}'. Pode ir para: {permitidos}"
        self.historico.append({"de": self.estado.name, "para": para.name, "quem": quem})
        self.estado := para

    action terminal():
        yield len(TRANSICOES[self.estado.name]) is 0

p := spawn Pedido(42)
p.mover(Estado.Pago, "gateway")
p.mover(Estado.Separado, "ana")
p.mover(Estado.Enviado, "transportadora")

monitor:
    p.mover(Estado.Cancelado, "cliente")
    assert no
handle Error as e:
    out e.message

p.mover(Estado.Entregue, "transportadora")
assert p.terminal()
assert len(p.historico) is 4
assert p.historico[0]["quem"] is "gateway"`, lang: 'df', title: `src/pedido.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/pedido as P

crucible "transicoes proibidas":
    trial "cancelado nao e enviado":
        p := spawn P.Pedido(1)
        p.mover(P.Estado.Cancelado, "x")
        expect(lambda => p.mover(P.Estado.Enviado, "x")).to_raise()`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["o estado é um `enum`", "`\"Pagu\"` é aceito e o pedido some de todo relatório"], ["a tabela fica num lugar só", "a regra *“cancelado não volta”* está escrita em cinco rotas, e uma esquece"], ["a mensagem lista para onde **pode** ir", "quem integra descobre as transições por tentativa e erro"], ["o histórico nasce com a transição", "o cliente pergunta quem cancelou, e ninguém sabe"]]}},
  {"h2": "Para ir além"},
  {"list": ["A máquina genérica da biblioteca: `Padroes.maquina` — [Arcane.Padroes](/docs/biblioteca/padroes).", "Transição que dispara evento de domínio: [Arcane.Dominio](/docs/biblioteca/dominio).", "Receita: [Máquina de estados](/docs/receitas/maquina-de-estados)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fluxo de pedido"}
      description={"Uma máquina de estados explícita, que recusa a transição impossível e guarda o histórico."}
      href={"/docs/projetos/maquina-de-estados"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
