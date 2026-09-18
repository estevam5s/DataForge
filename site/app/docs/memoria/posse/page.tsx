// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/memoria_posse.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Posse e empréstimo",
  description: "Arcane.Posse: dono exclusivo com liberação determinística, empréstimo com escopo, contagem de referência que solta na hora certa, e a referência fraca que quebra o ciclo.",
};

const blocos: Bloco[] = [
  {"p": "Numa linguagem com coleta automática, **vazar memória quase nunca é o problema**: o coletor resolve. O que ele não resolve é o **recurso** — o arquivo que não fecha, a conexão que fica aberta, o cadeado que ninguém solta — porque o coletor não promete *quando* passa. E há o defeito irmão: duas partes do programa escrevendo no mesmo objeto porque nenhuma delas sabe quem manda nele."},
  {"p": "`Arcane.Posse` traz a disciplina de posse para esse mundo: quem é o dono, quem tomou emprestado, e **quando** solta."},
  {"callout": {"tipo": "atencao", "titulo": "O que isto NÃO é", "texto": "Não é o borrow checker do Rust, e fingir que é seria pior que não ter. Nada aqui vira endereço inválido — o coletor continua no caminho, e a integridade da memória nunca esteve em risco. O que a posse protege é o **protocolo**: soltar uma vez, não usar depois, e não escrever no meio da leitura de outro."}},
  {"h2": "Dono: posse exclusiva, liberação na hora"},
  { code: `adopt Arcane.Posse as P

fechados := []
d := P.dono("conexao", lambda x => fechados.append(x))

assert d.usar(lambda x => len(x)) is 7     // empresta para ler
assert d.vivo()

d.soltar()                                  // o finalizador roda AGORA
assert not d.vivo()
assert fechados is ["conexao"]

d.soltar()                                  // idempotente: nada acontece
assert len(fechados) is 1`, lang: 'df' },
  {"p": "Usar depois de soltar é erro, e a mensagem diz o que aconteceu — não \"objeto inválido\":"},
  { code: `adopt Arcane.Posse as P

d := P.dono("arquivo")
d.soltar()

monitor:
    d.usar(lambda x => x)
    assert no
handle RuntimeError as e:
    assert "soltou" in e.message`, lang: 'df' },
  {"h3": "com: o RAII, inclusive no caminho de erro"},
  {"p": "Metade dos recursos vaza pelo **caminho de erro** — que é justamente o que ninguém testa. `P.com` solta no fim, sempre."},
  { code: `adopt Arcane.Posse as P

fechados := []

valor := P.com(P.dono("a", lambda x => fechados.append(x)),
               lambda x => len(x))
assert valor is 1 and fechados is ["a"]

monitor:
    P.com(P.dono("b", lambda x => fechados.append(x)),
          lambda x => trigger "falhou no meio")
handle Error as e:
    assert e.message is "falhou no meio"

assert fechados is ["a", "b"]               // soltou mesmo falhando`, lang: 'df' },
  {"h2": "Mover: quem move, perde"},
  { code: `adopt Arcane.Posse as P

a := P.dono([1, 2])
b := a.mover()

assert a.movido()
assert b.usar(lambda x => len(x)) is 2

monitor:
    a.usar(lambda x => len(x))
    assert no
handle RuntimeError as e:
    assert "moveu" in e.message`, lang: 'df' },
  {"p": "E o `dataforge check` acusa **antes de rodar** quando dá para provar pelo fluxo do arquivo:"},
  { code: `// dataforge check acusa a última linha com 'posse-movida':
//
//   a := P.dono([1])
//   b := a.mover()
//   a.usar(lambda x => len(x))     ← 'a' já foi movido (linha 2)
out "veja o bloco acima" `, lang: 'df' },
  {"h3": "Cópia e clone são coisas diferentes"},
  {"table": {"head": ["Forma", "O que faz", "Quando"], "rows": [["`copiar()`", "outro dono do **mesmo** valor", "o valor é o recurso: uma conexão, um socket"], ["`clonar()`", "outro dono de uma **cópia**", "o valor é o dado, e cada um segue o seu caminho"], ["`clonar(copiador)`", "a cópia que você escreve", "quando a profundidade é sua decisão"]]}},
  { code: `adopt Arcane.Posse as P

original := P.dono([1, 2])

rasa := original.copiar()
rasa.mudar(lambda x => x.append(3))         // mexe no MESMO valor

funda := original.clonar(lambda x => [...x])
funda.mudar(lambda x => x.append(9))        // mexe na cópia

assert original.usar(lambda x => len(x)) is 3
assert funda.usar(lambda x => len(x)) is 4`, lang: 'df' },
  {"h2": "Empréstimo: muitos leem, ou um escreve"},
  {"p": "A regra do borrow checker, cobrada **quando roda** — como o `RefCell`. O empréstimo vive no corpo que o recebeu, e não até o fim do bloco: é o mesmo efeito prático dos *non-lexical lifetimes*, por um caminho mais simples."},
  { code: `adopt Arcane.Posse as P

c := P.celula({"n": 0})

assert c.ler(lambda v => v["n"]) is 0
c.escrever(lambda v => v.set("n", 5))
assert c.ler(lambda v => v["n"]) is 5
assert c.emprestimos() is 0                 // nada aberto agora

// duas leituras ao mesmo tempo: pode
assert c.ler(lambda v => c.ler(lambda w => 1)) is 1

// escrever no meio de uma leitura: não
monitor:
    c.ler(lambda v => c.escrever(lambda w => w.set("n", 9)))
    assert no
handle RuntimeError as e:
    assert "lendo" in e.message`, lang: 'df' },
  {"p": "E o empréstimo não sobrevive ao escopo que o criou:"},
  { code: `adopt Arcane.Posse as P

d := P.dono([1, 2])
fugitivo := d.emprestar()      // sem corpo, o empréstimo já nasce encerrado

monitor:
    fugitivo.ler()
    assert no
handle RuntimeError as e:
    assert "escopo" in e.message`, lang: 'df' },
  {"h2": "Compartilhado: contagem determinística"},
  {"p": "Cada `clonar()` soma um; cada `soltar()` tira um. Quando o **último** sai, o finalizador roda — naquele instante, e não quando o coletor decidir passar. É essa previsibilidade que justifica a peça existir ao lado de uma referência comum."},
  { code: `adopt Arcane.Posse as P

fechados := []
a := P.compartilhado("cache", lambda x => fechados.append(x))
b := a.clonar()
c := a.clonar()

assert a.contar() is 3
b.soltar()
assert a.contar() is 2 and fechados is []

c.soltar()
a.soltar()
assert a.contar() is 0 and fechados is ["cache"]`, lang: 'df' },
  {"p": "`P.atomico` é o mesmo com a contagem válida **entre threads** — o `Arc`. A contagem sem trava perde incrementos em silêncio; medido neste repositório, 40.425 de 80.000."},
  { code: `adopt Arcane.Posse as P
adopt Arcane.Concurrent as C

raiz := P.atomico("recurso")
copias := []

action clonar_uma(i):
    copias.append(raiz.clonar())

C.para_cada(clonar_uma, [i cycle i in range(1, 51)])
assert raiz.contar() is 51`, lang: 'df' },
  {"h2": "O ciclo vaza — e a referência fraca o quebra"},
  {"p": "Dois compartilhados que se apontam nunca chegam a zero, e o finalizador de nenhum dos dois roda. É o problema do `Rc` em qualquer linguagem, e aqui ele aparece como é, em vez de sumir num silêncio:"},
  { code: `adopt Arcane.Posse as P

fechados := []
pai := P.compartilhado({"nome": "pai"}, lambda x => fechados.append("pai"))
filho := P.compartilhado({"nome": "filho"}, lambda x => fechados.append("filho"))

pai.usar(lambda v => v.set("filho", filho.clonar()))    // forte
filho.usar(lambda v => v.set("pai", pai.clonar()))      // forte: o ciclo

pai.soltar()
filho.soltar()
assert fechados is []                       // ninguém soltou: os dois vazam`, lang: 'df' },
  {"p": "A saída é a mesma de sempre: uma das voltas é fraca."},
  { code: `adopt Arcane.Posse as P

fechados := []
pai := P.compartilhado({"nome": "pai"}, lambda x => fechados.append("pai"))
filho := P.compartilhado({"nome": "filho"}, lambda x => fechados.append("filho"))

pai.usar(lambda v => v.set("filho", filho.clonar()))    // forte
filho.usar(lambda v => v.set("pai", P.fraco(pai)))      // FRACA: não conta

filho.soltar()
pai.soltar()
assert fechados is ["pai", "filho"]         // o de fora primeiro, e o que ele possuía`, lang: 'df' },
  {"p": "A fraca responde `Talvez` — ela não promete que o valor ainda existe, e o tipo diz isso:"},
  { code: `adopt Arcane.Posse as P

forte := P.compartilhado({"id": 1})
fraca := P.fraco(forte)

assert fraca.vivo() and fraca.obter().tem()
forte.soltar()
assert not fraca.vivo()
assert not fraca.obter().tem()`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Quem solta, solta o que possuía", "texto": "Um dono que guarda outro dono é dono dos dois: ao soltar, o de dentro é solto junto — é o *drop glue*. Sem isso, soltar o de fora deixaria o de dentro aberto, que é exatamente o vazamento que a peça existe para evitar."}},
  {"h2": "O que o `check` prova"},
  {"table": {"head": ["Código", "Acusa", "Severidade"], "rows": [["`posse-movida`", "usar um nome depois de `mover()`, com a linha do movimento", "erro"], ["`recurso-vazado`", "`P.dono(…)` numa ação que ninguém solta, move, devolve nem passa adiante", "aviso"], ["`emprestimo-escapa`", "`d.usar(lambda x => x)` — o corpo devolve o próprio empréstimo", "aviso"]]}},
  {"p": "Os dois últimos são **aviso**, e não erro, porque a análise vê um arquivo só: o recurso pode ser guardado num campo, entregue por um caminho que este arquivo não enxerga, ou solto num `defer`. E a acusação só vale para o que **nasceu** de `Arcane.Posse` — um blueprint com um método chamado `mover` não tem nada a ver com posse."},
  {"h2": "O que não existe, e por quê"},
  {"table": {"head": ["Não existe", "Por quê"], "rows": [["ownership imposto pela linguagem", "a posse aqui é **opt-in**: ela vale para o que você declara com `P.dono`. Impor a todo valor exigiria mudar a semântica de atribuição da linguagem inteira"], ["lifetimes explícitos (`'a`), elisão, variância", "não há inferência de região em tempo de compilação: o empréstimo tem escopo de **corpo**, e a análise estática cobre o que o fluxo de um arquivo prova"], ["ponteiro cru, aritmética de endereço, `unsafe`", "não há endereço para manipular: o valor é um objeto do interpretador"], ["stack vs heap, `Box` para mover ao heap", "a distinção não existe aqui; `Dono` é sobre **protocolo**, não sobre onde o valor mora"], ["borrow checker em tempo de compilação", "a regra é cobrada quando roda (como `RefCell`), e o `check` prova o subconjunto que o fluxo permite"]]}},
];

const headings = [{ id: 'dono-posse-exclusiva-liberacao-na-hora', text: "Dono: posse exclusiva, liberação na hora", level: 2 as const }, { id: 'com-o-raii-inclusive-no-caminho-de-erro', text: "com: o RAII, inclusive no caminho de erro", level: 3 as const }, { id: 'mover-quem-move-perde', text: "Mover: quem move, perde", level: 2 as const }, { id: 'copia-e-clone-sao-coisas-diferentes', text: "Cópia e clone são coisas diferentes", level: 3 as const }, { id: 'emprestimo-muitos-leem-ou-um-escreve', text: "Empréstimo: muitos leem, ou um escreve", level: 2 as const }, { id: 'compartilhado-contagem-deterministica', text: "Compartilhado: contagem determinística", level: 2 as const }, { id: 'o-ciclo-vaza-e-a-referencia-fraca-o-quebra', text: "O ciclo vaza — e a referência fraca o quebra", level: 2 as const }, { id: 'o-que-o-check-prova', text: "O que o `check` prova", level: 2 as const }, { id: 'o-que-nao-existe-e-por-que', text: "O que não existe, e por quê", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Posse e empréstimo"}
      description={"Arcane.Posse: dono exclusivo com liberação determinística, empréstimo com escopo, contagem de referência que solta na hora certa, e a referência fraca que quebra o ciclo."}
      href={"/docs/memoria/posse"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
