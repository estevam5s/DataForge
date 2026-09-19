// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/runtime_laco.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Fibras",
  description: "Um `stream action` suspenso em cada `emit` — corrotina de verdade, com a limitação sem pilha dita com esse nome.",
};

const blocos: Bloco[] = [
  {"p": "Uma fibra aqui **não é aproximação**. Um `stream action` da linguagem já é um gerador do Python, e o interpretador suspende o corpo dele em cada `emit`. O escalonador dirige esse gerador: o valor emitido diz **o que a fibra está esperando**, e a troca de contexto é o quadro do gerador."},
  { code: `adopt Arcane.Laco as L

stream action trabalhador(nome, diario):
    cycle i from 1 to 3:
        diario.append($"{nome}{i}")
        emit L.ceder()

laco := L.novo()
diario := []
L.fibra(laco, trabalhador, ["A", diario])
L.fibra(laco, trabalhador, ["B", diario])

assert L.fibras(laco) is 2
L.rodar(laco)

// intercaladas: e isto que prova o escalonamento cooperativo
assert diario is ["A1", "B1", "A2", "B2", "A3", "B3"]
assert L.fibras(laco) is 0`, lang: 'df' },
  {"p": "Se fossem sequenciais o diário seria `A1 A2 A3 B1 B2 B3`. Elas se intercalam porque cada `emit` devolve o controle ao escalonador, que escolhe a próxima."},
  {"h2": "O que uma fibra pode esperar"},
  {"table": {"head": ["Pedido", "Retoma quando"], "rows": [["`L.ceder()`", "na próxima volta — cede sem esperar nada"], ["`L.dormir(ms)`", "passado o prazo, **sem prender thread nenhuma**"], ["`L.depois_de(ms, caixa, chave, valor)`", "passado o prazo, com o valor já na caixa"], ["`L.ler(soquete, caixa, chave)`", "houver o que ler; o dado chega pela caixa"], ["`L.escrever(soquete)`", "der para escrever sem bloquear"], ["`L.esperar(outra)`", "a outra fibra terminar"]]}},
  {"p": "A lista é **fechada**: um vault qualquer emitido por engano vira erro com a lista, e não uma fibra parada para sempre esperando algo que ninguém registrou."},
  {"h2": "A caixa, e por que ela existe"},
  {"p": "`emit` é **instrução**, não expressão: ele não devolve valor para a fibra. Então o laço entrega por um vault que a fibra passou — a **caixa**. Ser explícito aqui é melhor que fingir o contrário."},
  { code: `adopt Arcane.Laco as L

stream action espera(caixa):
    emit L.depois_de(20, caixa, "resposta", "chegou")
    caixa["visto"] := caixa["resposta"]

laco := L.novo()
caixa := {"resposta": void, "visto": void}
L.fibra(laco, espera, [caixa])
L.rodar(laco)

assert caixa["visto"] is "chegou"`, lang: 'df' },
  {"h2": "Sem pilha — e isso tem nome"},
  {"callout": {"tipo": "atencao", "titulo": "Um `emit` dentro de uma ação chamada NÃO suspende a fibra", "texto": "Só o `emit` do corpo da própria fibra suspende. É a limitação de toda corrotina **sem pilha** (*stackless*) — a mesma dos iteradores do C# e do `yield` do Python. Suspender dentro de uma chamada exige pilha própria, e isso quer dizer troca de contexto em assembly ou uma extensão em C: as duas fora de uma linguagem sem dependência externa. É por isso que esta página diz **fibra** e não *green thread*."}},
  {"h2": "Cancelar"},
  { code: `adopt Arcane.Laco as L

stream action longa(diario):
    diario.append("comecei")
    emit L.dormir(50)
    diario.append("nao chega aqui")

laco := L.novo()
diario := []
f := L.fibra(laco, longa, [diario])
L.apos(laco, 5, lambda => L.cancelar(f))
L.rodar(laco)

assert diario is ["comecei"]
assert L.cancelada(f)`, lang: 'df' },
  {"p": "Cancelar uma fibra fecha o gerador — o que roda os `defer` do corpo, como um `halt` faria. Uma thread do sistema não se cancela assim: é a vantagem concreta de a fibra ser um objeto e não um recurso do SO."},
];

const headings = [{ id: 'o-que-uma-fibra-pode-esperar', text: "O que uma fibra pode esperar", level: 2 as const }, { id: 'a-caixa-e-por-que-ela-existe', text: "A caixa, e por que ela existe", level: 2 as const }, { id: 'sem-pilha-e-isso-tem-nome', text: "Sem pilha — e isso tem nome", level: 2 as const }, { id: 'cancelar', text: "Cancelar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Fibras"}
      description={"Um `stream action` suspenso em cada `emit` — corrotina de verdade, com a limitação sem pilha dita com esse nome."}
      href={"/docs/runtime/fibras"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
