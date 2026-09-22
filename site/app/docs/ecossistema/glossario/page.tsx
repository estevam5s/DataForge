// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/ecossistema_mais.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Glossário",
  description: "Os termos da documentação, com a definição curta e a página que explica cada um — conferidos contra o site.",
};

const blocos: Bloco[] = [
  {"p": "A documentação usa termos de compiladores, de concorrência, de domínio e de protocolos. O glossário é também um **dado**: `Ecossistema.glossario()` devolve a lista, e `definir(termo)` busca um — com sugestão quando o nome vem quase certo."},
  { code: `adopt Arcane.Ecossistema as E

d := E.definir("SSA")
assert d["pagina"] is "/docs/compilador/ssa"
out d["definicao"]

sugestao := void
monitor:
    E.definir("dominacia")
handle Error as e:
    sugestao := e.dica
assert sugestao.contains("dominancia")

assert len(E.glossario()) bigger_eq 38`, lang: 'df' },
  {"table": {"head": ["Termo", "Em uma linha"], "rows": [["**ABI**", "a superfície do que o `relay` exporta, comparada entre versões — [ver](/docs/abi)"], ["**agregado**", "a única porta de escrita de um grupo de objetos do domínio — [ver](/docs/dominio/agregados)"], ["**ator**", "estado com dono, alcançado só por mensagem — [ver](/docs/concorrencia/atores)"], ["**canal**", "o cano entre fibras que suspende quem envia quando cheio — [ver](/docs/runtime/canais)"], ["**chamada de cauda**", "`yield f(…)` que vira salto — [ver](/docs/compilador/cauda)"], ["**contrapressão**", "o consumidor lento freando o produtor — [ver](/docs/runtime/contrapressao)"], ["**CQRS**", "o modelo que decide separado do que responde — [ver](/docs/dominio/cqrs)"], ["**cursor**", "\"onde parou\" numa listagem, opaco — [ver](/docs/api/paginacao)"], ["**dominância**", "todo caminho até B passa por A — [ver](/docs/compilador/dominancia)"], ["**ETag**", "a etiqueta de uma versão de recurso HTTP — [ver](/docs/api/precondicoes)"], ["**fibra**", "`stream action` conduzido pelo laço — [ver](/docs/runtime/fibras)"], ["**fonte de eventos**", "guardar fatos, e derivar o estado — [ver](/docs/dominio/fonte-de-eventos)"], ["**idempotência**", "repetir o pedido sem repetir o efeito — [ver](/docs/api/idempotencia)"], ["**orçamento de erro**", "as falhas que o SLO permite — [ver](/docs/observabilidade/slo)"], ["**projeção**", "modelo de leitura montado dos eventos — [ver](/docs/dominio/projecoes)"], ["**sinal**", "um valor que sabe quem depende dele — [ver](/docs/reativo/sinais)"], ["**SSA**", "cada nome recebe valor uma vez só — [ver](/docs/compilador/ssa)"], ["**STM**", "escritas que acontecem juntas, ou não acontecem — [ver](/docs/concorrencia/stm)"], ["**taxa de queima**", "a velocidade com que o orçamento é gasto — [ver](/docs/observabilidade/slo)"], ["**varint**", "o inteiro de tamanho variável do protobuf — [ver](/docs/estruturas/varint)"]]}},
  {"p": "A lista completa, com 38 termos, sai de `E.glossario()`. Ela é conferida: um termo que aponta para uma página que não existe reprova a suíte de testes."},
];

const headings: never[] = [];

export default function Pagina() {
  return (
    <DocPage
      title={"Glossário"}
      description={"Os termos da documentação, com a definição curta e a página que explica cada um — conferidos contra o site."}
      href={"/docs/ecossistema/glossario"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
