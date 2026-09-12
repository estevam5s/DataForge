# -*- coding: utf-8 -*-
"""A página do servidor de linguagem."""

PAGINAS = [
{
"href": "/docs/tecnicas/lsp",
"title": "Servidor de linguagem (LSP)",
"description": "Autocompletar, erro ao digitar, ir-para-definição e renomear — do mesmo analisador que o 'dataforge check' usa.",
"blocos": [
 {"p": "O **servidor de linguagem** é o que transforma o editor de um bloco de notas colorido numa ferramenta. Ele fala o *Language Server Protocol* — o mesmo protocolo que TypeScript, Rust e Python usam — e é servido pelo mesmo analisador estático do `dataforge check`."},
 {"callout": {"tipo": "dica", "titulo": "Você não precisa fazer nada", "texto": "A extensão do VS Code inicia o servidor sozinha ao abrir um `.df`. Este documento é para quem usa outro editor, ou quer entender o que está acontecendo."}},

 {"h2": "O que ele responde"},
 {"table": {"head": ["Recurso", "O que faz", "Atalho"], "rows": [
   ["**Diagnóstico**", "erro e aviso sublinhados **enquanto se digita**, não só ao salvar", "—"],
   ["**Autocompletar**", "nomes do arquivo, embutidas, módulos e o que há dentro de cada um", "`Ctrl+Espaço`"],
   ["**Hover**", "a assinatura e o comentário que está acima da declaração", "parar o mouse"],
   ["**Ir para definição**", "salta para onde o nome foi declarado", "`F12`"],
   ["**Referências**", "onde mais aquele nome aparece", "`Shift+F12`"],
   ["**Esquema**", "ações, blueprints, records e enums na barra lateral", "`Ctrl+Shift+O`"],
   ["**Ajuda de assinatura**", "os parâmetros, enquanto se escreve a chamada", "ao abrir `(`"],
   ["**Renomear**", "troca o nome em todo o arquivo, recusando o que quebraria", "`F2`"],
   ["**Formatar**", "o mesmo `dataforge fmt`", "`Shift+Alt+F`"],
   ["**Correção rápida**", "aplica a sugestão do analisador", "`Ctrl+.`"]]}},

 {"h2": "Autocompletar sabe onde você está"},
 {"p": "Depois de um ponto, só vem o que existe **dentro** daquilo:"},
 {"code": """adopt Arcane.Math as M

M.▌         ← só os 51 símbolos de Arcane.Math
""", "lang": "text"},
 {"p": "Devolver o catálogo inteiro ali é o que faz o autocompletar virar ruído. Dentro do corpo de uma ação, os **parâmetros dela** aparecem — é o que mais faz alguém achar que o recurso não funciona:"},
 {"code": """action calcular(precoBase, desconto):
    total := ▌          ← 'precoBase' e 'desconto' aparecem aqui
""", "lang": "text"},
 {"p": "E os nomes do próprio arquivo vêm **antes** dos 1280 símbolos da stdlib — é o que se procura em nove de cada dez vezes."},

 {"h2": "O hover lê o seu comentário"},
 {"p": "DataForge não tem docstring. O costume — visível nos 219 exercícios e na stdlib inteira — é comentar **acima** da declaração, e é dali que o hover lê:"},
 {"code": """// Divide a conta entre as pessoas, arredondando para cima
// para o total nunca ficar menor que o valor original.
action dividir(total: Number, pessoas: Integer) -> Number:
    yield ceil(total / pessoas)
""", "lang": "df"},
 {"p": "Parar o mouse sobre `dividir` mostra a assinatura completa e as duas linhas. Sem sintaxe nova, sem anotação especial: o que já estava escrito passou a servir para mais uma coisa."},

 {"h2": "O que ele recusa"},
 {"p": "Renomear para uma palavra reservada é recusado na hora:"},
 {"code": """F2 sobre 'dobrar' → digitar 'yield'

  'yield' é palavra reservada do DataForge""", "lang": "text"},
 {"p": "Aceitar só adiaria o erro para a próxima execução — e aí ele apareceria longe da causa, num arquivo que \"estava funcionando\"."},

 {"h2": "Ele sobrevive ao arquivo pela metade"},
 {"p": "Esta é a decisão que mais se sente no uso. Enquanto se digita, o arquivo passa a **maior parte do tempo inválido** — falta um `:`, falta fechar um parêntese. Se cada estado inválido zerasse o que o servidor sabe, o autocompletar sumiria justamente enquanto se escreve."},
 {"p": "A última análise **boa** fica guardada e continua respondendo hover, autocompletar e esquema. O erro de sintaxe é publicado ao mesmo tempo — você vê o problema **e** continua com a ferramenta."},
 {"callout": {"tipo": "nota", "titulo": "É o que torna a ajuda de assinatura possível", "texto": "Quem pede os parâmetros de uma chamada está no meio de escrevê-la: o parêntese ainda não fechou, e o arquivo não compila. Depender de um parse bem-sucedido tornaria o recurso inútil no único momento em que ele é pedido."}},

 {"h2": "Outros editores"},
 {"p": "Qualquer editor que fale LSP serve. O comando é sempre o mesmo:"},
 {"code": """dataforge lsp""", "lang": "bash"},
 {"h3": "Neovim"},
 {"code": """vim.lsp.config.dataforge = {
  cmd = { 'dataforge', 'lsp' },
  filetypes = { 'dataforge' },
  root_markers = { 'forge.toml', '.git' },
}
vim.lsp.enable('dataforge')

vim.filetype.add({ extension = { df = 'dataforge' } })""", "lang": "text"},
 {"h3": "Helix — em `languages.toml`"},
 {"code": """[[language]]
name = "dataforge"
scope = "source.dataforge"
file-types = ["df"]
roots = ["forge.toml"]
indent = { tab-width = 4, unit = "    " }
language-servers = ["dataforge"]

[language-server.dataforge]
command = "dataforge"
args = ["lsp"]""", "lang": "toml"},
 {"h3": "Emacs — com `eglot`"},
 {"code": """(add-to-list 'auto-mode-alist '("\\\\.df\\\\'" . prog-mode))
(with-eval-after-load 'eglot
  (add-to-list 'eglot-server-programs
               '(dataforge-mode . ("dataforge" "lsp"))))""", "lang": "text"},

 {"h2": "Quando algo não funciona"},
 {"table": {"head": ["Sintoma", "Provável causa"], "rows": [
   ["Nenhum autocompletar", "o executável não está no `PATH` — veja o canal *DataForge* na saída do editor"],
   ["Erros em dobro", "o servidor **e** o check ao salvar ligados; o servidor desliga o segundo sozinho, mas uma extensão antiga em cache pode não fazer isso — reinstale com `dataforge editor`"],
   ["Parou de responder", "*DataForge: Reiniciar o servidor de linguagem*, na paleta de comandos"],
   ["Quero ver o que aconteceu", "aponte `dataforge.servidor.log` para um arquivo"]]}},
 {"callout": {"tipo": "atencao", "titulo": "Nada é impresso em stdout", "texto": "Para o servidor, a saída padrão **é** o canal do protocolo. Um `print` perdido corrompe a mensagem seguinte, e o editor desiste sem dizer por quê. É por isso que o registro vai para arquivo, e nunca para a tela."}},

 {"h2": "Desligar"},
 {"p": "Em *Settings*, `dataforge.servidor.ativo` como `false`. O editor volta ao diagnóstico simples — `dataforge check` ao salvar — e o resto da extensão continua igual."},
]},
]
