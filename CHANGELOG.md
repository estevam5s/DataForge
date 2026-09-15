# Mudanças

DataForge segue [versionamento semântico](https://semver.org). O que
cada número significa, e o que pode quebrar entre versões, está em
[`doc/ESTABILIDADE.md`](doc/ESTABILIDADE.md) — e é **verificado** por
`tests/test_estabilidade.py`, não só prometido.

> O histórico completo da 1.0.0, com tudo o que ela reúne, está em
> [dataforge-lang.vercel.app/docs/versoes](https://dataforge-lang.vercel.app/docs/versoes).
> Aqui ficam as mudanças **depois** dela, que é o que interessa a quem
> já tem código escrito.

---

## Não lançado

### Acrescentado

- **As mensagens saem em português, e `DF_IDIOMA=en` volta ao inglês.** O
  runtime falava inglês e a CLI falava português: medido, `interpreter.py`
  tinha 234 mensagens em inglês contra 55 em português, e `cli.py` o
  inverso. Quem escreve em pt-BR recebia `dataforge check` em português e
  o erro de execução em inglês, na mesma sessão. `dataforge/idioma.py`
  traduz **na hora de desenhar**, por um catálogo de 86 moldes — o texto
  nasce em inglês onde sempre nasceu, e `error.message` não muda, porque é
  o que um `handle` compara. O que ainda não tem tradução **sai em
  inglês**, que é o único fallback honesto, e um teste mede a cobertura
  para que a lista cresça em vez de parar pela metade.

- **O parser não para mais no primeiro erro de sintaxe.** Quatro erros
  num arquivo davam **uma** mensagem, e ela apontava a linha 2 para um
  descuido da linha 1 — porque um `+` pendurado no fim de uma linha só se
  revela quando o `:=` da seguinte aparece. Quem escrevia corrigia,
  compilava, descobria o segundo, corrigia, compilava: uma volta por
  erro. Agora a leitura se recupera no fim da instrução e segue, e
  `dataforge run` e `dataforge check` mostram a leva inteira, cada erro
  com o seu próprio trecho desenhado. A recuperação conta `INDENT` e
  `DEDENT` para **não sair do bloco** por engano — sem isso, um erro no
  corpo de uma ação faria o resto do arquivo virar um segundo mar de
  erros falsos. Guarda **um erro por linha** (a cascata é o eco, não o
  diagnóstico) com teto de 12, e a exceção continua carregando o
  **primeiro** erro, então todo `except ParseError` que já existia
  funciona como antes.

- **A ponte para o Python** — `adopt Python.numpy as np` traz qualquer
  biblioteca do Python. Os valores atravessam **sem conversão**: um
  `ndarray` continua um `ndarray`, e por isso `a * 2` é a conta
  vetorizada do numpy, e não um laço. `Arcane.Ponte` responde se um
  pacote existe, explora o que ele oferece e converte quando se pede.
  ([`/docs/tecnicas/ponte`](https://dataforge-lang.vercel.app/docs/tecnicas/ponte))

- **`Arcane.Decimal`** — número exato, para quando `0.1 + 0.2` precisa
  dar `0.3`. Arredonda meio-para-cima (contábil, não bancário), e
  `Decimal.repartir` divide sem perder centavo. Misturar `Decimal` com
  `Float` numa conta é **recusado**, para que a garantia não se perca em
  silêncio.
  ([`/docs/tecnicas/decimal`](https://dataforge-lang.vercel.app/docs/tecnicas/decimal))

- **Chamada de cauda** — `yield f(…)` onde `f` é a própria ação virou um
  salto: um quadro em vez de mil. Um milhão de chamadas recursivas onde
  antes mil já era `StackOverflowError`. Recusa-se quando há `defer`, no
  meio de `monitor`, em recursão indireta, e quando a ação nunca
  devolve — esta última para não trocar uma mensagem de erro por um
  travamento mudo.

- **Executável sem Python** — um arquivo por sistema, com o
  interpretador dentro. `dataforge` passa a rodar em máquina que não tem
  Python nenhum.

- **Compilação para fechamentos** — a árvore é percorrida uma vez e vira
  funções Python. De 1,23× a 1,80× conforme a carga, medido.

### Mudado

- **`void` não vira mais texto.** `"Olá, " + nome`, com `nome` valendo
  `void`, devolvia `"Olá, void"` — a palavra `void` impressa onde devia
  ir o nome, e sem nada denunciando. É o `"undefined"` do JavaScript, e
  era a última armadilha de corrupção silenciosa que nem o `check` nem o
  `lint` mencionavam. Agora é erro, e o `check` o acusa quando consegue
  provar que o lado é `Void` (calando quando não consegue, como sempre).
  **Número, booleano e coleção continuam coagindo** — ali os dois lados
  existem, e o texto é o que quem escreveu quis dizer. As duas saídas:
  `nome ?? ""` para dar um padrão, ou `$"Olá, {nome}"`, que é um pedido
  explícito e **continua desenhando `void`**. A coerção inteira passou a
  estar documentada na [§2.3 da referência](doc/REFERENCIA.md), onde
  antes `+` aparecia só como "soma".
  Nos 369 arquivos `.df` do repositório isto acertou **uma** linha, num
  exemplo que demonstrava imprimir cada tipo.

- **`frame`, `train` e `predict` fazem alguma coisa.** As três devolviam
  um vault com `__type__` e paravam ali. Agora `frame` devolve o Frame
  do `Arcane.Analytics` e `train`/`predict` chamam o `Arcane.Cortex`.
  **Se você dependia do vault com `__type__`, isso mudou** — mas ele não
  fazia nada, então não havia o que depender.

- **`async`/`await` é concorrente de verdade.** A palavra era aceita,
  guardada e nunca lida: chamar uma ação `async` não deixava nada mais
  rápido. Agora a chamada começa o trabalho numa thread e `await`
  espera. Seis esperas de 200 ms custam 200 ms, não 1,2 s.

- **`typeof` de um número de biblioteca** responde `Integer`/`Float` em
  vez do nome do tipo de lá. `np.int64` faz conta de inteiro, e
  `given typeof(x) is "Integer"` seria falso para um valor que soma,
  divide e compara como um.

### Corrigido

- **A metade das mensagens do CPython passava sem tradução.** A regra é
  que nenhuma mensagem cita tipo do Python — `int`, `str`, `dict` e
  `NoneType` não existem nesta linguagem, e uma mensagem nesses termos
  manda a pessoa procurar na documentação errada. `_traduzir_tipos` só
  trocava o nome **entre aspas**, e o CPython o escreve nu com a mesma
  frequência: quem abria um banco com o argumento errado recebia
  `expected str, bytes or os.PathLike object, not dict` — cinco palavras,
  nenhuma delas existente aqui. Agora a tradução reconhece a **moldura**
  (`, not dict`, `must be str`, `expected str`, `can only concatenate
  str`) em vez da palavra solta, que é o que permite estendê-la sem
  estragar texto legítimo: `file not found: list.txt` continua intacto.
  O nome da **implementação** também sai — `strptime() argument 1 must
  be…` virava a resposta de `Time.parse`, e quem escreveu nunca ouviu
  falar de `strptime`.

- **Nove mensagens escritas à mão na stdlib nomeavam o tipo do Python.**
  A trava existia e lia só `interpreter.py`, então `Arcane.Bytes` dizia
  "esperava bytes e veio dict", `Arcane.Decimal` "precisa de um Decimal,
  e veio str", e `opcoes.ler` — que responde por **todo** vault de opções
  da biblioteca — "e recebeu list". Todas passaram a usar `_df_type`, que
  é a mesma fonte que o `typeof` usa. A trava agora varre a árvore
  inteira, e permite o nome cru só onde o sujeito é uma **exceção do
  Python** ou um **nó da AST** — os dois casos em que não há nome nesta
  linguagem. E há uma segunda trava, **comportamental**: ela chama a
  stdlib com o argumento errado e lê a mensagem que sai, porque o texto
  que vazava não está escrito em arquivo nenhum do repositório.

- **O método de um `record` ficava fora do analisador, nas duas
  direções.** `p.naoExiste()` passava no `check` e só estourava em
  execução — a conferência existia para o campo (`p.clientte`) e para as
  duas formas em `blueprint`, e faltava justamente na que mais se
  escreve. A mesma raiz produzia o defeito inverso, que é pior: um
  método legítimo passado adiante como valor (`f := p.norma`) era
  **acusado de não existir**, porque o mapa de membros do record guardava
  só os campos. Os métodos passaram a morar num mapa separado — no mesmo
  dicionário, `Ponto(norma := 1)` e `p with {"norma": 1}` começariam a
  passar, que é trocar um falso alarme por um silêncio.

- **A chamada de um método inexistente saía sem linha nem coluna.**
  `o.semCampo` era reportado no lugar certo e `o.semMetodo()` em `0:0`,
  sem o trecho desenhado — para `record` e para `blueprint`. Quem decide
  que o nome não existe é o objeto, e ele não conhece o arquivo; a
  leitura de membro já tinha uma casca cujo único propósito era a
  posição, e a chamada não tinha a equivalente. Num arquivo de 200
  linhas a segunda forma não dizia onde.

- **A dica do erro de `record` listava só os campos.** Quem escrevia
  `normaa` era mandado procurar entre `x, y`, sem o `norma` que queria —
  um nome válido ali, omitido pela própria mensagem que deveria
  sugeri-lo.

- **`obj.metodo(…)` avaliava o objeto duas vezes** quando o método não
  era de nenhum tipo conhecido por nome. O resultado saía certo; o que
  se repetia era o **efeito colateral** — uma consulta ao banco, uma
  escrita em arquivo, um contador.

- **O registro de testes do Crucible vazava entre arquivos.** Ele era um
  objeto de módulo, um por processo, e `dataforge test` cria um
  interpretador por arquivo: o segundo via os *trials* do primeiro.
  Contagem errada, e a falha de um reaparecendo no relatório do outro.

- **O LSP não subia em nenhuma instalação por `pip`.** A extensão ia
  sem o `vscode-languageclient` — sem autocompletar, sem erro ao
  digitar, e sem nada explicando.

- **`await f() is "ok"` aguardava a comparação**, e não a chamada. Ficou
  escondido enquanto `await` era identidade.

- **O Windows** — a CLI morria com `UnicodeEncodeError` antes da
  primeira linha útil (a saída redirecionada é `cp1252`); a pilha não
  cabia em mil quadros no 3.10; `os.path.relpath` levantava entre
  unidades diferentes **dentro de uma mensagem de erro**; e `/tmp` estava
  cravado em doze lugares.

- **`math.factorial(x)` no 3.12, `(n)` no 3.13** — a documentação gerada
  dependia da versão de Python de quem rodou o gerador.

- **Cinco f-strings** usavam sintaxe só do 3.12. `dataforge/cli.py` não
  importava no 3.10, e com ele a CLI inteira.

---

## 1.0.0

A primeira versão pública. O histórico completo, com tudo o que ela
reúne, está em
[dataforge-lang.vercel.app/docs/versoes](https://dataforge-lang.vercel.app/docs/versoes).
