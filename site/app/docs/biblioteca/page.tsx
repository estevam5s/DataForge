import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Biblioteca Arcane",
  description: "Vinte módulos e 674 símbolos, sem uma única dependência externa.",
};

const blocos: Bloco[] = [
  {"h2": "Importar"},
  { code: `adopt Arcane.Math as Math                # o módulo inteiro
adopt Arcane.Math.{sqrt, factorial}       # só o que você usa
adopt {sqrt as raiz} from Arcane.Math     # com apelido

out Math.sqrt(16), sqrt(16), raiz(16)` },
  {"p": "Cada módulo tem um **nome curto** equivalente: `adopt Math as M` funciona igual a `adopt Arcane.Math as M`."},
  {"h2": "Os vinte módulos"},
  {"table": {"head": ["Módulo", "Símbolos", "Para quê"], "rows": [["[`Arcane.Analytics`](/docs/biblioteca/analytics)", "65", "Análise de dados: estatística, regressão, clustering e gráficos."], ["[`Arcane.Text`](/docs/biblioteca/text)", "58", "Manipulação de texto, tabelas, caixas e conversão de caixa."], ["[`Arcane.Functional`](/docs/biblioteca/functional)", "56", "Composição, lentes, Maybe/Either e transdutores."], ["[`Arcane.Time`](/docs/biblioteca/time)", "54", "Datas, horas, durações e cronometragem."], ["[`Arcane.Math`](/docs/biblioteca/math)", "51", "Matemática, álgebra linear e estatística."], ["[`Arcane.Async`](/docs/biblioteca/async)", "46", "Promessas, filas e agendamento."], ["[`Arcane.Database`](/docs/biblioteca/database)", "39", "SQLite: tabelas, consultas, transações e migrações."], ["[`Arcane.Crypto`](/docs/biblioteca/crypto)", "38", "Hashes, HMAC, senhas, codificações e aleatoriedade segura."], ["[`Arcane.OS`](/docs/biblioteca/os)", "38", "Sistema operacional, ambiente, disco e processo."], ["[`Arcane.Collections`](/docs/biblioteca/collections)", "35", "Pilha, fila, heap, grafo, união-busca e algoritmos."], ["[`Arcane.Test`](/docs/biblioteca/test)", "34", "Asserções e organização de suítes."], ["[`Arcane.Regex`](/docs/biblioteca/regex)", "32", "Expressões regulares e validadores brasileiros."], ["[`Arcane.IO`](/docs/biblioteca/io)", "27", "Arquivos, diretórios, JSON e CSV."], ["[`Arcane.Serialization`](/docs/biblioteca/serialization)", "26", "JSON, JSONL, CSV, INI, TOML e XML."], ["[`Arcane.Http`](/docs/biblioteca/http)", "17", "Servidor HTTP com rotas, middleware e JSON."], ["[`Arcane.Process`](/docs/biblioteca/process)", "15", "Execução de processos externos."], ["[`Arcane.Logging`](/docs/biblioteca/logging)", "14", "Registro estruturado com níveis e destinos."], ["[`Arcane.Data`](/docs/biblioteca/data)", "13", "DataFrames, séries e transformações."], ["[`Arcane.Web`](/docs/biblioteca/web)", "11", "Cliente HTTP, URL encoding e JSON."], ["[`Arcane.Cortex`](/docs/biblioteca/cortex)", "5", "Blocos de rede neural, visão e NLP."]]}},
  {"h2": "Sem dependências"},
  {"p": "Toda a biblioteca usa apenas a biblioteca padrão do Python. Isso significa que um programa DataForge roda em qualquer máquina com Python 3.10+, sem `pip install` de nada."},
  {"p": "A contrapartida é o escopo: não há cliente de PostgreSQL, nem parser de YAML, nem framework web completo. O que existe é o que dá para fazer bem sem arrastar o ecossistema inteiro junto."},
  {"h2": "Além dos módulos"},
  {"p": "Existem ainda **225 funções globais** disponíveis sem nenhum `adopt` — `len`, `sum`, `sorted`, `map`, `round`, `str`, e o resto. A lista completa está em [Funções embutidas](/docs/referencia/embutidas)."},
];

const headings = [{ id: 'importar', text: "Importar", level: 2 as const }, { id: 'os-vinte-modulos', text: "Os vinte módulos", level: 2 as const }, { id: 'sem-dependencias', text: "Sem dependências", level: 2 as const }, { id: 'alem-dos-modulos', text: "Além dos módulos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Biblioteca Arcane"}
      description={"Vinte módulos e 674 símbolos, sem uma única dependência externa."}
      href={"/docs/biblioteca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
