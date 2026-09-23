// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/posse_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Mover, emprestar e copiar",
  description: "As três formas de passar um recurso adiante — e o que cada uma promete.",
};

const blocos: Bloco[] = [
  {"p": "Passar um recurso para outra parte do programa tem três significados diferentes, e confundi-los é de onde vem quase todo bug de recurso."},
  {"table": {"head": ["", "O que acontece", "Quem fecha"], "rows": [["**mover**", "o dono antigo perde o valor", "o novo dono"], ["**emprestar**", "o outro usa, e devolve", "o dono, como antes"], ["**copiar**", "há dois valores independentes", "cada um o seu"]]}},
  { code: `adopt Arcane.Posse as Posse

original := Posse.dono({"id": 1}, void, "sessao")
novo := original.mover()

// O antigo perdeu: usá-lo é erro, e o erro diz que foi movido.
assert original.movido() is yes
assert novo.usar(lambda v => v["id"]) is 1

monitor:
    original.usar(lambda v => v["id"])
    assert no
handle Error as e:
    out e.message`, lang: 'df' },
  {"h2": "Emprestar, e o `com` que SOLTA"},
  {"p": "Duas peças parecidas com propósitos diferentes, e trocá-las é o erro mais comum desta área:"},
  {"table": {"head": ["", "`d.usar(acao)`", "`Posse.com(d, acao)`"], "rows": [["o que faz", "empresta para **ler**, e devolve", "usa e **solta** no fim"], ["o dono depois", "continua vivo", "**solto**"], ["equivale a", "um empréstimo", "o `defer` aplicado a um dono"], ["quando", "no meio do trabalho", "na última vez que se usa aquele recurso"]]}},
  { code: `adopt Arcane.Posse as Posse

// 'usar' empresta e devolve: o dono continua vivo.
d := Posse.dono([1, 2, 3])
assert d.usar(lambda v => len(v)) is 3
assert d.vivo() is yes
assert Posse.estado(d)["emprestimos"] is 0
d.soltar()

// 'com' é RAII: ele usa e SOLTA — inclusive quando o corpo falha,
// que é justamente o caminho por onde metade dos recursos vaza.
soltos := []
d2 := Posse.dono([1, 2], lambda v => soltos.append("fechou"))
assert Posse.com(d2, lambda v => len(v)) is 2
assert d2.solto() is yes
assert soltos is ["fechou"]

// E com erro no meio, ele solta do mesmo jeito.
d3 := Posse.dono([1], lambda v => soltos.append("fechou 3"))
monitor:
    Posse.com(d3, lambda v => 1 / 0)
handle Error:
    out "a ação falhou…"
assert d3.solto() is yes
assert soltos is ["fechou", "fechou 3"]`, lang: 'df' },
  {"h2": "Não se escreve no meio de uma leitura"},
  {"p": "É a regra que dá nome à disciplina: enquanto há um empréstimo de leitura vivo, um empréstimo **exclusivo** é recusado. Sem isso, a coleção muda debaixo de quem a percorre — e o sintoma é um item pulado, não um erro."},
  { code: `adopt Arcane.Posse as Posse

cel := Posse.celula([1, 2, 3])

// Ler e escrever recebem uma AÇÃO, e é isso que dá o escopo: o valor
// não escapa, e a exclusividade vale só enquanto a ação roda.
assert cel.ler(lambda v => len(v)) is 3

// O que a ação devolve passa a ser o valor — inclusive num número ou
// num texto, onde não há como mexer no lugar.
cel.escrever(lambda v => [...v, 4])
assert cel.ler(lambda v => len(v)) is 4

contador := Posse.celula(10)
contador.escrever(lambda v => v + 1)
assert contador.ler(lambda v => v) is 11

// 'trocar' devolve o anterior e põe o novo, sem janela entre os dois.
antigo := cel.trocar([9])
assert len(antigo) is 4
assert cel.ler(lambda v => v[0]) is 9`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Uma escrita que não escrevia", "texto": "`escrever` entregava o valor para a ação mexer **no lugar** e descartava o retorno. Num cluster isso funciona por acidente; num número, `escrever(lambda v => v + 1)` não escrevia nada — e o programa seguia com o valor velho, calado. Hoje o retorno é guardado, e devolver `void` continua sendo mexer no lugar."}},
  {"h2": "Copiar é RASA, e isso importa"},
  {"p": "`copiar()` devolve **outro dono do mesmo valor** — é a cópia rasa. Os dois podem soltar sem erro (soltar é idempotente), mas o valor lá dentro continua sendo um só:"},
  { code: `adopt Arcane.Posse as Posse

d := Posse.dono({"itens": [1, 2]})
c := d.copiar()

// Dois DONOS, um valor: mexer por um aparece no outro.
c.mudar(lambda v => {"itens": [...v["itens"], 3]})
assert c.usar(lambda v => len(v["itens"])) is 3
assert d.usar(lambda v => len(v["itens"])) is 2   // o 'd' guarda o antigo

// Para dois valores de verdade, copie o VALOR, e não o dono:
adopt Arcane.Objetos as Obj
outro := Posse.dono(Obj.clonar_fundo(d.usar(lambda v => v)))
outro.mudar(lambda v => {"itens": [...v["itens"], 9]})
assert d.usar(lambda v => len(v["itens"])) is 2`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Copiar um recurso quase nunca é o que se quer", "texto": "Copiar um **valor** é barato e seguro. Copiar um dono de arquivo aberto dá dois objetos que apontam para o mesmo descritor, e aí os dois vão fechá-lo. Por isso a cópia é explícita, e não o padrão: o padrão é mover."}},
];

const headings = [{ id: 'emprestar-e-o-com-que-solta', text: "Emprestar, e o `com` que SOLTA", level: 2 as const }, { id: 'nao-se-escreve-no-meio-de-uma-leitura', text: "Não se escreve no meio de uma leitura", level: 2 as const }, { id: 'copiar-e-rasa-e-isso-importa', text: "Copiar é RASA, e isso importa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Mover, emprestar e copiar"}
      description={"As três formas de passar um recurso adiante — e o que cada uma promete."}
      href={"/docs/memoria/posse/mover"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
