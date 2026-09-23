// GERADO por 'site/scripts/gerar_conteudo.py'. Nao edite aqui.
// A fonte e 'site/scripts/conteudo/concorrencia_extra.py' — mude la e rode o gerador.

import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "Medir sem inventar ganho",
  description: "As três formas de um teste de concorrência medir a máquina em vez do código.",
};

const blocos: Bloco[] = [
  {"p": "Concorrência é a área onde a medida engana mais, e onde um número errado é mais convincente. Três erros aparecem sempre, e os três já reprovaram o CI deste repositório."},
  {"h2": "1. Limite absoluto mede a máquina"},
  {"p": "`assert ms < 500` responde sobre o runner, e não sobre o algoritmo. Ele passa no seu computador e reprova num CI de três núcleos — e a reação natural (afrouxar o limite) tira o pouco que ele tinha de valor."},
  { code: `adopt Arcane.Bench as B

action trabalho():
    total := 0
    cycle i in range(0, 20000):
        total += i
    yield total

// Medir é fácil; o difícil é o que se COBRA da medida.
// O segundo parâmetro é o ARGUMENTO da ação, e o terceiro as
// repetições — trocar os dois é o erro mais comum aqui. Sem
// argumento, a ação é chamada sem nenhum.
r := B.medir(trabalho)
assert r["ms"] >= 0
assert r["por_segundo"] > 0
out $"{round(r['ms'], 2)} ms — e este número não serve de limite"`, lang: 'df' },
  {"h2": "2. A razão precisa de trabalho suficiente"},
  {"p": "Um teste de paralelismo comparou razão — o padrão certo — e falhou no Windows com **1,47**: o paralelo levou 0,44 s contra 0,30 s da série. O paralelismo estava certo; o que dominou foi o **custo de criar cinco threads**, que no Windows passa de 60 ms de trabalho. A correção não foi afrouxar: foi dar à medida um numerador maior."},
  { code: `adopt Arcane.Concurrent as C
adopt Arcane.Bench as B

action com_espera(x):
    sleep(40)          // E/S de mentira: o GIL é solto aqui
    yield x

action em_serie():
    yield [com_espera(i) cycle i in range(0, 4)]

action em_paralelo():
    yield C.map(com_espera, [0, 1, 2, 3])

serie := B.medir(em_serie)
junto := B.medir(em_paralelo)

razao := serie["ms"] / max(junto["ms"], 0.001)
// A cobrança é um FATOR, e com folga: quatro esperas de 40 ms em
// série são ~160 ms, e juntas são ~40 ms.
assert razao > 1.5
out $"{round(razao, 2)}× — e o limite cobrado é um fator, não um prazo"`, lang: 'df' },
  {"h2": "3. O `p` sozinho reprova por desenho"},
  {"p": "Alfa de 0,05 **significa** que uma em vinte comparações de coisas iguais cruza o limiar. Um teste que compara uma ação com ela mesma e só olha o `p` falha 5% das vezes — por definição, e não por defeito."},
  { code: `adopt Arcane.Perfil as P

action trabalho():
    total := 0
    cycle i in range(0, 3000):
        total += i
    yield total

// 'comparar' exige as DUAS perguntas: a ordem das amostras é
// acidente (o p), e daí? (o efeito, com piso). E ele alterna a ordem
// dentro da volta, porque quem mede primeiro paga a entrada dela.
r := P.comparar(trabalho, trabalho, {"amostras": 15})
out $"comparando uma ação com ela mesma: {r['mais_rapido']}"
out $"  fator {r['fator']}, p = {r['p_valor']}, significativo: {r['significativo']}"
assert r["mais_rapido"] is "empate"`, lang: 'df' },
  {"p": "Uma ferramenta que responde \"3% mais rápida\" a isso é **pior que nenhuma ferramenta**: é assim que se escolhe a implementação errada com convicção."},
  {"h2": "O ponto de calibração"},
  {"p": "Quando nem o fator basta — porque a máquina está disputada —, a saída é medir, **no mesmo instante**, um algoritmo cujo comportamento não está em dúvida. Se ele não der o esperado, a máquina não está medindo, e o teste diz isso e pula. Medido aqui, com seis threads queimando CPU: o linear foi de 1,98 para 3,30–4,90."},
  {"callout": {"tipo": "nota", "titulo": "A primeira medida nunca reprova", "texto": "Um CI que nasce vermelho por desenho é desligado no mesmo dia. `Arcane.Perfil` grava a primeira medida como referência e só compara a partir da segunda — e a tolerância é obrigatória, porque sem ela todo CI fica vermelho por ruído, o que dá no mesmo."}},
];

const headings = [{ id: '1-limite-absoluto-mede-a-maquina', text: "1. Limite absoluto mede a máquina", level: 2 as const }, { id: '2-a-razao-precisa-de-trabalho-suficiente', text: "2. A razão precisa de trabalho suficiente", level: 2 as const }, { id: '3-o-p-sozinho-reprova-por-desenho', text: "3. O `p` sozinho reprova por desenho", level: 2 as const }, { id: 'o-ponto-de-calibracao', text: "O ponto de calibração", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"Medir sem inventar ganho"}
      description={"As três formas de um teste de concorrência medir a máquina em vez do código."}
      href={"/docs/concorrencia/medir"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
