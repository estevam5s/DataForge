# Exercicio 226 — Instantâneo, banco isolado e teste instável

## Enunciado

Três ferramentas do Crucible para o que um teste comum não alcança bem:
resultado grande, estado que sobra entre testes, e falha que vai e volta.

## Instantâneo

```dataforge
trial "o relatorio nao muda sem aviso":
    Crucible.snapshot("relatorio", gerar_relatorio())
```

Para o que é grande demais para escrever à mão no teste: o HTML de uma
página, o relatório de trinta linhas, o JSON de uma rota. Escrever o
esperado à mão para isso dá um teste que ninguém mantém — e um teste
que ninguém mantém vira um teste que alguém comenta.

**Na primeira vez ele grava e passa.** É o único jeito de começar, e por
isso o arquivo vai no controle de versão: é no diff do commit que
alguém confere se o novo esperado está certo.

Para aceitar uma mudança intencional:

```bash
DF_ATUALIZAR_SNAPSHOT=1 dataforge crucible
```

Atualizar por padrão seria **pior que não ter instantâneo**: o teste
passaria sempre, gravando o errado por cima do certo.

Os arquivos ficam em `__snapshots__/<arquivo>.snap.json`, ao lado do
teste — assim andam junto num `git mv`, e o diff mostra os dois lado a
lado. As chaves saem ordenadas: um vault que muda de ordem de inserção
faria o instantâneo falhar sem nada ter mudado de verdade.

Quando muda, a mensagem traz o **diff**, e não os dois textos inteiros —
trezentas linhas lado a lado num terminal são ilegíveis, e ter
trezentas linhas é justamente o motivo de usar instantâneo.

## Banco que se desfaz

```dataforge
crucible "cadastro":
    Crucible.before(lambda suite: Crucible.banco(db))

    trial "grava":
        Banco.insert(db, "livros", {...})
        Crucible.expect(Banco.count(db, "livros")).to_be(3)

    trial "e o seguinte nao ve":
        Crucible.expect(Banco.count(db, "livros")).to_be(2)
```

O problema: um teste que grava deixa a linha lá, e o teste seguinte a
encontra. A suíte passa **na ordem em que foi escrita** e falha em
qualquer outra — e `--aleatorio` expõe isso de um jeito que parece
intermitente.

`Crucible.banco(db)` abre uma transação e a desfaz no fim do trial,
sempre. Apagar tudo entre testes seria a alternativa, e é mais lenta e
mais frágil: ela precisa saber a ordem das chaves estrangeiras.

## Teste instável

```dataforge
r := Crucible.flaky(consultar_a_api, 3, 0.5)
Crucible.expect(r["ok"]).to_be(yes)
```

Existe para o que depende de rede, de relógio ou de escalonamento — e
**não** para esconder um bug. Por isso ele devolve o número de
tentativas: um teste que precisa de três toda vez não é instável, está
quebrado, e o número é o que denuncia isso.

## Armadilha

`Crucible.expect(…).to_raise()` **não** captura o que `flaky` levanta ao
desistir: aquilo é a própria falha de expectativa do Crucible, que é o
sinal de teste reprovado — não um erro a capturar. Use
`monitor`/`handle` quando quiser conferir a desistência.

## Continua em

- [211 — Matchers](../25-testes-crucible/211_matchers.df)
- [212 — Dublês e fixtures](../25-testes-crucible/212_dubles_e_fixtures.df)
- [225 — Cobertura](225_cobertura.df)
