// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/reativo_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Operadores de fluxo",
  description: "morph, sift, distill, distintos, primeiros, pular, blocos, esperar e limitar — e quando cada um cabe.",
};

const blocos: Bloco[] = [
  {"p": "Um observável é um fluxo de valores no tempo, e os operadores montam fluxos a partir de outros — cada um devolve um **observável novo**, e o original continua como estava."},
  { code: `adopt Arcane.Reativo as R

cliques := R.observavel("cliques")
vistos := []
pares_vezes_dez := cliques.sift(lambda v: v % 2 is 0).morph(lambda v: v * 10)
inscricao := pares_vezes_dez.inscrever(lambda v: vistos.append(v))

cycle i in range(1, 7):
    cliques.emitir(i)
assert vistos is [20, 40, 60]

inscricao.cancelar()
cliques.emitir(8)
assert vistos is [20, 40, 60]           // cancelado, não recebe mais`, lang: 'df' },
  {"table": {"head": ["Operador", "Emite", "Para"], "rows": [["`morph(f)`", "`f(v)` de cada valor", "transformar"], ["`sift(cond)`", "só o que passa", "filtrar"], ["`distill(f, inicial)`", "o acumulado até aqui", "somatório corrente, estado de um jogo"], ["`distintos()`", "só quando muda em relação ao anterior", "não redesenhar à toa"], ["`primeiros(n)` · `pular(n)`", "os n primeiros · depois dos n primeiros", "o primeiro clique, ignorar o aquecimento"], ["`blocos(n)`", "grupos de n", "gravar em lote"], ["`esperar(s)`", "só quando para de chegar por s segundos", "a caixa de busca (*debounce*)"], ["`limitar(s)`", "no máximo um por janela", "o botão que não pode ser clicado duas vezes (*throttle*)"], ["`para_sinal(inicial)`", "vira um sinal com o último valor", "ligar o fluxo a um derivado"]]}},
  { code: `adopt Arcane.Reativo as R

vendas := R.observavel()
total := vendas.distill(lambda acc, v: acc + v, 0).para_sinal(0)
vendas.emitir(30)
vendas.emitir(12)
assert total.ler() is 42

leituras := R.observavel()
mudou := []
leituras.distintos().inscrever(lambda v: mudou.append(v))
cycle v in [20, 20, 21, 21, 20]:
    leituras.emitir(v)
assert mudou is [20, 21, 20]

lotes := []
fonte := R.observavel()
fonte.blocos(2).inscrever(lambda b: lotes.append(b))
cycle v in [1, 2, 3, 4]:
    fonte.emitir(v)
assert lotes is [[1, 2], [3, 4]]`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`esperar` e `limitar` são o contrário um do outro", "texto": "`esperar` emite o **último** depois do silêncio — a busca roda uma vez, quando a pessoa para de digitar. `limitar` emite o **primeiro** e ignora o resto da janela — o segundo clique no \"pagar\" não passa. Trocar os dois é o bug mais comum de interface reativa."}},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Operadores de fluxo"}
      description={"morph, sift, distill, distintos, primeiros, pular, blocos, esperar e limitar — e quando cada um cabe."}
      href={"/docs/reativo/operadores"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
