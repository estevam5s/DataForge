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

Um comando inexistente devolve código 127 em vez de derrubar o programa. Isso é
deliberado: falha de processo externo é um resultado esperado, não uma exceção.

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
Proc.run("cat", input_text := "vindo da entrada")
```

Útil para alimentar um filtro sem escrever arquivo temporário.

## Encadear

```dataforge
Proc.pipeline(["printf 'c\na\nb'", "sort"])
```

A saída de cada comando vira a entrada do próximo, e a cadeia **para no primeiro
que falhar** — devolvendo o resultado daquele, não um sucesso enganoso.

## Tempo limite

```dataforge
Proc.run("sleep 5", timeout := 1)     // ok = no, timed_out = yes
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

## Saída esperada

```
saida:  ola do processo
codigo: 0
ok:     yes

capture: 'direto'

inexistente -> codigo 127, ok=no
stderr: comando não encontrado: comando_que_nao_existe_xyz
...
pipeline ordenado: [a, b, c]

com timeout: ok=no
```

## Experimente

- Rode `git log --oneline -5` e mostre os commits formatados.
- Escreva `action tem_git()` usando `Proc.exists`.
- Compare `run` com `shell := yes` e sem, num comando com `*`.
