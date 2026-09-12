"""O adaptador de depuração — falado contra o processo de verdade.

Um adaptador testado por chamada de função prova que os métodos
existem. O que quebra na prática é outra coisa: a ordem das mensagens, o
`initialized` que sai antes da resposta, o quadro que aponta a linha
errada, e o programa que não bloqueia de fato ao parar. Nada disso
aparece sem falar o protocolo por um cano.

Por isso estes testes sobem `dataforge dap` como subprocesso e escrevem
`Content-Length` na entrada dele, exatamente como o VS Code faz.
"""

import json
import os
import subprocess
import sys
import threading
import time

import pytest

sys.path.insert(0, ".")


# ═══════════════════════════════════════════════════════════
#  O cano
# ═══════════════════════════════════════════════════════════

class Cliente:
    """O lado do editor: manda pedido, recebe resposta e evento."""

    def __init__(self, cwd="."):
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "dataforge", "dap"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, cwd=cwd)
        self.seq = 0
        self.eventos = []
        self.respostas = {}
        self._trava = threading.Lock()
        self._parar = False
        self.thread = threading.Thread(target=self._ler_sempre, daemon=True)
        self.thread.start()

    # ── escrever ────────────────────────────────────────────

    def pedir(self, comando, **args):
        self.seq += 1
        mensagem = {"seq": self.seq, "type": "request", "command": comando}
        if args:
            mensagem["arguments"] = args
        bruto = json.dumps(mensagem).encode()
        self.proc.stdin.write(b"Content-Length: %d\r\n\r\n" % len(bruto))
        self.proc.stdin.write(bruto)
        self.proc.stdin.flush()
        return self.seq

    def chamar(self, comando, prazo=10.0, **args):
        """Manda e espera a resposta daquele pedido."""
        seq = self.pedir(comando, **args)
        limite = time.time() + prazo
        while time.time() < limite:
            with self._trava:
                if seq in self.respostas:
                    return self.respostas.pop(seq)
            time.sleep(0.005)
        raise AssertionError(f"'{comando}' não respondeu em {prazo}s\n"
                             f"eventos: {[e['event'] for e in self.eventos]}\n"
                             f"stderr: {self._stderr()}")

    # ── ler ─────────────────────────────────────────────────

    def _ler_sempre(self):
        fonte = self.proc.stdout
        while not self._parar:
            tamanho = None
            while True:
                linha = fonte.readline()
                if not linha:
                    return
                linha = linha.strip()
                if not linha:
                    break
                if linha.lower().startswith(b"content-length:"):
                    tamanho = int(linha.split(b":", 1)[1])
            if not tamanho:
                continue
            corpo = b""
            while len(corpo) < tamanho:
                pedaco = fonte.read(tamanho - len(corpo))
                if not pedaco:
                    return
                corpo += pedaco
            mensagem = json.loads(corpo.decode())
            with self._trava:
                if mensagem.get("type") == "event":
                    self.eventos.append(mensagem)
                elif mensagem.get("type") == "response":
                    self.respostas[mensagem["request_seq"]] = mensagem

    def esperar_evento(self, nome, prazo=10.0, depois_de=0):
        """O primeiro evento `nome` a partir do índice dado."""
        limite = time.time() + prazo
        while time.time() < limite:
            with self._trava:
                for i, e in enumerate(self.eventos):
                    if i >= depois_de and e["event"] == nome:
                        return i, e
            time.sleep(0.005)
        raise AssertionError(
            f"o evento '{nome}' não chegou em {prazo}s\n"
            f"chegaram: {[e['event'] for e in self.eventos]}\n"
            f"stderr: {self._stderr()}")

    def nomes_dos_eventos(self):
        with self._trava:
            return [e["event"] for e in self.eventos]

    def _stderr(self):
        try:
            self.proc.stderr.flush()
        except Exception:                               # noqa: BLE001
            pass
        return ""

    # ── o começo de toda sessão ─────────────────────────────

    def preparar(self, programa, paradas=(), **extra):
        r = self.chamar("initialize", adapterID="dataforge")
        assert r["success"], r
        self.esperar_evento("initialized")
        if paradas:
            self.chamar("setBreakpoints",
                        source={"path": os.path.abspath(programa)},
                        breakpoints=[{"line": n} for n in paradas])
        self.chamar("configurationDone")
        return self.chamar("launch", program=os.path.abspath(programa),
                           **extra)

    def fechar(self):
        self._parar = True
        try:
            self.pedir("disconnect")
            self.proc.stdin.close()
        except Exception:                               # noqa: BLE001
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()


@pytest.fixture
def cliente():
    c = Cliente()
    yield c
    c.fechar()


@pytest.fixture
def programa(tmp_path):
    """Um programa com ação, laço e aritmética — o bastante para
    exercitar entrar, passar por cima e sair."""
    arquivo = tmp_path / "conta.df"
    arquivo.write_text('''// 1
action dobrar(x):
    interno := x * 2
    yield interno

total := 0
cycle i from 1 to 3:
    total := total + dobrar(i)

nome := "fim"
vault_de_teste := {"a": 1, "b": [10, 20]}
out total
''', encoding="utf-8")
    return str(arquivo)


# ═══════════════════════════════════════════════════════════
#  A ordem das mensagens
# ═══════════════════════════════════════════════════════════

def test_initialized_sai_depois_da_resposta_de_initialize(cliente, programa):
    """É ele que autoriza o editor a mandar os breakpoints.

    Mandá-lo antes da resposta faz o cliente descartar a configuração —
    e o sintoma é uma sessão que sobe com os breakpoints ignorados, sem
    nenhum erro.
    """
    r = cliente.chamar("initialize", adapterID="dataforge")
    assert r["success"]
    assert r["body"]["supportsConfigurationDoneRequest"] is True
    cliente.esperar_evento("initialized")


def test_o_programa_roda_e_termina_sem_parada_nenhuma(cliente, programa):
    cliente.preparar(programa)
    cliente.esperar_evento("exited")
    cliente.esperar_evento("terminated")
    assert "stopped" not in cliente.nomes_dos_eventos()


def test_stop_on_entry_para_na_primeira_instrucao(cliente, programa):
    """A primeira instrução é `action dobrar(x):` — declarar liga o nome,
    e o interpretador executa isso.

    Note a assimetria com a linha 2 como PARADA: ali ela é movida para
    dentro do corpo, porque quem marca a linha de uma ação quer parar
    quando ela RODA, não quando é declarada. `stopOnEntry` é outra
    pergunta: "onde o programa começa".
    """
    cliente.preparar(programa, stopOnEntry=True)
    _, e = cliente.esperar_evento("stopped")
    assert e["body"]["reason"] == "step"
    pilha = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]
    assert pilha[0]["name"] == "(programa)"
    assert pilha[0]["line"] == 2


# ═══════════════════════════════════════════════════════════
#  Breakpoints
# ═══════════════════════════════════════════════════════════

def test_a_parada_dispara_na_linha_pedida(cliente, programa):
    cliente.preparar(programa, paradas=[10])
    _, e = cliente.esperar_evento("stopped")
    assert e["body"]["reason"] == "breakpoint"
    assert e["body"]["line"] == 10


def test_uma_parada_em_comentario_e_movida_para_a_proxima_instrucao(cliente,
                                                                    programa):
    """Uma parada em comentário ou linha vazia nunca dispara, e o editor
    a mostra acesa — o pior dos dois mundos. Ela é movida, e o painel
    mostra onde ficou de verdade.
    """
    cliente.chamar("initialize", adapterID="dataforge")
    cliente.esperar_evento("initialized")
    r = cliente.chamar("setBreakpoints",
                       source={"path": os.path.abspath(programa)},
                       breakpoints=[{"line": 1}])   # a linha '// 1'
    marcada = r["body"]["breakpoints"][0]
    assert marcada["verified"] is True
    assert marcada["line"] != 1, "a parada ficou num comentário"
    assert marcada["line"] == 3                     # 'interno := x * 2'


def test_uma_parada_depois_do_fim_e_recusada_com_explicacao(cliente, programa):
    cliente.chamar("initialize", adapterID="dataforge")
    cliente.esperar_evento("initialized")
    r = cliente.chamar("setBreakpoints",
                       source={"path": os.path.abspath(programa)},
                       breakpoints=[{"line": 900}])
    marcada = r["body"]["breakpoints"][0]
    assert marcada["verified"] is False
    assert "instrução" in marcada["message"]


def test_a_parada_dentro_de_uma_acao_mostra_a_pilha(cliente, programa):
    cliente.preparar(programa, paradas=[3])
    cliente.esperar_evento("stopped")
    pilha = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]
    assert len(pilha) >= 2
    assert pilha[0]["name"] == "dobrar"
    assert pilha[0]["line"] == 3
    # O de fora aponta a linha de onde CHAMOU — é o que leva o cursor ao
    # lugar certo quando se clica nele.
    assert pilha[1]["name"] == "(programa)"
    assert pilha[1]["line"] == 8


# ═══════════════════════════════════════════════════════════
#  Andar
# ═══════════════════════════════════════════════════════════

def test_continue_solta_o_programa_ate_o_fim(cliente, programa):
    cliente.preparar(programa, paradas=[10])
    cliente.esperar_evento("stopped")
    assert cliente.chamar("continue", threadId=1)["success"]
    cliente.esperar_evento("terminated")


def test_step_in_entra_na_acao(cliente, programa):
    cliente.preparar(programa, paradas=[8])       # a linha que chama
    i, _ = cliente.esperar_evento("stopped")
    cliente.chamar("stepIn", threadId=1)
    _, e = cliente.esperar_evento("stopped", depois_de=i + 1)
    pilha = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]
    assert pilha[0]["name"] == "dobrar", (
        f"stepIn não entrou: parou em {e['body']['line']}")


def test_next_passa_por_cima_da_acao(cliente, programa):
    """'próximo' anda na MESMA ação. Sem a comparação de profundidade,
    ele entraria na chamada — que é o que 'entrar' faz."""
    cliente.preparar(programa, paradas=[8])
    i, _ = cliente.esperar_evento("stopped")
    cliente.chamar("next", threadId=1)
    _, e = cliente.esperar_evento("stopped", depois_de=i + 1)
    pilha = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]
    assert pilha[0]["name"] == "(programa)", (
        "'próximo' entrou na ação em vez de passar por cima")


def test_step_out_volta_para_quem_chamou(cliente, programa):
    cliente.preparar(programa, paradas=[3])
    i, _ = cliente.esperar_evento("stopped")
    pilha = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]
    assert pilha[0]["name"] == "dobrar"

    cliente.chamar("stepOut", threadId=1)
    cliente.esperar_evento("stopped", depois_de=i + 1)
    pilha = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]
    assert pilha[0]["name"] == "(programa)"


def test_cada_continue_para_de_novo_na_volta_do_laco(cliente, programa):
    """A parada está no corpo de um `cycle` de três voltas: ela precisa
    disparar três vezes, e não uma."""
    cliente.preparar(programa, paradas=[8])
    vezes = 0
    depois = 0
    for _ in range(3):
        i, _e = cliente.esperar_evento("stopped", depois_de=depois)
        vezes += 1
        depois = i + 1
        cliente.chamar("continue", threadId=1)
    assert vezes == 3
    cliente.esperar_evento("terminated")


# ═══════════════════════════════════════════════════════════
#  Variáveis
# ═══════════════════════════════════════════════════════════

def _variaveis_de(cliente, quadro=None):
    if quadro is None:
        quadro = cliente.chamar("stackTrace", threadId=1)[
            "body"]["stackFrames"][0]["id"]
    escopos = cliente.chamar("scopes", frameId=quadro)["body"]["scopes"]
    achado = {}
    for escopo in escopos:
        vs = cliente.chamar("variables",
                            variablesReference=escopo["variablesReference"])
        for v in vs["body"]["variables"]:
            achado.setdefault(v["name"], v)
    return escopos, achado


def test_o_painel_mostra_as_variaveis_do_quadro(cliente, programa):
    cliente.preparar(programa, paradas=[11])       # depois do laço
    cliente.esperar_evento("stopped")
    _, vs = _variaveis_de(cliente)
    assert vs["total"]["value"] == "12"            # 2 + 4 + 6
    assert vs["nome"]["value"] == "fim"
    assert vs["nome"]["type"] == "String"
    assert vs["total"]["type"] == "Integer"


def test_as_embutidas_nao_aparecem(cliente, programa):
    """São 228, e elas vivem no escopo global: despejá-las enterra as
    três variáveis que a pessoa parou para ver."""
    cliente.preparar(programa, paradas=[11])
    cliente.esperar_evento("stopped")
    _, vs = _variaveis_de(cliente)
    assert "sqrt" not in vs
    assert "len" not in vs
    assert len(vs) < 30


def test_o_local_da_acao_aparece_e_nao_vaza_para_fora(cliente, programa):
    cliente.preparar(programa, paradas=[4])        # 'yield interno'
    cliente.esperar_evento("stopped")
    quadros = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]
    _, dentro = _variaveis_de(cliente, quadros[0]["id"])
    assert "interno" in dentro
    assert "x" in dentro

    # E o quadro de fora não vê o local da ação.
    _, fora = _variaveis_de(cliente, quadros[1]["id"])
    assert "interno" not in fora


def test_um_vault_abre_em_arvore(cliente, programa):
    cliente.preparar(programa, paradas=[12])
    cliente.esperar_evento("stopped")
    _, vs = _variaveis_de(cliente)
    alvo = vs["vault_de_teste"]
    assert alvo["variablesReference"] != 0, "o vault não abre"

    filhos = cliente.chamar("variables",
                            variablesReference=alvo["variablesReference"])
    por_nome = {v["name"]: v for v in filhos["body"]["variables"]}
    assert por_nome["a"]["value"] == "1"
    # E o cluster dentro dele também abre.
    assert por_nome["b"]["variablesReference"] != 0
    netos = cliente.chamar(
        "variables",
        variablesReference=por_nome["b"]["variablesReference"])
    assert [v["value"] for v in netos["body"]["variables"]] == ["10", "20"]


def test_um_numero_de_referencia_de_outra_parada_nao_responde_valor_velho(
        cliente, programa):
    """A tabela é limpa a cada parada. Um número de uma parada anterior
    aponta para um escopo que já não existe, e responder com ele
    mostraria valores velhos como se fossem os de agora."""
    cliente.preparar(programa, paradas=[8])
    i, _ = cliente.esperar_evento("stopped")
    escopos, _ = _variaveis_de(cliente)
    velho = escopos[0]["variablesReference"]

    cliente.chamar("continue", threadId=1)
    cliente.esperar_evento("stopped", depois_de=i + 1)

    r = cliente.chamar("variables", variablesReference=velho)
    assert r["body"]["variables"] == []


# ═══════════════════════════════════════════════════════════
#  Avaliar
# ═══════════════════════════════════════════════════════════

def test_avaliar_usa_o_quadro_onde_se_parou(cliente, programa):
    """Avaliar no global mostraria o valor errado — ou nenhum — para as
    variáveis locais, que são as que se quer ver ao parar dentro de uma
    ação."""
    cliente.preparar(programa, paradas=[4])
    cliente.esperar_evento("stopped")
    quadros = cliente.chamar("stackTrace", threadId=1)["body"]["stackFrames"]

    dentro = cliente.chamar("evaluate", expression="interno",
                            frameId=quadros[0]["id"])
    assert dentro["success"]
    assert dentro["body"]["result"] == "2"

    # No quadro de fora, 'interno' não existe — e a resposta diz isso,
    # em vez de inventar um valor.
    fora = cliente.chamar("evaluate", expression="interno",
                          frameId=quadros[1]["id"])
    assert not fora["success"]


def test_avaliar_uma_expressao_e_nao_so_um_nome(cliente, programa):
    cliente.preparar(programa, paradas=[11])
    cliente.esperar_evento("stopped")
    quadro = cliente.chamar("stackTrace", threadId=1)[
        "body"]["stackFrames"][0]["id"]
    r = cliente.chamar("evaluate", expression="total * 2 + len(nome)",
                       frameId=quadro)
    assert r["success"]
    assert r["body"]["result"] == "27"          # 12*2 + 3


def test_avaliar_algo_errado_devolve_a_mensagem_e_nao_derruba_a_sessao(
        cliente, programa):
    cliente.preparar(programa, paradas=[11])
    cliente.esperar_evento("stopped")
    r = cliente.chamar("evaluate", expression="nao_existe_isto")
    assert not r["success"]
    assert r.get("message")
    # A sessão continua de pé: o próximo pedido responde.
    assert cliente.chamar("threads")["success"]


def test_avaliar_um_vault_devolve_referencia_que_abre(cliente, programa):
    cliente.preparar(programa, paradas=[12])
    cliente.esperar_evento("stopped")
    r = cliente.chamar("evaluate", expression='{"x": 9}')
    assert r["success"]
    assert r["body"]["variablesReference"] != 0
    filhos = cliente.chamar(
        "variables", variablesReference=r["body"]["variablesReference"])
    assert filhos["body"]["variables"][0]["value"] == "9"


# ═══════════════════════════════════════════════════════════
#  Parar de verdade, e desistir
# ═══════════════════════════════════════════════════════════

def test_parado_significa_parado(cliente, programa):
    """O programa precisa BLOQUEAR ao parar.

    Se o depurador não bloqueasse — girando num `sleep`, por exemplo —
    o interpretador continuaria andando enquanto a pessoa olha o
    painel, e o valor no painel seria de um instante que já passou.
    """
    cliente.preparar(programa, paradas=[8])
    cliente.esperar_evento("stopped")
    _, antes = _variaveis_de(cliente)
    time.sleep(0.4)
    _, depois = _variaveis_de(cliente)
    assert antes["total"]["value"] == depois["total"]["value"]
    assert cliente.nomes_dos_eventos().count("stopped") == 1


def test_pause_para_um_laco_infinito(tmp_path):
    """O caso em que pausar é a única saída — e a razão de o laço do
    protocolo viver numa thread separada do programa: um adaptador que
    só responde quando já está parado não serve aqui."""
    arquivo = tmp_path / "infinito.df"
    arquivo.write_text('n := 0\npersist yes:\n    n := n + 1\n',
                       encoding="utf-8")
    c = Cliente()
    try:
        c.preparar(str(arquivo))
        time.sleep(0.4)
        assert "stopped" not in c.nomes_dos_eventos()
        assert c.chamar("pause", threadId=1)["success"]
        _, e = c.esperar_evento("stopped")
        assert e["body"]["reason"] == "step"
        _, vs = _variaveis_de(c)
        assert int(vs["n"]["value"]) > 0
    finally:
        c.fechar()


def test_disconnect_encerra_um_laco_infinito(tmp_path):
    """Sem isso o processo ficaria para sempre depois de fechar o
    editor. `_Encerrar` deriva de `BaseException` pelo mesmo motivo de
    `halt`: o interpretador embrulha toda `Exception` que sobe num
    `RuntimeError_`, e o pedido de encerrar viraria uma mensagem de erro
    no meio do programa."""
    arquivo = tmp_path / "infinito.df"
    arquivo.write_text('n := 0\npersist yes:\n    n := n + 1\n',
                       encoding="utf-8")
    c = Cliente()
    c.preparar(str(arquivo))
    time.sleep(0.3)
    c.pedir("disconnect")
    c.proc.stdin.close()
    c.proc.wait(timeout=10)
    assert c.proc.returncode == 0


def test_terminate_no_meio_de_uma_parada(cliente, programa):
    cliente.preparar(programa, paradas=[8])
    cliente.esperar_evento("stopped")
    assert cliente.chamar("terminate")["success"]
    cliente.esperar_evento("terminated")


# ═══════════════════════════════════════════════════════════
#  O que dá errado
# ═══════════════════════════════════════════════════════════

def test_um_arquivo_que_nao_compila_falha_com_o_erro_de_verdade(cliente,
                                                                tmp_path):
    """A mensagem útil é a do erro de sintaxe, e ela vai para o console
    do editor — não um 'launch failed' seco."""
    arquivo = tmp_path / "quebrado.df"
    arquivo.write_text("x := := 1\n", encoding="utf-8")
    r = cliente.preparar(str(arquivo))
    assert not r["success"]
    _, saida = cliente.esperar_evento("output")
    assert saida["body"]["category"] == "stderr"
    assert saida["body"]["output"].strip()


def test_um_arquivo_que_nao_existe_diz_o_caminho(cliente, tmp_path):
    r = cliente.preparar(str(tmp_path / "nao-existe.df"))
    assert not r["success"]
    assert "nao-existe.df" in r["message"]


def test_um_erro_em_execucao_vai_para_o_console_e_o_codigo_e_1(cliente,
                                                               tmp_path):
    arquivo = tmp_path / "estoura.df"
    arquivo.write_text("x := 1\nout x / 0\n", encoding="utf-8")
    cliente.preparar(str(arquivo))
    _, saida = cliente.esperar_evento("output")
    # A mensagem do DataForge, com arquivo e linha — e não um
    # 'Traceback' do Python, que não diz nada sobre o programa.
    assert "DivisionByZeroError" in saida["body"]["output"]
    assert "line 2" in saida["body"]["output"]
    assert "Traceback" not in saida["body"]["output"]
    _, fim = cliente.esperar_evento("exited")
    assert fim["body"]["exitCode"] == 1


def test_um_comando_que_nao_se_atende_responde_falha(cliente):
    """Responder com sucesso a um comando não atendido faria o editor
    esperar por um efeito que não vem."""
    cliente.chamar("initialize", adapterID="dataforge")
    r = cliente.chamar("goto", targetId=1)
    assert not r["success"]
    assert "goto" in r["message"]


def test_pedir_pilha_antes_de_lancar_nao_derruba(cliente):
    cliente.chamar("initialize", adapterID="dataforge")
    r = cliente.chamar("stackTrace", threadId=1)
    assert r["success"]
    assert r["body"]["stackFrames"] == []


# ═══════════════════════════════════════════════════════════
#  As duas metades não podem divergir
# ═══════════════════════════════════════════════════════════

def test_a_linha_executavel_e_a_mesma_da_cobertura():
    """A parada precisa cair numa linha que o interpretador executa, e a
    pergunta é a MESMA que a cobertura faz. Duas definições divergiriam,
    e a parada cairia onde a cobertura não conta."""
    import inspect

    from dataforge import dap
    fonte = inspect.getsource(dap.Sessao._linhas_executaveis)
    assert "from .cobertura import linhas_executaveis" in fonte, (
        "o DAP passou a ter a própria definição de linha executável")


def test_o_dap_nao_importa_nada_de_fora():
    import ast
    import sys as _sys

    padrao = set(_sys.stdlib_module_names)
    arvore = ast.parse(open("dataforge/dap.py", encoding="utf-8").read())
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                assert alias.name.split(".")[0] in padrao, alias.name
        elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
            assert no.module.split(".")[0] in padrao, no.module


def test_desligar_devolve_o_interpretador_ao_estado_de_origem():
    """`interp.execute = original` pareceria desfazer, mas cria de novo
    um atributo de INSTÂNCIA com o método ligado: o interpretador sairia
    da depuração carregando uma indireção que não tinha antes."""
    from dataforge.dap import Canal, DepuradorDAP
    from dataforge.interpreter import Interpreter

    interp = Interpreter()
    assert "execute" not in interp.__dict__
    d = DepuradorDAP(Canal(), interp, "x.df", "x := 1\n")
    d.ligar()
    assert "execute" in interp.__dict__
    d.desligar()
    assert "execute" not in interp.__dict__
    assert interp.compilar_corpos is True


# ═══════════════════════════════════════════════════════════
#  A extensão e o adaptador precisam concordar
#
#  A extensão declara os campos do `launch.json` e o comando
#  a iniciar. Se ela declarar um campo que o adaptador
#  ignora, o F5 sobe e a opção não faz nada — calada.
# ═══════════════════════════════════════════════════════════

def _pacote_da_extensao():
    caminho = os.path.join("editor", "vscode", "package.json")
    if not os.path.isfile(caminho):
        pytest.skip("a extensão não está neste checkout")
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def test_a_extensao_declara_o_depurador_e_os_breakpoints():
    c = _pacote_da_extensao()["contributes"]
    assert c["breakpoints"] == [{"language": "dataforge"}], (
        "sem isto o VS Code não deixa clicar na margem de um .df")
    tipos = [d["type"] for d in c["debuggers"]]
    assert tipos == ["dataforge"]


def test_todo_campo_do_launch_json_e_atendido_pelo_adaptador():
    """Um campo declarado e ignorado é pior que um campo ausente: a
    pessoa marca `stopOnEntry` e nada acontece, sem erro."""
    import inspect

    from dataforge import dap

    depurador = _pacote_da_extensao()["contributes"]["debuggers"][0]
    campos = set(depurador["configurationAttributes"]["launch"]["properties"])
    fonte = inspect.getsource(dap.Sessao.req_launch)
    for campo in campos:
        assert f'"{campo}"' in fonte, (
            f"a extensão oferece '{campo}' no launch.json e o adaptador "
            f"não o lê")


def test_o_adaptador_e_iniciado_pelo_subcomando_que_existe():
    """`DebugAdapterExecutable(exe, ['dap'])` — e `dataforge dap` tem de
    ser um comando de verdade, senão o F5 falha com 'exited with code
    2' e nada explicando."""
    caminho = os.path.join("editor", "vscode", "src", "depuracao.ts")
    if not os.path.isfile(caminho):
        pytest.skip("a extensão não está neste checkout")
    with open(caminho, encoding="utf-8") as f:
        fonte = f.read()
    assert "['dap']" in fonte

    r = subprocess.run([sys.executable, "-m", "dataforge", "dap", "--help"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert r.returncode == 0
    assert "Debug Adapter Protocol" in r.stdout


def test_a_configuracao_inicial_do_f5_roda_de_verdade(tmp_path):
    """O `initialConfigurations` é o que o VS Code usa quando ninguém
    escreveu `launch.json`. Ele precisa funcionar como está — com as
    variáveis do editor resolvidas."""
    depurador = _pacote_da_extensao()["contributes"]["debuggers"][0]
    inicial = dict(depurador["initialConfigurations"][0])
    assert inicial["program"] == "${file}"
    assert inicial["cwd"] == "${workspaceFolder}"

    arquivo = tmp_path / "f5.df"
    arquivo.write_text('x := 2\nout x * 21\n', encoding="utf-8")

    # O que o VS Code faz com as variáveis: substituí-las.
    args = {k: v for k, v in inicial.items()
            if k not in ("type", "request", "name")}
    args["program"] = str(arquivo)
    args["cwd"] = str(tmp_path)

    c = Cliente()
    try:
        c.chamar("initialize", adapterID="dataforge")
        c.esperar_evento("initialized")
        c.chamar("setBreakpoints", source={"path": str(arquivo)},
                 breakpoints=[{"line": 2}])
        c.chamar("configurationDone")
        r = c.chamar("launch", **args)
        assert r["success"], r
        c.esperar_evento("stopped")
        quadro = c.chamar("stackTrace", threadId=1)[
            "body"]["stackFrames"][0]["id"]
        v = c.chamar("evaluate", expression="x * 21", frameId=quadro)
        assert v["body"]["result"] == "42"
        c.chamar("continue", threadId=1)
        _, fim = c.esperar_evento("exited")
        assert fim["body"]["exitCode"] == 0
    finally:
        c.fechar()
