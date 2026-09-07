# Exercicio 164 — Arquivos e diretórios

## Enunciado

Leia, escreva e organize arquivos com `Arcane.IO`.

## Texto

```dataforge
IO.write(caminho, texto)      // cria ou substitui
IO.append(caminho, texto)     // acrescenta ao fim
IO.read(caminho)              // devolve o conteúdo
```

Para trabalhar linha a linha, `.lines()` da própria string:

```dataforge
cycle linha in IO.read("dados.txt").lines():
    processar(linha)
```

Para arquivos grandes, prefira um `stream action` que emite linha por linha —
`IO.read` carrega tudo na memória.

## Formatos estruturados

```dataforge
IO.write_json(caminho, vault)     IO.read_json(caminho)
IO.write_csv(caminho, linhas)     IO.read_csv(caminho)
```

Fazem a serialização e a escrita numa chamada só, e é o que você quer na maioria
dos casos.

## Caminhos

```dataforge
IO.join(pasta, "arquivo.txt")     // monta com o separador certo
IO.basename(caminho)              // "notas.txt"
IO.dirname(caminho)               // a pasta
IO.ext(caminho)                   // ".txt"
IO.abs(caminho)                   // caminho absoluto
```

**Sempre use `IO.join`** em vez de concatenar com `"/"`. O separador muda entre
sistemas, e concatenar à mão é a forma mais rápida de escrever código que só
funciona na sua máquina.

## Diretórios

```dataforge
IO.mkdir(pasta)          // cria, inclusive os níveis intermediários
IO.list_dir(pasta)       // os nomes dentro dela
IO.exists(caminho)       // arquivo ou pasta
IO.file_exists(caminho)  // só arquivo
```

## Copiar, renomear, apagar

```dataforge
IO.copy(origem, destino)
IO.rename(antigo, novo)
IO.delete(caminho)
```

`rename` também **move** entre pastas — é a mesma operação no sistema de arquivos.

## Filtrar por extensão

```dataforge
textos := IO.list_dir(pasta) >> sift nome: nome.endswith(".txt")
```

`list_dir` devolve uma lista comum, então todo o pipeline funciona sobre ela.

## Limpeza garantida

Este exercício apaga o que criou. Num programa real, use `defer` para garantir
isso mesmo se algo falhar no meio:

```dataforge
action processar():
    IO.mkdir(temp)
    defer:
        limpar(temp)
    // ... o defer roda mesmo se isto disparar
```

## Saída esperada

```
lidas 3 linhas
tamanho: 47 bytes

nome:      notas.txt
pasta:     _exercicio_164
extensao:  .txt

config lida: {tema: escuro, fonte: 14, plugins: [a, b]}
csv tem 3 linhas

na pasta: [config.json, dados.csv, notas.txt]

arquivos .txt: 2

tudo limpo
```

## Experimente

- Escreva `action tamanho_da_pasta(p)` somando o tamanho de todos os arquivos.
- Faça um backup que copia só os arquivos alterados.
