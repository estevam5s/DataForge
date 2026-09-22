// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/cli_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "CLI",
  description: "Os 65 comandos do dataforge, do catálogo que o próprio help lê.",
};

const blocos: Bloco[] = [
  {"p": "`dataforge` — ou `df`, o mesmo programa — tem **65 comandos** em sete grupos. Esta tabela sai do catálogo que o próprio `dataforge help` lê: ela não tem como ficar para trás."},
  { code: `dataforge help              # a visão geral
dataforge help check        # tudo sobre um comando
dataforge check --help      # o mesmo
dataforge completar zsh     # o Tab do terminal, gerado do mesmo catálogo`, lang: 'bash' },
  {"h2": "Projeto"},
  {"table": {"head": ["Comando", "O que faz", "Também"], "rows": [["[`init`](/docs/cli/init)", "Cria forge.toml e o esqueleto do projeto", ""], ["[`api`](/docs/tecnicas/api)", "exporta a API de um servidor Kiln", ""], ["[`converter`](/docs/cli/scripts)", "traduz Python para DataForge", "`convert`, `migrar`"], ["[`new`](/docs/cli/new)", "Cria um projeto a partir de um modelo", ""], ["[`info`](/docs/cli/new)", "Mostra o manifesto do projeto atual", ""]]}},
  {"h2": "Executar"},
  {"table": {"head": ["Comando", "O que faz", "Também"], "rows": [["[`run`](/docs/cli/run)", "Executa um programa", ""], ["[`eval`](/docs/cli/scripts)", "Executa uma linha de codigo direto", ""], ["[`watch`](/docs/cli/watch)", "Reexecuta a cada mudanca no arquivo", ""], ["[`repl`](/docs/cli/repl)", "Console interativo", ""]]}},
  {"h2": "Qualidade"},
  {"table": {"head": ["Comando", "O que faz", "Também"], "rows": [["[`check`](/docs/cli/check)", "Analise estatica: nomes, aridade, tipos e alcance", ""], ["[`test`](/docs/cli/test)", "Executa a suite de testes", ""], ["[`fmt`](/docs/cli/fmt)", "Formata o codigo", ""], ["[`lint`](/docs/cli/lint)", "Aponta problemas de estilo e higiene", ""], ["[`seguranca`](/docs/cli/seguranca)", "Procura segredo escrito no codigo e padrao arriscado", "`sec`, `audit`"], ["[`bench`](/docs/cli/bench)", "Mede o tempo de execucao, repetindo", ""]]}},
  {"h2": "Pacotes"},
  {"table": {"head": ["Comando", "O que faz", "Também"], "rows": [["[`add`](/docs/cli/pacotes)", "Instala uma dependencia e grava no forge.toml", ""], ["[`remove`](/docs/cli/pacotes)", "Desinstala e tira do forge.toml", "`rm`, `uninstall`"], ["[`install`](/docs/cli/pacotes)", "Instala o que o forge.lock fixa", "`i`, `sync`"], ["[`update`](/docs/cli/pacotes)", "Move as versoes e reescreve o forge.lock", "`up`"], ["[`list`](/docs/cli/pacotes)", "Mostra o que esta instalado", "`ls`"], ["[`tree`](/docs/cli/pacotes)", "Desenha a arvore de dependencias", ""], ["[`why`](/docs/cli/pacotes)", "Explica por que um pacote esta instalado", ""], ["[`outdated`](/docs/cli/pacotes)", "Lista dependencias com versao mais nova disponivel", ""], ["[`search`](/docs/cli/pacotes)", "Procura pacotes no registro", ""], ["[`pack`](/docs/cli/pacotes)", "Empacota este projeto para publicar", ""], ["[`publish`](/docs/cli/pacotes)", "Publica o pacote num registro", ""], ["[`versions`](/docs/cli/versoes)", "As versoes instaladas, a ativa e a que o projeto exige", "`versoes`"], ["[`use`](/docs/cli/versoes)", "Fixa a versao do DataForge deste projeto", "`switch`"], ["[`upgrade`](/docs/cli/versoes)", "Instala uma versao AO LADO da atual", ""], ["[`workspace`](/docs/cli/workspace)", "Todos os pacotes da arvore, e os conflitos de faixa", "`ws`"], ["[`login`](/docs/pacotes/publicar)", "Guarda o token de publicacao no registro da comunidade", ""], ["[`logout`](/docs/pacotes/publicar)", "Esquece o token guardado", ""], ["[`whoami`](/docs/pacotes/publicar)", "Diz de quem e o token guardado, e o que ele alcanca", ""]]}},
  {"h2": "Analise"},
  {"table": {"head": ["Comando", "O que faz", "Também"], "rows": [["[`stats`](/docs/cli/analise)", "O tamanho e a forma do codigo", ""], ["[`profile`](/docs/cli/profile)", "Onde o tempo foi gasto, acao por acao", ""], ["[`fix`](/docs/cli/profile)", "Formata e aponta o que precisa de voce", ""]]}},
  {"h2": "Ambiente"},
  {"table": {"head": ["Comando", "O que faz", "Também"], "rows": [["[`devops`](/docs/devops)", "Gera os artefatos que levam o projeto ao ar", "`ops`"], ["[`telegram`](/docs/telegram)", "Cria, roda e publica um bot de Telegram.", "`bot`"], ["[`vitrine`](/docs/vitrine)", "Sobe um painel feito com Arcane.Vitrine", ""], ["[`editor`](/docs/cli/editor)", "Instala a coloracao de sintaxe no VS Code", ""], ["[`debug`](/docs/cli/debug)", "Roda parando onde voce mandar", ""], ["[`dap`](/docs/cli/debug)", "Adaptador de depuracao para o editor", ""], ["[`lsp`](/docs/cli/debug)", "Servidor de linguagem para o editor", ""]]}},
  {"h2": "Diagnostico"},
  {"table": {"head": ["Comando", "O que faz", "Também"], "rows": [["[`explain`](/docs/cli/explain)", "Explica um codigo de erro", ""], ["[`crucible`](/docs/cli/crucible)", "Roda as suites do Crucible, o framework de testes", "`cr`"], ["[`big-o`](/docs/cli/analise)", "Calcula a complexidade de cada acao, sem rodar o codigo", "`bigo`, `complexidade`"], ["[`oop`](/docs/cli/analise)", "Metricas de orientacao a objeto e os cheiros de SOLID", "`metricas-oop`"], ["[`custo`](/docs/cli/analise)", "Mostra o que cada 'adopt' traz junto", "`cost`"], ["`gramatica`", "A gramatica da linguagem, com exemplos conferidos", "`grammar`"], ["[`palavras`](/docs/referencia/palavras-reservadas)", "Lista as palavras da linguagem, com um exemplo de cada", "`keywords`"], ["[`erros`](/docs/referencia/erros)", "Lista o catalogo de erros da linguagem", "`errors`"], ["[`doc`](/docs/cli/doc)", "Gera documentacao Markdown a partir dos comentarios", ""], ["[`deps`](/docs/cli/analise)", "Mostra o grafo de imports do codigo", ""], ["[`tokens`](/docs/cli/internos)", "Mostra o fluxo de tokens (lexer)", ""], ["[`ast`](/docs/cli/internos)", "Mostra a arvore sintatica (parser)", ""], ["[`abi`](/docs/cli/abi)", "Compara duas versoes e diz se a nova QUEBRA a anterior", ""], ["[`alvo`](/docs/cli/abi)", "Este programa roda no navegador? no WASI? numa funcao?", ""], ["[`percurso`](/docs/cli/internos)", "Onde o tempo vai: as fases em ordem, medidas", ""], ["[`ecossistema`](/docs/ecossistema/componentes)", "O inventario da implementacao, conferido contra o disco", ""], ["[`principios`](/docs/ecossistema/principios)", "Os dez principios de design, com a prova de cada um", ""], ["[`ir`](/docs/cli/internos)", "Mostra o caminho inteiro: HIR, MIR, LIR e as analises", ""], ["[`completar`](/docs/cli/completar)", "Gera o autocompletar do terminal", "`completion`"], ["[`clean`](/docs/cli/cache)", "Limpa caches e artefatos de build", ""], ["[`version`](/docs/cli/scripts)", "Mostra a versao", ""], ["[`help`](/docs/cli/scripts)", "Mostra esta ajuda, ou a de um comando", ""]]}},
  {"h2": "O ciclo de trabalho"},
  { code: `dataforge new api loja        # comecar de um modelo que passa nos testes
cd loja

dataforge check src/          # nomes, tipos, aridade — antes de rodar
dataforge fmt src/            # formatar
dataforge test                # testes, com cobertura
dataforge run                 # executar a entrada do forge.toml`, lang: 'bash' },
  {"h2": "Em integração contínua"},
  { code: `dataforge fmt . --check && dataforge check . --strict --formato=github && dataforge test --minimo=80`, lang: 'bash' },
  {"p": "Todo comando sai com código **diferente de zero** quando falha, e o `&&` para na primeira etapa que quebrar. `--formato=github` põe o erro do `check` na linha do PR — ver [GitHub Actions](/docs/devops/github-actions)."},
  {"h2": "Por tema"},
  {"cards": [{"href": "/docs/cli/referencia", "title": "Referência completa", "desc": "todo comando, com opções, exemplos e apelidos"}, {"href": "/docs/cli/new", "title": "new e info", "desc": "os modelos de projeto"}, {"href": "/docs/cli/debug", "title": "debug, dap e lsp", "desc": "parar, vigiar, e o editor"}, {"href": "/docs/cli/analise", "title": "Análise do código", "desc": "stats, oop, big-o, custo, deps"}, {"href": "/docs/cli/profile", "title": "profile e fix", "desc": "onde o tempo vai; o que se conserta sozinho"}, {"href": "/docs/cli/seguranca", "title": "seguranca", "desc": "segredos e padrões arriscados"}, {"href": "/docs/cli/crucible", "title": "crucible", "desc": "filtro, tag, ordem aleatória, relatórios"}, {"href": "/docs/cli/internos", "title": "tokens, ast, ir, percurso", "desc": "o que o compilador vê"}, {"href": "/docs/cli/abi", "title": "abi e alvo", "desc": "o que quebra; onde roda"}, {"href": "/docs/cli/completar", "title": "completar", "desc": "o Tab no bash, zsh e fish"}, {"href": "/docs/cli/scripts", "title": "Em scripts", "desc": "códigos de saída, cor, ambiente, eval"}]},
];

const headings = [{ id: 'projeto', text: "Projeto", level: 2 as const }, { id: 'executar', text: "Executar", level: 2 as const }, { id: 'qualidade', text: "Qualidade", level: 2 as const }, { id: 'pacotes', text: "Pacotes", level: 2 as const }, { id: 'analise', text: "Analise", level: 2 as const }, { id: 'ambiente', text: "Ambiente", level: 2 as const }, { id: 'diagnostico', text: "Diagnostico", level: 2 as const }, { id: 'o-ciclo-de-trabalho', text: "O ciclo de trabalho", level: 2 as const }, { id: 'em-integracao-continua', text: "Em integração contínua", level: 2 as const }, { id: 'por-tema', text: "Por tema", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"CLI"}
      description={"Os 65 comandos do dataforge, do catálogo que o próprio help lê."}
      href={"/docs/cli"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
