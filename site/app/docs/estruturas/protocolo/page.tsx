// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um protocolo binário",
  description: "Mensagens TLV — tipo, tamanho, valor — com varint: escrever, ler, e o campo desconhecido que não quebra ninguém.",
};

const blocos: Bloco[] = [
  {"p": "TLV (tipo-tamanho-valor) é o desenho que sobrevive a versões: cada campo diz o próprio tamanho, então quem lê pode **pular** um campo que não conhece. É a mesma ideia do Protocol Buffers, e o motivo pelo qual um cliente antigo lê a mensagem de um servidor novo."},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

steady NOME := 1
steady IDADE := 2
steady FOTO := 9                     // um campo que a versão antiga não conhece

action campo(tipo, valor):
    yield Bytes.concatenar(Est.varint(tipo), Est.varint(len(valor)), valor)

action mensagem(campos):
    yield campos >> distill acc, c: Bytes.concatenar(acc, c) Bytes.de_texto("")

action ler(dados, conhecidos):
    saida := {}
    pos := 0
    persist pos smaller len(dados):
        t := Est.ler_varint(dados, pos)
        n := Est.ler_varint(dados, pos + t["tamanho"])
        inicio := pos + t["tamanho"] + n["tamanho"]
        given inicio + n["valor"] bigger len(dados):
            trigger $"o campo {t["valor"]} diz ter {n["valor"]} bytes e a mensagem acaba antes"
        given t["valor"] in conhecidos:
            saida[conhecidos[t["valor"]]] := Bytes.fatiar(dados, inicio, inicio + n["valor"])
        pos := inicio + n["valor"]            // o desconhecido é PULADO
    yield saida

m := mensagem([campo(NOME, Bytes.de_texto("Ana")), campo(FOTO, Bytes.de_hex("ffd8ffe0")),
               campo(IDADE, Est.varint(30))])
lido := ler(m, {NOME: "nome", IDADE: "idade"})
assert Bytes.para_texto(lido["nome"]) is "Ana"
assert Est.ler_varint(lido["idade"])["valor"] is 30`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "O tamanho vem de fora", "texto": "O tamanho de cada campo é **dado da mensagem**, e uma mensagem maliciosa diz ter 4 GB. Conferir `inicio + tamanho` contra o que chegou — antes de fatiar — é o que separa um erro legível de ler memória que não é desta mensagem. Ver [Entrada hostil](/docs/estruturas/entrada-hostil)."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Um protocolo binário"}
      description={"Mensagens TLV — tipo, tamanho, valor — com varint: escrever, ler, e o campo desconhecido que não quebra ninguém."}
      href={"/docs/estruturas/protocolo"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
