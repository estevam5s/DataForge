# Exercicio 235 — Dados binários com `Arcane.Bytes`

## Enunciado

Monte e leia um cabeçalho de protocolo, byte a byte.

## O que faltava

A linguagem tem o tipo `Bytes`, e não havia o que fazer com ele. Ler um arquivo
binário, falar um protocolo, montar um cabeçalho de quatro bytes — tudo isso
pedia sair da linguagem.

## A ordem dos bytes é obrigatória

```dataforge
Bytes.empacotar("i32", 1)      // recusado
Bytes.empacotar(">i32", 1)     // 00 00 00 01   ordem de rede
Bytes.empacotar("<i32", 1)     // 01 00 00 00   ordem do Intel
```

Um padrão silencioso aqui seria a pior decisão possível: um inteiro escrito na
ordem da **máquina** e lido na ordem da rede dá um número diferente, o programa
**não falha**, e o dado sai errado do outro lado.

Isso não aparece em teste — a máquina que escreve e a que lê são a mesma. Ele
aparece no dia em que o servidor muda de arquitetura, ou no dia em que alguém
lê o arquivo em outro lugar.

## Os nomes dizem o tamanho

`i32` é um inteiro de 32 bits em qualquer máquina. O `int` do C não é, e
descobrir isso depois de gravar um arquivo é caro.

| Escrita | O quê | Bytes |
|---------|-------|-------|
| `i8` `u8` | inteiro de 8 bits, com e sem sinal | 1 |
| `i16` `u16` | 16 bits | 2 |
| `i32` `u32` | 32 bits | 4 |
| `i64` `u64` | 64 bits | 8 |
| `f32` `f64` | ponto flutuante | 4 / 8 |
| `bool` | verdadeiro ou falso | 1 |
| `bytesN` | um bloco de tamanho fixo | N |

## O cursor anda sozinho

Ler com fatias exige calcular o deslocamento de cada campo:

```dataforge
versao := dados[0]
tipo := dados[1]
tamanho := dados[2:6]      // e aqui já é preciso lembrar que u32 são 4 bytes
```

Um erro num deles **desalinha tudo o que vem depois** — e o pior é que o
programa não quebra: ele entrega números plausíveis e errados.

```dataforge
leitor := Bytes.ler(mensagem)
versao := leitor.ler("u8")
tipo := leitor.ler("u8")
tamanho := leitor.ler("u32")
corpo := leitor.resto()
```

E ler além do fim diz **quanto falta**:

```
faltam bytes para ler 'u32': o cursor está em 1, o campo pede 4
e só há 1 até o fim.
```

## O despejo

É o que se olha quando o protocolo não bate — posição, hexadecimal e o texto
legível, lado a lado:

```
00000000  01 07 00 00 04 00 44 61 74 61 46 6f 72 67 65     |......DataForge|
```

É assim que se vê o byte a mais que desalinhou tudo.

## Segredo se compara em tempo fixo

```dataforge
Bytes.igual_em_tempo_fixo(token_recebido, token_certo)
```

Uma comparação comum para no **primeiro byte diferente**, e o tempo conta
quantos bateram. Com isso, um atacante descobre um token byte a byte, sem
nunca precisar acertá-lo inteiro por sorte.

## A janela não copia

Copiar um arquivo de 200 MB para ler 8 bytes é o jeito mais fácil de estourar
a memória. `Bytes.janela` aponta para os mesmos bytes; `Bytes.copiar` só é
chamado quando o pedaço precisa mesmo ser guardado.

## Saída esperada

```
01 07 00 00 04 00
v1 tipo=7 tamanho=1024 corpo=DataForge
00000000  01 07 00 00 04 00 44 61 74 61 46 6f 72 67 65     |......DataForge|
235 ok
```

## Para experimentar

- Troque `>u32` por `<u32` e veja o `1024` virar `262144`.
- Leia um campo a mais que o bloco tem, e leia a mensagem de erro.
- Monte um cabeçalho, mande por TCP (exercício 236) e leia do outro lado.
