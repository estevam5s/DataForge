import type { Metadata } from 'next';
import type { Bloco } from '@/lib/content';
import { DocPage } from '@/components/Doc';
import { Renderer } from '@/components/Renderer';

export const metadata: Metadata = {
  title: "aleatorio",
  description: "Aleatoriedade com semente: sorteio, embaralhar, amostra e distribuições.",
};

const blocos: Bloco[] = [
  { code: `dataforge add aleatorio`, lang: 'bash' },
  {"table": {"head": ["", ""], "rows": [["Versão", "`1.0.0`"], ["Licença", "MIT"], ["Dependências", "nenhuma"], ["Exporta", "8 símbolos"]]}},
  {"h2": "Por que existe"},
  {"p": "Com semente, a sequência se repete. É o que torna um teste que usa aleatoriedade reproduzível — sem isso, a falha de ontem não volta."},
  {"h2": "Uso"},
  { code: `adopt aleatorio as A

r := A.gerador(42)
out r.inteiro(1, 6)          // um dado
out A.embaralhar([1,2,3,4], r)`, lang: 'df' },
  {"h2": "API"},
  {"p": "O que `relay` exporta — 8 símbolos:"},
  { code: `blueprint Gerador
gerador(semente := 12345)
embaralhar(itens, r := void)
amostra(itens, quantos, r := void)
amostra_com_repeticao(itens, quantos, r := void)
normal(media := 0.0, desvio := 1.0, r := void)
uuid_simples(r := void)
entre(minimo, maximo, r := void)`, lang: 'df' },
  {"h2": "Instalar"},
  { code: `dataforge add aleatorio
dataforge add aleatorio@1.0.0
dataforge add aleatorio@^1.0`, lang: 'bash' },
];

const headings = [{ id: 'por-que-existe', text: "Por que existe", level: 2 as const }, { id: 'uso', text: "Uso", level: 2 as const }, { id: 'api', text: "API", level: 2 as const }, { id: 'instalar', text: "Instalar", level: 2 as const }];

export default function Pagina() {
  return (
    <DocPage
      title={"aleatorio"}
      description={"Aleatoriedade com semente: sorteio, embaralhar, amostra e distribuições."}
      href={"/docs/pacotes/aleatorio"}
      headings={headings}
    >
      <Renderer blocos={blocos} />
    </DocPage>
  );
}
