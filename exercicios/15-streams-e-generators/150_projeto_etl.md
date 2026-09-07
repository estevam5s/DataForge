# Exercicio 150 — Projeto: ETL com streams

## Enunciado

Monte um pipeline completo de **E**xtração, **T**ransformação e **C**arga usando
generators encadeados.

## A arquitetura

```
extrair()  →  separar()  →  limpar()  →  validar()  →  observe
   ↓             ↓            ↓            ↓             ↓
 origem      estrutura    normaliza     verifica     carrega
```

Cada estágio é um `stream action` que consome o anterior. A linha que monta tudo:

```dataforge
observe registro in validar(limpar(separar(extrair()))):
```

Nada roda até o `observe` pedir o primeiro item. Depois, cada linha atravessa os
quatro estágios individualmente.

## Um estágio, uma responsabilidade

| Estágio | Faz | Não faz |
|---------|-----|---------|
| `extrair` | produz linhas brutas | não interpreta |
| `separar` | quebra em campos | não limpa |
| `limpar` | normaliza caixa e espaços | não valida |
| `validar` | verifica e converte tipos | não decide o destino |

Essa separação não é preciosismo. Quando o formato de entrada mudar de CSV para
JSON, só `separar` muda. Quando a regra de e-mail mudar, só `validar` muda.

## Erros que atravessam o pipeline

O ponto mais delicado de um ETL: **uma linha ruim não pode derrubar as outras**.

A solução aqui é fazer o erro viajar como um dado:

```dataforge
emit {"__erro__": $"campos de menos: '{linha.trim()}'"}
```

Cada estágio seguinte reconhece o marcador e o repassa intacto:

```dataforge
match item:
    point {"__erro__": e}:
        emit item              // passa adiante sem tocar
    point [nome, email, ...]:
        emit {...}             // processa normalmente
```

No fim, o consumidor separa os dois fluxos. Ninguém perde dado e ninguém para o
processamento por causa de uma linha torta.

Um `monitor` em volta de tudo não resolveria: ele abortaria o pipeline inteiro na
primeira linha ruim.

## Normalizar na entrada

```dataforge
"nome": nome.trim().title(),        // "  ANA SILVA " → "Ana Silva"
"email": email.trim().lower(),      // " ana@Exemplo.COM " → "ana@exemplo.com"
```

Dados de fora chegam sujos. Limpar **uma vez**, na fronteira, evita ter que
lembrar disso em cada consulta depois.

## Converter só depois de validar

```dataforge
given not registro["idade"].isdigit():
    problemas.append("idade nao numerica")
...
"idade": cast registro["idade"] as Integer
```

A ordem importa: `cast "abc" as Integer` dispara erro. Verificar primeiro
transforma uma exceção num registro rejeitado com mensagem clara.

## Saída esperada

```
── carregados ──
  Ana Silva    vendas   R$ 5500
  Bruno Costa  ti       R$ 7200
  Carla Dias   vendas   R$ 9100

── rejeitados ──
  campos de menos: 'linha malformada'
  Diego Alves: email invalido
  Elena Rocha: idade nao numerica

── por setor ──
  vendas   n=2  media=R$ 7300.0
  ti       n=1  media=R$ 7200.0

folha total: R$ 21800
aproveitamento: 3/6
```

## Experimente

- Acrescente um estágio `deduplicar` que descarta e-mails repetidos.
- Grave os rejeitados num CSV com `Serde.records_to_csv`.
- Faça `extrair` ler de um arquivo real com `IO.read(...).lines()`.
