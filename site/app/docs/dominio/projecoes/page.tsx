// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/dominio_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Projeções",
  description: "Modelos de leitura montados dos eventos: idempotentes, reconstruíveis, e cada um do tamanho da sua pergunta.",
};

const blocos: Bloco[] = [
  {"p": "Reconstituir o agregado responde a perguntas sobre **uma** conta. \"Quanto entrou hoje em todas as contas?\" exigiria reconstituir todas. A projeção é a resposta pronta: um estado pequeno, atualizado a cada evento que interessa a ela, e que ignora o resto."},
  { code: `adopt Arcane.Dominio as D

armazem := D.armazem()
depositos := D.projecao({
    "Depositado": lambda s, d: {"total": s["total"] + d["valor"], "quantos": s["quantos"] + 1}
}, {"total": 0, "quantos": 0})
armazem.assinar(depositos.aplicar)

armazem.anexar("a", [{"nome": "ContaAberta", "dados": {}}, {"nome": "Depositado", "dados": {"valor": 50}}])
armazem.anexar("b", [{"nome": "Depositado", "dados": {"valor": 30}}])

assert depositos.estado() is {"total": 80, "quantos": 2}   // ContaAberta foi ignorado`, lang: 'df' },
  {"h2": "Idempotente pela posição"},
  {"p": "Todo registro do armazém tem uma `posicao` global. A projeção guarda a última aplicada e **não conta de novo** o que já viu — e reentrega acontece: na recuperação de uma falha, ao reler o histórico, ao receber o mesmo evento de dois caminhos."},
  { code: `adopt Arcane.Dominio as D

armazem := D.armazem()
armazem.anexar("a", [{"nome": "Depositado", "dados": {"valor": 50}}])
p := D.projecao({"Depositado": lambda s, d: {"total": s["total"] + d["valor"]}}, {"total": 0})

cycle r in armazem.todos() + armazem.todos():     // o mesmo registro, duas vezes
    p.aplicar(r)
assert p.estado()["total"] is 50

// um bug na projeção? conserte o aplicador e reconstrua do histórico
assert p.reconstruir(armazem.todos())["total"] is 50`, lang: 'df' },
  {"callout": {"tipo": "dica", "titulo": "Uma projeção por pergunta", "texto": "\"Total do dia\", \"clientes com saldo negativo\" e \"extrato da conta\" são três projeções, e não uma tabela com três usos. Cada uma é pequena, e jogar uma fora e reconstruir do histórico custa só tempo."}},
];

const headings = [{ id: 'idempotente-pela-posicao', text: "Idempotente pela posição", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Projeções"}
      description={"Modelos de leitura montados dos eventos: idempotentes, reconstruíveis, e cada um do tamanho da sua pergunta."}
      href={"/docs/dominio/projecoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
