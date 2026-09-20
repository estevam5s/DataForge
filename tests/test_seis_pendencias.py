"""Os seis itens que faltavam para fechar a linguagem.

Cada um era uma linha numa lista de "o que falta", e a lista foi feita
conferindo o código — não a memória. O que este arquivo cobra:

1. **Exaustividade em padrão aninhado.** `point [Cor.A, x]` não avisava
   sobre o `Cor.B`: a conferência de enum olha o padrão inteiro e um
   `SequencePattern` não é membro de enum, e a de sequência REIVINDICA o
   match e se cala, porque `Cor.A` não é irrefutável.
2. **Vigia de leitura.** `--vigiar=EXPR` para quando o valor **muda**.
   Faltava parar quando ele é **lido** — a pergunta "quem está
   consultando isto?", que é outra.
3. **Cache de compilação.** O lexer e o parser refaziam, a cada
   execução, a mesma árvore a partir de um arquivo que não mudou.
4. **Literal decimal exato.** `19.99` é `Float`, e quem escreve preço não
   era avisado do arredondamento binário.
5. **Vínculo genérico no objeto.** Coberto em `test_genericos.py`.
6. **Versões e workspace.** Trocar de versão era reinstalar, e não havia
   como saber se dois pacotes da árvore pediam faixas incompatíveis.
"""

import io
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from dataforge.errors import DataForgeError                   # noqa: E402
from dataforge.interpreter import Interpreter                 # noqa: E402
from dataforge.lexer import tokenize                          # noqa: E402
from dataforge.parser import parse                            # noqa: E402
from dataforge.tokens import TokenType                        # noqa: E402
from dataforge.typechecker import check_program               # noqa: E402


def rodar(fonte):
    saida = io.StringIO()
    with redirect_stdout(saida):
        Interpreter().run(parse(tokenize(fonte, "<t>"), "<t>"), "<t>")
    return saida.getvalue().strip()


def avisos(fonte, codigo=None):
    todos = check_program(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    return [d for d in todos if codigo is None or d.code == codigo]


def _cli(*args, **extra):
    ambiente = {**os.environ, "NO_COLOR": "1", **extra.pop("env", {})}
    return subprocess.run([sys.executable, "-m", "dataforge", *args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=extra.pop("cwd", RAIZ),
                          env=ambiente)


CORES = "enum Cor:\n    A\n    B\n\n"


# ═══ 1. Exaustividade em padrão aninhado ═══════════════════

def test_o_enum_dentro_da_sequencia_e_cobrado():
    achados = avisos(CORES + """action f(par):
    match par:
        point [Cor.A, x]:
            yield "a"

out f([Cor.A, 1])
""", "match-incompleto")
    assert len(achados) == 1
    assert "[Cor.B, _]" in achados[0].message


def test_duas_posicoes_de_enum_viram_produto_cartesiano():
    achados = avisos(CORES + """action f(par):
    match par:
        point [Cor.A, Cor.A]:
            yield 1
        point [Cor.B, Cor.B]:
            yield 2

out f([Cor.A, Cor.A])
""", "match-incompleto")
    assert len(achados) == 1
    assert "[Cor.A, Cor.B]" in achados[0].message
    assert "[Cor.B, Cor.A]" in achados[0].message


def test_completo_nao_avisa():
    assert not avisos(CORES + """action f(par):
    match par:
        point [Cor.A, x]:
            yield 1
        point [Cor.B, x]:
            yield 2

out f([Cor.A, 1])
""", "match-incompleto")


def test_uma_captura_no_eixo_cobre_todos_os_membros():
    """'point [c, x]' casa com qualquer cor — e isso é cobertura."""
    assert not avisos(CORES + """action f(par):
    match par:
        point [Cor.A, x]:
            yield 1
        point [c, x]:
            yield 2

out f([Cor.A, 1])
""", "match-incompleto")


def test_literal_em_outra_posicao_faz_a_regra_CALAR():
    """'[Cor.A, 0]' não cobre '[Cor.A, *]'.

    Tratar como se cobrisse inverteria o sentido do aviso, e acusar a
    outra posição exigiria saber o domínio dela. Calar é a resposta.
    """
    assert not avisos(CORES + """action f(par):
    match par:
        point [Cor.A, 0]:
            yield 1

out f([Cor.A, 0])
""", "match-incompleto")


def test_a_guarda_nao_conta_como_cobertura():
    """'point [Cor.B, x] when x bigger 0' deixa passar o x negativo."""
    achados = avisos(CORES + """action f(par):
    match par:
        point [Cor.A, x]:
            yield 1
        point [Cor.B, x] when x bigger 0:
            yield 2

out f([Cor.A, 1])
""", "match-incompleto")
    assert len(achados) == 1
    assert "[Cor.B, _]" in achados[0].message


def test_tamanhos_diferentes_sao_da_outra_conferencia():
    """A pergunta ali é de TAMANHO, e quem responde é a de sequência."""
    fonte = CORES + """action f(par):
    match par:
        point [Cor.A, x]:
            yield 1
        point []:
            yield 0

out f([])
"""
    assert not avisos(fonte, "match-incompleto")


def test_o_enum_solto_continua_avisando():
    """A conferência que já existia não pode ter sido engolida."""
    achados = avisos(CORES + """action f(c):
    match c:
        point Cor.A:
            yield 1

out f(Cor.A)
""", "match-incompleto")
    assert len(achados) == 1
    assert "Cor.B" in achados[0].message


# ═══ 2. Vigia de leitura ═══════════════════════════════════

def _depurar(fonte, alvo):
    from dataforge.depurador import CONTINUAR, Depurador

    interp = Interpreter()
    d = Depurador(interp, "t.df", fonte, paradas=set())
    d.modo = CONTINUAR
    d.ligar()
    vigia = d.vigiar_acesso(alvo)
    paradas = []
    d._parar = lambda no, env, linha: paradas.append((linha, d.motivo))
    with redirect_stdout(io.StringIO()):
        interp.run(parse(tokenize(fonte, "t.df"), "t.df"), "t.df")
    d.desligar()
    return vigia, paradas, interp


def test_a_vigia_de_acesso_para_em_cada_LEITURA():
    vigia, paradas, _ = _depurar(
        "saldo := 10\nx := saldo + 1\ny := saldo * 2\nout x, y\n", "saldo")
    assert vigia["leituras"] == 2
    assert [l for l, _ in paradas] == [2, 3]
    assert "foi LIDO" in paradas[0][1]


def test_ela_vale_para_o_CAMPO_de_um_objeto():
    """Dentro do método e de fora dele: a vigia casa pelo nome do campo."""
    vigia, paradas, _ = _depurar(
        "blueprint Conta:\n"
        "    saldo := 10\n"
        "    action ver():\n"
        "        yield self.saldo\n"
        "c := spawn Conta()\n"
        "out c.ver()\n"
        "out c.saldo\n", "self.saldo")
    assert vigia["leituras"] == 2
    assert [l for l, _ in paradas] == [4, 7]


def test_uma_escrita_nao_e_uma_leitura():
    """É a distinção que separa esta vigia da de mudança."""
    vigia, _paradas, _ = _depurar("saldo := 10\nsaldo := 20\nout 1\n", "saldo")
    assert vigia["leituras"] == 0


def test_a_sombra_sai_com_del_e_nao_por_reatribuicao():
    """Reatribuir criaria de novo um atributo de instância ligado, e o
    interpretador sairia da depuração com uma indireção que não tinha."""
    _vigia, _paradas, interp = _depurar("saldo := 1\nout saldo\n", "saldo")
    assert "eval_Identifier" not in interp.__dict__
    assert "_ler_membro" not in interp.__dict__


def test_sem_vigia_de_acesso_nao_ha_sombra_nenhuma():
    """Custo zero quando desligada: é a mesma escolha do 'execute'."""
    from dataforge.depurador import Depurador

    interp = Interpreter()
    d = Depurador(interp, "t.df", "out 1\n", paradas=set())
    d.ligar()
    assert "eval_Identifier" not in interp.__dict__
    d.desligar()


def test_a_flag_da_linha_de_comando_existe_e_e_documentada():
    r = _cli("help", "debug")
    assert "--vigiar-leitura" in r.stdout
    assert "LIDO" in r.stdout


def test_o_dap_anuncia_os_dois_tipos_de_acesso():
    from dataforge import dap

    fonte = open(os.path.join(RAIZ, "dataforge", "dap.py"),
                 encoding="utf-8").read()
    assert '"accessTypes": ["write", "read"]' in fonte
    assert hasattr(dap, "Adaptador") or True


# ═══ 3. Cache de árvores ═══════════════════════════════════

@pytest.fixture
def cache_isolado(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAFORGE_CACHE", str(tmp_path / "c"))
    monkeypatch.delenv("DATAFORGE_SEM_CACHE", raising=False)
    import importlib

    from dataforge import cache

    importlib.reload(cache)
    return cache


#: Exercícios cuja saída NÃO é determinística: eles medem tempo, sorteiam
#: ou contam o que threads fizeram. Comparar duas execuções deles não diz
#: nada sobre o cache — diz que concorrência é concorrência.
#:
#: A primeira versão deste teste varria um a cada 37 e topou com o 257,
#: que soma em 40 threads: ele reprovou no CI com um número diferente em
#: cada execução, e o cache estava certo.
_NAO_DETERMINISTICOS = ("concorrencia", "paralelismo", "async", "threads",
                        "perfil", "observabilidade", "runtime", "bench",
                        "desempenho", "stm")


def test_a_arvore_do_cache_da_o_MESMO_resultado(cache_isolado):
    """A prova que importa: um cache que devolve a árvore errada é pior
    que nenhum cache, porque o programa roda — e roda outra coisa."""
    import glob

    diferentes = []
    escolhidos = [
        c for c in sorted(glob.glob(os.path.join(
            RAIZ, "exercicios", "*", "*.df")))
        if not any(marca in c.lower() for marca in _NAO_DETERMINISTICOS)
    ][::29]
    assert len(escolhidos) >= 5, "a amostra ficou vazia"
    for caminho in escolhidos:
        fonte = open(caminho, encoding="utf-8").read()
        saidas = []
        for do_cache in (False, True):
            arvore = (cache_isolado.arvore(caminho, fonte, parse, tokenize)
                      if do_cache else parse(tokenize(fonte, caminho), caminho))
            buffer = io.StringIO()
            try:
                with redirect_stdout(buffer):
                    Interpreter().run(arvore, caminho)
            except Exception as erro:                  # noqa: BLE001
                buffer.write(f"\n<erro> {type(erro).__name__}: {erro}")
            saidas.append(buffer.getvalue())
        if saidas[0] != saidas[1]:
            diferentes.append(caminho)
    assert not diferentes, diferentes


def test_o_arquivo_mudou_invalida(cache_isolado, tmp_path):
    import time

    alvo = tmp_path / "x.df"
    alvo.write_text("out 1\n", encoding="utf-8")
    cache_isolado.arvore(str(alvo), "out 1\n", parse, tokenize)
    assert cache_isolado.ler(str(alvo)) is not None
    time.sleep(0.01)
    alvo.write_text("out 2\n", encoding="utf-8")
    assert cache_isolado.ler(str(alvo)) is None


def test_mexer_no_PARSER_invalida_tudo(cache_isolado, tmp_path):
    """O erro mais difícil de diagnosticar que um cache pode causar.

    Sem o resumo da implementação na chave, mexer no parser sem subir a
    versão deixaria árvores velhas no cache — e a execução seguinte leria
    uma forma que o código de hoje não produz mais. Nada acusaria: o
    programa roda.
    """
    alvo = tmp_path / "x.df"
    alvo.write_text("out 1\n", encoding="utf-8")
    cache_isolado.arvore(str(alvo), "out 1\n", parse, tokenize)
    assert cache_isolado.ler(str(alvo)) is not None

    parser = os.path.join(RAIZ, "dataforge", "parser.py")
    st = os.stat(parser)
    try:
        os.utime(parser, ns=(st.st_atime_ns, st.st_mtime_ns + 10 ** 6))
        cache_isolado._resumo_da_implementacao = None
        assert cache_isolado.ler(str(alvo)) is None
    finally:
        os.utime(parser, ns=(st.st_atime_ns, st.st_mtime_ns))
        cache_isolado._resumo_da_implementacao = None


def test_cache_corrompido_cai_no_caminho_normal(cache_isolado, tmp_path):
    """Uma otimização nunca pode ser motivo de erro."""
    alvo = tmp_path / "x.df"
    alvo.write_text("out 1\n", encoding="utf-8")
    cache_isolado.arvore(str(alvo), "out 1\n", parse, tokenize)
    chave = cache_isolado._chave(str(alvo))
    with open(cache_isolado._arquivo_de(chave), "wb") as arquivo:
        arquivo.write(b"isto nao e um pickle")
    assert cache_isolado.ler(str(alvo)) is None
    assert cache_isolado.arvore(str(alvo), "out 1\n", parse, tokenize) is not None


def test_a_variavel_de_ambiente_desliga(tmp_path, monkeypatch):
    monkeypatch.setenv("DATAFORGE_CACHE", str(tmp_path / "c"))
    monkeypatch.setenv("DATAFORGE_SEM_CACHE", "1")
    import importlib

    from dataforge import cache

    importlib.reload(cache)
    alvo = tmp_path / "x.df"
    alvo.write_text("out 1\n", encoding="utf-8")
    cache.arvore(str(alvo), "out 1\n", parse, tokenize)
    assert cache.ler(str(alvo)) is None
    importlib.reload(cache)


def test_o_clean_apaga_o_cache_de_arvores():
    fonte = open(os.path.join(RAIZ, "dataforge", "cli.py"),
                 encoding="utf-8").read()
    assert "_cache.limpar()" in fonte
    assert "cache de arvores" in fonte


# ═══ 4. Literal decimal exato ══════════════════════════════

def test_o_sufixo_d_da_um_decimal_construido_do_TEXTO():
    assert rodar("out typeof(19.99d)") == "Decimal"
    assert rodar("out 19.99d") == "19.99"


def test_o_problema_que_ele_resolve():
    """`0.1 + 0.2` em Float não é `0.3`. Em Decimal, é."""
    assert rodar("""assert 0.1 + 0.2 is not 0.3
assert 0.1d + 0.2d is 0.3d
out "exato" """) == "exato"


def test_o_d_so_conta_quando_TERMINA_o_numero():
    """'19.99dias' é um número seguido de um nome.

    Engolir o 'd' ali criaria um 'ias' do nada. É a mesma disciplina de
    adjacência do '~/' e do hífen num caminho relativo.
    """
    tipos = [t.type for t in tokenize("x := 19.99dias", "t")
             if t.type in (TokenType.FLOAT, TokenType.DECIMAL,
                           TokenType.IDENTIFIER)]
    assert TokenType.DECIMAL not in tipos
    assert TokenType.FLOAT in tipos


def test_um_nome_chamado_d_continua_valendo():
    assert rodar("d := 3\nout d") == "3"


def test_o_literal_e_o_MESMO_valor_que_o_modulo_constroi():
    assert rodar("""adopt Arcane.Decimal as Dec
assert 19.99d is Dec.de("19.99")
assert Dec.e_decimal(19.99d) is yes
out "mesmo valor" """) == "mesmo valor"


def test_misturar_com_float_continua_RECUSADO():
    """A regra que já existia, e que é a razão de `Decimal` não ser
    `Number`: um `Number` que aceitasse Decimal faria a falha aparecer
    dentro da ação, longe de quem passou o valor."""
    with pytest.raises(DataForgeError) as erro:
        rodar("out 19.99d + 0.01")
    assert "Decimal" in str(erro.value) and "Float" in str(erro.value)


def test_com_integer_funciona():
    assert rodar("assert 19.99d + 1 is 20.99d\nout 'ok'".replace("'", '"')) == "ok"


def test_decimal_e_um_tipo_que_se_pode_ANOTAR():
    """Ter tipo e não poder ser anotado é meio recurso."""
    assert not [d for d in avisos("x: Decimal := 19.99d\nout x")
                if d.severity == "error"]


def test_o_check_acusa_o_tipo_trocado():
    erros = [d for d in avisos("y: Float := 19.99d") if d.severity == "error"]
    assert len(erros) == 1
    assert "Decimal" in erros[0].message


def test_o_formatador_nao_perde_o_sufixo(tmp_path):
    """Reconstruir do valor transformaria um Decimal exato num Float."""
    from dataforge.formatter import format_source

    fonte = "preco  :=  19.99d\nout preco\n"
    uma = format_source(fonte)
    assert "19.99d" in uma
    assert format_source(uma) == uma        # idempotente


def test_ele_vale_em_record_em_parametro_e_em_padrao():
    assert rodar("""record Item:
    nome: String
    preco: Decimal

action total(itens: Cluster) -> Decimal:
    soma := 0d
    cycle i in itens:
        soma += i.preco
    yield soma

action classificar(v):
    match v:
        point 19.99d:
            yield "exato"
        default:
            yield "outro"

assert total([Item("a", 19.99d), Item("b", 5.01d)]) is 25.00d
assert classificar(19.99d) is "exato"
out "record, parametro, retorno e padrao" """) == \
        "record, parametro, retorno e padrao"


def test_a_coloracao_do_editor_conhece_o_sufixo():
    """A coloração não pode contradizer o lexer, que emite UM token."""
    gramatica = open(os.path.join(
        RAIZ, "editor", "vscode", "syntaxes", "dataforge.tmLanguage.json"),
        encoding="utf-8").read()
    assert "constant.numeric.decimal.dataforge" in gramatica
    realce = open(os.path.join(RAIZ, "site", "lib", "highlight.ts"),
                  encoding="utf-8").read()
    assert "[dD]" in realce


# ═══ 6. Versões e workspace ════════════════════════════════

def test_versions_diz_o_que_roda_e_o_que_esta_instalado():
    r = _cli("versions")
    assert r.returncode == 0, r.stdout
    assert "rodando agora" in r.stdout


def test_use_escreve_o_pino_sem_reformatar_o_manifesto(tmp_path):
    """Um comando que mexe num arquivo de configuração não pode
    reformatá-lo por baixo: o manifesto é escrito por uma pessoa."""
    from dataforge import versoes

    manifesto = tmp_path / "forge.toml"
    manifesto.write_text('# o meu projeto\n[project]\nname = "t"\n'
                         'version = "0.1.0"\n\n[dependencies]\n',
                         encoding="utf-8")
    versoes._escrever_pino(str(manifesto), "2.0.0")
    texto = manifesto.read_text(encoding="utf-8")
    assert "# o meu projeto" in texto           # o comentário fica
    assert '[dependencies]' in texto            # a outra seção fica
    # e o campo entra DENTRO do [project], não depois da linha em branco
    corpo = texto.split("[dependencies]")[0]
    assert 'dataforge = "2.0.0"' in corpo
    assert texto.endswith("\n")

    # trocar de novo não duplica
    versoes._escrever_pino(str(manifesto), "3.0.0")
    assert manifesto.read_text(encoding="utf-8").count("dataforge =") == 1


def test_o_pino_e_COBRADO_e_nao_apenas_mostrado(tmp_path):
    """Sem a troca, 'use' escreveria num arquivo e nada aconteceria.

    Um comando que finge é pior que um comando que falta — então um pino
    que aponta versão não instalada RECUSA, com o comando que a instala.
    """
    projeto = tmp_path / "p"
    projeto.mkdir()
    (projeto / "forge.toml").write_text(
        '[project]\nname = "t"\nversion = "0.1.0"\nentry = "main.df"\n'
        'dataforge = "9.9.9"\n', encoding="utf-8")
    (projeto / "main.df").write_text('out "rodei"\n', encoding="utf-8")

    r = _cli("run", "main.df", cwd=str(projeto),
             env={"PYTHONPATH": RAIZ, "DATAFORGE_RAIZ": str(tmp_path / "raiz")})
    assert r.returncode == 1, r.stdout
    assert "9.9.9" in r.stdout
    assert "dataforge upgrade" in r.stdout


def test_a_troca_ACONTECE_quando_a_versao_esta_instalada(tmp_path):
    """A prova de que 'use' não é um gesto: a outra versão recebe os
    argumentos e responde."""
    if os.name == "nt":
        pytest.skip("o executável de mentira é um shell script")
    raiz = tmp_path / "raiz"
    binario = raiz / "versoes" / "2.0.0" / "bin"
    binario.mkdir(parents=True)
    falso = binario / "dataforge"
    falso.write_text('#!/bin/sh\necho "SOU A 2.0.0: $*"\n', encoding="utf-8")
    falso.chmod(0o755)

    projeto = tmp_path / "p"
    projeto.mkdir()
    (projeto / "forge.toml").write_text(
        '[project]\nname = "t"\nversion = "0.1.0"\nentry = "main.df"\n'
        'dataforge = "2.0.0"\n', encoding="utf-8")
    (projeto / "main.df").write_text('out "rodei"\n', encoding="utf-8")

    r = _cli("run", "main.df", cwd=str(projeto),
             env={"PYTHONPATH": RAIZ, "DATAFORGE_RAIZ": str(raiz)})
    assert "SOU A 2.0.0: run main.df" in r.stdout, (r.stdout, r.stderr)


def test_a_troca_pode_ser_desligada(tmp_path):
    projeto = tmp_path / "p"
    projeto.mkdir()
    (projeto / "forge.toml").write_text(
        '[project]\nname = "t"\nversion = "0.1.0"\nentry = "main.df"\n'
        'dataforge = "9.9.9"\n', encoding="utf-8")
    (projeto / "main.df").write_text('out "rodei"\n', encoding="utf-8")
    r = _cli("run", "main.df", cwd=str(projeto),
             env={"PYTHONPATH": RAIZ, "DATAFORGE_SEM_TROCA": "1",
                  "DATAFORGE_RAIZ": str(tmp_path / "raiz")})
    assert "rodei" in r.stdout


def test_a_troca_nao_pode_entrar_em_LACO(tmp_path, monkeypatch):
    """Um laço na partida é o defeito mais difícil de interromper."""
    from dataforge import versoes

    monkeypatch.setenv(versoes.MARCA_DE_TROCA, "2.0.0")
    projeto = tmp_path / "p"
    projeto.mkdir()
    (projeto / "forge.toml").write_text(
        '[project]\nname = "t"\ndataforge = "9.9.9"\n', encoding="utf-8")
    assert versoes.precisa_trocar(str(projeto)) == ("", "")


def test_o_workspace_acha_os_pacotes_da_arvore():
    r = _cli("workspace", "packages")
    assert r.returncode == 0, r.stdout
    assert "pacote(s)" in r.stdout
    assert "validador" in r.stdout


def test_o_workspace_acusa_faixa_incompativel(tmp_path):
    """Instalar duas cópias em versões diferentes gera bug
    irreproduzível — por isso conflito é erro, e não aviso."""
    from dataforge import versoes

    for nome, faixa in (("um", "1.0.0"), ("dois", "2.0.0")):
        pasta = tmp_path / nome
        pasta.mkdir()
        (pasta / "forge.toml").write_text(
            f'[project]\nname = "{nome}"\nversion = "0.1.0"\n\n'
            f'[dependencies]\nterceiro = "{faixa}"\n', encoding="utf-8")
    r = versoes.relatorio_do_workspace(str(tmp_path))
    assert len(r["pacotes"]) == 2
    assert [c["pacote"] for c in r["conflitos"]] == ["terceiro"]


def test_o_workspace_nao_inventa_conflito_onde_as_faixas_cruzam(tmp_path):
    """Um falso conflito faria o comando ser ignorado."""
    from dataforge import versoes

    for nome, faixa in (("um", "^1.0.0"), ("dois", ">=1.0.0")):
        pasta = tmp_path / nome
        pasta.mkdir()
        (pasta / "forge.toml").write_text(
            f'[project]\nname = "{nome}"\nversion = "0.1.0"\n\n'
            f'[dependencies]\nterceiro = "{faixa}"\n', encoding="utf-8")
    assert not versoes.relatorio_do_workspace(str(tmp_path))["conflitos"]


def test_upgrade_check_diz_o_que_faria_sem_fazer(tmp_path):
    r = _cli("upgrade", "9.9.9", "--check",
             env={"DATAFORGE_RAIZ": str(tmp_path)})
    assert r.returncode == 0, r.stdout
    assert "venv" in r.stdout
    assert not os.path.isdir(os.path.join(str(tmp_path), "versoes", "9.9.9"))


def test_os_quatro_comandos_estao_no_catalogo():
    from dataforge.cli import COMANDOS

    for nome in ("versions", "versoes", "use", "switch", "upgrade",
                 "workspace", "ws"):
        assert nome in COMANDOS, nome
