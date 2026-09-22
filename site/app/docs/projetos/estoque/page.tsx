// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Controle de estoque",
  description: "Entrada, saída, reserva e o estoque mínimo — com a invariante que nunca deixa o saldo negativo.",
};

const blocos: Bloco[] = [
  {"p": "Estoque parece soma e subtração até a primeira venda de um item que não existe. A distinção que resolve é entre **disponível** e **físico**: o que está reservado para um pedido ainda está na prateleira, mas não pode ser vendido de novo. E a invariante *“disponível nunca é negativo”* é cobrada em toda operação, não em algumas."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["blueprint com invariante", "o saldo inconsistente é recusado na saída de cada método"], ["movimento como registro", "o saldo é a soma dos movimentos, e pode ser reconstruído"], ["reserva", "a diferença entre físico e disponível"], ["alerta de mínimo", "o ponto de pedido"]]}},
  {"h2": "Estrutura"},
  { code: `estoque/
  src/
    produto.df     saldo fisico, reservado, minimo
    movimento.df   entrada, saida, ajuste — imutaveis
    relatorio.df   o que repor
  tests/`, lang: 'text' },
  { code: `[project]
name = "estoque"
version = "0.1.0"
description = "Controle de estoque"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `record Movimento:
    tipo: String
    qtd: Integer
    motivo: String

blueprint Item(sku, minimo):
    fisico := 0
    reservado := 0
    movimentos: Cluster := []

    invariant self.fisico bigger_eq 0
    invariant self.reservado bigger_eq 0 and self.reservado smaller_eq self.fisico

    action disponivel():
        yield self.fisico - self.reservado

    action entrar(qtd, motivo):
        given qtd smaller_eq 0:
            trigger "entrada precisa ser positiva"
        self.fisico += qtd
        self.movimentos.append(Movimento("entrada", qtd, motivo))

    action reservar(qtd):
        given qtd bigger self.disponivel():
            trigger $"{self.sku}: pedidos {qtd}, disponiveis {self.disponivel()}"
        self.reservado += qtd

    action baixar(qtd, motivo):
        self.reservado -= qtd
        self.fisico -= qtd
        self.movimentos.append(Movimento("saida", qtd, motivo))

    action repor():
        yield self.disponivel() smaller_eq self.minimo

    action reconstruir():
        yield sum(self.movimentos >> morph m: (m.qtd given m.tipo is "entrada" otherwise -m.qtd))

cafe := spawn Item("CAFE-500", 5)
cafe.entrar(12, "nota 1234")
cafe.reservar(8)
assert cafe.disponivel() is 4
assert cafe.repor()

monitor:
    cafe.reservar(5)
    assert no
handle Error as e:
    out e.message

cafe.baixar(8, "pedido 77")
assert cafe.fisico is 4
assert cafe.reconstruir() is cafe.fisico

// A invariante pega o que a regra esqueceu: baixar sem ter reservado.
monitor:
    cafe.baixar(3, "erro de operacao")
    assert no
handle Error as e:
    out "recusado pela invariante: " + e.type`, lang: 'df', title: `src/produto.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/produto as P

crucible "estoque":
    trial "o saldo reconstruido bate":
        i := spawn P.Item("X", 1)
        i.entrar(10, "a")
        i.reservar(4)
        i.baixar(4, "b")
        expect i.reconstruir() is i.fisico`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["`invariant` no blueprint", "o método que esqueceu uma conferência deixa o saldo negativo"], ["físico e reservado separados", "dois pedidos vendem a mesma última unidade"], ["os movimentos são records", "a auditoria mostra um saldo que ninguém sabe de onde veio"], ["`reconstruir` a partir dos movimentos", "o saldo corrompido não tem como ser conferido"]]}},
  {"h2": "Para ir além"},
  {"list": ["As peças de DDD que cobram as distinções: [Arcane.Dominio](/docs/biblioteca/dominio).", "Dois operadores ao mesmo tempo: [Concorrência](/docs/tecnicas/concorrencia).", "Receita completa: [Inventário](/docs/receitas/inventario)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Controle de estoque"}
      description={"Entrada, saída, reserva e o estoque mínimo — com a invariante que nunca deixa o saldo negativo."}
      href={"/docs/projetos/estoque"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
