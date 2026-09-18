# 255 — A falha como valor, e a reflexão de tipos

## Três formas, três perguntas

| Forma | Quando | O que acontece |
|---|---|---|
| `monitor`/`handle`/`trigger` | o que **não era esperado**: disco cheio, rede caída, bug | interrompe, e sobe até quem sabe tratar |
| `void` com `??` e `?.` | a **ausência** simples: campo opcional, cache vazio | segue com um padrão |
| `Arcane.Resultado` | a falha **esperada** de uma fronteira: validação, busca, parsing | vira valor, e quem chama decide |

A regra prática: se quem chama **precisa** decidir o que fazer, devolva
`Resultado`. Se ninguém ali pode fazer nada a respeito, `trigger`.

Um `Resultado` que todo mundo ignora é pior que um erro — ele passa
adiante calado. Um `trigger` para o que era esperado obriga `monitor` em
todo lugar, e aí ninguém lê mais nenhum.

## Ler o valor é uma afirmação

`r.valor()` numa falha **levanta**, com o motivo dentro da mensagem: ali
quem escreveu afirmou que deu certo. Quem não quer afirmar tem duas
saídas que nunca levantam:

- `r.ou(padrao)` — o valor, ou o padrão;
- `r.exigir("minha mensagem")` — levanta, mas com a frase de quem chama.

E `mapear`, `entao` e `recuperar` atravessam a falha **intacta**, o que
dispensa um `given` entre cada passo da corrente.

## `tentar` não engole sinal de controle

`R.tentar` captura `DataForgeError` — o erro da linguagem. Um `halt`, um
`skip` ou um `yield` atravessa: eles derivam de `BaseException` de
propósito, e transformá-los em falha faria um `halt` dentro de um
`tentar` parar de sair do laço, calado.

## `Talvez`, apesar de `void`

`void` resolve a ausência em quase todo lugar. O que ele não resolve é
distinguir **"a chave não está lá"** de **"a chave está lá e vale
void"** — a dúvida de todo vault de configuração:

```dataforge
config := {"tema": void}
R.chave(config, "tema").tem()      // yes: está lá
R.chave(config, "idioma").tem()    // no:  não está
```

## Reflexão: o que `typeof` não responde

`typeof` dá o **nome** do tipo. `Arcane.Tipos` dá o resto:

- `Tipos.de("Positivo")` — espécie (`alias`, `uniao`, `intersecao`,
  `refinamento`, `opaco`), base, partes, regra;
- `Tipos.satisfaz(valor, "Positivo")` — confere e **responde**, em vez
  de levantar;
- `Tipos.forma(valor)` — a forma **estrutural**: `Cluster<Integer>`,
  `Tuple<Integer, String>`, `Vault<String, Integer>`. Uma coleção
  misturada responde `Cluster<Any>`, porque dizer o tipo do primeiro
  item seria mentira;
- `Tipos.campos(valor)` — os campos de um record, instância ou vault,
  com o tipo de cada um.

Juntando as duas peças sai um validador genérico em oito linhas: os
campos vêm da reflexão, a regra vem do tipo declarado, e o relato vem do
`Resultado`.

Reflexão responde **em execução**; o `dataforge check` prova antes de
rodar o que um literal permite provar. As duas se completam, e nenhuma
substitui a outra.
