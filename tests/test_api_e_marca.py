"""
Testes da API pública, da marca e do catálogo de problemas.

Tudo aqui é gerado do código-fonte. Estes testes existem para que o
gerado não fique atrasado em relação à fonte — o mesmo problema que a
gramática do editor já teve.
"""

import json
import os
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "problemas"))

from dataforge import __version__                                # noqa: E402
from dataforge.builtins import get_builtins                      # noqa: E402
from dataforge.stdlib import get_module, list_modules            # noqa: E402
from dataforge.tokens import (                                   # noqa: E402
    CONTEXTUAIS_BLUEPRINT, CONTEXTUAIS_KILN, KEYWORDS,
)

API = os.path.join(RAIZ, "site", "public", "api")


def carregar(nome):
    caminho = os.path.join(API, f"{nome}.json")
    if not os.path.isfile(caminho):
        pytest.skip(f"{nome}.json ainda não foi gerado")
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


# ── A versão é uma só ────────────────────────────────────────

def test_versao_e_1_0_0():
    """A linguagem foi publicada como 1.0.0. Nada pode mostrar 4.x."""
    assert __version__ == "1.0.0"


@pytest.mark.parametrize("arquivo,marcador", [
    ("pyproject.toml", 'version = "1.0.0"'),
    ("Dockerfile", 'image.version="1.0.0"'),
    ("scripts/instalar.sh", "DATAFORGE_VERSION:-1.0.0"),
    ("editor/vscode/package.json", '"version": "1.0.0"'),
])
def test_versao_bate_em_todo_lugar(arquivo, marcador):
    conteudo = open(os.path.join(RAIZ, arquivo), encoding="utf-8").read()
    assert marcador in conteudo, f"{arquivo} não diz 1.0.0"


def test_nada_visivel_mostra_a_numeracao_antiga():
    """O usuário pediu 1.0.0 explicitamente; 4.x não pode aparecer."""
    import glob
    suspeitos = []
    alvos = (glob.glob(os.path.join(RAIZ, "site", "components", "*.tsx"))
             + [os.path.join(RAIZ, "scripts", "instalar.sh"),
                os.path.join(RAIZ, "scripts", "instalar.ps1"),
                os.path.join(RAIZ, "Dockerfile")])
    for caminho in alvos:
        texto = open(caminho, encoding="utf-8", errors="replace").read()
        for marca in ("v4.", "4.2.0", "4.1.0"):
            if marca in texto:
                suspeitos.append(f"{os.path.basename(caminho)}: {marca}")
    assert not suspeitos, f"versão antiga visível: {suspeitos}"


# ── A API descreve a linguagem de verdade ────────────────────

def test_api_tem_todas_as_rotas():
    indice = carregar("index")
    assert indice["versao"] == __version__
    for rota in ("sintaxe", "embutidas", "modulos", "comandos",
                 "erros", "conteudos"):
        assert rota in indice["rotas"]


def test_api_lista_exatamente_as_palavras_reservadas():
    sintaxe = carregar("sintaxe")
    da_api = {r["palavra"] for r in sintaxe["reservadas"]}
    assert da_api == set(KEYWORDS), (
        "a API divergiu de tokens.py — rode "
        "'python3 scripts/gerar_api.py'")


def test_api_lista_as_contextuais():
    sintaxe = carregar("sintaxe")
    da_api = {c["palavra"] for c in sintaxe["contextuais"]}
    assert da_api == set(CONTEXTUAIS_BLUEPRINT) | set(CONTEXTUAIS_KILN)


def test_toda_palavra_da_api_tem_significado():
    """Uma palavra sem descrição é um buraco na referência do painel."""
    sintaxe = carregar("sintaxe")
    mudas = [r["palavra"] for r in sintaxe["reservadas"]
             if not r["descricao"]]
    mudas += [c["palavra"] for c in sintaxe["contextuais"]
              if not c["descricao"]]
    assert not mudas, f"sem descrição em gerar_api.py: {sorted(mudas)}"


def test_api_lista_todas_as_embutidas():
    embutidas = carregar("embutidas")
    assert set(embutidas["funcoes"]) == set(get_builtins())


def test_api_lista_todos_os_modulos():
    api = carregar("modulos")
    nomes_reais = {get_module(n).get("__name__", n)
                   for n in set(list_modules())}
    nomes_api = {m["nome"] for m in api["modulos"]}
    assert nomes_api == nomes_reais
    assert api["total_simbolos"] > 700


def test_api_traz_os_comandos_da_cli():
    """A API lista os comandos; COMANDOS inclui apelidos ('i', 'ls', '-h').

    Comparar os dois conjuntos direto acusaria diferença sempre. O que
    importa é que todo comando de verdade esteja na API.
    """
    from dataforge.cli import GRUPOS
    api = carregar("comandos")
    da_api = {c["nome"] for g in api["grupos"] for c in g["comandos"]}
    reais = {c.nome for _, cmds in GRUPOS for c in cmds}
    assert da_api == reais


# ── A marca ──────────────────────────────────────────────────

def test_o_caminho_da_marca_foi_gerado():
    caminho = os.path.join(RAIZ, "site", "lib", "marca.ts")
    assert os.path.isfile(caminho), "rode tools/vetorizar_logo.py"
    conteudo = open(caminho, encoding="utf-8").read()
    assert "CAMINHO_MARCA" in conteudo
    assert "VIEWBOX_MARCA" in conteudo
    # Um caminho curto demais é sinal de que a vetorização degenerou.
    assert len(conteudo) > 5000


@pytest.mark.parametrize("arquivo", [
    "site/public/marca.svg",
    "site/app/icon.svg",
    "editor/vscode/marca.svg",
    "site/app/apple-icon.png",
    "editor/vscode/icone.png",
])
def test_variantes_da_marca_existem(arquivo):
    assert os.path.isfile(os.path.join(RAIZ, arquivo))


def test_favicon_tem_cor_propria_e_a_marca_herda():
    """currentColor só resolve inline; num <img> ou favicon vira preto."""
    inline = open(os.path.join(RAIZ, "site", "public", "marca.svg"),
                  encoding="utf-8").read()
    favicon = open(os.path.join(RAIZ, "site", "app", "icon.svg"),
                   encoding="utf-8").read()
    assert "currentColor" in inline
    assert "currentColor" not in favicon
    assert "#ea2845" in favicon


def test_o_svg_usa_evenodd():
    """Sem evenodd, os vãos (olho, boca, garras) somem."""
    svg = open(os.path.join(RAIZ, "site", "public", "marca.svg"),
               encoding="utf-8").read()
    assert 'fill-rule="evenodd"' in svg


# ── Problemas de prática ─────────────────────────────────────

def test_catalogo_tem_problemas_de_todas_as_dificuldades():
    from catalogo import PROBLEMAS
    dificuldades = {p["dificuldade"] for p in PROBLEMAS}
    assert dificuldades == {"facil", "medio", "dificil"}


def test_todo_problema_esta_completo():
    from catalogo import PROBLEMAS
    vistos = set()
    for p in PROBLEMAS:
        for campo in ("slug", "titulo", "dificuldade", "categoria",
                      "enunciado", "assinatura", "casos", "solucao"):
            assert p.get(campo), f"{p.get('slug')} sem {campo}"
        assert len(p["casos"]) >= 3, f"{p['slug']} tem poucos casos"
        assert p["slug"] not in vistos, f"slug repetido: {p['slug']}"
        vistos.add(p["slug"])


def test_toda_solucao_de_referencia_passa_nos_proprios_casos():
    """Um problema cuja solução não passa é um problema quebrado.

    Este é o teste que mais importa do arquivo: sem ele, alguém resolve
    o problema certo e recebe 'errado'.
    """
    sys.path.insert(0, os.path.join(RAIZ, "scripts"))
    from gerar_problemas import verificar
    from catalogo import PROBLEMAS

    quebrados = {}
    for p in PROBLEMAS:
        falhas = verificar(p)
        if falhas:
            quebrados[p["slug"]] = falhas[0][1]
    assert not quebrados, f"soluções que não passam: {quebrados}"


# ── O runtime para o navegador ───────────────────────────────

def test_o_pacote_web_existe_e_tem_a_linguagem_inteira():
    import zipfile
    caminho = os.path.join(RAIZ, "site", "public", "dataforge-web.zip")
    assert os.path.isfile(caminho), "rode scripts/gerar_runtime_web.py"

    with zipfile.ZipFile(caminho) as z:
        nomes = z.namelist()
    for exigido in ("dataforge/interpreter.py", "dataforge/parser.py",
                    "dataforge/lexer.py", "dataforge/stdlib/kiln.py",
                    "dataforge/stdlib/arcane_excel.py"):
        assert exigido in nomes, f"falta {exigido} no pacote web"


def test_o_pacote_web_e_reproduzivel():
    """Datas fixas: senão o navegador rebaixa o cache a cada build."""
    import zipfile
    caminho = os.path.join(RAIZ, "site", "public", "dataforge-web.zip")
    with zipfile.ZipFile(caminho) as z:
        datas = {info.date_time for info in z.infolist()}
    assert datas == {(1980, 1, 1, 0, 0, 0)}


# ── As migrações do Supabase ─────────────────────────────────

@pytest.mark.parametrize("arquivo", ["01_esquema.sql", "02_agendamentos.sql"])
def test_migracoes_existem(arquivo):
    assert os.path.isfile(os.path.join(RAIZ, "supabase", arquivo))


def test_toda_tabela_da_migracao_liga_rls():
    """Uma tabela sem RLS é pública para qualquer um com a chave anon."""
    import re
    texto = ""
    for arquivo in ("01_esquema.sql", "02_agendamentos.sql"):
        texto += open(os.path.join(RAIZ, "supabase", arquivo),
                      encoding="utf-8").read()

    criadas = set(re.findall(
        r"create table if not exists public\.(\w+)", texto))
    protegidas = set(re.findall(
        r"alter table public\.(\w+)\s+enable row level security", texto))

    assert criadas - protegidas == set(), (
        f"sem RLS: {sorted(criadas - protegidas)}")


def test_o_script_de_migracao_nao_tem_segredo_embutido():
    """Um token no fonte vaza no primeiro commit.

    Comentários podem citar o prefixo ('sbp_…'); o que não pode é um
    token de verdade, que tem dezenas de caracteres depois do prefixo.
    """
    import re
    fonte = open(os.path.join(RAIZ, "scripts", "supabase_aplicar.py"),
                 encoding="utf-8").read()

    padroes = {
        "token de gestão": r"sbp_[A-Za-z0-9]{20,}",
        "chave JWT":       r"eyJ[A-Za-z0-9_-]{30,}",
    }
    for nome, padrao in padroes.items():
        assert not re.search(padrao, fonte), f"{nome} embutido no script"


def test_credenciais_ficam_fora_do_git():
    """A service_role ignora RLS: se vazar, o banco inteiro vaza."""
    ignorados = open(os.path.join(RAIZ, ".gitignore"),
                     encoding="utf-8").read()
    assert ".supabase.local" in ignorados
    assert ".env" in ignorados
