"""Um exemplo que RODA para cada palavra reservada.

Por que aqui
------------
O hover do editor dizia *o que* a palavra faz. Dizer é metade: quem está
aprendendo precisa ver **como se escreve**, e uma frase de dez palavras
não substitui três linhas de código.

Por que num arquivo só
----------------------
A mesma tabela alimenta o hover do LSP, o autocompletar e a página de
palavras reservadas do site. Já esteve escrita em dois lugares — e os
dois divergiram.

Por que eles precisam rodar
---------------------------
`tests/test_exemplos_palavras.py` executa **cada um**. Um exemplo de
documentação que não compila é pior que nenhum: ele ensina errado, e a
pessoa passa meia hora achando que o erro é dela.
"""

#: Palavra → (o que faz, exemplo que roda).
#:
#: O exemplo é autocontido de propósito: quem copia do hover cola num
#: arquivo vazio e vê funcionar.
PALAVRAS = {
    # ── Condicional ──
    "given": (
        "condicional — e o ternário, quando usado em expressão",
        'x := 10\ngiven x bigger 5:\n    out "grande"\notherwise:\n    out "pequeno"\n\n'
        'rotulo := "par" given x % 2 is 0 otherwise "impar"'),
    "orif": (
        "senão-se, dentro de um 'given'",
        'nota := 7\ngiven nota bigger_eq 9:\n    out "otimo"\norif nota bigger_eq 7:\n'
        '    out "bom"\notherwise:\n    out "revisar"'),
    "otherwise": (
        "o ramo final de um 'given', ou o 'else' do ternário",
        'given no:\n    out "nunca"\notherwise:\n    out "sempre"'),

    # ── Laços ──
    "cycle": (
        "laço — por faixa ou por coleção. A faixa é INCLUSIVA nos dois extremos",
        'cycle i from 1 to 3:\n    out i\n\ncycle nome in ["ana", "bru"]:\n    out nome'),
    "persist": (
        "laço enquanto a condição valer (while)",
        'n := 3\npersist n bigger 0:\n    out n\n    n -= 1'),
    "perform": (
        "roda uma vez antes de testar (do..while)",
        'n := 0\nperform:\n    out $"rodou com n={n}"\n    n += 1\npersist n smaller 2'),
    "halt": ("sai do laço",
             'cycle i from 1 to 10:\n    given i is 3:\n        halt\n    out i'),
    "skip": ("pula para a próxima volta",
             'cycle i from 1 to 5:\n    given i % 2 is 0:\n        skip\n    out i'),
    "step": ("o passo do 'cycle from … to'",
             'cycle i from 0 to 10 step 5:\n    out i'),
    "to": ("o fim da faixa do 'cycle', inclusive",
           'cycle i from 1 to 3:\n    out i'),
    "from": ("o início da faixa, ou a origem de um 'adopt' seletivo",
             'cycle i from 5 to 7:\n    out i\n\nadopt {sqrt} from Arcane.Math\nout sqrt(16)'),

    # ── Ações ──
    "action": ("declara uma ação",
               'action somar(a, b):\n    yield a + b\n\nout somar(2, 3)'),
    "yield": ("devolve e ENCERRA a ação — não é o 'yield' do Python",
              'action primeiro(xs):\n    cycle x in xs:\n        yield x\n\n'
              'out primeiro([7, 8, 9])'),
    "emit": ("produz um item sem encerrar — só dentro de 'stream action'",
             'stream action contar(ate):\n    cycle i from 1 to ate:\n        emit i\n\n'
             'out contar(4).to_cluster()'),
    "stream": ("generator preguiçoso, inclusive infinito",
               'stream action fib():\n    a := 0\n    b := 1\n    persist yes:\n'
               '        emit a\n        a, b := b, a + b\n\nout fib().take(6)'),
    "lambda": ("ação anônima, nas duas formas",
               'dobro := lambda x: x * 2\nsoma := lambda a, b => a + b\n'
               'out dobro(21), soma(1, 2)'),
    "async": ("a chamada COMEÇA o trabalho numa thread e devolve a tarefa",
              'async action buscar(n):\n    yield n * 10\n\n'
              'tarefas := [buscar(n) cycle n in [1, 2, 3]]\nout await tarefas'),
    "await": ("espera a tarefa terminar e entrega o valor",
              'async action dobro(n):\n    yield n * 2\n\nout await dobro(21)'),

    # ── Objetos ──
    "blueprint": ("declara uma classe, com campos no cabeçalho",
                  'blueprint Ponto(x, y):\n    action norma():\n'
                  '        yield sqrt(self.x ** 2 + self.y ** 2)\n\n'
                  'out (spawn Ponto(3, 4)).norma()'),
    "spawn": ("cria uma instância de um blueprint",
              'blueprint Caixa(nome):\n    action rotulo():\n        yield self.nome\n\n'
              'c := spawn Caixa("livros")\nout c.rotulo()'),
    "record": ("estrutura IMUTÁVEL, com igualdade estrutural",
               'record Ponto:\n    x: Integer\n    y: Integer\n\n'
               'p := Ponto(1, 2)\nout p, p with {"y": 9}, p is Ponto(1, 2)'),
    "enum": ("conjunto fechado de valores",
             'enum Status:\n    Ativo\n    Inativo := "off"\n\n'
             'out Status.Ativo, Status.Inativo.value'),
    "trait": ("contrato de métodos que um blueprint promete ter",
              'trait Area:\n    action area()\n\n'
              'blueprint Quadrado(lado) with Area:\n    action area():\n'
              '        yield self.lado ** 2\n\nout (spawn Quadrado(3)).area()'),
    "extends": ("herança",
                'blueprint Animal:\n    action som():\n        yield "?"\n\n'
                'blueprint Cao extends Animal:\n    action som():\n        yield "au"\n\n'
                'out (spawn Cao()).som()'),
    "self": ("a instância, dentro de um método — sempre explícito",
             'blueprint Contador(n):\n    action mais():\n        self.n += 1\n'
             '        yield self.n\n\nc := spawn Contador(0)\nout c.mais(), c.mais()'),
    "root": ("o método da mãe, quando a filha o substitui",
             'blueprint Base:\n    action nome():\n        yield "base"\n\n'
             'blueprint Filha extends Base:\n    action nome():\n'
             '        yield root.nome() + "+filha"\n\nout (spawn Filha()).nome()'),
    "static": ("membro que pertence ao blueprint, não à instância",
               'blueprint Config:\n    static padrao := "claro"\n\nout Config.padrao'),
    "private": ("só dentro do próprio blueprint",
                'blueprint Conta(saldo):\n    private action taxa():\n        yield 0.05\n\n'
                '    action cobrar():\n        yield self.saldo * self.taxa()\n\n'
                'out (spawn Conta(100.0)).cobrar()'),
    "protected": ("no próprio blueprint e nos herdeiros",
                  'blueprint Base:\n    protected action ajudar():\n        yield "ok"\n\n'
                  'blueprint Filha extends Base:\n    action usar():\n'
                  '        yield self.ajudar()\n\nout (spawn Filha()).usar()'),
    "final": ("método que a filha não pode substituir",
              'blueprint Base:\n    final action id():\n        yield 1\n\n'
              'out (spawn Base()).id()'),
    "abstract": ("blueprint que não se instancia; a filha completa",
                 'abstract blueprint Forma:\n    action area()\n\n'
                 'blueprint Circulo(r) extends Forma:\n    action area():\n'
                 '        yield 3.14159 * self.r ** 2\n\nout (spawn Circulo(2.0)).area()'),
    "get": ("propriedade de leitura, usada sem parênteses",
            'blueprint Retangulo(largura, altura):\n    get area():\n'
            '        yield self.largura * self.altura\n\n'
            'out (spawn Retangulo(3, 4)).area'),
    "set": ("propriedade de escrita — roda ao atribuir",
            'blueprint Termometro:\n    get c():\n        yield self._c ?? 0\n'
            '    set c(v):\n        self._c := v\n\n'
            't := spawn Termometro()\nt.c := 25\nout t.c'),

    # ── Pattern matching ──
    "match": ("casa por ESTRUTURA, não só por valor",
              'valor := [1, 2]\nmatch valor:\n    point [a, b]:\n        out $"par {a},{b}"\n'
              '    point Integer as n:\n        out $"numero {n}"\n    default:\n'
              '        out "outro"'),
    "point": ("um caso do 'match' — do específico ao geral",
              'match 7:\n    point 0:\n        out "zero"\n    point Integer as n:\n'
              '        out $"inteiro {n}"'),
    "when": ("guarda de um 'point'",
             'match 150:\n    point Integer as n when n bigger 100:\n        out "grande"\n'
             '    default:\n        out "normal"'),
    "default": ("o caso que pega o resto",
                'match "x":\n    point 1:\n        out "um"\n    default:\n        out "outro"'),

    # ── Erros ──
    "monitor": ("tenta — e 'monitor' sozinho NÃO engole o erro",
                'monitor:\n    trigger "falhou"\nhandle e:\n    out e.message'),
    "handle": ("captura por TIPO, comparando por herança",
               'monitor:\n    x := 1 / 0\nhandle DivisionByZeroError as e:\n    out e.type'),
    "ensure": ("roda sempre, com erro ou sem",
               'monitor:\n    out "tentando"\nensure:\n    out "sempre roda"'),
    "trigger": ("levanta um erro — sempre TriggerError, com uma mensagem",
                'monitor:\n    trigger "sem saldo"\nhandle Error as e:\n    out e.message'),
    "defer": ("adia até a saída da AÇÃO, mesmo com erro",
              'action processar():\n    defer:\n        out "limpou"\n    out "trabalhou"\n'
              '    yield "feito"\n\nout processar()'),
    "retry": ("repete a tentativa quando ela falha",
              'tentativas := 0\naction instavel():\n    tentativas += 1\n'
              '    given tentativas smaller 3:\n        trigger "ainda nao"\n    yield "ok"\n\n'
              'retry 5:\n    r := instavel()\nout r, tentativas'),
    "guard": ("sai cedo quando a condição NÃO vale",
              'action dividir(a, b):\n    guard b isnt 0 otherwise:\n'
              '        yield void\n    yield a / b\n\nout dividir(10, 2), dividir(1, 0)'),
    "recover": ("o que fazer quando o 'retry' esgota as tentativas",
                'tentativas := 0\naction instavel():\n    tentativas += 1\n'
                '    trigger "indisponivel"\n\n'
                'retry 3:\n    instavel()\nrecover e:\n'
                '    out $"desisti apos {tentativas}: {e.message}"'),
    "propagate": ("repassa para quem chamou o erro que se acabou de pegar",
                  'action f():\n    monitor:\n        trigger "falhou"\n'
                  '    handle e:\n        propagate e\n\n'
                  'monitor:\n    f()\nhandle e:\n    out $"chegou aqui: {e.message}"'),
    "assert": ("cobra uma verdade, com mensagem",
               'x := 42\nassert x is 42, "x devia ser 42"\nout "passou"'),
    "validate": ("cobra uma condição — como 'assert', mas para dado de entrada",
                 'idade := 30\nvalidate idade bigger 0, "idade precisa ser positiva"\n'
                 'out "idade aceita"'),
    "sift": ("filtra — o 'filter'",
             'out [1, 2, 3, 4, 5, 6] >> sift n: n % 2 is 0'),
    "morph": ("transforma — o 'map'",
              'out [1, 2, 3] >> morph n: n * 10'),
    "distill": ("reduz — e o valor inicial vem DEPOIS do corpo",
                'out [1, 2, 3, 4] >> distill acumulado, v: acumulado + v 0'),

    # ── Módulos ──
    "adopt": ("importa — módulo inteiro, seletivo, ou do Python",
              'adopt Arcane.Math as M\nadopt Arcane.Math.{floor}\n'
              'out M.sqrt(16), floor(3.9)'),
    "relay": ("exporta do arquivo atual",
              'action somar(a, b):\n    yield a + b\n\nrelay somar'),
    "as": ("dá um apelido ao que se importa, ou ao erro capturado",
           'adopt Arcane.Math as M\nout M.PI'),

    # ── Valores e operadores ──
    "steady": ("constante — reatribuir é erro",
               'steady PI := 3.14159\nout PI'),
    "shadow": ("declara uma cópia local, escondendo a de fora de propósito",
               'x := 1\naction f():\n    shadow x := 99\n    yield x\n\nout f(), x'),
    "yes": ("verdadeiro", 'out yes, typeof(yes)'),
    "no": ("falso — e é palavra reservada, cuidado ao nomear em português",
           'out no, not no'),
    "void": ("ausência de valor", 'out void, void ?? "padrao"'),
    "is": ("igualdade — o '==' de outras linguagens",
           'out 2 + 2 is 4, "a" is "a"'),
    "isnt": ("diferença", 'out 1 isnt 2'),
    "bigger": ("maior que", 'out 5 bigger 3'),
    "bigger_eq": ("maior ou igual", 'out 5 bigger_eq 5'),
    "smaller": ("menor que", 'out 3 smaller 5'),
    "smaller_eq": ("menor ou igual", 'out 3 smaller_eq 3'),
    "and": ("e — devolve o VALOR, não um booleano",
            'out yes and "segundo", 0 and 9'),
    "or": ("ou — devolve o primeiro verdadeiro",
           'out "" or "padrao", "primeiro" or "segundo"'),
    "not": ("negação", 'out not yes, not 0'),
    "in": ("pertence a — e também lê da entrada",
           'out 2 in [1, 2, 3], "a" in {"a": 1}'),
    "typeof": ("o tipo, no vocabulário da linguagem",
               'out typeof(1), typeof("x"), typeof([1]), typeof({"a": 1})'),
    "cast": ("converte explicitamente",
             'out cast "42" as Integer, cast 3.9 as Integer'),
    "delete": ("remove uma chave de um vault",
               'v := {"a": 1, "b": 2}\ndelete v["a"]\nout v'),
    "out": ("imprime, separando os valores por espaço",
            'out "ola", 42, [1, 2]'),
    "inspect": ("imprime mostrando o TIPO junto — para depurar",
                'x := [1, 2]\ninspect x'),
    "thread": ("roda o bloco numa thread",
               'adopt Arcane.Time as T\nresultados := []\nthread:\n'
               '    resultados.append(1)\nwait 50\nout len(resultados)'),
    "channel": ("fila com trava, para passar valor entre threads",
                'channel fila\nfila.send("oi")\nout fila.receive()'),
    "parallel": ("roda CADA INSTRUÇÃO do bloco numa thread",
                 'saidas := []\nparallel:\n    saidas.append(1)\n    saidas.append(2)\n'
                 'wait 80\nout len(saidas)'),
    "wait": ("dorme pelo número de milissegundos",
             'wait 10\nout "acordou"'),
    "pulse": ("dispara um evento nomeado, com dado opcional",
              'pulse "pedido.criado", {"id": 7}\nout "disparado"'),
    "observe": ("itera uma fonte reagindo a cada item",
                'observe x in [1, 2, 3]:\n    out x'),

    # ── Dados ──
    "frame": ("tabela de verdade, do Arcane.Analytics",
              't := frame [{"a": 1, "b": 2}, {"a": 3, "b": 4}]\nout t.shape()'),
    "train": ("treina um modelo do Arcane.Cortex",
              'dados := [{"x": 1.0, "y": 2.0}, {"x": 2.0, "y": 4.0}]\n'
              'm := train "linear" using {"linhas": dados, "alvo": "y",\n'
              '                           "colunas": ["x"]}\n'
              'out predict m using [{"x": 3.0}]'),
    "predict": ("prevê com um modelo treinado, ou com uma ação sua",
                'action meu(linhas):\n    yield [l["x"] * 2 cycle l in linhas]\n\n'
                'out predict meu using [{"x": 21}]'),
    "using": ("liga o 'train'/'predict' aos seus argumentos",
              'action f(linhas):\n    yield len(linhas)\n\nout predict f using [{"a": 1}]'),
    "forge": ("sinônimo de 'spawn' — cria uma instância",
              'blueprint Caixa(nome):\n    action rotulo():\n        yield self.nome\n\n'
              'c := forge Caixa("livros")\nout c.rotulo()'),
    "with": ("copia um record trocando campos — records são imutáveis",
             'record Ponto:\n    x: Integer\n    y: Integer\n\n'
             'p := Ponto(1, 2)\nout p with {"y": 9}, p'),
    "mark": ("aplica um decorador à ação seguinte",
             'action dobrar(f):\n    yield lambda x: f(x) * 2\n\n'
             'mark @dobrar\naction valor(x):\n    yield x\n\nout valor(21)'),
    # ── Kiln: as onze palavras do framework web ──
    #
    # Elas sao CONTEXTUAIS: o parser as reconhece pelo texto, e so onde
    # fazem sentido. Por isso nao estao em 'KEYWORDS' — e por isso
    # escaparam da trava de cobertura por muito tempo, deixando o hover
    # muda justamente sobre o codigo web, que e onde mais gente comeca.
    #
    # Nenhum exemplo SOBE um servidor: 'server' monta e 'ignite' acende,
    # e os exemplos param no primeiro. 'Kiln.test' exercita a rota sem
    # abrir socket, que e o que os torna executaveis num teste.
    "server": (
        "declara a aplicacao web — monta, e nao sobe",
        'adopt Kiln\n\nserver site on 0:\n    route GET "/":\n'
        '        respond "oi"\n\nout Kiln.test(site, "GET", "/")["body"]'),
    "route": (
        "declara uma rota: metodo, caminho e o que responder",
        'adopt Kiln\n\nserver api on 0:\n    route GET "/soma/:a/:b":\n'
        '        respond json {"total": int(params["a"]) + int(params["b"])}\n\n'
        'out Kiln.test(api, "GET", "/soma/2/3")["body"]["total"]'),
    "respond": (
        "envia a resposta e encerra a rota, como 'yield' encerra uma acao",
        'adopt Kiln\n\nserver api on 0:\n    route GET "/texto":\n'
        '        respond "puro"\n    route GET "/dados":\n'
        '        respond json {"ok": yes}\n    route GET "/pagina":\n'
        '        respond html "<h1>oi</h1>"\n\n'
        'out Kiln.test(api, "GET", "/dados")["body"]["ok"]'),
    "render": (
        "desenha um template da pasta de 'views', com os dados do 'with'",
        'adopt Kiln\nadopt Arcane.IO as IO\nadopt Arcane.OS as OS\n\n'
        'pasta := IO.join(OS.temp_dir(), "df-render-exemplo")\n'
        'IO.mkdir(pasta)\n'
        'IO.write_file(IO.join(pasta, "oi.html"), "<h1>{titulo}</h1>")\n\n'
        'server site on 0:\n    views pasta\n    route GET "/":\n'
        '        render "oi.html" with {"titulo": "Forja"}\n\n'
        'out Kiln.test(site, "GET", "/")["body"]'),
    "views": (
        "diz de qual pasta o 'render' le os templates",
        'adopt Kiln\nadopt Arcane.IO as IO\nadopt Arcane.OS as OS\n\n'
        'pasta := IO.join(OS.temp_dir(), "df-views-exemplo")\n'
        'IO.mkdir(pasta)\n'
        'IO.write_file(IO.join(pasta, "p.html"), "<p>{q}</p>")\n\n'
        'server site on 0:\n    views pasta\n    route GET "/":\n'
        '        render "p.html" with {"q": "pronto"}\n\n'
        'out Kiln.test(site, "GET", "/")["body"]'),
    "redirect": (
        "manda o visitante para outro caminho — 302 por padrao",
        'adopt Kiln\n\nserver site on 0:\n    route GET "/antigo":\n'
        '        redirect "/novo"\n    route GET "/novo":\n'
        '        respond "cheguei"\n\n'
        'r := Kiln.test(site, "GET", "/antigo")\n'
        'out r["status"], r["headers"]["Location"]'),
    "middleware": (
        "roda ANTES de toda rota — autenticacao, limite, log",
        'adopt Kiln\n\nserver api on 0:\n    middleware Kiln.logger()\n'
        '    route GET "/":\n        respond "passou"\n\n'
        'out Kiln.test(api, "GET", "/")["body"]'),
    "after": (
        "roda DEPOIS da rota, com a resposta pronta em maos",
        'adopt Kiln\n\naction marcar(req, res):\n'
        '    res["headers"]["X-Forja"] := "1"\n    yield res\n\n'
        'server api on 0:\n    after marcar\n    route GET "/":\n'
        '        respond "ok"\n\n'
        'out Kiln.test(api, "GET", "/")["status"]'),
    "mount": (
        "junta outro 'server' sob um prefixo de caminho",
        'adopt Kiln\n\nserver interno on 0:\n    route GET "/saude":\n'
        '        respond "viva"\n\nserver principal on 0:\n'
        '    mount interno at "/admin"\n    route GET "/":\n'
        '        respond "raiz"\n\n'
        'out Kiln.test(principal, "GET", "/admin/saude")["body"]'),
    "assets": (
        "serve arquivos de uma pasta sob um caminho publico",
        'adopt Kiln\nadopt Arcane.IO as IO\nadopt Arcane.OS as OS\n\n'
        'pasta := IO.join(OS.temp_dir(), "df-assets-exemplo")\n'
        'IO.mkdir(pasta)\n'
        'IO.write_file(IO.join(pasta, "e.css"), "body{margin:0}")\n\n'
        'server site on 0:\n    assets "/static" from pasta\n'
        '    route GET "/":\n        respond "raiz"\n\n'
        'out Kiln.test(site, "GET", "/static/e.css")["status"]'),
    "ignite": (
        "acende o forno: e ele que abre o socket e fica atendendo",
        'adopt Kiln\n\nserver site on 0:\n    route GET "/":\n'
        '        respond "oi"\n\n'
        '// O exemplo para aqui de proposito: \'ignite\' BLOQUEIA, e um\n'
        '// exemplo que nunca termina nao serve de exemplo. Troque o\n'
        '// \'no\' por \'yes\' e o servidor sobe de verdade.\n'
        'given no:\n    ignite site at "0.0.0.0" on 8080\n\n'
        'out Kiln.test(site, "GET", "/")["body"]'),

    # ── Dois modificadores de blueprint ──
    "operator": (
        "sobrecarrega um operador para o seu tipo",
        'blueprint Dinheiro(centavos):\n    operator + (outro):\n'
        '        yield spawn Dinheiro(self.centavos + outro.centavos)\n\n'
        'total := spawn Dinheiro(150) + spawn Dinheiro(250)\n'
        'out total.centavos'),
    "slots": (
        "fecha a lista de campos: o que nao esta ali nao pode ser criado",
        'blueprint Ponto:\n    slots x, y\n    action setup():\n'
        '        self.x := 0\n        self.y := 0\n\n'
        'p := spawn Ponto()\np.x := 3\nout p.x\n\n'
        'monitor:\n    p.z := 9\nhandle Error as e:\n    out "recusou z"'),
}
