# -*- coding: utf-8 -*-
"""'dataforge desktop' e 'dataforge mobile' — o programa vira aplicativo.

    dataforge desktop novo        um esqueleto de aplicacao de mesa
    dataforge desktop rodar app.df    abre a janela
    dataforge desktop empacotar app.df    .app, .exe ou binario
    dataforge desktop doctor      o que falta para empacotar aqui

    dataforge mobile novo         um esqueleto de aplicativo (Brasa)
    dataforge mobile rodar src/main.df   sobe na rede local
    dataforge mobile pwa app.df   gera o app instalavel no Android
    dataforge mobile doctor       o que existe e o que NAO existe

O que este comando faz, e o que ele delega
-------------------------------------------
Ele **gera** o icone, o manifesto e o arquivo de especificacao, e
chama o **PyInstaller** para montar o executavel — a mesma escolha do
`iot carregar`, que chama o arduino-cli. Empacotar um interpretador
Python num executavel e um problema resolvido, e resolve-lo de novo
daria um subconjunto pior amarrado a esta linguagem.

E sobre Android, a frase que este arquivo existe para nao deixar
ninguem inventar: **nao ha APK**. O caminho que funciona e o PWA — uma
aplicacao Vitrine servida por HTTPS, que o Android instala na tela
inicial, roda em tela cheia e abre sem navegador visivel. Ela nao e um
app nativo, e a pagina `mobile doctor` diz exatamente o que isso
custa.
"""

import json
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))


def color(texto, codigo):
    from .cli import color as _color
    return _color(texto, codigo)


def _valor(argumentos, flags, nome, padrao=None):
    for a in list(argumentos or []) + list(flags or []):
        if a.startswith(f"--{nome}="):
            return a.split("=", 1)[1]
    return padrao


def _tem(argumentos, flags, nome):
    return f"--{nome}" in (list(argumentos or []) + list(flags or []))


# ═══════════════════════════════════════════════════════════
#  Modelos
# ═══════════════════════════════════════════════════════════

MODELO_TELA = '''// {nome} — a aplicação, montada. Este arquivo NÃO abre a janela.
//
// Quem abre é o 'main.df'. É a separação do Kiln ('server' monta,
// 'ignite' sobe), e pela mesma razão: um teste que importasse este
// módulo abriria a janela e nunca terminaria.
//
// A forma é a da Vitrine: cada tela roda de novo a cada interação, e o
// estado sobrevive. Um clique, um item de menu e um atalho são EVENTOS
// — valem para uma execução só.

adopt Arcane.Bigorna as B

itens := []

app := B.app("{nome}", largura := 900, altura := 600)

app.menu("Arquivo", [
    B.item("Novo item", "novo", atalho := "Ctrl+N"),
    B.separador(),
    B.item("Exportar CSV…", "exportar", atalho := "Ctrl+E"),
])

action lista(t):
    t.titulo("{nome}")
    escolhido := t.tabela(["nome", "qtd"], itens, selecionar := yes)
    t.status($"{{len(itens)}} item(ns)")

    given t.comando("novo") or t.botao("Novo item", yes):
        t.ir("novo")

    given escolhido isnt void:
        t.texto($"selecionado: {{escolhido["nome"]}}")
        given t.botao("Excluir") and t.confirmar($"Excluir {{escolhido["nome"]}}?"):
            itens.remove(escolhido)
            t.notificar("excluído")
            t.atualizar()

    given t.comando("exportar"):
        caminho := t.salvar_arquivo("itens.csv", ["csv"])
        given caminho isnt void:
            t.guardar_pref("ultimo_export", caminho)
            t.notificar($"exportado: {{caminho}}")

action novo(t):
    t.titulo("Novo item")
    nome := t.entrada("Nome")
    qtd := t.numero("Quantidade", 1)
    given t.botao("Salvar", yes):
        given nome is "":
            t.erro("o nome é obrigatório")
        otherwise:
            itens.append({{"nome": nome, "qtd": qtd}})
            t.voltar()
    given t.botao("Cancelar"):
        t.voltar()

app.tela("lista", lista)
app.tela("novo", novo)

action limpar_tudo():
    itens.clear()

relay app, limpar_tudo
'''

MODELO_APP = '''// {nome} — o programa que abre a janela.

adopt Arcane.Bigorna as B
adopt ./tela as Tela

// Sem display (num servidor, num contêiner, no CI), abrir levantaria.
// Perguntar antes é o que faz o mesmo arquivo rodar nos dois lugares.
given B.tem_display():
    B.rodar(Tela.app)
otherwise:
    out "sem display — rode 'dataforge test' para exercitar a aplicação"
'''

MODELO_TESTE = '''// A aplicação inteira, testada sem abrir janela nenhuma.
//
// A Sonda clica, digita, abre menu, aperta atalho e responde diálogo —
// mas só o que o teste ROTEIRIZOU: uma tela que pede confirmação sem
// resposta combinada falha, em vez de receber um "sim" inventado.

adopt Arcane.Bigorna as B
adopt Arcane.Crucible as Crucible
adopt ../src/tela as Tela

crucible "a aplicacao":

    trial "o atalho abre o formulario":
        Tela.limpar_tudo()
        s := B.testar(Tela.app)
        s.atalho("Ctrl+N")
        expect s.tela_atual() is "novo"

    trial "salvar volta para a lista":
        Tela.limpar_tudo()
        s := B.testar(Tela.app)
        s.menu("Arquivo", "Novo item")
        s.digitar("Nome", "café")
        s.clicar("Salvar")
        expect s.tela_atual() is "lista"
        expect s.status() is "1 item(ns)"

    trial "o nome vazio e recusado":
        Tela.limpar_tudo()
        s := B.testar(Tela.app)
        s.atalho("Ctrl+N")
        s.clicar("Salvar")
        expect s.tem("o nome é obrigatório") is yes

    trial "excluir pede confirmacao":
        Tela.limpar_tudo()
        s := B.testar(Tela.app)
        s.atalho("Ctrl+N")
        s.digitar("Nome", "café")
        s.clicar("Salvar")
        s.selecionar(0)
        s.responder(yes)
        s.clicar("Excluir")
        expect s.status() is "0 item(ns)"

Crucible.run()
'''

MODELO_MOBILE_APP = '''// {nome} — o aplicativo, montado. Este arquivo NÃO sobe o servidor.
//
// Por baixo é a Vitrine: cada tela roda de novo a cada toque, e o
// estado sobrevive por sessão. A Brasa acrescenta a barra de abas, o
// topo com voltar, a lista tocável e o PWA que o celular instala.

adopt Arcane.Brasa as Br
adopt Arcane.Vitrine as V

tarefas := [{{"id": 1, "titulo": "Primeira tarefa", "feita": no}}]

app := Br.app("{nome}", cor := "#E8453C", descricao := "{nome}, no celular")

action inicio():
    Br.topo("{nome}")
    pendentes := [t cycle t in tarefas given not t["feita"]]
    given len(pendentes) is 0:
        Br.vazio("Nada pendente", "toque em + para criar uma tarefa")
    otherwise:
        Br.lista(pendentes, titulo := "titulo", destino := "/tarefa?id={{id}}")
    Br.botao_flutuante("Nova tarefa", "/nova")

action tarefa():
    id := int(V.parametro("id", "0"))
    achadas := [t cycle t in tarefas given t["id"] is id]
    Br.topo("Tarefa", voltar := yes)
    given len(achadas) is 0:
        Br.vazio("Tarefa não encontrada")
        V.parar()
    t := achadas[0]
    V.subtitulo(t["titulo"])
    given V.botao("Concluir"):
        t["feita"] := yes
        V.navegar("/")
    Br.compartilhar($"Tarefa: {{t["titulo"]}}")

action nova():
    Br.topo("Nova tarefa", voltar := yes)
    titulo := V.entrada("Título")
    given V.botao("Salvar"):
        given titulo is "":
            V.erro("o título é obrigatório")
        otherwise:
            tarefas.append({{"id": len(tarefas) + 1, "titulo": titulo, "feita": no}})
            V.navegar("/")

action feitas():
    Br.topo("Feitas")
    Br.lista([t cycle t in tarefas given t["feita"]], titulo := "titulo")

Br.tela("/", inicio, titulo := "Tarefas", icone := "conferir", aba := yes)
Br.tela("/feitas", feitas, titulo := "Feitas", icone := "estrela", aba := yes)
Br.tela("/tarefa", tarefa, titulo := "Tarefa")
Br.tela("/nova", nova, titulo := "Nova")

action recomecar():
    tarefas.clear()
    tarefas.append({{"id": 1, "titulo": "Primeira tarefa", "feita": no}})

relay app, recomecar
'''

MODELO_MOBILE_MAIN = '''// {nome} — sobe o aplicativo, e o celular na mesma rede o abre.

adopt Arcane.Brasa as Br
adopt ./app as App

Br.rodar(App.app, porta := 8600)
'''

MODELO_MOBILE_TESTE = '''// O aplicativo, testado sem navegador — e o PWA, conferido servindo.

adopt Arcane.Brasa as Br
adopt Arcane.Crucible as Crucible
adopt ../src/app as App

crucible "o aplicativo":

    trial "concluir tira da lista":
        App.recomecar()
        s := Br.testar(App.app)
        s.tocar("Primeira tarefa")
        s.clicar("Concluir")
        s.ir("/")
        expect s.tem("Nada pendente") is yes

    trial "criar uma tarefa":
        App.recomecar()
        s := Br.testar(App.app)
        s.tocar("Nova tarefa")
        s.digitar("Título", "comprar café")
        s.clicar("Salvar")
        s.ir("/")
        expect s.tem("comprar café") is yes

    trial "o PWA tem tudo que o Android exige":
        falhas := [c cycle c in Br.conferir_pwa(App.app) given not c["ok"]]
        expect len(falhas) is 0

Crucible.run()
'''


def _icone_svg(nome):
    letra = (nome or "D")[0].upper()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#0d1017"/>
  <text x="256" y="340" font-family="system-ui,sans-serif" font-size="280"
        font-weight="700" fill="#f4c95d" text-anchor="middle">{letra}</text>
</svg>
'''


# ═══════════════════════════════════════════════════════════
#  desktop
# ═══════════════════════════════════════════════════════════

def novo(argumentos, flags):
    """Um esqueleto de aplicação de mesa que já roda e já tem teste."""
    nome = (argumentos[0] if argumentos and not argumentos[0].startswith("-")
            else _valor(argumentos, flags, "nome", "meu-app"))
    pasta = _valor(argumentos, flags, "em", nome)
    if os.path.exists(pasta) and os.listdir(pasta):
        print(color(f"a pasta '{pasta}' já existe e não está vazia.", "1;31"))
        print("  escolha outro nome, ou passe --em=outra-pasta")
        return 1

    os.makedirs(os.path.join(pasta, "src"), exist_ok=True)
    os.makedirs(os.path.join(pasta, "tests"), exist_ok=True)
    titulo = nome.replace("-", " ").replace("_", " ").title()

    with open(os.path.join(pasta, "src", "tela.df"), "w", encoding="utf-8") as f:
        f.write(MODELO_TELA.format(nome=titulo))
    with open(os.path.join(pasta, "src", "main.df"), "w", encoding="utf-8") as f:
        f.write(MODELO_APP.format(nome=titulo))
    with open(os.path.join(pasta, "tests", "tela_test.df"), "w",
              encoding="utf-8") as f:
        f.write(MODELO_TESTE)
    with open(os.path.join(pasta, "forge.toml"), "w", encoding="utf-8") as f:
        f.write(f'[project]\nname = "{nome}"\nversion = "0.1.0"\n'
                f'description = "Aplicação de mesa"\nmain = "src/main.df"\n')
    with open(os.path.join(pasta, "icone.svg"), "w", encoding="utf-8") as f:
        f.write(_icone_svg(titulo))

    print(color(f"criado: {pasta}/", "1;32"))
    print(f"  {pasta}/src/tela.df          a aplicação (Bigorna) — não abre janela")
    print(f"  {pasta}/src/main.df          abre a janela")
    print(f"  {pasta}/tests/tela_test.df   o teste, sem display")
    print(f"  {pasta}/icone.svg            o ícone")
    print()
    print("  cd " + pasta)
    print("  dataforge desktop rodar src/main.df")
    print("  dataforge test")
    return 0


def rodar(argumentos, flags):
    """Abre a janela."""
    if not argumentos:
        print(color("falta o arquivo.", "1;31"))
        print("  dataforge desktop rodar src/main.df")
        return 2
    from .stdlib import get_module
    if not get_module("Arcane.Bigorna")["tem_display"]():
        print(color("não há display nesta máquina.", "1;33"))
        print("  num servidor, num contêiner ou por ssh sem X isso é normal.")
        print("  · para testar sem display: B.testar(app)")
        print("  · para servir uma interface por rede: dataforge vitrine run")
        return 1
    alvo = argumentos[0]
    return subprocess.run([sys.executable, "-m", "dataforge", "run", alvo],
                          check=False).returncode


def doctor(_argumentos, _flags):
    """O que falta para empacotar aqui."""
    from .stdlib import get_module

    achados = []
    try:
        import tkinter
        achados.append((True, "Tk", f"versão {tkinter.TkVersion}"))
    except ImportError:
        achados.append((False, "Tk", "falta — Debian/Ubuntu: apt install python3-tk"))

    tem_tela = get_module("Arcane.Janela")["tem_display"]()
    achados.append((tem_tela, "display",
                    "há para onde desenhar" if tem_tela else
                    "nenhum (normal em servidor, contêiner e ssh sem X)"))

    pyi = shutil.which("pyinstaller")
    achados.append((bool(pyi), "PyInstaller",
                    pyi or "falta — pip install pyinstaller"))

    alvo = {"darwin": ".app (macOS)", "win32": ".exe (Windows)"}.get(
        sys.platform, "binário (Linux)")
    achados.append((True, "alvo desta máquina", alvo))

    for ok, o_que, detalhe in achados:
        marca = color("✓", "1;32") if ok else color("✗", "1;31")
        print(f"  {marca} {o_que:<20} {detalhe}")

    if not pyi:
        print()
        print(color("Para empacotar:", "1;33"))
        print("  pip install pyinstaller")
        print("  dataforge desktop empacotar src/main.df --nome=MeuApp")
    print()
    print(color("O que NÃO existe, para não haver surpresa:", "0;90"))
    print("  · assinatura e notarização — no macOS, o usuário verá o aviso")
    print("    do Gatekeeper até você assinar com uma conta de desenvolvedor")
    print("  · instalador (.dmg, .msi) — o que sai é o executável")
    print("  · atualização automática")
    return 0 if pyi else 1


def empacotar(argumentos, flags):
    """Chama o PyInstaller e monta o executável desta plataforma."""
    if not argumentos:
        print(color("falta o arquivo da aplicação.", "1;31"))
        print("  dataforge desktop empacotar src/main.df --nome=MeuApp")
        return 2
    alvo = os.path.abspath(argumentos[0])
    if not os.path.isfile(alvo):
        print(color(f"não achei '{argumentos[0]}'.", "1;31"))
        return 1

    if not shutil.which("pyinstaller"):
        print(color("o PyInstaller não está instalado.", "1;31"))
        print("  pip install pyinstaller")
        print()
        print("  Ele é quem monta o executável — empacotar um interpretador")
        print("  Python é um problema resolvido, e resolvê-lo de novo daria")
        print("  um subconjunto pior amarrado a esta linguagem.")
        return 1

    nome = _valor(argumentos, flags, "nome",
                  os.path.splitext(os.path.basename(alvo))[0])
    saida = _valor(argumentos, flags, "em", "dist")
    janela = not _tem(argumentos, flags, "terminal")

    # O lançador: ele existe porque o PyInstaller empacota um PROGRAMA
    # PYTHON, e o que se quer rodar é um .df. A guarda do __main__ não
    # é decoração: sem ela, o 'spawn' de map_processos reexecuta a CLI
    # em cada trabalhador.
    lancador = os.path.join(os.path.dirname(alvo), f"_{nome}_lancador.py")
    with open(lancador, "w", encoding="utf-8") as f:
        # O import e de TOPO, e nao dentro da funcao: o PyInstaller
        # segue a arvore de imports ESTATICAMENTE, e um import lazy
        # deixa o interpretador inteiro de fora do pacote. O sintoma e
        # cruel — o .app monta, abre, e morre com "No module named
        # 'dataforge'", que parece falta de instalacao e nao falta de
        # empacotamento.
        f.write('# -*- coding: utf-8 -*-\n'
                '"""Gerado por \'dataforge desktop empacotar\'."""\n'
                'import multiprocessing\nimport os\nimport sys\n\n'
                'import dataforge\nimport dataforge.stdlib\n'
                'from dataforge.cli import main as cli\n\n'
                'def main():\n'
                '    aqui = os.path.dirname(os.path.abspath(__file__))\n'
                '    if getattr(sys, "frozen", False):\n'
                '        aqui = sys._MEIPASS\n'
                f'    sys.argv = ["dataforge", "run", os.path.join(aqui, "{os.path.basename(alvo)}")]\n'
                '    cli()\n\n'
                'if __name__ == "__main__":\n'
                '    # Sem ela, o \'spawn\' de map_processos reexecuta o\n'
                '    # app inteiro em cada trabalhador.\n'
                '    multiprocessing.freeze_support()\n'
                '    main()\n')

    # Onde o pacote MORA. Numa instalacao editavel (`pip install -e .`)
    # ele fica no repositorio, e o PyInstaller nao segue o arquivo .pth
    # que aponta para la: o pacote sai de fora, e o executavel morre
    # com "No module named 'dataforge'" — que parece falta de
    # instalacao, e e falta de empacotamento.
    aqui = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # A PASTA inteira do programa, e nao so o arquivo de entrada: um
    # aplicativo de verdade tem varios '.df', e empacotar so o main faz
    # o executavel morrer no primeiro 'adopt ./vizinho' — depois de
    # montar, abrir e parecer que funcionou.
    pasta_do_app = os.path.dirname(alvo)
    dados = [f"{pasta_do_app}{os.pathsep}."]
    for pasta, _sub, arquivos in os.walk(pasta_do_app):
        if any(p in pasta for p in ("__pycache__", ".git", "dist", "build")):
            continue
        relativo = os.path.relpath(pasta, pasta_do_app)
        for arquivo in arquivos:
            if arquivo.endswith((".df", ".toml", ".json", ".txt", ".html")):
                dados.append(f"{os.path.join(pasta, arquivo)}{os.pathsep}{relativo}")

    comando = ["pyinstaller", "--noconfirm", "--clean",
               "--name", nome, "--distpath", saida,
               "--paths", aqui,
               # A stdlib da linguagem e carregada por NOME, em tempo de
               # execucao: sem isto o pacote sai sem os modulos que o
               # programa adota, e a falha aparece no primeiro 'adopt'.
               "--collect-submodules", "dataforge",
               "--onefile"]
    for dado in dados:
        comando += ["--add-data", dado]
    if janela:
        comando.append("--windowed")
    comando.append(lancador)

    print(color(f"empacotando '{nome}'…", "1;36"))
    print(f"  {' '.join(comando)}")
    r = subprocess.run(comando, check=False)
    try:
        os.remove(lancador)
    except OSError:                                      # pragma: no cover
        pass
    if r.returncode != 0:
        print(color("o PyInstaller falhou.", "1;31"))
        return 1
    print(color(f"pronto: {saida}/", "1;32"))
    print()
    print(color("Antes de distribuir:", "0;90"))
    if sys.platform == "darwin":
        print("  · o macOS vai avisar que o app não é identificado até você")
        print("    assiná-lo: codesign --sign \"Developer ID\" e notarizar")
    elif sys.platform.startswith("win"):
        print("  · o SmartScreen vai avisar até o executável ter reputação")
        print("    ou uma assinatura de código")
    else:
        print("  · o binário depende da libc da máquina que o construiu —")
        print("    construa na distribuição mais antiga que você suporta")
    return 0


# ═══════════════════════════════════════════════════════════
#  mobile
# ═══════════════════════════════════════════════════════════

MANIFESTO = {
    "name": "", "short_name": "", "start_url": "/",
    "display": "standalone", "background_color": "#0d1017",
    "theme_color": "#0d1017", "orientation": "portrait",
    "icons": [],
}

TRABALHADOR = '''/* Gerado por 'dataforge mobile pwa'.
 *
 * O service worker e o que faz o Android oferecer "instalar" e o que
 * deixa o app abrir sem rede. A estrategia e REDE PRIMEIRO com cache
 * de reserva: um painel que mostra dado velho sem avisar e pior que
 * um painel que diz "sem conexao".
 */
const CACHE = '{nome}-v{versao}';
const ESSENCIAIS = ['/'];

self.addEventListener('install', (e) => {{
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ESSENCIAIS)));
  self.skipWaiting();
}});

self.addEventListener('activate', (e) => {{
  e.waitUntil(caches.keys().then((chaves) => Promise.all(
    chaves.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
}});

self.addEventListener('fetch', (e) => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(
    fetch(e.request)
      .then((r) => {{
        const copia = r.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copia));
        return r;
      }})
      .catch(() => caches.match(e.request).then(
        (r) => r || new Response('sem conexão', {{status: 503}})))
  );
}});
'''


def pwa(argumentos, flags):
    """Gera o manifesto, o ícone e o service worker de um app instalável."""
    nome = _valor(argumentos, flags, "nome", "Meu App")
    pasta = _valor(argumentos, flags, "em", "publico")
    versao = _valor(argumentos, flags, "versao", "1")
    os.makedirs(pasta, exist_ok=True)

    manifesto = dict(MANIFESTO)
    manifesto["name"] = nome
    manifesto["short_name"] = nome.split()[0][:12]
    manifesto["icons"] = [
        {"src": "/icone.svg", "sizes": "any", "type": "image/svg+xml"},
        {"src": "/icone-512.png", "sizes": "512x512", "type": "image/png",
         "purpose": "any maskable"},
    ]
    with open(os.path.join(pasta, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)
    with open(os.path.join(pasta, "sw.js"), "w", encoding="utf-8") as f:
        f.write(TRABALHADOR.format(nome=manifesto["short_name"].lower(),
                                   versao=versao))
    with open(os.path.join(pasta, "icone.svg"), "w", encoding="utf-8") as f:
        f.write(_icone_svg(nome))

    print(color(f"gerado em {pasta}/", "1;32"))
    print("  manifest.json   o que o Android lê para oferecer 'instalar'")
    print("  sw.js           o service worker — rede primeiro, cache de reserva")
    print("  icone.svg       o ícone")
    print()
    print(color("Ponha no HTML da sua aplicação, dentro do <head>:", "1;36"))
    print('  <link rel="manifest" href="/manifest.json">')
    print('  <meta name="theme-color" content="#0d1017">')
    print("  <script>navigator.serviceWorker?.register('/sw.js')</script>")
    print()
    print(color("E o que o Android exige, sem exceção:", "1;33"))
    print("  · HTTPS — em http:// ele não oferece instalar (localhost é exceção)")
    print("  · o manifesto com name, icons e display")
    print("  · um service worker registrado")
    return 0


def mobile_novo(argumentos, flags):
    """Um esqueleto de aplicativo Brasa que já roda e já tem teste."""
    nome = (argumentos[0] if argumentos and not argumentos[0].startswith("-")
            else _valor(argumentos, flags, "nome", "meu-app"))
    pasta = _valor(argumentos, flags, "em", nome)
    if os.path.exists(pasta) and os.listdir(pasta):
        print(color(f"a pasta '{pasta}' já existe e não está vazia.", "1;31"))
        print("  escolha outro nome, ou passe --em=outra-pasta")
        return 1
    os.makedirs(os.path.join(pasta, "src"), exist_ok=True)
    os.makedirs(os.path.join(pasta, "tests"), exist_ok=True)
    titulo = nome.replace("-", " ").replace("_", " ").title()
    arquivos = {
        os.path.join("src", "app.df"): MODELO_MOBILE_APP.format(nome=titulo),
        os.path.join("src", "main.df"): MODELO_MOBILE_MAIN.format(nome=titulo),
        os.path.join("tests", "app_test.df"): MODELO_MOBILE_TESTE,
        "forge.toml": (f'[project]\nname = "{nome}"\nversion = "0.1.0"\n'
                       f'description = "Aplicativo para celular"\nmain = "src/main.df"\n'),
    }
    for relativo, conteudo in arquivos.items():
        with open(os.path.join(pasta, relativo), "w", encoding="utf-8") as f:
            f.write(conteudo)
    print(color(f"criado: {pasta}/", "1;32"))
    print(f"  {pasta}/src/app.df          o aplicativo (Brasa) — não sobe servidor")
    print(f"  {pasta}/src/main.df         sobe, e mostra o endereço do celular")
    print(f"  {pasta}/tests/app_test.df   o teste, sem navegador — e o PWA conferido")
    print()
    print("  cd " + pasta)
    print("  dataforge test")
    print("  dataforge mobile rodar src/main.df")
    return 0


def mobile_rodar(argumentos, flags):
    """Sobe o aplicativo na rede local."""
    if not argumentos:
        print(color("falta o arquivo.", "1;31"))
        print("  dataforge mobile rodar src/main.df")
        return 2
    ambiente = dict(os.environ)
    porta = _valor(argumentos, flags, "porta")
    if porta:
        ambiente["BRASA_PORTA"] = str(porta)
    return subprocess.run([sys.executable, "-m", "dataforge", "run", argumentos[0]],
                          check=False, env=ambiente).returncode


def mobile_doctor(_argumentos, _flags):
    """O que existe e o que não existe para Android."""
    print(color("O que funciona hoje", "1;32"))
    print("  ✓ Arcane.Brasa: o framework de aplicativos — abas, topo com")
    print("    voltar, lista tocável, compartilhar, mapa e localização, e o")
    print("    PWA completo (manifesto, service worker, ícones PNG)")
    print("    dataforge mobile novo meu-app")
    print("  ✓ PWA a partir de uma aplicação Vitrine ou Kiln")
    print("    instala na tela inicial, abre em tela cheia, roda sem")
    print("    navegador visível e funciona offline com o service worker")
    print("  ✓ o servidor rodando no computador, e o celular na mesma rede")
    print("    (dataforge vitrine run --host=0.0.0.0)")
    print("  ✓ Termux: o interpretador roda num Android com Termux instalado")
    print("    — é o Python de verdade, com a linguagem inteira")
    print()
    print(color("O que NÃO existe", "1;31"))
    print("  ✗ APK — empacotar o interpretador num aplicativo Android")
    print("    exigiria python-for-android ou Chaquopy, e as duas trazem")
    print("    uma cadeia de dependências que a linguagem não tem")
    print("  ✗ widget nativo (Material, Compose)")
    print("  ✗ acesso a câmera, GPS ou notificação nativa pelo DataForge")
    print("    (o PWA alcança parte disso pelo navegador)")
    print("  ✗ publicação na Play Store")
    print()
    print(color("A decisão, escrita", "0;90"))
    print("  Um APK que empacota o CPython é possível e custa a promessa")
    print("  central do projeto: zero dependência. O PWA entrega o caso de")
    print("  uso real — uma ferramenta interna no celular de quem trabalha")
    print("  — sem quebrar nada. Dizer 'dá para fazer app Android' sem essa")
    print("  distinção seria a documentação mentindo sobre a linguagem.")
    return 0


# ═══════════════════════════════════════════════════════════

SUBCOMANDOS_DESKTOP = {
    "novo": novo, "new": novo,
    "rodar": rodar, "run": rodar,
    "empacotar": empacotar, "pack": empacotar,
    "doctor": doctor,
}

SUBCOMANDOS_MOBILE = {
    "novo": mobile_novo, "new": mobile_novo,
    "rodar": mobile_rodar, "run": mobile_rodar,
    "pwa": pwa,
    "doctor": mobile_doctor,
}


def executar(argumentos, flags=None, quais=None):
    flags = flags or {}
    tabela = quais or SUBCOMANDOS_DESKTOP
    if not argumentos or argumentos[0] in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0
    nome = argumentos[0]
    acao = tabela.get(nome)
    if acao is None:
        import difflib
        perto = difflib.get_close_matches(nome, tabela, 1, 0.6)
        print(color(f"'{nome}' não é um subcomando.", "1;31"))
        if perto:
            print(f"  você quis dizer '{perto[0]}'?")
        print(f"  os que existem: {', '.join(sorted(tabela))}")
        return 2
    try:
        return acao(argumentos[1:], flags)
    except KeyboardInterrupt:                            # pragma: no cover
        print()
        return 130


def executar_mobile(argumentos, flags=None):
    return executar(argumentos, flags, SUBCOMANDOS_MOBILE)
