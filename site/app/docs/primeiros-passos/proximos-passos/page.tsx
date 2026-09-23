// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/primeiros_passos_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Para onde ir agora",
  description: "Os caminhos depois do básico — conforme o que você quer construir.",
};

const blocos: Bloco[] = [
  {"p": "Com o que está nestas dez páginas já dá para escrever programas úteis: ler dados, decidir, repetir, organizar em ações. O próximo passo depende do que você quer construir."},
  {"table": {"head": ["Quero…", "Comece em"], "rows": [["entender a linguagem a fundo", "[Fundamentos](/docs/fundamentos) e [a referência](/docs/referencia/gramatica)"], ["analisar uma planilha ou um CSV", "[Dados](/docs/dados)"], ["fazer um site ou uma API", "[Kiln](/docs/kiln)"], ["um painel de gráficos", "[Vitrine](/docs/vitrine)"], ["um bot", "[Telegram](/docs/telegram)"], ["programar melhor, com testes", "[TDD](/docs/testes/tdd)"], ["entender por que um programa é lento", "[Big-O](/docs/big-o)"], ["ver um projeto de cada tipo", "[Os 22 tipos de projeto](/docs/projetos)"]]}},
  {"h2": "Praticar"},
  { code: `dataforge new cli minha-ferramenta   # um projeto que ja passa nos testes
dataforge palavras                   # cada palavra da linguagem, com exemplo que roda
python3 exercicios/run_all.py 01     # os exercicios do modulo 1`, lang: 'bash' },
  { code: `// Um ultimo exercicio: some so os pares de 1 a 100.
soma := 0
cycle n from 1 to 100:
    given n % 2 is 0:
        soma += n
assert soma is 2550
out "voce terminou os primeiros passos"`, lang: 'df' },
];

const headings = [{ id: 'praticar', text: "Praticar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Para onde ir agora"}
      description={"Os caminhos depois do básico — conforme o que você quer construir."}
      href={"/docs/primeiros-passos/proximos-passos"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
