// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Sinais e derivados",
  description: "Preguiçoso, memorizado, e com as dependências descobertas executando a fórmula.",
};

const blocos: Bloco[] = [
  {"h2": "O derivado é preguiçoso e memorizado"},
  {"p": "Ele só recalcula quando **alguém lê** e alguma dependência mudou. Recalcular na escrita faria uma cadeia de dez derivados rodar dez vezes por mudança — e a maioria deles nunca é lida."},
  { code: `contas := {"n": 0}

action calcular():
    contas["n"] := contas["n"] + 1
    yield itens.ler()

steady quantos := R.derivado(calcular)

quantos.ler()
quantos.ler()
quantos.ler()
assert contas["n"] is 1      // tres leituras, uma conta so`, lang: 'df' },
  {"h2": "As dependências são descobertas, não declaradas"},
  {"p": "Não há lista para escrever: o derivado roda, e **todo sinal lido durante a execução** entra. Uma lista escrita à mão envelhece na primeira condição nova dentro da fórmula, e o sintoma é um valor que para de atualizar."},
  { code: `action calcular_frete():
    given subtotal.ler() bigger 100.0:
        yield 0.0
    yield 20.0 - cupom.ler()

steady frete := R.derivado(calcular_frete)`, lang: 'df' },
  {"p": "Abaixo de 100 o frete **leu** o cupom, e mexer no cupom o invalida. Acima de 100 a fórmula toma o outro ramo e não lê mais: a partir daí, mexer no cupom não mexe em nada. As fontes que sumiram param de notificar — sem isso, uma fórmula com `given` acumularia as dependências dos dois ramos e recalcularia por mudanças que ela nem lê mais."},
  {"h2": "Escrever o mesmo valor não notifica"},
  {"p": "Um sinal que avisa sobre `x := x` faz uma cadeia recalcular por nada e um efeito de rede disparar duas vezes. A comparação pode ser trocada: `R.sinal(v, iguais := minha_comparacao)`."},
  {"h2": "Ler sem depender"},
  {"p": "`.valor()` devolve o valor **sem** registrar a dependência — o `untracked` dos outros frameworks. Sem ele, um derivado que lê um contador de depuração passaria a recalcular a cada incremento dele."},
  {"h2": "Um ciclo é recusado, com o caminho"},
  { code: `// erro: o derivado 'a' depende de si mesmo.
//   nota: a cadeia: a → b → a
//   dica: quebre o ciclo: um dos dois precisa ser um sinal`, lang: 'text' },
  {"p": "Dizer apenas \"há um ciclo\" manda procurar em toda a fórmula; a cadeia é o que o torna quebrável."},
];

const headings = [{ id: 'o-derivado-e-preguicoso-e-memorizado', text: "O derivado é preguiçoso e memorizado", level: 2 as const }, { id: 'as-dependencias-sao-descobertas-nao-declaradas', text: "As dependências são descobertas, não declaradas", level: 2 as const }, { id: 'escrever-o-mesmo-valor-nao-notifica', text: "Escrever o mesmo valor não notifica", level: 2 as const }, { id: 'ler-sem-depender', text: "Ler sem depender", level: 2 as const }, { id: 'um-ciclo-e-recusado-com-o-caminho', text: "Um ciclo é recusado, com o caminho", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Sinais e derivados"}
      description={"Preguiçoso, memorizado, e com as dependências descobertas executando a fórmula."}
      href={"/docs/reativo/sinais"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
