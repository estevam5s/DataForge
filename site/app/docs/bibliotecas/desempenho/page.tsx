// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/bibliotecas_avancado.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Prometer desempenho",
  description: "A média esconde a cauda, o teste t supõe o que não vale, e a primeira medida nunca pode reprovar.",
};

const blocos: Bloco[] = [
  {"p": "Uma biblioteca que promete *“3% mais rápida”* precisa de uma medida que sustente a frase. Quase toda medida ingênua não sustenta."},
  {"h2": "O teste que mais importa"},
  {"callout": {"tipo": "atencao", "titulo": "Compare uma ação com ela mesma, e exija “empate”", "texto": "Uma ferramenta de comparação que responde *“3% mais rápida”* a isso é **pior que nenhuma ferramenta** — é assim que se escolhe a implementação errada com convicção. É o primeiro teste a escrever, antes de medir qualquer coisa real."}},
  {"table": {"head": ["Erro", "Por quê", "O que fazer"], "rows": [["comparar médias", "a média esconde a cauda, que é o que o usuário sente", "percentis — P50, P95, P99"], ["teste t", "tempo não é normal: cauda longa, piso duro, picos de escalonamento", "Mann-Whitney, com correção de empates"], ["medir A inteiro, depois B", "uma queda de clock no meio vira *“B é mais lenta”*", "**intercalar** as medições"], ["o valor de `p` sozinho", "alfa de 0,05 *significa* 1 em 20 falsos positivos", "exigir também o **efeito**, com piso"], ["limite absoluto em ms", "mede a **máquina**, não o código", "cobrar um **fator**"]]}},
  {"h2": "A razão não basta, se o trabalho for pequeno"},
  {"p": "Um teste de paralelismo comparou razão — o padrão correto — e falhou com **1,47**: o paralelo levou 0,44 s contra 0,30 s da série. O paralelismo estava certo; o que dominou foi o **custo de criar cinco threads**, que no Windows passa de 60 ms de trabalho."},
  { code: `// Subir a espera de 0,06 s para 0,25 s resolveu: a serie vira
// ~1,25 s e o tempo de partida deixa de aparecer na conta.
//
// A regra: de o numerador maior, em vez de afrouxar o limite.
// Quatro tarefas em vez de duas; blocos de 300 mil em vez de 150.

adopt Arcane.Bench as B

acao := lambda teto: sum([n * n cycle n in range(1, teto)])
m := B.medir(acao, 20000, 5)
assert m["ms"] bigger_eq 0.0
out $"{m['repeticoes']} repeticoes, {m['ms']} ms"`, lang: 'df' },
  {"h2": "O ponto de calibração"},
  {"p": "Quando nem o fator basta, meça **um algoritmo conhecidamente linear no mesmo instante**. Se ele não der ~2 ao dobrar o `n`, a máquina não está medindo — e o teste diz isso e **pula**."},
  {"callout": {"tipo": "dica", "titulo": "Medido, com seis threads queimando CPU", "texto": "O linear foi de 1,98 para **3,30–4,90** e o quadrático de 4,17 para **9,66–14,26**. Mais repetições não salvam: o `Bench` já usa o **menor** tempo de N, e a disputa sustentada atinge todas as amostras. E a calibração não deixa de proteger nada — se o código virasse quadrático, a referência continuaria em 2."}},
  {"table": {"head": ["Regra do CI", "Porque"], "rows": [["a **primeira** medida nunca reprova", "um CI que nasce vermelho por desenho é desligado no mesmo dia"], ["a tolerância é **obrigatória**", "sem ela, todo CI fica vermelho por ruído de máquina — o que dá no mesmo"]]}},
  {"p": "Continue em [Arcane.Perfil](/docs/biblioteca/perfil) e [Percentis, e a cauda](/docs/observabilidade/perfil)."},
];

const headings = [{ id: 'o-teste-que-mais-importa', text: "O teste que mais importa", level: 2 as const }, { id: 'a-razao-nao-basta-se-o-trabalho-for-pequeno', text: "A razão não basta, se o trabalho for pequeno", level: 2 as const }, { id: 'o-ponto-de-calibracao', text: "O ponto de calibração", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Prometer desempenho"}
      description={"A média esconde a cauda, o teste t supõe o que não vale, e a primeira medida nunca pode reprovar."}
      href={"/docs/bibliotecas/desempenho"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
