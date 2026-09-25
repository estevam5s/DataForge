# -*- coding: utf-8 -*-
"""Aplicações de mesa — a Bigorna, e a Janela por baixo dela.

A regra da seção é a do repositório inteiro: **não se inventa que
existe**. A janela é nativa nos três sistemas, com o Tk da biblioteca
padrão; o que o Tk não tem de forma portável (bandeja, arrastar,
animação) não é prometido.

O celular mora em `mobile.py`. Todo bloco `.df` roda — sem display,
que é como o CI roda.
"""

PAGINAS = [{'href': '/docs/desktop',
  'title': 'Aplicações de mesa',
  'description': 'Bigorna: o framework de aplicações de mesa — várias telas, menus com atalhos, '
                 'diálogos nativos e preferências, em macOS, Windows e Linux, com zero '
                 'dependência.',
  'blocos': [{'p': 'A **Bigorna** é o framework de aplicações de mesa do DataForge. Ela desenha '
                   'janelas **nativas** com o Tk, que vem na biblioteca padrão do Python — nada '
                   'para instalar em macOS, Windows ou Linux — e acrescenta o que uma aplicação de '
                   'verdade tem em volta da tela: navegação, barra de menus, atalhos, diálogos do '
                   'sistema, barra de status e preferências salvas.'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'produtos := [{"nome": "café", "qtd": 12}]\n'
                      '\n'
                      'app := B.app("Estoque", pasta_de_config := '
                      '$"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")\n'
                      'app.menu("Arquivo", [B.item("Novo produto", "novo", atalho := "Ctrl+N")])\n'
                      '\n'
                      'action lista(t):\n'
                      '    t.titulo("Produtos")\n'
                      '    t.tabela(["nome", "qtd"], produtos)\n'
                      '    t.status($"{len(produtos)} produto(s)")\n'
                      '    given t.comando("novo"):\n'
                      '        t.ir("novo")\n'
                      '\n'
                      'action novo(t):\n'
                      '    t.titulo("Novo produto")\n'
                      '    nome := t.entrada("Nome")\n'
                      '    given t.botao("Salvar"):\n'
                      '        produtos.append({"nome": nome, "qtd": 0})\n'
                      '        t.voltar()\n'
                      '\n'
                      'app.tela("lista", lista)\n'
                      'app.tela("novo", novo)\n'
                      '\n'
                      '// Com display: B.rodar(app) abre a janela. Aqui, a Sonda usa a MESMA\n'
                      '// aplicação sem abrir nada — é assim que ela roda no CI.\n'
                      's := B.testar(app)\n'
                      's.atalho("Ctrl+N")                  // no macOS, Cmd+N — o mesmo atalho\n'
                      's.digitar("Nome", "açúcar")\n'
                      's.clicar("Salvar")\n'
                      'assert s.tela_atual() is "lista"\n'
                      'assert s.status() is "2 produto(s)"\n'
                      'out s.texto()',
              'lang': 'df'},
             {'h2': 'O que ela acrescenta à Janela'},
             {'p': '`Arcane.Janela` desenha **uma** tela. A Bigorna usa a mesma tela — os mesmos '
                   '22 componentes, a mesma árvore — e acrescenta o que vem em volta:'},
             {'table': {'head': ['Peça', 'Como se escreve', 'Página'],
                        'rows': [['várias telas',
                                  '`app.tela("novo", novo)` · `t.ir("novo")` · `t.voltar()`',
                                  '[Telas e menus](/docs/desktop/telas-e-menus)'],
                                 ['barra de menus',
                                  '`app.menu("Arquivo", [B.item(...)])`',
                                  '[Telas e menus](/docs/desktop/telas-e-menus)'],
                                 ['atalhos de teclado',
                                  '`atalho := "Ctrl+N"` — vira Cmd+N no macOS',
                                  '[Telas e menus](/docs/desktop/telas-e-menus)'],
                                 ['diálogos do sistema',
                                  '`t.confirmar(...)` · `t.abrir_arquivo()` · `t.salvar_arquivo()`',
                                  '[Diálogos](/docs/desktop/dialogos)'],
                                 ['status e notificação',
                                  '`t.status("3 itens")` · `t.notificar("salvo")`',
                                  '[Telas e menus](/docs/desktop/telas-e-menus)'],
                                 ['tabela com seleção',
                                  '`linha := t.tabela(..., selecionar := yes)`',
                                  '[Telas e menus](/docs/desktop/telas-e-menus)'],
                                 ['preferências',
                                  '`t.pref("tema")` · `t.guardar_pref("tema", "escuro")`',
                                  '[Preferências e tema](/docs/desktop/preferencias-e-tema)'],
                                 ['tema',
                                  '`B.app(..., tema := "escuro")`',
                                  '[Preferências e tema](/docs/desktop/preferencias-e-tema)']]}},
             {'h2': 'A forma: o programa roda de novo'},
             {'p': 'Como na Vitrine, **cada tela roda de novo a cada interação**, e o estado '
                   'sobrevive. Um clique, um item de menu e um atalho são **eventos**: valem para '
                   'uma execução só, e por isso um formulário não é salvo duas vezes. É o que '
                   'dispensa callback e diffing — e o que torna a aplicação testável.'},
             {'table': {'head': ['', 'Callback (Tk cru, Qt)', 'Reexecução (Bigorna)'],
                        'rows': [['onde mora o estado', 'espalhado em widgets', 'no vault da tela'],
                                 ['ler um campo', '`entry.get()`', '`nome := t.entrada("Nome")`'],
                                 ['redesenhar', 'você lembra de fazer', 'acontece'],
                                 ['testar', 'precisa de display e de robô', '`B.testar(app)`'],
                                 ['o custo', '—', 'a tela roda inteira a cada evento']]}},
             {'h2': 'Começar'},
             {'code': '$ dataforge desktop novo estoque\n'
                      '$ cd estoque\n'
                      '$ dataforge test                     # a aplicação inteira, sem abrir '
                      'janela\n'
                      '$ dataforge desktop rodar src/main.df\n'
                      '$ dataforge desktop empacotar src/main.df --nome=Estoque',
              'lang': 'bash'},
             {'p': 'O esqueleto separa `src/tela.df` (a aplicação montada) de `src/main.df` (que '
                   'abre a janela) pelo mesmo motivo do Kiln: um teste que importasse o módulo que '
                   'abre a janela **nunca terminaria**. E ele já sai com quatro testes — atalho, '
                   'menu, validação e exclusão confirmada — que passam no primeiro `dataforge '
                   'test`.'},
             {'h2': 'O que ela NÃO é'},
             {'list': ['Não há arrastar-e-soltar, animação, ícone na bandeja do sistema nem janela '
                       'transparente: o Tk não os tem de forma portável, e prometer um recurso que '
                       'funciona num sistema só é pior que não prometer.',
                       'Para **painel de dados**, a [Vitrine](/docs/vitrine), no navegador. Para o '
                       '**celular**, a [Brasa](/docs/mobile).',
                       'Para a mesma regra de negócio nos três, ver '
                       '[Multiplataforma](/docs/multiplataforma).']},
             {'cards': [{'title': 'Telas e menus',
                         'desc': 'navegação, menus, atalhos, status, notificação e seleção.',
                         'href': '/docs/desktop/telas-e-menus'},
                        {'title': 'Diálogos',
                         'desc': 'confirmar, abrir e salvar arquivo — e o teste que responde.',
                         'href': '/docs/desktop/dialogos'},
                        {'title': 'Preferências e tema',
                         'desc': 'a pasta certa de cada sistema, e claro/escuro.',
                         'href': '/docs/desktop/preferencias-e-tema'},
                        {'title': 'Testar sem display',
                         'desc': 'a Sonda, e o que ela não prova.',
                         'href': '/docs/desktop/testar'},
                        {'title': 'Empacotar',
                         'desc': '.app, .exe e binário.',
                         'href': '/docs/desktop/empacotar'},
                        {'title': 'Uma aplicação inteira',
                         'desc': 'estoque com arquivo, menus e teste.',
                         'href': '/docs/desktop/completo'}]}]},
 {'href': '/docs/desktop/telas-e-menus',
  'title': 'Telas, menus e atalhos',
  'description': 'Navegar entre telas com parâmetros, a barra de menus, atalhos que viram Cmd no '
                 'macOS, status, notificação e a tabela com seleção.',
  'blocos': [{'h2': 'Telas e navegação'},
             {'p': 'Cada tela é uma ação que recebe `t`. A **primeira registrada** é a que abre. '
                   '`t.ir(nome, parametros)` troca de tela e empilha; `t.voltar()` desempilha. Os '
                   'dois **acabam a tela ali** — o que vem depois deles não roda.'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'clientes := [{"id": 1, "nome": "Ana"}, {"id": 2, "nome": "Bruno"}]\n'
                      'app := B.app("CRM", pasta_de_config := '
                      '$"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")\n'
                      '\n'
                      'action lista(t):\n'
                      '    t.titulo("Clientes")\n'
                      '    cycle c in clientes:\n'
                      '        given t.botao(c["nome"]):\n'
                      '            t.ir("cliente", {"id": c["id"]})\n'
                      '\n'
                      'action cliente(t):\n'
                      '    id := t.parametro("id")\n'
                      '    t.titulo($"Cliente {id}")\n'
                      '    given t.botao("Voltar"):\n'
                      '        t.voltar()\n'
                      '\n'
                      'app.tela("lista", lista)\n'
                      'app.tela("cliente", cliente)\n'
                      '\n'
                      's := B.testar(app)\n'
                      's.clicar("Bruno")\n'
                      'assert s.tela_atual() is "cliente"\n'
                      'assert s.tem("Cliente 2")\n'
                      's.clicar("Voltar")\n'
                      'assert s.tela_atual() is "lista"',
              'lang': 'df'},
             {'callout': {'tipo': 'nota',
                          'titulo': 'Uma tela nova começa limpa',
                          'texto': 'Voltar a uma tela de cadastro não traz o que foi digitado na '
                                   'visita anterior. E uma tela que chama `t.ir()` sem condição, '
                                   'mandando para outra que manda de volta, é recusada depois de '
                                   '16 trocas — com a dica de pôr o `t.ir()` dentro de um `given`, '
                                   'em vez de travar a aplicação.'}},
             {'h2': 'Menus e atalhos'},
             {'p': '`B.item(rótulo, comando, atalho)` cria um item; `t.comando("novo")` é `yes` na '
                   'execução em que ele foi escolhido — pelo menu ou pelo atalho, que são o mesmo '
                   'evento.'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'app := B.app("Editor", pasta_de_config := '
                      '$"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")\n'
                      'app.menu("Arquivo", [\n'
                      '    B.item("Novo", "novo", atalho := "Ctrl+N"),\n'
                      '    B.item("Salvar", "salvar", atalho := "Ctrl+S"),\n'
                      '    B.separador(),\n'
                      '    B.item("Exportar PDF", "pdf", atalho := "Ctrl+Shift+E"),\n'
                      '])\n'
                      'app.menu("Ajuda", [B.item("Sobre", "sobre")])\n'
                      '\n'
                      'eventos := []\n'
                      '\n'
                      'action tela(t):\n'
                      '    t.titulo("Documento")\n'
                      '    cycle c in ["novo", "salvar", "pdf", "sobre"]:\n'
                      '        given t.comando(c):\n'
                      '            eventos.append(c)\n'
                      '\n'
                      'app.tela("doc", tela)\n'
                      '\n'
                      's := B.testar(app)\n'
                      's.atalho("Cmd+S")                   // Cmd e Ctrl são o mesmo atalho\n'
                      's.atalho("ctrl+shift+e")            // a grafia é normalizada\n'
                      's.menu("Ajuda", "Sobre")\n'
                      'assert eventos is ["salvar", "pdf", "sobre"]\n'
                      'out s.menus()',
              'lang': 'df'},
             {'table': {'head': ['Escrito', 'No macOS', 'No Windows e no Linux'],
                        'rows': [['`Ctrl+N`', '⌘N', 'Ctrl+N'],
                                 ['`Ctrl+Shift+S`', '⌘⇧S', 'Ctrl+Shift+S'],
                                 ['`Alt+F4`', '⌥F4', 'Alt+F4']]}},
             {'p': 'O programa escreve `Ctrl` **uma vez**, e no macOS ele vira Cmd sozinho: um '
                   'atalho que existisse num sistema só obrigaria a ramificar o código. Dois itens '
                   'com o mesmo atalho são **recusados** — só um deles rodaria, e qual dependeria '
                   'da ordem.'},
             {'h2': 'Status, notificação e atualizar'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'tarefas := ["ler", "escrever", "revisar"]\n'
                      'app := B.app("Tarefas", pasta_de_config := '
                      '$"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")\n'
                      '\n'
                      'action tela(t):\n'
                      '    t.lista(tarefas)\n'
                      '    t.status($"{len(tarefas)} tarefa(s)")\n'
                      '    given t.botao("Concluir a primeira"):\n'
                      '        tarefas.remove(tarefas[0])\n'
                      '        t.notificar("concluída")\n'
                      '        t.atualizar()               // o status acima já tinha sido '
                      'calculado\n'
                      '\n'
                      'app.tela("t", tela)\n'
                      '\n'
                      's := B.testar(app)\n'
                      's.clicar("Concluir a primeira")\n'
                      'assert s.status() is "2 tarefa(s)"\n'
                      'assert s.notificacoes() is ["concluída"]',
              'lang': 'df'},
             {'callout': {'tipo': 'atencao',
                          'titulo': 'Por que `t.atualizar()`',
                          'texto': 'Um clique vale para UMA execução. O status foi calculado '
                                   '**antes** de a tarefa sair da lista — sem `t.atualizar()`, a '
                                   'barra diria 3 depois de concluir uma. Ele roda a tela de novo, '
                                   'sem o evento e sem apagar os campos.'}},
             {'p': 'Na janela, a notificação aparece no topo e some sozinha em três segundos; o '
                   'status fica na barra de baixo.'},
             {'h2': 'Tabela com seleção'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'pedidos := [{"n": 101, "total": 30}, {"n": 102, "total": 45}]\n'
                      'app := B.app("Pedidos", pasta_de_config := '
                      '$"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")\n'
                      '\n'
                      'action tela(t):\n'
                      '    escolhido := t.tabela(["n", "total"], pedidos, selecionar := yes)\n'
                      '    given escolhido is void:\n'
                      '        t.texto("escolha um pedido")\n'
                      '    otherwise:\n'
                      '        t.texto($"pedido {escolhido["n"]}: R$ {escolhido["total"]}")\n'
                      '\n'
                      'app.tela("t", tela)\n'
                      '\n'
                      's := B.testar(app)\n'
                      'assert s.tem("escolha um pedido")\n'
                      's.selecionar(1)\n'
                      'assert s.tem("pedido 102: R$ 45")',
              'lang': 'df'},
             {'p': 'Ela devolve **o que foi passado** — o vault inteiro, e não o texto da célula '
                   '—, ou `void` enquanto nada foi escolhido. Uma seleção que aponta para além da '
                   'lista (ela encolheu) volta a `void`, em vez de devolver outra linha.'}]},
 {'href': '/docs/desktop/dialogos',
  'title': 'Diálogos',
  'description': 'Confirmar, abrir arquivo, salvar e escolher pasta — os do sistema na janela, e o '
                 'roteiro do teste na Sonda.',
  'blocos': [{'p': 'Na janela, cada diálogo é o **nativo** do sistema — o seletor de arquivos do '
                   'Finder, do Explorer ou do GTK. Na Sonda, é a resposta que o teste deu. E um '
                   'diálogo que o teste **não** roteirizou é falha: inventar um "sim" esconderia '
                   'exatamente o que quebra em produção.'},
             {'table': {'head': ['Chamada', 'Devolve', 'Cancelado'],
                        'rows': [['`t.confirmar(pergunta)`', '`yes` ou `no`', '`no`'],
                                 ['`t.abrir_arquivo(titulo, tipos)`', 'o caminho', '`void`'],
                                 ['`t.salvar_arquivo(nome_sugerido, tipos)`',
                                  'o caminho',
                                  '`void`'],
                                 ['`t.escolher_pasta(titulo)`', 'o caminho', '`void`']]}},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'itens := ["a", "b"]\n'
                      'salvo := []\n'
                      'app := B.app("Lista", pasta_de_config := '
                      '$"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")\n'
                      '\n'
                      'action tela(t):\n'
                      '    t.lista(itens)\n'
                      '    given t.botao("Apagar tudo") and t.confirmar("Apagar os itens?"):\n'
                      '        itens.clear()\n'
                      '    given t.botao("Exportar"):\n'
                      '        caminho := t.salvar_arquivo("itens.txt", ["txt"])\n'
                      '        given caminho isnt void:\n'
                      '            salvo.append(caminho)\n'
                      '\n'
                      'app.tela("t", tela)\n'
                      's := B.testar(app)\n'
                      '\n'
                      '// sem roteiro: falha, com a dica do que fazer\n'
                      'monitor:\n'
                      '    s.clicar("Apagar tudo")\n'
                      '    assert no\n'
                      'handle Error as e:\n'
                      '    out e.message\n'
                      '\n'
                      's.responder(no)\n'
                      's.clicar("Apagar tudo")\n'
                      'assert len(itens) is 2          // "não" não apaga\n'
                      '\n'
                      's.responder("/tmp/itens.txt")\n'
                      's.clicar("Exportar")\n'
                      'assert salvo is ["/tmp/itens.txt"]\n'
                      '\n'
                      's.responder(void)               // o usuário cancelou\n'
                      's.clicar("Exportar")\n'
                      'assert len(salvo) is 1\n'
                      'out s.dialogos_pedidos()',
              'lang': 'df'},
             {'callout': {'tipo': 'dica',
                          'titulo': '`t.botao(...) and t.confirmar(...)`',
                          'texto': 'O `and` para no primeiro `no`: o diálogo só abre na execução '
                                   'em que o botão foi clicado. Escrito ao contrário, a '
                                   'confirmação abriria em toda reexecução da tela.'}},
             {'p': '`s.dialogos_pedidos()` lista o que a tela pediu, na ordem — é como se confere '
                   'que a pergunta certa foi feita, e não só que a resposta funcionou.'}]},
 {'href': '/docs/desktop/preferencias-e-tema',
  'title': 'Preferências e tema',
  'description': 'O que a aplicação lembra entre uma abertura e outra, na pasta certa de cada '
                 'sistema — e o tema claro, escuro ou o do sistema.',
  'blocos': [{'h2': 'Preferências'},
             {'p': '`t.pref(chave, padrão)` lê; `t.guardar_pref(chave, valor)` grava **na hora**, '
                   'num `preferencias.json`. A gravação escreve ao lado e troca o arquivo: uma '
                   'aplicação fechada no meio não deixa um JSON pela metade. E um arquivo '
                   'corrompido não impede a aplicação de abrir — ela volta aos padrões.'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'pasta := $"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}"\n'
                      'app := B.app("Notas", pasta_de_config := pasta)\n'
                      '\n'
                      'action tela(t):\n'
                      '    tamanho := t.pref("fonte", 14)\n'
                      '    t.texto($"fonte {tamanho}")\n'
                      '    given t.botao("Aumentar"):\n'
                      '        t.guardar_pref("fonte", tamanho + 2)\n'
                      '        t.atualizar()\n'
                      '\n'
                      'app.tela("t", tela)\n'
                      '\n'
                      'B.testar(app).clicar("Aumentar")\n'
                      '\n'
                      '// Outra execução da aplicação lê o que ficou gravado.\n'
                      'de_novo := B.app("Notas", pasta_de_config := pasta)\n'
                      'de_novo.tela("t", tela)\n'
                      'assert B.testar(de_novo).tem("fonte 16")',
              'lang': 'df'},
             {'h2': 'Onde elas ficam'},
             {'table': {'head': ['Sistema', 'Pasta'],
                        'rows': [['macOS', '`~/Library/Application Support/<nome>`'],
                                 ['Windows', '`%APPDATA%\\<nome>`'],
                                 ['Linux', '`$XDG_CONFIG_HOME/<nome>`, ou `~/.config/<nome>`']]}},
             {'code': 'adopt Arcane.Bigorna as B\n\nout B.pasta_de_config("Minha Aplicação")',
              'lang': 'df'},
             {'callout': {'tipo': 'atencao',
                          'titulo': 'Nunca ao lado do executável',
                          'texto': 'É o erro clássico: num `.app` assinado e em "Arquivos de '
                                   'Programas" a pasta do executável é só de leitura, e a '
                                   'preferência some sem erro nenhum. O `pasta_de_config` no '
                                   '`B.app` existe para o teste e para quem precisa de outra pasta '
                                   '— não para isso.'}},
             {'h2': 'Tema'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      '\n'
                      'assert B.temas() is ["claro", "escuro", "sistema"]\n'
                      'escuro := B.app("Painel", tema := "escuro")\n'
                      'out escuro.tema',
              'lang': 'df'},
             {'p': '`sistema` (o padrão) deixa o Tk seguir o sistema — no macOS, o modo escuro vem '
                   'sozinho. `claro` e `escuro` pintam fundo, campos, tabela e barra de status com '
                   'uma paleta própria, igual nos três sistemas.'}]},
 {'href': '/docs/desktop/componentes',
  'title': 'Os componentes',
  'description': 'Vinte e dois componentes, os mesmos na Janela e numa tela da Bigorna — e o que '
                 'cada um devolve.',
  'blocos': [{'p': 'Cada chamada **põe** um componente e **devolve** o valor dele. É o que faz a '
                   'tela ser um programa comum, de cima para baixo.'},
             {'callout': {'tipo': 'nota',
                          'titulo': 'Os mesmos na Bigorna',
                          'texto': 'Uma tela da [Bigorna](/docs/desktop) recebe o mesmo `t`: tudo '
                                   'desta página vale lá, e ela acrescenta `t.comando`, `t.ir`, os '
                                   'diálogos, `t.status` e a tabela com seleção. Os exemplos '
                                   'abaixo usam a `Arcane.Janela`, a camada de baixo, porque ela '
                                   'basta para uma tela só.'}},
             {'h2': 'Entradas'},
             {'code': 'adopt Arcane.Janela as J\n'
                      '\n'
                      'action tela(t):\n'
                      '    nome := t.entrada("Nome", "")\n'
                      '    senha := t.senha("Senha")\n'
                      '    idade := t.numero("Idade", 18, 0, 120)\n'
                      '    obs := t.area("Observações", "", 4)\n'
                      '    cor := t.escolha("Cor", ["azul", "verde"], "verde")\n'
                      '    ativo := t.caixa("Ativo", yes)\n'
                      '    nivel := t.deslizante("Nível", 0, 10, 5)\n'
                      '    quando := t.data("Quando", "2026-09-22")\n'
                      '    onde := t.arquivo("Arquivo", "", ["csv"])\n'
                      '\n'
                      '    t.texto($"{nome}|{idade}|{cor}|{ativo}|{nivel}")\n'
                      '\n'
                      's := J.testar(tela)\n'
                      'assert s.campos() is ["Arquivo", "Ativo", "Cor", "Idade", "Nome", "Nível", '
                      '"Observações", "Quando", "Senha"]\n'
                      's.digitar("Nome", "Ana")\n'
                      's.digitar("Idade", 30)\n'
                      'assert s.tem("Ana|30|verde|yes|5")\n'
                      'out s.texto()',
              'lang': 'df'},
             {'table': {'head': ['Componente', 'Devolve', 'Nota'],
                        'rows': [['`entrada`', 'texto', 'uma linha'],
                                 ['`senha`', 'texto', 'esconde o que se digita'],
                                 ['`numero`',
                                  '**Integer ou Float**',
                                  'digitado ele chega como texto, e `n + 1` daria concatenação'],
                                 ['`area`', 'texto', 'várias linhas'],
                                 ['`escolha`', 'a opção', 'uma de uma lista'],
                                 ['`caixa`', '`yes`/`no`', ''],
                                 ['`deslizante`', 'número', 'com mínimo e máximo'],
                                 ['`data`', 'texto', 'sem seletor nativo — é um campo com formato'],
                                 ['`arquivo`', 'o caminho', 'sem display, é um campo de texto']]}},
             {'h2': 'Mostrar'},
             {'code': 'adopt Arcane.Janela as J\n'
                      '\n'
                      'action tela(t):\n'
                      '    t.titulo("Relatório")\n'
                      '    t.texto("uma linha de texto comum")\n'
                      '    t.aviso("deu certo")\n'
                      '    t.erro("não deu")\n'
                      '    t.separador()\n'
                      '    t.tabela(["produto", "preço"], [\n'
                      '        {"produto": "café", "preço": "32,90"},\n'
                      '        {"produto": "filtro", "preço": "8,50"},\n'
                      '    ])\n'
                      '    t.lista(["primeiro", "segundo"])\n'
                      '    t.progresso(0.72, "carregando")\n'
                      '\n'
                      's := J.testar(tela)\n'
                      'assert s.tem("Relatório") and s.tem("deu certo")\n'
                      'assert s.tabelas()[0]["linhas"] is [["café", "32,90"], ["filtro", "8,50"]]\n'
                      'out s.texto()',
              'lang': 'df'},
             {'p': 'A tabela aceita **vault ou lista**: com vault, as colunas casam pelo nome; com '
                   'lista, pela posição. Os dois são comuns — `Database.query` devolve vaults, e '
                   'um CSV lido devolve listas.'},
             {'h2': 'O botão vale para UMA execução'},
             {'code': 'adopt Arcane.Janela as J\n'
                      '\n'
                      'salvos := []\n'
                      '\n'
                      'action tela(t):\n'
                      '    t.entrada("Nome", "")\n'
                      '    given t.botao("Salvar", yes):\n'
                      '        salvos.append(1)\n'
                      '\n'
                      's := J.testar(tela)\n'
                      's.clicar("Salvar")\n'
                      'assert len(salvos) is 1\n'
                      '\n'
                      '// Reexecutar NÃO salva de novo: o clique é um evento, e não estado.\n'
                      's.digitar("Nome", "x")\n'
                      'assert len(salvos) is 1\n'
                      'out "um clique, um salvamento"',
              'lang': 'df'},
             {'p': 'Se o clique ficasse guardado, a próxima reexecução salvaria o formulário de '
                   'novo — e esse é o defeito clássico de quem monta isto à mão.'},
             {'h2': 'Agrupar'},
             {'code': 'adopt Arcane.Janela as J\n'
                      '\n'
                      'action tela(t):\n'
                      '    t.grupo("Identificação")\n'
                      '    t.entrada("Nome")\n'
                      '    t.entrada("E-mail")\n'
                      '    t.fim()\n'
                      '\n'
                      '    t.grupo("Endereço")\n'
                      '    t.entrada("Rua")\n'
                      '    t.fim()\n'
                      '\n'
                      's := J.testar(tela)\n'
                      'assert s.tem("Identificação") and s.tem("Endereço")\n'
                      'assert len(s.campos()) is 3\n'
                      'out s.texto()',
              'lang': 'df'},
             {'callout': {'tipo': 'atencao',
                          'titulo': 'Dois campos com o mesmo rótulo',
                          'texto': 'Eles existem — e sem um contador na chave dividiriam o estado, '
                                   'o que faz digitar num mudar o outro. A chave é '
                                   '`especie:rotulo`, com `#2` a partir do segundo.'}}]},
 {'href': '/docs/desktop/testar',
  'title': 'Testar sem display',
  'description': 'A Sonda usa a aplicação inteira — telas, menus, atalhos, diálogos — sem abrir '
                 'janela, e por isso roda no CI.',
  'blocos': [{'p': 'Uma biblioteca de interface que só funciona com display é uma biblioteca **sem '
                   'teste**: o runner do CI não tem display. A separação entre a **árvore** e o '
                   '**desenho** resolve isso — a Sonda monta a mesma árvore que o Tk desenharia, e '
                   'por isso ela não simula nada.'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.Crucible as Crucible\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      'itens := []\n'
                      'app := B.app("Lista", pasta_de_config := '
                      '$"{OS.temp_dir()}/df-doc-{randint(100000, 999999)}")\n'
                      'app.menu("Editar", [B.item("Limpar", "limpar", atalho := "Ctrl+L")])\n'
                      '\n'
                      'action tela(t):\n'
                      '    nome := t.entrada("Nome")\n'
                      '    given t.botao("Adicionar"):\n'
                      '        given nome is "":\n'
                      '            t.erro("o nome é obrigatório")\n'
                      '        otherwise:\n'
                      '            itens.append(nome)\n'
                      '    given t.comando("limpar") and t.confirmar("Limpar a lista?"):\n'
                      '        itens.clear()\n'
                      '    t.status($"{len(itens)} item(ns)")\n'
                      '\n'
                      'app.tela("t", tela)\n'
                      '\n'
                      'crucible "a lista":\n'
                      '    trial "o nome vazio é recusado":\n'
                      '        s := B.testar(app)\n'
                      '        s.clicar("Adicionar")\n'
                      '        expect s.tem("o nome é obrigatório") is yes\n'
                      '\n'
                      '    trial "o atalho limpa, depois de confirmar":\n'
                      '        s := B.testar(app)\n'
                      '        s.digitar("Nome", "café")\n'
                      '        s.clicar("Adicionar")\n'
                      '        s.responder(yes)\n'
                      '        s.atalho("Ctrl+L")\n'
                      '        expect len(itens) is 0\n'
                      '\n'
                      'Crucible.run()',
              'lang': 'df'},
             {'h2': 'O que a Sonda faz'},
             {'table': {'head': ['Chamada', 'Faz'],
                        'rows': [['`s.digitar(rotulo, valor)` · `s.marcar` · `s.escolher`',
                                  'preenche um campo e roda a tela'],
                                 ['`s.clicar(rotulo)`', 'clica — o clique vale para UMA execução'],
                                 ['`s.menu(titulo, item)` · `s.atalho("Ctrl+N")`',
                                  'o comando, pelo menu ou pelo teclado'],
                                 ['`s.selecionar(linha)`',
                                  'escolhe a linha de uma tabela selecionável'],
                                 ['`s.responder(valor)`', 'a resposta do PRÓXIMO diálogo'],
                                 ['`s.tela_atual()` · `s.status()` · `s.notificacoes()`',
                                  'onde está e o que mostrou'],
                                 ['`s.texto()` · `s.tem(texto)` · `s.valor(rotulo)`',
                                  'o conteúdo da tela'],
                                 ['`s.menus()` · `s.dialogos_pedidos()` · `s.arvore()`',
                                  'a estrutura, como dado']]}},
             {'p': "Um rótulo que não existe lista os que existem — `nao ha botao 'Salvr'` vem com "
                   '`os botoes sao: Salvar, Cancelar`. É a mesma mensagem da Janela e da Vitrine.'},
             {'h2': 'O que a Sonda NÃO prova'},
             {'list': ['**O desenho.** Por isso existe '
                       '`test_a_janela_de_verdade_tem_menu_status_e_navega`, que monta a janela no '
                       'Tk, aciona o menu **pelo próprio Tk** (`menu.invoke`) e confere os widgets '
                       '— e que pula onde não há display.',
                       '**A aparência** — fonte, espaçamento, cor. Nenhum teste aqui finge isso.',
                       '**O diálogo nativo** do sistema: a Sonda prova a pergunta e o que a tela '
                       'faz com a resposta, não o seletor de arquivos do Finder.']}]},
 {'href': '/docs/desktop/empacotar',
  'title': 'Empacotar',
  'description': '.app, .exe e binário — e as três coisas que o PyInstaller cobra sem avisar.',
  'blocos': [{'p': '`dataforge desktop empacotar` gera o lançador e chama o **PyInstaller**. É a '
                   'mesma escolha do `iot carregar`, que chama o `arduino-cli`: empacotar um '
                   'interpretador Python é um problema resolvido, e resolvê-lo de novo daria um '
                   'subconjunto pior amarrado a esta linguagem.'},
             {'code': '$ dataforge desktop doctor\n'
                      '  ✓ Tk                   versão 8.6\n'
                      '  ✓ display              há para onde desenhar\n'
                      '  ✓ PyInstaller          /usr/local/bin/pyinstaller\n'
                      '  ✓ alvo desta máquina   .app (macOS)\n'
                      '\n'
                      '$ dataforge desktop empacotar src/main.df --nome=Caixa\n'
                      "empacotando 'Caixa'…\n"
                      'pronto: dist/',
              'lang': 'bash'},
             {'h2': 'As três coisas que ele cobra sem avisar'},
             {'table': {'head': ['O quê', 'O sintoma', 'O que o comando faz'],
                        'rows': [['import lazy',
                                  '"No module named \'dataforge\'" — parece falta de instalação',
                                  'o lançador importa no **topo**, onde a análise estática '
                                  'enxerga'],
                                 ['instalação editável',
                                  'idem, e só na máquina de quem desenvolve',
                                  'passa `--paths` com a raiz do pacote'],
                                 ['só o arquivo de entrada',
                                  'morre no primeiro `adopt ./vizinho`',
                                  'empacota a **pasta inteira** do programa']]}},
             {'p': 'As três produzem o mesmo tipo de falha: o executável **monta, abre e morre** — '
                   'e a mensagem fala de uma biblioteca que quem escreveu nunca viu. Foram os três '
                   'defeitos desta implementação, nesta ordem.'},
             {'h2': 'E a guarda do `__main__`'},
             {'code': '// O lançador gerado tem isto, e não é decoração:\n'
                      '//\n'
                      '//     if __name__ == "__main__":\n'
                      '//         multiprocessing.freeze_support()\n'
                      '//         main()\n'
                      '//\n'
                      "// Sem ela, o 'spawn' de map_processos reexecuta o APLICATIVO INTEIRO\n"
                      '// em cada trabalhador — e a mensagem fala de "bootstrapping phase",\n'
                      '// vocabulário do multiprocessing, três camadas longe de quem chamou.\n'
                      'adopt Arcane.Concurrent as C\n'
                      'assert C.nucleos() >= 1\n'
                      'out "num executável congelado, freeze_support() vem ANTES de main()"',
              'lang': 'df'},
             {'h2': 'O que sai, por sistema'},
             {'table': {'head': ['Sistema', 'Sai', 'O que o usuário vê'],
                        'rows': [['macOS',
                                  '`dist/Nome.app` e `dist/Nome`',
                                  'o aviso do Gatekeeper até você assinar e notarizar'],
                                 ['Windows',
                                  '`dist/Nome.exe`',
                                  'o SmartScreen, até o executável ter reputação ou assinatura'],
                                 ['Linux',
                                  '`dist/Nome`',
                                  'depende da libc de quem construiu — construa na distro mais '
                                  'antiga que você suporta']]}},
             {'h2': 'O que NÃO existe'},
             {'list': ['**Assinatura e notarização** — é conta de desenvolvedor da Apple, e o '
                       'comando não a pede nem a esconde.',
                       '**Instalador** (`.dmg`, `.msi`, `.deb` do seu app) — o que sai é o '
                       'executável.',
                       '**Atualização automática.**',
                       '**Compilação cruzada**: um `.exe` se faz no Windows, e um `.app` no macOS. '
                       'O PyInstaller não cruza, e nenhuma opção aqui finge que cruza.']},
             {'callout': {'tipo': 'atencao',
                          'titulo': 'O binário é grande, e isso é o interpretador',
                          'texto': 'Um app de tela simples sai com ~9 MB porque ele **carrega o '
                                   'Python inteiro** junto. É o preço de distribuir para quem não '
                                   'tem nada instalado — e é o mesmo preço do binário da própria '
                                   'CLI.'}}]},
 {'href': '/docs/desktop/completo',
  'title': 'Uma aplicação inteira',
  'description': 'Um controle de estoque com arquivo, menus, atalhos, confirmação, exportação e '
                 'teste.',
  'blocos': [{'p': 'Juntando tudo: lê e grava um arquivo, tem menu com atalhos, lista e cadastro '
                   'em telas separadas, confirma antes de apagar, exporta CSV por um diálogo, '
                   'lembra a última pasta — e é testada sem display.'},
             {'code': 'adopt Arcane.Bigorna as B\n'
                      'adopt Arcane.Serialization as Ser\n'
                      'adopt Arcane.IO as IO\n'
                      'adopt Arcane.OS as OS\n'
                      '\n'
                      '// ── onde o dado mora ───────────────────────────────────────\n'
                      'pasta := $"{OS.temp_dir()}/df-estoque-{randint(100000, 999999)}"\n'
                      'IO.mkdir(pasta)\n'
                      'defer:\n'
                      '    IO.remove_tree(pasta)\n'
                      'ARQUIVO := $"{pasta}/estoque.json"\n'
                      '\n'
                      'action carregar():\n'
                      '    given not IO.exists(ARQUIVO):\n'
                      '        yield []\n'
                      '    yield Ser.from_json(IO.read(ARQUIVO))\n'
                      '\n'
                      'action gravar(lista):\n'
                      '    IO.write(ARQUIVO, Ser.to_json(lista))\n'
                      '\n'
                      'itens := carregar()\n'
                      '\n'
                      '// ── a aplicação ────────────────────────────────────────────\n'
                      'app := B.app("Estoque", pasta_de_config := $"{pasta}/config")\n'
                      'app.menu("Arquivo", [\n'
                      '    B.item("Novo produto", "novo", atalho := "Ctrl+N"),\n'
                      '    B.separador(),\n'
                      '    B.item("Exportar CSV…", "exportar", atalho := "Ctrl+E"),\n'
                      '])\n'
                      '\n'
                      'action lista(t):\n'
                      '    t.titulo("Estoque")\n'
                      '    escolhido := t.tabela(["nome", "qtd"], itens, selecionar := yes)\n'
                      '    t.status($"{len(itens)} produto(s)")\n'
                      '    given t.comando("novo") or t.botao("Novo produto", yes):\n'
                      '        t.ir("novo")\n'
                      '    given escolhido isnt void and t.botao("Excluir") and '
                      't.confirmar($"Excluir {escolhido["nome"]}?"):\n'
                      '        itens.remove(escolhido)\n'
                      '        gravar(itens)\n'
                      '        t.notificar("excluído")\n'
                      '        t.atualizar()\n'
                      '    given t.comando("exportar"):\n'
                      '        destino := t.salvar_arquivo("estoque.csv", ["csv"])\n'
                      '        given destino isnt void:\n'
                      '            linhas := ["nome,qtd"] + [$"{i["nome"]},{i["qtd"]}" cycle i in '
                      'itens]\n'
                      '            IO.write(destino, join("\\n", linhas))\n'
                      '            t.guardar_pref("ultimo_export", destino)\n'
                      '            t.notificar($"exportado: {destino}")\n'
                      '\n'
                      'action novo(t):\n'
                      '    t.titulo("Novo produto")\n'
                      '    nome := t.entrada("Produto")\n'
                      '    qtd := t.numero("Quantidade", 1, 1, 9999)\n'
                      '    given t.botao("Salvar", yes):\n'
                      '        given nome is "":\n'
                      '            t.erro("o produto é obrigatório")\n'
                      '        orif nome in [i["nome"] cycle i in itens]:\n'
                      '            t.erro($"\'{nome}\' já está no estoque")\n'
                      '        otherwise:\n'
                      '            itens.append({"nome": nome, "qtd": qtd})\n'
                      '            gravar(itens)\n'
                      '            t.voltar()\n'
                      '    given t.botao("Cancelar"):\n'
                      '        t.voltar()\n'
                      '\n'
                      'app.tela("lista", lista)\n'
                      'app.tela("novo", novo)\n'
                      '\n'
                      '// ── testar (com display: B.rodar(app)) ─────────────────────\n'
                      's := B.testar(app)\n'
                      's.atalho("Ctrl+N")\n'
                      's.digitar("Produto", "café")\n'
                      's.digitar("Quantidade", 12)\n'
                      's.clicar("Salvar")\n'
                      'assert s.tela_atual() is "lista"\n'
                      '\n'
                      's.atalho("Ctrl+N")\n'
                      's.digitar("Produto", "café")\n'
                      's.clicar("Salvar")\n'
                      'assert s.tem("já está no estoque")        // o duplicado é recusado\n'
                      's.clicar("Cancelar")\n'
                      '\n'
                      's.responder($"{pasta}/saida.csv")\n'
                      's.menu("Arquivo", "Exportar CSV…")\n'
                      'assert IO.read($"{pasta}/saida.csv") is "nome,qtd\\ncafé,12"\n'
                      'assert app.preferencias.ler("ultimo_export") is $"{pasta}/saida.csv"\n'
                      '\n'
                      's.selecionar(0)\n'
                      's.responder(yes)\n'
                      's.clicar("Excluir")\n'
                      'assert s.status() is "0 produto(s)"\n'
                      'assert len(Ser.from_json(IO.read(ARQUIVO))) is 0\n'
                      'out "estoque: ok"',
              'lang': 'df'},
             {'h2': 'As decisões que ela carrega'},
             {'table': {'head': ['Decisão', 'O que ela evita'],
                        'rows': [['o estado mora **fora** das telas',
                                  'ele seria recriado a cada reexecução, e a lista ficaria sempre '
                                  'vazia'],
                                 ['gravar a cada mudança', 'fechar a janela e perder o trabalho'],
                                 ['confirmar **antes** de excluir, com `and`',
                                  'o diálogo abrir em toda reexecução, e não só no clique'],
                                 ['`t.atualizar()` depois de excluir',
                                  'a barra de status mostrar a contagem de antes'],
                                 ['a validação devolve `t.erro`, e não levanta',
                                  'um erro que fecha a janela no meio do cadastro'],
                                 ['`defer` na pasta temporária',
                                  'lixo em disco a cada execução do exemplo']]}},
             {'h2': 'O que falta para virar produção'},
             {'list': ['**Desfazer**, que aqui seria uma pilha do estado anterior.',
                       '**Um banco** em vez de JSON, quando passar de alguns milhares de linhas — '
                       '`Arcane.Database` está a um `adopt` de distância.',
                       '**Assinar** o executável — ver [Empacotar](/docs/desktop/empacotar).']}]}]
