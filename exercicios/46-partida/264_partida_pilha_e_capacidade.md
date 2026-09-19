# 264 — a partida, a pilha e a fronteira de capacidade

Um programa não começa na primeira linha. Antes dela o `comptime` rodou
numa caixa sem E/S, os `adopt` carregaram módulos e as declarações de
topo foram içadas.

Nada disso era **visível** — e "por que a partida demora 400 ms?" não
tinha como ser respondido sem cronometrar à mão.

## As sete fases

```
lexer → parser → comptime → hoisting → adopt → programa → defer
```

Cada uma tem **o que faz escrito ao lado**: uma lista de nomes sem
explicação apodrece, e há teste cobrando o tamanho da descrição.

E cada `adopt` é **cronometrado**. São dois floats por import, num lugar
que roda uma vez — ligar a medida por opção faria ela existir só para
quem já desconfiava, e a pergunta aparece justamente quando ninguém
desconfiava.

## A pilha

O teto é **mil quadros**, e recursão legítima o atinge: uma travessia de
árvore de cinco mil nós não tem nada de infinita. Quem a escreve precisa
saber de quanto é o teto **antes** de bater nele.

`I.pilha()` dá profundidade, limite e quanto falta; `I.quadros()` dá quem
chamou quem.

**Subir o teto é recusado** além do que o Python aguenta: cada chamada
desta linguagem gasta vários quadros do CPython, e um teto alto demais
troca uma mensagem clara ("a recursão passou de mil quadros, e aqui estão
as duas saídas") por um `RecursionError` cru — que não fala desta
linguagem e não diz o que fazer.

As duas saídas continuam sendo as certas: `yield f(…)` como retorno
inteiro vira salto e **não tem teto**, ou um `cycle` com pilha explícita.

## Uma variável por thread

Um armazém por thread resolve metade do problema. A outra metade é o que
costuma faltar: a **inicialização declarada num lugar só**, e o
**finalizador** quando a thread acaba — sem ele, uma conexão aberta por
thread fica aberta depois que ela morre, e o sintoma aparece no servidor,
não no código.

**`inicial` é uma ação, não um valor.** Um valor seria compartilhado por
todas as threads — que é exatamente o que a variável por thread existe
para evitar. Passar um valor é recusado, com esse motivo na mensagem.

E o finalizador roda quando a thread é **coletada**, não no instante em
que ela termina: é o que o Python garante, e prometer precisão maior
seria prometer um gancho que não existe. Para liberar num instante
exato, `Arcane.Posse`.

## A fronteira de capacidade

O `comptime` já recusava `out`, `adopt` e `thread`: é uma fronteira de
capacidade escrita à mão, para um caso só. E o `--plugin=` roda um `.df`
arbitrário do projeto com **todos** os poderes — uma regra de lint que
pode abrir soquete.

`Cap.executar(acao, permissoes)` recusa o `adopt` de um módulo fora da
lista **pelo nome da capacidade que falta**, e não por um erro genérico.

A **ponte para o Python é capacidade própria**, e nunca vem junto: ela
alcança tudo o que o Python alcança, e deixá-la com outra faria o resto
da lista virar enfeite.

Um nome inventado é **recusado com a lista** — um erro de digitação
concederia silenciosamente nada, e a fronteira pareceria mais aberta do que
é.

E `Cap.observar` responde "de que esta ação precisa?": rode com a lista
vazia e leia os negados.

## O limite honesto — e ele é o modelo

**A fronteira não tira o que foi ENTREGUE.** Se você passa o módulo `IO` como
argumento, o código tem `IO`.

Isso **não é um furo: é o modelo**. Numa linguagem de capacidade, poder é
o que se **passa**, não o que está no ar — e é por isso que bloquear o
`adopt` (a autoridade ambiente) é a fronteira certa.

O módulo diz na cara o que não é, e `Cap.limites()` devolve essa lista
em tempo de execução:

- **não é uma caixa contra programa hostil**;
- a lista de módulos é escrita à mão, e um erro nela é um furo;
- contra código malicioso: processo separado, contêiner, ou o sistema
  operacional.

Escrito assim de propósito. Um módulo chamado *Sandbox* que prometesse
contenção seria usado onde não pode ser usado, e a descoberta viria por
incidente.

E a fronteira **se desfaz sempre**, inclusive quando o corpo falha: um
cofre que não se desfizesse travaria o programa inteiro.

## O que NÃO se aplica

- **boot, stack probes, stack guards, stack growth**: quem faz o boot e
  gerencia a pilha é o CPython.
- **thread-local allocators**: quem aloca é o CPython.
- **global constructors** no sentido do C++: não há.
- **overflow de inteiro**: não existe aqui — o inteiro é de precisão
  arbitrária, e uma classe inteira de bug não acontece. O preço é a conta
  ser mais lenta que uma de 64 bits.
