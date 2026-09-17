# 241 — O quadro, e os seis verbos do pipeline

## O que se pratica

Carregar um conjunto com ausência, olhar antes de calcular, filtrar,
agrupar, resumir, limpar e juntar — sem sair da linguagem.

## O que este exercício ensina que não é óbvio

**1. `perfil()` vem antes de qualquer conta.** Uma média sobre dados com
buraco não avisa que tinha buraco: ela só sai menor. Conferir a contagem
de ausentes primeiro é o passo que separa um relatório de um chute.

**2. A ausência não passa no filtro, e isso é de propósito.**
`>> onde valor bigger 50` deixa de fora a linha cujo `valor` é `void` —
comparar com o desconhecido não dá nem sim nem não. É a lógica de três
valores do SQL, e a de toda ferramenta de dados que existe.

A outra escolha — levantar erro — é o que a linguagem faz em toda
expressão comum, e está certa lá. Aqui tornaria o verbo inutilizável:
todo conjunto real tem ausência, e o primeiro `onde` de todo programa
morreria na primeira linha vazia. Quem **quer** a ausência pergunta por
ela: `onde valor is void`.

**3. Dentro de um `onde`, um nome nu é uma COLUNA.** E o escopo de fora
continua alcançável para tudo o que não for coluna — um limite guardado
numa variável funciona em `onde valor bigger limite`. Sem essa regra, o
mesmo código leria de dois jeitos conforme o que houvesse no escopo.

**4. `contagem` e `contagem_valida` respondem perguntas diferentes.**
Quantas linhas há, e quantas têm valor. Num conjunto com ausência,
confundir as duas troca a média — e o erro não aparece em lugar nenhum.

**5. Nada no `cycle`, no `len` ou no `>>` sabe o que é um quadro.** Eles
funcionam porque iterar um quadro dá **linhas como vault** — o mesmo
protocolo que faz a ponte para o Python funcionar sem conversão. Se
alguém um dia trocar protocolo por tipo, isso quebra inteiro.

**6. Todo verbo devolve um quadro novo.** Como `record` e `with`: o
original nunca muda. É o que permite comparar o antes e o depois, e o que
torna um pipeline reexecutável.

## Para ler depois

- [O Quadro](https://dataforge-lang.vercel.app/docs/dados/quadro)
- [Os verbos do pipeline](https://dataforge-lang.vercel.app/docs/dados/verbos)
- [O mapa do ecossistema de dados](https://dataforge-lang.vercel.app/docs/dados/mapa)
