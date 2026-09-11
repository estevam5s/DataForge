// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/versoes.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Versões",
  description: "O que mudou, quando, e por quê.",
};

const blocos: Bloco[] = [
  {"p": "DataForge segue [versionamento semântico](https://semver.org): `MAIOR.MENOR.CORREÇÃO`. Enquanto a linguagem está em 1.x, mudança que quebra código existente sobe o número do meio — e vem com o caminho de migração."},
  {"callout": {"tipo": "nota", "titulo": "A versão pública é 1.0.0", "texto": "Os números 3.x e 4.x que aparecem no histórico são de desenvolvimento, antes do primeiro lançamento. Quem instala hoje instala a 1.0.0."}},
  {"h2": "1.0.0 — o lançamento"},
  {"p": "A primeira versão pública reúne tudo o que foi construído. O que ela traz:"},
  {"h3": "A linguagem"},
  {"list": ["**81 palavras reservadas**, lexer com INDENT/DEDENT, parser recursivo descendente, AST tipada, analisador estático e interpretador de árvore — todos próprios, em Python puro, **sem dependência de runtime**.", "**Orientação a objetos completa**: `blueprint`, `record` imutável, `trait`, herança, `private`/`protected` que valem de verdade, propriedades `get`/`set`, métodos estáticos, sobrecarga de operadores, `final` e `abstract` com contrato conferido na declaração.", "**Pattern matching estrutural** com `match`/`point`/`when`/`default`, sobre literais, sequências, vaults, records e membros de enum.", "**Generators preguiçosos** (`stream action` + `emit`), inclusive infinitos.", "**Pipelines** `>> sift / morph / distill`, compreensões, spread, desestruturação, interpolação `$\"{x}\"`, `??` e `?.`.", "**Decoradores** `@Nome` com pilha, argumentos nomeados e metadados legíveis por `Arcane.Meta`.", "**Generics** `<T>` aceitos pelo analisador — documentam a relação entre entrada e saída."]},
  {"h3": "Erros: 177 códigos"},
  {"p": "De 10 para 177, em 15 famílias. As classes e o catálogo nascem da **mesma tabela** — antes eram duas listas escritas à mão, e elas divergiam."},
  {"list": ["`handle` compara por **herança**: `handle RuntimeError` pega `DivisionByZeroError`.", "`handle KeyError:` agora **filtra**. Antes virava nome de variável e o bloco engolia qualquer erro em silêncio — com 177 tipos isso deixa de ser detalhe.", "Exceção do Python vira erro da linguagem. `[].min()` subia como `Internal Error` que nem `monitor` capturava.", "`e.campos`, `e.nota` e `e.dica` legíveis pelo programa.", "`dataforge erros` lista o catálogo; `explain` aceita o código **ou** o nome da classe."]},
  {"h3": "Crucible — o framework de testes"},
  {"p": "Dez palavras contextuais, 59 matchers, dublês, teste por propriedade com contraexemplo encolhido, benchmark com p95 e quatro formatos de relatório. Ver [Crucible](/docs/crucible)."},
  {"h3": "Forge — cinco bancos de dados"},
  {"p": "PostgreSQL, MySQL, MariaDB, MongoDB, Redis e SQLite — cada driver falando o protocolo por socket, **sem dependência**. Mais construtor de consultas que nunca põe valor no texto do SQL, e ORM com relações que custam duas consultas em vez de N+1. Ver [banco de dados](/docs/banco-de-dados)."},
  {"h3": "Kiln — o framework web"},
  {"p": "Dez palavras próprias, roteamento, middleware, sessão, templates com escape automático. Ver [Kiln](/docs/kiln)."},
  {"h3": "Análise de complexidade"},
  {"p": "`dataforge big-o` diz a classe de cada ação **e o porquê**, distinguindo divisão e conquista de recursão exponencial. Ver [Big-O](/docs/big-o)."},
  {"h3": "Ferramentas"},
  {"table": {"head": ["Comando", "Faz"], "rows": [["`run`, `repl`, `watch`", "executar"], ["`check`, `lint`, `fmt`", "analisar e formatar"], ["`crucible`, `test`", "testar"], ["`big-o`, `custo`, `profile`, `bench`", "medir"], ["`erros`, `explain`", "entender um erro"], ["`new`, `init`, `info`", "criar projeto"], ["`add`, `install`, `pack`, `publish`", "pacotes"], ["`doc`, `stats`, `fix`, `editor`", "o resto"]]}},
  {"h3": "Ecossistema"},
  {"list": ["**22 módulos** `Arcane.*` na biblioteca padrão, com 753 símbolos", "**20 pacotes** no registro, escritos em DataForge", "**Extensão do VS Code** com 103 snippets, Big-O no editor, custo de import e painel de bancos", "**200 exercícios** e 42 exemplos, todos rodando", "**891 testes** automatizados"]},
  {"h2": "O caminho até aqui"},
  {"p": "As versões de desenvolvimento, e o que cada uma acrescentou:"},
  {"table": {"head": ["", "O que entrou"], "rows": [["**4.2**", "Kiln (framework web), Arcane.Excel sem dependência, extensão do VS Code"], ["**4.1**", "OOP completa: visibilidade, propriedades, estáticos, operadores, abstratos, generics, decoradores"], ["**4.0**", "Records, enums, pattern matching, generators, interpolação, ternário, `??`, `?.`, analisador estático, gerenciador de pacotes, seis ferramentas de linha de comando"], ["**3.1**", "Módulos, `relay`, detecção de ciclos, stack traces"], ["**3.0**", "Blueprints, traits, herança, `monitor`/`handle`/`ensure`"]]}},
  {"h2": "Bugs corrigidos que valem registro"},
  {"p": "Os que mudaram o comportamento da linguagem, e não só uma mensagem:"},
  {"table": {"head": ["Sintoma", "Causa"], "rows": [["`private` do pai recusado ao próprio pai", "a checagem olhava o blueprint da **instância**, não o de quem declarou o membro"], ["`[].min()` incapturável", "exceção do Python subia crua, sem virar erro da linguagem"], ["`handle KeyError:` engolia tudo", "o nome virava variável em vez de filtro"], ["`// 200, application/json` virava divisão", "comentário começando com número era lido como operando"], ["`// 10 — o dobro` virava divisão", "o travessão não marcava prosa"], ["campos mutáveis compartilhados entre instâncias", "o literal do padrão era avaliado uma vez, na declaração"], ["closures num laço viam o último valor", "o escopo era reaproveitado mesmo quando o corpo o capturava"], ["`profile` somava 207%", "recursão contada duas vezes; agora mede tempo **próprio**"], ["`-v` nunca ligava o modo verboso", "só flags com `--` eram reconhecidas; `-v` caía entre os alvos"], ["erros de sintaxe diziam `<stdin>`", "o nome do arquivo não chegava ao lexer e ao parser"]]}},
  {"p": "Cada um tem teste de regressão. A suíte só cresce."},
  {"h2": "O que ainda não existe"},
  {"p": "Declarado, para não haver surpresa:"},
  {"list": ["**LSP e depurador** — a extensão do VS Code analisa e roda, mas não há autocompletar sensível a contexto nem ponto de parada.", "**Bytecode** — é interpretador de árvore. Rápido o suficiente para o que a linguagem faz, e não para computação numérica pesada.", "**Sincronização entre threads** — sem mutex; a coordenação é por `channel`.", "**Exaustividade no `match`** — ele não avisa se um membro de enum ficou de fora.", "**`<T extends Comparable>`** — generics documentam, não restringem.", "**WebSocket e HTTP/2 no Kiln** — ele roda sobre o `http.server` do Python."]},
  {"p": "O plano completo está no [roadmap](/docs/roadmap)."},
];

const headings = [{ id: '100-o-lancamento', text: "1.0.0 — o lançamento", level: 2 as const }, { id: 'a-linguagem', text: "A linguagem", level: 3 as const }, { id: 'erros-177-codigos', text: "Erros: 177 códigos", level: 3 as const }, { id: 'crucible-o-framework-de-testes', text: "Crucible — o framework de testes", level: 3 as const }, { id: 'forge-cinco-bancos-de-dados', text: "Forge — cinco bancos de dados", level: 3 as const }, { id: 'kiln-o-framework-web', text: "Kiln — o framework web", level: 3 as const }, { id: 'analise-de-complexidade', text: "Análise de complexidade", level: 3 as const }, { id: 'ferramentas', text: "Ferramentas", level: 3 as const }, { id: 'ecossistema', text: "Ecossistema", level: 3 as const }, { id: 'o-caminho-ate-aqui', text: "O caminho até aqui", level: 2 as const }, { id: 'bugs-corrigidos-que-valem-registro', text: "Bugs corrigidos que valem registro", level: 2 as const }, { id: 'o-que-ainda-nao-existe', text: "O que ainda não existe", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Versões"}
      description={"O que mudou, quando, e por quê."}
      href={"/docs/versoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
