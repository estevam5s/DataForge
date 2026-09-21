# -*- coding: utf-8 -*-
"""A pagina /roadmap — e as tres formas de ela envelhecer calada.

Uma pagina de roadmap e o tipo de conteudo que mais rapido vira
mentira: ela fala do estado do projeto, e o estado do projeto muda
todo dia. Tres travas, uma por forma:

1. **O dado e gerado.** `site/lib/roadmap-gerado.json` sai de
   `Arcane.Percurso` e `Arcane.Ecossistema`, e este arquivo roda o
   gerador e compara. E a mesma trava das outras onze geracoes do
   repositorio.

2. **Toda rota citada existe.** As trilhas sao escritas a mao — a
   ordem em que vale a pena aprender e julgamento, nao dado. Mas o
   DESTINO de cada passo e conferido contra o disco: uma trilha que
   promete um caminho e entrega um 404 no meio e pior que nenhuma
   trilha.

3. **A rota esta no topo, e NAO na barra lateral.** Foi o pedido, e e
   uma decisao que se desfaz sozinha: quem acrescentar a pagina ao
   `nav.ts` "para facilitar" nao vai lembrar que ela foi tirada de la
   de proposito.
"""

import io
import json
import os
import re
import subprocess
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

GERADOR = os.path.join(RAIZ, "site", "scripts", "gerar_roadmap.py")
GERADO = os.path.join(RAIZ, "site", "lib", "roadmap-gerado.json")
TRILHAS = os.path.join(RAIZ, "site", "lib", "trilhas.ts")
NAV = os.path.join(RAIZ, "site", "lib", "nav.ts")
HEADER = os.path.join(RAIZ, "site", "components", "Header.tsx")
PAGINA = os.path.join(RAIZ, "site", "app", "roadmap", "page.tsx")


def _ler(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def dados():
    return json.loads(_ler(GERADO))


# ═══════════════════════════════════════════════════════════
#  1. O dado e gerado
# ═══════════════════════════════════════════════════════════

def test_o_json_do_roadmap_esta_em_dia():
    """A mesma trava das outras onze geracoes do repositorio."""
    saida = subprocess.run(
        [sys.executable, GERADOR, "--check"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", timeout=180)
    assert saida.returncode == 0, (
        "roadmap-gerado.json esta defasado. Rode:\n"
        "    python3 site/scripts/gerar_roadmap.py\n"
        + saida.stdout + saida.stderr)


def test_os_numeros_do_roadmap_vem_do_codigo(dados):
    """Se o JSON discordar do modulo, a pagina esta mostrando o passado."""
    from dataforge.stdlib import get_module

    eco = get_module("Arcane.Ecossistema")
    assert dados["numeros"] == dict(eco["numeros"]())
    assert len(dados["componentes"]) == dados["numeros"]["componentes"]
    assert len(dados["fases"]) == len(get_module("Arcane.Percurso")["fases"]())


def test_todo_modulo_da_biblioteca_aparece_em_algum_grupo(dados):
    """'Outros' existe para nada sumir, e ficar vazio e o estado certo.

    Um modulo que cai em 'Outros' e um modulo que ninguem colocou em
    lugar nenhum — aqui e na landing, que usa a mesma divisao.
    """
    assert dados["semGrupo"] == [], (
        f"modulo(s) sem grupo no roadmap: {dados['semGrupo']} — "
        "acrescente em GRUPOS_DE_MODULO de site/scripts/gerar_roadmap.py")

    from dataforge.stdlib import get_module, list_modules
    oficiais = {get_module(m)["__name__"] for m in list_modules()}
    no_mapa = {m["nome"] for g in dados["modulos"] for m in g["modulos"]}
    assert no_mapa == oficiais, (
        f"faltam no mapa: {sorted(oficiais - no_mapa)}\n"
        f"sobram no mapa: {sorted(no_mapa - oficiais)}")


def test_a_lista_do_que_nao_existe_nao_esta_vazia(dados):
    """Um roadmap que so lista conquistas e propaganda.

    Se um dia ela esvaziar de verdade, este teste reprova e alguem
    precisa decidir o que a pagina passa a dizer — que e melhor do que
    a secao sumir sem ninguem notar.
    """
    assert dados["naoExiste"], (
        "'o_que_nao_existe()' voltou vazia — confira se ela ainda e lida")
    for item in dados["naoExiste"]:
        assert item["estado"] == "nao-existe"
        assert item["o_que_e"], f"{item['no']} sem 'o_que_e'"


# ═══════════════════════════════════════════════════════════
#  2. Toda rota citada existe
# ═══════════════════════════════════════════════════════════

def _rotas_das_trilhas():
    texto = _ler(TRILHAS)
    # Pega 'href:' e 'exercicios:' — os dois sao rotas, e um exercicio
    # que aponta para uma pagina removida quebra igual.
    return sorted(set(re.findall(r"(?:href|exercicios):\s*'([^']+)'", texto)))


def test_toda_rota_das_trilhas_tem_pagina_no_disco():
    """Escrevendo estas trilhas, 8 de 36 rotas que eu 'sabia' nao existiam.

    `/docs/controle` e `/docs/pipeline` soam certas e as paginas se
    chamam `/docs/condicionais` e `/docs/pipelines`. Sem esta trava,
    oito passos de sete trilhas levariam a 404.
    """
    faltam = []
    for rota in _rotas_das_trilhas():
        pagina = os.path.join(RAIZ, "site", "app", rota.strip("/"), "page.tsx")
        if not os.path.isfile(pagina):
            faltam.append(rota)
    assert not faltam, f"rota(s) sem pagina: {faltam}"


def test_as_trilhas_citam_rotas_que_a_navegacao_conhece():
    """Uma rota fora do `nav.ts` existe e ninguem a encontra pelo menu.

    Nao e erro — `/roadmap` e justamente uma dessas —, mas um PASSO de
    trilha que so e alcancavel pela trilha isola o assunto do resto da
    documentacao.
    """
    nav = set(re.findall(r"href:\s*'([^']+)'", _ler(NAV)))
    fora = [r for r in _rotas_das_trilhas() if r not in nav]
    assert not fora, (
        f"passo(s) de trilha fora da navegacao: {fora} — "
        "eles existem, mas o menu nao os alcanca")


def test_nenhuma_trilha_aponta_para_si_mesma_como_pre_requisito():
    texto = _ler(TRILHAS)
    ids = re.findall(r"id:\s*'([\w-]+)',\s*\n\s*titulo:", texto)
    assert len(ids) >= 5, f"poucas trilhas encontradas: {ids}"
    assert len(set(ids)) == len(ids), f"id repetido: {ids}"

    for bloco in re.split(r"\n  \{\n", texto)[1:]:
        meu = re.search(r"id:\s*'([\w-]+)'", bloco)
        antes = re.search(r"antes:\s*\[([^\]]*)\]", bloco)
        if not meu or not antes:
            continue
        citados = re.findall(r"'([\w-]+)'", antes.group(1))
        assert meu.group(1) not in citados, f"'{meu.group(1)}' exige a si mesma"
        for c in citados:
            assert c in ids, f"'{meu.group(1)}' exige '{c}', que nao existe"


# ═══════════════════════════════════════════════════════════
#  3. A rota esta no topo, e NAO na barra lateral
# ═══════════════════════════════════════════════════════════

def test_a_pagina_do_roadmap_existe():
    assert os.path.isfile(PAGINA)
    assert "force-static" in _ler(PAGINA), (
        "sem 'force-static' o 'next build' com output:'export' falha")


def test_o_roadmap_esta_no_topo_e_nao_na_barra_lateral():
    """A decisao do pedido, registrada.

    Ela se desfaz sozinha: quem acrescentar a pagina ao `nav.ts` para
    'facilitar' nao vai lembrar que ela foi deixada de fora de
    proposito — a barra lateral e o indice da DOCUMENTACAO, e o
    roadmap fala do projeto.
    """
    header = _ler(HEADER)
    assert "/roadmap" in header, "o link nao esta no cabecalho"
    assert "link-topo" in header

    nav = _ler(NAV)
    assert "'/roadmap'" not in nav, (
        "o roadmap voltou para a barra lateral; o lugar dele e o topo")


def test_o_roadmap_e_alcancavel_no_celular():
    """No telefone o topo fica escondido (`hidden lg:block`).

    Sem a fila de rotas de topo no menu do celular, `/roadmap` e
    `/download` nao teriam como ser abertos num telefone: o menu mostra
    a barra lateral, e nenhuma das duas esta nela.
    """
    header = _ler(HEADER)
    menu = header[header.index("Navegação do celular"):]
    assert "/roadmap" in menu, (
        "o roadmap nao aparece no menu do celular, onde o topo esta escondido")


def test_o_roadmap_esta_no_sitemap():
    """Uma pagina fora do `nav.ts` nao entra no sitemap sozinha."""
    sitemap = _ler(os.path.join(RAIZ, "site", "app", "sitemap.ts"))
    avulsas = re.search(r"const AVULSAS = \[([^\]]*)\]", sitemap)
    assert avulsas and "/roadmap" in avulsas.group(1), (
        "o sitemap sai do nav.ts, e o roadmap nao esta nele: "
        "ele precisa entrar em AVULSAS")


# ═══════════════════════════════════════════════════════════
#  O mapa 3D
# ═══════════════════════════════════════════════════════════

def _sem_comentario(fonte):
    """O codigo, sem os comentarios.

    Uma trava que le o arquivo inteiro acusa a propria explicacao dela:
    a primeira versao de `test_a_posicao_dos_nos_e_deterministica`
    reprovou por causa da linha 'Nada de `Math.random`' no cabecalho do
    componente. E o mesmo defeito que o `lint` ja teve com o marcador
    'TODO', e a correcao e a mesma — olhar so o codigo.
    """
    sem_bloco = re.sub(r"/\*.*?\*/", "", fonte, flags=re.S)
    return re.sub(r"^\s*//.*$", "", sem_bloco, flags=re.M)


def test_o_mapa_3d_nao_busca_o_three_de_um_cdn():
    """A mesma regra da Vitrine: nada de CDN.

    Aqui o Three vem do `node_modules` por `import('three')`, que o
    bundler resolve em tempo de build. Um `<script src="https://…">`
    quebraria a pagina em rede fechada e tiraria a versao do controle
    do `package.json`.
    """
    fonte = _ler(os.path.join(RAIZ, "site", "components", "roadmap", "Mapa3D.tsx"))
    codigo = _sem_comentario(fonte)
    assert "cdn" not in codigo.lower()
    assert "https://" not in codigo
    assert "await import('three')" in codigo, "o Three precisa ser sob demanda"


def test_o_mapa_3d_devolve_a_cena_ao_desmontar():
    """Trocar de mapa tres vezes nao pode deixar tres cenas na GPU.

    E o vazamento classico de quem usa Three em React: `dispose()` nao
    e chamado, a geometria e o material continuam vivos, e a aba come
    memoria ate travar.
    """
    fonte = _ler(os.path.join(RAIZ, "site", "components", "roadmap", "Mapa3D.tsx"))
    assert "cancelAnimationFrame" in fonte
    assert "renderizador.dispose()" in fonte
    assert "for (const d of descartaveis) d.dispose()" in fonte


def test_o_mapa_3d_tem_saida_sem_webgl():
    """Um mapa que vira um retangulo vazio some com o conteudo junto."""
    fonte = _ler(os.path.join(RAIZ, "site", "components", "roadmap", "Mapa3D.tsx"))
    assert "function Lista(" in fonte
    assert "setSemWebGL" in fonte


def test_o_mapa_3d_respeita_quem_pediu_menos_movimento():
    fonte = _ler(os.path.join(RAIZ, "site", "components", "roadmap", "Mapa3D.tsx"))
    assert "prefers-reduced-motion" in fonte


def test_a_posicao_dos_nos_e_deterministica():
    """Uma constelacao que muda de forma a cada recarregamento nao e um
    mapa, e um protetor de tela — e o leitor perde a referencia de onde
    cada peca estava."""
    codigo = _sem_comentario(
        _ler(os.path.join(RAIZ, "site", "components", "roadmap", "Mapa3D.tsx")))
    assert "Math.random" not in codigo
