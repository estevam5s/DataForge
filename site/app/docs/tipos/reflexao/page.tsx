// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/tipos_resultado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Reflexão de tipos",
  description: "Arcane.Tipos: os metadados de um type declarado, conferir sem levantar, a forma estrutural de um valor e os campos de um record com o tipo de cada um.",
};

const blocos: Bloco[] = [
  {"p": "`typeof` responde o **nome** do tipo de um valor. Quem escreve validação genérica, serialização, formulário ou tabela a partir de um record precisa de mais: os metadados do tipo declarado, e uma conferência que **responda** em vez de levantar."},
  {"h2": "Os metadados de um `type`"},
  { code: `adopt Arcane.Tipos as Tipos

type Id := Integer
type Json := String | Integer
type Positivo := Integer where valor bigger 0
opaque type Cpf := String where len(valor) is 11

assert Tipos.de("Id")["especie"] is "alias"
assert Tipos.de("Json")["especie"] is "uniao"
assert Tipos.de("Json")["partes"] is ["String", "Integer"]
assert Tipos.de("Positivo")["especie"] is "refinamento"
assert Tipos.de("Positivo")["regra"] is "valor bigger 0"
assert Tipos.de("Cpf")["opaco"]
assert Tipos.existe("Id") and not Tipos.existe("NaoExiste")
assert len(Tipos.declarados()) is 4`, lang: 'df' },
  {"h2": "Conferir sem levantar"},
  {"p": "`satisfaz` responde `yes`/`no`. A base vem **antes** da regra: perguntar `len(valor)` a um número daria um erro do interpretador em vez de um `no` honesto."},
  { code: `adopt Arcane.Tipos as Tipos

type Positivo := Integer where valor bigger 0
opaque type Cpf := String where len(valor) is 11

assert Tipos.satisfaz(5, "Positivo")
assert not Tipos.satisfaz(-5, "Positivo")
assert not Tipos.satisfaz("texto", "Positivo")      // a base decide primeiro
assert Tipos.satisfaz(Cpf("12345678901"), "Cpf")
assert not Tipos.satisfaz("12345678901", "Cpf")     // nominal

// e quando você QUER o erro de sempre:
monitor:
    Tipos.conferir(-1, "Positivo")
    assert no
handle TypeError as e:
    assert "Positivo" in e.message`, lang: 'df' },
  {"h2": "A forma estrutural de um valor"},
  {"p": "`typeof([1, 2])` responde `Cluster` — o nome do tipo. `Tipos.forma([1, 2])` responde `Cluster<Integer>` — a forma. Uma coleção de tipos misturados responde `Cluster<Any>`: dizer o tipo do primeiro item seria mentira."},
  { code: `adopt Arcane.Tipos as Tipos

assert typeof([1, 2]) is "Cluster"
assert Tipos.forma([1, 2]) is "Cluster<Integer>"
assert Tipos.forma([1, "a"]) is "Cluster<Any>"
assert Tipos.forma((1, "a")) is "Tuple<Integer, String>"
assert Tipos.forma({"a": 1}) is "Vault<String, Integer>"
assert Tipos.forma([[1], [2]]) is "Cluster<Cluster<Integer>>"

assert Tipos.e_colecao((1, 2)) and not Tipos.e_colecao(3)
assert Tipos.e_imutavel((1, 2)) and not Tipos.e_imutavel([1, 2])`, lang: 'df' },
  {"h2": "Os campos, com o tipo de cada um"},
  {"p": "É o que transforma um tipo em formulário, tabela ou esquema sem escrever a lista de campos duas vezes."},
  { code: `adopt Arcane.Tipos as Tipos

record Cliente:
    nome: String
    idade: Integer

blueprint Conta:
    saldo := 0.0

c := Cliente("Ana", 30)
campos := Tipos.campos(c)

assert campos["nome"]["tipo"] is "String"
assert campos["idade"]["valor"] is 30
assert Tipos.campos(spawn Conta())["saldo"]["tipo"] is "Float"
assert Tipos.campos({"a": 1})["a"]["tipo"] is "Integer" `, lang: 'df' },
  {"h2": "Um validador genérico, em oito linhas"},
  {"p": "Juntando as duas peças: os campos vêm da reflexão, a regra vem do tipo declarado, e o relato vem do `Resultado`."},
  { code: `adopt Arcane.Tipos as Tipos
adopt Arcane.Resultado as R

type Positivo := Integer where valor bigger 0
type Email := String where "@" in valor

record Pedido:
    quantidade: Positivo
    contato: Email

action validar(vault, esperado) -> Resultado:
    problemas := []
    cycle campo in esperado:
        given not Tipos.satisfaz(vault[campo] ?? void, esperado[campo]):
            problemas.append($"{campo} não é {esperado[campo]}")
    yield R.falha(problemas) given len(problemas) bigger 0 otherwise R.ok(vault)

esperado := {"quantidade": "Positivo", "contato": "Email"}

assert validar({"quantidade": 2, "contato": "ana@x.com"}, esperado).deu_certo()

ruim := validar({"quantidade": 0, "contato": "ana"}, esperado)
assert ruim.falhou()
assert len(ruim.erro()) is 2`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Reflexão em execução, prova antes de rodar", "texto": "`Arcane.Tipos` responde **em execução**: é para código que decide sobre tipos que ele não conhece de antemão. A conferência que acontece antes de rodar é a do `dataforge check`, que prova o que um literal permite — as duas se completam, e nenhuma substitui a outra."}},
];

const headings = [{ id: 'os-metadados-de-um-type', text: "Os metadados de um `type`", level: 2 as const }, { id: 'conferir-sem-levantar', text: "Conferir sem levantar", level: 2 as const }, { id: 'a-forma-estrutural-de-um-valor', text: "A forma estrutural de um valor", level: 2 as const }, { id: 'os-campos-com-o-tipo-de-cada-um', text: "Os campos, com o tipo de cada um", level: 2 as const }, { id: 'um-validador-generico-em-oito-linhas', text: "Um validador genérico, em oito linhas", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Reflexão de tipos"}
      description={"Arcane.Tipos: os metadados de um type declarado, conferir sem levantar, a forma estrutural de um valor e os campos de um record com o tipo de cada um."}
      href={"/docs/tipos/reflexao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
