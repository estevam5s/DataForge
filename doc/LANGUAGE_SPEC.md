> ⚠️ **DOCUMENTO HISTÓRICO — não reflete a implementação atual.**
>
> Rascunho **descartado**: descreve uma sintaxe (`let x: Int32 = 10`, `fn`, `pipeline main { }`) que **não** é a da linguagem implementada. Mantido apenas como registro histórico de uma direção que não foi seguida.
>
> **Documentação vigente:** [`doc/TUTORIAL.md`](doc/TUTORIAL.md) · [`doc/REFERENCIA.md`](doc/REFERENCIA.md) · [`doc/BIBLIOTECA_PADRAO.md`](doc/BIBLIOTECA_PADRAO.md) · [`doc/INSTALACAO.md`](doc/INSTALACAO.md)

---

# LANGUAGE_SPEC.md

## Especificação Oficial da Linguagem DataForge

> **Status**: Draft v1.0
> **Categoria**: DSL para Análise de Dados e Estatística Avançada
> **Base**: Python 3 Runtime
> **Paradigmas**: Declarativo, Funcional, Orientado a Dados

---

## 1️⃣ Visão Geral da Linguagem

DataForge é uma linguagem de programação especializada (DSL) voltada para:

* Análise de dados
* Estatística avançada
* Engenharia de dados
* Pipelines analíticos

A linguagem prioriza:

* Clareza semântica
* Segurança em pipelines
* Expressividade estatística
* Integração total com Python

---

## 2️⃣ Princípios de Design

* Pipelines como cidadãos de primeira classe
* Tipos explícitos e semânticos
* Falhas são valores (não exceções implícitas)
* Funções puras por padrão
* Imutabilidade incentivada
* Leitura humana acima de otimizações prematuras

---

## 3️⃣ Estrutura Básica de um Programa

```dataforge
use dataforge.stats
use dataforge.frame

pipeline main {
    load "data.csv"
    >> clean
    >> analyze
    >> export "output.parquet"
}
```

---

## 4️⃣ Sintaxe Léxica

### 4.1 Comentários

```dataforge
// comentário de linha
/* comentário de bloco */
```

### 4.2 Identificadores

* Letras, números e `_`
* Não iniciam com número
* Case-sensitive

---

## 5️⃣ Tipos e Declarações

### 5.1 Declaração de Variáveis

```dataforge
let x: Int32 = 10
let name: String = "DataForge"
```

### 5.2 Inferência de Tipos

```dataforge
let y = 42
```

---

## 6️⃣ Funções

### 6.1 Funções Puras

```dataforge
fn square(x: Number): Number {
    return x * x
}
```

### 6.2 Funções Lambda

```dataforge
let inc = |x| => x + 1
```

---

## 7️⃣ Pipelines (Elemento Central)

```dataforge
pipeline etl {
    extract("api")
    >> transform
    >> validate
    >> load("db")
}
```

Regras:

* `>>` representa fluxo de dados
* Cada estágio recebe e retorna dados tipados

---

## 8️⃣ Controle de Fluxo

### 8.1 Condicionais

```dataforge
if x > 0 {
    positive()
} else {
    negative()
}
```

### 8.2 Loops (controlados)

```dataforge
for item in data {
    process(item)
}
```

---

## 9️⃣ Tipos Estatísticos — Sintaxe

```dataforge
let sample = Sample(data)
let mean = sample.mean()
let ci = sample.confidence_interval(0.95)
```

---

## 🔟 Tratamento de Erros Tipados

```dataforge
fn parse(input: String): Result<DataFrame, ParseError> {
    ...
}
```

Uso:

```dataforge
match result {
    Ok(df) => analyze(df)
    Err(e) => log(e)
}
```

---

## 1️⃣1️⃣ Integração com Python

```dataforge
py import pandas as pd

let df = py.call(pd.read_csv, "file.csv")
```

Conversão automática entre tipos compatíveis.

---

## 1️⃣2️⃣ Módulos e Imports

```dataforge
use dataforge.web
use dataforge.etl
```

---

## 1️⃣3️⃣ Gramática Simplificada (EBNF)

```ebnf
program        = { statement } ;
statement      = var_decl | fn_decl | pipeline_decl | expr ;
var_decl       = "let" identifier [ ":" type ] "=" expr ;
fn_decl        = "fn" identifier "(" params ")" [ ":" type ] block ;
pipeline_decl  = "pipeline" identifier block ;
expr           = literal | identifier | call | pipeline_expr ;
pipeline_expr  = expr ">>" expr ;
```

---

## 1️⃣4️⃣ Regras de Execução

* Execução determinística
* Avaliação lazy em pipelines
* Side effects isolados
* Logs estruturados

---

## 1️⃣5️⃣ Arquivos e Extensão

* Arquivos DataForge usam extensão `.df`
* Podem ser compilados ou interpretados

---

## 🧠 Conclusão

Esta especificação define a **sintaxe, gramática e princípios fundamentais** da linguagem DataForge, servindo como base para implementação do parser, runtime, tooling e documentação oficial.

---

**Documento vivo — sujeito a evolução conforme a linguagem amadurece.**
