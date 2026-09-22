# Biblioteca padrão DataForge — módulos `Arcane.*`

Referência gerada a partir das assinaturas reais do código
(`python3 tools/gerar_doc_stdlib.py`). Todo módulo é carregado com `adopt`:

```dataforge
adopt Arcane.Math as Math
out Math.sqrt(16)
```

Cada módulo tem um **nome curto** equivalente (`adopt Math as M` funciona igual).

## Índice

| Módulo | Nome curto | Símbolos | Para quê |
|--------|-----------|----------|----------|
| [`Arcane.Math`](#arcanemath) | `Math` | 72 | Matemática, álgebra linear e estatística básica. |
| [`Arcane.Text`](#arcanetext) | `Text` | 59 | Manipulação de texto, formatação, tabelas e conversão de caixa. |
| [`Arcane.Analytics`](#arcaneanalytics) | `Analytics` | 65 | Análise de dados: estatística, regressão, clustering e gráficos ASCII. |
| [`Arcane.Functional`](#arcanefunctional) | `Functional` | 56 | Utilitários funcionais: composição, lentes, Maybe/Either, transdutores. |
| [`Arcane.Database`](#arcanedatabase) | `Database / DB` | 64 | Banco de dados SQLite: tabelas, consultas, migrações e importação. |
| [`Arcane.Excel`](#arcaneexcel) | `Excel / Xlsx` | 29 | Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame. |
| [`Arcane.Meta`](#arcanemeta) | `Meta` | 12 | Metadados de decorador: ler @Nome em tempo de execução. |
| [`Kiln`](#kiln) | `Kiln` | 73 | Framework web: rotas, middleware, templates, sessão e arquivos estáticos. |
| [`Arcane.Test`](#arcanetest) | `Test` | 34 | Asserções e organização de suítes de teste. |
| [`Arcane.Regex`](#arcaneregex) | `Regex` | 46 | Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone). |
| [`Arcane.IO`](#arcaneio) | `IO` | 33 | Arquivos, diretórios, JSON, CSV e shell. |
| [`Arcane.Http`](#arcanehttp) | `Http / Server` | 17 | Servidor HTTP: rotas, middleware, JSON, arquivos estáticos. |
| [`Arcane.Async`](#arcaneasync) | `Async` | 52 | Promessas, filas, agendamento e execução concorrente. |
| [`Arcane.Data`](#arcanedata) | `Data` | 13 | DataFrames, séries e transformações tabulares. |
| [`Arcane.Web`](#arcaneweb) | `Web / Network` | 11 | Cliente HTTP, URL encoding e JSON. |
| [`Arcane.Cortex`](#arcanecortex) | `Cortex` | 25 | Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA. |
| [`Arcane.Time`](#arcanetime) | `Time` | 54 | Datas, horas, durações e cronometragem. |
| [`Arcane.OS`](#arcaneos) | `OS` | 43 | Sistema operacional, ambiente, disco e processo atual. |
| [`Arcane.Process`](#arcaneprocess) | `Process` | 15 | Execução de processos externos, com stdout, stderr e código de saída. |
| [`Arcane.Logging`](#arcanelogging) | `Logging / Log` | 14 | Registro estruturado de eventos, com níveis e destinos. |
| [`Arcane.Crypto`](#arcanecrypto) | `Crypto` | 53 | Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305). Assina e verifica JWT (HS256/384/512), com o algoritmo decidido por quem verifica e não pelo token. |
| [`Arcane.Seguranca`](#arcaneseguranca) | `Seguranca` | 54 | Escape por destino (HTML, atributo, JS, URL, shell, SQL LIKE, CSV, cabeçalho, log), sanitização de HTML por lista de permitidos, política e força de senha com vazamento por k-anonimato, TOTP/HOTP e códigos de recuperação, token e URL assinados com prazo e propósito, varredura de segredos por formato, redação de PII, defesa de SSRF e de travessia de caminho, limitador de taxa, bloqueio progressivo, trilha de auditoria encadeada e dez regras de análise estática. |
| [`Arcane.Politica`](#arcanepolitica) | `Politica` | 6 | Motor de autorização: RBAC com herança, ABAC por atributo, ACL por objeto, grupos, isolamento por inquilino, negação explícita que vence o papel e delegação com prazo. O padrão é negar, e toda decisão diz qual regra a tomou — um motor que responde só sim/não é impossível de auditar. |
| [`Arcane.Chaves`](#arcanechaves) | `Chaves` | 6 | Ciclo de vida de chave criptográfica: propósito cobrado, prazo, rotação que mantém as antigas decifrando o passado, identificador no dado cifrado, cifragem em envelope (DEK/KEK), recifragem, derivação por contexto (HKDF) e exportação do cofre cifrada pela senha mestra. |
| [`Arcane.Deteccao`](#arcanedeteccao) | `Deteccao` | 7 | Regras de detecção sobre eventos, com correlação por chave em janela deslizante, supressão, gravidade e mapa para MITRE ATT&CK; indicadores de comprometimento com prazo e normalização; padrões sobre conteúdo e leitura de log de acesso. O alerta carrega os eventos que o causaram. |
| [`Arcane.GitHub`](#arcanegithub) | `GitHub` | 19 | O que um programa precisa para viver no GitHub: no Actions, saídas, variáveis e resumo com delimitador seguro, anotações escapadas que aparecem na linha do PR, máscara linha a linha e grupos; webhooks com assinatura HMAC conferida em tempo constante sobre os bytes originais; e a API REST com paginação por Link e o limite de taxa que sobrou. |
| [`Arcane.Gramatica`](#arcanegramatica) | `Gramatica` | 10 | A gramática da linguagem como dado: as produções em EBNF, cada uma com um exemplo conferido contra o parser, a tabela de precedência provada pela árvore, os tokens de um texto, as instruções que o parser entendeu e a validação de sintaxe sem executar nada. |
| [`Arcane.Privacidade`](#arcaneprivacidade) | `Privacidade` | 10 | O que a LGPD pede, como operações sobre dado: pseudonimização com chave (e não hash sem chave, que se desfaz), generalização de quase-identificadores, a medida do k-anonimato, minimização por lista de permitidos, retenção, consentimento por titular e por finalidade com histórico, os direitos de acesso e eliminação percorrendo todo lugar onde o dado mora, e contagem com privacidade diferencial. |
| [`Arcane.Integridade`](#arcaneintegridade) | `Integridade` | 6 | Provar que o que está aqui é o que foi posto aqui: o valor SRI de um script de CDN, o manifesto SHA-256 de uma pasta com o que foi acrescentado, removido e alterado, e o manifesto assinado com uma chave que mora fora dali. |
| [`Arcane.Collections`](#arcanecollections) | `Collections` | 63 | Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca. |
| [`Arcane.Serialization`](#arcaneserialization) | `Serialization / Serde` | 26 | JSON, CSV, INI, TOML, XML e conversões entre eles. |
| [`Arcane.Forge`](#arcaneforge) | `Forge / Banco` | 31 | Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface. |
| [`Arcane.Crucible`](#arcanecrucible) | `Crucible` | 61 | Framework de testes: suítes, matchers, fixtures, dublês e benchmark. |
| [`Arcane.Iter`](#arcaneiter) | `Iter` | 44 | Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize. |
| [`Arcane.Color`](#arcanecolor) | `Color / Cor` | 66 | Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore. |
| [`Arcane.Concurrent`](#arcaneconcurrent) | `Concurrent / Paralelo` | 33 | Threads, processos, canal bloqueante, grupo de tarefas e prazo. |
| [`Arcane.Archive`](#arcanearchive) | `Archive / Zip` | 13 | Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb. Comprime e descomprime VALORES em memória, em deflate cru ou em gzip, com a taxa medida. |
| [`Arcane.Pipeline`](#arcanepipeline) | `Pipeline / Fluxo` | 11 | Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório. |
| [`Arcane.Stream`](#arcanestream) | `Stream / Corrente` | 17 | Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo. |
| [`Arcane.Observar`](#arcaneobservar) | `Observar / Observe` | 19 | Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados. |
| [`Arcane.Quadro`](#arcanequadro) | `Quadro` | 10 | A tabela de dados: colunas nomeadas e linhas como vault. Filtrar, agrupar, resumir, juntar, pivotar, limpar a ausência e a duplicata, converter tipos, normalizar, codificar e descrever — colunar por dentro, imutável por fora. |
| [`Arcane.Lago`](#arcanelago) | `Lago / Parquet` | 18 | Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação. |
| [`Arcane.Telegram`](#arcanetelegram) | `Telegram` | 34 | Bots de Telegram, do primeiro '/start' ao webhook em producao: cliente da Bot API com o limite de taxa lido de onde ele chega, tratadores por comando, texto, botao, midia e consulta inline, conversa como maquina de estados por chat, teclados, o escape de MarkdownV2 que salva a mensagem inteira, e uma sonda que testa o bot sem token e sem rede. |
| [`Arcane.Reativo`](#arcanereativo) | `Reativo` | 14 | Valores que avisam quando mudam: sinal (um valor com estado), derivado (calculado de outros, preguicoso e memorizado, com as dependencias DESCOBERTAS na execucao), efeito (o que acontece quando muda, com limpeza entre ciclos) e observavel (um fluxo no tempo, com morph, sift, distill, distintos, esperar, limitar, combinar e juntar). A diferenca entre valor e fluxo e mantida de proposito: um clique e fluxo, um saldo e valor. |
| [`Arcane.Dominio`](#arcanedominio) | `Dominio` | 18 | As pecas de um modelo de dominio que se sustenta (DDD): valor (igualdade por conteudo, imutavel, com regra cobrada na criacao), entidade (igualdade por identidade), agregado (a unica porta de escrita, com invariantes conferidas na SAIDA de cada comando e desfazer quando o comando falha no meio), evento (um fato no passado, imutavel), regra (condicao de negocio que se combina com e/ou/nao e explica o "nao"), repositorio (guarda agregados INTEIROS), unidade de trabalho (confirma tudo ou nada, e so entao publica) e contexto delimitado (com a traducao que atravessa a fronteira). |
| [`Arcane.Estrutura`](#arcaneestrutura) | `Estrutura` | 15 | Layout binario com NOME, e o ponteiro que o percorre: uma estrutura de campos nomeados com a ordem dos bytes cobrada e o alinhamento declarado (e conferido), uma janela que le e escreve no bloco original sem copiar, um bloco que sabe dizer quando foi liberado, e um ponteiro com aritmetica por ELEMENTO, cast, distancia e dono fraco. Fica entre o Arcane.Bytes, que empacota por formato posicional, e o Arcane.C, que exige FFI. |
| [`Arcane.Malha`](#arcanemalha) | `Malha` | 23 | Chamada entre serviços que não mente: cliente HTTP com prazo, retry com recuo e tremor, disjuntor de três estados, descoberta por nome e propagação automática do rastro do pedido. |
| [`Arcane.Url`](#arcaneurl) | `Url` | 14 | Endereços: ler um URL em partes, montar a partir delas, resolver caminho relativo como um navegador, trocar parâmetros preservando os outros, query string em vault (ou em cluster, quando a chave repete) e escape para caminho e para valor. |
| [`Arcane.Bytes`](#arcanebytes) | `Bytes` | 25 | Dados binários: empacotar e desempacotar campos com a ordem dos bytes declarada, um cursor que anda pelo bloco sem acertar índice à mão, janela que olha sem copiar, hexadecimal, base64, bits, despejo estilo hexdump e comparação em tempo fixo. |
| [`Arcane.Rede`](#arcanerede) | `Rede` | 16 | TCP, UDP, DNS e TLS: conexão com prazo, leitura que insiste até completar, servidor de uma thread por conexão, datagrama, resolução de nome, porta livre, espera de porta abrir e a validade do certificado de um host. |
| [`Arcane.Bench`](#arcanebench) | `Bench` | 7 | Medir, comparar e descobrir a classe de custo: tempo de uma ação, implementações lado a lado sem a ordem decidir quem ganha, e a curva medida em tamanhos crescentes dizendo qual O() descreve o que aconteceu. |
| [`Arcane.Reflexo`](#arcanereflexo) | `Reflexo` | 38 | Reflexão sobre blueprints, contratos e objetos: campos, métodos, modificadores, MRO, herdeiros, anotações, invocação por nome respeitando a visibilidade, criação de tipos em execução e diagrama de classes em Mermaid. |
| [`Arcane.Objetos`](#arcaneobjetos) | `Objetos` | 13 | Cópia rasa e funda, congelamento, igualdade estrutural, hash coerente, ordenação por campos e serialização polimórfica que só reconstrói os tipos autorizados e resolve ciclos. |
| [`Arcane.Injecao`](#arcaneinjecao) | `Injecao / DI` | 5 | Contêiner de injeção de dependência: único, transitório e por escopo, fábrica, valor pronto, dependência preguiçosa e opcional, injeção por construtor, campo e método, e detecção de ciclo com a cadeia inteira. |
| [`Arcane.Padroes`](#arcanepadroes) | `Padroes` | 20 | Os padrões de projeto que pedem mecanismo: único, pool, construtor, protótipo, flyweight, proxy, adaptador, composto, comandos com desfazer, cadeia, especificação, máquina de estados, memento, visitante, observável, mediador, repositório e barramento. |
| [`Arcane.Memoria`](#arcanememoria) | `Memoria` | 24 | O ciclo de vida visto de dentro: referência fraca, mapa fraco, ação ao descartar, instâncias vivas por blueprint, tamanho e layout. E o COLETOR sob controle: ligar, desligar, 'sem_gc' num trecho sensível a latência (que religa mesmo se o corpo falhar), limiares por geração, 'congelar' o que já vive para tirá-lo das varreduras, e a conta por geração. Mais a arena: um lote preparado de uma vez e reaproveitado, com 'limpar' soltando tudo numa chamada. |
| [`Arcane.C`](#arcanec) | `C / Nativo` | 23 | Falar com biblioteca nativa: abrir .so/.dylib/.dll, chamar funcao com assinatura declarada, struct e uniao com o layout de verdade (tamanho, alinhamento e deslocamento), ponteiro cru com aritmetica, memoria alocada a mao e callback — uma acao da linguagem chamada de dentro do C. Sobre ctypes, da biblioteca padrao: zero dependencia. |
| [`Arcane.Macro`](#arcanemacro) | `Macro` | 13 | A arvore como dado: ler o corpo de uma acao, percorrer, transformar e gerar codigo. 'citar' transforma texto em arvore, 'reescrever' devolve uma acao com o corpo trocado, 'nome_fresco' e 'renomear' dao higiene, e 'derivar' e a macro de atributo que gera __str__, __eq__, __lt__ e para_vault a partir dos campos. |
| [`Arcane.Compilador`](#arcanecompilador) | `Compilador` | 24 | O caminho de compilacao como dado: os tokens, a arvore, o HIR (a arvore depois do acucar, com a lista do que e acucar e do que so parece), o MIR (bloco basico, aresta, laco e tratador) e as analises que so o grafo responde — alcance, vivacidade, constante em todo caminho, escapatoria e o nome que so um ramo define. O LIR diz o que o compilador de fechamentos compilou e o que recuou para a arvore. |
| [`Arcane.Laco`](#arcanelaco) | `Laco / Reator` | 25 | O laco de eventos, o escalonador e as fibras: UMA thread dormindo no seletor do sistema (epoll, kqueue ou select) em vez de uma thread por conexao. Fila de prazos com 'apos' e 'a_cada', fila de prontas com teto opcional (contrapressao), executor para o trabalho que bloqueia, cancelamento, e fibras de verdade — um 'stream action' suspenso em cada 'emit'. |
| [`Arcane.Perfil`](#arcaneperfil) | `Perfil` | 16 | Medir com rigor, onde o 'Bench' da a media: percentis (p50, p95, p99, p999) com aquecimento separado, comparacao com SIGNIFICANCIA estatistica (Mann-Whitney, que nao supoe normalidade — tempo de execucao nao e normal), linha de base guardada para acusar regressao no CI, flame graph das ACOES da linguagem em SVG sem nada de fora, pausas do coletor medidas na fonte e contencao de trava. |
| [`Arcane.Inicio`](#arcaneinicio) | `Inicio` | 12 | O que roda ANTES da primeira linha: as fases da partida nomeadas e em ordem, e quanto cada 'adopt' custou — que e a unica forma de responder 'por que o programa demora a comecar?' sem cronometrar a mao. Mais armazenamento por THREAD com inicializacao e finalizador (o 'threading.local' da o armazem e nao da o resto), e a pilha que se pergunta: profundidade, teto, quanto falta e os quadros abertos. |
| [`Arcane.Capacidade`](#arcanecapacidade) | `Capacidade` | 6 | A fronteira de CAPACIDADE: roda uma acao com a lista de poderes que ela pode alcancar, e recusa o resto pelo NOME da capacidade que falta. A ponte para o Python e capacidade propria, e nunca vem junto. NAO e caixa contra programa hostil, e o modulo diz isso em 'limites()': ele bloqueia a autoridade ambiente (o 'adopt'), e nao tira o que foi ENTREGUE — o que e o modelo de capacidade, nao um defeito. |
| [`Arcane.Abi`](#arcaneabi) | `Abi` | 8 | A superficie de um modulo e o CONTRATO dele, e quebra-la e o mesmo problema que quebrar uma ABI — com outro nome e o mesmo sintoma: nao e erro de quem publicou, e erro de quem consome, depois. Compara duas versoes e diz o que quebrou (simbolo removido, aridade incompativel, parametro renomeado, tipo trocado, campo novo obrigatorio) e qual bump de semver a mudanca EXIGE. Mais o mapa de simbolos: de onde vem cada nome, o analogo do mapa que um ligador escreve. |
| [`Arcane.Alvo`](#arcanealvo) | `Alvo` | 7 | 'Isso roda no navegador?', respondido a partir dos 'adopt'. Seis alvos descritos (servidor, cli, navegador, wasi, funcao serverless, embarcado) com o que cada um suporta e POR QUE nao suporta o resto, no mesmo vocabulario de capacidade do 'Arcane.Capacidade'. A leitura e ESTATICA e o modulo diz isso em 'limites()': um 'roda' quer dizer 'nao achei impedimento por esta via', e nao 'vai funcionar'. |
| [`Arcane.Ecossistema`](#arcaneecossistema) | `Ecossistema` | 9 | O inventario da implementacao, CONFERIDO contra ela. Cada componente do desenho do ecossistema aponta arquivos de verdade e carrega um de tres estados: 'existe', 'equivale' (ha outra peca que responde a mesma pergunta, nomeada) ou 'nao-existe' (com o porque escrito). 'conferir()' cobra as duas direcoes — todo caminho citado existe no disco, e todo modulo do nucleo aparece em algum componente —, e e isso que impede o mapa de mentir quando uma peca muda de nome. 'o_que_nao_existe()' e a resposta honesta a 'o DataForge tem backend LLVM?'. |
| [`Arcane.Principios`](#arcaneprincipios) | `Principios` | 6 | Os dez principios de design, cada um com uma prova que RODA e o numero que ela deu — duas delas rodam o analisador e uma roda o interpretador, porque 'verificacao antes de rodar' e 'custo zero quando desligado' sao coisas que se demonstram. O veredito nao e dez de dez de proposito: 5 cumpridos, 4 parciais e 1 que nao se aplica. E as nove TENSOES: onde dois principios se contradizem, qual venceu, o custo aceito e o arquivo onde a decisao mora. |
| [`Arcane.Percurso`](#arcanepercurso) | `Percurso` | 5 | O caminho inteiro de um arquivo, fase por fase, MEDIDO: lexer, parser, HIR, tipos, MIR, analises, SSA, passes e LIR, com o que cada fase produziu e quanto tempo levou. Responde 'onde o tempo vai' quando um arquivo demora a abrir no editor. Ele NAO executa o programa — executar e o que o programa faz, e um comando que mostra fases nao pode abrir soquete. Traz tambem as divergencias entre o caminho real e o desenho da referencia. |
| [`Arcane.Dsl`](#arcanedsl) | `Dsl` | 18 | Combinadores para escrever uma linguagem pequena, propria: texto, numero, nome, aspas, espaco, sequencia, alternativa, repeticao, opcional e separado_por, com 'analisar' devolvendo Resultado e a falha dizendo a posicao e o que era esperado. |
| [`Arcane.Posse`](#arcaneposse) | `Posse` | 16 | Quem e o dono, quem tomou emprestado, e quando solta: posse exclusiva com liberacao deterministica ('dono' e 'com', o RAII), emprestimo com escopo (muitos leem OU um escreve, cobrado quando roda), contagem de referencia deterministica ('compartilhado' e 'atomico') e referencia fraca que quebra o ciclo. |
| [`Arcane.Stm`](#arcanestm) | `Stm / Transacional` | 13 | Memoria transacional: escritas que acontecem JUNTAS ou nao acontecem. Variavel transacional, 'atomicamente' com validacao otimista e repeticao no conflito, 'retentar' que espera em vez de girar, 'ou_entao' para compor duas operacoes bloqueantes, e estatisticas de conflito. |
| [`Arcane.Resultado`](#arcaneresultado) | `Resultado / Result` | 13 | A falha como VALOR, e a ausencia com nome: 'ok'/'falha' para quem devolve o erro em vez de levanta-lo, com 'mapear', 'entao', 'recuperar', 'ou' e 'todos' (a primeira falha vence); e 'Talvez' ('algo'/'nada') para onde 'void' e ambiguo — distinguir 'a chave nao esta la' de 'a chave vale void'. |
| [`Arcane.Tipos`](#arcanetipos) | `Tipos` | 10 | Reflexao sobre tipos: os metadados de um 'type' declarado (especie, base, regra, opaco), 'satisfaz' para conferir sem levantar, a forma ESTRUTURAL de um valor ('Cluster<Integer>', 'Tuple<Integer, String>') e os campos de um record ou instancia com o tipo de cada um. |
| [`Arcane.Eventos`](#arcaneeventos) | `Eventos` | 10 | Publicar e assinar sem as duas partes se conhecerem: emissor com curinga, ouvinte de uma vez só, contexto por thread que atravessa as camadas, fila de trabalho em segundo plano, e fila persistente em SQLite que sobrevive ao processo, com recuo exponencial, atraso e hora marcada, prioridade, chave contra repetição e carta morta. |
| [`Arcane.Cli`](#arcanecli) | `Cli` | 12 | A linha de comando de um programa escrito em DataForge: opções tipadas com valor padrão e escolhas, argumentos posicionais, subcomandos, ajuda gerada da declaração, perguntas no terminal e console interativo. |
| [`Arcane.Email`](#arcaneemail) | `Email` | 6 | Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza no cabeçalho, SMTP com TLS por padrão, prévia sem enviar e caixa de teste com o mesmo contrato. |
| [`Arcane.Html`](#arcanehtml) | `Html` | 11 | Ler HTML de verdade: seletor CSS, texto que junta com espaço, links absolutos, tabela como dado, escapar contra XSS, limpar toda a marcação e podar deixando só as tags permitidas. |
| [`Arcane.Lavra`](#arcanelavra) | `Lavra` | 42 | A consulta tipada: o cliente diz exatamente quais campos quer, numa consulta indentada, e recebe exatamente aqueles. O esquema nasce dos 'record' que já existem; traz resolvedores, contexto, trechos, variáveis, diretivas, contratos, uniões, introspecção, validação antes de executar, lote contra o N+1, paginação por cursor, limites de profundidade e custo, assinaturas por WebSocket e federação de vários serviços. |
| [`Arcane.Vitrine`](#arcanevitrine) | `Vitrine` | 213 | O framework de dashboards e aplicações de dados: você escreve um programa de cima para baixo e ele vira uma página web, com componentes, layout, gráficos em SVG, estado por sessão e cache — servido pelo Kiln. |
| [`Arcane.API`](#arcaneapi) | `API` | 7 | A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas. |
| [`Arcane.Decimal`](#arcanedecimal) | `Decimal / Exato` | 16 | Número decimal exato, para quando 0,1 + 0,2 precisa dar 0,3 — dinheiro, imposto, e todo número que alguém confere na mão. |
| [`Arcane.Ponte`](#arcaneponte) | `Ponte / Bridge` | 12 | A ponte para o Python: perguntar se um pacote existe, explorar o que ele oferece e converter o que ele devolve. |
| [`Arcane.Qualidade`](#arcanequalidade) | `Qualidade / Quality` | 13 | Qualidade de dados: as seis dimensões, perfil, validação e limpeza. |

> Os nomes curtos e os aliases (`DB`, `Server`, `Network`) apontam para o mesmo
> módulo — use o que ficar mais legível.

## Exemplos rápidos

```dataforge
adopt Arcane.Math as Math
adopt Arcane.Text as Text
adopt Arcane.Analytics as An

out Math.sqrt(16)                       // 4.0
out Math.is_prime(97)                   // yes
out Text.slug("Ola Mundo")              // ola-mundo
out Text.box("Relatorio")               // caixa desenhada
out An.correlation([1,2,3], [2,4,6])    // 1.0
```


---

## Arcane.Math

Matemática, álgebra linear e estatística básica.

```dataforge
adopt Arcane.Math as Math
```

**Constantes**

| Nome | Valor |
|------|-------|
| `E` | `2.718281828459045` |
| `INF` | `inf` |
| `NAN` | `nan` |
| `PI` | `3.141592653589793` |
| `TAU` | `6.283185307179586` |
| `random` | `{'random': <built-in method random of Random objec…` |

**Funções (66)**

| Assinatura |
|------------|
| `abs(x)` |
| `acos(x)` |
| `asin(x)` |
| `atan(x)` |
| `atan2(y, x)` |
| `cbrt(x)` |
| `ceil(x)` |
| `clamp(value, min_val, max_val)` |
| `comb(n, k)` |
| `complexo(real, imaginario=0.0)` |
| `complexo_conjugado(z)` |
| `complexo_de_polar(r, a)` |
| `complexo_exp(z)` |
| `complexo_fase(z)` |
| `complexo_log(z, base=None)` |
| `complexo_modulo(z)` |
| `complexo_partes(z)` |
| `complexo_polar(z)` |
| `complexo_raiz(z)` |
| `complexo_texto(z)` |
| `cos(x)` |
| `degrees(x)` |
| `determinant(matrix)` |
| `dot(a, b)` |
| `exp(x)` |
| `factorial(n)` |
| `fibonacci(n)` |
| `floor(x)` |
| `fracao(a, b=None)` |
| `fracao_de_texto(t)` |
| `fracao_dividido(a, b)` |
| `fracao_float(f)` |
| `fracao_limitar(f, teto)` |
| `fracao_menos(a, b)` |
| `fracao_partes(f)` |
| `fracao_soma(*p)` |
| `fracao_texto(f)` |
| `fracao_vezes(*p)` |
| `gcd(*inteiros)` |
| `hypot(*coordenadas)` |
| `identity(n)` |
| `is_prime(n)` |
| `lcm(a, b)` |
| `lerp(a, b, t)` |
| `log(x, base=e)` |
| `log10(x)` |
| `log2(x)` |
| `map_range(value, in_min, in_max, out_min, out_max)` |
| `matrix(data)` |
| `max(*valores)` |
| `mean(data)` |
| `median(data)` |
| `min(*valores)` |
| `ones(rows, cols=None)` |
| `perm(n, k=void)` |
| `pow(x, y)` |
| `radians(x)` |
| `round(numero, casas=void)` |
| `sin(x)` |
| `sqrt(x)` |
| `stdev(data)` |
| `sum(data)` |
| `tan(x)` |
| `transpose(matrix)` |
| `variance(data)` |
| `zeros(rows, cols=None)` |


---

## Arcane.Text

Manipulação de texto, formatação, tabelas e conversão de caixa.

```dataforge
adopt Arcane.Text as Text
```

**Funções (59)**

| Assinatura |
|------------|
| `align(lines, alignment='left', width=None)` |
| `box(text, style='single')` |
| `camel_case(text)` |
| `char_count(text, include_spaces=True)` |
| `closest(query, candidates, n=3)` |
| `constant_case(text)` |
| `construtor(inicial='')` |
| `currency(amount, symbol='$', decimals=2)` |
| `dedent(text)` |
| `diff(a, b)` |
| `distance(a, b)` |
| `dot_case(text)` |
| `escape_html(text)` |
| `escape_regex(text)` |
| `extract_emails(text)` |
| `extract_hashtags(text)` |
| `extract_links(text)` |
| `extract_mentions(text)` |
| `extract_numbers(text)` |
| `frequency(text)` |
| `fuzzy_match(query, text, threshold=0.6)` |
| `highlight(text, word, start='\x1b[1;33m', end='\x1b[0m')` |
| `indent(text, prefix='    ')` |
| `kebab_case(text)` |
| `line_count(text)` |
| `lorem(sentences=3)` |
| `ngrams(text, n=2)` |
| `normalize_whitespace(text)` |
| `number_format(n, decimals=2, thousands_sep=',', decimal_sep='.')` |
| `pad(text, width, fill=' ', align='left')` |
| `paragraph_count(text)` |
| `parse_csv(text, delimiter=',')` |
| `parse_ini(text)` |
| `parse_query(query_string)` |
| `pascal_case(text)` |
| `path_case(text)` |
| `random_string(length=16, charset='alphanumeric')` |
| `reading_time(text, wpm=200)` |
| `remove_accents(text)` |
| `render(template, context)` |
| `repeat_str(text, n, separator='')` |
| `sentence_case(text)` |
| `sentence_count(text)` |
| `similarity(a, b)` |
| `slug(text)` |
| `snake_case(text)` |
| `strip_ansi(text)` |
| `strip_html(text)` |
| `table(headers, rows, style='simple')` |
| `template(text)` |
| `title_case(text)` |
| `to_csv(data, delimiter=',')` |
| `to_query(params)` |
| `transliterate(text)` |
| `truncate(text, length=50, suffix='...')` |
| `unescape_html(text)` |
| `unified_diff(a, b, a_name='original', b_name='modified')` |
| `word_count(text)` |
| `wrap(text, width=80)` |


---

## Arcane.Analytics

Análise de dados: estatística, regressão, clustering e gráficos ASCII.

```dataforge
adopt Arcane.Analytics as Analytics
```

**Funções (65)**

| Assinatura |
|------------|
| `DataFrame(data=None, columns=None)` |
| `autocorrelation(data, lag=1)` |
| `bar_chart(data, labels=None, width=40, char='█')` |
| `bin_data(data, bins=5)` |
| `bootstrap(data, n_samples=1000, stat_fn=None)` |
| `box_plot(data, width=40)` |
| `correlation(x, y)` |
| `correlation_matrix(data_dict)` |
| `cosine_similarity(a, b)` |
| `covariance(x, y)` |
| `create_frame(data, columns=None)` |
| `cross_tab(data, row_fn, col_fn)` |
| `cumulative_sum(data)` |
| `data_types(data)` |
| `describe(data)` |
| `diff(data, periods=1)` |
| `euclidean_distance(a, b)` |
| `exponential_smoothing(data, alpha=0.3)` |
| `frequency_table(data)` |
| `from_csv(path, delimiter=',', has_header=True)` |
| `from_dict(d)` |
| `from_json(path)` |
| `from_records(records)` |
| `group_by(data, key_fn)` |
| `heatmap(matrix, row_labels=None, col_labels=None)` |
| `histogram(data, bins=10, width=40, char='█')` |
| `iqr(data)` |
| `kmeans(data, k=3, max_iter=100)` |
| `kurtosis(data)` |
| `lag(data, k=1)` |
| `line_chart(data, width=60, height=15)` |
| `linear_regression(x, y)` |
| `log_transform(data, base=None)` |
| `manhattan_distance(a, b)` |
| `mean(data)` |
| `median(data)` |
| `min_max_scale(data, feature_range=(0, 1))` |
| `missing_values(data)` |
| `mode(data)` |
| `moving_average(data, window=3)` |
| `normalize(data, low=0, high=1)` |
| `outliers(data, threshold=1.5)` |
| `percentile(data, p)` |
| `pivot_table(data, index_fn, value_fn, agg='sum')` |
| `predict_linear(model, x_val)` |
| `profile(data)` |
| `quartiles(data)` |
| `r_squared(x, y)` |
| `rank(data, method='average')` |
| `running_average(data)` |
| `sample(data, n=5, replace=False)` |
| `scatter_plot(x, y, width=40, height=20)` |
| `seasonality(data, period=7)` |
| `silhouette_score(data, labels)` |
| `skewness(data)` |
| `sparkline(data)` |
| `standardize(data)` |
| `stdev(data)` |
| `stratified_sample(data, labels, n_per_group=2)` |
| `summary(data)` |
| `trend(data)` |
| `unique_counts(data)` |
| `value_counts(data)` |
| `variance(data)` |
| `zscore(data)` |


---

## Arcane.Functional

Utilitários funcionais: composição, lentes, Maybe/Either, transdutores.

```dataforge
adopt Arcane.Functional as Functional
```

**Funções (56)**

| Assinatura |
|------------|
| `all_pass(*preds)` |
| `any_pass(*preds)` |
| `both(f, g)` |
| `chunk(n, collection)` |
| `complement(fn)` |
| `compose(*fns)` |
| `constantly(x)` |
| `curry(fn, arity=None)` |
| `drop_while(fn, collection)` |
| `either(f, g)` |
| `filter(fn, collection)` |
| `flat_map(fn, collection)` |
| `flip(fn)` |
| `frequencies(collection)` |
| `from_either(left_fn, right_fn, e)` |
| `from_maybe(default, m)` |
| `group_by(fn, collection)` |
| `identity(x)` |
| `index_by(fn, collection)` |
| `interleave(*collections)` |
| `into(target_type, xform, collection)` |
| `is_just(m)` |
| `is_left(e)` |
| `is_nothing(m)` |
| `is_right(e)` |
| `just(value)` |
| `juxt(*fns)` |
| `left(value)` |
| `lens(*keys)` |
| `map(fn, collection)` |
| `match(value, *cases)` |
| `maybe(value)` |
| `memoize(fn)` |
| `nothing()` |
| `once(fn)` |
| `over(lens, fn, obj)` |
| `partial(fn, *args)` |
| `partition_by(fn, collection)` |
| `pipe(*fns)` |
| `reduce(fn, collection, initial=None)` |
| `right(value)` |
| `scan(fn, collection, initial)` |
| `set_lens(lens, value, obj)` |
| `sort_by(fn, collection)` |
| `spread(fn)` |
| `take_while(fn, collection)` |
| `tap(fn, value)` |
| `thread_first(value, *fns)` |
| `thread_last(value, *fns)` |
| `trampoline(fn, *args)` |
| `transduce(xform, reducer, initial, collection)` |
| `try_catch(fn)` |
| `unique_by(fn, collection)` |
| `view(lens, obj)` |
| `when(*conditions)` |
| `zip_with(fn, *collections)` |


---

## Arcane.Database

Banco de dados SQLite: tabelas, consultas, migrações e importação.

```dataforge
adopt Arcane.Database as Database
```

**Funções (64)**

| Assinatura |
|------------|
| `Model(db, table, schema=None)` |
| `QueryBuilder(db, table)` |
| `add_column(db, table, name, col_type='TEXT')` |
| `aggregate(db, table, agregados, group_by=None, where=None, order_by=None, limit=None)` |
| `backup(db, dest_path)` |
| `begin(db)` |
| `builder(db, table)` |
| `check_foreign_keys(db)` |
| `close(db)` |
| `columns(db, table)` |
| `commit(db)` |
| `connect(path)` |
| `count(db, table, where=None)` |
| `create_index(db, table, columns, unique=False, name=None)` |
| `create_model(db, table, schema)` |
| `create_search(db, table, columns, nome=None)` |
| `create_table(db, name, schema)` |
| `database_size(db)` |
| `delete(db, table, where=None)` |
| `drop_index(db, nome)` |
| `drop_table(db, name)` |
| `execute(db, sql, params=None)` |
| `execute_many(db, sql, params_list)` |
| `execute_script(db, script)` |
| `exists(db, table, where)` |
| `explain(db, sql, params=None)` |
| `export_csv(db, table, path)` |
| `export_json(db, table, path)` |
| `foreign_keys(db, table)` |
| `group_count(db, table, column, where=None, order_by='quantidade DESC', limit=None)` |
| `import_csv(db, table, path, has_header=True)` |
| `import_json(db, table, path)` |
| `in_transaction(db)` |
| `increment(db, table, column, delta=1, where=None)` |
| `indexes(db, table=None)` |
| `insert(db, table, data)` |
| `insert_many(db, table, records)` |
| `insert_or_ignore(db, table, data)` |
| `integrity(db)` |
| `memory()` |
| `migrate(db, migrations)` |
| `migrations_applied(db)` |
| `paginate(db, table, pagina=1, por_pagina=20, where=None, order_by=None, columns=None)` |
| `query(db, sql, params=None)` |
| `query_one(db, sql, params=None)` |
| `rollback(db)` |
| `rollback_migration(db, migrations, ate=None)` |
| `savepoint(db, nome, acao)` |
| `schema_sql(db, table=None)` |
| `search(db, table, termo, limit=20, nome=None, columns=None)` |
| `seed(db, table, records)` |
| `select(db, table, where=None, order_by=None, limit=None, columns=None)` |
| `slow_log(db)` |
| `stats(db)` |
| `table_exists(db, name)` |
| `table_info(db, table)` |
| `tables(db)` |
| `transacao(db, acao)` |
| `transaction(db, acao)` |
| `update(db, table, data, where)` |
| `upsert(db, table, data, chaves)` |
| `upsert_many(db, table, records, chaves)` |
| `vacuum(db)` |
| `watch_slow(db, acima_de_ms=50)` |


---

## Arcane.Excel

Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame.

```dataforge
adopt Arcane.Excel as Excel
```

**Funções (29)**

| Assinatura |
|------------|
| `addr(linha, coluna)` |
| `append(aba, linha_valores)` |
| `autofit(aba)` |
| `bold_row(aba, linha)` |
| `cell(aba, linha, coluna, valor=None)` |
| `col_letter(indice)` |
| `column(livro, nome_aba, coluna)` |
| `dims(livro, nome=None)` |
| `drop_sheet(livro, nome)` |
| `formula(aba, ref, expressao)` |
| `formulas(aba)` |
| `freeze(aba, ref='A2')` |
| `from_csv(caminho, separador=',', nome='Planilha1')` |
| `from_frame(frame, nome='Dados', livro=None)` |
| `get(aba, ref)` |
| `get_formula(aba, ref)` |
| `new()` |
| `parse_addr(ref)` |
| `quick(caminho, dados, nome='Planilha1', cabecalho=None)` |
| `read(caminho)` |
| `records(livro, nome=None)` |
| `rows(livro, nome=None)` |
| `save(livro, caminho)` |
| `set(aba, ref, valor)` |
| `sheet(livro, nome, dados=None, cabecalho=None)` |
| `sheets(livro)` |
| `to_csv(livro, caminho, nome=None, separador=',')` |
| `to_frame(livro, nome=None)` |
| `width(aba, coluna, largura)` |


---

## Arcane.Meta

Metadados de decorador: ler @Nome em tempo de execução.

```dataforge
adopt Arcane.Meta as Meta
```

**Funções (12)**

| Assinatura |
|------------|
| `arg(alvo, nome, indice=0, padrao=None)` |
| `descrever(alvo)` |
| `filtrar(valores, nome)` |
| `ler(alvo, nome)` |
| `limpar(alvo)` |
| `marcar(alvo, nome, *args, **kwargs)` |
| `metodos_com(alvo, nome)` |
| `nomes(alvo)` |
| `opcao(alvo, nome, chave, padrao=None)` |
| `tem(alvo, nome)` |
| `todos(alvo)` |
| `todos_de(alvo, nome)` |


---

## Kiln

Framework web: rotas, middleware, templates, sessão e arquivos estáticos.

```dataforge
adopt Kiln as Kiln
```

**Funções (73)**

| Assinatura |
|------------|
| `Sala(nome='sala')` |
| `after(app, funcao)` |
| `any(app, padrao, handler)` |
| `app(nome='kiln', **config)` |
| `audit(escrever=None, metodos=('POST', 'PUT', 'PATCH', 'DELETE'))` |
| `auditoria(escrever=None, metodos=('POST', 'PUT', 'PATCH', 'DELETE'))` |
| `auth(verificador, esquema='Bearer')` |
| `body_limit(bytes_maximos=1048576)` |
| `buscar(itens, req=None, campos=(), parametro='q')` |
| `cabecalhos_seguros(csp="default-src 'self'", hsts=False, frame='DENY', referrer='strict-origin-when-cross-origin', permissoes='geolocation=(), microphone=(), camera=()')` |
| `cache(segundos=60, privado=False)` |
| `comprimir(minimo=1024)` |
| `conferir(dados, esquema)` |
| `config(app, chave, valor)` |
| `cookie(resp, nome, valor, dias=None, http_only=True, caminho='/', same_site='Lax', seguro=False)` |
| `cors(origens='*', metodos=None, cabecalhos=None)` |
| `csrf(segredo, campo='_csrf', cabecalho='X-CSRF-Token')` |
| `csrf_token(req, segredo=None)` |
| `delete(app, padrao, handler)` |
| `escape(texto)` |
| `evento(dados, tipo='', identificador='', reconectar=0)` |
| `file(caminho, tipo=None, baixar=None)` |
| `forge(nome='kiln', **config)` |
| `get(app, padrao, handler)` |
| `group(app, prefixo, meio=None)` |
| `guard(condicao, status=403, mensagem='sem permissão')` |
| `head(app, padrao, handler)` |
| `header(resp, chave, valor)` |
| `html(texto, status=200, cabecalhos=None)` |
| `idempotente(janela=86400)` |
| `json(dados, status=200, cabecalhos=None)` |
| `limite_de_corpo(bytes_maximos=1048576)` |
| `listen(app, porta=8080, host='127.0.0.1', silencioso=False)` |
| `logger(formato='dev')` |
| `mount(app, prefixo, outro)` |
| `on_error(app, status, handler)` |
| `options(app, padrao, handler)` |
| `ordenar(itens, req=None, campos=None, padrao='')` |
| `paginar(itens, req=None, por_pagina=20, teto=100)` |
| `patch(app, padrao, handler)` |
| `post(app, padrao, handler)` |
| `put(app, padrao, handler)` |
| `rate_limit(maximo=60, janela=60)` |
| `redirect(destino, status=302)` |
| `render(app, nome, dados=None, status=200)` |
| `render_string(texto, dados=None)` |
| `request_id(cabecalho='X-Request-Id')` |
| `resource(app, base, controlador)` |
| `route(app, metodo, padrao, handler)` |
| `routes(app)` |
| `sala(nome='sala')` |
| `salvar_upload(arquivo, pasta, nome=None, limite=0, tipos=None)` |
| `secure_headers(csp="default-src 'self'", hsts=False, frame='DENY', referrer='strict-origin-when-cross-origin', permissoes='geolocation=(), microphone=(), camera=()')` |
| `serve(app, porta=8080, host='127.0.0.1')` |
| `session_end(app, req, resp)` |
| `session_start(app, req, resp, dados=None)` |
| `sign(dados, segredo)` |
| `sse(gerador, cabecalhos=None)` |
| `static(app, prefixo, pasta)` |
| `stats(app)` |
| `status(codigo, mensagem=None)` |
| `stop(app)` |
| `stream(gerador, tipo='text/plain; charset=utf-8', cabecalhos=None)` |
| `templates(app, pasta)` |
| `test(app, metodo, caminho, corpo=None, cabecalhos=None)` |
| `text(texto, status=200, cabecalhos=None)` |
| `unsign(token, segredo)` |
| `upload(req, campo)` |
| `uploads(req)` |
| `use(app, funcao)` |
| `validar(esquema, alvo='body')` |
| `validate(esquema, alvo='body')` |
| `ws(app, padrao, handler)` |


---

## Arcane.Test

Asserções e organização de suítes de teste.

```dataforge
adopt Arcane.Test as Test
```

**Funções (34)**

| Assinatura |
|------------|
| `add_test(suite, name, spec)` |
| `assert_all(collection, predicate, msg=None)` |
| `assert_any(collection, predicate, msg=None)` |
| `assert_between(value, low, high, msg=None)` |
| `assert_close(actual, expected, tolerance=0.001, msg=None)` |
| `assert_contains(collection, item, msg=None)` |
| `assert_deep_eq(a, b, msg=None)` |
| `assert_empty(collection, msg=None)` |
| `assert_eq(actual, expected, msg=None)` |
| `assert_false(value, msg=None)` |
| `assert_greater(a, b, msg=None)` |
| `assert_instance(obj, blueprint_name, msg=None)` |
| `assert_keys(d, *expected_keys, msg=None)` |
| `assert_length(collection, expected, msg=None)` |
| `assert_less(a, b, msg=None)` |
| `assert_match(string, pattern, msg=None)` |
| `assert_neq(actual, expected, msg=None)` |
| `assert_not_contains(collection, item, msg=None)` |
| `assert_not_empty(collection, msg=None)` |
| `assert_not_void(value, msg=None)` |
| `assert_sorted(collection, reverse=False, msg=None)` |
| `assert_throws(func, msg=None)` |
| `assert_true(value, msg=None)` |
| `assert_type(value, expected_type, msg=None)` |
| `assert_unique(collection, msg=None)` |
| `assert_void(value, msg=None)` |
| `benchmark(func, iterations=1000)` |
| `describe(name, tests)` |
| `it(description, test_func)` |
| `mock(return_value=None)` |
| `run(suite, tests)` |
| `run_suite(suite)` |
| `spy(func)` |
| `suite(name='Test Suite')` |


---

## Arcane.Regex

Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone).

```dataforge
adopt Arcane.Regex as Regex
```

**Constantes**

| Nome | Valor |
|------|-------|
| `DOTALL` | `re.DOTALL` |
| `IGNORECASE` | `re.IGNORECASE` |
| `MULTILINE` | `re.MULTILINE` |
| `patterns` | `{'email': '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-z…` |

**Funções (42)**

| Assinatura |
|------------|
| `between(pattern_start, pattern_end, string, flags=0)` |
| `clean_whitespace(string)` |
| `compile(pattern, flags=0)` |
| `count(pattern, string, flags=0)` |
| `escape(string)` |
| `explain(pattern)` |
| `extract(pattern, string, flags=0)` |
| `extract_emails(string)` |
| `extract_numbers(string)` |
| `extract_urls(string)` |
| `extract_words(string)` |
| `findall(pattern, string, flags=0)` |
| `finditer(pattern, string, flags=0)` |
| `findnamed(pattern, string, flags=0)` |
| `fullmatch(pattern, string, flags=0)` |
| `group_names(pattern)` |
| `highlight(pattern, string, before='[', after=']', flags=0)` |
| `is_cnpj(string)` |
| `is_cpf(string)` |
| `is_date(string)` |
| `is_email(string)` |
| `is_exactly(pattern, string, flags=0)` |
| `is_ipv4(string)` |
| `is_phone(string)` |
| `is_url(string)` |
| `mask(string, pattern, mask_char='*')` |
| `match(pattern, string, flags=0)` |
| `named(pattern, string, flags=0)` |
| `positions(pattern, string, flags=0)` |
| `remove_html(string)` |
| `replace_all(pattern, repl, string)` |
| `replace_map(pattern, table, string, flags=0)` |
| `risk(pattern)` |
| `safe_search(pattern, string, ms=100, flags=0)` |
| `search(pattern, string, flags=0)` |
| `split(pattern, string, maxsplit=0, flags=0)` |
| `split_keep(pattern, string, flags=0)` |
| `sub(pattern, repl, string, count=0, flags=0)` |
| `sub_with(pattern, action, string, count=0, flags=0)` |
| `subn(pattern, repl, string, count=0, flags=0)` |
| `test(pattern, string, flags=0)` |
| `word_count(string)` |


---

## Arcane.IO

Arquivos, diretórios, JSON, CSV e shell.

```dataforge
adopt Arcane.IO as IO
```

**Funções (33)**

| Assinatura |
|------------|
| `abs(path)` |
| `append(path, content)` |
| `append_bytes(path, content)` |
| `basename(path)` |
| `copy(src, dst)` |
| `copy_tree(origem, destino)` |
| `cwd()` |
| `delete(path)` |
| `dirname(path)` |
| `exists(path)` |
| `ext(path)` |
| `file_exists(path)` |
| `join(*parts)` |
| `list_dir(path='.')` |
| `listdir(path='.')` |
| `mkdir(path)` |
| `open(path, mode='r')` |
| `path(path)` |
| `read(path)` |
| `read_bytes(path)` |
| `read_csv(path, cabecalho=False)` |
| `read_file(path)` |
| `read_json(path)` |
| `remove_tree(path)` |
| `rename(old, new)` |
| `rmdir(path)` |
| `shell(command)` |
| `size(path)` |
| `write(path, content)` |
| `write_bytes(path, content)` |
| `write_csv(path, data)` |
| `write_file(path, content)` |
| `write_json(path, data, indent=2)` |


---

## Arcane.Http

Servidor HTTP: rotas, middleware, JSON, arquivos estáticos.

```dataforge
adopt Arcane.Http as Http
```

**Funções (17)**

| Assinatura |
|------------|
| `cors(app)` |
| `create(name='DataForge App')` |
| `delete(app, path, handler)` |
| `get(app, path, handler)` |
| `html_response(html, status=200)` |
| `json_parser(app)` |
| `json_response(data, status=200)` |
| `listen(app, port=3000, host='0.0.0.0')` |
| `logger(app)` |
| `patch(app, path, handler)` |
| `post(app, path, handler)` |
| `put(app, path, handler)` |
| `route(app, method, path, handler)` |
| `static(app, directory)` |
| `stop(app)` |
| `templates(app, directory)` |
| `use(app, middleware)` |


---

## Arcane.Async

Promessas, filas, agendamento e execução concorrente.

```dataforge
adopt Arcane.Async as Async
```

**Funções (52)**

| Assinatura |
|------------|
| `all(promises)` |
| `any(promises)` |
| `ao_criar(funcao)` |
| `ao_falhar(funcao)` |
| `ao_terminar(funcao)` |
| `batch(fn)` |
| `buffer_op(size)` |
| `catch(promise, callback)` |
| `channel(buffer_size=0)` |
| `combine_latest(*observables)` |
| `computed(signals, fn)` |
| `debounce_op(ms)` |
| `delay(ms, fn=None)` |
| `distinct_op()` |
| `effect(signals, fn)` |
| `emit(emitter, event, *data)` |
| `emit_event(emitter, event, *data)` |
| `emitter()` |
| `esperar_todas(prazo=None)` |
| `event_emitter()` |
| `filter_op(fn)` |
| `from_list(lst)` |
| `interval(ms, count=10)` |
| `map_op(fn)` |
| `merge(*observables)` |
| `observable(producer=None)` |
| `of(*values)` |
| `off(emitter, event, callback=None)` |
| `on(emitter, event, callback)` |
| `once_event(emitter, event, callback)` |
| `parallel(*fns)` |
| `pipe_stream(observable, *operators)` |
| `promise(executor)` |
| `race(promises)` |
| `receive(ch)` |
| `reject(error)` |
| `resolve(value)` |
| `retry_task(fn, max_retries=3, delay_ms=100)` |
| `scan_op(fn, initial)` |
| `sem_ganchos()` |
| `send(ch, value)` |
| `sequential(*fns)` |
| `settled(promises)` |
| `signal(initial_value)` |
| `skip_op(n)` |
| `subject()` |
| `subscribe(observable, callback)` |
| `take_op(n)` |
| `task(fn)` |
| `then(promise, callback)` |
| `timeout(ms, fn)` |
| `vivas()` |


---

## Arcane.Data

DataFrames, séries e transformações tabulares.

```dataforge
adopt Arcane.Data as Data
```

**Funções (13)**

| Assinatura |
|------------|
| `Frame(data=None, columns=None)` |
| `correlate(x, y)` |
| `describe(data)` |
| `group_by(data, key_func)` |
| `merge(left, right, on)` |
| `normalize(data, min_val=0, max_val=1)` |
| `one_hot(labels)` |
| `pivot(data, index_col, value_col, agg='sum')` |
| `read_csv(path, header=True)` |
| `read_json(path)` |
| `series(data, name='series')` |
| `split(data, ratio=0.8)` |
| `standardize(data)` |


---

## Arcane.Web

Cliente HTTP, URL encoding e JSON.

```dataforge
adopt Arcane.Web as Web
```

**Funções (11)**

| Assinatura |
|------------|
| `check(user_id=None)` |
| `close()` |
| `decode_url(text)` |
| `encode_url(text)` |
| `get(url, headers=None)` |
| `json_parse(text)` |
| `json_stringify(obj, indent=None)` |
| `post(url, data=None, headers=None)` |
| `request(url, method='GET', data=None, headers=None)` |
| `serve(port=8080, host='0.0.0.0')` |
| `socket(host, port)` |


---

## Arcane.Cortex

Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA.

```dataforge
adopt Arcane.Cortex as Cortex
```

**Funções (25)**

| Assinatura |
|------------|
| `acuracia(reais, previstos)` |
| `aplicar_escala(linhas, escala)` |
| `arvore(linhas, alvo, colunas, profundidade=6, minimo=2)` |
| `avaliar(modelo, linhas)` |
| `bayes_texto(linhas, alvo, coluna)` |
| `carregar(caminho)` |
| `categorico(linhas, coluna, prefixo='')` |
| `dividir(linhas, proporcao=0.2, semente=42, estratificar='')` |
| `embaralhar(linhas, semente=42)` |
| `erro(reais, previstos)` |
| `escalonar(linhas, colunas)` |
| `floresta(linhas, alvo, colunas, arvores=20, profundidade=8, minimo=2, semente=42)` |
| `importancia(modelo)` |
| `kmedias(linhas, colunas, grupos=3, voltas=50, semente=42)` |
| `linear(linhas, alvo, colunas)` |
| `logistica(linhas, alvo, colunas, voltas=300, taxa=0.1)` |
| `matriz(modelo, linhas)` |
| `pca(linhas, colunas, componentes=2)` |
| `prever(modelo, linhas)` |
| `prever_um(modelo, linha)` |
| `probabilidade(modelo, linha)` |
| `resumo(modelo)` |
| `salvar(modelo, caminho)` |
| `validacao_cruzada(linhas, alvo, colunas, especie='floresta', dobras=5, semente=42, **extras)` |
| `vizinhos(linhas, alvo, colunas, k=5)` |


---

## Arcane.Time

Datas, horas, durações e cronometragem.

```dataforge
adopt Arcane.Time as Time
```

**Funções (54)**

| Assinatura |
|------------|
| `add_days(d, n)` |
| `add_hours(d, n)` |
| `add_minutes(d, n)` |
| `add_months(d, n)` |
| `add_seconds(d, n)` |
| `add_weeks(d, n)` |
| `add_years(d, n)` |
| `age(nascimento, referencia=None)` |
| `date(ano, mes, dia)` |
| `datetime(ano, mes, dia, hora=0, minuto=0, segundo=0)` |
| `day(d)` |
| `day_of_year(d)` |
| `days_between(a, b)` |
| `days_in_month(a, m)` |
| `diff(a, b)` |
| `duration(dias=0, horas=0, minutos=0, segundos=0)` |
| `end_of_day(d)` |
| `end_of_month(d)` |
| `format(d, formato='%Y-%m-%d %H:%M:%S')` |
| `from_iso(t)` |
| `from_timestamp(ts)` |
| `hour(d)` |
| `humanize(s)` |
| `is_after(a, b)` |
| `is_before(a, b)` |
| `is_leap_year(a)` |
| `is_same_day(a, b)` |
| `is_weekend(d)` |
| `measure(acao)` |
| `minute(d)` |
| `monotonic()` |
| `month(d)` |
| `month_name(d, curto=False)` |
| `now()` |
| `parse(texto, formato=None)` |
| `quarter(d)` |
| `second(d)` |
| `sleep(s)` |
| `start_of_day(d)` |
| `start_of_month(d)` |
| `stopwatch()` |
| `timestamp()` |
| `timezone_offset()` |
| `to_br(d)` |
| `to_date_string(d)` |
| `to_iso(d)` |
| `to_time_string(d)` |
| `to_utc(d)` |
| `today()` |
| `utcnow()` |
| `week_of_year(d)` |
| `weekday(d)` |
| `weekday_name(d, curto=False)` |
| `year(d)` |


---

## Arcane.OS

Sistema operacional, ambiente, disco e processo atual.

```dataforge
adopt Arcane.OS as OS
```

**Funções (43)**

| Assinatura |
|------------|
| `arch()` |
| `argv()` |
| `argv_completo()` |
| `beside(*partes)` |
| `chdir(caminho)` |
| `cpu_count()` |
| `cwd()` |
| `disk_usage(caminho='.')` |
| `env()` |
| `env_names()` |
| `executable()` |
| `exit(codigo=0)` |
| `get_env(nome, padrao=None)` |
| `has_env(nome)` |
| `home()` |
| `hostname()` |
| `info()` |
| `is_linux()` |
| `is_mac()` |
| `is_posix()` |
| `is_tty()` |
| `is_windows()` |
| `line_separator()` |
| `machine()` |
| `memory_info()` |
| `name()` |
| `parent_pid()` |
| `path_separator()` |
| `pid()` |
| `platform()` |
| `processor()` |
| `python_version()` |
| `release()` |
| `script()` |
| `script_dir()` |
| `separator()` |
| `set_env(nome, valor)` |
| `temp_dir()` |
| `terminal_size()` |
| `unset_env(nome)` |
| `user()` |
| `version()` |
| `which(prog)` |


---

## Arcane.Process

Execução de processos externos, com stdout, stderr e código de saída.

```dataforge
adopt Arcane.Process as Process
```

**Funções (15)**

| Assinatura |
|------------|
| `capture(comando, shell=False, timeout=None)` |
| `check(comando, shell=False, timeout=None)` |
| `exists(prog)` |
| `exit_code(comando, shell=False, timeout=None)` |
| `is_running(processo)` |
| `kill(processo)` |
| `pid()` |
| `pipeline(comandos, timeout=None)` |
| `python()` |
| `run(comando, shell=False, timeout=None, cwd=None, env=None, input_text=None)` |
| `run_shell(cmd, timeout=None)` |
| `spawn(comando, shell=False, cwd=None)` |
| `terminate(processo)` |
| `wait(processo, timeout=None)` |
| `which(programa)` |


---

## Arcane.Logging

Registro estruturado de eventos, com níveis e destinos.

```dataforge
adopt Arcane.Logging as Logging
```

**Funções (14)**

| Assinatura |
|------------|
| `as_json(a=True)` |
| `debug(m, campos=None)` |
| `default()` |
| `error(m, campos=None)` |
| `fatal(m, campos=None)` |
| `info(m, campos=None)` |
| `levels()` |
| `log(n, m, campos=None)` |
| `logger(nome='app', nivel='INFO')` |
| `set_level(n)` |
| `stats()` |
| `to_file(c, anexar=True)` |
| `trace(m, campos=None)` |
| `warn(m, campos=None)` |


---

## Arcane.Crypto

Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305). Assina e verifica JWT (HS256/384/512), com o algoritmo decidido por quem verifica e não pelo token.

```dataforge
adopt Arcane.Crypto as Crypto
```

**Funções (53)**

| Assinatura |
|------------|
| `algorithms()` |
| `apagar_seguro(caminho, passadas=1)` |
| `base32_decode(v)` |
| `base32_encode(v)` |
| `base64_decode(texto)` |
| `base64_encode(v)` |
| `base64url_decode(texto)` |
| `base64url_encode(v)` |
| `blake2b(v)` |
| `blake2s(v)` |
| `chave_nova(tamanho=32)` |
| `cifrar(dados, senha, iteracoes=None)` |
| `cifrar_arquivo(origem, destino='', senha='', iteracoes=None)` |
| `cifrar_pasta(pasta, destino='', senha='')` |
| `constant_time_equals(a, b)` |
| `decifrar(pacote, senha)` |
| `decifrar_arquivo(origem, destino='', senha='')` |
| `derivar_chave(senha, sal='', iteracoes=None)` |
| `e_cifrado(caminho)` |
| `hash(valor, algoritmo='sha256')` |
| `hash_file(caminho, algoritmo='sha256')` |
| `hash_password(senha, iteracoes=None, algoritmo='scrypt')` |
| `hex_decode(v)` |
| `hex_encode(v)` |
| `hmac(chave, mensagem, algoritmo='sha256')` |
| `hmac_verify(chave, mensagem, assinatura, algoritmo='sha256')` |
| `informacao_do_cofre(caminho)` |
| `jwt_algoritmos()` |
| `jwt_assinar(carga, chave, algoritmo='HS256', expira_em=0)` |
| `jwt_ler(token)` |
| `jwt_verificar(token, chave, algoritmo='HS256')` |
| `mask(texto, visiveis=4, caractere='*')` |
| `md5(v)` |
| `pbkdf2(senha, sal, iteracoes=200000, algoritmo='sha256')` |
| `precisa_rehash(guardada)` |
| `random_bytes(n=32)` |
| `random_choice(itens)` |
| `random_hex(n=32)` |
| `random_int(a, b)` |
| `random_password(tamanho=16, simbolos=True)` |
| `random_token(n=32)` |
| `rot13(t)` |
| `sha1(v)` |
| `sha224(v)` |
| `sha256(v)` |
| `sha384(v)` |
| `sha512(v)` |
| `short_id(n=12)` |
| `uuid()` |
| `uuid4()` |
| `uuid_hex()` |
| `verify_password(senha, guardada)` |
| `xor_cipher(texto, chave)` |


---

## Arcane.Seguranca

Escape por destino (HTML, atributo, JS, URL, shell, SQL LIKE, CSV, cabeçalho, log), sanitização de HTML por lista de permitidos, política e força de senha com vazamento por k-anonimato, TOTP/HOTP e códigos de recuperação, token e URL assinados com prazo e propósito, varredura de segredos por formato, redação de PII, defesa de SSRF e de travessia de caminho, limitador de taxa, bloqueio progressivo, trilha de auditoria encadeada e dez regras de análise estática.

```dataforge
adopt Arcane.Seguranca as Seguranca
```

**Funções (54)**

| Assinatura |
|------------|
| `analisar(fonte, caminho='')` |
| `assinar(valor, chave, proposito='', quando=None)` |
| `assinar_url(url, chave, prazo=3600, quando=None)` |
| `auditoria(caminho)` |
| `caminho_seguro(base, pedido)` |
| `chave_de_assinatura(bytes_=32)` |
| `codigos_de_recuperacao(quantos=10, grupos=3, tamanho=4)` |
| `conferir_pkce(verificador, desafio)` |
| `conferir_url(url, chave, quando=None)` |
| `conferir_vazamento(senha, respostas)` |
| `e_alta_entropia(texto, minimo=3.5)` |
| `e_segredo(v)` |
| `entropia(texto)` |
| `escapar_atributo(texto)` |
| `escapar_cabecalho(texto)` |
| `escapar_csv(valor)` |
| `escapar_html(texto)` |
| `escapar_js(texto)` |
| `escapar_log(texto)` |
| `escapar_regex(texto)` |
| `escapar_shell(texto)` |
| `escapar_sql_like(texto, escape='\\')` |
| `escapar_url(texto)` |
| `estado_de_oauth(bytes_=32)` |
| `exigir_politica(senha, opcoes=None)` |
| `exigir_sem_segredo(texto, onde='')` |
| `forca_da_senha(senha)` |
| `host_privado(host)` |
| `hotp(segredo, contador, digitos=6, algoritmo='sha1')` |
| `json_seguro(texto, opcoes=None)` |
| `ler_assinado(token, chave, prazo=None, proposito='')` |
| `limitador(limite, periodo=60.0, rajada=None)` |
| `limpar_html(texto, opcoes=None)` |
| `mascarar(valor, visivel=4)` |
| `mascarar_pii(texto, tipos=None)` |
| `nome_de_arquivo_seguro(nome, padrao='arquivo')` |
| `numero_seguro(texto, minimo=None, maximo=None, inteiro=True)` |
| `padroes_de_segredo()` |
| `pkce(tamanho=64)` |
| `politica(senha, opcoes=None)` |
| `prefixo_vazamento(senha)` |
| `procurar_segredos(texto, opcoes=None)` |
| `redigir(texto)` |
| `redirecionamento_seguro(destino, permitidos=None, padrao='/')` |
| `regras_de_analise()` |
| `segredo(valor, rotulo='segredo')` |
| `sem_controle(texto, permitir_quebra=False)` |
| `tentativas(limite=5, base=30.0, teto=3600.0)` |
| `totp_agora(segredo, janela=30, digitos=6, algoritmo='sha1', quando=None)` |
| `totp_conferir(segredo, codigo, janela=30, digitos=6, algoritmo='sha1', tolerancia=1, quando=None)` |
| `totp_segredo(bytes_=20)` |
| `totp_uri(segredo, conta, emissor='', digitos=6, janela=30, algoritmo='sha1')` |
| `url_segura(url, opcoes=None)` |
| `vazada(senha, tempo_limite=5.0)` |


---

## Arcane.Politica

Motor de autorização: RBAC com herança, ABAC por atributo, ACL por objeto, grupos, isolamento por inquilino, negação explícita que vence o papel e delegação com prazo. O padrão é negar, e toda decisão diz qual regra a tomou — um motor que responde só sim/não é impossível de auditar.

```dataforge
adopt Arcane.Politica as Politica
```

**Funções (6)**

| Assinatura |
|------------|
| `camadas()` |
| `casa(padrao, concreto)` |
| `de_vault(nome, definicao)` |
| `identidade(alvo)` |
| `motor(nome, inquilino='')` |
| `separacao_de_funcoes(politica, acao, solicitante, aprovador)` |


---

## Arcane.Chaves

Ciclo de vida de chave criptográfica: propósito cobrado, prazo, rotação que mantém as antigas decifrando o passado, identificador no dado cifrado, cifragem em envelope (DEK/KEK), recifragem, derivação por contexto (HKDF) e exportação do cofre cifrada pela senha mestra.

```dataforge
adopt Arcane.Chaves as Chaves
```

**Constantes**

| Nome | Valor |
|------|-------|
| `ESTADOS` | `['ativa', 'aposentada', 'revogada']` |
| `PROPOSITOS` | `['assinar', 'cifrar', 'derivar', 'autenticar']` |

**Funções (4)**

| Assinatura |
|------------|
| `cofre(opcoes=None)` |
| `derivar_de(chave, contexto, tamanho=32)` |
| `e_chave(v)` |
| `usar(chave, proposito)` |


---

## Arcane.Deteccao

Regras de detecção sobre eventos, com correlação por chave em janela deslizante, supressão, gravidade e mapa para MITRE ATT&CK; indicadores de comprometimento com prazo e normalização; padrões sobre conteúdo e leitura de log de acesso. O alerta carrega os eventos que o causaram.

```dataforge
adopt Arcane.Deteccao as Deteccao
```

**Constantes**

| Nome | Valor |
|------|-------|
| `GRAVIDADES` | `['informativo', 'baixo', 'medio', 'alto', 'critico…` |
| `TIPOS_DE_INDICADOR` | `['ip', 'dominio', 'url', 'hash', 'email', 'usuario…` |

**Funções (5)**

| Assinatura |
|------------|
| `indicadores()` |
| `ler_linha(linha, formato='combinado')` |
| `motor()` |
| `padrao(nome, textos, gravidade='medio', descricao='')` |
| `varrer(conteudo, padroes, minimo=1)` |


---

## Arcane.GitHub

O que um programa precisa para viver no GitHub: no Actions, saídas, variáveis e resumo com delimitador seguro, anotações escapadas que aparecem na linha do PR, máscara linha a linha e grupos; webhooks com assinatura HMAC conferida em tempo constante sobre os bytes originais; e a API REST com paginação por Link e o limite de taxa que sobrou.

```dataforge
adopt Arcane.GitHub as GitHub
```

**Funções (19)**

| Assinatura |
|------------|
| `ClienteGitHub(token='', base='https://api.github.com', prazo=30.0)` |
| `anotacao(nivel, mensagem, arquivo='', linha=0, coluna=0, titulo='', fim_linha=0)` |
| `anotar(nivel, mensagem, arquivo='', linha=0, coluna=0, titulo='')` |
| `assinatura(segredo, corpo)` |
| `cliente(token='', base='https://api.github.com', prazo=30.0)` |
| `conferir_webhook(segredo, corpo, cabecalho)` |
| `contexto()` |
| `em_actions()` |
| `escapar_dado(texto)` |
| `escapar_propriedade(texto)` |
| `evento()` |
| `evento_de_webhook(cabecalhos, corpo, segredo)` |
| `exportar(nome, valor)` |
| `grupo(nome, acao)` |
| `mascarar_no_log(valor)` |
| `no_path(pasta)` |
| `resumo(markdown)` |
| `saida(nome, valor)` |
| `tabela_markdown(linhas, colunas=None)` |


---

## Arcane.Gramatica

A gramática da linguagem como dado: as produções em EBNF, cada uma com um exemplo conferido contra o parser, a tabela de precedência provada pela árvore, os tokens de um texto, as instruções que o parser entendeu e a validação de sintaxe sem executar nada.

```dataforge
adopt Arcane.Gramatica as Gramatica
```

**Funções (10)**

| Assinatura |
|------------|
| `ebnf(grupo='')` |
| `grupos()` |
| `instrucoes(texto)` |
| `palavras()` |
| `precedencia()` |
| `producao(nome)` |
| `producoes(grupo='')` |
| `raiz(expressao)` |
| `tokens(texto)` |
| `validar(texto)` |


---

## Arcane.Privacidade

O que a LGPD pede, como operações sobre dado: pseudonimização com chave (e não hash sem chave, que se desfaz), generalização de quase-identificadores, a medida do k-anonimato, minimização por lista de permitidos, retenção, consentimento por titular e por finalidade com histórico, os direitos de acesso e eliminação percorrendo todo lugar onde o dado mora, e contagem com privacidade diferencial.

```dataforge
adopt Arcane.Privacidade as Privacidade
```

**Funções (10)**

| Assinatura |
|------------|
| `Consentimentos()` |
| `Titulares()` |
| `consentimentos()` |
| `contagem_privada(n, epsilon=1.0, semente=None)` |
| `generalizar(valor, tipo, nivel=1)` |
| `k_anonimato(linhas, quase_identificadores)` |
| `minimizar(linha, permitidos)` |
| `pseudonimizar(valor, chave, finalidade='', tamanho=16)` |
| `titulares()` |
| `vencidos(linhas, campo_data, dias, agora=None)` |


---

## Arcane.Integridade

Provar que o que está aqui é o que foi posto aqui: o valor SRI de um script de CDN, o manifesto SHA-256 de uma pasta com o que foi acrescentado, removido e alterado, e o manifesto assinado com uma chave que mora fora dali.

```dataforge
adopt Arcane.Integridade as Integridade
```

**Funções (6)**

| Assinatura |
|------------|
| `assinar_manifesto(m, chave)` |
| `conferir_manifesto(pasta, esperado, ignorar=None)` |
| `conferir_sri(conteudo, integridade)` |
| `manifesto(pasta, ignorar=None)` |
| `sri(conteudo, algoritmo='sha384')` |
| `verificar_manifesto(assinado, chave)` |


---

## Arcane.Collections

Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca.

```dataforge
adopt Arcane.Collections as Collections
```

**Funções (63)**

| Assinatura |
|------------|
| `add(conjunto, item)` |
| `batched(itens, n)` |
| `binary_search(ordenado, alvo)` |
| `bottom_n(itens, n, chave=None)` |
| `cartesian(a, b)` |
| `chain_vaults(*vaults)` |
| `chunk_evenly(itens, partes)` |
| `counter(itens=None)` |
| `deep_merge(a, b)` |
| `default_vault(padrao=None)` |
| `deque(itens=None, maximo=0)` |
| `difference(a, b)` |
| `discard(conjunto, item)` |
| `elements(contagem)` |
| `extend_left(fila, itens)` |
| `first_key(v)` |
| `flatten_deep(itens, profundidade=-1)` |
| `frozen(itens)` |
| `graph(dirigido=False)` |
| `group(itens, chave)` |
| `group_by(itens, chave)` |
| `heap(itens=None)` |
| `heap_peek(h)` |
| `heap_pop(h)` |
| `heap_push(h, item)` |
| `index_by(itens, chave)` |
| `intersection(a, b)` |
| `is_disjoint(a, b)` |
| `is_subset(a, b)` |
| `is_superset(a, b)` |
| `last_key(v)` |
| `merge_sorted(a, b)` |
| `most_common(fonte, n=0)` |
| `move_to_end(v, chave, para_o_fim=True)` |
| `n_largest(itens, n, chave=None)` |
| `n_smallest(itens, n, chave=None)` |
| `named(nome, campos, valores)` |
| `ordered(pares=None)` |
| `ordered_vault(pares=None)` |
| `pairwise(itens)` |
| `partition(itens, predicado)` |
| `peek(fila)` |
| `peek_left(fila)` |
| `pop(fila)` |
| `pop_left(fila)` |
| `priority_queue()` |
| `push(fila, item)` |
| `push_left(fila, item)` |
| `queue(itens=None)` |
| `rotate(colecao, n=1)` |
| `set(itens=None)` |
| `sliding_window(itens, tamanho)` |
| `sort_by(itens, chave)` |
| `sort_by_field(itens, campo, reverso=False)` |
| `stack(itens=None)` |
| `subtract(a, b)` |
| `symmetric_difference(a, b)` |
| `top_n(itens, n, chave=None)` |
| `total(contagem)` |
| `union(a, b)` |
| `union_find(itens=None)` |
| `unique_by(itens, chave)` |
| `zip_longest(a, b, preencher=None)` |


---

## Arcane.Serialization

JSON, CSV, INI, TOML, XML e conversões entre eles.

```dataforge
adopt Arcane.Serialization as Serialization
```

**Funções (26)**

| Assinatura |
|------------|
| `csv_to_records(texto, delimitador=',')` |
| `deep_copy(d)` |
| `flatten(dados, separador='.', prefixo='')` |
| `formats()` |
| `from_base64(t)` |
| `from_bytes(b)` |
| `from_csv(texto, delimitador=',', tem_cabecalho=False)` |
| `from_ini(texto)` |
| `from_json(texto)` |
| `from_json_lines(texto)` |
| `from_json_safe(texto, padrao=None)` |
| `from_toml(texto)` |
| `from_xml(texto)` |
| `is_valid_json(texto)` |
| `json_lines(registros)` |
| `json_path(dados, caminho, padrao=None)` |
| `json_pretty(d, indent=2)` |
| `records_to_csv(registros, delimitador=',')` |
| `to_base64(d)` |
| `to_bytes(d)` |
| `to_csv(linhas, delimitador=',', cabecalho=None)` |
| `to_ini(dados)` |
| `to_json(dados, indent=None, ordenar=False)` |
| `to_toml(dados)` |
| `to_xml(dados, raiz='root')` |
| `unflatten(plano, separador='.')` |


---

## Arcane.Forge

Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface.

```dataforge
adopt Arcane.Forge as Forge
```

**Funções (31)**

| Assinatura |
|------------|
| `buscar_modelo(nome)` |
| `colunas(db, t)` |
| `compose(url, servico='banco', volume=True)` |
| `conectar(url, **opcoes)` |
| `conexao(pool)` |
| `consultar(conexao, sql, parametros=None)` |
| `de(conexao, tabela)` |
| `de_ambiente(padrao='', variavel='', **opcoes)` |
| `de_csv(caminho_ou_texto)` |
| `dialetos()` |
| `esperar(url, prazo=30.0, intervalo=0.5, **opcoes)` |
| `executar(conexao, sql, parametros=None)` |
| `fechar(db)` |
| `ligar(modelo, conexao)` |
| `limpar_modelos()` |
| `memoria()` |
| `migracoes(conexao)` |
| `migrar_tudo(conexao)` |
| `modelo(nome, campos=None, opcoes=None)` |
| `modelos()` |
| `motores()` |
| `para_csv(linhas, caminho='')` |
| `ping(db)` |
| `pool(url, tamanho=5, **o)` |
| `primeiro(conexao, sql, parametros=None)` |
| `tabela(conexao, tabela)` |
| `tabelas(db)` |
| `tipos()` |
| `transacao(conexao, corpo)` |
| `url(url)` |
| `versao(db)` |


---

## Arcane.Crucible

Framework de testes: suítes, matchers, fixtures, dublês e benchmark.

```dataforge
adopt Arcane.Crucible as Crucible
```

**Constantes**

| Nome | Valor |
|------|-------|
| `matchers_novos` | `['to_be_one_of', 'to_be_ordered_by', 'to_be_subset…` |
| `mutacoes` | `[{'de': 'bigger_eq', 'para': 'bigger', 'descricao'…` |

**Funções (59)**

| Assinatura |
|------------|
| `after(corpo)` |
| `after_all(corpo)` |
| `approx(valor, casas=7)` |
| `banco(db)` |
| `before(corpo)` |
| `before_all(corpo)` |
| `benchmark(nome, acao, vezes=1000, aquecimento=10)` |
| `booleans()` |
| `capture(acao)` |
| `cenario(nome)` |
| `check(condicao, mensagem='a condicao nao se cumpriu')` |
| `clusters(item=None, tamanho_max=10)` |
| `com_relogio(acao, inicio=None)` |
| `contrato(nome, casos)` |
| `corrida(acao, threads=4, voltas=5000, leitor=None, esperado=None)` |
| `database(db)` |
| `describe(nome, corpo=None)` |
| `determinismo(acao, vezes=5)` |
| `diff(esperado, obtido)` |
| `expect(valor, rotulo='')` |
| `fail(mensagem='falhou por decisao do teste')` |
| `fixture(nome, corpo)` |
| `flaky(acao, tentativas=3, espera=0.0)` |
| `floats(minimo=-1000.0, maximo=1000.0)` |
| `forall(gerador, propriedade, casos=100, semente=None)` |
| `freeze_time(instante)` |
| `instantaneo(nome, valor, atualizar=None)` |
| `instavel(acao, tentativas=3, espera=0.0)` |
| `integers(minimo=-1000, maximo=1000)` |
| `json()` |
| `junit()` |
| `mock(nome='mock', alvo=None)` |
| `mutar(arquivo, rodar_testes, limite=40)` |
| `one_of(valores)` |
| `only(nome, corpo, tags=None)` |
| `pending(nome, motivo='', corpo=None)` |
| `relatorio_de_mutacao(resultado)` |
| `relogio(inicio=None)` |
| `report(colorir=True, verboso=False)` |
| `reset()` |
| `results()` |
| `run(opcoes=None)` |
| `servidor_falso(porta=0)` |
| `snapshot(nome, valor, atualizar=None)` |
| `snapshot_dir(arquivo)` |
| `spy(alvo, nome='spy')` |
| `stub(respostas=None, nome='stub')` |
| `suite(nome, corpo=None)` |
| `summary()` |
| `table(nome, casos, corpo, tags=None)` |
| `tag(*nomes)` |
| `tap()` |
| `temp_dir()` |
| `temp_file(conteudo='', sufixo='.txt')` |
| `test(nome, corpo, tags=None, prazo=0, repetir=1, dados=None)` |
| `texts(tamanho_max=20, alfabeto=None)` |
| `timed(acao, vezes=1)` |
| `trial(nome, corpo, tags=None, prazo=0, repetir=1, dados=None)` |
| `vaults(valor=None, tamanho_max=6)` |


---

## Arcane.Iter

Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize.

```dataforge
adopt Arcane.Iter as Iter
```

**Funções (44)**

| Assinatura |
|------------|
| `accumulate(fonte, funcao=None, inicial=None)` |
| `attr(nome)` |
| `batched(fonte, tamanho)` |
| `cache_info(memoizada)` |
| `chain(*fontes)` |
| `chunk(fonte, tamanho)` |
| `combinations(fonte, tamanho)` |
| `combinations_with_repetition(fonte, tamanho)` |
| `compose(*acoes)` |
| `compress(fonte, marcas)` |
| `constant(valor)` |
| `count(inicio=0, passo=1)` |
| `curry(funcao, aridade=2)` |
| `cycle_forever(itens)` |
| `drop(fonte, n)` |
| `drop_while(fonte, condicao)` |
| `filter_false(fonte, condicao)` |
| `flat_map(fonte, funcao)` |
| `flatten(fonte, profundidade=1)` |
| `flip(funcao)` |
| `group_runs(fonte, chave=None)` |
| `identity(x)` |
| `item(indice)` |
| `memoize(funcao, tamanho=128)` |
| `once(funcao)` |
| `op(simbolo)` |
| `pairwise(fonte)` |
| `partial(funcao, *fixos, **nomeados)` |
| `permutations(fonte, tamanho=0)` |
| `pipe(*acoes)` |
| `powerset(fonte)` |
| `product(*fontes, repetir=1)` |
| `reduce(fonte, funcao, inicial=None)` |
| `repeat(valor, vezes=0)` |
| `running_max(fonte)` |
| `running_sum(fonte)` |
| `slice(fonte, inicio, fim=None, passo=1)` |
| `take(fonte, n)` |
| `take_while(fonte, condicao)` |
| `to_cluster(fonte)` |
| `unique(fonte)` |
| `unique_by(fonte, chave)` |
| `window(fonte, tamanho)` |
| `zip_longest(a, b, preencher=None)` |


---

## Arcane.Color

Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore.

```dataforge
adopt Arcane.Color as Color
```

**Funções (66)**

| Assinatura |
|------------|
| `auto()` |
| `badge(texto, cor='blue')` |
| `bar(valor, total, largura=30, cor='green', mostrar_numero=True)` |
| `bg_rgb(texto, r, g, b)` |
| `black(texto)` |
| `blink(texto)` |
| `blue(texto)` |
| `bold(texto)` |
| `box(texto, titulo='', cor='cyan', largura=0)` |
| `bright_blue(texto)` |
| `bright_cyan(texto)` |
| `bright_green(texto)` |
| `bright_magenta(texto)` |
| `bright_red(texto)` |
| `bright_white(texto)` |
| `bright_yellow(texto)` |
| `cyan(texto)` |
| `dim(texto)` |
| `error(texto)` |
| `force(ligado=True)` |
| `gradient(texto, de, para)` |
| `gray(texto)` |
| `green(texto)` |
| `grey(texto)` |
| `hex(texto, cor)` |
| `hidden(texto)` |
| `info()` |
| `info_msg(texto)` |
| `italic(texto)` |
| `magenta(texto)` |
| `muted(texto)` |
| `on_black(texto)` |
| `on_blue(texto)` |
| `on_bright_blue(texto)` |
| `on_bright_cyan(texto)` |
| `on_bright_green(texto)` |
| `on_bright_magenta(texto)` |
| `on_bright_red(texto)` |
| `on_bright_white(texto)` |
| `on_bright_yellow(texto)` |
| `on_cyan(texto)` |
| `on_gray(texto)` |
| `on_green(texto)` |
| `on_grey(texto)` |
| `on_magenta(texto)` |
| `on_red(texto)` |
| `on_white(texto)` |
| `on_yellow(texto)` |
| `paint(texto, *nomes)` |
| `rainbow(texto)` |
| `red(texto)` |
| `reverse(texto)` |
| `rgb(texto, r, g, b)` |
| `rule(titulo='', cor='gray', largura=0)` |
| `spinner_frames(estilo='pontos')` |
| `strike(texto)` |
| `strip(texto)` |
| `success(texto)` |
| `supports()` |
| `table(linhas, cabecalho=True, cor='cyan')` |
| `tree(no, prefixo='', ultimo=True)` |
| `underline(texto)` |
| `warning(texto)` |
| `white(texto)` |
| `width(padrao=80)` |
| `yellow(texto)` |


---

## Arcane.Concurrent

Threads, processos, canal bloqueante, grupo de tarefas e prazo.

```dataforge
adopt Arcane.Concurrent as Concurrent
```

**Funções (33)**

| Assinatura |
|------------|
| `anel(capacidade=16)` |
| `atomico(inicial=None)` |
| `barreira(quantas)` |
| `canal(capacidade=0)` |
| `com_prazo(acao, segundos)` |
| `com_trava(trava, acao)` |
| `condicao()` |
| `contador(inicial=0)` |
| `dormir(segundos)` |
| `esperar(tarefa, prazo=None)` |
| `esperar_primeira(tarefas, prazo=None)` |
| `esperar_todas(tarefas, prazo=None)` |
| `evento()` |
| `executor(trabalhadores=4)` |
| `fila_sem_trava(itens=None)` |
| `grupo(trabalhadores=None, nome='')` |
| `lotes(acao, itens, tamanho=10, trabalhadores=None)` |
| `map(acao, itens, trabalhadores=None, prazo=None)` |
| `map_processos(acao, itens, trabalhadores=None)` |
| `mutex()` |
| `nucleos()` |
| `para_cada(acao, itens, trabalhadores=None)` |
| `pilha_sem_trava(itens=None)` |
| `pool_processos(trabalhadores=None)` |
| `processo(acao, *args)` |
| `promessa()` |
| `repetir_a_cada(acao, segundos, vezes=0)` |
| `rodar(acao, *args)` |
| `semaforo(quantos=1)` |
| `sou_principal()` |
| `thread_atual()` |
| `threads_vivas()` |
| `trava_leitura_escrita()` |


---

## Arcane.Archive

Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb. Comprime e descomprime VALORES em memória, em deflate cru ou em gzip, com a taxa medida.

```dataforge
adopt Arcane.Archive as Archive
```

**Funções (13)**

| Assinatura |
|------------|
| `acrescentar(arquivo, caminho, nome='')` |
| `compactar(origem, destino, nivel=6)` |
| `compactar_tar(origem, destino, compressao='gz')` |
| `comprimir(dados, nivel=6)` |
| `conferir(arquivo)` |
| `de_gzip(dados, como_texto=False)` |
| `descomprimir(dados, como_texto=False)` |
| `extrair(arquivo, destino='.', senha='')` |
| `extrair_tar(arquivo, destino='.')` |
| `gzip(dados, nivel=6)` |
| `ler_de(arquivo, nome, senha='')` |
| `listar(arquivo)` |
| `taxa(original, comprimido)` |


---

## Arcane.Pipeline

Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório.

```dataforge
adopt Arcane.Pipeline as Pipeline
```

**Funções (11)**

| Assinatura |
|------------|
| `esquecer_marca(fluxo, chave='')` |
| `etapa(fluxo, nome, acao, depende_de=None, tentativas=1, espera=0, quando=None, opcional=False, descricao='')` |
| `fluxo(nome, estado='')` |
| `grafico(fluxo)` |
| `historico(fluxo, quantos=10)` |
| `marca(fluxo, chave, padrao=None)` |
| `marcar(fluxo, chave, valor)` |
| `ordem(fluxo)` |
| `rodar(fluxo, contexto=None, ate=None)` |
| `rodar_ate(fluxo, etapa, contexto=None)` |
| `ultima_execucao(fluxo)` |


---

## Arcane.Stream

Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo.

```dataforge
adopt Arcane.Stream as Stream
```

**Funções (17)**

| Assinatura |
|------------|
| `atraso(corrente, topico, grupo)` |
| `confirmar(corrente, topico, grupo, evento)` |
| `confirmar_ate(corrente, topico, grupo, eventos)` |
| `consumir(corrente, topico, grupo, quantos=0, particao=None)` |
| `corrente(raiz)` |
| `grupos(corrente, topico)` |
| `informacao(corrente, topico)` |
| `janela(eventos, segundos=60, campo='quando')` |
| `ler_de(corrente, topico, desde=0, quantos=0, particao=None)` |
| `offset(corrente, topico, grupo)` |
| `publicar(corrente, topico, valor, chave=None)` |
| `publicar_lote(corrente, topico, eventos)` |
| `remover_topico(corrente, nome)` |
| `reter(corrente, topico, segmentos=10)` |
| `topico(corrente, nome, particoes=1)` |
| `topicos(corrente)` |
| `voltar(corrente, topico, grupo, para=0)` |


---

## Arcane.Observar

Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados.

```dataforge
adopt Arcane.Observar as Observar
```

**Funções (19)**

| Assinatura |
|------------|
| `abrir(painel, nome, dentro_de=None)` |
| `alertar(painel, regras)` |
| `arvore(painel)` |
| `contar(painel, nome, quanto=1)` |
| `cronometrar(painel, nome, acao)` |
| `derivar(painel, saida, entradas, como='')` |
| `fechar(painel, ident, estado='ok', detalhe=None)` |
| `grafo(painel)` |
| `impacto(painel, nome)` |
| `marcar(painel, nome, valor)` |
| `medir(painel, nome, valor)` |
| `origem(painel, nome, profundidade=20)` |
| `painel(nome, versao='', arquivo='')` |
| `prometheus(painel)` |
| `relatorio(painel)` |
| `resumo(painel)` |
| `salvar(painel, caminho='')` |
| `trechos(painel)` |
| `valor(painel, nome)` |


---

## Arcane.Quadro

A tabela de dados: colunas nomeadas e linhas como vault. Filtrar, agrupar, resumir, juntar, pivotar, limpar a ausência e a duplicata, converter tipos, normalizar, codificar e descrever — colunar por dentro, imutável por fora.

```dataforge
adopt Arcane.Quadro as Quadro
```

**Funções (10)**

| Assinatura |
|------------|
| `Grupo(quadro, chaves)` |
| `Quadro(colunas=None, dados=None)` |
| `agregacoes()` |
| `ausente(valor)` |
| `de_colunas(vault)` |
| `de_csv(caminho, separador=',', tipos=True)` |
| `de_json(caminho)` |
| `de_vaults(linhas)` |
| `tipos()` |
| `vazio(colunas=None)` |


---

## Arcane.Lago

Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação.

```dataforge
adopt Arcane.Lago as Lago
```

**Funções (18)**

| Assinatura |
|------------|
| `acrescentar(lago, tabela, linhas, particoes=None, compressao='gzip')` |
| `arquivos(lago, tabela, filtro=None)` |
| `camada(lago, nome)` |
| `compactar(lago, tabela, minimo=2)` |
| `esquema(lago, tabela)` |
| `esquema_parquet(caminho)` |
| `eventos(lago, quantos=20)` |
| `gravar(lago, tabela, linhas, particoes=None, compressao='gzip')` |
| `gravar_parquet(caminho, linhas, compressao='gzip')` |
| `lago(raiz)` |
| `ler(lago, tabela, filtro=None, colunas=None, limite=0)` |
| `ler_parquet(caminho, colunas=None)` |
| `particoes(lago, tabela)` |
| `promover(lago, tabela, de, para, transformar=None, particoes=None)` |
| `remover_particao(lago, tabela, filtro)` |
| `tabelas(lago)` |
| `tamanho(lago, tabela='')` |
| `vacuo(lago)` |


---

## Arcane.Telegram

Bots de Telegram, do primeiro '/start' ao webhook em producao: cliente da Bot API com o limite de taxa lido de onde ele chega, tratadores por comando, texto, botao, midia e consulta inline, conversa como maquina de estados por chat, teclados, o escape de MarkdownV2 que salva a mensagem inteira, e uma sonda que testa o bot sem token e sem rede.

```dataforge
adopt Arcane.Telegram as Telegram
```

**Constantes**

| Nome | Valor |
|------|-------|
| `ESPERA_LONGA` | `50` |
| `RAIZ` | `'https://api.telegram.org'` |
| `acoes` | `['typing', 'upload_photo', 'record_video', 'upload…` |

**Funções (31)**

| Assinatura |
|------------|
| `Aplicacao(token, estado=None, limitador=None, raiz=None)` |
| `Bot(token, raiz=None, prazo=25.0)` |
| `BotFalso(respostas=None)` |
| `Contexto(app, update)` |
| `Limitador(por_segundo=25.0, por_chat_por_minuto=18)` |
| `Sonda(aplicacao, chat=1001, usuario=None)` |
| `app(token, estado=None, limitador=None, raiz=None)` |
| `bloco(texto, linguagem='')` |
| `bot(token, raiz=None, prazo=25.0)` |
| `botao(texto, dados=None, url=None, inline_atual=None, pedir_contato=False, pedir_local=False, jogo=False, pagar=False, app_web=None)` |
| `botoes(linhas)` |
| `chamar(token, metodo, params=None, arquivos=None, prazo=25.0, raiz=None, tentativas=None)` |
| `codigo(texto)` |
| `escapar(texto)` |
| `escapar_html(texto)` |
| `estado_em_arquivo(pasta='.telegram/estado')` |
| `estado_em_memoria()` |
| `forcar_resposta(dica='', seletivo=False)` |
| `italico(texto)` |
| `limitar(por_segundo=25.0, por_chat_por_minuto=18)` |
| `link(texto, destino)` |
| `mencao(texto, id_usuario)` |
| `modo_servidor()` |
| `negrito(texto)` |
| `remover_teclado(seletivo=False)` |
| `riscado(texto)` |
| `segredo_do_ambiente(nome='TELEGRAM_TOKEN')` |
| `spoiler(texto)` |
| `sublinhado(texto)` |
| `teclado(linhas, uma_vez=True, ajustar=True, dica='', persistente=False)` |
| `testar(aplicacao, chat=1001, usuario=None)` |


---

## Arcane.Reativo

Valores que avisam quando mudam: sinal (um valor com estado), derivado (calculado de outros, preguicoso e memorizado, com as dependencias DESCOBERTAS na execucao), efeito (o que acontece quando muda, com limpeza entre ciclos) e observavel (um fluxo no tempo, com morph, sift, distill, distintos, esperar, limitar, combinar e juntar). A diferenca entre valor e fluxo e mantida de proposito: um clique e fluxo, um saldo e valor.

```dataforge
adopt Arcane.Reativo as Reativo
```

**Funções (14)**

| Assinatura |
|------------|
| `Derivado(formula, nome='derivado')` |
| `Efeito(acao, nome='efeito', agora=True)` |
| `Inscricao(cancelar)` |
| `Observavel(nome='observavel')` |
| `Sinal(inicial=None, nome='sinal', iguais=None)` |
| `combinar(*fontes)` |
| `de_cluster(itens, nome='de_cluster')` |
| `derivado(formula, nome='derivado')` |
| `efeito(acao, nome='efeito', agora=True)` |
| `intervalo(segundos, quantos=0, nome='intervalo')` |
| `juntar(*fontes)` |
| `lote(acao)` |
| `observavel(nome='observavel')` |
| `sinal(inicial=None, nome='sinal', iguais=None)` |


---

## Arcane.Dominio

As pecas de um modelo de dominio que se sustenta (DDD): valor (igualdade por conteudo, imutavel, com regra cobrada na criacao), entidade (igualdade por identidade), agregado (a unica porta de escrita, com invariantes conferidas na SAIDA de cada comando e desfazer quando o comando falha no meio), evento (um fato no passado, imutavel), regra (condicao de negocio que se combina com e/ou/nao e explica o "nao"), repositorio (guarda agregados INTEIROS), unidade de trabalho (confirma tudo ou nada, e so entao publica) e contexto delimitado (com a traducao que atravessa a fronteira).

```dataforge
adopt Arcane.Dominio as Dominio
```

**Funções (18)**

| Assinatura |
|------------|
| `Agregado(tipo, identidade=None, **estado)` |
| `Contexto(nome)` |
| `Entidade(tipo, identidade=None, **estado)` |
| `Evento(nome, dados=None, origem='', tipo='')` |
| `Regra(descricao, condicao)` |
| `Repositorio(tipo, ler=None, gravar=None, apagar=None, listar=None)` |
| `Unidade(publicar=None)` |
| `Valor(nome, campos, valores, regra=None, motivo='')` |
| `agregado(tipo, identidade=None, **estado)` |
| `contexto(nome)` |
| `entidade(tipo, identidade=None, **estado)` |
| `evento(nome, dados=None, origem='', tipo='')` |
| `novo_id()` |
| `regra(descricao, condicao)` |
| `repositorio(tipo)` |
| `repositorio_de(tipo, ler, gravar, apagar=None, listar=None)` |
| `unidade(publicar=None)` |
| `valor(nome, campos, regra=None, motivo='')` |


---

## Arcane.Estrutura

Layout binario com NOME, e o ponteiro que o percorre: uma estrutura de campos nomeados com a ordem dos bytes cobrada e o alinhamento declarado (e conferido), uma janela que le e escreve no bloco original sem copiar, um bloco que sabe dizer quando foi liberado, e um ponteiro com aritmetica por ELEMENTO, cast, distancia e dono fraco. Fica entre o Arcane.Bytes, que empacota por formato posicional, e o Arcane.C, que exige FFI.

```dataforge
adopt Arcane.Estrutura as Estrutura
```

**Funções (15)**

| Assinatura |
|------------|
| `Bloco(tamanho_ou_dados=0)` |
| `Janela(bloco_alvo, molde, deslocamento=0)` |
| `Molde(nome, campos, ordem='rede', empacotado=False)` |
| `Ponteiro(bloco_alvo, tipo='u8', deslocamento=0, ordem='rede')` |
| `alinhamento_de(tipo_ou_molde)` |
| `bloco(tamanho_ou_dados=0)` |
| `de_bytes(dados)` |
| `definir(nome, campos, ordem='rede', empacotado=False)` |
| `janela(alvo, molde, deslocamento=0)` |
| `janelas(alvo, molde, quantos=None, deslocamento=0)` |
| `nulo()` |
| `ponteiro(alvo, tipo='u8', deslocamento=0, ordem='rede')` |
| `tamanho_de(tipo_ou_molde)` |
| `tipos()` |
| `uniao(nome, campos, ordem='rede')` |


---

## Arcane.Malha

Chamada entre serviços que não mente: cliente HTTP com prazo, retry com recuo e tremor, disjuntor de três estados, descoberta por nome e propagação automática do rastro do pedido.

```dataforge
adopt Arcane.Malha as Malha
```

**Constantes**

| Nome | Valor |
|------|-------|
| `RETENTAVEIS` | `[408, 425, 429, 500, 502, 503, 504]` |

**Funções (22)**

| Assinatura |
|------------|
| `Cliente(base, opcoes=None)` |
| `Disjuntor(falhas=5, espera=30.0, nome='')` |
| `Passo(nome, fazer, desfazer=None, escreve=True, chave=None)` |
| `Saga(nome='saga', identificador=None, registro=None)` |
| `cabecalhos_de_contexto()` |
| `cliente(base, opcoes=None)` |
| `comecar_contexto(rastro=None, origem='', extra=None)` |
| `contexto()` |
| `de(nome, opcoes=None)` |
| `disjuntor(falhas=5, espera=30.0, nome='')` |
| `onde(nome)` |
| `padrao(opcoes)` |
| `propagar(req, origem='')` |
| `rastro()` |
| `recuo(tentativa, base=0.2, teto=10.0, tremor=True)` |
| `registrar(nome, base, opcoes=None)` |
| `resumo()` |
| `saga(nome='saga', identificador=None, registro=None)` |
| `saude()` |
| `servicos()` |
| `terminar_contexto()` |
| `vale_repetir(resposta)` |


---

## Arcane.Url

Endereços: ler um URL em partes, montar a partir delas, resolver caminho relativo como um navegador, trocar parâmetros preservando os outros, query string em vault (ou em cluster, quando a chave repete) e escape para caminho e para valor.

```dataforge
adopt Arcane.Url as Url
```

**Funções (14)**

| Assinatura |
|------------|
| `campos()` |
| `com_query(endereco, novos)` |
| `desescapar(texto)` |
| `e_absoluto(endereco)` |
| `escapar(texto)` |
| `escapar_tudo(texto)` |
| `host_de(endereco)` |
| `juntar(base, relativo)` |
| `ler(endereco)` |
| `montar(partes)` |
| `query(texto)` |
| `query_lista(texto)` |
| `query_texto(dados)` |
| `sem_query(endereco)` |


---

## Arcane.Bytes

Dados binários: empacotar e desempacotar campos com a ordem dos bytes declarada, um cursor que anda pelo bloco sem acertar índice à mão, janela que olha sem copiar, hexadecimal, base64, bits, despejo estilo hexdump e comparação em tempo fixo.

```dataforge
adopt Arcane.Bytes as Bytes
```

**Funções (25)**

| Assinatura |
|------------|
| `achar(dados, agulha, desde=0)` |
| `base64(dados)` |
| `bits(dados)` |
| `concatenar(*pedacos)` |
| `copiar(vista)` |
| `de_base64(texto)` |
| `de_bits(texto)` |
| `de_hex(texto)` |
| `de_texto(texto, codificacao='utf-8')` |
| `desempacotar(formato, dados)` |
| `despejo(dados, por_linha=16)` |
| `dividir(dados, separador)` |
| `empacotar(formato, *valores)` |
| `escrever(ordem='>')` |
| `fatiar(dados, inicio=0, fim=None)` |
| `hex(dados, separador='')` |
| `igual_em_tempo_fixo(a, b)` |
| `inverter(dados)` |
| `janela(dados, inicio=0, fim=None)` |
| `ler(dados, ordem='>')` |
| `ou_exclusivo(a, b)` |
| `para_texto(dados, codificacao='utf-8', estrito=False)` |
| `preencher(dados, tamanho_final, com=b'\x00', a_esquerda=False)` |
| `tamanho(formato)` |
| `tipos()` |


---

## Arcane.Rede

TCP, UDP, DNS e TLS: conexão com prazo, leitura que insiste até completar, servidor de uma thread por conexão, datagrama, resolução de nome, porta livre, espera de porta abrir e a validade do certificado de um host.

```dataforge
adopt Arcane.Rede as Rede
```

**Constantes**

| Nome | Valor |
|------|-------|
| `prazo_padrao` | `30.0` |

**Funções (15)**

| Assinatura |
|------------|
| `Conexao(bruto, endereco=None)` |
| `Servidor(atender, host='127.0.0.1', porta=0, fila=128, tls=None)` |
| `certificado_de(host, porta=443, prazo=30.0)` |
| `conectar(host, porta, prazo=30.0, tls=False, conferir=True)` |
| `dias_ate_vencer(host, porta=443)` |
| `esperar_porta(host, porta, prazo=30.0, intervalo=0.2)` |
| `meu_ip()` |
| `meu_nome()` |
| `nome_de(ip)` |
| `porta_aberta(host, porta, prazo=2.0)` |
| `porta_livre()` |
| `resolver(nome)` |
| `servir(atender, host='127.0.0.1', porta=0, tls=None)` |
| `servir_em_segundo_plano(atender, host='127.0.0.1', porta=0, tls=None)` |
| `udp(host='0.0.0.0', porta=0, escutar=False)` |


---

## Arcane.Bench

Medir, comparar e descobrir a classe de custo: tempo de uma ação, implementações lado a lado sem a ordem decidir quem ganha, e a curva medida em tamanhos crescentes dizendo qual O() descreve o que aconteceu.

```dataforge
adopt Arcane.Bench as Bench
```

**Funções (7)**

| Assinatura |
|------------|
| `classe(acao, tamanhos=None, preparar=None, repeticoes=3)` |
| `comparar(implementacoes, argumento=None, repeticoes=5, aquecer=1)` |
| `curva(acao, tamanhos, preparar=None, repeticoes=3, aquecer=1)` |
| `medir(acao, argumento=None, repeticoes=5, aquecer=1)` |
| `relatorio(resultado)` |
| `repetir(acao, vezes, argumento=None)` |
| `tabela(resultado)` |


---

## Arcane.Reflexo

Reflexão sobre blueprints, contratos e objetos: campos, métodos, modificadores, MRO, herdeiros, anotações, invocação por nome respeitando a visibilidade, criação de tipos em execução e diagrama de classes em Mermaid.

```dataforge
adopt Arcane.Reflexo as Reflexo
```

**Funções (38)**

| Assinatura |
|------------|
| `anotacoes(alvo, membro=None)` |
| `blueprints()` |
| `campos(alvo)` |
| `contratos(alvo)` |
| `criar_blueprint(nome, definicao=None)` |
| `cumpre(obj, contrato)` |
| `definir_metodo(molde, nome, acao)` |
| `descende(a, b)` |
| `descendentes(alvo)` |
| `diagrama(moldes, opcoes=None)` |
| `documentacao(alvo)` |
| `e_instancia(valor, molde)` |
| `escrever(obj, nome, valor)` |
| `especie(alvo)` |
| `estaticos(alvo)` |
| `faltando(obj, contrato)` |
| `herdeiros(alvo)` |
| `hierarquia(alvo)` |
| `inspecionar(obj)` |
| `instanciar(molde, args=None, nomeados=None)` |
| `invocar(obj, nome, args=None, nomeados=None)` |
| `ler(obj, nome)` |
| `maes(alvo)` |
| `membros(alvo)` |
| `meta(alvo)` |
| `meta_instancia(alvo)` |
| `metodos(alvo)` |
| `modificadores(alvo, membro)` |
| `molde(alvo)` |
| `mro(alvo)` |
| `nome(alvo)` |
| `operadores(alvo)` |
| `procurar(nome)` |
| `propriedades(alvo)` |
| `sugerir(alvo, nome)` |
| `tem(obj, nome)` |
| `tipo(valor)` |
| `traits(alvo)` |


---

## Arcane.Objetos

Cópia rasa e funda, congelamento, igualdade estrutural, hash coerente, ordenação por campos e serialização polimórfica que só reconstrói os tipos autorizados e resolve ciclos.

```dataforge
adopt Arcane.Objetos as Objetos
```

**Funções (13)**

| Assinatura |
|------------|
| `clonar(obj)` |
| `clonar_fundo(obj)` |
| `comparar_por(campos)` |
| `congelado(obj)` |
| `congelar(obj, fundo=False)` |
| `de_json(texto, tipos)` |
| `de_vault(dado, tipos, opcoes=None)` |
| `hash(obj)` |
| `identico(a, b)` |
| `igual(a, b)` |
| `ordenar(itens, campos)` |
| `para_json(obj, opcoes=None, indent=None)` |
| `para_vault(obj, opcoes=None)` |


---

## Arcane.Injecao

Contêiner de injeção de dependência: único, transitório e por escopo, fábrica, valor pronto, dependência preguiçosa e opcional, injeção por construtor, campo e método, e detecção de ciclo com a cadeia inteira.

```dataforge
adopt Arcane.Injecao as Injecao
```

**Constantes**

| Nome | Valor |
|------|-------|
| `ESCOPOS` | `['unico', 'transitorio', 'por_escopo']` |

**Funções (4)**

| Assinatura |
|------------|
| `Fornece(contrato)` |
| `Injetar(alvo=None)` |
| `Servico(escopo='transitorio')` |
| `conteiner(nome='raiz')` |


---

## Arcane.Padroes

Os padrões de projeto que pedem mecanismo: único, pool, construtor, protótipo, flyweight, proxy, adaptador, composto, comandos com desfazer, cadeia, especificação, máquina de estados, memento, visitante, observável, mediador, repositório e barramento.

```dataforge
adopt Arcane.Padroes as Padroes
```

**Funções (20)**

| Assinatura |
|------------|
| `adaptar(alvo, mapa)` |
| `barramento()` |
| `cadeia(manipuladores)` |
| `comandos(limite=100)` |
| `compartilhado(fabrica)` |
| `composto(valor=None)` |
| `construtor(molde, obrigatorios=None)` |
| `especificacao(predicado, nome='especificacao')` |
| `estrategias(padrao=None)` |
| `maquina(inicial, transicoes)` |
| `mediador()` |
| `memento(obj)` |
| `observavel()` |
| `pool(fabrica, tamanho=4, limpar=None)` |
| `prototipos()` |
| `proxy(alvo, interceptar)` |
| `repositorio(campo_id='id')` |
| `restaurar(obj, memento)` |
| `unico(fabrica)` |
| `visitar(obj, visitante)` |


---

## Arcane.Memoria

O ciclo de vida visto de dentro: referência fraca, mapa fraco, ação ao descartar, instâncias vivas por blueprint, tamanho e layout. E o COLETOR sob controle: ligar, desligar, 'sem_gc' num trecho sensível a latência (que religa mesmo se o corpo falhar), limiares por geração, 'congelar' o que já vive para tirá-lo das varreduras, e a conta por geração. Mais a arena: um lote preparado de uma vez e reaproveitado, com 'limpar' soltando tudo numa chamada.

```dataforge
adopt Arcane.Memoria as Memoria
```

**Funções (24)**

| Assinatura |
|------------|
| `ao_descartar(obj, acao)` |
| `arena(quantos, fabrica)` |
| `arena_estatisticas(a)` |
| `coletar(geracao=2)` |
| `comparar_layout(um, outro, amostras=20)` |
| `devolver(a, i)` |
| `estatisticas()` |
| `fraca(obj)` |
| `gc_congelados()` |
| `gc_congelar()` |
| `gc_descongelar()` |
| `gc_desligar()` |
| `gc_geracoes()` |
| `gc_ligado()` |
| `gc_ligar()` |
| `gc_limiares(*valores)` |
| `layout(alvo, amostras=20)` |
| `limpar(a)` |
| `mapa_fraco()` |
| `pegar(a)` |
| `referencias(obj)` |
| `sem_gc(acao)` |
| `tamanho(obj)` |
| `vivos(molde)` |


---

## Arcane.C

Falar com biblioteca nativa: abrir .so/.dylib/.dll, chamar funcao com assinatura declarada, struct e uniao com o layout de verdade (tamanho, alinhamento e deslocamento), ponteiro cru com aritmetica, memoria alocada a mao e callback — uma acao da linguagem chamada de dentro do C. Sobre ctypes, da biblioteca padrao: zero dependencia.

```dataforge
adopt Arcane.C as C
```

**Funções (23)**

| Assinatura |
|------------|
| `Biblioteca(lib, nome, caminho)` |
| `Bloco(quantos)` |
| `Ponteiro(endereco=0, tipo='u8')` |
| `RetornoDeChamada(acao, argumentos, retorno)` |
| `alinhamento_de(tipo)` |
| `alocar(bytes_quantos)` |
| `carregar(alvo, procurar=True)` |
| `copiar(destino, origem, quantos)` |
| `de_bytes(dados)` |
| `do_processo()` |
| `endianness()` |
| `enumeracao(pares)` |
| `estrutura(campos)` |
| `liberar(bloco)` |
| `matematica()` |
| `nulo(tipo='u8')` |
| `padrao()` |
| `para_bytes(alvo, quantos)` |
| `ponteiro(alvo, tipo='u8')` |
| `retorno_de_chamada(acao, argumentos=None, retorno='void')` |
| `tamanho_de(tipo)` |
| `tipos()` |
| `uniao(campos)` |


---

## Arcane.Macro

A arvore como dado: ler o corpo de uma acao, percorrer, transformar e gerar codigo. 'citar' transforma texto em arvore, 'reescrever' devolve uma acao com o corpo trocado, 'nome_fresco' e 'renomear' dao higiene, e 'derivar' e a macro de atributo que gera __str__, __eq__, __lt__ e para_vault a partir dos campos.

```dataforge
adopt Arcane.Macro as Macro
```

**Funções (13)**

| Assinatura |
|------------|
| `acao(nome, parametros, corpo, fechamento=None)` |
| `arvore(alvo)` |
| `citar(texto)` |
| `compilar(texto_fonte, nome='gerada', parametros=None)` |
| `derivar(*quais)` |
| `derivaveis()` |
| `nome_fresco(base='temp')` |
| `percorrer(dado, visitante)` |
| `reescrever(alvo, transformador)` |
| `renomear(dado, de, para)` |
| `substituir(dado, de, para)` |
| `texto(dado)` |
| `transformar(dado, acao)` |


---

## Arcane.Compilador

O caminho de compilacao como dado: os tokens, a arvore, o HIR (a arvore depois do acucar, com a lista do que e acucar e do que so parece), o MIR (bloco basico, aresta, laco e tratador) e as analises que so o grafo responde — alcance, vivacidade, constante em todo caminho, escapatoria e o nome que so um ramo define. O LIR diz o que o compilador de fechamentos compilou e o que recuou para a arvore.

```dataforge
adopt Arcane.Compilador as Compilador
```

**Funções (24)**

| Assinatura |
|------------|
| `acucares(fonte)` |
| `acucares_conhecidos()` |
| `alcance(fonte)` |
| `arvore(fonte)` |
| `blocos(fonte, nome=None)` |
| `constantes(fonte, nome=None)` |
| `corpos(fonte)` |
| `escapam(fonte, nome=None)` |
| `fases()` |
| `hir(fonte)` |
| `lir(fonte)` |
| `mir(fonte)` |
| `nao_e_acucar()` |
| `onde_talvez_nao_definidas(fonte)` |
| `otimizar(fonte, quais=None)` |
| `passes()` |
| `provadas(fonte, nome=None)` |
| `ramos_mortos(fonte)` |
| `resolucao(fonte)` |
| `ssa(fonte, nome=None)` |
| `talvez_nao_definidas(fonte, nome=None)` |
| `texto(fonte, fase='mir')` |
| `tokens(fonte)` |
| `vivas(fonte, nome=None)` |


---

## Arcane.Laco

O laco de eventos, o escalonador e as fibras: UMA thread dormindo no seletor do sistema (epoll, kqueue ou select) em vez de uma thread por conexao. Fila de prazos com 'apos' e 'a_cada', fila de prontas com teto opcional (contrapressao), executor para o trabalho que bloqueia, cancelamento, e fibras de verdade — um 'stream action' suspenso em cada 'emit'.

```dataforge
adopt Arcane.Laco as Laco
```

**Funções (25)**

| Assinatura |
|------------|
| `a_cada(laco, ms, acao, rotulo='')` |
| `agendar(laco, acao, rotulo='')` |
| `apos(laco, ms, acao, rotulo='')` |
| `cancelada(alvo)` |
| `cancelar(alvo)` |
| `ceder()` |
| `depois_de(ms, caixa, chave, valor='pronto')` |
| `dormir(ms)` |
| `escrever(soquete)` |
| `esperar(outra)` |
| `esquecer(laco, soquete)` |
| `estatisticas(laco)` |
| `executar(laco, trabalho, depois=None)` |
| `falhas(laco)` |
| `fechar(laco)` |
| `fibra(laco, acao, argumentos=None, nome='')` |
| `fibras(laco)` |
| `ler(soquete, caixa, chave, quanto=65536)` |
| `mecanismo(laco)` |
| `novo(teto=None)` |
| `parar(laco)` |
| `pedidos()` |
| `quando_escrever(laco, soquete, acao)` |
| `quando_ler(laco, soquete, acao)` |
| `rodar(laco, voltas=None)` |


---

## Arcane.Perfil

Medir com rigor, onde o 'Bench' da a media: percentis (p50, p95, p99, p999) com aquecimento separado, comparacao com SIGNIFICANCIA estatistica (Mann-Whitney, que nao supoe normalidade — tempo de execucao nao e normal), linha de base guardada para acusar regressao no CI, flame graph das ACOES da linguagem em SVG sem nada de fora, pausas do coletor medidas na fonte e contencao de trava.

```dataforge
adopt Arcane.Perfil as Perfil
```

**Funções (16)**

| Assinatura |
|------------|
| `chama_svg(perfil, largura=1200, altura_linha=18)` |
| `chama_texto(perfil)` |
| `com_trava(alvo, acao)` |
| `comecar_perfil(interp)` |
| `comparar(a, b, opcoes=None)` |
| `conferir(nome, medida, opcoes=None)` |
| `estatisticas_da_trava(alvo)` |
| `gc_pausas(acao)` |
| `guardar(nome, medida, arquivo='perfil-base.json')` |
| `mann_whitney(a, b)` |
| `medir(acao, opcoes=None)` |
| `perfilar(acao, interp=None)` |
| `relatorio(medida)` |
| `resumir(valores, casas=4)` |
| `terminar_perfil(coleta)` |
| `trava()` |


---

## Arcane.Inicio

O que roda ANTES da primeira linha: as fases da partida nomeadas e em ordem, e quanto cada 'adopt' custou — que e a unica forma de responder 'por que o programa demora a comecar?' sem cronometrar a mao. Mais armazenamento por THREAD com inicializacao e finalizador (o 'threading.local' da o armazem e nao da o resto), e a pilha que se pergunta: profundidade, teto, quanto falta e os quadros abertos.

```dataforge
adopt Arcane.Inicio as Inicio
```

**Funções (12)**

| Assinatura |
|------------|
| `adocoes()` |
| `definir(a, v)` |
| `fases()` |
| `limite_da_pilha(novo=None)` |
| `limpar(a)` |
| `local(inicial, ao_terminar=None, nome='')` |
| `meu(a)` |
| `pilha()` |
| `quadros()` |
| `relatorio()` |
| `texto_do_relatorio()` |
| `threads_com_valor(a)` |


---

## Arcane.Capacidade

A fronteira de CAPACIDADE: roda uma acao com a lista de poderes que ela pode alcancar, e recusa o resto pelo NOME da capacidade que falta. A ponte para o Python e capacidade propria, e nunca vem junto. NAO e caixa contra programa hostil, e o modulo diz isso em 'limites()': ele bloqueia a autoridade ambiente (o 'adopt'), e nao tira o que foi ENTREGUE — o que e o modelo de capacidade, nao um defeito.

```dataforge
adopt Arcane.Capacidade as Capacidade
```

**Funções (6)**

| Assinatura |
|------------|
| `capacidades()` |
| `executar(acao, permissoes=None, argumentos=None)` |
| `exige(nome_modulo)` |
| `limites()` |
| `modulos_de(capacidade)` |
| `observar(acao, permissoes=None, argumentos=None)` |


---

## Arcane.Abi

A superficie de um modulo e o CONTRATO dele, e quebra-la e o mesmo problema que quebrar uma ABI — com outro nome e o mesmo sintoma: nao e erro de quem publicou, e erro de quem consome, depois. Compara duas versoes e diz o que quebrou (simbolo removido, aridade incompativel, parametro renomeado, tipo trocado, campo novo obrigatorio) e qual bump de semver a mudanca EXIGE. Mais o mapa de simbolos: de onde vem cada nome, o analogo do mapa que um ligador escreve.

```dataforge
adopt Arcane.Abi as Abi
```

**Funções (8)**

| Assinatura |
|------------|
| `comparar(antes, depois)` |
| `compativel(antes, depois)` |
| `mapa(caminho)` |
| `quebras(antes, depois)` |
| `regras()` |
| `relatorio(resultado)` |
| `superficie(caminho)` |
| `veredito(antes, depois)` |


---

## Arcane.Alvo

'Isso roda no navegador?', respondido a partir dos 'adopt'. Seis alvos descritos (servidor, cli, navegador, wasi, funcao serverless, embarcado) com o que cada um suporta e POR QUE nao suporta o resto, no mesmo vocabulario de capacidade do 'Arcane.Capacidade'. A leitura e ESTATICA e o modulo diz isso em 'limites()': um 'roda' quer dizer 'nao achei impedimento por esta via', e nao 'vai funcionar'.

```dataforge
adopt Arcane.Alvo as Alvo
```

**Funções (7)**

| Assinatura |
|------------|
| `alvos()` |
| `conferir(caminho, alvo='servidor')` |
| `conferir_todos(caminho)` |
| `exigencias(caminho)` |
| `limites()` |
| `porque(alvo, capacidade)` |
| `relatorio(resultado)` |


---

## Arcane.Ecossistema

O inventario da implementacao, CONFERIDO contra ela. Cada componente do desenho do ecossistema aponta arquivos de verdade e carrega um de tres estados: 'existe', 'equivale' (ha outra peca que responde a mesma pergunta, nomeada) ou 'nao-existe' (com o porque escrito). 'conferir()' cobra as duas direcoes — todo caminho citado existe no disco, e todo modulo do nucleo aparece em algum componente —, e e isso que impede o mapa de mentir quando uma peca muda de nome. 'o_que_nao_existe()' e a resposta honesta a 'o DataForge tem backend LLVM?'.

```dataforge
adopt Arcane.Ecossistema as Ecossistema
```

**Constantes**

| Nome | Valor |
|------|-------|
| `ESTADOS` | `['existe', 'equivale', 'nao-existe']` |

**Funções (8)**

| Assinatura |
|------------|
| `arvore()` |
| `componentes()` |
| `conferir()` |
| `equivalencias()` |
| `grupos()` |
| `numeros()` |
| `o_que_nao_existe()` |
| `relatorio()` |


---

## Arcane.Principios

Os dez principios de design, cada um com uma prova que RODA e o numero que ela deu — duas delas rodam o analisador e uma roda o interpretador, porque 'verificacao antes de rodar' e 'custo zero quando desligado' sao coisas que se demonstram. O veredito nao e dez de dez de proposito: 5 cumpridos, 4 parciais e 1 que nao se aplica. E as nove TENSOES: onde dois principios se contradizem, qual venceu, o custo aceito e o arquivo onde a decisao mora.

```dataforge
adopt Arcane.Principios as Principios
```

**Constantes**

| Nome | Valor |
|------|-------|
| `VEREDITOS` | `['cumprido', 'parcial', 'nao-se-aplica']` |

**Funções (5)**

| Assinatura |
|------------|
| `conferir(nome=None)` |
| `principios()` |
| `relatorio()` |
| `tensoes()` |
| `veredito()` |


---

## Arcane.Percurso

O caminho inteiro de um arquivo, fase por fase, MEDIDO: lexer, parser, HIR, tipos, MIR, analises, SSA, passes e LIR, com o que cada fase produziu e quanto tempo levou. Responde 'onde o tempo vai' quando um arquivo demora a abrir no editor. Ele NAO executa o programa — executar e o que o programa faz, e um comando que mostra fases nao pode abrir soquete. Traz tambem as divergencias entre o caminho real e o desenho da referencia.

```dataforge
adopt Arcane.Percurso as Percurso
```

**Funções (5)**

| Assinatura |
|------------|
| `desenho()` |
| `divergencias()` |
| `fases()` |
| `percorrer(caminho, com_tipos=True)` |
| `relatorio(resultado)` |


---

## Arcane.Dsl

Combinadores para escrever uma linguagem pequena, propria: texto, numero, nome, aspas, espaco, sequencia, alternativa, repeticao, opcional e separado_por, com 'analisar' devolvendo Resultado e a falha dizendo a posicao e o que era esperado.

```dataforge
adopt Arcane.Dsl as Dsl
```

**Funções (18)**

| Assinatura |
|------------|
| `adiado(pegar)` |
| `analisar(analisador, entrada, tudo=True)` |
| `ate(parada)` |
| `entre_aspas(aspa='"')` |
| `espaco(obrigatorio=False)` |
| `exigir(analisador, mensagem)` |
| `gramatica(regras, inicial)` |
| `mapear(analisador, acao)` |
| `muitos(analisador, minimo=0)` |
| `nome()` |
| `numero()` |
| `opcional(analisador, padrao=None)` |
| `ou(analisadores)` |
| `qualquer_de(caracteres)` |
| `separado_por(item, separador, minimo=0)` |
| `seq(analisadores)` |
| `simbolo(qual)` |
| `texto(esperado)` |


---

## Arcane.Posse

Quem e o dono, quem tomou emprestado, e quando solta: posse exclusiva com liberacao deterministica ('dono' e 'com', o RAII), emprestimo com escopo (muitos leem OU um escreve, cobrado quando roda), contagem de referencia deterministica ('compartilhado' e 'atomico') e referencia fraca que quebra o ciclo.

```dataforge
adopt Arcane.Posse as Posse
```

**Funções (16)**

| Assinatura |
|------------|
| `Celula(valor)` |
| `Compartilhado(valor=None, ao_soltar=None, _nucleo=None, atomico=False)` |
| `Dono(valor, ao_soltar=None, nome='valor')` |
| `Emprestimo(valor, exclusivo=False)` |
| `Escopo()` |
| `Fraco(compartilhado)` |
| `atomico(valor=None, ao_soltar=None)` |
| `celula(valor=None)` |
| `com(alvo, acao)` |
| `com_escopo(acao)` |
| `compartilhado(valor=None, ao_soltar=None)` |
| `dono(valor=None, ao_soltar=None, nome='valor')` |
| `e_dono(valor)` |
| `escopo()` |
| `estado(alvo)` |
| `fraco(alvo)` |


---

## Arcane.Stm

Memoria transacional: escritas que acontecem JUNTAS ou nao acontecem. Variavel transacional, 'atomicamente' com validacao otimista e repeticao no conflito, 'retentar' que espera em vez de girar, 'ou_entao' para compor duas operacoes bloqueantes, e estatisticas de conflito.

```dataforge
adopt Arcane.Stm as Stm
```

**Funções (13)**

| Assinatura |
|------------|
| `Variavel(valor=None, nome='')` |
| `atomicamente(acao, tentativas=1000)` |
| `definir(var, novo)` |
| `em_transacao()` |
| `escrever(var, valor)` |
| `estatisticas()` |
| `ler(var)` |
| `modificar(var, acao)` |
| `ou_entao(primeira, segunda)` |
| `retentar()` |
| `valor(var)` |
| `variavel(valor=None, nome='')` |
| `zerar_estatisticas()` |


---

## Arcane.Resultado

A falha como VALOR, e a ausencia com nome: 'ok'/'falha' para quem devolve o erro em vez de levanta-lo, com 'mapear', 'entao', 'recuperar', 'ou' e 'todos' (a primeira falha vence); e 'Talvez' ('algo'/'nada') para onde 'void' e ambiguo — distinguir 'a chave nao esta la' de 'a chave vale void'.

```dataforge
adopt Arcane.Resultado as Resultado
```

**Funções (13)**

| Assinatura |
|------------|
| `Resultado(ok, valor=None, erro=None, detalhe=None)` |
| `Talvez(tem, valor=None)` |
| `algo(valor=None)` |
| `chave(vault, nome)` |
| `de(valor, motivo='void')` |
| `erros(resultados)` |
| `falha(erro='falhou', detalhe=None)` |
| `nada()` |
| `ok(valor=None)` |
| `primeiro(colecao, condicao=None)` |
| `talvez(valor)` |
| `tentar(acao, *args)` |
| `todos(resultados)` |


---

## Arcane.Tipos

Reflexao sobre tipos: os metadados de um 'type' declarado (especie, base, regra, opaco), 'satisfaz' para conferir sem levantar, a forma ESTRUTURAL de um valor ('Cluster<Integer>', 'Tuple<Integer, String>') e os campos de um record ou instancia com o tipo de cada um.

```dataforge
adopt Arcane.Tipos as Tipos
```

**Funções (10)**

| Assinatura |
|------------|
| `campos(valor)` |
| `conferir(valor, nome)` |
| `de(nome)` |
| `declarados()` |
| `e_colecao(valor)` |
| `e_imutavel(valor)` |
| `existe(nome)` |
| `forma(valor, profundidade=3)` |
| `nome_de(valor)` |
| `satisfaz(valor, nome)` |


---

## Arcane.Eventos

Publicar e assinar sem as duas partes se conhecerem: emissor com curinga, ouvinte de uma vez só, contexto por thread que atravessa as camadas, fila de trabalho em segundo plano, e fila persistente em SQLite que sobrevive ao processo, com recuo exponencial, atraso e hora marcada, prioridade, chave contra repetição e carta morta.

```dataforge
adopt Arcane.Eventos as Eventos
```

**Funções (10)**

| Assinatura |
|------------|
| `Emissor(nome='emissor', teto=1000)` |
| `Fila(trabalhador, operarios=2, nome='fila')` |
| `FilaPersistente(caminho, trabalhador=None, opcoes=None)` |
| `com_contexto(dados, acao)` |
| `contexto()` |
| `emissor(nome='emissor', teto=1000)` |
| `fila(trabalhador, operarios=2, nome='fila')` |
| `fila_persistente(caminho, trabalhador=None, opcoes=None)` |
| `guardar(chave, valor)` |
| `por(chave, padrao=None)` |


---

## Arcane.Cli

A linha de comando de um programa escrito em DataForge: opções tipadas com valor padrão e escolhas, argumentos posicionais, subcomandos, ajuda gerada da declaração, perguntas no terminal e console interativo.

```dataforge
adopt Arcane.Cli as Cli
```

**Funções (12)**

| Assinatura |
|------------|
| `Comando(nome=None, sobre='', versao='')` |
| `Console(prompt='> ', sobre='')` |
| `comando(nome=None, sobre='', versao='')` |
| `confirmar(texto, padrao=False)` |
| `console(prompt='> ', sobre='')` |
| `erro(texto, codigo=1)` |
| `escolher(texto, opcoes, padrao=0)` |
| `largura()` |
| `limpar()` |
| `perguntar(texto, padrao=None, valida=None)` |
| `segredo(texto='senha')` |
| `tem_terminal()` |


---

## Arcane.Email

Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza no cabeçalho, SMTP com TLS por padrão, prévia sem enviar e caixa de teste com o mesmo contrato.

```dataforge
adopt Arcane.Email as Email
```

**Funções (6)**

| Assinatura |
|------------|
| `Caixa()` |
| `Mensagem(de='', para=None, assunto='')` |
| `caixa()` |
| `enviar(mensagem_, servidor, porta=587, usuario='', senha='', seguro=True, prazo=30.0)` |
| `mensagem(de='', para=None, assunto='')` |
| `valido(endereco)` |


---

## Arcane.Html

Ler HTML de verdade: seletor CSS, texto que junta com espaço, links absolutos, tabela como dado, escapar contra XSS, limpar toda a marcação e podar deixando só as tags permitidas.

```dataforge
adopt Arcane.Html as Html
```

**Funções (11)**

| Assinatura |
|------------|
| `No(tag='', atributos=None, pai=None)` |
| `achar(fonte, seletor)` |
| `achar_todos(fonte, seletor)` |
| `desescapar(texto)` |
| `escapar(texto)` |
| `ler(fonte)` |
| `limpar(fonte)` |
| `links_de(fonte, base='')` |
| `podar(fonte, permitidas=None, links_seguros=True)` |
| `tabela_de(fonte, seletor='table')` |
| `texto_de(fonte)` |


---

## Arcane.Lavra

A consulta tipada: o cliente diz exatamente quais campos quer, numa consulta indentada, e recebe exatamente aqueles. O esquema nasce dos 'record' que já existem; traz resolvedores, contexto, trechos, variáveis, diretivas, contratos, uniões, introspecção, validação antes de executar, lote contra o N+1, paginação por cursor, limites de profundidade e custo, assinaturas por WebSocket e federação de vários serviços.

```dataforge
adopt Arcane.Lavra as Lavra
```

**Funções (42)**

| Assinatura |
|------------|
| `assinatura(esq, nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)` |
| `busca(esq, nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)` |
| `campo(esq, tipo_nome, nome, tipo_do_campo, resolve=None, args=None, descricao='', obsoleto='', custo=1)` |
| `cliente(url, cabecalhos=None, tempo_limite=10.0)` |
| `conferir(esq)` |
| `contexto(dados=None)` |
| `contrato(esq, nome, campos, descricao='', resolve_tipo=None)` |
| `descrever(esq)` |
| `diretiva(esq, nome, decidir)` |
| `em_segundo_plano(esquema, porta=0, host='127.0.0.1', caminho='/lavra', contexto_de=None)` |
| `entao(promessa, acao)` |
| `entrada(esq, alvo, nome=None, descricao='', campos=None)` |
| `enum(esq, nome, valores, descricao='')` |
| `erro(mensagem, codigo='erro', extra=None)` |
| `escalar(esq, nome, serializa=None, desserializa=None, descricao='')` |
| `esquema(nome='lavra')` |
| `estender(p, tipo_nome, campo_nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)` |
| `executar(esq, texto, variaveis=None, contexto=None, raiz=None, operacao=None, validar_antes=True)` |
| `fonte(nome='fonte')` |
| `introspeccao(esq, ligada=True)` |
| `juntar(p, servico, esquema)` |
| `ler(texto)` |
| `limites(esq, profundidade=None, complexidade=None, itens=None)` |
| `local(esquema, contexto=None)` |
| `lote(ctx, nome, buscar)` |
| `lotes(ctx)` |
| `mapa(p)` |
| `montar(app, esquema, caminho='/lavra', contexto_de=None, permitir_get=True, introspeccao_publica=True)` |
| `montar_assinaturas(app, esquema, caminho='/lavra/assinar', contexto_de=None)` |
| `mudanca(esq, nome, tipo_do_campo, resolve=None, args=None, descricao='', custo=1)` |
| `pagina(itens, primeiros=None, depois=None, total=None)` |
| `parar(app)` |
| `pedir(ctx, nome, chave)` |
| `portao(nome='portao')` |
| `preencher(ctx, nome, chave, valor)` |
| `recusar(mensagem='sem permissão', extra=None)` |
| `servir(esquema, porta=8080, host='127.0.0.1', caminho='/lavra', contexto_de=None, silencioso=False)` |
| `texto_do_esquema(esq)` |
| `tipo(esq, alvo, nome=None, descricao='', cumpre=None, campos=None, esconder=None)` |
| `tipo_pagina(esq, nome_do_item, nome=None)` |
| `uniao(esq, nome, membros, descricao='', resolve_tipo=None)` |
| `validar(esq, texto, operacao=None)` |


---

## Arcane.Vitrine

O framework de dashboards e aplicações de dados: você escreve um programa de cima para baixo e ele vira uma página web, com componentes, layout, gráficos em SVG, estado por sessão e cache — servido pelo Kiln.

```dataforge
adopt Arcane.Vitrine as Vitrine
```

**Constantes**

| Nome | Valor |
|------|-------|
| `estado` | `<dataforge.stdlib.vitrine.estado.Estado object at …` |
| `geral` | `<dataforge.stdlib.vitrine.estado.Geral object at 0…` |
| `i18n` | `<dataforge.stdlib.vitrine.extras.Traducao object a…` |
| `paleta` | `['#FED403', '#0F62FE', '#24A148', '#FA4D56', '#8A3…` |
| `tipos_de_grafico` | `['linha', 'barras', 'area', 'dispersao', 'pizza', …` |

**Funções (208)**

| Assinatura |
|------------|
| `abas(rotulos)` |
| `agendar(acao, a_cada, *args)` |
| `ajuda(alvo)` |
| `antes(funcao)` |
| `app(titulo='Vitrine', **config)` |
| `area_de_texto(rotulo, valor='', linhas=4, dica='', chave=None)` |
| `arquivo(rotulo, tipos=None, varios=False, chave=None)` |
| `atualizar_a_cada(segundos)` |
| `audio(origem, formato='audio/mpeg')` |
| `autenticacao(verificador, papeis=None)` |
| `autenticado()` |
| `autocompletar(rotulo, opcoes, valor='', dica='', chave=None)` |
| `avaliacao(rotulo, tipo='estrelas', maximo=5, valor=0, chave=None)` |
| `aviso(mensagem)` |
| `baixar(rotulo, conteudo, nome='dados.txt', tipo='text/plain')` |
| `barra_superior(titulo='', itens=None, ativo='', logo='', subtitulo='')` |
| `botao(rotulo, tipo='primario', chave=None, largura='')` |
| `busca(rotulo='Buscar', dica='', chave=None)` |
| `cabecalho(conteudo, nivel=3)` |
| `cache(*args, **kwargs)` |
| `caixa(rotulo, valor=False, chave=None)` |
| `camera(rotulo='Foto', chave=None)` |
| `caminho()` |
| `campo_validado(rotulo, regra, mensagem='', valor='', tipo='texto', dica='', chave=None)` |
| `carregando(mensagem='Carregando…')` |
| `cartao(titulo='', subtitulo='')` |
| `chat(altura=None)` |
| `chat_entrada(dica='Escreva uma mensagem…', chave=None, desabilitado=False)` |
| `chat_mensagem(quem='assistente', conteudo='', avatar='', hora='')` |
| `citacao(conteudo, autor='')` |
| `codigo(conteudo, linguagem='dataforge')` |
| `coluna(nome, titulo='', tipo='texto', formato='', largura=0, alinhar='', casas=None, ajuda='', editavel=False, opcoes=None, minimo=None, maximo=None, prefixo='', sufixo='', cores=None, oculta=False)` |
| `colunas(quantidade, larguras=None, espacamento='medio')` |
| `comemorar(tipo='balao')` |
| `compacto(valor, casas=1)` |
| `componente(nome, acao=None)` |
| `componentes()` |
| `conexao(nome, arquivo='', tipo='sqlite', **opcoes)` |
| `conexao_de(nome, bruta, tipo='externa')` |
| `conexoes()` |
| `configurar(chave=None, valor=None, **pares)` |
| `configurar_pagina(titulo='', icone='', **pares)` |
| `container(borda=False, altura=None)` |
| `cor(rotulo, valor='#FED403', chave=None)` |
| `data(rotulo, valor='', chave=None)` |
| `data_br(valor)` |
| `depois(funcao)` |
| `desenhar(g)` |
| `deslizante(rotulo, minimo=0, maximo=100, valor=None, passo=1, chave=None)` |
| `deslizante_opcoes(rotulo, opcoes, indice=0, chave=None)` |
| `dialogo(titulo, aberto=None, largura=520, chave=None)` |
| `divisor()` |
| `editor(dados, colunas=None, acrescentar=True, remover=True, altura=None, chave=None)` |
| `email(rotulo='E-mail', valor='', dica='', chave=None)` |
| `encerrar_sessao()` |
| `entrada(rotulo, valor='', dica='', tipo='texto', chave=None)` |
| `entrar(usuario, senha)` |
| `erro(mensagem)` |
| `escolha(rotulo, opcoes, indice=0, chave=None)` |
| `escolhas(rotulo, opcoes, padrao=None, chave=None)` |
| `escrever(*valores)` |
| `espacador()` |
| `espaco(altura=16)` |
| `esqueleto(linhas=3, altura=14, largura='100%')` |
| `estatisticas(dados, colunas=None)` |
| `excecao(erro, detalhe='')` |
| `exigir_login(mensagem='Entre para continuar.')` |
| `exigir_permissao(permissao, mensagem='')` |
| `expandir(rotulo, aberto=False)` |
| `exportar_csv(dados, nome='dados.csv', rotulo='Baixar CSV', separador=',')` |
| `exportar_excel(dados, nome='dados.xlsx', rotulo='Baixar Excel', aba='Dados')` |
| `exportar_json(dados, nome='dados.json', rotulo='Baixar JSON')` |
| `exportar_svg(grafico, nome='grafico.svg', rotulo='Baixar SVG')` |
| `faixa(rotulo, minimo=0, maximo=100, valor=None, passo=1, chave=None)` |
| `fechar_conexoes()` |
| `fluxo(gerador, velocidade=18)` |
| `formatar(valor, formato='', casas=None)` |
| `formula(expressao, bloco=True)` |
| `formulario(nome, limpar=False)` |
| `fragmento(chave, a_cada=0)` |
| `fragmentos()` |
| `frame(dados, colunas=None, altura=None)` |
| `galeria(imagens, colunas=3, legendas=None)` |
| `grade(dados, colunas=None, busca=True, paginar=25, selecionar='', ordenar_por='', decrescente=False, destacar=None, totais=None, altura=None, densidade='normal', numerar=False, chave=None, vazio='sem dados')` |
| `grafico(tipo='linha', dados=None)` |
| `grafico_area(dados, x='', y='', titulo='', altura=None, **kw)` |
| `grafico_area_empilhada(dados, x='', y=None, titulo='', altura=None, cores=None, **kw)` |
| `grafico_bala(valor, alvo, minimo=0, maximo=None, rotulo='', faixas=None, titulo='', altura=None, cores=None, formato='', **kw)` |
| `grafico_barras(dados, x='', y='', titulo='', altura=None, **kw)` |
| `grafico_barras_100(dados, x='', y=None, titulo='', altura=None, cores=None, **kw)` |
| `grafico_barras_h(dados, x='', y='', titulo='', altura=None, **kw)` |
| `grafico_bolhas(dados, x='', y='', tamanho='', rotulo='', titulo='', altura=None, cores=None, formato='', **kw)` |
| `grafico_caixa(dados, y=None, titulo='', altura=None, cores=None, formato='', **kw)` |
| `grafico_calendario(dados, data='', valor='', ano=None, titulo='', altura=None, cores=None, escala=None, **kw)` |
| `grafico_cascata(dados, x='', y='', titulo='', altura=None, cores=None, formato='', total=True, **kw)` |
| `grafico_combo(dados, x='', barras=None, linhas=None, titulo='', altura=None, cores=None, formato='', direita=None, empilhado=False, **kw)` |
| `grafico_dispersao(dados, x='', y='', titulo='', altura=None, **kw)` |
| `grafico_dispersao_xy(dados, x='', y='', titulo='', altura=None, cores=None, formato='', tendencia=False, **kw)` |
| `grafico_funil(dados, x='', y='', titulo='', altura=None, cores=None, formato='', **kw)` |
| `grafico_gantt(tarefas, titulo='', altura=None, cores=None, **kw)` |
| `grafico_linha(dados, x='', y='', titulo='', altura=None, **kw)` |
| `grafico_mapa(pontos, titulo='', altura=None, cores=None, formato='', **kw)` |
| `grafico_pareto(dados, x='', y='', titulo='', altura=None, cores=None, formato='', corte=80, **kw)` |
| `grafico_pizza(dados, x='', y='', titulo='', altura=None, **kw)` |
| `grafico_radar(dados, x='', y=None, titulo='', altura=None, cores=None, **kw)` |
| `grafico_rede(ligacoes, titulo='', altura=None, cores=None, **kw)` |
| `grafico_rosca(dados, x='', y='', titulo='', altura=None, **kw)` |
| `grafico_sankey(ligacoes, titulo='', altura=None, cores=None, formato='', **kw)` |
| `grafico_treemap(dados, rotulo='', valor='', titulo='', altura=None, cores=None, formato='', **kw)` |
| `grafico_velas(dados, data='', abertura='abertura', maxima='maxima', minima='minima', fechamento='fechamento', titulo='', altura=None, cores=None, formato='', **kw)` |
| `guardar_no_chat(quem, conteudo, chave='__chat__')` |
| `histograma(dados, campo='', faixas=10, titulo='', altura=None)` |
| `historico_de_chat(chave='__chat__')` |
| `hora(rotulo, valor='09:00', passo=60, chave=None)` |
| `html(conteudo)` |
| `html_da_pagina()` |
| `icone(nome, tamanho=18, cor='')` |
| `icones()` |
| `iframe(origem, altura=420, titulo='Conteúdo incorporado')` |
| `imagem(origem, legenda='', largura=None)` |
| `indicador(rotulo, valor, variacao=None, cor='', ajuda='', nota='', mini=None, alvo=None, formato='', icone='')` |
| `indicadores(itens, colunas=0)` |
| `informacao(mensagem)` |
| `interruptor(rotulo, valor=False, chave=None)` |
| `json(dados, expandido=True)` |
| `lateral()` |
| `legenda(conteudo)` |
| `linha(alinhar='inicio', espacamento='medio')` |
| `link(rotulo, destino, nova_aba=False)` |
| `logo(origem, destino='/', largura=132)` |
| `logs(quantos=100, nivel='')` |
| `malha(colunas=3, espacamento='medio', minimo=240)` |
| `mapa_de_calor(dados, x='', y='', valor='', titulo='', altura=None, cores=None, formato='', escala=None, **kw)` |
| `markdown(conteudo)` |
| `markdown_para_html(texto)` |
| `medidor(valor, minimo=0, maximo=100, titulo='', faixas=None, altura=None, formato='', rotulo='', cores=None, **kw)` |
| `menu(rotulo='Páginas')` |
| `metrica(rotulo, valor, variacao=None, ajuda='')` |
| `metricas()` |
| `mini_grafico(valores, tipo='linha', cor='', altura=34, largura=120, mostrar_valor=False)` |
| `modo_servidor()` |
| `moeda(valor, simbolo='R$', casas=2)` |
| `montar()` |
| `mudancas()` |
| `mudou(chave)` |
| `navegar(destino)` |
| `numero(rotulo, valor=0, minimo=None, maximo=None, passo=1, chave=None)` |
| `numero_br(valor, casas=0)` |
| `opcao(rotulo, opcoes, indice=0, chave=None)` |
| `pagina(caminho, acao=None, titulo='', icone='', oculta=False)` |
| `paginas()` |
| `painel(titulo='', subtitulo='', cor='', icone='', compacto=False, altura=None)` |
| `parametro(nome, padrao='')` |
| `parametros()` |
| `parar()` |
| `parar_servidor()` |
| `passos(rotulos, atual=0, concluidos=None)` |
| `pdf(origem, altura=640, pagina=1)` |
| `pedir(app, metodo, caminho, corpo=None, cabecalhos=None)` |
| `percentual(valor, casas=1, ja_e_percentual=True)` |
| `periodo(rotulo, inicio='', fim='', chave=None)` |
| `pilulas(rotulo, opcoes, padrao=None, varios=False, chave=None)` |
| `plugin(nome, instalar)` |
| `pode(permissao)` |
| `popover(rotulo, icone='', largura=300)` |
| `progresso(fracao, rotulo='')` |
| `recarregar()` |
| `recurso(*args, **kwargs)` |
| `registrar(mensagem, nivel='info', extra=None)` |
| `regra(coluna_alvo, condicao, valor=None, cor='aviso', coluna_pintada='')` |
| `rodar(acao=None, porta=8501, host='127.0.0.1', recarregar=False, silencioso=False)` |
| `rolagem(altura=320, borda=True)` |
| `sair()` |
| `saude()` |
| `segmentado(rotulo, opcoes, indice=0, chave=None)` |
| `segredo(chave, padrao='')` |
| `segredos(recarregar=False)` |
| `segredos_mascarados()` |
| `seletor_de_tema(rotulo='Tema')` |
| `selo(texto, cor='neutro', icone='')` |
| `selos(itens, cor='neutro')` |
| `senha(rotulo='Senha', dica='', chave=None)` |
| `separador(texto='', icone='')` |
| `servir(porta=0, host='127.0.0.1')` |
| `sessoes()` |
| `sessoes_em_arquivos(pasta)` |
| `sessoes_em_banco(caminho)` |
| `status(rotulo, estado='rodando', aberto=True)` |
| `subir(porta=8501, host='127.0.0.1', recarregar=False, silencioso=False)` |
| `subtitulo(conteudo)` |
| `sucesso(mensagem)` |
| `t(chave, **valores)` |
| `tabela(dados, colunas=None, altura=None)` |
| `tags(rotulo, valor=None, sugestoes=None, chave=None)` |
| `tarefa(acao, *args)` |
| `tema(qual=None, densidade=None)` |
| `temas()` |
| `testar(pagina_ou_app, caminho='/')` |
| `texto(*partes)` |
| `titulo(conteudo, icone='')` |
| `toast(mensagem, icone='', nivel='info', segundos=4)` |
| `traduzir(chave, **valores)` |
| `usar(nome, *args, **kwargs)` |
| `usuario()` |
| `validar(valor, regra, mensagem='')` |
| `vault(dados)` |
| `vazio()` |
| `video(origem, formato='video/mp4')` |


---

## Arcane.API

A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas.

```dataforge
adopt Arcane.API as API
```

**Funções (7)**

| Assinatura |
|------------|
| `curl(app, config=None)` |
| `insomnia(app, config=None)` |
| `markdown(app, config=None)` |
| `openapi(app, config=None)` |
| `postman(app, config=None)` |
| `resumo(app)` |
| `rotas(app)` |


---

## Arcane.Decimal

Número decimal exato, para quando 0,1 + 0,2 precisa dar 0,3 — dinheiro, imposto, e todo número que alguém confere na mão.

```dataforge
adopt Arcane.Decimal as Decimal
```

**Funções (16)**

| Assinatura |
|------------|
| `abs(d)` |
| `arredondar(valor, casas=0, modo='MEIO_PARA_CIMA')` |
| `casas(valor)` |
| `centavos(valor)` |
| `de(valor)` |
| `de_centavos(centavos)` |
| `e_decimal(x)` |
| `float(valor)` |
| `inteiro(valor)` |
| `media(valores)` |
| `modos()` |
| `repartir(valor, partes, casas=2)` |
| `sinal(d)` |
| `soma(valores)` |
| `texto(valor, casas=None)` |
| `zero()` |


---

## Arcane.Ponte

A ponte para o Python: perguntar se um pacote existe, explorar o que ele oferece e converter o que ele devolve.

```dataforge
adopt Arcane.Ponte as Ponte
```

**Funções (12)**

| Assinatura |
|------------|
| `assinatura(valor)` |
| `atributos(valor)` |
| `chamavel(x)` |
| `cluster(valor)` |
| `doc(valor)` |
| `empacotado() -> bool` |
| `importar(nome)` |
| `onde() -> str` |
| `tem(nome)` |
| `tipo(valor) -> str` |
| `vault(valor)` |
| `versao(nome)` |


---

## Arcane.Qualidade

Qualidade de dados: as seis dimensões, perfil, validação e limpeza.

```dataforge
adopt Arcane.Qualidade as Qualidade
```

**Funções (13)**

| Assinatura |
|------------|
| `atualidade(linhas, campo, dias=1)` |
| `completude(linhas, campos=None)` |
| `conferir(linhas, regras, parar_em=0)` |
| `duplicadas(linhas, campos)` |
| `esperar(linhas, regras, minimo=1.0)` |
| `fora_da_faixa(linhas, campo, minimo=None, maximo=None)` |
| `formatos()` |
| `perfil(linhas, amostra=0)` |
| `preencher(linhas, padroes)` |
| `relatorio(resultado, largura=72)` |
| `sem_duplicadas(linhas, campos=None)` |
| `so_validas(linhas, regras)` |
| `unicidade(linhas, campo)` |
