# 248 — Cópia, imutabilidade e serialização que não confia no dado

## O que se pratica

`Objetos.para_vault`/`para_json` com ciclo, `de_vault`/`de_json` com
lista de tipos, `clonar` e `clonar_fundo`, `igual` e `congelar`.

## O que este exercício ensina que não é óbvio

**1. O dado não escolhe o tipo.** `de_vault` exige a lista do que pode
construir. Um JSON com `"$tipo": "Administrador"` é recusado com
`UnsafeDeserializationError`. Em linguagens que deixaram o dado escolher,
foi assim que desserialização virou execução de código alheio.

**2. Ciclo não é recursão infinita.** O pedido aponta para o cliente, que
aponta para o pedido. A segunda vez que um objeto aparece ele vira
`{"$ref": n}`, e na volta a referência é religada: `volta.pedidos[0].cliente
is volta`.

**3. A reconstrução confere a invariante.** O `setup` não roda — ele pede
argumentos que o dado não tem —, mas a regra do tipo vale: um pedido com
60 itens é recusado **na chegada**, e não três telas depois.

**4. `private` não sai.** Serializar é publicar. `{"privados": yes}` inclui
os campos fechados para persistência própria, e a escolha fica explícita.

**5. Congelar é para sempre; a cópia não.** `clonar` de um objeto
congelado devolve um objeto editável — é o jeito de mexer numa
configuração que outra thread pode estar lendo.

## Para ir além

- Declare `static versao_do_esquema := 2` em `Pedido` e escreva uma
  metaclasse com `on_deserialize` que migra o dado da versão 1.
