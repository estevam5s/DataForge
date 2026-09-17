# 246 — Uma metaclasse que registra, valida e audita

## O que se pratica

`meta blueprint`, `using`, os ganchos `on_forge`, `on_write` e
`on_missing`, a herança da metaclasse e `Reflexo.meta_instancia`.

## O que este exercício ensina que não é óbvio

**1. A metaclasse age sobre a CLASSE, uma vez, e sobre os OBJETOS,
sempre.** `on_forge` roda quando `Cliente` é declarado; `on_write` roda
em cada escrita de cada cliente. É por isso que a validação de `id` falha
na declaração, antes de existir objeto nenhum.

**2. Ela é herdada.** `Cliente` e `Pedido` não escrevem `using`, e são
governados. Uma regra de domínio escrita uma vez vale para a família
inteira — e uma filha não consegue escapar dela.

**3. A metaclasse tem uma instância só.** `tabelas` e `escritas` são
campos dessa instância, compartilhada por todos os modelos. É o `self`
dos ganchos, e é onde um registro de classes naturalmente mora.

**4. Nomes de gancho são fixos, e o errado é recusado.** Um `on_forje`
nunca rodaria, e nada avisaria: a metaclasse pareceria ignorada. A
recusa vem com a sugestão do nome certo.

**5. Um gancho não dispara outro.** `R.campos(molde)` e `R.nome(obj)`
dentro dos ganchos não caem em `on_read` — sem essa regra, auditar
leituras seria recursão infinita.

## Para ir além

- Acrescente `on_spawn` devolvendo um objeto já criado para o mesmo `id`
  e transforme o modelo num mapa de identidade.
