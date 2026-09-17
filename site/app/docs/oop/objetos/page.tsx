// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/oop_meta.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Objetos: cópia, imutabilidade e serialização",
  description: "Arcane.Objetos: clonar raso e fundo, congelar, igualdade e hash coerentes, e serialização polimórfica que não deixa o dado escolher o tipo.",
};

const blocos: Bloco[] = [
  {"h2": "Identidade e igualdade"},
  {"p": "`is` entre instâncias é **identidade** — dois `spawn` são dois objetos. É o certo para entidade. Para objeto de valor há `__eq__`, ou `Objetos.igual`, que compara estrutura sem obrigar o blueprint a escrever nada."},
  { code: `adopt Arcane.Objetos as O

blueprint Endereco(rua, numero):
    x := 0

a := spawn Endereco("Flores", 10)
b := spawn Endereco("Flores", 10)
assert a isnt b                 // identidade
assert O.igual(a, b)            // estrutura
assert O.hash(a) is O.hash(b)   // coerente com igual`, lang: 'df' },
  {"h2": "Contrato entre __eq__ e __hash__"},
  {"p": "Uma instância é chave de vault. Quem declara `__eq__` precisa declarar `__hash__` coerente — objetos iguais com hash diferente somem do vault."},
  { code: `blueprint Cpf(numero):
    action __eq__(outro):
        yield self.numero is outro.numero
    action __hash__():
        yield self.numero

donos := {}
donos[spawn Cpf("123")] := "Ana"
assert donos[spawn Cpf("123")] is "Ana"
assert sorted([3, 1, 2]) is [1, 2, 3]`, lang: 'df' },
  {"h2": "Cópia"},
  { code: `adopt Arcane.Objetos as O

blueprint Carrinho:
    itens := []

c1 := spawn Carrinho()
c1.itens.append("caneta")

raso := O.clonar(c1)
fundo := O.clonar_fundo(c1)
fundo.itens.append("lápis")

assert raso.itens is c1.itens          // a mesma lista
assert len(c1.itens) is 1              // o fundo não mexeu no original`, lang: 'df' },
  {"p": "A cópia não roda `setup` — ela não **nasce**, é duplicada. `__copy__`, `__deepcopy__` e `__clone__` no blueprint assumem a cópia quando existem."},
  {"h2": "Congelar"},
  { code: `adopt Arcane.Objetos as O

blueprint Config:
    porta := 80

c := O.congelar(spawn Config())
assert O.congelado(c)
monitor:
    c.porta := 81
    assert no
handle FrozenObjectError:
    out "passe um objeto congelado a outra thread sem medo" `, lang: 'df' },
  {"h2": "Serialização polimórfica, e segura"},
  {"p": "`para_vault` grava `$tipo` e resolve ciclos com `$id`/`$ref`. `de_vault` **exige a lista de tipos** que pode reconstruir: um dado de fora com `\"$tipo\": \"Admin\"` não decide qual blueprint o programa constrói. É assim que desserialização vira execução de código alheio em linguagens que deixaram o dado escolher."},
  { code: `adopt Arcane.Objetos as O

blueprint Item(nome, preco):
    x := 0
blueprint Pedido:
    itens := []
    invariant len(self.itens) smaller_eq 100

p := spawn Pedido()
p.itens.append(spawn Item("caneta", 3))
dado := O.para_vault(p)
assert dado["$tipo"] is "Pedido"

volta := O.de_vault(dado, [Pedido, Item])
assert volta.itens[0].nome is "caneta"

monitor:
    O.de_vault({"$tipo": "Admin", "poderes": "todos"}, [Pedido, Item])
    assert no
handle UnsafeDeserializationError:
    out "tipo fora da lista: recusado" `, lang: 'df' },
  {"list": ["só os campos **públicos** saem por padrão; `{\"privados\": yes}` inclui os outros, para persistência própria;", "a reconstrução confere as **invariantes** — um dado que chega violando a regra do tipo é recusado ali;", "`static versao_do_esquema := 2` grava `$versao`, e `on_deserialize` numa metaclasse migra o vault antes de montar."]},
];

const headings = [{ id: 'identidade-e-igualdade', text: "Identidade e igualdade", level: 2 as const }, { id: 'contrato-entre-eq-e-hash', text: "Contrato entre __eq__ e __hash__", level: 2 as const }, { id: 'copia', text: "Cópia", level: 2 as const }, { id: 'congelar', text: "Congelar", level: 2 as const }, { id: 'serializacao-polimorfica-e-segura', text: "Serialização polimórfica, e segura", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Objetos: cópia, imutabilidade e serialização"}
      description={"Arcane.Objetos: clonar raso e fundo, congelar, igualdade e hash coerentes, e serialização polimórfica que não deixa o dado escolher o tipo."}
      href={"/docs/oop/objetos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
