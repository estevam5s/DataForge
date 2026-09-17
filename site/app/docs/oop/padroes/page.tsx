// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Padrões de projeto",
  description: "Os 23 padrões clássicos em DataForge: os que são a própria linguagem, e os que pedem mecanismo — Arcane.Padroes.",
};

const blocos: Bloco[] = [
  {"p": "A maior parte do catálogo clássico **já é a linguagem**, e escrever biblioteca para esses seria cerimônia. O módulo `Arcane.Padroes` existe para os que pedem estado ou controle que ninguém deveria reescrever a cada projeto."},
  {"table": {"head": ["Padrão", "Em DataForge"], "rows": [["Template Method", "`abstract blueprint` com `abstract action`"], ["Strategy", "`contract` + implementações; `Padroes.estrategias()` quando a escolha vem de configuração"], ["Decorator", "`mark @decorador`"], ["Iterator", "`stream action` + `emit`, ou `__iter__`"], ["Factory Method / Static Factory", "`static action criar(…)`; `overload action setup` para construtores nomeados"], ["Abstract Factory", "um `contract` de fábrica, injetado"], ["Singleton", "`Padroes.unico(fabrica)`, ou `c.unico(Tipo)` no contêiner"], ["Object Pool", "`Padroes.pool(fabrica, tamanho)`"], ["Builder", "`Padroes.construtor(Tipo, obrigatorios)`"], ["Prototype", "`Padroes.prototipos()`, com `clonar_fundo`"], ["Flyweight", "`Padroes.compartilhado(fabrica)`"], ["Adapter", "blueprint que embrulha, ou `Padroes.adaptar(obj, mapa)`"], ["Proxy", "`Padroes.proxy(alvo, interceptar)`, ou `on_call` numa metaclasse"], ["Composite", "`Padroes.composto()`"], ["Facade / Bridge", "blueprint comum, com o implementador num campo tipado por contrato"], ["Command", "`Padroes.comandos()` — executar, desfazer, refazer"], ["Chain of Responsibility", "`Padroes.cadeia([manipuladores])`"], ["Observer", "`Padroes.observavel()` — prioridade, filtro e 'parar'; `Arcane.Eventos` entre módulos"], ["Mediator", "`Padroes.mediador()`"], ["Memento", "`Padroes.memento(obj)` / `Padroes.restaurar(obj, m)`"], ["State", "`Padroes.maquina(inicial, transicoes)`"], ["Visitor", "`Padroes.visitar(obj, visitante)` — `visitar_<Tipo>` subindo a MRO"], ["Specification", "`Padroes.especificacao(predicado)` com `e`, `ou`, `nao`"]]}},
  {"h2": "Comandos com desfazer"},
  { code: `adopt Arcane.Padroes as P

blueprint Texto:
    conteudo := ""

blueprint Escrever(doc, trecho):
    action executar():
        self.doc.conteudo := self.doc.conteudo + self.trecho
    action desfazer():
        tamanho := len(self.doc.conteudo) - len(self.trecho)
        self.doc.conteudo := self.doc.conteudo.substring(0, tamanho)

doc := spawn Texto()
historico := P.comandos()
historico.executar(spawn Escrever(doc, "olá"))
historico.executar(spawn Escrever(doc, " mundo"))
historico.desfazer()
assert doc.conteudo is "olá"
historico.refazer()
assert doc.conteudo is "olá mundo"
`, lang: 'df' },
  {"h2": "Máquina de estados"},
  { code: `adopt Arcane.Padroes as P

pedido := P.maquina("rascunho", {
    "enviar":   {"de": ["rascunho"], "para": "enviado"},
    "aprovar":  {"de": ["enviado"], "para": "aprovado"},
    "cancelar": {"de": ["rascunho", "enviado"], "para": "cancelado"},
})
pedido.ir("enviar")
assert pedido.eventos() is ["aprovar", "cancelar"]
monitor:
    pedido.ir("enviar")
    assert no
handle StateError as e:
    out e.message`, lang: 'df' },
  {"h2": "Especificação e repositório"},
  { code: `adopt Arcane.Padroes as P

record Produto:
    id: Integer
    preco: Float
    ativo: Boolean

repo := P.repositorio()
repo.salvar(Produto(1, 10.0, yes))
repo.salvar(Produto(2, 99.0, yes))
repo.salvar(Produto(3, 150.0, no))

caro := P.especificacao(lambda p => p.preco bigger 50, "caro")
ativo := P.especificacao(lambda p => p.ativo, "ativo")
assert len(repo.filtrar(caro.e(ativo))) is 1`, lang: 'df' },
  {"h2": "Arquitetura: portas e adaptadores"},
  {"p": "Hexagonal, Clean e Onion dizem a mesma coisa com desenhos diferentes: o **domínio** não conhece banco, HTTP nem fila. Em DataForge, a porta é um `contract`, o adaptador é um blueprint `with` ele, e o contêiner liga os dois na borda do programa."},
  { code: `adopt Arcane.Injecao as DI
adopt Arcane.Padroes as P

// ── domínio: não adota nada de fora ──
contract Pagamentos:
    action cobrar(valor: Float) -> Boolean

blueprint Checkout(pagamentos: Pagamentos):
    action finalizar(total: Float):
        expects total bigger 0
        yield "pago" given self.pagamentos.cobrar(total) otherwise "recusado"

// ── adaptadores: a borda ──
blueprint PagamentoFalso with Pagamentos:
    action cobrar(valor: Float) -> Boolean:
        yield valor smaller 1000

// ── composição: um lugar só ──
c := DI.conteiner()
c.unico(Pagamentos, PagamentoFalso)
checkout := c.resolver(Checkout)
assert checkout.finalizar(50.0) is "pago"
assert checkout.finalizar(5000.0) is "recusado"
`, lang: 'df' },
];

const headings = [{ id: 'comandos-com-desfazer', text: "Comandos com desfazer", level: 2 as const }, { id: 'maquina-de-estados', text: "Máquina de estados", level: 2 as const }, { id: 'especificacao-e-repositorio', text: "Especificação e repositório", level: 2 as const }, { id: 'arquitetura-portas-e-adaptadores', text: "Arquitetura: portas e adaptadores", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Padrões de projeto"}
      description={"Os 23 padrões clássicos em DataForge: os que são a própria linguagem, e os que pedem mecanismo — Arcane.Padroes."}
      href={"/docs/oop/padroes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
