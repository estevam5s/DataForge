# Python — Trilha Completa do Básico ao Avançado

> Guia técnico e progressivo de Python, do primeiro contato com a linguagem até arquitetura de software, DDD, APIs REST, CRUD, persistência, concorrência, testes, segurança, performance, DevOps e aplicações avançadas.

---

## Sumário

1. [Fundamentos](#1-fundamentos)
2. [Tipos de dados](#2-tipos-de-dados)
3. [Operadores e expressões](#3-operadores-e-expressões)
4. [Controle de fluxo](#4-controle-de-fluxo)
5. [Funções](#5-funções)
6. [Coleções](#6-coleções)
7. [Strings](#7-strings)
8. [Expressões regulares](#8-expressões-regulares)
9. [Arquivos e diretórios](#9-arquivos-e-diretórios)
10. [Exceções e tratamento de erros](#10-exceções-e-tratamento-de-erros)
11. [Módulos, pacotes e ambientes](#11-módulos-pacotes-e-ambientes)
12. [Programação Orientada a Objetos](#12-programação-orientada-a-objetos)
13. [Recursos avançados de OOP](#13-recursos-avançados-de-oop)
14. [Type hints e tipagem](#14-type-hints-e-tipagem)
15. [Dataclasses, enums e validação](#15-dataclasses-enums-e-validação)
16. [Iteradores e generators](#16-iteradores-e-generators)
17. [Decorators e context managers](#17-decorators-e-context-managers)
18. [Programação funcional](#18-programação-funcional)
19. [Banco de dados](#19-banco-de-dados)
20. [CRUD completo](#20-crud-completo)
21. [ORM](#21-orm)
22. [APIs REST](#22-apis-rest)
23. [API com FastAPI](#23-api-com-fastapi)
24. [Autenticação e autorização](#24-autenticação-e-autorização)
25. [DDD](#25-ddd)
26. [Arquitetura em camadas](#26-arquitetura-em-camadas)
27. [SOLID e Design Patterns](#27-solid-e-design-patterns)
28. [Testes](#28-testes)
29. [Logging e observabilidade](#29-logging-e-observabilidade)
30. [Concorrência e paralelismo](#30-concorrência-e-paralelismo)
31. [Performance](#31-performance)
32. [Segurança](#32-segurança)
33. [Mensageria e sistemas distribuídos](#33-mensageria-e-sistemas-distribuídos)
34. [Cache](#34-cache)
35. [WebSockets](#35-websockets)
36. [CLI](#36-cli)
37. [Processamento de dados](#37-processamento-de-dados)
38. [Automação](#38-automação)
39. [DevOps](#39-devops)
40. [Docker](#40-docker)
41. [CI/CD](#41-cicd)
42. [Arquiteturas avançadas](#42-arquiteturas-avançadas)
43. [Boas práticas](#43-boas-práticas)
44. [Projetos progressivos](#44-projetos-progressivos)
45. [Checklist de domínio](#45-checklist-de-domínio)

---

# 1. Fundamentos

## 1.1 Primeiro programa

```python
print("Olá, mundo!")
```

## 1.2 Comentários

```python
# Comentário de uma linha

"""
Bloco de documentação.
"""
```

## 1.3 Variáveis

Python possui tipagem dinâmica:

```python
nome = "Maria"
idade = 25
altura = 1.68
ativo = True
```

Uma variável é uma referência para um objeto:

```python
x = 10
x = "Python"
```

## 1.4 Constantes por convenção

Python não possui constantes obrigatórias:

```python
MAX_TENTATIVAS = 3
API_URL = "https://api.exemplo.com"
```

## 1.5 Entrada e saída

```python
nome = input("Nome: ")
print(f"Olá, {nome}!")
```

Conversão:

```python
idade = int(input("Idade: "))
preco = float(input("Preço: "))
```

## 1.6 Indentação

Indentação define blocos:

```python
if idade >= 18:
    print("Maior de idade")
else:
    print("Menor de idade")
```

---

# 2. Tipos de dados

## 2.1 Principais tipos

```python
str
int
float
complex
bool
None
list
tuple
set
dict
```

## 2.2 Verificando tipos

```python
valor = 10

print(type(valor))
print(isinstance(valor, int))
```

## 2.3 Conversões

```python
int("10")
float("10.5")
str(100)
bool(1)
list("abc")
```

## 2.4 Mutabilidade

Imutáveis:

- `int`
- `float`
- `bool`
- `str`
- `tuple`
- `frozenset`

Mutáveis:

- `list`
- `dict`
- `set`

---

# 3. Operadores e expressões

## 3.1 Aritméticos

```python
+   # soma
-   # subtração
*   # multiplicação
/   # divisão
//  # divisão inteira
%   # módulo
**  # potência
```

## 3.2 Comparação

```python
==
!=
>
<
>=
<=
```

## 3.3 Lógicos

```python
and
or
not
```

## 3.4 Identidade

```python
is
is not
```

`is` verifica identidade do objeto; `==` verifica igualdade de valor.

## 3.5 Associação

```python
in
not in
```

## 3.6 Operador ternário

```python
status = "adulto" if idade >= 18 else "menor"
```

## 3.7 Assignment expression

```python
if (total := len(itens)) > 0:
    print(total)
```

---

# 4. Controle de fluxo

## 4.1 if / elif / else

```python
nota = 8

if nota >= 9:
    conceito = "A"
elif nota >= 7:
    conceito = "B"
else:
    conceito = "C"
```

## 4.2 for

```python
for numero in range(5):
    print(numero)
```

## 4.3 while

```python
contador = 0

while contador < 5:
    print(contador)
    contador += 1
```

## 4.4 break

```python
for numero in range(10):
    if numero == 5:
        break
```

## 4.5 continue

```python
for numero in range(10):
    if numero % 2 == 0:
        continue

    print(numero)
```

## 4.6 match/case

```python
comando = "listar"

match comando:
    case "listar":
        print("Listando")
    case "criar":
        print("Criando")
    case _:
        print("Desconhecido")
```

---

# 5. Funções

## 5.1 Função simples

```python
def somar(a, b):
    return a + b
```

## 5.2 Parâmetros padrão

```python
def saudar(nome="Visitante"):
    return f"Olá, {nome}"
```

## 5.3 Argumentos nomeados

```python
def criar_usuario(nome, idade):
    ...

criar_usuario(nome="Ana", idade=30)
```

## 5.4 *args

```python
def somar_todos(*numeros):
    return sum(numeros)
```

## 5.5 **kwargs

```python
def configurar(**opcoes):
    return opcoes
```

## 5.6 Keyword-only

```python
def criar(nome, *, ativo=True):
    ...
```

## 5.7 Positional-only

```python
def dividir(a, b, /):
    return a / b
```

## 5.8 Lambda

```python
dobro = lambda x: x * 2
```

## 5.9 Docstrings

```python
def calcular_total(preco, quantidade):
    """Calcula o valor total de uma compra."""
    return preco * quantidade
```

---

# 6. Coleções

## 6.1 Listas

```python
nomes = ["Ana", "João", "Carlos"]

nomes.append("Maria")
nomes.remove("João")
nomes.sort()
```

## 6.2 Tuplas

```python
coordenada = (10, 20)
```

## 6.3 Sets

```python
ids = {1, 2, 3, 3}
print(ids)
```

Operações:

```python
a | b
a & b
a - b
a ^ b
```

## 6.4 Dicionários

```python
usuario = {
    "nome": "Ana",
    "idade": 30
}

print(usuario["nome"])
usuario["ativo"] = True
```

## 6.5 Compreensões

```python
quadrados = [x ** 2 for x in range(10)]

pares = [x for x in range(20) if x % 2 == 0]

mapa = {x: x ** 2 for x in range(5)}

unicos = {x % 3 for x in range(10)}
```

---

# 7. Strings

## 7.1 Formatação

```python
nome = "Ana"
idade = 30

texto = f"{nome} possui {idade} anos."
```

## 7.2 Métodos importantes

```python
texto.upper()
texto.lower()
texto.strip()
texto.split()
texto.replace("a", "b")
texto.startswith("Py")
texto.endswith("on")
```

## 7.3 Slicing

```python
texto[0:5]
texto[:5]
texto[5:]
texto[::-1]
```

## 7.4 Unicode

Python trabalha nativamente com strings Unicode:

```python
mensagem = "Olá, programação!"
```

---

# 8. Expressões regulares

Utilize o módulo `re`.

```python
import re

padrao = r"\d+"
resultado = re.findall(padrao, "Pedido 123 e pedido 456")

print(resultado)
```

## 8.1 Principais símbolos

| Símbolo | Significado |
|---|---|
| `.` | qualquer caractere |
| `^` | início |
| `$` | fim |
| `*` | zero ou mais |
| `+` | um ou mais |
| `?` | zero ou um |
| `{n}` | quantidade exata |
| `[]` | conjunto |
| `()` | grupo |
| `\d` | dígito |
| `\w` | caractere de palavra |
| `\s` | espaço |

## 8.2 Validar email

```python
import re

email = "usuario@example.com"
padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"

if re.match(padrao, email):
    print("Email válido")
```

## 8.3 Substituição

```python
texto = "Meu CPF é 123.456.789-00"
resultado = re.sub(r"\d", "*", texto)
print(resultado)
```

## 8.4 Grupos nomeados

```python
padrao = r"(?P<ddd>\d{2}) (?P<numero>\d{4,5}-\d{4})"

match = re.search(padrao, "11 99999-1234")

if match:
    print(match.group("ddd"))
    print(match.group("numero"))
```

> Regex é excelente para padrões textuais, mas regras complexas devem permanecer no domínio da aplicação.

---

# 9. Arquivos e diretórios

## 9.1 Abrindo arquivos

```python
with open("dados.txt", "r", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()
```

Modos:

```text
r  leitura
w  escrita, sobrescreve
a  adiciona ao final
x  criação exclusiva
b  binário
t  texto
+  leitura e escrita
```

## 9.2 Escrever

```python
with open("dados.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write("Olá, Python!")
```

## 9.3 Ler linhas

```python
with open("dados.txt", encoding="utf-8") as arquivo:
    for linha in arquivo:
        print(linha.strip())
```

## 9.4 pathlib

```python
from pathlib import Path

arquivo = Path("dados.txt")

arquivo.write_text("Conteúdo", encoding="utf-8")
conteudo = arquivo.read_text(encoding="utf-8")
```

## 9.5 Diretórios

```python
from pathlib import Path

diretorio = Path("data")
diretorio.mkdir(parents=True, exist_ok=True)

for arquivo in diretorio.iterdir():
    print(arquivo)
```

## 9.6 JSON

```python
import json

dados = {
    "nome": "Ana",
    "idade": 30
}

with open("usuario.json", "w", encoding="utf-8") as arquivo:
    json.dump(dados, arquivo, indent=2, ensure_ascii=False)
```

Leitura:

```python
with open("usuario.json", encoding="utf-8") as arquivo:
    dados = json.load(arquivo)
```

## 9.7 CSV

```python
import csv

with open("usuarios.csv", "w", newline="", encoding="utf-8") as arquivo:
    writer = csv.writer(arquivo)
    writer.writerow(["id", "nome"])
    writer.writerow([1, "Ana"])
```

## 9.8 Arquivos binários

```python
with open("imagem.png", "rb") as arquivo:
    dados = arquivo.read()
```

---

# 10. Exceções e tratamento de erros

## 10.1 try/except

```python
try:
    valor = int(input("Número: "))
except ValueError:
    print("Número inválido")
```

## 10.2 else/finally

```python
try:
    resultado = 10 / 2
except ZeroDivisionError:
    print("Divisão por zero")
else:
    print(resultado)
finally:
    print("Finalizado")
```

## 10.3 Exceções customizadas

```python
class SaldoInsuficienteError(Exception):
    pass
```

Uso:

```python
if saldo < valor:
    raise SaldoInsuficienteError("Saldo insuficiente")
```

## 10.4 Exceções encadeadas

```python
try:
    int("abc")
except ValueError as exc:
    raise RuntimeError("Falha ao converter") from exc
```

---

# 11. Módulos, pacotes e ambientes

## 11.1 Import

```python
import math
from pathlib import Path
```

## 11.2 Módulo próprio

```text
projeto/
├── app.py
└── calculadora.py
```

```python
# calculadora.py
def somar(a, b):
    return a + b
```

```python
# app.py
from calculadora import somar

print(somar(2, 3))
```

## 11.3 Pacote

```text
app/
├── __init__.py
├── domain/
├── application/
└── infrastructure/
```

## 11.4 Ambiente virtual

```bash
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

## 11.5 Dependências

```bash
python -m pip install fastapi uvicorn
```

```bash
python -m pip freeze > requirements.txt
```

---

# 12. Programação Orientada a Objetos

## 12.1 Classe

```python
class Pessoa:
    def __init__(self, nome, idade):
        self.nome = nome
        self.idade = idade

    def apresentar(self):
        return f"Sou {self.nome}"
```

## 12.2 Instância

```python
pessoa = Pessoa("Ana", 30)
print(pessoa.apresentar())
```

## 12.3 Encapsulamento

```python
class Conta:
    def __init__(self, saldo):
        self._saldo = saldo

    @property
    def saldo(self):
        return self._saldo
```

## 12.4 Herança

```python
class Animal:
    def falar(self):
        raise NotImplementedError


class Cachorro(Animal):
    def falar(self):
        return "Au au"
```

## 12.5 Polimorfismo

```python
animais = [Cachorro()]

for animal in animais:
    print(animal.falar())
```

## 12.6 Composição

Prefira composição quando a relação não representa realmente um "é um":

```python
class Motor:
    def ligar(self):
        return "Motor ligado"


class Carro:
    def __init__(self):
        self.motor = Motor()

    def ligar(self):
        return self.motor.ligar()
```

---

# 13. Recursos avançados de OOP

## 13.1 Métodos de classe

```python
class Usuario:
    def __init__(self, nome):
        self.nome = nome

    @classmethod
    def convidado(cls):
        return cls("Convidado")
```

## 13.2 Métodos estáticos

```python
class Matematica:
    @staticmethod
    def somar(a, b):
        return a + b
```

## 13.3 Property setter

```python
class Produto:
    def __init__(self, preco):
        self.preco = preco

    @property
    def preco(self):
        return self._preco

    @preco.setter
    def preco(self, valor):
        if valor < 0:
            raise ValueError("Preço inválido")
        self._preco = valor
```

## 13.4 Métodos mágicos

```python
class Produto:
    def __init__(self, nome):
        self.nome = nome

    def __str__(self):
        return self.nome

    def __repr__(self):
        return f"Produto(nome={self.nome!r})"
```

Outros:

```text
__len__
__iter__
__next__
__eq__
__lt__
__hash__
__enter__
__exit__
__call__
__getitem__
__setitem__
```

## 13.5 ABC

```python
from abc import ABC, abstractmethod

class Repositorio(ABC):

    @abstractmethod
    def salvar(self, entidade):
        pass
```

---

# 14. Type hints e tipagem

## 14.1 Tipos básicos

```python
def somar(a: int, b: int) -> int:
    return a + b
```

## 14.2 Coleções

```python
def nomes() -> list[str]:
    return ["Ana", "João"]

def usuario() -> dict[str, str]:
    return {"nome": "Ana"}
```

## 14.3 Optional

```python
def buscar(id: int) -> str | None:
    ...
```

## 14.4 Union

```python
def converter(valor: int | str):
    ...
```

## 14.5 Protocol

```python
from typing import Protocol

class Logger(Protocol):
    def info(self, mensagem: str) -> None:
        ...
```

## 14.6 Alias

```python
type UserId = int
```

> Type hints documentam contratos e permitem análise estática com ferramentas como mypy e pyright.

---

# 15. Dataclasses, enums e validação

## 15.1 Dataclass

```python
from dataclasses import dataclass

@dataclass
class Usuario:
    nome: str
    idade: int
```

## 15.2 Frozen

```python
@dataclass(frozen=True)
class Coordenada:
    x: float
    y: float
```

## 15.3 Enum

```python
from enum import Enum

class Status(Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
```

## 15.4 Validação

Validação de entrada pode ser centralizada em modelos:

```python
class CriarUsuario:
    nome: str
    email: str
    idade: int
```

A validação de entrada não deve substituir as regras de negócio.

---

# 16. Iteradores e generators

## 16.1 Iterator

```python
numeros = iter([1, 2, 3])

print(next(numeros))
print(next(numeros))
```

## 16.2 Generator

```python
def contar():
    for i in range(5):
        yield i
```

## 16.3 Generator expression

```python
quadrados = (x ** 2 for x in range(1_000_000))
```

Generators são úteis para processamento incremental e economia de memória.

---

# 17. Decorators e context managers

## 17.1 Decorator

```python
from functools import wraps

def logar(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Executando {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


@logar
def somar(a, b):
    return a + b
```

## 17.2 Context manager

```python
with open("arquivo.txt", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()
```

Criando um:

```python
from contextlib import contextmanager

@contextmanager
def recurso():
    print("Abrindo")
    try:
        yield
    finally:
        print("Fechando")
```

---

# 18. Programação funcional

## 18.1 map

```python
numeros = [1, 2, 3]
dobros = list(map(lambda x: x * 2, numeros))
```

## 18.2 filter

```python
pares = list(filter(lambda x: x % 2 == 0, numeros))
```

## 18.3 reduce

```python
from functools import reduce

total = reduce(lambda a, b: a + b, numeros)
```

Na prática, comprehensions e funções como `sum`, `any`, `all`, `min` e `max` frequentemente são mais legíveis.

---

# 19. Banco de dados

## 19.1 SQL básico

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);
```

Inserção:

```sql
INSERT INTO users (name, email)
VALUES ('Ana', 'ana@example.com');
```

Consulta:

```sql
SELECT id, name, email
FROM users;
```

Atualização:

```sql
UPDATE users
SET name = 'Ana Silva'
WHERE id = 1;
```

Exclusão:

```sql
DELETE FROM users
WHERE id = 1;
```

## 19.2 SQLite

```python
import sqlite3

connection = sqlite3.connect("app.db")
cursor = connection.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS users "
    "(id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
)

connection.commit()
connection.close()
```

## 19.3 Transações

```python
with sqlite3.connect("app.db") as connection:
    connection.execute(
        "INSERT INTO users (name) VALUES (?)",
        ("Ana",)
    )
```

Sempre use parâmetros para valores externos. Nunca monte SQL concatenando entrada do usuário.

---

# 20. CRUD completo

CRUD significa:

- Create
- Read
- Update
- Delete

## 20.1 Modelo

```python
from dataclasses import dataclass

@dataclass
class Usuario:
    id: int | None
    nome: str
    email: str
```

## 20.2 Repository

```python
class UsuarioRepository:

    def criar(self, usuario: Usuario) -> Usuario:
        ...

    def buscar_por_id(self, user_id: int) -> Usuario | None:
        ...

    def listar(self) -> list[Usuario]:
        ...

    def atualizar(self, usuario: Usuario) -> Usuario:
        ...

    def remover(self, user_id: int) -> None:
        ...
```

## 20.3 CRUD SQL

```sql
-- CREATE
INSERT INTO users (name, email)
VALUES (?, ?);

-- READ
SELECT id, name, email
FROM users
WHERE id = ?;

-- UPDATE
UPDATE users
SET name = ?, email = ?
WHERE id = ?;

-- DELETE
DELETE FROM users
WHERE id = ?;
```

## 20.4 CRUD profissional

Considere:

- validação;
- transações;
- constraints;
- índices;
- paginação;
- ordenação;
- filtros;
- tratamento de erros;
- concorrência;
- autorização;
- auditoria;
- migrations;
- testes.

---

# 21. ORM

Um ORM mapeia objetos para tabelas relacionais.

Conceitos:

- Entity/Model;
- Session;
- Query;
- Relationship;
- Transaction;
- Migration;
- Lazy loading;
- Eager loading.

Exemplo conceitual:

```python
class User:
    id: int
    name: str
    email: str
```

Operações típicas:

```python
session.add(user)
session.commit()

user = session.get(User, user_id)

session.delete(user)
session.commit()
```

Ferramentas populares do ecossistema incluem SQLAlchemy e Django ORM.

---

# 22. APIs REST

## 22.1 Recursos e verbos

```text
GET     /users
GET     /users/10
POST    /users
PUT     /users/10
PATCH   /users/10
DELETE  /users/10
```

## 22.2 Status HTTP

| Código | Significado |
|---|---|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## 22.3 JSON

```json
{
  "id": 1,
  "name": "Ana",
  "email": "ana@example.com"
}
```

## 22.4 Query parameters

```text
GET /users?page=1&limit=20
```

## 22.5 Headers

Exemplos:

```text
Authorization
Content-Type
Accept
X-Request-ID
```

---

# 23. API com FastAPI

## 23.1 Instalação

```bash
pip install fastapi uvicorn
```

## 23.2 Aplicação

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Olá, API!"}
```

Executar:

```bash
uvicorn main:app --reload
```

## 23.3 GET

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

## 23.4 POST

```python
from pydantic import BaseModel

class CreateUser(BaseModel):
    name: str
    email: str


@app.post("/users", status_code=201)
def create_user(data: CreateUser):
    return data
```

## 23.5 PUT

```python
@app.put("/users/{user_id}")
def update_user(user_id: int, data: CreateUser):
    return {
        "id": user_id,
        **data.model_dump()
    }
```

## 23.6 DELETE

```python
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    return None
```

## 23.7 Estrutura recomendada

```text
app/
├── main.py
├── api/
│   └── routes/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   └── repositories/
├── application/
│   └── use_cases/
├── infrastructure/
│   ├── database/
│   └── repositories/
└── tests/
```

---

# 24. Autenticação e autorização

## 24.1 Autenticação

Responde:

> Quem é o usuário?

Mecanismos:

- sessão;
- OAuth2;
- OpenID Connect;
- JWT;
- API keys.

## 24.2 Autorização

Responde:

> O usuário pode executar esta ação?

Modelos:

- RBAC;
- ABAC;
- ACL;
- policies.

## 24.3 JWT

Estrutura:

```text
header.payload.signature
```

Nunca coloque segredos no payload.

## 24.4 Senhas

Nunca armazene senhas em texto puro. Use algoritmos apropriados de password hashing, como Argon2id ou bcrypt, por meio de bibliotecas confiáveis.

---

# 25. DDD

Domain-Driven Design organiza o software em torno do domínio do negócio.

## 25.1 Conceitos

- Domain;
- Entity;
- Value Object;
- Aggregate;
- Aggregate Root;
- Repository;
- Domain Service;
- Application Service;
- Domain Event;
- Bounded Context;
- Ubiquitous Language.

## 25.2 Entity

Possui identidade:

```python
class Pedido:
    def __init__(self, pedido_id, cliente_id):
        self.id = pedido_id
        self.cliente_id = cliente_id
```

## 25.3 Value Object

É definido por seus valores:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Email inválido")
```

## 25.4 Aggregate

```text
Pedido
├── ItemPedido
├── ItemPedido
└── ItemPedido
```

O `Pedido` pode ser o Aggregate Root.

## 25.5 Domain Service

Quando uma regra não pertence naturalmente a uma entidade específica:

```python
class CalculadoraFrete:
    def calcular(self, pedido):
        ...
```

## 25.6 Domain Event

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PedidoCriado:
    pedido_id: int
```

## 25.7 Bounded Context

Divida sistemas grandes por contextos:

```text
Vendas
├── Pedido
├── Carrinho
└── Cliente

Financeiro
├── Fatura
├── Pagamento
└── Reembolso
```

---

# 26. Arquitetura em camadas

Uma separação comum:

```text
Presentation
     ↓
Application
     ↓
Domain
     ↓
Infrastructure
```

## Presentation

Responsável por HTTP, CLI, entrada e saída.

## Application

Orquestra casos de uso:

```python
class CriarPedido:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, command):
        ...
```

## Domain

Contém regras de negócio.

## Infrastructure

Contém banco, mensageria, filesystem e serviços externos.

---

# 27. SOLID e Design Patterns

## 27.1 Single Responsibility

Uma classe deve possuir uma responsabilidade bem definida.

## 27.2 Open/Closed

Software deve permitir extensão sem exigir alterações constantes no código existente.

## 27.3 Liskov Substitution

Subtipos devem respeitar o contrato de seus tipos base.

## 27.4 Interface Segregation

Interfaces menores são preferíveis a contratos gigantes.

## 27.5 Dependency Inversion

Regras de negócio não devem depender diretamente de detalhes de infraestrutura.

## 27.6 Patterns importantes

### Factory

```python
class UserFactory:
    @staticmethod
    def create(nome):
        return Usuario(nome)
```

### Strategy

```python
class Desconto:
    def calcular(self, valor):
        raise NotImplementedError
```

### Repository

Abstrai persistência.

### Adapter

Converte uma interface em outra.

### Facade

Simplifica uma API complexa.

### Observer

Permite comunicação baseada em eventos.

### Builder

Facilita construção de objetos complexos.

> Design patterns devem resolver problemas reais, não apenas aumentar a complexidade do projeto.

---

# 28. Testes

## 28.1 Teste unitário

Com pytest:

```bash
pip install pytest
```

```python
def somar(a, b):
    return a + b


def test_somar():
    assert somar(2, 3) == 5
```

Executar:

```bash
pytest
```

## 28.2 Fixtures

```python
import pytest

@pytest.fixture
def usuario():
    return {"name": "Ana"}
```

## 28.3 Parametrização

```python
@pytest.mark.parametrize(
    "a,b,resultado",
    [
        (1, 2, 3),
        (2, 2, 4),
        (5, 5, 10),
    ],
)
def test_soma(a, b, resultado):
    assert a + b == resultado
```

## 28.4 Mock

```python
from unittest.mock import Mock

repository = Mock()
repository.buscar.return_value = {"id": 1}
```

## 28.5 Pirâmide de testes

Priorize:

1. testes unitários;
2. testes de integração;
3. testes de contrato;
4. testes end-to-end.

---

# 29. Logging e observabilidade

## 29.1 Logging

```python
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

logger.info("Aplicação iniciada")
logger.warning("Operação lenta")
logger.error("Falha")
```

## 29.2 Structured logging

```json
{
  "level": "INFO",
  "event": "user_created",
  "user_id": 10
}
```

## 29.3 Observabilidade

Três pilares:

- logs;
- métricas;
- traces.

Conceitos:

```text
request_id
trace_id
span_id
latency
throughput
error_rate
```

---

# 30. Concorrência e paralelismo

## 30.1 Threading

Útil principalmente para tarefas I/O-bound:

```python
from threading import Thread

def tarefa():
    print("Executando")

thread = Thread(target=tarefa)
thread.start()
thread.join()
```

## 30.2 Asyncio

```python
import asyncio

async def tarefa():
    await asyncio.sleep(1)
    return "ok"

resultado = asyncio.run(tarefa())
```

## 30.3 Gather

```python
resultados = await asyncio.gather(
    tarefa(),
    tarefa(),
    tarefa(),
)
```

## 30.4 Multiprocessing

Útil para tarefas CPU-bound:

```python
from multiprocessing import Process

def trabalho():
    print("CPU")

p = Process(target=trabalho)
p.start()
p.join()
```

## 30.5 Escolha

```text
I/O-bound → asyncio/threading
CPU-bound → multiprocessing
```

A escolha deve ser validada com medições e com o perfil real da aplicação.

---

# 31. Performance

## 31.1 Complexidade

Conheça:

```text
O(1)
O(log n)
O(n)
O(n log n)
O(n²)
```

## 31.2 Profiling

```bash
python -m cProfile app.py
```

## 31.3 Benchmark

```python
import timeit

resultado = timeit.timeit(
    "sum(range(1000))",
    number=10000
)

print(resultado)
```

## 31.4 Processo de otimização

1. medir;
2. localizar gargalo;
3. formular hipótese;
4. alterar;
5. medir novamente;
6. validar comportamento.

Evite otimização prematura.

---

# 32. Segurança

## 32.1 Princípios

- validar entrada;
- aplicar menor privilégio;
- proteger secrets;
- atualizar dependências;
- usar TLS;
- evitar SQL injection;
- evitar command injection;
- controlar uploads;
- limitar requisições;
- registrar eventos relevantes;
- não expor stack traces ao cliente.

## 32.2 Secrets

Não faça:

```python
DATABASE_PASSWORD = "senha-super-secreta"
```

Prefira:

```python
import os

password = os.environ["DATABASE_PASSWORD"]
```

## 32.3 SQL Injection

Evite:

```python
query = f"SELECT * FROM users WHERE name = '{name}'"
```

Prefira parâmetros:

```python
cursor.execute(
    "SELECT * FROM users WHERE name = ?",
    (name,)
)
```

---

# 33. Mensageria e sistemas distribuídos

Conceitos:

- Producer;
- Consumer;
- Queue;
- Topic;
- Broker;
- Message;
- Retry;
- Dead Letter Queue;
- Idempotência;
- Eventual consistency.

Exemplos de tecnologias:

```text
RabbitMQ
Kafka
Redis Streams
NATS
```

## 33.1 Idempotência

Uma operação idempotente pode ser repetida sem produzir efeitos indevidos adicionais.

Exemplo:

```text
POST /payments
Idempotency-Key: abc123
```

O servidor registra a chave e evita processar o mesmo pagamento duas vezes.

---

# 34. Cache

## 34.1 Cache local

```python
from functools import lru_cache

@lru_cache
def calcular(valor):
    return valor * 2
```

## 34.2 Cache distribuído

Redis é uma opção comum.

Conceitos:

- TTL;
- invalidation;
- cache-aside;
- write-through;
- write-behind;
- stampede protection.

> Cache melhora latência, mas adiciona complexidade de consistência.

---

# 35. WebSockets

WebSockets permitem comunicação bidirecional persistente.

Exemplo com FastAPI:

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        mensagem = await websocket.receive_text()
        await websocket.send_text(f"Recebido: {mensagem}")
```

Casos:

- chat;
- notificações;
- dashboards;
- colaboração em tempo real;
- monitoramento.

---

# 36. CLI

## 36.1 argparse

```python
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("nome")
parser.add_argument("--idade", type=int)

args = parser.parse_args()

print(args.nome, args.idade)
```

## 36.2 CLI profissional

```text
app create-user
app list-users
app delete-user 10
app migrate
```

Bibliotecas como Typer e Click facilitam CLIs maiores.

---

# 37. Processamento de dados

## 37.1 CSV

```python
import csv

with open("dados.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        print(row)
```

## 37.2 Pandas

```python
import pandas as pd

df = pd.read_csv("dados.csv")

print(df.head())
print(df.describe())
```

## 37.3 Transformações

```python
df["total"] = df["preco"] * df["quantidade"]

resultado = (
    df.groupby("categoria")["total"]
      .sum()
)
```

## 37.4 Processamento em escala

Para volumes maiores, avalie:

- processamento por chunks;
- Spark/PySpark;
- Dask;
- Polars;
- bancos analíticos;
- data warehouses;
- pipelines distribuídos.

---

# 38. Automação

Python pode automatizar:

- arquivos;
- relatórios;
- APIs;
- bancos;
- tarefas administrativas;
- processamento de dados;
- integração entre sistemas;
- testes;
- deploy.

Exemplo:

```python
from pathlib import Path

origem = Path("entrada")
destino = Path("processados")

destino.mkdir(exist_ok=True)

for arquivo in origem.glob("*.txt"):
    conteudo = arquivo.read_text(encoding="utf-8")
    novo = conteudo.upper()
    (destino / arquivo.name).write_text(novo, encoding="utf-8")
```

---

# 39. DevOps

## 39.1 Pipeline

```text
Código
 ↓
Git
 ↓
Testes
 ↓
Lint
 ↓
Build
 ↓
Docker
 ↓
CI
 ↓
CD
 ↓
Deploy
 ↓
Monitoramento
```

## 39.2 Git

```bash
git init
git add .
git commit -m "feat: primeira implementação"
git branch
git checkout
git merge
git pull
git push
```

## 39.3 Qualidade

Ferramentas do ecossistema:

```text
pytest
ruff
black
mypy
pyright
pre-commit
```

---

# 40. Docker

## 40.1 Dockerfile

```dockerfile
FROM python:3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

## 40.2 Build

```bash
docker build -t minha-api .
```

## 40.3 Run

```bash
docker run --rm -p 8000:8000 minha-api
```

## 40.4 Boas práticas

- imagem mínima;
- usuário não-root;
- `.dockerignore`;
- dependências reproduzíveis;
- healthcheck;
- configuração via ambiente;
- não incluir secrets na imagem.

---

# 41. CI/CD

## 41.1 Pipeline

Uma pipeline Python pode executar:

```text
checkout
 ↓
setup Python
 ↓
install dependencies
 ↓
lint
 ↓
type check
 ↓
unit tests
 ↓
integration tests
 ↓
build image
 ↓
security scan
 ↓
publish
 ↓
deploy
```

## 41.2 GitHub Actions

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"

      - run: pip install -r requirements.txt
      - run: pytest
```

---

# 42. Arquiteturas avançadas

## 42.1 Clean Architecture

```text
Entities
   ↑
Use Cases
   ↑
Adapters
   ↑
Frameworks/Drivers
```

Dependências devem apontar para dentro.

## 42.2 Hexagonal Architecture

Também conhecida como Ports and Adapters:

```text
             HTTP
              |
          [Adapter]
              |
[Adapter] → [Port] → [Domain]
              |
          [Port]
              |
          Database
```

## 42.3 CQRS

Separa:

```text
Command → alteração
Query   → leitura
```

## 42.4 Event-driven

```text
Pedido criado
      ↓
Domain Event
      ↓
Message Broker
   ↙   ↓   ↘
Email  Estoque  Financeiro
```

## 42.5 Microservices

Cada serviço deve possuir uma responsabilidade e fronteira de negócio clara.

Evite transformar um monólito simples em dezenas de serviços sem necessidade.

---

# 43. Boas práticas

## 43.1 PEP 8

Siga convenções de estilo.

## 43.2 Nomes

Prefira:

```python
quantidade_produtos = 10
```

Em vez de:

```python
q = 10
```

## 43.3 Funções pequenas

Prefira funções com responsabilidade clara.

## 43.4 Baixo acoplamento

Evite classes que conhecem detalhes internos de muitas outras classes.

## 43.5 Alta coesão

Mantenha responsabilidades relacionadas juntas.

## 43.6 Configuração externa

```text
Código
+
Configuração
+
Secrets
```

Não misture secrets ao código-fonte.

## 43.7 Dependências

Mantenha dependências atualizadas e utilize versões controladas quando precisar de builds reproduzíveis.

## 43.8 Documentação

Documente:

- decisões arquiteturais;
- contratos;
- APIs;
- configuração;
- execução;
- troubleshooting;
- regras de negócio relevantes.

---

# 44. Projetos progressivos

## Nível 1 — Iniciante

### Projeto 1: Calculadora

Requisitos:

- operações básicas;
- entrada do usuário;
- tratamento de erros;
- funções.

### Projeto 2: Lista de tarefas

Requisitos:

- criar;
- listar;
- concluir;
- remover;
- salvar em JSON.

---

## Nível 2 — Intermediário

### Projeto 3: Sistema de usuários

Requisitos:

- OOP;
- CRUD;
- SQLite;
- repository;
- validação;
- testes.

### Projeto 4: Gerenciador de arquivos

Requisitos:

- pathlib;
- leitura;
- escrita;
- busca;
- regex;
- processamento em lote.

---

## Nível 3 — Backend

### Projeto 5: API REST

Requisitos:

- FastAPI;
- CRUD;
- PostgreSQL;
- ORM;
- migrations;
- validação;
- autenticação;
- paginação;
- filtros;
- testes.

Estrutura:

```text
src/
├── main.py
├── api/
├── application/
├── domain/
├── infrastructure/
└── tests/
```

---

## Nível 4 — Arquitetura

### Projeto 6: E-commerce

Módulos:

```text
Identity
Catalog
Cart
Order
Payment
Inventory
Shipping
Notification
```

Aplicar:

- DDD;
- Clean Architecture;
- SOLID;
- Repository;
- Unit of Work;
- eventos;
- testes;
- observabilidade.

---

## Nível 5 — Distribuído

### Projeto 7: Plataforma de processamento

Componentes:

```text
API
 ↓
Queue
 ↓
Workers
 ↓
Database
 ↓
Cache
 ↓
Object Storage
 ↓
Monitoring
```

Requisitos:

- processamento assíncrono;
- retries;
- idempotência;
- DLQ;
- métricas;
- tracing;
- Docker;
- CI/CD.

---

# 45. Checklist de domínio

## Básico

- [ ] Sintaxe
- [ ] Variáveis
- [ ] Tipos
- [ ] Operadores
- [ ] Condicionais
- [ ] Loops
- [ ] Funções
- [ ] Strings
- [ ] Listas
- [ ] Tuplas
- [ ] Sets
- [ ] Dicionários

## Intermediário

- [ ] Exceptions
- [ ] Módulos
- [ ] Pacotes
- [ ] Virtual environments
- [ ] Filesystem
- [ ] JSON
- [ ] CSV
- [ ] Regex
- [ ] OOP
- [ ] Dataclasses
- [ ] Type hints
- [ ] Decorators
- [ ] Context managers
- [ ] Iterators
- [ ] Generators

## Backend

- [ ] HTTP
- [ ] REST
- [ ] FastAPI
- [ ] CRUD
- [ ] SQL
- [ ] PostgreSQL
- [ ] ORM
- [ ] Migrations
- [ ] Authentication
- [ ] Authorization
- [ ] Pagination
- [ ] Validation
- [ ] OpenAPI

## Engenharia de software

- [ ] SOLID
- [ ] Design Patterns
- [ ] DDD
- [ ] Clean Architecture
- [ ] Hexagonal Architecture
- [ ] Dependency Injection
- [ ] Repository
- [ ] Unit of Work
- [ ] Domain Events
- [ ] CQRS

## Qualidade

- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E
- [ ] Mocking
- [ ] Coverage
- [ ] Lint
- [ ] Formatting
- [ ] Static typing
- [ ] Code review

## Sistemas avançados

- [ ] Asyncio
- [ ] Threading
- [ ] Multiprocessing
- [ ] Queues
- [ ] Brokers
- [ ] Redis
- [ ] Caching
- [ ] WebSockets
- [ ] Observability
- [ ] Distributed systems
- [ ] Event-driven architecture

## DevOps

- [ ] Git
- [ ] Docker
- [ ] Docker Compose
- [ ] CI/CD
- [ ] Secrets
- [ ] Health checks
- [ ] Monitoring
- [ ] Deployment
- [ ] Rollback
- [ ] Infrastructure basics

---

# Conclusão

Dominar Python profissionalmente vai muito além de conhecer sua sintaxe. O caminho completo envolve:

```text
Python
  ↓
Fundamentos
  ↓
OOP
  ↓
Type Hints
  ↓
Arquivos
  ↓
Regex
  ↓
Banco de Dados
  ↓
CRUD
  ↓
APIs REST
  ↓
Testes
  ↓
SOLID
  ↓
DDD
  ↓
Clean/Hexagonal Architecture
  ↓
Async/Concurrency
  ↓
Mensageria
  ↓
Cache
  ↓
Observabilidade
  ↓
Segurança
  ↓
Docker
  ↓
CI/CD
  ↓
Sistemas Distribuídos
```

A evolução deve acontecer por projetos. O objetivo não é apenas memorizar recursos da linguagem, mas aprender a projetar, implementar, testar, proteger, observar e operar sistemas reais usando Python.
