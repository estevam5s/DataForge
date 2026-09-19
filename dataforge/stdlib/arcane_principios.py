# -*- coding: utf-8 -*-
"""Arcane.Principios — os dez principios, com a prova de cada um. E as tensoes.

O que faltava
-------------
A referencia Deep Tech fecha com dez principios de design. Uma lista de
principios e o texto mais facil de escrever num projeto e o mais facil de
nao cumprir: ninguem a executa, e por isso ela nunca reprova.

Aqui cada principio carrega:

    no_documento   a frase como o documento a escreve
    aqui           o que ela significa NESTA implementacao
    veredito       cumprido | parcial | nao-se-aplica
    prova          uma medida que RODA — e o numero que ela deu
    custo          o que foi entregue em troca

`conferir()` executa as dez provas. Duas delas rodam o analisador e o
interpretador sobre trechos proprios, porque "verificacao antes de rodar"
e "custa zero quando desligado" nao sao frases: sao coisas que se
demonstram ou nao se demonstram.

As tensoes sao o conteudo
-------------------------
Um principio isolado nao informa nada: todo mundo e a favor de seguranca
e de velocidade. O que informa e **onde dois principios se contradizem e
qual deles venceu** — e essa decisao, nesta linguagem, esta sempre num
arquivo. `TENSOES` traz nove, cada uma com a escolha, o porque, o custo
aceito e onde ela mora.

    adopt Arcane.Principios as Prin

    cycle p in Prin.conferir():
        out $"{p['principio']}: {p['veredito']} — {p['medido']}"

    cycle t in Prin.tensoes():
        out $"{t['entre'][0]} x {t['entre'][1]} -> {t['escolha']}"
"""

import os

from ..errors import RuntimeError_

#: Os tres vereditos. A lista e fechada de proposito: um quarto valor
#: seria onde "mais ou menos" se esconderia.
VEREDITOS = ("cumprido", "parcial", "nao-se-aplica")

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))


# ═══ As provas ═════════════════════════════════════════════
#
# Cada uma devolve (medido, como). `medido` e o numero ou a frase curta
# que sai da medicao; `como` diz o que foi feito para obte-la.

def _diagnosticos(fonte):
    """Roda o analisador sobre um trecho e devolve os diagnosticos."""
    from ..lexer import tokenize
    from ..parser import parse
    from ..typechecker import check_program
    return check_program(parse(tokenize(fonte, "<prova>"), "<prova>"),
                         "<prova>")


def _rodar(fonte):
    """Roda um trecho e devolve o interpretador, para olhar o estado."""
    from ..interpreter import Interpreter
    from ..lexer import tokenize
    from ..parser import parse
    interp = Interpreter()
    interp.run(parse(tokenize(fonte, "<prova>"), "<prova>"))
    return interp


def _prova_seguranca():
    """A escrita concorrente e ERRO ou AVISO? O numero e a severidade."""
    from .arcane_capacidade import CAPACIDADES, _EXIGE
    fonte = ("total := 0\n"
             "thread:\n"
             "    total := total + 1\n")
    achados = [d for d in _diagnosticos(fonte)
               if d.code == "escrita-concorrente"]
    severidade = achados[0].severity if achados else "nenhum"
    return (f"{len(CAPACIDADES)} capacidades, {len(_EXIGE)} modulos atras "
            f"delas; a escrita concorrente sai como '{severidade}'",
            "roda o 'check' sobre um 'thread' que escreve num nome de fora")


def _prova_custo_zero():
    """Os tres sentinelas `None` num objeto que nao usa recurso nenhum."""
    interp = _rodar("blueprint A:\n"
                    "    action f():\n"
                    "        yield 1\n"
                    "a := spawn A()\n")
    obj = interp.global_env.get("a")
    bp = interp.global_env.get("A")
    metodo = bp.methods.get("f") if hasattr(bp, "methods") else None
    nulos = []
    for rotulo, valor in (("DFInstance._estado", getattr(obj, "_estado", 1)),
                          ("DFBlueprint.vigias", getattr(bp, "vigias", 1)),
                          ("DFAction.extras", getattr(metodo, "extras", 1))):
        if valor is None:
            nulos.append(rotulo)
    atalhos = [n for n in ("leitura_simples", "escrita_simples")
               if getattr(bp, n, False)]
    return (f"{len(nulos)} de 3 sentinelas em None, {len(atalhos)} de 2 "
            f"atalhos de acesso ligados",
            "cria um blueprint sem contrato, invariante nem modificador e "
            "olha o que ele carrega")


def _prova_controle_explicito():
    from .. import tokens as _tokens
    from . import get_module
    posse = get_module("Arcane.Posse") or {}
    memoria = get_module("Arcane.Memoria") or {}
    tem_defer = "defer" in _tokens.KEYWORDS
    return (f"Posse com {len([k for k in posse if not k.startswith('__')])} "
            f"simbolos, Memoria com "
            f"{len([k for k in memoria if not k.startswith('__')])}, "
            f"'defer' {'e' if tem_defer else 'NAO e'} palavra da linguagem",
            "conta os simbolos das duas peças de recurso e confere 'defer'")


def _prova_compile_time():
    """Quatro erros que existiam so em execucao. Quantos o 'check' pega?"""
    trechos = {
        "indice fora do alcance": "xs := [1, 2, 3]\nout xs[10]\n",
        "chave ausente num vault": 'v := {"cidade": "SP"}\nout v["cidad"]\n',
        "laco que nunca roda": "cycle i from 5 to 1:\n    out i\n",
        "igualdade impossivel": 'out 1 is "1"\n',
    }
    pegos = []
    for rotulo, fonte in trechos.items():
        if _diagnosticos(fonte):
            pegos.append(rotulo)
    return (f"{len(pegos)} de {len(trechos)} erros de execucao acusados "
            f"ANTES de rodar",
            "roda o 'check' sobre quatro trechos com defeito conhecido")


def _prova_interoperabilidade():
    from . import get_module
    c = get_module("Arcane.C") or {}
    # Nao imprime nada: uma prova que escreve na saida suja o
    # relatorio de quem a chamou.
    fonte = "adopt Python.json as J\nfeito := J.dumps([1, 2])\n"
    try:
        _rodar(fonte)
        ponte = "a ponte para o Python resolve"
    except Exception as erro:                      # pragma: no cover
        ponte = f"a ponte falhou: {erro}"
    return (f"Arcane.C com {len([k for k in c if not k.startswith('__')])} "
            f"simbolos; {ponte}",
            "conta os simbolos do FFI e adota um modulo do Python de verdade")


def _prova_portabilidade():
    from .arcane_alvo import ALVOS
    tudo = [n for n, p in ALVOS.items() if not p["porque"]]
    nada = [n for n, p in ALVOS.items() if not p["suporta"]]
    return (f"{len(ALVOS)} alvos descritos: {len(tudo)} sem restricao, "
            f"{len(nada)} sem capacidade nenhuma ({', '.join(nada)})",
            "le a tabela de alvos e conta os extremos")


def _prova_performance_observavel():
    from ..cli import COMANDOS
    esperados = ("profile", "bench", "big-o", "custo", "ir", "percurso",
                 "stats", "oop")
    presentes = [c for c in esperados if c in COMANDOS]
    return (f"{len(presentes)} de {len(esperados)} comandos de medicao "
            f"presentes: {', '.join(presentes)}",
            "procura cada comando de medicao no catalogo da CLI")


def _prova_extensibilidade():
    from .. import tokens as _tokens
    from ..parser import Parser
    from . import get_module
    contextuais = (len(_tokens.CONTEXTUAIS_KILN)
                   + len(_tokens.CONTEXTUAIS_BLUEPRINT)
                   + len(_tokens.CONTEXTUAIS_TIPO)
                   + len(_tokens.CONTEXTUAIS_CRUCIBLE)
                   + len(Parser.VERBOS_DE_QUADRO))
    macro = get_module("Arcane.Macro") or {}
    dsl = get_module("Arcane.Dsl") or {}
    return (f"{len(_tokens.KEYWORDS)} palavras reservadas contra "
            f"{contextuais} CONTEXTUAIS; Macro com "
            f"{len([k for k in macro if not k.startswith('__')])} simbolos e "
            f"Dsl com {len([k for k in dsl if not k.startswith('__')])}",
            "conta as reservadas, as contextuais e os simbolos de "
            "metaprogramacao")


def _prova_runtime_modular():
    from ..interpreter import Interpreter
    interp = Interpreter()
    carregados = len(interp.modules)
    externas = []
    caminho = os.path.join(_RAIZ, "pyproject.toml")
    if os.path.isfile(caminho):
        try:
            import tomllib
            with open(caminho, "rb") as arquivo:
                externas = tomllib.load(arquivo)["project"].get(
                    "dependencies", [])
        except Exception:                          # pragma: no cover
            externas = []
    return (f"{carregados} modulos carregados num interpretador novo, "
            f"{len(externas)} dependencias externas no runtime",
            "abre um interpretador sem 'adopt' e le as dependencias do "
            "pyproject")


def _prova_escalabilidade():
    from .arcane_ecossistema import o_que_nao_existe
    from .arcane_alvo import ALVOS
    ausentes = [c["no"] for c in o_que_nao_existe()]
    vazios = [n for n, p in ALVOS.items() if not p["suporta"]]
    return (f"{len(ausentes)} componentes do desenho nao existem "
            f"({', '.join(ausentes)}); {len(vazios)} alvo(s) sem "
            f"capacidade nenhuma",
            "cruza o mapa do ecossistema com a tabela de alvos")


#: Os dez principios do documento, na ordem dele.
PRINCIPIOS = (
    {"numero": 1, "principio": "seguranca-por-padrao",
     "no_documento": "APIs seguras devem ser preferidas as operacoes "
                     "inseguras.",
     "aqui": "a fronteira de capacidade nega por omissao dentro de "
             "'Capacidade.executar', o zip e o tar recusam caminho para "
             "fora, a extracao de pacote recusa '../' e link simbolico, e "
             "nome de coluna nao vai cru para o SQL. Mas o analisador e "
             "OTIMISTA: a escrita concorrente e aviso, nao erro",
     "veredito": "parcial",
     "prova": _prova_seguranca,
     "custo": "um bug de concorrencia passa pelo 'check'. Recusa-lo "
              "proibiria o acumulador protegido por mutex, que e o uso "
              "correto",
     "onde": ("/docs/seguranca/capacidade", "/docs/tecnicas/concorrencia")},

    {"numero": 2, "principio": "custo-zero",
     "no_documento": "abstracoes de alto nivel devem compilar para codigo "
                     "equivalente a implementacoes manuais.",
     "aqui": "nao ha compilacao para codigo nativo, e por isso a frase do "
             "documento nao tem como valer. O que vale — e e cobrado — e "
             "OUTRA leitura: uma abstracao custa zero para quem NAO a usa. "
             "Contrato, invariante, sobrecarga, metaclasse, 'exclusive' e "
             "'lazy' vivem atras de tres sentinelas 'None', e o acesso a "
             "campo ficou mais rapido DEPOIS de os recursos existirem",
     "veredito": "nao-se-aplica",
     "prova": _prova_custo_zero,
     "custo": "quem acrescenta um jeito novo de interceptar acesso tem de "
              "derrubar o atalho do blueprint — e a falta nao da erro: so "
              "faz o recurso novo nao rodar para os objetos simples",
     "onde": ("/docs/oop/slots", "/docs/faq/desempenho")},

    {"numero": 3, "principio": "controle-explicito-de-recursos",
     "no_documento": "o desenvolvedor deve conseguir controlar memoria, "
                     "threads, I/O e recursos do sistema.",
     "aqui": "'defer' roda na saida da acao onde quer que esteja escrito; "
             "'Arcane.Posse' da posse exclusiva, emprestimo com escopo e "
             "contagem deterministica; 'Arcane.Memoria' liga e desliga o "
             "coletor, muda os limiares e congela; 'Arcane.Laco' entrega o "
             "escalonador",
     "veredito": "cumprido",
     "prova": _prova_controle_explicito,
     "custo": "o que se controla e o PROTOCOLO, nao a memoria: nao ha "
              "alocador proprio, porque ele exigiria estar fora do CPython",
     "onde": ("/docs/memoria/posse", "/docs/memoria/coletor")},

    {"numero": 4, "principio": "compile-time-first",
     "no_documento": "verificacoes e computacoes que possam ocorrer durante "
                     "a compilacao devem ser deslocadas para essa etapa.",
     "aqui": "o 'check' atravessa arquivos pela superficie, ve dentro dos "
             "objetos, prova o que um literal permite e recusa uma "
             "declaracao que se contradiz; 'comptime' calcula na leitura. "
             "O limite e deliberado: quando nao consegue PROVAR, ele cala",
     "veredito": "parcial",
     "prova": _prova_compile_time,
     "custo": "os silencios sao reais e estao listados. Um falso alarme "
              "ensina a desligar a verificacao inteira, e trocar um falso "
              "alarme por um silencio e a troca certa",
     "onde": ("/docs/tecnicas/analise-estatica", "/docs/metaprogramacao/comptime")},

    {"numero": 5, "principio": "interoperabilidade",
     "no_documento": "integracao com C, C++, sistemas operacionais, "
                     "bibliotecas nativas e hardware.",
     "aqui": "'Arcane.C' carrega biblioteca nativa, monta struct conferida "
             "contra a ABI e passa callback — o 'qsort' do C chama uma acao "
             "DataForge. E 'adopt Python.numpy' traz o ecossistema inteiro "
             "do Python SEM converter nada",
     "veredito": "cumprido",
     "prova": _prova_interoperabilidade,
     "custo": "a ponte so funciona porque o interpretador trata objeto "
              "estranho por protocolo. Trocar protocolo por 'isinstance' em "
              "qualquer lugar do caminho quebra a ponte inteira",
     "onde": ("/docs/ffi/c", "/docs/tecnicas/ponte")},

    {"numero": 6, "principio": "portabilidade",
     "no_documento": "suporte a multiplos sistemas operacionais, "
                     "arquiteturas e targets.",
     "aqui": "a portabilidade e HERDADA do CPython: onde ele roda, o "
             "DataForge roda, e o release constroi e testa nas quatro "
             "plataformas. 'Arcane.Alvo' descreve seis ambientes e diz por "
             "que cada um nao tem o que nao tem",
     "veredito": "parcial",
     "prova": _prova_portabilidade,
     "custo": "herdar e o que da ARM e Windows de graca, e e o que poe o "
              "teto de desempenho em ~6,5x. Compilar PARA WASM nao existe; "
              "rodar EM WASM funciona, e sao frases diferentes",
     "onde": ("/docs/alvos/portabilidade", "/docs/alvos/wasm")},

    {"numero": 7, "principio": "performance-observavel",
     "no_documento": "ferramentas de profiling, benchmarking e diagnostico "
                     "devem fazer parte do ecossistema.",
     "aqui": "'profile' da o tempo PROPRIO por acao; 'bench' mede e "
             "classifica a curva; 'big-o' LE a complexidade da arvore; "
             "'custo' estima; 'ir' e 'percurso' mostram as fases; "
             "'Arcane.Perfil' tem percentis, flame graph e Mann-Whitney "
             "para dizer se a diferenca e real",
     "veredito": "cumprido",
     "prova": _prova_performance_observavel,
     "custo": "medir e ler sao ferramentas que erram de formas OPOSTAS, e "
              "por isso existem as duas: a leitura ve 'cycle dentro de "
              "cycle' e diz O(n²) mesmo que o laco de dentro rode tres "
              "vezes; a medida nao sabe o que acontece com n maior",
     "onde": ("/docs/observabilidade/perfil", "/docs/big-o/analisar")},

    {"numero": 8, "principio": "extensibilidade",
     "no_documento": "macros, plugins, DSLs e APIs internas devem permitir "
                     "evolucao da linguagem.",
     "aqui": "'Arcane.Macro' trata a arvore como dado (citar, transformar, "
             "gerar, derivar); 'Arcane.Dsl' da combinadores para uma "
             "linguagem externa; o 'check' aceita plugin. E as palavras "
             "novas entram como CONTEXTUAIS, nao reservadas",
     "veredito": "cumprido",
     "prova": _prova_extensibilidade,
     "custo": "palavra contextual custa complexidade no parser — "
              "'_abre_server', '_e_modificador', '_abre_tipo'. O preco "
              "alternativo era tirar 'route', 'render', 'agrupar' e "
              "'ordenar' de quem escreve, e sete palavras reservadas ja "
              "foram REMOVIDAS por serem caras sem entregar nada",
     "onde": ("/docs/metaprogramacao/macros", "/docs/metaprogramacao/dsl")},

    {"numero": 9, "principio": "runtime-modular",
     "no_documento": "aplicacoes simples devem poder utilizar apenas os "
                     "componentes de runtime necessarios.",
     "aqui": "um programa que nao adota nada carrega ZERO modulos da "
             "biblioteca: o dicionario de cada um e construido no 'adopt'. "
             "E nao ha dependencia externa no runtime — a biblioteca padrao "
             "usa apenas a do Python",
     "veredito": "cumprido",
     "prova": _prova_runtime_modular,
     "custo": "ChaCha20-Poly1305, o '.xlsx', o WebSocket do RFC 6455 e os "
              "graficos em SVG foram escritos a mao onde havia biblioteca "
              "madura. E o preco: um app em rede fechada funciona",
     "onde": ("/docs/biblioteca", "/docs/referencia/arquitetura")},

    {"numero": 10, "principio": "escalabilidade-tecnica",
     "no_documento": "desde aplicacoes convencionais ate sistemas de baixo "
                     "nivel, kernels, embarcados e computacao de alto "
                     "desempenho.",
     "aqui": "aplicacao, servidor e linha de comando: sim, e e onde a "
             "linguagem vive. Kernel, bare-metal e microcontrolador: nao, e "
             "nao ha caminho a partir daqui — o runtime e o CPython. Mais "
             "de um nucleo existe, por processo, e foi medido em 3,45x",
     "veredito": "parcial",
     "prova": _prova_escalabilidade,
     "custo": "a metade de baixo do espectro esta fora, e o projeto prefere "
              "nomea-la a prometer. 'Arcane.Alvo' lista o que falta em cada "
              "capacidade do alvo 'embarcado' para que a ausencia apareca "
              "antes de alguem tentar",
     "onde": ("/docs/alvos/portabilidade", "/docs/tecnicas/processos")},
)


#: Onde dois principios se contradizem, e qual venceu. E o conteudo que
#: uma lista de principios nunca tem: a lista diz o que se quer, a tensao
#: diz o que se ESCOLHEU quando nao era possivel querer as duas coisas.
TENSOES = (
    {"entre": ("seguranca-por-padrao", "compile-time-first"),
     "escolha": "aviso, e nao erro, para a escrita concorrente",
     "porque": "um acumulador protegido por mutex passa pelo mesmo caminho "
               "de um sem protecao, e recusa-lo proibiria o uso correto. O "
               "aviso nomeia o que foi MEDIDO: seis pedidos simultaneos "
               "numa rota que le, espera e escreve entregaram 1 de 6",
     "custo": "um programa com bug de concorrencia passa pelo 'check'",
     "onde": "dataforge/typechecker.py — _CODIGO_CORRIDA"},

    {"entre": ("compile-time-first", "nao-dar-falso-alarme"),
     "escolha": "o analisador cala quando nao consegue provar",
     "porque": "a calibragem e 0 erros em 222 arquivos bons. A superficie "
               "devolve 'aberta' — e o analisador volta a calar — quando o "
               "outro arquivo nao compila, quando ha ciclo, quando a "
               "profundidade acaba e quando o 'relay' nomeia algo que so "
               "existe em execucao",
     "custo": "silencios reais e listados. Foram 649 falsos alarmes num "
              "projeto de 252 arquivos quando a inferencia usou o escopo "
              "errado, e a suite passava",
     "onde": "dataforge/superficie.py — aberta"},

    {"entre": ("custo-zero", "depurabilidade"),
     "escolha": "o depurador desliga a compilacao de fechamentos",
     "porque": "ele para em cada linha sombreando 'execute', e o corpo "
               "compilado passa por fora. Um depurador que enxerga metade "
               "das instrucoes e pior que um interpretador mais lento",
     "custo": "depurar e mais lento que rodar, e as duas execucoes nao sao "
              "o mesmo caminho — ha teste rodando os dois modos",
     "onde": "dataforge/depurador.py — compilar_corpos = False"},

    {"entre": ("custo-zero", "correcao"),
     "escolha": "o escopo do laco NAO e reaproveitado quando o corpo captura",
     "porque": "sem isso, as tres closures de um laco de tres voltas veriam "
               "todas o ultimo valor — o classico que o Python tem e que "
               "aqui nao acontece. '_corpo_captura_escopo' varre a arvore "
               "inteira, e nao so as instrucoes: um 'lambda' vive dentro de "
               "uma expressao",
     "custo": "a otimizacao mais perigosa do interpretador: erra-la nao da "
              "erro, da resposta errada",
     "onde": "dataforge/interpreter.py — _corpo_captura_escopo"},

    {"entre": ("extensibilidade", "nomes-bons-para-quem-escreve"),
     "escolha": "palavra nova entra como contextual",
     "porque": "'route', 'render', 'server', 'agrupar' e 'ordenar' sao nomes "
               "bons demais para tirar de quem escreve. Cada uma vale so "
               "onde o que vem depois confirma, e sete palavras reservadas "
               "ja foram removidas por serem caras sem entregar nada",
     "custo": "o parser fica mais complicado, e a gramatica do editor "
              "precisa de duas travas para nao envelhecer",
     "onde": "dataforge/tokens.py — CONTEXTUAIS_*"},

    {"entre": ("runtime-modular", "zero-dependencia-externa"),
     "escolha": "zero dependencia, e o codigo escrito a mao",
     "porque": "ChaCha20-Poly1305 pelo RFC 8439, o '.xlsx', o WebSocket "
               "pelo RFC 6455 e os graficos em SVG. Uma biblioteca de CDN "
               "quebra qualquer app em rede fechada — que e onde painel de "
               "dados costuma rodar",
     "custo": "criptografia e formato de arquivo escritos aqui, com o risco "
              "que isso tem. Ha teste proibindo 'http://', 'https://' e "
              "'cdn' no CSS e no JS da Vitrine",
     "onde": "dataforge/stdlib/cifra.py — RFC 8439"},

    {"entre": ("portabilidade", "performance"),
     "escolha": "herdar a portabilidade do CPython",
     "porque": "e o que da Linux, macOS, Windows, ARM e ARM64 sem uma linha "
               "de codigo de arquitetura, e o que faz 'adopt Python.numpy' "
               "existir",
     "custo": "o teto. A compilacao de fechamentos da 1,5x a 1,8x medidos, "
              "e o teto dessa tecnica — e o de uma VM de bytecode escrita "
              "em Python — e ~6,5x: o resto exigiria sair do Python",
     "onde": "dataforge/compilador.py"},

    {"entre": ("controle-explicito-de-recursos", "seguranca-por-padrao"),
     "escolha": "o ponteiro cru existe, e e onde a protecao para",
     "porque": "FFI sem ponteiro nao e FFI. 'Arcane.C' recusa o nulo e "
               "confere o layout da struct contra a ABI, mas aritmetica de "
               "ponteiro e aritmetica de ponteiro",
     "custo": "um segmentation fault nao e um erro da linguagem: e o "
              "processo morrendo. A fronteira esta documentada em vez de "
              "fingida",
     "onde": "dataforge/stdlib/arcane_c.py"},

    {"entre": ("mensagem-util", "identidade-do-erro"),
     "escolha": "traduzir no DESENHO, nunca em 'error.message'",
     "porque": "'e.message' e o que um 'handle' compara e o que milhares de "
               "testes comparam. Traduzir ali mudaria o comportamento de "
               "programa ja escrito — e o que interessa a um programa e a "
               "identidade do erro, nao o idioma dele",
     "custo": "a camada de idioma precisa de um piso de cobertura, porque o "
              "que falta sai em ingles legivel: o fallback certo e tambem o "
              "que esconde o buraco",
     "onde": "dataforge/idioma.py"},
)


def principios():
    """Os dez, sem rodar prova nenhuma — o texto e os vereditos."""
    return [{k: v for k, v in p.items() if k != "prova"}
            for p in PRINCIPIOS]


def tensoes():
    """Onde dois principios se contradizem, e qual venceu."""
    return [dict(t) for t in TENSOES]


def conferir(nome=None):
    """Roda a prova de cada principio e devolve o que ela mediu.

    Com `nome`, so aquele. Duas provas rodam o analisador e uma roda o
    interpretador: e a diferenca entre afirmar um principio e
    demonstra-lo.
    """
    alvo = str(nome) if nome is not None else None
    quais = [p for p in PRINCIPIOS if alvo is None or p["principio"] == alvo]
    if alvo is not None and not quais:
        raise RuntimeError_(
            f"'{alvo}' is not a known principle. They are: "
            f"{', '.join(p['principio'] for p in PRINCIPIOS)}.",
            doc="ecossistema/principios")

    saida = []
    for p in quais:
        try:
            medido, como = p["prova"]()
        except Exception as erro:                  # pragma: no cover
            medido, como = f"a prova falhou: {erro}", ""
        saida.append({"numero": p["numero"], "principio": p["principio"],
                      "veredito": p["veredito"], "aqui": p["aqui"],
                      "no_documento": p["no_documento"],
                      "custo": p["custo"], "onde": list(p["onde"]),
                      "medido": medido, "como": como})
    return saida


def veredito():
    """A conta dos vereditos — e ela nao e dez de dez, de proposito."""
    conta = {v: 0 for v in VEREDITOS}
    for p in PRINCIPIOS:
        conta[p["veredito"]] += 1
    return {"total": len(PRINCIPIOS), **conta,
            "tensoes": len(TENSOES)}


def relatorio():
    """Os dez principios medidos, e as nove tensoes."""
    linhas = ["  os dez principios, medidos", ""]
    marca = {"cumprido": "+", "parcial": "~", "nao-se-aplica": "-"}
    for p in conferir():
        linhas.append(f"  [{marca[p['veredito']]}] {p['numero']:>2}. "
                      f"{p['principio']}  ({p['veredito']})")
        linhas.append(f"        medido: {p['medido']}")
        linhas.append(f"        custo:  {p['custo']}")
        linhas.append("")
    conta = veredito()
    linhas.append(f"  {conta['cumprido']} cumpridos, {conta['parcial']} "
                  f"parciais, {conta['nao-se-aplica']} nao se aplicam")
    linhas.append("")
    linhas.append("  as tensoes — onde dois principios se contradizem:")
    linhas.append("")
    for t in TENSOES:
        linhas.append(f"   {t['entre'][0]}  x  {t['entre'][1]}")
        linhas.append(f"      escolha: {t['escolha']}")
        linhas.append(f"      custo:   {t['custo']}")
        linhas.append(f"      onde:    {t['onde']}")
        linhas.append("")
    return "\n".join(linhas)


class ArcanePrincipios:
    """O dicionario que `adopt Arcane.Principios` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Principios",
            "principios": principios,
            "tensoes": tensoes,
            "conferir": conferir,
            "veredito": veredito,
            "relatorio": relatorio,
            "VEREDITOS": list(VEREDITOS),
        }
