# 250 — Padrões com mecanismo: comando, estado e especificação

## O que se pratica

`Padroes.comandos`, `Padroes.maquina` com guarda, `Padroes.especificacao`
combinada, `Padroes.repositorio` e `Padroes.observavel` com prioridade.

## O que este exercício ensina que não é óbvio

**1. Metade do catálogo já é a linguagem.** Template Method é `abstract
blueprint`; Strategy é um contrato com duas implementações; Decorator é
`mark @…`. O módulo só traz os padrões que pedem **estado** — histórico
de comandos, estado atual de uma máquina — que ninguém deveria reescrever.

**2. A máquina recusa em vez de ignorar.** `fluxo.ir("enviar")` num pedido
aprovado é `StateError`, com a lista de onde o evento é permitido. Uma
máquina que ignora evento inválido esconde exatamente o bug que ela
existia para impedir.

**3. A especificação é uma regra de negócio com nome.** `caro.e(disponivel)`
lê como a frase do negócio, e cada peça se testa sozinha. O repositório
recebe a regra, e não um `given` espalhado por quem lista produtos.

**4. Prioridade decide a ordem; o registro não.** O ouvinte de segurança
foi assinado depois e roda antes. Um observador que depende da ordem de
assinatura quebra no dia em que alguém move um `adopt`.

## Para ir além

- Faça o ouvinte de segurança devolver `"parar"` para um pedido suspeito,
  e veja o de log não receber o evento.
