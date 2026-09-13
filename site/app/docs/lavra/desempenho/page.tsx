// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Desempenho",
  description: "O lote contra o N+1, paginação por cursor, cache e o custo de uma consulta.",
};

const blocos: Bloco[] = [
  {"h2": "O N+1, em uma frase"},
  {"p": "Uma consulta que pede 50 pedidos e, de cada um, o cliente, faz **51** consultas ao banco: uma para os pedidos e uma por cliente. O servidor parece rápido e o banco morre."},
  { code: `busca:
    pedidos(limite: 50):
        numero
        cliente:
            nome`, lang: 'lavra' },
  {"h2": "O lote, em uma frase"},
  {"p": "O resolvedor não **busca** — ele **pede**. Os pedidos feitos na mesma volta são juntados num só, e cada um recebe a sua parte."},
  { code: `action buscar_clientes(ids):
    yield Banco.varios(ctx["banco"], "clientes", ids)

action cliente_do_pedido(pedido, args, ctx):
    yield Lavra.pedir(ctx, "clientes", pedido.cliente_id)

Lavra.campo(esq, "Pedido", "cliente", "Cliente!", resolve := cliente_do_pedido)`, lang: 'df' },
  { code: `ctx := Lavra.contexto({"banco": conexao})
_ := Lavra.lote(ctx, "clientes", buscar_clientes)

r := Lavra.executar(esq, consulta, contexto := ctx)
out r["extensoes"]["lotes"]`, lang: 'df' },
  { code: `{clientes: {chamadas: 1, chaves: 50, economia: 49}}`, lang: 'text' },
  {"componente": "diagrama-lote"},
  {"p": "Cinquenta pedidos, **uma** ida ao banco. O `economia` está ali para ser olhado: um lote que devolve o valor certo e mesmo assim consulta cinquenta vezes passaria em qualquer teste que só olhasse o resultado."},
  {"h3": "Duas decisões do lote"},
  {"list": ["**Ele vive no contexto, não no módulo.** Um lote de processo guardaria o cliente depois que ele mudou, e serviria o valor velho para outra pessoa. O contexto morre com a consulta, que é exatamente a vida útil que um cache de leitura pode ter aqui.", "**A ordem da resposta é a ordem do pedido.** A função recebe as chaves e devolve os valores na MESMA ordem — ou um vault de chave → valor, que não depende de ordem nenhuma."]},
  {"callout": {"tipo": "perigo", "titulo": "A lista fora de ordem é o bug clássico", "texto": "Cada pedido recebe o cliente de outro, e **nada falha**. Por isso o Lavra recusa uma resposta com tamanho diferente do pedido, e diz por quê — é o único sintoma que essa falha tem."}},
  {"h2": "Paginação por cursor"},
  {"p": "Paginar por posição (`pule 20, traga 20`) parece mais simples e quebra do jeito mais difícil de ver: se alguém insere uma linha entre a página 1 e a 2, **um item desaparece** — ele desceu para a posição que já foi lida."},
  { code: `action pedidos_de(usuario, args, ctx):
    todos := Banco.pedidos(usuario.id)
    yield Lavra.pagina(todos, primeiros := args["primeiros"],
                       depois := args["depois"])

Lavra.tipo_pagina(esq, "Pedido")
Lavra.campo(esq, "Usuario", "pedidos", "PaginaPedido!",
    args := {"primeiros": {"tipo": "Integer", "padrao": 20},
             "depois": "String"},
    resolve := pedidos_de)`, lang: 'df' },
  { code: `busca:
    usuario(id: 1):
        pedidos(primeiros: 20, depois: "eyJ..."):
            itens:
                numero
            info:
                tem_proxima
                cursor_fim
            total`, lang: 'lavra' },
  {"p": "Com cursor, a página seguinte começa exatamente onde a anterior parou — independentemente do que aconteceu no meio."},
  {"h2": "Cache"},
  {"p": "Há três camadas, e elas não se substituem:"},
  {"table": {"head": ["Camada", "Vive", "Para quê"], "rows": [["o lote", "uma consulta", "o mesmo dado pedido várias vezes na mesma resposta"], ["`V.cache` / memoize", "o processo", "o cálculo caro que muda devagar"], ["cabeçalho HTTP", "o cliente", "a resposta inteira, quando ela pode envelhecer"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Uma mudança nunca entra em cache", "texto": "É por isso que a operação diz o que é no nome. Um intermediário pode guardar uma `busca` sem abrir o corpo; uma `mudanca`, nunca."}},
  {"h2": "O custo de uma consulta"},
  {"p": "Nem toda consulta custa o mesmo, e o tamanho do texto não diz nada: três linhas pedindo uma lista de mil itens custam mais que trinta linhas de campos escalares."},
  { code: `Lavra.campo(esq, "Usuario", "relatorio", "Relatorio!",
    resolve := gerar_relatorio, custo := 50)

Lavra.limites(esq, complexidade := 1000)`, lang: 'df' },
  {"p": "Um campo que devolve lista multiplica o custo do que vem dentro pelo argumento de limite — e, sem limite declarado, por dez. É o que faz `pedidos { itens { produto { … } } }` custar caro sem que ninguém precise contar à mão."},
  { code: `out r["extensoes"]`, lang: 'df' },
  { code: `{ms: 12.4, campos: 143, profundidade: 4, complexidade: 260,
 lotes: {clientes: {chamadas: 1, chaves: 50, economia: 49}}}`, lang: 'text' },
];

const headings = [{ id: 'o-n1-em-uma-frase', text: "O N+1, em uma frase", level: 2 as const }, { id: 'o-lote-em-uma-frase', text: "O lote, em uma frase", level: 2 as const }, { id: 'duas-decisoes-do-lote', text: "Duas decisões do lote", level: 3 as const }, { id: 'paginacao-por-cursor', text: "Paginação por cursor", level: 2 as const }, { id: 'cache', text: "Cache", level: 2 as const }, { id: 'o-custo-de-uma-consulta', text: "O custo de uma consulta", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Desempenho"}
      description={"O lote contra o N+1, paginação por cursor, cache e o custo de uma consulta."}
      href={"/docs/lavra/desempenho"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
