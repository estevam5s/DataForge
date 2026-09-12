// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/editor.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "A extensão do editor",
  description: "Cores, erros enquanto se digita, autocompletar, depurador com breakpoints, Big-O acima de cada ação, 49 comandos e o painel de bancos. O que cada coisa faz, e por quê.",
};

const blocos: Bloco[] = [
  {"p": "A extensão não reimplementa nada da linguagem: ela chama a CLI e desenha o resultado. É isso que garante que o sublinhado no editor, a saída do terminal e o que quebra o CI sejam **sempre a mesma coisa** — a alternativa seria um analisador no editor divergindo do analisador de verdade, e um editor que diz \"tudo certo\" sobre código que o CI recusa."},
  {"p": "O que ela acrescenta é o que só faz sentido dentro do editor: complexidade acima de cada ação, custo ao lado de cada import, breakpoints na margem, e um painel para os bancos do projeto."},
  {"h2": "Instalar"},
  { code: `dataforge editor`, lang: 'bash' },
  {"p": "Isso copia a extensão para todos os editores compatíveis que encontrar: **VS Code**, **VS Code Insiders**, **VSCodium**, **Cursor** e **Windsurf**. Reinicie o editor e abra um `.df`."},
  { code: `dataforge editor status     # onde está instalada
dataforge editor remove     # desinstala de todos`, lang: 'bash' },
  {"callout": {"tipo": "nota", "titulo": "Ela vem junto com a linguagem", "texto": "Não é preciso internet nem clonar o repositório: a extensão viaja dentro do pacote. `pip install dataforge-lang` já traz tudo — inclusive o cliente do servidor de linguagem, que vive fundo em `node_modules/` e por isso é fácil de deixar de fora no empacotamento. `tests/test_empacotamento.py` constrói o wheel e confere peça por peça, porque **um arquivo que falta ali não dá erro no repositório** — só para quem instalou."}},
  {"h2": "Erros enquanto você digita"},
  {"p": "O sublinhado vem do **mesmo** `dataforge check` que roda no CI, servido pelo servidor de linguagem — que reanalisa a cada tecla, e não só ao salvar."},
  {"table": {"head": ["O que ele acha", "Exemplo"], "rows": [["nome que não existe, com sugestão", "`p.clientte` → *did you mean 'cliente'?*"], ["aridade errada", "`criar(1, 2, 3)` numa ação de dois parâmetros"], ["tipo incompatível", "`x: Integer := \"texto\"`"], ["membro que o objeto não tem", "**inclusive vindo de outro arquivo**"], ["ciclo de import", "com a cadeia inteira: `a.df → b.df → c.df → a.df`"], ["código inalcançável", "depois de um `yield`"], ["membro de enum esquecido num `match`", "exaustividade"]]}},
  {"callout": {"tipo": "dica", "titulo": "O analisador é otimista de propósito", "texto": "Quando ele não consegue **provar** que algo está errado, fica calado. Um falso alarme ensina a ignorar mensagens, e aí os alarmes verdadeiros também são ignorados. Dentro de `monitor` e `retry`, erros são rebaixados a aviso — provocar falha ali é legítimo."}},
  {"h2": "Autocompletar, hover, ir-para-definição"},
  {"p": "O servidor de linguagem (`dataforge lsp`) é servido do mesmo `typechecker`. O que ele dá:"},
  {"table": {"head": ["Recurso", "O que faz"], "rows": [["autocompletar", "sensível a contexto, disparado por `.`, `:` e `@`"], ["hover", "a assinatura e o resumo, incluindo os símbolos da stdlib"], ["ir-para-definição", "`F12` — atravessa arquivos"], ["achar referências", "`Shift+F12`"], ["esquema do arquivo", "`Ctrl+Shift+O` — ações, blueprints, records"], ["ajuda de assinatura", "os parâmetros enquanto se escreve a chamada"], ["renomear", "`F2`, com verificação antes"], ["formatar", "o mesmo `dataforge fmt`"], ["correção rápida", "onde há uma sugestão a aplicar"], ["realçar ocorrências", "o nome sob o cursor, nas outras posições"]]}},
  {"p": "Os nomes do **próprio arquivo** vêm antes dos 1349 símbolos da stdlib — é o que se procura em nove de cada dez vezes."},
  {"callout": {"tipo": "nota", "titulo": "Um erro, uma vez", "texto": "Com o servidor ligado, ele assume os diagnósticos e a verificação-ao-salvar se desliga. Com os dois, o mesmo erro apareceria duas vezes no painel de problemas — e um deles ficaria desatualizado, o que é pior que não estar lá."}},
  {"h2": "Depurar: F5"},
  {"p": "Clique na margem para pôr um breakpoint e aperte **F5**. Não é preciso escrever `launch.json`."},
  {"table": {"head": ["No painel", "O que se vê"], "rows": [["**Variáveis**", "o escopo onde você parou, do mais próximo ao global — vault e cluster abrem em árvore"], ["**Pilha de chamadas**", "quem chamou quem; clicar leva ao lugar certo do arquivo certo"], ["**Console de depuração**", "qualquer expressão DataForge, avaliada **no quadro escolhido**"], ["**Entrar / Passar / Sair**", "`F11`, `F10`, `Shift+F11`"]]}},
  { code: `// Pare na linha do 'yield' e escreva no console:
total * 2 + len(nome)
cliente.saldo
[n * n cycle n in itens]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Uma parada em comentário é movida", "texto": "Uma parada numa linha que o interpretador não executa nunca dispararia, e o editor a mostraria acesa — o pior dos dois mundos. Ela é movida para a próxima linha executável, e o painel mostra onde ficou de verdade. A pergunta \"o que é linha executável\" é respondida pelo **mesmo** módulo que a cobertura usa: duas definições divergiriam, e a parada cairia onde a cobertura não conta."}},
  {"p": "As variáveis embutidas — 228 delas — **não** aparecem no painel. Elas vivem no escopo global, e despejá-las enterra as três variáveis que você parou para ver."},
  {"h3": "Depurar no terminal"},
  {"p": "O comando **Depurar no terminal** roda `dataforge debug`, que é passo a passo em texto. Serve onde interface gráfica nenhuma chega — por `ssh`, num container, num servidor."},
  { code: `dataforge debug conta.df --parar=42`, lang: 'bash' },
  {"p": "Dentro dele: `p` passo, `n` próximo, `f` sai da ação, `c` continua, `vars` lista o escopo, `pilha` mostra quem chamou quem, e qualquer expressão é avaliada no quadro onde você parou."},
  {"h2": "Big-O acima de cada ação"},
  {"p": "Uma lente sobre a declaração, com a complexidade estimada — e um aviso quando ela passa do limite que você configurou."},
  { code: `// O(n²) — dois laços aninhados sobre a mesma entrada
action duplicados(itens):
    saida := []
    cycle a in itens:
        cycle b in itens:
            given a is b:
                saida.append(a)
    yield saida`, lang: 'df' },
  {"p": "Clique na lente para ver **por quê**: qual laço, qual chamada, e o que domina. `dataforge.complexidade.avisarAcimaDe` controla o limite (padrão `O(n log n)`)."},
  {"h2": "Custo de cada import"},
  {"p": "Ao lado de cada `adopt`, quantos nomes ele traz ao escopo. O módulo inteiro traz tudo que ele tem; a forma seletiva traz o que você nomeou."},
  { code: `adopt Arcane.Math as Math          // o módulo inteiro
adopt Arcane.Math.{sqrt, floor}    // dois nomes`, lang: 'df' },
  {"h2": "Os 49 comandos"},
  {"p": "Tudo na paleta (`Ctrl+Shift+P`) sob **DataForge**, e na árvore **Ferramentas** da barra lateral."},
  {"h3": "Rodar e medir"},
  {"table": {"head": ["Comando", "O que faz", "Atalho"], "rows": [["Rodar arquivo", "no terminal", "`Ctrl+F5`"], ["Rodar e medir o tempo", "com cronômetro", "`Ctrl+Shift+F5`"], ["Rodar com `--debug`", "tokens, AST e traceback", "—"], ["Medir várias execuções", "média, mediana e p95 — uma execução só mede o ruído", "—"], ["Medir o desempenho", "a carga de referência", "—"], ["Perfilar", "tempo **próprio** por ação (o acumulado somaria mais de 100%)", "—"], ["Observar e reexecutar ao salvar", "para quem itera", "—"], ["Abrir o REPL", "com `:type`, `:ast`, `:load`", "—"], ["Avaliar expressão", "sem criar arquivo", "—"]]}},
  {"h3": "Qualidade"},
  {"table": {"head": ["Comando", "O que faz", "Atalho"], "rows": [["Verificar erros", "o `check` neste arquivo", "—"], ["Lint", "estilo e higiene", "—"], ["Formatar", "o `fmt`", "—"], ["Corrigir o que dá", "formata e aponta o que exige julgamento", "—"], ["Rodar os testes", "o Crucible", "`Ctrl+Alt+T`"], ["Cobertura", "quais linhas os testes rodaram", "—"], ["Cobertura: exigir um mínimo", "o que reprova no CI", "—"]]}},
  {"h3": "Entender"},
  {"table": {"head": ["Comando", "O que faz", "Atalho"], "rows": [["Analisar complexidade", "a estimativa, com o caminho", "`Ctrl+Alt+O`"], ["Big-O: a tabela de referência", "a escala, com números reais", "—"], ["Por que isto é assim?", "a decisão de projeto atrás do que está sob o cursor", "—"], ["Ver os tokens", "a saída do lexer", "—"], ["Ver a árvore sintática", "a AST", "—"], ["Inventário do projeto", "ações, blueprints, o arquivo e a ação mais longos", "—"], ["Explicar um código de erro", "`DF0601` em texto inteiro", "—"], ["Todos os códigos de erro", "o catálogo", "—"]]}},
  {"h3": "Projeto e pacotes"},
  {"table": {"head": ["Comando", "O que faz"], "rows": [["Novo projeto…", "os 9 modelos; o projeto criado passa nos próprios testes"], ["Ver o `forge.toml`", "o manifesto"], ["Instalar as dependências", "resolve o manifesto inteiro"], ["Acrescentar um pacote…", "com semver e lockfile"], ["Procurar no registro…", "por termo"], ["Pacotes instalados", "o que está lá"], ["Pacotes desatualizados", "o que subiu de versão"], ["Árvore de dependências", "quem pediu o quê"], ["Gerar a documentação", "Markdown a partir dos comentários"], ["Limpar caches e artefatos", "—"]]}},
  {"h3": "Vitrine e DevOps"},
  {"table": {"head": ["Comando", "O que faz"], "rows": [["Vitrine: subir recarregando ao salvar", "o `dev`, com hot reload"], ["Vitrine: por que não sobe?", "o `doctor` — a resposta é quase sempre `--host=0.0.0.0`"], ["DevOps: gerar artefatos…", "Dockerfile, compose, CI, k8s, Helm, Terraform, nginx, SBOM"], ["DevOps: o que falta para subir?", "o `doctor`, que funciona **mesmo num projeto que não compila**"]]}},
  {"h2": "O painel de bancos de dados"},
  {"p": "Na barra lateral, a árvore **Bancos de dados** lista as conexões do projeto. Cada uma pode ser testada, atualizada, removida — e **inserida como código** no editor, o que evita escrever a string de conexão à mão."},
  {"p": "Ela lê o mesmo lugar de onde o `Arcane.Forge` lê: não há uma segunda configuração para manter em sincronia."},
  {"h3": "Os snippets"},
  {"p": "Vinte e três atalhos, para as construções em que digitar o esqueleto custa mais que pensar nele:"},
  {"table": {"head": ["Digite", "Vira"], "rows": [["`action`", "uma ação com corpo"], ["`blueprint`", "uma classe com método"], ["`record`", "um record com campos"], ["`match`", "`match` com um `point` e o `default`"], ["`pipe`", "um pipeline `sift`/`morph`"], ["`server`", "uma aplicação Kiln completa, com `ignite`"], ["`crud`", "as cinco rotas RESTful de um recurso"], ["`routeparam`", "rota com parâmetro e o 404"], ["`xlsx`", "gravar uma planilha"], ["`istr`", "uma string interpolada"]]}},
  {"h2": "Cores, ícones e indentação"},
  {"p": "A gramática de cores é **gerada** de `tokens.py` — as 81 palavras reservadas, os operadores, a interpolação `$\"…{…}\"`, e a diferença entre `//` (comentário) e `~/` (divisão inteira)."},
  {"callout": {"tipo": "nota", "titulo": "Por que gerada", "texto": "A versão anterior era escrita à mão, e por isso não conhecia `record` nem `enum` — palavras que existiam na linguagem e apareciam sem cor. Hoje o gerador **recusa rodar** se uma palavra de `KEYWORDS` não estiver em nenhum grupo de cor, e um teste falha se o arquivo versionado divergir do que o gerador produz."}},
  {"p": "Junto vêm o tema de ícone de arquivo (o `.df` com a marca), 4 espaços de indentação forçados (`insertSpaces`, `tabSize: 4`, `detectIndentation: false` — tab é erro de sintaxe na linguagem), dobra de blocos, e os snippets das construções mais longas."},
  {"h2": "Configuração"},
  {"table": {"head": ["Chave", "Padrão", "O que faz"], "rows": [["`dataforge.caminho`", "*(vazio)*", "o executável, quando ele não está no `PATH`"], ["`dataforge.verificar`", "`true`", "sublinha erros e avisos"], ["`dataforge.servidor.ativo`", "`true`", "o servidor de linguagem"], ["`dataforge.servidor.log`", "*(vazio)*", "um arquivo onde ele grava o que acontece"], ["`dataforge.complexidade.mostrar`", "`true`", "a lente de Big-O"], ["`dataforge.complexidade.avisarAcimaDe`", "`O(n log n)`", "de onde vem o aviso"], ["`dataforge.custoDeImport`", "`true`", "o custo ao lado do `adopt`"], ["`dataforge.formatarAoSalvar`", "`false`", "roda o `fmt` ao salvar"]]}},
  {"callout": {"tipo": "dica", "titulo": "Três instalações, e a velha ganha", "texto": "O DataForge pode estar em três lugares: um `.venv`, o `~/.dataforge` do instalador, e o Python do sistema. Uma cópia antiga produz erros que **não existem** no seu código — foi assim que um `LexError: Unexpected character: '$'` apareceu num arquivo que usava interpolação normalmente. Se o editor discordar do terminal, `dataforge.caminho` resolve."}},
  {"h2": "Tarefas e o matcher de problemas"},
  {"p": "A extensão registra o tipo de tarefa `dataforge` e um *problem matcher* de mesmo nome: a saída de `check`, `lint` e `test` vira item clicável no painel de problemas — inclusive quando você roda por uma tarefa própria."},
  { code: `{
  "version": "2.0.0",
  "tasks": [{
    "type": "dataforge",
    "comando": "check",
    "problemMatcher": ["$dataforge"],
    "group": { "kind": "build", "isDefault": true }
  }]
}`, lang: 'json' },
  {"h2": "Outros editores"},
  {"p": "A gramática é TextMate padrão, em `editor/vscode/syntaxes/dataforge.tmLanguage.json` — Sublime Text e compatíveis leem o mesmo arquivo, e para Vim, Emacs ou Zed ela serve de referência: a lista de palavras por grupo de cor está toda ali."},
  {"p": "O servidor de linguagem e o depurador são processos que falam protocolo padrão, e por isso servem qualquer editor:"},
  { code: `dataforge lsp     # Language Server Protocol, no stdio
dataforge dap     # Debug Adapter Protocol, no stdio`, lang: 'bash' },
  {"p": "É por isso que a máquina dos dois mora na linguagem, e não na extensão: escrevê-la em TypeScript a amarraria ao VS Code. A extensão só diz ao editor qual processo iniciar."},
  {"p": "Para pular a instalação da extensão ao instalar a linguagem, defina `DATAFORGE_SEM_EDITOR=1`."},
  {"h2": "Onde continuar"},
  {"cards": [{"href": "/docs/cli", "title": "A CLI", "desc": "Os comandos que a extensão chama, com todas as opções."}, {"href": "/docs/tecnicas/lsp", "title": "O servidor de linguagem", "desc": "Como o autocompletar e o hover são servidos do typechecker."}, {"href": "/docs/big-o", "title": "Complexidade", "desc": "O que a lente estima, e o que ela não consegue provar."}, {"href": "/docs/tecnicas/analise-estatica", "title": "Análise estática", "desc": "O que o check acha antes de rodar — e o que o faz calar."}]},
];

const headings = [{ id: 'instalar', text: "Instalar", level: 2 as const }, { id: 'erros-enquanto-voce-digita', text: "Erros enquanto você digita", level: 2 as const }, { id: 'autocompletar-hover-ir-para-definicao', text: "Autocompletar, hover, ir-para-definição", level: 2 as const }, { id: 'depurar-f5', text: "Depurar: F5", level: 2 as const }, { id: 'depurar-no-terminal', text: "Depurar no terminal", level: 3 as const }, { id: 'big-o-acima-de-cada-acao', text: "Big-O acima de cada ação", level: 2 as const }, { id: 'custo-de-cada-import', text: "Custo de cada import", level: 2 as const }, { id: 'os-49-comandos', text: "Os 49 comandos", level: 2 as const }, { id: 'rodar-e-medir', text: "Rodar e medir", level: 3 as const }, { id: 'qualidade', text: "Qualidade", level: 3 as const }, { id: 'entender', text: "Entender", level: 3 as const }, { id: 'projeto-e-pacotes', text: "Projeto e pacotes", level: 3 as const }, { id: 'vitrine-e-devops', text: "Vitrine e DevOps", level: 3 as const }, { id: 'o-painel-de-bancos-de-dados', text: "O painel de bancos de dados", level: 2 as const }, { id: 'os-snippets', text: "Os snippets", level: 3 as const }, { id: 'cores-icones-e-indentacao', text: "Cores, ícones e indentação", level: 2 as const }, { id: 'configuracao', text: "Configuração", level: 2 as const }, { id: 'tarefas-e-o-matcher-de-problemas', text: "Tarefas e o matcher de problemas", level: 2 as const }, { id: 'outros-editores', text: "Outros editores", level: 2 as const }, { id: 'onde-continuar', text: "Onde continuar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"A extensão do editor"}
      description={"Cores, erros enquanto se digita, autocompletar, depurador com breakpoints, Big-O acima de cada ação, 49 comandos e o painel de bancos. O que cada coisa faz, e por quê."}
      href={"/docs/editor"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
