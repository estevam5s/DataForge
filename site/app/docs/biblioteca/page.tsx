import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

// Gerado por tools/gerar_pagina_biblioteca.py — não edite à mão.

export const metadata: Metadata = {
  title: "Biblioteca Arcane",
  description: "Trinta e oito módulos e 1280 símbolos, sem uma única dependência externa.",
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
    "h2": "Os trinta e oito módulos"
  },
  {
    "p": "São **1280 símbolos** ao todo. Esta tabela é gerada do próprio código: a contagem sai dos módulos e a descrição, do catálogo."
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
          "113",
          "O framework de dashboards e aplicações de dados: você escreve um programa de cima para baixo e ele vira uma página web, com componentes, layout, gráficos em SVG, estado por sessão e cache — servido pelo Kiln."
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
          "[`Kiln`](/docs/kiln)",
          "64",
          "Framework web: rotas, middleware, templates, sessão e arquivos estáticos."
        ],
        [
          "[`Arcane.Collections`](/docs/biblioteca/collections)",
          "63",
          "Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca."
        ],
        [
          "[`Arcane.Text`](/docs/biblioteca/text)",
          "58",
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
          "[`Arcane.Math`](/docs/biblioteca/math)",
          "51",
          "Matemática, álgebra linear e estatística básica."
        ],
        [
          "[`Arcane.Crypto`](/docs/biblioteca/crypto)",
          "48",
          "Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305)."
        ],
        [
          "[`Arcane.Async`](/docs/biblioteca/async)",
          "46",
          "Promessas, filas, agendamento e execução concorrente."
        ],
        [
          "`Arcane.Iter`",
          "44",
          "Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize."
        ],
        [
          "[`Arcane.Crucible`](/docs/tecnicas/testes)",
          "42",
          "Framework de testes: suítes, matchers, fixtures, dublês e benchmark."
        ],
        [
          "[`Arcane.OS`](/docs/biblioteca/os)",
          "42",
          "Sistema operacional, ambiente, disco e processo atual."
        ],
        [
          "[`Arcane.Database`](/docs/biblioteca/database)",
          "39",
          "Banco de dados SQLite: tabelas, consultas, migrações e importação."
        ],
        [
          "[`Arcane.Test`](/docs/biblioteca/test)",
          "34",
          "Asserções e organização de suítes de teste."
        ],
        [
          "[`Arcane.Regex`](/docs/biblioteca/regex)",
          "32",
          "Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone)."
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
          "[`Arcane.IO`](/docs/biblioteca/io)",
          "27",
          "Arquivos, diretórios, JSON, CSV e shell."
        ],
        [
          "[`Arcane.Serialization`](/docs/biblioteca/serialization)",
          "26",
          "JSON, CSV, INI, TOML, XML e conversões entre eles."
        ],
        [
          "[`Arcane.Concurrent`](/docs/tecnicas/concorrencia)",
          "25",
          "Threads, processos, canal bloqueante, grupo de tarefas e prazo."
        ],
        [
          "[`Arcane.Cortex`](/docs/biblioteca/cortex)",
          "25",
          "Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA."
        ],
        [
          "[`Arcane.Observar`](/docs/tecnicas/observar)",
          "19",
          "Observabilidade: métricas com percentil, tracing aninhado e linhagem de dados."
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
          "[`Arcane.Data`](/docs/biblioteca/data)",
          "13",
          "DataFrames, séries e transformações tabulares."
        ],
        [
          "[`Arcane.Qualidade`](/docs/tecnicas/qualidade)",
          "13",
          "Qualidade de dados: as seis dimensões, perfil, validação e limpeza."
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
          "[`Arcane.Archive`](/docs/tecnicas/arquivos)",
          "8",
          "Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb."
        ],
        [
          "[`Arcane.API`](/docs/tecnicas/api)",
          "7",
          "A API do Kiln vista de fora: OpenAPI, coleção do Insomnia e do Postman, curl e a tabela em Markdown — tudo derivado das rotas registradas."
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

const headings = [{ id: 'importar', text: "Importar", level: 2 as const }, { id: 'os-trinta-e-oito-modulos', text: "Os trinta e oito módulos", level: 2 as const }, { id: 'sem-dependencias', text: "Sem dependências", level: 2 as const }, { id: 'os-dois-frameworks-web', text: "Os dois frameworks web", level: 2 as const }, { id: 'alem-dos-modulos', text: "Além dos módulos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Biblioteca Arcane"}
      description={"Trinta e oito módulos e 1280 símbolos, sem uma única dependência externa."}
      href={"/docs/biblioteca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
