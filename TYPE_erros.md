# TYPES.md

## Especificação Oficial de Tipos — Linguagem DataForge

> **Status**: Draft v1.0
> **Escopo**: Definição oficial do sistema de tipos da linguagem DataForge
> **Objetivo**: Estabelecer um sistema de tipos mais rico, explícito e semântico que Python, focado em análise de dados, estatística avançada e engenharia de dados.

---

## 1️⃣1️⃣ Tipos de Erro (Tipados)

Em DataForge, erros **são tipos explícitos**, não exceções genéricas. Isso permite:

* Pipelines previsíveis
* Melhor observabilidade
* Tratamento funcional de falhas
* Menos `try/catch` implícito

### 11.1 Tipo Base

```
Error
```

Campos comuns:

* `message`
* `code`
* `context`
* `cause`

---

### 11.2 Erros de Tipo e Valor

```
TypeError
ValueError
CastError
OverflowError
UnderflowError
NullError
```

Usados quando há inconsistência semântica ou conversão inválida.

---

### 11.3 Erros de Dados e Estatística

```
DataError
MissingValueError
OutlierError
SchemaError
StatError
DistributionError
HypothesisError
ConfidenceIntervalError
```

Garantem rigor estatístico e integridade dos dados.

---

### 11.4 Erros de Pipeline e Execução

```
PipelineError
StageError
TaskError
DependencyError
ExecutionError
CheckpointError
```

Essenciais para engenharia de dados e orquestração.

---

### 11.5 Erros de IO, Rede e Web

```
IOError
FileNotFoundError
PermissionError
NetworkError
TimeoutError
HTTPError
APIError
ScrapingError
```

Projetados para ingestão de dados e integração externa.

---

### 11.6 Erros de Segurança e Infraestrutura

```
AuthError
CredentialError
SecretError
EncryptionError
VaultError
ConfigError
EnvError
```

Importantes para ambientes cloud e dados sensíveis.

---

### 11.7 Erros Funcionais e de Composição

```
ResultError
OptionError
LazyError
EffectError
```

Permitem falhas como valores composicionais.

---

### 11.8 Boas Práticas de Uso

* Erros **devem ser retornados**, não lançados
* Pipelines devem propagar erros automaticamente
* Logs estruturados devem consumir erros tipados

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

O sistema de tipos da DataForge é um **diferencial estratégico**, posicionando a linguagem acima do Python em expressividade semântica, segurança e clareza para análise de dados e engenharia de dados.

---

**Este documento serve como base oficial para implementação, documentação e evolução da linguagem.**
