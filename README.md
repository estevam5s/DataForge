<div align="center">

<img src="https://dataforge-lang.vercel.app/marca-256.png" alt="DataForge" width="120" height="120">

# DataForge

**Uma linguagem de programação interpretada, de propósito geral,
com vocabulário próprio.**

<sub>

`Python 3.10+` · `sem dependências no runtime` · `Next.js 15` · `React 19` ·
`TypeScript` · `Tailwind CSS` · `Supabase` · `SQLite` · `Docker` · `Vercel`

</sub>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.1.1-green.svg)](https://github.com/estevam5s/DataForge)
[![PyPI](https://img.shields.io/badge/pypi-dataforge--lang-blue.svg)](https://pypi.org/project/dataforge-lang/)
[![Tests](https://img.shields.io/badge/testes-4785%20passando-brightgreen.svg)](tests/)
[![Exercises](https://img.shields.io/badge/exerc%C3%ADcios-387%2F387-brightgreen.svg)](exercicios/)
[![Runtime deps](https://img.shields.io/badge/depend%C3%AAncias%20no%20runtime-nenhuma-brightgreen.svg)](pyproject.toml)

DataForge não é um DSL nem um transpilador. Tem **lexer, parser recursivo
descendente, AST tipada, analisador estático e interpretador de árvore
próprios**, escritos em Python puro — um programa `.df` roda em qualquer
máquina com Python 3.10+, sem `pip install` de mais nada.

Traz tipos verificados, pattern matching estrutural, pipelines na gramática,
generators preguiçosos, records imutáveis, 95 métodos mágicos, gerenciador de
pacotes com semver e lockfile, um framework web (**Kiln**), um framework de
testes (**Crucible**), um acesso a bancos de dados por protocolo próprio
(**Forge**) e **87 módulos** de biblioteca padrão com **2321 símbolos**.

[Instalação](#instalação) • [Tutorial](doc/TUTORIAL.md) • [Referência](doc/REFERENCIA.md) • [397 exercícios](exercicios/) • [Biblioteca](doc/BIBLIOTECA_PADRAO.md) • [Site](https://dataforge-lang.vercel.app) • [Roadmap](doc/ANALISE_E_ROADMAP.md)

</div>

---

```dataforge
adopt Arcane.Collections as Col

record Produto:
    nome: String
    preco: Number
    estoque: Integer

enum Situacao:
    EmFalta
    Critico
    Normal

action situacao_de(p: Produto) -> Situacao:
    match p:
        point Produto(estoque := 0):
            yield Situacao.EmFalta
        point Produto(estoque := e) when e smaller 5:
            yield Situacao.Critico
        default:
            yield Situacao.Normal

estoque := [
    Produto("Mouse", 80.0, 15),
    Produto("Teclado", 200.0, 3),
    Produto("Monitor", 1200.0, 0)
]

patrimonio := estoque
    >> morph p: p.preco * p.estoque
    >> distill acc, v: acc + v 0

cycle p in Col.sort_by_field(estoque, "preco", yes):
    out $"{p.nome.pad_end(10)} {situacao_de(p).name.pad_end(10)} R$ {p.preco * p.estoque}"

out $"\npatrimônio: R$ {patrimonio}"
out $"repor: {[p.nome cycle p in estoque given situacao_de(p) isnt Situacao.Normal]}"
```

```
Monitor    EmFalta    R$ 0.0
Teclado    Critico    R$ 600.0
Mouse      Normal     R$ 1200.0

patrimônio: R$ 1800.0
repor: [Teclado, Monitor]
```

---

## Por que DataForge

| | |
|---|---|
| **Vocabulário que descreve intenção** | `given`/`orif`/`otherwise`, `cycle`, `blueprint`, `monitor`/`handle`/`ensure` — as palavras dizem o que o código faz |
| **Tipos quando você quiser** | anotações opcionais, verificadas em tempo de execução **e** por análise estática |
| **Erros que ensinam** | `dataforge check` aponta linha, coluna e sugere a correção antes de executar |
| **Pattern matching estrutural** | por tipo, sequência, record, vault, enum — com guardas |
| **Pipelines são sintaxe** | `>> sift`, `>> morph`, `>> distill` fazem parte da gramática |
| **Generators preguiçosos** | `stream action` + `emit`, inclusive sequências infinitas |
| **Ferramentas oficiais** | `check`, `test`, `fmt`, `lint`, `doc`, `repl`, `init` |
| **Bateria inclusa** | 87 módulos com 2321 símbolos + 228 funções globais |
| **Zero dependências** | Python 3.10+ e nada mais |

---

## Instalação

**Pelo pip** — a forma mais curta, em qualquer sistema:

```bash
pip install dataforge-lang
```

Ela traz o interpretador, os 87 módulos da biblioteca, os 65 comandos e a
extensão do VS Code (`dataforge editor` a instala). Sem dependência externa
nenhuma: `pip` baixa um pacote e mais nada.

**macOS e Linux** — um comando, com ambiente próprio:

```bash
curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
```

Com `wget`, se preferir:

```bash
wget -qO- https://dataforge-lang.vercel.app/instalar.sh | sh
```

**Windows** (PowerShell):

```powershell
irm https://dataforge-lang.vercel.app/instalar.ps1 | iex
```

O instalador cria um ambiente próprio em `~/.dataforge`. Não mexe no Python
do sistema, não pede sudo, e desinstalar é apagar a pasta.

Ele também instala a **coloração de sintaxe** no VS Code, Insiders, Cursor,
VSCodium e Windsurf — todos os que encontrar. Reinicie o editor e todo `.df`
abre com as palavras reservadas coloridas, 23 snippets e a indentação de 4
espaços que a linguagem exige. Para refazer isso depois: `dataforge editor`.

**Docker** — sem instalar nada, nem Python:

```bash
docker run --rm -it estevan5s/dataforge repl
docker run --rm -v "$PWD:/app" estevan5s/dataforge run main.df
```

**Do código-fonte**:

```bash
git clone https://github.com/estevam5s/DataForge.git
cd DataForge
pip install -e .
```

Guia completo, com solução de problemas:
[`doc/INSTALACAO.md`](doc/INSTALACAO.md) ou
[dataforge-lang.vercel.app/docs/instalacao](https://dataforge-lang.vercel.app/docs/instalacao).

### Primeiro projeto

```bash
dataforge init meu-app
cd meu-app
dataforge run
dataforge test
```

### Pacotes

O gerenciador vem junto — não há binário separado:

```bash
dataforge add validador       # instala e grava no forge.toml
dataforge add tabela datas
dataforge install             # instala o que o forge.toml declara
dataforge search cpf          # procura no registro
dataforge list                # o que está instalado
```

```dataforge
adopt validador as V
adopt tabela as Tb

out V.cpf("529.982.247-25")                        // yes
out Tb.render([["Ana", 30]], ["Nome", "Idade"])
```

Semver (`^1.2.3`, `~1.2`, `>=1.0 <2.0`), lockfile com sha256, dependências
de registro, pasta local, git ou URL. Detalhes em
[Pacotes](https://dataforge-lang.vercel.app/docs/pacotes).

---

## A linguagem

### Fundamentos

```dataforge
nome := "DataForge"
steady VERSAO := "4.0.0"
idade: Integer := 30                 // tipo opcional, verificado

out $"Ola {nome}, versão {VERSAO}"   // interpolação
out 7 ~/ 2, 2 ** 10, 0 <= 5 <= 10    // operadores
out "a" in "casa", void ?? "padrão"  // pertinência, coalescência
```

### Controle de fluxo

```dataforge
idade := 30

given idade bigger_eq 18:
    out "adulto"
orif idade bigger_eq 12:
    out "adolescente"
otherwise:
    out "criança"

rotulo := "par" given idade % 2 is 0 otherwise "impar"    # ternário

cycle i from 1 to 5 step 2:
    out i

persist idade bigger 0:
    idade -= 10
```

### Coleções

```dataforge
nums := [1, 2, 3, 4, 5, 6]

out [n * n cycle n in nums given n % 2 is 0]    // compreensão
out {n: n * 2 cycle n in nums}                  // compreensão de vault
out nums[1:4], nums[::-1]                       // fatiamento
out [...nums, 7]                                // spread

primeiro, ...resto := nums                      // desestruturação
{nome, idade} := {"nome": "Ana", "idade": 30}
```

### Ações

```dataforge
action somar(a: Integer, b: Integer := 0) -> Integer:
    yield a + b

dobro := lambda x: x * 2

action registrar(fn):                  # um decorador é uma ação que envolve outra
    action envolvida(dados):
        out $"processando {len(dados)} item(ns)"
        yield fn(dados)
    yield envolvida

mark @registrar
action processar(dados):
    defer:
        out "limpou"                   # roda em qualquer caminho de saída
    yield dados >> morph d: d * 2

out somar(2), dobro(21), processar([1, 2, 3])
```

### Records e enums

```dataforge
record Usuario:
    nome: String
    idade: Integer
    email: String := "sem@email"

    action maior_de_idade():
        yield self.idade bigger_eq 18

u := Usuario("Ana", 30)
u2 := u with {"idade": 31}          // cópia; records são imutáveis
out Usuario("Ana", 30) is u          // yes — igualdade estrutural

enum Status:
    Ativo
    Inativo := "off"

out Status.Ativo.name, Status.from_value("off").name
```

### Pattern matching

```dataforge
action descrever(valor):
    match valor:
        point 0:
            yield "zero"
        point Integer as n when n bigger 100:
            yield "grande"
        point [primeiro, ...resto]:
            yield $"lista de {len(resto) + 1}"
        point Usuario(nome := n, idade := i) when i smaller 18:
            yield $"{n} é menor"
        point {"tipo": t}:
            yield $"vault {t}"
        point Status.Ativo:
            yield "ligado"
        default:
            yield "outro"

out descrever(0), descrever(500), descrever([1, 2, 3])
out descrever(Usuario("Kid", 12)), descrever(Status.Ativo)
```

### Erros

```dataforge
record Conta:
    titular: String
    saldo: Number

action sacar(conta, valor):
    guard valor bigger 0, "valor precisa ser positivo"
    guard valor smaller_eq conta.saldo, "saldo insuficiente"
    yield conta with {"saldo": conta.saldo - valor}

conta := Conta("Ana", 100)
out sacar(conta, 30)

monitor:
    sacar(conta, 9999)
handle SaldoInsuficienteError:
    out "sem saldo"
handle KeyError as e:
    out $"conta inexistente: {e.message}"
handle e:
    out $"{e.type}: {e.message}"
ensure:
    out "sempre roda"

tentativas := {"n": 0}
retry 3:
    tentativas["n"] := tentativas["n"] + 1
    given tentativas["n"] smaller 3:
        trigger "instabilidade"
    out $"conseguiu na tentativa {tentativas["n"]}"
handle e:
    out $"desistiu: {e}"
```

Erros trazem a pilha de chamadas:

```
RuntimeError: Division by zero
  em calculadora.df:12:15

    12 |     yield total / divisor
       |           ^

  Pilha de chamadas (mais recente primeiro):
    em media                  calculadora.df:12
    em relatorio              calculadora.df:28
    em main                   calculadora.df:45
```

### Pipelines e generators

```dataforge
record Venda:
    cliente: String
    valor: Number

vendas := [Venda("Ana", 250), Venda("Bruno", 80), Venda("Carla", 400)]

out vendas
    >> sift v: v.valor bigger 100
    >> morph v: v.valor * 1.1
    >> distill acc, v: acc + v 0

stream action fibonacci():
    a := 0
    b := 1
    persist yes:
        emit a
        a, b := b, a + b

out fibonacci().take(10)      // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Módulos

```dataforge
adopt Arcane.Math as Math              # o módulo inteiro
adopt Arcane.Math.{sqrt, floor}        # seletivo
adopt {sqrt as raiz} from Arcane.Math  # com apelido

out Math.factorial(5), sqrt(16), raiz(25)

action somar(a, b):
    yield a + b

relay somar                            # controla o que este módulo exporta
```

---

## Tabela de tradução

| Conceito | DataForge | | Conceito | DataForge |
|----------|-----------|---|----------|-----------|
| `=` | `:=` | | `class` / `new` | `blueprint` / `spawn` |
| `const` | `steady` | | `@dataclass(frozen)` | `record` |
| `print` | `out` | | `enum` | `enum` |
| f-string | `$"{x}"` | | `self` / `super` | `self` / `root` |
| `if/elif/else` | `given/orif/otherwise` | | `interface` | `trait` |
| ternário | `a given c otherwise b` | | `import` / `export` | `adopt` / `relay` |
| `match/case` | `match` / `point` / `when` | | `try/catch/finally` | `monitor/handle/ensure` |
| `for` | `cycle` | | `throw` | `trigger` |
| `while` | `persist` | | `true/false/null` | `yes/no/void` |
| `break`/`continue` | `halt`/`skip` | | `??` / `?.` / `in` / `is not` | iguais |
| `def` / `return` | `action` / `yield` | | `==` / `!=` | `is` / `isnt` |
| generator | `stream action` / `emit` | | `filter/map/reduce` | `>> sift/morph/distill` |
| list comprehension | `[e cycle x in f given c]` | | `//` (div. inteira) | **`~/`** |
| spread / rest `...` | igual | | decorador | `mark @nome` |

---

## Ferramentas

```bash
dataforge init [pasta]        # cria forge.toml e o esqueleto
dataforge run [arquivo.df]    # executa (sem argumento usa a entrada do manifesto)
dataforge check <alvo>        # análise estática: nomes, aridade, tipos
dataforge test [alvo] -v      # descobre e roda *_test.df e tests/
dataforge fmt <alvo> --check  # formata
dataforge lint <alvo>         # estilo e higiene
dataforge doc <alvo> --out=…  # documentação Markdown
dataforge repl                # console interativo
dataforge info                # mostra o manifesto
```

### `dataforge check` — o que ele encontra

```
src/main.df:9:11: erro: Parameter 'a' of 'somar' expects Integer but got String
    sugestão: Pass a Integer
src/main.df:10:5: erro: Undefined action 'sommar'
    sugestão: Did you mean 'somar'?
src/main.df:23:1: aviso: Action 'processar' declares '-> Integer' but can end without a 'yield'
    sugestão: Add a 'yield' at the end, or drop the return type
```

Nomes indefinidos, aridade errada, tipos incompatíveis, campos de record, membros
de enum, constantes reatribuídas, código inalcançável, retorno ausente — tudo
antes de executar uma linha.

### `forge.toml`

```toml
[project]
name = "meu-app"
version = "0.1.0"
entry = "src/main.df"
dataforge = ">=4.0"

[scripts]
start = "run src/main.df"
test = "test tests/"
```

Qualquer chave em `[scripts]` vira um comando: `dataforge start`.

### Em integração contínua

```bash
dataforge fmt . --check && dataforge check . && dataforge test
```

---

## Biblioteca padrão

<!-- stdlib:inicio -->
87 módulos, 2321 símbolos, mais 231 funções globais sem import.

| Módulo | Símbolos | Para quê |
|--------|----------|----------|
| `Arcane.Vitrine` | 213 | O framework de dashboards e aplicações de dados: você escreve um programa de cima para baixo e ele vira uma página web, com componentes, layout, gráficos em SVG, estado por sessão e cache — servido pelo Kiln. |
| `Kiln` | 80 | Framework web: rotas, middleware, templates, sessão e arquivos estáticos. |
| `Arcane.Math` | 72 | Matemática, álgebra linear e estatística básica. |
| `Arcane.Color` | 66 | Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore. |
| `Arcane.Analytics` | 65 | Análise de dados: estatística, regressão, clustering e gráficos ASCII. |
| `Arcane.Database` | 64 | Banco de dados SQLite: tabelas, consultas, migrações e importação. |
| `Arcane.Collections` | 63 | Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca. |
| `Arcane.Crucible` | 61 | Framework de testes: suítes, matchers, fixtures, dublês e benchmark. |
| `Arcane.Text` | 59 | Manipulação de texto, formatação, tabelas e conversão de caixa. |
| `Arcane.Functional` | 56 | Utilitários funcionais: composição, lentes, Maybe/Either, transdutores. |
| `Arcane.Seguranca` | 54 | Escape por destino (HTML, atributo, JS, URL, shell, SQL LIKE, CSV, cabeçalho, log), sanitização de HTML por lista de permitidos, política e força de senha com vazamento por k-anonimato, TOTP/HOTP e códigos de recuperação, token e URL assinados com prazo e propósito, varredura de segredos por formato, redação de PII, defesa de SSRF e de travessia de caminho, limitador de taxa, bloqueio progressivo, trilha de auditoria encadeada e dez regras de análise estática. |
| `Arcane.Time` | 54 | Datas, horas, durações e cronometragem. |
| `Arcane.Crypto` | 53 | Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305). Assina e verifica JWT (HS256/384/512), com o algoritmo decidido por quem verifica e não pelo token. |
| `Arcane.Async` | 52 | Promessas, filas, agendamento e execução concorrente. |
| `Arcane.Regex` | 46 | Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone). |
| `Arcane.Iter` | 44 | Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize. |
| `Arcane.OS` | 43 | Sistema operacional, ambiente, disco e processo atual. |
| `Arcane.Lavra` | 42 | A consulta tipada: o cliente diz exatamente quais campos quer, numa consulta indentada, e recebe exatamente aqueles. O esquema nasce dos 'record' que já existem; traz resolvedores, contexto, trechos, variáveis, diretivas, contratos, uniões, introspecção, validação antes de executar, lote contra o N+1, paginação por cursor, limites de profundidade e custo, assinaturas por WebSocket e federação de vários serviços. |
| `Arcane.Reflexo` | 38 | Reflexão sobre blueprints, contratos e objetos: campos, métodos, modificadores, MRO, herdeiros, anotações, invocação por nome respeitando a visibilidade, criação de tipos em execução e diagrama de classes em Mermaid. |
| `Arcane.Telegram` | 37 | Bots de Telegram, do primeiro '/start' ao webhook em producao: cliente da Bot API com o limite de taxa lido de onde ele chega, tratadores por comando, texto, botao, midia e consulta inline, conversa como maquina de estados por chat, teclados, o escape de MarkdownV2 que salva a mensagem inteira, e uma sonda que testa o bot sem token e sem rede. |
| `Arcane.Concurrent` | 35 | Threads, processos, canal bloqueante, grupo de tarefas e prazo. |
| `Arcane.Test` | 34 | Asserções e organização de suítes de teste. |
| `Arcane.Estrutura` | 33 | Layout binario com NOME, e o ponteiro que o percorre: uma estrutura de campos nomeados com a ordem dos bytes cobrada e o alinhamento declarado (e conferido), uma janela que le e escreve no bloco original sem copiar, um bloco que sabe dizer quando foi liberado, e um ponteiro com aritmetica por ELEMENTO, cast, distancia e dono fraco. Fica entre o Arcane.Bytes, que empacota por formato posicional, e o Arcane.C, que exige FFI. |
| `Arcane.IO` | 33 | Arquivos, diretórios, JSON, CSV e shell. |
| `Arcane.Forge` | 31 | Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface. |
| `Arcane.Excel` | 29 | Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame. |
| `Arcane.Laco` | 29 | O laco de eventos, o escalonador e as fibras: UMA thread dormindo no seletor do sistema (epoll, kqueue ou select) em vez de uma thread por conexao. Fila de prazos com 'apos' e 'a_cada', fila de prontas com teto opcional (contrapressao), executor para o trabalho que bloqueia, cancelamento, e fibras de verdade — um 'stream action' suspenso em cada 'emit'. |
| `Arcane.IoT` | 28 | Arduino e ESP32: Firmata pelo cabo, sketch gerado e gravado, sensores, MQTT — e um simulador de placa para testar sem hardware. |
| `Arcane.Compilador` | 26 | O caminho de compilacao como dado: os tokens, a arvore, o HIR (a arvore depois do acucar, com a lista do que e acucar e do que so parece), o MIR (bloco basico, aresta, laco e tratador) e as analises que so o grafo responde — alcance, vivacidade, constante em todo caminho, escapatoria e o nome que so um ramo define. O LIR diz o que o compilador de fechamentos compilou e o que recuou para a arvore. |
| `Arcane.Serialization` | 26 | JSON, CSV, INI, TOML, XML e conversões entre eles. |
| `Arcane.Bytes` | 25 | Dados binários: empacotar e desempacotar campos com a ordem dos bytes declarada, um cursor que anda pelo bloco sem acertar índice à mão, janela que olha sem copiar, hexadecimal, base64, bits, despejo estilo hexdump e comparação em tempo fixo. |
| `Arcane.C` | 25 | Falar com biblioteca nativa: abrir .so/.dylib/.dll, chamar funcao com assinatura declarada, struct e uniao com o layout de verdade (tamanho, alinhamento e deslocamento), ponteiro cru com aritmetica, memoria alocada a mao e callback — uma acao da linguagem chamada de dentro do C. Sobre ctypes, da biblioteca padrao: zero dependencia. |
| `Arcane.Cortex` | 25 | Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA. |
| `Arcane.Memoria` | 24 | O ciclo de vida visto de dentro: referência fraca, mapa fraco, ação ao descartar, instâncias vivas por blueprint, tamanho e layout. E o COLETOR sob controle: ligar, desligar, 'sem_gc' num trecho sensível a latência (que religa mesmo se o corpo falhar), limiares por geração, 'congelar' o que já vive para tirá-lo das varreduras, e a conta por geração. Mais a arena: um lote preparado de uma vez e reaproveitado, com 'limpar' soltando tudo numa chamada. |
| `Arcane.Dominio` | 23 | As pecas de um modelo de dominio que se sustenta (DDD): valor (igualdade por conteudo, imutavel, com regra cobrada na criacao), entidade (igualdade por identidade), agregado (a unica porta de escrita, com invariantes conferidas na SAIDA de cada comando e desfazer quando o comando falha no meio), evento (um fato no passado, imutavel), regra (condicao de negocio que se combina com e/ou/nao e explica o "nao"), repositorio (guarda agregados INTEIROS), unidade de trabalho (confirma tudo ou nada, e so entao publica) e contexto delimitado (com a traducao que atravessa a fronteira). |
| `Arcane.Malha` | 23 | Chamada entre serviços que não mente: cliente HTTP com prazo, retry com recuo e tremor, disjuntor de três estados, descoberta por nome e propagação automática do rastro do pedido. |
| `Arcane.Observar` | 22 | Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados. |
| `Arcane.Padroes` | 20 | Os padrões de projeto que pedem mecanismo: único, pool, construtor, protótipo, flyweight, proxy, adaptador, composto, comandos com desfazer, cadeia, especificação, máquina de estados, memento, visitante, observável, mediador, repositório e barramento. |
| `Arcane.GitHub` | 19 | O que um programa precisa para viver no GitHub: no Actions, saídas, variáveis e resumo com delimitador seguro, anotações escapadas que aparecem na linha do PR, máscara linha a linha e grupos; webhooks com assinatura HMAC conferida em tempo constante sobre os bytes originais; e a API REST com paginação por Link e o limite de taxa que sobrou. |
| `Arcane.Dsl` | 18 | Combinadores para escrever uma linguagem pequena, propria: texto, numero, nome, aspas, espaco, sequencia, alternativa, repeticao, opcional e separado_por, com 'analisar' devolvendo Resultado e a falha dizendo a posicao e o que era esperado. |
| `Arcane.Lago` | 18 | Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação. |
| `Arcane.Reativo` | 18 | Valores que avisam quando mudam: sinal (um valor com estado), derivado (calculado de outros, preguicoso e memorizado, com as dependencias DESCOBERTAS na execucao), efeito (o que acontece quando muda, com limpeza entre ciclos) e observavel (um fluxo no tempo, com morph, sift, distill, distintos, esperar, limitar, combinar e juntar). A diferenca entre valor e fluxo e mantida de proposito: um clique e fluxo, um saldo e valor. |
| `Arcane.Http` | 17 | Servidor HTTP: rotas, middleware, JSON, arquivos estáticos. |
| `Arcane.Stream` | 17 | Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo. |
| `Arcane.Algoritmos` | 16 | Os algoritmos clássicos com a complexidade como dado: busca binária, merge sort estável, counting sort, BFS, DFS, ordem topológica que mostra o ciclo, Dijkstra que recusa peso negativo, LCS, Levenshtein, mochila 0/1, KMP e o crivo — cada um conferido contra uma implementação ingênua. |
| `Arcane.Decimal` | 16 | Número decimal exato, para quando 0,1 + 0,2 precisa dar 0,3 — dinheiro, imposto, e todo número que alguém confere na mão. |
| `Arcane.Perfil` | 16 | Medir com rigor, onde o 'Bench' da a media: percentis (p50, p95, p99, p999) com aquecimento separado, comparacao com SIGNIFICANCIA estatistica (Mann-Whitney, que nao supoe normalidade — tempo de execucao nao e normal), linha de base guardada para acusar regressao no CI, flame graph das ACOES da linguagem em SVG sem nada de fora, pausas do coletor medidas na fonte e contencao de trava. |
| `Arcane.Posse` | 16 | Quem e o dono, quem tomou emprestado, e quando solta: posse exclusiva com liberacao deterministica ('dono' e 'com', o RAII), emprestimo com escopo (muitos leem OU um escreve, cobrado quando roda), contagem de referencia deterministica ('compartilhado' e 'atomico') e referencia fraca que quebra o ciclo. |
| `Arcane.Qualidade` | 16 | Qualidade de dados: as seis dimensões, perfil, validação e limpeza. |
| `Arcane.Rede` | 16 | TCP, UDP, DNS e TLS: conexão com prazo, leitura que insiste até completar, servidor de uma thread por conexão, datagrama, resolução de nome, porta livre, espera de porta abrir e a validade do certificado de um host. |
| `Arcane.Inicio` | 15 | O que roda ANTES da primeira linha: as fases da partida nomeadas e em ordem, e quanto cada 'adopt' custou — que e a unica forma de responder 'por que o programa demora a comecar?' sem cronometrar a mao. Mais armazenamento por THREAD com inicializacao e finalizador (o 'threading.local' da o armazem e nao da o resto), e a pilha que se pergunta: profundidade, teto, quanto falta e os quadros abertos. |
| `Arcane.Process` | 15 | Execução de processos externos, com stdout, stderr e código de saída. |
| `Arcane.Logging` | 14 | Registro estruturado de eventos, com níveis e destinos. |
| `Arcane.Url` | 14 | Endereços: ler um URL em partes, montar a partir delas, resolver caminho relativo como um navegador, trocar parâmetros preservando os outros, query string em vault (ou em cluster, quando a chave repete) e escape para caminho e para valor. |
| `Arcane.Archive` | 13 | Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb. Comprime e descomprime VALORES em memória, em deflate cru ou em gzip, com a taxa medida. |
| `Arcane.Data` | 13 | DataFrames, séries e transformações tabulares. |
| `Arcane.Macro` | 13 | A arvore como dado: ler o corpo de uma acao, percorrer, transformar e gerar codigo. 'citar' transforma texto em arvore, 'reescrever' devolve uma acao com o corpo trocado, 'nome_fresco' e 'renomear' dao higiene, e 'derivar' e a macro de atributo que gera __str__, __eq__, __lt__ e para_vault a partir dos campos. |
| `Arcane.Objetos` | 13 | Cópia rasa e funda, congelamento, igualdade estrutural, hash coerente, ordenação por campos e serialização polimórfica que só reconstrói os tipos autorizados e resolve ciclos. |
| `Arcane.Resultado` | 13 | A falha como VALOR, e a ausencia com nome: 'ok'/'falha' para quem devolve o erro em vez de levanta-lo, com 'mapear', 'entao', 'recuperar', 'ou' e 'todos' (a primeira falha vence); e 'Talvez' ('algo'/'nada') para onde 'void' e ambiguo — distinguir 'a chave nao esta la' de 'a chave vale void'. |
| `Arcane.Stm` | 13 | Memoria transacional: escritas que acontecem JUNTAS ou nao acontecem. Variavel transacional, 'atomicamente' com validacao otimista e repeticao no conflito, 'retentar' que espera em vez de girar, 'ou_entao' para compor duas operacoes bloqueantes, e estatisticas de conflito. |
| `Arcane.Cli` | 12 | A linha de comando de um programa escrito em DataForge: opções tipadas com valor padrão e escolhas, argumentos posicionais, subcomandos, ajuda gerada da declaração, perguntas no terminal e console interativo. |
| `Arcane.Meta` | 12 | Metadados de decorador: ler @Nome em tempo de execução. |
| `Arcane.Ponte` | 12 | A ponte para o Python: perguntar se um pacote existe, explorar o que ele oferece e converter o que ele devolve. |
| `Arcane.Ecossistema` | 11 | O inventario da implementacao, CONFERIDO contra ela. Cada componente do desenho do ecossistema aponta arquivos de verdade e carrega um de tres estados: 'existe', 'equivale' (ha outra peca que responde a mesma pergunta, nomeada) ou 'nao-existe' (com o porque escrito). 'conferir()' cobra as duas direcoes — todo caminho citado existe no disco, e todo modulo do nucleo aparece em algum componente —, e e isso que impede o mapa de mentir quando uma peca muda de nome. 'o_que_nao_existe()' e a resposta honesta a 'o DataForge tem backend LLVM?'. |
| `Arcane.Html` | 11 | Ler HTML de verdade: seletor CSS, texto que junta com espaço, links absolutos, tabela como dado, escapar contra XSS, limpar toda a marcação e podar deixando só as tags permitidas. |
| `Arcane.Pipeline` | 11 | Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório. |
| `Arcane.Web` | 11 | Cliente HTTP, URL encoding e JSON. |
| `Arcane.Abi` | 10 | A superficie de um modulo e o CONTRATO dele, e quebra-la e o mesmo problema que quebrar uma ABI — com outro nome e o mesmo sintoma: nao e erro de quem publicou, e erro de quem consome, depois. Compara duas versoes e diz o que quebrou (simbolo removido, aridade incompativel, parametro renomeado, tipo trocado, campo novo obrigatorio) e qual bump de semver a mudanca EXIGE. Mais o mapa de simbolos: de onde vem cada nome, o analogo do mapa que um ligador escreve. |
| `Arcane.Eventos` | 10 | Publicar e assinar sem as duas partes se conhecerem: emissor com curinga, ouvinte de uma vez só, contexto por thread que atravessa as camadas, fila de trabalho em segundo plano, e fila persistente em SQLite que sobrevive ao processo, com recuo exponencial, atraso e hora marcada, prioridade, chave contra repetição e carta morta. |
| `Arcane.Gramatica` | 10 | A gramática da linguagem como dado: as produções em EBNF, cada uma com um exemplo conferido contra o parser, a tabela de precedência provada pela árvore, os tokens de um texto, as instruções que o parser entendeu e a validação de sintaxe sem executar nada. |
| `Arcane.Janela` | 10 | Aplicação de mesa nativa com zero dependência: o Tk vem na biblioteca padrão. A árvore é separada do desenho, como na Vitrine — e por isso uma tela se testa sem display nenhum. |
| `Arcane.Privacidade` | 10 | O que a LGPD pede, como operações sobre dado: pseudonimização com chave (e não hash sem chave, que se desfaz), generalização de quase-identificadores, a medida do k-anonimato, minimização por lista de permitidos, retenção, consentimento por titular e por finalidade com histórico, os direitos de acesso e eliminação percorrendo todo lugar onde o dado mora, e contagem com privacidade diferencial. |
| `Arcane.Quadro` | 10 | A tabela de dados: colunas nomeadas e linhas como vault. Filtrar, agrupar, resumir, juntar, pivotar, limpar a ausência e a duplicata, converter tipos, normalizar, codificar e descrever — colunar por dentro, imutável por fora. |
| `Arcane.Tipos` | 10 | Reflexao sobre tipos: os metadados de um 'type' declarado (especie, base, regra, opaco), 'satisfaz' para conferir sem levantar, a forma ESTRUTURAL de um valor ('Cluster<Integer>', 'Tuple<Integer, String>') e os campos de um record ou instancia com o tipo de cada um. |
| `Arcane.API` | 7 | A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas. |
| `Arcane.Alvo` | 7 | 'Isso roda no navegador?', respondido a partir dos 'adopt'. Seis alvos descritos (servidor, cli, navegador, wasi, funcao serverless, embarcado) com o que cada um suporta e POR QUE nao suporta o resto, no mesmo vocabulario de capacidade do 'Arcane.Capacidade'. A leitura e ESTATICA e o modulo diz isso em 'limites()': um 'roda' quer dizer 'nao achei impedimento por esta via', e nao 'vai funcionar'. |
| `Arcane.Bench` | 7 | Medir, comparar e descobrir a classe de custo: tempo de uma ação, implementações lado a lado sem a ordem decidir quem ganha, e a curva medida em tamanhos crescentes dizendo qual O() descreve o que aconteceu. |
| `Arcane.Deteccao` | 7 | Regras de detecção sobre eventos, com correlação por chave em janela deslizante, supressão, gravidade e mapa para MITRE ATT&CK; indicadores de comprometimento com prazo e normalização; padrões sobre conteúdo e leitura de log de acesso. O alerta carrega os eventos que o causaram. |
| `Arcane.Capacidade` | 6 | A fronteira de CAPACIDADE: roda uma acao com a lista de poderes que ela pode alcancar, e recusa o resto pelo NOME da capacidade que falta. A ponte para o Python e capacidade propria, e nunca vem junto. NAO e caixa contra programa hostil, e o modulo diz isso em 'limites()': ele bloqueia a autoridade ambiente (o 'adopt'), e nao tira o que foi ENTREGUE — o que e o modelo de capacidade, nao um defeito. |
| `Arcane.Chaves` | 6 | Ciclo de vida de chave criptográfica: propósito cobrado, prazo, rotação que mantém as antigas decifrando o passado, identificador no dado cifrado, cifragem em envelope (DEK/KEK), recifragem, derivação por contexto (HKDF) e exportação do cofre cifrada pela senha mestra. |
| `Arcane.Email` | 6 | Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza no cabeçalho, SMTP com TLS por padrão, prévia sem enviar e caixa de teste com o mesmo contrato. |
| `Arcane.Integridade` | 6 | Provar que o que está aqui é o que foi posto aqui: o valor SRI de um script de CDN, o manifesto SHA-256 de uma pasta com o que foi acrescentado, removido e alterado, e o manifesto assinado com uma chave que mora fora dali. |
| `Arcane.Politica` | 6 | Motor de autorização: RBAC com herança, ABAC por atributo, ACL por objeto, grupos, isolamento por inquilino, negação explícita que vence o papel e delegação com prazo. O padrão é negar, e toda decisão diz qual regra a tomou — um motor que responde só sim/não é impossível de auditar. |
| `Arcane.Principios` | 6 | Os dez principios de design, cada um com uma prova que RODA e o numero que ela deu — duas delas rodam o analisador e uma roda o interpretador, porque 'verificacao antes de rodar' e 'custo zero quando desligado' sao coisas que se demonstram. O veredito nao e dez de dez de proposito: 5 cumpridos, 4 parciais e 1 que nao se aplica. E as nove TENSOES: onde dois principios se contradizem, qual venceu, o custo aceito e o arquivo onde a decisao mora. |
| `Arcane.Evolucao` | 5 | Como uma API muda sem pegar ninguém de surpresa: marcar uma ação como obsoleta (desde quando, por quê, o que usar) ou experimental, e manter um nome antigo que avisa. O aviso sai uma vez por ação, na saída de erro, e DF_OBSOLETOS=erro o transforma em erro no CI. |
| `Arcane.Injecao` | 5 | Contêiner de injeção de dependência: único, transitório e por escopo, fábrica, valor pronto, dependência preguiçosa e opcional, injeção por construtor, campo e método, e detecção de ciclo com a cadeia inteira. |
| `Arcane.Percurso` | 5 | O caminho inteiro de um arquivo, fase por fase, MEDIDO: lexer, parser, HIR, tipos, MIR, analises, SSA, passes e LIR, com o que cada fase produziu e quanto tempo levou. Responde 'onde o tempo vai' quando um arquivo demora a abrir no editor. Ele NAO executa o programa — executar e o que o programa faz, e um comando que mostra fases nao pode abrir soquete. Traz tambem as divergencias entre o caminho real e o desenho da referencia. |
<!-- stdlib:fim -->

Referência completa: [`doc/BIBLIOTECA_PADRAO.md`](doc/BIBLIOTECA_PADRAO.md)
(gerada a partir do código com `tools/gerar_doc_stdlib.py`).

---

## Kiln — o framework web

O DataForge tem um framework web próprio, com **sintaxe na linguagem**. Não é
um módulo com `lambda` dentro: uma rota se lê como uma rota.

```dataforge
adopt Kiln

server loja on 8080:
    middleware Kiln.logger()
    views "./paginas"

    route GET "/":
        render "catalogo.html" with {"produtos": produtos}

    route GET "/api/produtos/:id":
        p := achar(int(params["id"]))
        given p is void:
            respond 404 json {"erro": "não achei"}
        respond json p

    route POST "/api/produtos":
        respond 201 json criar(body)

ignite loja
```

Roteamento com `:param` e `*curinga`, middleware, CORS, limite de taxa,
autenticação, sessão com cookie, templates com escape automático, arquivos
estáticos e páginas de erro. **Zero dependências** — `http.server` e mais nada.

E dá para testar sem abrir socket:

```dataforge
r := Kiln.test(loja, "GET", "/api/produtos/2")
assert r["status"] is 200
```

O 404 e o **405 com `Allow`** vêm de graça; um erro na rota vira 500 sem
derrubar o servidor; `../` num caminho estático é recusado antes de o arquivo
ser aberto.

O projeto [`projetos/loja-web`](projetos/loja-web/) é um site completo —
catálogo, ficha, relatório, login e um `/relatorio.xlsx` gerado no pedido —
com 29 testes que rodam em 0,06 s.

Documentação: [doc/KILN.md](doc/KILN.md) ou
[dataforge-lang.vercel.app/docs/kiln](https://dataforge-lang.vercel.app/docs/kiln).

---

## Vitrine: um programa vira uma página web

Para **painel e aplicação de dados**, onde a página é o programa:

```dataforge
adopt Arcane.Vitrine as V

mark @V.cache
action vendas():
    yield DB.query(banco, "SELECT mes, receita, meta FROM vendas")

action painel():
    lado := V.lateral()
    regiao := lado.escolha("Região", ["Sudeste", "Sul", "Norte"])

    V.titulo("Dashboard de Vendas", icone := "📊")

    colunas := V.colunas(4)
    colunas[0].metrica("Receita", "R$ 850.000", variacao := 18.0)
    colunas[1].metrica("Clientes", "12.450", variacao := 8.0)
    colunas[2].metrica("Pedidos", "32.500", variacao := 14.0)
    colunas[3].metrica("Conversão", "8.4%", variacao := 1.2)

    V.grafico_linha(vendas(), x := "mes", y := ["receita", "meta"])
    V.frame(vendas())
    V.exportar_csv(vendas())

V.rodar(painel, porta := 8501)
```

A cada interação **o programa inteiro roda de novo**, e o estado da sessão
sobrevive — é o que dispensa callback e diffing. Não há HTML, CSS,
JavaScript nem build: o gráfico é SVG escrito no servidor, e o cliente são
~4 KB sem uma única CDN, porque painel de dados costuma rodar em rede
fechada.

Testar não precisa de navegador, porque a árvore de componentes é um dado:

```dataforge
t := V.testar(painel)
assert t.quantos("metrica") is 4

antes := t.metrica("Receita")
t.selecionar("Região", "Norte")
assert t.metrica("Receita") is not antes
assert not t.falhou()
```

Rode `dataforge run examples/vitrine_dashboard.df -- --servir` para ver.

Documentação: [doc/VITRINE.md](doc/VITRINE.md) ou
[dataforge-lang.vercel.app/docs/vitrine](https://dataforge-lang.vercel.app/docs/vitrine).

---

## Dados: banco, análise e planilhas

```dataforge
adopt Arcane.Database as DB
adopt Arcane.Analytics as An
adopt Arcane.Excel as Xls

registros := DB.query(banco, "SELECT * FROM vendas")
An.describe(An.from_records(registros))     # descreve cada coluna

livro := Xls.new()
aba := Xls.sheet(livro, "Vendas", registros)
Xls.formula(aba, "E7", "SUM(E2:E6)")        # o Excel calcula ao abrir
Xls.save(livro, "relatorio.xlsx")
```

O `.xlsx` é escrito e lido sem dependência externa — o arquivo abre no Excel,
no LibreOffice e no Google Sheets, e é lido de volta por openpyxl e pandas.

---

## Domínio: DDD com as distinções cobradas

```dataforge
adopt Arcane.Dominio as D

steady Dinheiro := D.valor("Dinheiro", ["quantia", "moeda"],
    regra := lambda v => v["quantia"] bigger_eq 0)

pedido := D.agregado("Pedido", "PED-7", total := 0)
pedido.invariante("o total nunca e negativo",
    lambda p => p.ler("total", 0) bigger_eq 0)

mark @pedido.comando("acrescentar")
action acrescentar(p, preco):
    p.mudar(total := p.ler("total", 0) + preco)
    p.aconteceu("ItemAcrescentado", {"preco": preco})

pedido.mudar(total := 999)      // recusado: só muda dentro de um comando
```

Um `blueprint` chamado `Pedido` com um comentário `// agregado` não impede
ninguém de mexer nos itens por fora. Aqui a invariante é conferida na **saída**
de cada comando, o comando recusado é **desfeito por inteiro** (estado, eventos
e versão), e o evento só é publicado quando a unidade de trabalho confirma —
publicar antes faz o mundo reagir a um fato que a transação ainda pode desfazer.

---

## Reativo: um valor que outros valores acompanham

```dataforge
adopt Arcane.Reativo as R

preco := R.sinal(10.0)
quantidade := R.sinal(3)
total := R.derivado(lambda => preco.ler() * quantidade.ler())

out total.ler()          // 30.0
quantidade.escrever(5)
out total.ler()          // 50.0 — ninguém recalculou à mão
```

O derivado é **preguiçoso e memorizado**, e as dependências são **descobertas**
na execução — não há lista para escrever, e por isso ela não envelhece na
primeira condição nova dentro da fórmula. A propagação tem duas fases: marcar o
grafo inteiro e, só então, avisar. Sem isso, um losango entrega um valor que
nunca existiu — um número errado na tela, que aparece e some sozinho.

**Sinal é valor; observável é fluxo.** Um clique é fluxo; um saldo é valor.
Frameworks que chamam os dois de "stream" fazem a pergunta *"qual é o valor
agora?"* deixar de ter resposta.

---

## Estruturas: layout binário com nome

```dataforge
adopt Arcane.Estrutura as Est

steady Cabecalho := Est.definir("Cabecalho", [
    ["magia", "u32"], ["versao", "u16"], ["registros", "u16"]
], ordem := "rede")

c := Cabecalho.ler(dados)
out c["versao"]

// E as janelas percorrem um arquivo de registros sem copiar nada:
cycle linha in Est.janelas(arquivo, Registro):
    out linha.ler("id"), linha.ler("preco")
```

Ele fica entre dois módulos que já existiam. `Arcane.Bytes` empacota por
**formato** e o resultado é posicional — `dados[3]` três meses depois não diz
nada. `Arcane.C` tem estrutura e ponteiro de verdade, e exige **FFI**: ler o
cabeçalho de um PNG não deveria precisar de `ctypes`.

A ordem dos bytes é obrigatória, o alinhamento é declarado e conferido, a janela
lê e escreve **no bloco**, e o ponteiro anda por **elemento** — `p + 1` num
`u32*` anda quatro bytes, como no C.

---

## Aprendendo

| Recurso | O que é |
|---------|---------|
| [**doc/TUTORIAL.md**](doc/TUTORIAL.md) | a linguagem do zero, com exemplos que rodam |
| [**doc/REFERENCIA.md**](doc/REFERENCIA.md) | gramática EBNF, palavras-chave, precedência, semântica |
| [**doc/BIBLIOTECA_PADRAO.md**](doc/BIBLIOTECA_PADRAO.md) | assinaturas dos 87 módulos |
| [**doc/INSTALACAO.md**](doc/INSTALACAO.md) | instalação passo a passo |
| [**doc/ANALISE_E_ROADMAP.md**](doc/ANALISE_E_ROADMAP.md) | estado técnico e o que falta |
| [**doc/ESTABILIDADE.md**](doc/ESTABILIDADE.md) | o que pode quebrar entre versões — e o teste que garante |
| [**CHANGELOG.md**](CHANGELOG.md) | o que mudou depois da 1.0.0 |
| [**CONTRIBUTING.md**](CONTRIBUTING.md) | como mandar o primeiro patch |
| [**exercicios/**](exercicios/) | 397 exercícios; do módulo 11 em diante, cada um com `.md` explicativo |
| [**examples/**](examples/) | 50 programas maiores |

### Os 397 exercícios

```bash
python3 exercicios/run_all.py        # todos
python3 exercicios/run_all.py 14     # só o módulo 14
```

Cada exercício **verifica o próprio resultado com `assert`**. Do módulo 11 em
diante, cada `.df` traz um `.md` ao lado — com o enunciado, o defeito que a
regra evita e o motivo de cada decisão. Há teste cobrando que nenhum fique
sem ele.

| Módulo | N | Tema |
|--------|---|------|
| 01 | 12 | fundamentos: tipos, operadores, precedência |
| 02 | 12 | controle de fluxo: condicionais e os quatro laços |
| 03 | 14 | coleções: clusters, fatiamento, vaults, busca |
| 04 | 10 | strings: métodos, regex, templates |
| 05 | 14 | ações: aridade, recursão, closures, lambdas, decoradores |
| 06 | 14 | blueprints: herança, traits, polimorfismo |
| 07 | 10 | erros: `monitor`, `handle` tipado, `guard`, `retry` |
| 08 | 12 | pipelines: `sift`/`morph`/`distill`, composição |
| 09 | 12 | módulos: `adopt`, Math, Analytics, IO, SQLite |
| 10 | 10 | avançado: async, threads, árvore binária, RPN |
| **11** | 6 | **tipos e checagem estática** |
| **12** | 6 | **records e enums** |
| **13** | 6 | **desestruturação, spread, compreensões, interpolação** |
| **14** | 6 | **pattern matching estrutural** |
| **15** | 6 | **streams e generators** |
| **16** | 6 | **módulos, testes, biblioteca publicável** |
| **17** | 6 | **tempo, sistema, processos, logging** |
| **18** | 6 | **serialização, arquivos, SQLite, HTTP** |
| **19** | 6 | **concorrência: async, threads, canais, retry** |
| **20** | 6 | **projetos finais: CLI, análise de dados, interpretador** |
| 21–34 | 84 | OOP avançado, Kiln, Vitrine, banco, testes, complexidade, binário |
| 35–49 | 90 | paralelismo, quadro, tipos, metaprogramação, FFI, compilador, ABI |
| **50** | 15 | **domínio e DDD: valor, agregado, evento, regra, unidade** |
| **51** | 15 | **programação reativa: sinal, derivado, efeito, observável** |
| **52** | 15 | **estruturas e ponteiros: layout binário, janela, bloco** |
| **53** | 15 | **regex avançado: grupos nomeados, explicação, risco** |
| **54** | 15 | **erros: as famílias, `defer`, `Resultado`, contratos** |
| **55** | 15 | **métodos mágicos: texto, ordem, coleção, acesso, reflexão** |
| **56** | 15 | **bots de Telegram: comandos, conversa, webhook, teste** |
| **57** | 15 | **Vitrine: layout, gráficos, cache, sessão, fragmento** |

---

## Desenvolvimento

```bash
pip install -e ".[dev]"

python3 -m pytest tests/ -q       # mais de 4500 testes
python3 exercicios/run_all.py     # 397 exercícios
```

Contexto para trabalhar no interpretador: [`CLAUDE.md`](CLAUDE.md).

### Arquitetura

```
arquivo.df → tokenize() → parse() → check_program() → Interpreter().run(ast)
             lexer.py     parser.py  typechecker.py   interpreter.py
```

| Arquivo | Responsabilidade | Linhas |
|---------|------------------|--------|
| `dataforge/tokens.py` | TokenType e as 81 palavras reservadas | 305 |
| `dataforge/lexer.py` | texto → tokens, INDENT/DEDENT, interpolação | 556 |
| `dataforge/parser.py` | recursivo descendente: tokens → AST | 1941 |
| `dataforge/ast_nodes.py` | nós da AST como dataclasses | 706 |
| `dataforge/interpreter.py` | interpretador de árvore: a semântica | 2703 |
| `dataforge/typechecker.py` | análise estática | 1193 |
| `dataforge/formatter.py` | `dataforge fmt` | 280 |
| `dataforge/linter.py` | `dataforge lint` | 394 |
| `dataforge/testrunner.py` | `dataforge test` | 194 |
| `dataforge/docgen.py` | `dataforge doc` | 218 |
| `dataforge/project.py` | `forge.toml` | 184 |
| `dataforge/builtins.py` | 228 funções globais | 1224 |
| `dataforge/stdlib/` | os 87 módulos, incluindo o Kiln, o Crucible e o Forge | 8200 |

---

## Estado do projeto

| Verificação | Resultado |
|-------------|-----------|
| Testes unitários | 1012 passando |
| Exercícios | 216/216 |
| Exemplos | 42/42 |
| Módulos da stdlib | 29/29 carregam |
| Pacotes do registro | 20 no registro, 4 escritos em DataForge com 46 testes |
| Análise estática sobre o repositório | 0 erros em 233 arquivos |
| Instalação via pip, curl e Docker | funciona |

### O que ainda não existe

Generics com restrição, exaustividade além de enum (o `match` já cobre
enum), depurador com breakpoint e VM de bytecode — hoje é interpretador
de árvore, e num laço quente isso se sente.
Detalhado em [`doc/ANALISE_E_ROADMAP.md`](doc/ANALISE_E_ROADMAP.md).

---

## Onde mais

| Onde | O quê |
|---|---|
| [dataforge-lang.vercel.app/docs](https://dataforge-lang.vercel.app/docs) | a documentação navegável, com busca |
| [dataforge-df/docs](https://github.com/dataforge-df/docs) | a mesma documentação em Markdown, para ler no GitHub ou clonar |
| [dataforge-df](https://github.com/dataforge-df) | a organização |
| [estevan5s/dataforge](https://hub.docker.com/r/estevan5s/dataforge) | a imagem Docker |

## Licença

MIT — veja [LICENSE](LICENSE).
