// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Paginação por cursor",
  description: "Por que `pagina=3` mente, e o que o cursor promete no lugar.",
};

const blocos: Bloco[] = [
  {"p": "Paginar por número (`?pagina=3&por=20`) é a forma mais comum, e ela **pula e repete linhas** em qualquer lista que muda: alguém insere na página 1, e o item que era o 20 vira o 21 — quem pede a página 2 nunca o vê."},
  {"table": {"head": ["", "Por número", "Por cursor"], "rows": [["\"me dê a página 3\"", "`OFFSET 40` — o banco varre 40 linhas e joga fora", "`WHERE id > 'abc'` — usa o índice"], ["alguém insere no meio", "linha pulada ou repetida", "estável: o cursor aponta para uma linha"], ["\"ir para a página 50\"", "funciona", "**não existe**, e é o preço"], ["custo em 1 milhão de linhas", "cresce com o deslocamento", "constante"]]}},
  { code: `adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer
    nome: String

TODOS := [Produto(i, $"produto {i}") cycle i in range(1, 31)]

action listar(raiz, args, ctx):
    // 'pagina' fatia sozinha: ela recebe a coleção INTEIRA, quantos
    // itens e o cursor — e devolve o recorte com as bordas e a info.
    // E o '??' não é opcional: uma chave que não veio não está no
    // vault, e indexá-la levanta.
    yield Lavra.pagina(TODOS, args["primeiros"] ?? 10,
                       args["depois"] ?? void, len(TODOS))

esq := Lavra.esquema("catalogo")
Lavra.tipo(esq, Produto)
Lavra.tipo_pagina(esq, "Produto")
Lavra.busca(esq, "produtos", "PaginaProduto!",
    args := {"primeiros": {"tipo": "Integer", "padrao": 10},
             "depois": "String"},
    resolve := listar)
Lavra.conferir(esq)

r := Lavra.executar(esq, """
busca:
    produtos(primeiros: 3):
        total
        info:
            tem_proxima
            cursor_fim
        itens:
            id
            nome
""")
pagina := r["dados"]["produtos"]
assert len(pagina["itens"]) is 3
assert pagina["total"] is 30
assert pagina["info"]["tem_proxima"] is yes
out pagina`, lang: 'df' },
  {"h2": "A segunda página"},
  { code: `adopt Arcane.Lavra as Lavra

record Produto:
    id: Integer

TODOS := [Produto(i) cycle i in range(1, 11)]

action listar(raiz, args, ctx):
    yield Lavra.pagina(TODOS, args["primeiros"] ?? 3,
                       args["depois"] ?? void, len(TODOS))

esq := Lavra.esquema("c")
Lavra.tipo(esq, Produto)
Lavra.tipo_pagina(esq, "Produto")
Lavra.busca(esq, "produtos", "PaginaProduto!",
    args := {"primeiros": "Integer", "depois": "String"}, resolve := listar)
Lavra.conferir(esq)

primeira := Lavra.executar(esq,
    "busca:\\n    produtos(primeiros: 3):\\n        info:\\n            cursor_fim\\n        itens:\\n            id")
cursor := primeira["dados"]["produtos"]["info"]["cursor_fim"]

segunda := Lavra.executar(esq,
    $"busca:\\n    produtos(primeiros: 3, depois: \\"{cursor}\\"):\\n        itens:\\n            id")
assert segunda["dados"]["produtos"]["itens"][0]["id"] is 4
out $"a segunda página começa no {segunda['dados']['produtos']['itens'][0]['id']}"`, lang: 'df' },
  {"h2": "O cursor é opaco, de propósito"},
  {"p": "Um cursor que é visivelmente o `id` convida o cliente a construí-lo, e aí a implementação **não pode mais mudar**: trocar de offset para keyset quebraria todo mundo. Codificá-lo (base64, ou assinado) é o que mantém a liberdade — e é o mesmo motivo de `Kiln.cursor` existir do lado REST."},
  {"callout": {"tipo": "nota", "titulo": "O teto vem ligado", "texto": "`primeiros` precisa de um padrão **e** de um máximo. Sem o máximo, `primeiros: 1000000` é um jeito educado de derrubar o servidor — e é a primeira coisa que um scanner tenta. `Lavra.limites(esq, itens := 100)` cobra isso no esquema inteiro."}},
];

const headings = [{ id: 'a-segunda-pagina', text: "A segunda página", level: 2 as const }, { id: 'o-cursor-e-opaco-de-proposito', text: "O cursor é opaco, de propósito", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Paginação por cursor"}
      description={"Por que `pagina=3` mente, e o que o cursor promete no lugar."}
      href={"/docs/lavra/paginacao"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
