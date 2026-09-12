"""Os componentes — texto, entrada, dados, layout, retorno.

Cada função aqui faz duas coisas: **põe um nó na árvore** e **devolve o
que quem escreve precisa**. Um `V.botao(...)` devolve `yes`/`no`, uma
`V.entrada(...)` devolve o texto digitado — porque o programa continua
de cima para baixo, e a linha seguinte já usa o valor.

É essa devolução que faz o modelo funcionar sem callback:

    given V.botao("Salvar"):
        salvar(V.entrada("Nome"))
"""

from .nucleo import Contexto, No


def _ctx():
    """O contexto da montagem atual, com uma mensagem que ajuda."""
    ctx = Contexto.atual()
    if ctx is None:
        from ...errors import RuntimeError_
        raise RuntimeError_(
            "componente da Vitrine chamado fora de uma aplicacao.", 0, 0,
            nota="a arvore so existe enquanto o programa da pagina roda",
            dica="ponha o codigo dentro de 'action pagina():' e suba com\n"
                 "    V.rodar(pagina)",
            doc="tecnicas/vitrine")
    return ctx


def _por(tipo, props=None, chave=None):
    ctx = _ctx()
    return ctx.por(No(tipo, props or {}, chave=chave))


# ═══════════════════════════════════════════════════════════
#  Texto
# ═══════════════════════════════════════════════════════════

def texto(*partes):
    """Texto simples. Vários argumentos viram uma linha, como o `out`."""
    conteudo = " ".join(_str(p) for p in partes)
    _por("texto", {"conteudo": conteudo})
    return conteudo


def titulo(conteudo, icone=""):
    _por("titulo", {"conteudo": _str(conteudo), "icone": icone})
    return conteudo


def subtitulo(conteudo):
    _por("subtitulo", {"conteudo": _str(conteudo)})
    return conteudo


def cabecalho(conteudo, nivel=3):
    _por("cabecalho", {"conteudo": _str(conteudo),
                       "nivel": max(1, min(6, int(nivel)))})
    return conteudo


def markdown(conteudo):
    _por("markdown", {"conteudo": _str(conteudo)})
    return conteudo


def codigo(conteudo, linguagem="dataforge"):
    _por("codigo", {"conteudo": _str(conteudo), "linguagem": linguagem})
    return conteudo


def html(conteudo):
    """HTML cru — e ele é **inserido sem escapar**.

    É a única porta de XSS da Vitrine, e ela existe porque às vezes não
    há alternativa. Nunca passe aqui algo que veio do usuário; para
    isso, `V.texto`, que escapa.
    """
    _por("html", {"conteudo": _str(conteudo)})
    return conteudo


def divisor():
    _por("divisor")


def espaco(altura=16):
    _por("espaco", {"altura": int(altura)})


# ═══════════════════════════════════════════════════════════
#  Entrada
# ═══════════════════════════════════════════════════════════

def botao(rotulo, tipo="primario", chave=None, largura=""):
    """Devolve `yes` no ciclo em que foi clicado, `no` nos outros.

    Vale por **uma** execução: um botão que continuasse verdadeiro
    dispararia a ação de novo no próximo carregamento da página, e
    duplicar um pagamento é o tipo de bug que ninguém perdoa.
    """
    ctx = _ctx()
    k = ctx.chave_para("botao", rotulo, chave)
    _por("botao", {"rotulo": _str(rotulo), "variante": tipo,
                   "chave": k, "largura": largura}, chave=k)
    return ctx.foi_acionado(k)


def entrada(rotulo, valor="", dica="", tipo="texto", chave=None):
    """Campo de texto. Devolve o que está digitado."""
    ctx = _ctx()
    k = ctx.chave_para("entrada", rotulo, chave)
    atual = ctx.valor_de(k, valor)
    ctx.guardar_valor(k, atual)
    _por("entrada", {"rotulo": _str(rotulo), "valor": _str(atual),
                     "dica": dica, "tipo": tipo, "chave": k}, chave=k)
    return atual


def area_de_texto(rotulo, valor="", linhas=4, dica="", chave=None):
    ctx = _ctx()
    k = ctx.chave_para("area", rotulo, chave)
    atual = ctx.valor_de(k, valor)
    ctx.guardar_valor(k, atual)
    _por("area", {"rotulo": _str(rotulo), "valor": _str(atual),
                  "linhas": int(linhas), "dica": dica, "chave": k}, chave=k)
    return atual


def numero(rotulo, valor=0, minimo=None, maximo=None, passo=1, chave=None):
    ctx = _ctx()
    k = ctx.chave_para("numero", rotulo, chave)
    atual = _numero_de(ctx.valor_de(k, valor), valor)
    if minimo is not None:
        atual = max(_numero_de(minimo, 0), atual)
    if maximo is not None:
        atual = min(_numero_de(maximo, atual), atual)
    ctx.guardar_valor(k, atual)
    _por("numero", {"rotulo": _str(rotulo), "valor": atual,
                    "minimo": minimo, "maximo": maximo,
                    "passo": passo, "chave": k}, chave=k)
    return atual


def deslizante(rotulo, minimo=0, maximo=100, valor=None, passo=1, chave=None):
    ctx = _ctx()
    k = ctx.chave_para("deslizante", rotulo, chave)
    padrao = valor if valor is not None else minimo
    atual = _numero_de(ctx.valor_de(k, padrao), padrao)
    atual = max(_numero_de(minimo, 0), min(_numero_de(maximo, 100), atual))
    ctx.guardar_valor(k, atual)
    _por("deslizante", {"rotulo": _str(rotulo), "minimo": minimo,
                        "maximo": maximo, "valor": atual, "passo": passo,
                        "chave": k}, chave=k)
    return atual


def caixa(rotulo, valor=False, chave=None):
    ctx = _ctx()
    k = ctx.chave_para("caixa", rotulo, chave)
    atual = bool(ctx.valor_de(k, valor))
    ctx.guardar_valor(k, atual)
    _por("caixa", {"rotulo": _str(rotulo), "valor": atual, "chave": k},
         chave=k)
    return atual


def interruptor(rotulo, valor=False, chave=None):
    ctx = _ctx()
    k = ctx.chave_para("interruptor", rotulo, chave)
    atual = bool(ctx.valor_de(k, valor))
    ctx.guardar_valor(k, atual)
    _por("interruptor", {"rotulo": _str(rotulo), "valor": atual, "chave": k},
         chave=k)
    return atual


def opcao(rotulo, opcoes, indice=0, chave=None):
    """Um de vários, em botões de rádio."""
    ctx = _ctx()
    lista = [_str(o) for o in (opcoes or [])]
    k = ctx.chave_para("opcao", rotulo, chave)
    padrao = lista[indice] if 0 <= indice < len(lista) else (
        lista[0] if lista else "")
    atual = ctx.valor_de(k, padrao)
    if atual not in lista and lista:
        atual = padrao
    ctx.guardar_valor(k, atual)
    _por("opcao", {"rotulo": _str(rotulo), "opcoes": lista,
                   "valor": atual, "chave": k}, chave=k)
    return atual


def escolha(rotulo, opcoes, indice=0, chave=None):
    """Um de vários, numa lista suspensa."""
    ctx = _ctx()
    lista = [_str(o) for o in (opcoes or [])]
    k = ctx.chave_para("escolha", rotulo, chave)
    padrao = lista[indice] if 0 <= indice < len(lista) else (
        lista[0] if lista else "")
    atual = ctx.valor_de(k, padrao)
    if atual not in lista and lista:
        atual = padrao
    ctx.guardar_valor(k, atual)
    _por("escolha", {"rotulo": _str(rotulo), "opcoes": lista,
                     "valor": atual, "chave": k}, chave=k)
    return atual


def escolhas(rotulo, opcoes, padrao=None, chave=None):
    """Vários de vários. Devolve um cluster."""
    ctx = _ctx()
    lista = [_str(o) for o in (opcoes or [])]
    k = ctx.chave_para("escolhas", rotulo, chave)
    inicial = [_str(p) for p in (padrao or [])]
    atual = ctx.valor_de(k, inicial)
    if not isinstance(atual, list):
        atual = [atual] if atual else []
    atual = [v for v in atual if v in lista]
    ctx.guardar_valor(k, atual)
    _por("escolhas", {"rotulo": _str(rotulo), "opcoes": lista,
                      "valor": atual, "chave": k}, chave=k)
    return atual


def data(rotulo, valor="", chave=None):
    ctx = _ctx()
    k = ctx.chave_para("data", rotulo, chave)
    atual = _str(ctx.valor_de(k, valor))
    ctx.guardar_valor(k, atual)
    _por("data", {"rotulo": _str(rotulo), "valor": atual, "chave": k},
         chave=k)
    return atual


def cor(rotulo, valor="#FED403", chave=None):
    ctx = _ctx()
    k = ctx.chave_para("cor", rotulo, chave)
    atual = _str(ctx.valor_de(k, valor))
    ctx.guardar_valor(k, atual)
    _por("cor", {"rotulo": _str(rotulo), "valor": atual, "chave": k}, chave=k)
    return atual


def arquivo(rotulo, tipos=None, varios=False, chave=None):
    """Devolve `void` até alguém enviar; depois, o vault do arquivo.

    Um arquivo tem `nome`, `tamanho`, `tipo` e `conteudo`. Com
    `varios := yes`, devolve um cluster deles.
    """
    ctx = _ctx()
    k = ctx.chave_para("arquivo", rotulo, chave)
    enviados = ctx.sessao.obter(f"__arquivo__{k}")
    _por("arquivo", {"rotulo": _str(rotulo),
                     "tipos": [_str(t) for t in (tipos or [])],
                     "varios": bool(varios), "chave": k}, chave=k)
    if enviados is None:
        return [] if varios else None
    return enviados


# ═══════════════════════════════════════════════════════════
#  Dados
# ═══════════════════════════════════════════════════════════

def tabela(dados, colunas=None, altura=None):
    """Uma tabela. Aceita cluster de vaults, Frame, ou matriz."""
    linhas, cabecalhos = _normalizar_tabela(dados, colunas)
    _por("tabela", {"linhas": linhas, "colunas": cabecalhos,
                    "altura": altura})
    return dados


def frame(dados, colunas=None, altura=None):
    """Uma tabela com ordenação e busca, para explorar dado."""
    linhas, cabecalhos = _normalizar_tabela(dados, colunas)
    _por("frame", {"linhas": linhas, "colunas": cabecalhos,
                   "altura": altura})
    return dados


def metrica(rotulo, valor, variacao=None, ajuda=""):
    """Um número grande, com a variação ao lado.

    A variação sobe em verde e desce em vermelho — e é por isso que ela
    é um número, e não um texto: a Vitrine precisa saber o sinal.
    """
    _por("metrica", {"rotulo": _str(rotulo), "valor": _str(valor),
                     "variacao": variacao, "ajuda": ajuda})
    return valor


def json_(dados, expandido=True):
    _por("json", {"dados": dados, "expandido": bool(expandido)})
    return dados


def vault(dados):
    """Um vault mostrado como lista de chave e valor."""
    _por("vault", {"dados": dados})
    return dados


# ═══════════════════════════════════════════════════════════
#  Retorno ao usuário
# ═══════════════════════════════════════════════════════════

def sucesso(mensagem):
    _por("alerta", {"nivel": "sucesso", "mensagem": _str(mensagem)})


def erro(mensagem):
    _por("alerta", {"nivel": "erro", "mensagem": _str(mensagem)})


def aviso(mensagem):
    _por("alerta", {"nivel": "aviso", "mensagem": _str(mensagem)})


def informacao(mensagem):
    _por("alerta", {"nivel": "info", "mensagem": _str(mensagem)})


def progresso(fracao, rotulo=""):
    """Barra de 0 a 1."""
    valor = max(0.0, min(1.0, float(fracao)))
    _por("progresso", {"valor": valor, "rotulo": _str(rotulo)})
    return valor


def carregando(mensagem="Carregando…"):
    _por("carregando", {"mensagem": _str(mensagem)})


def imagem(origem, legenda="", largura=None):
    _por("imagem", {"origem": _str(origem), "legenda": _str(legenda),
                    "largura": largura})


def audio(origem, formato="audio/mpeg"):
    _por("audio", {"origem": _str(origem), "formato": formato})


def video(origem, formato="video/mp4"):
    _por("video", {"origem": _str(origem), "formato": formato})


def link(rotulo, destino, nova_aba=False):
    _por("link", {"rotulo": _str(rotulo), "destino": _str(destino),
                  "nova_aba": bool(nova_aba)})


def baixar(rotulo, conteudo, nome="dados.txt", tipo="text/plain"):
    """Um botão que entrega um arquivo ao visitante."""
    ctx = _ctx()
    k = ctx.chave_para("baixar", rotulo)
    ctx.sessao.definir(f"__baixar__{k}",
                       {"conteudo": _str(conteudo), "nome": nome,
                        "tipo": tipo})
    _por("baixar", {"rotulo": _str(rotulo), "nome": nome, "chave": k},
         chave=k)


# ═══════════════════════════════════════════════════════════
#  Utilidades internas
# ═══════════════════════════════════════════════════════════

def _str(valor):
    """O valor como texto, no vocabulário da linguagem."""
    if valor is True:
        return "yes"
    if valor is False:
        return "no"
    if valor is None:
        return "void"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def _numero_de(valor, padrao):
    try:
        if isinstance(valor, bool):
            return int(valor)
        if isinstance(valor, (int, float)):
            return valor
        texto = str(valor).strip().replace(",", ".")
        return float(texto) if "." in texto else int(texto)
    except (TypeError, ValueError):
        return padrao


def _normalizar_tabela(dados, colunas=None):
    """Cluster de vaults, Frame ou matriz — tudo vira (linhas, colunas).

    Aceitar as três formas não é indulgência: elas são o que o
    `IO.read_csv`, o `Arcane.Database` e o `frame` da linguagem
    devolvem, e obrigar a converter seria pedir que a pessoa conheça a
    diferença antes de mostrar uma tabela.
    """
    if dados is None:
        return [], list(colunas or [])

    # Frame do Arcane.Analytics
    if hasattr(dados, "to_dict") and hasattr(dados, "columns"):
        registros = dados.to_dict()
        cabecalhos = list(colunas or dados.columns)
        return ([[_str(r.get(c, "")) for c in cabecalhos] for r in registros],
                cabecalhos)

    if isinstance(dados, dict):
        # Vault de colunas: {"a": [1, 2], "b": [3, 4]}
        if dados and all(isinstance(v, list) for v in dados.values()):
            cabecalhos = list(colunas or dados.keys())
            altura = max((len(v) for v in dados.values()), default=0)
            linhas = [[_str(dados.get(c, [])[i]
                            if i < len(dados.get(c, [])) else "")
                       for c in cabecalhos] for i in range(altura)]
            return linhas, cabecalhos
        return [[_str(k), _str(v)] for k, v in dados.items()], ["chave", "valor"]

    if isinstance(dados, (list, tuple)):
        itens = list(dados)
        if not itens:
            return [], list(colunas or [])

        if isinstance(itens[0], dict):
            cabecalhos = list(colunas) if colunas else []
            if not cabecalhos:
                # A ordem de aparição, e não a alfabética: quem montou o
                # vault escolheu uma ordem, e ela costuma ser a certa.
                vistos = []
                for reg in itens:
                    for c in reg:
                        if c not in vistos:
                            vistos.append(c)
                cabecalhos = vistos
            return ([[_str(r.get(c, "")) for c in cabecalhos] for r in itens],
                    cabecalhos)

        if isinstance(itens[0], (list, tuple)):
            largura = max(len(l) for l in itens)
            cabecalhos = list(colunas or [f"col{i + 1}" for i in range(largura)])
            return [[_str(v) for v in linha] for linha in itens], cabecalhos

        return [[_str(v)] for v in itens], list(colunas or ["valor"])

    return [[_str(dados)]], list(colunas or ["valor"])
