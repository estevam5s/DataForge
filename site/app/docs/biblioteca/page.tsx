import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

// Gerado por tools/gerar_pagina_biblioteca.py — não edite à mão.

export const metadata: Metadata = {
  title: "Biblioteca Arcane",
  description: "71 módulos e 1971 símbolos, sem uma única dependência externa.",
};

const blocos: Bloco[] = [
  {
    "h2": "Importar"
  },
  {
    "code": "adopt Arcane.Math as Math                # o módulo inteiro\nadopt Arcane.Math.{sqrt, factorial}       # só o que você usa\nadopt {sqrt as raiz} from Arcane.Math     # com apelido\n\nout Math.sqrt(16), sqrt(16), raiz(16)",
    "lang": "df"
  },
  {
    "p": "Cada módulo tem um **nome curto** equivalente: `adopt Math as M` funciona igual a `adopt Arcane.Math as M`."
  },
  {
    "h2": "Os 71 módulos"
  },
  {
    "p": "São **1971 símbolos** ao todo. Esta tabela é gerada do próprio código: a contagem sai dos módulos e a descrição, do catálogo."
  },
  {
    "table": {
      "head": [
        "Módulo",
        "Símbolos",
        "Para quê"
      ],
      "rows": [
        [
          "[`Arcane.Vitrine`](/docs/vitrine)",
          "213",
          "O framework de dashboards e aplicações de dados: você escreve um programa de cima para baixo e ele vira uma página web, com componentes, layout, gráficos em SVG, estado por sessão e cache — servido pelo Kiln."
        ],
        [
          "[`Kiln`](/docs/kiln)",
          "73",
          "Framework web: rotas, middleware, templates, sessão e arquivos estáticos."
        ],
        [
          "[`Arcane.Math`](/docs/biblioteca/math)",
          "72",
          "Matemática, álgebra linear e estatística básica."
        ],
        [
          "`Arcane.Color`",
          "66",
          "Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore."
        ],
        [
          "[`Arcane.Analytics`](/docs/biblioteca/analytics)",
          "65",
          "Análise de dados: estatística, regressão, clustering e gráficos ASCII."
        ],
        [
          "[`Arcane.Database`](/docs/biblioteca/database)",
          "64",
          "Banco de dados SQLite: tabelas, consultas, migrações e importação."
        ],
        [
          "[`Arcane.Collections`](/docs/biblioteca/collections)",
          "63",
          "Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca."
        ],
        [
          "[`Arcane.Text`](/docs/biblioteca/text)",
          "59",
          "Manipulação de texto, formatação, tabelas e conversão de caixa."
        ],
        [
          "[`Arcane.Functional`](/docs/biblioteca/functional)",
          "56",
          "Utilitários funcionais: composição, lentes, Maybe/Either, transdutores."
        ],
        [
          "[`Arcane.Time`](/docs/biblioteca/time)",
          "54",
          "Datas, horas, durações e cronometragem."
        ],
        [
          "[`Arcane.Async`](/docs/biblioteca/async)",
          "52",
          "Promessas, filas, agendamento e execução concorrente."
        ],
        [
          "[`Arcane.Crypto`](/docs/biblioteca/crypto)",
          "52",
          "Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305). Assina e verifica JWT (HS256/384/512), com o algoritmo decidido por quem verifica e não pelo token."
        ],
        [
          "[`Arcane.Crucible`](/docs/tecnicas/testes)",
          "50",
          "Framework de testes: suítes, matchers, fixtures, dublês e benchmark."
        ],
        [
          "`Arcane.Iter`",
          "44",
          "Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize."
        ],
        [
          "[`Arcane.OS`](/docs/biblioteca/os)",
          "43",
          "Sistema operacional, ambiente, disco e processo atual."
        ],
        [
          "`Arcane.Lavra`",
          "42",
          "A consulta tipada: o cliente diz exatamente quais campos quer, numa consulta indentada, e recebe exatamente aqueles. O esquema nasce dos 'record' que já existem; traz resolvedores, contexto, trechos, variáveis, diretivas, contratos, uniões, introspecção, validação antes de executar, lote contra o N+1, paginação por cursor, limites de profundidade e custo, assinaturas por WebSocket e federação de vários serviços."
        ],
        [
          "`Arcane.Reflexo`",
          "38",
          "Reflexão sobre blueprints, contratos e objetos: campos, métodos, modificadores, MRO, herdeiros, anotações, invocação por nome respeitando a visibilidade, criação de tipos em execução e diagrama de classes em Mermaid."
        ],
        [
          "[`Arcane.Test`](/docs/biblioteca/test)",
          "34",
          "Asserções e organização de suítes de teste."
        ],
        [
          "[`Arcane.Concurrent`](/docs/tecnicas/concorrencia)",
          "33",
          "Threads, processos, canal bloqueante, grupo de tarefas e prazo."
        ],
        [
          "[`Arcane.Regex`](/docs/biblioteca/regex)",
          "32",
          "Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone)."
        ],
        [
          "[`Arcane.IO`](/docs/biblioteca/io)",
          "30",
          "Arquivos, diretórios, JSON, CSV e shell."
        ],
        [
          "[`Arcane.Excel`](/docs/biblioteca/excel)",
          "29",
          "Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame."
        ],
        [
          "[`Arcane.Forge`](/docs/tecnicas/banco-de-dados)",
          "28",
          "Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface."
        ],
        [
          "[`Arcane.Serialization`](/docs/biblioteca/serialization)",
          "26",
          "JSON, CSV, INI, TOML, XML e conversões entre eles."
        ],
        [
          "[`Arcane.Bytes`](/docs/biblioteca/bytes)",
          "25",
          "Dados binários: empacotar e desempacotar campos com a ordem dos bytes declarada, um cursor que anda pelo bloco sem acertar índice à mão, janela que olha sem copiar, hexadecimal, base64, bits, despejo estilo hexdump e comparação em tempo fixo."
        ],
        [
          "[`Arcane.Cortex`](/docs/biblioteca/cortex)",
          "25",
          "Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA."
        ],
        [
          "`Arcane.Laco`",
          "25",
          "O laco de eventos, o escalonador e as fibras: UMA thread dormindo no seletor do sistema (epoll, kqueue ou select) em vez de uma thread por conexao. Fila de prazos com 'apos' e 'a_cada', fila de prontas com teto opcional (contrapressao), executor para o trabalho que bloqueia, cancelamento, e fibras de verdade — um 'stream action' suspenso em cada 'emit'."
        ],
        [
          "`Arcane.Compilador`",
          "24",
          "O caminho de compilacao como dado: os tokens, a arvore, o HIR (a arvore depois do acucar, com a lista do que e acucar e do que so parece), o MIR (bloco basico, aresta, laco e tratador) e as analises que so o grafo responde — alcance, vivacidade, constante em todo caminho, escapatoria e o nome que so um ramo define. O LIR diz o que o compilador de fechamentos compilou e o que recuou para a arvore."
        ],
        [
          "`Arcane.Memoria`",
          "24",
          "O ciclo de vida visto de dentro: referência fraca, mapa fraco, ação ao descartar, instâncias vivas por blueprint, tamanho e layout. E o COLETOR sob controle: ligar, desligar, 'sem_gc' num trecho sensível a latência (que religa mesmo se o corpo falhar), limiares por geração, 'congelar' o que já vive para tirá-lo das varreduras, e a conta por geração. Mais a arena: um lote preparado de uma vez e reaproveitado, com 'limpar' soltando tudo numa chamada."
        ],
        [
          "`Arcane.C`",
          "23",
          "Falar com biblioteca nativa: abrir .so/.dylib/.dll, chamar funcao com assinatura declarada, struct e uniao com o layout de verdade (tamanho, alinhamento e deslocamento), ponteiro cru com aritmetica, memoria alocada a mao e callback — uma acao da linguagem chamada de dentro do C. Sobre ctypes, da biblioteca padrao: zero dependencia."
        ],
        [
          "`Arcane.Malha`",
          "23",
          "Chamada entre serviços que não mente: cliente HTTP com prazo, retry com recuo e tremor, disjuntor de três estados, descoberta por nome e propagação automática do rastro do pedido."
        ],
        [
          "`Arcane.Padroes`",
          "20",
          "Os padrões de projeto que pedem mecanismo: único, pool, construtor, protótipo, flyweight, proxy, adaptador, composto, comandos com desfazer, cadeia, especificação, máquina de estados, memento, visitante, observável, mediador, repositório e barramento."
        ],
        [
          "[`Arcane.Observar`](/docs/tecnicas/observar)",
          "19",
          "Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados."
        ],
        [
          "`Arcane.Dsl`",
          "18",
          "Combinadores para escrever uma linguagem pequena, propria: texto, numero, nome, aspas, espaco, sequencia, alternativa, repeticao, opcional e separado_por, com 'analisar' devolvendo Resultado e a falha dizendo a posicao e o que era esperado."
        ],
        [
          "[`Arcane.Lago`](/docs/tecnicas/lago)",
          "18",
          "Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação."
        ],
        [
          "[`Arcane.Http`](/docs/biblioteca/http)",
          "17",
          "Servidor HTTP: rotas, middleware, JSON, arquivos estáticos."
        ],
        [
          "[`Arcane.Stream`](/docs/tecnicas/streaming)",
          "17",
          "Streaming: tópicos, partições, offsets, grupos de consumo e janelas de tempo."
        ],
        [
          "[`Arcane.Decimal`](/docs/tecnicas/decimal)",
          "16",
          "Número decimal exato, para quando 0,1 + 0,2 precisa dar 0,3 — dinheiro, imposto, e todo número que alguém confere na mão."
        ],
        [
          "`Arcane.Perfil`",
          "16",
          "Medir com rigor, onde o 'Bench' da a media: percentis (p50, p95, p99, p999) com aquecimento separado, comparacao com SIGNIFICANCIA estatistica (Mann-Whitney, que nao supoe normalidade — tempo de execucao nao e normal), linha de base guardada para acusar regressao no CI, flame graph das ACOES da linguagem em SVG sem nada de fora, pausas do coletor medidas na fonte e contencao de trava."
        ],
        [
          "`Arcane.Posse`",
          "16",
          "Quem e o dono, quem tomou emprestado, e quando solta: posse exclusiva com liberacao deterministica ('dono' e 'com', o RAII), emprestimo com escopo (muitos leem OU um escreve, cobrado quando roda), contagem de referencia deterministica ('compartilhado' e 'atomico') e referencia fraca que quebra o ciclo."
        ],
        [
          "[`Arcane.Rede`](/docs/biblioteca/rede)",
          "16",
          "TCP, UDP, DNS e TLS: conexão com prazo, leitura que insiste até completar, servidor de uma thread por conexão, datagrama, resolução de nome, porta livre, espera de porta abrir e a validade do certificado de um host."
        ],
        [
          "[`Arcane.Process`](/docs/biblioteca/process)",
          "15",
          "Execução de processos externos, com stdout, stderr e código de saída."
        ],
        [
          "[`Arcane.Logging`](/docs/biblioteca/logging)",
          "14",
          "Registro estruturado de eventos, com níveis e destinos."
        ],
        [
          "[`Arcane.Url`](/docs/biblioteca/url)",
          "14",
          "Endereços: ler um URL em partes, montar a partir delas, resolver caminho relativo como um navegador, trocar parâmetros preservando os outros, query string em vault (ou em cluster, quando a chave repete) e escape para caminho e para valor."
        ],
        [
          "[`Arcane.Archive`](/docs/tecnicas/arquivos)",
          "13",
          "Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb. Comprime e descomprime VALORES em memória, em deflate cru ou em gzip, com a taxa medida."
        ],
        [
          "[`Arcane.Data`](/docs/biblioteca/data)",
          "13",
          "DataFrames, séries e transformações tabulares."
        ],
        [
          "`Arcane.Macro`",
          "13",
          "A arvore como dado: ler o corpo de uma acao, percorrer, transformar e gerar codigo. 'citar' transforma texto em arvore, 'reescrever' devolve uma acao com o corpo trocado, 'nome_fresco' e 'renomear' dao higiene, e 'derivar' e a macro de atributo que gera __str__, __eq__, __lt__ e para_vault a partir dos campos."
        ],
        [
          "`Arcane.Objetos`",
          "13",
          "Cópia rasa e funda, congelamento, igualdade estrutural, hash coerente, ordenação por campos e serialização polimórfica que só reconstrói os tipos autorizados e resolve ciclos."
        ],
        [
          "[`Arcane.Qualidade`](/docs/tecnicas/qualidade)",
          "13",
          "Qualidade de dados: as seis dimensões, perfil, validação e limpeza."
        ],
        [
          "`Arcane.Resultado`",
          "13",
          "A falha como VALOR, e a ausencia com nome: 'ok'/'falha' para quem devolve o erro em vez de levanta-lo, com 'mapear', 'entao', 'recuperar', 'ou' e 'todos' (a primeira falha vence); e 'Talvez' ('algo'/'nada') para onde 'void' e ambiguo — distinguir 'a chave nao esta la' de 'a chave vale void'."
        ],
        [
          "`Arcane.Stm`",
          "13",
          "Memoria transacional: escritas que acontecem JUNTAS ou nao acontecem. Variavel transacional, 'atomicamente' com validacao otimista e repeticao no conflito, 'retentar' que espera em vez de girar, 'ou_entao' para compor duas operacoes bloqueantes, e estatisticas de conflito."
        ],
        [
          "[`Arcane.Cli`](/docs/biblioteca/cli)",
          "12",
          "A linha de comando de um programa escrito em DataForge: opções tipadas com valor padrão e escolhas, argumentos posicionais, subcomandos, ajuda gerada da declaração, perguntas no terminal e console interativo."
        ],
        [
          "`Arcane.Inicio`",
          "12",
          "O que roda ANTES da primeira linha: as fases da partida nomeadas e em ordem, e quanto cada 'adopt' custou — que e a unica forma de responder 'por que o programa demora a comecar?' sem cronometrar a mao. Mais armazenamento por THREAD com inicializacao e finalizador (o 'threading.local' da o armazem e nao da o resto), e a pilha que se pergunta: profundidade, teto, quanto falta e os quadros abertos."
        ],
        [
          "[`Arcane.Meta`](/docs/biblioteca/meta)",
          "12",
          "Metadados de decorador: ler @Nome em tempo de execução."
        ],
        [
          "[`Arcane.Ponte`](/docs/tecnicas/ponte)",
          "12",
          "A ponte para o Python: perguntar se um pacote existe, explorar o que ele oferece e converter o que ele devolve."
        ],
        [
          "[`Arcane.Html`](/docs/biblioteca/html)",
          "11",
          "Ler HTML de verdade: seletor CSS, texto que junta com espaço, links absolutos, tabela como dado, escapar contra XSS, limpar toda a marcação e podar deixando só as tags permitidas."
        ],
        [
          "[`Arcane.Pipeline`](/docs/tecnicas/pipeline)",
          "11",
          "Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório."
        ],
        [
          "[`Arcane.Web`](/docs/biblioteca/web)",
          "11",
          "Cliente HTTP, URL encoding e JSON."
        ],
        [
          "[`Arcane.Eventos`](/docs/biblioteca/eventos)",
          "10",
          "Publicar e assinar sem as duas partes se conhecerem: emissor com curinga, ouvinte de uma vez só, contexto por thread que atravessa as camadas, fila de trabalho em segundo plano, e fila persistente em SQLite que sobrevive ao processo, com recuo exponencial, atraso e hora marcada, prioridade, chave contra repetição e carta morta."
        ],
        [
          "`Arcane.Quadro`",
          "10",
          "A tabela de dados: colunas nomeadas e linhas como vault. Filtrar, agrupar, resumir, juntar, pivotar, limpar a ausência e a duplicata, converter tipos, normalizar, codificar e descrever — colunar por dentro, imutável por fora."
        ],
        [
          "`Arcane.Tipos`",
          "10",
          "Reflexao sobre tipos: os metadados de um 'type' declarado (especie, base, regra, opaco), 'satisfaz' para conferir sem levantar, a forma ESTRUTURAL de um valor ('Cluster<Integer>', 'Tuple<Integer, String>') e os campos de um record ou instancia com o tipo de cada um."
        ],
        [
          "`Arcane.Ecossistema`",
          "9",
          "O inventario da implementacao, CONFERIDO contra ela. Cada componente do desenho do ecossistema aponta arquivos de verdade e carrega um de tres estados: 'existe', 'equivale' (ha outra peca que responde a mesma pergunta, nomeada) ou 'nao-existe' (com o porque escrito). 'conferir()' cobra as duas direcoes — todo caminho citado existe no disco, e todo modulo do nucleo aparece em algum componente —, e e isso que impede o mapa de mentir quando uma peca muda de nome. 'o_que_nao_existe()' e a resposta honesta a 'o DataForge tem backend LLVM?'."
        ],
        [
          "`Arcane.Abi`",
          "8",
          "A superficie de um modulo e o CONTRATO dele, e quebra-la e o mesmo problema que quebrar uma ABI — com outro nome e o mesmo sintoma: nao e erro de quem publicou, e erro de quem consome, depois. Compara duas versoes e diz o que quebrou (simbolo removido, aridade incompativel, parametro renomeado, tipo trocado, campo novo obrigatorio) e qual bump de semver a mudanca EXIGE. Mais o mapa de simbolos: de onde vem cada nome, o analogo do mapa que um ligador escreve."
        ],
        [
          "[`Arcane.API`](/docs/tecnicas/api)",
          "7",
          "A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas."
        ],
        [
          "`Arcane.Alvo`",
          "7",
          "'Isso roda no navegador?', respondido a partir dos 'adopt'. Seis alvos descritos (servidor, cli, navegador, wasi, funcao serverless, embarcado) com o que cada um suporta e POR QUE nao suporta o resto, no mesmo vocabulario de capacidade do 'Arcane.Capacidade'. A leitura e ESTATICA e o modulo diz isso em 'limites()': um 'roda' quer dizer 'nao achei impedimento por esta via', e nao 'vai funcionar'."
        ],
        [
          "`Arcane.Bench`",
          "7",
          "Medir, comparar e descobrir a classe de custo: tempo de uma ação, implementações lado a lado sem a ordem decidir quem ganha, e a curva medida em tamanhos crescentes dizendo qual O() descreve o que aconteceu."
        ],
        [
          "`Arcane.Capacidade`",
          "6",
          "A fronteira de CAPACIDADE: roda uma acao com a lista de poderes que ela pode alcancar, e recusa o resto pelo NOME da capacidade que falta. A ponte para o Python e capacidade propria, e nunca vem junto. NAO e caixa contra programa hostil, e o modulo diz isso em 'limites()': ele bloqueia a autoridade ambiente (o 'adopt'), e nao tira o que foi ENTREGUE — o que e o modelo de capacidade, nao um defeito."
        ],
        [
          "[`Arcane.Email`](/docs/biblioteca/email)",
          "6",
          "Montar e enviar e-mail: texto e HTML juntos, anexos, cópia oculta que não vaza no cabeçalho, SMTP com TLS por padrão, prévia sem enviar e caixa de teste com o mesmo contrato."
        ],
        [
          "`Arcane.Principios`",
          "6",
          "Os dez principios de design, cada um com uma prova que RODA e o numero que ela deu — duas delas rodam o analisador e uma roda o interpretador, porque 'verificacao antes de rodar' e 'custo zero quando desligado' sao coisas que se demonstram. O veredito nao e dez de dez de proposito: 5 cumpridos, 4 parciais e 1 que nao se aplica. E as nove TENSOES: onde dois principios se contradizem, qual venceu, o custo aceito e o arquivo onde a decisao mora."
        ],
        [
          "`Arcane.Injecao`",
          "5",
          "Contêiner de injeção de dependência: único, transitório e por escopo, fábrica, valor pronto, dependência preguiçosa e opcional, injeção por construtor, campo e método, e detecção de ciclo com a cadeia inteira."
        ],
        [
          "`Arcane.Percurso`",
          "5",
          "O caminho inteiro de um arquivo, fase por fase, MEDIDO: lexer, parser, HIR, tipos, MIR, analises, SSA, passes e LIR, com o que cada fase produziu e quanto tempo levou. Responde 'onde o tempo vai' quando um arquivo demora a abrir no editor. Ele NAO executa o programa — executar e o que o programa faz, e um comando que mostra fases nao pode abrir soquete. Traz tambem as divergencias entre o caminho real e o desenho da referencia."
        ]
      ]
    }
  },
  {
    "h2": "Sem dependências"
  },
  {
    "p": "Toda a biblioteca usa apenas a biblioteca padrão do Python. Isso significa que um programa DataForge roda em qualquer máquina com Python 3.10+, sem `pip install` de nada."
  },
  {
    "p": "A contrapartida é o escopo: não há cliente de PostgreSQL nem parser de YAML na biblioteca. O que existe é o que dá para fazer bem sem arrastar o ecossistema inteiro junto — e, quando falta, [`adopt Python.<pacote>`](/docs/tecnicas/ponte) alcança qualquer biblioteca do Python."
  },
  {
    "h2": "Os dois frameworks web"
  },
  {
    "table": {
      "head": [
        "",
        "Kiln",
        "Vitrine"
      ],
      "rows": [
        [
          "Para",
          "sites e APIs",
          "painéis e aplicações de dados"
        ],
        [
          "Você escreve",
          "rotas que devolvem o que quiser",
          "um programa de cima para baixo"
        ],
        [
          "Sintaxe",
          "onze palavras contextuais",
          "nenhuma palavra nova"
        ],
        [
          "Documentação",
          "[/docs/kiln](/docs/kiln)",
          "[/docs/vitrine](/docs/vitrine)"
        ]
      ]
    }
  },
  {
    "p": "A Vitrine roda **sobre** o Kiln: HTTP, rotas, sessão e cabeçalhos de segurança vêm dele."
  },
  {
    "callout": {
      "tipo": "nota",
      "titulo": "Onde ver a assinatura de cada símbolo",
      "texto": "Os módulos sem link acima ainda não têm página própria. Para eles, `doc/BIBLIOTECA_PADRAO.md` no repositório traz todos os símbolos com assinatura, e `dataforge repl` responde `:doc Arcane.<Nome>`."
    }
  },
  {
    "h2": "Além dos módulos"
  },
  {
    "p": "Existem ainda **228 funções globais** disponíveis sem nenhum `adopt` — `len`, `sum`, `sorted`, `map`, `round`, `str`, e o resto. A lista completa está em [Funções embutidas](/docs/referencia/embutidas)."
  }
];

const headings = [{ id: 'importar', text: "Importar", level: 2 as const }, { id: 'os-71-modulos', text: "Os 71 módulos", level: 2 as const }, { id: 'sem-dependencias', text: "Sem dependências", level: 2 as const }, { id: 'os-dois-frameworks-web', text: "Os dois frameworks web", level: 2 as const }, { id: 'alem-dos-modulos', text: "Além dos módulos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Biblioteca Arcane"}
      description={"71 módulos e 1971 símbolos, sem uma única dependência externa."}
      href={"/docs/biblioteca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
