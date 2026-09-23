# -*- coding: utf-8 -*-
"""
O catalogo dos modulos da stdlib: nome, nome curto e para que serve.

Ele existe pelo mesmo motivo de 'catalogo_erros.py'. A descricao de
cada modulo era escrita em TRES lugares — a doc em Markdown, os dados
do site e a pagina de visao geral — e as tres divergiram: a pagina
ainda anunciava "vinte modulos e 675 simbolos" quando ja eram 33 e
1143, e o Arcane.Crypto aparecia com 38 simbolos tendo 48.

Divergencia assim nao se resolve com atencao; resolve-se tirando as
copias. A contagem de simbolos NAO esta aqui de proposito: ela sai do
codigo, sempre. O que se escreve a mao e so o que o codigo nao sabe
dizer — para que o modulo serve.

A ordem e a da doc: os quatro grandes primeiro, depois o resto por
assunto.
"""

#: nome oficial -> (para que serve, nome curto que 'adopt' tambem aceita)
DESCRICOES = {
    "Arcane.Janela": ("Aplicação de mesa nativa com zero dependência: o Tk vem "
                      "na biblioteca padrão. A árvore é separada do desenho, "
                      "como na Vitrine — e por isso uma tela se testa sem "
                      "display nenhum.",
                      "Janela / desktop"),
    "Arcane.IoT": ("Arduino e ESP32: Firmata pelo cabo, sketch gerado e gravado, "
                   "sensores, MQTT — e um simulador de placa para testar sem hardware.",
                   "IoT / Arduino"),
    "Arcane.Math": ("Matemática, álgebra linear e estatística básica.", "Math"),
    "Arcane.Text": ("Manipulação de texto, formatação, tabelas e conversão de caixa.", "Text"),
    "Arcane.Analytics": ("Análise de dados: estatística, regressão, clustering e gráficos ASCII.", "Analytics"),
    "Arcane.Functional": ("Utilitários funcionais: composição, lentes, Maybe/Either, transdutores.", "Functional"),
    "Arcane.Database": ("Banco de dados SQLite: tabelas, consultas, migrações e importação.", "Database / DB"),
    "Arcane.Excel": ("Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame.", "Excel / Xlsx"),
    "Arcane.Meta": ("Metadados de decorador: ler @Nome em tempo de execução.", "Meta"),
    "Kiln": ("Framework web: rotas, middleware, templates, sessão e arquivos estáticos.", "Kiln"),
    "Arcane.Test": ("Asserções e organização de suítes de teste.", "Test"),
    "Arcane.Regex": ("Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone).", "Regex"),
    "Arcane.IO": ("Arquivos, diretórios, JSON, CSV e shell.", "IO"),
    "Arcane.Http": ("Servidor HTTP: rotas, middleware, JSON, arquivos estáticos.", "Http / Server"),
    "Arcane.Async": ("Promessas, filas, agendamento e execução concorrente.", "Async"),
    "Arcane.Data": ("DataFrames, séries e transformações tabulares.", "Data"),
    "Arcane.Web": ("Cliente HTTP, URL encoding e JSON.", "Web / Network"),
    "Arcane.Cortex": ("Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA.", "Cortex"),

    # ── DataForge 4.0 ──
    "Arcane.Time": ("Datas, horas, durações e cronometragem.", "Time"),
    "Arcane.OS": ("Sistema operacional, ambiente, disco e processo atual.", "OS"),
    "Arcane.Process": ("Execução de processos externos, com stdout, stderr e código de saída.", "Process"),
    "Arcane.Logging": ("Registro estruturado de eventos, com níveis e destinos.", "Logging / Log"),
    "Arcane.Crypto": ("Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305). Assina e verifica JWT (HS256/384/512), com o algoritmo decidido por quem verifica e não pelo token.", "Crypto"),
    "Arcane.Seguranca": ("Escape por destino (HTML, atributo, JS, URL, shell, SQL LIKE, CSV, cabeçalho, log), sanitização de HTML por lista de permitidos, política e força de senha com vazamento por k-anonimato, TOTP/HOTP e códigos de recuperação, token e URL assinados com prazo e propósito, varredura de segredos por formato, redação de PII, defesa de SSRF e de travessia de caminho, limitador de taxa, bloqueio progressivo, trilha de auditoria encadeada e dez regras de análise estática.", "Seguranca"),
    "Arcane.Politica": ("Motor de autorização: RBAC com herança, ABAC por atributo, ACL por objeto, grupos, isolamento por inquilino, negação explícita que vence o papel e delegação com prazo. O padrão é negar, e toda decisão diz qual regra a tomou — um motor que responde só sim/não é impossível de auditar.", "Politica"),
    "Arcane.Chaves": ("Ciclo de vida de chave criptográfica: propósito cobrado, prazo, rotação que mantém as antigas decifrando o passado, identificador no dado cifrado, cifragem em envelope (DEK/KEK), recifragem, derivação por contexto (HKDF) e exportação do cofre cifrada pela senha mestra.", "Chaves"),
    "Arcane.Deteccao": ("Regras de detecção sobre eventos, com correlação por chave em janela deslizante, supressão, gravidade e mapa para MITRE ATT&CK; indicadores de comprometimento com prazo e normalização; padrões sobre conteúdo e leitura de log de acesso. O alerta carrega os eventos que o causaram.", "Deteccao"),
    "Arcane.GitHub": ("O que um programa precisa para viver no GitHub: no Actions, saídas, variáveis e resumo com delimitador seguro, anotações escapadas que aparecem na linha do PR, máscara linha a linha e grupos; webhooks com assinatura HMAC conferida em tempo constante sobre os bytes originais; e a API REST com paginação por Link e o limite de taxa que sobrou.", "GitHub"),
    "Arcane.Gramatica": ("A gramática da linguagem como dado: as produções em EBNF, cada uma com um exemplo conferido contra o parser, a tabela de precedência provada pela árvore, os tokens de um texto, as instruções que o parser entendeu e a validação de sintaxe sem executar nada.", "Gramatica"),
    "Arcane.Privacidade": ("O que a LGPD pede, como operações sobre dado: pseudonimização com chave (e não hash sem chave, que se desfaz), generalização de quase-identificadores, a medida do k-anonimato, minimização por lista de permitidos, retenção, consentimento por titular e por finalidade com histórico, os direitos de acesso e eliminação percorrendo todo lugar onde o dado mora, e contagem com privacidade diferencial.", "Privacidade"),
    "Arcane.Integridade": ("Provar que o que está aqui é o que foi posto aqui: o valor SRI de um script de CDN, o manifesto SHA-256 de uma pasta com o que foi acrescentado, removido e alterado, e o manifesto assinado com uma chave que mora fora dali.", "Integridade"),
    "Arcane.Evolucao": ("Como uma API muda sem pegar ninguém de surpresa: marcar uma ação como obsoleta (desde quando, por quê, o que usar) ou experimental, e manter um nome antigo que avisa. O aviso sai uma vez por ação, na saída de erro, e DF_OBSOLETOS=erro o transforma em erro no CI.", "Evolucao"),
    "Arcane.Algoritmos": ("Os algoritmos clássicos com a complexidade como dado: busca binária, merge sort estável, counting sort, BFS, DFS, ordem topológica que mostra o ciclo, Dijkstra que recusa peso negativo, LCS, Levenshtein, mochila 0/1, KMP e o crivo — cada um conferido contra uma implementação ingênua.", "Algoritmos"),
    "Arcane.Collections": ("Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca.", "Collections"),
    "Arcane.Serialization": ("JSON, CSV, INI, TOML, XML e conversões entre eles.", "Serialization / Serde"),

    # ── Depois do 4.0 ──
    "Arcane.Forge": ("Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface.", "Forge / Banco"),
    "Arcane.Crucible": ("Framework de testes: suítes, matchers, fixtures, dublês e benchmark.", "Crucible"),
    "Arcane.Iter": ("Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize.", "Iter"),
    "Arcane.Color": ("Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore.", "Color / Cor"),
    "Arcane.Concurrent": ("Threads, processos, canal bloqueante, grupo de tarefas e prazo.", "Concurrent / Paralelo"),
    "Arcane.Archive": ("Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb. Comprime e descomprime VALORES em memória, em deflate cru ou em gzip, com a taxa medida.", "Archive / Zip"),
    "Arcane.Pipeline": ("Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório.", "Pipeline / Fluxo"),
    "Arcane.Stream": ("Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo.", "Stream / Corrente"),
    "Arcane.Observar": ("Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados.", "Observar / Observe"),
    "Arcane.Quadro": ("A tabela de dados: colunas nomeadas e linhas como vault. Filtrar, agrupar, resumir, juntar, pivotar, limpar a ausência e a duplicata, converter tipos, normalizar, codificar e descrever — colunar por dentro, imutável por fora.", "Quadro"),
    "Arcane.Lago": ("Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação.", "Lago / Parquet"),
    "Arcane.Telegram": ("Bots de Telegram, do primeiro '/start' ao webhook em producao: cliente da Bot API com o limite de taxa lido de onde ele chega, tratadores por comando, texto, botao, midia e consulta inline, conversa como maquina de estados por chat, teclados, o escape de MarkdownV2 que salva a mensagem inteira, e uma sonda que testa o bot sem token e sem rede.", "Telegram"),
    "Arcane.Reativo": ("Valores que avisam quando mudam: sinal (um valor com estado), derivado (calculado de outros, preguicoso e memorizado, com as dependencias DESCOBERTAS na execucao), efeito (o que acontece quando muda, com limpeza entre ciclos) e observavel (um fluxo no tempo, com morph, sift, distill, distintos, esperar, limitar, combinar e juntar). A diferenca entre valor e fluxo e mantida de proposito: um clique e fluxo, um saldo e valor.", "Reativo"),
    "Arcane.Dominio": ("As pecas de um modelo de dominio que se sustenta (DDD): valor (igualdade por conteudo, imutavel, com regra cobrada na criacao), entidade (igualdade por identidade), agregado (a unica porta de escrita, com invariantes conferidas na SAIDA de cada comando e desfazer quando o comando falha no meio), evento (um fato no passado, imutavel), regra (condicao de negocio que se combina com e/ou/nao e explica o \"nao\"), repositorio (guarda agregados INTEIROS), unidade de trabalho (confirma tudo ou nada, e so entao publica) e contexto delimitado (com a traducao que atravessa a fronteira).", "Dominio"),
    "Arcane.Estrutura": ("Layout binario com NOME, e o ponteiro que o percorre: uma estrutura de campos nomeados com a ordem dos bytes cobrada e o alinhamento declarado (e conferido), uma janela que le e escreve no bloco original sem copiar, um bloco que sabe dizer quando foi liberado, e um ponteiro com aritmetica por ELEMENTO, cast, distancia e dono fraco. Fica entre o Arcane.Bytes, que empacota por formato posicional, e o Arcane.C, que exige FFI.", "Estrutura"),
    "Arcane.Malha": ("Chamada entre serviços que não mente: cliente HTTP com prazo, retry com recuo e tremor, disjuntor de três estados, descoberta por nome e propagação automática do rastro do pedido.", "Malha"),
    "Arcane.Url": ("Endereços: ler um URL em partes, montar a partir delas, resolver caminho relativo como um navegador, trocar parâmetros preservando os outros, query string em vault (ou em cluster, quando a chave repete) e escape para caminho e para valor.", "Url"),
    "Arcane.Bytes": ("Dados binários: empacotar e desempacotar campos com a ordem dos bytes declarada, um cursor que anda pelo bloco sem acertar índice à mão, janela que olha sem copiar, hexadecimal, base64, bits, despejo estilo hexdump e comparação em tempo fixo.", "Bytes"),
    "Arcane.Rede": ("TCP, UDP, DNS e TLS: conexão com prazo, leitura que insiste até completar, servidor de uma thread por conexão, datagrama, resolução de nome, porta livre, espera de porta abrir e a validade do certificado de um host.", "Rede"),
    "Arcane.Bench": ("Medir, comparar e descobrir a classe de custo: tempo de uma ação, implementações lado a lado sem a ordem decidir quem ganha, e a curva medida em tamanhos crescentes dizendo qual O() descreve o que aconteceu.", "Bench"),
    "Arcane.Reflexo": ("Reflexão sobre blueprints, contratos e objetos: campos, métodos, modificadores, MRO, herdeiros, anotações, invocação por nome respeitando a visibilidade, criação de tipos em execução e diagrama de classes em Mermaid.", "Reflexo"),
    "Arcane.Objetos": ("Cópia rasa e funda, congelamento, igualdade estrutural, hash coerente, ordenação por campos e serialização polimórfica que só reconstrói os tipos autorizados e resolve ciclos.", "Objetos"),
    "Arcane.Injecao": ("Contêiner de injeção de dependência: único, transitório e por escopo, fábrica, valor pronto, dependência preguiçosa e opcional, injeção por construtor, campo e método, e detecção de ciclo com a cadeia inteira.", "Injecao / DI"),
    "Arcane.Padroes": ("Os padrões de projeto que pedem mecanismo: único, pool, construtor, protótipo, flyweight, proxy, adaptador, composto, comandos com desfazer, cadeia, especificação, máquina de estados, memento, visitante, observável, mediador, repositório e barramento.", "Padroes"),
    "Arcane.Memoria": ("O ciclo de vida visto de dentro: referência fraca, mapa fraco, ação ao descartar, instâncias vivas por blueprint, tamanho e layout. E o COLETOR sob controle: ligar, desligar, 'sem_gc' num trecho sensível a latência (que religa mesmo se o corpo falhar), limiares por geração, 'congelar' o que já vive para tirá-lo das varreduras, e a conta por geração. Mais a arena: um lote preparado de uma vez e reaproveitado, com 'limpar' soltando tudo numa chamada.", "Memoria"),
    "Arcane.C": ("Falar com biblioteca nativa: abrir .so/.dylib/.dll, chamar funcao com assinatura declarada, struct e uniao com o layout de verdade (tamanho, alinhamento e deslocamento), ponteiro cru com aritmetica, memoria alocada a mao e callback — uma acao da linguagem chamada de dentro do C. Sobre ctypes, da biblioteca padrao: zero dependencia.", "C / Nativo"),
    "Arcane.Macro": ("A arvore como dado: ler o corpo de uma acao, percorrer, transformar e gerar codigo. 'citar' transforma texto em arvore, 'reescrever' devolve uma acao com o corpo trocado, 'nome_fresco' e 'renomear' dao higiene, e 'derivar' e a macro de atributo que gera __str__, __eq__, __lt__ e para_vault a partir dos campos.", "Macro"),
    "Arcane.Compilador": ("O caminho de compilacao como dado: os tokens, a arvore, o HIR (a arvore depois do acucar, com a lista do que e acucar e do que so parece), o MIR (bloco basico, aresta, laco e tratador) e as analises que so o grafo responde — alcance, vivacidade, constante em todo caminho, escapatoria e o nome que so um ramo define. O LIR diz o que o compilador de fechamentos compilou e o que recuou para a arvore.", "Compilador"),
    "Arcane.Laco": ("O laco de eventos, o escalonador e as fibras: UMA thread dormindo no seletor do sistema (epoll, kqueue ou select) em vez de uma thread por conexao. Fila de prazos com 'apos' e 'a_cada', fila de prontas com teto opcional (contrapressao), executor para o trabalho que bloqueia, cancelamento, e fibras de verdade — um 'stream action' suspenso em cada 'emit'.", "Laco / Reator"),
    "Arcane.Perfil": ("Medir com rigor, onde o 'Bench' da a media: percentis (p50, p95, p99, p999) com aquecimento separado, comparacao com SIGNIFICANCIA estatistica (Mann-Whitney, que nao supoe normalidade — tempo de execucao nao e normal), linha de base guardada para acusar regressao no CI, flame graph das ACOES da linguagem em SVG sem nada de fora, pausas do coletor medidas na fonte e contencao de trava.", "Perfil"),
    "Arcane.Inicio": ("O que roda ANTES da primeira linha: as fases da partida nomeadas e em ordem, e quanto cada 'adopt' custou — que e a unica forma de responder 'por que o programa demora a comecar?' sem cronometrar a mao. Mais armazenamento por THREAD com inicializacao e finalizador (o 'threading.local' da o armazem e nao da o resto), e a pilha que se pergunta: profundidade, teto, quanto falta e os quadros abertos.", "Inicio"),
    "Arcane.Capacidade": ("A fronteira de CAPACIDADE: roda uma acao com a lista de poderes que ela pode alcancar, e recusa o resto pelo NOME da capacidade que falta. A ponte para o Python e capacidade propria, e nunca vem junto. NAO e caixa contra programa hostil, e o modulo diz isso em 'limites()': ele bloqueia a autoridade ambiente (o 'adopt'), e nao tira o que foi ENTREGUE — o que e o modelo de capacidade, nao um defeito.", "Capacidade"),
    "Arcane.Abi": ("A superficie de um modulo e o CONTRATO dele, e quebra-la e o mesmo problema que quebrar uma ABI — com outro nome e o mesmo sintoma: nao e erro de quem publicou, e erro de quem consome, depois. Compara duas versoes e diz o que quebrou (simbolo removido, aridade incompativel, parametro renomeado, tipo trocado, campo novo obrigatorio) e qual bump de semver a mudanca EXIGE. Mais o mapa de simbolos: de onde vem cada nome, o analogo do mapa que um ligador escreve.", "Abi"),
    "Arcane.Alvo": ("'Isso roda no navegador?', respondido a partir dos 'adopt'. Seis alvos descritos (servidor, cli, navegador, wasi, funcao serverless, embarcado) com o que cada um suporta e POR QUE nao suporta o resto, no mesmo vocabulario de capacidade do 'Arcane.Capacidade'. A leitura e ESTATICA e o modulo diz isso em 'limites()': um 'roda' quer dizer 'nao achei impedimento por esta via', e nao 'vai funcionar'.", "Alvo"),
    "Arcane.Ecossistema": ("O inventario da implementacao, CONFERIDO contra ela. Cada componente do desenho do ecossistema aponta arquivos de verdade e carrega um de tres estados: 'existe', 'equivale' (ha outra peca que responde a mesma pergunta, nomeada) ou 'nao-existe' (com o porque escrito). 'conferir()' cobra as duas direcoes — todo caminho citado existe no disco, e todo modulo do nucleo aparece em algum componente —, e e isso que impede o mapa de mentir quando uma peca muda de nome. 'o_que_nao_existe()' e a resposta honesta a 'o DataForge tem backend LLVM?'.", "Ecossistema"),
    "Arcane.Principios": ("Os dez principios de design, cada um com uma prova que RODA e o numero que ela deu — duas delas rodam o analisador e uma roda o interpretador, porque 'verificacao antes de rodar' e 'custo zero quando desligado' sao coisas que se demonstram. O veredito nao e dez de dez de proposito: 5 cumpridos, 4 parciais e 1 que nao se aplica. E as nove TENSOES: onde dois principios se contradizem, qual venceu, o custo aceito e o arquivo onde a decisao mora.", "Principios"),
    "Arcane.Percurso": ("O caminho inteiro de um arquivo, fase por fase, MEDIDO: lexer, parser, HIR, tipos, MIR, analises, SSA, passes e LIR, com o que cada fase produziu e quanto tempo levou. Responde 'onde o tempo vai' quando um arquivo demora a abrir no editor. Ele NAO executa o programa — executar e o que o programa faz, e um comando que mostra fases nao pode abrir soquete. Traz tambem as divergencias entre o caminho real e o desenho da referencia.", "Percurso"),
    "Arcane.Dsl": ("Combinadores para escrever uma linguagem pequena, propria: texto, numero, nome, aspas, espaco, sequencia, alternativa, repeticao, opcional e separado_por, com 'analisar' devolvendo Resultado e a falha dizendo a posicao e o que era esperado.", "Dsl"),
    "Arcane.Posse": ("Quem e o dono, quem tomou emprestado, e quando solta: posse exclusiva com liberacao deterministica ('dono' e 'com', o RAII), emprestimo com escopo (muitos leem OU um escreve, cobrado quando roda), contagem de referencia deterministica ('compartilhado' e 'atomico') e referencia fraca que quebra o ciclo.", "Posse"),
    "Arcane.Stm": ("Memoria transacional: escritas que acontecem JUNTAS ou nao acontecem. Variavel transacional, 'atomicamente' com validacao otimista e repeticao no conflito, 'retentar' que espera em vez de girar, 'ou_entao' para compor duas operacoes bloqueantes, e estatisticas de conflito.", "Stm / Transacional"),
    "Arcane.Resultado": ("A falha como VALOR, e a ausencia com nome: 'ok'/'falha' para quem devolve o erro em vez de levanta-lo, com 'mapear', 'entao', 'recuperar', 'ou' e 'todos' (a primeira falha vence); e 'Talvez' ('algo'/'nada') para onde 'void' e ambiguo — distinguir 'a chave nao esta la' de 'a chave vale void'.", "Resultado / Result"),
    "Arcane.Tipos": ("Reflexao sobre tipos: os metadados de um 'type' declarado (especie, base, regra, opaco), 'satisfaz' para conferir sem levantar, a forma ESTRUTURAL de um valor ('Cluster<Integer>', 'Tuple<Integer, String>') e os campos de um record ou instancia com o tipo de cada um.", "Tipos"),
    "Arcane.Eventos": ("Publicar e assinar sem as duas partes se conhecerem: emissor com curinga, ouvinte de uma vez só, contexto por thread que atravessa as camadas, fila de trabalho em segundo plano, e fila persistente em SQLite que sobrevive ao processo, com recuo exponencial, atraso e hora marcada, prioridade, chave contra repetição e carta morta.", "Eventos"),
    "Arcane.Cli": ("A linha de comando de um programa escrito em DataForge: opções tipadas com valor padrão e escolhas, argumentos posicionais, subcomandos, ajuda gerada da declaração, perguntas no terminal e console interativo.", "Cli"),
    "Arcane.Email": ("Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza no cabeçalho, SMTP com TLS por padrão, prévia sem enviar e caixa de teste com o mesmo contrato.", "Email"),
    "Arcane.Html": ("Ler HTML de verdade: seletor CSS, texto que junta com espaço, links absolutos, tabela como dado, escapar contra XSS, limpar toda a marcação e podar deixando só as tags permitidas.", "Html"),
    "Arcane.Lavra": ("A consulta tipada: o cliente diz exatamente quais campos quer, numa consulta indentada, e recebe exatamente aqueles. O esquema nasce dos 'record' que já existem; traz resolvedores, contexto, trechos, variáveis, diretivas, contratos, uniões, introspecção, validação antes de executar, lote contra o N+1, paginação por cursor, limites de profundidade e custo, assinaturas por WebSocket e federação de vários serviços.", "Lavra"),
    "Arcane.Vitrine": ("O framework de dashboards e aplicações de dados: você escreve um programa de cima para baixo e ele vira uma página web, com componentes, layout, gráficos em SVG, estado por sessão e cache — servido pelo Kiln.", "Vitrine"),
    "Arcane.API": ("A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas.", "API"),
    "Arcane.Decimal": ("Número decimal exato, para quando 0,1 + 0,2 precisa dar 0,3 — dinheiro, imposto, e todo número que alguém confere na mão.", "Decimal / Exato"),
    "Arcane.Ponte": ("A ponte para o Python: perguntar se um pacote existe, explorar o que ele oferece e converter o que ele devolve.", "Ponte / Bridge"),
    "Arcane.Qualidade": ("Qualidade de dados: as seis dimensões, perfil, validação e limpeza.", "Qualidade / Quality"),
}


def descricao(nome):
    """Para que serve o modulo, ou "" se ele nao esta no catalogo."""
    return DESCRICOES.get(nome, ("", ""))[0]


def nome_curto(nome):
    """O apelido que 'adopt' tambem aceita."""
    return DESCRICOES.get(nome, ("", ""))[1]


#: A assinatura das funcoes que a stdlib expoe direto do C do Python.
#:
#: `math.factorial` chama o parametro de `x` ate o Python 3.12 e de `n`
#: a partir do 3.13. Como `Arcane.Math` publica `math.factorial` sem
#: envolve-la, `inspect.signature` vazava o nome interno do CPython para
#: dentro da documentacao da linguagem — e `doc/BIBLIOTECA_PADRAO.md`
#: passava a depender da versao de Python de quem rodou o gerador. Duas
#: maquinas certas produziam arquivos diferentes, e o CI cobrava a
#: diferenca sem que ninguem tivesse errado.
#:
#: A tabela existe para o DataForge nomear a propria interface. O nome
#: aqui e o que a documentacao mostra, independente de build.
#:
#: Ha teste garantindo que toda funcao C exposta tenha entrada: uma que
#: faltasse voltaria a herdar o nome do CPython em silencio.
ASSINATURAS = {
    # ── Arcane.Math ──
    "abs": "(x)",
    "acos": "(x)",
    "asin": "(x)",
    "atan": "(x)",
    "atan2": "(y, x)",
    "ceil": "(x)",
    "comb": "(n, k)",
    "cos": "(x)",
    "degrees": "(x)",
    "exp": "(x)",
    "factorial": "(n)",
    "floor": "(x)",
    "gcd": "(*inteiros)",
    "hypot": "(*coordenadas)",
    "log": "(x, base=e)",
    "log10": "(x)",
    "log2": "(x)",
    "perm": "(n, k=void)",
    "pow": "(x, y)",
    "radians": "(x)",
    "round": "(numero, casas=void)",
    "sin": "(x)",
    "sqrt": "(x)",
    "tan": "(x)",
    # ── Globais ──
    "max": "(*valores)",
    "min": "(*valores)",
}


def assinatura_fixa(simbolo):
    """A assinatura declarada, ou None se o simbolo nao esta na tabela."""
    return ASSINATURAS.get(simbolo)


def resumo_do_simbolo(valor):
    """A primeira linha ÚTIL da documentação de um símbolo.

    Uma função escrita em C guarda a assinatura dentro da própria
    docstring quando o CPython não a expõe por introspecção:

        3.13   'hypot(*coordinates) -> value\\n\\nMultidimensional…'
        3.14   'Multidimensional…'

    Ou seja, a primeira linha muda com a versão do Python — e o arquivo
    gerado passava a depender de quem rodou o gerador, com o job do CI
    que compara o versionado com o gerado reprovando sozinho. Pior que
    isso: no 3.13 o resumo publicado era `hypot(*coordinates) -> value`,
    que repete a assinatura em inglês em vez de dizer o que a função faz.

    Pular a linha de assinatura resolve os dois de uma vez, e o critério
    é estreito de propósito: ela precisa começar com o nome do próprio
    símbolo seguido de '('.
    """
    import inspect

    texto = (inspect.getdoc(valor) or "").strip()
    if not texto:
        return ""
    linhas = texto.split("\n")
    nome = getattr(valor, "__name__", "")
    if nome and linhas[0].startswith(nome + "("):
        for linha in linhas[1:]:
            if linha.strip():
                return linha.strip()
        return ""
    return linhas[0].strip()
