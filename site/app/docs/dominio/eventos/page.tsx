// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_ddd.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Eventos e unidade de trabalho",
  description: "Por que o fato espera a confirmação, e o que acontece quando ela não vem.",
};

const blocos: Bloco[] = [
  {"p": "Um evento é um fato que **aconteceu**. O nome no passado não é estilo: um evento chamado `CriarPedido` é um comando disfarçado, e quem o recebe acha que pode recusá-lo. Um `PedidoCriado` já aconteceu — quem escuta reage, e não decide."},
  { code: `e := D.evento("PedidoPago", {"valor": 120})
e.valor := 0
// erro: o evento 'PedidoPago' ja aconteceu: ele nao muda.`, lang: 'df' },
  {"h2": "O evento fica guardado até a confirmação"},
  { code: `publicados := []

action anotar(fato):
    publicados.append(fato.nome)

u := D.unidade(publicar := anotar)
u.registrar(pedido, pedidos)     // o agregado e o repositorio dele
assert len(publicados) is 0      // o mundo ainda nao sabe

u.confirmar()
assert len(publicados) is 2      // agora sim`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Publicar na hora é o defeito clássico", "texto": "O mundo reage a um fato que a transação ainda pode desfazer: o e-mail sai, e o pedido não existe. `desfazer()` descarta os eventos junto — eles nunca aconteceram."}},
  {"h2": "Todas as invariantes antes de qualquer gravação"},
  {"p": "A unidade confere **todos** os agregados registrados e só então grava **qualquer** um deles. Se a segunda gravação falhasse por invariante, a primeira já estaria no banco — e a transação de domínio teria vazado pela metade."},
  {"h2": "E não dá para desfazer o confirmado"},
  { code: `u.confirmar()
u.desfazer()
// erro: nao da para desfazer o que ja foi confirmado.
//   dica: publique um evento de compensacao`, lang: 'df' },
  {"p": "Os eventos já saíram, e quem reagiu a eles não tem como voltar atrás. A saída é a compensação — a mesma que a `Saga` do `Arcane.Malha` implementa quando a transação atravessa a rede."},
];

const headings = [{ id: 'o-evento-fica-guardado-ate-a-confirmacao', text: "O evento fica guardado até a confirmação", level: 2 as const }, { id: 'todas-as-invariantes-antes-de-qualquer-gravacao', text: "Todas as invariantes antes de qualquer gravação", level: 2 as const }, { id: 'e-nao-da-para-desfazer-o-confirmado', text: "E não dá para desfazer o confirmado", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Eventos e unidade de trabalho"}
      description={"Por que o fato espera a confirmação, e o que acontece quando ela não vem."}
      href={"/docs/dominio/eventos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
