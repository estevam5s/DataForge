# -*- coding: utf-8 -*-
"""Arcane.Ecossistema — o inventario da implementacao, conferido contra ela.

O que faltava
-------------
A referencia Deep Tech fecha com um desenho do ecossistema: `dfc` com
onze fases, `dfup`, `dfpm`, um runtime de seis pecas, sete ferramentas e
oito alvos. Um desenho desses e a coisa mais facil de escrever e a mais
facil de deixar envelhecer: ele nao roda, ninguem o executa, e no dia em
que uma peca muda de nome o mapa passa a mentir sem nada denunciar.

Este modulo e o desenho **conferido**. Cada componente aponta arquivos
de verdade, e `conferir()` cobra as duas direcoes:

* todo caminho citado no mapa **existe** no disco;
* todo modulo de `dataforge/` **aparece** em algum componente.

A segunda e a que importa. Sem ela, um modulo novo nasce fora do mapa e
o inventario fica incompleto em silencio — que e exatamente como a
tabela da biblioteca padrao ja divergiu em tres lugares.

Os tres estados, e o terceiro e o que vale
------------------------------------------
    existe       a peca esta aqui, com esse papel
    equivale     nao ha essa peca; ha outra que responde a MESMA
                 pergunta por outro mecanismo — nomeada, com o porque
    nao-existe   nao ha, e o porque esta escrito

`o_que_nao_existe()` e a lista mais util do modulo: ela e a resposta
honesta a "o DataForge tem um backend LLVM?" — e a resposta e nao, com
o que existe no lugar e o teto medido daquilo.

    adopt Arcane.Ecossistema as Eco

    out Eco.arvore()
    cycle f in Eco.o_que_nao_existe():
        out $"{f['no']}: {f['porque']}"
"""

import os

#: Os tres estados que um componente pode ter. A lista e fechada: um
#: quarto estado seria um lugar para esconder "mais ou menos".
ESTADOS = ("existe", "equivale", "nao-existe")

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

#: Arquivos de `dataforge/` que nao sao componente do ecossistema: a
#: arte da marca e os dois pontos de entrada. Sem esta lista, `conferir`
#: os acusaria de estarem fora do mapa, e um alarme falso todo dia
#: ensina a desligar a conferencia.
NAO_E_COMPONENTE = ("__init__.py", "__main__.py", "marca.py")

#: O mapa. Grupo -> componentes, na ordem do desenho do documento.
#:
#: `onde` e uma LISTA: uma peca do desenho quase nunca e um arquivo. O
#: lexer sao dois (`lexer.py` e `tokens.py`), e o verificador de tipos
#: sao quatro — separa-los seria fingir uma arrumacao que o codigo nao
#: tem.
ARVORE = (
    ("dfc — o compilador", (
        {"no": "Driver", "estado": "equivale",
         "onde": ("dataforge/cli.py", "dataforge/caminhos.py",
                  "dataforge/cache.py", "dataforge/completar.py"),
         "o_que_e": "o programa que recebe o arquivo e conduz as fases",
         "aqui": "nao ha um binario 'dfc' separado: o driver e o proprio "
                 "'dataforge', e cada fase tem um comando que a mostra "
                 "('tokens', 'ast', 'ir', 'percurso')",
         "porque": "um segundo executavel duplicaria a resolucao de "
                   "caminho e a leitura do forge.toml"},
        {"no": "Lexer", "estado": "existe",
         "onde": ("dataforge/lexer.py", "dataforge/tokens.py"),
         "o_que_e": "texto -> tokens, com INDENT/DEDENT e interpolacao",
         "aqui": "'tokenize()'; as 81 palavras reservadas vivem em KEYWORDS",
         "porque": ""},
        {"no": "Parser", "estado": "existe",
         "onde": ("dataforge/parser.py", "dataforge/gramatica.py"),
         "o_que_e": "tokens -> arvore, recursivo descendente",
         "aqui": "'parse()'; as palavras contextuais (Kiln, OOP, quadro) "
                 "sao reconhecidas aqui e nao em KEYWORDS",
         "porque": ""},
        {"no": "AST", "estado": "existe",
         "onde": ("dataforge/ast_nodes.py",),
         "o_que_e": "os nos da arvore",
         "aqui": "dataclasses com padroes; o interpretador despacha pelo "
                 "nome da classe",
         "porque": ""},
        {"no": "HIR", "estado": "existe",
         "onde": ("dataforge/hir.py",),
         "o_que_e": "a arvore depois do acucar sintatico",
         "aqui": "'normalizar()' abre 5 acucares; 8 construcoes NAO sao "
                 "acucar, e cada uma diz por que",
         "porque": ""},
        {"no": "Type Checker", "estado": "existe",
         "onde": ("dataforge/typechecker.py", "dataforge/diagnosticos.py",
                  "dataforge/tipos_nomeados.py",
                  "dataforge/colecoes_tipadas.py",
                  "dataforge/superficie.py", "dataforge/resolucao.py"),
         "o_que_e": "nomes, aridade, tipos, alcance",
         "aqui": "'check_program()'; atravessa arquivos pela superficie, e "
                 "e otimista de proposito — cala quando nao consegue provar",
         "porque": ""},
        {"no": "Borrow Checker", "estado": "equivale",
         "onde": ("dataforge/stdlib/arcane_posse.py",),
         "o_que_e": "provar, antes de rodar, que nenhuma referencia "
                    "sobrevive ao dono",
         "aqui": "'Arcane.Posse' da posse exclusiva, emprestimo com escopo "
                 "e contagem deterministica, e o 'check' acusa "
                 "'posse-movida', 'recurso-vazado' e 'emprestimo-escapa'",
         "porque": "num mundo com coletor, a integridade da memoria nunca "
                   "esteve em risco: o que se protege e o PROTOCOLO "
                   "(soltar uma vez, nao usar depois). Nao ha tempo de "
                   "vida declarado, e por isso nao e um borrow checker"},
        {"no": "MIR", "estado": "existe",
         "onde": ("dataforge/mir.py",),
         "o_que_e": "o grafo de fluxo: bloco basico e aresta rotulada",
         "aqui": "'construir()'; as arestas tem nome ('sim', 'nao', "
                 "'volta', 'halt', 'skip', 'erro', 'point', 'defer')",
         "porque": ""},
        {"no": "Dataflow Analyzer", "estado": "existe",
         "onde": ("dataforge/mir.py", "dataforge/ssa.py"),
         "o_que_e": "alcance, vivacidade, constantes, escapatoria",
         "aqui": "'alcancaveis', 'vivas', 'talvez_nao_definidas', "
                 "'constantes', 'escapam'; e SSA com nos phi e SCCP",
         "porque": ""},
        {"no": "LIR", "estado": "existe",
         "onde": ("dataforge/lir.py",),
         "o_que_e": "a ultima representacao antes de gerar codigo",
         "aqui": "'inventario()' diz o que o compilador de fechamentos "
                 "compilou e o que RECUOU para a arvore — que e o mapa "
                 "de onde o tempo vai",
         "porque": ""},
        {"no": "LLVM Backend", "estado": "nao-existe",
         "onde": ("dataforge/compilador.py", "dataforge/otimizar.py",
                  "dataforge/cauda.py"),
         "o_que_e": "emitir IR do LLVM e deixa-lo gerar codigo nativo",
         "aqui": "o backend e 'compilador.py': a arvore e percorrida uma "
                 "vez e vira fechamentos Python, o que tira o despacho do "
                 "caminho quente. Medido: 1,5x a 1,8x",
         "porque": "amarrar o LLVM tiraria a unica propriedade inegociavel "
                   "do projeto — zero dependencia externa no runtime. E o "
                   "teto desta tecnica, como o de uma VM de bytecode "
                   "escrita em Python, e ~6,5x: o resto exigiria sair do "
                   "Python, que e outra linguagem, nao outra fase"},
        {"no": "Code Generator", "estado": "nao-existe",
         "onde": (),
         "o_que_e": "emitir codigo de maquina",
         "aqui": "nao ha. O que sai do compilador e um fechamento, e quem "
                 "o executa e 'interpreter.py'",
         "porque": "sem backend nativo nao ha o que gerar. 'dataforge ir "
                   "--fase=lir' e onde isso fica visivel, e e de "
                   "proposito: a fase existe no mapa para que a ausencia "
                   "tenha lugar"},
    )),
    ("dfup — versoes", (
        {"no": "Version Manager", "estado": "existe",
         "onde": ("dataforge/versoes.py", "scripts/instalar.sh",
                  "scripts/instalar.ps1"),
         "o_que_e": "instalar, alternar e fixar versoes lado a lado",
         "aqui": "uma venv por versao em '~/.dataforge/versoes/<versao>'; "
                 "'versions' lista, 'use' fixa (no forge.toml, ou global com "
                 "'--global'), 'upgrade' instala ao lado. E o pino e "
                 "COBRADO: 'run' num projeto que exige outra versao entrega "
                 "a execucao a ela",
         "porque": "o limite: nao ha um 'shim' no PATH. O 'dataforge' que "
                   "se chama e o que esta instalado, e e ele que "
                   "redireciona — com 'DATAFORGE_SEM_TROCA=1' para "
                   "ignorar o pino uma vez"},
    )),
    ("dfpm — pacotes", (
        {"no": "Package Manager", "estado": "existe",
         "onde": ("dataforge/packages.py", "dataforge/registro_remoto.py"),
         "o_que_e": "resolver, baixar, instalar, empacotar, publicar",
         "aqui": "10 comandos; o registro e ESTATICO — uma pasta com "
                 "'index.json' servida por qualquer host, sem servidor a "
                 "manter",
         "porque": ""},
        {"no": "Dependency Resolver", "estado": "existe",
         "onde": ("dataforge/packages.py",),
         "o_que_e": "semver, faixas e trava",
         "aqui": "'resolver()' com '^', '~' e '>='; conflito de versao e "
                 "ERRO, nao aviso, e a mensagem diz quem pediu o que",
         "porque": ""},
        {"no": "Build System", "estado": "equivale",
         "onde": ("dataforge/project.py", "dataforge/devops.py",
                  "dataforge/devops_cli.py"),
         "o_que_e": "compilar o projeto e suas dependencias num artefato",
         "aqui": "'forge.toml' descreve o projeto e 'dataforge devops' "
                 "gera Dockerfile, compose, CI, manifestos e SBOM",
         "porque": "nao havendo compilacao para binario, nao ha etapa de "
                   "build a orquestrar: o artefato e o codigo mais o "
                   "'forge.lock'"},
        {"no": "Workspace Manager", "estado": "existe",
         "onde": ("dataforge/versoes.py", "dataforge/modelos.py",
                  "dataforge/scaffold.py"),
         "o_que_e": "varios pacotes num repositorio, vistos de uma vez",
         "aqui": "'dataforge workspace' acha todo 'forge.toml' da arvore, "
                 "lista os pacotes e ACUSA faixa incompativel do mesmo "
                 "terceiro — a interseccao sai da mesma classe que o "
                 "'resolver' usa. Sai com 2 quando ha conflito",
         "porque": "ele LE e relata: nao instala. Instalar a arvore inteira "
                   "de um comando que a pessoa rodou para 'ver o que tem' "
                   "seria mexer em disco sem ser pedido"},
    )),
    ("Runtime", (
        {"no": "Execution Engine", "estado": "existe",
         "onde": ("dataforge/interpreter.py", "dataforge/environment.py",
                  "dataforge/builtins.py", "dataforge/objetos.py",
                  "dataforge/magicos.py"),
         "o_que_e": "quem executa de fato",
         "aqui": "interpretador de arvore, com despacho por classe e "
                 "corpos compilados em fechamento",
         "porque": "o desenho do documento nao tem esta peca porque supoe "
                   "compilacao antecipada — aqui ela e o centro"},
        {"no": "Allocator", "estado": "nao-existe",
         "onde": ("dataforge/stdlib/arcane_memoria.py",),
         "o_que_e": "um alocador proprio, com arena, pool e estrategia "
                    "escolhida por quem escreve",
         "aqui": "o alocador e o do CPython. 'Arcane.Memoria' da arena, "
                 "referencia fraca, mapa fraco e controle do coletor "
                 "(ligar, desligar, limiares, congelar)",
         "porque": "trocar o alocador exigiria estar do lado de fora do "
                   "CPython. O que se pode fazer daqui — e se faz — e "
                   "mandar no COLETOR e medir a pausa dele"},
        {"no": "Scheduler", "estado": "existe",
         "onde": ("dataforge/stdlib/arcane_laco.py",),
         "o_que_e": "decidir quem roda agora",
         "aqui": "fila de prontas, monte de temporizadores e selector; "
                 "'Fibra' para corrotina com ceder explicito",
         "porque": ""},
        {"no": "Async Runtime", "estado": "existe",
         "onde": ("dataforge/stdlib/arcane_laco.py",
                  "dataforge/stdlib/arcane_paralelo.py"),
         "o_que_e": "'async'/'await' com sobreposicao de entrada e saida",
         "aqui": "chamar acao 'async' comeca o trabalho numa thread e "
                 "devolve tarefa; 'await' espera",
         "porque": "trabalho de CPU nao se sobrepoe: o GIL continua no "
                   "caminho, e a resposta ali e 'P.map_processos'"},
        {"no": "Event Loop", "estado": "existe",
         "onde": ("dataforge/stdlib/arcane_laco.py",),
         "o_que_e": "um laco que espera em soquete e temporizador",
         "aqui": "'Laco' com acordar por socketpair; medido ~1,1x o tempo "
                 "da versao com threads na carga de entrada e saida",
         "porque": ""},
        {"no": "Thread Runtime", "estado": "existe",
         "onde": ("dataforge/travessia.py",
                  "dataforge/stdlib/arcane_paralelo.py"),
         "o_que_e": "threads, e mais de um nucleo",
         "aqui": "'thread'/'parallel' para entrada e saida; para CPU, "
                 "'travessia.py' copia a DECLARACAO da acao para outro "
                 "processo. Medido: 3,45x em 10 nucleos",
         "porque": ""},
        {"no": "Error Runtime", "estado": "existe",
         "onde": ("dataforge/errors.py", "dataforge/catalogo_erros.py",
                  "dataforge/idioma.py", "dataforge/docs_links.py",
                  "dataforge/cauda.py"),
         "o_que_e": "levantar, propagar, desenhar",
         "aqui": "177 codigos, o trecho desenhado com a seta, 'doc=' "
                 "apontando a rota da documentacao, e o runtime falando "
                 "portugues ('DF_IDIOMA=en' volta ao ingles)",
         "porque": ""},
        {"no": "Bare-Metal Runtime", "estado": "nao-existe",
         "onde": (),
         "o_que_e": "rodar sem sistema operacional",
         "aqui": "nao ha, e nao ha caminho a partir daqui: o runtime e o "
                 "CPython",
         "porque": "'Arcane.Alvo' nomeia 'embarcado' com o que falta em "
                   "cada capacidade, justamente para que a ausencia "
                   "apareca antes de alguem tentar"},
    )),
    ("Tooling", (
        {"no": "LSP", "estado": "existe",
         "onde": ("dataforge/lsp.py",),
         "o_que_e": "hover, completar, ir-para, diagnostico no editor",
         "aqui": "'dataforge lsp'; a extensao do VS Code o instala",
         "porque": ""},
        {"no": "Debugger", "estado": "existe",
         "onde": ("dataforge/depurador.py", "dataforge/dap.py"),
         "o_que_e": "parar, olhar, andar",
         "aqui": "'debug' no terminal (serve por ssh) e 'dap' no painel "
                 "do editor, com vigia de valor",
         "porque": "e a peca que o desenho do documento nao lista, e a "
                   "que mais se usa"},
        {"no": "Formatter", "estado": "existe",
         "onde": ("dataforge/formatter.py",),
         "o_que_e": "formatar",
         "aqui": "'dataforge fmt'; idempotente, com teste cobrando isso",
         "porque": ""},
        {"no": "Linter", "estado": "existe",
         "onde": ("dataforge/linter.py",),
         "o_que_e": "estilo e higiene",
         "aqui": "'dataforge lint', com '// df: permitir <regra>' para "
                 "silenciar uma regra NOMEADA",
         "porque": ""},
        {"no": "Test Runner", "estado": "existe",
         "onde": ("dataforge/testrunner.py", "dataforge/cobertura.py"),
         "o_que_e": "descobrir e rodar testes, com cobertura",
         "aqui": "'dataforge test --cobertura --minimo=80'; o denominador "
                 "sai do parser e o numerador de 'execute' sombreado",
         "porque": ""},
        {"no": "Benchmark Runner", "estado": "existe",
         "onde": ("dataforge/stdlib/arcane_bench.py",
                  "dataforge/complexidade.py"),
         "o_que_e": "medir, e classificar a curva",
         "aqui": "'dataforge bench' mede e 'dataforge big-o' LE a "
                 "complexidade da arvore — as duas erram de formas "
                 "opostas, e por isso existem as duas",
         "porque": ""},
        {"no": "Profiler", "estado": "existe",
         "onde": ("dataforge/stdlib/arcane_perfil.py",),
         "o_que_e": "onde o tempo vai",
         "aqui": "'dataforge profile' mostra tempo PROPRIO por acao; "
                 "'Arcane.Perfil' tem percentis, flame graph em SVG, "
                 "pausas do coletor e Mann-Whitney para dizer se a "
                 "diferenca e real",
         "porque": ""},
        {"no": "Documentation Generator", "estado": "existe",
         "onde": ("dataforge/docgen.py", "dataforge/exemplos_palavras.py",
                  "dataforge/oop_analise.py", "dataforge/repl.py",
                  "dataforge/migrar.py", "dataforge/migrar_js.py",
                  "dataforge/vitrine_cli.py",
                  "dataforge/telegram_cli.py"),
         "o_que_e": "Markdown a partir dos comentarios",
         "aqui": "'dataforge doc'; e ao lado dele o REPL, as metricas CK "
                 "do 'oop', os conversores e as CLIs da Vitrine e do "
                 "Telegram",
         "porque": ""},
    )),
    ("Interoperabilidade", (
        {"no": "FFI / C", "estado": "existe",
         "onde": ("dataforge/stdlib/arcane_c.py",),
         "o_que_e": "chamar biblioteca nativa",
         "aqui": "'Arcane.C': biblioteca, ponteiro cru, struct conferida "
                 "contra a ABI, callback — o 'qsort' do C chamando uma "
                 "acao DataForge",
         "porque": ""},
        {"no": "Ponte para o Python", "estado": "existe",
         "onde": ("dataforge/ponte.py",),
         "o_que_e": "'adopt Python.numpy as np'",
         "aqui": "a ponte NAO converte: um 'ndarray' continua um "
                 "'ndarray', e isso so funciona porque o interpretador "
                 "trata objeto estranho por protocolo",
         "porque": ""},
        {"no": "Hardware e IoT", "estado": "existe",
         "onde": ("dataforge/stdlib/arcane_iot.py",
                  "dataforge/stdlib/iot_serial.py",
                  "dataforge/stdlib/iot_firmata.py",
                  "dataforge/stdlib/iot_simulador.py",
                  "dataforge/stdlib/iot_mqtt.py",
                  "dataforge/iot_cli.py"),
         "o_que_e": "falar com uma placa fisica",
         "aqui": "porta serial escrita aqui (termios e a API do Windows, "
                 "sem pyserial), Firmata 2.x completo, MQTT 3.1.1 falado a "
                 "mao, e um simulador de placa que fala os MESMOS bytes — "
                 "e o que torna testavel um programa de hardware",
         "porque": ""},
        {"no": "ABI e simbolos", "estado": "equivale",
         "onde": ("dataforge/stdlib/arcane_abi.py",),
         "o_que_e": "layout binario, ligador e mapa de simbolos",
         "aqui": "nao ha layout a quebrar; ha o mesmo PROBLEMA com outro "
                 "nome — 'Arcane.Abi' compara duas versoes de um modulo e "
                 "diz qual bump de semver a mudanca exige",
         "porque": "o sintoma e identico: nao e erro de quem publicou, e "
                   "de quem consome, depois"},
    )),
    ("Alvos", (
        {"no": "Linux, macOS, Windows", "estado": "existe",
         "onde": ("scripts/instalar.sh", "scripts/instalar.ps1",
                  "Dockerfile"),
         "o_que_e": "os tres sistemas de mesa e servidor",
         "aqui": "o release constroi nas quatro plataformas (Linux, macOS "
                 "Intel, macOS ARM, Windows) e roda exemplos e exercicios "
                 "PELO BINARIO",
         "porque": ""},
        {"no": "ARM, ARM64", "estado": "existe",
         "onde": (".github/workflows/release.yml",),
         "o_que_e": "as arquiteturas do Apple Silicon e dos servidores ARM",
         "aqui": "o macOS ARM e construido e testado a cada tag; onde o "
                 "CPython roda, o DataForge roda",
         "porque": ""},
        {"no": "RISC-V", "estado": "equivale",
         "onde": (),
         "o_que_e": "a arquitetura aberta",
         "aqui": "nao ha nada de arquitetura no projeto: se ha CPython "
                 "3.10+, roda. Nao e testado, e dizer 'suportado' seria "
                 "prometer o que ninguem verificou",
         "porque": "a portabilidade aqui e herdada, nao construida — o que "
                   "e uma vantagem e um limite ao mesmo tempo"},
        {"no": "WASM", "estado": "equivale",
         "onde": ("dataforge/stdlib/arcane_alvo.py",),
         "o_que_e": "compilar para WebAssembly",
         "aqui": "COMPILAR para WASM nao existe. RODAR em WASM funciona, "
                 "pelo Pyodide — com o interpretador inteiro junto",
         "porque": "sao duas frases diferentes, e confundi-las e a maneira "
                   "mais rapida de prometer um alvo que nao se entrega"},
        {"no": "Bare-Metal", "estado": "nao-existe",
         "onde": ("dataforge/stdlib/arcane_iot.py",),
         "o_que_e": "sem sistema operacional",
         "aqui": "o interpretador nao roda na placa, e nao ha caminho "
                 "para isso. O que ha e outra coisa, e ela e real: "
                 "'Arcane.IoT' CONTROLA a placa pelo cabo (Firmata) e "
                 "GERA o C++ que roda nela — o codigo do metal existe, "
                 "so nao e DataForge",
         "porque": "exigiria outro runtime inteiro; 'Arcane.Alvo' diz o "
                   "que falta em cada capacidade do alvo 'embarcado'"},
    )),
)


def _nos():
    for grupo, nos in ARVORE:
        for no in nos:
            yield grupo, no


def componentes():
    """Todo componente, com o grupo, o estado e se os arquivos existem."""
    saida = []
    for grupo, no in _nos():
        onde = list(no["onde"])
        saida.append({
            "grupo": grupo,
            "no": no["no"],
            "estado": no["estado"],
            "o_que_e": no["o_que_e"],
            "aqui": no["aqui"],
            "porque": no["porque"],
            "onde": onde,
            "no_disco": [c for c in onde
                         if os.path.isfile(os.path.join(_RAIZ, c))],
        })
    return saida


def grupos():
    """Os grupos do desenho, na ordem, com quantos componentes cada um."""
    return [{"grupo": g, "componentes": len(n),
             "existem": len([x for x in n if x["estado"] == "existe"])}
            for g, n in ARVORE]


def o_que_nao_existe():
    """O que NAO existe, com o porque. A lista mais util do modulo."""
    return [c for c in componentes() if c["estado"] == "nao-existe"]


def equivalencias():
    """O que existe por outro mecanismo, com o nome do que esta no lugar."""
    return [c for c in componentes() if c["estado"] == "equivale"]


def numeros():
    """As contagens, derivadas — nenhuma escrita a mao.

    A contagem de simbolos sai do MESMO levantamento que gera a pagina
    da biblioteca: uma soma propria sobre `DESCRICOES` ja divergiu dela
    em 112 simbolos, e o numero errado foi publicado.
    """
    from .catalogo import DESCRICOES
    from . import get_module, list_modules

    oficiais = sorted({n for n in list_modules() if n.startswith("Arcane.")}
                      | {n for n in DESCRICOES if n.startswith("Arcane.")})
    simbolos = 0
    contados = set()
    for nome in oficiais:
        modulo = get_module(nome)
        if modulo is None:
            continue
        oficial = modulo.get("__name__", nome)
        if oficial in contados:
            continue
        contados.add(oficial)
        simbolos += len([k for k in modulo if not k.startswith("__")])

    from ..cli import GRUPOS
    from .arcane_alvo import ALVOS

    nucleo = [f for f in sorted(os.listdir(os.path.join(_RAIZ, "dataforge")))
              if f.endswith(".py")]
    return {
        "modulos": len(contados),
        "simbolos": simbolos,
        "comandos": sum(len(lista) for _, lista in GRUPOS),
        "grupos_de_comando": len(GRUPOS),
        "alvos": len(ALVOS),
        "modulos_do_nucleo": len(nucleo),
        "componentes": len(list(_nos())),
        "existem": len([c for c in componentes() if c["estado"] == "existe"]),
        "equivalem": len(equivalencias()),
        "nao_existem": len(o_que_nao_existe()),
    }


def conferir():
    """O mapa bate com o disco? Nas duas direcoes.

    * `faltando` — caminho citado que nao existe mais
    * `orfaos`   — modulo de `dataforge/` que nao aparece em componente
                   nenhum

    A segunda e a que impede o inventario de ficar incompleto em
    silencio quando um modulo novo nasce.
    """
    faltando = []
    citados = set()
    for grupo, no in _nos():
        for caminho in no["onde"]:
            citados.add(caminho)
            if not os.path.exists(os.path.join(_RAIZ, caminho)):
                faltando.append({"no": no["no"], "grupo": grupo,
                                 "onde": caminho})

    nucleo = {f for f in os.listdir(os.path.join(_RAIZ, "dataforge"))
              if f.endswith(".py")} - set(NAO_E_COMPONENTE)
    nomeados = {os.path.basename(c) for c in citados
                if c.startswith("dataforge/") and "/stdlib/" not in c}
    orfaos = sorted(nucleo - nomeados)

    return {"ok": not faltando and not orfaos,
            "faltando": faltando, "orfaos": orfaos,
            "citados": len(citados)}


_MARCAS = {"existe": "+", "equivale": "~", "nao-existe": "-"}


def arvore():
    """O desenho, com uma marca por estado. `-` e o que nao existe."""
    linhas = ["DataForge — o ecossistema, conferido", "│"]
    grupos_lista = list(ARVORE)
    for i, (grupo, nos) in enumerate(grupos_lista):
        ultimo_grupo = i == len(grupos_lista) - 1
        linhas.append(f"{'└' if ultimo_grupo else '├'}── {grupo}")
        prefixo = "    " if ultimo_grupo else "│   "
        for j, no in enumerate(nos):
            ultimo = j == len(nos) - 1
            marca = _MARCAS[no["estado"]]
            linhas.append(f"{prefixo}{'└' if ultimo else '├'}── "
                          f"[{marca}] {no['no']}")
        if not ultimo_grupo:
            linhas.append("│")
    linhas.append("")
    linhas.append("  [+] existe   [~] equivale, por outro mecanismo   "
                  "[-] nao existe")
    return "\n".join(linhas)


def relatorio():
    """O inventario escrito: os numeros, o desenho e as ausencias."""
    n = numeros()
    linhas = [arvore(), "",
              f"  {n['componentes']} componentes: {n['existem']} existem, "
              f"{n['equivalem']} equivalem, {n['nao_existem']} nao existem",
              f"  {n['modulos']} modulos da biblioteca, {n['simbolos']} "
              f"simbolos, {n['comandos']} comandos, {n['alvos']} alvos",
              f"  {n['modulos_do_nucleo']} modulos no nucleo "
              f"('dataforge/*.py')", ""]
    linhas.append("  o que NAO existe, e por que:")
    for c in o_que_nao_existe():
        linhas.append(f"   {c['no']}")
        linhas.append(f"      no lugar:  {c['aqui']}")
        linhas.append(f"      porque:    {c['porque']}")
    conf = conferir()
    linhas.append("")
    if conf["ok"]:
        linhas.append(f"  o mapa bate com o disco ({conf['citados']} "
                      f"caminhos conferidos)")
    else:
        for f in conf["faltando"]:
            linhas.append(f"  FALTA no disco: {f['onde']} (em {f['no']})")
        for o in conf["orfaos"]:
            linhas.append(f"  FORA do mapa: dataforge/{o}")
    return "\n".join(linhas)


# ═══════════════════════════════════════════════════════════
#  Glossario
# ═══════════════════════════════════════════════════════════

#: (termo, definicao, pagina). A pagina e CONFERIDA contra o site por
#: um teste: um glossario que manda para 404 ensina a nao clicar — e o
#: roadmap ja teve oito passos assim.
GLOSSARIO = (
    ("ABI", "a superficie binaria e de chamada de um modulo; aqui, a "
     "superficie do que o 'relay' exporta, comparada entre versoes",
     "/docs/abi"),
    ("agregado", "a unica porta de escrita de um grupo de objetos do "
     "dominio, onde as invariantes sao cobradas", "/docs/dominio/agregados"),
    ("alinhamento", "o multiplo de endereco em que um campo binario "
     "comeca; o que sobra entre campos e o enchimento",
     "/docs/estruturas/alinhamento"),
    ("analisador", "o 'dataforge check': acha erro antes de rodar, e cala "
     "quando nao consegue provar", "/docs/compilador/analisador"),
    ("ator", "um estado com dono, alcancado so por mensagem, tratado uma "
     "de cada vez numa thread propria", "/docs/concorrencia/atores"),
    ("bloco basico", "instrucoes que rodam sempre juntas, sem desvio no "
     "meio; os nos do grafo de fluxo", "/docs/compilador/mir"),
    ("canal", "o cano entre fibras (ou threads) que suspende quem envia "
     "quando cheio: contrapressao de graca", "/docs/runtime/canais"),
    ("chamada de cauda", "'yield f(...)' como retorno inteiro: vira salto, "
     "e a recursao perde o teto", "/docs/compilador/cauda"),
    ("contrapressao", "o consumidor mais lento freando o produtor, em vez "
     "de a fila crescer sem fim", "/docs/runtime/contrapressao"),
    ("CQRS", "separar o modelo que decide do modelo que responde "
     "consultas", "/docs/dominio/cqrs"),
    ("CRC-32", "a conferencia de 32 bits do PNG, do ZIP e do gzip: pega "
     "erro de transmissao, nao adulteracao", "/docs/estruturas/conferencia"),
    ("cursor", "a posicao opaca de 'onde parou' numa listagem, que nao "
     "pula nem repete quando a lista muda", "/docs/api/paginacao"),
    ("derivado", "um valor calculado de sinais, recalculado so quando uma "
     "fonte lida muda", "/docs/reativo/sinais"),
    ("dominancia", "A domina B quando todo caminho ate B passa por A; "
     "decide onde vao os phi", "/docs/compilador/dominancia"),
    ("efeito", "a acao reativa que roda quando o que ela leu muda",
     "/docs/reativo/efeitos"),
    ("ETag", "a etiqueta de uma versao de recurso HTTP; forte, ela sustenta "
     "o If-Match", "/docs/api/precondicoes"),
    ("fibra", "um 'stream action' conduzido pelo laco de eventos: cede o "
     "controle em cada 'emit'", "/docs/runtime/fibras"),
    ("fonte de eventos", "guardar os fatos, e nao o estado; o estado e "
     "derivado deles", "/docs/dominio/fonte-de-eventos"),
    ("idempotencia", "repetir o pedido nao repete o efeito; a chave que "
     "impede a cobranca dupla", "/docs/api/idempotencia"),
    ("invariante", "o que precisa ser verdade sempre, cobrado na saida de "
     "cada comando", "/docs/dominio/agregados"),
    ("janela", "a leitura e escrita no lugar de um registro binario, sem "
     "copiar", "/docs/estruturas/janelas"),
    ("laco de eventos", "uma thread dormindo no seletor ate haver E/S, prazo "
     "ou tarefa: milhares de conexoes numa thread", "/docs/runtime/laco"),
    ("lexer", "a fase que transforma texto em tokens com linha e coluna",
     "/docs/compilador/lexer"),
    ("MIR", "o grafo de fluxo: blocos basicos e arestas rotuladas",
     "/docs/compilador/mir"),
    ("molde", "a descricao de um registro binario: campos, ordem dos bytes "
     "e alinhamento", "/docs/estruturas"),
    ("orcamento de erro", "as falhas que o objetivo do SLO permite; o que "
     "decide se da para arriscar", "/docs/observabilidade/slo"),
    ("ordem dos bytes", "big-endian (rede) ou little-endian (Intel): o "
     "mesmo numero em duas ordens", "/docs/estruturas/ordem-dos-bytes"),
    ("problema (RFC 9457)", "o erro HTTP que um programa le: type, title, "
     "status, detail", "/docs/api/problemas"),
    ("projecao", "um modelo de leitura montado dos eventos, idempotente pela "
     "posicao", "/docs/dominio/projecoes"),
    ("recurso", "um valor buscado fora, com o estado carregando, pronto ou "
     "erro, e a resposta velha descartada", "/docs/reativo/recursos"),
    ("sinal", "um valor que sabe quem depende dele", "/docs/reativo/sinais"),
    ("SLO", "o objetivo de nivel de servico: quanto do tempo o servico "
     "precisa estar certo", "/docs/observabilidade/slo"),
    ("SSA", "a forma em que cada nome recebe valor uma vez so, com phi nas "
     "juncoes", "/docs/compilador/ssa"),
    ("STM", "memoria transacional: escritas que acontecem juntas, ou nao "
     "acontecem", "/docs/concorrencia/stm"),
    ("superficie", "o que um modulo exporta com 'relay': o contrato com "
     "quem o adota", "/docs/abi/superficie"),
    ("taxa de queima", "quantas vezes mais rapido que o sustentavel o "
     "orcamento de erro esta sendo gasto", "/docs/observabilidade/slo"),
    ("varint", "o inteiro de tamanho variavel do protobuf: 7 bits por byte",
     "/docs/estruturas/varint"),
    ("versao esperada", "a versao lida quando o comando foi decidido; "
     "gravar sobre outra e recusado", "/docs/dominio/concorrencia-otimista"),
)


def glossario():
    """Os termos, com a definicao e a pagina que os explica."""
    return [{"termo": t, "definicao": d, "pagina": p} for t, d, p in GLOSSARIO]


def definir(termo):
    """A definicao de um termo — com sugestao quando o nome nao casa."""
    import difflib
    chave = str(termo).strip().lower()
    for t, d, p in GLOSSARIO:
        if t.lower() == chave:
            return {"termo": t, "definicao": d, "pagina": p}
    nomes = [t for t, _d, _p in GLOSSARIO]
    parecido = difflib.get_close_matches(str(termo), nomes, 1, 0.6)
    from ..errors import RuntimeError_
    raise RuntimeError_(
        f"'{termo}' nao esta no glossario.", 0, 0,
        dica=(f"voce quis dizer '{parecido[0]}'?" if parecido else
              "Ecossistema.glossario() lista todos"),
        doc="ecossistema/glossario")


class ArcaneEcossistema:
    """O dicionario que `adopt Arcane.Ecossistema` entrega."""

    def __new__(cls):
        return {
            "__name__": "Arcane.Ecossistema",
            "componentes": componentes,
            "grupos": grupos,
            "o_que_nao_existe": o_que_nao_existe,
            "equivalencias": equivalencias,
            "numeros": numeros,
            "conferir": conferir,
            "arvore": arvore,
            "relatorio": relatorio,
            "ESTADOS": list(ESTADOS),
            "glossario": glossario,
            "definir": definir,
        }
