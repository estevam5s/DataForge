import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sistema de tipos",
  description: "Os tipos internos, as anotações e as regras de compatibilidade.",
};

const blocos: Bloco[] = [
  {"h2": "Tipos internos"},
  {"table": {"head": ["Nome", "Representação", "Literal"], "rows": [["`Integer`", "inteiro de precisão arbitrária", "`42`"], ["`Float`", "ponto flutuante 64 bits", "`3.14`"], ["`String`", "texto imutável", "`\"a\"`"], ["`Boolean`", "`yes` / `no`", "`yes`"], ["`Void`", "ausência de valor", "`void`"], ["`Cluster`", "lista mutável ordenada", "`[1, 2]`"], ["`Vault`", "dicionário chave→valor", "`{\"k\": 1}`"], ["`Action`", "ação (função)", "`action f(): …`"], ["`Stream`", "sequência preguiçosa", "`stream action g(): …`"], ["`Blueprint`", "classe", "`blueprint P: …`"], ["`Record`", "tipo de dado imutável", "`record R: …`"], ["`Enum`", "conjunto fechado", "`enum E: …`"], ["*nome do tipo*", "instância", "`spawn P()`, `R(1)`, `E.A`"]]}},
  {"p": "`typeof(x)` devolve exatamente esses nomes — os mesmos que valem numa anotação."},
  {"h2": "Compatibilidade"},
  {"p": "A checagem aceita um valor quando:"},
  {"list": ["o tipo é exatamente o declarado;", "o declarado é `Any` (a checagem é desligada);", "o declarado é `Number` e o valor é `Integer` ou `Float`;", "o declarado é `Float` e o valor é `Integer` — **alargamento**;", "o declarado é o nome de um blueprint na cadeia de herança do valor."]},
  {"callout": {"tipo": "nota", "texto": "O alargamento `Integer → Float` é a única flexibilização, e existe porque é matematicamente seguro. O contrário perderia informação."}},
  {"h2": "Onde a checagem acontece"},
  {"table": {"head": ["Local", "Quando"], "rows": [["variável anotada", "na atribuição"], ["parâmetro anotado", "na chamada, antes de executar o corpo"], ["retorno anotado", "no `yield`"], ["campo de record", "na construção"], ["tudo acima", "também no `dataforge check`, sem executar"]]}},
  {"h2": "Semântica de valores"},
  {"list": ["**Inteiros** têm precisão arbitrária — não estouram.", "**Textos** são imutáveis; os métodos devolvem cópias.", "**Clusters e vaults** são mutáveis e passados por referência.", "**Records** são imutáveis, com igualdade estrutural.", "`/` sempre devolve `Float`; `~/` devolve `Integer` para operandos inteiros.", "Divisão por zero dispara `RuntimeError_`.", "`+` com um operando texto converte o outro para texto.", "Índices negativos contam a partir do fim."]},
  {"h2": "Verdadeiro e falso"},
  {"p": "São falsos: `void`, `no`, `0`, `0.0`, `\"\"`, `[]` e `{}`. Todo o resto é verdadeiro."},
  {"h2": "O que ainda não existe"},
  {"p": "**Generics** — `Cluster<T>`, `Vault<K,V>` e ações genéricas estão no [roadmap](/roadmap). Hoje, o conteúdo de uma coleção se valida com código."},
];

const headings = [{ id: 'tipos-internos', text: "Tipos internos", level: 2 as const }, { id: 'compatibilidade', text: "Compatibilidade", level: 2 as const }, { id: 'onde-a-checagem-acontece', text: "Onde a checagem acontece", level: 2 as const }, { id: 'semantica-de-valores', text: "Semântica de valores", level: 2 as const }, { id: 'verdadeiro-e-falso', text: "Verdadeiro e falso", level: 2 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sistema de tipos"}
      description={"Os tipos internos, as anotações e as regras de compatibilidade."}
      href={"/referencia/tipos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
