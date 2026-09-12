> ⚠️ **DOCUMENTO HISTÓRICO — não reflete a implementação atual.**
>
> Documentação da v3.0 com exemplos que **não compilam** na versão atual. Use `doc/TUTORIAL.md` e `doc/REFERENCIA.md`.
>
> **Documentação vigente:** [`doc/TUTORIAL.md`](TUTORIAL.md) · [`doc/REFERENCIA.md`](REFERENCIA.md) · [`doc/BIBLIOTECA_PADRAO.md`](BIBLIOTECA_PADRAO.md) · [`doc/INSTALACAO.md`](INSTALACAO.md)

---

# 📖 DataForge — Documentação Completa

> **DataForge v3.0** — Uma linguagem de programação inovadora construída sobre Python, com sintaxe única e palavras reservadas totalmente originais.

---

## 📑 Índice

1. [Instalação e Configuração](#1-instalação-e-configuração)
2. [Primeiros Passos](#2-primeiros-passos)
3. [Variáveis e Tipos de Dados](#3-variáveis-e-tipos-de-dados)
4. [Operadores](#4-operadores)
5. [Saída e Entrada de Dados](#5-saída-e-entrada-de-dados)
6. [Controle de Fluxo](#6-controle-de-fluxo)
7. [Loops (Repetição)](#7-loops-repetição)
8. [Ações (Funções)](#8-ações-funções)
9. [Blueprints (Classes)](#9-blueprints-classes)
10. [Traits (Interfaces)](#10-traits-interfaces)
11. [Tratamento de Erros](#11-tratamento-de-erros)
12. [Pipelines de Dados](#12-pipelines-de-dados)
13. [Módulos e Imports](#13-módulos-e-imports)
14. [Concorrência](#14-concorrência)
15. [Funções Embutidas](#15-funções-embutidas)
16. [Biblioteca Padrão](#16-biblioteca-padrão)
17. [REPL Interativo](#17-repl-interativo)
18. [Referência de Palavras Reservadas](#18-referência-de-palavras-reservadas)
19. [Guia de Estilo](#19-guia-de-estilo)
20. [Solução de Problemas](#20-solução-de-problemas)
21. [Novidades v3.0 — Métodos de String Avançados](#21-novidades-v30--métodos-de-string-avançados)
22. [Novidades v3.0 — Regex & Padrões](#22-novidades-v30--regex--padrões)
23. [Novidades v3.0 — Tratamento de Erros Avançado](#23-novidades-v30--tratamento-de-erros-avançado)
24. [Novidades v3.0 — Programação Funcional](#24-novidades-v30--programação-funcional)
25. [Novidades v3.0 — Matemática e Estatística Avançada](#25-novidades-v30--matemática-e-estatística-avançada)
26. [Novidades v3.0 — Coleções Avançadas & Tipagem](#26-novidades-v30--coleções-avançadas--tipagem)
27. [Novidades v3.0 — Programação Reativa & Streams](#27-novidades-v30--programação-reativa--streams)
28. [Novidades v3.0 — Framework de Testes](#28-novidades-v30--framework-de-testes)
29. [Novidades v3.0 — Programação Modular](#29-novidades-v30--programação-modular)
30. [Novidades v3.0 — Novos Módulos da Biblioteca Padrão](#30-novidades-v30--novos-módulos-da-biblioteca-padrão)
31. [Referência Completa de Funções Embutidas v3.0](#31-referência-completa-de-funções-embutidas-v30)

---

## 1. Instalação e Configuração

### Requisitos
- **Python 3.10** ou superior
- Sistema operacional: Windows, macOS ou Linux

### Instalação Local (Desenvolvimento)

```bash
# 1. Clone ou baixe o repositório
git clone https://github.com/seu-usuario/DataForge.git
cd DataForge

# 2. Instale em modo de desenvolvimento
pip install -e .

# 3. Verifique a instalação
dataforge version
```

### Instalação Rápida (pip)

```bash
pip install dataforge-lang
```

### Instalação Manual (sem pip)

```bash
# Navegue até o diretório do DataForge
cd /caminho/para/DataForge

# Execute diretamente com Python
python3 -m dataforge version
```

### Verificando a Instalação

```bash
# Qualquer um destes comandos funciona:
dataforge version        # Se instalado com pip
df version               # Alias curto
python3 -m dataforge version  # Execução direta
```

Saída esperada:
```
DataForge v2.0.0
```

---

## 2. Primeiros Passos

### Seu Primeiro Programa

Crie um arquivo chamado `hello.df`:

```
out "Hello, World!"
out "Bem-vindo ao DataForge!"
```

Execute:
```bash
dataforge run hello.df
# ou
python3 -m dataforge run hello.df
```

### Usando o REPL Interativo

```bash
dataforge repl
# ou
python3 -m dataforge repl
```

No REPL:
```
DataForge> out "Olá!"
Olá!
DataForge> x := 42
DataForge> out x * 2
84
```

### Comandos CLI Disponíveis

| Comando | Descrição |
|---------|-----------|
| `dataforge run arquivo.df` | Executa um programa |
| `dataforge repl` | Inicia o REPL interativo |
| `dataforge check arquivo.df` | Verifica erros de sintaxe |
| `dataforge tokens arquivo.df` | Mostra os tokens gerados |
| `dataforge ast arquivo.df` | Mostra a árvore sintática |
| `dataforge version` | Mostra a versão |
| `dataforge help` | Mostra ajuda |

### Flags Disponíveis

| Flag | Descrição |
|------|-----------|
| `--debug` | Modo debug com informações extras |
| `--time` | Mostra tempo de execução |
| `--no-color` | Desativa cores na saída |

---

## 3. Variáveis e Tipos de Dados

### Declaração de Variáveis

DataForge usa `:=` para atribuição (não `=`):

```
// Variável mutável
nome := "DataForge"
idade := 25
preco := 99.99
ativo := yes

// Constante (imutável) com 'steady'
steady PI := 3.14159
steady MAX := 100

// Variável de escopo local com 'shadow'
shadow temp := "temporário"
```

### Tipos de Dados

| Tipo DataForge | Equivalente Python | Exemplo |
|----------------|-------------------|---------|
| Integer | int | `42`, `0xFF`, `0b1010` |
| Float | float | `3.14`, `2.0` |
| String | str | `"texto"`, `'texto'` |
| Boolean | bool | `yes`, `no` |
| Void | None | `void` |
| Cluster | list | `[1, 2, 3]` |
| Vault | dict | `{"key": "value"}` |

### Strings

```
// String com aspas duplas
msg := "Hello, World!"

// String com aspas simples
msg2 := 'Hello!'

// String multilinha (triple quotes)
texto := """
    Esta é uma string
    com múltiplas linhas
"""

// Escape sequences
nova_linha := "Linha1\nLinha2"
tab := "Col1\tCol2"
```

### Clusters (Listas)

```
// Criação
numeros := [1, 2, 3, 4, 5]
nomes := ["Ana", "Bruno", "Carlos"]
misto := [1, "dois", yes, 3.14]
vazio := []

// Acesso por índice (começa em 0)
primeiro := numeros[0]    // 1
ultimo := numeros[4]      // 5

// Modificação
numeros[0] := 10

// Métodos de lista
numeros.append(6)
numeros.pop()
numeros.sort()
numeros.reverse()
tamanho := numeros.length()
```

### Vaults (Dicionários)

```
// Criação
pessoa := {"nome": "João", "idade": 30, "cidade": "SP"}

// Acesso
nome := pessoa["nome"]

// Modificação
pessoa["email"] := "joao@email.com"

// Verificação
tem_nome := contains(pessoa, "nome")    // yes
```

### Verificação de Tipo

```
x := 42
out typeof x          // Integer

nome := "DataForge"
out typeof nome       // String

lista := [1, 2, 3]
out typeof lista      // Cluster
```

### Conversão de Tipo (Cast)

```
numero_str := "42"
numero := cast numero_str as int       // 42

valor := 3.14
inteiro := cast valor as int           // 3

lista := cast "hello" as list          // ['h', 'e', 'l', 'l', 'o']
```

---

## 4. Operadores

### Operadores Aritméticos

| Operador | Descrição | Exemplo |
|----------|-----------|---------|
| `+` | Adição | `5 + 3` → `8` |
| `-` | Subtração | `5 - 3` → `2` |
| `*` | Multiplicação | `5 * 3` → `15` |
| `/` | Divisão | `10 / 3` → `3.333...` |
| `//` | Divisão inteira | `10 // 3` → `3` |
| `%` | Módulo (resto) | `10 % 3` → `1` |
| `**` | Potência | `2 ** 10` → `1024` |
| `-x` | Negação | `-5` |

### Operadores de Comparação

| Operador | Equivalente | Descrição |
|----------|-------------|-----------|
| `is` | `==` | Igual a |
| `isnt` | `!=` | Diferente de |
| `bigger` | `>` | Maior que |
| `smaller` | `<` | Menor que |
| `bigger_eq` | `>=` | Maior ou igual |
| `smaller_eq` | `<=` | Menor ou igual |

```
x := 10
y := 20

out x is 10           // yes
out x isnt y           // yes
out y bigger x         // yes
out x smaller y        // yes
out x bigger_eq 10     // yes
out y smaller_eq 20    // yes
```

### Operadores Lógicos

| Operador | Descrição |
|----------|-----------|
| `and` | E lógico |
| `or` | OU lógico |
| `not` | Negação lógica |

```
a := yes
b := no

out a and b           // no
out a or b            // yes
out not a             // no
out not b             // yes
```

### Operador de Pipeline

```
// >> envia dados para operações encadeadas
resultado := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] >> sift n: n % 2 is 0 >> morph n: n * n
// resultado = [4, 16, 36, 64, 100]
```

### Concatenação de Strings

```
nome := "Data" + "Forge"       // "DataForge"
msg := "Valor: " + 42          // "Valor: 42" (conversão automática)
```

---

## 5. Saída e Entrada de Dados

### Saída (out)

```
// Imprimir texto
out "Hello, World!"

// Imprimir variáveis
nome := "DataForge"
out nome

// Imprimir múltiplos valores (separados por espaço)
out "Nome:", nome, "- Versão:", 2

// Imprimir expressões
out 2 + 3
out "Resultado:", 10 * 5

// Saída sem argumentos (linha vazia)
out
```

### Entrada (in)

```
// Ler entrada do usuário
nome := in "Digite seu nome: "
out "Olá, " + nome + "!"

// Converter entrada para número
idade_str := in "Digite sua idade: "
idade := cast idade_str as int
out "Você tem", idade, "anos"
```

### Inspeção (Debug)

```
x := [1, 2, 3]
inspect x
// Saída: [INSPECT] type=Cluster value=[1, 2, 3]
```

---

## 6. Controle de Fluxo

### Condicional (given / orif / otherwise)

Equivalente a `if / elif / else`:

```
idade := 18

given idade bigger_eq 18:
    out "Adulto"
orif idade bigger_eq 13:
    out "Adolescente"
otherwise:
    out "Criança"
```

### Condicional Aninhado

```
nota := 85

given nota bigger_eq 90:
    out "A - Excelente"
orif nota bigger_eq 80:
    out "B - Bom"
orif nota bigger_eq 70:
    out "C - Regular"
orif nota bigger_eq 60:
    out "D - Suficiente"
otherwise:
    out "F - Insuficiente"
```

### Match (Switch/Case)

```
dia := "segunda"

match dia:
    point "segunda":
        out "Início da semana"
    point "sexta":
        out "Quase fim de semana!"
    point "sabado":
        out "Fim de semana!"
    point "domingo":
        out "Fim de semana!"
    default:
        out "Dia normal"
```

### Expressões Lógicas em Condições

```
idade := 25
tem_carteira := yes

given idade bigger_eq 18 and tem_carteira:
    out "Pode dirigir"
otherwise:
    out "Não pode dirigir"
```

---

## 7. Loops (Repetição)

### Cycle From-To (For com Range)

```
// Contar de 1 a 10
cycle i from 1 to 10:
    out i

// Com passo (step)
cycle i from 0 to 20 step 2:
    out i    // 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20

// Contagem regressiva
cycle i from 10 to 1 step -1:
    out i
```

### Cycle In (For-Each)

```
// Iterar sobre lista
frutas := ["maçã", "banana", "laranja"]
cycle fruta in frutas:
    out "Fruta:", fruta

// Iterar sobre string
cycle letra in "DataForge":
    out letra

// Com enumerate
cycle par in enumerate(["a", "b", "c"]):
    out par    // [0, a], [1, b], [2, c]
```

### Persist (While)

```
contador := 0
persist contador smaller 5:
    out "Contagem:", contador
    contador := contador + 1
```

### Perform (Do-While)

```
x := 1
perform:
    out "x =", x
    x := x + 1
persist x smaller_eq 5
```

### Controladores de Loop

```
// halt = break (parar o loop)
cycle i from 1 to 100:
    given i is 5:
        halt
    out i    // 1, 2, 3, 4

// skip = continue (pular iteração)
cycle i from 1 to 10:
    given i % 2 is 0:
        skip
    out i    // 1, 3, 5, 7, 9
```

---

## 8. Ações (Funções)

### Declaração Básica

```
action saudar(nome):
    out "Olá, " + nome + "!"

saudar("Maria")    // Olá, Maria!
```

### Retorno de Valor (yield)

```
action somar(a, b):
    yield a + b

resultado := somar(5, 3)
out resultado    // 8
```

### Parâmetros com Valor Padrão

```
action cumprimentar(nome, saudacao := "Olá"):
    out saudacao + ", " + nome + "!"

cumprimentar("João")            // Olá, João!
cumprimentar("Maria", "Bom dia")  // Bom dia, Maria!
```

### Funções Recursivas

```
action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

out fatorial(5)     // 120
out fatorial(10)    // 3628800
```

### Funções como Objetos de Primeira Classe

```
action dobro(x):
    yield x * 2

action triplo(x):
    yield x * 3

action aplicar(func, valor):
    yield func(valor)

out aplicar(dobro, 5)     // 10
out aplicar(triplo, 5)    // 15
```

### Closures

```
action criar_contador():
    contagem := 0
    action incrementar():
        contagem := contagem + 1
        yield contagem
    yield incrementar

contador := criar_contador()
out contador()    // 1
out contador()    // 2
out contador()    // 3
```

---

## 9. Blueprints (Classes)

### Declaração Básica

```
blueprint Animal:
    action setup(nome, som):
        self.nome := nome
        self.som := som

    action falar():
        out self.nome + " diz: " + self.som

gato := spawn Animal("Felix", "Miau!")
gato.falar()    // Felix diz: Miau!
```

### Herança

```
blueprint Veiculo:
    action setup(marca, ano):
        self.marca := marca
        self.ano := ano

    action info():
        out self.marca + " (" + str(self.ano) + ")"

blueprint Carro(Veiculo):
    action setup(marca, ano, portas):
        self.marca := marca
        self.ano := ano
        self.portas := portas

    action detalhes():
        self.info()
        out "Portas:", self.portas

meu_carro := spawn Carro("Toyota", 2024, 4)
meu_carro.detalhes()
// Toyota (2024)
// Portas: 4
```

### Variáveis Estáticas

```
blueprint Contador:
    static total := 0

    action setup():
        Contador.total := Contador.total + 1
        self.id := Contador.total

    action mostrar():
        out "Objeto #" + str(self.id) + " de " + str(Contador.total)

a := spawn Contador()
b := spawn Contador()
c := spawn Contador()
c.mostrar()    // Objeto #3 de 3
```

### Métodos Encadeados

```
blueprint Builder:
    action setup():
        self.items := []

    action add(item):
        self.items.append(item)
        yield self

    action build():
        yield self.items

resultado := spawn Builder()
lista := resultado.add("A").add("B").add("C").build()
out lista    // [A, B, C]
```

---

## 10. Traits (Interfaces)

```
trait Exibivel:
    action exibir()

trait Calculavel:
    action calcular()

blueprint Produto(Exibivel, Calculavel):
    action setup(nome, preco, qtd):
        self.nome := nome
        self.preco := preco
        self.qtd := qtd

    action exibir():
        out self.nome + " - R$" + str(self.preco)

    action calcular():
        yield self.preco * self.qtd

p := spawn Produto("Notebook", 3500.0, 2)
p.exibir()                     // Notebook - R$3500.0
out "Total:", p.calcular()     // Total: 7000.0
```

---

## 11. Tratamento de Erros

### Monitor / Handle / Ensure

Equivalente a `try / catch / finally`:

```
monitor:
    // Código que pode gerar erro
    resultado := 10 / 0
handle erro:
    // Tratamento do erro
    out "Erro capturado:", erro
ensure:
    // Sempre executa (opcional)
    out "Finalizado"
```

### Trigger (Lançar Erro)

```
action dividir(a, b):
    given b is 0:
        trigger "Divisão por zero não permitida!"
    yield a / b

monitor:
    resultado := dividir(10, 0)
handle erro:
    out "Erro:", erro    // Erro: Divisão por zero não permitida!
```

### Assert

```
action processar(valor):
    assert valor bigger 0, "Valor deve ser positivo"
    yield valor * 2

// Funciona:
out processar(5)    // 10

// Falha:
monitor:
    processar(-1)
handle erro:
    out erro    // Valor deve ser positivo
```

### Padrões de Tratamento de Erro

```
// Tratamento com recuperação
action ler_numero(texto):
    monitor:
        yield cast texto as int
    handle erro:
        out "Valor inválido, usando 0"
        yield 0

out ler_numero("42")     // 42
out ler_numero("abc")    // Valor inválido, usando 0 → 0
```

---

## 12. Pipelines de Dados

O operador `>>` canaliza dados por operações de transformação.

### Sift (Filtrar)

```
numeros := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

pares := numeros >> sift n: n % 2 is 0
out pares    // [2, 4, 6, 8, 10]

grandes := numeros >> sift n: n bigger 5
out grandes  // [6, 7, 8, 9, 10]
```

### Morph (Transformar/Map)

```
numeros := [1, 2, 3, 4, 5]

dobrados := numeros >> morph n: n * 2
out dobrados    // [2, 4, 6, 8, 10]

quadrados := numeros >> morph n: n ** 2
out quadrados   // [1, 4, 9, 16, 25]
```

### Distill (Reduzir)

```
numeros := [1, 2, 3, 4, 5]

soma := numeros >> distill acc, n: acc + n
out soma    // 15

produto := numeros >> distill acc, n: acc * n
out produto  // 120
```

### Pipelines Encadeados

```
numeros := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Filtrar pares, dobrar, e somar
resultado := numeros >> sift n: n % 2 is 0 >> morph n: n * 2 >> distill acc, n: acc + n
out resultado    // 60

// Processamento de nomes
nomes := ["Ana", "Bruno", "Carlos", "Diana", "Eduardo"]
resultado := nomes >> sift n: len(n) bigger 4 >> morph n: upper(n)
out resultado    // [BRUNO, CARLOS, DIANA, EDUARDO]
```

---

## 13. Módulos e Imports

### Adopt (Import)

```
// Importar módulo da biblioteca padrão
adopt Arcane.Math as math

// Usar funções do módulo
out math["sqrt"](16)    // 4.0
```

### Relay (Export)

```
// Em um arquivo utils.df:
action dobro(x):
    yield x * 2

action triplo(x):
    yield x * 3

relay dobro, triplo
```

### Módulos da Biblioteca Padrão

| Módulo | Descrição |
|--------|-----------|
| `Arcane.IO` | Operações de arquivo e I/O |
| `Arcane.Math` | Funções matemáticas avançadas |
| `Arcane.Web` | HTTP e servidores web |
| `Arcane.Cortex` | IA e Machine Learning |
| `Arcane.Data` | DataFrames e análise de dados |

---

## 14. Concorrência

### Threads

```
thread:
    cycle i from 1 to 5:
        out "Thread:", i
        sleep(100)

out "Main continua executando"
sleep(600)
```

### Channels

```
channel mensagens

thread:
    mensagens.send("Olá do thread!")

sleep(100)
msg := mensagens.receive()
out msg    // Olá do thread!
```

---

## 15. Funções Embutidas

### Conversão de Tipos

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `str(x)` | Converte para String | `str(42)` → `"42"` |
| `int(x)` | Converte para Integer | `int("42")` → `42` |
| `float(x)` | Converte para Float | `float("3.14")` → `3.14` |
| `bool(x)` | Converte para Boolean | `bool(1)` → `yes` |
| `type(x)` | Retorna tipo | `type(42)` → `"Integer"` |
| `len(x)` | Retorna comprimento | `len([1,2,3])` → `3` |

### Matemáticas

| Função | Descrição | Exemplo |
|--------|-----------|---------|
| `abs(x)` | Valor absoluto | `abs(-5)` → `5` |
| `min(...)` | Mínimo | `min(3, 1, 2)` → `1` |
| `max(...)` | Máximo | `max(3, 1, 2)` → `3` |
| `sum(list)` | Soma | `sum([1,2,3])` → `6` |
| `round(x, d)` | Arredonda | `round(3.14159, 2)` → `3.14` |
| `floor(x)` | Arredonda para baixo | `floor(3.7)` → `3` |
| `ceil(x)` | Arredonda para cima | `ceil(3.2)` → `4` |
| `sqrt(x)` | Raiz quadrada | `sqrt(16)` → `4.0` |
| `pow(x, y)` | Potência | `pow(2, 10)` → `1024.0` |
| `log(x)` | Logaritmo natural | `log(E)` → `1.0` |
| `sin(x)` | Seno | `sin(0)` → `0.0` |
| `cos(x)` | Cosseno | `cos(0)` → `1.0` |
| `tan(x)` | Tangente | `tan(0)` → `0.0` |

### Constantes

| Constante | Valor |
|-----------|-------|
| `PI` | 3.141592653589793 |
| `E` | 2.718281828459045 |
| `TAU` | 6.283185307179586 |
| `INF` | Infinito |
| `NAN` | Not a Number |

### Aleatório

| Função | Descrição |
|--------|-----------|
| `random()` | Float aleatório 0-1 |
| `randint(a, b)` | Inteiro aleatório a-b |
| `choice(list)` | Elemento aleatório |
| `shuffle(list)` | Embaralha lista |

### Coleções

| Função | Descrição |
|--------|-----------|
| `sorted(list)` | Ordena lista |
| `reversed(list)` | Inverte lista |
| `enumerate(list)` | Lista de [índice, valor] |
| `zip(a, b)` | Combina listas |
| `append(list, item)` | Adiciona item |
| `pop(list)` | Remove e devolve o último |
| `pop(vault, chave)` | Remove e devolve o valor; levanta se a chave não existe |
| `insert(list, i, item)` | Insere na posição |
| `remove(list, item)` | Remove o item (silencioso se não estiver lá) |
| `remove(vault, chave)` | Apaga a chave **no lugar** (silencioso se não existe) |
| `contains(col, item)` | Verifica existência |
| `flatten(list)` | Achata listas aninhadas |
| `unique(list)` | Remove duplicatas |
| `count(list)` | Conta elementos |
| `index(list, item)` | Encontra posição |
| `slice(list, start, end)` | Fatia lista |
| `keys(dict)` | Chaves do dicionário |
| `values(dict)` | Valores do dicionário |
| `items(dict)` | Pares chave-valor |

### Strings

| Função | Descrição |
|--------|-----------|
| `join(sep, list)` | Junta com separador |
| `split(str, sep)` | Divide string |
| `strip(str)` | Remove espaços |
| `upper(str)` | Maiúsculas |
| `lower(str)` | Minúsculas |
| `replace(str, old, new)` | Substitui texto |
| `startswith(str, prefix)` | Começa com |
| `endswith(str, suffix)` | Termina com |
| `find(str, sub)` | Encontra posição |
| `format(template, ...)` | Formata string |

### Tempo

| Função | Descrição |
|--------|-----------|
| `time()` | Timestamp atual |
| `sleep(ms)` | Pausa em milissegundos |

### Utilitários

| Função | Descrição |
|--------|-----------|
| `exists(x)` | Verifica se não é void |
| `freeze(x)` | Torna imutável |
| `thaw(x)` | Torna mutável |
| `hash(x)` | Hash do objeto |
| `id(x)` | ID único do objeto |
| `range(...)` | Gera sequência |

---

## 16. Biblioteca Padrão

### Arcane.IO — Entrada/Saída de Arquivos

```
adopt Arcane.IO as io

// Ler arquivo
conteudo := io["read_file"]("dados.txt")

// Escrever arquivo
io["write_file"]("saida.txt", "Hello DataForge!")

// Ler JSON
dados := io["read_json"]("config.json")

// Escrever JSON
io["write_json"]("config.json", {"chave": "valor"})
```

### Arcane.Math — Matemática Avançada

```
adopt Arcane.Math as math

// Funções trigonométricas
out math["sin"](PI / 2)
out math["cos"](0)

// Estatísticas
dados := [10, 20, 30, 40, 50]
out math["mean"](dados)
out math["median"](dados)
out math["stdev"](dados)

// Operações matriciais
m := [[1, 2], [3, 4]]
out math["matrix_multiply"](m, m)
```

### Arcane.Web — HTTP e Web

```
adopt Arcane.Web as web

// Cliente HTTP
resposta := web["get"]("https://api.exemplo.com/dados")

// Parse JSON
dados := web["json_decode"]('{"nome": "teste"}')

// URL encoding
encoded := web["url_encode"]("olá mundo")
```

### Arcane.Cortex — IA e Machine Learning

```
adopt Arcane.Cortex as ai

// Criar rede neural
modelo := ai["Sequential"]([10, 64, 32, 1])

// NLP
tokens := ai["tokenize"]("DataForge é incrível")
sentimento := ai["sentiment"]("I love DataForge!")
```

### Arcane.Data — DataFrames

```
adopt Arcane.Data as data

// Criar DataFrame
df := data["DataFrame"]({"nome": ["Ana", "Bruno"], "idade": [25, 30]})

// Estatísticas
out data["statistics"](df)

// Normalização
norm := data["normalize"]([10, 20, 30, 40, 50])
```

---

## 17. REPL Interativo

### Iniciando

```bash
dataforge repl
```

### Comandos Especiais do REPL

| Comando | Descrição |
|---------|-----------|
| `help` | Mostra ajuda |
| `env` | Mostra variáveis do ambiente |
| `tokens <código>` | Mostra tokens |
| `ast <código>` | Mostra AST |
| `reset` | Limpa o ambiente |
| `exit` ou `quit` | Sair |

### Entrada Multilinha

```
DataForge> action somar(a, b):
...     yield a + b
...
DataForge> out somar(3, 4)
7
```

---

## 18. Referência de Palavras Reservadas

### Mapeamento Completo DataForge → Python/Tradicionais

| DataForge | Equivalente | Categoria |
|-----------|-------------|-----------|
| `steady` | `const` | Declaração |
| `shadow` | `let` (scoped) | Declaração |
| `void` | `None` | Literal |
| `yes` | `True` | Literal |
| `no` | `False` | Literal |
| `:=` | `=` | Atribuição |
| `out` | `print` | I/O |
| `in` | `input` | I/O |
| `given` | `if` | Condicional |
| `orif` | `elif` | Condicional |
| `otherwise` | `else` | Condicional |
| `match` | `match/switch` | Condicional |
| `point` | `case` | Condicional |
| `default` | `default` | Condicional |
| `cycle` | `for` | Loop |
| `persist` | `while` | Loop |
| `perform` | `do` | Loop |
| `halt` | `break` | Loop |
| `skip` | `continue` | Loop |
| `from` | `from/range start` | Loop |
| `to` | `to/range end` | Loop |
| `step` | `step` | Loop |
| `action` | `def/function` | Função |
| `yield` | `return` | Função |
| `blueprint` | `class` | OOP |
| `spawn` | `new` | OOP |
| `self` | `self/this` | OOP |
| `root` | `super` | OOP |
| `trait` | `interface` | OOP |
| `static` | `static` | OOP |
| `adopt` | `import` | Módulo |
| `relay` | `export` | Módulo |
| `monitor` | `try` | Erro |
| `handle` | `catch/except` | Erro |
| `ensure` | `finally` | Erro |
| `trigger` | `raise/throw` | Erro |
| `assert` | `assert` | Erro |
| `async` | `async` | Concorrência |
| `await` | `await` | Concorrência |
| `thread` | `Thread` | Concorrência |
| `channel` | `Channel` | Concorrência |
| `pulse` | `emit` | Evento |
| `sift` | `filter` | Pipeline |
| `morph` | `map` | Pipeline |
| `distill` | `reduce` | Pipeline |
| `typeof` | `typeof` | Tipo |
| `cast` | `cast/convert` | Tipo |
| `delete` | `del` | Memória |
| `inspect` | `debug print` | Debug |
| `wait` | `sleep` | Tempo |
| `freeze` | `freeze/lock` | Utilitário |
| `thaw` | `unfreeze` | Utilitário |
| `frame` | `DataFrame` | Data Science |
| `cluster` | `list/array` | Data Science |
| `vault` | `dict/map` | Data Science |

---

## 19. Guia de Estilo

### Indentação

- Use **4 espaços** para indentação
- **NÃO** use tabs (gera erro `SyncError`)
- Blocos são delimitados por `:` seguido de indentação

```
// ✅ Correto
given x bigger 0:
    out "positivo"

// ❌ Errado (tab)
given x bigger 0:
	out "positivo"    // SyncError!
```

### Nomeação

```
// Variáveis: snake_case
meu_nome := "DataForge"
numero_max := 100

// Ações: snake_case
action calcular_total(itens):
    yield sum(itens)

// Blueprints: PascalCase
blueprint ContaBancaria:
    action setup(titular):
        self.titular := titular

// Constantes: UPPER_CASE
steady MAX_TENTATIVAS := 3
steady TAXA_JUROS := 0.05
```

### Comentários

```
// Comentário de linha única

# Também é comentário de linha única

/* Comentário
   de múltiplas
   linhas */
```

### Convenções

1. Uma declaração por linha
2. Espaço ao redor de `:=` e operadores
3. Linhas em branco entre blocos lógicos
4. Nomes descritivos para variáveis e ações
5. Documentação em comentários para ações complexas

---

## 20. Solução de Problemas

### Erros Comuns

#### SyncError: Tab character detected

```
// Problema: uso de tab
given x bigger 0:
	out "teste"    // ❌

// Solução: use 4 espaços
given x bigger 0:
    out "teste"    // ✅
```

#### ParseError: Expected ':=' 

```
// Problema: usando = em vez de :=
x = 10    // ❌

// Solução: use :=
x := 10   // ✅
```

#### ParseError: Expected ':' after action signature

```
// Problema: esqueceu o : após ação
action somar(a, b)    // ❌ (a menos que seja abstract)
    yield a + b

// Solução: adicione :
action somar(a, b):   // ✅
    yield a + b
```

#### NameError: Variable not found

```
// Problema: variável não declarada
out nome    // ❌

// Solução: declare antes
nome := "DataForge"
out nome    // ✅
```

#### RuntimeError: Division by zero

```
// Problema: divisão por zero
x := 10 / 0    // ❌

// Solução: use monitor/handle
monitor:
    x := 10 / 0
handle erro:
    out "Erro:", erro
```

### Dicas de Debug

```
// Use inspect para ver detalhes de uma variável
inspect minha_variavel

// Use typeof para ver o tipo
out typeof minha_variavel

// Use --debug na CLI
dataforge run --debug meu_programa.df

// Use check para verificar sintaxe sem executar
dataforge check meu_programa.df
```

---

## Apêndice: Extensão de Arquivo

DataForge usa a extensão `.df` para seus arquivos fonte.

```
meu_programa.df
utils.df
main.df
```

## Apêndice: Estrutura de Projeto Recomendada

```
meu-projeto/
├── main.df              # Ponto de entrada
├── modules/
│   ├── utils.df         # Utilitários
│   ├── models.df        # Blueprints
│   └── services.df      # Lógica de negócio
├── tests/
│   └── test_main.df     # Testes
└── README.md            # Documentação
```

---

*DataForge v3.0 — Forged for the Future* 🔥

---

# 🚀 DataForge v3.0 — Novas Funcionalidades

> O DataForge v3.0 traz mais de 130 novas funções embutidas, 5 novos módulos de biblioteca padrão, 9 novas palavras-chave, e suporte expandido para strings, regex, programação funcional, reativa, tratamento de erros avançado, e muito mais.

---

## 21. Novidades v3.0 — Métodos de String Avançados

DataForge v3.0 oferece mais de **50 métodos de string** acessíveis via notação de ponto e funções globais.

### Métodos de Ponto (`.method()`)

```
texto := "Hello, DataForge v3!"

// Transformação
texto.upper()         // "HELLO, DATAFORGE V3!"
texto.lower()         // "hello, dataforge v3!"
texto.title()         // "Hello, Dataforge V3!"
texto.capitalize()    // "Hello, dataforge v3!"
texto.swapcase()      // "hELLO, dATAfORGE V3!"

// Busca
texto.find("Forge")         // 9
texto.rfind("o")            // 14
texto.contains("v3")        // yes
texto.startswith("Hello")   // yes
texto.endswith("!")          // yes
texto.index_of("Data")      // 7

// Extração
texto.substring(0, 5)   // "Hello"
texto.slice(0, 5)       // "Hello"
texto.char_at(0)         // "H"

// Limpeza
"  hi  ".strip()         // "hi"
"  hi  ".lstrip()        // "hi  "
"  hi  ".rstrip()        // "  hi"
"  hi  ".trim()          // "hi"

// Padding & Alinhamento
"42".pad_start(8, "0")  // "00000042"
"42".pad_end(8, ".")    // "42......"
"hi".center(10, "-")    // "----hi----"

// Verificações
"abc".isalpha()     // yes
"123".isdigit()     // yes
"abc123".isalnum()  // yes
"  ".isspace()      // yes
"ABC".isupper()     // yes
"abc".islower()     // yes

// Manipulação
texto.replace("v3", "v4")     // "Hello, DataForge v4!"
texto.split(", ")              // ["Hello", "DataForge v3!"]
texto.words()                  // ["Hello,", "DataForge", "v3!"]
texto.lines()                  // ["Hello, DataForge v3!"]
texto.reverse()                // "!3v egroFataD ,olleH"
"abc".repeat(3)                // "abcabcabc"
texto.count("o")               // 2
"hello world".removeprefix("hello ")  // "world"
"file.txt".removesuffix(".txt")       // "file"
```

### Funções Globais de String

```
join(", ", ["a", "b", "c"])      // "a, b, c"
split("a,b,c", ",")              // ["a", "b", "c"]
upper("hello")                   // "HELLO"
lower("WORLD")                   // "world"
title("hello world")             // "Hello World"
strip("  hi  ")                  // "hi"
replace("abc", "b", "x")        // "axc"
contains("hello", "ell")        // yes
startswith("hello", "hel")      // yes
endswith("hello", "llo")        // yes
center("hi", 10, "-")           // "----hi----"
pad_start("42", 8, "0")         // "00000042"
pad_end("42", 8, ".")           // "42......"
repeat("*", 5)                  // "*****"
char_at("hello", 1)             // "e"
substring("hello", 1, 3)        // "el"
index_of("hello", "lo")         // 3
includes("hello", "ell")        // yes
concat("a", "b", "c")           // "abc"
char(65)                         // "A"
ord("A")                         // 65
template("Olá {name}", {"name": "Mundo"})  // "Olá Mundo"
```

---

## 22. Novidades v3.0 — Regex & Padrões

DataForge v3.0 inclui suporte completo a expressões regulares.

### Funções de Regex

```
// Teste simples
regex_test("\\d+", "abc123")                    // yes
regex_test("^\\d+$", "abc")                      // no

// Buscar correspondências
regex_match("(\\d+)-(\\d+)", "Tel: 555-1234")   // {"matched": yes, ...}
regex_search("\\d+", "abc123")                   // {"value": "123", ...}

// Encontrar todas as ocorrências
regex_findall("\\d+", "a1 b2 c3")              // ["1", "2", "3"]

// Substituição
regex_sub("\\d+", "X", "a1 b2 c3")            // "aX bX cX"

// Dividir
regex_split("[,;]", "a,b;c,d")                 // ["a", "b", "c", "d"]

// Contar
regex_count("\\d", "a1b2c3")                   // 3

// Extrair grupos
regex_extract("(\\w+)@(\\w+)", "user@host")    // ["user", "host"]
```

### Módulo Arcane.Regex

```
adopt Arcane.Regex

// Compilar padrão para reutilização
pattern := Regex.compile("\\d+")

// Padrões pré-definidos
Regex.patterns["email"]     // Padrão para e-mail
Regex.patterns["url"]       // Padrão para URL
Regex.patterns["ipv4"]      // Padrão para IPv4

// Validação
Regex.is_valid_email("user@test.com")   // yes
Regex.is_valid_url("https://df.dev")    // yes
```

---

## 23. Novidades v3.0 — Tratamento de Erros Avançado

### Guard (Guarda)

Verifica uma condição no início de uma ação. Se falhar, executa o bloco `otherwise:` e **interrompe** a execução da ação.

```
action process_age(age):
    guard age bigger_eq 0 otherwise:
        emit("Idade inválida!")
    guard age smaller_eq 150 otherwise:
        emit("Idade muito alta!")
    emit("Idade válida: " + str(age))

process_age(25)    // "Idade válida: 25"
process_age(-5)    // "Idade inválida!"
```

### Validate (Validação)

Similar ao guard, valida uma condição e executa bloco alternativo se falhar.

```
action process_order(qty, price):
    validate qty bigger 0 otherwise:
        emit("Quantidade inválida!")
    validate price bigger_eq 0 otherwise:
        emit("Preço negativo!")
    emit("Total: $" + str(qty * price))
```

### Retry (Repetir com Recuperação)

Tenta executar um bloco até N vezes, com bloco de recuperação.

```
retry 3:
    emit("Tentativa...")
    trigger "Falha simulada"
recover err:
    emit("Todas as tentativas falharam: " + str(err))
```

### Defer (Adiar)

Agenda um bloco de código para executar quando a ação terminar (cleanup).

```
action file_operation():
    emit("Abrindo recurso...")
    defer:
        emit("Fechando recurso (cleanup)")
    emit("Trabalhando com recurso...")

file_operation()
// Saída:
//   Abrindo recurso...
//   Trabalhando com recurso...
//   Fechando recurso (cleanup)
```

### Propagate (Propagar)

Re-lança um erro capturado para um contexto superior.

```
action inner():
    monitor:
        trigger "Erro profundo"
    handle err:
        emit("Inner: " + str(err))
        propagate err

action outer():
    monitor:
        inner()
    handle err:
        emit("Outer: " + str(err))
```

### Palavras-chave de Erro v3.0

| Palavra | Descrição |
|---------|-----------|
| `guard` | Verifica condição, interrompe se falhar |
| `validate` | Valida condição com bloco alternativo |
| `retry` | Tenta bloco N vezes |
| `recover` | Bloco de recuperação após retry |
| `defer` | Agenda código para executar no fim da ação |
| `propagate` | Re-lança erro para contexto superior |
| `observe` | Itera reativamente sobre coleção |
| `stream` | Expressão de stream |
| `parallel` | Execução paralela (simulada) |

---

## 24. Novidades v3.0 — Programação Funcional

### Composição e Pipe

```
action double(x):
    yield x * 2

action add_one(x):
    yield x + 1

// Compose: direita para esquerda
f := compose(add_one, double)
emit(f(5))    // 11 (double(5)=10, add_one(10)=11)

// Pipe: esquerda para direita
g := pipe_fn(double, add_one)
emit(g(5))    // 11
```

### Funções de Alta Ordem

```
// Identity
identity(42)              // 42

// Complement (inverter predicado)
action is_even(x):
    yield x % 2 == 0

is_odd := complement(is_even)
is_odd(3)                 // yes

// Every & Some
every(is_even, [2, 4, 6])     // yes
some(is_even, [1, 3, 4])      // yes
none_of(is_even, [1, 3, 5])   // yes

// Find
find_first(is_even, [1, 3, 4, 6])  // 4
find_last(is_even, [1, 3, 4, 6])   // 6
```

### Flat Map e Scan

```
action expand(x):
    yield [x, x * 10]

flat_map(expand, [1, 2, 3])   // [1, 10, 2, 20, 3, 30]

action add(a, b):
    yield a + b

scan(add, [1, 2, 3, 4], 0)    // [0, 1, 3, 6, 10]
```

### Memoização

```
action expensive(n):
    yield n * n * n

cached := memoize(expensive)
cached(5)   // Calcula
cached(5)   // Retorna do cache
```

### Once (Executar Uma Vez)

```
action init():
    yield "Initialized"

init_once := once(init)
init_once()  // "Initialized"
init_once()  // "Initialized" (retorna resultado anterior, não executa novamente)
```

---

## 25. Novidades v3.0 — Matemática e Estatística Avançada

### Funções Matemáticas Estendidas

```
// Raízes e Logaritmos
cbrt(27)           // 3.0
log2(1024)         // 10.0
log10(10000)       // 4.0
exp(1)             // 2.71828...

// Trigonometria
sin(PI / 2)        // 1.0
cos(0)             // 1.0
tan(PI / 4)        // ~1.0
asin(1)            // PI/2
acos(0)            // PI/2
atan(1)            // PI/4
atan2(1, 1)        // PI/4
degrees(PI)        // 180.0
radians(180)       // PI
hypot(3, 4)        // 5.0

// Combinatória
factorial(10)      // 3628800
gcd(48, 18)        // 6
lcm(12, 8)         // 24
comb(10, 3)        // 120
perm(5, 3)         // 60

// Utilitários
clamp(15, 0, 10)   // 10
lerp(0, 100, 0.5)  // 50.0
sign(-42)          // -1
is_finite(42)      // yes
is_nan(NAN)        // yes
is_inf(INF)        // yes
```

### Estatística

```
data := [23, 45, 12, 67, 34, 89]

mean(data)          // Média
median(data)        // Mediana
mode(data)          // Moda
stdev(data)         // Desvio padrão
variance(data)      // Variância
```

### Constantes

```
PI          // 3.141592653589793
E           // 2.718281828459045
INF         // Infinito
NAN         // Not a Number
MAX_INT     // 9223372036854775807
MIN_INT     // -9223372036854775808
NEWLINE     // "\n"
TAB         // "\t"
EMPTY       // ""
```

---

## 26. Novidades v3.0 — Coleções Avançadas & Tipagem

### Métodos de Lista (Ponto)

```
lista := [1, 2, 3, 4, 5]

lista.first()          // 1
lista.last()           // 5
lista.take(3)          // [1, 2, 3]
lista.drop(3)          // [4, 5]
lista.slice(1, 3)      // [2, 3]
lista.contains(3)      // yes
lista.index_of(3)      // 2
lista.reversed()       // [5, 4, 3, 2, 1]
lista.join(", ")       // "1, 2, 3, 4, 5"
lista.chunk(2)         // [[1, 2], [3, 4], [5]]
lista.unique()         // [1, 2, 3, 4, 5]
lista.flatten()        // (para listas aninhadas)
lista.rotate(2)        // [3, 4, 5, 1, 2]
lista.frequencies()    // {1: 1, 2: 1, ...}
lista.sum()            // 15
lista.min()            // 1
lista.max()            // 5
lista.mean()           // 3.0

// Funcionais no ponto
lista.map(double)       // [2, 4, 6, 8, 10]
lista.filter(is_even)   // [2, 4]
lista.every(is_even)    // no
lista.some(is_even)     // yes
lista.find(is_even)     // 2
```

### Funções de Coleção Globais

```
first([1, 2, 3])          // 1
last([1, 2, 3])           // 3
take([1, 2, 3, 4], 2)     // [1, 2]
drop([1, 2, 3, 4], 2)     // [3, 4]
chunk([1, 2, 3, 4, 5], 2) // [[1, 2], [3, 4], [5]]
rotate([1, 2, 3], 1)      // [2, 3, 1]
interleave([1, 2], [3, 4]) // [1, 3, 2, 4]
flatten([[1, 2], [3, 4]])  // [1, 2, 3, 4]
unique([1, 2, 2, 3])      // [1, 2, 3]
frequencies(["a", "b", "a"]) // {"a": 2, "b": 1}
```

### Métodos de Dicionário (Ponto)

```
d := {"name": "Alice", "age": 30}

d.keys()           // ["name", "age"]
d.values()         // ["Alice", 30]
d.items()          // [["name", "Alice"], ["age", 30]]
d.has("name")      // yes
d.get("name")      // "Alice"
d.get("email", "N/A") // "N/A"
d.length()         // 2
d.merge({"city": "SP"})  // {"name": "Alice", "age": 30, "city": "SP"}
d.pick("name")     // {"name": "Alice"}
d.omit("age")      // {"name": "Alice"}
d.invert()         // {"Alice": "name", 30: "age"}
```

### Funções de Dicionário Globais

```
keys(d)                         // ["name", "age"]
values(d)                       // ["Alice", 30]
pick(d, ["name"])               // {"name": "Alice"}
omit(d, ["age"])                // {"name": "Alice"}
merge_dicts(d1, d2)             // Combina dois dicts
invert_dict(d)                  // Inverte chave/valor
deep_copy(d)                    // Cópia profunda
```

### Sistema de Tipagem

```
is_string("hello")     // yes
is_number(42)          // yes
is_integer(42)         // yes
is_float(3.14)         // yes
is_boolean(yes)        // yes
is_list([1, 2])        // yes
is_dict({"a": 1})      // yes
is_void(void)          // yes
is_callable(print)     // yes
is_empty("")           // yes
is_empty([])           // yes
type_of("hello")       // "string"
type_of(42)            // "integer"
type_of([1, 2])        // "list"
coalesce(void, void, 42)   // 42
default_val(void, "fallback")  // "fallback"
```

---

## 27. Novidades v3.0 — Programação Reativa & Streams

### Observe (Observar)

Itera reativamente sobre uma coleção:

```
items := [10, 20, 30, 40, 50]
observe item in items:
    emit("Observado: " + str(item))
```

### Pipelines como Streams

```
numbers := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Filter → Map
result := numbers >> sift x: x % 2 == 0 >> morph x: x * x
emit(result)   // [4, 16, 36, 64, 100]
```

### Padrão Event-Driven

```
blueprint EventBus:
    action setup():
        self.handlers := {}
        self.log := []

    action on(event, handler):
        self.handlers[event] := handler

    action emit_event(event, data):
        given contains(self.handlers, event):
            handler := self.handlers[event]
            handler(data)

bus := spawn EventBus()

action on_login(data):
    emit("Login: " + str(data))

bus.on("login", on_login)
bus.emit_event("login", "Alice")
```

### State Machine (Máquina de Estados)

```
blueprint StateMachine:
    action setup(initial):
        self.state := initial
        self.transitions := {}
        self.history := [initial]

    action add_transition(from_st, event, to_st):
        key := from_st + ":" + event
        self.transitions[key] := to_st

    action send(event):
        key := self.state + ":" + event
        given contains(self.transitions, key):
            self.state := self.transitions[key]
            self.history := self.history + [self.state]

    action current():
        yield self.state

light := spawn StateMachine("red")
light.add_transition("red", "next", "green")
light.add_transition("green", "next", "yellow")
light.add_transition("yellow", "next", "red")
light.send("next")   // → green
```

---

## 28. Novidades v3.0 — Framework de Testes

### Padrão de Test Suite

```
blueprint TestRunner:
    action setup(name):
        self.name := name
        self.passed := 0
        self.failed := 0
        self.total := 0

    action assert_equal(actual, expected, msg):
        self.total := self.total + 1
        given actual == expected:
            self.passed := self.passed + 1
            emit("  ✓ " + msg)
        otherwise:
            self.failed := self.failed + 1
            emit("  ✗ " + msg)

    action summary():
        emit(self.name + ": " + str(self.passed) + "/" + str(self.total))

t := spawn TestRunner("Math Tests")
t.assert_equal(2 + 2, 4, "2+2=4")
t.assert_equal(abs(-5), 5, "abs(-5)=5")
t.summary()
```

### Módulo Arcane.Test

```
adopt Arcane.Test

// Criar suite de teste
suite := Test.create_suite("Minha Suite")

// Adicionar asserções
Test.assert_equal(suite, 1 + 1, 2, "soma básica")
Test.assert_true(suite, is_string("hi"), "tipo string")
Test.assert_contains(suite, [1, 2, 3], 2, "contém 2")
Test.assert_greater(suite, 10, 5, "10 > 5")

// Executar e mostrar resultados
Test.run_suite(suite)
```

---

## 29. Novidades v3.0 — Programação Modular

### Imports com `adopt`

```
adopt Arcane.Math       // Importa módulo de matemática
adopt Arcane.Regex      // Importa módulo de regex
adopt Arcane.Test       // Importa módulo de testes
adopt Arcane.Functional // Importa módulo funcional
adopt Arcane.Async      // Importa módulo assíncrono
adopt Arcane.Text       // Importa módulo de texto
```

### Módulos Disponíveis

| Módulo | Atalho | Descrição |
|--------|--------|-----------|
| `Arcane.Math` | `Math` | Funções matemáticas avançadas |
| `Arcane.Strings` | `Strings` | Utilitários de string |
| `Arcane.Collections` | `Collections` | Estruturas de dados |
| `Arcane.IO` | `IO` | Operações de arquivo |
| `Arcane.Stats` | `Stats` | Estatísticas |
| `Arcane.Regex` | `Regex` | Expressões regulares |
| `Arcane.Test` | `Test` | Framework de testes |
| `Arcane.Functional` | `Functional` | Programação funcional |
| `Arcane.Async` | `Async` | Programação assíncrona |
| `Arcane.Text` | `Text` | Processamento de texto |

### Padrão de Namespace com Blueprints

```
blueprint Config:
    static app_name := "MeuApp"
    static version := "1.0"

emit(Config.app_name)   // "MeuApp"
```

### Composição de Módulos

```
blueprint Logger:
    action setup(prefix):
        self.prefix := prefix
        self.entries := []

    action log(msg):
        entry := "[" + self.prefix + "] " + msg
        self.entries := self.entries + [entry]
        emit("  " + entry)

blueprint Database:
    action setup(name, logger):
        self.name := name
        self.data := {}
        self.logger := logger

    action put(key, val):
        self.data[key] := val
        self.logger.log("SET " + key)

logger := spawn Logger("DB")
db := spawn Database("main", logger)
db.put("user:1", {"name": "Alice"})
```

---

## 30. Novidades v3.0 — Novos Módulos da Biblioteca Padrão

### Arcane.Regex (~260 linhas)

- `Regex.compile(pattern)` — Compila padrão
- `Regex.match(pattern, text)` — Match completo
- `Regex.search(pattern, text)` — Primeira correspondência
- `Regex.findall(pattern, text)` — Todas as correspondências
- `Regex.sub(pattern, repl, text)` — Substituição
- `Regex.split(pattern, text)` — Dividir por padrão
- `Regex.patterns` — Dicionário com padrões comuns (email, url, ipv4, phone, date)
- Funções de validação: `is_valid_email`, `is_valid_url`, `is_valid_ipv4`

### Arcane.Test (~270 linhas)

- `Test.create_suite(name)` — Cria suite de testes
- `Test.assert_equal(suite, actual, expected, msg)` — Asserção de igualdade
- `Test.assert_true/false/not_equal` — Asserções básicas
- `Test.assert_greater/less/contains/type` — Asserções avançadas
- `Test.assert_throws(suite, func, msg)` — Testa exceções
- `Test.benchmark(func, iterations)` — Mede performance
- `Test.mock(return_value)` / `Test.spy()` — Mock e Spy
- `Test.describe(name)` / `Test.it(desc, suite, func)` — BDD

### Arcane.Functional (~400 linhas)

- `Functional.compose/pipe/curry/memoize` — Composição
- `Functional.map/filter/reduce/flat_map/zip_with` — Coleções
- `Functional.Maybe/Either` — Monads (Maybe.of, Maybe.nothing, Either.right, Either.left)
- `Functional.lens(getter, setter)` — Lenses
- `Functional.match_pattern(value, patterns)` — Pattern matching
- `Functional.transduce(xf, rf, init, coll)` — Transducers

### Arcane.Async (~400 linhas)

- `Async.promise(executor)` — Criar Promise
- `Async.resolve/reject(value)` — Resolver/Rejeitar
- `Async.all/race(promises)` — Combinar Promises
- `Async.observable(producer)` — Criar Observable
- `Async.from_list(items)` — Observable de lista
- `Async.map/filter/take/merge` — Operadores de stream
- `Async.event_emitter()` — Emissor de eventos
- `Async.scheduler()` — Agendador de tarefas
- `Async.signal(initial)` — Sinais reativos

### Arcane.Text (~420 linhas)

- `Text.template(tmpl, vars)` — Motor de templates
- Conversão de caso: `snake_case`, `camelCase`, `PascalCase`, `kebab-case`, `SCREAMING_SNAKE`, `Title Case`, `dot.case`, `path/case`, `sentence case`, `Header-Case`
- `Text.analyze(text)` — Análise (chars, words, sentences, avg_word_length)
- `Text.diff(a, b)` — Diferenças entre textos
- `Text.similarity(a, b)` — Similaridade (0.0 a 1.0)
- `Text.table(headers, rows)` — Formatação de tabela
- `Text.wrap(text, width)` — Quebra de linha
- `Text.csv_parse/csv_format` — CSV
- `Text.ini_parse/ini_format` — INI
- `Text.query_parse/query_format` — Query strings
- `Text.html_escape/html_unescape` — HTML
- `Text.lorem_ipsum(sentences)` — Gerador de texto

---

## 31. Referência Completa de Funções Embutidas v3.0

### Conversão de Tipos (10)
`str`, `int`, `float`, `bool`, `list`, `type_of`, `to_number`, `to_string`, `to_list`, `to_dict`

### Strings (50+)
`upper`, `lower`, `title`, `capitalize`, `strip`, `lstrip`, `rstrip`, `split`, `join`, `replace`, `find`, `rfind`, `startswith`, `endswith`, `contains`, `index_of`, `last_index_of`, `char_at`, `substring`, `center`, `ljust`, `rjust`, `zfill`, `pad_start`, `pad_end`, `repeat`, `reverse_str`, `trim`, `includes`, `concat`, `char`, `ord`, `encode`, `decode`, `format`, `count_str`, `expandtabs`, `partition`, `rpartition`, `splitlines`, `removeprefix`, `removesuffix`, `words`, `lines`, `template`, `swapcase`, `isalpha`, `isdigit`, `isalnum`, `isspace`, `isupper`, `islower`, `istitle`, `isnumeric`, `isascii`

### Regex (8)
`regex_match`, `regex_search`, `regex_findall`, `regex_sub`, `regex_split`, `regex_test`, `regex_count`, `regex_extract`

### Matemática (40+)
`abs`, `round`, `floor`, `ceil`, `sqrt`, `cbrt`, `pow`, `log`, `log2`, `log10`, `exp`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `degrees`, `radians`, `hypot`, `factorial`, `gcd`, `lcm`, `comb`, `perm`, `sum`, `min`, `max`, `mean`, `median`, `mode`, `stdev`, `variance`, `clamp`, `lerp`, `sign`, `is_finite`, `is_nan`, `is_inf`

### Aleatório (5)
`random`, `randint`, `choice`, `shuffle`, `sample`

### Coleções (25+)
`len`, `range`, `sorted`, `reversed`, `contains`, `enumerate`, `zip`, `unzip`, `first`, `last`, `take`, `drop`, `chunk`, `interleave`, `rotate`, `flatten`, `unique`, `merge_dicts`, `invert_dict`, `pick`, `omit`, `deep_copy`, `frequencies`, `keys`, `values`, `items`

### Funcional (20+)
`compose`, `pipe_fn`, `partial`, `curry`, `memoize`, `once`, `tap`, `identity`, `constantly`, `complement`, `every`, `some`, `none_of`, `find_first`, `find_last`, `flat_map`, `scan`, `zip_with`, `reduce`

### Itertools (6)
`count_from`, `cycle_iter`, `repeat_iter`, `accumulate`, `chain`, `product`

### Utilitários (10+)
`uuid`, `to_json`, `from_json`, `hash_value`, `base64_encode`, `base64_decode`, `env_var`, `timestamp`, `sleep`, `forge_error`

### Verificação de Tipo (14)
`is_string`, `is_number`, `is_integer`, `is_float`, `is_boolean`, `is_list`, `is_dict`, `is_void`, `is_callable`, `is_empty`, `is_even`, `is_odd`, `coalesce`, `default_val`, `assert_type`

### Constantes (9)
`PI`, `E`, `INF`, `NAN`, `NEWLINE`, `TAB`, `EMPTY`, `MAX_INT`, `MIN_INT`

---

## Resumo de Exemplos v3.0

| # | Exemplo | Recurso Principal |
|---|---------|-------------------|
| 31 | `31_string_methods.df` | 50+ métodos de string |
| 32 | `32_regex_patterns.df` | Regex e pattern matching |
| 33 | `33_error_handling_v3.df` | guard, retry, validate, defer, propagate |
| 34 | `34_functional_advanced.df` | compose, pipe, curry, memoize |
| 35 | `35_advanced_math.df` | Matemática e estatística avançada |
| 36 | `36_collections_types.df` | Coleções avançadas e tipagem |
| 37 | `37_reactive_streams.df` | Observe, eventos, state machine |
| 38 | `38_testing_framework.df` | Framework de testes |
| 39 | `39_modular_programming.df` | Módulos e composição |
| 40 | `40_v3_showcase.df` | Showcase completo v3.0 |

---

*DataForge v3.0 — Forged for the Future* 🔥
