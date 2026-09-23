// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/lavra_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Escalares próprios",
  description: "Data, dinheiro e CPF como tipo — validados na fronteira, uma vez.",
};

const blocos: Bloco[] = [
  {"p": "Um campo `String` que na verdade é uma data acaba validado em quinze lugares — e em catorze deles com uma regra ligeiramente diferente. Um **escalar próprio** move a validação para a fronteira, onde ela acontece uma vez."},
  { code: `adopt Arcane.Lavra as Lavra
adopt Arcane.Time as T

action data_para_texto(valor):
    yield str(valor)

action data_de_texto(texto):
    partes := texto.split("-")
    given len(partes) is not 3:
        trigger "uma Data é 'AAAA-MM-DD'"
    yield texto

esq := Lavra.esquema("agenda")
Lavra.escalar(esq, "Data", data_para_texto, data_de_texto,
              "uma data no formato AAAA-MM-DD")

record Evento:
    id: Integer
    quando: String

Lavra.tipo(esq, Evento)
Lavra.campo(esq, "Evento", "quando", "Data!")
Lavra.busca(esq, "evento", "Evento",
    resolve := lambda r, a, c => Evento(1, "2026-09-22"))
Lavra.conferir(esq)

r := Lavra.executar(esq, "busca:\\n    evento:\\n        quando")
assert r["dados"]["evento"]["quando"] is "2026-09-22"
out r["dados"]`, lang: 'df' },
  {"h2": "A validação acontece na entrada, e a recusa é clara"},
  { code: `adopt Arcane.Lavra as Lavra

action de_texto(texto):
    given len(texto.split("-")) is not 3:
        // 'Lavra.erro' vira um erro da RESPOSTA, com código; um
        // 'trigger' de texto vira falha do servidor, e o cliente
        // recebe 500 onde devia receber "o argumento está errado".
        trigger Lavra.erro("uma Data é 'AAAA-MM-DD'", "argumento")
    yield texto

esq := Lavra.esquema("a")
Lavra.escalar(esq, "Data", lambda v => str(v), de_texto)
Lavra.busca(esq, "quando", "String",
    args := {"dia": "Data!"}, resolve := lambda r, a, c => a["dia"])
Lavra.conferir(esq)

bom := Lavra.executar(esq, 'busca:\\n    quando(dia: "2026-01-01")')
assert bom["dados"]["quando"] is "2026-01-01"

ruim := Lavra.executar(esq, 'busca:\\n    quando(dia: "ontem")')
assert len(ruim["erros"]) is 1
out ruim["erros"][0]["mensagem"]`, lang: 'df' },
  {"h2": "Os quatro que quase todo esquema quer"},
  {"table": {"head": ["Escalar", "Por que não `String`"], "rows": [["`Data`, `DataHora`", "fuso, formato e ordenação — e um `String` não ordena como data"], ["`Dinheiro`", "`Float` **não serve**: 0,1 + 0,2 não é 0,3. Use `Decimal`, e transporte como texto"], ["`Email`, `Cpf`", "a validação passa a existir num lugar só, e o tipo documenta"], ["`URL`", "recusar `javascript:` na fronteira é mais barato que em cada tela"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Dinheiro em `Float` é o defeito que ninguém vê", "texto": "Ele funciona em todos os testes com valores pequenos, e aparece no fechamento do mês com um centavo de diferença. A linguagem tem `19.99d` e `Arcane.Decimal`, e recusa misturar `Decimal` com `Float` de propósito — justamente para a falha aparecer na fronteira, e não no relatório."}},
];

const headings = [{ id: 'a-validacao-acontece-na-entrada-e-a-recusa-e-clara', text: "A validação acontece na entrada, e a recusa é clara", level: 2 as const }, { id: 'os-quatro-que-quase-todo-esquema-quer', text: "Os quatro que quase todo esquema quer", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Escalares próprios"}
      description={"Data, dinheiro e CPF como tipo — validados na fronteira, uma vez."}
      href={"/docs/lavra/escalares"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
