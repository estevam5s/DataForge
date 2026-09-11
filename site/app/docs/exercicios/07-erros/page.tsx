// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "07 · Erros",
  description: "10 exercícios: monitor/handle/ensure, trigger, retry e defer.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 07`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["077", "**monitor / handle**", "capture uma divisao por zero sem derrubar o programa."], ["078", "**ensure (finally)**", "garanta que a limpeza rode com ou sem erro."], ["079", "**trigger (lancar erro)**", "valide a entrada de uma acao lancando erros descritivos."], ["080", "**handle tipado**", "capture apenas um tipo de erro e deixe os outros passarem."], ["081", "**monitor sem handle propaga**", "comprove que um monitor com apenas ensure nao engole o erro."], ["082", "**guard e validate**", "compare as duas formas de pre-condicao."], ["083", "**retry**", "repita uma operacao instavel ate ter sucesso."], ["084", "**propagate**", "registre o erro e repasse para o chamador."], ["085", "**assert**", "use assert como verificacao interna e capture a falha."], ["086", "**Pilha de erros e recuperacao**", "converta valores com fallback em varias camadas."]]}},
  {"p": "Rode um isolado com `dataforge run exercicios/07-erros/077_monitor_handle.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"07 · Erros"}
      description={"10 exercícios: monitor/handle/ensure, trigger, retry e defer."}
      href={"/docs/exercicios/07-erros"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
