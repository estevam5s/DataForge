# Engenharia de Dados, Análise de Dados e Python

> Guia completo de fundamentos, bibliotecas, ETL, ELT, pipelines, bancos de dados, qualidade, segurança, testes, observabilidade e arquitetura de dados com Python.

---

## Sumário

1. Visão geral
2. Fundamentos de Python
3. Python para Engenharia de Dados
4. Bibliotecas essenciais
5. Análise de dados
6. Estatística
7. ETL e ELT
8. Extração de dados
9. Transformação de dados
10. Carga de dados
11. Pipelines
12. Orquestração
13. Bancos de dados
14. SQL
15. Data Warehouse, Data Lake e Lakehouse
16. Processamento distribuído
17. APIs
18. Streaming
19. Qualidade de dados
20. Testes
21. Segurança
22. Observabilidade
23. Performance
24. Machine Learning aplicado a dados
25. Arquitetura de projetos Python
26. DevOps e CI/CD
27. Projetos práticos
28. Boas práticas
29. Plano de estudos
30. Glossário

---

# 1. Visão geral

## 1.1 O que é Engenharia de Dados?

Engenharia de Dados é a disciplina responsável por construir sistemas confiáveis para:

- coletar dados;
- transportar dados;
- armazenar dados;
- transformar dados;
- validar dados;
- disponibilizar dados;
- monitorar pipelines;
- garantir segurança e governança.

O objetivo é transformar dados brutos em dados confiáveis para aplicações, análises, BI, ciência de dados e inteligência artificial.

## 1.2 O que é Análise de Dados?

Análise de dados consiste em investigar dados para descobrir:

- padrões;
- tendências;
- anomalias;
- relações;
- indicadores;
- oportunidades;
- problemas;
- previsões.

## 1.3 Principais papéis

| Função | Responsabilidade |
|---|---|
| Analista de Dados | Análise e geração de insights |
| Engenheiro de Dados | Plataformas e pipelines |
| Cientista de Dados | Modelos estatísticos e preditivos |
| Engenheiro de ML | Machine Learning em produção |
| Engenheiro de Analytics | Camadas analíticas |
| Analista de BI | Dashboards e indicadores |

## 1.4 Fluxo geral

```text
Fontes
  |
  v
Extração
  |
  v
Dados Brutos
  |
  v
Transformação
  |
  v
Validação
  |
  v
Armazenamento
  |
  +--> Data Warehouse
  |
  +--> Data Lake
  |
  v
BI / Analytics / ML / APIs
```

---

# 2. Fundamentos de Python

## 2.1 Ambiente virtual

```bash
python --version

python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Instalação de dependências:

```bash
pip install pandas numpy
```

Gerar dependências:

```bash
pip freeze > requirements.txt
```

## 2.2 Variáveis

```python
nome = "Python"
idade = 30
preco = 99.90
ativo = True
```

## 2.3 Estruturas

```python
lista = [1, 2, 3]
tupla = (1, 2, 3)
conjunto = {1, 2, 3}

usuario = {
    "id": 1,
    "nome": "Ana"
}
```

## 2.4 Funções

```python
def calcular_total(preco: float, quantidade: int) -> float:
    return preco * quantidade
```

## 2.5 Exceções

```python
try:
    valor = int("abc")
except ValueError as exc:
    print(f"Erro: {exc}")
```

## 2.6 Arquivos

```python
from pathlib import Path

arquivo = Path("dados.txt")

arquivo.write_text(
    "Olá Python",
    encoding="utf-8"
)

conteudo = arquivo.read_text(
    encoding="utf-8"
)
```

## 2.7 Dataclasses

```python
from dataclasses import dataclass

@dataclass
class Cliente:
    id: int
    nome: str
    idade: int
```

## 2.8 Geradores

Geradores são úteis para processar grandes volumes sem carregar todos os registros na memória.

```python
def ler_numeros():
    for numero in range(1_000_000):
        yield numero
```

---

# 3. Python para Engenharia de Dados

Python é muito utilizado porque possui um grande ecossistema para:

- dados tabulares;
- computação científica;
- APIs;
- bancos de dados;
- arquivos;
- cloud;
- automação;
- ETL;
- Machine Learning;
- processamento distribuído.

## 3.1 Tipos de dados

### Estruturados

```text
id | nome | idade
1  | Ana  | 25
2  | João | 30
```

### Semiestruturados

```json
{
  "id": 1,
  "nome": "Ana",
  "idade": 25
}
```

### Não estruturados

- imagens;
- vídeos;
- áudio;
- PDFs;
- documentos;
- texto livre.

## 3.2 Formatos

- CSV
- JSON
- XML
- Excel
- Parquet
- Avro
- ORC
- TXT

## 3.3 Processamento em memória

```python
import pandas as pd

df = pd.read_csv("vendas.csv")
```

## 3.4 Processamento em lotes

```python
import pandas as pd

for lote in pd.read_csv("vendas.csv", chunksize=100_000):
    processar(lote)
```

---

# 4. Bibliotecas essenciais

## 4.1 NumPy

Computação numérica:

```python
import numpy as np

valores = np.array([10, 20, 30, 40])

print(valores.mean())
print(valores.sum())
```

## 4.2 Pandas

```python
import pandas as pd

df = pd.DataFrame({
    "produto": ["A", "B", "C"],
    "vendas": [100, 200, 150]
})

print(df)
```

## 4.3 Polars

```python
import polars as pl

df = pl.read_csv("vendas.csv")

resultado = (
    df.group_by("produto")
      .agg(pl.col("vendas").sum())
)
```

## 4.4 PyArrow

Especialmente importante para Apache Arrow e Parquet.

```python
import pyarrow.parquet as pq

tabela = pq.read_table("vendas.parquet")

print(tabela)
```

## 4.5 DuckDB

```python
import duckdb

resultado = duckdb.sql("""
    SELECT
        produto,
        SUM(vendas) AS total
    FROM 'vendas.parquet'
    GROUP BY produto
""")

print(resultado)
```

## 4.6 SQLAlchemy

```python
from sqlalchemy import create_engine

engine = create_engine(
    "sqlite:///dados.db"
)
```

## 4.7 Requests

```python
import requests

response = requests.get(
    "https://api.exemplo.com/dados",
    timeout=30
)

response.raise_for_status()

dados = response.json()
```

## 4.8 Pydantic

```python
from pydantic import BaseModel

class Cliente(BaseModel):
    id: int
    nome: str
    idade: int
```

## 4.9 Matplotlib

```python
import matplotlib.pyplot as plt

plt.plot(
    [1, 2, 3],
    [10, 20, 15]
)

plt.title("Vendas")
plt.xlabel("Período")
plt.ylabel("Valor")

plt.show()
```

## 4.10 Scikit-learn

```python
from sklearn.linear_model import LinearRegression

modelo = LinearRegression()
```

## 4.11 Pytest

```python
def test_soma():
    assert 2 + 2 == 4
```

Executar:

```bash
pytest
```

## 4.12 Ecossistema

| Biblioteca/Tecnologia | Uso |
|---|---|
| NumPy | Computação numérica |
| Pandas | Análise tabular |
| Polars | DataFrames performáticos |
| PyArrow | Arrow/Parquet |
| DuckDB | SQL analítico |
| SQLAlchemy | Bancos SQL |
| Requests | HTTP |
| Pydantic | Validação |
| Matplotlib | Gráficos |
| Seaborn | Visualização estatística |
| Scikit-learn | Machine Learning |
| Pytest | Testes |
| PySpark | Big Data |
| Dask | Computação paralela |
| Airflow | Orquestração |
| dbt | Transformação analítica |
| Great Expectations | Qualidade |
| FastAPI | APIs |
| Boto3 | AWS |

---

# 5. Análise de dados

## 5.1 Processo

```text
Pergunta
   |
Coleta
   |
Exploração
   |
Limpeza
   |
Transformação
   |
Análise
   |
Visualização
   |
Conclusão
```

## 5.2 Leitura

```python
import pandas as pd

df = pd.read_csv("vendas.csv")

print(df.head())
```

## 5.3 Inspeção

```python
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.info())
print(df.describe())
```

## 5.4 Valores ausentes

```python
print(df.isna().sum())
```

Preenchimento:

```python
df["idade"] = df["idade"].fillna(0)
```

Remoção:

```python
df = df.dropna()
```

## 5.5 Duplicados

```python
df = df.drop_duplicates()
```

## 5.6 Filtros

```python
df_filtrado = df[
    df["vendas"] > 100
]
```

## 5.7 Ordenação

```python
df = df.sort_values(
    "vendas",
    ascending=False
)
```

## 5.8 Agrupamento

```python
resultado = (
    df.groupby("categoria")["vendas"]
      .sum()
      .reset_index()
)
```

## 5.9 Agregações

```python
resultado = (
    df.groupby("categoria")
      .agg(
          faturamento=("valor_total", "sum"),
          media=("valor_total", "mean"),
          pedidos=("id", "count")
      )
      .reset_index()
)
```

## 5.10 Merge

```python
resultado = clientes.merge(
    pedidos,
    on="cliente_id",
    how="left"
)
```

## 5.11 Datas

```python
df["data"] = pd.to_datetime(df["data"])

df["ano"] = df["data"].dt.year
df["mes"] = df["data"].dt.month
df["dia"] = df["data"].dt.day
```

## 5.12 Texto

```python
df["nome"] = (
    df["nome"]
      .str.strip()
      .str.upper()
)
```

## 5.13 Exportação

```python
df.to_csv(
    "resultado.csv",
    index=False
)

df.to_parquet(
    "resultado.parquet",
    index=False
)
```

---

# 6. Estatística

## 6.1 Média

```python
media = df["valor"].mean()
```

## 6.2 Mediana

```python
mediana = df["valor"].median()
```

## 6.3 Desvio padrão

```python
desvio = df["valor"].std()
```

## 6.4 Variância

```python
variancia = df["valor"].var()
```

## 6.5 Correlação

```python
correlacao = df[
    ["idade", "renda"]
].corr()
```

## 6.6 Quantis

```python
q1 = df["valor"].quantile(0.25)
q2 = df["valor"].quantile(0.50)
q3 = df["valor"].quantile(0.75)
```

## 6.7 Estatística descritiva

```python
print(
    df["valor"].describe()
)
```

---

# 7. ETL e ELT

## 7.1 ETL

ETL significa:

```text
Extract
Transform
Load
```

Fluxo:

```text
Fonte
 |
Extract
 |
Transform
 |
Load
 |
Destino
```

## 7.2 ELT

ELT significa:

```text
Extract
Load
Transform
```

Fluxo:

```text
Fonte
 |
Extract
 |
Load
 |
Data Warehouse
 |
Transform
```

## 7.3 Quando usar ETL?

ETL pode ser interessante quando:

- a transformação precisa acontecer antes do armazenamento;
- existe restrição no destino;
- é necessário reduzir os dados antes da carga.

## 7.4 Quando usar ELT?

ELT é muito comum em arquiteturas analíticas modernas quando o armazenamento e processamento no destino são fortes.

---

# 8. Extração de dados

## 8.1 CSV

```python
import pandas as pd

df = pd.read_csv(
    "clientes.csv"
)
```

## 8.2 JSON

```python
import json

with open(
    "clientes.json",
    encoding="utf-8"
) as arquivo:
    dados = json.load(arquivo)
```

## 8.3 Excel

```python
df = pd.read_excel(
    "clientes.xlsx"
)
```

## 8.4 Parquet

```python
df = pd.read_parquet(
    "clientes.parquet"
)
```

## 8.5 API

```python
import requests

response = requests.get(
    "https://api.exemplo.com/clientes",
    timeout=30
)

response.raise_for_status()

clientes = response.json()
```

## 8.6 Paginação de API

```python
import requests

def buscar_clientes():
    pagina = 1
    resultado = []

    while True:
        response = requests.get(
            "https://api.exemplo.com/clientes",
            params={"page": pagina},
            timeout=30
        )

        response.raise_for_status()

        dados = response.json()

        itens = dados["items"]

        if not itens:
            break

        resultado.extend(itens)

        pagina += 1

    return resultado
```

## 8.7 Banco de dados

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg://usuario:senha@localhost/app"
)

df = pd.read_sql(
    "SELECT * FROM clientes",
    engine
)
```

---

# 9. Transformação de dados

Transformações comuns:

- limpeza;
- normalização;
- padronização;
- deduplicação;
- enriquecimento;
- agregação;
- joins;
- conversão de tipos;
- tratamento de nulos.

## 9.1 Conversão de tipos

```python
df["idade"] = pd.to_numeric(
    df["idade"],
    errors="coerce"
)
```

## 9.2 Normalização textual

```python
df["cidade"] = (
    df["cidade"]
      .str.strip()
      .str.lower()
)
```

## 9.3 Remover duplicados

```python
df = df.drop_duplicates(
    subset=["id"]
)
```

## 9.4 Criar coluna

```python
df["total"] = (
    df["quantidade"] *
    df["preco"]
)
```

## 9.5 Filtrar registros

```python
df = df[
    df["status"] == "ativo"
]
```

## 9.6 Funções

```python
def calcular_total(row):
    return (
        row["quantidade"] *
        row["preco"]
    )

df["total"] = df.apply(
    calcular_total,
    axis=1
)
```

Para grandes volumes, prefira operações vetorizadas quando possível.

---

# 10. Carga de dados

## 10.1 CSV

```python
df.to_csv(
    "saida.csv",
    index=False
)
```

## 10.2 Parquet

```python
df.to_parquet(
    "saida.parquet",
    index=False
)
```

## 10.3 Banco SQL

```python
df.to_sql(
    "clientes",
    engine,
    if_exists="append",
    index=False
)
```

## 10.4 Estratégias de carga

### Full Load

Carrega tudo.

```text
Fonte -> Destino
```

### Incremental Load

Carrega somente dados novos ou alterados.

```text
Fonte
 |
Filtro por data/id
 |
Novos registros
 |
Destino
```

### Upsert

Insere novos registros e atualiza existentes.

```text
INSERT + UPDATE
```

---

# 11. Pipelines

## 11.1 O que é um pipeline?

Pipeline é uma sequência automatizada de etapas.

```text
Extract
   |
Validate
   |
Transform
   |
Quality Check
   |
Load
   |
Monitor
```

## 11.2 Pipeline simples

```python
def extract():
    ...

def transform(data):
    ...

def validate(data):
    ...

def load(data):
    ...

def pipeline():
    data = extract()
    data = transform(data)
    validate(data)
    load(data)

if __name__ == "__main__":
    pipeline()
```

## 11.3 Pipeline idempotente

Uma operação idempotente pode ser executada mais de uma vez sem produzir resultados incorretos.

Exemplo:

```text
Processar vendas do dia 2026-09-10
```

Em vez de:

```text
INSERT indiscriminado
```

pode-se utilizar uma estratégia baseada em chave única e upsert.

## 11.4 Pipeline incremental

```python
from datetime import datetime

ultima_execucao = datetime(...)

dados = extrair(
    atualizado_desde=ultima_execucao
)
```

## 11.5 Pipeline com logging

```python
import logging

logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)

logger.info("Pipeline iniciado")

try:
    executar_pipeline()
    logger.info("Pipeline concluído")
except Exception:
    logger.exception(
        "Pipeline falhou"
    )
    raise
```

---

# 12. Orquestração

Orquestração é o gerenciamento de workflows.

Ferramentas conhecidas:

- Apache Airflow;
- Prefect;
- Dagster;
- Luigi;
- serviços gerenciados de cloud.

## 12.1 DAG

DAG significa:

```text
Directed Acyclic Graph
```

Exemplo:

```text
Extract
   |
   v
Validate
   |
   +------+
   |      |
   v      v
Clean   Enrich
   |      |
   +------+
      |
      v
     Load
```

## 12.2 Dependências

Um pipeline pode possuir:

```text
extract
   |
validate
   |
transform
   |
load
```

A etapa seguinte depende da conclusão da anterior.

## 12.3 Agendamento

Exemplo conceitual:

```text
Todos os dias às 02:00
        |
        v
Pipeline de vendas
```

---

# 13. Bancos de dados

## 13.1 Relacionais

Exemplos:

- PostgreSQL;
- MySQL;
- MariaDB;
- SQL Server;
- Oracle;
- SQLite.

## 13.2 NoSQL

Categorias:

- chave-valor;
- documentos;
- colunar;
- grafos.

Exemplos:

- Redis;
- MongoDB;
- Cassandra;
- Neo4j.

## 13.3 Conexão PostgreSQL

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg://usuario:senha@localhost/banco"
)
```

## 13.4 Leitura

```python
import pandas as pd

df = pd.read_sql(
    """
    SELECT *
    FROM vendas
    WHERE valor > 100
    """,
    engine
)
```

## 13.5 Escrita

```python
df.to_sql(
    "vendas_processadas",
    engine,
    if_exists="append",
    index=False
)
```

---

# 14. SQL

## 14.1 SELECT

```sql
SELECT
    id,
    nome,
    valor
FROM vendas;
```

## 14.2 WHERE

```sql
SELECT *
FROM vendas
WHERE valor > 100;
```

## 14.3 GROUP BY

```sql
SELECT
    categoria,
    SUM(valor) AS total
FROM vendas
GROUP BY categoria;
```

## 14.4 JOIN

```sql
SELECT
    c.nome,
    p.valor
FROM clientes c
JOIN pedidos p
    ON p.cliente_id = c.id;
```

## 14.5 Window Functions

```sql
SELECT
    cliente_id,
    data,
    valor,
    SUM(valor) OVER (
        PARTITION BY cliente_id
        ORDER BY data
    ) AS acumulado
FROM vendas;
```

## 14.6 CTE

```sql
WITH vendas_validas AS (
    SELECT *
    FROM vendas
    WHERE valor > 0
)
SELECT
    categoria,
    SUM(valor)
FROM vendas_validas
GROUP BY categoria;
```

---

# 15. Data Warehouse, Data Lake e Lakehouse

## 15.1 Data Warehouse

Armazena dados estruturados para análise.

```text
Fontes
  |
ETL/ELT
  |
Data Warehouse
  |
BI
```

## 15.2 Data Lake

Armazena grandes volumes de dados em diferentes formatos.

```text
Data Lake
 |
 +-- raw
 +-- bronze
 +-- silver
 +-- gold
```

## 15.3 Medallion Architecture

### Bronze

Dados brutos.

```text
raw/
```

### Silver

Dados limpos e padronizados.

```text
silver/
```

### Gold

Dados preparados para consumo.

```text
gold/
```

## 15.4 Lakehouse

Combina conceitos de:

- Data Lake;
- Data Warehouse;
- processamento analítico;
- governança.

---

# 16. Processamento distribuído

Quando os dados são grandes demais para uma única máquina, pode ser necessário distribuir o processamento.

## 16.1 Apache Spark

Python utiliza PySpark.

```bash
pip install pyspark
```

## 16.2 DataFrame

```python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Analytics")
    .getOrCreate()
)

df = spark.read.parquet(
    "vendas.parquet"
)

df.show()
```

## 16.3 Transformação

```python
resultado = (
    df.groupBy("categoria")
      .sum("valor")
)
```

## 16.4 Quando usar Spark?

Spark pode ser adequado quando:

- os dados são muito grandes;
- processamento distribuído é necessário;
- há workloads complexos;
- o processamento em uma única máquina não é suficiente.

Para datasets pequenos, Pandas, Polars ou DuckDB podem ser mais simples.

---

# 17. APIs e coleta de dados

## 17.1 API REST

```python
import requests

response = requests.get(
    "https://api.exemplo.com/produtos",
    timeout=30
)

response.raise_for_status()

produtos = response.json()
```

## 17.2 POST

```python
response = requests.post(
    "https://api.exemplo.com/clientes",
    json={
        "nome": "Ana"
    },
    timeout=30
)

response.raise_for_status()
```

## 17.3 Headers

```python
headers = {
    "Authorization": "Bearer TOKEN"
}

response = requests.get(
    url,
    headers=headers,
    timeout=30
)
```

Segredos não devem ficar diretamente no código.

---

# 18. Streaming

Streaming trata dados continuamente.

```text
Eventos
  |
  v
Broker
  |
  v
Consumidores
  |
  +--> Data Lake
  |
  +--> Data Warehouse
  |
  +--> Aplicações
```

Tecnologias comuns:

- Apache Kafka;
- Apache Pulsar;
- serviços de streaming em cloud.

## 18.1 Conceitos

### Producer

Produz eventos.

### Consumer

Consome eventos.

### Topic

Categoria lógica de eventos.

### Partition

Divisão paralela de um tópico.

### Offset

Posição de leitura de um consumidor.

---

# 19. Qualidade de dados

Qualidade deve ser tratada como parte do pipeline.

## 19.1 Dimensões

- completude;
- validade;
- unicidade;
- consistência;
- precisão;
- atualidade.

## 19.2 Validação simples

```python
assert df["id"].notna().all()
assert (df["valor"] >= 0).all()
```

Em sistemas reais, prefira mecanismos de validação estruturados.

## 19.3 Schema

```python
from pydantic import BaseModel

class Venda(BaseModel):
    id: int
    produto: str
    quantidade: int
    valor: float
```

## 19.4 Data Quality Pipeline

```text
Extract
 |
Schema Check
 |
Null Check
 |
Duplicate Check
 |
Business Rules
 |
Transform
 |
Load
```

## 19.5 Data Contracts

Um contrato pode definir:

```text
Campo: cliente_id
Tipo: inteiro
Obrigatório: sim
Descrição: Identificador do cliente
```

---

# 20. Testes

## 20.1 Teste unitário

```python
def calcular_total(
    preco: float,
    quantidade: int
) -> float:
    return preco * quantidade


def test_calcular_total():
    assert calcular_total(
        10,
        3
    ) == 30
```

## 20.2 Teste com pytest

```python
def test_valor_nao_negativo():
    valor = 100

    assert valor >= 0
```

## 20.3 Teste de pipeline

```python
def test_pipeline():
    dados = [
        {
            "id": 1,
            "valor": 100
        }
    ]

    resultado = transformar(dados)

    assert len(resultado) == 1
```

## 20.4 Tipos de teste

- unitário;
- integração;
- contrato;
- qualidade;
- regressão;
- carga;
- performance;
- end-to-end.

---

# 21. Segurança

## 21.1 Nunca armazenar senha no código

Evite:

```python
senha = "minha-senha"
```

Prefira variáveis de ambiente ou um gerenciador de segredos.

```python
import os

senha = os.getenv(
    "DATABASE_PASSWORD"
)
```

## 21.2 SQL Injection

Evite construir SQL com concatenação:

```python
# Evitar
query = f"SELECT * FROM users WHERE id = {user_id}"
```

Prefira parâmetros:

```python
from sqlalchemy import text

query = text("""
    SELECT *
    FROM users
    WHERE id = :id
""")

connection.execute(
    query,
    {"id": user_id}
)
```

## 21.3 Princípio do menor privilégio

Um pipeline deve possuir somente as permissões necessárias.

Exemplo:

```text
Pipeline de leitura
    |
    +--> SELECT

Pipeline de carga
    |
    +--> INSERT
```

## 21.4 Dados sensíveis

Devem possuir controles adequados de:

- acesso;
- criptografia;
- mascaramento;
- auditoria;
- retenção;
- descarte.

---

# 22. Observabilidade

Um pipeline profissional deve permitir responder:

- Executou?
- Quanto tempo demorou?
- Quantos registros processou?
- Quantos falharam?
- Qual etapa falhou?
- Quando ocorreu?
- Qual versão estava executando?

## 22.1 Logs

```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Processando %s registros",
    len(df)
)
```

## 22.2 Métricas

Exemplos:

```text
pipeline_duration_seconds
records_processed
records_failed
records_inserted
records_updated
```

## 22.3 Alertas

```text
Pipeline
   |
Falha
   |
Alerta
   |
Equipe
```

## 22.4 Tracing

Pode ajudar a acompanhar uma execução através de vários serviços.

---

# 23. Performance

## 23.1 Evite loops desnecessários

Evite:

```python
resultado = []

for valor in df["valor"]:
    resultado.append(valor * 2)
```

Prefira:

```python
df["resultado"] = df["valor"] * 2
```

## 23.2 Selecionar somente colunas necessárias

```python
df = pd.read_csv(
    "vendas.csv",
    usecols=[
        "id",
        "valor",
        "categoria"
    ]
)
```

## 23.3 Processar em chunks

```python
for chunk in pd.read_csv(
    "grande.csv",
    chunksize=100_000
):
    processar(chunk)
```

## 23.4 Formato Parquet

Parquet é especialmente útil em workloads analíticos porque suporta armazenamento colunar e compressão.

```python
df.to_parquet(
    "vendas.parquet"
)
```

## 23.5 Particionamento

Exemplo:

```text
vendas/
  ano=2026/
    mes=01/
    mes=02/
    mes=03/
```

Isso pode reduzir a quantidade de dados lidos em consultas filtradas.

---

# 24. Machine Learning aplicado a dados

Engenharia de dados e Machine Learning estão relacionados.

## 24.1 Pipeline

```text
Dados
 |
Limpeza
 |
Features
 |
Treinamento
 |
Validação
 |
Modelo
 |
Deploy
 |
Monitoramento
```

## 24.2 Scikit-learn

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

X = df[["idade", "renda"]]
y = df["valor"]

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
)

modelo = LinearRegression()

modelo.fit(
    X_train,
    y_train
)

predicoes = modelo.predict(X_test)
```

## 24.3 Feature Engineering

Exemplo:

```python
df["ticket_medio"] = (
    df["faturamento"] /
    df["quantidade_pedidos"]
)
```

## 24.4 Data leakage

Data leakage ocorre quando informações que não deveriam estar disponíveis no momento da previsão entram no treinamento.

É um dos problemas mais importantes em pipelines de ML.

---

# 25. Arquitetura de projetos Python

Uma estrutura profissional:

```text
data-platform/
│
├── src/
│   └── data_platform/
│       ├── __init__.py
│       ├── config.py
│       ├── logging.py
│       │
│       ├── extraction/
│       │   ├── __init__.py
│       │   ├── api.py
│       │   ├── files.py
│       │   └── database.py
│       │
│       ├── transformation/
│       │   ├── __init__.py
│       │   ├── cleaning.py
│       │   └── business_rules.py
│       │
│       ├── validation/
│       │   ├── __init__.py
│       │   └── quality.py
│       │
│       ├── loading/
│       │   ├── __init__.py
│       │   └── warehouse.py
│       │
│       └── pipelines/
│           ├── __init__.py
│           └── vendas.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── curated/
│
├── notebooks/
│
├── scripts/
│
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
└── requirements.txt
```

## 25.1 Separação de responsabilidades

Evite:

```python
def pipeline():
    # API
    # limpeza
    # SQL
    # validação
    # logging
    # armazenamento
```

Prefira:

```python
dados = extract()
dados = transform(dados)
validate(dados)
load(dados)
```

---

# 26. DevOps e CI/CD

## 26.1 Git

```bash
git init

git add .

git commit -m "initial commit"
```

## 26.2 Branch

```bash
git checkout -b feature/data-pipeline
```

## 26.3 CI

Uma pipeline CI pode executar:

```text
Push
 |
Lint
 |
Type Check
 |
Tests
 |
Build
```

## 26.4 Ferramentas

Exemplos:

- GitHub Actions;
- GitLab CI;
- Jenkins;
- Azure Pipelines.

## 26.5 Docker

Exemplo básico:

```dockerfile
FROM python:3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "data_platform"]
```

---

# 27. Projetos práticos

## Projeto 1 — ETL de vendas

### Objetivo

Criar um pipeline que:

1. lê CSV;
2. limpa dados;
3. valida registros;
4. calcula métricas;
5. grava Parquet;
6. grava no banco.

### Arquitetura

```text
vendas.csv
    |
    v
Extract
    |
    v
Transform
    |
    v
Validate
    |
    v
Parquet
    |
    v
PostgreSQL
```

### Código

```python
import pandas as pd

def extract(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates()

    df["valor_total"] = (
        df["quantidade"] *
        df["preco"]
    )

    return df


def validate(df: pd.DataFrame) -> None:
    if df["id"].isna().any():
        raise ValueError(
            "Existem IDs nulos"
        )

    if (df["valor_total"] < 0).any():
        raise ValueError(
            "Existem valores negativos"
        )


def load(
    df: pd.DataFrame,
    path: str
) -> None:
    df.to_parquet(
        path,
        index=False
    )


def main():
    df = extract(
        "data/raw/vendas.csv"
    )

    df = transform(df)

    validate(df)

    load(
        df,
        "data/processed/vendas.parquet"
    )


if __name__ == "__main__":
    main()
```

---

# 28. Projeto 2 — Pipeline de API

## Objetivo

Consumir uma API, normalizar os dados e armazená-los.

```python
import requests
import pandas as pd


def extract(url: str) -> list[dict]:
    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def transform(
    dados: list[dict]
) -> pd.DataFrame:
    df = pd.DataFrame(dados)

    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
    )

    return df


def load(
    df: pd.DataFrame,
    path: str
):
    df.to_parquet(
        path,
        index=False
    )
```

---

# 29. Projeto 3 — Data Lake

Estrutura:

```text
data-lake/
│
├── bronze/
│   └── vendas/
│
├── silver/
│   └── vendas/
│
└── gold/
    └── vendas_diarias/
```

### Bronze

Dados originais.

### Silver

Dados limpos.

### Gold

Dados agregados para consumo.

---

# 30. Projeto 4 — Data Warehouse

Modelo dimensional:

```text
                 dim_cliente
                      |
                      |
dim_produto --- fato_vendas --- dim_data
                      |
                      |
                dim_vendedor
```

## Fato

```text
fato_vendas
------------
id_venda
cliente_id
produto_id
data_id
quantidade
valor
```

## Dimensão

```text
dim_cliente
-----------
cliente_id
nome
cidade
estado
segmento
```

---

# 31. Projeto 5 — Pipeline incremental

Estratégia:

```text
Última execução
      |
      v
SELECT registros
WHERE updated_at > última_execução
      |
      v
Transform
      |
      v
Upsert
      |
      v
Atualizar checkpoint
```

Checkpoint:

```json
{
  "pipeline": "vendas",
  "last_execution": "2026-09-10T02:00:00"
}
```

---

# 32. Boas práticas

## 32.1 Código limpo

Prefira:

```python
def calcular_faturamento(
    vendas: pd.DataFrame
) -> float:
    return vendas["valor"].sum()
```

Em vez de funções gigantes.

## 32.2 Configuração

Evite:

```python
URL = "https://api.exemplo.com"
```

espalhado pelo projeto.

Centralize configurações.

## 32.3 Variáveis de ambiente

```python
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)
```

## 32.4 Logging

Utilize logs estruturados em aplicações maiores.

## 32.5 Tipagem

```python
def processar(
    dados: list[dict]
) -> list[dict]:
    ...
```

## 32.6 Testes

Toda transformação importante deve possuir testes.

## 32.7 Documentação

Documente:

- origem;
- destino;
- schema;
- regras;
- frequência;
- dependências;
- SLA;
- responsáveis;
- tratamento de erros.

---

# 33. Arquitetura completa de referência

Uma plataforma de dados pode ser organizada assim:

```text
                         FONTES
                           |
        +------------------+------------------+
        |                  |                  |
       API               CSV               Banco
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                       INGESTÃO
                           |
                           v
                     DATA LAKE
                           |
                 +---------+---------+
                 |                   |
              Bronze              Eventos
                 |                   |
                 v                   v
             Silver              Streaming
                 |
                 v
              Quality
                 |
                 v
                Gold
                 |
          +------+------+
          |             |
          v             v
       Warehouse      Lakehouse
          |             |
          +------+------+
                 |
                 v
              Analytics
                 |
       +---------+---------+
       |                   |
       v                   v
      BI                  ML
       |                   |
       +---------+---------+
                 |
                 v
               APIs
```

---

# 34. Checklist de um pipeline profissional

## Extração

- [ ] Fonte identificada
- [ ] Autenticação segura
- [ ] Timeout configurado
- [ ] Retry configurado
- [ ] Paginação implementada
- [ ] Rate limit tratado

## Transformação

- [ ] Tipos corretos
- [ ] Nulos tratados
- [ ] Duplicados tratados
- [ ] Regras de negócio implementadas
- [ ] Datas normalizadas
- [ ] Dados inválidos tratados

## Qualidade

- [ ] Schema validado
- [ ] Chaves verificadas
- [ ] Valores obrigatórios verificados
- [ ] Unicidade verificada
- [ ] Regras de negócio verificadas

## Armazenamento

- [ ] Formato adequado
- [ ] Particionamento
- [ ] Compressão
- [ ] Retenção
- [ ] Backup
- [ ] Controle de acesso

## Operação

- [ ] Logs
- [ ] Métricas
- [ ] Alertas
- [ ] Retry
- [ ] Idempotência
- [ ] Monitoramento
- [ ] Documentação

---

# 35. Plano de estudos

## Nível 1 — Python

Estude:

1. Sintaxe;
2. Tipos;
3. Funções;
4. Classes;
5. Exceções;
6. Arquivos;
7. Módulos;
8. Pacotes;
9. Tipagem;
10. Testes.

## Nível 2 — Dados

Estude:

1. NumPy;
2. Pandas;
3. Polars;
4. PyArrow;
5. Parquet;
6. DuckDB;
7. visualização;
8. estatística.

## Nível 3 — SQL

Estude:

1. SELECT;
2. WHERE;
3. JOIN;
4. GROUP BY;
5. CTE;
6. Window Functions;
7. índices;
8. transações;
9. otimização.

## Nível 4 — Engenharia de Dados

Estude:

1. ETL;
2. ELT;
3. pipelines;
4. incremental;
5. idempotência;
6. Data Lake;
7. Data Warehouse;
8. modelagem dimensional;
9. qualidade;
10. governança.

## Nível 5 — Big Data

Estude:

1. Spark;
2. particionamento;
3. processamento distribuído;
4. streaming;
5. Kafka;
6. arquiteturas distribuídas.

## Nível 6 — Produção

Estude:

1. Docker;
2. CI/CD;
3. cloud;
4. observabilidade;
5. segurança;
6. orquestração;
7. testes;
8. infraestrutura como código.

---

# 36. Stack recomendada para começar

Uma stack simples e poderosa:

```text
Python
   |
Pandas / Polars
   |
PyArrow
   |
Parquet
   |
DuckDB
   |
PostgreSQL
   |
Airflow / Prefect / Dagster
   |
Docker
   |
Git
   |
CI/CD
```

Para Big Data:

```text
Python
   |
PySpark
   |
Object Storage
   |
Data Lake
   |
Data Warehouse / Lakehouse
   |
BI / ML
```

---

# 37. Glossário

| Termo | Significado |
|---|---|
| ETL | Extract, Transform, Load |
| ELT | Extract, Load, Transform |
| API | Application Programming Interface |
| DAG | Directed Acyclic Graph |
| ETL Pipeline | Fluxo automatizado de processamento |
| Data Lake | Armazenamento de dados em grande escala |
| Data Warehouse | Armazém analítico estruturado |
| Lakehouse | Arquitetura que combina conceitos de Lake e Warehouse |
| Bronze | Camada bruta |
| Silver | Camada tratada |
| Gold | Camada curada |
| Batch | Processamento em lotes |
| Streaming | Processamento contínuo |
| Schema | Estrutura dos dados |
| Data Contract | Contrato entre produtor e consumidor |
| Idempotência | Reexecução sem efeitos incorretos |
| Upsert | Insert + Update |
| Partition | Divisão física/lógica dos dados |
| Checkpoint | Estado salvo de uma execução |
| SLA | Acordo de nível de serviço |
| Data Quality | Qualidade dos dados |
| Data Lineage | Rastreamento da origem e transformação |
| Feature | Variável usada em Machine Learning |
| Data Leakage | Vazamento de informação para o modelo |

---

# 38. Conclusão

Uma carreira sólida em Engenharia de Dados com Python exige muito mais do que saber Pandas.

A base deve combinar:

```text
Python
+
SQL
+
Estruturas de dados
+
Bancos de dados
+
ETL / ELT
+
Pipelines
+
Data Lake
+
Data Warehouse
+
Qualidade
+
Testes
+
Segurança
+
Observabilidade
+
Cloud
+
Orquestração
+
Big Data
```

O objetivo final é conseguir construir pipelines que sejam:

- confiáveis;
- reproduzíveis;
- testáveis;
- observáveis;
- seguros;
- escaláveis;
- performáticos;
- fáceis de manter.

Uma boa evolução prática é construir projetos progressivamente:

```text
CSV
 |
Python
 |
Pandas
 |
Parquet
 |
DuckDB
 |
PostgreSQL
 |
API
 |
ETL
 |
Pipeline incremental
 |
Orquestração
 |
Data Lake
 |
Data Warehouse
 |
Spark
 |
Streaming
 |
Cloud
```

Esse caminho cria uma base sólida para trabalhar profissionalmente com Engenharia de Dados, Analytics, BI, Ciência de Dados e Machine Learning.
