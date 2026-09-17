// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Modificadores",
  description: "private, protected, internal, readonly, override, final, sealed, exclusive, lazy e static steady — o que cada um promete, e quem confere.",
};

const blocos: Bloco[] = [
  {"p": "Um modificador é uma promessa escrita na declaração. A diferença entre uma promessa e um comentário é que **alguém confere**: o `dataforge check` antes de rodar, e o interpretador quando roda. Cada linha da tabela abaixo tem um erro com nome próprio, que um `handle` pega."},
  {"table": {"head": ["Modificador", "Vale em", "Promete", "Quebrar dá"], "rows": [["`private`", "ação, campo, propriedade", "só o blueprint que declarou lê, escreve e chama", "`TypeError`"], ["`protected`", "ação, campo, propriedade", "o blueprint e os herdeiros", "`TypeError`"], ["`internal`", "ação, campo, propriedade", "só o **arquivo** que declarou", "`InternalAccessError`"], ["`readonly`", "campo", "só a construção escreve", "`ReadOnlyFieldError`"], ["`static steady`", "campo estático", "constante de classe", "`ConstantReassignmentError`"], ["`override`", "ação, propriedade", "substitui um membro herdado", "`OverrideTargetError`"], ["`final`", "ação", "a filha não substitui", "`FinalOverrideError`"], ["`final blueprint`", "blueprint", "ninguém herda", "`FinalBlueprintError`"], ["`sealed blueprint`", "blueprint", "só herda quem está no mesmo arquivo", "`SealedBlueprintError`"], ["`exclusive`", "ação", "uma thread por vez no objeto", "—"], ["`lazy`", "`get`", "calcula uma vez por objeto", "—"]]}},
  {"h2": "Visibilidade: private, protected, internal"},
  {"p": "`private` e `protected` falam de **linhagem**; `internal` fala de **arquivo**. É a visibilidade de um módulo: as peças de dentro conversam, e quem adota o arquivo vê só o público."},
  { code: `blueprint Conta:
    private saldo := 0.0
    protected taxa := 0.01
    internal action auditar():
        yield $"saldo {self.saldo}"

    action depositar(v):
        self.saldo += v
        yield self.saldo

blueprint ContaPremium extends Conta:
    action custo(v):
        yield v * self.taxa          // protected: a filha lê

c := spawn ContaPremium()
c.depositar(100)
assert c.custo(100) is 1.0
assert c.auditar() is "saldo 100.0"   // internal: mesmo arquivo

monitor:
    out c.saldo
    assert no
handle TypeError as e:
    assert "private" in e.message`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Vale para a chamada também", "texto": "`obj.privado()` de fora é recusado exatamente como `obj.privado`. A leitura já era conferida; a chamada de método não era, e um `private action` podia ser chamado de qualquer lugar."}},
  {"h2": "readonly: identidade que não muda"},
  {"p": "Um campo `readonly` recebe valor enquanto o objeto nasce — no padrão, no cabeçalho, no `setup`, no corpo solto do blueprint — e depois disso é recusado. O `check` também acusa um método comum que o escreve."},
  { code: `blueprint Pedido:
    readonly id := 0
    readonly criado_em := "2026-09-17"
    itens := []

    action setup(id):
        self.id := id                 // construindo: permitido

p := spawn Pedido(42)
assert p.id is 42

monitor:
    p.id := 43
    assert no
handle ReadOnlyFieldError:
    out "o id de um pedido não muda"

// 'with' constrói OUTRO objeto, e por isso pode mudar um readonly
copia := p with {"id": 7}
assert copia.id is 7 and p.id is 42`, lang: 'df' },
  {"h2": "Constante de classe: static steady"},
  { code: `blueprint Http:
    static steady PORTA_PADRAO := 80
    static conexoes := 0

Http.conexoes := Http.conexoes + 1     // estático comum: muda
assert Http.PORTA_PADRAO is 80

monitor:
    Http.PORTA_PADRAO := 8080
    assert no
handle ConstantReassignmentError:
    out "constante é constante" `, lang: 'df' },
  {"h2": "override: a promessa que pega o erro de digitação"},
  {"p": "Sem `override`, um método com o nome quase certo vira um método novo, e o da mãe continua rodando — em silêncio. Com `override`, o nome errado é erro, com sugestão."},
  { code: `blueprint Animal:
    action falar():
        yield "..."

blueprint Gato extends Animal:
    override action falar():
        yield "miau"

assert (spawn Gato()).falar() is "miau"
`, lang: 'df' },
  { code: `blueprint Cachorro extends Animal:
    override action fala():     // erro[override-sem-alvo]: did you mean 'falar'?
        yield "au"
`, lang: 'text' },
  {"h2": "final e sealed: fechar a hierarquia"},
  {"p": "`final blueprint` fecha para todo mundo. `sealed blueprint` fecha para **fora do arquivo**: a família é conhecida e completa, que é o que deixa um `match` confiar que cobriu os casos."},
  { code: `final blueprint Dinheiro(centavos):
    action somar(outro):
        yield spawn Dinheiro(self.centavos + outro.centavos)

abstract sealed blueprint Forma:
    abstract action area()

blueprint Quadrado(lado) extends Forma:
    action area():
        yield self.lado ** 2

assert (spawn Dinheiro(150)).somar(spawn Dinheiro(50)).centavos is 200
assert (spawn Quadrado(3)).area() is 9

monitor:
    blueprint Moeda extends Dinheiro:
        simbolo := "R$"
    assert no
handle FinalBlueprintError:
    out "use composição: guarde um Dinheiro num campo" `, lang: 'df' },
  {"h2": "exclusive: o monitor do objeto"},
  {"p": "O `check` avisa quando duas threads escrevem no mesmo lugar (`escrita-concorrente`). `exclusive` é a correção no nível do objeto: só uma thread por vez roda um método exclusivo **daquele** objeto. A trava é reentrante — um método exclusivo que chama outro não espera por si mesmo."},
  { code: `blueprint Estoque:
    quantidade := 0
    exclusive action entrar(n):
        atual := self.quantidade
        self.quantidade := atual + n

e := spawn Estoque()
parallel:
    thread:
        cycle i from 1 to 500:
            e.entrar(1)
    thread:
        cycle i from 1 to 500:
            e.entrar(1)

assert e.quantidade is 1000`, lang: 'df' },
  {"h2": "lazy: calcular uma vez"},
  { code: `blueprint Relatorio(linhas):
    contas := 0
    lazy get total():
        self.contas += 1
        yield sum(self.linhas)

r := spawn Relatorio([10, 20, 30])
assert r.total is 60
assert r.total is 60
assert r.contas is 1        // o corpo rodou uma vez só`, lang: 'df' },
];

const headings = [{ id: 'visibilidade-private-protected-internal', text: "Visibilidade: private, protected, internal", level: 2 as const }, { id: 'readonly-identidade-que-nao-muda', text: "readonly: identidade que não muda", level: 2 as const }, { id: 'constante-de-classe-static-steady', text: "Constante de classe: static steady", level: 2 as const }, { id: 'override-a-promessa-que-pega-o-erro-de-digitacao', text: "override: a promessa que pega o erro de digitação", level: 2 as const }, { id: 'final-e-sealed-fechar-a-hierarquia', text: "final e sealed: fechar a hierarquia", level: 2 as const }, { id: 'exclusive-o-monitor-do-objeto', text: "exclusive: o monitor do objeto", level: 2 as const }, { id: 'lazy-calcular-uma-vez', text: "lazy: calcular uma vez", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Modificadores"}
      description={"private, protected, internal, readonly, override, final, sealed, exclusive, lazy e static steady — o que cada um promete, e quem confere."}
      href={"/docs/oop/modificadores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
