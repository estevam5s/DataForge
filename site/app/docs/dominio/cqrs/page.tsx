// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "CQRS",
  description: "O lado que decide e o lado que responde, separados: quando isso simplifica, e quando é peso morto.",
};

const blocos: Bloco[] = [
  {"p": "CQRS separa **comando** (muda o estado, e pode ser recusado) de **consulta** (lê, e nunca muda). No lado do comando, o modelo existe para proteger invariantes; no da consulta, para responder rápido. Tentar que um modelo só faça as duas coisas é de onde vem a tabela com quarenta colunas e três índices que brigam entre si."},
  { code: `adopt Arcane.Dominio as D

// evoluir: o estado depois de um fato. Pura, e nunca recusa nada.
aplicar := {
    "ContaAberta": lambda s, d: {"titular": d["titular"], "saldo": 0, "aberta": yes},
    "Depositado": lambda s, d: {...s, "saldo": s["saldo"] + d["valor"]},
    "Sacado": lambda s, d: {...s, "saldo": s["saldo"] - d["valor"]},
    "ContaEncerrada": lambda s, d: {...s, "aberta": no}
}

// decidir: os fatos que um comando produz — ou o motivo da recusa.
action decidir(estado, comando):
    tipo := comando["tipo"]
    given tipo is "abrir":
        yield [{"nome": "ContaAberta", "dados": {"titular": comando["titular"]}}]
    given not (estado["aberta"] ?? no):
        trigger "a conta não está aberta"
    given tipo is "depositar":
        yield [{"nome": "Depositado", "dados": {"valor": comando["valor"]}}]
    given tipo is "sacar":
        given comando["valor"] bigger estado["saldo"]:
            trigger $"saldo {estado["saldo"]} não cobre {comando["valor"]}"
        yield [{"nome": "Sacado", "dados": {"valor": comando["valor"]}}]
    trigger $"comando desconhecido: {tipo}"

armazem := D.armazem()

// ── lado da consulta: um vault pronto para a tela ──
saldos := {}
action ao_gravar(r):
    given r["nome"] is "ContaAberta":
        saldos[r["fluxo"]] := 0
    orif r["nome"] is "Depositado":
        saldos[r["fluxo"]] += r["dados"]["valor"]
    orif r["nome"] is "Sacado":
        saldos[r["fluxo"]] -= r["dados"]["valor"]
armazem.assinar(ao_gravar)

// ── lado do comando: decide, e grava ──
action comandar(conta, comando):
    historia := armazem.ler(conta)
    armazem.anexar(conta, decidir(D.reconstituir(historia, aplicar), comando), len(historia))

comandar("a", {"tipo": "abrir", "titular": "Ana"})
comandar("a", {"tipo": "depositar", "valor": 90})
comandar("b", {"tipo": "abrir", "titular": "Bia"})
assert saldos is {"a": 90, "b": 0}      // a leitura não reconstitui nada`, lang: 'df' },
  {"table": {"head": ["Vale a pena quando", "É peso morto quando"], "rows": [["as leituras são muito mais numerosas e diferentes das escritas", "a tela mostra exatamente o que se grava"], ["o modelo de escrita tem invariantes que a tela não precisa ver", "é um CRUD"], ["a leitura pode estar um pouco atrasada", "a leitura precisa ver a escrita no mesmo instante"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Consistência eventual", "texto": "Com a projeção atualizada por assinatura, no mesmo processo, ela está em dia quando `anexar` volta. Numa fila entre os dois lados, não: a tela pode mostrar o saldo de antes por alguns milissegundos. Diga isso a quem desenha a tela — \"acabei de depositar e o saldo não mudou\" vira chamado de suporte."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"CQRS"}
      description={"O lado que decide e o lado que responde, separados: quando isso simplifica, e quando é peso morto."}
      href={"/docs/dominio/cqrs"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
