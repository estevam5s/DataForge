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

- **JWT em `Arcane.Crypto`** — `jwt_assinar`, `jwt_verificar` e `jwt_ler`,
  com `HS256`/`HS384`/`HS512`. Mora ali porque um JWT **é** um HMAC sobre
  dois pedaços de base64url, e as duas peças já estavam no módulo. Três
  decisões: **quem decide o algoritmo é quem verifica**, e não o token — ler
  o `alg` do token é a falha clássica da área, e é como se aceita um
  `alg: none` forjado; `jwt_verificar` **devolve vault** (`valido`, `carga`,
  `motivo`) em vez de levantar, porque token inválido é o caso normal de um
  servidor; e um token **vencido entrega a carga**, para quem renova saber
  de quem era. Interopera: o vetor conhecido do `jwt.io` é aceito, e há
  teste para isso — um JWT que só esta biblioteca entende não é um JWT.

- **Compressão de valor em `Arcane.Archive`** — `comprimir`/`descomprimir`
  (deflate cru), `gzip`/`de_gzip` e `taxa`. O módulo fazia zip e tar de
  **arquivo**, e não havia como encolher um valor na memória — que é o que
  um corpo de HTTP, um campo de banco ou uma mensagem de fila pedem.
  Deflate e gzip são formatos **diferentes**, e a mensagem de erro de cada
  um diz isso: mandar deflate onde se prometeu `Content-Encoding: gzip` dá
  um corpo que o navegador recusa sem explicar. A `taxa` passa de 1 quando
  o dado não encolhe, que é a informação mais útil ali.

- **`Arcane.Url`** — o 48º módulo, e a primeira das lacunas do `TODO.md`
  medidas contra o que já existia. Ler um endereço em partes, montar de
  volta, resolver relativo como um navegador (`juntar`), trocar parâmetros
  preservando os outros (`com_query`, e `void` ali **apaga** o parâmetro),
  query string em vault ou em cluster quando a chave repete, e escape para
  caminho e para valor. Todo programa que fala HTTP mexe com URL, e isso
  vivia dentro do Kiln e do `Arcane.Http`, fora do alcance de quem escreve.
  Três decisões: a **porta** sai `Integer` (texto faria `porta + 1`
  concatenar) ou `void` quando a URL não a disse; `origem` **não leva
  credencial**, porque é o campo que vai para log e para CORS; e `montar`
  recusa campo que não conhece, porque `caminh` montaria um endereço sem
  caminho sem nada denunciando.

- **O `match` avisa o caso esquecido além do enum.** Booleano (`point yes`
  sem `point no`), sequência (`point [cabeça, ...resto]` sem `point []` — a
  recursão que quebra na lista vazia) e a família de um `abstract
  blueprint` (`point Circulo` e `point Quadrado` com um `Triangulo`
  concreto no arquivo). E dois furos da checagem de enum: `or` a fazia
  desistir, e um ramo com **guarda** contava como cobertura — `point Cor.Azul
  when x` deixa passar o Azul em que `x` não vale.

- **Generics com limite: `<T extends X>`.** O limite pode ser tipo
  embutido, blueprint, trait ou record, e — diferente do `<T>` solto, que
  só documenta — é **verificado**: o `check` confere o argumento na chamada
  (inclusive através de `adopt`), e a execução confere o valor. Dentro do
  corpo, `T extends Number` é um `Number` para o analisador, o que permite
  `a bigger b`.

- **Breakpoint condicional, contagem e logpoint.** No editor, as três
  opções da margem — "Edit Condition", "Hit Count", "Log Message" — que o
  VS Code escondia porque o adaptador respondia que não as suportava. No
  terminal, `b 12 se x bigger 3`, `b 12 vezes % 10` e `b 12 log x={x}`. O
  logpoint usa a interpolação da própria linguagem, com o mesmo formato de
  `$"…"`. Uma condição que não dá para avaliar **para e diz por quê**:
  calar faria a parada nunca disparar, e a pessoa concluiria que o código
  não passa por ali. Uma contagem que não se entende é recusada na margem.

- **O depurador do editor para cada thread sozinha.** O adaptador tinha um
  só estado de parada: com duas threads batendo em paradas, a segunda
  sobrescrevia a foto da primeira — a pilha de uma com as variáveis da
  outra — e soltar uma soltava as duas. Agora cada thread de `thread` e
  `parallel` para, mostra a própria pilha e anda sozinha, e o painel lista
  as threads vivas.

- **`parallel` por bloco.** Cada instrução de `parallel` era uma thread, e
  duas coisas que precisam acontecer em ordem — buscar e depois salvar —
  não tinham como ficar juntas. Agora um `thread:` **dentro** de `parallel`
  é uma tarefa só: o bloco roda em ordem, as tarefas rodam juntas, e o
  `parallel` espera todas. Sem palavra nova, e sem mudar nada que existia:
  instrução solta continua sendo uma tarefa cada, e `thread:` fora de
  `parallel` continua disparando e seguindo.

- **O canal sabe esperar.** `receive()` devolvia `void` na hora, e esperar
  por um item exigia um laço de `sleep` — que gasta CPU, acorda tarde e
  piora com muitos consumidores, justamente quando um canal serve para
  algo. Agora `receive(ms)` espera até aquele prazo e `receive(void)` espera
  o que for preciso, dormindo numa `Condition` até o `send` avisar. Medido:
  um consumidor acorda em ~155 ms quando o item é enviado aos 150 ms.
  `len(canal)` e `canal.pending()` dizem quantos itens há.

  **O padrão sem argumento continua sem esperar**, e de propósito: dois
  exercícios afirmam `fila.receive() is void` para o canal vazio. Trocar o
  padrão não daria erro em programa nenhum — daria **travamento**, a pior
  falha possível, porque não deixa mensagem nem pilha.

- **O contrato de trait é cobrado antes de rodar.** Era o item de topo do
  roadmap. O interpretador já o conferia no lugar certo — na **declaração**
  do blueprint, e não na chamada do método —, mas só em execução: um
  blueprint que esquecia um método do trait passava limpo no `check` e
  derrubava o programa ao ser declarado. Num projeto grande, o arquivo que o
  declara pode ser importado só num ramo, e aí o erro chega em produção.

  A conferência estática precisou de um conjunto de membros **diferente** do
  que já existia. Para `p.metodo`, o método abstrato de um trait conta: o
  trait promete que o membro existe, e quem escreve pode chamá-lo. Para o
  contrato, contar a promessa como cumprimento faz a regra aprovar
  exatamente o que ela deveria recusar — e foi o primeiro jeito que
  escrevi, com o teste do blueprint incompleto passando. Daí
  `_membros_implementados` ao lado de `_membros_com_heranca`.

  Cala nos três casos legítimos: o método veio da mãe, o blueprint é
  `abstract` (promete e não entrega de propósito), ou o trait vem de outro
  arquivo e não se sabe o que ele exige.

- **O analisador prova mais quatro coisas antes de rodar.** Medido numa
  bateria de dez erros que um analisador maduro pega, o `check` pegava
  **três**; hoje pega nove, e o `lint` o décimo. Os quatro que faltavam
  tinham em comum o fato de a informação para provar já existir no arquivo:
  `xs[10]` num cluster de três (`indice-fora-do-alcance`), `v["cidad"]` num
  vault sem a chave e com sugestão de nome parecido (`chave-ausente`),
  `cycle i from 5 to 1` que nunca roda e `step 0` que nunca termina
  (`cycle-vazio`), e `1 is "1"`, que é sempre `no`
  (`igualdade-impossivel`).

  A prudência é o recurso. Um nome perde a garantia do literal se em
  qualquer lugar do arquivo ele recebe valor duas vezes, é passado como
  argumento, tem um método que muda o tamanho chamado nele, ou tem índice
  ou chave escritos. E há três silêncios deliberados, cada um um falso
  alarme evitado no caminho mais comum: `v["k"] ?? padrao` não é acusado (é
  o conserto que a própria dica recomenda), um parâmetro de tipo genérico
  não é um tipo, e o tipo declarado de uma ação **decorada** não vale —
  `mark @repetir(3)` sobre `-> String` devolve um `Cluster`, e a
  comparação que o analisador chamava de impossível passa em execução.
  Nos 369 arquivos `.df` do repositório: **zero** alarme novo.

- **A §2.4 da referência documenta divisão, resto e arredondamento com
  negativos.** `-7 ~/ 2` é **-4** (arredonda para baixo, não para o zero),
  `-7 % 2` é **1** (o resto tem o sinal do divisor), e `round(2.5)` é
  **2.0** (empate vai para o par). As três operam como em Python, as três
  surpreendem quem espera C ou JavaScript, e nenhuma estava escrita — o que
  as tornava erro silencioso para quem supôs o contrário. Cada afirmação da
  seção é verificada por um `.df` que roda.

- **As 228 embutidas se explicam.** 202 delas — 88% — não tinham
  docstring nenhuma, e o hover mostrava a assinatura do invólucro
  (`len(*args, **kwargs)`) com a frase "Wraps a Python callable as a
  DataForge built-in", igual para todas. São as funções que todo iniciante
  toca primeiro e as únicas que não pedem `adopt`. Agora todas têm, e as
  que escondem uma armadilha a declaram: `round` arredonda o empate para o
  **par** (2,5 dá 2,0), `stdev` é **amostral** (divide por n-1), `hash`
  trabalha sobre o **texto** do valor (então `hash(1)` e `hash("1")`
  coincidem), `count` sem o item devolve o **tamanho**, `freeze` de um
  vault devolve pares e **não** um vault, e `sleep` conta em
  **milissegundos**. Há trava para as três coisas: nenhuma sem docstring,
  nenhuma reusando a frase do invólucro, e a armadilha do `sleep` fechada.

### Mudado

- **Desempenho, medido com `cProfile` e não com intuição.** As tabelas de
  método de texto, vault e cluster eram literais **dentro** de
  `_ler_membro_cru`: 146 lambdas construídos a cada `xs.append(i)` ou
  `"a".upper()`, para escolher um e jogar o resto fora. Agora moram no
  módulo. O pipeline (`sift`/`morph`/`distill`) passou a ser compilado para
  fechamentos, e a máquina de chamada deixou de refazer por chamada o que é
  da ação (nome do escopo, aridade na forma posicional exata, dois sets
  vazios por escopo). Medido: um laço de 200 mil `append` + `distill` caiu
  de **0,77 s para 0,27 s** (2,9×), 200 mil chamadas de método de **0,64 s
  para 0,49 s**, e `fib(24)` de **0,48 s para 0,42 s**.

- **Um erro dentro de `defer` não é mais descartado.** Era
  `except Exception: pass`, e isso estava escrito como decisão (na
  referência e no capítulo 17 da trilha). O `defer` é onde se fecha arquivo
  e se desfaz transação, então o erro que sumia era o de uma limpeza que
  não aconteceu — e o programa terminava com código 0. Agora vale o modelo
  do try-with-resources: **todos** os `defer` rodam mesmo que um falhe; se
  a ação saiu bem, o erro do `defer` viaja; se a ação já estava falhando,
  viaja o erro **original**, com o do `defer` em `e.outros`. A preocupação
  registrada — um erro de fechamento sequestrar o resultado — continua
  atendida no caminho em que ela importa.

  **Quebra código** que contava com o descarte. No repositório inteiro, só
  o exemplo da trilha que demonstrava o descarte dependia disso.

- **`e.outros`** traz os demais erros de um `handle`: a leva de um
  `parallel` e os erros de `defer` anexados. Eles eram desenhados no
  terminal e inalcançáveis de dentro do programa.

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

- **Um `defer` dentro de um laço nunca rodava.** Ele se registrava no
  escopo em que aparece, e só o escopo da **ação** era consultado na saída.
  `given` e `monitor` funcionavam por acidente — compartilham o escopo da
  ação; `cycle` e `persist` têm o próprio, e ali o `defer` ia para um lugar
  que ninguém olhava. Fechar um arquivo por volta é o uso mais óbvio de
  `defer` num laço, e era exatamente o que não acontecia, calado. No topo
  do programa, idem: não há ação nenhuma, e ele nunca rodava.

  Agora o `defer` procura a fronteira que **promete** rodá-lo: a ação, e —
  para quem dispara trabalho — a `thread` ou a tarefa de `parallel`, que é
  quando o recurso daquele trabalho deixa de ser usado; no topo, o fim do
  programa, inclusive quando ele sai por erro. O bloco continua rodando no
  escopo em que foi escrito, então o `defer` de um `cycle` vê o `i` da volta
  em que nasceu.

- **Um estágio de pipeline com ação nomeada não conferia nada.**
  `["x"] >> morph dobrar`, com `action dobrar(n: Integer) -> Integer`,
  devolvia `[xx]` em silêncio: era um caminho paralelo à chamada normal, sem
  aridade, sem tipo de parâmetro nem de retorno, e sem empilhar quadro (o
  erro saía sem pilha). Uma ação de dois parâmetros num `morph` dizia
  `'b' is not defined` em vez de nomear a aridade. A mesma ação respondia
  duas coisas conforme fosse chamada com parênteses ou por um `>>`.

- **O `check` acusava toda chamada de genérico com parâmetro `T`.**
  `eco<T>(x: T)` chamado com um texto dava "espera T, e recebeu String" —
  o `T` era tratado como nome de tipo. A documentação dizia que essa ação
  aceita qualquer valor, e o analisador a contradizia.

- **A filha não servia onde se espera a mãe, no `check`.** `usar(b: Base)`
  recebendo uma `Filha` era erro. A execução aceitava; o analisador
  comparava só nomes.

- **Um trait não servia como tipo.** `tamanho(m: Medivel)` com uma instância
  que adota `Medivel` levantava em execução, e `instanceof(x, "Medivel")` e
  `e_um(x, "Medivel")` respondiam `no` — as três olhavam a MRO, que não
  inclui trait.

- **Três lugares que não podem derrubar o que está em volta deixaram de
  descartar o erro.** O `after` do Kiln e o tratador de erro personalizado
  (`Kiln.on_error`) rodam com a resposta já decidida, e continuam sem
  derrubá-la — mas um `after` quebrado parecia um que funcionava, sem o
  cabeçalho e sem motivo; agora ele avisa no terminal. E
  `P.repetir_a_cada` fazia `except BaseException: pass` a cada volta, para
  sempre: uma limpeza agendada que falhava toda vez parecia uma que rodava.
  A repetição segue depois de uma falha, avisa **uma vez por mensagem
  diferente** (a mesma falha a cada 100 ms inundaria o terminal), e o vault
  devolvido ganhou `falhas()` e `ultimo_erro()` para o programa perguntar.

- **Segurança: o middleware do `Arcane.Http` deixava passar pedido
  recusado.** Um middleware que **levantava** era pulado
  (`except Exception: pass`) e o handler rodava. Com uma autenticação que
  recusa levantando — a forma mais natural de recusar —, um pedido **sem
  credencial recebia 200 e os dados da rota**. E um middleware que
  **respondia** `401` não interrompia nada: o handler rodava depois, com os
  efeitos dele (apagar, cobrar), e a resposta ainda saía `200`, porque
  `send` tinha `status=200` por padrão e atropelava o `res.status(401)` da
  linha anterior. Os três foram medidos contra um servidor de verdade.
  Agora o middleware falha **fechado**: levantou, é `500` e o handler não
  roda; respondeu, a resposta dele é a final. O Kiln, o framework
  principal, já se comportava assim — era este módulo que divergia.

- **Um erro dentro de `parallel` ou `thread` era engolido.** Os dois
  faziam `except Exception` e imprimiam `[Parallel Error] …` ou
  `[Thread Error] …` — uma linha sem trecho de código nem pilha — e o
  programa **seguia**. O código de saída era **0**, e `monitor/handle` não
  conseguia pegar o erro. Um CI rodando o arquivo passava verde com metade
  do trabalho perdida.

  `parallel` é estruturado, então o erro tem para onde voltar: ele espera
  **todas** as instruções e levanta o primeiro erro na linha do bloco, com
  os demais em `.outros`, na **ordem das instruções**. `handle` agora o
  pega. `thread:` não espera, então o erro é **desenhado na hora** na saída
  de erro e o programa termina com código diferente de zero. Saíram junto o
  `join(timeout=30)`, que **abandonava** as threads depois de 30 s, e o
  traceback do Python que `halt`/`skip`/`yield` produziam dentro de uma
  thread.

- **`cbrt` de um número negativo devolvia um complexo.** `cbrt(-8)` dava
  `(1.0000000000000002+1.7320508075688772j)` em vez de `-2`, porque
  `x ** (1/3)` de um negativo é complexo — e o número complexo era
  entregue calado a um programa que ia fazer conta com ele. Todo cubo tem
  uma raiz real.

- **`sleep` dizia uma unidade e usava outra.** O parâmetro se chamava
  `seconds` e o corpo dividia por mil: quem lesse a assinatura no hover
  escreveria `sleep(2)` esperando dois segundos e receberia dois
  milissegundos.

- **Dois temas de cor**, `DataForge Escuro` e `DataForge Claro`, **gerados
  da gramática**. O gerador recusa rodar se um dos 43 escopos ficar sem
  cor — a mesma trava da gramática, pelo mesmo motivo: um tema escrito à
  mão pinta o que o autor lembrou, e o que ele esquece herda a cor do tema
  anterior. As onze palavras do Kiln têm cor própria (elas são
  contextuais, e quem lê precisa ver que aquele `route` é a palavra do
  framework), o pipeline `>>` não tem a cor de `+`, e o claro não é o
  escuro invertido: o amarelo da marca dá contraste 1,3:1 sobre branco
  onde a WCAG pede 4,5:1.

- **O hover leva à documentação.** Ele dizia o que a palavra faz e
  mostrava um exemplo; faltava o passo seguinte, que é ir ler. Agora cada
  cartão traz o link da página certa e as **palavras do mesmo assunto** —
  `given` sem `orif` e `otherwise` ensina um terço do condicional. Os
  destinos vivem num lugar só (`docs_links.py`) e são **conferidos contra
  as páginas que existem**: um link quebrado num hover gasta a confiança
  de quem clicou.

- **Treze palavras não tinham hover nenhum** — as onze do Kiln mais
  `operator` e `slots`. Elas são contextuais e não estão em `KEYWORDS`, e
  a trava de cobertura lia só `KEYWORDS`: ficaram de fora justamente as do
  código web, que é onde mais gente começa. As 100 têm ficha agora, cada
  uma com um exemplo que **roda** na suíte.

- **`dataforge palavras`** — as 100 palavras no terminal, com o exemplo
  que roda e o endereço da doc. `--json` é o que a extensão consome, para
  não repetir a tabela.

- **Quatro comandos no editor**: abrir a documentação do símbolo sob o
  cursor (`Shift+F1`, resolvido pelo próprio hover do LSP, sem segunda
  cópia do mapa), as 100 palavras num seletor com inserir/ver/ler, trocar
  para o tema do DataForge, e escolher o idioma das mensagens — que passa
  por `DF_IDIOMA` em tudo o que a extensão roda, para o sublinhado no
  editor e a saída do terminal não falarem idiomas diferentes.

- **O hover de embutida mostrava o invólucro, não a função.** As 228
  embutidas são `BuiltinFunction`, e o cartão exibia `len(*args, **kwargs)`
  com a docstring "Wraps a Python callable as a DataForge built-in" —
  igual para todas as 228. Isso é pior que não ter hover: parece que a
  linguagem não sabe o que as próprias funções fazem. Agora mostra
  `len(obj)` e a documentação de verdade, no hover e no autocompletar.

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
