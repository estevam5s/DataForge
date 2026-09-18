# 256 — Posse, empréstimo e liberação determinística

Num mundo com coletor, **vazar memória quase nunca é o problema**. O que
o coletor não resolve é o **recurso**: o arquivo que não fecha, a conexão
que fica aberta, o cadeado que ninguém solta — porque ele não promete
*quando* passa.

## O que cada peça garante

| Peça | Garante | Equivale a |
|---|---|---|
| `P.dono(v, ao_soltar)` | um dono, um finalizador, uma vez | `Box` / `unique_ptr` |
| `P.com(dono, acao)` | solta no fim, **inclusive no erro** | RAII / `with` |
| `P.celula(v)` | muitos leem **ou** um escreve | `RefCell` |
| `P.compartilhado(v)` | solta quando o **último** sai | `Rc` |
| `P.atomico(v)` | o mesmo, válido entre threads | `Arc` |
| `P.fraco(c)` | observa sem segurar | `Weak` |

## Quem move, perde

`a.mover()` transfere a posse: `a` fica movido, e usá-lo é erro — com a
linha em que o valor saiu. Perguntar o **estado** (`a.movido()`,
`a.vivo()`) continua valendo: é exatamente o que se pergunta depois de
mover.

O `dataforge check` acusa isso **antes de rodar** (`posse-movida`) quando
o fluxo do arquivo permite provar. Ele só olha nomes que nasceram de
`Arcane.Posse`: um blueprint com um método chamado `mover` não tem nada a
ver com posse, e acusá-lo seria o falso alarme que ensina a desligar o
analisador.

## Cópia não é clone

- `copiar()` — outro dono do **mesmo** valor. É o que se quer quando o
  valor *é* o recurso (uma conexão).
- `clonar()` — outro dono de uma **cópia**. É o que se quer quando o
  valor é o dado.

Confundir os dois é como confundir `=` com `copy.deepcopy`: funciona até
o dia em que alguém escreve na sua lista.

## O empréstimo tem escopo

O valor é entregue ao corpo de `usar`, `mudar`, `ler` ou `escrever` — e
vale enquanto esse corpo roda. Pedir o valor **fora** de um corpo
(`emprestar()`) devolve um empréstimo já encerrado, e a mensagem diz por
quê: quem guarda a referência está pedindo o que o dono não controla mais.

É o mesmo efeito prático dos *non-lexical lifetimes*, por um caminho mais
simples: quem entrega sabe exatamente quando o valor volta.

## O ciclo vaza — e isso é mostrado

Dois compartilhados que se apontam com referências **fortes** nunca
chegam a zero, e nenhum finalizador roda. É o problema do `Rc` em
qualquer linguagem. Aqui ele aparece como é, em vez de sumir num
silêncio, e a saída é a de sempre: uma das voltas é fraca.

Quando o de fora solta, o que ele possuía é solto junto (*drop glue*) —
por isso a ordem é `["pai", "filho"]`, e não o contrário.

## O que isto não é

Não é o borrow checker do Rust. Nada aqui vira endereço inválido: o
coletor continua no caminho, e a integridade da memória nunca esteve em
risco. O que a posse protege é o **protocolo** — soltar uma vez, não usar
depois, não escrever no meio da leitura de outro. Não há ponteiro cru,
`unsafe`, lifetime explícito nem escolha entre pilha e heap: essas peças
pertencem a uma linguagem compilada com layout fixo.
