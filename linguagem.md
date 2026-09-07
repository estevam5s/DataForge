> ⚠️ **DOCUMENTO HISTÓRICO — não reflete a implementação atual.**
>
> Documento de **requisitos e planejamento**, não de comportamento atual. O que falta implementar de fato está em `doc/ANALISE_E_ROADMAP.md`.
>
> **Documentação vigente:** [`doc/TUTORIAL.md`](doc/TUTORIAL.md) · [`doc/REFERENCIA.md`](doc/REFERENCIA.md) · [`doc/BIBLIOTECA_PADRAO.md`](doc/BIBLIOTECA_PADRAO.md) · [`doc/INSTALACAO.md`](doc/INSTALACAO.md)

---

# DataForge

## Documento de Requisitos para Adição de Conteúdos à Linguagem

> **Objetivo deste documento**
>
> Definir **tudo o que é necessário adicionar, implementar ou planejar** para a evolução da linguagem DataForge, considerando bibliotecas nativas, integração com Python, módulos externos (como web scraping) e boas práticas de engenharia de linguagens.

---

## 1️⃣ Requisitos do Core da Linguagem

Esses itens são **obrigatórios** para qualquer evolução da linguagem e fazem parte da sua identidade.

### 1.1 Sintaxe e Semântica

* Definição formal da gramática
* Operador de pipeline (`>>`)
* Escopo de variáveis
* Imutabilidade opcional
* Avaliação lazy e eager

### 1.2 Sistema de Tipos

* Tipos primitivos (`Number`, `String`, `Boolean`, `Null`)
* Estruturas (`Array`, `Map`)
* Tipos tabulares (`Series`, `DataFrame`)
* Tipos estatísticos (`Sample`, `Distribution`)

### 1.3 Tratamento de Erros

* Erros semânticos
* Erros de pipeline
* Erros estatísticos
* Mensagens claras e rastreáveis

---

## 2️⃣ Requisitos de Bibliotecas Nativas (Oficiais)

Essas bibliotecas **devem ser mantidas junto com a linguagem**.

* Parser
* AST
* Runtime
* Executor de pipelines
* Criação e manipulação de DataFrames
* Operações vetorizadas
* GroupBy e aggregations
* Estatística descritiva
* Estatística inferencial
* Distribuições
* Amostragem
* Orquestração
* Dependências
* Reexecução parcial
* CSV
* JSON
* Parquet
* Excel

### 📦 dataforge.db

* SQLite nativo
* Conectores SQL
* ORM leve

---

## 3️⃣ Requisitos de Integração com Python

A linguagem **deve integrar e não competir** com Python.

### 3.1 Bibliotecas Python Essenciais

* NumPy (backend matemático)
* Pandas (interop de DataFrames)
* SciPy (estatística avançada)
* Scikit-learn (ML clássico)

### 3.2 Execução Híbrida

* Importação de módulos Python
* Conversão de tipos DataForge ↔ Python
* Extensões customizadas

---

## 4️⃣ Requisitos para Web Scraping e Dados Externos 🌐

Web scraping **não é core**, mas é um módulo oficial importante.

### 📦 dataforge.web

Funcionalidades necessárias:

* Requisições HTTP
* Parsing HTML
* Extração estruturada
* Conversão para DataFrame

Dependências Python:

* requests
* beautifulsoup4
* lxml

---

## 5️⃣ Requisitos para APIs e Integrações

### 📦 dataforge.api

* Consumo de APIs REST
* Autenticação (Token / OAuth básico)
* Paginação
* Rate limit handling

---

## 6️⃣ Requisitos para Engenharia de Dados (ETL)

### 📦 dataforge.etl

* Extract: arquivos, bancos, APIs
* Transform: limpeza, normalização, enriquecimento
* Load: bancos SQL, Data Lakes

---

## 7️⃣ Requisitos para Machine Learning

### 📦 dataforge.ml

* Regressão (linear, múltipla)
* Clustering (K-Means)
* Avaliação de modelos

Backend obrigatório:

* Scikit-learn

---

## 8️⃣ Requisitos para Visualização de Dados

### 📦 dataforge.viz

* Gráficos estatísticos
* Histogramas
* Boxplots

Backends:

* Matplotlib
* Plotly

---

## 9️⃣ Requisitos de Utilitários e Infraestrutura

### 📦 dataforge.utils

* Logging
* Configuração
* Variáveis de ambiente
* Cache

---

## 🔟 Requisitos de Qualidade e Engenharia

Esses itens **não são features**, mas são obrigatórios.

* Testes automatizados
* Benchmarks
* Documentação clara
* Exemplos reais
* Versionamento semântico

---

## 1️⃣1️⃣ Requisitos que NÃO devem entrar agora

Decisão estratégica para manter foco:

* Deep Learning
* Streaming pesado (Kafka)
* Orquestração enterprise (Airflow)
* Frontend/UI

---

## 🧠 Conclusão

Este documento define **o que precisa ser adicionado, mantido ou planejado** para a evolução consistente da linguagem DataForge, garantindo foco, maturidade técnica e crescimento sustentável.


## Adicionar mais conteudos

* Rapida execucao de codigos
* Modo debuger
* Operadores (Comparadores, Booleanos, Matematicos)
* Bibliotecas avancadas
* Bibliotecas de calculos matematicos
* Melhorar o prompt iteraticos
* Criacao de apps Desktops igual ao TKinter, mas voltados para a area de dados
* Modo debuger
* Visao computacional
* Tipos de dados (numericos, boolenaos, (str, tuple, list, etc ...), conjuntos, mapeamentos, dicionarios)
* Tratamento de erros
* Arquivos
* Adicione mais conteudos, bibliotecas, automacoes, SOLID, DDD, TDD, Padroes de projetos, codigo no terminal para criar ja um template de projeto (tem que ter cores no terminal e dizer qual tipo de projeto, seja ele API Rest, dados da area analise de dados), colocar mais conteutos sobre objetos, metodos, metodos de classe, servidor http para rodar como um flask, tudo isso para a essa linguagem.
* Metodos no terminal com o comando criar projetos a essa linguagem
* Tipos numericos:
    Int8, Int16, Int32, Int64
    UInt8, UInt16, UInt32, UInt64
    Float32, Float64
    Decimal
    BigInt
    Ratio
* Tipos Estatísticos (grande diferencial):
    Sample
    Population
    Distribution
    NormalDist
    UniformDist
    BinomialDist
    PoissonDist
    TimeSeries
    Histogram
    Correlation
    RegressionModel
* Tipos de Dados Tabulares e Analíticos:
    Series
    DataFrame
    Column
    Schema
    Row
    Index
    Partition
    Window
* Tipos Temporais Avançados (muito além de datetime):
    Date
    Time
    DateTime
    Timestamp
    Duration
    Interval
    TimeWindow
    BusinessDay
    Timezone
* Tipos de Pipeline e Engenharia de Dados (exclusivo):
    Pipeline
    Stage
    Task
    Node
    Dependency
    ExecutionPlan
    Checkpoint
    Artifact
* Tipos Funcionais (forte diferencial técnico):
    Function
    PureFunction
    Effect
    Lazy
    Thunk
    Result
    Option
    Either
    Try
* Tipos de Segurança e Infraestrutura:
    Secret
    Credential
    Token
    Encrypted
    Hash
    Checksum
    Vault
* Tipos de Configuração e Ambiente:
    Config
    Env
    Profile
    FeatureFlag
* Tipos Meta (linguagem refletiva):
    Type
    Module
    Package
    Version
    Dependency
    Metadata
    Annotation

## Extensao ao VSCODE

* Deve criar uma extensao ao vscode que indentifique:

    1. Sintaxe
    2. Cores para palavras reservadas
    3. Identacao
    4. Execucao direta ao navegador
    5. Adicionar icones ao arquivo .df