// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/partida_e_seguranca.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Uma variável por thread",
  description: "Inicialização declarada por thread e finalizador quando ela acaba — o que o armazém sozinho não dá.",
};

const blocos: Bloco[] = [
  {"p": "Um armazém por thread resolve metade do problema. A outra metade é o que costuma faltar: **a inicialização declarada num lugar só**, e o **finalizador** quando a thread acaba."},
  {"p": "Sem finalizador, uma conexão aberta por thread fica aberta depois que ela morre — e o sintoma aparece no servidor, não no código."},
  { code: `adopt Arcane.Inicio as I

// a inicializacao roda UMA VEZ POR THREAD, e cada uma ve a sua
contador := I.local(lambda => {"n": 0})

caixa := I.meu(contador)
caixa["n"] := caixa["n"] + 1

assert I.meu(contador)["n"] is 1
assert I.threads_com_valor(contador) bigger_eq 1`, lang: 'df' },
  {"table": {"head": ["Símbolo", "O que faz"], "rows": [["`I.local(inicial, ao_terminar?)`", "cria a variável; `inicial` é uma **ação que constrói** o valor"], ["`I.meu(local)`", "o valor desta thread, criando-o na primeira vez"], ["`I.definir(local, v)`", "troca o valor desta thread"], ["`I.limpar(local)`", "esquece; o próximo `meu` nasce de novo"], ["`I.threads_com_valor(local)`", "quantas threads têm valor guardado"]]}},
  {"h2": "Três decisões"},
  {"p": "**`inicial` é uma ação, e não um valor.** Um valor seria compartilhado por todas as threads — que é exatamente o que a variável por thread existe para evitar. Passar um valor é recusado, com esse motivo na mensagem."},
  {"p": "**A inicialização roda fora da trava.** Ela é código de quem chamou, pode demorar, e segurar a trava ali faria uma thread lenta parar todas as outras."},
  {"callout": {"tipo": "atencao", "titulo": "O finalizador roda quando a thread é COLETADA", "texto": "Não no instante em que ela termina. É o que `weakref.finalize` garante, e prometer precisão maior seria prometer um gancho que o Python não tem. Para liberar num instante exato, use [`Arcane.Posse`](/docs/memoria/posse): lá a liberação é por **escopo**, e determinística."}},
];

const headings = [{ id: 'tres-decisoes', text: "Três decisões", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Uma variável por thread"}
      description={"Inicialização declarada por thread e finalizador quando ela acaba — o que o armazém sozinho não dá."}
      href={"/docs/partida/por-thread"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
