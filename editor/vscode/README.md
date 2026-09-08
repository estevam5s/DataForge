# DataForge para VS Code

Suporte completo à linguagem [DataForge](https://dataforge-lang.vercel.app).

## O que ela faz

**Roda o arquivo.** `Ctrl+F5` abre o terminal e executa. `Ctrl+Shift+F5`
executa capturando tudo e cronometrando — e há um comando para repetir N
vezes e ver média, mediana e p95, porque a média sozinha esconde a pausa
do coletor de lixo.

**Sublinha os erros.** O mesmo analisador que roda no CI, chamado ao
salvar. O código do erro (`DF0601`) vira link para a explicação.

**Mostra o Big-O acima de cada ação.** Não é enfeite: `O(n²)` aparece
enquanto se escreve, com o motivo no hover — "dois laços aninhados, linhas
4 e 7" — e a sugestão do que fazer.

**Mostra quanto cada `adopt` custa**, ao lado da linha. `Arcane.Math` traz
52 símbolos; um programa que só queria `sqrt` paga por todos.

**Cria projetos.** Oito modelos, vindos da própria CLI.

**Lista seus bancos.** Painel lateral com as conexões, testadas pelo
`Forge` — o mesmo módulo que o seu código usa. A senha vai para o cofre do
sistema, não para o `settings.json`.

**103 snippets**, cobrindo a linguagem inteira: objetos com visibilidade e
operadores, pattern matching, Kiln, Crucible e Forge.

## Como ela funciona

A extensão **não reimplementa nada da linguagem**. Toda análise — erros,
complexidade, custo — é feita pela CLI, e a extensão só desenha o
resultado.

Não é preguiça: é a única forma de o editor, o terminal e o CI nunca
discordarem. Uma segunda implementação em TypeScript divergiria da
primeira no dia em que a linguagem ganhasse um nó novo, e você veria um
erro no editor que o `dataforge check` não confirma — ou pior, o
contrário. Há um teste que proíbe um lexer ou parser aparecer aqui.

## Instalação

A extensão precisa do `dataforge` no PATH:

```bash
curl -fsSL https://dataforge-lang.vercel.app/instalar.sh | sh
```

Se ele estiver em outro lugar, aponte em `dataforge.caminho`.

## Atalhos

| | |
|---|---|
| `Ctrl+F5` | rodar |
| `Ctrl+Shift+F5` | rodar e medir |
| `Ctrl+Alt+O` | analisar complexidade |
| `Ctrl+Alt+T` | rodar os testes |

## Configuração

| opção | padrão | |
|---|---|---|
| `dataforge.caminho` | `""` | onde está o executável |
| `dataforge.verificar` | `true` | sublinhar erros |
| `dataforge.complexidade.mostrar` | `true` | Big-O acima das ações |
| `dataforge.complexidade.avisarAcimaDe` | `O(n log n)` | o que marcar |
| `dataforge.custoDeImport` | `true` | tamanho ao lado do `adopt` |

MIT.
