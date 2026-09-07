---
name: criar-linguagem
description: Cria uma linguagem de programação completa e funcional do zero — lexer, parser, AST, interpretador, analisador estático, biblioteca padrão, CLI, gerenciador de pacotes, framework web, realce de sintaxe no editor e site de documentação. A linguagem-mãe (a que implementa) pode ser Python, JavaScript, TypeScript, Go, Rust, C, C++, C# ou Java. Também serve para criar um banco de dados, um framework, um runtime ou uma DSL. Use quando o usuário pedir para criar/projetar/implementar uma linguagem, um dialeto, um interpretador, um compilador, uma DSL, um framework ou um banco de dados próprio. SEMPRE comece perguntando a finalidade — a resposta muda tudo o que vem depois.
---

# Criar uma linguagem de programação

Esta skill nasceu de construir o **DataForge** até o fim: 25 mil linhas de
runtime, 502 testes, framework web próprio, gerenciador de pacotes, extensão
de editor, imagem Docker e site com 200 páginas. O que está aqui é o que
funcionou e o que custou caro.

---

## Passo 0 — Pergunte a finalidade. Sempre.

**Não escreva uma linha antes da resposta.** Uma linguagem para ensinar
crianças e uma para processar telemetria em tempo real não compartilham
quase nada. Pergunte, em uma única rodada:

```
Antes de começar, preciso de cinco respostas:

1. FINALIDADE — para que serve essa linguagem?
   (ensino · dados/análise · web/backend · scripts/automação · jogos ·
    configuração · DSL de um domínio · pesquisa/experimento · uso geral)

2. QUEM ESCREVE — quem vai programar nela?
   (iniciantes · quem já programa em outra linguagem · especialistas
    de um domínio que não são programadores · só você)

3. LINGUAGEM-MÃE — em que ela será implementada?
   (Python: mais rápido de construir, ótimo para árvore de sintaxe ·
    TypeScript/JS: roda no navegador sem esforço ·
    Go/Rust: desempenho e binário único ·
    C/C++: máximo controle, mais trabalho ·
    C#/Java: ecossistema corporativo)

4. IDENTIDADE — o que ela toma emprestado e o que faz diferente?
   Cite 1-3 linguagens que você admira, e o que te incomoda nelas.

5. ALCANCE — até onde vamos?
   (a) núcleo que roda: lexer, parser, interpretador, CLI
   (b) + biblioteca padrão, testes, analisador estático
   (c) + gerenciador de pacotes, framework web, editor, site
```

Se a pessoa responder só a primeira, siga com defaults sensatos e **diga
quais escolheu**. Não trave o trabalho esperando as cinco.

### Como a finalidade muda o projeto

| Finalidade | O que priorizar | O que cortar |
|---|---|---|
| Ensino | mensagens de erro que ensinam, sintaxe legível, REPL | desempenho, concorrência, metaprogramação |
| Dados/análise | pipelines, tabelas, imutabilidade, notação de coleções | OOP profunda, gerência de memória |
| Web/backend | rotas como sintaxe, async, JSON nativo, HTTP na stdlib | tipos dependentes, macros |
| Scripts | interpolação, arquivos, processos, `argv` fácil | sistema de tipos elaborado |
| Jogos | vetores, matemática, laços rápidos, estado mutável | imutabilidade estrita |
| Configuração | só dados, sem loops nem I/O — **termina sempre** | tudo que possa não terminar |
| DSL de domínio | vocabulário do domínio, poucas construções | generalidade |

---

## A arquitetura que funciona

```
texto → tokenize() → parse() → [check()] → executar()
        lexer        parser     analisador   interpretador
```

Cinco arquivos, nesta ordem de construção. **Cada um roda antes do
próximo existir.**

| Arquivo | Faz | Tamanho típico |
|---|---|---|
| `tokens` | o enum de tipos e o mapa de palavras reservadas | 200-300 linhas |
| `lexer` | texto → tokens; indentação, strings, comentários | 400-600 |
| `ast` | os nós, como estruturas de dados simples | 500-700 |
| `parser` | tokens → árvore, recursivo descendente | 1500-2500 |
| `interpreter` | percorre a árvore e executa | 2000-3000 |
| `checker` | erros antes de rodar: nomes, aridade, tipos | 800-1200 |

### Por que interpretador de árvore, e não bytecode

Um interpretador de árvore é **10× mais rápido de escrever** e 10× mais
fácil de depurar. Ninguém reclama de desempenho numa linguagem que ainda
não tem usuários. Bytecode é a versão 2.0 — e só se alguém medir e
reclamar.

### Recursivo descendente, e não gerador de parser

Um gerador (yacc, ANTLR) economiza tempo no começo e cobra depois: as
mensagens de erro ficam genéricas, e mensagem de erro é metade do valor
de uma linguagem. Escreva à mão. Uma função por construção sintática.

---

## Ordem de construção

Cada etapa termina com **algo que roda**. Nunca construa duas camadas sem
executar nada entre elas.

```
1. "olá mundo"          out "oi"
2. variáveis e contas   x := 2 + 3
3. condicionais         given/otherwise
4. laços                cycle, persist
5. funções              action/yield  ← a primeira metade
6. coleções             listas, dicionários, fatiamento
7. erros de verdade     linha, coluna, o que fazer  ← invista aqui
8. tipos compostos      classes ou records
9. módulos              import/export
10. biblioteca padrão   matemática, texto, arquivos, JSON
11. ferramentas         testes, formatador, linter
12. o resto             pacotes, web, editor, site
```

**O passo 7 é o que separa um brinquedo de uma linguagem.** Faça antes do 8.

---

## Vocabulário: escolha e registre

Se a linguagem tem palavras próprias, monte a tabela de tradução **antes**
de escrever o parser, e coloque-a no topo da documentação:

| Conceito | Sua linguagem | Python | JS |
|---|---|---|---|
| atribuir | `:=` | `=` | `=` |
| imprimir | `out` | `print` | `console.log` |
| condicional | `given/otherwise` | `if/else` | `if/else` |
| função | `action/yield` | `def/return` | `function/return` |

Três regras que evitam retrabalho:

1. **Uma palavra reservada é um nome roubado do usuário.** Antes de
   reservar `data`, `value` ou `state`, pergunte se vale.
2. **Palavras contextuais salvam nomes bons.** `get`, `route`, `render` e
   `server` só precisam ser especiais em um lugar. Reconheça-as pelo texto
   ali, e deixe-as livres no resto. É mais trabalho no parser e vale a pena.
3. **Toda palavra reservada precisa ser consumida pelo parser.** Uma
   palavra que ninguém lê só quebra código de usuário. Verifique:
   `grep -c "TokenType.NOVA" parser.*` tem que ser > 0.

---

## Mensagens de erro: onde a linguagem se prova

Compare:

```
✗  SyntaxError: invalid syntax
✓  erro[E0102]: 'no' é palavra reservada e não pode receber valor
     ┌─ conta.df:14:1
     │
   14│ no := 5
     │ ^^ aqui
     │
     = nota:  'no' é o literal falso
     = dica:  escolha outro nome, como 'nao' ou 'negado'
     = doc:   https://…/docs/variaveis
```

O molde: **código estável · o que aconteceu · onde (arquivo, linha,
coluna, trecho) · por que · o que fazer · onde ler mais**.

- Todo erro tem um **código estável** (`E0102`). Permite buscar, e permite
  um comando `explain E0102`.
- Quando houver um nome parecido no escopo, **sugira** (distância de
  edição resolve).
- O analisador estático é **otimista**: quando não consegue provar que algo
  está errado, cala. Um falso alarme ensina o usuário a ignorar avisos.

---

## Testes: a regra que segura tudo

**Ao corrigir um bug, escreva primeiro o teste que falha.** Sem exceção.

Quatro camadas:

| Camada | Cobre |
|---|---|
| unitários da implementação | lexer, parser, interpretador, casos de borda |
| regressão | todo bug já corrigido, um teste cada |
| exercícios executáveis | 100-200 programas na linguagem, cada um com `assert` |
| exemplos maiores | programas completos que precisam rodar |

Os exercícios são **documentação que não pode mentir**: se a sintaxe mudar,
eles quebram. Prefira citá-los na doc a inventar exemplos.

### Não afirme sem rodar

O interpretador está na sua frente. Antes de dizer que algo funciona,
execute. Isso vale especialmente ao escrever a documentação: cada trecho
de código na doc deveria ter rodado uma vez.

---

## Biblioteca padrão

Comece por seis módulos, nesta ordem: **texto, matemática, coleções,
arquivos, JSON, tempo**. Depois: HTTP, banco, processos, criptografia,
testes.

Duas decisões que valem:

- **Zero dependências externas no runtime.** Isso torna a instalação
  trivial, o Docker pequeno e — a surpresa — permite rodar a linguagem no
  navegador com WebAssembly (Pyodide, se a mãe for Python).
- **Funções que recebem "um campo" devem aceitar todas as formas de
  registro** que a linguagem tem (dicionário, record, instância). Foi um
  bug real: uma função de ordenação devolvia `None` para todos os records.

---

## O que vale construir depois do núcleo

Em ordem de retorno:

1. **Realce de sintaxe no editor** — a linguagem passa de "texto cinza" a
   linguagem de verdade. **Gere a gramática TextMate a partir do arquivo de
   tokens**, e escreva um teste que falha quando divergirem: uma gramática
   escrita à mão sempre fica para trás.
2. **Instalador de um comando** (`curl … | sh`) que também instala a
   extensão do editor.
3. **Gerenciador de pacotes.** Semver, lockfile com hash, registro
   estático (uma pasta com `index.json` — não precisa de servidor).
   Conflito de versão é **erro**, não aviso.
4. **Framework web com sintaxe própria**, se a finalidade for web. Rotas
   que se leem como rotas valem mais do que uma API com callbacks.
5. **Documentação gerada do código.** Toda contagem, assinatura e lista na
   documentação deve ser lida do fonte por um script. Documentação digitada
   à mão diverge — é questão de tempo.

---

## Adaptando para outros alvos

### Um banco de dados
Mesma espinha: parser de SQL (ou da sua linguagem de consulta) → plano →
executor. Comece por: armazenamento em arquivo append-only, índice B-tree,
`SELECT/INSERT/UPDATE/DELETE`, transações com WAL. Deixe otimizador de
consulta e MVCC para depois — e teste com falha simulada no meio da
escrita, que é onde bancos morrem.

### Um framework
Não invente conceito novo antes de resolver um problema real. Comece pelo
"olá mundo" mais curto possível e vá adicionando só o que cada exemplo
concreto exigir. Um framework que precisa de tutorial para o primeiro
programa já começou errado.

### Um runtime / VM
Instruções primeiro, otimização nunca no começo. Escreva o desmontador
junto com o montador — depurar bytecode sem ele é insuportável.

---

## Erros que custaram caro no DataForge

Todos reais. Evite-os.

1. **Reservar palavras boas globalmente.** `get`, `set` e `final` viraram
   reservadas e quebraram três arquivos do próprio repositório. A saída foi
   torná-las contextuais.
2. **Desugar reutilizando o nó da AST.** `v[f()] += 1` avaliava `f()` duas
   vezes. Descoberto porque uma amostragem ponderada deu 50/50 em vez de
   10/90 — silenciosamente. Se você reescreve uma construção em termos de
   outra, **avalie o alvo uma vez** e guarde o valor.
3. **Sinais de controle vazando.** `break` e `continue` implementados como
   exceção precisam de captura em todo lugar que a chama pode passar —
   senão o usuário vê o traceback da linguagem-mãe.
4. **Duas cópias do instalador.** Uma foi atualizada, a outra não, e o
   `curl | sh` em produção baixou uma versão que não existia. Gere as
   cópias, não as duplique — e teste em produção depois de publicar.
5. **Conexão de banco entre threads.** O servidor web atende um pedido por
   thread; SQLite recusa a conexão vinda de outra. Um teste na mesma thread
   **não pega isso** — só subir o servidor de verdade pegou.
6. **Formatador que piora o código.** O nosso não tratava menos unário e
   transformava `yield -1` em `yield - 1`. Resultado: ninguém rodava o
   formatador. Uma ferramenta em que não se confia é pior que nenhuma.
7. **Precedência em construções novas.** `>> distill a, v: a + v 0 / len(x)`
   dividia o zero inicial, não a soma. Documente a precedência da sintaxe
   nova com um exemplo do erro.

---

## Como conduzir o trabalho

- **Rode a suíte antes e depois de cada mudança.** Se algo já falhava
  antes, diga isso em vez de assumir a culpa.
- **Uma camada por vez, sempre executável.** Não escreva parser e
  interpretador juntos sem rodar nada.
- **Reproduza todo bug num programa mínimo antes de corrigir.** Depois,
  transforme esse programa no teste de regressão.
- **Não invente sintaxe na documentação.** Se não está nos testes que
  rodam, não existe.
- **Meça antes de otimizar.** Ninguém reclamou de desempenho ainda.

## Estado a reportar ao final de cada etapa

```
testes:      502 passando
exercícios:  200/200
análise:     0 erros em 302 arquivos
exemplos:    42/42
```

Números medidos, nunca estimados. Se algo está quebrado, diga qual e por quê.
