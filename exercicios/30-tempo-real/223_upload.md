# Exercicio 223 — Receber arquivo

## Enunciado

Receba uma planilha por `multipart/form-data`, leia o conteúdo e grave
em disco com segurança.

## O problema

O corpo de um pedido era interpretado como JSON ou como formulário
simples. Um `<input type="file">` chegava como **texto ilegível**, e
com isso toda tela que recebe planilha, foto ou documento ficava de
fora do framework.

## Conceitos

```dataforge
adopt Kiln

route POST "/importar":
    arquivo := Kiln.upload(req, "planilha")
    given arquivo is void:
        respond 400 json {"erro": "nenhum arquivo"}

    linhas := arquivo["texto"].lines()
    gravado := Kiln.salvar_upload(arquivo, "envios",
                                  tipos := [".csv", ".xlsx"],
                                  limite := 5242880)
    respond json {"linhas": len(linhas), "em": gravado["caminho"]}
```

| Chamada | Faz |
|---|---|
| `Kiln.upload(req, campo)` | um arquivo, ou `void` |
| `Kiln.uploads(req)` | todos, por nome de campo |
| `Kiln.salvar_upload(arq, pasta, …)` | grava, recusando o que não deve entrar |

O vault de um arquivo tem `nome`, `tipo`, `tamanho`, `conteudo` (bytes)
e `texto`.

## Campos e arquivos ficam separados

Os campos comuns ficam em `req["body"]`, como num formulário qualquer —
quem escreve lê `body["titulo"]` sem saber se o formulário tinha
arquivo. Os arquivos ficam em `req["files"]`, à parte: assim um `cycle`
sobre `body` não topa com bytes onde espera texto.

Um campo **repetido** vira cluster, e não o último valor: é assim que um
`<select multiple>` e uma lista de caixas chegam.

## As três recusas de `salvar_upload`

| Recusa | Por quê |
|---|---|
| nome com `/`, `\` ou `..` | `../../.ssh/authorized_keys` escreve fora da pasta |
| acima do limite | um upload de 4 GB enche o disco |
| extensão fora da lista | `.php` numa pasta servida como estática é execução remota |

E o nome final **nunca** é o que o cliente mandou: leva um prefixo
aleatório. Dois usuários enviando `foto.jpg` não podem sobrescrever um
ao outro, e um nome escolhido por quem envia é um nome que ele pode
adivinhar depois.

`nome_original` volta no resultado, para guardar no banco e mostrar ao
usuário.

## Por que recusar, e não sanear

`os.path.basename("../../x")` devolve `x` — a travessia fica
neutralizada. Mas um cliente que manda `../../.ssh/authorized_keys`
está quebrado ou é hostil, e aceitar como `authorized_keys` **esconde
isso de quem lê o log**.

## Armadilha

O limite de corpo do Kiln (`limite_corpo`, 10 MB por padrão) é
verificado **antes** de o corpo ser lido na memória. Um upload maior
que isso é recusado com 413 sem chegar à rota — ajuste
`Kiln.config(app, "limite_corpo", …)` antes de aumentar o limite do
`salvar_upload`.
