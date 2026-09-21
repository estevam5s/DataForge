# -*- coding: utf-8 -*-
"""Arcane.Reativo — valores que avisam quando mudam.

O que estes testes protegem, e por que cada um custa caro:

1. **O derivado é preguiçoso e memorizado.** Recalcular na escrita
   faria uma cadeia de dez derivados rodar dez vezes por mudança, e a
   maioria deles nunca é lida.

2. **As dependências são descobertas, não declaradas.** Uma lista
   escrita à mão envelhece na primeira condição nova dentro da
   fórmula — e o sintoma é um valor que para de atualizar.

3. **Escrever o mesmo valor não notifica.** Senão uma cadeia
   recalcula por nada e um efeito de rede dispara duas vezes.

4. **O operador liga preguiçoso.** Com a ligação na construção, uma
   fonte **fria** despejava os valores antes de o assinante final
   existir — e o resultado era uma lista vazia, sem erro nenhum.

5. **Sinal é valor; observável é fluxo.** Frameworks que chamam os
   dois de "stream" fazem a pergunta "qual é o valor agora?" deixar de
   ter resposta.
"""

import sys
import threading
import time

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module


@pytest.fixture
def R():
    return get_module("Arcane.Reativo")


# ═══════════════════════════════════════════════════════════
#  Sinal
# ═══════════════════════════════════════════════════════════

def test_o_sinal_guarda_e_devolve(R):
    s = R["sinal"](10)
    assert s.ler() == 10
    s.escrever(20)
    assert s.ler() == 20


def test_atualizar_le_e_escreve_sem_corrida(R):
    s = R["sinal"](10)
    s.atualizar(lambda v: v * 2)
    assert s.ler() == 20


def test_escrever_o_mesmo_valor_nao_notifica(R):
    """Uma cadeia de derivados recalcularia por nada, e um efeito de
    rede dispararia duas vezes."""
    vistos = []
    s = R["sinal"](1)
    s.observar(vistos.append)
    s.escrever(1)
    s.escrever(1)
    s.escrever(2)
    assert vistos == [2]


def test_o_sinal_aceita_a_propria_nocao_de_igual(R):
    """Um vault grande pode querer identidade, e uma comparação cara
    pode querer uma chave."""
    vistos = []
    s = R["sinal"]({"v": 1}, iguais=lambda a, b: a.get("v") == b.get("v"))
    s.observar(vistos.append)
    s.escrever({"v": 1, "extra": True})     # o 'v' não mudou
    s.escrever({"v": 2})
    assert len(vistos) == 1


def test_observar_devolve_o_cancelador(R):
    vistos = []
    s = R["sinal"](0)
    cancelar = s.observar(vistos.append)
    s.escrever(1)
    cancelar()
    s.escrever(2)
    assert vistos == [1]


# ═══════════════════════════════════════════════════════════
#  Derivado
# ═══════════════════════════════════════════════════════════

def test_o_derivado_acompanha_as_fontes(R):
    preco = R["sinal"](10.0, "preco")
    qtd = R["sinal"](3, "qtd")
    total = R["derivado"](lambda: preco.ler() * qtd.ler(), "total")

    assert total.ler() == 30.0
    qtd.escrever(5)
    assert total.ler() == 50.0


def test_o_derivado_e_preguicoso_e_memorizado(R):
    """Recalcular na escrita faria uma cadeia de dez rodar dez vezes
    por mudança, e a maioria nunca é lida."""
    contas = {"n": 0}
    fonte = R["sinal"](1)

    def formula():
        contas["n"] += 1
        return fonte.ler() * 2

    d = R["derivado"](formula)
    d.ler()
    d.ler()
    d.ler()
    assert contas["n"] == 1, "recalculou sem ninguém mudar nada"

    fonte.escrever(2)
    assert contas["n"] == 1, "recalculou na escrita, sem ninguém ler"
    d.ler()
    assert contas["n"] == 2


def test_as_dependencias_sao_descobertas_e_nao_declaradas(R):
    a = R["sinal"](1, "a")
    b = R["sinal"](100, "b")
    usar_b = R["sinal"](False, "usar_b")
    d = R["derivado"](lambda: b.ler() if usar_b.ler() else a.ler(), "d")

    assert d.ler() == 1
    assert d.fontes() == ["a", "usar_b"], "entrou uma fonte que não foi lida"

    usar_b.escrever(True)
    assert d.ler() == 100
    assert d.fontes() == ["b", "usar_b"]


def test_a_fonte_que_sumiu_para_de_notificar(R):
    """Sem isso, uma fórmula com `given` acumula dependências dos dois
    ramos e recalcula por mudanças que ela nem lê mais."""
    contas = {"n": 0}
    a = R["sinal"](1, "a")
    b = R["sinal"](2, "b")
    usar_a = R["sinal"](True, "usar_a")

    def formula():
        contas["n"] += 1
        return a.ler() if usar_a.ler() else b.ler()

    d = R["derivado"](formula)
    d.ler()
    usar_a.escrever(False)
    d.ler()
    antes = contas["n"]
    a.escrever(999)          # 'a' não é mais lido
    d.ler()
    assert contas["n"] == antes, "recalculou por uma fonte abandonada"


def test_um_ciclo_e_recusado_com_a_cadeia(R):
    """Dizer só "há um ciclo" manda procurar em toda a fórmula."""
    from dataforge.errors import RuntimeError_

    d1 = R["derivado"](lambda: d2.ler() + 1, "d1")
    d2 = R["derivado"](lambda: d1.ler() + 1, "d2")
    with pytest.raises(RuntimeError_) as erro:
        d1.ler()
    assert "d1" in str(erro.value.nota) and "d2" in str(erro.value.nota)


def test_o_derivado_encadeia(R):
    base = R["sinal"](2)
    dobro = R["derivado"](lambda: base.ler() * 2, "dobro")
    quadruplo = R["derivado"](lambda: dobro.ler() * 2, "quadruplo")
    assert quadruplo.ler() == 8
    base.escrever(3)
    assert quadruplo.ler() == 12


def test_valor_le_sem_criar_dependencia(R):
    """É a saída para ler um sinal dentro de um derivado sem que ele
    passe a depender dali."""
    a = R["sinal"](1, "a")
    ruido = R["sinal"](0, "ruido")
    d = R["derivado"](lambda: a.ler() + ruido.valor(), "d")
    assert d.ler() == 1
    assert d.fontes() == ["a"]


# ═══════════════════════════════════════════════════════════
#  Efeito
# ═══════════════════════════════════════════════════════════

def test_o_efeito_roda_uma_vez_ao_ser_criado(R):
    """Sem isso, quem escreve um efeito que desenha a tela vê a tela
    vazia até a primeira mudança — e conclui que não funciona."""
    saidas = []
    s = R["sinal"](1)
    R["efeito"](lambda: saidas.append(s.ler()))
    assert saidas == [1]
    s.escrever(2)
    assert saidas == [1, 2]


def test_o_efeito_para_quando_mandado(R):
    saidas = []
    s = R["sinal"](1)
    e = R["efeito"](lambda: saidas.append(s.ler()))
    e.parar()
    s.escrever(2)
    assert saidas == [1]


def test_a_limpeza_roda_antes_do_proximo_ciclo(R):
    """É como se cancela a inscrição antiga antes de abrir a nova —
    sem isso, um efeito que abre conexão abre uma por mudança."""
    eventos = []
    s = R["sinal"](1)

    def acao():
        valor = s.ler()
        eventos.append(f"abriu {valor}")
        return lambda: eventos.append(f"fechou {valor}")

    e = R["efeito"](acao)
    s.escrever(2)
    e.parar()
    assert eventos == ["abriu 1", "fechou 1", "abriu 2", "fechou 2"]


def test_um_efeito_sem_acao_diz_o_que_falta(R):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_):
        R["efeito"](42)


# ═══════════════════════════════════════════════════════════
#  Observável
# ═══════════════════════════════════════════════════════════

def test_o_observavel_entrega_ao_inscrito(R):
    vistos = []
    o = R["observavel"]()
    o.inscrever(vistos.append)
    o.emitir(1)
    o.emitir(2)
    assert vistos == [1, 2]


def test_cancelar_a_inscricao_para_de_receber(R):
    vistos = []
    o = R["observavel"]()
    inscricao = o.inscrever(vistos.append)
    o.emitir(1)
    inscricao.cancelar()
    o.emitir(2)
    assert vistos == [1]


def test_os_operadores_encadeiam(R):
    vistos = []
    o = R["observavel"]()
    o.sift(lambda v: v % 2 == 0).morph(lambda v: v * 10).inscrever(vistos.append)
    for n in range(1, 7):
        o.emitir(n)
    assert vistos == [20, 40, 60]


def test_o_operador_liga_preguicoso(R):
    """Com a ligação na construção, uma fonte **fria** despejava os
    valores antes de o assinante final existir — e o resultado era uma
    lista vazia, sem erro nenhum."""
    vistos = []
    R["de_cluster"]([1, 2, 3]).morph(lambda v: v * 2).inscrever(vistos.append)
    assert vistos == [2, 4, 6]


def test_de_cluster_emite_a_cada_inscricao(R):
    """Ele é frio: emitir antes de alguém escutar seria emitir para
    ninguém, que é o erro mais comum ao aprender fluxos."""
    fonte = R["de_cluster"]([1, 2])
    a, b = [], []
    fonte.inscrever(a.append)
    fonte.inscrever(b.append)
    assert a == [1, 2] and b == [1, 2]


def test_distill_emite_a_cada_valor(R):
    """Diferente do `>> distill` do pipeline: lá o resultado sai uma
    vez, no fim; aqui sai a cada valor, porque um fluxo não tem fim
    para esperar."""
    vistos = []
    o = R["observavel"]()
    o.distill(lambda a, v: a + v, 0).inscrever(vistos.append)
    for n in [1, 2, 3]:
        o.emitir(n)
    assert vistos == [1, 3, 6]


def test_distintos_pula_o_repetido_seguido(R):
    vistos = []
    o = R["observavel"]()
    o.distintos().inscrever(vistos.append)
    for v in [1, 1, 2, 2, 1]:
        o.emitir(v)
    assert vistos == [1, 2, 1]


def test_primeiros_encerra_o_fluxo(R):
    vistos, fim = [], []
    o = R["observavel"]()
    o.primeiros(2).inscrever(vistos.append, None, lambda: fim.append(True))
    for v in [1, 2, 3, 4]:
        o.emitir(v)
    assert vistos == [1, 2] and fim == [True]


def test_blocos_junta_em_grupos(R):
    vistos = []
    o = R["observavel"]()
    o.blocos(2).inscrever(vistos.append)
    for v in range(5):
        o.emitir(v)
    assert vistos == [[0, 1], [2, 3]]


def test_esperar_e_o_debounce(R):
    """É o operador da caixa de busca: sem ele, cada tecla dispara uma
    consulta, e a resposta da terceira pode chegar depois da quinta."""
    vistos = []
    o = R["observavel"]()
    o.esperar(0.05).inscrever(vistos.append)
    for v in "abc":
        o.emitir(v)
    time.sleep(0.18)
    assert vistos == ["c"], vistos


def test_limitar_e_o_throttle(R):
    """Ele emite o PRIMEIRO e ignora o resto da janela — o contrário
    do `esperar`."""
    vistos = []
    o = R["observavel"]()
    o.limitar(0.05).inscrever(vistos.append)
    o.emitir(1)
    o.emitir(2)
    time.sleep(0.07)
    o.emitir(3)
    assert vistos == [1, 3]


def test_ao_falhar_troca_o_erro_por_um_valor(R):
    vistos = []
    o = R["observavel"]()
    o.ao_falhar(lambda erro: f"tratado: {erro}").inscrever(vistos.append)
    o.emitir("ok")
    o.falhar("quebrou")
    assert vistos == ["ok", "tratado: quebrou"]


def test_combinar_so_emite_quando_todos_ja_falaram(R):
    """Antes disso o cluster teria buracos, e quem recebe teria de
    tratar um `void` que só acontece no começo — a fonte mais comum de
    bug em código reativo."""
    vistos = []
    a, b = R["observavel"]("a"), R["observavel"]("b")
    R["combinar"](a, b).inscrever(vistos.append)
    a.emitir("x")
    assert vistos == []
    b.emitir(1)
    assert vistos == [["x", 1]]
    a.emitir("y")
    assert vistos == [["x", 1], ["y", 1]]


def test_juntar_mistura_as_fontes(R):
    vistos = []
    a, b = R["observavel"]("a"), R["observavel"]("b")
    R["juntar"](a, b).inscrever(vistos.append)
    a.emitir(1)
    b.emitir(2)
    a.emitir(3)
    assert vistos == [1, 2, 3]


def test_o_intervalo_conta_e_para(R):
    vistos = []
    R["intervalo"](0.02, 3).inscrever(vistos.append)
    time.sleep(0.15)
    assert vistos == [0, 1, 2]


# ═══════════════════════════════════════════════════════════
#  A ponte entre as duas metades
# ═══════════════════════════════════════════════════════════

def test_o_fluxo_vira_valor_com_um_inicial(R):
    """Um valor sempre pode virar fluxo; um fluxo só vira valor quando
    alguém diz qual é o valor ANTES do primeiro item."""
    o = R["observavel"]()
    s = o.para_sinal("nada")
    assert s.ler() == "nada"
    o.emitir("chegou")
    assert s.ler() == "chegou"


def test_o_sinal_alimenta_um_derivado_que_alimenta_um_efeito(R):
    """A cadeia inteira, que é o que o módulo existe para fazer."""
    tela = []
    preco = R["sinal"](10.0, "preco")
    qtd = R["sinal"](2, "qtd")
    total = R["derivado"](lambda: preco.ler() * qtd.ler(), "total")
    R["efeito"](lambda: tela.append(total.ler()))

    qtd.escrever(3)
    preco.escrever(20.0)
    assert tela == [20.0, 30.0, 60.0]


# ═══════════════════════════════════════════════════════════
#  Threads
# ═══════════════════════════════════════════════════════════

def test_dois_derivados_em_threads_nao_se_misturam(R):
    """`_Rastro` é `threading.local` porque dois derivados calculando
    em threads diferentes não podem registrar dependência um no outro —
    esse bug seria intermitente e quase impossível de reproduzir."""
    a = R["sinal"](1, "a")
    b = R["sinal"](2, "b")
    da = R["derivado"](lambda: a.ler() * 10, "da")
    db = R["derivado"](lambda: b.ler() * 10, "db")
    erros = []

    def ler(d, esperado):
        for _ in range(200):
            if d.ler() != esperado:
                erros.append(d.nome)
                return

    linhas = [threading.Thread(target=ler, args=(da, 10)),
              threading.Thread(target=ler, args=(db, 20))]
    for linha in linhas:
        linha.start()
    for linha in linhas:
        linha.join(timeout=20)

    assert not erros
    assert da.fontes() == ["a"] and db.fontes() == ["b"]


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

def test_o_modulo_responde_pelos_apelidos():
    for nome in ("Arcane.Reativo", "Reativo", "Reactive", "Sinais"):
        modulo = get_module(nome)
        assert modulo is not None
        assert modulo["__name__"] == "Arcane.Reativo"


def test_o_catalogo_distingue_valor_de_fluxo():
    from dataforge.stdlib.catalogo import DESCRICOES

    descricao, curto = DESCRICOES["Arcane.Reativo"]
    assert curto == "Reativo"
    assert "fluxo" in descricao and "valor" in descricao


def test_o_reativo_nao_importa_nada_de_fora():
    import ast

    arvore = ast.parse(open("dataforge/stdlib/arcane_reativo.py",
                            encoding="utf-8").read())
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                assert alias.name.split(".")[0] in sys.stdlib_module_names


# ═══════════════════════════════════════════════════════════
#  O losango — a propagacao em duas fases
# ═══════════════════════════════════════════════════════════
#
# Estes sao os testes que mais importam do arquivo, porque o defeito
# que eles travam NAO levanta erro: ele entrega um valor que nunca
# existiu, na tela, e some sozinho no aviso seguinte.


def _losango(R, contas=None):
    """a → b → c, e tambem a → c. O grafo minimo com dois caminhos."""
    a = R["sinal"](1)

    def conta(chave, formula):
        def rodar():
            if contas is not None:
                contas[chave] = contas.get(chave, 0) + 1
            return formula()
        return rodar

    b = R["derivado"](conta("b", lambda: a.ler() * 2))
    c = R["derivado"](conta("c", lambda: a.ler() + b.ler()))
    return a, b, c


def test_o_losango_nao_entrega_valor_intermediario(R):
    """Medido antes da correcao: o efeito via 7, e depois 15.

    Com `a = 5`, o valor certo e 15 (5 + 10). O 7 era `5 + o b antigo`
    — um estado que nunca foi verdade, porque `b` ainda estava limpo
    quando `c` recalculou. `_derivados` e um SET: quem vem primeiro
    nao e escolhido por ninguem, e por isso o defeito aparecia e
    sumia conforme a ordem de hash.
    """
    a, _b, c = _losango(R)
    vistos = []
    R["efeito"](lambda: vistos.append(c.ler()))

    a.escrever(5)
    assert vistos == [3, 15], (
        "o efeito viu um valor que nunca existiu: %r" % (vistos,))


def test_o_efeito_alcancado_por_dois_caminhos_roda_uma_vez(R):
    a, _b, c = _losango(R)
    vezes = []
    R["efeito"](lambda: vezes.append(c.ler()))
    assert len(vezes) == 1                 # a criacao

    a.escrever(5)
    assert len(vezes) == 2                 # e NAO 3


def test_o_ouvinte_de_um_derivado_tambem_espera_a_marcacao(R):
    """Ler na fase de marcacao puxa um vizinho que ainda nao foi marcado."""
    a, _b, c = _losango(R)
    vistos = []
    c.observar(vistos.append)

    a.escrever(5)
    assert vistos == [15]


def test_o_lote_agrupa_de_verdade(R):
    """Ele montava uma lista de adiados que ninguem lia.

    O gancho era escrito num `threading.local` e nenhum caminho de
    escrita o consultava: `lote` existia, tinha doc, e nao agrupava
    nada — tres escritas davam tres notificacoes.
    """
    a = R["sinal"](1)
    b = R["sinal"](10)
    soma = R["derivado"](lambda: a.ler() + b.ler())
    vistos = []
    R["efeito"](lambda: vistos.append(soma.ler()))
    assert vistos == [11]

    R["lote"](lambda: (a.escrever(2), b.escrever(20), a.escrever(3)))
    assert vistos == [11, 23], (
        "tres escritas deviam dar UMA notificacao: %r" % (vistos,))


def test_o_lote_devolve_o_que_a_acao_devolveu(R):
    assert R["lote"](lambda: 42) == 42


def test_o_lote_avisa_mesmo_quando_a_acao_falha(R):
    """A escrita ja aconteceu; engolir o aviso deixaria a tela mentindo."""
    a = R["sinal"](1)
    vistos = []
    a.observar(vistos.append)

    def meio_caminho():
        a.escrever(9)
        raise ValueError("caiu depois de escrever")

    with pytest.raises(ValueError):
        R["lote"](meio_caminho)
    assert a.ler() == 9
    assert vistos == [9]


def test_uma_escrita_dentro_de_um_efeito_abre_a_PROXIMA_onda(R):
    """Reentrar faria a fila crescer enquanto e percorrida."""
    a = R["sinal"](1)
    eco = R["sinal"](0)
    vistos = []

    def espelhar():
        v = a.ler()
        if v < 3:
            eco.escrever(v)

    R["efeito"](espelhar)
    eco.observar(vistos.append)

    a.escrever(2)
    assert eco.ler() == 2
    assert vistos == [2]


def test_a_cadeia_longa_avisa_uma_vez_por_escrita(R):
    """Dez derivados em cadeia, e um efeito no fim."""
    a = R["sinal"](1)
    atual = a
    for _ in range(10):
        anterior = atual
        atual = R["derivado"](lambda fonte=anterior: fonte.ler() + 1)

    fim = atual
    vezes = []
    R["efeito"](lambda: vezes.append(fim.ler()))
    assert vezes == [11]

    a.escrever(2)
    assert vezes == [11, 12]


def test_ler_um_derivado_nao_dispara_ouvinte_de_ninguem(R):
    """O aviso era emitido de dentro do recalculo.

    Como o recalculo acontece no PULL, quem simplesmente lesse o
    derivado disparava o efeito de terceiros — num instante escolhido
    por quem leu primeiro, que e exatamente a janela do losango.
    """
    a = R["sinal"](1)
    d = R["derivado"](lambda: a.ler() * 2)
    vistos = []
    d.observar(vistos.append)
    assert vistos == []

    for _ in range(5):
        d.ler()
    assert vistos == []

    a.escrever(2)
    assert vistos == [4]


def test_observar_num_derivado_nunca_lido_liga_a_cadeia(R):
    """As dependencias sao descobertas EXECUTANDO a formula.

    Um derivado que ninguem leu nao esta ligado a fonte nenhuma:
    `observar` registrava a acao num objeto que jamais seria avisado,
    e ela ficava guardada para sempre sem nada denunciar.
    """
    a = R["sinal"](1)
    d = R["derivado"](lambda: a.ler() * 2)      # nunca lido
    vistos = []
    d.observar(vistos.append)                   # e nem por isso surdo

    a.escrever(5)
    assert vistos == [10]


def test_um_derivado_que_recalcula_para_o_MESMO_valor_nao_avisa(R):
    """`modulo` de 3 e de -3 e o mesmo numero — a tela nao muda."""
    a = R["sinal"](3)
    modulo = R["derivado"](lambda: abs(a.ler()))
    vistos = []
    modulo.observar(vistos.append)

    a.escrever(-3)
    assert modulo.ler() == 3
    assert vistos == []

    a.escrever(4)
    assert vistos == [4]


# ═══════════════════════════════════════════════════════════
#  A classe do erro E o contrato
# ═══════════════════════════════════════════════════════════

def _classe(nome):
    from dataforge.errors import erro_por_nome
    return erro_por_nome(nome)


def test_um_ciclo_levanta_ReactiveCycleError_com_a_cadeia(R):
    caixa = {}
    a = R["derivado"](lambda: caixa["b"].ler() + 1)
    b = R["derivado"](lambda: a.ler() + 1)
    caixa["b"] = b

    with pytest.raises(_classe("ReactiveCycleError")) as erro:
        a.ler()
    assert "→" in erro.value.nota          # a cadeia, e nao so "ha um ciclo"


def test_um_derivado_nao_pode_escrever(R):
    """O grafo mudaria enquanto esta sendo percorrido."""
    contador = R["sinal"](0)
    mau = R["derivado"](lambda: contador.escrever(1))
    with pytest.raises(_classe("ReactiveWriteError")):
        mau.ler()


def test_um_EFEITO_pode_escrever(R):
    """Ele nao tem valor a produzir; a escrita dele abre a proxima onda."""
    a = R["sinal"](1)
    eco = R["sinal"](0)
    R["efeito"](lambda: eco.escrever(a.ler() * 10))
    assert eco.ler() == 10
    a.escrever(3)
    assert eco.ler() == 30


def test_emitir_num_fluxo_encerrado_levanta(R):
    """Devolver `no` calado fazia o valor sumir sem nada no log."""
    o = R["observavel"]()
    o.encerrar()
    with pytest.raises(_classe("StreamClosedError")):
        o.emitir(1)


def test_o_caminho_de_DENTRO_desiste_calado(R):
    """Um temporizador que bate depois do cancelamento e o caso normal."""
    o = R["observavel"]()
    depois = o.morph(lambda v: v * 2)
    vistos = []
    inscricao = depois.inscrever(vistos.append)
    o.emitir(1)
    inscricao.cancelar()
    o.encerrar()
    assert vistos == [2]
    # O operador ja fechou a saida dele; empurrar ali nao levanta.
    assert depois._empurrar(99) is False


def test_a_base_reativa_pega_todas(R):
    base = _classe("ReactiveError")
    for nome in ["ReactiveCycleError", "ReactiveWriteError",
                 "StreamClosedError"]:
        assert issubclass(_classe(nome), base), nome
