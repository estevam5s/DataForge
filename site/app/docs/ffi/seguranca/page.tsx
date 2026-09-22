// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ffi_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Segurança na fronteira",
  description: "As cinco formas de corromper memória chamando C, e a conferência que cada uma pede.",
};

const blocos: Bloco[] = [
  {"p": "Do lado do DataForge, todo índice é conferido e nenhum ponteiro solto existe. Do lado do C, nada disso vale. Os defeitos abaixo não dão erro na linha que os causa: aparecem depois, em outro lugar, ou derrubam o processo sem mensagem."},
  {"table": {"head": ["Defeito", "Como acontece", "A conferência"], "rows": [["assinatura errada", "`i32` onde o C quer `i64`, `f32` onde quer `double`", "copie do `.h`, nunca de memória"], ["buffer pequeno", "passar 16 bytes para uma função que escreve 64", "alocar o que a documentação pede, com folga"], ["uso depois de liberar", "guardar um ponteiro de um bloco já liberado", "`C.liberar` num lugar só, e nada guarda o ponteiro depois"], ["callback coletado", "o C guarda a função e chama depois que o lado de cá a soltou", "manter a referência viva enquanto o C puder chamar"], ["thread errada", "biblioteca que não é thread-safe chamada de duas threads", "um `mutex` em volta de toda chamada a ela"]]}},
  { code: `adopt Arcane.C as C

bloco := C.alocar(4 * C.tamanho_de("i32"))
p := C.ponteiro(bloco, "i32")
p.escrever(7)
assert p.ler() is 7
C.liberar(bloco)

recusado := no
monitor:
    C.ponteiro(C.nulo(), "i32").ler()      // o nulo é recusado, e não lido
handle Error:
    recusado := yes
assert recusado`, lang: 'df' },
  {"callout": {"tipo": "perigo", "titulo": "Nunca com entrada de fora sem conferir", "texto": "Um tamanho que vem de um arquivo ou de um pedido HTTP e vai direto para uma função C é o estouro de buffer clássico, agora no seu programa. Confira o tamanho do lado de cá — onde a conferência existe — antes de atravessar."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Segurança na fronteira"}
      description={"As cinco formas de corromper memória chamando C, e a conferência que cada uma pede."}
      href={"/docs/ffi/seguranca"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
