# Exercicio 154 — Manifesto e ferramentas

## Enunciado

Conheça o `forge.toml` e os comandos de projeto que ele habilita.

## O manifesto

`forge.toml` fica na raiz do projeto e descreve o que ele é:

```toml
[project]
name = "meu-app"
version = "0.1.0"
entry = "src/main.df"
dataforge = ">=4.0"

[scripts]
start = "run src/main.df"
test = "test tests/"

[lint]
strict = false
ignore = ["magic-number"]
```

## Criar e inspecionar

```bash
dataforge init          # cria forge.toml, src/ e tests/
dataforge info          # mostra o manifesto e checa a versão
```

O `info` avisa se o `dataforge = ">=4.0"` não bate com a versão instalada — antes
de você descobrir isso por um erro de sintaxe estranho.

## O que o manifesto habilita

### Entrada padrão

```bash
dataforge run           # sem argumento: usa project.entry
```

### Scripts nomeados

Qualquer chave em `[scripts]` vira um comando:

```bash
dataforge start         # roda "run src/main.df"
dataforge test          # roda "test tests/"
```

Isso guarda o comando certo no repositório, em vez de num README que ninguém lê.

### Raiz do projeto

Comandos rodam a partir da pasta do `forge.toml`, não de onde você está. Rodar
`dataforge test` de dentro de `src/` funciona igual.

## O ciclo completo

```bash
dataforge init                # começar
dataforge check src/          # nomes, tipos, aridade
dataforge lint src/           # estilo e higiene
dataforge fmt src/            # formatar
dataforge test tests/ -v      # testes
dataforge doc src/ --out=doc/API.md
dataforge run                 # executar
```

Numa integração contínua, o conjunto vira:

```bash
dataforge fmt . --check && dataforge check . && dataforge test
```

Cada um sai com código diferente de zero em caso de falha.

## TOML no seu próprio código

`Arcane.Serialization` lê e escreve TOML, útil para configuração da sua
aplicação:

```dataforge
config := Serde.from_toml(IO.read("config.toml"))
porta := Serde.json_path(config, "servidor.porta", 8080)
```

O terceiro argumento de `json_path` é o padrão quando o caminho não existe — mais
direto que encadear `given` para cada nível.

## Saída esperada

```
name = "meu-app"
version = "0.1.0"
...

nome:    meu-app
entrada: src/main.df
script:  test tests/
ausente: nao definido

validacao: []
incompleto: [falta project.version, falta project.entry]
```

## Experimente

- Rode `dataforge init` numa pasta vazia e explore o que foi gerado.
- Adicione um script `fmt` e rode `dataforge fmt`.
- Escreva um validador de manifesto que também confere o formato da versão.
