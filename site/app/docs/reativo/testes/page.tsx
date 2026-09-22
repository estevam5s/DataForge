// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Testar código reativo",
  description: "Escrever, ler, contar execuções — e aguardar o recurso sem sleep arbitrário.",
};

const blocos: Bloco[] = [
  {"p": "O modelo reativo é **síncrono** por padrão: escrever num sinal recalcula os derivados e roda os efeitos antes de a escrita voltar. Isso torna o teste direto — sem esperar, sem relógio."},
  { code: `adopt Arcane.Reativo as R

preco := R.sinal(10)
qtd := R.sinal(2)
contas := [0]

action calcular():
    contas[0] += 1
    yield preco.ler() * qtd.ler()

total := R.derivado(calcular)

assert total.ler() is 20
assert total.ler() is 20
assert contas[0] is 1              // memorizado: duas leituras, uma conta
qtd.escrever(2)                     // o mesmo valor
assert total.ler() is 20 and contas[0] is 1
qtd.escrever(3)
assert total.ler() is 30 and contas[0] is 2`, lang: 'df' },
  {"h2": "O que conferir"},
  {"table": {"head": ["Pergunta", "Como"], "rows": [["o valor está certo?", "`derivado.ler()` depois de escrever"], ["recalcula à toa?", "contar as execuções da fórmula"], ["o efeito viu um estado intermediário?", "guardar o que ele viu numa lista, e comparar"], ["vazou?", "`sinal.ouvintes()` depois de parar"], ["o recurso terminou?", "`r.aguardar(prazo)` — espera o estado, e não um tempo fixo"]]}},
  {"callout": {"tipo": "atencao", "titulo": "Nunca `sleep` para esperar um recurso", "texto": "Um `sleep(100)` passa na sua máquina e falha num CI carregado, que é onde a busca demora 150 ms. `aguardar` espera o **estado** sair de \"carregando\", com um prazo que só é atingido quando algo está de fato errado."}},
];

const headings = [{ id: 'o-que-conferir', text: "O que conferir", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Testar código reativo"}
      description={"Escrever, ler, contar execuções — e aguardar o recurso sem sleep arbitrário."}
      href={"/docs/reativo/testes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
