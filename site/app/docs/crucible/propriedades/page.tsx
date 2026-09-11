// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/crucible_doc.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Teste por propriedade",
  description: "A regra em vez dos casos — e o contraexemplo encolhido até caber numa linha.",
};

const blocos: Bloco[] = [
  {"p": "Em vez de escrever trinta casos à mão, descreve-se a **regra que vale para todos** e deixa-se a máquina procurar o contraexemplo."},
  { code: `crucible "Propriedades":
    trial "inverter duas vezes volta ao original":
        Crucible.forall(
            Crucible.clusters(Crucible.integers(0, 100)),
            lambda xs: xs.reversed().reversed() is xs)

    trial "ordenar não muda o tamanho":
        Crucible.forall(
            Crucible.clusters(),
            lambda xs: len(sorted(xs)) is len(xs))`, lang: 'df' },
  {"h2": "Os geradores"},
  {"table": {"head": ["Gerador", "Produz"], "rows": [["`Crucible.integers(min, max)`", "inteiros na faixa"], ["`Crucible.floats(min, max)`", "reais na faixa"], ["`Crucible.texts(tamanho)`", "textos até o tamanho"], ["`Crucible.booleans()`", "`yes` e `no`"], ["`Crucible.clusters(item, max)`", "clusters do gerador dado"], ["`Crucible.vaults(valor, max)`", "vaults"], ["`Crucible.one_of([a, b])`", "um dos valores"]]}},
  {"p": "Geradores se combinam:"},
  { code: `crucible "Combinando":
    trial "só pares":
        pares := Crucible.integers(0, 1000).mapear(lambda n: n * 2)
        Crucible.forall(pares, lambda n: n % 2 is 0)

    trial "com filtro":
        positivos := Crucible.integers(-100, 100)
            .filtrar(lambda n: n bigger 0)
        Crucible.forall(positivos, lambda n: n bigger 0)`, lang: 'df' },
  {"h2": "O contraexemplo é encolhido"},
  {"p": "Um contraexemplo de novecentos dígitos prova que há bug e não ajuda a achar. Quando a propriedade falha, o Crucible **encolhe** até o menor valor que ainda falha:"},
  { code: `$ dataforge crucible

  1) Listas > nunca passa de dois itens

     a propriedade falhou depois de 7 caso(s).
         menor contraexemplo: [0, 0, 0]`, lang: 'bash' },
  {"p": "Sem o encolhimento, o contraexemplo seria a lista aleatória de 27 itens que falhou primeiro."},
  {"h2": "Quando vale"},
  {"list": ["**Ida e volta.** Serializar e desserializar deve devolver o original. Codificar e decodificar. Comprimir e descomprimir.", "**Invariantes.** Ordenar não muda o tamanho. Somar zero não muda o valor. Uma soma é comutativa.", "**Comparação com uma implementação óbvia.** A versão rápida deve concordar com a versão lenta e evidente."]},
  { code: `action soma_rapida(xs):
    yield sum(xs)

action soma_obvia(xs):
    total := 0
    cycle x in xs:
        total += x
    yield total

crucible "Equivalência":
    trial "as duas somas concordam":
        Crucible.forall(
            Crucible.clusters(Crucible.integers(-100, 100)),
            lambda xs: soma_rapida(xs) is soma_obvia(xs))`, lang: 'df' },
  {"callout": {"tipo": "nota", "titulo": "Não substitui os casos", "texto": "Teste por propriedade acha o que você não pensou. Casos escritos à mão documentam o que você pensou. Os dois servem, e o segundo lê melhor."}},
];

const headings = [{ id: 'os-geradores', text: "Os geradores", level: 2 as const }, { id: 'o-contraexemplo-e-encolhido', text: "O contraexemplo é encolhido", level: 2 as const }, { id: 'quando-vale', text: "Quando vale", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Teste por propriedade"}
      description={"A regra em vez dos casos — e o contraexemplo encolhido até caber numa linha."}
      href={"/docs/crucible/propriedades"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
