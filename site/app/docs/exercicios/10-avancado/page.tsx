// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "10 · Avançado",
  description: "10 exercícios: decoradores, generators, threads e canais.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 10`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["[111](#111-async-await)", "**async / await**", "declare acoes assincronas e aguarde o resultado."], ["[112](#112-thread)", "**thread**", "dispare trabalho em segundo plano e espere terminar."], ["[113](#113-channel)", "**channel**", "passe valores entre partes do programa por um canal."], ["[114](#114-parallel)", "**parallel**", "rode varias tarefas ao mesmo tempo."], ["[115](#115-defer-com-recursos-reais)", "**defer com recursos reais**", "garanta que o arquivo seja apagado mesmo apos erro."], ["[116](#116-lista-ligada-com-blueprints)", "**Lista ligada com blueprints**", "implemente uma lista ligada simples."], ["[117](#117-arvore-binaria-de-busca)", "**Arvore binaria de busca**", "insira valores e percorra em ordem."], ["[118](#118-maquina-de-estados)", "**Maquina de estados**", "modele o ciclo de vida de um pedido."], ["[119](#119-sistema-de-inventario)", "**Sistema de inventario**", "junte blueprints, pipelines, erros e relatorio."], ["[120](#120-avaliador-de-expressoes-em-notacao-polonesa-reversa)", "**Avaliador de expressoes em notacao polonesa reversa**", "escreva um mini interpretador dentro do DataForge."]]}},
  {"h2": "111 · async / await"},
  {"p": "**Enunciado.** declare acoes assincronas e aguarde o resultado."},
  { code: `async action buscar_usuario(id):
    yield {"id": id, "nome": "Usuario " + str(id)}

async action buscar_pedidos(id):
    yield [{"id":1, "usuario":id}, {"id":2, "usuario":id}]

usuario := await buscar_usuario(7)
pedidos := await buscar_pedidos(7)

out usuario
out "pedidos:", len(pedidos)

assert usuario["id"] is 7, "id do usuario"
assert usuario["nome"] is "Usuario 7", "nome"
assert len(pedidos) is 2, "dois pedidos"`, lang: 'df', title: `exercicios/10-avancado/111_async_await.df` },
  {"h2": "112 · thread"},
  {"p": "**Enunciado.** dispare trabalho em segundo plano e espere terminar."},
  { code: `resultados := []

thread:
    cycle i from 1 to 3:
        resultados.append("t1-" + str(i))

thread:
    cycle i from 1 to 3:
        resultados.append("t2-" + str(i))

wait 200
out "itens produzidos:", len(resultados)
assert len(resultados) is 6, "as duas threads produziram"`, lang: 'df', title: `exercicios/10-avancado/112_threads.df` },
  {"h2": "113 · channel"},
  {"p": "**Enunciado.** passe valores entre partes do programa por um canal."},
  { code: `channel fila

fila.send("primeiro")
fila.send("segundo")
fila.send("terceiro")

a := fila.receive()
b := fila.receive()

out a, b
assert a is "primeiro", "FIFO"
assert b is "segundo", "segunda leitura"
assert fila.receive() is "terceiro", "terceira leitura"
assert fila.receive() is void, "canal vazio devolve void"`, lang: 'df', title: `exercicios/10-avancado/113_channel.df` },
  {"h2": "114 · parallel"},
  {"p": "**Enunciado.** rode varias tarefas ao mesmo tempo."},
  { code: `adopt Arcane.Math as Math

saidas := []

parallel:
    saidas.append("tarefa A: " + str(Math.factorial(10)))
    saidas.append("tarefa B: " + str(Math.fibonacci(20)))
    saidas.append("tarefa C: " + str(Math.is_prime(9973)))

wait 200
cycle s in sorted(saidas):
    out s

assert len(saidas) is 3, "tres tarefas concluidas"`, lang: 'df', title: `exercicios/10-avancado/114_parallel.df` },
  {"h2": "115 · defer com recursos reais"},
  {"p": "**Enunciado.** garanta que o arquivo seja apagado mesmo apos erro."},
  { code: `adopt Arcane.IO as IO

caminho := "_exercicio_115.tmp"

action processa_arquivo(deve_falhar):
    IO.write(caminho, "dados")
    defer:
        IO.delete(caminho)
    given deve_falhar:
        trigger "falha no processamento"
    yield "processado"

out processa_arquivo(no)
assert IO.exists(caminho) is no, "defer apagou apos sucesso"

monitor:
    processa_arquivo(yes)
handle e:
    out "erro tratado:", e

out "arquivo ainda existe?", IO.exists(caminho)
assert IO.exists(caminho) is no, "defer tambem apagou apos o erro"
out "defer roda em todos os caminhos de saida"`, lang: 'df', title: `exercicios/10-avancado/115_defer_recurso.df` },
  {"h2": "116 · Lista ligada com blueprints"},
  {"p": "**Enunciado.** implemente uma lista ligada simples."},
  { code: `blueprint No(valor):
    action setup(valor):
        self.valor := valor
        self.proximo := void

blueprint ListaLigada:
    action setup():
        self.cabeca := void
        self.tamanho := 0

    action inserir(valor):
        novo := spawn No(valor)
        given self.cabeca is void:
            self.cabeca := novo
        otherwise:
            atual := self.cabeca
            persist atual.proximo isnt void:
                atual := atual.proximo
            atual.proximo := novo
        self.tamanho := self.tamanho + 1
        yield self.tamanho

    action para_cluster():
        saida := []
        atual := self.cabeca
        persist atual isnt void:
            saida.append(atual.valor)
            atual := atual.proximo
        yield saida

l := spawn ListaLigada()
cycle v in [10, 20, 30]:
    l.inserir(v)

out l.para_cluster(), "tamanho:", l.tamanho
assert l.para_cluster() is [10, 20, 30], "ordem de insercao"
assert l.tamanho is 3, "tamanho"`, lang: 'df', title: `exercicios/10-avancado/116_estruturas_dados.df` },
  {"h2": "117 · Arvore binaria de busca"},
  {"p": "**Enunciado.** insira valores e percorra em ordem."},
  { code: `blueprint NoArvore(valor):
    action setup(valor):
        self.valor := valor
        self.esq := void
        self.dir := void

action inserir(raiz, valor):
    given raiz is void:
        yield spawn NoArvore(valor)
    given valor smaller raiz.valor:
        raiz.esq := inserir(raiz.esq, valor)
    orif valor bigger raiz.valor:
        raiz.dir := inserir(raiz.dir, valor)
    yield raiz

action em_ordem(atual, saida):
    given atual is void:
        yield saida
    em_ordem(atual.esq, saida)
    saida.append(atual.valor)
    em_ordem(atual.dir, saida)
    yield saida

raiz := void
cycle v in [50, 30, 70, 20, 40, 60, 80]:
    raiz := inserir(raiz, v)

ordenado := em_ordem(raiz, [])
out ordenado
assert ordenado is [20, 30, 40, 50, 60, 70, 80], "percurso em ordem"
assert raiz.valor is 50, "raiz"
assert raiz.esq.valor is 30, "filho esquerdo"`, lang: 'df', title: `exercicios/10-avancado/117_arvore_binaria.df` },
  {"h2": "118 · Maquina de estados"},
  {"p": "**Enunciado.** modele o ciclo de vida de um pedido."},
  { code: `steady TRANSICOES := {
    "novo":["pago", "cancelado"],
    "pago":["enviado", "reembolsado"],
    "enviado":["entregue"],
    "entregue":[],
    "cancelado":[],
    "reembolsado":[]
}

blueprint Pedido:
    action setup():
        self.estado := "novo"
        self.historico := ["novo"]

    action mover(destino):
        permitidos := TRANSICOES[self.estado]
        given not permitidos.contains(destino):
            trigger "transicao invalida: " + self.estado + " -> " + destino
        self.estado := destino
        self.historico.append(destino)
        yield destino

p := spawn Pedido()
p.mover("pago")
p.mover("enviado")
p.mover("entregue")
out p.historico

assert p.estado is "entregue", "estado final"
assert p.historico is ["novo", "pago", "enviado", "entregue"], "historico"

invalida := no
monitor:
    p.mover("pago")
handle e:
    invalida := yes
    out "bloqueado:", e
assert invalida is yes, "transicao invalida bloqueada"`, lang: 'df', title: `exercicios/10-avancado/118_maquina_estados.df` },
  {"h2": "119 · Sistema de inventario"},
  {"p": "**Enunciado.** junte blueprints, pipelines, erros e relatorio."},
  { code: `adopt Arcane.Text as Text

blueprint Produto(codigo, nome, preco, quantidade):
    action valor_total():
        yield self.preco * self.quantidade

    action baixa(qtd):
        guard qtd smaller_eq self.quantidade, "estoque insuficiente para " + self.nome
        self.quantidade := self.quantidade - qtd
        yield self.quantidade

    action toString():
        yield self.codigo + " " + self.nome

estoque := [
    spawn Produto("P01", "Mouse", 80.0, 15),
    spawn Produto("P02", "Teclado", 200.0, 4),
    spawn Produto("P03", "Monitor", 1200.0, 2),
    spawn Produto("P04", "Cabo", 25.0, 60)
]

valores := estoque >> morph p: p.valor_total()
patrimonio := valores >> distill acc, v: acc + v 0

criticos := estoque >> sift p: p.quantidade smaller 5

out Text.box("Inventario")
cycle p in estoque:
    out "  " + p.codigo + " " + p.nome.pad_end(10) + str(p.quantidade).pad_start(4) + "  R$ " + str(p.valor_total())

out ""
out "patrimonio: R$", patrimonio
out "criticos:", criticos >> morph p: p.nome

assert round(patrimonio, 2) is 5900.0, "patrimonio"
assert len(criticos) is 2, "dois produtos criticos"

estoque[0].baixa(5)
assert estoque[0].quantidade is 10, "baixa aplicada"

erro := no
monitor:
    estoque[2].baixa(99)
handle e:
    erro := yes
    out "erro:", e
assert erro is yes, "baixa acima do estoque e bloqueada"`, lang: 'df', title: `exercicios/10-avancado/119_inventario_completo.df` },
  {"h2": "120 · Avaliador de expressoes em notacao polonesa reversa"},
  {"p": "**Enunciado.** escreva um mini interpretador dentro do DataForge."},
  { code: `action avaliar_rpn(expressao):
    pilha := []
    cycle token in expressao.words():
        given ["+", "-", "*", "/"].contains(token):
            given len(pilha) smaller 2:
                trigger "expressao malformada perto de '" + token + "'"
            b := pilha.pop()
            a := pilha.pop()
            match token:
                point "+":
                    pilha.append(a + b)
                point "-":
                    pilha.append(a - b)
                point "*":
                    pilha.append(a * b)
                point "/":
                    given b is 0:
                        trigger "divisao por zero"
                    pilha.append(a / b)
        otherwise:
            pilha.append(cast token as Float)
    given len(pilha) isnt 1:
        trigger "expressao incompleta"
    yield pilha[0]

casos := [
    ["3 4 +", 7.0],
    ["5 1 2 + 4 * + 3 -", 14.0],
    ["10 2 /", 5.0],
    ["2 3 4 * +", 14.0]
]

cycle caso in casos:
    obtido := avaliar_rpn(caso[0])
    out caso[0].pad_end(22) + "= " + str(obtido)
    assert obtido is caso[1], "resultado de " + caso[0]

erros := 0
cycle ruim in ["1 +", "1 0 /", "1 2"]:
    monitor:
        avaliar_rpn(ruim)
    handle e:
        erros += 1
        out "rejeitado '" + ruim + "': " + e

assert erros is 3, "as tres expressoes invalidas foram rejeitadas"
out "mini interpretador RPN validado"`, lang: 'df', title: `exercicios/10-avancado/120_interpretador_expressoes.df` },
  {"hr": true},
  {"p": "Rode um isolado com `dataforge run exercicios/10-avancado/111_async_await.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }, { id: '111-async-await', text: "111 · async / await", level: 2 as const }, { id: '112-thread', text: "112 · thread", level: 2 as const }, { id: '113-channel', text: "113 · channel", level: 2 as const }, { id: '114-parallel', text: "114 · parallel", level: 2 as const }, { id: '115-defer-com-recursos-reais', text: "115 · defer com recursos reais", level: 2 as const }, { id: '116-lista-ligada-com-blueprints', text: "116 · Lista ligada com blueprints", level: 2 as const }, { id: '117-arvore-binaria-de-busca', text: "117 · Arvore binaria de busca", level: 2 as const }, { id: '118-maquina-de-estados', text: "118 · Maquina de estados", level: 2 as const }, { id: '119-sistema-de-inventario', text: "119 · Sistema de inventario", level: 2 as const }, { id: '120-avaliador-de-expressoes-em-notacao-polonesa-reversa', text: "120 · Avaliador de expressoes em notacao polonesa reversa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"10 · Avançado"}
      description={"10 exercícios: decoradores, generators, threads e canais."}
      href={"/docs/exercicios/10-avancado"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
