# DataForge — análise técnica e o que falta

Auditoria completa do repositório, feita rodando o código, não lendo apenas.
Data da auditoria: 2026-09-06. Versão analisada: 3.0.0 → corrigida para 3.1.0.

---

## 1. Veredito: é uma linguagem de programação?

**Sim, sem ressalva.** DataForge tem os cinco componentes que definem uma
implementação de linguagem, todos escritos do zero e todos funcionando:

| Componente | Arquivo | Linhas | Estado |
|------------|---------|--------|--------|
| Lexer com INDENT/DEDENT | `lexer.py` | 473 | completo |
| Parser recursivo descendente | `parser.py` | 1.381 | completo |
| AST tipada (dataclasses) | `ast_nodes.py` | 503 | completo |
| Interpretador de árvore | `interpreter.py` | 1.658 | completo |
| Cadeia de escopos | `environment.py` | 91 | completo |
| Funções embutidas | `builtins.py` | 1.224 | 225 funções |
| Biblioteca padrão | `stdlib/` | 5.486 | 13 módulos, 454 símbolos |
| REPL | `repl.py` | 204 | funcional |
| CLI | `cli.py` | 749 | 8 comandos, 6 templates |

Não é um wrapper sobre `eval` do Python: cada construção tem seu nó de AST e sua
regra de avaliação. A prova prática está em `exercicios/`, onde um dos exercícios
é um **interpretador de notação polonesa reversa escrito em DataForge** — a
linguagem é expressiva o bastante para implementar outra.

### O que a torna avançada

- Sistema de tipos opcional com checagem em tempo de execução, incluindo
  parâmetros e retorno.
- Herança múltipla com resolução em profundidade, traits, sobrecarga de
  operadores e introspecção (`get_mro`, `has_method`, `get_fields`).
- Tratamento de erros com `handle` tipado, `retry`, `guard`, `validate`,
  `propagate`, `defer` (LIFO na saída do escopo) e `ensure`.
- Pipelines como sintaxe de primeira classe.
- Closures, ações de alta ordem, lambdas em três grafias, decoradores.
- Concorrência: `async/await`, threads, canais com trava, `parallel`, streams.
- Biblioteca padrão com servidor HTTP real (testado com requisições) e SQLite.

### O que ainda a separa de uma linguagem madura

Sem análise estática, sem gerenciador de pacotes, sem compilação para bytecode e
sem verificação de contrato de traits. Detalhes na seção 5.

---

## 2. Bugs encontrados e corrigidos

Todos foram reproduzidos com um `.df` mínimo, corrigidos e cobertos por teste de
regressão em `tests/test_regressoes.py`.

### Críticos — corrompiam a semântica

**1. `monitor/handle` capturava `yield`, `halt` e `skip`**

`HaltSignal`, `SkipSignal` e `YieldSignal` derivavam de `Exception`, e o
`except Exception` do `exec_MonitorBlock` os engolia. Consequência: um `yield`
dentro de um `monitor` nunca retornava — caía no `handle` como se fosse erro.

```dataforge
action f():
    monitor:
        yield 42          // devolvia void e rodava o handle
    handle e:
        out "erro"
```

**Correção:** os três passaram a derivar de `ControlSignal(BaseException)`.
Controle de fluxo deixou de ser confundível com erro.

**2. `monitor` sem `handle` engolia o erro silenciosamente**

Um `monitor:` seguido apenas de `ensure:` capturava tudo e seguia em frente. Erro
sumia sem rastro.

**Correção:** sem `handle`, o erro é relançado depois do `ensure`.

**3. `2 ** 3 ** 2` dava 64**

`parse_power` era não-associativo e ficava abaixo da multiplicação, então
`-2 ** 2` também dava `4` em vez de `-4`.

**Correção:** `**` associa à direita e liga mais forte que o unário.

**4. Aridade nunca era verificada**

`f(1)` numa ação de dois parâmetros ligava o segundo a `void`, e o erro só
aparecia depois, como `unsupported operand type(s) for +`. Argumentos a mais eram
descartados em silêncio.

**Correção:** `_check_arity` reporta o que falta, o que sobra e nomes
desconhecidos, no ponto da chamada.

**5. Recursão infinita derrubava o interpretador**

`RecursionError` do Python vazava como `Internal Error: maximum recursion depth
exceeded`, sem indicar a ação culpada.

**Correção:** contador de profundidade com limite de 1000 quadros e
`StackOverflowError_` nomeando a ação. O limite do Python foi elevado para 20.000
para que a checagem própria dispare antes.

**6. `adopt` de módulo inexistente criava um dicionário vazio**

Um erro de digitação em `adopt Arcane.Mathh` passava despercebido; o erro
aparecia páginas depois como `NameError`.

**Correção:** `ImportError_` listando os módulos disponíveis.

**7. `Arcane.Cortex` não carregava**

`cls._softmax` dentro de um `@staticmethod` — `cls` não existe ali. O módulo
inteiro quebrava ao ser importado.

**Correção:** referência pela classe. Todos os 30 nomes de módulo carregam.

**8. `setup` era ignorado quando havia parâmetros de construtor**

Um blueprint com `blueprint Pedido(cliente)` **e** um `action setup` nunca
executava o `setup`, então campos como `self.itens := []` nunca existiam.

**Correção:** os parâmetros são atribuídos e depois o `setup` roda.

**9. `str()` não respeitava `toString()`**

`out obj` chamava `toString`, mas `str(obj)` devolvia
`<Blueprint instance>`. As duas formas discordavam.

**Correção:** `str()` delega ao formatador do interpretador.

**10. `defer` não rodava quando a ação saía por erro**

O `_run_deferred` só era chamado no caminho de sucesso e no `yield`. Se a ação
falhasse, a limpeza agendada nunca acontecia — exatamente o cenário para o qual
`defer` existe. Um arquivo temporário ficava para trás no disco.

**Correção:** o `_run_deferred` passou para o `finally`, em `_call_action` e em
`_call_func`.

**11. Erros do Python vazavam como "Internal Error"**

`cycle x in 5`, `x[0]` sobre um inteiro e `observe` sobre um número produziam
mensagens Python cruas.

**Correção:** viram `TypeError_` com mensagem em vocabulário DataForge.

### Sérios — travavam uso legítimo

**12. `//` interpretado errado**

`lab[r][c] := 3  // marcar como caminho` era lido como divisão inteira, porque a
heurística só olhava o primeiro caractere depois de `//`. Um exemplo do próprio
repositório (`24_games_simulations.df`) falhava por isso.

**Correção:** heurística mais rigorosa (analisa se o resto da linha é prosa) e,
principalmente, o operador **`~/`**, inequívoco.

**13. Sete palavras reservadas sem uso**

`each`, `link`, `unlink`, `listen`, `claim`, `release` e `abstract` estavam em
`KEYWORDS` mas o parser nunca as consumia: só impediam o usuário de usá-las como
nome, sem entregar recurso nenhum.

**Correção:** removidas de `KEYWORDS` (os `TokenType` ficaram para uso futuro).

**14. `cluster`, `vault` e `range` eram funções impossíveis de chamar**

Estavam registradas em `builtins.py` **e** em `KEYWORDS`. `cluster([1,2])` era
erro de sintaxe.

**Correção:** removidas de `KEYWORDS`. As três funcionam.

**15. `pip install .` falhava**

`setup.py` apontava para `public/DataForge.png`, caminho inexistente. A
instalação abortava no build do wheel.

**Correção:** migração para `pyproject.toml`, sem `data_files` quebrado.

**16. `pytest` não coletava nada**

`tests/test_dataforge.py` chamava `sys.exit()` no nível do módulo; o pytest
abortava com `INTERNALERROR`. Além disso, a função auxiliar `test()` e a classe
`TestResults` eram coletadas como testes e falhavam por fixture ausente.

**Correção:** `sys.exit` sob `if __name__ == "__main__"`, auxiliares renomeadas
para `verificar()` e `Resultados`, e um `test_suite_legada()` expõe o resultado
ao pytest. Funciona nas duas formas.

**17. Todos os templates de `dataforge new` geravam código inválido**

Os seis templates usavam sintaxe que a linguagem não tem: `adopt X from "Y"`,
lambdas `=>` sem `lambda`, `end` para fechar blocos, `show()`, `isnot`,
`to_number()`, `push()`. Nenhum passava nem no `dataforge check`.

**Correção:** os seis foram reescritos em sintaxe real e verificados — os oito
arquivos `.df` gerados passam no `check`, e os executáveis rodam. O servidor
HTTP do template `api` foi testado com requisições reais (GET, POST, 404).

**18. `Text.render` só aceitava `{{chave}}`**

A documentação e o uso natural pediam `{chave}`.

**Correção:** aceita as duas formas.

**19. `Analytics.group_by` exigia uma função**

Agrupar por campo — o caso comum — obrigava a escrever uma lambda.

**Correção:** aceita também o nome do campo como texto.

**20. `Runtime_` — nome inexistente**

`_call_func` referenciava `Runtime_(...)`, que não existe. Qualquer valor não
chamável num pipeline geraria `NameError` do Python em vez de erro da linguagem.

**Correção:** `TypeError_` com mensagem adequada.

**21. `eval_BinaryOp` devolvia `None` em silêncio**

Um operador desconhecido caía fora do `if/elif` e a função devolvia `None`.

**Correção:** `RuntimeError_` explícito.

---

## 3. Recursos adicionados

Além das correções, a linguagem ganhou o que faltava para escrever código
idiomático sem contorcionismo:

| Recurso | Sintaxe | Por que |
|---------|---------|---------|
| Divisão inteira inequívoca | `a ~/ b` | remove a ambiguidade com comentário |
| Fatiamento | `l[1:3]`, `l[::2]`, `l[::-1]` | não existia; só índice simples |
| Comparação por símbolo | `<` `>` `<=` `>=` | antes só `smaller`/`bigger` |
| Comparação encadeada | `0 <= n <= 10` | evita repetir o termo do meio |
| Atribuição composta | `+=` `-=` `*=` `/=` `%=` | `x := x + 1` em todo lugar |
| Lambdas | `lambda x: e`, `lambda a, b => e` | não havia função anônima |
| Anotação de tipo em variável | `n: Integer := 5` | documentada, não implementada |
| Parâmetro e retorno tipados | `action f(n: Integer) -> Float:` | idem |
| Decoradores funcionais | `mark @nome` | o parser lia e descartava |
| Chamada encadeada | `f(1)(2)` | só era possível em identificador |
| `handle` tipado | `handle RuntimeError as e:` | documentado, não implementado |
| Objeto de erro | `e.type`, `e.message`, `e.line` | antes o erro virava só texto |
| Pipeline multilinha | linha iniciada por `>>` | quebrava a expressão |
| Unário `+` | `+5` | assimetria com `-5` |

---

## 4. Estado verificado

Comandos e resultados desta auditoria:

| Verificação | Comando | Resultado |
|-------------|---------|-----------|
| Testes unitários | `python3 -m pytest tests/ -q` | **77 passando** |
| Exercícios | `python3 exercicios/run_all.py` | **120/120** |
| Exemplos | `examples/*.df` | **42/42** |
| Blocos de documentação | executados um a um | **93/94** (o restante é lista de assinaturas) |
| Templates de projeto | `dataforge check` em cada `.df` gerado | **8/8** |
| Módulos da stdlib | import de todos | **30/30** |
| Instalação | `pip install .` em venv limpo | **funciona** |
| Servidor HTTP | GET, POST, GET por id, 404 | **funciona** |

### Os 120 exercícios

Cada um traz enunciado comentado e verifica o próprio resultado com `assert`.

| Módulo | Exercícios | Cobre |
|--------|-----------|-------|
| 01 fundamentos | 12 | tipos, operadores, precedência, conversão, anotações |
| 02 controle de fluxo | 12 | `given`, `match`, os quatro laços, `halt`/`skip`, `guard` |
| 03 coleções | 14 | clusters, fatiamento, vaults, matrizes, busca, ordenação |
| 04 strings | 10 | métodos, regex, templates, palíndromo, cifra de César |
| 05 ações | 14 | padrões, nomeados, tipos, aridade, recursão, closures, lambdas, decoradores, `defer` |
| 06 blueprints | 14 | construtores, herança, `root`, traits, polimorfismo, estáticos, operadores, padrões de projeto |
| 07 erros | 10 | `monitor`/`handle`/`ensure`, tipado, `guard`, `retry`, `propagate` |
| 08 pipelines | 12 | `sift`/`morph`/`distill`, composição, currying, streams |
| 09 módulos | 12 | `adopt` local e da stdlib, Math, Analytics, IO, JSON, SQLite, Text, Test |
| 10 avançado | 10 | async, threads, canais, `parallel`, lista ligada, árvore binária, máquina de estados, interpretador RPN |

---

## 5. O que falta para a linguagem estar completa

Em ordem de impacto. As três primeiras são o que separa DataForge de uma
linguagem que dá para usar em produção.

### Prioridade alta

**1. Análise estática (`dataforge check` de verdade)**

Hoje o `check` só valida sintaxe. Um nome inexistente, uma aridade errada ou um
tipo incompatível só aparecem quando aquela linha executa. Falta um passe sobre a
AST que verifique, antes de rodar: nomes não definidos, aridade das chamadas a
ações conhecidas, tipos nas anotações declaradas, `yield` fora de ação, e código
inalcançável depois de `yield`.

Isso é o que mais custa ao usuário hoje: um erro de digitação num ramo raro do
programa só aparece em produção.

**2. Rastreamento de pilha nos erros**

O erro atual dá linha e coluna do ponto de falha, mas não o caminho de chamadas.
Numa recursão ou numa cadeia de ações, saber apenas "linha 47" não localiza a
origem. Falta empilhar os quadros e imprimir algo como:

```
TriggerError [linha 47]: saldo insuficiente
  em sacar()        linha 47
  em processar()    linha 88
  em main           linha 120
```

**3. Sistema de módulos com escopo real**

`relay` hoje é decorativo: todas as variáveis de topo de um arquivo importado
ficam visíveis, exportadas ou não. Falta respeitar o `relay`, permitir import
seletivo (`adopt Arcane.Math.{sqrt, floor}`), resolver caminhos relativos ao
arquivo importador (e não ao diretório de trabalho) e detectar import circular.

### Prioridade média

**4. Açúcares que já se sente falta**

Ao escrever os 120 exercícios, estes foram os que fizeram falta:

| Falta | Sintaxe sugerida |
|-------|------------------|
| Compreensão de lista | `[n * 2 cycle n in lista given n bigger 0]` |
| Desestruturação | `a, b := [1, 2]` e `nome, idade := pessoa` |
| `cycle` com índice | `cycle i, v in enumerate(lista):` |
| Operador de pertinência | `x in lista` como expressão |
| Interpolação | `f"total: {x}"` |
| Ternário | `a given cond otherwise b` |

**5. Verificação de contrato de traits**

Um blueprint pode declarar `with Serializavel` e não implementar `serializar`.
Ninguém reclama até alguém chamar. Deveria falhar na declaração.

**6. Casamento de padrão em `match`**

Hoje `match` compara por igualdade. Falta desestruturar
(`point [a, b]:`), casar por tipo (`point Integer:`) e ter guardas
(`point n given n bigger 10:`).

**7. Geradores**

`yield` retorna e encerra. Não há como produzir uma sequência preguiçosa —
o que é uma lacuna sentida numa linguagem que se apresenta como voltada a dados.
Precisaria de outra palavra (`produce`, por exemplo) para não colidir.

**8. Concorrência com garantias**

`thread` e `parallel` não sincronizam variáveis compartilhadas; só `channel` é
seguro. Falta `mutex`/`lock`, `await` sobre várias tarefas em paralelo, e
`parallel` deveria tratar cada **bloco** como uma tarefa, não cada instrução.

### Prioridade baixa

**9. Ferramental**

- Formatador (`dataforge fmt`) — indentação obrigatória sem formatador convida a
  divergência de estilo.
- *Language server* (LSP) para autocompletar, ir-para-definição e erros em tempo
  real. A gramática TextMate existe, mas só colore.
- Depurador com breakpoints — hoje só `inspect`.
- Cobertura de testes.

**10. Gerenciador de pacotes**

Sem `dataforge install`, não há ecossistema: nenhuma forma de publicar ou
consumir bibliotecas de terceiros. Precisa de um registro, um manifesto
(`dataforge.toml`) e resolução de versões.

**11. Desempenho**

Interpretador de árvore, sem otimização. Alternativas, em ordem de esforço:
cachear a resolução de nomes por nó, compilar para bytecode com uma máquina de
pilha, ou traduzir para bytecode Python. Nada disso importa até alguém reclamar —
e ninguém reclamou ainda.

**12. `frame`, `train`, `predict`**

As três palavras existem no lexer, no parser e no interpretador, mas devolvem um
vault com um campo `__type__` e nada acontece. Ou se implementa (DataFrame de
verdade, ajuste de modelo) ou se remove. Manter marcador sintático sem semântica
é pior que não ter.

---

## 6. Roadmap sugerido

**3.2 — confiança**
Análise estática, rastreamento de pilha, contrato de traits.

**3.3 — ergonomia**
Compreensões, desestruturação, `cycle` com índice, `in` como operador,
interpolação, `match` com padrão.

**3.4 — módulos**
`relay` respeitado, import seletivo, caminhos relativos, detecção de ciclo.

**4.0 — ecossistema**
Gerenciador de pacotes, LSP, formatador, decisão sobre `frame`/`train`/`predict`.

---

## 7. Resumo em uma frase

DataForge é uma linguagem de programação real e razoavelmente completa, cuja
implementação tinha vinte e um defeitos — onze deles corrompendo a semântica —
que foram corrigidos e cobertos por teste; o que falta agora não é fundação, é
ferramental: análise estática, rastreamento de pilha e um sistema de módulos que
faça o que promete.
