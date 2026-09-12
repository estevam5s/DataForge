"""Arcane.Malha — o que muda quando a chamada atravessa a rede.

Uma chamada de função ou funciona, ou levanta. Uma chamada de **rede**
tem um terceiro estado: **não se sabe**. Ela pode ter chegado e a
resposta se perdido; pode estar a caminho; pode ter sido processada
duas vezes.

Quase todo bug de microserviço vem de tratar o terceiro estado como um
dos dois primeiros:

| O que se faz | O que acontece |
|---|---|
| tentar de novo sem cuidado | o pedido é processado duas vezes |
| esperar sem prazo | uma thread presa por serviço, para sempre |
| insistir num serviço caído | ele nunca se recupera, porque nunca para de receber |
| propagar só o dado | o rastro se perde na primeira fronteira |

Estes testes cobram os quatro — e o fazem contra um **servidor de
verdade**, com socket. Um cliente HTTP testado só com dublê não prova
nada sobre o que acontece quando o outro lado demora, fecha a conexão
ou devolve `Retry-After`.
"""

import json
import sys
import threading
import time

import pytest

sys.path.insert(0, ".")

from dataforge.stdlib import get_module
from dataforge.stdlib.arcane_malha import (Contexto, Disjuntor, REGISTRO,
                                           Saga, recuo)


@pytest.fixture
def M():
    return get_module("Arcane.Malha")


# ═══════════════════════════════════════════════════════════
#  Um serviço de verdade, para falar com
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def servico():
    """Um servidor HTTP que se comporta mal de propósito.

    Cada rota é um dos casos que separam um cliente que funciona de um
    que parece funcionar.
    """
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    estado = {"instavel": 0, "chamadas": [], "lento": 0.0}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _responder(self, status, corpo, extra=None):
            dados = json.dumps(corpo).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(dados)))
            for chave, valor in (extra or {}).items():
                self.send_header(chave, valor)
            self.end_headers()
            self.wfile.write(dados)

        def do_GET(self):
            estado["chamadas"].append({
                "caminho": self.path,
                "rastro": self.headers.get("X-Request-Id", ""),
                "origem": self.headers.get("X-Origem", ""),
                "ctx": {k[len("X-Ctx-"):].lower(): v
                        for k, v in self.headers.items()
                        if k.lower().startswith("x-ctx-")},
            })
            if self.path == "/ok":
                return self._responder(200, {"ok": True})
            if self.path == "/404":
                return self._responder(404, {"erro": "não achei"})
            if self.path == "/400":
                return self._responder(400, {"erro": "pedido errado"})
            if self.path == "/500":
                return self._responder(500, {"erro": "quebrado"})
            if self.path == "/429":
                return self._responder(429, {"erro": "devagar"},
                                       {"Retry-After": "0"})
            if self.path == "/instavel":
                estado["instavel"] += 1
                if estado["instavel"] < 3:
                    return self._responder(503, {"erro": "ainda não"})
                return self._responder(200, {"tentativas": estado["instavel"]})
            if self.path == "/lento":
                time.sleep(estado["lento"])
                return self._responder(200, {"ok": True})
            if self.path.startswith("/eco"):
                return self._responder(200, {"caminho": self.path})
            return self._responder(404, {"erro": "rota"})

        def do_POST(self):
            tamanho = int(self.headers.get("Content-Length") or 0)
            bruto = self.rfile.read(tamanho) if tamanho else b"{}"
            estado["chamadas"].append({
                "caminho": self.path,
                "rastro": self.headers.get("X-Request-Id", ""),
                "chave": self.headers.get("Idempotency-Key", ""),
                "corpo": bruto.decode(),
            })
            if self.path == "/500":
                return self._responder(500, {"erro": "quebrado"})
            return self._responder(201, {"criado": True})

    servidor = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    servidor.daemon_threads = True
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    porta = servidor.server_address[1]
    yield f"http://127.0.0.1:{porta}", estado
    servidor.shutdown()
    servidor.server_close()


# ═══════════════════════════════════════════════════════════
#  A chamada
# ═══════════════════════════════════════════════════════════

def test_uma_chamada_que_funciona(M, servico):
    base, _ = servico
    r = M["cliente"](base).get("/ok")
    assert r["ok"] and r["status"] == 200
    assert r["body"] == {"ok": True}
    assert r["ms"] > 0
    assert r["tentativas"] == 1


def test_um_erro_de_rede_devolve_vault_e_nao_levanta(M):
    """Quem chama um serviço precisa decidir o que fazer; um `monitor`
    em volta de cada chamada seria ruído."""
    # A porta 1 nunca aceita conexão.
    r = M["cliente"]("http://127.0.0.1:1", {"tentativas": 1}).get("/x")
    assert r["ok"] is False
    assert r["status"] == 0
    assert "erro" in r


def test_status_zero_distingue_nao_chegou_de_deu_erro(M, servico):
    """É o terceiro estado, e ele precisa ser distinguível de um 500:
    um 500 foi processado, e um 0 talvez não."""
    base, _ = servico
    quebrado = M["cliente"](base, {"tentativas": 1}).get("/500")
    sumido = M["cliente"]("http://127.0.0.1:1", {"tentativas": 1}).get("/x")
    assert quebrado["status"] == 500
    assert sumido["status"] == 0


def test_o_prazo_e_respeitado(M, servico):
    base, estado = servico
    estado["lento"] = 2.0
    comeco = time.perf_counter()
    r = M["cliente"](base, {"prazo": 0.3, "tentativas": 1}).get("/lento")
    decorrido = time.perf_counter() - comeco
    assert not r["ok"]
    # Sem prazo, isto esperaria os 2 s inteiros.
    assert decorrido < 1.5, f"esperou {decorrido:.2f}s"


# ═══════════════════════════════════════════════════════════
#  Retry: só o que é seguro
# ═══════════════════════════════════════════════════════════

def test_um_503_e_repetido_ate_passar(M, servico):
    base, _ = servico
    r = M["cliente"](base, {"tentativas": 4, "recuo": 0.01}).get("/instavel")
    assert r["ok"]
    assert r["tentativas"] == 3


@pytest.mark.parametrize("rota,codigo", [("/404", 404), ("/400", 400)])
def test_um_4xx_nao_e_repetido(M, servico, rota, codigo):
    """O pedido está errado, e mandar de novo dá o mesmo erro com mais
    latência."""
    base, estado = servico
    antes = len(estado["chamadas"])
    r = M["cliente"](base, {"tentativas": 4, "recuo": 0.01}).get(rota)
    assert r["status"] == codigo
    assert r["tentativas"] == 1
    assert len(estado["chamadas"]) - antes == 1


def test_um_post_nao_e_repetido_sem_chave(M, servico):
    """Um POST repetido pode cobrar duas vezes."""
    base, estado = servico
    antes = len(estado["chamadas"])
    r = M["cliente"](base, {"tentativas": 4, "recuo": 0.01}).post(
        "/500", {"valor": 1})
    assert r["tentativas"] == 1
    assert len(estado["chamadas"]) - antes == 1


def test_um_post_com_chave_de_idempotencia_e_repetido(M, servico):
    """Com a chave, é o **servidor** que garante que o efeito acontece
    uma vez — e aí repetir é seguro."""
    base, estado = servico
    antes = len(estado["chamadas"])
    r = M["cliente"](base, {"tentativas": 3, "recuo": 0.01}).post(
        "/500", {"valor": 1}, chave="abc-123")
    assert r["tentativas"] == 3
    assert len(estado["chamadas"]) - antes == 3
    assert estado["chamadas"][-1]["chave"] == "abc-123"


def test_o_retry_after_do_servidor_vence_o_recuo(M, servico):
    """Ele sabe quando vai estar pronto, e ignorar isso é insistir
    contra quem pediu para esperar.

    O limite é RELATIVO ao recuo configurado, e não um número fixo: a
    afirmação é "esperou muito menos que os 5 s que o recuo pediria",
    e máquina lenta só a reforça.
    """
    base, _ = servico
    recuo_configurado = 5.0
    # 'Retry-After: 0' significa "tente agora". Se o cabeçalho fosse
    # ignorado, o cliente esperaria o recuo inteiro.
    comeco = time.perf_counter()
    M["cliente"](base, {"tentativas": 2,
                        "recuo": recuo_configurado}).get("/429")
    decorrido = time.perf_counter() - comeco
    assert decorrido < recuo_configurado / 2, (
        f"esperou {decorrido:.2f}s de um recuo de {recuo_configurado}s: "
        f"o 'Retry-After: 0' foi ignorado")


def test_o_recuo_e_exponencial_e_com_tremor():
    """Sem tremor, cem clientes que falharam junto tentam de novo junto
    — e a rajada derruba o serviço que estava se recuperando."""
    sem = [recuo(n, base=1.0, tremor=False) for n in (1, 2, 3, 4)]
    assert sem == [1.0, 2.0, 4.0, 8.0]

    # Com tremor, vinte sorteios não podem dar todos o mesmo valor.
    com = {round(recuo(3, base=1.0), 6) for _ in range(20)}
    assert len(com) > 10
    assert all(0 <= v <= 4.0 for v in com)


def test_o_recuo_tem_teto():
    """Sem teto, a décima tentativa esperaria oito minutos."""
    assert recuo(20, base=1.0, teto=10.0, tremor=False) == 10.0


# ═══════════════════════════════════════════════════════════
#  Disjuntor
# ═══════════════════════════════════════════════════════════

def test_o_disjuntor_abre_e_para_de_tentar(M, servico):
    """Sem ele, um serviço que cai leva os que dependem dele: cada
    pedido espera o prazo inteiro, as threads acabam, e o que estava de
    pé cai também."""
    base, estado = servico
    cliente = M["cliente"](base, {
        "tentativas": 1, "disjuntor": {"falhas": 3, "espera": 30}})

    for _ in range(3):
        cliente.get("/500")
    assert cliente.disjuntor.estado == "aberto"

    antes = len(estado["chamadas"])
    r = cliente.get("/ok")
    assert not r["ok"]
    assert r["status"] == 0
    assert "disjuntor aberto" in r["erro"]
    assert r["tentativas"] == 0
    # E a chamada NÃO saiu.
    assert len(estado["chamadas"]) == antes


def test_um_4xx_nao_abre_o_disjuntor(M, servico):
    """4xx não é falha do serviço: o pedido está errado. Contar isso
    abriria o disjuntor por causa de um bug de quem chama."""
    base, _ = servico
    cliente = M["cliente"](base, {
        "tentativas": 1, "disjuntor": {"falhas": 2, "espera": 30}})
    for _ in range(5):
        cliente.get("/404")
    assert cliente.disjuntor.estado == "fechado"


def test_o_disjuntor_entreabre_e_fecha_no_sucesso(M, servico):
    base, _ = servico
    cliente = M["cliente"](base, {
        "tentativas": 1, "disjuntor": {"falhas": 2, "espera": 0.3}})
    for _ in range(2):
        cliente.get("/500")
    assert cliente.disjuntor.estado == "aberto"

    time.sleep(0.4)
    assert cliente.disjuntor.estado == "entreaberto"

    assert cliente.get("/ok")["ok"]
    assert cliente.disjuntor.estado == "fechado"


def test_a_sondagem_que_falha_reabre_e_reinicia_o_relogio():
    """Sem reiniciar, uma fila de threads sondaria em rajada."""
    d = Disjuntor(falhas=2, espera=0.3)
    d.registrar_falha()
    d.registrar_falha()
    time.sleep(0.4)
    assert d.estado == "entreaberto"

    d.registrar_falha()
    assert d.estado == "aberto"
    assert d.espera_restante() > 0.2


def test_o_entreaberto_evita_a_avalanche_na_volta():
    """Com cem threads esperando, abrir tudo de uma vez derruba o
    serviço no instante em que ele volta."""
    d = Disjuntor(falhas=1, espera=0.2)
    d.registrar_falha()
    assert not d.permite()
    time.sleep(0.3)
    # O estado muda para entreaberto, e a próxima passa.
    assert d.permite()


def test_o_disjuntor_e_seguro_entre_threads():
    d = Disjuntor(falhas=50, espera=30)

    def bater():
        for _ in range(100):
            d.registrar_falha()

    linhas = [threading.Thread(target=bater) for _ in range(4)]
    for t in linhas:
        t.start()
    for t in linhas:
        t.join()
    assert d.estado == "aberto"


def test_o_disjuntor_pode_ser_desligado(M, servico):
    base, _ = servico
    cliente = M["cliente"](base, {"tentativas": 1, "disjuntor": False})
    assert cliente.disjuntor is None
    for _ in range(10):
        cliente.get("/500")
    # Sem disjuntor, a décima primeira ainda sai.
    assert cliente.get("/ok")["ok"]


# ═══════════════════════════════════════════════════════════
#  Contexto
# ═══════════════════════════════════════════════════════════

def test_o_rastro_atravessa_a_fronteira(M, servico):
    """Sem um identificador que viaja com o pedido, investigar um
    incidente em cinco serviços é cruzar horário de log — impossível
    quando dois pedidos acontecem no mesmo segundo."""
    base, estado = servico
    M["comecar_contexto"](None, "pedidos")
    meu = M["rastro"]()
    try:
        M["cliente"](base).get("/ok")
        assert estado["chamadas"][-1]["rastro"] == meu
        assert estado["chamadas"][-1]["origem"] == "pedidos"
    finally:
        M["terminar_contexto"]()


def test_sem_contexto_nao_ha_cabecalho(M, servico):
    base, estado = servico
    M["terminar_contexto"]()
    M["cliente"](base).get("/ok")
    assert estado["chamadas"][-1]["rastro"] == ""


def test_o_extra_do_contexto_tambem_viaja(M, servico):
    base, estado = servico
    M["comecar_contexto"]("r-1", "web", {"tenant": "acme"})
    try:
        M["cliente"](base).get("/ok")
        assert estado["chamadas"][-1]["ctx"]["tenant"] == "acme"
    finally:
        M["terminar_contexto"]()


def test_propagar_continua_a_corrente(M):
    """É a metade que falta: sem ela, cada serviço começa um rastro novo
    e a corrente se quebra na fronteira."""
    pedido = {
        "headers": {"x-request-id": "veio-de-fora",
                    "x-ctx-tenant": "acme"},
        "state": {},
    }
    M["propagar"](pedido, "estoque")
    try:
        assert M["rastro"]() == "veio-de-fora"
        assert M["contexto"]()["extra"]["tenant"] == "acme"
        # E o rastro entra no estado do pedido, para o log alcançá-lo.
        assert pedido["state"]["rastro"] == "veio-de-fora"
    finally:
        M["terminar_contexto"]()


def test_propagar_sem_cabecalho_comeca_um_rastro(M):
    """A borda do sistema é onde o rastro nasce."""
    pedido = {"headers": {}, "state": {}}
    M["propagar"](pedido, "web")
    try:
        assert len(M["rastro"]()) > 8
    finally:
        M["terminar_contexto"]()


def test_o_contexto_e_por_thread(M):
    """Duas requisições ao mesmo tempo não podem misturar rastro."""
    vistos = {}

    def trabalhar(nome):
        Contexto.comecar(f"rastro-{nome}", nome)
        time.sleep(0.05)
        vistos[nome] = Contexto.atual()["rastro"]
        Contexto.terminar()

    linhas = [threading.Thread(target=trabalhar, args=(f"s{i}",))
              for i in range(5)]
    for t in linhas:
        t.start()
    for t in linhas:
        t.join()
    assert vistos == {f"s{i}": f"rastro-s{i}" for i in range(5)}


# ═══════════════════════════════════════════════════════════
#  Descoberta
# ═══════════════════════════════════════════════════════════

def test_registrar_e_achar(M, servico):
    base, _ = servico
    M["registrar"]("teste-estoque", base, {"tentativas": 1})
    assert M["onde"]("teste-estoque") == base
    assert M["de"]("teste-estoque").get("/ok")["ok"]


def test_o_cliente_e_reaproveitado(M, servico):
    """O disjuntor e as métricas vivem NO cliente: um cliente novo por
    chamada esqueceria que o serviço está caído, o que anula o
    disjuntor inteiro."""
    base, _ = servico
    M["registrar"]("teste-reuso", base)
    assert M["de"]("teste-reuso") is M["de"]("teste-reuso")


def test_a_variavel_de_ambiente_serve_de_fallback(M, monkeypatch):
    """É a convenção que o Compose e o Kubernetes já produzem."""
    monkeypatch.setenv("MEU_SERVICO_URL", "http://meu-servico:9000")
    assert M["onde"]("meu-servico") == "http://meu-servico:9000"


def test_um_host_sem_esquema_ganha_http(M, monkeypatch):
    monkeypatch.setenv("OUTRO_HOST", "outro:8080")
    assert M["onde"]("outro") == "http://outro:8080"


def test_um_servico_desconhecido_diz_como_registrar(M):
    with pytest.raises(Exception) as erro:
        M["de"]("nao-registrado-nenhum")
    assert "nao sei onde esta" in str(erro.value)
    assert "NAO_REGISTRADO_NENHUM_URL" in erro.value.nota


# ═══════════════════════════════════════════════════════════
#  Observar
# ═══════════════════════════════════════════════════════════

def test_as_metricas_contam_o_que_aconteceu(M, servico):
    base, _ = servico
    cliente = M["cliente"](base, {"tentativas": 3, "recuo": 0.01,
                                  "nome": "contado"})
    cliente.get("/ok")
    cliente.get("/404")
    cliente.get("/instavel")

    r = cliente.resumo()
    assert r["servico"] == "contado"
    assert r["chamadas"] == 3
    assert r["erros"] == 1
    assert r["media_ms"] > 0
    assert r["disjuntor"]["estado"] in ("fechado", "aberto", "entreaberto")


def test_a_saude_lista_os_clientes_ativos(M, servico):
    base, _ = servico
    M["registrar"]("teste-saude", base)
    M["de"]("teste-saude").get("/ok")
    nomes = {c["servico"] for c in M["saude"]()}
    assert "teste-saude" in nomes


# ═══════════════════════════════════════════════════════════
#  Sem dependência
# ═══════════════════════════════════════════════════════════

def test_a_malha_nao_importa_nada_de_fora():
    """A regra do projeto. O que falta no `urllib` — retry com recuo,
    disjuntor, propagação — é exatamente o que este módulo faz."""
    import ast
    import sys as _sys

    padrao = set(_sys.stdlib_module_names)
    arvore = ast.parse(open("dataforge/stdlib/arcane_malha.py",
                            encoding="utf-8").read())
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                assert alias.name.split(".")[0] in padrao, alias.name
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            assert no.module.split(".")[0] in padrao, no.module


def test_o_modulo_esta_registrado_pelos_tres_nomes():
    for nome in ("Arcane.Malha", "Malha", "Mesh"):
        modulo = get_module(nome)
        assert modulo is not None, nome
        assert modulo["__name__"] == "Arcane.Malha"


def test_o_catalogo_descreve_o_modulo():
    from dataforge.stdlib.catalogo import DESCRICOES
    assert "Arcane.Malha" in DESCRICOES


# ═══════════════════════════════════════════════════════════
#  Saga — escritas em serviços diferentes que precisam
#  acontecer juntas
#
#  Não existe transação que atravesse a rede: `BEGIN` no
#  serviço de estoque não alcança o de cobrança. A única
#  resposta correta é compensar, e compensar tem três modos de
#  dar errado: na ordem, no silêncio e na repetição.
# ═══════════════════════════════════════════════════════════

def _passos_de_teste():
    """Três passos que registram o que aconteceu, em ordem."""
    diario = []

    def fazer(nome, falha=None):
        def acao(estado, chave):
            diario.append(("fazer", nome, chave))
            if falha:
                raise RuntimeError(falha)
            return {nome: True}
        return acao

    def desfazer(nome, falha=None):
        def acao(estado, chave):
            diario.append(("desfazer", nome, chave))
            if falha:
                raise RuntimeError(falha)
        return acao

    return diario, fazer, desfazer


def test_a_saga_que_passa_nao_compensa_nada():
    diario, fazer, desfazer = _passos_de_teste()
    s = Saga("checkout")
    s.passo("a", fazer("a"), desfazer("a"))
    s.passo("b", fazer("b"), desfazer("b"))

    r = s.executar()
    assert r["ok"]
    assert r["concluidos"] == ["a", "b"]
    assert r["desfeitos"] == []
    assert [p for p, _, _ in diario] == ["fazer", "fazer"]


def test_a_compensacao_roda_em_ordem_inversa():
    """A ordem não é estética.

    Estornar a cobrança antes de liberar o estoque deixa uma janela em
    que o cliente não tem dinheiro nem produto.
    """
    diario, fazer, desfazer = _passos_de_teste()
    s = Saga("checkout")
    s.passo("reservar", fazer("reservar"), desfazer("reservar"))
    s.passo("cobrar", fazer("cobrar"), desfazer("cobrar"))
    s.passo("despachar", fazer("despachar", "transportadora caiu"),
            desfazer("despachar"))

    r = s.executar()
    assert not r["ok"]
    assert r["falhou_em"] == "despachar"
    assert r["desfeitos"] == ["cobrar", "reservar"]
    assert [n for tipo, n, _ in diario if tipo == "desfazer"] == [
        "cobrar", "reservar"]


def test_o_passo_que_falhou_nao_e_compensado():
    """Desfazer o que não aconteceu é o outro lado do mesmo bug.

    Um estorno de cobrança que nunca existiu devolve dinheiro que nunca
    foi cobrado.
    """
    diario, fazer, desfazer = _passos_de_teste()
    s = Saga("x")
    s.passo("a", fazer("a"), desfazer("a"))
    s.passo("b", fazer("b", "falhou"), desfazer("b"))

    r = s.executar()
    assert "b" not in r["desfeitos"]
    assert ("desfazer", "b", s.chave_de("b")) not in diario


def test_uma_compensacao_que_falha_vira_orfa_e_nao_para_as_outras():
    """Um estorno que não passa deixa o sistema inconsistente, e isso
    precisa chegar a um humano — engolir seria a pior falha possível.

    E as compensações seguintes ainda rodam: o estoque preso por um
    estorno que não passou seria um segundo problema criado pelo
    primeiro.
    """
    diario, fazer, desfazer = _passos_de_teste()
    s = Saga("x")
    s.passo("a", fazer("a"), desfazer("a"))
    s.passo("b", fazer("b"), desfazer("b", "gateway recusou"))
    s.passo("c", fazer("c", "falhou"), desfazer("c"))

    r = s.executar()
    assert not r["ok"]
    assert len(r["orfas"]) == 1
    assert r["orfas"][0]["passo"] == "b"
    assert "gateway" in r["orfas"][0]["erro"]
    # 'a' ainda foi desfeito, apesar de 'b' ter falhado ao desfazer.
    assert r["desfeitos"] == ["a"]


def test_a_saga_nao_levanta_nunca():
    """Levantar perderia a informação de quanto ela conseguiu desfazer
    — que é exatamente o que se precisa saber."""
    s = Saga("x")
    s.passo("a", lambda e, c: (_ for _ in ()).throw(ValueError("bum")))
    r = s.executar()
    assert r["ok"] is False
    assert "bum" in r["erro"]


def test_a_chave_de_idempotencia_e_estavel_entre_execucoes():
    """É o que permite reprocessar uma fila sem cobrar duas vezes."""
    a = Saga("checkout", "pedido-4711")
    b = Saga("checkout", "pedido-4711")
    assert a.chave_de("cobrar") == b.chave_de("cobrar") == "pedido-4711:cobrar"

    # Sagas diferentes, chaves diferentes — senão dois pedidos
    # distintos seriam confundidos com uma repetição.
    c = Saga("checkout", "pedido-4712")
    assert c.chave_de("cobrar") != a.chave_de("cobrar")


def test_a_chave_explicita_do_passo_vence():
    s = Saga("x", "id-1")
    s.passo("a", lambda e, c: None, chave="minha-chave")
    assert s.chave_de("a") == "minha-chave"


def test_o_passo_recebe_a_chave_que_chave_de_anuncia():
    """Se a chave passada ao passo divergisse da que `chave_de` informa,
    um serviço que guarda a chave para reconhecer repetição nunca
    reconheceria nada."""
    vistas = []
    s = Saga("x", "id-9")
    s.passo("cobrar", lambda e, c: vistas.append(c))
    s.executar()
    assert vistas == [s.chave_de("cobrar")]


def test_o_estado_atravessa_os_passos():
    s = Saga("x")
    s.passo("um", lambda e, c: {"valor": 10})
    s.passo("dois", lambda e, c: {"dobro": e["valor"] * 2})
    r = s.executar({"inicial": 1})
    assert r["estado"] == {"inicial": 1, "valor": 10, "dobro": 20}


def test_um_passo_que_devolve_algo_que_nao_e_vault_entra_pelo_nome():
    s = Saga("x")
    s.passo("score", lambda e, c: 700)
    r = s.executar()
    assert r["estado"]["score"] == 700


def test_um_passo_que_devolve_void_nao_mexe_no_estado():
    s = Saga("x")
    s.passo("log", lambda e, c: None)
    r = s.executar({"a": 1})
    assert r["estado"] == {"a": 1}


def test_conferir_acusa_o_passo_que_escreve_sem_compensacao():
    """Ele não falha em teste feliz: aparece no dia em que o passo
    seguinte falha, e aí já escreveu."""
    s = Saga("x")
    s.passo("consultar", lambda e, c: None, escreve=False)
    s.passo("reservar", lambda e, c: None, desfazer=lambda e, c: None)
    s.passo("marcar", lambda e, c: None)
    assert s.conferir() == ["marcar"]


def test_o_passo_sem_compensacao_e_pulado_no_desfazimento():
    diario, fazer, desfazer = _passos_de_teste()
    s = Saga("x")
    s.passo("ler", fazer("ler"), escreve=False)
    s.passo("escrever", fazer("escrever"), desfazer("escrever"))
    s.passo("cair", fazer("cair", "x"))
    r = s.executar()
    assert r["desfeitos"] == ["escrever"]


def test_o_diario_e_gravado_a_cada_passo_e_nao_no_fim():
    """Uma queda do processo no meio da saga perderia o que já foi
    feito, e ninguém saberia o que compensar."""
    linhas = []
    s = Saga("x", "id-1", registro=linhas.append)
    s.passo("a", lambda e, c: None, desfazer=lambda e, c: None)
    s.passo("b", lambda e, c: (_ for _ in ()).throw(RuntimeError("z")))
    s.executar()

    assert [l["situacao"] for l in linhas] == ["feito", "falhou", "desfeito"]
    assert [l["passo"] for l in linhas] == ["a", "b", "a"]
    assert all(l["id"] == "id-1" for l in linhas)
    assert all("ms" in l for l in linhas)


def test_um_diario_que_nao_grava_nao_derruba_a_saga():
    """Ela está no meio de escritas reais em serviços reais: falhar por
    causa do log seria trocar um problema pequeno por um grande."""
    def quebrado(linha):
        raise IOError("disco cheio")

    s = Saga("x", registro=quebrado)
    s.passo("a", lambda e, c: {"ok": 1})
    r = s.executar()
    assert r["ok"]
    assert r["estado"]["ok"] == 1


def test_o_diario_leva_o_rastro_do_contexto(M):
    """É o que liga o diário da saga ao log dos serviços que ela
    chamou."""
    Contexto.comecar("rastro-da-saga", "pedidos")
    try:
        s = Saga("x")
        s.passo("a", lambda e, c: None)
        r = s.executar()
        assert r["diario"][0]["rastro"] == "rastro-da-saga"
    finally:
        Contexto.terminar()


def test_a_saga_recusa_um_passo_que_nao_e_acao():
    s = Saga("x")
    with pytest.raises(ValueError, match="fazer"):
        s.passo("a", "nao sou acao")
    with pytest.raises(ValueError, match="desfazer"):
        s.passo("a", lambda e, c: None, desfazer=42)


def test_passo_devolve_a_saga_para_encadear():
    s = Saga("x")
    assert s.passo("a", lambda e, c: None) is s


def test_os_sinais_de_controle_atravessam_a_saga():
    """`halt`, `skip` e `yield` derivam de BaseException, e capturá-los
    faria um `halt` dentro de um passo virar 'a saga falhou'."""
    from dataforge.errors import YieldSignal

    s = Saga("x")
    s.passo("a", lambda e, c: (_ for _ in ()).throw(YieldSignal(7)))
    with pytest.raises(YieldSignal):
        s.executar()


def test_a_saga_esta_exposta_no_modulo(M):
    assert "saga" in M and "Saga" in M and "Passo" in M
    s = M["saga"]("checkout")
    assert isinstance(s, Saga)
    assert s.nome == "checkout"


def test_duas_sagas_nao_compartilham_estado(M):
    """O estado era um objeto de módulo em uma versão anterior deste
    desenho, e duas sagas no mesmo processo se viam."""
    a = M["saga"]("x")
    b = M["saga"]("x")
    a.passo("p", lambda e, c: {"v": 1})
    a.executar()
    assert b.estado == {}
    assert b.diario == []
    assert a.id != b.id
