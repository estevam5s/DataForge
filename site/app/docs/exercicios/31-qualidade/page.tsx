// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "31 · Qualidade",
  description: "3 exercícios: check, lint, cobertura e o que o CI cobra.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 31`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[227](#227-cobertura-o-que-os-testes-nao-exercitaram)", "**Cobertura: o que os testes NAO exercitaram**", ""], ["[228](#228-instantaneo-banco-isolado-e-teste-instavel)", "**Instantaneo, banco isolado e teste instavel**", ""], ["[229](#229-depurar-sem-out)", "**Depurar sem 'out'**", ""]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um traz a explicação junto", "texto": "Neste módulo, cada exercício vem com os conceitos, a saída esperada e sugestões para experimentar — tudo abaixo, e também em `.md` ao lado do `.df` no repositório."}},
  {"h2": "227 · Cobertura: o que os testes NAO exercitaram"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 227 — Cobertura: o que os testes NAO exercitaram
//
//  Uma suite verde nao diz nada sobre o que ela nao toca. Num sistema
//  de 200 arquivos, o codigo que ninguem exercitou e exatamente onde
//  o bug mora.
//
//  Este exercicio nao mede a si mesmo — a cobertura se pede na linha
//  de comando:
//
//      dataforge test --cobertura
//      dataforge test --minimo=80        # reprova abaixo disso
//      dataforge test --cobertura --linhas
//      dataforge crucible --cobertura
//
//  O que ele mostra e o que a medicao ENXERGA, e o que ela nao.
// ════════════════════════════════════════════════════════════

adopt Arcane.OS as OS
adopt Arcane.IO as IO
adopt Arcane.Process as P

// ── 1. Um projeto pequeno, com um ramo nao testado ──────────

raiz := IO.join(OS.temp_dir(), "df_cobertura_exercicio")
given IO.exists(raiz):
    IO.remove_tree(raiz)
IO.mkdir(IO.join(raiz, "src"))
IO.mkdir(IO.join(raiz, "tests"))

IO.write(IO.join(raiz, "forge.toml"),
    '[project]\\nname = "cob"\\nversion = "1.0.0"\\nentry = "src/main.df"\\n')

IO.write(IO.join(raiz, "src", "conta.df"), """
action taxa(valor, tipo):
    given tipo is "premium":
        yield valor * 0.01
    orif tipo is "comum":
        yield valor * 0.03
    yield valor * 0.05

action nunca_chamada(x):
    yield x * 2

relay taxa, nunca_chamada
""")

IO.write(IO.join(raiz, "src", "main.df"), """
adopt ./conta as C

out C.taxa(100, "comum")
""")

IO.write(IO.join(raiz, "tests", "conta_test.df"), """
adopt Arcane.Test as T
adopt ../src/conta as C

action test_premium():
    T.assert_eq(C.taxa(100, "premium"), 1.0)
""")

// ── 2. Medir ────────────────────────────────────────────────

r := P.run(["dataforge", "test", "--cobertura", "--linhas", "--no-color"],
    cwd := raiz)
saida := r["stdout"]

// So a secao de cobertura interessa: o nome do arquivo de teste
// aparece na linha de resultado dele, que e outra coisa.
// A barra invertida do Windows vira barra: o relatorio mostra o
// caminho como o SISTEMA o escreve, e um teste que procura "src/conta"
// passa em Linux e reprova no Windows.
relatorio := saida.split("Cobertura")[1].replace("\\\\", "/")

// O arquivo de codigo e medido; o de teste, nao — o que interessa
// medir e o codigo, nao a suite.
assert "src/conta.df" in relatorio
assert "conta_test.df" not in relatorio

// A acao que ninguem chamou aparece POR NOME. E a informacao que
// resolve: "58% coberto" nao diz o que fazer; "sem teste:
// nunca_chamada" diz.
assert "nunca_chamada" in relatorio

// E as linhas descobertas saem em faixas — uma lista de setenta
// numeros e ilegivel.
assert "linhas:" in relatorio

// ── 3. O minimo reprova, e isso e o que serve no CI ─────────

alto := P.run(["dataforge", "test", "--minimo=95", "--no-color"], cwd := raiz)
assert alto["exit_code"] is 1
assert "abaixo do mínimo" in alto["stdout"]

baixo := P.run(["dataforge", "test", "--minimo=10", "--no-color"], cwd := raiz)
assert baixo["exit_code"] is 0

// ── 4. O que a medicao NAO ve ───────────────────────────────
//
// Ela e de LINHA, e nao de ramo: 'given a and b' conta como coberta
// mesmo que 'b' nunca tenha sido avaliado. Medir ramo dobraria o
// custo, e cobertura de linha ja responde a pergunta que importa —
// "existe codigo que ninguem testou".
//
// Duas escolhas que mudam o que o numero diz:
//
//   - a linha do 'action' nao conta, so o corpo. Uma acao nunca
//     chamada aparece com 0%, e nao com 20%.
//   - um arquivo que NENHUM teste toca aparece com 0% em vez de sumir
//     do relatorio. Sumir e o que faz uma cobertura de 95% conviver
//     com metade do sistema sem teste.

assert "0.0%" in relatorio  // o main.df, que nenhum teste importa

IO.remove_tree(raiz)
out "225 ok — cobertura"`, lang: 'df', title: `exercicios/31-qualidade/227_cobertura.df` },
  {"h3": "O problema"},
  {"p": "Uma suíte verde não diz nada sobre o que ela não exercita. Num sistema de 200 arquivos, o código que ninguém tocou é exatamente onde o bug mora — e `13 passaram` não distingue \"o sistema está testado\" de \"os treze caminhos fáceis estão testados\"."},
  {"h3": "Como se pede"},
  { code: `dataforge test --cobertura
dataforge test --cobertura --linhas     # as linhas, em faixas
dataforge test --minimo=80              # reprova abaixo disso (saída 1)
dataforge crucible --cobertura`, lang: 'bash' },
  { code: `  src/main.df         ░░░░░░░░░░░░░░░░░░░░   0.0%  0/94
                      sem teste: montar_cli, mostrar, principal
  src/repositorio.df  ████████████████████ 100.0%  38/38
  src/tarefa.df       ████████████████████ 100.0%  14/14

  total  35.6%  52 de 146 linhas executáveis`, lang: 'text' },
  {"p": "`--minimo` aceita `80`, `80%` e `0.8`. A fronteira é em 1 **inclusive**: `--minimo=1` é um por cento, porque ninguém exige cobertura total digitando `1`."},
  {"h3": "O que faz o número significar algo"},
  {"p": "Os dois lados da fração têm um jeito próprio de mentir:"},
  {"table": {"head": ["Metade", "De onde vem", "Como mentiria"], "rows": [["denominador", "o parser: quais linhas são **executáveis**", "contar comentário e linha vazia dá um número sempre pessimista, que ninguém olha duas vezes"], ["numerador", "a execução, instrumentada", "com a compilação de corpos ligada, toda ação daria 0%"]]}},
  {"p": "E duas escolhas que mudam o que se lê:"},
  {"p": "**A linha do `action` não conta; o corpo conta.** Assim uma ação nunca chamada aparece com **0%**, e não com 20%."},
  {"p": "**Um arquivo que nenhum teste toca aparece com 0%**, em vez de sumir do relatório. Sumir é o que faz uma cobertura de 95% conviver com metade do sistema sem teste."},
  {"h3": "A informação que resolve"},
  {"p": "`58% coberto` não diz o que fazer. `sem teste: nunca_chamada` diz."},
  {"p": "Por isso o relatório lista, para cada arquivo, **os nomes das ações** cujo corpo nunca rodou — e com `--linhas`, as linhas em faixas (`3-5, 9, 11-12`), porque uma lista de setenta números é ilegível."},
  {"h3": "O que ela NÃO mede"},
  {"p": "É de **linha**, e não de ramo: `given a and b` conta como coberta mesmo que `b` nunca tenha sido avaliado. Medir ramo exigiria instrumentar a avaliação de expressão, o que dobraria o custo — e cobertura de linha já responde a pergunta que importa, que é \"existe código que ninguém testou\"."},
  {"h3": "Uma advertência"},
  {"p": "Cobertura alta não é qualidade. Um teste que chama tudo e não verifica nada dá 100%. O número serve para achar o que está a **zero**, e é aí que ele vale quase tudo o que custa."},
  {"h2": "228 · Instantaneo, banco isolado e teste instavel"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 228 — Instantaneo, banco isolado e teste instavel
//
//  Tres ferramentas do Crucible para o que um teste comum nao alcanca
//  bem: resultado grande, estado que sobra entre testes, e falha que
//  vai e volta.
// ════════════════════════════════════════════════════════════

adopt Crucible
adopt Arcane.Database as Banco

// ── 1. O banco de exemplo ───────────────────────────────────

db := Banco.memory()
Banco.create_table(db, "livros", {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "titulo": "TEXT NOT NULL",
        "preco": "REAL NOT NULL"
    })
Banco.insert_many(db, "livros", [
        {"titulo": "Duna", "preco": 79.9},
        {"titulo": "Neuromancer", "preco": 64.9}
    ])

action relatorio():
    linhas := Banco.aggregate(db, "livros",
        {"quantos":["count", "*"],
            "total":["sum", "preco"]})
    yield {"acervo": linhas[0]["quantos"], "valor": linhas[0]["total"]}

// ── 2. Instantaneo ──────────────────────────────────────────
//
// Para o que e grande demais para escrever a mao no teste: o HTML de
// uma pagina, o relatorio de trinta linhas, o JSON de uma rota.
// Escrever o esperado a mao para isso da um teste que ninguem mantem.
//
// Na PRIMEIRA vez ele grava e passa — e o unico jeito de comecar. O
// arquivo vai no controle de versao, e e no diff do commit que alguem
// confere se o novo esperado esta certo.
//
// Para aceitar uma mudanca intencional:
//     DF_ATUALIZAR_SNAPSHOT=1 dataforge crucible
//
// Atualizar por padrao seria pior que nao ter instantaneo: o teste
// passaria sempre, gravando o errado por cima do certo.

crucible "o relatorio":
    trial "nao muda sem aviso":
        Crucible.snapshot("relatorio_do_acervo", relatorio())

    trial "e o texto grande tambem entra":
        html := "<table>\\n  <tr><td>Duna</td></tr>\\n</table>"
        Crucible.snapshot("tabela_html", html)

// ── 3. Banco que se desfaz ──────────────────────────────────
//
// O problema: um teste que grava deixa a linha la, e o teste seguinte
// a encontra. A suite passa na ordem em que foi escrita e falha em
// qualquer outra — e '--aleatorio' expoe isso de um jeito que parece
// intermitente.
//
// 'Crucible.banco(db)' abre uma transacao e a desfaz no fim do trial,
// SEMPRE. Apagar tudo entre testes seria a alternativa, e e mais lenta
// e mais fragil: ela precisa saber a ordem das chaves estrangeiras.

crucible "isolamento de banco":
    Crucible.before(lambda suite: Crucible.banco(db))

    trial "um teste que grava":
        Banco.insert(db, "livros", {"titulo": "Solaris", "preco": 54.9})
        Crucible.expect(Banco.count(db, "livros")).to_be(3)

    trial "e o seguinte nao ve o que ele gravou":
        Crucible.expect(Banco.count(db, "livros")).to_be(2)

    trial "nem na ordem inversa":
        Banco.insert(db, "livros", {"titulo": "Fundacao", "preco": 49.9})
        Crucible.expect(Banco.count(db, "livros")).to_be(3)

// ── 4. Teste instavel ──────────────────────────────────────
//
// Existe para o que depende de rede, de relogio ou de escalonamento —
// e NAO para esconder um bug. Ele conta as tentativas: um teste que
// precisa de tres toda vez nao e instavel, esta quebrado, e o numero e
// o que denuncia isso.

crucible "instabilidade":
    trial "tenta de novo antes de desistir":
        tentativas := {"n": 0}

        action falha_duas_vezes():
            tentativas["n"] := tentativas["n"] + 1
            given tentativas["n"] smaller 3:
                trigger "a rede ainda nao respondeu"
            yield yes

        r := Crucible.flaky(falha_duas_vezes, 5)
        Crucible.expect(r["ok"]).to_be(yes)
        Crucible.expect(r["tentativas"]).to_be(3)

    trial "e desiste depois do limite":
        // 'to_raise' nao serve aqui: o que 'flaky' levanta ao desistir
        // e a propria falha de expectativa do Crucible, e ela e o
        // sinal de teste reprovado — nao um erro a capturar.
        desistiu := no
        monitor:
            Crucible.flaky(lambda: trigger("sempre falha"), 2)
        handle Error as e:
            desistiu := "2 tentativas" in e.message
        Crucible.expect(desistiu).to_be(yes)

// ── 5. Rodar ────────────────────────────────────────────────
//
// Fora do 'dataforge crucible', os instantaneos precisam saber de qual
// arquivo sao — quem roda pelo comando nao precisa disto.

Crucible.snapshot_dir(__file__)
r := Crucible.run()
assert r["falhou"] is 0, $"{r["falhou"]} falharam"
assert r["erro"] is 0
assert r["passou"] is 7

out "226 ok — instantaneo e isolamento"`, lang: 'df', title: `exercicios/31-qualidade/228_instantaneo_e_isolamento.df` },
  {"h3": "Instantâneo"},
  { code: `trial "o relatorio nao muda sem aviso":
    Crucible.snapshot("relatorio", gerar_relatorio())`, lang: 'df' },
  {"p": "Para o que é grande demais para escrever à mão no teste: o HTML de uma página, o relatório de trinta linhas, o JSON de uma rota. Escrever o esperado à mão para isso dá um teste que ninguém mantém — e um teste que ninguém mantém vira um teste que alguém comenta."},
  {"p": "**Na primeira vez ele grava e passa.** É o único jeito de começar, e por isso o arquivo vai no controle de versão: é no diff do commit que alguém confere se o novo esperado está certo."},
  {"p": "Para aceitar uma mudança intencional:"},
  { code: `DF_ATUALIZAR_SNAPSHOT=1 dataforge crucible`, lang: 'bash' },
  {"p": "Atualizar por padrão seria **pior que não ter instantâneo**: o teste passaria sempre, gravando o errado por cima do certo."},
  {"p": "Os arquivos ficam em `__snapshots__/<arquivo>.snap.json`, ao lado do teste — assim andam junto num `git mv`, e o diff mostra os dois lado a lado. As chaves saem ordenadas: um vault que muda de ordem de inserção faria o instantâneo falhar sem nada ter mudado de verdade."},
  {"p": "Quando muda, a mensagem traz o **diff**, e não os dois textos inteiros — trezentas linhas lado a lado num terminal são ilegíveis, e ter trezentas linhas é justamente o motivo de usar instantâneo."},
  {"h3": "Banco que se desfaz"},
  { code: `crucible "cadastro":
    Crucible.before(lambda suite: Crucible.banco(db))

    trial "grava":
        Banco.insert(db, "livros", {...})
        Crucible.expect(Banco.count(db, "livros")).to_be(3)

    trial "e o seguinte nao ve":
        Crucible.expect(Banco.count(db, "livros")).to_be(2)`, lang: 'df' },
  {"p": "O problema: um teste que grava deixa a linha lá, e o teste seguinte a encontra. A suíte passa **na ordem em que foi escrita** e falha em qualquer outra — e `--aleatorio` expõe isso de um jeito que parece intermitente."},
  {"p": "`Crucible.banco(db)` abre uma transação e a desfaz no fim do trial, sempre. Apagar tudo entre testes seria a alternativa, e é mais lenta e mais frágil: ela precisa saber a ordem das chaves estrangeiras."},
  {"h3": "Teste instável"},
  { code: `r := Crucible.flaky(consultar_a_api, 3, 0.5)
Crucible.expect(r["ok"]).to_be(yes)`, lang: 'df' },
  {"p": "Existe para o que depende de rede, de relógio ou de escalonamento — e **não** para esconder um bug. Por isso ele devolve o número de tentativas: um teste que precisa de três toda vez não é instável, está quebrado, e o número é o que denuncia isso."},
  {"h3": "Armadilha"},
  {"p": "`Crucible.expect(…).to_raise()` **não** captura o que `flaky` levanta ao desistir: aquilo é a própria falha de expectativa do Crucible, que é o sinal de teste reprovado — não um erro a capturar. Use `monitor`/`handle` quando quiser conferir a desistência."},
  {"h3": "Continua em"},
  {"list": ["[211 — Matchers](../25-testes-crucible/211_matchers.df)", "[212 — Dublês e fixtures](../25-testes-crucible/212_dubles_e_fixtures.df)", "[225 — Cobertura](225_cobertura.df)"]},
  {"h2": "229 · Depurar sem 'out'"},
  { code: `// ════════════════════════════════════════════════════════════
//  Exercicio 229 — Depurar sem 'out'
//
//  'out' no meio do codigo e o depurador mais usado do mundo, e ele
//  tem tres defeitos: muda o que voce esta medindo, tem de ser
//  removido depois, e nao mostra o que voce NAO pensou em imprimir.
//
//  Este exercicio nao usa o depurador interativo — ele exige um
//  terminal ou um editor. Ele exercita as DUAS pecas em que o
//  depurador se apoia, e que dao para verificar com 'assert': saber
//  quais linhas sao executaveis, e ler o valor no quadro certo.
// ════════════════════════════════════════════════════════════

// ── O programa que vamos investigar ─────────────────────────
//
// Ele tem um bug de verdade: a media de uma lista vazia.

action media(nums):
    soma := 0
    cycle n in nums:
        soma := soma + n
    yield soma / len(nums)

// ── 1. O erro diz o arquivo, a linha e a coluna ─────────────
//
// E o primeiro depurador: um stack trace que aponta o lugar.

monitor:
    media([])
    assert no  // nao chega aqui
handle Error as e:
    assert e.type is "DivisionByZeroError"
    // A linha e a do 'yield', dentro da acao — e nao a da chamada.
    assert e.line is 22

// ── 2. A pilha diz quem chamou quem ─────────────────────────
//
// Numa acao chamada de cinco lugares, "deu erro em media()" nao
// ajuda: o que importa e QUAL das cinco chamadas.

action relatorio(vendas):
    yield media(vendas)

monitor:
    relatorio([])
handle Error as e:
    nomes := [q["name"] cycle q in e.stack]
    assert "media" in nomes
    assert "relatorio" in nomes
    // Do mais externo para o mais interno: e a ordem em que se le
    // "quem chamou quem".
    assert nomes.index("relatorio") smaller nomes.index("media")

// ── 3. Consertado, com o caso que faltava ───────────────────

action media2(nums):
    given len(nums) is 0:
        yield 0.0
    soma := 0
    cycle n in nums:
        soma := soma + n
    yield soma / len(nums)

assert media2([]) is 0.0
assert media2([2, 4, 6]) is 4.0

// ── 4. 'defer' mostra sem sujar o caminho de saida ──────────
//
// Um 'out' antes de cada 'yield' precisa ser repetido em cada saida
// da acao — e a que voce esquecer e justamente a que da errado.
// 'defer' roda na saida, qualquer uma delas.

saidas := []

action classificar(n):
    // 'defer' abre BLOCO — nao aceita expressao na mesma linha.
    defer:
        saidas.append($"classificar({n}) saiu")
    given n smaller 0:
        yield "negativo"
    given n is 0:
        yield "zero"
    yield "positivo"

assert classificar(-5) is "negativo"
assert classificar(0) is "zero"
assert classificar(7) is "positivo"

// Tres saidas diferentes, tres registros — nenhum esquecido.
assert len(saidas) is 3
assert saidas[0] is "classificar(-5) saiu"

// ── 5. A pilha atravessa 'monitor' aninhado ─────────────────
//
// O quadro onde o erro NASCEU e o que importa, e nao o ponto onde
// alguem decidiu capturar. Um 'handle' tres niveis acima ainda ve o
// caminho inteiro.

action nivel3():
    trigger "o disco encheu"

action nivel2():
    yield nivel3()

action nivel1():
    monitor:
        yield nivel2()
    handle RuntimeError:
        // NAO pega: 'trigger' levanta TriggerError. A armadilha 18.
        yield "nao passa por aqui"

monitor:
    nivel1()
    assert no
handle Error as e:
    nomes := [q["name"] cycle q in e.pilha]
    assert nomes is ["nivel1", "nivel2", "nivel3"]

    // Cada quadro diz onde estava a chamada — arquivo inclusive, que e
    // o que faz a pilha servir num projeto de 200 arquivos.
    cycle q in e.pilha:
        assert q["line"] bigger 0
        assert "229_depurar" in q["file"]

// ── 6. Duas linhas diferentes, e as duas estao certas ──────
//
// E a confusao mais comum ao ler uma pilha:
//
//   e.line          onde o erro NASCEU
//   quadro["line"]  onde a CHAMADA foi feita
//
// Sao numeros diferentes de propósito. Para consertar, voce quer o
// primeiro; para entender por que aquela acao foi chamada com aquele
// argumento, o segundo.

monitor:
    media([])
handle Error as e:
    // Onde estourou: dentro de 'media', no 'yield'.
    assert e.line is 22

    // Onde 'media' foi chamada: aqui, DEPOIS da declaracao — e por
    // isso o numero e maior. Sao dois numeros diferentes, e as duas
    // respostas estao certas para perguntas diferentes.
    assert e.pilha[0]["name"] is "media"
    assert e.pilha[0]["line"] bigger e.line

    // E o arquivo, em cada quadro. Uma acao declarada num arquivo e
    // chamada de outro ja reportou a linha certa com o NOME do arquivo
    // errado — e isso manda a pessoa depurar o arquivo errado.
    assert "229_depurar.df" in e.pilha[0]["file"]

out "229 ok — depurar"`, lang: 'df', title: `exercicios/31-qualidade/229_depurar.df` },
  {"h3": "Por que não `out`"},
  {"p": "`out` no meio do código é o depurador mais usado do mundo, e tem três defeitos:"},
  {"table": {"head": ["Defeito", "Consequência"], "rows": [["muda o que você está medindo", "o `out` num laço apertado altera o tempo que você queria medir"], ["tem de ser removido depois", "e o que sobrar vira ruído na saída de produção"], ["só mostra o que você pensou em imprimir", "o valor que explica o bug é justamente o que você não suspeitou"]]}},
  {"p": "O terceiro é o pior. Um depurador mostra **tudo que está vivo** naquele ponto, incluindo o que você não sabia que precisava ver."},
  {"h3": "O que este exercício exercita"},
  {"p": "O depurador interativo precisa de um terminal (`dataforge debug`) ou de um editor (F5). Nenhum dos dois cabe num `assert`. O que cabe — e é o que este exercício cobra — são as informações em que ele se apoia, e que a linguagem entrega ao programa:"},
  { code: `monitor:
    media([])
handle Error as e:
    out e.type       // "DivisionByZeroError"
    out e.line       // 22 — a linha do yield, onde nasceu
    out e.pilha      // quem chamou quem`, lang: 'df' },
  {"h3": "`e.pilha` — quem chamou quem"},
  {"p": "Numa ação chamada de cinco lugares, *\"deu erro em `media()`\"* não ajuda: o que importa é **qual** das cinco chamadas."},
  { code: `handle Error as e:
    nomes := [q["name"] cycle q in e.pilha]
    assert nomes is ["nivel1", "nivel2", "nivel3"]`, lang: 'df' },
  {"p": "Do **mais externo para o mais interno** — a ordem em que se lê \"quem chamou quem\", e a mesma em que o stack trace desenha. Inverter aqui faria o programa e a tela discordarem sobre a mesma pilha."},
  {"p": "Cada quadro é um vault com `name`, `line`, `column` e `file`. O `file` é o que faz a pilha servir num projeto de 200 arquivos."},
  {"p": "`e.stack` é o mesmo — o nome em inglês, para quem já conhece a palavra."},
  {"h3": "As duas linhas, e as duas estão certas"},
  {"p": "É a confusão mais comum ao ler uma pilha:"},
  {"table": {"head": ["Campo", "O que é"], "rows": [["`e.line`", "onde o erro **nasceu**"], ["`quadro[\"line\"]`", "onde a **chamada** foi feita"]]}},
  { code: `monitor:
    media([])            // ← quadro["line"] aponta para cá
handle Error as e:
    assert e.line is 22  // ← dentro de 'media', no 'yield'
    assert e.pilha[0]["line"] bigger e.line`, lang: 'df' },
  {"p": "Números diferentes, de propósito. Para **consertar** você quer o primeiro; para entender **por que** aquela ação foi chamada com aquele argumento, o segundo."},
  {"p": "Um erro numa ação declarada num arquivo e chamada de outro já reportou a linha certa com o **nome do arquivo errado** — e o trecho desenhado embaixo da seta vinha do arquivo de quem chamou. Isso manda a pessoa depurar o arquivo errado, e é o pior tipo de mensagem de erro: confiante e errada."},
  {"h3": "`handle RuntimeError` não pega um `trigger`"},
  {"p": "A armadilha 18, e ela aparece neste exercício de propósito:"},
  { code: `action nivel1():
    monitor:
        yield nivel2()
    handle RuntimeError:
        yield "nao passa por aqui"      // nunca roda`, lang: 'df' },
  {"p": "`trigger` levanta `TriggerError`. Para pegar qualquer coisa, `handle Error`. Um `handle` do tipo errado é invisível: o código parece tratar o erro, e o erro passa por cima dele."},
  {"h3": "`defer` mostra sem sujar o caminho de saída"},
  {"p": "Um `out` antes de cada `yield` precisa ser repetido em **cada** saída da ação — e a que você esquecer é justamente a que dá errado."},
  { code: `action classificar(n):
    defer:
        saidas.append($"classificar({n}) saiu")
    given n smaller 0:
        yield "negativo"
    given n is 0:
        yield "zero"
    yield "positivo"`, lang: 'df' },
  {"p": "Três saídas diferentes, três registros, nenhum esquecido. `defer` abre **bloco** — não aceita expressão na mesma linha."},
  {"h3": "O depurador de verdade"},
  {"p": "Quando você tem terminal ou editor:"},
  { code: `dataforge debug conta.df              # para na primeira instrução
dataforge debug conta.df --parar=42   # só na linha 42`, lang: 'bash' },
  {"p": "Dentro dele: `p` passo, `n` próximo, `f` sai da ação, `c` continua, `vars` lista o escopo, `pilha` mostra quem chamou quem — e **qualquer expressão** é avaliada no quadro onde você parou."},
  {"p": "No VS Code, clique na margem e aperte **F5**. Os breakpoints, a pilha, as variáveis em árvore e o console de avaliação ficam no painel. O adaptador é `dataforge dap`, que fala Debug Adapter Protocol — o mesmo protocolo do Neovim, do Helix e do Emacs."},
  {"p": "Duas coisas que o depurador faz e que não são óbvias:"},
  {"list": ["**uma parada em comentário é movida** para a próxima linha executável,"]},
  {"p": "e o painel mostra onde ficou. Uma parada que nunca dispara, mostrada acesa, é o pior dos dois mundos;"},
  {"list": ["**as 228 embutidas não aparecem** no painel de variáveis. Elas vivem"]},
  {"p": "no escopo global, e despejá-las enterra as três variáveis que você parou para ver."},
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/31-qualidade/227_cobertura.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '227-cobertura-o-que-os-testes-nao-exercitaram', text: "227 · Cobertura: o que os testes NAO exercitaram", level: 2 as const }, { id: 'o-problema', text: "O problema", level: 3 as const }, { id: 'como-se-pede', text: "Como se pede", level: 3 as const }, { id: 'o-que-faz-o-numero-significar-algo', text: "O que faz o número significar algo", level: 3 as const }, { id: 'a-informacao-que-resolve', text: "A informação que resolve", level: 3 as const }, { id: 'o-que-ela-nao-mede', text: "O que ela NÃO mede", level: 3 as const }, { id: 'uma-advertencia', text: "Uma advertência", level: 3 as const }, { id: '228-instantaneo-banco-isolado-e-teste-instavel', text: "228 · Instantaneo, banco isolado e teste instavel", level: 2 as const }, { id: 'instantaneo', text: "Instantâneo", level: 3 as const }, { id: 'banco-que-se-desfaz', text: "Banco que se desfaz", level: 3 as const }, { id: 'teste-instavel', text: "Teste instável", level: 3 as const }, { id: 'armadilha', text: "Armadilha", level: 3 as const }, { id: 'continua-em', text: "Continua em", level: 3 as const }, { id: '229-depurar-sem-out', text: "229 · Depurar sem 'out'", level: 2 as const }, { id: 'por-que-nao-out', text: "Por que não `out`", level: 3 as const }, { id: 'o-que-este-exercicio-exercita', text: "O que este exercício exercita", level: 3 as const }, { id: 'epilha-quem-chamou-quem', text: "`e.pilha` — quem chamou quem", level: 3 as const }, { id: 'as-duas-linhas-e-as-duas-estao-certas', text: "As duas linhas, e as duas estão certas", level: 3 as const }, { id: 'handle-runtimeerror-nao-pega-um-trigger', text: "`handle RuntimeError` não pega um `trigger`", level: 3 as const }, { id: 'defer-mostra-sem-sujar-o-caminho-de-saida', text: "`defer` mostra sem sujar o caminho de saída", level: 3 as const }, { id: 'o-depurador-de-verdade', text: "O depurador de verdade", level: 3 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"31 · Qualidade"}
      description={"3 exercícios: check, lint, cobertura e o que o CI cobra."}
      href={"/docs/exercicios/31-qualidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
