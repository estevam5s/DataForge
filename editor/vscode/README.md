<div align="center">

<img src="https://dataforge-lang.vercel.app/marca-256.png" width="120" alt="DataForge" />

# DataForge para VS Code

**Suporte completo à linguagem [DataForge](https://dataforge-lang.vercel.app)** —
servidor de linguagem, Big-O no editor, custo de import, cobertura de
testes, painéis Vitrine, geradores DevOps, 49 comandos e 123 snippets.

[Documentação](https://dataforge-lang.vercel.app/docs) ·
[Exercícios](https://dataforge-lang.vercel.app/docs/exercicios) ·
[Download](https://dataforge-lang.vercel.app/download)

</div>

---

## O princípio: ela não reimplementa a linguagem

Toda análise — erro, complexidade, custo, formatação, autocompletar — é
feita pela **CLI**, e a extensão só desenha o resultado.

Não é preguiça: é a única forma de o editor, o terminal e o CI nunca
discordarem. Uma segunda implementação em TypeScript divergiria da
primeira no dia em que a linguagem ganhasse um nó novo, e você veria um
erro no editor que o `dataforge check` não confirma — ou, pior, o
contrário. **Há um teste que proíbe um lexer ou um parser aparecer
aqui.**

---

## Enquanto você escreve

### Erro sublinhado, a cada tecla

O servidor de linguagem (`dataforge lsp`) analisa a cada mudança, e
guarda a última análise boa — então autocompletar e hover continuam
funcionando **no meio de um erro de sintaxe**, que é justamente quando
você mais precisa deles.

O código do erro (`DF0601`) vira link para a explicação, e há correção
rápida onde o analisador sabe o que fazer.

### Hover com exemplo que roda

Parar o mouse numa palavra reservada mostra o que ela faz **e três
linhas de código**. Dizer é metade — os 87 exemplos são executados por
um teste a cada mudança do repositório, porque um exemplo de
documentação que não compila ensina errado.

O mesmo vale para os 37 módulos e as 228 funções embutidas: hover traz a
assinatura e o que a função faz, lido do próprio código.

### Big-O acima de cada ação

`O(n²)` aparece enquanto se escreve, com o motivo no hover — *"dois
laços aninhados, linhas 4 e 7"* — e a sugestão do que fazer. Configure o
limiar em `dataforge.complexidade.avisarAcimaDe`.

### Quanto cada `adopt` custa

Ao lado da linha: `Arcane.Math` traz 52 símbolos, e um programa que só
queria `sqrt` paga por todos. Use `adopt Arcane.Math.{sqrt}` e veja o
número cair.

---

## Rodar e medir

| | |
|---|---|
| `Ctrl+F5` | roda no terminal |
| `Ctrl+Shift+F5` | roda capturando tudo, com cronômetro |
| | `--debug`: tokens, AST e traceback completo |
| | repetir N vezes: média, **mediana e p95** |

A mediana e o p95 estão lá porque a média sozinha esconde a pausa do
coletor de lixo — uma execução em vinte que demora dez vezes mais
desaparece na média e aparece no p95.

E há `Observar e reexecutar ao salvar`, para quem itera.

---

## Depurar: F5

Clique na margem e aperte **F5**. Não é preciso escrever `launch.json`.

| No painel | O que se vê |
|---|---|
| **Variáveis** | o escopo onde você parou, do mais próximo ao global — vault e cluster abrem em árvore |
| **Pilha de chamadas** | quem chamou quem; clicar leva ao lugar certo do arquivo certo |
| **Console de depuração** | qualquer expressão DataForge, avaliada **no quadro onde você parou** |
| `F11` · `F10` · `Shift+F11` | entrar · passar por cima · sair da ação |

```dataforge
// Pare na linha do 'yield' e escreva no console:
total * 2 + len(nome)
[n * n cycle n in itens]
```

Três coisas que ele faz e que não são óbvias:

- **Uma parada em comentário é movida** para a próxima linha
  executável, e o painel mostra onde ficou. Uma parada que nunca
  dispara, mostrada acesa, é o pior dos dois mundos. A pergunta "o que
  é linha executável" é respondida pelo mesmo módulo que a cobertura
  usa — duas definições divergiriam.
- **As 228 embutidas não aparecem** no painel de variáveis. Elas vivem
  no escopo global, e despejá-las enterra as três variáveis que você
  parou para ver.
- **Avaliar usa o quadro escolhido**, e não o global: é justamente para
  as variáveis locais que a diferença importa.

O adaptador é `dataforge dap`, um processo que fala **Debug Adapter
Protocol** no stdio — o mesmo protocolo que qualquer editor moderno
fala. A extensão só diz ao VS Code qual processo iniciar; a máquina de
depuração mora na linguagem, e por isso serve Neovim, Helix e Emacs
também.

Para depurar onde não há interface gráfica — por `ssh`, num container —
o comando **Depurar no terminal** roda `dataforge debug`, que é passo a
passo em texto.

---

## Os 49 comandos

Abra a paleta (`Ctrl+Shift+P`) e digite **DataForge**.

**Executar** — rodar · rodar e medir · rodar com `--debug` · medir N
execuções · depurar · observar e reexecutar · avaliar expressão ·
perfilar (tempo por ação) · medir desempenho (bench)

**Qualidade** — verificar erros · formatar · lint · corrigir o que dá ·
rodar os testes · rodar o Crucible · **cobertura** (quais linhas os
testes rodaram) · **cobertura mínima** (reprova abaixo de N%) · analisar
complexidade · tabela de referência do Big-O · *por que isto é assim?*

**Vitrine** — subir o painel recarregando ao salvar · *por que não
sobe?* (o diagnóstico, da causa mais provável para a menos)

**DevOps** — **gerar artefatos** (Dockerfile, compose, CI, Kubernetes,
Helm, Terraform, nginx, Prometheus, SBOM, segredos) · *o que falta para
subir?*

**Projeto** — novo projeto (oito modelos, vindos da própria CLI) ·
inventário · gerar documentação · ver o `forge.toml` · limpar caches

**Pacotes** — instalar dependências · acrescentar · procurar no registro
· instalados · desatualizados · árvore de dependências

**Bancos** — nova conexão · testar · atualizar · remover · inserir o
código no editor

**Entender** — explicar um código de erro · todos os 177 códigos · ver
os tokens · ver a árvore sintática · abrir o REPL · abrir a documentação
· reiniciar o servidor de linguagem

---

## O painel lateral

Um ícone do DataForge na barra de atividades, com duas árvores:

**Conexões** — seus bancos, testados pelo `Arcane.Forge`, o mesmo módulo
que o seu código usa. **A senha vai para o cofre do sistema**, nunca
para o `settings.json` — que costuma acabar num repositório.

**Ferramentas** — oito grupos, a um clique: Executar, Qualidade,
Vitrine, DevOps, Complexidade, Pacotes, Inspecionar e Projeto.

A árvore é **estática** de propósito: nada nela consulta o disco nem
roda processo ao abrir. Um painel que trava enquanto o editor carrega é
pior que um painel ausente. E o que precisa de um `.df` aberto fica
**apagado** em vez de sumir — um item que desaparece parece defeito, um
item apagado ensina quando ele serve.

---

## Atalhos

| | |
|---|---|
| `Ctrl+F5` | rodar |
| `Ctrl+Shift+F5` | rodar e medir |
| `Ctrl+Alt+O` | analisar complexidade |
| `Ctrl+Alt+T` | rodar os testes |

No macOS, `Cmd` no lugar de `Ctrl`.

---

## 123 snippets

Cobrem a linguagem inteira: `action`, `blueprint` com visibilidade e
sobrecarga de operadores, `record`, `enum`, `trait`, `match`/`point`,
pipelines, `stream action`, rotas do Kiln, suítes do Crucible e modelos
do Forge.

Os que economizam mais tempo:

| Digite | Sai |
|---|---|
| `vitrine` | um painel completo — título, filtro, métricas, gráfico |
| `vcache` | `mark @V.cache` — obrigatório num painel, que roda inteiro a cada clique |
| `vform` | um formulário, cujos valores só chegam no envio |
| `vteste` | testar uma página sem navegador |
| `kupload` | receber arquivo, com as três recusas de segurança |
| `ksse` | uma resposta que não termina (o servidor empurra) |
| `kws` | WebSocket com sala |
| `btrans` | a operação inteira, ou nenhuma |
| `bupsert` | insere ou atualiza, sem duplicar |
| `bincr` | a baixa de estoque **no banco**, não na memória |
| `bagg` | relatório agrupado, sem escrever SQL |
| `bpag` | listagem paginada, com total e número de páginas |
| `bbusca` | busca textual FTS5 — `LIKE %x%` varre a tabela inteira |
| `bmig` | uma migração, com ida e volta |
| `snapshot` | instantâneo, para o que é grande demais para escrever à mão |
| `cbanco` | um teste que grava e não é visto pelo seguinte |

Digite o começo e `Tab`.

**Há um teste que compila os 123.** Um snippet que não compila é pior
que um snippet ausente: ele ensina sintaxe errada, e quem o usa
acredita.

---

## Configuração

| opção | padrão | |
|---|---|---|
| `dataforge.caminho` | `""` | onde está o executável, se não estiver no PATH |
| `dataforge.verificar` | `true` | sublinhar erros |
| `dataforge.servidor.ativo` | `true` | o servidor de linguagem |
| `dataforge.servidor.log` | `""` | `verbose` para depurar o próprio LSP |
| `dataforge.complexidade.mostrar` | `true` | Big-O acima das ações |
| `dataforge.complexidade.avisarAcimaDe` | `O(n log n)` | a partir de onde marcar |
| `dataforge.custoDeImport` | `true` | tamanho ao lado do `adopt` |
| `dataforge.formatarAoSalvar` | `false` | `dataforge fmt` ao salvar |

---

## Instalação

A extensão precisa do `dataforge` no PATH:

```bash
# macOS e Linux
curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh

# Windows
irm https://dataforge-lang.vercel.app/instalar.ps1 | iex

# ou, com Python 3.10+
pip install dataforge-lang
```

Há também um **instalador gráfico para Windows** e executáveis que não
precisam de Python, em
[dataforge-lang.vercel.app/download](https://dataforge-lang.vercel.app/download).

Se o executável estiver em outro lugar, aponte em `dataforge.caminho`.

> **Uma instalação antiga no PATH produz erros que não existem.** Se
> algo não fizer sentido, rode `dataforge --version` no terminal e
> confira que é a versão que você espera.

---

## Se algo não funcionar

**"O projeto não foi criado"** — a mensagem agora traz o motivo real, e
o botão *Ver a saída completa* abre o que a CLI imprimiu.

**Sem autocompletar** — o painel de saída (canal `DataForge`) diz se o
servidor subiu. `DataForge: Reiniciar o servidor de linguagem` costuma
resolver.

**Sem Big-O** — ele só aparece em ações; um arquivo só de código de topo
não tem o que medir.

---

## O que ela não faz

- **Não formata enquanto você digita.** `dataforge.formatarAoSalvar`
  liga a formatação ao salvar, e ela é desligada por padrão: formatador
  que reorganiza no meio da frase atrapalha mais que ajuda.
- **Não renomeia através de arquivos.** O `rename` do servidor vale
  dentro de um arquivo; o `adopt` cruzando módulos ainda é manual.
- **Não tem refatorações automáticas** além das correções rápidas que o
  analisador sabe provar.
- **Não depura mais de uma thread por vez.** A linguagem tem `thread` e
  `parallel`, mas o depurador sombreia `execute` no interpretador
  inteiro: apresentar N threads sem poder pará-las uma a uma seria uma
  interface que promete o que não cumpre.
- **Não tem breakpoint condicional** nem watchpoint. Parar e avaliar no
  console cobre o caso; a condição ainda é um `given` com `out`.

---

MIT · [Código-fonte](https://github.com/estevam5s/DataForge) ·
[Reportar um problema](https://github.com/estevam5s/DataForge/issues)
