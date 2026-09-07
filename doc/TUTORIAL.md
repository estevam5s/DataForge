# Tutorial DataForge — do zero ao primeiro sistema

Este tutorial ensina a linguagem inteira, na ordem em que ela é usada na prática.
Cada trecho de código roda como está — copie, cole em um `.df` e execute com
`dataforge run arquivo.df`.

Se ainda não instalou, veja [`INSTALACAO.md`](INSTALACAO.md).

**Índice**

1. [O que é DataForge](#1-o-que-é-dataforge)
2. [Anatomia de um programa](#2-anatomia-de-um-programa)
3. [Variáveis e tipos](#3-variáveis-e-tipos)
4. [Operadores](#4-operadores)
5. [Condicionais](#5-condicionais)
6. [Laços](#6-laços)
7. [Coleções](#7-coleções)
8. [Textos](#8-textos)
9. [Ações (funções)](#9-ações-funções)
10. [Blueprints (classes)](#10-blueprints-classes)
11. [Tratamento de erros](#11-tratamento-de-erros)
12. [Pipelines](#12-pipelines)
13. [Módulos](#13-módulos)
14. [Concorrência](#14-concorrência)
15. [Projeto final](#15-projeto-final)

---

## 1. O que é DataForge

DataForge é uma linguagem interpretada, de tipagem dinâmica com anotações
opcionais, escrita em Python. O que a distingue:

- **Vocabulário próprio**: em vez de `if/for/class/try`, usa
  `given/cycle/blueprint/monitor`. As palavras foram escolhidas para descrever a
  *intenção*, não a mecânica.
- **Pipelines nativos**: `>> sift`, `>> morph` e `>> distill` são sintaxe, não
  chamadas de biblioteca.
- **Blocos por indentação**: como Python, sem chaves e sem `end`.
- **Biblioteca padrão embutida**: 13 módulos `Arcane.*` com 454 símbolos, mais
  225 funções globais disponíveis sem import — de estatística a servidor HTTP.

### Tabela de tradução mental

Se você já programa, esta é a ponte:

| Conceito | Outras linguagens | DataForge |
|----------|-------------------|-----------|
| atribuição | `x = 1` | `x := 1` |
| constante | `const` / `final` | `steady` |
| imprimir | `print` / `console.log` | `out` |
| se / senão se / senão | `if` / `else if` / `else` | `given` / `orif` / `otherwise` |
| switch | `switch` / `case` | `match` / `point` / `default` |
| for | `for` | `cycle` |
| while | `while` | `persist` |
| do-while | `do ... while` | `perform ... persist` |
| break / continue | `break` / `continue` | `halt` / `skip` |
| função | `def` / `function` | `action` |
| return | `return` | `yield` |
| classe | `class` | `blueprint` |
| new | `new` | `spawn` |
| this / self | `this` / `self` | `self` (ou `this`) |
| super | `super` | `root` |
| interface | `interface` | `trait` |
| import | `import` | `adopt` |
| export | `export` | `relay` |
| try / catch / finally | `try` / `catch` / `finally` | `monitor` / `handle` / `ensure` |
| throw | `throw` / `raise` | `trigger` |
| true / false / null | `true` / `false` / `null` | `yes` / `no` / `void` |
| filter / map / reduce | `.filter` / `.map` / `.reduce` | `>> sift` / `>> morph` / `>> distill` |

---

## 2. Anatomia de um programa

```dataforge
// Comentário de uma linha
# Também funciona

/* Comentário
   de bloco */

// Não existe função main: o arquivo executa de cima para baixo.
out "primeira linha executada"

action cumprimentar(nome):
    yield "Ola, " + nome

out cumprimentar("mundo")
```

**Regras de formatação, todas obrigatórias:**

- Blocos abrem com `:` e são delimitados por **indentação**.
- Use **4 espaços** por nível. **Tabs são erro de sintaxe.**
- Uma instrução por linha; não existe `;`.

---

## 3. Variáveis e tipos

### Declaração

```dataforge
nome := "DataForge"        // cria ou atualiza
idade := 30
altura := 1.75
ativo := yes
vazio := void
```

O `:=` cria a variável se ela não existir e atualiza se existir.

### Constantes

```dataforge
steady PI := 3.14159
steady LIMITE := 100

// PI := 0   →  erro: Cannot reassign steady (constant) 'PI'
```

### Tipos primitivos

| Tipo | Exemplo | `typeof` devolve |
|------|---------|------------------|
| Inteiro | `42`, `0xFF`, `0b1010`, `1_000_000` | `"Integer"` |
| Decimal | `3.14`, `1.5e3` | `"Float"` |
| Texto | `"a"`, `'b'`, `"""várias linhas"""` | `"String"` |
| Booleano | `yes`, `no` | `"Boolean"` |
| Nulo | `void` | `"Void"` |
| Lista | `[1, 2, 3]` | `"Cluster"` |
| Dicionário | `{"k": 1}` | `"Vault"` |

```dataforge
out typeof(42)          // Integer
out typeof([1, 2])      // Cluster
out typeof({"a": 1})    // Vault
```

### Anotações de tipo

Opcionais, mas **verificadas em tempo de execução**:

```dataforge
idade: Integer := 30
nome: String := "Ana"
notas: Cluster := [8, 9, 10]

// idade: Integer := "trinta"
// → TypeError_: variable 'idade' declared as Integer but got String
```

Tipos aceitos: `Integer`, `Float`, `Number`, `String`, `Boolean`, `Cluster`,
`Vault`, `Void`, `Action`, `Any` e o nome de qualquer blueprint. Um `Integer` é
aceito onde se espera `Float`.

### Conversão

```dataforge
out cast "42" as Integer      // 42
out cast 3.9 as Integer       // 3   (trunca)
out cast 42 as String         // "42"
out str(42), int("7"), float("2.5"), bool(1)
```

### Escopo

```dataforge
x := 10

action le():
    yield x            // enxerga o escopo externo: 10

action sombreia():
    shadow x := 99     // cria uma cópia local
    yield x            // 99

out le(), sombreia(), x    // 10 99 10
```

`shadow` cria uma variável local que **não** afeta a externa.

---

## 4. Operadores

### Aritméticos

```dataforge
out 7 + 2      // 9
out 7 - 2      // 5
out 7 * 2      // 14
out 7 / 2      // 3.5    (sempre Float)
out 7 % 2      // 1
out 7 ** 2     // 49
out 7 ~/ 2     // 3      (divisão inteira)
```

> **Divisão inteira:** prefira **`~/`**. O `//` também funciona, mas é ambíguo —
> ele abre comentários. O lexer resolve pelo contexto, e a regra é: `7 // 2` é
> divisão; `x := 3  // marcar item` (dois ou mais espaços antes, seguido de
> prosa) é comentário. Use `~/` e nunca pense nisso.

### Precedência

Da mais alta para a mais baixa:

```
()  →  chamada / índice / .membro  →  **  →  - + (unários)
    →  * / % ~/  →  + -  →  comparações  →  not  →  and  →  or  →  >>
```

```dataforge
out 2 + 3 * 4        // 14
out 2 ** 3 ** 2      // 512    (associa à direita)
out -2 ** 2          // -4     (o sinal aplica depois)
```

### Comparação

Cada operador tem duas grafias, equivalentes:

| Palavra | Símbolo | Significado |
|---------|---------|-------------|
| `is` | `==` | igual |
| `isnt` | `!=` | diferente |
| `bigger` | `>` | maior |
| `smaller` | `<` | menor |
| `bigger_eq` | `>=` | maior ou igual |
| `smaller_eq` | `<=` | menor ou igual |

**Comparações encadeadas** funcionam:

```dataforge
nota := 7.5
out 0 <= nota <= 10           // yes
out 1 smaller 5 smaller 10    // yes
```

### Lógicos

```dataforge
out yes and no      // no
out yes or no       // yes
out not yes         // no
```

`and` e `or` têm avaliação curta-circuito.

### Atribuição composta

```dataforge
x := 10
x += 5      // 15
x -= 3      // 12
x *= 2      // 24
x /= 4      // 6.0
x %= 4      // 2.0
```

---

## 5. Condicionais

### given / orif / otherwise

```dataforge
action classificar(n):
    given n bigger 0:
        yield "positivo"
    orif n smaller 0:
        yield "negativo"
    otherwise:
        yield "zero"

out classificar(5)     // positivo
out classificar(-1)    // negativo
out classificar(0)     // zero
```

### match / point / default

```dataforge
action dia(n):
    match n:
        point 1:
            yield "segunda"
        point 2:
            yield "terca"
        default:
            yield "outro"

out dia(1)     // segunda
out dia(9)     // outro
```

`match` compara por igualdade e **não** cai de um `point` para o outro.

---

## 6. Laços

### Intervalo numérico

```dataforge
cycle i from 1 to 5:
    out i                 // 1 2 3 4 5   (o limite é inclusivo)

cycle i from 0 to 10 step 2:
    out i                 // 0 2 4 6 8 10

cycle i from 5 to 1 step -1:
    out i                 // 5 4 3 2 1
```

### Sobre uma coleção

```dataforge
cycle fruta in ["maca", "uva"]:
    out fruta

cycle letra in "abc":
    out letra

precos := {"maca": 3.5, "uva": 8.0}
cycle chave in precos.keys():
    out chave, precos[chave]
```

### Enquanto (while)

```dataforge
n := 1024
divisoes := 0
persist n bigger 1:
    n := n ~/ 2
    divisoes += 1
out divisoes      // 10
```

### Faça-enquanto (do-while)

```dataforge
i := 0
perform:
    out "roda ao menos uma vez"
    i += 1
persist i smaller 3
```

### halt e skip

```dataforge
cycle i from 1 to 100:
    given i % 3 is 0:
        skip              // pula para a próxima iteração
    given i bigger 10:
        halt              // sai do laço
    out i
```

---

## 7. Coleções

### Clusters (listas)

```dataforge
nums := [10, 20, 30, 40, 50]

out nums[0]        // 10
out nums[-1]       // 50    (índice negativo conta do fim)
out len(nums)      // 5

nums[1] := 99      // atribuição por índice
```

**Fatiamento** `[inicio:fim:passo]`:

```dataforge
l := [1, 2, 3, 4, 5]
out l[1:3]      // [2, 3]
out l[:2]       // [1, 2]
out l[3:]       // [4, 5]
out l[::2]      // [1, 3, 5]
out l[::-1]     // [5, 4, 3, 2, 1]
```

**Métodos** (assinaturas — `f` representa uma ação ou lambda):

```dataforge
l := [3, 1, 2]
l.append(4)              // adiciona no fim
l.insert(0, 0)           // insere na posição
l.remove(3)              // remove pelo valor
l.pop()                  // remove e devolve o último
l.pop(0)                 // remove e devolve o primeiro
l.sort()                 // ordena no lugar
l.reverse()              // inverte no lugar
l.contains(2)            // yes/no
l.index(2)               // posição
l.first()  l.last()
l.take(2)  l.drop(2)
l.unique()  l.flatten()  l.chunk(2)
l.join(", ")
l.map(f)  l.filter(f)  l.reduce(f, inicial)
l.every(f)  l.some(f)  l.find(f)
l.sum()  l.min()  l.max()  l.mean()
l.frequencies()
```

**Agregações globais:**

```dataforge
v := [120, 340, 90, 500]
out sum(v), min(v), max(v), mean(v), median(v), stdev(v)
out sorted(v), reversed(v), unique(v), flatten([[1],[2]])
```

### Vaults (dicionários)

```dataforge
pessoa := {"nome": "Ana", "idade": 30}

out pessoa["nome"]     // acesso por chave
out pessoa.nome        // acesso por ponto (equivalente)

pessoa["cidade"] := "Floripa"      // adiciona
pessoa["idade"] := 31              // atualiza
```

**Métodos:**

```dataforge
v := {"a": 1, "b": 2}
v.keys()  v.values()  v.items()
v.has("a")                 // yes
v.get("z", "padrao")       // valor com fallback
v.set("c", 3)  v.delete("a")
v.merge({"d": 4})
v.pick("a", "b")  v.omit("b")
v.invert()
v.map_values(lambda x: x * 10)
v.length()
```

**Percorrendo:**

```dataforge
estoque := {"parafuso": 120, "porca": 80}
cycle par in estoque.items():
    out par[0], "->", par[1]
```

---

## 8. Textos

```dataforge
s := "DataForge"

out s.length()          // 9
out s[0]                // D
out s[0:4]              // Data
out s.upper()           // DATAFORGE
out s.lower()  s.title()  s.capitalize()
out s.trim()  s.strip()
out s.contains("Forge")  s.startswith("Data")  s.endswith("ge")
out s.find("Forge")     // 4   (-1 se não achar)
out s.replace("Data", "Info")
out s.split("a")        // divide
out s.reverse()  s.repeat(2)
out s.pad_start(12, ".")  s.pad_end(12, ".")
out s.words()  s.lines()
out s.count("a")
```

Concatenação com `+`. Números viram texto automaticamente quando um dos lados é
texto:

```dataforge
out "total: " + str(42)
out "x" + 1              // "x1"
```

Juntar e separar:

```dataforge
campos := "a,b,c".split(",")     // ["a", "b", "c"]
out ";".join(campos)             // "a;b;c"
```

---

## 9. Ações (funções)

### Básico

```dataforge
action somar(a, b):
    yield a + b

out somar(2, 3)      // 5
```

`yield` devolve o valor **e encerra a ação**. Sem `yield`, a ação devolve `void`.

### Parâmetros com padrão

```dataforge
action criar(nome, papel := "leitor", ativo := yes):
    yield {"nome": nome, "papel": papel, "ativo": ativo}

out criar("Ana")                    // papel = "leitor"
out criar("Bruno", "admin")
```

### Argumentos nomeados

```dataforge
action retangulo(largura := 1, altura := 1):
    yield largura * altura

out retangulo(altura := 5, largura := 3)      // 15
```

### Parâmetros e retorno tipados

```dataforge
action media(nums: Cluster) -> Float:
    yield sum(nums) / len(nums)

out media([1, 2, 3])      // 2.0
// media("texto")  →  TypeError_
```

### Aridade verificada

Chamar com argumentos a mais ou a menos dispara erro:

```dataforge
action f(a, b):
    yield a + b

// f(1)          →  action 'f' is missing argument(s): b
// f(1, 2, 3)    →  action 'f' takes 2 argument(s) but 3 were given
```

### Recursão

```dataforge
action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)

out fatorial(6)      // 720
```

Recursão infinita vira `StackOverflowError_` depois de 1000 quadros, com o nome
da ação culpada na mensagem.

### Ações de alta ordem e closures

```dataforge
action fabrica_somador(n):
    action somador(x):
        yield x + n
    yield somador

soma10 := fabrica_somador(10)
out soma10(5)                  // 15
out fabrica_somador(3)(4)      // 7   (chamada encadeada)
```

### Lambdas

Três grafias, todas equivalentes:

```dataforge
dobro := lambda x: x * 2
soma := lambda a, b => a + b
fixo := lambda: 42

out [1, 2, 3].map(lambda n: n * n)          // [1, 4, 9]
out [1, 2, 3, 4].filter(lambda n: n % 2 is 0)
```

### Decoradores

```dataforge
action com_log(fn):
    action envolvida(x):
        out "  [log] chamada com", x
        yield fn(x)
    yield envolvida

mark @com_log
action triplo(x):
    yield x * 3

out triplo(5)
//   [log] chamada com 5
// 15
```

### defer

Agenda um bloco para rodar quando a ação terminar — mesmo se ela sair por erro.

```dataforge
action com_recurso():
    defer:
        out "fechou"
    out "abriu"
    yield "pronto"

out com_recurso()
// abriu
// fechou
// pronto
```

---

## 10. Blueprints (classes)

### Construtor por parâmetros

```dataforge
blueprint Ponto(x, y):
    action distancia():
        yield sqrt(self.x ** 2 + self.y ** 2)

    action toString():
        yield "(" + str(self.x) + ", " + str(self.y) + ")"

p := spawn Ponto(3, 4)
out p.x, p.distancia()      // 3 5.0
out str(p)                  // (3, 4)
```

Os parâmetros do cabeçalho viram campos automaticamente. `toString` é usado por
`out` e por `str()`.

### Construtor por setup

Para inicializar campos derivados:

```dataforge
blueprint Pedido:
    action setup(cliente):
        self.cliente := cliente
        self.itens := []

    action adicionar(item):
        self.itens.append(item)
        yield len(self.itens)

p := spawn Pedido("Ana")
p.adicionar("mouse")
```

As duas formas convivem: se um blueprint tem parâmetros **e** um `setup`, os dois
rodam (os parâmetros primeiro).

### Herança

```dataforge
blueprint Animal(nome):
    action falar():
        yield "..."
    action apresentar():
        yield self.nome + " diz " + self.falar()

blueprint Cachorro(nome) extends Animal:
    action falar():
        yield "Au au"

out (spawn Cachorro("Rex")).apresentar()     // Rex diz Au au
```

### root (super)

```dataforge
blueprint Base(nome):
    action descrever():
        yield "Base:" + self.nome

blueprint Derivada(nome) extends Base:
    action descrever():
        yield "Derivada[" + root.descrever() + "]"
```

### Traits (interfaces)

```dataforge
trait Serializavel:
    action serializar()

blueprint Produto(nome, preco) with Serializavel:
    action serializar():
        yield {"nome": self.nome, "preco": self.preco}
```

Um blueprint pode compor vários traits: `with A, B`.

### Membros estáticos

```dataforge
blueprint Contador:
    static total := 0
    action inc():
        Contador.total := Contador.total + 1

c := spawn Contador()
c.inc()
out Contador.total      // 1
```

### Sobrecarga de operadores

Defina os métodos `add`, `sub`, `mul`, `div`, `mod`, `pow`, `floordiv`:

```dataforge
blueprint Vetor(x, y):
    action add(o):
        yield spawn Vetor(self.x + o.x, self.y + o.y)
    action mul(k):
        yield spawn Vetor(self.x * k, self.y * k)
    action toString():
        yield "<" + str(self.x) + ", " + str(self.y) + ">"

out str(spawn Vetor(1, 2) + spawn Vetor(3, 4))     // <4, 6>
out str(spawn Vetor(1, 2) * 3)                     // <3, 6>
```

### Introspecção

```dataforge
blueprint Animal(nome):
    action falar():
        yield "..."

p := spawn Animal("Rex")

out typeof(p)             // nome do blueprint
out class_name(p)
out get_fields(p)         // campos da instância
out get_methods(p)        // métodos disponíveis
out has_method(p, "falar")
out has_field(p, "nome")
out get_mro(p)            // ordem de resolução
```

---

## 11. Tratamento de erros

### monitor / handle / ensure

```dataforge
monitor:
    x := 10 / 0
handle e:
    out "capturado:", e.type, "-", e.message
ensure:
    out "sempre roda"
```

O valor ligado ao `handle` expõe `.type`, `.message`, `.line`, e se comporta como
texto quando concatenado.

**Um `monitor` sem `handle` não engole o erro** — ele só garante o `ensure` e
deixa o erro subir. Isso é intencional: silenciar erro é sempre explícito.

### handle tipado

```dataforge
monitor:
    x := 1 / 0
handle RuntimeError as e:
    out "só pego erro de execução:", e.message
```

Tipos: `RuntimeError`, `TypeError`, `NameError`, `IndexError`, `TriggerError`,
`ImportError`, `StackOverflowError`. `Error`, `Exception` e `Any` pegam tudo.

### trigger

```dataforge
action idade_valida(n):
    given n smaller 0:
        trigger "idade não pode ser negativa"
    yield n
```

### guard e validate

Pré-condições que saem cedo:

```dataforge
action raiz(n):
    guard n bigger_eq 0 otherwise:
        out "entrada inválida"
    yield sqrt(n)                    // só chega aqui se passou

action dividir(a, b):
    guard b isnt 0, "divisor não pode ser zero"     // dispara erro
    yield a / b
```

`validate` funciona igual, testando se o valor é verdadeiro.

### retry

```dataforge
tentativas := {"n": 0}
retry 5:
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] smaller 3:
        trigger "instabilidade"
    out "sucesso na tentativa", tentativas["n"]
handle e:
    out "desistiu:", e
```

### propagate

Registra e repassa o erro para cima:

```dataforge
action camada_media():
    monitor:
        camada_baixa()
    handle e:
        out "logando:", e.message
        propagate e.message
```

### assert

```dataforge
action media(nums):
    assert len(nums) bigger 0, "a lista não pode ser vazia"
    yield sum(nums) / len(nums)
```

---

## 12. Pipelines

O operador `>>` encadeia transformações sobre uma coleção.

### sift — filtrar

```dataforge
nums := [1, 2, 3, 4, 5, 6]
out nums >> sift n: n % 2 is 0       // [2, 4, 6]
```

### morph — transformar

```dataforge
nums := [1, 2, 3, 4, 5, 6]
out nums >> morph n: n ** 2          // [1, 4, 9, 16, 25, 36]
```

### distill — reduzir

```dataforge
nums := [1, 2, 3, 4, 5, 6]
out nums >> distill acc, v: acc + v 0        // 21
//                          ^expressão   ^valor inicial
```

### Encadeamento e múltiplas linhas

```dataforge
vendas := [120, 45, 300, 80, 500, 15, 250]

total := vendas
    >> sift v: v bigger_eq 100
    >> morph v: v * 1.1
    >> distill acc, v: acc + v 0
```

Uma linha que começa com `>>` continua a expressão anterior.

### Ações nomeadas no pipeline

```dataforge
action eh_primo(n):
    given n smaller 2:
        yield no
    i := 2
    persist i * i smaller_eq n:
        given n % i is 0:
            yield no
        i += 1
    yield yes

out [1, 2, 3, 4, 5, 6, 7] >> sift eh_primo      // [2, 3, 5, 7]
```

### Alternativa: métodos

A mesma lógica, sem `>>`:

```dataforge
nums := [1, 2, 3, 4, 5, 6]
out nums.filter(lambda n: n % 2 is 0).map(lambda n: n * 10)
out nums.reduce(lambda a, b: a + b, 0)
```

---

## 13. Módulos

### Importar da biblioteca padrão

```dataforge
adopt Arcane.Math as Math
adopt Arcane.Text as Text

out Math.sqrt(16)        // 4.0
out Text.slug("Ola Mundo")
```

Os nomes curtos também valem: `adopt Math as M`.

Importar um módulo inexistente dispara `ImportError_` com a lista do que existe.

### Importar um arquivo local

`geometria.df`:

```dataforge
steady PI := 3.14159

action area_circulo(raio):
    yield PI * raio ** 2

relay PI, area_circulo
```

`main.df`, na mesma pasta:

```dataforge
adopt geometria as geo
out geo.area_circulo(2)
```

### Os 13 módulos

| Módulo | Para quê |
|--------|----------|
| `Arcane.Math` | Matemática e estatística (51 funções) |
| `Arcane.Text` | Manipulação de texto, tabelas, caixas (58) |
| `Arcane.Analytics` | Análise de dados, regressão, clustering (65) |
| `Arcane.Functional` | Utilitários funcionais, lentes, mônadas (56) |
| `Arcane.Database` | SQLite: tabelas, queries, migrações (39) |
| `Arcane.Test` | Asserções e suítes de teste (34) |
| `Arcane.Regex` | Expressões regulares e validadores BR (32) |
| `Arcane.IO` | Arquivos, JSON, CSV, diretórios (27) |
| `Arcane.Http` | Servidor HTTP com rotas e middleware (17) |
| `Arcane.Async` | Promessas, filas, agendamento (46) |
| `Arcane.Data` | DataFrames e transformações (13) |
| `Arcane.Web` | Cliente HTTP, URL, JSON (11) |
| `Arcane.Cortex` | Blocos de rede neural e NLP (5) |

Detalhes em [`BIBLIOTECA_PADRAO.md`](BIBLIOTECA_PADRAO.md).

---

## 14. Concorrência

### async / await

```dataforge
async action buscar(id):
    yield {"id": id, "nome": "Usuario " + str(id)}

usuario := await buscar(7)
out usuario
```

### thread

```dataforge
resultados := []

thread:
    cycle i from 1 to 3:
        resultados.append(i)

wait 200        // espera 200 ms
out len(resultados)
```

### channel

```dataforge
channel fila
fila.send("a")
fila.send("b")
out fila.receive()      // a
out fila.receive()      // b
out fila.receive()      // void   (canal vazio)
```

### parallel

```dataforge
parallel:
    out "tarefa A"
    out "tarefa B"
    out "tarefa C"
```

### Streams reativos

```dataforge
s := stream([10, 20, 30, 40])
observe valor in s:
    given valor bigger 35:
        halt
    out valor
```

---

## 15. Projeto final

Um inventário que usa quase tudo:

```dataforge
adopt Arcane.Text as Text

blueprint Produto(codigo, nome, preco, quantidade):
    action valor_total():
        yield self.preco * self.quantidade

    action baixa(qtd):
        guard qtd smaller_eq self.quantidade, "estoque insuficiente para " + self.nome
        self.quantidade := self.quantidade - qtd
        yield self.quantidade

    action toString():
        yield self.codigo + " " + self.nome

estoque := [
    spawn Produto("P01", "Mouse", 80.0, 15),
    spawn Produto("P02", "Teclado", 200.0, 4),
    spawn Produto("P03", "Monitor", 1200.0, 2)
]

patrimonio := estoque
    >> morph p: p.valor_total()
    >> distill acc, v: acc + v 0

criticos := estoque >> sift p: p.quantidade smaller 5

out Text.box("Inventario")
cycle p in estoque:
    out "  " + p.nome.pad_end(10) + str(p.quantidade).pad_start(4) + "   R$ " + str(p.valor_total())

out ""
out "patrimonio: R$", patrimonio
out "criticos:", criticos >> morph p: p.nome

monitor:
    estoque[2].baixa(99)
handle e:
    out "bloqueado:", e
```

Saída:

```
┌────────────┐
│ Inventario │
└────────────┘
  Mouse        15   R$ 1200.0
  Teclado       4   R$ 800.0
  Monitor       2   R$ 2400.0

patrimonio: R$ 4400.0
criticos: [Teclado, Monitor]
bloqueado: estoque insuficiente para Monitor
```

---

## Continuando

- **[`exercicios/`](../exercicios)** — 120 exercícios comentados, do "Olá mundo"
  a um interpretador RPN. Cada um verifica o próprio resultado com `assert`.
  Rode todos com `python3 exercicios/run_all.py`.
- **[`examples/`](../examples)** — 42 programas maiores: banco, loja, jogos,
  calculadora científica.
- **[`REFERENCIA.md`](REFERENCIA.md)** — a gramática e todas as palavras-chave.
- **[`BIBLIOTECA_PADRAO.md`](BIBLIOTECA_PADRAO.md)** — os módulos `Arcane.*`.
