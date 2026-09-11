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
    import glob
    import subprocess

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conteudo = os.path.join(raiz, "site", "scripts", "conteudo")
    modulos = [c for c in glob.glob(os.path.join(conteudo, "*.py"))
               if not os.path.basename(c).startswith("__")]
    assert modulos, "nenhum modulo de conteudo — o gerador mudou de lugar?"

    r = subprocess.run(
        [sys.executable, os.path.join(raiz, "site", "scripts",
                                      "gerar_conteudo.py")],
        capture_output=True, text=True, encoding="utf-8",
        cwd=os.path.join(raiz, "site", "scripts"), timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr

    geradas = [l.strip() for l in r.stdout.split("\n")
               if l.strip().startswith("/")]
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

    subprocess.run([sys.executable, os.path.join(scripts, "gerar_conteudo.py")],
                   capture_output=True, cwd=scripts, timeout=120, check=True)
    r = subprocess.run(
        [sys.executable, os.path.join(scripts, "gerar_indices.py"), "--check"],
        capture_output=True, text=True, encoding="utf-8", cwd=raiz, timeout=120)
    assert r.returncode == 0, (
        "logo depois de 'gerar_conteudo.py', o 'gerar_indices.py' ainda "
        "quer mudar as paginas — os dois discordam:\n" + r.stdout)
