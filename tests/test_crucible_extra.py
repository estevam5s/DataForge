# -*- coding: utf-8 -*-
"""Crucible — as ferramentas de cenário, e os matchers que faltavam.

O `crucible.py` responde "o valor é o esperado?". Estes testes cobrem
as perguntas que sobram, e o que cada uma protege:

1. **`to_change`** — o efeito colateral. Sem ele se escreve `antes`, a
   ação, `depois` e um assert: quatro linhas em que a do meio pode
   falhar em silêncio.

2. **`corrida`** — a linguagem **não sincroniza sozinha**, e isso está
   documentado. O `check` avisa sobre o padrão; avisar não é provar, e
   um teste que roda a ação uma vez por thread não detecta nada porque
   a janela é estreita.

3. **`servidor_falso`** — um dublê prova que o código chamou um
   método; isto prova que ele fala HTTP direito, e o que ele faz com
   um 503. É a segunda que quebra em produção.

4. **`mutar`** — cobertura responde "esta linha rodou?". Ela não
   responde "se esta linha estivesse errada, alguém reclamaria?".

5. **`relogio`** — um relógio ligado que escapa de um trial envenena
   todos os seguintes.
"""

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module


@pytest.fixture
def C():
    return get_module("Arcane.Crucible")


@pytest.fixture
def expect(C):
    return C["expect"]


# ═══════════════════════════════════════════════════════════
#  to_change
# ═══════════════════════════════════════════════════════════

def test_to_change_mede_a_diferenca(expect):
    conta = {"saldo": 100}
    expect(lambda: conta.update(saldo=conta["saldo"] + 10)).to_change(
        lambda: conta["saldo"]).por(10)


def test_to_change_diz_de_onde_para_onde(expect, C):
    conta = {"saldo": 100}
    expect(lambda: conta.update(saldo=150)).to_change(
        lambda: conta["saldo"]).de_para(100, 150)


def test_to_change_acusa_quando_nada_muda(expect, C):
    conta = {"saldo": 100}
    with pytest.raises(C["expect"](0).__class__.__mro__[0] and Exception) as erro:
        expect(lambda: None).to_change(lambda: conta["saldo"])
    assert "continuou em" in str(erro.value)


def test_to_change_diz_a_diferenca_real_quando_erra(expect):
    conta = {"saldo": 100}
    with pytest.raises(Exception) as erro:
        expect(lambda: conta.update(saldo=105)).to_change(
            lambda: conta["saldo"]).por(10)
    assert "mudou em 5" in str(erro.value)


def test_to_change_exige_uma_acao(expect):
    """Ele precisa **rodar** alguma coisa para ver o que mudou."""
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        expect(42).to_change(lambda: 1)
    assert "ACAO" in str(erro.value.message)


def test_to_not_change_e_um_matcher_proprio(expect):
    """`nao().to_change(...)` devolveria uma `Mudanca` sem sentido —
    encadear `.por(...)` depois de "não mudou" não quer dizer nada."""
    conta = {"saldo": 100}
    expect(lambda: None).to_not_change(lambda: conta["saldo"])
    with pytest.raises(Exception) as erro:
        expect(lambda: conta.update(saldo=1)).to_not_change(
            lambda: conta["saldo"])
    assert "nao devia mudar" in str(erro.value)


def test_a_negacao_do_to_change_nao_e_ramo_morto(expect):
    """O `_negado` era zerado ANTES de ser consultado, e a mensagem de
    "não devia mudar" nunca saía."""
    conta = {"saldo": 1}
    with pytest.raises(Exception) as erro:
        expect(lambda: conta.update(saldo=2)).nao().to_change(
            lambda: conta["saldo"])
    assert "nao devia mudar" in str(erro.value)


# ═══════════════════════════════════════════════════════════
#  Dublês
# ═══════════════════════════════════════════════════════════

def test_os_matchers_de_duble(expect, C):
    d = C["spy"](None)
    d.chamar("salvar", 1)
    d.chamar("salvar", 2)
    d.chamar("fechar")

    expect(d).to_have_been_called()
    expect(d).to_have_been_called("salvar")
    expect(d).to_have_been_called_times(2, "salvar")
    expect(d).to_have_been_called_once("fechar")
    expect(d).to_have_been_called_with(1)
    expect(d).to_have_been_called_in_order("salvar", "fechar")
    expect(d).to_have_never_been_called("apagar")


def test_chamado_uma_vez_nao_passa_com_tres(expect, C):
    """"Foi chamado" passa com três chamadas — e três chamadas de
    `cobrar()` é uma cobrança duplicada."""
    d = C["spy"](None)
    for _ in range(3):
        d.chamar("cobrar")
    expect(d).to_have_been_called("cobrar")
    with pytest.raises(Exception):
        expect(d).to_have_been_called_once("cobrar")


def test_a_ordem_admite_outras_chamadas_no_meio(expect, C):
    """Cobrar a sequência exata quebraria a cada chamada nova, e um
    teste que quebra sem o comportamento mudar é um teste apagado."""
    d = C["spy"](None)
    d.chamar("abrir")
    d.chamar("logar")
    d.chamar("fechar")
    expect(d).to_have_been_called_in_order("abrir", "fechar")


def test_um_matcher_de_duble_num_valor_comum_ensina(expect):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        expect(42).to_have_been_called()
    assert "spy" in str(erro.value.nota)


# ═══════════════════════════════════════════════════════════
#  Forma e conteúdo
# ═══════════════════════════════════════════════════════════

def test_match_vault_ignora_as_outras_chaves(expect):
    """Cobrar o vault inteiro obriga a escrever no teste campos que ele
    não testa — e no dia em que um campo novo aparece, dez testes
    quebram sem nenhum comportamento ter mudado."""
    resposta = {"status": 200, "corpo": "x", "ms": 12.3}
    expect(resposta).to_match_vault({"status": 200})
    with pytest.raises(Exception) as erro:
        expect(resposta).to_match_vault({"status": 404})
    assert "status" in str(erro.value)


def test_have_shape_cobra_o_tipo_e_nao_o_valor(expect):
    expect({"id": 1, "nome": "Ana"}).to_have_shape(
        {"id": "Integer", "nome": "String"})
    with pytest.raises(Exception) as erro:
        expect({"id": "1"}).to_have_shape({"id": "Integer"})
    assert "id" in str(erro.value)


def test_satisfy_e_a_saida_de_emergencia(expect):
    expect(7).to_satisfy(lambda v: v % 2 == 1, "ser ímpar")
    with pytest.raises(Exception) as erro:
        expect(8).to_satisfy(lambda v: v % 2 == 1, "ser ímpar")
    assert "ímpar" in str(erro.value)


def test_uma_condicao_que_estoura_nao_vira_falha_comum(expect):
    """Uma regra quebrada é uma regra quebrada, e não um valor ruim —
    dizer 'não satisfez' esconderia o bug real."""
    with pytest.raises(Exception) as erro:
        expect(1).to_satisfy(lambda v: 1 / 0)
    assert "estourou" in str(erro.value)


def test_contain_exactly_ignora_a_ordem(expect):
    expect([3, 1, 2]).to_contain_exactly([1, 2, 3])
    with pytest.raises(Exception) as erro:
        expect([1, 2]).to_contain_exactly([1, 2, 3])
    assert "falta" in str(erro.value)


def test_round_trip_cobra_a_ida_e_a_volta(expect):
    """É a propriedade que todo formato promete e quase nenhum cumpre
    na borda."""
    expect({"a": 1}).to_round_trip(json.dumps, json.loads)
    with pytest.raises(Exception) as erro:
        expect({1: "a"}).to_round_trip(json.dumps, json.loads)
    assert "voltar igual" in str(erro.value)


def test_within_percent_serve_a_escalas_diferentes(expect):
    """Uma tolerância absoluta é muito para um percentual e nada para
    um saldo."""
    expect(101).to_be_within_percent(100, 2)
    expect(1_010_000).to_be_within_percent(1_000_000, 2)
    with pytest.raises(Exception):
        expect(110).to_be_within_percent(100, 2)


def test_raise_matching_cobra_um_trecho_estavel(expect):
    """Cobrar a mensagem inteira quebra na primeira melhoria do texto."""
    def quebrar():
        raise ValueError("campo 'cpf' inválido")

    expect(quebrar).to_raise_matching(r"cpf")
    with pytest.raises(Exception) as erro:
        expect(lambda: None).to_raise_matching(r"cpf")
    assert "nada foi levantado" in str(erro.value)


def test_to_emit_separa_o_finito_do_infinito(expect):
    """Fundir as duas perguntas faria `to_emit([0,1,2])` passar sobre
    uma série que nunca acaba — e a afirmação "produz [0,1,2]" seria
    falsa. Um `stream action` infinito é comum na linguagem."""
    def infinito():
        n = 0
        while True:
            yield n
            n += 1

    def finito():
        yield 0
        yield 1
        yield 2

    expect(finito).to_emit([0, 1, 2])
    expect(infinito).to_emit_first([0, 1, 2])

    with pytest.raises(Exception) as erro:
        expect(infinito).to_emit([0, 1, 2])
    assert "continuou" in str(erro.value)


def test_to_emit_nao_trava_num_gerador_infinito(expect):
    """Comparar com um gerador que não acaba travaria o teste em vez de
    falhar — o pior desfecho possível num framework de teste."""
    def infinito():
        while True:
            yield 1

    with pytest.raises(Exception):
        expect(infinito).to_emit([1, 1])


def test_ordered_by_le_o_campo_de_vault_e_de_record(expect):
    expect([{"n": 1}, {"n": 2}]).to_be_ordered_by("n")
    with pytest.raises(Exception):
        expect([{"n": 2}, {"n": 1}]).to_be_ordered_by("n")


def test_nenhum_matcher_novo_sobrescreve_um_antigo():
    """Dois matchers com o mesmo nome fariam o segundo sumir em
    silêncio — e o teste que o usa passaria testando outra coisa."""
    from dataforge.stdlib import crucible_extra as E
    from dataforge.stdlib.crucible import Expectativa

    assert all(hasattr(Expectativa, nome) for nome in E._NOVOS)
    # A trava está no próprio módulo: ele levanta ao ser importado.
    assert len(E._NOVOS) == 20


# ═══════════════════════════════════════════════════════════
#  Corrida
# ═══════════════════════════════════════════════════════════

def test_a_corrida_detecta_a_atualizacao_perdida(C):
    """Duas threads escrevendo no mesmo nome perdem atualizações, em
    silêncio. O `check` avisa sobre o padrão; avisar não é provar."""
    contador = {"v": 0}

    def sem_trava():
        atual = contador["v"]
        time.sleep(0)          # abre a janela de propósito
        contador["v"] = atual + 1

    r = C["corrida"](sem_trava, threads=4, voltas=2000,
                     leitor=lambda: contador["v"])
    assert r.perdeu(), "a corrida não abriu janela nenhuma"
    assert r.perdidas() > 0
    assert r.para_vault()["threads"] == 4


def test_a_corrida_aprova_o_que_esta_protegido(C):
    trava = threading.Lock()
    contador = {"v": 0}

    def com_trava():
        with trava:
            contador["v"] += 1

    r = C["corrida"](com_trava, threads=4, voltas=2000,
                     leitor=lambda: contador["v"])
    assert not r.perdeu(), f"o mutex não segurou: {r.para_vault()}"


def test_a_corrida_anota_o_erro_de_dentro_da_thread(C):
    """Um erro dentro da thread morreria calado, e o teste passaria."""
    def quebrar():
        raise ValueError("estourou")

    r = C["corrida"](quebrar, threads=2, voltas=5)
    assert r.erros and "estourou" in r.erros[0]


# ═══════════════════════════════════════════════════════════
#  Determinismo
# ═══════════════════════════════════════════════════════════

def test_o_determinismo_pega_o_random_sem_semente(C):
    import random

    assert C["determinismo"](lambda: random.random())["estavel"] is False
    assert C["determinismo"](lambda: sorted([3, 1, 2]))["estavel"] is True


def test_o_determinismo_compara_por_foto_e_nao_por_referencia(C):
    """Duas listas iguais são objetos diferentes; comparar referência
    diria 'instável' para código perfeitamente determinístico."""
    assert C["determinismo"](lambda: [1, 2, 3])["estavel"] is True


# ═══════════════════════════════════════════════════════════
#  Relógio
# ═══════════════════════════════════════════════════════════

def test_o_relogio_anda_quando_se_manda(C):
    """`freeze_time` congela; este **anda** — e é isso que testa o que
    depende de intervalo, sem o teste precisar dormir."""
    def medir(r):
        inicio = time.time()
        r.avancar(minutos=31)
        return time.time() - inicio

    assert C["com_relogio"](medir, "2026-09-20 10:00:00") == 1860.0


def test_o_relogio_e_desligado_mesmo_com_falha(C):
    """Um relógio ligado que escapa de um trial que estourou faz TODOS
    os seguintes verem o tempo parado."""
    original = time.time
    with pytest.raises(ValueError):
        C["com_relogio"](lambda r: (_ for _ in ()).throw(ValueError("x")))
    assert time.time is original, "o relógio vazou para os próximos testes"


def test_o_relogio_entende_as_formas_de_data(C):
    for forma in ("2026-09-20", "2026-09-20 10:30", "2026-09-20T10:30:00"):
        assert C["relogio"](forma).agora > 0


def test_um_instante_que_nao_se_entende_diz_as_formas(C):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        C["relogio"]("ontem de manhã")
    assert "2026-09-20" in str(erro.value.nota)


# ═══════════════════════════════════════════════════════════
#  Servidor falso
# ═══════════════════════════════════════════════════════════

def test_o_servidor_falso_responde_o_que_foi_programado(C):
    s = C["servidor_falso"]()
    try:
        s.responder("/precos", {"dolar": 5.42})
        with urllib.request.urlopen(s.url("/precos")) as r:
            assert json.loads(r.read())["dolar"] == 5.42
        assert s.quantos("/precos") == 1
        assert s.ultimo("/precos")["metodo"] == "GET"
    finally:
        s.parar()


def test_o_servidor_falso_falha_um_numero_exato_de_vezes(C):
    """Sem o limite não dá para testar "falha duas vezes e na terceira
    funciona" — que é o que um cliente com recuo promete e quase nunca
    tem teste."""
    s = C["servidor_falso"]()
    try:
        s.falhar("/instavel", 503, vezes=2)
        s.responder("/instavel", {"ok": True})
        codigos = []
        for _ in range(3):
            try:
                with urllib.request.urlopen(s.url("/instavel")) as r:
                    codigos.append(r.status)
            except urllib.error.HTTPError as erro:
                codigos.append(erro.code)
        assert codigos == [503, 503, 200]
    finally:
        s.parar()


def test_uma_rota_que_nao_existe_responde_404(C):
    s = C["servidor_falso"]()
    try:
        with pytest.raises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(s.url("/nada"))
        assert erro.value.code == 404
    finally:
        s.parar()


def test_o_servidor_falso_guarda_o_corpo_que_recebeu(C):
    s = C["servidor_falso"]()
    try:
        s.responder("/eventos", {"ok": True})
        pedido = urllib.request.Request(
            s.url("/eventos"), data=b'{"tipo":"clique"}',
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(pedido).read()
        assert json.loads(s.ultimo("/eventos")["corpo"])["tipo"] == "clique"
    finally:
        s.parar()


# ═══════════════════════════════════════════════════════════
#  Contrato
# ═══════════════════════════════════════════════════════════

def test_o_contrato_roda_as_mesmas_provas_nas_duas(C, expect):
    """Duas implementações do mesmo trait costumam ter DOIS conjuntos
    de testes, e a segunda quebra no uso — porque o que ela não cumpre
    é justamente o que só o teste da primeira cobria."""
    class Boa:
        def __init__(self):
            self.d = {}

        def guardar(self, k, v):
            self.d[k] = v

        def ler(self, k):
            return self.d.get(k)

        def apagar(self, k):
            self.d.pop(k, None)

    class Furada(Boa):
        def apagar(self, k):
            pass

    def guarda_e_le(a):
        a.guardar("x", 1)
        expect(a.ler("x")).to_be(1)

    def apaga(a):
        a.guardar("x", 1)
        a.apagar("x")
        expect(a.ler("x")).to_be_void()

    provas = C["contrato"]("Armazem", [
        {"nome": "guarda e le", "prova": guarda_e_le},
        {"nome": "apaga", "prova": apaga}])
    provas.para("boa", Boa).para("furada", Furada)

    assert provas.resumo()["casos"] == 4
    falhas = provas.falhas()
    assert len(falhas) == 1
    assert falhas[0]["implementacao"] == "furada"
    assert falhas[0]["caso"] == "apaga"
    with pytest.raises(Exception):
        provas.cobrar()


def test_um_caso_de_contrato_mal_formado_ensina_a_forma(C):
    from dataforge.errors import RuntimeError_

    with pytest.raises(RuntimeError_) as erro:
        C["contrato"]("X", [{"nome": "sem prova"}])
    assert "prova" in str(erro.value.nota)


# ═══════════════════════════════════════════════════════════
#  Mutação
# ═══════════════════════════════════════════════════════════

def test_a_mutacao_troca_uma_coisa_por_vez():
    """Com duas trocas, um teste que pega a primeira esconde a segunda
    — e o relatório diz que ambas estão cobertas."""
    from dataforge.stdlib.crucible_extra import _mutantes

    gerados = _mutantes("action f(x):\n    yield x bigger 1 and x smaller 9\n")
    assert gerados
    for m in gerados:
        diferentes = sum(1 for a, b in zip(m["antes"].split(),
                                           m["depois"].split()) if a != b)
        assert diferentes <= 1, m


def test_bigger_nao_casa_dentro_de_bigger_eq():
    """Sem a fronteira de palavra, a mesma linha gerava duas mutações —
    uma delas trocando '>=' por '<=', que não é a troca anunciada. Um
    relatório que descreve uma mudança e faz outra é pior que nenhum."""
    from dataforge.stdlib.crucible_extra import _mutantes

    gerados = _mutantes("action f(x):\n    yield x bigger_eq 18\n")
    assert len(gerados) == 1
    assert gerados[0]["de"] == "bigger_eq" and gerados[0]["para"] == "bigger"
    assert "smaller_eq" not in gerados[0]["depois"]


def test_a_mutacao_nao_mexe_em_comentario():
    """Mudar um literal num comentário não muda comportamento nenhum, e
    o mutante sobreviveria sempre — enchendo o relatório de falsos
    buracos."""
    from dataforge.stdlib.crucible_extra import _mutantes

    assert _mutantes("// isto e yes e aquilo e no\n") == []


def test_a_mutacao_encontra_o_teste_que_nao_testa(C, tmp_path):
    alvo = tmp_path / "calculo.df"
    alvo.write_text("action maior(idade):\n    yield idade bigger_eq 18\n",
                    encoding="utf-8")

    fraca = C["mutar"](str(alvo), lambda: False, limite=5)
    assert fraca["pegos"] == 0
    assert fraca["sobreviventes"], "não gerou mutante nenhum"
    assert fraca["placar"] == 0.0

    boa = C["mutar"](
        str(alvo),
        lambda: "bigger_eq 18" not in alvo.read_text(encoding="utf-8"),
        limite=5)
    assert boa["placar"] == 1.0


def test_o_arquivo_volta_ao_original_mesmo_com_falha(C, tmp_path):
    """Um código-fonte silenciosamente alterado é o pior desfecho
    possível para uma ferramenta de teste."""
    alvo = tmp_path / "x.df"
    original = "action f(a):\n    yield a bigger 1\n"
    alvo.write_text(original, encoding="utf-8")

    def suite_que_estoura():
        raise RuntimeError("a suíte quebrou")

    C["mutar"](str(alvo), suite_que_estoura, limite=3)
    assert alvo.read_text(encoding="utf-8") == original


def test_um_arquivo_sem_mutacao_possivel_diz_isso(C, tmp_path):
    alvo = tmp_path / "vazio.df"
    alvo.write_text("out 1\n", encoding="utf-8")
    r = C["mutar"](str(alvo), lambda: True)
    assert r["mutantes"] == 0 and "nenhuma mutação" in r["nota"]


def test_o_relatorio_de_mutacao_nomeia_a_linha(C, tmp_path):
    alvo = tmp_path / "x.df"
    alvo.write_text("action f(a):\n    yield a bigger_eq 1\n", encoding="utf-8")
    texto = C["relatorio_de_mutacao"](C["mutar"](str(alvo), lambda: False))
    assert "linha 2" in texto and "bigger_eq → bigger" in texto


# ═══════════════════════════════════════════════════════════
#  O módulo
# ═══════════════════════════════════════════════════════════

def test_os_extras_estao_no_modulo(C):
    for nome in ("corrida", "determinismo", "relogio", "com_relogio",
                 "servidor_falso", "contrato", "mutar",
                 "relatorio_de_mutacao"):
        assert nome in C, f"'{nome}' não saiu no módulo"


def test_o_crucible_nao_importa_nada_de_fora():
    """A regra do projeto é zero dependência no runtime."""
    import ast

    for arquivo in ("crucible.py", "crucible_extra.py"):
        caminho = os.path.join("dataforge", "stdlib", arquivo)
        arvore = ast.parse(open(caminho, encoding="utf-8").read())
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    raiz = alias.name.split(".")[0]
                    assert raiz in sys.stdlib_module_names, \
                        f"{arquivo} importa {alias.name}"


# ═══════════════════════════════════════════════════════════
#  O analisador e o idioma da guarda contra nulo
# ═══════════════════════════════════════════════════════════

def test_o_check_estreita_o_tipo_depois_de_is_not_void():
    """`given x is not void:` é o idioma mais comum de guarda contra
    nulo, e ele era acusado na linha seguinte com `Cannot index a value
    of type Void` — sobre um código que roda.

    A saída de quem escreve, diante de um falso alarme no caminho mais
    comum, é desligar o analisador ou parar de usar a guarda. As duas
    são piores que o alarme.
    """
    from dataforge.lexer import tokenize
    from dataforge.parser import parse
    from dataforge.typechecker import check_program

    fonte = ("action f(v, chave):\n"
             "    item := v[chave] ?? void\n"
             "    given item is not void:\n"
             "        yield item[\"valor\"]\n"
             "    yield void\n")
    erros = [d for d in check_program(parse(tokenize(fonte, "x.df"), "x.df"),
                                      "x.df") if d.severity == "error"]
    assert not erros, [e.message for e in erros]


def test_o_estreitamento_nao_vale_no_otherwise():
    """No `otherwise` o nome **é** void — estreitar lá inverteria a
    prova, e o analisador passaria a calar sobre o erro de verdade."""
    from dataforge.typechecker import TypeChecker, UNKNOWN
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    programa = parse(tokenize("given x is not void:\n    out 1\n", "x.df"),
                     "x.df")
    estreitados = TypeChecker("x.df")._estreitar_por(
        programa.body[0].condition)
    assert estreitados == {"x": UNKNOWN}


def test_o_estreitamento_so_vale_para_a_comparacao_com_void():
    """Uma condição qualquer não prova nada sobre tipo, e concluir dali
    seria o analisador inventando o que não sabe."""
    from dataforge.lexer import tokenize
    from dataforge.parser import parse
    from dataforge.typechecker import TypeChecker

    for fonte in ("given x is 1:\n    out 1\n",
                  "given x bigger 2:\n    out 1\n",
                  "given x is void:\n    out 1\n"):
        programa = parse(tokenize(fonte, "x.df"), "x.df")
        assert TypeChecker("x.df")._estreitar_por(
            programa.body[0].condition) == {}, fonte


def test_o_exemplo_dos_cenarios_roda():
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvo = os.path.join(raiz, "examples", "crucible_cenarios.df")
    if not os.path.isfile(alvo):
        pytest.skip("o exemplo não está neste checkout")
    saida = subprocess.run([sys.executable, "-m", "dataforge", "run", alvo],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=raiz)
    assert saida.returncode == 0, saida.stdout + saida.stderr
    assert "cenarios ok" in saida.stdout
    # A corrida tem de PROVAR a perda: um exemplo que não detecta nada
    # ensina que o problema não existe.
    assert "perdeu 0" in saida.stdout, "o mutex não apareceu funcionando"
