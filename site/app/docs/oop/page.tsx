import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Orientação a objetos",
  description: "Blueprints, records, traits — e quando usar cada um.",
};

const blocos: Bloco[] = [
  {"p": "DataForge tem três formas de agrupar dados e comportamento. A escolha entre elas é a decisão de modelagem mais frequente, e a que mais custa quando erra."},
  {"table": {"head": ["", "Igualdade", "Muda?", "Para quê"], "rows": [["`record`", "estrutural", "não", "valor: ponto, dinheiro, data"], ["`blueprint`", "identidade", "sim", "entidade: conta, sessão, conexão"], ["`trait`", "—", "—", "contrato: o que um tipo precisa saber fazer"]]}},
  {"p": "A pergunta que decide entre os dois primeiros: **dois desses, com os mesmos valores, são a mesma coisa?** Dois pontos `(1, 2)` são — record. Duas contas com o mesmo saldo não são — blueprint."},
  {"h2": "O que o 4.1 trouxe"},
  {"p": "Até o 4.0 um blueprint tinha métodos, herança e traits. Faltava tudo o que separa a API pública do detalhe interno:"},
  { code: `blueprint Conta:
    private saldo: Float := 0.0
    protected titular: String := ""

    action setup(titular):
        self.titular := titular

    action depositar(valor):
        given valor smaller_eq 0:
            trigger "deposito precisa ser positivo"
        self.saldo += valor
        yield self.saldo

    action sacar(valor):
        given valor bigger self.saldo:
            trigger "saldo insuficiente"
        self.saldo -= valor
        yield self.saldo

    get extrato():
        yield $"{self.titular}: {self.saldo}"`, lang: 'df' },
  {"list": ["**Campos declarados** com tipo e padrão — [campos e visibilidade](/docs/oop/campos)", "**`private` e `protected`** que valem de verdade, não por convenção", "**Propriedades** `get`/`set` — [propriedades](/docs/oop/propriedades)", "**Métodos estáticos** — [estáticos](/docs/oop/estaticos)", "**Sobrecarga de operadores** — [operadores](/docs/oop/operadores)", "**Abstratos e contratos** conferidos na declaração — [abstratos](/docs/oop/abstratos)", "**`final`** para impedir sobrescrita"]},
  {"h2": "Por onde começar"},
  {"p": "Se você já usa blueprint, comece por [campos e visibilidade](/docs/oop/campos) — é o que muda mais o código do dia a dia. Se está modelando algo novo, [modelagem](/docs/oop/modelagem) discute as escolhas antes da sintaxe."},
  {"p": "Os dez exercícios do [módulo 21](/docs/exercicios) percorrem tudo isso na ordem, cada um rodando e com `.md` explicando o conceito."},
];

const headings = [{ id: 'o-que-o-41-trouxe', text: "O que o 4.1 trouxe", level: 2 as const }, { id: 'por-onde-comecar', text: "Por onde começar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Orientação a objetos"}
      description={"Blueprints, records, traits — e quando usar cada um."}
      href={"/docs/oop"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
