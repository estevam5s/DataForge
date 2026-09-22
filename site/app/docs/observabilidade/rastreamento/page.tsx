// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/observabilidade_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Rastreamento",
  description: "Trechos com pai e filho: a árvore de onde o tempo de um pedido foi gasto, e em qual etapa ele falhou.",
};

const blocos: Bloco[] = [
  {"p": "A métrica diz que o pedido levou 800 ms; o **rastreamento** diz em quê. Cada etapa abre um trecho, com o trecho de fora como pai, e fecha com o estado. A árvore resultante mostra onde o tempo foi — e qual trecho falhou."},
  { code: `adopt Arcane.Observar as O

p := O.painel("importacao")
tudo := O.abrir(p, "importar")
baixar := O.abrir(p, "baixar", tudo)
O.fechar(p, baixar)
validar := O.abrir(p, "validar", tudo)
O.fechar(p, validar, "falhou", "linha 812: CPF inválido")
O.fechar(p, tudo, "falhou")

trechos := O.trechos(p)
falhou := [t cycle t in trechos given t["estado"] is "falhou" and t["pai"] is not void]
assert falhou[0]["nome"] is "validar"
assert falhou[0]["detalhe"].contains("linha 812")`, lang: 'df' },
  {"h2": "Fechar sempre, até no erro"},
  {"p": "Um trecho aberto que nunca fecha some do relatório — justamente o da etapa que falhou. `O.cronometrar` abre, roda e fecha com o estado certo, mesmo quando a ação levanta:"},
  { code: `adopt Arcane.Observar as O

p := O.painel("job")
monitor:
    O.cronometrar(p, "calcular", lambda => 1 / 0)
handle Error:
    out "falhou — e o trecho foi fechado assim mesmo"
assert O.trechos(p)[0]["estado"] is "falhou"`, lang: 'df' },
  {"p": "Entre serviços, o id do rastreamento atravessa a rede no cabeçalho: ver [`Arcane.Malha`](/docs/tecnicas/microservicos) e `Contexto.propagar`."},
];

const headings = [{ id: 'fechar-sempre-ate-no-erro', text: "Fechar sempre, até no erro", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Rastreamento"}
      description={"Trechos com pai e filho: a árvore de onde o tempo de um pedido foi gasto, e em qual etapa ele falhou."}
      href={"/docs/observabilidade/rastreamento"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
