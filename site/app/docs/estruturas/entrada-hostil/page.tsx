// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ler entrada hostil",
  description: "Todo tamanho que vem do arquivo é suspeito: as cinco conferências antes de interpretar um byte.",
};

const blocos: Bloco[] = [
  {"p": "Um leitor de formato binário é a porta mais atacada de um sistema: o arquivo vem de fora, e cada número dentro dele — tamanho, contagem, deslocamento — decide **quanto** o programa vai ler e **onde**. Em C, confiar num desses números é o estouro de buffer clássico. Aqui a memória não corre risco, mas o programa ainda pode travar, alocar gigabytes ou ler o lugar errado."},
  {"table": {"head": ["Confira", "Contra", "Senão"], "rows": [["a assinatura", "a constante do formato", "interpreta um arquivo de outro formato"], ["o tamanho declarado", "o que realmente chegou", "fatia além do fim"], ["a contagem", "um teto razoável", "aloca um cluster de um bilhão de itens"], ["o deslocamento", "o intervalo do próprio arquivo", "lê fora dele"], ["a conferência (CRC)", "os dados", "interpreta lixo como dado válido"]]}},
  { code: `adopt Arcane.Estrutura as Est
adopt Arcane.Bytes as Bytes

steady MAX_ITENS := 10000
Cab := Est.definir("Cab", [["magica", "char", 4], ["quantos", "u32"]], "rede", yes)
Item := Est.definir("Item", [["id", "u32"]], "rede", yes)

action ler_lista(dados):
    given len(dados) smaller Cab.tamanho:
        trigger "arquivo menor que o cabeçalho"
    cab := Cab.ler(dados)
    given cab["magica"] is not "LIST":
        trigger $"assinatura '{cab["magica"]}' não é de uma lista"
    given cab["quantos"] bigger MAX_ITENS:
        trigger $"{cab["quantos"]} itens passa do teto de {MAX_ITENS}"
    precisa := Cab.tamanho + cab["quantos"] * Item.tamanho
    given precisa bigger len(dados):
        trigger $"declara {cab["quantos"]} itens ({precisa} bytes) e o arquivo tem {len(dados)}"
    yield [j["id"] cycle j in Est.janelas(dados, Item, cab["quantos"], Cab.tamanho)]

bom := Bytes.concatenar(Cab({"magica": "LIST", "quantos": 2}).bytes(),
    Item({"id": 7}).bytes(), Item({"id": 9}).bytes())
assert ler_lista(bom) is [7, 9]

mentiroso := Cab({"magica": "LIST", "quantos": 4000000000}).bytes()
recusado := void
monitor:
    ler_lista(mentiroso)
handle Error as e:
    recusado := e.message
assert recusado.contains("teto")`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Teste com lixo", "texto": "O teste que mais acha defeito num leitor binário é o de propriedade: milhares de entradas aleatórias, e a única exigência é que o leitor **recuse com erro da linguagem** — nunca trave, nunca estoure memória. Ver [Teste por propriedade](/docs/crucible/propriedades)."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Ler entrada hostil"}
      description={"Todo tamanho que vem do arquivo é suspeito: as cinco conferências antes de interpretar um byte."}
      href={"/docs/estruturas/entrada-hostil"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
