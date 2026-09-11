> ⚠️ **DOCUMENTO HISTÓRICO — não reflete a implementação atual.**
>
> Esta é uma **proposta** de especificação, escrita antes da implementação, e
> ela descreve uma linguagem diferente da que existe. Das 31 palavras
> reservadas que propõe, 23 vêm de Rust ou de JavaScript (`fn`, `let`, `mut`,
> `impl`, `trait`, `match`, `async`, `await`, `struct`, `enum`, …) — e a regra
> deste projeto é que as palavras da DataForge **não saiam de outra linguagem**.
> A promessa de interoperabilidade com a ABI C também não existe.
>
> A referência da linguagem que roda está em `doc/REFERENCIA.md`; o que falta,
> em `doc/ANALISE_E_ROADMAP.md`.

# Especificação Técnica e Manual de Referência Completo: Linguagem de Programação DataForge

---

## 1. Visão Geral da Linguagem & Filosofia de Design

**DataForge** é uma linguagem de programação multiparadigma, compilada/interpretada, de alto desempenho e fortemente tipada, projetada especificamente para manipulação de dados em grande escala, engenharia de dados, computação científica e sistemas orientados a eventos. 

A arquitetura da linguagem foca em três pilares fundamentais:
1. **Expressividade e Sintaxe Limpa:** Sintaxe moderna e minimalista (inspirada em Python, Rust e TypeScript), eliminando redundâncias sem comprometer a clareza visual.
2. **Desempenho e Segurança de Memória:** Execução de alta velocidade através de compilação JIT/AOT em LLVM e gerenciamento híbrido de memória (com foco em zero-cost abstractions).
3. **Imutabilidade e Concorrência Nativa:** Tipos de dados imutáveis por padrão, facilidade para pipelines paralelizados e concorrência orientada a atores e canais.

---

## 2. Sintaxe Básica e Lexicografia

### 2.1 Identificadores e Palavras-Chave
Os identificadores na DataForge seguem o padrão UTF-8 e devem começar com uma letra (`a-z`, `A-Z`) ou underline (`_`), seguidos por letras, dígitos (`0-9`) ou underlines.

#### Palavras-Chave Reservadas:
`let`, `mut`, `const`, `fn`, `struct`, `enum`, `type`, `trait`, `impl`, `if`, `else`, `match`, `for`, `while`, `loop`, `in`, `break`, `continue`, `return`, `async`, `await`, `import`, `export`, `as`, `use`, `pub`, `try`, `catch`, `throw`, `yield`, `pipeline`.

### 2.2 Literais e Delimitadores
* **Números Inteiros:** `42`, `-10`, `0xFF` (Hexadecimal), `0b1010` (Binário), `1_000_000` (Separadores de milhar).
* **Ponto Flutuante:** `3.14159`, `6.022e23`, `1.5f32`, `2.718f64`.
* **Strings e Bytes:** `"Texto padrão UTF-8"`, `r#"String crua (Raw String)"#`, `b"Array de Bytes"`.
* **Interpoladores de String:** `f"Resultado: ${expressao}"`.

---

## 3. Sistema de Tipos Formal (Type System)

DataForge possui um sistema de tipos estático com **inferência de tipos bidirecional**.

```
                           +-------------------+
                           |    Any / Unknown  |
                           +---------+---------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
 +---------+---------+                               +---------+---------+
 |   Tipos Primitivos |                               |   Tipos Compostos  |
 +---------+---------+                               +---------+---------+
 | i8 .. i128, u8..u128|                              | Arrays: [T; N]  |
 | f32, f64          |                               | Slices: [T]     |
 | bool, char, str   |                               | Tuplas: (T1, T2)|
 +-------------------+                               +-------------------+
           |                                                   |
           +-------------------------+-------------------------+
                                     |
                           +---------+---------+
                           |  Algebraic Data   |
                           |  Types (ADT)      |
                           +---------+---------+
                           | Structs & Enums   |
                           +-------------------+
```

### 3.1 Tipos Primitivos
* **Inteiros com sinal:** `i8`, `i16`, `i32`, `i64`, `i128`, `isize`.
* **Inteiros sem sinal:** `u8`, `u16`, `u32`, `u64`, `u128`, `usize`.
* **Ponto Flutuante:** `f32`, `f64`.
* **Booleano:** `bool` (`true`, `false`).
* **Texto:** `char` (Caractere Unicode 32-bit), `str` (Slice de string UTF-8).

### 3.2 Tipos Algebraicos de Dados (ADT)

#### Structs
```dataforge
pub struct DataFrameConfig {
    pub name: str,
    mut buffer_size: usize,
    read_only: bool,
}
```

#### Enums com Dados Associados
```dataforge
pub enum DataNode {
    Scalar(f64),
    Vector([f64]),
    Matrix { rows: usize, cols: usize, data: [f64] },
    Empty,
}
```

### 3.3 Generics e Restrições de Traits
```dataforge
fn process_stream<T, Engine>(stream: T, engine: Engine) -> Result<usize, StreamError>
where 
    T: Streamable + Iterable,
    Engine: ComputeEngine<Output = T::Item> 
{
    // Implementação
}
```

---

## 4. Declaração de Variáveis, Mutabilidade e Escopo

Por padrão, todas as associações de variáveis na DataForge são **imutáveis**. A alteração do valor exige a palavra-chave `mut`.

```dataforge
// Imutável (Inferência automática para i32)
let total_records = 5000;

// Mutável com tipagem explícita
let mut processing_status: str = "INITIALIZING";
processing_status = "RUNNING";

// Constantes compiladas (Escopo Global ou Local)
const MAX_PIPELINE_THREADS: usize = 64;
```

### 4.1 Sombreamento de Variáveis (Variable Shadowing)
DataForge permite sombrear variáveis no mesmo escopo ou em subescopos, alterando o tipo ou valor mantendo a imutabilidade posterior.

```dataforge
let raw_input: str = "4096";
let raw_input: i32 = raw_input.parse::<i32>()?; // Transforma str em i32
```

---

## 5. Operadores e Expressões

### 5.1 Tabela de Precedência de Operadores
*(Do nível mais alto de precedência para o mais baixo)*

| Precedência | Operadores | Descrição | Associatividade |
| :--- | :--- | :--- | :--- |
| **1 (Mais Alta)** | `()`, `[]`, `.`, `?` | Acesso, Indexação, Encadeamento, Propagation | Esquerda -> Direita |
| **2** | `!`, `-` (unário), `~`, `&`, `*` | Operadores Unários, Desreferência | Direita -> Esquerda |
| **3** | `*`, `/`, `%` | Multiplicação, Divisão, Resto | Esquerda -> Direita |
| **4** | `+`, `-` | Adição, Subtração | Esquerda -> Direita |
| **5** | `<<`, `>>` | Deslocamento de Bits (Bitwise Shift) | Esquerda -> Direita |
| **6** | `&` | E Lógico Bit a Bit (Bitwise AND) | Esquerda -> Direita |
| **7** | `^` | XOR Bit a Bit | Esquerda -> Direita |
| **8** | `\|` | OU Lógico Bit a Bit (Bitwise OR) | Esquerda -> Direita |
| **9** | `==`, `!=`, `<`, `>`, `<=`, `>=` | Comparações Relacionais | Esquerda -> Direita |
| **10** | `&&` | E Lógico Curtocirquitado (Logical AND) | Esquerda -> Direita |
| **11** | `\|\|` | OU Lógico Curtocirquitado (Logical OR) | Esquerda -> Direita |
| **12** | `|>` | **Operador de Pipeline de Dados** | Esquerda -> Direita |
| **13 (Mais Baixa)**| `=`, `+=`, `-=`, `*=`, `/=` | Atribuições | Direita -> Esquerda |

### 5.2 Operador Especial de Pipeline (`|>`)
Permite o encadeamento funcional de transformações sem aninhamento de chamadas:

```dataforge
let result = raw_dataset
    |> filter(|row| row.status == "ACTIVE")
    |> map(|row| row.calculate_tax())
    |> aggregate_sum();
```

---

## 6. Estruturas de Controle de Fluxo

### 6.1 Condicionais com Expressões
Em DataForge, o `if` é uma expressão que retorna valor:

```dataforge
let capacity_level = if current_load > 85.0 {
    "CRITICAL"
} else if current_load > 50.0 {
    "WARNING"
} else {
    "NORMAL"
};
```

### 6.2 Casamento de Padrões Avançado (`match`)
```dataforge
match node {
    DataNode::Scalar(val) if val > 0.0 => print(f"Escalar Positivo: {val}"),
    DataNode::Vector(ref arr) => print(f"Vetor com {arr.len()} elementos"),
    DataNode::Matrix { rows, cols, .. } => print(f"Matriz {rows}x{cols}"),
    _ => print("Outro formato de nó"),
}
```

### 6.3 Laços de Repetição e Iteradores
```dataforge
// Loop infinito controlado
loop {
    if !poll_events() { break; }
}

// Loop While tradicional
while connection.is_alive() {
    connection.heartbeat();
}

// Loop For sobre Iteradores
for record in dataset.iter() {
    process(record);
}
```

---

## 7. Funções, Lambdas e Closures

### 7.1 Declaração Formal de Funções
```dataforge
pub fn compute_moving_average(data: &[f64], window_size: usize) -> Result<[f64], EngineError> {
    if window_size == 0 || window_size > data.len() {
        return Err(EngineError::InvalidWindowSize);
    }
    
    let mut averages = [f64]::with_capacity(data.len() - window_size + 1);
    // Lógica de cálculo...
    Ok(averages)
}
```

### 7.2 Lambdas e Closures
```dataforge
// Closure com captura de escopo por referência
let multiplier = 2.5;
let scale_vector = |val: f64| -> f64 { val * multiplier };

let transformed = dataset.map(scale_vector);
```

---

## 8. Abstração Orientada a Objetos e Paradigma Funcional

DataForge não utiliza herança clássica baseada em classes. Ela adota **Composição sobre Herança**, estruturada via **Structs** e **Traits** (semelhante ao Rust).

### 8.1 Definição de Traits e Métodos (Polimorfismo)
```dataforge
pub trait Exportable {
    fn to_json(&self) -> str;
    fn to_parquet(&self) -> [u8];
}

struct AnalyticsReport {
    pub id: u64,
    pub metrics: [f64],
}

impl Exportable for AnalyticsReport {
    fn to_json(&self) -> str {
        // Implementação de serialização JSON
        f"{"id": {self.id}}"
    }
    
    fn to_parquet(&self) -> [u8] {
        // Implementação da conversão Parquet
        [0x50, 0x41, 0x52, 0x31] 
    }
}
```

---

## 9. Gerenciamento de Memória, Ciclo de Vida e Segurança

DataForge combina uma abordagem sem coletor de lixo (Garbage Collector) para regiões críticas usando **Ownership & Borrowing** (Propriedade e Empréstimo), com uma região opcional de **Arena Allocation** para grafos de dados temporários.

```
+-----------------------------------------------------------------------+
|                         SISTEMA DE MEMÓRIA                            |
+-----------------------------------------------------------------------+
|  STACK (Pilha)           |  HEAP (Sem GC - Borrow Checker)            |
|  - Tamanho fixo          |  - Sem alocação dupla / sem dangling ptrs |
|  - Tipos primitivos      |  - Ownership único por binding             |
|  - Ponteiros de escopo   |  - Empréstimos mutáveis e imutáveis        |
+-----------------------------------------------------------------------+
|  ARENA ALLOCATOR (Opcional para Processamento de Dados Batch)         |
|  - Alocação em bloco contíguo | Desalocação em massa pós-pipeline     |
+-----------------------------------------------------------------------+
```

### 9.1 Regras do Proprietário (Ownership Rules)
1. Cada valor na DataForge possui uma variável correspondente chamada seu **Proprietário**.
2. Apenas um proprietário pode existir por vez.
3. Quando o proprietário sai do escopo, o valor é desalocado imediatamente (`drop`).

### 9.2 Empréstimo e Referências (Borrowing)
* **Referências Imutáveis:** Múltiplas leituras simultâneas permitidas (`&T`).
* **Referências Mutáveis:** Apenas UMA escrita exclusiva permitida por escopo (`&mut T`).

```dataforge
fn calculate_length(s: &str) -> usize {
    s.len()
} // s sai do escopo, mas o valor original não é destruído pois é uma referência.
```

---

## 10. Concorrência e Paralelismo de Alto Desempenho

DataForge possui suporte nativo para concorrência estruturada, tarefas assíncronas de I/O e paralelismo multicore de dados (Data Parallelism).

### 10.1 Concorrência Assíncrona (`async/await`)
```dataforge
pub async fn fetch_remote_dataset(url: str) -> Result<Dataset, NetworkError> {
    let client = HttpClient::new();
    let response = client.get(url).await?;
    let raw_bytes = response.bytes().await?;
    
    Dataset::from_csv_bytes(raw_bytes)
}
```

### 10.2 Paralelismo de Dados Nativizado (`parallel pipeline`)
```dataforge
import std::parallel::par_iter;

let large_array: [f64] = generate_large_array();

// Execução paralelizada automaticamente em SIMD/Multithreads
let processed: [f64] = large_array
    .par_iter()
    .map(|x| x.sqrt() * 2.0)
    .collect();
```

### 10.3 Comunicação via Canais (Channels)
```dataforge
import std::sync::channel;

let (sender, receiver) = channel::<DataBlock>(100);

spawn async move {
    sender.send(read_next_block()).await.unwrap();
};
```

---

## 11. Biblioteca Padrão (Stdlib) e Manipulação de Dados

A Biblioteca Padrão da DataForge (`std`) é subdividida nos módulos estruturais descritos abaixo:

```
std
├── core (Tipos fundamentais, traços de conversão, primitivas)
├── io (Streams, leitura e escrita de arquivos, buffers)
├── collections (HashMap, BTreeMap, Queue, Vector)
├── dataframe (Motores de computação colunar estilo Arrow)
├── math (Matemática de alta precisão, álgebra linear, estatística)
├── net (Protocolos HTTP, WebSockets, TCP/UDP sockets)
├── sync (Mutex, RwLock, Channels, Atômicos)
└── sys (Chamadas de sistema, variáveis de ambiente, FFI)
```

### Exemplo: Manipulação Nativa de DataFrames
```dataforge
use std::dataframe::DataFrame;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let df = DataFrame::read_parquet("sales_2026.parquet")?;
    
    let summary = df.filter(df["revenue"] > 10000.0)?
                    .group_by(["region", "category"])?
                    .aggregate([
                        df["revenue"].sum().alias("total_revenue"),
                        df["units"].mean().alias("avg_units"),
                    ])?;
                    
    summary.write_csv("summary_report.csv")?;
    Ok(())
}
```

---

## 12. Tratamento de Erros e Diagnóstico

DataForge não utiliza Exceções tradicionais que causam interrupção opaca de controle. Erros são tratados explicitamente usando a Enumeração `Result<T, E>` e o operador de propagação `?`.

```dataforge
pub enum FileReadError {
    NotFound(str),
    PermissionDenied,
    CorruptedData { byte_offset: usize },
}

fn load_config(path: str) -> Result<Config, FileReadError> {
    let file = File::open(path)?; // Retorna FileReadError imediatamente se falhar
    let content = file.read_to_string()?;
    Config::parse(content)
}
```

---

## 13. Arquitetura do Compilador e Internos da VM

O compilador oficial da DataForge (`dfc`) executa em 5 fases contínuas:

```
+------------------+     +------------------+     +------------------+
|  Código-Fonte    | --> | Analisador       | --> | Analisador       |
|  (.df)           |     | Léxico (Lexer)   |     | Sintático        |
+------------------+     +------------------+     +------------------+
                                                           |
                                                           v
+------------------+     +------------------+     +------------------+
| Executável       | <-- | Gerador de       | <-- | Árvore Sintática |
| Binário / LLVM   |     | Código / LLVM IR |     | Abstrata (AST)   |
+------------------+     +------------------+     +------------------+
```

1. **Análise Léxica (Lexer):** Converte a stream de caracteres UTF-8 em uma sequência de Tokens tipados contendo Metadados de Linha e Coluna.
2. **Análise Sintática e Semântica (Parser & Type Checker):** Valida a gramática EBNF, gera a AST, resolve símbolos e executa verificação estática de tipos e verificação de ciclo de vida de empréstimos (Borrow Checker).
3. **Representação Intermediária da DataForge (DF-IR):** Aplica otimizações de nível de domínio (ex: fusão de pipelines de dados, vetorização SIMD).
4. **Geração de LLVM IR:** Traduz o DF-IR otimizado para Representação Intermediária do LLVM.
5. **Compilação Backend:** O LLVM compila o IR para código de máquina nativo (`x86_64`, `aarch64`, `wasm32`).

---

## 14. Interface de Função Estrangeira (FFI)

DataForge possui interoperabilidade bidirecional de custo zero com linguagens compatíveis com a ABI C.

### Importando Funções em C
```dataforge
extern "C" {
    fn openblas_dgemm(
        layout: i32, trans_a: i32, trans_b: i32,
        m: i32, n: i32, k: i32,
        alpha: f64, a: *const f64, lda: i32,
        b: *const f64, ldb: i32,
        beta: f64, c: *mut f64, ldc: i32
    );
}
```

### Exportando Métodos da DataForge para C/Python
```dataforge
#[no_mangle]
pub extern "C" fn dataforge_compute_hash(data: *const u8, len: usize) -> u64 {
    let slice = unsafe { std::slice::from_raw_parts(data, len) };
    std::hash::calculate(slice)
}
```

---

## 15. Ecossistema, Ferramental e Gerenciamento de Pacotes (`forge`)

A linguagem DataForge inclui a ferramenta CLI unificada chamada **`forge`**.

* **`forge new <project>`:** Inicializa a estrutura padrão do projeto.
* **`forge build --release`:** Compila o código com otimizações agressivas (LTO, vectorization).
* **`forge test`:** Executa a suíte integrada de testes unitários e de integração.
* **`forge fmt`:** Formata o código de acordo com o padrão oficial da linguagem.
* **`forge doc`:** Gera a documentação HTML do projeto e dependências automaticamente.

### Arquivo de Manifest de Projeto (`Forge.toml`)
```toml
[package]
name = "analytics_engine"
version = "1.0.0"
authors = ["Desenvolvedor <dev@dataforge.dev>"]
edition = "2026"

[dependencies]
dataforge_arrow = "2.4.0"
serde_json = "1.0.120"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

---

## 16. Exemplo Completo de Aplicação do Mundo Real

Abaixo está um programa completo e executável em DataForge demonstrando pipelines concorrentes, tratamento de erros, tipagem forte e manipulação de arquivos:

```dataforge
import std::io::File;
import std::dataframe::{DataFrame, Series};
import std::async::spawn;
import std::sync::channel;

pub struct ProcessedStats {
    pub total_records: usize,
    pub average_metric: f64,
}

pub async fn process_data_stream(filepath: str) -> Result<ProcessedStats, Box<dyn std::error::Error>> {
    print(f"[INFO] Iniciando processamento do arquivo: {filepath}");
    
    // 1. Carregamento do DataFrame
    let df = DataFrame::read_csv(filepath).await?;
    
    // 2. Validação e Filtragem via Pipeline
    let filtered_df = df
        |> filter(|row| row["status"] == "VALID")
        |> drop_nulls(["metric_value"]);
        
    let record_count = filtered_df.height();
    if record_count == 0 {
        return Err("Nenhum registro válido encontrado para processamento.".into());
    }
    
    // 3. Processamento concorrente das estatísticas
    let (tx, mut rx) = channel::<f64>(1);
    
    let metric_series = filtered_df["metric_value"].clone();
    spawn async move {
        let mean_val = metric_series.mean();
        tx.send(mean_val).await.unwrap();
    };
    
    let avg_result = rx.recv().await.ok_or("Falha ao receber resultado do cálculo.")?;
    
    // 4. Retorno estruturado dos resultados
    Ok(ProcessedStats {
        total_records: record_count,
        average_metric: avg_result,
    })
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let runtime = std::rt::Runtime::new();
    
    runtime.block_on(async {
        match process_data_stream("data_input.csv").await {
            Ok(stats) => {
                print("=== Processamento Concluído com Sucesso ===");
                print(f"Total de Registros: {stats.total_records}");
                print(f"Média Calculada: {stats.average_metric:.4}");
            },
            Err(err) => {
                print(f"[ERRO] Erro crítico no pipeline: {err}");
            }
        }
    });
    
    Ok(())
}
```
