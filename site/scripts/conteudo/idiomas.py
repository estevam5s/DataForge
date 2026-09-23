# -*- coding: utf-8 -*-
"""A camada de idioma, depois de deixar de ser binaria.

Ela nasceu com dois: 'pt' ou 'en'. Binaria, ela nao tinha como receber
uma traducao de fora — quem quisesse espanhol teria de editar o nucleo,
e uma traducao que exige um pull request na linguagem nao acontece.
"""

PAGINAS = [

{"href": "/docs/idiomas",
 "title": "Idiomas: a linguagem fala o seu",
 "description": "Mensagens em português, inglês e espanhol — e um catálogo de fora entra sem tocar no núcleo. O que não está traduzido sai em inglês, de propósito.",
 "blocos": [
 {"p": "O erro que você lê é metade da linguagem. `DF_IDIOMA` escolhe em qual língua ele sai, e a lista **não** é fechada: um catálogo é um arquivo, e uma pasta apontada por `DF_IDIOMA_CAMINHO` entra no registro como os de dentro."},

 {"h2": "Os três que vêm de fábrica"},
 {"code": """$ DF_IDIOMA=pt dataforge run pedido.df
erro[DF0602]: A chave "b" não está neste vault.
  = nota: o vault tem 1 chave(s): "a"
  = dica: use  valor ?? padrao  para um padrão, ou confira antes com  vault.has(chave)

$ DF_IDIOMA=en dataforge run pedido.df
error[DF0602]: Key "b" is not in this vault.
  = note: the vault has 1 key: "a"
  = hint: use  valor ?? padrao  for a fallback, or check first with  vault.has(chave)

$ DF_IDIOMA=es dataforge run pedido.df
error[DF0602]: La clave "b" no está en este vault.
  = nota: el vault tiene 1 clave(s): "a"
  = pista: use  valor ?? predeterminado  para un valor por defecto, o compruebe antes con  vault.has(clave)""", "lang": "bash"},
 {"p": "O padrão é **pt**, e `DF_IDIOMA=en` volta ao texto como ele nasce. O locale do sistema é lido inteiro: `es_AR.UTF-8` vale `es`."},

 {"h2": "O que a tradução NÃO toca"},
 {"callout": {"tipo": "atencao", "titulo": "`e.message` fica como nasceu", "texto": "A tradução acontece **na hora de desenhar**, e não no objeto de erro. `e.message` é o que um `handle` compara e o que 2600 testes comparam: traduzir ali mudaria o comportamento de programa já escrito — e a informação que interessa a um programa é a **identidade** do erro, não a redação dela."}},
 {"code": """monitor:
    v := {"a": 1}
    out v["b"]
handle Error as e:
    // Isto vale em qualquer idioma: a mensagem do objeto nasce em
    // ingles e fica em ingles. O que muda de lingua e o RELATORIO.
    assert "not in this vault" in e.message
    out "peguei"
""", "lang": "df"},

 {"h2": "O que falta sai em inglês"},
 {"p": "Ninguém traduz 530 mensagens numa tacada. Um catálogo incompleto que levantasse, ou que devolvesse a chave crua, seria pior que o inglês: **um erro é sempre mais útil legível em inglês do que ilegível na língua certa.**"},
 {"code": """$ dataforge idioma

  em vigor: pt   (DF_IDIOMA=—)

  es  53 inteiras, 62 pedacos   100%
  pt  53 inteiras, 62 pedacos   100%
  en  ingles — o texto como ele nasce, sem catalogo""", "lang": "bash"},
 {"p": "A cobertura é medida comparando os **padrões**, e não traduzindo texto: medir traduzindo o molde português daria 0% para todo idioma que não é o português, porque os padrões casam o texto em inglês. Foi o primeiro jeito que a ferramenta fez, e ela anunciou um catálogo completo como vazio."},

 {"h2": "Contribuir um idioma"},
 {"p": "Um arquivo `.py` que expõe `INTEIRAS` e `PEDACOS`. O nome dele é o código do idioma."},
 {"code": """# ~/meus-idiomas/fr.py
INTEIRAS = (
    (r"'(?P<n>.+)' is not defined\\.", "'{n}' n'est pas défini."),
    (r"Division by zero\\.",           "Division par zéro."),
)
PEDACOS = (
    (r"Did you mean '(?P<n>[^']+)'\\?", "Vouliez-vous dire '{n}' ?"),
)""", "lang": "text"},
 {"code": """$ DF_IDIOMA_CAMINHO=~/meus-idiomas DF_IDIOMA=fr dataforge run x.df
error[DF0401]: 'x' n'est pas défini.""", "lang": "bash"},
 {"table": {"head": ["Decisão", "Porque"], "rows": [
   ["os **padrões** vêm do catálogo em português", "um regex copiado à mão casaria *quase*, e 'quase' aqui é uma mensagem que sai em inglês sem ninguém entender por quê"],
   ["os grupos são **nomeados**", "numerados, inverter dois campos numa tradução passaria calado"],
   ["um catálogo quebrado é **ignorado**", "um erro de sintaxe num arquivo de tradução não pode impedir um programa de rodar — a tradução é conforto, e o inglês é o piso"],
   ["a pasta de fora **vence** a de dentro", "é o que permite corrigir uma tradução sem reinstalar nada"],
   ["não há `en.py`", "seria uma cópia identidade de 115 entradas, que divergiria na primeira mensagem nova"]]}},

 {"h2": "A moldura também é idioma"},
 {"p": "As quatro palavras que mais aparecem — `erro`, `aviso`, `nota`, `dica` — eram literais em português dentro do desenhador. `DF_IDIOMA=en` produzia:"},
 {"code": """erro[DF0602]: Key "b" is not in this vault.""", "lang": "text"},
 {"p": "Um rótulo em português em cima de uma mensagem em inglês, na **primeira linha** do relatório. A camada traduzia 530 mensagens e esquecia as quatro palavras que aparecem em todas elas. Elas moram fora dos catálogos, porque não são mensagens: são a forma do relatório — e um idioma que não declara a sua cai no **inglês**, não no português, para não produzir um meio-português."},
 {"callout": {"tipo": "dica", "titulo": "O que um script deve procurar", "texto": "O lugar — `arquivo:linha:coluna` — não muda de idioma. A palavra ao lado muda. Um script de CI que grepa `erro:` quebra no dia em que alguém põe `DF_IDIOMA=en` na máquina."}},

 {"h2": "O que isto não é"},
 {"list": [
   "**Não traduz as palavras da linguagem.** `given`, `cycle` e `action` são as mesmas em qualquer idioma — um programa escrito em espanhol não compilaria na máquina de quem escreve em português, e o código deixaria de ser portátil.",
   "**Não traduz a documentação.** Ela é escrita em pt-BR, e a tradução dela é outro trabalho.",
   "**Não há `Arcane.Idioma`.** Quem embute o DataForge e quer o texto traduzido chama `dataforge.idioma.traduzir` do lado do Python."]},
 {"cards": [
   {"href": "/docs/erros", "title": "Códigos de erro", "desc": "o catálogo, com o que fazer"},
   {"href": "/docs/cli/referencia", "title": "A CLI", "desc": "`dataforge idioma` e os outros"},
   {"href": "/docs/contribuir", "title": "Contribuir", "desc": "como mandar um catálogo"}]},
]},
]
