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


#: A mensagem de uma falha de CI vive numa LINHA. O resumo do pytest
#: corta no primeiro '\n', e a anotação do job é montada do resumo — foi
#: assim que três reprovações no Windows chegaram aqui dizendo apenas
#: "packaging\arch\PKGBUILD", que é a primeira linha de um stdout de
#: sucesso. O traceback estava no log do job, que exige autenticação.
def _uma_linha(r, quanto=1500):
    """O stdout e o stderr numa linha só, com a CAUDA preservada."""
    junto = ((r.stdout or "") + "\n" + (r.stderr or "")).strip()
    return " ⏎ ".join(junto.splitlines())[-quanto:]


def carregar(nome):
    caminho = os.path.join(API, f"{nome}.json")
    if not os.path.isfile(caminho):
        pytest.skip(f"{nome}.json ainda não foi gerado")
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


# ── A versão é uma só ────────────────────────────────────────

def test_a_versao_e_a_da_serie_1():
    """A linguagem foi publicada como 1.x. Nada pode mostrar 4.x.

    Antes isto se chamava `test_versao_e_1_0_0` e afirmava o numero
    exato. O nome de um teste nao pode conter o numero que ele confere:
    subir para 1.1.0 obrigava a RENOMEAR a funcao, e renomear e
    exatamente o que se esquece — o teste passa a reprovar o release
    correto, e a saida mais rapida e apaga-lo.
    """
    assert __version__.startswith("1."), __version__
    assert len(__version__.split(".")) == 3, __version__


#: Onde a versao aparece, e com que moldura em cada arquivo.
#:
#: O marcador e um MOLDE com '{v}', e nao o texto pronto: assim a lista
#: continua valendo depois de um bump, e o unico lugar que muda e
#: 'dataforge/__init__.py'.
MOLDES_DE_VERSAO = [
    ("pyproject.toml", 'version = "{v}"'),
    ("Dockerfile", 'image.version="{v}"'),
    ("scripts/instalar.sh", "DATAFORGE_VERSION:-{v}"),
    ("editor/vscode/package.json", '"version": "{v}"'),
    ("packaging/windows/scoop/dataforge.json", '"version": "{v}"'),
]


@pytest.mark.parametrize("arquivo,molde", MOLDES_DE_VERSAO)
def test_versao_bate_em_todo_lugar(arquivo, molde):
    conteudo = open(os.path.join(RAIZ, arquivo), encoding="utf-8").read()
    marcador = molde.format(v=__version__)
    assert marcador in conteudo, (
        f"{arquivo} nao diz {__version__} (procurei por {marcador!r})")


def test_nada_visivel_mostra_a_numeracao_antiga():
    """O usuário pediu 1.0.0 explicitamente; 4.x não pode aparecer.

    A busca é sobre o que fica **visível**, e por isso ignora
    comentário: a primeira versão acusou um `v4.03` que era uma
    coordenada dentro de um `path` de SVG e, depois, o comentário que
    explicava essa própria armadilha.

    É a terceira vez que uma trava deste repositório acusa a própria
    explicação — as outras duas foram o marcador `TODO` no lint e o
    `Math.random` no mapa 3D. A correção é sempre a mesma: olhar o
    código, e não o arquivo inteiro.
    """
    import glob
    import re

    def sem_comentario(texto, caminho):
        if caminho.endswith((".tsx", ".ts")):
            texto = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)
            return re.sub(r"^\s*//.*$", "", texto, flags=re.M)
        if caminho.endswith((".sh", ".ps1")) or caminho.endswith("Dockerfile"):
            return re.sub(r"^\s*#.*$", "", texto, flags=re.M)
        return texto

    suspeitos = []
    alvos = (glob.glob(os.path.join(RAIZ, "site", "components", "*.tsx"))
             + [os.path.join(RAIZ, "scripts", "instalar.sh"),
                os.path.join(RAIZ, "scripts", "instalar.ps1"),
                os.path.join(RAIZ, "Dockerfile")])
    for caminho in alvos:
        bruto = open(caminho, encoding="utf-8", errors="replace").read()
        texto = sem_comentario(bruto, caminho)
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
    # O amarelo do logo original, não o acento do site: a marca tem uma
    # cor, e ela não muda porque o tema da página é outro.
    assert "#FED403" in favicon


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

@pytest.mark.parametrize("arquivo", [
    "01_esquema.sql", "02_agendamentos.sql", "03_solucoes.sql"])
def test_migracoes_existem(arquivo):
    assert os.path.isfile(os.path.join(RAIZ, "supabase", arquivo))


def test_a_view_publica_nao_expoe_a_solucao():
    """O Postgres não faz RLS por coluna.

    Uma política que liberasse a linha de 'problemas' entregaria a
    resposta junto com o enunciado — foi o que aconteceu, e a saída foi
    esta view com as colunas explícitas. 'select *' aqui traria a
    solução de volta sem ninguém notar.
    """
    import re
    sql = open(os.path.join(RAIZ, "supabase", "03_solucoes.sql"),
               encoding="utf-8").read()

    corpo = sql[sql.index("create view public.problemas_publicos"):]
    corpo = corpo[:corpo.index(";")]

    assert "select *" not in corpo, "a view precisa listar as colunas"
    assert "solucao" not in corpo, "a view voltou a expor a solução"
    assert "where publicado" in corpo, "a view mostraria problemas ocultos"


def test_a_tabela_crua_de_problemas_e_so_de_admin():
    sql = open(os.path.join(RAIZ, "supabase", "03_solucoes.sql"),
               encoding="utf-8").read()
    assert 'drop policy if exists "problemas: publicados para todos"' in sql
    assert "e_admin()" in sql


def test_o_cliente_le_a_view_e_nao_a_tabela():
    fonte = open(os.path.join(RAIZ, "site", "lib", "supabase", "pratica.ts"),
                 encoding="utf-8").read()
    assert "from('problemas_publicos')" in fonte
    assert "rpc('solucao_de'" in fonte
    assert "from('problemas')\n" not in fonte


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


# ── Os códigos publicados na documentação ────────────────────

def test_todo_bloco_de_codigo_da_documentacao_compila():
    """Um trecho na doc que não compila ensina errado.

    Foi um problema real: o usuário copiou um exemplo, rodou e recebeu
    erro de sintaxe. A causa estava no lexer (comentário começando com
    número virava divisão), mas ninguém teria notado sem esta varredura.
    """
    import importlib.util

    caminho = os.path.join(RAIZ, "tools", "verificar_docs.py")
    spec = importlib.util.spec_from_file_location("verificar_docs", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    falhas = []
    for bloco in modulo.blocos_das_paginas():
        tipo = modulo.classificar(bloco)
        if tipo == "outro":
            continue
        if tipo == "lavra":
            # A linguagem de consulta do Lavra tem leitor proprio.
            erro = modulo.conferir_consulta_lavra(bloco["codigo"])
            if erro:
                falhas.append(f"{bloco['rota']}:{bloco['linha']} — {erro}")
            continue
        try:
            parse(tokenize(modulo.preparar(bloco["codigo"], tipo)))
        except Exception as erro:
            falhas.append(f"{bloco['rota']}:{bloco['linha']} — "
                          f"{str(erro).splitlines()[0][:80]}")

    assert not falhas, (
        f"{len(falhas)} bloco(s) não compilam:\n  " + "\n  ".join(falhas[:8]))


# ── Comentário que começa com número ─────────────────────────

@pytest.mark.parametrize("fonte,esperado", [
    ("out 7 // 2", "3"),
    ("out 100 // 7", "14"),
    ("out (10 + 4) // 2", "7"),
    ("out 9 // 2 + 1", "5"),
    ("a := 20\nout a // 3", "6"),
    ("out 7 // 2  // resultado inteiro", "3"),
])
def test_divisao_inteira_continua_funcionando(fonte, esperado):
    import io
    from contextlib import redirect_stdout
    from dataforge.interpreter import Interpreter
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        Interpreter().run(parse(tokenize(fonte)))
    assert buffer.getvalue().strip() == esperado


@pytest.mark.parametrize("fonte", [
    'x := 1   // 200, application/json',
    'x := 1   // 302, temporário',
    'x := 1   // 404 não achei',
    'x := 1   // 2 é o dobro',
    'x := 1   // 405 com Allow',
    'x := 1   // 90 dias de retenção',
])
def test_comentario_que_comeca_com_numero_e_comentario(fonte):
    """'// 200, application/json' virava divisão e quebrava o programa.

    Comentário de status HTTP é comum em documentação, e o erro
    aparecia numa linha que não tinha nada a ver com a causa.
    """
    from dataforge.interpreter import Interpreter
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    Interpreter().run(parse(tokenize(fonte)))   # não pode levantar


# ── O sticky da landing ──────────────────────────────────────

def test_o_ancestral_da_barra_nao_tem_overflow():
    """`overflow` num ancestral desliga o `sticky` do filho.

    Não há erro e não há aviso: o elemento simplesmente vira
    `relative` e some depois da primeira dobra. Foi o que aconteceu
    quando `.lp` ganhou `overflow-x: clip` para conter os brilhos de
    fundo — e a barra parou de acompanhar o site inteiro.

    O clip continua existindo, mas nas SEÇÕES, onde os brilhos
    nascem — e a barra é isenta por classe.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css = open(os.path.join(raiz, "site", "app", "globals.css"),
               encoding="utf-8").read()

    # O bloco `.lp { … }` — só ele, não `.lp-mono` nem `.lp > *`.
    bloco = re.search(r"\n\.lp\s*\{(.*?)\n\}", css, re.S)
    assert bloco, "não achei a regra .lp"
    assert "overflow" not in bloco.group(1), (
        "'.lp' voltou a ter overflow — isso desliga o sticky da barra")


def test_a_barra_da_landing_e_sticky_e_isenta_do_clip():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    nav = open(os.path.join(raiz, "site", "components", "landing",
                            "NavSite.tsx"), encoding="utf-8").read()
    css = open(os.path.join(raiz, "site", "app", "globals.css"),
               encoding="utf-8").read()

    assert "lp-barra" in nav, "a barra perdeu a classe que a isenta"
    assert "sticky" in nav
    assert ".lp > .lp-barra" in css, "a isenção sumiu do CSS"


def test_o_favicon_tem_um_desenho_por_tamanho():
    """O de 16px não pode ser um downscale do de 256.

    O PIL, ao salvar ICO com `sizes`, grava UMA imagem e reduz para as
    outras — e a versão pequena vira o borrão que a simplificação
    existe para evitar. Por isso o .ico é escrito à mão.

    O Pillow é dependência de desenvolvimento (`pip install -e .[dev]`),
    não do runtime: quem só roda DataForge não precisa dele. Sem ele
    instalado o teste diz isso, em vez de estourar um ImportError que
    parece defeito do repositório.
    """
    Image = pytest.importorskip(
        "PIL.Image", reason="o favicon é conferido com Pillow: pip install -e '.[dev]'")

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "app", "favicon.ico")
    if not os.path.isfile(caminho):
        pytest.skip("favicon ainda não foi gerado")

    imagem = Image.open(caminho)
    tamanhos = sorted(imagem.info.get("sizes", []))
    assert (16, 16) in tamanhos, "falta o tamanho que a aba usa"
    assert len(tamanhos) >= 4, f"só {len(tamanhos)} tamanho(s)"

    # O de 16 é desenhado à parte: ele tem menos cores distintas que um
    # downscale teria, porque é uma silhueta sólida.
    pequeno = Image.open(caminho)
    pequeno.size = (16, 16)
    pequeno.load()
    cores = len(set(pequeno.convert("RGB").getdata()))
    assert cores < 200, f"o de 16px parece um downscale ({cores} cores)"


# ── O índice lateral tem de descrever a própria página ────────

def test_o_indice_de_cada_pagina_bate_com_o_conteudo():
    """`headings` e `blocos` eram mantidos à mão, e divergiram em 50 páginas.

    O resultado não é uma página quebrada — é pior: a página abre, o
    texto está todo lá, e só o sumário mente. Seções que existem não
    aparecem no índice, e âncoras do índice não levam a lugar nenhum
    porque o `id` foi escrito diferente do que `slugify` calcula.

    Agora o índice é **gerado** do conteúdo. Este teste é a trava.
    """
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = subprocess.run(
        [sys.executable, os.path.join(raiz, "site", "scripts",
                                      "gerar_indices.py"), "--check"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz, timeout=120)
    assert r.returncode == 0, (
        "o índice lateral divergiu do conteúdo — rode "
        "'python3 site/scripts/gerar_indices.py':\n" + r.stdout + r.stderr)


def test_a_slugify_do_gerador_e_a_do_componente():
    """Duas implementações da mesma regra é como o `id` deixou de bater.

    O gerador é Python e o componente é TypeScript, então há mesmo duas.
    O que não pode é elas discordarem — quando discordam, o link do
    índice aponta para uma âncora que não existe e ninguém percebe.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(raiz, "site", "scripts"))
    from gerar_indices import slugify           # noqa: E402

    fonte = open(os.path.join(raiz, "site", "components", "Doc.tsx"),
                 encoding="utf-8").read()
    corpo = fonte[fonte.index("export function slugify"):]
    corpo = corpo[:corpo.index("\n}")]

    # As mesmas etapas, na mesma ordem.
    for etapa in ("toLowerCase", "normalize('NFD')", "trim"):
        assert etapa in corpo, f"o componente nao faz mais '{etapa}'"
    assert re.search(r"\[\^a-z0-9\\s-\]", corpo), \
        "o conjunto de caracteres aceitos mudou no componente"

    casos = [
        ("Sem Python na máquina", "sem-python-na-maquina"),
        ("HMAC — autenticar mensagens", "hmac-autenticar-mensagens"),
        ("Windows (PowerShell)", "windows-powershell"),
        # O 'trim' roda ANTES da troca de espaco por traco, entao nao
        # sobra traco na ponta.
        ("~/ em vez de //", "em-vez-de"),
        ("1.0.0 — o lançamento", "100-o-lancamento"),
    ]
    for texto, esperado in casos:
        assert slugify(texto) == esperado, f"{texto!r} -> {slugify(texto)!r}"


# ── Nenhum numero global defasado ────────────────────────────

#: Onde um número **global** pode aparecer escrito à mão.
#:
#: Fora daqui, um número seguido de "módulos"/"exercícios" costuma ser
#: local e correto: a página do módulo 01 diz "12 exercícios" porque são
#: doze naquele módulo, e a do pacote `moeda` diz "24 símbolos" porque
#: são os dele.
_GLOBAIS = {
    "site/app/page.tsx", "site/app/layout.tsx", "site/app/not-found.tsx",
    "site/app/instalar/page.tsx",
    "site/components/instalar/Assistente.tsx",
    "site/app/docs/page.tsx", "site/app/docs/faq/page.tsx",
    "site/app/docs/biblioteca/page.tsx",
    "site/app/docs/contribuir/page.tsx",
    "site/app/docs/referencia/arquitetura/page.tsx",
    "site/app/docs/tecnicas/lsp/page.tsx",
    "site/app/docs/tecnicas/editor/page.tsx",
    "site/app/docs/editor/page.tsx",
    "site/app/docs/tecnicas/analise-estatica/page.tsx",
    "site/app/docs/instalacao/page.tsx",
    "site/app/docs/big-o/analisar/page.tsx",
    "README.md",
}

#: Números que são legitimamente locais mesmo nos arquivos acima.
_EXCECOES = {
    # '/docs' fala dos 26 módulos DE EXERCÍCIO, não dos da stdlib.
    ("site/app/docs/page.tsx", 26, "modulos"),
    ("site/app/instalar/page.tsx", 26, "modulos"),
    ("site/components/instalar/Assistente.tsx", 26, "modulos"),
    # O desenho do autocompletar mostra o que 'Arcane.Math' oferece.
    ("site/app/docs/tecnicas/lsp/page.tsx", 51, "simbolos"),
}


def test_nenhum_numero_global_da_documentacao_esta_defasado():
    """A home dizia "20 módulos e 190 exercícios". Eram 34 e 216.

    Números escritos à mão envelhecem em silêncio: nada quebra, a página
    abre, e só o conteúdo mente. Era o caso em quinze arquivos, incluindo
    a descrição que vai para o Open Graph — o texto que aparece quando
    alguém compartilha o link.

    O parâmetro de comparação é `site/lib/dados-gerados.json`, que é
    gerado do código. Se ele e a prosa discordarem, a prosa está errada.
    """
    import glob
    import json
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(raiz, "site", "lib", "dados-gerados.json"),
              encoding="utf-8") as f:
        dados = json.load(f)

    reais = {
        "exercicios": sum(len(v) for v in dados["exercicios"].values()),
        "modulos": len(dados["modulos"]),
        "simbolos": sum(len(m["funcoes"]) for m in dados["modulos"].values()),
        "palavras": len(dados["palavras"]),
        "exemplos": len(glob.glob(os.path.join(raiz, "examples", "*.df"))),
    }

    # A negativa antes do numero e necessaria: sem ela, o comando
    # 'python3 exercicios/run_all.py' vira "3 exercicios".
    def _p(sufixo):
        return re.compile(r"(?<![A-Za-z0-9])(\d+) " + sufixo)

    padroes = [
        (_p(r"m[oó]dulos"), "modulos"),
        (_p(r"exerc[ií]cios"), "exercicios"),
        (_p(r"exemplos"), "exemplos"),
        (_p(r"s[ií]mbolos"), "simbolos"),
        (_p(r"palavras reservadas"), "palavras"),
    ]

    ruins = []
    for relativo in sorted(_GLOBAIS):
        caminho = os.path.join(raiz, relativo)
        if not os.path.exists(caminho):
            ruins.append(f"{relativo}: nao existe mais — tire da lista")
            continue
        conteudo = open(caminho, encoding="utf-8").read()
        for padrao, chave in padroes:
            for achado in padrao.finditer(conteudo):
                n = int(achado.group(1))
                if n == reais[chave] or (relativo, n, chave) in _EXCECOES:
                    continue
                ruins.append(
                    f"{relativo}: diz '{n} {chave}', sao {reais[chave]}")

    assert not ruins, (
        "numero escrito a mao que envelheceu — confira contra "
        "'site/lib/dados-gerados.json':\n  " + "\n  ".join(ruins))


def test_pagina_gerada_avisa_que_e_gerada():
    """Editar um `.tsx` gerado funciona até alguém rodar o gerador.

    Sessenta e sete páginas de `/docs` vêm de `site/scripts/conteudo/`.
    Elas não diziam isso em lugar nenhum: uma correção feita no `.tsx`
    sobrevivia ao commit, ao build e à revisão, e sumia na próxima
    geração sem nada explicando. Aconteceu com a contagem de símbolos da
    página do LSP, corrigida à mão e revertida em seguida.

    O aviso vai na **primeira linha do arquivo**, e não num comentário
    no gerador: quem abre a página para editar precisa ver antes de
    começar.
    """
    import importlib

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts = os.path.join(raiz, "site", "scripts")

    # A lista de páginas vem da MESMA fonte que o gerador usa, e não da
    # saída de console dele: analisar texto impresso amarra o teste ao
    # formato da mensagem, que não é contrato de nada.
    sys.path.insert(0, scripts)
    try:
        nomes = importlib.import_module("gerar_conteudo").MODULOS
        geradas = []
        for nome in nomes:
            modulo = importlib.import_module(f"conteudo.{nome}")
            geradas += [p["href"] for p in modulo.PAGINAS]
    finally:
        if scripts in sys.path:
            sys.path.remove(scripts)

    assert len(geradas) > 50, f"so {len(geradas)} paginas geradas?"

    sem_aviso = []
    for href in geradas:
        caminho = os.path.join(raiz, "site", "app",
                               href.lstrip("/"), "page.tsx")
        if not os.path.exists(caminho):
            continue
        primeira = open(caminho, encoding="utf-8").readline()
        if "GERADO" not in primeira:
            sem_aviso.append(href)

    assert not sem_aviso, (
        "pagina gerada sem o aviso na primeira linha — alguem vai "
        f"edita-la a mao e perder o trabalho: {sem_aviso[:8]}")


def test_os_dois_geradores_do_indice_concordam():
    """Eles escreviam a MESMA linha, e cada um de um jeito.

    `gerar_conteudo.py` montava o índice só com os `h2`, e minusculava
    **depois** de remover o que não é `[a-z0-9]` — o que apagava cada
    letra maiúscula, e `HMAC` virava âncora vazia. `gerar_indices.py`
    fazia certo, com `h2` e `h3`. Rodar um depois do outro mudava o
    arquivo, e o estado final dependia da ordem.
    """
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts = os.path.join(raiz, "site", "scripts")

    conteudo = subprocess.run(
        [sys.executable, os.path.join(scripts, "gerar_conteudo.py")],
        capture_output=True, text=True, encoding="utf-8",
        cwd=scripts, timeout=120)
    assert conteudo.returncode == 0, (
        "o 'gerar_conteudo.py' nem rodou:\n"
        + (conteudo.stdout or "") + (conteudo.stderr or ""))

    r = subprocess.run(
        [sys.executable, os.path.join(scripts, "gerar_indices.py"), "--check"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz, timeout=120)
    assert r.returncode == 0, (
        "logo depois de 'gerar_conteudo.py', o 'gerar_indices.py' ainda "
        "quer mudar as paginas — os dois discordam:\n"
        + (r.stdout or "") + (r.stderr or ""))


# ── A página de download não pode prometer o que não existe ──

def test_a_pagina_de_download_so_oferece_o_que_o_release_produz():
    """Um botão "Baixar" que dá 404 é pior que a ausência do botão.

    A página lista os arquivos por nome. Os nomes têm de bater com o que
    `release.yml` de fato constrói e anexa — e é fácil os dois
    divergirem, porque estão em linguagens e pastas diferentes.

    Quando uma forma ainda não existe (o AUR, a imagem no Docker Hub),
    ela fica marcada `pronto: false` e **não** ganha botão. Dizer "na
    próxima versão" é honesto; oferecer um link quebrado não é.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pagina = os.path.join(raiz, "site", "app", "download", "page.tsx")
    assert os.path.exists(pagina), "a rota /download sumiu"

    fonte = open(pagina, encoding="utf-8").read()
    fluxo = open(os.path.join(raiz, ".github", "workflows", "release.yml"),
                 encoding="utf-8").read()

    # Os nomes de artefato que a página oferece do release.
    oferecidos = set(re.findall(r"\$\{RELEASES\}/([A-Za-z0-9_.${}-]+)", fonte))
    assert oferecidos, "a pagina nao oferece nenhum arquivo do release"

    # O que o fluxo constrói, pelos sufixos que ele anexa.
    for nome in oferecidos:
        alvo = nome.replace("${VERSAO}", "1.0.0")
        if alvo.endswith(".exe"):
            assert "dataforge.iss" in fluxo, \
                f"'{alvo}' e oferecido e o fluxo nao gera instalador"
        elif alvo.endswith(".deb"):
            assert "gerar_pacotes.py" in fluxo, \
                f"'{alvo}' e oferecido e o fluxo nao gera o .deb"
        elif alvo.endswith((".tar.gz", ".zip")):
            assert "gerar_binario.py" in fluxo, \
                f"'{alvo}' e oferecido e o fluxo nao gera binario"


def test_o_que_nao_esta_pronto_nao_ganha_botao():
    """`pronto: false` tem de significar alguma coisa no HTML."""
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonte = open(os.path.join(raiz, "site", "app", "download", "page.tsx"),
                 encoding="utf-8").read()

    assert "forma.arquivo && forma.pronto" in fonte, \
        "o botao Baixar precisa depender de 'pronto'"
    assert "na próxima versão" in fonte, \
        "o que nao esta pronto precisa dizer isso"


def test_o_instalador_do_windows_tem_o_icone_que_ele_pede():
    """O `.iss` aponta um `.ico`, e ele é **gerado**.

    Sem o arquivo, o `iscc` falha no meio do release — e o erro aparece
    numa máquina Windows que ninguém tem à mão para depurar.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    iss = os.path.join(raiz, "packaging", "windows", "dataforge.iss")
    assert os.path.exists(iss), "o script do instalador sumiu"

    fonte = open(iss, encoding="utf-8").read()
    assert "SetupIconFile" in fonte

    icone = os.path.join(raiz, "editor", "vscode", "icone.ico")
    assert os.path.exists(icone), \
        "o .ico do instalador nao existe — rode tools/vetorizar_logo.py"

    gerador = open(os.path.join(raiz, "tools", "vetorizar_logo.py"),
                   encoding="utf-8").read()
    assert "icone.ico" in gerador, \
        "o .ico precisa ser gerado, e nao um arquivo solto que envelhece"


def test_o_pkgbuild_do_arch_esta_na_versao_da_linguagem():
    import re

    from dataforge import __version__

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "packaging", "arch", "PKGBUILD")
    assert os.path.exists(caminho), "o PKGBUILD sumiu"

    achado = re.search(r"^pkgver=(.+)$", open(caminho, encoding="utf-8").read(),
                       re.M)
    assert achado, "o PKGBUILD nao declara pkgver"
    assert achado.group(1) == __version__, (
        f"o PKGBUILD esta em {achado.group(1)} e a linguagem em "
        f"{__version__} — rode packaging/gerar_pacotes.py")


def test_o_pacote_e_conferido_pelo_CONTEUDO_e_nao_por_bytes():
    """O piso de bytes confundia duas coisas muito diferentes.

    Com a extensão do VS Code compilada o `.deb` tem ~6,5 MB; **sem
    ela**, ~1,3 MB — e `editor/vscode/out/` é gitignored, porque é
    artefato de build. Numa máquina limpa (a CI) o pacote nasce
    legitimamente menor, e o piso de 2 MB o recusava: **três testes
    falhavam desde que o piso existe**, e a mensagem culpava o
    `pip install --target`, que estava certo.

    O que o piso queria pegar era o pacote VAZIO — a versão publicada na
    1.0.0 tinha 1.194 bytes. Isso continua pego. O resto virou uma
    pergunta sobre conteúdo: a linguagem está lá dentro?
    """
    import sys as _sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _sys.path.insert(0, os.path.join(raiz, "packaging"))
    import gerar_pacotes as g

    base = "./usr/lib/python3/dist-packages"

    def arvore(com_extensao):
        itens = [(f"{base}/{n}", b"x" * 100, 0o644) for n in g.ESSENCIAIS]
        itens += [(f"{base}/dataforge/stdlib/m{i}.py", b"x" * 100, 0o644)
                  for i in range(g.MINIMO_DE_MODULOS_NO_PACOTE + 5)]
        if com_extensao:
            itens += [(f"{base}/dataforge/editor/vscode/out/a{i}.js",
                       b"x" * 9000, 0o644) for i in range(37)]
        return itens

    # Passa nos dois ambientes: é o ponto.
    assert g._conferir_conteudo(arvore(True))
    assert g._conferir_conteudo(arvore(False))

    # E recusa o que importa recusar.
    with pytest.raises(SystemExit) as erro:
        g._conferir_conteudo([a for a in arvore(False)
                              if "interpreter.py" not in a[0]])
    assert "interpreter.py" in str(erro.value)

    with pytest.raises(SystemExit) as erro:
        g._conferir_conteudo([(f"{base}/{n}", b"x", 0o644)
                              for n in g.ESSENCIAIS])
    assert "pela metade" in str(erro.value)

    # O piso continua pegando o pacote de 1.194 bytes que foi publicado.
    assert g.TAMANHO_MINIMO_DO_DEB > 100 * 1024
    assert g.TAMANHO_MINIMO_DO_DEB < 1024 * 1024, (
        "o piso voltou a recusar um pacote sem a extensão compilada")


def test_o_deb_gerado_e_um_ar_valido(tmp_path):
    """Publicar um pacote quebrado é pior que não publicar."""
    import io as _io
    import subprocess
    import tarfile

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = subprocess.run(
        [sys.executable, os.path.join(raiz, "packaging", "gerar_pacotes.py")],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz, timeout=120,
        env={**os.environ, "DF_PACOTES_SAIDA": str(tmp_path)})
    assert r.returncode == 0, _uma_linha(r)

    import glob
    debs = glob.glob(os.path.join(str(tmp_path), "*.deb"))
    assert debs, "nenhum .deb foi gerado"

    dados = open(debs[0], "rb").read()
    assert dados[:8] == b"!<arch>\n", "nao e um arquivo 'ar'"

    # Os três membros, na ordem que o dpkg exige.
    nomes, i = [], 8
    while i < len(dados):
        cabecalho = dados[i:i + 60]
        if len(cabecalho) < 60:
            break
        nomes.append(cabecalho[:16].decode().strip())
        tamanho = int(cabecalho[48:58].decode().strip())
        i += 60 + tamanho + (tamanho % 2)
    assert nomes == ["debian-binary", "control.tar.gz", "data.tar.gz"], \
        f"membros fora de ordem: {nomes}"


# ═══════════════════════════════════════════════════════════
#  Nenhum link interno aponta para o vazio
#
#  Havia um verificador, e ele cobria **um** arquivo de
#  conteúdo (o da Vitrine) e **uma** forma de link (a do
#  Markdown). Por isso `/docs/devops` — que eu pus num card
#  da página de microserviços — ficou apontando para uma rota
#  que não existia, e nada avisou.
#
#  Um link quebrado na documentação é pior que uma página
#  ausente: ele promete que a resposta existe.
# ═══════════════════════════════════════════════════════════

def _links_de(texto):
    """As duas formas: `](/rota)` do Markdown e `"href": "/rota"`.

    O BLOCO DE CÓDIGO fica de fora. Uma página que ensina HTML mostra

        <a href="/produto/1">Ver</a>

    dentro de um exemplo, e `/produto/1` não é uma rota do site — é o
    assunto da aula. Contá-lo como link quebrado faria a trava acusar
    justamente a documentação que faz o seu trabalho.
    """
    import re

    texto = re.sub(r"code:\s*`(?:[^`\\]|\\.)*`", "", texto, flags=re.S)
    achados = set(re.findall(r"\]\((/[a-z0-9/_.-]+)\)", texto))
    achados |= set(re.findall(r'"href":\s*"(/[a-z0-9/_.-]+)"', texto))
    achados |= set(re.findall(r"href=\{?[\"'](/[a-z0-9/_.-]+)[\"']", texto))
    return achados


def _rota_existe(app, destino):
    limpo = destino.strip("/")
    if not limpo:
        return True          # a home
    for nome in ("page.tsx", "route.ts"):
        if os.path.isfile(os.path.join(app, limpo, nome)):
            return True
    # Uma rota dinâmica: /docs/x/[slug]
    pai = os.path.dirname(limpo)
    if pai and os.path.isdir(os.path.join(app, pai)):
        for entrada in os.listdir(os.path.join(app, pai)):
            if entrada.startswith("[") and os.path.isfile(
                    os.path.join(app, pai, entrada, "page.tsx")):
                return True
    return False


def test_todo_link_interno_do_conteudo_aponta_para_uma_rota_que_existe():
    """Os arquivos de `site/scripts/conteudo/` são a FONTE das 95
    páginas geradas — corrigir o `.tsx` não resolve, porque o gerador o
    reescreve."""
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = os.path.join(raiz, "site", "app")
    fontes = glob.glob(os.path.join(raiz, "site", "scripts", "conteudo",
                                    "*.py"))
    if not fontes or not os.path.isdir(app):
        pytest.skip("o site não está neste checkout")

    quebrados = []
    for caminho in sorted(fontes):
        texto = open(caminho, encoding="utf-8").read()
        for destino in sorted(_links_de(texto)):
            if not _rota_existe(app, destino):
                quebrados.append(
                    f"{os.path.basename(caminho)} → {destino}")

    assert not quebrados, (
        "link(es) para rota que não existe:\n  " + "\n  ".join(quebrados))


def test_todo_link_interno_das_paginas_escritas_a_mao_tambem():
    """As páginas manuais não passam por gerador nenhum, e por isso
    ninguém as reescreve — um link errado ali fica para sempre."""
    import glob

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = os.path.join(raiz, "site", "app")
    if not os.path.isdir(app):
        pytest.skip("o site não está neste checkout")

    quebrados = []
    for caminho in sorted(glob.glob(os.path.join(app, "**", "*.tsx"),
                                    recursive=True)):
        texto = open(caminho, encoding="utf-8").read()
        for destino in sorted(_links_de(texto)):
            if not _rota_existe(app, destino):
                quebrados.append(
                    f"{os.path.relpath(caminho, raiz)} → {destino}")

    assert not quebrados, (
        "link(es) para rota que não existe:\n  " + "\n  ".join(quebrados))


def test_toda_rota_da_navegacao_existe():
    """Um item de menu que dá 404 é o pior lugar para um link quebrado:
    ele aparece em **todas** as páginas."""
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = os.path.join(raiz, "site", "app")
    nav = os.path.join(raiz, "site", "lib", "nav.ts")
    if not os.path.isfile(nav):
        pytest.skip("o site não está neste checkout")

    texto = open(nav, encoding="utf-8").read()
    quebrados = [d for d in sorted(set(
        re.findall(r"href:\s*'(/[a-z0-9/_.-]+)'", texto)))
        if not _rota_existe(app, d)]
    assert not quebrados, f"na navegação, para o vazio: {quebrados}"


def test_toda_pagina_de_docs_esta_alcancavel_pela_navegacao():
    """Uma página que existe e não está no menu é trabalho que ninguém
    encontra — foi o que aconteceu com `/docs/devops`, que nem página
    tinha, e com a `/docs/editor`, cuja URL a extensão publicada já
    anunciava."""
    import glob
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = os.path.join(raiz, "site", "app")
    nav = os.path.join(raiz, "site", "lib", "nav.ts")
    if not os.path.isfile(nav):
        pytest.skip("o site não está neste checkout")

    no_menu = set(re.findall(r"href:\s*'(/[a-z0-9/_.-]+)'",
                             open(nav, encoding="utf-8").read()))

    #: A ÚNICA exceção, e ela é nomeada uma a uma.
    #:
    #: A primeira versão deste teste excluía prefixos inteiros
    #: (`/docs/exercicios/`, `/docs/tecnicas/`, …) supondo que o texto
    #: da seção os encadeava. A suposição escondia **dez páginas**: os
    #: módulos de exercício 27 a 32, e `/docs/tecnicas/api`,
    #: `/decimal`, `/ponte` e `/editor`.
    #:
    #: Excluir por prefixo é excluir o que ainda não existe. Uma lista
    #: de exceções nomeadas cresce quando alguém decide que cresça.
    fora = {
        # Serve a MESMA página de '/docs/editor', para não quebrar os
        # seis links internos que apontavam para a rota antiga. Duas
        # entradas de menu para uma página seriam pior.
        "/docs/tecnicas/editor",
    }

    orfas = []
    for caminho in glob.glob(os.path.join(app, "docs", "**", "page.tsx"),
                             recursive=True):
        rota = "/" + os.path.relpath(os.path.dirname(caminho),
                                     app).replace(os.sep, "/")
        if rota in no_menu or "[" in rota:
            continue
        if rota in fora:
            continue
        orfas.append(rota)

    assert not orfas, (
        "página(s) de doc fora da navegação — quem procura não acha:\n  "
        + "\n  ".join(sorted(orfas)))


def test_a_home_nao_pode_escrever_numero_a_mao():
    """Três vezes o mesmo defeito, e a terceira foi a que ensinou.

    O comentário acima de `fatos` dizia "os mesmos que a suíte
    verifica", e a suíte não verificava nenhum: os valores estavam em
    1246 testes e 216 exercícios quando eram 2304 e 230. Corrigidos à
    mão, voltaram a envelhecer — 2332 quando eram 2377. E em
    `Aprender.tsx` havia quatro números sob a legenda "conferidos na
    última execução da suíte", todos falsos.

    Comparar o número escrito com o real resolve uma vez e deixa o
    atrito para a próxima pessoa. O que resolve sempre é o número não
    poder ser escrito: hoje ele sai de `site/scripts/gerar_dados.py`,
    que conta o repositório.

    Este teste cobra as duas pontas — a home lê do gerador, e o
    gerador conta certo.
    """
    import glob
    import json
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    componentes = os.path.join(raiz, "site", "components", "landing")
    if not os.path.isdir(componentes):
        pytest.skip("o site não está neste checkout")

    # ── 1. os números do gerador batem com o disco ──
    with open(os.path.join(raiz, "site", "lib", "dados-gerados.json"),
              encoding="utf-8") as f:
        dados = json.load(f)

    exercicios_reais = len(glob.glob(
        os.path.join(raiz, "exercicios", "*", "[0-9]*.df")))
    exercicios_ditos = sum(len(v) for v in dados["exercicios"].values())
    assert exercicios_ditos == exercicios_reais, (
        f"o gerador diz {exercicios_ditos} exercicios, sao "
        f"{exercicios_reais} — rode site/scripts/gerar_dados.py")

    funcoes_reais = 0
    for raiz_dir, _, nomes in os.walk(os.path.join(raiz, "tests")):
        for nome in nomes:
            if nome.endswith(".py"):
                with open(os.path.join(raiz_dir, nome), encoding="utf-8") as f:
                    funcoes_reais += len(re.findall(r"^def test_", f.read(),
                                                    re.M))
    ditas = dados["contagem"]["testes"]
    # 2% de folga: o arquivo gerado e versionado, e escrever um teste
    # sem regerar nao pode reprovar a suite inteira — mas divergir
    # muito significa que ninguem regera ha tempo.
    assert abs(ditas - funcoes_reais) / max(funcoes_reais, 1) <= 0.02, (
        f"o gerador diz {ditas} funcoes de teste, sao {funcoes_reais}")

    # ── 2. a home LE do gerador, e não escreve ──
    for arquivo in ("Heroi.tsx", "Aprender.tsx"):
        fonte = open(os.path.join(componentes, arquivo),
                     encoding="utf-8").read()
        assert "dados-gerados.json" in fonte, (
            f"{arquivo} precisa ler os numeros do gerador")

        # Um literal de 3+ digitos num rotulo de numero e o defeito
        # voltando. Os que sobram sao medida de layout ('[10ch]',
        # 'text-[13px]'), que nao sao afirmacao sobre o repositorio.
        suspeitos = re.findall(r"valor:\s*'(\d{3,})'", fonte)
        assert not suspeitos, (
            f"{arquivo} voltou a escrever numero a mao: {suspeitos}")

    # ── 3. e o rótulo diz QUAL número é ──
    #
    # A home ja disse "Testes passando" mostrando a contagem de
    # FUNCOES. O pytest reporta ~2377 casos porque 'parametrize'
    # expande uma funcao em varios: os dois numeros sao verdadeiros e
    # diferentes, e o rotulo precisa dizer qual esta ali.
    heroi = open(os.path.join(componentes, "Heroi.tsx"),
                 encoding="utf-8").read()
    # Só o que a página MOSTRA — um comentário pode citar o rótulo
    # antigo para explicar por que ele saiu, e citar não é anunciar.
    visivel = " ".join(re.findall(r">([^<>{}]+)<", heroi))
    assert "Funções de teste" in visivel, (
        "o rotulo do hero precisa dizer 'Funções de teste': o numero "
        "mostrado conta 'def test_', e nao os casos do pytest")
    assert "Testes passando" not in visivel


def test_o_indice_lateral_da_home_dos_docs_cobre_os_h2():
    """`/docs/page.tsx` é escrita à mão, e o `gerar_indices.py` não a
    toca: um `<H2>` novo fica fora do índice lateral, e a seção existe
    na página e não no menu de dentro dela.

    Aconteceu agora: a seção "Levar ao ar" — a que responde onde está a
    documentação de DevOps — entrou sem índice.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "app", "docs", "page.tsx")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")

    texto = open(caminho, encoding="utf-8").read()
    titulos = re.findall(r"<H2>([^<]+)</H2>", texto)
    no_indice = set(re.findall(r"text: '([^']+)'", texto))
    faltando = [t for t in titulos if t.strip() not in no_indice]
    assert not faltando, (
        f"<H2> fora do índice lateral: {faltando}")


def test_o_download_sai_pelo_dominio_do_site():
    """Os sete links iam para `github.com/.../releases/latest/download`,
    e **não existia release nenhum**: cada um dava a página 404 do
    GitHub. O site anunciava arquivos que não estavam em lugar algum.

    O teste ao lado (`…so_oferece_o_que_o_release_produz`) conferia que
    os NOMES batiam com o workflow — a coerência interna — e passava,
    porque nada checava se o release existia. Uma trava que valida o
    mapa e não o território.

    Hoje o caminho é `/baixar/<arquivo>`, um **rewrite** no
    `vercel.json`: a edge busca o asset e o serve pelo domínio do site.
    Quem instala não sai da página, e um ambiente que bloqueia o GitHub
    não impede a instalação.
    """
    import json
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonte = open(os.path.join(raiz, "site", "app", "download", "page.tsx"),
                 encoding="utf-8").read()

    assert "const RELEASES = `/baixar`" in fonte, (
        "o download voltou a apontar para fora do site")
    assert "github.com/estevam5s/DataForge/releases/latest/download" \
        not in fonte, "sobrou um link direto para o release"

    # E o rewrite que faz isso funcionar tem de existir.
    config = os.path.join(raiz, "site", "vercel.json")
    with open(config, encoding="utf-8") as f:
        vercel = json.load(f)

    rewrites = vercel.get("rewrites") or []
    baixar = [r for r in rewrites if r.get("source", "").startswith("/baixar")]
    assert baixar, "sem o rewrite, '/baixar/x' e um 404 do proprio site"

    destino = baixar[0]["destination"]
    assert "releases/latest/download" in destino
    assert ":arquivo" in destino, (
        "o rewrite precisa repassar o nome do arquivo")

    # Um segmento só: '/baixar/a/b' não pode montar caminho para fora
    # do release.
    assert baixar[0]["source"] == "/baixar/:arquivo", (
        f"o padrao ficou largo demais: {baixar[0]['source']}")

    # E o cabeçalho que faz baixar em vez de exibir.
    cabecalhos = vercel.get("headers") or []
    de_baixar = [h for h in cabecalhos
                 if h.get("source", "").startswith("/baixar")]
    assert de_baixar, "sem Content-Disposition, um .zip pode abrir no navegador"
    chaves = {c["key"].lower() for c in de_baixar[0]["headers"]}
    assert "content-disposition" in chaves


def test_todo_arquivo_oferecido_no_download_e_construido_por_alguem():
    """A página não oferece o que nenhum job constrói, nem esconde o que
    algum job constrói.

    Duas versões deste teste já passaram sobre uma página errada:

    1. A primeira comparava a página com o `release.yml` e dizia que
       estava tudo bem enquanto **nenhum** dos sete arquivos existia:
       não havia release. A coerência entre dois arquivos do
       repositório não é evidência de nada lá fora — quem vai ao
       território é `scripts/verificar_downloads.py`.
    2. A segunda comparava a página com uma lista escrita **aqui**, e
       `dataforge-macos-x64.tar.gz` estava nela. O nome nunca foi
       produzido por job nenhum: o runner que o construiria é arm64. O
       teste guardava a lista contra a página, e as duas concordavam
       sobre um arquivo inexistente.

    Agora os nomes saem da **matriz do workflow**, que é quem decide o
    que é construído, e a conferência é nos dois sentidos.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonte = open(os.path.join(raiz, "site", "app", "download", "page.tsx"),
                 encoding="utf-8").read()
    fluxo = open(os.path.join(raiz, ".github", "workflows", "release.yml"),
                 encoding="utf-8").read()

    from dataforge import __version__

    oferecidos = {n.replace("${VERSAO}", __version__) for n in
                  re.findall(r"\$\{RELEASES\}/([A-Za-z0-9_.${}-]+)", fonte)}

    # A matriz do 'construir': uma plataforma por 'nome:'. Comentário
    # não conta — o macos-x64 removido está lá explicado, e um regex
    # ingênuo o traria de volta.
    sem_comentario = "\n".join(
        l for l in fluxo.splitlines() if not l.lstrip().startswith("#"))
    # os 'steps' DEPOIS da matriz: o job que confere a versao vem antes
    # do 'construir' e tem os seus proprios
    inicio = sem_comentario.index("      matrix:")
    matriz = sem_comentario[inicio:sem_comentario.index("    steps:", inicio)]
    alvos = re.findall(r"nome:\s*(\S+)", matriz)
    assert alvos, "a matriz do release.yml mudou de forma"

    construidos = set()
    for alvo in alvos:
        if alvo.startswith("windows"):
            construidos.add(f"dataforge-{alvo}.zip")
            # O instalador gráfico sai do mesmo job, pelo Inno Setup.
            construidos.add(f"DataForge-{__version__}-{alvo}-setup.exe")
        else:
            construidos.add(f"dataforge-{alvo}.tar.gz")
    # E o job 'distros', que não é da matriz.
    construidos.add(f"dataforge_{__version__}_all.deb")

    sobrando = oferecidos - construidos
    assert not sobrando, (
        f"a pagina oferece o que nenhum job constroi: {sorted(sobrando)} — "
        f"o botao existe e o arquivo nao")

    faltando = construidos - oferecidos
    assert not faltando, (
        f"algum job constroi e a pagina nao oferece: {sorted(faltando)} — "
        f"o release carrega um arquivo que ninguem encontra")


def test_o_deb_instala_a_linguagem_e_nao_um_pip_install(tmp_path):
    """O `.deb` publicado tinha **1.194 bytes**.

    O corpo dele era um `postinst` chamando
    `pip install dataforge-lang==1.0.0`, e na época `dataforge-lang`
    não estava no PyPI: o `postinst` saía com erro e o `dpkg` deixava o
    pacote meio configurado. O `data.tar.gz` tinha um arquivo — um
    README.

    Hoje o pacote **está** no PyPI, e o defeito continua o mesmo: um
    `.deb` cujo corpo é um download não instala em máquina sem rede, e
    não é reproduzível — a mesma versão do pacote instala coisas
    diferentes conforme o dia.

    O CI conferia com `dpkg-deb --info`, que passa em qualquer `ar` bem
    formado. Este teste olha o que o gerador coloca dentro.
    """
    import subprocess
    import sys as _sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gerador = open(os.path.join(raiz, "packaging", "gerar_pacotes.py"),
                   encoding="utf-8").read()

    # A frase aparece na docstring do gerador, que conta a historia: a
    # conferencia e no 'postinst' que ele PRODUZ, mais abaixo.
    assert "dist-packages" in gerador, (
        "o pacote precisa instalar a arvore em /usr/lib/python3/dist-packages")

    # '/usr/bin/df' seria o df do coreutils. O apelido existe no wheel,
    # onde mora numa venv; num pacote de sistema ele sombrearia o
    # comando que mostra espaco em disco.
    assert 'COMANDOS = ["dataforge"]' in gerador, (
        "o .deb nao pode instalar 'df' em /usr/bin: e o coreutils")

    # E o gerador produz um pacote com a linguagem dentro. Roda de
    # verdade, porque a lista de arquivos vem do 'pip install --target':
    # um teste sobre o texto do gerador nao veria um wheel vazio.
    r = subprocess.run([_sys.executable, "packaging/gerar_pacotes.py"],
                       cwd=raiz, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       env={**os.environ, "DF_PACOTES_SAIDA": str(tmp_path)})
    assert r.returncode == 0, _uma_linha(r)

    import glob
    import tarfile
    debs = glob.glob(os.path.join(str(tmp_path), "*.deb"))
    assert debs, "o gerador nao escreveu .deb nenhum"
    deb = max(debs, key=os.path.getmtime)

    # Um 'ar': tres membros, e o terceiro e o que instala.
    with open(deb, "rb") as f:
        bruto = f.read()
    assert bruto.startswith(b"!<arch>\n")
    inicio = bruto.index(b"data.tar.gz")
    # O cabecalho do membro tem 60 bytes a partir do nome.
    tamanho = int(bruto[inicio + 48:inicio + 58].decode().strip())
    dados = bruto[inicio + 60:inicio + 60 + tamanho]

    import io as _io
    with tarfile.open(fileobj=_io.BytesIO(dados)) as tar:
        nomes = tar.getnames()
    arquivos = [n for n in nomes if not n.endswith("/")]

    assert "./usr/bin/dataforge" in nomes, nomes[:10]
    assert "./usr/bin/df" not in nomes, (
        "o .deb instalaria 'df' por cima do coreutils")
    assert any(n.endswith("dist-packages/dataforge/interpreter.py")
               for n in nomes), "o interpretador nao esta no pacote"
    assert sum(1 for n in nomes if "/stdlib/" in n) >= 39, (
        "a stdlib nao chegou inteira")
    assert len(arquivos) >= 100, (
        f"so {len(arquivos)} arquivo(s) — a linguagem nao esta dentro")

    # 'GNU_FORMAT': o PAX do Python e recusado pelo dpkg com
    # "unsupported PAX tar header type 'x'", e isso aparece so na hora
    # de instalar.
    assert "GNU_FORMAT" in gerador, (
        "sem GNU_FORMAT o dpkg recusa o tar: os caminhos dentro de "
        "node_modules passam de 100 caracteres e o tarfile emite PAX")

    # ── E o 'postinst' nao baixa nada ──
    inicio_c = bruto.index(b"control.tar.gz")
    tam_c = int(bruto[inicio_c + 48:inicio_c + 58].decode().strip())
    controle = bruto[inicio_c + 60:inicio_c + 60 + tam_c]
    with tarfile.open(fileobj=_io.BytesIO(controle)) as tar:
        script = tar.extractfile("./postinst").read().decode()
        control = tar.extractfile("./control").read().decode()
    assert "pip" not in script, (
        f"o postinst voltou a baixar da rede:\n{script}")
    assert "python3-pip" not in control, (
        "'python3-pip' nao e mais dependencia: nada e baixado")
    assert "Installed-Size" in control, (
        "sem 'Installed-Size' o apt nao sabe dizer quanto o pacote ocupa")


# ═══════════════════════════════════════════════════════════
#  O sitemap, e o domínio que o site anuncia
# ═══════════════════════════════════════════════════════════

def test_o_metadatabase_e_o_dominio_onde_o_site_vive():
    """Era `dataforge-lang.dev`, que **não responde**.

    Todo canônico e todo Open Graph apontavam para um endereço
    inexistente: um link compartilhado não mostra prévia, e um buscador
    indexa o lugar errado. E era o único lugar do repositório que citava
    esse domínio — não havia nem a intenção de usá-lo.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "app", "layout.tsx")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")

    fonte = open(caminho, encoding="utf-8").read()
    assert "dataforge-lang.vercel.app" in fonte
    assert "dataforge-lang.dev" not in fonte, (
        "o metadataBase voltou para um domínio que não responde")


def test_existe_sitemap_e_ele_sai_da_navegacao():
    """Não havia sitemap — `/sitemap.xml` dava 404 — e o site tem 96
    páginas de documentação. As mais fundas levam três ou quatro saltos,
    e o rastreador desiste antes.

    A lista sai de `nav.ts`, a mesma fonte da barra lateral: uma segunda
    lista aqui divergiria, e um sitemap que aponta para página removida
    é pior que nenhum.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "app", "sitemap.ts")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")

    fonte = open(caminho, encoding="utf-8").read()
    assert "from '@/lib/nav'" in fonte, (
        "o sitemap tem de sair da navegação, e não de uma lista à parte")
    # Sem isto o `next build` com `output: 'export'` falha.
    assert "force-static" in fonte

    robots = os.path.join(raiz, "site", "app", "robots.ts")
    assert os.path.isfile(robots), "sem robots.txt, o sitemap não é anunciado"
    assert "sitemap" in open(robots, encoding="utf-8").read()


def test_o_sitemap_construido_nao_tem_url_repetida_nem_rota_morta():
    """Conferido no arquivo **construído**, que é o que o rastreador lê.

    `/api` está na navegação e na lista de rotas avulsas: sem o `Set`,
    ela apareceria duas vezes — ignorado por uns rastreadores e
    reclamado por outros.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    construido = os.path.join(raiz, "site", "out", "sitemap.xml")
    if not os.path.isfile(construido):
        pytest.skip("o site não foi construído neste checkout")

    urls = re.findall(r"<loc>([^<]+)</loc>",
                      open(construido, encoding="utf-8").read())
    assert len(urls) > 200, f"só {len(urls)} URLs — a nav não foi lida?"
    assert len(urls) == len(set(urls)), "URL repetida no sitemap"

    app = os.path.join(raiz, "site", "app")
    base = "https://dataforge-lang.vercel.app"
    mortas = []
    for url in urls:
        rota = url[len(base):] or "/"
        if not _rota_existe(app, rota):
            mortas.append(rota)
    assert not mortas, f"o sitemap aponta para rota inexistente: {mortas}"


def test_o_download_nao_chama_de_pendente_o_que_ja_esta_publicado():
    """O inverso do erro dos sete links quebrados, e o mesmo defeito.

    A imagem do Docker Hub foi publicada — com README e as tags `latest`
    e `1.0.0` — e a página continuava com `pronto: false`, anunciando
    como "na próxima versão" algo que já estava no ar.

    A página e a realidade em dois lugares: um dizia mais do que existe,
    o outro dizia menos.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonte = open(os.path.join(raiz, "site", "app", "download", "page.tsx"),
                 encoding="utf-8").read()

    # O bloco do Docker, do título ao 'pronto'.
    bloco = re.search(r"titulo: 'Docker',.*?pronto: (true|false)", fonte,
                      re.S)
    assert bloco, "o bloco do Docker mudou de forma"
    assert bloco.group(1) == "true", (
        "a imagem está publicada em hub.docker.com/r/estevan5s/dataforge "
        "— 'pronto: false' esconde um caminho que funciona")

    # E o único que continua pendente é o AUR, que depende de submissão
    # a um repositório de terceiro.
    pendentes = re.findall(r"titulo: '([^']+)',(?:(?!titulo:).)*?"
                           r"pronto: false", fonte, re.S)
    # 'Executável — Intel' entrou nesta lista e NAO vem numa proxima
    # versao: o GitHub retirou os runners Intel do plano gratuito, e um
    # binario so pode ser construido na arquitetura em que roda. A
    # etiqueta dele diz "não há", e nao "na próxima versão".
    assert "espera: 'não há'" in fonte, (
        "o Mac Intel precisa de etiqueta propria: 'na próxima versão' "
        "prometeria um binario que nao vem")
    # As tres primeiras dependem de aprovacao FORA deste repositorio: um
    # PR aceito no 'microsoft/winget-pkgs', moderacao no chocolatey.org e
    # entrada num bucket do Scoop. Os manifestos existem e sao gerados
    # ('packaging/windows/'), e por isso a pagina mostra o comando com a
    # espera dita — prometer 'winget install' antes do PR seria oferecer
    # um comando que responde "No package found".
    assert pendentes == ["winget", "Chocolatey", "Scoop",
                         "Executável — Intel", "Arch Linux e derivadas"], (
        f"o que está pendente mudou: {pendentes} — confira se ainda é "
        f"verdade antes de ajustar este teste")

def test_a_landing_nao_engole_nenhum_modulo_da_arcane():
    """A seção Arcane agrupa os módulos por uma lista escrita à mão.

    O agrupamento é julgamento — nenhum gerador adivinha que `Kiln` é
    framework e `Excel` é formato — mas o preço de uma lista à mão é
    envelhecer. Um módulo novo que ninguém acrescentasse ali **sumiria
    da página**, sem erro e sem aviso, e o total logo acima continuaria
    certo: a página diria "40 módulos" e mostraria 39.

    O componente joga o que sobra num grupo "Outros" para que nada
    desapareça, e este teste reprova enquanto houver sobra — aparecer
    no lugar errado é ruim, desaparecer é pior.
    """
    import json
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(raiz, "site", "lib", "dados-gerados.json"),
              encoding="utf-8") as f:
        catalogo = set(json.load(f)["modulos"])

    fonte = open(os.path.join(raiz, "site", "components", "landing",
                              "Arcane.tsx"), encoding="utf-8").read()
    bloco = fonte[fonte.index("const grupos"):fonte.index("/** O que nenhum")]
    # A subtracao era {"rotulo", "chaves"} — e "chaves" tambem e o nome
    # de um MODULO ('Arcane.Chaves'). Tirar a palavra fazia o modulo
    # sumir da conta e o teste acusar um agrupamento que existe. A
    # propriedade do componente passou a se chamar 'modulos', e aqui
    # sobra so o rotulo.
    citados = set(re.findall(r"'([a-z_]+)'", bloco)) - {"rotulo", "modulos"}

    fora = sorted(catalogo - citados)
    assert not fora, (
        f"{len(fora)} modulo(s) sem grupo na landing: {fora} — eles caem "
        f"em 'Outros', que existe para nao sumirem, mas o lugar deles e "
        f"num grupo de verdade em site/components/landing/Arcane.tsx")

    fantasmas = sorted(citados - catalogo)
    assert not fantasmas, (
        f"a landing agrupa modulo(s) que nao existem: {fantasmas}")



def test_a_pagina_de_exercicio_mostra_o_exercicio():
    """As 32 páginas de `/docs/exercicios` paravam na tabela.

    Título e enunciado, e nada do código. Quem chegava por busca via a
    PROMESSA de 234 exercícios e nenhum deles — para ler um, era
    preciso clonar o repositório. O código é a resposta e o teste ao
    mesmo tempo; escondê-lo esvazia a seção inteira.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(raiz, "site", "scripts"))
    import conteudo.exercicios as ex             # noqa: E402

    paginas = {p["href"]: p for p in ex.PAGINAS}
    assert len(paginas) == len(ex.MODULOS) + 1

    total_blocos_de_codigo = 0
    for nome, itens, caminhos in ex.MODULOS:
        pagina = paginas[f"/docs/exercicios/{nome}"]
        codigos = [b for b in pagina["blocos"] if "code" in b and b.get("lang") == "df"]
        titulos = [b["h2"] for b in pagina["blocos"] if "h2" in b]
        total_blocos_de_codigo += len(codigos)

        # Um h2 por exercicio, alem do 'Os exercicios'.
        numerados = [t for t in titulos if t[:3].isdigit()]
        assert len(numerados) == len([1 for n, _, _ in itens if n]), nome

        # E o codigo de cada um esta la, de verdade.
        for caminho in caminhos:
            corpo = ex._corpo(caminho)
            primeira = next((l for l in corpo.split("\n")
                             if l.strip() and not l.strip().startswith("//")), "")
            if primeira:
                assert any(primeira in b["code"] for b in codigos), (
                    f"{caminho}: a primeira linha de codigo nao aparece na pagina")

    assert total_blocos_de_codigo >= 231, total_blocos_de_codigo


def test_o_rotulo_do_exercicio_e_o_mesmo_na_barra_e_na_pagina():
    """Dois rótulos para a mesma página é o começo do desencontro.

    O nome vinha da PASTA (`resto.replace('-', ' ').capitalize()`), que
    não tem acento: a aba dizia "03 · Colecoes", "05 · Acoes",
    "10 · Avancado" e "22 · Web kiln" enquanto a barra lateral, escrita
    à mão, dizia o certo.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(raiz, "site", "scripts"))
    import conteudo.exercicios as ex             # noqa: E402

    nav = open(os.path.join(raiz, "site", "lib", "nav.ts"),
               encoding="utf-8").read()
    da_barra = {
        href: titulo
        for titulo, href in re.findall(
            r"title: '([^']+)', href: '/docs/exercicios/([^']+)'", nav)
    }
    assert da_barra, "nao achei os exercicios em nav.ts"

    # A BARRA não leva o número, e a página leva.
    #
    # São coisas diferentes de propósito: na página o número é a
    # identidade do módulo — "o exercício 157" é como se fala dele —, e
    # na barra ele é ruído repetido 34 vezes, empurrando o nome para a
    # direita em toda linha.
    #
    # O que não pode divergir é o NOME.
    for nome, _, _ in ex.MODULOS:
        if nome not in da_barra:
            continue
        da_pagina = ex._rotulo(nome).split("·", 1)[-1].strip()
        assert da_pagina == da_barra[nome].strip(), (
            f"{nome}: a pagina diz {da_pagina!r} e a barra "
            f"{da_barra[nome]!r}")
        assert "·" not in da_barra[nome], (
            f"{nome}: o numero voltou para a barra lateral")


def test_a_previa_compartilhada_e_uma_imagem_que_as_redes_aceitam():
    """O `og:image` era um **SVG**.

    Nenhuma rede que mostra prévia aceita SVG — nem Facebook, nem
    LinkedIn, nem WhatsApp, Discord ou Telegram. O link era
    compartilhado e aparecia sem imagem nenhuma, que é pior do que não
    ter metadado: o card fica cinza e vazio.

    Três números que as redes cobram:

        proporção   1.91:1     o banner é 2.98:1 e seria cortado
        tamanho     1200x630   o que Facebook e LinkedIn pedem
        peso        < 300 KB   acima disso o WhatsApp desiste da prévia
    """
    from PIL import Image

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    publico = os.path.join(raiz, "site", "public")

    for nome in ("og.png", "og-docs.png", "og-lavra.png"):
        caminho = os.path.join(publico, nome)
        assert os.path.isfile(caminho), (
            f"{nome} não existe — rode 'python3 tools/gerar_og.py'")
        im = Image.open(caminho)
        assert im.format == "PNG", f"{nome} é {im.format}; as redes pedem PNG"
        assert im.size == (1200, 630), (
            f"{nome} é {im.size[0]}x{im.size[1]}, e o card pede 1200x630 — "
            f"qualquer outra proporção é recortada")
        peso = os.path.getsize(caminho)
        assert peso < 300 * 1024, (
            f"{nome} tem {peso // 1024} KB; acima de 300 KB o WhatsApp "
            f"costuma desistir da prévia")

    # E o que o site DECLARA aponta para elas.
    layout = open(os.path.join(raiz, "site", "app", "layout.tsx"),
                  encoding="utf-8").read()
    assert "/og.png" in layout, "o layout não aponta mais para a prévia"
    assert ".svg'" not in layout.split("openGraph")[1].split("}")[0], (
        "voltou um SVG para o og:image — nenhuma rede o mostra")


def test_a_descricao_compartilhada_diz_para_que_a_linguagem_serve():
    """É ela que decide o clique no feed.

    "Tipos verificados, pattern matching estrutural e pipelines
    nativos" é uma lista de recursos para quem já conhece. Quem vê o
    card no LinkedIn não conhece.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    layout = open(os.path.join(raiz, "site", "app", "layout.tsx"),
                  encoding="utf-8").read()

    inicio = layout.index("const DESCRICAO_LONGA")
    longa = layout[inicio:layout.index(";", inicio)]

    # Tem de dizer o PROPÓSITO, e não só a lista de recursos.
    for palavra in ("criada para", "português"):
        assert palavra in longa, f"a descrição não diz '{palavra}'"
    # E citar o que sustenta a linguagem.
    for peca in ("Kiln", "Vitrine", "Lavra", "Crucible", "Arcane"):
        assert peca in longa, f"a descrição não cita {peca}"

    # O LinkedIn corta perto de 300 caracteres na prévia, mas guarda a
    # descrição inteira; o limite prático é o do Open Graph.
    texto = longa.replace("'", "").replace("+", "")
    assert 400 < len(texto) < 1400, (
        f"a descrição tem {len(texto)} caracteres — curta demais não diz "
        f"nada, longa demais é cortada em todo lugar")


def test_o_dado_estruturado_descreve_a_linguagem():
    """O Open Graph diz o que MOSTRAR; o JSON-LD diz o que a coisa É.

    O LinkedIn usa para completar o card quando quem publica não
    escreveu nada — que é o caso mais comum: alguém cola o link e
    aperta publicar.
    """
    import json
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    saida = os.path.join(raiz, "site", "out", "index.html")
    if not os.path.isfile(saida):
        pytest.skip("o site não foi construído neste checkout")

    html = open(saida, encoding="utf-8").read()
    achado = re.search(
        r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S)
    assert achado, "a página não traz dado estruturado"

    dado = json.loads(achado.group(1))
    tipos = {n["@type"] for n in dado["@graph"]}
    assert {"SoftwareApplication", "WebSite", "TechArticle"} <= tipos

    app = next(n for n in dado["@graph"]
               if n["@type"] == "SoftwareApplication")
    assert app["name"] == "DataForge"
    assert app["image"].endswith(".png"), "a imagem do JSON-LD também é PNG"
    assert len(app["featureList"]) >= 10


def test_o_llms_txt_esta_em_dia_e_o_exemplo_dele_roda():
    """O arquivo que um modelo lê antes de escrever DataForge.

    Quem escreve nesta linguagem hoje quase sempre tem um modelo ao
    lado. E um modelo que nunca a viu faz o que qualquer um faria:
    chuta a sintaxe de Python. O resultado é código que não compila, e
    a culpa parece da linguagem.

    Duas coisas o tornam confiável, e as duas são cobradas aqui:

    1. **Ele é gerado.** Um resumo escrito à mão envelhece na primeira
       palavra reservada nova — e um resumo errado é pior que nenhum,
       porque o modelo confia nele.

    2. **O exemplo dele RODA.** Um trecho que não compila no arquivo
       que existe para ensinar a compilar é o pior defeito possível.
    """
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    r = subprocess.run(
        [sys.executable, os.path.join(raiz, "scripts", "gerar_llms.py"),
         "--check"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz)
    assert r.returncode == 0, (
        "o llms.txt está desatualizado:\n" + (r.stdout or "") + (r.stderr or ""))

    for destino in ("llms.txt", os.path.join("site", "public", "llms.txt")):
        caminho = os.path.join(raiz, destino)
        assert os.path.isfile(caminho), f"{destino} não existe"

    texto = open(os.path.join(raiz, "llms.txt"), encoding="utf-8").read()

    # As armadilhas vêm ANTES da lista de símbolos: o que faz um modelo
    # errar não é não saber que existe 'Arcane.Excel'.
    assert texto.index("Armadilhas") < texto.index("palavras reservadas")
    assert "`//` e COMENTARIO" in texto
    assert "NAO e Python com outras palavras" in texto

    # O exemplo roda.
    sys.path.insert(0, os.path.join(raiz, "scripts"))
    import importlib
    gerar = importlib.import_module("gerar_llms")

    import contextlib
    import io as _io

    from dataforge.interpreter import Interpreter
    from dataforge.lexer import tokenize
    from dataforge.parser import parse

    with contextlib.redirect_stdout(_io.StringIO()):
        Interpreter().run(parse(tokenize(gerar.EXEMPLO, "llms"), "llms"))


def test_o_llms_txt_e_servido_pelo_site():
    """Um `llms.txt` que não responde na raiz do site não é um llms.txt.

    A convenção é o endereço: `/llms.txt`. Um arquivo só no repositório
    serve a quem já clonou — que é exatamente quem não precisa dele.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    publico = os.path.join(raiz, "site", "public", "llms.txt")
    assert os.path.isfile(publico), (
        "o llms.txt precisa estar em site/public/ para ser servido em "
        "/llms.txt")

    saida = os.path.join(raiz, "site", "out", "llms.txt")
    if os.path.isfile(saida):
        assert open(saida, encoding="utf-8").read() == \
            open(publico, encoding="utf-8").read()


def test_o_indice_lateral_gruda_ate_o_fim_da_pagina():
    """`position: sticky` só gruda enquanto está dentro do container dele.

    O "Nesta página" vive num `<aside>` que é irmão do `<article>`. Com
    o rodapé **fora** dessa linha, o container terminava onde o artigo
    terminava — e o índice desgrudava na última tela, que é justamente
    onde quem leu tudo ainda quer pular para outra seção.

    A barra ESQUERDA já tinha recebido essa correção (o comentário está
    em `app/docs/layout.tsx`); a da direita ficou de fora.

    O teste confere o HTML **exportado**, e não o JSX: é a estrutura que
    chega ao navegador que decide se o sticky gruda.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    saida = os.path.join(raiz, "site", "out")
    if not os.path.isdir(saida):
        pytest.skip("o site não foi exportado neste checkout")

    paginas = [
        os.path.join(saida, "docs", "index.html"),
        os.path.join(saida, "docs", "tecnicas", "concorrencia", "index.html"),
    ]
    conferidas = 0
    for caminho in paginas:
        if not os.path.isfile(caminho):
            continue
        html = open(caminho, encoding="utf-8").read()
        conferidas += 1

        assert html.count("<footer") == 1, (
            f"{os.path.relpath(caminho, raiz)}: {html.count('<footer')} "
            f"rodapés — ele foi movido para dentro de DocPage, e uma cópia "
            f"no layout faria os dois aparecerem")

        # A marca é o 'data-redimensionavel', e não mais a classe de
        # largura: desde que o índice virou redimensionável a largura
        # vai no `style`, e procurar 'w-[220px]' não acharia nada — o
        # `continue` abaixo esvaziaria a trava em silêncio, que é o
        # jeito mais rápido de uma trava virar decoração.
        i_aside = html.find('data-redimensionavel="docs-indice"')
        i_footer = html.find("<footer")
        if i_aside < 0:
            continue        # página sem índice lateral
        assert 0 < i_footer < i_aside, (
            f"{os.path.relpath(caminho, raiz)}: o rodapé está DEPOIS do "
            f"índice lateral, ou fora da linha dele — e aí o sticky "
            f"desgruda antes do fim da página")

    if conferidas == 0:
        pytest.skip("as páginas esperadas não estão no export")


# ═══════════════════════════════════════════════════════════
#  A largura das barras é de quem lê
# ═══════════════════════════════════════════════════════════

def _fonte_do_redimensionavel(com_comentarios=False):
    """O componente, por padrão SEM os comentários.

    A primeira versão destas travas acusou o próprio parágrafo que
    explica o defeito ("ler `localStorage` no render quebra a
    hidratação"). Uma trava que não distingue código de prosa cobra que
    ninguém escreva sobre o assunto — é a mesma lição que
    `test_nenhum_script_procura_um_programa_com_o_comando_which` já
    tinha aprendido, ali resolvida lendo a árvore.

    Aqui não há árvore de TypeScript à mão, então a limpeza é textual:
    bloco `/* … */` e linha `//`. Ela erraria num `//` dentro de string
    — e não há nenhuma neste arquivo, que é o que o teste abaixo cobra.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "components", "Redimensionavel.tsx")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")
    fonte = open(caminho, encoding="utf-8").read()
    if com_comentarios:
        return fonte

    assert "://" not in fonte, (
        "o arquivo ganhou uma URL, e a limpeza de comentários abaixo "
        "cortaria a linha dela — leia com um analisador de verdade")
    sem_bloco = re.sub(r"/\*.*?\*/", "", fonte, flags=re.S)
    return "\n".join(linha.split("//")[0] for linha in sem_bloco.splitlines())


def test_as_DUAS_barras_da_doc_sao_redimensionaveis():
    """Largura fixa é uma aposta sobre o conteúdo alheio.

    `Arcane.Arquivo_Seguro.abrir_zip_seguro` não cabe em 248 px e vira
    reticências; num monitor de 27" sobra tela dos dois lados. A barra
    de navegação e o índice "Nesta página" têm um puxador cada, em
    lados opostos — o da esquerda cresce para a direita, o da direita
    cresce para a esquerda.

    O teste olha o HTML **exportado**: é a estrutura que chega ao
    navegador que decide, e não o JSX.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pagina = os.path.join(raiz, "site", "out", "docs", "index.html")
    if not os.path.isfile(pagina):
        pytest.skip("o site não foi exportado neste checkout")

    html = open(pagina, encoding="utf-8").read()
    for marca in ('data-redimensionavel="docs-lateral"',
                  'data-redimensionavel="docs-indice"'):
        assert marca in html, f"{marca} sumiu do HTML exportado"

    assert html.count('role="separator"') >= 2, (
        "cada barra precisa do seu puxador")
    # A largura inicial vai no style: sem ela, a barra nasceria com a
    # largura do conteúdo antes de o JavaScript rodar.
    assert "width:248px" in html and "width:220px" in html, html[:0]


def test_o_puxador_funciona_pelo_TECLADO_e_se_anuncia():
    """Uma barra que só responde ao arrasto não existe para quem navega
    por teclado — e um `separator` sem régua ARIA é anunciado como
    "separador", sem dizer largura nenhuma.

    A acessibilidade aqui não é camada por cima: é o que o elemento é.
    """
    fonte = _fonte_do_redimensionavel()

    for exigido in ('role="separator"', 'aria-orientation="vertical"',
                    "aria-valuenow", "aria-valuemin", "aria-valuemax",
                    "aria-valuetext", "tabIndex={0}", "onKeyDown"):
        assert exigido in fonte, f"o puxador perdeu {exigido}"

    for tecla in ("ArrowRight", "ArrowLeft", "Home", "End"):
        assert tecla in fonte, f"o teclado perdeu {tecla}"

    assert "onDoubleClick" in fonte, (
        "sem o clique duplo, quem arrastou demais não tem como voltar "
        "ao padrão sem adivinhar o número")


def test_a_largura_guardada_e_lida_DEPOIS_da_hidratacao():
    """Ler `localStorage` no render quebra a hidratação.

    O servidor gera o HTML sem saber o que este navegador guardou; se o
    primeiro render do cliente usar outro valor, o React descarta a
    árvore inteira e re-renderiza — e no meio disso a página pisca.

    A leitura tem de estar dentro de um efeito, e toda leitura e
    escrita dentro de `try`: em janela privada, com dados do site
    bloqueados, o acessador **lança**, e uma barra lateral não pode
    derrubar a documentação por causa disso.
    """
    fonte = _fonte_do_redimensionavel()

    assert "useEffect" in fonte
    antes_do_efeito = fonte[: fonte.index("useEffect(")]
    assert "localStorage" not in antes_do_efeito, (
        "o armazenamento é lido antes do primeiro efeito — isso roda no "
        "render e quebra a hidratação")

    # Cada acesso ao armazenamento está protegido.
    assert fonte.count("try {") >= 2, (
        "leitura e escrita precisam cada uma do seu 'try': em janela "
        "privada o acessador lança")


def test_o_arrasto_nao_re_renderiza_a_arvore_a_cada_pixel():
    """Com 190 rotas e seções animadas, um `setState` por evento de
    ponteiro faz o arrasto engasgar.

    Durante o movimento o que muda é uma propriedade CSS escrita direto
    no elemento; o estado do React só é atualizado quando o dedo sai.
    """
    fonte = _fonte_do_redimensionavel()

    i_mover = fonte.index("const mover = ")
    corpo = fonte[i_mover: fonte.index("const soltar = ")]
    assert "style.width" in corpo, (
        "o arrasto deixou de escrever a largura direto no DOM")
    assert "setLargura" not in corpo, (
        "voltou a re-renderizar a cada pixel arrastado")


def test_cada_lado_cresce_para_FORA_da_pagina():
    """Um sinal trocado faz a barra encolher quando se puxa para fora.

    É o defeito mais fácil de cometer aqui e o mais difícil de ver numa
    revisão: as duas barras usam a mesma conta, com o sinal invertido,
    e ler `inicioX - e.clientX` não diz para que lado a barra cresce.

    Não há navegador nesta suíte, então o que se prova é a **conta** —
    lida do componente, e não copiada, senão as duas poderiam divergir
    e o teste continuaria verde.
    """
    fonte = _fonte_do_redimensionavel()

    linhas = [l.strip() for l in fonte.splitlines() if "const delta" in l]
    assert len(linhas) == 1, f"a conta do arrasto mudou de forma: {linhas}"
    expressao = linhas[0]

    # A leitura é literal: se a expressão mudar, o teste para de saber o
    # que está exercitando e diz isso em vez de aprovar.
    assert "lado === 'esquerda' ? e.clientX - inicioX : inicioX - e.clientX" \
        in expressao, expressao

    def delta(lado, inicio_x, client_x):
        return client_x - inicio_x if lado == "esquerda" else inicio_x - client_x

    # Puxar para FORA da página (a direita, na barra esquerda; a
    # esquerda, no índice da direita) aumenta a largura.
    assert delta("esquerda", 300, 360) > 0, "a barra esquerda encolheu ao ser puxada para a direita"
    assert delta("esquerda", 300, 240) < 0
    assert delta("direita", 1200, 1140) > 0, "o índice encolheu ao ser puxado para a esquerda"
    assert delta("direita", 1200, 1260) < 0

    # E os limites existem nos dois sentidos.
    assert "Math.min(maximo, Math.max(minimo" in fonte, (
        "a largura deixou de ser limitada — arrastar até o fim comeria "
        "a coluna de texto")


# ═══════════════════════════════════════════════════════════
#  Turnstile: a proteção anti-robô da entrada do painel
# ═══════════════════════════════════════════════════════════

#: A chave de SITE é pública por desenho — ela vai no HTML de toda
#: página que mostra o widget. A SECRETA não pode estar em lugar
#: nenhum daqui, e o teste abaixo não a nomeia (nomeá-la seria
#: commitá-la): ele recusa qualquer chave com a forma de uma chave do
#: Turnstile que não seja a de site declarada.
CHAVE_DE_SITE_PUBLICA = "0x4AAAAAAE90dNHbqVbe4OI8"


def test_a_chave_SECRETA_do_turnstile_nao_esta_no_repositorio():
    """A secreta mora no painel do Supabase, e em nenhum outro lugar.

    Quem valida o desafio é o servidor que recebe a senha — o do
    Supabase. A chave secreta é o que autoriza aquela chamada ao
    `/siteverify` da Cloudflare: com ela, qualquer um resolve desafios
    em nome deste projeto.

    O teste não escreve a chave secreta (isso a commitaria). Ele
    procura pela **forma** de uma chave do Turnstile e aceita só a de
    site, que é pública.
    """
    import glob
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    padrao = re.compile(r"0x4AAAAAA[A-Za-z0-9]{10,}")

    alvos = []
    for pasta in ("site/app", "site/components", "site/lib", "site/scripts",
                  "dataforge", "scripts", "tools", "doc", "tests"):
        alvos += glob.glob(os.path.join(raiz, pasta, "**", "*.*"), recursive=True)
    alvos += [os.path.join(raiz, "site", "README.md"),
              os.path.join(raiz, "site", "vercel.json"),
              os.path.join(raiz, "CLAUDE.md")]

    # '__pycache__' fica de fora: o .pyc guarda as constantes deste
    # próprio arquivo, e a primeira versão da trava acusou a si mesma.
    intrusas = {}
    for caminho in alvos:
        if not os.path.isfile(caminho) or "/node_modules/" in caminho:
            continue
        if "__pycache__" in caminho or caminho.endswith((".pyc", ".png",
                                                         ".ico", ".gz",
                                                         ".woff", ".woff2")):
            continue
        try:
            texto = open(caminho, encoding="utf-8", errors="ignore").read()
        except OSError:                                    # pragma: no cover
            continue
        for achada in padrao.findall(texto):
            if achada != CHAVE_DE_SITE_PUBLICA:
                intrusas.setdefault(achada[:14] + "…", set()).add(
                    os.path.relpath(caminho, raiz))

    assert not intrusas, (
        "chave do Turnstile que NÃO é a de site (pública) no "
        f"repositório — se for a secreta, rotacione-a agora: {intrusas}")


def test_o_token_do_captcha_chega_as_TRES_rotas_de_autenticacao():
    """Entrar não é a única porta.

    Criar conta e recuperar senha **mandam e-mail**: um robô com uma
    lista de endereços transforma o projeto em remetente de spam sem
    precisar acertar senha nenhuma. As três passam o token.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "lib", "supabase", "auth.tsx")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")
    fonte = open(caminho, encoding="utf-8").read()

    assert fonte.count("captchaToken") >= 3, (
        "alguma das três rotas (entrar, registrar, recuperar) deixou de "
        "mandar o token")
    for chamada in ("signInWithPassword", "signUp", "resetPasswordForEmail"):
        i = fonte.index(chamada)
        trecho = fonte[i: i + 500]
        assert "captchaToken" in trecho, (
            f"'{chamada}' não manda o token do captcha")


def test_o_token_e_REINICIADO_depois_de_cada_tentativa():
    """O token é de uso único, e o defeito que isso causa é cruel.

    A pessoa erra a senha, corrige, envia de novo — e recebe um erro
    sobre captcha, que não tem nada a ver com o que ela acabou de
    fazer. O widget precisa ser reiniciado depois de **toda**
    tentativa, tenha ela dado certo ou não.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "components", "painel", "Entrar.tsx")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")
    fonte = open(caminho, encoding="utf-8").read()

    assert "reiniciar()" in fonte, "o widget não é reiniciado"

    # E o reinício vem ANTES do 'return' do caminho de erro: depois
    # dele, uma tentativa que falha deixaria o token queimado.
    i_reinicio = fonte.index("reiniciar()")
    i_erro = fonte.index("setErro(resultado)")
    assert i_reinicio < i_erro, (
        "o token só é reiniciado no caminho de sucesso — quem errou a "
        "senha ficaria com um token queimado na segunda tentativa")


def test_a_falha_do_captcha_e_dita_em_portugues():
    """O Supabase devolve o recado da Cloudflare quase cru.

    "captcha protection: request disallowed (timeout-or-duplicate)"
    fala de um serviço que quem está entrando não sabe que existe, num
    idioma que pode não ser o dele, e não diz o que fazer.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "lib", "turnstile.ts")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")
    fonte = open(caminho, encoding="utf-8").read()

    for causa in ("timeout-or-duplicate", "missing-input-response",
                  "invalid-input-response"):
        assert causa in fonte, f"a falha '{causa}' não tem tradução"

    cliente = open(os.path.join(raiz, "site", "lib", "supabase", "cliente.ts"),
                   encoding="utf-8").read()
    assert "traduzirFalhaDeCaptcha" in cliente, (
        "a tradução existe e ninguém a chama — o recado cru continua "
        "chegando a quem entra")


def test_o_captcha_falha_ABERTO_no_cliente():
    """Se o widget não carrega, o botão não pode morrer.

    Rede corporativa que bloqueia a Cloudflare, domínio ainda não
    liberado na chave, extensão de navegador que corta scripts de
    terceiro: em qualquer um desses o widget não aparece, e um botão
    que depende dele deixa a porta trancada **sem ninguém do outro
    lado para explicar**.

    Quem recusa de verdade é o servidor do Supabase, que vai responder
    com uma mensagem clara. O cliente falha aberto; o servidor falha
    fechado — e essa é a ordem certa, porque só um dos dois é
    confiável.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(raiz, "site", "components", "painel", "Entrar.tsx")
    if not os.path.isfile(caminho):
        pytest.skip("o site não está neste checkout")
    fonte = open(caminho, encoding="utf-8").read()

    assert "captchaFalhou" in fonte, (
        "não há como o formulário saber que o widget falhou")

    # A versão anterior deste teste exigia `!captchaFalhou` dentro do
    # `disabled`: o botão habilitava QUANDO O WIDGET AVISAVA que
    # falhou. Isso cobre menos do que parece — o `error-callback` não
    # dispara quando o widget renderiza e simplesmente **não
    # termina** (domínio não liberado, desafio que não resolve), e
    # nesse caso o botão ficava morto para sempre.
    #
    # Hoje a garantia é mais forte e mais simples de verificar: o
    # `disabled` **não menciona o captcha**. Quem recusa é o servidor.
    i = fonte.index("disabled={enviando")
    condicao = fonte[i: i + 120]
    assert "captcha" not in condicao.lower(), (
        f"o botão voltou a depender do captcha: {condicao}\n"
        "Falhar aberto aqui não enfraquece nada — sem token o Supabase "
        "recusa, e a mensagem dele já é traduzida.")

    # E há um prazo que desiste da espera, para o rótulo não ficar em
    # "verificando…" indefinidamente.
    assert "setTimeout" in fonte, (
        "sem prazo, uma verificação que não termina deixa o rótulo "
        "preso para sempre")


def test_as_paginas_da_biblioteca_saem_dos_MODULOS():
    """Elas traziam a lista de símbolos copiada à mão, e envelheceram.

    A de `Arcane.Regex` anunciava *"Funções (28)"* onde havia 44, e a
    contagem estava no **título** da seção — quem abre a página lê o
    número antes de ler a lista. E havia o outro lado: 32 dos 75
    módulos não tinham página nenhuma, e a única forma de ver a
    assinatura de um deles era abrir o código.
    """
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gerador = os.path.join(raiz, "tools", "gerar_paginas_biblioteca.py")
    if not os.path.isfile(gerador):
        pytest.skip("o gerador não está neste checkout")

    saida = subprocess.run([sys.executable, gerador, "--check"],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=raiz)
    assert saida.returncode == 0, saida.stdout + saida.stderr


def test_todo_modulo_da_arcane_tem_pagina_e_ela_esta_no_menu():
    """Uma página que o menu não cita é uma página que ninguém encontra.

    Era o estado de 32 módulos: a página não existia, e o item do menu
    também não. As duas listas eram escritas à mão, e a segunda é a
    que decide se alguém chega lá.
    """
    import re as _re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(raiz, "tools"))
    from gerar_paginas_biblioteca import modulos, SEM_PAGINA

    nav = open(os.path.join(raiz, "site", "lib", "nav.ts"),
               encoding="utf-8").read()
    no_menu = set(_re.findall(r"'(/docs/biblioteca/[^']+)'", nav))

    sem_pagina, sem_menu = [], []
    for curto, oficial, _desc, _mod in modulos():
        caminho = os.path.join(raiz, "site", "app", "docs", "biblioteca",
                               curto, "page.tsx")
        if not os.path.isfile(caminho):
            sem_pagina.append(oficial)
        if f"/docs/biblioteca/{curto}" not in no_menu:
            sem_menu.append(oficial)

    assert not sem_pagina, f"módulo sem página: {sem_pagina}"
    assert not sem_menu, f"página fora do menu: {sem_menu}"
    # E o contrário: o menu não pode citar um módulo que não existe.
    curtos = {c for c, _o, _d, _m in modulos()}
    inventados = sorted(
        h for h in no_menu
        if h != "/docs/biblioteca" and h.rsplit("/", 1)[-1] not in curtos)
    assert not inventados, f"o menu cita o que não existe: {inventados}"


def test_o_prologo_escrito_a_mao_nao_mora_no_arquivo_gerado():
    """Deixá-lo dentro de um `.tsx` marcado GERADO é o convite para
    editá-lo ali — e a correção some na próxima geração, sem nada
    explicando. Já foi assim que uma contagem voltou a ficar errada
    depois de corrigida."""
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta = os.path.join(raiz, "site", "scripts", "conteudo_biblioteca")
    assert os.path.isdir(pasta), "os prólogos precisam morar fora do .tsx"

    sys.path.insert(0, os.path.join(raiz, "tools"))
    from gerar_paginas_biblioteca import _prologo

    # Ao menos os que já existiam continuam lá: um prólogo perdido é
    # um exemplo que sumiu da doc sem ninguém notar.
    for curto in ("regex", "math", "crypto", "io"):
        assert _prologo(curto), f"o prólogo de {curto} sumiu"


def test_a_imagem_de_previa_nao_escreve_numero_a_mao():
    """Ela dizia "40 módulos" quando já eram 75, e "234 exercícios"
    quando já eram 387.

    Uma imagem de prévia é o cartão que aparece quando alguém
    compartilha o link, e um cartão que contradiz a página que ele
    anuncia é pior que nenhum. E ela **não aparece em revisão**:
    ninguém abre um PNG para conferir um número.
    """
    import re

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fonte = open(os.path.join(raiz, "tools", "gerar_og.py"),
                 encoding="utf-8").read()

    # As descrições ficam num bloco só; o que se proíbe ali é um número
    # solto ao lado de "módulos", "exercícios" ou "páginas".
    inicio = fonte.index("IMAGENS = [") if "IMAGENS = [" in fonte else 0
    bloco = fonte[inicio:]
    escritos = re.findall(
        r'"[^"]*?\b(\d+)\s+(módulos|exercícios|páginas)', bloco)
    assert not escritos, (
        f"número escrito à mão na imagem de prévia: {escritos} — "
        f"ele sai de '_contar()'")


def test_a_imagem_de_previa_e_deterministica():
    """Senão todo `--check` acusaria desatualização por ruído."""
    import hashlib
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alvo = os.path.join(raiz, "site", "public", "og.png")
    if not os.path.isfile(alvo):
        pytest.skip("a imagem não está neste checkout")

    def resumo():
        return hashlib.sha256(open(alvo, "rb").read()).hexdigest()

    antes = resumo()
    subprocess.run([sys.executable, os.path.join(raiz, "tools", "gerar_og.py")],
                   capture_output=True, text=True, encoding="utf-8", cwd=raiz)
    assert resumo() == antes, "gerar_og.py não é determinístico"
