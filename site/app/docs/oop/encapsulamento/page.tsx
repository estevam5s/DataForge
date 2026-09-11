// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Encapsulamento",
  description: "Esconder o detalhe para poder mudá-lo — e as validações que só existem porque ele existe.",
};

const blocos: Bloco[] = [
  {"p": "Encapsular não é esconder por esconder. É **separar o que os outros dependem do que você pode mudar amanhã**."},
  {"p": "Um campo público faz parte do contrato: mudá-lo quebra quem o usa. Um campo privado é seu — você troca a implementação e ninguém percebe."},
  {"h2": "O problema, concretamente"},
  { code: `// Sem encapsulamento: qualquer um mexe no saldo
blueprint ContaAberta:
    saldo: Float := 0.0

c := spawn ContaAberta()
c.saldo := -1000        // ninguém impediu
assert c.saldo is -1000.0`, lang: 'df' },
  { code: `// Com encapsulamento: a regra mora com o dado
blueprint Conta:
    private saldo: Float := 0.0

    action depositar(valor):
        given valor smaller_eq 0:
            trigger "depósito precisa ser positivo"
        self.saldo += valor
        yield self.saldo

    action sacar(valor):
        given valor bigger self.saldo:
            trigger "saldo insuficiente"
        self.saldo -= valor
        yield self.saldo

    get extrato():
        yield self.saldo

c := spawn Conta()
c.depositar(100)
c.sacar(30)
assert c.extrato is 70.0

monitor:
    c.sacar(1000)
handle e:
    assert e.message is "saldo insuficiente"`, lang: 'df' },
  {"p": "O saldo nunca fica negativo, e não porque quem usa lembrou de conferir — porque não há caminho até ele que não passe pela regra."},
  {"h2": "`private` alcança quem?"},
  {"p": "Só o blueprint que **declarou** o membro. Nem o herdeiro entra:"},
  { code: `blueprint Base:
    private segredo: Integer := 42
    protected compartilhado: Integer := 7

    action ler_proprio():
        yield self.segredo

blueprint Filho extends Base:
    action ler_protegido():
        yield self.compartilhado

// um método de Base lê o private de Base, mesmo numa instância de Filho
assert (spawn Filho()).ler_proprio() is 42
assert (spawn Filho()).ler_protegido() is 7

monitor:
    out (spawn Base()).segredo
handle e:
    assert "private" in e.message`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Quem declarou, não quem instanciou", "texto": "Um método herdado de `Base` que lê um `private` de `Base` funciona numa instância de `Filho` — o dono da visibilidade é quem escreveu o membro."}},
  {"h2": "Getters e setters, com propósito"},
  {"p": "Um `get`/`set` que só devolve e atribui o campo não encapsula nada — é um campo público com três linhas a mais. O valor aparece quando há **regra** ou **derivação**:"},
  { code: `blueprint Temperatura:
    private _celsius: Float := 0.0

    // derivada: não há campo 'fahrenheit', ele é calculado
    get fahrenheit():
        yield self._celsius * 9 / 5 + 32

    set fahrenheit(valor):
        self._celsius := (valor - 32) * 5 / 9

    get celsius():
        yield self._celsius

    set celsius(valor):
        given valor smaller -273.15:
            trigger "abaixo do zero absoluto"
        self._celsius := valor

t := spawn Temperatura()
t.celsius := 100
assert t.fahrenheit is 212.0
t.fahrenheit := 32
assert t.celsius is 0.0`, lang: 'df' },
  {"p": "Ver [propriedades](/docs/oop/propriedades) para a sintaxe completa."},
  {"h2": "Imutabilidade"},
  {"p": "A forma mais forte de encapsulamento: um valor que **não muda** não precisa de proteção. `record` é imutável, e alterar produz um valor novo:"},
  { code: `record Dinheiro:
    centavos: Integer
    moeda: String

    action somar(outro):
        given outro.moeda isnt self.moeda:
            trigger "moedas diferentes"
        yield Dinheiro(self.centavos + outro.centavos, self.moeda)

a := Dinheiro(1050, "BRL")
b := a.somar(Dinheiro(250, "BRL"))

assert a.centavos is 1050       // o original não mudou
assert b.centavos is 1300`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Imutável passa sem medo", "texto": "Um record pode ser passado a qualquer função sem risco de ela alterá-lo. É o que torna código concorrente tratável — e o que permite usá-lo como chave de vault."}},
  {"h2": "Ocultação de informação"},
  {"p": "O princípio geral, de David Parnas: **um módulo deve esconder uma decisão de projeto**. Se a decisão mudar, só ele muda."},
  { code: `blueprint Cache:
    private itens: Vault := {}
    private ordem: Cluster := []
    private limite: Integer := 100

    action guardar(chave, valor):
        given not self.itens.has(chave):
            self.ordem.append(chave)
        self.itens[chave] := valor
        given len(self.ordem) bigger self.limite:
            velha := self.ordem.pop(0)
            delete self.itens[velha]
        yield valor

    action pegar(chave):
        yield self.itens.get(chave, void)

c := spawn Cache()
c.guardar("a", 1)
assert c.pegar("a") is 1
assert c.pegar("z") is void`, lang: 'df' },
  {"p": "A decisão escondida aqui é *como* o cache decide o que descartar. Trocar por LRU de verdade, ou por tempo de vida, não muda uma linha de quem usa."},
];

const headings = [{ id: 'o-problema-concretamente', text: "O problema, concretamente", level: 2 as const }, { id: 'private-alcanca-quem', text: "`private` alcança quem?", level: 2 as const }, { id: 'getters-e-setters-com-proposito', text: "Getters e setters, com propósito", level: 2 as const }, { id: 'imutabilidade', text: "Imutabilidade", level: 2 as const }, { id: 'ocultacao-de-informacao', text: "Ocultação de informação", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Encapsulamento"}
      description={"Esconder o detalhe para poder mudá-lo — e as validações que só existem porque ele existe."}
      href={"/docs/oop/encapsulamento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
