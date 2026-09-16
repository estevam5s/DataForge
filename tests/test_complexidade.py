"""A analise de Big-O.

Um analisador que erra a classe e pior que nenhum: ele ensina errado, e
com confianca. Por isso quase todo teste aqui confere um algoritmo
CONHECIDO, cuja complexidade nao esta em disputa.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataforge.complexidade import (ESCALA, Ordem, analisar_fonte,  # noqa: E402
                                    para_json)


def ordem_de(fonte, nome):
    for r in analisar_fonte(fonte, "<teste>"):
        if r.nome == nome:
            return r
    raise AssertionError(f"'{nome}' nao foi analisada")


def tempo(fonte, nome):
    return ordem_de(fonte, nome).tempo.texto()


# ═══ A algebra ═════════════════════════════════════════════

def test_sequencia_fica_com_o_maior():
    """O(n) seguido de O(n^2) e O(n^2): o menor some para n grande."""
    assert Ordem.linear().maior(Ordem.quadratica()).texto() == "O(n^2)"
    assert Ordem.quadratica().maior(Ordem.linear()).texto() == "O(n^2)"


def test_aninhamento_multiplica():
    assert Ordem.linear().vezes(Ordem.linear()).texto() == "O(n^2)"
    assert Ordem.linear().vezes(Ordem.logaritmica()).texto() == "O(n log n)"
    assert Ordem.constante().vezes(Ordem.linear()).texto() == "O(n)"


def test_ordem_total_das_classes():
    """A ordem tem de bater com o crescimento real."""
    escada = [Ordem.constante(), Ordem.logaritmica(), Ordem.linear(),
              Ordem.linearitmica(), Ordem.quadratica(),
              Ordem.exponencial(), Ordem.fatorial()]
    pesos = [o._peso() for o in escada]
    assert pesos == sorted(pesos), pesos


def test_notacao():
    assert Ordem.constante().texto() == "O(1)"
    assert Ordem.logaritmica().texto() == "O(log n)"
    assert Ordem.linearitmica().texto() == "O(n log n)"
    assert Ordem(("polinomial"), 3, 0).texto() == "O(n^3)"
    assert Ordem.exponencial(3).texto() == "O(3^n)"


# ═══ Algoritmos conhecidos ═════════════════════════════════

@pytest.mark.parametrize("nome, esperado, fonte", [
    ("acesso", "O(1)", '''
action acesso(xs):
    yield xs[0] + xs[1]
'''),
    ("somar", "O(n)", '''
action somar(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total
'''),
    ("bolha", "O(n^2)", '''
action bolha(xs):
    cycle i in xs:
        cycle j in xs:
            given xs[i] bigger xs[j]:
                out i
'''),
    ("cubo", "O(n^3)", '''
action cubo(m):
    cycle a in m:
        cycle b in m:
            cycle c in m:
                out a
'''),
    ("binaria", "O(log n)", '''
action binaria(xs, alvo):
    baixo := 0
    alto := len(xs) - 1
    persist baixo smaller_eq alto:
        meio := (baixo + alto) ~/ 2
        given xs[meio] is alvo:
            yield meio
        orif xs[meio] smaller alvo:
            baixo := meio + 1
        otherwise:
            alto := meio - 1
    yield -1
'''),
    ("ordenar", "O(n log n)", '''
action ordenar(xs):
    yield sorted(xs)
'''),
    ("fib", "O(2^n)", '''
action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)
'''),
    ("fatorial", "O(n)", '''
action fatorial(n):
    given n smaller_eq 1:
        yield 1
    yield n * fatorial(n - 1)
'''),
])
def test_classe_de_algoritmo_conhecido(nome, esperado, fonte):
    assert tempo(fonte, nome) == esperado


def test_divisao_e_conquista_nao_e_exponencial():
    """merge sort e fibonacci ingenuo tem a MESMA forma: duas chamadas.

    O que os separa e a entrada — metade contra n-1. Confundir os dois
    e o erro mais caro que um analisador de complexidade pode cometer:
    ele condenaria todo algoritmo de divisao e conquista.
    """
    fonte = '''
action merge_sort(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    esquerda := merge_sort(xs[:meio])
    direita := merge_sort(xs[meio:])
    yield juntar(esquerda, direita)
'''
    assert tempo(fonte, "merge_sort") == "O(n log n)"


def test_compreensao_aninhada_e_quadratica():
    """Cabe numa linha, e nao parece um laco duplo."""
    fonte = '''
action pares(xs, ys):
    yield [[a, b] cycle a in xs cycle b in ys]
'''
    assert tempo(fonte, "pares") == "O(n^2)"


def test_in_sobre_cluster_dentro_de_laco_e_quadratico():
    """O O(n^2) mais comum que existe — e o mais facil de nao ver."""
    fonte = '''
action comuns(xs, ys):
    saida := []
    cycle x in xs:
        given x in ys:
            saida.append(x)
    yield saida
'''
    assert tempo(fonte, "comuns") == "O(n^2)"


def test_sorted_dentro_de_laco():
    """O laco esta a vista; o custo do sorted nao."""
    fonte = '''
action ruim(matriz):
    cycle linha in matriz:
        out sorted(linha)
'''
    assert tempo(fonte, "ruim") == "O(n^2 log n)"


def test_generator_tem_custo_por_item():
    """'persist yes' num generator e preguicoso, nao um laco infinito.

    Sem esta distincao, todo generator correto da linguagem seria
    reportado como indeterminado.
    """
    fonte = '''
stream action naturais():
    n := 0
    persist yes:
        emit n
        n += 1
'''
    r = ordem_de(fonte, "naturais")
    assert r.tempo.texto() == "O(1)"
    assert r.tipo == "stream action"


def test_laco_de_tamanho_fixo_e_constante():
    fonte = '''
action fixo():
    cycle i from 1 to 10:
        out i
'''
    assert tempo(fonte, "fixo") == "O(1)"


# ═══ Espaco ════════════════════════════════════════════════

def test_acumular_numa_colecao_e_linear_no_espaco():
    fonte = '''
action dobrar(xs):
    saida := []
    cycle x in xs:
        saida.append(x * 2)
    yield saida
'''
    assert ordem_de(fonte, "dobrar").espaco.texto() == "O(n)"


def test_somar_em_variavel_nao_gasta_espaco():
    fonte = '''
action somar(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total
'''
    assert ordem_de(fonte, "somar").espaco.texto() == "O(1)"


def test_recursao_gasta_pilha():
    """Mesmo sem alocar nada, a profundidade e memoria."""
    fonte = '''
action desce(n):
    given n smaller_eq 0:
        yield 0
    yield desce(n - 1)
'''
    assert ordem_de(fonte, "desce").espaco.texto() == "O(n)"


# ═══ O relatorio ═══════════════════════════════════════════

def test_o_motivo_acompanha_a_classe():
    """'O(n^2)' sozinho nao ajuda a melhorar nada."""
    fonte = '''
action pares(xs):
    cycle a in xs:
        cycle b in xs:
            out a
'''
    r = ordem_de(fonte, "pares")
    assert r.tempo.motivos, "sem motivo, o numero nao ensina nada"
    assert any("linha" in m for m in r.tempo.motivos)


def test_quadratico_avisa_e_sugere():
    fonte = '''
action pares(xs):
    cycle a in xs:
        cycle b in xs:
            out a
'''
    avisos = ordem_de(fonte, "pares").avisos
    assert avisos
    assert any("quadruplica" in a["texto"] for a in avisos)
    assert all(a["sugestao"] for a in avisos)


def test_exponencial_sugere_memoizacao():
    fonte = '''
action fib(n):
    given n smaller 2:
        yield n
    yield fib(n - 1) + fib(n - 2)
'''
    avisos = ordem_de(fonte, "fib").avisos
    assert any("memoiza" in a["sugestao"] for a in avisos)


def test_gravidade_separa_o_aceitavel_do_problema():
    assert Ordem.constante().gravidade() == 0
    assert Ordem.linear().gravidade() == 1
    assert Ordem.linearitmica().gravidade() == 1
    assert Ordem.quadratica().gravidade() == 2
    assert Ordem.exponencial().gravidade() == 3


def test_json_tem_o_que_o_editor_precisa():
    fonte = '''
action f(xs):
    cycle x in xs:
        out x
'''
    dados = para_json(analisar_fonte(fonte, "<t>"))
    assert "acoes" in dados and "pior" in dados
    acao = dados["acoes"][0]
    for chave in ("nome", "linha", "tempo", "espaco", "avisos"):
        assert chave in acao
    assert acao["tempo"]["notacao"] == "O(n)"


def test_escala_esta_ordenada_e_completa():
    assert len(ESCALA) >= 8
    for linha in ESCALA:
        for chave in ("notacao", "nome", "exemplo", "descricao",
                      "n10", "n1k", "n1m"):
            assert linha[chave], f"{linha['notacao']} sem {chave}"


# ═══ Robustez ══════════════════════════════════════════════

def test_analisa_todos_os_exercicios_sem_estourar():
    """200 arquivos reais: se a analise quebrar em algum, quebra em uso."""
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arquivos = glob.glob(os.path.join(raiz, "exercicios", "*", "*.df"))
    assert arquivos

    indeterminados = []
    for caminho in arquivos:
        with open(caminho, encoding="utf-8") as f:
            resultados = analisar_fonte(f.read(), caminho)
        for r in resultados:
            if r.tempo.familia == "desconhecido":
                indeterminados.append(f"{os.path.basename(caminho)}:{r.nome}")

    # Nao e erro haver algum: ha codigo cuja ordem nao da para provar.
    # E erro haver MUITOS — significaria que a deteccao esta cega.
    assert len(indeterminados) <= 3, indeterminados


def test_analisa_os_exemplos_sem_estourar():
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for caminho in glob.glob(os.path.join(raiz, "examples", "*.df")):
        with open(caminho, encoding="utf-8") as f:
            analisar_fonte(f.read(), caminho)


# ═══ O nome do arquivo vence o da tabela ═══════════════════

MERGE_SORT = '''
action intercalar(a, b):
    saida := []
    i := 0
    j := 0
    persist i smaller len(a) and j smaller len(b):
        given a[i] smaller_eq b[j]:
            saida.append(a[i])
            i += 1
        otherwise:
            saida.append(b[j])
            j += 1
    yield [...saida, ...a[i:], ...b[j:]]

action ordenar(xs):
    given len(xs) smaller_eq 1:
        yield xs
    meio := len(xs) ~/ 2
    yield intercalar(ordenar(xs[0:meio]), ordenar(xs[meio:]))
'''


def test_merge_sort_e_n_log_n_e_nao_n_log_quadrado():
    """O algoritmo mais conhecido da divisão e conquista.

    Ele saía como **O(n log^2 n)** porque a ação se chama `ordenar`, e
    `ordenar` está na tabela de custos dos embutidos como O(n log n): as
    duas chamadas recursivas cobravam o preço do embutido, e a regra da
    divisão e conquista multiplicava aquilo por log n de novo.

    Errar a classe do merge sort num analisador de Big-O é o pior lugar
    possível para errar — é o exemplo que todo mundo usa para conferir.
    """
    assert tempo(MERGE_SORT, "ordenar") == "O(n log n)"


def test_uma_acao_do_arquivo_vence_o_embutido_de_mesmo_nome():
    """`action unique(xs)` é a do arquivo, não a embutida.

    A tabela de custos é um atalho para o que a linguagem oferece; um
    nome DECLARADO no arquivo é o que vai ser chamado, e cobrar por ele o
    preço de outra coisa inventa um número.
    """
    fonte = ('action unique(xs):\n'
             '    yield xs[0]\n'
             'action usar(ys):\n'
             '    yield unique(ys)\n')
    assert tempo(fonte, "usar") == "O(1)"
    # E sem a declaração, o embutido continua valendo:
    assert tempo('action usar(ys):\n    yield unique(ys)\n', "usar") == "O(n)"


BUSCA_BINARIA_RECURSIVA = '''
action busca(xs, alvo, baixo, alto):
    given baixo bigger alto:
        yield -1
    meio := (baixo + alto) ~/ 2
    given xs[meio] is alvo:
        yield meio
    given xs[meio] smaller alvo:
        yield busca(xs, alvo, meio + 1, alto)
    yield busca(xs, alvo, baixo, meio - 1)
'''


def test_busca_binaria_recursiva_e_log_n_e_nao_exponencial():
    """Ela saía como **O(2^n)**, com o aviso grave mandando memoizar.

    Duas contagens erradas se somavam. A primeira: as duas chamadas
    recursivas estão em ramos **mutuamente exclusivos** — uma ou outra
    roda, nunca as duas —, e elas eram contadas como 2 porque a varredura
    olhava a árvore inteira sem olhar o fluxo. A segunda: a bisseção está
    em `meio := (baixo + alto) ~/ 2`, e a chamada passa `meio + 1`; quem
    procurava o `~/ 2` olhava só o argumento, e não o nome que o guarda.

    Dizer que uma busca binária é exponencial é o erro mais caro que este
    analisador podia cometer: ele acusa, com aviso grave, o algoritmo que
    a pessoa acabou de acertar.
    """
    assert tempo(BUSCA_BINARIA_RECURSIVA, "busca") == "O(log n)"


def test_fibonacci_ingenuo_continua_exponencial():
    """A guarda do lado oposto: aqui as duas chamadas rodam MESMO, na
    mesma expressão, e a entrada não se divide."""
    assert tempo('action fib(n):\n'
                 '    given n smaller 2:\n'
                 '        yield n\n'
                 '    yield fib(n - 1) + fib(n - 2)\n', "fib") == "O(2^n)"


def test_duas_chamadas_no_mesmo_caminho_continuam_contando_duas():
    """Um ramo que NÃO encerra não exclui o que vem depois."""
    fonte = ('action f(n):\n'
             '    given n smaller 2:\n'
             '        yield n\n'
             '    given n % 2 is 0:\n'
             '        a := f(n - 1)\n'
             '    b := f(n - 2)\n'
             '    yield b\n')
    assert tempo(fonte, "f") == "O(2^n)"


FIB_MEMO = '''
cache := {}

action fib_memo(n):
    given n smaller 2:
        yield n
    given cache.has(str(n)):
        yield cache[str(n)]
    valor := fib_memo(n - 1) + fib_memo(n - 2)
    cache[str(n)] := valor
    yield valor
'''


def test_o_fibonacci_memoizado_nao_e_exponencial():
    """O analisador **recomenda** memoizar e depois acusava o resultado.

    O aviso do O(2^n) diz, com todas as letras: "guarde os resultados já
    calculados num vault (memoizacao): quase sempre derruba para O(n)".
    Quem seguia o conselho recebia o mesmo O(2^n) e o mesmo aviso grave —
    uma ferramenta contradizendo o próprio conselho ensina a ignorá-la.

    Com o cache, cada argumento distinto é calculado **uma vez**: as
    chamadas repetidas saem pelo `yield` de cima.
    """
    assert tempo(FIB_MEMO, "fib_memo") == "O(n)"


ARVORE = '''
action em_ordem(atual, saida):
    given atual is void:
        yield saida
    em_ordem(atual.esq, saida)
    saida.append(atual.valor)
    em_ordem(atual.dir, saida)
    yield saida
'''


def test_percorrer_uma_arvore_e_linear_e_nao_exponencial():
    """Duas chamadas, sobre partes DIFERENTES da estrutura.

    `em_ordem(atual.esq, …)` e `em_ordem(atual.dir, …)` descem por
    galhos distintos: cada nó é visitado uma vez, e o total é O(n) nos
    nós. A forma é idêntica à do fibonacci ingênuo — duas chamadas, sem
    `~/ 2` à vista —, e por isso a travessia mais comum que existe era
    classificada como exponencial.
    """
    assert tempo(ARVORE, "em_ordem") == "O(n)"


def test_a_mesma_parte_duas_vezes_continua_exponencial():
    """A guarda: partes distintas é o que torna linear. O MESMO galho
    duas vezes dobra o trabalho a cada nível, como o fibonacci."""
    fonte = ('action f(atual):\n'
             '    given atual is void:\n'
             '        yield 0\n'
             '    yield f(atual.esq) + f(atual.esq)\n')
    assert tempo(fonte, "f") == "O(2^n)"
