# -*- coding: utf-8 -*-
"""Métodos mágicos, slots e MRO — as três páginas de OOP que faltavam.

A tabela dos 95 métodos **não** é escrita aqui: ela vem de
`dataforge/magicos.py`, a mesma de onde o interpretador lê. Escrever a
lista de novo garantiria divergência — foi o que aconteceu com a §7.5
da REFERENCIA, que ficou listando `add`/`sub`/`mul` muito depois de os
95 existirem.
"""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAIZ)

from dataforge import magicos  # noqa: E402

#: O título e a explicação de cada grupo. A ordem é a da página.
GRUPOS = [
    ("construcao", "Construção", "Nascer, morrer e copiar."),
    ("texto", "Texto", "O que `out`, `str()` e a interpolação chamam."),
    ("comparacao", "Comparação", "`is`, `isnt`, `<`, `<=`, `>`, `>=` e a ordenação."),
    ("aritmetica", "Aritmética", "`+` `-` `*` `/` `~/` `%` `**`."),
    ("refletida", "Aritmética refletida", "Quando o objeto está à **direita** do operador."),
    ("no-lugar", "Aritmética no lugar", "`+=`, `-=` e as outras compostas."),
    ("unario", "Unários", "`-x`, `+x`, `abs(x)`, `round(x)`."),
    ("bits", "Bits", "`&` `|` `^` `~` `<<` `>>`."),
    ("conversao", "Conversão", "`int()`, `float()`, `bool()`, `len()`, `hash()`."),
    ("colecao", "Coleção", "`[]`, `in`, percurso e tamanho."),
    ("chamada", "Chamada", "Fazer a instância ser chamável."),
    ("atributo", "Atributo", "Ler, escrever e remover campo."),
    ("descritor", "Descritor", "Um campo cujo acesso é controlado por outro objeto."),
    ("contexto", "Contexto", "Entrar e sair de um bloco com limpeza garantida."),
    ("assincrono", "Assíncrono", "`await` e percurso assíncrono."),
    ("tipo", "Tipo", "Como o objeto responde a perguntas sobre si mesmo."),
]


def _tabelas():
    """Uma tabela por grupo, direto de `dataforge.magicos`."""
    porgrupo = magicos.grupos()
    blocos = []
    for chave, titulo, resumo in GRUPOS:
        itens = porgrupo.get(chave)
        if not itens:
            continue
        blocos.append({"h2": f"{titulo} ({len(itens)})"})
        blocos.append({"p": resumo})
        blocos.append({"table": {
            "head": ["Método", "Parâmetros", "Chamado por"],
            "rows": [[f"`{i['nome']}`", str(i["aridade"]), i["descricao"]]
                     for i in itens]}})
    return blocos


PAGINAS = [
{
"href": "/docs/oop/magicos",
"title": "Métodos mágicos",
"description": f"Os {magicos.total()} ganchos que a linguagem procura no seu blueprint.",
"blocos": [
 {"p": f"Um **método mágico** é um gancho: a linguagem o procura no blueprint quando uma operação acontece sobre uma instância. Declarar `__add__` faz o `+` funcionar; declarar `__getitem__` faz o `[]` funcionar. São **{magicos.total()}**, em {len(GRUPOS)} grupos."},
 {"code": """blueprint Vetor:
    action setup(x, y):
        self.x := x
        self.y := y

    action __add__(outro):
        yield spawn Vetor(self.x + outro.x, self.y + outro.y)

    action __str__():
        yield $"({self.x}, {self.y})"

    action __eq__(outro):
        yield self.x is outro.x and self.y is outro.y

    action __len__():
        yield 2

out spawn Vetor(1, 2) + spawn Vetor(3, 4)      // imprime (4, 6)
assert len(spawn Vetor(1, 2)) is 2""", "lang": "df"},

 {"h2": "Por que o nome com dois sublinhados"},
 {"p": "Porque é o que quem chega do Python já conhece, e porque o sublinhado duplo sinaliza *isto não é para você chamar*: ele é chamado **pela linguagem**, no momento da operação. `v.__add__(outro)` funciona, mas escrever isso é o mesmo que escrever `v + outro` de um jeito pior."},
 {"callout": {"tipo": "nota", "titulo": "`operator +` continua valendo — e vence", "texto": "DataForge já tinha [`operator`](/docs/oop/operadores), que é mais direto de ler para quem nunca viu Python. Quando o blueprint declara os dois para a mesma operação, o `operator` tem prioridade. Eles convivem porque cobrem públicos diferentes."}},

 {"h2": "Um decorador que devolve void não substitui o alvo"},
 {"p": "Vale lembrar aqui porque é a regra que permite `@Rota(\"/x\")` apenas anotar: se um decorador devolvesse `void` e isso virasse o novo valor, a ação decorada sumiria."},

 *_tabelas(),

 {"h2": "O que não existe"},
 {"list": [
   "**Não há verificação de contrato.** Declarar `__iter__` sem `__next__` só falha quando alguém tenta percorrer o objeto.",
   "**`__slots__` não é um método mágico** — é uma declaração; veja [slots](/docs/oop/slots).",
   "**Um mágico que devolve o tipo errado não é corrigido.** `__len__` devolvendo texto quebra no `len()`, não na declaração."]},
]},

{
"href": "/docs/oop/slots",
"title": "slots",
"description": "Restringir os campos de uma instância — e gastar 64% menos memória por objeto.",
"blocos": [
 {"p": "`slots` declara **todos** os campos que uma instância pode ter. Quem tenta criar outro é recusado:"},
 {"code": """blueprint Ponto:
    slots x, y

    action setup(x, y):
        self.x := x
        self.y := y

p := spawn Ponto(1, 2)
out p.x                  // imprime 1
p.z := 3                 // erro: 'Ponto' has no field 'z'""", "lang": "df"},
 {"code": """erro[DF0402]: 'Ponto' has no field 'z'.
  = nota: it declares slots: x, y
  = dica: slots list every field the object may have; add it there,
          or remove the 'slots' declaration""", "lang": "text", "title": "saída"},

 {"h2": "Por que isso economiza memória"},
 {"p": "Sem `slots`, cada instância carrega um **vault** com os seus campos — e um vault guarda as chaves, a tabela de espalhamento e o espaço vago que ela precisa para não colidir. Com `slots`, a linguagem sabe de antemão quais campos existem e em que ordem, e guarda só os **valores**, numa lista."},
 {"p": "São **64% menos memória por objeto**, medido. Num programa com um milhão de instâncias, é a diferença entre caber e não caber."},
 {"callout": {"tipo": "dica", "titulo": "Quando usar", "texto": "Quando existirem **muitos** objetos do mesmo blueprint — pontos, linhas de um arquivo, nós de um grafo. Para um punhado de objetos de configuração, a economia não paga a rigidez."}},

 {"h2": "Herança"},
 {"p": "Herdar de um blueprint com `slots` e acrescentar os próprios é o caso normal: os campos se somam."},
 {"code": """blueprint Ponto:
    slots x, y

blueprint Ponto3D extends Ponto:
    slots z
    // a instância aceita x, y e z""", "lang": "df"},
 {"callout": {"tipo": "atencao", "titulo": "Um ancestral sem slots derruba a restrição", "texto": "Se **qualquer** blueprint da linhagem não declara `slots`, ele aceita campo livre — e a instância precisa de um vault de qualquer jeito. A restrição cai por terra, e a economia junto. Não é um defeito: é a única resposta correta."}},

 {"h2": "`slots` é contextual, não reservada"},
 {"p": "O parser só a reconhece dentro de um blueprint e quando o que vem depois confirma. `slots := 3` em qualquer lugar continua sendo uma variável chamada `slots` — pelo mesmo motivo de `get`, `set`, `final` e as dez palavras do [Kiln](/docs/kiln): são nomes bons demais para tirar de quem escreve."},
]},

{
"href": "/docs/oop/mro",
"title": "MRO — ordem de resolução",
"description": "Com herança múltipla, qual método ganha. Linearização C3.",
"blocos": [
 {"p": "Quando um blueprint herda de **um** pai, a busca de método é óbvia: ele, depois o pai, depois o avô. Com herança múltipla não é — e a **MRO** (*method resolution order*) é a lista que responde, calculada por **linearização C3**, a mesma do Python."},
 {"code": """blueprint A:
    action quem():
        yield "A"

blueprint B extends A:
    action quem():
        yield "B"

blueprint C extends A:
    action quem():
        yield "C"

blueprint D extends B, C:
    action de_quem_herdo():
        yield "de B e de C"

// D não declara 'quem': a MRO decide qual das duas responde
out (spawn D()).quem()      // "B" — a MRO é D, B, C, A""", "lang": "df"},

 {"h2": "As três garantias do C3"},
 {"list": [
   "**A classe vem antes das mães.** `D` antes de `B` e `C`.",
   "**A ordem em que as mães foram escritas é respeitada.** `extends B, C` põe `B` antes de `C`.",
   "**Uma mãe só aparece depois de todas as filhas dela.** `A` vem por último, mesmo sendo mãe de `B`.",
 ]},
 {"p": "Quando não existe ordem que satisfaça as três, a hierarquia é **ambígua** — e aí o C3 recusa, em vez de escolher em silêncio:"},
 {"code": """blueprint X extends A, B:
    // se B já herda de A, esta ordem se contradiz

erro: cannot linearize the hierarchy of 'X'""", "lang": "text"},
 {"p": "Recusar é o certo: uma escolha arbitrária aqui vira um bug que só aparece quando alguém acrescenta um método meses depois."},

 {"h2": "`root` segue a MRO"},
 {"p": "`root.metodo()` não vai ao \"primeiro pai\": vai ao **próximo na MRO**, a partir de onde a chamada está. É o que faz uma cadeia de `root` percorrer cada blueprint exatamente uma vez, mesmo em diamante."},
 {"code": """blueprint B extends A:
    action quem():
        yield "B->" + root.quem()

assert (spawn B()).quem() is "B->A\"""", "lang": "df"},

 {"h2": "Quando ela é calculada"},
 {"p": "Uma vez, na primeira consulta, e guardada. O C3 não é caro, mas a linhagem é percorrida em **toda** busca de método mágico — e aí a conta apareceria."},
]},
]
