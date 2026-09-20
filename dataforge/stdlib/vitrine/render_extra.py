"""O desenho dos componentes que vieram depois, e o estilo deles.

Este arquivo escreve em três lugares de `render.py`: `_DESENHO` (o
despacho por tipo de nó), `_SVG` (o despacho por tipo de gráfico) e as
listas `EXTRA_CSS`/`EXTRA_JS`. Ele é importado **no fim** daquele
arquivo, quando esses três já existem.

Por que não tudo num arquivo só
-------------------------------
`render.py` já tinha 1.600 linhas cobrindo trinta componentes. Somar
mais quarenta ali faria o desenho de um componente e o estilo dele
morarem a mil linhas de distância, e é essa distância que faz um botão
mudar de cor e ninguém achar onde. Aqui cada peça tem o seu desenho, o
seu CSS e o seu pedaço de cliente na mesma vizinhança.

A regra de sempre continua valendo: **todo texto passa por `_e()`**. O
único lugar que insere HTML cru é o `V.html(…)`, e ele avisa disso.
"""

import json
import math

from . import render as R
from . import render_graficos as RG

_e = R._e
_a = R._a
_filhos = R._filhos
_rotulo = R._rotulo
_problema = R._problema
_aria = R._aria
_classe_campo = R._classe_campo
_curto = R._numero_curto
_encurtar = R._encurtar


# ═══════════════════════════════════════════════════════════
#  Texto e conteúdo
# ═══════════════════════════════════════════════════════════

def d_legenda(no):
    return f'<p class="v-legenda-txt">{_e(no.props["conteudo"])}</p>'


def d_citacao(no):
    autor = (f'<footer class="v-citacao-autor">— {_e(no.props["autor"])}</footer>'
             if no.props.get("autor") else "")
    return (f'<blockquote class="v-citacao">{_e(no.props["conteudo"])}'
            f"{autor}</blockquote>")


def d_selo(no):
    p = no.props
    marca = (f'<span class="v-selo-icone">{_icone_svg(p["icone"], 13)}</span>'
             if p.get("icone") else "")
    return (f'<span class="v-selo v-selo-{_a(p.get("cor", "neutro"))}">'
            f'{marca}{_e(p["texto"])}</span>')


def d_selos(no):
    cor = _a(no.props.get("cor", "neutro"))
    itens = "".join(f'<span class="v-selo v-selo-{cor}">{_e(i)}</span>'
                    for i in no.props.get("itens", []))
    return f'<span class="v-selos">{itens}</span>'


def d_formula(no):
    corpo = _tex(no.props["tex"])
    marca = "div" if no.props.get("bloco") else "span"
    classe = "v-formula" + (" v-formula-bloco" if no.props.get("bloco") else "")
    return f'<{marca} class="{classe}">{corpo}</{marca}>'


#: O que a fórmula entende. Deliberadamente pequeno: é o que aparece
#: numa nota de rodapé de painel — e o que não está aqui sai como veio,
#: porque um símbolo errado é pior que um comando não traduzido.
_SIMBOLOS = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ",
    r"\epsilon": "ε", r"\theta": "θ", r"\lambda": "λ", r"\mu": "μ",
    r"\pi": "π", r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ", r"\phi": "φ",
    r"\omega": "ω", r"\Delta": "Δ", r"\Sigma": "Σ", r"\Omega": "Ω",
    r"\times": "×", r"\div": "÷", r"\pm": "±", r"\leq": "≤", r"\geq": "≥",
    r"\neq": "≠", r"\approx": "≈", r"\infty": "∞", r"\sum": "∑",
    r"\prod": "∏", r"\int": "∫", r"\sqrt": "√", r"\cdot": "·",
    r"\rightarrow": "→", r"\Rightarrow": "⇒", r"\in": "∈", r"\partial": "∂",
}


def _tex(texto):
    """Fração, potência e índice viram HTML; o resto é símbolo trocado."""
    import re

    saida = _e(texto)
    saida = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}",
                   r'<span class="v-frac"><i>\1</i><i>\2</i></span>', saida)
    saida = re.sub(r"\\sqrt\{([^{}]*)\}", r"√<span class='v-raiz'>\1</span>",
                   saida)
    saida = re.sub(r"\^\{([^{}]*)\}", r"<sup>\1</sup>", saida)
    saida = re.sub(r"\^(\w)", r"<sup>\1</sup>", saida)
    saida = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", saida)
    saida = re.sub(r"_(\w)", r"<sub>\1</sub>", saida)
    for comando, simbolo in _SIMBOLOS.items():
        saida = saida.replace(comando, simbolo)
    return saida.replace("{", "").replace("}", "")


def d_ajuda(no):
    p = no.props
    parametros = (f'<code class="v-ajuda-param">({", ".join(p["parametros"])})</code>'
                  if p.get("parametros") else "")
    doc = (f'<div class="v-md">{R.markdown(p["doc"])}</div>'
           if p.get("doc") else "")
    return (f'<div class="v-ajuda-bloco"><code class="v-ajuda-nome">'
            f'{_e(p["nome"])}</code>{parametros}{doc}</div>')


def d_fluxo(no):
    p = no.props
    passos = max(1, len(p["conteudo"]))
    animacao = (f' style="--v-passos:{passos};--v-dur:{passos * p["velocidade"]}ms"'
                if p.get("velocidade") else "")
    classe = "v-fluxo" + (" v-digitando" if p.get("velocidade") else "")
    return (f'<div class="{classe}"{animacao}>'
            f'<div class="v-md">{R.markdown(p["conteudo"])}</div></div>')


def d_icone(no):
    p = no.props
    estilo = f';color:{_a(p["cor"])}' if p.get("cor") else ""
    return (f'<span class="v-icone-caixa" style="width:{p["tamanho"]}px;'
            f'height:{p["tamanho"]}px{estilo}">'
            f'{_icone_svg(p["nome"], p["tamanho"])}</span>')


def _icone_svg(nome, tamanho=18):
    from .conteudo import ICONES
    caminho = ICONES.get(str(nome).strip().lower())
    if not caminho:
        return ""
    return (f'<svg viewBox="0 0 24 24" width="{int(tamanho)}" '
            f'height="{int(tamanho)}" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">'
            f'<path d="{_a(caminho)}"/></svg>')


# ═══════════════════════════════════════════════════════════
#  Mídia
# ═══════════════════════════════════════════════════════════

def d_pdf(no):
    p = no.props
    if not R._destino_seguro(p["origem"]):
        return _bloqueado("o endereço do PDF não é seguro")
    return (f'<object class="v-pdf" data="{_a(p["origem"])}#page={p["pagina"]}" '
            f'type="application/pdf" style="height:{p["altura"]}px">'
            f'<p class="v-legenda-txt">Seu navegador não abre PDF aqui. '
            f'<a class="v-link" href="{_a(p["origem"])}">Baixar o arquivo</a>.'
            f"</p></object>")


def d_iframe(no):
    p = no.props
    if not R._destino_seguro(p["origem"]):
        return _bloqueado("o endereço incorporado não é seguro")
    # `sandbox` sem `allow-same-origin`: o que entra aqui não é código
    # desta aplicação, e dar a ele a mesma origem é dar a ele a sessão
    # de quem está logado.
    return (f'<iframe class="v-iframe" src="{_a(p["origem"])}" '
            f'title="{_a(p["titulo"])}" style="height:{p["altura"]}px" '
            f'loading="lazy" referrerpolicy="no-referrer" '
            f'sandbox="allow-scripts allow-popups allow-forms"></iframe>')


def _bloqueado(motivo):
    return (f'<div class="v-alerta v-aviso" role="alert">'
            f'<span class="v-alerta-icone" aria-hidden="true">!</span>'
            f"<span>{_e(motivo)}</span></div>")


def d_galeria(no):
    p = no.props
    itens = "".join(
        f'<figure class="v-gal-item"><img src="{_a(img["origem"])}" '
        f'alt="{_a(img["legenda"])}" loading="lazy">'
        + (f'<figcaption>{_e(img["legenda"])}</figcaption>'
           if img["legenda"] else "")
        + "</figure>" for img in p["imagens"])
    return (f'<div class="v-galeria" style="--v-gal:{p["colunas"]}">'
            f"{itens}</div>")


# ═══════════════════════════════════════════════════════════
#  Situação
# ═══════════════════════════════════════════════════════════

def d_toast(no):
    p = no.props
    marca = (_icone_svg(p["icone"], 15) if p.get("icone") else "")
    return (f'<div class="v-toast v-toast-{_a(p.get("nivel", "info"))}" '
            f'role="status" aria-live="polite" '
            f'style="--v-toast-seg:{p.get("segundos", 4)}s">'
            f'{marca}<span>{_e(p["mensagem"])}</span></div>')


def d_esqueleto(no):
    p = no.props
    # A última linha é mais curta: um bloco de retângulos do mesmo
    # tamanho parece uma tabela quebrada, e não texto carregando.
    linhas = "".join(
        f'<span class="v-esq-linha" style="height:{p["altura"]}px;'
        f'width:{"62%" if i == p["linhas"] - 1 and p["linhas"] > 1 else p["largura"]}">'
        f"</span>" for i in range(p["linhas"]))
    return (f'<div class="v-esqueleto" aria-hidden="true" '
            f'data-v-carregando="1">{linhas}</div>')


def d_comemorar(no):
    tipo = no.props.get("tipo", "balao")
    formas = {"balao": "●", "neve": "❄", "confete": "▮"}
    pecas = "".join(
        f'<i style="--v-x:{(i * 37) % 100}%;--v-atraso:{(i % 12) * 0.18}s;'
        f'--v-giro:{(i * 47) % 360}deg">{formas.get(tipo, "●")}</i>'
        for i in range(26))
    return (f'<div class="v-comemorar v-com-{_a(tipo)}" aria-hidden="true">'
            f"{pecas}</div>")


def d_excecao(no):
    p = no.props
    detalhe = (f'<pre class="v-falha-detalhe">{_e(p["detalhe"])}</pre>'
               if p.get("detalhe") else "")
    return (f'<div class="v-alerta v-erro v-excecao" role="alert">'
            f'<span class="v-alerta-icone" aria-hidden="true">✕</span>'
            f'<span><code class="v-exc-tipo">{_e(p["tipo"])}</code> '
            f'{_e(p["mensagem"])}{detalhe}</span></div>')


def d_status(no):
    p = no.props
    estado = p.get("estado", "rodando")
    marcas = {"rodando": '<span class="v-giro" aria-hidden="true"></span>',
              "pronto": '<span class="v-status-ok" aria-hidden="true">✓</span>',
              "falhou": '<span class="v-status-erro" aria-hidden="true">✕</span>'}
    aberto = " open" if p.get("aberto") else ""
    return (f'<details class="v-status v-status-{_a(estado)}"{aberto}>'
            f'<summary>{marcas.get(estado, "")}'
            f'<span>{_e(p["rotulo"])}</span></summary>'
            f'<div class="v-status-int">{_filhos(no)}</div></details>')


# ═══════════════════════════════════════════════════════════
#  Conversa
# ═══════════════════════════════════════════════════════════

def d_chat(no):
    altura = (f' style="max-height:{int(no.props["altura"])}px;overflow-y:auto"'
              if no.props.get("altura") else "")
    return f'<div class="v-chat"{altura}>{_filhos(no)}</div>'


def d_chat_mensagem(no):
    p = no.props
    quem = p.get("quem", "assistente")
    inicial = {"usuario": "V", "assistente": "A", "sistema": "S"}.get(quem, "A")
    avatar = (f'<img class="v-chat-foto" src="{_a(p["avatar"])}" alt="">'
              if p.get("avatar") else
              f'<span class="v-chat-foto v-chat-inicial" aria-hidden="true">'
              f"{inicial}</span>")
    hora = (f'<time class="v-chat-hora">{_e(p["hora"])}</time>'
            if p.get("hora") else "")
    return (f'<div class="v-chat-msg v-chat-{_a(quem)}">{avatar}'
            f'<div class="v-chat-bolha">{_filhos(no)}{hora}</div></div>')


def d_chat_entrada(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    travado = " disabled" if p.get("desabilitado") else ""
    return (f'<div class="v-chat-entrada">'
            f'<input id="{ident}" class="v-entrada" type="text" '
            f'placeholder="{_a(p["dica"])}" data-v-campo="{_a(p["chave"])}" '
            f'data-v-sem-eco="1" data-v-enviar-chat="{_a(p["chave"])}"'
            f'{travado} autocomplete="off">'
            f'<button type="button" class="v-botao v-primario" '
            f'data-v-evento="{_a(p["chave"])}"{travado} aria-label="Enviar">'
            f'{_icone_svg("enviar", 16)}</button></div>')


# ═══════════════════════════════════════════════════════════
#  Entradas novas
# ═══════════════════════════════════════════════════════════

def d_hora(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    return (f'<div class="{_classe_campo(p)}">{_rotulo(p, ident)}'
            f'<input id="{ident}" class="v-entrada" type="time" '
            f'step="{int(p.get("passo", 60))}" value="{_a(p["valor"])}" '
            f'data-v-campo="{_a(p["chave"])}"{_aria(p)}>'
            f"{_problema(p)}</div>")


def d_periodo(no):
    p = no.props
    base = _a(p["chave"])
    return (f'<div class="{_classe_campo(p)}">{_rotulo(p)}'
            f'<div class="v-periodo">'
            f'<input class="v-entrada" type="date" value="{_a(p["inicio"])}" '
            f'aria-label="Início" data-v-campo="{base}" data-v-parte="0">'
            f'<span class="v-periodo-ate" aria-hidden="true">até</span>'
            f'<input class="v-entrada" type="date" value="{_a(p["fim"])}" '
            f'aria-label="Fim" data-v-campo="{base}" data-v-parte="1">'
            f"</div>{_problema(p)}</div>")


def d_faixa(no):
    p = no.props
    base = _a(p["chave"])
    comuns = (f'type="range" min="{_a(p["minimo"])}" max="{_a(p["maximo"])}" '
              f'step="{_a(p.get("passo", 1))}" class="v-slider v-slider-faixa" '
              f'data-v-campo="{base}" data-v-numero="1" data-v-adiar="1"')
    return (f'<div class="v-campo v-faixa">'
            f'<label class="v-rotulo">{_e(p["rotulo"])}'
            f'<span class="v-desl-valor" data-v-faixa-eco="{base}">'
            f'{_e(_curto(p["de"]))} – {_e(_curto(p["ate"]))}</span></label>'
            f'<div class="v-faixa-trilhos">'
            f'<input {comuns} value="{_a(p["de"])}" data-v-parte="0" '
            f'aria-label="mínimo">'
            f'<input {comuns} value="{_a(p["ate"])}" data-v-parte="1" '
            f'aria-label="máximo"></div></div>')


def d_deslizante_opcoes(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    marcas = "".join(f'<option value="{i}" label="{_a(o)}"></option>'
                     for i, o in enumerate(p["opcoes"]))
    return (f'<div class="v-campo v-desl">'
            f'<label class="v-rotulo" for="{ident}">{_e(p["rotulo"])}'
            f'<span class="v-desl-valor">{_e(p["valor"])}</span></label>'
            f'<input id="{ident}" class="v-slider" type="range" min="0" '
            f'max="{len(p["opcoes"]) - 1}" step="1" '
            f'value="{p["posicao"]}" list="l-{ident}" '
            f'data-v-campo="{_a(p["chave"])}" data-v-numero="1" '
            f'data-v-adiar="1" '
            f'aria-valuetext="{_a(p["valor"])}">'
            f'<datalist id="l-{ident}">{marcas}</datalist></div>')


def d_pilulas(no):
    p = no.props
    varios = p.get("varios")
    escolhidos = set(p["valor"] if varios else [p["valor"]])
    botoes = "".join(
        f'<button type="button" class="v-pilula'
        f'{" v-pilula-on" if o in escolhidos else ""}" '
        f'data-v-pilula="{_a(p["chave"])}" data-v-valor="{_a(o)}" '
        f'data-v-varios="{"1" if varios else ""}" '
        f'aria-pressed="{"true" if o in escolhidos else "false"}">'
        f"{_e(o)}</button>" for o in p["opcoes"])
    return (f'<fieldset class="{_classe_campo(p)}">'
            f'<legend class="v-rotulo">{_e(p["rotulo"])}</legend>'
            f'<div class="v-pilulas">{botoes}</div>{_problema(p)}</fieldset>')


def d_segmentado(no):
    p = no.props
    botoes = "".join(
        f'<button type="button" class="v-seg-item'
        f'{" v-seg-on" if o == p["valor"] else ""}" '
        f'data-v-pilula="{_a(p["chave"])}" data-v-valor="{_a(o)}" '
        f'role="radio" aria-checked="{"true" if o == p["valor"] else "false"}">'
        f"{_e(o)}</button>" for o in p["opcoes"])
    rotulo = (f'<legend class="v-rotulo">{_e(p["rotulo"])}</legend>'
              if p.get("rotulo") else "")
    return (f'<fieldset class="{_classe_campo(p)}">{rotulo}'
            f'<div class="v-segmentado" role="radiogroup" '
            f'aria-label="{_a(p["rotulo"])}">{botoes}</div></fieldset>')


def d_avaliacao(no):
    p = no.props
    formas = {"estrelas": ("★", "☆"), "coracoes": ("♥", "♡"),
              "polegares": ("👎", "👍")}
    cheio, vazio = formas.get(p.get("tipo"), formas["estrelas"])
    if p.get("tipo") == "polegares":
        itens = "".join(
            f'<button type="button" class="v-nota-item'
            f'{" v-nota-on" if p["valor"] == i + 1 else ""}" '
            f'data-v-nota="{_a(p["chave"])}" data-v-valor="{i + 1}" '
            f'aria-label="{"não gostei" if i == 0 else "gostei"}">'
            f"{(cheio, vazio)[i]}</button>" for i in range(2))
    else:
        itens = "".join(
            f'<button type="button" class="v-nota-item'
            f'{" v-nota-on" if i < p["valor"] else ""}" '
            f'data-v-nota="{_a(p["chave"])}" data-v-valor="{i + 1}" '
            f'aria-label="{i + 1} de {p["maximo"]}">'
            f'{cheio if i < p["valor"] else vazio}</button>'
            for i in range(p["maximo"]))
    return (f'<fieldset class="v-campo v-nota">'
            f'<legend class="v-rotulo">{_e(p["rotulo"])}</legend>'
            f'<div class="v-nota-itens">{itens}</div></fieldset>')


def d_tags(no):
    p = no.props
    base = _a(p["chave"])
    marcas = "".join(
        f'<span class="v-tag">{_e(t)}'
        f'<button type="button" class="v-tag-x" data-v-tag-rm="{base}" '
        f'data-v-valor="{_a(t)}" aria-label="remover {_a(t)}">×</button>'
        f"</span>" for t in p["valor"])
    lista = ""
    ligacao = ""
    if p.get("sugestoes"):
        lista = (f'<datalist id="s-{base}">' + "".join(
            f'<option value="{_a(s)}"></option>' for s in p["sugestoes"])
            + "</datalist>")
        ligacao = f' list="s-{base}"'
    guardado = _a(",".join(p["valor"]))
    return (f'<div class="{_classe_campo(p)}">{_rotulo(p)}'
            f'<div class="v-tags">{marcas}'
            f'<input class="v-tag-entrada" type="text" '
            f'placeholder="acrescentar…" data-v-tag="{base}"{ligacao} '
            f'autocomplete="off"></div>'
            f'<input type="hidden" data-v-campo="{base}" value="{guardado}" '
            f'data-v-tag-valor="{base}">'
            f"{lista}{_problema(p)}</div>")


def d_autocompletar(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    opcoes = "".join(f'<option value="{_a(o)}"></option>' for o in p["opcoes"])
    return (f'<div class="{_classe_campo(p)}">{_rotulo(p, ident)}'
            f'<input id="{ident}" class="v-entrada" type="text" '
            f'value="{_a(p["valor"])}" placeholder="{_a(p.get("dica", ""))}" '
            f'list="d-{ident}" data-v-campo="{_a(p["chave"])}" '
            f'autocomplete="off"{_aria(p)}>'
            f'<datalist id="d-{ident}">{opcoes}</datalist>'
            f"{_problema(p)}</div>")


def d_camera(no):
    p = no.props
    return (f'<div class="v-campo v-camera" data-v-camera="{_a(p["chave"])}">'
            f'{_rotulo(p)}'
            f'<video class="v-camera-tela" autoplay playsinline muted></video>'
            f'<canvas class="v-camera-tela" hidden></canvas>'
            f'<div class="v-camera-acoes">'
            f'<button type="button" class="v-botao v-secundario" '
            f'data-v-camera-abrir="1">Ligar a câmera</button>'
            f'<button type="button" class="v-botao v-primario" '
            f'data-v-camera-tirar="1" hidden>Tirar a foto</button></div>'
            f'<p class="v-legenda-txt v-camera-aviso" hidden></p></div>')


# ═══════════════════════════════════════════════════════════
#  Dados
# ═══════════════════════════════════════════════════════════

def d_indicador(no):
    p = no.props
    cor = p.get("cor") or ""
    estilo = f' style="--v-ind:{_a(_cor_do_tema(cor))}"' if cor else ""
    variacao = _variacao(p.get("variacao"))
    ajuda = (f'<span class="v-ajuda" title="{_a(p["ajuda"])}" '
             f'aria-label="{_a(p["ajuda"])}" role="note">?</span>'
             if p.get("ajuda") else "")
    marca = (f'<span class="v-ind-icone">{_icone_svg(p["icone"], 16)}</span>'
             if p.get("icone") else "")
    nota = (f'<span class="v-ind-nota">{_e(p["nota"])}</span>'
            if p.get("nota") else "")
    serie = (_mini_svg(p["serie"], _cor_do_tema(cor) or "var(--v-primaria)",
                       "area", 120, 30) if p.get("serie") else "")
    barra = ""
    if p.get("progresso"):
        pct = round(p["progresso"]["fracao"] * 100, 1)
        barra = (f'<div class="v-ind-meta"><div class="v-prog-trilho">'
                 f'<div class="v-prog-barra" style="width:{pct}%"></div></div>'
                 f'<span class="v-ind-meta-txt">{pct:g}% de '
                 f'{_e(p["progresso"]["alvo"])}</span></div>')
    return (f'<div class="v-indicador{" v-ind-cor" if cor else ""}"{estilo}>'
            f'<div class="v-ind-topo"><span class="v-ind-rotulo">'
            f'{_e(p["rotulo"])}{ajuda}</span>{marca}</div>'
            f'<div class="v-ind-valor">{_e(p["valor"])}</div>'
            f'<div class="v-ind-pe">{variacao}{nota}</div>'
            f"{barra}{serie}</div>")


def d_indicadores(no):
    colunas = no.props.get("colunas") or 0
    estilo = (f' style="grid-template-columns:repeat({colunas},minmax(0,1fr))"'
              if colunas else "")
    return f'<div class="v-indicadores"{estilo}>{_filhos(no)}</div>'


def _cor_do_tema(nome):
    """Um nome de cor do tema vira a variável CSS dele.

    Aceitar hexadecimal também é deliberado: a faixa de um indicador às
    vezes vem da própria categoria do dado, e obrigar a traduzir para
    um nome do tema tiraria a cor do gráfico ao lado.
    """
    conhecidas = {"primaria": "var(--v-primaria)", "sucesso": "var(--v-sucesso)",
                  "erro": "var(--v-erro)", "aviso": "var(--v-aviso)",
                  "info": "var(--v-info)", "neutro": "var(--v-texto-fraco)"}
    return conhecidas.get(str(nome), str(nome))


def _variacao(bruta):
    if bruta is None:
        return ""
    try:
        n = float(bruta)
    except (TypeError, ValueError):
        return f'<span class="v-variacao v-igual">{_e(bruta)}</span>'
    classe = "v-sobe" if n > 0 else ("v-desce" if n < 0 else "v-igual")
    seta = "▲" if n > 0 else ("▼" if n < 0 else "—")
    palavra = "aumento de" if n > 0 else (
        "queda de" if n < 0 else "sem variação,")
    return (f'<span class="v-variacao {classe}">'
            f'<span aria-hidden="true">{seta}</span> '
            f'<span class="v-so-leitor">{palavra} </span>{abs(n):g}%</span>')


def d_mini(no):
    p = no.props
    cor = p.get("cor") or "var(--v-primaria)"
    valor = ""
    if p.get("mostrar_valor") and p["valores"]:
        valor = (f'<span class="v-mini-valor">'
                 f'{_e(_curto(p["valores"][-1]))}</span>')
    return (f'<span class="v-mini">'
            f'{_mini_svg(p["valores"], cor, p["tipo"], p["largura"], p["altura"])}'
            f"{valor}</span>")


def _mini_svg(valores, cor, tipo="linha", largura=120, altura=30):
    """A série miúda. Sem eixo, sem grade e sem rótulo — de propósito."""
    numeros = [v for v in valores if isinstance(v, (int, float))]
    if len(numeros) < 2:
        return ""
    menor, maior = min(numeros), max(numeros)
    faixa = (maior - menor) or 1.0
    passo = largura / (len(numeros) - 1)
    pontos = [(i * passo, altura - 2 - (v - menor) / faixa * (altura - 4))
              for i, v in enumerate(numeros)]
    if tipo == "barras":
        larg = max(1.0, passo * 0.68)
        corpo = "".join(
            f'<rect x="{x - larg / 2:.1f}" y="{y:.1f}" width="{larg:.1f}" '
            f'height="{altura - y:.1f}" fill="{_a(cor)}" rx="1"/>'
            for x, y in pontos)
    else:
        traco = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                         for i, (x, y) in enumerate(pontos))
        corpo = ""
        if tipo == "area":
            corpo = (f'<path d="{traco} L{pontos[-1][0]:.1f},{altura} '
                     f'L0,{altura} Z" fill="{_a(cor)}" fill-opacity="0.18"/>')
        corpo += (f'<path d="{traco}" fill="none" stroke="{_a(cor)}" '
                  f'stroke-width="1.8" stroke-linecap="round" '
                  f'stroke-linejoin="round"/>')
    return (f'<svg class="v-mini-svg" viewBox="0 0 {largura} {altura}" '
            f'width="{largura}" height="{altura}" preserveAspectRatio="none" '
            f'aria-hidden="true">{corpo}</svg>')


def d_grade(no):
    p = no.props
    k = _a(p["chave"])
    partes = ['<div class="v-grade-caixa">']

    topo = []
    if p.get("busca"):
        topo.append(
            f'<input class="v-entrada v-busca" type="search" '
            f'placeholder="filtrar…" value="{_a(p.get("termo", ""))}" '
            f'data-v-campo="{k}:busca" aria-label="Filtrar a tabela">')
    topo.append(f'<span class="v-grade-conta">{p["total"]} linha(s)</span>')
    partes.append(f'<div class="v-grade-topo">{"".join(topo)}</div>')

    cabeca = []
    if p.get("selecionar"):
        cabeca.append('<th class="v-col-sel"><span class="v-so-leitor">'
                      "Seleção</span></th>")
    if p.get("numerar"):
        cabeca.append('<th class="v-col-num">#</th>')
    for col in p["colunas"]:
        seta = ""
        if p.get("ordem") == col["nome"]:
            seta = f'<span class="v-seta">{"▼" if p.get("desc") else "▲"}</span>'
        largura = (f' style="width:{col["largura"]}px"'
                   if col.get("largura") else "")
        titulo = (f' title="{_a(col["ajuda"])}"' if col.get("ajuda") else "")
        cabeca.append(
            f'<th class="v-al-{_a(col["alinhar"])}"{largura}{titulo}>'
            f'<button type="button" class="v-col-ordem" '
            f'data-v-ordenar-col="{k}" data-v-valor="{_a(col["nome"])}">'
            f'{_e(col["titulo"])}{seta}</button></th>')

    corpo = []
    for i, linha in enumerate(p["linhas"]):
        celulas = []
        if p.get("selecionar"):
            tipo = "radio" if p["selecionar"] == "linha" else "checkbox"
            celulas.append(
                f'<td class="v-col-sel"><input type="{tipo}" '
                f'value="{_a(linha["id"])}" data-v-campo="{k}:selecao" '
                f'data-v-varios="1"{" checked" if linha["marcada"] else ""} '
                f'aria-label="selecionar a linha {int(linha["id"]) + 1}"></td>')
        if p.get("numerar"):
            celulas.append(f'<td class="v-col-num">'
                           f'{p.get("primeiro", 0) + i + 1}</td>')
        celulas.extend(_celula_html(c) for c in linha["celulas"])
        celulas_html = "".join(celulas)
        corpo.append(f"<tr>{celulas_html}</tr>")

    rodape = ""
    if p.get("rodape"):
        vazias = (1 if p.get("selecionar") else 0) + (1 if p.get("numerar") else 0)
        celulas = "".join(f'<td class="v-al-{_a(t.get("alinhar", "esquerda"))}">'
                          f'{_e(t["texto"])}</td>' for t in p["rodape"])
        rodape = (f"<tfoot><tr>" + '<td></td>' * vazias + celulas
                  + "</tr></tfoot>")

    vazio = (f'<tbody><tr><td class="v-vazio" colspan="99">'
             f'{_e(p.get("vazio", "sem dados"))}</td></tr></tbody>')
    altura = (f'max-height:{int(p["altura"])}px' if p.get("altura") else "")
    partes.append(
        f'<div class="v-tabela-caixa v-rolagem" style="{altura}">'
        f'<table class="v-tabela v-grade-tabela v-dens-{_a(p.get("densidade", "normal"))}">'
        f'<thead><tr>{"".join(cabeca)}</tr></thead>'
        f'{"".join(corpo) and f"<tbody>{chr(10).join(corpo)}</tbody>" or vazio}'
        f"{rodape}</table></div>")

    if p.get("paginas", 1) > 1:
        partes.append(_paginacao(k, p["pagina"], p["paginas"]))
    partes.append("</div>")
    return "".join(partes)


def _celula_html(c):
    classe = f'v-al-{_a(c.get("alinhar", "esquerda"))}'
    if c.get("cor"):
        classe += f' v-cel-{_a(c["cor"])}'
    tipo = c.get("tipo")
    if tipo in ("barra", "progresso"):
        pct = round(c.get("fracao", 0.0) * 100, 1)
        return (f'<td class="{classe}"><div class="v-cel-barra">'
                f'<div class="v-cel-barra-int" style="width:{pct}%"></div>'
                f'</div><span class="v-cel-barra-txt">{_e(c["texto"])}</span></td>')
    if tipo == "mini":
        return (f'<td class="{classe}">'
                f'{_mini_svg(c.get("serie", []), "var(--v-primaria)", "linha", 90, 22)}'
                f"</td>")
    if tipo == "logico":
        marca = "✓" if c.get("logico") else "—"
        return (f'<td class="{classe} v-cel-logico">'
                f'<span aria-hidden="true">{marca}</span>'
                f'<span class="v-so-leitor">{"sim" if c.get("logico") else "não"}'
                f"</span></td>")
    if tipo == "link" and c.get("destino"):
        if not R._destino_seguro(c["destino"]):
            return f'<td class="{classe}">{_e(c["texto"])}</td>'
        return (f'<td class="{classe}"><a class="v-link" '
                f'href="{_a(c["destino"])}" target="_blank" '
                f'rel="noopener noreferrer">{_e(c["texto"] or c["destino"])}'
                f"</a></td>")
    if tipo == "imagem" and c.get("origem"):
        return (f'<td class="{classe}"><img class="v-cel-img" '
                f'src="{_a(c["origem"])}" alt="" loading="lazy"></td>')
    if tipo == "selo":
        return (f'<td class="{classe}"><span class="v-selo '
                f'v-selo-{_a(c.get("cor") or "neutro")}">{_e(c["texto"])}'
                f"</span></td>")
    return f'<td class="{classe}">{_e(c["texto"])}</td>'


def _paginacao(chave, pagina, paginas):
    def botao(alvo, rotulo, ativo=False, travado=False):
        if travado:
            return (f'<span class="v-pag-item v-pag-off" aria-hidden="true">'
                    f"{_e(rotulo)}</span>")
        atual = ' aria-current="page"' if ativo else ""
        return (f'<button type="button" class="v-pag-item'
                f'{" v-pag-on" if ativo else ""}" data-v-pagina="{chave}" '
                f'data-v-valor="{alvo}"{atual}>{_e(rotulo)}</button>')

    itens = [botao(pagina - 1, "‹", travado=pagina <= 1)]
    # Uma janela em volta da página atual: numerar cem páginas encheria
    # a linha e nenhuma delas seria clicada.
    inicio = max(1, min(pagina - 2, paginas - 4))
    for numero in range(inicio, min(paginas, inicio + 4) + 1):
        itens.append(botao(numero, str(numero), ativo=numero == pagina))
    itens.append(botao(pagina + 1, "›", travado=pagina >= paginas))
    return (f'<nav class="v-paginacao" aria-label="Páginas da tabela">'
            f'{"".join(itens)}<span class="v-pag-de">de {paginas}</span></nav>')


def d_editor(no):
    p = no.props
    k = _a(p["chave"])
    cabeca = "".join(f'<th class="v-al-{_a(c["alinhar"])}">{_e(c["titulo"])}</th>'
                     for c in p["colunas"])
    if p.get("remover"):
        cabeca += '<th class="v-col-sel"><span class="v-so-leitor">Remover</span></th>'
    linhas = []
    for linha in p["linhas"]:
        celulas = []
        for c in linha["celulas"]:
            if not c["editavel"]:
                celulas.append(f'<td class="v-al-{_a(c["alinhar"])}">'
                               f'{_e(c["texto"] or c["valor"])}</td>')
            elif c["opcoes"]:
                opcoes = "".join(
                    f'<option value="{_a(o)}"'
                    f'{" selected" if o == c["valor"] else ""}>{_e(o)}</option>'
                    for o in c["opcoes"])
                celulas.append(
                    f'<td><select class="v-cel-campo" '
                    f'data-v-campo="{_a(c["campo"])}">{opcoes}</select></td>')
            elif c["tipo"] == "logico":
                marcado = " checked" if c["valor"] in ("yes", "True", "1") else ""
                celulas.append(
                    f'<td class="v-al-centro"><input type="checkbox"{marcado} '
                    f'data-v-campo="{_a(c["campo"])}" data-v-bool="1"></td>')
            else:
                numero = c["tipo"] in ("numero", "moeda", "percentual",
                                       "compacto", "barra", "progresso")
                # As duas partes saem da f-string: aspa igual dentro da
                # interpolação só compila a partir do 3.12, e este
                # projeto vale do 3.10 em diante.
                tipo_html = "number" if numero else "text"
                marca_numero = ' data-v-numero="1"' if numero else ""
                celulas.append(
                    f'<td><input class="v-cel-campo v-al-{_a(c["alinhar"])}" '
                    f'type="{tipo_html}" value="{_a(c["valor"])}" '
                    f'data-v-campo="{_a(c["campo"])}"{marca_numero}></td>')
        if p.get("remover"):
            celulas.append(
                f'<td class="v-col-sel"><button type="button" '
                f'class="v-linha-x" data-v-evento="{k}:rm:{_a(linha["id"])}" '
                f'aria-label="remover a linha">×</button></td>')
        linhas.append("<tr>" + "".join(celulas) + "</tr>")
    altura = (f'max-height:{int(p["altura"])}px' if p.get("altura") else "")
    novo = ""
    if p.get("acrescentar"):
        novo = (f'<button type="button" class="v-botao v-secundario v-editor-add" '
                f'data-v-evento="{k}:novo">+ Acrescentar linha</button>')
    return (f'<div class="v-editor">'
            f'<div class="v-tabela-caixa v-rolagem" style="{altura}">'
            f'<table class="v-tabela v-grade-tabela">'
            f'<thead><tr>{cabeca}</tr></thead>'
            f'<tbody>{"".join(linhas)}</tbody></table></div>{novo}</div>')


# ═══════════════════════════════════════════════════════════
#  Layout
# ═══════════════════════════════════════════════════════════

def d_malha(no):
    p = no.props
    esp = {"nenhum": "0", "pequeno": "8px", "medio": "16px", "grande": "26px"}
    return (f'<div class="v-malha" style="gap:{esp.get(p.get("espacamento"), "16px")};'
            f'grid-template-columns:repeat(auto-fit,minmax(min({p["minimo"]}px,100%),1fr))">'
            f"{_filhos(no)}</div>")


def d_painel(no):
    p = no.props
    cabeca = ""
    if p.get("titulo") or p.get("subtitulo"):
        marca = (f'<span class="v-painel-icone">{_icone_svg(p["icone"], 15)}</span>'
                 if p.get("icone") else "")
        sub = (f'<span class="v-painel-sub">{_e(p["subtitulo"])}</span>'
               if p.get("subtitulo") else "")
        cabeca = (f'<header class="v-painel-topo">{marca}'
                  f'<span class="v-painel-titulo">{_e(p["titulo"])}</span>'
                  f"{sub}</header>")
    estilo = []
    if p.get("cor"):
        estilo.append(f"--v-painel:{_cor_do_tema(p['cor'])}")
    if p.get("altura"):
        estilo.append(f"min-height:{int(p['altura'])}px")
    atributo = f' style="{";".join(estilo)}"' if estilo else ""
    classe = "v-painel"
    if p.get("cor"):
        classe += " v-painel-cor"
    if p.get("compacto"):
        classe += " v-painel-compacto"
    return (f'<section class="{classe}"{atributo}>{cabeca}'
            f'<div class="v-painel-int">{_filhos(no)}</div></section>')


def d_barra_superior(no):
    p = no.props
    marca = ""
    if p.get("logo"):
        marca = f'<img class="v-topo-logo" src="{_a(p["logo"])}" alt="">'
    titulo = ""
    if p.get("titulo"):
        sub = (f'<span class="v-topo-sub">{_e(p["subtitulo"])}</span>'
               if p.get("subtitulo") else "")
        titulo = (f'<span class="v-topo-marca">{_e(p["titulo"])}{sub}</span>')
    itens = []
    for item in p["itens"]:
        ativo = " v-topo-on" if item["rotulo"] == p.get("ativo") else ""
        destino = item["destino"] or "/" + item["rotulo"].lower().replace(" ", "-")
        icone = (f'{_icone_svg(item["icone"], 15)} ' if item["icone"] else "")
        atual = ' aria-current="page"' if ativo else ""
        itens.append(f'<a class="v-topo-item{ativo}" href="{_a(destino)}"{atual}>'
                     f'{icone}{_e(item["rotulo"])}</a>')
    navegacao = (f'<nav class="v-topo-nav" aria-label="Seções">'
                 f'{"".join(itens)}</nav>' if itens else "")
    return (f'<header class="v-barra-superior">{marca}{titulo}{navegacao}'
            f'<div class="v-topo-acoes">{_filhos(no)}</div></header>')


def d_dialogo(no):
    p = no.props
    if not p.get("aberto"):
        return ""
    k = _a(p["chave"])
    return (f'<div class="v-dialogo-fundo" data-v-evento="{k}:fechar" '
            f'role="presentation"></div>'
            f'<div class="v-dialogo" role="dialog" aria-modal="true" '
            f'aria-label="{_a(p["titulo"])}" '
            f'style="max-width:{p["largura"]}px">'
            f'<header class="v-dialogo-topo">'
            f'<span class="v-dialogo-titulo">{_e(p["titulo"])}</span>'
            f'<button type="button" class="v-dialogo-x" '
            f'data-v-evento="{k}:fechar" aria-label="Fechar">×</button></header>'
            f'<div class="v-dialogo-int">{_filhos(no)}</div></div>')


def d_popover(no):
    p = no.props
    icone = (f'{_icone_svg(p["icone"], 15)} ' if p.get("icone") else "")
    return (f'<details class="v-popover">'
            f'<summary class="v-botao v-secundario">{icone}'
            f'{_e(p["rotulo"])}</summary>'
            f'<div class="v-popover-int" style="width:{p["largura"]}px">'
            f"{_filhos(no)}</div></details>")


def d_passos(no):
    p = no.props
    feitos = set(p.get("concluidos", []))
    itens = []
    for i, rotulo in enumerate(p["rotulos"]):
        if rotulo in feitos:
            estado, marca = "v-passo-feito", "✓"
        elif i == p["atual"]:
            estado, marca = "v-passo-agora", str(i + 1)
        else:
            estado, marca = "v-passo-futuro", str(i + 1)
        atual = ' aria-current="step"' if i == p["atual"] else ""
        itens.append(
            f'<li class="v-passo {estado}"{atual}>'
            f'<span class="v-passo-bola" aria-hidden="true">{marca}</span>'
            f'<span class="v-passo-txt">{_e(rotulo)}</span></li>')
    return f'<ol class="v-passos">{"".join(itens)}</ol>'


def d_separador(no):
    p = no.props
    if not p.get("texto"):
        return '<hr class="v-divisor">'
    icone = (f'{_icone_svg(p["icone"], 14)} ' if p.get("icone") else "")
    return (f'<div class="v-separador"><span class="v-separador-txt">'
            f'{icone}{_e(p["texto"])}</span></div>')


def d_fragmento(no):
    p = no.props
    tempo = (f' data-v-frag-seg="{p["a_cada"]}"' if p.get("a_cada") else "")
    return (f'<div class="v-fragmento" data-v-frag="{_a(p["chave"])}"{tempo}>'
            f"{_filhos(no)}</div>")


# ═══════════════════════════════════════════════════════════
#  Registro
# ═══════════════════════════════════════════════════════════

R._DESENHO.update({
    "legenda": d_legenda, "citacao": d_citacao, "selo": d_selo,
    "selos": d_selos, "formula": d_formula, "ajuda": d_ajuda,
    "fluxo": d_fluxo, "icone": d_icone,
    "pdf": d_pdf, "iframe": d_iframe, "galeria": d_galeria,
    "toast": d_toast, "esqueleto": d_esqueleto, "comemorar": d_comemorar,
    "excecao": d_excecao, "status": d_status,
    "chat": d_chat, "chat_mensagem": d_chat_mensagem,
    "chat_entrada": d_chat_entrada,
    "hora": d_hora, "periodo": d_periodo, "faixa": d_faixa,
    "deslizante_opcoes": d_deslizante_opcoes, "pilulas": d_pilulas,
    "segmentado": d_segmentado, "avaliacao": d_avaliacao, "tags": d_tags,
    "autocompletar": d_autocompletar, "camera": d_camera,
    "indicador": d_indicador, "indicadores": d_indicadores, "mini": d_mini,
    "grade": d_grade, "editor": d_editor,
    "malha": d_malha, "painel": d_painel, "barra_superior": d_barra_superior,
    "dialogo": d_dialogo, "popover": d_popover, "passos": d_passos,
    "separador": d_separador, "fragmento": d_fragmento,
})

R._SVG.update(RG.DESENHOS)


# ═══════════════════════════════════════════════════════════
#  Estilo
# ═══════════════════════════════════════════════════════════

_CSS = """
.v-legenda-txt{font-size:.8rem;color:var(--v-texto-fraco);margin:.3em 0 .8em}
.v-citacao{margin:14px 0;padding:10px 16px;border-left:3px solid
 var(--v-primaria);background:var(--v-fundo-alt);border-radius:0
 var(--v-raio) var(--v-raio) 0}
.v-citacao-autor{margin-top:6px;font-size:.82rem;color:var(--v-texto-fraco)}

.v-selo{display:inline-flex;align-items:center;gap:5px;padding:2px 9px;
 border-radius:999px;font-size:.76rem;font-weight:600;line-height:1.7;
 border:1px solid transparent;white-space:nowrap}
.v-selos{display:inline-flex;flex-wrap:wrap;gap:6px}
.v-selo-icone{display:inline-flex}
.v-selo-neutro{background:var(--v-fundo-alt);color:var(--v-texto-fraco);
 border-color:var(--v-borda)}
.v-selo-sucesso{background:color-mix(in srgb,var(--v-sucesso) 16%,transparent);
 color:var(--v-sucesso);border-color:color-mix(in srgb,var(--v-sucesso) 38%,transparent)}
.v-selo-erro{background:color-mix(in srgb,var(--v-erro) 16%,transparent);
 color:var(--v-erro);border-color:color-mix(in srgb,var(--v-erro) 38%,transparent)}
.v-selo-aviso{background:color-mix(in srgb,var(--v-aviso) 18%,transparent);
 color:var(--v-aviso);border-color:color-mix(in srgb,var(--v-aviso) 38%,transparent)}
.v-selo-info{background:color-mix(in srgb,var(--v-info) 16%,transparent);
 color:var(--v-info);border-color:color-mix(in srgb,var(--v-info) 38%,transparent)}
.v-selo-primaria{background:color-mix(in srgb,var(--v-primaria) 20%,transparent);
 color:var(--v-primaria);border-color:color-mix(in srgb,var(--v-primaria) 44%,transparent)}

.v-formula{font-family:var(--v-fonte-mono);font-size:1.02em}
.v-formula-bloco{text-align:center;margin:16px 0;font-size:1.12em}
.v-frac{display:inline-flex;flex-direction:column;vertical-align:-.5em;
 text-align:center}
.v-frac>i:first-child{border-bottom:1px solid currentColor;font-style:normal;
 padding:0 .3em}
.v-frac>i:last-child{font-style:normal;padding:0 .3em}
.v-raiz{border-top:1px solid currentColor;padding:0 .2em}
.v-ajuda-bloco{border:1px solid var(--v-borda);border-left:3px solid
 var(--v-info);border-radius:var(--v-raio);padding:12px 15px;margin:12px 0;
 background:var(--v-superficie)}
.v-ajuda-nome{font-weight:700;background:none;padding:0}
.v-ajuda-param{color:var(--v-texto-fraco);background:none}

.v-fluxo{margin:6px 0}
.v-digitando .v-md>*:first-child{animation:v-escrever var(--v-dur,1s) steps(var(--v-passos,40))}
@keyframes v-escrever{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
.v-icone-caixa{display:inline-flex;align-items:center;justify-content:center;
 vertical-align:-.16em;flex:0 0 auto}

.v-pdf,.v-iframe{width:100%;border:1px solid var(--v-borda);
 border-radius:var(--v-raio);margin:12px 0;background:var(--v-superficie)}
.v-galeria{display:grid;gap:10px;margin:14px 0;
 grid-template-columns:repeat(var(--v-gal,3),minmax(0,1fr))}
.v-gal-item{margin:0}
.v-gal-item img{width:100%;height:auto;border-radius:var(--v-raio);display:block}
.v-gal-item figcaption{font-size:.78rem;color:var(--v-texto-fraco);margin-top:4px}

.v-toast{position:fixed;right:18px;z-index:120;display:flex;gap:8px;
 align-items:center;padding:10px 15px;border-radius:var(--v-raio);
 background:var(--v-superficie);border:1px solid var(--v-borda);
 box-shadow:0 8px 28px rgba(0,0,0,.22);font-size:.9rem;
 animation:v-toast-entra .22s ease, v-toast-sai .4s ease var(--v-toast-seg,4s) forwards}
.v-toast-sucesso{border-left:3px solid var(--v-sucesso)}
.v-toast-erro{border-left:3px solid var(--v-erro)}
.v-toast-aviso{border-left:3px solid var(--v-aviso)}
.v-toast-info{border-left:3px solid var(--v-info)}
/* Empilhados a partir do rodapé: o segundo aviso não cobre o primeiro. */
.v-toast{bottom:18px}
.v-toast~.v-toast{bottom:76px}
.v-toast~.v-toast~.v-toast{bottom:134px}
@keyframes v-toast-entra{from{opacity:0;transform:translateY(12px)}}
@keyframes v-toast-sai{to{opacity:0;transform:translateY(-6px);visibility:hidden}}

.v-esqueleto{display:flex;flex-direction:column;gap:9px;margin:12px 0}
.v-esq-linha{display:block;border-radius:5px;
 background:linear-gradient(90deg,var(--v-fundo-alt) 25%,
 var(--v-borda) 37%,var(--v-fundo-alt) 63%);
 background-size:400% 100%;animation:v-brilho 1.4s ease-in-out infinite}
@keyframes v-brilho{0%{background-position:100% 0}100%{background-position:0 0}}

.v-comemorar{position:fixed;inset:0;pointer-events:none;z-index:110;
 overflow:hidden}
.v-comemorar i{position:absolute;top:-24px;left:var(--v-x);font-size:18px;
 color:var(--v-primaria);animation:v-cair 3.4s linear var(--v-atraso) forwards;
 transform:rotate(var(--v-giro))}
.v-com-balao i{animation-name:v-subir;top:auto;bottom:-30px;font-size:26px}
.v-com-neve i{color:var(--v-info)}
.v-com-confete i:nth-child(3n){color:var(--v-sucesso)}
.v-com-confete i:nth-child(3n+1){color:var(--v-erro)}
@keyframes v-cair{to{transform:translateY(105vh) rotate(720deg);opacity:.1}}
@keyframes v-subir{to{transform:translateY(-105vh) rotate(90deg);opacity:.1}}
.v-exc-tipo{background:color-mix(in srgb,var(--v-erro) 18%,transparent);
 color:var(--v-erro);font-weight:700}

.v-status{border:1px solid var(--v-borda);border-radius:var(--v-raio);
 margin:12px 0;background:var(--v-superficie)}
.v-status>summary{cursor:pointer;padding:11px 15px;font-weight:550;
 display:flex;align-items:center;gap:9px;list-style:none}
.v-status>summary::-webkit-details-marker{display:none}
.v-status-int{padding:2px 15px 14px}
.v-status-ok{color:var(--v-sucesso);font-weight:700}
.v-status-erro{color:var(--v-erro);font-weight:700}
.v-status-pronto{border-color:color-mix(in srgb,var(--v-sucesso) 40%,var(--v-borda))}
.v-status-falhou{border-color:color-mix(in srgb,var(--v-erro) 44%,var(--v-borda))}

.v-chat{display:flex;flex-direction:column;gap:14px;margin:14px 0}
.v-chat-msg{display:flex;gap:10px;align-items:flex-start}
.v-chat-usuario{flex-direction:row-reverse}
.v-chat-foto{width:30px;height:30px;border-radius:50%;flex:0 0 auto;
 object-fit:cover}
.v-chat-inicial{display:flex;align-items:center;justify-content:center;
 background:var(--v-fundo-alt);border:1px solid var(--v-borda);
 font-size:.76rem;font-weight:700;color:var(--v-texto-fraco)}
.v-chat-bolha{background:var(--v-superficie);border:1px solid var(--v-borda);
 border-radius:14px;padding:9px 15px;max-width:min(76ch,86%)}
.v-chat-usuario .v-chat-bolha{background:color-mix(in srgb,
 var(--v-primaria) 14%,var(--v-superficie))}
.v-chat-sistema .v-chat-bolha{background:var(--v-fundo-alt);
 font-size:.86rem;color:var(--v-texto-fraco)}
.v-chat-bolha .v-md p:first-child{margin-top:0}
.v-chat-bolha .v-md p:last-child{margin-bottom:0}
.v-chat-hora{display:block;font-size:.7rem;color:var(--v-texto-fraco);
 margin-top:5px}
.v-chat-entrada{display:flex;gap:8px;align-items:center;margin:14px 0;
 position:sticky;bottom:0;background:var(--v-fundo);padding:8px 0}
.v-chat-entrada .v-entrada{flex:1}

.v-periodo{display:flex;align-items:center;gap:8px}
.v-periodo .v-entrada{flex:1;min-width:0}
.v-periodo-ate{color:var(--v-texto-fraco);font-size:.82rem}
.v-faixa-trilhos{position:relative;display:grid}
.v-faixa-trilhos .v-slider{grid-area:1/1;background:transparent;
 pointer-events:none}
.v-faixa-trilhos .v-slider::-webkit-slider-thumb{pointer-events:auto}
.v-faixa-trilhos .v-slider::-moz-range-thumb{pointer-events:auto}

.v-pilulas{display:flex;flex-wrap:wrap;gap:7px}
.v-pilula{font:inherit;font-size:.85rem;font-weight:540;padding:5px 13px;
 border-radius:999px;border:1px solid var(--v-borda);cursor:pointer;
 background:var(--v-superficie);color:var(--v-texto-fraco);
 transition:background .12s,color .12s}
.v-pilula:hover{border-color:var(--v-primaria)}
.v-pilula-on{background:var(--v-primaria);color:var(--v-primaria-texto);
 border-color:var(--v-primaria)}
.v-segmentado{display:inline-flex;border:1px solid var(--v-borda);
 border-radius:var(--v-raio);overflow:hidden;background:var(--v-fundo-alt)}
.v-seg-item{font:inherit;font-size:.86rem;font-weight:540;padding:6px 15px;
 border:0;cursor:pointer;background:transparent;color:var(--v-texto-fraco);
 border-right:1px solid var(--v-borda)}
.v-seg-item:last-child{border-right:0}
.v-seg-on{background:var(--v-superficie);color:var(--v-texto);font-weight:620;
 box-shadow:inset 0 -2px 0 var(--v-primaria)}
.v-nota-itens{display:flex;gap:3px}
.v-nota-item{font:inherit;font-size:1.32rem;line-height:1;background:none;
 border:0;cursor:pointer;color:var(--v-borda);padding:1px 2px}
.v-nota-on{color:var(--v-primaria)}
.v-nota-item:hover{transform:scale(1.12)}

.v-tags{display:flex;flex-wrap:wrap;gap:6px;align-items:center;
 border:1px solid var(--v-borda);border-radius:var(--v-raio);
 padding:5px 8px;background:var(--v-superficie);min-height:37px}
.v-tag{display:inline-flex;align-items:center;gap:4px;padding:2px 4px 2px 9px;
 border-radius:999px;background:var(--v-fundo-alt);font-size:.8rem;
 border:1px solid var(--v-borda)}
.v-tag-x{background:none;border:0;cursor:pointer;color:var(--v-texto-fraco);
 font-size:1rem;line-height:1;padding:0 4px}
.v-tag-entrada{border:0;outline:none;background:transparent;font:inherit;
 color:var(--v-texto);flex:1;min-width:96px;padding:3px}
.v-camera-tela{width:100%;max-width:420px;border-radius:var(--v-raio);
 background:#000;display:block;margin-bottom:8px;aspect-ratio:4/3}
.v-camera-acoes{display:flex;gap:8px}

.v-indicadores{display:grid;gap:12px;margin:14px 0;
 grid-template-columns:repeat(auto-fit,minmax(min(190px,100%),1fr))}
.v-indicador{position:relative;display:flex;flex-direction:column;gap:3px;
 padding:14px 16px;background:var(--v-superficie);
 border:1px solid var(--v-borda);border-radius:var(--v-raio);overflow:hidden}
.v-ind-cor{border-left:3px solid var(--v-ind,var(--v-primaria))}
.v-ind-topo{display:flex;align-items:center;justify-content:space-between;
 gap:8px}
.v-ind-rotulo{font-size:.72rem;font-weight:620;letter-spacing:.07em;
 text-transform:uppercase;color:var(--v-texto-fraco)}
.v-ind-icone{color:var(--v-ind,var(--v-texto-fraco));display:inline-flex}
.v-ind-valor{font-size:1.68rem;font-weight:670;letter-spacing:-.028em;
 font-variant-numeric:tabular-nums;line-height:1.18;
 color:var(--v-ind,var(--v-texto))}
.v-ind-pe{display:flex;align-items:center;gap:8px;flex-wrap:wrap;
 min-height:1.2em}
.v-ind-nota{font-size:.76rem;color:var(--v-texto-fraco)}
.v-ind-meta{margin-top:8px}
.v-ind-meta-txt{font-size:.72rem;color:var(--v-texto-fraco);
 display:block;margin-top:4px}
.v-indicador .v-mini-svg{margin-top:8px;width:100%}

.v-mini{display:inline-flex;align-items:center;gap:7px;vertical-align:middle}
.v-mini-valor{font-size:.82rem;font-variant-numeric:tabular-nums;
 color:var(--v-texto-fraco)}
.v-mini-svg{display:block}

.v-grade-caixa{margin:14px 0}
.v-grade-topo{display:flex;align-items:center;justify-content:space-between;
 gap:12px;margin-bottom:8px;flex-wrap:wrap}
.v-grade-conta{font-size:.78rem;color:var(--v-texto-fraco);
 font-variant-numeric:tabular-nums}
.v-grade-tabela th{padding:0}
.v-col-ordem{font:inherit;font-weight:600;font-size:.8rem;background:none;
 border:0;cursor:pointer;color:var(--v-texto-fraco);padding:9px 13px;
 width:100%;text-align:inherit;display:flex;align-items:center;gap:5px;
 justify-content:inherit}
.v-al-direita{text-align:right}
.v-al-centro{text-align:center}
.v-al-direita .v-col-ordem{justify-content:flex-end}
.v-al-centro .v-col-ordem{justify-content:center}
.v-dens-compacta td{padding:4px 11px;font-size:.84rem}
.v-dens-folgada td{padding:13px 15px}
.v-col-sel,.v-col-num{width:1%;white-space:nowrap;text-align:center}
.v-col-num{color:var(--v-texto-fraco);font-size:.8rem;
 font-variant-numeric:tabular-nums}
.v-cel-barra{height:6px;border-radius:3px;background:var(--v-borda);
 overflow:hidden;min-width:56px;display:inline-block;width:100%;
 vertical-align:middle}
.v-cel-barra-int{height:100%;background:var(--v-primaria)}
.v-cel-barra-txt{font-size:.76rem;color:var(--v-texto-fraco);
 margin-left:6px;font-variant-numeric:tabular-nums}
.v-cel-img{width:30px;height:30px;object-fit:cover;border-radius:5px;
 display:block}
.v-cel-logico{color:var(--v-sucesso);font-weight:700}
.v-cel-sucesso{color:var(--v-sucesso);font-weight:580}
.v-cel-erro{color:var(--v-erro);font-weight:580}
.v-cel-aviso{color:var(--v-aviso);font-weight:580}
.v-cel-info{color:var(--v-info);font-weight:580}
.v-grade-tabela tfoot td{padding:9px 13px;font-weight:650;
 border-top:2px solid var(--v-borda);background:var(--v-fundo-alt);
 font-variant-numeric:tabular-nums}
.v-paginacao{display:flex;align-items:center;gap:4px;margin-top:9px;
 flex-wrap:wrap}
.v-pag-item{font:inherit;font-size:.83rem;min-width:30px;padding:4px 8px;
 border-radius:6px;border:1px solid var(--v-borda);cursor:pointer;
 background:var(--v-superficie);color:var(--v-texto-fraco)}
.v-pag-on{background:var(--v-primaria);color:var(--v-primaria-texto);
 border-color:var(--v-primaria);font-weight:620}
.v-pag-off{opacity:.4;padding:4px 8px;font-size:.83rem}
.v-pag-de{font-size:.78rem;color:var(--v-texto-fraco);margin-left:6px}
.v-editor .v-cel-campo{width:100%;font:inherit;font-size:.86rem;border:0;
 background:transparent;color:var(--v-texto);padding:6px 11px;outline:none}
.v-editor .v-cel-campo:focus{background:color-mix(in srgb,
 var(--v-primaria) 12%,transparent);border-radius:4px}
.v-editor td{padding:0}
.v-linha-x{background:none;border:0;cursor:pointer;font-size:1.05rem;
 color:var(--v-texto-fraco);padding:2px 8px}
.v-linha-x:hover{color:var(--v-erro)}
.v-editor-add{margin-top:9px;font-size:.85rem}

.v-malha{display:grid;margin:14px 0;align-items:start}
.v-painel{background:var(--v-superficie);border:1px solid var(--v-borda);
 border-radius:var(--v-raio);padding:15px 17px;margin:0 0 12px;
 display:flex;flex-direction:column;min-width:0}
.v-malha>.v-painel{margin:0}
.v-painel-cor{border-top:2px solid var(--v-painel,var(--v-primaria))}
.v-painel-compacto{padding:11px 13px}
.v-painel-topo{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;
 margin-bottom:11px}
.v-painel-icone{color:var(--v-painel,var(--v-texto-fraco));
 display:inline-flex;align-self:center}
.v-painel-titulo{font-size:.71rem;font-weight:700;letter-spacing:.09em;
 text-transform:uppercase;color:var(--v-texto-fraco)}
.v-painel-sub{font-size:.73rem;color:var(--v-texto-fraco);opacity:.8}
.v-painel-int{flex:1;min-width:0}
.v-painel-int>*:first-child{margin-top:0}
.v-painel-int>.v-grafico,.v-painel-int>.v-indicador{border:0;padding:0;
 background:none;margin:0}

.v-barra-superior{display:flex;align-items:center;gap:16px;flex-wrap:wrap;
 padding:10px 0 12px;margin-bottom:16px;
 border-bottom:1px solid var(--v-borda);position:sticky;top:0;
 background:var(--v-fundo);z-index:20}
.v-topo-logo{height:26px;width:auto}
.v-topo-marca{font-weight:660;letter-spacing:-.012em;display:flex;
 flex-direction:column;line-height:1.2}
.v-topo-sub{font-size:.7rem;font-weight:500;color:var(--v-texto-fraco);
 letter-spacing:.06em;text-transform:uppercase}
.v-topo-nav{display:flex;gap:2px;flex-wrap:wrap;overflow-x:auto}
.v-topo-item{display:inline-flex;align-items:center;gap:6px;padding:6px 13px;
 border-radius:999px;font-size:.87rem;font-weight:540;text-decoration:none;
 color:var(--v-texto-fraco);white-space:nowrap}
.v-topo-item:hover{background:var(--v-fundo-alt);color:var(--v-texto)}
.v-topo-on{background:var(--v-primaria);color:var(--v-primaria-texto)}
.v-topo-acoes{margin-left:auto;display:flex;gap:10px;align-items:center;
 flex-wrap:wrap}
.v-topo-acoes .v-campo{margin:0}
.v-topo-acoes .v-rotulo{font-size:.72rem;margin-bottom:2px}

.v-dialogo-fundo{position:fixed;inset:0;background:rgba(6,8,12,.55);
 z-index:130;animation:v-aparecer .16s ease}
.v-dialogo{position:fixed;z-index:131;left:50%;top:50%;
 transform:translate(-50%,-50%);width:calc(100% - 32px);
 background:var(--v-superficie);border:1px solid var(--v-borda);
 border-radius:calc(var(--v-raio) * 1.5);box-shadow:0 22px 60px rgba(0,0,0,.4);
 max-height:86vh;display:flex;flex-direction:column;
 animation:v-subir-pouco .18s ease}
.v-dialogo-topo{display:flex;align-items:center;justify-content:space-between;
 gap:12px;padding:15px 19px;border-bottom:1px solid var(--v-borda)}
.v-dialogo-titulo{font-weight:650;letter-spacing:-.012em}
.v-dialogo-x{background:none;border:0;cursor:pointer;font-size:1.4rem;
 line-height:1;color:var(--v-texto-fraco);padding:0 4px}
.v-dialogo-int{padding:16px 19px 20px;overflow:auto}
@keyframes v-aparecer{from{opacity:0}}
@keyframes v-subir-pouco{from{opacity:0;transform:translate(-50%,-46%)}}

.v-popover{display:inline-block;position:relative;margin:6px 0}
.v-popover>summary{list-style:none;display:inline-flex}
.v-popover>summary::-webkit-details-marker{display:none}
.v-popover-int{position:absolute;z-index:60;top:calc(100% + 6px);left:0;
 max-width:calc(100vw - 32px);background:var(--v-superficie);
 border:1px solid var(--v-borda);border-radius:var(--v-raio);
 box-shadow:0 12px 34px rgba(0,0,0,.24);padding:13px 15px}

.v-passos{display:flex;list-style:none;padding:0;margin:16px 0;gap:6px;
 flex-wrap:wrap;counter-reset:passo}
.v-passo{display:flex;align-items:center;gap:8px;flex:1;min-width:130px;
 font-size:.85rem;color:var(--v-texto-fraco)}
.v-passo-bola{width:24px;height:24px;border-radius:50%;flex:0 0 auto;
 display:flex;align-items:center;justify-content:center;font-size:.76rem;
 font-weight:650;border:1px solid var(--v-borda);
 background:var(--v-superficie)}
.v-passo-feito .v-passo-bola{background:var(--v-sucesso);color:#fff;
 border-color:var(--v-sucesso)}
.v-passo-agora .v-passo-bola{background:var(--v-primaria);
 color:var(--v-primaria-texto);border-color:var(--v-primaria)}
.v-passo-agora{color:var(--v-texto);font-weight:600}
.v-passo:not(:last-child)::after{content:"";flex:1;height:1px;
 background:var(--v-borda)}
.v-separador{display:flex;align-items:center;gap:12px;margin:22px 0;
 color:var(--v-texto-fraco)}
.v-separador::before,.v-separador::after{content:"";flex:1;height:1px;
 background:var(--v-borda)}
.v-separador-txt{font-size:.74rem;font-weight:620;letter-spacing:.08em;
 text-transform:uppercase;display:inline-flex;align-items:center;gap:6px}

.v-fragmento{display:block}
.v-fragmento[data-v-atualizando]{opacity:.55;transition:opacity .15s}

.v-leg-direita{display:grid;gap:14px;align-items:center;
 grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)}
.v-leg-direita .v-grafico-titulo{grid-column:1/-1}
.v-leg-direita .v-legenda{flex-direction:column;margin-top:0;
 align-items:flex-start}
.v-leg-valor{margin-left:6px;color:var(--v-texto);
 font-variant-numeric:tabular-nums}
.v-legenda-cat{display:grid;gap:3px 14px;
 grid-template-columns:repeat(auto-fit,minmax(min(190px,100%),1fr))}
.v-legenda-cat .v-legenda-item{display:grid;align-items:center;gap:7px;
 grid-template-columns:10px 1fr auto auto}
.v-leg-nome{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.v-leg-pct{font-style:normal;opacity:.7;font-variant-numeric:tabular-nums;
 min-width:3.4em;text-align:right}
.v-centro-valor{fill:var(--v-texto);font-size:var(--v-fs-centro,21px);
 font-weight:680;font-family:var(--v-fonte)}
.v-centro-rotulo{fill:var(--v-texto-fraco);font-size:var(--v-fs,11px);
 font-family:var(--v-fonte);letter-spacing:.06em;text-transform:uppercase}
.v-eixo-dir{fill:var(--v-texto-fraco);opacity:.85}
.v-leg-num,.v-tm-num,.v-bala-num{font-variant-numeric:tabular-nums}
.v-funil-sub{opacity:.75;font-size:10px}
.v-ponto{transition:r .12s}
.v-grafico:hover .v-ponto{r:4}

@media (max-width:860px){
 .v-galeria{--v-gal:2}
 .v-indicadores{grid-template-columns:repeat(auto-fit,minmax(min(150px,100%),1fr))
  !important}
 .v-barra-superior{position:static}
 .v-topo-acoes{margin-left:0;width:100%}
 .v-leg-direita{grid-template-columns:1fr}
 .v-paginacao{justify-content:center}
 .v-passo{min-width:100%}
 .v-passo:not(:last-child)::after{display:none}
}
@media print{
 .v-toast,.v-comemorar,.v-paginacao,.v-dialogo-fundo{display:none}
 .v-painel,.v-indicador{break-inside:avoid}
}
"""

R.EXTRA_CSS.append(_CSS)


# ═══════════════════════════════════════════════════════════
#  Cliente
# ═══════════════════════════════════════════════════════════
#
# Continua sendo JavaScript escrito à mão, sem build e sem dependência.
# O que cada bloco faz está dito antes dele — este arquivo é lido por
# quem procura por que um clique não chegou ao servidor.

_JS = r"""
(function(){
// Pílula, segmento e nota mandam o valor pelo mapa de campos avulsos,
// que é o mesmo caminho que a aba já usava.
document.addEventListener('click',function(ev){
  var p=ev.target.closest('[data-v-pilula]');
  if(p){
    var k=p.dataset.vPilula,v=p.dataset.vValor;
    if(p.dataset.vVarios){
      var atuais=[];
      p.parentNode.querySelectorAll('[data-v-pilula]').forEach(function(o){
        if(o.classList.contains('v-pilula-on')!==(o===p))atuais.push(o.dataset.vValor);
      });
      Vitrine.campo(k,atuais);
    }else Vitrine.campo(k,v);
    Vitrine.enviar('');return;
  }
  var n=ev.target.closest('[data-v-nota]');
  if(n){Vitrine.campo(n.dataset.vNota,Number(n.dataset.vValor));
    Vitrine.enviar('');return;}
  var o=ev.target.closest('[data-v-ordenar-col]');
  if(o){
    var chave=o.dataset.vOrdenarCol,coluna=o.dataset.vValor;
    var th=o.closest('th'),ja=th&&th.querySelector('.v-seta');
    Vitrine.campo(chave+':ordem',coluna);
    Vitrine.campo(chave+':desc',ja?!(ja.textContent==='▼'):false);
    Vitrine.campo(chave+':pagina',1);
    Vitrine.enviar('');return;
  }
  var pg=ev.target.closest('[data-v-pagina]');
  if(pg){Vitrine.campo(pg.dataset.vPagina+':pagina',Number(pg.dataset.vValor));
    Vitrine.enviar('');return;}
  var rm=ev.target.closest('[data-v-tag-rm]');
  if(rm){
    var alvo=document.querySelector('[data-v-tag-valor="'+rm.dataset.vTagRm+'"]');
    if(alvo){
      var lista=alvo.value?alvo.value.split(','):[];
      alvo.value=lista.filter(function(t){return t!==rm.dataset.vValor}).join(',');
      Vitrine.campo(rm.dataset.vTagRm,alvo.value);
    }
    Vitrine.enviar('');return;
  }
});

// A busca da grade reexecuta o programa: filtrar no servidor é o que
// faz o filtro valer para as cem mil linhas, e não só para as 25 que
// estão na tela.
document.addEventListener('input',function(ev){
  var el=ev.target;
  if(el.dataset&&el.dataset.vCampo&&/:busca$/.test(el.dataset.vCampo)){
    var chave=el.dataset.vCampo.replace(/:busca$/,'');
    Vitrine.campo(chave+':pagina',1);
  }
});

// A etiqueta entra com Enter ou vírgula. O valor viaja num campo
// escondido, separado por vírgula: é o menor contrato possível com o
// servidor, e sobrevive a um recarregamento.
document.addEventListener('keydown',function(ev){
  var t=ev.target.closest('[data-v-tag]');
  if(!t)return;
  if(ev.key!=='Enter'&&ev.key!==','){
    if(ev.key==='Backspace'&&t.value==='')  {
      var campo=document.querySelector('[data-v-tag-valor="'+t.dataset.vTag+'"]');
      if(campo&&campo.value){
        var l=campo.value.split(',');l.pop();campo.value=l.join(',');
        Vitrine.campo(t.dataset.vTag,campo.value);Vitrine.enviar('');
      }
    }
    return;
  }
  ev.preventDefault();
  var texto=t.value.trim();if(!texto)return;
  var alvo=document.querySelector('[data-v-tag-valor="'+t.dataset.vTag+'"]');
  var atual=alvo&&alvo.value?alvo.value.split(','):[];
  if(atual.indexOf(texto)<0)atual.push(texto);
  if(alvo)alvo.value=atual.join(',');
  t.value='';
  Vitrine.campo(t.dataset.vTag,atual.join(','));
  Vitrine.enviar('');
});

// O eco da faixa muda enquanto se arrasta, antes de o servidor
// responder: sem isso o número fica parado e parece travado.
document.addEventListener('input',function(ev){
  var el=ev.target.closest('[data-v-parte]');
  if(!el)return;
  var eco=document.querySelector('[data-v-faixa-eco="'+el.dataset.vCampo+'"]');
  if(!eco)return;
  var pares=document.querySelectorAll('[data-v-campo="'+el.dataset.vCampo+'"]');
  if(pares.length===2)eco.textContent=Math.min(pares[0].value,pares[1].value)+
    ' – '+Math.max(pares[0].value,pares[1].value);
});

// A caixa de conversa manda com Enter e esvazia na hora: o texto já
// foi para o servidor, e deixá-lo ali o reenviaria no próximo clique.
document.addEventListener('keydown',function(ev){
  var c=ev.target.closest('[data-v-enviar-chat]');
  if(!c||ev.key!=='Enter'||ev.shiftKey)return;
  ev.preventDefault();
  if(!c.value.trim())return;
  Vitrine.campo(c.dataset.vEnviarChat,c.value);
  Vitrine.enviar(c.dataset.vEnviarChat);
  c.value='';
});
document.addEventListener('click',function(ev){
  var b=ev.target.closest('[data-v-evento]');
  if(!b)return;
  var caixa=document.querySelector('[data-v-enviar-chat="'+b.dataset.vEvento+'"]');
  if(caixa){Vitrine.campo(b.dataset.vEvento,caixa.value);caixa.value='';}
});

// A câmera precisa de permissão E de HTTPS. Quando falta um dos dois o
// navegador recusa sem explicar, e um retângulo preto não diz nada —
// daí a mensagem abaixo do vídeo.
document.addEventListener('click',function(ev){
  var caixa=ev.target.closest('[data-v-camera]');
  if(!caixa)return;
  var video=caixa.querySelector('video'),tela=caixa.querySelector('canvas'),
      tirar=caixa.querySelector('[data-v-camera-tirar]'),
      aviso=caixa.querySelector('.v-camera-aviso');
  if(ev.target.closest('[data-v-camera-abrir]')){
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){
      aviso.hidden=false;
      aviso.textContent='A câmera exige HTTPS (ou localhost) e permissão do navegador.';
      return;
    }
    navigator.mediaDevices.getUserMedia({video:true}).then(function(fluxo){
      video.srcObject=fluxo;tirar.hidden=false;aviso.hidden=true;
    }).catch(function(e){
      aviso.hidden=false;
      aviso.textContent='A câmera não abriu: '+e.name+
        '. Confira a permissão do navegador e se a página está em HTTPS.';
    });
    return;
  }
  if(ev.target.closest('[data-v-camera-tirar]')){
    tela.width=video.videoWidth||640;tela.height=video.videoHeight||480;
    tela.getContext('2d').drawImage(video,0,0,tela.width,tela.height);
    var url=tela.toDataURL('image/png');
    Vitrine.enviar('',{arquivo:caixa.dataset.vCamera,arquivos:[
      {nome:'foto.png',tamanho:url.length,tipo:'image/png',
       conteudo:url.split(',')[1]}]});
  }
});

// Um fragmento com prazo próprio se atualiza sozinho, sem levar a
// página inteira junto.
setInterval(function(){
  if(document.hidden)return;
  document.querySelectorAll('[data-v-frag-seg]').forEach(function(el){
    var seg=Number(el.dataset.vFragSeg)||0;if(!seg)return;
    var agora=Date.now(),ultimo=Number(el.dataset.vFragEm||0);
    if(agora-ultimo<seg*1000)return;
    el.dataset.vFragEm=agora;
    Vitrine.enviar('',null,el.dataset.vFrag);
  });
},1000);
})();
"""

R.EXTRA_JS.append(_JS)
