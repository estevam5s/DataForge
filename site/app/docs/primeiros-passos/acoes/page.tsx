// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Ações — dar nome a um pedaço de código",
  description: "action, parâmetros e yield: escrever uma vez, usar em qualquer lugar.",
};

const blocos: Bloco[] = [
  {"p": "Quando o mesmo pedaço de código aparece duas vezes, ele merece um nome. Uma **ação** (a *função* de outras linguagens) recebe valores, faz algo com eles, e devolve um resultado com `yield`."},
  { code: `action imc(peso, altura):
    yield peso / (altura ** 2)

action classificar(valor):
    given valor smaller 18.5:
        yield "abaixo do peso"
    given valor smaller 25:
        yield "normal"
    yield "acima do peso"

meu := imc(70, 1.75)
out $"IMC {round(meu, 1)}: {classificar(meu)}"
assert classificar(imc(70, 1.75)) is "normal"`, lang: 'df' },
  {"callout": {"tipo": "atencao", "titulo": "`yield` devolve **e sai**", "texto": "Assim que um `yield` roda, a ação termina — o que vem depois não é executado. É o que permite escrever `classificar` sem `otherwise`: se a primeira condição valer, a ação já saiu."}},
  {"h2": "Valor padrão e tipos"},
  { code: `action saudar(nome: String, cumprimento := "Ola") -> String:
    yield $"{cumprimento}, {nome}!"

assert saudar("Ana") is "Ola, Ana!"
assert saudar("Bia", "Bom dia") is "Bom dia, Bia!"
// saudar(42) e acusado pelo 'dataforge check' antes de rodar`, lang: 'df' },
  {"p": "Próximo: [O primeiro programa completo](/docs/primeiros-passos/primeiro-programa)."},
];

const headings = [{ id: 'valor-padrao-e-tipos', text: "Valor padrão e tipos", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Ações — dar nome a um pedaço de código"}
      description={"action, parâmetros e yield: escrever uma vez, usar em qualquer lugar."}
      href={"/docs/primeiros-passos/acoes"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
