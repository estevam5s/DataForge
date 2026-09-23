// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/iot.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Um painel para a placa",
  description: "Vitrine e Arduino no mesmo programa: gráfico ao vivo, botão que liga o relé, e o cuidado com a thread.",
};

const blocos: Bloco[] = [
  {"p": "A Vitrine desenha painéis, e a placa produz números: juntar os dois é o caso que fecha o ciclo — ver o sensor num gráfico e agir com um botão. Mas há um detalhe que decide se funciona: **a página inteira roda de novo a cada interação**, e uma conexão serial não pode ser aberta a cada volta."},
  { code: `adopt Arcane.Vitrine as V
adopt Arcane.IoT as IoT

// V.recurso guarda o objeto POR PROCESSO: a porta abre uma vez
mark @V.recurso
action placa():
    p := IoT.conectar_simulada("uno")
    p.modo(13, "saida")
    p.modo(14, "analogico")
    p.relatar_analogico(0)
    yield p

assert placa().info()["pinos"] is 20
assert placa() is placa()            // a MESMA porta, na segunda chamada
placa().fechar()`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "Sem `V.recurso`, a porta abre a cada clique", "texto": "E a segunda abertura falha, porque a porta já está tomada pela primeira — o sintoma é um painel que funciona no primeiro carregamento e morre no primeiro clique, com um erro que fala de permissão. `V.recurso` guarda o objeto por processo, que é exatamente a vida de uma porta serial."}},
  {"h2": "O painel inteiro"},
  { code: `adopt Arcane.Vitrine as V
adopt Arcane.IoT as IoT

mark @V.recurso
action abrir():
    p := IoT.conectar_simulada("uno")
    p.modo(13, "saida")
    p.modo(14, "analogico")
    p.relatar_analogico(0)
    p.amostragem(200)
    yield p

action pagina():
    p := abrir()
    V.titulo("Estufa")

    leitura := p.analogico(0)
    colunas := V.colunas(3)
    colunas[0].metrica("Leitura", leitura)
    colunas[1].metrica("Temperatura", $"{round(IoT.tmp36(leitura), 1)} °C")
    colunas[2].metrica("Aquecedor", "ligado" given p.ler(13) otherwise "desligado")

    given V.botao("Alternar aquecedor"):
        p.escrever(13, not p.ler(13))

    V.atualizar_a_cada(2)

// Sonda: o painel testado sem navegador
s := V.testar(pagina)
s.rodar()
assert "Estufa" in s.texto()
s.clicar("Alternar aquecedor")
assert "Aquecedor" in s.texto()`, lang: 'df' },
  {"h2": "O tempo real da Vitrine é por pergunta"},
  {"p": "`V.atualizar_a_cada(2)` reexecuta a página de dois em dois segundos — é *polling*, e está escrito assim de propósito. A Vitrine não empurra dado (não usa WebSocket nem SSE), e para um painel de sensor isso é suficiente: o que muda a cada 200 ms não precisa ser visto a cada 200 ms."},
  {"h2": "Uma rota do Kiln, para a placa"},
  {"p": "Quando o que se quer é uma API — outro sistema lendo o sensor —, o Kiln serve. E aqui vale o aviso que o `check` dá sozinho:"},
  { code: `adopt Arcane.IoT as IoT

// o Kiln atende UM PEDIDO POR THREAD, e a placa é uma só:
// duas rotas escrevendo no mesmo pino ao mesmo tempo perdem ordens.
// A resposta é um mutex em volta da placa.
adopt Arcane.Concurrent as C

trava := C.mutex()
placa := IoT.conectar_simulada("uno")
placa.modo(13, "saida")

action ligar(valor):
    placa.escrever(13, valor)
    yield placa.ler(13)

// com_trava toma a trava, roda, e a SOLTA mesmo se o corpo estourar —
// soltar na mão funciona até o dia em que o corpo levanta, e aí a
// próxima thread espera para sempre.
assert C.com_trava(trava, lambda => ligar(yes)) is yes
assert C.com_trava(trava, lambda => ligar(no)) is no
placa.fechar()`, lang: 'df' },
  {"p": "O `dataforge check` **avisa** quando uma `route` escreve num nome que vem de fora (`escrita-concorrente`), e uma placa compartilhada é o caso exato: a concorrência é invisível para quem escreve a rota."},
];

const headings = [{ id: 'o-painel-inteiro', text: "O painel inteiro", level: 2 as const }, { id: 'o-tempo-real-da-vitrine-e-por-pergunta', text: "O tempo real da Vitrine é por pergunta", level: 2 as const }, { id: 'uma-rota-do-kiln-para-a-placa', text: "Uma rota do Kiln, para a placa", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Um painel para a placa"}
      description={"Vitrine e Arduino no mesmo programa: gráfico ao vivo, botão que liga o relé, e o cuidado com a thread."}
      href={"/docs/iot/painel"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
