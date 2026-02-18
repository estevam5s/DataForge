# TYPES.md

## Especificação Oficial de Tipos — Linguagem DataForge

> **Status**: Draft v1.0
> **Escopo**: Definição oficial do sistema de tipos da linguagem DataForge
> **Objetivo**: Estabelecer um sistema de tipos mais rico, explícito e semântico que Python, focado em análise de dados, estatística avançada e engenharia de dados.

---

## 1️⃣ Filosofia do Sistema de Tipos

O sistema de tipos da DataForge segue os princípios:

* Tipos **semânticos**, não apenas estruturais
* Tipos como **contratos de dados**
* Tipos explícitos para reduzir erros em pipelines
* Integração total com tipos Python
* Suporte a imutabilidade, lazy evaluation e composição funcional

> Em DataForge, tipos são **ferramentas de clareza**, não burocracia.

---

## 2️⃣ Tipos Primitivos

| Tipo      | Descrição           |
| --------- | ------------------- |
| `Void`    | Ausência de valor   |
| `Boolean` | Verdadeiro ou falso |
| `String`  | Texto Unicode       |
| `Char`    | Caractere único     |
| `Bytes`   | Dados binários      |

---

## 3️⃣ Tipos Numéricos Avançados

### 3.1 Inteiros

```
Int8, Int16, Int32, Int64
UInt8, UInt16, UInt32, UInt64
BigInt
```

### 3.2 Ponto Flutuante e Precisão

```
Float32
Float64
Decimal
Ratio
```

### 3.3 Constantes Numéricas

```
PI, E, TAU, INF, NAN
MAX_INT, MIN_INT
```

---

## 4️⃣ Tipos de Coleção

| Tipo          | Descrição        |
| ------------- | ---------------- |
| `List<T>`     | Lista ordenada   |
| `Set<T>`      | Conjunto único   |
| `Map<K,V>`    | Mapa chave-valor |
| `Tuple<T...>` | Estrutura fixa   |
| `Frozen<T>`   | Coleção imutável |

---

## 5️⃣ Tipos Funcionais

```
Function
PureFunction
Lazy<T>
Thunk<T>
Partial<T>
Result<Ok, Err>
Option<T>
Either<L, R>
Try<T>
```

Esses tipos permitem:

* Composição segura
* Tratamento explícito de falhas
* Avaliação preguiçosa

---

## 6️⃣ Tipos Estatísticos (Diferencial da Linguagem)

```
Sample
Population
Distribution
NormalDist
UniformDist
BinomialDist
PoissonDist
Histogram
Correlation
RegressionModel
ConfidenceInterval
HypothesisTest
```

Esses tipos encapsulam lógica estatística diretamente na linguagem.

---

## 7️⃣ Tipos Tabulares e Analíticos

```
Series<T>
DataFrame
Column<T>
Row
Schema
Index
Partition
Window
```

Projetados para substituir dependência direta de DataFrames externos.

---

## 8️⃣ Tipos Temporais

```
Date
Time
DateTime
Timestamp
Duration
Interval
TimeWindow
BusinessDay
Timezone
```

Essenciais para dados reais, séries temporais e janelas analíticas.

---

## 9️⃣ Tipos de Pipeline e Engenharia de Dados

```
Pipeline
Stage
Task
Node
Dependency
ExecutionPlan
Checkpoint
Artifact
```

Esses tipos tornam pipelines objetos de primeira classe.

---

## 🔟 Tipos de IO, Dados Externos e Web

```
File
Path
URL
Request
Response
Stream
```

Usados por módulos de ingestão, scraping e APIs.

---

## 1️⃣1️⃣ Tipos de Erro (Tipados)

```
Error
TypeError
ValueError
DataError
SchemaError
StatError
IOError
NetworkError
PipelineError
```

Falhas são valores tipados, não apenas exceções genéricas.

---

## 1️⃣2️⃣ Tipos de Segurança e Infraestrutura

```
Secret
Credential
Token
Encrypted<T>
Hash
Checksum
Vault
```

Projetados para ambientes corporativos e cloud.

---

## 1️⃣3️⃣ Tipos de Configuração e Ambiente

```
Config
Env
Profile
FeatureFlag
Version
```

Permitem execução previsível em múltiplos ambientes.

---

## 1️⃣4️⃣ Tipos Meta (Reflexão da Linguagem)

```
Type
Module
Package
Dependency
Metadata
Annotation
```

Permitem introspecção e tooling avançado.

---

## 1️⃣5️⃣ Integração com Python

Cada tipo DataForge possui:

* Mapeamento para tipo Python equivalente
* Conversão explícita bidirecional
* Fallback para objetos Python quando necessário

Exemplo conceitual:

```
DataFrame <-> pandas.DataFrame
List<T> <-> list
Map<K,V> <-> dict
```

---

## 1️⃣6️⃣ Regras de MVP (v1.0)

Tipos obrigatórios para v1:

* Primitivos
* Numéricos básicos
* List, Map
* DataFrame, Series
* Sample, Distribution
* Pipeline
* Error tipado

---

## 🧠 Conclusão

O sistema de tipos da DataForge é um **diferencial estratégico**, posicionando a linguagem
