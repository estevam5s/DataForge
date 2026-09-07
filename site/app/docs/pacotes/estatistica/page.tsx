import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "estatistica",
  description: "Estatística: média, mediana, desvio, quartis, correlação e regressão.",
};

const blocos: Bloco[] = [
  { code: `dataforge add estatistica`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "20 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Média sozinha engana: `[1, 1, 1, 97]` tem média 25, e nenhum valor perto disso. Por isso `resumo` devolve mediana e desvio junto — é o conjunto que diz a verdade sobre a distribuição."},
  {"h2": "Uso"},
  { code: `adopt estatistica as E

out E.media([1, 2, 3, 4])        // 2.5
out E.resumo(vendas)             // média, mediana, desvio, quartis
out E.correlacao(x, y)           // -1.0 a 1.0`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 20 símbolos:"},
  { code: `soma(v)
media(v)
mediana(v)
moda(v)
variancia(v, amostral := yes)
desvio_padrao(v, amostral := yes)
amplitude(v)
percentil(v, p)
quartis(v)
amplitude_interquartil(v)
extremos(v, fator := 1.5)
normalizar(v)
padronizar(v)
covariancia(x, y)
correlacao(x, y)
regressao(x, y)
resumo(v)
media_movel(v, janela)
histograma(v, faixas := 10)
ordenados(v)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add estatistica
dataforge add estatistica@1.0.0
dataforge add estatistica@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"estatistica"}
      description={"Estatística: média, mediana, desvio, quartis, correlação e regressão."}
      href={"/docs/pacotes/estatistica"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
