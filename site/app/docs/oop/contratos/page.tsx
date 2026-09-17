// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Contratos",
  description: "contract, invariant, expects e promises: interfaces que não carregam código, e design por contrato que diz de quem é o erro.",
};

const blocos: Bloco[] = [
  {"p": "Há dois sentidos de contrato em orientação a objetos, e o DataForge tem os dois: o **contrato de interface** (o que um tipo promete oferecer) e o **design por contrato** (o que uma operação exige e garante)."},
  {"h2": "contract: só a assinatura"},
  {"p": "Um `contract` declara métodos e propriedades sem corpo. Um corpo é recusado na leitura: implementação padrão é o papel do `trait`, e deixar o contrato carregar código apagaria a única diferença entre os dois."},
  { code: `contract Leitura<T>:
    action buscar(id: Integer) -> T

contract Escrita<T>:
    action salvar(item: T)

contract Repositorio<T> extends Leitura, Escrita:
    get total() -> Integer

blueprint RepoMemoria with Repositorio:
    itens := {}
    action buscar(id: Integer):
        yield self.itens[id] ?? void
    action salvar(item):
        self.itens[len(self.itens) + 1] := item
    get total():
        yield len(self.itens)

// quem só lê depende só de Leitura — o Princípio da Segregação de Interface
action primeiro(fonte: Leitura):
    yield fonte.buscar(1)

r := spawn RepoMemoria()
r.salvar("caneta")
assert primeiro(r) is "caneta"
assert r.total is 1`, lang: 'df' },
  {"table": {"head": ["", "trait", "contract"], "rows": [["corpo de método", "pode ter (implementação padrão)", "recusado"], ["estende outro", "não", "`contract A extends B, C`"], ["confere aridade de quem implementa", "não", "sim — `SignatureMismatchError`"], ["propriedade exigida", "não", "`get total() -> Integer`"], ["vale como tipo de parâmetro", "sim", "sim, inclusive o que ele herda"]]}},
  {"p": "Na declaração, o blueprint concreto que adota um contrato precisa ter cada método, **aceitar todos os argumentos** que o contrato passa (parâmetros a mais precisam de padrão) e ter cada propriedade exigida — como `get` ou como campo."},
  {"h2": "expects, promises, invariant"},
  {"p": "As três cláusulas respondem a mesma pergunta — *de quem é o erro?* — e é isso que as separa de um `assert`:"},
  {"table": {"head": ["Cláusula", "Onde", "Quando roda", "Erro", "Quem errou"], "rows": [["`expects cond, msg`", "corpo de ação", "onde estiver", "`PreconditionError`", "quem chamou"], ["`promises cond, msg`", "topo do corpo", "na saída, com `outcome`", "`PostconditionError`", "a ação"], ["`invariant cond, msg`", "corpo de blueprint", "depois de construir e de cada método público", "`InvariantError`", "a operação"]]}},
  { code: `blueprint Conta:
    saldo := 0
    invariant self.saldo bigger_eq 0, "saldo nunca fica negativo"

    action depositar(valor):
        expects valor bigger 0, "depósito precisa ser positivo"
        promises self.saldo is before(self.saldo) + valor
        self.saldo += valor
        yield self.saldo

    action sacar(valor):
        expects valor bigger 0, "saque precisa ser positivo"
        promises outcome is self.saldo
        self.saldo -= valor
        yield self.saldo

c := spawn Conta()
c.depositar(100)
assert c.sacar(30) is 70

monitor:
    c.depositar(-5)
    assert no
handle PreconditionError as e:
    assert "positivo" in e.message

monitor:
    c.sacar(500)
    assert no
handle InvariantError as e:
    assert "negativo" in e.message`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "before(…) é o valor da entrada", "texto": "`promises self.saldo is before(self.saldo) + valor` compara o estado da SAÍDA com o da ENTRADA. `before` avalia a expressão antes do corpo rodar e guarda o resultado — é o `old` do Eiffel."}},
  {"p": "A invariante é conferida quando a chamada **mais de fora** termina. Dentro de um método o objeto pode passar por estados intermediários — transferir entre dois campos exige duas escritas — e cobrar ali recusaria todo método correto. Um método `private` não dispara a conferência: ele é passo de outro."},
  {"h2": "Liskov, conferido"},
  {"p": "O Princípio da Substituição diz que a filha serve onde a mãe servia. A parte que dá para **provar** sem rodar, o `check` prova: uma sobrescrita que aceita menos argumentos que a mãe quebra todo código escrito para a mãe, e vira aviso `substituicao-quebrada`. Contra um contrato, é erro."},
  { code: `blueprint Exportador:
    action exportar(dados, formato := "csv"):
        yield formato

blueprint ExportadorJson extends Exportador:
    action exportar(dados, formato := "json"):     // aceita o mesmo: ok
        yield formato

assert (spawn ExportadorJson()).exportar([]) is "json"
`, lang: 'df' },
];

const headings = [{ id: 'contract-so-a-assinatura', text: "contract: só a assinatura", level: 2 as const }, { id: 'expects-promises-invariant', text: "expects, promises, invariant", level: 2 as const }, { id: 'liskov-conferido', text: "Liskov, conferido", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Contratos"}
      description={"contract, invariant, expects e promises: interfaces que não carregam código, e design por contrato que diz de quem é o erro."}
      href={"/docs/oop/contratos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
