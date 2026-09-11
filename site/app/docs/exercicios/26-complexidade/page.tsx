// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/exercicios.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "26 · Complexidade",
  description: "4 exercícios: Big-O, memoização e custo de estrutura.",
};

const blocos: Bloco[] = [
  { code: `python3 exercicios/run_all.py 26`, lang: 'bash' },
  {"h2": "Os exercícios"},
  {"table": {"head": ["#", "Título", "Enunciado"], "rows": [["213", "**Medir o crescimento, nao o relogio**", "escreva duas versoes do mesmo problema e compare as ordens."], ["214", "**Trocar tempo exponencial por memoria linear**", "faca fib(35) responder, sem esperar."], ["215", "**A estrutura certa**", "escolha entre cluster e vault pela operacao que voce faz."], ["216", "**Complexidade de espaco**", "processe mais dados do que cabem na memoria."]]}},
  {"callout": {"tipo": "dica", "titulo": "Cada um tem explicação ao lado", "texto": "Neste módulo, todo `.df` traz um `.md` com os conceitos, a saída esperada e sugestões — veja `exercicios/26-complexidade/`."}},
  {"p": "Rode um isolado com `dataforge run exercicios/26-complexidade/213_medir_o_crescimento.df`."},
];

const headings = [{ id: 'os-exercicios', text: "Os exercícios", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"26 · Complexidade"}
      description={"4 exercícios: Big-O, memoização e custo de estrutura."}
      href={"/docs/exercicios/26-complexidade"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
