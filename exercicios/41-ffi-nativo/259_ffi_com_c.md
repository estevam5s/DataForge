# 259 — chamar C: bibliotecas, ponteiros e callbacks

`adopt Python.numpy` resolve "preciso de uma biblioteca que alguém já
escreveu **em Python**". Faltava o degrau de baixo: chamar uma função de
uma biblioteca **C** — a `libm`, a `libz`, o `.so` que a empresa mantém
há quinze anos — sem escrever módulo de extensão e sem trazer
dependência. `Arcane.C` roda sobre o `ctypes`, que é da biblioteca padrão
do Python: nada é instalado e nada é compilado.

## A assinatura é declarada, e isso é o recurso

```dataforge
libm := C.matematica()
raiz := libm.funcao("sqrt", ["f64"], "f64")
assert raiz(16.0) is 4.0
```

Adivinhar o tipo erra fora do caso comum, e erra **calado**: um `i32`
onde o C espera `i64` passa em quase toda chamada e corrompe memória no
resto — longe da linha que causou. Declarar é o que impede isso.

A lista é fechada (`i8`…`i64`, `u8`…`u64`, `f32`, `f64`, `bool`, `char`,
`texto`, `bytes`, `ponteiro`, `tamanho`, `void`), e um tipo inventado é
recusado **com a lista**, em vez de virar um endereço qualquer.

## Os dois erros que FFI sempre tem

Biblioteca que não abre e símbolo que não existe. Os dois chegam do
sistema ilegíveis (`OSError: dlopen(…) no such file`), e aqui os dois
dizem o nome, onde foi procurado e o caminho de saída — por sistema
operacional. `lib.tem(nome)` deixa perguntar antes de tentar.

## O layout é a parte que ninguém acerta de cabeça

```dataforge
Mista := C.estrutura([["flag", "i8"], ["valor", "i32"]])
assert Mista.tamanho() is 8              // e nao 5
assert Mista.deslocamentos()["valor"] is 4
```

Tamanho, alinhamento e deslocamento vêm da ABI da plataforma. É o que
quebra quando a struct do C muda de campo — e o que não dá para conferir
lendo o cabeçalho de cabeça.

## Ponteiro é um endereço COM TIPO

O tipo não é decoração: é ele que diz quanto `deslocar(1)` anda e como
`ler()` interpreta os bytes. `deslocar_bytes(n)` existe para quando o
passo não é o tipo, e `como(tipo)` é o cast.

Só uma conferência é feita, e ela é a que vale o custo: **ponteiro
nulo**. Ler um endereço nulo derruba o processo, e a pilha que sobra não
fala do DataForge. O resto da segurança de memória, em FFI, é de quem
chama — e o módulo não finge o contrário.

Para não depender de disciplina, junte com `Arcane.Posse`:

```dataforge
P.com(P.dono(C.alocar(32), lambda b => C.liberar(b)),
      lambda bloco => bloco.tamanho())
```

O bloco sai no fim do escopo, **inclusive quando o corpo falha**.

## O C chamando uma ação sua

Metade das bibliotecas C úteis pede um ponteiro de função: `qsort` pede o
comparador, a libcurl pede o recebedor, a libz pede o alocador.

```dataforge
comparador := C.retorno_de_chamada(comparar, ["ponteiro", "ponteiro"], "i32")
qsort(area, 4, C.tamanho_de("i32"), comparador)
```

O `qsort` do C chama uma ação escrita em DataForge e ordena memória crua
com o resultado.

O **tempo de vida** é explícito (`vivo()`, `soltar()`) por um motivo
concreto: um callback coletado no meio de um `qsort` derruba o processo.
Um objeto que se segura é o que impede isso, e `vivo()` é o que permite
perguntar em vez de descobrir.

## O que NÃO existe — e por quê

- **binding automático a partir de `.h`**: não há leitor de cabeçalho. A
  assinatura é escrita à mão, e essa é a conferência.
- **C++ com nome decorado**: o *name mangling* não é estável entre
  compiladores. Só `extern "C"`.
- **`stdcall` do Windows**: só a convenção padrão.
- **bloco `unsafe`**: não há bloco a marcar — o módulo inteiro é a
  fronteira insegura, e a documentação diz isso em vez de espalhar uma
  palavra pelo código.
