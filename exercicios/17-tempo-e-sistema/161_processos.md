# Exercicio 161 — Executando processos

## Enunciado

Rode comandos externos, trate a saída e os erros.

## Segurança primeiro

Por padrão, `Arcane.Process` **não passa pelo shell**:

```dataforge
Proc.run("echo ola")                    // sem shell
Proc.run(["echo", "texto com espacos"]) // lista: mais seguro ainda
Proc.run("...", shell := yes)           // shell, conscientemente
```

Sem shell, não há injeção: `rm -rf /` dentro de uma variável vira um argumento
literal, não um comando. Só ligue `shell := yes` quando precisar de pipes,
redirecionamentos ou expansão de `*` — e nunca com texto vindo do usuário.

## O resultado

`run` sempre devolve um `ProcessResult`, mesmo quando falha:

| Campo | Contém |
|-------|--------|
| `stdout` | a saída padrão |
| `stderr` | a saída de erro |
| `exit_code` | 0 = sucesso |
| `ok` | `yes` se o código foi 0 |
| `failed` | o oposto de `ok` |
| `lines` | `stdout` já separado em linhas |

Um comando inexistente devolve um código de erro em vez de derrubar o programa.
Isso é deliberado: falha de processo externo é um resultado esperado, não uma
exceção.

O código, porém, **não é o mesmo em todo lugar**: 127 no Linux e no macOS, 1 no
Windows. É o primeiro sinal de algo que o exercício trata logo abaixo.

```dataforge
r := Proc.run("comando_inexistente")
given r.failed:
    out $"nao rolou: {r.stderr}"
```

## Atalhos

```dataforge
Proc.capture("echo x")     // só o stdout, sem a quebra final
Proc.check("test -f x")    // só yes/no
Proc.exit_code("cmd")      // só o número
Proc.exists("git")         // o programa está instalado?
```

## Enviar entrada

```dataforge
Proc.run("sort", input_text := "c\na\nb")
```

Útil para alimentar um filtro sem escrever arquivo temporário.

## Encadear

```dataforge
Proc.pipeline(["echo zebra", "sort"])
```

A saída de cada comando vira a entrada do próximo, e a cadeia **para no primeiro
que falhar** — devolvendo o resultado daquele, não um sucesso enganoso.

## Tempo limite

```dataforge
Proc.run("sleep 5", timeout := 1)     // ok = no, timed_out = yes
// (no Windows: "timeout 5")
```

Sempre ponha timeout em comando que fala com a rede. Sem ele, um servidor que
não responde trava seu programa indefinidamente.

## Processos em segundo plano

```dataforge
p := Proc.spawn("servidor --porta 8080")
// ... o programa continua
Proc.is_running(p)
Proc.terminate(p)      // pede para encerrar (SIGTERM)
Proc.kill(p)           // força (SIGKILL)
r := Proc.wait(p)      // espera e colhe o resultado
```

## O comando externo é onde o programa deixa de ser portátil

Tudo o mais em DataForge roda igual nos três sistemas. Chamar um programa de
fora é a fronteira: `echo` existe no Linux e no macOS como arquivo executável e
no Windows é embutido do interpretador de comandos, `cat` se chama `more`, e
`sleep` se chama `timeout`.

A resposta não é fingir que dá no mesmo. É decidir **uma vez**, no topo, e
escrever o resto igual:

```dataforge
adopt Arcane.OS as OS

steady WINDOWS := OS.is_windows()
steady ECO := "cmd /c echo" given WINDOWS otherwise "echo"
steady NAO_ENCONTRADO := 1 given WINDOWS otherwise 127
```

`sort` é uma das poucas exceções: existe com o mesmo nome nos dois e lê da
entrada padrão. Por isso o exercício o usa para mostrar `input_text` e
`pipeline`.

## Saída esperada

```
saida:  ola do processo
codigo: 0
ok:     yes

capture: 'direto'

inexistente -> codigo 127, ok=no

xyz existe?  no

lista: texto com espacos
stdin ordenado: [a, b, c]

pipeline: zebra

com timeout: ok=no
```

No Windows o `127` vira `1`. O resto é idêntico — e é por isso que o exercício
decide o comando **uma vez**, no topo.

## Experimente

- Rode `git log --oneline -5` e mostre os commits formatados.
- Rode o exercício no outro sistema operacional e veja o que muda.
- Escreva `action tem_git()` usando `Proc.exists`.
- Compare `run` com `shell := yes` e sem, num comando com `*`.
