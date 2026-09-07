# Referência da linguagem DataForge

Documento normativo: gramática, palavras-chave, operadores, tipos e semântica.
Para aprender a linguagem, comece pelo [`TUTORIAL.md`](TUTORIAL.md).

Versão descrita: **DataForge 3.1**

---

## 1. Estrutura léxica

### 1.1 Codificação e linhas

Arquivos `.df` são UTF-8. O fim de linha encerra uma instrução; não existe `;`.

### 1.2 Comentários

```dataforge
// linha
# linha
/* bloco
   de várias linhas */
```

### 1.3 Indentação

- Blocos abrem com `:` e são delimitados por indentação.
- **Tabs são erro** (`SyncError`). Use espaços — 4 por nível, por convenção.
- Dentro de `(`, `[`, `{` a indentação é ignorada.
- Uma linha começando com `.` continua o encadeamento de métodos anterior.
- Uma linha começando com `>>` continua o pipeline anterior.

### 1.4 Identificadores

Começam com letra ou `_`, seguidos de letras, dígitos ou `_`. Sensíveis à caixa.

### 1.5 Literais

| Forma | Exemplos |
|-------|----------|
| Inteiro decimal | `42`, `1_000_000` |
| Inteiro hexadecimal | `0xFF`, `0Xff` |
| Inteiro octal | `0o755` |
| Inteiro binário | `0b1010` |
| Decimal | `3.14`, `0.5` |
| Texto | `"a"`, `'a'` |
| Texto multilinha | `"""..."""`, `'''...'''` |
| Booleano | `yes`, `no` |
| Nulo | `void` |
| Lista | `[1, 2, 3]` |
| Dicionário | `{"k": v}` |

Escapes em texto: `\n`, `\t`, `\r`, `\\`, `\'`, `\"`, `\0`.

### 1.6 Palavras reservadas (78)

```
action    adopt     and       as        assert    async     await     bigger
bigger_eq blueprint cast      channel   cycle     default   defer     delete
distill   emit      ensure    extends   forge     frame     from      given
guard     halt      handle    in        inspect   is        isnt      lambda
mark      match     monitor   morph     no        not       observe   or
orif      otherwise out       parallel  perform   persist   point     predict
propagate pulse     recover   relay     retry     root      self      shadow
sift      skip      smaller   smaller_eq spawn    static    steady    step
stream    thread    to        train     trait     trigger   typeof    using
validate  void      wait      with      yes       yield
```

`cluster`, `vault` e `range` **não** são reservadas: são funções embutidas e
podem ser usadas como nomes.

Usar uma delas como nome produz um `ParseError` explicando qual é a palavra.

---

## 2. Operadores

### 2.1 Tabela completa

| Operador | Categoria | Significado |
|----------|-----------|-------------|
| `:=` | atribuição | atribui/declara |
| `+=` `-=` `*=` `/=` `%=` | atribuição | composta |
| `+` `-` `*` `/` `%` | aritmética | soma, subtração, produto, divisão, resto |
| `**` | aritmética | potência (associa à direita) |
| `~/` | aritmética | divisão inteira (**preferido**) |
| `//` | aritmética | divisão inteira (ambíguo — ver 2.3) |
| `is` / `==` | comparação | igual |
| `isnt` / `!=` | comparação | diferente |
| `bigger` / `>` | comparação | maior |
| `smaller` / `<` | comparação | menor |
| `bigger_eq` / `>=` | comparação | maior ou igual |
| `smaller_eq` / `<=` | comparação | menor ou igual |
| `and` `or` `not` | lógica | conjunção, disjunção, negação |
| `>>` | pipeline | encadeia `sift` / `morph` / `distill` |
| `.` | acesso | membro |
| `[]` | acesso | índice ou fatia |
| `()` | chamada | invocação |
| `->` | tipo | tipo de retorno de uma ação |
| `=>` | lambda | corpo de lambda (alternativa a `:`) |
| `@` | metadado | nome do decorador após `mark` |

### 2.2 Precedência

Da mais alta para a mais baixa:

| Nível | Operadores | Associatividade |
|-------|-----------|-----------------|
| 1 | `()` `[]` `.` | esquerda |
| 2 | `**` | direita |
| 3 | `-` `+` `not` (unários) | direita |
| 4 | `*` `/` `%` `~/` `//` | esquerda |
| 5 | `+` `-` | esquerda |
| 6 | comparações | encadeável |
| 7 | `not` | direita |
| 8 | `and` | esquerda |
| 9 | `or` | esquerda |
| 10 | `>>` | esquerda |

Consequências:

```dataforge
2 ** 3 ** 2    // 512, não 64
-2 ** 2        // -4, não 4
2 + 3 * 4      // 14
```

### 2.3 A ambiguidade de `//`

`//` abre comentário **e** é divisão inteira. O lexer decide pelo contexto:

É divisão inteira quando **todas** valerem:
1. o token anterior pode terminar uma expressão (valor, `)`, `]`, `}`);
2. há no máximo 2 espaços antes do `//`;
3. o que vem depois começa como operando (dígito, `(`, `-`, `_` ou letra);
4. o restante da linha não é prosa (duas palavras seguidas sem operador = prosa).

```dataforge
x := 7 // 2                     // divisão → 3
x := 3  // marcar como caminho  // comentário
```

**Recomendação: use `~/`.** É inequívoco e não depende de heurística.

### 2.4 Comparações encadeadas

```dataforge
nota := 7.5
out 0 <= nota <= 10        // equivale a (0 <= nota) and (nota <= 10)
out 1 smaller 5 smaller 10
```

O termo do meio é avaliado uma única vez.

---

## 3. Tipos

### 3.1 Tipos internos

| Nome DataForge | Representação | Literal |
|----------------|---------------|---------|
| `Integer` | inteiro de precisão arbitrária | `42` |
| `Float` | ponto flutuante 64 bits | `3.14` |
| `String` | texto imutável | `"a"` |
| `Boolean` | `yes` / `no` | `yes` |
| `Void` | ausência de valor | `void` |
| `Cluster` | lista mutável ordenada | `[1, 2]` |
| `Vault` | dicionário chave→valor | `{"k": 1}` |
| `Action` | ação (função) | `action f(): ...` |
| `Blueprint` | classe | `blueprint P: ...` |
| *nome do blueprint* | instância | `spawn P()` |

`typeof(x)` devolve esses nomes como texto.

### 3.2 Anotações de tipo

Opcionais e **verificadas em tempo de execução**:

```dataforge
idade: Integer := 30                       // variável
action f(n: Integer, s: String) -> Float:  // parâmetros e retorno
    yield n * 1.0
```

Nomes aceitos, com sinônimos:

| Canônico | Sinônimos aceitos |
|----------|-------------------|
| `Integer` | `integer`, `int` |
| `Float` | `float` |
| `Number` | `number` (aceita `Integer` ou `Float`) |
| `String` | `string`, `str`, `text` |
| `Boolean` | `boolean`, `bool` |
| `Cluster` | `cluster`, `list`, `array` |
| `Vault` | `vault`, `dict`, `map` |
| `Void` | `void`, `none` |
| `Action` | `action`, `function` |
| `Any` | `any` (desliga a checagem) |

Um nome não listado é tratado como nome de blueprint, e a checagem percorre a
cadeia de herança.

Regra de conveniência: **um `Integer` é aceito onde se espera `Float`**.

### 3.3 Conversão

Formas disponíveis (`valor` e `x` são espaços reservados):

```
cast valor as Integer        // Integer, Float, String, Boolean, Cluster
str(x)  int(x)  float(x)  bool(x)  cluster(x)  vault(x)
```

---

## 4. Declarações

### 4.1 Variável

```ebnf
identificador [":" tipo] ":=" expressão
```

`:=` cria no escopo atual se o nome não existir em nenhum escopo visível;
caso contrário, atualiza onde ele foi encontrado.

### 4.2 Constante

```ebnf
steady NOME := valor
```

Reatribuir ou apagar dispara `RuntimeError_`.

### 4.3 Shadow

```ebnf
shadow nome := valor
```

Cria uma variável **estritamente local**, mesmo que o nome exista fora.

### 4.4 Estático

```ebnf
static nome := valor
```

Dentro de um `blueprint`, cria um membro compartilhado por todas as instâncias.

---

## 5. Controle de fluxo

### 5.1 Condicional

```
given <condição> ":" bloco
{ orif <condição> ":" bloco }
[ otherwise ":" bloco ]
```

### 5.2 Seleção múltipla

```
match <expressão> ":"
    { point <valor> ":" bloco }
    [ default ":" bloco ]
```

Compara por igualdade; não há fall-through.

### 5.3 Laços

```
cycle <var> from <início> to <fim> [ step <passo> ] ":" bloco
cycle <var> in <coleção> ":" bloco
persist <condição> ":" bloco
perform ":" bloco persist <condição>
```

O `to` de `cycle from` é **inclusivo**. O `step` padrão é `1` e pode ser negativo.

### 5.4 Interrupção

| Palavra | Efeito |
|---------|--------|
| `halt` | sai do laço |
| `skip` | vai para a próxima iteração |

`halt` e `skip` atravessam blocos `monitor` sem serem capturados: são controle de
fluxo, não erros.

---

## 6. Ações

### 6.1 Declaração

```
[ mark "@" decorador [ "(" args ")" ] ]
[ async ] action nome "(" [ params ] ")" [ "->" tipo ] ":" bloco
```

Um parâmetro é `nome [":" tipo] [":=" padrão]`.

### 6.2 Retorno

`yield <expressão>` devolve o valor e encerra a ação. Sem `yield`, devolve `void`.

`yield` atravessa `monitor` sem ser capturado.

### 6.3 Aridade

Verificada na chamada. Argumentos faltando, sobrando ou com nome desconhecido
disparam `TypeError_` com a mensagem apontando o problema.

### 6.4 Lambdas

```
lambda [ params ] ( ":" | "=>" ) <expressão>
lambda "(" params-tipados ")" ( ":" | "=>" ) <expressão>
```

Anotações de tipo em lambda exigem parênteses (sem eles, `:` inicia o corpo).

```dataforge
lambda x: x * 2
lambda a, b => a + b
lambda: 42
lambda (n: Integer): n + 1
```

### 6.5 Decoradores

```ebnf
mark @envolver
action alvo(x):
    yield x
```

O decorador recebe a ação e devolve a substituta. Com argumentos
(`mark @cache(60)`), o decorador é chamado primeiro com os argumentos e o
resultado recebe a ação.

Vários `mark` empilham; o mais próximo da ação é aplicado primeiro.

### 6.6 defer

```ebnf
defer:
    bloco
```

Agenda o bloco para rodar na saída da ação, em ordem LIFO. Erros dentro de um
bloco `defer` são descartados.

### 6.7 Limite de recursão

O interpretador aborta em **1000 quadros** com `StackOverflowError_`, nomeando a
ação. Recursões legítimas de até ~900 níveis funcionam.

---

## 7. Blueprints

### 7.1 Declaração

```
blueprint Nome [ "(" params ")" ] [ extends Pai {"," Pai} ] [ with Trait {"," Trait} ] ":"
    corpo
```

### 7.2 Construção

Duas formas, que podem coexistir:

**Parâmetros no cabeçalho** — viram campos automaticamente:

```dataforge
blueprint Ponto(x, y):
    action mostrar():
        yield self.x
```

**Método `setup`** — para campos derivados:

```dataforge
blueprint Lista:
    action setup():
        self.itens := []
```

Se ambos existirem, os parâmetros são atribuídos primeiro e depois `setup` roda.
`initiate` é aceito como sinônimo de `setup`.

Instanciar: `spawn Nome(args)` ou `forge Nome(args)`. Chamar o blueprint
diretamente (`Nome(args)`) também instancia.

### 7.3 self e root

- `self` (ou `this`) é a instância atual.
- `root` resolve métodos do primeiro blueprint pai.

### 7.4 Traits

```ebnf
trait Nome:
    action assinatura()
```

Métodos do trait só são copiados para o blueprint se ele **não** definir o
próprio. Não há verificação de que o contrato foi cumprido — use
`has_method(x, "nome")` quando isso importar.

### 7.5 Métodos especiais

| Método | Chamado por |
|--------|-------------|
| `setup` / `initiate` | `spawn` |
| `toString` | `out`, `str()` |
| `add` `sub` `mul` `div` `mod` `pow` `floordiv` | `+` `-` `*` `/` `%` `**` `~/` |

### 7.6 Resolução de nomes

A busca em uma instância segue: campos → métodos do blueprint → estáticos →
pais (busca em profundidade, da esquerda para a direita).

---

## 8. Erros

### 8.1 Blocos

```
monitor ":" bloco
[ handle [ Tipo as ] nome ":" bloco ]
[ ensure ":" bloco ]
```

- **Sem `handle`**, o erro **não é capturado** — só o `ensure` roda antes de o
  erro subir.
- Com `handle Tipo as e`, só erros daquele tipo são capturados; os demais sobem.
- `Error`, `Exception` e `Any` capturam qualquer erro.

### 8.2 Objeto de erro

O nome ligado pelo `handle` expõe:

| Campo | Conteúdo |
|-------|----------|
| `.type` | nome do tipo, ex. `"RuntimeError"` |
| `.message` | a mensagem |
| `.line`, `.column` | posição de origem |

Ele se comporta como texto ao ser concatenado ou comparado com uma `String`.

### 8.3 Hierarquia de erros

| Tipo | Quando ocorre |
|------|---------------|
| `SyncError` | indentação inconsistente ou tab |
| `LexError` | caractere inválido, texto não terminado |
| `ParseError` | sintaxe inválida |
| `RuntimeError_` | divisão por zero, `assert` falso, operação inválida |
| `TypeError_` | tipo incompatível, aridade errada |
| `NameError_` | nome não definido |
| `IndexError_` | índice ou chave fora de alcance |
| `ImportError_` | módulo não encontrado |
| `TriggerError` | lançado por `trigger`, `guard`, `validate` |
| `StackOverflowError_` | recursão além de 1000 quadros |

### 8.4 Lançar e propagar

| Forma | Efeito |
|-------|--------|
| `trigger <expr>` | lança `TriggerError` com a mensagem |
| `guard <cond>, <msg>` | lança se a condição for falsa |
| `guard <cond> otherwise: bloco` | roda o bloco e **sai da ação** |
| `validate <expr>, <msg>` | lança se o valor for falso |
| `validate <expr> otherwise: bloco` | roda o bloco e sai da ação |
| `propagate <expr>` | relança |
| `assert <cond>, <msg>` | lança `RuntimeError_` se falso |

### 8.5 retry

```
retry <n> ":" bloco [ ( handle | recover ) [nome] ":" bloco ]
```

Tenta o bloco até `n` vezes. Se todas falharem, o handler roda com o último erro.

---

## 9. Pipelines

```
<expressão> { ">>" <operação> }
```

| Operação | Forma inline | Forma por referência |
|----------|--------------|----------------------|
| `sift` | `sift p: condição` | `sift nome_da_ação` |
| `morph` | `morph p: expressão` | `morph nome_da_ação` |
| `distill` | `distill acc, v: expr [inicial]` | `distill nome inicial` |

```dataforge
dados := [50, 120, 300, 90]
out dados
    >> sift v: v bigger 100
    >> morph v: v * 1.1
    >> distill acc, v: acc + v 0
```

Sem valor inicial, `distill` usa o primeiro elemento como acumulador.

---

## 10. Módulos

```
adopt <Nome>[.<Sub>] [ as <alias> ]
relay <nome> {"," <nome>}
```

Resolução, nesta ordem:
1. módulo já carregado (cache);
2. biblioteca padrão (`Arcane.*` e os nomes curtos);
3. arquivo `<caminho>.df` ou `<caminho>/main.df` relativo ao diretório atual.

Não encontrando, dispara `ImportError_` listando os módulos disponíveis.

`relay` documenta o que o módulo exporta. Na implementação atual, todas as
variáveis de nível superior do arquivo ficam acessíveis pelo alias.

---

## 11. Concorrência

| Construção | Semântica |
|------------|-----------|
| `async action f():` | marca a ação como assíncrona |
| `await <expr>` | resolve a corrotina |
| `thread: bloco` | roda o bloco em uma thread daemon |
| `parallel: bloco` | roda **cada instrução** do bloco em uma thread, com join de 30 s |
| `channel nome` | cria uma fila FIFO com trava |
| `nome.send(v)` / `nome.receive()` | escreve / lê (devolve `void` se vazio) |
| `wait <ms>` | dorme pelo número de milissegundos |
| `stream <expr>` | cria um stream a partir de uma coleção |
| `observe v in fonte: bloco` | itera a fonte; aceita `halt` e `skip` |
| `pulse <evento>[, <dado>]` | emite um evento |

> **Limitação:** não há sincronização automática de variáveis compartilhadas
> entre threads. `channel` é a via segura.

---

## 12. Gramática (EBNF)

```ebnf
programa       = { instrução } ;

instrução      = decl_var | decl_steady | decl_shadow | decl_static
               | decl_ação | decl_blueprint | decl_trait
               | adopt | relay
               | condicional | seleção | laço
               | bloco_erro | concorrência
               | out | yield | halt | skip | trigger | assert
               | delete | wait | inspect | expressão ;

decl_var       = identificador [ ":" tipo ] ":=" expressão
               | alvo ( "+=" | "-=" | "*=" | "/=" | "%=" ) expressão ;
decl_steady    = "steady" identificador ":=" expressão ;
decl_shadow    = "shadow" identificador ":=" expressão ;
decl_static    = "static" identificador ":=" expressão ;

decl_ação      = { "mark" "@" identificador [ "(" args ")" ] }
                 [ "async" ] "action" identificador
                 "(" [ params ] ")" [ "->" tipo ] ":" bloco ;
params         = param { "," param } ;
param          = identificador [ ":" tipo ] [ ":=" expressão ] ;

decl_blueprint = "blueprint" identificador [ "(" nomes ")" ]
                 [ "extends" nomes ] [ "with" nomes ] ":" bloco ;
decl_trait     = "trait" identificador ":" bloco ;

adopt          = "adopt" caminho [ "as" identificador ] ;
relay          = "relay" nomes ;

condicional    = "given" expressão ":" bloco
                 { "orif" expressão ":" bloco }
                 [ "otherwise" ":" bloco ] ;
seleção        = "match" expressão ":" INDENT
                 { "point" expressão ":" bloco }
                 [ "default" ":" bloco ] DEDENT ;

laço           = "cycle" identificador "from" expressão "to" expressão
                     [ "step" expressão ] ":" bloco
               | "cycle" identificador "in" expressão ":" bloco
               | "persist" expressão ":" bloco
               | "perform" ":" bloco "persist" expressão ;

bloco_erro     = "monitor" ":" bloco
                 [ "handle" [ identificador "as" ] identificador ":" bloco ]
                 [ "ensure" ":" bloco ]
               | "retry" expressão ":" bloco
                 [ ( "handle" | "recover" ) [ identificador ] ":" bloco ]
               | "guard" expressão ( [ "," expressão ] | "otherwise" ":" bloco )
               | "validate" expressão ( [ "," expressão ] | "otherwise" ":" bloco )
               | "propagate" [ expressão ]
               | "defer" ":" bloco ;

concorrência   = "thread" ":" bloco
               | "parallel" ":" bloco
               | "channel" identificador
               | "observe" identificador "in" expressão ":" bloco
               | "pulse" expressão [ "," expressão ] ;

expressão      = pipeline ;
pipeline       = ou { ">>" op_pipeline } ;
op_pipeline    = "sift"    ( identificador ":" ou | identificador )
               | "morph"   ( identificador ":" ou | identificador )
               | "distill" ( identificador [ "," ] identificador ":" ou [ ou ]
                           | identificador ou ) ;
ou             = e { "or" e } ;
e              = negação { "and" negação } ;
negação        = [ "not" ] comparação ;
comparação     = adição { op_comp adição } ;
adição         = multiplicação { ( "+" | "-" ) multiplicação } ;
multiplicação  = unário { ( "*" | "/" | "%" | "~/" | "//" ) unário } ;
unário         = ( "+" | "-" | "not" ) unário | potência ;
potência       = posfixo [ "**" unário ] ;
posfixo        = primário { "." nome | "[" índice "]" | "(" args ")" } ;
índice         = expressão | [expressão] ":" [expressão] [ ":" [expressão] ] ;

primário       = literal | identificador | "(" expressão ")"
               | lista | dicionário | lambda
               | "self" | "root"
               | ( "spawn" | "forge" ) posfixo
               | "typeof" unário
               | "cast" unário "as" identificador
               | "await" expressão
               | "stream" ou
               | "in" [ texto ]
               | "frame" primário
               | "train" posfixo "using" expressão
               | "predict" posfixo "using" expressão ;

lambda         = "lambda" [ params_lambda ] ( ":" | "=>" ) ou ;
lista          = "[" [ expressão { "," expressão } ] "]" ;
dicionário     = "{" [ par { "," par } ] "}" ;
par            = expressão ":" expressão ;

bloco          = NEWLINE INDENT { instrução } DEDENT ;
```

---

## 13. Funções embutidas

Disponíveis sem `adopt`. São 225 nomes, agrupados por tema:

**Tipos e conversão** — `len` `type` `str` `int` `float` `bool` `cluster` `vault`
`range` `cast`

**Texto** — `join` `split` `strip` `lstrip` `rstrip` `upper` `lower` `title`
`capitalize` `swapcase` `center` `ljust` `rjust` `zfill` `replace` `startswith`
`endswith` `find` `rfind` `index_of` `last_index_of` `char_at` `substring`
`isalpha` `isdigit` `isalnum` `isspace` `isupper` `islower` `istitle`
`isnumeric` `isascii` `repeat` `reverse_str` `trim` `pad_start` `pad_end`
`includes` `concat` `char` `ord` `encode` `decode` `format` `count_str`
`expandtabs` `partition` `rpartition` `splitlines` `removeprefix` `removesuffix`
`words` `lines` `template`

**Regex** — `regex_match` `regex_search` `regex_findall` `regex_sub`
`regex_split` `regex_test` `regex_count` `regex_extract`

**Matemática** — `abs` `min` `max` `sum` `round` `floor` `ceil` `sqrt` `cbrt`
`pow` `log` `log2` `log10` `exp` `sin` `cos` `tan` `asin` `acos` `atan` `atan2`
`degrees` `radians` `hypot` `factorial` `gcd` `lcm` `comb` `perm` `clamp` `lerp`
`sign` `is_nan` `is_inf` `is_finite`

**Estatística** — `mean` `median` `stdev` `variance` `mode` `percentile`
`random` `randint` `choice` `shuffle` `sample`

**Coleções** — `sorted` `reversed` `enumerate` `zip` `append` `pop` `insert`
`remove` `keys` `values` `items` `contains` `flatten` `unique` `count` `index`
`slice` `first` `last` `take` `drop` `chunk` `interleave` `rotate` `unzip`
`merge_dicts` `invert_dict` `pick` `omit` `deep_copy` `frequencies`

**Funcional** — `map` `filter` `reduce` `compose` `pipe_fn` `partial` `curry`
`memoize` `once` `tap` `identity` `constantly` `complement` `every` `some`
`none_of` `find_first` `find_last` `flat_map` `scan` `zip_with` `chain`
`product` `permutations` `combinations` `repeat_val` `accumulate`

**Sistema** — `time` `sleep` `timestamp` `exists` `freeze` `thaw` `hash` `id`
`uuid` `to_json` `from_json` `hash_md5` `hash_sha256` `base64_encode`
`base64_decode` `env_var`

**Predicados** — `is_empty` `is_string` `is_number` `is_integer` `is_float`
`is_boolean` `is_list` `is_dict` `is_void` `is_callable` `coalesce` `default`
`default_val` `assert_type` `validate` `instanceof`

**Introspecção** — `has_method` `has_field` `get_fields` `get_methods` `get_mro`
`get_parent` `class_name`

**Constantes globais** — `PI` `E` `TAU` `INF` `NAN` `MAX_INT` `MIN_INT`
`NEWLINE` `TAB` `EMPTY`

---

## 14. Semântica de valores

- **Inteiros** têm precisão arbitrária.
- **Textos** são imutáveis; métodos devolvem cópias.
- **Clusters e vaults** são mutáveis e passados por referência.
- `/` sempre devolve `Float`; `~/` devolve `Integer` para operandos inteiros.
- Divisão por zero (`/`, `~/`) dispara `RuntimeError_`.
- `+` com um operando texto converte o outro para texto.
- Índices negativos contam a partir do fim.
- Em contexto booleano: `void`, `no`, `0`, `""`, `[]` e `{}` são falsos.

---

## 15. Notas de implementação

- Interpretador de árvore (tree-walking), sem bytecode.
- Python 3.10+, sem dependências externas.
- Ordem: lexer (`lexer.py`) → parser recursivo descendente (`parser.py`) →
  interpretador (`interpreter.py`).
- Escopos formam uma cadeia (`environment.py`); a busca sobe até o global.
- Não há verificação estática antes da execução: `dataforge check` valida apenas
  a sintaxe.
