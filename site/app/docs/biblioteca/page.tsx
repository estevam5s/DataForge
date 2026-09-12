import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Biblioteca Arcane",
  description: "Trinta e seis módulos e 1160 símbolos, sem uma única dependência externa.",
};

const blocos: Bloco[] = [
  {"h2": "Importar"},
  { code: `adopt Arcane.Math as Math                # o módulo inteiro
adopt Arcane.Math.{sqrt, factorial}       # só o que você usa
adopt {sqrt as raiz} from Arcane.Math     # com apelido

out Math.sqrt(16), sqrt(16), raiz(16)` },
  {"p": "Cada módulo tem um **nome curto** equivalente: `adopt Math as M` funciona igual a `adopt Arcane.Math as M`."},
  {"h2": "Os trinta e dois módulos"},
  {"table": {"head": ["Módulo", "Símbolos", "Para quê"], "rows": [["`Arcane.Color`", "66", "Cor de 24 bits no terminal, tabela, moldura, barra de progresso e árvore."], ["[`Arcane.Analytics`](/docs/biblioteca/analytics)", "65", "Análise de dados: estatística, regressão, clustering e gráficos ASCII."], ["`Kiln`", "64", "Framework web: rotas, middleware, templates, sessão e arquivos estáticos."], ["[`Arcane.Collections`](/docs/biblioteca/collections)", "63", "Estruturas de dados e algoritmos: pilha, fila, grafo, união-busca."], ["[`Arcane.Text`](/docs/biblioteca/text)", "58", "Manipulação de texto, formatação, tabelas e conversão de caixa."], ["[`Arcane.Functional`](/docs/biblioteca/functional)", "56", "Utilitários funcionais: composição, lentes, Maybe/Either, transdutores."], ["[`Arcane.Time`](/docs/biblioteca/time)", "54", "Datas, horas, durações e cronometragem."], ["[`Arcane.Math`](/docs/biblioteca/math)", "51", "Matemática, álgebra linear e estatística básica."], ["[`Arcane.Crypto`](/docs/biblioteca/crypto)", "48", "Hashes, HMAC, senhas, codificações, aleatoriedade segura e cifragem de arquivo (ChaCha20-Poly1305)."], ["[`Arcane.Async`](/docs/biblioteca/async)", "46", "Promessas, filas, agendamento e execução concorrente."], ["`Arcane.Iter`", "44", "Iteradores preguiçosos e composição de ações: janelas, combinatória, memoize."], ["`Arcane.Crucible`", "42", "Framework de testes: suítes, matchers, fixtures, dublês e benchmark."], ["[`Arcane.OS`](/docs/biblioteca/os)", "42", "Sistema operacional, ambiente, disco e processo atual."], ["[`Arcane.Database`](/docs/biblioteca/database)", "39", "Banco de dados SQLite: tabelas, consultas, migrações e importação."], ["[`Arcane.Test`](/docs/biblioteca/test)", "34", "Asserções e organização de suítes de teste."], ["[`Arcane.Regex`](/docs/biblioteca/regex)", "32", "Expressões regulares e validadores brasileiros (CPF, CNPJ, telefone)."], ["[`Arcane.Excel`](/docs/biblioteca/excel)", "29", "Planilhas .xlsx: ler, gravar, fórmulas e conversão para CSV e frame."], ["`Arcane.Forge`", "28", "Banco de dados: SQLite, Postgres, MySQL, Redis e MongoDB pela mesma interface."], ["[`Arcane.IO`](/docs/biblioteca/io)", "27", "Arquivos, diretórios, JSON, CSV e shell."], ["[`Arcane.Serialization`](/docs/biblioteca/serialization)", "26", "JSON, CSV, INI, TOML, XML e conversões entre eles."], ["`Arcane.Concurrent`", "25", "Threads, processos, canal bloqueante, grupo de tarefas e prazo."], ["[`Arcane.Cortex`](/docs/biblioteca/cortex)", "25", "Aprendizado de máquina: regressão, árvore, floresta, k-NN, Naive Bayes, k-médias e PCA."], ["`Arcane.Lago`", "18", "Data Lake: Parquet nativo, partições Hive, camadas bronze/prata/ouro e compactação."], ["[`Arcane.Http`](/docs/biblioteca/http)", "17", "Servidor HTTP: rotas, middleware, JSON, arquivos estáticos."], ["[`Arcane.Process`](/docs/biblioteca/process)", "15", "Execução de processos externos, com stdout, stderr e código de saída."], ["[`Arcane.Logging`](/docs/biblioteca/logging)", "14", "Registro estruturado de eventos, com níveis e destinos."], ["[`Arcane.Data`](/docs/biblioteca/data)", "13", "DataFrames, séries e transformações tabulares."], ["`Arcane.Qualidade`", "13", "Qualidade de dados: as seis dimensões, perfil, validação e limpeza."], ["[`Arcane.Meta`](/docs/biblioteca/meta)", "12", "Metadados de decorador: ler @Nome em tempo de execução."], ["`Arcane.Pipeline`", "11", "Orquestração de ETL/ELT: DAG, dependências, retry, incremental e relatório."], ["[`Arcane.Web`](/docs/biblioteca/web)", "11", "Cliente HTTP, URL encoding e JSON."], ["`Arcane.Archive`", "8", "Zip e tar: compactar, listar, conferir e extrair recusando Zip Slip e zip bomb."]]}},
  {"h2": "Sem dependências"},
  {"p": "Toda a biblioteca usa apenas a biblioteca padrão do Python. Isso significa que um programa DataForge roda em qualquer máquina com Python 3.10+, sem `pip install` de nada."},
  {"p": "A contrapartida é o escopo: não há cliente de PostgreSQL, nem parser de YAML, nem framework web completo. O que existe é o que dá para fazer bem sem arrastar o ecossistema inteiro junto."},
  {"h2": "Além dos módulos"},
  {"p": "Existem ainda **228 funções globais** disponíveis sem nenhum `adopt` — `len`, `sum`, `sorted`, `map`, `round`, `str`, e o resto. A lista completa está em [Funções embutidas](/docs/referencia/embutidas)."},
];

const headings = [{ id: 'importar', text: "Importar", level: 2 as const }, { id: 'os-trinta-e-dois-modulos', text: "Os trinta e dois módulos", level: 2 as const }, { id: 'sem-dependencias', text: "Sem dependências", level: 2 as const }, { id: 'alem-dos-modulos', text: "Além dos módulos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Biblioteca Arcane"}
      description={"Trinta e seis módulos e 1160 símbolos, sem uma única dependência externa."}
      href={"/docs/biblioteca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
