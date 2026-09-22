// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/projetos_tipos.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Pedido distribuído",
  description: "Reservar, cobrar e despachar em três serviços — e desfazer em ordem inversa quando um falha.",
};

const blocos: Bloco[] = [
  {"p": "Não existe transação que atravesse a rede: `BEGIN` no serviço de estoque não alcança o de cobrança. A resposta é a saga — cada passo declara como se desfaz, e uma falha no meio desfaz, **em ordem inversa**, o que já aconteceu."},
  {"table": {"head": ["Peça", "O que ela exercita"], "rows": [["`Malha.saga`", "os passos e as compensações"], ["o estado da saga", "o que cada passo produziu"], ["`conferir()`", "o passo que escreve sem compensação, antes de rodar"], ["`orfas`", "a compensação que falhou, para um humano"]]}},
  {"h2": "Estrutura"},
  { code: `pedidos-distribuidos/
  src/
    estoque.df     reservar / liberar
    cobranca.df    cobrar / estornar
    envio.df       despachar
    saga.df        liga os tres
  tests/`, lang: 'text' },
  { code: `[project]
name = "pedidos-distribuidos"
version = "0.1.0"
description = "Saga de pedido"
entry = "src/main.df"
dataforge = ">=1.1"

[dependencies]

[scripts]
start = "run src/main.df"
test = "test tests/"`, lang: 'toml', title: `forge.toml` },
  {"h2": "O núcleo"},
  {"p": "Este bloco roda sozinho — copie para um arquivo e rode `dataforge run`. Ele termina com `assert`, e é assim que esta página é conferida a cada build."},
  { code: `adopt Arcane.Malha as Malha

estoque := {"cafe": 3}
cobrado := []
log := []

action reservar(estado, chave):
    given estoque["cafe"] smaller estado["qtd"]:
        trigger "sem estoque"
    estoque["cafe"] -= estado["qtd"]
    log.append("reservou")
    yield {"reserva": "R-1"}

action liberar(estado, chave):
    estoque["cafe"] += estado["qtd"]
    log.append("liberou")

action cobrar(estado, chave):
    given estado["cartao"] is "recusado":
        trigger "cartao recusado"
    cobrado.append(chave)
    log.append("cobrou")
    yield {"cobranca": "C-1"}

action estornar(estado, chave):
    cobrado.remove(chave)
    log.append("estornou")

action despachar(estado, chave):
    given estado["cep"] is "00000-000":
        trigger "cep nao atendido"
    log.append("despachou")

action saga_de_pedido():
    s := Malha.saga("pedido")
    s.passo("reservar", reservar, liberar)
    s.passo("cobrar", cobrar, estornar)
    s.passo("despachar", despachar, void, no)
    yield s

s := saga_de_pedido()
assert s.conferir() is []

r := s.executar({"qtd": 2, "cartao": "ok", "cep": "00000-000"})
out log
assert not r["ok"]
assert r["falhou_em"] is "despachar"
// Ordem INVERSA: estorna antes de liberar.
assert log is ["reservou", "cobrou", "estornou", "liberou"]
assert estoque["cafe"] is 3 and len(cobrado) is 0`, lang: 'df', title: `src/saga.df` },
  {"h2": "O teste"},
  {"p": "No projeto, a regra mora em `src/` e o teste a importa pelo caminho relativo — `dataforge test tests/` descobre o arquivo sozinho."},
  { code: `adopt ../src/saga as S

crucible "saga":
    trial "o passo que falhou nao e compensado":
        r := S.saga_de_pedido().executar({"qtd": 1, "cartao": "recusado", "cep": "1"})
        expect r["desfeitos"] is ["reservar"]`, lang: 'df', title: `tests/nucleo_test.df` },
  {"h2": "As decisões"},
  {"table": {"head": ["Decisão", "Sem ela"], "rows": [["compensar em ordem inversa", "o cliente fica sem dinheiro e sem produto por uma janela"], ["o passo que falhou não é desfeito", "o estorno de uma cobrança que não aconteceu"], ["a chave de idempotência por passo", "repetir a saga depois de uma queda cobra duas vezes"], ["`orfas` não é engolido", "um estorno que falhou deixa o sistema inconsistente, e ninguém sabe"]]}},
  {"h2": "Para ir além"},
  {"list": ["Chamadas HTTP de verdade com disjuntor e retentativa: [Microsserviços](/docs/tecnicas/microservicos).", "A saga **não** dá isolamento — entre reservar e cobrar, outro pedido vê o estoque reservado.", "A referência: [Arcane.Malha](/docs/biblioteca/malha)."]},
  {"p": "Volte para [todos os tipos de projeto](/docs/projetos)."},
];

const headings = [{ id: 'estrutura', text: "Estrutura", level: 2 as const }, { id: 'o-nucleo', text: "O núcleo", level: 2 as const }, { id: 'o-teste', text: "O teste", level: 2 as const }, { id: 'as-decisoes', text: "As decisões", level: 2 as const }, { id: 'para-ir-alem', text: "Para ir além", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Pedido distribuído"}
      description={"Reservar, cobrar e despachar em três serviços — e desfazer em ordem inversa quando um falha."}
      href={"/docs/projetos/saga"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
