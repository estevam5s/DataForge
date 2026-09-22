// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/estruturas_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Campos de bits",
  description: "Versão e tamanho do IPv4 no mesmo byte, as flags do TCP em 16 bits — com máscara, e nunca com o bitfield do C.",
};

const blocos: Bloco[] = [
  {"p": "Protocolos economizam: o primeiro byte do cabeçalho IPv4 guarda **dois** campos — a versão nos 4 bits de cima e o tamanho do cabeçalho nos 4 de baixo. `Est.campos_de_bits` descreve isso com nome, e o primeiro campo é o de **cima**, como toda RFC desenha."},
  { code: `adopt Arcane.Estrutura as Est

Ver_ihl := Est.campos_de_bits("Ver_ihl", [["versao", 4], ["ihl", 4]])
assert Ver_ihl.ler(0x45) is {"versao": 4, "ihl": 5}          // IPv4, 5 palavras de 32 bits
assert Ver_ihl.juntar({"versao": 4, "ihl": 5}) is 0x45
out Ver_ihl.mapa()`, lang: 'df' },
  {"h2": "As flags do TCP"},
  { code: `adopt Arcane.Estrutura as Est

Tcp := Est.campos_de_bits("Tcp", [
    ["deslocamento", 4], ["reservado", 3], ["ns", 1], ["cwr", 1], ["ece", 1],
    ["urg", 1], ["ack", 1], ["psh", 1], ["rst", 1], ["syn", 1], ["fin", 1]], 16)

syn_ack := Tcp.juntar({"deslocamento": 5, "syn": 1, "ack": 1})
assert syn_ack is 0x5012
flags := Tcp.ler(syn_ack)
assert flags["syn"] is 1 and flags["ack"] is 1 and flags["fin"] is 0`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "O valor que invadiria o vizinho", "texto": "Um 16 num campo de 4 bits, somado sem conferir, liga o bit do campo **ao lado**. O defeito aparece no outro campo, e a busca começa no lugar errado. `juntar` recusa (`BufferOverflowError`), com a faixa do campo na mensagem."}},
  {"callout": {"tipo": "nota", "titulo": "Por que não o bitfield do C", "texto": "`unsigned versao:4;` deixa a ordem dos bits para o compilador — e dois compiladores escolhem diferente. Todo código de rede sério usa máscara e deslocamento, que é o que `campos_de_bits` faz, com a ordem declarada."}},
];

const headings = [{ id: 'as-flags-do-tcp', text: "As flags do TCP", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Campos de bits"}
      description={"Versão e tamanho do IPv4 no mesmo byte, as flags do TCP em 16 bits — com máscara, e nunca com o bitfield do C."}
      href={"/docs/estruturas/bits"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
