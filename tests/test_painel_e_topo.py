# -*- coding: utf-8 -*-
"""O cabecalho e o painel — seis decisoes que se desfazem sozinhas.

Nenhuma delas tem teste de comportamento possivel aqui (e React, e o
site e exportado estatico), mas todas tem uma forma no codigo que
diz se a decisao continua valendo. E o mesmo tipo de trava que este
repositorio ja usa para a gramatica do editor e para o catalogo de
comandos: conferir a FORMA quando o comportamento nao esta ao
alcance.

A mais importante e a primeira: um botao de login desabilitado por um
widget de terceiro e uma porta trancada por acidente, sem ninguem do
outro lado para explicar.
"""

import io
import os
import re

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(RAIZ, "site")

HEADER = os.path.join(SITE, "components", "Header.tsx")
ENTRAR = os.path.join(SITE, "components", "painel", "Entrar.tsx")
CASCA = os.path.join(SITE, "components", "painel", "Casca.tsx")
REDES = os.path.join(SITE, "components", "Redes.tsx")
SESSAO = os.path.join(SITE, "lib", "supabase", "sessao-leve.ts")


def ler(caminho):
    with io.open(caminho, encoding="utf-8") as f:
        return f.read()


def sem_comentario(fonte):
    """So o codigo. Uma trava que le o arquivo inteiro acusa a propria
    explicacao dela — ja aconteceu duas vezes neste repositorio."""
    sem_bloco = re.sub(r"/\*.*?\*/", "", fonte, flags=re.S)
    return re.sub(r"^\s*//.*$", "", sem_bloco, flags=re.M)


# ═══════════════════════════════════════════════════════════
#  1. O login nao pode travar por causa do captcha
# ═══════════════════════════════════════════════════════════

def test_o_botao_de_entrar_nao_depende_do_captcha():
    """A falha que motivou isto: o formulario ficava em "Conclua a
    verificacao" para sempre.

    Bastava o widget da Cloudflare RENDERIZAR e nao terminar — dominio
    ainda nao liberado na chave, rede que bloqueia, extensao de
    navegador — para o botao nunca habilitar. E `error-callback` nao
    dispara nesse caso: nao ha erro, ha espera.

    Falhar ABERTO aqui nao enfraquece nada: quem recusa de verdade e o
    servidor do Supabase, e a mensagem dele e traduzida. Um envio
    recusado com motivo e sempre melhor que um botao que nao responde.
    """
    codigo = sem_comentario(ler(ENTRAR))

    assert "disabled={enviando}" in codigo, (
        "o botao de enviar precisa depender SO de 'enviando'")

    proibidos = [
        "disabled={enviando || (TURNSTILE_LIGADO && !captcha",
        "disabled={!captcha",
        "disabled={enviando || !captcha",
    ]
    for p in proibidos:
        assert p not in codigo, (
            f"o botao voltou a depender do captcha: {p!r}\n"
            "Isso tranca o login quando o widget nao termina.")


def test_ha_prazo_para_a_espera_do_captcha():
    """Sem prazo, o rotulo fica em "verificando…" para sempre."""
    codigo = sem_comentario(ler(ENTRAR))
    assert "setTimeout" in codigo and "setCaptchaFalhou(true)" in codigo, (
        "falta o prazo que desiste da verificacao e libera o rotulo")


def test_o_token_do_captcha_e_reiniciado_a_cada_envio():
    """Ele e de USO UNICO: sem reiniciar, o segundo envio falha por
    'timeout-or-duplicate' — e a pessoa ve uma mensagem sobre captcha
    logo depois de corrigir a senha."""
    codigo = sem_comentario(ler(ENTRAR))
    assert "widget.current?.reiniciar()" in codigo


def test_criar_conta_abre_no_modo_certo():
    """O cabecalho oferece duas portas; levar as duas ao mesmo
    formulario em modo 'entrar' faria a segunda mentir."""
    codigo = sem_comentario(ler(ENTRAR))
    assert "URLSearchParams" in codigo and "'registrar'" in codigo


# ═══════════════════════════════════════════════════════════
#  2. O cabecalho
# ═══════════════════════════════════════════════════════════

def test_o_topo_mostra_painel_ou_as_duas_portas():
    codigo = sem_comentario(ler(HEADER))
    assert "temSessao === true" in codigo, "falta o caso de quem ja entrou"
    assert "temSessao === false" in codigo, "falta o caso de quem nao entrou"
    assert "Criar conta" in codigo and "Entrar" in codigo


def test_o_terceiro_estado_da_sessao_nao_desenha_nada():
    """`null` e "ainda nao sei", e e diferente de `false`.

    Sem ele o cabecalho desenharia "Entrar" no primeiro quadro e
    trocaria por "Painel" um instante depois — o pulo que faz a pagina
    parecer quebrada para quem ja esta autenticado.
    """
    codigo = sem_comentario(ler(SESSAO))
    assert "boolean | null" in codigo
    assert "configurado ? null : false" in codigo, (
        "sem as variaveis do Supabase nao ha login possivel, e o "
        "carregamento nunca terminaria")


def test_a_sessao_leve_nao_le_o_armazenamento_do_navegador_direto():
    """A chave e detalhe interno do SDK, e um token EXPIRADO continua
    la. `getSession()` responde pelo estado de verdade."""
    codigo = sem_comentario(ler(SESSAO))
    assert "getSession()" in codigo
    assert "onAuthStateChange" in codigo, "sair noutra aba tem de refletir aqui"
    assert "localStorage" not in codigo


def test_o_pypi_esta_na_fileira_de_icones():
    codigo = ler(REDES)
    assert "https://pypi.org/project/dataforge-lang/" in codigo
    assert "'PyPI'" in codigo


def test_todo_link_externo_do_topo_tem_noopener():
    """`target="_blank"` sem `rel="noopener"` da a pagina aberta um
    `window.opener` que redireciona esta aba — o tabnabbing reverso,
    que a propria documentacao de seguranca deste projeto descreve."""
    for caminho in (HEADER, REDES, CASCA):
        fonte = ler(caminho)
        for m in re.finditer(r"target=\"_blank\"", fonte):
            janela = fonte[max(0, m.start() - 400): m.end() + 400]
            assert "noopener" in janela, (
                f"target=_blank sem rel=noopener em {os.path.basename(caminho)}")


def test_os_atalhos_de_assunto_somem_dentro_da_documentacao():
    """Quatro das 190 rotas que a barra lateral ja lista, repetidas no
    topo, nao ajudam a achar nada e gastam a largura da busca."""
    codigo = sem_comentario(ler(HEADER))
    assert "naDocumentacao" in codigo
    assert "!naDocumentacao && (" in codigo, (
        "os atalhos precisam ficar dentro da condicao")
    # E continuam existindo fora dela: na home nao ha barra lateral.
    assert "/docs/primeiros-passos" in codigo
    assert "/docs/biblioteca" in codigo


# ═══════════════════════════════════════════════════════════
#  3. O painel
# ═══════════════════════════════════════════════════════════

def test_a_administracao_e_uma_area_propria():
    """Antes, as oito rotas de admin ficavam empilhadas abaixo das
    quatorze do usuario: vinte e duas entradas na mesma barra."""
    codigo = sem_comentario(ler(CASCA))
    assert "emAdmin" in codigo
    assert "startsWith('/painel/admin')" in codigo
    assert "emAdmin ? (" in codigo, (
        "dentro da administracao a barra precisa trocar INTEIRA")


def test_a_administracao_abre_em_aba_nova():
    codigo = sem_comentario(ler(CASCA))
    m = re.search(r'href="/painel/admin"\s*\n\s*target="_blank"', codigo)
    assert m, "o botao da administracao precisa abrir em aba nova"


def test_ha_volta_do_admin_para_o_painel():
    """Uma area separada sem caminho de volta e uma armadilha."""
    codigo = sem_comentario(ler(CASCA))
    assert "Voltar ao painel" in codigo


def test_o_painel_tem_as_duas_voltas():
    """Sair do painel nao pode ser a unica saida do painel: sem estes
    dois, voltar exigia editar a barra de endereco — ou clicar em
    'Sair', que encerra a sessao para navegar."""
    codigo = sem_comentario(ler(CASCA))
    assert "Voltar ao site" in codigo
    assert 'href="/docs"' in codigo, "falta o caminho para a documentacao"


@pytest.mark.parametrize("icone", ["voltar", "escudo", "abrir", "livro"])
def test_os_icones_usados_existem(icone):
    """Um `Icone` com nome que nao esta no mapa desenha um SVG vazio —
    sem erro, e sem icone."""
    codigo = ler(CASCA)
    assert re.search(rf"^\s+{icone}: '", codigo, re.M), (
        f"'{icone}' e usado e nao esta em CAMINHOS")
