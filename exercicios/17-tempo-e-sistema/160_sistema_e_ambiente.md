# Exercicio 160 — Sistema e ambiente

## Enunciado

Consulte o sistema operacional, o disco e as variáveis de ambiente.

## Conceitos

`Arcane.OS` é **somente leitura por padrão**. As duas exceções — `set_env` e
`chdir` — estão marcadas como tal na documentação do módulo. Nada aqui apaga
arquivo ou mata processo.

## Identificar o sistema

```dataforge
OS.name()          // "Darwin", "Linux", "Windows"
OS.release()       OS.version()
OS.arch()          // "64bit"
OS.machine()       // "arm64", "x86_64"
OS.hostname()
OS.cpu_count()
OS.user()
```

Para ramificar por plataforma, prefira os predicados:

```dataforge
OS.is_windows()   OS.is_mac()   OS.is_linux()   OS.is_posix()
```

Eles são mais legíveis e mais robustos que comparar `OS.name()` com texto —
`"Darwin"` para macOS não é óbvio para quem lê.

## Ternário encadeado

```dataforge
plataforma := "Windows" given OS.is_windows()
    otherwise "macOS" given OS.is_mac()
    otherwise "Linux" given OS.is_linux()
    otherwise "outro"
```

Cada `otherwise` abre o próximo teste. Funciona, mas com quatro ramos um `given`/
`orif` em bloco já lê melhor — o ternário rende mais em dois ou três casos.

## Variáveis de ambiente

```dataforge
OS.get_env("PATH")                       // void se não existir
OS.get_env("PORTA", "8080")              // com padrão
OS.has_env("HOME")
OS.env()                                 // todas, como vault
OS.set_env("MINHA_VAR", "valor")
```

O segundo argumento de `get_env` é o que torna configuração por ambiente
utilizável:

```dataforge
porta := cast OS.get_env("PORTA", "8080") as Integer
```

Sem ele, cada leitura precisaria de um `given` para o caso ausente.

**Cuidado com segredos:** variáveis de ambiente costumam guardar senhas e
chaves. `OS.env()` traz tudo — nunca despeje isso em log.

## Disco

```dataforge
uso := OS.disk_usage(".")
uso.total_gb    uso.free_gb    uso.percent_used
```

Os campos em GB vêm arredondados, prontos para exibir; os campos em bytes
(`total`, `free`) servem para conta.

## `which`

```dataforge
OS.which("python3")     // caminho, ou void
```

Devolve `void` quando não encontra — combine com `??` para um padrão:

```dataforge
editor := OS.which("nvim") ?? OS.which("vim") ?? "nano"
```

## Saída esperada

```
┌─────────┐
│ Sistema │
└─────────┘
sistema:    Darwin 25.3.0
arquitetura: 64bit (arm64)
CPUs:       10
plataforma: macOS
...
```

(os valores dependem da sua máquina)

## Experimente

- Escreva um relatório que muda de formato conforme `OS.terminal_size()`.
- Leia a configuração de variáveis de ambiente com padrões sensatos.
