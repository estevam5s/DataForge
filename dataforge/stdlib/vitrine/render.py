"""O renderizador — a árvore vira HTML.

Por que HTML no servidor
------------------------
A árvore é montada aqui e chega pronta ao navegador. O JavaScript que
acompanha a página faz **uma** coisa: mandar de volta o que o usuário
fez e trocar o miolo pelo HTML novo. São ~4 KB, escritos à mão, sem
build e sem dependência.

A alternativa — mandar JSON e montar no cliente — exigiria um
framework de UI, uma etapa de build e um `node_modules`, num projeto
cuja regra é não ter dependência nenhuma. E tornaria a página inútil
sem JavaScript, o que aqui ela não é: o conteúdo já vem escrito.

Escapar é a regra, não a exceção
--------------------------------
Todo texto passa por `_e()`. O único lugar que insere HTML cru é o
`V.html(…)`, e ele avisa disso na própria documentação.
"""

import html as _html
import json
import math

from . import tema as _tema


def _e(valor):
    """Texto seguro para ir ao HTML."""
    if valor is None:
        return ""
    return _html.escape(str(valor), quote=True)


def _a(valor):
    """Texto seguro para ir dentro de um atributo."""
    return _html.escape(str(valor or ""), quote=True)


# ═══════════════════════════════════════════════════════════
#  A página inteira
# ═══════════════════════════════════════════════════════════

def pagina(ctx, config):
    """O documento completo — só no primeiro carregamento."""
    claro, escuro = _tema.resolver(config.get("tema"))
    titulo = _a(config.get("titulo", "Vitrine"))
    icone = config.get("icone", "")
    modo = config.get("modo_tema", "automatico")

    cabeca = [
        '<!DOCTYPE html><html lang="%s"><head>' % _a(config.get("idioma", "pt-BR")),
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>{titulo}</title>',
    ]
    if config.get("descricao"):
        cabeca.append(f'<meta name="description" content="{_a(config["descricao"])}">')
    if icone:
        cabeca.append(
            '<link rel="icon" href="data:image/svg+xml,'
            "<svg xmlns=%%22http://www.w3.org/2000/svg%%22 viewBox=%%220 0 100 100%%22>"
            "<text y=%%22.9em%%22 font-size=%%2290%%22>%s</text></svg>\">"
            % _a(icone))
    if config.get("manifesto"):
        cabeca.append('<link rel="manifest" href="/__vitrine__/manifesto.json">')

    cabeca.append(f"<style>{estilo(claro, escuro, modo)}</style>")
    if config.get("css"):
        cabeca.append(f"<style>{config['css']}</style>")
    cabeca.append("</head>")

    classe = "v-app" + (" v-com-lateral" if ctx.barra_lateral.filhos else "")
    corpo = [
        f'<body class="{classe}" data-tema="{_a(modo)}">',
        corpo_html(ctx, config),
        f"<script>{script(config)}</script>",
    ]
    if config.get("javascript"):
        corpo.append(f"<script>{config['javascript']}</script>")
    corpo.append("</body></html>")
    return "".join(cabeca) + "".join(corpo)


def corpo_html(ctx, config):
    """Só o miolo — é isto que troca a cada interação."""
    partes = ['<div id="v-raiz">']

    if ctx.barra_lateral.filhos:
        partes.append('<aside class="v-lateral"><div class="v-lateral-int">')
        partes.append(_filhos(ctx.barra_lateral))
        partes.append("</div></aside>")

    partes.append('<main class="v-main"><div class="v-largura">')
    if config.get("cabecalho"):
        partes.append(
            f'<header class="v-topo"><span class="v-marca">'
            f'{_e(config.get("titulo", ""))}</span></header>')
    partes.append(_filhos(ctx.raiz))
    for falha in ctx.falhas:
        partes.append(_falha(falha))
    partes.append("</div></main></div>")
    return "".join(partes)


def _filhos(no):
    return "".join(desenhar(f) for f in no.filhos)


def _falha(info):
    """Um erro do programa, mostrado na página.

    O detalhe só aparece em desenvolvimento. Em produção, mostrar o
    stack trace é entregar o caminho dos arquivos e o nome das funções
    a quem quiser atacar — e não ajuda em nada quem está usando o app.
    """
    detalhe = ""
    if info.get("detalhe"):
        detalhe = (f'<pre class="v-falha-detalhe">{_e(info["detalhe"])}</pre>')
    return (f'<div class="v-alerta v-erro"><strong>{_e(info["mensagem"])}'
            f"</strong>{detalhe}</div>")


# ═══════════════════════════════════════════════════════════
#  Um componente
# ═══════════════════════════════════════════════════════════

def desenhar(no):
    funcao = _DESENHO.get(no.tipo)
    if funcao is None:
        # Um tipo desconhecido vira um aviso visível em vez de sumir: um
        # componente que não aparece e não reclama é o pior dos dois.
        return (f'<div class="v-alerta v-aviso">componente desconhecido: '
                f'<code>{_e(no.tipo)}</code></div>')
    return funcao(no)


def _d_texto(no):
    return f'<p class="v-texto">{_e(no.props["conteudo"])}</p>'


def _d_titulo(no):
    icone = no.props.get("icone") or ""
    marca = f'<span class="v-icone">{_e(icone)}</span> ' if icone else ""
    return f'<h1 class="v-titulo">{marca}{_e(no.props["conteudo"])}</h1>'


def _d_subtitulo(no):
    return f'<h2 class="v-subtitulo">{_e(no.props["conteudo"])}</h2>'


def _d_cabecalho(no):
    n = no.props.get("nivel", 3)
    return f'<h{n} class="v-cabecalho">{_e(no.props["conteudo"])}</h{n}>'


def _d_markdown(no):
    return f'<div class="v-md">{markdown(no.props["conteudo"])}</div>'


def _d_codigo(no):
    ling = _a(no.props.get("linguagem", ""))
    return (f'<pre class="v-codigo" data-ling="{ling}"><code>'
            f'{_e(no.props["conteudo"])}</code></pre>')


def _d_html(no):
    # O único lugar sem escape. Ver a docstring de 'V.html'.
    return f'<div class="v-html">{no.props["conteudo"]}</div>'


def _d_divisor(_no):
    return '<hr class="v-divisor">'


def _d_espaco(no):
    return f'<div style="height:{int(no.props.get("altura", 16))}px"></div>'


def _d_botao(no):
    p = no.props
    largura = ' style="width:100%"' if p.get("largura") == "cheia" else ""
    return (f'<button type="button" class="v-botao v-{_a(p.get("variante", "primario"))}"'
            f' data-v-evento="{_a(p["chave"])}"{largura}>{_e(p["rotulo"])}</button>')


def _d_enviar(no):
    p = no.props
    return (f'<button type="button" class="v-botao v-{_a(p.get("variante", "primario"))}'
            f' v-enviar" data-v-enviar="{_a(p["chave"])}">{_e(p["rotulo"])}</button>')


def _rotulo(p, para=""):
    if not p.get("rotulo"):
        return ""
    atributo = f' for="{_a(para)}"' if para else ""
    return f'<label class="v-rotulo"{atributo}>{_e(p["rotulo"])}</label>'


def _d_entrada(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    tipos = {"texto": "text", "senha": "password", "email": "email",
             "numero": "number", "telefone": "tel", "busca": "search",
             "url": "url"}
    return (f'<div class="v-campo">{_rotulo(p, ident)}'
            f'<input id="{ident}" class="v-entrada" '
            f'type="{tipos.get(p.get("tipo"), "text")}" '
            f'value="{_a(p["valor"])}" placeholder="{_a(p.get("dica", ""))}" '
            f'data-v-campo="{_a(p["chave"])}"></div>')


def _d_area(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    return (f'<div class="v-campo">{_rotulo(p, ident)}'
            f'<textarea id="{ident}" class="v-entrada v-area" '
            f'rows="{int(p.get("linhas", 4))}" placeholder="{_a(p.get("dica", ""))}" '
            f'data-v-campo="{_a(p["chave"])}">{_e(p["valor"])}</textarea></div>')


def _d_numero(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    limites = ""
    if p.get("minimo") is not None:
        limites += f' min="{_a(p["minimo"])}"'
    if p.get("maximo") is not None:
        limites += f' max="{_a(p["maximo"])}"'
    return (f'<div class="v-campo">{_rotulo(p, ident)}'
            f'<input id="{ident}" class="v-entrada" type="number" '
            f'value="{_a(p["valor"])}" step="{_a(p.get("passo", 1))}"{limites} '
            f'data-v-campo="{_a(p["chave"])}" data-v-numero="1"></div>')


def _d_deslizante(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    return (f'<div class="v-campo v-desl">'
            f'<label class="v-rotulo" for="{ident}">{_e(p["rotulo"])}'
            f'<span class="v-desl-valor">{_e(p["valor"])}</span></label>'
            f'<input id="{ident}" class="v-slider" type="range" '
            f'min="{_a(p["minimo"])}" max="{_a(p["maximo"])}" '
            f'step="{_a(p.get("passo", 1))}" value="{_a(p["valor"])}" '
            f'data-v-campo="{_a(p["chave"])}" data-v-numero="1" '
            f'data-v-adiar="1"></div>')


def _d_caixa(no):
    p = no.props
    marcado = " checked" if p["valor"] else ""
    return (f'<label class="v-caixa"><input type="checkbox"{marcado} '
            f'data-v-campo="{_a(p["chave"])}" data-v-bool="1">'
            f'<span>{_e(p["rotulo"])}</span></label>')


def _d_interruptor(no):
    p = no.props
    marcado = " checked" if p["valor"] else ""
    return (f'<label class="v-interruptor"><input type="checkbox"{marcado} '
            f'data-v-campo="{_a(p["chave"])}" data-v-bool="1">'
            f'<span class="v-trilho"></span><span>{_e(p["rotulo"])}</span></label>')


def _d_opcao(no):
    p = no.props
    itens = "".join(
        f'<label class="v-radio"><input type="radio" '
        f'name="{_a(p["chave"])}" value="{_a(o)}"'
        f'{" checked" if o == p["valor"] else ""} '
        f'data-v-campo="{_a(p["chave"])}"><span>{_e(o)}</span></label>'
        for o in p["opcoes"])
    return f'<div class="v-campo">{_rotulo(p)}<div class="v-radios">{itens}</div></div>'


def _d_escolha(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    itens = "".join(
        f'<option value="{_a(o)}"{" selected" if o == p["valor"] else ""}>'
        f"{_e(o)}</option>" for o in p["opcoes"])
    return (f'<div class="v-campo">{_rotulo(p, ident)}'
            f'<select id="{ident}" class="v-entrada" '
            f'data-v-campo="{_a(p["chave"])}">{itens}</select></div>')


def _d_escolhas(no):
    p = no.props
    escolhidos = set(p["valor"])
    itens = "".join(
        f'<label class="v-caixa"><input type="checkbox" value="{_a(o)}"'
        f'{" checked" if o in escolhidos else ""} '
        f'data-v-campo="{_a(p["chave"])}" data-v-varios="1">'
        f'<span>{_e(o)}</span></label>' for o in p["opcoes"])
    return (f'<div class="v-campo">{_rotulo(p)}'
            f'<div class="v-caixas">{itens}</div></div>')


def _d_data(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    return (f'<div class="v-campo">{_rotulo(p, ident)}'
            f'<input id="{ident}" class="v-entrada" type="date" '
            f'value="{_a(p["valor"])}" data-v-campo="{_a(p["chave"])}"></div>')


def _d_cor(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    return (f'<div class="v-campo">{_rotulo(p, ident)}'
            f'<input id="{ident}" class="v-cor" type="color" '
            f'value="{_a(p["valor"])}" data-v-campo="{_a(p["chave"])}"></div>')


def _d_arquivo(no):
    p = no.props
    ident = f'v-{_a(p["chave"])}'
    aceita = (f' accept="{_a(",".join(p["tipos"]))}"' if p.get("tipos") else "")
    varios = " multiple" if p.get("varios") else ""
    return (f'<div class="v-campo v-arquivo">{_rotulo(p, ident)}'
            f'<input id="{ident}" type="file"{aceita}{varios} '
            f'data-v-arquivo="{_a(p["chave"])}"></div>')


def _d_tabela(no, rolagem=False):
    p = no.props
    cabeca = "".join(f"<th>{_e(c)}</th>" for c in p["colunas"])
    corpo = "".join(
        "<tr>" + "".join(f"<td>{_e(v)}</td>" for v in linha) + "</tr>"
        for linha in p["linhas"])
    altura = f' style="max-height:{int(p["altura"])}px"' if p.get("altura") else ""
    classe = "v-tabela-caixa" + (" v-rolagem" if rolagem else "")
    vazio = ('<tbody><tr><td class="v-vazio" colspan="99">sem dados</td></tr></tbody>'
             if not p["linhas"] else f"<tbody>{corpo}</tbody>")
    return (f'<div class="{classe}"{altura}><table class="v-tabela">'
            f"<thead><tr>{cabeca}</tr></thead>{vazio}</table></div>")


def _d_frame(no):
    p = no.props
    cabeca = "".join(
        f'<th data-v-ordenar="{i}">{_e(c)}<span class="v-seta"></span></th>'
        for i, c in enumerate(p["colunas"]))
    corpo = "".join(
        "<tr>" + "".join(f"<td>{_e(v)}</td>" for v in linha) + "</tr>"
        for linha in p["linhas"])
    altura = f'max-height:{int(p["altura"])}px' if p.get("altura") else ""
    return (f'<div class="v-frame">'
            f'<input class="v-entrada v-busca" placeholder="filtrar…" '
            f'data-v-filtrar="1">'
            f'<div class="v-tabela-caixa v-rolagem" style="{altura}">'
            f'<table class="v-tabela v-ordenavel">'
            f"<thead><tr>{cabeca}</tr></thead><tbody>{corpo}</tbody>"
            f'</table></div><div class="v-frame-pe">'
            f'{len(p["linhas"])} linha(s) × {len(p["colunas"])} coluna(s)'
            f"</div></div>")


def _d_metrica(no):
    p = no.props
    variacao = ""
    if p.get("variacao") is not None:
        try:
            n = float(p["variacao"])
        except (TypeError, ValueError):
            n = 0.0
        classe = "v-sobe" if n > 0 else ("v-desce" if n < 0 else "v-igual")
        seta = "▲" if n > 0 else ("▼" if n < 0 else "—")
        numero = f"{abs(n):g}"
        variacao = (f'<span class="v-variacao {classe}">{seta} {_e(numero)}%'
                    f"</span>")
    ajuda = (f'<span class="v-ajuda" title="{_a(p["ajuda"])}">?</span>'
             if p.get("ajuda") else "")
    return (f'<div class="v-metrica"><span class="v-metrica-rotulo">'
            f'{_e(p["rotulo"])}{ajuda}</span>'
            f'<span class="v-metrica-valor">{_e(p["valor"])}</span>'
            f"{variacao}</div>")


def _d_json(no):
    texto = json.dumps(_serializavel(no.props["dados"]), ensure_ascii=False,
                       indent=2, default=str)
    aberto = " open" if no.props.get("expandido", True) else ""
    return (f'<details class="v-json"{aberto}><summary>JSON</summary>'
            f"<pre><code>{_e(texto)}</code></pre></details>")


def _d_vault(no):
    dados = no.props["dados"]
    if not isinstance(dados, dict):
        return _d_json(no)
    itens = "".join(f"<dt>{_e(k)}</dt><dd>{_e(v)}</dd>"
                    for k, v in dados.items())
    return f'<dl class="v-vault">{itens}</dl>'


def _d_alerta(no):
    p = no.props
    icones = {"sucesso": "✓", "erro": "✕", "aviso": "!", "info": "i"}
    nivel = p.get("nivel", "info")
    return (f'<div class="v-alerta v-{_a(nivel)}">'
            f'<span class="v-alerta-icone">{icones.get(nivel, "i")}</span>'
            f'<span>{_e(p["mensagem"])}</span></div>')


def _d_progresso(no):
    p = no.props
    pct = round(p["valor"] * 100, 2)
    rotulo = f'<span class="v-prog-rotulo">{_e(p["rotulo"])}</span>' if p.get("rotulo") else ""
    return (f'<div class="v-prog">{rotulo}<div class="v-prog-trilho" '
            f'role="progressbar" aria-valuenow="{pct}" aria-valuemin="0" '
            f'aria-valuemax="100"><div class="v-prog-barra" '
            f'style="width:{pct}%"></div></div></div>')


def _d_carregando(no):
    return (f'<div class="v-carregando"><span class="v-giro"></span>'
            f'<span>{_e(no.props["mensagem"])}</span></div>')


def _d_imagem(no):
    p = no.props
    largura = f' style="width:{int(p["largura"])}px"' if p.get("largura") else ""
    legenda = (f'<figcaption>{_e(p["legenda"])}</figcaption>'
               if p.get("legenda") else "")
    return (f'<figure class="v-figura"><img src="{_a(p["origem"])}" '
            f'alt="{_a(p.get("legenda", ""))}" loading="lazy"{largura}>'
            f"{legenda}</figure>")


def _d_audio(no):
    p = no.props
    return (f'<audio class="v-audio" controls preload="none">'
            f'<source src="{_a(p["origem"])}" type="{_a(p["formato"])}">'
            f"</audio>")


def _d_video(no):
    p = no.props
    return (f'<video class="v-video" controls preload="metadata">'
            f'<source src="{_a(p["origem"])}" type="{_a(p["formato"])}">'
            f"</video>")


def _d_link(no):
    p = no.props
    alvo = ' target="_blank" rel="noopener noreferrer"' if p.get("nova_aba") else ""
    return f'<a class="v-link" href="{_a(p["destino"])}"{alvo}>{_e(p["rotulo"])}</a>'


def _d_baixar(no):
    p = no.props
    return (f'<a class="v-botao v-secundario" '
            f'href="/__vitrine__/baixar/{_a(p["chave"])}" '
            f'download="{_a(p["nome"])}">{_e(p["rotulo"])}</a>')


# ── Layout ───────────────────────────────────────────────────

def _d_pagina(no):
    return _filhos(no)


def _d_colunas(no):
    esp = {"nenhum": "0", "pequeno": "8px", "medio": "16px", "grande": "28px"}
    lacuna = esp.get(no.props.get("espacamento", "medio"), "16px")
    return (f'<div class="v-colunas" style="gap:{lacuna}">{_filhos(no)}</div>')


def _d_coluna(no):
    return (f'<div class="v-coluna" style="flex:{no.props["proporcao"]} 1 0">'
            f"{_filhos(no)}</div>")


def _d_container(no):
    classe = "v-container" + (" v-borda" if no.props.get("borda") else "")
    altura = (f' style="max-height:{int(no.props["altura"])}px;overflow:auto"'
              if no.props.get("altura") else "")
    return f'<div class="{classe}"{altura}>{_filhos(no)}</div>'


def _d_linha(no):
    esp = {"nenhum": "0", "pequeno": "8px", "medio": "16px", "grande": "28px"}
    lacuna = esp.get(no.props.get("espacamento", "medio"), "16px")
    alinhar = {"inicio": "flex-start", "centro": "center",
               "fim": "flex-end", "entre": "space-between"}
    just = alinhar.get(no.props.get("alinhar", "inicio"), "flex-start")
    return (f'<div class="v-linha" style="gap:{lacuna};justify-content:{just}">'
            f"{_filhos(no)}</div>")


def _d_cartao(no):
    p = no.props
    cabeca = ""
    if p.get("titulo") or p.get("subtitulo"):
        sub = (f'<span class="v-cartao-sub">{_e(p["subtitulo"])}</span>'
               if p.get("subtitulo") else "")
        cabeca = (f'<div class="v-cartao-topo">'
                  f'<span class="v-cartao-titulo">{_e(p["titulo"])}</span>'
                  f"{sub}</div>")
    return f'<section class="v-cartao">{cabeca}{_filhos(no)}</section>'


def _d_expandir(no):
    p = no.props
    aberto = " open" if p.get("aberto") else ""
    return (f'<details class="v-expandir"{aberto} '
            f'data-v-expandir="{_a(p["chave"])}">'
            f'<summary>{_e(p["rotulo"])}</summary>'
            f'<div class="v-expandir-int">{_filhos(no)}</div></details>')


def _d_abas(no):
    p = no.props
    botoes = "".join(
        f'<button type="button" class="v-aba-botao'
        f'{" v-ativa" if r == p["ativa"] else ""}" '
        f'data-v-aba="{_a(p["chave"])}" data-v-valor="{_a(r)}" '
        f'role="tab" aria-selected="{"true" if r == p["ativa"] else "false"}">'
        f"{_e(r)}</button>" for r in p["rotulos"])
    return (f'<div class="v-abas"><div class="v-abas-topo" role="tablist">'
            f"{botoes}</div>{_filhos(no)}</div>")


def _d_aba(no):
    escondido = "" if no.props.get("visivel") else " hidden"
    return (f'<div class="v-aba" role="tabpanel"{escondido}>'
            f"{_filhos(no)}</div>")


def _d_formulario(no):
    return (f'<form class="v-formulario" data-v-form="{_a(no.props["chave"])}" '
            f'onsubmit="return false">{_filhos(no)}</form>')


def _d_vazio(no):
    return f'<div class="v-vazio-area">{_filhos(no)}</div>'


def _d_espacador(_no):
    return '<div style="flex:1"></div>'


# ═══════════════════════════════════════════════════════════
#  Gráfico — SVG escrito aqui
# ═══════════════════════════════════════════════════════════

def _d_grafico(no):
    p = no.props
    series = p.get("series") or []
    categorias = p.get("categorias") or []
    titulo = (f'<div class="v-grafico-titulo">{_e(p["titulo"])}</div>'
              if p.get("titulo") else "")
    if not series or not categorias:
        return (f'<div class="v-grafico">{titulo}'
                f'<div class="v-vazio">sem dados para desenhar</div></div>')

    tipo = p.get("grafico", "linha")
    desenho = _SVG.get(tipo, _svg_linha)(p, series, categorias)
    legenda = ""
    if p.get("legenda") and len(series) > 1:
        cores = p.get("cores") or ["#FED403"]
        legenda = '<div class="v-legenda">' + "".join(
            f'<span class="v-legenda-item">'
            f'<i style="background:{_a(cores[i % len(cores)])}"></i>'
            f'{_e(s["nome"])}</span>' for i, s in enumerate(series)) + "</div>"
    return f'<div class="v-grafico">{titulo}{desenho}{legenda}</div>'


#: A moldura do SVG. As coordenadas são as do desenho, e o CSS estica a
#: largura — é o que torna o gráfico responsivo sem recalcular nada.
_L, _A = 800, 280
_MARGEM = {"cima": 16, "baixo": 34, "esq": 52, "dir": 12}


def _area_util(altura):
    return (_L - _MARGEM["esq"] - _MARGEM["dir"],
            altura - _MARGEM["cima"] - _MARGEM["baixo"])


def _moldura(altura, dentro):
    return (f'<svg class="v-svg" viewBox="0 0 {_L} {altura}" '
            f'preserveAspectRatio="none" role="img">{dentro}</svg>')


def _escala(series, props, empilhado=False):
    """O topo e o piso do eixo Y, arredondados para um número redondo.

    Um eixo que vai até 1 237 não ajuda ninguém a ler o gráfico; até
    1 500, com marcas de 500 em 500, ajuda.
    """
    valores = []
    if empilhado:
        for i in range(len(series[0]["valores"])):
            valores.append(sum(s["valores"][i] for s in series
                               if i < len(s["valores"])))
    else:
        for s in series:
            valores.extend(s["valores"])
    valores = [v for v in valores if isinstance(v, (int, float))] or [0]

    maior = props.get("max_y")
    menor = props.get("min_y")
    maior = float(maior) if maior is not None else max(valores)
    menor = float(menor) if menor is not None else min(min(valores), 0.0)
    if maior == menor:
        maior = menor + 1
    passo = _passo_bonito((maior - menor) / 4)
    topo = math.ceil(maior / passo) * passo
    piso = math.floor(menor / passo) * passo
    return piso, (topo if topo > piso else piso + passo), passo


def _passo_bonito(cru):
    if cru <= 0:
        return 1.0
    potencia = 10 ** math.floor(math.log10(cru))
    for multiplo in (1, 2, 2.5, 5, 10):
        if cru <= multiplo * potencia:
            return multiplo * potencia
    return 10 * potencia


def _grade(piso, topo, passo, altura, mostrar=True):
    largura_util, altura_util = _area_util(altura)
    partes = []
    valor = piso
    while valor <= topo + passo / 2:
        y = _MARGEM["cima"] + altura_util * (1 - (valor - piso) / (topo - piso))
        if mostrar:
            partes.append(
                f'<line class="v-grade" x1="{_MARGEM["esq"]}" y1="{y:.1f}" '
                f'x2="{_L - _MARGEM["dir"]}" y2="{y:.1f}"/>')
        partes.append(
            f'<text class="v-eixo" x="{_MARGEM["esq"] - 8}" y="{y + 4:.1f}" '
            f'text-anchor="end">{_e(_numero_curto(valor))}</text>')
        valor += passo
    return "".join(partes)


def _rotulos_x(categorias, altura):
    largura_util, _ = _area_util(altura)
    n = len(categorias)
    # Com muitas categorias, mostrar todas vira uma mancha preta. Um a
    # cada k continua dizendo onde o eixo começa e termina.
    salto = max(1, math.ceil(n / 12))
    partes = []
    for i, c in enumerate(categorias):
        if i % salto and i != n - 1:
            continue
        x = _MARGEM["esq"] + (largura_util * (i + 0.5) / n if n > 1
                              else largura_util / 2)
        partes.append(
            f'<text class="v-eixo" x="{x:.1f}" y="{altura - 12}" '
            f'text-anchor="middle">{_e(c)}</text>')
    return "".join(partes)


def _y_de(valor, piso, topo, altura):
    _, altura_util = _area_util(altura)
    return _MARGEM["cima"] + altura_util * (1 - (valor - piso) / (topo - piso))


def _svg_linha(props, series, categorias, preencher=False):
    altura = int(props.get("altura", 280))
    largura_util, _ = _area_util(altura)
    piso, topo, passo = _escala(series, props)
    cores = props.get("cores") or ["#FED403"]
    n = len(categorias)
    partes = [_grade(piso, topo, passo, altura, props.get("grade", True))]

    for indice, serie in enumerate(series):
        cor = cores[indice % len(cores)]
        pontos = []
        for i, valor in enumerate(serie["valores"][:n]):
            x = _MARGEM["esq"] + (largura_util * i / (n - 1) if n > 1
                                  else largura_util / 2)
            pontos.append((x, _y_de(valor, piso, topo, altura)))
        if not pontos:
            continue
        caminho = (_curva(pontos) if props.get("suave")
                   else " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                                 for i, (x, y) in enumerate(pontos)))
        if preencher:
            base = _y_de(max(piso, 0), piso, topo, altura)
            partes.append(
                f'<path d="{caminho} L{pontos[-1][0]:.1f},{base:.1f} '
                f'L{pontos[0][0]:.1f},{base:.1f} Z" fill="{_a(cor)}" '
                f'fill-opacity="0.18" stroke="none"/>')
        partes.append(f'<path d="{caminho}" fill="none" stroke="{_a(cor)}" '
                      f'stroke-width="2.5" stroke-linejoin="round" '
                      f'stroke-linecap="round"/>')
        for x, y in pontos:
            partes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" '
                          f'fill="{_a(cor)}"/>')
    partes.append(_rotulos_x(categorias, altura))
    return _moldura(altura, "".join(partes))


def _curva(pontos):
    """Uma curva suave por Catmull-Rom convertida para Bézier.

    A conversão existe porque o SVG não tem Catmull-Rom, e interpolar à
    mão passaria por cima dos pontos — uma curva que não toca o dado que
    representa é um gráfico que mente.
    """
    if len(pontos) < 3:
        return " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                        for i, (x, y) in enumerate(pontos))
    d = [f"M{pontos[0][0]:.1f},{pontos[0][1]:.1f}"]
    for i in range(len(pontos) - 1):
        p0 = pontos[max(0, i - 1)]
        p1, p2 = pontos[i], pontos[i + 1]
        p3 = pontos[min(len(pontos) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} "
                 f"{p2[0]:.1f},{p2[1]:.1f}")
    return " ".join(d)


def _svg_area(props, series, categorias):
    return _svg_linha(props, series, categorias, preencher=True)


def _svg_barras(props, series, categorias):
    altura = int(props.get("altura", 280))
    largura_util, _ = _area_util(altura)
    empilhado = bool(props.get("empilhado"))
    piso, topo, passo = _escala(series, props, empilhado)
    cores = props.get("cores") or ["#FED403"]
    n = len(categorias)
    grupo = largura_util / max(1, n)
    partes = [_grade(piso, topo, passo, altura, props.get("grade", True))]
    base = _y_de(max(piso, 0), piso, topo, altura)

    for i in range(n):
        acumulado = 0.0
        for indice, serie in enumerate(series):
            valor = serie["valores"][i] if i < len(serie["valores"]) else 0
            cor = cores[indice % len(cores)]
            if empilhado:
                y0 = _y_de(acumulado, piso, topo, altura)
                y1 = _y_de(acumulado + valor, piso, topo, altura)
                x = _MARGEM["esq"] + grupo * i + grupo * 0.15
                larg = grupo * 0.7
                acumulado += valor
            else:
                larg = grupo * 0.7 / len(series)
                x = _MARGEM["esq"] + grupo * i + grupo * 0.15 + larg * indice
                y0, y1 = base, _y_de(valor, piso, topo, altura)
            cima, alt = min(y0, y1), abs(y1 - y0)
            partes.append(
                f'<rect x="{x:.1f}" y="{cima:.1f}" width="{larg:.1f}" '
                f'height="{max(alt, 0.5):.1f}" fill="{_a(cor)}" rx="2">'
                f'<title>{_e(categorias[i])}: {_e(_numero_curto(valor))}</title>'
                f"</rect>")
            if props.get("rotulos") and not empilhado:
                partes.append(
                    f'<text class="v-eixo" x="{x + larg / 2:.1f}" '
                    f'y="{cima - 5:.1f}" text-anchor="middle">'
                    f"{_e(_numero_curto(valor))}</text>")
    partes.append(_rotulos_x(categorias, altura))
    return _moldura(altura, "".join(partes))


def _svg_barras_h(props, series, categorias):
    altura = max(int(props.get("altura", 280)), 26 * len(categorias) + 40)
    cores = props.get("cores") or ["#FED403"]
    valores = [s["valores"] for s in series]
    maior = max((max(v) if v else 0) for v in valores) or 1
    esq = 120
    largura_util = _L - esq - 60
    partes = []
    passo_y = (altura - 20) / max(1, len(categorias))
    for i, categoria in enumerate(categorias):
        valor = valores[0][i] if i < len(valores[0]) else 0
        larg = max(1.0, largura_util * (valor / maior))
        y = 10 + passo_y * i + passo_y * 0.2
        partes.append(
            f'<text class="v-eixo" x="{esq - 8}" y="{y + passo_y * 0.42:.1f}" '
            f'text-anchor="end">{_e(categoria)}</text>'
            f'<rect x="{esq}" y="{y:.1f}" width="{larg:.1f}" '
            f'height="{passo_y * 0.6:.1f}" rx="3" fill="{_a(cores[0])}"/>'
            f'<text class="v-eixo" x="{esq + larg + 8:.1f}" '
            f'y="{y + passo_y * 0.42:.1f}">{_e(_numero_curto(valor))}</text>')
    return _moldura(altura, "".join(partes))


def _svg_dispersao(props, series, categorias):
    altura = int(props.get("altura", 280))
    largura_util, _ = _area_util(altura)
    piso, topo, passo = _escala(series, props)
    cores = props.get("cores") or ["#FED403"]
    n = len(categorias)
    partes = [_grade(piso, topo, passo, altura, props.get("grade", True))]
    for indice, serie in enumerate(series):
        cor = cores[indice % len(cores)]
        for i, valor in enumerate(serie["valores"][:n]):
            x = _MARGEM["esq"] + (largura_util * i / (n - 1) if n > 1
                                  else largura_util / 2)
            y = _y_de(valor, piso, topo, altura)
            partes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" '
                          f'fill="{_a(cor)}" fill-opacity="0.75">'
                          f'<title>{_e(categorias[i])}: '
                          f"{_e(_numero_curto(valor))}</title></circle>")
    partes.append(_rotulos_x(categorias, altura))
    return _moldura(altura, "".join(partes))


def _svg_pizza(props, series, categorias, buraco=0.0):
    altura = int(props.get("altura", 280))
    cores = props.get("cores") or ["#FED403"]
    valores = [max(0.0, float(v)) for v in series[0]["valores"]]
    total = sum(valores)
    if total <= 0:
        return _moldura(altura, '<text class="v-eixo" x="400" y="140" '
                                'text-anchor="middle">sem dados</text>')
    cx, cy = 260.0, altura / 2
    raio = min(altura / 2 - 16, 110)
    angulo = -math.pi / 2
    partes = []
    for i, valor in enumerate(valores):
        fatia = 2 * math.pi * (valor / total)
        fim = angulo + fatia
        cor = cores[i % len(cores)]
        if fatia >= 2 * math.pi - 1e-9:
            # Uma fatia única fecha o arco em si mesma e some. Um
            # círculo inteiro é o desenho certo.
            partes.append(f'<circle cx="{cx}" cy="{cy:.1f}" r="{raio:.1f}" '
                          f'fill="{_a(cor)}"/>')
        else:
            partes.append(_fatia(cx, cy, raio, angulo, fim, cor, buraco))
        meio = angulo + fatia / 2
        rotulo_r = raio * (0.62 if not buraco else (0.5 + buraco / 2))
        if valor / total > 0.05:
            partes.append(
                f'<text class="v-fatia" x="{cx + math.cos(meio) * rotulo_r:.1f}" '
                f'y="{cy + math.sin(meio) * rotulo_r + 4:.1f}" '
                f'text-anchor="middle">{valor / total * 100:.0f}%</text>')
        angulo = fim

    for i, categoria in enumerate(categorias):
        y = cy - raio + 14 + i * 22
        if y > altura - 8:
            break
        partes.append(
            f'<rect x="440" y="{y - 10:.1f}" width="12" height="12" rx="2" '
            f'fill="{_a(cores[i % len(cores)])}"/>'
            f'<text class="v-eixo" x="460" y="{y:.1f}">{_e(categoria)} — '
            f"{_e(_numero_curto(valores[i]))}</text>")
    return _moldura(altura, "".join(partes))


def _svg_rosca(props, series, categorias):
    return _svg_pizza(props, series, categorias, buraco=0.55)


def _fatia(cx, cy, raio, inicio, fim, cor, buraco=0.0):
    grande = 1 if (fim - inicio) > math.pi else 0
    x1, y1 = cx + math.cos(inicio) * raio, cy + math.sin(inicio) * raio
    x2, y2 = cx + math.cos(fim) * raio, cy + math.sin(fim) * raio
    if buraco <= 0:
        d = (f"M{cx:.1f},{cy:.1f} L{x1:.1f},{y1:.1f} "
             f"A{raio:.1f},{raio:.1f} 0 {grande} 1 {x2:.1f},{y2:.1f} Z")
    else:
        ri = raio * buraco
        xi1, yi1 = cx + math.cos(fim) * ri, cy + math.sin(fim) * ri
        xi2, yi2 = cx + math.cos(inicio) * ri, cy + math.sin(inicio) * ri
        d = (f"M{x1:.1f},{y1:.1f} A{raio:.1f},{raio:.1f} 0 {grande} 1 "
             f"{x2:.1f},{y2:.1f} L{xi1:.1f},{yi1:.1f} "
             f"A{ri:.1f},{ri:.1f} 0 {grande} 0 {xi2:.1f},{yi2:.1f} Z")
    return f'<path d="{d}" fill="{_a(cor)}"/>'


def _numero_curto(valor):
    """1234567 vira 1,2 M. Um eixo cheio de zeros não se lê."""
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    for limite, sufixo in ((1e9, " B"), (1e6, " M"), (1e3, " k")):
        if abs(n) >= limite:
            reduzido = n / limite
            texto = (f"{reduzido:.1f}".rstrip("0").rstrip(".")
                     .replace(".", ","))
            return texto + sufixo
    if n == int(n):
        return str(int(n))
    return f"{n:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def _serializavel(valor):
    """O que o `json` não conhece vira texto, em vez de derrubar a página."""
    if isinstance(valor, dict):
        return {str(k): _serializavel(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_serializavel(v) for v in valor]
    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor
    if hasattr(valor, "fields"):
        return _serializavel(dict(valor.fields))
    return str(valor)


_SVG = {
    "linha": _svg_linha,
    "area": _svg_area,
    "barras": _svg_barras,
    "barras_horizontais": _svg_barras_h,
    "dispersao": _svg_dispersao,
    "pizza": _svg_pizza,
    "rosca": _svg_rosca,
    "histograma": _svg_barras,
}

_DESENHO = {
    "pagina": _d_pagina, "texto": _d_texto, "titulo": _d_titulo,
    "subtitulo": _d_subtitulo, "cabecalho": _d_cabecalho,
    "markdown": _d_markdown, "codigo": _d_codigo, "html": _d_html,
    "divisor": _d_divisor, "espaco": _d_espaco, "botao": _d_botao,
    "enviar": _d_enviar, "entrada": _d_entrada, "area": _d_area,
    "numero": _d_numero, "deslizante": _d_deslizante, "caixa": _d_caixa,
    "interruptor": _d_interruptor, "opcao": _d_opcao, "escolha": _d_escolha,
    "escolhas": _d_escolhas, "data": _d_data, "cor": _d_cor,
    "arquivo": _d_arquivo, "tabela": _d_tabela, "frame": _d_frame,
    "metrica": _d_metrica, "json": _d_json, "vault": _d_vault,
    "alerta": _d_alerta, "progresso": _d_progresso,
    "carregando": _d_carregando, "imagem": _d_imagem, "audio": _d_audio,
    "video": _d_video, "link": _d_link, "baixar": _d_baixar,
    "colunas": _d_colunas, "coluna": _d_coluna, "container": _d_container,
    "linha_layout": _d_linha, "cartao": _d_cartao, "expandir": _d_expandir,
    "abas": _d_abas, "aba": _d_aba, "formulario": _d_formulario,
    "vazio": _d_vazio, "espacador": _d_espacador, "grafico": _d_grafico,
}
#: 'linha' é o container horizontal; o nome bate com o de uma tabela, e
#: quem desempata é o tipo do nó, não o nome.
_DESENHO["linha"] = _d_linha


# ═══════════════════════════════════════════════════════════
#  Markdown — o suficiente, e nada além
# ═══════════════════════════════════════════════════════════

def markdown(texto):
    """Títulos, listas, tabela simples, ênfase, código, link.

    Deliberadamente pequeno. Um Markdown completo é um projeto do
    tamanho deste módulo, e o que falta aqui tem saída: `V.html` para o
    caso raro, `V.tabela` para tabela de verdade.
    """
    linhas = str(texto).split("\n")
    saida, i = [], 0
    lista_aberta = None

    def fechar():
        nonlocal lista_aberta
        if lista_aberta:
            saida.append(f"</{lista_aberta}>")
            lista_aberta = None

    while i < len(linhas):
        linha = linhas[i]
        crua = linha.strip()

        if crua.startswith("```"):
            fechar()
            i += 1
            bloco = []
            while i < len(linhas) and not linhas[i].strip().startswith("```"):
                bloco.append(linhas[i])
                i += 1
            saida.append(f'<pre class="v-codigo"><code>'
                         f'{_e(chr(10).join(bloco))}</code></pre>')
            i += 1
            continue

        if not crua:
            fechar()
            i += 1
            continue

        if crua.startswith("#"):
            fechar()
            nivel = min(6, len(crua) - len(crua.lstrip("#")))
            saida.append(f"<h{nivel}>{_linha(crua.lstrip('# '))}</h{nivel}>")
        elif crua in ("---", "***", "___"):
            fechar()
            saida.append('<hr class="v-divisor">')
        elif crua.startswith("> "):
            fechar()
            saida.append(f"<blockquote>{_linha(crua[2:])}</blockquote>")
        elif crua[:2] in ("- ", "* ") or crua[:2] == "+ ":
            if lista_aberta != "ul":
                fechar()
                saida.append("<ul>")
                lista_aberta = "ul"
            saida.append(f"<li>{_linha(crua[2:])}</li>")
        elif _numerada(crua):
            if lista_aberta != "ol":
                fechar()
                saida.append("<ol>")
                lista_aberta = "ol"
            saida.append(f"<li>{_linha(crua.split('.', 1)[1].strip())}</li>")
        elif crua.startswith("|") and crua.endswith("|"):
            fechar()
            bloco = []
            while (i < len(linhas) and linhas[i].strip().startswith("|")):
                bloco.append(linhas[i].strip())
                i += 1
            saida.append(_tabela_md(bloco))
            continue
        else:
            fechar()
            saida.append(f"<p>{_linha(crua)}</p>")
        i += 1

    fechar()
    return "".join(saida)


def _numerada(linha):
    cabeca = linha.split(".", 1)[0]
    return cabeca.isdigit() and "." in linha


def _tabela_md(bloco):
    def celulas(linha):
        return [c.strip() for c in linha.strip("|").split("|")]

    if len(bloco) >= 2 and set(bloco[1].replace("|", "").replace(" ", "")) <= set("-:"):
        cabeca, corpo = celulas(bloco[0]), bloco[2:]
    else:
        cabeca, corpo = [], bloco
    th = ("<thead><tr>" + "".join(f"<th>{_linha(c)}</th>" for c in cabeca)
          + "</tr></thead>") if cabeca else ""
    td = "".join("<tr>" + "".join(f"<td>{_linha(c)}</td>" for c in celulas(l))
                 + "</tr>" for l in corpo)
    return (f'<div class="v-tabela-caixa"><table class="v-tabela">'
            f"{th}<tbody>{td}</tbody></table></div>")


def _linha(texto):
    """Ênfase, código e link — **depois** de escapar tudo.

    A ordem é o que importa: escapar primeiro e só então reconhecer a
    marcação impede que um `<script>` escrito no Markdown vire script.
    """
    saida = _e(texto)
    saida = _entre(saida, "`", "<code>", "</code>")
    saida = _entre(saida, "**", "<strong>", "</strong>")
    saida = _entre(saida, "*", "<em>", "</em>")
    saida = _links(saida)
    return saida


def _entre(texto, marca, abre, fecha):
    partes = texto.split(marca)
    if len(partes) < 3:
        return texto
    saida = [partes[0]]
    for i, parte in enumerate(partes[1:], start=1):
        saida.append((abre if i % 2 else fecha) + parte)
    # Um marcador ímpar sobrando deixaria a tag aberta e comeria o resto
    # da página. Nesse caso, o texto volta como estava.
    if len(partes) % 2 == 0:
        return texto
    return "".join(saida)


def _links(texto):
    saida, i = [], 0
    while True:
        abre = texto.find("[", i)
        if abre < 0:
            break
        fecha = texto.find("]", abre)
        par = texto.find("(", fecha) if fecha > 0 else -1
        fim = texto.find(")", par) if par == fecha + 1 else -1
        if fecha < 0 or par != fecha + 1 or fim < 0:
            saida.append(texto[i:abre + 1])
            i = abre + 1
            continue
        rotulo = texto[abre + 1:fecha]
        destino = texto[par + 1:fim]
        if _destino_seguro(destino):
            saida.append(texto[i:abre])
            saida.append(f'<a class="v-link" href="{_a(destino)}">{rotulo}</a>')
        else:
            saida.append(texto[i:fim + 1])
        i = fim + 1
    saida.append(texto[i:])
    return "".join(saida)


def _destino_seguro(destino):
    """`javascript:` num link é XSS com outra roupa."""
    limpo = destino.strip().lower().replace("\t", "").replace("\n", "")
    return not limpo.startswith(("javascript:", "vbscript:", "data:text/html"))


# ═══════════════════════════════════════════════════════════
#  CSS e JavaScript
# ═══════════════════════════════════════════════════════════

def estilo(claro, escuro, modo="automatico"):
    variaveis_claro = _tema.variaveis(claro)
    variaveis_escuro = _tema.variaveis(escuro)
    regras = [f":root{{{variaveis_claro}}}"]
    if modo == "escuro":
        regras = [f":root{{{variaveis_escuro}}}"]
    elif modo == "automatico":
        regras.append(f"@media (prefers-color-scheme:dark){{"
                      f':root:not([data-tema="claro"]){{{variaveis_escuro}}}}}')
        regras.append(f'[data-tema="escuro"]{{{variaveis_escuro}}}')
    return "".join(regras) + _CSS


_CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--v-fundo);color:var(--v-texto);
 font-family:var(--v-fonte);font-size:15px;line-height:1.55;
 -webkit-font-smoothing:antialiased}
#v-raiz{display:flex;min-height:100vh}
.v-main{flex:1;min-width:0}
.v-largura{max-width:var(--v-largura);margin:0 auto;padding:28px 24px 72px}
.v-lateral{width:288px;flex:0 0 288px;background:var(--v-fundo-alt);
 border-right:1px solid var(--v-borda);min-height:100vh}
.v-lateral-int{padding:22px 18px;position:sticky;top:0}
.v-topo{display:flex;align-items:center;gap:10px;padding-bottom:14px;
 margin-bottom:18px;border-bottom:1px solid var(--v-borda)}
.v-marca{font-weight:650;letter-spacing:-.01em}
.v-titulo{font-size:1.85rem;font-weight:680;letter-spacing:-.022em;
 margin:.2em 0 .5em}
.v-subtitulo{font-size:1.3rem;font-weight:640;letter-spacing:-.015em;
 margin:1.3em 0 .5em}
.v-cabecalho{font-weight:630;margin:1.2em 0 .4em}
.v-texto{margin:.5em 0}
.v-divisor{border:0;border-top:1px solid var(--v-borda);margin:22px 0}
.v-icone{font-size:.9em}
.v-md h1,.v-md h2,.v-md h3{letter-spacing:-.015em;margin:1.1em 0 .4em}
.v-md p{margin:.5em 0}
.v-md blockquote{margin:.8em 0;padding:.1px 14px;border-left:3px solid
 var(--v-borda);color:var(--v-texto-fraco)}
.v-codigo{background:var(--v-fundo-alt);border:1px solid var(--v-borda);
 border-radius:var(--v-raio);padding:13px 15px;overflow-x:auto;
 font-family:var(--v-fonte-mono);font-size:.855rem;line-height:1.5}
code{font-family:var(--v-fonte-mono);font-size:.88em;
 background:var(--v-fundo-alt);padding:.1em .35em;border-radius:4px}
.v-codigo code{background:none;padding:0}
.v-link{color:var(--v-info);text-decoration:none}
.v-link:hover{text-decoration:underline}

.v-botao{font:inherit;font-weight:560;padding:8px 17px;border-radius:var(--v-raio);
 border:1px solid transparent;cursor:pointer;transition:filter .12s,
 background .12s;display:inline-flex;align-items:center;gap:7px;
 text-decoration:none;line-height:1.4}
.v-botao:hover{filter:brightness(.94)}
.v-botao:active{transform:translateY(1px)}
.v-botao:focus-visible{outline:2px solid var(--v-info);outline-offset:2px}
.v-primario{background:var(--v-primaria);color:var(--v-primaria-texto)}
.v-secundario{background:var(--v-superficie);color:var(--v-texto);
 border-color:var(--v-borda)}
.v-perigo{background:var(--v-erro);color:#fff}
.v-fantasma{background:transparent;color:var(--v-texto)}

.v-campo{margin:14px 0}
.v-rotulo{display:flex;justify-content:space-between;font-size:.84rem;
 font-weight:560;color:var(--v-texto-fraco);margin-bottom:5px}
.v-entrada{width:100%;font:inherit;padding:8px 11px;border-radius:var(--v-raio);
 border:1px solid var(--v-borda);background:var(--v-superficie);
 color:var(--v-texto)}
.v-entrada:focus{outline:none;border-color:var(--v-primaria);
 box-shadow:0 0 0 3px color-mix(in srgb,var(--v-primaria) 22%,transparent)}
.v-area{resize:vertical;font-family:inherit}
.v-cor{width:56px;height:34px;padding:2px;border:1px solid var(--v-borda);
 border-radius:var(--v-raio);background:var(--v-superficie)}
.v-slider{width:100%;accent-color:var(--v-primaria)}
.v-desl-valor{font-variant-numeric:tabular-nums;color:var(--v-texto)}
.v-caixa,.v-radio{display:flex;align-items:center;gap:8px;margin:6px 0;
 cursor:pointer}
.v-caixas,.v-radios{display:flex;flex-direction:column;gap:2px}
.v-interruptor{display:flex;align-items:center;gap:10px;margin:10px 0;
 cursor:pointer}
.v-interruptor input{position:absolute;opacity:0;width:0;height:0}
.v-trilho{width:38px;height:21px;border-radius:11px;background:var(--v-borda);
 position:relative;transition:background .16s;flex:0 0 auto}
.v-trilho::after{content:"";position:absolute;top:2px;left:2px;width:17px;
 height:17px;border-radius:50%;background:#fff;transition:transform .16s;
 box-shadow:0 1px 3px rgba(0,0,0,.3)}
.v-interruptor input:checked+.v-trilho{background:var(--v-primaria)}
.v-interruptor input:checked+.v-trilho::after{transform:translateX(17px)}

.v-colunas{display:flex;flex-wrap:wrap;align-items:flex-start;margin:6px 0}
.v-coluna{min-width:170px}
.v-linha{display:flex;align-items:center;flex-wrap:wrap;margin:8px 0}
.v-container{margin:4px 0}
.v-borda{border:1px solid var(--v-borda);border-radius:var(--v-raio);padding:16px}
.v-cartao{background:var(--v-superficie);border:1px solid var(--v-borda);
 border-radius:var(--v-raio);padding:17px 19px;margin:12px 0}
.v-cartao-topo{margin-bottom:10px}
.v-cartao-titulo{font-weight:620;display:block;letter-spacing:-.01em}
.v-cartao-sub{font-size:.85rem;color:var(--v-texto-fraco)}
.v-expandir{border:1px solid var(--v-borda);border-radius:var(--v-raio);
 margin:10px 0;background:var(--v-superficie)}
.v-expandir>summary{cursor:pointer;padding:11px 15px;font-weight:560;
 list-style:none}
.v-expandir>summary::-webkit-details-marker{display:none}
.v-expandir>summary::before{content:"▸";display:inline-block;width:1.1em;
 color:var(--v-texto-fraco);transition:transform .14s}
.v-expandir[open]>summary::before{transform:rotate(90deg)}
.v-expandir-int{padding:2px 15px 14px}
.v-abas{margin:14px 0}
.v-abas-topo{display:flex;gap:2px;border-bottom:1px solid var(--v-borda);
 overflow-x:auto}
.v-aba-botao{font:inherit;font-weight:540;background:none;border:0;
 border-bottom:2px solid transparent;padding:9px 15px;cursor:pointer;
 color:var(--v-texto-fraco);white-space:nowrap}
.v-aba-botao.v-ativa{color:var(--v-texto);border-bottom-color:var(--v-primaria)}
.v-aba{padding-top:16px}
.v-formulario{border:1px solid var(--v-borda);border-radius:var(--v-raio);
 padding:16px 18px;margin:14px 0;background:var(--v-superficie)}

.v-metrica{display:flex;flex-direction:column;gap:2px;padding:14px 16px;
 background:var(--v-superficie);border:1px solid var(--v-borda);
 border-radius:var(--v-raio);margin:8px 0}
.v-metrica-rotulo{font-size:.82rem;color:var(--v-texto-fraco);font-weight:540}
.v-metrica-valor{font-size:1.75rem;font-weight:660;letter-spacing:-.025em;
 font-variant-numeric:tabular-nums;line-height:1.15}
.v-variacao{font-size:.84rem;font-weight:580}
.v-sobe{color:var(--v-sucesso)}.v-desce{color:var(--v-erro)}
.v-igual{color:var(--v-texto-fraco)}
.v-ajuda{display:inline-flex;align-items:center;justify-content:center;
 width:15px;height:15px;border-radius:50%;border:1px solid var(--v-borda);
 font-size:10px;margin-left:5px;cursor:help}

.v-tabela-caixa{border:1px solid var(--v-borda);border-radius:var(--v-raio);
 overflow:auto;margin:12px 0;background:var(--v-superficie)}
.v-rolagem{overflow-y:auto}
.v-tabela{width:100%;border-collapse:collapse;font-size:.89rem}
.v-tabela th{text-align:left;font-weight:600;padding:9px 13px;
 background:var(--v-fundo-alt);border-bottom:1px solid var(--v-borda);
 position:sticky;top:0;white-space:nowrap}
.v-tabela td{padding:8px 13px;border-bottom:1px solid var(--v-borda)}
.v-tabela tbody tr:last-child td{border-bottom:0}
.v-tabela tbody tr:hover{background:var(--v-fundo-alt)}
.v-ordenavel th{cursor:pointer;user-select:none}
.v-seta{margin-left:5px;opacity:.45;font-size:.8em}
.v-frame{margin:12px 0}
.v-busca{max-width:260px;margin-bottom:8px}
.v-frame-pe{font-size:.79rem;color:var(--v-texto-fraco);margin-top:6px}
.v-vazio{color:var(--v-texto-fraco);font-size:.88rem;padding:16px;
 text-align:center}
.v-vault{display:grid;grid-template-columns:auto 1fr;gap:4px 18px;margin:12px 0;
 font-size:.9rem}
.v-vault dt{font-weight:580;color:var(--v-texto-fraco)}
.v-vault dd{margin:0}
.v-json{border:1px solid var(--v-borda);border-radius:var(--v-raio);
 margin:12px 0;background:var(--v-superficie)}
.v-json>summary{cursor:pointer;padding:9px 14px;font-size:.85rem;
 color:var(--v-texto-fraco)}
.v-json pre{margin:0;padding:0 14px 12px;overflow:auto;
 font-family:var(--v-fonte-mono);font-size:.82rem}

.v-alerta{display:flex;gap:10px;align-items:flex-start;padding:11px 15px;
 border-radius:var(--v-raio);margin:11px 0;border:1px solid;font-size:.92rem}
.v-alerta-icone{flex:0 0 auto;width:18px;height:18px;border-radius:50%;
 display:flex;align-items:center;justify-content:center;font-size:11px;
 font-weight:700;color:#fff;margin-top:2px}
.v-sucesso{border-color:var(--v-sucesso);
 background:color-mix(in srgb,var(--v-sucesso) 10%,transparent)}
.v-sucesso .v-alerta-icone{background:var(--v-sucesso)}
.v-erro{border-color:var(--v-erro);
 background:color-mix(in srgb,var(--v-erro) 10%,transparent)}
.v-erro .v-alerta-icone{background:var(--v-erro)}
.v-aviso{border-color:var(--v-aviso);
 background:color-mix(in srgb,var(--v-aviso) 12%,transparent)}
.v-aviso .v-alerta-icone{background:var(--v-aviso)}
.v-info{border-color:var(--v-info);
 background:color-mix(in srgb,var(--v-info) 10%,transparent)}
.v-info .v-alerta-icone{background:var(--v-info)}
.v-falha-detalhe{margin:8px 0 0;font-size:.78rem;white-space:pre-wrap;
 font-family:var(--v-fonte-mono);opacity:.85}

.v-prog{margin:12px 0}
.v-prog-rotulo{font-size:.83rem;color:var(--v-texto-fraco);
 display:block;margin-bottom:5px}
.v-prog-trilho{height:7px;border-radius:4px;background:var(--v-borda);
 overflow:hidden}
.v-prog-barra{height:100%;background:var(--v-primaria);
 transition:width .25s ease}
.v-carregando{display:flex;align-items:center;gap:10px;padding:14px 0;
 color:var(--v-texto-fraco);font-size:.9rem}
.v-giro{width:15px;height:15px;border:2px solid var(--v-borda);
 border-top-color:var(--v-primaria);border-radius:50%;
 animation:v-girar .7s linear infinite}
@keyframes v-girar{to{transform:rotate(360deg)}}

.v-figura{margin:14px 0}
.v-figura img{max-width:100%;height:auto;border-radius:var(--v-raio);display:block}
.v-figura figcaption{font-size:.82rem;color:var(--v-texto-fraco);margin-top:6px}
.v-audio,.v-video{width:100%;margin:12px 0;border-radius:var(--v-raio)}

.v-grafico{background:var(--v-superficie);border:1px solid var(--v-borda);
 border-radius:var(--v-raio);padding:14px 16px;margin:14px 0}
.v-grafico-titulo{font-weight:600;font-size:.95rem;margin-bottom:10px;
 letter-spacing:-.01em}
.v-svg{width:100%;height:auto;display:block;overflow:visible}
.v-grade{stroke:var(--v-borda);stroke-width:1}
.v-eixo{fill:var(--v-texto-fraco);font-size:11px;font-family:var(--v-fonte)}
.v-fatia{fill:#fff;font-size:12px;font-weight:600;font-family:var(--v-fonte)}
.v-legenda{display:flex;flex-wrap:wrap;gap:14px;margin-top:10px;
 font-size:.82rem;color:var(--v-texto-fraco)}
.v-legenda-item{display:flex;align-items:center;gap:6px}
.v-legenda-item i{width:10px;height:10px;border-radius:2px;display:inline-block}

.v-ocupado #v-raiz{opacity:.62;transition:opacity .18s .1s}
.v-fita{position:fixed;top:0;left:0;right:0;height:2px;z-index:99;
 background:var(--v-primaria);transform:scaleX(0);transform-origin:left;
 transition:transform .2s}
.v-ocupado .v-fita{transform:scaleX(.75)}

@media (max-width:860px){
 #v-raiz{flex-direction:column}
 .v-lateral{width:100%;flex:none;min-height:0;border-right:0;
  border-bottom:1px solid var(--v-borda)}
 .v-lateral-int{position:static;padding:16px}
 .v-largura{padding:20px 16px 56px}
 .v-coluna{flex:1 1 100% !important}
 .v-titulo{font-size:1.5rem}
}
@media (prefers-reduced-motion:reduce){
 *{animation-duration:.01ms !important;transition-duration:.01ms !important}
}
@media print{
 .v-lateral,.v-botao,.v-busca{display:none}
 .v-cartao,.v-grafico,.v-tabela-caixa{break-inside:avoid}
}
"""


def script(config):
    """O cliente inteiro. Uma função, sem dependência, sem build."""
    intervalo = int(config.get("atualizar_a_cada") or 0)
    return _JS.replace("__INTERVALO__", str(intervalo * 1000))


_JS = r"""
(function(){
var R=document.getElementById('v-raiz'),campos={},pendente=null,ocupado=false;
var fita=document.createElement('div');fita.className='v-fita';
document.body.appendChild(fita);

function valorDe(el){
  if(el.dataset.vBool)return el.checked;
  if(el.dataset.vNumero)return el.value===''?0:Number(el.value);
  return el.value;
}
function coletar(){
  var fora={};
  document.querySelectorAll('[data-v-campo]').forEach(function(el){
    var k=el.dataset.vCampo;
    if(el.dataset.vVarios){
      (fora[k]=fora[k]||[]);
      if(el.checked)fora[k].push(el.value);
    }else if(el.type==='radio'){
      if(el.checked)fora[k]=el.value;
    }else fora[k]=valorDe(el);
  });
  for(var k in campos)fora[k]=campos[k];
  return fora;
}
function enviar(evento,extra){
  if(ocupado){pendente=[evento,extra];return;}
  ocupado=true;document.body.classList.add('v-ocupado');
  fetch('/__vitrine__/acao',{method:'POST',
    headers:{'Content-Type':'application/json','X-Vitrine':'1'},
    body:JSON.stringify({evento:evento||'',campos:coletar(),
      extra:extra||null,caminho:location.pathname+location.search})})
  .then(function(r){return r.json()})
  .then(function(d){
    if(d.redirecionar){location.href=d.redirecionar;return;}
    if(d.html!==undefined){
      var foco=document.activeElement,id=foco&&foco.id,
          pos=foco&&foco.selectionStart;
      R.outerHTML=d.html;R=document.getElementById('v-raiz');
      if(id){var novo=document.getElementById(id);
        if(novo){novo.focus();
          try{if(pos!=null)novo.setSelectionRange(pos,pos)}catch(e){}}}
    }
    if(d.titulo)document.title=d.titulo;
    campos={};
  })
  .catch(function(e){console.error('[vitrine]',e)})
  .finally(function(){
    ocupado=false;document.body.classList.remove('v-ocupado');
    if(pendente){var p=pendente;pendente=null;enviar(p[0],p[1]);}
  });
}
window.Vitrine={atualizar:function(){enviar('')},enviar:enviar};

document.addEventListener('click',function(ev){
  var b=ev.target.closest('[data-v-evento]');
  if(b){enviar(b.dataset.vEvento);return;}
  var s=ev.target.closest('[data-v-enviar]');
  if(s){enviar(s.dataset.vEnviar);return;}
  var a=ev.target.closest('[data-v-aba]');
  if(a){campos[a.dataset.vAba]=a.dataset.vValor;enviar('');return;}
  var th=ev.target.closest('.v-ordenavel th');
  if(th){ordenar(th);return;}
});
document.addEventListener('toggle',function(ev){
  var d=ev.target.closest('[data-v-expandir]');
  if(d)campos[d.dataset.vExpandir]=d.open;
},true);

var espera=null;
document.addEventListener('input',function(ev){
  var el=ev.target.closest('[data-v-campo]');
  if(!el)return;
  if(el.closest('[data-v-form]'))return;      // formulário só no envio
  if(el.dataset.vAdiar){
    var d=el.parentNode.querySelector('.v-desl-valor');
    if(d)d.textContent=el.value;
  }
  clearTimeout(espera);
  espera=setTimeout(function(){enviar('')},el.type==='range'?260:420);
});
document.addEventListener('change',function(ev){
  var el=ev.target.closest('[data-v-campo]');
  if(!el||el.closest('[data-v-form]'))return;
  if(el.tagName==='SELECT'||el.type==='checkbox'||el.type==='radio'||
     el.type==='date'||el.type==='color'){clearTimeout(espera);enviar('')}
});
document.addEventListener('keydown',function(ev){
  if(ev.key!=='Enter')return;
  var f=ev.target.closest('[data-v-form]');
  if(f){var b=f.querySelector('[data-v-enviar]');
    if(b&&ev.target.tagName!=='TEXTAREA'){ev.preventDefault();
      enviar(b.dataset.vEnviar)}}
});

document.addEventListener('change',function(ev){
  var el=ev.target.closest('[data-v-arquivo]');
  if(!el||!el.files.length)return;
  var pacote=[],restam=el.files.length;
  Array.prototype.forEach.call(el.files,function(arq){
    var leitor=new FileReader();
    leitor.onload=function(){
      pacote.push({nome:arq.name,tamanho:arq.size,tipo:arq.type,
        conteudo:leitor.result.split(',')[1]||''});
      if(--restam===0)enviar('',{arquivo:el.dataset.vArquivo,arquivos:pacote});
    };
    leitor.readAsDataURL(arq);
  });
});

document.addEventListener('input',function(ev){
  var busca=ev.target.closest('[data-v-filtrar]');
  if(!busca)return;
  var termo=busca.value.toLowerCase(),
      corpo=busca.parentNode.querySelector('tbody');
  if(!corpo)return;
  Array.prototype.forEach.call(corpo.rows,function(l){
    l.hidden=termo&&l.textContent.toLowerCase().indexOf(termo)<0;
  });
});
function ordenar(th){
  var tabela=th.closest('table'),i=+th.dataset.vOrdenar,
      corpo=tabela.tBodies[0],
      desc=th.getAttribute('data-v-desc')==='1';
  var linhas=Array.prototype.slice.call(corpo.rows);
  linhas.sort(function(a,b){
    var x=a.cells[i].textContent,y=b.cells[i].textContent,
        nx=parseFloat(x.replace(',','.')),ny=parseFloat(y.replace(',','.'));
    var r=(!isNaN(nx)&&!isNaN(ny))?nx-ny:x.localeCompare(y,'pt-BR');
    return desc?-r:r;
  });
  linhas.forEach(function(l){corpo.appendChild(l)});
  tabela.querySelectorAll('th').forEach(function(o){
    o.removeAttribute('data-v-desc');
    var s=o.querySelector('.v-seta');if(s)s.textContent='';
  });
  th.setAttribute('data-v-desc',desc?'0':'1');
  var seta=th.querySelector('.v-seta');if(seta)seta.textContent=desc?'▲':'▼';
}

var periodo=__INTERVALO__;
if(periodo>0)setInterval(function(){
  // Uma aba escondida não precisa de dado fresco, e cobrar do servidor
  // por uma página que ninguém está vendo é desperdício puro.
  if(!document.hidden&&!ocupado)enviar('');
},periodo);
})();
"""
