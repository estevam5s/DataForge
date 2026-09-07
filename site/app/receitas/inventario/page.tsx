import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sistema de inventário",
  description: "Records, enums, regras puras e relatório — a estrutura de uma aplicação de verdade.",
};

const blocos: Bloco[] = [
  {"p": "Este é o código completo do exercício `119_inventario_completo.df`, que roda e verifica a si mesmo."},
  { code: `adopt Arcane.Text as Text

blueprint Produto(codigo, nome, preco, quantidade):
    action valor_total():
        yield self.preco * self.quantidade

    action baixa(qtd):
        guard qtd smaller_eq self.quantidade, "estoque insuficiente para " + self.nome
        self.quantidade := self.quantidade - qtd
        yield self.quantidade

    action toString():
        yield self.codigo + " " + self.nome

estoque := [
    spawn Produto("P01", "Mouse", 80.0, 15),
    spawn Produto("P02", "Teclado", 200.0, 4),
    spawn Produto("P03", "Monitor", 1200.0, 2),
    spawn Produto("P04", "Cabo", 25.0, 60)
]

valores := estoque >> morph p: p.valor_total()
patrimonio := valores >> distill acc, v: acc + v 0

criticos := estoque >> sift p: p.quantidade smaller 5

out Text.box("Inventario")
cycle p in estoque:
    out "  " + p.codigo + " " + p.nome.pad_end(10) + str(p.quantidade).pad_start(4) + "  R$ " + str(p.valor_total())

out ""
out "patrimonio: R$", patrimonio
out "criticos:", criticos >> morph p: p.nome

assert round(patrimonio, 2) is 5900.0, "patrimonio"
assert len(criticos) is 2, "dois produtos criticos"

estoque[0].baixa(5)
assert estoque[0].quantidade is 10, "baixa aplicada"

erro := no
monitor:
    estoque[2].baixa(99)
handle e:
    erro := yes
    out "erro:", e
assert erro is yes, "baixa acima do estoque e bloqueada"`, title: `119_inventario_completo.df` },
  {"h2": "As camadas"},
  {"table": {"head": ["Camada", "Contém", "Depende de"], "rows": [["**Modelo**", "records, enums", "nada"], ["**Regras**", "decisões de negócio", "modelo"], ["**Apresentação**", "como virar texto", "modelo, regras"], ["**Aplicação**", "orquestra o fluxo", "todas"]]}},
  {"p": "O modelo não sabe que existe apresentação; as regras não sabem se o resultado vira terminal, HTTP ou CSV."},
  {"h2": "Regras puras são testáveis"},
  {"p": "Uma ação que não imprime, não lê arquivo e não consulta banco tem teste de uma linha. Se ela também formatasse a saída, testá-la exigiria comparar strings."},
  {"p": "Mais sobre isso em [Estrutura de projeto](/tecnicas/projeto)."},
];

const headings = [{ id: 'as-camadas', text: "As camadas", level: 2 as const }, { id: 'regras-puras-sao-testaveis', text: "Regras puras são testáveis", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sistema de inventário"}
      description={"Records, enums, regras puras e relatório — a estrutura de uma aplicação de verdade."}
      href={"/receitas/inventario"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
