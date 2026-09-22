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

### Corrigido — defeitos da linguagem achados escrevendo a documentação

Cada um apareceu porque um bloco da documentação que devia rodar não
rodava — e a causa era da linguagem, e não do bloco.

| Defeito | Efeito |
|---|---|
| **duas instruções na mesma linha** eram aceitas | `x := 12   // 3 parcelas` virava uma divisão seguida de uma instrução solta; **17 blocos do site** só "compilavam" por isso. Agora é erro de sintaxe, com a dica do `//` |
| **`@f()` era tratado como `@f`** | `mark @app.texto()` chamava `app.texto(acao)`, e a ação caía no parâmetro do padrão: o bot ficava calado |
| **o corpo de `lambda` não absorvia `??` nem o ternário** | `lambda x: v[x] ?? 0` nunca usava o padrão; `lambda s: "" given ok(s) otherwise "x"` avaliava `s` fora do lambda |
| **o campo de um `D.valor` era sombreado por método** | `cliente.nome` devolvia o método `nome()`, e não "Ana" |
| **`Kiln.use(app, Kiln.idempotente())`** registrava só metade | a resposta não era guardada, e o reenvio cobrava de novo |
| **a sonda do Telegram marcava todo chat como privado** | não havia como testar um comando de grupo (`e_admin()` era sempre `yes`) |
| **`Molde({...})`** não aceitava vault | só argumentos nomeados, com erro de aridade sem nome |
| **`O.alertar` com lista** estourava com um nome do Python | aceita a lista de regras, e o vault de antes |
| **`Comp.tokens`** devolvia `str(valor)` | `7` chegava como `"7"`, e o fim de arquivo como o texto `"None"` |

E o `check` ganhou o aviso `coalescencia-engole-comparacao`:
`v[k] ?? void is void` é `v[k] ?? (void is void)`, e a pergunta "é void?"
nunca é feita.

### Adicionado — à linguagem, para as seções de API a concorrência

| Onde | O quê |
|---|---|
| `Kiln` | `problema` (RFC 9457), `negociar` (Accept, q, curinga), `precondicao` (If-Match → 412/428, If-None-Match), `etiqueta` (ETag forte), `cursor`/`ler_cursor` (opaco e assinado), `links` (RFC 8288) |
| `Arcane.Telegram` | `dividir` — o limite de 4096 é em **UTF-16**, e o escape do MarkdownV2 nunca é partido; `paginado` e `ler_pagina` |
| `Arcane.Dominio` | fonte de eventos: `armazem` com `versao_esperada` e o novo `AggregateVersionError` (DF1610), `reconstituir` estrito, `projecao` idempotente pela posição |
| `Arcane.Estrutura` | campos `char[N]` e `bytes[N]`; `campos_de_bits`; operações de bits (`bits_e`, `bits_ou`, `bits_xou`, `bits_nao`, `deslocar`, `contar_uns`…) — funções, porque `>>`, `\|` e `&` já têm dono; `varint`/`ler_varint` (LEB128), `zigzag`; `crc32`; `trocar_ordem`; `mapear` (arquivo em memória) |
| `Arcane.Reativo` | `historico` (desfazer/refazer; um `lote` é um passo) e `recurso` (carregando/pronto/erro, com a resposta velha descartada) |
| `Arcane.C` | `errno` e `zerar_errno` — toda biblioteca abre com `use_errno` |
| `Arcane.Compilador` | `dominancia` e `dot` (o grafo de fluxo para o Graphviz) |
| `Arcane.Laco` | canal entre fibras: `canal`, `enviar`, `receber` |
| `Arcane.Observar` | `orcamento`, `queima` e `alerta_slo` (janela dupla) |
| `Arcane.Inicio` | `ao_encerrar`, `esquecer_encerramento`, `encerrando` — SIGTERM sai com 143, finalizadores ao contrário |
| `Arcane.Abi` | `proxima_versao` (com a regra do 0.x) e `changelog` |
| `Arcane.Ecossistema` | `glossario` e `definir` — cada termo aponta para uma página que existe |
| `Arcane.Concurrent` | `ator`: estado com dono, mensagem em fila |

### Documentação — mais 109 rotas

API (10), Telegram (8), Domínio (9), Estruturas (15), Reativo (8), FFI (7),
Compilador (9), Runtime (7), Observabilidade (7), Partida (6), ABI (7),
Ecossistema (6) e Concorrência (8). **Onze são a página-raiz de uma seção
que respondia 404**: `/docs/ffi`, `/docs/compilador`, `/docs/runtime`,
`/docs/observabilidade`, `/docs/memoria`, `/docs/partida`,
`/docs/hardware`, `/docs/abi`, `/docs/alvos`, `/docs/ecossistema` e
`/docs/concorrencia`.

### Adicionado — à linguagem

| O quê | Antes |
|---|---|
| `{1, 2, 3}`, `{x * 2 cycle x in xs}` e `set(fonte)` — o **conjunto** tem literal, compreensão e anotação (`s: Set`) | só havia `set()` embutido de fora, e `Set` não era um tipo que se pudesse escrever |
| `input(pergunta)` — lê uma linha; `void` no fim da entrada | a linguagem não tinha como perguntar nada a quem roda o programa |
| `relay novo as antigo` — exportar com outro nome | renomear uma ação pública quebrava quem a importava, e o `dataforge abi` dizia MAIOR |
| `Quadro.janela`, `acumulado`, `defasar`, `variacao`, `ranquear` | média móvel e total acumulado exigiam um laço à mão |
| `Arcane.Evolucao` — `obsoleta`, `experimental`, `renomeada`; `DF_OBSOLETOS=erro` no CI | marcar uma ação como obsoleta era um comentário |
| `Arcane.Algoritmos` — 14 clássicos (busca binária, Dijkstra, ordem topológica, LCS, Levenshtein, mochila, KMP, crivo…), cada um com a complexidade que promete | escrevia-se à mão, e errado |

Um conjunto só guarda valor que não muda: `{[1, 2]}` é recusado **na
leitura** (`set-item-mutavel`) com a saída na mensagem — `freeze(x)` ou
uma tupla.

### Adicionado — ao analisador

- `assert-sempre-verdadeiro`: `assert xs >> morph x: x is 1` testa o
  **pipeline**, que é sempre verdadeiro — o `is` fica dentro do corpo do
  `morph`. O aviso pede os parênteses. Achado escrevendo a documentação:
  um bloco passava sem conferir nada.
- Uma palavra reservada como **parâmetro** (`action f(no)`) diz qual é
  a palavra e o que fazer, em vez de um erro de sintaxe genérico.

### Documentação — 57 rotas novas

Mais as páginas de referência de `Arcane.Algoritmos` e `Arcane.Evolucao`.

| Seção | Rotas |
|---|---|
| `/docs/primeiros-passos/…` | 10 — do olá-mundo ao primeiro programa, erros comuns e próximos passos |
| `/docs/fundamentos` (o índice, que respondia **404**) e `/docs/fundamentos/…` | 1 + 9 — conjuntos, números, ausência, conversões, igualdade, imutabilidade, textos, ordem superior, recursão |
| `/docs/big-o/…` | 9 — algoritmos, busca, ordenação, grafos, programação dinâmica, texto, escolher, medir, exercícios |
| `/docs/modulos/…` | 9 — renomear, fachada, ciclos, visibilidade, estado, entrada, a ponte, dividir |
| `/docs/bibliotecas/…` | 9 — obsolescência, experimental, changelog, licença, dependências, mensagens, estabilidade, migração, checklist |
| `/docs/dados/…` | 10 — janelas, séries temporais, juntar, pivotar, limpeza, estatística, amostragem, exportar, volume, visualizar |

Todas na barra lateral, nos índices das seções, e todo bloco de código
**roda** — `tests/test_paginas_novas_rodam.py` executa cada um.

---

## 1.1.1

Correção de publicação, mais as vinte e sete rotas de documentação e o
banco em contêiner que estavam em "Não lançado".

### Corrigido — o logo do pacote no PyPI

A 1.1.0 subiu com o README apontando para `site/public/marca-favicon.svg`,
um caminho **relativo ao repositório**. O PyPI serve a descrição fora
dele, então a página do pacote mostrava o ícone de imagem quebrada. O
endereço agora é absoluto (`https://dataforge-lang.vercel.app/marca-256.png`),
e há teste sobre isso.

Uma descrição já publicada não pode ser trocada: o PyPI recusa o
reenvio de uma versão que existe. A correção **exige** uma versão nova,
e é por isso que esta é a 1.1.1.

### Adicionado — o banco em contêiner

| Símbolo | O quê |
|---|---|
| `Forge.esperar(url)` | espera o banco **aceitar** conexão, e devolve a conexão aberta |
| `Forge.de_ambiente()` | `DATABASE_URL`, `DB_URL` ou `FORGE_DATABASE_URL` |
| `Forge.compose(url)` | o serviço, o volume e a URL de dentro da rede |

`esperar` só repete **erro passageiro** — conexão recusada, reset,
`the database system is starting up`. Credencial errada levanta na
hora: repetir uma senha errada por quarenta segundos troca um erro
claro por um travamento, e o programa que espera não fica mais certo
por isso. Medido: 0,51 s contra um contêiner recém-subido, e 4 ms para
recusar uma senha errada.

### Adicionado — o ORM que faltava

`tem_muitos_atraves` (três consultas, e não N+1), `escopo`/`usar` e
`paginar`. Um `tem_muitos` através de uma tabela de junção era a
relação que mais aparece num modelo real e a única que não existia.

### Adicionado — vinte e sete rotas de documentação

Nove em **banco de dados** (contêiner, PostgreSQL, MySQL, Redis e
MongoDB, produção, receitas, e três de ORM), nove em **módulos** (as
formas de `adopt`, `relay`, pacotes, lockfile, registro, workspace,
organizar, diagnóstico, testar) e nove em **bibliotecas** (API,
opções, erros, documentar, desempenho, segurança, CI, a ponte, e
quatro bibliotecas de verdade).

Os 38 blocos DataForge delas foram extraídos e executados antes de a
página existir.

### Corrigido — a opção que não existe num `Campo`

Ela chegava como a mensagem de aridade do Python, que fala de outra
coisa. Agora o erro diz **qual** opção não existe, e lista as que o
`Campo` aceita.

---

## Não lançado

### Adicionado — sete frentes de documentação, e o que elas pediram da linguagem

**Projetos:** 22 tipos de projeto em `/docs/projetos` (CLI, API REST, ETL,
motor de regras, jogo, cálculo financeiro, autenticação, fila, interpretador,
máquina de estados, estoque, bot, painel, classificador, detector de intrusão,
cofre, planilha reativa, rotas, biblioteca, saga, agendador cron, site
estático) — cada um montado e testado como projeto a cada execução da suíte.

**Testes:** 10 rotas (TDD, unitários, parametrizados, cenários, integração,
ponta a ponta, erros, regressão, pirâmide, instáveis) e `Crucible.cenario`.

**DevOps:** 12 rotas, `Arcane.GitHub`, `dataforge check --formato=github`, e
os geradores `devops github`, `ci gitlab`, `devcontainer`, `pre-commit` e
`systemd`.

**CLI:** o índice e a referência completa saem do catálogo (65 comandos),
11 rotas por tema, e `dataforge completar <bash|zsh|fish>`.

**Gramática:** `dataforge/gramatica.py` — 55 produções conferidas contra o
parser, precedência e associatividade provadas pela árvore, as 81 palavras
reservadas cobertas; `Arcane.Gramatica`, `dataforge gramatica` e 12 páginas.

**Segurança:** 10 rotas (OWASP, API, web, segredos, logs, LGPD,
anonimização, integridade, cadeia, incidentes), `Arcane.Privacidade` e
`Arcane.Integridade`.

### Corrigido

- `NO_COLOR` não era respeitado pela CLI nem pelo `check`.
- As descrições de `new`, `palavras` e `erros` no `help` traziam números
  que envelheceram (oito modelos, 177 códigos); hoje saem dos dados.
- Os dois geradores de índice discordavam numa página sem `h2`.


### Adicionado — `Arcane.Politica`, `Arcane.Chaves` e `Arcane.Deteccao`

Os três buracos reais do `DATAFORGE_CYBER_SECURITY.md`. A maioria das
61 frentes já tinha resposta; estas não tinham nenhuma.

- **`Arcane.Politica`** — motor de autorização. Sete camadas numa
  ordem que é **contrato** (`tenant`, `negacao`, `acl`, `regra`,
  `papel`, `delegacao`, `padrao`), RBAC com herança, ABAC por
  atributo, ACL por objeto, grupos, isolamento por inquilino,
  delegação com prazo e separação de funções.
  - **O padrão é negar**, a **negação explícita vence o papel**,
    **ninguém delega o que não tem**, e **toda decisão diz qual regra
    a tomou** — um motor que responde só sim/não é impossível de
    auditar.
  - Uma regra que **falha nega**: tratar a exceção como "não opino"
    faria um bug virar autorização.
  - A **aridade da condição é perguntada**, não adivinhada. A primeira
    versão chamava com quatro argumentos e recuava no `TypeError` — e
    uma `DFAction` levanta `TypeError_` da *linguagem*, que não é o do
    Python. O erro virava "a regra falhou" e, com ele, uma negação:
    uma regra correta recusada porque o motor errou a chamada.
- **`Arcane.Chaves`** — ciclo de vida da chave. Propósito cobrado,
  prazo, rotação que **mantém as antigas decifrando o passado**,
  `kid` no dado cifrado, envelope (DEK/KEK), recifragem, derivação por
  contexto (HKDF), exportação cifrada e `precisa_rotacionar`.
  - **`cifra.abrir` devolve `None` quando a etiqueta não fecha.**
    Defensável na primitiva; aqui vira **erro**. Um `desenvelopar` que
    devolvesse `void` faria o programa acima gravar nada onde havia um
    dado — a falha de integridade é o assunto todo do AEAD.
- **`Arcane.Deteccao`** — regras sobre eventos, correlação **por
  chave** em janela **deslizante**, supressão, gravidade, mapa para
  MITRE ATT&CK, indicadores com prazo e normalização, padrões sobre
  conteúdo e leitura de log combinado.
  - Cinco falhas de cinco pessoas diferentes **não** são força bruta —
    e o alerta que mais custa é o que está errado.
  - Uma regra que falha é **contada**, e as outras seguem: um motor
    que morre no primeiro erro deixa de detectar tudo o resto, e o
    silêncio parece calmaria.
- Três classes de erro novas: `AuthorizationError`, `DelegationError`
  e `CryptoKeyError`. O catálogo vai de 215 para **218**.
- Três páginas de documentação novas — [Criptografia e
  chaves](/docs/seguranca/criptografia), [Detecção e
  resposta](/docs/seguranca/deteccao) e [Operação e
  conformidade](/docs/seguranca/operacao) — e as três de biblioteca.
  A seção de segurança passou a **doze** páginas no sidebar.

### Corrigido — três colisões de nome entre os módulos de segurança

`test_nenhum_nome_se_repete_entre_os_modulos_de_seguranca` compara
`Seguranca`, `Politica`, `Chaves`, `Deteccao` e `Crypto` dois a dois, e
achou três:

- **`politica`** — política de *senha* contra motor de autorização. O
  novo passou a se chamar `motor`.
- **`analisar`** — as dez regras sobre um `.df` contra padrões sobre
  conteúdo qualquer. O novo passou a se chamar `varrer`.
- **`motor`** — este **não** era a mesma pergunta duas vezes: ele
  nomeia o objeto principal de dois módulos, e ninguém o chama sem o
  prefixo. Está em `COLISOES_DELIBERADAS`, que é **nomeada** de
  propósito — uma exceção genérica desligaria a trava.

### Corrigido — a trava que acusava a própria explicação

`test_nada_visivel_mostra_a_numeracao_antiga` procurava `v4.` no
arquivo inteiro, e acusou uma coordenada `v4.03` dentro de um `path`
de SVG — e depois o comentário que explicava essa armadilha. É a
terceira vez que isso acontece neste repositório (as outras: o
marcador `TODO` no lint e o `Math.random` no mapa 3D). Hoje ela ignora
comentário.

E a propriedade `chaves` do componente da landing virou `modulos`: ela
colidia com o **módulo** `Arcane.Chaves`, e o teste subtraía a palavra
— fazendo o módulo sumir da conta e acusar um agrupamento que existe.

---


### Adicionado — a seção de segurança da informação

- Onze páginas no sidebar (`/docs/seguranca/mapa` e as irmãs), cobrindo
  o currículo inteiro: tríade CIA, autenticação, autorização,
  responsabilização, não-repúdio, privilégio mínimo, defesa em
  profundidade, zero trust, seguro por desenho e por padrão, modelagem
  de ameaças (STRIDE), superfície de ataque, fronteiras de confiança e
  de segurança, gestão de risco, políticas, segurança de tipos e de
  memória, limites, ausência segura, dados imutáveis, validação,
  codificação de saída, serialização segura, senha e hashing, MFA,
  TOTP, WebAuthn, OAuth 2.0, OIDC, SAML, LDAP, JWT, tokens, sessão,
  força bruta, *credential stuffing*, bloqueio, atrasos progressivos,
  limite de taxa, detecção de segredos, linter, análise estática,
  auditoria e privacidade/LGPD.
- **Cada conceito traz o veredito.** Não existe aqui WebAuthn, passkeys,
  SAML, LDAP, Argon2id, bcrypt nem assinatura assimétrica — e cada um
  diz **por quê** e **o que usar no lugar**. Uma página que promete
  WebAuthn e não tem manda alguém construir autenticação em cima de
  algo que não está lá.
- **Os 30 blocos `.df` rodam**, e não só compilam. Cinco falharam na
  primeira passada, e os cinco eram erro meu: `cifrar` devolve Bytes,
  `jwt_verificar` devolve `{valido, carga, motivo}` em vez de levantar,
  dois `adopt` no fim do bloco, um `skip` dentro de `handle`, e
  `IO.remove` onde o nome é `IO.delete`.
- A rota `/docs/seguranca` **já tinha dono** e ficou onde estava; o mapa
  da seção é `/docs/seguranca/mapa`, seguindo a convenção de
  `/docs/partida/mapa`. Duas ferramentas escrevendo o mesmo arquivo
  fazem o resultado depender da ordem em que rodam.

### Alterado — `Crypto.hash_password` usa scrypt

- PBKDF2 só encadeia hash e é barato de acelerar em GPU. O scrypt é
  *memory-hard*: exige ~32 MB por tentativa, e memória é o que uma GPU
  não tem em abundância por núcleo.
- **`verify_password` continua aceitando o formato antigo.** Se não
  aceitasse, o dia da atualização seria o dia em que ninguém entra, e a
  saída de emergência seria mandar todo mundo redefinir a senha. O
  formato é auto-descritivo, o que torna a próxima troca barata.
- **`Crypto.precisa_rehash`** é novo: o login bem-sucedido é o **único**
  momento em que a senha em claro está disponível para regravar. Sem
  ele, um banco fica para sempre no algoritmo com que nasceu.
- `algoritmo := "pbkdf2"` volta ao anterior, para quem precisa conferir
  a senha em outro sistema.

### Adicionado — as peças locais do OAuth 2.0

- **`Seg.pkce`** (RFC 7636), **`conferir_pkce`** e **`estado_de_oauth`**.
  O fluxo inteiro é integração, não primitiva; o que cabe numa
  biblioteca é a parte criptográfica, que é onde as implementações
  erram.
- Só **`S256`**. O método `plain` manda o verificador *como* desafio, o
  que não protege de nada — quem intercepta a primeira ida já tem os
  dois. Ele existe no RFC por compatibilidade e não é oferecido aqui.

---

## 1.1.0

Primeira versão publicada no **PyPI**: `pip install dataforge-lang`.

### Adicionado — `Arcane.Seguranca`: o que se faz com a entrada de fora

- 52 símbolos. `Arcane.Crypto` tem as **primitivas** — resumo, HMAC,
  senha derivada, aleatório de verdade, ChaCha20-Poly1305, JWT — e este
  módulo as **chama** em vez de reimplementá-las. Há teste proibindo um
  nome repetido entre os dois: duas contas iguais escritas duas vezes
  divergem, e no dia em que divergirem será a de segurança que estará
  errada.
- **Escapar é por destino, nunca "em geral".** Doze: HTML, atributo,
  JavaScript, URL, shell, SQL `LIKE`, CSV, regex, cabeçalho, log, mais
  `sem_controle` e `limpar_html`. O que protege uma página não protege
  uma linha de shell, e o que protege shell estraga um CSV.
  - `escapar_csv` existe porque o Excel e o Sheets **executam** a célula
    que começa com `=`, `+`, `-` ou `@`. Um nome de usuário
    `=HYPERLINK(...)` vira link ativo na planilha de quem exportou.
  - `escapar_log` porque um `\n` num campo acrescenta uma **linha
    inteira** ao log, e a investigação seguinte lê um evento que nunca
    aconteceu.
  - `limpar_html` usa lista de **permitidos**, nunca de proibidos: a
    história do XSS é a lista dos que não pensaram em tudo.
- **TOTP e HOTP pelos vetores dos RFCs** (4226 e 6238), com teste sobre
  cada um dos dez. Uma implementação de OTP que não os reproduz está
  errada mesmo que "funcione" — o autenticador do usuário vai discordar.
  A comparação é em tempo constante, e a tolerância de janela existe
  porque o relógio do telefone anda alguns segundos fora.
- **Token e URL assinados com prazo e propósito.** Sem o propósito, o
  token que confirma um e-mail **serve para trocar a senha** — os dois
  são assinados com a mesma chave. E a assinatura é conferida **antes**
  do prazo: a data de dentro do token é dado de quem o mandou até a
  assinatura fechar. `ExpiredTokenError` é separado de `SignatureError`
  porque a resposta ao usuário é outra.
- **`Segredo`**, um valor opaco para texto, interpolação e serialização.
  Um segredo vaza em log muito mais do que em commit, e pelo caminho
  mais inocente: alguém imprime o vault inteiro para depurar. Ele não
  protege da memória — transforma um vazamento acidental numa linha
  explícita (`revelar()`) que aparece na revisão de código.
- **Varredura de segredo por formato**, e o que a faz calar custou mais
  que o que a faz falar:
  - um valor que se **anuncia** como exemplo (`"123456:AAHexemplo"` num
    exercício que *ensina* a não escrever token no arquivo);
  - **JWT com papel `anon`** — a chave `anon` do Supabase vai no pacote
    do navegador de propósito, e só o conteúdo a separa da
    `service_role`, que é comprometimento total. O papel é lido de
    dentro do próprio token;
  - credencial de `localhost` e dos domínios reservados da RFC 2606.
  - Sem esses três silêncios ela acusava **19 vezes** no repositório, e
    as 19 eram falso alarme. Uma varredura que acusa o material didático
    do próprio projeto é desligada no mesmo dia — e junto com ela vão os
    achados de verdade.
- **Entrada hostil:** `url_segura` (SSRF — resolve o nome antes de
  responder, porque `localtest.me` resolve para `127.0.0.1` e quem ataca
  controla o DNS dele), `caminho_seguro` (`realpath` antes de comparar),
  `redirecionamento_seguro`, `json_seguro` (profundidade e tamanho),
  `nome_de_arquivo_seguro` (inclusive os nomes reservados do Windows e
  as marcas que invertem a leitura), `numero_seguro`.
- **`limitador`** (balde de fichas, porque janela fixa deixa gastar o
  limite duas vezes na virada) e **`tentativas`** (bloqueio que dobra).
- **`auditoria`**: uma linha por evento, cada uma com o resumo da
  anterior. Não impede editar o arquivo — nada num arquivo local impede
  —, mas `conferir()` diz em **qual** registro a cadeia quebrou. Os
  dados passam por `redigir` antes de serem gravados: uma trilha de
  auditoria é exatamente o tipo de arquivo que acaba anexado a um
  chamado.
- Família de erro **DF19xx** (7 classes), com `SecurityError` na base.
  O catálogo passou de 208 para **215**.

### Adicionado — `dataforge seguranca`

- Roda as duas varreduras sobre um projeto, e **não só sobre os `.df`**:
  lê `.env`, `.json`, `.toml`, `.yml`, `.sh`, `.ts` e `.md` também,
  porque um segredo vaza do arquivo de configuração muito mais do que do
  código. `--strict` reprova a esteira de CI, `--json` vira entrada de
  outra ferramenta, `--so=alto` esconde os médios.
- O escape `// df: permitir segredo-no-codigo` vale em **qualquer**
  arquivo, e não só num `.df`: um segredo de brinquedo mora tanto num
  teste em Python quanto num exemplo em Markdown, e sem escape ali a
  única saída é desligar a varredura inteira.

### Adicionado — a página `/roadmap`

- O mapa da linguagem em três dimensões (Three.js, carregado sob
  demanda): as **10 fases** de um arquivo, os **41 componentes** do
  ecossistema com o veredito de cada um, e os **76 módulos** agrupados.
  Clicar num ponto abre o que ele é, o que existe aqui no lugar dele, e
  por quê.
- **Os dados são gerados** (`site/scripts/gerar_roadmap.py`), de
  `Arcane.Percurso.fases()` e `Arcane.Ecossistema.componentes()` — que
  `conferir()` cobra contra o disco nas duas direções. Um mapa de
  arquitetura escrito à mão envelhece no primeiro módulo novo, e
  envelhece calado.
- Ela mostra **o que não existe** junto com o que existe, de
  `o_que_nao_existe()`. Um roadmap que só lista conquistas é propaganda
  — e escrita à mão, essa lista envelheceria exatamente no dia em que
  alguém implementasse um dos itens.
- Sete **trilhas** com 53 passos. Cada passo diz o que a pessoa sabe
  fazer depois dele, e não o que ele contém. Os destinos são conferidos:
  escrevendo-as, **8 de 36** rotas que eu "sabia" não existiam —
  `/docs/controle` e `/docs/pipeline` soam certas, e as páginas se
  chamam `/docs/condicionais` e `/docs/pipelines`.
- A rota fica no **topo**, e não na barra lateral — e há teste sobre
  isso, nas duas direções. No celular o topo some, então o menu ganhou
  a fila das rotas de topo: sem ela, `/roadmap` e `/download` não teriam
  como ser abertos num telefone.

### Corrigido

- O teste da versão chamava-se `test_versao_e_1_0_0` e afirmava o número
  exato em três lugares. O nome de um teste não pode conter o número que
  ele confere: subir de versão obrigava a **renomear a função**, e
  renomear é o que se esquece — o teste passa a reprovar o release
  correto, e a saída mais rápida é apagá-lo. Hoje ele deriva de
  `__version__`, e a lista de arquivos é de **moldes**.
- `packaging/windows/dataforge.iss` é escrito à mão, e a mensagem do
  teste mandava rodar o gerador — que não o escreve.

---

### Adicionado — `Arcane.Dominio`: DDD com as distinções cobradas

- DDD é um conjunto de **distinções**, e o valor delas está em serem
  cobradas — não em serem nomeadas. Um `blueprint` chamado `Pedido` com
  um comentário `// agregado` não impede ninguém de mexer nos itens por
  fora.
- Sete peças: `valor` (igualdade por conteúdo, imutável, com a regra
  cobrada na **criação**), `entidade` (igualdade por identidade),
  `agregado`, `evento`, `regra`, `repositorio`, `unidade` e `contexto`.
- **A invariante é cobrada na saída de cada comando.** Cobrar na entrada
  deixa o objeto quebrado quando o comando falha no meio.
- **O comando recusado é desfeito por inteiro** — estado, eventos e
  versão. Sem isso, metade da mudança fica aplicada, e a próxima leitura
  vê um agregado que nunca deveria existir; inclusive um **evento** de
  um comando que não aconteceu.
- **O evento só é publicado quando a unidade confirma.** Publicar antes
  faz o mundo reagir a um fato que a transação ainda pode desfazer: o
  e-mail sai, e o pedido não existe.
- **`por_que_nao` aponta a parte que falhou**, e não a frase inteira:
  *"maior de idade E mora no Brasil"* não diz qual das duas a pessoa
  precisa resolver — e essa frase é o que vai para a tela.

### Adicionado — `Arcane.Reativo`, e o valor que nunca existiu

- Sinal (valor com estado), derivado (preguiçoso e memorizado), efeito e
  observável (fluxo). A distinção entre **valor** e **fluxo** é mantida
  de propósito: frameworks que chamam os dois de "stream" fazem a
  pergunta *"qual é o valor agora?"* deixar de ter resposta.
- **A propagação tem duas fases.** Num losango — `c` lê `a` e `b`, e `b`
  lê `a` — marcar e avisar numa fase só entregava `[3, 7, 15]` onde o
  certo é `[3, 15]`: o **7** era `5 + o b antigo`, um valor que nunca foi
  verdade. E a lista de dependentes é um conjunto, então qual caminho
  vem primeiro não era escolhido por ninguém.
- **O aviso pertence à propagação, e não ao recálculo.** Avisar de
  dentro do `_calcular` fazia uma simples **leitura** disparar efeito de
  terceiros.
- **`lote` montava uma lista de adiados que ninguém lia** — o gancho era
  escrito num `threading.local` e nenhum caminho de escrita o
  consultava. Três escritas davam três notificações, exatamente como sem
  ele.
- **`observar` num derivado nunca lido** registrava a ação num objeto que
  jamais seria avisado: as dependências nascem da **execução**, e um
  derivado que ninguém leu não está ligado a fonte nenhuma.
- **Um derivado não pode escrever** (`ReactiveWriteError`): a fórmula é
  lida para descobrir de que ela depende, e escrever de dentro dela faz
  a propagação correr no meio da própria descoberta. Um **efeito**
  escrevendo continua legítimo.

### Adicionado — `Arcane.Estrutura`: layout binário com nome

- Fica entre `Arcane.Bytes` (empacota por **formato**, e o resultado é
  posicional) e `Arcane.C` (estrutura e ponteiro de verdade, e exige
  **FFI**). Ler o cabeçalho de um PNG não deveria precisar de `ctypes`.
- **A ordem dos bytes é obrigatória** e o **alinhamento é conferido** —
  inclusive o do registro inteiro, senão um cluster deles sai torto a
  partir do segundo.
- **A janela não copia**: copiar um registro de 4 KB para ler um campo de
  2 bytes é o que faz um parser de arquivo grande levar minutos.
- **A faixa vem do tipo declarado**: *"um u8 vai de 0 a 255"*, e não
  `'B' format requires 0 <= number <= 255` — quem escreveu `u8` não tem
  como ligar uma coisa à outra.
- **O ponteiro segura o bloco.** A referência fraca fazia
  `Est.ponteiro(Est.bloco(8), "u32")` nascer pendurado; num mundo com
  coletor a memória nunca esteve em risco, e o que se protege é o
  **protocolo** — que tem um ponto só: `liberar()`.

### Adicionado — `IO.read_bytes`, `write_bytes` e `append_bytes`

- A linguagem sabia **produzir** bytes — `Bytes`, `Estrutura`, `Crypto`
  — e não sabia gravá-los. `IO.write` abre em modo texto com UTF-8:
  passar bytes levanta, e passar o texto de um `para_texto` **corrompe**
  o que não for texto válido.
- `write_bytes` aceita bytes, um `Bloco`, um cluster de números ou um
  texto — obrigar a lembrar de `.bytes()` é a forma mais rápida de
  gravar a representação em texto de um objeto no lugar do conteúdo.

### Adicionado — `repr`, e o `__repr__` que era inalcançável

- `__repr__` estava na lista de mágicos, na referência e na doc de OOP,
  e a linguagem não tinha como pedi-lo: não havia `repr`, e um cluster
  de objetos imprime com `__str__`. Ele só era alcançado como
  **reserva**, quando não havia `__str__` — exatamente quando não se
  queria a distinção.
- `str("oi  ")` é `oi  `; `repr("oi  ")` é `"oi  "`. Num log, a segunda
  forma mostra o espaço que sobrou no fim.

### Adicionado — `Arcane.Regex`: quatro recursos que eram inalcançáveis

- **Grupos nomeados chegam ao resultado.** `(?P<ano>…)` compilava e o
  valor vinha **por posição** — ninguém escreve isso para depois ler
  `groups[2]`. `named`, `findnamed` e `group_names` completam o
  conjunto, e `groups` continua onde estava.
- **`fullmatch` e `is_exactly`**: `match` ancora só no começo, e validar
  com ele aceita lixo no fim, calado.
- **`sub_with` troca calculando**, com a ação recebendo o mesmo vault de
  `search`; devolver `void` não troca.
- **`explain` lê o padrão em português** e **`risk` acusa os quatro
  desenhos clássicos** de retrocesso catastrófico — dizendo que é uma
  leitura de **forma**, e não uma prova.
- **O objeto de `compile` tinha cinco operações**, na forma que a doc
  recomenda para um laço: quem compilava perdia `finditer`, os grupos
  nomeados, `fullmatch`, `split` e a contagem.

### Adicionado — três famílias de erro

- `DF16xx` domínio, `DF17xx` reativo e `DF18xx` memória estruturada.
  Cada base (`DomainError`, `ReactiveError`, `LayoutError`) pega a
  família, e cada peça levanta a sua — levantar `RuntimeError` em tudo
  faz a distinção morrer na fronteira do `handle`.

### Corrigido — cinco defeitos do interpretador

- **`obj.metodo()` chamava `obj()`** quando o receptor era chamável: o
  ramo de despacho ignorava o nome do método. Não havia erro — o valor
  errado seguia adiante, e a queixa saía uma linha abaixo, sobre outra
  coisa.
- **`handle <Nome>` não casava um record levantado.**
  `_error_matches` consultava `tipo_usuario` e **nada** o escrevia: o
  ramo existia, tinha docstring, e era inalcançável.
- **Um objeto de fora não podia responder à escrita de membro.**
  `valor.campo := x` dava `Cannot set a member on a Valor` — verdade, e
  sem nenhuma saída. A leitura já era por protocolo.
- **O `check` acusava `-obj` num blueprint com `__neg__`.** Um falso
  alarme sobre um recurso que a própria referência documenta ensina a
  ignorar o analisador.
- **O `lint` acusava `TODO` em português.** Este repositório escreve
  palavra em MAIÚSCULA para enfatizar, e *"TODO objeto que declara
  tamanho"* virava pendência; e um `TODO:` **dentro de um texto** — o
  exemplo de um exercício que demonstra um lint — também.

### Corrigido — duas superfícies para o mesmo conceito

- **`ctx.estado` do Telegram devolvia uma cópia.**
  `ctx.estado["k"] := v` escrevia num dicionário descartável e a mudança
  sumia — sem erro, sem aviso, e com a documentação prometendo
  *"sobrevive entre mensagens"*. Hoje é uma **vista** que lê e grava
  através do armazém.
- **`V.estado["n"] := 1` era erro** na Vitrine: o objeto tinha `obter` e
  `definir` e nenhuma das duas formas naturais. Os dois têm a forma de
  vault agora, e os nomes de sempre continuam.
- **O dublê do Telegram era mais estreito que o original.**
  `BotFalso.responder_inline` aceitava `**kw` — por **nome**, e não por
  **posição**. Uma chamada posicional funcionava em produção e estourava
  no teste.
- **`ctx.responder_consulta` não existia**: era a única resposta que
  caía no bot cru, com o id da consulta à mão — que é exatamente o que
  se esquece.

### Adicionado — 120 exercícios, e as páginas da biblioteca

- Oito módulos novos (50–57): domínio, reativo, estruturas, regex
  avançado, erros, métodos mágicos, Telegram e Vitrine. São **387**
  exercícios em 57 módulos, cada um com `assert` e com um `.md` ao lado.
- **As páginas de `/docs/biblioteca/<modulo>` eram uma cópia à mão**: a
  de `Arcane.Regex` anunciava *"Funções (28)"* onde havia 44 — e a
  contagem estava no **título**. E 32 dos 75 módulos não tinham página
  nenhuma. Agora a tabela sai do próprio módulo, e o que foi escrito à
  mão mora fora do arquivo gerado.


### Adicionado — `Arcane.Abi`: a superfície é o contrato

- **Quebrar a superfície de um módulo é o mesmo problema que quebrar uma
  ABI**, com outro nome e o mesmo sintoma cruel: não é erro de
  compilação de quem publicou — o módulo novo compila, os testes passam,
  o pacote sobe — e o erro acontece na máquina de **quem consome**,
  depois, no dia da atualização.
- O gerenciador de pacotes já tinha semver, `forge.lock` e verificação
  de integridade. **Faltava o que decide o número**: nada conferia se a
  versão nova quebra a anterior, e o bump era escolhido a olho.
- `dataforge abi antes.df depois.df` compara duas versões e devolve o
  veredito que a mudança **exige**: `maior`, `menor` ou `correcao`. Sai
  com **2** quando quebra, para reprovar no CI.
- **Onze regras nomeadas**, cada uma com o porquê e o que fazer:
  `simbolo-removido`, `especie-trocada`, `aridade-incompativel`,
  `parametro-renomeado`, `tipo-de-parametro`, `retorno-trocado`,
  `campo-removido` — e as compatíveis `simbolo-novo`,
  `parametro-opcional-novo`, `campo-novo-opcional`.
- **`parametro-renomeado` é a regra que uma ferramenta feita para C não
  precisaria ter**: aqui a chamada com nome existe (`somar(a := 1)`),
  então o nome do parâmetro é contrato e não só a posição.
- **Um terceiro balde para o que a superfície não decide.** Acrescentar
  campo a um `record` quebra *se* ele não tiver padrão — e a superfície
  lê a declaração sem executá-la, então não sabe qual dos dois é.
  Acusar reprovaria um release correto; calar deixaria passar um que
  quebra. `campo-novo-em-record` aparece em destaque e não reprova;
  `--estrito` o trata como quebra.
- **Uma superfície que não compila não julga**: devolve `desconhecido`
  com o motivo. Um falso alarme aqui desliga a conferência inteira.
- **`Abi.mapa`** — de onde vem cada nome: `modulo`, `local`, `embutido`
  ou **`desconhecido`**. É o análogo do mapa que um ligador escreve, e a
  linha `desconhecido` é a que paga a ferramenta.

### Adicionado — `Arcane.Alvo`: onde este programa roda

- `dataforge alvo app.df --alvo=navegador` responde a partir dos
  `adopt`. **Seis alvos**: `servidor`, `cli`, `navegador`, `wasi`,
  `funcao` (serverless) e `embarcado`.
- **Cada ausência vem com o motivo**, e não só com um `não`: threads no
  navegador dependem de `SharedArrayBuffer` e de isolamento de origem;
  soquete cru não existe numa aba; o WASI não tem `fork`.
- **O vocabulário é o mesmo** de `Arcane.Capacidade`: lá as capacidades
  são cobradas em execução, aqui são lidas antes de rodar. Dois
  vocabulários divergiriam no primeiro módulo novo.
- **O limite está dito em voz alta**, e `Alvo.limites()` o devolve em
  execução: a leitura é **estática**, de um arquivo; um módulo alcançado
  indiretamente não aparece; e um `roda` quer dizer "não achei
  impedimento por esta via", não "vai funcionar".
- **WebAssembly, com precisão**: *compilar para* WASM **não existe**;
  *rodar em* WASM **funciona**, pelo Pyodide — é rodar o CPython em
  WebAssembly, e o interpretador inteiro vai junto. A página separa as
  duas frases, porque a diferença aparece no tamanho do artefato.
- Documentação:
  [`/docs/abi/superficie`](https://dataforge-lang.vercel.app/docs/abi/superficie),
  `/compatibilidade`, `/simbolos`, `/docs/alvos/portabilidade`,
  `/docs/alvos/wasm` e o mapa das partes 18 e 19; exercício 265.

### Adicionado — `Arcane.Inicio`: o que roda antes da primeira linha

- **As sete fases da partida**, nomeadas e em ordem (`lexer`, `parser`,
  `comptime`, `hoisting`, `adopt`, `programa`, `defer`), cada uma com o
  que faz escrito ao lado — uma lista de nomes sem explicação apodrece.
- **Cada `adopt` é cronometrado.** Era a única forma de responder "por
  que a partida demora 400 ms?" sem cronometrar à mão. A medida é
  **sempre ligada**: são dois floats por import, num lugar que roda uma
  vez, e ligá-la por opção a faria existir só para quem já desconfiava.
- **Uma variável por thread com inicialização e finalizador.**
  `threading.local` dá o armazém e não dá o resto — sem finalizador, uma
  conexão aberta por thread fica aberta depois que ela morre, e o
  sintoma aparece no servidor, não no código. `inicial` é uma **ação que
  constrói** o valor, e passar um valor é recusado: um valor seria
  compartilhado por todas as threads, que é o que a variável existe para
  evitar.
- **A pilha se pergunta**: `I.pilha()` (profundidade, teto, quanto
  falta), `I.quadros()` (quem chamou quem) e `I.limite_da_pilha()`.
  Baixar o teto vale de verdade; **subir é recusado** além do que o
  Python aguenta — cada chamada desta linguagem gasta vários quadros do
  CPython, e um teto alto demais troca uma mensagem clara por um
  `RecursionError` cru que não fala desta linguagem.

### Adicionado — `Arcane.Capacidade`: a fronteira de autoridade

- O `comptime` já recusava `out`, `adopt` e `thread`: era uma fronteira
  escrita à mão, para um caso só. E o `--plugin=` roda um `.df`
  arbitrário do projeto com **todos** os poderes.
- `Cap.executar(acao, permissoes)` recusa o `adopt` de um módulo fora da
  lista **pelo nome da capacidade que falta**. Oito capacidades:
  `arquivos`, `rede`, `processo`, `banco`, `threads`, `nativo`,
  `python`, `ambiente`.
- **A ponte para o Python é capacidade própria**, e nunca vem junto: ela
  alcança tudo o que o Python alcança, e deixá-la com outra faria o
  resto da lista virar enfeite.
- Um nome inventado é **recusado com a lista** — um erro de digitação
  concederia silenciosamente nada, e a fronteira pareceria mais aberta.
- `Cap.observar` responde "de que esta ação precisa?": rode sem nada e
  leia os negados.
- **O limite está escrito em voz alta**, e `Cap.limites()` o devolve em
  execução: **não é caixa contra programa hostil**; ele bloqueia a
  autoridade **ambiente** e **não tira o que foi ENTREGUE** — o que é o
  modelo de capacidade, não um defeito. Um módulo chamado *Sandbox* que
  prometesse contenção seria usado onde não pode, e a descoberta viria
  por incidente.
- Documentação:
  [`/docs/partida/inicio`](https://dataforge-lang.vercel.app/docs/partida/inicio),
  `/por-thread`, `/pilha`, `/docs/seguranca/capacidade`, o mapa das
  partes 13 e 15, e **o mapa de hardware** (partes 9, 14 e 16 — todas
  "não se aplica", com o porquê de cada uma); exercício 264.

### Adicionado — `Arcane.Perfil`: percentis, significância e regressão

- **A média esconde o que o usuário sente.** Cem requisições de 10 ms e
  uma de 1000 ms dão média 20 ms; `Arcane.Bench` respondia só isso.
  `P.medir` devolve a distribuição: `p50`, `p90`, `p95`, `p99`, `p999`,
  `min`, `max`, `desvio` e `vazao`, com o **aquecimento separado e
  declarado** — as primeiras execuções medem a partida, não o programa.
- **O percentil sai da amostra por posto**, sem interpolar: interpolar
  inventa um valor que não aconteceu, e num P99 de latência o que se
  quer é uma medida que existiu.
- **`P.comparar` com significância estatística.** Comparar uma ação com
  ela mesma **não pode** dar "3% mais rápida" — é o que separa medição
  de superstição, e é o primeiro teste do arquivo. A conta é
  **Mann-Whitney U** (com correção de empates), e **não** o teste t:
  tempo de execução não é normal, e um teste que supõe normalidade
  responde com confiança sobre uma suposição falsa. As duas medições são
  **intercaladas**, senão uma queda de clock no meio vira "B é mais
  lenta".
- **`sobreposicao`**: o `p` diz *se* há diferença; ela diz **quanto**.
- **Regressão contra linha de base** (`P.guardar`/`P.conferir`), com duas
  escolhas que mantêm o CI utilizável: **a primeira medida nunca
  reprova** (um CI que nasce vermelho por desenho é desligado), e a
  **tolerância é obrigatória** (sem ela, todo CI fica vermelho por ruído
  de máquina).
- **Flame graph das AÇÕES**, pelo mesmo gancho do `dataforge profile`,
  por tempo **próprio** — somar o acumulado daria mais de 100%.
  `P.chama_svg` sai **sem nada de fora** (a regra da Vitrine) e
  `P.chama_texto` no formato dobrado que o `flamegraph.pl` consome.
- **`P.gc_pausas`**: a pausa do coletor é o que transforma um P50 bom num
  P99 ruim, e não aparece em medida que olhe só o tempo total.
- **`P.trava`**: contenção **não aparece num perfil de CPU** — a thread
  bloqueada não gasta CPU nenhuma. A distinção entre "peguei na hora" e
  "esperei" vem de uma tentativa sem bloqueio antes da aquisição real.

### Adicionado — o coletor sob controle, e a arena

- **A distinção que quase todo mundo erra**: no CPython quem libera é a
  contagem de referência, e ela roda na hora; o **coletor** existe só
  para o **ciclo**. Desligá-lo **não vaza memória em geral** — só deixa
  o ciclo para trás, e é por isso que a técnica é segura num trecho curto.
- **`Mem.sem_gc`** religa **mesmo se o corpo falhar**: deixar o coletor
  desligado por causa de um erro é pior que a pausa que se queria evitar.
- `Mem.gc_ligar/gc_desligar/gc_ligado`, `gc_limiares` (os três, lidos e
  ajustados), `gc_congelar` (tira o que já vive das varreduras — o que um
  servidor faz antes do primeiro pedido) e `gc_geracoes`.
- **A afirmação é medida**: 6000 ciclos alocados dão 3 pausas e 1,84 ms
  com o coletor ligado, e **0 pausas** com ele desligado.
- **`Mem.arena`** — não é um allocator (quem aloca é o CPython): é o
  **padrão de uso** que muda. Ela **cresce e conta** quando acaba (travar
  seria pior, crescer calado esconderia o dimensionamento), **recusa**
  devolver o que não veio dela, e `limpar` solta o lote numa chamada.
- Documentação:
  [`/docs/observabilidade/perfil`](https://dataforge-lang.vercel.app/docs/observabilidade/perfil),
  `/comparar`, `/chamadas`, `/docs/memoria/coletor` e o mapa das partes
  17, 10 e 11; exercício 263.

### Adicionado — `Arcane.Laco`: laço de eventos, escalonador e fibras

- **O modelo que faltava.** `async/await` é **uma thread por tarefa**, e
  o Kiln atende **um pedido por thread**: serve para sobrepor E/S, e não
  escala. `Arcane.Laco` é o reator — **uma** thread dormindo no seletor
  do sistema (`epoll` no Linux, `kqueue` no macOS e BSD, `select` no
  Windows) e acordando quando um descritor tem trabalho.
- **O número, medido**: 2000 conexões simultâneas atendidas por **uma**
  thread com **+0 MB**, contra 2000 threads e **+36 MB**. O tempo quase
  empata (~1,1×) — o que muda é a **forma da conta**: o custo do laço é
  plano, o do modelo de threads é linear (~36 KB por thread). O 1,1× está
  publicado: esconder o caso em que os dois empatam seria escolher a
  medida que favorece.
- **Não gira em vão**, e há teste: com um temporizador a 200 ms, menos de
  50 voltas. Espera ocupada daria milhões.
- **Escalonador**: `agendar` (FIFO), `apos` e `a_cada` (heap de prazos,
  com desempate estável), `cancelar` para tarefa e fibra, e
  **contrapressão** por teto opcional — sem teto, uma fonte mais rápida
  que o consumo troca falha visível por morte por memória.
- **`L.executar`** manda o que bloqueia para um pool e devolve pela fila.
  Sem isso, um `sleep` dentro do laço trava **toda** conexão aberta. E
  `agendar` de outra thread **acorda** o laço por autocano
  (*socketpair*): um seletor acorda por descritor, e uma fila em memória
  não é um descritor.
- **Um erro num retorno de chamada não derruba o laço** — é contado,
  guardado com tipo e texto, e o laço segue. Um reator que morre no
  primeiro erro derruba o servidor inteiro por causa de **uma** conexão.
- **Fibras de verdade, sobre máquina que já existia.** Um `stream
  action` já é um gerador do Python que o interpretador suspende em cada
  `emit`: é esse o ponto de parada, e a troca de contexto é o quadro do
  gerador. Duas fibras cedendo produzem `A1 B1 A2 B2 A3 B3` — se fossem
  sequenciais seria `A1 A2 A3 B1 B2 B3`.
- **Sem pilha, e com esse nome**: um `emit` dentro de uma ação
  **chamada** não suspende a fibra. É a limitação de toda corrotina
  *stackless*, e é por isso que a doc diz **fibra** e não *green thread*.
  Como `emit` é instrução e não expressão, o laço entrega pela **caixa**
  — um vault que a fibra passou.
- Não existem, e está dito com o motivo: *work stealing* (o GIL come o
  ganho), `io_uring` (exigiria extensão em C), IOCP (no Windows o
  `selectors` usa `select`, com teto de 512 descritores).
- Documentação:
  [`/docs/runtime/laco`](https://dataforge-lang.vercel.app/docs/runtime/laco),
  `/escalonador`, `/fibras` e o mapa da parte 12; exercício 262.

### Adicionado — SSA, propagação condicional, e a otimização **medida**

- **`ssa.py`**: dominância, dominador imediato, fronteira de dominância e
  nó **φ**. Cada nome é numerado, cada versão tem exatamente uma
  definição, e cada leitura diz **qual** versão está lendo — a pergunta
  que o MIR sozinho não responde. As instruções **não** são reescritas
  em três endereços: a versão é anexada, porque reescrever criaria uma
  segunda semântica para manter em sincronia com o interpretador.
- **Propagação condicional de constante**: ela **não avalia** o ramo cuja
  condição prova falsa, e por isso a junção conclui o que a propagação
  sobre o MIR perde. Há teste rodando as duas análises sobre o mesmo
  programa — sem ele, "mais forte" seria só uma afirmação.
- **`ramo-morto`** no `check`: o ramo cuja condição se **prova** falsa. A
  prova vem do SSA, e não de olhar o literal — `limite := 5` seguido de
  `given limite bigger 10` é a forma que aparece em código de verdade.
  Dois silêncios **medidos**: `persist yes:` com `halt` é o laço infinito
  legítimo (sem essa exceção, 29 acusações no repositório, todas em
  generator infinito), e um `match` sobre valor constante não diz qual
  `point` casa.
- **`otimizar.py`** — três passes sobre o HIR: `dobra-de-constante`,
  `ramo-morto` e `inalcancavel`. Nada que possa falhar é dobrado: `1 / 0`
  moveria o erro para a **carga**, `"a" + 1` mudaria a mensagem,
  `2 ** 1000000` montaria meio milhão de dígitos no carregamento.
- **Dez nós novos no compilador de fechamentos**, escolhidos pelo
  inventário do LIR e não por intuição: `UnaryOp`, `MembershipOp`,
  `TernaryExpression`, `CoalesceOp`, `TypeofExpression`, `SliceAccess`,
  `SteadyDeclaration`, `AssertStatement`, `HaltStatement`,
  `SkipStatement` — mais `v["k"] := x`, que era o alvo que mais recuava
  dentro de laço. Três auxiliares (`_aplicar_unario`, `_pertence`,
  `_escrever_indice`) foram **extraídos** no interpretador para que a
  semântica fosse reusada, e não copiada.
- **O resultado, medido e desconfortável**: **1,33×** numa carga feita dos
  nós que o inventário aponta, e **1,01× — nada** em 59 exercícios reais.
  O que recua é dominado por nós que rodam uma vez, e o trabalho da volta
  já estava compilado. Os passes ficam **desligados por padrão**, e o
  número está na documentação com esse nome.
- **`dataforge ir --fase=ssa|otimizado`**, e `Arcane.Compilador` ganhou
  `ssa`, `provadas`, `ramos_mortos`, `passes` e `otimizar`.
- Corrigido, de passagem: a condição da fronteira de dominância estava
  **invertida** na primeira versão (perguntava "`b` domina `atual`?" onde
  a pergunta é "`atual` é o dominador imediato de `b`?"), e produzia um φ
  em todo bloco de todo laço. E `lir.py` não contava **compreensão** nem
  **pipeline** como laço — eram os recuos que mais custavam, e estavam
  escondidos do próprio relatório que existe para achá-los.
- Não há LLVM, código de máquina, target triple nem passe em C++, e há
  uma página dizendo isso com o motivo de cada um.
- Documentação:
  [`/docs/compilador/ssa`](https://dataforge-lang.vercel.app/docs/compilador/ssa),
  `/otimizacao`, `/backend` e o mapa da parte 8; exercício 261.

### Adicionado — a arquitetura interna, exposta: HIR, MIR, LIR e `dataforge ir`

- **`dataforge ir <arquivo>`**: o caminho de compilação inteiro, fase por
  fase. `--fase=tokens|ast|hir|mir|analises|lir|tudo`, `--acao=<nome>` e
  `--json`. O repositório tinha `tokens` e `ast` — a primeira fase e a
  terceira; as quatro do meio não apareciam em lugar nenhum.
- **`hir.py` — a árvore depois do açúcar.** Cinco açúcares são abertos
  (`orif-aninhado`, `composta-simples`, `pertence-negado`,
  `perform-para-persist`, `sinal-de-literal`) e **oito formas que só
  parecem** estão listadas com o motivo ao lado — `cycle from..to` não
  vira `range` porque `range` materializa a lista; `a ?? b` avaliaria o
  lado esquerdo duas vezes; `mark @f` não é `g := f(g)` porque um
  decorador que devolve `void` não substitui o alvo. A prova da
  normalização não é a forma da árvore: exercícios do repositório rodam
  nas duas formas e a **saída** é comparada caractere por caractere.
  `hir.resolucao` diz, por corpo, o que é parâmetro, local, livre e
  embutido.
- **`mir.py` — o grafo de fluxo.** Um corpo por ação (mais `(programa)` e
  uma por rota do Kiln), blocos básicos e arestas rotuladas (`sim`,
  `nao`, `volta`, `halt`, `skip`, `erro`, `point`, `default`, `defer`).
  Três decisões: ele é construído **a partir do HIR** (é o que paga a
  normalização); a aresta de erro sai da **entrada** do `monitor`, para a
  análise ver o pior caso honesto; e o que roda fora da ordem
  (`thread`, `parallel`, `server`) é **opaco**, porque abrir o corpo num
  grafo sequencial afirmaria uma ordem que não existe.
- **Cinco análises de fluxo**: `alcancaveis`, `vivas`,
  `talvez_nao_definidas`, `constantes` (com interseção: dois ramos que
  discordam não deixam constante) e `escapam` (`devolvido`,
  `fechamento`, `concorrente`, `guardado`).
- **`talvez-nao-definida`** — o aviso que o `check` não sabia dar: o nome
  que **só um ramo** atribui. O analisador registrava o nome do ramo, e
  isso está certo — `given` compartilha o escopo —, mas não contava por
  quantos caminhos ele passa. O laço conta como ramo: ele pode não rodar
  nenhuma vez. Cala com `monitor`, `defer`, fechamento, bloco opaco, e
  quando o nome existe **fora** — `:=` dentro de uma ação escreve o nome
  externo quando ele existe, e sem essa regra os nove contadores por
  fechamento do repositório seriam acusados. **Zero falso alarme** nos
  387 arquivos do repositório.
- **`lir.py`** — o que o compilador de fechamentos **realmente**
  compilou, e o que recuou para a árvore, por classe de nó, com os
  recuos **dentro de laço** em separado (os únicos que aparecem num
  perfil). A conta sai das tabelas do próprio `compilador.py`; uma
  segunda lista divergiria no primeiro nó novo.
- **`Arcane.Compilador`**: as mesmas fases como **dado**, de dentro da
  linguagem — o que permite a um [plugin do
  `check`](https://dataforge-lang.vercel.app/docs/metaprogramacao/plugins)
  perguntar coisas de **fluxo**, e não só de forma. `Arcane.Macro` para
  na árvore.
- Não há fase de código de máquina, e nada finge que há: `--fase=llvm` é
  recusado com a lista e com o motivo.
- Documentação:
  [`/docs/compilador/pipeline`](https://dataforge-lang.vercel.app/docs/compilador/pipeline),
  `/hir`, `/mir`, `/analises` e o mapa da parte 7; exercício 260.

### Adicionado — `Arcane.C`: falar com biblioteca nativa

- **Chamar C**: `C.carregar(nome)`, `C.padrao()`, `C.matematica()`,
  `C.do_processo()` abrem `.so`, `.dylib` e `.dll`; `lib.funcao(nome,
  [tipos], retorno)` declara a assinatura e devolve uma ação chamável.
  Roda sobre o `ctypes`, que é da biblioteca padrão do Python — **zero
  dependência continua valendo**. `adopt Python.numpy` resolvia "uma
  biblioteca escrita em Python"; faltava o degrau de baixo.
- **A assinatura é declarada, não adivinhada.** A lista de tipos é
  fechada (`i8`…`i64`, `u8`…`u64`, `f32`, `f64`, `bool`, `char`, `texto`,
  `bytes`, `ponteiro`, `tamanho`, `void`) e um tipo inventado é recusado
  **com a lista**. Um `i32` onde o C espera `i64` passa em quase toda
  chamada e corrompe memória no resto — calado, e longe da causa.
- **Layout de verdade**: `C.estrutura`, `C.uniao` e `C.enumeracao` dão
  `tamanho()`, `alinhamento()` e `deslocamentos()` pela ABI da
  plataforma — inclusive o padding (um `i8` antes de um `i32` ocupa 8, não
  5). `C.tamanho_de`, `C.alinhamento_de`, `C.endianness`, `C.tipos`.
- **Ponteiro cru é um endereço COM TIPO**: `C.ponteiro(alvo, tipo)`,
  `ler`, `escrever`, `deslocar(n)` (itens), `deslocar_bytes(n)`,
  `como(tipo)`, `bytes(n)`, `texto()`, `e_nulo()`. Memória à mão com
  `C.alocar`, `C.liberar`, `C.copiar`, `C.de_bytes`, `C.para_bytes`.
  A **única** conferência automática é o nulo, porque lê-lo derruba o
  processo e a pilha que sobra não fala do DataForge.
- **Callback**: `C.retorno_de_chamada(acao, [tipos], retorno)` faz o C
  chamar uma ação DataForge — testado com o `qsort` da libc ordenando
  memória crua por um comparador escrito na linguagem. O tempo de vida é
  explícito (`vivo()`, `soltar()`): um callback coletado no meio de um
  `qsort` derruba o processo.
- Os dois erros que FFI sempre tem — biblioteca que não abre e símbolo
  que não existe — dizem o nome, onde foi procurado e o caminho de saída
  por sistema operacional, em vez do `OSError: dlopen(…)` cru.
- Documentação: [`/docs/ffi/c`](https://dataforge-lang.vercel.app/docs/ffi/c),
  `/ponteiros`, `/callbacks` e o mapa da parte 6; exercício 259.

### Adicionado — metaprogramação: `comptime`, macros, DSLs e plugins do `check`

- **`comptime`**: a conta feita **na carga**, antes da primeira linha do
  programa, e congelada. Tabela de consulta gerada, constante calculada e
  `assert` que vira trava de build — o `dataforge check` o executa e
  acusa com `comptime-falhou`. O corpo roda numa **caixa**: `out`,
  `adopt`, `thread` e `parallel` são recusados com o motivo, senão
  "tempo de compilação" seria só "mais cedo". A palavra é contextual:
  `comptime := 3` continua valendo.
- **`Arcane.Macro`**: a árvore como **dado**. `arvore`, `citar`, `texto`,
  `percorrer`, `transformar`, `substituir`, `renomear`, `nome_fresco`,
  `acao`, `compilar`, `reescrever` — e `derivar`, a macro de atributo
  que gera `__str__`, `__eq__`, `__lt__` e `para_vault` a partir dos
  campos. A expansão roda na carga, e a higiene é explícita.
- **`Arcane.Dsl`**: combinadores para uma linguagem externa própria, com
  `analisar` devolvendo `Resultado` e a falha dizendo posição, esperado e
  trecho.
- **Plugins do `check`**: um `.df` com `verificar(arvore, arquivo)`,
  passado por `--plugin=` ou declarado em `forge.toml` (`[check] plugins`).
  O código da regra aparece na mensagem, `// df: permitir <codigo>`
  silencia, e um plugin quebrado vira **diagnóstico** — não traceback.
- Documentação: [`/docs/metaprogramacao/comptime`](https://dataforge-lang.vercel.app/docs/metaprogramacao/comptime),
  `/macros`, `/dsl`, `/plugins` e o mapa da parte 5; exercício 258.

### Adicionado — `Arcane.Stm`, atômicos com CAS e estruturas sem trava

- **`Arcane.Stm`**: memória transacional. `variavel` e `atomicamente`,
  com validação otimista e repetição no conflito; erro no meio desfaz o
  rascunho e **sobe**; a transação lê a própria escrita; aninhar é
  achatar, e é isso que permite **compor** duas operações transacionais
  numa terceira — o que o mutex não dá. `retentar()` dorme até uma
  variável lida mudar, e `ou_entao` tenta a segunda quando a primeira
  pede para esperar. `estatisticas()` mostra confirmadas, conflitos e
  esperas.
- **`C.atomico(v)`**: `comparar_e_trocar` (CAS), `trocar`, `somar`,
  `pegar_e_somar`, `atualizar` — a peça com que se escreve um contador
  sem trava.
- **`C.fila_sem_trava()`, `C.pilha_sem_trava()`, `C.anel(n)`**:
  estruturas cujo caminho comum não pega trava (o `append`/`popleft` do
  `deque` acontece inteiro em C). O anel descarta o **mais velho** ao
  encher.
- **`C.executor(n)`** (pool que fica de pé) e **`C.promessa()`** (o
  resultado que alguém vai cumprir, com falha que chega a quem espera).
- Documentação: [`/docs/concorrencia/stm`](https://dataforge-lang.vercel.app/docs/concorrencia/stm),
  [`/docs/concorrencia/sem-trava`](https://dataforge-lang.vercel.app/docs/concorrencia/sem-trava),
  o mapa em [`/docs/concorrencia/mapa`](https://dataforge-lang.vercel.app/docs/concorrencia/mapa)
  e o exercício 257.

### Adicionado — `Arcane.Posse`: posse, empréstimo e liberação determinística

- **`P.dono(valor, ao_soltar)`**: um dono, um finalizador, uma vez.
  `soltar()` roda **agora** — e não quando o coletor decidir passar;
  `P.com(dono, acao)` solta no fim, **inclusive quando o corpo falha**,
  que é o caminho por onde metade dos recursos vaza.
- **`mover()`**: quem move, perde. Usar depois é erro em execução, e o
  `check` acusa antes (`posse-movida`) quando o fluxo do arquivo prova.
  `copiar()` (mesmo valor) e `clonar()` (cópia) são coisas diferentes.
- **`P.celula`**: muitos leem **ou** um escreve — a regra do borrow
  checker, cobrada quando roda. O empréstimo vive no corpo que o
  recebeu, e pedi-lo fora dele devolve um empréstimo já encerrado.
- **`P.compartilhado` e `P.atomico`**: contagem determinística — o
  finalizador roda quando o **último** dono sai. O segundo vale entre
  threads.
- **`P.fraco`**: observa sem segurar, e responde `Talvez`. Um ciclo de
  referências fortes vaza, e isso é **mostrado** em vez de escondido; a
  saída é a de sempre, e está documentada.
- Quem solta, solta o que possuía (*drop glue*).
- **`Mem.layout` e `Mem.comparar_layout`**: o custo de um objeto,
  medido em objetos de verdade — `slots` contra dicionário.
- Documentação: [`/docs/memoria/posse`](https://dataforge-lang.vercel.app/docs/memoria/posse),
  [`/docs/memoria/layout`](https://dataforge-lang.vercel.app/docs/memoria/layout)
  e o exercício 256.

### Adicionado — `Arcane.Resultado` e `Arcane.Tipos`

- **`Arcane.Resultado`**: a falha como **valor**, que é a terceira forma
  que faltava ao lado de `monitor`/`trigger` (o inesperado) e de `void`
  com `??` (a ausência). `R.ok`/`R.falha`, com `mapear`, `entao`,
  `recuperar`, `ou`, `exigir`, `R.tentar` (que captura o erro da
  linguagem e **deixa passar** sinal de controle) e `R.todos` (a lista
  pronta, ou o primeiro motivo). Ler `valor()` de uma falha levanta,
  porque ali quem escreveu afirmou.
- **`Talvez`** (`algo`/`nada`/`chave`/`primeiro`), para onde `void` é
  ambíguo: distinguir "a chave não está lá" de "a chave vale void".
- **`Arcane.Tipos`**: reflexão sobre tipos. Os metadados de um `type`
  declarado (`especie`, `base`, `partes`, `regra`, `opaco`),
  `satisfaz` (confere e responde, sem levantar), `conferir` (levanta o
  erro de sempre), `forma` — a forma **estrutural** de um valor
  (`Cluster<Integer>`, `Tuple<Integer, String>`) — e `campos`, que dá os
  campos de um record, instância ou vault com o tipo de cada um.
- Documentação: [`/docs/tipos/resultado`](https://dataforge-lang.vercel.app/docs/tipos/resultado),
  [`/docs/tipos/reflexao`](https://dataforge-lang.vercel.app/docs/tipos/reflexao)
  e o exercício 255.

### Adicionado — tuplas

- **`(1, "a")`** é uma tupla: tamanho fixo, um tipo por casa, imutável e
  hasheável — serve como chave de vault e item de `Set`. `(1)` continua
  sendo agrupamento; `(1,)` é a tupla de um item e `()` a vazia.
- **`Tuple<A, B, …>`**: a quantidade de argumentos **é** o tamanho. A
  conferência nomeia a casa (`place 0`) e o tamanho errado é relatado como
  forma errada, na execução e no `check` (`tipo-do-conteudo`).
- É o tipo do **retorno duplo**:
  `action dividir(a, b) -> Tuple<Integer, Integer>`, com desestruturação
  (`inteiro, resto := dividir(17, 5)`).
- Ela percorre, serializa (array no JSON) e atravessa processo.
- `Tuple` e `Frozen` são coisas diferentes, e continuam sendo: `Frozen` é
  um `Cluster` congelado, `Tuple` é uma forma. `freeze([1, 2])` segue
  respondendo `Frozen`.
- Documentação: [`/docs/tipos/tuplas`](https://dataforge-lang.vercel.app/docs/tipos/tuplas),
  a visão geral em [`/docs/tipos/visao-geral`](https://dataforge-lang.vercel.app/docs/tipos/visao-geral),
  `doc/REFERENCIA.md` §3.3 e o exercício 254.

### Adicionado — generics no resto do sistema de tipos

- **`record Caixa<T>`, `enum Talvez<T>` e `trait Comparavel<T>`** passaram a
  existir: antes eram erro de sintaxe. `<T extends X>` é cobrado nas duas
  metades (o `check` na construção, com `generic-bound`, e a execução no
  valor), e o argumento chega ao **campo**: `Caixa<Integer>` recusa um texto
  lá dentro, nomeando o campo.
- **Tipos indexados**: o argumento de um genérico pode ser um **número**
  (`Vetor<3>`), e a regra do tipo o enxerga —
  `type Vetor<N> := Cluster<Float> where len(valor) is N`. O `check` prova o
  tamanho de um literal antes de rodar.
- **`trait B extends A`**: um trait herda exigências e implementações padrão.
  A mensagem de quem não implementa nomeia quem **declarou** a exigência, e
  não quem a repassou.
- **Tipo associado e constante associada** em trait: `type Item := Any` e
  `steady LIMITE := 3`. Quem implementa preenche o tipo, e ele vale como
  anotação (`-> Item`) e como membro (`Fila.Item`).
- Documentação: [`/docs/tipos/genericos`](https://dataforge-lang.vercel.app/docs/tipos/genericos),
  [`/docs/tipos/traits`](https://dataforge-lang.vercel.app/docs/tipos/traits),
  `doc/REFERENCIA.md` §7.4 e o exercício 253.

### Corrigido

- Uma coleção tipada por **parâmetro de tipo** deixou de guardar:
  `blueprint Pilha<T>` com `itens: Cluster<T> := []` recusava `append(1)` —
  o genérico não servia para o único uso que ele tem.
- O formatador não espaça mais o genérico de uma **declaração**:
  `action f<T>(x)` e `record Par<A, B>` saíam como `action f < T > (x)`.
- `self.campo` de um campo `T extends Number` conta como `Number` dentro da
  declaração: `self.quanto * 2` acusava "Cannot multiply T by Integer".

### Adicionado — `type`: o sistema de tipos nomeados

- **`type Nome := …`** em cinco formas: alias (`Integer`), alias genérico
  (`Par<T> := Cluster<T>`), união (`String | Integer | Void`), interseção
  (`Serial & Ordenavel`) e refinamento (`Integer where valor bigger 0`).
  A união e a interseção também valem direto na anotação, sem nome.
- **`opaque type Cpf := String where len(valor) is 11`** — o tipo
  **nominal**: só nasce por `Cpf(…)`, que valida; um texto com onze
  dígitos não serve no lugar. O valor delega por protocolo (texto,
  igualdade, ordem, hash, conta, tamanho, índice) e `.valor` desembrulha.
- A regra de um refinamento é conferida em **toda fronteira**: declaração,
  parâmetro, retorno e campo — e a base é conferida antes dela.
- O `check` prova o que um literal permite, com códigos próprios:
  `tipo-refinado`, `tipo-uniao`, `tipo-intersecao`, `tipo-opaco`,
  `tipo-circular`, mais `declaracao-repetida` e `unknown-type` com
  sugestão. A prova roda num avaliador puro, com lista fechada de funções.
- `relay Positivo, Cpf` exporta um tipo; o outro arquivo escreve
  `T.Positivo`.
- `type`, `opaque` e `where` são **contextuais**: `type := 3` continua
  valendo. O editor, o site e o LSP as conhecem.
- Documentação: [`/docs/tipos-nomeados`](https://dataforge-lang.vercel.app/docs/tipos-nomeados),
  `doc/REFERENCIA.md` §3.3 e o exercício 252.

### Adicionado — a sessão da Vitrine entre processos

- **`sessoes_em`**: a sessão mora num armazém. `V.sessoes_em_banco(caminho)`
  (SQLite em WAL; aceita a conexão do `Arcane.Database`),
  `V.sessoes_em_arquivos(pasta)` (um JSON por sessão, com trava do sistema e
  troca atômica) ou qualquer blueprint com `carregar`, `gravar` e `apagar`.
  Dois processos atrás de um balanceador passam a ver a mesma sessão — o
  contador continua e o login não cai.
- A sessão é gravada uma vez por pedido, **por chave** e só com o que mudou,
  inclusive mutação no lugar. Um valor que não atravessa processo é
  recusado na página, com a chave e o tipo.

### Corrigido — fixação de sessão na Vitrine

- Um `vitrine_sid` que a aplicação não conhece deixou de virar sessão com
  aquele id: vira uma sessão nova, com id sorteado.

### Adicionado — watchpoint no depurador

- **A vigia para quando um valor MUDA.** No terminal, `w <expr>`,
  `vigias` e `desvigiar N`; na linha de comando,
  `dataforge debug p.df --vigiar=total` (repetível); no editor, data
  breakpoint (`supportsDataBreakpoints`, motivo `data breakpoint` com o
  antes e o depois). É conferida depois de cada instrução e para na linha
  que mudou; a mutação no lugar (`xs.append`) e o campo mudado dentro de
  um método contam. Uma vigia criada numa ação só olha aquela ação. Sem
  vigia, nada é avaliado a mais.

### Adicionado — o tipo do conteúdo das coleções

- **`Cluster<T>`, `Vault<K, V>` e `Set<T>`**, aninháveis
  (`Vault<String, Cluster<Integer>>`). Até aqui o parser recusava a forma.
  O conteúdo é conferido **na fronteira** — declaração, parâmetro, retorno,
  campo —, com o item ou a chave nomeados na mensagem; **na inserção**, para
  a coleção que nasce na declaração (`append`, `insert`, `extend`,
  `xs[i] :=`, `+=`, `v[k] :=`, `set`, `update`, `add`); e **pelo `check`**,
  quando um literal prova o erro (`tipo-do-conteudo`), inclusive um tipo
  interno desconhecido. Uma coleção que já existia é conferida e continua
  sendo o mesmo objeto — sem cópia. Mensagens em pt-BR.
- O lexer deixou de tratar o `>`/`>>` que fecha `Cluster<…>` no fim da
  linha como continuação de expressão, e o formatador não espaça o genérico.

### Corrigido — posição de erro

- Um erro da linguagem levantado longe do código (sem linha) ganha a
  posição da instrução que o disparou, no interpretador e no compilador de
  fechamentos. Antes saía em `0:0`, sem o trecho desenhado.

### Adicionado — fila persistente

- **`Eventos.fila_persistente(caminho, trabalhador, opcoes)`** — a fila de
  trabalho que sobrevive ao processo, num SQLite (o `sqlite3` da
  biblioteca padrão, sem dependência nova). Reserva atômica com **prazo**:
  a tarefa de um processo que morreu no meio — inclusive por `kill -9` —
  volta a ficar disponível quando a reserva vence. **Recuo exponencial**
  com teto e tremor (`recuo`, `fator`, `recuo_maximo`, `tremor`),
  **atraso** e **hora marcada** (`publicar(item, {"atraso": 60})`,
  `agendar(item, quando)`), `prioridade`, `chave` contra tarefa repetida,
  e **carta morta** depois de `tentativas` falhas, com o último erro e o
  histórico de todos (`mortas()`, `reprocessar(id)`, `descartar_mortas()`).
  Várias filas no mesmo arquivo (`nome`), e operários em threads ou
  `processar()` síncrono. É entrega "pelo menos uma vez": o trabalhador
  deve ser idempotente. 15 testes, um deles matando um processo de verdade.

### Corrigido — o .deb de 1.194 bytes

- **O `.deb` publicado na `v1.0.0` estava vazio porque a tag era mais
  velha que a correção.** O gerador já montava o pacote inteiro (6,5 MB)
  desde `be61b47`; a tag `v1.0.0` aponta para `05977e9`, anterior a ele, e
  o CI empacotou o código da tag. Três travas para não repetir:
  o `release.yml` ganhou o job `versao`, que recusa uma tag diferente de
  `__version__` (ou `pyproject.toml` divergindo) **antes** de construir;
  `gerar_pacotes.py` recusa terminar com um `.deb` abaixo de 2 MB; e
  `verificar_downloads.py` passou a ter piso **por tipo de arquivo** —
  o piso geral de 100 KB deixava passar um `.deb` sem a biblioteca.
- `scripts/publicar_release.sh` é o caminho de publicação escrito: confere
  `gh` autenticado, árvore limpa e igual ao `origin/main`, tag nova e igual
  à versão, o `.deb` local acima do piso; marca, espera o workflow e
  confere o tamanho do `.deb` **publicado**. Sem `--executar`, só mostra.

### Adicionado — OOP como sistema

- **Treze palavras contextuais novas**, todas livres como nome fora do
  lugar delas (`readonly := 3` continua sendo uma variável):
  `internal`, `readonly`, `override`, `overload`, `exclusive`, `lazy` e
  `invariant` no corpo de blueprint; `sealed` e `meta` antes de
  `blueprint`; `contract` e `augment` no topo; `expects` e `promises` no
  corpo de ação. Nenhuma entrou em `KEYWORDS`.
- **`contract`** — só assinaturas, com herança entre contratos, propriedade
  exigida (`get total() -> Integer`), aridade conferida na declaração e
  valendo como tipo de parâmetro inclusive pelo que herda.
- **Design por contrato**: `expects` (pré-condição), `promises` (pós,
  com `outcome` e `before(…)`) e `invariant` — conferida depois da
  construção e de cada método público chamado de fora. Os erros já
  existiam no catálogo (`PreconditionError`, `PostconditionError`,
  `InvariantError`) e nada os levantava.
- **Modificadores**: `internal` (visível no arquivo), `readonly` (só a
  construção escreve), `override` (com sugestão do nome certo),
  `exclusive` (uma thread por vez no objeto, trava reentrante), `lazy get`,
  `static steady` (constante de classe), `final blueprint` e
  `sealed blueprint`.
- **`overload`** em ação de topo, método e construtor: escolha por aridade
  e tipo, o tipo exato vence o compatível, empate é erro.
- **Metaclasses**: `meta blueprint` + `using`, com dez ganchos de nome fixo
  (`on_forge`, `on_extend`, `on_spawn`, `on_ready`, `on_read`,
  `on_missing`, `on_write`, `on_call`, `on_serialize`, `on_deserialize`),
  herdadas, e recusando gancho desconhecido e metaclasses em conflito.
- **`augment`** — acrescentar a um blueprint existente sem substituir nada,
  sem tocar `final` e sem atravessar o arquivo de um `sealed`.
- **Cabeçalho com tipo e padrão** (`blueprint Caixa<T>(valor: T, rotulo := "")`),
  **blueprints aninhados** (`spawn Loja.Item()`), **decoradores em campo e
  propriedade**, e **`teardown`/`__del__`** que rodam de verdade.
- **Cinco módulos**: `Arcane.Reflexo` (introspecção e invocação que
  respeitam a visibilidade, tipos criados em execução, diagrama em
  Mermaid), `Arcane.Objetos` (cópia, congelamento, igualdade estrutural,
  serialização polimórfica que só reconstrói tipos autorizados e resolve
  ciclos), `Arcane.Injecao` (contêiner único/transitório/por escopo, com
  detecção de ciclo e de dependência cativa), `Arcane.Padroes` (os padrões
  que pedem mecanismo) e `Arcane.Memoria` (referência fraca, coletor).
- **`dataforge oop`** — métricas de Chidamber e Kemerer (WMC, DIT, NOC,
  CBO, RFC, LCOM), fan-in/out, instabilidade e manutenibilidade, e treze
  cheiros ligados ao princípio SOLID que ferem; `--diagrama`,
  `--hierarquia`, `--json`, `--strict`.
- **O `check` prova** override sem alvo, herança de `final`, contrato
  incompleto ou com aridade incompatível, `readonly` escrito fora da
  construção, gancho desconhecido, sobrecarga duplicada e `spawn` de
  contrato; e **avisa** `substituicao-quebrada` (Liskov).
- **LSP**: ir para implementação e hierarquia de tipos.
- Doze códigos de erro (DF0917–DF0928, DF0319), onze páginas em
  `/docs/oop`, e o módulo de exercícios `37-oop-sistema` (242–251).

### Corrigido — OOP

- **Metade dos 95 métodos mágicos da documentação não rodava.**
  `__getattr__`, `__setattr__`, `__delattr__`, `__getattribute__`, os
  descritores, `__new__`, `__del__`, `__init_subclass__`, `__int__`,
  `__float__`, `__round__`, `__abs__`, `__reversed__`, `__format__` e
  `__hash__` estavam na tabela e em lugar nenhum do interpretador — e
  `int(obj)` respondia com `'DFInstance'`, um nome do Python. A instância
  agora responde aos protocolos do host, e por isso os embutidos e a
  biblioteca inteira os honram sem saber deles.
- **`private action` podia ser chamada de fora.** A leitura de campo
  conferia a visibilidade; a chamada de método, não.
- **`private x := 1` sem tipo não compilava**, e `blueprint Caixa<T>(valor: T)`
  também não.
- **Chamar o blueprint como função (`Nome()`) nascia sem os padrões dos
  campos** que `spawn Nome()` tinha: eram dois caminhos de construção, e
  hoje é um.
- **`obj with {…}` numa instância estourava** tentando atribuir a uma
  propriedade sem escrita.
- **`__exit__(tipo, erro, pilha)` dava "missing argument(s)"** no fim do
  bloco `with`.
- **O analisador não contava `porta := 80` no corpo como campo**, e
  acusava `obj.porta` como membro inexistente — dentro do arquivo e
  através de `adopt`.

### Desempenho

- O acesso a membro ganhou um caminho direto para blueprint sem
  propriedade, descritor, gancho ou mágico de acesso, decidido uma vez
  por blueprint. Um laço de chamada de método, leitura de campo e `spawn`
  que levava 4,47 s leva cerca de 3,8 s — mesmo pagando pelos recursos novos.

### Adicionado

- **`Arcane.Quadro` — a tabela de dados**, e o 49º módulo. Colunas
  nomeadas e linhas como vault, colunar por dentro e imutável por fora:
  `pegar`, `sem`, `onde`, `ordenar`, `distintas`, `com`, `mapear`,
  `converter`, `inferir_tipos`, `nulos`, `sem_nulos`, `preencher`,
  `agrupar`, `resumir` (14 agregações), `contar_valores`,
  `tabela_cruzada`, `pivotar`, `despivotar`, `juntar` (os quatro JOIN do
  SQL), `empilhar`, `normalizar`, `padronizar`, `codificar`,
  `discretizar`, `descrever`, `correlacao`, `perfil`, `fora_da_curva`,
  e entrada/saída por CSV e JSON. 74 testes.
- **Seis verbos novos no operador `>>`** — `onde`, `pegar`, `sem`,
  `ordenar`, `agrupar` e `resumir` —, atravessando os cinco lugares de
  sempre mais o compilador. Eles são **contextuais**, como as onze
  palavras do Kiln: valem só depois de um `>>` e continuam livres como
  nome. Dentro de um `onde`, uma coluna se escreve **nua**
  (`onde valor bigger 50`), e ela vence um nome de fora com o mesmo nome.
- **Três páginas novas** em `/docs/dados`: o Quadro, os verbos, e o
  **mapa do ecossistema** — as 32 áreas de dados cruzadas com o que
  existe, marcando o que é nativo, o que atravessa a ponte para o Python,
  e o que não existe por decisão, com o motivo de cada um.
- Exercício **241**, no módulo novo `36-quadro-e-dados`.

### Corrigido

- **Havia dois DataFrames que divergiam.**
  `Arcane.Analytics.DataFrame` e `Arcane.Data.Frame` eram classes
  independentes, com `group_by`, `describe`, `normalize`, `merge` e
  `pivot` implementados duas vezes — e `describe` devolvia **chaves
  diferentes** conforme o módulo adotado (`25%`/`50%`/`75%` numa,
  `median` na outra). Duas respostas para "descreva estes dados" na mesma
  linguagem. `Quadro.descrever` é o contrato único; as duas antigas
  continuam funcionando, porque quebrar código que existe seria pior.

### Corrigido

- **`point [a, a]` casava com `[1, 2]`.** O padrão diz "dois itens
  **iguais**", e era lido como "dois itens quaisquer, e fique com o
  segundo". É a mesma família do argumento nomeado repetido e do
  parâmetro declarado duas vezes: um nome ligado duas vezes, calado. O
  `or` continua livre — `point [a] or {"v": a}` liga `a` uma vez em cada
  ramo, e exatamente um ramo casa.
- **Sete recados do CPython chegavam ao usuário inteiros.**
  `int("abc")` respondia *invalid literal for int() with base 10* — uma
  frase que fala de uma função que não existe nesta linguagem e não diz
  o que fazer. É o erro mais comum de todo programa que lê entrada: todo
  formulário, todo CSV, todo argumento de linha de comando passa por um
  `int(texto)`. Os nomes de tipo já eram traduzidos; a **frase inteira**
  não era. Agora `int`, `float`, `math domain error`, "cannot be
  interpreted as an integer", "not iterable" e os dois "index out of
  range" viram mensagem desta linguagem, com dica.

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

### Adicionado

- **Vinte e duas páginas novas de documentação**, em sete rotas que não
  existiam:
  **`/docs/modulos`** (5) — o sistema de módulos em nível de
  especificação, comparado a CommonJS e a ECMAScript: o algoritmo exato
  de resolução, carga única e estado compartilhado, ciclos, a superfície
  que o analisador lê, e a camada de template ao lado de EJS e
  Handlebars.
  **`/docs/bibliotecas`** (7) — do primeiro arquivo ao pacote publicado:
  estrutura, contrato, testes, semver, publicação e manutenção.
  **`/docs/dados`** (3) e **`/docs/sqlite`** — análise, ETL com
  idempotência e falha parcial, qualidade de dados, e o banco que vem
  junto.
  **`/docs/vm`** — como um `.df` executa, e por que não há VM de
  bytecode (o teto medido é ~6,5×).
  **`/docs/arquivos`**, **`/docs/repl`**, **`/docs/testes`** e
  **`/docs/api`** — sistema de arquivos, o console, a rota única de
  testes, e REST/RESTful com os códigos de status e idempotência.
- **`IO.read_csv(caminho, yes)`** devolve um cluster de vaults, usando a
  primeira linha como chaves — a forma com que o resto da linguagem
  trabalha.

### Corrigido

- **`IO.write_csv` destruía um cluster de vaults, em silêncio.** Ele
  passava a lista direto para o escritor de CSV, que itera cada linha — e
  iterar um vault dá as **chaves**. Gravar dois registros escrevia o
  cabeçalho duas vezes e perdia todos os valores, sem erro nenhum. Perder
  dado calado é a pior falha possível numa função de gravar arquivo, e o
  vault é a forma natural de linha aqui: é o que `read_json` devolve e o
  que `Database.query` devolve.
- **`adopt minha-lib` não compilava.** O lexer entrega o hífen como
  subtração, o loop de segmento parava ali, e o parser reclamava do `as`
  seguinte. O caminho relativo (`adopt ./minha-lib`) já colava o hífen; o
  nome nu, não — ou seja, `dataforge init minha-lib` criava um pacote que
  a linguagem não conseguia importar pelo nome, que é justamente como o
  teste de uma biblioteca precisa importá-la.

- **Ganchos de ciclo de vida para tarefas `async`** — `Async.ao_criar`,
  `ao_terminar`, `ao_falhar`, `sem_ganchos`, `vivas()` e
  `esperar_todas()`. Uma tarefa nasce numa thread e termina em outra, e
  no meio disso não havia onde pendurar um cronômetro, um id de pedido
  ou um contador. `vivas()` responde "por que este programa não
  termina?". Um gancho que levanta **não** derruba a tarefa: observação
  que quebra o observado é pior que não observar.
- **`.causa` num erro capturado**, e a cadeia desenhada no relatório.

### Corrigido

- **Uma tarefa `async` que falha e ninguém espera não some mais.** Era a
  última das três a engolir erro em silêncio — `thread` e `parallel` já
  desenhavam o erro e reprovavam a saída, e a tarefa `async` saía com
  **código 0** levando o erro junto. É o mesmo defeito que fez o Node
  passar a derrubar o processo numa promessa rejeitada sem tratamento.
  Disparar e esquecer continua valendo quando dá certo; o que não pode
  sumir é a falha.
- **Embrulhar um erro apagava o original.** `handle Error as e:` seguido
  de `trigger "não deu para carregar"` produzia uma mensagem que dizia o
  **quê** e perdia o **porquê**: a chave ausente, o arquivo que não
  existe, a conexão recusada sumiam inteiros. Agora o erro tratado vira
  `.causa` do novo, e o relatório desenha a cadeia com o trecho, a nota
  e a dica de cada camada.

- **JavaScript e TypeScript viram DataForge.** `dataforge converter` já
  lia Python pelo `ast`; agora lê `.js`, `.jsx`, `.mjs`, `.cjs`, `.ts`,
  `.tsx`, `.mts` e `.cts` por um **tokenizador e um parser próprios** —
  a regra de zero dependência vale aqui também. Traduz `class` para
  `blueprint`, `interface` para `trait`, `switch` para `match`,
  `try/catch/finally` para `monitor/handle/ensure`, template literal
  para interpolação, seta para `lambda` (e para uma ação nomeada quando
  o corpo é um bloco, porque o `lambda` daqui é uma expressão só), e
  aproveita as anotações de tipo do TypeScript. O que não tem
  equivalente honesto vira `TODO(converter)` com o código original ao
  lado. 44 testes, e quase todos **executam** o que saiu em vez de
  comparar texto.
- **Sete comandos novos na extensão do VS Code.** Converter este
  arquivo, a seleção ou uma pasta inteira — o resultado abre ao lado e a
  notificação conta as pendências. E **subir, parar, reiniciar e abrir**
  o servidor (Kiln ou Vitrine), com terminal próprio, descoberta da
  entrada pelo `forge.toml` e indicador na barra de status. Três opções
  novas: `dataforge.servidor.porta`, `.host` e `.abrirNavegador`.

- **Sete páginas novas de complexidade**, em `/docs/big-o`: recorrências e
  o Teorema Mestre, análise amortizada, Ω/Θ e limites inferiores,
  estruturas avançadas (heap, união-busca, deque, contador), complexidade
  em paralelo, a constante que decide, e complexidade em dados e I/O.
  Todo número citado foi **medido nesta máquina**: 118x entre buscar num
  cluster e num vault, 2,02x ao dobrar o número de `append` (que é o que
  prova o amortizado), 15x entre ordenar tudo e um heap de 10, 16,6x
  entre varrer a tabela e usar índice, 6,4x entre N+1 e uma consulta, e
  4,71x com processos em 10 núcleos.
- **`/docs/primeiros-passos` e `/docs/fundamentos/anotacoes-de-tipo`**
  quase dobraram: a linguagem em cinco minutos, um programa inteiro, o
  que um erro mostra, testes, REPL, editor e as seis armadilhas de quem
  chega; e do lado dos tipos, genéricos com limite, trait como tipo, o
  tipo atravessando o `adopt`, e a tabela do que faz o analisador calar.

### Corrigido

- **Quatro classes erradas no `dataforge big-o`**, todas medidas contra
  algoritmos conhecidos. O **merge sort** saía como `O(n log^2 n)`: a ação
  se chama `ordenar`, que está na tabela de custos dos embutidos, e o
  preço dela era cobrado das chamadas recursivas e multiplicado de novo.
  A **busca binária recursiva** saía como `O(2^n)` — as duas chamadas
  estão em ramos mutuamente exclusivos e eram somadas, e a bisseção mora
  no `meio := (baixo + alto) ~/ 2`, que ninguém seguia. O **fibonacci
  memoizado** saía como `O(2^n)`, com o aviso mandando memoizar o que já
  estava memoizado. E **percorrer uma árvore** saía como `O(2^n)`, embora
  `f(no.esq)` e `f(no.dir)` desçam por galhos diferentes.
- **`has_field`, `get_fields`, `has_method` e `get_methods` mentiam sobre
  todo record.** `has_field(p, "x")` respondia `no` para um campo que
  existe, e `get_fields(p)` devolvia vazio: os quatro procuravam a forma
  de uma instância de blueprint. Uma pergunta de reflexão respondida
  errado é pior que uma que levanta — quem escreve
  `given has_field(p, "email")` segue pelo ramo errado, calado.
- **`xs: Cluster<Integer>`** respondia `Era esperado IDENTIFIER, got LT` e
  ainda arrastava a linha seguinte para um segundo erro. Agora diz o que
  não existe e o que escrever: o tipo do conteúdo de uma coleção não é
  verificado, anote como `Cluster`.

- **`spawn B().f()` significava outra coisa.** O `spawn` consumia a cadeia
  inteira de pós-fixos, então a linha era lida como `spawn (B().f())`: o que
  chegava para construir era o resultado de um método, e a mensagem culpava a
  ação — *"'<action f>' is not a blueprint, so it cannot be spawned"*. É a
  forma mais natural que existe (`new B().f()` em quase toda linguagem), e o
  parêntese que consertava não estava em mensagem nenhuma. Agora o `spawn`
  leva o nome e os argumentos do construtor, e o que vem depois é aplicado
  sobre a instância.
- **Cinco declarações que se contradizem**, todas aceitas em silêncio:
  `action f(a, a)` — o primeiro parâmetro não tinha como ser lido, e
  `f(1, 2)` devolvia 2;
  `action f(a := 1, b)` — o padrão nunca podia ser usado, porque `f(2)` deixa
  `b` sem valor e `f(2, 3)` passa por cima dele;
  dois métodos com o mesmo nome no mesmo blueprint — o segundo vencia, e o
  campo repetido de um `record` e o membro repetido de um `enum` já eram
  acusados;
  um método com o nome de um campo do cabeçalho (`blueprint B(x)` com
  `action x()`) — o **campo** vence, e o método existe no arquivo sem nunca
  rodar;
  e duas declarações de topo com o mesmo nome no mesmo arquivo, que agora são
  **aviso** (`declaracao-repetida`) — a segunda vence, e a primeira não tem
  como ser alcançada.

- **Quatro enganos que passavam calados**, achados numa bateria de dez
  erros novos contra o analisador:
  `f() := 2` respondia **"'f' é palavra reservada e não pode receber
  valor"** — `f` não é reservada, e renomear não conserta nada: o problema é
  atribuir ao resultado de uma chamada. Cada alvo inválido agora diz o que
  ele é (chamada, número, texto, conta, fatia), e a mensagem de palavra
  reservada ficou para quem é de fato reservada — `"a" := 1` também
  acusava "'a' é palavra reservada".
  `f(a := 1, a := 2)` **descartava o primeiro valor** em silêncio, e
  `P(x := 1, x := 2)` construía o record com o segundo: num vault a última
  chave vencer é regra, numa chamada é engano, e adivinhar qual dos dois
  valores sobra não dá.
  `{"a": 1, "a": 2}` ganhou aviso (`chave-repetida`) — a regra não muda, mas
  a mesma chave duas vezes no mesmo literal é sempre engano.
  `blueprint Ciclo extends Ciclo` passava limpo, e **uma mãe que não existe
  era ignorada em execução**: o blueprint nascia sem ela, e a falta aparecia
  páginas depois como "has no member", longe da causa.

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
