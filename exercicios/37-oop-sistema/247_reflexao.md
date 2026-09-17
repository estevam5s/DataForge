# 247 — Um validador genérico escrito com reflexão

## O que se pratica

Anotações em campo (`@Obrigatorio`, `@Tamanho(3, 20)`), `Reflexo.campos`,
`ler`/`escrever`/`invocar` por nome, `sugerir` e `diagrama`.

## O que este exercício ensina que não é óbvio

**1. Em campo, o decorador é anotação.** `@Tamanho(3, 20)` não embrulha
nada — não há valor para embrulhar na declaração. Ele grava nome e
argumentos, e quem precisa lê: aqui, o validador.

**2. O validador não conhece `Usuario`.** Ele pergunta ao tipo o que o
tipo declara. É assim que ORM, serializador e formulário são escritos uma
vez para todos os modelos — e é por isso que reflexão existe.

**3. Saber que existe não é poder ler.** `R.campos` lista `senha` com a
visibilidade ao lado, porque isso é documentação. `R.ler(u, "senha")` é
recusado exatamente como `u.senha` seria: se a reflexão abrisse o que o
autor fechou, `private` seria só uma sugestão para quem não conhece o
módulo — e é justamente quem conhece que precisa ser contido.

**4. Reflexão custa.** Cada leitura por texto passa pela busca completa
de membro, visibilidade e ganchos. Use em framework e ferramenta; no laço
quente, escreva `u.nome`.

## Para ir além

- Acrescente `@Formato("email")` e valide com `Arcane.Regex`.
- Gere o formulário HTML de `Usuario` a partir das mesmas anotações.
