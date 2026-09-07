#!/usr/bin/env python3
"""
O catálogo de problemas de prática do painel.

Cada problema traz enunciado, exemplos, casos de teste e uma solução de
referência **em DataForge**. O script `scripts/gerar_problemas.py` roda
todas as soluções contra todos os casos antes de publicar: um problema
cuja própria solução não passa é um problema quebrado, e descobrir isso
pelo usuário é tarde demais.

A assinatura é a ação que o usuário precisa escrever. O corretor chama
`resolver(...)` com cada entrada e compara com a saída esperada.
"""

PROBLEMAS = [
    # ── Fáceis: fundamentos ──────────────────────────────────
    {
        "slug": "soma-dois",
        "titulo": "Soma de dois números",
        "dificuldade": "facil",
        "categoria": "fundamentos",
        "conceitos": ["acoes", "aritmetica"],
        "enunciado":
            "Escreva a ação `resolver(a, b)` que devolve a soma de dois "
            "inteiros.\n\nÉ o primeiro problema: serve para você conhecer o "
            "editor, o botão de rodar e o formato da resposta.",
        "assinatura": "action resolver(a, b):",
        "exemplos": [
            {"entrada": "a = 2, b = 3", "saida": "5"},
            {"entrada": "a = -1, b = 1", "saida": "0"},
        ],
        "dicas": [
            "`yield` devolve o valor e encerra a ação.",
            "A soma é `a + b` — sem mistério.",
        ],
        "casos": [
            {"entrada": [2, 3], "saida": 5},
            {"entrada": [-1, 1], "saida": 0},
            {"entrada": [0, 0], "saida": 0},
            {"entrada": [1000000, 1], "saida": 1000001},
            {"entrada": [-50, -50], "saida": -100},
        ],
        "solucao": "action resolver(a, b):\n    yield a + b",
    },
    {
        "slug": "maior-da-lista",
        "titulo": "Maior da lista",
        "dificuldade": "facil",
        "categoria": "colecoes",
        "conceitos": ["cycle", "comparacao"],
        "enunciado":
            "Devolva o maior número de um cluster.\n\nA lista nunca vem "
            "vazia. Resolva com um `cycle`, não com a função `max` — o "
            "objetivo é praticar o laço.",
        "assinatura": "action resolver(nums):",
        "exemplos": [
            {"entrada": "nums = [3, 7, 2]", "saida": "7"},
            {"entrada": "nums = [-5, -2, -9]", "saida": "-2"},
        ],
        "dicas": [
            "Comece assumindo que o primeiro é o maior.",
            "`bigger` compara: `given n bigger maior:`",
        ],
        "casos": [
            {"entrada": [[3, 7, 2]], "saida": 7},
            {"entrada": [[-5, -2, -9]], "saida": -2},
            {"entrada": [[42]], "saida": 42},
            {"entrada": [[1, 1, 1]], "saida": 1},
            {"entrada": [[0, 100, -100, 50]], "saida": 100},
        ],
        "solucao":
            "action resolver(nums):\n"
            "    maior := nums[0]\n"
            "    cycle n in nums:\n"
            "        given n bigger maior:\n"
            "            maior := n\n"
            "    yield maior",
    },
    {
        "slug": "inverter-texto",
        "titulo": "Inverter um texto",
        "dificuldade": "facil",
        "categoria": "textos",
        "conceitos": ["fatiamento", "textos"],
        "enunciado":
            "Devolva o texto de trás para frente.\n\nO DataForge fatia com "
            "passo negativo, como Python.",
        "assinatura": "action resolver(texto):",
        "exemplos": [
            {"entrada": 'texto = "forja"', "saida": '"ajrof"'},
            {"entrada": 'texto = "ana"', "saida": '"ana"'},
        ],
        "dicas": ["`texto[::-1]` inverte em um passo."],
        "casos": [
            {"entrada": ["forja"], "saida": "ajrof"},
            {"entrada": ["ana"], "saida": "ana"},
            {"entrada": [""], "saida": ""},
            {"entrada": ["a"], "saida": "a"},
            {"entrada": ["DataForge"], "saida": "egroFataD"},
        ],
        "solucao": "action resolver(texto):\n    yield texto[::-1]",
    },
    {
        "slug": "par-ou-impar",
        "titulo": "Par ou ímpar",
        "dificuldade": "facil",
        "categoria": "fundamentos",
        "conceitos": ["condicionais", "resto"],
        "enunciado":
            'Devolva "par" ou "impar" conforme o número.\n\nZero é par.',
        "assinatura": "action resolver(n):",
        "exemplos": [
            {"entrada": "n = 4", "saida": '"par"'},
            {"entrada": "n = 7", "saida": '"impar"'},
        ],
        "dicas": [
            "`%` dá o resto da divisão.",
            'O ternário cabe numa linha: `"par" given n % 2 is 0 otherwise "impar"`',
        ],
        "casos": [
            {"entrada": [4], "saida": "par"},
            {"entrada": [7], "saida": "impar"},
            {"entrada": [0], "saida": "par"},
            {"entrada": [-3], "saida": "impar"},
            {"entrada": [-8], "saida": "par"},
        ],
        "solucao":
            "action resolver(n):\n"
            '    yield "par" given n % 2 is 0 otherwise "impar"',
    },
    {
        "slug": "contar-vogais",
        "titulo": "Contar vogais",
        "dificuldade": "facil",
        "categoria": "textos",
        "conceitos": ["cycle", "in", "textos"],
        "enunciado":
            "Conte quantas vogais há no texto.\n\nSó minúsculas sem acento: "
            "a, e, i, o, u.",
        "assinatura": "action resolver(texto):",
        "exemplos": [
            {"entrada": 'texto = "forja"', "saida": "2"},
            {"entrada": 'texto = "xyz"', "saida": "0"},
        ],
        "dicas": [
            "`c in \"aeiou\"` testa se o caractere é vogal.",
            "Um `cycle` sobre o texto passa por cada caractere.",
        ],
        "casos": [
            {"entrada": ["forja"], "saida": 2},
            {"entrada": ["xyz"], "saida": 0},
            {"entrada": [""], "saida": 0},
            {"entrada": ["aeiou"], "saida": 5},
            {"entrada": ["dataforge"], "saida": 4},
        ],
        "solucao":
            "action resolver(texto):\n"
            "    total := 0\n"
            "    cycle c in texto:\n"
            '        given c in "aeiou":\n'
            "            total += 1\n"
            "    yield total",
    },
    {
        "slug": "fizzbuzz",
        "titulo": "FizzBuzz",
        "dificuldade": "facil",
        "categoria": "fundamentos",
        "conceitos": ["condicionais", "cycle", "colecoes"],
        "enunciado":
            'Devolva um cluster de 1 a n onde múltiplos de 3 viram "Fizz", '
            'de 5 viram "Buzz", e de ambos viram "FizzBuzz". Os demais '
            "entram como número mesmo.\n\nO clássico. A ordem dos testes é "
            "o que separa quem acerta de quem quase acerta.",
        "assinatura": "action resolver(n):",
        "exemplos": [
            {"entrada": "n = 5", "saida": '[1, 2, "Fizz", 4, "Buzz"]'},
        ],
        "dicas": [
            "Teste 15 primeiro — ou 3 e 5 juntos.",
            "`cycle i from 1 to n` é inclusivo nos dois extremos.",
        ],
        "casos": [
            {"entrada": [5], "saida": [1, 2, "Fizz", 4, "Buzz"]},
            {"entrada": [3], "saida": [1, 2, "Fizz"]},
            {"entrada": [15], "saida": [1, 2, "Fizz", 4, "Buzz", "Fizz", 7, 8,
                                        "Fizz", "Buzz", 11, "Fizz", 13, 14,
                                        "FizzBuzz"]},
            {"entrada": [1], "saida": [1]},
        ],
        "solucao":
            "action resolver(n):\n"
            "    saida := []\n"
            "    cycle i from 1 to n:\n"
            "        given i % 15 is 0:\n"
            '            saida.append("FizzBuzz")\n'
            "        orif i % 3 is 0:\n"
            '            saida.append("Fizz")\n'
            "        orif i % 5 is 0:\n"
            '            saida.append("Buzz")\n'
            "        otherwise:\n"
            "            saida.append(i)\n"
            "    yield saida",
    },

    # ── Médios ───────────────────────────────────────────────
    {
        "slug": "dois-numeros",
        "titulo": "Dois números que somam",
        "dificuldade": "medio",
        "categoria": "colecoes",
        "conceitos": ["vault", "busca"],
        "enunciado":
            "Dado um cluster e um alvo, devolva os índices dos dois números "
            "que somam o alvo.\n\nHá exatamente uma resposta, e nenhum "
            "elemento se usa duas vezes. Devolva os índices em ordem "
            "crescente.\n\nA solução ingênua compara todos com todos e custa "
            "n². Dá para fazer em uma passada.",
        "assinatura": "action resolver(nums, alvo):",
        "exemplos": [
            {"entrada": "nums = [2, 7, 11, 15], alvo = 9", "saida": "[0, 1]"},
            {"entrada": "nums = [3, 2, 4], alvo = 6", "saida": "[1, 2]"},
        ],
        "dicas": [
            "Enquanto percorre, guarde num vault o que já viu: valor → índice.",
            "Para cada número, o complemento é `alvo - n`. Já apareceu?",
        ],
        "casos": [
            {"entrada": [[2, 7, 11, 15], 9], "saida": [0, 1]},
            {"entrada": [[3, 2, 4], 6], "saida": [1, 2]},
            {"entrada": [[3, 3], 6], "saida": [0, 1]},
            {"entrada": [[-1, -2, -3, -4, -5], -8], "saida": [2, 4]},
            {"entrada": [[0, 4, 3, 0], 0], "saida": [0, 3]},
        ],
        "solucao":
            "action resolver(nums, alvo):\n"
            "    vistos := {}\n"
            "    cycle i from 0 to len(nums) - 1:\n"
            "        falta := alvo - nums[i]\n"
            "        given falta in vistos:\n"
            "            yield [vistos[falta], i]\n"
            "        vistos[nums[i]] := i\n"
            "    yield []",
    },
    {
        "slug": "palindromo",
        "titulo": "É palíndromo?",
        "dificuldade": "medio",
        "categoria": "textos",
        "conceitos": ["textos", "normalizacao"],
        "enunciado":
            "Diga se o texto é um palíndromo, ignorando maiúsculas, espaços "
            "e pontuação.\n\nSó letras e dígitos contam.",
        "assinatura": "action resolver(texto):",
        "exemplos": [
            {"entrada": 'texto = "A man, a plan, a canal: Panama"', "saida": "yes"},
            {"entrada": 'texto = "corrida"', "saida": "no"},
        ],
        "dicas": [
            "Primeiro limpe: fique só com o que é letra ou dígito, em minúsculas.",
            "Depois compare o limpo com o limpo invertido.",
        ],
        "casos": [
            {"entrada": ["A man, a plan, a canal: Panama"], "saida": True},
            {"entrada": ["corrida"], "saida": False},
            {"entrada": [""], "saida": True},
            {"entrada": ["ab"], "saida": False},
            {"entrada": ["Socorram-me, subi no onibus em Marrocos"], "saida": True},
        ],
        "solucao":
            "action resolver(texto):\n"
            "    limpo := \"\"\n"
            "    cycle c in lower(texto):\n"
            "        given isalnum(c):\n"
            "            limpo += c\n"
            "    yield limpo is limpo[::-1]",
    },
    {
        "slug": "agrupar-anagramas",
        "titulo": "Agrupar anagramas",
        "dificuldade": "medio",
        "categoria": "colecoes",
        "conceitos": ["vault", "ordenacao"],
        "enunciado":
            "Agrupe as palavras que são anagramas entre si.\n\nDevolva os "
            "grupos ordenados: cada grupo com as palavras em ordem "
            "alfabética, e os grupos ordenados pela primeira palavra.",
        "assinatura": "action resolver(palavras):",
        "exemplos": [
            {"entrada": 'palavras = ["ovo", "voo", "sal"]',
             "saida": '[["ovo", "voo"], ["sal"]]'},
        ],
        "dicas": [
            "Duas palavras são anagramas quando têm as mesmas letras ordenadas: `join(\"\", sorted([c cycle c in p]))` dá a chave.",
            "Use isso como chave de um vault.",
        ],
        "casos": [
            {"entrada": [["ovo", "voo", "sal"]], "saida": [["ovo", "voo"], ["sal"]]},
            {"entrada": [["a"]], "saida": [["a"]]},
            {"entrada": [[]], "saida": []},
            {"entrada": [["amor", "roma", "ramo", "casa"]],
             "saida": [["amor", "ramo", "roma"], ["casa"]]},
        ],
        "solucao":
            "action resolver(palavras):\n"
            "    grupos := {}\n"
            "    cycle p in palavras:\n"
            '        chave := join("", sorted([c cycle c in p]))\n'
            "        given chave in grupos:\n"
            "            grupos[chave].append(p)\n"
            "        otherwise:\n"
            "            grupos[chave] := [p]\n"
            "    saida := []\n"
            "    cycle chave in grupos:\n"
            "        saida.append(sorted(grupos[chave]))\n"
            "    yield sorted(saida)",
    },
    {
        "slug": "fibonacci",
        "titulo": "Fibonacci",
        "dificuldade": "medio",
        "categoria": "recursao",
        "conceitos": ["iteracao", "generators"],
        "enunciado":
            "Devolva o n-ésimo número de Fibonacci, começando em "
            "F(0) = 0 e F(1) = 1.\n\nUma solução recursiva ingênua custa 2ⁿ "
            "e trava para n = 40. A iterativa resolve em n passos.",
        "assinatura": "action resolver(n):",
        "exemplos": [
            {"entrada": "n = 7", "saida": "13"},
            {"entrada": "n = 0", "saida": "0"},
        ],
        "dicas": [
            "Guarde só os dois últimos.",
            "`a, b := b, a + b` troca os dois de uma vez.",
        ],
        "casos": [
            {"entrada": [7], "saida": 13},
            {"entrada": [0], "saida": 0},
            {"entrada": [1], "saida": 1},
            {"entrada": [10], "saida": 55},
            {"entrada": [40], "saida": 102334155},
        ],
        "solucao":
            "action resolver(n):\n"
            "    a := 0\n"
            "    b := 1\n"
            "    cycle i from 1 to n:\n"
            "        a, b := b, a + b\n"
            "    yield a",
    },
    {
        "slug": "parenteses-balanceados",
        "titulo": "Parênteses balanceados",
        "dificuldade": "medio",
        "categoria": "estruturas",
        "conceitos": ["pilha", "vault"],
        "enunciado":
            "Diga se os delimitadores `()`, `[]` e `{}` estão balanceados e "
            "na ordem certa.\n\n`([)]` é inválido: fecha na ordem errada.",
        "assinatura": "action resolver(texto):",
        "exemplos": [
            {"entrada": 'texto = "({[]})"', "saida": "yes"},
            {"entrada": 'texto = "([)]"', "saida": "no"},
        ],
        "dicas": [
            "Uma pilha: empilhe ao abrir, desempilhe ao fechar.",
            "Se desempilhar e não bater, já deu errado.",
        ],
        "casos": [
            {"entrada": ["({[]})"], "saida": True},
            {"entrada": ["([)]"], "saida": False},
            {"entrada": [""], "saida": True},
            {"entrada": ["((("], "saida": False},
            {"entrada": [")("], "saida": False},
            {"entrada": ["{[()]}"], "saida": True},
        ],
        "solucao":
            "action resolver(texto):\n"
            '    pares := {")": "(", "]": "[", "}": "{"}\n'
            "    pilha := []\n"
            "    cycle c in texto:\n"
            '        given c in "([{":\n'
            "            pilha.append(c)\n"
            "        orif c in pares:\n"
            "            given len(pilha) is 0:\n"
            "                yield no\n"
            "            given pilha.pop() isnt pares[c]:\n"
            "                yield no\n"
            "    yield len(pilha) is 0",
    },
    {
        "slug": "maior-subsequencia",
        "titulo": "Maior soma contígua",
        "dificuldade": "medio",
        "categoria": "algoritmos",
        "conceitos": ["kadane", "programacao-dinamica"],
        "enunciado":
            "Encontre a maior soma de uma sublista contígua não vazia.\n\n"
            "Todos os números podem ser negativos — nesse caso, a resposta é "
            "o menos ruim deles.",
        "assinatura": "action resolver(nums):",
        "exemplos": [
            {"entrada": "nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]", "saida": "6"},
            {"entrada": "nums = [-1, -2]", "saida": "-1"},
        ],
        "dicas": [
            "Em cada posição, decida: estender a soma anterior ou recomeçar aqui?",
            "É o algoritmo de Kadane, e cabe em cinco linhas.",
        ],
        "casos": [
            {"entrada": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "saida": 6},
            {"entrada": [[-1, -2]], "saida": -1},
            {"entrada": [[5]], "saida": 5},
            {"entrada": [[1, 2, 3, 4]], "saida": 10},
            {"entrada": [[-5, -1, -3]], "saida": -1},
        ],
        "solucao":
            "action resolver(nums):\n"
            "    melhor := nums[0]\n"
            "    atual := nums[0]\n"
            "    cycle i from 1 to len(nums) - 1:\n"
            "        atual := max(nums[i], atual + nums[i])\n"
            "        melhor := max(melhor, atual)\n"
            "    yield melhor",
    },

    # ── Difíceis ─────────────────────────────────────────────
    {
        "slug": "mediana-dois-ordenados",
        "titulo": "Mediana de duas listas ordenadas",
        "dificuldade": "dificil",
        "categoria": "algoritmos",
        "conceitos": ["busca-binaria", "ordenacao"],
        "enunciado":
            "Dadas duas listas já ordenadas, devolva a mediana das duas "
            "juntas.\n\nSe o total for par, a mediana é a média dos dois do "
            "meio. Junte e ordene se quiser — mas a solução elegante não "
            "precisa juntar nada.",
        "assinatura": "action resolver(a, b):",
        "exemplos": [
            {"entrada": "a = [1, 3], b = [2]", "saida": "2.0"},
            {"entrada": "a = [1, 2], b = [3, 4]", "saida": "2.5"},
        ],
        "dicas": [
            "A saída é sempre Float, mesmo quando o valor é inteiro.",
            "Juntar e ordenar custa (n+m)·log(n+m) e passa nos testes.",
        ],
        "casos": [
            {"entrada": [[1, 3], [2]], "saida": 2.0},
            {"entrada": [[1, 2], [3, 4]], "saida": 2.5},
            {"entrada": [[], [1]], "saida": 1.0},
            {"entrada": [[0, 0], [0, 0]], "saida": 0.0},
            {"entrada": [[1, 2, 3, 4, 5], [6, 7, 8]], "saida": 4.5},
        ],
        "solucao":
            "action resolver(a, b):\n"
            "    todos := sorted([...a, ...b])\n"
            "    n := len(todos)\n"
            "    meio := n ~/ 2\n"
            "    given n % 2 is 1:\n"
            "        yield float(todos[meio])\n"
            "    yield (todos[meio - 1] + todos[meio]) / 2.0",
    },
    {
        "slug": "menor-janela",
        "titulo": "Menor janela que cobre",
        "dificuldade": "dificil",
        "categoria": "algoritmos",
        "conceitos": ["janela-deslizante", "vault"],
        "enunciado":
            "Encontre a menor sublista contígua de `texto` que contém todos "
            "os caracteres de `alvo`, contando repetições.\n\nSe não "
            'existir, devolva "".',
        "assinatura": "action resolver(texto, alvo):",
        "exemplos": [
            {"entrada": 'texto = "ADOBECODEBANC", alvo = "ABC"', "saida": '"BANC"'},
            {"entrada": 'texto = "a", alvo = "aa"', "saida": '""'},
        ],
        "dicas": [
            "Duas bordas que só avançam: a direita expande, a esquerda encolhe.",
            "Conte quantos caracteres do alvo ainda faltam, não compare vaults.",
        ],
        "casos": [
            {"entrada": ["ADOBECODEBANC", "ABC"], "saida": "BANC"},
            {"entrada": ["a", "aa"], "saida": ""},
            {"entrada": ["a", "a"], "saida": "a"},
            {"entrada": ["ab", "b"], "saida": "b"},
            {"entrada": ["aaflslflsldkalskaaa", "aaa"], "saida": "aaa"},
        ],
        "solucao":
            "action resolver(texto, alvo):\n"
            "    given len(alvo) is 0 or len(texto) smaller len(alvo):\n"
            '        yield ""\n'
            "    falta := {}\n"
            "    cycle c in alvo:\n"
            "        falta[c] := (falta[c] ?? 0) + 1\n"
            "    pendentes := len(alvo)\n"
            "    esquerda := 0\n"
            "    melhor_inicio := -1\n"
            "    melhor_tam := len(texto) + 1\n"
            "    cycle direita from 0 to len(texto) - 1:\n"
            "        c := texto[direita]\n"
            "        given c in falta:\n"
            "            given falta[c] bigger 0:\n"
            "                pendentes -= 1\n"
            "            falta[c] := falta[c] - 1\n"
            "        persist pendentes is 0:\n"
            "            given direita - esquerda + 1 smaller melhor_tam:\n"
            "                melhor_tam := direita - esquerda + 1\n"
            "                melhor_inicio := esquerda\n"
            "            saindo := texto[esquerda]\n"
            "            given saindo in falta:\n"
            "                falta[saindo] := falta[saindo] + 1\n"
            "                given falta[saindo] bigger 0:\n"
            "                    pendentes += 1\n"
            "            esquerda += 1\n"
            '    yield "" given melhor_inicio is -1 '
            "otherwise texto[melhor_inicio:melhor_inicio + melhor_tam]",
    },
    {
        "slug": "escadas",
        "titulo": "Subindo a escada",
        "dificuldade": "medio",
        "categoria": "recursao",
        "conceitos": ["programacao-dinamica"],
        "enunciado":
            "Você sobe 1 ou 2 degraus por vez. De quantas formas distintas "
            "dá para subir uma escada de n degraus?\n\nn = 0 tem uma forma: "
            "não subir.",
        "assinatura": "action resolver(n):",
        "exemplos": [
            {"entrada": "n = 3", "saida": "3"},
            {"entrada": "n = 4", "saida": "5"},
        ],
        "dicas": [
            "Para chegar ao degrau n, você veio do n-1 ou do n-2.",
            "É Fibonacci com outro nome.",
        ],
        "casos": [
            {"entrada": [3], "saida": 3},
            {"entrada": [4], "saida": 5},
            {"entrada": [0], "saida": 1},
            {"entrada": [1], "saida": 1},
            {"entrada": [30], "saida": 1346269},
        ],
        "solucao":
            "action resolver(n):\n"
            "    anterior := 1\n"
            "    atual := 1\n"
            "    cycle i from 1 to n:\n"
            "        anterior, atual := atual, anterior + atual\n"
            "    yield anterior",
    },
    {
        "slug": "rotacionar-lista",
        "titulo": "Rotacionar a lista",
        "dificuldade": "facil",
        "categoria": "colecoes",
        "conceitos": ["fatiamento", "resto"],
        "enunciado":
            "Rotacione o cluster k posições para a direita.\n\nk pode ser "
            "maior que o tamanho da lista.",
        "assinatura": "action resolver(nums, k):",
        "exemplos": [
            {"entrada": "nums = [1,2,3,4,5], k = 2", "saida": "[4, 5, 1, 2, 3]"},
        ],
        "dicas": [
            "`k % len(nums)` evita voltas inteiras à toa.",
            "Fatie em dois pedaços e junte na ordem invertida.",
        ],
        "casos": [
            {"entrada": [[1, 2, 3, 4, 5], 2], "saida": [4, 5, 1, 2, 3]},
            {"entrada": [[1, 2], 3], "saida": [2, 1]},
            {"entrada": [[1], 0], "saida": [1]},
            {"entrada": [[1, 2, 3], 3], "saida": [1, 2, 3]},
        ],
        "solucao":
            "action resolver(nums, k):\n"
            "    given len(nums) is 0:\n"
            "        yield []\n"
            "    corte := k % len(nums)\n"
            "    yield [...nums[len(nums) - corte:], ...nums[:len(nums) - corte]]",
    },
]
